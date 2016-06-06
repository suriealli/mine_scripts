#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DoubleEleven.DEGroupBuyConfig")
#===============================================================================
# 双十一2015 团购送神石 config
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLod" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("DoubleEleven")
	
	CIRCULAR_FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	CIRCULAR_FILE_FLODER_PATH.AppendPath("CircularActive")
	
	#团购送神石基本配置 ｛dayIndex:cfg,｝
	DEGroupBuy_BaseConfig_Dict = {} 
	#活动时间控制配置
	DEGroupBuyActive_cfg = None


class DEGroupBuy(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("DEGroupBuy.txt")
	def __init__(self):
		self.dayIndex = int
		self.goodsItem = self.GetEvalByString
		self.needUnbindRMB = int
		self.rebateItems1 = self.GetEvalByString
		self.unlockCnt1 = int
		self.rebateItems2 = self.GetEvalByString
		self.unlockCnt2 = int
		self.rebateItems3 = self.GetEvalByString
		self.unlockCnt3 = int
		self.rebateItems4 = self.GetEvalByString
		self.unlockCnt4 = int
		self.rebateItems5 = self.GetEvalByString
		self.unlockCnt5 = int
		self.rebateItems6 = self.GetEvalByString
		self.unlockCnt6 = int
		self.rebateItems7 = self.GetEvalByString
		self.unlockCnt7 = int
	
	def pre_process(self):
		self.UnlockRewardList = []
		self.UnlockRewardList.append((self.unlockCnt1, self.rebateItems1))
		self.UnlockRewardList.append((self.unlockCnt2, self.rebateItems2))
		self.UnlockRewardList.append((self.unlockCnt3, self.rebateItems3))
		self.UnlockRewardList.append((self.unlockCnt4, self.rebateItems4))
		self.UnlockRewardList.append((self.unlockCnt5, self.rebateItems5))
		self.UnlockRewardList.append((self.unlockCnt6, self.rebateItems6))
		self.UnlockRewardList.append((self.unlockCnt7, self.rebateItems7))
		

def LoadDEGroupBuy():
	global DEGroupBuy_BaseConfig_Dict
	for cfg in DEGroupBuy.ToClassType():
		dayIndex = cfg.dayIndex
		if dayIndex in DEGroupBuy_BaseConfig_Dict:
			print "GE_EXC,repeat dayIndex(%s) in DEGroupBuy_BaseConfig_Dict" % dayIndex
		cfg.pre_process()
		DEGroupBuy_BaseConfig_Dict[dayIndex] = cfg
		

def GetCfgByDayIndex(dayIndex):
	'''
	返回天数 dayIndex 对应的 配置
	'''
	tCfg = None
	if dayIndex in DEGroupBuy_BaseConfig_Dict:
		tCfg = DEGroupBuy_BaseConfig_Dict[dayIndex]
	
	return tCfg

	
class DEGroupBuyActive(TabFile.TabLine):
	FilePath = CIRCULAR_FILE_FLODER_PATH.FilePath("DEGroupBuyActive.txt")
	def __init__(self):
		self.activeIndex = int
		self.activeName = str
		self.beginTime = self.GetDatetimeByString
		self.endTime = self.GetDatetimeByString
		self.totalDay = int
	
def LoadDEGroupBuyActive():
	'''
	加载并启动活动
	'''
	global DEGroupBuyActive_cfg
	for cfg in DEGroupBuyActive.ToClassType():
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in DEGroupBuyActive_cfg"
			continue
		DEGroupBuyActive_cfg = cfg
			

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadDEGroupBuy()
		LoadDEGroupBuyActive()
