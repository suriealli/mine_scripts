#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQActivePage.QQActivePage")
#===============================================================================
# 腾讯活动页面
#===============================================================================
import Environment
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Role.Data import EnumTempObj, EnumObj

#app_custom=FIRST_PUBLISH1
#app_custom=FIRST_PUBLISH2
#app_custom=FIRST_PUBLISH3

P_ConfigDict = {"FIRST_PUBLISH1" : 1, #QQ空间礼包 登录就发
				"FIRST_PUBLISH2" : 2, #邀请好友礼包 邀请后再发
				"FIRST_PUBLISH3" : 3}#等级礼包 等级达到34级才发

RewardDict = {1 : 26627,
				2 : 26628,
				3 : 26629}

def SyncRoleOtherData(role, param):
	loginInfo = role.GetTempObj(EnumTempObj.LoginInfo)
	app_custom = loginInfo.get("app_custom", "")
	if not app_custom:
		return
	
	fid = P_ConfigDict.get(app_custom)
	if not fid:
		return
	
	itemcoding = RewardDict.get(fid)
	if not itemcoding:
		return
	pd = role.GetObj(EnumObj.QQActivePageData)
	if not pd:
		pd = {1 : set(), 2 : set()}
		role.SetObj(EnumObj.QQActivePageData, pd)
		
	activeset = pd.get(1)
	rewardset = pd.get(2)
	if fid in activeset or fid in rewardset:
		#已经激活过了
		return
	
	with Tra_QQActivePage:
		if fid == 1:
			#激活，记录发奖，发奖
			activeset.add(fid)
			pd[2].add(fid)
			role.SetObj(EnumObj.QQActivePageData, pd)
			role.AddItem(itemcoding, 1)
		elif fid == 2:
			#激活
			activeset.add(fid)
			role.SetObj(EnumObj.QQActivePageData, pd)
		elif fid == 3:
			if role.GetLevel() < 34:
				#等级不足,激活
				activeset.add(fid)
				role.SetObj(EnumObj.QQActivePageData, pd)
			else:
				#等级够了激活，记录发奖，发奖
				activeset.add(fid)
				pd[2].add(fid)
				role.SetObj(EnumObj.QQActivePageData, pd)
				role.AddItem(itemcoding, 1)
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveQQActivePage, pd)

def AfterLevelUp(role, param):
	pd = role.GetObj(EnumObj.QQActivePageData)
	if not pd:
		return
	fid = 3
	itemcoding = RewardDict.get(fid)
	if not itemcoding:
		return
	if role.GetLevel() != 34:
		return
	
	if fid not in pd[1] :
		return
	
	if fid in pd[2]:
		print "GE_EXC, repeat and error in AfterLevelUp QQActivePage"
		return
	with Tra_QQActivePageReward:
		pd[2].add(fid)
		role.AddItem(itemcoding, 1)


def AfterInvite(role, param):
	pd = role.GetObj(EnumObj.QQActivePageData)
	if not pd:
		return
	fid = 2
	if fid not in pd[1] :
		return
	if fid in pd[2]:
		return
	
	itemcoding = RewardDict.get(fid)
	if not itemcoding:
		return
	with Tra_QQActivePageReward:
		pd[2].add(fid)
		role.AddItem(itemcoding, 1)

if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.EnvIsQQ() or Environment.IsDevelop) and (not Environment.IsCross):
		#Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_AfterLevelUp, AfterLevelUp)
		Event.RegEvent(Event.Eve_AfterInviteQQFriend, AfterInvite)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		
		Tra_QQActivePage = AutoLog.AutoTransaction("Tra_QQActivePage", "腾讯页面礼包登记")
		Tra_QQActivePageReward = AutoLog.AutoTransaction("Tra_QQActivePageReward", "腾讯页面礼包奖励")

