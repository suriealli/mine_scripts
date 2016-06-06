#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQLZ.QQLZBaoXiangConfig")
#===============================================================================
# 蓝钻宝箱配置
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("QQLZ")
	
	QQLZBaoXiang_Config_Base = None	#活动控制配置

	QQLZBX_REWARD_RANDOM_DICT_6 = {}		#蓝钻宝箱前六个随机字典
	QQLZBX_REWARD_RANDOM_DICT_3 = {}		#蓝钻宝箱后三个随机字典
	
	QQLZBX_LEVEL_DICT = {}					#蓝钻宝箱等级段标志

class QQLZBaoXiangBase(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("QQLZBaoXiangBase.txt")
	def __init__(self):
		self.activeTitle = str
		self.beginDate = self.GetDatetimeByString
		self.endDate = self.GetDatetimeByString
		self.needLevel = int

class QQLZBaoXiangRewardConfig(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("QQLZBaoXiangReward.txt")
	def __init__(self):
		self.section = int
		self.level = self.GetEvalByString
		self.items = self.GetEvalByString 
		self.itemsShow = self.GetEvalByString

def LoadQQLZBaoXiangBase():
	global QQLZBaoXiang_Config_Base
	for cfg in QQLZBaoXiangBase.ToClassType():
		if QQLZBaoXiang_Config_Base:
			print "GE_EXC, QQLZBaoXiang_Config_Base already have data!"
		QQLZBaoXiang_Config_Base = cfg

def LoadQQLZBaoXiangReward():
	global QQLZBX_REWARD_RANDOM_DICT_6
	global QQLZBX_REWARD_RANDOM_DICT_3
	for config in QQLZBaoXiangRewardConfig.ToClassType():
		REWARD_RANDOM_DICT_6 = Random.RandomRate()
		REWARD_RANDOM_DICT_3 = Random.RandomRate()
		for index, coding, cnt, rate in config.items:
			REWARD_RANDOM_DICT_6.AddRandomItem(rate, (index,coding, cnt))
		for index, coding, cnt, rate in config.itemsShow:
			REWARD_RANDOM_DICT_3.AddRandomItem(rate, (index,coding, cnt))
		for _level in xrange(config.level[0], config.level[1] + 1):
			QQLZBX_REWARD_RANDOM_DICT_6[_level] = REWARD_RANDOM_DICT_6
			QQLZBX_REWARD_RANDOM_DICT_3[_level] = REWARD_RANDOM_DICT_3
			QQLZBX_LEVEL_DICT[_level] = config.section

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadQQLZBaoXiangBase()
		LoadQQLZBaoXiangReward()
