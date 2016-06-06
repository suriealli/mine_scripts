#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# QQ开通、续费黄钻
#===============================================================================
from ComplexServer.Plug.DB import DBHelp
from Integration import AutoHTML
from Integration.Help import OtherHelp
from Integration.WebPage.User import Permission

def Open(request):
	return OtherHelp.Apply(_Open, request, __name__)

def _Open(request):
	openid = AutoHTML.AsString(request.GET, "openid")
	#appid = AutoHTML.AsString(request.GET, "appid")
	#ts = AutoHTML.AsString(request.GET, "ts")
	#payitem = AutoHTML.AsString(request.GET, "payitem")
	discountid = AutoHTML.AsString(request.GET, "discountid")
	token = AutoHTML.AsString(request.GET, "token")
	billno = AutoHTML.AsString(request.GET, "billno")
	#version = AutoHTML.AsString(request.GET, "version")
	zoneid = AutoHTML.AsInt(request.GET, "zoneid")
	#providetype = AutoHTML.AsString(request.GET, "providetype")
	#sig = AutoHTML.AsString(request.GET, "sig")
	
	con = DBHelp.ConnectMasterDBByID(zoneid)
	with con as cur:
		cur.execute("select role_id from role_data where account = %s;", openid)
		result = cur.fetchall()
		if not result:
			return repr({"ret":5, "msg":"no openid"})
		roleid = result[0][0]
		g_con = DBHelp.ConnectGlobalWeb()
		with g_con as g_cur:
			h = g_cur.execute("insert ignore qq_open(account, token, billno) values(%s, %s, %s);", (openid, token, billno))
			# 重复发货，返回OK
			if h == 0:
				return repr({"ret":0, "msg":"OK"})
		# 通知服务器发货
		if DBHelp.InsertRoleCommand_Cur(cur, roleid, "('Game.ThirdParty.QOpen', 'OnKaiTongCommand', '%s')" % discountid):
			return repr({"ret":0, "msg":"OK"})
		else:
			return repr({"ret":6, "msg":"no role or role is lost."})

Permission.reg_public(Open)
