#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.JT.JTCheers")
#===============================================================================
# 跨服争霸赛喝彩
#===============================================================================
import Environment
import cRoleMgr
from Common.Message import AutoMessage, PyMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Role.Data import EnumInt16
import cComplexServer
from ComplexServer.Plug.Control import ControlProxy
import cProcess
from Game.Persistence import Contain
from Game.Role.Mail import Mail
from ComplexServer.Log import AutoLog
from Game.Role import Event
from ComplexServer import Init
from Game.Activity.Title import Title
from Game.JT import JTDefine

CheersIndex = 10
ResponsesIndex = 11

if "_HasLoad" not in dir():
	#奖池神石数
	JTCheersPoolValue = AutoMessage.AllotMessage("JTCheersPoolValue", "跨服争霸赛喝彩奖池神石数")
	#服ID，服名，战队ID，战队名，战队积分，战队段位，战队数据，战队成员IDs，总战力， 排名
	#{队伍id:[服务器ID，服务器名字，队伍ID，队伍名字，积分，段位，成员数据，战队等级，胜率(万份比)，总战力，总排名, 战队人气, 回应次数],...}
	JTCheersTeamData = AutoMessage.AllotMessage("JTCheersTeamData", "跨服争霸赛喝彩战队数据")
	#喝彩次数
	JTCheersCntData = AutoMessage.AllotMessage("JTCheersCntData", "跨服争霸赛喝彩数量数据")
	
	JTCheersOneCheers_Log = AutoLog.AutoTransaction("JTCheersOneCheers_Log", "跨服争霸赛喝彩一次")
	JTCheersTenCheers_Log = AutoLog.AutoTransaction("JTCheersTenCheers_Log", "跨服争霸赛喝彩十次")
	JTCheersOneResponses_Log = AutoLog.AutoTransaction("JTCheersOneResponses_Log", "跨服争霸赛回应一次")
	JTCheersTenResponses_Log = AutoLog.AutoTransaction("JTCheersTenResponses_Log", "跨服争霸赛回应十次")
	JTCheersReward_Log = AutoLog.AutoTransaction("JTCheersReward_Log", "跨服争霸赛喝彩结束邮件奖励")
	
	IsStart = False
	IsEnd = False
	
	PoolValue = 0
	TeamDataDict = {}
	
	BroadRoleIDSet = set()
	
def RequestOpenPanel(role, msg):
	'''
	跨服争霸赛打开喝彩面板
	@param role:
	@param msg:
	'''
	global IsEnd, BroadRoleIDSet, JTCheers_Dict
	if not IsEnd: return
	
	if not JTCheers_Dict.returnDB:
		return
	
	if role.GetLevel() < EnumGameConfig.JTCheersMinLevel:
		return
	
	roleId = role.GetRoleID()
	if roleId not in BroadRoleIDSet:
		BroadRoleIDSet.add(roleId)
		
	global PoolValue, TeamDataDict
	role.SendObj(JTCheersPoolValue, PoolValue)
	role.SendObj(JTCheersTeamData, TeamDataDict)
	role.SendObj(JTCheersCntData, JTCheers_Dict.get(roleId, 0))
	
def RequestClosePanel(role, msg):
	'''
	跨服争霸赛关闭喝彩面板
	@param role:
	@param msg:
	'''
	global IsEnd, BroadRoleIDSet
	if not IsEnd: return
	
	roleId = role.GetRoleID()
	
	if roleId in BroadRoleIDSet:
		BroadRoleIDSet.discard(roleId)
	
def RequestCheers(role, msg):
	'''
	一次喝彩
	@param role:
	@param msg:战队id
	'''
	global IsStart
	if not IsStart:
		role.Msg(2, 0, GlobalPrompt.JTCheersEnd)
		return
	
	teamId = msg
	
	global TeamDataDict, PoolValue
	if teamId not in TeamDataDict:
		return
	
	if role.GetLevel() < EnumGameConfig.JTCheersMinLevel:
		return
	
	global JTCheers_Dict
	if not JTCheers_Dict.returnDB: return
	
	roleId = role.GetRoleID()
	nowCheersCnt = JTCheers_Dict.get(roleId, 0)
	
	if nowCheersCnt >= EnumGameConfig.JTCheersMaxCnt:
		return
	if role.GetUnbindRMB_Q() < EnumGameConfig.JTCheersCheersRMB:
		return
	
	with JTCheersOneCheers_Log:
		TeamDataDict[teamId][CheersIndex] += 1
		
		role.DecUnbindRMB_Q(EnumGameConfig.JTCheersCheersRMB)
		role.IncI16(EnumInt16.JTCheersCnt, 1)
		
		PoolValue += EnumGameConfig.JTCheersCheersRMB
	
	oldCheersCnt, oldRespCnt = TeamDataDict[teamId][CheersIndex], TeamDataDict[teamId][ResponsesIndex]
	
	if oldRespCnt >= EnumGameConfig.JTCheersTitleNeedPCnt and oldCheersCnt < EnumGameConfig.JTCheersTitleNeedCCnt and oldCheersCnt >= EnumGameConfig.JTCheersTitleNeedCCnt:
		#获得称号
		for roleId in TeamDataDict[teamId][7]:
			Title.AddTitle(roleId, EnumGameConfig.JTCheersTitle)
	
	nowCheersCnt += 1
	JTCheers_Dict[roleId] = nowCheersCnt
	JTCheers_Dict.changeFlag = True
	
	role.SendObj(JTCheersPoolValue, PoolValue)
	role.SendObj(JTCheersTeamData, TeamDataDict)
	role.SendObj(JTCheersCntData, nowCheersCnt)
	
	role.Msg(2, 0, GlobalPrompt.JTCheersOneSuc)
	
def RequestTenCheers(role, msg):
	'''
	十次喝彩
	@param role:
	@param msg:战队id
	'''
	global IsStart
	if not IsStart:
		role.Msg(2, 0, GlobalPrompt.JTCheersEnd)
		return
	
	teamId = msg
	
	global TeamDataDict
	if teamId not in TeamDataDict:
		return
	
	if role.GetLevel() < EnumGameConfig.JTCheersMinLevel:
		return
	
	global JTCheers_Dict
	if not JTCheers_Dict.returnDB: return
	
	roleId = role.GetRoleID()
	nowCheersCnt = JTCheers_Dict.get(roleId, 0)
	afterCheersCnt = nowCheersCnt + 10
	if afterCheersCnt > EnumGameConfig.JTCheersMaxCnt:
		return
	needRMB = EnumGameConfig.JTCheersCheersRMB * 10
	if role.GetUnbindRMB_Q() < needRMB:
		return
	
	global PoolValue
	with JTCheersTenCheers_Log:
		TeamDataDict[teamId][CheersIndex] += 10
		
		role.DecUnbindRMB_Q(needRMB)
		role.IncI16(EnumInt16.JTCheersCnt, 10)
		
		PoolValue += needRMB
	
	oldCheersCnt, oldRespCnt = TeamDataDict[teamId][CheersIndex], TeamDataDict[teamId][ResponsesIndex]
	
	if oldRespCnt >= EnumGameConfig.JTCheersTitleNeedPCnt and oldCheersCnt < EnumGameConfig.JTCheersTitleNeedCCnt and oldCheersCnt >= EnumGameConfig.JTCheersTitleNeedCCnt:
		#获得称号
		for roleId in TeamDataDict[teamId][7]:
			Title.AddTitle(roleId, EnumGameConfig.JTCheersTitle)
	
	JTCheers_Dict[roleId] = afterCheersCnt
	JTCheers_Dict.changeFlag = True
	
	role.SendObj(JTCheersPoolValue, PoolValue)
	role.SendObj(JTCheersTeamData, TeamDataDict)
	role.SendObj(JTCheersCntData, afterCheersCnt)
	
	role.Msg(2, 0, GlobalPrompt.JTCheersTenSuc)
	
def RequestResponses(role, msg):
	'''
	回应一次喝彩
	@param role:
	@param msg:
	'''
	global IsStart
	if not IsStart:
		role.Msg(2, 0, GlobalPrompt.JTCheersEnd)
		return
	
	if role.GetLevel() < EnumGameConfig.JTCheersMinLevel:
		return
	
	teamId = role.GetJTeamID()
	
	global TeamDataDict, PoolValue
	if teamId not in TeamDataDict:
		return
	
	if role.GetLevel() < EnumGameConfig.JTCheersMinLevel:
		return
	if TeamDataDict[teamId][ResponsesIndex] >= TeamDataDict[teamId][CheersIndex]:
		return
	if role.GetUnbindRMB() < EnumGameConfig.JTCheersResponsesRMB:
		return
	
	oldCheersCnt, oldRespCnt = TeamDataDict[teamId][CheersIndex], TeamDataDict[teamId][ResponsesIndex]
	TeamDataDict[teamId][ResponsesIndex] = newRespCnt = TeamDataDict[teamId][ResponsesIndex] + 1
	
	if oldCheersCnt >= EnumGameConfig.JTCheersTitleNeedCCnt and oldRespCnt < EnumGameConfig.JTCheersTitleNeedPCnt and newRespCnt >= EnumGameConfig.JTCheersTitleNeedPCnt:
		#获得称号
		for roleId in TeamDataDict[teamId][7]:
			Title.AddTitle(roleId, EnumGameConfig.JTCheersTitle)
	
	with JTCheersOneResponses_Log:
		role.DecUnbindRMB(EnumGameConfig.JTCheersResponsesRMB)
		PoolValue += EnumGameConfig.JTCheersResponsesRMB
	
	role.SendObj(JTCheersPoolValue, PoolValue)
	role.SendObj(JTCheersTeamData, TeamDataDict)
	
	role.Msg(2, 0, GlobalPrompt.JTCheersRespOneSuc)
	
def RequestTenResponses(role, msg):
	'''
	回应十次喝彩
	@param role:
	@param msg:
	'''
	global IsStart
	if not IsStart:
		role.Msg(2, 0, GlobalPrompt.JTCheersEnd)
		return
	
	teamId = role.GetJTeamID()
	
	global TeamDataDict, PoolValue
	if teamId not in TeamDataDict:
		return
	
	if role.GetLevel() < EnumGameConfig.JTCheersMinLevel:
		return
	if (TeamDataDict[teamId][ResponsesIndex] + 10) > TeamDataDict[teamId][CheersIndex]:
		return
	needRMB = EnumGameConfig.JTCheersResponsesRMB * 10
	if role.GetUnbindRMB() < needRMB:
		return
	
	oldCheersCnt, oldRespCnt = TeamDataDict[teamId][CheersIndex], TeamDataDict[teamId][ResponsesIndex]
	TeamDataDict[teamId][ResponsesIndex] = newRespCnt = TeamDataDict[teamId][ResponsesIndex] + 10
	if oldCheersCnt >= EnumGameConfig.JTCheersTitleNeedCCnt and oldRespCnt < EnumGameConfig.JTCheersTitleNeedPCnt and newRespCnt >= EnumGameConfig.JTCheersTitleNeedPCnt:
		#获得称号
		for roleId in TeamDataDict[teamId][7]:
			Title.AddTitle(roleId, EnumGameConfig.JTCheersTitle)
	
	with JTCheersTenResponses_Log:
		role.DecUnbindRMB(needRMB)
		PoolValue += needRMB
	
	role.SendObj(JTCheersPoolValue, PoolValue)
	role.SendObj(JTCheersTeamData, TeamDataDict)
	
	role.Msg(2, 0, GlobalPrompt.JTCheersRespTenSuc)
	
def RequestLogicJTCheersData(sessionid, msg):
	'''
	请求逻辑进程返回奖池数据和战队喝彩数据
	@param sessionid:
	@param msg:
	'''
	global PoolValue, TeamDataDict
	backid, _ = msg
	ControlProxy.CallBackFunction(sessionid, backid, (cProcess.ProcessID, PoolValue, TeamDataDict))

def UpdataJTCheersDataToLogic(sessionid, msg):
	'''
	控制进程向逻辑进程同步奖池数据和战队喝彩数据
	@param sessionid:
	@param msg:
	'''
	global PoolValue, TeamDataDict, BroadRoleIDSet
	PoolValue, TeamDataDict = msg
	
	for roleId in BroadRoleIDSet:
		role = cRoleMgr.FindRoleByRoleID(roleId)
		if not role:
			continue
		role.SendObj(JTCheersPoolValue, PoolValue)
		role.SendObj(JTCheersTeamData, TeamDataDict)

def UpdataJTCheersRewardDataToLogic(sessionid, msg):
	'''
	控制进程向逻辑进程同步奖励数据
	@param sessionid:
	@param msg:(总奖池, {服务器id:喝彩加回应总数})
	'''
	global JTCheers_Dict
	if not JTCheers_Dict.returnDB:
		print 'GE_EXC, UpdataJTCheersRewardDataToLogic JTCheers_Dict not returnDB'
		return
	
	totalPoolValue, totalCnt = msg
	
	#总次数
	aReward = totalPoolValue / totalCnt
	
	with JTCheersReward_Log:
		for roleId, cnt in JTCheers_Dict.iteritems():
			rewardRMB = aReward * cnt
			Mail.SendMail(roleId, GlobalPrompt.JTCheersMail_Title, GlobalPrompt.JTCheersMail_Sender, GlobalPrompt.JTCheersMail_Content % rewardRMB, unbindrmb = rewardRMB)
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveJTCheersData, JTCheers_Dict.data)
	
	JTCheers_Dict.clear()
	
def BeforeExit(role, param):
	global IsEnd
	if not IsEnd: return
	
	global BroadRoleIDSet
	roleId = role.GetRoleID()
	
	if roleId in BroadRoleIDSet:
		BroadRoleIDSet.discard(roleId)
	
def TryUpdate():
	global IsStart, IsEnd
	IsStart, IsEnd, _ = JTDefine.GetZBStartCnt()
	
	if not IsEnd: return
	
	#起服的时候尝试向控制进程请求数据
	ControlProxy.SendControlMsg(PyMessage.Control_GetGlobalZBCheersData, cProcess.ProcessID)
	
def AfterNewDay():
	global IsStart, IsEnd
	IsStart, IsEnd, _ = JTDefine.GetZBStartCnt()
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.EnvIsQQ() or Environment.EnvIsFT() or Environment.IsDevelop) and not Environment.IsCross:
		#role_id --> 喝彩次数
		JTCheers_Dict = Contain.Dict("JTCheers_Dict", (2038, 1, 1))
		
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_OpenPanel", "跨服争霸赛打开喝彩面板"), RequestOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_Cheers", "跨服争霸赛一次喝彩"), RequestCheers)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_TenCheers", "跨服争霸赛十次喝彩"), RequestTenCheers)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_Responses", "跨服争霸赛回应一次喝彩"), RequestResponses)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_TenResponses", "跨服争霸赛回应十次喝彩"), RequestTenResponses)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_ClosePanel", "跨服争霸赛关闭喝彩面板"), RequestClosePanel)
		#请求逻辑进程返回奖池数据和战队喝彩数据(回调)
		cComplexServer.RegDistribute(PyMessage.Control_RequestLogicZBCheersData, RequestLogicJTCheersData)
		#控制进程向逻辑进程同步奖池数据和战队喝彩数据
		cComplexServer.RegDistribute(PyMessage.Control_UpdataZBCheersDataToLogic, UpdataJTCheersDataToLogic)
		#控制进程向逻辑进程同步奖励数据
		cComplexServer.RegDistribute(PyMessage.Control_GetGlobalZBCheersReward, UpdataJTCheersRewardDataToLogic)
		
		Init.InitCallBack.RegCallbackFunction(TryUpdate)
		
		Event.RegEvent(Event.Eve_ClientLost, BeforeExit)
		Event.RegEvent(Event.Eve_BeforeExit, BeforeExit)
		
