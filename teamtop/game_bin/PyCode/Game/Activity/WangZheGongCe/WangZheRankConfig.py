#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.WangZheGongCe.WangZheRankConfig")
#===============================================================================
# 王者公测积分排行榜  config
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("WangZheGongCe")
	
	WangZheRank_MaxServerType = 0			#最大服务器类型
	WangZheRank_ServerType_Dict = {}		#服务器类型2开服天数 {serverType:cfg,}
	WangZheRank_LocalRankReward_Dict = {}	#本服排名奖励配置 {serverType:{rank:cfg,},}
	WangZheRank_ConsolationReward_Dict = {}	#安慰奖配置 {serverType:cfg,}

class WangZheRankServerType(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("WangZheRankServerType.txt")
	def __init__(self):
		self.serverType = int
		self.kaifuDay = self.GetEvalByString

def LoadWangZheRankServerType():
	global WangZheRank_ServerType_Dict
	for cfg in WangZheRankServerType.ToClassType():
		serverType = cfg.serverType
		if serverType in WangZheRank_ServerType_Dict: 
			print "GE_EXC, repeat serverType(%s) in WangZheRank_ServerType_Dict" % serverType
		WangZheRank_ServerType_Dict[serverType] = cfg


class WangZheLocalRank(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("WangZheLocalRank.txt")
	def __init__(self):
		self.serverType = int
		self.rank = int
		self.needJiFen = int
		self.rewardItems = self.GetEvalByString

def LoadWangZheLocalRank():
	global WangZheRank_MaxServerType
	global WangZheRank_LocalRankReward_Dict
	for cfg in WangZheLocalRank.ToClassType():
		serverType = cfg.serverType
		rank = cfg.rank
		serverTypeRewardDict = WangZheRank_LocalRankReward_Dict.setdefault(serverType, {})
		if rank in serverTypeRewardDict:
			print "GE_EXC, repeat rank(%s) in WangZheRank_LocalRankReward_Dict of serverType(%s) " % (rank, serverType)
		serverTypeRewardDict[rank] = cfg
		
		if serverType > WangZheRank_MaxServerType:
			WangZheRank_MaxServerType = serverType

class WangZheRankConsolationReward(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("WangZheRankConsolationReward.txt")
	def __init__(self):
		self.serverType = int 
		self.minJiFen = int
		self.needJiFen = int
		self.rewardItems = self.GetEvalByString

def LoadWangZheRankConsolationReward():
	global WangZheRank_ConsolationReward_Dict
	for cfg in WangZheRankConsolationReward.ToClassType():
		serverType = cfg.serverType
		if serverType in WangZheRank_ConsolationReward_Dict:
			print "GE_EXC, repeat serverType(%s) in WangZheRank_ConsolationReward_Dict" % serverType
		WangZheRank_ConsolationReward_Dict[serverType] = cfg

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadWangZheRankServerType()
		LoadWangZheLocalRank()
		LoadWangZheRankConsolationReward()