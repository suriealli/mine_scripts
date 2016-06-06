#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionTJHCMgr")
#===============================================================================
# 天降横财 Mgr
#===============================================================================
import cRoleMgr
import cProcess
import cDateTime
import cNetMessage
import cComplexServer
import time
import random
import Environment
from Common.Other import EnumGameConfig, GlobalPrompt
from Common.Message import AutoMessage, PyMessage
from ComplexServer.Log import AutoLog
from ComplexServer.Plug.Control import ControlProxy
from Game.Role import Event
from Game.Role.Mail import Mail
from Game.GlobalData import ZoneName
from Game.Persistence import Contain
from Game.SysData import WorldDataNotSync, WorldData
from Game.Role.Data import EnumInt32, EnumInt16
from Game.Activity.PassionAct import PassionTJHCConfig, PassionActVersionMgr


FOURMINSEC = 4 * 60
DEFAULT_REWARDID = 0 	#默认奖励ID  0表示未开奖

if "_HasLoad" not in dir():
	#活动开关
	IS_START = False
	#活动结束时间戳
	ENDTIME = 0
	#活動時間配置
	ACTIVE_CFG = None
	#是否开奖期间 本服跨服数据传输延迟保护
	IS_LOTTERYTIME = False
	#当前中奖记录缓存[(UniqueCode,roleName,zoneName,rewardId),]
	TJHC_PreciousRecord_List = []
	
	#天降横财_活动状态同步 格式( IS_START, endTime) (非零表示活动结束时间戳，零表示告知活动结束！)
	TJHC_ActiveState_S = AutoMessage.AllotMessage("TJHC_ActiveState_S", "天降横财_活动状态同步")
	#天降横财_中奖记录同步 格式 [(u_code,roleName,zoneName,rewardId),]
	TJHC_PreciousRecord_S = AutoMessage.AllotMessage("TJHC_PreciousRecord_S", "天降横财_中奖记录同步")
	#天降横财_我的兑奖码同步  格式：{u_code:rewardId}
	TJHC_MyUniqueCode_S = AutoMessage.AllotMessage("TJHC_MyUniqueCode_S", "天降横财_我的兑奖码同步")
	
	#日志
	Tra_TJHC_ActivateCode = AutoLog.AutoTransaction("Tra_TJHC_ActivateCode", "天降横财_激活兑奖码") 
	Tra_TJHC_GetReward = AutoLog.AutoTransaction("Tra_TJHC_GetReward", "天降横财_领取兑奖码奖励")
	Tra_TJHC_AutoReward = AutoLog.AutoTransaction("Tra_TJHC_AutoReward", "天降横财_活动结束自动发送未领取奖励")
	Tra_TJHC_NonactivatedReward = AutoLog.AutoTransaction("Tra_TJHC_NonactivatedReward", "天降横财_活动结束自动发送未激活兑奖码奖励")
	

#===============================================================================
# 活动控制
#===============================================================================
def OpenActive(callArgv, regparam):
	'''
	天降横财-开启
	'''
	#新服不给开启
	if not IsOldServer():
		return
	
	global ENDTIME
	global IS_START
	global ACTIVE_CFG
	
	if IS_START:
		print 'GE_EXC, repeat start TJHC'
		return
	IS_START = True
	
	ENDTIME, ACTIVE_CFG = regparam
	
	cNetMessage.PackPyMsg(TJHC_ActiveState_S, (IS_START,ENDTIME))
	cRoleMgr.BroadMsg()
	
	#活动开启 即可处理
	InitActiveRound()
	
	
def CloseActive(callArgv, regparam):
	'''
	天降横财-结束
	'''
	global IS_START
	
	if not IS_START:
		print 'GE_EXC, repeat end TJHC'
		return
	IS_START = False
	
	cNetMessage.PackPyMsg(TJHC_ActiveState_S, (IS_START,ENDTIME))
	cRoleMgr.BroadMsg()


#===============================================================================
# 客户端请求
#===============================================================================
def OnOpenPanel(role, msg = None):
	'''
	天降横财_请求打开操作面板
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.TJHC_NeedLevel:
		return
	
	role.SendObj(TJHC_PreciousRecord_S, TJHC_PreciousRecord_List)
	
	
def OnOpenMyPanel(role, msg = None):
	'''
	天降横财_请求打开兑奖码面板
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.TJHC_NeedLevel:
		return
	
	role.SendObj(TJHC_MyUniqueCode_S, TJHC_LotteryRecord_Dict_A.get(role.GetRoleID(), {}))
	

def OnActivateCode(role, msg = 1):
	'''
	天降横财_请求激活兑奖码
	@param msg: activateCnt
	'''
	if not IS_START:
		return
	
	if IS_LOTTERYTIME:
		role.Msg(2, 0, GlobalPrompt.TJHC_Tips_IsLottery)
		return
	
	if role.GetLevel() < EnumGameConfig.TJHC_NeedLevel:
		return
	
	#玩家当前兑奖码奖励数据条数过多
	targetCnt = msg
	roleId = role.GetRoleID()
	global TJHC_LotteryRecord_Dict_A
	roleTotalCode = len(TJHC_LotteryRecord_Dict_A.get(roleId, {}))
	if roleTotalCode + targetCnt > EnumGameConfig.TJHC_RoleUCode_RoundMaxCnt:
		role.Msg(2, 0, GlobalPrompt.TJHC_Tips_RoleDataOverFlow_1 % EnumGameConfig.TJHC_RoleUCode_RoundMaxCnt)
		return
	
	#本服本轮参与兑奖码过多
	global TJHC_NextRoundGambler_Dict
	if len(TJHC_NextRoundGambler_Dict) + targetCnt > EnumGameConfig.TJHC_ServerUCode_MaxCnt:
		role.Msg(2, 0, GlobalPrompt.TJHC_Tips_ServerDataOverFlow)
		return
	
	#玩家本次活动激活的兑奖码过多
	activatedCnt = role.GetI16(EnumInt16.TJHC_ActivatedCnt)
	if targetCnt + activatedCnt > EnumGameConfig.TJHC_RoleUCode_TotalMaxCnt:
		role.Msg(2, 0, GlobalPrompt.TJHC_Tips_RoleDataOverFlow_2)
		return
	
	totalConsumeRMB_Q = role.GetI32(EnumInt32.TJHC_ConsumeUnbindRMB_Q) + role.GetI32(EnumInt32.DayConsumeUnbindRMB_Q)
	canActivateCnt = totalConsumeRMB_Q / EnumGameConfig.TJHC_UniqueCode_Price
	if canActivateCnt - activatedCnt < targetCnt:
		print "GE_EXC, canActivateCnt(%s) - activatedCnt(%s) < targetCnt(%s)" % (canActivateCnt, activatedCnt, targetCnt)
		return
	
	#process
	with Tra_TJHC_ActivateCode:
		global TJHC_LotteryRecord_Dict_B
		roleName = role.GetRoleName()
		zoneName = ZoneName.GetRoleZoneName(role)
		realActivatedCnt = 0
		for _ in xrange(targetCnt):
			uniqueCode = GetUniqueCode()
			#Dict_B 优先判断是否此code是否有主了
			if uniqueCode in TJHC_LotteryRecord_Dict_B:
				print "GE_EXC ,TJHC::OnActivateCode,get a repeat uniqueCode(%s) in TJHC_LotteryRecord_Dict_B" % uniqueCode
				continue
			#Gambler_Dict 判断当前参与的兑奖券是否重复
			if uniqueCode in TJHC_NextRoundGambler_Dict:
				print "GE_EXC ,TJHC::OnActivateCode,get a repeat uniqueCode(%s) in TJHC_NextRoundGambler_Dict" % uniqueCode
				continue
			
			#Dict_A
			roleData_DictA = TJHC_LotteryRecord_Dict_A.setdefault(roleId, {})
			if uniqueCode in roleData_DictA:
				print "GE_EXC,TJHC::OnActivateCode,get a repeat uniqueCode(%s) in TJHC_LotteryRecord_Dict_A" % uniqueCode
				continue
			
			#统计实际有效的兑奖码
			realActivatedCnt += 1
			#Dict_A 保存
			roleData_DictA[uniqueCode] = DEFAULT_REWARDID
			TJHC_LotteryRecord_Dict_A.HasChange()
			#Dict_B 保存
			TJHC_LotteryRecord_Dict_B[uniqueCode] = roleId
			#Gambler_Dict 保存
			TJHC_NextRoundGambler_Dict[uniqueCode] = [roleId, roleName, zoneName]	
			#log
			AutoLog.LogBase(roleId, AutoLog.eveTJHCActivateCode, uniqueCode)	
	
		#记录已激活兑奖码数量
		role.IncI16(EnumInt16.TJHC_ActivatedCnt, realActivatedCnt)
	

def OnGetReward(role, msg = None):
	'''
	天降横财_请求领取奖励
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.TJHC_NeedLevel:
		return
	
	roleId = role.GetRoleID()
	global TJHC_LotteryRecord_Dict_A
	roleData_DictA = TJHC_LotteryRecord_Dict_A.get(roleId, None)
	if not roleData_DictA:
		return
	
	rewardDict = {}
	rewardCodeSet = set()
	for tCode, tRewardId in roleData_DictA.iteritems():
		if tRewardId != DEFAULT_REWARDID:
			rewardCodeSet.add(tCode)
			rewardCfg = PassionTJHCConfig.TJHC_RewardConfig_Dict.get(tRewardId)
			coding, cnt = rewardCfg.rewardItem
			if coding in rewardDict:
				rewardDict[coding] += cnt
			else:
				rewardDict[coding] = cnt
	
	if len(rewardDict) < 1:
		return
	
	prompt = GlobalPrompt.TJHC_Tips_Reward
	with Tra_TJHC_GetReward:
		#处理兑奖码数据
		global TJHC_LotteryRecord_Dict_B
		for tCode in rewardCodeSet:
			if tCode in TJHC_LotteryRecord_Dict_B:
				del TJHC_LotteryRecord_Dict_B[tCode]
			
			if tCode in roleData_DictA:
				del roleData_DictA[tCode]
				TJHC_LotteryRecord_Dict_A.HasChange()
			
			if len(roleData_DictA) == 0:
				del TJHC_LotteryRecord_Dict_A[roleId]				
						
		#获得
		for coding, cnt in rewardDict.iteritems():
			role.AddItem(coding, cnt)
			prompt += GlobalPrompt.Item_Tips % (coding, cnt)
		
	#获得提示
	role.Msg(2, 0, prompt)
	#同步最新我的兑奖码数据
	role.SendObj(TJHC_MyUniqueCode_S, roleData_DictA)
	

#===============================================================================
# 辅助
#===============================================================================
def InitActiveRound():
	'''
	根据回合控制配置表 处理回合触发及tick
	'''
	nowTime = cDateTime.Seconds()
	for roundId, tCfg in PassionTJHCConfig.TJHC_LotteryControl_Dict.iteritems():
		syncTime =  int(time.mktime(tCfg.syncTime.timetuple()))
		lotteryTime = int(time.mktime(tCfg.lotteryTime.timetuple()))
		if syncTime <= nowTime < lotteryTime:
			#即将开奖同步本服参与奖券数据
			SendLocalData()
			cComplexServer.RegTick(lotteryTime - nowTime + FOURMINSEC, AfterLottery, roundId)
		elif nowTime < syncTime:
			#注册一个tick激活
			cComplexServer.RegTick(syncTime - nowTime, SendLocalData)	
			cComplexServer.RegTick(lotteryTime - nowTime + FOURMINSEC, AfterLottery, roundId)
			

def SendLocalData(callArgvs = None, regParams = None):
	'''
	发送本服当前参与数据到跨服 等待抽奖
	'''
	#活动未开启
	if not IS_START:
		return
	
	#本轮已经触发过发送数据
	global IS_LOTTERYTIME
	if IS_LOTTERYTIME:
		return 
	
	#进入抽奖阶段
	IS_LOTTERYTIME = True
	oldVersion = TJHC_NextRoundGambler_Dict["version"]
	del TJHC_NextRoundGambler_Dict["version"]
	ControlProxy.SendControlBigMsg(PyMessage.TJHC_SendGamblerData_Logic2Control, TJHC_NextRoundGambler_Dict.data)
	TJHC_NextRoundGambler_Dict["version"] = oldVersion
	

def AfterLottery(callArgvs = None, regParams = None):
	'''
	本服按照配置表tick触发
	抽奖后处理 若活动继续开启 解锁抽奖阶段标志
	'''
	#活动结束 处理未领取的奖励自动发奖
	if not IS_START:
		AuToReward()
		return
	
	global IS_LOTTERYTIME
	if not IS_LOTTERYTIME:
		return
	
	#异常 未收到开奖结果 主动请求开奖数据
	roundId = regParams
	ControlProxy.SendControlMsgAndBack(PyMessage.TJHC_RequestLotteryResult_Logic2Control, roundId, RequestBackFun, roundId)


def GetUniqueCode():
	'''
	生成并返回一个 UniqueCode
	''' 
	baseN = WorldDataNotSync.GetTHJCBaseN()
	WorldDataNotSync.SetTJHCBaseN(baseN + 1)
	return baseN * EnumGameConfig.TJHC_BaseN_Factor + cProcess.ProcessID


def GetRewardItemList(UniqueCodeDict = {}):
	'''
	根据 兑奖码奖励状态 返回可领取的奖励道具列表
	'''
	rewardItemDict = {}
	for _, rewardId in UniqueCodeDict.iteritems():
		if rewardId == DEFAULT_REWARDID:
			rewardId = EnumGameConfig.TJHC_NOMAL_REWARDID
		rewardCfg = PassionTJHCConfig.TJHC_RewardConfig_Dict.get(rewardId, None)
		if rewardCfg:
			coding ,cnt = rewardCfg.rewardItem
			rewardItemDict[coding] = rewardItemDict.get(coding, 0) + cnt
	
	rewardList = []
	for coding, cnt in rewardItemDict.iteritems():
		rewardList.append((coding, cnt))
	return rewardList
		

def IsOldServer():
	'''
	天降横财新服老服区分
	'''
	if WorldData.GetWorldKaiFuDay() > EnumGameConfig.TJHC_NeedKaiFuDay:
		return True
	else:
		return False

#===============================================================================
# 事件
#===============================================================================
def OnSyncOtherData(role, param = None):
	'''
	角色上限同步活动状态
	'''
	if IS_START:
		role.SendObj(TJHC_ActiveState_S, (IS_START,ENDTIME))
	else:
		NonactivatedCodeReward(role, PassionTJHCConfig.TJHC_NomalReward)
	


def AfterChangeDayConsumeUnbindRMB_Q(role, param = None):
	'''
	每日清理消耗充值神石 归并到活动期间今日之前的充值神石总消耗
	'''
	if not IS_START:
		return
	
	beginTime = ACTIVE_CFG.beginTime
	now = cDateTime.Now()
	interval = now - beginTime
	if interval.days < 1:
		return 
	
	oldValue, newValue = param
	if newValue == 0 and oldValue > 0:
		role.IncI32(EnumInt32.TJHC_ConsumeUnbindRMB_Q, oldValue)


def AfterLoadTJHCDictA():
	'''
	数据载回处理
	'''
	nowVersion = PassionActVersionMgr.PassionVersion
	dataVersion = TJHC_LotteryRecord_Dict_A.get("version", 0)
	if nowVersion != dataVersion or not dataVersion:
		TJHC_LotteryRecord_Dict_A.data = {}
		TJHC_LotteryRecord_Dict_A["version"] = nowVersion
		TJHC_LotteryRecord_Dict_A.HasChange()


def AfterLoadTJHCDictB():
	'''
	数据载回处理
	'''
	nowVersion = PassionActVersionMgr.PassionVersion
	dataVersion = TJHC_LotteryRecord_Dict_B.get("version", 0)
	if nowVersion != dataVersion or not dataVersion:
		TJHC_LotteryRecord_Dict_B.data = {}
		TJHC_LotteryRecord_Dict_B["version"] = nowVersion
		TJHC_LotteryRecord_Dict_B.HasChange()
	
	
def AfterLoadTJHCDictC():
	'''
	数据载回处理
	'''
	nowVersion = PassionActVersionMgr.PassionVersion
	dataVersion = TJHC_NextRoundGambler_Dict.get("version", 0)
	if nowVersion != dataVersion or not dataVersion:
		TJHC_NextRoundGambler_Dict.data = {}
		TJHC_NextRoundGambler_Dict["version"] = nowVersion
		TJHC_NextRoundGambler_Dict.HasChange()


def AfterLoadWDNS(param1 = None, param2 = None):
	'''
	基数和版本载回处理 
	'''
	WDNS = WorldDataNotSync
	nowVersion = PassionActVersionMgr.PassionVersion
	baseNVersion = WDNS.WorldDataPrivate[WDNS.PassionTJHCBaseNVersion]
	if not baseNVersion or baseNVersion != nowVersion:
		WDNS.WorldDataPrivate[WDNS.PassionTJHCBaseNVersion] = nowVersion
		WDNS.WorldDataPrivate[WDNS.PassionTJHCBaseN] = random.randint(*EnumGameConfig.TJHC_BaseN_Range)


#===============================================================================
# 进程通信
#===============================================================================
def OnSendLotteryResult(sessionid, msg):
	'''
	天降横财_发送抽奖结果_控制进程到逻辑进程
	@param sessionid:
	@param msg: LotteryResultData  
	'''
	if not IS_START:
		print "GE_EXC, TJHC::OnSendLotteryResult, IS_START(%s)" % IS_START
		return
	
	#清除抽奖阶段开关
	global IS_LOTTERYTIME
	if IS_LOTTERYTIME:
		IS_LOTTERYTIME = False
	
	#{uCode:[roleId,roleName,zoneName,rewardId],}
	lotteryResult_Dict = msg
	roleToBeSyncSet = set() 
	
	#处理中奖
	global TJHC_NextRoundGambler_Dict
	for uCode, info in lotteryResult_Dict.iteritems():
		if uCode in TJHC_NextRoundGambler_Dict:
			luckyRoleId, rewardId = info[0], info[3]
			localRoleId = TJHC_NextRoundGambler_Dict[uCode][0]
			if luckyRoleId != localRoleId:
				print "GE_EXC, TJHC::OnSendLotteryResult, the lucky uCode(%s) with roleId(%s) not local roleId(%s)" % (uCode, luckyRoleId, localRoleId)
				continue
			#删除Gambler_Dict中中奖了的ucode
			roleToBeSyncSet.add(localRoleId)
			del TJHC_NextRoundGambler_Dict[uCode]
			#同步更新到Dict_A
			roleData_DictA = TJHC_LotteryRecord_Dict_A.setdefault(luckyRoleId, {})
			roleData_DictA[uCode] = rewardId
			TJHC_LotteryRecord_Dict_A.HasChange()
			
	#处理剩下的安慰奖
	for tCode in TJHC_NextRoundGambler_Dict.keys():
		roleId = TJHC_LotteryRecord_Dict_B.get(tCode, None)
		roleToBeSyncSet.add(roleId)
		if not roleId:
			continue
		
		roleData_DictA = TJHC_LotteryRecord_Dict_A.get(roleId, None)
		if not roleData_DictA:
			continue
		
		roleData_DictA[tCode] = EnumGameConfig.TJHC_NOMAL_REWARDID
		TJHC_LotteryRecord_Dict_A.HasChange()
		
	#清楚本轮参与兑奖码数据
	oldVersion = TJHC_NextRoundGambler_Dict["version"]
	TJHC_NextRoundGambler_Dict.clear()
	TJHC_NextRoundGambler_Dict["version"] = oldVersion
	#中奖记录缓存
	global TJHC_PreciousRecord_List
	for uCode, info in lotteryResult_Dict.iteritems():
		tCfg = PassionTJHCConfig.TJHC_RewardConfig_Dict.get(info[3], None)
		if not tCfg or not tCfg.isPrecious:
			continue
		tInfo = [uCode, info[1], info[2], info[3]]
		TJHC_PreciousRecord_List.append(tInfo)
	
	#截断 最多TJHC_PreciousRecordCnt条
	TJHC_PreciousRecord_List = TJHC_PreciousRecord_List[EnumGameConfig.TJHC_PreciousRecordCnt * (-1):]
	
	#广播中奖记录
	cNetMessage.PackPyMsg(TJHC_PreciousRecord_S, TJHC_PreciousRecord_List)
	cRoleMgr.BroadMsg()
	
	#开奖广播
	cRoleMgr.Msg(11, 0, GlobalPrompt.TJHC_Msg_AfterLottery)
	
	#同步参与本轮的玩家
	for tRoleId in roleToBeSyncSet:
		tRole = cRoleMgr.FindRoleByRoleID(tRoleId)
		if not tRole or tRole.IsLost() or tRole.IsKick():
			continue
		tRole.SendObj(TJHC_MyUniqueCode_S, TJHC_LotteryRecord_Dict_A.get(tRoleId, {}))
	
	print "TJHC,OnSendLotteryResult::Success!"


def RequestBackFun(callArgvs = None, regParams = None):
	'''
	请求开奖结果返回
	'''
	#不管如何 清除开奖阶段开关
	global IS_LOTTERYTIME
	if IS_LOTTERYTIME:
		IS_LOTTERYTIME = False
	else:
		#本服不是等待开奖结果状态
		return
	
	lotteryResult_Dict = {}
	if callArgvs == None:
		print "GE_EXC,TJHC::RequestBackFun,self back!"
	else:
		callRoundId, lotteryResult_Dict = callArgvs
		regRoundId = regParams
		
		#开奖回合不一致
		if callRoundId != regRoundId:
			print "GE_EXC,TJHC::RequestBackFun, callRoundId(%s) != regRoundId(%s)" % (callRoundId,regRoundId)

	#强制处理 确保后续数据正常！
	OnSendLotteryResult(None, lotteryResult_Dict)


def AuToReward():
	'''
	活动结束后 自动发送玩家没有领取的奖励
	'''
	if IS_START:
		return
	
	global TJHC_LotteryRecord_Dict_A
	oldVersion = TJHC_LotteryRecord_Dict_A["version"]
	del TJHC_LotteryRecord_Dict_A["version"]
	if len(TJHC_LotteryRecord_Dict_A) < 1:
		TJHC_LotteryRecord_Dict_A["version"] = oldVersion
		return
	
	#除了version之外还有数据
	with Tra_TJHC_AutoReward:
		for roleId, roleData_DictA in TJHC_LotteryRecord_Dict_A.iteritems():
			if type(roleId) is int or type(roleId) is long:
				Mail.SendMail(roleId, GlobalPrompt.TJHC_Mail_Title, GlobalPrompt.TJHC_Mail_Sender, GlobalPrompt.TJHC_Mail_Content, GetRewardItemList(roleData_DictA))
	
	#处理A
	TJHC_LotteryRecord_Dict_A.clear()
	TJHC_LotteryRecord_Dict_A["version"] = oldVersion
	#处理B
	global TJHC_LotteryRecord_Dict_B
	if len(TJHC_LotteryRecord_Dict_B) > 1:
		oldVersion = TJHC_LotteryRecord_Dict_B["version"]
		TJHC_LotteryRecord_Dict_B.clear()
		TJHC_LotteryRecord_Dict_B["version"] = oldVersion
		
	#处理C
	global TJHC_NextRoundGambler_Dict
	if len(TJHC_NextRoundGambler_Dict) > 1:
		oldVersion = TJHC_NextRoundGambler_Dict["version"]
		TJHC_NextRoundGambler_Dict.clear()
		TJHC_NextRoundGambler_Dict["version"] = oldVersion
		
	#在线玩家未激活的兑换码资格处理
	for tRole in cRoleMgr.GetAllRole():
		NonactivatedCodeReward(tRole, PassionTJHCConfig.TJHC_NomalReward)


def NonactivatedCodeReward(role, rewardItem):
	'''
	玩家未激活的兑换码资格处理
	'''
	if role.IsLost() or role.IsKick():
		return
	
	activatedCnt = role.GetI16(EnumInt16.TJHC_ActivatedCnt)
	totalConsumeRMB_Q = role.GetI32(EnumInt32.TJHC_ConsumeUnbindRMB_Q)# + role.GetI32(EnumInt32.DayConsumeUnbindRMB_Q)
	canActivateCnt = totalConsumeRMB_Q / EnumGameConfig.TJHC_UniqueCode_Price
	remainCnt = min(canActivateCnt, EnumGameConfig.TJHC_RoleUCode_TotalMaxCnt) - activatedCnt
	if remainCnt > 0:
		with Tra_TJHC_NonactivatedReward:
			role.IncI16(EnumInt16.TJHC_ActivatedCnt, remainCnt)
			Mail.SendMail(role.GetRoleID(), GlobalPrompt.TJHC_Mail_Title2, GlobalPrompt.TJHC_Mail_Sender2, GlobalPrompt.TJHC_Mail_Content2 % remainCnt, [(rewardItem[0], rewardItem[1] * remainCnt)])
	

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#事件
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncOtherData)
		Event.RegEvent(Event.Eve_AfterLoadWorldDataNotSync, AfterLoadWDNS)
		Event.RegEvent(Event.Eve_AfterChangeDayConsumeUnbindRMB_Q, AfterChangeDayConsumeUnbindRMB_Q)
		
		cComplexServer.RegAfterNewDayCallFunction(AuToReward)
		
		#持久化数据
		#A 天降横财抽奖状态记录 {roleId:{u_code:rewardId},}
		TJHC_LotteryRecord_Dict_A = Contain.Dict("TJHC_LotteryRecord_Dict_A", (2038, 1, 1), AfterLoadTJHCDictA)
		#B 天降横财抽奖状态记录 {u_code:roleId,}
		TJHC_LotteryRecord_Dict_B = Contain.Dict("TJHC_LotteryRecord_Dict_B", (2038, 1, 1), AfterLoadTJHCDictB)
		#C 天降横财 下轮参与兑奖数据 {u_code:[roleId,roleName,zoneName],}
		TJHC_NextRoundGambler_Dict = Contain.Dict("TJHC_NextRoundGambler_Dict", (2038, 1, 1), AfterLoadTJHCDictC)
		
		#进程通信
		cComplexServer.RegDistribute(PyMessage.TJHC_SendLotteryResult_Control2Logic, OnSendLotteryResult)
		
		#客户端消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TJHC_OnOpenPanel", "天降横财_请求打开操作面板"), OnOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TJHC_OnOpenMyPanel", "天降横财_请求打开兑奖码面板"), OnOpenMyPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TJHC_OnActivateCode", "天降横财_请求激活兑奖码"), OnActivateCode)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TJHC_OnGetReward", "天降横财_请求领取奖励"), OnGetReward)
