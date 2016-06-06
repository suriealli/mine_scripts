#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionRechargeRankConfig")
#===============================================================================
# 激情活动 -- 充值排名配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("PassionAct")
	
	PassionRechargeRank_Dict = {}			#本服排行榜奖励
	PassionRechargeRankReward_Dict = {}		#达标奖励
	PassionRechargeRankMinRMB = 0			#达标最少神石

class PassionRechargeRank(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionRechargeLocalRank.txt")
	def __init__(self):
		self.rank = int								#排名
		self.needRMB = int							#需要充值神石
		self.rewardItems = eval						#奖励

def LoadPassionRechargeRank():
	global PassionRechargeRank_Dict
	
	for PRR in PassionRechargeRank.ToClassType():
		if PRR.rank in PassionRechargeRank_Dict:
			print "GE_EXC, repeat rank(%s) in PassionRechargeRank_Dict" % PRR.rank
		PassionRechargeRank_Dict[PRR.rank] = PRR
	
class PassionRechargeRankReward(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionRechargeRankReward.txt")
	def __init__(self):
		self.needRMB = int
		self.rewardItems = eval

def LoadPassionRechargeRankReward():
	global PassionRechargeRankReward_Dict, PassionRechargeRankMinRMB
	
	for PRRR in PassionRechargeRankReward.ToClassType():
		if PRRR.needRMB in PassionRechargeRankReward_Dict:
			print "GE_EXC, repeat needRMB (%s) in PassionRechargeRankReward_Dict" % PRRR.needRMB
		PassionRechargeRankReward_Dict[PRRR.needRMB] = PRRR
		if PassionRechargeRankMinRMB:
			print 'GE_EXC, PassionRechargeRankConfig too more min rmb'
		PassionRechargeRankMinRMB = PRRR.needRMB
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadPassionRechargeRank()
		LoadPassionRechargeRankReward()
