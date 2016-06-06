#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.NationDay.StrikeBoss")
#===============================================================================
# 击杀国庆boss
#===============================================================================
import cRoleMgr
import Environment
from Game.Role import Event
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from Game.Activity import CircularDefine
from Game.Activity.NationDay import StrikeBossConfig


if "_HasLoad" not in dir():
	
	NeedLevel = 30
	
	#活动开启的标志 
	__IS_START = False
	
	#日志
	Tra_NationDayStrikeBoss = AutoLog.AutoTransaction("Tra_NationDayStrikeBoss", "国庆活动击杀boss")

def StrikeBossStart(*param):
	'''
	击杀boss活动开启
	'''
	_, circularType = param
	if circularType != CircularDefine.CA_NationStrikeBoss:
		return
	global __IS_START
	if __IS_START is True:
		print "GE_EXC, NationDay_StrikeBoss has already been started"
		return
	__IS_START = True

def StrikeBossEnd(*param):
	'''
	击杀boss活动关闭
	'''
	_, circularType = param
	if circularType != CircularDefine.CA_NationStrikeBoss:
		return
	global __IS_START
	if __IS_START is False:
		print "GE_EXC, NationDay_StrikeBoss has already been ended"
		return
	__IS_START = False


def RequestStrikeBoss(role, msg):
	'''
	客户端请求击杀boss
	@param role:
	@param msg:
	'''
	if __IS_START == False:
		return
	#玩家等级不符合要求
	roleLevel = role.GetLevel()
	if roleLevel < NeedLevel:
		return
	bosstype, cnt = msg
	if not cnt in (1, 10):
		return
	#背包空间不足,有可能十次都是不同道具
	if role.PackageEmptySize() < cnt:
		role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
		return
	#命魂背包空间不足,有可能十次都是命魂 
	if role.GetTarotEmptySize() < cnt:
		role.Msg(2, 0, GlobalPrompt.TarotIsFull_Tips)
		return
	section = StrikeBossConfig.StrikeBossSetionDict.get(roleLevel)
	if not section:
		print "GE_EXC, error while section = StrikeBossConfig.StrikeBossSetionDict.get(roleLevel), no such roleLevel(%s)" % roleLevel
		return

	#根据击杀的boss的类型的不同获取不同的随机配置
	bossConfig = StrikeBossConfig.StrikeBossRateDict.get((section, bosstype))
	if not bossConfig:
		print "GE_EXC, error while bossConfig = StrikeBossConfig.StrikeBossRateDict.get((section, bosstype)) in NationDay, no such (section, bosstype)(%s,%s)" % (section, bosstype)
		return
	
	cardID = bossConfig.CostCoding
	totalCostCnt = bossConfig.CostCnt * cnt
	
	#如果玩家的道具不足的话
	if role.ItemCnt(cardID) < totalCostCnt:
		return

	awardItemDict = {}				#存放获取的普通道具的coding和cnt
	awardTarotDict = {}				#存放获取的命魂的coding和cnt
	broadItemList = []				#存放需要全服公告的物品，每次需要公告的击杀公告一次
	broadTarotList = []				#存放需要全服公告的命魂，每次需要公告的击杀公告一次
	
	
	#获取cnt次击杀的奖励,cnt只能是一次或10次
	randomRate = bossConfig.RandomRate
	for _ in xrange(cnt):
		itemIndex = randomRate.RandomOne()
		itemconfig = StrikeBossConfig.StrikeBossConfigDict.get(itemIndex)
		if not itemIndex:
			print "GE_EXC, error while itemconfig = StrikeBossConfig.StrikeBossConfigDict.get(itemIndex), no such itemIdex(%s)" % itemIndex
			return
		
		itemCoding, itemCnt = itemconfig.Item
		#普通道具
		if itemconfig.Type == 1:
			awardItemDict[itemCoding] = awardItemDict.get(itemCoding, 0) + itemCnt
			#是否需要公告
			if itemconfig.IsBroadcast == 1:
				broadItemList.append((itemCoding, itemCnt))
		
		#命魂 
		elif itemconfig.Type == 2:
			awardTarotDict[itemCoding] = awardTarotDict.get(itemCoding, 0) + itemCnt
			#是否需要公告
			if itemconfig.IsBroadcast == 1:
				broadTarotList.append((itemCoding, itemCnt))
	#精英boss
	if bosstype == 1:
		Tips = GlobalPrompt.ND_StrikeBoss_KillNormal % cnt
	elif bosstype == 2:
		Tips = GlobalPrompt.ND_StrikeBoss_KillElite % cnt
	else:
		return
		

	with Tra_NationDayStrikeBoss:
		#扣除物品
		if role.DelItem(cardID, totalCostCnt) < totalCostCnt:
			return
		#发放普通道具奖励
		for propCoding, propCnt in awardItemDict.iteritems():
			if propCnt > 0:
				role.AddItem(propCoding, propCnt)
				Tips += GlobalPrompt.Item_Tips % (propCoding, propCnt)
		#发放命魂奖励
		for tarotCoding, tarotCnt in awardTarotDict.iteritems():
			if tarotCnt > 0:
				role.AddTarotCard(tarotCoding, tarotCnt)
				Tips += GlobalPrompt.Tarot_Tips % (tarotCoding, tarotCnt)
	
	role.Msg(2, 0, Tips)
	#全服公告,这里策划要求每次击杀单独做一次公告
	roleName = role.GetRoleName()
	#普通道具的公告
	for icoding, icnt in broadItemList:
		if icnt > 0:
			cRoleMgr.Msg(1, 0, GlobalPrompt.ND_StrikeBoss_item_ServerTell % (roleName, icoding, icnt))
	#命魂的公告
	for tcoding, tcnt in broadTarotList:
		if tcnt > 0:
			cRoleMgr.Msg(1, 0, GlobalPrompt.ND_StrikeBoss_tarot_ServerTell % (roleName, tcoding, tcnt))


if "_HasLoad" not in dir():
	if not Environment.IsCross and Environment.HasLogic:
		Event.RegEvent(Event.Eve_StartCircularActive, StrikeBossStart)
		Event.RegEvent(Event.Eve_EndCircularActive, StrikeBossEnd)
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestNationDay_StrikeBoss", "国庆活动请求击杀boss"), RequestStrikeBoss)
		
