#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ChaosDivinity.ChaosDivinityMgr")
#===============================================================================
# 混沌神域
#===============================================================================
import cComplexServer
import cProcess
import cRoleMgr
import cDateTime
import Environment
from Common.Message import AutoMessage,PyMessage
from ComplexServer.Log import AutoLog
from Common.Other import GlobalPrompt,EnumSocial,EnumGameConfig
from ComplexServer import Init
from Game.Persistence import Contain
from Game.Role import Event,Status,Rank
from Game.Role.Data import EnumObj,EnumDayInt8,EnumDayInt1,EnumInt1,EnumCD,EnumInt32,EnumTempObj
from Game.RoleFightData import RoleFightData
from Game.RoleView import RoleView
from Game.Team import TeamBase,EnumTeamType
from Game.Fight import Fight,Middle
from Game.Union import UnionMgr,UnionDefine
from ComplexServer.Plug.Control import ControlProxy
from Game.GlobalData import ZoneName
from Game.ChaosDivinity import ChaosDivinityConfig
from Game.ChaosDivinity.ChaosDivinityConfig import ChaosDivinity_BossListDict,ChaosDivinity_BossInfoDict,ChaosDivinity_PassiveSkillList,ChaosDivinity_RankRewardDict


if "_HasLoad" not in dir():

	DayKey 	 = 0		#日期key
	DataKey = 1 	#数据Key

	#跨服排行榜数据 ，前50名数据, 今天，昨天
	ControlRank = [] #单个排名内容(角色ID，角色名字，服务器名字, 章节, 回合数, 战斗力)
	ControlRank_Old = []

	RealRankReward = (0,{})
	RealRankReward2 = (0, {}) 	#控制、逻辑服务器时间可能不同步，需要一个缓存

	RankRewardID = -1 	#排行榜可领奖励
	LocalRank	 = 0 	#混沌神域本服排名

	OpenPaneRoles = set()	#
	#日志
	ChaosDivinity_Reward = AutoLog.AutoTransaction("ChaosDivinity_Reward", "混沌神域战斗奖励")
	Tra_ChaosDivinity_Skill = AutoLog.AutoTransaction("Tra_ChaosDivinity_Skill", "混沌神域选择被动技能")
	ChaosDivinity_InviteSub = AutoLog.AutoTransaction("ChaosDivinity_InviteSub", "混沌神域邀请替身")
	ChaosDivinity_RankReward = AutoLog.AutoTransaction("ChaosDivinity_RankReward", "混沌神域排行榜奖励")
	ChaosDivinity_LocalRank = AutoLog.AutoTransaction("ChaosDivinity_LocalRank", "混沌神域本地排行榜")
	#消息
	ChaosDivinity_BossList 			 = AutoMessage.AllotMessage("ChaosDivinity_BossList", "混沌神域Boos清单")	#{index:[mcid]}
	ChaosDivinity_TeamInfo 			 = AutoMessage.AllotMessage("ChaosDivinity_TeamInfo", "混沌神域组队信息")
	ChaosDivinity_PassiveSkillInfo 	 = AutoMessage.AllotMessage("ChaosDivinity_PassiveSkillInfo", "混沌神域被动技能")
	ChaosDivinity_RewardStar		 = AutoMessage.AllotMessage("ChaosDivinity_RewardStar", "混沌神域星级评价")
	ChaosDivinity_ActiveID			 = AutoMessage.AllotMessage("ChaosDivinity_ActiveID", "混沌神域激活章节")
	ChaosDivinity_InviteInfo 		 = AutoMessage.AllotMessage("ChaosDivinity_InviteInfo", "混沌神域好友邀请")

	ChaosDivinity_SubStituteData	 = AutoMessage.AllotMessage("ChaosDivinity_ShowSubStitute", "显示混沌神域替身数据")
	ChaosDivinity_SubTeamInfo 		 = AutoMessage.AllotMessage("ChaosDivinity_Substitute_Team", "混沌神域替身组队信息")
	ChaosDivinity_DismissSubTeam 	 = AutoMessage.AllotMessage("ChaosDivinity_DismissSubTeam", "混沌神域替身队伍解散")

	ChaosDivinity_Rank 				 = AutoMessage.AllotMessage("ChaosDivinity_Rank", "混沌神域排行榜") #{0:今日排行榜,1:昨日排行榜,2:排行榜是否可领奖励}


#===============================================================================
# (角色ID)，(角色名字)，服务器名字, 章节, 回合数, 战斗力,进程ID
#===============================================================================
#该排行榜非个人排行，可以复用SmallRoleRank
class CDBestChallageRank(Rank.SmallRoleRank):
	defualt_data_create = dict				#持久化数据需要定义的数据类型
	max_rank_size = 50						#最大排行榜 50个
	dead_time = (2038, 1, 1)
	
	needSync = False						#不需要同步给客户端 
	name = "ChaosDivinity_BestChallage"
	
	# 返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		#章节
		if v1[3] != v2[3]:
			return v1[3] < v2[3]
		#通关回合数
		if v1[4] != v2[4]:
			return v1[4] > v2[4]
		#挑战时的战斗力
		if v1[5] != v2[5]:
			return v1[5] < v2[5]
		#角色ID
		return v1[0][0] < v2[0][0]

	def Clear(self):
		#清理数据
		self.data = {}
		self.min_role_id = 0
		self.min_value = 0
		self.changeFlag = True
	
	def AfterLoadFun(self):
		Rank.SmallRoleRank.AfterLoadFun(self)
		TryUpdate()

#离线角色
class SubRole(object):
	def __init__(self,roleid,skillids):
		self.role_id 	= roleid
		self.skill_ids 	= skillids

#混沌神域替身组队
class ChaosDivinitySubTeam(object):
	def __init__(self, role):
		self.role = role
		self.members = [SubRole(role.GetRoleID(),role.GetObj(EnumObj.ChaosDivinityData)[1])]
		self.max_member_cnt = 3
		self.memberDataDict = {role.GetRoleID():[role.GetRoleName(), role.GetLevel(),role.GetSex(), role.GetCareer(), role.GetGrade(),role.GetZDL(),role.GetObj(EnumObj.ChaosDivinityData)[1]]}

		self.role_map = {role.GetRoleID():self.members[0]}

	#强制刷新队长
	def SyncRole(self):
		self.memberDataDict[self.role.GetRoleID()] = [self.role.GetRoleName(), self.role.GetLevel(),self.role.GetSex(), self.role.GetCareer(), self.role.GetGrade(),self.role.GetZDL(),self.role.GetObj(EnumObj.ChaosDivinityData)[1]]

	def SyncMember(self):
		self.SyncRole()

		unionObj = self.role.GetUnionObj()
		if not unionObj:
			return

		for sub_role in self.members:
			if sub_role.role_id != self.role.GetRoleID():
				self.memberDataDict[sub_role.role_id] = GetSampleInfo(unionObj,sub_role)

	def GetSubRole(self,roleId):
		return self.role_map.get(roleId,None)

	def IsInTeam(self,roleId):
		return self.GetSubRole(roleId) is not None

	def sync_client(self):
		dataList = []
		for sub_role in self.members:
			name,level,sex, career, grade, zdl,skill_ids = self.memberDataDict[sub_role.role_id]
			dataList.append((sub_role.role_id, name, level, sex, career, grade, zdl,skill_ids))

		self.role.SendObj(ChaosDivinity_SubTeamInfo, dataList)

	def join(self,unionObj, roleId):
		for sub_role in self.members:
			if roleId == sub_role.role_id:
				return False
		
		if self.is_full():
			return False

		#验证是否工会成员
		skill_ids = ChaosDivinityConfig.GetRandomSkill(2)

		sub_role = SubRole(roleId,skill_ids)
		self.members.append(sub_role)

		self.memberDataDict[roleId] = GetSampleInfo(unionObj,sub_role)
		self.role_map[roleId] = sub_role

		self.sync_client()
		return True
		
	def kick(self, roleId):
		sub_role = self.role_map.get(roleId,None)
		if not sub_role:
			return

		self.members.remove(sub_role)
		del self.memberDataDict[sub_role.role_id]
		del self.role_map[roleId]

		self.sync_client()

	def dismiss(self, role):
		role.SetTempObj(EnumTempObj.ChaosDivinityTeam, None)
		
		#退出组队状态
		Status.Outstatus(role, EnumInt1.ST_Team)
		role.SendObj(ChaosDivinity_DismissSubTeam,None)

	def is_full(self):
		if len(self.members) >= self.max_member_cnt:
			return True
		return False

#战斗状态辅助
class FightState(object):
	boss_count = 0 		#boss数量
	reward_roles = [] 	#玩家列表
	index = -1 			#章节索引

	def __init__(self,index,roles,bosscnt):
		self.reward_roles = roles
		self.boss_count = bosscnt
		self.index = index

	def GetBossCnt(self):
		'''
		总共Boss数
		'''
		return self.boss_count

	def IsFinished(self,fight):
		'''
		是否通关
		'''
		return fight.result == 1

	def Reward(self,killed_boss):
		'''
		发放战斗奖励
		'''
		return ChaosDivinityConfig.GetReward(self.index,killed_boss)

	def RewardStar(self,role,begin_star,end_star):
		'''
		发放星级奖励
		'''
		return ChaosDivinityConfig.GetStarReward(self.index,begin_star,end_star)

	def EvaluateAll(self,fight_round,killed_boss,fight):
		'''
		更新所有数据
		'''
		#更新排行榜
		if self.IsFinished(fight):
			if len(self.reward_roles) > 1:
				role_ids 	= [ role.GetRoleID() for role in self.reward_roles]
				role_names 	= [ role.GetRoleName() for role in self.reward_roles]
				team_zdl = 0
				for role in self.reward_roles:
					team_zdl += role.GetZDL()

				#按角色ID排序,对队伍做哈希
				role_ids_hash = [ role.GetRoleID() for role in self.reward_roles]
				role_ids_hash.sort(key = lambda x:x)

				unique_team = (role_ids_hash[0],role_ids_hash[1],role_ids_hash[2])

				global CDR
				CDR.HasData(unique_team,[role_ids,role_names,ZoneName.ZoneName,self.index,fight_round,team_zdl,cProcess.ProcessID])
		#统计奖励
		for role in self.reward_roles:
			if killed_boss <= 0:
				continue
			if role.IsKick():
				continue

			reward_dict = {1:[], 2:0, 3:0}	#{1:道具,2:历练值,3:印章}

			temp_dict = {1:[],2:0,3:0}
			#击杀Boss奖励
			if IsCanReward(role):
				temp_dict = self.Reward(killed_boss)

			reward_dict[1].extend(temp_dict.get(1,[]))
			reward_dict[2] += temp_dict.get(2,0)
			reward_dict[3] += temp_dict.get(3,0)
			#星级奖励
			star = -1
			temp_dict = {1:[],2:0,3:0}

			if self.IsFinished(fight):
				star 	 = ChaosDivinityConfig.GetStar(self.index,fight_round)
				old_star = GetRoleStar(role,self.index)

				if star > old_star:
					temp_dict = self.RewardStar(role,old_star+1,star)
				#激活下一个章节
				if self.index > GetActiveId(role):
					SetActiveId(role,self.index)

			reward_dict[1].extend(temp_dict.get(1,[]))
			reward_dict[2] += temp_dict.get(2,0)
			reward_dict[3] += temp_dict.get(3,0)

			#记录挑战次数
			if IsCanReward(role):
				role.SetDI8(EnumDayInt8.ChaosDivinityCnt,1)

			#记录通关星级
			if star >=0 and star < 3:
				if star > GetRoleStar(role,self.index):
					SetRoleStar(role,self.index,star)

			#没有奖励
			if len(reward_dict[1]) == 0 and reward_dict[2] == 0 and reward_dict[3] == 0:
				continue

			tips = GlobalPrompt.Reward_Tips

			#处理叠加道具
			reward_dict[1] = UniqueItem(reward_dict[1])

			#道具奖励
			for coding,cnt in reward_dict[1].iteritems():
				role.AddItem(coding,cnt)
				tips += GlobalPrompt.Item_Tips % (coding,cnt)
			#历练值奖励
			if reward_dict[2] > 0:
				role.IncI32(EnumInt32.SealLiLianAmounts, reward_dict[2])
				tips += GlobalPrompt.SealExp_Tips % reward_dict[2]
			#印章奖励
			if reward_dict[3] > 0:
				role.IncI32(EnumInt32.SealAmounts, reward_dict[3])
				tips += GlobalPrompt.Seal_Tips % reward_dict[3]

			role.Msg(2,0,tips)

def UniqueItem(item_list):
	'''
	处理叠加道具
	'''
	item_dict = {}
	for coding,cnt in item_list:
		item_dict[coding] = item_dict.get(coding,0) + cnt

	return item_dict

def GetSampleInfo(unionObj,sub_role):
	'''
	获取工会玩家基本信息(离线)
	'''
	#获取一个玩家的头像
	role = cRoleMgr.FindRoleByRoleID(sub_role.role_id)
	if role:
		#先尝试查找在线玩家
		return (role.GetRoleName(),role.GetLevel(),role.GetSex(), role.GetCareer(), role.GetGrade(), role.GetZDL(),sub_role.skill_ids)

	inviteRoleId = sub_role.role_id

	return(unionObj.get_member_data(inviteRoleId, UnionDefine.M_NAME_IDX)
			,unionObj.get_member_data(inviteRoleId, UnionDefine.M_LEVEL_IDX)
			,unionObj.get_member_data(inviteRoleId, UnionDefine.M_PICTURE_IDX)[0]
			,unionObj.get_member_data(inviteRoleId, UnionDefine.M_PICTURE_IDX)[1]
			,unionObj.get_member_data(inviteRoleId, UnionDefine.M_PICTURE_IDX)[2]
			,unionObj.get_member_data(inviteRoleId, UnionDefine.M_ZDL_IDX)
			,sub_role.skill_ids)

	#return (roledata[EnumSocial.RoleNameKey],roledata[EnumSocial.RoleLevelKey],roledata[EnumSocial.RoleSexKey], roledata[EnumSocial.RoleCareerKey], roledata[EnumSocial.RoleGradeKey],roledata[EnumSocial.RoleZDLKey],sub_role.skill_ids)

def GetSampleInfoByID(roleId):
	#获取一个玩家的头像
	role = cRoleMgr.FindRoleByRoleID(roleId)
	if role:
		#先尝试查找在线玩家
		return (roleId,role.GetRoleName(),role.GetLevel())
	rD = RoleView.RoleView_BT.GetData().get(roleId)
	if not rD:
		return (1, 1, 1)
	roledata = rD["viewData"][1]
	return (roleId,roledata[EnumSocial.RoleNameKey],roledata[EnumSocial.RoleLevelKey], roledata[EnumSocial.RoleZDLKey])

def IsCanSync(team):
	'''
	队伍是否可同步
	'''
	return  not team.leader.IsKick() \
			and not Status.IsInStatus(team.leader, EnumInt1.ST_FightStatus)

def IsCanInvite(role):
	'''
	队伍是否可发出邀请
	'''
	team = role.GetTeam()
	if not team:
		return False

	return  not Status.IsInStatus(team.leader, EnumInt1.ST_FightStatus) \
			and not team.IsFull()

def IsCanStart(role):
	'''
	是否可以开启战斗
	'''
	#获取队伍
	team = role.GetTeam()
	if not team:
		return False

	return team.IsTeamLeader(role) \
			and len(team.members) == 3 \
			and Status.CanInStatus_Roles(team.members,EnumInt1.ST_FightStatus)

def IsCanReward(role):
	'''
	是否影响玩家数据
	'''
	return not role.GetI1(EnumInt1.ChaosDivinityNoReward) \
			and role.GetDI8(EnumDayInt8.ChaosDivinityCnt) <= 0

def SetRoleSkill(role,skill_ids):
	temp_dict = role.GetObj(EnumObj.ChaosDivinityData)
	temp_dict[1] = set(skill_ids)

	role.SetObj(EnumObj.ChaosDivinityData,temp_dict)
	#log
	with Tra_ChaosDivinity_Skill:
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveChaosDivinitySkill, temp_dict[1])

def SetRoleStar(role,index,star):
	temp_dict = role.GetObj(EnumObj.ChaosDivinityData)
	temp_dict[2][index] = star

	role.SetObj(EnumObj.ChaosDivinityData,temp_dict)

	SyncRewardStar(role,index)

def GetRoleStar(role,index):
	temp_dict = role.GetObj(EnumObj.ChaosDivinityData)
	return temp_dict[2][index]

def GetActiveId(role):
	return role.GetObj(EnumObj.ChaosDivinityData)[0]

def SetActiveId(role,index):
	temp_dict = role.GetObj(EnumObj.ChaosDivinityData)
	temp_dict[0] = index
	role.SetObj(EnumObj.ChaosDivinityData,temp_dict)

def IncHireCount(role,desRoleId):
	temp_dict = role.GetObj(EnumObj.ChaosDivinityData)
	temp_dict[3][desRoleId] = temp_dict.get(desRoleId,0) + 1

	role.SetObj(EnumObj.ChaosDivinityData,temp_dict)

def GetHireCount(role,desRoleId):
	temp_dict = role.GetObj(EnumObj.ChaosDivinityData)[3]
	return temp_dict.get(desRoleId,0)

def ClearHireCount(role):
	temp_dict = role.GetObj(EnumObj.ChaosDivinityData)
	temp_dict[3] = {}

	role.SetObj(EnumObj.ChaosDivinityData,temp_dict)

def CreateSubstituteTeam(role):
	'''
	创建替身组队
	'''
	#是否已经有队伍
	sTeam = role.GetTempObj(EnumTempObj.ChaosDivinityTeam)
	if sTeam:
		sTeam.sync_client()
		return True
	
	#状态判断
	if not Status.TryInStatus(role, EnumInt1.ST_Team):
		return False

	sTeam = ChaosDivinitySubTeam(role)
	role.SetTempObj(EnumTempObj.ChaosDivinityTeam, sTeam)

	sTeam.sync_client()


	return True

def SyncTeamInfo(role,index):
	'''
	同步混沌神域队伍信息
	'''
	team_list = TeamBase.CDTeamList.get(index,[])

	team_info_list = []
	for team in team_list:
		if IsCanSync(team):
			team_info_list.append(ExtractTeamInfo(team))

	role.SendObj(ChaosDivinity_TeamInfo, team_info_list)

def ExtractTeamInfo(team):
	'''
	混沌神域队伍信息
	'''
	#队伍ID，队长头像(性别, 职业, 进阶)，队长名，队长等级,队长战斗力,队伍人数
	return (team.team_id, team.leader.GetSex(), team.leader.GetCareer(), team.leader.GetGrade(), team.leader.GetRoleName(), team.leader.GetLevel(),team.leader.GetZDL(), len(team.members))

def SyncPassiveSkill(role):
	'''
	同步角色被动技能
	''' 
	
	role.SendObj(ChaosDivinity_PassiveSkillInfo,role.GetObj(EnumObj.ChaosDivinityData)[1])

def SyncActiveId(role):
	'''
	同步激活章节
	'''

	role.SendObj(ChaosDivinity_ActiveID,role.GetObj(EnumObj.ChaosDivinityData)[0])

def SyncRewardStar(role,index):
	'''
	同步评价星级
	'''
	star_dict = role.GetObj(EnumObj.ChaosDivinityData)[2]
	star = star_dict.get(index,-2)

	if star != -2:
		role.SendObj(ChaosDivinity_RewardStar,star)

def EveryMember(roles,operator):
	'''
	操作队员
	'''
	for index,role in enumerate(roles):
		if role:
			operator(index+1,role)

def PaneBroadCast(auto_message,msg_param):
	'''
	面板内广播
	'''
	global OpenPaneRoles
	for roleId in OpenPaneRoles:
		role = cRoleMgr.FindRoleByRoleID(roleId)
		if role:
			role.SendObj(auto_message,msg_param)

def GVE_ChaosDivinityBySub(role,index,role_fightdata,fight_ids,fight_type,afterfight,onleave = None, afterplay = None):
	'''
	替身参与战
	'''

	fight = Fight.Fight(fight_type)
	fight.restore = True

	left_camp,right_camp = fight.create_camp()
	leaderRoleId = role.GetRoleID()

	#修正组队位置
	for team_pos,(sub_role,_) in enumerate(role_fightdata):
		roledata,_ = Middle.GetRoleData(role,False,team_pos+1)
		role_fightdata[team_pos][1][0][Middle.GFightPos] = roledata[Middle.GFightPos]

	#修正被动技能
	for team_pos,(sub_role,_) in enumerate(role_fightdata):
		#主角
		if sub_role.role_id == leaderRoleId:
			for skill_id in role.GetObj(EnumObj.ChaosDivinityData)[1]:
				role_fightdata[team_pos][1][0][Middle.PassiveSkills].append((skill_id,0))
		#替身
		else:
			for skill_id in sub_role.skill_ids:
				role_fightdata[team_pos][1][0][Middle.PassiveSkills].append((skill_id,0))

	#创建战斗单位
	for team_pos,(sub_role,fight_data) in enumerate(role_fightdata):
		#主角
		if sub_role.role_id == leaderRoleId:
			left_camp.create_online_role_unit(role,role.GetRoleID(),fight_data,use_px = True)
		#替身
		else:
			left_camp.create_outline_role_unit(fight_data)

	#创建Boss
	for mcid in fight_ids:
		right_camp.create_monster_camp_unit(mcid)

	#战斗回调
	fight.after_fight_fun = afterfight		#战斗结束（所有的在线角色一定已经离场了）
	fight.on_leave_fun = onleave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_play_fun = afterplay		#客户端播放完毕（一定在战斗结束后触发）

	#user data
	fight.after_fight_param = FightState(index,[role],len(fight_ids))
	#开始战斗
	fight.start()

def GVE_ChaosDivinity(index,role_ids, fight_ids, fight_type, afterfight, onleave = None, afterplay = None):
	'''
	混沌神域GVE战斗
	'''

	fight = Fight.Fight(fight_type)
	fight.restore = True

	left_camp, right_camp = fight.create_camp()
	
	#获取角色战斗数据
	role_datas = {}
	def fetch_role_data(team_pos,role):
		role_datas[team_pos] = Middle.GetRoleData(role,False,team_pos)
	EveryMember(role_ids,fetch_role_data)

	#被动技能修正
	EveryMember(role_ids,
		lambda team_pos,role:
			map(lambda skill_id: role_datas[team_pos][0][Middle.PassiveSkills].append((skill_id,0)),role.GetObj(EnumObj.ChaosDivinityData)[1]))

	#战斗相关初始化
	EveryMember(role_ids,
		lambda team_pos,role:
			left_camp.create_online_role_unit(role,role.GetRoleID(),role_datas[team_pos],use_px = True))

	#创建Boss
	for mcid in fight_ids:
		right_camp.create_monster_camp_unit(mcid)

	#战斗回调
	fight.after_fight_fun = afterfight		#战斗结束（所有的在线角色一定已经离场了）
	fight.on_leave_fun = onleave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_play_fun = afterplay		#客户端播放完毕（一定在战斗结束后触发）

	#user data
	fight.after_fight_param = FightState(index,role_ids,len(fight_ids))
	#开始战斗
	fight.start()

def AfterFight(fight):
	'''
	 战斗结束（所有的在线角色一定已经离场了）
	'''
	fight_state = fight.after_fight_param

	#总共击杀Boss数
	killed_boss = 0

	if not fight_state.IsFinished(fight):
		killed_boss = fight_state.GetBossCnt() - len(fight.right_camp.wheels) - 1
	else:
		killed_boss = fight_state.GetBossCnt()

	with ChaosDivinity_Reward:
		#战斗奖励
		fight_state.EvaluateAll(fight.round,killed_boss,fight)

def AfterPlay(fight):
	'''
	客户端播放结束
	'''
	if not fight: return
	fight_state = fight.after_fight_param

	#解散替身队伍
	if len(fight_state.reward_roles) == 1:
		role = fight_state.reward_roles[0]
		if role.IsKick():
			return
		sTeam = role.GetTempObj(EnumTempObj.ChaosDivinityTeam)
		if sTeam:
			sTeam.dismiss(role)

#事件
def OnRoleLost(role,msg):
	'''
	玩家掉线
	'''
	global OpenPaneRoles
	OpenPaneRoles.discard(role.GetRoleID())

def OnRoleExit(role, param):
	team = role.GetTeam()
	if team:
		#有队伍则退出队伍
		if EnumTeamType.IsChaosDivinityType(team.team_type):
			#离开队伍
			team.Quit(role)
	else:
		sTeam = role.GetTempObj(EnumTempObj.ChaosDivinityTeam)
		if sTeam:
			sTeam.dismiss(role)

def RandomBoss():
	'''
	随机更新Boss
	'''
	global ChaosDivinityBossDict

	if DataKey not in ChaosDivinityBossDict.keys():
		ChaosDivinityBossDict[DataKey] = {}

	boss_dict = ChaosDivinityBossDict[DataKey]

	for index in ChaosDivinity_BossListDict.keys():
		cfg = ChaosDivinity_BossListDict[index]
		#随机多个不重复怪物
		boss_dict[index] = cfg.random_boss_list()

	ChaosDivinityBossDict.HasChange()

def OnEveryNewDay():
	'''
	每日更新
	'''
	#随机Boss表
	RandomBoss()

	global ChaosDivinityBossDict
	PaneBroadCast(ChaosDivinity_BossList,ChaosDivinityBossDict.get(DataKey,{}))

	#用本服缓存来更新排行榜
	global ControlRank,ControlRank_Old
	ControlRank_Old = ControlRank
	ControlRank = []

	#清空本服缓存
	global RealRankReward
	RealRankReward = (0,{})

	global RealRankReward2
	dayFlag,_ = RealRankReward2
	#控制今日排行数据已收到
	if dayFlag == ( cDateTime.Days() - 1 ):
		RealRankReward = RealRankReward2
		UpdateReleatedCache()
		RealRankReward2 = (0,{})

	global CDR
	with ChaosDivinity_LocalRank:
		AutoLog.LogBase(AutoLog.SystemID,AutoLog.eveChaosDivinityLocalRank,(cDateTime.Days(),CDR.data))
	#清空排行榜
	
	CDR.Clear()

def OnInitRolePyObj(role, param = None):
	'''
	初始化玩家obj
	@@@此时数据已经载入,不能覆盖
	'''
	pyobj = role.GetObj(EnumObj.ChaosDivinityData)

	#激活章节
	if 0 not in pyobj:
		#默认开启第一章
		pyobj[0] = 0

	#被动技能
	if 1 not in pyobj:
		pyobj[1] = set()

	#挑战星级
	if 2 not in pyobj:
		star_dict = {}
		for index in xrange(1,13): star_dict[index] = -1
		pyobj[2] = star_dict

	#雇佣记录
	#if 3 not in pyobj:
	#	pyobj[3] = {}

	#默认开启第一章
	role.SetObj(EnumObj.ChaosDivinityData,pyobj)

def OnSyncRoleOtherData(role, param):
	'''
	@param role:
	@param param:
	'''
	sTeam = role.GetTempObj(EnumTempObj.ChaosDivinityTeam)
	if sTeam:
		#显示战斗力排行前10玩家替身
		SyncSubRoleDataByZDL(role,10)
		sTeam.sync_client()

	#同步排行榜
	SyncAllRank(role)

def DailyClear(role, param):
	'''
	周一清理
	'''
	if cDateTime.WeekDay() != 1:
		return

	#清空雇佣记录
	ClearHireCount(role)

#客户端请求
def OpenPane(role,msg):
	'''
	打开面板
	'''
	#等级限制
	if role.GetLevel() < 120:
		return

	index = msg
	if not index:
		index = 1

	#同步开启章节
	SyncActiveId(role)
	#同步今日开启Boss
	global ChaosDivinityBossDict
	role.SendObj(ChaosDivinity_BossList,ChaosDivinityBossDict.get(DataKey,{}))
	#同步被动技能信息
	SyncPassiveSkill(role)
	#同步星级评价
	SyncRewardStar(role,index)
	#同步本服组队信息
	SyncTeamInfo(role,index)

	#同步替身组队
	sTeam = role.GetTempObj(EnumTempObj.ChaosDivinityTeam)
	if sTeam:
		sTeam.sync_client()

	global OpenPaneRoles
	OpenPaneRoles.add(role.GetRoleID())

def ClosePane(role,msg):
	'''
	关闭面板
	'''
	global OpenPaneRoles
	OpenPaneRoles.discard(role.GetRoleID())

def OnWorldCall(role,msg):
	'''
	世界邀请
	'''
	team = role.GetTeam()
	if not team:
		return

	if not EnumTeamType.IsChaosDivinityType(team.team_type):
		return

	#世界邀请CD未冷却
	if role.GetCD(EnumCD.ChaosDivinityWorldCall) > 0:
		return

	if not IsCanInvite(role):
		return

	#设置邀请CD
	role.SetCD(EnumCD.ChaosDivinityWorldCall, 20)
	#传闻
	index = EnumTeamType.GetCDIndexByTeamType(team.team_type)
	tips = GlobalPrompt.GetCD_WorldCall_Tips(index)

	cRoleMgr.Msg(7, 0, tips % (team.leader.GetRoleName(), 3 - len(team.members), team.team_id))


def OnInviteRole(role,msg):
	'''
	好友邀请
	'''
	if not msg: return

	team = role.GetTeam()
	if not team:
		return

	if not team.CanInvite(role):
		return

	desRoleId = msg
	#玩家无法被邀请
	desRole = cRoleMgr.FindRoleByRoleID(desRoleId)
	if not desRole:
		role.Msg(2, 0, GlobalPrompt.TEAM_NOT_ONLINE_PROMPT)
		return
	elif desRole.HasTeam():
		role.Msg(2, 0, GlobalPrompt.TEAM_HAS_TEAM_PROMPT)
		return

	#无法发出邀请
	if not IsCanInvite(role):
		return

	if not team.CanBeInvite(desRole):
		return

	if EnumTeamType.IsChaosDivinityType(team.team_type):
		index = team.team_type - EnumTeamType.T_ChaosDivinity1 + 1
		#队伍id, 玩家名
		desRole.SendObjAndBack(ChaosDivinity_InviteInfo, (role.GetRoleName(),index), 120, InviteBack, team.team_id)

def InviteBack(role, callargv, regparam):
	'''
	邀请回调
	'''
	teamId = regparam

	#拒绝邀请
	if callargv != 1:
		return

	team =  TeamBase.GetTeamByTeamID(teamId)
	if not team:
		role.Msg(2, 0, GlobalPrompt.TEAM_NOT_EXIST_PROMPT)
		return

	if not team.CanJoin(role):
		return

	#加入队伍
	team.AddMember(role)

def OnFightStart(role,msg):
	'''
	战斗开始
	'''

	if not msg :
		return

	#章节索引
	backId,index = msg

	max_challengeId = GetActiveId(role) + 1
	if index > max_challengeId:
		return

	#开始GVE车轮战
	global ChaosDivinityBossDict
	boss_dict = ChaosDivinityBossDict.get(DataKey,{})
	boss_list = boss_dict.get(index,[])

	fight_ids = []
	for bossId in boss_list:
		campId = ChaosDivinity_BossInfoDict.get(bossId,-1)
		if campId == -1:
			print "GE_EXC,no campId in ChaosDivinity_BossInfoDict where bossId(%s)"% bossId
			return
		fight_ids.append(campId)

	if not len(fight_ids):
		print "GE_EXC, no boss in ChaosDivinityBossDict where index(%s)" % index
		return

	cfg = ChaosDivinity_BossListDict.get(index,None)
	if not cfg:
		return

	team = role.GetTeam()

	#真身组队战
	if team:
		if not IsCanStart(role):
			return
		GVE_ChaosDivinity(index,team.members,fight_ids,cfg.fightType,AfterFight)
	else:
		sTeam = role.GetTempObj(EnumTempObj.ChaosDivinityTeam)
		if sTeam and not sTeam.is_full():
			return

		#替身组队战
		if sTeam:
			roleFightDataList = []
			for team_pos,sub_role in enumerate(sTeam.members):
				roleFightData  = None
				#主角
				if sub_role.role_id == role.GetRoleID():
					roleFightData = Middle.GetRoleData(role,False,team_pos)
				else:
					import copy
					FightData = RoleFightData.GetRoleFightData(sub_role.role_id)
					roleFightData = copy.deepcopy(FightData)
					
				if not roleFightData:
					#没有战斗数据
					continue
				roleFightDataList.append((sub_role, roleFightData))
			GVE_ChaosDivinityBySub(role,index,roleFightDataList,fight_ids,cfg.fightType,AfterFight,afterplay = AfterPlay)

	role.CallBackFunction(backId, None)

def OnPassiveSkillSelected(role,msg):
	'''
	选择被动技能
	'''
	if not msg: return

	client_skill_ids = msg

	skill_ids = []
	for skill_id in client_skill_ids:
		if skill_id in ChaosDivinity_PassiveSkillList:
			if len(skill_ids) < 2 and skill_id not in skill_ids:
				skill_ids.append(skill_id)
			else:
				break

	SetRoleSkill(role,skill_ids)

	#同步被动技能信息
	SyncPassiveSkill(role)

	team = role.GetTeam()
	if team: team.SyncClient()		#强制同步队员信息

	sTeam = role.GetTempObj(EnumTempObj.ChaosDivinityTeam)
	if sTeam:
		sTeam.SyncRole()
		sTeam.sync_client()

def OnNoReward(role,msg):
	'''
	设置无奖励模式
	'''	

	role.SetI1(EnumInt1.ChaosDivinityNoReward,int(msg > 0))

def OnFastJoin(role,msg):
	'''
	请求快速组队
	'''
	tIndex = msg
	teamList = TeamBase.CDTeamList.get(tIndex)
	if teamList is None:
		return
	#状态判断
	if not Status.CanInStatus(role, EnumInt1.ST_Team):
		return
	
	for team in teamList:
		if Status.IsInStatus(team.leader, EnumInt1.ST_FightStatus):
			continue
		if not team.CanJoin(role):
			continue
		team.Join(role)

def SyncSubRoleDataByZDL(role,up_to_zdl_rank):
	'''
	根据战斗力同步替身数据
	'''
	memberList = UnionMgr.GetZDLRank(role,up_to_zdl_rank,EnumGameConfig.ChaosDivinityLevel)
	#没有数据
	if not memberList or not len(memberList):
		return

	role.SendObj(ChaosDivinity_SubStituteData,memberList)

def OnCreateSubstituteTeam(role,msg):
	'''
	请求替身组队
	'''
	if not CreateSubstituteTeam(role):
		return

	#显示战斗力排行前10玩家替身
	SyncSubRoleDataByZDL(role,10)

def OnInviteSubstitute(role,msg):
	'''
	邀请替身组队
	'''
	if not msg:
		return

	backId,inviteRoleId = msg

	unionObj = role.GetUnionObj()
	if not unionObj:
		return

	sTeam = role.GetTempObj(EnumTempObj.ChaosDivinityTeam)
	if not sTeam:
		return

	#队伍中已有该ID
	if sTeam.IsInTeam(inviteRoleId):
		return

	if sTeam.is_full():
		return

	if role.GetBindRMB() < EnumGameConfig.ChaosDivinitySubRMB:
		return
	
	sTeam.join(unionObj,inviteRoleId)

	#消耗固定魔晶
	with ChaosDivinity_InviteSub:
		role.DecBindRMB(EnumGameConfig.ChaosDivinitySubRMB)

	role.CallBackFunction(backId, None)

def OnKickSubstitute(role,msg):
	'''
	踢掉替身队员
	'''
	if not msg:
		return

	desRoleId = msg
	if role.GetRoleID() == desRoleId:
		return
	
	sTeam = role.GetTempObj(EnumTempObj.ChaosDivinityTeam)
	if not sTeam:
		return

	sTeam.kick(desRoleId)

def OnDismissSubstitute(role,msg):
	'''
	解散替身队伍
	'''
	sTeam = role.GetTempObj(EnumTempObj.ChaosDivinityTeam)
	if not sTeam:
		return

	sTeam.dismiss(role)

def OnSubstituteChangePos(role,msg):
	'''
	请求替身交换位置
	'''

	pos1,pos2 = msg
	#位置是否合法
	if pos1 not in (1,2,3) or pos2 not in (1,2,3):
		return
	if pos1 == pos2:
		return
	
	sTeam = role.GetTempObj(EnumTempObj.ChaosDivinityTeam)
	if not sTeam:
		return
	
	cnt = len(sTeam.members)
	if pos1 > cnt or pos2 > cnt:
		return
	
	#交换两个位置
	sTeam.members[pos1-1], sTeam.members[pos2-1] = sTeam.members[pos2-1], sTeam.members[pos1-1]
	
	sTeam.sync_client()

def OnSelectPassiveSkillForSub(role,msg):
	'''
	请求为替身选择被动技能
	'''
	if not msg: return

	desRoleId,client_skill_ids = msg

	sTeam = role.GetTempObj(EnumTempObj.ChaosDivinityTeam)
	if not sTeam:
		return

	if not sTeam.IsInTeam(desRoleId):
		return

	#被动技能验证
	skill_ids = []
	for skill_id in client_skill_ids:
		if skill_id in ChaosDivinity_PassiveSkillList:
			if len(skill_ids) < 2 and skill_id not in skill_ids:
				skill_ids.append(skill_id)
			else:
				break

	sub_role = sTeam.GetSubRole(desRoleId)
	if sub_role:
		sub_role.skill_ids = skill_ids

	sTeam.SyncMember()
	sTeam.sync_client()

def OnFightEnd(role,msg):
	'''
	客户端请求结束战斗
	'''
	#不在战斗状态
	if not Status.IsInStatus(role, EnumInt1.ST_FightStatus):
		return

	is_leader = False
	#身份验证
	team = role.GetTeam()
	if team and team.leader == role:
		is_leader = True

	sTeam = role.GetTempObj(EnumTempObj.ChaosDivinityTeam)
	if sTeam:
		is_leader = True

	if not is_leader:
		return

	#结束战斗
	camp = role.GetTempObj(EnumTempObj.FightCamp)
	if not camp:
		return
	camp.fight.end(-1)

def GetLogicRank():
	#获取本服前50名数据
	global CDR
	return CDR.data.values()

def OnControlRequestRank(sessionid, msg):
	'''
	#控制进程请求获取本服前50名数据
	@param sessionid:
	@param msg:
	'''
	if not CDR.returnDB:
		return
	backid, _ = msg
	ControlProxy.CallBackFunction(sessionid, backid, (cProcess.ProcessID, GetLogicRank()))

def SyncAllRank(role):
	global ControlRank,ControlRank_Old,RankRewardID

	IsCanReward = 0
	if RankRewardID != -1:
		IsCanReward = 1
	role.SendObj(ChaosDivinity_Rank,{0:ControlRank,1:ControlRank_Old,2:IsCanReward})

def OnRequestRank(role,msg):
	'''
	客户端请求查看排行榜
	'''
	if role.GetLevel() < EnumGameConfig.ChaosDivinityLevel:
		return

	SyncAllRank(role)

def OnControlSyncRank(sessionid, msg):
	'''
	控制进程更新今日排行榜
	'''
	global ControlRank
	ControlRank = msg

def OnControlSyncAll(sessionid, msg):
	'''
	控制进程更新今日、昨日排行榜
	'''
	global ControlRank,ControlRank_Old,RealRankReward
	ControlRank,ControlRank_Old,RealRankReward = msg

	global RealRankReward2
	RealRankReward2 = (0,{})

	UpdateReleatedCache()

def UpdateRankReward():
	global RankRewardID,LocalRank,NewRealRankReward

	_,rewardDict = NewRealRankReward
	rewardId = rewardDict.get(cProcess.ProcessID,-1)

	#本服可领奖
	if rewardId != -1:
		RankRewardID = rewardId[0]
		LocalRank = rewardId[1]
	else:
		RankRewardID = -1
		LocalRank = 0

def UpdateReleatedCache():
	'''
	更新本服缓存
	'''
	#查找本服是否可领奖
	global RankRewardID,LocalRank,RealRankReward
	_,rewardDict = RealRankReward
	rewardId = rewardDict.get(cProcess.ProcessID,-1)

	#本服可领奖
	if rewardId != -1:
		RankRewardID = rewardId[0]
		LocalRank = rewardId[1]
	else:
		RankRewardID = -1
		LocalRank = 0

	global ControlRank,ControlRank_Old
	IsCanReward = 0
	if RankRewardID != -1:
		IsCanReward = 1
	PaneBroadCast(ChaosDivinity_Rank,{0:ControlRank,1:ControlRank_Old,2:IsCanReward})

def OnForwardDataReceived():
	'''
	'''
	global RealRankReward2
	dayFlag,_ = RealRankReward2

	#本地服务器已跨天
	if dayFlag == (cDateTime.Days() - 1):
		#更新本服缓存
		global RealRankReward
		RealRankReward = RealRankReward2
		UpdateReleatedCache()
		#重置缓存
		RealRankReward2 = (0,{})

def OnRankRewardUpdated(sessionid, msg):
	'''
	控制进程通知逻辑进程排行榜奖励已更新
	此时本地服务器时间可能没有跨天，故先缓存数据
	'''
	global RealRankReward2
	RealRankReward2 = msg

	OnForwardDataReceived()


def OnReward(role,msg):
	'''
	请求领取奖励
	'''
	if role.GetLevel() < EnumGameConfig.ChaosDivinityLevel:
		return

	global RankRewardID
	if RankRewardID == -1:
		return

	cfg = ChaosDivinity_RankRewardDict.get(RankRewardID,None)
	if not cfg:
		return

	role_names = []
	#系统广播
	global RealRankReward
	_,rewardDict = RealRankReward
	rewardId = rewardDict.get(cProcess.ProcessID,-1)
	if rewardId != -1:
		role_names = rewardId[2]
	else:
		return

	if role.GetDI1(EnumDayInt1.ChaosDivinityReward):
		return

	tips = GlobalPrompt.Reward_Tips
	#发奖
	with ChaosDivinity_RankReward:
		#道具奖励
		for item in cfg.rewardItem:
			role.AddItem(*item)
			tips += GlobalPrompt.Item_Tips % item
		#历练值奖励
		if cfg.rewardExp > 0:
			role.IncI32(EnumInt32.SealLiLianAmounts, cfg.rewardExp)
			tips += GlobalPrompt.SealExp_Tips % cfg.rewardExp
		#已领取奖励
		role.SetDI1(EnumDayInt1.ChaosDivinityReward,1)

		role.Msg(2,0,tips)

	global LocalRank
	#系统广播
	if LocalRank:
		cRoleMgr.Msg(1, 0, GlobalPrompt.CD_RankReward_Tips % (role.GetRoleName(),LocalRank,role_names[0],role_names[1],role_names[2]))

def OnTYRankUpdate(sessionid,msg):
	'''
	今日、昨日排行榜更新
	'''
	global ControlRank,ControlRank_Old
	ControlRank,ControlRank_Old = msg

	global RankRewardID

	IsCanReward = 0
	if RankRewardID != -1:
		IsCanReward = 1
	PaneBroadCast(ChaosDivinity_Rank,{0:ControlRank,1:ControlRank_Old,2:IsCanReward})


def TryUpdate():
	'''
	'''
	if not CDR.returnDB:
		#数据没有完全载回
		return
	#向控制进程请求跨服排行榜数据
	ControlProxy.SendControlMsg(PyMessage.Control_ChaosDivinityLogicRequest, None)


def AfterBossListLoaded():
	'''
	持久化数据初始化
	'''
	global ChaosDivinityBossDict

	if ChaosDivinityBossDict.get(DayKey,-1) != cDateTime.Days():
		#清空数据
		ChaosDivinityBossDict.clear()
		#更新日期戳
		ChaosDivinityBossDict[DayKey] = cDateTime.Days()
		#重新随机一次Boss列表
		RandomBoss()

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_InitRolePyObj, OnInitRolePyObj)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		Event.RegEvent(Event.Eve_BeforeExit, OnRoleExit)
		Event.RegEvent(Event.Eve_ClientLost, OnRoleLost)
		cComplexServer.RegAfterNewDayCallFunction(OnEveryNewDay)
		Init.InitCallBack.RegCallbackFunction(TryUpdate)

		#请求逻辑进程的排行榜数据(回调)
		cComplexServer.RegDistribute(PyMessage.Control_RequestLogicChaosDivinityRank, OnControlRequestRank)
		#控制进程向逻辑进程同步今日排行榜数据
		#cComplexServer.RegDistribute(PyMessage.Control_SyncChaosDivinityTodayRank, OnControlSyncRank)
		#控制进程向逻辑进程同步排行榜所有数据
		cComplexServer.RegDistribute(PyMessage.Control_SyncChaosDivinityAllRank, OnControlSyncAll)
		#控制进程通知逻辑进程排行榜奖励已更新
		cComplexServer.RegDistribute(PyMessage.Control_RankRewardUpdated, OnRankRewardUpdated)
		#控制进程向逻辑进程同步今日、昨日排行榜数据
		#cComplexServer.RegDistribute(PyMessage.Control_SyncChaosDivinityTYRank, OnTYRankUpdate)

		#神域通关排行榜
		CDR = CDBestChallageRank()

		#每日Boss数据
		ChaosDivinityBossDict = Contain.Dict("ChaosDivinityBossList", (2038, 1, 1), AfterBossListLoaded)	#{index:[mcid]}

		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChaosDivinity_RequestOpenPane", "请求打开混沌神域面板"), OpenPane)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChaosDivinity_RequestClosePane", "请求关闭混沌神域面板"), ClosePane)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChaosDivinity_RequestWorldCall", "请求混沌神域世界邀请"), OnWorldCall)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChaosDivinity_RequestRoleInvite", "请求混沌神域好友邀请"), OnInviteRole)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChaosDivinity_Request", "请求混沌神域无奖励模式"), OnNoReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChaosDivinity_RequestStart", "请求混沌神域开始"), OnFightStart)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChaosDivinity_FastJoin", "请求混沌神域快速组队"), OnFastJoin)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChaosDivinity_RequestSelectPassiveSkill", "请求选择被动技能"), OnPassiveSkillSelected)

		#Z
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChaosDivinity_Create_Substitute_Team", "请求混沌神域替身组队"), OnCreateSubstituteTeam)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChaosDivinity_Invite_Substitute", "请求混沌神域邀请替身"), OnInviteSubstitute)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChaosDivinity_Kick_Substitute", "请求混沌神域踢掉替身"), OnKickSubstitute)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChaosDivinity_Dismiss_Substitute_Team", "请求混沌神域解散替身队伍"), OnDismissSubstitute)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChaosDivinity_Substitute_Team_Change_Pos", "请求混沌神域交换替身位置"), OnSubstituteChangePos)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChaosDivinity_FightEnd", "请求结束战斗"), OnFightEnd)

		#排行榜相关
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChaosDivinity_RequestRank", "混沌神域请求排行榜"), OnRequestRank)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChaosDivinity_RequestReward", "混沌神域请求领取奖励"), OnReward)
