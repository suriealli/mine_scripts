#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ExtendReward")
#===============================================================================
# 一些特殊的额外奖励功能
#===============================================================================


if "_HasLoad" not in dir():
	ExtendRewardFuns = set()


def GetExtendReward(role, param):
	'''
	
	@param role:
	@param param:(activityType, idx)(活动类型，战斗场次)
	'''
	#额外的奖励物品
	rewardDict = {}
	global ExtendRewardFuns
	for fun in ExtendRewardFuns:
		rewards = fun(role, param)
		if not rewards:
			continue
		for itemCoing, itemCnt in rewards.iteritems():
			rewardDict[itemCoing] = rewardDict.get(itemCoing, 0) + itemCnt
	return rewardDict



def InitExtendRewardFun():
	global ExtendRewardFuns
	from Game.Activity.DragonEgg import DragonEggMgr
	ExtendRewardFuns.add(DragonEggMgr.DragonEgg_ExtendReward)
	
	from Game.Activity.SeaXunbao import SeaXunbao
	ExtendRewardFuns.add(SeaXunbao.SeaXunbaoMap_ExtendReward)
	
	from Game.Activity.PetLuckyFarm import PetLuckyFarm
	ExtendRewardFuns.add(PetLuckyFarm.PetLuckyFarm_ExtendReward)

	from Game.Activity.DragonStele import DragonSteleMgr
	ExtendRewardFuns.add(DragonSteleMgr.DragonStele_ExtendReward)

	from Game.Activity.GodsTreasure import GodsTreasureMgr
	ExtendRewardFuns.add(GodsTreasureMgr.TreasureDetector_ExtendReward)
	
	from Game.Activity.LanternFestival import HappynessLantern
	ExtendRewardFuns.add(HappynessLantern.HappynessLantern_ExtendReward)
	
	from Game.Activity.ValentineDay import RosePresentMgr
	ExtendRewardFuns.add(RosePresentMgr.RosePresent_ExtendReward)
	
	from Game.Activity.DuanWuJie import DuanWuJie
	ExtendRewardFuns.add(DuanWuJie.DuanWuJie_ExtendReward)
	
	from Game.Activity.PassionAct import PassionNianShouMgr
	ExtendRewardFuns.add(PassionNianShouMgr.PassionNianShou_ExtendReward)

if "_HasLoad" not in dir():
	InitExtendRewardFun()



#def ExtendReward(role, param):
#	#注意返回值必须是字典或者None
#	return {25601 : 20}

