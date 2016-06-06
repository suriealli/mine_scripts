#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Tarot.TarotConfig")
#===============================================================================
# 占卜配置
#===============================================================================
import random
import Environment
import DynamicPath
from Util.File import TabFile
from Util import Random
from Common.Other import EnumGameConfig



if "_HasLoad" not in dir():
	TAROT_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	TAROT_FILE_FOLDER_PATH.AppendPath("Tarot")
	
	#占卜配置
	Tarot_ZhanBu_Config_Dict = {}
	#塔罗牌配置
	TarotCardConfig_Dict = {}
	#卡品阶对应类型列表字典配置
	TarotCardGrade_Dict = {}
	#60级以下随机的卡品阶对应类型列表字典配置
	TarotCardGrade_Dict_60 = {}
	
	#品阶，等级对应经验
	TarotCardGradeLevelExp_Dict = {}
	#升级经验配置
	TarotCardLevelUpExp_Dict = {}
	
	#兑换商店
	TarotShop_Config_Dict = {}
	#等级开启可装备格子配置
	TarotLevelOpenSizeConfig_Dict = {}
	
	#占卜光环升级经验配置
	TarotRingLevelExp_Dict = {}
	#占卜光环等级加成配置
	TarotRingConfig_Dict = {}
	#高级占卜
	TarotActiveRMB_Confg = Random.RandomRate()
	TarotActiveRMB_Confg_Level_60 = Random.RandomRate()
##################################################################################

def TarotActiveRMB(roleLevel):
	#高级占卜随机类型
	if roleLevel < 60:
		return random.choice(TarotActiveRMB_Confg_Level_60.RandomOne())
	return random.choice(TarotActiveRMB_Confg.RandomOne())


#塔罗玩法配置
class TarotConfig(TabFile.TabLine):
	FilePath = TAROT_FILE_FOLDER_PATH.FilePath("Tarot.txt")
	def __init__(self):
		self.zIndex = int
		self.name = str
		self.next_rate = int
		self.needMoney = int
		self.grade_rate = self.GetEvalByString
		
	def Preprocess(self):
		#初始化随机塔罗牌组
		self.randomGrade = Random.RandomRate()
		self.randomGrade_level_60 = Random.RandomRate()
		for grade, rate in self.grade_rate:
			self.randomGrade.AddRandomItem(rate, TarotCardGrade_Dict.get(grade))
			self.randomGrade_level_60.AddRandomItem(rate, TarotCardGrade_Dict_60.get(grade))

	def RandomCardType(self, roleLevel):
		#随机一个卡类型
		if roleLevel < 60:
			return random.choice(self.randomGrade_level_60.RandomOne())
		return random.choice(self.randomGrade.RandomOne())
	
	def RandomNextIndex(self):
		#随机下一个类型
		if random.randint(1, 10000) < self.next_rate:
			return self.zIndex + 1
		else:
			return 1
	


class TarotCardConfig(TabFile.TabLine):
	FilePath = TAROT_FILE_FOLDER_PATH.FilePath("TarotCard.txt")
	def __init__(self):
		self.tType = int
		self.name = str
		self.grade = int
		self.level_60 = int
		self.isLog = int
		self.canRing = int
		self.canEquitment = int
		self.canMix = int
		self.canBeMix = int
		self.oneKeyMix = int
		self.sellMoney = int#出售价格
		self.sellHp = int#出售命力
		self.baseExp = int
		self.pt = int
		self.pv = self.GetEvalByString
		self.pt2 = int
		self.pv2 = self.GetEvalByString



class CardLevelExpConfig(TabFile.TabLine):
	FilePath = TAROT_FILE_FOLDER_PATH.FilePath("CardLevelExp.txt")
	def __init__(self):
		self.cardGrade = int
		self.level = int
		self.levelUpExp = int
		self.eatLevelExp = int


class TarotLevelOpenSizeConfig(TabFile.TabLine):
	FilePath = TAROT_FILE_FOLDER_PATH.FilePath("LevelOpenPackage.txt")
	def __init__(self):
		self.level = int
		self.openSize = int


class TarotShopConfig(TabFile.TabLine):
	FilePath = TAROT_FILE_FOLDER_PATH.FilePath("TarotShop.txt")
	def __init__(self):
		self.card_Type = int
		self.name = str
		self.needTarotHP = int
		self.needLevel = int



#占卜光环
class TarotRingConfig(TabFile.TabLine):
	FilePath = TAROT_FILE_FOLDER_PATH.FilePath("TarotRing.txt")
	def __init__(self):
		self.ringLevel = int
		self.ringExp = int
		self.grade4 = self.GetEvalByString
		self.grade5 = self.GetEvalByString
		self.grade6 = self.GetEvalByString

	def Preprocess(self):
		pass
	
	
	def Get_Coef(self, grade, level):
		if grade == 4:
			return self.grade4[level - 1]
		if grade == 5:
			return self.grade5[level - 1]
		if grade == 6:
			return self.grade6[level - 1]
		return 0
		
def LoadTarotConfig():
	#载入塔罗牌玩法配置
	global Tarot_ZhanBu_Config_Dict
	for TC in TarotConfig.ToClassType():
		Tarot_ZhanBu_Config_Dict[TC.zIndex] = TC


def LoadTarotCardConfig():
	#载入塔罗牌配置
	global TarotCardConfig_Dict
	global TarotCardGrade_Dict, TarotCardGrade_Dict_60
	for TCC in TarotCardConfig.ToClassType():
		if TCC.tType in TarotCardConfig_Dict:
			print "GE_EXC, repeat tType in LoadTarotCardConfig (%s)" % TCC.tType
		TarotCardConfig_Dict[TCC.tType] = TCC

		#组别分类
		tempList = None
		if TCC.grade not in TarotCardGrade_Dict:
			TarotCardGrade_Dict[TCC.grade] = tempList = []
		else:
			tempList = TarotCardGrade_Dict[TCC.grade]
		tempList.append(TCC.tType)
		
		tempList = None
		if TCC.grade not in TarotCardGrade_Dict_60:
			TarotCardGrade_Dict_60[TCC.grade] = tempList = []
		else:
			tempList = TarotCardGrade_Dict_60[TCC.grade]
		if TCC.level_60:
			tempList.append(TCC.tType)


	global Tarot_ZhanBu_Config_Dict
	for cfg in Tarot_ZhanBu_Config_Dict.itervalues():
		cfg.Preprocess()
	
	global TarotActiveRMB_Confg, TarotActiveRMB_Confg_Level_60
	
	TarotActiveRMB_Confg.AddRandomItem(EnumGameConfig.TarotActive_Grade_4, TarotCardGrade_Dict[4])
	TarotActiveRMB_Confg.AddRandomItem(EnumGameConfig.TarotActive_Grade_5, TarotCardGrade_Dict[5])
	
	TarotActiveRMB_Confg_Level_60.AddRandomItem(EnumGameConfig.TarotActive_Grade_4, TarotCardGrade_Dict_60[4])
	TarotActiveRMB_Confg_Level_60.AddRandomItem(EnumGameConfig.TarotActive_Grade_5, TarotCardGrade_Dict_60[5])
	
	
def LoadTarotCardLevelExpConfig():
	#载入塔罗牌升级经验配置
	global TarotCardGradeLevelExp_Dict
	for TLEC in CardLevelExpConfig.ToClassType():
		if TLEC.cardGrade not in TarotCardGradeLevelExp_Dict:
			TarotCardGradeLevelExp_Dict[TLEC.cardGrade] = {}
			TarotCardLevelUpExp_Dict[TLEC.cardGrade] = {}
		TarotCardGradeLevelExp_Dict[TLEC.cardGrade][TLEC.level] = TLEC.eatLevelExp
		TarotCardLevelUpExp_Dict[TLEC.cardGrade][TLEC.level] = TLEC.levelUpExp


def LoadTarotShopConfig():
	global TarotShop_Config_Dict
	global TarotCardConfig_Dict
	for TPs in TarotShopConfig.ToClassType():
		if TPs.card_Type in TarotShop_Config_Dict:
			print "GE_EXC, repeat card_Type in LoadTarotShopConfig (%s) " % TPs.pline
		if TPs.card_Type not in TarotCardConfig_Dict:
			print "GE_EXC error not this tarot card in TarotShop (%s)" % TPs.card_Type 
			continue
		TarotShop_Config_Dict[TPs.card_Type] = TPs


def LoadTarotLevelOpenSizeConfig():
	#载入塔罗牌玩法配置
	global TarotLevelOpenSizeConfig_Dict
	for TC in TarotLevelOpenSizeConfig.ToClassType():
		TarotLevelOpenSizeConfig_Dict[TC.level] = TC.openSize
		if TC.openSize > 8:
			print "GE_EXC, error in LoadTarotLevelOpenSizeConfig TC.openSize > 8"




def LoadTarotRingConfig():
	#载入塔罗牌玩法配置
	global TarotRingLevelExp_Dict
	global TarotRingConfig_Dict
	for TC in TarotRingConfig.ToClassType():
		TarotRingLevelExp_Dict[TC.ringLevel] = TC.ringExp
		TarotRingConfig_Dict[TC.ringLevel] = TC
		TC.Preprocess()

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadTarotConfig()
		LoadTarotCardConfig()
		LoadTarotCardLevelExpConfig()
		LoadTarotShopConfig()
		LoadTarotLevelOpenSizeConfig()
		LoadTarotRingConfig()
		


