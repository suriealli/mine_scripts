#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Scene.MapMgr")
#===============================================================================
# 地图相关,地图底层配置
#===============================================================================
import os
import glob
import cSceneMgr
import Environment
import DynamicPath


def LoadMapConfig():
	#载入地图格子配置
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("MapConfig")
	for filePath in glob.glob(FILE_FOLDER_PATH.FilePath("*.txt")):
		mapId = filePath[filePath.rfind(os.sep)+1:filePath.rfind(".txt")]
		cSceneMgr.CreateMapTemplate(int(mapId), filePath)

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadMapConfig()

