#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Task.SubTask")
#===============================================================================
# 支线任务
#===============================================================================
import cRoleMgr
import cRoleDataMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumAppearance, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Task import TaskConfig, EnumTaskType
from Game.Role.Data import EnumObj, EnumDisperseInt32, EnumTempObj, EnumDayInt8, EnumInt32,\
	EnumInt1

if "_HasLoad" not in dir():
	SubTask_Data = AutoMessage.AllotMessage("SubTask_Data", "同步支线任务数据")
	SubTask_FinishOne = AutoMessage.AllotMessage("SubTask_FinishOne", "同步完成了一个支线任务")
	
	Tra_SubTaskReward = AutoLog.AutoTransaction("Tra_SubTaskReward", "支线任务奖励")

	
	#支线任务条件检测函数
	SubTaskCheckFun_Dict = {}

def LinkCheckSubTaskFun():
	#链接每一种支线任务的检测函数
	global SubTaskCheckFun_Dict
	SubTaskCheckFun_Dict[EnumTaskType.EnSubTask_LevelUpHero] = CheckHeroLevel 		#升级英雄
	SubTaskCheckFun_Dict[EnumTaskType.EnSubTask_UpgradeHero] = HasHero 				#升阶英雄
	SubTaskCheckFun_Dict[EnumTaskType.EnSubTask_FinishFB] = IsFinishFB 				#通关副本
	SubTaskCheckFun_Dict[EnumTaskType.EnSubTask_FinishEvilHole] = IsFinishEvilHole 	#通关恶魔深渊
	SubTaskCheckFun_Dict[EnumTaskType.EnSubTask_JoinUnion] = IsJoinUnion 			#加入帮派
	SubTaskCheckFun_Dict[EnumTaskType.EnSubTask_JoinCamp] = IsJoinCamp 				#加入阵营
	SubTaskCheckFun_Dict[EnumTaskType.EnSubTask_ExChangeItem] = CheckExChangeItem 	#兑换物品
	SubTaskCheckFun_Dict[EnumTaskType.EnSubTask_GetJJCScore] = CheckJJCScore 		#获得竞技场积分
	SubTaskCheckFun_Dict[EnumTaskType.EnSubTask_HeroOnStation] = CheckHeroOnStation #上阵英雄
	SubTaskCheckFun_Dict[EnumTaskType.EnSubTask_UseHeroDesk] = UseHeroDesk 			#使用点将台
	
	SubTaskCheckFun_Dict[EnumTaskType.EnSubTask_ZhaoMuHero] = HasHero 				#招募英雄
	SubTaskCheckFun_Dict[EnumTaskType.EnSubTask_RoleGrade] = CheckRoleGrade 		#主角品阶
	
	SubTaskCheckFun_Dict[EnumTaskType.EnSubTask_StarGirlUnLock] = CheckStarGirlUnLock
	
	
	#预处理配置表对象的检测函数
	for cfg in TaskConfig.SubTaskConfig_Dict.itervalues():
		fun = SubTaskCheckFun_Dict.get(cfg.taskType)
		if not fun:
			print "GE_EXC, error in LinkCheckSubTaskFun not this type (%s)" % cfg.taskType
			continue
		cfg.LinkCheckFun(fun)

def OnGetSubTaskReward(role, msg):
	'''
	请求完成领取一个已经完成的支线任务奖励
	@param role:
	@param msg:
	'''
	subTaskObj = role.GetObj(EnumObj.SubTaskDict)
	finishset = subTaskObj[3]
	taskIndex = msg
	if taskIndex not in finishset:
		return
	
	cfg = TaskConfig.SubTaskConfig_Dict.get(taskIndex)
	if not cfg:
		return
	
	with Tra_SubTaskReward:
		finishset.discard(taskIndex)
		cfg.RewardRole(role)

	#尝试激活下一批任务
	if cfg.nextCfgs:
		for nextCfg in cfg.nextCfgs:
			if role.GetLevel() < nextCfg.needLevel:
				#等级还不足激活这个任务，加入等待激活集合中
				subTaskObj[1].add(nextCfg.subTaskIndex)
			else:
				AcceptTaskEx(role, subTaskObj, nextCfg)

	role.SendObj(SubTask_Data, (subTaskObj[2], subTaskObj[3]))

def BelieveClientTaskReward(role, msg):
	'''
	领取相信客户端任务奖励
	@param role:
	@param msg:
	'''
	taskIndex = msg
	
	cfg = TaskConfig.BelieveClientTask_Dict.get(taskIndex)
	if not cfg:
		return
	if role.GetLevel() < cfg.needLevel:
		return
	
	if role.GetI1(EnumInt1.DownloadMicroend):
		return
	role.SetI1(EnumInt1.DownloadMicroend, True)
	
	with Tra_SubTaskReward:
		tips = GlobalPrompt.Reward_Tips
		if cfg.rewardExp:
			role.IncExp(cfg.rewardExp)
			tips += GlobalPrompt.Exp_Tips % cfg.rewardExp
		if cfg.rewardMoney:
			role.IncMoney(cfg.rewardMoney)
			tips += GlobalPrompt.Money_Tips % cfg.rewardMoney
		if cfg.rewardBindRMB:
			role.IncBindRMB(cfg.rewardBindRMB)
			tips += GlobalPrompt.BindRMB_Tips % cfg.rewardBindRMB
		if cfg.rewardItems:
			for item in cfg.rewardItems:
				role.AddItem(*item)
				tips += GlobalPrompt.Item_Tips % item
		role.Msg(2, 0, tips)
	
def AcceptTask(role, taskIndex):
	#接手一个任务
	subTaskObj = role.GetObj(EnumObj.SubTaskDict)
	taskCfg = TaskConfig.SubTaskConfig_Dict.get(taskIndex)
	if not taskCfg:
		print "GE_EXC, error AcceptTask not this task (%s)" % taskIndex
		return
	AcceptTaskEx(role, subTaskObj, taskCfg)

def AcceptTaskEx(role, subTaskObj, taskCfg):
	#已经可以接取这个任务了
	subTaskObj[2].add(taskCfg.subTaskIndex)
	#缓存检测
	cacheDict = role.GetTempObj(EnumTempObj.SubTaskCheckCache)
	if taskCfg.taskType not in cacheDict:
		cacheDict[taskCfg.taskType] = {taskCfg.subTaskIndex : taskCfg}
	else:
		cacheDict[taskCfg.taskType][taskCfg.subTaskIndex] = taskCfg
	
	#检测是否可以完成这个任务(注意有可能循环调用，读表的时候需要检测循环激活任务)
	CheckSubTask(role, taskCfg)



#####################################################################
def CheckSubTask(role, taskCfg, param = None):
	taskIndex = taskCfg.subTaskIndex
	subtasDict = role.GetObj(EnumObj.SubTaskDict)
	unfinishSet = subtasDict[2]
	if taskIndex not in unfinishSet:
		return False
	
	#----------------------------------------------------------
	#判断主体
	if not taskCfg.checkFun(role, taskCfg, param):
		return False
	#----------------------------------------------------------
	
	cacheDict = role.GetTempObj(EnumTempObj.SubTaskCheckCache)
	if cacheDict and taskCfg.taskType in cacheDict:
		#清理检测缓存设置
		if taskIndex in cacheDict[taskCfg.taskType]:
			del cacheDict[taskCfg.taskType][taskIndex]
	#完成了这个任务
	unfinishSet.discard(taskIndex)
	subtasDict[3].add(taskIndex)
	#同步客户端
	role.SendObj(SubTask_FinishOne, taskIndex)
	return True

########################################################################
def IsJoinUnion(role, taskCfg, param = None):
	#是否加入公会
	return role.GetUnionID() != 0

def IsJoinCamp(role, taskCfg, param = None):
	#是否加入阵营
	return role.GetDI32(EnumDisperseInt32.CampID) != 0

def IsFinishFB(role, taskCfg, param = None):
	#是否完成了副本
	fbId = taskCfg.taskParam[0]
	if fbId not in role.GetObj(EnumObj.FB_Star):
		return False
	return True

def IsFinishEvilHole(role, taskCfg, param = None):
	#是否完成了恶魔深渊
	fbId, needStar = taskCfg.taskParam
	star = role.GetObj(EnumObj.EvilHole_Star).get(fbId)
	if not star or star < needStar:
		return False
	return True


def CheckRoleGrade(role, taskCfg, param = None):
	#角色进阶
	grade = taskCfg.taskParam[0]
	return role.GetGrade() >= grade


def HasHero(role, taskCfg, param = None):
	#招募和进阶英雄
	heroNumber, heroType = taskCfg.taskParam
	heroMgr = role.GetTempObj(EnumTempObj.enHeroMgr)
	for hero in heroMgr.HeroDict.itervalues():
		if hero.GetType() != heroType:
			continue
		if hero.GetNumber() >= heroNumber:
			return True
	return False


def CheckHeroLevel(role, taskCfg, param = None):
	#升级英雄
	#某个类型的英雄 大于等于number,大于等于level
	heroNumber, level, heroType = taskCfg.taskParam
	heroMgr = role.GetTempObj(EnumTempObj.enHeroMgr)
	for hero in heroMgr.HeroDict.itervalues():
		if hero.GetType() != heroType:
			continue
		if hero.GetNumber() < heroNumber:
			continue
		if hero.GetLevel() >= level:
			return True
	return False

def CheckHeroOnStation(role, taskCfg, param = None):
	#英雄上阵
	heroNumber, heroType = taskCfg.taskParam
	heroMgr = role.GetTempObj(EnumTempObj.enHeroMgr)
	for hero in heroMgr.HeroDict.itervalues():
		if hero.GetType() != heroType:
			continue
		if hero.GetNumber() < heroNumber:
			continue
		if hero.GetStationID() != 0:
			return True
	return False

def CheckExChangeItem(role, taskCfg, param = None):
	#兑换物品
	if param is None:
		return False
	itemCoding = taskCfg.taskParam[0]
	if itemCoding != param:
		return False
	return True

def CheckJJCScore(role, taskCfg, param = None):
	#竞技积分
	jjcScore = taskCfg.taskParam[0]
	return role.GetDI8(EnumDayInt8.JJC_Score) >= jjcScore

def UseHeroDesk(role, taskCfg, param = None):
	#点将台
	if param is None:
		return False
	#只要有触发就是完成(触发的时候，参数不是None)
	return True

def CheckStarGirlUnLock(role, taskCfg, param = None):
	#是否解锁星灵
	starGirlMgr = role.GetTempObj(EnumTempObj.StarGirlMgr)
	stargirlId = taskCfg.taskParam[0]
	return stargirlId in starGirlMgr.girl_dict

#####################################################################
#事件触发
#####################################################################
def TriggerSubTask(role, param):
	#普通支线任务触发
	enumType, _ = param
	#优化检测
	cacheDict = role.GetTempObj(EnumTempObj.SubTaskCheckCache)
	if enumType not in cacheDict:
		#不需要检测这个
		return
	
	for cfg in cacheDict[enumType].values():
		#触发检测
		CheckSubTask(role, cfg, param[1])

def AfterChangeCamp(role, oldValue, newValue):
	#加入阵营(特殊)
	cacheDict = role.GetTempObj(EnumTempObj.SubTaskCheckCache)
	if not cacheDict:
		return
	cfgDict = cacheDict.get(EnumTaskType.EnSubTask_JoinCamp)
	if not cfgDict:
		return
	CheckSubTask(role, cfgDict.values()[0])

def AfterChangeUnionID(role, oldValue, newValue):
	#加入公会(特殊)
	if newValue == 0:
		return
	cacheDict = role.GetTempObj(EnumTempObj.SubTaskCheckCache)
	if not cacheDict:
		return
	cfgDict = cacheDict.get(EnumTaskType.EnSubTask_JoinUnion)
	if not cfgDict:
		return
	CheckSubTask(role, cfgDict.values()[0])
	
	#设置外观
	role.SetApperance(EnumAppearance.App_UnionId, newValue)


#####################################################################
#数据同步
#####################################################################
def AfterLogin(role, param):
	#缓存需要检测的支线任务配置到TempObj中
	stDict = role.GetObj(EnumObj.SubTaskDict)
	cacheDict = {}
	for SubTaskIndex in stDict[2]:
		cfg = TaskConfig.SubTaskConfig_Dict.get(SubTaskIndex)
		if not cfg:
			print "GE_EXC, error in AfterLogin cache subtask cfg (%s)" % SubTaskIndex
			continue
		if cfg.taskType not in cacheDict:
			cacheDict[cfg.taskType] = {SubTaskIndex : cfg}
		else:
			cacheDict[cfg.taskType][SubTaskIndex] = cfg
	
	#设置缓存配置字典
	role.SetTempObj(EnumTempObj.SubTaskCheckCache, cacheDict)


def AfterLevelUp(role, param):
	#角色升级之后,检测是否触发接取支线任务
	subTaskObj = role.GetObj(EnumObj.SubTaskDict)
	unFinishTasks = subTaskObj[2]
	activeTasks = TaskConfig.LevelActiveSubTask.get(role.GetLevel())
	needSync = False
	if activeTasks:
		#等级激活，并且没有前置条件的任务,等级到了直接接取任务
		needSync = True
		for taskCfg in activeTasks:
			AcceptTaskEx(role, subTaskObj, taskCfg)

	unAcceptTasks = subTaskObj[1]
	if unAcceptTasks:
		#检测有前置条件，但是等级不够的未接任务是否可以接取了
		acceptTaskSet = set()
		errorTaskSet = set()
		level = role.GetLevel()
		
		cacheDict = role.GetTempObj(EnumTempObj.SubTaskCheckCache)
		for taskIndex in unAcceptTasks:
			cfg = TaskConfig.SubTaskConfig_Dict.get(taskIndex)
			if not cfg:
				print "GE_EXC, del sub task in AfterLevelUp not this task"
				errorTaskSet.add(taskIndex)
				continue
			if cfg.needLevel > level:
				continue
			
			acceptTaskSet.add(cfg)
			needSync = True
			if cfg.taskType not in cacheDict:
				cacheDict[cfg.taskType] = {taskIndex : cfg}
			else:
				cacheDict[cfg.taskType][taskIndex] = cfg
		
		for ti in errorTaskSet:
			unAcceptTasks.discard(ti)
		for accepttaskcfg in acceptTaskSet:
			unAcceptTasks.discard(accepttaskcfg.subTaskIndex)
			AcceptTaskEx(role, subTaskObj, accepttaskcfg)
	
	if needSync:
		role.SendObj(SubTask_Data, (unFinishTasks, subTaskObj[3]))
	
def SyncRoleOtherData(role, param):
	#同步支线任务所有数据
	stDict = role.GetObj(EnumObj.SubTaskDict)
	role.SendObj(SubTask_Data, (stDict[2], stDict[3]))


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#服务器启动预处理
		LinkCheckSubTaskFun()
		
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_AfterLevelUp, AfterLevelUp)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		#触发检测
		Event.RegEvent(Event.Eve_SubTask, TriggerSubTask)
		
		cRoleDataMgr.SetDisperseInt32Fun(EnumDisperseInt32.CampID, AfterChangeCamp)
		cRoleDataMgr.SetInt32Fun(EnumInt32.UnionID, AfterChangeUnionID)
		
		#客户端请求
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("SubTask_OnGetSubTaskReward", "请求领取一个已经完成的支线任务奖励"), OnGetSubTaskReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("SubTask_BelieveClient", "请求领取信任客户端任务奖励"), BelieveClientTaskReward)
		
		