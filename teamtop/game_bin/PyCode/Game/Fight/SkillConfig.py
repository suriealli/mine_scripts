#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.SkillConfig")
#===============================================================================
# 技能配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile


if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("Fight")
	
	PassiveSkillConfig_Dict = {}


#被动技能
class PassiveSkillConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassiveSkill.txt")
	def __init__(self):
		self.skillId = int			#英雄编号
		self.skillName = str					#名字
		self.pt1 = self.GetPropertyIndex
		self.ptt1 = self.GetIntByString
		self.pv1 = self.GetIntByString
		
		self.pt2 = self.GetPropertyIndex
		self.ptt2 = self.GetIntByString
		self.pv2 = self.GetIntByString


	def Preprocess(self):
		#绝对值
		self.property_dict = {}
		#万份比
		self.property_p_dict = {}
		
		if self.pt1 and self.pv1:
			if self.ptt1 == 1:
				self.property_dict[self.pt1] = self.pv1
			else:
				self.property_p_dict[self.pt1] = self.pv1

		if self.pt2 and self.pv2:
			if self.ptt2 == 2:
				self.property_dict[self.pt2] = self.pv2
			else:
				self.property_p_dict[self.pt2] = self.pv2


def LoadPassiveSkillConfig():
	#读取日常任务配置
	global PassiveSkillConfig_Dict
	for psc in PassiveSkillConfig.ToClassType():
		if psc.skillId in PassiveSkillConfig_Dict:
			print "GE_EXC, error in LoadPassiveSkillConfig (%s)" % psc.skillId
		PassiveSkillConfig_Dict[psc.skillId] = psc
		psc.Preprocess()
		

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadPassiveSkillConfig()


