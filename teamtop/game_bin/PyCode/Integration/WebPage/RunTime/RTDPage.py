#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 运行时做
#===============================================================================
from django.http import HttpResponse
from Integration import AutoHTML
from Integration.Help import Concurrent, WorldHelp
from Integration.WebPage.User import Permission


def ReqRefresh(request):
	'''
	【运行】--刷新区缓存
	'''
	AutoHTML.RefreshProcessCache()
	
	return HttpResponse("Refresh Ok")

def Req(request):
	'''
	【运行】--GM指令
	'''
	return HttpResponse(html)

def Res(request):
	pkeys = AutoHTML.AsProcessKeys(request.POST)
	command = AutoHTML.AsString(request.POST, "tarea")
	tg = Concurrent.TaskGroup()
	for pkey in pkeys:
		tg.append(Concurrent.GMTask(pkey, command))
	tg.execute()
	return HttpResponse(tg.to_html(WorldHelp.GetFullNameByProcessKey, WorldHelp.CmpProcessKey))

html = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>GM指令</title>
</head>
<body>
<form action="%s" method="POST" target="_blank">
%s
<br><br>
%s
<input type="submit" name="提交" />
</form>
</body>
</html>''' % (AutoHTML.GetURL(Res), AutoHTML.ToProcess(), AutoHTML.ToTextarea())


Permission.reg_develop(ReqRefresh)
Permission.reg_develop(Req)
Permission.reg_develop(Res)
Permission.reg_log(Res)

