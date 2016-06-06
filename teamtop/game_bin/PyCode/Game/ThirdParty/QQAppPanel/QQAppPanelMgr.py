#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQAppPanel.QQAppPanelMgr")
#===============================================================================
# QQ应用面板管理
#===============================================================================
import Environment
import cRoleMgr
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from ComplexServer.API import QQHttp
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Role.Data import EnumTempObj, EnumInt1, EnumObj, EnumDayInt1, EnumInt8
from Game.ThirdParty.QQAppPanel import QQAppPanelConfig

if "_HasLoad" not in dir():
	ON_APP_PANEL_REWARD_ITEM_CODING = 25738		#添加应用面板物品奖励
	APP_PANEL_LOGIN_DAYS_MAX = 7				#QQ应用面板登陆最大天数
	
	#消息
	QQ_Show_App_Login_Reward_Panel = AutoMessage.AllotMessage("QQ_Show_App_Login_Reward_Panel", "通知客户端显示QQ应用登陆奖励面板")
	

def IsAppOnPanel(role):
	login_info = role.GetTempObj(EnumTempObj.LoginInfo)
	openid = login_info["account"]
	openkey = login_info["openkey"]
	pf = login_info["pf"]
	QQHttp.is_app_onpanel(openid, openkey, pf, OnCheckIsAppOnPanel, role)
	
def ShowAppLoginRewardPanel(role):
	rewardDict = role.GetObj(EnumObj.AppPanelLoginReward)
	
	showList = []
	for x in xrange(APP_PANEL_LOGIN_DAYS_MAX):
		days = x + 1
		if days not in rewardDict:
			showList.append(0)
		else:
			showList.append(1)
	#同步客户端
	role.SendObj(QQ_Show_App_Login_Reward_Panel, showList)
	
def GetAppPanelLoginReward(role, days):
	#登陆天数是否达到条件
	if days > role.GetI8(EnumInt8.AppPanelLoginDays):
		return
	
	#奖励配置
	config = QQAppPanelConfig.APP_PANEL_LOGIN_REWARD.get(days)
	if not config:
		return
	
	rewardDict = role.GetObj(EnumObj.AppPanelLoginReward)
	#是否已经领取过奖励
	if days in rewardDict:
		return
	
	#设置已领取
	rewardDict[days] = 1
	
	#奖励
	prompt = ""
	if config.bindRMB:
		#魔晶
		role.IncBindRMB(config.bindRMB)
		#提示
		prompt = GlobalPrompt.BindRMB_Tips % config.bindRMB
	if config.rewardItemList:
		for item in config.rewardItemList:
			role.AddItem(*item)
			#提示字符串
			prompt += GlobalPrompt.Item_Tips % (item[0], item[1])
			
	#提示
	role.Msg(2, 0, prompt)
		
	#刷新面板
	ShowAppLoginRewardPanel(role)
	
#===============================================================================
# 腾讯接口返回
#===============================================================================
def OnCheckIsAppOnPanel(response, regparam):
	code, body = response
	if code != 200:
		return
	body = eval(body)
	if body["ret"] != 0:
		return
	#是否添加到QQ主面板
	if body["in_applist"] != 1:
		return
	
	role = regparam
	#是否已经添加到QQ主面板
	if role.GetI1(EnumInt1.QAppOnPanel):
		return
	
	#设置添加到QQ主面板
	role.SetI1(EnumInt1.QAppOnPanel, 1)
	#奖励
	role.AddItem(ON_APP_PANEL_REWARD_ITEM_CODING, 1)
	
	if not role.GetDI1(EnumDayInt1.QAppPanelLogin):
		#设置今日已经登陆QQ应用面板
		role.SetDI1(EnumDayInt1.QAppPanelLogin, 1)
		#已经登陆的天数
		loginDays = role.GetI8(EnumInt8.AppPanelLoginDays)
		if loginDays < APP_PANEL_LOGIN_DAYS_MAX:
			#登陆天数+1
			role.IncI8(EnumInt8.AppPanelLoginDays, 1)
	
	#提示
	role.Msg(2, 0, GlobalPrompt.QQ_APP_ON_PANEL_REWARD_PROMPT % (ON_APP_PANEL_REWARD_ITEM_CODING, 1))
	
#===============================================================================
# 事件
#===============================================================================
def OnSyncRoleOtherData(role, param):
	'''
	角色登陆同步其它剩余数据
	@param role:
	@param param:
	'''
	#同步应用登陆奖励面板数据
	ShowAppLoginRewardPanel(role)
	
	#应用是否在QQ面板上面
	if not role.GetI1(EnumInt1.QAppOnPanel):
		return
	
	#今天是否已经登陆QQ应用面板
	if role.GetDI1(EnumDayInt1.QAppPanelLogin):
		return
	
	#设置今日已经登陆QQ应用面板
	role.SetDI1(EnumDayInt1.QAppPanelLogin, 1)
	
	#已经登陆的天数
	loginDays = role.GetI8(EnumInt8.AppPanelLoginDays)
	if loginDays >= APP_PANEL_LOGIN_DAYS_MAX:
		return
	
	#登陆天数+1
	role.IncI8(EnumInt8.AppPanelLoginDays, 1)
	
#===============================================================================
# 客户端请求
#===============================================================================
def RequestQQIsAppOnPanel(role, msg):
	'''
	客户端请求验证是否加入了应用面板
	@param role:
	@param msg:
	'''
	if Environment.EnvIsQQ():
		IsAppOnPanel(role)
	
def RequestQQOpenAppLoginRewardPanel(role, msg):
	'''
	客户端请求打开QQ应用面板登陆奖励面板
	@param role:
	@param msg:
	'''
	ShowAppLoginRewardPanel(role)
	
def RequestQQGetAppLoginReward(role, msg):
	'''
	客户端请求领取QQ应用面板登陆奖励
	@param role:
	@param msg:
	'''
	days = msg
	
	#日志
	with TraGetAppLoginReward:
		GetAppPanelLoginReward(role, days)
	
if "_HasLoad" not in dir():
	if Environment.EnvIsQQ() and (not Environment.IsCross):
		#角色登陆同步其它剩余数据
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		#日志
		TraGetAppLoginReward = AutoLog.AutoTransaction("TraGetAppLoginReward", "领取QQ应用面板登陆奖励")
		#注册消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQ_Is_App_On_Panel", "客户端请求验证是否加入了应用面板"), RequestQQIsAppOnPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQ_Get_App_Login_Reward", "客户端请求领取QQ应用面板登陆奖励"), RequestQQGetAppLoginReward)
