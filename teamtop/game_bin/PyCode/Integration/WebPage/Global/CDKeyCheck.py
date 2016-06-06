#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.Global.CDKeyCheck")
#===============================================================================
# CDKEY查询，运营使用
#===============================================================================
from django.http import HttpResponse
from Integration import AutoHTML
from Integration.WebPage.User import Permission
from Game.CDKey import CDKey
from ComplexServer.Plug.DB import DBHelp

SQL = "select count(*) from cdkey_%s where role_id > 0 and cdkey in %s;"
SQL_One = "select count(*) from cdkey_%s where role_id > 0 and cdkey = '%s';"

SQL_Detail = "select role_id from cdkey_%s where role_id > 0 and cdkey = '%s';"

def Req_Test(request):
	'''
	【数据与工具】--查询CDKEY使用情况
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
		newSql = SQL_One % (config.special, cdkeyList[0])
	else:
		newSql = SQL % (config.special, str(tuple(cdkeyList)))
	
	gd = AutoHTML.Table(["cdkey类型", "已经使用数量", "剩余使用数量",], [], "数据")
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		cur.execute(newSql)
		result = cur.fetchall()
		if result:
			useCount = result[0][0]
			gd.body.append((config.name, useCount, totalCount - useCount))
		return HttpResponse(gd.ToHtml())
	

html_test = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>查询CDKEY使用情况</title>
</head>
<body>
<form action="%s" method="POST" target="_blank">
<p>请输入CDKEY，数量不要超过1万条, 一次只能输入一个类型的CDKEY</p>
%s
<input type="submit" name="提交" />
</form>
</body>
</html>''' % (AutoHTML.GetURL(Res_Test), AutoHTML.ToTextarea(h = "600"))


def Req_CDKeyDetail(request):
	'''
	【数据与工具】--查询CDKEY使用详细情况
	'''
	cdkey =  AutoHTML.AsString(request.GET, "cdkey")
	roleId = "未使用"
	if cdkey:
		config = CDKey.GetConfig(cdkey)
		if config:
			sp = CDKey.GetSpecialStr(cdkey)
			con = DBHelp.ConnectGlobalWeb()
			sql = SQL_Detail % (config.special, cdkey)
			with con as cur:
				cur.execute(sql)
				result = cur.fetchall()
				if result:
					roleId = result[0][0]
		else:
			roleId = "没有这类型的CDKEY配置"
	result = ""
	if cdkey:
		result = "CDKEY : %s   --> : %s" % (cdkey, roleId)
	html = '''
	<html>
	<head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
	<title>查询CDKEY使用详细情况</title>
	</head>
	<body>
	<form action="%s" method="GET">
	CDKEY：<input type="text" name="cdkey" style="width:200; "><br>
	<p></p>
	<input type="submit" value="查询" />
	<p> %s </p>
	</form>
	</body>
	</html>''' % (AutoHTML.GetURL(Req_CDKeyDetail), result)
	
	return HttpResponse(html)



Permission.reg_design(Req_CDKeyDetail)
Permission.reg_design(Req_Test)
Permission.reg_design(Res_Test)