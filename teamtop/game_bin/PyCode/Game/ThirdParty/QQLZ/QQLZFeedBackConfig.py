#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQLZ.QQLZHappyDrawConfig")
#===============================================================================
# 蓝钻转转乐配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile
from Util import Random
from Game.Role.Data import EnumObj,EnumInt8

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("QQLZ")

	QQLZ_FEEDBACK_ACT_CONTROL = None
	QQLZ_FEEDBACK_REWARD = {}
	QQLZ_FEEDBACK_REWARD_Group = {}

	GroupRandomObj = Random.RandomRate()

class QQLZFeedBackActControl(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("QQLZFeedBackActControl.txt")
	def __init__(self):
		self.activeTitle = str
		self.beginDate = self.GetDatetimeByString
		self.endDate = self.GetDatetimeByString

class QQLZFeedBackReward(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("QQLZFeedBackReward.txt")
	def __init__(self):
		self.rewardId = int
		self.isPrecious = int
		self.item = self.GetEvalByString
		self.rateValue = int

class QQLZFeedBackRewardGroup(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("QQLZFeedBackRewardGroup.txt")
	def __init__(self):
		self.index = int
		self.rewardGroup = self.GetEvalByString

def LoadQQLZFeedBackActControl():
	global QQLZ_FEEDBACK_ACT_CONTROL

	for cfg in QQLZFeedBackActControl.ToClassType():
		if QQLZ_FEEDBACK_ACT_CONTROL:
			print "GE_EXC, LoadQQLZFeedBackActControl already have data!"
		QQLZ_FEEDBACK_ACT_CONTROL = cfg

def LoadQQLZFeedBackReward():
	global QQLZ_FEEDBACK_REWARD

	for cfg in QQLZFeedBackReward.ToClassType():
		if cfg.rewardId in QQLZ_FEEDBACK_REWARD:
			print "GE_EXC, repeat rewardId(%s) in QQLZ_FEEDBACK_REWARD" % cfg.rewardId
		QQLZ_FEEDBACK_REWARD[cfg.rewardId] = cfg

def LoadQQLZFeedBackRewardGroup():
	global QQLZ_FEEDBACK_REWARD_Group,GroupRandomObj

	for cfg in QQLZFeedBackRewardGroup.ToClassType():
		if cfg.index in QQLZ_FEEDBACK_REWARD_Group:
			print "GE_EXC, repeat index(%s) in QQLZ_FEEDBACK_REWARD_Group" % cfg.index
		for rewardId in cfg.rewardGroup:
			if rewardId not in QQLZ_FEEDBACK_REWARD:
				print "GE_EXC, no rewardId(%s) in QQLZ_FEEDBACK_REWARD" % rewardId
		if len(cfg.rewardGroup) < 12:
			print "GE_EXC, reward group(%s) less than 12 items in QQLZ_FEEDBACK_REWARD_Group" % cfg.index
		QQLZ_FEEDBACK_REWARD_Group[cfg.index] = cfg
		GroupRandomObj.AddRandomItem(100,cfg.index)

def GetRandomGroup(groupId):
	'''
	随机一组不重复奖励组
	'''
	global QQLZ_FEEDBACK_REWARD_Group

	randomobj = Random.RandomRate()
	for index in QQLZ_FEEDBACK_REWARD_Group:
		if index != groupId:
			randomobj.AddRandomItem(100,index)

	return randomobj.RandomOne()

def GetRandomOne(role):
	'''
	除去已获取的奖励，从剩余中随机出一个奖励
	概率
	@param role:
	'''
	global QQLZ_FEEDBACK_REWARD_Group,QQLZ_FEEDBACK_REWARD

	#修正角色数据
	if role.GetI8(EnumInt8.QQLZFeedBackRewardGroup) not in QQLZ_FEEDBACK_REWARD_Group:
		role.SetI8(EnumInt8.QQLZFeedBackRewardGroup,1)
		role.SetObj(EnumObj.QQLZFeedBackData,{})

	#获取玩家已获得列表
	getedData = role.GetObj(EnumObj.QQLZFeedBackData)

	roleRewardId = role.GetI8(EnumInt8.QQLZFeedBackRewardGroup)

	NEW_RANDOM = Random.RandomRate()
	for rewardId in QQLZ_FEEDBACK_REWARD_Group[roleRewardId].rewardGroup:
		cfg = QQLZ_FEEDBACK_REWARD.get(rewardId,None)
		if not cfg:
			print "GE_EXC, no cfg in QQLZ_FEEDBACK_REWARD where index(%s)" % rewardId
		if cfg and rewardId not in getedData:
			NEW_RANDOM.AddRandomItem(cfg.rateValue, (cfg.rewardId, cfg.item))
	return NEW_RANDOM.RandomOne()

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadQQLZFeedBackActControl()
		LoadQQLZFeedBackReward()
		LoadQQLZFeedBackRewardGroup()