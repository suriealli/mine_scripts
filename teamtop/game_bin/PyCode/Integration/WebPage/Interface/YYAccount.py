#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.Interface.YYAccount")
#===============================================================================
# YY--日统计
#===============================================================================
import time
import md5
import json
from django.http import HttpResponse
from Integration import AutoHTML
from Integration.WebPage.User import Permission
from ComplexServer.Plug.DB import DBHelp

KEY = "YYAccount_@dsefs0_idws_3r"

def checkByName(request):
	Name = AutoHTML.AsString(request.GET, 'nickname')
	server = AutoHTML.AsString(request.GET, 'server')
	unixtime = AutoHTML.AsInt(request.GET, 'ts')
	sign = AutoHTML.AsString(request.GET, 'sign')
	
	#验证时间
	if abs(time.time() - unixtime) > 900:
		#print 'Time Expired!',abs(time.time() - unixtime)
		return HttpResponse(-2)
	
	#签名验证
	if sign.lower() != md5.new("%s%s%s%s" % (KEY,server,Name,unixtime)).hexdigest():
		#print 'Sign Not Valid!',abs(time.time() - unixtime)
		return HttpResponse(-2)
	
	
	con = DBHelp.ConnectMasterDBByID_HasExcept(server)
	if not con:
		return HttpResponse(-3)
	
	SQL = 'select account from role_data where role_name="%s"' % (Name)
	with con as cur:
		# roleTotal
		cur.execute(SQL)
		result = cur.fetchall()
		if not result:
			return HttpResponse(-1)
		Account = result[0][0]
		
		return HttpResponse(Account)

Permission.reg_public(checkByName)