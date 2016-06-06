#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.DailyFB.DailyFBConfig")
#===============================================================================
# 勇者试炼场Config
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Game.Role.Data import EnumCD

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("DailyFB")
	
	DailyFB_BaseConfig_Dict = {}	#勇者试炼场基本配置{FBLevel:cfg,}
	DailyFB_PassReward_Dict = {}	#勇者试炼场通关奖励配置{FBLevel:{rangeId:cfg,},}
	DailyFB_PassReward_Range2ID_Dict = {}	#勇者试炼场通关奖励等级区段等级ID关联{rangeId:levelRange,}
	DailyFB_FightConfig_Dict = {}	#勇者试炼场战斗配置 {FBLevel:{roleLevel:cfg,},}
	
class DailyFBBase(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("DailyFBBase.txt")
	def __init__(self):
		self.FBLevel = int
		self.openCondition = self.GetEvalByString
		self.sweepNeedVIP = int
		self.passKillNum = int
		self.maxKillNum = int
	
	def CanJoin(self, role):
		#判断 是否可以进场 (月卡 or 年卡) and VIP 
		monthCardLimit, yearCardLimit, VIPLimite = self.openCondition
		if role.GetVIP() < VIPLimite:
			return False
		
		if (monthCardLimit or yearCardLimit):
			if Environment.EnvIsNA():
				if not (role.GetCD(EnumCD.Card_Month) or role.GetCD(EnumCD.Card_HalfYear) or role.GetCD(EnumCD.Card_Quarter) or role.GetCD(EnumCD.Card_Year)):
					return False
			else:
				if not ((monthCardLimit and role.GetCD(EnumCD.Card_Month)) or (yearCardLimit and role.GetCD(EnumCD.Card_HalfYear))): 
					return False
		return True
		
class DailyFBPassReward(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("DailyFBPassReward.txt")
	def __init__(self):
		self.FBLevel = int
		self.rangeId = int
		self.levelRange = self.GetEvalByString
		self.rewardMoney = int
		self.rewardItems = self.GetEvalByString

class DailyFBFight(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("DailyFBFight.txt")
	def __init__(self):
		self.FBLevel = int
		self.roleLevel = int
		self.addExp = int
		self.discountExp = int
		self.campId = int
		self.fightType = int
		self.totalExp = int
		self.ActaddExp = int
		self.ActdiscountExp = int
		self.ActtotalExp = int

def LoadDailyFBBase():
	global DailyFB_BaseConfig_Dict
	for cfg in DailyFBBase.ToClassType():
		FBLevel = cfg.FBLevel
		if FBLevel in DailyFB_BaseConfig_Dict:
			print "GE_EXC,repeat FBLevel(%s) in DailyFB_BaseConfig_Dict" % FBLevel
		DailyFB_BaseConfig_Dict[FBLevel] = cfg

def LoadDailyFBPassReward():
	global DailyFB_PassReward_Dict
	global DailyFB_PassReward_Range2ID_Dict
	for cfg in DailyFBPassReward.ToClassType():
		FBLevel = cfg.FBLevel
		rangeId = cfg.rangeId
		levelRange = cfg.levelRange
		#等级区段等级ID关联
		DailyFB_PassReward_Range2ID_Dict[rangeId] = levelRange
		#通关奖励配置
		passRewardDict = DailyFB_PassReward_Dict.setdefault(FBLevel,{})
		if rangeId in passRewardDict:
			print "GE_EXC,repeat rangeId(%s) in DailyFB_PassReward_Dict with FBLevel(%s)" % (rangeId, FBLevel)
		passRewardDict[rangeId] = cfg

def LoadDailyFBFight():
	global DailyFB_FightConfig_Dict
	for cfg in DailyFBFight.ToClassType():
		FBLevel = cfg.FBLevel
		roleLevel = cfg.roleLevel
		fightCfgDict = DailyFB_FightConfig_Dict.setdefault(FBLevel, {})
		if roleLevel in fightCfgDict:
			print "GE_EXC,repeat roleLevel(%s) in DailyFB_FightConfig_Dict with FBLevel(%s)" % (roleLevel, FBLevel)
		fightCfgDict[roleLevel] = cfg
		
def GetBaseCfgByFBLevel(FBLevel):
	'''
	获取对应FBLevel的基本配置
	'''
	return DailyFB_BaseConfig_Dict.get(FBLevel)
	
def GetPassRewardCfgByLevels(FBLevel, roleLevel):
	'''
	获取对应FB对应玩家等级的通关奖励配置
	'''
	rewardDict = DailyFB_PassReward_Dict.get(FBLevel)
	if not rewardDict:
		print "GE_EXC,GetPassRewardCfgByLevels::can not get rewardDict by FBLevel(%s)" % FBLevel
		return None
	
	tmpRangeId = 1
	for rangeId, levelRange in DailyFB_PassReward_Range2ID_Dict.iteritems():
		tmpRangeId = rangeId
		levelDown, levelUp = levelRange
		if levelDown <= roleLevel <= levelUp:
			break
	
	rewardCfg = rewardDict.get(tmpRangeId)
	if not rewardCfg:
		print "GE_EXC,GetPassRewardCfgByLevels::can not get rewardCfg by roleLevel(%s) and FBLevel(%s)" % (roleLevel, FBLevel)
		return None
	
	return rewardCfg

def GetFightCfgByLevels(FBLevel, roleLevel):
	'''
	获取对应FB对应玩家等级的战斗配置
	'''
	fightCfgDict = DailyFB_FightConfig_Dict.get(FBLevel)
	if not fightCfgDict:
		print "GE_EXC,GetFightCfgByLevels::can not get fightCfgDict by FBLevel(%s)" % FBLevel
		return None
	
	fightCfg = fightCfgDict.get(roleLevel)
	if not fightCfg:
		print "GE_EXC,GetFightCfgByLevels::can not get fightCfg by roleLevel(%s) and FBLevel(%s)" % (roleLevel, FBLevel)
		return None
	
	return fightCfg
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadDailyFBBase()
		LoadDailyFBPassReward()
		LoadDailyFBFight()