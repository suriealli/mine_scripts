#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.LatestActivity.LatestActivityConfig")
#===============================================================================
# 最新活动配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	LATEST_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	LATEST_FILE_FOLDER_PATH.AppendPath("LatestActivity")
	
	ACT_BASE_DICT = {}			#基础配置
	ACT_REWARD_DICT = {}		#奖励配置
	ACT_TASK_DICT = {}			#活跃度任务配置
	ACT_TASK_ID_SET = set()		#活跃度活动id集合
	CHECK_CODING_SET = set()	#需要监听的道具
	
class LatestActBase(TabFile.TabLine):
	'''
	最新活动基础配置表
	'''
	FilePath = LATEST_FILE_FOLDER_PATH.FilePath("LatestActBase.txt")
	def __init__(self):
		self.actId		= int
		self.kaifuDay	= int
		self.startKaifu	= self.GetEvalByString
		self.daytick	= int
		self.rewardList	= self.GetEvalByString
		self.checkCoding= int

class LatestActReward(TabFile.TabLine):
	'''
	最新活动奖励配置
	'''
	FilePath = LATEST_FILE_FOLDER_PATH.FilePath("LatestActReward.txt")
	def __init__(self):
		self.rewardId	 = int
		self.needLevel	 = int
		self.dayGettimes = int
		self.mountEvolve = int
		self.StarGirlStar= int
		self.mountGrade	 = int
		self.needFillRMB_D= int
		self.needConsumeRMB = int
		self.needItem	 = self.GetEvalByString
		self.needPetStarNum = int
		self.needPetGrade= int
		self.wingLevel	 = int
		self.dragonGrade = int
		self.washCnt = int
		self.zhanHunStar = int
		self.StationSoulLevel = int
		self.HallowsCnt = int
		self.rewardTarot = int
		self.rewardItems = self.GetEvalByString
		self.bindRMB	 = int
		self.money		 = int
		self.TempBless	 = self.GetEvalByString
		self.activityScore = int				#活跃度
	
def LoadLatestActBase():
	global ACT_BASE_DICT
	global CHECK_CODING_SET
	
	for cfg in LatestActBase.ToClassType():
		if cfg.actId in ACT_BASE_DICT:
			print "GE_EXC,repeat actId(%s) in LoadLatestActBase" % cfg.actId
		ACT_BASE_DICT[cfg.actId] = cfg
		if cfg.checkCoding:
			CHECK_CODING_SET.add(cfg.checkCoding)
		
		
def LoadLatestActReward():
	global ACT_REWARD_DICT
	
	for cfg in LatestActReward.ToClassType():
		if cfg.rewardId in ACT_REWARD_DICT:
			print "GE_EXC, repeat rewardId(%s) in LoadLatestActReward" % cfg.rewardId
		ACT_REWARD_DICT[cfg.rewardId] = cfg
		
class LatestActActivityTask(TabFile.TabLine):
	'''
	最新活动活跃度配置
	'''
	FilePath = LATEST_FILE_FOLDER_PATH.FilePath("TaskConfig.txt")
	def __init__(self):
		self.actId	= int
		self.index	= int
		self.score= int
		self.max_cnt= int
		self.consume = int				#消费任务
		self.fill = int					#充值任务
	
def LoadLatestActActivityTask():
	global ACT_TASK_DICT
	
	for cfg in LatestActActivityTask.ToClassType():
		if (cfg.actId, cfg.index) in ACT_BASE_DICT:
			print "GE_EXC,repeat actId(%s), index(%s) in LoadLatestActActivityTask" % (cfg.actId, cfg.index)
		ACT_TASK_DICT[(cfg.actId, cfg.index)] = cfg
		ACT_TASK_ID_SET.add(cfg.actId)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadLatestActBase()
		LoadLatestActReward()
		LoadLatestActActivityTask()
	
		
