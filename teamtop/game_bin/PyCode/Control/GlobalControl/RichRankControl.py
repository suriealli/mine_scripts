#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Control.GlobalControl.RichRankControl")
#===============================================================================
# 双十二富豪榜控制模块
#===============================================================================
import time
import datetime
import cComplexServer
import cDateTime
import DynamicPath
import Environment
from Common.Message import PyMessage
from Common.Other import GlobalDataDefine
from ComplexServer.API import GlobalHttp
from ComplexServer.Plug.Control import ControlProxy
from Control import ProcessMgr
from Util.File import TabFile

if "_HasLoad" not in dir():
	CFILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	CFILE_FOLDER_PATH.AppendPath("CircularActive")
	
	IS_START = False						#活动是否开启
	RETURN_DB = False						#数据载入是否成功
	
	#总逻辑进程数量
	TOTAL_LOGIC_CNT = 0
	
	LOGIC_RICH_RANK_DICT = {}		#逻辑进程富豪榜缓存数据{服务器ID --> [[累计消耗神石, 玩家ID, 玩家名, 等级, 服务器名]]}
	
	RICH_RANK_CACHE = []			#富豪榜缓存（用于全逻辑服排行榜排序）
	
#===============================================================================
# 配置表
#===============================================================================
class RichRankActiveConfig(TabFile.TabLine):
	FilePath = CFILE_FOLDER_PATH.FilePath("RichRankActive.txt")
	def __init__(self):
		self.beginTime = eval				#开始时间
		self.endTime = eval					#结束时间
	
	def active(self):
		#当前时间
		nowDate = (cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second())
		#开始时间戳
		beginTime = int(time.mktime(datetime.datetime(*self.beginTime).timetuple()))
		#结束时间戳
		endTime = int(time.mktime(datetime.datetime(*self.endTime).timetuple()))
		#当前时间戳
		nowTime = int(time.mktime(datetime.datetime(cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second()).timetuple()))
		
		if self.beginTime <= nowDate < self.endTime:
			#在开始和结束时间戳之间, 激活
			OpenRichRank(None, None)
			cComplexServer.RegTick(endTime - nowTime + 60, CloseRichRank)
		elif nowDate < self.beginTime:
			#在开始时间戳之前
			cComplexServer.RegTick(beginTime - nowTime, OpenRichRank)
			cComplexServer.RegTick(endTime - nowTime + 60, CloseRichRank)

def LoadRichRankActiveConfig():
	for config in RichRankActiveConfig.ToClassType(False):
		if config.beginTime > config.endTime:
			print "GE_EXC, beginTime > endTime in RichRankActive"
			return
		#读取配置表的时候尝试激活活动
		config.active()
		
#===============================================================================
# 
#===============================================================================
def InitGetRankEx():
	#向数据库请求载入排行榜数据
	key = GlobalDataDefine.RichRankKey
	GlobalHttp.GetGlobalDataByKeys([key, ], OnGetRichRankBack, key)
	
def OnGetRichRankBack(response, regparam):
	#数据返回了
	if response is None:
		#自返回
		return
	
	key = regparam
	
	#分析和处理数据
	datadict = response
	Checkdata(datadict, cDateTime.Days(), key)
	
	global RETURN_DB
	RETURN_DB = True
	
	#同步数据给所有的逻辑进程
	SyncAllLogic()
	
def Checkdata(datadict, nowdays, key):
	#检查和分析数据库返回的数据
	rank = []
	data = datadict.get(key)

	if data:
		d, rankdata = data
		if d == nowdays:
			#确定是今天的数据
			rank = rankdata
			SetRankData(rank)
		elif d > nowdays:
			#天数有问题
			if not Environment.IsDevelop:
				print "GE_EXC, day error in OnGetRankBack in RichRankControl"
			return
		elif d == nowdays - 1:
			#数据库里面的数据有点旧了，更新一下
			GlobalHttp.SetGlobalData(key, (nowdays, []))
			#设置当前缓存数据
			SetRankData([])
			return
		else:
			# 已经相差2天了，清理数据?
			GlobalHttp.SetGlobalData(key, (nowdays, []))
			#设置当前缓存数据
			SetRankData([])
			return
	
def SetRankData(rank):
	#设置缓存数据
	global RICH_RANK_CACHE
	
	#重新排序, 先排充值, 再排角色ID
	rank.sort(key = lambda it:(it[0], it[1]), reverse = True)
	
	RICH_RANK_CACHE = rank

def RequestLogicRank():
	#向所有的逻辑进程获取排行榜数据
	global TOTAL_LOGIC_CNT
	TOTAL_LOGIC_CNT = len(ProcessMgr.ControlProcesssSessions)
	for sessionid, cp in ProcessMgr.ControlProcesssSessions.iteritems():
		if cp.processid >= 30000:
			#跨服服务器不处理
			TOTAL_LOGIC_CNT -= 1
			continue
		ControlProxy.SendLogicMsgAndBack(sessionid, PyMessage.Control_RequestLogicRichRank, None, LogicBackRank, sessionid)
	
def LogicBackRank(callargv, regparam):
	#逻辑进程返回或者自返回
	global TOTAL_LOGIC_CNT
	TOTAL_LOGIC_CNT -= 1
	
	if callargv:
		global LOGIC_RICH_RANK_DICT
		processId, logicRichRankList = callargv
		LOGIC_RICH_RANK_DICT[processId] = logicRichRankList
		
	if TOTAL_LOGIC_CNT == 0:
		#所有的逻辑进程已经返回了排行榜,对排行榜进行排序,然后更新到数据库
		SortAndUpdateRank()
	elif TOTAL_LOGIC_CNT < 0:
		print "GE_EXC, error in RichRankControl RequestBack (%s)" % TOTAL_LOGIC_CNT
	
def SortAndUpdateRank():
	#更新数据库中的排行榜数据
	global RICH_RANK_CACHE
	RICH_RANK_CACHE = []
	
	for l in LOGIC_RICH_RANK_DICT.itervalues():
		RICH_RANK_CACHE.extend(l)
	
	if RICH_RANK_CACHE:
		#先排累计消耗神石, 再排角色ID
		RICH_RANK_CACHE.sort(key = lambda it:(it[0], it[1]), reverse = True)
		RICH_RANK_CACHE = RICH_RANK_CACHE[:100]
		GlobalHttp.SetGlobalData(GlobalDataDefine.RichRankKey, (cDateTime.Days(), RICH_RANK_CACHE))
		
	#同步数据给所有的逻辑进程
	SyncAllLogic()
	
def SyncAllLogic():
	#同步最新的富豪榜给所有的逻辑进程
	for processId in LOGIC_RICH_RANK_DICT.iterkeys():
		cp = ProcessMgr.ControlProcesssIds.get(processId)
		if not cp:
			if not Environment.IsDevelop:
				print "GE_EXC, RichRankControl SyncAllLogic not process sessionid (%s)" % processId
			continue
		sessionid = cp.session_id
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdateLogicRichRank, RICH_RANK_CACHE)
	
#===============================================================================
# tick
#===============================================================================
def OpenRichRank(callArgv, regparam):
	#开启双十二富豪榜
	global IS_START
	if IS_START is True:
		print "GE_EXC, RichRank is already open"
		return
	IS_START = True
	
	#活动开启清空
	global LOGIC_RICH_RANK_DICT
	global RICH_RANK_CACHE
	LOGIC_RICH_RANK_DICT = {}
	RICH_RANK_CACHE = []

def CloseRichRank(callArgv, regparam):
	#结束双十二富豪榜
	global IS_START
	if not IS_START:
		print "GE_EXC, RichRank is already close"
		return
	IS_START = False
	
	#向逻辑进程请求数据,并且进行排序，写入数据库，把最新的排序更新到逻辑进程
	RequestLogicRank()
	
	#活动结束后10分钟发奖
	cComplexServer.RegTick(10 * 60, RichRankReward)
	
def RichRankReward(callArgv, regparam):
	#同步最新的富豪榜给所有的逻辑进程并通知发奖励
	for processId in LOGIC_RICH_RANK_DICT.iterkeys():
		cp = ProcessMgr.ControlProcesssIds.get(processId)
		if not cp:
			if not Environment.IsDevelop:
				print "GE_EXC, RichRankControl RichRankReward not process sessionid (%s)" % processId
			continue
		sessionid = cp.session_id
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_RequestLogicRichRankReward, RICH_RANK_CACHE)

#===============================================================================
# 时间
#===============================================================================
def AfterNewHour():
	#每一个整点向所有的逻辑进程请求每一个服务器的前30名玩家数据，等待回调并且记录数据
	#如果有某些逻辑进程没有返回或者其他原因导致了这个回调是自回调的。这个时候，就会使用上一个小时
	#的旧数据代替这个一个服的数据。
	
	#所有的回调都完毕后，触发对这些玩家数据排序出前100名。并且http请求更新到数据库
	#（缺数据清理规则，数据中可能要存储天数的时间戳，清理天数 - 2 以后的数据 （因为是保存2天的数据））
	if IS_START is False:
		#活动没有开启
		return
	
	#nowHour = cDateTime.Hour()
	global RETURN_DB
	if RETURN_DB is False:
		print "GE_EXC, RichRankControl AfterNewHour error not ReturnDB"
		#数据没有载回, 尝试再次载入
		InitGetRankEx()
		return

	#向逻辑进程请求数据,并且进行排序，写入数据库，把最新的排序更新到逻辑进程
	RequestLogicRank()
		
#===============================================================================
# 逻辑服请求
#===============================================================================
def LogicRequestRichRank(sessionid, msg):
	'''
	#逻辑进程主动请求富豪榜数据
	@param sessionid:
	@param msg:(进程ID， 富豪榜)
	'''
	global RETURN_DB, LOGIC_RICH_RANK_DICT
	#先记录逻辑进程的区域类型
	processId, rank = msg
	LOGIC_RICH_RANK_DICT[processId] =  rank
	
	if not RETURN_DB:
		#控制进程当前还没有从DB载回数据，等待数据载回来再发过去
		return
	
	global RICH_RANK_CACHE
	ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdateLogicRichRank, RICH_RANK_CACHE)


if "_HasLoad" not in dir():
	if Environment.HasControl:
		LoadRichRankActiveConfig()
		InitGetRankEx()
		cComplexServer.RegAfterNewHourCallFunction(AfterNewHour)
		cComplexServer.RegDistribute(PyMessage.Control_RequestControlRichRank, LogicRequestRichRank)
		
		