#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Task.MainTask")
#===============================================================================
# 主线任务
#===============================================================================
import cRoleMgr
import Environment
from Util import Callback
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from ComplexServer.Plug.DB import DBProxy
from Game.Task import TaskConfig, EnumTaskType
from Game.Role.Data import EnumDynamicInt64, EnumTempObj, EnumObj, EnumInt1
from Game.Role import Event


def LogFirstRole(role):
	# 统计第一次操作（要求当前步骤为0，设置为非0）
	login_info = role.GetTempObj(EnumTempObj.LoginInfo)
	DBProxy.DBRoleVisit(role.GetRoleID(), "Info_Operate", login_info.get("account", "unknwon"))


def RequestGoStep(role, msg):
	'''
	客户端请求改变主线任务步骤
	@param role:
	@param msg:
	'''
	next_step = msg
	now_step = role.GetDI64(EnumDynamicInt64.Task_Main)
	if now_step == 0:
		LogFirstRole(role)
	# 找到当前任务步骤
	now_mtc = TaskConfig.MainTaskConfig_Dict.get(now_step)
	if now_mtc is None:
		print "GE_EXC, role(%s), can't find now_step(%s)." % (role.GetRoleID(), now_step)
		role.WPE()
		return
	
	#尝试进入下一个步骤
	TryNextStep(role, now_mtc, now_step, next_step)

def TryNextStep(role, now_mtc, now_step, next_step, needBefore = True):
	# 匹配下一步
	next_mtc = now_mtc.GetNext(next_step)
	#错了就直接不处理了
	if next_mtc is False:
		return
	# 可能是最后一步了，可能是表填错了。
	if next_mtc is None:
		print "GE_EXC, cfg error RequestGoStep now_step(%s) next_step (%s)" % (now_step, next_step)
		return
	if role.GetLevel() < next_mtc.needLv:
		#等级不足
		return
	
	if now_mtc.checkFun:
		#任务完成条件检测
		if not now_mtc.checkFun(role, now_mtc.taskParam):
			return
	
	if needBefore is True:
		#需要进入下一步前做某些事情，做完重新调用这个函数，设置needBefore = False
		if BeforeChangeStep(next_step, role) is True:
			return 

	with TraMainTask:
		# 记录新的主线任务步骤
		role.SetDI64(EnumDynamicInt64.Task_Main, next_step)
		#发放旧的步骤的任务奖励
		now_mtc.RewardRole(role)
		#触发改变主线步骤调用函数
		AfterChangeStep(next_step, role)
		#触发其他事件(注意参数是当前任务的配置)
		Event.TriggerEvent(Event.Eve_AfterChangeStep, role, next_mtc)
		#检测是否可以连续跳转步骤
		CheckNextStep(role, next_mtc)
		#记录日志
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveMainTask, next_step)
		#必须返回True
		return True


def CheckNextStep(role, now_mtc):
	#检测是否可以再次跳转步骤
	if not now_mtc:
		return
	next_step = now_mtc.nextStep
	#next_mtc = now_mtc.next_step_cfg
	if now_mtc.taskType <= 0 or not now_mtc.checkFun:
		#不是服务器需要检测的任务，不自动跳转步骤
		return
	TryNextStep(role, now_mtc, now_mtc.stepIndex, next_step)


def RequestTaskEgg(role, msg):
	'''
	只主线任务砸蛋
	@param role:
	@param msg:
	'''
	
	if role.GetI1(EnumInt1.MianTaskEgg):
		return
	with TraMainTaskEgg:
		#先设置已经领取
		role.SetI1(EnumInt1.MianTaskEgg, True)
		
		tips = GlobalPrompt.Reward_Tips
		role.IncMoney(EnumGameConfig.EggMoney)
		tips += GlobalPrompt.Money_Tips % EnumGameConfig.EggMoney
		role.IncBindRMB(EnumGameConfig.EggBindRMB)
		tips += GlobalPrompt.BindRMB_Tips % EnumGameConfig.EggBindRMB
		for itemCoding, cnt in EnumGameConfig.EggItems:
			role.AddItem(itemCoding, cnt)
			tips += GlobalPrompt.Item_Tips % (itemCoding, cnt)
		
		role.Msg(2, 0, tips)
######################################################################################
#任务条件处理模版函数
######################################################################################

def PreprocessTask():
	#预处理任务
	#链接任务对应的检测任务达成条件的检测函数
	for taskStep, mtc in TaskConfig.MainTaskConfig_Dict.iteritems():
		#预处理
		mtc.Preprocess()
		taskType = mtc.taskType
		if taskType <= 0:
			continue
		
		if taskType == EnumTaskType.EnTask_StudySkill:
			mtc.SetCheckFun(CheckSkillLevel)
		elif taskType == EnumTaskType.EnTask_LevelUpSkill:
			mtc.SetCheckFun(CheckSkillLevel)
		elif taskType == EnumTaskType.EnTask_ZhaoMuHero:
			mtc.SetCheckFun(CheckHero)
		elif taskType == EnumTaskType.EnTask_LevelUpHero:
			mtc.SetCheckFun(CheckHeroLevel)
		elif taskType == EnumTaskType.EnTask_UpgradeHero:
			mtc.SetCheckFun(CheckHero)
		elif taskType == EnumTaskType.EnTask_HeroOnStation:
			mtc.SetCheckFun(CheckHeroStation)
		else:
			print "GE_EXC, error tasktype(%s) in PreprocessTask  taskStep(%s)" % (taskType, taskStep)

def CheckHero(role, param):
	#是有有这个类型，大于等于这个编号的英雄
	heroNumber, heroType, _ = param
	heroMgr = role.GetTempObj(EnumTempObj.enHeroMgr)
	for hero in heroMgr.HeroDict.itervalues():
		if hero.GetType() != heroType:
			continue
		if hero.GetNumber() >= heroNumber:
			return True
	return False


def CheckHeroLevel(role, param):
	#指定英雄等级
	heroNumber, level, heroType = param
	heroMgr = role.GetTempObj(EnumTempObj.enHeroMgr)
	for hero in heroMgr.HeroDict.itervalues():
		if hero.GetType() != heroType:
			continue
		if hero.GetNumber() < heroNumber:
			continue
		if hero.GetLevel() >= level:
			return True
	return False


def CheckHeroStation(role, param):
	#英雄上阵
	heroNumber, heroType, _ = param
	heroMgr = role.GetTempObj(EnumTempObj.enHeroMgr)
	for hero in heroMgr.HeroDict.itervalues():
		if hero.GetType() != heroType:
			continue
		if hero.GetNumber() < heroNumber:
			continue
		if hero.GetStationID() != 0:
			return True
	return False

def CheckSkillLevel(role, param):
	#要区分职业
	skillId, skillId2, level = param
	if role.GetCareer() == 2:
		skillId = skillId2

	skillDict = role.GetObj(EnumObj.RoleSkill)
	skillLevel = skillDict.get(skillId, 0)
	if skillLevel < level:
		return False
	
	return True

######################################################################################
#改变步骤之前需要先触发
######################################################################################
def RegBeforeChangeStep(step):
	#注册改变步骤函数
	def f(fun):
		global BeforeChangeStep_Fun
		BeforeChangeStep_Fun.RegCallbackFunction(step, fun)
		return fun
	return f

def RegBeforeChangeStepEx(step, fun, regindex = -1):
	#注册改变步骤函数
	global BeforeChangeStep_Fun
	BeforeChangeStep_Fun.RegCallbackFunction(step, fun, index = regindex)

def BeforeChangeStep(step, role):
	#改变步骤，触发函数
	global BeforeChangeStep_Fun
	if step not in BeforeChangeStep_Fun.fundict:
		return False
	BeforeChangeStep_Fun.CallAllFunctionExs(step, role)
	return True


######################################################################################
#改变步骤之后触发
######################################################################################
def RegChangeStep(step):
	#注册改变步骤函数
	def f(fun):
		global AfterChangeStep_Fun
		AfterChangeStep_Fun.RegCallbackFunction(step, fun)
		return fun
	return f

def RegChangeStepEx(step, fun):
	#注册改变步骤函数
	global AfterChangeStep_Fun
	AfterChangeStep_Fun.RegCallbackFunction(step, fun)

def AfterChangeStep(step, role):
	#改变步骤，触发函数
	global AfterChangeStep_Fun
	if step not in AfterChangeStep_Fun.fundict:
		return
	AfterChangeStep_Fun.CallAllFunctionExs(step, role)


def AfterLogin(role, param):
	#登录初始化主线任务战斗怒气保存字典
	role.SetTempObj(EnumTempObj.MainTask_Moral, {})


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		PreprocessTask()
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
	
	BeforeChangeStep_Fun = Callback.LocalCallbacks()
	AfterChangeStep_Fun  = Callback.LocalCallbacks()
	
	
	TraMainTask = AutoLog.AutoTransaction("TraMainTask", "完成主线任务")
	TraMainTaskEgg = AutoLog.AutoTransaction("TraMainTaskEgg", "主线任务砸蛋")
	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Task_Main", "完成一个主线任务"), RequestGoStep)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Task_Main_Egg", "主线任务砸蛋"), RequestTaskEgg)
	
	
