#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 角色备份
#===============================================================================
from Tool import SaveVIP
from ComplexServer.Plug.DB import DBHelp
from Integration import AutoHTML
from Integration.WebPage.User import Permission
from django.http import HttpResponse

def Req(request):
	'''【数据与工具】--角色备份'''
	return HttpResponse(html)

def Res(request):
	param = AutoHTML.AsString(request.POST, "param")
	fun = sel.GetValue(request.POST)
	return fun(param)

def ShowBack(param):
	role_id = int(param)
	table = AutoHTML.Table(["备份点", "备份时间"])
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		cur.execute("select bid, back_time from role_back where role_id = %s;" % role_id)
		for bid, back_time in cur.fetchall():
			table.body.append((bid, back_time))
	return HttpResponse(table.ToHtml())
	
def DoBack(param):
	role_id = int(param)
	SaveVIP.SaveOneRole(role_id)
	return HttpResponse("OK")

def DoRevert(bid):
	SaveVIP.Revert(bid)
	return HttpResponse("OK")

sel = AutoHTML.Select()
sel.Append("查看备份点", ShowBack)
sel.Append("备份", DoBack)
sel.Append("还原", DoRevert)

html = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>角色备份</title>
</head>
<body>
<form action="%s" method="POST" target="_blank">
<table border='1px' cellspacing='0px' style='border-collapse:collapse'>
<tr><td>操作</td><td>%s</td></tr>
<tr><td>参数</td><td><input type="text" name="param"></td></tr>
</table>
<input type="submit" name="提交" />
</form>
</body>
</html>''' % (AutoHTML.GetURL(Res), sel.ToHtml())


Permission.reg_develop(Req)
Permission.reg_develop(Res)

