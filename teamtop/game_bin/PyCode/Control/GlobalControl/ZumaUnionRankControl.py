#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Control.GlobalControl.ZumaUnionRankControl")
#===============================================================================
# 祖玛公会排行榜控制模块
#===============================================================================

import cComplexServer
import cDateTime
import Environment
from Common.Message import PyMessage
from Common.Other import GlobalDataDefine
from ComplexServer.API import GlobalHttp
from ComplexServer.Plug.Control import ControlProxy
from Control import ProcessMgr

if "_HasLoad" not in dir():
	RETURN_DB = False						#数据载入是否成功
	
	#总逻辑进程数量
	TOTAL_LOGIC_CNT = 0
	
	LOGIC_ZUMA_UNION_RANK_DICT = {}		#逻辑进程祖玛公会榜缓存数据{服务器ID --> [[累计消耗神石, 玩家ID, 玩家名, 等级, 服务器名]]}
	
	ZUMA_UNION_TODAY_RANK_CACHE = []		#今日祖玛公会榜缓存（用于全逻辑服排行榜排序）
	ZUMA_UNION_YESTERDAY_RANK_CACHE = []	#昨日祖玛公会榜缓存（用于全逻辑服排行榜排序）
	
#===============================================================================
# 
#===============================================================================
def InitGetRankEx():
	#向数据库请求载入排行榜数据
	todayKey = GlobalDataDefine.ZumaUnionTodayRankKey
	yesterdayKey = GlobalDataDefine.ZumaUnionYesterdayRankKey
	GlobalHttp.GetGlobalDataByKeys([todayKey, yesterdayKey], OnGetZumaUnionRankBack, (todayKey, yesterdayKey))
	
def OnGetZumaUnionRankBack(response, regparam):
	#数据返回了
	if response is None:
		#自返回
		return
	
	todayKey, yesterdayKey = regparam
	
	#分析和处理数据
	datadict = response
	Checkdata(datadict, cDateTime.Days(), todayKey, yesterdayKey)
	
	global RETURN_DB
	RETURN_DB = True
	
	#同步数据给所有的逻辑进程
	SyncAllLogic()
	
def Checkdata(datadict, nowdays, nowKey, oldKey):
	#检查和分析数据库返回的数据
	nowRank = []
	oldRank = []
	data = datadict.get(nowKey)
	olddata = datadict.get(oldKey)
	
	if data:
		d, rankdata = data
		if d == nowdays:
			#确定是今天的数据
			nowRank = rankdata
		elif d > nowdays:
			#天数有问题
			if not Environment.IsDevelop:
				print "GE_EXC, day error in OnGetRankBack"
			return
		elif d == nowdays - 1:
			#昨天的数据？
			oldRank = rankdata
			#数据库里面的数据有点旧了，更新一下
			GlobalHttp.SetGlobalData(nowKey, (nowdays, []))
			GlobalHttp.SetGlobalData(oldKey, (nowdays - 1, oldRank))
			#设置当前缓存数据
			SetRankData([], oldRank)
			return
		else:
			# 已经相差2天了，清理数据?
			GlobalHttp.SetGlobalData(nowKey, (nowdays, []))
			GlobalHttp.SetGlobalData(oldKey, (nowdays - 1, []))
			return
	
	if olddata:
		oldday, oldrankdata = olddata
		if oldday == nowdays - 1:
			#天数准确
			oldRank = oldrankdata
		elif oldday >= nowdays:
			if not Environment.IsDevelop:
				print "GE_EXC, old day error in OnGetRankBack"
		else:
			#旧数据太旧了，直接清理
			GlobalHttp.SetGlobalData(oldKey, (nowdays - 1, []))
	
	SetRankData(nowRank, oldRank)
	
def SetRankData(nowRank, oldRank):
	#设置缓存数据
	global ZUMA_UNION_TODAY_RANK_CACHE
	global ZUMA_UNION_YESTERDAY_RANK_CACHE
	
	#重新排序, 先排充值, 再排角色ID
	nowRank.sort(key = lambda it:(it[0], it[1]), reverse = True)
	oldRank.sort(key = lambda it:(it[0], it[1]), reverse = True)
	
	ZUMA_UNION_TODAY_RANK_CACHE = nowRank
	ZUMA_UNION_YESTERDAY_RANK_CACHE = oldRank

def RequestLogicRank():
	#向所有的逻辑进程获取排行榜数据
	global TOTAL_LOGIC_CNT
	TOTAL_LOGIC_CNT = len(ProcessMgr.ControlProcesssSessions)
	for sessionid, cp in ProcessMgr.ControlProcesssSessions.iteritems():
		if cp.processid >= 30000:
			#跨服服务器不处理
			TOTAL_LOGIC_CNT -= 1
			continue
		ControlProxy.SendLogicMsgAndBack(sessionid, PyMessage.Control_RequestLogicZumaUnionRank, None, LogicBackRank, sessionid)
	
def LogicBackRank(callargv, regparam):
	#逻辑进程返回或者自返回
	global TOTAL_LOGIC_CNT
	TOTAL_LOGIC_CNT -= 1
	
	if callargv:
		global LOGIC_ZUMA_UNION_RANK_DICT
		processId, logicZumaUnionRankList = callargv
		LOGIC_ZUMA_UNION_RANK_DICT[processId] = logicZumaUnionRankList
		
	if TOTAL_LOGIC_CNT == 0:
		#所有的逻辑进程已经返回了排行榜,对排行榜进行排序,然后更新到数据库
		SortAndUpdateRank()
	elif TOTAL_LOGIC_CNT < 0:
		print "GE_EXC, error in ZumaUnionRankControl RequestBack (%s)" % TOTAL_LOGIC_CNT
	
def SortAndUpdateRank():
	#更新数据库中的排行榜数据
	global ZUMA_UNION_TODAY_RANK_CACHE
	ZUMA_UNION_TODAY_RANK_CACHE = []
	
	for l in LOGIC_ZUMA_UNION_RANK_DICT.itervalues():
		ZUMA_UNION_TODAY_RANK_CACHE.extend(l)
	
	if ZUMA_UNION_TODAY_RANK_CACHE:
		#先排累计消耗神石, 再排角色ID
		ZUMA_UNION_TODAY_RANK_CACHE.sort(key = lambda it:(it[0], it[1]), reverse = True)
		ZUMA_UNION_TODAY_RANK_CACHE = ZUMA_UNION_TODAY_RANK_CACHE[:100]
		GlobalHttp.SetGlobalData(GlobalDataDefine.ZumaUnionTodayRankKey, (cDateTime.Days(), ZUMA_UNION_TODAY_RANK_CACHE))
		
	#同步数据给所有的逻辑进程
	SyncAllLogicToday()
	
def SyncAllLogic():
	#同步最新的富豪榜给所有的逻辑进程
	for processId in LOGIC_ZUMA_UNION_RANK_DICT.iterkeys():
		cp = ProcessMgr.ControlProcesssIds.get(processId)
		if not cp:
			if not Environment.IsDevelop:
				print "GE_EXC, ZumaUnionRankControl SyncAllLogic not process sessionid (%s)" % processId
			continue
		sessionid = cp.session_id
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdateZumaUnionRankToLogic, (ZUMA_UNION_TODAY_RANK_CACHE, ZUMA_UNION_YESTERDAY_RANK_CACHE))
	
def SyncAllLogicToday():
	#同步当天最新的排行榜给所有的逻辑进程
	global ZUMA_UNION_TODAY_RANK_CACHE
	for processId in LOGIC_ZUMA_UNION_RANK_DICT.iterkeys():
		cp = ProcessMgr.ControlProcesssIds.get(processId)
		if not cp:
			if not Environment.IsDevelop:
				print "GE_EXC, ZumaUnionRankControl SyncAllLoginToday not process sessionid (%s)" % processId
			continue
		sessionid = cp.session_id
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdateZumaUnionRankToLogic_T, ZUMA_UNION_TODAY_RANK_CACHE)

#===============================================================================
# 时间
#===============================================================================
def AfterNewHour():
	#每一个整点向所有的逻辑进程请求每一个服务器的前30名玩家数据，等待回调并且记录数据
	#如果有某些逻辑进程没有返回或者其他原因导致了这个回调是自回调的。这个时候，就会使用上一个小时
	#的旧数据代替这个一个服的数据。
	
	#所有的回调都完毕后，触发对这些玩家数据排序出前100名。并且http请求更新到数据库
	#（缺数据清理规则，数据中可能要存储天数的时间戳，清理天数 - 2 以后的数据 （因为是保存2天的数据））
	
	global RETURN_DB
	if RETURN_DB is False:
		print "GE_EXC, ZumaUnionRankControl AfterNewHour error not ReturnDB"
		#数据没有载回, 尝试再次载入
		InitGetRankEx()
		return
	
	#向逻辑进程请求数据,并且进行排序，写入数据库，把最新的排序更新到逻辑进程
	RequestLogicRank()
	
	nowHour = cDateTime.Hour()
	if nowHour == 0:
		#活动结束后10分钟发奖
		cComplexServer.RegTick(10 * 60, ZumaUnionRankReward)
		
def ZumaUnionRankReward(callArgv, regparam):
	global ZUMA_UNION_TODAY_RANK_CACHE
	global ZUMA_UNION_YESTERDAY_RANK_CACHE
	#同步最新的祖玛公会排行榜给所有的逻辑进程并通知发奖励
	for processId in LOGIC_ZUMA_UNION_RANK_DICT.iterkeys():
		cp = ProcessMgr.ControlProcesssIds.get(processId)
		if not cp:
			if not Environment.IsDevelop:
				print "GE_EXC, ZumaUnionRankControl ZumaUnionRankReward not process sessionid (%s)" % processId
			continue
		sessionid = cp.session_id
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_RequestLogicZumaUnionRankReward, ZUMA_UNION_TODAY_RANK_CACHE)
	
	#处理排行榜
	ZUMA_UNION_YESTERDAY_RANK_CACHE = ZUMA_UNION_TODAY_RANK_CACHE
	ZUMA_UNION_TODAY_RANK_CACHE = []
	
#===============================================================================
# 逻辑服请求
#===============================================================================
def LogicRequestZumaUnionRank(sessionid, msg):
	'''
	#逻辑进程主动请求祖玛公会榜数据
	@param sessionid:
	@param msg:(进程ID， 积分排行榜)
	'''
	global LOGIC_ZUMA_UNION_RANK_DICT
	#先记录逻辑进程的区域类型
	processId, rank = msg
	LOGIC_ZUMA_UNION_RANK_DICT[processId] =  rank
	
	if not RETURN_DB:
		#控制进程当前还没有从DB载回数据，等待数据载回来再发过去
		return
	
	ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdateZumaUnionRankToLogic, (ZUMA_UNION_TODAY_RANK_CACHE, ZUMA_UNION_YESTERDAY_RANK_CACHE))


if "_HasLoad" not in dir():
	if Environment.HasControl:
		InitGetRankEx()
		cComplexServer.RegAfterNewHourCallFunction(AfterNewHour)
		cComplexServer.RegDistribute(PyMessage.Control_RequestControlZumaUnionRank, LogicRequestZumaUnionRank)
		
		