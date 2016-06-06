#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.Holiday.HolidayRechargeRewardMgr")
#===============================================================================
# 元旦充值奖励Mgr
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Activity import CircularDefine
from Game.Role.Data import EnumInt32, EnumInt16
from Game.Activity.Holiday import HolidayRechargeRewardConfig
	
if "_HasLoad" not in dir():
	IS_START = False
	HolidayRechargeReward_OnlineRole_Set = set()		#缓存打开面板的角色ID
	HolidayRechargeReward_PreciousRecord_List = []		#缓存大奖记录[(roleName,coding,cnt)]
	
	HolidayRechargeReward_PreciousRecord_S = AutoMessage.AllotMessage("HolidayRechargeReward_PreciousRecord_S", "元旦充值抽奖_珍贵奖励记录同步")
	
	Tra_HolidayRechargeReward_GetLotteryTimes  = AutoLog.AutoTransaction("Tra_Holiday_RechargeReward_GetLotteryTimes", "元旦充值奖励_兑换抽奖次数")
	Tra_HolidayRechargeReward_LotteryReward = AutoLog.AutoTransaction("Tra_HolidayRechargeReward_LotteryReward", "元旦充值奖励_抽奖")
	
#### 活动控制  start ####
def OnStartHolidayRecharge(*param):
	'''
	开启活动
	'''
	_, circularType = param
	if CircularDefine.CA_HolidayRechargeLottery != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open HolidayRecharge"
		return
		
	IS_START = True

def OnEndHolidayRecharge(*param):
	'''
	结束活动
	'''
	_, circularType = param
	if CircularDefine.CA_HolidayRechargeLottery != circularType:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC, end HolidayRecharge while not start"
		return
		
	IS_START = False

#### 请求start ####
def OnOpenPanel(role, msg = None):
	'''
	打开操作面板
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.HolidayRechargeReward_NeedLevel:
		return
	
	global HolidayRechargeReward_OnlineRole_Set
	HolidayRechargeReward_OnlineRole_Set.add(role.GetRoleID())
	
	role.SendObj(HolidayRechargeReward_PreciousRecord_S, HolidayRechargeReward_PreciousRecord_List)

def OnClosePanel(role, msg = None):
	'''
	关闭操作面板
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.HolidayRechargeReward_NeedLevel:
		return
	
	global HolidayRechargeReward_OnlineRole_Set
	HolidayRechargeReward_OnlineRole_Set.discard(role.GetRoleID())
	
def OnGetLotteryTimes(role, msg = None):
	'''
	元旦充值奖励_请求兑换抽奖次数
	'''
	if not IS_START:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.HolidayRechargeReward_NeedLevel:
		return
	
	#参数异常
	rewardIndex = msg
	rewardCfg = HolidayRechargeRewardConfig.Holiday_RechargeReward_Config_Dict.get(rewardIndex)
	if not rewardCfg:
		return
	
	#已领取
	rechargeRewardRecord = role.GetI32(EnumInt32.Holiday_RechargeRewardRecord)
	if rewardIndex & rechargeRewardRecord:
		return
	
	#充值不达标
	holidayRechargeRMB = role.GetDayBuyUnbindRMB_Q()
	if holidayRechargeRMB < rewardCfg.needRechargeRMB:
		return
	
	#process
	rewardLotteryTimes = rewardCfg.rewardLotteryTimes
	with Tra_HolidayRechargeReward_GetLotteryTimes:
		#update record
		role.IncI32(EnumInt32.Holiday_RechargeRewardRecord, rewardIndex)
		#获取次数
		role.IncI16(EnumInt16.HolidayLotteryTimes, rewardLotteryTimes)
	
	#prompt
	rewardPrompt = GlobalPrompt.HolidayRechargeReward_Tips_Head + GlobalPrompt.HolidayRechargeReward_Tips_LotteryTimes % rewardLotteryTimes
	role.Msg(2, 0, rewardPrompt)
	
def OnLotteryReward(role, msg = None):
	'''
	元旦充值奖励_请求抽奖
	'''
	if not IS_START:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.HolidayRechargeReward_NeedLevel:
		return
	
	#剩余次数不足
	effectLotteryTime = role.GetI16(EnumInt16.HolidayLotteryTimes)
	if effectLotteryTime < 1:
		return
	
	randomObj = HolidayRechargeRewardConfig.GetRandomObjByLevel(roleLevel)
	if not randomObj:
		print "GE_EXC, OnLotteryReward:: can not get randomObj by roleLevel(%s)" % roleLevel
		return
	
	reward = randomObj.RandomOne()
	if not reward:
		print "GE_EXC, OnLotteryReward:: config error, can not RandomOne by randomObj.randomList"
		return
	
	#process
	_, coding, cnt, isPrecious = reward
	with Tra_HolidayRechargeReward_LotteryReward:
		#扣次数
		role.DecI16(EnumInt16.HolidayLotteryTimes, 1)
		#物品获得
		role.AddItem(coding, cnt)
	
	#提示
	rewardPrompt = GlobalPrompt.HolidayLotteryReward_Tips_Head + GlobalPrompt.HolidayLotteryReward_Tips_Item % (coding, cnt)
	role.Msg(2, 0, rewardPrompt)
	
	#大奖处理
	if isPrecious:
		roleName = role.GetRoleName()
		global HolidayRechargeReward_PreciousRecord_List
		preciousInfo = (roleName, coding, cnt)
		if len(HolidayRechargeReward_PreciousRecord_List) >= EnumGameConfig.HRR_PreciousRecordMaxSize:
			HolidayRechargeReward_PreciousRecord_List.pop(0)
		HolidayRechargeReward_PreciousRecord_List.append(preciousInfo)
		
		#同步最新珍贵奖励记录给缓存的role
		invalidRoleSet = set()
		global HolidayRechargeReward_OnlineRole_Set
		for tmpRoleId in HolidayRechargeReward_OnlineRole_Set:
			tmpRole = cRoleMgr.FindRoleByRoleID(tmpRoleId)
			if not tmpRole:
				invalidRoleSet.add(tmpRoleId)
				continue
			tmpRole.SendObj(HolidayRechargeReward_PreciousRecord_S, HolidayRechargeReward_PreciousRecord_List)
		
		#删除缓存的无效roleId
		if len(invalidRoleSet) > 0:
			HolidayRechargeReward_OnlineRole_Set.difference_update(invalidRoleSet)
		
		preciousMsg = GlobalPrompt.HolidayLotteryReward_Msg_Precious % (roleName, coding, cnt)
		cRoleMgr.Msg(11, 0, preciousMsg)
			


def OnRoleDayClear(role, param = None):
	'''
	元旦充值奖励_每日重置
	'''
	#重置抽奖次数兑换记录
	role.SetI32(EnumInt32.Holiday_RechargeRewardRecord, 0)
	#重置剩余次数
	role.SetI16(EnumInt16.HolidayLotteryTimes, 0)

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
	
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartHolidayRecharge)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndHolidayRecharge)	
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("HolidayRechargeReward_OnOpenPanel", "元旦充值奖励_打开面板"), OnOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("HolidayRechargeReward_OnClosePanel", "元旦充值奖励_关闭面板"), OnClosePanel)	
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("HolidayRechargeReward_OnGetLotteryTimes", "元旦充值奖励_请求兑换抽奖次数"), OnGetLotteryTimes)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("HolidayRechargeReward_OnLotteryReward", "元旦充值奖励_请求抽奖"), OnLotteryReward)
