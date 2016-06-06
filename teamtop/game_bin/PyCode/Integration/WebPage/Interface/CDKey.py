#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 激活CDKey
#===============================================================================
import os
import uuid
import datetime
from django.http import HttpResponse
from ComplexServer.Plug.DB import DBHelp
from Game.CDKey import CDKey
from Integration import AutoHTML, settings
from Integration.Help import OtherHelp
from Integration.WebPage.User import Permission
from Integration.WebPage.model import me


def ActivateCDKey(request):
	return OtherHelp.Apply(_ActivateCDKey, request, "ActivateCDKey.log")

def _ActivateCDKey(request):
	roleid = AutoHTML.AsString(request.GET, "roleid")
	cdkey = AutoHTML.AsString(request.GET, "cdkey")
	# 没有该类CDKEY
	config = CDKey.GetConfig(cdkey)
	if not config:
		return HttpResponse("1")
	
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		if cur.execute("update cdkey_%s set role_id = %s, activaty_datetime = now() where cdkey = '%s' and role_id = 0;" % (config.special, roleid, cdkey)):
			return HttpResponse("0")
		else:
			return HttpResponse("2")

def BuildCDKeySel():
	cdkeys = []
	for config in CDKey.CKC.itervalues():
		cdkeys.append((config.name, config.special))
	
	cdkeys.sort(key = lambda it:it[1])
	sel = AutoHTML.Select()
	for name, special in cdkeys:
		sel.Append(special + "--" + name, special)
	return sel

def Req(request):
	'''
	【接口】--创建CDKEY
	'''
	sel = BuildCDKeySel()
	html = '''
	<html>
	<head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
	<title>%s</title>
	</head>
	<body>
	<form  action="%s" method="get" target="_blank">
	%s
	%s<input type="text" name="cnt" value="0"><br>
	<input type="submit" value="%s">
	</form>
	</body>
	</html>
	'''  % (
		me.say(request,"生成CD-KEY"),
		AutoHTML.GetURL(Res),
		sel.ToHtml(),
		me.say(request,"创建数量/个"),
		me.say(request,"创建")
	)
	return HttpResponse(html)

def Res(request):
	sel = BuildCDKeySel()
	special = sel.GetValue(request.GET)
	cnt = AutoHTML.AsInt(request.GET, "cnt")
	
	if cnt > 100000:
		return HttpResponse(
			me.say(request,"数量太多了")
		)
	
	if cnt < 100:
		cdkeys = CreateCDKey(special, cnt)
		return HttpResponse("<br>".join(cdkeys))
	else:
		now = datetime.datetime.now()
		file_name = "%s_%s_%s_%s_%s_%s_%s.txt" % (special, now.year, now.month, now.day, now.hour, now.minute, now.second)
		with open(settings.static_floder + os.sep + file_name, "w") as f:
			for _ in xrange(cnt / 5000 + 1):
				for cdkey in CreateCDKey(special, 5000):
					f.write(cdkey)
					f.write("\n")
		return HttpResponse("%s<a href='/site_medias/%s'>%s</a>" % (
			me.say(request,"速度下载，可能会没了。。。"),
			file_name,	
			file_name
		))

def CreateCDKey(special, cnt):
	cdkeys = []
	for _ in xrange(cnt):
		cdkeys.append("%s-%s" % (special, str(uuid.uuid4())))
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		if cur.executemany("insert into cdkey_" + special + " (cdkey) values(%s);", cdkeys):
			return cdkeys
		else:
			return []



Permission.reg_develop(Req)
Permission.reg_develop(Res)
Permission.reg_public(ActivateCDKey)
Permission.reg_log(Res)

