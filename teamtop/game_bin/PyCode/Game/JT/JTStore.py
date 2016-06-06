#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.JT.JTStore")
#===============================================================================
# 跨服竞技场金券兑换商店
#===============================================================================
import random
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Game.Role.Data import EnumInt32, EnumDayInt8
from ComplexServer.Log import AutoLog
from Game.Persistence import Contain
from Common.Other import GlobalPrompt
from Game.JT import JTConfig
from Game.Role import Event


if "_HasLoad" not in dir():
	
	#消息
	SyncJTStoreExchangeData = AutoMessage.AllotMessage("SyncJTStoreExchangeData", "跨服竞技场金券兑换商店同步物品兑换信息")
	SyncJTStoreGoods = AutoMessage.AllotMessage("SyncJTStoreGoods", "跨服竞技场金券兑换商店同步当前出售物品")
	#日志
	Tra_JTStore_RequestExchange = AutoLog.AutoTransaction("Tra_JTStore_RequestExchange", "跨服竞技场金券兑换商店请求兑换物品")
	Tra_JTStore_RequestRefresh = AutoLog.AutoTransaction("Tra_JTStore_RequestRefresh", "跨服竞技场金券兑换商店请求刷新出售物品")


def RefreshGoods(role, tell=False):
	'''
	刷新商店物品以及清空已购买次数
	'''
	allGoodList = JTConfig.JTStoreConfigDict.keys()
	if len(allGoodList) < 6:
		print "GE_EXC,TConfig.JTStoreConfigDict less than 6 goods"
		return
	roleId = role.GetRoleID()
	newGoodList = random.sample(allGoodList, 6)
	
	global JTStoreGoods_Dict
	global JTStoreData_Dict
	JTStoreGoods_Dict[roleId] = newGoodList
	JTStoreGoods_Dict.HasChange()
	if roleId in JTStoreData_Dict:
		del JTStoreData_Dict[roleId]
	
	role_id = role.GetRoleID()
	exchangeDict = JTStoreData_Dict.setdefault(role_id, {})
	role.SendObj(SyncJTStoreExchangeData, exchangeDict)
	role.SendObj(SyncJTStoreGoods, newGoodList)
	
	if tell is True:
		role.Msg(2, 0, GlobalPrompt.JT_StoreRrfreshOkay)


def RequestOpenPanel(role, msg):
	'''
	客户端请求打开商店面板
	@param role:
	@param msg:
	'''
	role_id = role.GetRoleID()
	exchangeDict = JTStoreData_Dict.get(role_id, {})
	if role_id not in JTStoreGoods_Dict:
		RefreshGoods(role)
		return
	
	goodList = JTStoreGoods_Dict[role_id]
	role.SendObj(SyncJTStoreGoods, goodList)
	role.SendObj(SyncJTStoreExchangeData, exchangeDict)
	


def RequestRefreshGoods(role, msg):
	'''
	客户端请求刷新商店物品
	'''
	eldCnt = role.GetDI8(EnumDayInt8.JTStoreRefreshCnt)
	nowCnt = eldCnt + 1
	config = JTConfig.JTSToreRefreshConfigDict.get(nowCnt)
	if not config:
		return
	if role.GetI32(EnumInt32.JTGold) < config.needJTGold:
		return
	with Tra_JTStore_RequestRefresh:
		role.DecI32(EnumInt32.JTGold, config.needJTGold)
		role.IncDI8(EnumDayInt8.JTStoreRefreshCnt, 1)
		RefreshGoods(role, tell=True)


def RequestExchange(role, msg):
	'''
	客户端请求兑换物品
	@param role:
	@param msg:
	'''
	idx, cnt = msg

	if not cnt > 0:
		return

	config = JTConfig.JTStoreConfigDict.get(idx, None)
	#不能购买不存在的物品
	if config == None:
		print "GE_EXC , error while config = JTStoreConfig.JTStoreConfigDict.get(idx, None), no such idx(%s)" % idx
		return
	
	#购买该物品的总次数大于限定的次数
	global JTStoreData_Dict
	role_id = role.GetRoleID()
	exchangeDict = JTStoreData_Dict.setdefault(role_id, {})
	elder_times = exchangeDict.get(idx, 0)
	
	goodList = JTStoreGoods_Dict.get(role_id, [])
	if not goodList:
		return
	if idx not in goodList:
		return
	
	
	#如果config.limitcnt<=0的话认为是不限购
	if config.limitcnt > 0:
		if elder_times >= config.limitcnt:
			return
		#如果本次购买的次数购买后大过了限制购买的次数
		if elder_times + cnt > config.limitcnt:
			return


	#如果战队积分不符合要求
	if role.GetJTeamScore() < config.needteampoint:
		return
	
	#个人金券少于兑换改物品的金券数
	totalprice = config.price * cnt
	if role.GetI32(EnumInt32.JTGold) < totalprice:
		return
	
	thingmsg = ""

	with Tra_JTStore_RequestExchange:
		#扣除金券
		role.DecI32(EnumInt32.JTGold, totalprice)
		#增加次数
		exchangeDict[idx] = exchangeDict.get(idx, 0) + cnt
		JTStoreData_Dict.HasChange()
		#普通道具
		if config.type == 1:
			role.AddItem(config.code, cnt)
			thingmsg += GlobalPrompt.Item_Tips % (config.code, cnt)
		#命魂
		elif config.type == 2:
			role.AddTarotCard(config.code, cnt)
			thingmsg += GlobalPrompt.Tarot_Tips % (config.code, cnt)
		else:
			return
		
		role.SendObj(SyncJTStoreExchangeData, exchangeDict)
		role.Msg(2, 0, GlobalPrompt.JT_ExchangeOkay + thingmsg)


def DayliClear(role, param):
	'''
	每日清理
	'''
	RefreshGoods(role)


if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.EnvIsQQ() or Environment.EnvIsFT() or Environment.IsDevelop or Environment.EnvIsNA() or Environment.EnvIsRU() or Environment.EnvIsPL()) and not Environment.IsCross:
		#role_id:{交易id:交易次数}
		JTStoreData_Dict = Contain.Dict("JTStoreData_Dict", (2038, 1, 1), None, None)
		#对角色而言当前出售的商品内容role_id-->(交易id列表)
		JTStoreGoods_Dict = Contain.Dict("JTStoreGoods_Dict", (2038, 1, 1), None, None)
		
		Event.RegEvent(Event.Eve_RoleDayClear, DayliClear)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_RequestExchange", "跨服竞技场金券兑换商店请求兑换物品"), RequestExchange)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JTStore_RequestOpenPanel", "跨服竞技场金券兑换商店打开面板"), RequestOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JTStore_RequestRefresh", "跨服竞技场金券兑换商店刷新"), RequestRefreshGoods)
