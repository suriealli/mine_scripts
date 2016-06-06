#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Flower.FlowerConfig")
#===============================================================================
# 鲜花系统配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("Flower")
	
	Flower_Dict = {}
	FlowerCntSet = set()
	FlowerLocalRank_Dict = {}
	
	KuafuFlowerRankServerType_Dict = {}
	
class FlowerConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("Flower.txt")
	def __init__(self):
		self.flowerCnt = int			#鲜花数
		self.meili = int				#魅力
		self.qinmi = int				#亲密
		self.needItemCoding = int		#道具id
		self.isRumor = int				#是否喇叭公告
		
def LoadFlowerConfig():
	global Flower_Dict, FlowerCntSet
	
	for fc in FlowerConfig.ToClassType():
		if fc.flowerCnt in Flower_Dict:
			print 'GE_EXC, repeat flowerCnt %s in Flower_Dict' % fc.flowerCnt
		Flower_Dict[fc.flowerCnt] = fc
		FlowerCntSet.add(fc.flowerCnt)
	
class KuafuFlowerRankServerTypeConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("KuafuFlowerRankServerType.txt")
	def __init__(self):
		self.serverType = int						#服务器类型
		self.kaifuDay = eval						#开服天数区间
	
def LoadKuafuFlowerRankServerTypeConfig():
	global KuafuFlowerRankServerType_Dict
	
	for KFR in KuafuFlowerRankServerTypeConfig.ToClassType():
		if KFR.serverType in KuafuFlowerRankServerType_Dict:
			print "GE_EXC, repeat serverType (%s) in KuafuFlowerRankServerType_Dict" % KFR.serverType
			continue
		KuafuFlowerRankServerType_Dict[KFR.serverType] = KFR
	
class LocalFlowerRankConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("LocalFlowerRank.txt")
	def __init__(self):
		self.sex = int						#性别
		self.rankInterval = eval			#排名区间
		self.reward = eval					#奖励道具
		
def LoadLocalFlowerRankConfig():
	global FlowerLocalRank_Dict
	
	for LFR in LocalFlowerRankConfig.ToClassType():
		if LFR.sex not in FlowerLocalRank_Dict:
			FlowerLocalRank_Dict[LFR.sex] = {}
		if LFR.rankInterval in FlowerLocalRank_Dict[LFR.sex]:
			print 'GE_EXC, repeat rankInterval %s in FlowerLocalRank_Dict[LFR.sex]' % LFR.rankInterval
		FlowerLocalRank_Dict[LFR.sex][LFR.rankInterval] = LFR.reward
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadFlowerConfig()
		LoadKuafuFlowerRankServerTypeConfig()
		LoadLocalFlowerRankConfig()
		
