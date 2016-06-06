#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.KuaFuJJC.KuaFuJJCConfig")
#===============================================================================
# 跨服个人竞技场配置
#===============================================================================
import datetime
import cComplexServer
import cDateTime
import cRoleMgr
import DynamicPath
import Environment
from Common.Message import AutoMessage
from Game.Role import Event
from Game.SysData import WorldData
from Util.File import TabFile

KUAFU_JJC_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
KUAFU_JJC_FILE_FOLDER_PATH.AppendPath("KuaFuJJC")

if "_HasLoad" not in dir():
	ELECTION_CHALLENGE_DATA_OBJ_IDX = 2		#海选挑战数据Obj索引
	FINALS_CHALLENGE_DATA_OBJ_IDX = 3		#决赛挑战数据Obj索引
	UNION_SCORE_REWARD_OBJ_IDX = 4			#公会积分奖励Obj索引
	
	IS_START = False		#跨服竞技场是否开启
	KUAFU_JJC_DAY = 0		#当前是跨服竞技场第几天
	DAYS_BEFORE_START = 0	#距离活动开启还有多少天
	
	KUAFU_JJC_SCENE_ID = 375		#跨服竞技场场景ID
	ROLE_ELECTION_RANK_CNT = 100	#个人海选积分排行数量
	UNION_ELECTION_RANK_CNT = 15	#公会海选积分排行数量
	ROLE_FINALS_RANK_CNT = 100		#个人决赛积分排行数量
	
	ELECTION_START_TIME = datetime.time(12,0)
	ELECTION_END_TIME = datetime.time(21,55)
	FINALS_START_TIME = datetime.time(22,0)
	FINALS_END_TIME = datetime.time(22,30)
	GUESS_START_TIME = datetime.time(8,0)
	GUESS_END_TIME = datetime.time(21,59)
	
	KUAFU_JJC_ZONE = {}					#跨服个人竞技场区域
	KUAFU_JJC_ACTIVE_CONFIG = None		#跨服个人竞技场激活配置
	KUAFU_JJC_ELECTION_ROUND = {}		#跨服个人竞技场海选轮数
	KUAFU_JJC_FINALS_ROUND = {}			#跨服个人竞技场决赛轮数
	KUAFU_JJC_GROUP = {}				#跨服个人竞技场分组
	LAST_GROUP_ID = 0					#最后一组ID
	KUAFU_JJC_BUY_CNT = {}				#跨服个人竞技场购买次数
	KUAFU_JJC_UNION_RANK_REWARD = {}	#跨服个人竞技场海选公会排行奖励
	KUAFU_JJC_FINALS_RANK_REWARD = {}	#跨服个人竞技场决赛排行奖励
	KUAFU_JJC_UNION_SCORE_REWARD = {}	#跨服个人竞技场公会积分奖励
	
	#消息
	KuaFu_JJC_Sync_Day = AutoMessage.AllotMessage("KuaFu_JJC_Sync_Day", "通知客户端同步跨服竞技场活动天数")
	
#===============================================================================
# 配置表对象
#===============================================================================
class KuaFuJJCActive(TabFile.TabLine):
	FilePath = KUAFU_JJC_FILE_FOLDER_PATH.FilePath("KuaFuJJCActive.txt")
	def __init__(self):
		self.startDate = self.GetEvalByString	#第一次开启的日期
		self.durationDays = int					#开启持续天数
		self.circularDays = int					#结束后隔多少天会重新开启
		
	def CheckOpen(self):
		'''
		检查开启
		'''
		global IS_START
		global KUAFU_JJC_DAY
		global DAYS_BEFORE_START
		
		#当前日期
		nowDate = cDateTime.Now().date()
		#第一次开启的日期
		startDate = datetime.datetime(*self.startDate)
		#循环开启周期天数 = 活动持续天数 + 结束后到下一次开启的天数
		cycleDays = self.durationDays + self.circularDays
		#开启日期到当前日期过了多少天
		overDays = (nowDate - startDate.date()).days
		
		if overDays == 0:
			#正好是开启的日期
			IS_START = True
			KUAFU_JJC_DAY = 1
		elif overDays < 0:
			#还没到活动开启时间
			KUAFU_JJC_DAY = 0
			DAYS_BEFORE_START = -overDays
		else:
			#当前日期比第一次开启日期大，这个活动已经开启过一次或者多次
			#计算已经进行的循环次数的跨越天数
			circularpassDays = overDays / cycleDays * cycleDays
			#计算当前天处于最近的一个循环周期中的天数
			start_overdays = overDays - circularpassDays
			if start_overdays < self.durationDays:
				#属于开启期内，需要马上开启,并且计算结束天数
				IS_START = True
				KUAFU_JJC_DAY = start_overdays + 1
			else:
				#处于等待开启时间段,计算还有多少天要开启
				nextOpendays = cycleDays - start_overdays
				DAYS_BEFORE_START = nextOpendays
				
				
class KuaFuJJCZone(TabFile.TabLine):
	'''
	跨服个人竞技场区域
	'''
	FilePath = KUAFU_JJC_FILE_FOLDER_PATH.FilePath("KuaFuJJCZone.txt")
	def __init__(self):
		self.zoneId = int
		self.kaiFuDaysInterval = self.GetEvalByString
		
class KuaFuJJCElectionRound(TabFile.TabLine):
	'''
	跨服个人竞技场海选轮数
	'''
	FilePath = KUAFU_JJC_FILE_FOLDER_PATH.FilePath("KuaFuJJCElectionRound.txt")
	def __init__(self):
		self.roundId = int
		self.opponentCnt = int
		self.rewardItem = self.GetEvalByString
		self.needReset = int
		
class KuaFuJJCFinalsRound(TabFile.TabLine):
	'''
	跨服个人竞技场决赛轮数
	'''
	FilePath = KUAFU_JJC_FILE_FOLDER_PATH.FilePath("KuaFuJJCFinalsRound.txt")
	def __init__(self):
		self.roundId = int
		self.opponentCnt = int
		self.rewardItem = self.GetEvalByString
		self.needReset = int
		
class KuaFuJJCGroup(TabFile.TabLine):
	'''
	跨服个人竞技场分组
	'''
	FilePath = KUAFU_JJC_FILE_FOLDER_PATH.FilePath("KuaFuJJCGroup.txt")
	def __init__(self):
		self.groupId = int
		self.groupName = str
		self.rankInterval = self.GetEvalByString
		self.groupLen = int
		
class KuaFuJJCBuyCnt(TabFile.TabLine):
	'''
	跨服个人竞技场购买次数
	'''
	FilePath = KUAFU_JJC_FILE_FOLDER_PATH.FilePath("KuaFuJJCBuyCnt.txt")
	def __init__(self):
		self.cnt = int
		self.needKuaFuMoney = int
		
class KuaFuJJCUnionRankReward(TabFile.TabLine):
	'''
	跨服个人竞技场海选公会排行奖励
	'''
	FilePath = KUAFU_JJC_FILE_FOLDER_PATH.FilePath("KuaFuJJCUnionRankReward.txt")
	def __init__(self):
		self.rank = int
		self.rewardItem = self.GetEvalByString
		
class KuaFuJJCFinalsRankReward(TabFile.TabLine):
	'''
	跨服个人竞技场决赛排行奖励
	'''
	FilePath = KUAFU_JJC_FILE_FOLDER_PATH.FilePath("KuaFuJJCFinalsRankReward.txt")
	def __init__(self):
		self.rank = int
		self.rewardItem = self.GetEvalByString
		self.rewardTitleId = int
		
class KuaFuJJCUnionScoreReward(TabFile.TabLine):
	'''
	跨服个人竞技场公会积分奖励
	'''
	FilePath = KUAFU_JJC_FILE_FOLDER_PATH.FilePath("KuaFuJJCUnionScoreReward.txt")
	def __init__(self):
		self.rewardId = int
		self.score = int
		self.rewardItem = self.GetEvalByString
		self.rewardMoney = int
		
#===============================================================================
# 读取配置表
#===============================================================================
def LoadKuaFuJJCActive():
	global KUAFU_JJC_ACTIVE_CONFIG
	for config in KuaFuJJCActive.ToClassType():
		KUAFU_JJC_ACTIVE_CONFIG = config
		
def LoadKuaFuJJCZone():
	global KUAFU_JJC_ZONE
	for config in KuaFuJJCZone.ToClassType():
		KUAFU_JJC_ZONE[config.zoneId] = config
		
def LoadKuaFuJJCElectionRound():
	global KUAFU_JJC_ELECTION_ROUND
	for config in KuaFuJJCElectionRound.ToClassType():
		KUAFU_JJC_ELECTION_ROUND[config.roundId] = config
		
def LoadKuaFuJJCFinalsRound():
	global KUAFU_JJC_FINALS_ROUND
	for config in KuaFuJJCFinalsRound.ToClassType():
		KUAFU_JJC_FINALS_ROUND[config.roundId] = config
		
def LoadKuaFuJJCGroup():
	global KUAFU_JJC_GROUP
	global LAST_GROUP_ID
	for config in KuaFuJJCGroup.ToClassType():
		KUAFU_JJC_GROUP[config.groupId] = config
		if config.groupId > LAST_GROUP_ID:
			LAST_GROUP_ID = config.groupId
			
def LoadKuaFuJJCBuyCnt():
	global KUAFU_JJC_BUY_CNT
	for config in KuaFuJJCBuyCnt.ToClassType():
		KUAFU_JJC_BUY_CNT[config.cnt] = config
		
def LoadKuaFuJJCUnionRankReward():
	global KUAFU_JJC_UNION_RANK_REWARD
	for config in KuaFuJJCUnionRankReward.ToClassType():
		KUAFU_JJC_UNION_RANK_REWARD[config.rank] = config
		
def LoadKuaFuJJCFinalsRankReward():
	global KUAFU_JJC_FINALS_RANK_REWARD
	for config in KuaFuJJCFinalsRankReward.ToClassType():
		KUAFU_JJC_FINALS_RANK_REWARD[config.rank] = config
		
def LoadKuaFuJJCUnionScoreReward():
	global KUAFU_JJC_UNION_SCORE_REWARD
	for config in KuaFuJJCUnionScoreReward.ToClassType():
		KUAFU_JJC_UNION_SCORE_REWARD[config.rewardId] = config

#===============================================================================
# 事件
#===============================================================================
def AfterLoadWorldData(param1, param2):
	#载入世界数据之后,处理所有的循环活动
	KUAFU_JJC_ACTIVE_CONFIG.CheckOpen()

#===============================================================================
# 时间
#===============================================================================
def AfterNewDay():
	global IS_START
	global KUAFU_JJC_DAY
	global DAYS_BEFORE_START
	
	if IS_START is True:
		#活动正在开启中
		if KUAFU_JJC_DAY > 0 and KUAFU_JJC_DAY < KUAFU_JJC_ACTIVE_CONFIG.durationDays:
			KUAFU_JJC_DAY += 1
		elif KUAFU_JJC_DAY == KUAFU_JJC_ACTIVE_CONFIG.durationDays:
			#第7天跨天，活动结束
			IS_START = False
			KUAFU_JJC_DAY = 0
			DAYS_BEFORE_START = KUAFU_JJC_ACTIVE_CONFIG.durationDays
			#版本号+1
			WorldData.SetKuaFuJJCVersionId(WorldData.GetKuaFuJJCVersionId() + 1)
	else:
		if DAYS_BEFORE_START > 0:
			DAYS_BEFORE_START -= 1
			if DAYS_BEFORE_START == 0:
				#活动开启
				IS_START = True
				KUAFU_JJC_DAY = 1
	
	#通知所有人
	for role in cRoleMgr.GetAllRole():
		SyncKuaFuJJCDay(role)
		
#===============================================================================
# 接口
#===============================================================================
def IsFinals():
	if KUAFU_JJC_DAY == 7:
		return True
	return False

def CanJoinKuaFuJJCScene():
	if IS_START is False:
		return False
	
	t = cDateTime.Now().time()
	if KUAFU_JJC_DAY == 1:
		#第一天不能进入
		return False
	elif KUAFU_JJC_DAY >= 2 and KUAFU_JJC_DAY <= 6:
		#判断海选活动时间
		if t < ELECTION_START_TIME or t > ELECTION_END_TIME:
			return False
	elif KUAFU_JJC_DAY == 7:
		#判断决赛活动时间
		if t < FINALS_START_TIME or t > FINALS_END_TIME:
			return False
		
	return True

def CanGuess():
	t = cDateTime.Now().time()
	if t < GUESS_START_TIME or t > GUESS_END_TIME:
		return False
	
	return True

#===============================================================================
# Sync Client
#===============================================================================
def SyncKuaFuJJCDay(role):
	if WorldData.GetWorldKaiFuDay() - KUAFU_JJC_DAY + 1 < 10:
		#和谐跨服不足10天的服务器看不到活动图标
		role.SendObj(KuaFu_JJC_Sync_Day, (0, DAYS_BEFORE_START))
	else:
		#活动当前是第几天，距离下次活动开启还有几天
		role.SendObj(KuaFu_JJC_Sync_Day, (KUAFU_JJC_DAY, DAYS_BEFORE_START))
	
				
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadKuaFuJJCActive()
		LoadKuaFuJJCZone()
		LoadKuaFuJJCElectionRound()
		LoadKuaFuJJCFinalsRound()
		LoadKuaFuJJCGroup()
		LoadKuaFuJJCBuyCnt()
		LoadKuaFuJJCUnionRankReward()
		LoadKuaFuJJCFinalsRankReward()
		LoadKuaFuJJCUnionScoreReward()
		
		#事件
		Event.RegEvent(Event.Eve_AfterLoadWorldData, AfterLoadWorldData)
		#每日调用
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
		
		
		