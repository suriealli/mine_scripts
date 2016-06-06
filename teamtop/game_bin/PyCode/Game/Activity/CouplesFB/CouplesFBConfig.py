#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.CouplesFB.CouplesFBConfig")
#===============================================================================
# 情缘副本配置
#===============================================================================
import Environment
import DynamicPath
from Util import Random
from Util.File import TabFile



if "_HasLoad" not in dir():	
	COUPLES_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	COUPLES_FILE_FOLDER_PATH.AppendPath("CouplesFB")
	
	COUPLES_BASE_DICT = {}	#情缘副本基础配置
	RANDOM_EVENT_DICT = {}	#随机触发事件配置(不包含buff)
	EVENT_ID_DICT = {}	#事件配置
	RANDOM_LUCKY_DICT = {}	#幸运抽奖配置
	COUPLES_BUFF_DICT = {}	#buff配置
	COUPLES_REWARD_DICT = {}	#奖励配置表
	COUPLES_BUY_COST = {}	#副本购买次数消耗
	
class CouplesFB(TabFile.TabLine):
	'''
	情缘副本
	'''
	FilePath = COUPLES_FILE_FOLDER_PATH.FilePath("CouplesFB.txt")
	def __init__(self):
		self.FBId			= int
		self.needLevel		= int
		self.freeQuick		= int
		self.FreeneedVIP	= int
		self.RMBQuick		= int
		self.RMBneedVIP		= int
		self.movedecpro		= self.GetEvalByString
		self.moveaddpro		= self.GetEvalByString
		self.timedecpro		= self.GetEvalByString
		self.timeaddpro		= self.GetEvalByString
		self.nothing		= self.GetEvalByString
		self.eventId		= int
		self.fightType		= int
		self.campId			= int
		self.monsterHp		= int
		self.fightrewards	= int
		self.bossfightType	= int
		self.bosscampId		= int
		self.bossHp			= int
		self.bossrewards	= int
		self.drawId			= int
		self.timeS			= int
		self.rewardS		= int
		self.timeA			= int
		self.rewardA		= int
		self.timeB			= int
		self.rewardB		= int
		self.timeC			= int
		self.rewardC		= int
		self.timeD			= int
		self.rewardD		= int

class CouplesEvent(TabFile.TabLine):
	'''
	情缘事件配置
	'''
	FilePath = COUPLES_FILE_FOLDER_PATH.FilePath("CouplesEvent.txt")
	def __init__(self):
		self.eventId		= int
		self.event1			= int
		self.cnt1			= int
		self.randomIndex1	= self.GetEvalByString
		
		self.event2			= int
		self.cnt2			= int
		self.randomIndex2	= self.GetEvalByString
		
		self.event3			= int
		self.cnt3			= int
		self.randomIndex3	= self.GetEvalByString
		
		self.event4			= int
		self.cnt4			= int
		self.randomIndex4	= self.GetEvalByString
		
		self.event5			= int
		self.cnt5			= int
		self.randomIndex5	= self.GetEvalByString
		
		self.event6			= int
		self.cnt6			= int
		self.randomIndex6	= self.GetEvalByString
		
		self.event7			= int
		self.cnt7			= int
		self.randomIndex7	= self.GetEvalByString
		
		self.event8			= int
		self.cnt8			= int
		self.randomIndex8	= self.GetEvalByString
		
		self.event9			= int
		self.cnt9			= int
		self.randomIndex9	= self.GetEvalByString
		
		self.event10		= int
		self.cnt10			= int
		self.randomIndex10	= self.GetEvalByString

		self.event11		= int
		self.cnt11			= int
		self.randomIndex11	= self.GetEvalByString

		self.event12		= int
		self.cnt12			= int
		self.randomIndex12	= self.GetEvalByString

class LuckyDraw(TabFile.TabLine):
	'''
	幸运抽奖
	'''
	FilePath = COUPLES_FILE_FOLDER_PATH.FilePath("LuckyDraw.txt")
	def __init__(self):
		self.drawId		= int
		
		self.reward1	= int
		self.rewardpro1	= int
		self.item1		= self.GetEvalByString
		self.gold1		= int
		self.bindRMB1	= int
		
		self.reward2	= int
		self.rewardpro2	= int
		self.item2		= self.GetEvalByString
		self.gold2		= int
		self.bindRMB2	= int
		
		self.reward3	= int
		self.rewardpro3	= int
		self.item3		= self.GetEvalByString
		self.gold3		= int
		self.bindRMB3	= int
		
		self.reward4	= int
		self.rewardpro4	= int
		self.item4		= self.GetEvalByString
		self.gold4		= int
		self.bindRMB4	= int
		
class CouBuffInfo(TabFile.TabLine):
	'''
	情缘副本buff
	'''
	FilePath = COUPLES_FILE_FOLDER_PATH.FilePath("CouBuffInfo.txt")
	def __init__(self):
		self.buffId		= int
		self.keeptime	= int
		self.fightCD	= int
		self.moveCD		= int
		self.randompro	= int
		self.fightbuff	= int

class CouplesReward(TabFile.TabLine):
	'''
	情缘副本奖励配置
	'''
	FilePath = COUPLES_FILE_FOLDER_PATH.FilePath("CouplesReward.txt")
	def __init__(self):
		self.rewardId	= int
		self.gold		= int
		self.bindRMB	= int
		self.items		= self.GetEvalByString

class BuyTimes(TabFile.TabLine):
	'''
	情缘副本购买次数消耗
	'''
	FilePath = COUPLES_FILE_FOLDER_PATH.FilePath("BuyTimes.txt")
	def __init__(self):
		self.buyTimes	= int
		self.costRMB	= int
		
def LoadCouplesFB():
	global COUPLES_BASE_DICT
	global RANDOM_EVENT_DICT
	for cfg in CouplesFB.ToClassType():
		if cfg.FBId in COUPLES_BASE_DICT:
			print "GE_EXC,repeat FBId(%s) in LoadCouplesFB" % cfg.FBId
		COUPLES_BASE_DICT[cfg.FBId] = cfg
		RANDOM = Random.RandomRate()
		if cfg.movedecpro:
			RANDOM.AddRandomItem(cfg.movedecpro[0], cfg.movedecpro[1])
		if cfg.moveaddpro:
			RANDOM.AddRandomItem(cfg.moveaddpro[0], cfg.moveaddpro[1])
		if cfg.timedecpro:
			RANDOM.AddRandomItem(cfg.timedecpro[0], cfg.timedecpro[1])
		if cfg.timeaddpro:
			RANDOM.AddRandomItem(cfg.timeaddpro[0], cfg.timeaddpro[1])
		if cfg.nothing:
			RANDOM.AddRandomItem(cfg.nothing[0], cfg.nothing[1])
		RANDOM_EVENT_DICT[cfg.FBId] = RANDOM


def LoadCouplesEvent():
	global EVENT_ID_DICT
	for cfg in CouplesEvent.ToClassType():
		if cfg.eventId in EVENT_ID_DICT:
			print "GE_EXC,repeat FBID(%s) in EVENT_ID_DICT" % cfg.eventId
		event_dict = {}
		event_dict[cfg.event1] = [cfg.cnt1, cfg.randomIndex1]
		event_dict[cfg.event2] = [cfg.cnt2, cfg.randomIndex2]
		event_dict[cfg.event3] = [cfg.cnt3, cfg.randomIndex3]
		event_dict[cfg.event4] = [cfg.cnt4, cfg.randomIndex4]
		event_dict[cfg.event5] = [cfg.cnt5, cfg.randomIndex5]
		event_dict[cfg.event6] = [cfg.cnt6, cfg.randomIndex6]
		event_dict[cfg.event7] = [cfg.cnt7, cfg.randomIndex7]
		event_dict[cfg.event8] = [cfg.cnt8, cfg.randomIndex8]
		event_dict[cfg.event9] = [cfg.cnt9, cfg.randomIndex9]
		event_dict[cfg.event10] = [cfg.cnt10, cfg.randomIndex10]
		event_dict[cfg.event11] = [cfg.cnt11, cfg.randomIndex11]
		event_dict[cfg.event12] = [cfg.cnt12, cfg.randomIndex12]
		for data in event_dict.values():
			cnt, randomList = data
			if len(randomList) < cnt:
				print "GE_EXC, in LoadCouplesEvent cnt(%s) and len(randomList)(%s) is wrong" % (cnt, randomList)
				return
		EVENT_ID_DICT[cfg.eventId] = event_dict

def LoadLuckyDraw():
	global RANDOM_LUCKY_DICT
	for cfg in LuckyDraw.ToClassType():
		if cfg.drawId in RANDOM_LUCKY_DICT:
			print "GE_EXC,repeat drawId(%s) in LoadLuckyDraw" % cfg.drawId
		NEW_RANDOM = Random.RandomRate()
		if cfg.rewardpro1:
			NEW_RANDOM.AddRandomItem(cfg.rewardpro1, [cfg.reward1, cfg.item1, cfg.gold1, cfg.bindRMB1])
		if cfg.rewardpro2:
			NEW_RANDOM.AddRandomItem(cfg.rewardpro2, [cfg.reward2, cfg.item2, cfg.gold2, cfg.bindRMB2])
		if cfg.rewardpro3:
			NEW_RANDOM.AddRandomItem(cfg.rewardpro3, [cfg.reward3, cfg.item3, cfg.gold3, cfg.bindRMB3])
		if cfg.rewardpro4:
			NEW_RANDOM.AddRandomItem(cfg.rewardpro4, [cfg.reward4, cfg.item4, cfg.gold4, cfg.bindRMB4])
		RANDOM_LUCKY_DICT[cfg.drawId] = NEW_RANDOM

def LoadCouBuffInfo():
	global COUPLES_BUFF_DICT
	for cfg in CouBuffInfo.ToClassType():
		if cfg.buffId in COUPLES_BUFF_DICT:
			print "GE_EXC,repeat buffId(%s) in LoadCouBuffInfo" % cfg.buffId
		COUPLES_BUFF_DICT[cfg.buffId] = cfg

def LoadCouplesReward():
	global COUPLES_REWARD_DICT
	for cfg in CouplesReward.ToClassType():
		if cfg.rewardId in COUPLES_REWARD_DICT:
			print "GE_EXC,repeat rewardId(%s) in LoadCouplesReward" % cfg.rewardId
		COUPLES_REWARD_DICT[cfg.rewardId] = cfg

def LoadBuyTimes():
	global COUPLES_BUY_COST
	for cfg in BuyTimes.ToClassType():
		if cfg.buyTimes in COUPLES_BUY_COST:
			print "GE_EXC,repeat buyTimes(%s) in LoadBuyTimes" % cfg.buyTimes
		COUPLES_BUY_COST[cfg.buyTimes] = cfg

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadCouplesFB()
		LoadCouplesEvent()
		LoadLuckyDraw()
		LoadCouBuffInfo()
		LoadCouplesReward()
		LoadBuyTimes()
