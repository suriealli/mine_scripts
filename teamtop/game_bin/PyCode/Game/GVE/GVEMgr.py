#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.GVE.GVEMgr")
#===============================================================================
# GVE管理
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from Game.GVE import GVEConfig, GVEMirror
from Game.Role import Status, Event
from Game.Role.Data import EnumInt1, EnumObj, EnumTempObj, EnumCD, EnumDayInt8
from Game.Team import EnumTeamType, TeamBase
from Game.VIP import VIPConfig

if "_HasLoad" not in dir():
	#消息
	GVE_Show_Main_Panel = AutoMessage.AllotMessage("GVE_Show_Main_Panel", "通知客户端显示GVE主面板")
	GVE_Show_Invite_Panel = AutoMessage.AllotMessage("GVE_Show_Invite_Panel", "通知客户端显示GVE邀请面板")
	GVE_Show_Invite_Data = AutoMessage.AllotMessage("GVE_Show_Invite_Data", "通知客户端显示GVE邀请信息")
	
	GVE_WORLD_CALL_CD = 20	#GVE世界邀请CD
	GVE_BUY_CNT_NEED_RMB = 50	#购买GVE副本次数消耗的RMB
	
def IsDragonLevelMeetCondition(team, needLevel):
	for member in team.members:
		dragonMgr = member.GetTempObj(EnumTempObj.DragonMgr)
		#判断神龙等级
		if dragonMgr.level < needLevel:
			return False
	
	return True
	
def ChooseGVEFB(role, fbId):
	'''
	选择GVE副本
	@param role:
	@param fbId:
	'''
	team = role.GetTeam()
	if not team:
		return
	
	#是否队长
	if not team.IsTeamLeader(role):
		return
	
	#获取GVE副本配置
	fbConfig = GVEConfig.GVE_FB.get(fbId)
	if not fbConfig:
		return
	
	#是否已经选择了相同的副本
	if team.fb_id == fbId:
		return
	
	dragonMgr = role.GetTempObj(EnumTempObj.DragonMgr)
	#判断神龙等级
	if dragonMgr.level < fbConfig.needLevel:
		return
	
	#设置副本
	team.fb_id = fbId
	
	#同步整个队伍
	team.SyncClient()
	
def GVEStart(role, fbId):
	#获取队伍
	team = role.GetTeam()
	if not team:
		return
	
	#判断组队类型
	if team.team_type != EnumTeamType.T_GVE:
		return
	
	#队伍人数是否满足条件
	needMemberCnt = team.max_member_cnt - len(team.members)
	if needMemberCnt > 0:
		#提示
		role.Msg(2, 0, GlobalPrompt.GVE_NEED_CAREER_PROMPT % needMemberCnt)
		return
		
	#配置
	fbConfig = GVEConfig.GVE_FB.get(fbId)
	if not fbConfig:
		return
	
	#队伍神龙等级是否足够
	if IsDragonLevelMeetCondition(team, fbConfig.needLevel) is False:
		#提示
		role.Msg(2, 0, GlobalPrompt.GVE_NEED_DRAGON_LEVEL_PROMPT % fbConfig.needLevel)
		return
	
	#队伍能否进入战斗状态
	if not Status.CanInStatus_Roles(team.members, EnumInt1.ST_InTeamMirror):
		return
	
	#创建GVE多人副本
	GVEMirror.GVEMirror(team, fbConfig)
	
def GVEWorldCall(role):
	team = role.GetTeam()
	if not team:
		return
	
	#CD时间
	cd = role.GetCD(EnumCD.GVEWorldCallCD)
	if cd > 0:
		return
	
	#队伍是否已满
	if team.IsFull():
		#提示
		role.Msg(2, 0, GlobalPrompt.GVE_TEAM_FULL_CANT_INVITE_PROMPT)
		return
	
	role.SetCD(EnumCD.GVEWorldCallCD, GVE_WORLD_CALL_CD)
	
	#传闻
	needMemberCnt = team.max_member_cnt - len(team.members)
	cRoleMgr.Msg(7, 0, GlobalPrompt.GVE_WORLD_CALL % (team.leader.GetRoleName(), needMemberCnt, team.team_id))
	
def SetGVENoReward(role):
	if role.GetI1(EnumInt1.GVEFBNotCost) is True:
		role.SetI1(EnumInt1.GVEFBNotCost, False)
	else:
		role.SetI1(EnumInt1.GVEFBNotCost, True)
	
def RandomJoinTeam(role):
	#状态判断
	if not Status.CanInStatus(role, EnumInt1.ST_Team):
		return
	
	for team in TeamBase.GVE_TEAM_LIST:
		#队伍是否已经在副本中
		if team.leader.GetTempObj(EnumTempObj.MirrorScene):
			continue
		
		if not team.CanJoin(role):
			continue
	
		team.Join(role)
		
def GVEInviteFriend(role, desRoleId):
	'''
	GVE邀请好友
	@param role:
	@param desRoleId:
	'''
	team = role.GetTeam()
	if not team:
		return
	
	if not team.CanInvite(role):
		return
	
	#是否已经在副本中
	if role.GetTempObj(EnumTempObj.MirrorScene):
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
	
	#队伍id, 玩家名
	desRole.SendObjAndBack(GVE_Show_Invite_Data, role.GetRoleName(), 120, InviteBack, (team.team_id, sceneId, x, y))
	
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
	
	#加入队伍
	team.AddMember(role)

	#传送
	role.Revive(sceneId, x, y)
	
def GVEFinishCardReward(role):
	mirror = role.GetTempObj(EnumTempObj.MirrorScene)
	if not mirror:
		return
	
	if not isinstance(mirror, GVEMirror.GVEMirror):
		return
	
	mirror.GetCardReward(role)
	
def GVEBuyCnt(role):
	vipLevel = role.GetVIP()
	vipConfig = VIPConfig._VIP_BASE.get(vipLevel)
	if not vipConfig:
		return
	
	if role.GetDI8(EnumDayInt8.GVEFBBuyCnt) >= vipConfig.gve:
		return
	
	#消耗RMB
	if role.GetRMB() < GVE_BUY_CNT_NEED_RMB:
		return
	role.DecRMB(GVE_BUY_CNT_NEED_RMB)
	
	role.IncDI8(EnumDayInt8.GVEFBBuyCnt, 1)
	
#===============================================================================
# 显示
#===============================================================================
def ShowGVEMainPanel(role):
	'''
	显示GVE主面板
	@param role:
	'''
	sendList = []
	for team in TeamBase.GVE_TEAM_LIST:
		#队伍是否已经在副本中
		if team.leader.GetTempObj(EnumTempObj.MirrorScene):
			continue
		#队伍ID，队长名字，副本ID，队伍人数
		sendList.append((team.team_id, team.leader.GetRoleName(), team.fb_id, len(team.members)))
	
	#同步客户端
	role.SendObj(GVE_Show_Main_Panel, sendList)
	
def ShowGVEInvitePanel(role):
	'''
	显示GVE邀请面板
	@param role:
	'''
	#好友字典
	friendDict = role.GetObj(EnumObj.Social_Friend)
	
	sendFriendList = []
	for friendId in friendDict.iterkeys():
		friend = cRoleMgr.FindRoleByRoleID(friendId)
		if not friend:
			continue
		sendFriendList.append((friend.GetRoleID(), friend.GetRoleName(), friend.GetDragonCareerID(), friend.GetLevel()))
	
	role.SendObj(GVE_Show_Invite_Panel, sendFriendList)
	
#===============================================================================
# 事件
#===============================================================================
def OnRoleExit(role, param):
	'''
	角色离线
	@param role:
	@param param:
	'''
	team = role.GetTeam()
	
	if not team:
		return
	
	#有队伍则退出队伍
	if team.team_type == EnumTeamType.T_GVE:
		#离开队伍
		team.Quit(role)
	
#===============================================================================
# 客户端请求
#===============================================================================
def RequestOpenGVEMainPanel(role, msg):
	'''
	客户端请求打开GVE主面板
	@param role:
	@param msg:
	'''
	ShowGVEMainPanel(role)
	
def RequestOpenGVEInvitePanel(role, msg):
	'''
	客户端请求打开GVE邀请面板
	@param role:
	@param msg:
	'''
	ShowGVEInvitePanel(role)
	
def RequestChooseGVEFB(role, msg):
	'''
	客户端请求选择GVE副本
	@param role:
	@param msg:
	'''
	fbId = msg
	
	ChooseGVEFB(role, fbId)
	
def RequestGVEStart(role, msg):
	'''
	客户端请求GVE开始
	@param role:
	@param msg:
	'''
	fbId = msg
	
	GVEStart(role, fbId)
	
def RequestGVEWorldCall(role, msg):
	'''
	客户端请求GVE世界邀请
	@param role:
	@param msg:
	'''
	GVEWorldCall(role)

def RequestGVESetNoReward(role, msg):
	'''
	客户端请求GVE设置无奖励模式
	@param role:
	@param msg:
	'''
	SetGVENoReward(role)
	
def RequestGVERandomJoinTeam(role, msg):
	'''
	客户端请求GVE随缘组队
	@param role:
	@param msg:
	'''
	RandomJoinTeam(role)
	
def RequestGVEInviteFriend(role, msg):
	'''
	客户端请求GVE邀请好友
	@param role:
	@param msg:
	'''
	friendRoleId = msg
	
	GVEInviteFriend(role, friendRoleId)
	
def RequestGVEFinishCardReward(role, msg):
	'''
	客户端请求GVE通关翻牌奖励
	@param role:
	@param msg:
	'''
	GVEFinishCardReward(role)
	
def RequestGVEBuyCnt(role, msg):
	'''
	客户端请求GVE购买次数
	@param role:
	@param msg:
	'''
	GVEBuyCnt(role)
	

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross and (Environment.EnvIsNA() or Environment.IsDevelop):
		#事件
		Event.RegEvent(Event.Eve_BeforeExit, OnRoleExit)
		
		#注册消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GVE_Open_Main_Panel", "客户端请求打开GVE主面板"), RequestOpenGVEMainPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GVE_Open_Invite_Panel", "客户端请求打开GVE邀请面板"), RequestOpenGVEInvitePanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GVE_Choose_FB", "客户端请求选择GVE副本"), RequestChooseGVEFB)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GVE_Start", "客户端请求GVE开始"), RequestGVEStart)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GVE_World_Call", "客户端请求GVE世界邀请"), RequestGVEWorldCall)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GVE_Set_No_Reward", "客户端请求GVE设置无奖励模式"), RequestGVESetNoReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GVE_Random_Join_Team", "客户端请求GVE随缘组队"), RequestGVERandomJoinTeam)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GVE_Invite_Friend", "客户端请求GVE邀请好友"), RequestGVEInviteFriend)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GVE_Finish_Card_Reward", "客户端请求GVE通关翻牌奖励"), RequestGVEFinishCardReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GVE_Buy_Cnt", "客户端请求GVE购买次数"), RequestGVEBuyCnt)
		
	