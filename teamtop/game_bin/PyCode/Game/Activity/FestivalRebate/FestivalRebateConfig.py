#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.FestivalRebate.FestivalRebateConfig")
#===============================================================================
# 春节大回馈 Config
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile
from Common.Other import EnumGameConfig


if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("FestivalRebate")
	
#	#活动时间控制
#	FestivalRebate_Active_Control = None
	
	#返利比例控制{rebateIndex:cfg,}
	FestivalRebate_RebateControl_Dict = {}
	FestivalRebate_SortedIndex_List = []
		
class FestivalRebateBase(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("FestivalRebateBase.txt")
	def __init__(self):
		self.rebateIndex = int
		self.RMBRange = self.GetEvalByString
		self.rebatePercent = int


def LoadFestivalRebateBase():
	global FestivalRebate_RebateControl_Dict
	for cfg in FestivalRebateBase.ToClassType():
		rebateIndex = cfg.rebateIndex
		if rebateIndex in FestivalRebate_RebateControl_Dict:
			print "GE_EXC,FestivalRebateBase Error:repeat rebateIndex(%s) in FestivalRebate_RebateControl_Dict" % rebateIndex
		FestivalRebate_RebateControl_Dict[rebateIndex] = cfg
	
	global FestivalRebate_SortedIndex_List
	FestivalRebate_SortedIndex_List = sorted([i for i in FestivalRebate_RebateControl_Dict.keys()], key=lambda i:i, reverse=False)


def CalculateRebateRMB(buyRMB=0):
	'''
	根据购买神石 计算回馈神石
	'''
	#小于最低区段下限 没有返利资格
	if buyRMB < FestivalRebate_RebateControl_Dict[FestivalRebate_SortedIndex_List[0]].RMBRange[0]:
		return 0
	
	#超过最大区段上限 取最高区段返利比例
	if buyRMB > FestivalRebate_RebateControl_Dict[FestivalRebate_SortedIndex_List[-1]].RMBRange[1]:
		rebatePercent = FestivalRebate_RebateControl_Dict[FestivalRebate_SortedIndex_List[-1]].rebatePercent
		return min(EnumGameConfig.FestivalRebate_MaxRebate, int((rebatePercent * buyRMB) / 10000.0))
	
	#否则 落位再计算
	rebateIndex = 0
	for tRebateIndex in FestivalRebate_SortedIndex_List:
		rebateIndex = tRebateIndex
		RMBRange = FestivalRebate_RebateControl_Dict[tRebateIndex].RMBRange
		if RMBRange[0] <= buyRMB <= RMBRange[1]:
			break
	
	rebatePercent = FestivalRebate_RebateControl_Dict[rebateIndex].rebatePercent
	return min(EnumGameConfig.FestivalRebate_MaxRebate, int((rebatePercent * buyRMB) / 10000.0))
	
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadFestivalRebateBase()
