#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQTips.QQTips")
#===============================================================================
# QQ会员Tips礼包
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumTempObj, EnumInt8
from Game.Role import Event

#app_custom=huiyuantips
def SyncRoleOtherData(role, param):
	loginInfo = role.GetTempObj(EnumTempObj.LoginInfo)
	app_custom = loginInfo.get("app_custom", "")
	if not app_custom:
		return
	
	if app_custom != "huiyuantips":
		return
	
	if role.GetI8(EnumInt8.QQTipsFlag) > 0:
		return
	
	role.SetI8(EnumInt8.QQTipsFlag, 1)


def RequestQQTipsRewrad(role, msg):
	'''
	请求领取QQ会员Tips礼包
	@param role:
	@param msg:
	'''
	if role.GetI8(EnumInt8.QQTipsFlag) != 1:
		return
	with Tra_QQTipsRewrad:
		role.SetI8(EnumInt8.QQTipsFlag, 2)
		role.AddItem(26900, 1)

if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.EnvIsQQ() or Environment.IsDevelop) and not Environment.IsCross:
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		
		Tra_QQTipsRewrad = AutoLog.AutoTransaction("Tra_QQTipsRewrad", "QQ会员Tips礼包")
	
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQ_RequestQQTipsRewrad", "请求领取QQ会员Tips礼包"), RequestQQTipsRewrad)
		