#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.KongJianDecennial.KongJianRechargeMgr")
#===============================================================================
# 累充送惊喜 Mgr
#===============================================================================
import cRoleMgr
import Environment
from Common.Other import GlobalPrompt, EnumGameConfig
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Activity import CircularDefine
from Game.Role.Data import EnumObj, EnumDayInt8
from Game.Activity.KongJianDecennial import KongJianRechargeConfig

if "_HasLoad" not in dir():
	IS_START = False
	
	Tra_KongJianRecharge_GetRechargeReward = AutoLog.AutoTransaction("Tra_KongJianRecharge_GetRechargeReward", "累充送惊喜充值返利_领取奖励")
	
	#格式{rewardIndex:levelRangeId,}
	KongJianRecharge_RewardRecord_S = AutoMessage.AllotMessage("KongJianRecharge_RewardRecord_S", "累充送惊喜充值返利_领奖记录同步")

#### 活动控制  start ####
def OnStartKongJianRecharge(*param):
	'''
	开启活动
	'''
	_, circularType = param
	if CircularDefine.CA_KongJianRecharge != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open KongJianRecharge"
		return
		
	IS_START = True

def OnEndKongJianRecharge(*param):
	'''
	结束活动
	'''
	_, circularType = param
	if CircularDefine.CA_KongJianRecharge != circularType:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC, end KongJianRecharge while not start"
		return
		
	IS_START = False
	
#客户端请求 start
def OnGetRechargeReward(role, msg):
	'''
	累充送惊喜_请求领取充值奖励
	'''
	if not IS_START:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.KJD_NeedLevel:
		return
	
	if not role.IsKongJianDecennialRole():
		return
	
	rewardIndex = msg
	rewardRecordDict = role.GetObj(EnumObj.KongJianDecennial)[1]
	if rewardIndex in rewardRecordDict:
		return
	
	levelRangeId = KongJianRechargeConfig.GetLevelRangeIdByLevel(roleLevel)
	rewardCfg = KongJianRechargeConfig.GetCfgByIndexAndLevel(rewardIndex, roleLevel)
	if not rewardCfg:
		return
	
	needRechargeRMB = KongJianRechargeConfig.KJDRecharge_Unlock_Dict.get(rewardIndex)
	if role.GetDayBuyUnbindRMB_Q() < needRechargeRMB:
		return
	
	prompt = GlobalPrompt.KJD_Tips_Head
	with Tra_KongJianRecharge_GetRechargeReward:
		#领奖记录
		rewardRecordDict[rewardIndex] = levelRangeId
		#奖励魔晶
		rewardBindRMB = rewardCfg.rewardBindRMB
		if rewardBindRMB > 0:
			role.IncBindRMB(rewardBindRMB)
			prompt += GlobalPrompt.BindRMB_Tips % rewardBindRMB
		#奖励金币
		rewardMoney = rewardCfg.rewardMoney
		if rewardMoney > 0:
			role.IncMoney(rewardMoney)
			prompt += GlobalPrompt.Money_Tips % rewardMoney
		#兑换币
		rewardExchangeCoin = rewardCfg.rewardExchangeCoin
		if rewardExchangeCoin > 0:
			role.IncDI8(EnumDayInt8.KongJianDecennialExchangeCoin, rewardExchangeCoin)
			prompt += GlobalPrompt.KJDExchangeCoin_Tips % rewardExchangeCoin
		#奖励道具
		for coding, cnt in rewardCfg.rewardItems:
			role.AddItem(coding, cnt)
			prompt += GlobalPrompt.Item_Tips % (coding, cnt)
	
	#获得提示
	role.Msg(2, 0, prompt)
	#同步领奖记录
	role.SendObj(KongJianRecharge_RewardRecord_S, rewardRecordDict)

#事件 start
def OnInitRole(role, param = None):
	'''
	初始化objkey
	'''
	KongJianDecennialData = role.GetObj(EnumObj.KongJianDecennial)
	if 1 not in KongJianDecennialData:
		KongJianDecennialData[1] = {}

def OnSyncRoleOtherData(role, param = None):
	'''
	角色上线 同步活动状态 
	'''
	if not IS_START:
		return
	
	if not role.IsKongJianDecennialRole():
		return
	
	#同步领奖记录
	role.SendObj(KongJianRecharge_RewardRecord_S, role.GetObj(EnumObj.KongJianDecennial)[1])
	
#def AfterRecharge(role, param = None):
#	'''
#	活动开启首天  统计充值神石数量
#	'''
#	if not IS_START:
#		return
#	
#	if not role.IsKongJianDecennialRole():
#		return
#	
#	#非充值
#	oldValue, newValue = param
#	if newValue <= oldValue:
#		return
#	
#	#统计充值神石数量
#	oldRechageRMB = role.GetI32(EnumInt32.KongJianRechargeDayBuyRMB)
#	role.SetI32(EnumInt32.KongJianRechargeDayBuyRMB, oldRechageRMB - oldValue + newValue) 

def OnRoleDayClear(role, calArgv = None, regparam = None):
	'''
	跨天清理
	'''
	
	
	#清空充值领奖记录
	KongJianDecennialData = role.GetObj(EnumObj.KongJianDecennial)
	rechargeRewardRecordDict = KongJianDecennialData[1]
	rechargeRewardRecordDict.clear()
	
#	#清空今日充值神石
#	role.SetI32(EnumInt32.KongJianRechargeDayBuyRMB, 0)
	
	#同步领奖记录
	if role.IsKongJianDecennialRole():
		role.SendObj(KongJianRecharge_RewardRecord_S, rechargeRewardRecordDict)

if "_HasLoad" not in dir():
	if Environment.HasLogic and Environment.EnvIsQQ():
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
	
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_InitRolePyObj, OnInitRole)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartKongJianRecharge)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndKongJianRecharge)
#		Event.RegEvent(Event.AfterChangeUnbindRMB_Q, AfterRecharge)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KongJianRecharge_OnGetRechargeReward", "累充送惊喜_请求领取充值奖励"), OnGetRechargeReward)
