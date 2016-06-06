#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 角色日志统计，产出消耗的东西
#===============================================================================
import datetime
import Environment
from ComplexServer.Plug.DB import DBHelp
from Integration import AutoHTML
from Integration.Help import WorldHelp, WebTask, ConfigHelp
from Integration.WebPage.User import Permission
from django.http import HttpResponse

Query = AutoHTML.Select()
Query.Append("次数人数", 0)
Query.Append("OBJ（按Obj分类）", 1)
Query.Append("OBJ（按事务分类）", 2)
Query.Append("数值（按事件分类）", 3)
Query.Append("数值（按事务分类）", 4)
html = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>日志统计</title>
</head>
<body>
<form  action="%s" method="post" target="_blank">
%s<br>
名称<input type="text" name="tname" value=""  style='width:300'><br>
描述<input type="text" name="instruction" value=""  style='width:600'><br>
统计%s<br>
从<input type='text' name='start_time' value="%s" style='width:300'/>到<input type='text' name='end_time' value="%s" style='width:300'/><br>
OBJ<input type="text" name="objs" value=""  style='width:300'><br>
事务<input type="text" name="transaction" value=""  style='width:300'>事件<input type="text" name="event" value=""  style='width:300'><br>
数值<input type="text" name="value" value=""  style='width:300'><br>
<input type="submit" value="很慢很慢的统计"><br>
</form>
</body>
</html>'''

def Req(request):
	'''【数据与工具】--日志统计'''
	now = datetime.datetime.now()
	one_day_ago = now - datetime.timedelta(days = 1)
	return HttpResponse(html  % (AutoHTML.GetURL(Res), AutoHTML.ToDataBase(), Query.ToHtml(), one_day_ago.strftime("%Y-%m-%d %H:%M:%S"), now.strftime("%Y-%m-%d %H:%M:%S")))

def Res(request):
	dbids = AutoHTML.AsDataBaseIDs(request.POST)
	name = AutoHTML.AsString(request.POST, "tname")
	instruction = AutoHTML.AsString(request.POST, "instruction")
	start_time = AutoHTML.AsDateTime(request.POST, "start_time")
	end_time = AutoHTML.AsDateTime(request.POST, "end_time")
	transactions = [int(i) for i in AutoHTML.AsString(request.POST, "transaction").split(" ") if i.isdigit()]
	events = [int(i) for i in AutoHTML.AsString(request.POST, "event").split(" ") if i.isdigit()]
	objs = [int(i) for i in AutoHTML.AsString(request.POST, "objs").split(" ") if i.isdigit()]
	value = AutoHTML.AsInt(request.POST, "value")
	query = Query.GetValue(request.POST)
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
	# 构建筛选条件
	wheres = []
	# obj筛选
	if query == 0:
		if objs and value:
			return HttpResponse("不能同时有OBJ和Value值啊！")
		if not build_where(wheres, [("obj_type", objs), ("log_transaction", transactions), ("log_event", events)]):
			return HttpResponse("查询条件奇葩！")
		if value > 0:
			wheres.append("log_old_value <= log_new_value")
		elif value < 0:
			wheres.append("log_old_value >= log_new_value")
		task = LogCountTask()
	elif query in (1, 2):
		if not build_where(wheres, [("obj_type", objs), ("log_transaction", transactions), ("log_event", events)]):
			return HttpResponse("查询条件奇葩！")
		task = LogObjTask()
	# 数值筛选
	elif query in (3, 4):
		if not build_where(wheres, [("log_transaction", transactions), ("log_event", events)]):
			return HttpResponse("查询条件奇葩！")
		if value > 0:
			wheres.append("log_old_value <= log_new_value")
		elif value < 0:
			wheres.append("log_old_value >= log_new_value")
		else:
			return HttpResponse("数值要填写啊！！！")
		task = LogValueTask()
	else:
		return HttpResponse("请不要篡改协议！")
	wheres.append("log_datetime >= '%s'" % start_time.strftime("%Y-%m-%d %H:%M:%S"))
	wheres.append("log_datetime <= '%s'" % end_time.strftime("%Y-%m-%d %H:%M:%S"))
	# 组合SQL的where部分
	where = " and ".join(wheres)
	argv = {"start_time": start_time, "end_time":end_time,
		"transactions": transactions, "events": events,
		"objs": objs, "value": value, "query": query,
		"where": where,
		}
	
	for dbid in dbids:
		task.append_ctask(dbid, WorldHelp.GetZone()[dbid].get_name())
	tid = task.create(name, instruction, argv)
	if tid:
		return HttpResponse("创建任务<a href='/Tool/ShowTask/ShowTask/?tid=%s'>%s</a>" % (tid, tid))
	else:
		return HttpResponse("有太多的任务还未完成！")

def is_continue(values):
	values.sort()
	for idx in xrange(len(values) - 1):
		if values[idx] + 1 != values[idx + 1]:
			return False
	return True

def build_where(wheres, column_values):
	# 排除没有值的项
	column_values = [cv for cv in column_values if cv[1]]
	# 查找一个值只要一项的项或者连续的项
	for idx in xrange(len(column_values)):
		column, values = column_values[idx]
		if len(values) == 1:
			break
		if is_continue(values):
			break
	else:
		if len(column_values) > 1:
			return False
	for idx in xrange(len(column_values)):
		column, values = column_values[idx]
		if len(values) == 1:
			wheres.append("%s = %s" % (column, values[0]))
			continue
		# 判断是否连续
		if is_continue(values):
			wheres.append("%s >= %s and %s <= %s" % (column, values[0], column, values[-1]))
		else:
			tmp = "%s = %%s" % column
			wheres.append("(%s)" % (" or ".join([tmp % value for value in values])))
	return True

class LogCountTask(WebTask.ZoneTask):
	RTYPE = tuple
	def _do_ctask(self, ctid, argv, limit = ""):
		from Integration.WebPage.DataBase import RoleLog
		con = DBHelp.ConnectMasterDBByID(ctid, "role_sys_log")
		log_id_set = set()
		role_id_set = set()
		objs = argv["objs"]
		value = argv["value"]
		start_time = argv["start_time"]
		end_time = argv["end_time"]
		where = argv["where"]
		with con as cur:
			if (not objs) and (not value):
				for suff in RoleLog.get_suffs(cur, start_time, end_time):
					h = cur.execute("select log_id, role_id from log_base%s where %s %s" % (suff, where, limit))
					self.rows += h
					for log_id, role_id in cur.fetchall():
						log_id_set.add(log_id)
						role_id_set.add(role_id)
			if not value:
				for suff in RoleLog.get_suffs(cur, start_time, end_time):
					h = cur.execute("select log_id, role_id from log_obj%s where %s %s" % (suff, where, limit))
					self.rows += h
					for log_id, role_id in cur.fetchall():
						log_id_set.add(log_id)
						role_id_set.add(role_id)
			if not objs:
				for suff in RoleLog.get_suffs(cur, start_time, end_time):
					h = cur.execute("select log_id, role_id from log_value%s where %s %s" % (suff, where, limit))
					self.rows += h
					for log_id, role_id in cur.fetchall():
						log_id_set.add(log_id)
						role_id_set.add(role_id)
			cur.close()
		return len(log_id_set), len(role_id_set)
	
	def get_task_result(self):
		table = AutoHTML.Table(["区ID", "区名", "次数", "人数"])
		total = [0, 0]
		for zid, zname, result in self.results:
			role_cnt, log_cnt = result
			table.body.append((zid, zname, role_cnt, log_cnt))
			total[0] += role_cnt
			total[1] += log_cnt
		row = ["0", "总共"]
		row.extend(total)
		table.body.insert(0, row)
		return table.ToHtml()

class LogObjTask(WebTask.ZoneTask):
	RTYPE = dict
	def _do_ctask(self, ctid, argv, limit = ""):
		from Integration.WebPage.DataBase import RoleLog
		con = DBHelp.ConnectMasterDBByID(ctid, "role_sys_log")
		result = {}
		query = argv["query"]
		start_time = argv["start_time"]
		end_time = argv["end_time"]
		where = argv["where"]
		with con as cur:
			for suff in RoleLog.get_suffs(cur, start_time, end_time):
				if query == 1:
					h = cur.execute("select obj_type, obj_int from log_obj%s where %s %s" % (suff, where, limit))
					self.rows += h
				else:
					h = cur.execute("select log_transaction, obj_int from log_obj%s where %s %s" % (suff, where, limit))
					self.rows += h
				for t, i in cur.fetchall():
					result[t] = result.get(t, 0) + i
			cur.close()
		return result
	
	def get_task_result(self):
		# 1 先搜集所以的key
		keys = set()
		for _, _, result in self.results:
			keys.update(result.iterkeys())
		keys = list(keys)
		# 获取参数
		con = DBHelp.ConnectHouTaiWeb()
		with con as cur:
			cur.execute("select argv from task where tid = %s;" % self.tid)
			argv = eval(cur.fetchall()[0][0])
		# 构建表格
		head = ["区ID", "区名"]
		if argv["query"] == 1:
			for key in keys:
				head.append(ConfigHelp.GetFullNameByCoding(key))
		else:
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

class LogValueTask(WebTask.ZoneTask):
	RTYPE = dict
	def _do_ctask(self, ctid, argv, limit = ""):
		from Integration.WebPage.DataBase import RoleLog
		con = DBHelp.ConnectMasterDBByID(ctid, "role_sys_log")
		query = argv["query"]
		start_time = argv["start_time"]
		end_time = argv["end_time"]
		where = argv["where"]
		result = {}
		with con as cur:
			for suff in RoleLog.get_suffs(cur, start_time, end_time):
				if query == 3:
					h = cur.execute("select log_event, log_old_value, log_new_value from log_value%s where %s %s" % (suff, where, limit))
					self.rows += h
				else:
					h = cur.execute("select log_transaction, log_old_value, log_new_value from log_value%s where %s %s" % (suff, where, limit))
					self.rows += h
				for t, l, n in cur.fetchall():
					result[t] = result.get(t, 0) + abs(l - n)
			cur.close()
		return result
	
	def get_task_result(self):
		# 1 先搜集所以的key
		keys = set()
		for _, _, result in self.results:
			keys.update(result.iterkeys())
		keys = list(keys)
		# 获取参数
		con = DBHelp.ConnectHouTaiWeb()
		with con as cur:
			cur.execute("select argv from task where tid = %s;" % self.tid)
			argv = eval(cur.fetchall()[0][0])
		# 构建表格
		head = ["区ID", "区名"]
		if argv["query"] == 3:
			for key in keys:
				head.append(ConfigHelp.GetFullNameByEvent(key))
		else:
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
