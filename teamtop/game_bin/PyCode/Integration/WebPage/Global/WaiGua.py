#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.Global.WaiGua")
#===============================================================================
# 注释
#===============================================================================
import Environment
from django.http import HttpResponse
from Integration.Help import OtherHelp
from Integration import AutoHTML
from World import Define
from ComplexServer.Plug.DB import DBHelp
from Integration.WebPage.User import Permission


def ReqWaiGua(request):
	'''【数据与工具】--查询外挂封号数据'''
	gd = AutoHTML.Table(["区ID", "区名", "角色帐号","角色ID", "角色名", "vip等级", "Q点", "使用外挂次数", "封号天数", "开始时间", "结束时间"], [], "外挂封号数据")
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		cur.execute("select pid, zone_name, account, role_id, role_name, viplevel, qpoint, usecounts, days, lock_start_datetime, lock_end_datetime from waigua_role;")
		result = cur.fetchall()
		if result:
			gd.body = list(result)
			gd.body.sort(key = lambda it:it[0], reverse = True)
		return HttpResponse(gd.ToHtml())


def WaiGuaRole(request):
	return OtherHelp.Apply(_WaiGuaRole, request, __name__)
	
def _WaiGuaRole(request):
	roleid = AutoHTML.AsInt(request.POST, "roleid")
	account = AutoHTML.AsString(request.POST, "account")
	name = AutoHTML.AsString(request.POST, "name")
	days = AutoHTML.AsInt(request.POST, "days")
	usecounts = AutoHTML.AsInt(request.POST, "usecounts")
	process_id = AutoHTML.AsInt(request.POST, "pid")
	zone_name = AutoHTML.AsString(request.POST, "zone_name")
	viplevel = AutoHTML.AsInt(request.POST, "viplevel")
	qp = AutoHTML.AsInt(request.POST, "qp")

	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		h = cur.execute("replace into waigua_role (pid, zone_name, account, role_id, role_name, viplevel, qpoint, days, usecounts, lock_start_datetime, lock_end_datetime) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, now(), now() + INTERVAL %s DAY);", (process_id, zone_name, account, roleid, name, viplevel, qp, days, usecounts, days))
	con.close()
	return h

Permission.reg_public(WaiGuaRole)
Permission.reg_public(_WaiGuaRole)
Permission.group([ReqWaiGua],['design','operate'])