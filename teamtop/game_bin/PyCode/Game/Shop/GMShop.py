#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Shop.GMShop")
#===============================================================================
# GM商店
#===============================================================================
import DynamicPath
import Environment
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumInt32
from Game.Shop import Trade
from Game.SysData import WorldData

if "_HasLoad" not in dir():
	Tips_1 = "兑换成功"

class GMShop(Trade.ShopBase):
	FilePath = DynamicPath.DynamicFolder(DynamicPath.ConfigPath).AppendPath("Shop").FilePath("GMShop.txt")
	def __init__(self):
		self.tradeId = int		#名字必须这样
		self.itemCoding = int
		self.needGMScore = int
		self.needLevel = int
		self.needWorldLevel = int

	def do_trade(self, role, cnt):
		with TraGMShopTrade:
			self._do_trade(role, cnt)
	
	def _do_trade(self, role, cnt):
		#背包满
		if role.PackageIsFull():
			return
		
		if role.GetLevel() < self.needLevel:
			return
		
		if WorldData.GetWorldLevel() < self.needWorldLevel:
			return
		
		needGMScore = self.needGMScore * cnt
		if role.GetI32(EnumInt32.GMScore) < needGMScore:
			return
		
		role.DecI32(EnumInt32.GMScore, needGMScore)
		
		role.AddItem(self.itemCoding, cnt)
		
		role.Msg(2, 0, Tips_1)
		
if "_HasLoad" not in dir():
	if not Environment.IsCross:
		GMShop.reg()
		
		#日志
		TraGMShopTrade = AutoLog.AutoTransaction("TraGMShopTrade", "GM商店兑换")
		
		