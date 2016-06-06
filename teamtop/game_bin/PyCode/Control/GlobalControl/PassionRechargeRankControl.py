#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Control.GlobalControl.PassionRechargeRankControl")
#===============================================================================
# 激情活动 -- 充值排名控制
#===============================================================================
import copy
import time
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
	RankCache = []
	RankCache_old = []
	
	#注意这里只有一个区域了
	#逻辑进程排行榜缓存数据{服务器Id: 前500名数据列表}
	LoginRankAll_Dict = {}
	#总共的逻辑进程
	TotalLogicCnt = 0
	
	#数据载入是否成功
	ReturnDB = False
	#活动是否开启
	IS_START = False
	#载回数据
	LoadDataDict = {}
	
	CFILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	CFILE_FOLDER_PATH.AppendPath("CircularActive")
	
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("PassionAct")
	
	#积分排行—— 排行版奖励字典  {(index,levelRangeId):PassionRechargeRankConfig,}
	PassionRechargeKuaFuRank_Dict = {}
	#区间对应的排行榜奖励索引 {rankInterval:index,} 
	PassionRechargeKuaFuRankToIndex_Dict = {}
	#等级段关联等级段ID{levelRangeId:levelRange,}
	PassionRechargeKuaFuRankLevelID2Range_Dict = {}
	
class PassionRechargeRankActiveConfig(TabFile.TabLine):
	FilePath = CFILE_FOLDER_PATH.FilePath("PassionRechargeRankActive.txt")
	def __init__(self):
		self.startTime = self.GetDatetimeByString
		self.endTime = self.GetDatetimeByString
		
	
	def init_active(self):
		#开始时间戳
		beginTime = int(time.mktime((self.startTime).timetuple()))
		#结束时间戳
		endTime = int(time.mktime((self.endTime).timetuple()))
		#当前时间戳
		nowTime = cDateTime.Seconds()
		
		if beginTime <= nowTime < endTime:
			#在开始和结束时间戳之间, 激活
			OpenPassionRechargeRank(None, endTime)
			cComplexServer.RegTick(endTime - nowTime + 60, ClosePassionRechargeRank)
		elif nowTime < beginTime:
			#在开始时间戳之前
			cComplexServer.RegTick(beginTime - nowTime, OpenPassionRechargeRank, endTime)
			cComplexServer.RegTick(endTime - nowTime + 60, ClosePassionRechargeRank)

def LoadPassionRechargeRankActiveConfig():
	for cfg in PassionRechargeRankActiveConfig.ToClassType(False):
		if cfg.startTime > cfg.endTime:
			print "GE_EXC, startTime > endTime in PassionRechargeRankActive"
			return
		cfg.init_active()
		
class PassionRechargeKuaFuRankConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionRechargeKuaFuRank.txt")
	def __init__(self):
		self.index = int							#排名奖励索引
		self.rankInterval = eval					#排名区间
		self.needRMB = int							#占位最低充值
		self.levelRangeId = int						#等级段ID
		self.levelRange = self.GetEvalByString		#等级段
		self.rewardItems = eval							#奖励
	
def LoadPassionRechargeKuaFuRankConfig():
	global PassionRechargeKuaFuRank_Dict, PassionRechargeKuaFuRankToIndex_Dict, PassionRechargeKuaFuRankLevelID2Range_Dict
	
	for cfg in PassionRechargeKuaFuRankConfig.ToClassType(False):
		index = cfg.index
		levelRangeId = cfg.levelRangeId
		levelRange = cfg.levelRange
		rankInterval = cfg.rankInterval
		if (index, levelRangeId) in PassionRechargeKuaFuRank_Dict:
			print "GE_EXC, repeat (index : %s, levelRangeId:%s) in PassionRechargeKuaFuRank_Dict" % (index, levelRangeId)
			
		#排名区间 -- > 排名索引
		if rankInterval not in PassionRechargeKuaFuRankToIndex_Dict:
			PassionRechargeKuaFuRankToIndex_Dict[rankInterval] = index
			
		PassionRechargeKuaFuRank_Dict[(index, levelRangeId)] = cfg
		
		PassionRechargeKuaFuRankLevelID2Range_Dict[levelRangeId] = levelRange

def GetRankCfgByRankAndType(rank, roleLevel):
	'''
	返回排名rank对应的排名index
	'''
	retIndex = 0
	for rankInterval, index in PassionRechargeKuaFuRankToIndex_Dict.iteritems():
		rankDown , rankUp = rankInterval
		if rankDown <= rank and rank <= rankUp:
			retIndex = index
	
	tmpLevelRangeId = 0
	for levelRangeId, levelRange in PassionRechargeKuaFuRankLevelID2Range_Dict.iteritems():
		tmpLevelRangeId = levelRangeId
		if levelRange[0] <= levelRange[1]:
			break
	
	rankCfg = PassionRechargeKuaFuRank_Dict.get((retIndex,tmpLevelRangeId))
	return rankCfg
	
def OpenPassionRechargeRank(callArgv, regparam):
	#开启积分排行
	global IS_START
	if IS_START:
		print "GE_EXC, PassionRechargeRank is already open"
		return
	IS_START = True

def ClosePassionRechargeRank(callArgv, regparam):
	#结束积分排行
	global IS_START
	if not IS_START:
		print "GE_EXC, PassionRechargeRank is already close"
		return
	
	#清理排行榜数据
	global RankCache, RankCache_old
	RankCache = []
	RankCache_old = []
	
	global LoginRankAll_Dict
	#清理逻辑进程排行榜缓存数据{服务器Id: 前500名数据列表}
	LoginRankAll_Dict = {}
	
	IS_START = False

def AfterNewMinute():
	'''
	'''
	global IS_START
	if not IS_START: return
	
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
		print "GE_EXC, PassionRechargeRankControl AfterNewHour error not ReturnDB"
		#数据没有载回, 尝试再次载入
		InitGetRankEx()
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
		ControlProxy.SendLogicMsgAndBack(sessionid, PyMessage.Control_RequestLogicPassionRechargeRank, None, LogicBackRank, sessionid)

def LogicBackRank(callargv, regparam):
	#逻辑进程返回或者自返回
	global TotalLogicCnt
	TotalLogicCnt -= 1
	if callargv:
		global LoginRankAll_Dict
		processId, logicranklist = callargv
		LoginRankAll_Dict[processId] = logicranklist

	if TotalLogicCnt == 0:
		#所有的逻辑进程已经返回了排行榜,对排行榜进行排序,然后更新到数据库
		SortAndUpdataRank()
	elif TotalLogicCnt < 0:
		print "GE_EXC, error in PassionRechargeRankControl RequestBack (%s)" % TotalLogicCnt
	
def SortAndUpdataRank():
	#更新数据库中的排行榜数据
	global RankCache, LoginRankAll_Dict
	days = cDateTime.Days()
	RankCache = []
	
	for l in LoginRankAll_Dict.values():
		RankCache.extend(l)
		
	if RankCache:
		RankCache.sort(key = lambda it:(it[0], it[1], it[4]), reverse = True)
		RankCache = RankCache[:500]
		GlobalHttp.SetGlobalData(GlobalDataDefine.PassionRechargeRankDataKey, (days, RankCache))

	#同步数据给所有的逻辑进程(当天数据)
	SyncAllLoginToday()

def NewDayRewardRoles():
	#发邮件对排行榜上面的玩家发奖
	global LoginRankAll_Dict, RankCache, RankCache_old
	
	#清理一天的排行榜缓存
	LoginRankAll_Dict =  {}
	#替换昨天的跨服排行榜
	RankCache_old = RankCache
	#清理今天的跨服排行榜
	RankCache = []
	
	days = cDateTime.Days()
	
	#更新跨服数据到数据库中
	GlobalHttp.SetGlobalData(GlobalDataDefine.PassionRechargeRankDataKey_old, (days - 1, RankCache_old))
	GlobalHttp.SetGlobalData(GlobalDataDefine.PassionRechargeRankDataKey, (days, RankCache))
	
	#第一区域服务器
	RewardRolesByServerType(RankCache_old)
	
def RewardRolesByServerType(rankData):
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
		cfg = GetRankCfgByRankAndType(tmpRank, rank[4])
		if not cfg:
			print 'GE_EXC, RewardRolesByServerType::AfterNewHour can not find rank %s cfg' % tmpRank
			continue
		
		while rank[0] < cfg.needRMB:
			#如果当前的积分小于需要的积分, 排名往后加
			tmpRank += 1
			if tmpRank > maxRankLen:
				break
			#获取下一个排名的配置
			cfg = GetRankCfgByRankAndType(tmpRank, rank[4])
			if not cfg:
				print 'GE_EXC, RewardRolesByServerType::AfterNewHour can not find rank %s cfg' % tmpRank
				continue
		
		if tmpRank > maxRankLen:
			#跳出for循环
			break
		
		if rank[0] < cfg.needRMB:
			print 'GE_EXC,RewardRolesByServerType:: AfterNewHour error'
			continue
		
		tmpRankDict[rank[1]] = [tmpRank,rank[4]]
		#完了排名+1
		tmpRank += 1
	
	maildatas = []	
	transaction = AutoLog.traPassionRechargeRankMailReward
	for roleid, rankInfo in tmpRankDict.iteritems():
		rank, roleLevel = rankInfo
		rolemaildata = (roleid, GlobalPrompt.PassionRechargeRank_KuaFu_Title, GlobalPrompt.PassionRechargeRank_KuaFu_Sender, GlobalPrompt.PassionRechargeRank_KuaFu_Content % (cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), rank), transaction, GetRankMailReward(rank, roleLevel))
		maildatas.append(rolemaildata)
	#发送邮件奖励
	GlobalHttp.SendRoleMail(maildatas)
	
	print 'BLUE, PassionRechargeKuaFuRank %s' % tmpRankDict
	
def GetRankMailReward(rank, roleLevel):
	#组合一个邮件奖励字典
	mailData = {}
	
	#排名 --> 排名区间 --> 奖励索引
	global PassionRechargeKuaFuRankToIndex_Dict
	index = 0
	for (begin, end), rewardIndex in PassionRechargeKuaFuRankToIndex_Dict.iteritems():
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
	for levelRangeId, levelRange in PassionRechargeKuaFuRankLevelID2Range_Dict.iteritems():
		tmpLevelRangeId = levelRangeId
		if levelRange[0] <= roleLevel <= levelRange[1]:
			break
	else:
		print 'GE_EXC, PassionRechargeKuaFuRank can not find %s level range id' % roleLevel
		return
	
	#(奖励索引, 服务器类型) --> 奖励
	cfg = PassionRechargeKuaFuRank_Dict.get((index, tmpLevelRangeId))
	if not cfg:
		print "GE_EXC, GetRankMailReward can not find reward by rank (%s) " % rank
		return
	
	#目前只有物品奖励
	if cfg.rewardItems:
		mailData[EnumMail.EnumItemsKey] = copy.deepcopy(cfg.rewardItems)
	return mailData

###############################################################################
def InitGetRankEx():
	#数据太大了, 要分开载入
	key = GlobalDataDefine.PassionRechargeRankDataKey
	oldkey = GlobalDataDefine.PassionRechargeRankDataKey_old
	
	GlobalHttp.GetGlobalData(key, OnGetRankBackEx, key)
	GlobalHttp.GetGlobalData(oldkey, OnGetRankBackEx, oldkey)

def OnGetRankBackEx(response, regparam):
	#今日数据和昨日数据是分开载入的, 这里有两次返回, 特殊处理一下
	if response is None:
		#自返回
		return
	
	key = regparam
	
	global LoadDataDict
	if key not in LoadDataDict:
		#缓存
		LoadDataDict[key] = response
	else:
		return
	
	if len(LoadDataDict) < 2:
		#载回计数
		return
	
	#处理数据
	days = cDateTime.Days()
	Checkdata(LoadDataDict, days, GlobalDataDefine.PassionRechargeRankDataKey, GlobalDataDefine.PassionRechargeRankDataKey_old)
	
	#清理缓存
	LoadDataDict = {}
	
	#已经载入成功了
	global ReturnDB
	ReturnDB = True
	#同步数据给所有的逻辑进程
	SyncAllLogin()

def SetRankData(nowRank, oldRank):
	#设置缓存数据
	global RankCache
	global RankCache_old
	
	#重新排序
	nowRank.sort(key = lambda it:(it[0], it[1], it[4]), reverse = True)
	oldRank.sort(key = lambda it:(it[0], it[1], it[4]), reverse = True)
	
	RankCache = nowRank
	RankCache_old = oldRank
	
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
	global LoginRankAll_Dict
	for processId in LoginRankAll_Dict.iterkeys():
		cp = ProcessMgr.ControlProcesssIds.get(processId)
		if not cp:
			if not Environment.IsDevelop:
				print "GE_EXC, SyncAllLogin not process sessionid (%s)" % processId
			continue
		sessionid = cp.session_id
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataPassionRechargeRankToLogic, (RankCache, RankCache_old))

def SyncAllLoginToday():
	#同步当天最新的排行榜给所有的逻辑进程
	global LoginRankAll_Dict
	for processId in LoginRankAll_Dict.iterkeys():
		cp = ProcessMgr.ControlProcesssIds.get(processId)
		if not cp:
			if not Environment.IsDevelop:
				print "GE_EXC, SyncAllLoginToday not process sessionid (%s)" % processId
			continue
		sessionid = cp.session_id
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataPassionRechargeRankToLogic_T, RankCache)

def LoginRequestRank(sessionid, msg):
	'''
	#逻辑进程主动请求跨服排行榜数据
	@param sessionid:
	@param msg:(进程ID， 进程区域类型)
	'''
	global ReturnDB,  LoginRankAll_Dict, RankCache, RankCache_old
	#先记录逻辑进程的区域类型
	processId, rank = msg
	LoginRankAll_Dict[processId] =  rank
	
	if not ReturnDB:
		#控制进程当前还没有从DB载回数据，等待数据载回来再发过去
		return

	#根据类型发送数据
	ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataPassionRechargeRankToLogic, (RankCache, RankCache_old))

def AfterLoadWorldData():
	'''
	世界数据载回后 
	'''
	LoadPassionRechargeRankActiveConfig()

if "_HasLoad" not in dir():
	if Environment.HasControl:
		LoadPassionRechargeKuaFuRankConfig()
		LoadPassionRechargeRankActiveConfig()
		InitGetRankEx()
		cComplexServer.RegAfterNewMinuteCallFunction(AfterNewMinute)
		cComplexServer.RegDistribute(PyMessage.Control_GetPassionRechargeRank, LoginRequestRank)

	
