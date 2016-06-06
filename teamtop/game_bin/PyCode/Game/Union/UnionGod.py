#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Union.UnionGod")
#===============================================================================
# 公会魔神
#===============================================================================
import cDateTime
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumFightStatistics, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.DailyDo import DailyDo
from Game.Fight import Fight
from Game.Role import Status, Event
from Game.Role.Data import EnumDayInt8, EnumInt1
from Game.Union import UnionConfig, UnionDefine, UnionMgr
from Game.YYAnti import YYAnti

if "_HasLoad" not in dir():
	#消息
	Union_Show_God_Panel = AutoMessage.AllotMessage("Union_Show_God_Panel", "通知客户端显示公会魔神面板")

def IsNextDay(role, unionObj):
	'''
	是否下一天
	@param role:
	@param unionObj:
	'''
	days = cDateTime.Days()
	if days > unionObj.god[UnionDefine.GOD_DAYS_IDX]:
		unionObj.god[UnionDefine.GOD_DAYS_IDX] = days
		#清理最高通关记录topRoleId ,topGodId, roleName, sex, career, grade
		unionObj.god[UnionDefine.GOD_TOP_IDX] = (0, 0, "", 0, 0, 0)
		#清理每日通关列表
		unionObj.god[UnionDefine.GOD_TODAY_PASS_LIST_IDX] = []
		#清理通关次数
		unionObj.god[UnionDefine.GOD_FIGHT_IDX] = {}
		#保存
		unionObj.HasChange()
		
def ShowGodPanel(role):
	'''
	显示魔神面板
	@param role:
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	#是否到下一天
	IsNextDay(role, unionObj)
	
	topRoleId, topGodId, topRoleName, sex, career, grade = unionObj.god[UnionDefine.GOD_TOP_IDX]
	#最高挑战角色ID，性别，职业，进阶，最高挑战角色名，最高挑战ID，通关列表
	role.SendObj(Union_Show_God_Panel, (topRoleId, sex, career, grade, topRoleName, topGodId, unionObj.god[UnionDefine.GOD_TODAY_PASS_LIST_IDX]))
	
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
	IsNextDay(role, unionObj)
	
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
	
	#战斗
	PVE_UnionGod(role, 10, godConfig.godCampId, hasBuff, AfterFight, godId)
	
def WinChallenge(role, godId, fightObj):
	'''
	魔神挑战胜利
	@param role:
	@param godId:
	'''
	#设置魔神进度
	role.SetDI8(EnumDayInt8.UnionGodProgress, godId)
	#公会
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	#设置最高魔神相关
	if unionObj.god[UnionDefine.GOD_TOP_IDX][1] < godId:
		roleName = role.GetRoleName()
		#roleId, godId, name, sex, career, grade
		unionObj.god[UnionDefine.GOD_TOP_IDX] = (role.GetRoleID(), godId, roleName, role.GetSex(), role.GetCareer(), role.GetGrade())
		#公会广播
		unionObj.AddNews(GlobalPrompt.UNION_GOD_FIRST_KILL_NEWS % (roleName, godId))
		#公会频道
		UnionMgr.UnionMsg(unionObj, GlobalPrompt.UNION_GOD_FIRST_KILL_MSG % (roleName, godId))
		
	#记录今日通关魔神
	if godId not in unionObj.god[UnionDefine.GOD_TODAY_PASS_LIST_IDX]:
		unionObj.god[UnionDefine.GOD_TODAY_PASS_LIST_IDX].append(godId)
	
	#增加对应魔神的挑战次数
	fightTimesDict = unionObj.god.get(UnionDefine.GOD_FIGHT_IDX, {})
	fightTimesDict[godId] = fightTimesDict.get(godId, 0) + 1

	#保存
	unionObj.HasChange()
	#魔神奖励
	godConfig = UnionConfig.UNION_GOD.get(godId)
	if godConfig:
		#YY防沉迷对奖励特殊处理
		yyAntiFlag = role.GetAnti()
		if yyAntiFlag == 1:
			rewardMoney = godConfig.rewardMoney_fcm
			rewardItem = godConfig.rewardItemList_fcm
		elif yyAntiFlag == 0:
			rewardMoney = godConfig.rewardMoney
			rewardItem = godConfig.rewardItemList
		else:
			rewardMoney = 0
			rewardItem = ()
			role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
		
		role.IncMoney(rewardMoney)
		showItemList = []
		for item in rewardItem:
			role.AddItem(*item)
			showItemList.append(item)
		
		#战斗奖励统计显示
		roleId = role.GetRoleID()
		fightObj.set_fight_statistics(roleId, EnumFightStatistics.EnumMoney, rewardMoney)
		fightObj.set_fight_statistics(roleId, EnumFightStatistics.EnumItems, showItemList)
		
	#刷新面板
	ShowGodPanel(role)
	UnionMgr.ShowMainPanel(role)
	#每日必做 -- 挑战魔神
	Event.TriggerEvent(Event.Eve_DoDailyDo, role, (DailyDo.Daily_UG, 1))
	#精彩活动
	from Game.Activity.WonderfulAct import WonderfulActMgr, EnumWonderType
	WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_UnionGod, unionObj)
#===============================================================================
# 战斗相关
#===============================================================================
def PVE_UnionGod(role, fightType, mcid, hasBuff, AfterFight, afterFightParam = None, OnLeave = None, AfterPlay = None):
	'''
	公会魔神PVE
	@param role:
	@param fightType:
	@param mcid:
	@param hasBuff:
	@param AfterFight:
	@param afterFightParam:
	@param OnLeave:
	@param AfterPlay:
	'''
	# 1创建一场战斗(必须传入战斗类型，不同的战斗不要让策划复用战斗类型)
	fight = Fight.Fight(fightType)
	# 可以手动设置是否为pvp战斗，否则将是战斗配子表中战斗类型对应的pvp战斗取值
	# fight.pvp = True
	# 可收到设置客户端断线重连是否还原战斗,默认不还原
	fight.restore = True
	# 2创建两个阵营
	left_camp, right_camp = fight.create_camp()
	# 3在阵营中创建战斗单位
	left_camp.create_online_role_unit(role, role.GetRoleID(), use_px = True)
	# create_monster_camp_unit是创建一波怪物
	right_camp.create_monster_camp_unit(mcid)
	#是否有buff
	if hasBuff is True:
		for u in left_camp.pos_units.itervalues():
			u.damage_upgrade_rate += 10.0
			u.damage_reduce_rate += 0.9
	# 4设置回调函数（不是一定需要设置回调函数，按需来）
	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	# 如果需要带参数，则直接绑定在fight对象上
	fight.after_fight_param = afterFightParam
	# 5开启战斗（之后就不能再对战斗做任何设置了）
	fight.start()

def OnLeave(fight, role, reason):
	# reason 0战斗结束离场；1战斗中途掉线
	print "OnLeave", role.GetRoleID(), reason
	# fight.result如果没“bug”的话将会取值1左阵营胜利；0平局；-1右阵营胜利；None战斗未结束
	# 注意，只有在角色离开的回调函数中fight.result才有可能为None

def AfterFight(fight):
	godId = fight.after_fight_param
	
	#获取战斗role
	if not fight.left_camp.roles:
		return
	left_camp_roles_list = list(fight.left_camp.roles)
	role = left_camp_roles_list[0]
	
	# fight.round当前战斗回合
	# fight.result如果没“bug”的话将会取值1左阵营胜利；0平局；-1右阵营胜利
	# 故判断胜利请按照下面这种写法明确判定
	if fight.result == 1:
		#日志
		with TraUnionGodWinReward:
			#魔神挑战胜利
			WinChallenge(role, godId, fight)
	elif fight.result == -1:
		pass
	else:
		pass
		
def AfterPlay(fight):
	print "AfterPlay", fight.after_play_param


#===============================================================================
# 客户端请求
#===============================================================================
def RequestUnionOpenGodPanel(role, msg):
	'''
	客户端请求打开公会魔神面板
	@param role:
	@param msg:
	'''
	ShowGodPanel(role)
	
def RequestUnionChallengeGod(role, msg):
	'''
	客户端请求挑战公会魔神
	@param role:
	@param msg:
	'''
	godId = msg
	
	#挑战时间限制
	if cDateTime.Hour() == 23 and cDateTime.Minute() >= 55:
		#提示
		role.Msg(2, 0, GlobalPrompt.UNION_GOD_CANT_CHALLENGE)
		return
	
	ChallengeGod(role, godId)

if "_HasLoad" not in dir():
	#日志
	TraUnionGodWinReward = AutoLog.AutoTransaction("TraUnionGodWinReward", "公会魔神挑战胜利奖励")
	if Environment.HasLogic and not Environment.IsCross:
		#注册消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Open_God_Panel", "客户端请求打开公会魔神面板"), RequestUnionOpenGodPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Challenge_God", "客户端请求挑战公会魔神"), RequestUnionChallengeGod)
	
	
	
