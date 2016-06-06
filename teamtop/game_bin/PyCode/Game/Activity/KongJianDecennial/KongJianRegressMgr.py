#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.KongJianDecennial.KongJianRegressMgr")
#===============================================================================
# 空间回归Mgr
#===============================================================================
import cRoleMgr
import Environment
from Common.Other import GlobalPrompt
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Role.Data import EnumInt1, EnumTempInt64
from Game.Activity import CircularDefine
from Game.Activity.KongJianDecennial import KongJianRegressConfig

if "_HasLoad" not in dir():
	IS_START = False
	
	Tra_KongJianRegress_GetRegressReward = AutoLog.AutoTransaction("Tra_KongJianRegress_GetRegressReward", "空间回归_领取回归礼包奖励")

#### 活动控制  start ####
def OnStartKongJianRegress(*param):
	'''
	开启活动
	'''
	_, circularType = param
	if CircularDefine.CA_KongJianRegress != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open KongJianRegress"
		return
		
	IS_START = True

def OnEndKongJianRegress(*param):
	'''
	结束活动
	'''
	_, circularType = param
	if CircularDefine.CA_KongJianRegress != circularType:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC, end KongJianRegress while not start"
		return
		
	IS_START = False

#客户端请求 start
def OnGetRegressReward(role, msg = None):
	'''
	空间回归_请求领取回归奖励
	'''
	if not IS_START:
		return
	
	isQzone = role.GetTI64(EnumTempInt64.IsQzone)
	isPengYou = role.GetTI64(EnumTempInt64.IsPengYou)
	if not (isQzone or isPengYou):
		return
	
	if role.GetI1(EnumInt1.KongJianRegressRewardFlag):
		return
	
	rewardCfg =  KongJianRegressConfig.GetRewardCfg()
	if not rewardCfg:
		print "GE_EXC, KongJianRegressMgr::OnGetRegressReward::not rewardCfg"
		return
	
	prompt = GlobalPrompt.KJD_Tips_Head
	with Tra_KongJianRegress_GetRegressReward:
		role.SetI1(EnumInt1.KongJianRegressRewardFlag, 1)
		
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
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartKongJianRegress)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndKongJianRegress)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KongJianRegress_OnGetRegressReward", "空间回归_请求领取回归奖励"), OnGetRegressReward)
		
		
