# -*- coding:UTF-8 -*-
#!/usr/bin/env python
# XRLAM("Game.JT.JTConfig")
#===============================================================================
# 跨服竞技场配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile
from Game.Property import PropertyEnum
from Game.Role.Mail import Mail


weeksender = "系统"
weektitle = "主题：跨服组队竞技场每周结算"
weekcontent = "内容：您的战队在跨服组队竞技场中获得%s战队积分，全服排名%s名，获得%s功勋"
weekcontent2 = "内容：您的战队在跨服组队竞技场中获得%s战队积分，全服排名大于2001名，获得%s功勋"


if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("JT")
	
	JTMedalConfigDict = {}			#勋章配置字典
	JTStoreConfigDict = {}			#荣誉(金券)兑换商店配置字典
	JTSToreRefreshConfigDict = {}	#兑换商店刷新配置字典 
	JTSRConfigDict = {}				#争霸赛全服奖励
	
	
	############################################################
	#新版配置
	JTDayRewardDict = {}
	WeekReward_IntKey_Dict = {}
	WeekReward_TupleKey_Dict = {}
	JTGradeDict = {}
	WeekRewardRank = 3000
	MinGradeMinScore = 1250 #最小的积分，低于这个就没段位
	MaxGradeConfig = None
	MaxUnRankGradeConfig = None
	#战斗积分计算参数配置
	JTScoreKEList = []
	JTScoreMWinList = []
	JTScoreMLoseList = []
	#段位称号
	JTGradeTitleSet = set()
	#争霸赛奖励
	JT_ZB_Reward = {}
	############################################################


def GetWeekRewardConfig(rank):
	if rank > WeekRewardRank:
		#最大排名奖励
		rank = WeekRewardRank
	global WeekReward_IntKey_Dict, WeekReward_TupleKey_Dict
	intcfg = WeekReward_IntKey_Dict.get(rank)
	if intcfg:
		return intcfg
	for rankTuple, cfg, in WeekReward_TupleKey_Dict.iteritems():
		if rankTuple[0] <= rank <= rankTuple[1]:
			return cfg
	return None

def GetLoginGrade(teamScore):
	#逻辑进程计算不在排行榜上面的战队的段位
	if teamScore <= MinGradeMinScore:
		return 0
	nowgradeconfig = MaxUnRankGradeConfig
	for _ in range(len(JTGradeDict)):
		if teamScore >= nowgradeconfig.minScore:
			return nowgradeconfig.grade
		nowgradeconfig = JTGradeDict.get(nowgradeconfig.grade -1)
		if not nowgradeconfig:
			return 0
	return 0


###########################################################################
#勋章
class JTMedalConfig(TabFile.TabLine, PropertyEnum.PropertyRead):
	FilePath = FILE_FOLDER_PATH.FilePath("jtmedal.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.level = int
		self.needJTexp = int
		self.crystalPostion = eval

class JTStoreConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("jtstore.txt")
	def __init__(self):
		self.idx = int
		self.type = int
		self.code = int
		self.price = int
		self.needteampoint = int
		self.needselfpoint = int
		self.limitcnt = int


class JTStorerefreshConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("jtstoreRefresh.txt")
	def __init__(self):
		self.refreshCnt = int
		self.needJTGold = int
	

class JTSRConfig(TabFile.TabLine):
	SRFP = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	SRFP.AppendPath("JTGroup")
	FilePath = SRFP.FilePath("jtallreward.txt")
	def __init__(self):
		self.rewardType = int
		self.item = self.GetEvalByString
###########################################################################

#日结奖励
class JTDayRewardConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("JTDayRewardNew.txt")
	def __init__(self):
		self.grade = int
		self.rongyu = int
		self.gongxun = int

#周结奖励
class JTWeekRewardConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("JTWeekReward.txt")
	def __init__(self):
		self.rank = self.GetEvalByString
		self.rongyu = int
		self.gongxun = self.GetEvalByString
		self.items = self.GetEvalByString
	
	def IsIntReward(self, flag):
		self.intflag = flag
		#功勋=（S-a）*（n-m）/(b-a)+m
		if flag is False:
			self.a = self.rank[0]
			self.b = self.rank[1]
			
			self.wm = self.gongxun[0]
			self.wn = self.gongxun[1]
			self.wparam = 1.0 * (self.wn - self.wm) / (self.b - self.a)

	def Reward(self, roleId, rank, teamScore):
		if self.intflag:
			realgongxun = self.gongxun
		else:
			realgongxun = int(self.wn - (rank - self.a) * self.wparam)
		if rank < 2001:
			Mail.SendMail(roleId, weektitle, weeksender, weekcontent % (teamScore, rank, realgongxun), items = self.items, jtgold = self.rongyu, jtexp = realgongxun)
		else:
			Mail.SendMail(roleId, weektitle, weeksender, weekcontent2 % (teamScore, realgongxun), items = self.items, jtgold = self.rongyu, jtexp = realgongxun)
#段位配置
class JTGradeConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("JTGrade.txt")
	def __init__(self):
		self.grade = int
		self.score = self.GetEvalByString
		self.name = str
		self.needrank = int
		self.titleId = int
		
	def Preprocess(self):
		self.minScore = self.score[0]


class JTScoreKEConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("JTScoreKE.txt")
	def __init__(self):
		self.teamScore = int
		self.K = int
		self.E = int

class JTScoreMConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("JTScoreM.txt")
	def __init__(self):
		self.teamScore = int
		self.M_win = int
		self.M_lose = int

class JTZBReward(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("JTZBReward.txt")
	def __init__(self):
		self.groupId = int
		self.rank = int
		self.itemRewards = self.GetEvalByString
		self.titleId = int
############################################################################
#旧配置
############################################################################
def LoadJTMedalConfig():
	global JTMedalConfigDict
	for config in JTMedalConfig.ToClassType():
		if config.level in JTMedalConfigDict:
			print "GE_EXC, repeat config.level(%s) in JTMedalConfigDict" % config.level
		config.InitProperty()
		JTMedalConfigDict[config.level] = config


def LoadJTStoreConfig():
	global JTStoreConfigDict
	for config in JTStoreConfig.ToClassType():
		if config.idx in JTStoreConfigDict:
			print "GE_EXC,repeat config.idx(%s) in JTStoreConfigDict" % config.idx
		JTStoreConfigDict[config.idx] = config


def LoadJTStoreRefreshConfig():
	global JTSToreRefreshConfigDict
	for config in JTStorerefreshConfig.ToClassType():
		if config.refreshCnt in JTSToreRefreshConfigDict:
			print "GE_EXC,repeat refreshCnt(%s) in JTSToreRefreshConfigDict" % config.refreshCnt
		JTSToreRefreshConfigDict[config.refreshCnt] = config


def LoadJTSRConfigDict():
	#跨服争霸服务器奖励
	global JTSRConfigDict
	for config in JTSRConfig.ToClassType():
		JTSRConfigDict[config.rewardType] = config.item

def GetSRItem(rewardType, index = 0):
	#1	初级冠军全服奖励   2	初级亚军全服奖励   3	初级季军全服奖励
	#4	精锐冠军全服奖励   5	精锐亚军全服奖励   6	精锐季军全服奖励
	#7	巅峰冠军全服奖励   8	巅峰亚军全服奖励   9	巅峰季军全服奖励
	if rewardType == 1:
		if index == 1:
			return JTSRConfigDict.get(1)
		if index == 2:
			return JTSRConfigDict.get(2)
		if index == 3:
			return JTSRConfigDict.get(3)
	if rewardType == 2:
		if index == 1:
			return JTSRConfigDict.get(4)
		if index == 2:
			return JTSRConfigDict.get(5)
		if index == 3:
			return JTSRConfigDict.get(6)
	if rewardType == 3:
		if index == 1:
			return JTSRConfigDict.get(7)
		if index == 2:
			return JTSRConfigDict.get(8)
		if index == 3:
			return JTSRConfigDict.get(9)
	return None

############################################################################
#新版配置
############################################################################
def LoadDayRewardConfig():
	global JTDayRewardDict
	for config in JTDayRewardConfig.ToClassType():
		if config.grade in JTDayRewardDict:
			print "GE_EXC,repeat grade(%s) in LoadDayRewardConfig" % config.grade
		JTDayRewardDict[config.grade] = config


def LoadWeekRewardConfig():
	global WeekReward_IntKey_Dict, WeekReward_TupleKey_Dict, WeekRewardRank
	for cfg in JTWeekRewardConfig.ToClassType():
		if type(cfg.rank) == type(1):
			WeekReward_IntKey_Dict[cfg.rank] = cfg
			cfg.IsIntReward(True)
			continue
		start, end = cfg.rank
		if end == -1:
			WeekRewardRank = start
			WeekReward_IntKey_Dict[start] = cfg
			cfg.IsIntReward(True)
		else:
			WeekReward_TupleKey_Dict[(start, end)] = cfg
			cfg.IsIntReward(False)

def LoadGradeConfig():
	#注意这个Config对象被多个地方hold住的，reload时需要注意处理各种逻辑
	global JTGradeDict, MaxGradeConfig, MinGradeMinScore
	global JTGradeTitleSet
	for config in JTGradeConfig.ToClassType():
		if config.grade in JTGradeDict:
			print "GE_EXC,repeat grade(%s) in LoadGradeConfig" % config.grade
		JTGradeDict[config.grade] = config
		config.Preprocess()
		#最小的积分，低于这个就没段位
		MinGradeMinScore = min(MinGradeMinScore, config.score[0])
		JTGradeTitleSet.add(config.titleId)
	#最高的段位
	MaxGradeConfig = JTGradeDict.get(max(JTGradeDict.keys()))
	global MaxUnRankGradeConfig
	MaxUnRankGradeConfig = MaxGradeConfig
	#找出最高的不用排名限制的段位配置,用于本服段位更新
	for _ in range(len(JTGradeDict)):
		if MaxUnRankGradeConfig.needrank:
			MaxUnRankGradeConfig = JTGradeDict.get(MaxUnRankGradeConfig.grade - 1)
			if not MaxUnRankGradeConfig:
				print "GE_EXC LoadGradeConfig MaxUnRankGradeConfig error"
			continue
		break
	

def LoadJTScoreKEConfig():
	global JTScoreKEList
	for config in JTScoreKEConfig.ToClassType():
		JTScoreKEList.append((config.teamScore, config.K, config.E))
		
def LoadJTScoreMConfig():
	global JTScoreMWinList, JTScoreMLoseList
	for config in JTScoreMConfig.ToClassType():
		JTScoreMWinList.append((config.teamScore, config.M_win))
		JTScoreMLoseList.append((config.teamScore, config.M_lose))

def LoadJTZBReward():
	global JT_ZB_Reward
	
	for cfg in JTZBReward.ToClassType():
		key = (cfg.groupId, cfg.rank)
		if key in JT_ZB_Reward:
			print "GE_EXC,repeat JT_ZB_ReWard groupId(%s) and rank(%s) in LoadJTZBReward" % (cfg.groupId, cfg.rank)
			continue
		JT_ZB_Reward[key] = cfg
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadJTMedalConfig()
		LoadJTStoreConfig()
		LoadJTSRConfigDict()
		LoadJTStoreRefreshConfig()
		
		LoadDayRewardConfig()
		LoadWeekRewardConfig()
		LoadGradeConfig()
		LoadJTScoreKEConfig()
		LoadJTScoreMConfig()
		LoadJTZBReward()
		