#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.KuaFuJJC.KuaFuJJCCross")
#===============================================================================
# 跨服竞技场跨服进程
#===============================================================================
import copy
import random
import cComplexServer
import cDateTime
import cRoleDataMgr
import cRoleMgr
import cSceneMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, EnumAward, EnumFightStatistics,\
	GlobalPrompt
from ComplexServer.Log import AutoLog
from ComplexServer.Time import Cron
from Game.Activity.Award import AwardMgr
from Game.Activity.Title import Title
from Game.Fight import FightEx, Middle
from Game.KuaFuJJC import KuaFuJJCConfig
from Game.Persistence import BigTable, Contain
from Game.Role import Rank, Status, Call
from Game.Role.Data import EnumObj, EnumDayInt8, EnumTempInt64, EnumInt1,\
	EnumInt32, EnumInt16, EnumCD
from Game.Role.Mail import Mail
from Game.Role import Event

if "_HasLoad" not in dir():
	
	KUAFU_JJC_ROLE_DICT = {}				#跨服竞技场角色字典
	CROSS_ROLEID_TO_UNION_DATA_DICT = {}	#跨服角色ID对应公会数据字典(用来缓存玩家公会数据)
	ROLE_ELECTION_RANK = {}					#缓存个人海选排行榜
	UNION_ELECTION_RANK = {}				#缓存公会海选排行榜
	ROLE_FINALS_RANK = {}					#缓存个人决赛排行榜
	ZONEID_TO_JJC_ROLE_DATA_FROM_LOGIC = {}	#保存从逻辑进程发送过来的竞技场角色数据
	
	ROLE_ELECTION_SCORE_RANK_IDX = 1		#个人海选积分排行榜
	UNION_ELECTION_SCORE_RANK_IDX = 2		#公会海选积分排行榜
	ROLE_FINALS_SCORE_RANK_IDX = 3			#个人决赛积分排行榜
	
	#消息
	KuaFu_JJC_Cross_Show_Election_Challenge_Data = AutoMessage.AllotMessage("KuaFu_JJC_Cross_Show_Election_Challenge_Data", "通知客户端显示跨服个人竞技场海选挑战信息")
	KuaFu_JJC_Cross_Show_Finals_Challenge_Data = AutoMessage.AllotMessage("KuaFu_JJC_Cross_Show_Finals_Challenge_Data", "通知客户端显示跨服个人竞技场决赛挑战信息")
	KuaFu_JJC_Cross_Show_Role_Election_Rank = AutoMessage.AllotMessage("KuaFu_JJC_Cross_Show_Role_Election_Rank", "通知客户端显示跨服个人竞技场个人海选积分排行榜")
	KuaFu_JJC_Cross_Show_Union_Election_Rank = AutoMessage.AllotMessage("KuaFu_JJC_Cross_Show_Union_Election_Rank", "通知客户端显示跨服个人竞技场公会海选积分排行榜")
	KuaFu_JJC_Cross_Show_Role_Finals_Rank = AutoMessage.AllotMessage("KuaFu_JJC_Cross_Show_Role_Finals_Rank", "通知客户端显示跨服个人竞技场个人决赛积分排行榜")
	KuaFu_JJC_Cross_Show_Data_Panel = AutoMessage.AllotMessage("KuaFu_JJC_Cross_Show_Data_Panel", "通知客户端显示跨服个人竞技场信息面板")
	KuaFu_JJC_Cross_Show_Reset_Round_Panel = AutoMessage.AllotMessage("KuaFu_JJC_Cross_Show_Reset_Round_Panel", "通知客户端显示跨服个人竞技场重置轮数面板")
	KuaFu_JJC_Cross_Sync_Day = AutoMessage.AllotMessage("KuaFu_JJC_Cross_Sync_Day", "通知客户端同步跨服服务器跨服个人竞技场活动天数")
	
	
class KuaFuJJCRole(object):
	def __init__(self, kuaFuJJCData):
		self.role_id = kuaFuJJCData["role_id"]
		self.role_name = kuaFuJJCData["role_name"]
		self.role_level = kuaFuJJCData["role_level"]
		self.role_sex = kuaFuJJCData["role_sex"]
		self.role_grade = kuaFuJJCData["role_grade"]
		self.role_career = kuaFuJJCData["role_career"]
		self.role_zdl = kuaFuJJCData["role_zdl"]
		self.role_wing_id = kuaFuJJCData["role_wing_id"]
		self.role_fashion_clithes = kuaFuJJCData["role_fashion_clithes"]
		self.role_fashion_hat = kuaFuJJCData["role_fashion_hat"]
		self.role_fashion_weapons = kuaFuJJCData["role_fashion_weapons"]
		self.role_fashion_state = kuaFuJJCData["role_fashion_state"]
		self.role_fight_data = kuaFuJJCData["role_fight_data"]
		self.role_election_score = kuaFuJJCData["role_election_score"]
		self.role_finals_score = kuaFuJJCData["role_finals_score"]
		self.role_zone_name = kuaFuJJCData["role_zone_name"]
		self.role_war_station = kuaFuJJCData["role_war_station"]
		self.role_station_soul = kuaFuJJCData.get("role_station_soul", 0)
		
	def HasChange(self):
		KUAFU_JJC_BT.SetValue(self.__dict__)
		
	def HasDelete(self):
		KUAFU_JJC_BT.DelKey(self.role_id)
		KUAFU_JJC_BT.SaveData()
		
	def GetStandAppearence(self):
		return (self.role_id, self.role_name, self.role_sex, self.role_grade, 
			self.role_career, self.role_level, self.role_wing_id, 
			self.role_fashion_clithes, self.role_fashion_hat, 
			self.role_fashion_weapons, self.role_fashion_state, 
			self.role_zdl, self.role_zone_name, self.role_war_station, self.role_station_soul)
		
	def GetPalaceStandAppearence(self):
		return (self.role_id, self.role_name, self.role_sex, self.role_grade, 
			self.role_career, self.role_level, self.role_wing_id, 
			self.role_fashion_clithes, self.role_fashion_hat, 
			self.role_fashion_weapons, self.role_fashion_state, 
			self.role_zdl, self.role_zone_name, self.role_finals_score, self.role_war_station, self.role_station_soul)

class KuaFuJJCRoleElectionScoreRank(Rank.LittleRank):
	def __init__(self, maxRankSize):
		Rank.LittleRank.__init__(self, maxRankSize)
	
	# 返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		return v1[1] < v2[1]
	
	def Clear(self):
		#清理数据
		self.data = {}
		self.min_role_id = 0
		self.min_value = 0
		
class KuaFuJJCUnionElectionScoreRank(Rank.LittleRank):
	def __init__(self, maxRankSize):
		Rank.LittleRank.__init__(self, maxRankSize)
	
	# 返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		return v1[1] < v2[1]
	
	def Clear(self):
		#清理数据
		self.data = {}
		self.min_role_id = 0
		self.min_value = 0
		
class KuaFuJJCRoleFinalsScoreRank(Rank.LittleRank):
	def __init__(self, maxRankSize):
		Rank.LittleRank.__init__(self, maxRankSize)
	
	# 返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		return v1[1] < v2[1]
	
	def Clear(self):
		#清理数据
		self.data = {}
		self.min_role_id = 0
		self.min_value = 0
		
		
		
def SaveKuaFuJJCRoleData(jjcRoleDataList):
	'''
	保存跨服竞技场数据
	@param role:
	'''
	global KUAFU_JJC_ROLE_DICT
	
	for data in jjcRoleDataList:
		
		role_id, role_name, role_level, role_sex, role_grade, role_career, role_zdl, role_wing_id, role_fashion_clithes, role_fashion_hat, role_fashion_weapons, role_fashion_state, role_fight_data, role_zone_name, role_war_station,role_station_soul = data
		
		#获取保存的积分
		electionScore = 0
		finalsScore = 0
		jjcRole = KUAFU_JJC_ROLE_DICT.get(role_id)
		if jjcRole:
			electionScore = jjcRole.role_election_score
			finalsScore = jjcRole.role_finals_score
		
		d = {"role_id": role_id, "role_name": role_name, "role_level": role_level, "role_sex": role_sex,
			"role_grade": role_grade, "role_career": role_career, "role_zdl": role_zdl,
			"role_wing_id": role_wing_id, "role_fashion_clithes":role_fashion_clithes, 
			"role_fashion_hat":role_fashion_hat, "role_fashion_weapons":role_fashion_weapons, 
			"role_fashion_state":role_fashion_state, "role_fight_data":role_fight_data, 
			"role_election_score":electionScore, "role_finals_score":finalsScore, "role_zone_name":role_zone_name, 
			"role_war_station":role_war_station, "role_station_soul":role_station_soul}
		
		KUAFU_JJC_ROLE_DICT[role_id] = kuaFuJJCRole = KuaFuJJCRole(d)
		#保存
		kuaFuJJCRole.HasChange()
		
	KUAFU_JJC_BT.SaveData()
		
def GetGroupList(roleId):
	zoneId = 0
	if roleId in KUAFU_JJC_CROSS_ROLEID_TO_ZONEID_DICT:
		zoneId = KUAFU_JJC_CROSS_ROLEID_TO_ZONEID_DICT[roleId]
	else:
		return []
	
	if zoneId not in KUAFU_JJC_CROSS_ZONEID_TO_GROUP:
		return []
	groupDict = KUAFU_JJC_CROSS_ZONEID_TO_GROUP[zoneId]
	
	for group in groupDict.itervalues():
		if roleId in group:
			return list(group)
	
	#不在任何分组内，是否有海选资格，返回最后一个分组
	if roleId in KUAFU_JJC_CROSS_ELECTION_ROLEID_LIST:
		return list(groupDict[KuaFuJJCConfig.LAST_GROUP_ID])
	
	return []

def GetGroupID(roleId):
	zoneId = 0
	if roleId in KUAFU_JJC_CROSS_ROLEID_TO_ZONEID_DICT:
		zoneId = KUAFU_JJC_CROSS_ROLEID_TO_ZONEID_DICT[roleId]
	else:
		return 0
	
	if zoneId not in KUAFU_JJC_CROSS_ZONEID_TO_GROUP:
		return 0
	groupDict = KUAFU_JJC_CROSS_ZONEID_TO_GROUP[zoneId]
	
	for groupId, group in groupDict.iteritems():
		if roleId in group:
			return groupId
		
	#不在任何分组内，是否有海选资格，返回最后一个分组
	if roleId in KUAFU_JJC_CROSS_ELECTION_ROLEID_LIST:
		return KuaFuJJCConfig.LAST_GROUP_ID
	
	return 0
	
def ElectionChallenge(role, desRoleId):
	#战斗状态
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	jjcDataDict = role.GetObj(EnumObj.KuaFuJJCData)
	
	challengeRoleIdDict = jjcDataDict[KuaFuJJCConfig.ELECTION_CHALLENGE_DATA_OBJ_IDX]
	if desRoleId not in challengeRoleIdDict:
		return
	
	#是否已经挑战过
	if challengeRoleIdDict[desRoleId]:
		return
	
	kuaFuJJCRole = KUAFU_JJC_ROLE_DICT.get(desRoleId)
	if not kuaFuJJCRole:
		return
	
	#次数判断
	if role.GetDI8(EnumDayInt8.KuaFuJJCFreeCnt) >= EnumGameConfig.KUAFU_JJC_FREE_CNT:
		if role.GetI16(EnumInt16.KuaFuJJCChallengeCnt) > 0:
			role.DecI16(EnumInt16.KuaFuJJCChallengeCnt, 1)
		else:
			return
	else:
		role.IncDI8(EnumDayInt8.KuaFuJJCFreeCnt, 1)
	
	#战斗
	FightEx.PVP_JJC(role, 0, kuaFuJJCRole.role_fight_data, AfterElectionFight, afterFightParam=desRoleId)
	
def FinalsChallenge(role, desRoleId):
	#战斗状态
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	#是否有决赛资格
	if CanChallengeFinals(role) is False:
		return
	
	jjcDataDict = role.GetObj(EnumObj.KuaFuJJCData)
	
	challengeRoleIdDict = jjcDataDict[KuaFuJJCConfig.FINALS_CHALLENGE_DATA_OBJ_IDX]
	if desRoleId not in challengeRoleIdDict:
		return
	
	#是否已经挑战过
	if challengeRoleIdDict[desRoleId]:
		return
	
	kuaFuJJCRole = KUAFU_JJC_ROLE_DICT.get(desRoleId)
	if not kuaFuJJCRole:
		return
	
	#次数判断
	if role.GetDI8(EnumDayInt8.KuaFuJJCFinalsFreeCnt) >= EnumGameConfig.KUAFU_JJC_FINALS_FREE_CNT:
		if role.GetI16(EnumInt16.KuaFuJJCChallengeCnt) > 0:
			role.DecI16(EnumInt16.KuaFuJJCChallengeCnt, 1)
		else:
			return
	else:
		role.IncDI8(EnumDayInt8.KuaFuJJCFinalsFreeCnt, 1)
	
	if not kuaFuJJCRole.role_fight_data:
		NotFightDataWin(role, desRoleId)
		return
	#战斗
	FightEx.PVP_JJC(role, 0, kuaFuJJCRole.role_fight_data, AfterFinalsFight, afterFightParam=desRoleId)
	
def CanChallengeFinals(role):
	roleId = role.GetRoleID()
	
	#获取区域ID
	zoneId = KUAFU_JJC_CROSS_ROLEID_TO_ZONEID_DICT.get(roleId, 0)
	
	#是否有对应区域ID的排行榜
	if zoneId not in ROLE_ELECTION_RANK:
		return False
	littleRank = ROLE_ELECTION_RANK[zoneId]
	
	#是否有决赛资格
	if roleId not in littleRank.data:
		return False
	
	return True
	
def AfterJoinCrossScene(role, param):
	global CROSS_ROLEID_TO_UNION_DATA_DICT
	global KUAFU_JJC_CROSS_UNION_PROCESS_ID
	
	zoneName, zoneId, processId, unionName, leaderName = param
	
	#刚刚跨服过来，到达准备间，调用的第一个函数
	if KuaFuJJCConfig.IS_START is False:
		#活动已经结束了,或者没开启
		role.GotoLocalServer(None, None)
		return
	
	roleId = role.GetRoleID()
	#保存区域ID，便于查看数据
	if roleId not in KUAFU_JJC_CROSS_ROLEID_TO_ZONEID_DICT:
		KUAFU_JJC_CROSS_ROLEID_TO_ZONEID_DICT[roleId] = zoneId
	
	#若有区域ID，则有资格，保存区域ID，创建对手
	#是否有参加海选资格
	if roleId in KUAFU_JJC_CROSS_ELECTION_ROLEID_LIST:
		#保存
		CreateKuaFuJJCRole(role, zoneName)
	
	#创建对手
	CreateOpponent(role)
	
	#公会数据
	unionId = role.GetUnionID()
	if unionId:
		CROSS_ROLEID_TO_UNION_DATA_DICT[unionId] = [unionName, zoneName, leaderName]
		KUAFU_JJC_CROSS_UNION_PROCESS_ID[unionId] = processId
	
	#同步挑战数据
	if KuaFuJJCConfig.IsFinals() is False:
		ShowElectionChallengeData(role)
	else:
		ShowFinalsChallengeData(role)
		
	#同步客户端
	SyncKuaFuJJCDay(role)
	ShowDataPanel(role)
		
def SyncKuaFuJJCDay(role):
	#活动当前是第几天，距离下次活动开启还有几天
	role.SendObj(KuaFu_JJC_Cross_Sync_Day, (KuaFuJJCConfig.KUAFU_JJC_DAY, KuaFuJJCConfig.DAYS_BEFORE_START))
	
def CreateKuaFuJJCRole(role, zoneName):
	global KUAFU_JJC_ROLE_DICT
	
	roleId = role.GetRoleID()
	if roleId in KUAFU_JJC_ROLE_DICT:
		return
	
	d = {"role_id": roleId, "role_name": role.GetRoleName(), 
	"role_level": role.GetLevel(), "role_sex": role.GetSex(), 
	"role_grade": role.GetGrade(), "role_career": role.GetCareer(), 
	"role_zdl": role.GetZDL(), "role_wing_id": role.GetWingID(), 
	"role_fashion_clithes":role.GetTI64(EnumTempInt64.FashionClothes),
	"role_fashion_hat":role.GetTI64(EnumTempInt64.FashionHat),
	"role_fashion_weapons":role.GetTI64(EnumTempInt64.FashionWeapons),
	"role_fashion_state":role.GetI1(EnumInt1.FashionViewState),
	"role_fight_data":None,
	"role_election_score":role.GetI32(EnumInt32.KuaFuJJCElectionScore),
	"role_finals_score":role.GetI32(EnumInt32.KuaFuJJCFinalsScore), 
	"role_zone_name":zoneName,
	"role_war_station":role.GetI16(EnumInt16.WarStationStarNum),
	"role_station_soul":role.GetI16(EnumInt16.StationSoulId)}

	KUAFU_JJC_ROLE_DICT[roleId] = kuaFuJJCRole = KuaFuJJCRole(d)
	#保存
	kuaFuJJCRole.HasChange()
	
def CreateRoleFightData(role):
	global KUAFU_JJC_ROLE_DICT
	
	roleId = role.GetRoleID()
	if roleId not in KUAFU_JJC_ROLE_DICT:
		return
	
	kuaFuJJCRole = KUAFU_JJC_ROLE_DICT[roleId]
	kuaFuJJCRole.role_fight_data = Middle.GetRoleData(role, True)
	#保存
	kuaFuJJCRole.HasChange()
	
def CreateOpponent(role):
	jjcDataDict = role.GetObj(EnumObj.KuaFuJJCData)
	
	roleId = role.GetRoleID()
	groupList = GetGroupList(roleId)
	if not groupList:
		return
	
	#对手不能有自己
	if roleId in groupList:
		groupList.remove(roleId)
	
	if KuaFuJJCConfig.IsFinals() is False:
		#海选
		electionChallengeData = jjcDataDict[KuaFuJJCConfig.ELECTION_CHALLENGE_DATA_OBJ_IDX]
		electionRound = role.GetI16(EnumInt16.KuaFuJJCElectionRound)
		if electionChallengeData:
			if 0 in electionChallengeData.values():
				#还有未挑战的对手
				return
			else:
				#挑战完所有对手
				roundConfig = KuaFuJJCConfig.KUAFU_JJC_ELECTION_ROUND.get(electionRound)
				if not roundConfig:
					return
				#是否需要重置
				if roundConfig.needReset:
					#通知客户端显示重置轮数
					role.SendObj(KuaFu_JJC_Cross_Show_Reset_Round_Panel, None)
					return
				
		config = KuaFuJJCConfig.KUAFU_JJC_ELECTION_ROUND.get(electionRound + 1)
		if not config:
			return
		
		groupLen = len(groupList)
		if not groupLen:
			return
		
		#轮次+1
		role.IncI16(EnumInt16.KuaFuJJCElectionRound, 1)
		
		#清空海选挑战数据
		electionChallengeData.clear()
		
		sampleCnt = min(groupLen, config.opponentCnt)
		for opponentRoleId in random.sample(groupList, sampleCnt):
			electionChallengeData[opponentRoleId] = 0
			
		#同步客户端
		ShowElectionChallengeData(role)
	else:
		#决赛
		#是否有决赛资格
		if CanChallengeFinals(role) is False:
			return
		
		finalsChallengeData = jjcDataDict[KuaFuJJCConfig.FINALS_CHALLENGE_DATA_OBJ_IDX]
		finalRound = role.GetI16(EnumInt16.KuaFuJJCFinalsRound)
		
		#已经有决赛挑战数据
		if finalsChallengeData:
			return
		
		config = KuaFuJJCConfig.KUAFU_JJC_FINALS_ROUND.get(finalRound + 1)
		if not config:
			return
		
		zoneId = KUAFU_JJC_CROSS_ROLEID_TO_ZONEID_DICT.get(roleId, 0)
		if not zoneId:
			return
		#是否有对应区域ID的排行榜
		if zoneId not in ROLE_ELECTION_RANK:
			return
		littleRank = ROLE_ELECTION_RANK[zoneId]
		
		#获取随机
		roleIdList = littleRank.data.keys()
		roleIdList.remove(roleId)
		
		groupLen = len(roleIdList)
		if not groupLen:
			return
		
		#轮次+1
		role.IncI16(EnumInt16.KuaFuJJCFinalsRound, 1)
		
		#清空决赛挑战数据
		finalsChallengeData.clear()
		
		sampleCnt = min(groupLen, config.opponentCnt)
		for opponentRoleId in random.sample(roleIdList, sampleCnt):
			finalsChallengeData[opponentRoleId] = 0
			
		#同步客户端
		ShowFinalsChallengeData(role)
		
def InitOpponent(role):
	'''
	初始化对手
	@param role:
	'''
	jjcDataDict = role.GetObj(EnumObj.KuaFuJJCData)
	
	roleId = role.GetRoleID()
	groupList = GetGroupList(roleId)
	if not groupList:
		return
	
	#对手不能有自己
	if roleId in groupList:
		groupList.remove(roleId)
	
	if KuaFuJJCConfig.IsFinals() is False:
		#海选
		electionChallengeData = jjcDataDict[KuaFuJJCConfig.ELECTION_CHALLENGE_DATA_OBJ_IDX]
		electionRound = role.GetI16(EnumInt16.KuaFuJJCElectionRound)
		
		#已经有海选挑战数据
		if electionChallengeData:
			return
				
		config = KuaFuJJCConfig.KUAFU_JJC_ELECTION_ROUND.get(electionRound + 1)
		if not config:
			return
		
		groupLen = len(groupList)
		if not groupLen:
			return
		
		#轮次+1
		role.IncI16(EnumInt16.KuaFuJJCElectionRound, 1)
		
		sampleCnt = min(groupLen, config.opponentCnt)
		for opponentRoleId in random.sample(groupList, sampleCnt):
			electionChallengeData[opponentRoleId] = 0
			
		#同步客户端
		ShowElectionChallengeData(role)
	else:
		#决赛
		#是否有决赛资格
		if CanChallengeFinals(role) is False:
			return
		
		finalsChallengeData = jjcDataDict[KuaFuJJCConfig.FINALS_CHALLENGE_DATA_OBJ_IDX]
		finalRound = role.GetI16(EnumInt16.KuaFuJJCFinalsRound)
		
		#已经有决赛挑战数据
		if finalsChallengeData:
			return
		
		config = KuaFuJJCConfig.KUAFU_JJC_FINALS_ROUND.get(finalRound + 1)
		if not config:
			return
		
		zoneId = KUAFU_JJC_CROSS_ROLEID_TO_ZONEID_DICT.get(roleId, 0)
		if not zoneId:
			return
		#是否有对应区域ID的排行榜
		if zoneId not in ROLE_ELECTION_RANK:
			return
		littleRank = ROLE_ELECTION_RANK[zoneId]
		
		#获取随机
		roleIdList = littleRank.data.keys()
		roleIdList.remove(roleId)
		
		groupLen = len(roleIdList)
		if not groupLen:
			return
		
		#轮次+1
		role.IncI16(EnumInt16.KuaFuJJCFinalsRound, 1)
		
		sampleCnt = min(groupLen, config.opponentCnt)
		for opponentRoleId in random.sample(roleIdList, sampleCnt):
			finalsChallengeData[opponentRoleId] = 0
			
		#同步客户端
		ShowFinalsChallengeData(role)
			
def ElectionZDLSort():
	'''
	海选使用战斗力排名
	'''
	global KUAFU_JJC_CROSS_ZONEID_TO_GROUP
	
	for zoneId, jjcRoleDataDict in ZONEID_TO_JJC_ROLE_DATA_FROM_LOGIC.iteritems():
		jjcRoleDataList = jjcRoleDataDict.values()
		#根据战斗力排序
		jjcRoleDataList.sort(key=lambda x:x[6], reverse=True)
		
		KUAFU_JJC_CROSS_ZONEID_TO_GROUP[zoneId] = groupDict = {}
		saveKuaFuJJCRoleDataList = []
		for groupId, groupConfig in KuaFuJJCConfig.KUAFU_JJC_GROUP.iteritems():
			start, end = groupConfig.rankInterval
			#最后一个分组特殊处理
			if groupId == KuaFuJJCConfig.LAST_GROUP_ID:
				remainDataList = [data[0] for data in jjcRoleDataList[start-1 : ]]
				lastGroup = []
				if len(remainDataList) > groupConfig.groupLen:
					groupDict[groupId] = lastGroup = random.sample(remainDataList, groupConfig.groupLen)
				else:
					groupDict[groupId] = lastGroup = remainDataList
				for roleId in lastGroup:
					saveKuaFuJJCRoleDataList.append(jjcRoleDataDict[roleId])
				
				continue
			
			#其他组正常处理
			groupDict[groupId] = [data[0] for data in jjcRoleDataList[start-1 : end]]
			saveKuaFuJJCRoleDataList.extend(jjcRoleDataList[start-1 : end])
		
		#保存
		KUAFU_JJC_CROSS_ZONEID_TO_GROUP.changeFlag = True
		SaveKuaFuJJCRoleData(saveKuaFuJJCRoleDataList)
			
def ElectionScoreSort():
	'''
	海选使用海选积分排名
	'''
	global KUAFU_JJC_CROSS_ZONEID_TO_GROUP
	
	for zoneId, jjcRoleDataDict in ZONEID_TO_JJC_ROLE_DATA_FROM_LOGIC.iteritems():
		jjcRoleDataList = jjcRoleDataDict.values()
		
		sortList = []
		#生成排序列表
		for data in jjcRoleDataList:
			roleId = data[0]
			electionScore = 0
			if roleId in KUAFU_JJC_ROLE_DICT:
				electionScore = KUAFU_JJC_ROLE_DICT[roleId].role_election_score
			sortList.append((roleId, electionScore))
		
		#根据海选积分排序
		sortList.sort(key=lambda x:x[1], reverse=True)
		
		KUAFU_JJC_CROSS_ZONEID_TO_GROUP[zoneId] = groupDict = {}
		saveKuaFuJJCRoleDataList = []
		for groupId, groupConfig in KuaFuJJCConfig.KUAFU_JJC_GROUP.iteritems():
			start, end = groupConfig.rankInterval
			#最后一个分组特殊处理
			if groupId == KuaFuJJCConfig.LAST_GROUP_ID:
				remainDataList = [data[0] for data in sortList[start-1 : end]]
				lastGroup = []
				if len(remainDataList) > groupConfig.groupLen:
					groupDict[groupId] = lastGroup = random.sample(jjcRoleDataList, groupConfig.groupLen)
				else:
					groupDict[groupId] = lastGroup = remainDataList
				for roleId in lastGroup:
					saveKuaFuJJCRoleDataList.append(jjcRoleDataDict[roleId])
				
				continue
			else:
				sortList1 = sortList[start-1 : end]
				groupDict[groupId] = l = []
				LA = l.append
				SA = saveKuaFuJJCRoleDataList.append
				for roleid,_ in sortList1:
					LA(roleid)
					SA(jjcRoleDataDict[roleid])
			#其他组正常处理
			#groupDict[groupId] = [data[0] for data in jjcRoleDataList[start-1 : end]]
			#saveKuaFuJJCRoleDataList.extend(jjcRoleDataList[start-1 : end])
		
		#保存
		KUAFU_JJC_CROSS_ZONEID_TO_GROUP.changeFlag = True
		SaveKuaFuJJCRoleData(saveKuaFuJJCRoleDataList)
		
def BuyChallengeCnt(role):
	buyCnt = role.GetI16(EnumInt16.KuaFuJJCBuyCnt)
	
	config = KuaFuJJCConfig.KUAFU_JJC_BUY_CNT.get(buyCnt + 1)
	if not config:
		return
	
	if role.GetKuaFuMoney() < config.needKuaFuMoney:
		return
	
	role.DecKuaFuMoney(config.needKuaFuMoney)
	
	#次数增加
	role.IncI16(EnumInt16.KuaFuJJCBuyCnt, 1)
	role.IncI16(EnumInt16.KuaFuJJCChallengeCnt, 1)
		
def ResetRound(role):
	#判断是否真的需要重置
	if Environment.EnvIsNA():
		if role.GetKuaFuMoney() < EnumGameConfig.KUAFU_JJC_RESET_ROUND_KUAFU_MONEY_NA:
			return
	else:
		if role.GetKuaFuMoney() < EnumGameConfig.KUAFU_JJC_RESET_ROUND_KUAFU_MONEY:
			return
	
	jjcDataDict = role.GetObj(EnumObj.KuaFuJJCData)
	if KuaFuJJCConfig.IsFinals() is False:
		#海选
		electionChallengeData = jjcDataDict[KuaFuJJCConfig.ELECTION_CHALLENGE_DATA_OBJ_IDX]
		if not electionChallengeData:
			return
		
		challengeFlagList = electionChallengeData.values()
		if 0 in challengeFlagList:
			#还有未挑战的数据
			return
		if Environment.EnvIsNA():
			role.DecKuaFuMoney(EnumGameConfig.KUAFU_JJC_RESET_ROUND_KUAFU_MONEY_NA)
		else:
			role.DecKuaFuMoney(EnumGameConfig.KUAFU_JJC_RESET_ROUND_KUAFU_MONEY)
		
		#清空挑战数据
		electionChallengeData.clear()
		
		CreateOpponent(role)
	else:
		#决赛
		finalsChallengeData = jjcDataDict[KuaFuJJCConfig.FINALS_CHALLENGE_DATA_OBJ_IDX]
		if not finalsChallengeData:
			return
		
		challengeFlagList = finalsChallengeData.values()
		if 0 in challengeFlagList:
			#还有未挑战的数据
			return
		
		if Environment.EnvIsNA():
			role.DecKuaFuMoney(EnumGameConfig.KUAFU_JJC_RESET_ROUND_KUAFU_MONEY_NA)
		else:
			role.DecKuaFuMoney(EnumGameConfig.KUAFU_JJC_RESET_ROUND_KUAFU_MONEY)
		
		#清空挑战数据
		finalsChallengeData.clear()
		
		CreateOpponent(role)
		
def FinalsRefreshUseMoney(role):
	'''
	决赛手动刷新，需要跨服币
	@param role:
	'''
	roleId = role.GetRoleID()
	jjcDataDict = role.GetObj(EnumObj.KuaFuJJCData)
	finalsChallengeData = jjcDataDict[KuaFuJJCConfig.FINALS_CHALLENGE_DATA_OBJ_IDX]
	finalRound = role.GetI16(EnumInt16.KuaFuJJCFinalsRound)
	
	config = KuaFuJJCConfig.KUAFU_JJC_FINALS_ROUND.get(finalRound)
	if not config:
		return
	
	zoneId = KUAFU_JJC_CROSS_ROLEID_TO_ZONEID_DICT.get(roleId, 0)
	if not zoneId:
		return
	#是否有对应区域ID的排行榜
	if zoneId not in ROLE_ELECTION_RANK:
		return
	littleRank = ROLE_ELECTION_RANK[zoneId]
	
	#获取随机
	roleIdList = littleRank.data.keys()
	roleIdList.remove(roleId)
	
	groupLen = len(roleIdList)
	if not groupLen:
		return
	
	#判断CD
	cd = role.GetCD(EnumCD.KuaFuJJCFinalsRefreshCD)
	if cd > 0:
		needKuaFuMoney = (cd / 60 + 1) * 2
		
		#是否有足够的跨服币
		if role.GetKuaFuMoney() < needKuaFuMoney:
			return
		
		role.DecKuaFuMoney(needKuaFuMoney)
	
	#设置CD
	role.SetCD(EnumCD.KuaFuJJCFinalsRefreshCD, 5 * 60)
	
	#清空决赛挑战数据
	finalsChallengeData.clear()
	
	sampleCnt = min(groupLen, config.opponentCnt)
	for opponentRoleId in random.sample(roleIdList, sampleCnt):
		finalsChallengeData[opponentRoleId] = 0
		
	#同步客户端
	ShowFinalsChallengeData(role)
	
def FinalsRefreshFree(role):
	'''
	决赛刷新，免费
	@param role:
	'''
	roleId = role.GetRoleID()
	jjcDataDict = role.GetObj(EnumObj.KuaFuJJCData)
	finalsChallengeData = jjcDataDict[KuaFuJJCConfig.FINALS_CHALLENGE_DATA_OBJ_IDX]
	finalRound = role.GetI16(EnumInt16.KuaFuJJCFinalsRound)
	
	config = KuaFuJJCConfig.KUAFU_JJC_FINALS_ROUND.get(finalRound + 1)
	if not config:
		return
	
	zoneId = KUAFU_JJC_CROSS_ROLEID_TO_ZONEID_DICT.get(roleId, 0)
	if not zoneId:
		return
	#是否有对应区域ID的排行榜
	if zoneId not in ROLE_ELECTION_RANK:
		return
	littleRank = ROLE_ELECTION_RANK[zoneId]
	
	#获取随机
	roleIdList = littleRank.data.keys()
	roleIdList.remove(roleId)
	
	groupLen = len(roleIdList)
	if not groupLen:
		return
	
	#轮次+1
	role.IncI16(EnumInt16.KuaFuJJCFinalsRound, 1)
	
	#清空决赛挑战数据
	finalsChallengeData.clear()
	
	sampleCnt = min(groupLen, config.opponentCnt)
	for opponentRoleId in random.sample(roleIdList, sampleCnt):
		finalsChallengeData[opponentRoleId] = 0
	
	#同步客户端
	ShowFinalsChallengeData(role)
		
#===============================================================================
# 显示
#===============================================================================
def ShowElectionChallengeData(role):
	jjcDataDict = role.GetObj(EnumObj.KuaFuJJCData)
	
	canChallengeRoleIdDict = jjcDataDict[KuaFuJJCConfig.ELECTION_CHALLENGE_DATA_OBJ_IDX]
	
	canChallengeDict = {}
	for challengeRoleId in canChallengeRoleIdDict.iterkeys():
		if challengeRoleId not in KUAFU_JJC_ROLE_DICT:
			continue
		kuaFuJJCRole = KUAFU_JJC_ROLE_DICT[challengeRoleId]
		canChallengeDict[challengeRoleId] = kuaFuJJCRole.GetStandAppearence()
	
	#同步客户端
	role.SendObj(KuaFu_JJC_Cross_Show_Election_Challenge_Data, (canChallengeDict.values(), canChallengeRoleIdDict))
	
def ShowFinalsChallengeData(role):
	jjcDataDict = role.GetObj(EnumObj.KuaFuJJCData)
	
	canChallengeRoleIdDict = jjcDataDict[KuaFuJJCConfig.FINALS_CHALLENGE_DATA_OBJ_IDX]
	
	canChallengeDict = {}
	for challengeRoleId in canChallengeRoleIdDict.iterkeys():
		if challengeRoleId not in KUAFU_JJC_ROLE_DICT:
			continue
		kuaFuJJCRole = KUAFU_JJC_ROLE_DICT[challengeRoleId]
		canChallengeDict[challengeRoleId] = kuaFuJJCRole.GetStandAppearence()
	
	#同步客户端
	role.SendObj(KuaFu_JJC_Cross_Show_Finals_Challenge_Data, (canChallengeDict.values(), canChallengeRoleIdDict))
	
def ShowRoleElectionRank(role):
	#获取区域ID
	roleId = role.GetRoleID()
	
	zoneId = KUAFU_JJC_CROSS_ROLEID_TO_ZONEID_DICT.get(roleId, 0)
	if not zoneId:
		return
		
	#是否有对应区域ID的排行榜
	if zoneId not in ROLE_ELECTION_RANK:
		return
	
	littleRank = ROLE_ELECTION_RANK[zoneId]
	
	#同步客户端
	role.SendObj(KuaFu_JJC_Cross_Show_Role_Election_Rank, littleRank.data.items())
	
def ShowUnionElectionRank(role):
	#获取区域ID
	roleId = role.GetRoleID()
	
	zoneId = KUAFU_JJC_CROSS_ROLEID_TO_ZONEID_DICT.get(roleId, 0)
	if not zoneId:
		return
		
	#是否有对应区域ID的排行榜
	if zoneId not in UNION_ELECTION_RANK:
		return
	
	littleRank = UNION_ELECTION_RANK[zoneId]
	
	#同步客户端
	role.SendObj(KuaFu_JJC_Cross_Show_Union_Election_Rank, littleRank.data.items())
	
def ShowRoleFinalsRank(role):
	#获取区域ID
	roleId = role.GetRoleID()
	
	zoneId = KUAFU_JJC_CROSS_ROLEID_TO_ZONEID_DICT.get(roleId, 0)
	if not zoneId:
		return
		
	#是否有对应区域ID的排行榜
	if zoneId not in ROLE_FINALS_RANK:
		return
	
	littleRank = ROLE_FINALS_RANK[zoneId]
	
	#同步客户端
	role.SendObj(KuaFu_JJC_Cross_Show_Role_Finals_Rank, littleRank.data.items())
	
def ShowDataPanel(role):
	roleId = role.GetRoleID()
	groupId = GetGroupID(roleId)
	unionScore = KUAFU_JJC_CROSS_UNION_SCORE.get(role.GetUnionID(), 0)
	
	#海选资格
	canElection = 0
	if roleId in KUAFU_JJC_CROSS_ELECTION_ROLEID_LIST:
		canElection = 1
	
	#决赛资格
	canFinals = 0
	if CanChallengeFinals(role) is True:
		canFinals = 1
	
	#海选资格，决赛资格，分组ID，公会积分
	role.SendObj(KuaFu_JJC_Cross_Show_Data_Panel, (canElection, canFinals, groupId, unionScore))
	
#===============================================================================
# 战斗相关
#===============================================================================
def OnLeave(fight, role, reason):
	# reason 0战斗结束离场；1战斗中途掉线
	print "OnLeave", role.GetRoleID(), reason
	# fight.result如果没“bug”的话将会取值1左阵营胜利；0平局；-1右阵营胜利；None战斗未结束
	# 注意，只有在角色离开的回调函数中fight.result才有可能为None

def AfterElectionFight(fight):
	desRoleId = fight.after_fight_param
	
	#获取战斗玩家
	if not fight.left_camp.roles:
		return
	left_camp_roles_list = list(fight.left_camp.roles)
	role = left_camp_roles_list[0]
	
	# fight.round当前战斗回合
	#print "fight round", fight.round
	# fight.result如果没“bug”的话将会取值1左阵营胜利；0平局；-1右阵营胜利
	# 故判断胜利请按照下面这种写法明确判定
	if fight.result == 1:
		#print "left win"
		#挑战成功
		
		#日志
		with TraKFJJCElectionWin:
			WinElectionChallenge(role, desRoleId, fight)
		
		#创建战斗数据
		CreateRoleFightData(role)
		#重新创建对手
		CreateOpponent(role)
		
	elif fight.result == -1:
		#print "right win"
		#挑战失败
		
		#日志
		with TraKFJJCElectionLost:
			LostELectionChallenge(role, desRoleId, fight)
	else:
		#print "all lost"
		pass
	
	#同步客户端
	ShowDataPanel(role)
	ShowRoleElectionRank(role)
	ShowUnionElectionRank(role)
	
def AfterFinalsFight(fight):
	desRoleId = fight.after_fight_param
	
	#获取战斗玩家
	if not fight.left_camp.roles:
		return
	left_camp_roles_list = list(fight.left_camp.roles)
	role = left_camp_roles_list[0]
	
	# fight.round当前战斗回合
	#print "fight round", fight.round
	# fight.result如果没“bug”的话将会取值1左阵营胜利；0平局；-1右阵营胜利
	# 故判断胜利请按照下面这种写法明确判定
	if fight.result == 1:
		#print "left win"
		#挑战成功
		
		#日志
		with TraKFJJCFinalsWin:
			WinFinalsChallenge(role, desRoleId, fight)
		
		#胜利后免费刷新对手
		FinalsRefreshFree(role)
		
	elif fight.result == -1:
		#print "right win"
		#挑战失败
		
		#日志
		with TraKFJJCFinalsLost:
			LostFinalsChallenge(role, desRoleId, fight)
	else:
		#print "all lost"
		pass
	
	#同步客户端
	ShowDataPanel(role)
	ShowRoleFinalsRank(role)


def NotFightDataWin(role, desRoleId):
	#日志
	with TraKFJJCFinalsWin:
		WinFinalsChallenge(role, desRoleId, None)
	#胜利后免费刷新对手
	FinalsRefreshFree(role)
	#同步客户端
	ShowDataPanel(role)
	ShowRoleFinalsRank(role)
	#给提示
	role.Msg(2, 0, GlobalPrompt.KUAFU_JJC_NOT_FIGHT_MSG)

def WinElectionChallenge(role, desRoleId, fightObj):
	jjcDataDict = role.GetObj(EnumObj.KuaFuJJCData)
	challengeRoleIdDict = jjcDataDict[KuaFuJJCConfig.ELECTION_CHALLENGE_DATA_OBJ_IDX]
	if desRoleId not in challengeRoleIdDict:
		return
	
	#是否已经挑战过
	if challengeRoleIdDict[desRoleId]:
		return
	challengeRoleIdDict[desRoleId] = 1
	
	#计算海选积分
	winningStreak = role.GetI16(EnumInt16.KuaFuJJCElectionWinningStreak)
	addScore = 400 + (winningStreak * (random.randint(100, 150))+random.randint(1, 100))
	
	#连胜+1
	role.IncI16(EnumInt16.KuaFuJJCElectionWinningStreak, 1)
	
	#加分
	role.IncI32(EnumInt32.KuaFuJJCElectionScore, addScore)
	unionId = role.GetUnionID()
	if unionId:
		#今日公会积分
		global KUAFU_JJC_CROSS_UNION_TODAY_SCORE
		if unionId not in KUAFU_JJC_CROSS_UNION_TODAY_SCORE:
			KUAFU_JJC_CROSS_UNION_TODAY_SCORE[unionId] = addScore
		else:
			KUAFU_JJC_CROSS_UNION_TODAY_SCORE[unionId] += addScore
		#公会总积分
		global KUAFU_JJC_CROSS_UNION_SCORE
		if unionId not in KUAFU_JJC_CROSS_UNION_SCORE:
			KUAFU_JJC_CROSS_UNION_SCORE[unionId] = addScore
		else:
			KUAFU_JJC_CROSS_UNION_SCORE[unionId] += addScore
			
	
	#奖励
	electionRound = role.GetI16(EnumInt16.KuaFuJJCElectionRound)
	roundConfig = KuaFuJJCConfig.KUAFU_JJC_ELECTION_ROUND.get(electionRound)
	showItemList = []
	if roundConfig:
		if roundConfig.rewardItem:
			role.AddItem(*roundConfig.rewardItem)
			showItemList.append(roundConfig.rewardItem)
	
	#战斗奖励统计显示
	roleId = role.GetRoleID()
	fightObj.set_fight_statistics(roleId, EnumFightStatistics.EnumKFJJCElectionScore, addScore)
	fightObj.set_fight_statistics(roleId, EnumFightStatistics.EnumItems, showItemList)
	
	#进榜
	InElectionScoreRank(role, addScore)
	
	#同步客户端
	ShowElectionChallengeData(role)
	
def LostELectionChallenge(role, desRoleId, fightObj):
	jjcDataDict = role.GetObj(EnumObj.KuaFuJJCData)
	challengeRoleIdDict = jjcDataDict[KuaFuJJCConfig.ELECTION_CHALLENGE_DATA_OBJ_IDX]
	if desRoleId not in challengeRoleIdDict:
		return
	
	#是否已经挑战过
	if challengeRoleIdDict[desRoleId]:
		return
	
	#奖励
	electionRound = role.GetI16(EnumInt16.KuaFuJJCElectionRound)
	roundConfig = KuaFuJJCConfig.KUAFU_JJC_ELECTION_ROUND.get(electionRound)
	showItemList = []
	if roundConfig:
		if roundConfig.rewardItem:
			role.AddItem(*roundConfig.rewardItem)
			showItemList.append(roundConfig.rewardItem)
	
	#重置连胜
	role.SetI16(EnumInt16.KuaFuJJCElectionWinningStreak, 0)
	
	#战斗奖励统计显示
	roleId = role.GetRoleID()
	fightObj.set_fight_statistics(roleId, EnumFightStatistics.EnumItems, showItemList)
	
def WinFinalsChallenge(role, desRoleId, fightObj):
	jjcDataDict = role.GetObj(EnumObj.KuaFuJJCData)
	challengeRoleIdDict = jjcDataDict[KuaFuJJCConfig.FINALS_CHALLENGE_DATA_OBJ_IDX]
	if desRoleId not in challengeRoleIdDict:
		return
	
	#是否已经挑战过
	if challengeRoleIdDict[desRoleId]:
		return
	challengeRoleIdDict[desRoleId] = 1
	
	#计算决赛积分
	winningStreak = role.GetI16(EnumInt16.KuaFuJJCFinalsWinningStreak)
	addScore = 400 + (winningStreak * (random.randint(100, 150))+random.randint(1, 100))
	
	#连胜+1
	role.IncI16(EnumInt16.KuaFuJJCFinalsWinningStreak, 1)
	
	#加分
	role.IncI32(EnumInt32.KuaFuJJCFinalsScore, addScore)
	
	#奖励
	finalsRound = role.GetI16(EnumInt16.KuaFuJJCFinalsRound)
	roundConfig = KuaFuJJCConfig.KUAFU_JJC_FINALS_ROUND.get(finalsRound)
	showItemList = []
	if roundConfig:
		if roundConfig.rewardItem:
			role.AddItem(*roundConfig.rewardItem)
			showItemList.append(roundConfig.rewardItem)
	
	#战斗奖励统计显示
	roleId = role.GetRoleID()
	if fightObj:
		fightObj.set_fight_statistics(roleId, EnumFightStatistics.EnumKFJJCFinalsScore, addScore)
		fightObj.set_fight_statistics(roleId, EnumFightStatistics.EnumItems, showItemList)
	
	#进榜
	InFinalsScoreRank(role, addScore)
	
	#同步客户端
	ShowFinalsChallengeData(role)
	
def LostFinalsChallenge(role, desRoleId, fightObj):
	jjcDataDict = role.GetObj(EnumObj.KuaFuJJCData)
	challengeRoleIdDict = jjcDataDict[KuaFuJJCConfig.FINALS_CHALLENGE_DATA_OBJ_IDX]
	if desRoleId not in challengeRoleIdDict:
		return
	
	#是否已经挑战过
	if challengeRoleIdDict[desRoleId]:
		return
	
	#重置
	role.SetI16(EnumInt16.KuaFuJJCFinalsWinningStreak, 0)
	
	#奖励
	finalsRound = role.GetI16(EnumInt16.KuaFuJJCFinalsRound)
	roundConfig = KuaFuJJCConfig.KUAFU_JJC_FINALS_ROUND.get(finalsRound)
	showItemList = []
	if roundConfig:
		if roundConfig.rewardItem:
			role.AddItem(*roundConfig.rewardItem)
			showItemList.append(roundConfig.rewardItem)
	
	#重置连胜
	role.SetI16(EnumInt16.KuaFuJJCFinalsWinningStreak, 0)
	
	#战斗奖励统计显示
	roleId = role.GetRoleID()
	fightObj.set_fight_statistics(roleId, EnumFightStatistics.EnumItems, showItemList)
	
def InElectionScoreRank(role, addScore):
	global KUAFU_JJC_CROSS_RANK
	global ROLE_ELECTION_RANK
	global UNION_ELECTION_RANK
	
	#进榜
	roleId = role.GetRoleID()
	zoneId = KUAFU_JJC_CROSS_ROLEID_TO_ZONEID_DICT.get(roleId, 0)
	if not zoneId:
		return
	
	#个人海选积分榜
	if zoneId not in ROLE_ELECTION_RANK:
		ROLE_ELECTION_RANK[zoneId] = KuaFuJJCRoleElectionScoreRank(KuaFuJJCConfig.ROLE_ELECTION_RANK_CNT)
	roleLittleRank = ROLE_ELECTION_RANK[zoneId]
	
	if roleId in KUAFU_JJC_ROLE_DICT:
		kuaFuJJCRole = KUAFU_JJC_ROLE_DICT[roleId]
		roleLittleRank.HasData(roleId, [kuaFuJJCRole.role_name, kuaFuJJCRole.role_election_score, kuaFuJJCRole.role_zone_name])
		#保存到持久化数据
		KUAFU_JJC_CROSS_RANK[ROLE_ELECTION_SCORE_RANK_IDX][zoneId] = copy.deepcopy(roleLittleRank.data)
		KUAFU_JJC_CROSS_RANK.changeFlag = True
	
	#公会海选积分榜
	unionId = role.GetUnionID()
	if not unionId:
		return
	
	if zoneId not in UNION_ELECTION_RANK:
		UNION_ELECTION_RANK[zoneId] = KuaFuJJCUnionElectionScoreRank(KuaFuJJCConfig.UNION_ELECTION_RANK_CNT)
	unionLittleRank = UNION_ELECTION_RANK[zoneId]
	
	if unionId in CROSS_ROLEID_TO_UNION_DATA_DICT:
		unionName, zoneName, leaderName = CROSS_ROLEID_TO_UNION_DATA_DICT[unionId]
		totalScore = KUAFU_JJC_CROSS_UNION_SCORE[unionId]
		unionLittleRank.HasData(unionId, [unionName, totalScore, zoneName, leaderName])
		#保存到持久化数据
		KUAFU_JJC_CROSS_RANK[UNION_ELECTION_SCORE_RANK_IDX][zoneId] = copy.deepcopy(unionLittleRank.data)
		KUAFU_JJC_CROSS_RANK.changeFlag = True
	
def InFinalsScoreRank(role, addScore):
	global KUAFU_JJC_CROSS_RANK
	global ROLE_ELECTION_RANK
	global UNION_ELECTION_RANK
	
	#进榜
	roleId = role.GetRoleID()
	zoneId = KUAFU_JJC_CROSS_ROLEID_TO_ZONEID_DICT.get(roleId, 0)
	if not zoneId:
		return
	
	#个人海选积分榜
	if zoneId not in ROLE_FINALS_RANK:
		ROLE_FINALS_RANK[zoneId] = KuaFuJJCRoleFinalsScoreRank(KuaFuJJCConfig.ROLE_FINALS_RANK_CNT)
	roleLittleRank = ROLE_FINALS_RANK[zoneId]
	
	if roleId not in KUAFU_JJC_ROLE_DICT:
		return
	
	kuaFuJJCRole = KUAFU_JJC_ROLE_DICT[roleId]
	roleLittleRank.HasData(roleId, [kuaFuJJCRole.role_name, kuaFuJJCRole.role_finals_score, kuaFuJJCRole.role_zone_name])
	
	#保存到持久化数据
	KUAFU_JJC_CROSS_RANK[ROLE_FINALS_SCORE_RANK_IDX][zoneId] = copy.deepcopy(roleLittleRank.data)
	KUAFU_JJC_CROSS_RANK.changeFlag = True
	
def UnionElectionRankReward():
	for littleRank in UNION_ELECTION_RANK.itervalues():
		
		sorList = []
		for k, v in littleRank.data.iteritems():
			l = [k, ]
			l.extend(v)
			sorList.append(l)
		
		#根据海选积分排序(先积分，后unionId)
		sorList.sort(key=lambda x:(x[2], x[0]), reverse=True)
		#取前十名
		sortList = sorList[:10]
		for idx, data in enumerate(sortList):
			unionId = data[0]
			rank = idx + 1
			processId = KUAFU_JJC_CROSS_UNION_PROCESS_ID.get(unionId, 0)
			if not processId:
				print "GE_EXC KUAFU_JJC UnionElectionRankReward error not processId unionid(%s)" % unionId
				continue
			Call.ServerCall(processId, "Game.KuaFuJJC.KuaFuJJCMgr", "CrossToLogicJJCElectionUnionReward", (rank, unionId))

def FinalsRankReward():
	zoneIdToFinalsFirstRoleIdDict = {}
	for zoneId, littleRank in ROLE_FINALS_RANK.iteritems():
		
		sorList = []
		for k, v in littleRank.data.iteritems():
			l = [k, ]
			l.extend(v)
			sorList.append(l)
		
		#根据决赛积分排序
		sorList.sort(key=lambda x:x[2], reverse=True)
		#取前100名
		sortList = sorList[:100]
		for idx, data in enumerate(sortList):
			rank = idx + 1
			roleId = data[0]
			
			rewardConfig = KuaFuJJCConfig.KUAFU_JJC_FINALS_RANK_REWARD.get(rank)
			if not rewardConfig:
				continue
			
			AwardMgr.SetAward(roleId, EnumAward.KuaFuJJCFinalsRankAward, itemList = rewardConfig.rewardItem, clientDescParam = (rank, ))
		
			#决赛称号奖励
			if rank >= 1 and rank <= 3:
				if rewardConfig.rewardTitleId:
					Title.AddTitle(roleId, rewardConfig.rewardTitleId)
		
		#记录每个区域决赛第一名
		zoneIdToFinalsFirstRoleIdDict[zoneId] = sorList[0][0]
		
		#日志事件
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveKuaFuJJCFinalsRewardRank, sorList)

	#通知所有逻辑进程决赛竞猜结果
	Call.ServerCall(0, "Game.KuaFuJJC.KuaFuJJCMgr", "CrossCallToSendFinalsGuessResult", zoneIdToFinalsFirstRoleIdDict)

def SavePalaceData():
	global KUAFU_JJC_CROSS_PALACE_DATA
	for zoneId, littleRank in ROLE_FINALS_RANK.iteritems():
		
		KUAFU_JJC_CROSS_PALACE_DATA[zoneId] = palaceDataList = []
		
		sorList = []
		for k, v in littleRank.data.iteritems():
			l = [k, ]
			l.extend(v)
			sorList.append(l)
		
		#根据决赛积分排序(先积分，后roleId)
		sorList.sort(key=lambda x:x[2], reverse=True)
		
		#取前10名
		sortList = sorList[:10]
		for data in sortList:
			roleId = data[0]
			
			if roleId not in KUAFU_JJC_ROLE_DICT:
				continue
			
			kuaFuJJCRole = KUAFU_JJC_ROLE_DICT[roleId]
			
			palaceDataList.append(kuaFuJJCRole.GetPalaceStandAppearence())
	
	#保存标志
	KUAFU_JJC_CROSS_PALACE_DATA.changeFlag = True
	
def DayClear():
	global KUAFU_JJC_CROSS_UNION_TODAY_SCORE
	KUAFU_JJC_CROSS_UNION_TODAY_SCORE.clear()
		
def ClearAllData():
	#缓存数据
	global KUAFU_JJC_ROLE_DICT
	global CROSS_ROLEID_TO_UNION_DATA_DICT
	global ROLE_ELECTION_RANK
	global UNION_ELECTION_RANK
	global ROLE_FINALS_RANK
	global ZONEID_TO_JJC_ROLE_DATA_FROM_LOGIC
	KUAFU_JJC_ROLE_DICT.clear()
	CROSS_ROLEID_TO_UNION_DATA_DICT.clear()
	ROLE_ELECTION_RANK.clear()
	UNION_ELECTION_RANK.clear()
	ROLE_FINALS_RANK.clear()
	ZONEID_TO_JJC_ROLE_DATA_FROM_LOGIC.clear()
	
	#持久化数据
	global KUAFU_JJC_BT
	global KUAFU_JJC_CROSS_ELECTION_ROLEID_LIST
	global KUAFU_JJC_CROSS_ROLEID_TO_ZONEID_DICT
	global KUAFU_JJC_CROSS_RANK
	global KUAFU_JJC_CROSS_ZONEID_TO_GROUP
	global KUAFU_JJC_CROSS_UNION_SCORE
	global KUAFU_JJC_CROSS_UNION_PROCESS_ID
	
	btData = KUAFU_JJC_BT.GetData()
	for key in btData.keys():
		KUAFU_JJC_BT.DelKey(key)
	
	KUAFU_JJC_CROSS_ELECTION_ROLEID_LIST.clear()
	
	KUAFU_JJC_CROSS_ROLEID_TO_ZONEID_DICT.clear()
	
	#排行榜数据不能直接删除，防止服务器一周不关闭时找不到key
	KUAFU_JJC_CROSS_RANK[ROLE_ELECTION_SCORE_RANK_IDX].clear()
	KUAFU_JJC_CROSS_RANK[UNION_ELECTION_SCORE_RANK_IDX].clear()
	KUAFU_JJC_CROSS_RANK[ROLE_FINALS_SCORE_RANK_IDX].clear()
	KUAFU_JJC_CROSS_RANK.changeFlag = True
	
	KUAFU_JJC_CROSS_ZONEID_TO_GROUP.clear()
	KUAFU_JJC_CROSS_UNION_SCORE.clear()
	KUAFU_JJC_CROSS_UNION_PROCESS_ID.clear()
			
#===============================================================================
# DB AfterLoad
#===============================================================================
def KuaFuJJCBTAfterLoad():
	global KUAFU_JJC_ROLE_DICT
	
	jjcData = KUAFU_JJC_BT.GetData()
	if jjcData:
		for roleId, data in jjcData.iteritems():
			KUAFU_JJC_ROLE_DICT[roleId] = KuaFuJJCRole(data)

def KuaFuJJCCrossRoleIdListAfterLoad():
	pass

def KuaFuJJCCrossRoleIdToZoneIdDictAfterLoad():
	pass

def KuaFuJJCCrossRankAfterLoad():
	global KUAFU_JJC_CROSS_RANK
	global ROLE_ELECTION_RANK
	global UNION_ELECTION_RANK
	global ROLE_FINALS_RANK
	
	#个人海选积分排行榜
	if ROLE_ELECTION_SCORE_RANK_IDX not in KUAFU_JJC_CROSS_RANK:
		KUAFU_JJC_CROSS_RANK[ROLE_ELECTION_SCORE_RANK_IDX] = {}
	else:
		#还原排行榜
		rankDict = KUAFU_JJC_CROSS_RANK[ROLE_ELECTION_SCORE_RANK_IDX]
		for zoneId, dataDict in rankDict.iteritems():
			ROLE_ELECTION_RANK[zoneId] = littleRank = KuaFuJJCRoleElectionScoreRank(KuaFuJJCConfig.ROLE_ELECTION_RANK_CNT)
			for k, v in dataDict.iteritems():
				littleRank.HasData(k, v)
	
	#公会海选积分排行榜
	if UNION_ELECTION_SCORE_RANK_IDX not in KUAFU_JJC_CROSS_RANK:
		KUAFU_JJC_CROSS_RANK[UNION_ELECTION_SCORE_RANK_IDX] = {}
	else:
		#还原排行榜
		rankDict = KUAFU_JJC_CROSS_RANK[UNION_ELECTION_SCORE_RANK_IDX]
		for zoneId, dataDict in rankDict.iteritems():
			UNION_ELECTION_RANK[zoneId] = littleRank = KuaFuJJCUnionElectionScoreRank(KuaFuJJCConfig.UNION_ELECTION_RANK_CNT)
			for k, v in dataDict.iteritems():
				littleRank.HasData(k, v)
		
	#决赛积分排行榜
	if ROLE_FINALS_SCORE_RANK_IDX not in KUAFU_JJC_CROSS_RANK:
		KUAFU_JJC_CROSS_RANK[ROLE_FINALS_SCORE_RANK_IDX] = {}
	else:
		#还原排行榜
		rankDict = KUAFU_JJC_CROSS_RANK[ROLE_FINALS_SCORE_RANK_IDX]
		for zoneId, dataDict in rankDict.iteritems():
			ROLE_FINALS_RANK[zoneId] = littleRank = KuaFuJJCRoleFinalsScoreRank(KuaFuJJCConfig.ROLE_FINALS_RANK_CNT)
			for k, v in dataDict.iteritems():
				littleRank.HasData(k, v)
				
	#保存标志
	KUAFU_JJC_CROSS_RANK.changeFlag = True
		
def KuaFuJJCCrossZoneIdToGroupAfterLoad():
	pass

def KuaFuJJCCrossGroupScoreAfterLoad():
	pass

def KuaFuJJCCrossUnionScoreAfterLoad():
	pass

def KuaFuJJCCrossUnionTodayScoreAfterLoad():
	pass

def KuaFuJJCCrossUnionProcessIdAfterLoad():
	pass

def KuaFuJJCCrossPalaceDataAfterLoad():
	pass

#===============================================================================
# 时间
#===============================================================================
def AfterNewDay():
	if KuaFuJJCConfig.IS_START is False:
		return
	
	#每日清理
	DayClear()
	
	if KuaFuJJCConfig.KUAFU_JJC_DAY == 2:
		#跨服竞技场海选第1天按战斗力排序
		ElectionZDLSort()
	elif KuaFuJJCConfig.KUAFU_JJC_DAY >= 3 and KuaFuJJCConfig.KUAFU_JJC_DAY <= 6:
		#跨服竞技场海选第2~5天按海选积分排序
		ElectionScoreSort()
		
def TodayElectionOver():
	#今日海选活动结束，清空今日资格玩家
	global KUAFU_JJC_CROSS_ROLEID_TO_ZONEID_DICT
	if not KUAFU_JJC_CROSS_ROLEID_TO_ZONEID_DICT.returnDB:
		return
	KUAFU_JJC_CROSS_ROLEID_TO_ZONEID_DICT.clear()
	
	#把玩家T出跨服场景
	scene = cSceneMgr.SearchPublicScene(KuaFuJJCConfig.KUAFU_JJC_SCENE_ID)
	if scene:
		for role in scene.GetAllRole():
			role.GotoLocalServer(None, None)
			
	#海选结束发奖
	if KuaFuJJCConfig.KUAFU_JJC_DAY == 6:
		#海选公会排行奖励
		UnionElectionRankReward()
		
		#拥有决赛资格的玩家入决赛积分榜,海选积分上榜玩家有资格参加决赛
		global ROLE_FINALS_RANK
		global KUAFU_JJC_CROSS_RANK
		
		zoneIdToGuessRoleData = {}
		for zoneId, electionLittleRank in ROLE_ELECTION_RANK.iteritems():
			ROLE_FINALS_RANK[zoneId] = finalsLittleRankObj = KuaFuJJCRoleFinalsScoreRank(KuaFuJJCConfig.ROLE_FINALS_RANK_CNT)
			
			guessRoleData = {}
			for k, v in electionLittleRank.data.iteritems():
				name = v[0]
				electionScore = v[1]
				zoneName = v[2]
				
				finalsLittleRankObj.HasData(k, [name, 0, zoneName])
				
				#生成竞猜数据
				kuaFuJJCRole = KUAFU_JJC_ROLE_DICT.get(k)
				if kuaFuJJCRole:
					guessRoleData[k] = (k, name, electionScore, kuaFuJJCRole.role_sex, kuaFuJJCRole.role_career, kuaFuJJCRole.role_grade, zoneName)
				
				#日志
				with TraKFJJCFinalsMail:
					#决赛资格邮件
					Mail.SendMail(k, GlobalPrompt.KUAFU_JJC_FINALS_TITLE, GlobalPrompt.KUAFU_JJC_FINALS_SENDER, GlobalPrompt.KUAFU_JJC_FINALS_MAIL)
				
				
			#保存到持久化数据
			KUAFU_JJC_CROSS_RANK[ROLE_FINALS_SCORE_RANK_IDX][zoneId] = copy.deepcopy(finalsLittleRankObj.data)
			KUAFU_JJC_CROSS_RANK.changeFlag = True
			
			#决赛竞猜数据
			zoneIdToGuessRoleData[zoneId] = guessRoleData
		
		#通知所有逻辑进程决赛竞猜所有角色
		print "RED", zoneIdToGuessRoleData
		Call.ServerCall(0, "Game.KuaFuJJC.KuaFuJJCMgr", "CrossCallToSendFinalsGuessData", zoneIdToGuessRoleData)
		
		#日志
		with TraKFJJCInFinalsList:
			#日志事件
			for zoneId, electionLittleRank in ROLE_ELECTION_RANK.iteritems(): 
				AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveKuaFuJJCInFinalsList, (zoneId, electionLittleRank.data))

def AfterLoadWorldData(param1, param2):
	#载入世界数据完成后，假如是个人竞技的第7天，重新生成份竞猜数据给逻辑进程
	if KuaFuJJCConfig.KUAFU_JJC_DAY == 7:
		GetGuessRoleData()

def GetGuessRoleData():
	#生成竞猜数据
	global ROLE_FINALS_RANK
	global KUAFU_JJC_CROSS_RANK
	
	zoneIdToGuessRoleData = {}
	for zoneId, electionLittleRank in ROLE_ELECTION_RANK.iteritems():
		guessRoleData = {}
		for k, v in electionLittleRank.data.iteritems():
			name = v[0]
			electionScore = v[1]
			zoneName = v[2]
			#生成竞猜数据
			kuaFuJJCRole = KUAFU_JJC_ROLE_DICT.get(k)
			if kuaFuJJCRole:
				guessRoleData[k] = (k, name, electionScore, kuaFuJJCRole.role_sex, kuaFuJJCRole.role_career, kuaFuJJCRole.role_grade, zoneName)
		#决赛竞猜数据
		zoneIdToGuessRoleData[zoneId] = guessRoleData
	#通知所有逻辑进程决赛竞猜所有角色
	print "RED, GetGuessRoleData:", zoneIdToGuessRoleData
	Call.ServerCall(0, "Game.KuaFuJJC.KuaFuJJCMgr", "CrossCallToSendFinalsGuessData", zoneIdToGuessRoleData)
	
	
def FinalsOver():
	#决赛结束
	
	#把玩家T出跨服场景
	scene = cSceneMgr.SearchPublicScene(KuaFuJJCConfig.KUAFU_JJC_SCENE_ID)
	if scene:
		for role in scene.GetAllRole():
			role.GotoLocalServer(None, None)
			
	#决赛结束发奖
	if KuaFuJJCConfig.KUAFU_JJC_DAY != 7:
		return
	
	#保存龙骑殿堂数据
	SavePalaceData()
	
	#日志
	with TraKFJJCFinalsRewardRank:
		#决赛排行奖励
		FinalsRankReward()
	
	#清理活动所有数据
	ClearAllData()
	
def Per30Minutes():
	#0点不同步,防止跨天清理出问题
	if cDateTime.Hour() == 0:
		return
	
	if not KUAFU_JJC_CROSS_UNION_TODAY_SCORE.returnDB:
		return
	sendDict = {}
	for unionId, score in KUAFU_JJC_CROSS_UNION_TODAY_SCORE.iteritems():
		
		processId = KUAFU_JJC_CROSS_UNION_PROCESS_ID.get(unionId)
		if not processId:
			continue
		datadict = sendDict.setdefault(processId, {})
		datadict[unionId] = score
		
	
	for processId, datadict in sendDict.iteritems():
		Call.ServerCall(processId, "Game.KuaFuJJC.KuaFuJJCMgr", "CrossToLogicJJCUnionTodayScore", datadict)
	
	
#===============================================================================
# 设置数组改变调用的函数
#===============================================================================
def AfterChangeKuaFuJJCElectionScore(role, oldValue, newValue):
	roleId = role.GetRoleID()
	if roleId not in KUAFU_JJC_ROLE_DICT:
		return
	
	kuaFuJJCRole = KUAFU_JJC_ROLE_DICT[roleId]
	kuaFuJJCRole.role_election_score = role.GetI32(EnumInt32.KuaFuJJCElectionScore)
	#保存
	kuaFuJJCRole.HasChange()
	
def AfterChangeKuaFuJJCFinalsScore(role, oldValue, newValue):
	roleId = role.GetRoleID()
	if roleId not in KUAFU_JJC_ROLE_DICT:
		return
	
	kuaFuJJCRole = KUAFU_JJC_ROLE_DICT[roleId]
	kuaFuJJCRole.role_finals_score = role.GetI32(EnumInt32.KuaFuJJCFinalsScore)
	#保存
	kuaFuJJCRole.HasChange()
	
#===============================================================================
# 逻辑进程请求
#===============================================================================
def LogicToCrossJJCDataCall(msg):
	
	zoneId, kuaFuJJCDataDict = msg
	
	global ZONEID_TO_JJC_ROLE_DATA_FROM_LOGIC
	global KUAFU_JJC_CROSS_ELECTION_ROLEID_LIST
	global KUAFU_JJC_CROSS_ROLEID_TO_ZONEID_DICT
	
	#缓存逻辑进程发送过来的竞技场数据
	if zoneId not in ZONEID_TO_JJC_ROLE_DATA_FROM_LOGIC:
		ZONEID_TO_JJC_ROLE_DATA_FROM_LOGIC[zoneId] = {}
	ZONEID_TO_JJC_ROLE_DATA_FROM_LOGIC[zoneId].update(kuaFuJJCDataDict)
	
	#保存海选资格roleId
	KUAFU_JJC_CROSS_ELECTION_ROLEID_LIST.extend(kuaFuJJCDataDict.keys())
	
	#保存区域ID
	for roleId in kuaFuJJCDataDict.iterkeys():
		KUAFU_JJC_CROSS_ROLEID_TO_ZONEID_DICT[roleId] = zoneId
		
def LogicRequestCrossPalaceDataCall(msg):
	zoneId, processId, roleId = msg
	
	if zoneId not in KUAFU_JJC_CROSS_PALACE_DATA:
		return
	
	palaceData = KUAFU_JJC_CROSS_PALACE_DATA[zoneId]
	if not palaceData:
		return

	Call.ServerCall(processId, "Game.KuaFuJJC.KuaFuJJCMgr", "CrossToLogicJJCPalaceData", (roleId, palaceData))
	
#===============================================================================
# 客户端请求
#===============================================================================
def RequestKuaFuJJCElectionChallenge(role, msg):
	'''
	客户端请求跨服组队竞技场海选挑战
	@param role:
	@param msg:
	'''
	desRoleId = msg
	
	#判断活动时间
	t = cDateTime.Now().time()
	if t < KuaFuJJCConfig.ELECTION_START_TIME or t > KuaFuJJCConfig.ELECTION_END_TIME:
		return
	
	ElectionChallenge(role, desRoleId)
	
def RequestKuaFuJJCFinalsChallenge(role, msg):
	'''
	客户端请求跨服组队竞技场决赛挑战
	@param role:
	@param msg:
	'''
	desRoleId = msg
	
	if KuaFuJJCConfig.IsFinals() is False:
		return
	
	FinalsChallenge(role, desRoleId)
	
def RequestKuaFuJJCOpenRoleElectionRank(role, msg):
	'''
	客户端请求打开跨服个人竞技场个人海选积分榜
	@param role:
	@param msg:
	'''
	ShowRoleElectionRank(role)
	
def RequestKuaFuJJCOpenUnionElectionRank(role, msg):
	'''
	客户端请求打开跨服个人竞技场公会海选积分榜
	@param role:
	@param msg:
	'''
	ShowUnionElectionRank(role)
	
def RequestKuaFuJJCOpenRoleFinalsRank(role, msg):
	'''
	客户端请求打开跨服个人竞技场个人决赛积分榜
	@param role:
	@param msg:
	'''
	ShowRoleFinalsRank(role)
	
def RequestKuaFuJJCBuyChallengeCnt(role, msg):
	'''
	客户端请求跨服个人竞技场购买挑战次数
	@param role:
	@param msg:
	'''
	#日志
	with TraKFJJCBuyCnt:
		BuyChallengeCnt(role)
	
def RequestKuaFuJJCResetRound(role, msg):
	'''
	客户端请求跨服个人竞技场重置轮数
	@param role:
	@param msg:
	'''
	#日志
	with TraKFJJCResetRound:
		ResetRound(role)

def RequstKuaFuJJCFinalsRefresh(role, msg):
	'''
	客户端请求跨服个人竞技场决赛手动刷新
	@param role:
	@param msg:
	'''
	#是否有决赛资格
	if CanChallengeFinals(role) is False:
		return
	
	#日志
	with TraKFJJCFinalsRefresh:
		FinalsRefreshUseMoney(role)

def RequstKuaFuJJCLeaveScene(role, msg):
	'''
	客户端请求离开跨服竞技场场景
	@param role:
	@param msg:
	'''
	role.GotoLocalServer(None, None)
	
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.EnvIsQQ() or Environment.EnvIsFT() or (Environment.EnvIsNA() and not Environment.IsNAPLUS1) or Environment.IsDevelop) and Environment.IsCross:
		#持久化数据
		KUAFU_JJC_BT = BigTable.BigTable("sys_kuafu_jjc", 100, KuaFuJJCBTAfterLoad)
		#跨服个人竞技场海选资格roleId列表
		KUAFU_JJC_CROSS_ELECTION_ROLEID_LIST = Contain.List("KUAFU_JJC_CROSS_ELECTION_ROLEID_LIST", (2038, 1, 1), KuaFuJJCCrossRoleIdListAfterLoad)
		#跨服个人竞技场角色对应区域字典{roleId: zoneId},每日十点，跨服竞技1-6天由逻辑进程发过来，玩家进入跨服场景时也会进行赋值
		KUAFU_JJC_CROSS_ROLEID_TO_ZONEID_DICT = Contain.Dict("KUAFU_JJC_CROSS_ROLEID_TO_ZONEID_DICT", (2038, 1, 1), KuaFuJJCCrossRoleIdToZoneIdDictAfterLoad)
		#跨服个人竞技场排行榜
		KUAFU_JJC_CROSS_RANK = Contain.Dict("KUAFU_JJC_CROSS_RANK", (2038, 1, 1), KuaFuJJCCrossRankAfterLoad)
		#跨服个人竞技场区域ID对应分组
		KUAFU_JJC_CROSS_ZONEID_TO_GROUP = Contain.Dict("KUAFU_JJC_CROSS_ZONEID_TO_GROUP", (2038, 1, 1), KuaFuJJCCrossZoneIdToGroupAfterLoad)
		#跨服个人竞技场公会积分
		KUAFU_JJC_CROSS_UNION_SCORE = Contain.Dict("KUAFU_JJC_CROSS_UNION_SCORE", (2038, 1, 1), KuaFuJJCCrossUnionScoreAfterLoad)
		#跨服个人竞技场公会今日积分
		KUAFU_JJC_CROSS_UNION_TODAY_SCORE = Contain.Dict("KUAFU_JJC_CROSS_UNION_TODAY_SCORE", (2038, 1, 1), KuaFuJJCCrossUnionTodayScoreAfterLoad)
		#跨服个人竞技场公会进程ID
		KUAFU_JJC_CROSS_UNION_PROCESS_ID = Contain.Dict("KUAFU_JJC_CROSS_UNION_PROCESS_ID", (2038, 1, 1), KuaFuJJCCrossUnionProcessIdAfterLoad)
		#跨服个人竞技场龙骑殿堂数据
		KUAFU_JJC_CROSS_PALACE_DATA = Contain.Dict("KUAFU_JJC_CROSS_PALACE_DATA", (2038, 1, 1), KuaFuJJCCrossPalaceDataAfterLoad)
		
		#每日调用
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
		#事件
		Event.RegEvent(Event.Eve_AfterLoadWorldData, AfterLoadWorldData)
		
		#设置数组改变调用的函数
		cRoleDataMgr.SetInt32Fun(EnumInt32.KuaFuJJCElectionScore, AfterChangeKuaFuJJCElectionScore)
		cRoleDataMgr.SetInt32Fun(EnumInt32.KuaFuJJCFinalsScore, AfterChangeKuaFuJJCFinalsScore)
		
		#时间
		Cron.CronDriveByMinute((2038, 1, 1), TodayElectionOver, H = "H == 21", M = "M == 55")
		Cron.CronDriveByMinute((2038, 1, 1), FinalsOver, H = "H == 22", M = "M == 30")
		Cron.CronDriveByMinute((2038, 1, 1), Per30Minutes, M = "M == 0 or M == 30")
		
		#日志
		TraKFJJCElectionWin = AutoLog.AutoTransaction("TraKFJJCElectionWin", "跨服个人竞技场海选挑战胜利")
		TraKFJJCElectionLost = AutoLog.AutoTransaction("TraKFJJCElectionLost", "跨服个人竞技场海选挑战失败")
		TraKFJJCFinalsWin = AutoLog.AutoTransaction("TraKFJJCFinalsWin", "跨服个人竞技场决赛挑战胜利")
		TraKFJJCFinalsLost = AutoLog.AutoTransaction("TraKFJJCFinalsLost", "跨服个人竞技场决赛挑战失败")
		TraKFJJCResetRound = AutoLog.AutoTransaction("TraKFJJCResetRound", "跨服个人竞技场重置轮数")
		TraKFJJCBuyCnt = AutoLog.AutoTransaction("TraKFJJCBuyCnt", "跨服个人竞技场购买行动力")
		TraKFJJCInFinalsList = AutoLog.AutoTransaction("TraKFJJCInFinalsList", "跨服个人竞技场进入决赛名单")
		TraKFJJCFinalsRewardRank = AutoLog.AutoTransaction("TraKFJJCFinalsRewardRank", "跨服个人竞技场决赛奖励排名")
		TraKFJJCFinalsMail = AutoLog.AutoTransaction("TraKFJJCFinalsMail", "跨服个人竞技场决赛邮件")
		TraKFJJCFinalsRefresh = AutoLog.AutoTransaction("TraKFJJCFinalsRefresh", "跨服个人竞技场决赛手动刷新")
		
		
		#客户端请求消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KuaFu_JJC_Cross_Election_Challenge", "客户端请求跨服个人竞技场海选挑战"), RequestKuaFuJJCElectionChallenge)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KuaFu_JJC_Cross_Finals_Challenge", "客户端请求跨服个人竞技场决赛挑战"), RequestKuaFuJJCFinalsChallenge)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KuaFu_JJC_Cross_Open_Role_Election_Score_Rank", "客户端请求打开跨服个人竞技场个人海选积分榜"), RequestKuaFuJJCOpenRoleElectionRank)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KuaFu_JJC_Cross_Open_Union_Election_Score_Rank", "客户端请求打开跨服个人竞技场公会海选积分榜"), RequestKuaFuJJCOpenUnionElectionRank)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KuaFu_JJC_Cross_Open_Role_Finals_Score_Rank", "客户端请求打开跨服个人竞技场个人决赛积分榜"), RequestKuaFuJJCOpenRoleFinalsRank)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KuaFu_JJC_Cross_Buy_Challenge_Cnt", "客户端请求跨服个人竞技场购买挑战次数"), RequestKuaFuJJCBuyChallengeCnt)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KuaFu_JJC_Cross_Reset_Round", "客户端请求跨服个人竞技场重置轮数"), RequestKuaFuJJCResetRound)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KuaFu_JJC_Cross_Finals_Refresh", "客户端请求跨服个人竞技场决赛手动刷新"), RequstKuaFuJJCFinalsRefresh)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KuaFu_JJC_Cross_Leave_Scene", "客户端请求离开跨服个人竞技场场景"), RequstKuaFuJJCLeaveScene)
		
		
