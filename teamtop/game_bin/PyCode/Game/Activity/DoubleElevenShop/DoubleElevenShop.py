#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DoubleElevenShop.DoubleElevenShop")
#===============================================================================
# 狂欢兑不停
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
from Game.Activity.DoubleElevenShop import DEShopConfig

if "_HasLoad" not in dir():
	DoubleElevenShopIsOpen = False
	
	DoubleElevenShopData = AutoMessage.AllotMessage("DoubleElevenShopData", "狂欢兑不停兑换数据")
	
	DoubleElevenShopEx_Log = AutoLog.AutoTransaction("DoubleElevenShopEx_Log", "狂欢兑不停兑换日志")
	
def OpenElevenShop(param1, param2):
	if param2 != CircularDefine.CA_DoubleElevenShop:
		return
	
	global DoubleElevenShopIsOpen
	if DoubleElevenShopIsOpen:
		print "GE_EXC, DoubleElevenShop is already open"
		return
	
	DoubleElevenShopIsOpen = True

def CloseElevenShop(param1, param2):
	if param2 != CircularDefine.CA_DoubleElevenShop:
		return
	
	global DoubleElevenShopIsOpen
	if not DoubleElevenShopIsOpen:
		print "GE_EXC, DoubleElevenShop is already close"
		return
	
	DoubleElevenShopIsOpen = False

def RequestExchange(role, msg):
	'''
	请求狂欢兑不停兑换
	@param role:
	@param msg:
	'''
	global DoubleElevenShopIsOpen
	if not DoubleElevenShopIsOpen:
		return
	
	#等级判断
	if role.GetLevel() < EnumGameConfig.DoubleElevenShop_LvLimit:
		return
	coding, cnt = msg
	cfg = DEShopConfig.DoubleElevenShop_Dict.get(coding)
	if not cfg:
		print "GE_EXC, double eleven shop can not find coding (%s) in DoubleElevenShop_Dict" % coding
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
		elShopObj = role.GetObj(EnumObj.DoubleElevenShop)[1]
		if coding not in elShopObj:
			elShopObj[coding] = cnt
		elif elShopObj[coding] + cnt > cfg.limitCnt:
			#超过限购
			return
		else:
			elShopObj[coding] += cnt
		role.GetObj(EnumObj.DoubleElevenShop)[1] = elShopObj
		#限购的记录购买数量
		role.SendObj(DoubleElevenShopData, elShopObj)
	
	with DoubleElevenShopEx_Log:
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
	global DoubleElevenShopIsOpen
	if not DoubleElevenShopIsOpen:
		return
	
	if role.GetLevel() < EnumGameConfig.DoubleElevenShop_LvLimit:
		return
	
	role.SendObj(DoubleElevenShopData, role.GetObj(EnumObj.DoubleElevenShop)[1])
	
def AfterLogin(role, param):
	if not role.GetObj(EnumObj.DoubleElevenShop):
		role.SetObj(EnumObj.DoubleElevenShop, {1:{}})
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		
		Event.RegEvent(Event.Eve_StartCircularActive, OpenElevenShop)
		Event.RegEvent(Event.Eve_EndCircularActive, CloseElevenShop)
		
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DoubleElevenShop_Exchange", "请求狂欢兑不停兑换"), RequestExchange)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DoubleElevenShop_Open", "请求打开狂欢兑不停商店"), RequestOpenShop)
		