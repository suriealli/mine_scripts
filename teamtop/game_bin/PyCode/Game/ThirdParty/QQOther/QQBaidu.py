#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQOther.QQBaidu")
#===============================================================================
# 官网百度搜索礼包
#===============================================================================
import Environment
from Game.Role import Event
from Game.Role.Data import EnumInt1, EnumTempObj
from ComplexServer.Log import AutoLog

Tips = "恭喜你成功领取了#C(#FFFF00)百度专区礼包#n！请在背包内查收使用。"

def SyncRoleOtherData(role, param):
	if role.GetI1(EnumInt1.QQBaiduLibao):
		return
	
	loginInfo = role.GetTempObj(EnumTempObj.LoginInfo)
	app_custom = loginInfo.get("app_custom", "")
	if not app_custom:
		return
	
	if app_custom != "pinpai":
		return
	
	with Tra_BaiduLibao:
		role.SetI1(EnumInt1.QQBaiduLibao, 1)
		role.AddItem(27385,1)
	role.Msg(4, 0, Tips)
	

if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.EnvIsQQ() or Environment.IsDevelop) and not Environment.IsCross:
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		
		Tra_BaiduLibao = AutoLog.AutoTransaction("Tra_BaiduLibao", "百度礼包")

