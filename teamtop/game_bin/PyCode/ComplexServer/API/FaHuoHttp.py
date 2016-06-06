#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("ComplexServer.API.FaHuoHttp")
#===============================================================================
# 发货HTTP访问
#===============================================================================
import Environment
from ComplexServer.Plug.Http import HttpProxy

FA_HOU_HOST = "1.4.14.176"
FA_HOU_PORT = 1027
if Environment.IsQQUnion:
	FA_HOU_HOST = "10.207.141.155"
	FA_HOU_PORT = 9001
FA_HOU_HOST1 = "10.207.150.242"
FA_HOU_PORT1 = 9001
FA_HOU_HOST2 = "10.207.150.241"
FA_HOU_PORT2 = 9001

BUY_GOODS_URI = "/Interface/QQGoods/BuyGoods/"

def buy_goods(openid, openkey, pf, create_pf, from2, from3, pfkey, roleid, payitem, goodsmeta, goodsurl, level, backfun, regparam):
	get = {"openid":openid, "openkey":openkey, "appmode": 1,
		"pf":pf, "create_pf":create_pf, "from2":from2, "from3":from3, "pfkey":pfkey,
		"roleid":roleid, "payitem":payitem, "goodsmeta":goodsmeta, "goodsurl":goodsurl, "level":level}
	HttpProxy.HttpRequest(FA_HOU_HOST, FA_HOU_PORT, BUY_GOODS_URI, get, None, 30, backfun, regparam)

