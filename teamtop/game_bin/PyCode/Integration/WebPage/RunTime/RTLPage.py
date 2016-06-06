#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 运行时登录信息
#===============================================================================
from Integration import AutoHTML
from django.http import HttpResponse
from Integration.Help import Concurrent
from Integration.WebPage.User import Permission

def Req(request):
	'''
	【工具】--登录信息
	'''
	return HttpResponse(html)

def Res(request):
	pkeys = AutoHTML.AsProcessKeys(request.POST)
	role_name = AutoHTML.AsString(request.POST, "role_name")
	if len(pkeys) != 1:
		return HttpResponse("只能选择一个进程！")
	pkey = pkeys[0]
	s = Concurrent.GMCommand(pkey, command % role_name)
	return HttpResponse(AutoHTML.PyStringToHtml(s))

command = '''
import cRoleMgr
for role in cRoleMgr.GetAllRole():
	if role.GetRoleName() == "%s":
		pprint(role.GetTempObj(0))
'''

html = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>GM指令</title>
</head>
<body>
<form action="%s" method="POST" target="_blank">
%s
<br><br>
角色名:<input type="text" id="role_name" name="role_name"><br>
<input type="submit" name="提交" />
</form>
</body>
</html>''' % (AutoHTML.GetURL(Res), AutoHTML.ToProcess())


Permission.reg_design(Req)
Permission.reg_design(Res)
