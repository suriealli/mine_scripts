#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Union.UnionConfig")
#===============================================================================
# 公会配置
#===============================================================================
import DynamicPath
import Environment
from Common.Other import GlobalPrompt
from Game.Property import PropertyEnum
from Util import Random
from Util.File import TabFile
from Game.Role import Event

UNION_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
UNION_FILE_FOLDER_PATH.AppendPath("Union")

if "_HasLoad" not in dir():
	UNION_BASE = {}				#公会基础
	UNION_JOB = {}				#公会职位
	UNION_DAY_BOX = {}			#公会每日宝箱
	UNION_ACHIEVEMENT_BOX = {}	#公会成就宝箱
	UNION_TREASURE_GET = {}		#公会夺宝领取宝箱
	UNION_TREASURE_ROB = {}		#公会夺宝夺取宝箱
	UNION_GOD = {}				#公会魔神
	UNION_FB_BASE = {}			#公会副本基础
	UNION_FB_BUY_CNT = {}		#公会副本购买次数
	UNION_FB_MONSTER = {}		#公会副本怪物
	
	UNION_TASK = {}						#公会任务
	UNION_TASK_LEVEL_RANDOM_DICT = {}	#公会任务等级随机
	UNION_TASK_REWARD_FACTOR = {}		#公会任务奖励系数
	
	UNION_LEVEL_MAX = 0			#公会最大等级
	UNION_FB_ID_MAX = 0			#公会副本最大ID
	UNION_GODID_MAX = 0			#公会魔神最大ID
	UNION_POPULATION_MIN = 0	#公会最小人口
	
	UnionShenShouFeedDict = {}	#公会神兽喂养配置字典
	UnionShenShouLevelDict = {} #公会神兽等级配置字典
	UnionGoodConfigDict = {}	#公会普通商品配置字典
	UnionShenShouGoodDict = {}	#公会神兽掉落商品配置字典
	UnionSkillConfigDict = {}	#公会技能配置字典
	UnionShenShouBufDict = {}	#公会神兽buf(祝福)配置字典
	UnionShenShouHurtRankCfgDict = {} #公会神兽伤害排行奖励配置字典
	
	UnionMagicTowerDict = {}	#公会魔法塔配置字典
	UnionShenShouTanDict = {}	#公会神兽坛配置字典
	UnionStoreDict = {}			#公会商店配置字典 
	
	UNION_EXPLORE_EVENT = {}				#公会魔域探秘事件
	UNION_EXPLORE_BUY_CNT = {}				#公会魔域探秘购买行动力
	UNION_EXPLORE_QUESTION = {}				#公会魔域探秘答题
	UNION_EXPLORE_MONSTER = {}				#公会魔域探秘怪物
	UNION_EXPLORE_PRISONER_OUTPUT_LIST = []	#公会魔域探秘战俘列表
	UNION_EXPLORE_QUESTION_REWARD = {}		#公会魔域探秘答题奖励
	UNION_EXPLORE_MONSTER_REWARD = {}		#公会魔域探秘打怪物奖励
	UNION_EXPLORE_TREASURE_REWARD = {}		#公会魔域探秘宝箱奖励
	UNION_EXPLORE_PRISONER_REWARD = {}		#公会魔域探秘抓战俘奖励
	
	UNION_EXPLORE_EVENT_RANDOM_OBJ = Random.RandomRate()#公会魔域探秘事件随机对象
	
class UnionBase(TabFile.TabLine):
	'''
	公会基础配置
	'''
	FilePath = UNION_FILE_FOLDER_PATH.FilePath("UnionBase.txt")
	def __init__(self):
		self.level = int
		self.levelUpNeedExp = int
		self.population = int
		
class Job(TabFile.TabLine):
	'''
	职位配置表
	'''
	FilePath = UNION_FILE_FOLDER_PATH.FilePath("Job.txt")
	def __init__(self):
		self.jobId = int
		self.jobName = str
		self.jobMaxCnt = int
		self.recruit = int
		self.kickOut = int
		self.notice = int
		self.allotJob = int
		self.buildingLevelUp = int
		self.skillResearch = int
		self.shenshouUpGrade = int
		self.goodActivate = int
		self.callShenShou = int
		
class DayBox(TabFile.TabLine):
	'''
	每日宝箱配置表
	'''
	FilePath = UNION_FILE_FOLDER_PATH.FilePath("DayBox.txt")
	def __init__(self):
		self.level = int
		self.needContribution = int
		self.money = int
		self.item = self.GetEvalByString
		self.money_fcm = int                          #金币奖励防沉迷
		self.item_fcm = self.GetEvalByString          #物品奖励防沉迷
		
class AchievementBox(TabFile.TabLine):
	'''
	成就宝箱配置表
	'''
	FilePath = UNION_FILE_FOLDER_PATH.FilePath("AchievementBox.txt")
	def __init__(self):
		self.level = int
		self.devote = int
		self.money = int
		self.bindRMB = int
		self.item = self.GetEvalByString
		self.money_fcm = int                          #金币奖励 防沉迷
		self.bindRMB_fcm = int                        #魔晶奖励 防沉迷
		self.item_fcm = self.GetEvalByString          #物品奖励 防沉迷
		
class God(TabFile.TabLine):
	'''
	公会魔神配置表
	'''
	FilePath = UNION_FILE_FOLDER_PATH.FilePath("God.txt")
	def __init__(self):
		self.godId = int
		self.godName = str
		self.godCampId = int
		self.rewardMoney = int
		self.rewardItemList = self.GetEvalByString
		self.rewardMoney_fcm = int                    #通关金币奖励
		self.rewardItemList_fcm = self.GetEvalByString#通关物品奖励
		
class TreasureGet(TabFile.TabLine):
	'''
	公会夺宝领取宝箱配置表
	'''
	FilePath = UNION_FILE_FOLDER_PATH.FilePath("TreasureGet.txt")
	def __init__(self):
		self.boxType = int
		self.level = int
		self.money = int
		self.money_fcm = int                          #金币防沉迷
		
class TreasureRob(TabFile.TabLine):
	'''
	公会夺宝夺取宝箱配置表
	'''
	FilePath = UNION_FILE_FOLDER_PATH.FilePath("TreasureRob.txt")
	def __init__(self):
		self.boxType = int
		self.level = int
		self.money = int
		self.itemList = self.GetEvalByString
		self.money_fcm = int                          #金币防沉迷
		self.itemList_fcm = self.GetEvalByString      #物品防沉迷
		
class UnionFBBase(TabFile.TabLine):
	'''
	公会副本基础配置表
	'''
	FilePath = UNION_FILE_FOLDER_PATH.FilePath("UnionFBBase.txt")
	def __init__(self):
		self.fbId = int
		self.sceneId = int
		self.defaultPos = self.GetEvalByString
		self.fightType = int
		self.eliteName = str
		self.eliteNpcType = int
		self.elitePos = self.GetEvalByString
		self.eliteCampId = int
		self.rewardItemList = self.GetEvalByString
		self.rewardMoney = int
		self.rewardItemList_fcm = self.GetEvalByString#奖励道具，数量
		self.rewardMoney_fcm = int                    #奖励金币
		
class UnionFBBuyCnt(TabFile.TabLine):
	'''
	公会副本购买次数配置表
	'''
	FilePath = UNION_FILE_FOLDER_PATH.FilePath("UnionFBBuyCnt.txt")
	def __init__(self):
		self.cnt = int
		self.needRMB = int
		
class UnionFBMonster(TabFile.TabLine):
	'''
	公会副本怪物配置表
	'''
	FilePath = UNION_FILE_FOLDER_PATH.FilePath("UnionFBMonster.txt")
	def __init__(self):
		self.fbId = int
		self.levelId = int
		self.sceneId = int
		self.nextLevelNeedOccupation = int
		self.fightType = int
		self.monsterName = str
		self.monsterNpcType = int
		self.monsterPos = self.GetEvalByString
		self.monsterCampIdList = self.GetEvalByString
		self.rewardItemList = self.GetEvalByString
		self.rewardMoney = int
		self.oddsRewardItem = self.GetEvalByString
		self.odds = int
		self.rewardItemList_fcm = self.GetEvalByString#奖励道具，数量
		self.rewardMoney_fcm = int                    #奖励金币


class UnionShenShouFeedConfig(TabFile.TabLine):
	'''
	公会神兽配置表
	'''
	FilePath = UNION_FILE_FOLDER_PATH.FilePath("UnionShenShouFeed.txt")
	def __init__(self):
		self.feedType = int
		self.costMoney = int
		self.costUnbindRMB = int
		self.growthValue = int
		self.incContribution = int
		
class UnionShenShouLevelConfig(TabFile.TabLine):
	'''
	 公会神兽等级配置
	'''
	FilePath = UNION_FILE_FOLDER_PATH.FilePath("UnionShenShouLevel.txt")
	def __init__(self):
		self.shenshouId = int
		self.upGradeId = int
		self.npcType = int
		self.maxGrouthValue = int
		self.shenshouName = str
		self.needUnionResorce = int
		self.needShenShouTanLevel = int
		self.shenshouName = str
		self.fightType = int
		self.monsterId = int
		self.awardInShop = eval
		self.moneyCoe = int
		self.contributionCoe = int
		self.moneyMax = int
		self.contributionMax = int
	
	def PreCoding(self):
		self.StoreRandomRate = randomRate = Random.RandomRate()
		for index, cnt, rate in self.awardInShop:
			randomRate.AddRandomItem(rate, (index, cnt))
			

class UnionGoodConfig(TabFile.TabLine):
	'''
	公会普通商品配置
	'''
	FilePath = UNION_FILE_FOLDER_PATH.FilePath("UnionGood.txt")
	def __init__(self):
		self.goodId = int
		self.dailyLimitCnt = int
		self.costContribution = int
		self.costUnbindRMB = int
		self.needStoreLevel = int
		self.needUnionResorce = int
		self.item = eval


class UnionShenShouGoodConfig(TabFile.TabLine):
	'''
	公会商品配置
	'''
	FilePath = UNION_FILE_FOLDER_PATH.FilePath("UnionShenShouGood.txt")
	def __init__(self):
		self.goodId = int
		self.dailyLimitCnt = int
		self.costContribution = int
		self.costUnbindRMB = int
		self.item = eval


class UnionSkillConfig(TabFile.TabLine, PropertyEnum.PropertyRead):
	'''
	公会技能配置（全部都是被动技能，实际也就是增加主角属性）
	'''
	FilePath = UNION_FILE_FOLDER_PATH.FilePath("UnionSkill.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.idx = int
		self.level = int
		self.name = str
		self.roleLevel = int
		self.maxProcess = int
		self.processPerHour = int
		self.needMagicTowerLevel = int 
		self.continueTime = int
		self.needContriLearn = int
		self.needMoney = int
		self.needContriActive = int
		self.needResorcePerHour = int

class UnionMagicTowerConfig(TabFile.TabLine):
	'''
	公会魔法塔配置 
	'''
	FilePath = UNION_FILE_FOLDER_PATH.FilePath("UnionMagicTower.txt")
	def __init__(self):
		self.level = int
		self.needUnionLevel = int
		self.needUnionResorce = int

class UnionShenShouTanConfig(TabFile.TabLine):
	'''
	公会神兽坛配置 
	'''
	FilePath = UNION_FILE_FOLDER_PATH.FilePath("UnionShenShouTan.txt")
	def __init__(self):
		self.level = int
		self.needUnionLevel = int
		self.needUnionResorce = int

class UnionStoreConfig(TabFile.TabLine):
	'''
	公会商店配置 
	'''
	FilePath = UNION_FILE_FOLDER_PATH.FilePath("UnionStore.txt")
	def __init__(self):
		self.level = int
		self.needUnionLevel = int
		self.needUnionResorce = int
		
		
class UnionShenShouBufConfig(TabFile.TabLine):
	'''
	公会神兽祝福（buf）配置
	'''
	FilePath = UNION_FILE_FOLDER_PATH.FilePath("UnionShenShouBuf.txt")
	def __init__(self):
		self.cnt = int
		self.costUnbindRMB = int
		self.damageupgrade = int


class UnionShenShouHurtRankConfig(TabFile.TabLine):
	'''
	公会神兽排行榜奖励配置
	'''
	FilePath = UNION_FILE_FOLDER_PATH.FilePath("UnionShenShouHurtRankAward.txt")
	def __init__(self):
		self.rank = int
		self.contribution = int

		
class UnionTask(TabFile.TabLine):
	FilePath = UNION_FILE_FOLDER_PATH.FilePath("UnionTask.txt")
	def __init__(self):
		self.taskIndex = int
		self.group = int
		self.minLevel = int#大于等于
		self.maxLevel = int#小于等于
		self.rewardContribution = int
		self.rewardResource = int
		self.rewardExp = int
		
		self.mf1 = int
		self.mf2 = int
		
		self.killNpcId1 = int
		self.killNpcId2 = int
		
		self.rewardContribution_fcm = int             #奖励个人贡献
		self.rewardResource_fcm = int                 #奖励公会资源
		self.rewardExp_fcm = int                      #奖励经验

	def Preprocess(self, npc_data_dict):
		self.m_dict = {}
		
		if self.killNpcId1:
			npcCfg = npc_data_dict.get(self.killNpcId1)
			if not npcCfg:
				return False
			self.m_dict[self.killNpcId1] = (1, self.mf1, npcCfg.sceneID, npcCfg.npcPosX, npcCfg.npcPosY, npcCfg.clickLen)
		
		if self.killNpcId2:
			npcCfg = npc_data_dict.get(self.killNpcId2)
			if not npcCfg:
				return False
			self.m_dict[self.killNpcId2] = (2, self.mf2, npcCfg.sceneID, npcCfg.npcPosX, npcCfg.npcPosY, npcCfg.clickLen)
		
		return True
	
	def RewardRole(self, role, star = 1):
		starConfig = UNION_TASK_REWARD_FACTOR.get(star)
		if not starConfig:
			return
		
		#YY防沉迷对奖励特殊处理
		yyAntiFlag = role.GetAnti()
		if yyAntiFlag == 1:
			tmpContribution = self.rewardContribution_fcm
			tmpExp = self.rewardExp_fcm
			tmpSecource = self.rewardResource_fcm
		elif yyAntiFlag == 0:
			tmpContribution = self.rewardContribution
			tmpExp = self.rewardExp
			tmpSecource = self.rewardResource
		else:
			role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
			return
		
		roleExp = int(tmpExp * (starConfig.expFactor / 100.0))
		if roleExp:
			role.IncExp(roleExp)
			role.Msg(2, 0, GlobalPrompt.Exp_Tips % roleExp)
		
		#公会相关奖励
		unionObj = role.GetUnionObj()
		if not unionObj:
			return
		contribution = int(tmpContribution * (starConfig.contributionFactor / 100.0))
		if contribution:
			role.IncContribution(contribution)
			role.Msg(2, 0, GlobalPrompt.UnionContribution_Tips % contribution)
		
		unionResource = int(tmpSecource * (starConfig.resourceFactor / 100.0))
		if unionResource:
			unionObj.IncUnionResource(unionResource)
#			unionObj.resource += unionResource
			unionObj.HasChange()
			role.Msg(2, 0, GlobalPrompt.UnionResource_Tips % unionResource)
			
class UnionTaskRewardFactor(TabFile.TabLine):
	FilePath = UNION_FILE_FOLDER_PATH.FilePath("UnionTaskRewardFactor.txt")
	def __init__(self):
		self.star = int
		self.expFactor = int
		self.resourceFactor = int
		self.contributionFactor = int
		
#===============================================================================
# 公会魔域探秘
#===============================================================================
class UnionExploreBuyCnt(TabFile.TabLine):
	'''
	公会魔域探秘购买行动力
	'''
	FilePath = UNION_FILE_FOLDER_PATH.FilePath("UnionExploreBuyCnt.txt")
	def __init__(self):
		self.cnt = int
		self.needRMB = int
		
class UnionExploreEvent(TabFile.TabLine):
	'''
	公会魔域探秘购买事件
	'''
	FilePath = UNION_FILE_FOLDER_PATH.FilePath("UnionExploreEvent.txt")
	def __init__(self):
		self.eventId = int
		self.eventOdds = int
		
class UnionExploreQuestion(TabFile.TabLine):
	'''
	 答题问题配置表
	'''
	FilePath = UNION_FILE_FOLDER_PATH.FilePath("UnionExploreQuestion.txt")
	def __init__(self):
		self.questionId = int
		self.right = int
		
class UnionExploreMonster(TabFile.TabLine):
	'''
	 魔域探秘怪物配置表
	'''
	FilePath = UNION_FILE_FOLDER_PATH.FilePath("UnionExploreMonster.txt")
	def __init__(self):
		self.meterRange = self.GetEvalByString
		self.mcidList = self.GetEvalByString
		
class UnionExplorePrisonerOutput(TabFile.TabLine):
	'''
	 魔域探秘战俘产出配置表
	'''
	FilePath = UNION_FILE_FOLDER_PATH.FilePath("UnionExplorePrisonerOutput.txt")
	def __init__(self):
		self.zdlRange = self.GetEvalByString
		self.resourceRange = self.GetEvalByString
		self.timeRange = self.GetEvalByString
		
class UnionExploreQuestionReward(TabFile.TabLine):
	'''
	 答题奖励
	'''
	FilePath = UNION_FILE_FOLDER_PATH.FilePath("UnionExploreQuestionReward.txt")
	def __init__(self):
		self.level = int
		self.rightUpRange = self.GetEvalByString
		self.wrongDownRange = self.GetEvalByString
		self.exploreFactor = int
		self.rightContribution = int
		self.rightResource = int
		self.wrongContribution = int
		self.wrongResource = int
		
class UnionExploreMonsterReward(TabFile.TabLine):
	'''
	 打怪物奖励
	'''
	FilePath = UNION_FILE_FOLDER_PATH.FilePath("UnionExploreMonsterReward.txt")
	def __init__(self):
		self.level = int
		self.winUpRange = self.GetEvalByString
		self.lostDownRange = self.GetEvalByString
		self.exploreFactor = int
		self.winContribution = int
		self.winResource = int
		self.lostContribution = int
		self.lostResource = int
		
class UnionExploreTreasureReward(TabFile.TabLine):
	'''
	 宝箱奖励
	'''
	FilePath = UNION_FILE_FOLDER_PATH.FilePath("UnionExploreTreasureReward.txt")
	def __init__(self):
		self.levelRange = self.GetEvalByString
		self.meterRange = self.GetEvalByString
		self.rewardItemData = self.GetEvalByString
		self.upRange = self.GetEvalByString
		self.rewardItemData_fcm = self.GetEvalByString#奖励道具(几率，道具Coding，数量）
		
	def init_random(self):
		self.itemRandomObj = Random.RandomRate()
		for odds, itemCoding, itemCnt in self.rewardItemData:
			self.itemRandomObj.AddRandomItem(odds, (itemCoding, itemCnt))
		#防沉迷随机对象
		self.itemRandomObj_fcm = Random.RandomRate()
		for odds, itemCoding, itemCnt in self.rewardItemData_fcm:
			self.itemRandomObj_fcm.AddRandomItem(odds, (itemCoding, itemCnt))
		
class UnionExplorePrisonerReward(TabFile.TabLine):
	'''
	 抓俘虏奖励
	'''
	FilePath = UNION_FILE_FOLDER_PATH.FilePath("UnionExplorePrisonerReward.txt")
	def __init__(self):
		self.level = int
		self.winUpRange = self.GetEvalByString
		self.lostDownRange = self.GetEvalByString
		self.exploreFactor = int
		self.winContribution = int
		self.winResource = int
		self.lostContribution = int
		self.lostResource = int
		
def LoadUnionBase():
	global UNION_BASE
	global UNION_LEVEL_MAX
	global UNION_POPULATION_MIN
	for config in UnionBase.ToClassType():
		#公会最少人口
		if config.level == 1:
			UNION_POPULATION_MIN = config.population
		#公会最大等级
		if config.level > UNION_LEVEL_MAX:
			UNION_LEVEL_MAX = config.level
		
		UNION_BASE[config.level] = config
		
def LoadUnionJob():
	global UNION_JOB
	for config in Job.ToClassType():
		UNION_JOB[config.jobId] = config
		
def LoadDayBox():
	global UNION_DAY_BOX
	for config in DayBox.ToClassType():
		UNION_DAY_BOX[config.level] = config
		
def LoadAchievementBox():
	global UNION_ACHIEVEMENT_BOX
	for config in AchievementBox.ToClassType():
		UNION_ACHIEVEMENT_BOX[config.level] = config
		
def LoadGod():
	global UNION_GOD
	global UNION_GODID_MAX
	for config in God.ToClassType():
		if config.godId > UNION_GODID_MAX:
			UNION_GODID_MAX = config.godId
		UNION_GOD[config.godId] = config
		
def LoadTreasureGet():
	global UNION_TREASURE_GET
	for config in TreasureGet.ToClassType():
		if config.boxType in UNION_TREASURE_GET:
			UNION_TREASURE_GET[config.boxType][config.level] = config
		else:
			UNION_TREASURE_GET[config.boxType] = {config.level: config}
			
def LoadTreasureRob():
	global UNION_TREASURE_ROB
	for config in TreasureRob.ToClassType():
		if config.boxType in UNION_TREASURE_ROB:
			UNION_TREASURE_ROB[config.boxType][config.level] = config
		else:
			UNION_TREASURE_ROB[config.boxType] = {config.level: config}
			
def LoadUnionFBBase():
	global UNION_FB_BASE
	global UNION_FB_ID_MAX
	for config in UnionFBBase.ToClassType():
		if config.fbId > UNION_FB_ID_MAX:
			UNION_FB_ID_MAX = config.fbId
		UNION_FB_BASE[config.fbId] = config
		
def LoadUnionFBBuyCnt():
	global UNION_FB_BUY_CNT
	for config in UnionFBBuyCnt.ToClassType():
		UNION_FB_BUY_CNT[config.cnt] = config
		
def LoadUnionFBMonster():
	global UNION_FB_MONSTER
	for config in UnionFBMonster.ToClassType():
		UNION_FB_MONSTER[(config.fbId, config.levelId)] = config

def LoadUnionShenShouFeedConfig():
	global UnionShenShouFeedDict
	for config in UnionShenShouFeedConfig.ToClassType():
		if config.feedType in UnionShenShouFeedDict:
			print "GE_EXC,repeat config.feedType(%s)in UnionShenShouFeedDict" % config.feedType
		UnionShenShouFeedDict[config.feedType] = config

def LoadUnionShenShoulevelConfig():
	global UnionShenShouLevelDict
	for config in UnionShenShouLevelConfig.ToClassType():
		if config.shenshouId in UnionShenShouLevelDict:
			print "GE_EXC, repeat config.shenshouId(%s) in UnionShenShouLevelDict" % config.shenshouId
		config.PreCoding()
		UnionShenShouLevelDict[config.shenshouId] = config

def LoadUnionGoodConfig():
	global UnionGoodConfigDict
	for config in UnionGoodConfig.ToClassType():
		if config.goodId in UnionGoodConfigDict:
			print "GE_EXC,repeat goodId(%s) in UnionGoodConfigDict" % config.goodId
		UnionGoodConfigDict[config.goodId] = config


def LoadUnionShenShouGoodConfig():
	global UnionShenShouGoodDict
	for config in UnionShenShouGoodConfig.ToClassType():
		if config.goodId in UnionShenShouGoodDict:
			print "GE_EXC,repeat goodId(%s) in UnionShenShouGoodDict" % config.goodId
		UnionShenShouGoodDict[config.goodId] = config




def LoadUnionSkillConfig():
	global UnionSkillConfigDict
	for config in UnionSkillConfig.ToClassType():
		if (config.idx, config.level) in UnionSkillConfigDict:
			print "GE_EXC,repeat (idx,level)(%s,%s) in UnionSkillConfigDict" % (config.idx, config.level)
		config.InitProperty()
		UnionSkillConfigDict[(config.idx, config.level)] = config

def LoadUnionMagicTowerConfig():
	global UnionMagicTowerDict
	for config in UnionMagicTowerConfig.ToClassType():
		if config.level in UnionMagicTowerDict:
			print "GE_EXC,repeat level (%s) in UnionMagicTowerDict" % config.level
		UnionMagicTowerDict[config.level] = config

def LoadUnionShenShouTanConfig():
	global UnionShenShouTanDict
	for config in UnionShenShouTanConfig.ToClassType():
		if config.level in UnionShenShouTanDict:
			print "GE_EXC, repeat level(%s) in UnionShenShouTanDict" % config.level
		UnionShenShouTanDict[config.level] = config

def LoadUnionStoreConfig():
	global UnionStoreDict
	for config in UnionStoreConfig.ToClassType():
		if config.level in UnionStoreDict:
			print "GE_EXC,repeat level(%s) in UnionStoreSict" % config.level
		UnionStoreDict[config.level] = config

def LoadUnionShenShouBufConfig():
	global UnionShenShouBufDict
	for config in UnionShenShouBufConfig.ToClassType():
		if config.cnt in UnionShenShouBufDict:
			print "GE_EXC,repeat cnt(%s) in UnionShenShouBufDict" % config.cnt
		UnionShenShouBufDict[config.cnt] = config


def LoadUnionShenShouHurtRank():
	global UnionShenShouHurtRankCfgDict
	for config in UnionShenShouHurtRankConfig.ToClassType():
		if config.rank in UnionShenShouHurtRankCfgDict:
			print "GE_EXC,repeat rank(%s) in UnionShenShouHurtRankCfgDict" % config.rank
		UnionShenShouHurtRankCfgDict[config.rank] = config.contribution
	

def LoadUnionTask():
	global UNION_TASK
	
	Group_Level_Dict = {}
	Group_Cfgs = {}
	for dtc in UnionTask.ToClassType():
		if dtc.taskIndex in UNION_TASK:
			print "GE_EXC, LoadUnionTask repeat taskIndex(%s)" % dtc.taskIndex
		UNION_TASK[dtc.taskIndex] = dtc
		
		if dtc.group not in Group_Level_Dict:
			Group_Level_Dict[dtc.group] = (dtc.minLevel, dtc.maxLevel)
			if dtc.minLevel >= dtc.maxLevel:
				print "GE_EXC, error in  LoadUnionTask dtc.minLevel <= dtc.maxLevel (%s)" % dtc.taskIndex
			
			Group_Cfgs[dtc.group] = [dtc.taskIndex]
		else:
			minLevel, maxLevel = Group_Level_Dict[dtc.group]
			if minLevel != dtc.minLevel or maxLevel != dtc.maxLevel:
				print "GE_EXC, error in  LoadUnionTask minLevel != dtc.maxLevel or maxLevel != dtc.maxLevel (%s)" % dtc.taskIndex
			Group_Cfgs[dtc.group].append(dtc.taskIndex)
	
	#构建等级随机任务
	global UNION_TASK_LEVEL_RANDOM_DICT
	for group, leveld in Group_Level_Dict.iteritems():
		minLevel, maxLevel = leveld
		randomItem = Random.RandomRate()
		for taskIndex in Group_Cfgs[group]:
			randomItem.AddRandomItem(1, taskIndex)
			
		for i in xrange(minLevel, maxLevel + 1):
			if i in UNION_TASK_LEVEL_RANDOM_DICT:
				print "GE_EXC, error in LoadUnionTask level error", i
				continue
			UNION_TASK_LEVEL_RANDOM_DICT[i] = randomItem
	
#	from Game.NPC import NPCMgr
#	if NPCMgr.SceneNPC_Dict:
#		for taskIndex, cfg in UNION_TASK.iteritems():
#			if not cfg.Preprocess(NPCMgr.SceneNPC_Dict):
#				print "GE_EXC, UNION_TASK Preprocess warning (%s)" % taskIndex

		
def LoadUnionTaskRewardFactor():
	global UNION_TASK_REWARD_FACTOR
	for config in UnionTaskRewardFactor.ToClassType():
		UNION_TASK_REWARD_FACTOR[config.star] = config
		
def LoadUnionExploreBuyCnt():
	global UNION_EXPLORE_BUY_CNT
	for config in UnionExploreBuyCnt.ToClassType():
		UNION_EXPLORE_BUY_CNT[config.cnt] = config
		
def LoadUnionExploreEvent():
	global UNION_EXPLORE_EVENT
	global UNION_EXPLORE_EVENT_RANDOM_OBJ
	for config in UnionExploreEvent.ToClassType():
		UNION_EXPLORE_EVENT[config.eventId] = config
		UNION_EXPLORE_EVENT_RANDOM_OBJ.AddRandomItem(config.eventOdds, config.eventId)
		
def LoadUnionExploreQuestion():
	global UNION_EXPLORE_QUESTION
	for config in UnionExploreQuestion.ToClassType():
		UNION_EXPLORE_QUESTION[config.questionId] = config
		
def LoadUnionExploreMonster():
	global UNION_EXPLORE_MONSTER
	for config in UnionExploreMonster.ToClassType():
		for meter in xrange(config.meterRange[0], config.meterRange[1] + 1):
			UNION_EXPLORE_MONSTER[meter] = config
			
def LoadUnionExplorePrisonerOutput():
	global UNION_EXPLORE_PRISONER_OUTPUT_LIST
	for config in UnionExplorePrisonerOutput.ToClassType():
		UNION_EXPLORE_PRISONER_OUTPUT_LIST.append(config)
		
def LoadUnionExploreQuestionReward():
	global UNION_EXPLORE_QUESTION_REWARD
	for config in UnionExploreQuestionReward.ToClassType():
		UNION_EXPLORE_QUESTION_REWARD[config.level] = config
		
def LoadUnionExploreMonsterReward():
	global UNION_EXPLORE_MONSTER_REWARD
	for config in UnionExploreMonsterReward.ToClassType():
		UNION_EXPLORE_MONSTER_REWARD[config.level] = config
		
def LoadUnionExploreTreasureReward():
	global UNION_EXPLORE_TREASURE_REWARD
	for config in UnionExploreTreasureReward.ToClassType():
		config.init_random()
		for level in xrange(config.levelRange[0], config.levelRange[1] + 1):
			l = UNION_EXPLORE_TREASURE_REWARD.setdefault(level, [])
			l.append(config)
			
def LoadUnionExplorePrisonerReward():
	global UNION_EXPLORE_PRISONER_REWARD
	for config in UnionExplorePrisonerReward.ToClassType():
		UNION_EXPLORE_PRISONER_REWARD[config.level] = config

def AfterLoadSceneNPC(SceneNPC_Dict, param):
	from Game.NPC import NPCMgr
	if NPCMgr.SceneNPC_Dict:
		for taskIndex, cfg in UNION_TASK.iteritems():
			if not cfg.Preprocess(NPCMgr.SceneNPC_Dict):
				print "GE_EXC, UNION_TASK Preprocess warning (%s)" % taskIndex
	else:
		print "GE_EXC UNION_TASK need SceneNPC_Dict"
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadUnionBase()
		LoadUnionJob()
		LoadDayBox()
		LoadAchievementBox()
		LoadGod()
		LoadTreasureGet()
		LoadTreasureRob()
		LoadUnionFBBase()
		LoadUnionFBBuyCnt()
		LoadUnionFBMonster()
		LoadUnionShenShouFeedConfig()
		LoadUnionShenShoulevelConfig()
		LoadUnionGoodConfig()
		LoadUnionShenShouGoodConfig()
		LoadUnionSkillConfig()
		LoadUnionMagicTowerConfig()
		LoadUnionShenShouTanConfig()
		LoadUnionStoreConfig()
		LoadUnionShenShouBufConfig()
		LoadUnionShenShouHurtRank()
		LoadUnionTask()
		LoadUnionTaskRewardFactor()
		LoadUnionExploreBuyCnt()
		LoadUnionExploreEvent()
		LoadUnionExploreQuestion()
		LoadUnionExploreMonster()
		LoadUnionExplorePrisonerOutput()
		LoadUnionExploreQuestionReward()
		LoadUnionExploreMonsterReward()
		LoadUnionExploreTreasureReward()
		LoadUnionExplorePrisonerReward()
		Event.RegEvent(Event.Eve_AfterLoadSceneNPC, AfterLoadSceneNPC)

