#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ChunJieYuanXiao.ChunJieYuanXiaoChongZhiConfig")
#===============================================================================
# 元宵节充值活动配置表
#===============================================================================

import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	NYD_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	NYD_FILE_FOLDER_PATH.AppendPath("ChunJieYuanXiao")
	YuanXiaoChongZhiReward = {}

class YuanXiaoChongZhi(TabFile.TabLine):
	FilePath = NYD_FILE_FOLDER_PATH.FilePath("PassionYuanXiaoChongZhiReward.txt")
	def __init__(self):
		self.RewardId = int
		self.NeedRechargeRMB = int
		self.Awards = self.GetEvalByString
		self.HuaDengAmounts = int 

def LoadYuanXiaoChongZhi():
	global YuanXiaoChongZhiReward
	for cf in YuanXiaoChongZhi.ToClassType() :
		if cf.RewardId in YuanXiaoChongZhiReward :
			print "GE_EXC, repeat RewardId is in YuanXiaoChongZhiReward in LoadYuanXiaoChongZhi" % cf.RewardId
		YuanXiaoChongZhiReward[cf.RewardId] = cf
	


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadYuanXiaoChongZhi()