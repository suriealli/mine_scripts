#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Control.GlobalControl.Game2048RankControl")
#===============================================================================
# 注释 @author: GaoShuai 2015
#===============================================================================

import cComplexServer
import cDateTime
import Environment
import DynamicPath
from ComplexServer.Log import AutoLog
from Util.File import TabFile
from Common.Message import PyMessage
from Common.Other import GlobalDataDefine
from ComplexServer.API import GlobalHttp
from ComplexServer.Plug.Control import ControlProxy
from Control import ProcessMgr
from Game.Role.Mail import EnumMail
from Common.Other import GlobalPrompt

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("2048Game")
	RETURN_DB = False						#数据载入是否成功
	
	Game2048RewardDict = {}
	
	#总逻辑进程数量
	TOTAL_LOGIC_CNT = 0
	
	LOGIC_GAME2048_RANK_DICT = {}		#逻辑进程宝石2048榜缓存数据{服务器ID --> [[累计消耗神石, 玩家ID, 玩家名, 等级, 服务器名]]}
	
	GAME2048_TODAY_RANK_CACHE = []		#今日宝石2048榜缓存（用于全逻辑服排行榜排序）
	GAME2048_YESTERDAY_RANK_CACHE = []	#昨日宝石2048榜缓存（用于全逻辑服排行榜排序）
	
#===============================================================================
# 
#===============================================================================
def InitGetRankEx():
	#向数据库请求载入排行榜数据
	todayKey = GlobalDataDefine.Game2048TodayRankKey
	yesterdayKey = GlobalDataDefine.Game2048YesterdayRankKey
	GlobalHttp.GetGlobalDataByKeys([todayKey, yesterdayKey], OnGetGame2048RankBack, (todayKey, yesterdayKey))

def OnGetGame2048RankBack(response, regparam):
	#数据返回了
	if response is None:
		#自返回
		print 'GE_EXC, response is None OnGetGame2048RankBack'
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
	global GAME2048_TODAY_RANK_CACHE
	global GAME2048_YESTERDAY_RANK_CACHE
	
	#重新排序, 先排得分, 再排角色ID
	nowRank.sort(key=lambda it:(it[1], -it[0]), reverse=True)
	oldRank.sort(key=lambda it:(it[1], -it[0]), reverse=True)
	
	GAME2048_TODAY_RANK_CACHE = nowRank
	GAME2048_YESTERDAY_RANK_CACHE = oldRank

def RequestLogicRank():
	#向所有的逻辑进程获取排行榜数据
	global TOTAL_LOGIC_CNT
	TOTAL_LOGIC_CNT = len(ProcessMgr.ControlProcesssSessions)
	for sessionid, cp in ProcessMgr.ControlProcesssSessions.iteritems():
		if cp.processid >= 30000:
			#跨服服务器不处理
			TOTAL_LOGIC_CNT -= 1
			continue
		ControlProxy.SendLogicMsgAndBack(sessionid, PyMessage.Control_RequestLogicGame2048Rank, None, LogicBackRank, sessionid)
	
def LogicBackRank(callargv, regparam):
	#逻辑进程返回或者自返回
	global TOTAL_LOGIC_CNT
	TOTAL_LOGIC_CNT -= 1
	
	if callargv:
		global LOGIC_GAME2048_RANK_DICT
		processId, logicZumaUnionRankList = callargv
		LOGIC_GAME2048_RANK_DICT[processId] = logicZumaUnionRankList
		
	if TOTAL_LOGIC_CNT == 0:
		#所有的逻辑进程已经返回了排行榜,对排行榜进行排序,然后更新到数据库
		SortAndUpdateRank()
	elif TOTAL_LOGIC_CNT < 0:
		print "GE_EXC, error in Game2048RankControl RequestBack (%s)" % TOTAL_LOGIC_CNT
	
def SortAndUpdateRank():
	#更新数据库中的排行榜数据
	global GAME2048_TODAY_RANK_CACHE
	GAME2048_TODAY_RANK_CACHE = []
	
	for l in LOGIC_GAME2048_RANK_DICT.itervalues():
		GAME2048_TODAY_RANK_CACHE.extend(l)
	if GAME2048_TODAY_RANK_CACHE:
		#先排得分, 再排角色ID
		GAME2048_TODAY_RANK_CACHE.sort(key=lambda it:(it[1], -it[0]), reverse=True)
		##只排前20名
		GAME2048_TODAY_RANK_CACHE = GAME2048_TODAY_RANK_CACHE[:20]
		GlobalHttp.SetGlobalData(GlobalDataDefine.Game2048TodayRankKey, (cDateTime.Days(), GAME2048_TODAY_RANK_CACHE))
	
	
	if cDateTime.Hour() == 0:
		SyncAllLogic()
	else:
		#同步数据给所有的逻辑进程
		SyncAllLogicToday()
	
	
def SyncAllLogic():
	#同步最新的排行榜给所有的逻辑进程
	for processId in LOGIC_GAME2048_RANK_DICT.iterkeys():
		cp = ProcessMgr.ControlProcesssIds.get(processId)
		if not cp:
			if not Environment.IsDevelop:
				print "GE_EXC, Game2048RankControl SyncAllLogic not process sessionid (%s)" % processId
			continue
		sessionid = cp.session_id
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdateGame2048RankToLogic, (GAME2048_TODAY_RANK_CACHE, GAME2048_YESTERDAY_RANK_CACHE))
	
def SyncAllLogicToday():
	#同步当天最新的排行榜给所有的逻辑进程
	global GAME2048_TODAY_RANK_CACHE
	for processId in LOGIC_GAME2048_RANK_DICT.iterkeys():
		cp = ProcessMgr.ControlProcesssIds.get(processId)
		if not cp:
			if not Environment.IsDevelop:
				print "GE_EXC, Game2048RankControl SyncAllLoginToday not process sessionid (%s)" % processId
			continue
		sessionid = cp.session_id
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdateGame2048RankToLogic_T, GAME2048_TODAY_RANK_CACHE)

#===============================================================================
# 时间
#===============================================================================
def AfterNewMinute():
	#每一个整点向所有的逻辑进程请求每一个服务器的前20名玩家数据，等待回调并且记录数据
	#如果有某些逻辑进程没有返回或者其他原因导致了这个回调是自回调的。这个时候，就会使用上一个小时
	#的旧数据代替这个一个服的数据。
	
	#所有的回调都完毕后，触发对这些玩家数据排序出前20名。并且http请求更新到数据库
	#（缺数据清理规则，数据中可能要存储天数的时间戳，清理天数 - 2 以后的数据 （因为是保存2天的数据））
	if not RETURN_DB:
		#数据没有载回, 尝试再次载入
		InitGetRankEx()
		return
	
	nowMinute = cDateTime.Minute()
	nowHour = cDateTime.Hour()
	
	if nowMinute not in (0, 30, 58):
		#0, 30, 58这三个时间点可能触发向逻辑进程请求数据
		return
	if nowMinute == 58 and nowHour != 23:
		#58分的时候只有是23点才会向逻辑进程请求数据
		return
	
	if nowHour == 0 and nowMinute == 0:
		#0点0分的时候只发奖，操作数据库数据，逻辑进程自己把今天的数据拷贝到“昨天”的数据里面
		Game2048RankReward()
		SyncAllLogic()
	else:
		#向逻辑进程请求数据,并且进行排序，写入数据库，把最新的排序更新到逻辑进程
		RequestLogicRank()

def Game2048RankReward():
	#处理排行榜
	global GAME2048_YESTERDAY_RANK_CACHE, GAME2048_TODAY_RANK_CACHE
	GAME2048_YESTERDAY_RANK_CACHE = GAME2048_TODAY_RANK_CACHE
	GAME2048_TODAY_RANK_CACHE = []
	#这里要修改日志的定义
	transaction = AutoLog.traGame2048Reward
	maildatas = []
	for index, rd in enumerate(GAME2048_YESTERDAY_RANK_CACHE):
		rank = index + 1
		roleid = rd[0]
		rewards = Game2048RewardDict.get(rank)
		if not rewards:
			#只排前20名
			print "GE_EXC, can't find the reward, where index = %s and roleid = %s" % (rank, roleid)
			continue
		mailData = {EnumMail.EnumItemsKey:rewards}
		rolemaildata = (roleid, GlobalPrompt.Game2048Title, GlobalPrompt.Sender, GlobalPrompt.Game2048Content % rank, transaction, mailData)
		maildatas.append(rolemaildata)
	#发送邮件奖励
	GlobalHttp.SendRoleMail(maildatas)
		
#===============================================================================
# 逻辑服请求
#===============================================================================
def LogicRequestGame2048Rank(sessionid, msg):
	'''
	#逻辑进程主动请求宝石2048榜数据
	@param sessionid:
	@param msg:(进程ID， 积分排行榜)
	'''
	global LOGIC_GAME2048_RANK_DICT
	#先记录逻辑进程的区域类型
	
	processId, rank = msg
	LOGIC_GAME2048_RANK_DICT[processId] = rank
	
	if not RETURN_DB:
		#控制进程当前还没有从DB载回数据，等待数据载回来再发过去
		return
	
	ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdateGame2048RankToLogic, (GAME2048_TODAY_RANK_CACHE, GAME2048_YESTERDAY_RANK_CACHE))


class finalsRewardConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("2048Reward.txt")
	def __init__(self):
		self.rank = self.GetEvalByString
		self.rewardItems = self.GetEvalByString


def LoadfinalsRewardConfig():
	global Game2048RewardDict
	for cfg in finalsRewardConfig.ToClassType(False):
		minLev, maxLev = cfg.rank
		for level in range(minLev, maxLev + 1):
			if level in Game2048RewardDict:
				print "GE_EXC, repeat index(%s) in Game2048RewardDict" % level
			Game2048RewardDict[level] = cfg.rewardItems


if "_HasLoad" not in dir():
	if Environment.HasControl and (Environment.EnvIsQQ() or Environment.IsDevelop or Environment.EnvIsFT() or Environment.EnvIsTK()):
		LoadfinalsRewardConfig()
		InitGetRankEx()
		cComplexServer.RegAfterNewMinuteCallFunction(AfterNewMinute)
		cComplexServer.RegDistribute(PyMessage.Control_RequestControlGame2048Rank, LogicRequestGame2048Rank)
		
