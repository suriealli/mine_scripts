#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.CrossTeamTower.CTTRank")
#===============================================================================
# 虚空幻境排行榜
#===============================================================================
import copy
import Environment
import cDateTime
import cSceneMgr
import cProcess
from Game.Persistence import Contain
from ComplexServer.Time import Cron
from ComplexServer.Log import AutoLog
from Game.SysData import WorldData
from World import Define
from Game.Role import Rank, Event
from Game.CrossTeamTower import CTTConfig
from Game.Role.Mail import Mail
from Common.Other import GlobalPrompt, EnumGameConfig
from Game.NPC import EnumNPCData
from Game.Activity.Title import Title

if "_HasLoad" not in dir():
	RANK_INDEX_1 = 1	#排行榜数据
	RANK_INDEX_2 = 2	#记录上周前3玩家
	MAX_RANK_NUM = 200	#排行榜最大人数
	CARRER, SEX = 1, 1 	#默认雕像的职业和性别
	#3个雕像的坐标朝向
	STATUE_DATA = {1:(3643,370,1),2:(3666,277,1),3:(3449,386,1)}
	STATUE_OBJ = []		#缓存雕像对象
	#日志
	CTT_Rank_Data = AutoLog.AutoTransaction("CTT_Rank_Data", "虚空幻境周日结算前120名排行榜数据")
	CTT_Rank_Reward = AutoLog.AutoTransaction("CTT_Rank_Reward", "虚空幻境排行榜奖励")
	
class CTTRank(Rank.LittleRank):
	def __init__(self, maxRankSize):
		Rank.LittleRank.__init__(self, maxRankSize)
	
	# 返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		#(role.GetRoleName(), role.GetRoleID(), role.GetZDL(), fightRound, layer, zoneName, career, sex)
		return (v1[4], -v1[3], v1[2], v1[1]) < (v2[4], -v2[3], v2[2], v2[1])
	
	def Clear(self):
		#清理数据
		self.data = {}
		self.min_role_id = 0
		self.min_value = 0
		
def UpdateCTTRank(role, fightRound, layer):
	from Game.CrossTeamTower import CrossTTMgr
	zoneName = CrossTTMgr.GetRoleZoneName(role)
	CTT.HasData(role.GetRoleID(), [role.GetRoleName(), role.GetRoleID(), role.GetZDL(), fightRound, layer, zoneName, role.GetCareer(), role.GetSex()])
	#保存到持久化数据
	CROSS_TEAM_TOWER_RANK[RANK_INDEX_1] = copy.deepcopy(CTT.data)
	CROSS_TEAM_TOWER_RANK.changeFlag = True

def SortAndReward():
	if cDateTime.WeekDay() != 0:
		return
	global CROSS_TEAM_TOWER_RANK
	rankData = copy.deepcopy(CTT.data)
	
	dataList = rankData.values()
	dataList.sort(key = lambda u:(u[4], -u[3], u[2], u[1]), reverse = True)
	dataList = dataList[0:120]
	#这里保存前3玩家
	CROSS_TEAM_TOWER_RANK[RANK_INDEX_2] = dataList[0:3]
	CROSS_TEAM_TOWER_RANK.changeFlag = True
	
	with CTT_Rank_Data:
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveCrossTeamTowerRankData, dataList)
	
	for index, roledata in enumerate(dataList):
		roleId = roledata[1]
		index += 1
		key = CTTConfig.GetRightRankKey(index)
		if not key:
			continue
		cfg = CTTConfig.CTT_RANK_REWARD.get(key)
		if not cfg:
			continue
		with CTT_Rank_Reward:
			Mail.SendMail(roleId, GlobalPrompt.CTT_MAIL_TITLE, GlobalPrompt.CTT_MAIL_SENDER, GlobalPrompt.CTT_MAIL_CONTENT % index, items = cfg.itemReward)
			if cfg.titleId:
				Title.AddTitle(roleId, cfg.titleId)
	#清理数据
	ClearData()
	#创建雕像
	CreateStatue()
	
def ClearData():
	global CROSS_TEAM_TOWER_RANK
	global STATUE_OBJ
	
	CTT.Clear()
	CROSS_TEAM_TOWER_RANK[RANK_INDEX_1].clear()
	CROSS_TEAM_TOWER_RANK.changeFlag = True
	#清理雕像
	if not STATUE_OBJ:
		return
	scene = cSceneMgr.SearchPublicScene(EnumGameConfig.CTT_SCENE_ID)
	if not scene:
		print 'Ge_EXC, no scene = cSceneMgr.SearchPublicScene(SceneID),(%s)in CTTRank' % EnumGameConfig.CTT_SCENE_ID
		return
	for obj in STATUE_OBJ:
		scene.DestroyNPC(obj.GetNPCID())
	STATUE_OBJ = []
	
def CreateStatue():
	#创建雕像
	global CROSS_TEAM_TOWER_RANK
	global STATUE_DATA
	global STATUE_OBJ
	
	if STATUE_OBJ:
		return
	
	scene = cSceneMgr.SearchPublicScene(EnumGameConfig.CTT_SCENE_ID)
	if not scene:
		print 'Ge_EXC, no scene = cSceneMgr.SearchPublicScene(SceneID),(%s)in CTTRank' % EnumGameConfig.CTT_SCENE_ID
		return
	
	firstThirddata = CROSS_TEAM_TOWER_RANK.get(RANK_INDEX_2)
	statueData = {}
	if firstThirddata:
		for index, roledata in enumerate(firstThirddata):
			index += 1
			name,_,_,_,_,_,career,sex = roledata
			statueData[index] = (name, career, sex)
	
	for index in range(3):
		index += 1
		#默认的名字，职业和性别
		name = GlobalPrompt.CTT_STATUE_NO_DATA % index
		career, sex = CARRER, SEX
		
		data = statueData.get(index)
		if data:
			rolename, career, sex = data
			name = GlobalPrompt.CTT_STATUE_DATA %(index, rolename)
			
		cfg = CTTConfig.CTT_STATUE_DATA.get((career, sex))
		if not cfg:
			print 'GE_EXC, error in npctype = KaifuBossConfig.KaifuBossStatueDict.get((career, sex)),cannot find key %s' % (career, sex)
			continue
		x, y, p = STATUE_DATA[index]
		NPC = scene.CreateNPC(cfg.npctype, x, y, p, 1, {EnumNPCData.EnNPC_Name : name})
		STATUE_OBJ.append(NPC)
			
def CrossRankAfterLoad():
	global CROSS_TEAM_TOWER_RANK
	
	if RANK_INDEX_1 not in CROSS_TEAM_TOWER_RANK:
		CROSS_TEAM_TOWER_RANK[RANK_INDEX_1] = {}
	else:
		#还原排行榜
		rankDict = CROSS_TEAM_TOWER_RANK[RANK_INDEX_1]
		for roleId, data in rankDict.iteritems():
			CTT.HasData(roleId, data)
			
	if RANK_INDEX_2 not in CROSS_TEAM_TOWER_RANK:
		CROSS_TEAM_TOWER_RANK[RANK_INDEX_2] = []
	#缓存份数据
	global RANK_DATA
	RANK_DATA = CTT.data
	#创建雕像
	CreateStatue()

def OnAfterLoadWorldData(role, param):
	if not WorldData.WD.returnDB:
		return
	if not CROSS_TEAM_TOWER_RANK.returnDB:
		return
	#创建雕像
	CreateStatue()
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.EnvIsQQ() or Environment.EnvIsFT() or Environment.IsDevelop) and Environment.IsCross and cProcess.ProcessID == Define.GetCrossID_2():
		CTT = CTTRank(MAX_RANK_NUM)
		CROSS_TEAM_TOWER_RANK = Contain.Dict("CROSS_TEAM_TOWER_RANK", (2038, 1, 1), CrossRankAfterLoad)
		#周日的23.59分发奖并清数据
		Cron.CronDriveByMinute((2038, 1, 1), SortAndReward, H = "H == 23", M = "M == 59")
		
		Event.RegEvent(Event.Eve_AfterLoadWorldData, OnAfterLoadWorldData)