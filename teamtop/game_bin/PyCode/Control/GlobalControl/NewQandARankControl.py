#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Control.GlobalControl.NewQandARankControl")
#===============================================================================
# 新答题活动跨服排行控制 @author: Administrator 2015
#===============================================================================
import cComplexServer
import Environment
import DynamicPath
from World import Define
from Util.File import TabFile
from ComplexServer.Plug.Control import ControlProxy
from ComplexServer.Log import AutoLog
from ComplexServer.Time import Cron
from Common.Other import GlobalPrompt
from Common.Message import PyMessage
from Common.Other import GlobalDataDefine
from ComplexServer.API import GlobalHttp
from Control import ProcessMgr
from Game.Role.Mail import EnumMail


if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("XinDaTi")
	
	RETURN_DB = False					#数据载入是否成功
	#总逻辑进程数量
	TOTAL_LOGIC_CNT = 0
	
	LOGIC_FINALS_RANK_DICT = {}			#逻辑进程新答题缓存数据{服务器ID:[(得分，用时，结束时间，角色id, 角色名, 服务器名)]}
	
	FINALS_CONTROL_RANK_CACHE = []		#答题决赛排行榜(用于全逻辑服排行榜排序)
	
	finalsSpecialRewardDict = {}		#新答题决赛前50名奖励字典


def InitGetRankEx():
	#向数据库请求载入排行榜数据
	finalsKey = GlobalDataDefine.FinalsRankDataKey
	GlobalHttp.GetGlobalData(finalsKey, OnGetZumaUnionRankBack, None)


def OnGetZumaUnionRankBack(response, finalsKey):
	#数据返回了
	if response is None:
		#自返回
		return
	dataList = response
	#设置缓存数据
	global FINALS_CONTROL_RANK_CACHE
	
	if response != 0:
		FINALS_CONTROL_RANK_CACHE = dataList
	global RETURN_DB
	RETURN_DB = True
	#同步数据给所有的逻辑进程
	SyncAllLogic()


#===============================================================================
# 时间
#===============================================================================
def endQandAFinals():
	#在新答题活动决赛完成之后触发，向所有的逻辑进程请求每一个服务器的前50名玩家数据，等待回调并且记录数据
	#如果有某些逻辑进程没有返回或者其他原因导致了这个回调是自回调的。这个时候，就会使用上一次答题的旧数据代替这个服的数据。
	#所有的回调都完毕后，触发对这些玩家数据排序出前50名。并且http请求更新到数据库

	#向逻辑进程获取排行榜数据,并且进行排序，写入数据库，把最新的排序更新到逻辑进程
	global TOTAL_LOGIC_CNT
	TOTAL_LOGIC_CNT = len(ProcessMgr.ControlProcesssSessions)
	for sessionid, cp in ProcessMgr.ControlProcesssSessions.iteritems():
		if cp.processid >= 30000:
			#跨服服务器不处理
			TOTAL_LOGIC_CNT -= 1
			continue
		ControlProxy.SendLogicMsgAndBack(sessionid, PyMessage.Control_RequestFinalsRankData, None, LogicBackRank, sessionid)


def LogicBackRank(callargv, regparam):
	#逻辑进程返回或者自返回
	global TOTAL_LOGIC_CNT
	TOTAL_LOGIC_CNT -= 1
	
	if callargv:
		global LOGIC_FINALS_RANK_DICT
		processId, finalsRankList = callargv
		LOGIC_FINALS_RANK_DICT[processId] = finalsRankList
		
	if TOTAL_LOGIC_CNT == 0:
		#所有的逻辑进程已经返回了排行榜,对排行榜进行排序,然后更新到数据库
		SortAndUpdateRank()
	elif TOTAL_LOGIC_CNT < 0:
		print "GE_EXC, error in NewQandARankControl LogicBackRank (%s)" % TOTAL_LOGIC_CNT


def SortAndUpdateRank():
	#更新数据库中的排行榜数据
	global FINALS_CONTROL_RANK_CACHE, LOGIC_FINALS_RANK_DICT
	FINALS_CONTROL_RANK_CACHE = []
	
	for l in LOGIC_FINALS_RANK_DICT.itervalues():
		FINALS_CONTROL_RANK_CACHE.extend(l)
	
	if FINALS_CONTROL_RANK_CACHE:
		#重新排序, 得分，用时，结束时间，角色id
		FINALS_CONTROL_RANK_CACHE.sort(key=lambda x:(-x[0], x[1], x[2], x[3]))
		FINALS_CONTROL_RANK_CACHE = FINALS_CONTROL_RANK_CACHE[:50]
		GlobalHttp.SetGlobalData(GlobalDataDefine.FinalsRankDataKey, FINALS_CONTROL_RANK_CACHE)
	
	FinalsRankReward()
	#同步数据给所有的逻辑进程
	SyncAllLogic()


def SyncAllLogic():
	#同步最新排行榜给所有的逻辑进程
	for processId, cp in ProcessMgr.ControlProcesssIds.iteritems():
		if processId == Define.GetCrossID_2():
			continue
		if processId == Define.GetDefaultCrossID():
			continue
		sessionid = cp.session_id
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdateNewQandARank, FINALS_CONTROL_RANK_CACHE)


def FinalsRankReward():
	global FINALS_CONTROL_RANK_CACHE, finalsSpecialRewardDict
	
	transaction = AutoLog.traQuestionFinalsRankMailReward
	maildatas = []
	for index, rd in enumerate(FINALS_CONTROL_RANK_CACHE):
		rank = index + 1
		roleid = rd[3]
		if rank not in finalsSpecialRewardDict:
			print finalsSpecialRewardDict.keys()
		rewards = finalsSpecialRewardDict.get(rank)
		if not rewards:
			print "GE_EXC, can't find the reward, where index = %s and roleid = %s" % (rank, roleid)
			continue
		mailData = {EnumMail.EnumItemsKey:rewards}
		rolemaildata = (roleid, GlobalPrompt.FinalsRewardTitle_1, GlobalPrompt.Sender, GlobalPrompt.FinalsRewardContent_1 % rank, transaction, mailData)
		maildatas.append(rolemaildata)
		
	#发送邮件奖励
	GlobalHttp.SendRoleMail(maildatas)


class finalsRewardConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("finalsReward.txt")
	def __init__(self):
		self.rank = self.GetEvalByString
		self.itemsReward = self.GetEvalByString


def LoadfinalsRewardConfig():
	global finalsSpecialRewardDict
	for cfg in finalsRewardConfig.ToClassType(False):
		minLev, maxLev = cfg.rank
		if maxLev >= 51:
			continue
		for level in range(minLev, maxLev + 1):
			if level in finalsSpecialRewardDict:
				print "GE_EXC, repeat index(%s) in finalsSpecialRewardDict" % level
			finalsSpecialRewardDict[level] = cfg.itemsReward


def LogicRequestFinalsRank(sessionid, msg):
	'''
	#逻辑进程主动请求新答题决赛排行数据
	@param sessionid:
	@param msg:(进程ID， 新答题决赛排行榜)
	'''
	global FINALS_CONTROL_RANK_CACHE, LOGIC_FINALS_RANK_DICT
	#先记录逻辑进程的区域类型
	processId, rank = msg
	LOGIC_FINALS_RANK_DICT[processId] = rank
	
	if not RETURN_DB:
		#控制进程当前还没有从DB载回数据，重复调用数据载回来，再发过去
		InitGetRankEx()
		return
	
	ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdateNewQandARank, FINALS_CONTROL_RANK_CACHE)


if "_HasLoad" not in dir():
	if Environment.HasControl:
		LoadfinalsRewardConfig()
		InitGetRankEx()
		Cron.CronDriveByMinute((2038, 1, 1), endQandAFinals, w="w == 7", H="H == 16", M="M == 0")
		cComplexServer.RegDistribute(PyMessage.Control_LogicSendFinalsRankData, LogicRequestFinalsRank)
