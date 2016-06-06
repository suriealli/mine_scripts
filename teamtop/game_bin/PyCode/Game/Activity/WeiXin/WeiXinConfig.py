#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.WeiXin.WeiXinConfig")
#===============================================================================
# 微信配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	WX_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	WX_FILE_FOLDER_PATH.AppendPath("WeiXin")
	
	WeiXin_Dict = {}
	WeiboZone_Dict = {}
	
class WeiXinConfig(TabFile.TabLine):
	FilePath = WX_FILE_FOLDER_PATH.FilePath("WeiXinConfig.txt")
	def __init__(self):
		self.index = int
		self.needCnt = int
		self.rewards = eval

class WeiboZoneConfig(TabFile.TabLine):
	FilePath = WX_FILE_FOLDER_PATH.FilePath("WeiboZoneConfig.txt")
	def __init__(self):
		self.index = int
		self.nextIndex = int
		self.rewards = eval
		
def LoadWeiXinConfig():
	global WeiXin_Dict
	
	for WX in WeiXinConfig.ToClassType():
		if WX.index in WeiXin_Dict:
			print "GE_EXC, repeat index(%s) in WeiXin_Dict" % WX.index
			continue
		WeiXin_Dict[WX.index] = WX
	
def LoadWeiboZoneConfig():
	global WeiboZone_Dict
	
	for WZ in WeiboZoneConfig.ToClassType():
		if WZ.index in WeiboZone_Dict:
			print "GE_EXC, repeat index(%s) in WeiboZone_Dict" % WZ.index
			continue
		WeiboZone_Dict[WZ.index] = WZ
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadWeiXinConfig()
		LoadWeiboZoneConfig()