#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionTaoGuanConfig")
#===============================================================================
# 激情活动--欢乐砸陶罐配置
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("PassionAct")
	
	PassionTaoGuanConfigDict = {}


class PassionTaoGuan(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionTaoGuan.txt")
	def __init__(self):
		self.rewardTaoCi = eval
		self.levelRange = eval
		self.rewardItemList = eval
	
	def precoding(self):
		itemRandomRate = self.itemRandomRate = Random.RandomRate()
		for itemCoding, itemCnt, rate, isBroadcast in self.rewardItemList:
			itemRandomRate.AddRandomItem(rate, (itemCoding, itemCnt, isBroadcast))
		
		taociRandomRate = self.taociRandomRate = Random.RandomRate()
		for taociCoding, taociCnt, rate in self.rewardTaoCi:
			taociRandomRate.AddRandomItem(rate, (taociCoding, taociCnt))


def LoadPassionTaoGuan():
	global PassionTaoGuanConfigDict
	for config in PassionTaoGuan.ToClassType():
		config.precoding()
		startLevel, endlevel = config.levelRange
		for level in xrange(startLevel, endlevel + 1):
			if level in PassionTaoGuanConfigDict:
				print "GE_EXC,repeat level(%s) in PassionTaoGuanConfigDict" % level
			PassionTaoGuanConfigDict[level] = config


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadPassionTaoGuan()

