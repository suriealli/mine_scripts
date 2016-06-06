#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.QQidip.QQOnline")
#===============================================================================
# 腾讯查询服务器在线
#===============================================================================
import datetime
from ComplexServer.Plug.DB import DBHelp
from Common import Serialize

'''
	"body" :
	{
		"AreaId" :	  /* 所在大区ID */
	}
	"body" :
    {
        "CurRegNum" : ,    /* 已注册人数 */
        "MaxOnline" : ,    /* 最大在线人数 */
        "Online" :         /* 当前在线人数 */
    }
'''

SQL_Online = "select roles from online_info order by sta_time desc limit 1;"
SQl_MaxOnline = 'select max(roles) from `online_info` where date_format(sta_time,"%%Y-%%m-%%d") between "%s" and "%s" '
SQL_NewRole = "select data from sys_persistence where per_key = 'world_data_notsync'; "

#正式接口
def Online(request):
	serverid = request.BodyGet("AreaId")
	con = DBHelp.ConnecMianZoneMasterDBByID(serverid)
	if not con:
		return request.ErrorResponse(-1007, "area error")
	date = str(datetime.datetime.now().date())
	OnlineCnt = 0
	MaxOnline = 0
	CurRegNum = 0
	with con as cur:
		cur.execute(SQL_Online)
		result = cur.fetchall()
		
		if result:
			OnlineCnt = result[0][0]
		SM = SQl_MaxOnline % (date, date)
		cur.execute(SM)
		result = cur.fetchall()
		
		if result:
			MaxOnline = result[0][0]
		
		cur.execute(SQL_NewRole)
		result = cur.fetchall()
		if result:
			data = Serialize.String2PyObj(result[0][0])
			CurRegNum = data.get(4, 0)
			
		return request.response({"Online":OnlineCnt, "MaxOnline":MaxOnline, "CurRegNum" : CurRegNum}, 0)


