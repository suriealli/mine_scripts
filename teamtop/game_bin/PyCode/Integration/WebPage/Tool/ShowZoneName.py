#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.Tool.ShowZoneName")
#===============================================================================
# 导出游戏区名字信息
#===============================================================================
from django.http import HttpResponse
from ComplexServer.Plug.DB import DBHelp
from Integration import AutoHTML
from Integration.WebPage.User import Permission
from Integration.Help import OtherHelp

html = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>导出游戏区名字信息</title>
</head>
<body>
%s<br>
</body>
</html>'''

def ShowZoneName(request):
	'''【测试】--导出游戏区名字信息'''
	con = DBHelp.ConnectGlobalWeb()
	zoneShow = AutoHTML.Table(["zoneId", "zoneName"], [], "区名字信息")
	
	with con as cur:
		cur.execute("select zid, name from zone;")
		for zid, zname in cur.fetchall():
			zoneShow.body.append((zid, zname))
	zoneShow.body.sort()
	zoneShow.body.insert(0, ("区ID", "区名字"))
	return HttpResponse(html % (zoneShow.ToHtml()))


def GetZoneName(request):
	return OtherHelp.Apply(_GetZoneName, request, __name__)



def _GetZoneName(request):
	con = DBHelp.ConnectGlobalWeb()
	zones = {}
	with con as cur:
		cur.execute("select zid, name from zone;")
		for zid, zname in cur.fetchall():
			zones[zid] = zname
	return zones

def GetZoneNameEx(request):
	return OtherHelp.Apply(_GetZoneNameEx, request, __name__)

def _GetZoneNameEx(request):
	con = DBHelp.ConnectGlobalWeb()
	zones = {}
	zoneIds = AutoHTML.AsString(request.GET, "zoneids")
	zoneIds = eval(zoneIds)
	for zoneId in zoneIds:
		with con as cur:
			cur.execute("select zid, name from zone where zid = %s;", zoneId)
			for zid, zname in cur.fetchall():
				zones[zid] = zname
	return zones


Permission.reg_develop(ShowZoneName)
Permission.reg_public(GetZoneName)
Permission.reg_public(GetZoneNameEx)

