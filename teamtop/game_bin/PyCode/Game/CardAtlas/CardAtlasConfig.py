#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.CardAtlas.CardAtlasConfig")
#===============================================================================
# 卡牌图鉴配置
#===============================================================================
import DynamicPath
from Util.File import TabFile
import Environment
from Game.Property import PropertyEnum

if "_HasLoad" not in dir():
	DailyDo_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	DailyDo_FILE_FOLDER_PATH.AppendPath("CardAtlas")
	
	Card_Dict = {}
	AtlasAct_Dict = {}
	AtlasBelong_Dict = {}
	AtlasLevel_Dict = {}
	AtlasGrade_Dict = {}
	AtlasSuitGrade_Dict = {}
	
class CardConfig(TabFile.TabLine):
	FilePath = DailyDo_FILE_FOLDER_PATH.FilePath("card.txt")
	def __init__(self):
		self.cardId = int
		self.returnChip = int
	
def LoadCardConfig():
	global Card_Dict
	
	for cfg in CardConfig.ToClassType():
		if cfg.cardId in Card_Dict:
			print 'GE_EXC, repeat cardId %s in CardAtlasConfig.Card_Dict' % cfg.cardId
		Card_Dict[cfg.cardId] = cfg
	
class AtlasGradeConfig(TabFile.TabLine, PropertyEnum.PropertyRead):
	FilePath = DailyDo_FILE_FOLDER_PATH.FilePath("atlasGrade.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		
		self.atlasId = int
		self.atlasGrade = int
		self.actNeedCard = int
		self.belongSuit = int
		self.upGradeNeedCard = int
		self.nextGrade = int
		self.addCoef = int
	
def LoadAtlasGradeConfig():
	global AtlasGrade_Dict, AtlasAct_Dict, AtlasBelong_Dict
	
	for cfg in AtlasGradeConfig.ToClassType():
		if (cfg.atlasId, cfg.atlasGrade) in AtlasGrade_Dict:
			print 'GE_EXC, repeat atlasId %s, atlasGrade %s in CardAtlasConfig.AtlasGrade_Dict' % (cfg.atlasId, cfg.atlasGrade)
		cfg.InitProperty()
		AtlasGrade_Dict[(cfg.atlasId, cfg.atlasGrade)] = cfg
		
		#图鉴激活
		if cfg.actNeedCard:
			if cfg.atlasId in AtlasAct_Dict:
				print 'GE_EXC, repeat act atlas need card, atlasid %s, atlas grade %s' % (cfg.atlasId, cfg.atlasGrade)
			AtlasAct_Dict[cfg.atlasId] = cfg
		
		#图鉴组
		if cfg.belongSuit not in AtlasBelong_Dict:
			AtlasBelong_Dict[cfg.belongSuit] = set()
		AtlasBelong_Dict[cfg.belongSuit].add(cfg.atlasId)
		
class AtlasLevelConfig(TabFile.TabLine, PropertyEnum.PropertyRead):
	FilePath = DailyDo_FILE_FOLDER_PATH.FilePath("atlasLevel.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		
		self.atlasLevel = int
		self.needGrade = int
		self.upLevelNeedChip = int
		self.nextLevel = int
		
def LoadAtlasLevelConfig():
	global AtlasLevel_Dict
	
	for cfg in AtlasLevelConfig.ToClassType():
		if cfg.atlasLevel in AtlasLevel_Dict:
			print 'GE_EXC, repeat atlasId %s in CardAtlasConfig.AtlasLevel_Dict' % cfg.atlasLevel
		cfg.InitProperty()
		AtlasLevel_Dict[cfg.atlasLevel] = cfg
	
class AtlasSuitGradeConfig(TabFile.TabLine, PropertyEnum.PropertyRead):
	FilePath = DailyDo_FILE_FOLDER_PATH.FilePath("atlasSuitGrade.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		
		self.suitId = int
		self.suitGradeP = int
		
		self.pt1 = int
		self.pv1 = int
		
		self.pt2 = int
		self.pv2 = int
		
		self.pt3 = int
		self.pv3 = int
		
		self.pt4 = int
		self.pv4 = int
		
	def InitPercentProperty(self):
		self.percent_property_dict = {}
		if self.pt1:
			self.percent_property_dict[self.pt1] = self.pv1
		if self.pt2:
			self.percent_property_dict[self.pt2] = self.pv2
		if self.pt3:
			self.percent_property_dict[self.pt3] = self.pv3
		if self.pt4:
			self.percent_property_dict[self.pt4] = self.pv4
		
def LoadAtlasSuitGradeConfig():
	global AtlasSuitGrade_Dict
	
	for cfg in AtlasSuitGradeConfig.ToClassType():
		if (cfg.suitId, cfg.suitGradeP) in AtlasSuitGrade_Dict:
			print 'GE_EXC, repeat suitId %s, suitGradeP %s in CardAtlasConfig.AtlasSuitGrade_Dict' % (cfg.suitId, cfg.suitGradeP)
		cfg.InitProperty()
		cfg.InitPercentProperty()
		AtlasSuitGrade_Dict[(cfg.suitId, cfg.suitGradeP)] = cfg
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadCardConfig()
		LoadAtlasGradeConfig()
		LoadAtlasLevelConfig()
		LoadAtlasSuitGradeConfig()
		
	
