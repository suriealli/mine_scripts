#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.Interface.NALevelRank")
#===============================================================================
# 北美获取等级排行数据
#===============================================================================
import md5
import json
from django.http import HttpResponse
from Integration.Help import OtherHelp
from Integration import AutoHTML
from Integration.WebPage.User import Permission
from ComplexServer.Plug.DB import DBHelp
from ComplexServer.API import Define as Http_Define
from Common import Serialize
from Integration.WebPage.model import me

KEY = "a6#47jk&u_wde#ptz6H"

def Req_LevelRank(request):
	'''
	【接口】--北美获取等级排名
	'''
	table = AutoHTML.Table([
		me.say(request,"区"),
		"<input type='text' name='serverid'>"
	])
	html = '''
	<html>
	<head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
	<title>%s</title>
	</head>
	<body>
	<form action="%s" method="GET" target="_blank">
	%s
	<input type="submit" value="%s" />
	</form>
	</body>
	</html>''' % (
		me.say(request,"北美获取等级排名"),
		AutoHTML.GetURL(Res_LevelRank),
		table.ToHtml(),
		me.say(request,"获取")
	)
	return HttpResponse(html)
	
def Res_LevelRank(request):
	serverid = AutoHTML.AsInt(request.GET, "serverid")
	sign = md5.new("%s%s" % (serverid, KEY)).hexdigest()
	d = {"serverid": serverid,
		"sign" : sign,
		}
	return _LevelRankBack(OtherHelp.Request(d))

def LevelRankBack(request):
	return OtherHelp.Apply(_LevelRankBack, request, __name__)

def _LevelRankBack(request):
	serverid = AutoHTML.AsInt(request.GET, "serverid")
	sign = AutoHTML.AsString(request.GET, "sign")
	#验证签名
	if sign != md5.new("%s%s" % (serverid, KEY)).hexdigest():
		return HttpResponse(Http_Define.ErrorSign)
	
	con = DBHelp.ConnecMianZoneMasterDBByID(serverid)
	if not con:
		return HttpResponse("serverid error")
	rank = GetRank(con)
	#取前20
	rank = rank[:20]
	#返回列表
	res_rank = []
	for data in rank:
		res_rank.append({"RoleId" : str(data[0]), "RoleName" : data[1], "roleLevel": data[2], "roleZDL":data[3], "account":data[5]})
	return HttpResponse(json.dumps(res_rank))
	
def GetRank(con):
	with con as cur:
		cur.execute("select data from sys_persistence where per_key = 'Rank_Level';")
		result = cur.fetchall()
		if not result:
			return []
		data = Serialize.String2PyObj(result[0][0])
		l = []
		LA = l.append
		#(name, level, zdl, flower, exp,xxx, xxx, xxx,account)
		for roleid, d in data.iteritems():
			print d
			account = ""
			if len(d) >= 9:
				account = d[8]
			#roleid, name level zdl exp
			LA((roleid, d[0], d[1], d[2], d[4], account))
		l.sort(key = lambda it:(it[2], it[4]), reverse = True)
		return l
	

Permission.reg_develop(Req_LevelRank)
Permission.reg_develop(Res_LevelRank)
Permission.reg_public(LevelRankBack)