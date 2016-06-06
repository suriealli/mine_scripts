#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.RunTime.RTBPage")
#===============================================================================
# 查看大表
#===============================================================================
from django.http import HttpResponse
from Game.Persistence import BigTable
from Integration import AutoHTML
from Integration.Help import Concurrent, WorldHelp
from Integration.WebPage.User import Permission

def Req(request):
	'''
	【运行】--查询BigTable数据
	'''
	return HttpResponse(html)

C1 = '''from ThirdLib import PrintHelp
from Game.Persistence import BigTable
PrintHelp.pprint(BigTable.ALL_TABLES["%s"].datas.get(%s))
'''
C2 = '''from ThirdLib import PrintHelp
from Game.Persistence import BigTable
print "len is", len(BigTable.ALL_TABLES["%s"].datas.keys())
PrintHelp.pprint(BigTable.ALL_TABLES["%s"].datas.keys())
'''

def Res(request):
	pkeys = AutoHTML.AsProcessKeys(request.POST)
	varname =  sel.GetValue(request.POST)
	key = AutoHTML.AsInt(request.POST, "bigtablekey")
	if key:
		command = C1 % (varname, key)
	else:
		command = C2 % (varname, varname)
	
	tg = Concurrent.TaskGroup()
	for pkey in pkeys:
		tg.append(Concurrent.GMTask(pkey, command))
	tg.execute()
	return HttpResponse(tg.to_html(WorldHelp.GetFullNameByProcessKey, WorldHelp.CmpProcessKey))


sel = AutoHTML.Select()
for key in BigTable.ALL_TABLES.iterkeys():
	sel.Append("BigTable-%s" % key, key)
html = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>查看BigTable数据</title>
</head>
<body>
<form action="%s" method="POST" target="_blank">
%s
<br><br>
%s
<p>不填写下面的key则查询这个bigtable的所有的key</p>
指定key：<input type="text" name="bigtablekey">
<br><br>
<input type="submit" name="提交" />
</form>
</body>
</html>''' % (AutoHTML.GetURL(Res), AutoHTML.ToProcess(), sel.ToHtml())


Permission.reg_develop(Req)
Permission.reg_develop(Res)