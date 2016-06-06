#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.SystemRank.QQLogicRank")
#===============================================================================
# 腾讯消费排行榜 (消费神石，包括充值和奖励神石)
#===============================================================================
import Environment
import cProcess
import cDateTime
import cComplexServer
from Common.Message import PyMessage
from ComplexServer.Plug.Control import ControlProxy
from ComplexServer.Time import Cron
from Game.Role import Rank, Event
from Game.Role.Data import EnumDisperseInt32, EnumTempObj

class QQRank(Rank.SmallRoleRank):
	defualt_data_create = dict				#持久化数据需要定义的数据类型
	max_rank_size = 100						#最大排行榜 100个
	dead_time = (2038, 1, 1)

	name = "Rank_QQ"
	needSync = False
	
	# 返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		return v1[0] < v2[0]
	
	# 打开排行榜
	def Open(self, role, msg = None):
		#判断CD
		return
	
	def ReturnData(self):
		return self.data

	def Clear(self):
		self.data = {}
		self.min_role_id = 0
		self.min_value = None
		
		self.HasChange()

def AfterNewDay():
	#每天清理排行榜数据
	QQR.Clear()

def RoleDayClear(role, param):
	#角色每日清理
	role.SetDI32(EnumDisperseInt32.DayConsumeRMB, 0)


def  AfterConsume(role, param):
	#消费神石
	oldValue, newValue = param
	if newValue > oldValue:
		return
	role.IncDI32(EnumDisperseInt32.DayConsumeRMB, oldValue - newValue)
	QQR.HasData(role.GetRoleID(), (role.GetDI32(EnumDisperseInt32.DayConsumeRMB), role.GetRoleID(), role.GetRoleName(), role.GetTempObj(EnumTempObj.LoginInfo)['account']))


def RequestQQRank(sessionid, msg):
	backid, controlweekday = msg
	weekday = cDateTime.WeekDay()
	if controlweekday != weekday:
		return
	ControlProxy.CallBackFunction(sessionid, backid, (cProcess.ProcessID, weekday, QQR.data.values()))

def SendLoginRank():
	#23：58分主动发送一次，防止逻辑进程和控制进程的时间有差异
	ControlProxy.SendControlMsg(PyMessage.Control_ReceiveQQRank, (cProcess.ProcessID, cDateTime.WeekDay(), QQR.data.values()))


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		if Environment.IsQQ or Environment.IsDevelop:
			QQR = QQRank()
			Event.RegEvent(Event.AfterChangeUnbindRMB_Q, AfterConsume)
			Event.RegEvent(Event.AfterChangeUnbindRMB_S, AfterConsume)
			Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
			
			cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
			cComplexServer.RegDistribute(PyMessage.Control_RequestQQRank, RequestQQRank)
			Cron.CronDriveByMinute((2038, 1, 1), SendLoginRank, H = "H == 23", M = "M == 58")
			