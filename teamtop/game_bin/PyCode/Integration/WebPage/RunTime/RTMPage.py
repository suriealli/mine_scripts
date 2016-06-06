#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 运行时重载模块
#===============================================================================
from django.http import HttpResponse
from Integration import AutoHTML
from Integration.Help import Concurrent, WorldHelp
from Integration.WebPage.User import Permission

def Req(request):
	'''
	【运行】--重载脚本
	'''
	return HttpResponse(html)

def Res(request):
	pkeys = AutoHTML.AsProcessKeys(request.POST)
	reloads = AutoHTML.AsStrings(request.POST)
	commands = []
	for s in reloads:
		if s.startswith("XRLAM") or s.startswith("DisableFunction"):
			commands.append(s)
		else:
			return HttpResponse("非法指令，只能重载脚本和禁用函数！")
	
	gt = Concurrent.TaskGroup()
	for pkey in pkeys:
		gt.append(Concurrent.GMTask(pkey, "\n".join(commands)))
	gt.execute()
	return HttpResponse(gt.to_html(WorldHelp.GetFullNameByProcessKey, WorldHelp.CmpProcessKey))

html = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>重载脚本</title>
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

Permission.reg_develop(Req)
Permission.reg_develop(Res)
Permission.reg_log(Res)

