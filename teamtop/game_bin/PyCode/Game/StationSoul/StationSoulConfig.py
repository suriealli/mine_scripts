#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.StationSoul.StationSoulConfig")
#===============================================================================
# 阵灵 Config
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile
from Game.Property import PropertyEnum


if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("StationSoul")
	
	#阵灵基本配置 {ssId:cfg,}
	StationSoul_BaseConfig_Dict = {} 
	#阵灵强化石配置{itemCoding:cfg,}
	StationSoul_ItemConfig_Dict = {}
	DEFAULT_STATIONSOUL_ITEM = 0
	
class StationSoul(TabFile.TabLine, PropertyEnum.PropertyRead):
	FilePath = FILE_FLODER_PATH.FilePath("StationSoul.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.ssId = int
		self.gradeLevel = int
		self.starLevel = int
		self.canBreak = int
		self.maxItemCnt = int
		self.nextSSId = int
		self.price = int
		self.upgradeItem = self.GetEvalByString
		self.otherItemCoding = self.GetEvalByString
		self.needWarStationId = int
		self.breakItem = self.GetEvalByString
		self.skillState = self.GetEvalByString
		#属性万分比
		self.attack_pt = int
		self.attack_mt = int
		self.maxhp_t = int
		self.crit_t = int
		self.critpress_t = int
		self.parry_t = int
		self.puncture_t = int
		self.antibroken_t = int
		self.notbroken_t = int
	
	def InitPPT(self):
		'''
		预处理万分比属性
		'''
		self.ppt_dict = {}
		self.ppt_dict[PropertyEnum.attack_p] = self.attack_pt
		self.ppt_dict[PropertyEnum.attack_m] = self.attack_mt
		self.ppt_dict[PropertyEnum.maxhp] = self.maxhp_t
		self.ppt_dict[PropertyEnum.crit] = self.crit_t
		self.ppt_dict[PropertyEnum.critpress] = self.critpress_t
		self.ppt_dict[PropertyEnum.parry] = self.parry_t
		self.ppt_dict[PropertyEnum.puncture] = self.puncture_t
		self.ppt_dict[PropertyEnum.antibroken] = self.antibroken_t
		self.ppt_dict[PropertyEnum.notbroken] = self.notbroken_t		


def LoadStationSoul():
	global StationSoul_BaseConfig_Dict
	for cfg in StationSoul.ToClassType():
		ssId = cfg.ssId
		if ssId in StationSoul_BaseConfig_Dict:
			print "GE_EXC,repeat ssId(%s) in StationSoul_BaseConfig_Dict" % ssId
		nextSSId = cfg.nextSSId
		upgradeItem = cfg.upgradeItem
		breakItem = cfg.breakItem
		if nextSSId and not upgradeItem and not breakItem:
			print "GE_EXC, Config error not upgradeItem and not breakItem!"
		cfg.InitProperty()
		cfg.InitPPT()
		StationSoul_BaseConfig_Dict[ssId] = cfg		


class StationSoulItem(TabFile.TabLine, PropertyEnum.PropertyRead):
	#战魂强化石
	FilePath = FILE_FLODER_PATH.FilePath("StationSoulItem.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.coding = int	


def LoadStationSoulItem():
	global DEFAULT_STATIONSOUL_ITEM
	global StationSoul_ItemConfig_Dict
	for cfg in StationSoulItem.ToClassType():
		if cfg.coding in StationSoul_ItemConfig_Dict:
			print "GE_EXC,repeat coding(%s) in StationSoul_ItemConfig_Dict" % cfg.coding
		cfg.InitProperty()
		StationSoul_ItemConfig_Dict[cfg.coding] = cfg
		DEFAULT_STATIONSOUL_ITEM = cfg.coding
			
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadStationSoul()
		LoadStationSoulItem()