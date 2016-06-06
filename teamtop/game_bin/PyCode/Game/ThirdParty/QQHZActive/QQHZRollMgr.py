#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQHZActive.QQHZRollMgr")
#===============================================================================
# 黄钻兑好礼Mgr
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
from Game.ThirdParty.QQHZActive import QQHZRollConfig

OPEN_STATE = 1
CLOSE_STATE = 0

if "_HasLoad" not in dir():
	IS_START = False	#黄钻兑好礼活动开关标志
	ENDTIME = 0			#活动结束时间戳
	#消息
	QQHZRoll_ActiveState_S = AutoMessage.AllotMessage("QQHZRoll_ActiveState_S", "黄钻兑好礼_同步活动状态")
	QQHZRoll_LotteryResult_SB = AutoMessage.AllotMessage("QQHZRoll_LotteryResult_SB", "黄钻兑好礼_同步抽奖结果")
	#事务
	Tra_QQHZRoll_Lottery = AutoLog.AutoTransaction("Tra_QQHZRoll_Lottery", "黄钻兑好礼_抽奖获得")
	Tra_QQHZRoll_Exchange = AutoLog.AutoTransaction("Tra_QQHZRoll_Exchange", "黄钻兑好礼_兑换")

#============= 活动控制 ====================
#启服之后根据当前时间和活动配置时间 注册tick控制活动
def Initialize():	
	'''
	初始化活动tick
	'''
	#获取活动配置时间
	activeBase = QQHZRollConfig.QQHZRoll_Config_Base
	if not activeBase:
		print "GE_EXC, activeBase is None while Initialize QQHZRoll"
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
		QQHZRoll_Start(None, endTime)
		cComplexServer.RegTick(endTime - nowTime, QQHZRoll_End)
	elif nowDate < beginDate:
		#注册开启和结束的tick
		cComplexServer.RegTick(beginTime - nowTime, QQHZRoll_Start, endTime)
		cComplexServer.RegTick(endTime - nowTime, QQHZRoll_End)
		
	#如果活动没有结束，对版本号进行检测
	if nowDate < endDate:
		Event.TriggerEvent(Event.Eve_QQCheckVersion, None, (0, beginDate, "QQHZRoll"))

def QQHZRoll_Start(callArgv, regParam):
	'''
	开启黄钻兑好礼
	'''
	global IS_START
	global ENDTIME
	if IS_START:
		print "GE_EXC,repeat start QQHZRoll"
		return
	
	IS_START = True
	ENDTIME = regParam
	cNetMessage.PackPyMsg(QQHZRoll_ActiveState_S, (OPEN_STATE, ENDTIME))
	cRoleMgr.BroadMsg()

def QQHZRoll_End(callArgv, regParam):
	'''
	结束黄钻兑好礼
	'''
	global IS_START
	if not IS_START:
		print "GE_EXC,close QQHZRoll while not open"
		return
	
	IS_START = False
	cNetMessage.PackPyMsg(QQHZRoll_ActiveState_S, (CLOSE_STATE, ENDTIME))
	cRoleMgr.BroadMsg()	

#### 客户端请求 start
def OnLottery(role, msg=None):
	'''
	黄钻兑好礼_请求抽奖
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.QQHZRoll_NeedLevel:
		return
	
	#剩余抽奖次数不足
	kaiTongTimes = role.GetI8(EnumInt8.QQHuangZuanKaiTongTimes)
	usedTimes = role.GetI8(EnumInt8.QQHZRoll_UsedTimes_Roll)
	if usedTimes >= kaiTongTimes:
		return
	
	reward = QQHZRollConfig.QQHZRoll_RandomObj.RandomOne()
	if not reward:
		print "GE_EXC, config error! can not get reward by QQHZRoll_RandomObj.RandomOne()!"
		return
	
	rewardId, coding, cnt = reward
	with Tra_QQHZRoll_Lottery:
		#增加已抽奖次数
		role.IncI8(EnumInt8.QQHZRoll_UsedTimes_Roll, 1)
	
	#同步并等待回调
	role.SendObjAndBack(QQHZRoll_LotteryResult_SB, rewardId, 8, LotteryCallBack, (role.GetRoleID(), coding, cnt))

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
	with Tra_QQHZRoll_Lottery:
		#获得物品
		role.AddItem(coding, cnt)
		#加次数
		role.IncI16(EnumInt16.QQHZRollCrystal, EnumGameConfig.QQHZRoll_CrystalBaseCnt)
	
	rewardPromt = GlobalPrompt.QQHZRoll_Tips_Head + GlobalPrompt.QQHZRoll_Tips_Item % (coding, cnt) + GlobalPrompt.QQHZRoll_Tips_Crystal % EnumGameConfig.QQHZRoll_CrystalBaseCnt
	role.Msg(2, 0, rewardPromt)
	
def OnExchange(role, msg):
	'''
	黄钻兑好礼_请求兑换
	@param msg: exchangeId
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.QQHZRoll_NeedLevel:
		return
	
	#参数->配置
	exchangeId = msg
	exchangeCfg = QQHZRollConfig.QQHZRoll_Exchange_Dict.get(exchangeId)
	if not exchangeCfg:
		return
	
	#剩余黄钻水晶不足
	needCnt = exchangeCfg.needCnt
	effectCnt = role.GetI16(EnumInt16.QQHZRollCrystal)
	if effectCnt < needCnt:
		return
	
	coding, cnt = exchangeCfg.item
	with Tra_QQHZRoll_Exchange:
		#扣除黄钻水晶
		role.DecI16(EnumInt16.QQHZRollCrystal, needCnt)
		#获得物品
		role.AddItem(coding, cnt)
	
	#获得提示
	prompt = GlobalPrompt.QQHZRoll_Tips_HeadEx + GlobalPrompt.QQHZRoll_Tips_Item % (coding, cnt)
	role.Msg(2, 0, prompt)

def OnSyncRoleOtherData(role, param):
	'''
	同步活动状态
	'''
	if not IS_START:
		return
	role.SendObj(QQHZRoll_ActiveState_S, (OPEN_STATE, ENDTIME))

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#pre_process
		Initialize()
		#事件
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQHZRoll_OnLottery", "黄钻兑好礼_请求抽奖"), OnLottery)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQHZRoll_OnExchange", "黄钻兑好礼_请求兑换"), OnExchange)
