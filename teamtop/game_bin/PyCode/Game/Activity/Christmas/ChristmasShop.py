#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.Christmas.ChristmasShop")
#===============================================================================
# 狂欢兑不停 - 圣诞嘉年华
#===============================================================================
import Environment
import cRoleMgr
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.SysData import WorldData
from Game.Role.Data import EnumObj
from Game.Activity import CircularDefine
from Game.Activity.Christmas import ChristmasHaoConfig

if "_HasLoad" not in dir():
	ChristmasShopIsOpen = False
	
	ChristmasShopData = AutoMessage.AllotMessage("ChristmasShopData", "圣诞狂欢兑不停兑换数据")
	
	ChristmasShopEx_Log = AutoLog.AutoTransaction("ChristmasShopEx_Log", "圣诞狂欢兑不停兑换日志")
	
def OpenElevenShop(param1, param2):
	if param2 != CircularDefine.CA_ChristmasShop:
		return
	
	global ChristmasShopIsOpen
	if ChristmasShopIsOpen:
		print "GE_EXC, ChristmasShop is already open"
		return
	
	ChristmasShopIsOpen = True

def CloseElevenShop(param1, param2):
	if param2 != CircularDefine.CA_ChristmasShop:
		return
	
	global ChristmasShopIsOpen
	if not ChristmasShopIsOpen:
		print "GE_EXC, ChristmasShop is already close"
		return
	
	ChristmasShopIsOpen = False

def RequestExchange(role, msg):
	'''
	请求狂欢兑不停兑换
	@param role:
	@param msg:
	'''
	global ChristmasShopIsOpen
	if not ChristmasShopIsOpen:
		return
	
	#等级判断
	if role.GetLevel() < EnumGameConfig.ChristmasShopLvLimit:
		return
	
	coding, cnt = msg
	cfg = ChristmasHaoConfig.ChristmasShop_Dict.get(coding)
	if not cfg:
		print "GE_EXC, double eleven shop can not find coding (%s) in ChristmasShop_Dict" % coding
		return
	
	#角色等级不足
	if role.GetLevel() < cfg.needLevel:
		return
	
	#世界等级不足
	if WorldData.GetWorldLevel() < cfg.needWorldLevel:
		return
	
	if not cnt: return
	
	#兑换需要物品不够
	needCnt = cfg.needItemCnt * cnt
	if role.ItemCnt(cfg.needCoding) < needCnt:
		return
	
	if cfg.limitCnt:
		if cnt > cfg.limitCnt:
			#购买个数超过限购
			return
		elShopObj = role.GetObj(EnumObj.ChristmasActive)[2]
		if coding not in elShopObj:
			elShopObj[coding] = cnt
		elif elShopObj[coding] + cnt > cfg.limitCnt:
			#超过限购
			return
		else:
			elShopObj[coding] += cnt
		role.GetObj(EnumObj.ChristmasActive)[2] = elShopObj
		#限购的记录购买数量
		role.SendObj(ChristmasShopData, elShopObj)
	
	with ChristmasShopEx_Log:
		#发放兑换物品
		role.DelItem(cfg.needCoding, needCnt)
		role.AddItem(coding, cnt)
	role.Msg(2, 0, GlobalPrompt.Reward_Tips + GlobalPrompt.Item_Tips % (coding, cnt))
	
def RequestOpenShop(role, param):
	'''
	请求打开狂欢兑不停商店
	@param role:
	@param param:
	'''
	global ChristmasShopIsOpen
	if not ChristmasShopIsOpen:
		return
	
	if role.GetLevel() < EnumGameConfig.ChristmasShopLvLimit:
		return
	
	role.SendObj(ChristmasShopData, role.GetObj(EnumObj.ChristmasActive)[2])
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_StartCircularActive, OpenElevenShop)
		Event.RegEvent(Event.Eve_EndCircularActive, CloseElevenShop)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChristmasShop_Exchange", "请求圣诞狂欢兑不停兑换"), RequestExchange)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChristmasShop_Open", "请求打开圣诞狂欢兑不停商店"), RequestOpenShop)
		