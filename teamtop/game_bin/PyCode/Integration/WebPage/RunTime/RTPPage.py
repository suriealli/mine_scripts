#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 运行时进程状态
#===============================================================================
from Integration import AutoHTML
from django.http import HttpResponse
from Integration.Help import Concurrent, WorldHelp
from Integration.WebPage.User import Permission

def Req(request):
	'''
	【运维】--进程状态
	'''
	return HttpResponse(HTTP_SHOW_PROCESS)

def Res(request):
	pkeys = AutoHTML.AsProcessKeys(request.POST)
	sel = SEL.GetValue(request.POST)
	only_error = AutoHTML.AsBool(request.POST, "only_error")
	valueFun = None
	if sel == "ping":
		command = "print 1"
		if only_error: valueFun = lambda v: True if v == "1\n" else v
	elif sel == "match":
		command = "MD5()"
		if only_error: valueFun = lambda v: True if v == "(True, True, True)\n" else v
	elif sel == "checkdata":
		command = "CheckDataLoadDB()"
		if only_error: valueFun = lambda v: True if v == "(True, True)\n" else v
	elif sel == "isopen":
		command = "IsOpen()"
		if only_error: valueFun = lambda v: True if v == "True\n" else v
	else:
		return HttpResponse("未知命令%s" % sel)
	
	tg = Concurrent.TaskGroup()
	for pkey in pkeys:
		tg.append(Concurrent.GMTask(pkey, command))
	tg.execute()
	return HttpResponse(tg.to_html(WorldHelp.GetFullNameByProcessKey, WorldHelp.CmpProcessKey, valueFun))

SEL = AutoHTML.Select()
SEL.Append("是否正常工作", "ping")
SEL.Append("是否可以开放普通号", "checkdata")
SEL.Append("文件是否同步", "match")
SEL.Append("是否已经开放了", "isopen")
HTTP_SHOW_PROCESS = '''<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>进程状态</title>
</head>
<body>
<form action="%s" method="POST" target="_blank">
%s
<br>
只显示有问题的结果<input type="checkbox" name="only_error" value="only_error">
<br>
%s
<input type="submit" name="提交" />
</form>
</body>
</html>''' % (AutoHTML.GetURL(Res), AutoHTML.ToProcess(), SEL.ToHtml())




def ReqProcess(request):
	'''
	【运维】--进程关闭
	'''
	return HttpResponse(HTTP_PROCESS)

def ResProcess(request):
	pkeys = AutoHTML.AsProcessKeys(request.POST)
	confirm = AutoHTML.AsString(request.POST, "confirm")
	if confirm != "Yes123456789":
		return HttpResponse("确认码错误:%s" % confirm)
	only_error = AutoHTML.AsBool(request.POST, "only_error")
	valueFun = None
	command = "Kill()"
	if only_error: valueFun = lambda v: True if v == "kill...\n" else v
	tg = Concurrent.TaskGroup()
	for pkey in pkeys:
		tg.append(Concurrent.GMTask(pkey, command))
	tg.execute()
	return HttpResponse(tg.to_html(WorldHelp.GetFullNameByProcessKey, WorldHelp.CmpProcessKey, valueFun))


HTTP_PROCESS = '''<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>服务器管理</title>
</head>
<body>
<form action="%s" method="POST" target="_blank">
%s
<br>
只显示有问题的结果<input type="checkbox" name="only_error" value="only_error">
<br>
请确认是否关闭：<input type="text" name="confirm">
<input type="submit" name="关闭" />
</form>
</body>
</html>''' % (AutoHTML.GetURL(ResProcess), AutoHTML.ToProcess())


Permission.reg_develop(ReqProcess)
Permission.reg_develop(ResProcess)
Permission.reg_log(ResProcess)

Permission.reg_develop(Req)
Permission.reg_develop(Res)
Permission.reg_log(Res)

