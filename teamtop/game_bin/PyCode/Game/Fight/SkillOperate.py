#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.SkillOperate")
#===============================================================================
# 技能操作
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Fight import SkillOperateConfig
from Game.Role.Data import EnumInt32, EnumObj, EnumTempObj

if "_HasLoad" not in dir():
	#事务
	Tra_StudySkill = AutoLog.AutoTransaction("Tra_StudySkill", "学习一个技能")
	Tra_LevelUpSkill = AutoLog.AutoTransaction("Tra_LevelUpSkill", "升级一个技能")
	Tra_EvolveSuperSkill = AutoLog.AutoTransaction("Tra_EvolveSuperSkill", "进化超级技能")
	Tra_LevelUpSuperSkill = AutoLog.AutoTransaction("Tra_LevelUpSuperSkill", "升级一个超级技能")
	#同步
	Skill_S_RoleFightSkill = AutoMessage.AllotMessage("Skill_S_RoleFightSkill", "同步出战技能ID列表")
	Skill_S_RoleSkill = AutoMessage.AllotMessage("Skill_S_RoleSkill", "同步已经学习的技能字典数据")

def OnRequestStudySkill(role, msg):
	'''
	请求学习技能
	@param role:
	@param msg:
	'''
	backId, skillId = msg
	cfg = SkillOperateConfig.RoleSkillConfig_Dict.get(skillId)
	if not cfg:
		return
	
	targetSkillCfg = cfg.get(1)
	if not targetSkillCfg:
		return
	
	#已学习
	skillDict = role.GetObj(EnumObj.RoleSkill)
	if skillId in skillDict:
		return
	
	#基本检测
	if not CheckBaseCondition(role, targetSkillCfg):
		return
	
	#前置技能
	if not CheckPerSkillCodition(skillDict, targetSkillCfg):
		return
	
	#龙脉约束检测
	if not CheckRoleDragonCondition(role, targetSkillCfg):
		return
	
	with Tra_StudySkill:
		#消耗技能点
		role.DecI32(EnumInt32.SkillPoint, targetSkillCfg.skillPoint)
		#增加新技能
		skillDict[skillId] = 1
	
	#回调客户端
	role.CallBackFunction(backId, None)
	
	#技能自动上阵处理
	if not targetSkillCfg.isAutoEquip:
		return
	
	#出战技能已满
	fightSkillList = role.GetObj(EnumObj.RoleFightSkill)[1]
	if len(fightSkillList) >= 5:
		return
	
	#技能出战
	fightSkillList.append(skillId)	
	role.SendObj(Skill_S_RoleFightSkill, fightSkillList)

def LevelUpSkill(role, msg):
	'''
	请求升级技能
	@param role:
	@param msg:
	'''
	#参数检测
	backId, skillId = msg
	cfg = SkillOperateConfig.RoleSkillConfig_Dict.get(skillId)
	if not cfg:
		return
	
	#是否已经学习
	skillDict = role.GetObj(EnumObj.RoleSkill)
	skillLevel = skillDict.get(skillId)
	if not skillLevel:
		return
	
	#目标技能是否存在
	targetSkillCfg = cfg.get(skillLevel + 1)
	if not targetSkillCfg:
		return
	
	#基本条件检测
	if not CheckBaseCondition(role, targetSkillCfg):
		return
	
	#前置技能检测
	if not CheckPerSkillCodition(skillDict, targetSkillCfg):
		return
	
	#龙脉约束检测
	if not CheckRoleDragonCondition(role, targetSkillCfg):
		return
	
	with Tra_LevelUpSkill:
		#扣除技能点
		role.DecI32(EnumInt32.SkillPoint, targetSkillCfg.skillPoint)
		#提升技能等级
		skillDict[skillId] = skillLevel + 1
	
	#回调客户端
	role.CallBackFunction(backId, (skillId, None))

def OnEquipSkill(role, msg):
	'''
	出战技能
	@param role:
	@param msg:
	'''
	#参数检测
	backId, skillId = msg	
	skillDict = role.GetObj(EnumObj.RoleSkill)	
	if skillId not in skillDict:
		return
	
	#已出战
	fightSkillList = role.GetObj(EnumObj.RoleFightSkill)[1]
	if skillId in fightSkillList:
		return
	
	#没有空技能槽
	if len(fightSkillList) >= 5:
		return
	
	#出战并回调
	fightSkillList.append(skillId)
	role.CallBackFunction(backId, None)

def UnLoadSkill(role, msg):
	'''
	取消出战技能
	@param role:
	@param msg:
	'''
	#为出战技能
	backId, skillId = msg
	fightSkillList = role.GetObj(EnumObj.RoleFightSkill)[1]
	if skillId not in fightSkillList:
		return
	
	#特殊判断, 第一个技能不能下阵 
	if skillId in EnumGameConfig.SKILLOPERATE_CannotChangePosSkillID:
		return
	
	#下阵并回调
	fightSkillList.remove(skillId)
	role.CallBackFunction(backId, None)

def SetFightSkillToPos(role, msg):
	'''
	出战
	@param role:
	@param msg:
	'''
	#参数检测
	backId, (skillId, pos) = msg
	if pos < 0 or pos > 4:
		return
	
	#特殊判断, 第一个技能不能交换位置
	if skillId in EnumGameConfig.SKILLOPERATE_CannotChangePosSkillID:
		return
	
	#出战技能未满
	fightSkillList = role.GetObj(EnumObj.RoleFightSkill)[1]
	if len(fightSkillList) < 5:
		return
	
	#未学习该技能
	skillDict = role.GetObj(EnumObj.RoleSkill)	
	if skillId not in skillDict:
		return
	
	#出阵 
	if skillId in fightSkillList:
		index = fightSkillList.index(skillId)
		if index == pos:
			return
		#特殊判断, 不能和第一个技能交换位置
		if fightSkillList[pos] in EnumGameConfig.SKILLOPERATE_CannotChangePosSkillID:
			return
		fightSkillList[pos], fightSkillList[index] = fightSkillList[index], fightSkillList[pos]
	else:
		fightSkillList[pos] = skillId
	
	#回调
	role.CallBackFunction(backId, None)
	
def OnRequestEvolveSkill(role, msg):
	'''
	技能进化请求处理
	@param role:
	@param msg: backId，superSkillId 
	'''
	#检测对应技能是否存在
	backId, superSkillId = msg
	superSkillDict = SkillOperateConfig.RoleSuperSkillConfig_Dict.get(superSkillId)
	if not superSkillDict:
		return
	
	#目标技能是否存在
	targetSkillCfg = superSkillDict.get(1)
	if not targetSkillCfg:
		return
	
	#已经拥有该技能
	roleSkillDict = role.GetObj(EnumObj.RoleSkill)
	if targetSkillCfg.skillId in roleSkillDict:
		return
	
	#基本条件检测
	if not CheckBaseCondition(role, targetSkillCfg):
		return
	
	#前置技能检测
	if not CheckPerSkillCodition(roleSkillDict, targetSkillCfg):
		return
	
	#时装条件检测
	if not CheckSuperSkillFashionCondition(role, targetSkillCfg):
		return 
	
	#道具需求检测
	if targetSkillCfg.needPro:
		coding, cnt = targetSkillCfg.needPro
		if role.ItemCnt(coding) < cnt:
			return
	
	#先回调  再处理完同步(客户端需求)
	role.CallBackFunction(backId, (targetSkillCfg.perSkillID,superSkillId))
	
	#process
	with Tra_EvolveSuperSkill:
		#扣除技能点
		if targetSkillCfg.skillPoint:
			role.DecI32(EnumInt32.SkillPoint, targetSkillCfg.skillPoint)
		
		#扣除消耗道具
		if targetSkillCfg.needPro:
			coding, cnt = targetSkillCfg.needPro
			role.DelItem(coding, cnt)
		
		#删除进化前技能 
		roleSkillDict = role.GetObj(EnumObj.RoleSkill)
		if targetSkillCfg.replaceSkillId in roleSkillDict:
			del roleSkillDict[targetSkillCfg.replaceSkillId]
		#增加进化后技能
		roleSkillDict[superSkillId] = 1
		#update玩家技能
		role.SetObj(EnumObj.RoleSkill, roleSkillDict)
	
	#替换已出战的进化前技能
	fightSkillList = role.GetObj(EnumObj.RoleFightSkill)[1]
	if targetSkillCfg.replaceSkillId not in fightSkillList:
		return
	
	oldSkillIndex = fightSkillList.index(targetSkillCfg.replaceSkillId)
	fightSkillList[oldSkillIndex] = superSkillId
	
	#同步最新出战技能
	role.SendObj(Skill_S_RoleFightSkill, fightSkillList)

def OnLevelUpSuperSkill(role, msg):
	'''
	高级技能升级请求处理
	@param role: 
	@param msg: backId, superSkillId 
	'''
	#检测对应技能是否存在
	backId, superSkillId = msg
	superSkillDict = SkillOperateConfig.RoleSuperSkillConfig_Dict.get(superSkillId)
	if not superSkillDict:
		return
	
	#未学习该技能
	roleSkillDict = role.GetObj(EnumObj.RoleSkill)
	oldLevel = roleSkillDict.get(superSkillId)
	if not oldLevel:
		return
	
	#该技能没有更高等级
	targetSkillCfg = superSkillDict.get(oldLevel + 1)
	if not targetSkillCfg:
		return
	
	#检测基本条件
	if not CheckBaseCondition(role, targetSkillCfg):
		return
	
	#时装条件检测
	if not CheckSuperSkillFashionCondition(role, targetSkillCfg):
		return 
	
	#龙脉约束检测
	if not CheckRoleDragonCondition(role, targetSkillCfg):
		return
	
	#星灵星级约束检测
	if not CheckRoleStarGirlCondition(role, targetSkillCfg):
		return
	
	#道具需求检测
	if targetSkillCfg.needPro:
		coding, cnt = targetSkillCfg.needPro
		if role.ItemCnt(coding) < cnt:
			return
	
	#成功升级回调
	role.CallBackFunction(backId, superSkillId)
	
	#process
	with Tra_LevelUpSuperSkill:
		#扣除技能点 技能点是否足够已在check中检测 直接扣除
		if targetSkillCfg.skillPoint:
			role.DecI32(EnumInt32.SkillPoint, targetSkillCfg.skillPoint)
		
		#扣除消耗道具
		if targetSkillCfg.needPro:
			coding, cnt = targetSkillCfg.needPro
			role.DelItem(coding, cnt)
		
		#技能等级提升
		roleSkillDict[superSkillId] = oldLevel + 1
		#update玩家技能
		role.SetObj(EnumObj.RoleSkill, roleSkillDict)
	
def CheckBaseCondition(role, targetSkillCfg):
	'''
	技能状态为roleSkillDict前提下 检测目标技能targetSkillCfg的基本条件：
	职业、等级、星阶、技能点
	'''
	if role.GetCareer() != targetSkillCfg.needCareer:
		return False
	
	#等级限制
	if targetSkillCfg.needRoleLv:
		if role.GetLevel() < targetSkillCfg.needRoleLv:
			return False
	
	#星阶限制
	if targetSkillCfg.needGrade:
		if role.GetGrade() < targetSkillCfg.needGrade:
			return False
	
	#技能点不足
	if role.GetI32(EnumInt32.SkillPoint) < targetSkillCfg.skillPoint:
		return False
	
	return True

def CheckPerSkillCodition(roleSkillDict, targetSkillCfg):
	'''
	检测技能学习状态为roleSkillDict的前提下  是否满足目标技能targetSkillCfg的前置技能条件
	'''
	if targetSkillCfg.perSkillCondition:
		isPreSkillOK = False
		for needSkillId, needLevel in targetSkillCfg.perSkillCondition:
			tmpPreSkillLevel = roleSkillDict.get(needSkillId)
			if tmpPreSkillLevel and tmpPreSkillLevel >= needLevel:
				isPreSkillOK = True
				break
		#不满足前置条件约束
		if not isPreSkillOK:
			return False
	
	#没有前置技能要求 直接满足
	return True

def CheckRoleDragonCondition(role, skillCfg):
	'''
	检测玩家是否达到技能配置skillCfg的龙脉需求
	@return: True if satisfy, False otherwise.
	'''
	#保证参数有效性
	if not role or not skillCfg:
		return False
	
	#获取龙脉数据
	dragonVeinMgr = role.GetTempObj(EnumTempObj.DragonVein) 
	#龙脉总等级
	if skillCfg.dragonVeinLevel:
		if dragonVeinMgr.total_level < skillCfg.dragonVeinLevel:
			return False  
	
	#龙脉各品阶
	if skillCfg.dragonVeinGrades:
		gradeDict = dragonVeinMgr.grade_dict
		for grade, needNum in skillCfg.dragonVeinGrades:
			#统计大于等于grade的龙脉总数
			satisfyNum = 0
			for k, v in gradeDict.iteritems():
				if k >= grade:
					satisfyNum += v
					
			if satisfyNum < needNum:
				return False 
		
	#某龙某珠某等级
	if skillCfg.dragonBalls:
		dragonTrainMgr = role.GetTempObj(EnumTempObj.DragonTrainMgr)
		for dragonID, pos, needGrade in skillCfg.dragonBalls:
			#未激活神龙
			if dragonID not in dragonTrainMgr.dragon_dict:
				return False
	
			dragonObj = dragonTrainMgr.dragon_dict[dragonID]			
			curGrade = dragonObj.ball_dict.get(pos, 0)
			if curGrade < needGrade:
				return False
		
	return True

def CheckSuperSkillFashionCondition(role, superSkillCfg):
	'''
	高级技能时装条件检测
	@param role:
	@param superSkillCfg:  
	@return: True if satisfy, False otherwise.
	'''
	#指定时装部位约束
	if superSkillCfg.fashionNomal:
		FashionGlobalMgr = role.GetTempObj(EnumTempObj.enRoleFashionGlobalMgr)
		posGradeStarDict = FashionGlobalMgr.GetPosGradeStarDict()
		
		satisfyNum = 0
		needNum = len(superSkillCfg.fashionNomal)
		for pos, needGrade, needStar in superSkillCfg.fashionNomal:
			#玩家在要求的部位没有时装 
			if pos not in posGradeStarDict:
				return False
			
			gradeStarDict = posGradeStarDict.get(pos)
			for myGrade, myStar in gradeStarDict:
				if myGrade >= needGrade and myStar >= needStar:
					satisfyNum += 1
					break	#该部位条件以满足 跳出去判断下一个部位 保证satisfyNum一个部位只统计一次满足的情况
		
		if satisfyNum < needNum:
			return False	
			
	#指定特定时装约束
	if superSkillCfg.fashionSpecial:
		FashionGlobalMgr = role.GetTempObj(EnumTempObj.enRoleFashionGlobalMgr)
		actived_dict = FashionGlobalMgr.fashion_active_dict
		for coding, grade, star in superSkillCfg.fashionSpecial:
			if coding not in actived_dict:
				return False
			
			fashionData = actived_dict.get(coding)			
			if fashionData[1] < grade:
				return False
			
			if fashionData[3] < star:
				return False
			
	#通过检测		
	return True

def CheckRoleStarGirlCondition(role, skillCfg):
	'''
	检测role关与skillCfg要求的星灵星级要求是否满足
	@return: True if satisfy, False otherwise.
	'''
	#保证参数有效性
	if not role or not skillCfg:
		return False
	
	#获取龙脉数据
	starGirlMgr = role.GetTempObj(EnumTempObj.StarGirlMgr)
	starLevelDict = starGirlMgr.GetAllStarGirlStarLevel()
	needLevel = skillCfg.starGirlStarLevel
	if not needLevel:
		return True
	
	#遍历 星灵-星级 字典 判断是否满足
	satisfyFlag = False
	for _, starLevel in starLevelDict.iteritems():
		if starLevel >= needLevel:
			satisfyFlag = True
			break
	
	return satisfyFlag

def SyncRoleOtherData(role, param):
	'''
	同步技能学习状态 和 出战技能列表
	'''
	role.SendObj(Skill_S_RoleSkill, role.GetObj(EnumObj.RoleSkill))
	role.SendObj(Skill_S_RoleFightSkill, role.GetObj(EnumObj.RoleFightSkill)[1])

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
	
	#请求
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Skill_OnRequestStudySkill", "学习一个技能"), OnRequestStudySkill)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Skill_LevelUpSkill", "升级一个技能"), LevelUpSkill)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Skill_OnEquipSkill", "出战技能"), OnEquipSkill)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Skill_UnLoadSkill", "取消出战技能"), UnLoadSkill)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Skill_SetFightSkillToPos", "设置一个出战技能(出战到哪一个位置)"), SetFightSkillToPos)
	
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Skill_OnRequestEvolveSkill", "进化一个技能"), OnRequestEvolveSkill)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Skill_OnLevelUpSuperSkill", "升级一个高级技能"), OnLevelUpSuperSkill)