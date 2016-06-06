#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.SevenDayHegemony.SDHTargetFun")
#===============================================================================
# 七日争霸目标奖励领取函数
#===============================================================================
from Game.Role.Data import EnumObj
from ComplexServer.Log import AutoLog
from Common.Other import GlobalPrompt
from Game.Purgatory import Purgatory
from Game.Activity.SevenDayHegemony import SDHDefine, SDHFunGather, SDHConfig

if "_HasLoad" not in dir():
	Tra_SevenDayHegemony_T_UnionFB = AutoLog.AutoTransaction("Tra_SevenDayHegemony_T_UnionFB", "七日争霸活动公会副本目标奖励")
	Tra_SevenDayHegemony_T_Purgatory = AutoLog.AutoTransaction("Tra_SevenDayHegemony_T_Purgatory", "七日争霸活动心魔炼狱目标奖励")
	Tra_SevenDayHegemony_T_TeamTower = AutoLog.AutoTransaction("Tra_SevenDayHegemony_T_TeamTower", "七日争霸活动组队爬塔目标奖励")


@SDHFunGather.RegTargetRewardFun(SDHDefine.UnionFB)
def RequestSDHReward_UnionFB(role, index):
	'''
	客户端请求领取公会副本进度目标的奖励,目标为副本id副本关卡
	'''
	#如果角色不在公会中，则不能领取奖励
	actType = SDHDefine.UnionFB
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	targetAwardData = role.GetObj(EnumObj.SevenDayHegemony).setdefault('targetAward', {})
	awardSet = targetAwardData.setdefault(actType, set())
	#已经领取过了
	if index in awardSet:
		return
	
	#公会副本的最大进度
	maxId, maxLevel, maxOccupation = unionObj.GetMaxOccupation()
	
	config = SDHConfig.SDHTargetConfigDict.get((actType, index))
	if config is None:
		return
	
	if (maxId, maxLevel, maxOccupation) < config.param:
		return
	
	itemlist = config.item
	tarotlist = config.tarot
	bindrmb = config.bindRMB
	unbindrmb_s = config.unbindRMB_S
	
	tips = GlobalPrompt.Reward_Tips
	item_tips = GlobalPrompt.Item_Tips
	tarot_tips = GlobalPrompt.Tarot_Tips
	bind_RMB_tips = GlobalPrompt.BindRMB_Tips
	unbind_RMB_S_tips = GlobalPrompt.UnBindRMB_Tips
	
	#发放奖励,设置已经领取
	with Tra_SevenDayHegemony_T_UnionFB:
		awardSet.add(index)
		
		if itemlist:
			for coding, cnt in itemlist:
				if cnt:
					role.AddItem(coding, cnt)
					tips += item_tips % (coding, cnt)
					
		if tarotlist:
			for coding, cnt in tarotlist:
				if cnt:
					role.AddTarotCard(coding, cnt)
					tips += tarot_tips % (coding, cnt)
		if bindrmb:
			role.IncBindRMB(bindrmb)
			tips += bind_RMB_tips % bindrmb
	
		if unbindrmb_s:
			role.IncUnbindRMB_S(unbindrmb_s)
			tips += unbind_RMB_S_tips % unbindrmb_s
	
	SDHFunGather.SyncTargetAwardLog(role)
	role.Msg(2, 0, tips)


@SDHFunGather.RegTargetRewardFun(SDHDefine.Purgatory)
def RequestSDHReward_Purgatory(role, index):
	'''
	客户端请求领取心魔炼狱的目标奖励
	'''
	actType = SDHDefine.Purgatory
	targetAwardData = role.GetObj(EnumObj.SevenDayHegemony).setdefault('targetAward', {})
	awardSet = targetAwardData.setdefault(actType, set())
	#已经领取过了
	if index in awardSet:
		return
	roleId = role.GetRoleID()
	if roleId not in Purgatory.PurgatoryBestDict:
		return
	historyIndex, historyRound = Purgatory.PurgatoryBestDict[roleId]
	config = SDHConfig.SDHTargetConfigDict.get((actType, index))
	if config is None:
		return
	
	needIndex, needRound = config.param
	if historyIndex < needIndex:
		return
	elif historyIndex == needIndex:
		if historyRound > needRound:
			return
	
	itemlist = config.item
	tarotlist = config.tarot
	bindrmb = config.bindRMB
	unbindrmb_s = config.unbindRMB_S
	
	tips = GlobalPrompt.Reward_Tips
	item_tips = GlobalPrompt.Item_Tips
	tarot_tips = GlobalPrompt.Tarot_Tips
	bind_RMB_tips = GlobalPrompt.BindRMB_Tips
	unbind_RMB_S_tips = GlobalPrompt.UnBindRMB_Tips
	
	#发放奖励,设置已经领取
	with Tra_SevenDayHegemony_T_Purgatory:
		awardSet.add(index)
		
		if itemlist:
			for coding, cnt in itemlist:
				if cnt:
					role.AddItem(coding, cnt)
					tips += item_tips % (coding, cnt)
					
		if tarotlist:
			for coding, cnt in tarotlist:
				if cnt:
					role.AddTarotCard(coding, cnt)
					tips += tarot_tips % (coding, cnt)
		if bindrmb:
			role.IncBindRMB(bindrmb)
			tips += bind_RMB_tips % bindrmb
	
		if unbindrmb_s:
			role.IncUnbindRMB_S(unbindrmb_s)
			tips += unbind_RMB_S_tips % unbindrmb_s
	
	SDHFunGather.SyncTargetAwardLog(role)
	role.Msg(2, 0, tips)


@SDHFunGather.RegTargetRewardFun(SDHDefine.TeamTower)
def RequestSDHReward_TeamTower(role, index):
	'''
	客户端请求获取组队爬塔的目标奖励
	'''
	actType = SDHDefine.TeamTower
	targetAwardData = role.GetObj(EnumObj.SevenDayHegemony).setdefault('targetAward', {})
	awardSet = targetAwardData.setdefault(actType, set())
	#已经领取过了
	if index in awardSet:
		return
	
	TeamTowerData = role.GetObj(EnumObj.TeamTowerData)
	if 2 not in TeamTowerData:
		return
	historyIndex, historyRound = TeamTowerData[2]
	
	config = SDHConfig.SDHTargetConfigDict.get((actType, index))
	if config is None:
		return
	
	needIndex, needRound = config.param
	if historyIndex < needIndex:
		return
	elif historyIndex == needIndex:
		if historyRound > needRound:
			return
		
	itemlist = config.item
	tarotlist = config.tarot
	bindrmb = config.bindRMB
	unbindrmb_s = config.unbindRMB_S
	
	tips = GlobalPrompt.Reward_Tips
	item_tips = GlobalPrompt.Item_Tips
	tarot_tips = GlobalPrompt.Tarot_Tips
	bind_RMB_tips = GlobalPrompt.BindRMB_Tips
	unbind_RMB_S_tips = GlobalPrompt.UnBindRMB_Tips
	
	#发放奖励,设置已经领取
	with Tra_SevenDayHegemony_T_TeamTower:
		awardSet.add(index)
		
		if itemlist:
			for coding, cnt in itemlist:
				if cnt:
					role.AddItem(coding, cnt)
					tips += item_tips % (coding, cnt)
					
		if tarotlist:
			for coding, cnt in tarotlist:
				if cnt:
					role.AddTarotCard(coding, cnt)
					tips += tarot_tips % (coding, cnt)
		if bindrmb:
			role.IncBindRMB(bindrmb)
			tips += bind_RMB_tips % bindrmb
	
		if unbindrmb_s:
			role.IncUnbindRMB_S(unbindrmb_s)
			tips += unbind_RMB_S_tips % unbindrmb_s

	SDHFunGather.SyncTargetAwardLog(role)
	role.Msg(2, 0, tips)

