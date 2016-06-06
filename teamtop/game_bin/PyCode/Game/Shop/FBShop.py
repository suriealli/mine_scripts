#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Shop.FBShop")
#===============================================================================
# 副本兑换商店
#===============================================================================
import DynamicPath
from ComplexServer.Log import AutoLog
from Game.Shop import Trade
from Game.Role.Data import EnumInt16
from Game.Task import EnumTaskType
from Game.Role import Event
from Game import GlobalMessage


Tips_1 = "兑换成功"

class FBShop(Trade.ShopBase):
	FilePath = DynamicPath.DynamicFolder(DynamicPath.ConfigPath).AppendPath("Shop").FilePath("FBShop.txt")
	def __init__(self):
		self.tradeId = int#名字必须这样
		self.itemCoding = int
		self.needItemCoding = int
		self.needCnt = int
		self.needLevel = int
		self.needActiveFBID = int
	
	def Preprocess(self):
		#预处理
		from Game.Item import ItemConfig
		self.isEquipment = False
		if self.itemCoding in ItemConfig.EquipmentCodingSet:
			self.isEquipment = True

	def do_trade(self, role, argv):
		with TraFBShopTrade:
			self._do_trade(role, argv)
	
	def _do_trade(self, role, cnt):
		#背包满
		if role.PackageIsFull():
			return
		
		if role.GetLevel() < self.needLevel:
			return
		
		if role.GetI16(EnumInt16.FB_Active_ID) < self.needActiveFBID:
			return
		
		needCnt = self.needCnt * cnt
		if role.ItemCnt(self.needItemCoding) < needCnt:
			return
		if role.DelItem(self.needItemCoding, needCnt) < needCnt:
			return
		role.AddItem(self.itemCoding, cnt)
		Event.TriggerEvent(Event.Eve_SubTask, role, (EnumTaskType.EnSubTask_ExChangeItem, self.itemCoding))
		role.Msg(2, 0, Tips_1)
		if role.GetLevel() <= 39 and self.isEquipment is True:
			#39级之前需要提示穿装备
			role.SendObj(GlobalMessage.Notify_PutOnEquipment, None)

if "_HasLoad" not in dir():
	FBShop.reg()
	TraFBShopTrade = AutoLog.AutoTransaction("TraFBShopTrade", "副本商店兑换")
	
	