#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.FiveOneDay.DragonBaoKu")
#===============================================================================
# 神龙宝库活动
#===============================================================================

import cRoleMgr
import Environment
import DragonBaoKuConfig
from ComplexServer.Log import AutoLog
from Game.Activity import CircularDefine
from Common.Message import AutoMessage
from Game.Role.Data import EnumObj
from Common.Other import GlobalPrompt
from Game.Role import Event


if "_HasLoad" not in dir():
	IS_START = False				#活动开启结束标志
	
	#消息
	Sync_exchange_times_for_client = AutoMessage.AllotMessage("Sync_exchange_times_for_client", "同步神龙宝库兑换物品和已经兑换数量")
	#日志
	
def DragonBaoKuStart(*param):
	'''
	神龙宝库活动开启
	'''
	_, circularType = param
	if circularType != CircularDefine.CA_FiveOneDragonBaoKu:
		return
	
	global IS_START
	if IS_START is True:
		print "GE_EXC, DragonBaoKu is already start"
		return
	
	IS_START = True


def DragonBaoKuEnd(*param):
	global IS_START
	
	_, circularType = param
	if circularType != CircularDefine.CA_FiveOneDragonBaoKu:
		return
	if IS_START is False:
		print "GE_EXC, DragonBaoKu has been ended"
		return
	IS_START = False


def RequestExchange(role, msg):
	'''
	 客户端请求用龙珠兑换物品
	'''
	global IS_START
	if IS_START is False:
		return
	
	#需要兑换的物品,数量
	item_coding,cnt = msg
	
	if cnt < 1:
		return
	
	item_dict_class = DragonBaoKuConfig.REWARD_ITEM_DICT.get(item_coding)
	if not item_dict_class:
		print "GE_EXC, can not find item_coding(%s) in DragonBaoKuConfig.REWARD_ITEM_DICT" % item_coding
		return
	#判断角色等级
	if item_dict_class.needLevel > role.GetLevel():
		return
	
	#用于兑换的物品(龙珠)编码
	need_Item = item_dict_class.needItemCoding
	
	#判断是否超过兑换的最大数量
	exchange_dict = role.GetObj(EnumObj.FiveOneDayObj).get(4,{})
	
	if item_dict_class.maxNum != -1 and exchange_dict.get(item_coding, 0) + cnt > item_dict_class.maxNum:
		return
	
	#判断物品（龙珠）够不够
	need_Item_Num = item_dict_class.dragonBall*cnt
	if need_Item_Num > role.ItemCnt( need_Item ):
		return
	#次数加cnt
	exchange_dict[item_coding] = exchange_dict.get(item_coding,0)+cnt 
	#给用户发物品
	with DragonBaoKuReward:
		#减物品（龙珠），加物品
		role.DelItem(need_Item, need_Item_Num)
		role.AddItem(item_coding, cnt)
		
	role.SendObj(Sync_exchange_times_for_client, exchange_dict)
	role.Msg(2, 0, GlobalPrompt.Reward_Item_Tips % (item_coding, cnt))
	

def SyncExchangeTimes(role, param):
	'''
	 同步兑换的物品数量
	'''
	global IS_START
	if IS_START is False:
		return
	exchange_times = role.GetObj(EnumObj.FiveOneDayObj).get(4,{})
	role.SendObj(Sync_exchange_times_for_client,exchange_times)
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#事件
		Event.RegEvent(Event.Eve_StartCircularActive, DragonBaoKuStart)
		Event.RegEvent(Event.Eve_EndCircularActive, DragonBaoKuEnd)
		Event.RegEvent(Event.Eve_SyncRoleOtherData,SyncExchangeTimes)
		#日志
		DragonBaoKuReward = AutoLog.AutoTransaction("DragonBaoKuReward", "神龙宝库兑换物品")
		
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestDragonBaoKuExchange", "客户端请求神龙宝库兑换商店兑换商品"), RequestExchange)
		
