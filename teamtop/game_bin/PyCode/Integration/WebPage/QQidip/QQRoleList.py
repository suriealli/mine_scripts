#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.QQidip.QQRoleList")
#===============================================================================
# 角色列表
#===============================================================================
from ComplexServer.Plug.DB import DBHelp


'''
"RoleList_count" : ,    /* 角色列表的最大数量 */
"RoleList" :            /* 角色列表 */
[
	{
	"RoleId" : "",      /* 角色ID */
	"RoleName" : ""     /* 角色名 */
	}
]'''

SQL = "select role_id, role_name from role_data where account = %s;"

#正式接口
def RoleList(request):
	serverid = request.BodyGet("AreaId")
	Uin = request.BodyGet("Uin")
	if not serverid or not Uin:
		return 
	con = DBHelp.ConnectMasterDBByID_HasExcept(serverid)
	if not con:
		con = DBHelp.ConnectMasterDBByID_Union_HasExcept(serverid)
		if not con:
			return request.ErrorResponse(-1007, "area error")
	with con as cur:
		cur.execute(SQL, Uin)
		result = cur.fetchall()
		if not result:
			#查询不到角色
			return request.response({}, 1)
			
		RoleId, RoleName = result[0]
		RoleList = [{'RoleId': str(RoleId), 'RoleName' :RoleName}]
		return request.response({"RoleList_count": 1, "RoleList" : RoleList})


