#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Shop.Trade")
#===============================================================================
# 交易
#===============================================================================
import cRoleMgr
from Util.File import TabFile
from Common.Message import AutoMessage


class ShopBase(TabFile.TabLine):
	FilePath = None
	@classmethod
	def reg(cls):
		if cls.__name__ in Shops:
			print "GE_EXC, repeat shop(%s)" % cls.__name__
			return
		Shops[cls.__name__] = cls
	
	def Preprocess(self):
		#预处理
		pass
	
	def do_trade(self, role, argv):
		#需要加日志事务,切记
		assert False

def OnClientRequestTrade(role, msg):
	'''
	客户端请求交易
	@param role:
	@param msg:
	'''
	shopname, tradeid, argv = msg
	#购买数量不合法
	if argv <= 0:
		role.WPE(11)
		return
	shop = Goods.get(shopname)
	if shop is None:
		print "GE_EXC, can't find shop(%s) by role(%s)" % (shopname, role.GetRoleID())
		role.WPE()
		return
	goods = shop.get(tradeid)
	if goods is None:
		print "GE_EXC, can't find shop(%s) goods(%s) by role(%s)" % (shopname, tradeid, role.GetRoleID())
		role.WPE()
		return
	goods.do_trade(role, argv)

if "_HasLoad" not in dir():
	Shops = {}
	Goods = {}
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Trade_Request", "客户端请求商品交易"), OnClientRequestTrade)


