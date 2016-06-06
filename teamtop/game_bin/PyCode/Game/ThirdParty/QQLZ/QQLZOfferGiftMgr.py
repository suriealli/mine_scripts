#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQLZ.QQLZOfferGiftMgr")
#===============================================================================
# 蓝钻献大礼Mgr
#===============================================================================
import time
import datetime
import cRoleMgr
import cDateTime
import cNetMessage
import cComplexServer
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Role.Data import EnumInt8, EnumDayInt8
from Game.ThirdParty.QQLZ import QQLZRollGiftMgr, QQLZOfferGiftConfig

QQLZGIFT_OG = 1	#蓝钻献大礼
CLOSE_STATE = 0			#关闭
OPEN_STATE = 1			#开启

if "_HasLoad" not in dir():
	IS_START = False	#蓝钻献大礼活动开关标志
	ENDTIME = 0			#活动结束时间戳
	#日志
	Tra_QQLZGift_OG_Reward = AutoLog.AutoTransaction("Tra_QQLZGift_OG_Reward", "蓝钻献大礼奖励")
	#同步 PS:之前两个活动在一个模块共用 调整代码之后 为了保证协议不变故如此！
	QQLZGift_State_OfferGift = QQLZRollGiftMgr.QQLZGift_State_OfferGift

def QQLZGiftOGControl(beginDate, endDate):
	'''
	蓝钻献大礼动态控制
	'''
	#当前已开启
	if IS_START:
		print "GE_EXC, repeat open QQLZGift_Offer"
		return	
	
	#当前日期-时间
	nowDate = (cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second())
	nowTime = int(time.mktime(datetime.datetime(cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second()).timetuple()))
	
	#开始时间-结束时间
	beginTime = int(time.mktime(datetime.datetime(*beginDate).timetuple()))
	endTime = int(time.mktime(datetime.datetime(*endDate).timetuple()))
	
	if beginDate <= nowDate < endDate:
		#开启 并注册结束tick
		QQLZGift_StartOG(None, endTime)
		cComplexServer.RegTick(endTime - nowTime, QQLZGift_EndOG)
	elif nowDate < beginDate:
		#注册开启和结束的tick
		cComplexServer.RegTick(beginTime - nowTime, QQLZGift_StartOG, endTime)
		cComplexServer.RegTick(endTime - nowTime, QQLZGift_EndOG)
		
	#如果活动没有结束，对版本号进行检测
	if nowDate < endDate:
		Event.TriggerEvent(Event.Eve_QQCheckVersion, None, (1, beginDate, "QQLZOfferGift"))

def QQLZGift_StartOG(callArgv, regParam):
	'''
	开启钻大礼某活动
	@param callargv: 
	@param regparam: (QQLZGift_Type, endTime):(活动类型,结束时间戳) 
	'''
	# 已开启 无视
	global IS_START
	global ENDTIME
	if IS_START:
		print "GE_EXC, QQLZGift_Start::repeat open QQLZGiftOG"
		return
	
	#开启黄钻献大礼 广播通知开启
	IS_START = True
	ENDTIME = regParam
	cNetMessage.PackPyMsg(QQLZGift_State_OfferGift, (OPEN_STATE, ENDTIME))
	cRoleMgr.BroadMsg()

def QQLZGift_EndOG(callArgv, regParam):
	'''
	关闭蓝钻献大礼
	@param callargv: 
	@param regparam: QQLZGift_Type:活动类型
	'''
	#未开启 无视
	global IS_START
	if not IS_START:
		print "GE_EXC,QQLZGift_End::active is not open"
		return
	
	#关闭蓝钻献大礼 广播通知
	IS_START = False
	cNetMessage.PackPyMsg(QQLZGift_State_OfferGift, (CLOSE_STATE, ENDTIME))
	cRoleMgr.BroadMsg()	

def OnGetOfferGift(role, param = None):
	'''
	蓝钻 献大礼 奖励领取
	'''
	# 未开启对应活动 无视
	if not IS_START:
		return
	
	#等级限制
	if role.GetLevel() < EnumGameConfig.QQLZGift_OG_NeedLevel:
		return
	
	#献大礼处理
	OGEffectiveNum = role.GetI8(EnumInt8.QQLanZuanKaiTongTimes)	
	OGUsedNum = role.GetI8(EnumInt8.QQLZGift_UsedNum_Offer)
	OGTodayNum = role.GetDI8(EnumDayInt8.QQLZGift_OG_TodayTimes)
		
	#今日次数已满
	if OGTodayNum >= EnumGameConfig.QQLZGift_OG_DayMaxTimes:
		return
	
	#剩余次数不足
	if (OGEffectiveNum < 1 or OGUsedNum >= OGEffectiveNum):
		return
		
	#获取配置
	cfg = QQLZOfferGiftConfig.QQLZ_GIFT_OFFER_GIFT_DICT.get(1,None)
	if not cfg:
		return
		
	#process
	with Tra_QQLZGift_OG_Reward:
		#增加已抽奖次数
		role.SetI8(EnumInt8.QQLZGift_UsedNum_Offer, OGUsedNum + 1)
		role.SetDI8(EnumDayInt8.QQLZGift_OG_TodayTimes, OGTodayNum + 1)
			
		rewardItemMsg = ""
		for item in cfg.nomalItems:
			role.AddItem(*item)
			rewardItemMsg += GlobalPrompt.QQLZGift_Tips_Reward_Item % (item[0], item[1])
			
		randomItem = QQLZOfferGiftConfig.GetRandomOG()
		role.AddItem(*randomItem)	
		rewardItemMsg += GlobalPrompt.QQLZGift_Tips_Reward_Item % (randomItem[0], randomItem[1])
	
		promptMsg = GlobalPrompt.QQLZGift_Tips_Reward_Head + rewardItemMsg
		role.Msg(2, 0, promptMsg)			

def OnSyncRoleOtherData(role, param):
	'''
	同步蓝钻献大礼开启状态
	'''
	#未开启
	if not IS_START:
		return
	
	#黄钻献大礼 当前开启 同步
	role.SendObj(QQLZGift_State_OfferGift, (OPEN_STATE, ENDTIME))

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#事件
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		#注册消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQLZGift_OnGetOfferGift", "蓝钻献大礼奖励领取"), OnGetOfferGift)
		
