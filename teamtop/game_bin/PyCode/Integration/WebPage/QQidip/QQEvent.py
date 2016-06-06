#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.QQidip.QQEvent")
#===============================================================================
# 查询事件完成情况
#===============================================================================
from ComplexServer.Plug.DB import DBHelp


#任务id	事件
#1	巨龙宝藏
#2	心魔炼狱
#3	组队爬塔
#4	情缘副本
#5	许愿池
#6	经验日常
#7	体力日常
#8	炼金
#9	竞技场
#10	答题
#11	魔兽入侵
#12	城主轮值
#13	荣耀之战


#	"body" :
#	{
#		"IsFinish" :	  /* 完成/未完成 */ #0已经完成  1，未完成   2，不存在这个事件
#		"FinishNum" :      /* 任务完成次数 */
#	}

SQL = "select event_num from qq_idip_event where role_id =%s and event_id=%s  and (DATEDIFF(event_time, NOW())=0); "
SQL_Role = "select role_id from role_data where role_id = %s;"

#正式接口
def Event(request):
	serverid = request.BodyGet("AreaId")
	role_id = request.BodyGet("RoleId")
	EventId = request.BodyGet("EventId")
	isFinish = 1 
	finishCnt = 0
	con = DBHelp.ConnectMasterDBByID_HasExcept(serverid)
	if not con:
		con = DBHelp.ConnectMasterDBByID_Union_HasExcept(serverid)
		if not con:
			return request.ErrorResponse(-1007, "area error")
	
	if EventId < 1  or EventId > 13:
		return request.ErrorResponse(-1011, "event error ")
	
	with con as cur:
		cur.execute(SQL_Role, role_id)
		result = cur.fetchall()
		if not result:
			#查询不到角色
			return request.response({}, 1)
		
		cur.execute(SQL, (role_id, EventId))
		result = cur.fetchall()
		if not result:
			#查询不到角色
			finishCnt = 0
		else:
			isFinish = 0 
			finishCnt = result[0][0]
	
	return request.response({"IsFinish":isFinish, "FinishNum":finishCnt})




