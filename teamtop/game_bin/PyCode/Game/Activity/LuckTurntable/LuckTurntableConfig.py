#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.LuckTurntable.LuckTurntableConfig")
#===============================================================================
# 幸运转盘配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile
from Util import Random

if "_HasLoad" not in dir():
	LuckTurntable_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	LuckTurntable_FILE_FOLDER_PATH.AppendPath("LuckTurantable")
	
	LuckTurntable_Lucktype_dict = {}		#幸运类型配置
	LuckTurntable_Award_dict = {}			#奖励配置
	LuckTurntable_Luckcnt_dict = {}			#不同VIP级别使用次数配置


class LuckTurntable_LucktypeConfig(TabFile.TabLine):
	'''
	 幸运类型配置表
	'''
	FilePath = LuckTurntable_FILE_FOLDER_PATH.FilePath("LuckType.txt")
	def __init__(self):
		self.lv = 			int
		self.type = 		int

class LuckTurntable_AwardConfig(TabFile.TabLine):
	FilePath = LuckTurntable_FILE_FOLDER_PATH.FilePath("reward.txt")
	def __init__(self):
		
		self.type = 		int
		self.Items = 		self.GetEvalByString
	
	def recodingrandomaward(self):
		#定义三个Random.RandomRate()变量
		self.randomaward1 = Random.RandomRate()
		self.randomaward2 = Random.RandomRate()
		self.randomaward3 = Random.RandomRate()
		#对数据进行预处理，分别生成5%神石奖励为0,25%奖励为0以及正常奖励三种情况的Random.RandomRate()
		randomitems = self.Items
		
		randomaward1_AddRandomItem = self.randomaward1.AddRandomItem
		for rewarditem , r_rate in randomitems.iteritems():
			randomaward1_AddRandomItem(r_rate, rewarditem)

		
		randomaward2_AddRandomItem = self.randomaward2.AddRandomItem
		randomitems[25] = 0
		for rewarditem , r_rate in randomitems.iteritems():
			randomaward2_AddRandomItem(r_rate, rewarditem)

		randomaward3_AddRandomItem = self.randomaward3.AddRandomItem
		randomitems[5] = 0
		for rewarditem , r_rate in randomitems.iteritems():
			randomaward3_AddRandomItem(r_rate, rewarditem)	


	def randomaward(self, PoolRMB):
		#生成随机奖励
		if PoolRMB <= 6000:
			return self.randomaward3
		elif PoolRMB <= 10000:
			return self.randomaward2
		return self.randomaward1

class LuckTurntable_LuckcntConfig(TabFile.TabLine):
	FilePath = LuckTurntable_FILE_FOLDER_PATH.FilePath("lukcnt.txt")
	def __init__(self):
		self.viplv = 		int
		self.cnt = 			int
		
def Load_LuckTurntable_LucktypeConfig():
	global LuckTurntable_Lucktype_dict
	for config in LuckTurntable_LucktypeConfig.ToClassType():
		if config.lv in LuckTurntable_Lucktype_dict:
			print "GE_EXC, repeat config.lv(%) in Load_LuckTurntable_LuckcntConfig " % config.lv
		LuckTurntable_Lucktype_dict[config.lv] = config

def Load_LuckTurntable_AwardConfig():	
	global LuckTurntable_Award_dict
	for config in LuckTurntable_AwardConfig.ToClassType():
		if config.type in LuckTurntable_Award_dict:
			print "GE_EXC, repeat config.type(%) in Load_LuckTurntable_AwardConfig " % config.type
		config.recodingrandomaward()
		LuckTurntable_Award_dict[config.type] = config.randomaward

def LoadLuckTurntable_LuckcntConfig():	
	global LuckTurntable_Luckcnt_dict
	for config in LuckTurntable_LuckcntConfig.ToClassType():
		if config.viplv in LuckTurntable_Luckcnt_dict:
			print "GE_EXC, repeat config.viplv(%) in Load_LuckTurntable_LuckcntConfig " % config.viplv
		LuckTurntable_Luckcnt_dict[config.viplv] = config



if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Load_LuckTurntable_LucktypeConfig()
		Load_LuckTurntable_AwardConfig()
		LoadLuckTurntable_LuckcntConfig()
		