#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.OldPlayer.OldPlayerConfig")
#===============================================================================
# 老玩家回流活动配置
#===============================================================================
import time
import DynamicPath
import Environment
from Util.File import TabFile
import cDateTime
import cComplexServer
from Common.Message import AutoMessage
import cNetMessage
import cRoleMgr

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("OldPlayerBack")
	
	ActVersion = 0
	IsStart = False
	EndTime = 0
	LoginRewardOSDict = {}
	LevelRewardNSDict = {}
	OldPlayerOnlyOSDict = {}
	OldPlayerOnlyNSDict = {}
	OldPlayerVIPOnlyOSDict = {}
	OldPlayerVIPOnlyNSDict = {}
	#消息
	SyncOldPlayerActStatu = AutoMessage.AllotMessage("SyncOldPlayerActStatu", "同步老玩家回流活动开启情况")


class OldPlayerBackActiveConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("ShiJianKongZhi.txt")
	def __init__(self):
		self.actVersion = int									#活动版本号
		self.beginTime = self.GetDatetimeByString				#开始时间
		self.endTime = self.GetDatetimeByString					#结束时间
	
	def Active(self):
		#开始时间戳
		beginTime = int(time.mktime(self.beginTime.timetuple()))
		#结束时间戳
		endTime = int(time.mktime(self.endTime.timetuple()))
		
		if endTime <= beginTime:
			print "GE_EXC, endTime <= beginTime in OldPlayerBackActiveConfig"
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
		print "GE_EXC,OldPlayerBackActive has been started"
		return
	IsStart = True
	EndTime, ActVersion = param
	#同步客户端活动开启
	cNetMessage.PackPyMsg(SyncOldPlayerActStatu, (IsStart, EndTime, ActVersion))
	cRoleMgr.BroadMsg()


def End(callargv, param):
	global IsStart, EndTime, ActVersion
	if IsStart is False:
		print "GE_EXC,OldPlayerBackActive has been ended"
		return
	IsStart = False
	EndTime = 0
	ActVersion = 0
	#同步客户端活动开启
	cNetMessage.PackPyMsg(SyncOldPlayerActStatu, (IsStart, EndTime, ActVersion))
	cRoleMgr.BroadMsg()


def LoadOldPlayerBackActiveConfig():
	for cfg in OldPlayerBackActiveConfig.ToClassType():
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in OldPlayerBackActiveConfig"
			return
		#无依赖, 起服触发
		cfg.Active()


class LoginRewardOS(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("HuiGuiDengluDaliLaoFu.txt")
	def __init__(self):
		self.index = int						#活动id
		self.loginDays = int					#需要登录的天数
		self.items = eval						#奖励道具
		self.bindRMB = int						#奖励魔晶
		self.money = int						#奖励金币


class LevelRewardNS(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("HuiGuiDengjiDaliXinFu.txt")
	def __init__(self):
		self.index = int						#活动id
		self.needLevel = int					#需要的角色等级
		self.items = eval						#奖励道具
		self.bindRMB = int						#奖励魔晶
		self.money = int						#奖励金币


class OldPlayerOnlyOS(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("DuXiangJiangLiLaoFu.txt")
	def __init__(self):
		self.index = int						#活动id
		self.totalRecharge = int				#累计充值
		self.items = eval						#奖励道具


class OldPlayerOnlyNS(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("DuXiangJiangLiXinFu.txt")
	def __init__(self):
		self.index = int						#活动id
		self.totalRecharge = int				#累计充值
		self.items = eval						#奖励道具


class OldPlayerVIPOnlyOS(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("GuizuDuXiangLaoFu.txt")
	def __init__(self):
		self.index = int						#活动id
		self.totalCost = int					#累计消费
		self.items = eval						#奖励道具
		self.needVIP = int						#需要本服的VIP等级


class OldPlayerVIPOnlyNS(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("GuizuDuXiangXinFu.txt")
	def __init__(self):
		self.index = int						#活动id
		self.totalCost = int					#累计消费
		self.items = eval						#奖励道具
		self.needVIP = int						#需要老服的VIP等级


def LoadLoginRewardOS():
	global LoginRewardOSDict
	for config in LoginRewardOS.ToClassType():
		if config.index in LoginRewardOSDict:
			print "GE_EXC,repeat index(%s) in LoginRewardOSDict " % config.index
		LoginRewardOSDict[config.index] = config


def LoadLevelRewardNS():
	global LevelRewardNSDict
	for config in LevelRewardNS.ToClassType():
		if config.index in LevelRewardNSDict:
			print "GE_EXC,repeat index(%s) in LevelRewardNSDict " % config.index
		LevelRewardNSDict[config.index] = config
		
		
def LoadOldPlayerOnlyOS():
	global OldPlayerOnlyOSDict
	for config in OldPlayerOnlyOS.ToClassType():
		if config.index in OldPlayerOnlyOSDict:
			print "GE_EXC,repeat index(%s) in OldPlayerOnlyOSDict " % config.index
		OldPlayerOnlyOSDict[config.index] = config
		
		
def LoadOldPlayerOnlyNS():
	global OldPlayerOnlyNSDict
	for config in OldPlayerOnlyNS.ToClassType():
		if config.index in OldPlayerOnlyNSDict:
			print "GE_EXC,repeat index(%s) in OldPlayerOnlyNSDict " % config.index
		OldPlayerOnlyNSDict[config.index] = config
		
		
def LoadOldPlayerVIPOnlyOS():
	global OldPlayerVIPOnlyOSDict
	for config in OldPlayerVIPOnlyOS.ToClassType():
		if config.index in OldPlayerVIPOnlyOSDict:
			print "GE_EXC,repeat index(%s) in OldPlayerVIPOnlyOSDict " % config.index
		OldPlayerVIPOnlyOSDict[config.index] = config
		
		
def LoadOldPlayerVIPOnlyNS():
	global OldPlayerVIPOnlyNSDict
	for config in OldPlayerVIPOnlyNS.ToClassType():
		if config.index in OldPlayerVIPOnlyNSDict:
			print "GE_EXC,repeat index(%s) in OldPlayerVIPOnlyNSDict " % config.index
		OldPlayerVIPOnlyNSDict[config.index] = config			


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadLoginRewardOS()
		LoadLevelRewardNS()
		LoadOldPlayerOnlyOS()
		LoadOldPlayerOnlyNS()
		LoadOldPlayerVIPOnlyOS()
		LoadOldPlayerVIPOnlyNS()
		LoadOldPlayerBackActiveConfig()
