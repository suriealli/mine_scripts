#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.GodsTreasure.GodsTreasureMgr")
#===============================================================================
# 众神秘宝管理
#===============================================================================
import random
import cDateTime
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Activity import CircularDefine
from Game.Activity.GodsTreasure import GodsTreasureConfig
from Game.Role import Event
from Game.Role.Data import EnumObj, EnumInt16

if "_HasLoad" not in dir():
	IS_START = False		#活动是否开启
	
	NOT_OPEN = 1
	HAS_OPENED = 0
	
	#消息
	Gods_Treasure_Show_Panel = AutoMessage.AllotMessage("Gods_Treasure_Show_Panel", "通知客户端显示众神秘宝面板")

def ShowGodsTreasurePanel(role):
	gtDict = role.GetObj(EnumObj.GodsTreasure)
	
	if not gtDict:
		InitGodsTreasure(role)
	elif role.GetI16(EnumInt16.GodTreasureUpdateDays) != cDateTime.Days():
		InitGodsTreasure(role)
	elif NOT_OPEN not in gtDict.values():
		InitGodsTreasure(role)
				
	#同步客户端
	role.SendObj(Gods_Treasure_Show_Panel, gtDict)
		
def InitGodsTreasure(role):
	gtDict = role.GetObj(EnumObj.GodsTreasure)
	
	#清空
	gtDict.clear()
	
	#设置清理时间
	role.SetI16(EnumInt16.GodTreasureUpdateDays, cDateTime.Days())
	
	#15个位置随机9个位置
	posIdList = random.sample([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15], 9)
	
	for posId in posIdList:
		gtDict[posId] = NOT_OPEN	#初始化为未开启状态
		
def GodsTreasureSearch(role, treasureType, posId):
	gtDict = role.GetObj(EnumObj.GodsTreasure)
	
	#是否已经开启
	if posId not in gtDict:
		return
	if gtDict[posId] == HAS_OPENED:
		return
	
	baseConfig = GodsTreasureConfig.GODS_TREASURE_BASE.get(treasureType)
	if not baseConfig:
		return
	
	#判断条件
	if role.ItemCnt(baseConfig.needItemCoding) < 1:
		return
	if role.GetMoney() < baseConfig.needMoney:
		return
	
	#扣除道具
	role.DelItem(baseConfig.needItemCoding, 1)
	#扣除金币
	if baseConfig.needMoney:
		role.DecMoney(baseConfig.needMoney)
	
	#设置为已开启
	gtDict[posId] = HAS_OPENED
	
	#奖励
	rewardId = baseConfig.randomObj.RandomOne()
	rewardConfig = GodsTreasureConfig.GODS_TREASURE_REWARD.get(rewardId)
	if not rewardConfig:
		return
	role.AddItem(rewardConfig.rewardItemCoding, rewardConfig.rewardItemCnt)
	
	#提示
	prompt = GlobalPrompt.GODS_TREASURE_ONE_SUCCESS_PROMPT % (rewardConfig.rewardItemCoding, rewardConfig.rewardItemCnt)
	role.Msg(2, 0, prompt)
	
	#是否传闻
	if rewardConfig.isHearsay:
		cRoleMgr.Msg(3, 0, GlobalPrompt.GODS_TREASURE_GOOD_ITEM_HEARSAY % (role.GetRoleName(), rewardConfig.rewardItemCoding, rewardConfig.rewardItemCnt))
	
	#同步面板
	ShowGodsTreasurePanel(role)
	
def GodsTreasureFastSearch(role, treasureType):
	gtDict = role.GetObj(EnumObj.GodsTreasure)
	
	if not gtDict:
		return
	
	#探宝次数
	searchCnt = gtDict.values().count(NOT_OPEN)
	if searchCnt == 0:
		return
	
	baseConfig = GodsTreasureConfig.GODS_TREASURE_BASE.get(treasureType)
	if not baseConfig:
		return
	
	#判断条件
	if role.ItemCnt(baseConfig.needItemCoding) < searchCnt:
		return
	totalNeedMoney = baseConfig.needMoney * searchCnt
	if role.GetMoney() < totalNeedMoney:
		return
	
	#扣除道具
	role.DelItem(baseConfig.needItemCoding, searchCnt)
	#扣除金币
	if totalNeedMoney:
		role.DecMoney(totalNeedMoney)
	
	#清空数据
	gtDict.clear()
	
	itemPrompt = ""
	for _ in xrange(searchCnt):
		#奖励
		rewardId = baseConfig.randomObj.RandomOne()
		rewardConfig = GodsTreasureConfig.GODS_TREASURE_REWARD.get(rewardId)
		if not rewardConfig:
			return
		role.AddItem(rewardConfig.rewardItemCoding, rewardConfig.rewardItemCnt)
		
		#物品提示
		itemPrompt += GlobalPrompt.GODS_TREASURE_ITEM_PROMPT % (rewardConfig.rewardItemCoding, rewardConfig.rewardItemCnt)
		
		#是否传闻
		if rewardConfig.isHearsay:
			cRoleMgr.Msg(3, 0, GlobalPrompt.GODS_TREASURE_GOOD_ITEM_HEARSAY % (role.GetRoleName(), rewardConfig.rewardItemCoding, rewardConfig.rewardItemCnt))
	
	#提示
	role.Msg(2, 0, GlobalPrompt.GODS_TREASURE_SUCCESS_PROMPT % itemPrompt)
	
	#同步面板
	ShowGodsTreasurePanel(role)
	
#===============================================================================
# 探宝器掉落
#===============================================================================
def TreasureDetector_ExtendReward(role, param):
	#活动是否开始
	global IS_START
	if IS_START is False:
		return None
	
	activityType, idx = param
	
	oddsConfig = GodsTreasureConfig.TREASURE_DETECTOR.get((activityType, idx))
	if not oddsConfig:
		return None
	
	rewardDict = {}
	#探宝器掉落
	if role.GetLevel() >= oddsConfig.needLevel:
		if random.randint(1, 10000) <= oddsConfig.dropOdds:
			rewardDict[oddsConfig.dropItemCoding] = 1
	
	return rewardDict
	
#===============================================================================
# 事件
#===============================================================================
def GodsTreasureStart(*param):
	'''
	众神秘宝活动开启
	'''
	_, circularType = param
	if circularType != CircularDefine.CA_GodsTreasure:
		return
	
	global IS_START
	if IS_START is True:
		print "GE_EXC, GodsTreasure is already start"
		return
	
	IS_START = True


def GodsTreasureEnd(*param):
	'''
	众神秘宝活动关闭
	'''
	_, circularType = param
	if circularType != CircularDefine.CA_GodsTreasure:
		return
	
	global IS_START
	if IS_START is False:
		print "GE_EXC, GodsTreasure is already end"
		return
	
	IS_START = False
	
#===============================================================================
# 客户端请求
#===============================================================================
def RequestGodsTreasureOpenPanel(role, msg):
	'''
	客户端请求打开众神秘宝面板
	@param role:
	@param msg:
	'''
	#活动是否开始
	if IS_START is False:
		return
	
	ShowGodsTreasurePanel(role)

def RequestGodsTreasureSearch(role, msg):
	'''
	客户端请求众神秘宝探宝
	@param role:
	@param msg:
	'''
	#活动是否开始
	if IS_START is False:
		return
	
	treasureType, idx = msg
	
	#日志
	with TraGodsTreasureSearch:
		GodsTreasureSearch(role, treasureType, idx)
	
	
def RequestGodsTreasureFastSearch(role, msg):
	'''
	客户端请求众神秘宝一键探宝
	@param role:
	@param msg:
	'''
	#活动是否开始
	if IS_START is False:
		return
	
	treasureType = msg
	
	#日志
	with TraGodsTreasureFastSearch:
		GodsTreasureFastSearch(role, treasureType)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#事件
		Event.RegEvent(Event.Eve_StartCircularActive, GodsTreasureStart)
		Event.RegEvent(Event.Eve_EndCircularActive, GodsTreasureEnd)
		
		#日志
		TraGodsTreasureSearch = AutoLog.AutoTransaction("TraGodsTreasureSearch", "众神秘宝探宝")
		TraGodsTreasureFastSearch = AutoLog.AutoTransaction("TraGodsTreasureFastSearch", "众神秘宝一键探宝")
		
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Gods_Treasure_Open_Panel", "客户端请求打开众神秘宝面板"), RequestGodsTreasureOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Gods_Treasure_Search", "客户端请求众神秘宝探宝"), RequestGodsTreasureSearch)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Gods_Treasure_Fast_Search", "客户端请求众神秘宝一键探宝"), RequestGodsTreasureFastSearch)
		
		