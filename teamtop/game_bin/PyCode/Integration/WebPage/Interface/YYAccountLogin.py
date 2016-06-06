#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.Interface.YYAccountLogin")
#===============================================================================
# YY登录
#===============================================================================
import md5
import time
import uuid
from ComplexServer.Plug.DB import DBHelp
from Integration import AutoHTML
from Integration.Help import OtherHelp
from django.http import HttpResponse, HttpResponseRedirect
from Integration.WebPage.User import Permission
from ComplexServer.API import Define as Http_Define
from Integration.WebPage.model import me

KEY = "YYlogin_#0odfd_sd1_o"
CLIENT_URL_TEST = "http://lqyy-ver-client.gamepf.com/?"
CLIENT_URL_NOMAL = "http://lqyy-entry.gamepf.com/?"

def Req_YYAccountLogin(request):
	'''
	【接口】--YY登录
	'''
	table = AutoHTML.Table([
		me.say(request,"帐号"),
		"<input type='text' name='account'>"
	])
	table.body.append([
		me.say(request,"游戏编号"),
		"<input type='text' name='game'>"
	])
	table.body.append([
		me.say(request,"服"),
		"<input type='text' name='server'>"
	])
	table.body.append([
		me.say(request,"防沉迷"),
		"<input type='text' name='fm'>"
	])
	table.body.append([
		me.say(request,"backurl"),
		"<input type='text' name='backurl'>"
	])
	table.body.append([
		me.say(request,"dwservId"),
		"<input type='text' name='dwservId'>"
	])
	table.body.append([
		me.say(request,"token"),
		"<input type='text' name='token'>"
	])
	table.body.append([
		me.say(request,"loaditems"),
		"<input type='text' name='loaditems'>"
	])
	table.body.append([
		me.say(request,"微端"),
		"<input type='text' name='client'>"
	])
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
	</html>''' % (
		me.say(request,"第三方登录"),
		AutoHTML.GetURL(Res_YYAccountLogin),
		table.ToHtml(),
		me.say(request,"登录")
	)
	return HttpResponse(html)

def Res_YYAccountLogin(request):
	account = AutoHTML.AsString(request.GET, "account")
	game = AutoHTML.AsString(request.GET, "game")
	server = AutoHTML.AsInt(request.GET, "server")
	fm = AutoHTML.AsInt(request.GET, "fm")
	backurl = AutoHTML.AsString(request.GET, "backurl")
	dwservId = AutoHTML.AsString(request.GET, "dwservId")
	tocken = AutoHTML.AsString(request.GET, "tocken")
	loaditems = AutoHTML.AsString(request.GET, "loaditems")
	client = AutoHTML.AsString(request.GET, "client")
	pf = AutoHTML.AsString(request.GET, "pf")
	unixtime = int(time.time())
	sign = md5.new("%s%s%s%s%s%s%s%s%s%s%s" % (account, fm, unixtime, game, server, backurl, dwservId, tocken, loaditems, client, KEY)).hexdigest()
	d = {"account":account,
		"game":game,
		"server":server,
		"fm":fm,
		"backurl":backurl,
		"dwservId":dwservId,
		"tocken":tocken,
		"loaditems":loaditems,
		"client":client,
		"time":unixtime,
		"sign":sign,
		"pf":pf
		}
	return _YYAccountLogin(OtherHelp.Request(d))
	
def YYAccountLogin(request):
	return OtherHelp.Apply(_YYAccountLogin, request, __name__)

def _YYAccountLogin(request):
	# 获取参数
	account = AutoHTML.AsString(request.GET, "account")
	game = AutoHTML.AsString(request.GET, "game")
	server = AutoHTML.AsInt(request.GET, "server")
	unixtime = AutoHTML.AsInt(request.GET, "time")
	fm = AutoHTML.AsInt(request.GET, "fm")
	backurl = AutoHTML.AsString(request.GET, "backurl")
	dwservId = AutoHTML.AsString(request.GET, "dwservId")
	tocken = AutoHTML.AsString(request.GET, "tocken")
	loaditems = AutoHTML.AsString(request.GET, "loaditems")
	client = AutoHTML.AsString(request.GET, "client")
	pf = AutoHTML.AsString(request.GET, "pf")
	sign = AutoHTML.AsString(request.GET, "sign")
	
	#检测时间
	ut = int(time.time())
	if abs(ut - unixtime) > 300:
		return HttpResponse(Http_Define.ErrorTime)
	
	#验证签名
	if sign.lower() != md5.new("%s%s%s%s%s%s%s%s%s%s%s" % (account, fm, unixtime, game, server, backurl, dwservId, tocken, loaditems, client, KEY)).hexdigest():
		return HttpResponse(Http_Define.ErrorSign)
	
	#临时登录密码
	session = uuid.uuid4()
	ip, port = DBHelp.GetPublicIPAndPortByZoneID(server)
	
	con = DBHelp.ConnectMasterDBByID(server)
	if not con:
		return HttpResponse(Http_Define.ErrorServer)
	with con as cur:
		if cur.execute("replace into account_login (account, session, login_time, thirdparty) values(%s, %s, now(), %s);", (account, session, 'yy')):
			url_param = "ip=%s&port=%s&serverid=%s&openid=%s&openkey=%s&userip=%s&pf=%s&pfkey=%s&fm=%s&backurl=%s&dwservId=%s&loaditems=%s&client=%s" % (ip, port, server, account, session, '',pf,'',fm,backurl,dwservId,loaditems,client)
			if int(server) == 10002:
				return HttpResponseRedirect(CLIENT_URL_TEST + url_param)
			else:
				return HttpResponseRedirect(CLIENT_URL_NOMAL + url_param)
		else:
			return HttpResponse("error_data")

Permission.reg_develop(Req_YYAccountLogin)
Permission.reg_develop(Res_YYAccountLogin)
Permission.reg_public(YYAccountLogin)