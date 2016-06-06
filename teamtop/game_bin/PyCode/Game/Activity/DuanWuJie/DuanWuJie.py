#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DuanWuJie.DuanWuJie")
#===============================================================================
# 欢庆端午节
#===============================================================================
import random
import cRoleMgr
import Environment
from Game.Role import Event
from Game.Role.Data import EnumInt8
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Game.Activity import CircularDefine
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Activity.DuanWuJie import DuanWuJieConfig

if "_HasLoad" not in dir():
	IsStart = False
	
	#日志
	TraDuanWuJieOpenNormalZongzi = AutoLog.AutoTransaction("TraDuanWuJieOpenNormalZongzi", "欢庆端午节开普通粽子")
	TraDuanWuJieOpenGoldZongzi = AutoLog.AutoTransaction("TraDuanWuJieOpenGoldZongzi", "欢庆端午节开黄金粽子")
	TraDuanWuJieOpenNormalZongziTen = AutoLog.AutoTransaction("TraDuanWuJieOpenNormalZongziTen", "欢庆端午节开普通粽子十次")
	TraDuanWuJieOpenGoldZongziTen = AutoLog.AutoTransaction("TraDuanWuJieOpenGoldZongziTen", "欢庆端午节开黄金粽子十次")


def Start(*param):
	'''
	开启欢庆端午节
	'''
	_, circularType = param
	if circularType != CircularDefine.CA_DuanWuJieZongzi:
		return
	# 已开启 
	global IsStart
	if IsStart is True:
		print "GE_EXC,repeat open DuanWuJie"
		return
	IsStart = True	


def End(*param):
	'''
	关闭欢庆端午节
	'''
	_, circularType = param
	if circularType != CircularDefine.CA_DuanWuJieZongzi:
		return
	
	# 未开启 
	global IsStart
	if IsStart is False:
		print "GE_EXC,end DuanWuJie while not open "
		return
	IsStart = False	


def RequestOpenNormalZongzi(role, msg):
	'''
	客户端请求开普通粽子
	'''
	if IsStart is False:
		return
	if role.GetLevel() < EnumGameConfig.DuanWuJieNeedLevel:
		return
	if role.ItemCnt(EnumGameConfig.DuanWuJieNormalZongziCoding) < 1:
		return
	if role.GetMoney() < EnumGameConfig.DuanWuJieNormalPrice:
		return
	roleLevel = role.GetLevel()
	levelRange = DuanWuJieConfig.LevelRangeDict.get(roleLevel)
	if levelRange is None:
		print "GE_EXC,role(%s) level(%s) error while levelRange = DuanWuJieConfig.LevelRangeDict.get(roleLevel)" % (role.GetRoleID(), roleLevel)
		return
	config = DuanWuJieConfig.NormalZongziConfigDict.get(levelRange)
	if config is None:
		return
	
	rewardID = config.randomRate.RandomOne()
	rewardConfig = DuanWuJieConfig.RewardConfigDict.get(rewardID)
	if rewardConfig is None:
		print "GE_EXC,error while rewardConfig = DuanWuJieConfig.RewardConfigDict.get(rewardID) (%s)" % rewardID
		return
	
	tips = GlobalPrompt.DuanWuJieZongzi
	with TraDuanWuJieOpenNormalZongzi:
		if role.DelItem(EnumGameConfig.DuanWuJieNormalZongziCoding, 1) < 1:
			return
		role.DecMoney(EnumGameConfig.DuanWuJieNormalPrice)
		#道具
		if rewardConfig.Type == 1:
			role.AddItem(rewardConfig.ItemCode, rewardConfig.Cnt)
			tips += GlobalPrompt.Item_Tips % (rewardConfig.ItemCode, rewardConfig.Cnt)
		#命魂
		elif rewardConfig.Type == 2:
			role.AddTarotCard(rewardConfig.ItemCode, rewardConfig.Cnt)
			tips += GlobalPrompt.Tarot_Tips % (rewardConfig.ItemCode, rewardConfig.Cnt)
		#天赋卡 
		elif rewardConfig.Type == 3:
			for _ in xrange(rewardConfig.Cnt):
				role.AddTalentCard(rewardConfig.ItemCode)
			tips += GlobalPrompt.Talent_Tips % (rewardConfig.ItemCode, rewardConfig.Cnt)
		else:
			return
	role.Msg(2, 0, tips)


def RequestOpenGoldZongzi(role, msg):
	'''
	客户端请求打开黄金粽子
	'''
	if IsStart is False:
		return
	if role.GetLevel() < EnumGameConfig.DuanWuJieNeedLevel:
		return
	if role.ItemCnt(EnumGameConfig.DuanWuJieGoldZongziCoding) < 1:
		return
	if role.GetUnbindRMB() < EnumGameConfig.DuanWuJieGoldPrice:
		return
	
	#当前方案
	currentIndex = role.GetI8(EnumInt8.DuanWuJieGoldZongzi)
	if currentIndex == 0:
		currentIndex = 1
	
	roleLevel = role.GetLevel()
	levelRange = DuanWuJieConfig.LevelRangeDict.get(roleLevel)
	if levelRange is None:
		print "GE_EXC,role(%s) level(%s) error while levelRange = DuanWuJieConfig.LevelRangeDict.get(roleLevel)" % (role.GetRoleID(), roleLevel)
		return
	
	config = DuanWuJieConfig.GoldZongziConfigDict.get((currentIndex, levelRange))
	if config is None:
		print "GE_EXC,error while config = DuanWuJieConfig.GoldZongziConfigDict.get((currentIndex, levelRange))(%s,%s)" % (currentIndex, levelRange)
		return
	
	newIndex = currentIndex
	maxIndex = max([key[0] for key in DuanWuJieConfig.GoldZongziConfigDict.keys()])
	rewardID = config.randomRate.RandomOne()
	if rewardID == config.precious:
		newIndex = newIndex + 1
		if newIndex > maxIndex:
			newIndex = 1
		
	rewardConfig = DuanWuJieConfig.RewardConfigDict.get(rewardID)
	if rewardConfig is None:
		print "GE_EXC,error while rewardConfig = DuanWuJieConfig.RewardConfigDict.get(rewardID) (%s)" % rewardID
		return
	
	needGlobalTell = False
	if rewardConfig.IsBroadcast == 1:
		needGlobalTell = True
	
	globalTell = GlobalPrompt.DuanWuJieGlobalTell % role.GetRoleName()
	tips = GlobalPrompt.DuanWuJieZongzi
	with TraDuanWuJieOpenGoldZongzi:
		if role.DelItem(EnumGameConfig.DuanWuJieGoldZongziCoding, 1) < 1:
			return
		role.DecUnbindRMB(EnumGameConfig.DuanWuJieGoldPrice)
		role.SetI8(EnumInt8.DuanWuJieGoldZongzi, newIndex)
		#道具
		if rewardConfig.Type == 1:
			role.AddItem(rewardConfig.ItemCode, rewardConfig.Cnt)
			tips += GlobalPrompt.Item_Tips % (rewardConfig.ItemCode, rewardConfig.Cnt)
			globalTell += GlobalPrompt.DuanWuJieItem_Tips % (rewardConfig.ItemCode, rewardConfig.Cnt)
		#命魂
		elif rewardConfig.Type == 2:
			role.AddTarotCard(rewardConfig.ItemCode, rewardConfig.Cnt)
			tips += GlobalPrompt.Tarot_Tips % (rewardConfig.ItemCode, rewardConfig.Cnt)
			globalTell += GlobalPrompt.DuanWuJieTarot_Tips % (rewardConfig.ItemCode, rewardConfig.Cnt)
		#天赋卡 
		elif rewardConfig.Type == 3:
			for _ in xrange(rewardConfig.Cnt):
				role.AddTalentCard(rewardConfig.ItemCode)
			tips += GlobalPrompt.Talent_Tips % (rewardConfig.ItemCode, rewardConfig.Cnt)
			globalTell += GlobalPrompt.DuanWuJieTalent_Tips % (rewardConfig.ItemCode, rewardConfig.Cnt)
		else:
			return
	
	role.Msg(2, 0, tips)
	if needGlobalTell:
		globalTell += GlobalPrompt.DuanWuJieLink
		cRoleMgr.Msg(11, 0, globalTell)


def RequestOpenNormalZongziTen(role, msg):
	'''
	客户端请求开十次普通粽子
	'''
	if IsStart is False:
		return
	if role.GetLevel() < EnumGameConfig.DuanWuJieNeedLevel:
		return
	
	if role.ItemCnt(EnumGameConfig.DuanWuJieNormalZongziCoding) < 10:
		return
	
	price = 10 * EnumGameConfig.DuanWuJieNormalPrice
	if role.GetMoney() < price:
		return
	
	roleLevel = role.GetLevel()
	levelRange = DuanWuJieConfig.LevelRangeDict.get(roleLevel)
	if levelRange is None:
		print "GE_EXC,role(%s) level(%s) error while levelRange = DuanWuJieConfig.LevelRangeDict.get(roleLevel)" % (role.GetRoleID(), roleLevel)
		return
	config = DuanWuJieConfig.NormalZongziConfigDict.get(levelRange)
	if config is None:
		print "error while config = DuanWuJieConfig.NormalZongziConfigDict.get(levelRange)(%s)" % levelRange
		return
	
	rewardIDList = []
	for _ in xrange(10):
		rewardID = config.randomRate.RandomOne()
		rewardIDList.append(rewardID)
	
	rewardItemDict = {}
	rewardTarotDict = {}
	rewardTalentCardDict = {}
	for rewardID in rewardIDList:
		rewardConfig = DuanWuJieConfig.RewardConfigDict.get(rewardID)
		if not rewardConfig:
			print "GE_EXC,error while rewardConfig = DuanWuJieConfig.RewardConfigDict.get(rewardID)" % rewardID
			return
		if rewardConfig.Type == 1:
			rewardItemDict[rewardConfig.ItemCode] = rewardItemDict.get(rewardConfig.ItemCode, 0) + rewardConfig.Cnt
		elif rewardConfig.Type == 2:
			rewardTarotDict[rewardConfig.ItemCode] = rewardTarotDict.get(rewardConfig.ItemCode, 0) + rewardConfig.Cnt
		elif rewardConfig.Type == 3:
			rewardTalentCardDict[rewardConfig.ItemCode] = rewardTalentCardDict.get(rewardConfig.ItemCode, 0) + rewardConfig.Cnt
		else:
			return
	
	tips = GlobalPrompt.DuanWuJieZongzi
	with TraDuanWuJieOpenNormalZongziTen:
		if role.DelItem(EnumGameConfig.DuanWuJieNormalZongziCoding, 10) < 10:
			return
		
		role.DecMoney(price)
		for item in rewardItemDict.iteritems():
			role.AddItem(*item)
			tips += GlobalPrompt.Item_Tips % item
		for tarot in rewardTarotDict.iteritems():
			role.AddTarotCard(*tarot)
			tips += GlobalPrompt.Tarot_Tips % tarot
		for talentID, cnt in rewardTalentCardDict.iteritems():
			for _ in xrange(cnt):
				role.AddTalentCard(talentID)
			tips += GlobalPrompt.Talent_Tips % (talentID, cnt)
	
	role.Msg(2, 0, tips)
	

def RequestOpenGoldZongziTen(role, msg):
	'''
	客户端请求打开十次黄金粽子
	'''
	if IsStart is False:
		return
	if role.GetLevel() < EnumGameConfig.DuanWuJieNeedLevel:
		return
	if role.ItemCnt(EnumGameConfig.DuanWuJieGoldZongziCoding) < 10:
		return
	price = 10 * EnumGameConfig.DuanWuJieGoldPrice
	if role.GetUnbindRMB() < price:
		return
	
	roleLevel = role.GetLevel()
	levelRange = DuanWuJieConfig.LevelRangeDict.get(roleLevel)
	if levelRange is None:
		print "GE_EXC,role(%s) level(%s) error while levelRange = DuanWuJieConfig.LevelRangeDict.get(roleLevel)" % (role.GetRoleID(), roleLevel)
		return
	
	#当前方案
	currentIndex = role.GetI8(EnumInt8.DuanWuJieGoldZongzi)
	if currentIndex == 0:
		currentIndex = 1 
	newIndex = currentIndex
	maxIndex = max([key[0] for key in DuanWuJieConfig.GoldZongziConfigDict.keys()])
	
	rewardIDList = []
	for _ in xrange(10):
		config = DuanWuJieConfig.GoldZongziConfigDict.get((newIndex, levelRange))
		if config is None:
			print "GE_EXC,error while config = DuanWuJieConfig.GoldZongziConfigDict.get((newIndex, levelRange)(%s,%s)" % (newIndex, levelRange)
			return
		
		rewardID = config.randomRate.RandomOne()
		
		if rewardID == config.precious:
			newIndex += 1
			if newIndex > maxIndex:
				newIndex = 1
				
		rewardIDList.append(rewardID)
	
	rewardItemDict = {}
	rewardTarotDict = {}
	rewardTalentCardDict = {}
	
	globalTellItemDict = {}
	globalTellTarotDict = {}
	globalTellTalentDict = {}
	for rewardID in rewardIDList:
		rewardConfig = DuanWuJieConfig.RewardConfigDict.get(rewardID)
		if not rewardConfig:
			print "GE_EXC,error while rewardConfig = DuanWuJieConfig.RewardConfigDict.get(rewardID)" % rewardID
			return
		if rewardConfig.Type == 1:
			rewardItemDict[rewardConfig.ItemCode] = rewardItemDict.get(rewardConfig.ItemCode, 0) + rewardConfig.Cnt
			if rewardConfig.IsBroadcast == 1:
				globalTellItemDict[rewardConfig.ItemCode] = globalTellItemDict.get(rewardConfig.ItemCode, 0) + rewardConfig.Cnt
		elif rewardConfig.Type == 2:
			rewardTarotDict[rewardConfig.ItemCode] = rewardTarotDict.get(rewardConfig.ItemCode, 0) + rewardConfig.Cnt
			if rewardConfig.IsBroadcast == 1:
				globalTellTarotDict[rewardConfig.ItemCode] = globalTellTarotDict.get(rewardConfig.ItemCode, 0) + rewardConfig.Cnt
		elif rewardConfig.Type == 3:
			rewardTalentCardDict[rewardConfig.ItemCode] = rewardTalentCardDict.get(rewardConfig.ItemCode, 0) + rewardConfig.Cnt
			if rewardConfig.IsBroadcast == 1:
				globalTellTalentDict[rewardConfig.ItemCode] = globalTellTalentDict.get(rewardConfig.ItemCode, 0) + rewardConfig.Cnt
		else:
			return
		
	tips = GlobalPrompt.DuanWuJieZongzi
	with TraDuanWuJieOpenGoldZongziTen:
		if role.DelItem(EnumGameConfig.DuanWuJieGoldZongziCoding, 10) < 10:
			return
		role.DecUnbindRMB(price)
		role.SetI8(EnumInt8.DuanWuJieGoldZongzi, newIndex)
		
		for item in rewardItemDict.iteritems():
			role.AddItem(*item)
			tips += GlobalPrompt.Item_Tips % item
		for tarot in rewardTarotDict.iteritems():
			role.AddTarotCard(*tarot)
			tips += GlobalPrompt.Tarot_Tips % tarot
		for talentID, cnt in rewardTalentCardDict.iteritems():
			for _ in xrange(cnt):
				role.AddTalentCard(talentID)
			tips += GlobalPrompt.Talent_Tips % (talentID, cnt)
	
	role.Msg(2, 0, tips)
	
	if not(globalTellItemDict or globalTellTarotDict or globalTellTalentDict):
		return
	globalTell = GlobalPrompt.DuanWuJieGlobalTell % role.GetRoleName()
	for item in globalTellItemDict.iteritems():
		globalTell += GlobalPrompt.DuanWuJieItem_Tips % item
	for tarot in globalTellTarotDict.iteritems():
		globalTell += GlobalPrompt.DuanWuJieTarot_Tips % tarot
	for talent in globalTellTalentDict.iteritems():
		globalTell += GlobalPrompt.DuanWuJieTalent_Tips % talent
	globalTell += GlobalPrompt.DuanWuJieLink
	cRoleMgr.Msg(11, 0, globalTell)


def DuanWuJie_ExtendReward(role, param):
	'''
	副本和英灵神殿 通关活动期间概率获得普通粽子
	'''
	if IsStart is False:
		return None
	
	activityType, idx = param
	config = DuanWuJieConfig.ZongziDropConfigDict.get((activityType, idx))
	if not config:
		return None
	rewardDict = {}

	#黄金粽子掉落
	if random.randint(1, 10000) <= config.goldRate:
		rewardDict[config.goldCoding] = 1
	
	#普通粽子掉落
	if random.randint(1, 10000) <= config.normalRate:
		rewardDict[config.normalCoding] = 1
		
	return rewardDict


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, Start)
		Event.RegEvent(Event.Eve_EndCircularActive, End)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestOpenNormalZongziDuanWuJie", "客户端请求开普通粽子"), RequestOpenNormalZongzi)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestOpenGoldZongziDuanWuJie", "客户端请求打开黄金粽子"), RequestOpenGoldZongzi)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestOpenNormalZongziTenDuanWuJie", "客户端请求开十次普通粽子"), RequestOpenNormalZongziTen)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestOpenGoldZongziTenDuanWuJie", "客户端请求打开十次黄金粽子"), RequestOpenGoldZongziTen)
