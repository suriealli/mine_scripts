#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.JT.JTZBGroup")
#===============================================================================
# 争霸赛小组赛
#===============================================================================
import random
import cComplexServer
import cSceneMgr
import cNetMessage
import Environment
import cRoleMgr
import cProcess
import cDateTime
from World import Define
from Game.Persistence import Contain
from ComplexServer.Time import Cron
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Fight import FightEx
from Common.Other import GlobalPrompt
from Game.Role import Status,Call, Event
from Game.Role.Data import EnumTempObj, EnumInt1, EnumTempInt64,EnumInt64
from Game.JT import JTDefine

if "_HasLoad" not in dir():
	
	IsGroupFightStart = False	#战斗开启标志
	GroupRound = 0	#战斗轮次
	GroupTeamDict = {} #临时战队对象字典，战区->obj
	GroupFightObjs = set()	#战斗对象缓存，用于结束超时的战斗
	GroupRankDict = {}	#排名
	GroupTeamIdDict = {}	#teamId->战区
	MatchTeamDict = {}	#{groupId->{teamId:obj}}	#缓存3人都参加活动的战队，用于匹配
	Fight_Result = {}	#保存所有的战斗结果
	#消息
	NJT_S_GroupPanalData = AutoMessage.AllotMessage("NJT_S_GroupPanalData", "同步新版跨服争霸小组战队数据")
	NJT_S_GroupFightResult = AutoMessage.AllotMessage("NJT_S_GroupFightResult", "同步新版跨服争霸小组比赛轮次信息")
	NJT_S_PointRank = AutoMessage.AllotMessage("NJT_S_PointRank", "同步新版跨服争霸积分榜")
	NJT_S_CrossChangePos = AutoMessage.AllotMessage("NJT_S_CrossChangePos", "同步新版跨服争霸战队出战位置修改")
	NJT_S_CrossChangeLeader = AutoMessage.AllotMessage("NJT_S_CrossChangeLeader", "同步新版跨服争霸更新队长ID")
	NJT_S_CrossRequestLeader = AutoMessage.AllotMessage("NJT_S_CrossRequestLeader", "有人请求做队长")
	#日志
	Tra_InitNZBGroupData = AutoLog.AutoTransaction("Tra_InitNZBGroupData", "跨服争霸小组初始化数据")
	
class GroupTeam(object):
	def __init__(self, teamId, groupIndex, teamData):
		#服ID，服名，战队ID，战队名，战队积分，战队段位，战队数据，战队成员IDs，总战力， 排名
		self.teamId = teamId
		self.teamName = teamData[3]
		self.teamPoint = teamData[4]
		self.teamGrade = teamData[5]
		self.processName = teamData[1]
		self.processID = teamData[0]
		self.totalZdl = teamData[8]
		self.memberIds = teamData[7]
		self.groupIndex = groupIndex
		self.teamData = teamData[6]
		
		self.roles = []
		self.memberVeiwData = []	#存外观数据
		#已经战斗过的小组ID
		self.hasFightTeams = set()
		self.groupRound = 0
		self.winCnt = 0
		self.loseCnt = 0
		self.point = 0
		self.rank = 0
		
		self.fightResult_data = {}
		

	def JoinRole(self, role):
		global MatchTeamDict
		self.roles.append(role)
		if len(self.roles) == 1:
			self.matchTeamLeaderId = role.GetRoleID()
		if self.groupIndex not in MatchTeamDict:
			MatchTeamDict[self.groupIndex] = {}
		groupDict = MatchTeamDict[self.groupIndex]
		if len(self.roles) == 3:#达到匹配要求，加入字典
			groupDict[self.teamId] = self
		role.SetTempObj(EnumTempObj.CrossJTGroupTeam, self)
		#随机组队战的上阵英雄
		nowHeroID = role.GetI64(EnumInt64.JTHeroID)
		if not nowHeroID:
			self.RandomJTHero(role)
			return
		#同步战队面板数据，对战数据
		self.BroadPanal()
		role.SendObj(NJT_S_GroupFightResult, self.fightResult_data)
		
	def RandomJTHero(self, role):
		#随机一个上阵英雄
		sm = role.GetTempObj(EnumTempObj.enStationMgr)
		if len(sm.station_to_id) < 2:
			return
		for heroId in sm.station_to_id.itervalues():
			if heroId == role.GetRoleID():
				continue
			role.SetI64(EnumInt64.JTHeroID, heroId)
			return
		
	def BroadPanal(self):
		#同步面板信息,战队名字，战队积分，段位，胜利次数，失败次数,成员面板外观数据(顺序列表)
		cNetMessage.PackPyMsg(NJT_S_GroupPanalData, (self.teamName, \
									self.teamPoint, \
									self.teamGrade, \
									self.winCnt, \
									self.loseCnt,\
									self.GetMemberSyncData(),\
									self.matchTeamLeaderId,\
									self.teamId))
		for role in self.roles:
			role.BroadMsg_NoExcept()
			
	def GetMemberSyncData(self):
		#成员面板外观数据
		self.memberVeiwData = []
		for role in self.roles:
			self.memberVeiwData.append((role.GetRoleID(), \
										role.GetRoleName(),\
										role.GetSex(), \
										role.GetGrade(), \
										role.GetCareer(), \
										role.GetWingID(),\
										role.GetLevel(), \
										role.GetZDL(), \
										role.GetTI64(EnumTempInt64.FashionClothes),\
										role.GetTI64(EnumTempInt64.FashionHat),\
										role.GetTI64(EnumTempInt64.FashionWeapons),\
										role.GetI1(EnumInt1.FashionViewState)))
		return self.memberVeiwData
	
	def LeaveRole(self, role):
		global MatchTeamDict
		if role in self.roles: 
			self.roles.remove(role)
		#假如是队长
		if role.GetRoleID() == self.matchTeamLeaderId and len(self.roles) > 0:
			self.matchTeamLeaderId = self.roles[0].GetRoleID()
		#队伍无人了，设置队长为0
		if len(self.roles) <= 0:
			self.matchTeamLeaderId = 0
		#假如在匹配字典中
		if self.groupIndex not in MatchTeamDict:
			MatchTeamDict[self.groupIndex] = {}
		groupDict = MatchTeamDict[self.groupIndex]
		if self.teamId in groupDict:#不达匹配要求，删除
			del groupDict[self.teamId]
			
		role.SetTempObj(EnumTempObj.CrossJTGroupTeam, None)
		self.BroadPanal()
	
	def IsMatchTeamLeader(self, role):
		return role.GetRoleID() == self.matchTeamLeaderId
	
	def ChangeLeader(self, roleId):
		if len(self.roles) < 1:
			return
		for role in self.roles:
			if role.GetRoleID() == roleId:
				self.matchTeamLeaderId = roleId
				cNetMessage.PackPyMsg(NJT_S_CrossChangeLeader, roleId)
				for role in self.roles:
					role.BroadMsg_NoExcept()
				return
			
	def ChangeFightPos(self, pos1, pos2):
		if not self.roles or pos1 > len(self.roles) or pos2 > len(self.roles):
			return
		self.roles[pos1], self.roles[pos2] = self.roles[pos2], self.roles[pos1]
		cNetMessage.PackPyMsg(NJT_S_CrossChangePos, (pos1 + 1, pos2 + 1))
		for role in self.roles:
			role.BroadMsg_NoExcept()
			
	def ByeMsg(self, role = None):
		if role:
			role.Msg(2, 0, GlobalPrompt.JT_ZB_Tips_1)
		else:
			for role in self.roles:
				role.Msg(2, 0, GlobalPrompt.JT_ZB_Tips_1)
				
	def ReadyFight(self, otherTeam):
		self.hasFightTeams.add(otherTeam.teamId)
	
	def ByeRound(self, processName = "", teamName = ""):
		#轮空了，直接胜利	
		SetFightResult(self.teamName, "", -2, self.groupIndex)
		
		self.winCnt += 1
		self.point += 100
		self.BroadPanal()
		for role in self.roles:
			role.Msg(2, 0, GlobalPrompt.JT_ZB_Tips_1)
	
	def FightResult(self, processName, teamName, result):
		#战斗结果
		if result == 1 : 
			self.winCnt += 1
			self.point += 100
		elif result == -1 : self.loseCnt += 1
		elif result == 2:
			self.point += 50
		self.BroadPanal()
	
	def GetRankData(self):
		return [self.teamId, self.teamName, self.processName, self.processID, self.point, self.teamPoint, self.teamGrade, self.totalZdl, self.winCnt, self.loseCnt, self.memberIds, self.rank, self.teamData]
	
	def UpdataRank(self, rank):
		self.rank = rank
		
	def SynRankToTeam(self, rank):
		for role in self.roles:
			role.SendObj(NJT_S_PointRank, rank)
			global Fight_Result
			self.fightResult_data = Fight_Result.get(self.groupIndex)
			role.SendObj(NJT_S_GroupFightResult, self.fightResult_data)
########################################################################################
#玩家进入后处理
########################################################################################
def AfterJoinGroup(role, param):
	#逻辑进程进入跨服时候调用的函数
	global GroupTeamDict
	global IsGroupFightStart
	if not IsGroupFightStart:
		#传送回去
		role.GotoLocalServer(None, None)
		return
	teamId, groupIndex = param
	groupTeams = GroupTeamDict.get(groupIndex)
	if not groupTeams:
		print "GE_EXC AfterJoinGroup not this groupteams (%s)" % groupIndex
		return
	gteam = groupTeams.get(teamId)
	if not gteam:
		print "GE_EXC AfterJoinGroup not gteam (%s) (%s)" % (groupIndex, teamId)
		return
	gteam.JoinRole(role)
########################################################################################
#筛选数据
########################################################################################
def InitZBSelectData(JTCrossRankLevelDict):
	#筛选有资格争霸的战队，根据等级区间将玩家加入对应的战区
	#60到139加入初级组
	global JT_ZBSelectData
	
	nowDays = cDateTime.Days()
	if nowDays <= JT_ZBSelectData.get(3):#已经筛选过了
		return
	
	chujiGroup = []
	if 1 in JTCrossRankLevelDict:
		chujiGroup.extend(JTCrossRankLevelDict[1])
	if 2 in JTCrossRankLevelDict:
		chujiGroup.extend(JTCrossRankLevelDict[2])
	if 3 in JTCrossRankLevelDict:
		chujiGroup.extend(JTCrossRankLevelDict[3])
	if 4 in JTCrossRankLevelDict:
		chujiGroup.extend(JTCrossRankLevelDict[4])
	#根据总排名进行排序，然后取前100
	chujiGroup.sort(key = lambda it:it[10], reverse = False)
	chujiGroup = chujiGroup[:100]
	#140到159加入精锐组
	jingruiGroup = []
	if 5 in JTCrossRankLevelDict:
		jingruiGroup.extend(JTCrossRankLevelDict[5][:100])
	#160以上加入巅峰组
	dianfengGroup = []
	if 6 in JTCrossRankLevelDict:
		dianfengGroup.extend(JTCrossRankLevelDict[6][:100])
	InitData(chujiGroup, jingruiGroup, dianfengGroup, nowDays)
	
def InitData(chujiGroup, jingruiGroup, dianfengGroup, nowDays):
	global JT_ZBSelectData
	global GroupTeamIdDict
	#先清理数据
	JT_ZBSelectData.clear()
	
	JT_ZBSelectData[1] = JTZB = {}
	#初级战区
	chujiList = []
	for data in chujiGroup:
		processId, processName, teamId, teamName,point, teamGrade, teamData, _, _, totalZDL, rank = data
		memberIds = set()
		for td in teamData:
			if len(td) >= 4:
				memberIds.add(td[3])
		#服ID，服名，战队ID，战队名，战队积分，战队段位，战队数据，战队成员IDs，总战力， 排名
		chujiList.append([processId, processName, teamId, teamName,point, teamGrade, teamData, memberIds, totalZDL, rank])
	JTZB[1] = chujiList
	#精锐战区
	jingruiList = []
	for data in jingruiGroup:
		processId, processName, teamId, teamName,point, teamGrade, teamData, _, _, totalZDL, rank = data
		memberIds = set()
		for td in teamData:
			if len(td) >= 4:
				memberIds.add(td[3])
		#16, '\xe3\', 4651016045594480L, '\xe9\x', 700, 0, [('\xe6\x88\x91\xe6\x98\xaf\xe7\xba\xaa\xe5\xa7\x94', 137, 1403, 68719476752L), ('\xe8\x9b\x8b\xe7\xa5\x9e', 168, 11700143, 68719476749L), ('\xe7\xba\xaa\xe5\xa7\x94\xe9\xa2\x86\xe5\xaf\xbc', 137, 1403, 68719476750L)], set([68719476752L, 68719476749L, 68719476750L]), 11702949, 2]]}}
		#服ID，服名，战队ID，战队名，战队积分，战队段位，战队数据，战队成员IDs，总战力， 排名
		jingruiList.append([processId, processName, teamId, teamName, point, teamGrade, teamData, memberIds, totalZDL, rank])
	JTZB[2] = jingruiList
	#巅峰战区
	dianfengList = []
	for data in dianfengGroup:
		processId, processName, teamId, teamName,point, teamGrade, teamData, _, _, totalZDL, rank = data
		memberIds = set()
		for td in teamData:
			if len(td) >= 4:
				memberIds.add(td[3])
		#服ID，服名，战队ID，战队名，战队积分，战队段位，战队数据，战队成员IDs，总战力， 排名
		dianfengList.append([processId, processName, teamId, teamName,point, teamGrade, teamData, memberIds, totalZDL, rank])
	JTZB[3] = dianfengList
	JT_ZBSelectData[3] = nowDays	#设置筛选数据的天数
	JT_ZBSelectData.changeFlag = True
	
	#同步到所有的逻辑进程，让逻辑进程记录并且通知相关的具有资格的战队玩家
	SycGroupRankData(0, True)
	
	with Tra_InitNZBGroupData:
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveNZBGroupInitData, JTZB)
		
def SycGroupRankData(processId = 0, mail = False):
	global JT_ZBSelectData
	Call.SuperServerCall(processId, "Game.JT.JTLogicZB", "ReceiveGroupRank", (JT_ZBSelectData.get(1), mail))

def UpdataGroupRankData(param):
	#逻辑进程请求小组赛数据
	processId = param
	SycGroupRankData(processId)
########################################################################################
#活动开启
########################################################################################
def ReadyGroupFight():
	#周一准备开启100进32强赛，提前10分钟准备数据
	num = JTDefine.GetZBStartFlagNum()
	if num != 1: return
	
	global IsGroupFightStart, GroupTeamDict, GroupFightObjs, JT_ZBSelectData, MatchTeamDict
	IsGroupFightStart = True
	GroupTeamDict = {}
	GroupFightObjs = set()
	MatchTeamDict = {}
	
	zbData = JT_ZBSelectData.get(1)
	if not zbData:
		print "GE_EXC,ReadyGroupFight error not teams"
		return
	for groupIndex, teamList in zbData.iteritems():
		GroupTeamDict[groupIndex] = groupTeams = {}
		for teamData in teamList:
			teamId = teamData[2]
			groupTeams[teamId] = GroupTeam(teamId, groupIndex, teamData)
	#10分钟后正式开启22:00
	cComplexServer.RegTick(60 * 10, StartGroupFight, None)

def StartGroupFight(callArgv = None, regparam = None):
	#开始小组比赛
	global GroupRound
	global IsGroupFightStart
	global JT_FightGroupDict
	if not IsGroupFightStart:
		return
	GroupRound = 0
	#第一轮
	OneRound(True, True)
	#22:45结束
	cComplexServer.RegTick(60 * 45, EndGroupFight, None)
	
def OneRound(callArgv = None, regparam = None):
	#每5.30分钟一轮
	global IsGroupFightStart
	if not IsGroupFightStart:
		return
	global GroupRound
	global GroupFightObjs
	global MatchTeamDict
	
	GroupFightObjs = set()
	GroupRound += 1
	if GroupRound > 8:
		return
	for groupId, teamDict in MatchTeamDict.iteritems():
		teamIds = set(teamDict.keys())
		for teamId, gteam in teamDict.iteritems():
			if gteam.groupRound == GroupRound:
				continue
			gteam.groupRound = GroupRound
			if teamId in teamIds:
				teamIds.remove(teamId)
				
			randomList = teamIds - gteam.hasFightTeams
			if not randomList:
				#没有匹配的战队了，就轮空直接赢
				gteam.ByeRound()
				continue

			teamId_2 = random.sample(randomList,1)[0]
			#从匹配中移除
			teamIds.remove(teamId_2)
			gteam2 = teamDict.get(teamId_2)
			if not gteam2:
				#随机出来的战队不存在，就轮空直接赢
				gteam.ByeRound()
				continue
			if gteam2.groupRound == GroupRound:
				print "GE_EXC, repeat match team2 in GroupRound repeat",groupId,teamId,teamId_2,GroupRound
				continue
			#匹配成功，尝试进入战斗
			gteam2.groupRound = GroupRound
			gteam2.ReadyFight(gteam)
			gteam.ReadyFight(gteam2)
			TryFight(True, (gteam, gteam2, 1, groupId))

	#5分的时候检查一下是否已经全部结束战斗
	cComplexServer.RegTick(60 * 5, CheckFightEnd, None)
	#判断是否结束
	if GroupRound <= 8:
		#5分钟下一轮
		cComplexServer.RegTick(60 * 5 + 30, OneRound, None)
	
	if IsGroupFightStart:
		cComplexServer.RegTick(60 * 2, SynRankToTeam, None)
		
def CheckFightEnd(callArgv = None, regparam = None):
	#在下一轮开启前，检查一下战斗是否已经结束，没有结束则强制结束,按平局处理
	global GroupFightObjs, IsGroupFightStart
	
	if GroupFightObjs and IsGroupFightStart:
		for fightObj in GroupFightObjs:
			if fightObj.result is not None:
				continue
			print "GE_EXC CheckFightEnd has not end fight"
			fightObj.end(2)
	GroupFightObjs = set()
	#更新排行榜
	UpdataGroupRank()
	
def TryFight(callArgv = None, regparam = None):
	global IsGroupFightStart
	if not IsGroupFightStart:
		return
	gteam1, gteam2, teamRound, groupId = regparam
	#尝试进入战斗，如果两方都有人，就进入战斗，没有就等待20秒
	if gteam1.roles and gteam2.roles:
		#判断是否可以进入战斗状态
		canFight = True
		for role in gteam1.roles:
			if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
				canFight = False
				break
		for role in gteam2.roles:
			if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
				canFight = False
				break
		if canFight is True:
			TeamFight(gteam1, gteam2, groupId)
			return
		print "GE_EXC, ZBGroup, TryFight but in fightstatus"
	if teamRound < 2 :
		#等待20秒匹配一次
		cComplexServer.RegTick(20, TryFight, (gteam1, gteam2, teamRound + 1,groupId))
		return

	#超时，没人的队伍就输
	if gteam1.roles and not gteam2.roles:
		FightResult(gteam1, 1, gteam2, -1, groupId)
		gteam1.ByeMsg()
	elif gteam2.roles and not gteam1.roles:
		FightResult(gteam1, -1, gteam2, 1, groupId)
		gteam2.ByeMsg()
	elif not gteam1.roles and not gteam2.roles:
		FightResult(gteam1, -1, gteam2, -1, groupId)
	else:
		#都有人,判断那个队伍因为在战斗状态，导致匹配战斗打不起来
		print "GE_EXC, TryFight timeout but in fightstatus"
		isInFightStatue_1 = 1
		for role in gteam1.roles:
			if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
				isInFightStatue_1 = -1
				break
		isInFightStatue_2 = 1
		for role in gteam2.roles:
			if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
				isInFightStatue_2 = -1
				break
		#谁在战斗状态就谁输
		FightResult(gteam1, isInFightStatue_1, gteam2, isInFightStatue_2, groupId)
		
def TeamFight(gteam1, gteam2, groupId):
	#进入战斗
	global GroupFightObjs
	fobj = FightEx.PVP_JTGroup(gteam1.roles, gteam2.roles, JTDefine.JT_fightType, AfterTeamFight, (gteam1, gteam2, groupId))
	GroupFightObjs.add(fobj)
	
def AfterTeamFight(fightObj):
	#战斗回调,处理结果
	winorlose = fightObj.result
	(gteam1, gteam2, groupId) = fightObj.after_fight_param
	#胜负
	if winorlose == 1:
		FightResult(gteam1, 1, gteam2, -1, groupId)
	elif winorlose == -1:
		FightResult(gteam1, -1, gteam2, 1, groupId)
	else:
		#平局
		FightResult(gteam1, -1, gteam2, -1, groupId)

	
def FightResult(gteam1, winorlose1, gteam2, winorlose2, groupId):
	#战斗结果处理
	if winorlose1 == -1 and winorlose2 == -1:
		#按平均处理
		winorlose1 = 2
		winorlose2 = 2
	
	SetFightResult(gteam1.teamName, gteam2.teamName, winorlose1, groupId)
	
	gteam1.FightResult(gteam2.processName, gteam2.teamName, winorlose1)
	gteam2.FightResult(gteam1.processName, gteam1.teamName, winorlose2)
	
def SetFightResult(teamName1, teamName2, result, groupId):
	global Fight_Result, GroupRound
	if groupId not in Fight_Result:
		Fight_Result[groupId] = {}
	groupData = Fight_Result[groupId]
	if GroupRound not in groupData:
		groupData[GroupRound] = []
	FightList = groupData[GroupRound]
	FightList.append((teamName1, teamName2, result))
	
def UpdataGroupRank():
	#更新小组排名
	global GroupRankDict
	global GroupTeamDict
	for gIndex, gteams in GroupTeamDict.iteritems():
		rank = []
		for gteam in gteams.itervalues():
			rank.append(gteam.GetRankData())
		#teamId,teamName,processName,processID,point,teamPoint,teamGrade,totalZdl,winCnt,loseCnt,memberIds,rank,teamData
		#1、积分多的排前 ；2.积分相同的战队积分高排前，3.2者都相同的话战队总战力高的在前
		rank.sort(key = lambda it:(it[4], it[5], it[7]), reverse = True)
		#更新缓存对象中的排名
		for rankIndex, teamData in enumerate(rank):
			teamId = teamData[0]
			gteam = gteams.get(teamId)
			if not gteam:
				continue
			gteam.UpdataRank(rankIndex + 1)
		#重新更新排行位置
		for realRank, rankdata in enumerate(rank):
			rankdata[11] = realRank + 1
		
		#缓存
		GroupRankDict[gIndex] = rank
		#同步各个战队
		for gteam in gteams.itervalues():
			gteam.SynRankToTeam(rank)
			
	#更新持久化数据
	global JT_ZBSelectData
	JT_ZBSelectData[2] = GroupRankDict
	JT_ZBSelectData.changeFlag = True
	
def SynRankToTeam(callArgv = None, regparam = None):
	global IsGroupFightStart
	if not IsGroupFightStart:
		return
	
	global GroupRankDict
	for gIndex, gteams in GroupTeamDict.iteritems():
		for gteam in gteams.itervalues():
			gteam.SynRankToTeam(GroupRankDict.get(gIndex, []))
			
	cComplexServer.RegTick(60 * 2, SynRankToTeam, None)
	
def EndGroupFight(callArgv = None, regparam = None):
	global IsGroupFightStart
	if not IsGroupFightStart:
		return
	IsGroupFightStart = False
	#结束,全部回到本服
	scene = cSceneMgr.SearchPublicScene(JTDefine.JTZBSceneID)
	if scene:
		for role in scene.GetAllRole():
			role.GotoLocalServer(None, None)
	UpdataGroupRank()
	#清理数据
	ClearTempData()
	#记录状态
	global JT_ZBSelectData
	from Game.JT import JTZBFinal
	#生成总决赛数据
	JTZBFinal.InitFinal(JT_ZBSelectData.get(2))
	
def ClearTempData():
	global GroupTeamDict,GroupRound,GroupFightObjs, GroupRankDict,Fight_Result
	GroupTeamDict = {}
	GroupRound = 0
	GroupFightObjs = set()
	GroupRankDict = {}
	Fight_Result = {}

		
def AfterLoadZBSelectData():
	global JT_ZBSelectData
	global GroupTeamIdDict
	if 1 not in JT_ZBSelectData:#{初级战区1：rank, 精锐战区：rank, 顶峰战区： rank}
		JT_ZBSelectData[1] = {}
	if 2 not in JT_ZBSelectData:
		JT_ZBSelectData[2] = {}#排序后的数据
	if 3 not in JT_ZBSelectData:#记录开启时的天数
		JT_ZBSelectData[3] = 0
	zbData = JT_ZBSelectData.get(1)
	num = JTDefine.GetZBStartFlagNum()
	if zbData and num in [0,1,2,3,4]:
		#同步到所有的逻辑进程，让逻辑进程记录并且通知相关的具有资格的战队玩家
		SycGroupRankData()
		if num == 1:#小组赛那天假如重启的话，重新生成一份战队缓存数据
			global GroupTeamDict
			for groupIndex, teamList in zbData.iteritems():
				GroupTeamDict[groupIndex] = groupTeams = {}
				for teamData in teamList:
					teamId = teamData[2]
					groupTeams[teamId] = GroupTeam(teamId, groupIndex, teamData)
	
def RequestGroupLeave(role, msg):
	'''
	请求离开跨服争霸小组赛(总决赛也是用这个)
	@param role:
	@param msg:
	'''
	if role.GetSceneID() != JTDefine.JTZBSceneID:
		return
	role.GotoLocalServer(None, None)
	
def RequestChangeFightHero(role, msg):
	'''
	改变英雄上阵
	@param role:
	@param msg:
	'''
	heroId = msg
	hero = role.GetHero(heroId)
	if not hero or not hero.GetStationID():
		return
	if role.GetI64(EnumInt64.JTHeroID) == heroId:
		return
	if role.GetTempObj(EnumTempObj.CrossJTGroupTeam) or role.GetTempObj(EnumTempObj.CrossJTFinalTeam):
		role.SetI64(EnumInt64.JTHeroID, heroId)

def RequestChangeJTeamPos(role, msg):
	'''
	改变队员出战位置
	@param role:
	@param msg:
	'''
	pos1, pos2 = msg
	#位置是否合法
	if pos1 not in (1,2,3) or pos2 not in (1,2,3):
		return
	if pos1 == pos2:
		return
	cjteam = role.GetTempObj(EnumTempObj.CrossJTGroupTeam)
	if not cjteam:
		cjteam = role.GetTempObj(EnumTempObj.CrossJTFinalTeam)
	if not cjteam:
		return
	if not cjteam.IsMatchTeamLeader(role):
		return
	cjteam.ChangeFightPos(pos1-1, pos2-1)
	
def RequestChangeJTeamLeader(role, param):
	'''
	转让战队匹配队伍的队长
	@param role:
	@param param:
	'''
	leaderId = param
	cjteam = role.GetTempObj(EnumTempObj.CrossJTGroupTeam)
	if not cjteam:
		cjteam = role.GetTempObj(EnumTempObj.CrossJTFinalTeam)
	if not cjteam:
		return
	if not cjteam.IsMatchTeamLeader(role):
		return
	if leaderId == role.GetRoleID():
		return
	cjteam.ChangeLeader(leaderId)
	
def RequestToBeJTeamLeader(role, msg):
	'''
	申请成为战队匹配的队长
	@param role:
	@param msg:
	'''
	cjteam = role.GetTempObj(EnumTempObj.CrossJTGroupTeam)
	if not cjteam:
		cjteam = role.GetTempObj(EnumTempObj.CrossJTFinalTeam)
	if not cjteam:
		return
	if cjteam.IsMatchTeamLeader(role):
		return
	
	leader = cRoleMgr.FindRoleByRoleID(cjteam.matchTeamLeaderId)
	if not leader or leader.IsLost():
		cjteam.ChangeLeader(role.GetRoleID())
		return
	
	leader.SendObjAndBack(NJT_S_CrossRequestLeader, role.GetRoleName(), 60, LeaderBack, role.GetRoleID())
	
def LeaderBack(role, callArgv, regparam):
	#队长回调，或者超时回调
	if callArgv == 1:
		cjteam = role.GetTempObj(EnumTempObj.CrossJTGroupTeam)
		if not cjteam:
			cjteam = role.GetTempObj(EnumTempObj.CrossJTFinalTeam)
		if not cjteam:
			return
		if not cjteam.IsMatchTeamLeader(role):
			return
		newLeader = cRoleMgr.FindRoleByRoleID(regparam)
		if not newLeader:
			return
		leaderjteam = newLeader.GetTempObj(EnumTempObj.CrossJTGroupTeam)
		if not leaderjteam:
			leaderjteam = newLeader.GetTempObj(EnumTempObj.CrossJTFinalTeam)
		if not leaderjteam:
			return
		if leaderjteam.teamId != cjteam.teamId:
			return
		leaderjteam.ChangeLeader(regparam)
	elif callArgv is None:
		newLeader = cRoleMgr.FindRoleByRoleID(regparam)
		if not newLeader:
			return
		leaderjteam = newLeader.GetTempObj(EnumTempObj.CrossJTGroupTeam)
		if not leaderjteam:
			leaderjteam = role.GetTempObj(EnumTempObj.CrossJTFinalTeam)
		if not leaderjteam:
			return
		if leaderjteam.IsMatchTeamLeader(newLeader):
			return
		leaderjteam.ChangeLeader(regparam)
		
def OnRoleExit(role, param):
	fteam = role.GetTempObj(EnumTempObj.CrossJTGroupTeam)
	if not fteam: return
	fteam.LeaveRole(role)
	
def ClientLost(role, param):
	fteam = role.GetTempObj(EnumTempObj.CrossJTGroupTeam)
	if not fteam: return
	fteam.LeaveRole(role)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.EnvIsQQ() or Environment.IsDevelop or Environment.EnvIsFT()) and Environment.IsCross:
		if cProcess.ProcessID == Define.GetDefaultCrossID():
			JT_ZBSelectData = Contain.Dict("JT_ZBSelectData", (2038, 1, 1), AfterLoadZBSelectData)
			#开始前5分钟的定时器
			Cron.CronDriveByMinute((2038, 1, 1), ReadyGroupFight, H="H == 21", M="M == 50")
			
			Event.RegEvent(Event.Eve_BeforeExit, OnRoleExit)
			Event.RegEvent(Event.Eve_ClientLost, ClientLost)
			
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_NZBRequestGroupLeave", "请求离开新版跨服争霸小组赛(总决赛也是同一个)"), RequestGroupLeave)
			
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_NZBRequestChangeFightHero", "改变英雄上阵"), RequestChangeFightHero)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_NZBRequestChangeJTeamPos", "修改战队队员出战的位置"), RequestChangeJTeamPos)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_NZBRequestChangeJTeamLeader", "转让战队匹配队伍的队长"), RequestChangeJTeamLeader)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_NZBRequestToBeJTeamLeader", "申请成为战队匹配的队长"), RequestToBeJTeamLeader)
		
		
