#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.LostScene.LostSceneMgr")
#===============================================================================
# 迷失之境
#===============================================================================
import Environment
import random
import cRoleMgr
import cProcess
import cDateTime
from World import Define
from Common.Message import AutoMessage
from Game.Team import TeamBase, EnumTeamType
from Game.Role.Data import EnumTempObj, EnumInt1, EnumCD, EnumObj, EnumInt32
from Common.Other import EnumGameConfig, EnumRoleStatus, GlobalPrompt
from Game.Role import Status, Event
from Game.LostScene import LostSceneMirror, LostSceneConfig
from Game.CrossTeamTower import CrossTTMgr
from ComplexServer.Log import AutoLog

if "_HasLoad" not in dir():
	LostSceneSkillFun_Dict = {}
	LostSceneInviteCD_Dict = {}

	#队伍ID,队长名字,队伍人数
	LostScene_Syn_OpenData = AutoMessage.AllotMessage("LostScene_Syn_OpenData", "打开迷失之境面板同步数据")
	#{以兑换道具coding:已兑换数量}
	LostScene_ExchangeData = AutoMessage.AllotMessage("LostScene_ExchangeData", "冒险商店兑换数据")
	#邀请者名字, 队伍id
	LostScene_Invite = AutoMessage.AllotMessage("LostScene_Invite", "迷失之境邀请")
	#技能释放成功
	LostScene_UseSkill = AutoMessage.AllotMessage("LostScene_UseSkill", "迷失之境技能释放成功")
	
	
	LostSceneExchange_Log = AutoLog.AutoTransaction("LostSceneExchange_Log", "迷失之境兑换日志")
	LostSceneArrest_Log = AutoLog.AutoTransaction("LostSceneArrest_Log", "迷失之境抓捕成功日志")
	
def RequestOpenPanel(role, msg):
	'''
	请求打开组队面板
	@param role:
	@param msg:
	'''
	#同步所有队伍信息
	sendList = []
	for team in TeamBase.LOSTSCENE_LIST:
		#队伍是否已经在副本中
		if team.leader.GetTempObj(EnumTempObj.MirrorScene):
			continue
		#队伍ID,队长名字,队伍人数
		sendList.append((team.team_id, team.leader.GetRoleName(), len(team.members)))
	role.SendObj(LostScene_Syn_OpenData, sendList)
	
def RequestFastJoinTeam(role, msg):
	'''
	快速组队
	@param role:
	@param msg:
	'''
	if role.GetLevel() < EnumGameConfig.LostSceneNeedLevel:
		return
	if not Status.CanInStatus(role, EnumInt1.ST_Team):
		return
	
	for team in TeamBase.LOSTSCENE_LIST:
		#队伍是否已经在副本中
		if team.leader.GetTempObj(EnumTempObj.MirrorScene):
			continue
		if not team.CanJoin(role):
			continue
		team.Join(role)
	
def RequestInviteJoinTeam(role, msg):
	'''
	迷失之境客户端请求邀请组队
	@param role:
	@param msg:
	'''
	if role.GetLevel() < EnumGameConfig.LostSceneNeedLevel:
		return

	team = role.GetTeam()
	if (not team) or (len(team.members) == team.max_member_cnt) or (team.team_type != EnumTeamType.T_LostScene):
		#没有队伍 or 队伍类型不是迷失之境队伍
		return

	if role.GetTempObj(EnumTempObj.MirrorScene):
		#已经在场景中了不能邀请
		return
	
	tRoleId = msg
	if not tRoleId:
		#世界邀请
		if role.GetCD(EnumCD.LostSceneWorldInviteCD):
			return
		role.SetCD(EnumCD.LostSceneWorldInviteCD, 60)
		cRoleMgr.Msg(1, 0, GlobalPrompt.LostSceneWorldInvite % (role.GetRoleName(), 5 - len(team.members), team.team_id))
		return

	#邀请单个玩家
	tRole = cRoleMgr.FindRoleByRoleID(tRoleId)
	if not tRole:
		role.Msg(2, 0, GlobalPrompt.LostSceneInviteOutline)
		return

	#20s邀请cd
	global LostSceneInviteCD_Dict
	roleId = role.GetRoleID()
	if roleId not in LostSceneInviteCD_Dict:
		LostSceneInviteCD_Dict[roleId] = {tRoleId:cDateTime.Seconds()}
	elif tRoleId not in LostSceneInviteCD_Dict[roleId]:
		LostSceneInviteCD_Dict[roleId][tRoleId] = cDateTime.Seconds()
	else:
		cd = LostSceneInviteCD_Dict[roleId][tRoleId]
		nowSec = cDateTime.Seconds()
		if nowSec - cd < 20:
			#加个提示
			role.Msg(2, 0, GlobalPrompt.LostSceneInviteCDTips)
			return
		#更新一下cd
		LostSceneInviteCD_Dict[roleId][tRoleId] = nowSec

	if tRole.GetLevel() < EnumGameConfig.LostSceneNeedLevel:
		return
	if not Status.CanInStatus(tRole, EnumInt1.ST_Team):
		#不能进入组队状态
		return
	
	role.Msg(2, 0, GlobalPrompt.LostSceneInviteSuccess)
	
	tRole.SendObj(LostScene_Invite, (role.GetRoleName(), team.team_id))
	

def RequestBegin(role, msg):
	'''
	开始
	@param role:
	@param msg:
	'''
	if role.GetLevel() < EnumGameConfig.LostSceneNeedLevel:
		return
	
	#获取队伍
	team = role.GetTeam()
	if not team:
		return
	
	if (len(team.members) != team.max_member_cnt) or (not team.IsTeamLeader(role)) or(team.team_type != EnumTeamType.T_LostScene):
		return
	
	if not Status.CanInStatus_Roles(team.members, EnumInt1.ST_InTeamMirror):
		return
	
	LostSceneMirror.LostSceneMirror(team)
	
def RequestQuit(role, msg):
	'''
	退出
	@param role:
	@param msg:
	'''
	team = role.GetTeam()
	if (not team) or (team.team_type != EnumTeamType.T_LostScene):
		#没有队伍 or 队伍类型不是迷失之境队伍
		return

	if not role.GetTempObj(EnumTempObj.MirrorScene):
		return

	posx, posy = CrossTTMgr.GetTPPox()
	role.Revive(EnumGameConfig.CTT_SCENE_ID, posx, posy)
	
def GetTPPox():
	posx1, posx2, posy1, posy2 = EnumGameConfig.KuafuPosRandomRange[random.randint(0, 3)]
	return (random.randint(posx1, posx2), random.randint(posy1, posy2))

def RequestUseSkill(role, msg):
	'''
	使用技能
	@param role:
	@param msg:skillId
	'''
	team = role.GetTeam()
	if (not team) or (team.team_type != EnumTeamType.T_LostScene):
		#没有队伍 or 队伍类型不是迷失之境队伍
		return

	mirrorScene = role.GetTempObj(EnumTempObj.MirrorScene)
	if not mirrorScene:
		return

	skillData = role.GetTempObj(EnumTempObj.LostScene)
	if not skillData:
		return

	skillId, beUseId, isRole = msg
	
	if skillId not in skillData:
		return
	
	skillFun = LostSceneSkillFun_Dict.get(skillId)
	if not skillFun:
		return
	skillFun(role, skillId, skillData, mirrorScene, beUseId, isRole)
	
def RequestTurnCard(role, msg):
	'''
	翻牌
	@param role:
	@param msg:None
	'''
	posIndex = msg
	if posIndex not in (1,2,3,4,5):
		return
	
	team = role.GetTeam()
	if (not team) or (team.team_type != EnumTeamType.T_LostScene):
		#没有队伍 or 队伍类型不是迷失之境队伍
		return

	mirrorScene = role.GetTempObj(EnumTempObj.MirrorScene)
	if not mirrorScene:
		return
	
	mirrorScene.TurnCard(role, posIndex)
	
def RequestExchange(role, msg):
	'''
	兑换
	@param role:
	@param msg:
	'''
	if role.GetLevel() < EnumGameConfig.LostSceneNeedLevel:
		return
	
	coding, cnt = msg
	
	if (not cnt) or (not coding):
		return
	
	#背包满
	if role.PackageIsFull():
		return
	
	cfg = LostSceneConfig.LostSceneExchange_Dict.get(coding)
	if not cfg:
		print "GE_EXC, LostSceneMgr can not find coding:(%s) in LostSceneExchange_Dict" % coding
		return
	exDict = role.GetObj(EnumObj.LostSceneObj).get(1)
	if exDict is None:
		return
	nowCnt = exDict.get(coding, 0)
	
	if cfg.limitCnt:
		if nowCnt + cnt > cfg.limitCnt:
			return
	
	needScore = cfg.needScore * cnt
	if needScore > role.GetI32(EnumInt32.LostSceneScore):
		return
	
	with LostSceneExchange_Log:
		role.DecI32(EnumInt32.LostSceneScore, needScore)
		
		role.AddItem(coding, cnt)
		
		tips = GlobalPrompt.LostSceneExchangeSUC
		
		if cfg.limitCnt:
			exDict[coding] = nowCnt + cnt
			role.GetObj(EnumObj.LostSceneObj)[1] = exDict
			role.SendObj(LostScene_ExchangeData, exDict)
			
			tips += GlobalPrompt.Item_Tips % (coding, cnt)
	
	role.Msg(2, 0, tips)
#===============================================================================
# 技能
#===============================================================================
def UseSpeedSkill(role, skillId, skillData, mirrorScene, beUseId=None, isRole=False):
	#极速
	#冷却时间9秒，持续5秒，移动速度增加150%。无特效。
	if role.GetRoleID() != mirrorScene.findRoleId:
		return
	if (not mirrorScene.canUseSkill) or (not mirrorScene.allCanUseSkill):
		return
	
	nowSec = cDateTime.Seconds()
	if skillData[skillId] > nowSec:
		return
	skillData[skillId] = nowSec + 9
	role.SetTempObj(EnumTempObj.LostScene, skillData)
	
	role.SendObj(LostSceneMirror.LostSceneSkillData, skillData)
	
	roleSpeed = role.GetMoveSpeed()
	
	role.SetMoveSpeed(int(roleSpeed * 1.5))
	
	role.SendObj(LostScene_UseSkill, skillId)
	
	role.RegTick(5, FinishSpeedSkill, roleSpeed)
	
	role.Msg(2, 0, GlobalPrompt.LostSceneUseSpeedSkill)
	
def FinishSpeedSkill(role, callargv, regparam):
	roleSpeed = regparam
	role.SetMoveSpeed(roleSpeed)
	
def UseFindSkill(role, skillId, skillData, mirrorScene, beUseId=None, isRole=False):
	#侦测
	#自身位置
	if role.GetRoleID() != mirrorScene.findRoleId:
		return
	if (not mirrorScene.canUseSkill) or (not mirrorScene.allCanUseSkill):
		return
	
	nowSec = cDateTime.Seconds()
	if skillData[skillId] > nowSec:
		return
	skillData[skillId] = nowSec + 5
	role.SetTempObj(EnumTempObj.LostScene, skillData)
	
	role.SendObj(LostSceneMirror.LostSceneSkillData, skillData)
	
	posX, posY = role.GetPos()
	#计算侦测范围
	X = EnumGameConfig.LostSceneFindRangeX
	Y = EnumGameConfig.LostSceneFindRangeY
	minX, minY, maxX, maxY = posX - X, posY - Y, posX + X, posY + Y
	roleId = role.GetRoleID()
	
	haveRole = False
	
	#检测玩家
	for rd in mirrorScene.rewardDict[LostSceneMirror.EnumTick].keys():
		if rd == roleId:
			continue
		tRole = cRoleMgr.FindRoleByRoleID(rd)
		if not tRole:
			continue
		if not tRole.GetTempObj(EnumTempObj.MirrorScene):
			continue
		tmpX, tmpY = tRole.GetPos()
		
		if (minX <= tmpX <= maxX) and (minY <= tmpY <= maxY):
			#侦测到人
			haveRole = True
			break
	#检测假人
	if not haveRole:
		for npc in mirrorScene.mirrorNPCDict.values():
			if not npc.roleId:
				continue
			haveRole = True
			break
	
	if haveRole:
		role.SetAppStatus(EnumRoleStatus.LostScene_Find)
		
		role.RegTick(5, FinishFindSkill, None)
	else:
		role.Msg(2, 0, GlobalPrompt.LostSceneTips_4)
	
	role.SendObj(LostScene_UseSkill, skillId)
	
def FinishFindSkill(role, callargv, regparam):
	role.SetAppStatus(0)
	
def UseArrestSkill(role, skillId, skillData, mirrorScene, beUseId=None, isRole=False):
	#抓捕
	if role.GetRoleID() != mirrorScene.findRoleId:
		return
	if (not mirrorScene.canUseSkill) or (not mirrorScene.allCanUseSkill):
		return
	
	nowSec = cDateTime.Seconds()
	if skillData[skillId] > nowSec:
		return
	skillData[skillId] = nowSec + 5
	role.SetTempObj(EnumTempObj.LostScene, skillData)
	
	role.SendObj(LostSceneMirror.LostSceneSkillData, skillData)
	
	if not isRole:
		#获取npc
		beUseRole = mirrorScene.mirrorNPCDict.get(beUseId)
		if not beUseRole:
			return
	else:
		#获取角色role
		beUseRole = cRoleMgr.FindRoleByRoleID(beUseId)
		if not beUseRole:
			return
	
	(rx, ry), (tx, ty) = role.GetPos(), beUseRole.GetPos()
	if abs(tx - rx) > EnumGameConfig.LostSceneFindRangeX or abs(ty - ry) > EnumGameConfig.LostSceneFindRangeY:
		#超出距离
		return
	
	X = EnumGameConfig.LostSceneArrestRangeX
	Y = EnumGameConfig.LostSceneArrestRangeY
	minX, minY, maxX, maxY = tx - X, ty - Y, tx + X, ty + Y
	
	roleDict = {}
	
	#检测玩家
	for rd in mirrorScene.roleIdSet:
		tRole = cRoleMgr.FindRoleByRoleID(rd)
		if not tRole:
			continue
		if not tRole.GetTempObj(EnumTempObj.MirrorScene):
			continue
		tmpX, tmpY = tRole.GetPos()
		
		if (minX <= tmpX <= maxX) and (minY <= tmpY <= maxY):
			#侦测到人
			roleDict[rd] = tRole
			continue
	
	#检测假人
	npcSet = set()
	for npc in mirrorScene.mirrorNPCDict.values():
		if not npc.roleId:
			continue
		tmpX, tmpY = npc.GetPos()
		
		if (minX <= tmpX <= maxX) and (minY <= tmpY <= maxY):
			#侦测到人
			roleDict[npc.roleId] = None
			npcSet.add(npc.GetNPCID())
			continue
	
	#删除npc
	for npcId in npcSet:
		npc = mirrorScene.mirrorNPCDict.get(npcId)
		if npc:
			npc.Destroy()
	
	#抓到玩家
	with LostSceneArrest_Log:
		isSuc = False
		for findRoleId, findRole in roleDict.iteritems():
			if mirrorScene.FindOne(role, findRoleId, findRole):
				isSuc = True
		if isSuc:
			AutoLog.LogBase(role.GetRoleID(), AutoLog.eveLostSceneFind, 1)
		else:
			AutoLog.LogBase(role.GetRoleID(), AutoLog.eveLostSceneFind, 0)
	
	role.SendObj(LostScene_UseSkill, skillId)
	
def UseChangeSkill(role, skillId, skillData, mirrorScene, beUseId=None, isRole=False):
	#变身
	if role.GetRoleID() not in mirrorScene.rewardDict[LostSceneMirror.EnumTick]:
		return
	
	if not mirrorScene.allCanUseSkill:
		return
	
	nowSec = cDateTime.Seconds()
	if skillData[skillId] > nowSec:
		return
	skillData[skillId] = nowSec + 5
	role.SetTempObj(EnumTempObj.LostScene, skillData)
	
	role.SendObj(LostSceneMirror.LostSceneSkillData, skillData)
	
	apps = LostSceneConfig.LostSceneSkillRoleStatus_Dict.get(skillId)
	if not apps:
		return
	
	role.SetAppStatus(apps)
	
	role.SendObj(LostScene_UseSkill, skillId)
	
def LoadSkillFun():
	global LostSceneSkillFun_Dict
	LostSceneSkillFun_Dict = {}
	
	LostSceneSkillFun_Dict[1] = UseSpeedSkill
	LostSceneSkillFun_Dict[2] = UseFindSkill
	LostSceneSkillFun_Dict[3] = UseArrestSkill
	LostSceneSkillFun_Dict[4] = UseChangeSkill
	LostSceneSkillFun_Dict[5] = UseChangeSkill
	LostSceneSkillFun_Dict[6] = UseChangeSkill
	
#===============================================================================
# 事件
#===============================================================================
def AfterLogin(role, param):
	lostSceneObj = role.GetObj(EnumObj.LostSceneObj)
	if not lostSceneObj:
		role.SetObj(EnumObj.LostSceneObj, {1:{}})
	if 1 not in lostSceneObj:
		role.GetObj(EnumObj.LostSceneObj)[1] = {}
	
def ClientLost(role, param):
	team = role.GetTeam()
	if not team:
		return
	if team.team_type != EnumTeamType.T_LostScene:
		return
	#离开队伍
	team.Quit(role)
	
def SyncRoleOtherData(role, param):
	#上线同步兑换数据
	role.SendObj(LostScene_ExchangeData, role.GetObj(EnumObj.LostSceneObj).get(1, {}))
	
def RoleDayClear(role, param):
	#每日清理兑换数据
	if role.GetObj(EnumObj.LostSceneObj):
		role.GetObj(EnumObj.LostSceneObj)[1] = {}
	role.SendObj(LostScene_ExchangeData, role.GetObj(EnumObj.LostSceneObj).get(1, {}))
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.IsDevelop or Environment.EnvIsQQ() or Environment.EnvIsFT()):
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
	
	if Environment.HasLogic and (Environment.IsDevelop or Environment.EnvIsQQ() or Environment.EnvIsFT()):
		if Environment.IsCross and cProcess.ProcessID == Define.GetCrossID_2():
			
			LoadSkillFun()
			
			Event.RegEvent(Event.Eve_BeforeExit, ClientLost)
			Event.RegEvent(Event.Eve_ClientLost, ClientLost)
			Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
			
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("LS_OpenPanel", "迷失之境客户端请求打开组队面板"), RequestOpenPanel)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("LS_Begin", "迷失之境客户端请求开始"), RequestBegin)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("LS_Quit", "迷失之境客户端请求退出"), RequestQuit)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("LS_UseSkill", "迷失之境客户端请求使用技能"), RequestUseSkill)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("LS_TurnCard", "迷失之境客户端请求翻牌"), RequestTurnCard)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("LS_Exchange", "冒险商店兑换"), RequestExchange)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("LS_FastJoinTeam", "迷失之境客户端请求快速组队"), RequestFastJoinTeam)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("LS_InviteJoinTeam", "迷失之境客户端请求邀请组队"), RequestInviteJoinTeam)
			