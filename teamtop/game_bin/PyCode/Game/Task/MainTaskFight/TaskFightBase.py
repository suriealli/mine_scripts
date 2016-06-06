#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Task.MainTaskFight.TaskFightBase")
#===============================================================================
# 主线任务战斗基类
#===============================================================================
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumFightStatistics
from ComplexServer.Log import AutoLog
from Game.Fight import FightEx, SkillOperate
from Game.Role import Status
from Game.Role.Data import EnumDynamicInt64, EnumInt1, EnumObj, EnumTempInt64
from Game.Task import MainTask, TaskConfig


if "_HasLoad" not in dir():
	MianTask_Fight = AutoMessage.AllotMessage("MianTask_Fight", "主线任务战斗")
	
	Tra_MainTaskFight = AutoLog.AutoTransaction("Tra_MainTaskFight", "主线任务战斗奖励")

	
class TFight(object):
	def __init__(self, step, fightCfg = 0):
		'''
		任务战斗
		@param step:
		@param campId:
		@param AfterFightFun:
		'''
		self.fightType = fightCfg.fightType
		self.fightCampId = fightCfg.fightCampId
		self.step = step
		self.fightCfg = fightCfg
		self.anger = fightCfg.anger
		
		self.studySkill = fightCfg.studySkill
		
		MainTask.RegBeforeChangeStepEx(step, self.BeforeChangeStep)
	
	def BeforeChangeStep(self, role):
		#需要判断状态
		if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
			return
	
		self.StartFight(role)
		
	def StartFight(self, role):
		if self.studySkill:
			self.StudySkill(role)
		
		role.SendObj(MianTask_Fight, self.step)
		
		role.SetTI64(EnumTempInt64.MainTaskFightStep, self.step)
		
		#版本判断
		if Environment.EnvIsNA():
			if self.step == 20:
				FightEx.PVE_MainTaskSpecial1(role, self.fightCampId, self.fightType, self.AfterFight , None, self.anger, AfterPlay = self.AfterPlay)
			elif self.step == 50:
				FightEx.PVE_MainTaskSpecial2(role, self.fightCampId, self.fightType, self.AfterFight , None, self.anger, AfterPlay = self.AfterPlay)
			else:
				FightEx.PVE_Task(role, self.fightCampId, self.fightType, self.AfterFight , None, self.anger, AfterPlay = self.AfterPlay)
		
		elif Environment.EnvIsFT() or Environment.EnvIsTK():
			if self.step == 20:
				FightEx.PVE_MainTaskSpecial_tw1(role, self.fightCampId, self.fightType, self.AfterFight , None, self.anger, AfterPlay=self.AfterPlay)
			elif self.step == 50:
				FightEx.PVE_MainTaskSpecial_tw2(role, self.fightCampId, self.fightType, self.AfterFight , None, self.anger, AfterPlay=self.AfterPlay)
			else:
				FightEx.PVE_Task(role, self.fightCampId, self.fightType, self.AfterFight , None, self.anger, AfterPlay=self.AfterPlay)
			
		else:
			FightEx.PVE_Task(role, self.fightCampId, self.fightType, self.AfterFight , None, self.anger, AfterPlay = self.AfterPlay)
	
	
	def AfterPlay(self, fightObj):
		#回调触发
		roles = fightObj.left_camp.roles
		if not roles:
			return
		role = list(roles)[0]
		role.SetTI64(EnumTempInt64.MainTaskFightStep, 0)
		
		if fightObj.result != 1:
			return
		now_step = role.GetDI64(EnumDynamicInt64.Task_Main)
		now_mtc = TaskConfig.MainTaskConfig_Dict.get(now_step)
		if now_mtc is None:
			return
		with Tra_MainTaskFight:
			#改变步骤
			if MainTask.TryNextStep(role, now_mtc, now_step, self.step, False) is True:
				#战斗奖励(可以优化)
				self.fightCfg.RewardRole(role, fightObj.round)
	
	def AfterFight(self, fightObj):
		#回调触发
		if fightObj.result != 1:
			return
		roles = fightObj.left_camp.roles
		if not roles:
			return
		role = list(roles)[0]
		
		star, exp, money, itemCoding, cnt = self.fightCfg.GetFightReward(fightObj.round)
		
		roleId = role.GetRoleID()
		fightObj.set_fight_statistics(roleId, EnumFightStatistics.EnumMainTaskStar, star)
		fightObj.set_fight_statistics(roleId, EnumFightStatistics.EnumExp, exp)
		fightObj.set_fight_statistics(roleId, EnumFightStatistics.EnumMoney, money)
		fightObj.set_fight_statistics(roleId, EnumFightStatistics.EnumItems, [(itemCoding, cnt)])


	def StudySkill(self, role):
		skillId, s2 = self.studySkill
		if role.GetCareer() == 2:
			skillId = s2
			
		skillDict = role.GetObj(EnumObj.RoleSkill)
		if skillId in skillDict:
			return
		skillDict[skillId] = 1
		role.SendObj(SkillOperate.Skill_S_RoleSkill, skillDict)
		
		fightSkillList = role.GetObj(EnumObj.RoleFightSkill)[1]
		if len(fightSkillList) >= 5:
			return
		fightSkillList.append(skillId)
		
		role.SendObj(SkillOperate.Skill_S_RoleFightSkill, fightSkillList)
		
		
