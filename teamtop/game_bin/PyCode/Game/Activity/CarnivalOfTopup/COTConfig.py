#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.CarnivalOfTopup.COTConfig")
#===============================================================================
# 狂欢充值配置
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	RuneWheel_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	RuneWheel_FILE_FOLDER_PATH.AppendPath("CarnivalOfTopup")
	
	COTConfigDict = {}
	COTConfigRandomDict = {}
	COTItemLimitDict = {}


class COTConfig(TabFile.TabLine):
	'''
	狂欢充值配置
	'''
	FilePath = RuneWheel_FILE_FOLDER_PATH.FilePath("CarnivalOfTopup.txt")
	def __init__(self):
		self.activeID = int
		self.awardid = int
		self.awardrate = int
		self.awarditems = self.GetEvalByString
		self.addTarot = self.GetEvalByString
		self.talentcard = self.GetIntByString

class COTItemLimitConfig(TabFile.TabLine):
	'''
	狂欢奖品限制配置
	'''
	FilePath = RuneWheel_FILE_FOLDER_PATH.FilePath("COTItemLimit.txt")
	def __init__(self):
		self.awardid = int
		self.LimitCnt = int

def LoadCOTConfig():
	'''
	载入充值配置
	'''
	global COTConfigDict
	for config in COTConfig.ToClassType():
		if (config.activeID, config.awardid) in COTConfigDict:
			print "GE_EXC, repeat (config.activeID, config.awardid)(%s,%s) while LoadCOTConfig" % (config.activeID, config.awardid)
		COTConfigDict[(config.activeID, config.awardid)] = config
		
	global COTConfigRandomDict
	for (activeID, awardid), iconfig in COTConfigDict.iteritems():
		ratelist = COTConfigRandomDict.setdefault(activeID, [])
		ratelist.append((iconfig.awardrate, awardid))
		
def GetRandomOne(activeID, limitlist):
	RANDOM_ITEM = Random.RandomRate()
	#这里limitlist必须是列表
	if not isinstance(limitlist, list):
		print "GE_EXC, limitlist must be type<list> in CarnivalOfTopup.COTConfig"
		return
	ratelist = COTConfigRandomDict.get(activeID, None)
	if not ratelist:
		print "GE_EXC, error while ratelist = COTConfigRandomDict.get(activeID, None),no such activeID(%s)" % activeID
		return
	for rate, awardid in ratelist:
		if awardid in limitlist:
			continue
		RANDOM_ITEM.AddRandomItem(rate, awardid)
	return RANDOM_ITEM.RandomOne()
	
def LoadCOTItemLimitConfig():
	'''
	载入奖品限制配置
	'''
	global COTItemLimitDict
	for config in COTItemLimitConfig.ToClassType():
		if config.awardid in COTItemLimitDict:
			print "GE_EXC, repeat config.awardid(%s) while LoadCOTItemLimitConfig" % config.awardid
		COTItemLimitDict[config.awardid] = config.LimitCnt


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadCOTConfig()
		LoadCOTItemLimitConfig()
		

