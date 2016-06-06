#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 删除区
#===============================================================================
from Integration import AutoHTML
from ComplexServer.Plug.DB import DBHelp
from django.http import HttpResponse
from Integration.WebPage.User import Permission
from Integration.WebPage.Global import Add

html = '''<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>删除一个区</title>
</head>
<body>
%s
<form action="%s" method="GET" target="_blank">
%s
<input type="submit" name="提交" />
</form>
</body>
</html>''' 

def Reg(request):
	'''【配置】--删除游戏区'''
	con = DBHelp.ConnectGlobalWeb()
	sel = AutoHTML.Select2()
	with con as cur:
		cur.execute("select zid, name from zone_tmp")
		for zid, zname in cur.fetchall():
			sel.Append(zname, zid)
	
	cp = '''<iframe  src='%s'  style="width:100%%;height:50px""  frameborder="0" marginwidth="0" marginheight="0"></iframe><br><hr>'''%AutoHTML.GetURL(Add.CopyTmpConfig)
	return HttpResponse(html % (cp, AutoHTML.GetURL(Res), sel.ToHtml()))

def Res(request):
	zid = AutoHTML.AsInt(request.GET, "sel")
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		cur.execute("select ztype, all_process_key, d_process_key, ghl_process_key from zone_tmp where zid = %s;", zid)
		result = cur.fetchall()
		if not result:
			return HttpResponse("不能删除服类型%s" % zid)
		ztype, all_process_key, d_process_key, ghl_process_key = result[0]
		if ztype == "Single":
			h1 = cur.execute("delete from zone_tmp where zid = %s;", zid)
			h2 = cur.execute("delete from process_tmp where pkey = %s;", all_process_key)
			return HttpResponse("删除单进程区%s-%s" % (h1, h2))
		if ztype == "Standard":
			h1 = cur.execute("delete from zone_tmp where zid = %s;", zid)
			h2 = cur.execute("delete from process_tmp where pkey = %s;", d_process_key)
			h3 = cur.execute("delete from process_tmp where pkey = %s;", ghl_process_key)
			return HttpResponse("删除标准区%s-%s-%s" % (h1, h2, h3))
		return HttpResponse("不能删除服类型%s" % ztype)

Permission.reg_develop(Reg)
Permission.reg_develop(Res)

