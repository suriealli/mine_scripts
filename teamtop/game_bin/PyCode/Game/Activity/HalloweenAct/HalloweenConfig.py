#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.HalloweenAct.HalloweenConfig")
#===============================================================================
# 万圣节活动配置
#===============================================================================
import Environment
import DynamicPath
from Util import Random
from Util.File import TabFile
from Game.Property import PropertyEnum

if "_HasLoad" not in dir():
	HALLOWEEN_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	HALLOWEEN_FILE_FOLDER_PATH.AppendPath("HalloweenAct")
	
	KILL_GHOST_DICT = {}	#击杀鬼配置
	COLLECT_CARD_DICT = {}	#收集配置
	OPEN_LIGHT_DICT = {}	#点灯配置
	TASK_REWARD_DICT = {}	#任务配置
	CARD_BUFF_DICT = {}		#变身卡buff
	CARD_CODING_LIST = []	#存变身卡的coding
	
class KillGhost(TabFile.TabLine):
	'''
	击杀鬼配置表
	'''
	FilePath = HALLOWEEN_FILE_FOLDER_PATH.FilePath("KillGhost.txt")
	def __init__(self):
		self.LevelRange	 = self.GetEvalByString
		self.unBindRMB	 = int
		self.gold		 = int
		self.killTimes	 = int
		self.reward		 = self.GetEvalByString
		
	def Precoding(self):
		self.RandomRate = Random.RandomRate()
		for item in self.reward:
			self.RandomRate.AddRandomItem(item[2], item)

			
class CollectCard(TabFile.TabLine):
	'''
	卡片收集配置
	'''
	FilePath = HALLOWEEN_FILE_FOLDER_PATH.FilePath("CollectCard.txt")
	def __init__(self):
		self.rewardId	 = int
		self.needCard	 = self.GetEvalByString
		self.reward		 = self.GetEvalByString
		self.IsBro		 = int

class OpenLight(TabFile.TabLine):
	'''
	点灯配置
	'''
	FilePath = HALLOWEEN_FILE_FOLDER_PATH.FilePath("OpenLight.txt")
	def __init__(self):
		self.index		 = int
		self.times		 = int
		self.unBindRMB	 = int
		
		self.LevelRang1	 = self.GetEvalByString
		self.reward1	 = self.GetEvalByString
		
		self.LevelRang2	 = self.GetEvalByString
		self.reward2	 = self.GetEvalByString
		
		self.extendReward= self.GetEvalByString
	
	def Procoding(self):
		if self.reward1:
			self.RandomRate1 = Random.RandomRate()
			for item in self.reward1:
				self.RandomRate1.AddRandomItem(item[2], item)
		if self.reward2:
			self.RandomRate2 = Random.RandomRate()
			for item in self.reward2:
				self.RandomRate2.AddRandomItem(item[2], item)
			
class HalloweenTask(TabFile.TabLine):
	'''
	任务配置
	'''
	FilePath = HALLOWEEN_FILE_FOLDER_PATH.FilePath("HalloweenTask.txt")
	def __init__(self):
		self.TaskId	 = int
		self.buffId	 = int
		self.reward	 = self.GetEvalByString
		
class CardBuff(TabFile.TabLine, PropertyEnum.PropertyRead):
	'''
	变身卡buff
	'''
	FilePath = HALLOWEEN_FILE_FOLDER_PATH.FilePath("CardBuff.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.buffId	 = int
		self.coding	 = int
		self.startTime = self.GetDatetimeByString
		self.endTime = self.GetDatetimeByString
		self.keepTime= int
	
def LoadKillGhost():
	global KILL_GHOST_DICT
	
	for cfg in KillGhost.ToClassType():
		if cfg.LevelRange in KILL_GHOST_DICT:
			print "GE_EXC,repeat LevelRange(%s) in LoadKillGhost" % cfg.LevelRange
		KILL_GHOST_DICT[cfg.LevelRange] = cfg
		cfg.Precoding()
	
def LoadCollectCard():
	global COLLECT_CARD_DICT
	
	for cfg in CollectCard.ToClassType():
		if cfg.rewardId in COLLECT_CARD_DICT:
			print "GE_EXC,repeat rewardId(%s) in LoadCollectCard" % cfg.rewardId
		COLLECT_CARD_DICT[cfg.rewardId] = cfg
	
def LoadOpenLight():
	global OPEN_LIGHT_DICT
	
	for cfg in OpenLight.ToClassType():
		if cfg.index in OPEN_LIGHT_DICT:
			print "GE_EXC,repeat index(%s) in openlight" % cfg.index
		OPEN_LIGHT_DICT[cfg.index] = cfg
		cfg.Procoding()
		
def LoadHalloweenTask():
	global TASK_REWARD_DICT
	
	for cfg in HalloweenTask.ToClassType():
		if cfg.TaskId in TASK_REWARD_DICT:
			print "GE_EXC,repeat TaskId(%s) in HalloweenTask" % cfg.TaskId
		TASK_REWARD_DICT[cfg.TaskId] = cfg
		
def LoadCardBuff():
	global CARD_BUFF_DICT
	global CARD_CODING_LIST
	for cfg in CardBuff.ToClassType():
		if cfg.buffId in CARD_BUFF_DICT:
			print "GE_EXC,repeat buffId(%s) in LoadCardBuff" % cfg.buffId
		CARD_BUFF_DICT[cfg.buffId] = cfg
		if cfg.coding not in CARD_CODING_LIST:
			CARD_CODING_LIST.append(cfg.coding)
		cfg.InitProperty()
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadKillGhost()
		LoadCollectCard()
		LoadOpenLight()
		LoadHalloweenTask()
		LoadCardBuff()
		