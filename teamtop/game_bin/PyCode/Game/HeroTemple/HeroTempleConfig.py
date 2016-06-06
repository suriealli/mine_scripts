#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.HeroTemple.HeroTempleConfig")
#===============================================================================
# 英灵神殿配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Util import Random

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("HeroTemple")
	
	HeroTemple_Dict = {}
	HeroTempleCnt_Dict = {}
	HeroTemple_fcm_Dict = {}
	
		
class HeroTempleConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("HeroTemple.txt")
	def __init__(self):
		self.heroTempleIndex = int
		self.fightType = int
		self.mcid = int
		self.templeName = str
		self.stageId = int
		self.rewardMoney = int
		self.reward = eval
		self.rate = eval
		self.needLevel = int
		self.randomRewardCoding = int


class HeroTemple_fcmConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("HeroTemple.txt")
	def __init__(self):
		self.heroTempleIndex = int
		self.fightType = int
		self.mcid = int
		self.templeName = str
		self.stageId = int
		self.randomRewardCoding = int
		self.needLevel = int
		self.rewardMoney_fcm = int                    #奖励金币
		self.reward_fcm = self.GetEvalByString        #固定奖励
		self.rate_fcm = self.GetEvalByString          #[(个数, 概率)]


class HeroTempleCntConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("HeroTempleCnt.txt")
	def __init__(self):
		self.cnt = int
		self.needRMB = int
	
def LoadHeroTempleCntConfig():
	global HeroTempleCnt_Dict
	for HTC in HeroTempleCntConfig.ToClassType():
		if HTC.cnt in HeroTempleCnt_Dict:
			print "GE_EXC, repeat cnt (%s) in HeroTempleCnt_Dict" % HTC.cnt
			continue
		HeroTempleCnt_Dict[HTC.cnt] = HTC
	
def LoadHeroTempleConfig():
	global HeroTemple_Dict
	for HT in HeroTempleConfig.ToClassType():
		if HT.heroTempleIndex in HeroTemple_Dict:
			print "GE_EXC, repeat heroTempleIndex (%s) in HeroTemple_Dict" % HT.heroTempleIndex
			continue
		HeroTemple_Dict[HT.heroTempleIndex] = HT
		HT.flag = True
		if not HT.randomRewardCoding:
			continue
		HT.HT_RandomCnt = Random.RandomRate()
		for rate in HT.rate:
			HT.HT_RandomCnt.AddRandomItem(rate[1], rate[0])


def LoadHeroTemple_fcmConfig():
	global HeroTemple_fcm_Dict
	for HT in HeroTemple_fcmConfig.ToClassType():
		if HT.heroTempleIndex in HeroTemple_fcm_Dict:
			print "GE_EXC, repeat heroTempleIndex (%s) in HeroTemple_fcm_Dict" % HT.heroTempleIndex
			continue
		HeroTemple_fcm_Dict[HT.heroTempleIndex] = HT
		HT.flag = True
		HT.rewardMoney = HT.rewardMoney_fcm
		HT.reward = HT.reward_fcm
		if not HT.randomRewardCoding:
			continue
		HT.HT_RandomCnt = Random.RandomRate()
		for rate in HT.rate_fcm:
			HT.HT_RandomCnt.AddRandomItem(rate[1], rate[0])

if "_HasLoad" not in dir():
	if Environment.HasLogic and (not Environment.IsCross):
		LoadHeroTempleCntConfig()
		LoadHeroTempleConfig()
		LoadHeroTemple_fcmConfig()
	
