#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.AutoHTML")
#===============================================================================
# 辅助构建和读取HTML模块
#===============================================================================
import datetime
from django.utils import encoding
from django.http import HttpResponse
from ThirdLib import PrintHelp
from World import Define as World_Define, Define
from ComplexServer.API import Define as Http_Define
from Integration.Help import WorldHelp

Error = HttpResponse(Http_Define.Error)

def PyStringToHtml(s):
	s = s.replace("\n", "<br>")
	s = s.replace("\t", "&nbsp;&nbsp;")
	s = s.replace(" ", "&nbsp;")
	return s

def PyObjToHtml(o):
	return PyStringToHtml(PrintHelp.pformat(o))

def AsBool(GET_POST, name):
	return name in GET_POST

def AsString(GET_POST, name):
	return encoding.smart_str(GET_POST.get(name, ""))

def AsStrings(GET_POST, name = "tarea"):
	s = AsString(GET_POST, name)
	ret = []
	for it in s.split('\n'):
		if it.endswith('\r'):
			it = it[:-1]
		if not it:
			continue
		ret.append(it)
	return ret

def AsInt(GET_POST, name):
	s = GET_POST.get(name)
	if s:
		return int(s)
	else:
		return 0

def AsInts(GET_POST, name):
	s = GET_POST.get(name, "")
	ret = []
	for it in s.split('\n'):
		if it.endswith('\r'):
			it = it[:-1]
		if not it:
			continue
		ret.append(int(it))
	return ret

def AsDate(GET_POST):
	return datetime.datetime.strptime(GET_POST["date"], "%Y-%m-%d").date()

def AsDateTime(GET_POST, name = "datetime"):
	return datetime.datetime.strptime(GET_POST[name], "%Y-%m-%d %H:%M:%S")

def AsList(GET_POST, name):
	return [encoding.smart_str(item) for item in GET_POST.getlist(name) if item]

def AsSet(GET_POST, name):
	return set(AsList(GET_POST, name))

def GetURL(fun):
	import AutoURL
	return "/%s/%s/" % (AutoURL.GetURI(fun.__module__), fun.__name__)

# HTML表格
class Table(object):
	def __init__(self, head, body = None, tatil = None):
		self.head = head
		if body is None:
			self.body = []
		else:
			self.body = body
		self.tatil = tatil
	
	def __Rows(self):
		lh = len(self.head)
		for row in self.body:
			lr = len(row)
			if lh == lr:
				yield row
			elif lh > lr:
				row = list(row)
				row.extend([None] * (lh - lr))
				yield row
			else:
				row = list(row)
				r1 = row[:lh - 1]
				r2 = map(str, row[lh - 1:])
				r1.append(",".join(r2))
				yield r1
	
	def ToHtml(self, valign=''):
		res = []
		# 标题
		if self.tatil:
			res.append("<font color='blue'>%s</font><br>" % self.tatil)
		res.append("<table border='1px' cellspacing='0px' style='border-collapse:collapse'>")
		# 表头
		res.append("<tr>")
		for c in self.head:
			if valign:
				res.append("<td valign='%s'>%s</td>" % (valign, c))
			else:
				res.append("<td>%s</td>" % c)
		res.append("</tr>")
		# 表体
		for row in self.__Rows():
			res.append("<tr>")
			for c in row:
				if valign:
					res.append("<td valign='%s'>%s</td>" % (valign, c))
				else:
					res.append("<td>%s</td>" % c)
			res.append("</tr>")
		res.append("</table>")
		res.append("<br>")
		return "".join(res)

def MakeTable(rows):
	html = ["<table border='1px' cellspacing='0px' style='border-collapse:collapse'>"]
	for row in rows:
		html.append("<tr>")
		for cell in row:
			html.append("<td>%s</td>" % cell)
		html.append("</tr>")
	html.append("</table>")
	return "".join(html)

def MakeInnerTable(rows):
	html = ["<table border='1px' cellspacing='0px' frame='void' style='border-collapse:collapse'>"]
	for row in rows:
		html.append("<tr>")
		for cell in row:
			html.append("<td>%s</td>" % cell)
		html.append("</tr>")
	html.append("</table>")
	return "".join(html)

class Select(object):
	def __init__(self, name = "sel", width = 200):
		self.name = name
		self.width = width
		self.lis = []
	
	def Append(self, show, value):
		self.lis.append((show, value))
	
	def ToHtml(self):
		res = ["<select name='%s' style='width:%s'>" % (self.name, self.width)]
		for idx, info in enumerate(self.lis):
			res.append("<option value ='%s'>%s</option>" % (idx, info[0]))
		res.append("</select>")
		res.append("<br>")
		return "".join(res)
	
	def GetValue(self, GET_POST):
		return self.lis[AsInt(GET_POST, self.name)][1]

class Select2(object):
	def __init__(self, name = "sel", width = 200):
		self.name = name
		self.width = width
		self.lis = []
	
	def Append(self, show, value):
		self.lis.append((show, value))
	
	def ToHtml(self):
		res = ["<select name='%s' style='width:%s'>" % (self.name, self.width)]
		for show, value in self.lis:
			res.append("<option value ='%s'>%s</option>" % (value, show))
		res.append("</select>")
		res.append("<br>")
		return "".join(res)
	
	def GetValue(self, GET_POST):
		return self.lis[AsInt(GET_POST, self.name)][1]

_ProcessControl = None
_ProcessControl_Test = None
_ProcessJS = '''<script language="javascript">
function checkall(cname, plug, checked){
	var cbs = document.getElementsByName(cname); 
	for (var i=0; i<cbs.length; i++){
		if(cbs[i].alt.indexOf(plug) >= 0) {cbs[i].checked = checked;};
	};
};
</script>
进程-->
<input type="checkbox" name="A" onclick="checkall('process', 'A', this.checked)" />所有(A)&nbsp;&nbsp;
<input type="checkbox" name="C" onclick="checkall('process', 'C', this.checked)" />控制(C)&nbsp;&nbsp;
<input type="checkbox" name="G" onclick="checkall('process', 'G', this.checked)" />网关(G)&nbsp;&nbsp;
<input type="checkbox" name="H" onclick="checkall('process', 'H', this.checked)" />HTTP(H)&nbsp;&nbsp;
<input type="checkbox" name="L" onclick="checkall('process', 'L', this.checked)" />逻辑(L)&nbsp;&nbsp;
<input type="checkbox" name="D" onclick="checkall('process', 'D', this.checked)" />数据(D)&nbsp;&nbsp;<br>
'''

def RefreshProcessCache():
	global _ProcessControl, _ProcessControl_Test
	_ProcessControl = None
	_ProcessControl_Test = None


def ToProcess():
	global _ProcessControl
	if _ProcessControl: return _ProcessControl
	# 配置
	MAX_CELL_CNT = 4
	MAX_PROCESS_CNT = 4
	# 缓存控制进程信息
	control_process = []
	# 缓存每个服的进程信息
	world_process = {}
	# 将进程分类
	for process in WorldHelp.GetProcess().itervalues():
		if World_Define.IsControlProcessKey(process.pkey):
			control_process.append(process)
		else:
			world_process.setdefault(process.work_zid, []).append(process)
	# 构建html代码
	html = [_ProcessJS]
	html.append("<table border='1px' cellspacing='0px' style='border-collapse:collapse'>")
	# 第一行是全局控制进程
	row = ["控制进程"]
	control_process.sort()
	for process in control_process:
		row.append("<input type='checkbox' name='process' value ='%s' alt = 'A|%s' />%s" % (process.pkey, process.get_plug_coding(), process.pkey))
	html.append("<tr><td colspan='%s'>%s</td></tr>" % (MAX_CELL_CNT, MakeInnerTable([row])))
	# 接下来按照区ID，构建区进程
	world_process = world_process.items()
	world_process.sort(key=lambda it:it[0])
	for _, process in world_process:
		process.sort()
	idx = 0
	while idx < len(world_process):
		cell_cnt = 0
		html.append("<tr>")
		while cell_cnt < MAX_CELL_CNT:
			# 获取本个和下一个区的进程信息
			if idx < len(world_process):
				now_zone_id, now_process = world_process[idx]
				now_zone_name = WorldHelp.GetFullNameByZoneID(now_zone_id)
			else:
				now_zone_id = 0
				now_zone_name = ""
				now_process = []
			if idx + 1 < len(world_process):
				next_zone_id, next_process = world_process[idx + 1]
				next_zone_name = WorldHelp.GetFullNameByZoneID(next_zone_id)
			else:
				next_zone_id = 0
				next_zone_name = ""
				next_process = []
			# 两个都不超出
			if len(now_process) <= MAX_PROCESS_CNT and len(next_process) <= MAX_PROCESS_CNT:
				row = [now_zone_name]
				for process in now_process:
					row.append("<input type='checkbox' name='process' value ='%s' alt = 'A|%s' />%s" % (process.pkey, process.get_plug_coding(), process.pkey))
				html.append("<td>%s</td>" % MakeInnerTable([row]))
				row = [next_zone_name]
				for process in next_process:
					row.append("<input type='checkbox' name='process' value ='%s' alt = 'A|%s' />%s" % (process.pkey, process.get_plug_coding(), process.pkey))
				html.append("<td>%s</td>" % MakeInnerTable([row]))
				cell_cnt += 2
				idx += 2
			else:
				row = [now_zone_name]
				for process in now_process:
					row.append("<input type='checkbox' name='process' value ='%s' alt = 'A|%s' />%s" % (process.pkey, process.get_plug_coding(), process.pkey))
				html.append("<td colspan='2'>%s</td>" % MakeInnerTable([row]))
				cell_cnt += 2
				idx += 1
		html.append("</tr>")
	html.append("</table>")
	_ProcessControl = "".join(html)
	return _ProcessControl


def ToProcessTest():
	global _ProcessControl_Test
	if _ProcessControl_Test: return _ProcessControl_Test
	# 配置
	MAX_CELL_CNT = 4
	MAX_PROCESS_CNT = 4
	# 缓存控制进程信息
	control_process = []
	# 缓存每个服的进程信息
	world_process = {}
	# 将进程分类
	
	for process in WorldHelp.GetProcess().itervalues():
		if process.pid not in Define.TestWorldIDs:
			continue
		if World_Define.IsControlProcessKey(process.pkey):
			control_process.append(process)
		else:
			world_process.setdefault(process.work_zid, []).append(process)
	# 构建html代码
	html = [_ProcessJS]
	html.append("<table border='1px' cellspacing='0px' style='border-collapse:collapse'>")
	# 第一行是全局控制进程
	row = ["控制进程"]
	control_process.sort()
	for process in control_process:
		row.append("<input type='checkbox' name='process' value ='%s' alt = 'A|%s' />%s" % (process.pkey, process.get_plug_coding(), process.pkey))
	html.append("<tr><td colspan='%s'>%s</td></tr>" % (MAX_CELL_CNT, MakeInnerTable([row])))
	# 接下来按照区ID，构建区进程
	world_process = world_process.items()
	world_process.sort(key=lambda it:it[0])
	for _, process in world_process:
		process.sort()
	idx = 0
	while idx < len(world_process):
		cell_cnt = 0
		html.append("<tr>")
		while cell_cnt < MAX_CELL_CNT:
			# 获取本个和下一个区的进程信息
			if idx < len(world_process):
				now_zone_id, now_process = world_process[idx]
				now_zone_name = WorldHelp.GetFullNameByZoneID(now_zone_id)
			else:
				now_zone_id = 0
				now_zone_name = ""
				now_process = []
			if idx + 1 < len(world_process):
				next_zone_id, next_process = world_process[idx + 1]
				next_zone_name = WorldHelp.GetFullNameByZoneID(next_zone_id)
			else:
				next_zone_id = 0
				next_zone_name = ""
				next_process = []
			# 两个都不超出
			if len(now_process) <= MAX_PROCESS_CNT and len(next_process) <= MAX_PROCESS_CNT:
				row = [now_zone_name]
				for process in now_process:
					row.append("<input type='checkbox' name='process' value ='%s' alt = 'A|%s' />%s" % (process.pkey, process.get_plug_coding(), process.pkey))
				html.append("<td>%s</td>" % MakeInnerTable([row]))
				row = [next_zone_name]
				for process in next_process:
					row.append("<input type='checkbox' name='process' value ='%s' alt = 'A|%s' />%s" % (process.pkey, process.get_plug_coding(), process.pkey))
				html.append("<td>%s</td>" % MakeInnerTable([row]))
				cell_cnt += 2
				idx += 2
			else:
				row = [now_zone_name]
				for process in now_process:
					row.append("<input type='checkbox' name='process' value ='%s' alt = 'A|%s' />%s" % (process.pkey, process.get_plug_coding(), process.pkey))
				html.append("<td colspan='2'>%s</td>" % MakeInnerTable([row]))
				cell_cnt += 2
				idx += 1
		html.append("</tr>")
	html.append("</table>")
	_ProcessControl_Test = "".join(html)
	return _ProcessControl_Test



def AsProcessKeys(GET_POST):
	return [str(processkey) for processkey in GET_POST.getlist("process")]

def ToTextarea(name = "tarea", h = "300"):
	return '''<textarea wrap="off" name="%s" style="width:100%%;height:%s;"></textarea><br><br>''' % (name,  h)

_DataBaseControl = None
_DataBaseJS = '''<script language="javascript">
function checkall(cname, plug, checked){
	var cbs = document.getElementsByName(cname); 
	for (var i=0; i<cbs.length; i++){
		cbs[i].checked = checked;
	};
};
</script>
数据库-->
<input type="checkbox" name="A" onclick="checkall('database', 'A', this.checked)" />所有&nbsp;&nbsp;
'''
def ToDataBase():
	global _DataBaseControl
	if _DataBaseControl: return _DataBaseControl
	role_cells = 10
	database_table = []
	row = []
	zones = WorldHelp.GetZone().values()
	zones.sort(key=lambda zone:zone.zid)
	for zone in zones:
		if len(row) == role_cells:
			database_table.append(row)
			row = []
		row.append('''<input type="checkbox" name="database" value ="%s" />%s(%s)<br>''' % (zone.zid, zone.zid, zone.get_name()))
	else:
		if len(row) != role_cells:
			row.extend(["None"] * (role_cells - len(row)))
		database_table.append(row)
	table = [_DataBaseJS]
	table.append("<table border='1'>")
	for row in database_table:
		table.append("<tr>")
		for cell in row:
			table.append("<td>%s</td>" % cell)
		table.append("</tr>")
	table.append("</table>")
	_DataBaseControl = "".join(table)
	return _DataBaseControl

def AsDataBaseIDs(GET_POST):
	return [int(dbid) for dbid in GET_POST.getlist("database")]

