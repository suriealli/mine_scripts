#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.NationalDayFB.NationalDayFB")
#===============================================================================
# 国庆副本
#===============================================================================
import random
import Environment
import cSceneMgr
import cRoleMgr
import cComplexServer
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, EnumFightStatistics, GlobalPrompt
from Game.Fight import Fight
from Game.Scene import PublicScene
from Game.Role import Status, Event
from Game.Persistence import Contain
from Game.Role.Data import EnumInt1, EnumInt32, EnumObj
from Game.Activity import CircularDefine
from Game.Activity.NationalDayFB import NationalDayFBConfig

if "_HasLoad" not in dir():
	
	FB_SENCEID_LIST = [300,301,302,303,304,305,306,307,308,309]	#副本场景ID列表
	MONSTER_POS_X_Y = [(1374,786),(2167,593),(2684,935),(3478,605),(2609,1427), \
						(2467,1881),(3393,2136),(1881,2032),(1162,1985),(803,1654)]#各种刷怪的坐标
	MONSTER_ID = 1085	#怪ID
	TP_X, TP_Y = 614, 429	#传送坐标
	MAX_FIGHT_NPC = 20		#场景的怪物数
	MAX_ROLE_SCENCE = 50	#每个场景的最大人数
	
	DB_INDEX_1 = 1	#DB索引
	
	CAN_JOIN_SCENE_ID = 300	#玩家可进入的场景
	
	IS_START = False	#活动开启标志
	
	SCENEID_FBOBJ_DICT = {}	#senceId->副本对象
	
	NDFB_GlobalKill = AutoMessage.AllotMessage("NDFB_GlobalKill", "返回国庆副本全民战斗数据")
	#日志
	NDFBKillReward = AutoLog.AutoTransaction("NDFBKillReward", "国庆副本杀怪奖励")
	NDFBGlobalReward = AutoLog.AutoTransaction("NDFBGlobalReward", "国庆副本全民战斗奖励")
#=================================循环活动开启关闭==========================
def StartCircularActive(*param):
	'''
	国庆活动副本开启
	'''
	_, activetype = param
	if activetype != CircularDefine.ND_FB:
		return
	global IS_START
	if IS_START:
		print "GE_EXC, NationalDayFB is already started "
		return
	IS_START = True
	
	#初始化各个场景副本
	InitNationFB()

def EndCircularActive(*param):
	'''
	国庆活动副本关闭
	'''
	_, activetype = param
	if activetype != CircularDefine.ND_FB:
		return
	global IS_START
	if not IS_START:
		print "GE_EXC, NationalDayFB is already ended "
		return
	IS_START = False
	#清空数据
	clearData()
#=============================================================

class NationalDayFB(object):
	def __init__(self, sceneId):
		self.sceneId = sceneId
		self.NPC_List = []		#npc对象列表
		self.NPCID_List = []	#npcId列表
		self.scene = cSceneMgr.SearchPublicScene(self.sceneId)
		if not self.scene:
			print "GE_EXC, NationalDayFB can not find sceneId(%s)" % self.sceneId
			return
		self.role_list = set()		#该场景中的玩家ID
		self.FirstCreateNPC()
		
	def FirstCreateNPC(self):
		#第一次创建的怪
		global IS_START
		global MONSTER_POS_X_Y
		
		if IS_START is False:
			return
		#每个坐标刷的怪数
		times = MAX_FIGHT_NPC / len(MONSTER_POS_X_Y)
		
		for pos in MONSTER_POS_X_Y:
			for _ in xrange(times):
				self.CreateOneNPC(pos[0], pos[1])
				
	def DelOneNPC(self, npc):
		#删除一NPC
		npcId = npc.GetNPCID()
		if npcId in self.NPCID_List:
			self.NPCID_List.remove(npcId)
		if npc in self.NPC_List:
			self.NPC_List.remove(npc)
		self.scene.DestroyNPC(npcId)
		
	def CreateOneNPC(self, x, y):
		#创建一NPC
		global IS_START
		if IS_START is False:
			return
		npc = self.scene.CreateNPC(MONSTER_ID, x, y, 1, 1)
		self.NPC_List.append(npc)
		self.NPCID_List.append(npc.GetNPCID())
		
	def AfterJoin(self, role):
		#玩家进入场景
		roleId = role.GetRoleID()
		if roleId not in self.role_list:
			self.role_list.add(roleId)
		#判断该场景
		self.JudgeScene()
			
	def JudgeScene(self):
		#判断场景是否已满，是否激活下个场景ID
		global FB_SENCEID_LIST
		global CAN_JOIN_SCENE_ID
		#人数已达标
		if len(self.role_list) >= MAX_ROLE_SCENCE:
			#获取当前可进场景在场景列表中的index
			old_index = FB_SENCEID_LIST.index(CAN_JOIN_SCENE_ID)
			#已经是最后个场景了,下个可进场景为场景列表的第一个
			if old_index + 1 >= len(FB_SENCEID_LIST):
				CAN_JOIN_SCENE_ID = FB_SENCEID_LIST[0]
			else:
				#下个可进场景为场景列表的下一个
				CAN_JOIN_SCENE_ID = FB_SENCEID_LIST[old_index + 1]
				
	def AfterBeforeLeave(self, role):
		#玩家离开场景
		roleId = role.GetRoleID()
		if roleId in self.role_list:
			self.role_list.remove(roleId)
	
	def ClearData(self):
		#清理玩家,将里面的玩家传出
		role_list = []
		role_list.extend(self.role_list)
		for roleId in role_list:
			role = cRoleMgr.FindRoleByRoleID(roleId)
			if role:
				role.RegTick(10, Back, None)
		self.role_list = set()
		
		#清理NPC
		npc_list = []
		npc_list.extend(self.NPC_List)
		for npc in npc_list:
			self.DelOneNPC(npc)

def Back(role, callargv, regparam):
	global FB_SENCEID_LIST
	
	if role.GetSceneID() in FB_SENCEID_LIST:
		role.BackPublicScene()
		
def InitNationFB():
	#初始化场景
	global FB_SENCEID_LIST
	global SCENEID_FBOBJ_DICT
	
	#初始化之前，先清理次数据，防止重复创建
	for _, obj in SCENEID_FBOBJ_DICT.iteritems():
		obj.ClearData()
	SCENEID_FBOBJ_DICT = {}

	for sceneId in FB_SENCEID_LIST:
		SCENEID_FBOBJ_DICT[sceneId] = NationalDayFB(sceneId)

def clearData():
	#清除数据
	global NationDayKillData
	global SCENEID_FBOBJ_DICT
	global CAN_JOIN_SCENE_ID
	
	#清空全服战斗数
	NationDayKillData.clear()
	#可进场景重置为第一个场景
	CAN_JOIN_SCENE_ID = 300
	
	for _, obj in SCENEID_FBOBJ_DICT.iteritems():
		obj.ClearData()
	SCENEID_FBOBJ_DICT = {}

def IncGlobalKillTimes():
	#增加全服击杀次数
	global NationDayKillData
	
	NationDayKillData[DB_INDEX_1] = NationDayKillData.get(DB_INDEX_1, 0) + 1
	NationDayKillData.changeFlag = True
	
	nowKill = NationDayKillData.get(DB_INDEX_1, 0)
	#达到相应的击杀数，发世界公告
	if nowKill in NationalDayFBConfig.NATION_KILLCNT_LIST:
		cRoleMgr.Msg(11, 0, GlobalPrompt.ND_KILL_MSG % nowKill)
#=============================玩家事件============================
def OnRoleClientLost(role, param):
	#角色客户端掉线
	global FB_SENCEID_LIST
	
	if role.GetSceneID() in FB_SENCEID_LIST:
		role.BackPublicScene()
		
def RoleDayClear(role, param):
	#玩家每日清理
	role.SetI32(EnumInt32.NationFBDayExp, 0)
	#清空每日的已领取记录
	NationData = role.GetObj(EnumObj.NationData)
	NationData[1] = set()
	
def AfterLogin(role, param):
	#玩家登陆后
	NationData = role.GetObj(EnumObj.NationData)
	if 1 not in NationData:
		NationData[1] = set()
	if 2 not in NationData:
		NationData[2] = set()
#=====================================================
def PVE_NDFB(role, fightType, mcid):
	fight = Fight.Fight(fightType)
	# 可收到设置客户端断线重连是否还原战斗,默认不还原
	fight.restore = True
	#创建两个阵营
	left_camp, right_camp = fight.create_camp()
	#在阵营中创建战斗单位
	left_camp.create_online_role_unit(role, role.GetRoleID())
	right_camp.create_monster_camp_unit(mcid)
	#设置回调函数
	fight.after_fight_fun = AfterFight		#战斗结束
	fight.after_play_fun = AfterPlay		#客户端播放完毕
	fight.start()
	
def AfterPlay(fight):
	#role.SetCD(EnumCD., nValue)
	pass

def AfterFight(fight):
	#无论输赢都给奖励,根据玩家等级取配置
	roles = fight.left_camp.roles
	if not roles:
		return
	role = list(roles)[0]
	roleId = role.GetRoleID()
	
	cfg = NationalDayFBConfig.NATION_KILL_REWARD_DICT.get(role.GetLevel())
	if not cfg:
		print "GE_EXC,can not find level(%s) in NationalDayFB.AfterPlay" % role.GetLevel()
		return
	#每日获取经验上限已满
	if role.GetI32(EnumInt32.NationFBDayExp) >= cfg.maxExp:
		return
	fight.set_fight_statistics(roleId, EnumFightStatistics.EnumExp, cfg.addExp)
	
	with NDFBKillReward:
		role.IncI32(EnumInt32.NationFBDayExp, cfg.addExp)
		role.IncExp(cfg.addExp)
		#两个物品的随机是相对独立的
		random_value1 = random.randint(1, 10000)
		if random_value1 <= cfg.pro1:
			for reward in cfg.rewards1:
				role.AddItem(*reward)
			fight.set_fight_statistics(roleId, EnumFightStatistics.EnumItems, cfg.rewards1)
		
		random_value2 = random.randint(1, 10000)
		if random_value2 <= cfg.pro2:
			for reward in cfg.rewards2:
				role.AddItem(*reward)
			fight.set_fight_statistics(roleId, EnumFightStatistics.EnumItems, cfg.rewards2)
#=====================场景=========================
@PublicScene.RegSceneAfterJoinRoleFun(300)
def AfterJoin1(scene, role):
	AfterJoinScene(scene, role)

@PublicScene.RegSceneAfterJoinRoleFun(301)
def AfterJoin2(scene, role):
	AfterJoinScene(scene, role)

@PublicScene.RegSceneAfterJoinRoleFun(302)
def AfterJoin3(scene, role):
	AfterJoinScene(scene, role)

@PublicScene.RegSceneAfterJoinRoleFun(303)
def AfterJoin4(scene, role):
	AfterJoinScene(scene, role)

@PublicScene.RegSceneAfterJoinRoleFun(304)
def AfterJoin5(scene, role):
	AfterJoinScene(scene, role)

@PublicScene.RegSceneAfterJoinRoleFun(305)
def AfterJoin6(scene, role):
	AfterJoinScene(scene, role)

@PublicScene.RegSceneAfterJoinRoleFun(306)
def AfterJoin7(scene, role):
	AfterJoinScene(scene, role)

@PublicScene.RegSceneAfterJoinRoleFun(307)
def AfterJoin8(scene, role):
	AfterJoinScene(scene, role)

@PublicScene.RegSceneAfterJoinRoleFun(308)
def AfterJoin9(scene, role):
	AfterJoinScene(scene, role)

@PublicScene.RegSceneAfterJoinRoleFun(309)
def AfterJoin10(scene, role):
	AfterJoinScene(scene, role)

@PublicScene.RegSceneBeforeLeaveFun(300)
def BeforeLeave(scene, role):
	BeforeLevelScene(scene, role)

@PublicScene.RegSceneBeforeLeaveFun(301)
def BeforeLeave1(scene, role):
	BeforeLevelScene(scene, role)

@PublicScene.RegSceneBeforeLeaveFun(302)
def BeforeLeave2(scene, role):
	BeforeLevelScene(scene, role)

@PublicScene.RegSceneBeforeLeaveFun(303)
def BeforeLeave3(scene, role):
	BeforeLevelScene(scene, role)

@PublicScene.RegSceneBeforeLeaveFun(304)
def BeforeLeave4(scene, role):
	BeforeLevelScene(scene, role)

@PublicScene.RegSceneBeforeLeaveFun(305)
def BeforeLeave5(scene, role):
	BeforeLevelScene(scene, role)

@PublicScene.RegSceneBeforeLeaveFun(306)
def BeforeLeave6(scene, role):
	BeforeLevelScene(scene, role)

@PublicScene.RegSceneBeforeLeaveFun(307)
def BeforeLeave7(scene, role):
	BeforeLevelScene(scene, role)

@PublicScene.RegSceneBeforeLeaveFun(308)
def BeforeLeave8(scene, role):
	BeforeLevelScene(scene, role)

@PublicScene.RegSceneBeforeLeaveFun(309)
def BeforeLeave9(scene, role):
	BeforeLevelScene(scene, role)

def AfterJoinScene(scene, role):
	global SCENEID_FBOBJ_DICT
	sceneId = scene.GetSceneID()
	FBObj = SCENEID_FBOBJ_DICT.get(sceneId)
	if FBObj:
		FBObj.AfterJoin(role)

def BeforeLevelScene(scene, role):
	global SCENEID_FBOBJ_DICT
	sceneId = scene.GetSceneID()
	FBObj = SCENEID_FBOBJ_DICT.get(sceneId)
	if FBObj:
		FBObj.AfterBeforeLeave(role)
#=============================客户端消息================================
def RequestNDFBEnterScene(role, param):
	'''
	客户端请求进入副本
	@param role:
	@param param:
	'''
	if IS_START is False:#未开启
		return
	#玩家等级不足
	if role.GetLevel() < EnumGameConfig.NATION_MIN_LEVEL:
		return
	#已经在该地图
	if role.GetSceneID() in FB_SENCEID_LIST:
		return
	#传送前判断是否能进入传送状态
	if not Status.CanInStatus(role, EnumInt1.ST_TP):
		return
	#传送
	role.Revive(CAN_JOIN_SCENE_ID, TP_X, TP_Y)

def RequestNDFBExitScene(role, param):
	'''
	客户端请求退出副本
	@param role:
	@param param:
	'''
	global FB_SENCEID_LIST
	
	if role.GetSceneID() in FB_SENCEID_LIST:
		role.BackPublicScene()
		
def RequestNDFBOpenPanel(role, param):
	'''
	客户端请求打开全民战斗界面
	@param role:
	@param param:
	'''
	global NationDayKillData
	
	if IS_START is False:#未开启
		return
	
	NationData = role.GetObj(EnumObj.NationData)
	GetedSet = NationData.get(1, set())
	
	role.SendObj(NDFB_GlobalKill, (NationDayKillData.get(1), GetedSet))
	
def RequestNDFBGetReward(role, param):
	'''
	客户端请求获取全民战斗奖励
	@param role:
	@param param:
	'''
	index = param
	#未开启
	if IS_START is False:
		return
	
	NationData = role.GetObj(EnumObj.NationData)
	GetedSet = NationData.get(1, set())
	if index in GetedSet:#已经领取了
		return
	
	cfg = NationalDayFBConfig.NATION_GLOBAL_REWARD_DICT.get(index)
	if not cfg:
		print "GE_EXC, can not find index(%s) in RequestNDFBGetReward" % index
		return
	
	global NationDayKillData
	#数量没达标
	if cfg.FightCnt > NationDayKillData.get(1, 0):
		return
	
	with NDFBGlobalReward:
		GetedSet.add(index)
		role.AddItem(cfg.rewards[0], cfg.rewards[1])
		
		role.SendObj(NDFB_GlobalKill, (NationDayKillData.get(1), GetedSet))


def RequestNDFBFight(role, param):
	'''
	客户端请求国庆副本战斗
	@param role:
	@param param:
	'''
	global IS_START
	global FB_SENCEID_LIST
	
	#还没开始
	if IS_START is False:
		return
	#玩家等级不足
	if role.GetLevel() < EnumGameConfig.NATION_MIN_LEVEL:
		return
	#玩家不在指定的场景中
	sceneId = role.GetSceneID()
	if sceneId not in FB_SENCEID_LIST:
		return
	#战斗状态
	if Status.IsInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	cfg = NationalDayFBConfig.NATION_KILL_REWARD_DICT.get(role.GetLevel())
	if not cfg:
		print "GE_EXC,can not find level(%s) in NationalDayFB.AfterPlay" % role.GetLevel()
		return
	if not cfg.campId or not cfg.fightType:
		return
	
	#增加全服战斗次数
	IncGlobalKillTimes()
	#战斗
	PVE_NDFB(role, cfg.fightType, cfg.campId)

#=================================================
def AfterNewDay():
	global IS_START
	if not IS_START : return
	
	global NationDayKillData
	if not NationDayKillData : return
	
	NationDayKillData[DB_INDEX_1] = 0
	
def NDFBKillDataAfterLoadDB():
	global NationDayKillData
	if DB_INDEX_1 not in NationDayKillData:
		NationDayKillData[DB_INDEX_1] = 0	#记录活动期间总的杀怪数
		
if "_HasLoad" not in dir():
	if Environment.HasLogic or Environment.HasWeb:
		NationDayKillData = Contain.Dict("NationDayKillData", (2038, 1, 1), NDFBKillDataAfterLoadDB, isSaveBig = False)
	
	if Environment.HasLogic and not Environment.IsCross:
		#事件
		Event.RegEvent(Event.Eve_ClientLost, OnRoleClientLost)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_StartCircularActive, StartCircularActive)
		Event.RegEvent(Event.Eve_EndCircularActive, EndCircularActive)	
		#跨天处理
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
		
	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NDFB_Join_Scene", "客户端请求进入国庆副本"), RequestNDFBEnterScene)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NDFB_Exit_Scene", "客户端请求退出国庆副本"), RequestNDFBExitScene)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NDFB_Open_GlobalPanel", "客户端请求打开全民战斗界面"), RequestNDFBOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NDFB_Get_GlobalReward", "客户端请求获取全民战斗奖励"), RequestNDFBGetReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NDFB_Request_Fight", "客户端请求国庆副本战斗"), RequestNDFBFight)
		
		