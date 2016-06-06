#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Control.GlobalControl.TurnTableControl")
#===============================================================================
# 神石大转盘控制
#===============================================================================
import time
import random
import datetime
import cDateTime
import cComplexServer
import Environment
import DynamicPath
from Util.File import TabFile
from Control import ProcessMgr
from Common.Message import PyMessage
from Common.Other import GlobalDataDefine, EnumGameConfig
from ComplexServer.Time import Cron
from ComplexServer.Plug.Control import ControlProxy
from ComplexServer.API import GlobalHttp

if "_HasLoad" not in dir():
	IsStart = False
	ActiveID = 0
	
	#总的逻辑进程个数
	TotalLogicCnt = 0
	#奖池神石数
	TotalPoolValue = 0
	#临时奖池神石数（统计的时候要用的）
	TotalPoolValueEx = 0
	#收集数据的时候返回的进程id集合
	BackProcessIdSet = set()
	
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("CircularActive")
#===============================================================================
# 配置
#===============================================================================
class TurnTableActiveConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("TurnTableActive.txt")
	def __init__(self):
		self.activeID = int
		self.beginTime = eval
		self.endTime = eval
	
	def Active(self):
		beginTime = int(time.mktime(datetime.datetime(*self.beginTime).timetuple()))
		endTime = int(time.mktime(datetime.datetime(*self.endTime).timetuple()))
		nowTime = cDateTime.Seconds()
		if beginTime <= nowTime < endTime:
			#激活
			OpenActive(None, self.activeID)
			cComplexServer.RegTick(endTime - nowTime, CloseActive)
		elif nowTime < beginTime:
			#注册一个tick激活
			cComplexServer.RegTick(beginTime - nowTime, OpenActive, self.activeID)
			cComplexServer.RegTick(endTime - nowTime, CloseActive)
		
def LoadTurnTableActiveConfig():
	for cfg in TurnTableActiveConfig.ToClassType(False):
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in TurnTableActiveConfig"
		cfg.Active()
#===============================================================================
# 活动开关
#===============================================================================
def OpenActive(callArgv, regparam):
	global IsStart, ActiveID
	if IsStart:
		print 'GE_EXC, repeat start TurnTable'
	IsStart = True
	ActiveID = regparam
	
	#因为这里要给一个初始值
	#活动开启的时候载回数据、初始化数据、同步数据
	GlobalHttp.GetGlobalData(GlobalDataDefine.TurnTablePoolValueKey, OnGetPoolValueBack)
	
def CloseActive(callArgv, regparam):
	global IsStart
	if not IsStart:
		print 'GE_EXC, repeat end TurnTable'
	IsStart = False
	
def RequestLogicPoolValue():
	#向所有的逻辑进程获取奖池数据
	global IsStart
	if not IsStart: return
	
	global TotalLogicCnt
	TotalLogicCnt = len(ProcessMgr.ControlProcesssSessions)
	
	for sessionid, cp in ProcessMgr.ControlProcesssSessions.iteritems():
		if cp.processid >= 30000:
			#跨服服务器不处理
			TotalLogicCnt -= 1
			continue
		ControlProxy.SendLogicMsgAndBack(sessionid, PyMessage.Control_RequestLogicTurnTablePoolValue, None, LogicBackPoolValue, sessionid)

def LogicBackPoolValue(callargv, regparam):
	#逻辑进程返回或者自返回
	global TotalLogicCnt, TotalPoolValue, TotalPoolValueEx, ActiveID, BackProcessIdSet
	TotalLogicCnt -= 1
	
	if callargv:
		processId, poolValue = callargv
		if processId in BackProcessIdSet:
			#防止重复计算
			return
		#盈亏 = 逻辑进程奖池神石数 - 上次同步的奖池神石数
		TotalPoolValueEx = TotalPoolValueEx + poolValue - TotalPoolValue

	if TotalLogicCnt == 0:
		#所有逻辑进程都已经返回了
		#更新全服奖池数据
		TotalPoolValue += TotalPoolValueEx
		
		if TotalPoolValue < EnumGameConfig.TurnTableInitPoolValue:
			#奖池神石数少于初始奖池神石数
			TotalPoolValue = EnumGameConfig.TurnTableInitPoolValue
		elif TotalPoolValue > 250000:
			#奖池数超过25w的话, 在24w和25w之间随机取一个数
			TotalPoolValue = random.randint(240000, 250000)
		
		TotalPoolValueEx = 0
		BackProcessIdSet = set()
		#保存全局数据
		GlobalHttp.SetGlobalData(GlobalDataDefine.TurnTablePoolValueKey, (ActiveID, TotalPoolValue))
		#同步所有逻辑进程
		SyncAllLogic()
	elif TotalLogicCnt < 0:
		print "GE_EXC, error in TurnTableControl RequestBack (%s)" % TotalLogicCnt
	
def SyncAllLogic():
	#同步所有逻辑进程
	global TotalPoolValue
	for sessionid, cp in ProcessMgr.ControlProcesssSessions.iteritems():
		if cp.processid >= 30000:
			#跨服服务器不处理
			continue
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataTurnTablePoolValueToLogic, TotalPoolValue)
	
def InitGetRankEx():
	#载回全服奖池数据
	GlobalHttp.GetGlobalData(GlobalDataDefine.TurnTablePoolValueKey, OnGetPoolValueBack)
	
def OnGetPoolValueBack(response, regparam):
	#http返回
	if response is None:
		return
	
	#检查数据
	CheckPoolValue(response)
	
def CheckPoolValue(response):
	global ActiveID, TotalPoolValue
	
	if not response:
		#初始化数据格式
		activeID, poolValue = 0, 0
	else:
		activeID, poolValue = response
	
	if activeID != ActiveID:
		#活动id不一样, 清理数据
		GlobalHttp.SetGlobalData(GlobalDataDefine.TurnTablePoolValueKey, (ActiveID, EnumGameConfig.TurnTableInitPoolValue))
		TotalPoolValue = EnumGameConfig.TurnTableInitPoolValue
	else:
		TotalPoolValue = poolValue
	
	#数据载回来了, 同步逻辑进程
	SyncAllLogic()
	
def LoginRequestGlobalPoolValue(sessionid, msg):
	#逻辑进程向控制进程请求数据
	global TotalPoolValue
	if not TotalPoolValue:
		#数据还没有载回来, 等载回来的时候再同步给逻辑进程
		return
	
	ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataTurnTablePoolValueToLogic, TotalPoolValue)
	
if "_HasLoad" not in dir():
	if Environment.HasControl:
		LoadTurnTableActiveConfig()
		
		#这里不用在起服的时候载回了, 活动开启的时候会给一个初始值
		#InitGetRankEx()
		
		Cron.CronDriveByMinute((2038, 1, 1), RequestLogicPoolValue, M="M == 30 or M == 0")
		
		cComplexServer.RegDistribute(PyMessage.Control_GetGlobalTurnTablePoolValue, LoginRequestGlobalPoolValue)
		
