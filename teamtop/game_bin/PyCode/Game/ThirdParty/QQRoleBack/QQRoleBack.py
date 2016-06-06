#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQRoleBack.QQRoleBack")
#===============================================================================
# 流失用户回流(腾讯自己定义的回流活动，和我们开发这边定义的另外一个角色回流是有区别的)
#===============================================================================
import Environment
import cRoleMgr
import cDateTime
from Common.Message import AutoMessage
from ComplexServer.API import QQHttp
from ComplexServer.Log import AutoLog
from Game.Role import Event, Call
from Game.Role.Data import EnumTempObj, EnumObj, EnumDayInt1



#濒临流失獎勵
L1 = [(26044, 1), (26634, 1), (26119, 1)]
#濒临流失連續登錄獎勵
L1_Day = {1 : (480000, 20, [(26266, 1), (26033, 1)]),
		2 : (680000, 30, [(26266, 1), (26033, 1)]),
		3 : (880000, 50, [(26266, 1), (26033, 1)]),
		}


#已流失獎勵
L2 = [(26026, 1), (26634, 2), (26267, 1)]
#已流失連續登錄獎勵
L2_Day = {1 : (880000, 100, [(26044, 1), (26119, 1)]),
		2 : (1880000, 150, [(26044, 2), (26119, 2)]),
		3 : (2880000, 200, [(26044, 3), (26119, 3)]),
		}




if "_HasLoad" not in dir():
	pass



def AfterLogin(role, param):
	#登录的时候查询
	login_info = role.GetTempObj(EnumTempObj.LoginInfo)
	openid = login_info["account"]
	pf = login_info["pf"]
	userip = login_info["userip"]
	openkey = login_info["openkey"]
	
	app_appbitmap = login_info.get("app_appbitmap", 0)
	app_custom = login_info.get("app_custom", "")
	if app_appbitmap or app_custom == "refluxGiftForAppWall" or app_custom == "appNumFromList":
		QQHttp.get_app_flag(openid, openkey, pf, userip, AfterGetAppFlagBack, (role.GetRoleID(), openid, pf, userip, openkey))
	
	
def AfterGetAppFlagBack(response, regparam):
	code, body = response
	if code != 200:
		print "GE_EXC, AfterGetAppFlagBack code error (%s)" % code
		return
	
	result = eval(body)
	if  result.get("ret") != 0:
		print "GE_EXC AfterGetAppFlagBack ret error", response
		return
	
	customflag = result.get("customflag", 0)
	if not customflag:
		return
	
	roleId, openid, pf, userip, openkey = regparam
	role = cRoleMgr.FindRoleByRoleID(roleId)
	if not role:
		return
	#1表示濒临沉默用户，2表示沉默用户
	groupId = customflag & 1
	if not groupId:
		groupId = customflag & 2
		if not groupId:
			return
	
	#先删除流失标志,回调后再设置发奖内容
	QQHttp.del_app_flag(openid, openkey, pf, userip, 1, groupId, DelAppFlagBack, (roleId, groupId))
	
def DelAppFlagBack(response, regparam):
	code, body = response
	if code != 200:
		print "GE_EXC, DelAppFlagBack code error (%s)" % code
		return
	
	result = eval(body)
	if result.get("ret") != 0:
		#删除失败
		print "GE_EXC, DelAppFlagBack error result response", response
		return
	
	#发离线命令改数据
	roleId, groupId = regparam
	Call.LocalDBCall(roleId, InitBackData, groupId)


def InitBackData(role, groupId):
	#{1:回流用户群ID, 2:回流当天day时间戳, 3:回流礼包领取状态, 4:回来连续登录奖励领取记录列表[day1, day2, day3]}
	if not groupId:
		return
	roleBackData = role.GetObj(EnumObj.QQRoleBackData)
	nowdays = cDateTime.Days()
	if roleBackData:
		oldDays = roleBackData.get(2)
		if oldDays and nowdays - oldDays < 4:
			#4天内又流失了？无视
			print "GE_EXC, repeat qq role back last 4 days"
			return 
	
	with Tra_QQRoleBack:
		roleBackData = {1 : groupId, 2 : nowdays, 3 : 1, 4 : []}
		role.SetObj(EnumObj.QQRoleBackData, roleBackData)
		#记录日志
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveQQRoleBack, roleBackData)
		#同步数据
		role.SendObj(QQRoleBack_S_SyncData, roleBackData)


def RequestGetReward(role, msg):
	'''
	请求领取回流角色礼包
	@param role:
	@param msg:
	'''
	backId, _ = msg
	roleBackData = role.GetObj(EnumObj.QQRoleBackData)
	if not roleBackData:
		return
	
	if roleBackData.get(3) != 1:
		return
	
	if role.GetDI1(EnumDayInt1.QQRoleBackRewardFlag):
		print "GE_EXC, Warning repeat QQRoleBackRewardFlag set true role(%s)" % role.GetRoleID()
		return
	
	with Tra_QQRoleBackReward:
		groupId = roleBackData[1]
		#设置已经领取
		roleBackData[3] = 2
		#防刷
		role.SetDI1(EnumDayInt1.QQRoleBackRewardFlag, True)
		#按照groupId发奖励
		if groupId == 1:
			for coding, cnt in L1:
				role.AddItem(coding, cnt)
		else:
			for coding, cnt in L2:
				role.AddItem(coding, cnt)
				
	role.CallBackFunction(backId, None)
	
	
	
def RequestGetDayReward(role, msg):
	'''
	请求领取回流角色连续登录礼包
	@param role:
	@param msg:
	'''
	
	backId, _ = msg
	roleBackData = role.GetObj(EnumObj.QQRoleBackData)
	if not roleBackData:
		return
	
	nowDays = cDateTime.Days()
	
	backdays = roleBackData.get(2)
	if nowDays - backdays > 2:
		#只有连续3天
		return
	roledays = roleBackData.get(4)
	if roledays and nowDays in roledays:
		return
	
	cntstatus = nowDays - backdays + 1
	groupId = roleBackData[1]
	rewards = None
	if groupId == 1:
		rewards = L1_Day.get(cntstatus)
	else:
		rewards = L2_Day.get(cntstatus)
	
	if not rewards:
		print "GE_EXC, RequestGetDayReward error not rewards"
		return
	
	with Tra_QQRoleBackDayRewrad:
		roledays.append(nowDays)
		
		money, rmb, items = rewards
		role.IncMoney(money)
		role.IncBindRMB(rmb)
		for coding, cnt in items:
			role.AddItem(coding, cnt)
		
	role.CallBackFunction(backId, None)


def SyncRoleOtherData(role, msg):
	roleBackData = role.GetObj(EnumObj.QQRoleBackData)
	if roleBackData:
		#先同步一次数据
		role.SendObj(QQRoleBack_S_SyncData, roleBackData)


if "_HasLoad" not in dir():
	QQRoleBack_S_SyncData = AutoMessage.AllotMessage("QQRoleBack_S_SyncData", "同步回流角色数据")
	
	Tra_QQRoleBack = AutoLog.AutoTransaction("Tra_QQRoleBack", "角色回流到游戏")
	Tra_QQRoleBackReward = AutoLog.AutoTransaction("Tra_QQRoleBackReward", "回流角色礼包奖励")
	Tra_QQRoleBackDayRewrad = AutoLog.AutoTransaction("Tra_QQRoleBackDayRewrad", "回流角色连续登录礼包奖励")
	
	if Environment.HasLogic and Environment.EnvIsQQ()  and (not Environment.IsCross):
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQRoleBack_RequestGetReward", "请求领取回流角色礼包"), RequestGetReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQRoleBack_RequestGetDayReward", "请求领取回流角色连续登录礼包"), RequestGetDayReward)
		
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		