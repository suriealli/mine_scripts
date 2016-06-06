#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.RunTimeTest.RTDTestPage")
#===============================================================================
# 注释
#===============================================================================
from django.http import HttpResponse
from Integration import AutoHTML
from Integration.Help import Concurrent, WorldHelp
from Integration.WebPage.User import Permission
from World import Define


def Req_Test(request):
	'''
	【测试】--模拟服GM指令
	'''
	return HttpResponse(html_test)

def Res_Test(request):
	pkeys = AutoHTML.AsProcessKeys(request.POST)
	command = AutoHTML.AsString(request.POST, "tarea")
	tg = Concurrent.TaskGroup()
	pc = WorldHelp.GetProcess()
	for pkey in pkeys:
		pcobj = pc.get(pkey)
		if not pcobj:
			continue
		if pcobj.pid not in Define.TestWorldIDs:
			continue
		tg.append(Concurrent.GMTask(pkey, command))
	tg.execute()
	return HttpResponse(tg.to_html(WorldHelp.GetFullNameByProcessKey, WorldHelp.CmpProcessKey))

html_test = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>模拟服GM指令</title>
</head>
<body>
<form action="%s" method="POST" target="_blank">
%s
<br><br>
%s
<input type="submit" name="提交" />
</form>
</body>
</html>''' % (AutoHTML.GetURL(Res_Test), AutoHTML.ToProcessTest(), AutoHTML.ToTextarea())


Permission.reg_design(Req_Test)
Permission.reg_design(Res_Test)