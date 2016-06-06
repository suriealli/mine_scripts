#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DoubleEleven.DETopicConfig")
#===============================================================================
# 双十一2015 专题转盘  config
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Util import Random

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("DoubleEleven")
	
	CIRCULAR_FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	CIRCULAR_FILE_FLODER_PATH.AppendPath("CircularActive")
	
	#活动控制配置
	DETopicActive_cfg = None
	
	#专题转盘基本配置 {topicId:cfg,}
	DETopic_BaseConfig_Dict = {}

	#专题转盘控制配置 {dayIndex:{levelRangeId:cfg,},}
	DETopic_ControlConfig_Dict = {}
	

class DETopicBase(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("DETopicBase.txt")
	def __init__(self):
		self.topicId = int
		self.oneNeedRMB = int
		self.tenNeedRMB = int
		self.needRMBType = int
		self.dayMaxLotteryCnt = int
		self.rewardPool =self.GetEvalByString
	
	def pre_precess(self):
		'''
		组装抽奖随机器
		'''
		self.randomObj = Random.RandomRate()
		for itemIndex ,coding, cnt, rateValue,isPrecious in self.rewardPool:
			tInfo = [self.topicId, itemIndex, coding, cnt, isPrecious]
			self.randomObj.AddRandomItem(rateValue, tInfo)
	

def LoadDETopicBase():
	global DETopic_BaseConfig_Dict
	for cfg in DETopicBase.ToClassType():
		topicId = cfg.topicId
		if topicId in DETopic_BaseConfig_Dict:
			print "GE_EXC,repeat topicId(%s) in DETopic_BaseConfig_Dict" % topicId
		cfg.pre_precess()
		DETopic_BaseConfig_Dict[topicId] = cfg


class DETopicControl(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("DETopicControl.txt")
	def __init__(self):
		self.dayIndex = int
		self.levelRangeId = int
		self.levelRange = self.GetEvalByString
		self.topicId = int


def LoadDETopicControl():
	global DETopic_ControlConfig_Dict
	for cfg in DETopicControl.ToClassType():
		dayIndex = cfg.dayIndex
		levelRangeId = cfg.levelRangeId
		dayIndexDict = DETopic_ControlConfig_Dict.setdefault(dayIndex, {})
		if levelRangeId in dayIndexDict:
			print "GE_EXC, repeat levelRangeId(%s) in DETopic_ControlConfig_Dict with dayIndex(%s)" % (levelRangeId, dayIndex)
		dayIndexDict[levelRangeId] = cfg
	
def GetTopicCfgDayIndexAndLevel(dayIndex, roleLevel):
	'''
	获取 天数索引dayIndex  和 玩家等级 roleLevel 对应开启的专题转盘
	'''
	tCfg = None
	dayIndexDict = DETopic_ControlConfig_Dict.get(dayIndex, {})
	for _, cfg in dayIndexDict.iteritems():
		levelDown, levelUp = cfg.levelRange
		if levelDown <= roleLevel <= levelUp:
			tCfg = cfg
			break
	return tCfg


def GetTopicIdByDayAndLevel(dayIndex, roleLevel):
	'''
	获取 天数dayIndex 和 玩家等级roleLevel 对应开启专题ID 
	'''
	topicCfg = GetTopicCfgDayIndexAndLevel(dayIndex, roleLevel)
	if not topicCfg:
		print "GE_EXC,DETopicConfig::GetTopicIdByDayAndLevel:: can not find topic config by dayIndex(%s) and roleLevel(%s)" % (dayIndex, roleLevel)
		return 1
	else:
		return topicCfg.topicId
	
class DETopicActive(TabFile.TabLine):
	FilePath = CIRCULAR_FILE_FLODER_PATH.FilePath("DETopicActive.txt")
	def __init__(self):
		self.activeIndex = int
		self.activeName = str
		self.beginTime = self.GetDatetimeByString
		self.endTime = self.GetDatetimeByString
		self.totalDay = int
	
def LoadDETopicActive():
	'''
	加载并启动活动
	'''
	global DETopicActive_cfg
	for cfg in DETopicActive.ToClassType():
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in DETopicActive_cfg"
			continue
		DETopicActive_cfg = cfg
			

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadDETopicBase()
		LoadDETopicControl()
		LoadDETopicActive()