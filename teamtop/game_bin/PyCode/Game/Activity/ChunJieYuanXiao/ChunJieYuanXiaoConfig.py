#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ChunJieYuanXiao.ChunJieYuanXiaoConfig")
#===============================================================================
# 元宵花灯配置表
#===============================================================================

import Environment
import DynamicPath
from Util.File import TabFile
from Util import Random
if "_HasLoad" not in dir():
	NYD_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	NYD_FILE_FOLDER_PATH.AppendPath("ChunJieYuanXiao")
	YuanXiaoHeroDict = {}			#事件字典
	YuanXiaoHeigtAwardDict = {}		#奖励字典
	YuanXiaoBuyHuaDeng = {}			#购买花灯字典
	YuanXiaoHeightRandom = {}			#抽奖机


class ChunJieYuanXiaoAward(TabFile.TabLine):
	FilePath = NYD_FILE_FOLDER_PATH.FilePath("PassionYuanXiaoAward.txt")
	def __init__(self):
		self.AwaIndex = int
		self.Level = self.GetEvalByString
		self.Height = self.GetEvalByString
		self.Reward = self.GetEvalByString

def LoadYuanXiaoAward():
	global YuanXiaoHeigtAwardDict
	for cf in ChunJieYuanXiaoAward.ToClassType():
		if cf.AwaIndex in YuanXiaoHeigtAwardDict :
			print "GE_EXC, repeat AwaIndex %s is in YuanXiaoHeigtAwardDict" % cf.AwaIndex
		YuanXiaoHeigtAwardDict[cf.AwaIndex] = cf
	

def LoadYuanXiaoRandom():
	global YuanXiaoHeightRandom
	for cf in ChunJieYuanXiaoAward.ToClassType():
		if cf.AwaIndex not in YuanXiaoHeightRandom :
			YuanXiaoHeightRandom[cf.AwaIndex] = Random.RandomRate()
		for ItemsCoding,_2,rate in cf.Reward :
			YuanXiaoHeightRandom[cf.AwaIndex].AddRandomItem(rate,ItemsCoding)

class ChunJieYuanXiaoBuyHuaDeng(TabFile.TabLine):
	FilePath = NYD_FILE_FOLDER_PATH.FilePath("PassionYuanXiaoBuyHuaDeng.txt")
	def __init__(self):
		self.BuyIndex = int
		self.CostRmb = int
		self.Award = int
	

def LoadChunJieYuanXiaoBuyHuaDeng():
	global YuanXiaoBuyHuaDeng
	for cf in ChunJieYuanXiaoBuyHuaDeng.ToClassType():
		if cf.BuyIndex in YuanXiaoBuyHuaDeng :
			print "GE_EXC, repeat BuyIndex %s is in YuanXiaoBuyHuaDeng" % cf.BuyIndex
		YuanXiaoBuyHuaDeng[cf.BuyIndex] = cf
	

class ChunJieYuanXiaoHero(TabFile.TabLine):
	FilePath = NYD_FILE_FOLDER_PATH.FilePath("PassionYuanXiaoHero.txt")
	def __init__(self):
		self.HeroId = int
		self.HeroGrade = int
		self.HeroAttribute = int
		self.IncHit = int
		self.IncHitRate = int
		self.IncNormalRate = int
		self.IncSpecialRate = int
		self.Rate = int
		
	
def LoadChunJieYuanXiaoHero():
	global YuanXiaoHeroDict
	for cf in ChunJieYuanXiaoHero.ToClassType():
		if cf.HeroId in YuanXiaoHeroDict :
			print "GE_EXC, repeat HeroId %s is in YuanXiaoHeroDict" % cf.HeroId
		YuanXiaoHeroDict[(cf.HeroId, cf.HeroGrade)] = cf

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadYuanXiaoAward()
		LoadChunJieYuanXiaoBuyHuaDeng()
		LoadChunJieYuanXiaoHero()
		LoadYuanXiaoRandom()