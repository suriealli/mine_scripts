#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DoubleEleven.SeckillMgr")
#===============================================================================
# 注释
#===============================================================================
import datetime
import cComplexServer
import cDateTime
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Activity import CircularDefine
from Game.Activity.DoubleEleven import SeckillConfig
from Game.Role import Event
from Game.SysData import WorldData

if "_HasLoad" not in dir():
	IS_START = False		#活动是否开启
	WORLD_LEVEL = 0			#当前波数世界等级
	WAVE = 0				#当前波数
	
	LIMIT_CNT_ITEM_DICT = {}	#限购物品数量字典
	LIMIT_TIME_ITEM_LIST = []	#限时物品列表
	
	#消息
	Seckill_Show_Panel = AutoMessage.AllotMessage("Seckill_Show_Panel", "通知客户端显示双十一秒杀汇面板")
	
def ShowSeckillPanel(role):
	role.SendObj(Seckill_Show_Panel, (WORLD_LEVEL, WAVE, LIMIT_CNT_ITEM_DICT))
	
def SeckillBuy(role, itemDataId):
	global LIMIT_CNT_ITEM_DICT
	global LIMIT_TIME_ITEM_LIST
	
	itemDataConfig = SeckillConfig.SECKILL_ITEM.get(itemDataId)
	if not itemDataConfig:
		return
	
	if itemDataConfig.isLimitCnt:
		#是否有限购数量信息
		if itemDataId not in LIMIT_CNT_ITEM_DICT:
			return
		
		#是否已经卖完
		cnt = LIMIT_CNT_ITEM_DICT[itemDataId]
		if cnt <= 0:
			#刷新面板
			ShowSeckillPanel(role)
			#提示
			role.Msg(2, 0, GlobalPrompt.SECKILL_ITEM_CNT_OVER_PROMPT)
			return
		
		#RMB判断
		currentPrict = itemDataConfig.currentPrice
		if itemDataConfig.isNeedUnbindRMB_Q:
			if role.GetUnbindRMB_Q() < currentPrict:
				return
			role.DecUnbindRMB_Q(currentPrict)
		else:
			if role.GetUnbindRMB() < currentPrict:
				return
			role.DecUnbindRMB(currentPrict)
			
		LIMIT_CNT_ITEM_DICT[itemDataId] = cnt - 1
		
		role.AddItem(itemDataConfig.itemCoding, itemDataConfig.itemCnt)
		
	elif itemDataConfig.isLimitTime:
		#是否有限时信息
		if itemDataId not in LIMIT_TIME_ITEM_LIST:
			#提示
			role.Msg(2, 0, GlobalPrompt.SECKILL_ITEM_TIME_OVER_PROMPT)
			return
		
		#RMB判断
		currentPrict = itemDataConfig.currentPrice
		if itemDataConfig.isNeedUnbindRMB_Q:
			if role.GetUnbindRMB_Q() < currentPrict:
				return
			role.DecUnbindRMB_Q(currentPrict)
		else:
			if role.GetUnbindRMB() < currentPrict:
				return
			role.DecUnbindRMB(currentPrict)
		
		role.AddItem(itemDataConfig.itemCoding, itemDataConfig.itemCnt)
		
	#刷新面板
	ShowSeckillPanel(role)
	
def NextWave():
	global WORLD_LEVEL
	global WAVE
	global LIMIT_CNT_ITEM_DICT
	global LIMIT_TIME_ITEM_LIST
	
	worldLevel = WorldData.GetWorldLevel()
	if worldLevel not in SeckillConfig.SECKILL_WORLD_LEVEL_TO_WAVE_BASE:
		return
	waveConfigDict = SeckillConfig.SECKILL_WORLD_LEVEL_TO_WAVE_BASE[worldLevel]
	#是否开启下一波秒杀
	nextWaveConfig = waveConfigDict.get(WAVE + 1)
	if not nextWaveConfig:
		return
	
	nowDateTime = cDateTime.Now()
	startDateTime = datetime.datetime(*nextWaveConfig.startDate)
	endDateTime = datetime.datetime(*nextWaveConfig.endDate)
	
	if nowDateTime >= startDateTime and nowDateTime < endDateTime:
		WORLD_LEVEL = worldLevel
		WAVE += 1
	else:
		return
	
	#生成限购数量物品信息
	LIMIT_CNT_ITEM_DICT = {}
	LIMIT_TIME_ITEM_LIST = []
	for itemDataId in nextWaveConfig.itemData:
		itemDataConfig = SeckillConfig.SECKILL_ITEM.get(itemDataId)
		if not itemDataConfig:
			continue
		
		#判断是否限购物品
		if itemDataConfig.isLimitCnt:
			LIMIT_CNT_ITEM_DICT[itemDataId] = itemDataConfig.limitCnt
		
		if itemDataConfig.isLimitTime:
			cComplexServer.RegTick(itemDataConfig.limitTime, ItemTimeOver, itemDataId)
			LIMIT_TIME_ITEM_LIST.append(itemDataId)
	
	#刷新面板数据
	for role in cRoleMgr.GetAllRole():
		ShowSeckillPanel(role)
	
	#传闻
	cRoleMgr.Msg(1, 0, GlobalPrompt.SECKILL_START_HEARSAY)

#===============================================================================
# 时间
#===============================================================================
def PerMinute():
	global WAVE
	global LIMIT_CNT_ITEM_DICT
	global LIMIT_TIME_ITEM_LIST
	
	if IS_START is False:
		return
	
	#是否开启下一波秒杀
	NextWave()
		
def ItemTimeOver(callArgv, regparam):
	'''
	物品限时结束
	@param callArgv:
	@param regparam:
	'''
	global LIMIT_TIME_ITEM_LIST
	
	itemDataId = regparam
	if itemDataId in LIMIT_TIME_ITEM_LIST:
		LIMIT_TIME_ITEM_LIST.remove(itemDataId)
	
	
#===============================================================================
# 事件
#===============================================================================
def SeckillStart(*param):
	'''
	双十一秒杀汇活动开启
	'''
	_, circularType = param
	if circularType != CircularDefine.CA_Seckill:
		return
	
	global IS_START
	
	if IS_START is True:
		print "GE_EXC, Seckill is already start"
		return
	
	IS_START = True
	

def SeckillEnd(*param):
	'''
	双十一秒杀汇活动关闭
	'''
	_, circularType = param
	if circularType != CircularDefine.CA_Seckill:
		return
	
	global IS_START
	if IS_START is False:
		print "GE_EXC, Seckill is already end"
		return
	
	IS_START = False
	
#===============================================================================
# 消息
#===============================================================================
def RequestSeckillOpenPanel(role, msg):
	'''
	客户端请求打开双十一秒杀汇面板
	@param role:
	@param msg:
	'''
	ShowSeckillPanel(role)

def RequestSeckillBuy(role, msg):
	'''
	客户端请求打开双十一秒杀汇购买
	@param role:
	@param msg:
	'''
	#活动是否开始
	if IS_START is False:
		return
	
	itemDataId = msg
	
	#日志
	with TraSeckillBuy:
		SeckillBuy(role, itemDataId)

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#注册每分钟调用
		if Environment.IsDevelop or Environment.EnvIsTK() or Environment.EnvIsRU():
			cComplexServer.RegAfterNewMinuteCallFunction(PerMinute)
		
		#事件
		Event.RegEvent(Event.Eve_StartCircularActive, SeckillStart)
		Event.RegEvent(Event.Eve_EndCircularActive, SeckillEnd)
		
		#日志
		TraSeckillBuy = AutoLog.AutoTransaction("TraSeckillBuy", "双十一秒杀汇购买")
		
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Seckill_Open_Panel", "客户端请求打开双十一秒杀汇面板"), RequestSeckillOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Seckill_Buy", "客户端请求打开双十一秒杀汇购买"), RequestSeckillBuy)
		
		
		
		
