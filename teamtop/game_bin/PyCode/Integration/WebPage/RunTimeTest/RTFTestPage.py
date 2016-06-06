#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.RunTimeTest.RTFTestPage")
#===============================================================================
# 注释
#===============================================================================
import inspect
from django.http import HttpResponse
from Game import RTF
from Integration import AutoHTML
from Integration.Help import Concurrent, WorldHelp
from Integration.WebPage.User import Permission
from World import Define

def Req(request):
	'''
	【测试】--模拟服调用函数
	'''
	return HttpResponse(html)

def Res(request):
	pkeys = AutoHTML.AsProcessKeys(request.POST)
	commands = ["from Game import RTF"]
	for key in RTF.RTF_FUN.iterkeys():
		value = AutoHTML.AsString(request.POST, key)
		if value == '@':
			continue
		commands.append("RTF.CallFunction('%s', (%s,))" % (key, value))
	
	tg = Concurrent.TaskGroup()
	pc = WorldHelp.GetProcess()
	for pkey in pkeys:
		pcobj = pc.get(pkey)
		if not pcobj:
			continue
		if pcobj.pid not in Define.TestWorldIDs:
			continue
		tg.append(Concurrent.GMTask(pkey, "\n".join(commands)))
	tg.execute()
	return HttpResponse(tg.to_html(WorldHelp.GetFullNameByProcessKey, WorldHelp.CmpProcessKey))

tb = AutoHTML.Table(["函数", "说明", "默认参数"])
for key, fun in  RTF.RTF_FUN.iteritems():
	args, _, _, defual = inspect.getargspec(fun)
	tb.body.append(("%s(%s)<br><input type='text' name='%s' value='@' size='100'>" % (key, ", ".join(args), key), fun.__doc__.replace("@", "<br>"), str(defual)))
html = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>调用函数</title>
</head>
<body>
<form  action="%s" method="POST" target="_blank">
%s
<br>
%s
<input type="submit" name="提交" />
</form>
</body>
</html>''' % (AutoHTML.GetURL(Res), AutoHTML.ToProcessTest(), tb.ToHtml())
del tb

Permission.reg_design(Req)
Permission.reg_design(Res)
