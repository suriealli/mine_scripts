#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.Station.StationConfig")
#===============================================================================
# 阵位配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	STATION_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	STATION_FILE_FOLDER_PATH.AppendPath("Station")
	
	#助阵位声望
	HelpStationAct_Dict = {}
	#助阵位镶嵌
	HelpStationMosaic_Dict = {}
	#神佑卷轴兑换
	HelpStationCrystalEx_Dict = {}
	#镶嵌加成
	HSMosaicPercent_Dict = {}
	
class HelpStationMosaicPercent(TabFile.TabLine):
	FilePath = STATION_FILE_FOLDER_PATH.FilePath("HelpStationMosaicPrecent.txt")
	def __init__(self):
		self.mosaicLevel = int					#镶嵌等级
		self.proPercent = int					#加成万分比
	
def LoadHSMosaicPercent():
	#镶嵌等级加成万分比
	global HSMosaicPercent_Dict
	for HSMP in HelpStationMosaicPercent.ToClassType():
		if HSMP.mosaicLevel in HSMosaicPercent_Dict:
			print "GE_EXC, repeat mosaicLevel:%s in HSMosaicPercent_Dict" % HSMP.mosaicLevel
		HSMosaicPercent_Dict[HSMP.mosaicLevel] = HSMP
	
class HelpStationMosaic(TabFile.TabLine):
	FilePath = STATION_FILE_FOLDER_PATH.FilePath("HelpStationMosaic.txt")
	def __init__(self):
		self.mosaicLevel = int					#镶嵌等级
		self.needCrystal = int					#需要一级神佑卷轴个数
		self.lowList = eval						#可用低级神佑卷轴coding
		
def LoadHSMosaic():
	global HelpStationMosaic_Dict
	for HSM in HelpStationMosaic.ToClassType():
		if HSM.mosaicLevel in HelpStationMosaic_Dict:
			print "GE_EXC, repeat mosaicLevel:%s in HelpStationMosaic_Dict" % HSM.mosaicLevel
		HelpStationMosaic_Dict[HSM.mosaicLevel] = HSM
	
class HelpStationCrystalEx(TabFile.TabLine):
	FilePath = STATION_FILE_FOLDER_PATH.FilePath("HelpStationCrystalEx.txt")
	def __init__(self):
		self.crystalCoding = int					#神佑卷轴coding
		self.exCrystal = int						#兑换的一级神佑卷轴个数
	
def LoadHSCrystalEx():
	global HelpStationCrystalEx_Dict
	for HSCE in HelpStationCrystalEx.ToClassType():
		if HSCE.crystalCoding in HelpStationCrystalEx_Dict:
			print "GE_EXC, repeat crystalLevel:%s in HelpStationCrystalEx_Dict" % HSCE.crystalCoding
		HelpStationCrystalEx_Dict[HSCE.crystalCoding] = HSCE
	
class HelpStationConfig(TabFile.TabLine):
	FilePath = STATION_FILE_FOLDER_PATH.FilePath("HelpStation.txt")
	def __init__(self):
		self.station = int			#助阵位ID
		self.star = int				#星级
		self.needRepution = int		#需要声望
	
def LoadHelpStationConfig():
	global HelpStationAct_Dict
	for HS in HelpStationConfig.ToClassType():
		if (HS.station, HS.star) in HelpStationAct_Dict:
			print "GE_EXC, repeat (station:%s, star:%s) in HelpStationAct_Dict" % (HS.station, HS.star)
			continue
		HelpStationAct_Dict[(HS.station, HS.star)] = HS
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadHelpStationConfig()
		LoadHSMosaic()
		LoadHSCrystalEx()
		LoadHSMosaicPercent()
		