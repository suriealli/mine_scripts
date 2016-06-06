#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.LianChongRebate.LianChongRebateConfig")
#===============================================================================
# 连充返利 Config
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("LianChongRebate")
	
	#等级区段 和 奖励项达标天次区段 
	LianChong_DayRange_Dict = {}		#完成天数段ID-天数区段 关联 {dayRangeId:dayRange,}	
	LianChong_LevelRange_Dict = {}		#等级段ID-等级段 关联{levelRangeId:levelRange,}
	
	#当日充值条件 和 奖励
	LianChong_Reward_Dict = {}			#连充奖励 :{rewardType:{levelRangeId:{dayRangeId:cfg,},},}
	LianChong_RewardCondition_Dict = {}	#当日充值返利项达标条件{rewardType:needRMB,}	
	
	#累计充值 解锁奖励条件 和 奖励
	LianChong_Unlock_Dict = {}			#累计充值天次奖励解锁条件{rewardType:{rewardLevel:needBuyTimes,},}	
	LianChong_UnlockReward_Dict = {}	#累计充值解锁奖励{rewardType:{rewardLevel:{levelRangeId:cfg,},},}
	

#### 奖励项达标天次区段
class LianChongDayRange(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("LianChongDayRange.txt")
	def __init__(self):
		self.dayRangeId = int
		self.dayRange = self.GetEvalByString
		
def GetDayRangeIdByTimes(boughtTimes):
	'''
	根据次数 返回次数所在区段的ID
	'''
	retDayRangeId = 0
	for dayRangeId, dayRange in LianChong_DayRange_Dict.iteritems():
		retDayRangeId = dayRangeId
		dayRangeDown, dayRangeUp = dayRange
		if dayRangeDown <= boughtTimes <= dayRangeUp:
			break
	
	return retDayRangeId

#### 等级区段
class LianChongLevelRange(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("LianChongLevelRange.txt")
	def __init__(self):
		self.levelRangeId = int 
		self.levelRange = self.GetEvalByString

def GetLevelRangeIdByLevel(roleLevel):
	'''
	根据等级返回 等级对应所在区段的ID
	'''
	retLevelRangeId = 0
	for levelRangeId, levelRange in LianChong_LevelRange_Dict.iteritems():
		retLevelRangeId = levelRangeId
		levelRangeDown, levelRangeUp = levelRange
		if levelRangeDown <= roleLevel <= levelRangeUp:
			break
	
	return retLevelRangeId

#### 每日充值返利项奖励
class LianChongReward(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("LianChongReward.txt")
	def __init__(self):
		self.rewardType = int
		self.levelRangeId = int
		self.dayRangeId = int
		self.rewardItems = self.GetEvalByString

def GetLianChongRewardCfg(rewardType, roleLevel, buyTimes):
	'''
	获取 rewardType, levelRangeId, dayRangeId对应的奖励配置
	'''
	levelRangeId = GetLevelRangeIdByLevel(roleLevel)
	if not levelRangeId:
		return None
	
	dayRangeId = GetDayRangeIdByTimes(buyTimes)
	if not dayRangeId:
		return None
	
	rewardTypeDict = LianChong_Reward_Dict.get(rewardType)
	if not rewardTypeDict:
		return None
	
	levelRangeDict = rewardTypeDict.get(levelRangeId)
	if not levelRangeDict:
		return None
	
	rewardCfg = levelRangeDict.get(dayRangeId)
	return rewardCfg

#### 每日充值返利项达成条件
class LianChongRewardCondition(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("LianChongRewardCondition.txt")
	def __init__(self):
		self.rewardType = int
		self.needBuyRMB = int
	
	def isSatisify(self, role):
		'''
		根据玩家数据 判断是否满足对应项
		'''
		if role.GetDayBuyUnbindRMB_Q() < self.needBuyRMB:
			return False
		else:
			return True

#### 累计充值 解锁奖励条件		
class LianChongUnlock(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("LianChongUnlock.txt")
	def __init__(self):
		self.rewardType = int
		self.rewardLevel = int
		self.needBuyTimes = int
	
def GetUnLockCfgByTypeAndLevel(rewardType, rewardLevel):
	'''
	获取 rewardType, rewardLevel 对应 needBuyTimes
	'''
	rewardTypeDict = LianChong_Unlock_Dict.get(rewardType)
	if not rewardTypeDict:
		return None
	
	if rewardLevel not in rewardTypeDict:
		return None
	else:
		return rewardTypeDict[rewardLevel]
	
#### 累计充值达标项奖励
class LianChongUnlockReward(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("LianChongUnlockReward.txt")
	def __init__(self):
		self.rewardType = int
		self.rewardLevel = int
		self.levelRangeId = int
		self.rewardItem = self.GetEvalByString

def GetUnlockRewardCfg(rewardType, rewardLevel, roleLevel):
	'''
	获取 rewardType, rewardLevel, levelRangeId对应的奖励配置
	'''
	rewardTypeDict = LianChong_UnlockReward_Dict.get(rewardType)
	if not rewardTypeDict:
		return None
	
	rewardLevelDict = rewardTypeDict.get(rewardLevel)
	if not rewardLevelDict:
		return None
	
	unlockRewardCfg = rewardLevelDict.get(GetLevelRangeIdByLevel(roleLevel))
	return unlockRewardCfg

## 加载配置
def LoadLianChongDayRange():
	global LianChong_DayRange_Dict
	for cfg in LianChongDayRange.ToClassType():
		dayRangeId = cfg.dayRangeId
		dayRange = cfg.dayRange
		if dayRangeId in LianChong_DayRange_Dict:
			print "GE_EXC, repeat dayRangeId(%s) in LianChong_DayRange_Dict" % dayRangeId
		LianChong_DayRange_Dict[dayRangeId] = dayRange

def LoadLianChongLevelRange():
	global LianChong_LevelRange_Dict
	for cfg in LianChongLevelRange.ToClassType():
		levelRangeId = cfg.levelRangeId
		levelRange = cfg.levelRange
		if levelRangeId in LianChong_LevelRange_Dict:
			print "GE_EXC, repeat levelRangeId(%s) in LianChong_LevelRange_Dict" % levelRangeId
		LianChong_LevelRange_Dict[levelRangeId] = levelRange

def LoadLianChongReward():
	global LianChong_Reward_Dict
	for cfg in LianChongReward.ToClassType():
		rewardType = cfg.rewardType
		levelRangeId = cfg.levelRangeId
		dayRangeId = cfg.dayRangeId
		rewardTypeDict = LianChong_Reward_Dict.setdefault(rewardType, {})
		levelRangeIdDict = rewardTypeDict.setdefault(levelRangeId, {})
		if dayRangeId in levelRangeIdDict:
			print "GE_EXC, repeat dayRangeId(%s) in LianChong_Reward_Dict with rewardType(%s) and levelRangeId(%s)" % (dayRangeId, rewardType, levelRangeId)
		levelRangeIdDict[dayRangeId] = cfg

def LoadLianChongRewardCondition():
	global LianChong_RewardCondition_Dict
	for cfg in LianChongRewardCondition.ToClassType():
		rewardType = cfg.rewardType
		needBuyRMB = cfg.needBuyRMB
		if rewardType in LianChong_RewardCondition_Dict:
			print "GE_EXC,repeat rewardType(%s) in LianChong_RewardCondition_Dict" % rewardType
		LianChong_RewardCondition_Dict[rewardType] = needBuyRMB

def LoadLianChongUnlock():
	global LianChong_Unlock_Dict
	for cfg in LianChongUnlock.ToClassType():
		rewardType = cfg.rewardType
		rewardLevel = cfg.rewardLevel
		needBuyTimes = cfg.needBuyTimes
		rewardTypeDict = LianChong_Unlock_Dict.setdefault(rewardType, {})
		if rewardLevel in rewardTypeDict:
			print "GE_EXC,repeat rewardLevel(%d) in LianChong_Unlock_Dict with rewardType(%s) " % (rewardLevel, rewardType)
		rewardTypeDict[rewardLevel] = needBuyTimes

def LoadLianChongUnlockReward():
	global LianChong_UnlockReward_Dict
	for cfg in LianChongUnlockReward.ToClassType():
		rewardType = cfg.rewardType
		rewardLevel = cfg.rewardLevel
		levelRangeId = cfg.levelRangeId
		rewardTypeDict = LianChong_UnlockReward_Dict.setdefault(rewardType, {})
		rewardLevelDict = rewardTypeDict.setdefault(rewardLevel, {})
		if levelRangeId in rewardLevelDict:
			print "GE_EXC,repeat levelRangeId(%s) in LianChong_UnlockReward_Dict with rewardType(%s) and rewardLeve(%s)" % (levelRangeId, rewardType, rewardLevel)
		rewardLevelDict[levelRangeId] = cfg

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadLianChongDayRange()
		LoadLianChongLevelRange()
		LoadLianChongReward()
		LoadLianChongRewardCondition()
		LoadLianChongUnlock()
		LoadLianChongUnlockReward()