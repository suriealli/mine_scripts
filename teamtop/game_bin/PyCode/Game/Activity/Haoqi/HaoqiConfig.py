#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.Haoqi.HaoqiConfig")
#===============================================================================
# 豪气冲天配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	HQFILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	HQFILE_FOLDER_PATH.AppendPath("Haoqi")
	
	HaoqiRMBReward_Dict = {}		#充值奖励
	HaoqiLocalRank_Dict = {}		#本地排行榜奖励
	
class HaoqiLocalRankConfig(TabFile.TabLine):
	FilePath = HQFILE_FOLDER_PATH.FilePath("HaoqiLocalRank.txt")
	def __init__(self):
		self.rank = int
		self.rewardItems = eval
		self.money = int
		self.bindRMB = int
	
class HaoqiRMBRewardConfig(TabFile.TabLine):
	FilePath = HQFILE_FOLDER_PATH.FilePath("HaoqiRMBReward.txt")
	def __init__(self):
		self.index = int
		self.rewardItems = eval
	
def LoadHaoqiRMBRewardConfig():
	global HaoqiRMBReward_Dict
	
	for HRD in HaoqiRMBRewardConfig.ToClassType():
		if HRD.index in HaoqiRMBReward_Dict:
			print 'GE_EXC, repeat index : %s in HaoqiRMBReward_Dict' % HRD.index
			continue
		HaoqiRMBReward_Dict[HRD.index] = HRD
	
def LoadHaoqiRankConfig():
	global HaoqiLocalRank_Dict
	
	for HLRC in HaoqiLocalRankConfig.ToClassType():
		if HLRC.rank in HaoqiLocalRank_Dict:
			print "GE_EXC, repeat rank : %s in HaoqiLocalRank_Dict" % HLRC.rank
			continue
		HaoqiLocalRank_Dict[HLRC.rank] = HLRC

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadHaoqiRankConfig()
		LoadHaoqiRMBRewardConfig()
	