#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 显示任务
#===============================================================================
import sys
import datetime
from ComplexServer.Plug.DB import DBHelp
from Integration import AutoHTML
from django.http import HttpResponse
from Integration.WebPage.User import Permission

datetime

html_list = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>任务列表</title>
</head>
<body>
%s
</body>
</html>'''

def Req(request):
	'''【数据与工具】--任务系统'''
	taskid = AutoHTML.AsInt(request.GET, "taskid")
	table = AutoHTML.Table(["详情", "删除", "总共", "完成", "任务ID", "任务名", "说明", "参数"], [], "任务列表") 
	con = DBHelp.ConnectHouTaiWeb()
	with con as cur:
		if taskid:
			cur.execute("delete from task where total = finish and tid < %s;" % taskid)
		cur.execute("select tid, name, instruction, argv, total, finish from task order by tid desc;")
		for tid, name, instruction, argv, total, finish in cur.fetchall():
			show = "<a href='/Tool/ShowTask/ShowTask/?tid=%s'>查看</a>" % tid
			delete = "<a href='/Tool/ShowTask/DelTask/?tid=%s'>删除</a>" % tid
			argv = eval(argv)
			table.body.append((show, delete, total, finish, tid, name, instruction, AutoHTML.PyObjToHtml(argv)))
	return HttpResponse(html_list % table.ToHtml())

html_detail = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>任务详情</title>
</head>
<body>
<table><tr><td valign="top">%s</td></tr>
<tr><td valign="top">%s</td></tr>
</table><br>
%s<br>
%s<br>
</body>
</html>'''

def ShowTask(request):
	tid = AutoHTML.AsInt(request.GET, "tid")
	rows = []
	con = DBHelp.ConnectHouTaiWeb()
	with con as cur:
		cur.execute("select cls, name, instruction, argv, total, finish from task where tid = %s;" % tid)
		line = cur.fetchall()[0]
		rows.append(("任务ID", tid))
		rows.append(("任务逻辑", line[0]))
		rows.append(("任务名", line[1]))
		rows.append(("说明", line[2]))
		rows.append(("参数", AutoHTML.PyObjToHtml(eval(line[3]))))
		rows.append(("总共", line[4]))
		rows.append(("完成", line[5]))
	# 如果完成了，显示最终结果
	if line[4] <= line[5]:
		module_name, cls_name = eval(line[0])
		__import__(module_name)
		module = sys.modules[module_name]
		cls = getattr(module, cls_name)
		obj = cls(tid)
		obj.do_task()
		chirld = ""
		error = obj.get_task_error()
		result = obj.get_task_result()
	else:
		cur.execute("select ctid, cname, mutex, process, work_state, start_time from ctask where tid = %s;" % tid)
		table = AutoHTML.Table(["子任务ID", "子任务名", "互斥关系", "处理进程信息", "工作状态", "开始时间", "重置"], [], "子任务情况")
		for ctid, cname, mutex, process, work_state, start_time in cur.fetchall():
			reset = "<a href = '/Tool/ShowTask/Reset/?tid=%s&ctid=%s' target='_blank'>重置</a>" % (tid, ctid)
			table.body.append((ctid, cname, mutex, process, work_state, start_time, reset))
		chirld = table.ToHtml()
		error = ""
		result = ""
	return HttpResponse(html_detail % (AutoHTML.MakeTable(rows), chirld, error, result))

def DelTask(request):
	tid = AutoHTML.AsInt(request.GET, "tid")
	con = DBHelp.ConnectHouTaiWeb()
	with con as cur:
		cur.execute("delete from task where tid = %s;" % tid)
		cur.execute("delete from ctask where tid = %s;" % tid)
	return Req(request)

def Reset(request):
	tid = AutoHTML.AsInt(request.GET, "tid")
	ctid = AutoHTML.AsInt(request.GET, "ctid")
	con = DBHelp.ConnectHouTaiWeb()
	with con as cur:
		h =cur.execute("update ctask set result = NULL, work_state = '', process = '' where tid = %s and ctid = %s;" % (tid, ctid))
		return HttpResponse(h)

Permission.reg_design(Req)
Permission.reg_design(ShowTask)
Permission.reg_design(DelTask)
Permission.reg_design(Reset)
