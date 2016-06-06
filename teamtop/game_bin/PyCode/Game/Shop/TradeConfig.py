#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Shop.TradeConfig")
#===============================================================================
# 交易商店
#===============================================================================
import Environment
from ComplexServer import Init
from Game.Shop import Trade

def OnServerUp():
	for shop_name, shop_class in Trade.Shops.iteritems():
		Trade.Goods[shop_name] = d = {}
		for shop in shop_class.ToClassType():
			if shop.tradeId in d:
				print "GE_EXC repeat tradeId(%s) in %s.txt" % (shop.tradeId, shop_name)
				continue
			d[shop.tradeId] = shop
			shop.Preprocess()
		
		if shop_name == "Mall":
			#特殊，额外记录商城表
			from Game.Shop import Mall
			Mall.MallConfig_Dict = d

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Init.InitCallBack.RegCallbackFunction(OnServerUp)

