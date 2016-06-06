#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QInvite")
#===============================================================================
# QQ邀请
#===============================================================================
import Environment
from ComplexServer.API import QQHttp
from ComplexServer.Plug.DB import DBHelp
from Game.Role import Event, Call
from Game.Role.Data import EnumTempObj, EnumObj

def AfterInit(role, param):
	if not Environment.EnvIsQQ():
		return
	roleid = role.GetRoleID()
	login_info = role.GetTempObj(EnumTempObj.LoginInfo)
	openid = login_info["account"]
	openkey = login_info["openkey"]
	pf = login_info["pf"]
	userip = login_info["userip"]
	via = login_info.get("invkey", "via")
	invkey = login_info.get("invkey", "")
	# 腾讯罗盘上报
	report_register_accept(openid, pf, userip, roleid, via, invkey)
	# 如果是邀请，则验证邀请
	if invkey:
		itime = login_info.get("itime")
		if itime is None: return
		iopenid = login_info.get("iopenid")
		if iopenid is None: return
		app_custom = login_info.get("app_custom")
		if app_custom is None: return
		# 检测自定义参数
		if not app_custom.isdigit():
			print "GE_EXC, invite app_custom(%s) error1." % app_custom
			return
		iroleid = int(app_custom)
		if not DBHelp.GetDBIDByRoleID(iroleid):
			print "GE_EXC, invite app_custom(%s) error2." % app_custom
			return
		QQHttp.verify_invkey(openid, openkey, pf, invkey, itime, iopenid, OnVerifyInvkey, (role, iroleid))

def OnVerifyInvkey(response, regparam):
	code, body = response
	if code != 200:
		return
	body = eval(body)
	if body["ret"] != 0:
		return
	if body["is_right"] != 1:
		return
	role, iroleid = regparam
	role.GetObj(EnumObj.InviteInfo)[0] = iroleid

def OnFriendInfoChange(role, param):
	invite_info = role.GetObj(EnumObj.InviteInfo)
	iroleid = invite_info.get(0)
	if not iroleid:
		return
	Call.RemoteCall(iroleid, OnFriendInfoUpdate, (role.GetRoleID(), role.GetLevel(), role.GetConsumeQPoint()))

def OnFriendInfoUpdate(role, param):
	friend_id, level, qpoint = param
	role.GetObj(EnumObj.InviteInfo)[friend_id] = (level, qpoint)
	Event.TriggerEvent(Event.Eve_AfterInviteeChange, role, param)

def report_register_accept(openid, pf, userip, roleid, via, invkey):
	source = "%s.%s" % (pf, via)
	source

if "_HasLoad" not in dir():
	if Environment.EnvIsQQ() and (not Environment.IsCross):
		Event.RegEvent(Event.Eve_FirstInitRole, AfterInit)
		Event.RegEvent(Event.Eve_AfterLevelUp, OnFriendInfoChange)
		Event.RegEvent(Event.Eve_GamePoint, OnFriendInfoChange)
