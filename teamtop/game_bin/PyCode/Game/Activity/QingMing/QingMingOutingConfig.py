#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.QingMing.QingMingOutingConfig")
#===============================================================================
# 清明踏青 Config
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Util import Random

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("QingMing")
	
	QMO_LotteryRange2ID_Dict = {}		#清明踏青翻牌 等级段ID-等级段 关联 {levelRangeId:levelRange,}
	QMO_LotteryRandomObj_Dict = {}		#清明踏青翻牌 奖励随机器 {levelRangeId:randomObj,} randomList->[rateValue,(rewardId,coding, cnt,isPrecious)]
	
	QMO_UnlockRange2ID_Dict = {}		#清明踏青累计翻牌次数解锁奖励    等级段ID-等级段 关联 {levelRangeId:levelRange,}
	QMO_UnlockReward_Dict = {}			#清明踏青累计翻牌次数解锁奖励 配置 {rewardIndex:{levelRangeId:cfg,},}
	
class QingMingOutingLottery(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("QingMingOutingLottery.txt")
	def __init__(self):
		self.rewardId = int
		self.levelRangeId = int
		self.levelRange = self.GetEvalByString
		self.rewardItem = self.GetEvalByString
		self.rateValue = int
		self.isPrecious = int

def GetRadomObjByLevel(roleLevel):
	'''
	获取对应等级的抽奖随机器
	'''
	tmpLevelRangeId = 0
	for levelRangeId, levelRange in QMO_LotteryRange2ID_Dict.iteritems():
		levelDown, levelUp = levelRange
		tmpLevelRangeId = levelRangeId
		if levelDown <= roleLevel <= levelUp:
			break
	
	if tmpLevelRangeId in QMO_LotteryRandomObj_Dict:
		return QMO_LotteryRandomObj_Dict[tmpLevelRangeId]
	else:
		return None

class QingMingOutingUnlockReward(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("QingMingOutingUnlockReward.txt")
	def __init__(self):
		self.rewardIndex = int
		self.levelRangeId = int
		self.levelRange = self.GetEvalByString
		self.rewardItems = self.GetEvalByString
		self.needValue = int

def GetUnlockRewardCfgByLevel(roleLevel, rewardIndex):
	'''
	获取对应等级 对应rewardIndex的解锁奖励配置
	'''
	tmpLevelRangeId = 0
	for levelRangeId, levelRange in QMO_UnlockRange2ID_Dict.iteritems():
		levelDown, levelUp = levelRange
		tmpLevelRangeId = levelRangeId
		if levelDown <= roleLevel <= levelUp:
			break
	
	rewardIndexDict = QMO_UnlockReward_Dict.get(rewardIndex)
	if not rewardIndexDict:
		return None
	
	if tmpLevelRangeId in rewardIndexDict:
		return rewardIndexDict[tmpLevelRangeId]
	else:
		return None
		
def LoadQingMingOutingLottery():
	global QMO_LotteryRange2ID_Dict
	global QMO_LotteryRandomObj_Dict
	for cfg in QingMingOutingLottery.ToClassType():
		rewardId = cfg.rewardId
		levelRangeId = cfg.levelRangeId
		levelRange = cfg.levelRange
		coding, cnt = cfg.rewardItem
		rateValue = cfg.rateValue
		isPrecious = cfg.isPrecious
		
		QMO_LotteryRange2ID_Dict[levelRangeId] = levelRange
		
		randomObj = QMO_LotteryRandomObj_Dict.setdefault(levelRangeId, Random.RandomRate())
		randomObj.AddRandomItem(rateValue,[rewardId, coding, cnt, isPrecious])

def LoadQingMingOutingUnlockReward():
	global QMO_UnlockRange2ID_Dict
	global QMO_UnlockReward_Dict
	for cfg in QingMingOutingUnlockReward.ToClassType():
		rewardIndex = cfg.rewardIndex
		levelRangeId = cfg.levelRangeId
		levelRange = cfg.levelRange
		
		QMO_UnlockRange2ID_Dict[levelRangeId] = levelRange
		
		rewardIndexDict = QMO_UnlockReward_Dict.setdefault(rewardIndex, {})
		if levelRangeId in rewardIndexDict:
			print "GE_EXC,repeat levelrangeId(%s) in QMO_UnlockReward_Dict with rewardIndex(%s)" % (levelRangeId, rewardIndex)
		rewardIndexDict[levelRangeId] = cfg

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadQingMingOutingLottery()
		LoadQingMingOutingUnlockReward()		