#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.Title.TitleConfig")
#===============================================================================
# 称号功能配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Game.Property import PropertyEnum

if "_HasLoad" not in dir():
	T_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	T_FILE_FOLDER_PATH.AppendPath("Title")
	
	#称号字典
	Title_Dict = {}
	
	TitleLevel_Dict = {}
	TitleStar_Dict = {}
	TitleItem_Dict = {}


class TitleConfig(TabFile.TabLine):
	FilePath = T_FILE_FOLDER_PATH.FilePath("Title.txt")
	def __init__(self):
		self.titleId = int						#称号ID
		self.time = int							#称号持续时间
		self.titleName = str					#称号名称
		self.pType = int						#(0, 不加属性, 1,主角属性，2，全队属性)
		self.canLevelUp = int 
		self.canStarUp = int



class TitleLevelConfig(TabFile.TabLine, PropertyEnum.PropertyRead, PropertyEnum.PropertyRead_2):
	FilePath = T_FILE_FOLDER_PATH.FilePath("TitleLevel.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		PropertyEnum.PropertyRead_2.__init__(self)
		self.titleId = int
		self.level = int
		self.maxExp = int
		
		self.incPercentPt_1 = int
		self.incPercentPv_1 = int
		
		self.incPercentPt_2 = int
		self.incPercentPv_2 = int
		
	def InitPercentProperty(self):
		self.percent_property_dict = {}
		if self.incPercentPt_1:
			self.percent_property_dict[self.incPercentPt_1] = self.incPercentPv_1
		if self.incPercentPt_2:
			self.percent_property_dict[self.incPercentPt_2] = self.incPercentPv_2

class TitleStarConfig(TabFile.TabLine, PropertyEnum.PropertyRead, PropertyEnum.PropertyRead_2):
	FilePath = T_FILE_FOLDER_PATH.FilePath("TitleStar.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		PropertyEnum.PropertyRead_2.__init__(self)
		self.titleId = int
		self.star = int
		self.needTitleLevel = int
		self.needItems = self.GetEvalByString
		
		self.incPercentPt_1 = int
		self.incPercentPv_1 = int
		
		self.incPercentPt_2 = int
		self.incPercentPv_2 = int
		
	def InitPercentProperty(self):
		self.percent_property_dict = {}
		if self.incPercentPt_1:
			self.percent_property_dict[self.incPercentPt_1] = self.incPercentPv_1
		if self.incPercentPt_2:
			self.percent_property_dict[self.incPercentPt_2] = self.incPercentPv_2
		
class TitleItem(TabFile.TabLine):
	'''
	激活称号道具
	'''
	FilePath = T_FILE_FOLDER_PATH.FilePath("TitleItem.txt")
	def __init__(self):
		self.coding = int
		self.backItem = self.GetEvalByString
		
def LoadTitleItemConfig():
	global TitleItem_Dict
	
	for cfg in TitleItem.ToClassType():
		if cfg.coding in TitleItem_Dict:
			print "GE_EXC,repeat coding(%s) in LoadTitleItemConfig" % cfg.coding
		TitleItem_Dict[cfg.coding] = cfg
		
def LoadTitleConfig():
	global Title_Dict
	for tt in TitleConfig.ToClassType():
		if tt.titleId in Title_Dict:
			print "GE_EXC, repeat title titleId in LoadTitleConfig  (%s)" % tt.titleId
		Title_Dict[tt.titleId] = tt


def LoadTitleLevelConfig():
	global TitleLevel_Dict
	for tt in TitleLevelConfig.ToClassType():
		key = (tt.titleId, tt.level)
		if key in TitleLevel_Dict:
			print "GE_EXC, repeat key in LoadTitleLevelConfig  " ,key
		tt.InitProperty()
		tt.InitProperty_2()
		tt.InitPercentProperty()
		TitleLevel_Dict[key] = tt
		

def LoadTitleStarConfig():
	global TitleStar_Dict
	for tt in TitleStarConfig.ToClassType():
		key = (tt.titleId, tt.star)
		if key in TitleStar_Dict:
			print "GE_EXC, repeat key in LoadTitleStarConfig " ,key
		tt.InitProperty()
		tt.InitProperty_2()
		tt.InitPercentProperty()
		TitleStar_Dict[key] = tt

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadTitleConfig()
		LoadTitleLevelConfig()
		LoadTitleStarConfig()
		LoadTitleItemConfig()
		