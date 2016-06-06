#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.Interface.AccountLogin")
#===============================================================================
# 帐号登录
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
import Environment

KEY = "ifg#98s_twwq_#f3dna"

def GetKey():
	#新版KEY每一个版本都分配一个key
	if Environment.IsRUXP:
		return "101XP_loginppo_#sahJ7d_0oIO_s"
	elif Environment.IsPL:
		return "Poland_loginss#oO0eef5843ed#kcx"
	elif Environment.IsPLXP:
		return "Poland101xp_loginss#_ddddd#ccxx#eer"
	elif Environment.IsTKPLUS1:
		return "tkplus1#_longins_#0o12gfdsins"
	elif Environment.IsRURBK:
		return 'RBK_loginalfjaljljf#lkjlkj#jkjha'
	elif Environment.IsRUGN:
		return "GN_logindfjaljljf#dfdsfs#jkjha"
	elif Environment.IsTKESP:
		return "tkesp#_logins0o_#dfg134#_1fgh"
	elif Environment.IsFR:
		return "#_frlogin_#dfd0o_0dfd_#34d"
	elif Environment.IsNAPLUS1:
		return "_#naplus1-#dfgdg870o_dfm8dfj#"
	elif Environment.IsEN:
		return "#_dfs_en-d0o34213dffd_#8dgd"
	elif Environment.IsESP:
		return "#_gxs_esp-d0ofasfdsdffd_#8dddgd"
	elif Environment.Is7K:
		return "7k7k_login_#_#sdffd_#8dddgd#34d"
	else:
		#旧版的
		return KEY


def Req_AccountLogin(request):
	'''
	【接口】--第三方登录
	'''
	table = AutoHTML.Table([
		me.say(request,"客户端地址"),
		"<input type='text' name='clienturl'>"
	])
	table.body.append([
		me.say(request,"区"),
		"<input type='text' name='serverid'>"
	])
	table.body.append([
		me.say(request,"帐号"),
		"<input type='text' name='account'>"
	])
	table.body.append([
		me.say(request,"第三方数据"),
		"<input type='text' name='thirdparty'>"
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
		AutoHTML.GetURL(Res_AccountLogin),
		table.ToHtml(),
		me.say(request,"登录")
	)
	return HttpResponse(html)

def Res_AccountLogin(request):
	clienturl = AutoHTML.AsString(request.GET, "clienturl")
	serverid = AutoHTML.AsInt(request.GET, "serverid")
	account = AutoHTML.AsString(request.GET, "account")
	thirdparty = AutoHTML.AsString(request.GET, "thirdparty")
	unixtime = int(time.time())
	sign = md5.new("%s%s%s%s%s" % (serverid, account, thirdparty, unixtime, GetKey())).hexdigest()
	d = {"serverid": serverid,
		"account": account,
		"thirdparty": thirdparty,
		"unixtime": unixtime,
		"sign": sign
		}
	response = _AccountLogin(OtherHelp.Request(d))
	if clienturl:
		return HttpResponseRedirect(clienturl + response.content)
	else:
		return response



def AccountLogin(request):
	return OtherHelp.Apply(_AccountLogin, request, __name__)

def _AccountLogin(request):
	# 获取参数
	serverid = AutoHTML.AsInt(request.GET, "serverid")
	account = AutoHTML.AsString(request.GET, "account")
	thirdparty = AutoHTML.AsString(request.GET, "thirdparty")
	unixtime = AutoHTML.AsInt(request.GET, "unixtime")
	sign = AutoHTML.AsString(request.GET, "sign")
	userip = AutoHTML.AsString(request.GET, "userip")
	# 检测签名
	ut = int(time.time())
	if abs(ut - unixtime) > 900:
		return HttpResponse(Http_Define.ErrorTime)
	
#	if thirdparty:
#		thirdparty_eval = eval(thirdparty)
#	else:
#		pass
	#验证签名
	if sign != md5.new("%s%s%s%s%s" % (serverid, account, thirdparty, unixtime, GetKey())).hexdigest():
		return HttpResponse(Http_Define.ErrorSign)
	
	#临时登录密码
	session = uuid.uuid4()
	ip, port = DBHelp.GetPublicIPAndPortByZoneID(serverid)
	
	con = DBHelp.ConnectMasterDBByID(serverid)
	with con as cur:
		if cur.execute("replace into account_login (account, session, login_time, thirdparty) values(%s, %s, now(), %s);", (account, session, thirdparty)):
			return HttpResponse("ip=%s&port=%s&serverid=%s&openid=%s&openkey=%s&userip=%s&pf=pf&pfkey=pfkey" % (ip, port, serverid, account, session, userip))
		else:
			return HttpResponse("error_data")

Permission.reg_design(Req_AccountLogin)
Permission.reg_design(Res_AccountLogin)
Permission.reg_public(AccountLogin)

