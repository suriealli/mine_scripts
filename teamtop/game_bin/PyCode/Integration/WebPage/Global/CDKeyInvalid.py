#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.Global.CDKeyInvalid")
#===============================================================================
# 注释
#===============================================================================
from django.http import HttpResponse
from Integration import AutoHTML
from Integration.WebPage.User import Permission
from Game.CDKey import CDKey
from ComplexServer.Plug.DB import DBHelp

SQL = "Update cdkey_%s set role_id = 1  where role_id = 0 and cdkey in %s;"
SQL_ONE = "Update cdkey_%s set role_id = 1  where role_id = 0 and cdkey = '%s';"

def Req_Test(request):
	'''
	【数据与工具】--作废CDKEY
	'''
	return HttpResponse(html_test)



def Res_Test(request):
	cdkeyList = AutoHTML.AsStrings(request.POST, "tarea")
	if len(cdkeyList) < 1:
		return HttpResponse(html_test)
	
	config = CDKey.GetConfig(cdkeyList[0])
	if not config:
		return HttpResponse("查询不到这类型的CDKEY")
	sp = CDKey.GetSpecialStr(cdkeyList[0])
	for cdkey in cdkeyList:
		if not cdkey.startswith(sp):
			return HttpResponse("一次只能操作一个类型的cdkey")
	totalCount = len(cdkeyList)
	if totalCount == 1:
		newSql = SQL_ONE % (config.special, cdkeyList[0])
	else:
		newSql = SQL % (config.special, str(tuple(cdkeyList)))
	gd = AutoHTML.Table(["cdkey类型", "输入总量", "当前操作作废数量",], [], "当前输入CDKEY已经全部作废")
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		invalidCount = cur.execute(newSql)
		gd.body.append((config.name, totalCount, invalidCount))
		return HttpResponse(gd.ToHtml())
	

html_test = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>作废CDKEY</title>
</head>
<body>
<form action="%s" method="POST" target="_blank">
<p>请输入CDKEY，数量不要超过1万条, 一次只能输入一个类型的CDKEY</p>
%s
<input type="submit" name="提交" />
</form>
</body>
</html>''' % (AutoHTML.GetURL(Res_Test), AutoHTML.ToTextarea(h = "600"))


Permission.reg_design(Req_Test)
Permission.reg_design(Res_Test)