#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.DeepHell.DeepHellConfig")
#===============================================================================
# 深渊炼狱 config
#===============================================================================
import time
import random
import datetime
import cProcess
import cDateTime
import cComplexServer
import Environment
import DynamicPath
from World import Define
from Util.File import TabFile
from Game.Role import Event


if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("DeepHell")
	
	# 深渊炼狱 活动时间配置 {activeIndex:cfg,}
	DeepHell_ActiveConfig_Dict = {}	
	#深渊炼狱 房间配置 {roomID:cfg,}
	DeepHell_RoomConfig_Dict = {}	
	#深渊炼狱 战区类型 {areaType:levelrange,}
	DeepHell_AreaType_Dict = {}	
	#深渊炼狱 塔层配置 {floorIndex:cfg,}
	DeepHell_FloorConfig_Dict = {}
	#深渊炼狱 怪物类型集合
	DeepHell_MonsterType_Set = set()	
	#深渊炼狱 塔层奖励 {roomAreaType:{floorIndex:cfg,},}
	DeepHell_FloorReward_Dict = {}	
	#深渊炼狱 积分排名奖励 {roomAreaType:{rank:cfg,},}
	DeepHell_ScoreRankReward_Dict = {}	
	#深渊炼狱 角色头顶状态{stateId:killRange,}
	DeepHell_RoleState_Dict = {}
	

#===============================================================================
# 活动时间控制
#===============================================================================
class DeepHellActive(TabFile.TabLine):
	'''
	深渊炼狱 活动时间控制
	'''
	FilePath = FILE_FLODER_PATH.FilePath("DeepHellActive.txt")
	def __init__(self):
		self.activeIndex = int
		self.activeName = str
		self.beginTime = self.GetEvalByString
		self.initTime = self.GetEvalByString
		self.endTime = self.GetEvalByString
	

	def init_active(self, isCross = False):
		'''
		注册触发逻辑
		'''
		activeIndex = self.activeIndex
		beginTime = int(time.mktime(datetime.datetime(*self.beginTime).timetuple()))
		initTime = int(time.mktime(datetime.datetime(*self.initTime).timetuple()))
		endTime = int(time.mktime(datetime.datetime(*self.endTime).timetuple()))
		nowTime = cDateTime.Seconds()
		
		processModule = None
		if isCross:
			from Game.DeepHell import DeepHellCross
			processModule = DeepHellCross
			#跨服开始倒计时比本服多了1分钟  and 结束后倒计时1分钟 + 20S保护时间确保先结算完毕
			endTime += 120
		else:
			from Game.DeepHell import DeepHellMgr
			processModule = DeepHellMgr
		
		
		#活动图标时间控制
		if beginTime <= nowTime < endTime:
			#激活
			processModule.OpenActive(None, activeIndex)
			cComplexServer.RegTick(endTime - nowTime, processModule.CloseActive, activeIndex)
		elif nowTime < beginTime:
			#注册一个tick激活
			cComplexServer.RegTick(beginTime - nowTime, processModule.OpenActive, activeIndex)
			cComplexServer.RegTick(endTime - nowTime, processModule.CloseActive)
			
		#活动真正开始控制
		if nowTime < initTime:
			cComplexServer.RegTick(initTime - nowTime, processModule.InitActive, activeIndex)
		
		
def LoadDeepHellActive(isCross = False):
	'''
	加载 深渊炼狱 活动时间 配置
	'''
	global DeepHell_ActiveConfig_Dict
	for cfg in DeepHellActive.ToClassType():
		activeIndex = cfg.activeIndex
		if activeIndex in DeepHell_ActiveConfig_Dict:
			print "GE_EXC,repeat activeIndex(%s) in DeepHell_ActiveConfig_Dict" % activeIndex
		initTime = int(time.mktime(datetime.datetime(*cfg.initTime).timetuple()))
		endTime = int(time.mktime(datetime.datetime(*cfg.endTime).timetuple()))
		if endTime - initTime < 40 * 60:
			print "GE_EXC,Deep Hell Config error, endTime too early"
		DeepHell_ActiveConfig_Dict[activeIndex] = cfg


#===============================================================================
# 房间配置
#===============================================================================
class DeepHellRoom(TabFile.TabLine):
	'''
	深渊炼狱 房间配置
	'''
	FilePath = FILE_FLODER_PATH.FilePath("DeepHellRoom.txt")
	def __init__(self):
		self.roomID = int
		self.roomAreaType = int
		self.levelRange = self.GetEvalByString
		self.expectRoleCnt = int
		self.nextRoomID = int
		self.sceneList = self.GetEvalByString


def LoadDeepHellRoom():
	'''
	加载 深渊炼狱 房间配置
	'''
	global DeepHell_AreaType_Dict
	global DeepHell_RoomConfig_Dict
	for cfg in DeepHellRoom.ToClassType():
		roomID = cfg.roomID
		if roomID in DeepHell_RoomConfig_Dict:
			print "GE_EXC,repeat roomID(%s) in DeepHell_RoomConfig_Dict" % roomID
		DeepHell_RoomConfig_Dict[roomID] = cfg
		#战区
		DeepHell_AreaType_Dict[cfg.roomAreaType] = cfg.levelRange
	
	
def GetAreaTypeByLevel(roleLevel):
	'''
	返回 roleLevel 对应所属战区类型
	'''
	areaType = 1
	for tAreaType, levelRange in DeepHell_AreaType_Dict.iteritems():
		areaType = tAreaType
		if levelRange[0] <= roleLevel <= levelRange[1]:
			break
	
	return areaType



#===============================================================================
# 塔层配置
#===============================================================================
class DeepHellFloor(TabFile.TabLine):
	'''
	深渊炼狱 塔层配置
	'''
	FilePath = FILE_FLODER_PATH.FilePath("DeepHellFloor.txt")
	def __init__(self):
		self.floorIndex = int
		self.nextFloorIndex = int
		self.lastFloorIndex = int
		self.maxKillCnt = int
		self.crashKillCnt = int
		self.killBaseScore = int
		self.killAddScore = int
		self.crashRate = int
		self.noCrashNeedRMB = int
		self.monsterRefreshInterval = int
		self.monsterList = self.GetEvalByString
		self.reviewAreaList = self.GetEvalByString
	
	def random_review_pos(self):
		'''
		随机塔层出生点
		@return: pos_x,pos_y
		'''
		reviewArea = self.reviewAreaList[random.randint(0, len(self.reviewAreaList) - 1)]
		return random.randint(reviewArea[0], reviewArea[2]), random.randint(reviewArea[1], reviewArea[3])


def LoadDeepHellFloor():
	'''
	加载 深渊炼狱 塔层配置
	'''
	global DeepHell_MonsterType_Set
	global DeepHell_FloorConfig_Dict
	for cfg in DeepHellFloor.ToClassType():
		floorIndex = cfg.floorIndex
		if floorIndex in DeepHell_FloorConfig_Dict:
			print "GE_EXC,repeat floorIndex(%s) in DeepHell_FloorConfig_Dict" % floorIndex
		if len(cfg.reviewAreaList) < 1:
			print "GE_EXC,LoadDeepHellFloor:: config error no reviewAreaList"
		DeepHell_FloorConfig_Dict[floorIndex] = cfg
		
		for monster in cfg.monsterList:
			DeepHell_MonsterType_Set.add(monster[0])
		

def GetMonsterInfoByFloorIndex(floorIndex):
	'''
	获取塔层怪物列表
	'''
	monsterList = []
	refreshInterval = 0
	floorCfg = DeepHell_FloorConfig_Dict.get(floorIndex, None)
	if floorCfg:
		monsterList = floorCfg.monsterList
		refreshInterval = floorCfg.monsterRefreshInterval
	
	return refreshInterval, monsterList


#===============================================================================
# 塔层奖励配置
#===============================================================================
class DeepHellFloorReward(TabFile.TabLine):
	'''
	深渊炼狱 塔层奖励
	'''
	FilePath = FILE_FLODER_PATH.FilePath("DeepHellFloorReward.txt")
	def __init__(self):
		self.roomAreaType = int
		self.floorIndex = int
		self.rewardItems = self.GetEvalByString


def LoadDeepHellFloorReward():
	'''
	加载 深渊炼狱 塔层奖励
	'''
	global DeepHell_FloorReward_Dict
	for cfg in DeepHellFloorReward.ToClassType():
		roomAreaType = cfg.roomAreaType
		floorIndex = cfg.floorIndex
		areaFloorDict = DeepHell_FloorReward_Dict.setdefault(roomAreaType, {})
		if floorIndex in areaFloorDict:
			print "GE_EXC,repeat floorIndex(%s) with roomAreaType(%s) in DeepHell_FloorReward_Dict" % (floorIndex, roomAreaType)
		areaFloorDict[floorIndex] = cfg


def GetFloorRewardByTypeAndIndex(roomType, floorIndex):
	'''
	返回 塔层奖励list
	''' 
	rewardConfigDict = DeepHell_FloorReward_Dict.get(roomType, None)
	if not rewardConfigDict:
		return []
	
	rewardCfg = rewardConfigDict.get(floorIndex, None)
	if not rewardCfg:
		return []
	
	return rewardCfg.rewardItems	
		

#===============================================================================
# 积分排名配置
#===============================================================================
class DeepHellScoreRank(TabFile.TabLine):
	'''
	 深渊炼狱 积分排名奖励
	'''
	FilePath = FILE_FLODER_PATH.FilePath("DeepHellScoreRank.txt")
	def __init__(self):
		self.roomAreaType = int
		self.rankIndex = int
		self.rankInterval = self.GetEvalByString
		self.rewardItems = self.GetEvalByString


def LoadDeepHellScoreRank():
	'''
	加载 深渊炼狱 积分排名奖励
	'''
	global DeepHell_ScoreRankReward_Dict
	for cfg in DeepHellScoreRank.ToClassType():
		roomAreaType = cfg.roomAreaType
		areaRankDict = DeepHell_ScoreRankReward_Dict.setdefault(roomAreaType,{})
		rankDown, rankUp = cfg.rankInterval
		for rank in xrange(rankDown, rankUp + 1):
			if rank in areaRankDict:
				print "GE_EXC,repeat rank(%s) with roomAreaType(%s) in DeepHell_ScoreRankReward_Dict" % (rank, roomAreaType)
			areaRankDict[rank] = cfg


def GetRankRewardByTypeAndRank(roomType, rank):
	'''
	获取对应房间ID 的 排名奖励道具list
	'''
	rewardConfigDict = DeepHell_ScoreRankReward_Dict.get(roomType, None)
	if not rewardConfigDict:
		return []
	
	rewardCfg = rewardConfigDict.get(rank, None)
	if not rewardCfg:
		return []
	
	return rewardCfg.rewardItems	


#===============================================================================
# 头顶状态配置
#===============================================================================
class DeepHellState(TabFile.TabLine):
	'''
	深渊炼狱状态
	'''
	FilePath = FILE_FLODER_PATH.FilePath("DeepHellState.txt")
	def __init__(self):
		self.statusId = int
		self.isFightStatus = int
		self.killRange = self.GetEvalByString


def LoadDeepHellState():
	'''
	加载 深渊炼狱状态
	'''
	global DeepHell_RoleState_Dict
	for cfg in DeepHellState.ToClassType():
		statusId = cfg.statusId
		if statusId in DeepHell_RoleState_Dict:
			print "GE_EXC, repeat stateId(%s) in " % statusId
		
		if not 130 <= statusId <= 170:
			print "GE_EXC,LoadDeepHellState, stateId(%s) out of range" % statusId
			
		DeepHell_RoleState_Dict[statusId] = cfg


def GetStateByKillCnt(killCnt, isFightStatus):
	'''
	获取对应击杀数的头顶状态
	'''
	tStatusId = 0
	for statusId, cfg in DeepHell_RoleState_Dict.iteritems():
		if not tStatusId:
			tStatusId = statusId
		if cfg.isFightStatus == isFightStatus and cfg.killRange[0] <= killCnt <= cfg.killRange[1]:
			return statusId
	
	#异常 返回第一个状态
	return tStatusId
		
		
def LoadConfig():
	'''
	加载所有配置
	'''
	#加载时间控制
	LoadDeepHellActive(Environment.IsCross)
	#加载房间配置
	LoadDeepHellRoom()
	#加载塔层配置
	LoadDeepHellFloor()
	#加载 塔层奖励
	LoadDeepHellFloorReward()
	#加载 积分排名奖励
	LoadDeepHellScoreRank()
	#加载 深渊炼狱状态
	LoadDeepHellState()
	

def AfterLoadWD(callArgvs = None, regParams = None):
	'''
	世界数据载回之后 加载配置
	'''
	#本服 or 默认跨服 处理就好了
	if not Environment.IsCross or cProcess.ProcessID == Define.GetDefaultCrossID():
		for cfg in DeepHell_ActiveConfig_Dict.values():
			cfg.init_active(Environment.IsCross)
	else:
		pass
	

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadConfig()
		#加载活动时间控制
		Event.RegEvent(Event.Eve_AfterLoadWorldData, AfterLoadWD)		