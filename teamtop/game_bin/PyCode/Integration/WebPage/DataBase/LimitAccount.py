#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 限登录帐号
#===============================================================================
from Integration import AutoHTML
from ComplexServer.Plug.DB import DBHelp
from django.http import HttpResponse
from Integration.WebPage.User import Permission
from Integration.WebPage.model import me

def Req(request):
	'''【数据与工具】--添加内部登录帐号'''
	account = AutoHTML.AsString(request.GET, "account")
	info = AutoHTML.AsString(request.GET, "info")
	if account and info:
		con = DBHelp.ConnectGlobalWeb()
		with con as cur:
			cur.execute("replace into inner_account(account, info) values(%s, %s);", (account, info))
			cur.close()
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		cur.execute("select account, info from inner_account;")
		table = AutoHTML.Table([me.say(request,"帐号"),me.say(request,"信息")], cur.fetchall())
	html = '''
	<html>
	<head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
	<title>%s</title>
	</head>
	<body>
	%s
	<form action="%s" method="GET">
	%s：<input type="text" name="account"><br>
	%s：<input type="text" name="info"><br>
	<input type="submit" value="%s" />
	</form>
	</body>
	</html>'''%(
		me.say(request,"内部登录帐号"),
		table.ToHtml(),
		AutoHTML.GetURL(Req),
		me.say(request,"帐号"),
		me.say(request,"信息"),
		me.say(request,"添加")
	)
	return HttpResponse(html)


def ReqDelete(request):
	'''【数据与工具】--删除内部登录帐号'''
	account = AutoHTML.AsString(request.GET, "account")
	if account:
		con = DBHelp.ConnectGlobalWeb()
		with con as cur:
			cur.execute("delete from inner_account where account = %s;", account)
			cur.close()
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		cur.execute("select account, info from inner_account;")
		table = AutoHTML.Table([me.say(request,"帐号"),me.say(request,"信息")], cur.fetchall())
	html = '''
	<html>
	<head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
	<title>%s</title>
	</head>
	<body>
	%s
	<form action="%s" method="GET">
	%s：<input type="text" name="account"><br>
	<input type="submit" value="%s" />
	</form>
	</body>
	</html>'''%(
		me.say(request,"内部登录帐号"),
		table.ToHtml(),
		AutoHTML.GetURL(ReqDelete),
		me.say(request,"帐号"),
		me.say(request,"删除")
	)
	return HttpResponse(html)



Permission.reg_operate(Req)
Permission.reg_operate(ReqDelete)