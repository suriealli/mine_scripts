#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.OG.OGConfig")
#===============================================================================
# OG配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

OG_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
OG_FILE_FOLDER_PATH.AppendPath("OG")

if "_HasLoad" not in dir():
	OG_TASK = {}
	
class OGTask(TabFile.TabLine):
	'''
	OG任务配置
	'''
	FilePath = OG_FILE_FOLDER_PATH.FilePath("OGTask.txt")
	def __init__(self):
		self.taskId = int

def LoadOGTask():
	global OG_TASK
	for config in OGTask.ToClassType():
		OG_TASK[config.taskId] = config 

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadOGTask()
		
		