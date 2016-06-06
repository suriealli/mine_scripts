#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Task.DayTask")
#===============================================================================
# 每日任务(日常任务,体力任务)
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Role import Event, Status
from Game.Role.Data import EnumObj, EnumDayInt8, EnumInt1
from Game.Task import TaskConfig
from Game.Fight import FightEx
from Game.ThirdParty.QQidip import QQEventDefine
from Common.Other import EnumGameConfig


DayNeedLevel = 33 #需要等级
TiLiNeedLevel = 32
FastFinishNeedRMB = 10		#任务快速完成RMB单价
FastFinishNeedRMB_NA = 50	#任务快速完成RMB单价_北美版
FastFinishNeedRMB_RU = 30	#任务快速完成RMB单价_俄罗斯版
FreeVIP = 7
if "_HasLoad" not in dir():
	DayTask_S_DayTaskData = AutoMessage.AllotMessage("DayTask_S_DayTaskData", "同步日常任务数据")
	DayTask_S_TiLiTaskData = AutoMessage.AllotMessage("DayTask_S_TiLiTaskData", "同步体力任务数据")
	
	Tra_Day_Task_Finish = AutoLog.AutoTransaction("Tra_Day_Task_Finish", "完成一个日常任务")
	Tra_Day_Task_Fast_Finish = AutoLog.AutoTransaction("Tra_Day_Task_Fast_Finish", "快速完成一个日常任务")
	Tra_Day_Task_FinishAll = AutoLog.AutoTransaction("Tra_Day_Task_FinishAll", "快速完成全部日常任务")
	
	Tra_TiLi_Task_Finish = AutoLog.AutoTransaction("Tra_TiLi_Task_Finish", "完成一个体力任务")
	Tra_TiLi_Task_Fast_Finish = AutoLog.AutoTransaction("Tra_TiLi_Task_Fast_Finish", "快速完成一个体力任务")
	Tra_TiLi_Task_FinishAll = AutoLog.AutoTransaction("Tra_TiLi_Task_FinishAll", "快速完成全部体力任务")


def RandomDayTask(role):
	#随机一个日常任务为可接取状态
	level = role.GetLevel()
	randomItem = TaskConfig.DayTaskLevelRandom_Dict.get(level)
	if not randomItem:
		print "GE_EXC, error in RandomDayTask not random roleLevel(%s)" % level
		return
	taskIndex = randomItem.RandomOne()
	role.SetObj(EnumObj.DayTask, {-1 : taskIndex, 0 : 0, 1 : 0, 2 : 0, 3 : 0, 4 : 0})

def GetRandomDayTaskIndex(role):
	level = role.GetLevel()
	randomItem = TaskConfig.DayTaskLevelRandom_Dict.get(level)
	if not randomItem:
		print "GE_EXC, error in GetRandomDayTaskIndex not random roleLevel(%s)" % level
		return
	return randomItem.RandomOne()


def RandomTiLiTask(role):
	level = role.GetLevel()
	randomItem = TaskConfig.TiLiTaskLevelRandom_Dict.get(level)
	if not randomItem:
		print "GE_EXC, error in RandomTiLiTask not random roleLevel(%s)" % level
		return
	taskIndex = randomItem.RandomOne()
	role.SetObj(EnumObj.TiLiTask, {-1 : taskIndex, 0 : 0, 1 : 0, 2 : 0, 3 : 0, 4 : 0})

def GetRandomTiLiTaskIndex(role):
	level = role.GetLevel()
	randomItem = TaskConfig.TiLiTaskLevelRandom_Dict.get(level)
	if not randomItem:
		print "GE_EXC, error in GetRandomTiLiTaskIndex not random roleLevel(%s)" % level
		return
	return randomItem.RandomOne()


def FinishAllDayTask(role):
	#是否已经完成了今天的日常任务
	if role.GetLevel() < 60:
		return role.GetDI8(EnumDayInt8.DayTaskCnt) >= 30
	else:
		return role.GetDI8(EnumDayInt8.DayTaskCnt) >= 60


def GetCanFinishDayTaskCnt(role):
	if role.GetLevel() < 60:
		return 30 - role.GetDI8(EnumDayInt8.DayTaskCnt)
	else:
		return 60 - role.GetDI8(EnumDayInt8.DayTaskCnt)
	
def FinishAllTiLiTask(role):
	#是否已经完成了今天的体力任务
	if role.GetLevel() < 60:
		return role.GetDI8(EnumDayInt8.TiLiTaskCnt) >= 30
	else:
		return role.GetDI8(EnumDayInt8.TiLiTaskCnt) >= 60

def GetCanFinishTiLiTaskCnt(role):
	if role.GetLevel() < 60:
		return 30 - role.GetDI8(EnumDayInt8.TiLiTaskCnt)
	else:
		return 60 - role.GetDI8(EnumDayInt8.TiLiTaskCnt)

def DoDayTask(role, msg):
	'''
	请求做日常任务(接任务，完成任务)
	@param role:
	@param msg:
	'''
	
	if role.GetLevel() < DayNeedLevel:
		return
	
	taskObj = role.GetObj(EnumObj.DayTask)
	if not taskObj:
		return
	unAcceptTaskIndex = taskObj[-1]
	if unAcceptTaskIndex:
		#接任务
		role.SetObj(EnumObj.DayTask, {-1 : 0, 0 : unAcceptTaskIndex, 1 : 0, 2 : 0, 3 : 0, 4 : 0})
	else:
		#完成任务
		taskIndex = taskObj[0]
		if not taskIndex:
			return
		cfg = TaskConfig.DayTaskConfig_Dict.get(taskIndex)
		if not cfg:
			return
		if not taskObj[1] or not taskObj[2] or \
			not taskObj[3] or not taskObj[4]:
			#没有完成任务
			return
		
		with Tra_Day_Task_Finish:
			#完成一个任务
			role.IncDI8(EnumDayInt8.DayTaskCnt, 1)
			if FinishAllDayTask(role):
				#完成了所有任务
				role.SetObj(EnumObj.DayTask, {})
			else:
				#重新随机一个
				RandomDayTask(role)
			#奖励玩家
			cfg.RewardRole(role)
		
			Event.TriggerEvent(Event.QQidip_Eve, role, QQEventDefine.QQ_DayTask)
			
			Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_DayTask, 1))
			
	role.SendObj(DayTask_S_DayTaskData, role.GetObj(EnumObj.DayTask))
	
	Event.TriggerEvent(Event.Eve_FB_DayTask, role)

def FaskFinishDayTask(role, msg):
	'''
	快速完成日常任务
	
	@param role:
	@param msg:
	'''
	taskObj = role.GetObj(EnumObj.DayTask)
	if not taskObj:
		return
	
	perTaskNeedRMB = FastFinishNeedRMB
	#版本判断
	if Environment.EnvIsNA():
		perTaskNeedRMB = FastFinishNeedRMB_NA
	elif Environment.EnvIsRU():
		perTaskNeedRMB = FastFinishNeedRMB_RU
	
	param = msg
	if param == 0:
		#完全全部
		if taskObj[0]:
			#有
			return
		cnt = GetCanFinishDayTaskCnt(role)
		if cnt <= 0:
			return
		taskIndex = GetRandomDayTaskIndex(role)
		cfg = TaskConfig.DayTaskConfig_Dict.get(taskIndex)
		if not cfg:
			return
		with Tra_Day_Task_FinishAll:
			if role.GetVIP() < FreeVIP:
				needRMB = cnt * perTaskNeedRMB
				if role.GetRMB() < needRMB:
					return
				role.DecRMB(needRMB)
			
			role.IncDI8(EnumDayInt8.DayTaskCnt, cnt)
			role.SetObj(EnumObj.DayTask, {})
			cfg.RewardRole(role, cnt)
		Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_DayTask, cnt))
	elif param == 1:
		#完成一个
		taskIndex = taskObj[0]
		if not taskIndex:
			return
		cfg = TaskConfig.DayTaskConfig_Dict.get(taskIndex)
		if not cfg:
			return
		
		with Tra_Day_Task_Fast_Finish:
			if role.GetVIP() < FreeVIP:
				if role.GetRMB() < perTaskNeedRMB:
					return
				
				role.DecRMB(perTaskNeedRMB)
				
			#完成一个任务
			role.IncDI8(EnumDayInt8.DayTaskCnt, 1)
			if FinishAllDayTask(role):
				#完成了所有任务
				role.SetObj(EnumObj.DayTask, {})
			else:
				#重新随机一个
				RandomDayTask(role)
			#奖励玩家
			cfg.RewardRole(role)
		Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_DayTask, 1))
	else:
		return
	Event.TriggerEvent(Event.QQidip_Eve, role, QQEventDefine.QQ_DayTask)
	Event.TriggerEvent(Event.Eve_FB_DayTask, role)
	role.SendObj(DayTask_S_DayTaskData, role.GetObj(EnumObj.DayTask))

def AttackDayTaskMonster(role, msg):
	'''
	攻击一个日常任务怪物
	@param role:
	@param msg:
	'''
	npcId = msg

	taskObj = role.GetObj(EnumObj.DayTask)
	if not taskObj:
		return
	
	cfg = TaskConfig.DayTaskConfig_Dict.get(taskObj[0])
	if not cfg:
		return
	
	npcData = cfg.m_dict.get(npcId)
	if not npcData:
		return
	
	monsterIndex, fightCampID, sceneId, posX, posY, clickLen = npcData
	#判断是否可以攻击
	if taskObj.get(monsterIndex) != 0:
		return
	
	if role.GetSceneID() != sceneId:
		return
	
	rolePosX, rolePosY = role.GetPos()
	if abs(rolePosX - posX) > clickLen * 2:
		return
	if abs(rolePosY - posY) > clickLen * 2:
		return
	#战斗状态
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		return
	#进入战斗，战斗胜利回调触发完成一个子任务
	FightEx.PVE_DayTask(role, fightCampID, 0, None, monsterIndex, None, AfterPlayDayTask)


def AfterPlayDayTask(fightObj):
	#战斗回调
	if fightObj.result != 1:
		return
	
	roles = fightObj.left_camp.roles
	if not roles:
		return
	role = list(roles)[0]
	monsterIndex = fightObj.after_fight_param
	taskObj = role.GetObj(EnumObj.DayTask)
	if not taskObj:
		return
	if taskObj.get(monsterIndex) != 0:
		return
	taskObj[monsterIndex] = 1
	
	role.SendObj(DayTask_S_DayTaskData, taskObj)



def DoTiLiTask(role, msg):
	'''
	接受一个体力任务
	@param role:
	@param msg:
	'''
	
	if role.GetLevel() < TiLiNeedLevel:
		return
	
	taskObj = role.GetObj(EnumObj.TiLiTask)
	if not taskObj:
		return
	unAcceptTaskIndex = taskObj[-1]
	if unAcceptTaskIndex:
		#接任务
		role.SetObj(EnumObj.TiLiTask, {-1 : 0, 0 : unAcceptTaskIndex, 1 : 0, 2 : 0, 3 : 0, 4 : 0})
	else:
		#完成任务
		taskIndex = taskObj[0]
		if not taskIndex:
			return
		cfg = TaskConfig.TiLiTaskConfig_Dict.get(taskIndex)
		if not cfg:
			return
		if not taskObj[1] or not taskObj[2] or \
			not taskObj[3] or not taskObj[4]:
			#没有完成任务
			return
		
		with Tra_TiLi_Task_Finish:
			#完成一个任务
			role.IncDI8(EnumDayInt8.TiLiTaskCnt, 1)
			if FinishAllTiLiTask(role):
				#完成了所有任务
				role.SetObj(EnumObj.TiLiTask, {})
			else:
				#重新随机一个
				RandomTiLiTask(role)
			#奖励玩家
			cfg.RewardRole(role)
			
			Event.TriggerEvent(Event.QQidip_Eve, role, QQEventDefine.QQ_TiLiTask)
			
	role.SendObj(DayTask_S_TiLiTaskData, role.GetObj(EnumObj.TiLiTask))
	Event.TriggerEvent(Event.Eve_FB_TiLiTask, role)


def FaskFinishTiLiTask(role, msg):
	'''
	快速完成体力任务
	
	@param role:
	@param msg:
	'''
	taskObj = role.GetObj(EnumObj.TiLiTask)
	if not taskObj:
		return
	
	perTaskNeedRMB = FastFinishNeedRMB
	#版本判断
	if Environment.EnvIsNA():
		perTaskNeedRMB = FastFinishNeedRMB_NA
	elif Environment.EnvIsRU():
		perTaskNeedRMB = FastFinishNeedRMB_RU
	
	param = msg
	if param == 0:
		#完全全部
		if taskObj[0]:
			#有
			return
		cnt = GetCanFinishTiLiTaskCnt(role)
		if cnt <= 0:
			return
		taskIndex = GetRandomTiLiTaskIndex(role)
		cfg = TaskConfig.TiLiTaskConfig_Dict.get(taskIndex)
		if not cfg:
			return
		with Tra_TiLi_Task_FinishAll:
			if role.GetVIP() < FreeVIP:
				needRMB = cnt * perTaskNeedRMB
				if role.GetRMB() < needRMB:
					return
				role.DecRMB(needRMB)
			role.IncDI8(EnumDayInt8.TiLiTaskCnt, cnt)
			role.SetObj(EnumObj.TiLiTask, {})
			cfg.RewardRole(role, cnt)
	elif param == 1:
		#完成一个
		taskIndex = taskObj[0]
		if not taskIndex:
			return
		cfg = TaskConfig.TiLiTaskConfig_Dict.get(taskIndex)
		if not cfg:
			return
		
		with Tra_TiLi_Task_Fast_Finish:
			if role.GetVIP() < FreeVIP:
				if role.GetRMB() < perTaskNeedRMB:
					return
				
				role.DecRMB(perTaskNeedRMB)
			
			#完成一个任务
			role.IncDI8(EnumDayInt8.TiLiTaskCnt, 1)
			if FinishAllTiLiTask(role):
				#完成了所有任务
				role.SetObj(EnumObj.TiLiTask, {})
			else:
				#重新随机一个
				RandomTiLiTask(role)
			#奖励玩家
			cfg.RewardRole(role)
	else:
		return
	
	Event.TriggerEvent(Event.QQidip_Eve, role, QQEventDefine.QQ_TiLiTask)
	Event.TriggerEvent(Event.Eve_FB_TiLiTask, role)
	role.SendObj(DayTask_S_TiLiTaskData, role.GetObj(EnumObj.TiLiTask))


def AttackTiLiTaskMonster(role, msg):
	'''
	攻击一个体力任务的怪物
	@param role:
	@param msg:
	'''
	npcId = msg
	
	taskObj = role.GetObj(EnumObj.TiLiTask)
	if not taskObj:
		return
	
	cfg = TaskConfig.TiLiTaskConfig_Dict.get(taskObj[0])
	if not cfg:
		return
	
	npcData = cfg.m_dict.get(npcId)
	if not npcData:
		return
	
	monsterIndex, fightCampID, sceneId, posX, posY, clickLen = npcData
	#判断是否可以攻击
	if taskObj.get(monsterIndex) != 0:
		return
	
	if role.GetSceneID() != sceneId:
		return
	
	rolePosX, rolePosY = role.GetPos()
	if abs(rolePosX - posX) > clickLen * 2:
		return
	if abs(rolePosY - posY) > clickLen * 2:
		return
	#战斗状态
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		return
	#进入战斗，战斗胜利回调触发完成一个子任务
	FightEx.PVE_DayTask(role, fightCampID, 0, None, monsterIndex, None, AfterTiLiFightPlay)


def AfterTiLiFightPlay(fightObj):
	#战斗回调
	if fightObj.result != 1:
		return
	
	roles = fightObj.left_camp.roles
	if not roles:
		return
	
	role = list(roles)[0]
	monsterIndex = fightObj.after_fight_param
	taskObj = role.GetObj(EnumObj.TiLiTask)
	if not taskObj:
		return
	if taskObj.get(monsterIndex) != 0:
		return
	taskObj[monsterIndex] = 1
	
	role.SendObj(DayTask_S_TiLiTaskData, taskObj)

def SyncRoleOtherData(role, param):
	#登录同步任务数据
	role.SendObj(DayTask_S_DayTaskData, role.GetObj(EnumObj.DayTask))
	role.SendObj(DayTask_S_TiLiTaskData, role.GetObj(EnumObj.TiLiTask))

def RoleDayClear(role, param):
	#每日清理，随机新的日常和体力任务
	roleLevel = role.GetLevel()
	if roleLevel >= DayNeedLevel:
		if not role.GetObj(EnumObj.DayTask):
			RandomDayTask(role)
			role.SendObj(DayTask_S_DayTaskData, role.GetObj(EnumObj.DayTask))
	if roleLevel >= TiLiNeedLevel:
		if not role.GetObj(EnumObj.TiLiTask):
			RandomTiLiTask(role)
			role.SendObj(DayTask_S_TiLiTaskData, role.GetObj(EnumObj.TiLiTask))
		

def AfterLevelUp(role, param):
	#升级触发激活任务
	roleLevel = role.GetLevel()
	if roleLevel == DayNeedLevel:
		if not role.GetObj(EnumObj.DayTask):
			RandomDayTask(role)
			role.SendObj(DayTask_S_DayTaskData, role.GetObj(EnumObj.DayTask))
	
	if roleLevel == TiLiNeedLevel:
		if not role.GetObj(EnumObj.TiLiTask):
			RandomTiLiTask(role)
			role.SendObj(DayTask_S_TiLiTaskData, role.GetObj(EnumObj.TiLiTask))


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
	
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_AfterLevelUp, AfterLevelUp)
		
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DayTask_DoDayTask", "请求做日常任务(接任务，完成任务)"), DoDayTask)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DayTask_AttackDayTaskMonster", "请求攻击一个日常任务怪物"), AttackDayTaskMonster)

		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DayTask_FaskFinishDayTask", "请求快速完成日常任务"), FaskFinishDayTask)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DayTask_FaskFinishTiLiTask", "请求快速完成体力任务"), FaskFinishTiLiTask)

		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DayTask_DoTiLiTask", "请求做体力任务(接任务，完成任务)"), DoTiLiTask)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DayTask_AttackTiLiTaskMonster", "请求攻击一个体力任务的怪物"), AttackTiLiTaskMonster)
		
