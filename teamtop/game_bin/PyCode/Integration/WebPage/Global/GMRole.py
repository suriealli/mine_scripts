#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.Global.GMRole")
#===============================================================================
# 内部号记录
#===============================================================================
import Environment
from django.http import HttpResponse
from Integration.Help import OtherHelp
from Integration import AutoHTML
from World import Define
from ComplexServer.Plug.DB import DBHelp
from Integration.WebPage.User import Permission


PW = "@LYLQS*3000W+"
def Req(request):
	'''【数据与工具】--查询内部数据'''
	return HttpResponse(html)

def ShowGM(request):
	password = AutoHTML.AsString(request.GET, "password")
	if PW != password:
		return HttpResponse("password error")
	gd = AutoHTML.Table(["进程ID", "角色帐号","角色ID", "角色名", "角色等级", "vip等级", "Q点",  "最后一次时间"], [], "内部数据")
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		cur.execute("select pid, account, role_id, role_name, level, viplevel, qp, save_datetime from gm_role;")
		result = cur.fetchall()
		if result:
			gd.body = list(result)
			gd.body.sort(key = lambda it:(it[0], it[6], it[4]), reverse = True)
		return HttpResponse(gd.ToHtml())

html = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>内部数据</title>
</head>
<body>
<form action="%s" method="GET" target="_blank">
密码：<input type="text" name="password"><br>
<input type="submit" name="查询" />
</form>
</body>
</html>''' % (AutoHTML.GetURL(ShowGM), )



def GMRole(request):
	return OtherHelp.Apply(_GMRole, request, __name__)
	
def _GMRole(request):
	roleid = AutoHTML.AsInt(request.POST, "roleid")
	account = AutoHTML.AsString(request.POST, "account")
	name = AutoHTML.AsString(request.POST, "name")
	level = AutoHTML.AsInt(request.POST, "level")
	process_id = AutoHTML.AsInt(request.POST, "pid")
	viplevel = AutoHTML.AsInt(request.POST, "viplevel")
	qp = AutoHTML.AsInt(request.POST, "qp")
	if Environment.IsDevelop:
		return
	else:
		if process_id in Define.TestWorldIDs:
			return
	
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		h = cur.execute("replace into gm_role (role_id, account, role_name, pid, level, viplevel, qp, save_datetime) values(%s, %s, %s, %s, %s, %s, %s, now());", (roleid, account, name, process_id, level, viplevel, qp))
	con.close()
	return h

Permission.reg_public(GMRole)
Permission.reg_public(_GMRole)
Permission.reg_develop(Req)
Permission.reg_develop(ShowGM)

