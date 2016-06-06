#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ValentineDay.GlamourRankConfig")
#===============================================================================
# 魅力排行 Config
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("ValentineDay")
	
	GlamourRank_MaxServerType = 0			#最大服务器类型
	GlamourRank_ServerType_Dict = {}		#服务器类型2开服天数 {serverType:cfg,}
	GlamourRank_LocalRankReward_Dict = {}	#本服排名奖励配置 {serverType:{rank:cfg,},}
	GlamourRank_ConsolationReward_Dict = {}	#安慰奖配置 {serverType:cfg,}

class GlamourRankServerType(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("GlamourRankServerType.txt")
	def __init__(self):
		self.serverType = int
		self.kaifuDay = self.GetEvalByString

def LoadGlamourRankServerType():
	global GlamourRank_ServerType_Dict
	for cfg in GlamourRankServerType.ToClassType():
		serverType = cfg.serverType
		if serverType in GlamourRank_ServerType_Dict: 
			print "GE_EXC, repeat serverType(%s) in GlamourRank_ServerType_Dict" % serverType
		GlamourRank_ServerType_Dict[serverType] = cfg


class GlamourLocalRank(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("GlamourLocalRank.txt")
	def __init__(self):
		self.serverType = int
		self.rank = int
		self.needGalmour = int
		self.rewardItems = self.GetEvalByString

def LoadGlamourLocalRank():
	global GlamourRank_MaxServerType
	global GlamourRank_LocalRankReward_Dict
	for cfg in GlamourLocalRank.ToClassType():
		serverType = cfg.serverType
		rank = cfg.rank
		serverTypeRewardDict = GlamourRank_LocalRankReward_Dict.setdefault(serverType, {})
		if rank in serverTypeRewardDict:
			print "GE_EXC, repeat rank(%s) in GlamourRank_LocalRankReward_Dict of serverType(%s) " % (rank, serverType)
		serverTypeRewardDict[rank] = cfg
		
		if serverType > GlamourRank_MaxServerType:
			GlamourRank_MaxServerType = serverType

class GlamourRankConsolationReward(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("GlamourRankConsolationReward.txt")
	def __init__(self):
		self.serverType = int 
		self.minGlamour = int
		self.needGlamour = int
		self.rewardItems = self.GetEvalByString

def LoadGlamourRankConsolationReward():
	global GlamourRank_ConsolationReward_Dict
	for cfg in GlamourRankConsolationReward.ToClassType():
		serverType = cfg.serverType
		if serverType in GlamourRank_ConsolationReward_Dict:
			print "GE_EXC, repeat serverType(%s) in GlamourRank_ConsolationReward_Dict" % serverType
		GlamourRank_ConsolationReward_Dict[serverType] = cfg

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadGlamourRankServerType()
		LoadGlamourLocalRank()
		LoadGlamourRankConsolationReward()