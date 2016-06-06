#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.QandA.PuzzleConfig")

#===============================================================================
#趣味拼图配置
#===============================================================================

import DynamicPath
import Environment
from Util.File import TabFile


if "_HasLoad" not in dir() :
	PUZZLE_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	PUZZLE_FILE_FOLDER_PATH.AppendPath("XinDaTi")
	PUZZLE_AWARD = {}				#趣味拼图奖励配置
	PUZZLE_PICTURE ={}
	
	
class PuzzleAward(TabFile.TabLine):
	FilePath = PUZZLE_FILE_FOLDER_PATH.FilePath("AwardPuzzle.txt")
	def __init__(self):
		self.AwardId = int
		self.AwardLevel = self.GetEvalByString
		self.LeftTime = int
		self.Award = self.GetEvalByString
		self.Money = int
		self.Money_fcm = int                          #金币奖励
		self.Award_fcm = self.GetEvalByString         #奖励
		
		
def LoadPuzzleAward():
	global 	PUZZLE_AWARD
	for cfg in 	PuzzleAward.ToClassType():
		if cfg.AwardId in PUZZLE_AWARD:
			print "GE_EXC, repeat cfg.awardId(%s) in LoadPuzzleAward " % cfg.AwardId
		PUZZLE_AWARD[cfg.AwardId] = cfg
		
class PuzzlePicture(TabFile.TabLine):
	FilePath = PUZZLE_FILE_FOLDER_PATH.FilePath("PuzzlePicture.txt")
	def __init__(self):		
		self.PictureId = int
		
		
def LoadPicture():
	global PUZZLE_PICTURE
	for cfg in PuzzlePicture.ToClassType():
		if cfg.PictureId in PUZZLE_PICTURE :
			print "GE_EXC, repeat cfg.PictureId(%s) in LOadPicture" % cfg.PictureId
		PUZZLE_PICTURE[cfg.PictureId]=cfg
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadPuzzleAward()
		LoadPicture()
