#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 角色数据查询
#===============================================================================
import json
from Integration import AutoHTML
from ComplexServer.Plug.DB import DBHelp
from django.http import HttpResponse
from Integration.Help import OtherHelp
from Integration.WebPage.User import Permission
from Integration.WebPage.model import me

def Req_GetRoleData(request):
	'''
	【接口】--第三方获取数据
	'''
	table = AutoHTML.Table([me.say(request,"区"), "<input type='text' name='serverid'>"])
	table.body.append([me.say(request,"帐号"), "<input type='text' name='account'>"])
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
	</html>''' % (me.say(request,"第三方获取数据"),AutoHTML.GetURL(Res_GetRoleData), table.ToHtml(),me.say(request,"查询"))
	return HttpResponse(html)

def Res_GetRoleData(request):
	serverid = AutoHTML.AsInt(request.GET, "serverid")
	account = AutoHTML.AsString(request.GET, "account")
	d = {"serverid": serverid,
		"account": account,
		}
	return _GetRoleData(OtherHelp.Request(d))

def GetRoleData(request):
	return OtherHelp.Apply(_GetRoleData, request, __name__)

def _GetRoleData(request):
	serverid = AutoHTML.AsInt(request.GET, "serverid")
	account = AutoHTML.AsString(request.GET, "account")
	con = DBHelp.ConnectMasterDBByID(serverid)
	with con as cur:
		cur.execute("select role_id, role_name, di32_11 from role_data where account = %s", account)
		result = cur.fetchall()
		if not result:
			return AutoHTML.Error
		role_id, role_name, level = result[0]
		return HttpResponse(json.dumps({"role_id":role_id, "role_name":role_name, "level":level}))



Permission.reg_develop(Req_GetRoleData)
Permission.reg_develop(Res_GetRoleData)
Permission.reg_public(GetRoleData)
