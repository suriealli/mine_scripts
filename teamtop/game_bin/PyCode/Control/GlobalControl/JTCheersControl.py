#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Control.GlobalControl.JTCheersControl")
#===============================================================================
# 跨服争霸赛控制模块（活动开启时间计算得来, 不是读表控制）
#===============================================================================
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
from Game.JT import JTDefine

#战队人气（喝彩次数）
CheersIndex = 10
#回应次数
ResponsesIndex = 11
#积分
ScoreIndex = 4

if "_HasLoad" not in dir():
	IsStart = False
	IsEnd = False
	
	ActiveID = 0
	
	#总的逻辑进程个数
	TotalLogicCnt = 0
	
	#奖池神石数
	TotalPoolValue = 0
	#临时奖池神石数（统计的时候要用的）
	TotalPoolValueEx = 0
	
	#记录请求数据次数
	GetDataCnt = 0
	
	#巅峰战队战队喝彩数据
	TeamCheersDataDict = {}
	#临时巅峰战队喝彩数据
	TeamCheersDataDictEx = {}
	
	#收集数据的时候返回的进程id集合
	BackProcessIdSet = set()
	
	IsTeamDataReturn = False
	FirstTeamId = 0
	
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("JT")
	
	JTCheersPoolIncPercent_Dict = {}
	JTCheersPoolValue_List = []
	
#===============================================================================
# 配置
#===============================================================================
class JTCheersPoolConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("JTCheersPoolIncPercent.txt")
	def __init__(self):
		self.poolValue = int
		self.incPercent = int
	
def LoadTurnTableActiveConfig():
	global JTCheersPoolIncPercent_Dict, JTCheersPoolValue_List
	
	for cfg in JTCheersPoolConfig.ToClassType(False):
		if cfg.poolValue in JTCheersPoolIncPercent_Dict:
			print "GE_EXC, repeat poolValue %s in JTCheersPoolIncPercent_Dict" % cfg.poolValue
			continue
		JTCheersPoolIncPercent_Dict[cfg.poolValue] = cfg
		JTCheersPoolValue_List.append(cfg.poolValue)
	JTCheersPoolValue_List = list(set(JTCheersPoolValue_List))
	JTCheersPoolValue_List.sort()
	
#===============================================================================
# 获取巅峰战队数据
def GetTeamData(callargv=None, regparam=None):
	#这里随机向一个非跨服逻辑进程请求数据
	for sessionid, cp in ProcessMgr.ControlProcesssSessions.iteritems():
		if cp.processid >= 30000:
			continue
		ControlProxy.SendLogicMsgAndBack(sessionid, PyMessage.Control_GetGlobalZBTeamData, None, LogicBackTeamData, sessionid)
		break
	
def LogicBackTeamData(callargv, regparam):
	#跨服逻辑进程返回数据
	global TeamCheersDataDict, GetDataCnt
	teamDataList = callargv
	
	if not teamDataList:
		print 'GE_EXC, JTCheersControl LogicBackTeamData empty data'
		#5分钟后再次请求数据
		GetDataCnt += 1
		if GetDataCnt >= 5:
			#5次后还没拿到数据就算了
			return
		cComplexServer.RegTick(300, GetTeamData, None)
		return
	
	global IsTeamDataReturn
	IsTeamDataReturn = True
	
	#处理数据
	TeamCheersDataDict = {teamData[2] : teamData for teamData in teamDataList}
	for teamData in TeamCheersDataDict.values():
		teamData.extend([0, 0])
	
	#活动开始
	StartCheers()
	
def LogicBackFirstTeamData(callargv, regparam):
	#返回冠军队伍id
	global FirstTeamId
	FirstTeamId = callargv
	
	if not FirstTeamId:
		print 'GE_EXC, JTCheersControl LogicBackFirstTeamData get empty data'
		#5分钟后再次请求冠军数据
		cComplexServer.RegTick(300, LogicBackFirstTeamData, None)
		return
	
	#活动结束
	End()

def StartCheers():
	#开始
	#检查数据
	GlobalHttp.GetGlobalData(GlobalDataDefine.JTCheersPoolValue, OnGetPoolValueBack)
	GlobalHttp.GetGlobalData(GlobalDataDefine.JTCheersTeamData, OnGetCheersTeamDataBack)
	#同步
	SyncAllLogic()
#===============================================================================
#===============================================================================
# 活动开关
#===============================================================================
def TryStart():
	#起服的时候尝试判断活动是否开启
	global IsStart, IsEnd, ActiveID, TeamCheersDataDict
	IsStart, IsEnd, ActiveID = JTDefine.GetZBStartCnt()
	
	if not IsEnd:
		return
	
	#请求数据
	GetTeamData()
	
def HalfHour():
	global IsStart, IsTeamDataReturn
	
	if not IsStart:
		return
	
	if not IsTeamDataReturn:
		#之前的数据没有载回来, 再次尝试载回数据
		GetTeamData()
	else:
		#每半个小时同步一次数据
		RequestLogicData()
	
def AfterNewDay():
	#每天结束后尝试开启或关闭活动
	global IsStart, IsEnd, ActiveID, TeamCheersDataDict, TotalPoolValue
	
	isStart, isEnd, ActiveID = JTDefine.GetZBStartCnt()
	
	if (not IsStart) and isStart:
		#活动之前没开, 现在开了
		GetTeamData()
	
	if IsEnd and (isEnd is False):
		#活动之前开的, 现在关了
		#先要拿到第一名的队伍id
		for sessionid, cp in ProcessMgr.ControlProcesssSessions.iteritems():
			if cp.processid >= 30000:
				continue
			ControlProxy.SendLogicMsgAndBack(sessionid, PyMessage.Control_GetGlobalZBFirstTeamData, None, LogicBackFirstTeamData, sessionid)
			break
	
	IsStart, IsEnd = isStart, isEnd
	
def End():
	#计算奖池神石数
	global TotalPoolValue, JTCheersPoolValue_List, TeamCheersDataDict, GetDataCnt
	
	GetDataCnt = 0
	
	if not TeamCheersDataDict:
		print 'GE_EXC, JTCheersControl End TeamCheersDataDict is empty'
		return
	
	#排序
	teamDataList = TeamCheersDataDict.items()
	teamDataList.sort(key = lambda x : (x[1][CheersIndex], x[1][ResponsesIndex], x[1][ScoreIndex], x[0]), reverse=True)
	#获取喝彩第一战队id
	firstTeamID = teamDataList[0][0]
	
	#获取冠军队伍id
	global FirstTeamId
	if not FirstTeamId:
		print 'GE_EXC, JTCheersControl End FirstTeamId error'
	
	percent = 0
	#预测对了
	if firstTeamID == FirstTeamId:
		percent = 2500
	
	cfg = JTCheersPoolIncPercent_Dict.get(GetCloseValue(TotalPoolValue, JTCheersPoolValue_List))
	if cfg:
		percent += cfg.incPercent
	else:
		percent += 10000
	
	afterIncPoolValue = percent * TotalPoolValue / 10000
	
	TotalPoolValue = afterIncPoolValue
	
	#通知逻辑进程发放奖励
	#计算喝彩次数
	
	ServerCheersCnt = 0
	for teamData in TeamCheersDataDict.itervalues():
		ServerCheersCnt += teamData[CheersIndex]
	
	if not ServerCheersCnt:
		print 'GE_EXC, JTCheersControl ServerCheersCnt is zero'
	else:
		SendReward(ServerCheersCnt)
		
		print 'BLUE, TotalPoolValue %s, totalCheersCnt %s' % (TotalPoolValue, ServerCheersCnt)
	
	#清理数据
	TotalPoolValue = 0
	TeamCheersDataDict = {}
	GlobalHttp.SetGlobalData(GlobalDataDefine.JTCheersPoolValue, ())
	GlobalHttp.SetGlobalData(GlobalDataDefine.JTCheersTeamData, ())
	
	SyncAllLogic()
	
def SendReward(ServerCheersCnt):
	#通知逻辑进程发放奖励
	global TotalPoolValue
	for sessionid, cp in ProcessMgr.ControlProcesssSessions.iteritems():
		if cp.processid >= 30000:
			continue
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_GetGlobalZBCheersReward, (TotalPoolValue, ServerCheersCnt))
	
def GetCloseValue(value, valueList):
	tmpValue = 0
	for i in valueList:
		if i > value:
			return tmpValue
		tmpValue = i
	return 0

def RequestLogicData():
	#向逻辑进程收集数据
	global TotalLogicCnt
	TotalLogicCnt = len(ProcessMgr.ControlProcesssSessions)
	
	for sessionid, cp in ProcessMgr.ControlProcesssSessions.iteritems():
		if cp.processid >= 30000:
			#跨服服务器不处理
			TotalLogicCnt -= 1
			continue
		ControlProxy.SendLogicMsgAndBack(sessionid, PyMessage.Control_RequestLogicZBCheersData, None, LogicBackData, sessionid)

def LogicBackData(callargv, regparam):
	#逻辑进程返回或者自返回
	global TotalLogicCnt, TotalPoolValue, TotalPoolValueEx, ActiveID, BackProcessIdSet, TeamCheersDataDict, TeamCheersDataDictEx
	TotalLogicCnt -= 1
	
	if callargv:
		#进程id, 奖池神石数, 喝彩次数
		processId, poolValue, cheersDict = callargv
		
		if processId in BackProcessIdSet:
			#防止重复计算
			return
		
		#奖池收益 = 逻辑进程奖池神石数 - 上次同步的奖池神石数
		TotalPoolValueEx = TotalPoolValueEx + poolValue - TotalPoolValue
		
		#喝彩次数计算
		for teamId, teamData in TeamCheersDataDict.iteritems():
			if teamId not in cheersDict:
				print 'GE_EXC, LogicBackPoolValue return error data %s' % teamId
				continue
			
			#旧的喝彩次数
			oldCheersCnt, oldResponsesCnt = teamData[CheersIndex], teamData[ResponsesIndex]
			
			#收集的逻辑进程喝彩次数
			newCheersCnt, newResponsesCnt = cheersDict[teamId][CheersIndex], cheersDict[teamId][ResponsesIndex]
			
			if teamId not in TeamCheersDataDictEx:
				#初始化喝彩次数盈亏
				TeamCheersDataDictEx[teamId] = [0, 0]
			
			#计算盈亏
			if newCheersCnt < oldCheersCnt:
				print 'GE_EXC, LogicBackPoolValue return new value < old value'
			else:
				TeamCheersDataDictEx[teamId][0] += newCheersCnt - oldCheersCnt
				TeamCheersDataDictEx[teamId][1] += newResponsesCnt - oldResponsesCnt
			
			
	if TotalLogicCnt == 0:
		#所有逻辑进程都已经返回了
		
		#更新全服奖池数据
		TotalPoolValue += TotalPoolValueEx
		TotalPoolValueEx = 0
		
		#更新战队喝彩数据
		for teamId, cheersData in TeamCheersDataDictEx.iteritems():
			teamData = TeamCheersDataDict.get(teamId)
			if not teamData:
				print 'GE_EXC, LogicBackPoolValue error %s' % teamId
				continue
			teamData[CheersIndex] += cheersData[0]
			teamData[ResponsesIndex]+= cheersData[1]
			
			TeamCheersDataDict[teamId] = teamData
		
		TeamCheersDataDictEx = {}
		
		#清理返回的进程id集合
		BackProcessIdSet = set()
		
		#保存全局数据
		GlobalHttp.SetGlobalData(GlobalDataDefine.JTCheersPoolValue, (ActiveID, TotalPoolValue))
		GlobalHttp.SetGlobalData(GlobalDataDefine.JTCheersTeamData, (ActiveID, TeamCheersDataDict))
		
		#同步所有逻辑进程
		SyncAllLogic()
	elif TotalLogicCnt < 0:
		print "GE_EXC, error in TurnTableControl RequestBack (%s)" % TotalLogicCnt
	
def SyncAllLogic():
	#同步所有逻辑进程
	global TotalPoolValue, TeamCheersDataDict
	for sessionid, cp in ProcessMgr.ControlProcesssSessions.iteritems():
		if cp.processid >= 30000:
			continue
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataZBCheersDataToLogic, (TotalPoolValue, TeamCheersDataDict))
	
def OnGetPoolValueBack(response, regparam):
	if response is None:
		return
	#检查数据
	CheckPoolValue(response)
	
def OnGetCheersTeamDataBack(response, regparam):
	if response is None:
		#注意这个和上面一个函数不一样
		return
	CheckCheersTeamData(response)
	
def CheckPoolValue(response):
	global ActiveID, TotalPoolValue
	
	if not response:
		#初始化数据格式
		activeID, poolValue = -1, 0
	else:
		activeID, poolValue = response
	
	if activeID != ActiveID:
		#活动id不一样, 清理数据
		TotalPoolValue = 0
		GlobalHttp.SetGlobalData(GlobalDataDefine.JTCheersPoolValue, (ActiveID, TotalPoolValue))
	else:
		TotalPoolValue = poolValue
	
def CheckCheersTeamData(response):
	global ActiveID, TeamCheersDataDict
	
	if not response:
		activeID, teamData = -1, {}
	else:
		activeID, teamData = response
	
	if activeID != ActiveID:
		#新的活动了, 更新保存的巅峰战队数据
		GlobalHttp.SetGlobalData(GlobalDataDefine.JTCheersTeamData, (ActiveID, TeamCheersDataDict))
	else:
		TeamCheersDataDict = teamData
	
	#这份数据不需要同步
	
def LoginRequestGlobalData(sessionid, msg):
	#逻辑进程向控制进程请求数据
	global TotalPoolValue, TeamCheersDataDict
	if not TotalPoolValue:
		#数据还没有载回来, 等载回来的时候再同步给逻辑进程
		return
	
	ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataZBCheersDataToLogic, (TotalPoolValue, TeamCheersDataDict))
	
if "_HasLoad" not in dir():
	if Environment.HasControl and (Environment.EnvIsQQ() or Environment.EnvIsFT()):
		LoadTurnTableActiveConfig()
		
		TryStart()
		
		Cron.CronDriveByMinute((2038, 1, 1), HalfHour, M="M == 30 or M == 0")
		
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
		
		cComplexServer.RegDistribute(PyMessage.Control_GetGlobalZBCheersData, LoginRequestGlobalData)
		
