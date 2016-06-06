#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.Interface.QQMyRoleBack")
#===============================================================================
# 查询是否是回流角色
#===============================================================================
from ComplexServer.Plug.DB import DBHelp
from Integration.WebPage.User import Permission
from Integration.Help import OtherHelp
from Integration import AutoHTML
from django.http import HttpResponse
from Integration.WebPage.model import me

def Test_CheckRoleBack(request):
	'''
	【接口】--回流角色vip等级
	'''
	html = '''
	<html>
	<head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
	<title>%s</title>
	</head>
	<body>
	<form action="%s" method="GET" target="_blank">
	%s：<input type="text" name="account">
	<input type="submit" value="%s" />
	</form>
	</body>
	</html>''' % (me.say(request,'回流角色vip等级'),AutoHTML.GetURL(CheckRoleBack),me.say(request,'角色帐号'),me.say(request,'查询'))
	return HttpResponse(html)

def CheckRoleBack(request):
	return OtherHelp.Apply(_CheckRoleBack, request, __name__)

def _CheckRoleBack(request):
	con = DBHelp.ConnectGlobalWeb()
	account = AutoHTML.AsString(request.GET, "account")
	with con as cur:
		cur.execute("select viplevel from back_role where account = %s;", account)
		ret = cur.fetchall()
		if not ret:
			return None
		return ret[0][0]

Permission.reg_public(CheckRoleBack)
