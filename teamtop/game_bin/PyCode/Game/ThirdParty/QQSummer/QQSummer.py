#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQSummer.QQSummer")
#===============================================================================
# 暑期活动
#===============================================================================
import Environment
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Role.Data import EnumTempObj, EnumInt1
from ComplexServer.API import QQHttp

app_custom_Config = "QZ.HUODONG.SUMMERHOLIDAY"

systemError = "系统错误"
e0 = "无效uin"
e1 = "无效appid"
e2 = "无效taskid"
e3 = "无效sourceid"
e4 = "该app未上架"
e5 = "任务未开始"
e6 = "任务已经结束"
e7 = "任务不存在"
e8 = "任务已经完成"

ErrorCodeDict = {2000:e0,
				2001:e1,
				2002:e2,
				2003:e3,
				2004:e4,
				2005:e5,
				2006:e6,
				2007:e7,
				2008:e8,
				}

InitTaskId = 1001
LevelTaskIDDict = {10: 1002, 20:1003, 30:1004}

def FirstInitRole(role, param):
	'''
	角色初始化
	@param role:
	@param param:
	'''
	loginInfo = role.GetTempObj(EnumTempObj.LoginInfo)
	app_custom = loginInfo.get("app_custom", "")
	if not app_custom:
		return
	if app_custom_Config not in app_custom:
		return
	
	with TraQQSummerCreateRole:
		role.SetI1(EnumInt1.IsQQSummer, 1)
	openid = loginInfo["account"]
	pf = loginInfo["pf"]
	userip = loginInfo["userip"]
	openkey = loginInfo["openkey"]
	QQHttp.summer_task(openid, openkey, pf, userip, InitTaskId, AfterSummerTaskBack, (role.GetRoleID(), InitTaskId, role.GetLevel()))


def AfterLevelUp(role, param):
	'''
	角色升级
	@param role:
	@param param:
	'''
	loginInfo = role.GetTempObj(EnumTempObj.LoginInfo)
	app_custom = loginInfo.get("app_custom", "")
	if not app_custom:
		return
	if app_custom_Config not in app_custom:
		return
	pf = loginInfo["pf"]
	if pf != "qzone":
		return
	if not role.GetI1(EnumInt1.IsQQSummer):
		return
	taskID = LevelTaskIDDict.get(role.GetLevel())
	if not taskID:
		return
	openid = loginInfo["account"]
	
	userip = loginInfo["userip"]
	openkey = loginInfo["openkey"]
	QQHttp.summer_task(openid, openkey, pf, userip, taskID, AfterSummerTaskBack, (role.GetRoleID(), taskID, role.GetLevel()))


def AfterSummerTaskBack(response, regparam):
	code, body = response
	if code != 200:
		print "GE_EXC, AfterSummerTaskBack code error ",response
		return
	if not body:
		print "GE_EXC AfterSummerTaskBack error not body", response
		return
	result = eval(body)
	code = result.get("code")
	if code != 0:
		errormsg = ErrorCodeDict.get(code, result.get("message"))
		print "GE_EXC, AfterSummerTaskBack error code(%s) message(%s)" % (code, errormsg)
		return
	if regparam[1] == InitTaskId:
		return
	roleId, taskId, rolelevel = regparam
	with TraQQSummerLevel:
		AutoLog.LogValue(roleId, AutoLog.eveQQSummerLevel, rolelevel, rolelevel, taskId)


if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.EnvIsQQ() or Environment.IsDevelop) and (not Environment.IsCross):
		Event.RegEvent(Event.Eve_AfterLevelUp, AfterLevelUp)
		Event.RegEvent(Event.Eve_FirstInitRole, FirstInitRole)
		TraQQSummerCreateRole = AutoLog.AutoTransaction("TraQQSummerCreateRole", "QQ空间暑期活动创建角色日志")
		TraQQSummerLevel = AutoLog.AutoTransaction("TraQQSummerLevel", "QQ空间暑期活动升级日志")
		