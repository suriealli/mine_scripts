#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Control.GlobalControl.HaoqiControl")
#===============================================================================
# 豪气冲天控制模块
#===============================================================================
import time
import datetime
import cDateTime
import cComplexServer
import DynamicPath
import Environment
from Util.File import TabFile
from Common.Message import PyMessage
from Common.Other import GlobalDataDefine, GlobalPrompt
from Control import ProcessMgr
from ComplexServer.Plug.Control import ControlProxy
from ComplexServer.API import GlobalHttp
from ComplexServer.Log import AutoLog
from Game.Role.Mail import EnumMail

if "_HasLoad" not in dir():
	TotalLogicCnt = 0						#总共的逻辑进程
	ReturnDB = False						#数据载入是否成功
	HaoqiIsOpen = False						#活动是否开启
	
	HaoqiRankCache = []						#今日排行榜数据
	HaoqiRankCacheOld = []					#昨日排行榜数据
	
	LoginRank_Dict = {}						#逻辑进程排行榜缓存数据{服务器ID --> [[充值, 玩家ID, 玩家名, 服务器名]]}
	
	HaoqiRank_Dict = {}						#豪气冲天排行榜奖励字典
	
	CFILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	CFILE_FOLDER_PATH.AppendPath("CircularActive")
	
	HQFILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	HQFILE_FOLDER_PATH.AppendPath("Haoqi")
#===============================================================================
# 配置
#===============================================================================
class HaoqiActiveConfig(TabFile.TabLine):
	FilePath = CFILE_FOLDER_PATH.FilePath("HaoqiActive.txt")
	def __init__(self):
		self.beginTime = eval				#开始时间
		self.endTime = eval					#结束时间
	
	def Active(self):
		#当前时间
		nowDate = (cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second())
		#开始时间戳
		beginTime = int(time.mktime(datetime.datetime(*self.beginTime).timetuple()))
		#结束时间戳
		endTime = int(time.mktime(datetime.datetime(*self.endTime).timetuple()))
		#当前时间戳
		nowTime = int(time.mktime(datetime.datetime(cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second()).timetuple()))
		
		#晚一分钟结束
		if self.beginTime <= nowDate < self.endTime:
			#在开始和结束时间戳之间, 激活
			OpenHaoqi(None, None)
			cComplexServer.RegTick(endTime - nowTime + 60, CloseHaoqi)
		elif nowDate < self.beginTime:
			#在开始时间戳之前
			cComplexServer.RegTick(beginTime - nowTime, OpenHaoqi)
			cComplexServer.RegTick(endTime - nowTime + 60, CloseHaoqi)
		
def LoadHaoqiActiveConfig():
	for cfg in HaoqiActiveConfig.ToClassType(False):
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in HaoqiActive"
			return
		#不需要依赖什么, 在起服的时候就可以触发了
		cfg.Active()
	
class HaoqiRankConfig(TabFile.TabLine):
	FilePath = HQFILE_FOLDER_PATH.FilePath("HaoqiRank.txt")
	def __init__(self):
		self.rank = int							#排名
		self.rewardItems = eval
		self.money = int
		self.bindRMB = int
	
def LoadHaoqiRankConfig():
	global HaoqiRank_Dict
	
	for HRC in HaoqiRankConfig.ToClassType(False):
		if HRC.rank in HaoqiRank_Dict:
			print "GE_EXC, repeat rank : %s in HaoqiRank_Dict" % HRC.rank
			continue
		HaoqiRank_Dict[HRC.rank] = HRC
#===============================================================================
# 活动开关
#===============================================================================
def OpenHaoqi(callArgv, regparam):
	global HaoqiIsOpen
	if HaoqiIsOpen:
		print "GE_EXC, Haoqi is already open"
		return
	HaoqiIsOpen = True

def CloseHaoqi(callArgv, regparam):
	global HaoqiIsOpen
	if not HaoqiIsOpen:
		print "GE_EXC, Haoqi is already close"
		return
	HaoqiIsOpen = False
	
	#活动关闭时清理
	global HaoqiRankCache, HaoqiRankCacheOld, LoginRank_Dict
	HaoqiRankCache = []
	HaoqiRankCacheOld = []
	LoginRank_Dict = {}

def AfterNewMinute():
	#每一个整点向所有的逻辑进程请求每一个服务器的前10名玩家数据，等待回调并且记录数据
	#如果有某些逻辑进程没有返回或者其他原因导致了这个回调是自回调的。这个时候，就会使用上一个小时
	#的旧数据代替这个一个服的数据。
	
	#所有的回调都完毕后，触发对这些玩家数据排序出前100名。并且http请求更新到数据库
	#（缺数据清理规则，数据中可能要存储天数的时间戳，清理天数 - 2 以后的数据 （因为是保存2天的数据））
	
	global HaoqiIsOpen
	if not HaoqiIsOpen: return
	
	nowMinute = cDateTime.Minute()
	nowHour = cDateTime.Hour()
	
	if nowMinute not in (0, 30, 58):
		#0, 30, 58这三个时间点可能触发向逻辑进程请求数据
		return
	if nowMinute == 58 and nowHour != 23:
		#58分的时候只有是23点才会向逻辑进程请求数据
		return
	
	global ReturnDB
	if ReturnDB is False:
		print "GE_EXC, HaoqiControl AfterNewHour error not ReturnDB"
		#数据没有载回, 尝试再次载入
		InitGetHaoqiRank()
		return
	
	if nowHour == 0 and nowMinute == 0:
		#0点0分的时候只发奖，操作数据库数据，逻辑进程自己把今天的数据拷贝到“昨天”的数据里面
		NewDayRewardRoles()
	else:
		#向逻辑进程请求数据,并且进行排序，写入数据库，把最新的排序更新到逻辑进程
		RequestLogicRank()
	
def RequestLogicRank():
	#向所有的逻辑进程获取排行榜数据
	global TotalLogicCnt
	TotalLogicCnt = len(ProcessMgr.ControlProcesssSessions)
	
	for sessionid, cp in ProcessMgr.ControlProcesssSessions.iteritems():
		if cp.processid >= 30000:
			#跨服服务器不处理
			TotalLogicCnt -= 1
			continue
		ControlProxy.SendLogicMsgAndBack(sessionid, PyMessage.Control_RequestLogicHaoqiRank, None, LogicBackRank, sessionid)

def LogicBackRank(callargv, regparam):
	#逻辑进程返回或者自返回
	global TotalLogicCnt
	TotalLogicCnt -= 1
	
	if callargv:
		global LoginRank_Dict
		processId, logicranklist = callargv
		LoginRank_Dict[processId] = logicranklist
		
	if TotalLogicCnt == 0:
		#所有的逻辑进程已经返回了排行榜,对排行榜进行排序,然后更新到数据库
		SortAndUpdataRank()
	elif TotalLogicCnt < 0:
		print "GE_EXC, error in HaoqiControl RequestBack (%s)" % TotalLogicCnt
	
def SortAndUpdataRank():
	#更新数据库中的排行榜数据
	global HaoqiRankCache
	HaoqiRankCache = []
	
	for l in LoginRank_Dict.values():
		HaoqiRankCache.extend(l)
	
	if HaoqiRankCache:
		#先排充值, 再排角色ID
		HaoqiRankCache.sort(key = lambda it:(it[0], it[1]), reverse = True)
		HaoqiRankCache = HaoqiRankCache[:100]
		GlobalHttp.SetGlobalData(GlobalDataDefine.HaoqiDataKey, (cDateTime.Days(), HaoqiRankCache))
		
	#同步数据给所有的逻辑进程(当天数据)
	SyncAllLoginToday()

def NewDayRewardRoles():
	#发邮件对排行榜上面的玩家发奖
	global LoginRank_Dict
	LoginRank_Dict =  {}
	
	global HaoqiRankCache, HaoqiRankCacheOld
	
	#替换昨天的跨服排行榜
	HaoqiRankCacheOld = HaoqiRankCache
	#清理今天的跨服排行榜
	HaoqiRankCache = []
	
	days = cDateTime.Days()
	
	#更新跨服数据到数据库中
	GlobalHttp.SetGlobalData(GlobalDataDefine.HaoqiOldDataKey, (days - 1, HaoqiRankCacheOld))
	
	GlobalHttp.SetGlobalData(GlobalDataDefine.HaoqiDataKey, (days, HaoqiRankCache))
	
	#邮件奖励
	transaction = AutoLog.traHaoqiMailReward
	
	maildatas = []
	for index, rd in enumerate(HaoqiRankCacheOld):
		rank = index + 1
		roleid = rd[1]
		rolemaildata = (roleid, GlobalPrompt.Haoqi_Title, GlobalPrompt.Haoqi_Sender, GlobalPrompt.Haoqi_Content % rank, transaction, GetHaoqiRankMailReward(rank))
		maildatas.append(rolemaildata)
	#发送邮件奖励
	GlobalHttp.SendRoleMail(maildatas)
	
def GetHaoqiRankMailReward(rank):
	#组合一个邮件奖励字典
	mailData = {}
	
	global HaoqiRank_Dict
	cfg = HaoqiRank_Dict.get(rank)
	if not cfg:
		print "GE_EXC, GetHaoqiRankMailReward can not find reward by rank (%s)" % rank
		return
	
	if cfg.rewardItems:
		mailData[EnumMail.EnumItemsKey] = cfg.rewardItems
	if cfg.money:
		mailData[EnumMail.EnumMonyKey] = cfg.money
	if cfg.bindRMB:
		mailData[EnumMail.EnumBindRMBKey] = cfg.bindRMB
	
	return mailData
###############################################################################
def InitGetHaoqiRank():
	#向数据库请求载入排行榜数据
	key = GlobalDataDefine.HaoqiDataKey
	oldkey = GlobalDataDefine.HaoqiOldDataKey
	GlobalHttp.GetGlobalDataByKeys([key, oldkey], OnGetHaoqiRankBack, (key, oldkey))
	
def OnGetHaoqiRankBack(response, regparam):
	#数据返回了
	if response is None:
		#自返回
		return
	
	key, oldkey = regparam
	
	#分析和处理数据
	datadict = response
	Checkdata(datadict, cDateTime.Days(), key, oldkey)
	
	global ReturnDB
	ReturnDB = True
	
	#同步数据给所有的逻辑进程
	SyncAllLogin()
	
def SetRankData(nowRank, oldRank):
	#设置缓存数据
	global HaoqiRankCache, HaoqiRankCacheOld
	
	#重新排序, 先排充值, 再排角色ID
	nowRank.sort(key = lambda it:(it[0], it[1]), reverse = True)
	oldRank.sort(key = lambda it:(it[0], it[1]), reverse = True)
	
	HaoqiRankCache = nowRank
	HaoqiRankCacheOld = oldRank
	
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

def SyncAllLogin():
	#同步数据给所有的逻辑进程(今天和昨天)
	global LoginRank_Dict, HaoqiRankCache, HaoqiRankCacheOld
	for processId in LoginRank_Dict.iterkeys():
		cp = ProcessMgr.ControlProcesssIds.get(processId)
		if not cp:
			if not Environment.IsDevelop:
				print "GE_EXC, SyncAllLogin not process sessionid (%s)" % processId
			continue
		ControlProxy.SendLogicMsg(cp.session_id, PyMessage.Control_UpdataHaoqiRankToLogic, (HaoqiRankCache, HaoqiRankCacheOld))

def SyncAllLoginToday():
	#同步当天最新的排行榜给所有的逻辑进程
	global LoginRank_Dict, HaoqiRankCache
	for processId in LoginRank_Dict.iterkeys():
		cp = ProcessMgr.ControlProcesssIds.get(processId)
		if not cp:
			if not Environment.IsDevelop:
				print "GE_EXC, SyncAllLoginToday not process sessionid (%s)" % processId
			continue
		sessionid = cp.session_id
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataHaoqiRankToLogic_T, HaoqiRankCache)

def LoginRequestHaoqiRank(sessionid, msg):
	'''
	#逻辑进程主动请求跨服排行榜数据
	@param sessionid:
	@param msg:(进程ID， 充值排行榜)
	'''
	global ReturnDB, LoginRank_Dict
	#先记录逻辑进程的区域类型
	processId, rank = msg
	LoginRank_Dict[processId] =  rank
	
	if not ReturnDB:
		#控制进程当前还没有从DB载回数据，等待数据载回来再发过去
		return
	
	global HaoqiRankCache, HaoqiRankCacheOld
	ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataHaoqiRankToLogic, (HaoqiRankCache, HaoqiRankCacheOld))

if "_HasLoad" not in dir():
	if Environment.HasControl:
		LoadHaoqiActiveConfig()
		LoadHaoqiRankConfig()
		
		InitGetHaoqiRank()
		cComplexServer.RegAfterNewMinuteCallFunction(AfterNewMinute)
		cComplexServer.RegDistribute(PyMessage.Control_GetHaoqiRank, LoginRequestHaoqiRank)
		
	