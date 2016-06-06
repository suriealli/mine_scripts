#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.MysteryShop.MysteryShop")
#===============================================================================
# 神秘商店
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Activity.MysteryShop import MysteryShopConfig
from Game.SysData import WorldData
from Game.Role.Data import EnumObj, EnumTempObj
from Game.Role import Event
from Game.Activity import CircularDefine

if "_HasLoad" not in dir():
	MysterShopRecord = AutoMessage.AllotMessage("MysterShopRecord", "神秘商店兑换记录")
	
	MysterShopMine_Log = AutoLog.AutoTransaction("MysterShopMine_Log", "神秘商店兑换矿石")
	MysterShopItem_Log = AutoLog.AutoTransaction("MysterShopItem_Log", "神秘商店兑换道具")
	
	MysteryShopIsOpen = False
	
def OpenMysterShop(role, param):
	if param != CircularDefine.CA_MysterShop:
		return
	
	global MysteryShopIsOpen
	if MysteryShopIsOpen:
		print "GE_EXC, MysterShop is already open"
		return
	MysteryShopIsOpen = True
	
def CloseMysterShop(role, param):
	if param != CircularDefine.CA_MysterShop:
		return
	
	global MysteryShopIsOpen
	if not MysteryShopIsOpen:
		print "GE_EXC, MysterShop is already close"
		return
	MysteryShopIsOpen = False
	
def RequestOpenMysteryShop(role, msg):
	'''
	请求打开神秘商店
	@param role:
	@param msg:
	'''
	global MysteryShopIsOpen
	if not MysteryShopIsOpen:
		return
	
	if role.GetLevel() < EnumGameConfig.MysterShop_LevelLimit:
		return
	
	role.SendObj(MysterShopRecord, role.GetObj(EnumObj.MysterShopRecord))
	
def RequestExchangeMine(role, msg):
	'''
	请求兑换矿石
	@param role:
	@param msg:
	'''
	global MysteryShopIsOpen
	if not MysteryShopIsOpen:
		return
	if role.GetLevel() < EnumGameConfig.MysterShop_LevelLimit:
		return
	
	itemCoding, cnt = msg
	cfg = MysteryShopConfig.MysterShopMine_Dict.get(itemCoding)
	if not cfg:
		return
	needUnbindRMB = cfg.needUnbindRMB * cnt
	if role.GetUnbindRMB() < needUnbindRMB:
		return
	if role.PackageIsFull():
		role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
		return
	
	with MysterShopMine_Log:
		role.DecUnbindRMB(needUnbindRMB)
		role.AddItem(*msg)
		role.Msg(2, 0, GlobalPrompt.Reward_Item_Tips % msg)
	
def RequestExchangItem(role, msg):
	'''
	请求兑换道具
	@param role:
	@param msg:
	'''
	global MysteryShopIsOpen
	if not MysteryShopIsOpen:
		return
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.MysterShop_LevelLimit:
		return
	
	itemCoding = msg
	if not itemCoding:
		return
	cfg = MysteryShopConfig.MysterShop_Dict.get(itemCoding)
	if not cfg:
		return
	#世界等级
	if WorldData.GetWorldLevel() < cfg.needWorldLevel:
		return
	#角色等级
	if roleLevel < cfg.needLevel:
		return
	
	if (not cfg.isItem) and role.TarotPackageIsFull():
		#是命魂且命魂背包满
		role.Msg(2, 0, GlobalPrompt.TarotIsFull_Tips)
		return
	elif (cfg.isItem == 1) and role.PackageIsFull():
		#是物品且物品背包满
		role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
		return
	elif (cfg.isItem == 2) and role.GetTempObj(EnumTempObj.TalentCardMgr).PackageIsFull():
		#是天赋卡且天赋卡背包满
		role.Msg(2, 0, GlobalPrompt.TalentIsFull_Tips)
		return
	
	exchangeRecord = role.GetObj(EnumObj.MysterShopRecord)
	#限购判断
	if cfg.isLimit and itemCoding in exchangeRecord and exchangeRecord[itemCoding] >= cfg.limitCnt:
		return
	if role.ItemCnt(cfg.needCoding) < cfg.needItemCnt:
		return
	
	with MysterShopItem_Log:
		role.DelItem(cfg.needCoding, cfg.needItemCnt)
		#只记录限购的购买数量
		if cfg.isLimit and not exchangeRecord.get(itemCoding):
			exchangeRecord[itemCoding] = 1
		elif cfg.isLimit and exchangeRecord.get(itemCoding):
			exchangeRecord[itemCoding] += 1
		role.SetObj(EnumObj.MysterShopRecord, exchangeRecord)
		if not cfg.isItem:
			role.AddTarotCard(itemCoding, 1)
			role.Msg(2, 0, GlobalPrompt.Reward_Tips + GlobalPrompt.Tarot_Tips % (itemCoding, 1))
		elif cfg.isItem == 1:
			role.AddItem(itemCoding, 1)
			role.Msg(2, 0, GlobalPrompt.Reward_Tips + GlobalPrompt.Item_Tips % (itemCoding, 1))
		elif cfg.isItem == 2:
			role.AddTalentCard(itemCoding)
			role.Msg(2, 0, GlobalPrompt.Reward_Tips + GlobalPrompt.Talent_Tips % (itemCoding, 1))
		else:
			print 'GE_EXC, MysteryShop item type error'
			return
		
		role.SendObj(MysterShopRecord, exchangeRecord)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, OpenMysterShop)
		Event.RegEvent(Event.Eve_EndCircularActive, CloseMysterShop)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("MysterShop_OpenPanel", "请求打开神秘商店"), RequestOpenMysteryShop)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("MysterShop_Mine", "请求兑换矿石"), RequestExchangeMine)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("MysterShop_Item", "请求兑换道具"), RequestExchangItem)
		