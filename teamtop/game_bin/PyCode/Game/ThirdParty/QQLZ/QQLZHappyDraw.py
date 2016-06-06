#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQLZ.QQLZHappyDraw")
#===============================================================================
# 蓝钻转转乐
#===============================================================================
import time
import cComplexServer
import Environment
import cDateTime
import cRoleMgr
import cNetMessage
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Role import Call, Event
from Game.Role.Data import EnumObj, EnumInt8, EnumInt16
from Game.ThirdParty.QQLZ import QQLZHappyDrawConfig

OPEN_STATE = 1
CLOSE_STATE = 0

if "_HasLoad" not in dir():
	IS_START = False	#蓝钻转转乐活动开关标志
	ENDTIME = 0			#活动结束时间戳
	#消息
	QQLZHappyDraw_ActiveState = AutoMessage.AllotMessage("QQLZHappyDraw_ActiveState", "蓝钻转转乐同步活动状态")
	QQLZHappyDraw_GetList = AutoMessage.AllotMessage("QQLZHappyDraw_GetList", "蓝钻转转乐已获取奖励列表")
	QQLZHappyDraw_LotteryResult = AutoMessage.AllotMessage("QQLZHappyDraw_LotteryResult", "蓝钻转转乐同步抽奖结果")
	#事务
	Tra_QQLZHappyDraw_Lottery = AutoLog.AutoTransaction("Tra_QQLZHappyDraw_Lottery", "蓝钻转转乐抽奖获得")
	Tra_QQLZHappyDraw_Exchange = AutoLog.AutoTransaction("Tra_QQLZHappyDraw_Exchange", "蓝钻转转乐兑换")
	
#============= 活动控制 ====================
#启服之后根据当前时间和活动配置时间 注册tick控制活动
def Initialize():	
	'''
	初始化活动tick
	'''
	#获取活动配置时间
	activeBase = QQLZHappyDrawConfig.QQLZ_HAPPYDRAW_BASE
	if not activeBase:
		print "GE_EXC, activeBase is None while Initialize QQLZHappyDraw"
		return
	beginDate = activeBase.beginDate
	endDate = activeBase.endDate
	
	#当前日期-时间
	nowDate = cDateTime.Now()
	nowTime = cDateTime.Seconds()
	
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
		Event.TriggerEvent(Event.Eve_QQCheckVersion, None, (1, beginDate, "QQLZHappyDraw"))

def QQLZRoll_Start(callArgv, regParam):
	'''
	开启蓝钻转转乐
	'''
	global IS_START
	global ENDTIME
	if IS_START:
		print "GE_EXC,repeat start QQLZHappyDraw"
		return
	
	IS_START = True
	ENDTIME = regParam
	cNetMessage.PackPyMsg(QQLZHappyDraw_ActiveState, (OPEN_STATE, ENDTIME))
	cRoleMgr.BroadMsg()
	
def QQLZRoll_End(callArgv, regParam):
	'''
	结束蓝钻转转乐
	'''
	global IS_START
	if not IS_START:
		print "GE_EXC,close QQLZHappyDraw while not open"
		return
	
	IS_START = False
	cNetMessage.PackPyMsg(QQLZHappyDraw_ActiveState, (CLOSE_STATE, ENDTIME))
	cRoleMgr.BroadMsg()

#=========消息处理===========
def OnLottery(role, param):
	'''
	蓝钻转转乐_请求抽奖
	@param role:
	@param param:
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.QQLZHappyDraw_NeedLevel:
		return
	
	#剩余抽奖次数不足
	kaiTongTimes = role.GetI8(EnumInt8.QQLanZuanKaiTongTimes)
	usedTimes = role.GetI8(EnumInt8.QQLZHappyDraw_UsedTimes)
	if usedTimes >= kaiTongTimes:
		return
	
	reward = QQLZHappyDrawConfig.GetRandomOne(role)
	if not reward:
		print "GE_EXC, config error! can not get reward by QQLZHappyDrawConfig.GetRandomOne!"
		return
	
	rewardId, (coding, cnt) = reward
	getedData = role.GetObj(EnumObj.QQLZHDData)
	if rewardId in getedData:
		print "GE_EXC,repeat random rewardId in QQLZHappyDraw.OnLottery"
		return
	with Tra_QQLZHappyDraw_Lottery:
		#增加已抽奖次数
		role.IncI8(EnumInt8.QQLZHappyDraw_UsedTimes, 1)
		getedData.add(rewardId)
		if len(getedData) >= 12:#一轮奖励全领完，制空进入下一轮
			role.SetObj(EnumObj.QQLZHDData, set())
		#同步并等待回调
		role.SendObjAndBack(QQLZHappyDraw_LotteryResult, rewardId, 8, LotteryCallBack, (role.GetRoleID(), coding, cnt))
		
def LotteryCallBack(role, callargv, regparam):
	'''
	抽奖回调
	'''
	roleId, coding, cnt = regparam
	if not roleId or not coding or not cnt:
		print "GE_EXC, QQLZHappyDraw error regparam:roleId(%s), coding(%s), cnt(%s)" % (roleId, coding, cnt)
		return
	
	Call.LocalDBCall(roleId, RealAward, (coding, cnt))
	
def RealAward(role, param):
	'''
	抽奖实际获得处理
	'''
	coding, cnt = param
	with Tra_QQLZHappyDraw_Lottery:
		#获得物品
		role.AddItem(coding, cnt)
		#加次数
		role.IncI16(EnumInt16.QQLZHappyDCrystal, EnumGameConfig.QQLZHappyDraw_CrystalBaseCnt)
	
	rewardPromt = GlobalPrompt.QQHZRoll_Tips_Head + GlobalPrompt.QQLZRoll_Tips_Item % (coding, cnt) + GlobalPrompt.QQLZRoll_Tips_Crystal % EnumGameConfig.QQLZRoll_CrystalBaseCnt
	role.Msg(2, 0, rewardPromt)
	#同步已领取列表给客户端
	role.SendObj(QQLZHappyDraw_GetList, role.GetObj(EnumObj.QQLZHDData))
	
def OnExchange(role, msg):
	'''
	蓝钻兑好礼_请求兑换
	@param msg: exchangeId
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.QQLZHappyDraw_NeedLevel:
		return
	
	#参数->配置
	exchangeId = msg
	exchangeCfg = QQLZHappyDrawConfig.QQLZ_HAPPYDRAW_EXCHANGE.get(exchangeId)
	if not exchangeCfg:
		print "GE_EXC,can not find exchangeId(%s) in QQLZHappyDrawConfig.QQLZ_HAPPYDRAW_EXCHANGE" % exchangeId
		return
	
	#剩余蓝钻水晶不足
	needCnt = exchangeCfg.needCnt
	effectCnt = role.GetI16(EnumInt16.QQLZHappyDCrystal)
	if effectCnt < needCnt:
		return
	
	coding, cnt = exchangeCfg.item
	with Tra_QQLZHappyDraw_Exchange:
		#扣除蓝钻水晶
		role.DecI16(EnumInt16.QQLZHappyDCrystal, needCnt)
		#获得物品
		role.AddItem(coding, cnt)
	
	#获得提示
	prompt = GlobalPrompt.QQLZRoll_Tips_HeadEx + GlobalPrompt.QQLZRoll_Tips_Item % (coding, cnt)
	role.Msg(2, 0, prompt)
	
def OpenPanel(role, param):
	'''
	客户端请求打开界面
	@param role:
	@param param:
	'''
	#同步已领取列表给客户端
	role.SendObj(QQLZHappyDraw_GetList, role.GetObj(EnumObj.QQLZHDData))
#===========玩家事件=============
def OnSyncRoleOtherData(role, param):
	if not IS_START:
		return
	role.SendObj(QQLZHappyDraw_ActiveState, (OPEN_STATE, ENDTIME))
	
def AfterLogin(role, param):
	if role.GetObj(EnumObj.QQLZHDData) == {}:
		role.SetObj(EnumObj.QQLZHDData, set())
		
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Initialize()
		#事件
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQLZHappyDraw_OnLottery", "蓝钻转转乐请求抽奖"), OnLottery)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQLZHappyDraw_Exchange", "蓝钻转转乐请求兑换"), OnExchange)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQLZHappyDraw_OpenPanel", "蓝钻转转乐请求打开界面"), OpenPanel)
