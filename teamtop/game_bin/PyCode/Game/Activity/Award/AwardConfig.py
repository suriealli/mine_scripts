#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.Award.AwardConfig")
#===============================================================================
# 龙骑配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile
from ComplexServer.Log import AutoLog

AWARD_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
AWARD_FILE_FOLDER_PATH.AppendPath("Award")

if "_HasLoad" not in dir():
	AWARD_BASE = {}			#奖励基础配置
	AWARD_ENUM_LIST = []	#用于生成奖励枚举
	AWARDID_TO_LOG_OBJ = {}	#奖励ID索引日志对象
	
class AwardBase(TabFile.TabLine):
	FilePath = AWARD_FILE_FOLDER_PATH.FilePath("AwardBase.txt")
	def __init__(self):
		self.awardId = int
		self.awardEnumName = str
		self.awardName = str

def LoadAwardBase():
	global AWARD_BASE
	global AWARD_ENUM_LIST
	global AWARDID_TO_LOG_OBJ
	for config in AwardBase.ToClassType():
		AWARD_ENUM_LIST.append(config)
		AWARD_BASE[config.awardId] = config
		#保存日志对象
		logObj = AutoLog.AutoTransaction(config.awardEnumName, config.awardName)
		AWARDID_TO_LOG_OBJ[config.awardId] = logObj

def LoadAwardEnumList():
	global AWARD_ENUM_LIST
	for config in AwardBase.ToClassType():
		AWARD_ENUM_LIST.append(config)

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadAwardBase()
		