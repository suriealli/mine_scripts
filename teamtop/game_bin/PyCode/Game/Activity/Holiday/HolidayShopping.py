#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.Holiday.HolidayShopping")
#===============================================================================
# 跨年购物节(购买道具得积分)
#===============================================================================
import time
import datetime
import cRoleMgr
import cDateTime
import Environment
import cComplexServer
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Common.Other import EnumSysData, GlobalPrompt, EnumGameConfig
from Game.Role import Event
from Game.Activity import CircularDefine
from Game.Activity.Holiday import HolidayConfig
from Game.SysData import WorldData
from Game.Role.Data import EnumDayInt1, EnumDayInt8
from Game.Role.Mail import Mail

if "_HasLoad" not in dir():
	IsOpen = False							#活动是否开启
	Wave = 0								#第几波
	SecondWaveTime = (2015,4,6,0,0,0)		#元旦时间
	
	#DI1枚举
	DI1EnumToIndex = {1:EnumDayInt1.HolidayScore_1, 2:EnumDayInt1.HolidayScore_2, 3:EnumDayInt1.HolidayScore_3}
	#DI8枚举
	DI8EnumToIndex = {1:EnumDayInt8.HolidayWishLimitCnt_1, 2:EnumDayInt8.HolidayWishLimitCnt_2, 3:EnumDayInt8.HolidayWishLimitCnt_3}
	
	HolidayShoppingBuy_Log = AutoLog.AutoTransaction("HolidayShoppingBuy_Log", "元旦购物节购物日志")
	HolidayShoppingReward_Log = AutoLog.AutoTransaction("HolidayShoppingReward_Log", "元旦购物节积分奖励日志")
	
def OpenAct(param1, param2):
	if param2 != CircularDefine.CA_HolidayShopping:
		return
	
	global IsOpen
	if IsOpen:
		print 'GE_EXC, ShoppingFestival is already open'
	IsOpen = True
	
	#计算波数
	global SecondWaveTime, Wave
	nowDate = (cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second())
	if nowDate > SecondWaveTime:
		#元旦过了, 第二波了
		Wave = 2
	else:
		#元旦还没过, 第一波
		Wave = 1
		#注册一个到元旦刷新的tick
		nowSec = cDateTime.Seconds()
		beginSec = int(time.mktime(datetime.datetime(*SecondWaveTime).timetuple()))
		if beginSec < nowSec:
			print 'GE_EXC, ShoppingFestival OpenAct time error'
			Wave = 2
			return
		cComplexServer.RegTick(beginSec - nowSec, UpdataWave)
	
def UpdataWave(argv, param):
	global Wave
	if Wave != 1:
		print "GE_EXC, ShoppingFestival UpdataWave error"
	Wave = 2
	
def CloseAct(param1, param2):
	if param2 != CircularDefine.CA_HolidayShopping:
		return
	
	global IsOpen, Wave
	if not IsOpen:
		print 'GE_EXC, ShoppingFestival is already close'
	IsOpen = False
	Wave = 0

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
		#没有找到返回最后一个值
		return tmp_level
	
def RequestBuy(role, msg):
	'''
	请求购买
	@param role:
	@param msg:
	'''
	global IsOpen, Wave
	if not IsOpen: return
	if not Wave: return
	if not WorldData.WD.returnDB: return
	
	#等级
	level = role.GetLevel()
	if level < EnumGameConfig.HolidayOnlineReward_NeedLevel:
		return
	level = GetCloseValue(level, HolidayConfig.ShoppingFestivalLv_List)
	
	goodNumber, cnt = msg
	if cnt <= 0:
		return
	
	#配置
	cfg = HolidayConfig.ShoppingFestival_Dict.get((goodNumber, level))
	if not cfg:
		return
	if Wave not in cfg.waveGoodDict:
		return
	#限购
	global DI8EnumToIndex
	index = DI8EnumToIndex.get(goodNumber)
	if not index:
		return
	if role.GetDI8(index) + cnt > cfg.limitCnt:
		return
	
	goodCoding, needUnbindRMB, needUnbindRMB_Q = cfg.waveGoodDict[Wave]
	
	with HolidayShoppingBuy_Log:
		#加购买个数
		role.IncDI8(index, cnt)
		if needUnbindRMB:
			needUnbindRMB *= cnt
			if role.GetUnbindRMB() < needUnbindRMB:
				return
			#扣钱
			role.DecUnbindRMB(needUnbindRMB)
			
			if role.PackageEmptySize() < cnt:
				Mail.SendMail(role.GetRoleID(), GlobalPrompt.HShoppingMailTitle_1, GlobalPrompt.HShoppingMailSender_1, GlobalPrompt.HShoppingMailContent_1, items=[[goodCoding,cnt]])
			else:
				role.AddItem(goodCoding, cnt)
			
			#加积分
			WorldData.IncHoilyShoppingScore(needUnbindRMB, HolidayConfig.ShoppingScore_List)
			
			role.Msg(2, 0, GlobalPrompt.Item_Tips % (goodCoding, cnt))
		elif needUnbindRMB_Q:
			needUnbindRMB_Q *= cnt
			if role.GetUnbindRMB_Q() < needUnbindRMB_Q:
				return
			#扣钱
			role.DecUnbindRMB_Q(needUnbindRMB_Q)
			
			if role.PackageEmptySize() < cnt:
				Mail.SendMail(role.GetRoleID(), GlobalPrompt.HShoppingMailTitle_1, GlobalPrompt.HShoppingMailSender_1, GlobalPrompt.HShoppingMailContent_1, items=[[goodCoding,cnt]])
			else:
				role.AddItem(goodCoding, cnt)
			
			#加积分
			WorldData.IncHoilyShoppingScore(needUnbindRMB_Q, HolidayConfig.ShoppingScore_List)
			
			role.Msg(2, 0, GlobalPrompt.Item_Tips % (goodCoding, cnt))
		else:
			print 'GE_EXC, RequestBuy needUnbindRMB %s, needUnbindRMB_Q %s' % (needUnbindRMB, needUnbindRMB_Q)
			return
	
def RequestScoreReward(role, msg):
	'''
	请求领取积分奖励
	@param role:
	@param msg:
	'''
	global IsOpen
	if not IsOpen: return
	if not WorldData.WD.returnDB: return
	
	if role.GetLevel() < EnumGameConfig.HolidayOnlineReward_NeedLevel:
		return
	
	#积分
	score = WorldData.WD.get(EnumSysData.HoilyShoppingScore)
	if not score:
		return
	
	scoreIndex = msg
	if not scoreIndex:
		return
	
	#是否领取
	global DI1EnumToIndex
	index = DI1EnumToIndex.get(scoreIndex)
	if not index:
		return
	if role.GetDI1(index):
		return
	
	#配置
	cfg = HolidayConfig.ShoppingScore_Dict.get(scoreIndex)
	if not cfg:
		return
	#积分不够
	if score < cfg.minScore:
		return
	
	with HolidayShoppingReward_Log:
		role.SetDI1(index, True)
		if role.PackageIsFull():
			Mail.SendMail(role.GetRoleID(), GlobalPrompt.HShoppingMailTitle_2, GlobalPrompt.HShoppingMailSender_2, GlobalPrompt.HShoppingMailContent_2, items=[[cfg.rewardCoding, 1]])
		else:
			role.AddItem(cfg.rewardCoding, 1)
		role.Msg(2, 0, GlobalPrompt.Item_Tips % (cfg.rewardCoding, 1))
	
def AfterNewDay():
	if not WorldData.WD.returnDB:
		return
	
	#每日清理元旦购物节积分
	WorldData.ClearHoilyShoppingScore()
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_StartCircularActive, OpenAct)
		Event.RegEvent(Event.Eve_EndCircularActive, CloseAct)
		
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("HolidayShopping_Buy", "请求元旦购物节购物"), RequestBuy)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("HolidayShopping_Reward", "请求领取元旦购物节积分奖励"), RequestScoreReward)
		
		