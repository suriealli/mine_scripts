#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.Interface.NARoleBack")
#===============================================================================
# 北美流失用户召回
#===============================================================================
import md5
import time
from django.http import HttpResponse
from Integration.Help import OtherHelp
from Integration import AutoHTML
from Integration.WebPage.User import Permission
from ComplexServer.Plug.DB import DBHelp
from ComplexServer.API import Define as Http_Define
from Integration.WebPage.model import me

KEY = "s5#4qk&cw_de#dvz6H"

def Req_RoleBack(request):
	'''
	【接口】--北美流失召回
	'''
	table = AutoHTML.Table([me.say(request,"区"), "<input type='text' name='serverid'>"])
	table.body.append([me.say(request,"帐号"), "<input type='text' name='account'>"])
	table.body.append(["itemCoding", "<input type='text' name='itemCoding'>"])
	html = '''
	<html>
	<head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
	<title>%s</title>
	</head>
	<body>
	<form action="%s" method="GET" target="_blank">
	%s
	<input type="submit" value="%s" />
	</form>
	</body>
	</html>''' % (me.say(request,"北美流失召回"),AutoHTML.GetURL(Res_RoleBack), table.ToHtml(),me.say(request,"召回"))
	return HttpResponse(html)

def Res_RoleBack(request):
	serverid = AutoHTML.AsInt(request.GET, "serverid")
	account = AutoHTML.AsString(request.GET, "account")
	itemCoding = AutoHTML.AsInt(request.GET, "itemCoding")
	#unixTimes = AutoHTML.AsInt(request.GET, "unixTimes")
	unixtime = int(time.time())
	sign = md5.new("%s%s%s%s%s" % (serverid, account, itemCoding, unixtime, KEY)).hexdigest()
	d = {"serverid": serverid,
		"account": account,
		"itemCoding" :itemCoding,
		"unixtime" : unixtime,
		"sign" : sign,
		}
	return _RoleBack(OtherHelp.Request(d))


def RoleBack(request):
	return OtherHelp.Apply(_RoleBack, request, __name__)

def _RoleBack(request):
	serverid = AutoHTML.AsInt(request.GET, "serverid")
	account = AutoHTML.AsString(request.GET, "account")
	unixtime = AutoHTML.AsInt(request.GET, "unixtime")
	itemCoding = AutoHTML.AsInt(request.GET, "itemCoding")
	sign = AutoHTML.AsString(request.GET, "sign")
	#验证时间
	#if abs(time.time() - unixtime) > 900:
	#	return HttpResponse(Http_Define.ErrorTime)
	#验证签名
	if sign != md5.new("%s%s%s%s%s" % (serverid, account, itemCoding, unixtime, KEY)).hexdigest():
		return HttpResponse(Http_Define.ErrorSign)
	
	con = DBHelp.ConnectMasterDBByID(serverid)
	with con as cur:
		cur.execute("select role_id, di32_11 from role_data where account = %s; ", account)
		result = cur.fetchall()
		if not result:
			return HttpResponse("error_norole")
		
		role_id = result[0][0]
		#经确认无需判断等级
#		role_level = result[0][1]
#		if role_level < 60:
#			return HttpResponse("role level not enought")

		if not DBHelp.InsertRoleCommand_Cur(cur, role_id, "('Game.ThirdParty.NA.NARoleBack', 'NABackReward', (%s, 1, %s))" % (itemCoding, unixtime)):
			return HttpResponse("error_rolecommamd")
	
		return HttpResponse("ok")



Permission.reg_develop(Req_RoleBack)
Permission.reg_develop(Res_RoleBack)
Permission.reg_public(RoleBack)
