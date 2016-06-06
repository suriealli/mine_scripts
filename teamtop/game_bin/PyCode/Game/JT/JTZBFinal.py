#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.JT.JTZBFinal")
#===============================================================================
# 跨服争霸赛
#===============================================================================
import random
import copy
import Environment
import cComplexServer
import cSceneMgr
import cNetMessage
import cProcess
import cDateTime
from Game.Persistence import Contain, BigTable
from World import Define
from ComplexServer.Time import Cron
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Common.Other import GlobalPrompt
from Game.Role import Call
from Game.Fight import FightEx
from Game.Role import Status, Event
from Game.Activity.Title import Title
from Game.Role.Mail import Mail
from Game.Role.Data import EnumTempObj,EnumInt1, EnumObj, EnumTempInt64, EnumInt16
from Game.JT import JTDefine, JTConfig, JTZBGroup

if "_HasLoad" not in dir():
	IsFinalStart = False	#比赛是否开始标志
	FinalStep = 0			#比赛第几步
	FinalStepList = [32,16,8]
	#32 : 32->16, 
	#16 : 16->8, 
	#8 : 8->4, 
	#4 : 4->1, 
	#3 : 第3名
	#2 : 第二名
	#1 : 第一名
	FinalFightRound = 0		#一场比赛打了几轮
	FinalTeamDict = {}	#缓存可参加当场比赛的战队对象
	MatchTeamDict = {}	#{groupId->{teamId:obj}}	#缓存3人都参加活动的战队，用于匹配
	GroupFightObjs = set()
	Final_Fight_Result = {}	#保存战斗结果信息
	Fight_View_Data = {}	#缓存一场战斗的观战数据
	#消息
	NJT_S_ZBFinalPanal = AutoMessage.AllotMessage("NJT_S_ZBFinalPanal", "同步新版跨服争霸总决赛战队面板数据")
	NJT_S_ZBFightResult = AutoMessage.AllotMessage("NJT_S_ZBFightResult", "同步新版跨服争霸总决赛战斗结果")
	#日志
	Tra_InitNZB32Data = AutoLog.AutoTransaction("Tra_InitNZB32Data", "新版跨服争霸生成32强数据")
	Tra_NJTFinalRoundData = AutoLog.AutoTransaction("Tra_NJTFinalRoundData", "新版跨服争霸总决赛每轮战斗结果")
	Tra_NJTFinalRoleViewData = AutoLog.AutoTransaction("Tra_NJTFinalRoleViewData", "新版跨服争霸同步冠军战队3人外观数据")
	Tra_NZBJoinReward = AutoLog.AutoTransaction("Tra_NZBJoinReward", "新版跨服争霸赛参加奖")
	Tra_NZBFinalReward = AutoLog.AutoTransaction("Tra_NZBFinalReward", "新版跨服争霸赛总决赛奖励")
	
class FinalTeam(object):
	def __init__(self, teamId, groupIndex, teamData):
		#队伍ID, 队伍名，服名，服ID，战队积分，战队段位，总战斗力，成员IDs, 总排名, 队伍信息，index
		self.teamId = teamId
		self.groupId = groupIndex	#1初级 2精锐 3巅峰
		self.teamData = teamData
		self.teamName = teamData[1]
		self.processName = teamData[2]
		self.processId = teamData[3]
		self.teamPoint = teamData[4]
		self.teamGrade = teamData[5]
		self.totalZDL = teamData[6]
		self.teamdata = teamData[9]
		self.finalGrade = teamData[10]
		
		self.roles = []
		self.memberVeiwData = []
		#已经战斗过的小组ID
		self.hasFightTeams = set()
		self.fightResult = {}
		self.groupRound = 0
		
		self.winCnt = 0
		self.loseCnt = 0
		self.isEnd = False
		
		self.fightResult_data = {}
		self.matchTeamLeaderId = 0
		
	def JoinRole(self, role):
		self.roles.append(role)
		role.SetTempObj(EnumTempObj.CrossJTFinalTeam, self)
		
		if len(self.roles) == 1:
			self.matchTeamLeaderId = role.GetRoleID()
			
		if len(self.roles) == 3:
			if self.isEnd:
				return
			global MatchTeamDict
			if self.groupId not in MatchTeamDict:
				MatchTeamDict[self.groupId] = {}
			group_dict = MatchTeamDict[self.groupId]
			group_dict[self.teamId] = self
		
		self.BroadPanal()
		role.SendObj(NJT_S_ZBFightResult, self.fightResult_data)
		
	def BroadPanal(self):
		#同步面板信息,战队名字，胜利次数，失败次数,成员面板外观数据(顺序列表)
		cNetMessage.PackPyMsg(NJT_S_ZBFinalPanal, (self.teamName, \
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
		role.SetTempObj(EnumTempObj.CrossJTFinalTeam, None)
		#假如是队长
		if role.GetRoleID() == self.matchTeamLeaderId and len(self.roles) > 0:
			self.matchTeamLeaderId = self.roles[0].GetRoleID()
		#队伍无人了，设置队长为0
		if len(self.roles) <= 0:
			self.matchTeamLeaderId = 0
			
		if len(self.roles) < 3:
			self.DelMatchTeam()
			
		self.BroadPanal()
		
	def IsMatchTeamLeader(self, role):
		return role.GetRoleID() == self.matchTeamLeaderId
	
	def ChangeLeader(self, roleId):
		if len(self.roles) < 1:
			return
		for role in self.roles:
			if role.GetRoleID() == roleId:
				self.matchTeamLeaderId = roleId
				cNetMessage.PackPyMsg(JTZBGroup.NJT_S_CrossChangeLeader, roleId)
				for role in self.roles:
					role.BroadMsg_NoExcept()
				return
			
	def ChangeFightPos(self, pos1, pos2):
		if not self.roles or pos1 > len(self.roles) or pos2 > len(self.roles):
			return
		self.roles[pos1], self.roles[pos2] = self.roles[pos2], self.roles[pos1]
		
		cNetMessage.PackPyMsg(JTZBGroup.NJT_S_CrossChangePos, (pos1 + 1, pos2 + 1))
		for role in self.roles:
			role.BroadMsg_NoExcept()
			
	def BroadResult(self):
		for role in self.roles:
			role.SendObj(NJT_S_ZBFinalPanal, (self.teamName, self.winCnt, self.loseCnt))
		
	def ByeRound(self):
		#轮空
		SetFianlFightResult(self.teamName, '', -2, self.groupId)
		print "BLUE,JTZBFinal final team ByeRound",self.teamId
		for role in self.roles:
			role.Msg(2, 0, GlobalPrompt.JT_ZB_Tips_1)
		if self.isEnd:
			print "GE_EXC,final team bye error is End (%s)" % self.teamId
			return
		self.Win()
		
	def Win(self):
		self.winCnt += 1
		self.BroadPanal()
		if self.isEnd:
			return
		if self.winCnt >= 2:
			#匹配列表中删除该战队
			self.DelMatchTeam()
			self.isEnd = True
			self.nextGrade()
		with Tra_NJTFinalRoundData:
			AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveNJTFinalRoundData, (self.teamId))
			
	def Lose(self):
		self.loseCnt += 1
		self.BroadPanal()
		if self.isEnd:
			return
		if self.loseCnt >= 2:
			self.DelMatchTeam()
			if self.groupRound == 3 and self.finalGrade == 4:
				#3回合输2场的为第3名
				self.finalGrade = 3
			self.isEnd = True
			for role in self.roles:
				role.Msg(2, 0, GlobalPrompt.JT_OutGrade)
		with Tra_NJTFinalRoundData:
			AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveNJTFinalRoundData, (self.teamId))
			
	def DelMatchTeam(self):
		#匹配列表中删除该战队
		global MatchTeamDict
		if self.groupId not in MatchTeamDict:
			MatchTeamDict[self.groupId] = {}
		group_dict = MatchTeamDict[self.groupId]
		if self.teamId in group_dict:
			del group_dict[self.teamId]
		
	def nextGrade(self):
		global FinalStepList
		if self.finalGrade in FinalStepList:#16,8,4强
			self.finalGrade = self.finalGrade / 2
		else:
			if self.finalGrade == 4:
				if self.groupRound == 2:
					#2回合结束战斗的是冠军
					self.finalGrade = 1
				elif self.groupRound == 3:
					#3回合胜率2次的为亚军
					self.finalGrade = 2
		for role in self.roles:
			role.Msg(2, 0, GlobalPrompt.JT_NextGrade)
		
	def ReadyFight(self, otherTeam):
		self.hasFightTeams.add(otherTeam.teamId)
		#准备和这个队伍比赛
		self.BroadResult()
		
	def SynResultByGroup(self):
		global Final_Fight_Result
		
		self.fightResult_data = Final_Fight_Result.get(self.groupId)
		for role in self.roles:
			role.SendObj(NJT_S_ZBFightResult, self.fightResult_data)
		
def ReadyFinalFight1():
	#争霸赛第二天，星期二，21.55-22.20
	#32进16比赛，提前5分钟进入
	#8进4比赛，提前5分钟进入
	#4进1比赛，提前5分钟进入
	num = JTDefine.GetZBStartFlagNum()
	if num not in [2,3,4]:
		return
	global FinalStep
	if num == 2:
		FinalStep = 32
	elif num == 3:
		FinalStep = 8
	else:
		FinalStep = 4
	BuildFinalData()
	
def ReadyFinalFight2():
	#争霸赛第二天，星期二，22.25-22.50
	#16进8比赛，提前15分钟进入
	#8进4比赛，提前15分钟进入
	num = JTDefine.GetZBStartFlagNum()
	if num != 2:
		return
	global FinalStep
	FinalStep = 16
	BuildFinalData()
	
	
def BuildFinalData():
	global IsFinalStart
	global FinalTeamDict
	global FinalStep
	global NJT_Final_Dict
	global Final_Fight_Result
	global Fight_View_Data
	
	IsFinalStart = True
	FinalTeamDict = {}
	Final_Fight_Result = {}
	Fight_View_Data = {}
	
	if FinalStep == 32 or FinalStep == 8 or FinalStep == 4:
		#10分钟后开启
		cComplexServer.RegTick(60 * 10, StartFinal, FinalStep)
	elif FinalStep == 16:
		#6分钟后开启
		cComplexServer.RegTick(60 * 6, StartFinal, FinalStep)
		
	for groupId, teamList in NJT_Final_Dict.data.iteritems():
		if groupId == 4:
			continue
		FinalTeamDict[groupId] = TEMP_TEAM = {}
		for teamData in teamList:
			if teamData[10] != FinalStep:
				continue
			teamId = teamData[0]
			TEMP_TEAM[teamId] = FinalTeam(teamId, groupId, teamData)
	
def StartFinal(callArgv = None, regparam = None):
	global IsFinalStart
	if not IsFinalStart:
		return
	global FinalFightRound
	global FinalStep
	#3轮比赛开始
	FinalFightRound = 0
	FinalOneRound()
	#结束
	if FinalStep == 32 or FinalStep == 16:
		cComplexServer.RegTick(60 * 23, EndFinal, None)
	elif FinalStep == 8 or FinalStep == 4:
		cComplexServer.RegTick(60 * 30, EndFinal, None)
		
		
def EndFinal(callArgv = None, regparam = None):
	global FinalStep
	global IsFinalStart
	if not IsFinalStart:
		return
	IsFinalStart = False
	scene = cSceneMgr.SearchPublicScene(JTDefine.JTZBSceneID)
	if scene:
		for role in scene.GetAllRole():
			role.GotoLocalServer(None, None)
	
	#32 : 32->16, 
	#16 : 16->8, 
	#8 : 8->4, 
	global NJT_Final_Dict
	global FinalTeamDict
	#3轮比赛都结束时，才将进阶数据写入DB，这样做是为了在3轮比赛中出现停服现象，起服后能重新开启比赛，不必做数据修复相关
	for groupId, teamList in NJT_Final_Dict.data.iteritems():
		if groupId == 4: continue
		teamDict = FinalTeamDict.get(groupId, {})
		for teamData in teamList:
			teamId = teamData[0]
			team = teamDict.get(teamId)
			if not team:
				continue
			teamData[10] = team.finalGrade
	NJT_Final_Dict.HasChange()
	
	if FinalStep == 4:
		#冠军了，总决赛结束,发奖励
		ZBReward()
		#取第三战区冠军战队数据
		SaveStatueData()
		SyncFinalToLogic(0, False, True)
	else:
		SyncFinalToLogic(0, True, False)
	#同步观战数据
	SynZBFinalViweData()
#	#更新状态
#	if FinalStep in FinalStepList:#步骤在32-16,16-8,8-4
#		FinalStep = FinalStep / 2
	ClearTempData()
	
def ClearTempData():
	global FinalTeamDict,FinalFightRound,GroupFightObjs,MatchTeamDict,Final_Fight_Result
	FinalTeamDict = {}
	FinalFightRound = 0
	GroupFightObjs = set()
	FinalStep = 0
	MatchTeamDict = {}
	Final_Fight_Result = {}
	
def ZBReward():
	#参与奖1-100名都获得
	rankData = JTZBGroup.JT_ZBSelectData.get(2)
	for groubId, rankList in rankData.iteritems():
		reward = JTDefine.JTZBJoinLiBao.get(groubId)
		if not reward:
			print "GE_EXC,JTDefine.JTZBJoinLiBao has no key(%s)" % groubId
			continue
		for teamdata in rankList:
			with Tra_NZBJoinReward:
				for roleId in teamdata[10]:
					Mail.SendMail(roleId, GlobalPrompt.JT_RewardMailTitle, GlobalPrompt.JT_RewardMailSender, GlobalPrompt.JT_RewardMailContent1, items = reward)
	#冠军礼包、亚军礼包、季军礼包、8强礼包
	global NJT_Final_Dict
	for groupId, rankList in NJT_Final_Dict.data.iteritems():
		if groupId == 4 : continue
		zhanqu = GlobalPrompt.ReturnJTZhanqu(groupId)
		for teamData in rankList:
			teamIndex = teamData[10]
			if teamIndex > 32:
				continue
			key = (groupId, teamIndex)
			cfg = JTConfig.JT_ZB_Reward.get(key)
			if not cfg:
				continue
			with Tra_NZBFinalReward:
				for roleId in teamData[7]:
					if cfg.itemRewards:
						Mail.SendMail(roleId, GlobalPrompt.JT_RewardMailTitle, GlobalPrompt.JT_RewardMailSender, GlobalPrompt.JT_RewardMailContent2 % (zhanqu, teamIndex,), items = cfg.itemRewards)
					if cfg.titleId:
						Title.AddTitle(roleId, cfg.titleId)
				
def SaveStatueData():
	global NJT_Final_Dict
	NJT_Final_Dict[4] = {}
	#保存各个战区前3的玩家
	threeData = NJT_Final_Dict.get(4)
	for groupId, teamList in NJT_Final_Dict.data.iteritems():
		if groupId == 4: continue
		threeData[groupId] = THREE_DATA = {}
		for teamData in teamList:
			if teamData[10] == 1 or teamData[10] == 2 or teamData[10] == 3:
				THREE_DATA[teamData[10]] = teamData
	NJT_Final_Dict.changeFlag = True
	
	#存巅峰战区第一名战队成员的外观数据
	teamList = NJT_Final_Dict.get(3)
	if not teamList:
		return
	memberIds = set()
	for team in teamList:
		if team[10] != 1:
			continue
		memberIds = team[7]
	if not memberIds:
		print "GE_EXC,JTZBFinal.EndFinal memberIds is None"
		return
	global NJT_Statue_Data
	global NJT_Final_Role

	#清理不是巅峰冠军战队成员的外观数据
	for roleId in NJT_Final_Role.keys():
		if roleId not in memberIds:
			del NJT_Final_Role[roleId]
	#清理老数据先
	NJT_Statue_Data.clear()
	#写入新的外观数据
	for memberId in memberIds:
		NJT_Statue_Data[memberId] = NJT_Final_Role.get(memberId)
	#NJT_Statue_Data.changeFlag = True
	#同步外观数据
	SynStatueData()
	
def FinalOneRound(callArgv = None, regparam = None):
	#一轮战斗处理逻辑
	global IsFinalStart
	if not IsFinalStart:
		return
	global FinalFightRound
	global MatchTeamDict
	FinalFightRound += 1
	if FinalFightRound > 3:
		return
	
	#其中1，3轮随机匹配即可，第二轮比赛需要将胜一场和失败一场的分表进行匹配
	if FinalFightRound == 1 or FinalFightRound == 3:
		for groupId, teamDict in MatchTeamDict.items():
			teamIds = set(teamDict.keys())
			for teamId, gteam in teamDict.items():
				if gteam.groupRound == FinalFightRound:
					continue
				gteam.groupRound = FinalFightRound
				if teamId in teamIds:
					teamIds.remove(teamId)
				if not teamIds:
					#无随机了，就直接赢
					gteam.ByeRound()
					continue
				teamId_2 = random.sample(teamIds,1)[0]
				#从匹配列表中删除战队2
				teamIds.remove(teamId_2)
				
				gteam2 = teamDict.get(teamId_2)
				if not gteam2:
					#随机出来的战队不存在，就轮空直接赢
					gteam.ByeRound()
					continue
				if gteam2.groupRound == FinalFightRound:
					print "GE_EXC, JTZBFinal.FinalOneRound repeat match team2 in GroupRound repeat",groupId,teamId,teamId_2,FinalFightRound
					gteam.ByeRound()
					continue
				#匹配成功，尝试进入战斗
				gteam2.groupRound = FinalFightRound
				
				gteam2.ReadyFight(gteam)
				gteam.ReadyFight(gteam2)

				TryFight(True, (gteam, gteam2, 1, groupId))
				
	elif FinalFightRound == 2:
		#第二场比赛,
		winMatch = {}
		lostMatch = {}
		for groupId, teamDict in MatchTeamDict.iteritems():
			winMatch[groupId] = WIN_DICT = {}
			lostMatch[groupId] = LOST_DICT = {}
			for teamId, team in teamDict.iteritems():
				if team.winCnt == 1:
					WIN_DICT[teamId] = team
				else:
					LOST_DICT[teamId] = team
		for groupId, teamDict in winMatch.items():
			teamIds = set(teamDict.keys())
			for teamId, gteam in teamDict.items():
				if gteam.groupRound == FinalFightRound:
					continue
				gteam.groupRound = FinalFightRound
				
				if teamId in teamIds:
					teamIds.remove(teamId)
				if not teamIds:
					#无随机列表，直接赢
					gteam.ByeRound()
					continue
				teamId_2 = random.sample(teamIds,1)[0]
				teamIds.remove(teamId_2)
				
				gteam2 = teamDict.get(teamId_2)
				if not gteam2:
					#随机出来的战队不存在，就轮空直接赢
					gteam.ByeRound()
					continue
				if gteam2.groupRound == FinalFightRound:
					print "GE_EXC, JTZBFinal.FinalOneRound repeat match team2 in GroupRound repeat",groupId,teamId,teamId_2,FinalFightRound
					gteam.ByeRound()
					continue
				#匹配成功，尝试进入战斗
				gteam2.groupRound = FinalFightRound
				gteam2.ReadyFight(gteam)
				gteam.ReadyFight(gteam2)
				TryFight(True, (gteam, gteam2, 1, groupId))
		
		for groupId, teamDict in lostMatch.items():
			teamIds = set(teamDict.keys())
			for teamId, gteam in teamDict.items():
				if gteam.groupRound == FinalFightRound:
					continue
				gteam.groupRound = FinalFightRound
				if teamId in teamIds:
					teamIds.remove(teamId)
				if not teamIds:
					#无随机列表，直接赢
					gteam.ByeRound()
					continue
				teamId_2 = random.sample(teamIds,1)[0]
				teamIds.remove(teamId_2)
				
				gteam2 = teamDict.get(teamId_2)
				if not gteam2:
					#随机出来的战队不存在，就轮空直接赢
					gteam.ByeRound()
					continue
				if gteam2.groupRound == FinalFightRound:
					print "GE_EXC, JTZBFinal.FinalOneRound repeat match team2 in GroupRound repeat",groupId,teamId,teamId_2,FinalFightRound
					continue
				#匹配成功，尝试进入战斗
				gteam2.groupRound = FinalFightRound
				gteam2.ReadyFight(gteam)
				gteam.ReadyFight(gteam2)
				TryFight(True, (gteam, gteam2, 1, groupId))
	global FinalStep
	if FinalStep == 32 or FinalStep == 16:
		#7分之后处理超时战斗
		cComplexServer.RegTick(60 * 7, CheckFightAndWait, None)
	elif FinalStep == 8 or FinalStep == 4:
		#9分之后处理超时战斗
		cComplexServer.RegTick(60 * 9, CheckFightAndWait, None)
	#2分钟后同步次结果
	cComplexServer.RegTick(60 * 2, SynFightResult, None)

def SynFightResult(callArgv = None, regparam = None):
	#同步战斗结果
	global IsFinalStart
	
	global FinalTeamDict
	for _, teamDict in FinalTeamDict.iteritems():
		for team in teamDict.itervalues():
			team.SynResultByGroup()
	if not IsFinalStart:
		return
	cComplexServer.RegTick(60 * 2, SynFightResult, None)
		
def CheckFightAndWait(callArgv = None, regparam = None):
	#在下一轮开启前，检查一下战斗是否已经结束，没有结束则强制结束
	global GroupFightObjs, IsFinalStart
	if not IsFinalStart:
		return
	if GroupFightObjs:
		for fightObj in GroupFightObjs:
			if fightObj.result is not None:
				continue
			print "GE_EXC CheckFightEnd has not end fight"
			fightObj.end(0)
		GroupFightObjs = set()
	#同步观战数据到逻辑服
	#SynZBFinalViweData()
	#同步下结果
	global FinalTeamDict
	for _, teamDict in FinalTeamDict.iteritems():
		for team in teamDict.itervalues():
			team.SynResultByGroup()
	#30秒后下一轮
	cComplexServer.RegTick(30, FinalOneRound, None)
	
	
def TryFight(callArgv = None, regparam = None):
	global IsFinalStart
	if not IsFinalStart:
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
		print "GE_EXC, JTZBFinal, TryFight but in fightstatus"
	if teamRound < 2 :
		#等待20秒匹配一次
		cComplexServer.RegTick(20, TryFight, (gteam1, gteam2, teamRound + 1, groupId))
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
		print "GE_EXC, JTZBFinal TryFight timeout but in fightstatus"
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
	fobj = FightEx.PVP_JTFinal(gteam1.roles, gteam2.roles, JTDefine.JT_fightType, AfterTeamFight, (gteam1, gteam2, groupId))
	GroupFightObjs.add(fobj)
	
def AfterTeamFight(fightObj):
	global IsFinalStart
	if not IsFinalStart:
		print "GE_EXC, AfterTeamFight final is end"
		return
	#战斗回调,处理结果
	winorlose = fightObj.result
	gteam1, gteam2, groupId = fightObj.after_fight_param
	if winorlose == 1:
		FightResult(gteam1, 1, gteam2, -1, groupId)
	elif winorlose == -1:
		FightResult(gteam1, -1, gteam2, 1, groupId)
	else:
		#根据战队积分，谁高谁赢
		if gteam1.teamPoint > gteam2.teamPoint:
			FightResult(gteam1, 1, gteam2, -1, groupId)
		elif gteam1.teamPoint < gteam2.teamPoint:
			FightResult(gteam1, -1, gteam2, 1, groupId)
		else:
			if gteam1.totalZDL > gteam2.totalZDL:
				FightResult(gteam1, 1, gteam2, -1, groupId)
			else:
				#不考虑总战力相等的情况
				FightResult(gteam1, -1, gteam2, 1, groupId)
	#获取观战数据
	JTFightViewData = fightObj.GetViewData()
	SaveFightViewData(JTFightViewData, gteam1, gteam2)
	
def SaveFightViewData(JTFightViewData, gteam1, gteam2):
	global FinalStep
	global FinalFightRound
#	global NJT_Fiht_ViewData
	global Fight_View_Data
	
#	if not NJT_Fiht_ViewData.returnDB:
#		return
	
	if FinalStep not in [32,16,8,4]:
		print "GE_EXC,JTZBFinal AfterTeamFight FinalStep(%s) is Wrong!" % FinalStep
		#步数有问题就取战队1的步数
		FinalStep = gteam1.finalGrade
	#获取战队所在的战区
	groupId = gteam1.groupId
#	FightViewData = NJT_Fiht_ViewData.GetValue(groupId).get("FightViewData", {})
#	if FinalStep not in FightViewData:
#		FightViewData[FinalStep] = {} 
#	viewdata = FightViewData[FinalStep]
	teamId1, teamId2 = gteam1.teamId, gteam2.teamId
	teamData1 = (gteam1.teamName, gteam1.processName, gteam1.teamPoint)
	teamData2 = (gteam2.teamName, gteam2.processName, gteam2.teamPoint)
	packData = [(teamData1, teamData2), JTFightViewData]
#	viewdata[(teamId1, teamId2, FinalFightRound)] = packData
#	NJT_Fiht_ViewData.SetKeyValue(groupId, {"group_index":groupId, "FightViewData":FightViewData})
	#缓存
	if groupId not in Fight_View_Data:
		Fight_View_Data[groupId] = {}
	group_viewdata = Fight_View_Data[groupId]
	if FinalStep not in group_viewdata:
		group_viewdata[FinalStep] = {}
	temp_viewdata = group_viewdata[FinalStep]
	temp_viewdata[(teamId1, teamId2, FinalFightRound)] = packData
	
def FightResult(gteam1, winorlose1, gteam2, winorlose2, groupId):
	#处理战斗结果
	if winorlose1 == -1 and winorlose2 == -1:
		#根据战队积分，谁高谁赢
		if gteam1.teamPoint > gteam2.teamPoint:
			winorlose1 = 1
		elif gteam1.teamPoint < gteam2.teamPoint:
			winorlose2 = 1
		else:
			if gteam1.totalZDL > gteam2.totalZDL:
				winorlose1 = 1
			else:
				#不考虑总战力相等的情况
				winorlose2 = 1
			
	if winorlose1 == 1:
		gteam1.Win()
		gteam2.Lose()
		SetFianlFightResult(gteam1.teamName, gteam2.teamName, 1, groupId)
	else:
		gteam1.Lose()
		gteam2.Win()
		SetFianlFightResult(gteam1.teamName, gteam2.teamName, -1, groupId)
		
def SetFianlFightResult(teamName1, teamName2, result, groupId):
	#设置战斗结果
	global Final_Fight_Result
	global FinalFightRound
	if groupId not in Final_Fight_Result:
		Final_Fight_Result[groupId] = {}
	groupData = Final_Fight_Result[groupId]
	if FinalFightRound not in groupData:
		groupData[FinalFightRound] = []
	resultList = groupData[FinalFightRound]
	resultList.append((teamName1, teamName2, result))
	
	
def InitFinal(rankDict):
	#根据小组赛发过来的数据，生成各战区32强数据
	
	global NJT_Final_Dict
	for groupId, rankList in rankDict.iteritems():
		selectRank = copy.deepcopy(rankList[:32])
		selecelList = []
		for rankdata in selectRank:
			#teamId,teamName,processName,processID,point,teamPoint,teamGrade,totalZdl,winCnt,loseCnt,memberIds,rank,teamData
			teamId,teamName,processName,processID,_,teamPoint,teamGrade,totalZdl,_,_,memberIds,rank,teamData = rankdata
			#队伍ID, 队伍名，服名，服ID，战队积分，战队段位，总战斗力，成员IDs, 总排名, 队员信息, index
			#新增参数，设置该战队的步骤，设置为32，表示该战队为32强，可以参加32->16比赛
			selecelList.append([teamId, teamName, processName, processID, teamPoint, teamGrade, totalZdl, memberIds, rank, teamData, 32])
		NJT_Final_Dict[groupId] = selecelList
	NJT_Final_Dict[4] = {}
	NJT_Final_Dict.changeFlag = True
	with Tra_InitNZB32Data:
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveNZB32Data, NJT_Final_Dict)
	#清空观战数据
	if 1 in NJT_Fiht_ViewData.datas:
		NJT_Fiht_ViewData.SetKeyValue(1, {"group_index":1, "FightViewData":{}})
	if 2 in NJT_Fiht_ViewData.datas:
		NJT_Fiht_ViewData.SetKeyValue(2, {"group_index":2, "FightViewData":{}})
	if 3 in NJT_Fiht_ViewData.datas:
		NJT_Fiht_ViewData.SetKeyValue(3, {"group_index":3, "FightViewData":{}})
		
	SyncFinalToLogic(0, True, False)
	
def SyncFinalToLogic(processId = 0, mail = False, end = False):
	#同步总决赛数据到逻辑进程
	global NJT_Final_Dict
	Call.ServerCall(processId, "Game.JT.JTLogicZB", "ReceiveFinalData", (NJT_Final_Dict.data, mail, end))

def UpdataFinalData(param):
	#逻辑进程请求决赛数据
	processId = param
	SyncFinalToLogic(processId)
	
def SynZBFinalViweData(processId = 0):
	#同步观战数据到逻辑进程
	#global NJT_Fiht_ViewData
	#fightViewData = {}
	#for index, data in NJT_Fiht_ViewData.datas.iteritems():
	#	fightViewData[index] = data.get("FightViewData", {})
	#Call.SuperServerCall(processId, "Game.JT.JTLogicZB", "ReceiveFinalFightData", fightViewData)
	global Fight_View_Data
	if not Fight_View_Data:
		return
	Call.SuperServerCall(processId, "Game.JT.JTLogicZB", "ReceiveFinalFightData", Fight_View_Data)
	
def UpdataZBFinalViweData(param):
	#逻辑进程请求观战数据
	processId = param
	SynZBFinalViweData(processId)
	
def SynStatueData(processId = 0):
	#同步雕像数据
	global NJT_Statue_Data
	Call.ServerCall(processId, "Game.JT.JTLogicZB", "ReceiveFinalStatueData", NJT_Statue_Data.data)
	
def UpdataStatueData(param):
	#逻辑进程请求雕像数据
	processId = param
	SynStatueData(processId)
##########################################################################
#玩家进入跨服
##########################################################################
def AfterJoinFinal(role, param):
	global IsFinalStart, FinalStep
	global FinalTeamDict
	if IsFinalStart is False or not FinalStep:
		role.GotoLocalServer(None, None)
		return
	teamId, groupIndex = param
	
	groupTeams = FinalTeamDict.get(groupIndex)
	if not groupTeams:
		print "GE_EXC,JTZBFinal AfterJoinFinal not this groupteams (%s)" % groupIndex
		role.GotoLocalServer(None, None)
		return
	gteam = groupTeams.get(teamId)
	if not gteam:
		print "GE_EXC,JTZBFinal AfterJoinGroup not gteam (%s) (%s)" % (groupIndex, teamId)
		role.GotoLocalServer(None, None)
		return
	gteam.JoinRole(role)
	
	UpdataFinalRoleData(role, gteam.processName)
	
def UpdataFinalRoleData(role, processName):
	#更新雕像数据
	global NJT_Final_Role
	viewData = {}
	viewData[1] = role.GetRoleID()
	viewData[2] = role.GetRoleName()						#名字
	viewData[3] = role.GetSex()							#性别
	viewData[4] = role.GetCareer()						#职业
	viewData[5] = role.GetGrade()						#进阶
	viewData[6] = role.GetObj(EnumObj.Title).get(2, [])#角色称号
	viewData[7] = role.GetWingID()						#翅膀ID
	viewData[8] = role.GetTI64(EnumTempInt64.FashionClothes)#时装衣服
	viewData[9] = role.GetTI64(EnumTempInt64.FashionHat)#时装帽子
	viewData[10] = role.GetTI64(EnumTempInt64.FashionWeapons)#时装武器
	viewData[11] = role.GetI1(EnumInt1.FashionViewState)#时装显示状态
	viewData[12] = role.GetZDL()						#玩家战斗力
	viewData[13] = processName							#服名
	viewData[14] = role.GetI16(EnumInt16.WarStationStarNum)#战阵
	viewData[15] = role.GetI16(EnumInt16.StationSoulId)	#阵灵
	
	NJT_Final_Role[role.GetRoleID()] = viewData
	
def OnRoleExit(role, param):
	fteam = role.GetTempObj(EnumTempObj.CrossJTFinalTeam)
	if not fteam: return
	fteam.LeaveRole(role)

def ClientLost(role, param):
	fteam = role.GetTempObj(EnumTempObj.CrossJTFinalTeam)
	if not fteam : return
	fteam.LeaveRole(role)
#==================================================================
def AfterLoadJTFinal():
	global NJT_Final_Dict
	if 1 not in NJT_Final_Dict:#初级战区
		NJT_Final_Dict[1] = {}
	if 2 not in NJT_Final_Dict:#精锐战区
		NJT_Final_Dict[2] = {}
	if 3 not in NJT_Final_Dict:#巅峰战区
		NJT_Final_Dict[3] = {}
	if 4 not in NJT_Final_Dict:#记录3个战区的前3
		NJT_Final_Dict[4] = {}
	num = JTDefine.GetZBStartFlagNum()
	if num in (2,3,4):
		SyncFinalToLogic()
		
def AfterLoad():
	global NJT_Fiht_ViewData
	if 1 not in NJT_Fiht_ViewData.datas:
		NJT_Fiht_ViewData.SetKeyValue(1, {"group_index":1, "FightViewData":{}})
	if 2 not in NJT_Fiht_ViewData.datas:
		NJT_Fiht_ViewData.SetKeyValue(2, {"group_index":2, "FightViewData":{}})
	if 3 not in NJT_Fiht_ViewData.datas:
		NJT_Fiht_ViewData.SetKeyValue(3, {"group_index":3, "FightViewData":{}})
	
def AfterLoadJTStatueData():
	SynStatueData()

def AfterLoadFinalRole():
	pass
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.EnvIsQQ() or Environment.IsDevelop or Environment.EnvIsFT()) and Environment.IsCross:
		if cProcess.ProcessID == Define.GetDefaultCrossID():
			#初级战区，精锐战区， 巅峰战区
			NJT_Final_Dict = Contain.Dict("NJT_Final_Dict", (2038, 1, 1), AfterLoadJTFinal)
			#存观战数据{战区:{32进16:{(teamId1,teamId2,ground):观战数据}}
			#这个持久化数据已经不用了，观战数据改为缓存了
			NJT_Fiht_ViewData = BigTable.BigTable("njt_fight_viewdata", 100, AfterLoad)
			#雕像数据
			NJT_Statue_Data = Contain.Dict("NJT_Statue_Data", (2038, 1, 1), AfterLoadJTStatueData)
			#存玩家外观数据
			NJT_Final_Role = Contain.Dict("NJT_Final_Role", (2038, 1, 1), AfterLoadFinalRole)
			#32-16，8-4，4-1
			Cron.CronDriveByMinute((2038, 1, 1), ReadyFinalFight1, H="H == 21", M="M == 50")
			#16-8
			Cron.CronDriveByMinute((2038, 1, 1), ReadyFinalFight2, H="H == 22", M="M == 24")
			
			Event.RegEvent(Event.Eve_BeforeExit, OnRoleExit)
			Event.RegEvent(Event.Eve_ClientLost, ClientLost)
		