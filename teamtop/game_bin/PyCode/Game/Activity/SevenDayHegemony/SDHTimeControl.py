#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.SevenDayHegemony.SDHTimeControl")
#===============================================================================
# 七日争霸时间控制模块
#===============================================================================

import cRoleMgr
import cDateTime
import cNetMessage
import cComplexServer
import DynamicPath
import Environment
from Util import Time
from Game.Role import Event
from Util.File import TabFile
from Game.SysData import WorldData
from Common.Other import EnumSysData
from Common.Message import AutoMessage
from Game.Activity.SevenDayHegemony import SDHDefine, SDHFunGather

if "_HasLoad" not in dir():
	FileFolderPath = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FileFolderPath.AppendPath("SevenDayHegemony")
	
	OneDay = 24 * 60 * 60
	SDHActEndTimeDict = {}			#七日争霸结束时间字典actType-->endTime
	
	#消息
	SyncSDHEndTime = AutoMessage.AllotMessage("SyncSevenDayHegemonyEndTime", "同步七日争霸所有活动的结束时间")
	TellClientSevenDayHegemonyAllEnd = AutoMessage.AllotMessage("TellClientSevenDayHegemonyAllEnd", "通知客户端七日争霸的所有活动都结束了")


class SDHActConfig(TabFile.TabLine):
	FilePath = FileFolderPath.FilePath("SDHAct.txt")
	startTickId = 0
	endTickId = 0
	lastTickId = 0
	def __init__(self):
		self.actType = int				#活动类型
		self.isLastAct = int			#是否最后一个活动
		self.beginDay = int				#活动开启
		self.continueDay = int			#持续天数
		self.Name = str					#活动名字
		
	def Active(self):
		
		#当前时间
		nowSeconds = cDateTime.Seconds()
		#开服时间
		worldData = WorldData.WD[EnumSysData.KaiFuKey]

		kaifuSeconds = Time.DateTime2UnitTime(worldData)
		
		#时间错了
		if nowSeconds < kaifuSeconds:
			print 'GE_EXC, SDHActConfig Active time error'
			return
		
		#计算开始时间
		beginSeconds = kaifuSeconds + self.beginDay * OneDay
		#结束时间
		self.endSeconds = beginSeconds + self.continueDay * OneDay

		#缓存住活动结束时间
		global SDHActEndTimeDict
		SDHActEndTimeDict[self.actType] = self.endSeconds
		
		#如果当前时间正正好是在活动的开启期间
		if beginSeconds <= nowSeconds < self.endSeconds:
			#活动开启 
			StartSDHAct(None, self.actType)
			self.startTickId = 0
			#注册活动结束的tick
			self.endTickId = cComplexServer.RegTick(self.endSeconds - nowSeconds, EndSDHAct, self.actType)
			
			#如果是最后一个活动的话
			if self.isLastAct:
				#注册最后一个活动的tick，这里延迟十秒等待排行奖励的结算
				self.lastTickId = cComplexServer.RegTick(self.endSeconds - nowSeconds + 10, EndLastTarget)
		
		#如果当前的时间在活动开启之前	
		elif nowSeconds < beginSeconds:
			#在开始时间戳之前，则需要注册活动开始和结束的tick，如果是最后一个活动，还要注册最后一个活动结束的tick
			self.startTickId = cComplexServer.RegTick(beginSeconds - nowSeconds, StartSDHAct, self.actType)
			self.endTickId = cComplexServer.RegTick(self.endSeconds - nowSeconds, EndSDHAct, self.actType)
			
			if self.isLastAct:
				self.lastTickId = cComplexServer.RegTick(self.endSeconds - nowSeconds + 10, EndLastTarget)

		#活动已经结束，则判断活动是否结算过，如果没有结算过，则应该对活动进行结算。避免在结算时间刚好服务器维护，导致活动没有结算数据
		else:
			if self.actType not in SDHFunGather.SevenDayHegemonyDict.get("accountSet", set()):
				SDHFunGather.RankAccount(self.actType)


	def AfterSetKaifuTime(self):
		'''
		重新设置开服时间后的处理,清理掉已经注册的tick
		'''
		if self.startTickId:
			#如果活动尚未开启，则应该取消掉活动开始和结束的tick
			cComplexServer.UnregTick(self.startTickId)
			cComplexServer.UnregTick(self.endTickId)
			cComplexServer.UnregTick(self.lastTickId)
		elif self.endTickId:
			#取消结束tick
			cComplexServer.UnregTick(self.endTickId)
			SDHFunGather.StartFlag[self.actType] = False
			if self.lastTickId:
				#取消最后一个活动结束tick
				cComplexServer.UnregTick(self.lastTickId)
			
		#清理掉开始和结束的tickID
		self.startTickId = 0
		self.endTickId = 0
		self.lastTickId = 0



def LoadSDHActConfig():
	SDHActConfigDict = SDHFunGather.SDHActConfigDict
	for config in SDHActConfig.ToClassType():
		if config.actType in SDHActConfigDict:
			print 'GE_EXC, repeat actType %s in SDHActiveConfigDict' % config.actType
			continue
		SDHActConfigDict[config.actType] = config
		
	if not SDHFunGather.SevenDayHegemonyDict.returnDB: 
		return
	if not WorldData.WD.returnDB:
		return
	if SDHFunGather.IsOldServer():
		return
	SDHFunGather.TryActive()
		

#===========================================================
#七日争霸活动开启函数
#===========================================================
def AfterSetKaiFuTime(callargv, regparam):
	'''
	在设置开服时间后的处理
	'''
	#首先清理掉之前tick
	if SDHFunGather.TryActiveTickId > 0:
		cComplexServer.UnregTick(SDHFunGather.TryActiveTickId)
		SDHFunGather.TryActiveTickId = 0
	
	SDHActConfigDict = SDHFunGather.SDHActConfigDict
	#先把缓存的活动结束时间清理掉
	global SDHActEndTimeDict
	SDHActEndTimeDict.clear()
	
	#设置开服时间后先删除持久化字典, 之后会根据时间结算排行榜
	SevenDayHegemonyDict = SDHFunGather.SevenDayHegemonyDict
	SevenDayHegemonyDict.clear()
	SevenDayHegemonyDict['accountSet'] = set()
	
	#对所有的时间配置进行设置开服时间后的处理
	for config in SDHActConfigDict.itervalues():
		config.AfterSetKaifuTime()
		
	#当前时间
	nowSeconds = cDateTime.Seconds()
	#开服时间
	worldData = WorldData.WD[EnumSysData.KaiFuKey]
	kaifuSeconds = Time.DateTime2UnitTime(worldData)
	
	#老服不开
	if SDHFunGather.IsOldServer():
		return
	#开服时间超过14天不开
	elif nowSeconds - kaifuSeconds >= 14 * OneDay:
		return
	
	SDHFunGather.TryActive()
	#同步客户端最新的活动结束时间
	cNetMessage.PackPyMsg(SyncSDHEndTime, SDHActEndTimeDict)
	cRoleMgr.BroadMsg()


def StartSDHAct(callargv, regparam):
	'''
	开启某个七日争霸活动
	'''
	actType = regparam
	StartFlag = SDHFunGather.StartFlag
	if StartFlag.setdefault(actType, False) is True:
		print "GE_EXC, actType(%s) has already started!" % actType
		return
	StartFlag[actType] = True


def EndSDHAct(callargv, regparam):
	'''
	结束某个七日争霸活动
	'''
	actType = regparam
	StartFlag = SDHFunGather.StartFlag
	if StartFlag.setdefault(actType, False) is  not True:
		print "GE_EXC, actType(%s) has already ended!" % actType
		return
	StartFlag[actType] = False
	SDHFunGather.RankAccount(actType)


def EndLastTarget(callargv, regparam):
	'''
	结束所有的七日争霸活动,对没有领取过排行奖励的玩家发放邮件奖励
	'''
	accountSet = SDHFunGather.SevenDayHegemonyDict.get('accountSet', set())
	if len(accountSet) != 3:
		print "GE_EXC, SevenDayHegemony all end but not all account. accountSet is %s" % str(accountSet)
		return
	for actType in [SDHDefine.Purgatory, SDHDefine.TeamTower, SDHDefine.UnionFB]:
		#邮件发放奖励
		SDHFunGather.MailReward(actType)
	
	cNetMessage.PackPyMsg(TellClientSevenDayHegemonyAllEnd, None)
	cRoleMgr.BroadMsg()


def OnRoleLoginSyncData(role, param):
	'''
	角色上线后同步所有的七日争霸活动的结束时间
	'''
	role.SendObj(SyncSDHEndTime, SDHActEndTimeDict)


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnRoleLoginSyncData)
		Event.RegEvent(Event.Eve_AfterSetKaiFuTime, AfterSetKaiFuTime)
		LoadSDHActConfig()
