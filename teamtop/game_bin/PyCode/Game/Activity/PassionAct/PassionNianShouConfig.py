#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionNianShouConfig")
#===============================================================================
# 打年兽
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("PassionAct")
	NianShouReward = {}
	#年兽的抽奖机
	NianShou_Reward_Random = {}
	#活动的抽奖道具
	NianShou_Item_Drop = {}


class PassionNianShou(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionNianShouReward.txt")
	def __init__(self):
		self.rewardId = int
		self.rewardType = int
		self.rangeId = int
		self.levelRange = self.GetEvalByString
		self.item = self.GetEvalByString
		self.rate = int
		self.isPrecious =int
		self.isBroadcast = int


def LoadPassionNianShou():
	global NianShou_Reward_Random, NianShouReward
	for cf in PassionNianShou.ToClassType() :
		if cf.rangeId not in NianShou_Reward_Random :
			NianShou_Reward_Random[cf.rangeId] = Random.RandomRate()
		NianShou_Reward_Random[cf.rangeId].AddRandomItem(cf.rate, cf.rewardId)
		NianShouReward[cf.rewardId] = cf


class PassionNianShouDrop(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionNianShouDrop.txt")
	def __init__(self):
		self.activityType = int
		self.fightIdx = int
		self.dropRate = int
		self.proCoding = int

def LoadPassionNianShouDrop():
	global NianShou_Item_Drop
	for cf in PassionNianShouDrop.ToClassType() :
		if (cf.activityType, cf.fightIdx) in NianShou_Item_Drop :
			print "GE_EXC, repeat activityType %s fightIdx %s is in NianShou_Item_Drop" % (cf.activityType, cf.fightIdx)
		NianShou_Item_Drop[(cf.activityType, cf.fightIdx)] = cf

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadPassionNianShou()
		LoadPassionNianShouDrop()