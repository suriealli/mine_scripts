#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.LanternFestival.LanternStore")
#===============================================================================
# 元宵节商店
#===============================================================================
import cRoleMgr
import Environment
from Game.Role import Event
from Game.Role.Data import EnumObj
from Game.SysData import WorldData
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Game.Activity import CircularDefine
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Activity.LanternFestival import LanternFestivalConfig

if "_HasLoad" not in dir():
	IsStart = False
	
	SyncLanternStoreRoleBuyData = AutoMessage.AllotMessage("SyncLanternStoreRoleBuyData", "同步元宵商店角色购买数据")
	
	TraLanternStoreExchange = AutoLog.AutoTransaction("TraLanternStoreExchange", "元宵节花灯商店兑换")
	
def Start(param1, param2):
	if param2 != CircularDefine.CA_LanternStore:
		return
	
	global IsStart
	if IsStart:
		print "GE_EXC, LanternStore is already open"
		return
	
	IsStart = True


def End(param1, param2):
	if param2 != CircularDefine.CA_LanternStore:
		return
	global IsStart
	if not IsStart:
		print "GE_EXC, LanternStore is already close"
		return
	IsStart = False


def RequestExchange(role, msg):
	'''
	客户端请求元宵商店兑换
	@param role:
	@param msg:
	'''
	if IsStart is False:
		return
	
	#等级判断
	if role.GetLevel() < EnumGameConfig.LanternFestivalNeedLevel:
		return
	
	coding, cnt = msg
	if cnt <= 0:
		return
	
	config = LanternFestivalConfig.LanternStoreConfigDict.get(coding)
	if not config:
		return
	
	#角色等级不足
	if role.GetLevel() < config.needLevel:
		return
	
	#世界等级不足
	if WorldData.GetWorldLevel() < config.needWorldLevel:
		return
	
	#兑换需要物品不够
	needCoding = config.needCoding
	needCnt = config.needItemCnt * cnt
	if role.ItemCnt(needCoding) < needCnt:
		return
	
	#如果有限购的话
	buyDataDict = role.GetObj(EnumObj.LanternFestival).setdefault('store', {})
	oldBuyCnt = buyDataDict.get(coding, 0)
	if config.limitCnt:
		#记录角色购买次数的字典
		if oldBuyCnt + cnt > config.limitCnt:
			return

	#这里需要增加日志
	with TraLanternStoreExchange:
		if role.DelItem(needCoding, needCnt) < needCnt:
			return
		buyDataDict[coding] = oldBuyCnt + cnt
		role.AddItem(coding, cnt)
	
	role.SendObj(SyncLanternStoreRoleBuyData, buyDataDict)
	role.Msg(2, 0, GlobalPrompt.Reward_Tips + GlobalPrompt.Item_Tips % (coding, cnt))
	
	
def RequestOpenPanel(role, param):
	'''
	客户端请求打开元宵商店面板
	@param role:
	@param param:
	'''
	if not IsStart:
		return
	if role.GetLevel() < EnumGameConfig.LanternFestivalNeedLevel:
		return

	buyDataDict = role.GetObj(EnumObj.LanternFestival).get('store', {})
	role.SendObj(SyncLanternStoreRoleBuyData, buyDataDict)
	

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, Start)
		Event.RegEvent(Event.Eve_EndCircularActive, End)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestExchangeLanternStore", "客户端请求元宵商店兑换"), RequestExchange)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestOpenLanternStorePanel", "客户端请求打开元宵商店面板"), RequestOpenPanel)
