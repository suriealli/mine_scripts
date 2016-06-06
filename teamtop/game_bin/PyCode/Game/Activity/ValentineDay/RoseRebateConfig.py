#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ValentineDay.RoseRebateConfig")
#===============================================================================
# 玫瑰返利Config
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("ValentineDay")

	RoseRebate_BaseConfig_Dict = {}		#玫瑰返利配置 {rebateCategory:{rebateType:cfg,},}

class RoseRebate(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("RoseRebate.txt")
	def __init__(self):
		self.rebateCategory = int	#返利大条
		self.needTotalNum = int		#需要达标人数
		self.rebateType = int		#返利小项
		self.needRoseNum = int		#需要赠送99朵玫瑰总数达到才算一个到needTotalNum
		self.needVIP = int			#领取此项需要VIP
		self.rebateItem = self.GetEvalByString	#返利获得道具

def GetRebateCfg(rebateCategory, rebateType):
	'''
	返回对应rebateCategory, rebateType的返利配置
	'''
	rebateCfg = None
	rebateCfgDict = RoseRebate_BaseConfig_Dict.get(rebateCategory, None)
	if rebateCfgDict:
		rebateCfg = rebateCfgDict.get(rebateType)
		return rebateCfg
	else:
		return None
		
def LoadRoseRebate():
	global RoseRebate_BaseConfig_Dict
	for cfg in RoseRebate.ToClassType():
		rebateCategory = cfg.rebateCategory
		rebateType = cfg.rebateType
		rebateCfgDict = RoseRebate_BaseConfig_Dict.setdefault(rebateCategory, {})
		if rebateType in rebateCfgDict:
			print "GE_EXC,repeat rebateType(%s) of rebateCategory(%s) in RoseRebate_BaseConfig_Dict" % (rebateType, rebateCategory)
		rebateCfgDict[rebateType] = cfg

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadRoseRebate()