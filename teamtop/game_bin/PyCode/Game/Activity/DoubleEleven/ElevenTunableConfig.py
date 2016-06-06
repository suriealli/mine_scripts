#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DoubleEleven.ElevenTunableConfig")
#===============================================================================
# 双十一转盘配置  @author GaoShuai 2015
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("DoubleEleven")
	
	ElevenTutable_Dict = {}

class ElevenTunableConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("ElevenTutable.txt")
	def __init__(self):
		self.levelRange = self.GetEvalByString		#等级区间
		self.items = self.GetEvalByString			#轮盘物品配置
		self.needKeys = self.GetEvalByString		#需要物品道具
		
def LoadElevenTunableConfig():
	global ElevenTutable_Dict
	
	for cfg in ElevenTunableConfig.ToClassType():
		minLevel, maxLevel = cfg.levelRange
		RandomRate = Random.RandomRate()
		for (index, item, cnt, percent, special) in cfg.items:
			RandomRate.AddRandomItem(percent, (index, item, cnt, special))
		for level in range(minLevel, maxLevel + 1):
			if level in ElevenTutable_Dict:
				print "GE_EXC, repeat index(%s) in ElevenTutable_Dict" % level				
			ElevenTutable_Dict[level] = (RandomRate, cfg.needKeys)
		
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadElevenTunableConfig()
