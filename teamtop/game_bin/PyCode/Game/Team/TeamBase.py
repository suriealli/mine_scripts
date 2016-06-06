#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Team.TeamBase")
#===============================================================================
# 队伍管理
# 1. 队伍信息不跨进程
# 2. 队伍ID不保存在角色数据上，角色上线的时候主动同步客户端
#===============================================================================
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from Game.Role import Status
from Game.Role.Data import EnumInt1, EnumInt8, EnumTempObj, EnumTempInt64,\
	EnumDayInt1,EnumObj
from Game.Team import TeamData, EnumTeamType
from Game.TeamTower import TTConfig

if "_HasLoad" not in dir():
	TEAMID_TO_TEAM = {}			#队伍ID-->TEAM
	ROLEID_TO_TEAM = {}			#角色ID-->TEAM
	UNIONID_TO_TEAM_LIST = {}	#公会ID-->[team1, team2, ...]
	GVE_TEAM_LIST = []			#GVE队伍列表
	KAIFUBOSS_TEAM_LIST = []	#开服boss队伍列表
	HEFUBOSS_TEAM_LIST = []		#合服boss队伍列表
	TEAM_TOWER_LIST_0 = []		#组队爬塔序章
	TEAM_TOWER_LIST_1 = []		#组队爬塔章节1
	TEAM_TOWER_LIST_2 = []		#组队爬塔章节2
	TEAM_TOWER_LIST_3 = []		#组队爬塔章节3
	TEAM_TOWER_LIST_4 = []		#组队爬塔章节4
	TEAM_TOWER_LIST_5 = []		#组队爬塔章节5
	TEAM_TOWER_LIST_6 = []		#组队爬塔章节6
	CROSS_TEAM_TOWER_LIST = []	#虚空幻境
	LOSTSCENE_LIST = []			#迷失之境
	SHENSHUMIJING_LIST = []		#神树密境

	CHAOSDIVINITY_TEAM_LIST_1 = []		#混沌神域章节1
	CHAOSDIVINITY_TEAM_LIST_2 = []		#混沌神域章节2
	CHAOSDIVINITY_TEAM_LIST_3 = []		#混沌神域章节3
	CHAOSDIVINITY_TEAM_LIST_4 = []		#混沌神域章节4
	CHAOSDIVINITY_TEAM_LIST_5 = []		#混沌神域章节5
	CHAOSDIVINITY_TEAM_LIST_6 = []		#混沌神域章节6
	CHAOSDIVINITY_TEAM_LIST_7 = []		#混沌神域章节7
	CHAOSDIVINITY_TEAM_LIST_8 = []		#混沌神域章节8
	CHAOSDIVINITY_TEAM_LIST_9 = []		#混沌神域章节9
	CHAOSDIVINITY_TEAM_LIST_10 = []		#混沌神域章节10
	CHAOSDIVINITY_TEAM_LIST_11 = []		#混沌神域章节11
	CHAOSDIVINITY_TEAM_LIST_12 = []		#混沌神域章节12
	
	#记得添加到这里
	TTListDict = {0:TEAM_TOWER_LIST_0, 1 : TEAM_TOWER_LIST_1, 2 : TEAM_TOWER_LIST_2, 3 : TEAM_TOWER_LIST_3, 4 : TEAM_TOWER_LIST_4, 5 : TEAM_TOWER_LIST_5, 6:TEAM_TOWER_LIST_6, 7:LOSTSCENE_LIST, 8:SHENSHUMIJING_LIST}
	
	CDTeamList ={1:CHAOSDIVINITY_TEAM_LIST_1
				,2:CHAOSDIVINITY_TEAM_LIST_2
				,3:CHAOSDIVINITY_TEAM_LIST_3
				,4:CHAOSDIVINITY_TEAM_LIST_4
				,5:CHAOSDIVINITY_TEAM_LIST_5
				,6:CHAOSDIVINITY_TEAM_LIST_6
				,7:CHAOSDIVINITY_TEAM_LIST_7
				,8:CHAOSDIVINITY_TEAM_LIST_8
				,9:CHAOSDIVINITY_TEAM_LIST_9
				,10:CHAOSDIVINITY_TEAM_LIST_10
				,11:CHAOSDIVINITY_TEAM_LIST_11
				,12:CHAOSDIVINITY_TEAM_LIST_12}
	
	JTProcess_TO_Team_List = {}	#跨服组队竞技场本服队伍,进程ID-->[team1, team2, ...]
	
	#消息
	Team_SyncInfo = AutoMessage.AllotMessage("Team_SyncInfo", "通知客户端队伍信息")
	Team_SyncDismiss = AutoMessage.AllotMessage("Team_SyncDismiss", "通知客户端队伍解散")
	Team_SyncQuit = AutoMessage.AllotMessage("Team_SyncQuit", "通知客户端退出队伍")
	Team_SyncBeKicked = AutoMessage.AllotMessage("Team_SyncBeKicked", "通知客户端成员被踢出队伍")

#===============================================================================
# role接口
#===============================================================================
def GetTeam(role):
	'''获取当前的组队对象'''
	return ROLEID_TO_TEAM.get(role.GetRoleID())

def HasTeam(role):
	'''判断角色是否有队伍了 team'''
	return role.GetRoleID() in ROLEID_TO_TEAM

#===============================================================================
# 其它接口
#===============================================================================
def GetTeamByRoleID(roleId):
	return ROLEID_TO_TEAM.get(roleId)

def GetTeamByTeamID(teamId):
	return TEAMID_TO_TEAM.get(teamId)

def GetRoleTeamData(role):
	'''
	用于同步的队员信息
	@param role:
	'''
	from Game.CrossTeamTower import CrossTTMgr
	dragonMgr = role.GetTempObj(EnumTempObj.DragonMgr)
	dragonLevel = 0
	if dragonMgr:
		dragonLevel = dragonMgr.level
	#roleId，名字，性别，职业，进阶，行动力，神龙职业，神龙等级,翅膀，是否显示时装，时装衣服，时装帽子，时装武器, 战斗力, 等级， 服信息,被动技能
	return role.GetRoleID(), role.GetRoleName(), role.GetSex(), role.GetCareer(), role.GetGrade(), role.GetI8(EnumInt8.UnionFBCnt), role.GetDragonCareerID(), dragonLevel, \
		role.GetI8(EnumInt8.WingId),role.GetI1(EnumInt1.FashionViewState), role.GetTI64(EnumTempInt64.FashionClothes), role.GetTI64(EnumTempInt64.FashionHat), \
		role.GetTI64(EnumTempInt64.FashionWeapons), role.GetI8(EnumInt8.StarGirlFollowId), role.GetZDL(), role.GetLevel(), CrossTTMgr.GetRoleZoneName(role), role.GetObj(EnumObj.ChaosDivinityData).get(1, set())
#===============================================================================
# 队伍基类
#===============================================================================
class TeamBase(TeamData.TeamData):
	def __init__(self, role, teamType):
		global TEAMID_TO_TEAM
		global ROLEID_TO_TEAM
		global UNIONID_TO_TEAM_LIST
		global GVE_TEAM_LIST
		global KAIFUBOSS_TEAM_LIST
		global TEAM_TOWER_LIST_1,TEAM_TOWER_LIST_2, TEAM_TOWER_LIST_3, TEAM_TOWER_LIST_4, TEAM_TOWER_LIST_5
		global JTProcess_TO_Team_List
		global CROSS_TEAM_TOWER_LIST
		global LOSTSCENE_LIST
		global SHENSHUMIJING_LIST
		global CDTeamList
		
		TeamData.TeamData.__init__(self, role, teamType)
		
		#全局数据管理
		roleId = role.GetRoleID()
		unionId = role.GetUnionID()
		TEAMID_TO_TEAM[self.team_id] = self
		ROLEID_TO_TEAM[roleId] = self
		
		#判断队伍类型
		if teamType == EnumTeamType.T_UnionFB:
			unionId = role.GetUnionID()
			UNIONID_TO_TEAM_LIST.setdefault(unionId, []).append(self)
		elif teamType == EnumTeamType.T_GVE:
			GVE_TEAM_LIST.append(self)
		elif teamType == EnumTeamType.T_KaifuBoss:
			KAIFUBOSS_TEAM_LIST.append(self)
		elif teamType == EnumTeamType.T_HefuBoss:
			HEFUBOSS_TEAM_LIST.append(self)
		elif teamType == EnumTeamType.T_TeamTower_0:
			TEAM_TOWER_LIST_0.append(self)
		elif teamType == EnumTeamType.T_TeamTower_1:
			TEAM_TOWER_LIST_1.append(self)
		elif teamType == EnumTeamType.T_TeamTower_2:
			TEAM_TOWER_LIST_2.append(self)
		elif teamType == EnumTeamType.T_TeamTower_3:
			TEAM_TOWER_LIST_3.append(self)
		elif teamType == EnumTeamType.T_TeamTower_4:
			TEAM_TOWER_LIST_4.append(self)
		elif teamType == EnumTeamType.T_TeamTower_5:
			TEAM_TOWER_LIST_5.append(self)
		elif teamType == EnumTeamType.T_TeamTower_6:
			TEAM_TOWER_LIST_6.append(self)
		elif teamType == EnumTeamType.T_JT:
			processId = role.GetJTProcessID()
			JTProcess_TO_Team_List.setdefault(processId, []).append(self)
			#组队竞技场匹配专用
			self.matchRound_1 = 0
			self.matchRound_2 = 0
			self.teamScore = 0
			self.matchTimes = 0
		elif teamType == EnumTeamType.T_CrossTeamTower:
			CROSS_TEAM_TOWER_LIST.append(self)
		elif teamType == EnumTeamType.T_LostScene:
			#迷失之境五人组队
			self.max_member_cnt = 5
			LOSTSCENE_LIST.append(self)
		elif teamType == EnumTeamType.T_Shenshumijing:
			#神树密境
			SHENSHUMIJING_LIST.append(self)
		elif EnumTeamType.IsChaosDivinityType(teamType):
			#混沌神域
			index = teamType - EnumTeamType.T_ChaosDivinity1 + 1
			ChaosDivinityTeamList = CDTeamList.get(index,-1)
			if ChaosDivinityTeamList != -1:
				ChaosDivinityTeamList.append(self)
		else:
			print "GE_EXC, error team create (%s)" % teamType
		
		
		#状态
		Status.TryInStatus(role, EnumInt1.ST_Team)
		
		#创建成功，同步客户端
		self.SyncClient()
		
	def Join(self, role):
		'''
		加入队伍
		@param role:
		'''
		#加入队伍
		self.AddMember(role)
		
	def Dismiss(self):
		'''
		解散队伍
		'''
		global ROLEID_TO_TEAM
		
		#在线队员
		for member in self.members:
			#先同步
			member.SendObj(Team_SyncDismiss, None)
			mid = member.GetRoleID()
			if mid in ROLEID_TO_TEAM:
				#删除队伍信息
				del ROLEID_TO_TEAM[mid]
			#退出组队状态
			Status.Outstatus(member, EnumInt1.ST_Team)
		
		self.members = []
		
		#清理队伍
		self.Clear()
		
	def Quit(self, role):
		'''
		退出队伍
		@param role:
		@param backFunId:
		'''
		#离开队伍
		self.RemoveMember(role)
		
		#通知客户端退出队伍
		role.SendObj(Team_SyncQuit, None)

		
		#队伍已经没人了
		if not self.members:
			#清理队伍
			self.Clear()
			return
		
		#队长离开队伍
		if self.leader == role:
			#更换队长，取最近的成员
			self.NewLeader(self.members[0])
			
		#同步客户端
		self.SyncClient()
		
	def Kick(self, role):
		'''
		踢掉成员
		@param role:
		'''
		self.RemoveMember(role)
		#通知客户端
		role.SendObj(Team_SyncBeKicked, None)
		
		self.SyncClient()
		
	def ChangePos(self, pos1, pos2):
		'''
		改变位置
		@param pos1:
		@param pos2:
		'''
		#改变队员位置
		cnt = len(self.members)
		if pos1 > cnt or pos2 > cnt:
			return
		#交换两个位置
		self.members[pos1 - 1], self.members[pos2 - 1] = self.members[pos2 - 1], self.members[pos1 - 1]
		#同步客户端
		self.SyncClient()
		
	def Clear(self):
		'''
		清理队伍数据
		'''
		global TEAMID_TO_TEAM
		global UNIONID_TO_TEAM_LIST
		global GVE_TEAM_LIST
		global TEAM_TOWER_LIST_1, TEAM_TOWER_LIST_2, TEAM_TOWER_LIST_3, TEAM_TOWER_LIST_4, TEAM_TOWER_LIST_5
		global LOSTSCENE_LIST
		
		if self.team_id in TEAMID_TO_TEAM:
			del TEAMID_TO_TEAM[self.team_id]
		
		if self.team_type == EnumTeamType.T_UnionFB:
			if self.union_id in UNIONID_TO_TEAM_LIST:
				if self in UNIONID_TO_TEAM_LIST[self.union_id]:
					UNIONID_TO_TEAM_LIST[self.union_id].remove(self)
				else:
					print "GE_EXC team Clear error T_UnionFB not in list"
			else:
				print "GE_EXC team Clear error T_UnionFB not in UNIONID_TO_TEAM_LIST"
				
		elif self.team_type == EnumTeamType.T_GVE:
			if self in GVE_TEAM_LIST:
				GVE_TEAM_LIST.remove(self)
			else:
				print "GE_EXC team Clear error T_GVE"
		elif self.team_type == EnumTeamType.T_KaifuBoss:
			if self in KAIFUBOSS_TEAM_LIST:
				KAIFUBOSS_TEAM_LIST.remove(self)
			else:
				print "GE_EXC team Clear error T_KaifuBoss"
		elif self.team_type == EnumTeamType.T_HefuBoss:
			if self in HEFUBOSS_TEAM_LIST:
				HEFUBOSS_TEAM_LIST.remove(self)
			else:
				print "GE_EXC team Clear error T_HefuBoss"
		elif self.team_type == EnumTeamType.T_TeamTower_0:
			if self in TEAM_TOWER_LIST_0:
				TEAM_TOWER_LIST_0.remove(self)
			else:
				print "GE_EXC team Clear error T_TeamTower_0"
		elif self.team_type == EnumTeamType.T_TeamTower_1:
			if self in TEAM_TOWER_LIST_1:
				TEAM_TOWER_LIST_1.remove(self)
			else:
				print "GE_EXC team Clear error T_TeamTower_1"
		elif self.team_type == EnumTeamType.T_TeamTower_2:
			if self in TEAM_TOWER_LIST_2:
				TEAM_TOWER_LIST_2.remove(self)
			else:
				print "GE_EXC team Clear error T_TeamTower_2"
		elif self.team_type == EnumTeamType.T_TeamTower_3:
			if self in TEAM_TOWER_LIST_3:
				TEAM_TOWER_LIST_3.remove(self)
			else:
				print "GE_EXC team Clear error T_TeamTower_3"
		elif self.team_type == EnumTeamType.T_TeamTower_4:
			if self in TEAM_TOWER_LIST_4:
				TEAM_TOWER_LIST_4.remove(self)
			else:
				print "GE_EXC team Clear error T_TeamTower_4"
		elif self.team_type == EnumTeamType.T_TeamTower_5:
			if self in TEAM_TOWER_LIST_5:
				TEAM_TOWER_LIST_5.remove(self)
			else:
				print "GE_EXC team Clear error T_TeamTower_5"
				
		elif self.team_type == EnumTeamType.T_TeamTower_6:
			if self in TEAM_TOWER_LIST_6:
				TEAM_TOWER_LIST_6.remove(self)
			else:
				print "GE_EXC team Clear error T_TeamTower_6"
				
		elif self.team_type == EnumTeamType.T_JT:
			if self.processId in JTProcess_TO_Team_List:
				if self in JTProcess_TO_Team_List[self.processId]:
					JTProcess_TO_Team_List[self.processId].remove(self)
				else:
					print "GE_EXC team Clear error T_JT not in list"
			else:
				print "GE_EXC team Clear error T_JT not in JTProcess_TO_Team_List"
		elif self.team_type == EnumTeamType.T_CrossTeamTower:
			if self in CROSS_TEAM_TOWER_LIST:
				CROSS_TEAM_TOWER_LIST.remove(self)
			else:
				print "GE_EXC team Clear error T_CrossTeamTower"
		elif self.team_type == EnumTeamType.T_LostScene:
			if self in LOSTSCENE_LIST:
				LOSTSCENE_LIST.remove(self)
			else:
				print "GE_EXC team Clear error T_LostScene"
		elif self.team_type == EnumTeamType.T_Shenshumijing:
			if self in SHENSHUMIJING_LIST:
				SHENSHUMIJING_LIST.remove(self)
			else:
				print "GE_EXC team Clear error T_Shenshumijing"
		elif EnumTeamType.IsChaosDivinityType(self.team_type):
			#混沌神域
			index = self.team_type - EnumTeamType.T_ChaosDivinity1 + 1
			ChaosDivinityTeamList = CDTeamList.get(index,-1)
			if ChaosDivinityTeamList != -1:
				if self in ChaosDivinityTeamList:
					ChaosDivinityTeamList.remove(self)
		else:
			print "GE_EXC team Clear error not teamtype", self.team_type
		
	def NewLeader(self, role):
		self.leader = role
		#同步客户端
		self.SyncClient()
	
	def AddMember(self, role):
		global ROLEID_TO_TEAM
		
		if not Status.TryInStatus(role, EnumInt1.ST_Team):
			return
		
		
		ROLEID_TO_TEAM[role.GetRoleID()] = self
		self.members.append(role)
		
		self.SyncClient()
		
	def RemoveMember(self, role):
		global ROLEID_TO_TEAM
		
		#移除一个成员(注意需要最后才处理全局数据)
		roleId = role.GetRoleID()
		
		if role in self.members:
			self.members.remove(role)
		
		if roleId in ROLEID_TO_TEAM:
			del ROLEID_TO_TEAM[roleId]
		
		Status.Outstatus(role, EnumInt1.ST_Team)
		
	def BroadMsg(self, msg, param):
		'''
		队伍内广播消息
		@param msg:
		@param param:
		'''
		for member in self.members:
			member.SendObj(msg, param)
		
	def SyncClient(self):
		'''
		同步队伍所有人队伍数据
		'''
		memberData = []
		for member in self.members:
			memberData.append(GetRoleTeamData(member))
		#teamId，leaderId，成员数据
		packData = self.team_id, self.team_type, self.leader.GetRoleID(), self.fb_id, memberData
		self.BroadMsg(Team_SyncInfo, packData)
	
	def CheckFollow(self):
		#检查一下跟随状态
		if self.team_type == EnumTeamType.T_JT or self.team_type == EnumTeamType.T_LostScene:
			# 跨服组队竞技场不跟随、迷失之境不跟随
			return
		elif EnumTeamType.IsTeamTowerType(self.team_type):
			if not self.leader.GetTempObj(EnumTempObj.MirrorScene):
				return
		scene = self.leader.GetScene()
		posX, posY = self.leader.GetPos()
		for member in self.members:
			if member == self.leader:
				continue
			if member.GetScene() != scene:
				#场景不一样？
				#scene.JoinRole(member, posX, posY)
				continue
			x, y = member.GetPos()
			#不在附近
			if abs(x - posX) > 800:
				member.JumpPos(posX, posY)
				continue
			if abs(y - posY) > 800:
				member.JumpPos(posX, posY)
				continue
		
	def CanJoin(self, role):
		#判断队伍类型
		if self.team_type == EnumTeamType.T_UnionFB:
			#等级限制
			if role.GetLevel() < EnumGameConfig.TEAM_UNION_FB_NEED_LEVEL:
				return False
			#需要有公会
			unionId = role.GetUnionID()
			if not unionId:
				return
			#需要和队长同个公会
			if unionId != self.leader.GetUnionID():
				return
		elif self.team_type == EnumTeamType.T_GVE:
			#等级限制
			if role.GetLevel() < EnumGameConfig.TEAM_GVE_NEED_LEVEL:
				return False
			#需要有神龙职业
			if not role.GetDragonCareerID():
				return False
			#队伍是否已经在副本中
			if self.leader.GetTempObj(EnumTempObj.MirrorScene):
				return False
		elif EnumTeamType.IsTeamTowerType(self.team_type):
			if self.team_type == EnumTeamType.T_TeamTower_0:
				if role.GetLevel() < EnumGameConfig.TEAM_TOWER_NEED_LEVEL_0:
					role.Msg(2, 0, GlobalPrompt.TT_Level_Tips_0)
					return
			else:
				if role.GetLevel() < EnumGameConfig.TEAM_TOWER_NEED_LEVEL:
					role.Msg(2, 0, GlobalPrompt.TT_Level_Tips)
					return False
			if self.leader.GetTempObj(EnumTempObj.MirrorScene):
				#已经开始打了
				return False
			if role.GetI8(EnumInt8.UnionFBId):
				return False
			index = EnumTeamType.GetTeamTowerTypeIndex(self.team_type)
			#判断坐骑是否是飞行坐骑
			cfg = TTConfig.TeamTowerConfig_Dict.get(index)
			if not cfg:
				return False
			if role.GetRightMountID() not in cfg.needMountIDs:
				role.Msg(2, 0, GlobalPrompt.TT_JoinMount_Tips)
				return False
		elif self.team_type == EnumTeamType.T_KaifuBoss:
			if role.GetLevel() < EnumGameConfig.KaifuBossNeedLevel:
				return False
			
		elif self.team_type == EnumTeamType.T_HefuBoss:
			if role.GetLevel() < EnumGameConfig.HefuBossNeedLevel:
				return False
		
		elif self.team_type == EnumTeamType.T_JT:
			if role.GetJTProcessID() != self.processId:
				return False
			if Status.IsInStatus(role, EnumInt1.ST_JTMatch):
				#匹配中
				return
			for member in self.members:
				if Status.IsInStatus(member, EnumInt1.ST_JTMatch):
					#这个队伍在匹配中
					return
		elif self.team_type == EnumTeamType.T_CrossTeamTower:
			if role.GetLevel() < EnumGameConfig.CTT_NEED_LEVEL:
				role.Msg(2, 0, GlobalPrompt.CTT_LIMIT_LEVEL)
				return False
		elif self.team_type == EnumTeamType.T_LostScene:
			if self.leader.GetTempObj(EnumTempObj.MirrorScene):
				#已经开始打了
				role.Msg(2, 0, GlobalPrompt.TEAM_IN_FIGHT_PROMPT)
				return False
			if role.GetLevel() < EnumGameConfig.LostSceneNeedLevel:
				return False
			if role.GetDI1(EnumDayInt1.LostSceneIsIn):
				role.Msg(2, 0, GlobalPrompt.LostSceneCannotIn)
				return False
		elif self.team_type == EnumTeamType.T_Shenshumijing:
			if role.GetLevel() < EnumGameConfig.ShenshumijingLevel:
				return False
		elif EnumTeamType.IsChaosDivinityType(self.team_type):
			if role.GetLevel() < EnumGameConfig.ChaosDivinityLevel:
				return False
			max_activeId = role.GetObj(EnumObj.ChaosDivinityData)[0]
			index = self.team_type - EnumTeamType.T_ChaosDivinity1 + 1
			#激活章节小于队伍章节
			if max_activeId + 1 < index:
				role.Msg(2, 0, GlobalPrompt.CD_TeamCanNotJoin_Tips)
				return False
		else:
			print "GE_EXC can join error not this teamtype (%s)" % self.team_type
			return
			
		if role.HasTeam():
			return False
		
		if self.IsFull():
			#提示
			role.Msg(2, 0, GlobalPrompt.TEAM_FULL_PROMPT)
			return False
		
		if not Status.CanInStatus(role, EnumInt1.ST_Team):
			return False
		
		return True
	
	def CanDismiss(self, role):
		#判断队伍类型
		if EnumTeamType.IsTeamTowerType(self.team_type):
			if Status.IsInStatus(role, EnumInt1.ST_InTeamMirror):
				#副本中不能解散队伍
				return False
		elif self.team_type == EnumTeamType.T_JT:
			if Status.IsInStatus(role, EnumInt1.ST_JTMatch):
				return False
		elif self.team_type == EnumTeamType.T_CrossTeamTower:
			if Status.IsInStatus(role, EnumInt1.ST_InTeamMirror):
				#副本中不能解散队伍
				return False
		elif self.team_type == EnumTeamType.T_LostScene:
			if Status.IsInStatus(role, EnumInt1.ST_InTeamMirror):
				#副本中不能解散队伍
				return False
		elif EnumTeamType.IsChaosDivinityType(self.team_type):
			if Status.IsInStatus(role, EnumInt1.ST_FightStatus):
				return False
		#是否可以解散队伍
		if not self.IsTeamLeader(role):
			return False
		return True
	
	def CanQuit(self, role):
		#是否可以离开队伍
		if EnumTeamType.IsTeamTowerType(self.team_type):
			if role.GetTempObj(EnumTempObj.MirrorScene):
				return False
		elif self.team_type == EnumTeamType.T_JT:
			if Status.IsInStatus(role, EnumInt1.ST_JTMatch):
				return False
		elif self.team_type == EnumTeamType.T_CrossTeamTower:
			if role.GetTempObj(EnumTempObj.MirrorScene):
				return False
		elif self.team_type == EnumTeamType.T_LostScene:
			if Status.IsInStatus(role, EnumInt1.ST_InTeamMirror):
				#副本中不能解散队伍
				return False
		elif EnumTeamType.IsChaosDivinityType(self.team_type):
			if Status.IsInStatus(role, EnumInt1.ST_FightStatus):
				return False
		return True
	
	def CanKick(self, role):
		#是否可以踢掉成员
		if EnumTeamType.IsTeamTowerType(self.team_type):
			if Status.IsInStatus(role, EnumInt1.ST_InTeamMirror):
				#副本中不能踢掉成员
				return False
		elif self.team_type == EnumTeamType.T_GVE:
			if Status.IsInStatus(role, EnumInt1.ST_InTeamMirror):
				#副本中不能踢掉成员
				return False
		elif self.team_type == EnumTeamType.T_JT:
			if Status.IsInStatus(role, EnumInt1.ST_JTMatch):
				return
		elif self.team_type == EnumTeamType.T_CrossTeamTower:
			if Status.IsInStatus(role, EnumInt1.ST_InTeamMirror):
				#副本中不能踢掉成员
				return False
		elif self.team_type == EnumTeamType.T_LostScene:
			if Status.IsInStatus(role, EnumInt1.ST_InTeamMirror):
				#副本中不能解散队伍
				return False
		if not self.IsTeamLeader(role):
			return False
		return True
	
	def CanInvite(self, role):
		if self.IsFull():
			return False
		
		return True
	
	def CanBeInvite(self, role):
		#判断队伍类型
		if self.team_type == EnumTeamType.T_UnionFB:
			#等级限制
			if role.GetLevel() < EnumGameConfig.TEAM_UNION_FB_NEED_LEVEL:
				return False
			
		elif self.team_type == EnumTeamType.T_GVE:
			#等级限制
			if role.GetLevel() < EnumGameConfig.TEAM_GVE_NEED_LEVEL:
				return False
		elif EnumTeamType.IsTeamTowerType(self.team_type):
			if self.team_type == EnumTeamType.T_TeamTower_0:
				if role.GetLevel() < EnumGameConfig.TEAM_TOWER_NEED_LEVEL_0:
					return
			else:
				if role.GetLevel() < EnumGameConfig.TEAM_TOWER_NEED_LEVEL:
					return False
		elif self.team_type == EnumTeamType.T_JT:
			if self.processId != role.GetJTProcessID():
				return False
			if Status.IsInStatus(role, EnumInt1.ST_JTMatch):
				#匹配中
				return
		elif self.team_type == EnumTeamType.T_CrossTeamTower:
			if role.GetLevel() < EnumGameConfig.CTT_NEED_LEVEL:
				return False
		elif self.team_type == EnumTeamType.T_LostScene:
			if role.GetLevel() < EnumGameConfig.LostSceneNeedLevel:
				return False
		elif self.team_type == EnumTeamType.T_Shenshumijing:
			if role.GetLevel() < EnumGameConfig.ShenshumijingLevel:
				return False
			
		if role.HasTeam():
			return False
		
		if self.IsFull():
			return False
		
		if not Status.CanBeInStatus(role, EnumInt1.ST_Team):
			return False
		
		return True
	
	
