#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.HeroShengdian.HeroShengdianConfig")
#===============================================================================
# 英雄圣殿配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Util import Random

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("HeroShengdian")
	
	HeroShengdian_Dict = {}
	HeroShengdianCnt_Dict = {}
	
class HeroShengdianConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("HeroShengdian.txt")
	def __init__(self):
		self.heroShengdianIndex = int
		self.fightType = int
		self.mcid = int
		self.reward = eval
		self.randomRewardCoding = int
		self.rate = eval
		self.shengdianName = str
		self.stageId = int
		self.needLevel = int
		
class HeroShengdianCntConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("HeroShenddianCnt.txt")
	def __init__(self):
		self.cnt = int
		self.needUnbindRMB = int
	
def LoadHeroShengdianCntConfig():
	global HeroShengdianCnt_Dict
	for HSC in HeroShengdianCntConfig.ToClassType():
		if HSC.cnt in HeroShengdianCnt_Dict:
			print "GE_EXC, repeat cnt (%s) in HeroShengdianCnt_Dict" % HSC.cnt
			continue
		HeroShengdianCnt_Dict[HSC.cnt] = HSC
	
def LoadHeroShengdianConfig():
	global HeroShengdian_Dict
	for HSI in HeroShengdianConfig.ToClassType():
		if HSI.heroShengdianIndex in HeroShengdian_Dict:
			print "GE_EXC, repeat heroShengdianIndex (%s) in HeroShengdian_Dict" % HSI.heroShengdianIndex
			continue
		HeroShengdian_Dict[HSI.heroShengdianIndex] = HSI
		
		if not HSI.randomRewardCoding:
			continue
		HSI.HSI_RandomCnt = Random.RandomRate()
		for rate in HSI.rate:
			HSI.HSI_RandomCnt.AddRandomItem(rate[1], rate[0])
		
if "_HasLoad" not in dir():
	if Environment.HasLogic and (not Environment.IsCross):
		LoadHeroShengdianConfig()
		LoadHeroShengdianCntConfig()
