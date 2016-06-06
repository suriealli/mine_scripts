#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Union.UnionFB")
#===============================================================================
# 公会副本
#===============================================================================
import random
import Environment
import cDateTime
import cRoleDataMgr
import cRoleMgr
from Common.Message import AutoMessage
from Common.Other import EnumFightStatistics, GlobalPrompt, EnumGameConfig
from ComplexServer.Log import AutoLog
from ComplexServer.Time import Cron
from Game.Activity.SevenDayHegemony import SDHFunGather, SDHDefine
from Game.Fight import FightEx
from Game.Role import Status, Event
from Game.Role.Data import EnumInt8, EnumInt1, EnumInt16, EnumTempObj
from Game.RoleFightData import RoleFightData
from Game.Scene import PublicScene
from Game.SystemRank import SystemRank
from Game.Team import TeamBase, EnumTeamType
from Game.Union import UnionConfig, UnionDefine
from Game.VIP import VIPConfig


if "_HasLoad" not in dir():
	UNION_FB_ACTIVATE_LEVEL = 60	#公会副本激活等级
	UNION_FB_DAY_CNT = 3			#公会副本每天次数
	UNION_FB_ELITE_DAY_CNT = 1		#公会副本精英每天次数
	UNION_FB_LEVEL_CNT = 6			#公会副本关卡数量
	UNION_FB_UPDATE_HOUR = 14		#公会副本次数14点更新
	
	#消息
	Union_FB_Show_Panel = AutoMessage.AllotMessage("Union_FB_Show_Panel", "通知客户端显示公会副本面板")
	Union_FB_Show_Teams = AutoMessage.AllotMessage("Union_FB_Show_Teams", "通知客户端显示公会副本所有组队信息")
	Union_FB_Show_Union_Online_Members = AutoMessage.AllotMessage("Union_FB_Show_Union_Online_Members", "通知客户端显示公会副本公会在线成员信息")
	Union_FB_Sync_All_Data = AutoMessage.AllotMessage("Union_FB_Sync_All_Data", "通知客户端公会副本所有数据")
	Union_FB_Call_Team_Member_Cnt_Change = AutoMessage.AllotMessage("Union_FB_Call_Team_Member_Cnt_Change", "通知客户端通知队伍成员公会副本行动力改变")
	
	Union_FB_Show_Substitute = AutoMessage.AllotMessage("Union_FB_Show_Substitute", "通知客户端显示公会副本替身")
	Union_FB_Sync_Substitute_Team = AutoMessage.AllotMessage("Union_FB_Sync_Substitute_Team_Data", "通知客户端公会副本替身队伍数据")
	
class UnionFBSubstituteTeam(object):
	def __init__(self, role):
		self.role = role
		self.union_obj = role.GetUnionObj()
		self.members = [role.GetRoleID()]
		self.max_member_cnt = 3
		self.memberDataDict = {role.GetRoleID():[role.GetRoleName(), role.GetSex(), role.GetCareer(), role.GetGrade()]}
		
	def sync_client(self):
		dataList = []
		
		for roleId in self.members:
			name, sex, career, grade = self.memberDataDict[roleId]
			dataList.append((roleId, name, sex, career, grade))
				
		self.role.SendObj(Union_FB_Sync_Substitute_Team, dataList)
		
	def get_member_data(self):
		pass
		
	def join(self, roleId):
		if roleId in self.members:
			return
		
		if self.is_full() is True:
			return
		
		sex, career, grade = self.union_obj.get_member_data(roleId, UnionDefine.M_PICTURE_IDX)
		self.members.append(roleId)
		
		self.memberDataDict[roleId] = [self.union_obj.get_member_data(roleId, UnionDefine.M_NAME_IDX), sex, career, grade]
		
		self.sync_client()
		
	def kick(self, roleId):
		if roleId in self.members:
			self.members.remove(roleId)
			del self.memberDataDict[roleId]
			
		self.sync_client()
		
	def dismiss(self, role):
		role.SetTempObj(EnumTempObj.UnionFBSubstituteTeam, None)
		
		#退出组队状态
		Status.Outstatus(role, EnumInt1.ST_Team)
			
	def is_full(self):
		if len(self.members) >= self.max_member_cnt:
			return True
		return False
			

def OpenAll(role, fbId):
	'''
	GM指令开启所有副本关卡
	@param role:
	@param fbId:
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	if fbId not in unionObj.fb:
		unionObj.fb[fbId] = {}
	
	for x in xrange(UNION_FB_LEVEL_CNT):
		levelId = x + 1
		
		#配置
		fbConfig = UnionConfig.UNION_FB_MONSTER.get((fbId, levelId))
		if not fbConfig:
			return
		
		unionObj.fb[fbId][levelId] = fbConfig.nextLevelNeedOccupation
	
	#配置
	nextFBConfig = UnionConfig.UNION_FB_MONSTER.get((fbId + 1, 1))
	if not nextFBConfig:
		return
	unionObj.fb[fbId + 1] = {1: 0}

def IsUpdateUnionFBCnt(role):
	'''
	是否更新公会副本次数
	@param role:
	'''
	#等级限制
	if role.GetLevel() < UNION_FB_ACTIVATE_LEVEL:
		return
	
	days = cDateTime.Days()
	lastUpdataDays = role.GetI16(EnumInt16.UnionFBCntUpdateDays)
	if days <= lastUpdataDays:
		return
	
	#判断是不是第二天
	if lastUpdataDays + 1 == days:
		#是否超过了14点
		if cDateTime.Hour() < UNION_FB_UPDATE_HOUR:
			return
	
	#重置公会副本行动力
	role.SetI8(EnumInt8.UnionFBCnt, UNION_FB_DAY_CNT)
	#重置精英收益次数
	role.SetI1(EnumInt1.UnionFBElite, UNION_FB_ELITE_DAY_CNT)
	#重置公会副本购买次数
	role.SetI8(EnumInt8.UnionFBBuyCnt, 0)
	#设置更新时间
	role.SetI16(EnumInt16.UnionFBCntUpdateDays, days)
		
	#判断是否离线超过两天
	if days - lastUpdataDays >= 2:
		#是否超过了14点
		if cDateTime.Hour() < UNION_FB_UPDATE_HOUR:
			#设置更新时间
			role.SetI16(EnumInt16.UnionFBCntUpdateDays, days - 1)
	
def InUnionFB(role, fbId):
	'''
	进入公会副本
	@param role:
	@param fbId:
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	#还没有开通对应章节
	if fbId not in unionObj.fb:
		return
	
	#配置
	fbConfig = UnionConfig.UNION_FB_BASE.get(fbId)
	if not fbConfig:
		return
	
	#能否进入公会副本状态
	if not Status.CanInStatus(role, EnumInt1.ST_UnionFB):
		return
	
	#传送
	x, y = fbConfig.defaultPos
	role.Revive(fbConfig.sceneId, x, y)
	
def UnionFBFight(role, levelId):
	#战斗状态
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	fbId = role.GetI8(EnumInt8.UnionFBId)
	if not fbId:
		return
	
	if levelId == 0:
		#精英
		if not role.GetI1(EnumInt1.UnionFBElite):
			#次数不足
			return
		
		#只能单人挑战
		team = role.GetTeam()
		if team:
			return
		
		#配置
		fbConfig = UnionConfig.UNION_FB_BASE.get(fbId)
		if not fbConfig:
			return
		
		#战斗
		FightEx.PVE(role, fbConfig.fightType, fbConfig.eliteCampId, AfterFightForElite, regParam = fbId)
	else:
		#普通关卡
		
		#是否激活了对应关卡
		unionObj = role.GetUnionObj()
		if not unionObj:
			return
		if fbId not in unionObj.fb:
			return
		if levelId not in unionObj.fb[fbId]:
			return
		
		#配置
		fbConfig = UnionConfig.UNION_FB_MONSTER.get((fbId, levelId))
		if not fbConfig:
			return
		
		#获取队伍
		team = role.GetTeam()
		if team:
			#判断组队类型
			if team.team_type != EnumTeamType.T_UnionFB:
				return
			
			#队伍能否进入战斗状态
			if not Status.CanInStatus_Roles(team.members, EnumInt1.ST_FightStatus):
				return
			
			#提示(如果勾选了不消耗次数)
			for member in team.members:
				if member.GetI1(EnumInt1.UnionFBNotCost):
					member.Msg(2, 0, GlobalPrompt.UNION_FB_NO_COST)
			
			#车轮战
			FightEx.PVE_UnionFB(team.leader, team.members, fbConfig.fightType, fbConfig.monsterCampIdList, AfterFightForLevel, regParam = (fbId, levelId, unionObj))
		else:
			#替身队伍
			sTeam = role.GetTempObj(EnumTempObj.UnionFBSubstituteTeam)
			
			if not sTeam:
				return
			
			roleFightDataList = []
			for memberRoleId in sTeam.members:
				roleFightData = RoleFightData.GetRoleFightData(memberRoleId)
				if not roleFightData:
					#没有战斗数据
					continue
				roleFightDataList.append((memberRoleId, roleFightData))
	
			FightEx.PVE_UnionFB_Subsitute(role, roleFightDataList, fbConfig.fightType, fbConfig.monsterCampIdList, AfterFightForLevel, regParam = (fbId, levelId, unionObj))
	
def BuyCnt(role):
	'''
	公会副本购买次数
	@param role:
	'''
	#不是贵族无法购买次数
	vip = role.GetVIP()
	if vip == 0:
		return
	
	vipConfig = VIPConfig._VIP_BASE.get(vip)
	if not vipConfig:
		return
	
	cnt = role.GetI8(EnumInt8.UnionFBBuyCnt)
	#已经达到最大购买次数
	if cnt >= vipConfig.unionFBBuyCnt:
		return
	
	#购买次数配置表
	cntConfig = UnionConfig.UNION_FB_BUY_CNT.get(cnt + 1)
	if not cntConfig:
		return
	
	#判断RMB
	if role.GetRMB() < cntConfig.needRMB:
		return
	
	#扣除
	role.DecRMB(cntConfig.needRMB)
	
	#购买次数增加
	role.IncI8(EnumInt8.UnionFBBuyCnt, 1)
	
	#公会副本次数增加
	role.IncI8(EnumInt8.UnionFBCnt, 1)
	
def UnionFBSetNotCost(role):
	'''
	公会副本设置不消耗次数
	@param role:
	'''
	if role.GetI1(EnumInt1.UnionFBNotCost):
		role.SetI1(EnumInt1.UnionFBNotCost, 0)
	else:
		role.SetI1(EnumInt1.UnionFBNotCost, 1)
		
def UnionFBSetAutoAcceptTeamInvite(role):
	'''
	公会副本设置自动接受组队邀请
	@param role:
	'''
	if role.GetI1(EnumInt1.TeamAutoAcceptInvite):
		role.SetI1(EnumInt1.TeamAutoAcceptInvite, 0)
	else:
		role.SetI1(EnumInt1.TeamAutoAcceptInvite, 1)
		
#===============================================================================
# 替身组队
#===============================================================================
def UnionFBCreateSubstituteTeam(role):
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	#是否已经有队伍
	sTeam = role.GetTempObj(EnumTempObj.UnionFBSubstituteTeam)
	if sTeam:
		sTeam.sync_client()
		return
	
	#状态判断
	if not Status.TryInStatus(role, EnumInt1.ST_Team):
		return
	
	sTeam = UnionFBSubstituteTeam(role)
	
	role.SetTempObj(EnumTempObj.UnionFBSubstituteTeam, sTeam)
	
	sTeam.sync_client()
	
def UnionFBKickSubstitute(role, desRoleId):
	if role.GetRoleID() == desRoleId:
		return
	
	sTeam = role.GetTempObj(EnumTempObj.UnionFBSubstituteTeam)
	if not sTeam:
		return
	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	sTeam.kick(desRoleId)
	
def UnionFBInviteSubstitute(role, inviteRoleId):
	if role.GetRoleID() == inviteRoleId:
		return
	
	sTeam = role.GetTempObj(EnumTempObj.UnionFBSubstituteTeam)
	if not sTeam:
		return
	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	daysDict = unionObj.get_other_data(UnionDefine.O_SUPER_CARDS_DAYS_IDX)
	outDateDays = daysDict.get(inviteRoleId, 0)
	nowDays = cDateTime.Days()
	if nowDays > outDateDays:
		return
	
	sTeam.join(inviteRoleId)
	
	#替身玩家是否在线
	inviteRole = cRoleMgr.FindRoleByRoleID(inviteRoleId)
	if inviteRole:
		#提示
		inviteRole.Msg(2, 0, GlobalPrompt.UNION_FB_INVITE_SUBSTITUTE % role.GetRoleName())
	
def UnionFBSubstituteTeamChangePos(role, pos1, pos2):
	#位置是否合法
	if pos1 not in (1,2,3) or pos2 not in (1,2,3):
		return
	if pos1 == pos2:
		return
	
	sTeam = role.GetTempObj(EnumTempObj.UnionFBSubstituteTeam)
	if not sTeam:
		return
	
	cnt = len(sTeam.members)
	if pos1 > cnt or pos2 > cnt:
		return
	
	#交换两个位置
	sTeam.members[pos1 - 1], sTeam.members[pos2 - 1] = sTeam.members[pos2 - 1], sTeam.members[pos1 - 1]
	
	sTeam.sync_client()
	
#===============================================================================
# reward
#===============================================================================
def EliteReward(role, fbId, fightObj):
	'''
	精英奖励
	@param role:
	@param fbId:
	'''
	roleId = role.GetRoleID()
	
	#是否有收益次数
	if not role.GetI1(EnumInt1.UnionFBElite):
		return
	
	fbConfig = UnionConfig.UNION_FB_BASE.get(fbId)
	if not fbConfig:
		return
	
	#扣除收益次数
	role.SetI1(EnumInt1.UnionFBElite, 0)
	
	
	#YY防沉迷对奖励特殊处理
	yyAntiFlag = role.GetAnti()
	if yyAntiFlag == 1:
		rewardMoney = fbConfig.rewardMoney_fcm
		rewardItemList = fbConfig.rewardItemList_fcm
	elif yyAntiFlag == 0:
		rewardMoney = fbConfig.rewardMoney
		rewardItemList = fbConfig.rewardItemList
	else:
		rewardMoney = 0
		rewardItemList = ()
		role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
	
	#奖励
	if rewardMoney:
		role.IncMoney(rewardMoney)
		fightObj.set_fight_statistics(roleId, EnumFightStatistics.EnumMoney, rewardMoney)
	showItemList = []
	for item in rewardItemList:
		role.AddItem(*item)
		showItemList.append(item)
	fightObj.set_fight_statistics(roleId, EnumFightStatistics.EnumItems, showItemList)
		
def LevelReward(role, fbId, levelId, fightObj):
	'''
	关卡奖励
	@param role:
	@param fbId:
	@param levelId:
	'''
	roleId = role.GetRoleID()
	
	levelConfig = UnionConfig.UNION_FB_MONSTER.get((fbId, levelId))
	if not levelConfig:
		return
	
	#扣除收益次数
	role.DecI8(EnumInt8.UnionFBCnt, 1)
	#YY防沉迷对奖励特殊处理
	yyAntiFlag = role.GetAnti()
	if yyAntiFlag == 1:
		rewardMoney = levelConfig.rewardMoney_fcm
		rewardItemList = levelConfig.rewardItemList_fcm
	elif yyAntiFlag == 0:
		rewardMoney = levelConfig.rewardMoney
		rewardItemList = levelConfig.rewardItemList
	else:
		rewardMoney = 0
		rewardItemList = ()
		role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
	#奖励
	if rewardMoney:
		role.IncMoney(rewardMoney)
		fightObj.set_fight_statistics(roleId, EnumFightStatistics.EnumMoney, rewardMoney)
	showItemList = []
	for item in rewardItemList:
		role.AddItem(*item)
		showItemList.append(item)
		
	#概率奖励
	if levelConfig.oddsRewardItem:
		ri = random.randint(1, 10000)
		if ri <= levelConfig.odds:
			role.AddItem(*levelConfig.oddsRewardItem)
			showItemList.append(levelConfig.oddsRewardItem)
	
	fightObj.set_fight_statistics(roleId, EnumFightStatistics.EnumItems, showItemList)
	
	Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_UnionFB, 1))
	
	#版本判断
	if Environment.EnvIsNA():
		#开服活动
		kaifuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
		kaifuActMgr.union_fb(fbId, levelId)
		
def IncUnionFBOccupation(role, fbId, levelId):
	'''
	增加公会副本占领度
	@param role:
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	#公会副本是否存在
	if fbId not in unionObj.fb:
		return
	if levelId not in unionObj.fb[fbId]:
		return
	
	occupation = unionObj.fb[fbId][levelId]
	#关卡配置
	levelConfig = UnionConfig.UNION_FB_MONSTER.get((fbId, levelId))
	if not levelConfig:
		return
	
	#占领度已满
	if occupation >= levelConfig.nextLevelNeedOccupation:
		return
	
	nowOccupation = occupation + 1
	unionObj.fb[fbId][levelId] = nowOccupation
	
	#占领度是否刚好满
	if nowOccupation == levelConfig.nextLevelNeedOccupation:
		#是否已经是最大的关卡
		if levelId >= UNION_FB_LEVEL_CNT:
			#是否已经激活了下一个副本
			if fbId >= UnionConfig.UNION_FB_ID_MAX:
				#已经是最后一个副本
				return
			else:
				#激活下一个副本
				unionObj.fb[fbId + 1] = {1: 0}
		else:
			#激活本副本下一个关卡
			unionObj.fb[fbId][levelId + 1] = 0
				
	#保存
	unionObj.HasChange()
	#更新公会副本排行榜
	SystemRank.UpdateUnionFBRank(unionObj)
	
#===============================================================================
# 显示
#===============================================================================
def ShowUnionFBPanel(role):
	'''
	显示公会副本面板
	@param role:
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	#生成副本相关信息
	if not unionObj.fb:
		#生成副本第一章节第一个关卡
		unionObj.fb[1] = {1: 0}
		#保存
		unionObj.HasChange()
	
	#同步客户端
	role.SendObj(Union_FB_Show_Panel, unionObj.fb)
	
def ShowUnionOnlineMembers(role):
	'''
	显示公会在线成员
	@param role:
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	roleId = role.GetRoleID()
	
	sendList = []
	for memberId in unionObj.members.iterkeys():
		#玩家是否在线
		member = cRoleMgr.FindRoleByRoleID(memberId)
		if not member:
			continue
		level = member.GetLevel()
		#等级是否满足
		if level < UNION_FB_ACTIVATE_LEVEL:
			continue
		#不用显示自己
		if memberId == roleId:
			continue
		#公会成员是否有队伍
		if memberId in TeamBase.ROLEID_TO_TEAM:
			continue
		#roleId, 成员名, 成员等级
		sendList.append((memberId, member.GetRoleName(), level))
		
	#同步客户端
	role.SendObj(Union_FB_Show_Union_Online_Members, sendList)

def ShowUnionFBTeams(role):
	'''
	显示公会副本所有队伍
	@param role:
	'''
	unionId = role.GetUnionID()
	if not unionId:
		return
	
	unionTeamList = TeamBase.UNIONID_TO_TEAM_LIST.get(unionId)
	if not unionTeamList:
		return
	
	sendList = []
	for team in unionTeamList:
		if team.leader.IsKick():
			continue
		#队伍是否正在战斗中
		if Status.IsInStatus(team.leader, EnumInt1.ST_FightStatus):
			continue
		#是否在同一个副本中
		if role.GetI8(EnumInt8.UnionFBId) != team.leader.GetI8(EnumInt8.UnionFBId):
			continue
		#队伍ID，队长头像(性别, 职业, 进阶)，队长名，队伍人数
		sendList.append((team.team_id, team.leader.GetSex(), team.leader.GetCareer(), team.leader.GetGrade(), team.leader.GetRoleName(), len(team.members)))
		
	#同步客户端
	role.SendObj(Union_FB_Show_Teams, sendList)
	
def ShowUnionFBSubstitute(role):
	'''
	显示公会副本替身
	@param role:
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	roleId = role.GetRoleID()
	
	showDatas = {}
	nowDays = cDateTime.Days()
	for substituteRoleId, outDateDays in unionObj.other_data[UnionDefine.O_SUPER_CARDS_DAYS_IDX].iteritems():
		if nowDays >= outDateDays:
			continue
		
		#不能邀请自己的替身
		if roleId == substituteRoleId:
			continue
		
		showDatas[substituteRoleId] = [unionObj.get_member_data(substituteRoleId, UnionDefine.M_NAME_IDX), 
									unionObj.get_member_data(substituteRoleId, UnionDefine.M_LEVEL_IDX)]
	
	role.SendObj(Union_FB_Show_Substitute, showDatas)
	
#===============================================================================
# 战斗相关
#===============================================================================
def AfterFightForElite(fight):
	'''
	精英AfterFight
	@param fight:
	'''
	fbId = fight.after_fight_param
	# fight.round当前战斗回合
	# fight.result如果没“bug”的话将会取值1左阵营胜利；0平局；-1右阵营胜利
	# 故判断胜利请按照下面这种写法明确判定
	if fight.result == 1:
		#获取战斗role
		if not fight.left_camp.roles:
			return
		left_camp_roles_list = list(fight.left_camp.roles)
		role = left_camp_roles_list[0]
		#left win
		#精英奖励
		#日志
		with TraUnionFBEliteReward:
			EliteReward(role, fbId, fight)
	elif fight.result == -1:
		#right win
		pass
	else:
		#all lost
		pass
	
def AfterFightForLevel(fight):
	'''
	关卡AfterFight
	@param fight:
	'''
	fbId, levelId, unionObj = fight.after_fight_param
	
	# fight.round当前战斗回合
	# fight.result如果没“bug”的话将会取值1左阵营胜利；0平局；-1右阵营胜利
	# 故判断胜利请按照下面这种写法明确判定
	if fight.result == 1:
		#left win
		#获取战斗role
		for role in fight.left_camp.roles:
			#是否勾选了不消耗行动力
			if role.GetI1(EnumInt1.UnionFBNotCost):
				continue
			#是否有收益次数
			if role.GetI8(EnumInt8.UnionFBCnt) == 0:
				continue
			#增加公会占领度
			IncUnionFBOccupation(role, fbId, levelId)
			#关卡奖励
			#日志
			with TraUnionFBLevelReward:
				LevelReward(role, fbId, levelId, fight)
				
			#版本判断
			if Environment.EnvIsNA():
				#北美万圣节活动
				HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
				HalloweenNAMgr.finish_union_fb()
			elif Environment.EnvIsRU():
				#七日活动
				sevenActMgr = role.GetTempObj(EnumTempObj.SevenActMgr)
				#完成公会副本
				sevenActMgr.finish_union_fb()
				
		#最后同步客户端公会占领度
		for roleId in unionObj.members:
			theRole = cRoleMgr.FindRoleByRoleID(roleId)
			if not theRole:
				continue
			#同步客户端公会副本所有数据
			theRole.SendObj(Union_FB_Sync_All_Data, unionObj.fb)
		
	elif fight.result == -1:
		#right win
		pass
	else:
		#all lost
		pass
		
#===============================================================================
# 场景相关
#===============================================================================
@PublicScene.RegSceneAfterCreateFun(11)
def AfterCreateUnionFB1(scene):
	fbId = 1
	CreateUnionFBNPC(scene, fbId)
	
@PublicScene.RegSceneAfterCreateFun(12)
def AfterCreateUnionFB2(scene):
	fbId = 2
	CreateUnionFBNPC(scene, fbId)

@PublicScene.RegSceneAfterCreateFun(13)
def AfterCreateUnionFB3(scene):
	fbId = 3
	CreateUnionFBNPC(scene, fbId)

@PublicScene.RegSceneAfterCreateFun(14)
def AfterCreateUnionFB4(scene):
	fbId = 4
	CreateUnionFBNPC(scene, fbId)
	
@PublicScene.RegSceneAfterCreateFun(67)
def AfterCreateUnionFB5(scene):
	fbId = 5
	CreateUnionFBNPC(scene, fbId)
	
@PublicScene.RegSceneAfterCreateFun(68)
def AfterCreateUnionFB6(scene):
	fbId = 6
	CreateUnionFBNPC(scene, fbId)
		
def CreateUnionFBNPC(scene, fbId):
	'''
	创建公会副本NPC
	@param scene:
	@param fbId:
	'''
	fbConfig = UnionConfig.UNION_FB_BASE.get(fbId)
	if not fbConfig:
		return
	
	#创建精英NPC
	x, y = fbConfig.elitePos
	npc = scene.CreateNPC(fbConfig.eliteNpcType, x, y, 0, 1)
	npc.SetPyDict(1, 0)
	
	#创建关卡怪物
	for x in xrange(UNION_FB_LEVEL_CNT):
		levelId = x + 1
		levelConfig = UnionConfig.UNION_FB_MONSTER.get((fbId, levelId))
		if not levelConfig:
			continue
		#创建怪物NPC
		x, y = levelConfig.monsterPos
		npc = scene.CreateNPC(levelConfig.monsterNpcType, x, y, 0, 1)
		npc.SetPyDict(1, levelId)
		
@PublicScene.RegSceneAfterJoinRoleFun(11)
def AfterJoinUnionFB1(scene, role):
	fbId = 1
	AfterJoinUnionFBScene(role, fbId)

@PublicScene.RegSceneAfterJoinRoleFun(12)
def AfterJoinUnionFB2(scene, role):
	fbId = 2
	AfterJoinUnionFBScene(role, fbId)

@PublicScene.RegSceneAfterJoinRoleFun(13)
def AfterJoinUnionFB3(scene, role):
	fbId = 3
	AfterJoinUnionFBScene(role, fbId)

@PublicScene.RegSceneAfterJoinRoleFun(14)
def AfterJoinUnionFB4(scene, role):
	fbId = 4
	AfterJoinUnionFBScene(role, fbId)
	
@PublicScene.RegSceneAfterJoinRoleFun(67)
def AfterJoinUnionFB5(scene, role):
	fbId = 5
	AfterJoinUnionFBScene(role, fbId)
	
@PublicScene.RegSceneAfterJoinRoleFun(68)
def AfterJoinUnionFB6(scene, role):
	fbId = 6
	AfterJoinUnionFBScene(role, fbId)
	
def AfterJoinUnionFBScene(role, fbId):
	'''
	加入公会副本场景后调用
	@param role:
	@param fbId:
	'''
	#强制进入公会副本状态
	Status.ForceInStatus(role, EnumInt1.ST_UnionFB)
	
	#记录当前在哪个副本
	role.SetI8(EnumInt8.UnionFBId, fbId)
	
	#同步客户端公会占领度
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	#同步客户端公会副本所有数据
	role.SendObj(Union_FB_Sync_All_Data, unionObj.fb)
	
@PublicScene.RegSceneBeforeLeaveFun(11)
def BeforeLeaveUnionFB1(scene, role):
	fbId = 1
	BeforeLeaveUnionFBScene(role, fbId)

@PublicScene.RegSceneBeforeLeaveFun(12)
def BeforeLeaveUnionFB2(scene, role):
	fbId = 2
	BeforeLeaveUnionFBScene(role, fbId)

@PublicScene.RegSceneBeforeLeaveFun(13)
def BeforeLeaveUnionFB3(scene, role):
	fbId = 3
	BeforeLeaveUnionFBScene(role, fbId)

@PublicScene.RegSceneBeforeLeaveFun(14)
def BeforeLeaveUnionFB4(scene, role):
	fbId = 4
	BeforeLeaveUnionFBScene(role, fbId)
	
@PublicScene.RegSceneBeforeLeaveFun(67)
def BeforeLeaveUnionFB5(scene, role):
	fbId = 5
	BeforeLeaveUnionFBScene(role, fbId)
	
@PublicScene.RegSceneBeforeLeaveFun(68)
def BeforeLeaveUnionFB6(scene, role):
	fbId = 6
	BeforeLeaveUnionFBScene(role, fbId)
	
def BeforeLeaveUnionFBScene(role, fbId):
	'''
	离开公会副本场景前调用
	@param role:
	@param fbId:
	'''
	#退出公会副本状态
	Status.Outstatus(role, EnumInt1.ST_UnionFB)
	
	#设置副本ID为0
	role.SetI8(EnumInt8.UnionFBId, 0)
	
	#不在战斗状态
	team = role.GetTeam()
	#有队伍则退出队伍
	if team and team.team_type == EnumTeamType.T_UnionFB:
		#离开队伍
		team.Quit(role)
	else:
		#是否有替身队伍
		sTeam = role.GetTempObj(EnumTempObj.UnionFBSubstituteTeam)
		if sTeam:
			sTeam.dismiss(role)
		
#===============================================================================
# 时间相关
#===============================================================================
def ResetUnionFBCnt():
	days = cDateTime.Days()
	for role in cRoleMgr.GetAllRole():
		#重置公会副本行动力
		role.SetI8(EnumInt8.UnionFBCnt, UNION_FB_DAY_CNT)
		#重置精英收益次数
		role.SetI1(EnumInt1.UnionFBElite, UNION_FB_ELITE_DAY_CNT)
		#重置公会副本购买次数
		role.SetI8(EnumInt8.UnionFBBuyCnt, 0)
		#设置更新时间
		role.SetI16(EnumInt16.UnionFBCntUpdateDays, days)
		
#===============================================================================
# 事件
#===============================================================================
def OnSyncRoleOtherData(role, param):
	'''
	登陆同步数据
	@param role:
	@param param:
	'''
	if SDHFunGather.StartFlag[SDHDefine.UnionFB]:
		unionObj = role.GetUnionObj()
		if unionObj:
			role.SendObj(Union_FB_Sync_All_Data, unionObj.fb)
			
	#是否更新公会副本次数
	IsUpdateUnionFBCnt(role)
	fbId = role.GetI8(EnumInt8.UnionFBId)
	if not fbId:
		return
	
	#是否正在战斗状态
	if Status.IsInStatus(role, EnumInt1.ST_FightStatus):
		#在战斗状态,则进入副本
		InUnionFB(role, fbId)
		return
	else:
		#不在战斗状态
		team = role.GetTeam()
		#有队伍则退出队伍
		if team:
			#离开队伍
			team.Quit(role)
		else:
			#是否有替身队伍
			sTeam = role.GetTempObj(EnumTempObj.UnionFBSubstituteTeam)
			if sTeam:
				sTeam.dismiss(role)
			
		#设置副本ID为0
		role.SetI8(EnumInt8.UnionFBId, 0)
		
		#和谐在战斗中下线，战斗状态中无法传送离开场景的情况
		fbConfig = UnionConfig.UNION_FB_BASE.get(fbId)
		if not fbConfig:
			return
		if role.GetSceneID() == fbConfig.sceneId:
			#传送
			role.Revive(16, 2618, 2491)
	
def OnRoleLevelUp(role, param):
	'''
	升级
	@param role:
	@param param:
	'''
	#60级激活公会副本
	if role.GetLevel() == UNION_FB_ACTIVATE_LEVEL:
		#激活给予公会副本行动力
		role.SetI8(EnumInt8.UnionFBCnt, UNION_FB_DAY_CNT)
		#激活给予精英收益次数
		role.SetI1(EnumInt1.UnionFBElite, UNION_FB_ELITE_DAY_CNT)
		#重置公会副本购买次数
		role.SetI8(EnumInt8.UnionFBBuyCnt, 0)
		
		days = cDateTime.Days()
		#是否超过了14点
		if cDateTime.Hour() < UNION_FB_UPDATE_HOUR:
			#设置更新时间
			role.SetI16(EnumInt16.UnionFBCntUpdateDays, days - 1)
		else:
			#设置更新时间
			role.SetI16(EnumInt16.UnionFBCntUpdateDays, days)
		
def OnRoleClientLost(role, param):
	'''
	角色客户端掉线
	@param role:
	@param param:
	'''
	fbId = role.GetI8(EnumInt8.UnionFBId)
	if not fbId:
		return
	
	fbConfig = UnionConfig.UNION_FB_BASE.get(fbId)
	if not fbConfig:
		return
	if role.GetSceneID() != fbConfig.sceneId:
		print "GE_EXC OnRoleClientLost error union fb scene id (%s)" % role.GetRoleID()
		return
	
	#是否正在战斗状态
	if Status.IsInStatus(role, EnumInt1.ST_FightStatus):
		return
	else:
		#不在战斗状态
		
		#退出公会副本场景
		role.BackPublicScene()
	
def OnRoleExit(role, param):
	'''
	角色离线
	@param role:
	@param param:
	'''
	if role.GetI8(EnumInt8.UnionFBId) == 0:
		return
	
	#退出公会副本场景
	role.BackPublicScene()
	
#===============================================================================
# 数组改变调用
#===============================================================================
def AfterChangeUnionFBCnt(role, oldValue, newValue):
	'''
	公会副本行动力改变
	@param role:
	@param oldValue:
	@param newValue:
	'''
	team = role.GetTeam()
	if not team:
		return
	
	#通知队伍成员行动力变化
	team.BroadMsg(Union_FB_Call_Team_Member_Cnt_Change, (role.GetRoleID(), newValue))
	
#===============================================================================
# 客户端请求
#===============================================================================
def RequestUnionFBOpenPanel(role, msg):
	'''
	客户端请求公会副本面板
	@param role:
	@param msg:
	'''
	#等级限制
	if role.GetLevel() < UNION_FB_ACTIVATE_LEVEL:
		return
	
	#是否更新公会副本次数
	IsUpdateUnionFBCnt(role)
	
	ShowUnionFBPanel(role)
	
def RequestUnionFBOpenTeamPanel(role, msg):
	#等级限制
	if role.GetLevel() < UNION_FB_ACTIVATE_LEVEL:
		return
	
	#显示在线公会成员
	ShowUnionOnlineMembers(role)
	
def RequestUnionFBGetTeams(role, msg):
	'''
	客户端请求获取公会队伍
	@param role:
	@param msg:
	'''
	#等级限制
	if role.GetLevel() < UNION_FB_ACTIVATE_LEVEL:
		return
	
	#显示所有公会副本队伍
	ShowUnionFBTeams(role)
	
def RequestUnionFBIn(role, msg):
	'''
	客户端请求进入公会副本
	@param role:
	@param msg:
	'''
	fbId = msg
	
	#等级限制
	if role.GetLevel() < UNION_FB_ACTIVATE_LEVEL:
		return
	
	InUnionFB(role, fbId)
	
def RequestUnionFBOut(role, msg):
	'''
	客户端请求退出公会副本
	@param role:
	@param msg:
	'''
	#等级限制
	if role.GetLevel() < UNION_FB_ACTIVATE_LEVEL:
		return
	
	if role.GetI8(EnumInt8.UnionFBId) == 0:
		return
	
	#战斗状态中不能退出场景
	if Status.IsInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	#退出多人副本状态
	Status.Outstatus(role, EnumInt1.ST_InTeamMirror)
	
	#离开场景
	role.BackPublicScene()
	
	team = role.GetTeam()
	if team:
		#离开队伍
		team.Quit(role)
	else:
		#是否有替身队伍
		sTeam = role.GetTempObj(EnumTempObj.UnionFBSubstituteTeam)
		if sTeam:
			sTeam.dismiss(role)
		
	#设置副本ID为0
	role.SetI8(EnumInt8.UnionFBId, 0)
	
def RequestUnionFBFight(role, msg):
	'''
	客户端请求公会副本战斗
	@param role:
	@param msg:
	'''
	levelId = msg
	
	#等级限制
	if role.GetLevel() < UNION_FB_ACTIVATE_LEVEL:
		return
	
	#没有公会不能挑战
	if not role.GetUnionID():
		return
	
	#是否更新公会副本次数
	IsUpdateUnionFBCnt(role)
	
	UnionFBFight(role, levelId)
	
def RequestUnionFBBuyCnt(role, msg):
	'''
	客户端请求公会副本购买次数
	@param role:
	@param msg:
	'''
	#等级限制
	if role.GetLevel() < UNION_FB_ACTIVATE_LEVEL:
		return
	
	#日志
	with TraUnionFBBuyCnt:
		BuyCnt(role)
	
def RequestUnionFBSetNotCost(role, msg):
	'''
	客户端请求公会副本设置不消耗次数
	@param role:
	@param msg:
	'''
	#等级限制
	if role.GetLevel() < UNION_FB_ACTIVATE_LEVEL:
		return
	
	UnionFBSetNotCost(role)
	
def RequestUnionFBSetAutoAcceptTeamInvite(role, msg):
	'''
	客户端请求设置公会副本自动接受组队邀请
	@param role:
	@param msg:
	'''
	#是否满足组队等级条件
	if role.GetLevel() < UNION_FB_ACTIVATE_LEVEL:
		return
	
	UnionFBSetAutoAcceptTeamInvite(role)
	
def RequestUnionFBCreateSubstituteTeam(role, msg):
	'''
	客户端请求创建公会副本替身队伍
	@param role:
	@param msg:
	'''
	#是否满足组队等级条件
	if role.GetLevel() < UNION_FB_ACTIVATE_LEVEL:
		return
	
	UnionFBCreateSubstituteTeam(role)
	
	ShowUnionFBSubstitute(role)
	
def RequestUnionFBKickSubstitute(role, msg):
	'''
	客户端请求踢掉公会副本替身
	@param role:
	@param msg:
	'''
	#是否满足组队等级条件
	if role.GetLevel() < UNION_FB_ACTIVATE_LEVEL:
		return
	
	desRoleId = msg
	
	UnionFBKickSubstitute(role, desRoleId)
	
	
def RequestUnionFBDismissSubstituteTeam(role, msg):
	'''
	客户端请求解散公会副本替身队伍
	@param role:
	@param msg:
	'''
	#是否满足组队等级条件
	if role.GetLevel() < UNION_FB_ACTIVATE_LEVEL:
		return
	
	backFunId, _ = msg
	
	sTeam = role.GetTempObj(EnumTempObj.UnionFBSubstituteTeam)
	if not sTeam:
		return
	sTeam.dismiss(role)
	
	#回调客户端
	role.CallBackFunction(backFunId, None)
	
def RequestUnionFBSubstituteTeamChangePos(role, msg):
	'''
	客户端请求公会副本替身队伍交换位置
	@param role:
	@param msg:
	'''
	#是否满足组队等级条件
	if role.GetLevel() < UNION_FB_ACTIVATE_LEVEL:
		return
	
	pos1, pos2 = msg
	
	UnionFBSubstituteTeamChangePos(role, pos1, pos2)
	
def RequestUnionFBInviteSubstitute(role, msg):
	#是否满足组队等级条件
	if role.GetLevel() < UNION_FB_ACTIVATE_LEVEL:
		return
	
	inviteRoleId = msg
	
	UnionFBInviteSubstitute(role, inviteRoleId)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		#公会副本重置行动力时间
		Cron.CronDriveByMinute((2038, 1, 1), ResetUnionFBCnt, H = "H == 14", M = "M == 0")
	
	if Environment.HasLogic and not Environment.IsCross:
		#事件
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		Event.RegEvent(Event.Eve_AfterLevelUp, OnRoleLevelUp)
		Event.RegEvent(Event.Eve_ClientLost, OnRoleClientLost)
		Event.RegEvent(Event.Eve_BeforeExit, OnRoleExit)
		
		#设置数组改变调用的函数
		cRoleDataMgr.SetInt8Fun(EnumInt8.UnionFBCnt, AfterChangeUnionFBCnt)
		
		#日志
		TraUnionFBLevelReward = AutoLog.AutoTransaction("TraUnionFBLevelReward", "公会副本关卡奖励")
		TraUnionFBEliteReward = AutoLog.AutoTransaction("TraUnionFBEliteReward", "公会副本精英奖励")
		TraUnionFBBuyCnt = AutoLog.AutoTransaction("TraUnionFBBuyCnt", "公会副本购买行动力")
		
		#注册消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_FB_Open_Panel", "客户端请求公会副本面板"), RequestUnionFBOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_FB_Open_Team_Panel", "客户端请求打开公会副本队伍面板"), RequestUnionFBOpenTeamPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_FB_Get_Teams", "客户端请求获取公会副本队伍"), RequestUnionFBGetTeams)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_FB_In", "客户端请求进入公会副本"), RequestUnionFBIn)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_FB_Out", "客户端请求退出公会副本"), RequestUnionFBOut)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_FB_Fight", "客户端请求公会副本战斗"), RequestUnionFBFight)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_FB_Buy_Cnt", "客户端请求公会副本购买次数"), RequestUnionFBBuyCnt)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_FB_Set_Not_Cost", "客户端请求公会副本设置不消耗次数"), RequestUnionFBSetNotCost)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_FB_Set_Auto_Accept_Invite", "客户端请求设置公会副本自动接受组队邀请"), RequestUnionFBSetAutoAcceptTeamInvite)

		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_FB_Create_Substitute_Team", "客户端请求创建公会副本替身队伍"), RequestUnionFBCreateSubstituteTeam)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_FB_Kick_Substitute", "客户端请求踢掉公会副本替身"), RequestUnionFBKickSubstitute)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_FB_Dismiss_Substitute_Team", "客户端请求解散公会副本替身队伍"), RequestUnionFBDismissSubstituteTeam)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_FB_Substitute_Team_Change_Pos", "客户端请求公会副本替身队伍交换位置"), RequestUnionFBSubstituteTeamChangePos)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_FB_Invite_Substitute", "客户端请求邀请公会副本替身"), RequestUnionFBInviteSubstitute)

