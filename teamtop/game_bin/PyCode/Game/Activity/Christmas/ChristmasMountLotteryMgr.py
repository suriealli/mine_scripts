#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.Christmas.ChristmasMountLotteryMgr")
#===============================================================================
# 圣诞坐骑转转乐Mgr
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Call, Event
from Game.Role.Data import EnumDayInt8, EnumInt32
from Game.Activity import CircularDefine
from Game.Activity.Christmas import ChristmasMountLotteryConfig

if "_HasLoad" not in dir():
	IS_START = False
	ChristmasMountLottery_OnlineRole_Set = set()	#缓存打开面板的角色ID
	ChristmasMountLottery_PreciousRecord_List = []	#缓存大奖记录[(roleName,coding,cnt)]
	
	Tra_ChristmasMountLottery_SingleLottery = AutoLog.AutoTransaction("Tra_ChristmasMountLottery_SingleLottery", "圣诞坐骑转转乐_单次抽奖")
	Tra_ChristmasMountLottery_BatchLottery = AutoLog.AutoTransaction("Tra_ChristmasMountLottery_BatchLottery", "圣诞坐骑转转乐_批量抽奖")

	ChristmasMountLottery_PreciousRecord_S = AutoMessage.AllotMessage("ChristmasMountLottery_PreciousRecord_S", "圣诞坐骑转转乐_大奖记录同步")
	ChristmasMountLottery_LotteryResult_SB = AutoMessage.AllotMessage("ChristmasMountLottery_LotteryResult_SB", "圣诞坐骑转转乐_抽奖结果同步回调")

#### 活动控制  start ####
def OnStartMountLottery(*param):
	'''
	开启活动
	'''
	_, circularType = param
	if CircularDefine.CA_ChristmasMountLottery != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open MountLottery"
		return
		
	IS_START = True

def OnEndMountLottery(*param):
	'''
	结束活动
	'''
	_, circularType = param
	if CircularDefine.CA_ChristmasMountLottery != circularType:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC, end MountLottery while not start"
		return
		
	IS_START = False

#### 请求start
def OnOpenPanel(role, msg = None):
	'''
	请求打开面板
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.ChristmasMountLottery_NeedLevel:
		return
	
	#缓存该玩家已打开面板
	global ChristmasMountLottery_OnlineRole_Set
	ChristmasMountLottery_OnlineRole_Set.add(role.GetRoleID())
	#同步当前大奖记录
	role.SendObj(ChristmasMountLottery_PreciousRecord_S, ChristmasMountLottery_PreciousRecord_List)

def OnClosePanel(role, msg = None):
	'''
	请求关闭面板
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.ChristmasMountLottery_NeedLevel:
		return
	
	#清除缓存该玩家已打开面板
	global ChristmasMountLottery_OnlineRole_Set
	ChristmasMountLottery_OnlineRole_Set.discard(role.GetRoleID())

def OnSingleLottery(role, msg = None):
	'''
	单次抽奖请求
	'''
	if not IS_START:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.ChristmasMountLottery_NeedLevel:
		return
	
	#判定消耗 神石 or 免费次数
	needUnbindRMB = 0
	needLotteryTimes = 0
	effectFreeTimes = role.GetDI8(EnumDayInt8.ChristmasMountLotteryFreeTimes)
	if effectFreeTimes < 1:
		needUnbindRMB = EnumGameConfig.ChristmasMountLottery_LotteryCost
		if Environment.EnvIsNA():
			needUnbindRMB = EnumGameConfig.ChristmasMountLottery_LotteryCost_NA
	else:
		needLotteryTimes = 1
		needUnbindRMB = EnumGameConfig.ChristmasMountLottery_DiscountCost
		if Environment.EnvIsNA():
			needUnbindRMB = EnumGameConfig.ChristmasMountLottery_DiscountCost_NA
	
	#需要神石且神石不足
	if needUnbindRMB > 0 and role.GetUnbindRMB() < needUnbindRMB:
		return
	
	randomObj = ChristmasMountLotteryConfig.GetRandomObjByLevel(roleLevel)
	if not randomObj:
		print "GE_EXC, MountLottery::OnSingleLottery::can not get randomObj by roleLevel(%s)" % roleLevel
		return
	
	reward = randomObj.RandomOne()
	if not reward:
		print "GE_EXC, MountLottery::OnSingleLottery:: randomObj.RandomOne() is None"
		return
	
	#扣消耗
	with Tra_ChristmasMountLottery_SingleLottery:
		#扣神石 加积分
		if needUnbindRMB > 0:
			role.DecUnbindRMB(needUnbindRMB)
			role.IncI32(EnumInt32.ChristmasConsumeExp, needUnbindRMB)
		#扣折扣次数
		if needLotteryTimes > 0:
			role.DecDI8(EnumDayInt8.ChristmasMountLotteryFreeTimes, 1)
			AutoLog.LogBase(role.GetRoleID(), AutoLog.eveChristmasMountLotteryDiscountLottery, needLotteryTimes)
	
	#积分提示
	if needUnbindRMB > 0:
		role.Msg(2, 0, GlobalPrompt.Christmas_Tips_ConsumeEXp % needUnbindRMB)
			
	#抽奖结果 同步回调
	roleId = role.GetRoleID()
	roleName = role.GetRoleName()
	rewardId, itemIndex, coding, cnt, isPrecious = reward
	role.SendObjAndBack(ChristmasMountLottery_LotteryResult_SB, (itemIndex, rewardId), 8, OnSingleLotteryCallBack, (roleId, roleName, coding, cnt, isPrecious))

def OnBatchLottery(role, msg = None):
	'''
	批量抽奖请求
	'''
	if not IS_START:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.ChristmasMountLottery_NeedLevel:
		return
	
	#判定神石 和 免费次数消耗
	needUnbindRMB = 0
	freeTimesCost = EnumGameConfig.ChristmasMountLottery_BatchLotteryNum
	effectFreeTimes = role.GetDI8(EnumDayInt8.ChristmasMountLotteryFreeTimes)
	if effectFreeTimes < EnumGameConfig.ChristmasMountLottery_BatchLotteryNum:
		needUnbindRMB = (EnumGameConfig.ChristmasMountLottery_BatchLotteryNum - effectFreeTimes) * EnumGameConfig.ChristmasMountLottery_LotteryCost
		if Environment.EnvIsNA():
			needUnbindRMB = (EnumGameConfig.ChristmasMountLottery_BatchLotteryNum - effectFreeTimes) * EnumGameConfig.ChristmasMountLottery_LotteryCost_NA
		freeTimesCost = effectFreeTimes
	else:
		pass
	
	#免费次数改成了折扣次数 补上所需神石
	needUnbindRMB += freeTimesCost * EnumGameConfig.ChristmasMountLottery_DiscountCost
	if Environment.EnvIsNA():
		needUnbindRMB += freeTimesCost * EnumGameConfig.ChristmasMountLottery_DiscountCost_NA
	
	if needUnbindRMB > 0 and role.GetUnbindRMB() < needUnbindRMB:
		return
	
	#抽奖随机器
	randomObj = ChristmasMountLotteryConfig.GetRandomObjByLevel(roleLevel)
	if not randomObj:
		print "GE_EXC, ChristmasMountLottery::OnBatchLottery:: can not get randomObj by roleLevel(%s)" % roleLevel
		return
	
	#组装奖励字典
	rewardDict = {}		#{coding:cnt,}
	preciousRewardList = []	#[(coding,cnt)]
	for _ in xrange(EnumGameConfig.ChristmasMountLottery_BatchLotteryNum):
		reward = randomObj.RandomOne()
		if not reward:
			print "GE_EXC,ChristmasMountLottery::OnBatchLottery:: randomObj.RandomOne() is None"
			continue

		_, _, coding, cnt, isPrecious = reward
		if coding in rewardDict:
			rewardDict[coding] += cnt
		else:
			rewardDict[coding] = cnt
		
		if isPrecious:
			preciousInfo = (coding, cnt)
			preciousRewardList.append(preciousInfo)	
		
	#奖励字典为空
	if len(rewardDict) < 1:
		print "GE_EXC, ChristmasMountLottery::OnBatchLottery:: len(rewardDict) < 1 "
		return
	
	#扣除消耗
	rewardPrompt = GlobalPrompt.ChristmasMountLottery_Tips_Head
	roleName = role.GetRoleName()
	with Tra_ChristmasMountLottery_BatchLottery:
		#神石
		if needUnbindRMB > 0:
			role.DecUnbindRMB(needUnbindRMB)
			role.IncI32(EnumInt32.ChristmasConsumeExp, needUnbindRMB)
		#免费次数
		if freeTimesCost > 0:
			role.DecDI8(EnumDayInt8.ChristmasMountLotteryFreeTimes, freeTimesCost)
			AutoLog.LogBase(role.GetRoleID(), AutoLog.eveChristmasMountLotteryDiscountLottery, freeTimesCost)
		#发奖励
		for tmpCoding, tmpCnt in rewardDict.iteritems():
			role.AddItem(tmpCoding, tmpCnt)
			rewardPrompt += GlobalPrompt.ChristmasMountLottery_Tips_Item % (tmpCoding, tmpCnt)
	
	#抽奖提示
	role.Msg(2, 0, rewardPrompt)
	
	#积分提示
	if needUnbindRMB > 0:
		role.Msg(2, 0, GlobalPrompt.Christmas_Tips_ConsumeEXp % needUnbindRMB)
		
	#大奖处理
	if len(preciousRewardList) > 0:
		global ChristmasMountLottery_PreciousRecord_List
		for tmpPreciousInfo in preciousRewardList:
			coding, cnt = tmpPreciousInfo
			if len(ChristmasMountLottery_PreciousRecord_List) >= EnumGameConfig.ChristmasMountLottery_RecordMaxNum:
				ChristmasMountLottery_PreciousRecord_List.pop(0)
			ChristmasMountLottery_PreciousRecord_List.append((roleName, coding, cnt))
		
		#同步最新珍贵奖励记录给缓存的role
		invalidRoleSet = set()
		global ChristmasMountLottery_OnlineRole_Set
		for tmpRoleId in ChristmasMountLottery_OnlineRole_Set:
			tmpRole = cRoleMgr.FindRoleByRoleID(tmpRoleId)
			if not tmpRole:
				invalidRoleSet.add(tmpRoleId)
				continue
			tmpRole.SendObj(ChristmasMountLottery_PreciousRecord_S, ChristmasMountLottery_PreciousRecord_List)
		
		#删除缓存的无效roleId
		if len(invalidRoleSet) > 0:
			ChristmasMountLottery_OnlineRole_Set.difference_update(invalidRoleSet)
	else:
		pass

def OnSingleLotteryCallBack(role, calArgv, regParam):
	'''
	抽奖回调
	'''
	roleId, roleName, coding, cnt, isPrecious = regParam
	#大奖处理
	if isPrecious:
		global ChristmasMountLottery_PreciousRecord_List
		preciousInfo = (roleName, coding, cnt)
		if len(ChristmasMountLottery_PreciousRecord_List) >= EnumGameConfig.ChristmasMountLottery_RecordMaxNum:
			ChristmasMountLottery_PreciousRecord_List.pop(0)
		ChristmasMountLottery_PreciousRecord_List.append(preciousInfo)
		
		#同步最新珍贵奖励记录给缓存的role
		invalidRoleSet = set()
		global ChristmasMountLottery_OnlineRole_Set
		for tmpRoleId in ChristmasMountLottery_OnlineRole_Set:
			tmpRole = cRoleMgr.FindRoleByRoleID(tmpRoleId)
			if not tmpRole:
				invalidRoleSet.add(tmpRoleId)
				continue
			tmpRole.SendObj(ChristmasMountLottery_PreciousRecord_S, ChristmasMountLottery_PreciousRecord_List)
		
		#删除缓存的无效roleId
		if len(invalidRoleSet) > 0:
			ChristmasMountLottery_OnlineRole_Set.difference_update(invalidRoleSet)
		
	Call.LocalDBCall(roleId, LotteryRealAward, (coding, cnt))

def LotteryRealAward(role, param):
	'''
	回调实际发奖励
	'''
	coding, cnt = param
	with Tra_ChristmasMountLottery_SingleLottery:
		#物品获得
		role.AddItem(coding, cnt)
		#获得提示
		role.Msg(2, 0, GlobalPrompt.ChristmasMountLottery_Tips_Head + GlobalPrompt.ChristmasMountLottery_Tips_Item % (coding, cnt))

def OnIncLotteryTime(role, param):
	'''
	参加活动 触发增加抽奖次数
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.ChristmasMountLottery_NeedLevel:
		return
	
	#参数不对不处理
	source = param
	if source not in EnumGameConfig.Source_List:
		return
	
	#今日已经增加对应次数
	incRecord = role.GetDI8(EnumDayInt8.ChristmasIncRecordMountLottery)
	if incRecord & source:
			return
	
	#写记录
	role.IncDI8(EnumDayInt8.ChristmasIncRecordMountLottery, source)
	#加次数
	role.IncDI8(EnumDayInt8.ChristmasMountLotteryFreeTimes, 1)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartMountLottery)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndMountLottery)
		Event.RegEvent(Event.Eve_IncChristmasMountotteryTime, OnIncLotteryTime)

		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChristmasMountLottery_OnOpenPanel", "圣诞坐骑转转乐_请求打开面板"), OnOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChristmasMountLottery_OnClosePanel", "圣诞坐骑转转乐_请求关闭面板"), OnClosePanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChristmasMountLottery_OnSingleLottery", "圣诞坐骑转转乐_请求单次抽奖"), OnSingleLottery)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChristmasMountLottery_OnBatchLottery", "圣诞坐骑转转乐_请求批量抽奖"), OnBatchLottery)
		