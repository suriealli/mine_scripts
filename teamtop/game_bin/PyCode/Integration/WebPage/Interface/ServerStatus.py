#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.Interface.ServerStatus")
#===============================================================================
# 第三方查询服务器状态接口
#===============================================================================
from django.http import HttpResponse
from Integration import AutoHTML
from Integration.Help import OtherHelp, Concurrent
from Integration.WebPage.User import Permission
from Integration.WebPage.model import me


def Test_ServerStatus(request):
	'''
	【接口】--服务器状态
	'''
	return HttpResponse(
		html%(
			me.say(request,'查询服务器状态'),
			AutoHTML.GetURL(ServerStatus),
			me.say(request,'服务器ID'),
			me.say(request,'查询')
		)
	)

def ServerStatus(request):
	return OtherHelp.Apply(_ServerStatus, request, __name__)


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
</html>'''



def _ServerStatus(request):
	# 获取参数
	serverid = AutoHTML.AsInt(request.GET, "sid")
	pkey = "GHL" + str(serverid)
	gmresult = Concurrent.GMCommand(pkey, "print 1")
	if gmresult == "1\n":
		return HttpResponse("0")
	else:
		return AutoHTML.Error


Permission.reg_develop(Test_ServerStatus)
Permission.reg_public(ServerStatus)
