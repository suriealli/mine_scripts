#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionSignInConfig")
#===============================================================================
# 签到配置
#===============================================================================

import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir() :
	SignIn_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	SignIn_FILE_FOLDER_PATH.AppendPath("PassionAct")
	SIGN_IN_AWARD = {}


class SignInAward (TabFile.TabLine):
	FilePath = SignIn_FILE_FOLDER_PATH.FilePath("PassionSignInAward.txt")
	def __init__(self):
		self.SignInId = int 
		self.SignInTime = int 
		self.rewardItem = self.GetEvalByString



def LoadSignInAward():
	global SIGN_IN_AWARD
	for cfg in SignInAward.ToClassType():
		if cfg.SignInId in SIGN_IN_AWARD :
			print "GE_EXC, repeat cfg.SignInId(%s) in LoadSignInAward" % cfg.SignInId
		SIGN_IN_AWARD[cfg.SignInId]=cfg
		


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadSignInAward()