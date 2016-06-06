#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.NationDay.NationBack")
#===============================================================================
# 神石回赠
#===============================================================================
import Environment
import datetime
import cRoleMgr
import cDateTime
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Activity import CircularDefine, CircularActive
from Game.Persistence import Contain
from Game.Role.Config import RoleConfig

if "_HasLoad" not in dir():
	#判断神石回赠的字典是否载回来了
	isNationDickNotReturn = False
	isNationBackOpen = False
	needResetRoleIdSet = set()
	
	#{活动第几天:[当天充值神石, 当天获得经验, 是否领取, 当天开始时的经验], ...}
	NationBackData = AutoMessage.AllotMessage("NationBackData", "节日有礼回赠数据")
	
	NationBack_Log = AutoLog.AutoTransaction("NationBack_Log", "领取节日有礼回赠日志")

def ActiveLastTime():
	#这个函数用来控制活动开启的时间，如果是繁体版的话则时间是8天
	lastTime = 12
	if Environment.EnvIsFT():
		lastTime = 7
	return lastTime

#===============================================================================
# 客户端请求
#===============================================================================
def RequestNationBack(role, msg):
	'''
	请求领取回赠
	@param role:
	@param msg:存放的Unix天数
	'''
	global isNationBackOpen
	if not isNationBackOpen: return
	
	global NationBackDict
	if not NationBackDict.returnDB: return
	
	days = msg
	roleId = role.GetRoleID()
	
	if role.GetLevel() < EnumGameConfig.NationLevelLimit:
		return
	beginDays = NationBackDict.get('begin_days')
	if not beginDays:
		return
	nationData = NationBackDict.get(roleId)
	if not nationData:
		return
	if days not in nationData:
		return
	pastDays = cDateTime.Days() - beginDays - days + 1
	if pastDays < ActiveLastTime():
		return
	backRMB, backExp, isAward, _ = nationData[days]
	if isAward:
		return
	if not backRMB and not backExp:
		return
	nationData[days][2] = 1
	NationBackDict.changeFlag = True
	
	with NationBack_Log:
		if backRMB:
			rewardRMB = backRMB * 5 / 100
			role.IncUnbindRMB_S(rewardRMB)
			role.Msg(2, 0, GlobalPrompt.UnBindRMB_Tips % rewardRMB)
		if backExp:
			rewardExp = backExp * 5 / 100
			role.IncExp(backExp * 5 / 100)
			role.Msg(2, 0, GlobalPrompt.Exp_Tips % rewardExp)
	role.SendObj(NationBackData, nationData)
	
def RequestOpenNationBack(role, msg):
	'''
	请求打开神石回赠面板
	@param role:
	@param msg:
	'''
	global isNationBackOpen
	if not isNationBackOpen: return
	
	global NationBackDict
	if not NationBackDict.returnDB: return
	
	role.SendObj(NationBackData, NationBackDict.get(role.GetRoleID(), {}))
	

		
#===============================================================================
# 神石回赠充值阶段
#===============================================================================
def OpenNationBack(role, param):
	if param != CircularDefine.CA_NationBack:
		return
	
	global isNationBackOpen
	if isNationBackOpen:
		print "GE_EXC, isNationBackOpen is already open"
	isNationBackOpen = True
	
	#持久化字典没有载回, 载回的时候会计算一次begin_days
	global NationBackDict
	if not NationBackDict.returnDB: return
	
	#如果持久化数据先载回来了, 但是活动还没有开这里begin_days==0, 所以修正一下begin_days
	for activeId, (activeType, _) in CircularActive.CircularActiveCache_Dict.iteritems():
		if activeType != param:
			continue
		nationId = activeId
		break
	else:
		print 'GE_EXC, nationback can not find activeId in open event'
		return
	cfg = CircularActive.CircularActiveConfig_Dict.get(nationId)
	if not cfg:
		print 'GE_EXC, nationback can not find activeId in CircularActiveConfig_Dict' % nationId
		return
	NationBackDict['begin_days'] = cDateTime.Days() - (datetime.datetime(cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second()) - datetime.datetime(*cfg.startDate)).days
	NationBackDict.changeFlag = True
	
def CloseNationBack(role, param):
	if param != CircularDefine.CA_NationBack:
		return
	
	global isNationBackOpen
	if not isNationBackOpen:
		print "GE_EXC, isNationBackOpen is already close"
	isNationBackOpen = False
	
	#活动结束的时候清理
	global NationBackDict
	NationBackDict.clear()
	
def AfterChangeUnbindRMB_Q(role, param):
	global isNationBackOpen
	if not isNationBackOpen: return
	
	oldValue, newValue = param
	if newValue < oldValue: return
	
	global NationBackDict
	if not NationBackDict.returnDB: return
	
	beginDays = NationBackDict.get('begin_days')
	if not beginDays:
		return
	pastDays = cDateTime.Days() - beginDays + 1
	if pastDays > ActiveLastTime():
		return
	
	roleId = role.GetRoleID()
	
	if roleId not in NationBackDict:
		NationBackDict[roleId] = {pastDays : [newValue - oldValue, 0, 0, ReturnTotalExp(role)]}
	else:
		if pastDays in NationBackDict[roleId]:
			NationBackDict[roleId][pastDays][0] += newValue - oldValue
		else:
			NationBackDict[roleId][pastDays] = [newValue - oldValue, 0, 0, 0, ReturnTotalExp(role)]
	NationBackDict.changeFlag = True
	
def RoleDayClear(role, param):
	global isNationBackOpen
	if not isNationBackOpen: return
	
	global NationBackDict
	if not NationBackDict.returnDB:
		#数据没有载回来, 记录玩家ID
		global needResetRoleIdSet
		needResetRoleIdSet.add(role.GetRoleID())
		return
	
	beginDays = NationBackDict.get('begin_days')
	if not beginDays:
		return
	pastDays = cDateTime.Days() - beginDays + 1
	if pastDays > ActiveLastTime():
		return
	roleId = role.GetRoleID()
	if roleId not in NationBackDict:
		#初始化今天的数据
		NationBackDict[roleId] = {pastDays : [0, 0, 0, ReturnTotalExp(role)]}
	else:
		newExp = ReturnTotalExp(role)
		nationBackData = NationBackDict[roleId]
		if pastDays - 1 in nationBackData:
			#如果昨天有数据的话, 计算一下昨天获得的经验值
			oldExp = nationBackData[pastDays - 1][3]
			if oldExp:
				nationBackData[pastDays - 1][1] = newExp - oldExp
		#初始化今天的数据
		nationBackData[pastDays] = [0, 0, 0, newExp]
		NationBackDict[roleId] = nationBackData
	NationBackDict.changeFlag = True
	
def ReturnTotalExp(role):
	#返回当前的总经验值
	level = role.GetLevel()
	totalExp = 0
	RLG = RoleConfig.LevelExp_Dict.get
	for l in xrange(1, level):
		maxExp = RLG(l)
		if not maxExp:
			break
		totalExp += maxExp
	return totalExp + role.GetExp()

def BeforeExit(role, param):
	global isNationBackOpen
	if not isNationBackOpen: return
	
	global NationBackDict
	if not NationBackDict.returnDB: return
	
	beginDays = NationBackDict.get('begin_days')
	if not beginDays:
		return
	pastDays = cDateTime.Days() - beginDays + 1
	if pastDays > ActiveLastTime():
		return
	roleId = role.GetRoleID()
	if roleId not in NationBackDict:
		return
	nationBackData = NationBackDict[roleId]
	#这里可能在跨天的dayclear还没有调用的时候调用, 不处理
	if pastDays not in nationBackData:
		return
	oldExp = nationBackData[pastDays][3]
	if not oldExp:
		return
	#离开的时候计算一下今天已获得的总经验值
	nationBackData[pastDays][1] = ReturnTotalExp(role) - oldExp
	NationBackDict[roleId] = nationBackData
	NationBackDict.changeFlag = True
	
def AfterLogin(role, param):
	global isNationBackOpen
	if not isNationBackOpen: return
	
	global NationBackDict
	if not NationBackDict.returnDB:
		#数据还没有载回, 记录玩家ID
		global needResetRoleIdSet
		needResetRoleIdSet.add(role.GetRoleID())
		return
	
	beginDays = NationBackDict.get('begin_days')
	if not beginDays:
		return
	pastDays = cDateTime.Days() - beginDays + 1
	if pastDays > ActiveLastTime():
		return
	roleId = role.GetRoleID()
	if roleId not in NationBackDict:
		NationBackDict[roleId] = {pastDays : [0, 0, 0, ReturnTotalExp(role)]}
	elif pastDays not in NationBackDict[roleId]:
		NationBackDict[roleId][pastDays] = [0, 0, 0, ReturnTotalExp(role)]
	NationBackDict.changeFlag = True
#===============================================================================
# 处理
#===============================================================================
def AfterLoad():
	global isNationBackOpen, NationBackDict
	if not isNationBackOpen:
		#活动没有开启
		NationBackDict['begin_days'] = 0
		return
	
	#活动开启了之后持久化数据才载回来, 这里需要计算一下begin_days
	for activeId, (activeType, _) in CircularActive.CircularActiveCache_Dict.iteritems():
		if activeType != CircularDefine.CA_NationBack:
			continue
		nationId = activeId
		break
	else:
		print 'GE_EXC, nationback can not find activeId in AfterLoad'
		return
	cfg = CircularActive.CircularActiveConfig_Dict.get(nationId)
	if not cfg:
		print 'GE_EXC, nationback can not find activeId in CircularActiveConfig_Dict AfterLoad' % nationId
		return
	NationBackDict['begin_days'] = beginDays = cDateTime.Days() - (datetime.datetime(cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second()) - datetime.datetime(*cfg.startDate)).days
	NationBackDict.changeFlag = True
	
	#这里可能有玩家在持久化数据没有载回来的情况下登录, 所以在持久化数据载回时初始化一下玩家经验值
	global needResetRoleIdSet
	if not needResetRoleIdSet: return
	
	pastDays = cDateTime.Days() - beginDays + 1
	if pastDays > ActiveLastTime():
		return
	
	CFR = cRoleMgr.FindRoleByRoleID
	for roleId in needResetRoleIdSet:
		role = CFR(roleId)
		if not role:
			#不在线的不管了, 等下次上线的时候再初始化
			continue
		if roleId not in NationBackDict:
			#之前不在字典里
			NationBackDict[roleId] = {pastDays : [0, 0, 0, ReturnTotalExp(role)]}
		elif pastDays not in NationBackDict[roleId]:
			#之前在这个字典里, 但是今天的数据还没有
			NationBackDict[roleId][pastDays] = [0, 0, 0, ReturnTotalExp(role)]
	NationBackDict.changeFlag = True
	#清理
	needResetRoleIdSet = set()
	
if "_HasLoad" not in dir():
	if (Environment.HasLogic or Environment.HasWeb) and (not Environment.EnvIsNA()):
		#{'begin_days':活动开启时的unix天数, roleId:{活动开启的天数:[当前天数充值神石数, 当前天数获得经验, 是否领取奖励, 当天开始时的经验]}}
		NationBackDict = Contain.Dict("NationBackDict", (2038, 1, 1), AfterLoad)
		
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, OpenNationBack)
		Event.RegEvent(Event.Eve_EndCircularActive, CloseNationBack)
		
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		Event.RegEvent(Event.Eve_BeforeExit, BeforeExit)
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		
		#改变Q点神石
		Event.RegEvent(Event.AfterChangeUnbindRMB_Q, AfterChangeUnbindRMB_Q)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NationBack_Award", "请求领取节日有礼回赠"), RequestNationBack)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NationBack_Open", "请求打开节日有礼回赠"), RequestOpenNationBack)
		
