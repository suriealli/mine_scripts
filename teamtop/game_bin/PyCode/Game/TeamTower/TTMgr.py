#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.TeamTower.TTMgr")
#===============================================================================
# 组队爬塔管理器
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Role import Event, Status
from Game.Team import TeamBase, EnumTeamType
from Game.Role.Data import EnumTempObj, EnumInt1, EnumObj, EnumCD, EnumTempInt64,\
	EnumDayInt8
from Game.TeamTower import TTMirror, TTConfig
from Game.SysData import WorldDataNotSync
from Game.Activity.SevenDayHegemony import SDHFunGather, SDHDefine
from ComplexServer.Log import AutoLog


if "_HasLoad" not in dir():
	TT_S_TodayData = AutoMessage.AllotMessage("TT_S_TodayData", "同步更组队爬塔今天的数据")
	
	Tra_TTOneKeyReward = AutoLog.AutoTransaction("Tra_TTOneKeyReward", "组队爬塔一键收益奖励")

	

def OpenPanel(role, msg):
	'''
	客户端请求打开组队爬塔大厅面板
	@param role:
	@param msg:
	'''
	backId, tIndex = msg
	if tIndex == 0:
		if role.GetLevel() < EnumGameConfig.TEAM_TOWER_NEED_LEVEL_0:
			return
	else:
		if role.GetLevel() < EnumGameConfig.TEAM_TOWER_NEED_LEVEL:
			return
	
	tlist = TeamBase.TTListDict.get(tIndex)
	if tlist is None:
		return
	sendList = []
	for team in tlist:
		#队伍是否已经在副本中
		if team.leader.GetTempObj(EnumTempObj.MirrorScene):
			continue
		#队伍ID，队长名字，副本ID，队伍人数
		sendList.append((team.team_id, team.leader.GetRoleName(), len(team.members)))
	
	wtd = WorldDataNotSync.WorldDataPrivate[WorldDataNotSync.TeamTowerFinishDict]

	#同步客户端 (组队信息，  全服前章节的通关次数)
	role.CallBackFunction(backId, (sendList, wtd))
	
	role.SendObj(TT_S_TodayData, role.GetObj(EnumObj.TeamTowerData).get(3, [0, 0, 0]))

def RequestTTStart(role, msg):
	'''
	请求进入组队爬塔
	@param role:
	@param msg:
	'''
	#获取队伍
	team = role.GetTeam()
	if not team:
		return
	
	if len(team.members) != 3 or not team.IsTeamLeader(role):
		#人数不足
		return
	ttIndex = EnumTeamType.GetTeamTowerTypeIndex(team.team_type)
	if ttIndex is None:
		return
	
	#配置
	ttconfig = TTConfig.TeamTowerConfig_Dict.get(ttIndex)
	if not ttconfig:
		return
	
	#队伍能否进入战斗状态
	if not Status.CanInStatus_Roles(team.members, EnumInt1.ST_InTeamMirror):
		return
	#创建组队爬塔副本
	TTMirror.TTMirror(team, ttconfig)
	
	#圣诞转转乐
	for member in team.members:
		Event.TriggerEvent(Event.Eve_IncChristmasWingLotteryTime, member, EnumGameConfig.Source_TeamTower)
		Event.TriggerEvent(Event.Eve_LatestActivityTask, member, (EnumGameConfig.LA_TT, 1))
	
def SetRewardModel(role, msg):
	'''
	客户端请求设置组队爬塔无奖励模式
	@param role:
	@param msg:
	'''
	if msg:
		role.SetI1(EnumInt1.TeamTowerNoReward, 1)
	else:
		role.SetI1(EnumInt1.TeamTowerNoReward, 0)


def TTWorldCall(role, msg):
	'''
	组队爬塔世界邀请
	@param role:
	@param msg:
	'''
	team = role.GetTeam()
	if not team:
		return
	#CD时间
	if role.GetCD(EnumCD.TeamTowerWorldCall) > 0:
		return
	#队伍是否已满
	if team.IsFull():
		return
	if not EnumTeamType.IsTeamTowerType(team.team_type):
		return

	role.SetCD(EnumCD.TeamTowerWorldCall, 20)
	
	
	index = EnumTeamType.GetTeamTowerTypeIndex(team.team_type)
	if index is None:
		return
	
	tips = GlobalPrompt.GetTT_WorldCall_Tips(index)
	if not tips:
		print "GE_EXC, TTWorldCall not tips index(%s)" % index
		return
	#传闻
	cRoleMgr.Msg(7, 0, tips % (team.leader.GetRoleName(), 3 - len(team.members), team.team_id))


def RequestInvite(role, msg):
	'''
	客户端请求组队爬塔邀请好友
	@param role:
	@param msg:
	'''
	team = role.GetTeam()
	if not team:
		return
	
	if not team.CanInvite(role):
		return
	
	#是否已经在副本中
	if role.GetTempObj(EnumTempObj.MirrorScene):
		return
	
	desRoleId = msg
	# 发送邀请
	desRole = cRoleMgr.FindRoleByRoleID(desRoleId)
	if not desRole:
		#提示
		role.Msg(2, 0, GlobalPrompt.TEAM_NOT_ONLINE_PROMPT)
		return
	if desRole.HasTeam():
		#提示
		role.Msg(2, 0, GlobalPrompt.TEAM_HAS_TEAM_PROMPT)
		return
	
	if not team.CanBeInvite(desRole):
		return
	
	index = EnumTeamType.GetTeamTowerTypeIndex(team.team_type)
	if index is None:
		return
	
	if desRole.GetTI64(EnumTempInt64.TT_AutoInvite):
		InviteBack(desRole, 1, team.team_id)
	else:
		#队伍id, 玩家名
		desRole.SendObjAndBack(TTMirror.TT_S_Show_Invite_Data, (role.GetRoleName(), index), 120, InviteBack, team.team_id)
	
def InviteBack(role, callargv, regparam):
	'''
	邀请回调
	@param role:
	@param callargv:
	@param regparam:
	'''
	teamId = regparam
	
	#被邀请的角色回调函数
	if callargv != 1:
		#拒绝加入组队
		return

	team =  TeamBase.GetTeamByTeamID(teamId)
	if not team:
		#提示
		role.Msg(2, 0, GlobalPrompt.TEAM_NOT_EXIST_PROMPT)
		return
	
	if not team.CanJoin(role):
		return
	
	#加入队伍
	team.AddMember(role)


def FastJoinTeam(role, msg):
	'''
	客户端请求组队爬塔快速组队
	@param role:
	@param msg:
	'''
	tIndex = msg
	teamList = TeamBase.TTListDict.get(tIndex)
	if teamList is None:
		return
	#状态判断
	if not Status.CanInStatus(role, EnumInt1.ST_Team):
		return
	
	for team in teamList:
		#队伍是否已经在副本中
		if team.leader.GetTempObj(EnumTempObj.MirrorScene):
			continue
		if not team.CanJoin(role):
			continue
		team.Join(role)

def SetAutoJoinTT(role, msg):
	'''
	客户端请求组队爬塔快速组队
	@param role:
	@param msg:
	'''
	if msg not in (1, 0):
		return
	role.SetTI64(EnumTempInt64.TT_AutoInvite, msg)

def OneKeyReward(role, msg):
	'''
	组队爬塔一键收益
	@param role:
	@param msg:
	'''
	if role.GetVIP() < EnumGameConfig.TT_OneKeyNeedVIPLevel:
		return
	if role.GetDI8(EnumDayInt8.TT_RewradTimes) >= EnumGameConfig.TT_RewardTimes:
		return
	
	ttdata = role.GetObj(EnumObj.TeamTowerData)
	nowData = ttdata.get(3)
	if not nowData:
		return
	
	nowIndex, nowLayer, nowScore = nowData
	if not nowLayer:
		return
	indexCfgDict = TTConfig.TeamTowerLayerConfig_Dict.get(nowIndex)
	if not indexCfgDict:
		return
	layercfg = indexCfgDict.get(1)
	if not layercfg:
		return
	ttconfig = TTConfig.TeamTowerConfig_Dict.get(nowIndex)
	if not ttconfig:
		return
	
	totalMoney = 0
	totalSoul = 0
	totalitems = {}
	
	if nowScore:
		#通关评价奖励
		scoreReward = ttconfig.GetReward(role, nowScore)
		if not scoreReward:
			return
		scoreMoney, scoreSoul, scoreItems = scoreReward
		totalMoney += scoreMoney
		totalSoul += scoreSoul
		for itemCoding, itemCnt in scoreItems:
			totalitems[itemCoding] = totalitems.get(itemCoding, 0) + itemCnt

	with Tra_TTOneKeyReward:
		#扣除次数
		role.IncDI8(EnumDayInt8.TT_RewradTimes, 1)
		for _ in range(ttconfig.maxLayer):
			#每一层奖励
			for rewardCfg in layercfg.rewardCfgs:
				money, soul, items = rewardCfg.GetReward(role)
				totalMoney += money
				totalSoul += soul
				for itemCoding, itemCnt in items:
					totalitems[itemCoding] = totalitems.get(itemCoding, 0) + itemCnt
			#下一层
			layercfg = layercfg.ttLayerNextCfg
			if not layercfg:
				break
			if layercfg.layer > nowLayer:
				break
		
		tips = GlobalPrompt.TT_OneKeyTips
		if totalMoney:
			role.IncMoney(totalMoney)
		tips += GlobalPrompt.Money_Tips % totalMoney
		if totalSoul:
			role.IncDragonSoul(totalSoul)
		tips += GlobalPrompt.DragonSoul_Tips % totalSoul
		for itemCoding, itemCnt in totalitems.iteritems():
			role.AddItem(itemCoding, itemCnt)
			tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt)
		
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveTTOneKeyData, (nowIndex, nowLayer, nowScore))
		role.Msg(2, 0, tips)
		
		if nowScore:
			wtd = WorldDataNotSync.WorldDataPrivate[WorldDataNotSync.TeamTowerFinishDict]
			wtd[nowIndex] = wtd.get(nowIndex, 0) + 1
			WorldDataNotSync.WorldDataPrivate.HasChange()
		
		Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_TT, 1))

############################################################################
def OnRoleExit(role, param):
	team = role.GetTeam()
	if not team:
		return
	#有队伍则退出队伍
	if EnumTeamType.IsTeamTowerType(team.team_type):
		#离开队伍
		team.Quit(role)


def AfterLogin(role, param):
	ttdata = role.GetObj(EnumObj.TeamTowerData)
	if not ttdata:
		role.SetObj(EnumObj.TeamTowerData, {1:{},  3 : [0, 0, 0]})
	else:
		#新增每日记录通关数据
		if 3 not in ttdata:
			ttdata[3] = [0, 0, 0]

def SyncRoleOtherData(role, param):
	role.SendObj(TTMirror.TT_S_ShowData, role.GetObj(EnumObj.TeamTowerData)[1])
	bestData = role.GetObj(EnumObj.TeamTowerData).get(2, [0, 0])
	if SDHFunGather.StartFlag[SDHDefine.TeamTower] is True:
		role.SendObj(TTMirror.TT_S_SyncBest, bestData)

def RoleDayClear(role, param):
	if 3 not in role.GetObj(EnumObj.TeamTowerData):
		return
	role.GetObj(EnumObj.TeamTowerData)[3] = [0, 0, 0]


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#事件
		Event.RegEvent(Event.Eve_BeforeExit, OnRoleExit)
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		#注册消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TT_OnOpenPanel", "客户端请求打开组队爬塔大厅面板"), OpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TT_SetRewardModel", "客户端请求设置组队爬塔无奖励模式"), SetRewardModel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TT_TTWorldCall", "客户端请求组队爬塔世界邀请"), TTWorldCall)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TT_RequestTTStart", "客户端请求开始组队爬塔"), RequestTTStart)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TT_RequestInvite", "客户端请求组队爬塔邀请好友"), RequestInvite)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TT_FastJoinTeam", "客户端请求组队爬塔快速组队"), FastJoinTeam)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TT_SetAutoJoinTT", "客户端请求设置组队爬塔自动接受邀请"), SetAutoJoinTT)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TT_OneKeyReward", "客户端请求组队爬塔一键收益"), OneKeyReward)
		
		
		
