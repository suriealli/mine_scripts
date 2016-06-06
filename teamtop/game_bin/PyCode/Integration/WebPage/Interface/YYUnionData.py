#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.Interface.YYUnionData")
#===============================================================================
# YY线上公会数据接口
#===============================================================================
import time
import md5
import json
import struct
from django.http import HttpResponse
from Integration.Help import OtherHelp
from Integration import AutoHTML
from Integration.WebPage.User import Permission
from Integration.WebPage.model import me
from ComplexServer.Plug.DB import DBHelp
from ComplexServer.API import Define as Http_Define
from Game.Role.Data import EnumInt32
from Common import Serialize

ALLINFO_KEY = "Union_AllInfo#_0dod#_dfgg"
UNION_KEY = "Union_Info_fg0o8#f_ojd"
ROLE_KEY = "RoleUnion_Info_#df97j_dfu0o#1"

#http://127.0.0.1:8000/Interface/YYUnionData/Req_YYUnionInfo/?index=3&server=108&game=1&account=1&roleId=463856468603&roleName=dfd
def Req_YYUnionInfo(request):
	'''
	【接口】--YY公会查询
	'''
	table = AutoHTML.Table([
		me.say(request,"选择(1.查全服，2.公会人数，3.角色公会)"),
		"<input type='text' name='index'>"
	])
	table.body.append([
		me.say(request,"区"),
		"<input type='text' name='server'>"
	])
	table.body.append([
		me.say(request,"游戏编号"),
		"<input type='text' name='game'>"
	])
	table.body.append([
		me.say(request,"公会id(查询公会人数)"),
		"<input type='text' name='guildId'>"
	])
	table.body.append([
		me.say(request,"帐号(查询玩家公会)"),
		"<input type='text' name='account'>"
	])
	table.body.append([
		me.say(request,"角色ID(查询玩家公会)"),
		"<input type='text' name='roleId'>"
	])
	table.body.append([
		me.say(request,"角色名(查询玩家公会)"),
		"<input type='text' name='roleName'>"
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
		me.say(request,"YY公会信息"),
		AutoHTML.GetURL(Res_YYUnionInfo),
		table.ToHtml(),
		me.say(request,"查询")
	)
	return HttpResponse(html)

def Res_YYUnionInfo(request):
	index = AutoHTML.AsInt(request.GET, "index")
	game = AutoHTML.AsString(request.GET, "game")
	server = AutoHTML.AsInt(request.GET, "server")
	guildId = AutoHTML.AsInt(request.GET, "guildId")
	roleId = AutoHTML.AsString(request.GET, "roleId")
	roleName = AutoHTML.AsString(request.GET, "roleName")
	account = AutoHTML.AsString(request.GET, "account")
	unixtime = int(time.time())
	if index == 1:
		sign = md5.new("%s%s%s%s" % (game,server,unixtime,ALLINFO_KEY)).hexdigest()
		d = {"time":unixtime,
			"game":game,
			"server":server,
			"sign" : sign,
			}
		return _YYUnionAllInfo(OtherHelp.Request(d))
	elif index == 2:
		sign = md5.new("%s%s%s%s%s" % (game,server,guildId,unixtime,UNION_KEY)).hexdigest()
		d = {"time":unixtime,
			"game":game,
			"server":server,
			"sign" : sign,
			"guildId" : guildId
			}
		return _YYUnionInfo(OtherHelp.Request(d))
	elif index == 3:
		sign = md5.new("%s%s%s%s%s%s%s" % (account,game,server,roleId,roleName,unixtime,ROLE_KEY)).hexdigest()
		d = {"time":unixtime,
			"game":game,
			"server":server,
			"sign" : sign,
			"roleId" : roleId,
			"roleName":roleName,
			"account":account
			}
		return _YYRoleUInfo(OtherHelp.Request(d))
	
def YYUnionAllInfo(request):
	return OtherHelp.Apply(_YYUnionAllInfo, request, __name__)

def _YYUnionAllInfo(request):
	game = AutoHTML.AsString(request.GET, 'game')
	server = AutoHTML.AsString(request.GET, 'server')
	unixtime = AutoHTML.AsInt(request.GET, 'time')
	sign = AutoHTML.AsString(request.GET, 'sign')
	
	#验证时间
	if abs(time.time() - unixtime) > 900:
		return HttpResponse(json.dumps({"message":Http_Define.ErrorTime}))
	#签名验证
	if sign != md5.new("%s%s%s%s" % (game,server,unixtime,ALLINFO_KEY)).hexdigest():
		return HttpResponse(json.dumps({"message":Http_Define.ErrorSign}))
	
	con = DBHelp.ConnectMasterDBByID_HasExcept(server)
	if not con:
		return HttpResponse(json.dumps({"message":Http_Define.ErrorServer}))
	
	with con as cur:
		cur.execute("select union_id, name from sys_union;")
		result = cur.fetchall()
		if not result:
			return HttpResponse(json.dumps({"message":Http_Define.Error}))
		unionData = []
		for unionid, name in result:
			guildId, guildName = unionid, name
			unionData.append(json.dumps({"guildId":guildId, "guildName":guildName}))
			
		return HttpResponse(json.dumps({"message":'ok', "status":200, "data":unionData}))

def YYUnionInfo(request):
	return OtherHelp.Apply(_YYUnionInfo, request, __name__)

def _YYUnionInfo(request):
	game = AutoHTML.AsString(request.GET, 'game')
	server = AutoHTML.AsInt(request.GET, 'server')
	unixtime = AutoHTML.AsInt(request.GET, 'time')
	sign = AutoHTML.AsString(request.GET, 'sign')
	guildId = AutoHTML.AsInt(request.GET, 'guildId')
	#验证时间
	if abs(time.time() - unixtime) > 900:
		return HttpResponse(json.dumps({"message":Http_Define.ErrorTime}))
	#签名验证
	if sign != md5.new("%s%s%s%s%s" % (game,server,guildId,unixtime,UNION_KEY)).hexdigest():
		return HttpResponse(json.dumps({"message":Http_Define.ErrorSign}))
	
	con = DBHelp.ConnectMasterDBByID_HasExcept(server)
	if not con:
		return HttpResponse(json.dumps({"message":Http_Define.ErrorServer}))
	
	with con as cur:
		cur.execute("select count(members) from sys_union where union_id = %s;" % guildId)
		result = cur.fetchall()
		if not result:
			return HttpResponse(json.dumps({"message":Http_Define.Error}))
		membersCnt = result[0][0]
		return HttpResponse(json.dumps({"message":'ok', "status":200, "data":[{"guildId":guildId, "headCount":membersCnt}]}))
	
def YYRoleUInfo(request):
	return OtherHelp.Apply(_YYRoleUInfo, request, __name__)

def _YYRoleUInfo(request):
	account = AutoHTML.AsInt(request.GET, 'account')
	game = AutoHTML.AsString(request.GET, 'game')
	server = AutoHTML.AsInt(request.GET, 'server')
	roleId = AutoHTML.AsString(request.GET, 'roleId')
	roleName = AutoHTML.AsString(request.GET, 'roleName')
	unixtime = AutoHTML.AsInt(request.GET, 'time')
	sign = AutoHTML.AsString(request.GET, 'sign')
	#验证时间
	if abs(time.time() - unixtime) > 900:
		return HttpResponse(json.dumps({"message":Http_Define.ErrorTime}))
	#签名验证
	if sign.lower() != md5.new("%s%s%s%s%s%s%s" % (account,game,server,roleId,roleName,unixtime,ROLE_KEY)).hexdigest():
		return HttpResponse(json.dumps({"message":Http_Define.ErrorSign}))
	
	con = DBHelp.ConnectMasterDBByID_HasExcept(server)
	if not con:
		return HttpResponse(json.dumps({"message":Http_Define.ErrorServer}))
	
	with con as cur:
		cur.execute("select array from role_data where role_id = %s" % roleId)
		result = cur.fetchall()
		if not result:
			return HttpResponse(json.dumps({"message":Http_Define.Error}))
		unionId = 0
		for row in result:
			array = Serialize.String2PyObjEx(row[0])
			if array is None:
				continue
			i32 = struct.unpack("i" * (len(array[1]) / 4), array[1])
			unionId = i32[EnumInt32.UnionID]
		if not unionId:
			return HttpResponse(json.dumps({"message":'ok', "status":200, "data":[{"guildId":"", "guildIdName":"", "exists":'false'}]}))
		else:
			cur.execute("select name from sys_union where union_id = %s;" % unionId)
			result = cur.fetchall()
			if not result:
				return HttpResponse(json.dumps({"message":"union_error"}))
			unionName = result[0][0]
			return HttpResponse(json.dumps({"message":'ok', "status":200, "data":[{"guildId":unionId, "guildIdName":unionName, "exists":'true'}]}))
	
Permission.reg_develop(Req_YYUnionInfo)
Permission.reg_develop(Res_YYUnionInfo)
Permission.reg_public(YYUnionAllInfo)
Permission.reg_public(YYUnionInfo)
Permission.reg_public(YYRoleUInfo)