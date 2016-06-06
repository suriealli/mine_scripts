#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQAppPanel.QQAppPanelConfig")
#===============================================================================
# 龙骑配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

QQ_APP_PANEL_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
QQ_APP_PANEL_FILE_FOLDER_PATH.AppendPath("QQAppPanel")

if "_HasLoad" not in dir():
	APP_PANEL_LOGIN_REWARD = {}
	
class AppPanelLoginReward(TabFile.TabLine):
	'''
	应用面板登陆奖励
	'''
	FilePath = QQ_APP_PANEL_FILE_FOLDER_PATH.FilePath("AppPanelLoginReward.txt")
	def __init__(self):
		self.days = int
		self.bindRMB = int
		self.rewardItemList = self.GetEvalByString

def LoadAppPanelLoginReward():
	global APP_PANEL_LOGIN_REWARD
	for config in AppPanelLoginReward.ToClassType():
		APP_PANEL_LOGIN_REWARD[config.days] = config 

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadAppPanelLoginReward()
		