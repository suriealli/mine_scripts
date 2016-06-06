#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 显示权限
#===============================================================================
import Environment
from django.http import HttpResponse
from Integration.WebPage.User import Permission

html = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>后台信息</title>
</head>
<body>
%s<br>
</body>
</html>'''

def Req(request):
	'''
	【用户】后台信息
	'''
	from Integration import AutoHTML, AutoURL
	title = ["IP:%s" % Environment.IP]
	for group in request.session.get("permission", set()):
		title.append(group)
	for name in dir(Environment):
		if not name.startswith("Is"):
			continue
		if getattr(Environment, name):
			title.append(name)
	title = " ".join(title)
	table = AutoHTML.Table(["匹配项", "权限", "说明", "模块", "函数"], [], title)
	kv = AutoURL.auto_patterns.items()
	kv.sort(key=lambda it:it[0])
	for parttern, handle in kv:
		permission = []
		pub = False
		if handle.url in Permission.public:
			permission.append("公共")
			pub = True
		if handle.url in Permission.develop:
			permission.append("开发")
		if handle.url in Permission.operate:
			permission.append("运营")
		if handle.url in Permission.design:
			permission.append("策划")
		if handle.url in Permission.host:
			permission.append("管理")
		if Permission.check(request, handle.url):
			parttern = "<font color='blue'>%s</font>" % parttern
		if pub:
			permission = "<font color='red'>%s</font>" % ", ".join(permission)
		else:
			permission = ", ".join(permission)
		table.body.append((parttern, permission, handle.fun.__doc__, handle.fun.__module__, handle.fun.__name__))
	return HttpResponse(html % table.ToHtml())

Permission.reg_develop(Req)

