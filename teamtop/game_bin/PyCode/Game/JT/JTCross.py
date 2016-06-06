#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.JT.JTCross")
#===============================================================================
# 组队竞技场活动模块(跨服进程)
#===============================================================================
import cRoleMgr
import cNetMessage
import cSceneMgr
import cProcess
import cComplexServer
import Environment
import cDateTime
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from World import Define
from ComplexServer.Log import AutoLog
from Game.Persistence import Contain
from Game.Role import Status, Event, Call
from Game.Role.Data import EnumInt1, EnumTempObj, EnumDayInt8, EnumCD, EnumTempInt64,\
	EnumInt64
from Game.JT import JTDefine, JTConfig, JTZBGroup
from Game.Fight import FightEx



MatchMaxTimes = 12		#15秒匹配一次，匹配180秒，总共15次
ProtectScore = 1750		#保护积分，最低积分

if "_HasLoad" not in dir():
	IsStart = False
	MatchRound = 0
	MatchTeams = set()

	#跨服服务器管理的战队临时对象
	Cross_JT_Dict = {}
	#等级段对应的排行榜
	JTCrossRankLevelDict = {}
	#等级段对应的排行榜(用于同步给客户端) 截断了数据，每个等级段保留JTDefine.MaxLevelRank个数据
	JTCrossRankLevel_Sync_Dict = {}

	#匹配状态  1 正在匹配  0 取消匹配  2 匹配超时 3 匹配成功
	JT_S_MatchStatus = AutoMessage.AllotMessage("JT_S_MatchStatus", "同步组队竞技场匹配状态")
	JT_S_FightInfo = AutoMessage.AllotMessage("JT_S_FightInfo", "同步组队竞技场战斗结算面板")
	JT_S_JTInfo = AutoMessage.AllotMessage("JT_S_JTInfo", "同步组队竞技场竞技信息")
	JT_S_UpdateJTScore = AutoMessage.AllotMessage("JT_S_UpdateJTScore", "同步更新战队积分和胜负值")
	JT_S_CrossChangePos = AutoMessage.AllotMessage("JT_S_CrossChangePos", "同步战队出战位置修改")
	JT_S_CrossChangeLeader = AutoMessage.AllotMessage("JT_S_CrossChangeLeader", "同步更新匹配队长ID")
	JT_S_CrossRequestLeader = AutoMessage.AllotMessage("JT_S_CrossRequestLeader", "有人请求做匹配队长")
	
	#日志
	Tra_JS_FightReward = AutoLog.AutoTransaction("Tra_JS_FightReward", "组队竞技场战斗奖励")
	Tra_JS_CrossMonthClear = AutoLog.AutoTransaction("Tra_JS_CrossMonthClear", "跨服竞技场月结清理")


#跨服战队对象(用与积分计算)
class CrossJTeam(object):
	def __init__(self, role, teamData):
		#初始化数据
		self.processId, \
		self.processName, \
		self.teamId, \
		self.teamName, \
		self.teamFlag, \
		self.teamScore, \
		self.teamGrade,\
		self.leaderId, \
		self.leaderName,\
		self.winCount,\
		self.loseCount,\
		self.nowrank, \
		self.memberIds,\
		self.teamMaxScore,\
		self.teamMaxGrade,\
		self.memberRankData = teamData
		
		self.members = []
		
		self.matchRound = 0
		self.matchTimes = 0
		self.maxLevel = 0
		self.totalZDL = 0
		self.fightTimes = 0
		self.hasChange = False
		
		self.matchTeamLeaderId = 0
		self.memberVeiwData = []
		self.memberFightEndPanelData = {}
		
	def JoinCrossJTeam(self, role):
		role.SetTempObj(EnumTempObj.CrossJTeamObj, self)
		self.members.append(role)
		#清空缓存数据
		self.memberVeiwData = []
		self.memberFightEndPanelData = {}
		if len(self.members) == 1:
			self.matchTeamLeaderId = role.GetRoleID()
		elif len(self.members) == 3:
			#人齐了，算一下总战力和战队等级
			self.totalZDL = 0
			for role in self.members:
				self.totalZDL += role.GetZDL()
				self.maxLevel = max(self.maxLevel, role.GetLevel())
		#同步面板数据
		self.BroadPanel()
		#随机组队战的上阵英雄
		nowHeroID = role.GetI64(EnumInt64.JTHeroID)
		if not nowHeroID:
			self.RandomJTHero(role)
			return
		hero = role.GetHero(nowHeroID)
		if not hero or not hero.GetStationID():
			role.SetI64(EnumInt64.JTHeroID, 0)
			self.RandomJTHero(role)
			return
	
	def LeaveCrossJTeam(self, role):
		self.members.remove(role)
		role.SetTempObj(EnumTempObj.CrossJTeamObj, None)
		if role.GetRoleID() == self.matchTeamLeaderId and len(self.members) > 0:
			self.matchTeamLeaderId = self.members[0].GetRoleID()
		#清空缓存数据
		self.memberVeiwData = []
		self.memberFightEndPanelData = {}
		if len(self.members) <= 0:
			self.matchTeamLeaderId = 0
		else:
			self.BroadPanel()
	
	def GetJTeamLevel(self):
		return self.maxLevel
	
	def GetWinRate(self):
		return int (self.winCount * 10000.0 / (self.winCount + self.loseCount))
	
	def GetTotalZDL(self):
		return self.totalZDL
	
	def IsMatchTeamLeader(self, role):
		return  role.GetRoleID() == self.matchTeamLeaderId
	
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
	
	def ChangePos(self, pos1, pos2):
		if not self.members or pos1 > len(self.members) or pos2 > len(self.members):
			return
		self.members[pos1], self.members[pos2] = self.members[pos2], self.members[pos1]
		cNetMessage.PackPyMsg(JT_S_CrossChangePos, (pos1 + 1, pos2 + 1))
		for role in self.members:
			role.BroadMsg_NoExcept()
	
	def ChangeLeader(self, roleId):
		if len(self.members) < 1:
			return
		for role in self.members:
			if role.GetRoleID() == roleId:
				self.matchTeamLeaderId = roleId
				cNetMessage.PackPyMsg(JT_S_CrossChangeLeader, roleId)
				for role in self.members:
					role.BroadMsg_NoExcept()
				return

	def GetEndFightData(self, score):
		#获取战斗结算面板数据
		return (self.processName, \
				self.teamName, \
				self.teamFlag, \
				self.teamGrade, \
				self.teamScore, \
				score, self.GetMemberFightPanelData())
	
	def GetMemberFightPanelData(self):
		if self.memberFightEndPanelData:
			return self.memberFightEndPanelData
		#更新成员信息,用于战斗结算面板
		for role in self.members:
			self.memberFightEndPanelData[role.GetRoleID()] = [role.GetRoleName(), \
														role.GetGrade(), \
														role.GetCareer(), \
														role.GetSex(), \
														role.GetLevel(), \
														role.GetZDL() , \
														]
		return self.memberFightEndPanelData
		
	def GetMemberSyncData(self):
		#成员面板外观数据
		if self.memberVeiwData:
			return self.memberVeiwData
		self.memberVeiwData = []
		for role in self.members:
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
	
	
	def BroadPanel(self):
		#同步面板信息,战队名字，战队积分，段位， 现在排名，胜利次数，失败次数,匹配队长ID,成员面板外观数据(顺序列表)
		cNetMessage.PackPyMsg(JT_S_JTInfo, (self.teamName, \
									self.teamScore, \
									self.teamGrade, \
									self.nowrank, \
									self.winCount, \
									self.loseCount,\
									self.matchTeamLeaderId,\
									self.GetMemberSyncData()))
		for role in self.members:
			role.BroadMsg_NoExcept()
	
	def BroadAfterFight(self):
		#战斗后数据修改广播
		cNetMessage.PackPyMsg(JT_S_UpdateJTScore, (self.teamScore, self.winCount, self.loseCount))
		for role in self.members:
			role.BroadMsg_NoExcept()
		
	def FightResult(self, teamscore, winorlose):
		#战斗结束后的分数记录 win：winorlose = 1     lose:winorlose = -1 
		if winorlose == 1:
			self.winCount += 1
		else:
			self.loseCount += 1
		#更新战队积分
		self.teamScore += teamscore
		self.teamScore = max(JTDefine.DefaultJTScore, self.teamScore)
		#写入到持久化数据中
		self.UpdateSave()
		self.fightTimes += 1
		self.hasChange = True
	
	def UpdateSave(self):
		#写入到持久化数据中
		global JT_CrossTeamDict
		#服务器ID，服务器名字，队伍ID，队伍名字，积分，段位，成员数据，战队等级，胜率(万份比)，总战力，总排名
		JT_CrossTeamDict[self.teamId] = [self.processId, \
										self.processName, \
										self.teamId, \
										self.teamName,\
										self.teamScore,\
										self.teamGrade, \
										self.memberRankData,\
										self.GetJTeamLevel(),\
										self.GetWinRate(),\
										self.GetTotalZDL(),
										self.nowrank]
	
	def GetChangeInfo(self):
		#获取同步回去本服的数据 
		return (self.teamScore, \
				self.winCount, \
				self.loseCount, \
				self.fightTimes)

#===============================================================================
#进入到跨服调用
#===============================================================================
def AfterJoinCrossJTScene(role, param):
	global IsStart
	if IsStart is False:
		#活动已经结束了,或者没开启
		role.GotoLocalServer(None, None)
		return
	teamId = role.GetJTeamID()
	if not teamId:
		role.GotoLocalServer(None, None)
		return
	#进程ID，战队数据
	_, teamData = param
	cjtObj = Cross_JT_Dict.get(teamId)
	if not cjtObj:
		#初始化跨服这里的战队缓存对象, 不能重复初始化，第一个过来的成员负责初始化
		Cross_JT_Dict[teamId] = cjtObj = CrossJTeam(role, teamData)
	cjtObj.JoinCrossJTeam(role)

#===============================================================================
#具体逻辑
#===============================================================================
#匹配次数和分差
matchtRoundDict = {1:200, 2:200, 3:400, 4:600, 5:800, 6:1000,\
					7:1300, 8:1500, 9:1800, 10:2000}
def GetMatchRange(matchSeconds):
	return matchtRoundDict.get(matchSeconds, 2000)

def CallPerSecond():
	global IsStart
	if IsStart is False:
		return
	
	global MatchRound
	MatchRound +=1
	if MatchRound % 14 != 0:
		return
	
	global MatchTeams
#	if len(MatchTeams) < 2:
#		return
	with Tra_JS_FightReward:
		#本轮没有匹配到的队伍
		DonotMatchTeams = set()
		DA = DonotMatchTeams.add
		SO = Status.Outstatus
		EST = EnumInt1.ST_JTMatch
		for team in MatchTeams:
			if team.matchRound == MatchRound : continue
			#每次只会主动匹配一次
			team.matchRound = MatchRound
			team.matchTimes += 1
			
			teamHasMatch = False
			matchteam = None
			
			teamscore = team.teamScore
			matchRange = GetMatchRange(team.matchTimes)
			teamid = team.teamId
			for matchteam in MatchTeams:
				if matchteam.matchRound == MatchRound : continue
				if teamid == matchteam.teamId : continue
				if abs(teamscore - matchteam.teamScore) > matchRange : continue
				teamHasMatch = True
				#被匹配到的这轮就不用再匹配了
				matchteam.matchRound = MatchRound
				GoFight(team, matchteam)
				break
			if teamHasMatch is True:
				continue
			if team.matchTimes < MatchMaxTimes:
				#没有匹配到的进入下一轮匹配
				DA(team)
				continue
			#匹配超时
			for member in team.members:
				SO(member, EST)
				member.SendObj(JT_S_MatchStatus, 2)
		#更新下一轮匹配列表
		MatchTeams = DonotMatchTeams

def ReadyFight(team1, team2):
	#战斗前状态和奖励处理
	ED8 = EnumDayInt8.JTDayFightTimes
	EST = EnumInt1.ST_JTMatch
	SO = Status.Outstatus
	JDT = JTDefine.DayFightRewardTimes
	JTFI = JTDefine.FightRewardItem
	EJID = EnumInt64.JTFightTeamID
	for role in team1.members:
		SO(role, EST)
		role.SendObj(JT_S_MatchStatus, 3)
		if role.GetDI8(ED8) >= 125:
			continue
		role.IncDI8(ED8, 1)
		if role.GetDI8(ED8) <= JDT:
			role.AddItem(*JTFI)
		role.SetI64(EJID, team1.teamId)
	for role in team2.members:
		SO(role, EST)
		role.SendObj(JT_S_MatchStatus, 3)
		if role.GetDI8(ED8) >= 125:
			continue
		role.IncDI8(ED8, 1)
		if role.GetDI8(ED8) <= JDT:
			role.AddItem(*JTFI)
		role.SetI64(EJID, team2.teamId)
		
def GoFight(mteam1, mteam2):
	#进入战斗
	ReadyFight(mteam1, mteam2)
	FightEx.PVP_JT(mteam1.members, mteam2.members, JTDefine.JT_fightType, AfterFight, (mteam1, mteam2))

def AfterFight(fightObj):
	winorlose = fightObj.result
	(mteam1, mteam2) = fightObj.after_fight_param
	leftteamScore = CountScore(mteam1.teamScore, mteam2.teamScore, winorlose)
	rightteamScore = CountScore(mteam2.teamScore, mteam1.teamScore, -winorlose)
	leftdata = mteam1.GetEndFightData(leftteamScore)
	rightdata = mteam2.GetEndFightData(rightteamScore)
	
	#更新到战队临时对象上
	mteam1.FightResult(leftteamScore, winorlose)
	mteam2.FightResult(rightteamScore, -winorlose)
	
	#发送战斗统计数据
	if winorlose == 1:
		cNetMessage.PackPyMsg(JT_S_FightInfo, (leftdata, rightdata))
	else:
		cNetMessage.PackPyMsg(JT_S_FightInfo, (rightdata, leftdata))
	for role in fightObj.left_camp.roles:
		role.BroadMsg_NoExcept()
	for role in fightObj.right_camp.roles:
		role.BroadMsg_NoExcept()
	
	#更新面板积分和胜负
	mteam1.BroadAfterFight()
	mteam2.BroadAfterFight()


def GetMWin(teamscore):
	#系数teamscore 积分差:我的战队-别人战队
	for score, m in JTConfig.JTScoreMWinList:
		if teamscore <= score:
			return m
	print "GE_EXC jtcross error GetMWin not this config (%s)" % teamscore
	return 0

def GetMLose(teamscore):
	#系数teamscore 积分差:我的战队-别人战队
	for score, m in JTConfig.JTScoreMLoseList:
		if teamscore <= score:
			return m
	print "GE_EXC jtcross error GetMLose not this config (%s)" % teamscore
	return 0

def GetKE(teamscore):
	for score, k, m in JTConfig.JTScoreKEList:
		if teamscore <= score:
			return k, m
	print "GE_EXC, jtcross error GetKE not this config (%s)" % teamscore
	return 0, 0

def CountScore(meteam_Score, theyteam_Score, winorlose):
	#Y=E*（K*M） 
	if meteam_Score <= ProtectScore and winorlose != 1:
		#输了，保护积分，不扣分
		return 0
	K, E = GetKE(meteam_Score)
	if winorlose == 1:
		E = 100
		M = GetMWin(meteam_Score - theyteam_Score)
	else:
		M = GetMLose(meteam_Score - theyteam_Score)
	
	score = int(E * 0.01 * K * M * 0.01)
	if score != 0:
		return score
	if winorlose == 1:
		return 1
	return 0

##########################################################################
#活动开启关闭，由时间模块控制
##########################################################################
def StartCrossJT():
	global IsStart
	IsStart = True

def EndCrossJT():
	global IsStart
	if IsStart is False:
		return
	IsStart = False
	
	#结束，清理数据，踢掉玩家
	global MatchTeams
	MatchTeams = set()
	#直接全部人传送回去
	scene = cSceneMgr.SearchPublicScene(JTDefine.JTReadySceneID)
	if scene:
		for role in scene.GetAllRole():
			role.GotoLocalServer(None, None)
	
	#重新排序
	SortCrossRank()
	#把新的排名同步给所有的逻辑进程
	UpdataRankToLogic()
	#把参加过这次获得的战斗信息重新同步到所有的逻辑进程
	UpdataJTeamInfoToLogic()
	global Cross_JT_Dict
	Cross_JT_Dict = {}
	
#===============================================================================
#客户端消息处理
#===============================================================================
def RequestStartMatch(role, msg):
	'''
	请求跨服组队竞技场开始匹配
	@param role:
	@param msg:
	'''
	global IsStart
	if IsStart is False:
		return
	if role.GetCD(EnumCD.JTMatchCD):
		return
	cjteam = role.GetTempObj(EnumTempObj.CrossJTeamObj)
	if not cjteam:
		return
	global MatchTeams
	if cjteam in MatchTeams:
		return
	if not cjteam.IsMatchTeamLeader(role):
		return
	if len(cjteam.members) != 3:
		return
	for member in cjteam.members:
		if not Status.CanInStatus(member, EnumInt1.ST_JTMatch):
			return
	#进入匹配状态
	for member in cjteam.members:
		Status.ForceInStatus(member, EnumInt1.ST_JTMatch)
	#清理匹配次数
	cjteam.matchTimes = 0
	MatchTeams.add(cjteam)
	role.SetCD(EnumCD.JTMatchCD, 15)
	for role in cjteam.members:
		role.SendObj(JT_S_MatchStatus, 1)

def RequestCancleMatch(role, msg):
	'''
	请求跨服组队竞技场取消匹配
	@param role:
	@param msg:
	'''
	global IsStart
	if IsStart is False:
		return
	if not Status.IsInStatus(role, EnumInt1.ST_JTMatch):
		return
	cjteam = role.GetTempObj(EnumTempObj.CrossJTeamObj)
	if not cjteam:
		return
	if not cjteam.IsMatchTeamLeader(role):
		return
	if role.GetCD(EnumCD.JTMatchCD):
		role.Msg(2, 0, GlobalPrompt.JT_Tips_15)
		return
	CancleMatch(cjteam)

def RequestCrossRank(role, msg):
	'''
	请求查看跨服进程的组队竞技排行榜
	@param role:
	@param msg:
	'''
	global IsStart
	if IsStart is False:
		return
	if not role.GetTempObj(EnumTempObj.CrossJTeamObj):
		return
	backId, levelrangeIndex = msg
	global JTCrossRankLevel_Sync_Dict
	role.CallBackFunction(backId, JTCrossRankLevel_Sync_Dict.get(levelrangeIndex, []))

def RequestLeaveJT(role, msg):
	'''
	请求离开跨服组队竞技场
	@param role:
	@param msg:
	'''
	if not role.GetTempObj(EnumTempObj.CrossJTeamObj):
		return
	role.GotoLocalServer(None, None)

def RequestChangeFightHero(role, msg):
	'''
	修改战队战斗时上阵的英雄
	@param role:
	@param msg:
	'''
	heroId = msg
	hero = role.GetHero(heroId)
	if not hero or not hero.GetStationID():
		return
	if role.GetI64(EnumInt64.JTHeroID) == heroId:
		return
	cjteam = role.GetTempObj(EnumTempObj.CrossJTeamObj)
	if not cjteam:
		return
	role.SetI64(EnumInt64.JTHeroID, heroId)


def RequestChangeJTeamPos(role, msg):
	'''
	修改战队队员出战的位置
	@param role:
	@param msg:
	'''
	pos1, pos2 = msg
	#位置是否合法
	if pos1 not in (1,2,3) or pos2 not in (1,2,3):
		return
	if pos1 == pos2:
		return
	cjteam = role.GetTempObj(EnumTempObj.CrossJTeamObj)
	if not cjteam:
		return
	if not cjteam.IsMatchTeamLeader(role):
		return
	cjteam.ChangePos(pos1-1, pos2-1)

def RequestChangeJTeamLeader(role, msg):
	'''
	转让战队匹配队伍的队长
	@param role:
	@param msg:
	'''
	leaderId = msg
	cjteam = role.GetTempObj(EnumTempObj.CrossJTeamObj)
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
	cjteam = role.GetTempObj(EnumTempObj.CrossJTeamObj)
	if not cjteam:
		return
	if cjteam.IsMatchTeamLeader(role):
		return
	
	leader = cRoleMgr.FindRoleByRoleID(cjteam.matchTeamLeaderId)
	if not leader or leader.IsLost():
		cjteam.ChangeLeader(role.GetRoleID())
		return
	
	leader.SendObjAndBack(JT_S_CrossRequestLeader, role.GetRoleName(), 60, LeaderBack, role.GetRoleID())
	

def LeaderBack(role, callArgv, regparam):
	#队长回调，或者超时回调
	if callArgv == 1:
		cjteam = role.GetTempObj(EnumTempObj.CrossJTeamObj)
		if not cjteam:
			return
		if not cjteam.IsMatchTeamLeader(role):
			return
		newLeader = cRoleMgr.FindRoleByRoleID(regparam)
		if not newLeader:
			return
		leaderjteam = newLeader.GetTempObj(EnumTempObj.CrossJTeamObj)
		if not leaderjteam:
			return
		if leaderjteam.teamId != cjteam.teamId:
			return
		leaderjteam.ChangeLeader(regparam)
	elif callArgv is None:
		newLeader = cRoleMgr.FindRoleByRoleID(regparam)
		if not newLeader:
			return
		leaderjteam = newLeader.GetTempObj(EnumTempObj.CrossJTeamObj)
		if not leaderjteam:
			return
		if leaderjteam.IsMatchTeamLeader(newLeader):
			return
		leaderjteam.ChangeLeader(regparam)
#================================================================================================
#事件处理
#================================================================================================
def OnRoleExit(role, param):
	global IsStart
	if IsStart is False:
		return
	cjteam = role.GetTempObj(EnumTempObj.CrossJTeamObj)
	if not cjteam:
		return
	cjteam.LeaveCrossJTeam(role)
	if not Status.IsInStatus(role, EnumInt1.ST_JTMatch):
		return
	CancleMatch(cjteam)

def ClientLost(role, param):
	if IsStart is False:
		return
	cjteam = role.GetTempObj(EnumTempObj.CrossJTeamObj)
	if not cjteam:
		return
	cjteam.LeaveCrossJTeam(role)
	if not Status.IsInStatus(role, EnumInt1.ST_JTMatch):
		return
	CancleMatch(cjteam)

def CancleMatch(cjteam):
	#取消匹配
	global MatchTeams
	MatchTeams.discard(cjteam)
	cjteam.matchTimes = 0
	for role in cjteam.members:
		Status.Outstatus(role, EnumInt1.ST_JTMatch)
		role.SendObj(JT_S_MatchStatus, 0)

def CallNewDay():
	WeekDay = cDateTime.WeekDay()
	if WeekDay != 0:
		return
	num = JTDefine.GetZBStartFlagNum()
	if num == 0:
		global JTCrossRankLevel_Sync_Dict
		#重新排序
		SortCrossRank()
		JTZBGroup.InitZBSelectData(JTCrossRankLevel_Sync_Dict)
#================================================================================================
#排行数据处理
#================================================================================================

def LoginRequestRank(param):
	#逻辑进程请求排行榜
	processId = param
	UpdataRankToLogic(processId)

def LoginChangeJTinfo(param):
	#逻辑进程的战队信息改变了
	jteamId, info = param
	global JT_CrossTeamDict
	jteamData = JT_CrossTeamDict.get(jteamId)
	if not jteamData:
		return
	if info is None:
		del JT_CrossTeamDict[jteamId]
		return
	jteamName, memberRankData = info
	jteamData[3] = jteamName
	jteamData[6] = memberRankData

###########################################################################
#排行榜数据处理
###########################################################################

def UpdataRankToLogic(processId = 0):
	#把排行榜数据同步到逻辑进程
	global JTCrossRankLevelDict
	Call.SuperServerCall(processId, "Game.JT.JTeam", "UpdateRankByCross", JTCrossRankLevelDict)


def UpdataJTeamInfoToLogic():
	#把战队数据同步到逻辑进程
	global Cross_JT_Dict
	processInfoDict = {}
	PIG = processInfoDict.get
	for teamId, jteam in Cross_JT_Dict.iteritems():
		if not jteam.hasChange:
			continue
		processId = jteam.processId
		teaminfo = jteam.GetChangeInfo()
		teaminfodict = PIG(processId)
		if teaminfodict:
			teaminfodict[teamId] = teaminfo
		else:
			processInfoDict[processId] = {teamId : teaminfo}
	
	CS = Call.ServerCall
	for processId, processTeamInfoDict in processInfoDict.iteritems():
		CS(processId, "Game.JT.JTeam", "UpdateJTeamInfoByCross", processTeamInfoDict)


def GetJTeamLevelRangeIndex(teamLevel):
	if 60 <= teamLevel < 80: return 1
	elif 80 <= teamLevel < 100: return 2
	elif 100 <= teamLevel < 120: return 3
	elif 120 <= teamLevel < 140: return 4
	elif 140 <= teamLevel < 160: return 5
	elif 160 <= teamLevel: return 6
	else : return 1

def GetGrade(rank, teamScore, guidegradeconfig):
	'''
	根据排名，积分获取段位
	@param rank:
	@param teamScore:
	@param guidegradeconfig:引导配置
	原理是先排序，从第一名遍历起，先获取最大段位配置为引导配置，判断积分和排名是否符合
	不符合就使用下一个段位的配置,使用引导配置可以减少区间遍历的次数
	'''
	
	if not guidegradeconfig:
		print "GE_EXC. GetGrade jtcross grade error "
		#guidegradeconfig = JTConfig.JTGradeDict.get(max(JTConfig.JTGradeDict.keys()))
		return 0, None
	
	if teamScore < guidegradeconfig.minScore:
		#积分不够，下一个段位
		guidegradeconfig = JTConfig.JTGradeDict.get(guidegradeconfig.grade - 1)
		if not guidegradeconfig:
			print "GE_EXC. next grade jtcross grade error "
			return 0, None
		return GetGrade(rank, teamScore, guidegradeconfig)
		
	#积分符合
	if not guidegradeconfig.needrank or rank <= guidegradeconfig.needrank:
		#排名也符合, 或者没有排名需求，就是这个段位了
		return guidegradeconfig.grade, guidegradeconfig

	#不符合排名，下一个段位
	guidegradeconfig = JTConfig.JTGradeDict.get(guidegradeconfig.grade - 1)
	if not guidegradeconfig:
		print "GE_EXC. rank grade jtcross grade error "
		return 0 , None
	return GetGrade(rank, teamScore, guidegradeconfig)
	

def SortCrossRank():
	#排序
	global JT_CrossTeamDict
	global JTCrossRankLevelDict
	global JTCrossRankLevel_Sync_Dict
	JTCrossRankLevelDict = {}
	JTCrossRankLevel_Sync_Dict = {}
	
	teamDataList = JT_CrossTeamDict.values()
	teamDataList.sort(key = lambda it:(it[4], it[8], it[9]), reverse = True)
	teamDataList = teamDataList[:JTDefine.MaxRank]
	teamIds = [teamdata[2] for teamdata in teamDataList]
	
	for teamId in JT_CrossTeamDict.keys():
		if teamId in teamIds:
			continue
		#删除不在榜上的人的数据
		del JT_CrossTeamDict[teamId]
	
	guidegradeconfig = JTConfig.MaxGradeConfig
	MINSCORE = JTConfig.MinGradeMinScore
	#按照积分和排名修正段位, 按照战队等级组合成同步排行榜
	
	for rank, rankData in enumerate(teamDataList):
		teamscore = rankData[4]
		if teamscore < MINSCORE or not guidegradeconfig:
			rankData[5] = 0
		else:
			rankData[5], guidegradeconfig = GetGrade(rank + 1, teamscore, guidegradeconfig)
		#插入真正的排名
		rankData[10] = rank + 1
		#构造等级段排行榜, 用于同步给客户端
		rangeIndex = GetJTeamLevelRangeIndex(rankData[7])
		levelList = JTCrossRankLevelDict.get(rangeIndex)
		if not levelList:
			levelList = JTCrossRankLevelDict[rangeIndex] = []
		levelList.append(rankData)
	
	#构建排行榜同步数据，截留JTDefine.MaxLevelRank名
	for rangeIndex, rankDateList in JTCrossRankLevelDict.items():
		if len(rankDateList) <= JTDefine.MaxLevelRank:
			JTCrossRankLevel_Sync_Dict[rangeIndex] = rankDateList
		else:
			JTCrossRankLevel_Sync_Dict[rangeIndex] = rankDateList[:JTDefine.MaxLevelRank]

def AfterLoad():
	#排序，并且同步到所有的逻辑进程(参数 0)
	SortCrossRank()
	UpdataRankToLogic()


if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.EnvIsQQ() or Environment.EnvIsFT() or Environment.IsDevelop or (Environment.EnvIsNA() and not Environment.IsNAPLUS1) or (Environment.EnvIsRU()and not Environment.IsRUGN) or Environment.EnvIsPL()) and Environment.IsCross:
		if cProcess.ProcessID == Define.GetDefaultCrossID():
			#JT_CrossTeamDict = Contain.Dict("JT_CrossTeamDict", (2038, 1, 1), AfterLoad)
			JT_CrossTeamDict = Contain.Dict("JT_CrossTeamDictNew", (2038, 1, 1), AfterLoad)
			
			cComplexServer.RegPerSecondCallFunction(CallPerSecond)
			cComplexServer.RegAfterNewDayCallFunction(CallNewDay)
			
			Event.RegEvent(Event.Eve_BeforeExit, OnRoleExit)
			Event.RegEvent(Event.Eve_ClientLost, ClientLost)
			
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_RequestLeaveJT", "请求离开跨服组队竞技场"), RequestLeaveJT)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_RequestJTRank", "请求查看组队竞技排行榜"), RequestCrossRank)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_RequestStartMatch", "请求跨服组队竞技场开始匹配"), RequestStartMatch)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_RequestCancleMatch", "请求跨服组队竞技场取消匹配"), RequestCancleMatch)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_Cross_RequestChangeFightHero", "修改战队战斗时上阵的英雄"), RequestChangeFightHero)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_Cross_RequestChangeJTeamPos", "修改战队队员出战的位置"), RequestChangeJTeamPos)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_Cross_RequestChangeJTeamLeader", "转让战队匹配队伍的队长"), RequestChangeJTeamLeader)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_Cross_RequestToBeJTeamLeader", "申请成为战队匹配的队长"), RequestToBeJTeamLeader)
