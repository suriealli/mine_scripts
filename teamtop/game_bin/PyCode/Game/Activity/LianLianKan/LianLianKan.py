#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.LianLianKan.LianLianKan")
#===============================================================================
# 连连看
#===============================================================================
import random
import Environment
import cRoleMgr
from Common.Other import EnumGameConfig, GlobalPrompt
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Role.Data import EnumObj, EnumDayInt1, EnumDayInt8
from Game.Activity import CircularDefine
from Game.Activity.LianLianKan import LianLianKanConfig


if "_HasLoad" not in dir():
	IS_START = False	#活动开启标志
	Random_List = [[2,3,8,9],[4,5,11,12],[6,13,14,21],[19,20,26,27],[18,23,24,25],[15,16,17]]
	#日志
	TraLLKanRefresh = AutoLog.AutoTransaction("TraLLKanRefresh", "连连看刷新游戏消耗")
	TraLLKanPlay = AutoLog.AutoTransaction("TraLLKanPlay", "连连看消除奖励")
	TraLLKanStart = AutoLog.AutoTransaction("TraLLKanStart", "开始连连看游戏")
	TraLLKanBuy = AutoLog.AutoTransaction("TraLLKanBuy", "连连看购买次数")
	TraLLKanGet = AutoLog.AutoTransaction("TraLLKanGet", "连连看领取每日首充次数")
	#消息
	LLK_Syc_GameData = AutoMessage.AllotMessage("LLK_Syc_GameData", "同步连连看数据")
	
	
def OpenLLKan(role, param):
	#活动开始
	if param != CircularDefine.CA_LianLianKan:
		return
	global IS_START
	if IS_START:
		print "GE_EXC, LLKan is already open"
		return
	IS_START = True
	
def CloseLLKan(role, param):
	#活动结束
	if param != CircularDefine.CA_LianLianKan:
		return
	global IS_START
	if not IS_START:
		print "GE_EXC, LLKan is already close"
	IS_START = False
	
def InitGame(role, refresh=True):
	rewardIdList = LianLianKanConfig.GetRewardIdsByLevel(role.GetLevel())
	if not rewardIdList:
		print "GE_EXC,can not find rewardIdList by Level(%s) in LianLianKan.InitGame" % role.GetLevel()
		return
	rewardIdList += rewardIdList
	#打乱顺序
	random.shuffle(rewardIdList)
	index_list = []
	for indexList in Random_List:
		index_list.append(random.choice(indexList))
	random.shuffle(index_list)
	GameData = dict(zip(index_list,rewardIdList))
	role.SetObj(EnumObj.LianLianKanData, GameData)
	role.SendObj(LLK_Syc_GameData, GameData)
	
#==============================================================================
def RequestGameStart(role, param):
	'''
	客户端请求开始连连看游戏
	@param role:
	@param param:
	'''
	global IS_START
	if not IS_START:
		return
	LianLianKanData = role.GetObj(EnumObj.LianLianKanData)
	if LianLianKanData:
		role.Msg(2, 0, GlobalPrompt.LLKan_No_Start)
		return
	rewardIdList = LianLianKanConfig.GetRewardIdsByLevel(role.GetLevel())
	if not rewardIdList:
		print "GE_EXC,can not find rewardIdList by Level(%s) in LianLianKan.RequestGameStart" % role.GetLevel()
		return
	LLKanFreeTimes = role.GetDI1(EnumDayInt1.LLKanFreeTimes)
	free = False
	if LLKanFreeTimes:
		#无免费次数
		if role.GetDI8(EnumDayInt8.LLKanPlayTimes) < 1:
			return
	else:
		free = True
	with TraLLKanStart:
		if free:
			role.SetDI1(EnumDayInt1.LLKanFreeTimes, 1)
		else:
			role.DecDI8(EnumDayInt8.LLKanPlayTimes, 1)
		InitGame(role)
		
	
def RequestGameRefresh(role, param):
	'''
	客户端请求刷新连连看
	@param role:
	@param param:
	'''
	global IS_START
	if not IS_START:
		return
	LianLianKanData = role.GetObj(EnumObj.LianLianKanData)
	if not LianLianKanData:
		return
	if len(LianLianKanData.keys()) != 6:
		return
	cost = EnumGameConfig.LianLianKan_RefreshCost
	if role.GetUnbindRMB() < cost:
		return
	with TraLLKanRefresh:
		role.DecUnbindRMB(cost)
		InitGame(role)
		
def RequestGamePlay(role, param):
	'''
	客户端请求连连看消除
	@param role:
	@param param:
	'''
	global IS_START
	if not IS_START:
		return
	index1, index2 = param
	
	LianLianKanData = role.GetObj(EnumObj.LianLianKanData)
	if not LianLianKanData:
		return
	if index1 not in LianLianKanData or index2 not in LianLianKanData:
		return
	if LianLianKanData.get(index1) != LianLianKanData.get(index2):
		return
	rewardId = LianLianKanData.get(index1)
	cfg = LianLianKanConfig.LianLianKan_Reward.get(rewardId)
	if not cfg:
		print "GE_EXC,can not find rewardId(%s) in LianLianKan.RequestGamePlay" % rewardId
		return
	with TraLLKanPlay:
		#删除对应的位置和奖励
		del LianLianKanData[index1]
		del LianLianKanData[index2]
		#发奖
		tips = GlobalPrompt.Reward_Tips
		if cfg.rewardItems:
			for coding, cnt in cfg.rewardItems:
				role.AddItem(coding, cnt)
				tips += GlobalPrompt.Item_Tips % (coding, cnt)
				if cfg.IsMsg:
					cRoleMgr.Msg(11, 0, GlobalPrompt.LLKan_BorMst % (role.GetRoleName(), coding, cnt))
		role.SendObj(LLK_Syc_GameData, LianLianKanData)
		role.Msg(2, 0, tips)
		
def RequestGameBuy(role, param):
	'''
	客户端请求购买连连看次数
	@param role:
	@param param:
	'''
	global IS_START
	if not IS_START:
		return
	LLKanBuyTimes = role.GetDI8(EnumDayInt8.LLKanBuyTimes)
	if LLKanBuyTimes >= EnumGameConfig.LianLianKan_BuyMaxTimes:
		return
	
	cfg = LianLianKanConfig.LianLianKan_BuyDict.get(LLKanBuyTimes + 1)
	if not cfg:
		print "GE_EXC,can not find buyTimes(%s) in LianLianKan.RequestGameBuy" % (LLKanBuyTimes + 1)
		return
	
	if role.GetUnbindRMB() < cfg.cost:
		return
	with TraLLKanBuy:
		role.DecUnbindRMB(cfg.cost)
		role.IncDI8(EnumDayInt8.LLKanBuyTimes, 1)
		role.IncDI8(EnumDayInt8.LLKanPlayTimes, 1)
		
def RequestGameGetTimes(role, param):
	'''
	客户端请求领取连连看首充奖励次数
	@param role:
	@param param:
	'''
	global IS_START
	if not IS_START:
		return
	if role.GetDI1(EnumDayInt1.LLKanGetTimes):
		return
	if role.GetDayBuyUnbindRMB_Q() < 100:
		return
	with TraLLKanGet:
		role.SetDI1(EnumDayInt1.LLKanGetTimes, 1)
		role.IncDI8(EnumDayInt8.LLKanPlayTimes, 1)
	
def OnSyncRoleOtherData(role, param):
	global IS_START
	if not IS_START:
		return
	role.SendObj(LLK_Syc_GameData, role.GetObj(EnumObj.LianLianKanData))
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		
		Event.RegEvent(Event.Eve_StartCircularActive, OpenLLKan)
		Event.RegEvent(Event.Eve_EndCircularActive, CloseLLKan)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("LianLianKan_StartGame", "客户端请求开始连连看游戏"), RequestGameStart)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("LianLianKan_RefreshGame", "客户端请求刷新连连看"), RequestGameRefresh)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("LianLianKan_PlayGame", "客户端请求连连看消除"), RequestGamePlay)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("LianLianKan_BuyGame", "客户端请求购买连连看次数"), RequestGameBuy)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("LianLianKan_GetGameTimes", "客户端请求领取连连看首充奖励次数"), RequestGameGetTimes)