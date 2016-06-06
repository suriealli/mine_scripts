#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.Game2048.Game2048Config")
#===============================================================================
# 注释 @author: GaoShuai 2015
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("2048Game")
	
	Game2048_Dict = {}
	Game2048BuyTimes_Dict = {}
	Game2048StepAndPoint_Dict = {}


class Game2048Config(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("2048Game.txt")
	def __init__(self):
		self.index = int				#跨服排名区间
		self.level = int				#跨服排名奖励
		self.goalIndex = int 			#第几个目标
		self.needIndex = self.GetEvalByString
		self.point = int
		self.maxStep = int
		self.goal = self.GetEvalByString
		self.nextIndex = int
		self.reward = self.GetEvalByString
		

class Game2048BuyTimesConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("2048BuyTimes.txt")
	def __init__(self):
		self.buyCnt = int				#跨服排名区间
		self.needRMB = int				#跨服排名奖励


class Game2048StepAndPointConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("2048StepAndPoint.txt")
	def __init__(self):
		self.index = int				#跨服排名区间
		self.leaveStep = int
		self.point = int				#跨服排名奖励


def LoadGame2048():
	global Game2048_Dict, Game2048StepAndPoint_Dict
	
	for cfg in Game2048Config.ToClassType():
		Game2048StepAndPoint_Dict[cfg.index] = {}
		if cfg.index in Game2048_Dict:
			print "GE_EXC, repeat index(%s) in Game2048_Dict" % cfg.index
		cfg.goal.append(0)
		Game2048_Dict[cfg.index] = cfg
	
	#载入每关积分数
	LoadGame2048StepAndPoint()


def LoadGame2048BuyTimes():
	global Game2048BuyTimes_Dict
	for cfg in Game2048BuyTimesConfig.ToClassType():
		if cfg.buyCnt in Game2048BuyTimes_Dict:
			print "GE_EXC, repeat buyCnt(%s) in Game2048BuyTimes_Dict" % cfg.buyCnt
		Game2048BuyTimes_Dict[cfg.buyCnt] = cfg.needRMB


def LoadGame2048StepAndPoint():
	#在函数LoadGame2048执行之后调用
	global Game2048StepAndPoint_Dict
	
	for cfg in Game2048StepAndPointConfig.ToClassType():
		if cfg.index not in Game2048StepAndPoint_Dict:
			print "GE_EXC, cannot find the index(%s) in Game2048StepAndPoint_Dict" % cfg.index
			continue
		if cfg.leaveStep in Game2048StepAndPoint_Dict[cfg.index]:
			print "GE_EXC, repeat leaveStep(%s) in Game2048StepAndPoint_Dict[%s]" % (cfg.leaveStep, cfg.index)
		Game2048StepAndPoint_Dict[cfg.index][cfg.leaveStep] = cfg.point


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadGame2048()
		LoadGame2048BuyTimes()
