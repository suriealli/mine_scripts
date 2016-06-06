#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.JT.JTLogicZB")
#===============================================================================
# 跨服争霸，逻辑进程
#===============================================================================
import Environment
import cNetMessage
import cComplexServer
import cRoleMgr
import cProcess
from ComplexServer import Init
from ComplexServer.Time import Cron
from ComplexServer.Log import AutoLog
from World import Define
from Common.Message import AutoMessage, PyMessage
from Game.Role import Call
from Game.Role import Event
from Common import CValue
from ComplexServer.Plug import Switch
from Game.Persistence import Contain
from Common.Other import GlobalPrompt
from Game.Role import Status
from Game.Fight import Fight
from Game.Role.Data import EnumInt1, EnumCD
from Game.JT import JTDefine, JTZBGroup, JTeam, JTZBFinal, JTConfig
from ComplexServer.Plug.Control import ControlProxy


if "_HasLoad" not in dir():
	#小组赛比赛开始，有资格的战队可以进入比赛
	IsGroupFightStart = False
	#总决赛
	IsFinalFightStart = False	#总决赛是否开启
	FinalFightStep = 0
	#32 : 32->16, 
	#16 : 16->8, 
	#8 : 8->4, 
	#4 : 4->1, 
	JT_GROUP_DICT = {}	#保存100强名单
	JT_FINAL_DICT = {}	#保存总决赛数据
	JT_FIGHT_DICT = {}	#保存观战数据
	JT_CLIENT_DICT = {}	#发给客户端的观战数据
	JT_Sttue_Data = {}	#雕像数据
	
	ServerRewardIsStart = False #全服奖励
	FinalServerRewardCacheDict = {}	#缓存份全服数据
	
	JT_S_HasServerReward = AutoMessage.AllotMessage("JT_S_HasServerReward", "同步跨服争霸服务器奖励可以领取")
	NJT_S_InviteJT = AutoMessage.AllotMessage("NJT_S_InviteJT", "同步有人邀请进入跨服争霸")
	JT_S_ServerReward = AutoMessage.AllotMessage("JT_S_ServerReward", "同步服务器和个人全服奖励")
	#日志
	Tra_NJTZB_SRInit = AutoLog.AutoTransaction("Tra_NJTZB_SRInit", "新版跨服争霸服务器奖励生成数据")
	Tra_JTZB_SR = AutoLog.AutoTransaction("Tra_JTZB_SR", "领取跨服争霸服务器奖励")
#########################################################################################
def RequestGet100Data(role, param):
	'''
	请求查看100强数据
	@param role:
	@param param:
	'''
	backId, groupId = param
	if groupId not in (1,2,3):
		return
	num = JTDefine.GetZBStartFlagNum()
	if num not in  [0,1,2,3,4]:
		return
	global JT_GROUP_DICT
	global JT_FINAL_DICT
	role.CallBackFunction(backId, (JT_GROUP_DICT.get(groupId), JT_FINAL_DICT.get(groupId)))

def RequestGetStatueData(role, param):
	'''
	请求获取雕像数据
	@param role:
	@param param:
	'''
	backId, _ = param
	global JT_Sttue_Data
	role.CallBackFunction(backId, JT_Sttue_Data)
	
def RequestGetFightViewData(role, param):
	'''
	请求查看观战数据
	@param role:
	@param param:
	'''
	backId, (groupId, FinalStep) = param
	num = JTDefine.GetZBStartFlagNum()
	if num not in [2,3,4]:
		return
	
	global JT_CLIENT_DICT
	role.CallBackFunction(backId, JT_CLIENT_DICT.get(groupId, {}).get(FinalStep, {}))

def RequestFightView(role, param):
	'''
	请求观战
	@param role:
	@param param:
	'''
	groupId, FinalStep, teamId1, teamId2, ground = param
	if groupId not in (1,2,3):
		return
	global JT_FIGHT_DICT
	
	Fight_Data = JT_FIGHT_DICT.get(groupId)
	if not Fight_Data:
		return
	data = Fight_Data.get(FinalStep)
	if not data:
		return
	key = (teamId1, teamId2, ground)
	fightdata = data.get(key)
	if not fightdata:
		key = (teamId2, teamId1, ground)
		fightdata = data.get(key)
		if not fightdata:
			return
	initdata, veiwdata = fightdata[1]
	role.SendObj(Fight.Fight_Init, initdata)
	for data in veiwdata:
		role.SendObj(Fight.Fight_List, data)
	
	
def RequesrJoinGroupFight(role, msg):
	'''
	请求进入跨服争霸小组赛
	@param role:
	@param msg:
	'''
	jtobj = role.GetJTObj()
	if not jtobj:
		role.Msg(2, 0, GlobalPrompt.JT_GroupTips1)
		return
	if not Status.CanInStatus(role, EnumInt1.ST_JTGoToCross):
		return
	global IsGroupFightStart
	#判断活动是否已经开启
	if IsGroupFightStart is False:
		role.Msg(2, 0, GlobalPrompt.JT_GroupTips2)
		return
	#判断资格
	groupData = jtobj.GetGroupIndex()
	if not groupData:
		role.Msg(2, 0, GlobalPrompt.JT_GroupTips1)
		return
	#传送到跨服场景
	role.GotoCrossServer(None, JTDefine.JTZBSceneID, 958, 579, JTZBGroup.AfterJoinGroup, (jtobj.teamId, groupData[0]))
	
def InviteJoinJT(role, param):
	'''
	客户端邀请战队队员进入跨服争霸
	@param role:
	@param param:
	'''
	backId, roleid = param
	
	if role.GetCD(EnumCD.JTInviteToCrossCD):
		return
	jtobj = role.GetJTObj()
	if not jtobj:
		role.Msg(2, 0, GlobalPrompt.JT_GroupTips1)
		return
	if roleid == role.GetRoleID():
		return
	if roleid not in jtobj.members:
		return
	if not IsFinalFightStart and not IsGroupFightStart:
		role.Msg(2, 0, GlobalPrompt.JT_GroupTips2)
		return
	irole = cRoleMgr.FindRoleByRoleID(roleid)
	if not irole or irole.IsLost():
		role.Msg(2, 0, GlobalPrompt.JT_Tips_21)
		return
	if not Status.CanInStatus(irole, EnumInt1.ST_JTGoToCross):
		role.Msg(2, 0, GlobalPrompt.JT_Tips_18)
		return
	#判断资格
	groupData = jtobj.GetGroupIndex()
	if not groupData:
		role.Msg(2, 0, GlobalPrompt.JT_GroupTips1)
		return
	_, groupIndex = groupData
	if IsFinalFightStart:
		if groupIndex > FinalFightStep:
			role.Msg(2, 0, GlobalPrompt.JT_GroupTips1)
			return
	
	irole.SendObjAndBack(NJT_S_InviteJT, role.GetRoleName(), 60, InviteToCrossBack, None)
	role.CallBackFunction(backId, None)
	role.SetCD(EnumCD.JTInviteToCrossCD, 3)
	
def InviteToCrossBack(role, callArgv, regparam):
	if callArgv == 1 or callArgv is None:
		#同意或自动回调
		if IsFinalFightStart:
			RequestJoinFinalFight(role, None)
		if IsGroupFightStart:
			RequesrJoinGroupFight(role, None)
	
def RequestJoinFinalFight(role, param):
	'''
	请求进入跨服争霸赛总决赛
	@param role:
	@param param:
	'''
	jtobj = role.GetJTObj()
	if not jtobj:
		role.Msg(2, 0, GlobalPrompt.JT_GroupTips1)
		return
	if not Status.CanInStatus(role, EnumInt1.ST_JTGoToCross):
		return
	global IsFinalFightStart
	if not IsFinalFightStart:
		role.Msg(2, 0, GlobalPrompt.JT_GroupTips2)
		return
	groupData = jtobj.GetGroupIndex()
	if not groupData:
		role.Msg(2, 0, GlobalPrompt.JT_GroupTips1)
		return
	groupId, groupIndex = groupData
	global FinalFightStep
	if groupIndex > FinalFightStep:
		role.Msg(2, 0, GlobalPrompt.JT_GroupTips1)
		return
	#传送到跨服场景
	role.GotoCrossServer(None, JTDefine.JTZBSceneID, 958, 579, JTZBFinal.AfterJoinFinal, (jtobj.teamId, groupId))

def RequestServerRewardData(role, msg):
	'''
	请求查询争霸赛服务器奖励数据(服务器，个人)
	@param role:
	@param msg:
	'''
	global NJT_ServerRewardDict
	global NJT_ServerRewardRoleRecord
	global ServerRewardIsStart
	if not ServerRewardIsStart:
		return
	if role.GetLevel() < 30:
		return
	backId, _ = msg
	role.CallBackFunction(backId, (NJT_ServerRewardDict.data, NJT_ServerRewardRoleRecord.get(role.GetRoleID(), {})))

def SyncRoleOtherData(role, param):
	global NJT_ServerRewardDict
	global NJT_ServerRewardRoleRecord
	global ServerRewardIsStart
	if not ServerRewardIsStart:
		return
	if role.GetLevel() < 30:
		return
	role.SendObj(JT_S_ServerReward, (NJT_ServerRewardDict.data, NJT_ServerRewardRoleRecord.get(role.GetRoleID(), {})))
	
def RequestGetServerReward(role, msg):
	'''
	请求领取争霸赛服务器奖励
	@param role:
	@param msg:
	'''
	backId, (rewardType, index) = msg
	global ServerRewardIsStart
	if not ServerRewardIsStart:
		return
	if role.GetLevel() < 30:
		return
	if not HasServerReward(role):
		return
	global NJT_ServerRewardRoleRecord
	roledata = NJT_ServerRewardRoleRecord.get(role.GetRoleID())
	if not roledata:
		NJT_ServerRewardRoleRecord[role.GetRoleID()] = roledata = {1 : [0] * 3, 2 : [0] * 3, 3 : [0] * 3}
	
	item = JTConfig.GetSRItem(rewardType, index)
	if not item:
		return
	with Tra_JTZB_SR:
		global NJT_ServerRewardDict
		
		if rewardType == 1:
			if index < 1 or index > 3:
				return
			serverdata = FinalServerRewardCacheDict.get(1)
			if not serverdata:
				return
			if not serverdata.get(index):
				return
			if roledata[1][index - 1]:
				return
			roledata[1][index - 1] = 1
			role.AddItem(*item)
			
		elif rewardType == 2:
			if index < 1 or index > 3:
				return
			serverdata = FinalServerRewardCacheDict.get(2)
			if not serverdata:
				return
			if not serverdata.get(index):
				return
			if roledata[2][index - 1]:
				return
			roledata[2][index - 1] = 1
			role.AddItem(*item)
		elif rewardType == 3:
			if index < 1 or index > 3:
				return
			serverdata = FinalServerRewardCacheDict.get(3)
			if not serverdata:
				return
			if not serverdata.get(index):
				return
			if roledata[3][index - 1]:
				return
			roledata[3][index - 1] = 1
			role.AddItem(*item)
	role.CallBackFunction(backId, (rewardType, index))
	SRMSG(role.GetRoleName(), rewardType, index)
	
def SRMSG(roleName, rewardType, index):
	#跨服争霸服务器奖励全部提示
	if rewardType not in (1, 2,3):
		return
	global NJT_ServerRewardDict
	datadict = NJT_ServerRewardDict.get(rewardType)
	if not datadict:
		return
	teamdata = datadict.get(index)
	if not teamdata:
		return
	rtypemsg = GlobalPrompt.JT_Chuji
	if rewardType == 2:
		rtypemsg = GlobalPrompt.JT_Jingrui
	elif rewardType == 3:
		rtypemsg = GlobalPrompt.JT_Dianfeng
	fst = GlobalPrompt.JT_SR_3
	if index == 1:
		fst = GlobalPrompt.JT_SR_1
	elif index == 2:
		fst = GlobalPrompt.JT_SR_2
	memberNames = teamdata[3]
	mtips = ",".join(memberNames)
	msg = GlobalPrompt.JT_FinalTips_10 % (roleName, fst, rtypemsg, fst, mtips)
	cRoleMgr.Msg(3, 0, msg)
############################小组赛############################
def ReadyGroupFight():
	#开始小组比赛，准备进入了 (提前了5分钟，总共50分钟)
	num = JTDefine.GetZBStartFlagNum()
	if num != 1:
		return
	global IsGroupFightStart
	IsGroupFightStart = True
	cComplexServer.RegTick(60 * 5, BroadMsg, 1)
	cComplexServer.RegTick(60 * 46, EndGroupFight, None)
	cRoleMgr.Msg(1, 0, GlobalPrompt.JT_GroupStart)
	
def BroadMsg(callArgv = None, regparam = None):
	fightround = regparam
	cRoleMgr.Msg(1, 0, GlobalPrompt.JT_32RoundMsg % fightround)
	fightround += 1
	if fightround <= 8:
		cComplexServer.RegTick(60 * 5 + 30, BroadMsg, fightround)
	
	
def EndGroupFight(callArgv = None, regparam = None):
	global IsGroupFightStart
	IsGroupFightStart = False
	cRoleMgr.Msg(1, 0, GlobalPrompt.JT_EndFight1)
###########################总决赛##########################
def ReadyFinalFight32_16():
	#32进16的比赛
	num = JTDefine.GetZBStartFlagNum()
	if num not in  [2,3,4]:
		return
	global FinalFightStep
	if num == 2:
		FinalFightStep = 32
		cRoleMgr.Msg(1, 0, GlobalPrompt.JT_FinalTips_2)
		cComplexServer.RegTick(60 * 5, BroadMsg2, 1)
	elif num == 3:
		FinalFightStep = 8
		cComplexServer.RegTick(60 * 5, BroadMsg4, 1)
		cRoleMgr.Msg(1, 0, GlobalPrompt.JT_FinalTips_4)
	elif num == 4:
		FinalFightStep = 4
		cComplexServer.RegTick(60 * 5, BroadMsg5, 1)
		cRoleMgr.Msg(1, 0, GlobalPrompt.JT_FinalTips_5)
		
	global IsFinalFightStart
	IsFinalFightStart = True
	if num == 2:
		cComplexServer.RegTick(60 * 29, EndFinalFight, FinalFightStep)
	else:
		cComplexServer.RegTick(60 * 36, EndFinalFight, FinalFightStep)
	
def ReadyFinalFight16_8():
	#16进8的比赛
	num = JTDefine.GetZBStartFlagNum()
	if num != 2:
		return
	global FinalFightStep
	FinalFightStep = 16
	global IsFinalFightStart
	IsFinalFightStart = True
	cComplexServer.RegTick(60 * 25, EndFinalFight, FinalFightStep)
	cComplexServer.RegTick(60 * 5, BroadMsg3, 1)
	cRoleMgr.Msg(1, 0, GlobalPrompt.JT_FinalTips_3)

def BroadMsg2(callArgv = None, regparam = None):
	fightround = regparam
	cRoleMgr.Msg(1, 0, GlobalPrompt.JT_16RoundMsg % fightround)
	fightround += 1
	if fightround <= 3:
		cComplexServer.RegTick(60 * 7 + 30, BroadMsg2, fightround)

def BroadMsg3(callArgv = None, regparam = None):
	fightround = regparam
	cRoleMgr.Msg(1, 0, GlobalPrompt.JT_8RoundMsg % fightround)
	fightround += 1
	if fightround <= 3:
		cComplexServer.RegTick(60 * 7 + 30, BroadMsg3, fightround)
		
def BroadMsg4(callArgv = None, regparam = None):
	fightround = regparam
	cRoleMgr.Msg(1, 0, GlobalPrompt.JT_4RoundMsg % fightround)
	fightround += 1
	if fightround <= 3:
		cComplexServer.RegTick(60 * 9 + 30, BroadMsg4, fightround)
		
def BroadMsg5(callArgv = None, regparam = None):
	fightround = regparam
	cRoleMgr.Msg(1, 0, GlobalPrompt.JT_1RoundMsg % fightround)
	fightround += 1
	if fightround <= 3:
		cComplexServer.RegTick(60 * 9 + 30, BroadMsg5, fightround)
		
def EndFinalFight(callArgv = None, regparam = None):
	global IsFinalFightStart, FinalFightStep
	IsFinalFightStart = False
	
	if FinalFightStep == 32:
		cRoleMgr.Msg(1, 0, GlobalPrompt.JT_EndFight2)
	elif FinalFightStep == 16:
		cRoleMgr.Msg(1, 0, GlobalPrompt.JT_EndFight3)
	elif FinalFightStep == 8:
		cRoleMgr.Msg(1, 0, GlobalPrompt.JT_EndFight4)
	elif FinalFightStep == 4:
		cRoleMgr.Msg(1, 0, GlobalPrompt.JT_EndFight5)
		
	FinalFightStep = 0
	
		
#########################################################################################
#跨服同步过来的数据
#########################################################################################
def ReceiveGroupRank(param):
	#收到跨服进程同步过来的100强名单
	data, mail = param
	global JT_GROUP_DICT
	JT_GROUP_DICT = data
	
	if not mail:
		return
	#修改战队数据
	for gruopId, teanList in JT_GROUP_DICT.iteritems():
		for teamData in teanList:
			#服务器ID，服务器名字，队伍ID，队伍名字，积分，段位，成员数据，战队等级，胜率(万份比)，总战力，总排名
			teamId = teamData[2]
			teamObj = JTeam.JJT_Obj_Dict.get(teamId)
			if not teamObj:
				continue
			#设置战队为100强
			teamObj.SetGroupIndex(gruopId, 100)
			
			
def ReceiveFinalData(param):
	#收到跨服进程同步过来的总决赛数据
	global JT_FINAL_DICT
	finalData, mail, end = param
	JT_FINAL_DICT = finalData
	if mail:
		#修改战队数据
		for groupId, teamList in JT_FINAL_DICT.iteritems():
			if groupId == 4:
				continue
			for teamData in teamList:
				#teamId,teamName,processName,processID,teamPoint,teamGrade,totalZdl,memberIds,rank,teamData,32
				#队伍ID, 队伍名，服名，服ID，战队积分，战队段位，总战斗力，成员IDs, 总排名, 队伍信息,index
				teamId = teamData[0]
				teamObj = JTeam.JJT_Obj_Dict.get(teamId)
				if not teamObj:
					continue
				#设置战队的步骤
				teamObj.SetGroupIndex(groupId, teamData[10])
	if end:
		#争霸赛打完了
		InitServerReward()
		#清理战队有关争霸赛的数据
		EndZBAndClear(True)
	
def ReceiveFinalFightData(FightData):
	#收到跨服战斗数据
	global JT_FIGHT_DICT
	global JT_CLIENT_DICT
	
	if not FightData: return
	
	for groupId, data in FightData.iteritems():
		if groupId not in JT_FIGHT_DICT:
			JT_FIGHT_DICT[groupId] = data
		else:
			group_olddata = JT_FIGHT_DICT.get(groupId)
			for step, viewData in data.iteritems():
				if step not in group_olddata:
					group_olddata[step] = viewData
				else:
					oldData = group_olddata[step]
					for viewkey, fightdata in viewData.iteritems():
						oldData[viewkey] = fightdata
	
	JT_CLIENT_DICT = {}
	for groupId, data in JT_FIGHT_DICT.iteritems():
		JT_CLIENT_DICT[groupId] = JCD = {}
		for index, fightData in data.iteritems():
			JCD[index] = FD = {}
			for key, teamfight in fightData.iteritems():
				FD[key] = teamfight[0]	
#	JT_CLIENT_DICT = {}
#	JT_FIGHT_DICT = FightData
#	
#	for groupId, data in JT_FIGHT_DICT.iteritems():
#		JT_CLIENT_DICT[groupId] = JCD = {}
#		for index, fightData in data.iteritems():
#			JCD[index] = FD = {}
#			for key, teamfight in fightData.iteritems():
#				FD[key] = teamfight[0]
	
def ReceiveFinalStatueData(statueData):
	global JT_Sttue_Data
	JT_Sttue_Data = statueData
	
######################################################################
def EndZBAndClear(param = None):
	#结束，清理数据 
	if param is True:
		for jteam in JTeam.JJT_Obj_Dict.itervalues():
			jteam.ClearZBData()
	elif JTDefine.GetZBStartFlagNum() == 4 or JTDefine.GetZBStartFlagNum() == 5:
		for jteam in JTeam.JJT_Obj_Dict.itervalues():
			jteam.ClearZBData()
			
def InitServerReward():
	ClearServerReward()
	global JT_FINAL_DICT
	global ServerRewardIsStart
	global NJT_ServerRewardDict
	
	ServerRewardIsStart = True
	
	FinalData = JT_FINAL_DICT.get(4)
	if not FinalData:
		print "GE_EXC,JTLogicZB.InitServerReward has no JT_FINAL_DICT[4]"
		return
	NJT_ServerRewardDict[1] = {}
	NJT_ServerRewardDict[2] = {}
	NJT_ServerRewardDict[3] = {}
	
	with Tra_NJTZB_SRInit:
		if FinalData[1]:
			InitServerRewardEx(1, FinalData[1])
		if FinalData[2]:
			InitServerRewardEx(2, FinalData[2])
		if FinalData[3]:
			InitServerRewardEx(3, FinalData[3])
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveJTSR, NJT_ServerRewardDict.data)
		UpdateServerRewardCache()
		BroadServerRewrad()
		
def BroadServerRewrad():
	cNetMessage.PackPyMsg(JT_S_HasServerReward, 1)
	cRoleMgr.BroadMsg()
	
def IsLocalTeam(teamId):
	#队伍ID由进程ID组成--高16位是进程ID
	#pid = teamId / CValue.P2_48
	return (teamId / CValue.P2_48) in Switch.LocalServerIDs

def InitServerRewardEx(finalType, teamDataDict):
	if not teamDataDict:
		return
	global NJT_ServerRewardDict, FinalServerRewardCacheDict
	
	ServerDict = NJT_ServerRewardDict.get(finalType)
	#冠军
	SetServerReward(ServerDict, 1, teamDataDict.get(1))
	#亚军
	SetServerReward(ServerDict, 2, teamDataDict.get(2))
	#季军
	SetServerReward(ServerDict, 3, teamDataDict.get(3))
		
def SetServerReward(ServerDict, rewardType, teamData):
	if not teamData:
		return
	teamId = teamData[0]
	#队伍ID, 队伍名，服名， 队员名，是否是本服
	names = []
	for member in teamData[9]:
		names.append(member[0])
	ServerDict[rewardType] = [teamId, teamData[1], teamData[2], names, IsLocalTeam(teamId)]
	
def ClearServerReward():
	global NJT_ServerRewardDict, NJT_ServerRewardRoleRecord
	if NJT_ServerRewardDict.returnDB:
		NJT_ServerRewardDict.clear()
	if NJT_ServerRewardRoleRecord.returnDB:
		NJT_ServerRewardRoleRecord.clear()
	
def UpdateServerRewardCache():
	#建立一份缓存
	global NJT_ServerRewardDict, FinalServerRewardCacheDict
	FinalServerRewardCacheDict[1] = rc1 = {}
	FinalServerRewardCacheDict[2] = rc2 = {}
	FinalServerRewardCacheDict[3] = rc3 = {}
	
	for rewradTyps, datas in NJT_ServerRewardDict[1].iteritems():
		rc1[rewradTyps] = datas[4]
	for rewradTyps, datas in NJT_ServerRewardDict[2].iteritems():
		rc2[rewradTyps] = datas[4]
	for rewradTyps, datas in NJT_ServerRewardDict[3].iteritems():
		rc3[rewradTyps] = datas[4]
		
def HasServerReward(role):
	global NJT_ServerRewardRoleRecord, FinalServerRewardCacheDict
	roledata = NJT_ServerRewardRoleRecord.get(role.GetRoleID())
	if not roledata:
		sr1 = FinalServerRewardCacheDict.get(1)
		if sr1:
			if True in sr1.values():
				return True
		sr2 = FinalServerRewardCacheDict.get(2)
		if sr2:
			if True in sr2.values():
				return True
		sr3 = FinalServerRewardCacheDict.get(3)
		if sr3:
			if True in sr3.values():
				return True
	else:
		#冠亚季
		sr1 = FinalServerRewardCacheDict.get(1)
		if sr1:
			if True in sr1.values():
				sr1_roledata = roledata.get(1)
				if not sr1_roledata:
					return True
				for rType, rFlag in sr1.iteritems():
					if not sr1_roledata[rType - 1] and rFlag:
						return True
		sr2 = FinalServerRewardCacheDict.get(2)
		if sr2:
			if True in sr2.values():
				sr2_roledata = roledata.get(2)
				if not sr2_roledata:
					return True
				for rType, rFlag in sr2.iteritems():
					if not sr2_roledata[rType - 1] and rFlag:
						return True
		sr3 = FinalServerRewardCacheDict.get(3)
		if sr3:
			if True in sr3.values():
				sr3_roledata = roledata.get(3)
				if not sr3_roledata:
					return True
				for rType, rFlag in sr3.iteritems():
					if not sr3_roledata[rType - 1] and rFlag:
						return True
	return False

def CheckServerRewardStart():
	global ServerRewardIsStart
	dayNum = JTDefine.GetZBStartFlagNum()
	if dayNum < 4 or dayNum > 7:
		ServerRewardIsStart = False
	else:
		ServerRewardIsStart = True
#=================================================================
def CallNewDay():
	CheckServerRewardStart()
	
def ServerStart():
	#服务器启动,向跨服进程请求数据
	if Environment.IsCross:
		return
	CheckServerRewardStart()
	
	num = JTDefine.GetZBStartFlagNum()
	if num in [2,3,4]:
		#请求观战数据
		Call.ServerCall(Define.GetDefaultCrossID(), "Game.JT.JTZBFinal", "UpdataZBFinalViweData", cProcess.ProcessID)
	if num in [1,2,3,4]:
		#请求小组赛数据
		Call.ServerCall(Define.GetDefaultCrossID(), "Game.JT.JTZBGroup", "UpdataGroupRankData", cProcess.ProcessID)
		#请求决赛数据
		Call.ServerCall(Define.GetDefaultCrossID(), "Game.JT.JTZBFinal", "UpdataFinalData", cProcess.ProcessID)
	#请求雕像数据
	Call.ServerCall(Define.GetDefaultCrossID(), "Game.JT.JTZBFinal", "UpdataStatueData", cProcess.ProcessID)
	
def AfterLoadServerRewardDict():
	CheckServerRewardStart()
	global ServerRewardIsStart
	if ServerRewardIsStart is False:
		return
	global NJT_ServerRewardDict
	if not NJT_ServerRewardDict.data:
		return
	UpdateServerRewardCache()

def AfterLoadServerRewardRoleDict():
	pass

def RequestLogicJTTeamData(sessionid, msg):
	'''
	请求巅峰战队数据
	@param sessionid:
	@param msg:
	'''
	backId, _ = msg
	global JT_GROUP_DICT
	if not JT_GROUP_DICT:
		return
	
	ControlProxy.CallBackFunction(sessionid, backId, JT_GROUP_DICT.get(3, []))
	
def RequestLogicJTFirstTeamData(sessionid, msg):
	'''
	请求巅峰战队冠军队伍id
	@param sessionid:
	@param msg:
	'''
	backId, _ = msg
	global NJT_ServerRewardDict
	if not NJT_ServerRewardDict:
		print 'JTLogicZB empty NJT_ServerRewardDict'
		ControlProxy.CallBackFunction(sessionid, backId, -1)
		return
	firstTeamData = NJT_ServerRewardDict.get(3)
	if not firstTeamData:
		print 'JTLogicZB empty NJT_ServerRewardDict[3]'
		ControlProxy.CallBackFunction(sessionid, backId, -1)
		return
	teamData = firstTeamData.get(1)
	if not teamData:
		print 'JTLogicZB empty firstTeamData'
		ControlProxy.CallBackFunction(sessionid, backId, -1)
		return
	
	ControlProxy.CallBackFunction(sessionid, backId, teamData[0])
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.IsDevelop or Environment.EnvIsQQ() or Environment.EnvIsFT()) and not Environment.IsCross:
		#跨服争霸服务器奖励记录服务器数据{战区: {1 : 冠军, 2:亚军, 3:季军},}
		NJT_ServerRewardDict = Contain.Dict("NJT_ServerRewardDict", (2038, 1, 1), AfterLoadServerRewardDict)
		#跨服争霸服务器奖励记录个人数据 roleId-->{1 : 初级[0,0,0], 2 : 精锐[0,0,0], 3 : 巅峰[0,0,0]}
		NJT_ServerRewardRoleRecord = Contain.Dict("NJT_ServerRewardRoleRecord", (2038, 1, 1), AfterLoadServerRewardRoleDict)
		
		cComplexServer.RegAfterNewDayCallFunction(CallNewDay)
		Init.InitCallBack.RegCallbackFunction(ServerStart)
		
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		#小组赛
		Cron.CronDriveByMinute((2038, 1, 1), ReadyGroupFight, H="H == 21", M="M == 55")
		#总决赛 
		#32->16, 8->4, 4->1
		Cron.CronDriveByMinute((2038, 1, 1), ReadyFinalFight32_16, H="H == 21", M="M == 55")
		#16->8
		Cron.CronDriveByMinute((2038, 1, 1), ReadyFinalFight16_8, H="H == 22", M="M == 25")
		
		Cron.CronDriveByMinute((2038, 1, 1), EndZBAndClear, H="H == 22", M="M == 40")
		#进入跨服
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NJT_RequesrJoinZBGroupFight", "请求进入跨服争霸小组赛"), RequesrJoinGroupFight)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NJT_RequestJoinZBFinalFight", "请求进入跨服争霸总决赛"), RequestJoinFinalFight)
		#争霸赛服务器奖励
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NJT_RequestServerRewardData", "请求查询争霸赛服务器奖励数据(服务器，个人)"), RequestServerRewardData)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NJT_RequestGetServerReward", "请求领取争霸赛服务器奖励"), RequestGetServerReward)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NJT_RequestGet100Data", "请求查看100强数据"), RequestGet100Data)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NJT_RequestFightViewData", "请求查看观战数据"), RequestGetFightViewData)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NJT_RequestStatueData", "请求获取争霸赛雕像数据"), RequestGetStatueData)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NJT_RequestFightView", "请求观战"), RequestFightView)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NJT_InviteJoinJT", "客户端邀请战队队员进入跨服争霸"), InviteJoinJT)
		
		cComplexServer.RegDistribute(PyMessage.Control_GetGlobalZBTeamData, RequestLogicJTTeamData)
		cComplexServer.RegDistribute(PyMessage.Control_GetGlobalZBFirstTeamData, RequestLogicJTFirstTeamData)
		
