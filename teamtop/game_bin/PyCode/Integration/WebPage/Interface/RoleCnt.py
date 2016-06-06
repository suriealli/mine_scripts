#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.Interface.RoleCnt")
#===============================================================================
# 第三方查询角色人数接口
#===============================================================================
from ComplexServer.API import Define
from django.http import HttpResponse
from Integration import AutoHTML
from Integration.Help import OtherHelp, Concurrent
from Integration.WebPage.User import Permission
from Integration.WebPage.model import me

def Test_RoleCnt(request):
	'''
	【接口】--服务器角色数
	'''
	html = '''
	<html>
	<head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
	<title>%s</title>
	</head>
	<body>
	<form action="%s" method="GET" target="_blank">
	%s：<input type="text" name="sid">
	<input type="submit" value="%s" />
	</form>
	</body>
	</html>''' % (me.say(request,'查询角色人数'),AutoHTML.GetURL(RoleCnt),me.say(request,'服务器ID'),me.say(request,'查询'))
	return HttpResponse(html)

def RoleCnt(request):
	return OtherHelp.Apply(_RoleCnt, request, __name__)



def _RoleCnt(request):
	# 获取参数
	serverid = AutoHTML.AsInt(request.GET, "sid")
	pkey = "GHL" + str(serverid)
	gmresult = Concurrent.GMCommand(pkey, "import Game.Role.RoleMgr as M;print len(M.RoleID_Role),")
	if type(gmresult) is str and gmresult.isdigit():
		return HttpResponse(gmresult)
	else:
		return HttpResponse("%s_%s" % (Define.Error, str(gmresult)))

Permission.reg_develop(Test_RoleCnt)
Permission.reg_public(RoleCnt)
