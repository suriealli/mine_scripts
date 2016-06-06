#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.DragonKnightChallenge.DragonKnightChallengeMgr")
#===============================================================================
# 龙骑试炼Mgr
#===============================================================================
import Environment
import cRoleMgr
from Common.Message import AutoMessage
from Game.Fight import Fight
from Game.Persistence import Contain
from Common.Other import EnumGameConfig, GlobalPrompt, EnumFightStatistics
from Game.DragonKnightChallenge import DragonKnightChallengeConfig
from Game.Role.Data import EnumInt16, EnumInt1
from Game.Role import Status
from ComplexServer.Log import AutoLog
from Game.Activity.Title import Title

if "_HasLoad" not in dir():
	#消息
	DKC_ChallengeRecord_S = AutoMessage.AllotMessage("DKC_ChallengeRecord_S", "龙骑试炼_同步最新试练记录")
	#日志
	Tra_DKC_ChallengeReward = AutoLog.AutoTransaction("Tra_DKC_ChallengeReward", "龙骑试炼_试炼奖励")

#### 客户端请求 start
def OnOpenPanel(role, msg = None):
	'''
	龙骑试炼_打开试炼面板
	'''
	if role.GetLevel() < EnumGameConfig.DKC_NeedLevel:
		return
	
	role.SendObj(DKC_ChallengeRecord_S, DKC_ChallengeRecord_Dict.data)

def OnChallenge(role, msg):
	'''
	龙骑试炼_试炼挑战
	@param msg: 试炼关卡
	'''
	if role.GetLevel() < EnumGameConfig.DKC_NeedLevel:
		return
	
	challengeLevel = msg
	challengeCfg = DragonKnightChallengeConfig.DKC_BASECONFIG_DICT.get(challengeLevel)
	if not challengeCfg:
		return
	
	#关卡不对
	passedLevel = role.GetI16(EnumInt16.DKCPassedLevel)
	if passedLevel + 1 != challengeLevel:
		return
	
	#战力不够
	if role.GetZDL() < challengeCfg.needZDL:
		return
	
	#是否能进入龙骑试炼战斗
	if not Status.CanInStatus(role, EnumInt1.ST_DKCFight):
		return
	
	#是否能进入战斗
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	#强制进入龙骑试练状态
	Status.ForceInStatus(role, EnumInt1.ST_DKCFight)
	
	#战斗
	PVE_DKCFight(role, challengeCfg.fightType, challengeCfg.campId, challengeCfg)

#### 战斗start
def PVE_DKCFight(role, fightType, mcid, regParam):
	'''
	勇者试炼场PVE战斗
	'''
	fight = Fight.Fight(fightType)
	# 可收到设置客户端断线重连是否还原战斗,默认不还原
	fight.restore = True
	#创建两个阵营
	left_camp, right_camp = fight.create_camp()
	#在阵营中创建战斗单位
	left_camp.create_online_role_unit(role, role.GetRoleID())
	right_camp.create_monster_camp_unit(mcid)
	#设置回调函数
	fight.after_fight_fun = AfterFight		#战斗结束
	fight.after_play_fun = AfterPlay		#客户端播放完毕
	fight.after_fight_param = regParam		#注册参数
	fight.start()

def AfterFight(fightObj):
	'''
	战斗结束  
	'''
	#获取战斗role
	if not fightObj.left_camp.roles:
		return
	left_camp_roles_list = list(fightObj.left_camp.roles)
	role = left_camp_roles_list[0]
	
	#退出龙骑试练状态
	Status.Outstatus(role, EnumInt1.ST_DKCFight)
	challengeCfg = fightObj.after_fight_param
	if fightObj.result == 1:
		with Tra_DKC_ChallengeReward:
			#奖励道具
			rewardItemList = []
			for coding, cnt in challengeCfg.rewardItem:
				rewardItemList.append((coding, cnt))
			fightObj.set_fight_statistics(role.GetRoleID(), EnumFightStatistics.EnumItems, rewardItemList)
	elif fightObj.result == -1:
		pass
	else:
		pass
		
def AfterPlay(fightObj):
	'''
	播放战斗结束  
	'''
	#获取战斗role
	if not fightObj.left_camp.roles:
		return
	left_camp_roles_list = list(fightObj.left_camp.roles)
	role = left_camp_roles_list[0]
	if not role or role.IsKick():
		return
		
	prompt = GlobalPrompt.DKC_Tips_Head
	challengeCfg = fightObj.after_fight_param
	if fightObj.result == 1:
		with Tra_DKC_ChallengeReward:
			#设置通关关卡
			role.SetI16(EnumInt16.DKCPassedLevel, challengeCfg.DKCLevel)
			#奖励道具
			for coding, cnt in challengeCfg.rewardItem:
				role.AddItem(coding, cnt)
				prompt += GlobalPrompt.DKC_Tips_Item % (coding, cnt)
			#称号奖励
			if challengeCfg.rewardTitle:
				Title.AddTitle(role.GetRoleID(), challengeCfg.rewardTitle)
		
		#处理本服本关卡试练记录
		global DKC_ChallengeRecord_Dict
		latestRecordList = DKC_ChallengeRecord_Dict.setdefault(challengeCfg.DKCLevel, [])
		latestRecordList.append((role.GetRoleName(), role.GetZDL()))
		relativeSize = len(latestRecordList) - EnumGameConfig.DKC_PassRecordNum
		if relativeSize > 0:
			#记录数量超过 截断
			latestRecordList = latestRecordList[relativeSize:]
		DKC_ChallengeRecord_Dict[challengeCfg.DKCLevel] = latestRecordList
		
		#同步最新挑战记录
		role.SendObj(DKC_ChallengeRecord_S, DKC_ChallengeRecord_Dict.data)
		
		#提示
		role.Msg(2, 0, prompt)
		#广播
		cRoleMgr.Msg(3, 0, GlobalPrompt.DKC_Msg_Pass % (role.GetRoleName(), challengeCfg.levelName, challengeCfg.titleName))
	elif fightObj.result == -1:
		pass
	else:
		pass

def AfterLoadDKC():
	pass

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DKC_OnOpenPanel", "龙骑试炼_打开试炼面板"), OnOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DKC_OnChallenge", "龙骑试炼_试炼挑战"), OnChallenge)
		#持久化数据  {DKCLevel:[(name,ZDL),],}
		DKC_ChallengeRecord_Dict = Contain.Dict("DKC_ChallengeRecord_Dict", (2038, 1, 1), AfterLoadDKC)