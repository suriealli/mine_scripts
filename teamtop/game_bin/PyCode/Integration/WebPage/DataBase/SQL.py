#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 直接运行SQL
#===============================================================================
from django.http import HttpResponse
from Integration import AutoHTML
from Integration.Help import Concurrent, WorldHelp
from Integration.WebPage.User import Permission
import datetime

def Req(request):
	'''
	【运行】--执行SQL
	'''
	return HttpResponse(html)

def Res(request):
	dbids = AutoHTML.AsDataBaseIDs(request.POST)
	start_time = AutoHTML.AsDateTime(request.POST, "start_time")
	end_time = AutoHTML.AsDateTime(request.POST, "end_time")
	tarea = AutoHTML.AsString(request.POST, "tarea")
	# 分析sql
	lis = tarea.split(";")
	if len(lis) != 2:
		return HttpResponse("SQL 必须有;")
	sql = lis[0]
	if lis[1]:
		merge_name = lis[1]
	else:
		merge_name = None
	# 并行查询
	tg = Concurrent.TaskGroup()
	tg.result_types = tuple
	for dbid in dbids:
		tg.append(Concurrent.DBTask(dbid, sql, start_time, end_time))
	tg.execute()
	# 获取结果
	kv = tg.results.items()
	# 按照dbid排序
	kv.sort(key=lambda it:it[0])
	# 不合并结果，一个个的显示
	if merge_name is None:
		head = []
		body = []
		for dbid, result in kv:
			for row in result:
				if not head:
					head.append("服信息-列名")
					head.extend(row.iterkeys())
				assert len(row) + 1 == len(head)
				table_row = [WorldHelp.GetFullNameByZoneID(dbid)]
				for idx in xrange(1, len(head)):
					table_row.append(row[head[idx]])
				body.append(table_row)
		if tg.is_all_ok():
			title = "全部执行成功"
		else:
			title = "请求：%s, 结果：%s" % (len(tg.tasks), len(kv))
		table = AutoHTML.Table(head, body, title)
		return HttpResponse(table.ToHtml())
	# 合并结果
	else:
		d = {}
		data_name = None
		for dbid, result in kv:
			for row in result:
				if len(row) != 2:
					return HttpResponse("结果必须是两列才能合并(或者是输入了一条SQL，但是有换行。。)")
				if merge_name not in row:
					return HttpResponse("没有找到合并的列(%s)-->" % merge_name + "返回的列名是(%s-%s)" % row.keys())
				if data_name is None:
					for name in row.iterkeys():
						if name == merge_name:
							continue
						data_name = name
						break
				merge_value = row[merge_name]
				data_value = row[data_name]
				if not isinstance(data_value, (int, long, float)):
					return HttpResponse("%s不支持加法运算" % data_value)
				d[merge_value] = d.get(merge_value, 0) + data_value
		if tg.is_all_ok():
			title = "全部执行成功"
		else:
			title = "请求：%s, 结果：%s" % (len(tg.tasks), len(kv))
		table = AutoHTML.Table([merge_name, data_name], d.items(), title)
		return HttpResponse(table.ToHtml())

html = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>执行SQL</title>
</head>
<body>
<form action="%s" method="POST" target="_blank">
%s<br>
从<input type='text' name='start_time' value="%s" style='width:300'/>到<input type='text' name='end_time' value="%s" style='width:300'/><br>
格式化参数：suff;如果开始时间==结束时间则查询数据表，否则查询日志表
%s<br>
<input type="submit" name="提交" />
</form>
</body>
</html>''' % (AutoHTML.GetURL(Res), AutoHTML.ToDataBase(),
			datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
			datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
			AutoHTML.ToTextarea())

Permission.reg_develop(Req)
Permission.reg_develop(Res)
Permission.reg_log(Res)
