#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ValentineDay.GlamourPartyConfig")
#===============================================================================
# 魅力派对 Config
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("ValentineDay")
	
	GlamourParty_ConfigBase_Dict = {}		#魅力派对基本配置 {partyGrade:cfg,}
	GlamourParty_TargetConfig_Dict = {}		#魅力派对目标配置{targetId:cfg,}

class GlamourParty(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("GlamourParty.txt")
	def __init__(self):
		self.partyGrade = int
		self.qinmiPercent = int
		self.addGlamour = int
		

class GlamourPartyTarget(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("GlamourPartyTarget.txt")
	def __init__(self):
		self.targetId = int
		self.needTotalGlamour = int
		self.rewardItems = self.GetEvalByString

def LoadGlamourParty():
	global GlamourParty_ConfigBase_Dict
	for cfg in GlamourParty.ToClassType():
		partyGrade = cfg.partyGrade
		if partyGrade in GlamourParty_ConfigBase_Dict:
			print "GE_EXC, repeat partyGrade(%s) in GlamourParty_ConfigBase_Dict"
		GlamourParty_ConfigBase_Dict[partyGrade] = cfg

def LoadGlamourPartyTarget():
	global GlamourParty_TargetConfig_Dict
	for cfg in GlamourPartyTarget.ToClassType():
		targetId = cfg.targetId
		if targetId in GlamourParty_TargetConfig_Dict:
			print "GE_EXC, repeat targetId(%s) in GlamourParty_TargetConfig_Dict" % targetId
		GlamourParty_TargetConfig_Dict[targetId] = cfg

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadGlamourParty()
		LoadGlamourPartyTarget()