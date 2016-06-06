#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.Tool.VersionAccount")
#===============================================================================
# 版本管理
#===============================================================================
import md5
import Environment
from Integration import AutoHTML
from ComplexServer.Plug.DB import DBHelp
from django.http import HttpResponse
from Integration.WebPage.User import Permission
from Integration.WebPage.model import me

if Environment.IsDevelop:
	def Req(request):
		'''【内网】--添加版本管理帐号'''
		account = AutoHTML.AsString(request.GET, "account")
		password = AutoHTML.AsString(request.GET, "password")
		password2 = AutoHTML.AsString(request.GET, "password2")
		if password2 != password:
			return HTMLEx(request)
		actype = AutoHTML.AsInt(request.GET, "actype")
		envs = AutoHTML.AsString(request.GET, "envs")
		password = str(md5.new(password).hexdigest())
		adminpassword = AutoHTML.AsString(request.GET, "adminpassword")
		adminpassword = str(md5.new(adminpassword).hexdigest())
		#longqishi
		if adminpassword != 'b22fc83340a75a5fe2b408f96d68fb20':
			return HTMLEx(request)
		if account and password and actype and envs:
			con = DBHelp.ConnectHouTaiWeb()
			with con as cur:
				print "ddd", account, password
				cur.execute("replace into version_tool(account, password, actype, envs) values(%s, %s, %s, %s);", (account, password, actype, envs))
				cur.close()
		
		return HTMLEx(request)
	


def HTMLEx(request):
	con = DBHelp.ConnectHouTaiWeb()
	with con as cur:
		cur.execute("select account, actype, envs from version_tool;")
		table = AutoHTML.Table([me.say(request,"帐号"),me.say(request,"帐号类型"), me.say(request,"可以管理的版本")], cur.fetchall())
		
	table2 = AutoHTML.Table([me.say(request,"帐号"),"<input type='text' name='account'>"])
	table2.body.append([me.say(request,"密码"),"<input type='text' name='password'>"])
	table2.body.append([me.say(request,"再次输入密码"),"<input type='text' name='password2'>"])
	table2.body.append([me.say(request,"帐号类型(0:啥权限都没，1:普通，2:超级)"),"<input type='text' name='actype'>"])
	table2.body.append([me.say(request,"可以管理的版本(列表形式['all', 'qq', 'na','rumsk', 'tk', 'pl', 'de', 'fr', 'en']之类的)"),"<input type='text' name='envs'>"])
	table2.body.append([me.say(request,"管理员密码"),"<input type='text' name='adminpassword'>"])
	
	html = '''
	<html>
	<head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
	<title>%s</title>
	</head>
	<body>
	%s
	<form action="%s" method="GET" target="_blank">
	%s
	<input type="submit" value="%s" />
	</form>
	</body>
	</html>'''%(
		me.say(request,"版本管理帐号"),
		table.ToHtml(),
		AutoHTML.GetURL(Req),
		table2.ToHtml(),
		me.say(request,"添加")
	)
	return HttpResponse(html)


if Environment.IsDevelop:
	Permission.reg_operate(Req)
