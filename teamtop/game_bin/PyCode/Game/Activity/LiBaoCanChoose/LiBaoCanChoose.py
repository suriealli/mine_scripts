#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.LiBaoCanChoose.LiBaoCanChoose")
#===============================================================================
# 可选择奖励的礼包
#===============================================================================
import cRoleMgr
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Activity.LiBaoCanChoose import LiBaoChooseConfig

def RequestGetReward(role, param):
	'''
	客户端请求领取礼包奖励
	@param role:
	@param param:
	'''
	backId, (coding, index) = param
	if role.ItemCnt(coding) < 1:
		return
	LiBao_CFG = LiBaoChooseConfig.LiBaoChooConfig_Dict.get(coding)
	if not LiBao_CFG:
		print "GE_EXC, can not find coding(%s) in LiBaoChooConfig_Dict" % coding
		return
	rewardId = LiBao_CFG.GetRewardId(index)
	if not rewardId:
		print "GE_EXC,the index(%s) can not find in LiBaoChooConfig_Dict,coding(%s)" % (index, coding)
		return
	RewardCfg = LiBaoChooseConfig.LiBaoForReward_Dict.get(rewardId)
	if not RewardCfg:
		print "GE_EXC,can not find rewardId(%s) in LiBaoForReward_Dict" % rewardId
		return
	with TraLiBaoRewardC:
		role.DelItem(coding, 1)
		if RewardCfg.money:
			role.IncMoney(RewardCfg.money)
			role.Msg(2, 0, GlobalPrompt.Money_Tips % RewardCfg.money)
		if RewardCfg.bindrmb:
			role.IncBindRMB(RewardCfg.bindrmb)
			role.Msg(2, 0, GlobalPrompt.BindRMB_Tips % RewardCfg.bindrmb)
		if RewardCfg.items:
			for itemCoding, itemCnt in RewardCfg.items:
				role.AddItem(itemCoding, itemCnt)
				role.Msg(2, 0, GlobalPrompt.Item_Tips % (itemCoding, itemCnt))
	role.CallBackFunction(backId, None)
	
if "_HasLoad" not in dir():

	#日志
	TraLiBaoRewardC = AutoLog.AutoTransaction("TraLiBaoRewardC", "获取可选择礼包奖励")
	
	#注册消息
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Get_LiBaoReward", "客户端请求领取礼包奖励"), RequestGetReward)
