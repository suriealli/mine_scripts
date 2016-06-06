#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DoubleEleven.DETopicMgr")
#===============================================================================
# 双十一2015 专题转盘 Mgr
#===============================================================================
import cRoleMgr
import cDateTime
import cNetMessage
import cComplexServer
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event, Call
from Game.Role.Data import EnumInt8, EnumInt16
from Game.Activity.DoubleEleven import DETopicConfig


IDX_DETopic = 2
if "_HasLoad" not in dir():
	#活动开关标志
	IS_START = False
	#活动结束时间戳
	ENDTIME = 0
	#天数索引
	DAYINDEX = 0
	#珍稀奖励记录[(roleName,coding,cnt),] 
	DETopic_PreciousRecord_List = []
	#当前打开操作面板的玩家ID集合
	DETopic_OpenPanelRole_Set = set()
	
	#活动状态同步 格式: endTime (非零表示活动结束时间戳，零表示告知活动结束！)
	DETopic_ActiveState_S = AutoMessage.AllotMessage("DETopic_ActiveState_S", "专题转盘_活动状态同步")
	#同步珍稀中奖记录 格式  [(roleName,coding,cnt),] 
	DETopic_PreciousRecord_S = AutoMessage.AllotMessage("DETopic_PreciousRecord_S", "专题转盘_珍稀中奖纪录同步")
	#同步抽奖结果 格式 itemIndex 表示抽中物品的itemIndex
	DETopic_LotteryResult_SB = AutoMessage.AllotMessage("DETopic_LotteryResult_SB", "专题转盘_抽奖结果同步回调")
	
	Tra_DETopic_LotteryYiCi = AutoLog.AutoTransaction("Tra_DETopic_LotteryYiCi", "专题转盘_抽奖一次")
	Tra_DETopic_LotteryShiCi = AutoLog.AutoTransaction("Tra_DETopic_LotteryShiCi", "专题转盘_抽奖十次")
	Tra_DETopic_InitTopicId = AutoLog.AutoTransaction("Tra_DETopic_InitTopicId", "专题转盘_初始化专题ID")
	
#===============================================================================
# 活动控制
#===============================================================================
def OpenActive(callArgv, regparam):
	'''
	古堡探秘-开启
	'''
	global ENDTIME
	global IS_START
	
	if IS_START:
		print 'GE_EXC, repeat start DETopic'
		return
	IS_START = True
	
	ENDTIME = regparam
	
	cNetMessage.PackPyMsg(DETopic_ActiveState_S, (IS_START,ENDTIME))
	cRoleMgr.BroadMsg()
	
	#活动开启即可计算天数索引  不能直接设置为1 有可能活动期间重启服务器
	CalculateDayIndex()
	
	
def CloseActive(callArgv, regparam):
	'''
	古堡探秘-结束
	'''
	global IS_START
	
	if not IS_START:
		print 'GE_EXC, repeat end DETopic'
		return
	IS_START = False
	
	cNetMessage.PackPyMsg(DETopic_ActiveState_S, (IS_START,ENDTIME))
	cRoleMgr.BroadMsg()


#===============================================================================
# 客户端请求
#===============================================================================
def OnOpenPanel(role,msg = None):
	'''
	专题转盘_请求打开操作面板
	'''
	if not IS_START:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.DETopic_NeedLevel:
		return
	
	global DETopic_OpenPanelRole_Set
	DETopic_OpenPanelRole_Set.add(role.GetRoleID())
	
	oldTopicId = role.GetI8(EnumInt8.DETopicTodayTopicId)
	if not oldTopicId or oldTopicId not in DETopicConfig.DETopic_BaseConfig_Dict:
		with Tra_DETopic_InitTopicId:
			role.SetI8(EnumInt8.DETopicTodayTopicId, DETopicConfig.GetTopicIdByDayAndLevel(DAYINDEX, roleLevel))
	
	role.SendObj(DETopic_PreciousRecord_S, DETopic_PreciousRecord_List)


def OnClosePanel(role, msg = None):
	'''
	专题转盘_请求关闭操作面板
	'''
	if not IS_START:
		return
	
	global DETopic_OpenPanelRole_Set
	DETopic_OpenPanelRole_Set.discard(role.GetRoleID())
	

def OnLotteryYiCi(role, msg = None):
	'''
	专题转盘_请求抽奖一次
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.DETopic_NeedLevel:
		return
	
	topicId = role.GetI8(EnumInt8.DETopicTodayTopicId)
	topicCfg = DETopicConfig.DETopic_BaseConfig_Dict.get(topicId, None)
	if not topicCfg:
		print "GE_EXC,DETopicMgr::OnLotteryYiCi can not get topic config by topicId(%s), role(%s)" % (topicId, role.GetRoleID()) 
		return
	
	lotteryCnt = role.GetI16(EnumInt16.DETopicLotteryCnt)
	if lotteryCnt + 1 > topicCfg.dayMaxLotteryCnt:
		return
	
	
	needRMB = topicCfg.oneNeedRMB
	needRMBType = topicCfg.needRMBType
	if needRMBType == 0:
		DECRMB_FUN = role.DecUnbindRMB
		if role.GetUnbindRMB() < needRMB:
			return
	elif needRMBType == 1:
		DECRMB_FUN = role.DecUnbindRMB_Q
		if role.GetUnbindRMB_Q() < needRMB:
			return
	else:
		return
	
	rewardInfo = topicCfg.randomObj.RandomOne()
	if not rewardInfo:
		print "GE_EXC, DETopicMgr::OnLotteryYiCi can not random reward by config with topicId(%s)" % topicCfg.topicId
		return
	
	_, itemIndex, coding, cnt, isPrecious = rewardInfo
	with Tra_DETopic_LotteryYiCi:
		#扣钱
		DECRMB_FUN(needRMB)
		#增加抽奖次数记录
		role.IncI16(EnumInt16.DETopicLotteryCnt, 1)
	
	#回调
	role.SendObjAndBack(DETopic_LotteryResult_SB, itemIndex, 8, LotteryCallBack, [role.GetRoleID(), role.GetRoleName(), coding, cnt, isPrecious])


def OnLotteryShiCi(role, msg = None):
	'''
	专题转盘_请求抽奖十次
	'''
	#屏蔽10次抽奖
	return
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.DETopic_NeedLevel:
		return
	
	topicId = role.GetI8(EnumInt8.DETopicTodayTopicId)
	topicCfg = DETopicConfig.DETopic_BaseConfig_Dict.get(topicId, None)
	if not topicCfg:
		print "GE_EXC,DETopicMgr::OnLotteryShiCi can not get topic config by topicId(%s), role(%s)" % (topicId, role.GetRoleID()) 
		return
	
	lotteryCnt = role.GetI16(EnumInt16.DETopicLotteryCnt)
	if lotteryCnt + 10 > topicCfg.dayMaxLotteryCnt:
		return
	
	
	needRMB = topicCfg.tenNeedRMB
	needRMBType = topicCfg.needRMBType
	if needRMBType == 0:
		DECRMB_FUN = role.DecUnbindRMB
		if role.GetUnbindRMB() < needRMB:
			return
	elif needRMBType == 1:
		DECRMB_FUN = role.DecUnbindRMB_Q
		if role.GetUnbindRMB_Q() < needRMB:
			return
	else:
		return
	
	reward_Dict = {}
	preciousReward_List = []
	roleName = role.GetRoleName()
	randomObj = topicCfg.randomObj
	for _ in xrange(10):
		rewardInfo = randomObj.RandomOne()
		if not rewardInfo:
			print "GE_EXC, DETopicMgr::OnLotteryShiCi can not random reward by config with topicId(%s)" % topicCfg.topicId
			continue
		
		_, _, coding, cnt, isPrecious = rewardInfo
		reward_Dict[coding] = reward_Dict.get(coding,0) + cnt
		if isPrecious:
			preciousReward_List.append((roleName, coding, cnt,))
	
	if len(reward_Dict) < 1:
		print "GE_EXC, DETopicMgr::OnLotteryShiCi no reward!"
		return
	
	prompt = GlobalPrompt.DETopic_Tips_ShiCiHead
	with Tra_DETopic_LotteryShiCi:
		#扣钱
		DECRMB_FUN(needRMB)
		#增加抽奖次数记录
		role.IncI16(EnumInt16.DETopicLotteryCnt, 10)
		#获得
		for coding, cnt in reward_Dict.iteritems():
			role.AddItem(coding, cnt)
			prompt += GlobalPrompt.Item_Tips % (coding, cnt)
		
	
	#提示
	role.Msg(2, 0, prompt)
	#珍惜奖励处理
	if len(preciousReward_List) > 0:
		global DETopic_PreciousRecord_List
		for preciousInfo in preciousReward_List:
			if len(DETopic_PreciousRecord_List) >= EnumGameConfig.DETopic_PreciousRecordMaxSize:
				DETopic_PreciousRecord_List.pop(0)
			DETopic_PreciousRecord_List.append(preciousInfo)
			
		#同步最新珍贵奖励记录给缓存的role
		invalidRoleSet = set()
		global DETopic_OpenPanelRole_Set
		for tmpRoleId in DETopic_OpenPanelRole_Set:
			tmpRole = cRoleMgr.FindRoleByRoleID(tmpRoleId)
			if not tmpRole:
				invalidRoleSet.add(tmpRoleId)
				continue
			tmpRole.SendObj(DETopic_PreciousRecord_S, DETopic_PreciousRecord_List)
			
		#删除缓存的无效roleId
		if len(invalidRoleSet) > 0:
			DETopic_OpenPanelRole_Set.difference_update(invalidRoleSet)	


#===============================================================================
# 辅助
#===============================================================================
def LotteryCallBack(role, callargv, regparam):
	'''
	转盘抽奖结果回调处理
	'''
	roleId, roleName, coding, cnt, isPrecious = regparam
	
	#珍贵奖励记录处理
	if isPrecious:
		global DETopic_PreciousRecord_List
		preciousInfo = (roleName, coding, cnt)
		if len(DETopic_PreciousRecord_List) >= EnumGameConfig.DETopic_PreciousRecordMaxSize:
			DETopic_PreciousRecord_List.pop(0)
		DETopic_PreciousRecord_List.append(preciousInfo)
		
		#同步最新珍贵奖励记录给缓存的role
		invalidRoleSet = set()
		global DETopic_OpenPanelRole_Set
		for tmpRoleId in DETopic_OpenPanelRole_Set:
			tmpRole = cRoleMgr.FindRoleByRoleID(tmpRoleId)
			if not tmpRole:
				invalidRoleSet.add(tmpRoleId)
				continue
			tmpRole.SendObj(DETopic_PreciousRecord_S, DETopic_PreciousRecord_List)
		
		#删除缓存的无效roleId
		if len(invalidRoleSet) > 0:
			DETopic_OpenPanelRole_Set.difference_update(invalidRoleSet)
		
	Call.LocalDBCall(roleId, RealAward, (coding, cnt))


#离线命令 最终发奖励 确保一定到位
def RealAward(role, param):
	'''
	抽奖最终发奖励
	'''	
	coding, cnt = param
	with Tra_DETopic_LotteryYiCi:
		#获得
		role.AddItem(coding, cnt)	
		
	#提示
	role.Msg(2, 0, GlobalPrompt.DETopic_Tips_YiCiHead + GlobalPrompt.Item_Tips % (coding, cnt))


def CalculateDayIndex():
	'''
	计算当前活动开启天数
	'''
	#活动开始的天数
	baseCfg = DETopicConfig.DETopicActive_cfg 
	if not baseCfg:
		print "GE_EXC,CircularActive.DETopicActive_cfg is None"
		return
	
	#当前日期时间
	nowDate = cDateTime.Now()
	#活动持续开启的天数
	durableDay = (nowDate - baseCfg.beginTime).days
	#更新全局DAY_INDEX
	global DAYINDEX
	DAYINDEX = durableDay + 1	
	#超过 强制设置最后一天
	if DAYINDEX > baseCfg.totalDay:
		DAYINDEX = baseCfg.totalDay


def OnRoleDayClear(role, param = None):
	'''
	跨天处理
	1.重置专题ID
	2.重置转盘次数
	'''
	#清理抽奖次数
	role.SetI16(EnumInt16.DETopicLotteryCnt, 0)
	
	#活动继续开启 同步更新相关与天数有关数据
	if IS_START:
		#等级不足 无法参与 不需要初始化
		if role.GetLevel() < EnumGameConfig.DEQiangHongBao_NeedLevel:
			return
		
		with Tra_DETopic_InitTopicId:
			role.SetI8(EnumInt8.DETopicTodayTopicId, DETopicConfig.GetTopicIdByDayAndLevel(DAYINDEX, role.GetLevel()))
		

def OnSyncRoleOtherData(role, param = None):
	'''
	上线同步
	'''
	#活动开启同步
	if IS_START:
		role.SendObj(DETopic_ActiveState_S, (IS_START, ENDTIME))
		
		#等级不足 参与不了活动 不用初始数据
		if role.GetLevel() < EnumGameConfig.DETopic_NeedLevel:
			return
		
		#当前数据OK 无需重置
		oldTopicId = role.GetI8(EnumInt8.DETopicTodayTopicId)
		todayTopicId = DETopicConfig.GetTopicIdByDayAndLevel(DAYINDEX, role.GetLevel())
		if oldTopicId == todayTopicId:
			return
		
		with Tra_DETopic_InitTopicId:
			role.SetI8(EnumInt8.DETopicTodayTopicId, todayTopicId)

		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
	
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		cComplexServer.RegAfterNewDayCallFunction(CalculateDayIndex)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DETopic_OnOpenPanel", "专题转盘_请求打开操作面板"), OnOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DETopic_OnClosePanel", "专题转盘_请求关闭操作面板"), OnClosePanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DETopic_OnLotteryYiCi", "专题转盘_请求抽奖一次"), OnLotteryYiCi)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DETopic_OnLotteryShiCi", "专题转盘_请求抽奖十次"), OnLotteryShiCi)
		