#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.RMBBank.RMBBankConfig")
#===============================================================================
# 神石银行
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	RMBB_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	RMBB_FILE_FOLDER_PATH.AppendPath("RMBBank")
	
	RMBBankGrade_Dict = {}
	RMBBankRate_Dict = {}
	
class RMBBankGradeConfig(TabFile.TabLine):
	FilePath = RMBB_FILE_FOLDER_PATH.FilePath("RMBBankGradeConfig.txt")
	def __init__(self):
		self.index = int				#档次索引
		self.RMB_Q = int				#Q点神石
	
class RMBBankRateConfig(TabFile.TabLine):
	FilePath = RMBB_FILE_FOLDER_PATH.FilePath("RMBBankRateConfig.txt")
	def __init__(self):
		self.index = int				
		self.needLevel = int					#需要等级
		self.returnUnbindRMBRates = int			#返还神石百分比
		self.returnBindRMBRates = int			#返还魔晶百分比
	
def LoadRMBBankGradeConfig():
	global RMBBankGrade_Dict
	
	for RA in RMBBankGradeConfig.ToClassType():
		if RA.index in RMBBankGrade_Dict:
			print "GE_EXC, repeat index (%s) in RMBBankGrade_Dict" % RA.index
			continue
		RMBBankGrade_Dict[RA.index] = RA
	
def LoadRMBBankRateConfig():
	global RMBBankRate_Dict
	
	for RA in RMBBankRateConfig.ToClassType():
		if RA.index in RMBBankRate_Dict:
			print "GE_EXC, repeat index (%s) in RMBBankRate_Dict" % RA.index
			continue
		RMBBankRate_Dict[RA.index] = RA
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadRMBBankGradeConfig()
		LoadRMBBankRateConfig()
		