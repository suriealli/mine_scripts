#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Item.MysteryBox.MysteryBoxConfig")
#===============================================================================
# 神秘宝箱 Config
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile
from Util import Random


if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("ItemConfig")
	
	#格式{boxCoding:cfg,}
	MYSTERYBOX_BASECONFIG_DICT = {}

class MysteryBox(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("MysteryBox.txt")
	def __init__(self):
		self.boxCoding = int
		self.boxName = str
		self.needLevel = int
		self.maxOpenCnt = int
		self.needRMBList = self.GetEvalByString
		self.rewardItems = self.GetEvalByString
		self.timeOutSeconds = int
	

def LoadMysteryBox():
	global MYSTERYBOX_BASECONFIG_DICT
	for cfg in MysteryBox.ToClassType():
		boxCoding = cfg.boxCoding
		maxOpenCnt = cfg.maxOpenCnt
		needRMBList = cfg.needRMBList
		if boxCoding in MYSTERYBOX_BASECONFIG_DICT:
			print "GE_EXC,repeat boxCoding(%s) in MYSTERYBOX_BASECONFIG_DICT" % boxCoding
		if len(needRMBList) < maxOpenCnt:
			print "GE_EXC, MysteryBox config error len(needRMBList) < maxOpenCnt,boxCoding(%s)" % boxCoding
		MYSTERYBOX_BASECONFIG_DICT[boxCoding] = cfg


def GetRandomObjByCodingAndData(boxCoding, stateSet):
	'''
	返回对应boxCoding在已经抽取了 stateSet 的情况下 的抽奖随机器
	@param boxCoding: 宝箱coding
	@param stateSet: 已抽取的idx集合
	'''
	if boxCoding not in MYSTERYBOX_BASECONFIG_DICT:
		return None
	
	randomObj = Random.RandomRate()
	boxCfg = MYSTERYBOX_BASECONFIG_DICT.get(boxCoding)
	for idx, coding, cnt, rateValue, isPrecious in boxCfg.rewardItems:
		if idx in stateSet:
			continue
		randomObj.AddRandomItem(rateValue, [idx, coding, cnt, isPrecious])
	
	return randomObj
		
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadMysteryBox()
