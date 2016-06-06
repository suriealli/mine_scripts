#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.VIP.XinYueVIP.XinYueVIP")
#===============================================================================
# 心悦特权
#===============================================================================
import cDateTime
import Environment
import cRoleMgr
from Util import Time
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from Game.Role import Event
from Game.Role.Data import EnumObj, EnumInt8
from Game.VIP.XinYueVIP import XinYueVIPConfig
from Game.ThirdParty import QQLog

LEVEL_VIP_TYPE = 2	#VIP等级奖励
DAY_REWARD_TYPE = 3	#每日奖励
WEEK_REWARD_TYPE = 4#每周奖励
MONTH_REWARD_TYPE =5#每月奖励

if "_HasLoad" not in dir():
	Syn_XinYue_Data = AutoMessage.AllotMessage("Syn_XinYue_Data", "同步心悦特权各种状态")
	
	#日志
	XYVipRoleLevelReward = AutoLog.AutoTransaction("XYVipRoleLevelReward", "心悦玩家等级礼包")
	XYVipReward = AutoLog.AutoTransaction("XYVipReward", "心悦礼包")
	
def GetRoleLevelReward(role, param):
	'''
	玩家领取心悦玩家等级礼包
	@param role:
	@param param:
	'''
	index = param
	
	XinYueVIPData = role.GetObj(EnumObj.XinYueVIPData)
	GetedData = XinYueVIPData.get(1, set())
	if index in GetedData:
		return
	
	cfg = XinYueVIPConfig.XINYUE_ROLE_LEVEL_DICT.get(index)
	if not cfg:
		print "GE_EXC,can not find index(%s) in XinYueVIP.RoleGetRoleLevelReward" % index
		return
	
	if role.GetI8(EnumInt8.QQXinYueVipLevel) < cfg.needVIPLevel:
		return
	
	if role.GetLevel() < cfg.needLevel:
		return
	
	with XYVipRoleLevelReward:
		XinYueVIPData[1].add(index)
		
		tips = GlobalPrompt.Reward_Tips
		if cfg.codingRrward:
			for reward in cfg.codingRrward:
				role.AddItem(*reward)
				tips += GlobalPrompt.Item_Tips % (reward[0], reward[1])
				QQLog.LogXinYueLiBao(role, reward[0], reward[1])
		SynXinYueData(role)
		role.Msg(2, 0, tips)
		
def RoleGetVIPReward(role, param):
	'''
	客户端请求领取奖励
	@param role:
	@param param:
	'''
	index, rewardType = param
	
	cfg = XinYueVIPConfig.XINYUE_REWARD_DICT.get(index)
	if not cfg:
		print "GE_EXC,can not find index(%s) in XinYueVIP.RoleGetVIPReward" % index
		return
	
	if role.GetI8(EnumInt8.QQXinYueVipLevel) != cfg.needVIPLevel:
		return
	
	XinYueVIPData = role.GetObj(EnumObj.XinYueVIPData)
	if rewardType == LEVEL_VIP_TYPE:
		if index in XinYueVIPData.get(2, set()):
			return
		XinYueVIPData[2].add(index)
		GiveReward(role, cfg.VIPLevelReward)
	elif rewardType == DAY_REWARD_TYPE:
		if index in XinYueVIPData.get(3, set()):
			return
		XinYueVIPData[3].add(index)
		GiveReward(role, cfg.dayReward)
	elif rewardType == WEEK_REWARD_TYPE:
		if index in XinYueVIPData.get(4, set()):
			return
		XinYueVIPData[4].add(index)
		#记录领取时的周数
		XinYueVIPData[6] = Time.GetYearWeek(cDateTime.Now())
		
		GiveReward(role, cfg.weekReward)
	elif rewardType == MONTH_REWARD_TYPE:
		if index in XinYueVIPData.get(5, set()):
			return
		XinYueVIPData[5].add(index)
		#记录领取奖励时的年数和周数
		XinYueVIPData[7] = [cDateTime.Year(),cDateTime.Month()]
		
		GiveReward(role, cfg.monthReward)
	else:
		return
	SynXinYueData(role)
	
def GiveReward(role, rewards):
	with XYVipReward:
		tips = GlobalPrompt.Reward_Tips
		if rewards:
			for reward in rewards:
				role.AddItem(*reward)
				tips += GlobalPrompt.Item_Tips % (reward[0], reward[1])
				QQLog.LogXinYueLiBao(role, reward[0], reward[1])
		role.Msg(2, 0, tips)
	
def SynXinYueData(role):
	role.SendObj(Syn_XinYue_Data, role.GetObj(EnumObj.XinYueVIPData))
#==============================================================
def OnRoleLogin(role, param):
	#玩家登录
	XinYueVIPData = role.GetObj(EnumObj.XinYueVIPData)
	if 1 not in XinYueVIPData:#玩家等级级礼包
		XinYueVIPData[1] = set()
	if 2 not in XinYueVIPData:#vip等级礼包
		XinYueVIPData[2] = set()
	if 3 not in XinYueVIPData:#每日礼包
		XinYueVIPData[3] = set()
	if 4 not in XinYueVIPData:#每周礼包
		XinYueVIPData[4] = set()
	if 5 not in XinYueVIPData:#每月礼包
		XinYueVIPData[5] = set()
	if 6 not in XinYueVIPData:#每周领奖励时记录一年的第几周数
		XinYueVIPData[6] = 0
	if 7 not in XinYueVIPData:#每月领奖时记录的年数和月数
		XinYueVIPData[7] = []
	SynXinYueData(role)
		
def SyncRoleOtherData(role, param):
	SynXinYueData(role)
	
def RoleDayClear(role, param):
	#每日清理
	XinYueVIPData = role.GetObj(EnumObj.XinYueVIPData)
	#清理每日礼包
	XinYueVIPData[3] = set()
	#检测每周，每月礼包是否要清理了
	weekData = XinYueVIPData.get(6, 0)
	if weekData:
		#一年的第几周
		nowWeek = Time.GetYearWeek(cDateTime.Now())
		if nowWeek != weekData:
			#不同周，证明跨周了清理
			XinYueVIPData[4] = set()
			XinYueVIPData[6] = 0
	else:
		if XinYueVIPData.get(4) and Time.GetYearWeek(cDateTime.Now()) != 0:
			XinYueVIPData[4] = set()
		
	monthData = XinYueVIPData.get(7, [])
	if monthData and len(monthData) == 2:
		yearNum, monthNum = monthData
		#获取当前的年数和月数
		nowYear, nowMonth = cDateTime.Year(),cDateTime.Month()
		if yearNum != nowYear:
			#年不相同，证明跨年了，可以清理
			XinYueVIPData[5] = set()
			XinYueVIPData[7] = []
		else:
			if monthNum != nowMonth:
				#同年不同月，清理之
				XinYueVIPData[5] = set()
				XinYueVIPData[7] = []
	SynXinYueData(role)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_AfterLogin, OnRoleLogin)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
	
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("XinYue_Get_RoleLevel_Reward", "玩家领取心悦玩家等级礼包"), GetRoleLevelReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("XinYue_Get_Reward", "玩家领取心悦奖励"), RoleGetVIPReward)
		