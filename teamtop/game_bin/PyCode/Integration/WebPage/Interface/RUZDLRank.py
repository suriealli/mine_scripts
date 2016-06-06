#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.Interface.RUZDLRank")
#===============================================================================
# 俄罗斯战斗力排行榜
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

KEY = "add6#47jk&fafsd#fasfggg"

def Req_ZDLRank(request):
	'''
	【接口】--俄罗斯获取战斗力排行榜
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
		me.say(request,"俄罗斯获取战斗力排行榜"),
		AutoHTML.GetURL(Res_ZDLRank),
		table.ToHtml(),
		me.say(request,"获取")
	)
	return HttpResponse(html)
	
def Res_ZDLRank(request):
	serverid = AutoHTML.AsInt(request.GET, "serverid")
	sign = md5.new("%s%s" % (serverid, KEY)).hexdigest()
	d = {"serverid": serverid,
		"sign" : sign,
		}
	return _ZDLRankBack(OtherHelp.Request(d))

def ZDLRankBack(request):
	return OtherHelp.Apply(_ZDLRankBack, request, __name__)

def _ZDLRankBack(request):
	serverid = AutoHTML.AsInt(request.GET, "serverid")
	sign = AutoHTML.AsString(request.GET, "sign")
	
	#验证签名
	if sign != md5.new("%s%s" % (serverid, KEY)).hexdigest():
		return HttpResponse(Http_Define.ErrorSign)
	
	con = DBHelp.ConnecMianZoneMasterDBByID(serverid)
	if not con:
		return HttpResponse("serverid error")
	rank = GetRank(con)
	#取前10
	rank = rank[:10]
	#返回列表
	res_rank = []
	for data in rank:
		#roleid, name zdl level
		res_rank.append({"RoleId" : str(data[0]), "RoleName" : data[1], "roleZDL":data[2], "roleLevel": data[3]})
	return HttpResponse(json.dumps(res_rank))
	
def GetRank(con):
	with con as cur:
		cur.execute("select data from sys_persistence where per_key = 'Rank_ZDL';")
		result = cur.fetchall()
		if not result:
			return []
		data = Serialize.String2PyObj(result[0][0])
		l = []
		LA = l.append
		#(name, level, zdl, flower, roleId)
		for roleid, d in data.iteritems():
			print d
			#roleid, name zdl level
			LA((roleid, d[0], d[2], d[1]))
		l.sort(key = lambda it:(it[1], it[2]), reverse = True)
		return l

Permission.reg_develop(Req_ZDLRank)
Permission.reg_develop(Res_ZDLRank)
Permission.reg_public(ZDLRankBack)

