#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Team.TeamMgr")
#===============================================================================
# 队伍管理
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from Game.Role import Event, Status
from Game.Role.Data import EnumInt1, EnumInt8, EnumDayInt1
from Game.Team import TeamBase, EnumTeamType
from Game.TeamTower import TTConfig
from Game.SysData import WorldDataNotSync

if "_HasLoad" not in dir():
	#消息
	Team_Show_Invite_Data = AutoMessage.AllotMessage("Team_Show_Invite_Data", "通知客户端显示组队邀请信息")
	Team_Show_Apply_Leader_Panel = AutoMessage.AllotMessage("Team_Show_Apply_Leader_Panel", "通知客户端显示申请队长面板")
	Team_Show_ShenshuInvite_Data = AutoMessage.AllotMessage("Team_Show_ShenshuInvite_Data", "通知客户端显示神树密境组队邀请信息")
	
def CanCreateTeam(role, teamType):
	#是否已经有队伍
	if role.HasTeam():
		return False
	
	#组队状态判断
	if not Status.CanInStatus(role, EnumInt1.ST_Team):
		return False
	
	#组队类型是否合法
	if teamType < EnumTeamType.T_Base or teamType > EnumTeamType.T_Max:
		return False
	
	if teamType == EnumTeamType.T_UnionFB:
		#等级限制
		if role.GetLevel() < EnumGameConfig.TEAM_UNION_FB_NEED_LEVEL:
			return False
		#需要有公会才能创建队伍
		if not role.GetUnionID():
			return False
		if role.GetI8(EnumInt8.UnionFBId) == 0:
			#必须在里面才可以创建队伍
			return
	elif teamType == EnumTeamType.T_GVE:
		#等级限制
		if role.GetLevel() < EnumGameConfig.TEAM_GVE_NEED_LEVEL:
			return False
		#需要有神龙职业
		if not role.GetDragonCareerID():
			return False
	elif EnumTeamType.IsTeamTowerType(teamType):
		if teamType == EnumTeamType.T_TeamTower_0:
			if role.GetLevel() < EnumGameConfig.TEAM_TOWER_NEED_LEVEL_0:
				return
		else:
			if role.GetLevel() < EnumGameConfig.TEAM_TOWER_NEED_LEVEL:
				return False
		if role.GetI8(EnumInt8.UnionFBId):
			return False
		index = EnumTeamType.GetTeamTowerTypeIndex(teamType)
		#判断全服通关人数是否足够
		frontIndex = index - 1
		cfg = TTConfig.TeamTowerConfig_Dict.get(frontIndex)
		if cfg:
			fd = WorldDataNotSync.WorldDataPrivate[WorldDataNotSync.TeamTowerFinishDict]
			nowCnt = fd.get(frontIndex)
			if cfg.maxPeople:
				if not nowCnt:
					return False
				if nowCnt < cfg.maxPeople:
					return False
			#判断坐骑是否是飞行坐骑
			cfg = TTConfig.TeamTowerConfig_Dict.get(index)
			if not cfg:
				return False
			if role.GetRightMountID() not in cfg.needMountIDs:
				role.Msg(2, 0, GlobalPrompt.TT_JoinMount_Tips)
				return False
	elif teamType == EnumTeamType.T_JT:
		if not Environment.IsCross:
			return False
		if Status.IsInStatus(role, EnumInt1.ST_JTMatch):
			#匹配中
			return
	elif teamType == EnumTeamType.T_CrossTeamTower:
		if not Environment.IsCross:
			return False
		if role.GetLevel() < EnumGameConfig.CTT_NEED_LEVEL:
			return False
	elif teamType == EnumTeamType.T_LostScene:
		if not Environment.IsCross:
			return False
		if role.GetLevel() < EnumGameConfig.LostSceneNeedLevel:
			return False
		if role.GetDI1(EnumDayInt1.LostSceneIsIn):
			role.Msg(2, 0, GlobalPrompt.LostSceneCannotIn)
			return False
	elif teamType == EnumTeamType.T_Shenshumijing:
		if role.GetLevel() < EnumGameConfig.ShenshumijingLevel:
			return False
	elif EnumTeamType.IsChaosDivinityType(teamType):
		if role.GetLevel() < EnumGameConfig.ChaosDivinityLevel:
			return False
	else:
		#还没有定义规则
		return False
	
	
	return True

def CreateTeam(role, teamType):
	'''
	创建
	@param role:
	@param teamType:
	'''
	if Environment.IsCross and (teamType != EnumTeamType.T_JT and teamType != EnumTeamType.T_CrossTeamTower and teamType != EnumTeamType.T_LostScene):
		#跨服环境下只能创建这个队伍
		return
	#是否满足创建队伍条件
	if not CanCreateTeam(role, teamType):
		return
	#开服boss组队需要传入对应的场景
	if teamType == EnumTeamType.T_KaifuBoss:
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
	team =  TeamBase.GetTeamByTeamID(teamId)
	if not team:
		#提示
		role.Msg(2, 0, GlobalPrompt.TEAM_NOT_EXIST_PROMPT)
		return
	
	if not team.CanJoin(role):
		return
	
	#状态判断
	if not Status.CanInStatus(role, EnumInt1.ST_Team):
		return
	if Status.IsInStatus(team.leader, EnumInt1.ST_FightStatus):
		#提示
		role.Msg(2, 0, GlobalPrompt.TEAM_IN_FIGHT_PROMPT)
		return
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
	if memberId == role.GetRoleID():
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
	
	if team.team_type == EnumTeamType.T_JT:
		if Status.IsInStatus(role, EnumInt1.ST_JTMatch):
			return
	
	
	member = cRoleMgr.FindRoleByRoleID(memberId)
	if not member:
		return
	
	if member not in team.members:
		return
	
	team.NewLeader(member)
	role.Msg(2, 0, GlobalPrompt.TEAM_TransferTeamLeader)
	
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
	
	if team.team_type == EnumTeamType.T_JT:
		if Status.IsInStatus(role, EnumInt1.ST_JTMatch):
			return
	#通知队长
	team.leader.SendObjAndBack(Team_Show_Apply_Leader_Panel, role.GetRoleName(), 80, OnBackApplyLeader, role.GetRoleID())
	
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
	if pos1 not in (1,2,3) or pos2 not in (1,2,3):
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
	公会副本组队邀请
	@param role:
	@param desRoleId:
	'''
	unionId = role.GetUnionID()
	if not unionId:
		return
	
	team = role.GetTeam()
	if not team:
		return
	
	if team.team_type != EnumTeamType.T_UnionFB:
		print "GE_EXC T_UnionFB TeamInvite not this type (%s)" % team.team_type
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
	
	#是否同一个公会
	if unionId != desRole.GetUnionID():
		return
	
	if not team.CanBeInvite(desRole):
		return
	
	#队长的位置
	sceneId = role.GetSceneID()
	x, y = role.GetPos()
	
	#被邀请的人是否开启了自动同意邀请
	if desRole.GetI1(EnumInt1.TeamAutoAcceptInvite):
		if not team.CanJoin(desRole):
			return
		
		#传送
		desRole.Revive(sceneId, x, y)
		
		#加入队伍
		team.AddMember(desRole)
		
		return
	
	#队伍id, 玩家名, 副本ID
	desRole.SendObjAndBack(Team_Show_Invite_Data, (team.team_id, role.GetRoleName(), role.GetI8(EnumInt8.UnionFBId)), 120, InviteBack, (team.team_id, sceneId, x, y))
	
def TeamShenshuInvite(role, desRoleId):
	'''
	神数秘境组队邀请
	@param role:
	@param desRoleId:
	'''
	team = role.GetTeam()
	if not team:
		return
	
	if team.team_type != EnumTeamType.T_Shenshumijing:
		print "GE_EXC T_Shenshumijing TeamInvite not this type (%s)" % team.team_type
		return
	
	if not team.CanInvite(role):
		return
	
	from Game.Activity.Shenshumijing import Shenshumijing
	if not Shenshumijing.IsStart:
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
	
	if not team.CanBeInvite(desRole):
		return
	
	#队长的位置
	sceneId = role.GetSceneID()
	x, y = role.GetPos()
	
	#被邀请的人是否开启了自动同意邀请
	if desRole.GetI1(EnumInt1.ShenshuAutoAcceptInvite):
		if not team.CanJoin(desRole):
			return
		
		#传送
		desRole.Revive(sceneId, x, y)
		
		#加入队伍
		team.AddMember(desRole)
		
		return
	
	#队伍id, 玩家名, 副本ID
	desRole.SendObjAndBack(Team_Show_ShenshuInvite_Data, (team.team_id, role.GetRoleName()), 120, InviteBack, (team.team_id, sceneId, x, y))
	
def TeamConfirmFollower(role):
	'''
	确认跟随
	@param role:
	'''
	team = role.GetTeam()
	if not team:
		return
	
	if not team.IsTeamLeader(role):
		return
	
	team.CheckFollow()
		
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
	memberId = regparam
	if yesOrNo == 1 or yesOrNo is None:
		#同意 或者超时回调
		TransferTeamLeader(role, memberId)
#	elif yesOrNo == 2:
#		#拒绝
#		pass
#	else:
#		pass

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
	
	team =  TeamBase.GetTeamByTeamID(teamId)
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
	
	CreateTeam(role, teamType)
	
def RequestDismissTeam(role, msg):
	'''
	客户端请求解散队伍
	@param role:
	@param msg:
	'''
	DismissTeam(role)
	
def RequestJoinTeam(role, msg):
	'''
	客户端请求加入队伍
	@param role:
	@param msg:
	'''
	teamId = msg
	
	JoinTeam(role, teamId)
	
def RequestQuitTeam(role, msg):
	'''
	客户端请求离开队伍
	@param role:
	@param msg:
	'''
	QuitTeam(role)
	
def RequestKickTeamMember(role, msg):
	'''
	客户端请求踢人出队伍
	@param role:
	@param msg:
	'''
	memberId = msg
	
	KickTeamMember(role, memberId)
	
def RequestTransferTeamLeader(role,msg):
	'''
	客户端请求转让队长
	@param role:
	@param msg:
	'''
	memberId = msg
	
	TransferTeamLeader(role, memberId)
	
def RequestApplyTeamLeader(role, msg):
	'''
	客户端请求申请队长
	@param role:
	@param msg:
	'''
	backFunId, _ = msg
	
	ApplyTeamLeader(role, backFunId)
	
def RequestTeamChangePos(role, msg):
	'''
	客户端请求请求改变队伍队员位置
	@param role:
	@param msg:
	'''
	pos1, pos2 = msg
	
	TeamChangePos(role, pos1, pos2)
	
def RequestTeamInvite(role, msg):
	'''
	客户端请求邀请玩家加入队伍(公会副本专用)
	@param role:
	@param msg:roleid
	'''
	desRoleId = msg
	
	TeamInvite(role, desRoleId)
	
def RequestTeamShenshuInvite(role, msg):
	'''
	客户端请求邀请玩家加入神树密境队伍
	@param role:
	@param msg:
	'''
	TeamShenshuInvite(role, msg)
	
def RequestTeamConfirmFollower(role, msg):
	'''
	客户端请求检测跟随的队友（看不到跟随的队员了）
	@param role:
	@param msg:
	'''
	#是否满足组队等级条件
	TeamConfirmFollower(role)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		#登陆同步角色数据
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Team_Create", "客户端请求创建队伍"), RequestCreateTeam)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Team_Dismiss", "客户端请求解散队伍"), RequestDismissTeam)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Team_Join", "客户端请求加入队伍"), RequestJoinTeam)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Team_Quit", "客户端请求离开队伍"), RequestQuitTeam)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Team_Kick", "客户端请求踢人出队伍"), RequestKickTeamMember)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Team_Transfer_Leader", "客户端请求转让队长"), RequestTransferTeamLeader)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Team_Apply_Leader", "客户端请求申请队长"), RequestApplyTeamLeader)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Team_Change_Pos", "客户端请求请求改变队伍队员位置"), RequestTeamChangePos)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Team_Invite", "客户端请求邀请玩家加入队伍"), RequestTeamInvite)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Team_ConfirmFollower", "客户端请求检测跟随的队友"), RequestTeamConfirmFollower)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Team_ShenshuInvite", "客户端请求邀请玩家加入神树密境队伍"), RequestTeamShenshuInvite)
	
