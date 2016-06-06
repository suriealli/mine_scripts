#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Dragon.DragonMgr")
#===============================================================================
# 神龙管理
#===============================================================================
import cRoleDataMgr
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Dragon import DragonBase, DragonConfig
from Game.Role import Event
from Game.Role.Data import EnumTempObj, EnumInt8, EnumInt16

if "_HasLoad" not in dir():
	#消息
	Dragon_Show_Main_Panel = AutoMessage.AllotMessage("Dragon_Show_Main_Panel", "通知客户端显示神龙主面板")

def ShowDragonMainPanel(role):
	dragonMgr = role.GetTempObj(EnumTempObj.DragonMgr)
	
	#等级，经验，阶级，主动技能字典，被动技能字典
	role.SendObj(Dragon_Show_Main_Panel, (dragonMgr.level, dragonMgr.exp, dragonMgr.grade, dragonMgr.active_skill_dict, dragonMgr.passive_skill_dict))

def DragonChangeCareer(role, careerId, backFunId):
	dragonMgr = role.GetTempObj(EnumTempObj.DragonMgr)
	
	#职业是否相同
	if dragonMgr.career_id == careerId:
		return
	
	#是否存在对应职业的配置
	careerConfig = DragonConfig.DRAGON_CAREER.get(careerId)
	if not careerConfig:
		return
	
	#是否第一次转职
	cnt = role.GetI8(EnumInt8.DragonChangeJobCnt)
	if cnt == 0:
		#创建神龙
		dragonMgr.create_dragon(careerId, careerConfig)
		#转职次数增加
		role.IncI8(EnumInt8.DragonChangeJobCnt, 1)
		#成功回调客户端
		role.CallBackFunction(backFunId, None)
		return
	
	if cnt > DragonConfig.MAX_CHANGE_JON_TIMES:
		cnt = DragonConfig.MAX_CHANGE_JON_TIMES
	cntConfig = DragonConfig.CHANGE_JOB.get(cnt)
	if not cntConfig:
		return
	
	#扣魔晶
	if role.GetRMB() < cntConfig.needRMB:
		return
	role.DecRMB(cntConfig.needRMB)
	
	#次数增加
	if cnt < DragonConfig.MAX_CHANGE_JON_TIMES:
		role.IncI8(EnumInt8.DragonChangeJobCnt, 1)
	
	#转职
	dragonMgr.change_dragon(careerId, careerConfig)
	
	#成功回调客户端
	role.CallBackFunction(backFunId, None)
	
	#更新面板
	ShowDragonMainPanel(role)
	
def DragonLevelUp(role):
	dragonMgr = role.GetTempObj(EnumTempObj.DragonMgr)
	
	#是否已经升级到当前阶级的最大等级
	gradeConfig = DragonConfig.DRAGON_GRADE.get(dragonMgr.grade)
	if not gradeConfig:
		return
	if dragonMgr.level == gradeConfig.maxLevel:
		return
	
	#遍历经验道具
	for itemCoding in DragonConfig.EXP_ITEM_CODING_LIST:
		cnt = role.ItemCnt(itemCoding)
		if cnt == 0:
			continue
		
		itemExpConfig = DragonConfig.DRAGON_EXP_ITEM.get(itemCoding)
		if not itemExpConfig:
			continue
		
		#获取这种物品需要扣除的数量
		delItemCnt = GetDelItemCnt(role, cnt, itemExpConfig, gradeConfig.maxLevel)
		if delItemCnt == 0:
			continue
		
		#删除经验道具
		role.DelItem(itemCoding, delItemCnt)
		
		totalAddExp = delItemCnt * itemExpConfig.exp
		#增加神龙经验
		AddDragonExp(role, totalAddExp, gradeConfig.maxLevel)
	
	#更新面板
	ShowDragonMainPanel(role)
	
def GetDelItemCnt(role, hasItemCnt, itemExpConfig, maxLevel):
	dragonMgr = role.GetTempObj(EnumTempObj.DragonMgr)
	
	delItemCnt = 0
	
	#是否已经升级到当前阶级的最大等级
	if dragonMgr.level == maxLevel:
		return delItemCnt
	
	levelConfig = DragonConfig.DRAGON_EXP.get(dragonMgr.level)
	if not levelConfig:
		return delItemCnt
	
	nowExp = dragonMgr.exp
	itemExp = itemExpConfig.exp
	newLevel = dragonMgr.level
	for _ in xrange(hasItemCnt):
		delItemCnt += 1
		nowExp += itemExp
		
		while nowExp >= levelConfig.exp and newLevel != maxLevel:
			newLevel += 1
			
			#是否已经是当前阶段最高级
			if newLevel == maxLevel:
				nowExp = 0
			else:
				nowExp -= levelConfig.exp
				
			levelConfig = DragonConfig.DRAGON_EXP.get(newLevel)
			if not levelConfig:
				break
			
		if newLevel == maxLevel:
			break
		
	return delItemCnt
		
def AddDragonExp(role, addExp, maxLevel):
	dragonMgr = role.GetTempObj(EnumTempObj.DragonMgr)
	
	levelConfig = DragonConfig.DRAGON_EXP.get(dragonMgr.level)
	if not levelConfig:
		return
	
	nowExp = dragonMgr.exp + addExp
	oldDragonLevel = dragonMgr.level
	while nowExp >= levelConfig.exp and dragonMgr.level != maxLevel:
		dragonMgr.set_dragon_level(dragonMgr.level + 1)
		
		#是否已经是当前阶段最高级
		if dragonMgr.level == maxLevel:
			nowExp = 0
		else:
			nowExp -= levelConfig.exp
			
		levelConfig = DragonConfig.DRAGON_EXP.get(dragonMgr.level)
		if not levelConfig:
			break
		
	dragonMgr.exp = nowExp
	
	#日志事件
	AutoLog.LogBase(role.GetRoleID(), AutoLog.eveDragonLevel, (oldDragonLevel, dragonMgr.level))
	
def DragonUpgrade(role):
	dragonMgr = role.GetTempObj(EnumTempObj.DragonMgr)
	
	gradeConfig = DragonConfig.DRAGON_GRADE.get(dragonMgr.grade)
	if not gradeConfig:
		return
	
	#是否满足升阶等级条件
	if dragonMgr.level != gradeConfig.maxLevel:
		return
	
	#是否已经达到最高阶
	if not gradeConfig.needItemCoding:
		return
	
	#是否有足够的升阶道具
	cnt = role.ItemCnt(gradeConfig.needItemCoding)
	if cnt < gradeConfig.needItemCnt:
		return
	
	#扣除升级道具
	role.DelItem(gradeConfig.needItemCoding, gradeConfig.needItemCnt)
	
	oldDragonGrade = dragonMgr.grade
	#升阶
	dragonMgr.grade += 1
	
	#获得组队技能点
	if gradeConfig.skillPointReward > 0:
		role.IncI16(EnumInt16.DragonSkillPoint, gradeConfig.skillPointReward)
		
	#日志事件
	AutoLog.LogBase(role.GetRoleID(), AutoLog.eveDragonGrade, (oldDragonGrade, dragonMgr.grade))
	
	#提示
	role.Msg(2, 0, GlobalPrompt.DRAGON_UPGRADE_PROMPT)
	
	#更新面板
	ShowDragonMainPanel(role)
	
def DragonStudySkill(role, skillId, backFunId):
	dragonMgr = role.GetTempObj(EnumTempObj.DragonMgr)
	
	careerConfig = DragonConfig.DRAGON_CAREER.get(dragonMgr.career_id)
	if not careerConfig:
		return
	
	#判断技能类型
	if skillId == careerConfig.passiveSkill1:
		#被动技能
		StudyPassiveSkill(role, skillId, backFunId)
	else:
		#主动技能
		StudyActiveSkill(role, skillId, backFunId)
		
		
def StudyActiveSkill(role, skillId, backFunId):
	dragonMgr = role.GetTempObj(EnumTempObj.DragonMgr)
	
	activeSkillList = DragonConfig.ACTIVE_SKILL_DICT.get(dragonMgr.career_id)
	if not activeSkillList:
		return
	#是否对应职业可以学习的主动技能
	if skillId not in activeSkillList:
		return
	
	#是否已经学习了此技能
	if skillId not in dragonMgr.active_skill_dict:
		#判断是否满足学习条件
		skillConfig = DragonConfig.DRAGON_SKILL.get((skillId, 1))
		if not skillConfig:
			return
		
		#是否需要前置技能
		if skillConfig.needSkill:
			preSkillId, preLevel = skillConfig.needSkill
			if preSkillId not in dragonMgr.active_skill_dict:
				if preSkillId not in dragonMgr.passive_skill_dict:
					return
				else:
					#技能等级是否满足
					if dragonMgr.passive_skill_dict[preSkillId] < preLevel:
						return
			else:
				#技能等级是否满足
				if dragonMgr.active_skill_dict[preSkillId] < preLevel:
					return
		
		#扣除技能点
		if role.GetI16(EnumInt16.DragonSkillPoint) < skillConfig.needSkillPoint:
			return
		role.DecI16(EnumInt16.DragonSkillPoint, skillConfig.needSkillPoint)
		
		#学习
		dragonMgr.active_skill_dict[skillId] = 1
		
	else:
		#升级
		level = dragonMgr.active_skill_dict[skillId]
		
		#判断是否满足升级条件
		skillConfig = DragonConfig.DRAGON_SKILL.get((skillId, level))
		if not skillConfig:
			return
		
		#是否已经满级
		if level >= skillConfig.maxLevel:
			return
		
		#是否需要前置技能
		if skillConfig.needSkill:
			preSkillId, preLevel = skillConfig.needSkill
			if preSkillId not in dragonMgr.active_skill_dict:
				if preSkillId not in dragonMgr.passive_skill_dict:
					return
				else:
					#技能等级是否满足
					if dragonMgr.passive_skill_dict[preSkillId] < preLevel:
						return
			else:
				#技能等级是否满足
				if dragonMgr.active_skill_dict[preSkillId] < preLevel:
					return
		
		#下一等级技能的配置
		nextSkillConfig = DragonConfig.DRAGON_SKILL.get((skillId, level + 1))
		if not nextSkillConfig:
			return
		#扣除技能点
		if role.GetI16(EnumInt16.DragonSkillPoint) < nextSkillConfig.needSkillPoint:
			return
		role.DecI16(EnumInt16.DragonSkillPoint, nextSkillConfig.needSkillPoint)
		
		#升级
		dragonMgr.active_skill_dict[skillId] += 1
		
	#回调客户端成功
	role.CallBackFunction(backFunId, None)
		
	#更新面板
	ShowDragonMainPanel(role)
		
def StudyPassiveSkill(role, skillId, backFunId):
	dragonMgr = role.GetTempObj(EnumTempObj.DragonMgr)
	
	#是否已经学习了此技能
	if skillId not in dragonMgr.passive_skill_dict:
		#判断是否满足学习条件
		skillConfig = DragonConfig.DRAGON_SKILL.get((skillId, 1))
		if not skillConfig:
			return
		
		#判断前置技能(只有一个被动技能，前置技能是主动技能)
		if skillConfig.needSkill:
			needSkillId, needSkillLevel = skillConfig.needSkill
			if needSkillId not in dragonMgr.active_skill_dict:
				return
			if needSkillLevel > dragonMgr.active_skill_dict[needSkillId]:
				return
		
		#扣除技能点
		if role.GetI16(EnumInt16.DragonSkillPoint) < skillConfig.needSkillPoint:
			return
		role.DecI16(EnumInt16.DragonSkillPoint, skillConfig.needSkillPoint)
		
		#学习
		dragonMgr.passive_skill_dict[skillId] = 1
		
	else:
		#升级
		level = dragonMgr.passive_skill_dict[skillId]
		
		#判断是否满足升级条件
		skillConfig = DragonConfig.DRAGON_SKILL.get((skillId, level))
		if not skillConfig:
			return
		
		#是否已经满级
		if level >= skillConfig.maxLevel:
			return
		
		#判断前置技能(只有一个被动技能，前置技能是主动技能)
		if skillConfig.needSkill:
			needSkillId, needSkillLevel = skillConfig.needSkill
			if needSkillId not in dragonMgr.active_skill_dict:
				return
			if needSkillLevel > dragonMgr.active_skill_dict[needSkillId]:
				return
		
		#扣除技能点
		if role.GetI16(EnumInt16.DragonSkillPoint) < skillConfig.needSkillPoint:
			return
		role.DecI16(EnumInt16.DragonSkillPoint, skillConfig.needSkillPoint)
		
		#升级
		dragonMgr.passive_skill_dict[skillId] += 1
		
	#回调客户端成功
	role.CallBackFunction(backFunId, None)
		
	#更新面板
	ShowDragonMainPanel(role)
	
#===============================================================================
# 事件
#===============================================================================
def OnRoleInit(role, param):
	'''
	角色初始化
	@param role:
	@param param:
	'''
	role.SetTempObj(EnumTempObj.DragonMgr, DragonBase.DragonMgr(role))
	
def OnRoleSave(role, param):
	'''
	角色保存
	@param role:
	@param param:
	'''
	dragonMgr = role.GetTempObj(EnumTempObj.DragonMgr)
	dragonMgr.save()
	
#===============================================================================
# 设置数组改变调用的函数
#===============================================================================
def AfterChangeDragonSkillPoint(role, oldValue, newValue):
	if newValue <= oldValue:
		return
	
	#技能点增加
	v = newValue - oldValue
	
	#累计组队技能点添加
	role.IncI16(EnumInt16.DragonAllSkillPoint, v)
	
#===============================================================================
# 客户端请求
#===============================================================================
def RequestDragonOpenMainPanel(role, msg):
	'''
	客户端请求打开神龙主面板
	@param role:
	@param msg:
	'''
	ShowDragonMainPanel(role)

def RequestDragonChangeCareer(role, msg):
	'''
	客户端请求神龙职业转换
	@param role:
	@param msg:
	'''
	backFunId, careerId = msg
	
	DragonChangeCareer(role, careerId, backFunId)
	
def RequestDragonLevelUp(role, msg):
	'''
	客户端请求神龙升级
	@param role:
	@param msg:
	'''
	
	#日志
	with TraDragonLevelUp:
		DragonLevelUp(role)
	
def RequestDragonUpgrade(role, msg):
	'''
	客户端请求神龙进阶
	@param role:
	@param msg:
	'''
	#日志
	with TraDragonUpgrade:
		DragonUpgrade(role)
	
def RequestDragonStudySkill(role, msg):
	'''
	客户端请求学习神龙技能
	@param role:
	@param msg:
	'''
	backFunId, skillId = msg
	
	DragonStudySkill(role, skillId, backFunId)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.EnvIsNA() or Environment.IsDevelop):
		#角色初始化
		Event.RegEvent(Event.Eve_InitRolePyObj, OnRoleInit)
		#角色保存
		Event.RegEvent(Event.Eve_BeforeSaveRole, OnRoleSave)
	
	if Environment.HasLogic and not Environment.IsCross and (Environment.EnvIsNA() or Environment.IsDevelop):
		#设置数组改变调用的函数
		cRoleDataMgr.SetInt16Fun(EnumInt16.DragonSkillPoint, AfterChangeDragonSkillPoint)
		
		#日志
		TraDragonLevelUp = AutoLog.AutoTransaction("TraDragonLevelUp", "神龙升级")
		TraDragonUpgrade = AutoLog.AutoTransaction("TraDragonUpgrade", "神龙进阶")
		
		#注册消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Dragon_Open_Main_Panel", "客户端请求打开神龙主面板"), RequestDragonOpenMainPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Dragon_Change_Career", "客户端请求神龙职业转换"), RequestDragonChangeCareer)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Dragon_Level_Up", "客户端请求神龙升级"), RequestDragonLevelUp)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Dragon_Upgrade", "客户端请求神龙进阶"), RequestDragonUpgrade)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Dragon_Study_Skill", "客户端请求学习神龙技能"), RequestDragonStudySkill)
		