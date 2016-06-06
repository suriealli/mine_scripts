#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.KongJianDecennial.KongJianLoginRewardMgr")
#===============================================================================
# 天天领好礼 Mgr
#===============================================================================
import cRoleMgr
import Environment
from Common.Other import GlobalPrompt, EnumGameConfig
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Role.Data import EnumDayInt1
from Game.Activity import CircularDefine
from Game.Activity.KongJianDecennial import KongJianLoginRewardConfig

if "_HasLoad" not in dir():
	IS_START = False
	
	Tra_KongJianLoginReward_GetLoginReward = AutoLog.AutoTransaction("Tra_KongJianLoginReward_GetLoginReward", "天天领好礼_领取回归礼包奖励")

#### 活动控制  start ####
def OnStartKongJianLoginReward(*param):
	'''
	开启活动
	'''
	_, circularType = param
	if CircularDefine.CA_KongJianLoginReward != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open KongJianLoginReward"
		return
		
	IS_START = True

def OnEndKongJianLoginReward(*param):
	'''
	结束活动
	'''
	_, circularType = param
	if CircularDefine.CA_KongJianLoginReward != circularType:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC, end KongJianLoginReward while not start"
		return
		
	IS_START = False

#客户端请求 start
def OnGetLoginRewardReward(role, msg = None):
	'''
	天天领好礼_请求领取回归奖励
	'''
	if not IS_START:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.KJD_NeedLevel:
		return
	
	if not role.IsKongJianDecennialRole():
		return
	
	if role.GetDI1(EnumDayInt1.KongJianLoginRewardFlag):
		return
	
	rewardCfg =  KongJianLoginRewardConfig.GetRewardCfg()
	if not rewardCfg:
		print "GE_EXC, KongJianLoginRewardMgr::OnGetLoginRewardReward::not rewardCfg"
		return
	
	prompt = GlobalPrompt.KJD_Tips_Head
	with Tra_KongJianLoginReward_GetLoginReward:
		role.SetDI1(EnumDayInt1.KongJianLoginRewardFlag, 1)
		
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
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartKongJianLoginReward)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndKongJianLoginReward)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KongJianLoginReward_OnGetLoginRewardReward", "天天领好礼_请求领取回归奖励"), OnGetLoginRewardReward)
