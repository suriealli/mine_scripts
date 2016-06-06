#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionConsumeRankConfig")
#===============================================================================
# 激情活动 -- 消费排名配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("PassionAct")
	
	PassionConsumeRank_Dict = {}			#本服排行榜奖励
	PassionConsumeRankReward_Dict = {}		#达标奖励
	PassionConsumeRankMinRMB = 0			#达标最少神石

class PassionConsumeRank(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionConsumeLocalRank.txt")
	def __init__(self):
		self.rank = int								#排名
		self.needRMB = int							#需要消费神石
		self.rewardItems = eval						#奖励

def LoadPassionConsumeRank():
	global PassionConsumeRank_Dict
	
	for PRR in PassionConsumeRank.ToClassType():
		if PRR.rank in PassionConsumeRank_Dict:
			print "GE_EXC, repeat rank(%s) in PassionConsumeRank_Dict" % PRR.rank
		PassionConsumeRank_Dict[PRR.rank] = PRR
	
class PassionConsumeRankReward(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionConsumeRankReward.txt")
	def __init__(self):
		self.needRMB = int
		self.rewardItems = eval

def LoadPassionConsumeRankReward():
	global PassionConsumeRankReward_Dict, PassionConsumeRankMinRMB
	
	for PRRR in PassionConsumeRankReward.ToClassType():
		if PRRR.needRMB in PassionConsumeRankReward_Dict:
			print "GE_EXC, repeat needRMB (%s) in PassionConsumeRankReward_Dict" % PRRR.needRMB
		PassionConsumeRankReward_Dict[PRRR.needRMB] = PRRR
		if PassionConsumeRankMinRMB:
			print 'GE_EXC, PassionConsumeRankConfig too more min rmb'
		PassionConsumeRankMinRMB = PRRR.needRMB
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadPassionConsumeRank()
		LoadPassionConsumeRankReward()
