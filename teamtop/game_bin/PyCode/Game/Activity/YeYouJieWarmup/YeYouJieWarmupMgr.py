#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.YeYouJieWarmup.YeYouJieWarmupMgr")
#===============================================================================
# 页游节预热
#===============================================================================
import cRoleMgr
import cDateTime
import Environment
import DynamicPath
import cNetMessage
import cComplexServer
from Util import Time
from Game.Role import Event
from Util.File import TabFile
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from Game.Role.Data import EnumObj, EnumDayInt1, EnumInt8
from Game.Activity.YeYouJieWarmup import YeYouJieWarmupConfig

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("YeYouJieWarmUp")
	
	IsStart = False
	EndSeconds = 0
	
	#日志
	TraYeYouJieWarmupLoginRewards = AutoLog.AutoTransaction("TraYeYouJieWarmupLoginRewards", "腾讯页游节活动每日登录奖励")
	TraYeYouJieWarmupRechargeRewards = AutoLog.AutoTransaction("TraYeYouJieWarmupRechargeRewards", "腾讯页游节活动每日充值奖励")
	
	#消息
	SyncYeYouJieWarmupTime = AutoMessage.AllotMessage("SyncYeYouJieWarmupTime", "同步页游节活动开启结束时间")
	SyncYeYouJieWarmupRoleLoginRewardsGot = AutoMessage.AllotMessage("SyncYeYouJieWarmupRoleLoginRewardsGot", "同步页游节活动角色已领取登录奖励数据")


class ShiJianKongZhiConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("ShiJianKongZhi.txt")
	def __init__(self):
		self.beginTime = self.GetDatetimeByString				#开始时间
		self.endTime = self.GetDatetimeByString					#结束时间
	
	def Active(self):
		#开始时间戳
		beginSeconds = Time.DateTime2UnitTime(self.beginTime)
		#结束时间戳
		endSeconds = Time.DateTime2UnitTime(self.endTime)
		
		if beginSeconds >= endSeconds:
			print "GE_EXC,YeYouJieWarmupConfig TimeControl Error start_time %s,end_time:%s" % (beginSeconds, endSeconds)
			return
		
		#当前时间戳
		nowSeconds = cDateTime.Seconds()
		
		if beginSeconds <= nowSeconds < endSeconds:
			#在开始和结束时间戳之间, 激活
			Start(None, endSeconds)
			cComplexServer.RegTick(endSeconds - nowSeconds , End)
			
		elif nowSeconds < beginSeconds:
			#在开始时间戳之前
			cComplexServer.RegTick(beginSeconds - nowSeconds, Start, endSeconds)
			cComplexServer.RegTick(endSeconds - nowSeconds , End)


def Start(callargv, param):
	global IsStart, EndSeconds
	if IsStart is True:
		print "GE_EXC, YeYouJieWarmUp has been started"
		return
	
	EndSeconds = param
	IsStart = True
			
	#同步客户端活动开启
	cNetMessage.PackPyMsg(SyncYeYouJieWarmupTime, (IsStart, EndSeconds))
	cRoleMgr.BroadMsg()


def End(callargv, param):
	global IsStart, EndSeconds
	if IsStart is False:
		print "GE_EXC, YeYouJieWarmUp has been ended"
		return
	IsStart = False
	EndSeconds = 0
	#同步客户端活动开启
	cNetMessage.PackPyMsg(SyncYeYouJieWarmupTime, (IsStart, EndSeconds))
	cRoleMgr.BroadMsg()


def LoadShiJianKongZhiConfig():
	for cfg in ShiJianKongZhiConfig.ToClassType():
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in ShiJianKongZhiConfig in YeYouJieWarmUp"
			return
		#无依赖, 起服触发
		cfg.Active()

	
def RequestGetLoginRewards(role, msg):
	'''
	客户端请求领取每日登录奖励
	@param role:
	@param msg:奖励index
	'''
	#角色等级不满足条件
	if role.GetLevel() < EnumGameConfig.YeYouJieWarmUpNeedLevel:
		return
	
	#不是活动时间
	if IsStart is False:
		return
	
	index = msg
	gotSet = role.GetObj(EnumObj.YeYouJieWarmup).setdefault(1, set())
	#已经领取的不能重复领取
	if index in gotSet:
		return
	
	config = YeYouJieWarmupConfig.LoginRewardsConfigDict.get(index)
	if config is None:
		print "GE_EXC, GE_EXC, error config = YeYouJieWarmupConfig.LoginRewardsConfigDict.get(%s) for role(%s)" % (index, role.GetRoleID())
		return
	
	loginDays = role.GetI8(EnumInt8.YeYouJieWarmupLoginDays)
	if loginDays < config.Days:
		return
	
	with TraYeYouJieWarmupLoginRewards:
		gotSet.add(index)
		role.AddItem(*config.Items)
	
	role.SendObj(SyncYeYouJieWarmupRoleLoginRewardsGot, gotSet)
	role.Msg(2, 0, GlobalPrompt.YeYouJieWarmupLoginRewardsTip)


def RequestGetRechargeRewards(role, msg):
	'''
	客户端请求领取每日充值奖励
	@param role:
	@param msg:
	'''
	#角色等级不满足条件
	if role.GetLevel() < EnumGameConfig.YeYouJieWarmUpNeedLevel:
		return
	
	#不是活动时间
	if IsStart is False:
		return
	
	if role.GetDI1(EnumDayInt1.YeYouJieWarmupHasGotRechargeRewards):
		return
	
	#当日没有充值
	dayBuyUnbindRMB = role.GetDayBuyUnbindRMB_Q()
	if dayBuyUnbindRMB <= 0:
		return
	
	roleLevel = role.GetLevel()
	config = YeYouJieWarmupConfig.RechargeRewardsConfigDict.get(roleLevel)
	if config is None:
		print "GE_EXC, error config = YeYouJieWarmupConfig.RechargeRewardsConfigDict.get(%s) for role(%s)" % (roleLevel, role.GetRoleID())
		return
	
	with TraYeYouJieWarmupRechargeRewards:
		role.SetDI1(EnumDayInt1.YeYouJieWarmupHasGotRechargeRewards, True)
		role.IncMoney(config.Money)
		for item in config.Items:
			role.AddItem(*item)
	
	role.Msg(2, 0, GlobalPrompt.YeYouJieWarmupRechargeRewardsTips)


def SyncRoleOtherData(role, param):
	#活动期间角色上线同步登录奖励领取数据
	if IsStart is False:
		return
	
	gotSet = role.GetObj(EnumObj.YeYouJieWarmup).get(1, set())
	role.SendObj(SyncYeYouJieWarmupRoleLoginRewardsGot, gotSet)
	role.SendObj(SyncYeYouJieWarmupTime, (IsStart, EndSeconds))


def DailyClear(role, param):
	'''
	每日清理,仅在在线跨天及每日第一次登录的时候触发
	'''
	if IsStart is False:
		return
	
	hasLoginToday = role.GetDI1(EnumDayInt1.YeYouJieWarmupHasLoginToday)
	if hasLoginToday:
		return
	
	role.SetDI1(EnumDayInt1.YeYouJieWarmupHasLoginToday, True)
	role.IncI8(EnumInt8.YeYouJieWarmupLoginDays, 1)


if "_HasLoad" not in dir():
	#逻辑进程
	if Environment.HasLogic:
		#语言环境(开发环境,腾讯，腾讯联盟)
		if Environment.IsDevelop or Environment.EnvIsQQ() or Environment.EnvIsQQUnion():
			Event.RegEvent(Event.Eve_RoleDayClear, DailyClear)
			
			#非跨服环境
			if not Environment.IsCross:
				LoadShiJianKongZhiConfig()
				#事件触发
				Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
				#客户端请求
				cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestGetLoginRewardsYeYouJieWarmup", "腾讯页游节预热活动请求获取登录奖励"), RequestGetLoginRewards)
				cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestGetRechangeRewardsYeYouJieWarmup", "腾讯页游节预热活动请求获取充值奖励"), RequestGetRechargeRewards)
