#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.HappyNewYear.NewYearShop")
#===============================================================================
# 新年乐翻天-新年兑不停
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
from Game.Activity.HappyNewYear import NewYearConfig

if "_HasLoad" not in dir():
	NewYearShopIsOpen = False
	
	NewYearShopData = AutoMessage.AllotMessage("NewYearShopData", "新年狂欢兑不停兑换数据")
	
	NewYearShopEx_Log = AutoLog.AutoTransaction("NewYearShopEx_Log", "新年狂欢兑不停兑换日志")
	
def OpenElevenShop(param1, param2):
	if param2 != CircularDefine.CA_NewYearShop:
		return
	
	global NewYearShopIsOpen
	if NewYearShopIsOpen:
		print "GE_EXC, NewYearShop is already open"
		return
	
	NewYearShopIsOpen = True

def CloseElevenShop(param1, param2):
	if param2 != CircularDefine.CA_NewYearShop:
		return
	
	global NewYearShopIsOpen
	if not NewYearShopIsOpen:
		print "GE_EXC, NewYearShop is already close"
		return
	
	NewYearShopIsOpen = False

def RequestExchange(role, msg):
	'''
	请求新年兑不停兑换
	@param role:
	@param msg:
	'''
	global NewYearShopIsOpen
	if not NewYearShopIsOpen:
		return
	
	#等级判断
	if role.GetLevel() < EnumGameConfig.NYEAR_MIN_LEVEL:
		return
	
	coding, cnt = msg
	cfg = NewYearConfig.NewYearShop_Dict.get(coding)
	if not cfg:
		print "GE_EXC, NEW YEAR shop can not find coding (%s) in NewYearShop_Dict" % coding
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
		elShopObj = role.GetObj(EnumObj.NYearDataEX).get(3)
		if not elShopObj:
			elShopObj = {}
		if coding not in elShopObj:
			elShopObj[coding] = cnt
		elif elShopObj[coding] + cnt > cfg.limitCnt:
			#超过限购
			return
		else:
			elShopObj[coding] += cnt
		role.GetObj(EnumObj.NYearDataEX)[3] = elShopObj
		#限购的记录购买数量
		role.SendObj(NewYearShopData, elShopObj)
	
	with NewYearShopEx_Log:
		#发放兑换物品
		role.DelItem(cfg.needCoding, needCnt)
		role.AddItem(coding, cnt)
	role.Msg(2, 0, GlobalPrompt.Reward_Tips + GlobalPrompt.Item_Tips % (coding, cnt))
	
def RequestOpenShop(role, param):
	'''
	请求打开新年兑不停商店
	@param role:
	@param param:
	'''
	global NewYearShopIsOpen
	if not NewYearShopIsOpen:
		return
	
	if role.GetLevel() < EnumGameConfig.NYEAR_MIN_LEVEL:
		return
	
	role.SendObj(NewYearShopData, role.GetObj(EnumObj.NYearDataEX).get(3))
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_StartCircularActive, OpenElevenShop)
		Event.RegEvent(Event.Eve_EndCircularActive, CloseElevenShop)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NewYearShop_Exchange", "请求新年狂欢兑不停兑换"), RequestExchange)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NewYearShop_Open", "请求打开新年狂欢兑不停商店"), RequestOpenShop)
		
