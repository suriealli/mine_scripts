#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 测试上报
#===============================================================================
import random
import urllib
import urllib2
import traceback
from django.http import HttpResponse
from Integration import AutoHTML
from ComplexServer.API import QQHttp
from ComplexServer.Plug.DB import DBHelp
from Integration.WebPage.User import Permission
import time
from Integration.WebPage.model import me

html = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>%s</title>
</head>
<body>
<form action="%s" method="POST">
%s：<input type="text" name="role_ids"><br>
cmd：<input type="text" name="cmd"><br>
<input type="submit" value="%s" />
</form>
</body>
</html>'''

def Reg(request):
	'''【接口】--上报数据'''
	return HttpResponse(html % (
		me.say(request,'上报数据'),
		AutoHTML.GetURL(Res),
		me.say(request,'角色ID列表'),
		me.say(request,'添加')
	))

def Res(request):
	GET_POST = request.POST
	role_ids = eval(AutoHTML.AsString(GET_POST, "role_ids"))
	cmd = AutoHTML.AsString(GET_POST, "cmd")
	body = do_roles(role_ids, cmd)
	table = AutoHTML.Table([
		me.say(request,"角色ID"),
		me.say(request,"结果")
	], body)
	return HttpResponse(table.ToHtml())

def do_roles(role_ids, cmd):
	role_ids = list(role_ids)
	role_ids.sort()
	dbid = 0
	con = None
	result = []
	for role_id in role_ids:
		if dbid != DBHelp.GetDBIDByRoleID(role_id):
			if con is not None:
				con.close()
			dbid = DBHelp.GetDBIDByRoleID(role_id)
			con = DBHelp.ConnectMasterDBByID(dbid)
		try:
			result.append((role_id, do_role(con, role_id, cmd)))
		except:
			result.append((role_id, AutoHTML.PyStringToHtml(traceback.format_exc())))
	if con is not None:
		con.close()
	return result

def do_role(con, role_id, cmd):
		with con as cur:
			cur.execute("select report_time, report_info from report_info where role_id = %s;", role_id)
			result = cur.fetchall()
			if not result:
				return "没有这个角色的上报信息！NO REPORT INFO FOR THIS USER!"
			report_time, report_info = result[0]
			report_info = eval(report_info)
			fun = globals()[cmd]
			result = fun(report_info)
			return "%s:%s" % (report_time, result)

def report(uri, get):
	host = "tencentlog.com"
	url = "http://%s:%s%s?%s" % (host, 80, uri, urllib.urlencode(get))
	response = urllib2.urlopen(url).read()
	return response

def l(info):
	get = {"appid":QQHttp.APP_ID, "userip":info["userip"], "svrip":QQHttp.IIP(),
		"domain":info["domain"], "worldid":info["worldid"], "opuid":int(info["opuid"]),
		"opopenid":info["opopenid"], "source":info["source"], "level":info["level"], "time":int(time.time())}
	return report("/stat/report_login.php", get)

def q(info):
	get = {"appid":QQHttp.APP_ID, "userip":info["userip"], "svrip":QQHttp.IIP(),
		"domain":info["domain"], "worldid":info["worldid"], "opuid":int(info["opuid"]),
		"opopenid":info["opopenid"], "source":info["source"], "time":int(time.time()),
		"level":info["level"], "onlinetime":random.randint(300, 1234)}
	return report("/stat/report_quit.php", get)

def lq(info):
	r1 = l(info)
	r2 = q(info)
	return "%s-%s" %(r1, r2)

Permission.reg_develop(Reg)
Permission.reg_public(Res)
