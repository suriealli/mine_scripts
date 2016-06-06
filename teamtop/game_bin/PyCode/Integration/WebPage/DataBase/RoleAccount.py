#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 角色帐号
#===============================================================================
from django.http import HttpResponse
from Util import OutBuf
from World import Define
from ComplexServer.Plug.DB import DBHelp
from Integration import AutoHTML
from Integration.Help import OtherHelp
from Integration.WebPage.User import Permission
from Integration.WebPage.DataBase import RoleData
import Environment

def Del(request):
	'''【测试】--模拟服角色删除'''
	role_id = AutoHTML.AsInt(request.POST, "roleid")
	if not role_id:
		return HttpResponse(html_del)
	if DBHelp.GetDBIDByRoleID(role_id) not in Define.TestWorldIDs:
		return HttpResponse("只能删除测试服的角色啊！！！")
	con = DBHelp.ConnectMasterDBRoleID(role_id)
	with con as cur:
		h = cur.execute("update role_data set account = %s where role_id = %s;", (str(role_id), role_id))
		cur.close()
		return HttpResponse(str(h))

html_del = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>角色删除</title>
</head>
<body>
<form action="%s" method="POST" target="_blank">
角色ID：<input type="text" name="roleid"><br>
<input type="submit" name="删除" />
</form>
</body>
</html>''' % (AutoHTML.GetURL(Del), )


def Import(request):
	'''【测试】--模拟服角色导入'''
	import BuildRole
	import datetime
	datetime
	roleid = AutoHTML.AsInt(request.POST, "roleid")
	dbid = AutoHTML.AsInt(request.POST, "dbid")
	account = AutoHTML.AsString(request.POST, "account")
	if not roleid:
		return HttpResponse(html_import)
	if dbid not in Define.TestWorldIDs:
		return HttpResponse("只能导入模拟服！")
	with OutBuf.OutBuf_NoExcept() as out:
		role_info = RoleData.ExportRole(OtherHelp.Request(request.POST))
		role_info = eval(role_info.content)
		BuildRole.RealImportRole(role_info, dbid, account)
		return HttpResponse(out.get_value())


def Import_Develop(request):
	'''【测试】--角色导入到内网'''
	import BuildRole
	import datetime
	datetime
	roleid = AutoHTML.AsInt(request.POST, "roleid")
	dbid = AutoHTML.AsInt(request.POST, "dbid")
	account = AutoHTML.AsString(request.POST, "account")
	pf = AutoHTML.AsString(request.POST, "pf")
	if not roleid:
		return HttpResponse(html_import_develop)
	if not Environment.IsDevelop:
		return HttpResponse("只能内网使用")
	if dbid not in Define.TestWorldIDs:
		return HttpResponse("只能导入模拟服！")
	with OutBuf.OutBuf_NoExcept() as out:
		#role_info = RoleData.ExportRole(OtherHelp.Request(request.POST))
		#role_info = eval(role_info.content)
		#BuildRole.RealImportRole(role_info, dbid, account)
		BuildRole.ImportRole(roleid, dbid, account, pf)
		return HttpResponse(out.get_value())
	


html_import = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>角色导入</title>
</head>
<body>
<form  action="%s" method="post" target="_blank">
<table>
<tr><td>源角色ID</td><td><input type="text" name="roleid"></td></tr>
<tr><td>目标服</td><td><input type="text" name="dbid" value="2"></td></tr>
<tr><td>目标帐号</td><td><input type="text" name="account"></td></tr>
</table>
<input type="submit" value="导入">
</form>
</body>
</html>''' % (AutoHTML.GetURL(Import), )



html_import_develop = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>角色导入内网</title>
</head>
<body>
<form  action="%s" method="post" target="_blank">
<table>
<tr><td>源角色ID</td><td><input type="text" name="roleid"></td></tr>
<tr><td>角色所属平台(qq,qu,ft,na)</td><td><input type="text" name="pf"></td></tr>
<tr><td>目标服</td><td><input type="text" name="dbid" value="2"></td></tr>
<tr><td>目标帐号</td><td><input type="text" name="account"></td></tr>
</table>
<input type="submit" value="导入">
</form>
</body>
</html>''' % (AutoHTML.GetURL(Import_Develop), )



Permission.reg_public(Del)
Permission.reg_public(Import)
Permission.reg_public(Import_Develop)

