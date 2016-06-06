#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.OldRoleBackFT.OldRoleBackFT")
#===============================================================================
# 繁体版老玩家回流
#===============================================================================
import cDateTime
import cRoleMgr
import cNetMessage
import DynamicPath
import Environment
import cComplexServer
from Util import Time
from Util.File import TabFile
from Game.Role import Event
from Game.Role.Mail import Mail
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Role.Data import EnumDisperseInt32, EnumInt1, EnumInt16, EnumObj, EnumInt8
from Game.Activity.OldRoleBackFT import OldRoleBackFTConfig


if "_HasLoad" not in dir():
	IsStart = False
	ActVersion = 0
	EndTime = 0
	NeedLevel = 40
	BackNeedUnloginDays = 10
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("OldRoleBakcFT")
	
	#日志
	TraOldRoleBackFT = AutoLog.AutoTransaction("TraOldRoleBackFT", "【繁体版】老玩家回流")
	TraOldRoleBackFTVersion = AutoLog.AutoTransaction("TraOldRoleBackFTVersion", "【繁体版】老玩家回流版本号更迭")
	TraOldRoleBackFTRechareAward = AutoLog.AutoTransaction("TraOldRoleBackFTRechareAward", "【繁体版】老玩家回流首充奖励")
	TraOldRoleBackFTBackAward = AutoLog.AutoTransaction("TraOldRoleBackFTBackAward", "【繁体版】老玩家回流登录奖励")
	TraOldRoleBackFTBackSignIn = AutoLog.AutoTransaction("TraOldRoleBackFTBackSignIn", "【繁体版】老玩家回流签到")
	TraOldRoleBackFTBackSignInRemedy = AutoLog.AutoTransaction("TraOldRoleBackFTBackSignInRemedy", "【繁体版】老玩家回流补签")
	
	#消息
	SyncOldRoleBackFTStatu = AutoMessage.AllotMessage("SyncOldRoleBackFTStatu", "【繁体版】同步老玩家回流活动开启状态")
	SyncOldRoleBackFTSignInData = AutoMessage.AllotMessage("SyncOldRoleBackFTSignInData", "【繁体版】同步老玩家回流活动签到数据")
	

class OldRoleBackFTTimeConfig(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("ShiJianKongZhi.txt")
	def __init__(self):
		self.actVersion = int									#活动版本号
		self.beginTime = self.GetDatetimeByString				#开始时间
		self.endTime = self.GetDatetimeByString					#结束时间
	
	def Active(self):
		#开始时间戳
		beginTime = Time.DateTime2UnitTime(self.beginTime)
		#结束时间戳
		endTime = Time.DateTime2UnitTime(self.endTime)
		
		if endTime <= beginTime:
			print "GE_EXC, endTime <= beginTime in OldRoleBackFTTimeConfig"
			return
		
		#当前时间戳
		nowTime = cDateTime.Seconds()
		
		if beginTime <= nowTime < endTime:
			#在开始和结束时间戳之间, 激活
			Start(None, (endTime, self.actVersion))
			cComplexServer.RegTick(endTime - nowTime , End)
			
		elif nowTime < beginTime:
			#在开始时间戳之前
			cComplexServer.RegTick(beginTime - nowTime, Start, (endTime, self.actVersion))
			cComplexServer.RegTick(endTime - nowTime , End)


def Start(callargv, param):
	global IsStart, EndTime, ActVersion
	if IsStart is True:
		print "GE_EXC,OldRoleBackFT has been started"
		return
	#下两行不能调换顺序，因为要确保IsStart为真的时候，活动版本号已经初始化了
	EndTime, ActVersion = param
	IsStart = True
	
	for theRole in cRoleMgr.GetAllRole():
		if theRole.IsKick():
			continue
		
		if  theRole.GetI16(EnumInt16.OldRoleBackFTVersion) < ActVersion:
			with TraOldRoleBackFTVersion:
				#清空上次活动的数据
				theRole.SetI1(EnumInt1.Is_FT_OldRoleBack, False)
				#干掉签到数据
				theRole.SetI8(EnumInt8.FTOldRoleBackSingUpRemedyCnt, 0)
				theRole.GetObj(EnumObj.OldRoleback_FT)[1] = set()
				
				#干掉首次登录奖励数据
				theRole.SetI1(EnumInt1.FT_OldRoleBack_HasGotLoginReward, False)
				#干掉首充额外奖励数据
				theRole.SetI1(EnumInt1.FT_OldRoleBack_HasGotChargeReward, False)
				#设置活动版本号
				theRole.SetI16(EnumInt16.OldRoleBackFTVersion, ActVersion)
		
		
	#同步客户端活动开启
	cNetMessage.PackPyMsg(SyncOldRoleBackFTStatu, (IsStart, EndTime))
	cRoleMgr.BroadMsg()


def End(callargv, param):
	global IsStart, EndTime, ActVersion
	if IsStart is False:
		print "GE_EXC,OldRoleBackFT has been ended"
		return
	IsStart = False
	EndTime = 0
	ActVersion = 0
	#同步客户端活动开启
	cNetMessage.PackPyMsg(SyncOldRoleBackFTStatu, (IsStart, EndTime))
	cRoleMgr.BroadMsg()


def LoadOldRoleBackFTTimeConfig():
	for cfg in OldRoleBackFTTimeConfig.ToClassType():
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in OldRoleBackFTTimeConfig"
			return
		#无依赖, 起服触发
		cfg.Active()


def OnAfterRoleLogin(role, param):
	'''
	角色登录处理
	'''
	if IsStart is False:
		return
	
	if role.GetI16(EnumInt16.OldRoleBackFTVersion) < ActVersion:
		#清空上次活动的数据
		with TraOldRoleBackFTVersion:
			role.SetI1(EnumInt1.Is_FT_OldRoleBack, False)
			#干掉签到数据
			role.SetI8(EnumInt8.FTOldRoleBackSingUpRemedyCnt, 0)
			role.GetObj(EnumObj.OldRoleback_FT)[1] = set()
				
			#干掉首次登录奖励数据
			role.SetI1(EnumInt1.FT_OldRoleBack_HasGotLoginReward, False)
			#干掉首充额外奖励数据
			role.SetI1(EnumInt1.FT_OldRoleBack_HasGotChargeReward, False)
			#设置活动版本号
			role.SetI16(EnumInt16.OldRoleBackFTVersion, ActVersion)
		
	elif role.GetI16(EnumInt16.OldRoleBackFTVersion) > ActVersion:
		print "role(%s) GE_EXC,OldRoleBackFTVersion > now ActVersion" % role.GetRoleID()
		return
	
	else:
		return

	lastSaveSeconds = role.GetDI32(EnumDisperseInt32.LastSaveUnixTime)
	#角色第一次登录
	if lastSaveSeconds == 0:
		return
	if role.GetLevel() < 2:
		return
	
	lastSaveDays = (lastSaveSeconds + cDateTime.TimeZoneSeconds()) / 86400
	nowDays = cDateTime.Days()
	if nowDays - lastSaveDays < BackNeedUnloginDays:
		return
	
	#记录回流时间戳
	with TraOldRoleBackFT:
		role.SetI1(EnumInt1.Is_FT_OldRoleBack, True)
		role.SetDI32(EnumDisperseInt32.OldRoleBackDays_FT, nowDays)
	
	#如果已经领取过回流登录奖励
	if role.GetI1(EnumInt1.FT_OldRoleBack_HasGotLoginReward):
		return
	
	#发邮件奖励
	with TraOldRoleBackFTBackAward:
		role.SetI1(EnumInt1.FT_OldRoleBack_HasGotLoginReward, True)
		roleID = role.GetRoleID()
		Mail.SendMail(roleID,
					GlobalPrompt.OldRoleBackFTMailTitle1,
					 GlobalPrompt.OldRoleBackFTMailSender,
					 GlobalPrompt.OldRoleBackFTMailContent1 ,
					 money=EnumGameConfig.FTOldRoleBackLoginMoney,
					 items=EnumGameConfig.FTOldRoleBackLoginItems,
					 bindrmb=EnumGameConfig.FTOldRoleBackLoginbindRMB,
					 unbindrmb=EnumGameConfig.FTOldRoleBackLoginUnbindRMB)


def RequestSignIn(role, msg):
	'''
	客户端请求签到
	'''
	#活动没开始
	if IsStart is False:
		return
	
	if role.GetLevel() < NeedLevel:
		return
	
	#版本号不对
	if role.GetI16(EnumInt16.OldRoleBackFTVersion) != ActVersion:
		return
	#不是回流角色
	if role.GetI1(EnumInt1.Is_FT_OldRoleBack) is False:
		return
	
	#获取角色回流的时间戳
	backDays = role.GetDI32(EnumDisperseInt32.OldRoleBackDays_FT)
	nowDays = cDateTime.Days()
	#今天是第几天
	nowWhichDay = nowDays - backDays + 1
	gotSet = role.GetObj(EnumObj.OldRoleback_FT).setdefault(1, {})
	
	purposeDay = msg
	
	if purposeDay in gotSet:
		return
	#如果目标日期大过今天
	if purposeDay > nowWhichDay:
		return
	
	#是否补签
	isRemedy = False
	if nowWhichDay != purposeDay:
		isRemedy = True
	
	config = OldRoleBackFTConfig.SignUpConfigDict.get(purposeDay)
	if not config:
		print "GE_EXC,error config = OldRoleBackFTConfig.SignUpConfigDict.get(%s)" % purposeDay
		return
	
	if isRemedy:
		oldCnt = role.GetI8(EnumInt8.FTOldRoleBackSingUpRemedyCnt)
		nowCnt = oldCnt + 1
		price = OldRoleBackFTConfig.SignUpRemedyPriceDict.get(nowCnt)
		if not price:
			print "GE_EXC,error OldRoleBackFTConfig.SignUpRemedyPriceDict.get(%s) for role(%s)" % (nowCnt, role.GetRoleID())
			return
		if role.GetUnbindRMB() < price:
			return
		
		with TraOldRoleBackFTBackSignIn:
			gotSet.add(purposeDay)
			role.IncI8(EnumInt8.FTOldRoleBackSingUpRemedyCnt, 1)
			role.DecUnbindRMB(price)
			if config.money:
				role.IncMoney(config.money)
			if config.bindRMB:
				role.IncBindRMB(config.bindRMB)
			if config.unbindRMB:
				role.IncUnbindRMB_S(config.unbindRMB)
			if config.items:
				for item in config.items:
					role.AddItem(*item)
		
	else:
		with TraOldRoleBackFTBackSignIn:
			gotSet.add(purposeDay)
			if config.money:
				role.IncMoney(config.money)
			if config.bindRMB:
				role.IncBindRMB(config.bindRMB)
			if config.unbindRMB:
				role.IncUnbindRMB_S(config.unbindRMB)
			if config.items:
				for item in config.items:
					role.AddItem(*item)
	
	role.SendObj(SyncOldRoleBackFTSignInData, gotSet)


def AfterChangeUnbindRMB_Q(role, params):
	'''
	回归首充奖励
	'''
	if IsStart is False:
		return
	if role.GetLevel() < NeedLevel:
		return
	
	oldValue, newValue = params
	chargeValue = newValue - oldValue
	if chargeValue <= 0:
		return
	
	#版本号不对
	if role.GetI16(EnumInt16.OldRoleBackFTVersion) != ActVersion:
		return
	#不是回流角色
	if role.GetI1(EnumInt1.Is_FT_OldRoleBack) is False:
		return
	
	#已经领取过这个奖励了
	if role.GetI1(EnumInt1.FT_OldRoleBack_HasGotChargeReward):
		return
		
	rewardValue = min(chargeValue, 10000)
	
	with TraOldRoleBackFTRechareAward:
		role.SetI1(EnumInt1.FT_OldRoleBack_HasGotChargeReward, True)
		roleID = role.GetRoleID()
		Mail.SendMail(roleID, GlobalPrompt.OldRoleBackFTMailTitle2,
				GlobalPrompt.OldRoleBackFTMailSender,
				GlobalPrompt.OldRoleBackFTMailContent2 % (chargeValue, rewardValue) ,
				unbindrmb=rewardValue)


def SyncRoleOtherData(role, param):
	'''
	同步角色其它信息
	'''
	if IsStart is False:
		return
	
	gotSet = role.GetObj(EnumObj.OldRoleback_FT).get(1, {})
	role.SendObj(SyncOldRoleBackFTSignInData, gotSet)
	role.SendObj(SyncOldRoleBackFTStatu, (IsStart, EndTime))


if "_HasLoad" not in dir():
	#注意，这个只在繁体版才有
	if Environment.HasLogic and not Environment.IsCross and (Environment.EnvIsFT() or Environment.IsDevelop):
		LoadOldRoleBackFTTimeConfig()
		Event.RegEvent(Event.AfterChangeUnbindRMB_Q, AfterChangeUnbindRMB_Q)
		Event.RegEvent(Event.Eve_AfterLogin, OnAfterRoleLogin)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestSignInOldRoleBackFT", "【繁体版】老玩家回流活动客户端请求签到"), RequestSignIn)

