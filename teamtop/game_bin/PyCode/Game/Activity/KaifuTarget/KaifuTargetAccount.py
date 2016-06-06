#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.KaifuTarget.KaifuTargetAccount")
#===============================================================================
# 七日目标排行榜结算函数
#===============================================================================
import Environment
from Game.Role import RoleMgr, Event
from Game.Activity.KaifuTarget import TargetDefine
from Game.SystemRank import SystemRank
from Game.SysData import WorldData

if "_HasLoad" not in dir():
	AccountFunDict = {}
	
def AccountLevelRank():
	if not SystemRank.LR.returnDB:
		print 'GE_EXC, SystemRank.LR not returnDB'
		return
	
	#更新等级榜
	for role in RoleMgr.RoleID_Role.itervalues():
		SystemRank.UpdateLevelRank(role)
	
	rank_data = SystemRank.LR.ReturnData().items()
	#等级 --> 经验 --> ID
	rank_data.sort(key = lambda x:(x[1][1], x[1][4], -x[0]), reverse = True)
	#前二十名
	rank_data = rank_data[:20]
	
	#空的排行榜 ?
	if not rank_data:
		return {}, None
	
	#第一名名字
	firstName = rank_data[0][1][0]
	#{roleId:[rank, 是否领取奖励, 排行榜数据]}
	rankDict = {}
	for index, (roleId, rankData) in enumerate(rank_data):
		if roleId in rankDict:
			print 'GE_EXC, AccountLevelRank error id %s' % roleId
			continue
		rankDict[roleId] = {1:[index + 1, 0, rankData]}
	return rankDict, firstName

def AccountLevelRankEx():
	if not SystemRank.LR.returnDB:
		print 'GE_EXC, SystemRank.LR not returnDB'
		return
	
	#更新等级榜
	for role in RoleMgr.RoleID_Role.itervalues():
		SystemRank.UpdateLevelRank(role)
	
	rank_data = SystemRank.LR.ReturnData().items()
	#剔除掉等级不够的
	rank_data = [(k,v) for (k,v) in rank_data if v[1] >= 30]
	#等级 --> 经验 --> ID
	rank_data.sort(key = lambda x:(x[1][1], x[1][4], -x[0]), reverse = True)
	#前二十名
	rank_data = rank_data[:10]
	
	#空的排行榜 ?
	if not rank_data:
		return {}, None
	
	#第一名名字
	firstName = rank_data[0][1][0]
	#{roleId:[rank, 是否领取奖励, 排行榜数据]}
	rankDict = {}
	for index, (roleId, rankData) in enumerate(rank_data):
		if roleId in rankDict:
			print 'GE_EXC, AccountLevelRank error id %s' % roleId
			continue
		rankDict[roleId] = {1:[index + 1, 0, rankData]}
	return rankDict, firstName

def AccountGemRank():
	if not SystemRank.EG.returnDB:
		print 'GE_EXC, SystemRank.EG not returnDB'
		return
	
	#更新宝石榜
	for role in RoleMgr.RoleID_Role.itervalues():
		SystemRank.UpdateEquipmentGem(role)
	
	rank_data = SystemRank.EG.ReturnData().items()
	#宝石等级 --> 角色等级 --> 角色经验 --> 角色ID
	rank_data.sort(key = lambda x:(x[1][1], x[1][2], x[1][3], -x[0]), reverse = True)
	#前二十名
	rank_data = rank_data[:20]
	
	#空的排行榜 ?
	if not rank_data:
		return {}, None
	
	#第一名名字
	firstName = rank_data[0][1][0]
	#{roleId:[rank, 是否领取奖励, 排行榜数据]}
	rankDict = {}
	for index, (roleId, rankData) in enumerate(rank_data):
		if roleId in rankDict:
			print 'GE_EXC, AccountLevelRank error id %s' % roleId
			continue
		rankDict[roleId] = {1:[index + 1, 0, rankData]}
	return rankDict, firstName

def AccountMountRank():
	if not SystemRank.MR.returnDB:
		print 'GE_EXC, SystemRank.MR not returnDB'
		return
	
	#更新坐骑榜
	for role in RoleMgr.RoleID_Role.itervalues():
		SystemRank.UpdateMountRank(role)
	
	rank_data = SystemRank.MR.ReturnData().items()
	#坐骑等级 --> 坐骑经验 --> 角色ID
	rank_data.sort(key = lambda x:(x[1][1], x[1][2], -x[0]), reverse = True)
	#前二十名
	rank_data = rank_data[:20]
	
	#空的排行榜 ?
	if not rank_data:
		return {}, None
	
	#第一名名字
	firstName = rank_data[0][1][0]
	#{roleId:[rank, 是否领取奖励, 排行榜数据]}
	rankDict = {}
	for index, (roleId, rankData) in enumerate(rank_data):
		if roleId in rankDict:
			print 'GE_EXC, AccountLevelRank error id %s' % roleId
			continue
		rankDict[roleId] = {1:[index + 1, 0, rankData]}
	return rankDict, firstName

def AccountWedingRingRank():
	if not SystemRank.WR.returnDB:
		print 'GE_EXC, SystemRank.WR not returnDB'
		return
	
	#更新婚戒榜
	for role in RoleMgr.RoleID_Role.itervalues():
		SystemRank.UpdateWeddingRing(role)
	
	rank_data = SystemRank.WR.ReturnData().items()
	#婚戒等级 --> 婚戒经验 --> 角色ID
	rank_data.sort(key = lambda x:(x[1][1], x[1][2], -x[0]), reverse = True)
	#前二十名
	rank_data = rank_data[:20]
	
	#空的排行榜 ?
	if not rank_data:
		return {}, None
	
	#第一名名字
	firstName = rank_data[0][1][0]
	#{roleId:[rank, 是否领取奖励, 排行榜数据]}
	rankDict = {}
	for index, (roleId, rankData) in enumerate(rank_data):
		if roleId in rankDict:
			print 'GE_EXC, AccountLevelRank error id %s' % roleId
			continue
		rankDict[roleId] = {1:[index + 1, 0, rankData]}
	return rankDict, firstName

def AccountRoleZDLRank():
	if not SystemRank.RZ.returnDB:
		print 'GE_EXC, SystemRank.RZ not returnDB'
		return
	
	#更新主角战斗力榜
	for role in RoleMgr.RoleID_Role.itervalues():
		SystemRank.UpdateRoleZDL(role)
	
	rank_data = SystemRank.RZ.ReturnData().items()
	#主角战斗力 --> 角色等级 --> 角色经验 --> 角色ID
	rank_data.sort(key = lambda x:(x[1][1], x[1][2], x[1][3], -x[0]), reverse = True)
	#前二十名
	rank_data = rank_data[:20]
	
	#空的排行榜 ?
	if not rank_data:
		return {}, None
	
	#第一名名字
	firstName = rank_data[0][1][0]
	#{roleId:[rank, 是否领取奖励, 排行榜数据]}
	rankDict = {}
	for index, (roleId, rankData) in enumerate(rank_data):
		if roleId in rankDict:
			print 'GE_EXC, AccountLevelRank error id %s' % roleId
			continue
		rankDict[roleId] = {1:[index + 1, 0, rankData]}
	return rankDict, firstName

def AccountHeroZDLRank():
	if not SystemRank.HEROZDL_BT.returnDB:
		print 'GE_EXC, SystemRank.HEROZDL_BT not returnDB'
		return
	
	#英雄战斗力榜
	SystemRank.SortedHeroZDL()
	
	#前二十名
	rank_data = SystemRank.HERO_ZDL_LIST[:20]
	
	#空的排行榜 ?
	if not rank_data:
		return {}, None
	
	#第一名名字
	firstName = rank_data[0][1][5]
	#{roleId:[rank, 是否领取奖励, 排行榜数据]}
	rankDict = {}
	for index, (heroId, rankData) in enumerate(rank_data):
		roleId = rankData[4]
		if roleId not in rankDict:
			rankDict[roleId] = {heroId:[index + 1, 0, rankData]}
		else:
			if heroId in rankDict[roleId]:
				print 'GE_EXC, AccountHeroZDLRank error role id %s, hero id %s' % (roleId, heroId)
				continue 
			rankDict[roleId][heroId] = [index + 1, 0, rankData]
		
	return rankDict, firstName

def AccountTotalZDLRank():
	if not SystemRank.ZR.returnDB:
		print 'GE_EXC, SystemRank.ZR not returnDB'
		return
	
	#更新总战斗力榜
	for role in RoleMgr.RoleID_Role.itervalues():
		SystemRank.UpdateZDLRank(role)
	
	rank_data = SystemRank.ZR.ReturnData().items()
	#等级 --> 经验 --> ID
	rank_data.sort(key = lambda x:(x[1][2], x[1][1], x[0]), reverse = True)
	#前二十名
	rank_data = rank_data[:20]
	
	#空的排行榜 ?
	if not rank_data:
		return {}, None
	
	#第一名名字
	firstName = rank_data[0][1][0]
	#{roleId:[rank, 是否领取奖励, 排行榜数据]}
	rankDict = {}
	for index, (roleId, rankData) in enumerate(rank_data):
		if roleId in rankDict:
			print 'GE_EXC, AccountLevelRank error id %s' % roleId
			continue
		rankDict[roleId] = {1:[index + 1, 0, rankData]}
	return rankDict, firstName

def AccountTotalZDLRankEx():
	if not SystemRank.ZR.returnDB:
		print 'GE_EXC, SystemRank.ZR not returnDB'
		return
	
	#更新总战斗力榜
	for role in RoleMgr.RoleID_Role.itervalues():
		SystemRank.UpdateZDLRank(role)
	
	rank_data = SystemRank.ZR.ReturnData().items()
	#剔除掉等级不够的
	rank_data = [(k,v) for (k,v) in rank_data if v[2] >= 50000]
	
	#等级 --> 经验 --> ID
	rank_data.sort(key = lambda x:(x[1][2], x[1][1], x[0]), reverse = True)
	#前二十名
	rank_data = rank_data[:10]
	
	#空的排行榜 ?
	if not rank_data:
		return {}, None
	
	#第一名名字
	firstName = rank_data[0][1][0]
	#{roleId:[rank, 是否领取奖励, 排行榜数据]}
	rankDict = {}
	for index, (roleId, rankData) in enumerate(rank_data):
		if roleId in rankDict:
			print 'GE_EXC, AccountLevelRank error id %s' % roleId
			continue
		rankDict[roleId] = {1:[index + 1, 0, rankData]}
	return rankDict, firstName

def LinkAccountFun(param1, param2):
	global AccountFunDict
	
	#先清空
	AccountFunDict = {}
	AccountFunDict[TargetDefine.Level] = AccountLevelRank
	AccountFunDict[TargetDefine.Gem] = AccountGemRank
	AccountFunDict[TargetDefine.Mount] = AccountMountRank
	AccountFunDict[TargetDefine.WedingRing] = AccountWedingRingRank
	AccountFunDict[TargetDefine.RoleZDL] = AccountRoleZDLRank
	AccountFunDict[TargetDefine.HeroZDL] = AccountHeroZDLRank
	AccountFunDict[TargetDefine.TotalZDl] = AccountTotalZDLRank
		
	#再赋值
	if WorldData.WD[1] > TargetDefine.KaifuTime_New:
		AccountFunDict = {}
		AccountFunDict[TargetDefine.NewLevel] = AccountLevelRankEx
		AccountFunDict[TargetDefine.NewTotalZDl] = AccountTotalZDLRankEx
	if WorldData.WD[1] > TargetDefine.KaifuTime_Old:
		AccountFunDict = {}
		AccountFunDict[TargetDefine.Level] = AccountLevelRank
		AccountFunDict[TargetDefine.Gem] = AccountGemRank
		AccountFunDict[TargetDefine.Mount] = AccountMountRank
		AccountFunDict[TargetDefine.WedingRing] = AccountWedingRingRank
		AccountFunDict[TargetDefine.RoleZDL] = AccountRoleZDLRank
		AccountFunDict[TargetDefine.HeroZDL] = AccountHeroZDLRank
		AccountFunDict[TargetDefine.TotalZDl] = AccountTotalZDLRank
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		#世界数据载回好后处理排行榜函数
		Event.RegEvent(Event.Eve_AfterLoadWorldData, LinkAccountFun)
		