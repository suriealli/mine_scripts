#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DragonTreasure.DragonTreasureConfig")
#===============================================================================
# 巨龙宝藏配置表
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile
from Util import Random
from Game.Role.Data import EnumObj

if "_HasLoad" not in dir():
	DragonTreasure_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	DragonTreasure_FILE_FOLDER_PATH.AppendPath("DragonTreasure")
	
	DRAGON_EVENT_DICT = {}	#特殊事件
	DRAGON_ID_MAP_DICT = {}	#场景id对应的名字
	DRAGON_REWARD_DICT = {} #巨龙珍宝奖励
	DIG_EVENT_DICT = {}#挖宝事件
	TYPE_EVENT_DICT = {} #事件类型对应概率
	SCENE_ID_LIST = [] #记录场景的列表
	BUY_DIG_COST_DICT = {}	#购买挖宝次数消耗
	RANDOM = Random.RandomRate()
	
class DragonEvent(TabFile.TabLine):
	'''
	特殊事件配置表
	'''
	FilePath = DragonTreasure_FILE_FOLDER_PATH.FilePath("DragonEvent.txt")
	def __init__(self):
		self.eventId  = int
		self.sceneId1 = int
		self.sceneId2 = int
		self.sceneId3 = int
		self.reward   = self.GetEvalByString
		self.tittle   = str 
		
def LoadDragonEvent():
	global DRAGON_EVENT_DICT
	for config in DragonEvent.ToClassType():
		if config.eventId in DRAGON_EVENT_DICT:
			print "GE_EXC, repeat eventId in DragonEvent (%s)" % config.eventId
		DRAGON_EVENT_DICT[config.eventId] = config		

def GetcfgBySceneId(sceneId):
	'''
	根据场景Id获取满足条件的新事件ID
	@param sceneId:
	'''
	global DRAGON_EVENT_DICT
	for event_id, cfg in DRAGON_EVENT_DICT.iteritems():
		if cfg.sceneId1 == sceneId:
			return event_id
	print "GE_EXC,can not find eventId by sceneId=(%s) in DragonTreasureConfig" % sceneId
	return None

def GetNextSceneByScene(event_id, scene_id):
	'''
	根据事件ID和场景ID，获取下个该触发的场景ID
	@param event_id:
	@param scene_id:
	'''
	global DRAGON_EVENT_DICT
	cfg = DRAGON_EVENT_DICT.get(event_id)
	if not cfg:
		print "GE_EXC,can not find DragonEvent by eventId(%s)" % event_id
		return
	if scene_id == cfg.sceneId1:
		return cfg.sceneId2, 1
	elif scene_id == cfg.sceneId2:
		return cfg.sceneId3, 2
	else:
		return None, None

class DragonReward(TabFile.TabLine):
	'''
	巨龙珍宝奖励配置表
	'''
	FilePath = DragonTreasure_FILE_FOLDER_PATH.FilePath("DragonReward.txt")
	def __init__(self):
		self.rewardId   = int
		self.rate       = int
		self.itemconfig = int
		self.cnt        = int
		self.bindRMB    = int
		self.public     = int
		self.cnt_fcm = int                            #数量
		self.bindRMB_fcm = int                        #魔晶

class DragonDigEvent(TabFile.TabLine):
	'''
	挖宝事件配置表
	'''
	FilePath = DragonTreasure_FILE_FOLDER_PATH.FilePath("DragonDigEvent.txt")
	def __init__(self):
		self.EventId = int
		self.EventType = int
		self.MinLevel = int
		self.MaxLevel = int
		self.mci = int
		self.fightType = int
		self.Gold = int
		self.RMB = int
		self.times = int
		self.Lucktimes = int
		self.item = int
		self.cnt = int
		self.Gold_fcm = int                           #奖励金币
		self.RMB_fcm = int                            #奖励魔晶
		self.cnt_fcm = int                            #数量
		
class DragonID(TabFile.TabLine):
	'''
	巨龙宝藏场景配置
	'''
	FilePath = DragonTreasure_FILE_FOLDER_PATH.FilePath("DragonIdName.txt")
	def __init__(self):
		self.sceneId1 = int
		
class EventForType(TabFile.TabLine):
	'''
	挖宝事件类型概率表
	'''
	FilePath = DragonTreasure_FILE_FOLDER_PATH.FilePath("EventForType.txt")
	def __init__(self):
		self.EventType = int
		self.rate = int

def LoadEventForType():
	global RANDOM
	for cfg in EventForType.ToClassType():
		RANDOM.AddRandomItem(cfg.rate, cfg.EventType)
		
class BuyDigCost(TabFile.TabLine):
	'''
	购买挖宝次数消费
	'''
	FilePath = DragonTreasure_FILE_FOLDER_PATH.FilePath("BuyDigCost.txt")
	def __init__(self):
		self.BuyTime	 = int
		self.DigCost	 = int
		self.DigLuckyCost= int
		
def LoadBuyDigCost():
	global BUY_DIG_COST_DICT
	
	for cfg in BuyDigCost.ToClassType():
		if cfg.BuyTime in BUY_DIG_COST_DICT:
			print "GE_EXC, repeat BuyTime(%s) in LoadBuyDigCost" % cfg.BuyTime
			return
		BUY_DIG_COST_DICT[cfg.BuyTime] = cfg
	
def LoadDragonReward():
	#from Game.Item import ItemConfig
	global DRAGON_REWARD_DICT	
	for sc in DragonReward.ToClassType():
		if sc.rewardId in DRAGON_REWARD_DICT:
			print 'GE_EXC, repeat stageid= (%s) in stagescoreReward' % sc.rewardId
		#if not ItemConfig.CheckItemCoding(sc.itemconfig):
		#	print "GE_EXC,no this item=(%s) in DragonReward" % sc.itemconfig
		DRAGON_REWARD_DICT[sc.rewardId] = sc
		#RANDOM.AddRandomItem(sc.rate, sc.rewardId)

def LoadDragonDigEvent():
	global DIG_EVENT_DICT
	for cfg in DragonDigEvent.ToClassType():
		if cfg.EventId in DIG_EVENT_DICT:
			print "GE_EXC,repeate eventid(%s) in dragondigevent" % cfg.EventId
		DIG_EVENT_DICT[cfg.EventId] = cfg

def LoadDragonID():
	global SCENE_ID_LIST
	for cfg in DragonID.ToClassType():
		if cfg.sceneId1 in SCENE_ID_LIST:
			print "GE_EXC, repeate sceneId1 in DragonID" % cfg.sceneId1
			continue
		SCENE_ID_LIST.append(cfg.sceneId1)

def GetRandomOne(role):
	'''
	除去已获取的奖励，重新计算剩余物品的
	概率
	@param role:
	'''
	global DRAGON_REWARD_DICT
	#获取玩家已获得列表
	dragonTreasure_obj = role.GetObj(EnumObj.Dragon_Treasure)
	if not dragonTreasure_obj:
		print "GE_EXC, the roleId=(%s) can not find EnumObj.Dragon_Treasure" % role.GetRoleID()
		return	
	getted_item = dragonTreasure_obj.get(3)
	
	NEW_RANDOM = Random.RandomRate()
	for rewardId, cfg in DRAGON_REWARD_DICT.iteritems():
		if rewardId not in getted_item:
			NEW_RANDOM.AddRandomItem(cfg.rate, cfg.rewardId)
	return NEW_RANDOM.RandomOne()

def GetEventByType(etype, level):
	'''
	根据事件类型和玩家等级获取对应事件配置
	@param etype:
	@param level:
	'''	
	global DIG_EVENT_DICT
	for _, cfg in DIG_EVENT_DICT.iteritems():
		if cfg.EventType == etype:
			if cfg.MinLevel <= level <= cfg.MaxLevel:
				return cfg
	return None
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadDragonEvent()
		LoadDragonReward()
		LoadDragonDigEvent()
		LoadEventForType()
		LoadDragonID()
		LoadBuyDigCost()
		
