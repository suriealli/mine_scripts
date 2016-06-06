#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.SevenDayHegemony.SDHFunGather")
#===============================================================================
# 七日争霸函数集合，与客户端的交互统统放在这个模块
#===============================================================================
import datetime
import cRoleMgr
import Environment
from Game.Role import Event
from Game.SysData import WorldData
from Game.Role.Data import EnumObj
from Common.Other import EnumSysData
from Game.Persistence import Contain
from Common.Message import AutoMessage
from Game.Activity.SevenDayHegemony import SDHDefine
from ComplexServer.Time.Cron import cDateTime
from Util import Time
import cComplexServer

if "_HasLoad" not in dir():
	NeedRoleLevel = 30					#需要的角色等级
	SDHActConfigDict = {}				#七日争霸时间配置字典	
	TargetRewardFun_Dict = {}			#七日争霸目标奖励函数字典
	RankRewardFun_Dict = {}				#七日争霸排行榜奖励函数字典
	MailRewardFun_Dict = {}				#七日争霸邮件发放奖励函数字典
	RankAccountFun_Dict = {}			#七日争霸排行榜计算函数字典
	
	
	#活动开启结束的标志
	StartFlag = {SDHDefine.Purgatory:False,
				SDHDefine.TeamTower:False,
				SDHDefine.UnionFB:False
				}
	
	#繁体的时间
	if Environment.EnvIsFT():
		#早于这个时间开服的服务器不开启七日争霸活动
		SDHTime = datetime.datetime(2015, 1, 16, 2, 0, 0)
		#这个时间之后开的服都不开七日争霸
		SDHNewTime = datetime.datetime(2020, 10, 23, 2, 0, 0)
	elif Environment.EnvIsPL():
		#早于这个时间开服的服务器不开启七日争霸活动
		SDHTime = datetime.datetime(2015, 1, 11, 2, 0, 0)
		#这个时间之后开的服都不开七日争霸
		SDHNewTime = datetime.datetime(2015, 12, 10, 2, 0, 0)
	#其他的时间
	else:
		#早于这个时间开服的服务器不开启七日争霸活动
		SDHTime = datetime.datetime(2015, 1, 11, 2, 0, 0)
		#这个时间之后开的服都不开七日争霸
		SDHNewTime = datetime.datetime(2015, 10, 23, 2, 0, 0)
	
	TryActiveTickId = 0 
	
	#消息
	SyncSevenDayHegemontRankData = AutoMessage.AllotMessage("SyncSevenDayHegemontRankData", "同步七日争霸排行榜信息 ")
	SyncSevenDayHegemontRankAwardLog = AutoMessage.AllotMessage("SyncSevenDayHegemontRankAwardLog", "同步七日争霸排行奖励领取信息 ")
	SyncSevenDayHegemonyTargetAwardLog = AutoMessage.AllotMessage("SyncSevenDayHegemonyTargetAwardLog", "同步七日争霸目标奖励领取信息 ")

def IsOldServer():
	kaifuTime = WorldData.WD[EnumSysData.KaiFuKey]
	return kaifuTime < SDHTime or kaifuTime > SDHNewTime

#=============================================================================================
#奖励函数注册
#=============================================================================================
def RegTargetRewardFun(actType):
	'''
	注册目标奖励函数
	'''
	def f(fun):
		global TargetRewardFun_Dict
		if actType in TargetRewardFun_Dict:
			print "GE_EXC,repeat actType in RegTargetRewardFun (%s) in SevenDayHegemony" % actType
		TargetRewardFun_Dict[actType] = fun
		return fun
	return f	


def RegRankRewardFun(actType):
	'''
	注册排行榜奖励函数
	'''
	def f(fun):
		global RankRewardFun_Dict
		if actType in RankRewardFun_Dict:
			print "GE_EXC,repeat targetType in RegRankRewardFun (%s) in SevenDayHegemony" % actType
		RankRewardFun_Dict[actType] = fun
		return fun
	return f


def RegMailRewardFun(actType):
	'''
	注册邮件奖励函数
	'''
	def f(fun):
		global MailRewardFun_Dict
		if actType in MailRewardFun_Dict:
			print "GE_EXC,repeat targetType in RegMailRewardFun (%s) in SevenDayHegemony" % actType
		MailRewardFun_Dict[actType] = fun
		return fun
	return f


def RegRankAccountFun(actType):
	'''
	注册目标奖励函数
	'''
	def f(fun):
		global RankAccountFun_Dict
		if actType in RankAccountFun_Dict:
			print "GE_EXC,repeat actType in RankAccountFun_Dict (%s) in SevenDayHegemony" % actType
		RankAccountFun_Dict[actType] = fun
		return fun
	return f	


#=======================================================================================
#客户端请求
#=======================================================================================
def RequestTargetReward(role, msg):
	'''
	客户端请求领取七日争霸目标奖励
	'''
	if role.GetLevel() < NeedRoleLevel:
		return
	actType, Index = msg
	if not StartFlag[actType]:
		return
	
	fun = TargetRewardFun_Dict.get(actType)
	if fun is None:
		return
	fun(role, Index)


def RequestRankReward(role, msg):
	'''
	客户端请求领取日日争霸排行榜奖励
	'''
	if role.GetLevel() < NeedRoleLevel:
		return
	#只有在七日争霸活动有任何一个子活动在开启的情况下才能领取
	if IsAllEnd():
		return
	
	actType = msg
	fun = RankRewardFun_Dict.get(actType)
	if fun is None:
		return
	fun(role)


def RequestOpenPanel(role, msg):
	'''
	客户端请求打开面板
	'''
	if role.GetLevel() < NeedRoleLevel:
		return
	SyncTargetAwardLog(role)
	SyncRankAwardLog(role)
	SyncRank(role)
	

def MailReward(actType):
	'''
	邮件发放活动排名奖励
	'''
	fun = MailRewardFun_Dict.get(actType)
	if fun is None:
		return
	
	actCfg = SDHActConfigDict.get(actType)
	if actCfg is None:
		return
	actName = actCfg.Name
	
	rankDict = SevenDayHegemonyDict.get('rankData', {}).get(actType, {})
	for objectID, data in rankDict.iteritems():
		rank = data[0]
		fun(objectID, rank, actName)


def RankAccount(actType):
	'''
	结算排行榜
	'''
	fun = RankAccountFun_Dict.get(actType)
	if fun is None:
		return
	#已经结算过了
	if actType in SevenDayHegemonyDict.get("accountSet", set()):
		return
	fun()


def SyncTargetAwardLog(role):
	'''
	同步客户端目标奖励领取情况
	'''
	data = role.GetObj(EnumObj.SevenDayHegemony)
	role.SendObj(SyncSevenDayHegemonyTargetAwardLog, data)
	

def SyncRankAwardLog(role):
	'''
	同步客户端排行奖励领取情情况
	'''
	roleId = role.GetRoleID()
	data = SevenDayHegemonyDict.get('rankAwardLog', {}).get(roleId, set())
	role.SendObj(SyncSevenDayHegemontRankAwardLog, data)


def SyncRank(role):
	'''
	同步客户端排行榜信息
	'''
	data = SevenDayHegemonyDict.get('rankData', {})
	role.SendObj(SyncSevenDayHegemontRankData, data)


def IsAllEnd():
	'''
	七日争霸活动全部结束
	'''
	return StartFlag.values() == len(StartFlag) * [False]



def OnRoleLoginSyncData(role, param):
	'''
	角色上线后同步所有七日争霸的数据
	'''
	if role.GetLevel() < NeedRoleLevel:
		return
	#所有活动均未开启 
	if IsAllEnd():
		return
		
	roleId = role.GetRoleID()
	data1 = role.GetObj(EnumObj.SevenDayHegemony)
	data2 = SevenDayHegemonyDict.get('rankAwardLog', {}).get(roleId, set())
	data3 = SevenDayHegemonyDict.get('rankData', {})
	role.SendObj(SyncSevenDayHegemonyTargetAwardLog, data1)
	role.SendObj(SyncSevenDayHegemontRankAwardLog, data2)
	role.SendObj(SyncSevenDayHegemontRankData, data3)


#=================================================================================
#三触发，在世界数据载回，持久化数据载回和配置表载入之后分别进行一次触发
#                                       顺序可能颠倒
#                          ↓¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯↓
#数据载入过程------------->worldData--------------------->persistensData-------------->
#                              ↑                                   ↑
#活动开启三触发 --------------------->AfterLoadWorldData----------------->AfterLoad---->
#================================================================================
def AfterLoadWorldData(param1, param2):
	#世界数据载回后尝试触发活动
	#如果持久化字典没有载回的等持久化字典载回后再尝试触发
	if IsOldServer():
		return
	if not SevenDayHegemonyDict.returnDB: 
		return
	
	global SDHActConfigDict
	if not SDHActConfigDict:
		print "GE_EXC, error! no SDHActConfigDict!"
		return
	TryActive()


def AfterLoad():
	global SevenDayHegemonyDict
	SevenDayHegemonyDict.setdefault('accountSet', set())
	#世界数据没有载回的话等世界数据载回后再尝试触发
	if not WorldData.WD.returnDB:
		return
	if IsOldServer():
		return
	global SDHActConfigDict
	if not SDHActConfigDict:
		print "GE_EXC, error! no SDHActConfigDict!"
		return
	TryActive()


def TryActive(arg=None, param=None):
	if Environment.EnvIsRU():
		#俄罗斯屏蔽七日争霸
		return
	
	#当前时间
	nowSeconds = cDateTime.Seconds()
	#开服时间
	worldData = WorldData.WD[EnumSysData.KaiFuKey]
	kaifuSeconds = Time.DateTime2UnitTime(worldData)
	
	
	if kaifuSeconds > nowSeconds:
		global TryActiveTickId
		TryActiveTickId = cComplexServer.RegTick(kaifuSeconds - nowSeconds + 5, TryActive, None)
		return
		
	for config in SDHActConfigDict.itervalues():
		config.Active()

	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#{"accountSet"已经结算的活动:set([1,2,3])},"rankData":{actType:{rankList排行字典}}，"rankAwardLog":{roleID-->set([领取过排行奖励的actType])}}
		SevenDayHegemonyDict = Contain.Dict("SevenDayHegemonyDict", (2038, 1, 1), afterLoadFun=AfterLoad)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnRoleLoginSyncData)
		Event.RegEvent(Event.Eve_AfterLoadWorldData, AfterLoadWorldData)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestTargetAward_SDH", "客户端请求领取七日争霸目标奖励"), RequestTargetReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestRankAward_SDH", "客户端请求领取七日争霸排行奖励"), RequestRankReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestOpenPanel_SDH", "客户端请求打开七日争霸面板"), RequestOpenPanel)
		

