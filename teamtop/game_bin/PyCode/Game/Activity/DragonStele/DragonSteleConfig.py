#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DragonStele.DragonSteleConfig")
#===============================================================================
# 龙魂石碑配置
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("DragonStele")
	
	#龙魂石碑奖励类型-等级区段 关联 {rewardType:{rangeId:levelRange,},}
	#通过 祈祷类型 和 玩家等级 获取rewardType和rangeId 再找到奖励随机器中的randomer
	DRAGON_STELE_REWARD_TYPE_RANGE = {}	
	
	#龙魂石碑奖励随机器{rewardType:{rangeId:randomer}} 
	#randomer表示该类型该等级区段下的奖励池随机器-[rate,(rewardId, rewardType, rangeId, coding, cnt, itemType, isPrecious)]
	DRAGON_STELE_REWARD_RANDOMER = {}
	
	#副本 & 英灵神殿 掉落龙币配置
	DRAGONSTELE_DROP_CONFIG_DICT = {}	

class DragonSteleReward(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("DragonSteleReward.txt")
	def __init__(self):
		self.rewardId = int		#奖励ID
		self.rewardType = int	#奖励类型（1-普通祈祷 2-高级祈祷 3-额外奖励）
		self.rangeId = int		#等级区段ID 
		self.levelRange = self.GetEvalByString	#等级区段
		self.item = self.GetEvalByString		#（coding,cnt,itemType）
		self.rate = int		#概率
		self.isPrecious = int	#是否珍稀

class DragonSteleDrop(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("DragonSteleDrop.txt")
	def __init__(self):
		self.activityType = int 
		self.fightIdx = int 
		self.dropRate = int 
		self.proCoding = int

def GetRandomOne(rewardType = 1,roleLevel = 1):
	'''
	根据奖励类型和玩家等级 随机奖励项
	@param rewardType:奖励类型1、2、3
	@param roleLevel:万家等级
	@return: randomer
	'''
	rangeDict = DRAGON_STELE_REWARD_TYPE_RANGE.get(rewardType, None)
	if not rangeDict:
		print "GE_EXC,cannot get rangeDict with rewardType(%s)" % rewardType
		return None
	
	tmpRangeId = 1
	for rangId, levelRange in rangeDict.iteritems():
		tmpRangeId = rangId
		levelDown, levelUp = levelRange
		if levelDown <= roleLevel and roleLevel <= levelUp:
			break
	
	randomerDict = DRAGON_STELE_REWARD_RANDOMER.get(rewardType, None)
	if not randomerDict:
		print "GE_EXC,can not get randomerDict with rewardType(%s)" % rewardType
		return None
	
	return randomerDict.get(tmpRangeId, None)

def LoadDragonSteleReward():
	global DRAGON_STELE_REWARD_RANDOMER
	global DRAGON_STELE_REWARD_TYPE_RANGE
	for cfg in DragonSteleReward.ToClassType():
		rewardId = cfg.rewardId
		rewardType = cfg.rewardType
		rangeId = cfg.rangeId
		levelRange = cfg.levelRange
		randomRate = cfg.rate
		coding, cnt, itemType = cfg.item
		isPrecious = cfg.isPrecious
		
		if rewardType == 1 or rewardType == 2 or rewardType == 3:
			#装载奖励生成器
			randomerDict = DRAGON_STELE_REWARD_RANDOMER.setdefault(rewardType,{})
			if rangeId not in randomerDict:
				randomerDict[rangeId] = Random.RandomRate()
			randomerDict[rangeId].AddRandomItem(randomRate, (rewardId, rewardType, rangeId, coding, cnt, itemType, isPrecious))
		
			#奖励关联器
			typeRangeDict = DRAGON_STELE_REWARD_TYPE_RANGE.setdefault(rewardType,{})
			if rangeId not in typeRangeDict:
				typeRangeDict[rangeId] = levelRange
		else:
			print "GE_EXC,error rewardType(%s) in dragon stele config" % rewardType

def LoadDragonSteleDrop():
	global DRAGONSTELE_DROP_CONFIG_DICT
	for cfg in DragonSteleDrop.ToClassType():
		DRAGONSTELE_DROP_CONFIG_DICT[(cfg.activityType, cfg.fightIdx)] = cfg
			
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadDragonSteleReward()
		LoadDragonSteleDrop()