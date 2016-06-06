#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 角色命令日志查询
#===============================================================================
import datetime
from django.http import HttpResponse
from ComplexServer.Plug.DB import DBHelp
from Integration import AutoHTML
from Integration.WebPage.User import Permission

html = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>角色GM指令日志</title>
</head>
<body>
<form  action="%s" method="post" target="_blank">
%s
<input type="submit" value="查询">
</form>
</body>
</html>'''

def Req(request):
	'''【工具】--角色命令日志查询'''
	now = datetime.datetime.now()
	one_day_ago = now - datetime.timedelta(days = 1)
	
	table = AutoHTML.Table(["开始时间（必填）", "<input type='text' name='start_time' value='%s' style='width:300'/>" % one_day_ago.strftime("%Y-%m-%d %H:%M:%S")])
	table.body.append(["结束时间（必填）", "<input type='text' name='end_time' value='%s' style='width:300'/>" % now.strftime("%Y-%m-%d %H:%M:%S")])
	return HttpResponse(html % (AutoHTML.GetURL(Res), table.ToHtml()))

def Res(request):
	start_time = AutoHTML.AsDateTime(request.POST, "start_time")
	end_time = AutoHTML.AsDateTime(request.POST, "end_time")
	# 0确保开始时间小于结束时间
	if start_time > end_time:
		start_time , end_time = end_time, start_time
		
	start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')
	end_time = end_time.strftime('%Y-%m-%d %H:%M:%S')
	
	con = DBHelp.ConnectHouTaiWeb()
	log = []
	with con as cur:
		cur.execute("show tables")
		for row in cur.fetchall():
			if row[0] == 'role_gm':
				break
		else:
			return HttpResponse("该版本暂未开放此功能!")
		cur.execute("SELECT user, role_ids, command, exec_time FROM role_gm WHERE exec_time >= '%s' AND exec_time <= '%s'" % (start_time, end_time))
		log.extend(cur.fetchall())
	
	# 构建完整事务
	tras = {}
	for l in log:
		t = tras.get(l[0])
		if t is None:
			tras[l[0]] = t = Tra()
		t.append_log(l)
	
	# 按时间排序
	tras = tras.values()
	tras.sort(key=lambda it:it.exec_time)
	# 显示
	html = ["<font color='blue'>%s个帐号执行命令</font>" % len(tras)]
	for tra in tras:
		html.append(tra.to_html())
	return HttpResponse("<br>".join(html))

class Tra(object):
	def __init__(self):
		self.user = None
		self.role_ids = ''
		self.command = ''
		self.exec_time = None
		self.log = []
		
	def init(self, l):
		if self.user is not None:
			return
		self.user = l[0]
		self.role_ids = l[1]
		self.command = l[2]
		self.exec_time = l[3]
	
	def append_log(self, log):
		self.init(log)
		self.log.append(log)
	
	def to_html(self):
		html =["<br>"]
		html.append("<table border='0'><tr valign='top'>")
		if self.log:
			html.append("<td>")
			html.append(AutoHTML.Table(["帐号/ip地址", "使用对象角色id", "角色命令", "执行时间"], self.log).ToHtml())
			html.append("</td>")
		html.append("</tr></table>")
		return "".join(html)

Permission.group([Req,Res],['design','operate', 'develop', 'host'])