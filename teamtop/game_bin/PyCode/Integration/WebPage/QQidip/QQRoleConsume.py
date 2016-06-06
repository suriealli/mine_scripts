#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.QQidip.QQRoleConsume")
#===============================================================================
# 角色消费信息
#===============================================================================
from ComplexServer.Plug.DB import DBHelp
from Common import Serialize
from Game.Role.Data import EnumObj

SQL = "select array from role_data where account = %s;"

def RoleConsume(request):
	serverid = request.BodyGet("AreaId")
	Uin = request.BodyGet("Uin")
	
	BeginTime = request.BodyGet("BeginTime")
	#EndTime = request.BodyGet("EndTime")
	
	con = DBHelp.ConnectMasterDBByID_HasExcept(serverid)
	if not con:
		con = DBHelp.ConnectMasterDBByID_Union_HasExcept(serverid)
		if not con:
			return request.ErrorResponse(-1007, "area error")
	
	startDays = (BeginTime + 28800) / 86400
	#endDays = (EndTime + 28800) / 86400
	Num = 0
	with con as cur:
		cur.execute(SQL, Uin)
		result = cur.fetchall()
		if not result:
			#查询不到角色
			return request.response({}, 1)
		array = result[0][0]
		array = Serialize.String2PyObjEx(array)
		roleObj = array[10]
		consumeDict = roleObj[EnumObj.QQidipRoleConsume]
		if consumeDict:
			for days, cnt in consumeDict.iteritems():
				if days < startDays:
					continue
				Num += cnt
	
	return request.response({"Num": Num})

