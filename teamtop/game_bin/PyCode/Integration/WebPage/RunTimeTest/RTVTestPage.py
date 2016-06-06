#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.RunTimeTest.RTVTestPage")
#===============================================================================
# 注释
#===============================================================================
from django.http import HttpResponse
from Game.Persistence import Base
from Integration import AutoHTML
from Integration.Help import Concurrent, WorldHelp
from Integration.WebPage.User import Permission
from World import Define

def Req(request):
	'''
	【测试】--模拟服查看数据
	'''
	return HttpResponse(html)

C1 = '''from ThirdLib import PrintHelp
from Game.Persistence import Base
PrintHelp.pprint(Base.KeyDict["%s"].data)
'''
C2 = '''from ThirdLib import PrintHelp
import sys
module = sys.modules["%s"]
obj = getattr(module, "%s")
PrintHelp.pprint(obj)
'''
def Res(request):
	pkeys = AutoHTML.AsProcessKeys(request.POST)
	modulename, varname =  sel.GetValue(request.POST)
	if modulename is None:
		command = C1 % varname
	else:
		command = C2 % (modulename, varname)
	
	tg = Concurrent.TaskGroup()
	pc = WorldHelp.GetProcess()
	for pkey in pkeys:
		pcobj = pc.get(pkey)
		if not pcobj:
			continue
		if pcobj.pid not in Define.TestWorldIDs:
			continue
		tg.append(Concurrent.GMTask(pkey, command))
	tg.execute()
	return HttpResponse(tg.to_html(WorldHelp.GetFullNameByProcessKey, WorldHelp.CmpProcessKey))

sel = AutoHTML.Select()
for key in Base.KeyDict.iterkeys():
	sel.Append("持久化数据-%s" % key, (None, key))
html = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>查看数据</title>
</head>
<body>
<form action="%s" method="POST" target="_blank">
%s
<br><br>
%s
<input type="submit" name="提交" />
</form>
</body>
</html>''' % (AutoHTML.GetURL(Res), AutoHTML.ToProcessTest(), sel.ToHtml())


Permission.reg_design(Req)
Permission.reg_design(Res)