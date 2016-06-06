#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.QQidip.QQOpenID")
#===============================================================================
# 查询OPENID
#===============================================================================
from ComplexServer.Plug.DB import DBHelp


SQL = "select role_id from role_data where account = %s;"

#正式接口
def OpenID(request):
	serverid = request.BodyGet("AreaId")
	OpenId = request.BodyGet("OpenId")
	con = DBHelp.ConnectMasterDBByID_HasExcept(serverid)
	if not con:
		con = DBHelp.ConnectMasterDBByID_Union_HasExcept(serverid)
		if not con:
			return request.ErrorResponse(-1007, "area error")
	with con as cur:
		cur.execute(SQL, OpenId)
		result = cur.fetchall()
		if not result:
			#查询不到角色
			return request.response({}, 1)
		
		return request.response({"Uin" : OpenId})
