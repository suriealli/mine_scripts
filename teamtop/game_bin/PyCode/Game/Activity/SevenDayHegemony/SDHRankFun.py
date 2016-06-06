#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.SevenDayHegemony.SDHRankFun")
#===============================================================================
# 七日争霸排行奖励领取函数
#===============================================================================
from ComplexServer.Log import AutoLog
from Common.Other import GlobalPrompt
from Game.Activity.SevenDayHegemony import SDHDefine, SDHFunGather, SDHConfig


if "_HasLoad" not in dir():
	Tra_SevenDayHegemony_UnionFB = AutoLog.AutoTransaction("Tra_SevenDayHegemony_UnionFB", "七日争霸活动公会副本排行榜奖励")
	Tra_SevenDayHegemony_Purgatory = AutoLog.AutoTransaction("Tra_SevenDayHegemony_Purgatory", "七日争霸活动心魔炼狱排行榜奖励")
	Tra_SevenDayHegemony_TeamTower = AutoLog.AutoTransaction("Tra_SevenDayHegemony_TeamTower", "七日争霸活动组队爬塔排行榜奖励")


@SDHFunGather.RegRankRewardFun(SDHDefine.UnionFB)
def RequestSDHReward_UnionFB(role):
	'''
	客户端请求领取公会副本排行榜奖励
	'''
	#如果角色不在公会中，则不能领取奖励
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	SevenDayHegemonyDict = SDHFunGather.SevenDayHegemonyDict
	roleId = role.GetRoleID()
	actType = SDHDefine.UnionFB
	awardSet = SevenDayHegemonyDict.setdefault('rankAwardLog', {}).setdefault(roleId, set())
	
	#已经领取过了公会副本的排行奖励
	if actType in awardSet:
		return
	
	#获取已经结算过的活动set,如果活动还没有结算过的话不能领奖
	accountSet = SevenDayHegemonyDict.setdefault('accountSet', set())
	if actType not in accountSet:
		return
	rankData = SDHFunGather.SevenDayHegemonyDict.setdefault('rankData', {})
	rankDict = rankData.get(actType, {})
	
	unionID = unionObj.union_id
	if unionID not in rankDict:
		return
	
	rank = rankDict[unionID][0]
	
	config = SDHConfig.SDHRankConfigDict.get((actType, rank))
	if config is None:
		return
	
	
	itemlist = config.item
	tarotlist = config.tarot
	bindrmb = config.bindRMB
	money = config.money
	contribution = config.contribution
	
	tips = GlobalPrompt.Reward_Tips
	item_tips = GlobalPrompt.Item_Tips
	tarot_tips = GlobalPrompt.Tarot_Tips
	bind_RMB_tips = GlobalPrompt.BindRMB_Tips
	money_tips = GlobalPrompt.Money_Tips
	contribution_tips = GlobalPrompt.UnionContribution_Tips
	
	#这里添加日志
	#发放奖励,设置已经领取
	with Tra_SevenDayHegemony_UnionFB:
		awardSet.add(actType)
		SevenDayHegemonyDict.HasChange()
		
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
			
		if money:
			role.IncMoney(money)
			tips += contribution_tips % money
			
		if contribution:
			role.IncContribution(contribution)
			tips += money_tips % contribution_tips
		
	SDHFunGather.SyncRankAwardLog(role)
	role.Msg(2, 0, tips)



@SDHFunGather.RegRankRewardFun(SDHDefine.Purgatory)
def RequestSDHReward_Purgatory(role):
	'''
	客户端请求领取心魔炼狱的排行奖励
	'''
	SevenDayHegemonyDict = SDHFunGather.SevenDayHegemonyDict
	roleId = role.GetRoleID()
	actType = SDHDefine.Purgatory
	awardSet = SevenDayHegemonyDict.setdefault('rankAwardLog', {}).setdefault(roleId, set())
	
	#已经领取过了公会副本的排行奖励
	if actType in awardSet:
		return
	
	#获取已经结算过的活动set,如果活动还没有结算过的话不能领奖
	accountSet = SevenDayHegemonyDict.setdefault('accountSet', set())
	if actType not in accountSet:
		return
	rankData = SDHFunGather.SevenDayHegemonyDict.setdefault('rankData', {})
	rankDict = rankData.get(actType, {})
	
	if roleId not in rankDict:
		return
	
	rank = rankDict[roleId][0]
	
	config = SDHConfig.SDHRankConfigDict.get((actType, rank))
	if config is None:
		return
	
	itemlist = config.item
	tarotlist = config.tarot
	bindrmb = config.bindRMB
	money = config.money
	contribution = config.contribution
	
	tips = GlobalPrompt.Reward_Tips
	item_tips = GlobalPrompt.Item_Tips
	tarot_tips = GlobalPrompt.Tarot_Tips
	bind_RMB_tips = GlobalPrompt.BindRMB_Tips
	money_tips = GlobalPrompt.Money_Tips
	contribution_tips = GlobalPrompt.UnionContribution_Tips
	#这里添加日志
	#发放奖励,设置已经领取
	with Tra_SevenDayHegemony_Purgatory:
		awardSet.add(actType)
		SevenDayHegemonyDict.HasChange()
		
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
			
		if money:
			role.IncMoney(money)
			tips += money_tips % money
		
		if contribution:
			role.IncContribution(contribution)
			tips += money_tips % contribution_tips
			
	SDHFunGather.SyncRankAwardLog(role)
	role.Msg(2, 0, tips)


@SDHFunGather.RegRankRewardFun(SDHDefine.TeamTower)
def RequestSDHReward_TeamTower(role):
	'''
	客户端请求获取组队爬塔的排行奖励
	'''
	SevenDayHegemonyDict = SDHFunGather.SevenDayHegemonyDict
	roleId = role.GetRoleID()
	actType = SDHDefine.TeamTower
	awardSet = SevenDayHegemonyDict.setdefault('rankAwardLog', {}).setdefault(roleId, set())
	
	#已经领取过了公会副本的排行奖励
	if actType in awardSet:
		return
	
	#获取已经结算过的活动set,如果活动还没有结算过的话不能领奖
	accountSet = SevenDayHegemonyDict.setdefault('accountSet', set())
	if actType not in accountSet:
		return
	rankData = SDHFunGather.SevenDayHegemonyDict.setdefault('rankData', {})
	rankDict = rankData.get(actType, {})
	
	if roleId not in rankDict:
		return
	
	rank = rankDict[roleId][0]
	
	config = SDHConfig.SDHRankConfigDict.get((actType, rank))
	if config is None:
		return
	
	itemlist = config.item
	tarotlist = config.tarot
	bindrmb = config.bindRMB
	money = config.money
	contribution = config.contribution
	
	tips = GlobalPrompt.Reward_Tips
	item_tips = GlobalPrompt.Item_Tips
	tarot_tips = GlobalPrompt.Tarot_Tips
	bind_RMB_tips = GlobalPrompt.BindRMB_Tips
	money_tips = GlobalPrompt.Money_Tips
	contribution_tips = GlobalPrompt.UnionContribution_Tips
	
	#发放奖励,设置已经领取
	with Tra_SevenDayHegemony_TeamTower:
		awardSet.add(actType)
		SevenDayHegemonyDict.HasChange()
		
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
			
		if money:
			role.IncMoney(money)
			tips += money_tips % money
			
		if contribution:
			role.IncContribution(contribution)
			tips += money_tips % contribution_tips
	
	SDHFunGather.SyncRankAwardLog(role)
	role.Msg(2, 0, tips)

