#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.JT.JTeam")
#===============================================================================
# 跨服组队 战队系统
#===============================================================================
import cProcess
import cRoleMgr
import cDateTime
import cComplexServer
import Environment
from World import Define
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from ComplexServer import Init
from ComplexServer.Log import AutoLog
from Game.Persistence import Contain
from Game.JT import JTDefine, JTEnum, JTCross, JTConfig
from Game.Role import Call, Event, Status
from Game.GlobalData import ZoneName
from Game.SysData import WorldData
from Game.Role.Data import EnumTempInt64, EnumInt1, EnumInt64, EnumCD
from Game.Activity.Title import Title
from Game.Role.Mail import Mail


if "_HasLoad" not in dir():
	IsStart = False
	#战队缓存对象
	JJT_Obj_Dict = {}
	#战队名字集合
	JTeamNameSet = set()
	#战队排名levelIndex --> rankList
	JTeamRankLevelDict = {}
	JTeamRankLevelSyncDict = {}
	
	JT_S_TeamData = AutoMessage.AllotMessage("JT_S_TeamData", "同步战队数据")
	JT_S_Invite = AutoMessage.AllotMessage("JT_S_Invite", "同步战队邀请加入")
	JT_S_RequestJoin = AutoMessage.AllotMessage("JT_S_RequestJoin", "同步有人请求加入队伍")
	JT_S_AcceptRefuse = AutoMessage.AllotMessage("JT_S_AcceptRefuse", "同步拒绝申请加入队伍")
	JT_S_TeamScore = AutoMessage.AllotMessage("JT_S_TeamScore", "同步战队积分和自己的积分")
	JT_S_RewardGrade = AutoMessage.AllotMessage("JT_S_RewardGrade", "同步可以领取的战队奖励段位")
	
	JT_S_InviteToCross = AutoMessage.AllotMessage("JT_S_InviteToCross", "同步有人邀请进入跨服组队竞技")
	JT_S_OtherTeamStart = AutoMessage.AllotMessage("JT_S_OtherTeamStart", "开始同步其他战队信息")
	JT_S_OtherTeamData = AutoMessage.AllotMessage("JT_S_OtherTeamData", "同步其他战队信息")
	#日志
	Tra_JS_CreateTeam = AutoLog.AutoTransaction("Tra_JS_CreateTeam", "创建战队")
	Tra_JS_JoinTeam = AutoLog.AutoTransaction("Tra_JS_JoinTeam", "加入战队")
	Tra_JS_LeaveTeam = AutoLog.AutoTransaction("Tra_JS_LeaveTeam", "离开战队")
	Tra_JS_KickTeam = AutoLog.AutoTransaction("Tra_JS_KickTeam", "被踢出战队")
	Tra_JS_DismissTeam = AutoLog.AutoTransaction("Tra_JS_DismissTeam", "解散战队")
	Tra_JS_ChangeTeam = AutoLog.AutoTransaction("Tra_JS_ChangeTeam", "修改战队信息")
	Tra_JS_LoginRevert = AutoLog.AutoTransaction("Tra_JS_LoginRevert", "战队登录修复")
	
	Tra_JS_DayReward = AutoLog.AutoTransaction("Tra_JS_DayReward", "组队竞技场日结奖励")
	Tra_JS_DayRewardData = AutoLog.AutoTransaction("Tra_JS_DayRewardData", "组队竞技场日结系统记录")
	
	Tra_JS_WeekReward = AutoLog.AutoTransaction("Tra_JS_WeekReward", "组队竞技场周结奖励")
	Tra_JS_WeekRewardData = AutoLog.AutoTransaction("Tra_JS_WeekRewardData", "组队竞技场周结系统记录")
	
	Tra_JS_NeiWangRevert = AutoLog.AutoTransaction("Tra_JS_NeiWangRevert", "内网修复战队ID")
	
	Tra_NJTZB_Mail = AutoLog.AutoTransaction("Tra_NJTZB_Mail", "新版跨服争霸晋级邮件")
	
def WorldLevelEnough():
	#世界等级是否足够
	return WorldData.GetWorldLevel() >= JTDefine.JTNeedWorldLevel

def IsJTeamCanDo():
	#是否可以操作战队
	global IsStart
	if IsStart is True:
		return False
	#0 - 6点不能操作战队
	return cDateTime.Hour() >= 6

def GetJTObj(role):
	'''获取战队对象(本服逻辑进程专用)'''
	teamId = role.GetJTeamID()
	if not teamId:
		return None
	return GetTeamObj(teamId)

def GetJTeamScore(role):
	'''获取战队积分'''
	jtobj = role.GetJTObj()
	if not jtobj:
		return 0
	return jtobj.teamScore

def GetTeamObj(teamId):
	#获取战队对象
	global JJT_Obj_Dict
	return JJT_Obj_Dict.get(teamId)

#战队类
class JTTeamBase(object):
	def __init__(self, teamId, teamData = None, role = None, teamName = "", teamFlag = 0):
		self.teamId = teamId
		if teamData is None:
			#创建新战队
			self.CreateNewJTeam(role, teamName, teamFlag)
		else:
			#数据库数据解包
			self.teamName = teamData.get(JTEnum.JTE_TeamName)
			self.teamFlag = teamData.get(JTEnum.JTE_TeamFlag)
			self.leaderId = teamData.get(JTEnum.JTE_TeamLeaderID)
			self.leaderName = teamData.get(JTEnum.JTE_TeamLeaderName)
			self.teamScore = teamData.get(JTEnum.JTE_TeamScore)
			self.teamGrade = teamData.get(JTEnum.JTE_TeamGrade)
			self.teamRank = teamData.get(JTEnum.JTE_TeamRank)
			self.teamOldRank = teamData.get(JTEnum.JTE_TeamOldRank)
			self.teamWinCount = teamData.get(JTEnum.JTE_TeamWinCount)
			self.teamLoseCount = teamData.get(JTEnum.JTE_TeamLoseCount)
			self.members = teamData.get(JTEnum.JTE_TeamMemberDict)
			self.teamMaxScore = teamData.get(JTEnum.JTE_TeamMaxScore)
			self.teamMaxGrade = teamData.get(JTEnum.JTE_TeamMaxGrade)
			self.teamDayFightCount = teamData.get(JTEnum.JTE_TeamDayFightCount, 0)
			self.teamWeekCount = teamData.get(JTEnum.JTE_TeamWeekCount, 0)
			self.ZBData = teamData.get(JTEnum.JTE_ZBData, [])
		
		self.teamLevelIndex = 0
		
		global JTeamNameSet
		JTeamNameSet.add(self.teamName)
		
		self.applyJoinSet = set()
		self.inviteRoleIds = set()
		
		self.needUpgrade = False
		
	def CreateNewJTeam(self, role, teamName, teamFlag):
		#创建战队，初始化数据
		self.teamName = teamName
		self.teamFlag = teamFlag
		self.leaderId = role.GetRoleID()
		self.leaderName = role.GetRoleName()
		self.teamScore = JTDefine.DefaultJTScore
		self.teamGrade = 0
		self.teamRank = JTDefine.MaxRank + 1
		self.teamOldRank = JTDefine.MaxRank + 1
		self.teamWinCount = 0
		self.teamLoseCount = 0
		self.members = {}
		self.teamMaxScore = JTDefine.DefaultJTScore
		self.teamMaxGrade = 0
		self.teamDayFightCount = 0
		self.teamWeekCount = 0
		self.ZBData = []
		
		role.SetJTeamID(self.teamId)
		#更新自己的信息
		self.UpdataMemberData(role)
		self.UpdateSave()
	
	def IsLeader(self, role):
		return role.GetRoleID() == self.leaderId
	
	def CanJoinCross(self):
		#战队需要有3个人才能过去
		return len(self.members) == 3
	
	def IsLock(self):
		return False
	
	def GetJTeamTitleID(self):
		if not self.teamGrade:
			return 0
		gradeConfig = JTConfig.JTGradeDict.get(self.teamGrade)
		if gradeConfig:
			return gradeConfig.titleId
		return 0
	##############################################################################
	#基本操作
	##############################################################################
	
	def RequestJoin(self, role):
		#请求加入队伍
		roleId = role.GetRoleID()
		if roleId in self.applyJoinSet:
			role.Msg(2, 0, GlobalPrompt.JT_Tips_9)
			return False
		leader = cRoleMgr.FindRoleByRoleID(self.leaderId)
		if not leader:
			role.Msg(2, 0, GlobalPrompt.JT_Tips_11)
			return False
		self.applyJoinSet.add(roleId)
		leader.SendObj(JT_S_RequestJoin, (roleId, role.GetRoleName(), role.GetZDL()))
		return True
	
	def AcceptJoin(self, leader, roleId, actype):
		#处理申请
		if roleId not in self.applyJoinSet:
			return
		self.applyJoinSet.discard(roleId)
		role = cRoleMgr.FindRoleByRoleID(roleId)
		if not role:
			leader.Msg(2, 0, GlobalPrompt.JT_Tips_12)
			return
		if role.GetJTeamID():
			leader.Msg(2, 0, GlobalPrompt.JT_Tips_8)
			return
		ftid = role.GetI64(EnumInt64.JTFightTeamID)
		if ftid and ftid != self.teamId:
			leader.Msg(2, 0, GlobalPrompt.JT_Tips_17)
			return
		if actype == 1:
			self.Join(role)
			self.SyncTeamToRole(leader)
		else:
			#被拒绝了
			role.SendObj(JT_S_AcceptRefuse, self.teamId)
	
	def Join(self, role):
		with Tra_JS_JoinTeam:
			#加入队伍
			role.SetJTeamID(self.teamId)
			self.UpdataMemberData(role)
			#更新保存
			self.UpdateSave()
			self.SyncTeamToRole(role)
			#战队段位称号
			titleId = self.GetJTeamTitleID()
			if titleId:
				Title.AddTitle(role.GetRoleID(), titleId)
	
	def Leave(self, role):
		#离开队伍
		with Tra_JS_LeaveTeam:
			roleId = role.GetRoleID()
			oldData = self.members.get(roleId)
			if oldData:
				del self.members[roleId]
				#更新保存
				self.UpdateSave()
			#清理自己的数据
			ClearJTeamData(role, self.GetJTeamTitleID())
			#没人了，解散战队
			if len(self.members) <= 0:
				self.Dismiss(role)
			else:
				if self.leaderId == roleId:
					self.ChangeLeader(None, self.members.keys()[0])
	
	def Kick(self, leader, roleId):
		with Tra_JS_KickTeam:
			#被踢了
			oldData = self.members.get(roleId)
			if not oldData:
				return
			del self.members[roleId]
			#更新保存
			self.UpdateSave()
			self.SyncTeamToRole(leader)
			#同步到这个被踢的人
			Call.LocalDBCall(roleId, BeKickNew, self.GetJTeamTitleID())
			Mail.SendMail(roleId, GlobalPrompt.JTKickTitle, GlobalPrompt.Sender, GlobalPrompt.JTKickContent % leader.GetRoleName())
			
	def InviteRole(self, role, inviterole):
		#不要判断重复邀请，这个只用于邀请返回的时候判断一下有没有被邀请过
		self.inviteRoleIds.add(inviterole.GetRoleID())
		inviterole.SendObj(JT_S_Invite, (self.teamId, self.teamName, role.GetRoleName()))
	
	def Dismiss(self, role):
		with Tra_JS_DismissTeam:
			#解散队伍
			titleId = self.GetJTeamTitleID()
			for memberId in self.members.keys():
				Call.LocalDBCall(memberId, DissmissCallNew, titleId)
			#更新和清理数据
			global JJT_Obj_Dict
			del JJT_Obj_Dict[self.teamId]
			#解散了 
			self.UpdateSave(True)
			AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveJTDismiss, self.teamId)
	
	def ChangeLeader(self, role, newLeaderId):
		#转让队长
		newleaderdata = self.members.get(newLeaderId)
		if not newleaderdata:
			return
		self.leaderId = newLeaderId
		self.leaderName =newleaderdata[0] 
		self.UpdateSave()
		self.SyncTeamToRole(role)
		self.applyJoinSet = set()
		newLeader = cRoleMgr.FindRoleByRoleID(newLeaderId)
		if newLeader:
			self.SyncTeamToRole(newLeader)
		if role:
			role.Msg(2, 0, GlobalPrompt.JT_Tips_1)
	
	def ChangeInfo(self, role, teamName, teamFlag):
		#改变资料
		self.teamFlag = teamFlag
		self.teamName = teamName
		self.UpdateSave()
		self.SyncTeamToRole(role)
		role.Msg(2, 0, GlobalPrompt.JT_ChangeInfo)
	
	##############################################################################
	def Save(self):
		JT_TeamDict[self.teamId] = self.GetSaveData()
	
	def UpdateSave(self, isdismiss = False, needSyncToCross = True):
		#更新和保存这个队伍信息到持久化字典
		global JT_TeamDict
		if isdismiss:
			del JT_TeamDict[self.teamId]
		else:
			self.Save()
		if self.teamRank > JTDefine.MaxRank:
			#不在排行榜内，不更新到跨服进程
			return
		if isdismiss:
			#解散，删除队伍
			Call.ServerCall(Define.GetDefaultCrossID(), "Game.JT.JTCross", "LoginChangeJTinfo", (self.teamId, None))
		elif needSyncToCross is True:
			Call.ServerCall(Define.GetDefaultCrossID(), "Game.JT.JTCross", "LoginChangeJTinfo", (self.teamId, self.GetRankSyncData()))
	
	def UpdateByCrossInfo(self, info):
		#跨服活动结束了，把参与的战队数据同步回来，更新本地数据
		teamScore, winCount, loseCount, fightTimes = info
		if teamScore != self.teamScore:
			self.needUpgrade = True
		self.teamScore = teamScore
		self.teamWinCount = winCount
		self.teamLoseCount = loseCount
		self.teamDayFightCount += fightTimes
		self.teamMaxScore = max(self.teamMaxScore, self.teamScore)
		#不需要再同步回去跨服了
		self.UpdateSave(needSyncToCross = False)
	
	def UpdataByRank(self, levelIndex, teamGrade, rank):
		#根据排名更新数据
		self.teamLevelIndex = levelIndex
		if teamGrade != self.teamGrade:
			self.UpdataMemberGradeTitle(teamGrade)
		self.teamGrade = teamGrade
		self.teamMaxGrade = max(self.teamMaxGrade, self.teamGrade)
		self.teamRank = rank
		self.UpdateSave(needSyncToCross = False)
		self.needUpgrade = False
	
	def UpdataNotInRank(self):
		if self.needUpgrade is False:
			#没有去参加活动，或者在排行榜上面，已经更新过数据了
			return
		#参加了活动，但是不在榜上，需要单独更新段位和排名
		self.teamRank = JTDefine.MaxRank + 1
		teamGrade = JTConfig.GetLoginGrade(self.teamScore)
		if teamGrade != self.teamGrade:
			self.UpdataMemberGradeTitle(teamGrade)
		self.teamGrade = teamGrade
		self.teamMaxGrade = max(self.teamMaxGrade, self.teamGrade)
		self.UpdateSave(needSyncToCross = False)
		self.needUpgrade = False
	
	
	def UpdataMemberGradeTitle(self, nowGrade):
		#titleId = self.GetJTeamTitleID()
		self.teamGrade = nowGrade
		newTitleId = self.GetJTeamTitleID()
		for roleId in self.members.keys():
			#if titleId:
			#	Title.DeleteTitleCall(roleId, titleId)
			Title.DeleteJTeamTitleCall(roleId)
			if newTitleId:
				Title.AddTitle(roleId, newTitleId)

	
	def UpdataMemberData(self, role):
		#更新自己的数据 @members
		self.members[role.GetRoleID()] = [role.GetRoleName(),\
										role.GetSex(), \
										role.GetGrade(), \
										role.GetCareer(), \
										role.GetWingID(),\
										role.GetLevel(), \
										role.GetZDL(), \
										role.GetTI64(EnumTempInt64.FashionClothes),\
										role.GetTI64(EnumTempInt64.FashionHat),\
										role.GetTI64(EnumTempInt64.FashionWeapons),\
										role.GetI1(EnumInt1.FashionViewState)]

	#--------------------------------------------------------------------------------
	
	def SyncTeamToRole(self, role):
		if not role:
			return
		#把队伍信息同步给角色
		role.SendObj(JT_S_TeamData, self.GetSyncData())
	
	def GetZDLAvg(self):
		#获取平均战斗力
		membercnt = len(self.members)
		if membercnt <= 0 : return 0
		zdl = 0
		for md in self.members.itervalues():
			zdl += md[6]
		return zdl / membercnt
	
	def GetSaveData(self):
		return {JTEnum.JTE_TeamID:self.teamId,\
						JTEnum.JTE_TeamName : self.teamName,\
						JTEnum.JTE_TeamFlag : self.teamFlag,\
						JTEnum.JTE_TeamLeaderID : self.leaderId,\
						JTEnum.JTE_TeamLeaderName : self.leaderName,\
						JTEnum.JTE_TeamScore : self.teamScore,\
						JTEnum.JTE_TeamGrade : self.teamGrade,\
						JTEnum.JTE_TeamRank : self.teamRank,\
						JTEnum.JTE_TeamOldRank : self.teamOldRank,\
						JTEnum.JTE_TeamWinCount : self.teamWinCount,\
						JTEnum.JTE_TeamLoseCount : self.teamLoseCount,\
						JTEnum.JTE_TeamMemberDict : self.members,\
						JTEnum.JTE_TeamMaxScore : self.teamMaxScore,\
						JTEnum.JTE_TeamMaxGrade : self.teamMaxGrade,\
						JTEnum.JTE_TeamDayFightCount : self.teamDayFightCount,\
						JTEnum.JTE_TeamWeekCount : self.teamWeekCount,\
						JTEnum.JTE_ZBData: self.ZBData
						}
	
	def GetSycnListData(self):
		#获取本服可以加入的战队列表时返回的数据
		return (self.teamId, \
				self.teamName, \
				self.leaderId, \
				self.teamScore, \
				self.GetZDLAvg(), \
				len(self.members), \
				self.leaderName)
	
	def GetSyncData(self):
		#获取同步给客户端的数据
		return (self.teamId, \
				self.teamName, \
				self.teamFlag, \
				self.leaderId, \
				self.leaderName, \
				self.teamScore, \
				self.teamGrade,\
				self.teamRank,\
				self.teamOldRank,\
				self.teamWinCount,\
				self.teamLoseCount,\
				self.teamMaxScore,\
				self.teamMaxGrade,\
				self.teamDayFightCount,\
				self.members)

	def GetRankSyncData(self):
		#获取用于排行榜更新的数据
		return (self.teamName, self.GetMemberRankData())
	
	def GetMemberRankData(self):
		#name, level, zdl
		return [(memberData[0], memberData[5], memberData[6], roleId) for roleId, memberData in self.members.iteritems()]
			
	def GetCrossNeedData(self):
		#获取进入跨服时候需要的数据
		return (cProcess.ProcessID, \
				ZoneName.ZoneName, \
				self.teamId, \
				self.teamName, \
				self.teamFlag, \
				self.teamScore, \
				self.teamGrade,\
				self.leaderId, \
				self.leaderName,\
				self.teamWinCount,\
				self.teamLoseCount,\
				self.teamRank, \
				self.members.keys(),\
				self.teamMaxScore,\
				self.teamMaxGrade,\
				self.GetMemberRankData())
	
	def SetGroupIndex(self, groupId, value):
		if self.ZBData:
			#已有数据
			old_groupId, oldValue = self.ZBData
			if old_groupId != groupId:
				print "GE_EXC,JTeam.SetGroupIndex old_groupId(%s) != groupId(%s)" % (old_groupId, groupId)
				return
			if oldValue <= value:
				return
		self.ZBData = (groupId, value)
		self.UpdateSave()
		#给玩家发邮件
		with Tra_NJTZB_Mail:
			if value == 100:
				#拥有参数资格
				for roleId in self.members.keys():
					Mail.SendMail(roleId, GlobalPrompt.JT_100Title, GlobalPrompt.JT_100Sender, GlobalPrompt.JT_100Content % (GlobalPrompt.ReturnJTZhanqu(groupId)))
			elif value == 32:
				#32强
				for roleId in self.members.keys():
					Mail.SendMail(roleId, GlobalPrompt.JT_32Title, GlobalPrompt.JT_32Sender, GlobalPrompt.JT_32Content % (GlobalPrompt.ReturnJTZhanqu(groupId)))
			elif value == 16:
				for roleId in self.members.keys():
					Mail.SendMail(roleId, GlobalPrompt.JT_16Title, GlobalPrompt.JT_16Sender, GlobalPrompt.JT_16Content % (GlobalPrompt.ReturnJTZhanqu(groupId)))
			elif value == 8:
				for roleId in self.members.keys():
					Mail.SendMail(roleId, GlobalPrompt.JT_8Title, GlobalPrompt.JT_8Sender, GlobalPrompt.JT_8Content % (GlobalPrompt.ReturnJTZhanqu(groupId)))
			elif value == 4:
				for roleId in self.members.keys():
					Mail.SendMail(roleId, GlobalPrompt.JT_4Title, GlobalPrompt.JT_4Sender, GlobalPrompt.JT_4Content % (GlobalPrompt.ReturnJTZhanqu(groupId)))
			
	def GetGroupIndex(self):
		return self.ZBData
	
	def ClearZBData(self):
		self.ZBData = []
		
############################################################################################
def ClearJTeamData(role, titleId):
	#清理个人战队数据
	role.SetJTeamID(0)
	if titleId:
		#清理战队称号
		Title.DeleteTitle(role, titleId)
	elif titleId == -1:
		#强制清除所有的战队称号
		Title.DeleteJTeamTitle(role, None)


def GetCanJoinTeamData():
	#获取可以加入的战队列表
	canjoindict = []
	CA = canjoindict.append
	for jtobj in JJT_Obj_Dict.itervalues():
		if len(jtobj.members) >= 3:
			continue
		CA(jtobj.GetSycnListData())
	return canjoindict

############################################################################################
#旧离线命令,不能删除
def BeKick(role, param):
	with Tra_JS_KickTeam:
		ClearJTeamData(role, None)

def DissmissCall(role, param):
	with Tra_JS_DismissTeam:
		ClearJTeamData(role, None)
		
#新离线命令
def BeKickNew(role, param):
	with Tra_JS_KickTeam:
		ClearJTeamData(role, param)

def DissmissCallNew(role, param):
	with Tra_JS_DismissTeam:
		ClearJTeamData(role, param)

############################################################################################
def OpenJTeamPanel(role, msg):
	'''
	打开战队面板
	@param role:
	@param msg:
	'''
	if role.GetLevel() < JTDefine.JTNeedLevel:
		return
	backId, _ = msg
	teamId = role.GetJTeamID()
	LoginSyncData(role, None)
	if not teamId:
		role.CallBackFunction(backId, None)
		return
	jtobj = GetTeamObj(teamId)
	if jtobj:
		#有自己的战队,只看到自己战队的信息
		role.CallBackFunction(backId, jtobj.GetSyncData())
		return
	
	if Environment.IsDevelop or cProcess.ProcessID in Define.TestWorldIDs:
		with Tra_JS_NeiWangRevert:
			ClearJTeamData(role, -1)
	else:
		print "GE_EXC, error in OpenJTeamPanel not teamobj (%s)" % teamId

def CreateJTeam(role, msg):
	'''
	创建战队
	@param role:
	@param msg:
	'''
	if role.GetJTeamID():
		return
	if role.GetI64(EnumInt64.JTFightTeamID):
		role.Msg(2, 0, GlobalPrompt.JT_Tips_16)
		return
	if role.GetLevel() < JTDefine.JTNeedLevel:
		return
	if not WorldLevelEnough():
		role.Msg(2, 0, GlobalPrompt.JT_WorldLevel)
		return 
	if role.GetRMB() < JTDefine.CreateJTeamNeedRMB:
		return
	if not role.IsLocalServer():
		return
	teamName, teamFlag = msg
	if teamFlag < 1 or teamFlag > JTDefine.MaxTeamFlag:
		return
	if  not teamName or len(teamName) > 24:
		return
	global JTeamNameSet
	if teamName in JTeamNameSet:
		#名字重复
		role.Msg(2, 0, GlobalPrompt.JT_SameName)
		return
	
	with Tra_JS_CreateTeam:
		JTeamNameSet.add(teamName)
		#扣钱
		role.DecRMB(JTDefine.CreateJTeamNeedRMB)
		#分配一个队伍ID
		teamId = cProcess.AllotGUID64()
		#创建
		jtt = JTTeamBase(teamId, None, role, teamName, teamFlag)
		#缓存
		global JJT_Obj_Dict
		JJT_Obj_Dict[teamId] = jtt
		#同步给客户端
		jtt.SyncTeamToRole(role)

def RequestJoinJTeam(role, msg):
	'''
	请求加入战队
	@param role:
	@param msg:
	'''
	if role.GetJTeamID():
		return
	if role.GetLevel() < JTDefine.JTNeedLevel:
		return
	if not role.IsLocalServer():
		return
	
	if not IsJTeamCanDo():
		role.Msg(2, 0, GlobalPrompt.JT_CanNotDo)
		return
	
	backId, teamId = msg
	ftid = role.GetI64(EnumInt64.JTFightTeamID)
	if ftid and ftid != teamId:
		role.Msg(2, 0, GlobalPrompt.JT_Tips_16)
		return
	
	jtobj = GetTeamObj(teamId)
	if not jtobj:
		return
	if jtobj.IsLock():
		role.Msg(2, 0, GlobalPrompt.JT_CanNotDo)
		return
	if len(jtobj.members) >= 3:
		role.Msg(2, 0, GlobalPrompt.JT_Team_Full)
		return
	
	if jtobj.RequestJoin(role) is True:
		role.CallBackFunction(backId, teamId)

def AcceptJoin(role, msg):
	'''
	处理申请加入队伍的请求
	@param role:
	@param msg:
	'''
	backid, (actype, roleId) = msg
	
	teamId = role.GetJTeamID()
	jtobj = GetTeamObj(teamId)
	if not jtobj:
		return
	if not jtobj.IsLeader(role):
		return
	if len(jtobj.members) >= 3:
		role.Msg(2, 0, GlobalPrompt.JT_Team_Full)
		return
	if not IsJTeamCanDo():
		role.Msg(2, 0, GlobalPrompt.JT_CanNotDo)
		return
	if jtobj.IsLock():
		role.Msg(2, 0, GlobalPrompt.JT_CanNotDo)
		return
	jtobj.AcceptJoin(role, roleId, actype)
	role.CallBackFunction(backid, None)

def LeaveJTeam(role, msg):
	'''
	离开战队
	@param role:
	@param msg:
	'''
	teamId = role.GetJTeamID()
	if not teamId:
		return
	jtobj = GetTeamObj(teamId)
	if not jtobj:
		print "GE_EXC, leave team not obj"
		return
	if role.GetRoleID() not in jtobj.members:
		return
	if not IsJTeamCanDo():
		role.Msg(2, 0, GlobalPrompt.JT_CanNotDo)
		return
	if jtobj.IsLock():
		role.Msg(2, 0, GlobalPrompt.JT_CanNotDo)
		return
	if JTDefine.GetZBStartFlagNum() in [1,2,3,4]:
		role.Msg(2, 0, GlobalPrompt.JT_CanNotDo)
		return
	jtobj.Leave(role)
def KickMember(role, msg):
	'''
	踢掉战队成员
	@param role:
	@param msg:
	'''
	memberId = msg
	if memberId == role.GetRoleID():
		return
	teamId = role.GetJTeamID()
	if not teamId:
		return
	jtobj = GetTeamObj(teamId)
	if not jtobj:
		print "GE_EXC, KickMember team not obj"
		return
	if not jtobj.IsLeader(role):
		return
	if not IsJTeamCanDo():
		role.Msg(2, 0, GlobalPrompt.JT_CanNotDo)
		return
	if jtobj.IsLock():
		role.Msg(2, 0, GlobalPrompt.JT_CanNotDo)
		return
	jtobj.Kick(role, memberId)
	
def InviteMember(role, msg):
	'''
	邀请加入战队
	@param role:
	@param msg:
	'''
	teamId = role.GetJTeamID()
	if not teamId:
		return
	jtobj = GetTeamObj(teamId)
	if not jtobj:
		print "GE_EXC, InviteMember team not obj"
		return
	if not jtobj.IsLeader(role):
		return
	if len(jtobj.members) >= 3:
		role.Msg(2, 0, GlobalPrompt.JT_Team_Full)
		return
	if jtobj.IsLock():
		role.Msg(2, 0, GlobalPrompt.JT_CanNotDo)
		return
	backId, inviteroleId = msg
	if role.GetRoleID() == inviteroleId:
		return
	if not IsJTeamCanDo():
		role.Msg(2, 0, GlobalPrompt.JT_CanNotDo)
		return
	inviterole = cRoleMgr.FindRoleByRoleID(inviteroleId)
	if not inviterole:
		return
	
	if inviterole.GetJTeamID():
		role.Msg(2, 0, GlobalPrompt.JT_Tips_8)
		return
	
	if inviterole.GetLevel() < JTDefine.JTNeedLevel:
		return
	
	if not inviterole.IsLocalServer():
		return
	ftid = inviterole.GetI64(EnumInt64.JTFightTeamID)
	if ftid and ftid != teamId:
		role.Msg(2, 0, GlobalPrompt.JT_Tips_17)
		return
	if inviteroleId in jtobj.inviteRoleIds:
		return
	
	jtobj.InviteRole(role, inviterole)
	role.CallBackFunction(backId, inviteroleId)

def InviteBack(role, msg):
	'''
	邀请回复
	@param role:
	@param msg:
	'''
	backType, teamId = msg
	if role.GetJTeamID():
		return
	ftid = role.GetI64(EnumInt64.JTFightTeamID)
	if ftid and ftid != teamId:
		role.Msg(2, 0, GlobalPrompt.JT_Tips_16)
		return
	jtobj = GetTeamObj(teamId)
	if not jtobj:
		# 提示队伍已经解散
		role.Msg(2, 0, GlobalPrompt.JT_Tips_13)
		return
	if jtobj.IsLock():
		role.Msg(2, 0, GlobalPrompt.JT_CanNotDo)
		return
	roleId = role.GetRoleID()
	if roleId not in jtobj.inviteRoleIds:
		return
	
	#回复一次，就删除这个记录
	jtobj.inviteRoleIds.discard(roleId)
	if not IsJTeamCanDo():
		role.Msg(2, 0, GlobalPrompt.JT_CanNotDo)
		return
	
	if backType == 1:
		#接受
		if len(jtobj.members) >= 3:
			role.Msg(2, 0, GlobalPrompt.JT_Tips_10)
			return
		jtobj.Join(role)
		leader = cRoleMgr.FindRoleByRoleID(jtobj.leaderId)
		if leader:
			jtobj.SyncTeamToRole(leader)
	else:
		leader = cRoleMgr.FindRoleByRoleID(jtobj.leaderId)
		if not leader:
			return
		leader.Msg(2, 0, GlobalPrompt.JT_Tips_14 % role.GetRoleName())
def ChangeLeader(role, msg):
	'''
	转让队长
	@param role:
	@param msg:
	'''
	teamId = role.GetJTeamID()
	if not teamId : return
	jtobj = GetTeamObj(teamId)
	if not jtobj:
		print "GE_EXC, def ChangeLeader team not obj"
		return
	if not jtobj.IsLeader(role) : return
	if jtobj.IsLock():
		role.Msg(2, 0, GlobalPrompt.JT_CanNotDo)
		return
	memberId = msg
	if role.GetRoleID() == memberId:
		return
	if memberId not in jtobj.members:
		return
	if not IsJTeamCanDo():
		role.Msg(2, 0, GlobalPrompt.JT_CanNotDo)
		return
	
	jtobj.ChangeLeader(role, memberId)

def ChangeInfo(role, msg):
	'''
	修改战队信息
	@param role:
	@param msg:
	'''
	teamId = role.GetJTeamID()
	if not teamId : return
	jtobj = GetTeamObj(teamId)
	if not jtobj:
		print "GE_EXC, ChangeInfo team not obj"
		return
	if not jtobj.IsLeader(role) : return
	
	if jtobj.IsLock():
		role.Msg(2, 0, GlobalPrompt.JT_CanNotDo)
		return
	teamName, teamFlag = msg
	if teamFlag < 1 or teamFlag > JTDefine.MaxTeamFlag:
		return
	
	global JTeamNameSet
	if teamName in JTeamNameSet:
		return
	if not teamName or len(teamName) > 24:
		return
	if not IsJTeamCanDo():
		role.Msg(2, 0, GlobalPrompt.JT_CanNotDo)
		return
	
	isFree = False
	if str(jtobj.teamId) == jtobj.teamName:
		isFree = True
	else:
		if role.GetRMB() < JTDefine.ChanegInfoNeedRMB:
			return
	with Tra_JS_ChangeTeam:
		JTeamNameSet.add(teamName)
		if isFree is False:
			role.DecRMB(JTDefine.ChanegInfoNeedRMB)
		jtobj.ChangeInfo(role, teamName, teamFlag)

def CheckOtherJTeam(role, msg):
	'''
	查看其他战队详细信息
	@param role:
	@param msg:
	'''
	teamData = GetCanJoinTeamData()
	role.SendObj(JT_S_OtherTeamStart, 1)
	role.SendObj(JT_S_OtherTeamData, teamData[:400])
	if len(teamData) > 400:
		role.SendObj(JT_S_OtherTeamData, teamData[400:800])
	if len(teamData) > 800:
		role.SendObj(JT_S_OtherTeamData, teamData[800:1200])
	if len(teamData) > 1200:
		role.SendObj(JT_S_OtherTeamData, teamData[1200:1600])
	if len(teamData) > 1600:
		role.SendObj(JT_S_OtherTeamData, teamData[1600:])
	
def CheckJTeamInfo(role, msg):
	'''
	查看其他战队详细信息
	@param role:
	@param msg:
	'''
	backId, teamid = msg
	jtobj = GetTeamObj(teamid)
	if not jtobj:
		return
	role.CallBackFunction(backId, jtobj.GetSyncData())

def GetJTeamDayReward(role, msg):
	'''
	查看其他战队详细信息
	@param role:
	@param msg:
	'''
	backId, _ = msg
	global JT_RoleRewardGrade
	grade = JT_RoleRewardGrade.get(role.GetRoleID())
	if not grade:
		return
	
	role.CallBackFunction(backId, None)

def RequeseJoinJT(role, msg):
	'''
	请求进入跨服组队竞技场
	@param role:
	@param msg:
	'''
	jtobj = role.GetJTObj()
	if not jtobj:
		return
	if not jtobj.CanJoinCross():
		return
	if not Status.CanInStatus(role, EnumInt1.ST_JTGoToCross):
		return
	global IsStart
	#判断活动是否已经开启
	if IsStart is False:
		role.Msg(2, 0, GlobalPrompt.JT_NotStart)
		return
	#传送到跨服场景
	role.GotoCrossServer(None, JTDefine.JTReadySceneID, 958, 579, JTCross.AfterJoinCrossJTScene, (cProcess.ProcessID, jtobj.GetCrossNeedData()))
	#王者公测奖励狂翻倍触发任务进度之跨服竞技  因为马上过去跨服了 同步客户端没意义 故False 回本服时候会触发同步最新
	Event.TriggerEvent(Event.Eve_WangZheCrazyRewardTask, role, (EnumGameConfig.WZCR_Task_KuaFuJT, False))
	#激情活动奖励狂翻倍触发任务进度之跨服竞技  因为马上过去跨服了 同步客户端没意义 故False 回本服时候会触发同步最新
	Event.TriggerEvent(Event.Eve_PassionMultiRewardTask, role, (EnumGameConfig.PassionMulti_Task_KuaFuJT, False))

def RequestLogicRank(role, msg):
	'''
	客户端请求查看逻辑进程的组队竞技排行榜
	@param role:
	@param msg:
	'''
	if role.GetLevel() < JTDefine.JTNeedLevel:
		return
	backId, levelIndex = msg
	role.CallBackFunction(backId, JTeamRankLevelSyncDict.get(levelIndex, []))

def RequestGetDayReward(role, msg):
	'''
	客户端请求领取日结奖励
	@param role:
	@param msg:
	'''
	backId, _ = msg
	grade = JT_RoleRewardGrade.get(role.GetRoleID())
	if not grade:
		return
	config = JTConfig.JTDayRewardDict.get(grade)
	if not config:
		return
	with Tra_JS_DayReward:
		del JT_RoleRewardGrade[role.GetRoleID()]
		role.IncRongYu(config.rongyu)
		role.IncGongXun(config.gongxun)
	
	role.Msg(2, 0, GlobalPrompt.Reward_Tips + (GlobalPrompt.RongYu_Tips % config.rongyu) + (GlobalPrompt.GongXun_Tips % config.gongxun))
	role.CallBackFunction(backId, None)


def InviteJoinCross(role, msg):
	'''
	邀请进入跨服组队竞技
	@param role:
	@param msg:
	'''
	global IsStart
	#判断活动是否已经开启
	if IsStart is False:
		role.Msg(2, 0, GlobalPrompt.JT_Tips_19)
		return
	if role.GetCD(EnumCD.JTInviteToCrossCD):
		return
	backId, roleid = msg
	if roleid == role.GetRoleID():
		return
	
	irole = cRoleMgr.FindRoleByRoleID(roleid)
	if not irole or irole.IsLost():
		role.Msg(2, 0, GlobalPrompt.JT_Tips_21)
		return
	jtobj = role.GetJTObj()
	if not jtobj or not jtobj.CanJoinCross():
		role.Msg(2, 0, GlobalPrompt.JT_Tips_20)
		return

	if not Status.CanInStatus(irole, EnumInt1.ST_JTGoToCross):
		role.Msg(2, 0, GlobalPrompt.JT_Tips_18)
		return
	
	irole.SendObjAndBack(JT_S_InviteToCross, role.GetRoleName(), 60, InviteToCrossBack, None)
	role.CallBackFunction(backId, None)
	role.SetCD(EnumCD.JTInviteToCrossCD, 3)
	
def InviteToCrossBack(role, callArgv, regparam):
	if callArgv == 1 or callArgv is None:
		#同意或者是自动回调
		RequeseJoinJT(role, None)

################################################################################
#数据载入处理
################################################################################
def AfterLoad():
	#构建缓存管理对象
	global JT_TeamDict, JJT_Obj_Dict
	if "newversion" not in JT_TeamDict:
		#新版本兼容@JT_TeamDict
		for teamId, teamData in JT_TeamDict.items():
			teamName, teamFlag, _, leaderId, leaderName, members, _, _, _ = teamData
			newmemberdict = {}
			for memberId, memberdata in members.items():
				name, sex, grade, career, wingid, level, zdl, _,_,_,_,_, _, _ = memberdata
				newmemberdict[memberId] = [name, sex, grade, career, wingid, level, zdl, 0, 0, 0, 0]
			#新的战队数据
			newTeamData = {JTEnum.JTE_TeamID : teamId,\
						JTEnum.JTE_TeamName : teamName,\
						JTEnum.JTE_TeamFlag : teamFlag,\
						JTEnum.JTE_TeamLeaderID : leaderId,\
						JTEnum.JTE_TeamLeaderName : leaderName,\
						JTEnum.JTE_TeamScore : JTDefine.DefaultJTScore,\
						JTEnum.JTE_TeamGrade : 0,\
						JTEnum.JTE_TeamRank : JTDefine.MaxRank + 1,\
						JTEnum.JTE_TeamOldRank : JTDefine.MaxRank + 1,\
						JTEnum.JTE_TeamWinCount : 0,
						JTEnum.JTE_TeamLoseCount : 0,
						JTEnum.JTE_TeamMemberDict : newmemberdict,\
						JTEnum.JTE_TeamMaxScore : JTDefine.DefaultJTScore,\
						JTEnum.JTE_TeamMaxGrade : 0
						}
			JT_TeamDict[teamId] = newTeamData
		JT_TeamDict["newversion"] = "Finish Version up"
	
	for teamId, teamData in JT_TeamDict.iteritems():
		if teamId == "newversion":
			continue
		JJT_Obj_Dict[teamId] = JTTeamBase(teamId, teamData)

def CreatTestTeam(role):
	#创建测试数据
	global JT_TeamDict
	global JJT_Obj_Dict
	
	teamId, leaderId, rank = cProcess.AllotGUID64(), cProcess.AllotGUID64(), 1
	teamName, leaderName = "战队名%s", "队长名%s"
	for _ in xrange(2000):
		newTeamData = {JTEnum.JTE_TeamID : teamId,\
				JTEnum.JTE_TeamName : teamName % teamId,\
				JTEnum.JTE_TeamFlag : 1,\
				JTEnum.JTE_TeamLeaderID : leaderId,\
				JTEnum.JTE_TeamLeaderName : leaderName % leaderId,\
				JTEnum.JTE_TeamScore : JTDefine.DefaultJTScore,\
				JTEnum.JTE_TeamGrade : 0,\
				JTEnum.JTE_TeamRank : rank,\
				JTEnum.JTE_TeamOldRank : rank,\
				JTEnum.JTE_TeamWinCount : 0,
				JTEnum.JTE_TeamLoseCount : 0,
				JTEnum.JTE_TeamMemberDict : UpdataMemberData1(role),\
				JTEnum.JTE_TeamMaxScore : JTDefine.DefaultJTScore,\
				JTEnum.JTE_TeamMaxGrade : 0
				}
		rank += 1
		teamId += 1
		leaderId += 1
		JT_TeamDict[teamId] = newTeamData
		
	for teamId, teamData in JT_TeamDict.iteritems():
		if teamId == "newversion":
			continue
		JJT_Obj_Dict[teamId] = JTTeamBase(teamId, teamData)
		
def UpdataMemberData1(role):
	members = {}
	members[role.GetRoleID()] = [role.GetRoleName(),\
										role.GetSex(), \
										role.GetGrade(), \
										role.GetCareer(), \
										role.GetWingID(),\
										role.GetLevel(), \
										role.GetZDL(), \
										role.GetTI64(EnumTempInt64.FashionClothes),\
										role.GetTI64(EnumTempInt64.FashionHat),\
										role.GetTI64(EnumTempInt64.FashionWeapons),\
										role.GetI1(EnumInt1.FashionViewState)]
	return members

def AfterLoadRoleRewardGrade():
	pass

################################################################################
#跨服数据处理
################################################################################
def UpdateRankByCross(crossrankdict):
	#跨服把排行榜数据同步过来了
	hasdatateams = set()
	for levelIndex, rankDataList in crossrankdict.iteritems():
		#服务器ID，服务器名字，队伍ID，队伍名字，积分，段位，成员数据，战队等级，胜率(万份比)，总战力，总排名
		for rankData in rankDataList:
			teamId, teamGrade, rank = rankData[2], rankData[5], rankData[10]
			jteam = JJT_Obj_Dict.get(teamId)
			if not jteam:
				continue
			jteam.UpdataByRank(levelIndex, teamGrade, rank)
			hasdatateams.add(teamId)
		
		global JTeamRankLevelSyncDict
		#构建同步字典
		if len(rankDataList) <= JTDefine.MaxLevelRank:
			JTeamRankLevelSyncDict[levelIndex] = rankDataList
		else:
			JTeamRankLevelSyncDict[levelIndex] = rankDataList[:JTDefine.MaxLevelRank]
	
	#更新不在榜上面的战队数据
	for jteamID, jteam in JJT_Obj_Dict.iteritems():
		if jteamID in hasdatateams:
			continue
		jteam.UpdataNotInRank()
	

def UpdateJTeamInfoByCross(jteamInfoDict):
	#跨服进程把参与活动的战队数据更新过来了
	if not jteamInfoDict:
		return
	global JJT_Obj_Dict
	for teamId, info in jteamInfoDict.iteritems():
		teamObj = JJT_Obj_Dict.get(teamId)
		if not teamObj:
			continue
		teamObj.UpdateByCrossInfo(info)

def RequestControlRank():
	#向逻辑进程请求组队竞技排行榜
	if Environment.IsCross:
		return
	Call.ServerCall(Define.GetDefaultCrossID(), "Game.JT.JTCross", "LoginRequestRank", cProcess.ProcessID)

################################################################################
#角色事件处理
################################################################################
def LoginSyncData(role, param):
	rewardGrade = JT_RoleRewardGrade.get(role.GetRoleID())
	if rewardGrade:
		role.SendObj(JT_S_RewardGrade, rewardGrade)

def AfterLogin(role, param):
	#登录，更新战斗内部信息
	tobj = role.GetJTObj()
	if not tobj : 
		teamId = role.GetJTeamID()
		if teamId:
			with Tra_JS_LoginRevert:
				print "GE_EXC,role(%s) have JTeamId(%s) but not have JTObj" % (role.GetRoleID(), role.GetJTeamID())
				ClearJTeamData(role, -1)
		return
	md = tobj.members.get(role.GetRoleID())
	if not md :
		with Tra_JS_LoginRevert:
			#这里可能是离线命令还没有执行？
			print "GE_EXC role in jt but not in member (%s) (%s)" % (role.GetRoleID(), role.GetJTeamID())
			ClearJTeamData(role, tobj.GetJTeamTitleID())
		return
	tobj.UpdataMemberData(role)
	
	global JT_TeamDict
	rolejteamId = role.GetJTeamID()
	roleId = role.GetRoleID()
	for teamId, jteam in JJT_Obj_Dict.items():
		if roleId in jteam.members and teamId != rolejteamId:
			print "GE_EXC, JTeam repair team (%s, %s)" % (roleId, teamId)
			del JT_TeamDict[teamId]
			del JJT_Obj_Dict[teamId]

def BeforeExit(role, param):
	#退出游戏更新一次
	tobj = role.GetJTObj()
	if not tobj : return
	md = tobj.members.get(role.GetRoleID())
	if not md : return
	tobj.UpdataMemberData(role)

def RoleDayClear(role, param):
	#每日清理匹配队伍记录
	role.SetI64(EnumInt64.JTFightTeamID, 0)

def AfterNewDay():
	#先发日结奖励,记录到JT_RoleRewardGrade
	daydata = {}
	needDayCount = JTDefine.DayRewardNeedFightCount
	for jteam in JJT_Obj_Dict.itervalues():
		if jteam.teamDayFightCount < needDayCount:
			if jteam.teamDayFightCount == 0:
				continue
			jteam.teamDayFightCount = 0
			jteam.Save()
			continue
		jteam.teamDayFightCount = 0
		jteam.teamWeekCount += 1
		jteam.Save()
		for roleId in jteam.members:
			JT_RoleRewardGrade[roleId] = jteam.teamGrade
			daydata[roleId] = jteam.teamGrade
			
	with Tra_JS_DayRewardData:
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveJTeamDayRewardData, daydata)
		
	if cDateTime.WeekDay() != 0:
		return
	#周结奖励
	weekData = {}
	needCount = JTDefine.WeekRewardNeedCount
	with Tra_JS_WeekReward:
		for jteamId, jteam in JJT_Obj_Dict.iteritems():
			if jteam.teamWeekCount < needCount:
				if jteam.teamOldRank == jteam.teamRank and jteam.teamWeekCount == 0:
					continue
				jteam.teamOldRank = jteam.teamRank
				jteam.teamWeekCount = 0
				jteam.Save()
				continue
			jteam.teamOldRank = jteam.teamRank
			jteam.teamWeekCount = 0
			jteam.Save()
			weekConfig = JTConfig.GetWeekRewardConfig(jteam.teamRank)
			if not weekConfig:
				continue
			weekData[jteamId] = (jteam.teamRank, jteam.members.keys())
			for roleId in jteam.members:
				weekConfig.Reward(roleId, jteam.teamRank, jteam.teamScore)
	with Tra_JS_WeekRewardData:
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveJTeamWeekRewardData, weekData)


if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.EnvIsQQ() or Environment.EnvIsFT() or Environment.IsDevelop or (Environment.EnvIsNA()  and not Environment.IsNAPLUS1) or (Environment.EnvIsRU() and not Environment.IsRUGN) or Environment.EnvIsPL()) and not Environment.IsCross:
		#旧版teamId:{1:[战队ID，战斗名字，战队标识， 队长ID，队长名字， 战队积分]， 2:{成员信息字典}｝
		#新版@JT_TeamDict
		JT_TeamDict = Contain.Dict("JT_TeamDict", (2038, 1, 1), AfterLoad)
		JT_RoleRewardGrade = Contain.Dict("JT_RoleRewardGrade", (2038, 1, 1), AfterLoadRoleRewardGrade)
		
		Init.InitCallBack.RegCallbackFunction(RequestControlRank)
		
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
		
		Event.RegEvent(Event.Eve_SyncRoleOtherData, LoginSyncData)
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_BeforeExit, BeforeExit)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_CreateJTeam", "请求创建战队"), CreateJTeam)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_JoinJTeam", "请求申请加入战队"), RequestJoinJTeam)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_AcceptJoin", "请求处理战队申请"), AcceptJoin)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_LeaveJTeam", "请求离开战队"), LeaveJTeam)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_KickMember", "请求踢掉战队成员"), KickMember)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_InviteMember", "请求邀请加入战队"), InviteMember)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_InviteBack", "请求邀请回复"), InviteBack)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_ChangeLeader", "请求战队转让队长"), ChangeLeader)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_ChangeInfo", "请求修改战队信息"), ChangeInfo)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_OpenJTeamPanel", "请求打开战队主面板"), OpenJTeamPanel)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_CheckOtherJTeams", "请求查询其他战队列表"), CheckOtherJTeam)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_CheckJTeamInfo", "请求查询其他战队详细信息"), CheckJTeamInfo)

		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_RequeseJoinJT", "请求进入跨服组队竞技场"), RequeseJoinJT)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_RequestJTRank", "请求查看组队竞技排行榜"), RequestLogicRank)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_RequestGetDayReward", "客户端请求领取日结奖励"), RequestGetDayReward)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_InviteJoinCross", "客户端邀请战队队员进入跨服"), InviteJoinCross)
		
