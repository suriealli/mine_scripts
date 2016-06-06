#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ValentineDay.ValentineVersionMgr")
#===============================================================================
# 魅力情人节活动版本管理  此活动版本号不支持热更
#===============================================================================
import Environment
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Role.Data import EnumInt32, EnumInt16, EnumDayInt1, EnumObj

#### 魅力情人节活动版本号  再次开启活动递增该版本号
###############################################
ValentineVersion = 1
###############################################

if "_HasLoad" not in dir():
	
	Tra_Valentine_UpdateVersion = AutoLog.AutoTransaction("Tra_Valentine_UpdateVersion", "魅力情人节_更新活动版本号")

def UpdateVersion(role, param = None):
	'''
	根据情人节活动版本号 和 记录的版本好 处理角色Obj数据
	'''
	roleVersion = role.GetI32(EnumInt32.ValentineDayVersion)
	if ValentineVersion == roleVersion:
		return
	
	if ValentineVersion < roleVersion:
		print "GE_EXC, ValentineVersionMgr::UpdateVersion ValentineVersion(%s) < roleVersion (%s)" % (ValentineVersion, roleVersion)
		return 
	
	#重置相关数据
	with Tra_Valentine_UpdateVersion:
		#升级版本号
		role.SetI32(EnumInt32.ValentineDayVersion, ValentineVersion)
		#今日赠送99朵玫瑰数量
		role.SetI16(EnumInt16.RosePresentSendTimes, 0)
		#今日魅力值
		role.SetI32(EnumInt32.DayGlamourExp, 0)
		#历史总魅力值
		role.SetI32(EnumInt32.HistoryGlamourExp, 0)
		#今日是否领取魅力排行安慰奖
		role.SetDI1(EnumDayInt1.GlamourRank_IsReward, 0)
		#Obj 
		role.SetObj(EnumObj.ValentineDayData, {1:{}, 2:{}, 3:{}, 4:set(), 5:{}})

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_AfterLogin, UpdateVersion)