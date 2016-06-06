#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DragonEgg.DragonEggMgr")
#===============================================================================
# 注释
#===============================================================================
import random
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Activity import CircularDefine
from Game.Activity.DragonEgg import DragonEggConfig
from Game.Role import Event
from Game.Role.Data import EnumInt16

if "_HasLoad" not in dir():
	NEED_LEVEL = 30
	BUY_GOLD_EGG_CNT_MAX = 3		#购买金龙蛋超过此值价格不变
	
	EGG_TYPE_TO_CODING = {1: 26300, 2: 26301}	#龙蛋类型索引物品coding
	
	DRAGON_EGG_NEWS = []			#龙蛋新闻
	DRAGON_EGG_NEWS_CNT_MAX = 10	#最大新闻数量
	
	IS_START = False		#活动是否开启
	
	#消息
	Dragon_Egg_Show_Panel = AutoMessage.AllotMessage("Dragon_Egg_Show_Panel", "通知客户端显示砸龙蛋面板")

def ShowDragonEggPanel(role):
	role.SendObj(Dragon_Egg_Show_Panel, DRAGON_EGG_NEWS)

def DragonEggBreak(role, eggType, backFunId):
	eggCoding = EGG_TYPE_TO_CODING.get(eggType)
	if not eggCoding:
		return
	
	#是否有龙蛋
	itemCnt = role.ItemCnt(eggCoding)
	if itemCnt <= 0:
		return
	
	level = role.GetLevel()
	#获取配置
	eggConfigDict = DragonEggConfig.EGG_REWARD.get(eggType)
	if not eggConfigDict:
		return
	randomObj = eggConfigDict.get(level)
	if not randomObj:
		return
	
	#是否满足消耗条件
	if eggType == 1:
		#日志
		with TraDragonGoldEggBreak:
			GoldEggBreak(role, backFunId, eggType, eggCoding, randomObj)
	elif eggType == 2:
		#日志
		with TraDragonSilverEggBreak:
			SilverEggBreak(role, backFunId, eggType, eggCoding, randomObj)
	
def GoldEggBreak(role, backFunId, eggType, eggCoding, randomObj):
	#金龙蛋
	breakGoldDragonEggCnt = role.GetI16(EnumInt16.GoldDragonEggBreakCnt)
	
	#金龙蛋消耗配置
	goldEggConsumeConfig = None
	if breakGoldDragonEggCnt >= 3:
		goldEggConsumeConfig = DragonEggConfig.GOLD_EGG_CONSUME.get(3)
	else:
		goldEggConsumeConfig = DragonEggConfig.GOLD_EGG_CONSUME.get(breakGoldDragonEggCnt + 1)
	if not goldEggConsumeConfig:
		return
		
	#RMB是否足够
	if role.GetUnbindRMB() < goldEggConsumeConfig.needRMB:
		return
	
	#砸金龙蛋次数增加
	role.IncI16(EnumInt16.GoldDragonEggBreakCnt, 1)
	
	#扣RMB
	role.DecUnbindRMB(goldEggConsumeConfig.needRMB)
	
	#扣物品
	role.DelItem(eggCoding, 1)
	
	#随机
	rewardCoding, rewardCnt, isHearsay = randomObj.RandomOne()
	
	#奖励
	role.AddItem(rewardCoding, rewardCnt)
	
	#回调客户端
	role.CallBackFunction(backFunId, (rewardCoding, rewardCnt, eggType))
	
	#奖励是否需要公告
	if isHearsay:
		cRoleMgr.Msg(1, 0, GlobalPrompt.DRAGON_REWARD_HEARSAY % (role.GetRoleName(), rewardCoding, rewardCnt))
	
	#保存砸龙蛋信息
	global DRAGON_EGG_NEWS
	DRAGON_EGG_NEWS.insert(0, (role.GetRoleID(), role.GetRoleName(), role.GetLevel(), 
							role.GetSex(), role.GetCareer(), role.GetGrade(), rewardCoding, rewardCnt))
	#最多只能保存10条
	if len(DRAGON_EGG_NEWS) > DRAGON_EGG_NEWS_CNT_MAX:
		DRAGON_EGG_NEWS.pop()
	
	#显示主面板
	ShowDragonEggPanel(role)

def SilverEggBreak(role, backFunId, eggType, eggCoding, randomObj):
	#银龙蛋
	#金币是否足够
	if Environment.EnvIsNA():
		if role.GetMoney() < EnumGameConfig.SILVER_EGG_NEED_MONEY_NA:
			return
		#扣金币
		role.DecMoney(EnumGameConfig.SILVER_EGG_NEED_MONEY_NA)
	else:
		if role.GetMoney() < EnumGameConfig.SILVER_EGG_NEED_MONEY:
			return
		#扣金币
		role.DecMoney(EnumGameConfig.SILVER_EGG_NEED_MONEY)
	
	#扣物品
	role.DelItem(eggCoding, 1)
	
	#随机
	rewardCoding, rewardCnt, isHearsay = randomObj.RandomOne()
	
	#奖励
	role.AddItem(rewardCoding, rewardCnt)
	
	#回调客户端
	role.CallBackFunction(backFunId, (rewardCoding, rewardCnt, eggType))
	
	#奖励是否需要公告
	if isHearsay:
		cRoleMgr.Msg(1, 0, GlobalPrompt.DRAGON_REWARD_HEARSAY % (role.GetRoleName(), rewardCoding, rewardCnt))
	
	#保存砸龙蛋信息
	global DRAGON_EGG_NEWS
	DRAGON_EGG_NEWS.insert(0, (role.GetRoleID(), role.GetRoleName(), role.GetLevel(), 
							role.GetSex(), role.GetCareer(), role.GetGrade(), rewardCoding, rewardCnt))
	#最多只能保存10条
	if len(DRAGON_EGG_NEWS) > DRAGON_EGG_NEWS_CNT_MAX:
		DRAGON_EGG_NEWS.pop()
	
	#显示主面板
	ShowDragonEggPanel(role)
	
#===============================================================================
# 其它玩法掉落龙蛋
#===============================================================================
def DragonEgg_ExtendReward(role, param):
	#活动是否开始
	if IS_START is False:
		return None
	
	activityType, idx = param
	
	oddsConfig = DragonEggConfig.ACTIVITY_EGG.get((activityType, idx))
	if not oddsConfig:
		return None
	
	rewardDict = {}
	#金龙蛋掉落
	if random.randint(1, 10000) <= oddsConfig.goldEggOdds:
		rewardDict[oddsConfig.goldEggCoding] = 1
	
	#银龙蛋掉落
	if random.randint(1, 10000) <= oddsConfig.silverEggOdds:
		rewardDict[oddsConfig.silverEggCoding] = 1
	
	return rewardDict

#===============================================================================
# 事件
#===============================================================================
def OnRoleDayClear(role, param):
	'''
	每日清理
	@param role:
	@param param:
	'''
	role.SetI16(EnumInt16.GoldDragonEggBreakCnt, 0)

def DragonEggStart(*param):
	'''
	砸龙蛋活动开启
	'''
	_, circularType = param
	if circularType != CircularDefine.CA_DragonEgg:
		return
	
	global IS_START
	if IS_START is True:
		print "GE_EXC, DragonEgg is already start"
		return
	
	IS_START = True


def DragonEggEnd(*param):
	'''
	砸龙蛋活动关闭
	'''
	_, circularType = param
	if circularType != CircularDefine.CA_DragonEgg:
		return
	
	global IS_START
	if IS_START is False:
		print "GE_EXC, DragonEgg is already end"
		return
	
	IS_START = False
	
#===============================================================================
# 客户端请求
#===============================================================================
def RequestDragonEggOpenPanel(role, msg):
	'''
	客户端请求打开砸龙蛋面板
	@param role:
	@param msg:
	'''
	#活动是否开始
	if IS_START is False:
		return
	
	ShowDragonEggPanel(role)
	
def RequestDragonEggBreak(role, msg):
	'''
	客户端请求砸龙蛋
	@param role:
	@param msg:
	'''
	#活动是否开始
	if IS_START is False:
		return
	
	backFunId, eggType = msg
	
	#等级限制
	if role.GetLevel() < NEED_LEVEL:
		return
	
	DragonEggBreak(role, eggType, backFunId)

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
		
	if Environment.HasLogic and not Environment.IsCross:
		#事件
		Event.RegEvent(Event.Eve_StartCircularActive, DragonEggStart)
		Event.RegEvent(Event.Eve_EndCircularActive, DragonEggEnd)
	
		#日志
		TraDragonGoldEggBreak = AutoLog.AutoTransaction("TraDragonGoldEggBreak", "砸金龙蛋")
		TraDragonSilverEggBreak = AutoLog.AutoTransaction("TraDragonSilverEggBreak", "砸银龙蛋")
	
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Dragon_Egg_Open_Panel", "客户端请求打开砸龙蛋面板"), RequestDragonEggOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Dragon_Egg_Break", "客户端请求砸龙蛋"), RequestDragonEggBreak)
	
	