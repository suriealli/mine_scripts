#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.GuBaoTanMi.GuBaoTanMiMgr")
#===============================================================================
# 古堡探秘 Mgr
#===============================================================================
import cProcess
import cRoleMgr
import cNetMessage
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event, Call
from Game.Persistence import Contain
from Game.GlobalData import ZoneName
from Game.Activity.GuBaoTanMi import GuBaoTanMiConfig


CT_TANMI = 1
CT_EXCHANGE = 2


if "_HasLoad" not in dir():
	#活动开关标志
	IS_START = False
	#活动结束时间戳
	ENDTIME = 0
	#打开操作界面的角色ID缓存集合
	GuBaoTanMi_BroadRoleID_Set = set()
	#大奖记录 格式：[[zoneName,roleName,coding1,cnt1,coding2,cnt2],] PS:因为两种记录格式差异 若coding2和cnt2为零 表示探秘中奖纪录 否则表示兑换特殊奖励记录
	GuBaoTanMi_PreciousRecord_List = []
	#活动状态同步 格式: endTime (非零表示活动结束时间戳，零表示告知活动结束！)
	GuBaoTanMi_ActiveState_S = AutoMessage.AllotMessage("GuBaoTanMi_ActiveState_S", "古堡探秘_活动状态同步")
	#累计探秘解锁奖励数据 {1:累计探秘次数, 2:set(已领取的 rewardIndex 集合)} PS:里面的key可选
	GuBaoTanMi_UnlockRewardData_S = AutoMessage.AllotMessage("GuBaoTanMi_UnlockRewardData_S", "古堡探秘_累计探秘解锁奖励数据")
	#大奖记录同步 
	GuBaoTanMi_PreciousRecord_S = AutoMessage.AllotMessage("GuBaoTanMi_PreciousRecord_S", "古堡探秘_大奖记录同步")
	
	Tra_GuBaoTanMi_TanMiYiCi = AutoLog.AutoTransaction("Tra_GuBaoTanMi_TanMiYiCi", "古堡探秘_探秘一次")
	Tra_GuBaoTanMi_TanMiShiCi = AutoLog.AutoTransaction("Tra_GuBaoTanMi_TanMiShiCi", "古堡探秘_探秘十次")
	Tra_GuBaoTanMi_TanMiWuShiCi = AutoLog.AutoTransaction("Tra_GuBaoTanMi_TanMiWuShiCi", "古堡探秘_探秘五十次")
	Tra_GuBaoTanMi_SpeciousBox = AutoLog.AutoTransaction("Tra_GuBaoTanMi_SpeciousBox", "古堡探秘_兑换特殊奖励")
	Tra_GuBaoTanMi_UnlockReward = AutoLog.AutoTransaction("Tra_GuBaoTanMi_UnlockReward", "古堡探秘_累计探秘解锁奖励")

#===============================================================================
# 活动控制
#===============================================================================
def OpenActive(callArgv, regparam):
	'''
	古堡探秘-开启
	'''
	global ENDTIME
	global IS_START
	global GuBaoTanMi_UnlockReward_Dict
	
	if IS_START:
		print 'GE_EXC, repeat start GuBaoTanMi'
		return
	IS_START = True
	
	activeID, endTime = regparam
	if activeID != GuBaoTanMi_UnlockReward_Dict.get('activeID'):
		GuBaoTanMi_UnlockReward_Dict.clear()
		GuBaoTanMi_UnlockReward_Dict['activeID'] = activeID
		GuBaoTanMi_UnlockReward_Dict.HasChange()
	
	ENDTIME = endTime
	
	cNetMessage.PackPyMsg(GuBaoTanMi_ActiveState_S, endTime)
	cRoleMgr.BroadMsg()
	
def CloseActive(callArgv, regparam):
	'''
	古堡探秘-结束
	'''
	global ENDTIME
	global IS_START
	global GuBaoTanMi_BroadRoleID_Set
	global GuBaoTanMi_PreciousRecord_List
	
	if not IS_START:
		print 'GE_EXC, repeat end GuBaoTanMi'
		return
	IS_START = False
	
	#活动结束后清理
	GuBaoTanMi_BroadRoleID_Set = set()
	GuBaoTanMi_PreciousRecord_List = []
	
	cNetMessage.PackPyMsg(GuBaoTanMi_ActiveState_S, 0)
	cRoleMgr.BroadMsg()


#===============================================================================
# 客户端请求
#===============================================================================
def OnOpenPanel(role, msg = None):
	'''
	古堡探秘_客户端请求打开操作面板
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.GuBaoTanMi_NeedLevel:
		return
	
	global GuBaoTanMi_BroadRoleID_Set
	GuBaoTanMi_BroadRoleID_Set.add(role.GetRoleID())
	
	role.SendObj(GuBaoTanMi_PreciousRecord_S, GuBaoTanMi_PreciousRecord_List)
	role.SendObj(GuBaoTanMi_UnlockRewardData_S, GuBaoTanMi_UnlockReward_Dict.get(role.GetRoleID(),{}))
	

def OnClosePanel(role, msg = None):
	'''
	古堡探秘_客户端请求关闭操作面板
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.GuBaoTanMi_NeedLevel:
		return
	
	global GuBaoTanMi_BroadRoleID_Set
	GuBaoTanMi_BroadRoleID_Set.discard(role.GetRoleID())
	

def OnTanMiYiCi(role, msg = None):
	'''
	古堡探秘_客户端请求探秘一次
	'''
	if not IS_START:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.GuBaoTanMi_NeedLevel:
		return
	
	#统计探秘道具和神石需求
	tanMiCnt = 1
	haveFDJCnt = role.ItemCnt(EnumGameConfig.GuBaoTanMi_FangDaJing)
	needFDJCnt = min(haveFDJCnt, tanMiCnt)
	costRMB = EnumGameConfig.GuBaoTanMi_YiCiRMB
	if Environment.EnvIsNA():
		costRMB = EnumGameConfig.GuBaoTanMi_YiCiRMB_NA
	needRMB = max(0, (tanMiCnt - haveFDJCnt) * costRMB)
	
	#判断实际是否足够
	if role.GetUnbindRMB_Q() < needRMB or role.ItemCnt(EnumGameConfig.GuBaoTanMi_FangDaJing) < needFDJCnt:
		return
	
	with Tra_GuBaoTanMi_TanMiYiCi:
		DoTanMi(role, tanMiCnt, needFDJCnt, needRMB)
	
def OnTanMiShiCi(role, msg = None):
	'''
	古堡探秘_客户端请求探秘十次
	'''
	if not IS_START:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.GuBaoTanMi_NeedLevel:
		return
	
	#统计探秘道具和神石需求
	tanMiCnt = 10
	haveFDJCnt = role.ItemCnt(EnumGameConfig.GuBaoTanMi_FangDaJing)
	needFDJCnt = min(haveFDJCnt, tanMiCnt)
	costRMB = EnumGameConfig.GuBaoTanMi_YiCiRMB
	if Environment.EnvIsNA():
		costRMB = EnumGameConfig.GuBaoTanMi_YiCiRMB_NA
	needRMB = max(0, (tanMiCnt - haveFDJCnt) * costRMB)
	
	#判断实际是否足够
	if role.GetUnbindRMB_Q() < needRMB or role.ItemCnt(EnumGameConfig.GuBaoTanMi_FangDaJing) < needFDJCnt:
		return
	
	with Tra_GuBaoTanMi_TanMiShiCi:
		DoTanMi(role, tanMiCnt, needFDJCnt, needRMB)


def OnTanMiWuShiCi(role, msg = None):
	'''
	古堡探秘_客户端请求探秘五十次
	'''
	if not IS_START:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.GuBaoTanMi_NeedLevel:
		return
	
	#统计探秘道具和神石需求
	tanMiCnt = 50
	haveFDJCnt = role.ItemCnt(EnumGameConfig.GuBaoTanMi_FangDaJing)
	needFDJCnt = min(haveFDJCnt, tanMiCnt)
	costRMB = EnumGameConfig.GuBaoTanMi_YiCiRMB
	if Environment.EnvIsNA():
		costRMB = EnumGameConfig.GuBaoTanMi_YiCiRMB_NA
	needRMB = max(0, (tanMiCnt - haveFDJCnt) * costRMB)
	
	#判断实际是否足够
	if role.GetUnbindRMB_Q() < needRMB or role.ItemCnt(EnumGameConfig.GuBaoTanMi_FangDaJing) < needFDJCnt:
		return
	
	with Tra_GuBaoTanMi_TanMiWuShiCi:
		DoTanMi(role, tanMiCnt, needFDJCnt, needRMB)
		

def OnGetSpeciousBox(role, msg):
	'''
	古堡探秘_客户端请求领取特殊宝箱
	'''
	if not IS_START:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.GuBaoTanMi_NeedLevel:
		return
	
	rewardIndex = msg
	rewardCfg = GuBaoTanMiConfig.GetSRCfgByLevelAndIndex(roleLevel, rewardIndex)
	if not rewardCfg:
		return
	
	needCoding, needCnt = rewardCfg.needItem
	if role.ItemCnt(needCoding) < needCnt:
		return
	
	if role.PackageEmptySize() < 1:
		role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
		return
	
	with Tra_GuBaoTanMi_SpeciousBox:
		#扣除消耗
		role.DelItem(needCoding, needCnt)
		#获得道具
		coding, cnt = rewardCfg.rewardItem
		role.AddItem(coding, cnt)
		#提示
		role.Msg(2, 0, GlobalPrompt.Reward_Tips + GlobalPrompt.Item_Tips % (coding, cnt))
		#广播&记录
		roleName = role.GetRoleName()
		cRoleMgr.Msg(1, 0, GlobalPrompt.GuBaoTanMi_MSg_Special % (roleName, rewardCfg.needItemName, coding, cnt))
		Call.ServerCall(0, "Game.Activity.GuBaoTanMi.GuBaoTanMiMgr", "AllServerPrecious", (ZoneName.GetRoleZoneName(role), roleName, CT_EXCHANGE, [needCoding, needCnt, coding, cnt]))
	
		
def OnGetUnlockReward(role, msg):
	'''
	古堡探秘_客户端请求领取累计探秘解锁奖励
	'''
	if not IS_START:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.GuBaoTanMi_NeedLevel:
		return
	
	rewardIndex = msg
	rewardCfg = GuBaoTanMiConfig.GetUnlockRewardByIndex(rewardIndex)
	if not rewardCfg:
		return
	
	if role.PackageEmptySize() < 5:
		role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
		return
	
	#初始化判断
	global GuBaoTanMi_UnlockReward_Dict
	roleId = role.GetRoleID()
	if roleId not in GuBaoTanMi_UnlockReward_Dict:
		GuBaoTanMi_UnlockReward_Dict[roleId] = {1:0,2:set()}
		GuBaoTanMi_UnlockReward_Dict.HasChange()
	
	#已经领取
	roleTanMiDataDict = GuBaoTanMi_UnlockReward_Dict[roleId]
	roleRewardSet = roleTanMiDataDict[2]
	if rewardIndex in roleRewardSet:
		return
	
	#累计探秘次数不足
	if roleTanMiDataDict[1] < rewardCfg.needTanMiCnt:
		return
	
	prompt = GlobalPrompt.Reward_Tips
	with Tra_GuBaoTanMi_UnlockReward:
		#领奖记录
		roleRewardSet.add(rewardIndex)
		GuBaoTanMi_UnlockReward_Dict.HasChange()
		#获得
		for coding, cnt in rewardCfg.rewardItems:
			role.AddItem(coding, cnt)
			prompt += GlobalPrompt.Item_Tips % (coding, cnt)
	
	#提示
	role.Msg(2, 0, prompt)
	#同步最新数据
	role.SendObj(GuBaoTanMi_UnlockRewardData_S, roleTanMiDataDict)


#===============================================================================
#辅助
#===============================================================================
def DoTanMi(role, tanMiCnt, needFDJCnt, needRMB):
	'''
	处理批量探秘操作
	'''
	roleLevel = role.GetLevel()
	randomObj = GuBaoTanMiConfig.GetRandomObjByLevel(roleLevel)
	if not randomObj:
		print "GE_EXC, OnTanMiYiCi::can not get randomObj By roleLevel(%s) role(%s)" % (roleLevel, role.GetRoleID())
		return
	
	#装载本次随机奖励
	rewardDict = {}
	specialList = []
	for _ in xrange(tanMiCnt):
		rewardInfo = randomObj.RandomOne()
		_, coding, cnt, isPrecious = rewardInfo
		if coding in rewardDict:
			rewardDict[coding] += cnt
		else:
			rewardDict[coding] = cnt
		
		if isPrecious:
			specialList.append([coding, cnt])
	
	#process
	prompt = GlobalPrompt.Reward_Tips
	#累计探秘次数
	roleId = role.GetRoleID()
	global GuBaoTanMi_UnlockReward_Dict
	if roleId not in GuBaoTanMi_UnlockReward_Dict:
		GuBaoTanMi_UnlockReward_Dict[roleId] = {1:tanMiCnt,2:set()}
	else:
		GuBaoTanMi_UnlockReward_Dict[roleId][1] += tanMiCnt
	GuBaoTanMi_UnlockReward_Dict.HasChange()
	#消耗神石 和 探秘道具
	if needFDJCnt > 0:
		role.DelItem(EnumGameConfig.GuBaoTanMi_FangDaJing, needFDJCnt)
	if needRMB > 0:
		role.DecUnbindRMB_Q(needRMB)
	#获得道具
	for coding, cnt in rewardDict.iteritems():
		role.AddItem(coding, cnt)
		prompt += GlobalPrompt.Item_Tips % (coding, cnt)	
	#同步客户端最新数据
	role.SendObj(GuBaoTanMi_UnlockRewardData_S, GuBaoTanMi_UnlockReward_Dict[roleId])
	
	#提示 广播 记录处理
	role.Msg(2, 0, prompt)
	if len(specialList) > 0:
		roleName = role.GetRoleName()
		Call.ServerCall(0, "Game.Activity.GuBaoTanMi.GuBaoTanMiMgr", "AllServerPrecious", (ZoneName.GetRoleZoneName(role), roleName, CT_TANMI, specialList))
		for coding, cnt in specialList:
			cRoleMgr.Msg(1, 0, GlobalPrompt.GuBaoTanMi_Msg_Precious % (roleName, coding, cnt))
			
			
#===============================================================================
# ServerCall函数
#===============================================================================
def AllServerPrecious(param):
	'''
	大奖记录处理
	@param param: processId, roleName, coding1, cnt1, coding2, cnt2
	若 coding2为零 则表示探秘中大奖 否则表示领取特殊奖励
	'''
	global GuBaoTanMi_BroadRoleID_Set
	global GuBaoTanMi_PreciousRecord_List
	zName, roleName, callType, realParam = param
	
	if callType == CT_TANMI:
		specialList = realParam
		for coding, cnt in specialList:
			if len(GuBaoTanMi_PreciousRecord_List) > 100:
				GuBaoTanMi_PreciousRecord_List.pop(0)
			GuBaoTanMi_PreciousRecord_List.append([zName, roleName, coding, cnt, 0, 0])
	elif callType == CT_EXCHANGE:
		coding1, cnt1, coding2, cnt2 = realParam
		if len(GuBaoTanMi_PreciousRecord_List) > 100:
			GuBaoTanMi_PreciousRecord_List.pop(0)
		GuBaoTanMi_PreciousRecord_List.append([zName, roleName, coding1, cnt1, coding2, cnt2])
	else:
		return
	
	invalidRoleSet = set()
	for roleId in GuBaoTanMi_BroadRoleID_Set:
		role = cRoleMgr.FindRoleByRoleID(roleId)
		if not role or role.IsLost() or role.IsKick():
			invalidRoleSet.add(roleId)
			continue
		role.SendObj(GuBaoTanMi_PreciousRecord_S, GuBaoTanMi_PreciousRecord_List)
	
	GuBaoTanMi_BroadRoleID_Set.difference_update(invalidRoleSet)
	
	
#===============================================================================
#事件
#===============================================================================
def OnSyncOtherData(role, param = None):
	'''
	角色上线同步活动状态
	'''
	if not IS_START:
		return
	
	role.SendObj(GuBaoTanMi_ActiveState_S, ENDTIME)


def OnRoleOffLine(role, param = None):
	'''
	角色离线
	'''
	if not IS_START:
		return
	
	global GuBaoTanMi_BroadRoleID_Set
	GuBaoTanMi_BroadRoleID_Set.discard(role.GetRoleID())
	

def AfterLoadGuBaoTanMi():
	if not GuBaoTanMi_UnlockReward_Dict:
		#活动id不一样的时候清理数据
		GuBaoTanMi_UnlockReward_Dict["activeID"] = 0
		GuBaoTanMi_UnlockReward_Dict.HasChange()
	
	#持久化数据载回后尝试开启
	from Game.Activity import CircularActive
	for cfg in CircularActive.GuBaoTanMiActive_Dict.itervalues():
		cfg.Active()


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#格式 {roleId:{1:TanMiCnt,2:set(rewardIndex1,rewardIndex2,)}} 1-探秘次数 2-累计探秘奖励领取记录
		GuBaoTanMi_UnlockReward_Dict = Contain.Dict("GuBaoTanMi_UnlockReward_Dict", (2038, 1, 1), AfterLoadGuBaoTanMi)
		
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncOtherData)
		Event.RegEvent(Event.Eve_ClientLost, OnRoleOffLine)
		Event.RegEvent(Event.Eve_BeforeExit, OnRoleOffLine)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GuBaoTanMi_OnOpenPanel", "古堡探秘_客户端请求打开操作面板"), OnOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GuBaoTanMi_OnClosePanel", "古堡探秘_客户端请求关闭操作面板"), OnClosePanel)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GuBaoTanMi_OnTanMiYiCi", "古堡探秘_客户端请求探秘一次"), OnTanMiYiCi)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GuBaoTanMi_OnTanMiShiCi", "古堡探秘_客户端请求探秘十次"), OnTanMiShiCi)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GuBaoTanMi_OnTanMiWuShiCi", "古堡探秘_客户端请求探秘五十次"), OnTanMiWuShiCi)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GuBaoTanMi_OnGetSpeciousBox", "古堡探秘_客户端请求领取特殊宝箱"), OnGetSpeciousBox)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GuBaoTanMi_OnGetUnlockReward", "古堡探秘_客户端请求领取累计探秘解锁奖励"), OnGetUnlockReward)
