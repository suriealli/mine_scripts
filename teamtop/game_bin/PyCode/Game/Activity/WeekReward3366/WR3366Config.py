#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.WeekReward3366.WR3366Config")
#===============================================================================
# 3366 一周豪礼
#===============================================================================
from Util.File import TabFile
import Environment
import DynamicPath
from Game.Role.Data import EnumInt8

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("WeekReward3366")
	
	WEEK_REWARD_3366_CCONFIG_DICT = {}		#3366活动配置{activeID:cfg}
	WEEK_REWARD_3366_REWARDS_DICT = {}		#3366一周豪礼奖励配置{rewardID:cfg}
	WEEK_REWARD_3366_REWARDID_LIST = []		#3366一周豪礼奖励ID顺序列表[rewardID1,rewardID2,]

class WR3366Control(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("WR3366Control.txt")
	def __init__(self):
		self.activeID 		= int 	#活动ID
		self.beginDate 		= eval 	#活动开始日期
		self.endDate 		= eval 	#活动结束日期

class WR3366Rewards(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("WR3366Rewards.txt")
	def __init__(self):
		self.rewardID	= int 	#奖励ID
		self.day		= int 	#奖励对应登陆天数
		self.items		= eval	#奖励物品
		self.money		= int 	#奖励金币
		self.bindRMB	= int 	#奖励魔晶

def LoadWR3366Control():
	global WEEK_REWARD_3366_CCONFIG_DICT
	for cfg in WR3366Control.ToClassType():
		if cfg.activeID != 1:
			print "GE_EXC,error activeID(%s)" % cfg.activeID
			continue
		
		if cfg.activeID in WEEK_REWARD_3366_CCONFIG_DICT:
			print "GE_EXC,repeat activeID(%s) in WEEK_REWARD_3366_CCONFIG_DICT" % cfg.activeID
		WEEK_REWARD_3366_CCONFIG_DICT[cfg.activeID] = cfg
	
	if len(WEEK_REWARD_3366_CCONFIG_DICT) != 1:
		print "GE_EXC, config error! len(WEEK_REWARD_3366_CCONFIG_DICT)(%s) != 1" % len(WEEK_REWARD_3366_CCONFIG_DICT)

def LoadWR3366Rewards():
	global WEEK_REWARD_3366_REWARDS_DICT
	global WEEK_REWARD_3366_REWARDID_LIST
	for cfg in WR3366Rewards.ToClassType():
		if cfg.rewardID in WEEK_REWARD_3366_REWARDS_DICT:
			print "GE_EXC,repeat rewardID(%s) in WEEK_REWARD_3366_REWARDS_DICT" % cfg.rewardID
		WEEK_REWARD_3366_REWARDS_DICT[cfg.rewardID] = cfg
		WEEK_REWARD_3366_REWARDID_LIST.append(cfg.rewardID)
	
	WEEK_REWARD_3366_REWARDID_LIST.sort()
		
def GetNextReward(role):
	'''
	获取玩家下一个可领取3366一周豪礼奖励cfg
	@param role:
	@return: None or WR3366Rewards中的某一项 若已经全部领取 返回None
	'''
	WR3366_RewardRecord = role.GetI8(EnumInt8.WR3366_RewardRecord)
	for rewardID in WEEK_REWARD_3366_REWARDID_LIST:
		if WR3366_RewardRecord & rewardID:
			continue
		return WEEK_REWARD_3366_REWARDS_DICT.get(rewardID)
	return None

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadWR3366Control()
		LoadWR3366Rewards()