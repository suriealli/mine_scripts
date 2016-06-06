#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Shop.LingShiShop")
#===============================================================================
# 灵石商店
#===============================================================================
from Game.Shop import Trade
import DynamicPath
import Environment
from ComplexServer.Log import AutoLog

if "_HasLoad" not in dir():
	Tips_1 = "兑换成功"

class LingShiShop(Trade.ShopBase):
	FilePath = DynamicPath.DynamicFolder(DynamicPath.ConfigPath).AppendPath("Shop").FilePath("LingShiShop.txt")
	def __init__(self):
		self.tradeId = int#名字必须这样
		self.itemCoding = int
		self.needItemCoding = int
		self.needCnt = int
		self.needLevel = int
		
	def do_trade(self, role, cnt):
		with TraLingShiShopTrade:
			self._do_trade(role, cnt)
	
	def _do_trade(self, role, cnt):
		#背包满
		if role.PackageIsFull():
			return
		
		if role.GetLevel() < self.needLevel:
			return
		
		needCnt = self.needCnt * cnt
		if role.ItemCnt(self.needItemCoding) < needCnt:
			return
		if role.DelItem(self.needItemCoding, needCnt) < needCnt:
			return
		role.AddItem(self.itemCoding, cnt)
		role.Msg(2, 0, Tips_1)
		
if "_HasLoad" not in dir():
	if not Environment.IsCross:
		LingShiShop.reg()
		
		#日志
		TraLingShiShopTrade = AutoLog.AutoTransaction("TraLingShiShopTrade", "灵石商店兑换")
		
		
		