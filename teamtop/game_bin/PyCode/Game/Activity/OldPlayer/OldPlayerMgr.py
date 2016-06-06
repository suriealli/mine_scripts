#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.OldPlayer.OldPlayerMgr")
#===============================================================================
# 老玩家回流活动
#===============================================================================
import cRoleMgr
import cDateTime
import Environment
from Game.Role import Event
from Game.SysData import WorldData
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from Game.Role.Data import EnumObj, EnumInt8, EnumInt1, EnumDisperseInt32, EnumInt16
from Game.Activity.OldPlayer import OldPlayerConfig

if "_HasLoad" not in dir():
	#老玩家回流Obj枚举
	EnumOldPlayerLoginReward_OS = 1
	EnumOldPlayerLevelReward_NS = 2
	EnumOldPlayerOnly_OS = 3
	EnumOldPlayerOnly_NS = 4
	EnumOldPlayerVIPOnly_OS = 5
	EnumOldPlayerVIPOnly_NS = 6
	
	#消息
	SyncOldPlayerLoginReward_OS = AutoMessage.AllotMessage("SyncOldPlayerLoginReward_OS", "同步回归登录大礼(老服)领取数据")
	SyncOldPlayerLevelReward_NS = AutoMessage.AllotMessage("SyncOldPlayerLevelReward_NS", "同步回归等级大礼(新服)领取数据")
	SyncOldPlayerOnly_OS = AutoMessage.AllotMessage("SyncOldPlayerOnly_OS", "同步老玩家独享奖励(老服)领取数据")
	SyncOldPlayerOnly_NS = AutoMessage.AllotMessage("SyncOldPlayerOnly_NS", "同步老玩家独享奖励(新服)领取数据")
	SyncOldPlayerVIPOnly_OS = AutoMessage.AllotMessage("SyncOldPlayerVIPOnly_OS", "同步老玩家贵族特权奖励(老服)领取数据")
	SyncOldPlayerVIPOnly_NS = AutoMessage.AllotMessage("SyncOldPlayerVIPOnly_NS", "同步老玩家贵族特权奖励(新服)领取数据")
	
	
	TraBackToNewServer = AutoLog.AutoTransaction("TraBackToNewServer", "老玩家回流至新服")
	TraBackToOldServer = AutoLog.AutoTransaction("TraBackToOldServer", "老玩家回流至老服")
	TraOldPlayerLoginReward_OS = AutoLog.AutoTransaction("TraOldPlayerLoginReward_OS", "老玩家回流回归登录大礼(老服)")
	TraOldPlayerLevelReward_NS = AutoLog.AutoTransaction("TraOldPlayerLevelReward_NS", "老玩家回流回归等级大礼(新服)")
	TraOldPlayerOnly_OS = AutoLog.AutoTransaction("TraOldPlayerOnly_OS", "老玩家回流老玩家独享奖励(老服)")
	TraOldPlayerOnly_NS = AutoLog.AutoTransaction("TraOldPlayerOnly_NS", "老玩家回流老玩家独享奖励(新服)")
	TraOldPlayerVIPOnly_OS = AutoLog.AutoTransaction("TraOldPlayerVIPOnly_OS", "老玩家回流老玩家贵族特权奖励(老服)")
	TraOldPlayerVIPOnly_NS = AutoLog.AutoTransaction("TraOldPlayerVIPOnly_NS", "老玩家回流老玩家贵族特权奖励(新服)")
	

def RequestLoginReward_OS(role, msg):
	'''
	请求获取回归登录大礼(老服)OS = Old Server
	@param role:
	@param msg:奖励索引
	'''
	#判断是否是老服回流老服的玩家
	if role.GetI1(EnumInt1.IsLocalServerBack) is False:
		return
	if role.GetLevel() < EnumGameConfig.BackToOldNeedLevel:
		return
	index = msg
	gotSet = role.GetObj(EnumObj.OldPlayerBack).setdefault(EnumOldPlayerLoginReward_OS, set())
	if index in gotSet:
		return
	
	nowDays = cDateTime.Days()
	backDays = role.GetDI32(EnumDisperseInt32.OldServerBackDays_OS)
	
	loginDays = nowDays - backDays + 1
	config = OldPlayerConfig.LoginRewardOSDict.get(index)
	if config is None:
		return
	
	if loginDays != config.loginDays:
		return
	
	tips = GlobalPrompt.Reward_Tips
	
	with TraOldPlayerLoginReward_OS:
		gotSet.add(index)
		for item in config.items:
			role.AddItem(*item)
			tips += GlobalPrompt.Item_Tips % item
			
		if config.money:
			role.IncMoney(config.money)
			tips += GlobalPrompt.Money_Tips % config.money
		if config.bindRMB:
			role.IncBindRMB(config.bindRMB)
			tips += GlobalPrompt.BindRMB_Tips % config.bindRMB
		
		backDays = role.GetDI32(EnumDisperseInt32.OldServerBackDays_OS)
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveOldPlayerBackReward, (backDays, index))
		
	role.Msg(2, 0, tips)
	role.SendObj(SyncOldPlayerLoginReward_OS, gotSet)


def RequestLevelReward_NS(role, msg):
	'''
	请求获取回归等级大礼(新服)NS = New Server
	@param role:
	@param msg:奖励索引
	'''
	#判断是否是老服回流新服的玩家
	if role.GetI1(EnumInt1.IsOldServerBack) is False:
		return
	
	index = msg
	gotSet = role.GetObj(EnumObj.OldPlayerBack).setdefault(EnumOldPlayerLevelReward_NS, set())
	if index in gotSet:
		return
	
	config = OldPlayerConfig.LevelRewardNSDict.get(index)
	if config is None:
		return
	
	if role.GetLevel() < config.needLevel:
		return
	
	tips = GlobalPrompt.Reward_Tips
	
	with TraOldPlayerLevelReward_NS:
		gotSet.add(index)
		for item in config.items:
			role.AddItem(*item)
			tips += GlobalPrompt.Item_Tips % item
		if config.money:
			role.IncMoney(config.money)
			tips += GlobalPrompt.Money_Tips % config.money
		if config.bindRMB:
			role.IncBindRMB(config.bindRMB)
			tips += GlobalPrompt.BindRMB_Tips % config.bindRMB

	role.Msg(2, 0, tips)
	role.SendObj(SyncOldPlayerLevelReward_NS, gotSet)
	

def RequestOldPlayerOnly_OS(role, msg):
	'''
	请求获取老玩家独享奖励(老服)OS = Old Server
	@param role:
	@param msg:奖励索引
	'''
	if role.GetI1(EnumInt1.IsLocalServerBack) is False:
		return
	
	if OldPlayerConfig.IsStart is False:
		return
	
	if role.GetI16(EnumInt16.OldPlayerBackVersion) != OldPlayerConfig.ActVersion:
		return
		
	index = msg
	gotSet = role.GetObj(EnumObj.OldPlayerBack).setdefault(EnumOldPlayerOnly_OS, set())
	if index in gotSet:
		return
	
	config = OldPlayerConfig.OldPlayerOnlyOSDict.get(index)
	if config is None:
		return
	
	if role.GetDayBuyUnbindRMB_Q() < config.totalRecharge:
		return
	
	tips = GlobalPrompt.Reward_Tips
	
	with TraOldPlayerOnly_OS:
		gotSet.add(index)
		for item in config.items:
			role.AddItem(*item)
			tips += GlobalPrompt.Item_Tips % item
		
		backDays = role.GetDI32(EnumDisperseInt32.OldServerBackDays_OS)
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveOldPlayerBackReward, (backDays, index))
		
	role.Msg(2, 0, tips)
	role.SendObj(SyncOldPlayerOnly_OS, gotSet)


def RequestOldPlayerOnly_NS(role, msg):
	'''
	请求获取老玩家独享奖励(新服)NS = New Server
	@param role:
	@param msg:奖励索引
	'''
	#老玩家回归老服和回归新服的条件可能同时满足，如果同时满足的话，则只考虑是回归老服的情况
	if role.GetI1(EnumInt1.IsLocalServerBack) is True:
		return
	if role.GetI1(EnumInt1.IsOldServerBack) is False:
		return
	
	if OldPlayerConfig.IsStart is False:
		return
	
	if role.GetI16(EnumInt16.OldPlayerBackVersion) != OldPlayerConfig.ActVersion:
		return
	
	index = msg
	gotSet = role.GetObj(EnumObj.OldPlayerBack).setdefault(EnumOldPlayerOnly_NS, set())
	if index in gotSet:
		return
	
	config = OldPlayerConfig.OldPlayerOnlyNSDict.get(index)
	if config is None:
		return
	
	if role.GetDayBuyUnbindRMB_Q() < config.totalRecharge:
		return
	tips = GlobalPrompt.Reward_Tips

	with TraOldPlayerOnly_NS:
		gotSet.add(index)
		for item in config.items:
			role.AddItem(*item)
			tips += GlobalPrompt.Item_Tips % item
	role.Msg(2, 0, tips)
	role.SendObj(SyncOldPlayerOnly_NS, gotSet)


def RequestOldPlayerVIPOnly_OS(role, msg):
	'''
	请求获取老玩家贵族特权奖励(老服)OS = Old Server
	@param role:
	@param msg:奖励索引
	'''
	if role.GetI1(EnumInt1.IsLocalServerBack) is False:
		return
	if OldPlayerConfig.IsStart is False:
		return
	
	if role.GetI16(EnumInt16.OldPlayerBackVersion) != OldPlayerConfig.ActVersion:
		return
	
	index = msg
	gotSet = role.GetObj(EnumObj.OldPlayerBack).setdefault(EnumOldPlayerVIPOnly_OS, set())
	if index in gotSet:
		return
	config = OldPlayerConfig.OldPlayerVIPOnlyOSDict.get(index)
	if config is None:
		return
	
	if role.GetDayConsumeUnbindRMB() < config.totalCost:
		return
	if role.GetVIP() < config.needVIP:
		return
	
	tips = GlobalPrompt.Reward_Tips
	#这里添加日志并且发奖
	
	with TraOldPlayerVIPOnly_OS:
		gotSet.add(index)
		for item in config.items:
			role.AddItem(*item)
			tips += GlobalPrompt.Item_Tips % item
		backDays = role.GetDI32(EnumDisperseInt32.OldServerBackDays_OS)
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveOldPlayerBackReward, (backDays, index))

	role.Msg(2, 0, tips)
	role.SendObj(SyncOldPlayerVIPOnly_OS, gotSet)


def RequestOldPlayerVIPOnly_NS(role, msg):
	'''
	请求获取老玩家贵族特权独享奖励(新服)NS = New Server
	@param role:
	@param msg:奖励索引
	'''
	#老玩家回归老服和回归新服的条件可能同时满足，如果同时满足的话，则只考虑是回归老服的情况
	if role.GetI1(EnumInt1.IsLocalServerBack) is True:
		return
	if role.GetI1(EnumInt1.IsOldServerBack) is False:
		return
	
	if OldPlayerConfig.IsStart is False:
		return
	
	if role.GetI16(EnumInt16.OldPlayerBackVersion) != OldPlayerConfig.ActVersion:
		return
	
	index = msg
	gotSet = role.GetObj(EnumObj.OldPlayerBack).setdefault(EnumOldPlayerVIPOnly_NS, set())
	if index in gotSet:
		return
	
	config = OldPlayerConfig.OldPlayerVIPOnlyNSDict.get(index)
	if config is None:
		return
	
	oldVIP = role.GetI8(EnumInt8.OldServerVip)
	if oldVIP < config.needVIP:
		return
	
	if role.GetDayConsumeUnbindRMB() < config.totalCost:
		return
	
	tips = GlobalPrompt.Reward_Tips
	
	with TraOldPlayerVIPOnly_NS:
		gotSet.add(index)
		for item in config.items:
			role.AddItem(*item)
			tips += GlobalPrompt.Item_Tips % item
	role.Msg(2, 0, tips)
	role.SendObj(SyncOldPlayerVIPOnly_NS, gotSet)


def OnAfterBack(role, param):
	'''
	角色回流触发
	只有老服的玩家在回流后登录新的服务器才会触发Eve_RoleBackVIPLevel这个事件
	也就是说触发了事件的话肯定是在新服了
	Eve_RoleBackVIPLevel时间触发在AfterRoleLogin之后
	'''
	#只有在活动期间老服回归的才算作是老服回归的成员
	if OldPlayerConfig.IsStart is False:
		return
	
	with TraBackToNewServer:
		#设为从老服回流至新服的玩家
		role.SetI1(EnumInt1.IsOldServerBack, True)
		#设置老服回流活动版本号
		role.SetI16(EnumInt16.OldPlayerBackVersion, OldPlayerConfig.ActVersion)
		#记录在老服的VIP等级
		oldServerVip = param
		role.SetI8(EnumInt8.OldServerVip, oldServerVip)


def OnAfterRoleLogin(role, param):
	'''
	角色登录处理
	'''
	#只有在活动期间老服回归的才算作是老服回归的角色
	if OldPlayerConfig.IsStart is False:
		return
	
	#开服时间小于10天的服不能算老服
	if WorldData.GetWorldKaiFuDay() < EnumGameConfig.BackToOldNeedKaiFuDay:
		return
	
	if role.GetLevel() < EnumGameConfig.BackToOldNeedLevel:
		return
	
	lastSaveSeconds = role.GetDI32(EnumDisperseInt32.LastSaveUnixTime)
	lastSaveDays = (lastSaveSeconds + cDateTime.TimeZoneSeconds()) / 86400
	nowDays = cDateTime.Days()
	if nowDays - lastSaveDays < EnumGameConfig.BackToOldNeedUnloginDays:
		return
	
	with TraBackToOldServer:
		#记录角色回流的时间戳(天)
		role.SetDI32(EnumDisperseInt32.OldServerBackDays_OS, nowDays)
		#设置为老服回流至老服角色
		role.SetI1(EnumInt1.IsLocalServerBack, True)
		#设置老服回流至老服的版本号
		role.SetI16(EnumInt16.OldPlayerBackVersion, OldPlayerConfig.ActVersion)
		
		roleData = role.GetObj(EnumObj.OldPlayerBack)
		
		if EnumOldPlayerLoginReward_OS in roleData:
			del roleData[EnumOldPlayerLoginReward_OS]


def OnSyncRoleOtherData(role, param):
	'''
	同步角色其它数据
	'''
	if role.GetI1(EnumInt1.IsOldServerBack) is True:
		gotSet2 = role.GetObj(EnumObj.OldPlayerBack).get(EnumOldPlayerLevelReward_NS, set())
		role.SendObj(SyncOldPlayerLevelReward_NS, gotSet2)
		
	if role.GetI1(EnumInt1.IsLocalServerBack) is True:
		gotSet1 = role.GetObj(EnumObj.OldPlayerBack).get(EnumOldPlayerLoginReward_OS, set())
		if OldPlayerConfig.IsStart is True:
			gotset3 = role.GetObj(EnumObj.OldPlayerBack).get(EnumOldPlayerOnly_OS, set())
			gotset5 = role.GetObj(EnumObj.OldPlayerBack).get(EnumOldPlayerVIPOnly_OS, set())
			role.SendObj(SyncOldPlayerOnly_OS, gotset3)
			role.SendObj(SyncOldPlayerVIPOnly_OS, gotset5)
		role.SendObj(SyncOldPlayerLoginReward_OS, gotSet1)
	
	elif role.GetI1(EnumInt1.IsOldServerBack) is True:
		if OldPlayerConfig.IsStart is True:
			gotset4 = role.GetObj(EnumObj.OldPlayerBack).get(EnumOldPlayerOnly_NS, set())
			gotset6 = role.GetObj(EnumObj.OldPlayerBack).get(EnumOldPlayerVIPOnly_NS, set())
			role.SendObj(SyncOldPlayerOnly_NS, gotset4)
			role.SendObj(SyncOldPlayerVIPOnly_NS, gotset6)
	
	role.SendObj(OldPlayerConfig.SyncOldPlayerActStatu, (OldPlayerConfig.IsStart, OldPlayerConfig.EndTime, OldPlayerConfig.ActVersion))


def RoleDayClear(role, param):
	roleData = role.GetObj(EnumObj.OldPlayerBack)
	gotset3 = roleData[EnumOldPlayerOnly_OS] = set()
	gotset4 = roleData[EnumOldPlayerOnly_NS] = set()
	gotset5 = roleData[EnumOldPlayerVIPOnly_OS] = set()
	gotset6 = roleData[EnumOldPlayerVIPOnly_NS] = set()
	
	if OldPlayerConfig.IsStart is False:
		return
	
	if role.GetI1(EnumInt1.IsLocalServerBack) is True:
		role.SendObj(SyncOldPlayerOnly_OS, gotset3)
		role.SendObj(SyncOldPlayerVIPOnly_OS, gotset5)
	
	elif role.GetI1(EnumInt1.IsOldServerBack) is True:
		role.SendObj(SyncOldPlayerOnly_NS, gotset4)
		role.SendObj(SyncOldPlayerVIPOnly_NS, gotset6)


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.EnvIsFT():
		
		if not Environment.IsCross:
			Event.RegEvent(Event.Eve_RoleBackVIPLevel, OnAfterBack)
			Event.RegEvent(Event.Eve_AfterLogin, OnAfterRoleLogin)
			Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestOldPlayerLoginReward_OS", "客户端请求获取回归登录大礼(老服)"), RequestLoginReward_OS)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestOldPlayerLevelReward_NS", "客户端请求获取回归等级大礼(新服)"), RequestLevelReward_NS)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestOldPlayerOnly_OS", "客户端请求获取老玩家独享奖励(老服)"), RequestOldPlayerOnly_OS)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestOldPlayerOnly_NS", "客户端请求获取老玩家独享奖励(新服)"), RequestOldPlayerOnly_NS)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestOldPlayerVIPOnly_OS", "客户端请求获取老玩家贵族特权奖励(老服)"), RequestOldPlayerVIPOnly_OS)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestOldPlayerVIPOnly_NS", "客户端请求获取老玩家贵族特权奖励(新服)"), RequestOldPlayerVIPOnly_NS)
		

