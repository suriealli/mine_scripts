#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.SkillOperateConfig")
#===============================================================================
# 技能操作配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile
from Common.Other import EnumGameConfig

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("StudySkill")
	
	RoleSkillConfig_Dict = {}		#普通技能升级配置 {skillId:{skillLevel:cfg,},}
	RoleSuperSkillConfig_Dict = {}	#超级技能升级配置 {skillId:{skillLevel:cfg,},}

class RoleSkillConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("SkillLevelup.txt")
	def __init__(self):
		self.skillId = int
		self.skillType = int	#技能类型(0-普通技能 1-龙脉技能)
		self.level = int		#技能等级
		self.maxLevel = int
		self.isAutoEquip = int
		
		self.needRoleLv = self.GetIntByString
		self.needCareer = int	#必填
		self.needGrade = self.GetIntByString	
		
		#两个前置技能 满足其中一个就算条件满足(因为 英勇打击 和 审判 进化变成了 恶魔血月斩 和 天使审判 )
		self.perSkillID = self.GetIntByString 		#前置技能1
		self.perSkillLevel = self.GetIntByString	#前置技能1等级
		self.perSkillIDEx = self.GetIntByString		#前置技能2
		self.perSkillLevelEx = self.GetIntByString	#前置技能2等级
		
		self.skillPoint = self.GetIntByString		#消耗技能点
		
		#for 龙脉技能
		self.dragonVeinLevel = self.GetIntByString		#龙脉技能总等级要求
		self.dragonVeinGrades = self.GetEvalByString 	#龙脉各品阶数量要求[(grade,needNum),]
		self.dragonBalls = self.GetEvalByString			#龙珠等级要求[(dradonID,pos,level)]
		
		#for 进化
		self.canEvolve = self.GetIntByString		#是否可进化超级技能
		self.superSkillID = self.GetIntByString		#进化后超级技能ID
		
	def CheckAndPreProcess(self):
		#把两个前置条件(如果有)组装起来 方便使用 二者有一即可满足
		self.perSkillCondition = []	
		if self.perSkillID:
			if not self.perSkillLevel:
				print "GE_EXC RoleSkillConfig error skillId(%s) have perSkillID (%s) without perSkillLevel" % (self.skillId, self.perSkillID)
			self.perSkillCondition.append((self.perSkillID, self.perSkillLevel))
		
		if self.perSkillIDEx:
			if not self.perSkillLevelEx:
				print "GE_EXC,RoleSkillConfig error skillId(%s) have perSkillIDEx(%s) without perSkillLevelEx" % (self.skillId, self.perSkillIDEx)
			self.perSkillCondition.append((self.perSkillIDEx,self.perSkillLevelEx))
		
		if self.canEvolve:
			if not self.superSkillID :
				print "GE_EXC, RoleSkillConfig error cfg(%s) canEvolve(%s) without superSkillID(%s)" % (self.skillId, self.canEvolve, self.superSkillID)
		
		if self.skillType == EnumGameConfig.SKILLOPERATE_DragonveinSkill:
			if not (self.dragonVeinLevel or self.dragonVeinGrades or self.dragonBalls):
				print "GE_EXC, RoleSkillConfig error cfg(%s) dragonVein skill without any dragon condition" % self.skillId

class RoleSuperSkillConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("SuperSkillLevelup.txt")
	def __init__(self):
		self.skillId = int 		#技能ID
		self.level = int 		#技能等级
		self.maxLevel = int 	#技能最大等级
		self.isAutoEquip = int	#是否自动装备
		self.needRoleLv = self.GetIntByString	#需要主角等级
		self.needCareer = int	#主角职业
		self.needGrade = self.GetIntByString	#主角品阶 
		
		#两个前置技能 满足其中一个就算条件满足(因为 英勇打击 和 审判 进化变成了 恶魔血月斩 和 天使审判 )
		self.perSkillID = self.GetIntByString 
		self.perSkillLevel = self.GetIntByString 	
		self.perSkillIDEx = self.GetIntByString		
		self.perSkillLevelEx = self.GetIntByString	
		
		self.replaceSkillId = self.GetIntByString	#进化后替换原有技能
		self.fashionNomal = self.GetEvalByString	#某部位时装星阶条件[(pos,grade,star)]
		self.fashionSpecial = self.GetEvalByString	#指定某时装星阶条件[(coding,grade,star)]
		
		self.dragonVeinLevel = self.GetIntByString		#龙脉总等级要求	
		self.dragonVeinGrades = self.GetEvalByString	#龙脉各品阶数量要求[(grade,needNum),]
		self.dragonBalls = self.GetEvalByString			#龙珠等级要求[(dradonID,pos,level)]
		self.starGirlStarLevel = self.GetIntByString	#某星灵星级要求 任意星灵达到该等级即可
		self.needPro = self.GetEvalByString				#道具需求(coding,cnt)
		
		self.skillPoint = self.GetIntByString	#消耗技能点	
	
	def CheckAndPreProcess(self):
		#把两个前置条件(如果有)组装起来 方便使用 二者有一即可满足
		self.perSkillCondition = []	
		if self.perSkillID:
			if not self.perSkillLevel:
				print "GE_EXC RoleSuperSkillConfig error skillId(%s) have perSkillID (%s) without perSkillLevel" % (self.skillId, self.perSkillID)
			self.perSkillCondition.append((self.perSkillID,self.perSkillLevel))
			
		if self.perSkillIDEx:
			if not self.perSkillLevelEx:
				print "GE_EXC,RoleSuperSkillConfig error skillId(%s) have perSkillIDEx(%s) without perSkillLevelEx" % (self.skillId, self.perSkillIDEx)
			self.perSkillCondition.append((self.perSkillIDEx,self.perSkillLevelEx))

def LoadRoleSkillConfig():
	global RoleSkillConfig_Dict
	for RSC in RoleSkillConfig.ToClassType():
		if RSC.skillId not in RoleSkillConfig_Dict:
			RoleSkillConfig_Dict[RSC.skillId] = {}
		RoleSkillConfig_Dict[RSC.skillId][RSC.level] = RSC
		RSC.CheckAndPreProcess()

def LoadRoleSuperSkillConfig():
	global RoleSuperSkillConfig_Dict
	for RSSC in RoleSuperSkillConfig.ToClassType():
		if RSSC.skillId not in RoleSuperSkillConfig_Dict:
			RoleSuperSkillConfig_Dict[RSSC.skillId] = {}
		RoleSuperSkillConfig_Dict[RSSC.skillId][RSSC.level] = RSSC
		RSSC.CheckAndPreProcess()

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadRoleSkillConfig()
		LoadRoleSuperSkillConfig()