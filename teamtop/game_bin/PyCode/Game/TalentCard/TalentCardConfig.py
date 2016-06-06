#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.TalentCard.TalentCardConfig")
#===============================================================================
# 天赋卡配置表
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	TALENT_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	TALENT_FILE_FOLDER_PATH.AppendPath("TalentCard")

	TALENT_BASE_DICT = {}		#天赋卡基础配置
	TALENT_LEVEL_EXP_DICT = {}	#天赋卡升级配置
	TALENT_SUIT_DICT = {}		#天赋卡套装配置
	TALENT_DEC_DICT = {}		#天赋卡分解配置
	TALENT_UNLOCK_DICT = {}		#解锁卡槽配置表
	TALENT_DEBRIS_DICT = {}

	
class TalentCardBase(TabFile.TabLine):
	'''
	天赋卡基础配置表
	'''
	FilePath = TALENT_FILE_FOLDER_PATH.FilePath("TalentCard.txt")
	def __init__(self):
		self.cardId			= int
		self.cardtype		= int
		self.name			= str
		self.grade			= int
		self.maxlevel		= int
		self.heroput		= int
		self.exchangeItem	= self.GetEvalByString
		self.pt1			= int
		self.pv1			= self.GetEvalByString
		self.pt2			= int
		self.pv2			= self.GetEvalByString
		self.cardskill		= self.GetEvalByString
		self.suitId			= self.GetEvalByString
		self.skill_zdl		= self.GetEvalByString
		
class CardLevelExp(TabFile.TabLine):
	'''
	天赋卡升级配置表
	'''
	FilePath = TALENT_FILE_FOLDER_PATH.FilePath("CardLevelExp.txt")
	def __init__(self):
		self.cardId		= int
		self.level		= int
		self.starNum	= self.GetEvalByString
		self.cardNum	= self.GetEvalByString

class TalentCardSuit(TabFile.TabLine):
	'''
	天赋卡套装属性
	'''
	FilePath = TALENT_FILE_FOLDER_PATH.FilePath("TalentCardSuit.txt")
	def __init__(self):
		self.suitId		= int
		self.cnt		= int
		self.skill		= self.GetEvalByString
		self.pt1		= int
		self.pv1		= self.GetEvalByString
		self.pt2		= int
		self.pv2		= self.GetEvalByString
		self.skillzdl	= self.GetEvalByString

class DecTalent(TabFile.TabLine):
	'''
	天赋卡分解配置表
	'''
	FilePath = TALENT_FILE_FOLDER_PATH.FilePath("DecTalent.txt")
	def __init__(self):
		self.cardId		= int
		self.cardLevel		= int
		self.UnbindRMB		= int
		self.backstar		= self.GetEvalByString
		self.backcard		= self.GetEvalByString

class UnLockTalent(TabFile.TabLine):
	'''
	解锁卡槽配置
	'''
	FilePath = TALENT_FILE_FOLDER_PATH.FilePath("UnLockTalent.txt")
	def __init__(self):
		self.unLockId	= int
		self.needItem	= self.GetEvalByString

class DebrisSell(TabFile.TabLine):
	'''
	碎片出售配置表
	'''
	FilePath = TALENT_FILE_FOLDER_PATH.FilePath("DebrisSell.txt")
	def __init__(self):
		self.itemId 	= int
		self.backCoding	= int
		self.backCnt	= int
		
def LoadTalentCard():
	global TALENT_BASE_DICT
	for cardCfg in TalentCardBase.ToClassType():
		if cardCfg.cardId in TALENT_BASE_DICT:
			print "GE_EXC,repeat cardType(%s) in TalentCardConfig" % cardCfg.cardId
		TALENT_BASE_DICT[cardCfg.cardId] = cardCfg

def LoadCardLevelExp():
	global TALENT_LEVEL_EXP_DICT
	for Expcfg in CardLevelExp.ToClassType():
		key = (Expcfg.cardId, Expcfg.level)
		if key in TALENT_LEVEL_EXP_DICT:
			print "GE_EXC,repeat cardType(%s) and level(%s) in CardLevelExp" % (Expcfg.cardId, Expcfg.level)
		TALENT_LEVEL_EXP_DICT[key] = Expcfg

def LoadTalentSuit():
	global TALENT_SUIT_DICT
	for SuitCfg in TalentCardSuit.ToClassType():
		if SuitCfg.suitId in TALENT_SUIT_DICT:
			print "GE_EXC,repeat suitId(%s) in LoadTalentSuit" % SuitCfg.suitId
		TALENT_SUIT_DICT[SuitCfg.suitId] = SuitCfg

def LoadDecTalent():
	global TALENT_DEC_DICT
	for DecCfg in DecTalent.ToClassType():
		Deckey = (DecCfg.cardId, DecCfg.cardLevel)
		if Deckey in TALENT_DEC_DICT:
			print "GE_EXC,repeat cardType(%s) and cardLevel(%s) in LoadDecTalent" % (DecCfg.cardId, DecCfg.cardLevel)
		TALENT_DEC_DICT[Deckey] = DecCfg

def LoadUnLockTalent():
	global TALENT_UNLOCK_DICT
	for unlockCfg in UnLockTalent.ToClassType():
		if unlockCfg.unLockId in TALENT_UNLOCK_DICT:
			print "GE_EXC, repeat unLockId(%s) in UnLockTalent" % unlockCfg.unLockId
		TALENT_UNLOCK_DICT[unlockCfg.unLockId] = unlockCfg

def LoadDebrisSell():
	global TALENT_DEBRIS_DICT
	for DeCfg in DebrisSell.ToClassType():
		if DeCfg.itemId in TALENT_DEBRIS_DICT:
			print "GE_EXC, repeat itemId(%s) in LoadDebrisSell" % DeCfg.itemId
		TALENT_DEBRIS_DICT[DeCfg.itemId] = (DeCfg.backCoding, DeCfg.backCnt)
			
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadTalentCard()
		LoadCardLevelExp()
		LoadTalentSuit()
		LoadDecTalent()
		LoadUnLockTalent()
		LoadDebrisSell()
		