#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 角色命令接口【第三方版】
#===============================================================================
import md5
import time
import Environment
from Integration import AutoHTML
from ComplexServer.Plug.DB import DBHelp
from django.http import HttpResponse
from Integration.Help import OtherHelp
from Integration.WebPage.User import Permission
from Integration.WebPage.model import me

KEY = "234lkkjas23k&×KGH$"

def Req_ExecuteRoleCommand(request):
	'''
	【接口】--第三方执行角色命令
	'''
	table = AutoHTML.Table([me.say(request,"区"), "<input type='text' name='serverid'>"])
	table.body.append([me.say(request,"帐号"), "<input type='text' name='account'>"])
	table.body.append([me.say(request,"命令"), "<input type='text' name='command'>"])
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
	</html>''' % (me.say(request,"第三方执行角色命令"),AutoHTML.GetURL(Res_ExecuteRoleCommand), table.ToHtml(),me.say(request,"执行"))
	return HttpResponse(html)

def Res_ExecuteRoleCommand(request):
	serverid = AutoHTML.AsInt(request.GET, "serverid")
	account = AutoHTML.AsString(request.GET, "account")
	command = AutoHTML.AsString(request.GET, "command")
	unixtime = int(time.time())
	sign = md5.new("%s%s%s%s%s" % (serverid, account, command, unixtime, KEY)).hexdigest()
	d = {"serverid": serverid,
		"account": account,
		"command": command,
		"unixtime":unixtime,
		"sign":sign
		}
	return _ExecuteRoleCommand(OtherHelp.Request(d))

def ExecuteRoleCommand(request):
	return OtherHelp.Apply(_ExecuteRoleCommand, request, __name__)

def _ExecuteRoleCommand(request):
	if Environment.EnvIsQQ():
		return AutoHTML.Error
	serverid = AutoHTML.AsInt(request.GET, "serverid")
	account = AutoHTML.AsString(request.GET, "account")
	unixtime = AutoHTML.AsInt(request.GET, "unixtime")
	command = AutoHTML.AsString(request.GET, "command")
	sign = AutoHTML.AsString(request.GET, "sign")
	if abs(time.time() - unixtime) > 900:
		return AutoHTML.Error
	if sign != md5.new("%s%s%s%s%s" % (serverid, account, command, unixtime, KEY)).hexdigest():
		return AutoHTML.Error
	con = DBHelp.ConnectMasterDBByID(serverid)
	with con as cur:
		cur.execute("select role_id from role_data where account = %s", account)
		result = cur.fetchall()
		if not result:
			return AutoHTML.Error
		role_id, = result[0]
		if DBHelp.InsertRoleCommand_Cur(cur, role_id, command):
			return HttpResponse("ok")
		else:
			return AutoHTML.Error



Permission.reg_develop(Req_ExecuteRoleCommand)
Permission.reg_develop(Res_ExecuteRoleCommand)
Permission.reg_public(ExecuteRoleCommand)
