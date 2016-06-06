#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionTGPointExchangeConfig")
#===============================================================================
# 感恩节积分兑换配置  @author liujia 2015
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("PassionAct")

	PassionActTGPointExchange_Dict = {}
	PassionActTGPointPointControlList = []

#感恩节积分兑换基础配置
class PassionActPointExchangeConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionActTGPointExchange.txt")
	def __init__(self):
		self.index = int                            #物品索引
		self.minLevel = int                         #需要角色最小等级
		self.needPoint = int                        #需要积分数
		self.items = self.GetEvalByString           #兑换的物品
		self.special = int                          #是否极品道具，进行全服公告并记录
		self.limitCnt = int                         #物品限购个数(-1表示不限购)
		self.freshType = int                        #刷新机制(0:每日,1:永久)
		

def LoadTGPointExchangeConfig():
	global PassionActTGPointExchange_Dict
	global PassionActTGPointPointControlList

	for cfg in PassionActPointExchangeConfig.ToClassType():
		if cfg.index in PassionActTGPointExchange_Dict:
			print "GE_EXC, repeat index(%s) in PassionActTGPointExchange_Dict" % cfg.index
		PassionActTGPointExchange_Dict[cfg.index] = cfg
		PassionActTGPointPointControlList.append(cfg.index)

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadTGPointExchangeConfig()
