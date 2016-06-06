#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.JT.JTTimeControl")
#===============================================================================
# 时间控制
#===============================================================================
import datetime
import cDateTime
import cRoleMgr
import cProcess
import Environment
from Common.Other import GlobalPrompt
from World import Define
from ComplexServer.Time import Cron
from Game.SysData import WorldData
from Game.JT import JTDefine
from Game.Role import Event




if "_HasLoad" not in dir():
	#跨服提前2分钟开启
	#在每日的10:00~13:00，15:00~18:00，22:00~23:30三个时间段可以进入跨服场景。
	JTStartCrossTimeConfig = [(9, 58, 13, 0), (14, 58, 18, 0), (21, 58, 23, 30)]
	JTStartLogicTimeConfig = [(10, 0, 13, 0), (15, 0, 18, 0), (22, 0, 23, 30)]


def IsZBTime():
	num = JTDefine.GetZBStartFlagNum()
	if num in [1,2,3,4]:
		return True
	return False
#############################################################################
#逻辑进程时间控制
#############################################################################
def CheckStartJTLogic(param1, param2):
	#因为活动时间长度大，所以需要在启动服务器的时候做开启检查，并且结束的触发也是要用cron而不是tick
	if WorldData.GetWorldLevel() < JTDefine.JTNeedWorldLevel:
		return
	if IsZBTime():
		return
	from Game.JT import JTeam
	nowTime = cDateTime.Now()
	year, month, day = cDateTime.Year(), cDateTime.Month(), cDateTime.Day()
	for startHour, startMinute, endHour, endMinute in JTStartLogicTimeConfig:
		startTime = datetime.datetime(year, month, day, startHour, startMinute, 0)
		endTime = datetime.datetime(year, month, day, endHour, endMinute, 0)
		if startTime < nowTime < endTime:
			JTeam.IsStart = True
			return

def StartJTLogic():
	if WorldData.GetWorldLevel() < JTDefine.JTNeedWorldLevel:
		return
	if Environment.IsCross:
		return
	if IsZBTime():
		return
	from Game.JT import JTeam
	JTeam.IsStart = True
	cRoleMgr.Msg(1, 0, GlobalPrompt.JT_Start)

def EndJTLogic():
	if Environment.IsCross:
		return
	from Game.JT import JTeam
	JTeam.IsStart = False


#############################################################################
#跨服进程时间控制
#############################################################################
def CheckStartJTCross(param1, param2):
	#因为活动时间长度大，所以需要在启动服务器的时候做开启检查，并且结束的触发也是要用cron而不是tick
	nowTime = cDateTime.Now()
	year, month, day = cDateTime.Year(), cDateTime.Month(), cDateTime.Day()
	from Game.JT import JTCross
	for startHour, startMinute, endHour, endMinute in JTStartCrossTimeConfig:
		startTime = datetime.datetime(year, month, day, startHour, startMinute, 0)
		endTime = datetime.datetime(year, month, day, endHour, endMinute, 0)
		if startTime < nowTime < endTime:
			JTCross.StartCrossJT()
			return

def StartJTCross():
	if not Environment.IsCross:
		return
	if not cProcess.ProcessID == Define.GetDefaultCrossID():
		return
	if IsZBTime():
		return
	from Game.JT import JTCross
	JTCross.StartCrossJT()

def EndJTCross():
	if not Environment.IsCross:
		return
	if not cProcess.ProcessID == Define.GetDefaultCrossID():
		return
	from Game.JT import JTCross
	JTCross.EndCrossJT()


if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.EnvIsQQ() or Environment.EnvIsFT() or Environment.IsDevelop or Environment.EnvIsNA() or (Environment.EnvIsRU() and not Environment.IsRUGN) or Environment.EnvIsPL()):
		if not Environment.IsCross:
			#本服
			Event.RegEvent(Event.Eve_AfterLoadWorldData, CheckStartJTLogic)
			#Init.InitCallBack.RegCallbackFunction(CheckStartJTLogic)
			for startHour, startMinute, endHour, endMinute in JTStartLogicTimeConfig:
				sH, sM = "H == %s" % startHour, "M == %s" % startMinute
				eH, eM = "H == %s" % endHour, "M == %s" % endMinute
				Cron.CronDriveByMinute((2038, 1, 1), StartJTLogic, H = sH, M=sM)
				Cron.CronDriveByMinute((2038, 1, 1), EndJTLogic, H = eH, M=eM)
		else:
			if cProcess.ProcessID == Define.GetDefaultCrossID():
				#跨服
				Event.RegEvent(Event.Eve_AfterLoadWorldData, CheckStartJTCross)
				#Init.InitCallBack.RegCallbackFunction(CheckStartJTCross)
				for startHour, startMinute, endHour, endMinute in JTStartCrossTimeConfig:
					sH, sM = "H == %s" % startHour, "M == %s" % startMinute
					eH, eM = "H == %s" % endHour, "M == %s" % endMinute
					Cron.CronDriveByMinute((2038, 1, 1), StartJTCross, H = sH, M=sM)
					Cron.CronDriveByMinute((2038, 1, 1), EndJTCross, H = eH, M=eM)
