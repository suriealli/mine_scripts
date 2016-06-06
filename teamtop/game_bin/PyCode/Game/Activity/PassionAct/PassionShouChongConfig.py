#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionShouChongConfig")
#===============================================================================
# 每日首冲配置
#===============================================================================
import cDateTime
import DynamicPath
import Environment
from Util.File import TabFile


if "_HasLoad" not in dir() :
	SHOUCHONG_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	SHOUCHONG_FILE_FOLDER_PATH.AppendPath("PassionAct")
	SHOUCHONG_AWARD = {}
	CHONGZHI_AWARD = {}
	


class ShouChong (TabFile.TabLine):
	FilePath = SHOUCHONG_FILE_FOLDER_PATH.FilePath("PassionShouChong.txt")
	def __init__(self):
		self.ShouChongId = int 
		self.dayTime = self.GetDatetimeByString
		self.rewardItem = self.GetEvalByString
		self.Counts = int


def LoadShouChong():
	global SHOUCHONG_AWARD
	for cfg in ShouChong.ToClassType():
		if cfg.ShouChongId in SHOUCHONG_AWARD :
			print "GE_EXC, repeat cfg.ShouChongId(%s) in LoadShouChong" % cfg.ShouChongId
		SHOUCHONG_AWARD[cfg.ShouChongId]=cfg


def GetShouChongObj():
	nowTime = cDateTime.Now()
	for _, cfg in SHOUCHONG_AWARD.items():
		if nowTime.year == cfg.dayTime.year and nowTime.month == cfg.dayTime.month and nowTime.day == cfg.dayTime.day:
			return cfg
	return None


class ChongZhi (TabFile.TabLine):
	FilePath = SHOUCHONG_FILE_FOLDER_PATH.FilePath("PassionChongZhiDays.txt")
	def __init__(self):
		self.ChongZhiId = int 
		self.ChongZhiDays = int 
		self.rewardItem = self.GetEvalByString
	

def LoadChongZhi():
	global CHONGZHI_AWARD
	for cfg in ChongZhi.ToClassType():
		if cfg.ChongZhiId in CHONGZHI_AWARD :
			print "GE_EXC, repeat cfg.ChongZhiId(%s) in LoadChongZhi" % cfg.ChongZhiId
		CHONGZHI_AWARD[cfg.ChongZhiId]=cfg


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadShouChong()
		LoadChongZhi()
