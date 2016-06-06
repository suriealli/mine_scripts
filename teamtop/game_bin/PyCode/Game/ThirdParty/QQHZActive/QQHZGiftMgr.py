#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQHZActive.QQHZGiftMgr")
#===============================================================================
# 黄钻大礼 akm
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
from Game.ThirdParty.QQHZActive import QQHZGiftConfig

CLOSE_STATE = 0			#关闭
OPEN_STATE = 1			#开启

QQHZGift_RG = 0			#黄钻转大礼
QQHZGift_OG = 1			#黄钻献大礼

if "_HasLoad" not in dir():
	QQHZ_GIFT_ONLINE_TYPE_DICT = {}					#黄钻大礼活动当前开启的类型集合{活动类型:结束时间戳}
	
	QQHZGift_State_Roll = AutoMessage.AllotMessage("QQHZGift_State_RollGift_S", "黄钻转大礼活动状态同步")
	QQHZGift_State_Offer = AutoMessage.AllotMessage('QQHZGift_State_OfferGift_S', "黄钻献大礼活动状态同步")	
	
	QQHZGift_Roll_Result = AutoMessage.AllotMessage("QQHZGift_Roll_Result_SB", "黄钻转大礼抽奖结果")
	
	Tra_QQHZGift_Roll = AutoLog.AutoTransaction("Tra_QQHZGift_Roll", "黄钻转大礼礼包获取")
	Tra_QQHZGift_Offer = AutoLog.AutoTransaction("Tra_QQHZGift_Offer", "黄钻献大礼物品获取")

def Initialize():
	'''
	初始化活动tick
	'''
	nowDate = (cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second())
	nowTime = int(time.mktime(datetime.datetime(cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second()).timetuple()))
	
	for _,config in QQHZGiftConfig.QQHZ_GIFT_ACTIVE_CONFIG_DICT.iteritems():
		beginTime = int(time.mktime(datetime.datetime(*config.beginDate).timetuple()))
		endTime = int(time.mktime(datetime.datetime(*config.endDate).timetuple()))
		QQHZGift_Type = config.activeType
		
		if config.beginDate <= nowDate < config.endDate:
			#开启 并注册结束tick
			QQHZGift_Start(None,(QQHZGift_Type,endTime))
			cComplexServer.RegTick(endTime - nowTime, QQHZGift_End, QQHZGift_Type)
		elif nowDate < config.beginDate:
			#注册开启和结束的tick
			cComplexServer.RegTick(beginTime - nowTime, QQHZGift_Start, (QQHZGift_Type,endTime))
			cComplexServer.RegTick(endTime - nowTime, QQHZGift_End, QQHZGift_Type)

def QQHZGiftOGControl(beginDate, endDate):
	'''
	黄钻献大礼 活动控制 （黄钻转大礼由配置控制  黄钻献大礼根据前者效果动态控制）
	'''
	#活动类型
	QQHZGift_Type = QQHZGift_OG
	
	#当前已开启
	if QQHZGift_Type in QQHZ_GIFT_ONLINE_TYPE_DICT:
		print "GE_EXC, repeat open QQHZGift_Offer"
		return	
	
	#当前日期-时间
	nowDate = (cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second())
	nowTime = int(time.mktime(datetime.datetime(cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second()).timetuple()))
	
	#开始时间-结束时间
	beginTime = int(time.mktime(datetime.datetime(*beginDate).timetuple()))
	endTime = int(time.mktime(datetime.datetime(*endDate).timetuple()))
	
	if beginDate <= nowDate < endDate:
		#开启 并注册结束tick
		QQHZGift_Start(None,(QQHZGift_Type,endTime))
		cComplexServer.RegTick(endTime - nowTime, QQHZGift_End, QQHZGift_Type)
	elif nowDate < beginDate:
		#注册开启和结束的tick
		cComplexServer.RegTick(beginTime - nowTime, QQHZGift_Start, (QQHZGift_Type,endTime))
		cComplexServer.RegTick(endTime - nowTime, QQHZGift_End, QQHZGift_Type)
		
	#如果活动没有结束，对版本号进行检测
	if nowDate < endDate:
		Event.TriggerEvent(Event.Eve_QQCheckVersion, None, (0, beginDate, "QQHZGift"))

def QQHZGift_Start(callargv, regparam):
	'''
	开启黄钻大礼某活动
	@param callargv: 
	@param regparam: (QQHZGift_Type, endTime):(活动类型,结束时间戳) 
	'''
	#类型检测
	QQHZGift_Type, endTime = regparam
	if QQHZGift_Type < QQHZGift_RG or QQHZGift_Type > QQHZGift_OG:
		print "GE_EXC, QQHZGift_Start::error QQHZGift_Type(%s)" % QQHZGift_Type
		return
	
	# 已开启 无视
	global QQHZ_GIFT_ONLINE_TYPE_DICT
	if QQHZGift_Type in QQHZ_GIFT_ONLINE_TYPE_DICT:
		print "GE_EXC, QQHZGift_Start::repeat open QQHZGift: QQHZGift_Type(%s)" % QQHZGift_Type
		return
	
	if QQHZGift_Type == QQHZGift_RG:
		#开启黄钻转大礼
		QQHZ_GIFT_ONLINE_TYPE_DICT[QQHZGift_Type] = endTime
		cNetMessage.PackPyMsg(QQHZGift_State_Roll, (OPEN_STATE,endTime))
	elif QQHZGift_Type == QQHZGift_OG:
		#开启黄钻献大礼
		QQHZ_GIFT_ONLINE_TYPE_DICT[QQHZGift_Type] = endTime
		cNetMessage.PackPyMsg(QQHZGift_State_Offer, (OPEN_STATE,endTime))
	else:
		pass	
	
	#广播通知开启
	cRoleMgr.BroadMsg()

def QQHZGift_End(callargv, regparam):
	'''
	关闭黄钻大礼某活动
	@param callargv: 
	@param regparam: QQHZGift_Type:活动类型
	'''
	QQHZGift_Type = regparam
	
	#类型检测
	if QQHZGift_Type < QQHZGift_RG or QQHZGift_Type > QQHZGift_OG:
		print "GE_EXC,QQHZGift_End::error QQHZGift_Type(%s)" % QQHZGift_Type
		return
	
	#未开启 无视
	global QQHZ_GIFT_ONLINE_TYPE_DICT
	if QQHZGift_Type not in QQHZ_GIFT_ONLINE_TYPE_DICT:
		print "GE_EXC,QQHZGift_End::QQHZGift_Type(%s) is not open" % QQHZGift_Type
		return
	
	if QQHZGift_Type == QQHZGift_RG:
		#开启黄钻转大礼
		del QQHZ_GIFT_ONLINE_TYPE_DICT[QQHZGift_Type]
		cNetMessage.PackPyMsg(QQHZGift_State_Roll, (CLOSE_STATE,0))
	elif QQHZGift_Type == QQHZGift_OG:
		#开启黄钻献大礼
		del QQHZ_GIFT_ONLINE_TYPE_DICT[QQHZGift_Type]	
		cNetMessage.PackPyMsg(QQHZGift_State_Offer, (CLOSE_STATE,0))
	else:
		pass	
	
	#广播通知开启
	cRoleMgr.BroadMsg()	
	
def OnRollGift(role, param):
	'''
	黄钻转大礼 抽奖
	'''
	#活动未开启
	if QQHZGift_RG not in QQHZ_GIFT_ONLINE_TYPE_DICT:
		return
	
	#等级限制
	if role.GetLevel() < EnumGameConfig.QQHZGift_RollGiftNeedLevel:
		return
	
	#转大礼处理
	RGEffectiveNum	= role.GetI8(EnumInt8.QQHuangZuanKaiTongTimes)
	RGUsedNum	= role.GetI8(EnumInt8.QQHZGift_UsedNum_Roll)
		
	# 剩余次数不足
	if (RGEffectiveNum < 1 or RGUsedNum >= RGEffectiveNum):
		return
		
	# 次数已满
	if RGUsedNum >= EnumGameConfig.QQHZGift_RGMaxNum:
		return
		
	#随机“新”礼包
	curLiBaoID = QQHZGiftConfig.QQHZRG_RANDOMER.RandomOne()
	if not curLiBaoID or curLiBaoID not in QQHZGiftConfig.QQHZ_GIFT_ROLL_GIFT_DICT:
		return 
		
	#获取配置失效
	curLiBaocfg = QQHZGiftConfig.QQHZ_GIFT_ROLL_GIFT_DICT.get(curLiBaoID)
	if not curLiBaocfg:
		return
	
	#增加已抽奖次数
	RGUsedNum += 1
	with Tra_QQHZGift_Roll:
		role.SetI8(EnumInt8.QQHZGift_UsedNum_Roll, RGUsedNum)
		
	# 发送抽奖结果 等待回调 超时自动触发
	role.SendObjAndBack(QQHZGift_Roll_Result, curLiBaoID, 8, QQHZGiftRGCallBack, (curLiBaocfg, RGUsedNum))		

def OnGetOfferGift(role, param):
	'''
	黄钻 献大礼 奖励领取
	'''
	# 未开启对应活动 无视
	if QQHZGift_OG not in QQHZ_GIFT_ONLINE_TYPE_DICT:
		return
	
	#等级限制
	if role.GetLevel() < EnumGameConfig.QQHZGift_RollGiftNeedLevel:
		return
	
	#献大礼处理
	OGEffectiveNum	= role.GetI8(EnumInt8.QQHuangZuanKaiTongTimes)	
	OGUsedNum	= role.GetI8(EnumInt8.QQHZGift_UsedNum_Offer)
	OGTodayNum	= role.GetDI8(EnumDayInt8.QQHZGift_OG_TodayTimes)
		
	#今日次数已满
	if OGTodayNum >= EnumGameConfig.QQHZGift_OG_Daily_MaxNum:
		return
	
	#剩余次数不足
	if (OGEffectiveNum < 1 or OGUsedNum >= OGEffectiveNum):
		return
		
	#获取配置失效
	cfg = QQHZGiftConfig.QQHZ_GIFT_OFFER_GIFT_DICT.get(1,None)
	if not cfg:
		return
		
	#process
	with Tra_QQHZGift_Offer:
		#增加已抽奖次数
		role.SetI8(EnumInt8.QQHZGift_UsedNum_Offer, OGUsedNum + 1)
		role.SetDI8(EnumDayInt8.QQHZGift_OG_TodayTimes, OGTodayNum + 1)
			
		rewardItemMsg = ""
		for item in cfg.nomalItems:
			role.AddItem(*item)
			rewardItemMsg += GlobalPrompt.QQHZGift_Tips_Reward_Item % (item[0], item[1])
			
		randomItem = QQHZGiftConfig.GetRandomOG()
		role.AddItem(*randomItem)	
		rewardItemMsg += GlobalPrompt.QQHZGift_Tips_Reward_Item % (randomItem[0], randomItem[1])
	
		promptMsg =GlobalPrompt.QQHZGift_Tips_Reward_Head + rewardItemMsg
		role.Msg(2, 0, promptMsg)			
	
def QQHZGiftRGCallBack(role, callargv, regparam):
	'''
	黄钻转大礼抽奖回调
	@param role: 
	@param callargv:
	@param regparam:  LiBaoID 抽奖随机出来的礼包ID
	'''
	# 参数检测
	curLiBaocfg, RGUsedNum = regparam	
	# process
	with Tra_QQHZGift_Roll:
		# 礼包获得
		itemCoding, itemCnt = curLiBaocfg.itemCoding
		role.AddItem(itemCoding, itemCnt)
		# 额外获取--黄钻坐骑
		Master_Reward_Tips = ""
		if RGUsedNum == EnumGameConfig.QQHZGift_RGMaxNum:
			role.AddItem(EnumGameConfig.QQHZGift_RGMountProCoding, 1)
			Master_Reward_Tips = GlobalPrompt.QQHZGift_Tips_Reward_Master
		
		promptMsg = GlobalPrompt.QQHZGift_Tips_Reward_Head + GlobalPrompt.QQHZGift_Tips_Reward_Item % (itemCoding, itemCnt) + Master_Reward_Tips
		role.Msg(2, 0, promptMsg)	
		
def OnSyncRoleOtherData(role, param):
	'''
	同步黄钻活动开启集合
	'''
	#黄钻转大礼 当前开启
	if QQHZGift_RG in QQHZ_GIFT_ONLINE_TYPE_DICT:
		role.SendObj(QQHZGift_State_Roll, (OPEN_STATE, QQHZ_GIFT_ONLINE_TYPE_DICT[QQHZGift_RG]))
	
	#黄钻献大礼 当前开启
	if QQHZGift_OG in QQHZ_GIFT_ONLINE_TYPE_DICT:
		role.SendObj(QQHZGift_State_Offer, (OPEN_STATE,QQHZ_GIFT_ONLINE_TYPE_DICT[QQHZGift_OG]))
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Initialize()			
		
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
	
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQHZGift_OnRollGift", "黄钻转大礼抽奖"), OnRollGift)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQHZGift_OnGetOfferGift", "黄钻献大礼奖励领取"), OnGetOfferGift)
