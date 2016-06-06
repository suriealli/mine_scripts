#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.DragonKnightChallenge.DKCNewConfig")
#===============================================================================
# 新龙骑试炼config
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile
from Util import Random

IDX_INDEX = 2

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("DragonKnightChallenge")
	
	DKCNEW_BASECONFIG_DICT = {}	#新龙骑试炼基本配置{DKCLevel:cfg,}
	
	DKCNEW_REWARDCONFIG_DICT = {} #新龙骑试炼奖励配置  {DKCLevel:{rewardPoolId:cfg,},}
	DKCNEW_RANDOMOBJ_DICT = {}	#新龙骑试炼 奖励随机器 {DKCLevel:{rewardPoolId:randomObj,},}
	

class DKCNewBase(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("DKCNewBase.txt")
	def __init__(self):
		self.DKCLevel = int
		self.levelName = str
		self.campId = int
		self.fightType = int
	

def LoadDKCNewBase():
	global DKCNEW_BASECONFIG_DICT
	for cfg in DKCNewBase.ToClassType():
		DKCLevel = cfg.DKCLevel
		if DKCLevel in DKCNEW_BASECONFIG_DICT:
			print "GE_EXC,repeat DKCLevel(%s) in DKCNEW_BASECONFIG_DICT" % DKCLevel
		DKCNEW_BASECONFIG_DICT[DKCLevel] = cfg



class DKCNewReward(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("DKCNewReward.txt")
	def __init__(self):
		self.DKCLevel = int
		self.rewardPoolId = int
		self.rateValue = int
		self.rewardItems = self.GetEvalByString
	
	def pre_process(self):
		self.rewardItemsDict = {}
		for idx, coding, cnt in self.rewardItems:
			self.rewardItemsDict[idx] = [coding, cnt]
	
	
def LoadDKCNewReward():
	global DKCNEW_REWARDCONFIG_DICT 
	global DKCNEW_RANDOMOBJ_DICT
	for cfg in DKCNewReward.ToClassType():
		DKCLevel = cfg.DKCLevel
		rewardPoolId = cfg.rewardPoolId
		rewardItems = cfg.rewardItems
		
		cfg.pre_process()
		
		DKCLevelDict_1 = DKCNEW_REWARDCONFIG_DICT.setdefault(DKCLevel, {})
		if rewardPoolId in DKCLevelDict_1:
			print "GE_EXC, repeat rewardPoolId(%s) with DKCLevel(%s) in DKCNEW_REWARDCONFIG_DICT" % (rewardPoolId, DKCLevel)
		DKCLevelDict_1[rewardPoolId] = cfg
	
	
		DKCLevelDict_2 = DKCNEW_RANDOMOBJ_DICT.setdefault(DKCLevel, {})
		if rewardPoolId in DKCLevelDict_2:
			print "GE_EXC,repeat rewardPoolId(%s) with DKCLevel(%s) in DKCNEW_RANDOMOBJ_DICT" % (rewardPoolId, DKCLevel)
		randomObj = Random.RandomRate()
		for idx, coding, cnt in rewardItems:
			#里面是等概率 随便弄个概率1就是了
			randomObj.AddRandomItem(1, [DKCLevel, rewardPoolId, idx, coding, cnt])
		DKCLevelDict_2[rewardPoolId] = randomObj


def GetRandomObjByLevelAndState(DKCLevel, stateDict):
	'''
	根据关卡 和 对应宝箱状态 返回抽奖随机器
	@param DKCLevel: 关卡
	@param stateDict: 宝箱状态{rewardPoolId:[idx,state],}  
	'''
	randomObj = Random.RandomRate()
	for rewardPoolId , stateData in stateDict.iteritems():
		idx, pos = stateData
		#潜规则  pos>表示已经抽取了的
		if not pos:
			rewardCfg = (DKCNEW_REWARDCONFIG_DICT.get(DKCLevel, {})).get(rewardPoolId, None)
			if not rewardCfg:
				continue
			
			rateValue = rewardCfg.rateValue
			coding, cnt = rewardCfg.rewardItemsDict.get(idx)
			randomObj.AddRandomItem(rateValue, [DKCLevel, rewardPoolId, idx, coding, cnt])
	
	return randomObj	

def GetRandomDictByLevel(DKCLevel):
	'''
	返回对应DKCLevel 的随机奖励字典
	'''
	rewardDict = {}
	for rewardPoolId, randomObj in DKCNEW_RANDOMOBJ_DICT.get(DKCLevel, {}).iteritems():
		rewardDict[rewardPoolId] = [randomObj.RandomOne()[IDX_INDEX], 0]
		
	return rewardDict

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadDKCNewBase()
		LoadDKCNewReward()

