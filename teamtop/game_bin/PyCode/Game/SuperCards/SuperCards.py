#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.SuperCards.SuperCards")
#===============================================================================
# 至尊周卡
#===============================================================================
import Environment
import cRoleMgr
import cDateTime
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Fight import Fight
from Game.Role import Event, Status
from Game.Role.Data import EnumInt32, EnumDayInt1, EnumObj, EnumInt1,\
	EnumDayInt8
from Game.SuperCards import SuperCardsConfig, EnumSuperCards
from Game.SysData import WorldData
from Game.Union import UnionDefine, UnionGod, UnionConfig

if "_HasLoad" not in dir():
	#至尊周卡一键收益函数字典
	SuperCardsFun_Dict = {}
	
	SuperCardsData = AutoMessage.AllotMessage("SuperCardsData", "至尊周卡数据")
	SuperCardsFail = AutoMessage.AllotMessage("SuperCardsFail", "至尊周卡失效")
	
	SuperCardsBuy_Log = AutoLog.AutoTransaction("SuperCardsBuy_Log", "至尊周卡购买日志")
	SuperCardsReward_Log = AutoLog.AutoTransaction("SuperCardsReward_Log", "至尊周卡奖励日志")
	
	
def AfterLoad():
	pass

def RegSuperCardsFun(superCardsType):
	'''
	注册至尊周卡特权函数
	'''
	def f(fun):
		global SuperCardsFun_Dict
		if superCardsType in SuperCardsFun_Dict:
			print "GE_EXC,repeat targetType in RegSuperCardsFun (%s)" % superCardsType
		SuperCardsFun_Dict[superCardsType] = fun
		return fun
	return f

def ChallengeGod(role, godId):
	'''
	挑战魔神
	@param role:
	@param godId:
	'''
	#战斗状态
	if Status.IsInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	#是否到下一天
	UnionGod.IsNextDay(role, unionObj)
	
	#今日是否可以挑战(只能一个个挑战)
	if role.GetDI8(EnumDayInt8.UnionGodProgress) + 1 != godId:
		return
	
	#魔神配置
	godConfig = UnionConfig.UNION_GOD.get(godId)
	if not godConfig:
		return
	
	#是否有buff
	hasBuff = False
	if godId in unionObj.god[UnionDefine.GOD_TODAY_PASS_LIST_IDX]:
		hasBuff = True
	
	return PVE_UnionGodEx(role, EnumGameConfig.SkipFightType, godConfig.godCampId, hasBuff, godId)

def OpenSuperCardsUnionFB(role):
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	cardsObj = role.GetObj(EnumObj.SuperCards)
	unionObj.SetSuperCardsDays(role.GetRoleID(), cardsObj[1])

def CloseSuperCardsUnionFB(role):
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	unionObj.DelSuperCardsDays(role.GetRoleID())
	
def PVE_UnionGodEx(role, fightType, campId, hasBuff, godId):
	#公会魔神pve战斗, 跳过不播放战斗
	fight = Fight.Fight(fightType)
	fight.restore = True
	left_camp, right_camp = fight.create_camp()
	left_camp.create_online_role_unit(role)
	right_camp.create_monster_camp_unit(campId)
	
	#是否有buff
	if hasBuff is True:
		for u in left_camp.pos_units.itervalues():
			u.damage_upgrade_rate += 10.0
			u.damage_reduce_rate += 0.9
	
	#跳过不播放战斗
	fight.skip_fight_play = True
	
	fight.start()
	
	#获取战斗role
	if not fight.left_camp.roles:
		return
	left_camp_roles_list = list(fight.left_camp.roles)
	role = left_camp_roles_list[0]
	
	if fight.result == 1:
		#日志
		with UnionGod.TraUnionGodWinReward:
			#魔神挑战胜利
			UnionGod.WinChallenge(role, godId, fight)
			return True
	else:
		return False

def RequestBuy(role, msg):
	'''
	请求购买
	@param role:
	@param msg:
	'''
	#等级
	if role.GetLevel() < EnumGameConfig.SuperCardsLvLimit:
		return
	
	cardsObj = role.GetObj(EnumObj.SuperCards)
	if not cardsObj:
		return
	
	nowDays = cDateTime.Days()
	
	if cardsObj.get(1):
		return
	
	#今日累计充值
	if role.GetI32(EnumInt32.DayBuyUnbindRMB_Q) < EnumGameConfig.SuperCardsBuyLimit or role.GetUnbindRMB_Q() < EnumGameConfig.SuperCardsBuyRMB:
		return
	
	with SuperCardsBuy_Log:
		role.DecUnbindRMB_Q(EnumGameConfig.SuperCardsBuyRMB)
	
	cardsObj[1] = nowDays + 7
	role.SetObj(EnumObj.SuperCards, cardsObj)
	
	#全服开启公会副本替身组队
	WorldData.SetSuperCardsUnionFB(1)
	
	role.SendObj(SuperCardsData, cardsObj)
	
	role.Msg(2, 0, GlobalPrompt.SuperCardsBuySuccess)
	cRoleMgr.Msg(1, 0, GlobalPrompt.SuperCardsBuySucess2 % role.GetRoleName())
	
def AcTiveSuperCard(role, keepdays):
	cardsObj = role.GetObj(EnumObj.SuperCards)
	if not cardsObj:
		return
	if cardsObj.get(1):#已经有至尊周卡
		cardsObj[1] += keepdays
	else:
		nowDays = cDateTime.Days()
		cardsObj[1] = nowDays + keepdays
	#全服开启公会副本替身组队
	WorldData.SetSuperCardsUnionFB(1)
	role.SendObj(SuperCardsData, cardsObj)
	
def RequestUse(role, msg):
	'''
	请求使用特权
	@param role:
	@param msg:
	'''
	if Environment.EnvIsYY():
		if role.GetLevel() < EnumGameConfig.Card_BuyLevelLimit:
			return
	else:
		if role.GetLevel() < EnumGameConfig.SuperCardsLvLimit:
			return
	
	cardsObj = role.GetObj(EnumObj.SuperCards)
	if not cardsObj:
		return
	
	if not cardsObj.get(1):
		return
	
	index = msg
	
	if index >= EnumSuperCards.MaxIndex or index < 1:
		return
	
	isUse = False
	if index in cardsObj[2]:
		cardsObj[2].discard(index)
		#关闭公会副本特权
		if index == EnumSuperCards.UnionFBSubstitute:
			CloseSuperCardsUnionFB(role)
	else:
		cardsObj[2].add(index)
		isUse = True
		#开启公会副本特权
		if index == EnumSuperCards.UnionFBSubstitute:
			OpenSuperCardsUnionFB(role)
	
	role.SetObj(EnumObj.SuperCards, cardsObj)
	
	role.SendObj(SuperCardsData, cardsObj)
	
	if isUse:
		role.Msg(2, 0, GlobalPrompt.SuperCardsUseSuccess)
	
def RequestReward(role, msg):
	'''
	请求奖励
	@param role:
	@param msg:
	'''
	if Environment.EnvIsYY():
		return
	#等级
	if role.GetLevel() < EnumGameConfig.SuperCardsLvLimit:
		return
	if role.GetDI1(EnumDayInt1.SuperCardsReward):
		return
	
	cardsObj = role.GetObj(EnumObj.SuperCards)
	if not cardsObj:
		return
	
	buyDays = cardsObj.get(1)
	if not buyDays:
		return
	
	pastDays = cDateTime.Days() - buyDays + 8
	if pastDays > 7:
		return
	elif pastDays <= 0:
		#如果是用gm指令发的周卡, 每天领取第一天奖励
		pastDays = 1
	
	cfg = SuperCardsConfig.SuperCardsReward_Dict.get(pastDays)
	if not cfg:
		print 'GE_EXC, SuperCards RequestReward can not find %s days reward' % pastDays
		return
	
	role.SetDI1(EnumDayInt1.SuperCardsReward, True)
	
	with SuperCardsReward_Log:
		tips = GlobalPrompt.Reward_Tips
		GI = GlobalPrompt.Item_Tips
		for item in cfg.rewardItems:
			role.AddItem(*item)
			tips += GI % item
		role.Msg(2, 0, tips)
	
def RequestOneKeyReward(role, msg):
	'''
	请求至尊周卡一键
	@param role:
	@param msg:
	'''
	if Environment.EnvIsYY():
		if role.GetLevel() < EnumGameConfig.Card_BuyLevelLimit:
			return
	else:
		if role.GetLevel() < EnumGameConfig.SuperCardsLvLimit:
			return
	
	cardsObj = role.GetObj(EnumObj.SuperCards)
	if not cardsObj:
		return
	
	if not cardsObj.get(1):
		return
	
	index = msg
	
	if index in cardsObj[3]:
		return
	
	global SuperCardsFun_Dict
	fun = SuperCardsFun_Dict.get(index)
	if not fun:
		return
	
	if fun(role):
		cardsObj[3].add(index)
	else:
		return
	role.SetObj(EnumObj.SuperCards, cardsObj)
	
	role.SendObj(SuperCardsData, cardsObj)
	
def SyncRoleOtherData(role, param):
	role.SendObj(SuperCardsData, role.GetObj(EnumObj.SuperCards))

def AfterLogin(role, param):
	if not role.GetObj(EnumObj.SuperCards):
		role.SetObj(EnumObj.SuperCards, {1:0, 2:set(), 3:set()})

def RoleDayClear(role, param):
	cardsObj = role.GetObj(EnumObj.SuperCards)
	if not cardsObj:
		return
	if cardsObj[1]:
		if cDateTime.Days() >= cardsObj[1]:
			cardsObj = {1:0, 2:set(), 3:set()}
			#过期删除公会记录的至尊周卡
			CloseSuperCardsUnionFB(role)
			role.SendObj(SuperCardsFail, None)
		else:
			cardsObj[3] = set()
		role.SetObj(EnumObj.SuperCards, cardsObj)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("SuperCards_Buy", "请求购买至尊周卡"), RequestBuy)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("SuperCards_Reward", "请求领取至尊周卡每日奖励"), RequestReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("SuperCards_Use", "请求使用至尊周卡特权"), RequestUse)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("SuperCards_OneKeyReward", "请求至尊周卡一键"), RequestOneKeyReward)
		
		

