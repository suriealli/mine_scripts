#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.KaifuTarget.KaifuTargetRequest")
#===============================================================================
# 七日目标客户端请求
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig
from Game.SysData import WorldData
from Game.Activity.KaifuTarget import TargetDefine, KaifuTargetFun, KaifuRankFun
from Game.Role import Event

if "_HasLoad" not in dir():
	#七日目标目标奖励函数字典
	TargetRewardFun_Dict = {}
	#七日目标排行榜奖励函数字典
	RankRewardFun_Dict = {}
	
#=============================================================================================
#客户端请求
#=============================================================================================
def RequestTargetReward(role, msg):
	'''
	请求目标奖励
	@param role:
	@param msg:
	'''
	targetType, targetIndex = msg
	
	if role.GetLevel() < EnumGameConfig.KaifuTargetNeedLevel:
		return

	#目标相应的活动类型须注册奖励函数
	if targetType not in TargetRewardFun_Dict:
		return
	
	rewardFun = TargetRewardFun_Dict[targetType]
	rewardFun(role, targetIndex)

def RequestRankReward(role, msg):
	'''
	请求排行榜奖励
	@param role:
	@param msg:
	'''
	targetType, param = msg
	if role.GetLevel() < EnumGameConfig.KaifuTargetNeedLevel:
		return
	#排行榜相应的活动类型须注册奖励函数
	if targetType not in RankRewardFun_Dict:
		return
	rewardFun = RankRewardFun_Dict[targetType]
	rewardFun(role, param)

#=============================================================================================
#奖励函数
#=============================================================================================
def LoadTargetRewardFun():
	global TargetRewardFun_Dict
	
	#清理
	TargetRewardFun_Dict = {}
	TargetRewardFun_Dict[TargetDefine.Level] = KaifuTargetFun.RequestTargetReward_level
	TargetRewardFun_Dict[TargetDefine.Mount] = KaifuTargetFun.RequestTargetReward_mount
	TargetRewardFun_Dict[TargetDefine.Gem] = KaifuTargetFun.RequestTargetReward_gem
	TargetRewardFun_Dict[TargetDefine.WedingRing] = KaifuTargetFun.RequestTargetReward_ring
	TargetRewardFun_Dict[TargetDefine.HeroZDL] = KaifuTargetFun.RequestTargetReward_herozdl
	TargetRewardFun_Dict[TargetDefine.RoleZDL] = KaifuTargetFun.RequestTargetReward_rolezdl
	TargetRewardFun_Dict[TargetDefine.TotalZDl] = KaifuTargetFun.RequestTargetReward_zdl
		
	#赋值
	if WorldData.WD[1] > TargetDefine.KaifuTime_New:
		TargetRewardFun_Dict = {}
		TargetRewardFun_Dict[TargetDefine.NewLevel] = KaifuTargetFun.RequestTargetReward_level
		TargetRewardFun_Dict[TargetDefine.NewMount] = KaifuTargetFun.RequestTargetReward_mount
		TargetRewardFun_Dict[TargetDefine.NewGem] = KaifuTargetFun.RequestTargetReward_gem
		TargetRewardFun_Dict[TargetDefine.NewTotalZDl] = KaifuTargetFun.RequestTargetReward_zdl
		TargetRewardFun_Dict[TargetDefine.NewConsume] = KaifuTargetFun.RequestTargetReward_Consume
		TargetRewardFun_Dict[TargetDefine.NewCharge] = KaifuTargetFun.RequestTargetReward_Charge
	if WorldData.WD[1] > TargetDefine.KaifuTime_Old:
		TargetRewardFun_Dict = {}
		TargetRewardFun_Dict[TargetDefine.Level] = KaifuTargetFun.RequestTargetReward_level
		TargetRewardFun_Dict[TargetDefine.Mount] = KaifuTargetFun.RequestTargetReward_mount
		TargetRewardFun_Dict[TargetDefine.Gem] = KaifuTargetFun.RequestTargetReward_gem
		TargetRewardFun_Dict[TargetDefine.WedingRing] = KaifuTargetFun.RequestTargetReward_ring
		TargetRewardFun_Dict[TargetDefine.HeroZDL] = KaifuTargetFun.RequestTargetReward_herozdl
		TargetRewardFun_Dict[TargetDefine.RoleZDL] = KaifuTargetFun.RequestTargetReward_rolezdl
		TargetRewardFun_Dict[TargetDefine.TotalZDl] = KaifuTargetFun.RequestTargetReward_zdl

def LoadKaifuRankFun():
	global RankRewardFun_Dict
	
	#清理
	RankRewardFun_Dict = {}
	RankRewardFun_Dict[TargetDefine.Level] = KaifuRankFun.RequestRankReward_level
	RankRewardFun_Dict[TargetDefine.Mount] = KaifuRankFun.RequestRankReward_mount
	RankRewardFun_Dict[TargetDefine.Gem] = KaifuRankFun.RequestRankReward_gem
	RankRewardFun_Dict[TargetDefine.WedingRing] = KaifuRankFun.RequestRankReward_ring
	RankRewardFun_Dict[TargetDefine.HeroZDL] = KaifuRankFun.RequestRankReward_herozdl
	RankRewardFun_Dict[TargetDefine.RoleZDL] = KaifuRankFun.RequestRankReward_rolezdl
	RankRewardFun_Dict[TargetDefine.TotalZDl] = KaifuRankFun.RequestRankReward_zdl
		
	#赋值
	if WorldData.WD[1] > TargetDefine.KaifuTime_New:
		RankRewardFun_Dict = {}
		RankRewardFun_Dict[TargetDefine.NewLevel] = KaifuRankFun.RequestRankReward_level
		RankRewardFun_Dict[TargetDefine.NewTotalZDl] = KaifuRankFun.RequestRankReward_mount
	if WorldData.WD[1] > TargetDefine.KaifuTime_Old:
		RankRewardFun_Dict = {}
		RankRewardFun_Dict[TargetDefine.Level] = KaifuRankFun.RequestRankReward_level
		RankRewardFun_Dict[TargetDefine.Mount] = KaifuRankFun.RequestRankReward_mount
		RankRewardFun_Dict[TargetDefine.Gem] = KaifuRankFun.RequestRankReward_gem
		RankRewardFun_Dict[TargetDefine.WedingRing] = KaifuRankFun.RequestRankReward_ring
		RankRewardFun_Dict[TargetDefine.HeroZDL] = KaifuRankFun.RequestRankReward_herozdl
		RankRewardFun_Dict[TargetDefine.RoleZDL] = KaifuRankFun.RequestRankReward_rolezdl
		RankRewardFun_Dict[TargetDefine.TotalZDl] = KaifuRankFun.RequestRankReward_zdl
	
def AfterLoadWorldData(param1, param2):
	LoadTargetRewardFun()
	LoadKaifuRankFun()
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_AfterLoadWorldData, AfterLoadWorldData)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KaifuTarget_TReward", "请求七日目标目标奖励"), RequestTargetReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KaifuTarget_RReward", "请求七日目标排行榜奖励"), RequestRankReward)
