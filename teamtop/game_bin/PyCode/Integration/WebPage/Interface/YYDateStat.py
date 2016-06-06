#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.Interface.YYDateStat")
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

KEY = "YYDateStat_#ujhk0_iuj_7u"

def YYDateStat(request):
	Date = AutoHTML.AsString(request.GET, 'date')
	game = AutoHTML.AsString(request.GET, 'game')
	server = AutoHTML.AsString(request.GET, 'server')
	unixtime = AutoHTML.AsInt(request.GET, 'time')
	sign = AutoHTML.AsString(request.GET, 'sign')
	
	#验证时间
	if abs(time.time() - unixtime) > 900:
		return HttpResponse(json.dumps({"retcode" : -1}))
	
	#签名验证
	if sign.lower() != md5.new("%s%s%s%s" % (game,server,unixtime,KEY)).hexdigest():
		return HttpResponse(json.dumps({"retcode" : -1}))
	
	
	con = DBHelp.ConnectMasterDBByID_HasExcept(server)
	if not con:
		return HttpResponse(json.dumps({"retcode" : -3}))
	
	SQL_roleTotal = 'select count(role_id) as roleTotal from role_data where date_format(from_unixtime(di32_10),"%%Y%%m%%d")="%s"' % (Date)
	SQL_loginTotal = 'select count(account) as loginTotal from login_info where date_format(login_day,"%%Y%%m%%d")="%s"' % (Date)
	SQL_maxOnline = 'select max(roles) as maxOnline from online_info where date_format(sta_time,"%%Y%%m%%d")="%s"' % (Date)
	with con as cur:
		# roleTotal
		cur.execute(SQL_roleTotal)
		result = cur.fetchall()
		if not result:
			return HttpResponse(json.dumps({"retcode" : -2}))
		roleTotal = result[0][0]

		# loginTotal
		cur.execute(SQL_loginTotal)
		result = cur.fetchall()
		if not result:
			return HttpResponse(json.dumps({"retcode" : -2}))
		loginTotal = result[0][0]

		# maxOnline
		cur.execute(SQL_maxOnline)
		result = cur.fetchall()
		if not result:
			return HttpResponse(json.dumps({"retcode" : -2}))
		maxOnline = result[0][0]
		
		return HttpResponse(
			json.dumps({
				"retcode" : 1,
				"data":{
					"roleTotal":roleTotal,
					"loginTotal":loginTotal,
					"maxOnline":maxOnline
				}
			})
		)

Permission.reg_public(YYDateStat)