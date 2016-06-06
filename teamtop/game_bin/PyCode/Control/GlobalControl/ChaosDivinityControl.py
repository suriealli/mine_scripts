#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Control.GlobalControl.BraveHeroControl")
#===============================================================================
# 勇者英雄坛控制模块
#===============================================================================
import cDateTime
import cComplexServer
import DynamicPath
import Environment
from Util.File import TabFile
from Common.Message import PyMessage
from Common.Other import GlobalDataDefine
from Control import ProcessMgr
from ComplexServer.Plug.Control import ControlProxy
from ComplexServer.API import GlobalHttp
from ComplexServer.Time import Cron

if "_HasLoad" not in dir():
	DES_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	DES_FILE_FOLDER_PATH.AppendPath("ChaosDivinity")

	#排行榜数据缓存(保证排行数据不会被擦除)
	LoginRankAll_Dict = {}

	RankCache 		 = [] 	#今日排行
	RankOldCache 	 = [] 	#昨日排行

	RankReward 		= (0,{}) 	#{processId:(rewardId)}

	ChaosDivinity_RankRewardDict = {}

	#总共的逻辑进程
	TotalLogicCnt = 0

	#数据载入是否成功
	ReturnDB = False

#混沌神域排行奖励配置
class ChaosDivinityRankReward(TabFile.TabLine):
	FilePath = DES_FILE_FOLDER_PATH.FilePath("ChaosDivinityRank.txt")

	def __init__(self):
		self.rewardId 			= int
		self.rankRange 			= self.GetEvalByString
		self.rewardItem 		= self.GetEvalByString
		self.rewardExp 			= int

def LoadRankReward():
	global ChaosDivinity_RankRewardDict
	global ChaosDivinity_RankRewardList

	for cfg in ChaosDivinityRankReward.ToClassType(False):
		if cfg.rewardId in ChaosDivinity_RankRewardDict:
			print "GE_EXC, repeat rewardId(%s) in ChaosDivinity_RankRewardDict"% cfg.rewardId
		ChaosDivinity_RankRewardDict[cfg.rewardId] = cfg

def GetRewardByRank(rank):
	'''
	通过排名获取奖励
	'''
	global ChaosDivinity_RankRewardDict
	for cfg in ChaosDivinity_RankRewardDict.values():
		if cfg.rankRange[0] <= rank and rank <= cfg.rankRange[1]:
			return cfg.rewardId

	return -1

def InitGetRank():
	key = GlobalDataDefine.ChaosDivinityRankKey
	oldkey = GlobalDataDefine.ChaosDivinityYesterdayRankKey
	rewardKey = GlobalDataDefine.ChaosDivinityReward

	GlobalHttp.GetGlobalDataByKeys([key, oldkey,rewardKey], OnGetRankBack, (key, oldkey, rewardKey))

def OnGetRankBack(response, regparam):
	#数据返回了
	if response is None:
		#自返回
		return
	global RankReward
	
	key, oldkey, rewardKey = regparam
	
	#分析和处理数据
	datadict = response
	days = cDateTime.Days()
	Checkdata(datadict, days, key, oldkey)

	rewardInfo = datadict.get(rewardKey)
	if rewardInfo:
		RankReward = rewardInfo
		#数据已过期
		if RankReward[0] != days-1:
			RankReward = (days-1,{})
			GlobalHttp.SetGlobalData(rewardKey,RankReward)
	else:
		GlobalHttp.SetGlobalData(rewardKey,RankReward)

	#已经载入成功了
	global ReturnDB
	ReturnDB = True
	#同步数据给所有的逻辑进程
	SyncAllLogin()


def SetRankData( nowRank, oldRank):
	#设置缓存数据
	global RankCache,RankOldCache

	#重新排序
	#nowRank.sort(key = lambda it:it[0], reverse = True)
	#oldRank.sort(key = lambda it:it[0], reverse = True)

	RankCache = nowRank
	RankOldCache = oldRank

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
			SetRankData( [], oldRank)
			return
		else:
			# 已经相差2天了，清理数据?
			GlobalHttp.SetGlobalData(nowKey, (nowdays, []))
			GlobalHttp.SetGlobalData(oldKey, (nowdays - 1, []))
			SetRankData([],[])
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
	SetRankData( nowRank, oldRank)

def RequestLogicRank():
	#向所有的逻辑进程获取排行榜数据
	global TotalLogicCnt
	TotalLogicCnt = len(ProcessMgr.ControlProcesssSessions)
	for sessionid, cp in ProcessMgr.ControlProcesssSessions.iteritems():
		if cp.processid >= 30000:
			#跨服服务器不处理
			TotalLogicCnt -= 1
			continue
		ControlProxy.SendLogicMsgAndBack(sessionid, PyMessage.Control_RequestLogicChaosDivinityRank, None, LogicBackRank, sessionid)

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
		print "GE_EXC, error in BraveHeroControl RequestBack (%s)" % TotalLogicCnt

def cmped(v1,v2):
	if v1 > v2:
		return 1
	elif v1 < v2:
		return -1
	else:
		return 0

def rank_cmp(v1,v2):
	#章节
	ret = cmped(v1[3],v2[3])
	if ret:
		return ret
	#通关回合数
	ret = cmped(v1[4],v2[4])
	if ret:
		return -ret
	#挑战时的战斗力
	ret = cmped(v1[5],v2[5])
	if ret:
		return ret
	#角色ID
	return cmped(v1[0][0],v2[0][0])

def SortAndUpdataRank():
	'''
	更新排行榜
	'''
	global LoginRankAll_Dict,RankCache
	days = cDateTime.Days()

	RankCache = []

	for l in LoginRankAll_Dict.values():
		RankCache.extend(l)

	if RankCache:
		#排序
		RankCache.sort(cmp = rank_cmp, reverse = True)
		RankCache = RankCache[:50]

		GlobalHttp.SetGlobalData(GlobalDataDefine.BraveHeroDataKey_1, (days, RankCache))

		#同步排行榜到逻辑进程
		SyncAllLogin()

def SyncAllLoginToday():
	#同步当天最新的排行榜给所有的逻辑进程
	global TotalLogicCnt
	TotalLogicCnt = len(ProcessMgr.ControlProcesssSessions)
	
	global ConsumeRecord
	for sessionid, cp in ProcessMgr.ControlProcesssSessions.iteritems():
		if cp.processid >= 30000:
			#跨服服务器不处理
			TotalLogicCnt -= 1
			continue
		
		#同步给逻辑进程字典格式{index:cnt}
		SyncLogicProcess(sessionid)

def SyncLogicProcess(sessionid):
	global RankCache
	if sessionid in ProcessMgr.ControlProcesssSessions.keys():
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_SyncChaosDivinityTodayRank, RankCache)

def SyncAllLogin():
	global TotalLogicCnt
	TotalLogicCnt = len(ProcessMgr.ControlProcesssSessions)
	
	global ConsumeRecord
	global RankCache,RankOldCache,RankReward
	for sessionid, cp in ProcessMgr.ControlProcesssSessions.iteritems():
		if cp.processid >= 30000:
			#跨服服务器不处理
			TotalLogicCnt -= 1
			continue
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_SyncChaosDivinityAllRank,(RankCache,RankOldCache,RankReward))

def NotifyLogicRewardUpdated(param):
	global TotalLogicCnt
	TotalLogicCnt = len(ProcessMgr.ControlProcesssSessions)
	
	global ConsumeRecord
	for sessionid, cp in ProcessMgr.ControlProcesssSessions.iteritems():
		if cp.processid >= 30000:
			#跨服服务器不处理
			TotalLogicCnt -= 1
			continue
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_RankRewardUpdated,param)

def NewDayRewardRoles():
	#发邮件对排行榜上面的玩家发奖
	global LoginRankAll_Dict
	#清理一天的排行榜缓存
	LoginRankAll_Dict = {}
	global RankCache,RankOldCache,RankReward
	
	#替换昨天的跨服排行榜
	RankOldCache = RankCache

	#清理今天的跨服排行榜
	RankCache = []

	days = cDateTime.Days()
	#更新跨服数据到数据库中
	GlobalHttp.SetGlobalData(GlobalDataDefine.ChaosDivinityYesterdayRankKey, (days - 1, RankOldCache))
	GlobalHttp.SetGlobalData(GlobalDataDefine.ChaosDivinityRankKey, (days, RankCache))

	#重算奖励
	RankReward = (days-1,{})
	#(角色ID)，(角色名字)，服务器名字, 章节, 回合数, 战斗力,进程ID
	for rank,l in enumerate(RankOldCache):
		processid = l[6]
		if RankReward[1].get(processid,-1) == -1:
			rewardId = GetRewardByRank(rank+1)
			if rewardId == -1:
				print "GE_EXC,no reward in ChaosDivinity_RankRewardDict rank(%s)"%(rank+1)
			else:
				RankReward[1][processid] = (rewardId,rank+1,(l[1]))

	#更新排行榜奖励到数据库
	GlobalHttp.SetGlobalData(GlobalDataDefine.ChaosDivinityReward,RankReward)

	#通知逻辑进程排行奖励已更新
	NotifyLogicRewardUpdated(RankReward)

def AfterNewHour():
	#每一个整点向所有的逻辑进程请求每一个服务器的前50名玩家数据，等待回调并且记录数据
	#如果有某些逻辑进程没有返回或者其他原因导致了这个回调是自回调的。这个时候，就会使用上一个小时
	#的旧数据代替这个一个服的数据。
	
	#所有的回调都完毕后，触发对这些玩家数据排序出前100名。并且http请求更新到数据库
	#（缺数据清理规则，数据中可能要存储天数的时间戳，清理天数 - 2 以后的数据 （因为是保存2天的数据））
	nowHour = cDateTime.Hour()
	global ReturnDB
	if ReturnDB is False:
		print "GE_EXC, ChaosDivinityControl AfterNewHour error not ReturnDB"
		#数据没有载回, 尝试再次载入
		InitGetRank()
		return
	
	if nowHour == 0:
		#0点的时候只发奖，操作数据库数据，逻辑进程自己把今天的数据拷贝到“昨天”的数据里面
		NewDayRewardRoles()
	else:
		#向逻辑进程请求数据,并且进行排序，写入数据库，把最新的排序更新到逻辑进程
		RequestLogicRank()

def LoginRequestRank(sessionid, msg):
	'''
	#逻辑进程主动请求跨服排行榜数据
	@param sessionid:
	@param msg
	'''
	global ReturnDB
	if not ReturnDB:
		#控制进程当前还没有从DB载回数据，等待数据载回来再发过去
		return

	global RankCache,RankOldCache,RankReward
	ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_SyncChaosDivinityAllRank, (RankCache,RankOldCache,RankReward))

def OnRanKFinished():
	'''
	'''
	global ReturnDB
	if ReturnDB is False:
		print "GE_EXC, ChaosDivinityControl AfterNewHour error not ReturnDB"
		#数据没有载回, 尝试再次载入
		InitGetRank()
		return

	#向逻辑进程请求数据,并且进行排序，写入数据库，把最新的排序更新到逻辑进程
	RequestLogicRank()

if "_HasLoad" not in dir():
	if Environment.HasControl:
		LoadRankReward()
		InitGetRank()
		cComplexServer.RegAfterNewHourCallFunction(AfterNewHour)
		cComplexServer.RegDistribute(PyMessage.Control_ChaosDivinityLogicRequest, LoginRequestRank)

		Cron.CronDriveByMinute((2038, 1, 1), OnRanKFinished, H="H == 23", M="M == 50")
