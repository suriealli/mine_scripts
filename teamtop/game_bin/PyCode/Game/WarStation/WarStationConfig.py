#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.WarStation.WarStationConfig")
#===============================================================================
# 战阵配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Game.Property import PropertyEnum

if "_HasLoad" not in dir():
	WARSTATION_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	WARSTATION_FILE_FOLDER_PATH.AppendPath("WarStation")
	
	WAR_STATION_BASE = {}
	THOUSAND_TIMES_PRO_DICT = {} #万分比属性
	WAR_STATION_ITEM = {}	#战魂石配置

class WarStation(TabFile.TabLine, PropertyEnum.PropertyRead):
	
	FilePath = WARSTATION_FILE_FOLDER_PATH.FilePath("WarStation.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.starId		= int
		self.IsMax		= int
		self.grade		= int
		self.starNum	= int
		self.useTimes	= int
		self.price		= int
		self.needItem	= self.GetEvalByString
		self.NextID		= int
		self.breakItem	= self.GetEvalByString
		#下面几个为万分比属性
		self.attack_pt	= int
		self.attack_mt	= int
		self.maxhp_t	= int
		self.crit_t		= int
		self.critpress_t= int
		self.parry_t	= int
		self.puncture_t	= int
		self.antibroken_t=int
		self.notbroken_t=int
	
	def InitThousandPro(self):
		self.thousand_pro_dict = {}
		if self.attack_pt:
			self.thousand_pro_dict[PropertyEnum.attack_p] = self.attack_pt
		if self.attack_mt:
			self.thousand_pro_dict[PropertyEnum.attack_m] = self.attack_mt
		if self.maxhp_t:
			self.thousand_pro_dict[PropertyEnum.maxhp] = self.maxhp_t
		if self.crit_t:
			self.thousand_pro_dict[PropertyEnum.crit] = self.crit_t
		if self.critpress_t:
			self.thousand_pro_dict[PropertyEnum.critpress] = self.critpress_t
		if self.parry_t:
			self.thousand_pro_dict[PropertyEnum.parry] = self.parry_t
		if self.puncture_t:
			self.thousand_pro_dict[PropertyEnum.puncture] = self.puncture_t
		if self.antibroken_t:
			self.thousand_pro_dict[PropertyEnum.antibroken] = self.antibroken_t
		if self.notbroken_t:
			self.thousand_pro_dict[PropertyEnum.notbroken] = self.notbroken_t
			
class WarStationItem(TabFile.TabLine, PropertyEnum.PropertyRead):
	#战魂强化石
	FilePath = WARSTATION_FILE_FOLDER_PATH.FilePath("WarStationItem.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.coding = int
		
		
def LoadWarStation():
	global WAR_STATION_BASE
	
	for cfg in WarStation.ToClassType():
		if cfg.starId in WAR_STATION_BASE:
			print "GE_EXC,repeat starId(%s) in LoadWarStation" % cfg.starId
		cfg.InitProperty()
		cfg.InitThousandPro()
		WAR_STATION_BASE[cfg.starId] = cfg
		
def LoadWarStationItem():
	global WAR_STATION_ITEM
	
	for cfg in WarStationItem.ToClassType():
		if cfg.coding in WAR_STATION_ITEM:
			print "GE_EXC,repeat coding(%s) in WarStationConfig.LoadWarStationItem" % cfg.coding
		WAR_STATION_ITEM[cfg.coding] = cfg
		cfg.InitProperty()
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadWarStation()
		LoadWarStationItem()
		