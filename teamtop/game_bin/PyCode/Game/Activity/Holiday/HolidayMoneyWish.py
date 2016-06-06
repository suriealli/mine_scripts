#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.Holiday.HolidayMoneyWish")
#===============================================================================
# 金币祈福礼(金币抽奖)
#===============================================================================
import Environment
import cRoleMgr
from Common.Other import GlobalPrompt, EnumGameConfig
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Activity import CircularDefine
from Game.Activity.Holiday import HolidayConfig
from Game.Role.Data import EnumDayInt8
from Game.Role.Mail import Mail

if "_HasLoad" not in dir():
	IsOpen = False			#活动是否开启
	
	RecordList = []			#祈福奖励记录(10条)	玩家名字, 道具coding, 道具cnt
	
	HolidayWishRecord = AutoMessage.AllotMessage("HolidayWishRecord", "元旦祈福奖励记录")
	
	HolidayMoneyWish_Log = AutoLog.AutoTransaction("HolidayMoneyWish_Log", "元旦金币祈福日志")
	
def OpenAct(param1, param2):
	if param2 != CircularDefine.CA_HolidayMoneyWish:
		return
	
	global IsOpen
	if IsOpen:
		print 'GE_EXC, MoneyWish is already open'
	IsOpen = True
	
def CloseAct(param1, param2):
	if param2 != CircularDefine.CA_HolidayMoneyWish:
		return
	
	global IsOpen
	if not IsOpen:
		print 'GE_EXC, MoneyWish is already close'
	IsOpen = False

def GetCloseValue(value, value_list):
	'''
	返回第一个大于value的上一个值
	@param value:
	@param value_list:
	'''
	tmp_level = 0
	for i in value_list:
		if i > value:
			return tmp_level
		tmp_level = i
	else:
		return tmp_level
	
def RequestOpen(role, msg):
	'''
	请求打开祈福
	@param role:
	@param msg:
	'''
	global IsOpen
	if not IsOpen: return
	
	if role.GetLevel() < EnumGameConfig.HolidayOnlineReward_NeedLevel:
		return
	
	global RecordList
	role.SendObj(HolidayWishRecord, RecordList)
	
def RequestWish(role, msg):
	'''
	请求祈福
	@param role:
	@param msg:
	'''
	global IsOpen
	if not IsOpen: return
	
	#等级
	level = role.GetLevel()
	if level < EnumGameConfig.HolidayOnlineReward_NeedLevel:
		return
	level = GetCloseValue(level, HolidayConfig.MoneyWishLv_List)
	
	#配置
	cfg = HolidayConfig.MoneyWish_Dict.get(level)
	if not cfg:
		print 'GE_EXC, MoneyWish RequestWish can not find %s cfg' % role.GetLevel()
		return
	
	#金币不够
	if role.GetMoney() < cfg.needMoney:
		return
	
	with HolidayMoneyWish_Log:
		if role.GetDI8(EnumDayInt8.HolidayWishFreeCnt) < 2:
			#有免费次数
			role.DecMoney(cfg.needMoney)
			role.IncDI8(EnumDayInt8.HolidayWishFreeCnt, 1)
			itemCoding, itemCnt, isRecord = cfg.randomReward.RandomOne()
			
			if role.PackageEmptySize() < itemCnt:
				Mail.SendMail(role.GetRoleID(), GlobalPrompt.HWishMailTitle, GlobalPrompt.HWishMailSender, GlobalPrompt.HWishMailContent, items=[[itemCoding, itemCnt]])
			else:
				role.AddItem(itemCoding, itemCnt)
			
			Record(role, itemCoding, itemCnt, isRecord)
			
			role.Msg(2, 0, GlobalPrompt.HolidayWishTips % (itemCoding, itemCnt))
			
		elif role.GetDI8(EnumDayInt8.HolidayWishCnt):
			#有奖励次数
			role.DecMoney(cfg.needMoney)
			role.DecDI8(EnumDayInt8.HolidayWishCnt, 1)
			itemCoding, itemCnt, isRecord = cfg.randomReward.RandomOne()
			
			if role.PackageEmptySize() < itemCnt:
				Mail.SendMail(role.GetRoleID(), GlobalPrompt.HWishMailTitle, GlobalPrompt.HWishMailSender, GlobalPrompt.HWishMailContent, items=[[itemCoding, itemCnt]])
			else:
				role.AddItem(itemCoding, itemCnt)
			
			Record(role, itemCoding, itemCnt, isRecord)
			
			role.Msg(2, 0, GlobalPrompt.HolidayWishTips % (itemCoding, itemCnt))
		else:
			return

def Record(role, itemCoding, itemCnt, isRecord):
	if not isRecord:
		return
	RecordList.append([role.GetRoleName(), itemCoding, itemCnt])
	if len(RecordList) > 10:
		RecordList.pop(0)
	role.SendObj(HolidayWishRecord, RecordList)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_StartCircularActive, OpenAct)
		Event.RegEvent(Event.Eve_EndCircularActive, CloseAct)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("HolidayMoneyWish_Open", "请求打开元旦金币祈福"), RequestOpen)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("HolidayMoneyWish_Wish", "请求元旦金币祈福"), RequestWish)
		
