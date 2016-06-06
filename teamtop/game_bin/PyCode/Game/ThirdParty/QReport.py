#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QReport")
#===============================================================================
# 腾讯罗盘上报模块
#===============================================================================
import copy
import Environment
import cRoleMgr
#import cDateTime
import cComplexServer
from ComplexServer.API import QQHttp
from ComplexServer.Plug.DB import DBProxy
from Game.Role import Event
from Game.Role.Data import EnumTempObj, EnumTempInt64
#from Game.Persistence import Contain
from Game.ThirdParty import QQLog
from Game.SysData import WorldDataNotSync


RoleLoginTick = {}

if "_HasLoad" not in dir():
	Report_Minutes = 0
	Pf_RoleSet = set()
	Pf_RoleCnt_Dict = {}
	
	NowDayChargeDataDict = None


def UpLoadReport(roleid, get, login_info):
	copydict = copy.deepcopy(login_info)
	del copydict["ClientKey"]
	DBProxy.DBRoleVisit(roleid, "Info_Report", (roleid, get, copydict))

def AfterLogin(role, param):
	if not Environment.EnvIsQQ():
		return
	login_info = role.GetTempObj(EnumTempObj.LoginInfo)
	openid = login_info["account"]
	pf = login_info["pf"]
	via = login_info.get("via", "")
	source = "%s.%s" % (pf, via)
	userip = login_info["userip"]
	roleid = role.GetRoleID()
	level = role.GetLevel()
	get = QQHttp.report_login(openid, pf, userip, roleid, source, level, ReportBack, "report_login  pf : " + pf)
	# 保存上报信息
	UpLoadReport(roleid, get, login_info)
	pfnum = 0
	global Pf_RoleSet, Pf_RoleCnt_Dict
	if roleid not in Pf_RoleSet:
		Pf_RoleSet.add(roleid)
		Pf_RoleCnt_Dict[pf] = pfnum = Pf_RoleCnt_Dict.get(pf, 0) + 1
	
	if pfnum:
		QQHttp.report_online(pf, pfnum, ReportBack, "report_online  pf : " + pf)
	
	global RoleLoginTick
	tickid = RoleLoginTick.get(roleid)
	if tickid:
		role.UnregTick(tickid)
	#登录续期
	RoleLoginTick[roleid] = role.RegTick(3600, IsLogin, role)
	
	QQLog.LogLogin(role, pf, openid, userip)
	

def IsLogin(role, callArgv, regparam):
	if role.IsKick():
		return
	login_info = role.GetTempObj(EnumTempObj.LoginInfo)
	openid = login_info["account"]
	pf = login_info["pf"]
	openkey = login_info["openkey"]
	QQHttp.is_login(openid, openkey, pf, IsLoginBack, regparam)

def IsLoginBack(response, regparam):
	code, body = response
	if code != 200:
		return
	res = eval(body)
	if res.get("ret") != 0:
		return
	#登录续期
	role = regparam
	if role.IsKick():
		return
	global RoleLoginTick
	RoleLoginTick[role.GetRoleID()] = role.RegTick(3600, IsLogin, role)


def BeforeExit(role, param):
	if not Environment.EnvIsQQ():
		return
	login_info = role.GetTempObj(EnumTempObj.LoginInfo)
	openid = login_info["account"]
	pf = login_info["pf"]
	via = login_info.get("via", "")
	source = "%s.%s" % (pf, via)
	userip = login_info["userip"]
	roleid = role.GetRoleID()
	level = role.GetLevel()
	onlinetime = role.GetTI64(EnumTempInt64.LoginOnlineTime)
	QQHttp.report_quit(openid, pf, userip, roleid, source, level, onlinetime, ReportBack, "report_quit  pf : " + pf)
	
	
	global Pf_RoleSet, Pf_RoleCnt_Dict
	if roleid in Pf_RoleSet:
		Pf_RoleSet.discard(roleid)
		cnt = Pf_RoleCnt_Dict.get(pf)
		if cnt:
			cnt -= 1
			if cnt <= 0:
				del Pf_RoleCnt_Dict[pf]
			else:
				Pf_RoleCnt_Dict[pf] = cnt
	
	QQLog.LogExit(role, pf, openid, userip)

def AfterInit(role, param):
	if not Environment.EnvIsQQ():
		return
	login_info = role.GetTempObj(EnumTempObj.LoginInfo)
	openid = login_info["account"]
	pf = login_info["pf"]
	via = login_info.get("via", "")
	source = "%s.%s" % (pf, via)
	userip = login_info["userip"]
	roleid = role.GetRoleID()
	
	if login_info.get("invkey"):
		QQHttp.report_register(openid, pf, userip, roleid, source, ReportBack, "report_register  pf : " + pf)
	else:
		QQHttp.report_accept(openid, pf, userip, roleid, source, ReportBack, "report_accept  pf : " + pf)
	
	QQLog.LogCreateRole(role, pf, openid, userip)


def AfterConsumeQPoint(role, param):
	if not Environment.EnvIsQQ():
		return
	goods_id, goods_price, goods_cnt = param
	login_info = role.GetTempObj(EnumTempObj.LoginInfo)
	openid = login_info["account"]
	pf = login_info["pf"]
	via = login_info.get("via", "")
	source = "%s.%s" % (pf, via)
	userip = login_info["userip"]
	roleid = role.GetRoleID()
	#上报充值
	QQHttp.report_recharge(openid, pf, userip, roleid, source, goods_price * 10 * goods_cnt, goods_id, goods_cnt, ReportRechargeBack, (roleid, pf, goods_price))
	QQLog.LogConsume(role, pf, openid, userip, goods_id, goods_price, goods_cnt)


def AfterChangeUnbindRMB(role, param):
	if not Environment.EnvIsQQ():
		return
	oldValue, newValue = param
	if newValue > oldValue:
		#不是消费
		return
	goods_price = oldValue - newValue
	goods_cnt = 1
	goods_id = 1001#特殊
	#goods_id, goods_price, goods_cnt = param
	login_info = role.GetTempObj(EnumTempObj.LoginInfo)
	openid = login_info["account"]
	pf = login_info["pf"]
	via = login_info.get("via", "")
	source = "%s.%s" % (pf, via)
	userip = login_info["userip"]
	roleid = role.GetRoleID()
	#上报单位为Q分（100Q分 = 10Q点 = 1Q币）。
	QQHttp.report_consume(openid, pf, userip, roleid, source, goods_price * 10, goods_id, goods_cnt, ReportBack, "report_consume  pf : " + pf)


def Register(role, param):
	if not Environment.EnvIsQQ():
		return
	login_info = role.GetTempObj(EnumTempObj.LoginInfo)
	openid = login_info["account"]
	pf = login_info["pf"]
	via = login_info.get("via", "")
	source = "%s.%s" % (pf, via)
	userip = login_info["userip"]
	roleid = role.GetRoleID()
	QQHttp.report_register(openid, pf, userip, roleid, source, ReportBack, "Register  pf : " + pf)


def Invite(role, param):
	if not Environment.EnvIsQQ():
		return
	login_info = role.GetTempObj(EnumTempObj.LoginInfo)
	openid = login_info["account"]
	pf = login_info["pf"]
	via = login_info.get("via", "")
	source = "%s.%s" % (pf, via)
	userip = login_info["userip"]
	roleid = role.GetRoleID()
	QQHttp.report_invite(openid, pf, userip, roleid, source, ReportBack, "Invite  pf : " + pf)


def AfterNewMinute():
	#每5分钟上报实时在线
	global Report_Minutes
	Report_Minutes += 1
	if Report_Minutes % 5 != 0:
		return
	global Pf_RoleCnt_Dict
	if not Pf_RoleCnt_Dict:
		return
	
	for pf, pfnum in Pf_RoleCnt_Dict.iteritems():
		QQHttp.report_online(pf, pfnum, ReportBack, "report_online  pf : " + pf)
		QQLog.LogOnline(pf, pfnum)
	
	#更新最大在线人数
	roleCnt = len(cRoleMgr.GetAllRole())
	WorldDataNotSync.WorldDataPrivate[WorldDataNotSync.MaxOnlineToday] = max(roleCnt, WorldDataNotSync.WorldDataPrivate.get(WorldDataNotSync.MaxOnlineToday, 0))

def ReportBack(response, regparam):
	#上报回调
	return

#	if response is None:
#		print "GE_EXC, QReport  (%s) back response is None" % (regparam)
#		return
#	code, body = response
#	if code != 200:
#		print "GE_EXC, QReport (%s) back code(%s), body(%s)" % (regparam, code, body)

def ReportRechargeBack(response, regparam):
	pass
#	roleId, pf, goods_price = regparam
#	if response is None:
#		RechargeFail(roleId, pf, goods_price)
#		print "GE_EXC ReportRechargeBack response is None"
#		return
#	code, body = response
#	if code != 200:
#		RechargeFail(roleId, pf, goods_price)
#		print "GE_EXC ReportRechargeBack code error (%s) body (%s)" % (code, body)
#		return
#	
#	RechargeSucceed(roleId, pf, goods_price)


def GetNowDayData():
	global NowDayChargeDataDict
#	if NowDayChargeDataDict is None:
#		if not QReport_Dict.returnDB:
#			return None
#		days = cDateTime.Days()
#		if days not in QReport_Dict:
#			QReport_Dict[days] = NowDayChargeDataDict = {}
#		else:
#			NowDayChargeDataDict = QReport_Dict[days]
	return NowDayChargeDataDict


def RechargeSucceed(roleId, pf, goods_price):
	pass
#	daysDict = GetNowDayData()
#	if daysDict is None:
#		print  "GE_EXC RechargeSucceed daysDict is None"
#		return
#	pfdata = daysDict.get(pf)
#	if not pfdata:
#		#上报成功次数，上报成功总额，上报失败次数，上报失败总额
#		daysDict[pf] = [1, goods_price, 0, 0]
#	else:
#		pfdata[0] += 1
#		pfdata[1] += goods_price

def RechargeFail(roleId, pf, goods_price):
	pass
#	daysDict = GetNowDayData()
#	if daysDict is None:
#		print  "GE_EXC RechargeFail daysDict is None"
#		return
#	pfdata = daysDict.get(pf)
#	if not pfdata:
#		#上报成功次数，上报成功总额，上报失败次数，上报失败总额
#		daysDict[pf] = [0, 0, 1, goods_price]
#	else:
#		pfdata[2] += 1
#		pfdata[3] += goods_price

def AfterNewDay():
	global NowDayChargeDataDict
	NowDayChargeDataDict = None

def AfterLoad():
	pass
#	nowdays = cDateTime.Days()
#	for days in QReport_Dict.keys():
#		if nowdays - days > 62:
#			#只保存2个月的数据
#			del QReport_Dict[days]

if "_HasLoad" not in dir():
	if Environment.EnvIsQQ() and Environment.HasLogic and (not Environment.IsCross):
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_BeforeExit, BeforeExit)
		Event.RegEvent(Event.Eve_FirstInitRole, AfterInit)
		Event.RegEvent(Event.Eve_GamePoint, AfterConsumeQPoint)
		Event.RegEvent(Event.AfterChangeUnbindRMB_Q, AfterChangeUnbindRMB)
		#特殊事件触发
		Event.RegEvent(Event.Eve_SyncRoleOtherData, AfterLogin)
		Event.RegEvent(Event.Eve_ClientLost, BeforeExit)

		cComplexServer.RegAfterNewMinuteCallFunction(AfterNewMinute)
		
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
		
		#QReport_Dict = Contain.Dict("QReport_Dict", (2038, 1, 1), AfterLoad)
		