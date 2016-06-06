#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Config.RoleConfig")
#===============================================================================
# 角色配置表
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Game.Property import PropertyEnum


if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("RoleConfig")
	
	LEVEL_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	LEVEL_FILE_FOLDER_PATH.AppendPath("LevelGife")
	
	#角色基础配置
	RoleBase_Dict = {}
	#等级经验表
	LevelExp_Dict = {}
	#等级获得技能点
	LevelSkillPoint_Dict = {}
	#根据品阶获取星级
	Grade_To_Star_Dict = {}
	#根据品阶获取颜色编码
	Grade_To_ColorCode_Dict = {}

#经验配置
class LevelExpConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("LevelExp.txt")
	def __init__(self):
		self.level = int
		self.exp = int

class LevelSkillPointConfig(TabFile.TabLine):
	FilePath = LEVEL_FILE_FOLDER_PATH.FilePath("LevelUp.txt")
	def __init__(self):
		self.index = int#等级
		self.skillPoint = int


class RoleBaseProConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("RoleBaseProConfig.txt")
	def __init__(self):
		self.career = int				#职业
		self.grade = int				#等阶
		self.sex = int					#性别
		
		self.star = int					#星级
		self.colorCode = int			#颜色编码
		
		self.upgradeNeedItem = eval		#升阶需要物品
		self.upgradeNeedLv = int		#升阶需要等级
		self.getSkillPoint = int		#升阶获得技能点
		self.nextGrade = int			#下一等阶
		
		self.attack_Plus = int			#攻击成长
		self.attack_Coe = int			#攻击系数
		self.maxhp_Plus = int			#生命成长
		self.maxhp_Coe = int			#生命系数
		
		self.maxhp = int				#生命
		self.attackspeed = int			#攻击速度
		self.anger = int				#怒气
		self.attack_Plus = int			#攻击成长
		self.attack_Coe = int			#攻击系数
		self.attack_p = int				#物攻
		self.defense_p = int			#物防
		self.attack_m = int				#法功
		self.defense_m = int			#法防
		self.crit = int					#暴击
		self.critpress = int			#免暴
		self.antibroken = int			#破防
		self.notbroken = int			#免破
		self.parry = int				#格挡
		self.puncture = int				#破挡
		self.damageupgrade = int		#增伤
		self.damagereduce = int			#免伤
		
		self.CuiLianShiCnt = int		#可以使用淬炼石最大个数
		
	def InitProperty(self):
		self.p_dict = {}
		self.p_dict[PropertyEnum.maxhp] = (self.maxhp, self.maxhp_Plus, self.maxhp_Coe)
		self.p_dict[PropertyEnum.attackspeed] = (self.attackspeed, 0, 0)
		self.p_dict[PropertyEnum.anger] = (self.anger, 0, 0)
		self.p_dict[PropertyEnum.attack_p] = (self.attack_p, self.attack_Plus, self.attack_Coe)
		self.p_dict[PropertyEnum.defense_p] = (self.defense_p, 0, 0)
		self.p_dict[PropertyEnum.attack_m] = (self.attack_m, self.attack_Plus, self.attack_Coe)
		self.p_dict[PropertyEnum.defense_m] = (self.defense_m, 0, 0)
		self.p_dict[PropertyEnum.crit] = (self.crit, 0, 0)
		self.p_dict[PropertyEnum.critpress] = (self.critpress, 0, 0)
		self.p_dict[PropertyEnum.antibroken] = (self.antibroken, 0, 0)
		self.p_dict[PropertyEnum.notbroken] = (self.notbroken, 0, 0)
		self.p_dict[PropertyEnum.parry] = (self.parry, 0, 0)
		self.p_dict[PropertyEnum.puncture] = (self.puncture, 0, 0)
		self.p_dict[PropertyEnum.damageupgrade] = (self.damageupgrade, 0, 0)
		self.p_dict[PropertyEnum.damagereduce] = (self.damagereduce, 0, 0)

		
		global Grade_To_Star_Dict
		if self.grade in Grade_To_Star_Dict:
			if Grade_To_Star_Dict[self.grade] != self.star:
				print "GE_EXC, grade to star error", self.career, self.sex, self.grade
		Grade_To_Star_Dict[self.grade] = self.star
		
		global Grade_To_ColorCode_Dict
		if self.grade in Grade_To_ColorCode_Dict:
			if Grade_To_ColorCode_Dict[self.grade] != self.colorCode:
				print "GE_EXC, grade to colorCode error", self.career, self.sex, self.grade
		Grade_To_ColorCode_Dict[self.grade] = self.colorCode
		
		
def LoadRoleBaseProConfig():
	global RoleBase_Dict
	for RB in RoleBaseProConfig.ToClassType():
		if (RB.career, RB.grade, RB.sex) in RoleBase_Dict:
			print "GE_EXC, repeat in LoadRoleBaseProConfig, (career:%s, grade:%s, sex:%s)" % (RB.career, RB.grade, RB.sex)
			continue
		RoleBase_Dict[(RB.career, RB.grade, RB.sex)] = RB
		RB.InitProperty()
	
def LoadLevelExpConfig():
	global LevelExp_Dict
	for LEC in LevelExpConfig.ToClassType():
		if LEC.level in LevelExp_Dict:
			print "GE_EXC, repeat in LoadLevelExpConfig, (%s)" % LEC.level
		LevelExp_Dict[LEC.level] = LEC.exp
		

def LoadLevelSkillPointConfig():
	global LevelSkillPoint_Dict
	for LEC in LevelSkillPointConfig.ToClassType():
		if LEC.index in LevelSkillPoint_Dict:
			print "GE_EXC, repeat in LoadLevelSkillPointConfig, (%s)" % LEC.index
		
		LevelSkillPoint_Dict[LEC.index] = LEC.skillPoint



if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadLevelExpConfig()
		LoadRoleBaseProConfig()
		LoadLevelSkillPointConfig()
