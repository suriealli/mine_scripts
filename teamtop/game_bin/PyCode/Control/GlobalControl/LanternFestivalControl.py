#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Control.GlobalControl.LanternFestivalControl")
#===============================================================================
# 元宵节积分跨服排行控制模块
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
	IsStart = False					#活动开启关闭标志
	HttpDataReturn = False			#HTTP请求是否载回数据的标志
	
	TotalLogicCnt = 0				#逻辑进程总数
	
	LogicRankDict = {}				#processType-->processId-->ranklist
	LogicTypeDict = {}
	
	#数据载回是否成功
	ReturnSet = set()				#载回数据的服务器分区类型
	ReturnHttp = False				#数据是否全部载回
	
	
	RankCacheT_1 = []
	RankCacheT_2 = []
	RankCacheT_3 = []
	RankCacheT_4 = []
	RankCacheT_5 = []
	
	RankCacheY_1 = []
	RankCacheY_2 = []
	RankCacheY_3 = []
	RankCacheY_4 = []
	RankCacheY_5 = []
	
	CFILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	CFILE_FOLDER_PATH.AppendPath("CircularActive")
	
	LFILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	LFILE_FOLDER_PATH.AppendPath("LanternFestival")
	
	LanternRankConfigDict = {}		
#===============================================================================
# 配置
#===============================================================================
class LanternFestivalActiveConfig(TabFile.TabLine):
	FilePath = CFILE_FOLDER_PATH.FilePath("LanternFestivalActive.txt")
	def __init__(self):
		self.beginTime = eval				#开始时间
		self.endTime = eval					#结束时间
	
	def Active(self):
		#开始时间戳
		beginTime = int(time.mktime(datetime.datetime(*self.beginTime).timetuple()))
		#结束时间戳
		endTime = int(time.mktime(datetime.datetime(*self.endTime).timetuple()))
		#当前时间戳
		nowTime = cDateTime.Seconds()
		
		#控制进程晚一分钟结束
		if beginTime <= nowTime < endTime:
			#在开始和结束时间戳之间, 激活
			Start(None, None)
			cComplexServer.RegTick(endTime - nowTime + 60, End)
		elif nowTime < beginTime:
			#在开始时间戳之前
			cComplexServer.RegTick(beginTime - nowTime, Start)
			cComplexServer.RegTick(endTime - nowTime + 60, End)


def LoadLanternFestivalActiveConfig():
	for cfg in LanternFestivalActiveConfig.ToClassType(False):
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in LanternFestivalActive"
			return
		#不需要依赖什么, 在起服的时候就可以触发了
		cfg.Active()


class LanternRankConfig(TabFile.TabLine):
	FilePath = LFILE_FOLDER_PATH.FilePath("LanternCrossRank.txt")
	def __init__(self):
		self.rank = int							#排名
		self.serverType = int					#服务器类型
		self.needScore = int
		self.rewardItems = eval
		self.money = int
		self.bindRMB = int


def LoadLanternRankConfig():
	global LanternRankConfigDict
	for config in LanternRankConfig.ToClassType(False):
		if (config.rank, config.serverType) in LanternRankConfigDict:
			print "GE_EXC, repeat (rank,serverType)(%s,%s) in LanternRankConfigDict" % (config.rank, config.serverType)
		LanternRankConfigDict[(config.rank, config.serverType)] = config
		
#===============================================================================
# 活动开关
#===============================================================================
def Start(callArgv, regparam):
	global IsStart
	if IsStart:
		print "GE_EXC, LanternFestival is already open"
		return
	IsStart = True


def End(callArgv, regparam):
	global IsStart
	if not IsStart:
		print "GE_EXC, LanternFestival is already close"
		return
	IsStart = False


def RequestGetLogicRank():
	'''
	请求获取逻辑进程排行榜
	'''
	global TotalLogicCnt
	TotalLogicCnt = len(ProcessMgr.ControlProcesssSessions)
	
	for sessionid, cp in ProcessMgr.ControlProcesssSessions.iteritems():
		if cp.processid >= 30000:
			#进程id大于30000的为跨服进程
			TotalLogicCnt -= 1 
			continue
		ControlProxy.SendLogicMsgAndBack(sessionid, PyMessage.Control_RequestLogicLanternRank, None, CallBackLogicRank, TotalLogicCnt)
	

def CallBackLogicRank(callargv, regparam):
	'''
	请求获取逻辑进程排行榜回调函数
	'''
	global TotalLogicCnt
	TotalLogicCnt -= 1
	
	if callargv:
		processId, serverType, logicranklist = callargv
		rankDict = LogicRankDict.setdefault(serverType, {})
		global LogicTypeDict
		LogicTypeDict.setdefault(processId, serverType)
		rankDict[processId] = logicranklist
		
	if TotalLogicCnt == 0:
		#所有的逻辑进程已经返回了排行榜,对排行榜进行排序,然后更新到数据库
		RecountCrossRank()

	elif TotalLogicCnt < 0:
		print "GE_EXC, error in LanternFestivalControl RequestBack (%s)" % TotalLogicCnt
	

def RecountCrossRank():
	'''
	重算跨服排行榜
	'''
	globalDict = globals()
	days = cDateTime.Days()
	for pType, rankDict in LogicRankDict.iteritems():
		cacheName = 'RankCacheT_%s' % pType
		if cacheName not in globalDict:
			continue
		RankCacheT = globalDict[cacheName] = []
		
		for l in rankDict.itervalues():
			RankCacheT.extend(l)
		
		if RankCacheT:
			RankCacheT.sort(key=lambda it:it[:3], reverse=True)
			globalDict[cacheName] = RankCacheT = RankCacheT[:100]
			attrName = 'LanternFestivalRank_%s' % pType
			if not hasattr(GlobalDataDefine, attrName):
				print "GE_EXC, not hasattr(GlobalDataDefine, %s)" % attrName
				continue
			GlobalHttp.SetGlobalData(getattr(GlobalDataDefine, attrName), (days, RankCacheT))
	
	SyncAllLogicRankToday()
		

def SyncAllLogicRankToday():
	'''
	同步当天最新的排行榜给所有的逻辑进程
	'''
	globalDict = globals()
	for processId, pType in LogicTypeDict.iteritems():
		cp = ProcessMgr.ControlProcesssIds.get(processId)
		if not cp:
			if not Environment.IsDevelop:
				print "GE_EXC, SyncAllLogicRankToday not process sessionid (%s)" % processId
			continue
		sessionid = cp.session_id
		
		cacheName = "RankCacheT_%s" % pType
		if cacheName not in globalDict:
			print "GE_EXC, SyncAllLogicRankToday error pType (%s)" % pType
			continue
		RankCacheT = globalDict[cacheName]
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdateLanternRankToLogic_T, RankCacheT)


def OnLogicRequestCrossRank(sessionid, msg):
	'''
	逻辑进程请求获取跨服排行榜
	'''
	processId, pType, rank = msg
	global LogicRankDict, LogicTypeDict
	LogicRankDict.setdefault(pType, {})[processId] = rank
	LogicTypeDict.setdefault(processId, pType)
	
	listNameT = 'RankCacheT_%s' % pType
	listNameY = 'RankCacheY_%s' % pType
	
	globalDict = globals()
	if listNameT not in globalDict or listNameY not in globalDict:
		print "GE_EXC, error pType (%s) in OnLogicRequestCrossRank" % pType
		return
	
	rankCacheT = globalDict[listNameT]
	rankCacheY = globalDict[listNameY]
	
	ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdateLanternRankToLogic, (rankCacheT, rankCacheY))


def AfterNewMinute():
	#每一个整点向所有的逻辑进程请求每一个服务器的前100名玩家数据，等待回调并且记录数据
	#如果有某些逻辑进程没有返回或者其他原因导致了这个回调是自回调的。这个时候，就会使用上一个小时
	#的旧数据代替这个一个服的数据。
	
	#所有的回调都完毕后，触发对这些玩家数据排序出前100名。并且http请求更新到数据库
	#（缺数据清理规则，数据中可能要存储天数的时间戳，清理天数 - 2 以后的数据 （因为是保存2天的数据））
	
	if IsStart is False:
		return
	
	nowMinute = cDateTime.Minute()
	nowHour = cDateTime.Hour()
	
	if nowMinute not in (0, 30, 58):
		#0, 30, 58这三个时间点可能触发向逻辑进程请求数据
		return
	if nowMinute == 58 and nowHour != 23:
		#58分的时候只有是23点才会向逻辑进程请求数据
		return
	

	if HttpDataReturn is False:
		print "GE_EXC, LanternFestivalControl AfterNewHour error not HttpDataReturn"
		#数据没有载回, 尝试再次载入
		LoadCrossRankHttp()
		return
	
	if nowHour == 0 and nowMinute == 0:
		#0点0分的时候只发奖，操作数据库数据，逻辑进程自己把今天的数据拷贝到“昨天”的数据里面
		NewDayRewardRoles()
	else:
		#向逻辑进程请求数据,并且进行排序，写入数据库，把最新的排序更新到逻辑进程
		RequestGetLogicRank()


def LoadCrossRankHttp():
	'''
	起服时通过http载回之前记录的跨服排行数据
	'''
	pType_1 = 1
	key_1 = GlobalDataDefine.LanternFestivalRank_1
	oldKey_1 = GlobalDataDefine.LanternFestivalRankOld_1
	GlobalHttp.GetGlobalDataByKeys([key_1, oldKey_1], OnGetRankBackHttp, (pType_1, key_1, oldKey_1))
	
	pType_2 = 2
	key_2 = GlobalDataDefine.LanternFestivalRank_2
	oldKey_2 = GlobalDataDefine.LanternFestivalRankOld_2
	GlobalHttp.GetGlobalDataByKeys([key_2, oldKey_2], OnGetRankBackHttp, (pType_2, key_2, oldKey_2))
	
	pType_3 = 3
	key_3 = GlobalDataDefine.LanternFestivalRank_3
	oldKey_3 = GlobalDataDefine.LanternFestivalRankOld_3
	GlobalHttp.GetGlobalDataByKeys([key_3, oldKey_3], OnGetRankBackHttp, (pType_3, key_3, oldKey_3))
	
	pType_4 = 4
	key_4 = GlobalDataDefine.LanternFestivalRank_4
	oldKey_4 = GlobalDataDefine.LanternFestivalRankOld_4
	GlobalHttp.GetGlobalDataByKeys([key_4, oldKey_4], OnGetRankBackHttp, (pType_4, key_4, oldKey_4))
	
	pType_5 = 5
	key_5 = GlobalDataDefine.LanternFestivalRank_5
	oldKey_5 = GlobalDataDefine.LanternFestivalRankOld_5
	GlobalHttp.GetGlobalDataByKeys([key_5, oldKey_5], OnGetRankBackHttp, (pType_5, key_5, oldKey_5))
	

def OnGetRankBackHttp(response, regparam):
	'''
	http载回回调
	'''
	#超时
	if response is None:
		print 'GE_EXC, response is None'
		return
	
	dataDict = response
	pType, key, oldkey = regparam
	days = cDateTime.Days()
	CheckData(dataDict, pType, days, key, oldkey)
	
	global ReturnSet
	ReturnSet.add(pType)
	
	global HttpDataReturn

	if len(ReturnSet) >= 5:
		HttpDataReturn = True
		#同步数据给所有的逻辑进程
		SyncAllLogicRankToday()


def CheckData(datadict, pType, nowdays, nowKey, oldKey):
	'''
	检查和分析http返回的数据
	'''
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
			SetRankData(pType, [], oldRank)
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
			
	SetRankData(pType, nowRank, oldRank)


def SetRankData(pType, nowRank, oldRank):	
	globalDict = globals()
	cacheName = 'RankCacheT_%s' % pType
	oldCacheName = 'RankCacheY_%s' % pType
	if cacheName not in globalDict or oldCacheName not in globalDict:
		print "GE_EXC, pType(%s) error while SetRankData in LanternFestivalControl"
		return
	
	#重新排序
	nowRank.sort(key=lambda it:it[:3], reverse=True)
	oldRank.sort(key=lambda it:it[:3], reverse=True)
	
	globalDict[cacheName] = nowRank
	globalDict[oldCacheName] = oldRank


def NewDayRewardRoles():
	#发邮件对排行榜上面的玩家发奖
	global LogicRankDict
	#清理一天的排行榜缓存
	LogicRankDict = {1 : {}, 2 : {}, 3 : {}, 4 : {}, 5:{}}
	
	global RankCacheT_1, RankCacheT_2, RankCacheT_3, RankCacheT_4, RankCacheT_5
	global RankCacheY_1, RankCacheY_2, RankCacheY_3, RankCacheY_4, RankCacheY_5
	
	#替换昨天的跨服排行榜
	RankCacheT_1, RankCacheY_1 = [], RankCacheT_1
	RankCacheT_2, RankCacheY_2 = [], RankCacheT_2
	RankCacheT_3, RankCacheY_3 = [], RankCacheT_3
	RankCacheT_4, RankCacheY_4 = [], RankCacheT_4
	RankCacheT_5, RankCacheY_5 = [], RankCacheT_5

	
	days = cDateTime.Days()
	
	#更新跨服数据到数据库中
	GlobalHttp.SetGlobalData(GlobalDataDefine.LanternFestivalRankOld_1, (days - 1, RankCacheY_1))
	GlobalHttp.SetGlobalData(GlobalDataDefine.LanternFestivalRankOld_2, (days - 1, RankCacheY_2))
	GlobalHttp.SetGlobalData(GlobalDataDefine.LanternFestivalRankOld_3, (days - 1, RankCacheY_3))
	GlobalHttp.SetGlobalData(GlobalDataDefine.LanternFestivalRankOld_4, (days - 1, RankCacheY_4))
	GlobalHttp.SetGlobalData(GlobalDataDefine.LanternFestivalRankOld_5, (days - 1, RankCacheY_5))
	
	GlobalHttp.SetGlobalData(GlobalDataDefine.LanternFestivalRank_1, (days, RankCacheT_1))
	GlobalHttp.SetGlobalData(GlobalDataDefine.LanternFestivalRank_2, (days, RankCacheT_2))
	GlobalHttp.SetGlobalData(GlobalDataDefine.LanternFestivalRank_3, (days, RankCacheT_3))
	GlobalHttp.SetGlobalData(GlobalDataDefine.LanternFestivalRank_4, (days, RankCacheT_4))
	GlobalHttp.SetGlobalData(GlobalDataDefine.LanternFestivalRank_5, (days, RankCacheT_5))
	
	#邮件奖励
	transaction = AutoLog.traLanternRankMailReward
	LG = LanternRankConfigDict.get
	maxRankLen = 100	#排行榜最大个数
	
	globalDict = globals()
	for serverType in xrange(1, 6):
		tmpRank = 1			#初始排名
		tmpRankDict = {}
		maildatas = []
		RankCacheY = globalDict["RankCacheY_%s" % serverType]
		for rankData in RankCacheY:
			if tmpRank > maxRankLen:
				continue
			#先拿到当前排名需要的积分配置
			cfg = LG((tmpRank, serverType))
			if not cfg:
				print 'GE_EXC, LanternRankConfigDict can not find (tmpRank, serverType)(%s,%s) cfg' % (tmpRank, serverType)
				continue
			
			while rankData[0] < cfg.needScore:
				#如果当前的积分小于需要的积分, 排名往后加
				tmpRank += 1
				if tmpRank > maxRankLen:
					break
				#获取下一个排名的配置
				cfg = LG((tmpRank, serverType))
				if not cfg:
					print 'GE_EXC, AfterNewHour can not find rank %s cfg' % tmpRank
					continue
			
			if tmpRank > maxRankLen:
				#跳出for循环
				break
			
			if rankData[0] < cfg.needScore:
				print 'GE_EXC, AfterNewHour error'
				continue
			
			tmpRankDict[rankData[2]] = tmpRank
			#完了排名+1
			tmpRank += 1
			
		for roleid, rank in tmpRankDict.iteritems():
			rolemaildata = (roleid, GlobalPrompt.LanternFesitivalC_Title, GlobalPrompt.LanternFesitivalC_Sender, GlobalPrompt.LanternFesitivalC_Content % rank, transaction, GetRankMailReward(rank, serverType))
			maildatas.append(rolemaildata)
		#发送邮件奖励
		GlobalHttp.SendRoleMail(maildatas)		

	
def GetRankMailReward(rank, serverType):
	#组合一个邮件奖励字典
	mailData = {}
	
	global LanternRankConfigDict
	cfg = LanternRankConfigDict.get((rank, serverType))
	if not cfg:
		print "GE_EXC, LanternRankConfigDict can not find reward by rank (%s)" % rank
		return
	
	if cfg.rewardItems:
		mailData[EnumMail.EnumItemsKey] = cfg.rewardItems
	if cfg.money:
		mailData[EnumMail.EnumMonyKey] = cfg.money
	if cfg.bindRMB:
		mailData[EnumMail.EnumBindRMBKey] = cfg.bindRMB
	
	return mailData


if "_HasLoad" not in dir():
	if Environment.HasControl:
		LoadCrossRankHttp()
		LoadLanternFestivalActiveConfig()
		LoadLanternRankConfig()
		cComplexServer.RegAfterNewMinuteCallFunction(AfterNewMinute)
		cComplexServer.RegDistribute(PyMessage.Logic_RequestGetCrossLanternRank, OnLogicRequestCrossRank)
