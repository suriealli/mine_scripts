# -*- coding:UTF-8 -*-
# XRLAM("Control.GlobalControl.QQRank")
#===============================================================================
# 腾讯全服消费排行榜(所有的服务器)
#===============================================================================
import cDateTime
import cComplexServer
import Environment
from Common.Message import PyMessage
from Control import ProcessMgr
from ComplexServer.API import GlobalHttp
from ComplexServer.Plug.Control import ControlProxy
from ComplexServer.Time import Cron

if "_HasLoad" not in dir():
	TotalLogicCnt = 0
	LoginRankDict = {}
	WeekDay = cDateTime.WeekDay()
	DayID = int(cDateTime.Now().strftime('%Y%m%d'))

def GetLoginRank():
	#每小时向所有的逻辑进程发送指令获取排行榜数据,并且进行排序
	global TotalLogicCnt, WeekDay, DayID
	TotalLogicCnt = len(ProcessMgr.ControlProcesssSessions)
	WeekDay = cDateTime.WeekDay()
	DayID = int(cDateTime.Now().strftime('%Y%m%d'))
	for sessionid, cp in ProcessMgr.ControlProcesssSessions.iteritems():
		if cp.processid >= 30000:
			#跨服服务器不处理
			TotalLogicCnt -= 1
			continue
		ControlProxy.SendLogicMsgAndBack(sessionid, PyMessage.Control_RequestQQRank, WeekDay, LogicBackRank, sessionid)

def LogicBackRank(callargv, regparam):
	#逻辑进程返回或者自返回
	global TotalLogicCnt, WeekDay
	TotalLogicCnt -= 1
	if callargv:
		processId, logicweekday, logicranklist = callargv
		if logicweekday == WeekDay:
			LoginRankDict[processId] = logicranklist

	if TotalLogicCnt == 0:
		#所有的逻辑进程已经返回了排行榜,对排行榜进行排序,然后更新到数据库
		SortAndUpdataRank()

def SortAndUpdataRank():
	global LoginRankDict, WeekDay, DayID
	l = []
	for rl in LoginRankDict.itervalues():
		l.extend(rl)
	#排序，取前100名
	l.sort(key = lambda it:it[0], reverse = True)
	l = l[:100]
	
	#保存
	GlobalHttp.QQConsumeRank(l, DayID)

def ReceiveQQRank(sessionid, msg):
	#接收到逻辑进程发过来的排行榜
	processId, logicweekday, logicranklist = msg
	global WeekDay
	if logicweekday != WeekDay:
		return
	global LoginRankDict
	LoginRankDict[processId] = logicranklist

def AfterNewDay():
	global LoginRankDict, WeekDay
	LoginRankDict = {}
	WeekDay = cDateTime.WeekDay()

if "_HasLoad" not in dir():
	if Environment.HasControl:
		if Environment.IsQQ or Environment.IsDevelop:
			Cron.CronDriveByMinute((2038, 1, 1), GetLoginRank, M = "M == 58")
			cComplexServer.RegDistribute(PyMessage.Control_ReceiveQQRank, ReceiveQQRank)
			