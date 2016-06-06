#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 角色信息
#===============================================================================
from Integration import AutoHTML
from django.http import HttpResponse
from ComplexServer.Plug.DB import DBHelp
from Integration.Help import WorldHelp
from Integration.WebPage.User import Permission

def Req(request):
	'''【工具】--角色信息'''
	return HttpResponse(html)

def Res(request):
	role_id = AutoHTML.AsInt(request.POST, "role_id")
	role_name = AutoHTML.AsString(request.POST, "role_name")
	account = AutoHTML.AsString(request.POST, "account")
	dbids = AutoHTML.AsDataBaseIDs(request.POST)
	
	body = []
	if role_id:
		con = DBHelp.ConnectMasterDBRoleID(role_id)
		with con as cur:
			cur.execute("select role_id, role_name, account, di32_3, di32_4, di32_6, di32_11, di32_12, di32_13, di32_14 from role_data where role_id = %s;", role_id)
			for role_id, role_name, account, di32_3, di32_4, di32_6, di32_11, di32_12, di32_13, di32_14 in cur.fetchall():
				body.append((WorldHelp.GetFullNameByRoleID(role_id), role_id, role_name, account, di32_3, di32_4, di32_6, di32_11, di32_12, di32_13, di32_14))
	elif role_name:
		for dbid in dbids:
			con = DBHelp.ConnectMasterDBByID(dbid)
			with con as cur:
				cur.execute("select role_id, role_name, account, di32_3, di32_4, di32_6, di32_11, di32_12, di32_13, di32_14 from role_data where role_name like %s;", role_name)
				for role_id, role_name, account, di32_3, di32_4, di32_6, di32_11, di32_12, di32_13, di32_14 in cur.fetchall():
					body.append((WorldHelp.GetFullNameByZoneID(dbid), role_id, role_name, account, di32_3, di32_4, di32_6, di32_11, di32_12, di32_13, di32_14))
	elif account:
		for dbid in dbids:
			con = DBHelp.ConnectMasterDBByID(dbid)
			with con as cur:
				cur.execute("select role_id, role_name, account, di32_3, di32_4, di32_6, di32_11, di32_12, di32_13, di32_14 from role_data where account = %s;", account)
				for role_id, role_name, account, di32_3, di32_4, di32_6, di32_11, di32_12, di32_13, di32_14 in cur.fetchall():
					body.append((WorldHelp.GetFullNameByZoneID(dbid), role_id, role_name, account, di32_3, di32_4, di32_6, di32_11, di32_12, di32_13, di32_14))
	
	table = AutoHTML.Table(["区", "角色ID", "角色名", "帐号", "封号", "禁言", "消费Q点", "等级", "VIP", "非绑定RMB", "绑定RMB"], body)
	return HttpResponse(table.ToHtml())

html = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>角色信息</title>
</head>
<body>
<form action="%s" method="POST" target="_blank">
%s<br>
<table border='1px' cellspacing='0px' style='border-collapse:collapse'>
<tr><td>角色ID</td><td><input type="text" name="role_id"></td></tr>
<tr><td>角色名</td><td><input type="text" name="role_name"></td></tr>
<tr><td>帐号</td><td><input type="text" name="account"></td></tr>
</table>
<input type="submit" name="查询" />
</form>
</body>
</html>''' % (AutoHTML.GetURL(Res), AutoHTML.ToDataBase())

Permission.group([Req,Res],['design','operate'])

