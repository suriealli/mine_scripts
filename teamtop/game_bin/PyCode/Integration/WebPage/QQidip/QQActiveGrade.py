#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.QQidip.QQActiveGrade")
#===============================================================================
# 查询活跃度(每日必做积分)
#===============================================================================
import struct
from ComplexServer.Plug.DB import DBHelp
from Common import Serialize
from Game.Role.Data import EnumInt16


SQL = "select array from role_data where role_id = %s;"

#正式接口
def ActiveGrade(request):
	serverid = request.BodyGet( "AreaId")
	RoleId = request.BodyGet("RoleId")
	con = DBHelp.ConnectMasterDBByID_HasExcept(serverid)
	if not con:
		con = DBHelp.ConnectMasterDBByID_Union_HasExcept(serverid)
		if not con:
			return request.ErrorResponse(-1007, "area error")
	with con as cur:
		cur.execute(SQL, RoleId)
		result = cur.fetchall()
		if not result:
			#查询不到角色
			return request.response({}, 1)
		
		array = result[0][0]
		array = Serialize.String2PyObjEx(array)
		i16 = struct.unpack("h" * (len(array[2]) / 2), array[2])
		Num = i16[EnumInt16.DailyDoScore]
		return request.response({"Num" : Num})

