#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.QandA.NewQandAConfig")
#===============================================================================
# 新答题活动配置表   @author: Gaoshuai 2015
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile
from Util import Random


if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("XinDaTi")
	
	questionBankDict = {}		#所有题库配置
	questionTypeDict = {}		#每日答题数量类型配置
	questionRandomDict = {}		#每日答题随机对象字典{0：周日随机对象， 1：周一随机对象 ...}
	finalsRewardDict = {}		#新答题决赛50名之后奖励，这里最好改成一个List
	scoreRankdDict = {}			#初赛得分排名字典{分数：排名等级}
	firstRewardDict = {}		#初赛奖励字典{1：items, 2:items}
	firstRewardDict_fcm = {}	#初赛奖励字典{1：items, 2:items},YY防沉迷


class questionBankConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("questionBank.txt")
	def __init__(self):
		self.index = int	
		self.type = int
		self.answer = self.GetEvalByString


class questionTypeConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("questionType.txt")
	def __init__(self):
		self.index = int
		self.questionIndex = self.GetEvalByString


class finalsRewardConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("finalsReward.txt")
	def __init__(self):
		self.rank = self.GetEvalByString
		self.itemsReward = self.GetEvalByString


class fristRewardConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("fristReward.txt")
	def __init__(self):
		self.scoreIndex = int
		self.levelRange = self.GetEvalByString
		self.score = self.GetEvalByString
		self.money = int
		self.reward = self.GetEvalByString
		self.money_fcm = int                          #金币奖励
		self.reward_fcm = self.GetEvalByString        #奖励列表（itemCoding,itemCnt）


def LoadquestionBankConfig():
	global questionBankDict, questionRandomDict
	for cfg in questionBankConfig.ToClassType():
		if cfg.index in questionBankDict:
			print "GE_EXC, repeat index(%s) in questionBankDict" % cfg.index
		questionBankDict[cfg.index] = set(cfg.answer)
		
		if cfg.type in questionRandomDict:
			RandomObj = questionRandomDict[cfg.type]
			RandomObj.AddRandomItem(10, cfg.index)
		else:
			RandomObj = Random.RandomRate()
			questionRandomDict[cfg.type] = RandomObj


def LoadquestionTypeConfig():
	global questionTypeDict
	for cfg in questionTypeConfig.ToClassType():
		if cfg.index in questionTypeDict:
			print "GE_EXC, repeat index(%s) in questionTypeDict" % cfg.index
		questionTypeDict[cfg.index] = cfg.questionIndex


def LoadfinalsRewardConfig():
	global finalsRewardDict
	
	for cfg in finalsRewardConfig.ToClassType():
		minLev, maxLev = cfg.rank
		if minLev < 51:
			continue
		
		for level in range(minLev, maxLev + 1):
			if level in finalsRewardDict:
				print "GE_EXC, repeat index(%s) in finalsRewardDict" % level
			finalsRewardDict[level] = cfg.itemsReward


def LoadfristRewardConfig():
	global scoreRankdDict, firstRewardDict
	
	for cfg in fristRewardConfig.ToClassType():
		minScore, maxScore = cfg.score
		for score in range(minScore, maxScore + 1):
			if score in scoreRankdDict:
				continue
			scoreRankdDict[score] = cfg
		
		if cfg.scoreIndex not in firstRewardDict:
			firstRewardDict[cfg.scoreIndex] = {}
			firstRewardDict_fcm[cfg.scoreIndex] = {}
		minLevel, maxLevel = cfg.levelRange
		for level in range(minLevel, maxLevel + 1):
			firstRewardDict[cfg.scoreIndex][level] = (cfg.reward, cfg.money)
			firstRewardDict_fcm[cfg.scoreIndex][level] = (cfg.reward_fcm, cfg.money_fcm)


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadquestionBankConfig()
		LoadquestionTypeConfig()
		LoadfinalsRewardConfig()
		LoadfristRewardConfig()
