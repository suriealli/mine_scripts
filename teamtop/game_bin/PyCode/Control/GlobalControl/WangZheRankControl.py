#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Control.GlobalControl.WangZheRankControl")
#===============================================================================
# 王者公测积分排行榜 Control
#===============================================================================
import copy
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
	RankCache_1 = []
	
	RankCache_old_1 = []
	
	#逻辑进程排行榜缓存数据{服务器区域类型 : {服务器Id: 前100名数据列表}}
	LoginRankAll_Dict = {1 : {}}
	
	#总共的逻辑进程
	TotalLogicCnt = 0
	
	#逻辑进程区域类型
	LogicType_Dict = {}
	
	#数据载入是否成功
	ReturnDB = False
	ReturnIndexset = set()
	
	IS_START = False
	
	FIRSTDAY_DATETIME = None
	
	CFILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	CFILE_FOLDER_PATH.AppendPath("CircularActive")
	
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("WangZheGongCe")
	
	#积分排行—— 排行版奖励字典  {(index,serverType,levelRangeId):WangZheKuaFuRankConfig,}
	WangZheKuaFuRank_Dict = {}
	#区间对应的排行榜奖励索引 {rankInterval:index,} 
	WangZheKuaFuRankToIndex_Dict = {}
	#等级段关联等级段ID{levelRangeId:levelRange,}
	WangZheKuaFuRankLevelID2Range_Dict = {}
	
	
class WangZheRankActiveConfig(TabFile.TabLine):
	FilePath = CFILE_FOLDER_PATH.FilePath("WangZheRankActive.txt")
	def __init__(self):
		self.activeName = str
		self.startTime = self.GetDatetimeByString
		self.endTime = self.GetDatetimeByString
	
	def init_active(self):
		global FIRSTDAY_DATETIME
		FIRSTDAY_DATETIME = self.startTime
		#当前日期时间
		nowDate = cDateTime.Now()
		#开始时间戳
		beginTime = int(time.mktime((self.startTime).timetuple()))
		#结束时间戳
		endTime = int(time.mktime((self.endTime).timetuple()))
		#当前时间戳
		nowTime = int(time.mktime(datetime.datetime(cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second()).timetuple()))
		
		if self.startTime <= nowDate < self.endTime:
			#在开始和结束时间戳之间, 激活
			OpenWangZheRank(None, endTime)
			cComplexServer.RegTick(endTime - nowTime + 60, CloseWangZheRank)
		elif nowDate < self.startTime:
			#在开始时间戳之前
			cComplexServer.RegTick(beginTime - nowTime, OpenWangZheRank, endTime)
			cComplexServer.RegTick(endTime - nowTime + 60, CloseWangZheRank)

def LoadWangZheRankActiveConfig():
	for cfg in WangZheRankActiveConfig.ToClassType(False):
		if cfg.startTime > cfg.endTime:
			print "GE_EXC, startTime > endTime in WangZheRankActive"
			return
		cfg.init_active()
		
class WangZheKuaFuRankConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("WangZheKuaFuRank.txt")
	def __init__(self):
		self.index = int						#排名奖励索引
		self.rankInterval = eval				#排名区间
		self.serverType = int					#服务器类型
		self.needJiFen = int					#占位最低积分值
		self.levelRangeId = int					#等级段ID
		self.levelRange = self.GetEvalByString	#等级段
		self.reward = eval						#奖励
		self.rewardEx = self.GetEvalByString	#特殊奖励
	
def LoadWangZheKuaFuRankConfig():
	global WangZheKuaFuRank_Dict
	global WangZheKuaFuRankToIndex_Dict
	global WangZheKuaFuRankLevelID2Range_Dict
	
	for cfg in WangZheKuaFuRankConfig.ToClassType(False):
		index = cfg.index
		serverType = cfg.serverType
		levelRangeId = cfg.levelRangeId
		levelRange = cfg.levelRange
		rankInterval = cfg.rankInterval
		if (index, serverType, levelRangeId) in WangZheKuaFuRank_Dict:
			print "GE_EXC, repeat (index : %s, serverType : %s,levelRangeId:%s) in WangZheKuaFuRank_Dict" % (index, serverType, levelRangeId)
			
		#排名区间 -- > 排名索引
		if rankInterval not in WangZheKuaFuRankToIndex_Dict:
			WangZheKuaFuRankToIndex_Dict[rankInterval] = index
			
		WangZheKuaFuRank_Dict[(index, serverType, levelRangeId)] = cfg
		
		WangZheKuaFuRankLevelID2Range_Dict[levelRangeId] = levelRange

def GetRankCfgByRankAndType(rank, serverType, roleLevel):
	'''
	返回排名rank对应的排名index
	'''
	retIndex = 0
	for rankInterval, index in WangZheKuaFuRankToIndex_Dict.iteritems():
		rankDown , rankUp = rankInterval
		if rankDown <= rank and rank <= rankUp:
			retIndex = index
	
	tmpLevelRangeId = 0
	for levelRangeId, levelRange in WangZheKuaFuRankLevelID2Range_Dict.iteritems():
		tmpLevelRangeId = levelRangeId
		if levelRange[0] <= levelRange[1]:
			break
	
	rankCfg = WangZheKuaFuRank_Dict.get((retIndex,serverType, tmpLevelRangeId))
	return rankCfg
	
def OpenWangZheRank(callArgv, regparam):
	#开启积分排行
	global IS_START
	if IS_START:
		print "GE_EXC, WangZheRank is already open"
		return
	IS_START = True

def CloseWangZheRank(callArgv, regparam):
	#结束积分排行
	global IS_START
	if not IS_START:
		print "GE_EXC, WangZheRank is already close"
		return
	
	#清理排行榜数据
	global RankCache_1
	RankCache_1= []
	global RankCache_old_1
	RankCache_old_1 = []
	
	global LoginRankAll_Dict, LogicType_Dict
	#清理逻辑进程排行榜缓存数据{服务器区域类型 : {服务器Id: 前100名数据列表}}
	LoginRankAll_Dict = {1 : {}}
	#清理逻辑进程区域类型
	LogicType_Dict = {}
	
	IS_START = False

def AfterNewMinute():
	'''
	'''
	if not IS_START:
		#活动没有开启
		return
	
	now = cDateTime.Now()
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
		print "GE_EXC, WangZheRankControl AfterNewHour error not ReturnDB"
		#数据没有载回, 尝试再次载入
		InitGetRankEx()
		return
	
	if nowHour == 0 and nowMinute == 0:
		#0点0分的时候只发奖，操作数据库数据，逻辑进程自己把今天的数据拷贝到“昨天”的数据里面
		isRewardEx = False
		tmpTimeDelta = now - FIRSTDAY_DATETIME
		if tmpTimeDelta.days == 1:
			isRewardEx = True
		
		#联盟的不发额外特殊奖励
		if Environment.EnvIsQQUnion():
			isRewardEx = False
		
		NewDayRewardRoles(isRewardEx)
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
		ControlProxy.SendLogicMsgAndBack(sessionid, PyMessage.Control_RequestLogicWangZheRank, None, LogicBackRank, sessionid)


def LogicBackRank(callargv, regparam):
	#逻辑进程返回或者自返回
	global TotalLogicCnt
	TotalLogicCnt -= 1
	if callargv:
		global LogicType_Dict, LoginRankAll_Dict
		processId, serverType, logicranklist = callargv
		LogicType_Dict[processId] = serverType
		rankDict = LoginRankAll_Dict.get(serverType)
		if not rankDict:
			LoginRankAll_Dict[serverType] = rankDict = {} 
		rankDict[processId] = logicranklist

	if TotalLogicCnt == 0:
		#所有的逻辑进程已经返回了排行榜,对排行榜进行排序,然后更新到数据库
		SortAndUpdataRank()
	elif TotalLogicCnt < 0:
		print "GE_EXC, error in WangZheRankControl RequestBack (%s)" % TotalLogicCnt
	
def SortAndUpdataRank():
	#更新数据库中的排行榜数据
	global RankCache_1, RankCache_2, RankCache_3, RankCache_4, RankCache_5
	days = cDateTime.Days()
	RankCache_1 = []
	ranDict = LoginRankAll_Dict.get(1, {})
	for l in ranDict.values():
		RankCache_1.extend(l)
		
	if RankCache_1:
		RankCache_1.sort(key = lambda it:(it[0], it[1]), reverse = True)
		RankCache_1 = RankCache_1[:500]
		GlobalHttp.SetGlobalData(GlobalDataDefine.WangZheRankDataKey_1, (days, RankCache_1))

	#同步数据给所有的逻辑进程(当天数据)
	SyncAllLoginToday()

def NewDayRewardRoles(isRewardEx = False):
	#发邮件对排行榜上面的玩家发奖
	global LoginRankAll_Dict
	#清理一天的排行榜缓存
	LoginRankAll_Dict =  {1 : {}}
	global RankCache_1
	global RankCache_old_1
	
	#替换昨天的跨服排行榜
	RankCache_old_1 = RankCache_1
	
	#清理今天的跨服排行榜
	RankCache_1 = []
	
	days = cDateTime.Days()
	
	#更新跨服数据到数据库中
	GlobalHttp.SetGlobalData(GlobalDataDefine.WangZheRankDataKey_old_1, (days - 1, RankCache_old_1))
	GlobalHttp.SetGlobalData(GlobalDataDefine.WangZheRankDataKey_1, (days, RankCache_1))
	
	#第一区域服务器
	RewardRolesByServerType(RankCache_old_1, 1, isRewardEx)
	
	
def RewardRolesByServerType(rankData, serverType, isRewardEx = False):
	'''
	根据排行数据 和 服务器类型 结算
	'''
	tmpRankDict = {}	#{roleId:[rank,roleLevel]}
	tmpRank = 1			#初始排名
	maxRankLen = 500	#排行榜最大个数
	
	for rank in rankData:
		if tmpRank > maxRankLen:
			#超过排行榜最大个数了
			continue
		
		#先拿到当前排名需要的积分配置
		cfg = GetRankCfgByRankAndType(tmpRank, serverType, rank[4])
		if not cfg:
			print 'GE_EXC, RewardRolesByServerType::AfterNewHour can not find rank %s cfg' % tmpRank
			continue
		
		while rank[0] < cfg.needJiFen:
			#如果当前的积分小于需要的积分, 排名往后加
			tmpRank += 1
			if tmpRank > maxRankLen:
				break
			#获取下一个排名的配置
			cfg = GetRankCfgByRankAndType(tmpRank, serverType, rank[4])
			if not cfg:
				print 'GE_EXC, RewardRolesByServerType::AfterNewHour can not find rank %s cfg' % tmpRank
				continue
		
		if tmpRank > maxRankLen:
			#跳出for循环
			break
		
		if rank[0] < cfg.needJiFen:
			print 'GE_EXC,RewardRolesByServerType:: AfterNewHour error'
			continue
		
		tmpRankDict[rank[1]] = [tmpRank,rank[4]]
		#完了排名+1
		tmpRank += 1
	
	maildatas = []	
	transaction = AutoLog.traWangZheRankMailReward
	for roleid, rankInfo in tmpRankDict.iteritems():
		rank, roleLevel = rankInfo
		rolemaildata = (roleid, GlobalPrompt.WangZheRank_Title, GlobalPrompt.WangZheRank_Sender, GlobalPrompt.WangZheRank_Content % rank, transaction, GetRankMailReward(rank, roleLevel, serverType, isRewardEx))
		maildatas.append(rolemaildata)
	#发送邮件奖励
	GlobalHttp.SendRoleMail(maildatas)
	
def GetRankMailReward(rank, roleLevel, serverType, isRewardEx = False):
	#组合一个邮件奖励字典
	mailData = {}
	
	#排名 --> 排名区间 --> 奖励索引
	global WangZheKuaFuRankToIndex_Dict
	index = 0
	for (begin, end), rewardIndex in WangZheKuaFuRankToIndex_Dict.iteritems():
		if (begin == end) and (rank == begin):
			#begin == end
			index = rewardIndex
			break
		elif (begin != end) and (begin <= rank <= end):
			#begin != end
			index = rewardIndex
			break
	else:
		print "GE_EXC, GetRankMailReward can not find index by rank (%s)" % rank
		return
	
	tmpLevelRangeId = 0
	for levelRangeId, levelRange in WangZheKuaFuRankLevelID2Range_Dict.iteritems():
		tmpLevelRangeId = levelRangeId
		if levelRange[0] <= roleLevel <= levelRange[1]:
			break
	
	#(奖励索引, 服务器类型) --> 奖励
	cfg = WangZheKuaFuRank_Dict.get((index, serverType, tmpLevelRangeId))
	if not cfg:
		print "GE_EXC, GetRankMailReward can not find reward by rank (%s) serverType (%s)" % (rank, serverType)
		return
	
	#目前只有物品奖励
	if cfg.reward:
		mailData[EnumMail.EnumItemsKey] = copy.deepcopy(cfg.reward)
	if isRewardEx is True:
		if cfg.rewardEx:
			(mailData[EnumMail.EnumItemsKey]).extend(cfg.rewardEx)
	
	return mailData

###############################################################################
def InitGetRankEx():
	index = 1
	key = GlobalDataDefine.WangZheRankDataKey_1
	oldkey = GlobalDataDefine.WangZheRankDataKey_old_1
	GlobalHttp.GetGlobalDataByKeys([key, oldkey], OnGetRankBackEx, (index, key, oldkey))
	

def OnGetRankBackEx(response, regparam):
	#数据返回了
	if response is None:
		#自返回
		return
	
	index, key, oldkey = regparam
	
	#分析和处理数据
	datadict = response
	days = cDateTime.Days()
	Checkdata(datadict, index, days, key, oldkey)
	
	global ReturnIndexset
	ReturnIndexset.add(index)

	#已经载入成功了
	global ReturnDB
	if len(ReturnIndexset) >= 1:
		ReturnDB = True
		#同步数据给所有的逻辑进程
		SyncAllLogin()

def SetRankData(pType, nowRank, oldRank):
	#设置缓存数据
	global RankCache_1
	global RankCache_old_1
	
	#重新排序
	nowRank.sort(key = lambda it:it[0], reverse = True)
	oldRank.sort(key = lambda it:it[0], reverse = True)
	
	if pType == 1:
		RankCache_1 = nowRank
		RankCache_old_1 = oldRank
		
	
def Checkdata(datadict, pType, nowdays, nowKey, oldKey):
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

def SyncAllLogin():
	#同步数据给所有的逻辑进程(今天和昨天)
	global LogicType_Dict
	for processId, pType in LogicType_Dict.iteritems():
		cp = ProcessMgr.ControlProcesssIds.get(processId)
		if not cp:
			if not Environment.IsDevelop:
				print "GE_EXC, SyncAllLogin not process sessionid (%s)" % processId
			continue
		sessionid = cp.session_id
		if pType == 1:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataWangZheRankToLogic, (RankCache_1, RankCache_old_1))
		else:
			print "GE_EXC, SyncAllLogin error pType (%s)" % pType

def SyncAllLoginToday():
	#同步当天最新的排行榜给所有的逻辑进程
	global LogicType_Dict
	for processId, pType in LogicType_Dict.iteritems():
		cp = ProcessMgr.ControlProcesssIds.get(processId)
		if not cp:
			if not Environment.IsDevelop:
				print "GE_EXC, SyncAllLoginToday not process sessionid (%s)" % processId
			continue
		sessionid = cp.session_id
		if pType == 1:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataWangZheRankToLogic_T, RankCache_1)
		else:
			print "GE_EXC, SyncAllLogin error pType (%s)" % pType

def LoginRequestRank(sessionid, msg):
	'''
	#逻辑进程主动请求跨服排行榜数据
	@param sessionid:
	@param msg:(进程ID， 进程区域类型)
	'''
	global ReturnDB,  LogicType_Dict
	#先记录逻辑进程的区域类型
	processId, pType, rank = msg
	LoginRankAll_Dict[pType][processId] =  rank
	
	LogicType_Dict[processId] = pType
	
	if not ReturnDB:
		#控制进程当前还没有从DB载回数据，等待数据载回来再发过去
		return

	#根据类型发送数据
	if pType == 1:
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataWangZheRankToLogic, (RankCache_1, RankCache_old_1))
	else:
		print "GE_EXC, error pType (%s) in LoginRequestRank" % pType

if "_HasLoad" not in dir():
	if Environment.HasControl:
		LoadWangZheRankActiveConfig()
		LoadWangZheKuaFuRankConfig()
		InitGetRankEx()
		
		cComplexServer.RegAfterNewMinuteCallFunction(AfterNewMinute)
		cComplexServer.RegDistribute(PyMessage.Control_GetWangZheRank, LoginRequestRank)
