#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Control.GlobalControl.CatchingFishControl")
#===============================================================================
# 捕鱼活动的控制进程
#===============================================================================
import time
import datetime
import cDateTime
import cComplexServer
import Environment
import DynamicPath
from Util.File import TabFile
from Control import ProcessMgr
from Common.Message import PyMessage
from Common.Other import GlobalDataDefine
from ComplexServer.Time import Cron
from ComplexServer.Plug.Control import ControlProxy
from ComplexServer.API import GlobalHttp
from ComplexServer.Log import AutoLog
from Game.Role.Mail import EnumMail
from Common.Other import GlobalPrompt

if "_HasLoad" not in dir():
	IsStart = False
	ActiveID = 0
	TotalLogicCnt = 0						#逻辑进程总数
	CatchingFishRecordList = []				#跨服积分排行榜
	LOGIC_CATCH_RANK_DICT = {}				#逻辑进程捕鱼缓存数据{服务器ID:[(积分，角色id, 角色名, 等级, 服务器名)]}
	CatchingFishReward = {}					#捕鱼积分奖励字典
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("CatchingFish")
	YestDayCatchingFishRecordList = []		#昨天跨服积分排行榜


class CatchingFishActive(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("CatchingFishActive.txt")
	def __init__(self):
		self.activeID = int
		self.beginTime = eval
		self.endTime = eval
	def Active(self):
		beginTime = int(time.mktime(datetime.datetime(*self.beginTime).timetuple()))
		endTime = int(time.mktime(datetime.datetime(*self.endTime).timetuple()))
		nowTime = cDateTime.Seconds()
		if beginTime <= nowTime < endTime:
			#激活
			OpenActive(None, self.activeID)
			cComplexServer.RegTick(endTime - nowTime + 60, CloseActive)
		elif nowTime < beginTime:
			#注册一个tick激活
			cComplexServer.RegTick(beginTime - nowTime, OpenActive, self.activeID)
			cComplexServer.RegTick(endTime - nowTime +60, CloseActive)
	

def LoadCatchingFishActive():
	for cfg in CatchingFishActive.ToClassType(False):
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in TurnTableActiveConfig"
		cfg.Active()
#================================================================================
#控制活动的开启
#================================================================================
def OpenActive(callArgv, regparam):
	global IsStart, ActiveID, CatchingFishRecordList, LOGIC_CATCH_RANK_DICT, TotalLogicCnt
	if IsStart:
		print 'GE_EXC, repeat start CatchingFishActive'
	IsStart = True
	ActiveID = regparam
	CatchingFishRecordList = []
	LOGIC_CATCH_RANK_DICT = {}
	TotalLogicCnt = 0
	#活动开启的时候载回数据、初始化数据、同步数据
	GlobalHttp.GetGlobalData(GlobalDataDefine.CatchingFishYestDayRankDateKey, CatchingFishYestDayDateBack)
	GlobalHttp.GetGlobalData(GlobalDataDefine.CatchingFishRankDataKey, CatchingFishRankDataBack)
	
def CloseActive(callArgv, regparam):
	global IsStart, CatchingFishRecordList, LOGIC_CATCH_RANK_DICT
	if not IsStart:
		print 'GE_EXC, repeat end CatchingFishActive'
	IsStart = False
	CatchingFishRecordList = []
	LOGIC_CATCH_RANK_DICT = {}

#================================================================================
#积分排行榜
#================================================================================
def CatchingFishRankDataBack(response, finalsKey):
	
	#数据返回了
	if not response :
		#自返回
		return
	IsToday, dataList = response
	#设置缓存数据
	global CatchingFishRecordList
	if response != 0 and IsToday == cDateTime.Days():
		CatchingFishRecordList = dataList
	global RETURN_DB
	RETURN_DB = True
	#同步数据给所有的逻辑进程
	SyncAllLogic()

#得到数据库里最新的排行榜数据
def GetCatchingFishRankDate(response, finalsKey):
	#数据返回了
	if not response :
		#自返回
		return
	IsToday, dataList = response
	if response != 0 and IsToday == cDateTime.Days():
		return dataList
	

#昨天的排行榜数据更新
def CatchingFishYestDayDateBack(response, finalsKey):
	#数据返回了
	if response is None:
		#自返回
		return
	YestDay, dataList = response
	#设置缓存数据
	global YestDayCatchingFishRecordList
	if response != 0 and YestDay + 1 == cDateTime.Days():
		YestDayCatchingFishRecordList = dataList
	

def GetCalculusList():
	#向所有的逻辑进程获取捕积分数据
	global IsStart, TotalLogicCnt
	if not IsStart: return
	if cDateTime.Hour() == 0 and cDateTime.Minute() == 0 :
		CatchingFishRankReward()
		return
	TotalLogicCnt = len(ProcessMgr.ControlProcesssSessions)
	for sessionid, cp in ProcessMgr.ControlProcesssSessions.iteritems():
		if cp.processid >= 30000:
			#跨服服务器不处理
			TotalLogicCnt -= 1
			continue
		ControlProxy.SendLogicMsgAndBack(sessionid, PyMessage.CatchingFish_Calculs_FromLogic, None, LogicBackCalculus, sessionid)


def LogicBackCalculus(callargv, regparam):
	'''
	逻辑进程的数据载回
	'''
	global TotalLogicCnt
	TotalLogicCnt-=1
	if callargv:
		global LOGIC_CATCH_RANK_DICT
		processId, finalsRankList = callargv
		LOGIC_CATCH_RANK_DICT[processId] = finalsRankList
	if TotalLogicCnt == 0 :
		#所有的逻辑进程已经返回了排行榜,对排行榜进行排序,然后更新到数据库
		SortAndUpdateRank()
	elif TotalLogicCnt < 0 :
		print "GE_EXC, error in CatchingFishControl LogicBackCalculus (%s)" % TotalLogicCnt
	

def SortAndUpdateRank():
	'''
	更新数据库的排行榜
	'''
	global LOGIC_CATCH_RANK_DICT,CatchingFishRecordList
	CatchingFishRecordList = []
	for l in LOGIC_CATCH_RANK_DICT.itervalues():
		if not l :
			continue
		CatchingFishRecordList.extend(l)
	#排序，先积分后id
	if CatchingFishRecordList :
		CatchingFishRecordList.sort(key=lambda x:(-x[0], -x[1]))
		CatchingFishRecordList = CatchingFishRecordList[:10]
		GlobalHttp.SetGlobalData(GlobalDataDefine.CatchingFishRankDataKey,(cDateTime.Days(), CatchingFishRecordList))
	
	if cDateTime.Hour() == 23 and cDateTime.Minute() >= 55 :
		return
	#同步数据给所有的逻辑进程
	SyncAllLogic()
	

def SyncAllLogic():
	'''
	控制进程同步逻辑进程
	'''
	global CatchingFishRecordList
	for sessionid, cp in ProcessMgr.ControlProcesssSessions.iteritems():
		if cp.processid >= 30000:
			#跨服服务器不处理
			continue
		ControlProxy.SendLogicMsg(sessionid, PyMessage.CatchingFish_CalculusToLogicControl, (CatchingFishRecordList, YestDayCatchingFishRecordList))

def UpdateYestDay():
	global YestDayCatchingFishRecordList
	if not YestDayCatchingFishRecordList :
		return
	GlobalHttp.SetGlobalData(GlobalDataDefine.CatchingFishYestDayRankDateKey,(cDateTime.Days(), YestDayCatchingFishRecordList))

def CatchingFishRankReward():
	'''
	发送奖励
	'''
	global CatchingFishReward,CatchingFishRecordList, YestDayCatchingFishRecordList
	transaction = AutoLog.traCatchingFishMailReward
	maildatas = []
	#YestDayCatchingFishRecordList = GlobalHttp.GetGlobalData(GlobalDataDefine.CatchingFishRankDataKey, GetCatchingFishRankDate)
	YestDayCatchingFishRecordList = CatchingFishRecordList
	if len(CatchingFishRecordList) > 10 :
		print "GE_EXC, length is out of CatchingFishRankReward in CatchingFishControl"
	for index, rd in enumerate(CatchingFishRecordList):
		rank = index + 1
		roleid = rd[1]
		roleLevel = rd[3]
		minlevel = 0
		for cf in CatchingFishReward.keys() :
			if cf[0][0] <= rank and rank <= cf[0][1] :
				ranks = cf[0]
			if roleLevel < cf[1] :
				continue
			if minlevel <= cf[1] :
				minlevel = cf[1]
		rewardcf = CatchingFishReward.get((ranks, minlevel))
		if not rewardcf :
			print "GE_EXC, can't find the reward, where index = %s and level = %s in CatchingFishRankReward"  % (rank, minlevel)
			continue
		reward = rewardcf.itemsReward
		mailData = {EnumMail.EnumItemsKey:reward}
		rolemaildata = (roleid, GlobalPrompt.CatchingFishAwardTitle, GlobalPrompt.Sender, GlobalPrompt.CatchingFishAwardContent % rank, transaction, mailData)
		maildatas.append(rolemaildata)
		
	if not maildatas :
		return
	#发送邮件奖励
	GlobalHttp.SendRoleMail(maildatas)
	CatchingFishRecordList = []
	UpdateYestDay()
	SyncAllLogic()
#===============================================
#载入奖励配置表
#===============================================
class CatchingReward(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("CatchingFishAward.txt")
	def __init__(self):
		self.rank = self.GetEvalByString
		self.MinLevel = int
		self.itemsReward = self.GetEvalByString
		

def LoadCatchingReward():
	global CatchingFishReward
	for cf in CatchingReward.ToClassType(False) :
		CatchingFishReward[(cf.rank,cf.MinLevel)] = cf
		

def RequestGlobalCalculusList(sessionid, msg):
	'''
	#逻辑进程主动请求捕鱼达人积分排行数据
	@param sessionid:
	@param msg:(进程ID， 新答题决赛排行榜)
	'''
	#逻辑进程向控制进程请求数据
	global CatchingFishRecordList
	ControlProxy.SendLogicMsg(sessionid, PyMessage.CatchingFish_CalculusToLogicControl, (CatchingFishRecordList, YestDayCatchingFishRecordList))
	
	
if "_HasLoad" not in dir():
	if Environment.HasControl:
		LoadCatchingFishActive()
		LoadCatchingReward()
		Cron.CronDriveByMinute((2038, 1, 1), GetCalculusList,  H="H == 23", M="M == 55")
		Cron.CronDriveByMinute((2038, 1, 1), GetCalculusList,   M="M == 30 or M == 0")
		cComplexServer.RegDistribute(PyMessage.CatchingFish_Calculus_FromControl, RequestGlobalCalculusList)
