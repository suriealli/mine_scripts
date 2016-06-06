#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.QingMing.QingMingRankConfig")
#===============================================================================
# 清明消费排行榜
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("QingMing")
	
	QingMingRank_MaxServerType = 0			#最大服务器类型
	QingMingRank_ServerType_Dict = {}		#服务器类型2开服天数 {serverType:cfg,}
	QingMingRank_LocalRankReward_Dict = {}	#本服排名奖励配置 {serverType:{rank:cfg,},}
	QingMingRank_ConsolationReward_Dict = {}	#安慰奖配置 {serverType:cfg,}

class QingMingRankServerType(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("QingMingRankServerType.txt")
	def __init__(self):
		self.serverType = int
		self.kaifuDay = self.GetEvalByString

def LoadQingMingRankServerType():
	global QingMingRank_ServerType_Dict
	for cfg in QingMingRankServerType.ToClassType():
		serverType = cfg.serverType
		if serverType in QingMingRank_ServerType_Dict: 
			print "GE_EXC, repeat serverType(%s) in QingMingRank_ServerType_Dict" % serverType
		QingMingRank_ServerType_Dict[serverType] = cfg


class QingMingLocalRank(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("QingMingLocalRank.txt")
	def __init__(self):
		self.serverType = int
		self.rank = int
		self.needValue = int
		self.rewardItems = self.GetEvalByString

def LoadQingMingLocalRank():
	global QingMingRank_MaxServerType
	global QingMingRank_LocalRankReward_Dict
	for cfg in QingMingLocalRank.ToClassType():
		serverType = cfg.serverType
		rank = cfg.rank
		serverTypeRewardDict = QingMingRank_LocalRankReward_Dict.setdefault(serverType, {})
		if rank in serverTypeRewardDict:
			print "GE_EXC, repeat rank(%s) in QingMingRank_LocalRankReward_Dict of serverType(%s) " % (rank, serverType)
		serverTypeRewardDict[rank] = cfg
		
		if serverType > QingMingRank_MaxServerType:
			QingMingRank_MaxServerType = serverType

class QingMingRankConsolationReward(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("QingMingRankConsolationReward.txt")
	def __init__(self):
		self.serverType = int 
		self.minValue = int
		self.needValue = int
		self.rewardItems = self.GetEvalByString

def LoadQingMingRankConsolationReward():
	global QingMingRank_ConsolationReward_Dict
	for cfg in QingMingRankConsolationReward.ToClassType():
		serverType = cfg.serverType
		if serverType in QingMingRank_ConsolationReward_Dict:
			print "GE_EXC, repeat serverType(%s) in QingMingRank_ConsolationReward_Dict" % serverType
		QingMingRank_ConsolationReward_Dict[serverType] = cfg

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadQingMingRankServerType()
		LoadQingMingLocalRank()
		LoadQingMingRankConsolationReward()