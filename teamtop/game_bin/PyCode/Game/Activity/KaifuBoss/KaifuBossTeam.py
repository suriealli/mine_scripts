#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.KaifuBoss.KaifuBossTeam")
#===============================================================================
# 开服boss组队相关
#===============================================================================

import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Role import Status
from Game.Role.Data import EnumInt1, EnumObj, EnumInt8
from Game.Team import EnumTeamType, TeamBase

if "_HasLoad" not in dir():
	Sync_kaifuBoss_SeverTeams_Data = AutoMessage.AllotMessage("Sync_kaifuBoss_SeverTeams_Data", "同步开服boss全服组队信息")
	Show_KaifuBoss_Invite_Data = AutoMessage.AllotMessage("Show_KaifuBoss_Invite_Data", "通知客户端显示开服boss组队邀请信息")
	Show_KaifuBoss_Apply_Leader_Panel = AutoMessage.AllotMessage("Show_KaifuBoss_Apply_Leader_Panel", "通知客户端显示开服boss申请队长面板")

def CanCreateTeam(role, teamType):
	#是否已经有队伍
	if role.HasTeam():
		return False
	#组队状态判断
	if not Status.CanInStatus(role, EnumInt1.ST_Team):
		return False
	#组队类型是否合法
	if teamType != EnumTeamType.T_KaifuBoss:
		return False

	return True

def CreateTeam(role, teamType):
	'''
	创建
	@param role:
	@param teamType:
	'''
	#是否满足创建队伍条件
	if not CanCreateTeam(role, teamType):
		return
	#开服boss组队需要传入对应的场景
	if teamType != EnumTeamType.T_KaifuBoss:
		return
	role.Revive(64, 1000, 900)
	#创建队伍
	TeamBase.TeamBase(role, teamType)
	
def DismissTeam(role):
	'''
	解散队伍
	@param role:
	'''
	team = role.GetTeam()
	if not team :
		return
	
	if not team.CanDismiss(role):
		return
	
	team.Dismiss()
	
def JoinTeam(role, teamId):
	'''
	加入队伍
	@param role:
	@param teamId:
	'''
	
	team = TeamBase.GetTeamByTeamID(teamId)
	if not team:
		#提示
		role.Msg(2, 0, GlobalPrompt.TEAM_NOT_EXIST_PROMPT)
		return
	
	if not team.CanJoin(role):
		return
	if Status.IsInStatus(team.leader, EnumInt1.ST_FightStatus):
		#提示
		role.Msg(2, 0, GlobalPrompt.TEAM_IN_FIGHT_PROMPT)
		return
	sceneId = team.leader.GetSceneID()
	x, y = team.leader.GetPos()
	role.Revive(sceneId, x, y)
	team.Join(role)
	
def QuitTeam(role):
	'''
	退出队伍
	@param role:
	'''
	team = role.GetTeam()
	if not team:
		return
	
	if not team.CanQuit(role):
		return
	
	team.Quit(role)
	
def KickTeamMember(role, memberId):
	'''
	踢掉队伍成员
	@param role:
	@param memberId:
	'''
	team = role.GetTeam()
	if not team:
		return
	
	if not team.CanKick(role):
		return
	
	member = cRoleMgr.FindRoleByRoleID(memberId)
	if not member:
		return
	
	if member not in team.members:
		return
	
	team.Kick(member)
	
def TransferTeamLeader(role, memberId):
	'''
	转让队长
	@param role:
	@param memberId:
	'''
	roleId = role.GetRoleID()
	if roleId == memberId:
		#不能转让给自己
		return
	
	team = role.GetTeam()
	if not team:
		return
	
	if not team.IsTeamLeader(role):
		return
	
	member = cRoleMgr.FindRoleByRoleID(memberId)
	if not member:
		return
	
	if member not in team.members:
		return
	
	team.NewLeader(member)
	
def ApplyTeamLeader(role, backFunId):
	'''
	申请队长
	@param role:
	@param backFunId:
	'''
	team = role.GetTeam()
	if not team:
		return
	
	#队长不能申请队长
	if team.IsTeamLeader(role):
		return
	
	#是否队伍成员
	if role not in team.members:
		return
	#通知队长
	team.leader.SendObjAndBack(Show_KaifuBoss_Apply_Leader_Panel, role.GetRoleName(), 80, OnBackApplyLeader, role.GetRoleID())
	
	#回调客户端申请成功
	role.CallBackFunction(backFunId, None)
	
def TeamChangePos(role, pos1, pos2):
	'''
	交换队伍内位置
	@param role:
	@param pos1:
	@param pos2:
	'''
	#位置是否合法
	if pos1 not in (1, 2, 3) or pos2 not in (1, 2, 3):
		return
	if pos1 == pos2:
		return
	
	team = role.GetTeam()
	#队伍不存在
	if not team:
		return
	
	#不是队长
	if not team.IsTeamLeader(role):
		return
	
	team.ChangePos(pos1, pos2)
	
def TeamInvite(role, desRoleId):
	'''
	组队邀请
	@param role:
	@param desRoleId:
	'''
	team = role.GetTeam()
	if not team:
		return
	
	if not team.CanInvite(role):
		return
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
	
	#被邀请是否满足组队等级条件
	if desRole.GetLevel() < EnumGameConfig.KaifuBossNeedLevel:
		return
	
	if not team.CanBeInvite(desRole):
		return
	
	
	if not desRoleId in role.GetObj(EnumObj.Social_Friend):
		return
	#队长的位置
	sceneId = role.GetSceneID()
	x, y = role.GetPos()
	
	#队伍id, 玩家名, 副本ID
	desRole.SendObjAndBack(Show_KaifuBoss_Invite_Data, (team.team_id, role.GetRoleName(), role.GetI8(EnumInt8.UnionFBId)), 120, InviteBack, (team.team_id, sceneId, x, y))

def ShowTeams(role):
	'''
	显示开服boss所有队伍
	@param role:
	'''
	teamlist = TeamBase.KAIFUBOSS_TEAM_LIST
	sendList = []
	for team in teamlist:
		#队伍是否正在战斗中
		if Status.IsInStatus(team.leader, EnumInt1.ST_FightStatus):
			continue
		#队伍ID，队长头像(性别, 职业, 进阶)，队长名，队伍人数
		sendList.append((team.team_id, team.leader.GetSex(), team.leader.GetCareer(), team.leader.GetGrade(), team.leader.GetRoleName(), len(team.members)))
	#同步客户端
	role.SendObj(Sync_kaifuBoss_SeverTeams_Data, sendList)

#===============================================================================
# 回调函数
#===============================================================================
def OnBackApplyLeader(role, callArgv, regparam):
	'''
	申请队伍回调
	@param role:
	@param callArgv:
	@param regparam:
	'''
	yesOrNo = callArgv
	if not yesOrNo:
		return
	
	memberId = regparam
	
	if yesOrNo == 1:
		#同意
		TransferTeamLeader(role, memberId)
	elif yesOrNo == 2:
		#拒绝
		pass
	else:
		pass

def InviteBack(role, callargv, regparam):
	'''
	邀请回调
	@param role:
	@param callargv:
	@param regparam:
	'''
	teamId, sceneId, x, y = regparam
	
	#被邀请的角色回调函数
	if callargv != 1:
		#拒绝加入组队
		return
	
	if teamId == 0:
		#提示
		role.Msg(2, 0, GlobalPrompt.TEAM_NOT_EXIST_PROMPT)
		return
	
	team = TeamBase.GetTeamByTeamID(teamId)
	if not team:
		#提示
		role.Msg(2, 0, GlobalPrompt.TEAM_NOT_EXIST_PROMPT)
		return
	
	if not team.CanJoin(role):
		return
	
	#传送
	role.Revive(sceneId, x, y)
	
	#加入队伍
	team.AddMember(role)
#===============================================================================
# 事件
#===============================================================================
def OnSyncRoleOtherData(role, param):
	'''
	角色登陆后同步数据
	@param role:
	@param param:
	'''
	#角色登陆后调用
	team = role.GetTeam()
	# 队伍不存在了
	if not team:
		return
	#同步客户端
	team.SyncClient()
	
#===============================================================================
# 客户端请求
#===============================================================================
def RequestCreateTeam(role, msg):
	'''
	客户端请求创建队伍
	@param role:
	@param msg:
	'''
	teamType = msg
	
	#是否满足组队等级条件
	if role.GetLevel() < EnumGameConfig.KaifuBossNeedLevel:
			return
	CreateTeam(role, teamType)
	
def RequestDismissTeam(role, msg):
	'''
	客户端请求解散队伍
	@param role:
	@param msg:
	'''
	#是否满足组队等级条件
	if role.GetLevel() < EnumGameConfig.KaifuBossNeedLevel:
		return
	
	DismissTeam(role)
	
def RequestJoinTeam(role, msg):
	'''
	客户端请求加入队伍
	@param role:
	@param msg:
	'''
	teamId = msg
	
	#是否满足组队等级条件
	if role.GetLevel() < EnumGameConfig.KaifuBossNeedLevel:
		return
	JoinTeam(role, teamId)
	
def RequestQuitTeam(role, msg):
	'''
	客户端请求离开队伍
	@param role:
	@param msg:
	'''
	#是否满足组队等级条件
	if role.GetLevel() < EnumGameConfig.KaifuBossNeedLevel:
			return
	
	QuitTeam(role)
	
def RequestKickTeamMember(role, msg):
	'''
	客户端请求踢人出队伍
	@param role:
	@param msg:
	'''
	memberId = msg
	
	#是否满足组队等级条件
	if role.GetLevel() < EnumGameConfig.KaifuBossNeedLevel:
		return
	
	KickTeamMember(role, memberId)
	
def RequestTransferTeamLeader(role, msg):
	'''
	客户端请求转让队长
	@param role:
	@param msg:
	'''
	memberId = msg
	
	#是否满足组队等级条件
	if role.GetLevel() < EnumGameConfig.KaifuBossNeedLevel:
		return
	
	TransferTeamLeader(role, memberId)
	
def RequestApplyTeamLeader(role, msg):
	'''
	客户端请求申请队长
	@param role:
	@param msg:
	'''
	backFunId, _ = msg
	
	#是否满足组队等级条件
	if role.GetLevel() < EnumGameConfig.KaifuBossNeedLevel:
		return
	
	ApplyTeamLeader(role, backFunId)
	
def RequestTeamChangePos(role, msg):
	'''
	客户端请求请求改变队伍队员位置
	@param role:
	@param msg:
	'''
	pos1, pos2 = msg
	
	#是否满足组队等级条件
	if role.GetLevel() < EnumGameConfig.KaifuBossNeedLevel:
		return
	
	TeamChangePos(role, pos1, pos2)
	
def RequestTeamInvite(role, msg):
	'''
	客户端请求邀请玩家加入队伍
	@param role:
	@param msg:roleid
	'''
	desRoleId = msg
	
	#是否满足组队等级条件
	if role.GetLevel() < EnumGameConfig.KaifuBossNeedLevel:
		return
	TeamInvite(role, desRoleId)

def RequestGetTeams(role, msg):
	'''
	客户端请求获取当前队伍信息
	@param role:
	@param msg:roleid
	'''
	if role.GetLevel() < EnumGameConfig.KaifuBossNeedLevel:
		return
	ShowTeams(role)

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KaifuBoss_Team_Create", "客户端请求创建开服boss队伍"), RequestCreateTeam)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KaifuBoss_Team_Dismiss", "客户端请求解散开服boss队伍"), RequestDismissTeam)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KaifuBoss_Team_Join", "客户端请求加入开服boss队伍"), RequestJoinTeam)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KaifuBoss_Team_Quit", "客户端请求离开开服boss队伍"), RequestQuitTeam)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KaifuBoss_Team_Kick", "客户端请求踢人出开服boss队伍"), RequestKickTeamMember)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KaifuBoss_Team_Transfer_Leader", "客户端请求转让开服boss队长"), RequestTransferTeamLeader)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KaifuBoss_Team_Apply_Leader", "客户端请求申请开服boss队长"), RequestApplyTeamLeader)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KaifuBoss_Team_Change_Pos", "客户端请求请求改变开服boss队伍队员位置"), RequestTeamChangePos)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KaifuBoss_Team_Invite", "客户端请求邀请玩家加入开服boss队伍"), RequestTeamInvite)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KaifuBoss_Get_Teams", "客户端请求获取当前队伍信息"), RequestGetTeams)
