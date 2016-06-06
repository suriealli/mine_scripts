#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionGodTreeExchangeConfig")
#===============================================================================
# 国庆神树兑换配置	@author: GaoShuai
#===============================================================================
import DynamicPath
from Util.File import TabFile
import Environment

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("PassionAct")
	
	#激情有礼任务达成累计奖励配置
	GodTreeExchange_Dict = {}		#{rewardIndex:rewardItem,}


class PassionNationExchange(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("PassionGodTreeExchange.txt")
	def __init__(self):
		self.index = int
		self.minLevel = int
		self.needCoding = int
		self.needCnt = int
		self.items = self.GetEvalByString
		self.special = int
		self.limitCnt = int
		
def LoadPassionNationExchange():
	global NationalExchange_Dict
	for cfg in PassionNationExchange.ToClassType():
		if cfg.index in GodTreeExchange_Dict:
			print "GE_EXC,repeat item index(%s) in NationalExchange_Dict, PassionNationalExchange.txt" % cfg.index
		GodTreeExchange_Dict[cfg.index] = cfg
		
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadPassionNationExchange()
