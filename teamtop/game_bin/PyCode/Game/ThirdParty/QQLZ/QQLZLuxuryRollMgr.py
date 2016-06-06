#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQLZ.QQLZLuxuryRollMgr")
#===============================================================================
# 豪华蓝钻转大礼Mgr
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
from Game.Role import Call, Event
from Game.Role.Data import EnumInt8, EnumInt16, EnumTempInt64
from Game.ThirdParty.QQLZ import QQLZLuxuryRollConfig

OPEN_STATE = 1
CLOSE_STATE = 0

if "_HasLoad" not in dir():
	IS_START = False	#豪华蓝钻转大礼活动开关标志
	ENDTIME = 0			#活动结束时间戳
	#消息
	QQLZLuxuryRoll_ActiveState_S = AutoMessage.AllotMessage("QQLZLuxuryRoll_ActiveState_S", "豪华蓝钻转大礼_同步活动状态")
	QQLZLuxuryRoll_LotteryResult_SB = AutoMessage.AllotMessage("QQLZLuxuryRoll_LotteryResult_SB", "豪华蓝钻转大礼_同步抽奖结果")
	#事务
	Tra_QQLZLuxuryRoll_Lottery = AutoLog.AutoTransaction("Tra_QQLZLuxuryRoll_Lottery", "豪华蓝钻转大礼_抽奖获得")
	Tra_QQLZLuxuryRoll_Exchange = AutoLog.AutoTransaction("Tra_QQLZLuxuryRoll_Exchange", "豪华蓝钻转大礼_兑换")

#============= 活动控制 ====================
#启服之后根据当前时间和活动配置时间 注册tick控制活动
def Initialize():	
	'''
	初始化活动tick
	'''
	#获取活动配置时间
	activeBase = QQLZLuxuryRollConfig.QQLZLuxuryRoll_Config_Base
	if not activeBase:
		print "GE_EXC, activeBase is None while Initialize QQLZLuxuryRoll"
		return
	beginDate = activeBase.beginDate
	endDate = activeBase.endDate
	
	#当前日期-时间
	nowDate = cDateTime.Now()
	nowTime = int(time.mktime(datetime.datetime(cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second()).timetuple()))
	
	#开始时间戳-结束时间戳
	beginTime = int(time.mktime(beginDate.timetuple()))
	endTime = int(time.mktime(endDate.timetuple()))
	
	if beginDate <= nowDate < endDate:
		#开启 并注册结束tick
		QQLZLuxuryRoll_Start(None, endTime)
		cComplexServer.RegTick(endTime - nowTime, QQLZLuxuryRoll_End)
	elif nowDate < beginDate:
		#注册开启和结束的tick
		cComplexServer.RegTick(beginTime - nowTime, QQLZLuxuryRoll_Start, endTime)
		cComplexServer.RegTick(endTime - nowTime, QQLZLuxuryRoll_End)
		
	#如果活动没有结束，对版本号进行检测
	if nowDate < endDate:
		Event.TriggerEvent(Event.Eve_QQCheckVersion, None, (2, beginDate, "QQLZLuxuryRoll"))

def QQLZLuxuryRoll_Start(callArgv, regParam):
	'''
	开启豪华蓝钻转大礼
	'''
	global IS_START
	global ENDTIME
	if IS_START:
		print "GE_EXC,repeat start QQLZLuxuryRoll"
		return
	
	IS_START = True
	ENDTIME = regParam
	cNetMessage.PackPyMsg(QQLZLuxuryRoll_ActiveState_S, (OPEN_STATE, ENDTIME))
	cRoleMgr.BroadMsg()

def QQLZLuxuryRoll_End(callArgv, regParam):
	'''
	结束豪华蓝钻转大礼
	'''
	global IS_START
	if not IS_START:
		print "GE_EXC,close QQLZLuxuryRoll while not open"
		return
	
	IS_START = False
	cNetMessage.PackPyMsg(QQLZLuxuryRoll_ActiveState_S, (CLOSE_STATE, ENDTIME))
	cRoleMgr.BroadMsg()	

#### 客户端请求 start
def OnLottery(role, msg=None):
	'''
	豪华蓝钻转大礼_请求抽奖
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.QQLZLuxuryRoll_NeedLevel:
		return
	
	#非蓝钻渠道
	isQQGame = role.GetTI64(EnumTempInt64.IsQQGame)
	is3366 = role.GetTI64(EnumTempInt64.Is3366)
	if not isQQGame and not is3366:
		return
	
	#剩余抽奖次数不足
	kaiTongTimes = role.GetI8(EnumInt8.QQHaoHuaLanZuanKaiTongTimes)
	usedTimes = role.GetI8(EnumInt8.QQLZLuxury_UsedTimes_Roll)
	if usedTimes >= kaiTongTimes:
		return
	
	reward = QQLZLuxuryRollConfig.QQLZLuxuryRoll_RandomObj.RandomOne()
	if not reward:
		print "GE_EXC, config error! can not get reward by QQLZLuxuryRoll_RandomObj.RandomOne()!"
		return
	
	rewardId, coding, cnt = reward
	with Tra_QQLZLuxuryRoll_Lottery:
		#增加已抽奖次数
		role.IncI8(EnumInt8.QQLZLuxury_UsedTimes_Roll, 1)
	
	#同步并等待回调
	role.SendObjAndBack(QQLZLuxuryRoll_LotteryResult_SB, rewardId, 8, LotteryCallBack, (role.GetRoleID(), coding, cnt))

def LotteryCallBack(role, callargv, regparam):
	'''
	抽奖回调
	'''
	roleId, coding, cnt = regparam
	if not roleId or not coding or not cnt:
		print "GE_EXC, error regparam:roleId(%s), coding(%s), cnt(%s)" % (roleId, coding, cnt)
		return
	
	Call.LocalDBCall(roleId, RealAward, (coding, cnt))

def RealAward(role, param):
	'''
	抽奖实际获得处理
	'''
	coding, cnt = param
	with Tra_QQLZLuxuryRoll_Lottery:
		#获得物品
		role.AddItem(coding, cnt)
		#加次数
		role.IncI16(EnumInt16.QQLZLuxuryRollCrystal, EnumGameConfig.QQLZLuxuryRoll_CrystalBaseCnt)
	
	rewardPromt = GlobalPrompt.QQLZLuxuryRoll_Tips_Head + GlobalPrompt.QQLZLuxuryRoll_Tips_Item % (coding, cnt) + GlobalPrompt.QQLZLuxuryRoll_Tips_Crystal % EnumGameConfig.QQLZLuxuryRoll_CrystalBaseCnt
	role.Msg(2, 0, rewardPromt)
	
def OnExchange(role, msg):
	'''
	豪华蓝钻转大礼_请求兑换
	@param msg: exchangeId
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.QQLZLuxuryRoll_NeedLevel:
		return
	
	#非蓝钻渠道
	isQQGame = role.GetTI64(EnumTempInt64.IsQQGame)
	is3366 = role.GetTI64(EnumTempInt64.Is3366)
	if not isQQGame and not is3366:
		return
	
	#参数->配置
	exchangeId = msg
	exchangeCfg = QQLZLuxuryRollConfig.QQLZLuxuryRoll_Exchange_Dict.get(exchangeId)
	if not exchangeCfg:
		return
	
	#剩余蓝钻水晶不足
	needCnt = exchangeCfg.needCnt
	effectCnt = role.GetI16(EnumInt16.QQLZLuxuryRollCrystal)
	if effectCnt < needCnt:
		return
	
	coding, cnt = exchangeCfg.item
	with Tra_QQLZLuxuryRoll_Exchange:
		#扣除蓝钻水晶
		role.DecI16(EnumInt16.QQLZLuxuryRollCrystal, needCnt)
		#获得物品
		role.AddItem(coding, cnt)
	
	#获得提示
	prompt = GlobalPrompt.QQLZLuxuryRoll_Tips_HeadEx + GlobalPrompt.QQLZLuxuryRoll_Tips_Item % (coding, cnt)
	role.Msg(2, 0, prompt)

def OnSyncRoleOtherData(role, param):
	'''
	同步活动状态
	'''
	if not IS_START:
		return
	role.SendObj(QQLZLuxuryRoll_ActiveState_S, (OPEN_STATE, ENDTIME))

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#pre_process
		Initialize()
		#事件
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQLZLuxuryRoll_OnLottery", "豪华蓝钻转大礼_请求抽奖"), OnLottery)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQLZLuxuryRoll_OnExchange", "豪华蓝钻转大礼_请求兑换"), OnExchange)
