#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionSpringHongBaoConfig")
#===============================================================================
# 红包闹新春,春节活动 @author: GaoShuai 2016
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("PassionAct")
	SpringHongBao_Dict = {}

class PassionSpringHongBaoConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionSpringHongBao.txt")
	def __init__(self):
		self.index = int					#索引
		self.needRMB = int					#需要消费神石
		self.reward = self.GetEvalByString	#奖励
		
def LoadPassionSpringHongBaoConfig():
	global SpringHongBao_Dict
	
	for cfg in PassionSpringHongBaoConfig.ToClassType():
		if cfg.index in SpringHongBao_Dict:
			print "GE_EXC, repeat index(%s) in SpringHongBao_Dict" % cfg.index
		SpringHongBao_Dict[cfg.index] = cfg


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadPassionSpringHongBaoConfig()
