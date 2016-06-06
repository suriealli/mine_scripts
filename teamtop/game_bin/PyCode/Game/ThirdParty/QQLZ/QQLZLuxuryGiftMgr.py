#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQLZ.QQLZLuxuryGiftMgr")
#===============================================================================
# 蓝钻豪华六重礼Mgr
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
from Game.Role.Data import EnumTempInt64, EnumInt8
from Game.ThirdParty.QQLZ import QQLZLuxuryGiftConfig

OPEN_STATE = 1
CLOSE_STATE = 0

if "_HasLoad" not in dir():
	IS_START = False	#蓝钻豪华六重礼活动开关标志
	ENDTIME = 0			#活动结束时间戳
	#消息
	QQLZLuxuryGift_ActiveState_Sync = AutoMessage.AllotMessage("QQLZLuxuryGift_ActiveState_Sync", "同步蓝钻六重礼活动状态")
	#事务
	Tra_QQLZLuxuryGift_GetReward = AutoLog.AutoTransaction("Tra_QQLZLuxuryGift_GetKaiTongReward", "领取蓝钻六重礼奖励")

#============= 活动控制 ====================
#启服之后根据当前时间和活动配置时间 注册tick控制活动
def Initialize():	
	'''
	初始化活动tick
	'''
	#获取活动配置时间
	activeBase = QQLZLuxuryGiftConfig.QQLZLuxuryGift_Config_Base
	if not activeBase:
		print "GE_EXC, activeBase is None while Initialize QQLZLuxuryGift"
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
		QQLZLuxuryGift_Start(None, endTime)
		cComplexServer.RegTick(endTime - nowTime, QQLZLuxuryGift_End)
	elif nowDate < beginDate:
		#注册开启和结束的tick
		cComplexServer.RegTick(beginTime - nowTime, QQLZLuxuryGift_Start, endTime)
		cComplexServer.RegTick(endTime - nowTime, QQLZLuxuryGift_End)

	#如果活动没有结束，对版本号进行检测
	if nowDate < endDate:
		Event.TriggerEvent(Event.Eve_QQCheckVersion, None, (2, beginDate, "QQLZLuxuryGift"))

def QQLZLuxuryGift_Start(callArgv, regParam):
	'''
	开启蓝钻豪华六重礼
	'''
	global IS_START
	global ENDTIME
	if IS_START:
		print "GE_EXC,repeat start QQLZLuxuryGift"
		return
	
	IS_START = True
	ENDTIME = regParam
	cNetMessage.PackPyMsg(QQLZLuxuryGift_ActiveState_Sync, (OPEN_STATE, ENDTIME))
	cRoleMgr.BroadMsg()

def QQLZLuxuryGift_End(callArgv, regParam):
	'''
	结束蓝钻豪华六重礼
	'''
	global IS_START
	if not IS_START:
		print "GE_EXC,close QQLZLuxuryGift while not open"
		return
	
	IS_START = False
	cNetMessage.PackPyMsg(QQLZLuxuryGift_ActiveState_Sync, (CLOSE_STATE, ENDTIME))
	cRoleMgr.BroadMsg()

#### 请求 start ####
def OnGetReward(role, msg):
	'''
	领取蓝钻豪华六重礼某项奖励
	@param msg: rewardId 欲领取的奖励ID 
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.QQLZLuxuryGift_NeedLevel:
		return
	
	#非蓝钻渠道
	isQQGame = role.GetTI64(EnumTempInt64.IsQQGame)
	is3366 = role.GetTI64(EnumTempInt64.Is3366)
	if not isQQGame and not is3366:
		return
	
	#查找对应奖励配置项
	rewardId = msg
	rewardCfg = QQLZLuxuryGiftConfig.QQLZLuxuryGift_Reward_Dict.get(rewardId)
	if not rewardCfg:
		print "GE_EXC, error rewardId(%s) can not get rewardCfg while get QQLZLuxuryGift" % rewardId
		return
	
	#已领取
	rewardRecord = role.GetI8(EnumInt8.QQLZLuxuryGiftRewardRecord)
	if rewardRecord & rewardId:
		print "GE_EXC, rewardId(%s) has been getton before" % rewardId
		return
	
	#开通次数是否满足
	needKaiTongTimes = rewardCfg.needKaiTongTimes
	effectKaiTongTimes = role.GetI8(EnumInt8.QQHaoHuaLanZuanKaiTongTimes)
	if effectKaiTongTimes < needKaiTongTimes:
		print "GE_EXC,QQLZLuxuryGift::effectKaiTongTimes(%s) < needKaiTongTimes(%s) can not get rewardId(%s)" % (effectKaiTongTimes, needKaiTongTimes,rewardId)
		return
	
	coding, cnt = rewardCfg.item
	rewardPrompt = GlobalPrompt.QQLZLuxuryGift_Tips_Head + GlobalPrompt.QQLZLuxuryGift_Tips_Item % (coding, cnt)
	with Tra_QQLZLuxuryGift_GetReward:
		#更新领取记录
		role.IncI8(EnumInt8.QQLZLuxuryGiftRewardRecord, rewardId)
		#发奖
		role.AddItem(coding, cnt)
	#获得提示 及 广播
	role.Msg(2, 0, rewardPrompt)
	
#### 事件 start ####
def OnSyncRoleOtherData(role, param):
	'''
	登录同步蓝钻豪华六重礼开启状态
	'''
	if not IS_START:
		return
	role.SendObj(QQLZLuxuryGift_ActiveState_Sync, (OPEN_STATE, ENDTIME))
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#pre_process
		Initialize()
		#事件
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQLZLuxuryGift_OnGetReward", "蓝钻豪华六重礼领取奖励"), OnGetReward)
