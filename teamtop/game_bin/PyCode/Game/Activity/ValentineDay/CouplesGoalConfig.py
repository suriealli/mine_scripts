#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ValentineDay.CouplesGoalConfig")
#===============================================================================
# 情人目标 Config
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("ValentineDay")
	
	CouplesGoal_GoalConfig_Dict = {}		#情人目标配置 {goalType:{goalID:cfg,},}
	CouplesGoal_GoalID2Cfg_Dict = {}		#情人目标基本配置 {goalId:cfg,}

class CouplesGoal(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("CouplesGoal.txt")
	def __init__(self):
		self.goalID = int
		self.goalType = int
		self.needValue = int
		self.rewardItems = self.GetEvalByString
		self.needDayClear = int

def LoadCouplesGoal():
	global CouplesGoal_GoalConfig_Dict
	global CouplesGoal_GoalID2Cfg_Dict
	for cfg in CouplesGoal.ToClassType():
		goalID = cfg.goalID
		goalType = cfg.goalType
		
		if goalID in CouplesGoal_GoalID2Cfg_Dict:
			print "GE_EXC,repeat goalID(%s) in CouplesGoal_GoalID2Cfg_Dict" % goalID
		CouplesGoal_GoalID2Cfg_Dict[goalID] = cfg
		
		goalTypeCfgDict = CouplesGoal_GoalConfig_Dict.setdefault(goalType, {})
		if goalID in goalTypeCfgDict:
			print "GE_EXC,repeat goalID(%s) in goalTypeCfgDict" % goalID
		goalTypeCfgDict[goalID] = cfg

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadCouplesGoal()