#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.RMBFund.RMBFundConfig")
#===============================================================================
# 神石基金
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	RMBF_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	RMBF_FILE_FOLDER_PATH.AppendPath("RMBFund")
	
	RMBFund_Dict = {}
	RMBFund_List = []
	
	RMBPoint_Dict = {}
	RMBPoint_List = []
	
	RMBFundActive_Dict = {}
	
class RMBFundConfig(TabFile.TabLine):
	FilePath = RMBF_FILE_FOLDER_PATH.FilePath("RMBFundConfig.txt")
	def __init__(self):
		self.days = int		#天数
		self.rate = int		#利率
	
class RMBPointConfig(TabFile.TabLine):
	FilePath = RMBF_FILE_FOLDER_PATH.FilePath("RMBPointConfig.txt")
	def __init__(self):
		self.qPoint = int
		self.canBuyFund = int
	
class RMBFundActive(TabFile.TabLine):
	FilePath = RMBF_FILE_FOLDER_PATH.FilePath("RMBFundActive.txt")
	def __init__(self):
		self.index = int
		self.beginDay = int
		self.endDay = int
	
def LoadRMBFundActive():
	global RMBFundActive_Dict
	
	for RA in RMBFundActive.ToClassType():
		if RA.index in RMBFundActive_Dict:
			print "GE_EXC, repeat index (%s) in RMBFundActive_Dict" % RA.index
			continue
		RMBFundActive_Dict[(RA.beginDay, RA.endDay)] = RA.index
	
def LoadRMBFundConfig():
	global RMBFund_Dict
	
	for RF in RMBFundConfig.ToClassType():
		if RF.days in RMBFund_Dict:
			print "GE_EXC, repeat days (%s) in RMBFund_Dict" % RF.days
			continue
		RMBFund_Dict[RF.days] = RF
		RMBFund_List.append(RF.days)
	RMBFund_List.sort()
	
def LoadRMBPointConfig():
	global RMBPoint_Dict
	
	for RP in RMBPointConfig.ToClassType():
		if RP.qPoint in RMBPoint_Dict:
			print "GE_EXC, repeat qPoint (%s) in RMBPoint_Dict" % RP.qPoint
		RMBPoint_Dict[RP.qPoint] = RP.canBuyFund
		RMBPoint_List.append(RP.qPoint)
	RMBPoint_List.sort()
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadRMBFundConfig()
		LoadRMBPointConfig()
		LoadRMBFundActive()
		