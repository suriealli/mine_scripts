#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQLZ.QQLZXunBaoMgr")
#===============================================================================
# 注释
#===============================================================================
import Environment
import cRoleMgr
import cDateTime
import random
import cNetMessage
import cComplexServer
from Util import Time
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumInt8, EnumTempInt64
from Game.ThirdParty.QQLZ import QQLZXunBaoConfig
from Common.Other import GlobalPrompt
from Common.Message import AutoMessage
from Game.Role import Event
OPEN_STATE = 1
CLOSE_STATE = 0

if "_HasLoad" not in dir():
	IS_START = False	#蓝钻寻宝活动开启标志
	ENDTIME = 0			#活动结束时间戳
	
	#日志
	QQLZXB_Add_Times = AutoLog.AutoTransaction("QQLZXB_Add_Times", "蓝钻寻宝增加次数")
	QQLZXB_Reward = AutoLog.AutoTransaction("QQLZXB_Reward", "蓝钻寻宝领取奖励")
	QQLZXB_BackHome = AutoLog.AutoTransaction("QQLZXB_BackHome", "蓝钻寻宝回到原点")
	
	#消息
	QQLZXunBao_Step_Sync = AutoMessage.AllotMessage("QQLZXunBao_Step_Sync", "同步蓝钻寻宝本次的骰子点数")
	QQLZXunBao_ActiveState_Sync = AutoMessage.AllotMessage("QQLZXunBao_ActiveState_Sync", "同步蓝钻寻宝活动状态")
#============= 活动控制 ====================
#启服之后根据当前时间和活动配置时间 注册tick控制活动
def Initialize():	
	'''
	初始化活动 tick
	'''
	#获取活动配置时间
	activeBase = QQLZXunBaoConfig.QQLZXunBao_Config_Base
	if not activeBase:
		print "GE_EXC, activeBase is None while Initialize QQLZXunBao"
		return
	beginDate = activeBase.beginDate
	endDate = activeBase.endDate
	
	#当前日期-时间
	nowDate = cDateTime.Now()
	nowTime = cDateTime.Seconds()
	#开始时间戳-结束时间戳
	beginTime = Time.DateTime2UnitTime(beginDate)
	endTime = Time.DateTime2UnitTime(endDate)
	
	if beginDate <= nowDate < endDate:
		#开启 并注册结束tick
		QQLZXunBao_Start(None, endTime)
		cComplexServer.RegTick(endTime - nowTime, QQLZXunBao_End)
	elif nowDate < beginDate:
		#注册开启和结束的tick
		cComplexServer.RegTick(beginTime - nowTime, QQLZXunBao_Start, endTime)
		cComplexServer.RegTick(endTime - nowTime, QQLZXunBao_End)
		
	#如果活动没有结束，对版本号进行检测
	if nowDate < endDate:
		Event.TriggerEvent(Event.Eve_QQCheckVersion, None, (1, beginDate, "QQLZXunBao"))

def QQLZXunBao_Start(callArgv, regParam):
	'''
	开启蓝钻寻宝活动
	'''
	global IS_START
	global ENDTIME
	if IS_START:
		print "GE_EXC,repeat start QQLZXunBao"
		return
	
	IS_START = True
	ENDTIME = regParam
	cNetMessage.PackPyMsg(QQLZXunBao_ActiveState_Sync, (OPEN_STATE, ENDTIME))
	cRoleMgr.BroadMsg()

def QQLZXunBao_End(callArgv, regParam):
	'''
	结束蓝钻寻宝活动
	'''
	global IS_START
	if not IS_START:
		print "GE_EXC,close QQLZXunBao while not open"
		return
	
	IS_START = False
	cNetMessage.PackPyMsg(QQLZXunBao_ActiveState_Sync, (CLOSE_STATE, ENDTIME))
	cRoleMgr.BroadMsg()
	

def RequestStepForward(role, param=None):
	'''
	 客户端请求蓝钻寻宝
	@param role:
	@param param is not used
	'''
	global IS_START
	if not IS_START:
		return
	#非蓝钻渠道
	if role.GetTI64(EnumTempInt64.QVIP) != 2:
		return
	activeBase = QQLZXunBaoConfig.QQLZXunBao_Config_Base
	if role.GetLevel() < activeBase.needLevel:
		return
	#判断蓝钻密匙够不够
	if role.GetI8(EnumInt8.QQLanZuanKaiTongTimes) <= role.GetI8(EnumInt8.QQLZXunBao):
		return
	#已经到达终点
	if role.GetI8(EnumInt8.QQLZXunBaoStep) >= 40:
		return
	XunBaoStep = random.randint(1, 6)
	#增加寻宝次数，要在函数回调之前增加次数，不然会多次触发此函数
	with QQLZXB_Add_Times:
		role.IncI8(EnumInt8.QQLZXunBao, 1)
		role.IncI8(EnumInt8.QQLZXunBaoStep, XunBaoStep)
		
	role.SendObjAndBack(QQLZXunBao_Step_Sync, [XunBaoStep], 20, OneTimeCallBack, XunBaoStep)

def OneTimeCallBack(role, callargv, argparam=None):
	'''
	一次抽奖客户端回调
	'''
	reward_Dict = QQLZXunBaoConfig.QQLZXunBao_DICT
	
	rewardIndex = role.GetI8(EnumInt8.QQLZXunBaoStep)
	if rewardIndex > 40:
		rewardIndex = 40
	reward = reward_Dict.get(rewardIndex, 0)
	if not reward:
		print "GE_EXC, QQLZXunBao has not the reward(%s)" % rewardIndex
		return 
	coding, cnt = reward
	#发物品
	with QQLZXB_Reward:		
		role.AddItem(coding, cnt)
	#获得提示及广播
	rewardPrompt = GlobalPrompt.Reward_Tips + GlobalPrompt.Item_Tips % (coding, cnt)
	role.Msg(2, 0, rewardPrompt)

def RequestBackHome(role, msg=None):
	'''
	蓝钻寻宝请求回到原点
	'''
	global IS_START
	if not IS_START:
		return
	
	activeBase = QQLZXunBaoConfig.QQLZXunBao_Config_Base
	if role.GetLevel() < activeBase.needLevel:
		return
	
	with QQLZXB_BackHome:
		role.SetI8(EnumInt8.QQLZXunBaoStep, 0)
	
	role.SendObj(QQLZXunBao_Step_Sync, [0])

def OnSyncRoleOtherData(role, param):
	if not IS_START:
		return
	role.SendObj(QQLZXunBao_ActiveState_Sync, (OPEN_STATE, ENDTIME))

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Initialize()
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		#注册消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQLZXBRequestStepForward", "蓝钻寻宝掷骰子向前走"), RequestStepForward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQLZXBRequestBackHome", "蓝钻寻宝回到原点"), RequestBackHome)
