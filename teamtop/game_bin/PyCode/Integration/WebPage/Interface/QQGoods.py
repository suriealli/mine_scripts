#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# QQ购物
#===============================================================================
import time
import urllib
import httplib
import Environment
from ComplexServer.API import QQHttp
from ComplexServer.Plug.DB import DBHelp
from Integration import AutoHTML
from Integration.Help import OtherHelp
from Integration.WebPage.User import Permission
from Integration.WebPage.Interface import QQConfirm

BUY_GOODS_URI = "/v3/pay/buy_goods"
BUY_GOODS_SQL = "insert into charge (account, role_id, token, from_1, from_2, from_3, create_from, payitem, level, openkey, dt) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW());"
#GET_GOODS_SQL = "select role_id, openkey, from_1 from charge where token = %s and now() < dt + INTERVAL 15 MINUTE;"
GET_GOODS_SQL = "select role_id, openkey, from_1 from charge where token = %s;"
DRIVE_GOODS_SQL = "update charge set billno = %s, amt = %s, payamt_coins = %s, pubacct_payamt_coins = %s where token = %s;"

def BuyGoods(request):
	return OtherHelp.Apply(_BuyGoods, request, "BuyGoods.log")

def _BuyGoods(request):
	assert Environment.EnvIsQQ()
	# 参数
	openid = AutoHTML.AsString(request.GET, "openid")
	openkey = AutoHTML.AsString(request.GET,"openkey")
	appmode = AutoHTML.AsString(request.GET, "appmode")
	pf = AutoHTML.AsString(request.GET, "pf")
	create_pf = AutoHTML.AsString(request.GET, "create_pf")
	from2 = AutoHTML.AsString(request.GET, "from2")
	from3 = AutoHTML.AsString(request.GET, "from3")
	pfkey = AutoHTML.AsString(request.GET, "pfkey")
	roleid = AutoHTML.AsInt(request.GET,"roleid")
	ts = int(time.time())
	payitem = AutoHTML.AsString(request.GET, "payitem")
	goodsmeta = AutoHTML.AsString(request.GET, "goodsmeta")
	goodsurl = AutoHTML.AsString(request.GET, "goodsurl")
	level = AutoHTML.AsInt(request.GET, "level")
	zoneid = DBHelp.GetDBIDByRoleID(roleid)
	get = {"openid":openid, "openkey":openkey, "appid":QQHttp.APP_ID,
		"appmode":appmode, "pf":pf, "pfkey":pfkey, "ts":ts, "payitem":payitem,
		"goodsmeta":goodsmeta, "goodsurl":goodsurl, "zoneid":zoneid}
	QQHttp.make_sig(BUY_GOODS_URI, get, {})
	# https访问
	https_con = httplib.HTTPSConnection(QQHttp.HOST)
	https_con.request("GET", BUY_GOODS_URI+ "?" + urllib.urlencode(get))
	response = https_con.getresponse()
	# 访问失败
	if response.status != 200:
		return repr({"ret":1, "msg":"connect error."})
	sbody = response.read()
	body = eval(sbody)
	if 0 != body["ret"]:
		return body
	# 写数据库
	mysql_con = DBHelp.ConnectMasterDBByID(zoneid)
	with mysql_con as cur:
		cur.execute(BUY_GOODS_SQL, (openid, roleid, body["token"], pf, from2, from3, create_pf, payitem, level, openkey))
		cur.close()
	mysql_con.close()
	# 返回
	return sbody

def DriveGoods(request):
	return OtherHelp.Apply(_DriveGoods, request, "DriveGoods.log")

def _DriveGoods(request):
	assert Environment.EnvIsQQ()
	# 参数
	openid = AutoHTML.AsString(request.GET,"openid")
	payitem = AutoHTML.AsString(request.GET,"payitem")
	token = AutoHTML.AsString(request.GET,"token")
	billno = AutoHTML.AsString(request.GET,"billno")
	zoneid = AutoHTML.AsString(request.GET,"zoneid")
	version = AutoHTML.AsString(request.GET, "version")
	providetype = AutoHTML.AsString(request.GET,"providetype")
	amt = AutoHTML.AsInt(request.GET,"amt")
	payamt_coins = AutoHTML.AsInt(request.GET,"payamt_coins")
	pubacct_payamt_coins = AutoHTML.AsInt(request.GET,"pubacct_payamt_coins")
	# 校验发货
	con = DBHelp.ConnectMasterDBByID(zoneid)
	with con as cur:
		cur.execute(GET_GOODS_SQL, token)
		result = cur.fetchall()
		if not result:
			return repr({"ret":3, "msg":" token is not exist."})
		roleid, openkey, pf = result[0]
		cur.execute(DRIVE_GOODS_SQL, (billno, amt, payamt_coins, pubacct_payamt_coins, token))
		bcammand = DBHelp.InsertRoleCommand_Cur(cur, roleid, "('Game.ThirdParty.QPointShop', 'OnDeliverGoods', '%s')" % payitem)
		cur.close()
	con.close()
	# 确认
	QQConfirm.Confirm(openid, openkey, pf, int(time.time()), payitem, token, billno, version, zoneid, providetype, 0, amt, payamt_coins, pubacct_payamt_coins)
	# 返回
	if bcammand:
		return repr({"ret":0, "msg":"success."})
	else:
		return repr({"ret":4, "msg":"no role or role is lost."})

Permission.reg_public(BuyGoods)
Permission.reg_public(DriveGoods)

