#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.KongJianDecennial.KongJianFirstRechargeMgr")
#===============================================================================
# 首充拿大礼 Mgr
#===============================================================================
import cRoleMgr
import Environment
from Common.Other import GlobalPrompt, EnumGameConfig
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Role.Data import EnumDayInt1
from Game.Activity import CircularDefine
from Game.Activity.KongJianDecennial import KongJianFirstRechargeConfig

if "_HasLoad" not in dir():
	IS_START = False
	
	Tra_KongJianFirstRecharge_GetFirstRechargeReward = AutoLog.AutoTransaction("Tra_KongJianFirstRecharge_GetFirstRechargeReward", "首充拿大礼_领取回归礼包奖励")

#### 活动控制  start ####
def OnStartKongJianFirstRecharge(*param):
	'''
	开启活动
	'''
	_, circularType = param
	if CircularDefine.CA_KongJianFirstRecharge != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open KongJianFirstRecharge"
		return
		
	IS_START = True

def OnEndKongJianFirstRecharge(*param):
	'''
	结束活动
	'''
	_, circularType = param
	if CircularDefine.CA_KongJianFirstRecharge != circularType:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC, end KongJianFirstRecharge while not start"
		return
		
	IS_START = False

#客户端请求 start
def OnGetFirstRechargeReward(role, msg = None):
	'''
	首充拿大礼_请求领取回归奖励
	'''
	if not IS_START:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.KJD_NeedLevel:
		return
	
	if not role.IsKongJianDecennialRole():
		return
	
	if role.GetDI1(EnumDayInt1.KongJianFirstRechargeRewardFlag):
		return
	
	if role.GetDayBuyUnbindRMB_Q() < 1:
		return
	
	rewardCfg =  KongJianFirstRechargeConfig.GetRewardCfg()
	if not rewardCfg:
		print "GE_EXC, KongJianFirstRechargeMgr::OnGetFirstRechargeReward::not rewardCfg"
		return
	
	prompt = GlobalPrompt.KJD_Tips_Head
	with Tra_KongJianFirstRecharge_GetFirstRechargeReward:
		role.SetDI1(EnumDayInt1.KongJianFirstRechargeRewardFlag, 1)
		
		rewardMoney = rewardCfg.rewardMoney
		if rewardMoney > 0:
			role.IncMoney(rewardMoney)
			prompt += GlobalPrompt.Money_Tips % rewardMoney
		
		rewardBindRMB = rewardCfg.rewardBindRMB
		if rewardBindRMB > 0:
			role.IncBindRMB(rewardBindRMB)
			prompt += GlobalPrompt.BindRMB_Tips % rewardBindRMB
		
		for coding, cnt in rewardCfg.rewardItems:
			role.AddItem(coding, cnt)
			prompt += GlobalPrompt.Item_Tips % (coding, cnt)
	
	role.Msg(2, 0, prompt)

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartKongJianFirstRecharge)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndKongJianFirstRecharge)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KongJianFirstRecharge_OnGetFirstRechargeReward", "首充拿大礼_请求领取回归奖励"), OnGetFirstRechargeReward)
