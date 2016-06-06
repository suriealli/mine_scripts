#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionRechargeHongBaoConfig")
#===============================================================================
# 充值送红包配置  @author: Gaoshuai 2015
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("PassionActDoubleTwelve")
	
	RechargeHongBaoObj = None


class PassionRechargeAndRewardConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionRechargeHongBao.txt")
	def __init__(self):
		self.rechargeRMB = int						#需要消费神石
		self.items = self.GetEvalByString			#奖励


def LoadPassionRechargeAndRewardConfig():
	global RechargeHongBaoObj
	
	cnt = 0
	for cfg in PassionRechargeAndRewardConfig.ToClassType():
		RechargeHongBaoObj = cfg
		cnt += 1
		if cnt > 1 :
			print "GE_EXC, more than one line in PassionRechargeAndReward.txt, please check it."


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadPassionRechargeAndRewardConfig()
