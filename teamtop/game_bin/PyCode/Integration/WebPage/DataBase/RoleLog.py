#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 角色日志查询
#===============================================================================
import datetime
from django.http import HttpResponse
from Common import CValue
from World import Language
from ComplexServer.Log import AutoLog
from ComplexServer.Plug.DB import DBHelp
from Integration import AutoHTML
from Integration.Help import ConfigHelp
from Integration.WebPage.User import Permission

html = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>角色日志</title>
</head>
<body>
<form  action="%s" method="post" target="_blank">
%s
<input type="submit" value="慢慢查询">
</form>
</body>
</html>'''
k_v = AutoLog.Transactions.items()
k_v.sort(key=lambda it: it[0])
transaction = AutoHTML.Select("log_transaction", 300)
transaction.Append("0-占位", 0)
for value, show in k_v:
	transaction.Append("%s-%s" % (value, show), value)
k_v = AutoLog.Events.items()
k_v.sort(key=lambda it: it[0])
event = AutoHTML.Select("log_event", 300)
event.Append("0-占位", 0)
for value, show in k_v:
	event.Append("%s-%s" % (value, show), value)
k_v = ConfigHelp.GetCodingName().items()
k_v.sort(key=lambda it:it[0])
obj = AutoHTML.Select("log_obj", 300)
obj.Append("0-占位", 0)
for coding, name in k_v:
	obj.Append("%s-%s" % (coding, name), coding)

def Req(request):
	'''【工具】--角色日志'''
	now = datetime.datetime.now()
	one_day_ago = now - datetime.timedelta(days = 1)
	
	table = AutoHTML.Table(["角色ID或者数据库ID（必填）", "<input type='text' name='role_id' value='0' style='width:300'/>"])
	table.body.append(["开始时间（必填）", "<input type='text' name='start_time' value='%s' style='width:300'/>" % one_day_ago.strftime("%Y-%m-%d %H:%M:%S")])
	table.body.append(["结束时间（必填）", "<input type='text' name='end_time' value='%s' style='width:300'/>" % now.strftime("%Y-%m-%d %H:%M:%S")])
	table.body.append(["事务（对所有筛选有效）", transaction.ToHtml()])
	table.body.append(["事件（对所有筛选有效）", event.ToHtml()])
	table.body.append(["内容（对所有筛选有效）", "<input type='text' name='log_content' style='width:300'/>"])
	table.body.append(["OBJ（仅对OBJ筛选有效）", obj.ToHtml()])
	table.body.append(["数值（仅对数值筛选有效）", "<input type='text' name='log_value' value='0' style='width:300'/>"])
	table.body.append(["筛选", "基本<input type='radio' name='log_where' value='base' checked=''>&nbsp&nbspOBJ<input type='radio' name='log_where' value='obj'>&nbsp&nbsp数值<input type='radio' name='log_where' value='value'>"])
	table.body.append(["查询", "基本<input type='checkbox' name='log_select' value='base' checked=''>&nbsp&nbspOBJ<input type='checkbox' name='log_select' value='obj' checked=''>&nbsp&nbsp数值<input type='checkbox' name='log_select' value='value' checked=''>"])
	return HttpResponse(html % (AutoHTML.GetURL(Res), table.ToHtml()))

def Res(request):
	role_id = AutoHTML.AsInt(request.POST, "role_id")
	start_time = AutoHTML.AsDateTime(request.POST, "start_time")
	end_time = AutoHTML.AsDateTime(request.POST, "end_time")
	log_transaction = transaction.GetValue(request.POST)
	log_event = event.GetValue(request.POST)
	log_content = AutoHTML.AsString(request.POST, "log_content")
	log_obj = obj.GetValue(request.POST)
	log_value = AutoHTML.AsInt(request.POST, "log_value")
	log_where = AutoHTML.AsString(request.POST, "log_where")
	log_select = AutoHTML.AsSet(request.POST, "log_select")
	# 0确保开始时间小于结束时间
	if start_time > end_time:
		start_time , end_time = end_time, start_time
	# 1构建where条件
	wheres = []
	# 根据角色ID筛选
	if role_id > CValue.P2_32:
		wheres.append("role_id = %s" % role_id)
	# 根据事物筛选
	if log_transaction:
		wheres.append("log_transaction = %s" % log_transaction)
	# 留一个后门用于查询无事务的日志
	elif log_content == "0":
		wheres.append("log_transaction = 0")
		log_content = ""
	# 根据事件筛选
	if log_event:
		wheres.append("log_event = %s" % log_event)
	# 如果有对象，则可以按照对象coding筛选
	if log_where == "obj" and log_obj:
		wheres.append("obj_type = %s" % log_obj)
	# 加上时间筛选
	wheres.append("log_datetime >= '%s'" % start_time.strftime("%Y-%m-%d %H:%M:%S"))
	wheres.append("log_datetime <= '%s'" % end_time.strftime("%Y-%m-%d %H:%M:%S"))
	# 如果有数值，则可以按照数值筛选
	if log_where == "value" and log_value:
		if log_value > 0:
			wheres.append("log_new_value - log_old_value >= %s" % log_value)
		elif log_value < 0:
			wheres.append("log_old_value - log_new_value >= %s" % -log_value)
	# 如果有内容，则可以按照内容筛选
	if log_content and Language.all_english(log_content):
		wheres.append("log_content like '%s'" % log_content)
	# 2获取数据库连接
	if role_id > CValue.P2_32:
		con = DBHelp.ConnectMasterDBRoleID(role_id, "role_sys_log")
	else:
		con = DBHelp.ConnectMasterDBByID(role_id, "role_sys_log")
	# 3查询
	bases = []
	objs = []
	values = []
	where = " and ".join(wheres)
	with con as cur:
		for suff in get_suffs(cur, start_time, end_time):
			sql_log_id = "select distinct(log_id) from log_%s%s where %s limit 1000" % (log_where, suff, where)
			#print sql_log_id
			if "base" in log_select:
				sql_base = "select b.log_id, b.role_id, b.log_transaction, b.log_event, b.log_datetime, b.log_content from (%s) as sf inner join log_base%s as b using(log_id);" % (sql_log_id, suff)
				#print sql_base
				cur.execute(sql_base)
				bases.extend(cur.fetchall())
			if "obj" in log_select:
				sql_obj = "select o.log_id, o.role_id, o.log_transaction, o.log_event, o.log_datetime, o.log_content, o.obj_id, o.obj_type, o.obj_int, o.obj_data from (%s) as sf inner join log_obj%s as o using(log_id);" % (sql_log_id, suff)
				#print sql_obj
				cur.execute(sql_obj)
				objs.extend(cur.fetchall())
			if "value" in log_select:
				sql_value = "select v.log_id, v.role_id, v.log_transaction, v.log_event, v.log_datetime, v.log_content, v.log_old_value, v.log_new_value from (%s) as sf inner join log_value%s as v using(log_id);" % (sql_log_id, suff)
				#print sql_value
				cur.execute(sql_value)
				values.extend(cur.fetchall())
	# 构建完整事务
	tras = {}
	for b in bases:
		t = tras.get(b[0])
		if t is None:
			tras[b[0]] = t = Tra()
		t.append_base(b)
	for o in objs:
		t = tras.get(o[0])
		if t is None:
			tras[o[0]] = t = Tra()
		t.append_obj(o)
	for v in values:
		t = tras.get(v[0])
		if t is None:
			tras[v[0]] = t = Tra()
		t.append_value(v)
	# 按时间排序
	tras = tras.values()
	tras.sort(key=lambda it:it.log_datetime)
	# 显示
	html = ["<font color='blue'>%s个事务</font>" % len(tras)]
	for tra in tras:
		html.append(tra.to_html())
	return HttpResponse("<br>".join(html))

def get_suffs(cur, start_time, end_time):
	suffs = []
	table_name_begin = "log_base"
	# 获取所有的表名
	cur.execute("show tables;")
	for row in cur.fetchall():
		tablename = row[0]
		if not tablename.startswith(table_name_begin):
			continue
		# 查找该表的时间跨度
		cur.execute("select min(log_datetime), max(log_datetime) from %s" % tablename)
		result = cur.fetchall()
		if not result:
			continue
		result = result[0]
		if (not result[0]) or (not result[1]):
			continue
		# 该表不在该时间段，忽视
		if result[0] > end_time:
			continue
		if tablename != table_name_begin and result[1] < start_time:
			continue
		# 保存后缀
		suffs.append(tablename[len(table_name_begin):])
	return suffs

class Tra(object):
	def __init__(self):
		self.log_id = None
		self.log_datetime = None
		self.log_transaction = None
		self.base = []
		self.obj = []
		self.value = []
	
	def init(self, l):
		if self.log_id is not None:
			return
		self.log_id = l[0]
		self.log_datetime = l[4]
		self.log_transaction = l[2]
	
	def append_base(self, b):
		self.init(b)
		self.base.append(b)
	
	def append_obj(self, o):
		self.init(o)
		self.obj.append(o)
	
	def append_value(self, v):
		self.init(v)
		self.value.append(v)
	
	def to_html(self):
		html =["日志ID:%s-事务:%s-时间:%s<br>" % (self.log_id, ConfigHelp.GetFullNameByTransaction(self.log_transaction), self.log_datetime)]
		html.append("<table border='0'><tr valign='top'>")
		if self.base:
			html.append("<td>")
			rows = [(b[1], ConfigHelp.GetFullNameByEvent(b[3]), b[5]) for b in self.base]
			html.append(AutoHTML.Table(["角色ID", "事件", "内容"], rows).ToHtml())
			html.append("</td>")
		if self.obj:
			html.append("<td>")
			rows = []
			RA = rows.append
			CGE = ConfigHelp.GetFullNameByEvent
			CGT = ConfigHelp.GetFullNameByTarotType
			CGC = ConfigHelp.GetFullNameByCoding
			for o in self.obj:
				if o[3] == 30015 or 30016 == o[3]:
					#命魂
					RA((o[1], CGE(o[3]), o[5], o[6], CGT(o[7]), o[8], o[9]))
				else:
					#物品英雄
					RA((o[1], CGE(o[3]), o[5], o[6], CGC(o[7]), o[8], o[9]))
					
			html.append(AutoHTML.Table(["角色ID", "事件", "内容", "obj_id", "obj_type", "obj_int", "obj_data"], rows).ToHtml())
			html.append("</td>")
		if self.value:
			html.append("<td>")
			rows = [(v[1], ConfigHelp.GetFullNameByEvent(v[3]), v[5], v[6], v[7]) for v in self.value]
			html.append(AutoHTML.Table(["角色ID", "事件", "内容", "旧值", "新值"], rows).ToHtml())
			html.append("</td>")
		html.append("</tr></table>")
		return "".join(html)

Permission.group([Req,Res],['design','operate'])


