#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionChristmasExchangeConfig")
#===============================================================================
# 圣诞大兑换 @author: GaoShuai 2015
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("PassionAct")
	ChristmasExchange_Dict = {}

class PassionChristmasExchange(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionChristmasExchange.txt")
	def __init__(self):
		self.index = int						#索引
		self.RMB_Q = int						#需要充值神石
		self.needItems = self.GetEvalByString		#需要道具
		self.dayLimit = int						#每日限购
		self.allLimit = int						#活动限购
		self.rewards = self.GetEvalByString		#道具奖励
		self.RMB = int							#奖励神石奖励
		self.Money = int						#金币奖励
		self.MoJing = int						#魔晶奖励


def LoadPassionChristmasExchange():
	global ChristmasExchange_Dict
	
	for cfg in PassionChristmasExchange.ToClassType():
		cntFlag = 0
		if cfg.rewards:
			cntFlag += 1
		if cfg.RMB:
			cntFlag += 1
		if cfg.Money:
			cntFlag += 1
		if cfg.MoJing:
			cntFlag += 1
		
		if cntFlag != 1:
			print "GE_EXC, repeat reward in ChristmasExchange_Dict, where index = %s" % cfg.index
			
		if cfg.index in ChristmasExchange_Dict:
			print "GE_EXC, repeat index(%s) in ChristmasExchange_Dict" % cfg.index
		ChristmasExchange_Dict[cfg.index] = cfg


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadPassionChristmasExchange()
