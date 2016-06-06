#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.CrossTeamTower.CrossTTMgr")
#===============================================================================
# 虚空幻境
#===============================================================================
import random
import cProcess
import Environment
import cSceneMgr
import cDateTime
import cRoleMgr
import cComplexServer
from ComplexServer.Time import Cron
from World import Define
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Team import TeamBase, EnumTeamType
from Game.Role import Status, Call, Event
from Game.CrossTeamTower import CTTMirror, CTTConfig, CTTRank
from Game.GlobalData import ZoneName
from Game.Role.Data import EnumCD, EnumTempInt64, EnumInt1, EnumTempObj, EnumObj, EnumDayInt8, EnumInt32, EnumInt64, EnumInt16
from Common.Other import GlobalPrompt, EnumGameConfig

if "_HasLoad" not in dir():
	NOW_PLAYER_IN_SCENE = 0			#当前场景的人数
	
	CAN_JOIN_LOCAL = True			#是否能进的标志(本服)
	CAN_JOIN_CROSS = True			#是否能进的标志(跨服)
	
	ROLEID_ZONE_DICT = {}			#缓存玩家的服名，roleId -> zoneName
	START_TIME = 10					#神界开启时间
	END_TIME = 22					#神界关闭时间
	CTT_MIRROR_END_TIME = 23		#虚空幻境关闭时间
	
	CTT_Syn_OpenData = AutoMessage.AllotMessage("CTT_Syn_OpenData", "打开虚空幻境界面同步数据")
	CTT_S_Show_Invite_Data = AutoMessage.AllotMessage("CTT_S_Show_Invite_Data", "通知客户端虚空幻境有人邀请你")
	CTT_Syn_ExchangeData = AutoMessage.AllotMessage("CTT_Syn_ExchangeData", "同步虚空幻境兑换商店数据")
	CTT_Syn_RankData = AutoMessage.AllotMessage("CTT_Syn_RankData", "同步虚空幻境排行榜数据")
	CTT_Syn_ApplyData = AutoMessage.AllotMessage("CTT_Syn_ApplyData", "通知客户端申请入队信息")
	#日志
	Tra_CTTFreshCost = AutoLog.AutoTransaction("Tra_CTTFreshCost", "虚空幻境兑换商店刷新消耗")
	Tra_CTTBuyCost = AutoLog.AutoTransaction("Tra_CTTBuyCost", "虚空幻境兑换商店购买消耗")

def RequestTP(role, param):
	'''
	客户端请求进入虚空幻境场景
	@param role:
	@param param:
	'''
	back_Id, _ = param
	if role.GetLevel() < EnumGameConfig.CTT_JOIN_LEVEL:
		return
	if cDateTime.Hour() < START_TIME or cDateTime.Hour() > END_TIME:
		return
	global CAN_JOIN_LOCAL
	if not CAN_JOIN_LOCAL:
		role.CallBackFunction(back_Id, False)
		return
	
	if role.GetCD(EnumCD.CroSSTPCD):
		role.CallBackFunction(back_Id, False)
		return
	
	#角色状态判断
	if not Status.CanInStatus(role, EnumInt1.ST_TP):
		role.CallBackFunction(back_Id, False)
		return
	
	role.SetCD(EnumCD.CroSSTPCD, EnumGameConfig.CLICK_TP_CD)
	role.CallBackFunction(back_Id, True)
	
	posx, posy = GetTPPox()
	role.GotoCrossServer(Define.GetCrossID_2(), EnumGameConfig.CTT_SCENE_ID, posx, posy, AfterJoinKuafuParty, (ZoneName.ZoneName))
	
def GetTPPox():
	posx1, posx2, posy1, posy2 = EnumGameConfig.KuafuPosRandomRange[random.randint(0, 3)]
	return (random.randint(posx1, posx2), random.randint(posy1, posy2))

def CrossCallToSendJoinState(param):
	global CAN_JOIN_LOCAL
	CAN_JOIN_LOCAL = param
	

def RadioStartMsg():
	cRoleMgr.Msg(3, 0, GlobalPrompt.CTT_START_MSG)
	
def RadioEndMsg():
	cRoleMgr.Msg(3, 0, GlobalPrompt.CTT_END_MSG)
#=============================以下为跨服逻辑==================================
def AfterJoinKuafuParty(role, param):
	global NOW_PLAYER_IN_SCENE
	global ROLEID_ZONE_DICT
	
	NOW_PLAYER_IN_SCENE += 1
	#缓存服名
	ROLEID_ZONE_DICT[role.GetRoleID()] = param
	
	global CAN_JOIN_CROSS
	if not CAN_JOIN_CROSS:
		role.GotoLocalServer(None, None)
	
	if NOW_PLAYER_IN_SCENE > EnumGameConfig.MAX_PLAYER_IN_SCENE:
		#将玩家传回本服
		role.GotoLocalServer(None, None)
		
	if NOW_PLAYER_IN_SCENE >= EnumGameConfig.MAX_PLAYER_IN_SCENE and CAN_JOIN_CROSS:
		CAN_JOIN_CROSS = False
		#通知所有逻辑进程决赛竞猜结果
		Call.ServerCall(0, "Game.CrossTeamTower.CrossTTMgr", "CrossCallToSendJoinState", CAN_JOIN_CROSS)
	
	
def OpenPanel(role, param):
	'''
	客户端请求打开虚空幻境大厅面板
	@param role:
	@param param:
	'''
	sendList = []
	for team in TeamBase.CROSS_TEAM_TOWER_LIST:
		#队伍是否已经在副本中
		mirrorState = 0	#副本是否开启标志
		layer = 0		#爬了多少层
		MirrorScene = team.leader.GetTempObj(EnumTempObj.MirrorScene)
		if MirrorScene:
			if len(team.members) >= 3:
				continue
			mirrorState = 1
			layer = MirrorScene.layer
		#队伍ID，队长名字，副本ID，队伍人数
		sendList.append((team.team_id, team.leader.GetRoleName(), len(team.members), mirrorState, layer))
	role.SendObj(CTT_Syn_OpenData, sendList)
	role.SendObj(CTT_Syn_RankData, CTTRank.CTT.data.values())
	
def RequestCTTStart(role, param):
	'''
	客户端请求开始虚空幻境
	@param role:
	@param param:
	'''
	if role.GetLevel() < EnumGameConfig.CTT_NEED_LEVEL:
		return
	#获取队伍
	team = role.GetTeam()
	if not team:
		return
	
	if cDateTime.Hour() >= CTT_MIRROR_END_TIME:
		for member in team.members:
			member.Msg(2, 0, GlobalPrompt.CTT_MIRROR_CLOSED)
		return
	
	if len(team.members) != 3 or not team.IsTeamLeader(role):
		#人数不足
		return
	
	for member in team.members:
		nowHeroID = member.GetI64(EnumInt64.JTHeroID)
		if not nowHeroID:
			RandomCTTHero(member)
			
	#队伍能否进入战斗状态
	if not Status.CanInStatus_Roles(team.members, EnumInt1.ST_InTeamMirror):
		return
	
	#创建组队爬塔副本
	CTTMirror.CTTMirror(team)
	
def RandomCTTHero(role):
	sm = role.GetTempObj(EnumTempObj.enStationMgr)
	if len(sm.station_to_id) < 2:
		return
	for heroId in sm.station_to_id.itervalues():
		if heroId == role.GetRoleID():
			continue
		role.SetI64(EnumInt64.JTHeroID, heroId)
		
def CTTWorldCall(role, msg):
	'''
	虚空幻境世界邀请
	@param role:
	@param msg:
	'''
	team = role.GetTeam()
	if not team:
		return
	#CD时间
	if role.GetCD(EnumCD.CrossTeamTower) > 0:
		return
	#队伍是否已满
	if team.IsFull():
		return
	if not EnumTeamType.T_CrossTeamTower:
		return

	role.SetCD(EnumCD.CrossTeamTower, 60)
	
	#传闻
	cRoleMgr.Msg(7, 0, GlobalPrompt.CTT_WorldCall_Tips % (team.leader.GetRoleName(), 3 - len(team.members), team.team_id))
	
def RequestInvite(role, msg):
	'''
	客户端请求虚空幻境邀请好友
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
	
	if desRole.GetTI64(EnumTempInt64.CTT_AutoInvite):
		InviteBack(desRole, 1, team.team_id)
	else:
		#队伍id, 玩家名
		desRole.SendObjAndBack(CTT_S_Show_Invite_Data, (role.GetRoleName()), 120, InviteBack, team.team_id)
	
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
	客户端请求虚空幻境快速组队
	@param role:
	@param msg:
	'''
	#状态判断
	if not Status.CanInStatus(role, EnumInt1.ST_Team):
		return
	
	for team in TeamBase.CROSS_TEAM_TOWER_LIST:
		#队伍是否已经在副本中
		if team.leader.GetTempObj(EnumTempObj.MirrorScene):
			continue
		if not team.CanJoin(role):
			continue
		team.Join(role)

def SetAutoJoinTT(role, param):
	'''
	客户端请求虚空幻境自动组队
	@param role:
	@param msg:
	'''
	if param not in (1, 0):
		return
	role.SetTI64(EnumTempInt64.CTT_AutoInvite, param)
	
def RequestNoReward(role, param):
	'''
	客户端请求虚空幻境无奖励模式
	@param role:
	@param param:
	'''
	if param not in (1, 0):
		return
	role.SetI1(EnumInt1.CTTNoRewardState, param)
	
def RequestChangeFightHero(role, msg):
	'''
	修改虚空幻境战斗时上阵的英雄
	@param role:
	@param msg:
	'''
	#直接用了组队跨服竞技的
	heroId = msg
	hero = role.GetHero(heroId)
	if not hero or not hero.GetStationID():
		return
	if role.GetI64(EnumInt64.JTHeroID) == heroId:
		return
	team = role.GetTeam()
	if not team:
		return
	if team.team_type != EnumTeamType.T_CrossTeamTower:
		return
	role.SetI64(EnumInt64.JTHeroID, heroId)

def RequestExitScene(role, param):
	'''
	客户端请求退出神界
	@param role:
	@param param:
	'''
	role.GotoLocalServer(0, 0)
	
def RequestExchange(role, param):
	'''
	客户端请求虚空幻境兑换
	@param role:
	@param param:
	'''
	goodsId = param
	
	CTTRoleData = role.GetObj(EnumObj.CTTRoleData)
	goodsDict = CTTRoleData.get(1)

	if goodsId not in goodsDict.keys():
		return
	
	if goodsDict.get(goodsId):#已经购买过了
		return
	
	cfg = CTTConfig.CTT_EXCHANGE_DICT.get(goodsId)
	if not cfg:
		print "GE_EXC,can not find goodsID(%s) in CrossMgrTT.RequestExchange" % goodsId
		return
	
	if role.GetI32(EnumInt32.CTTPoint) < cfg.needPoint:
		return 
	
	with Tra_CTTBuyCost:
		role.DecI32(EnumInt32.CTTPoint, cfg.needPoint)
		#设置为已购买
		goodsDict[goodsId] = 1
		
		tips = GlobalPrompt.Reward_Tips
		if cfg.rewards:
			coding, cnt = cfg.rewards
			role.AddItem(coding, cnt)
			tips += GlobalPrompt.Item_Tips % (coding, cnt)
		role.SendObj(CTT_Syn_ExchangeData, goodsDict)
	
def RequestExchangePanel(role, param):
	'''
	客户端请求打开虚空幻境兑换界面
	@param role:
	@param param:
	'''
	role.SendObj(CTT_Syn_ExchangeData, role.GetObj(EnumObj.CTTRoleData).get(1))
	
def RequestFresh(role, param):
	'''
	客户端请求虚空幻境兑换商店刷新
	@param role:
	@param param:
	'''
	freshTimes = role.GetDI8(EnumDayInt8.CTTFreshTimes)
	nextfreshTimes = freshTimes + 1
	if nextfreshTimes > CTTConfig.MAX_FRESH_TIMES:
		nextfreshTimes = CTTConfig.MAX_FRESH_TIMES

	costPoint = CTTConfig.CTT_FRESH_DICT.get(nextfreshTimes)
	if not costPoint:
		print "GE_EXC,can not find freshTime(%s) in CrossTTMgr.RequestFresh" % freshTimes
		return
	if role.GetI32(EnumInt32.CTTPoint) < costPoint:
		return
	with Tra_CTTFreshCost:
		role.DecI32(EnumInt32.CTTPoint, costPoint)
		role.IncDI8(EnumDayInt8.CTTFreshTimes, 1)
		FreshGoods(role, 0)
	
def RequestExitMirror(role, param):
	'''
	客户端请求退出虚空幻境
	@param role:
	@param param:
	'''
	if not role.GetTempObj(EnumTempObj.MirrorScene):
		return
	posx, posy = GetTPPox()
	role.Revive(EnumGameConfig.CTT_SCENE_ID, posx, posy)
	
def RequestApplyTeam(role, param):
	'''
	客户端请求入队
	@param role:
	@param param:
	'''
	teamId = param
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
	if team.leader.IsKick():
		return
	if team.leader.GetTempObj(EnumTempObj.MirrorScene):
		#队伍已开始爬塔
		if len(team.members) >= 3:
			return
		team.leader.SendObjAndBack(CTT_Syn_ApplyData, (role.GetRoleName(), role.GetZDL()), 120, OnBackApplyJoinTeam, role.GetRoleID())
		role.Msg(2, 0, GlobalPrompt.CTT_APPLY_SUC)
	else:
		if Status.IsInStatus(team.leader, EnumInt1.ST_FightStatus):
			#提示
			role.Msg(2, 0, GlobalPrompt.TEAM_IN_FIGHT_PROMPT)
			return
		team.Join(role)
		
def OnBackApplyJoinTeam(role, callargv, regparam):
	#申请加入队伍回调
	if callargv != "greed":
		return
	applyId = regparam
	team = role.GetTeam()
	if not team:
		return
	if team.leader != role:
		return
	if len(team.members) >= 3:
		return
	MirrorScene = role.GetTempObj(EnumTempObj.MirrorScene)
	if not MirrorScene:
		return
	applyer = cRoleMgr.FindRoleByRoleID(applyId)
	if not applyer:
		return
	if not Status.CanInStatus(applyer, EnumInt1.ST_Team):
		return
	if not team.CanJoin(applyer):
		return
	#加入队伍
	team.AddMember(applyer)
	MirrorScene.team = team
	#队长的位置
	x, y = role.GetPos()
	MirrorScene.mirrorScene.JoinRole(applyer, x, y)
	MirrorScene.AfterJoinRole(applyer)
		
def OperationTick():
	for role in cRoleMgr.GetAllRole():
		#刷新商品
		FreshGoods(role, 1)
	
def FreshGoods(role, freshtype):
	goodsList = CTTConfig.FreashGOODs()
	if not goodsList:return
	
	goods_dict = dict((i,0) for i in goodsList)
	#设置玩家新的商品列表
	CTTRoleData = role.GetObj(EnumObj.CTTRoleData)
	CTTRoleData[1] = goods_dict
	if freshtype == 1:#系统刷新记录刷新的天数
		days = cDateTime.Days()
		CTTRoleData[2] = days
	role.SendObj(CTT_Syn_ExchangeData, CTTRoleData.get(1))
	
def RadioCrossEndMsg():
	cRoleMgr.Msg(3, 0, GlobalPrompt.CTT_CROSS_END_MSG)
	
def RadioCrossEndMsg2():
	cRoleMgr.Msg(3, 0, GlobalPrompt.CTT_CROSS_END_MSG2)
	
def RadioCrossEndMsg3():
	cRoleMgr.Msg(3, 0, GlobalPrompt.CTT_CROSS_END_MSG3)
	
def RadioCrossEndMsg4():
	cRoleMgr.Msg(3, 0, GlobalPrompt.CTT_CROSS_END_MSG4)
	cComplexServer.RegTick(60, TPRole)
	
def TPRole(callargv, regparam):
	scene = cSceneMgr.SearchPublicScene(EnumGameConfig.CTT_SCENE_ID)
	if scene:
		#将场景里的玩家清理
		for role in scene.GetAllRole():
			role.GotoLocalServer(None, None)
	
def GetRoleZoneName(role):
	global ROLEID_ZONE_DICT
	
	roleId = role.GetRoleID()
	if roleId in ROLEID_ZONE_DICT:
		return ROLEID_ZONE_DICT.get(roleId)
	return ZoneName.GetRoleZoneName(role)

def OnRoleExit(role, param):
	team = role.GetTeam()
	if team:
		#有队伍则退出队伍
		if team.team_type == EnumTeamType.T_CrossTeamTower:
			#离开队伍
			team.Quit(role)
	
	sceneId = role.GetSceneID()
	if sceneId != EnumGameConfig.CTT_SCENE_ID and sceneId not in CTTConfig.SCENE_ID_SET:
		return
	
	global NOW_PLAYER_IN_SCENE
	global ROLEID_ZONE_DICT
	
	NOW_PLAYER_IN_SCENE -= 1
	#删除服信息
	roleId = role.GetRoleID()
	if roleId in ROLEID_ZONE_DICT:
		del ROLEID_ZONE_DICT[roleId]
	
	global CAN_JOIN_CROSS
	if NOW_PLAYER_IN_SCENE <= EnumGameConfig.MAX_CLOSE_TP_CNT and not CAN_JOIN_CROSS:
		CAN_JOIN_CROSS = True
		Call.ServerCall(0, "Game.CrossTeamTower.CrossTTMgr", "CrossCallToSendJoinState", CAN_JOIN_CROSS)

def ClientLost(role, param):
	team = role.GetTeam()
	if team:
		#有队伍则退出队伍
		if team.team_type == EnumTeamType.T_CrossTeamTower:
			#离开队伍
			team.Quit(role)
		
def OnSyncRoleOtherData(role, param):
	days = cDateTime.Days()
	lastUpdataDays = role.GetObj(EnumObj.CTTRoleData).get(2)
	if days <= lastUpdataDays:
		return
	
	#判断是不是第二天
	if lastUpdataDays + 1 == days:
		#是否超过了12点
		if cDateTime.Hour() < 12:
			return
	FreshGoods(role, 1)
	
def AfterLogin(role, param):
	CTTRoleData = role.GetObj(EnumObj.CTTRoleData)
	if 1 not in CTTRoleData:
		CTTRoleData[1] = {}
	if 2 not in CTTRoleData:
		CTTRoleData[2] = 0
	
def RoleDayClear(role, param):
	if role.GetI16(EnumInt16.CTTDayPoint):
		role.SetI16(EnumInt16.CTTDayPoint, 0)
		
if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.IsDevelop or Environment.EnvIsQQ() or Environment.EnvIsFT()):
		
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		
		if not Environment.IsCross:
			Cron.CronDriveByMinute((2038, 1, 1), RadioStartMsg, H = "H == 10", M = "M == 00")
			Cron.CronDriveByMinute((2038, 1, 1), RadioEndMsg, H = "H == 23", M = "M == 00")
		
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CTT_TPCrossScene", "客户端请求进入神界"), RequestTP)
		
		if Environment.IsCross and cProcess.ProcessID == Define.GetCrossID_2():
			#各种世界公告
			Cron.CronDriveByMinute((2038, 1, 1), RadioCrossEndMsg, H = "H == 23", M = "M == 00")
			Cron.CronDriveByMinute((2038, 1, 1), RadioCrossEndMsg2, H = "H == 23", M = "M == 29")
			Cron.CronDriveByMinute((2038, 1, 1), RadioCrossEndMsg3, H = "H == 23", M = "M == 49")
			Cron.CronDriveByMinute((2038, 1, 1), RadioCrossEndMsg4, H = "H == 23", M = "M == 58")
			#兑换商店刷新时间
			Cron.CronDriveByMinute((2038, 1, 1), OperationTick, H = "H == 12", M = "M == 0")
			
			Event.RegEvent(Event.Eve_BeforeExit, OnRoleExit)
			Event.RegEvent(Event.Eve_ClientLost, ClientLost)
			
			Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
			
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CTT_OnOpenPanel", "客户端请求打开虚空幻境大厅面板"), OpenPanel)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CTT_RequestCTTStart", "客户端请求开始虚空幻境"), RequestCTTStart)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CTT_RequestCTT_WorldCall", "客户端请求虚空幻境世界邀请"), CTTWorldCall)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CTT_RequestCTT_Invite", "客户端请求虚空幻境邀请好友"), RequestInvite)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CTT_RequestCTT_FastJoin", "客户端请求虚空幻境快速组队"), FastJoinTeam)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CTT_RequestCTT_AutoJoin", "客户端请求虚空幻境自动组队"), SetAutoJoinTT)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CTT_RequestCTT_ExitScene", "客户端请求退出神界"), RequestExitScene)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CTT_RequestCTT_ExchangePanel", "客户端请求打开虚空幻境兑换界面"), RequestExchangePanel)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CTT_RequestCTT_Exchange", "客户端请求虚空幻境兑换"), RequestExchange)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CTT_RequestCTT_Fresh", "客户端请求虚空幻境兑换商店刷新"), RequestFresh)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CTT_RequestCTT_NoReward", "客户端请求虚空幻境无奖励模式"), RequestNoReward)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CTT_RequestCTT_HeroStation", "修改虚空幻境战斗时上阵的英雄"), RequestChangeFightHero)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CTT_RequestCTT_ExitMirror", "客户端请求退出虚空幻境"), RequestExitMirror)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CTT_RequestCTT_ApplyTeam", "客户端申请入队"), RequestApplyTeam)
			
			