#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 运行时调用函数
#===============================================================================
import inspect
from django.http import HttpResponse
from Game import RTF
from Integration import AutoHTML
from Integration.Help import Concurrent, WorldHelp
from Integration.WebPage.User import Permission

def Req(request):
	'''
	【运行】--调用函数
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
	for pkey in pkeys:
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
</html>''' % (AutoHTML.GetURL(Res), AutoHTML.ToProcess(), tb.ToHtml())
del tb


def ReqB(request):
	'''
	【运维】--新服管理
	'''
	return HttpResponse(html2)

def ResB(request):
	pkeys = AutoHTML.AsProcessKeys(request.POST)
	commands = ["from Game import RTF"]
	for key in RTF.RTF_BACK_FUN.iterkeys():
		value = AutoHTML.AsString(request.POST, key)
		if value == '@':
			continue
		commands.append("RTF.CallFunctionBack('%s', (%s,))" % (key, value))
	
	tg = Concurrent.TaskGroup()
	for pkey in pkeys:
		tg.append(Concurrent.GMTask(pkey, "\n".join(commands)))
	tg.execute()
	return HttpResponse(tg.to_html(WorldHelp.GetFullNameByProcessKey, WorldHelp.CmpProcessKey))

tbB = AutoHTML.Table(["函数", "说明", "默认参数"])
for key, fun in  RTF.RTF_BACK_FUN.iteritems():
	args, _, _, defual = inspect.getargspec(fun)
	tbB.body.append(("%s(%s)<br><input type='text' name='%s' value='@' size='100'>" % (key, ", ".join(args), key), fun.__doc__.replace("@", "<br>"), str(defual)))
html2 = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>新服管理</title>
</head>
<body>
<form  action="%s" method="POST" target="_blank">
%s
<br>
%s
<input type="submit" name="提交" />
</form>
</body>
</html>''' % (AutoHTML.GetURL(ResB), AutoHTML.ToProcess(), tbB.ToHtml())
del tbB




Permission.reg_develop(ReqB)
Permission.reg_develop(ResB)
Permission.reg_log(ResB)

Permission.reg_develop(Req)
Permission.reg_develop(Res)
Permission.reg_log(Res)

