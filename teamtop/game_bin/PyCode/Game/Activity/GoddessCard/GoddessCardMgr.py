#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.GoddessCard.GoddessCardMgr")
#===============================================================================
# 女神卡牌
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Activity import CircularDefine
from Game.Activity.GoddessCard import GoddessCardConfig
from Game.Role import Event
from Game.Role.Data import EnumObj, EnumInt8, EnumDayInt8, EnumInt1
from Util import Random

if "_HasLoad" not in dir():
	
	IS_START = False			#活动是否开启
	
	CARD_POS_IDX = 1			#卡牌位置索引
	TREASURE_REWARD_ID_IDX = 2	#宝箱奖励索引
	TREASURE_STATE_IDX = 3		#宝箱领取状态索引
	GROUP_CARD_IDX = 4			#组合卡牌索引
	GROUP_ID_IDX = 5			#组合ID索引
	GROUP_ACTIVATED_IDX = 6		#组合已激活索引
	DOUBLE_TREASURE_IDX = 7		#开箱奖励翻倍索引
	
	G_CARD_POSITION_ROLE_RANDOM_OBJ_DICT = {}	#女神卡牌位置角色随机对象字典
	
	#消息
	Goddess_Card_Show_Panel = AutoMessage.AllotMessage("Goddess_Card_Show_Panel", "通知客户端显示女神卡牌面板")
	Goddess_Card_Trigger_Group = AutoMessage.AllotMessage("Goddess_Card_Trigger_Group", "通知客户端触发女神卡牌组合")
	
def GetRound8(i):
	l = []
	
	config = GoddessCardConfig.GODDESS_CARD_POSITION_ODDS.get(i)
	if not config:
		return l
	
	return config.roundEightPoint
	
def GetRoleGoddessCardRandomObj(role):
	gCardDataDict = role.GetObj(EnumObj.GoddessCard)
	posDict = gCardDataDict[CARD_POS_IDX]
	roleId = role.GetRoleID()
	
	global G_CARD_POSITION_ROLE_RANDOM_OBJ_DICT
	if roleId in G_CARD_POSITION_ROLE_RANDOM_OBJ_DICT:
		return G_CARD_POSITION_ROLE_RANDOM_OBJ_DICT[roleId]
	
	randomObj = Random.RandomRate()
	for posId, config in GoddessCardConfig.GODDESS_CARD_POSITION_ODDS.iteritems():
		
		#可能上次活动开启玩到一半，已有开启的卡牌
		if posId in posDict:
			continue
		
		randomObj.AddRandomItem(config.turnOverOdds, posId)
	
	G_CARD_POSITION_ROLE_RANDOM_OBJ_DICT[roleId] = randomObj
	
	return randomObj

def TurnOverCardReward(role, cardRewardId):
	#翻牌奖励
	cardRewardConfig = GoddessCardConfig.GODDESS_CARD_REWARD.get(cardRewardId)
	if not cardRewardConfig:
		return
	itemCoding, itemCnt = cardRewardConfig.rewardItemRandomObj.RandomOne()
	role.AddItem(itemCoding, itemCnt)
	
	#提示
	role.Msg(2, 0, GlobalPrompt.Reward_Tips +  GlobalPrompt.Item_Tips % (itemCoding, itemCnt))
	
	#传闻
	if itemCoding == 27676:
		cRoleMgr.Msg(3, 0, GlobalPrompt.GODDESS_CARD_REWARD_HEARSAY % (role.GetRoleName(), itemCoding, itemCnt))
	
def TurnOverOneCard(role):
	gCardDataDict = role.GetObj(EnumObj.GoddessCard)
	groupCardList = gCardDataDict[GROUP_CARD_IDX]
	
	posRandomObj = GetRoleGoddessCardRandomObj(role)
	
	posId = posRandomObj.RandomOneThenDelete()
	if not posId:
		#有可能位置全部随机完毕
		return
	
	posDict = gCardDataDict[CARD_POS_IDX]
	if posId in posDict:
		return
	
	cardRewardId = 0
	#随机卡牌类型
	if GoddessCardConfig.POSITION_CNT_MAX - len(posDict) <= len(groupCardList):
		#翻牌只剩下组合卡牌，直接出组合卡牌
		posDict[posId] = cardRewardId = groupCardList.pop()
	else:
		#是否有组合卡牌
		if groupCardList:
			#是否满足出组合的限制
			cardIdx = GoddessCardConfig.GROUP_CARD_CNT_MAX - len(groupCardList) + 1	#当前准备出第几张组合牌
			groupLimitConfig = GoddessCardConfig.GODDESS_GROUP_LIMIT[cardIdx]
			if len(posDict) < groupLimitConfig.needTurnOverCardCnt:
				#不满足条件一定出英雄卡牌
				posDict[posId] = cardRewardId = GoddessCardConfig.HERO_CARD_RANDOM_OBJ.RandomOne()
			else:
				cardType = GoddessCardConfig.GODDESS_CARD_TYPE_RANDOM_OBJ.RandomOne()
				if cardType == GoddessCardConfig.HERO_CARD_TYPE:
					posDict[posId] = cardRewardId = GoddessCardConfig.HERO_CARD_RANDOM_OBJ.RandomOne()
				elif cardType == GoddessCardConfig.GODDESS_CARD_TYPE:
					#翻牌只剩下女神卡牌，直接出女神卡牌
					posDict[posId] = cardRewardId = groupCardList.pop()
		else:
			#没有组合卡牌就出英雄牌
			posDict[posId] = cardRewardId = GoddessCardConfig.HERO_CARD_RANDOM_OBJ.RandomOne()
	
	#翻牌奖励
	TurnOverCardReward(role, cardRewardId)
	
	#同步客户端
	ShowGoddessCardPanel(role)
	
def GoddessCardTurnOverOne(role):
	#翻牌次数
	if role.GetI8(EnumInt8.GoddessCardTurnOverCnt) == 0:
		return
	
	needUnbindRMB = 0
	if Environment.EnvIsNA():
		needUnbindRMB = EnumGameConfig.GODDESS_CARD_TURN_OVER_ONE_NEED_RMB_NA
	else:
		needUnbindRMB = EnumGameConfig.GODDESS_CARD_TURN_OVER_ONE_NEED_RMB
	#是否足够RMB
	if role.GetUnbindRMB() < needUnbindRMB:
		return
	
	role.DecUnbindRMB(needUnbindRMB)
	role.DecI8(EnumInt8.GoddessCardTurnOverCnt, 1)
	
	TurnOverOneCard(role)
	
	#是否激活组合
	IsActivatedGroup(role)
	
def GoddessCardTurnOverFive(role):
	#是否足够RMB
	needUnbindRMB = 0
	if Environment.EnvIsNA():
		needUnbindRMB = EnumGameConfig.GODDESS_CARD_TURN_OVER_FIVE_NEED_RMB_NA
	else:
		needUnbindRMB = EnumGameConfig.GODDESS_CARD_TURN_OVER_FIVE_NEED_RMB
		
	if role.GetUnbindRMB() < needUnbindRMB:
		return
	role.DecUnbindRMB(needUnbindRMB)
	
	for _ in xrange(5):
		#翻牌次数
		if role.GetI8(EnumInt8.GoddessCardTurnOverCnt) == 0:
			return
		role.DecI8(EnumInt8.GoddessCardTurnOverCnt, 1)
		
		TurnOverOneCard(role)
	
	#是否激活组合
	IsActivatedGroup(role)

def GoddessCardTurnOverFinal(role):
	if role.GetI1(EnumInt1.GoddessCardTurnOverFinal):
		#提示
		role.Msg(2, 0, GlobalPrompt.GODDESS_CARD_ALREADY_FINAL_PROMPT)
		return
	role.SetI1(EnumInt1.GoddessCardTurnOverFinal, 1)
	
	#是否足够RMB
	needUnbindRMB = 0
	if Environment.EnvIsNA():
		needUnbindRMB = EnumGameConfig.GODDESS_CARD_TURN_OVER_FINAL_NEED_RMB_NA
	else:
		needUnbindRMB = EnumGameConfig.GODDESS_CARD_TURN_OVER_FINAL_NEED_RMB
	if role.GetUnbindRMB() < needUnbindRMB:
		return
	role.DecUnbindRMB(needUnbindRMB)
	
	TurnOverOneCard(role)
	
	#是否激活组合
	IsActivatedGroup(role)
	
def GoddessCardGetTreasure(role, treasureId):
	gCardDataDict = role.GetObj(EnumObj.GoddessCard)
	
	posDict = gCardDataDict[CARD_POS_IDX]
	treasureRewardIdDict = gCardDataDict[TREASURE_REWARD_ID_IDX]
	treasureStateDict = gCardDataDict[TREASURE_STATE_IDX]
	doubleTreasure = gCardDataDict[DOUBLE_TREASURE_IDX]
	
	if treasureId not in treasureRewardIdDict:
		return
	if treasureId not in treasureStateDict:
		return
	
	#是否满足领取条件(满足行列规则）
	treasureBaseConfig = GoddessCardConfig.GODDESS_TREASURE_BASE.get(treasureId)
	if not treasureBaseConfig:
		return
	for activateTreasureId in treasureBaseConfig.activateCondition:
		if activateTreasureId not in posDict:
			return
	
	rewardId = treasureRewardIdDict[treasureId]
	rewardConfig = GoddessCardConfig.GODDESS_TREASURE_REWARD.get(rewardId)
	if not rewardConfig:
		return
	
	#已经领取
	if treasureStateDict[treasureId]:
		return
	treasureStateDict[treasureId] = 1
	
	#重置双倍奖励
	if doubleTreasure:
		gCardDataDict[DOUBLE_TREASURE_IDX] = 0
	
	prompt = GlobalPrompt.Reward_Tips
	#奖励
	for coding, cnt in rewardConfig.rewardItem:
		#是否有双倍奖励
		if doubleTreasure:
			cnt = cnt * 2
		role.AddItem(coding, cnt)
		
		prompt += GlobalPrompt.Item_Tips % (coding, cnt)
		
	#提示
	role.Msg(2, 0, prompt)
		
	#同步客户端
	ShowGoddessCardPanel(role)
	
def GoddessCardReset(role):
	role.SetI8(EnumInt8.GoddessCardTurnOverCnt, 20)
	role.SetI1(EnumInt1.GoddessCardTurnOverFinal, 0)
	
	gCardDataDict = role.GetObj(EnumObj.GoddessCard)
	gCardDataDict[CARD_POS_IDX] = {}
	gCardDataDict[TREASURE_REWARD_ID_IDX] = treasureRewardIdDict = {}
	gCardDataDict[TREASURE_STATE_IDX] = treasureStateDict = {}
	gCardDataDict[GROUP_CARD_IDX] = groupCardList = []
	gCardDataDict[GROUP_ID_IDX] = 0
	gCardDataDict[GROUP_ACTIVATED_IDX] = 0
	gCardDataDict[DOUBLE_TREASURE_IDX] = 0
	
	
	roleId = role.GetRoleID()
	#重置翻牌随机
	global G_CARD_POSITION_ROLE_RANDOM_OBJ_DICT
	if roleId in G_CARD_POSITION_ROLE_RANDOM_OBJ_DICT:
		del G_CARD_POSITION_ROLE_RANDOM_OBJ_DICT[roleId]
	
	#计算宝箱奖励
	for treasureId, config in GoddessCardConfig.GODDESS_TREASURE_BASE.iteritems():
		if config.treasureType == 1:
			treasureRewardIdDict[treasureId] = GoddessCardConfig.GODDESS_TREASURE1_RANDOM_OBJ.RandomOne()
		elif config.treasureType == 2:
			treasureRewardIdDict[treasureId] = GoddessCardConfig.GODDESS_TREASURE2_RANDOM_OBJ.RandomOne()
		elif config.treasureType == 3:
			treasureRewardIdDict[treasureId] = GoddessCardConfig.GODDESS_TREASURE3_RANDOM_OBJ.RandomOne()
		treasureStateDict[treasureId] = 0
		
	#保存随机到的卡牌女神组合
	groupId = GoddessCardConfig.GODDESS_CARD_GROUP_RANDOM_OBJ.RandomOne()
	groupConfig = GoddessCardConfig.GODDESS_GROUP_REWARD.get(groupId)
	if not groupConfig:
		print "GE_EXC can't find groupConfig in GoddessCardReset(%s, %s)" % (roleId, groupId)
		return
	gCardDataDict[GROUP_ID_IDX] = groupId
	groupCardList.extend(groupConfig.groupData)
	
	#同步客户端
	ShowGoddessCardPanel(role)
	
def IsActivatedGroup(role):
	gCardDataDict = role.GetObj(EnumObj.GoddessCard)
	if gCardDataDict[GROUP_CARD_IDX]:
		return
	
	#是否激活过
	if gCardDataDict[GROUP_ACTIVATED_IDX]:
		return
	
	activateGroupId = gCardDataDict[GROUP_ID_IDX]
	groupConfig = GoddessCardConfig.GODDESS_GROUP_REWARD.get(activateGroupId)
	if not groupConfig:
		return
	
	#通知客户端(组合ID，组合配置，当前轮数)
	role.SendObjAndBack(Goddess_Card_Trigger_Group, activateGroupId, 10, CallBackActivateGroup, (activateGroupId, groupConfig, role.GetDI8(EnumDayInt8.GoddessCardResetCnt)))
	
def CallBackActivateGroup(role, callargv, regparam):
	activateGroupId, groupConfig, resetCnt = regparam
	
	#防止组合被带入下一轮
	if role.GetDI8(EnumDayInt8.GoddessCardResetCnt) != resetCnt:
		return
	
	#日志
	with TraGoddessCardActivateGroup:
		ActivateGroup(role, activateGroupId, groupConfig)
	
def ActivateGroup(role, activateGroupId, groupConfig):
	#是否激活过组合
	gCardDataDict = role.GetObj(EnumObj.GoddessCard)
	if gCardDataDict[GROUP_ACTIVATED_IDX]:
		return
	
	#防止重复激活组合
	if gCardDataDict[GROUP_ID_IDX] != activateGroupId:
		return
	if gCardDataDict[GROUP_CARD_IDX]:
		return
	
	#激活
	gCardDataDict[GROUP_ACTIVATED_IDX] = 1
	
	if groupConfig.groupRewardType == 2:
		#物品奖励
		if groupConfig.rewardItem:
			prompt = GlobalPrompt.Reward_Tips
			for coding, cnt in groupConfig.rewardItem:
				role.AddItem(coding, cnt)
				prompt += GlobalPrompt.Item_Tips % (coding, cnt)
			#提示
			role.Msg(2, 0, prompt)
	elif groupConfig.groupRewardType:
		#触发各种特殊事件
		if activateGroupId == 1:
			for _ in xrange(4):
				TurnOverOneCard(role)
		elif activateGroupId == 2:
			for _ in xrange(3):
				TurnOverOneCard(role)
		elif activateGroupId == 3:
			for _ in xrange(2):
				TurnOverOneCard(role)
		elif activateGroupId == 4:
			for _ in xrange(1):
				TurnOverOneCard(role)
		elif activateGroupId == 5:
			TurnOverRound8(role, 4, groupConfig)
		elif activateGroupId == 6:
			TurnOverRound8(role, 3, groupConfig)
		elif activateGroupId == 7:
			TurnOverRound8(role, 2, groupConfig)
		elif activateGroupId == 8:
			TurnOverRound8(role, 1, groupConfig)
		elif activateGroupId == 9:
			gCardDataDict[DOUBLE_TREASURE_IDX] = 1
	
	#同步客户端
	ShowGoddessCardPanel(role)
	
def TurnOverRound8(role, cardCnt, groupConfig):
	gCardDataDict = role.GetObj(EnumObj.GoddessCard)
	
	posDict = gCardDataDict[CARD_POS_IDX]
	#反转
	cardRewardIdToPosDict = dict([(v, k) for k, v in posDict.iteritems()])
	
	turnOverCnt = 0
	for groupCardRewardId in groupConfig.groupData:
		if groupCardRewardId not in cardRewardIdToPosDict:
			return
		groupCardPos = cardRewardIdToPosDict[groupCardRewardId]
		
		#获取周围8格位置
		round8PosList = GetRound8(groupCardPos)
		for pos in round8PosList:
			#是否有未翻开的卡牌
			if pos in posDict:
				continue
			
			#翻牌次数已满足
			if turnOverCnt >= cardCnt:
				break
			
			turnOverCnt += 1
			posDict[pos] = cardRewardId = GoddessCardConfig.HERO_CARD_RANDOM_OBJ.RandomOne()
			
			#删除随机对象中的位置
			DelPosInRandomObj(role, pos)
			
			#翻牌奖励
			TurnOverCardReward(role, cardRewardId)
		
	#同步客户端
	ShowGoddessCardPanel(role)
	
def DelPosInRandomObj(role, pos):
	'''
	删除随机对象中的位置
	@param role:
	@param pos:
	'''
	global G_CARD_POSITION_ROLE_RANDOM_OBJ_DICT
	
	roleId = role.GetRoleID()
	
	if roleId not in G_CARD_POSITION_ROLE_RANDOM_OBJ_DICT:
		return
	
	randomObj = G_CARD_POSITION_ROLE_RANDOM_OBJ_DICT[roleId]
	
	delIdx = -1
	rate = 0
	for idx, data in enumerate(randomObj.randomList):
		if pos == data[1]:
			delIdx = idx
			rate = data[0]
			break
	
	if delIdx < 0:
		return
	
	del randomObj.randomList[delIdx]
	randomObj.totalRate -= rate
	
#===============================================================================
# 显示
#===============================================================================
def ShowGoddessCardPanel(role):
	gCardDataDict = role.GetObj(EnumObj.GoddessCard)
	
	posDict = gCardDataDict.get(CARD_POS_IDX, {})
	treasureRewardIdDict = gCardDataDict.get(TREASURE_REWARD_ID_IDX, {})
	treasureStateDict = gCardDataDict.get(TREASURE_STATE_IDX, {})
	
	#通知客户端
	role.SendObj(Goddess_Card_Show_Panel, (posDict, treasureRewardIdDict, treasureStateDict))
	
#===============================================================================
# 事件
#===============================================================================
def GoddessCardStart(*param):
	'''
	女神卡牌活动开启
	'''
	_, circularType = param
	if circularType != CircularDefine.CA_GoddessCard:
		return
	
	global IS_START
	if IS_START is True:
		print "GE_EXC, GoddessCard is already start"
		return
	
	IS_START = True

def GoddessCardEnd(*param):
	'''
	女神卡牌活动关闭
	'''
	_, circularType = param
	if circularType != CircularDefine.CA_GoddessCard:
		return
	
	global IS_START
	if IS_START is False:
		print "GE_EXC, GoddessCard is already end"
		return
	
	IS_START = False
	
def OnRoleDayClear(role, param):
	'''
	角色每日清理调用
	@param role:
	@param param:
	'''
	GoddessCardReset(role)
	
def SyncRoleOtherData(role, param):
	'''
	角色登录同步其他剩余的数据
	@param role:
	@param param:
	'''
	gCardDataDict = role.GetObj(EnumObj.GoddessCard)
	if not gCardDataDict:
		#第一次登录的玩家
		GoddessCardReset(role)
		
	#同步客户端
	ShowGoddessCardPanel(role)
	
#===============================================================================
# 客户端请求
#===============================================================================
def RequestGoddessCardOpenPanel(role, msg):
	'''
	客户端请求打开女神卡牌面板
	@param role:
	@param msg:
	'''
	#活动是否开始
	if IS_START is False:
		return
	
	ShowGoddessCardPanel(role)

def RequestGoddessCardTurnOverOne(role, msg):
	'''
	客户端请求女神卡牌翻牌1次
	@param role:
	@param msg:
	'''
	#活动是否开始
	if IS_START is False:
		return
	
	#日志
	with TraGoddessCardTurnOverOne:
		GoddessCardTurnOverOne(role)

def RequestGoddessCardTurnOverFive(role, msg):
	'''
	客户端请求女神卡牌翻牌5次
	@param role:
	@param msg:
	'''
	#活动是否开始
	if IS_START is False:
		return
	
	#日志
	with TraGoddessCardTurnOverFive:
		GoddessCardTurnOverFive(role)
	
def RequestGoddessCardTurnOverFinal(role, msg):
	'''
	客户端请求女神卡牌终极翻牌
	@param role:
	@param msg:
	'''
	#活动是否开始
	if IS_START is False:
		return
	
	#日志
	with TraGoddessCardTurnOverFinal:
		GoddessCardTurnOverFinal(role)
	
def RequestGoddessCardGetTreasure(role, msg):
	'''
	客户端请求领取女神卡牌宝箱
	@param role:
	@param msg:
	'''
	#活动是否开始
	if IS_START is False:
		return
	
	treasureId = msg
	
	#日志
	with TraGoddessCardGetTreasure:
		GoddessCardGetTreasure(role, treasureId)
	
def RequestGoddessCardReset(role, msg):
	'''
	客户端请求女神卡牌重置
	@param role:
	@param msg:
	'''
	#活动是否开始
	if IS_START is False:
		return
	
	if role.GetDI8(EnumDayInt8.GoddessCardResetCnt) >= EnumGameConfig.GODDESS_CARD_RESET_CNT:
		return
	
	#日志
	with TraGoddessCardReset:
		role.IncDI8(EnumDayInt8.GoddessCardResetCnt, 1)
	
	GoddessCardReset(role)

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#事件
		#每日清理调用
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
		#角色登录同步其他剩余的数据
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		#循环活动
		Event.RegEvent(Event.Eve_StartCircularActive, GoddessCardStart)
		Event.RegEvent(Event.Eve_EndCircularActive, GoddessCardEnd)
		
		#日志
		TraGoddessCardGetTreasure = AutoLog.AutoTransaction("TraGoddessCardGetTreasure", "女神卡牌领取宝箱")
		TraGoddessCardTurnOverOne = AutoLog.AutoTransaction("TraGoddessCardTurnOverOne", "女神卡牌翻牌1次")
		TraGoddessCardTurnOverFive = AutoLog.AutoTransaction("TraGoddessCardTurnOverFive", "女神卡牌翻牌5次")
		TraGoddessCardTurnOverFinal = AutoLog.AutoTransaction("TraGoddessCardTurnOverFinal", "女神卡牌终极翻牌")
		TraGoddessCardActivateGroup = AutoLog.AutoTransaction("TraGoddessCardActivateGroup", "女神卡牌组合激活")
		TraGoddessCardReset = AutoLog.AutoTransaction("TraGoddessCardReset", "女神卡牌重置")
		
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Goddess_Card_Open_Panel", "客户端请求打开女神卡牌面板"), RequestGoddessCardOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Goddess_Card_Turn_Over_One", "客户端请求女神卡牌翻牌1次"), RequestGoddessCardTurnOverOne)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Goddess_Card_Turn_Over_Five", "客户端请求女神卡牌翻牌5次"), RequestGoddessCardTurnOverFive)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Goddess_Card_Turn_Over_Final", "客户端请求女神卡牌终极翻牌"), RequestGoddessCardTurnOverFinal)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Goddess_Card_Get_Treasure", "客户端请求领取女神卡牌宝箱"), RequestGoddessCardGetTreasure)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Goddess_Card_Reset", "客户端请求女神卡牌重置"), RequestGoddessCardReset)
		

