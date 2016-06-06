#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ZhongQiu.ZhongQiuShouChongConfig")
#===============================================================================
# 中秋首冲 config
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("ZhongQiu")
	
	#中秋首冲奖励配置 {dayIndex:cfg,}
	ZhongQiuShouChong_Reward_Dict = {}


class ZhongQiuShouChong(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("ZhongQiuShouChong.txt")
	def __init__(self):
		self.dayIndex = int
		self.rewardItems = self.GetEvalByString
		self.rewardStep = int
		
	
def LoadZhongQiuShouChong():
	global ZhongQiuShouChong_Reward_Dict
	for cfg in ZhongQiuShouChong.ToClassType():
		dayIndex = cfg.dayIndex
		if dayIndex in ZhongQiuShouChong_Reward_Dict:
			print "GE_EXC, repeat dayIndex(%s) in ZhongQiuShouChong_Reward_Dict" % dayIndex
		ZhongQiuShouChong_Reward_Dict[dayIndex] = cfg


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadZhongQiuShouChong()