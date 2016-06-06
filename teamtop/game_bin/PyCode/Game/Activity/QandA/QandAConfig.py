#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.QandA.QandAConfig")
#===============================================================================
# 答题配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile





if "_HasLoad" not in dir():
	QandA_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	QandA_FILE_FOLDER_PATH.AppendPath("exam")
	

	QandA_QA_dict = {}					#答题问题配置
	QandA_Award_dict = {}				#答题奖励配置
	QandA_Questiontype_dict = {}		#题目类型配置，对应世界等级

	

class QandA_QAConfig(TabFile.TabLine):
	'''
	 答题问题配置表
	'''
	FilePath = QandA_FILE_FOLDER_PATH.FilePath("examLib.txt")
	def __init__(self):
		self.index = int
		self.exam_type = int
		self.right = int


class QandA_AwardConfig(TabFile.TabLine):
	'''
	 答题奖励配置表
	'''
	FilePath = QandA_FILE_FOLDER_PATH.FilePath("examAward.txt")
	def __init__(self):
		self.lvl = int
		self.r_item = self.GetEvalByString
		self.r_money = int
		self.w_item = self.GetEvalByString
		self.w_money = int

class QandA_QuestypeConfig(TabFile.TabLine):
	'''
	 问题类型配置表
	'''
	FilePath = QandA_FILE_FOLDER_PATH.FilePath("examType.txt")
	def __init__(self):
		self.global_level = int
		self.exam_type = int


def LoadQandA_QAConfig():
	'''
	 读取答题问题配置表
	'''
	global QandA_QA_dict
	for config in QandA_QAConfig.ToClassType():
		if config.index in QandA_QA_dict:
			print "GE_EXC, repeat config.index(%s) in LoadQandA_QAConfig " % config.index
		QandA_QA_dict[config.index] = config
	

def LoadQandA_AwardConfig():
	'''
	 读取奖励配置表
	'''
	global QandA_Award_dict
	for config in QandA_AwardConfig.ToClassType():
		if config.lvl in QandA_Award_dict:
			print "GE_EXC, repeat config.lvl(%s) in QandA_AwardConfig " % config.lvl
		QandA_Award_dict[config.lvl] = config


def LoadQandA_QuestypeConfig():
	'''
	 读取题目类型配置表
	'''
	global QandA_Questiontype_dict
	for config in QandA_QuestypeConfig.ToClassType():
		if config.global_level in QandA_Questiontype_dict:
			print "GE_EXC, repeat config.global_level(%s) in QandA_Questiontype_dict " % config.global_level
		QandA_Questiontype_dict[config.global_level] = config




if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.EnvIsQQ() and not Environment.EnvIsQQUnion():
		#旧答题，国服不开放
		LoadQandA_QAConfig()
		LoadQandA_AwardConfig()
		LoadQandA_QuestypeConfig()
