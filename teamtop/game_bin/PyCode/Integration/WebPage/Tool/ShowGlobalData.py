#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.Tool.ShowGlobalData")
#===============================================================================
# 查询全局数据
#===============================================================================
from django.http import HttpResponse
from ComplexServer.Plug.DB import DBHelp
from Integration import AutoHTML
from Integration.WebPage.User import Permission
from Common.Other import GlobalDataDefine
from Integration.Help import OtherHelp


html = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>全局数据(正式服)</title>
</head>
<body>
%s<br>
</body>
</html>'''


html_test = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>全局数据(测试服)</title>
</head>
<body>
%s<br>
</body>
</html>'''

def ShowG(request):
	'''【运行】--查询全局数据(正式服)'''
	gd = AutoHTML.Table(["全局数据Key", "名称","值", "修改时间"], [], "全局数据")
	con = DBHelp.ConnectGlobalWeb()
	definedict = OtherHelp.GetMoudleDefineZS(GlobalDataDefine)
	dataList = []
	with con as cur:
		cur.execute("select global_data_key, data, save_datetime from global_data ;")
		result = cur.fetchall()
		if result:
			for global_data_key, data, save_datetime in result:
				if "_testworld" in global_data_key:
					continue
				if data:
					data = eval(data)
				
				dataList.append((global_data_key, AutoHTML.PyObjToHtml(data), save_datetime))
				
			dataList.sort(key = lambda it:it[0])
		
		for ld in dataList:
			gkey = ld[0]
			gd.body.append((gkey, definedict.get(int(gkey), gkey), ld[1], ld[2]))
		return HttpResponse(html % gd.ToHtml())

def ShowG_test(request):
	'''【测试】--查询全局数据(模拟服)'''
	gd = AutoHTML.Table(["全局数据Key", "名称", "值", "修改时间"], [], "全局数据")
	con = DBHelp.ConnectGlobalWeb()
	definedict = OtherHelp.GetMoudleDefineZS(GlobalDataDefine)
	dataList = []
	with con as cur:
		cur.execute("select global_data_key, data, save_datetime from global_data ;")
		result = cur.fetchall()
		if result:
			for global_data_key, data, save_datetime in result:
				if "_testworld" not in global_data_key:
					continue
				if data:
					data = eval(data)
			
				gkey = int(global_data_key[:global_data_key.find('_')])
				
				dataList.append((gkey, AutoHTML.PyObjToHtml(data), save_datetime))
				
		dataList.sort(key = lambda it:it[0])
		
		for ld in dataList:
			gkey = ld[0]
			gd.body.append((gkey, definedict.get(gkey, gkey), ld[1], ld[2]))
		return HttpResponse(html_test % gd.ToHtml())


Permission.reg_develop(ShowG)
Permission.reg_design(ShowG_test)
