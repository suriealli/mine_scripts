#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQLZ.QQLZRollMgr")
#===============================================================================
# 蓝钻兑好礼Mgr
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
from Game.Role.Data import EnumInt8, EnumInt16
from Game.ThirdParty.QQLZ import QQLZRollConfig

OPEN_STATE = 1
CLOSE_STATE = 0

if "_HasLoad" not in dir():
	IS_START = False	#蓝钻兑好礼活动开关标志
	ENDTIME = 0			#活动结束时间戳
	#消息
	QQLZRoll_ActiveState_S = AutoMessage.AllotMessage("QQLZRoll_ActiveState_S", "蓝钻兑好礼_同步活动状态")
	QQLZRoll_LotteryResult_SB = AutoMessage.AllotMessage("QQLZRoll_LotteryResult_SB", "蓝钻兑好礼_同步抽奖结果")
	#事务
	Tra_QQLZRoll_Lottery = AutoLog.AutoTransaction("Tra_QQLZRoll_Lottery", "蓝钻兑好礼_抽奖获得")
	Tra_QQLZRoll_Exchange = AutoLog.AutoTransaction("Tra_QQLZRoll_Exchange", "蓝钻兑好礼_兑换")

#============= 活动控制 ====================
#启服之后根据当前时间和活动配置时间 注册tick控制活动
def Initialize():	
	'''
	初始化活动tick
	'''
	#获取活动配置时间
	activeBase = QQLZRollConfig.QQLZRoll_Config_Base
	if not activeBase:
		print "GE_EXC, activeBase is None while Initialize QQLZRoll"
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
		QQLZRoll_Start(None, endTime)
		cComplexServer.RegTick(endTime - nowTime, QQLZRoll_End)
	elif nowDate < beginDate:
		#注册开启和结束的tick
		cComplexServer.RegTick(beginTime - nowTime, QQLZRoll_Start, endTime)
		cComplexServer.RegTick(endTime - nowTime, QQLZRoll_End)
		
	#如果活动没有结束，对版本号进行检测
	if nowDate < endDate:
		Event.TriggerEvent(Event.Eve_QQCheckVersion, None, (1, beginDate, "QQLZRoll"))

def QQLZRoll_Start(callArgv, regParam):
	'''
	开启蓝钻兑好礼
	'''
	global IS_START
	global ENDTIME
	if IS_START:
		print "GE_EXC,repeat start QQLZRoll"
		return
	
	IS_START = True
	ENDTIME = regParam
	cNetMessage.PackPyMsg(QQLZRoll_ActiveState_S, (OPEN_STATE, ENDTIME))
	cRoleMgr.BroadMsg()

def QQLZRoll_End(callArgv, regParam):
	'''
	结束蓝钻兑好礼
	'''
	global IS_START
	if not IS_START:
		print "GE_EXC,close QQLZRoll while not open"
		return
	
	IS_START = False
	cNetMessage.PackPyMsg(QQLZRoll_ActiveState_S, (CLOSE_STATE, ENDTIME))
	cRoleMgr.BroadMsg()	

#### 客户端请求 start
def OnLottery(role, msg=None):
	'''
	蓝钻兑好礼_请求抽奖
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.QQLZRoll_NeedLevel:
		return
	
	#剩余抽奖次数不足
	kaiTongTimes = role.GetI8(EnumInt8.QQLanZuanKaiTongTimes)
	usedTimes = role.GetI8(EnumInt8.QQLZRoll_UsedTimes_Roll)
	if usedTimes >= kaiTongTimes:
		return
	
	reward = QQLZRollConfig.QQLZRoll_RandomObj.RandomOne()
	if not reward:
		print "GE_EXC, config error! can not get reward by QQLZRoll_RandomObj.RandomOne()!"
		return
	
	rewardId, coding, cnt = reward
	with Tra_QQLZRoll_Lottery:
		#增加已抽奖次数
		role.IncI8(EnumInt8.QQLZRoll_UsedTimes_Roll, 1)
	
	#同步并等待回调
	role.SendObjAndBack(QQLZRoll_LotteryResult_SB, rewardId, 8, LotteryCallBack, (role.GetRoleID(), coding, cnt))

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
	with Tra_QQLZRoll_Lottery:
		#获得物品
		role.AddItem(coding, cnt)
		#加次数
		role.IncI16(EnumInt16.QQLZRollCrystal, EnumGameConfig.QQLZRoll_CrystalBaseCnt)
	
	rewardPromt = GlobalPrompt.QQHZRoll_Tips_Head + GlobalPrompt.QQLZRoll_Tips_Item % (coding, cnt) + GlobalPrompt.QQLZRoll_Tips_Crystal % EnumGameConfig.QQLZRoll_CrystalBaseCnt
	role.Msg(2, 0, rewardPromt)
	
def OnExchange(role, msg):
	'''
	蓝钻兑好礼_请求兑换
	@param msg: exchangeId
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.QQLZRoll_NeedLevel:
		return
	
	#参数->配置
	exchangeId = msg
	exchangeCfg = QQLZRollConfig.QQLZRoll_Exchange_Dict.get(exchangeId)
	if not exchangeCfg:
		return
	
	#剩余蓝钻水晶不足
	needCnt = exchangeCfg.needCnt
	effectCnt = role.GetI16(EnumInt16.QQLZRollCrystal)
	if effectCnt < needCnt:
		return
	
	coding, cnt = exchangeCfg.item
	with Tra_QQLZRoll_Exchange:
		#扣除蓝钻水晶
		role.DecI16(EnumInt16.QQLZRollCrystal, needCnt)
		#获得物品
		role.AddItem(coding, cnt)
	
	#获得提示
	prompt = GlobalPrompt.QQLZRoll_Tips_HeadEx + GlobalPrompt.QQLZRoll_Tips_Item % (coding, cnt)
	role.Msg(2, 0, prompt)

def OnSyncRoleOtherData(role, param):
	'''
	同步活动状态
	'''
	if not IS_START:
		return
	role.SendObj(QQLZRoll_ActiveState_S, (OPEN_STATE, ENDTIME))

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#pre_process
		Initialize()
		#事件
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQLZRoll_OnLottery", "蓝钻兑好礼_请求抽奖"), OnLottery)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQLZRoll_OnExchange", "蓝钻兑好礼_请求兑换"), OnExchange)
