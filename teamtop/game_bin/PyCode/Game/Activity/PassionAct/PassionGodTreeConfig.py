#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionGodTreeConfig")
#===============================================================================
# 国庆神树探秘兑换配置	 @author: GaoShuai
#===============================================================================
import Environment
import DynamicPath
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("PassionAct")
	
	#激情有礼任务达成累计奖励配置
	GodTree_Dict = {}			#{等级区间: 该等级区间配置对象}
	random_Dict = {}			#{等级区间索引: 奖励随机对象}


class PassionGodTree(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("PassionGodTree.txt")
	def __init__(self):
		self.levelRangeId = int
		self.levelRange = self.GetEvalByString
		self.needCoding = int
		self.needRMB_Q = int
		
class PassionGodTreeReward(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("PassionGodTreeReward.txt")
	def __init__(self):
		self.index = int
		self.levelRangeId = int
		self.items = self.GetEvalByString
		self.percent = int
		self.special = int
		
def LoadPassionGodTree():
	global GodTree_Dict
	for cfg in PassionGodTree.ToClassType():
		if cfg.levelRangeId in GodTree_Dict:
			print "GE_EXC,repeat item index(%s) in GodTree_Dict, PassionGodTree.txt" % cfg.levelRange
		GodTree_Dict[cfg.levelRangeId] = cfg
		
def LoadPassionGodTreeReward():
	global GodTree_Reward_Dict
	global random_Dict
	levelRange_Set = GetlevelRange_Set()
	for levelRangeId in levelRange_Set:
		random_Dict[levelRangeId] = Random.RandomRate()
	
	for cfg in PassionGodTreeReward.ToClassType():
		if cfg.levelRangeId not in levelRange_Set:
			print "GE_EXC, levelRangeId(%s) not in levelRange_Set, check file PassionGodTreeReward.txt and PassionGodTree.txt please." % cfg.levelRangeId
		random_Dict[cfg.levelRangeId].AddRandomItem(cfg.percent, (cfg.items, cfg.special))
def GetlevelRange_Set():
	temp_Set = set()
	for _, item in GodTree_Dict.items():
		temp_Set.add(item.levelRangeId)
	return temp_Set
def Getindex(level):
	index = 0
	for level_tuple in GodTree_Reward_Dict.keys():
		if level_tuple[0] <= level <= level_tuple[1]:
			index = GodTree_Reward_Dict[level_tuple][0]
			break
	return index

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadPassionGodTree()
		LoadPassionGodTreeReward()
