#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DragonStele.DragonSteleMgr")
#===============================================================================
# 龙魂石碑Mgr
#===============================================================================
import random
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Role.Data import EnumInt16
from Game.Activity import CircularDefine
from Game.Activity.DragonStele import DragonSteleConfig

NOMAL_PRAY = 1
SPECIAL_PRAY = 2
EXTRA_PRAY = 3

ITEM_TYPE_PRO = 1	#普通道具
ITEM_TYPE_TAROT = 2	#命魂

if "_HasLoad" not in dir():
	IS_START = False	#龙魂石碑开关标志
	
	Tra_DragonStelePray_Nomal = AutoLog.AutoTransaction("Tra_DragonStelePray_Nomal","龙魂石碑普通祈祷")
	Tra_DragonStelePray_Special = AutoLog.AutoTransaction("Tra_DragonStelePray_Special","龙魂石碑高级祈祷")
	Tra_DragonStelePray_Extra = AutoLog.AutoTransaction("Tra_DragonStelePray_Extra","龙魂石碑百次高级祈祷额外获得")

def OnStartDragonStele(*param):
	'''
	开启龙魂石碑
	'''
	_, circularType = param
	if circularType != CircularDefine.CA_DragonStele:
		return
	
	# 已开启 
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open DragonStele"
		return
		
	IS_START = True	

def OnEndDragonStele(*param):
	'''
	关闭龙魂石碑
	'''
	_, circularType = param
	if circularType != CircularDefine.CA_DragonStele:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC,end dragonStele while not open "
		return
		
	IS_START = False	

def OnNomalPray(role, param = 0):
	'''
	龙魂石碑普通祈祷
	'''
	if not IS_START:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.DragonStele_NeedLevel:
		return
	
	#是否批量祈祷
	isBatch = param
	
	prayTimes = 1	
	if isBatch:
		prayTimes = EnumGameConfig.DragonStele_BatchTimes
	
	needProCnt = prayTimes
	needMoney = 0
	if Environment.EnvIsNA():
		needMoney = prayTimes * EnumGameConfig.DragonStele_PrayMoney_NA
	else:
		needMoney = prayTimes * EnumGameConfig.DragonStele_PrayMoney
	if role.GetMoney() < needMoney:
		return
	
	if role.ItemCnt(EnumGameConfig.DragonStele_PrayPro_Nomal) < needProCnt:
		return
	
	rewardDict = GetRewardByTypeLevelTimes(NOMAL_PRAY, roleLevel, prayTimes)
	if not rewardDict:
		print "GE_EXC,OnNomalPray::can not get rewardDict with rewardType(%s), roleLevel(%s), prayTimes(%s)" % (NOMAL_PRAY, roleLevel, prayTimes)
		return
	
	with Tra_DragonStelePray_Nomal:
		#扣除金币
		role.DecMoney(needMoney)
		#消耗道具
		role.DelItem(EnumGameConfig.DragonStele_PrayPro_Nomal, needProCnt)
		#增加今日普通祈祷次数
		role.IncI16(EnumInt16.DragonSteleNomalTimes, prayTimes)
		
		#获得奖励 并 提示 
		allItemPrompt = ""
		preciousItemMsg = ""
		for coding, cnt, itemType, isPrecious in rewardDict.values():
			if itemType == ITEM_TYPE_PRO:
				role.AddItem(coding, cnt)
				allItemPrompt += GlobalPrompt.DragonStele_Tips_Item % (coding, cnt)
			elif itemType == ITEM_TYPE_TAROT:
				role.AddTarotCard(coding, cnt)
				allItemPrompt += GlobalPrompt.DragonStele_Tips_Tarot % (coding, cnt)
			else:
				pass
			
			if isPrecious:
				if len(preciousItemMsg) > 0:
					preciousItemMsg += GlobalPrompt.DragonStele_Msg_Sep
				
				if itemType == ITEM_TYPE_PRO:
					preciousItemMsg += GlobalPrompt.DragonStele_Msg_Item % (coding, cnt)
				elif itemType == ITEM_TYPE_TAROT:
					allItemPrompt += GlobalPrompt.DragonStele_Msg_Tarot % (coding, cnt)
				else:
					pass
		
		rewardPrompt = GlobalPrompt.DragonStele_Tips_Head + allItemPrompt
		role.Msg(2, 0, rewardPrompt)
		
		#珍惜获得广播
		if len(preciousItemMsg) > 0:
			rewardMsg = GlobalPrompt.DragonStele_Msg_Precious % (role.GetRoleName(), preciousItemMsg)
			cRoleMgr.Msg(11, 0, rewardMsg)
		else:
			pass
		
def OnSpecialPray(role, param = 0):
	'''
	龙魂石碑高级祈祷
	'''
	if not IS_START:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.DragonStele_NeedLevel:
		return
	
	#是否批量祈祷
	isBatch = param
	
	prayTimes = 1
	if isBatch:
		prayTimes = EnumGameConfig.DragonStele_BatchTimes
	
	needProCnt = prayTimes	
	haveProCnt = role.ItemCnt(EnumGameConfig.DragonStele_PrayPro_Special)
	toConsumeCnt = needProCnt
	needUnbindRMB = 0
	if haveProCnt < needProCnt:
		#道具不足 神石补上
		toConsumeCnt = haveProCnt
		if Environment.EnvIsNA():
			needUnbindRMB = (needProCnt - haveProCnt) * EnumGameConfig.DragonStele_PrayRMB_NA
		else:
			needUnbindRMB = (needProCnt - haveProCnt) * EnumGameConfig.DragonStele_PrayRMB
		if role.GetUnbindRMB() < needUnbindRMB:
			return
	
	#产出随机奖励
	rewardDict = GetRewardByTypeLevelTimes(SPECIAL_PRAY, roleLevel, prayTimes)
	if not rewardDict:
		print "GE_EXC,OnSpecialPray::can not get rewardDict with rewardType(%s), roleLevel(%s), prayTimes(%s)" % (SPECIAL_PRAY, roleLevel, prayTimes)
		return
	
	#统计所需额外奖励次数
	extraRewardTimes = 0
	todayPrayTimes = role.GetI16(EnumInt16.DragonSteleSpecialTime)
	for _ in xrange(prayTimes):
		todayPrayTimes += 1
		if todayPrayTimes > 0 and todayPrayTimes % EnumGameConfig.DragonStele_ExtraBoundary == 0:
			extraRewardTimes += 1
	
	#产出额外奖励
	if extraRewardTimes > 0:
		extraRewardDict = GetRewardByTypeLevelTimes(EXTRA_PRAY, roleLevel, extraRewardTimes)
		if not extraRewardDict:
			print "GE_EXC,OnSpecialPray::can not get extraRewardDict with rewardType(%s), roleLevel(%s), prayTimes(%s)" % (SPECIAL_PRAY, roleLevel, prayTimes)
			return
		
	with Tra_DragonStelePray_Special:
		#扣除神石
		if needUnbindRMB > 0:
			role.DecUnbindRMB(needUnbindRMB)
		#消耗道具
		if toConsumeCnt > 0:
			role.DelItem(EnumGameConfig.DragonStele_PrayPro_Special, toConsumeCnt)
		#增加今日高级祈祷次数
		role.IncI16(EnumInt16.DragonSteleSpecialTime, prayTimes)
		
		#获得随机奖励 并 提示 
		allItemPrompt = ""
		preciousItemMsg = ""
		for coding, cnt, itemType, isPrecious in rewardDict.values():
			if itemType == ITEM_TYPE_PRO:
				role.AddItem(coding, cnt)
				allItemPrompt += GlobalPrompt.DragonStele_Tips_Item % (coding, cnt)
			elif itemType == ITEM_TYPE_TAROT:
				role.AddTarotCard(coding, cnt)
				allItemPrompt += GlobalPrompt.DragonStele_Tips_Tarot % (coding, cnt)
			else:
				pass
			
			if isPrecious:
				if len(preciousItemMsg) > 0:
					preciousItemMsg += GlobalPrompt.DragonStele_Msg_Sep
				if itemType == ITEM_TYPE_PRO:
					preciousItemMsg += GlobalPrompt.DragonStele_Msg_Item % (coding, cnt)
				elif itemType == ITEM_TYPE_TAROT:
					preciousItemMsg += GlobalPrompt.DragonStele_Msg_Tarot % (coding, cnt)
		
		rewardPrompt = GlobalPrompt.DragonStele_Tips_Head + allItemPrompt
		role.Msg(2, 0, rewardPrompt)
		
		#珍惜获得广播
		if len(preciousItemMsg) > 0:
			rewardMsg = GlobalPrompt.DragonStele_Msg_Precious % (role.GetRoleName(), preciousItemMsg)
			cRoleMgr.Msg(11, 0, rewardMsg)
		else:
			pass
		
		#获得额外奖励 并 广播
		if extraRewardTimes > 0:
			extraItemMsg = ""
			with Tra_DragonStelePray_Extra:
				for coding, cnt, itemType, isPrecious in extraRewardDict.values():
					if len(extraItemMsg) > 0:
						extraItemMsg += GlobalPrompt.DragonStele_Msg_Sep
					
					if itemType == ITEM_TYPE_PRO:
						role.AddItem(coding, cnt)
						extraItemMsg += GlobalPrompt.DragonStele_Msg_Item % (coding, cnt)
					elif itemType == ITEM_TYPE_TAROT:
						role.AddTarotCard(coding, cnt)
						extraItemMsg += GlobalPrompt.DragonStele_Msg_Tarot % (coding, cnt)
					else:
						pass
			
			cRoleMgr.Msg(11, 0, GlobalPrompt.DragonStele_Msg_Extra % (role.GetRoleName(), extraItemMsg))

def GetRewardByTypeLevelTimes(rewardType = NOMAL_PRAY, roleLevel = 1, prayTimes = 1):
	'''
	获取随机奖励dict
	@param rewardType:奖励类型
	@param roleLevel: 玩家等级
	@param prayTimes: 祈祷次数 
	@return: rewardDict {coding:(coding,cnt,itemType,isPrecious),}
	'''
	rewardRandomer = DragonSteleConfig.GetRandomOne(rewardType, roleLevel)
	if not rewardRandomer or not len(rewardRandomer.randomList):
		return
	
	#随机奖励并归并数量
	rewardDict = {}
	for _ in xrange(prayTimes):
		#百次高级祈祷额外 获得全部奖励
		if rewardType == EXTRA_PRAY:
			for _, reward in rewardRandomer.randomList:
				_, _, _, coding, cnt, itemType, isPrecious = reward
				if coding in rewardDict:
					cnt += rewardDict[coding][1]		
				rewardDict[coding] = (coding, cnt, itemType, isPrecious)
		elif rewardType == NOMAL_PRAY or rewardType == SPECIAL_PRAY:
			_, _, _, coding, cnt, itemType, isPrecious = rewardRandomer.RandomOne()
			if coding in rewardDict:
				cnt += rewardDict[coding][1]		
			rewardDict[coding] = (coding, cnt, itemType, isPrecious)
		else:
			pass
	
	return rewardDict

def DragonStele_ExtendReward(role, param):
	'''
	副本和英灵神殿 通关活动期间概率获得银龙币
	'''
	global IS_START
	if not IS_START:
		return None
	
	activityType, idx = param	
	cfg = DragonSteleConfig.DRAGONSTELE_DROP_CONFIG_DICT.get((activityType, idx))
	if not cfg:
		return None
	
	rewardDict = {}
	#龙币掉落
	if random.randint(1, 10000) <= cfg.dropRate:
		rewardDict[cfg.proCoding] = 1
	
	return rewardDict

def OnRoleDayClear(role, param = None):
	'''
	重置今日祈祷次数
	'''
	#普通祈祷次数
	role.SetI16(EnumInt16.DragonSteleNomalTimes, 0)
	#高级祈祷次数
	role.SetI16(EnumInt16.DragonSteleSpecialTime, 0)

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
		
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartDragonStele)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndDragonStele)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DragonStele_OnNomalPray", "龙魂石碑普通祈祷请求"), OnNomalPray) 
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DragonStele_OnSpecialPray", "龙魂石碑高级祈祷请求"), OnSpecialPray)