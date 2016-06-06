#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.TimeLimitSupply.TLSConfig")
#===============================================================================
# 限时特供
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("TimeLimitSupply")
	
	TimeLimitSupply_Dict = {}
	TimeLimitConfig_Dict = {}
	
class TimeLimitSupplyConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath('TimeLimitSupply.txt')
	def __init__(self):
		self.number = int							#编号
		self.actType = int							#活动类型
		self.param = int							#活动参数	
		self.rewardItem = eval						#奖励物品

def LoadTimeLimitSupplyConfig():
	global TimeLimitSupply_Dict
	
	for TLS in TimeLimitSupplyConfig.ToClassType():
		if TLS.number in TimeLimitSupply_Dict:
			print 'GE_EXC, repeat number %s in TimeLimitSupply_Dict' % TLS.number
			continue
		TimeLimitSupply_Dict[TLS.number] = TLS

class TimeLimitConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath('TimeLimitConfig.txt')
	def __init__(self):
		self.actId = int							#活动ID
		self.actList = eval							#要开启的活动ID列表(按先后顺序)
		
def LoadTimeLimitConfig():
	global TimeLimitConfig_Dict
	
	for TLC in TimeLimitConfig.ToClassType():
		if TLC.actId in TimeLimitConfig_Dict:
			print 'GE_EXC, repeat actId %s in TimeLimitConfig_Dict' % TLC.actId
			continue
		TimeLimitConfig_Dict[TLC.actId] = TLC
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadTimeLimitSupplyConfig()
		LoadTimeLimitConfig()
	