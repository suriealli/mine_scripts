#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 在某个事情附近做了啥
#===============================================================================
import datetime
import Environment
from Util import Time
from ComplexServer.Plug.DB import DBHelp
from Integration import AutoHTML
from Integration.Help import WebTask, WorldHelp, ConfigHelp
from Integration.WebPage.User import Permission
from django.http import HttpResponse

html = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>行为统计</title>
</head>
<body>
<form  action="%s" method="post" target="_blank">
%s<br>
名称<input type="text" name="tname" value=""  style='width:300'><br>
描述<input type="text" name="instruction" value=""  style='width:600'><br>
从<input type='text' name='start_time' value="%s" style='width:300'/>到<input type='text' name='end_time' value="%s" style='width:300'/><br>
延迟<input type="text" name="delta" value="(-10800, 10800)"  style='width:600'><br>
Q点<input type="text" name="qp" value="(100,9999999)"  style='width:600'><br>
最后<input type="text" name="last" value="5"  style='width:600'><br>
<input type="submit" value="很慢很慢的统计"><br>
</form>
</body>
</html>'''

def Req(request):
	'''【数据与工具】--行为统计'''
	now = datetime.datetime.now()
	one_day_ago = now - datetime.timedelta(days = 1)
	return HttpResponse(html  % (AutoHTML.GetURL(Res), AutoHTML.ToDataBase(), one_day_ago.strftime("%Y-%m-%d %H:%M:%S"), now.strftime("%Y-%m-%d %H:%M:%S")))

def Res(request):
	return HttpResponse("这样查询会死人的")
	dbids = AutoHTML.AsDataBaseIDs(request.POST)
	name = AutoHTML.AsString(request.POST, "tname")
	instruction = AutoHTML.AsString(request.POST, "instruction")
	start_time = AutoHTML.AsDateTime(request.POST, "start_time")
	end_time = AutoHTML.AsDateTime(request.POST, "end_time")
	delta = eval(AutoHTML.AsString(request.POST, "delta"))
	qp = eval(AutoHTML.AsString(request.POST, "qp"))
	last = AutoHTML.AsInt(request.POST, "last")
	# 一定选了区
	if not dbids:
		return HttpResponse("至少要选择一个区！")
	# 确保开始时间小于结束时间
	if start_time > end_time:
		start_time , end_time = end_time, start_time
	if not Environment.IsWindows:
		if not name:
			return HttpResponse("要一个名称啊！")
		if len(instruction) < 20:
			return HttpResponse("大哥，多些点说明啊！")
	argv = {"start_time": start_time, "end_time": end_time, "delta": delta, "qp":qp, "last":last}
	task = LogNearbyTask()
	for dbid in dbids:
		task.append_ctask(dbid, WorldHelp.GetZone()[dbid].get_name())
	tid = task.create(name, instruction, argv)
	if tid:
		return HttpResponse("创建任务<a href='/Tool/ShowTask/ShowTask/?tid=%s'>%s</a>" % (tid, tid))
	else:
		return HttpResponse("有太多的任务还未完成！")

class LogNearbyTask(WebTask.ZoneTask):
	RTYPE = dict
	def _do_ctask(self, ctid, argv):
		return self.get_lost_log(ctid, argv)
	
	def get_lost_log(self, ctid, argv):
		from Integration.WebPage.DataBase import RoleLog
		start_time = Time.DateTime2UnitTime(argv["start_time"])
		end_time = Time.DateTime2UnitTime(argv["end_time"])
		delta = argv["delta"]
		qp = argv["qp"]
		last = argv["last"]
		tdelta = datetime.timedelta(seconds = delta[0]), datetime.timedelta(seconds = delta[1])
		result = {}
		con = DBHelp.ConnectMasterDBByID(ctid, "role_sys_log")
		with con as cur:
			log_ids = set()
			cur.execute("select role_id, di32_0 from role_sys_data_%s.role_data" % ctid + " where di32_6 > %s and di32_6 < %s and di32_0 > %s and di32_0 < %s;", (qp[0], qp[1], start_time, end_time))
			for role_id, di32_0 in cur.fetchall():
				dt = Time.UnixTime2DateTime(di32_0)
				tstart_time = dt + tdelta[0]
				tend_time = dt + tdelta[1]
				distinct_logs = []
				for suff in RoleLog.get_suffs(cur, tstart_time, tend_time):
					cur.execute("select log_id, log_transaction, log_datetime from log_obj" + suff + " where role_id = %s and log_datetime > %s and log_datetime < %s;", (role_id, tstart_time, tend_time))
					for log_id, log_transaction, log_datetime in cur.fetchall():
						if log_id in log_ids:
							continue
						log_ids.add(log_id)
						distinct_logs.append((log_transaction, log_datetime))
					cur.execute("select log_id, log_transaction, log_datetime from log_value" + suff + " where role_id = %s and log_datetime > %s and log_datetime < %s;", (role_id, tstart_time, tend_time))
					for log_id, log_transaction, log_datetime in cur.fetchall():
						if log_id in log_ids:
							continue
						log_ids.add(log_id)
						distinct_logs.append((log_transaction, log_datetime))
					# 按照时间顺序排序
					distinct_logs.sort(key=lambda it:it[1])
					# 取最后几个
					distinct_logs = distinct_logs[-last:]
					# 统计
					for log_transaction, _ in distinct_logs:
						result[log_transaction] = result.get(log_transaction, 0) + 1
		return result
	
	def get_task_result(self):
		# 1 先搜集所以的key
		keys = set()
		for _, _, result in self.results:
			keys.update(result.iterkeys())
		keys = list(keys)
		# 构建表格
		head = ["区ID", "区名"]
		for key in keys:
			head.append(ConfigHelp.GetFullNameByTransaction(key))
		body = []
		total = [0] * len(keys)
		for zid, zname, result in self.results:
			row = [zid, zname]
			for idx, key in enumerate(keys):
				value = result.get(key, 0)
				row.append(value)
				total[idx] += value
			body.append(row)
		total_row = ["0", "总共"]
		total_row.extend(total)
		body.insert(0, total_row)
		table = AutoHTML.Table(head, body)
		return table.ToHtml()

Permission.reg_design(Req)
Permission.reg_design(Res)
