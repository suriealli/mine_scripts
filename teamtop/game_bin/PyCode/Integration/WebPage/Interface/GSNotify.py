#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.Interface.GSNotify")
#===============================================================================
# 客服系统回复提示
#===============================================================================
from django.http import HttpResponse
from Integration.Help import OtherHelp
from Integration import AutoHTML
from Integration.WebPage.User import Permission
from ComplexServer.Plug.DB import DBHelp
from Integration.WebPage.model import me

def Req_GSNotify(request):
	'''
	【接口】--客服系统回复提示
	'''
	table = AutoHTML.Table([me.say(request,"区"), "<input type='text' name='serverid'>"])
	table.body.append([me.say(request,"帐号"), "<input type='text' name='account'>"])
	table.body.append(["roleid", "<input type='text' name='roleid'>"])
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
	</html>''' % (me.say(request,"客服系统回复提示"),AutoHTML.GetURL(Res_GSNotify), table.ToHtml(),me.say(request,"提示"))
	return HttpResponse(html)

def Res_GSNotify(request):
	serverid = AutoHTML.AsInt(request.GET, "serverid")
	account = AutoHTML.AsString(request.GET, "account")
	roleid = AutoHTML.AsString(request.GET, "roleid")
	d = {"serverid": serverid,
		"account": account,
		"roleid" :roleid,
		}
	return _GSNotify(OtherHelp.Request(d))


def GSNotify(request):
	return OtherHelp.Apply(_GSNotify, request, __name__)

def _GSNotify(request):
	serverid = AutoHTML.AsInt(request.GET, "serverid")
	#account = AutoHTML.AsString(request.GET, "account")
	roleid = AutoHTML.AsInt(request.GET, "roleid")
	con = DBHelp.ConnectMasterDBByID(serverid)
	with con as cur:
		if not DBHelp.InsertRoleCommand_Cur(cur, roleid, "('Game.ThirdParty.GameMsg', 'GSNotify', None)"):
			return HttpResponse("error_rolecommamd")
		return HttpResponse("ok")


Permission.reg_develop(Req_GSNotify)
Permission.reg_develop(Res_GSNotify)
Permission.reg_public(GSNotify)