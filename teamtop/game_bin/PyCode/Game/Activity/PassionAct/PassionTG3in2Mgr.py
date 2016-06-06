#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionTG3in2Mgr")
#===============================================================================
# 感恩节买二送一
#===============================================================================
import Environment
import cRoleMgr
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Activity import CircularDefine
from Game.Activity.PassionAct import PassionTG3in2Config

if "_HasLoad" not in dir():
	TG3in2IsOpen = False
	
	DoubleElevenShopData = AutoMessage.AllotMessage("TG3in2ShopData", "买二送一商店数据")
	
	DoubleElevenShopEx_Log = AutoLog.AutoTransaction("TG3in2ShopEx_Log", "买二送一购买日志")
	
def Open3in2Shop(param1, param2):
	if param2 != CircularDefine.CA_PassionTGBuy3in2:
		return
	
	global TG3in2IsOpen
	if TG3in2IsOpen:
		print "GE_EXC, TG3in2IsOpen is already open"
		return
	
	TG3in2IsOpen = True

def Close3in2Shop(param1, param2):
	if param2 != CircularDefine.CA_PassionTGBuy3in2:
		return
	
	global TG3in2IsOpen
	if not TG3in2IsOpen:
		print "GE_EXC, TG3in2IsOpen is already close"
		return
	
	TG3in2IsOpen = False

def RequestBuy(role, msg):
	'''
	请求买二送一购买
	@param role:
	@param msg:
	'''
	global TG3in2IsOpen
	if not TG3in2IsOpen:
		return

	coding, cnt = msg
	cfg = PassionTG3in2Config.TG3in2Config_Dict.get(coding)
	if not cfg:
		print "GE_EXC,TG3in2 shop can not find coding (%s) in TG3in2Config_Dict" % coding
		return
	
	#角色等级不足
	if role.GetLevel() < cfg.needLevel:
		return
	
	if not cnt: return
	
	#不是3整数倍
	if cnt % 3:
		return
	#充值神石不够
	realCnt = (cnt/3) * 2
	needRMB = cfg.needRMB * realCnt
	if role.GetUnbindRMB_Q() < needRMB:
		role.Msg(2, 0, GlobalPrompt.UnbindRMB_Q_NotEnough)
		return

	if role.PackageEmptySize() < cnt:
		role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips2)
		return
	
	#全部不限购买
	with DoubleElevenShopEx_Log:
		#发放物品
		role.DecUnbindRMB_Q(needRMB)
		role.AddItem(coding, cnt)
	role.Msg(2, 0, GlobalPrompt.Reward_Tips + GlobalPrompt.Item_Tips % (coding, cnt))
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		
		Event.RegEvent(Event.Eve_StartCircularActive, Open3in2Shop)
		Event.RegEvent(Event.Eve_EndCircularActive, Close3in2Shop)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TG3in2Shop_Exchange", "请求买二送一购买"), RequestBuy)
		
