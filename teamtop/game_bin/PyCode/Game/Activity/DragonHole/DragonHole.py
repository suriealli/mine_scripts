#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DragonHole.DragonHole")
#===============================================================================
# 勇闯龙窟，这个只有繁体版有哦
#===============================================================================
import cRoleMgr
import Environment
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, EnumFightStatistics
from Game.Fight import Fight
from Game.Scene import PublicScene
from Game.Role import Status, Event
from Game.Role.Data import EnumInt1, EnumInt32
from Game.Activity.DragonHole import DragonHoleConfig

if "_HasLoad" not in dir():
	Scene_List = [340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354]	#场景ID列表
	Monster_Postion = [(1374, 786), (2167, 593), (2684, 935), (3478, 605), (2609, 1427), \
					(2467, 1881), (3393, 2136), (1881, 2032), (1162, 1985), (803, 1654)] #刷怪点
	Monster_ID = 1085	#怪ID
	TP_X, TP_Y = 614, 429	#传送坐标
	Max_Fight_NPC = 20		#场景的怪物数
	Max_Role_Number = 50	#每个场景的最大人数
	
	Can_Join_Scene_ID = 340
	DragonHoleObjDict = {}

	#日志
	Tra_DragonHoleReward = AutoLog.AutoTransaction("Tra_DragonHoleReward", "勇闯龙窟击杀怪物奖励")

class DragonHole(object):
	def __init__(self, sceneId):
		self.sceneId = sceneId
		self.NPC_List = []		#npc对象列表
		self.NPCID_List = []	#npcId列表
		self.role_list = set()	#该场景中的玩家ID
		self.scene = None		#场景，当场景创建成功后置为场景，见AfterCreatFun

	def FirstCreateNPC(self):
		#第一次创建的怪
		#每个坐标刷的怪数
		times = Max_Fight_NPC / len(Monster_Postion)
		for pos in Monster_Postion:
			for _ in xrange(times):
				self.CreateOneNPC(pos[0], pos[1])
		
	def CreateOneNPC(self, x, y):
		#创建一NPC
		npc = self.scene.CreateNPC(Monster_ID, x, y, 1, 1)
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
		global Can_Join_Scene_ID
		#人数已达标
		if len(self.role_list) >= Max_Role_Number:
			#获取当前可进场景在场景列表中的index
			old_index = Scene_List.index(Can_Join_Scene_ID)
			#已经是最后个场景了,下个可进场景为场景列表的第一个
			if old_index + 1 >= len(Scene_List):
				Can_Join_Scene_ID = Scene_List[0]
			else:
				#下个可进场景为场景列表的下一个
				Can_Join_Scene_ID = Scene_List[old_index + 1]
				
	def AfterBeforeLeave(self, role):
		#玩家离开场景
		roleId = role.GetRoleID()
		if roleId in self.role_list:
			self.role_list.remove(roleId)

def BackpublicScene(role, callargv, regparam):
	global Scene_List
	if role.GetSceneID() in Scene_List:
		role.BackPublicScene()

def InitDragonHole(*param):
	#初始化场景
	global Scene_List
	global DragonHoleObjDict
	for sceneId in Scene_List:
		DragonHoleObjDict[sceneId] = DragonHole(sceneId)

#==============================================================
#角色事件
#==============================================================
def OnRoleClientLost(role, param):
	#角色客户端掉线
	if role.GetSceneID() in Scene_List:
		role.BackPublicScene()

def RoleDayClear(role, param):
	#玩家每日清理
	role.SetI32(EnumInt32.DragonHoleDailyExp, 0)

#==============================================================
#场景处理
#==============================================================
def AfterJoinScene(scene, role):
	sceneId = scene.GetSceneID()
	FBObj = DragonHoleObjDict.get(sceneId)
	if FBObj:
		FBObj.AfterJoin(role)

def BeforeLevelScene(scene, role):
	sceneId = scene.GetSceneID()
	FBObj = DragonHoleObjDict.get(sceneId)
	if FBObj:
		FBObj.AfterBeforeLeave(role)

def AfterCreatFun(scene):
	sceneId = scene.GetSceneID()
	FBObj = DragonHoleObjDict.get(sceneId)
	if FBObj:
		FBObj.scene = scene
		FBObj.FirstCreateNPC()

def RegSceneFun():
	for SceneId in Scene_List:
		PublicScene.RegSceneAfterJoinRoleFun(SceneId)(AfterJoinScene)
		PublicScene.RegSceneBeforeLeaveFun(SceneId)(BeforeLevelScene)
		PublicScene.RegSceneAfterCreateFun(SceneId)(AfterCreatFun)

#==============================================================
#战斗处理
#==============================================================
def PVE_DragonHole(role, fightType, mcid):
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
	pass

def AfterFight(fight):
	#无论输赢打了就给奖励,根据玩家等级取配置
	roles = fight.left_camp.roles
	if not roles:
		return
	role = list(roles)[0]
	roleId = role.GetRoleID()
	cfg = DragonHoleConfig.DragonHoleConfigDict.get(role.GetLevel())
	if not cfg:
		print "GE_EXC,error while cfg = DragonHoleConfig.DragonHoleConfigDict.get(role.GetLevel()), no such rolelevel(%s)" % role.GetLevel()
		return
	#每日获取经验上限已满
	now_exp = role.GetI32(EnumInt32.DragonHoleDailyExp)
	if now_exp >= cfg.maxExp:
		return
	#每日获得的经验是不能超过最大经验的
	exp_to_inc = min(cfg.addExp, cfg.maxExp - now_exp)
	fight.set_fight_statistics(roleId, EnumFightStatistics.EnumExp, exp_to_inc)
	with Tra_DragonHoleReward:
		role.IncI32(EnumInt32.DragonHoleDailyExp, exp_to_inc)
		role.IncExp(exp_to_inc)

#==============================================================
#角色请求
#==============================================================
def RequestEnterScene(role, param):
	'''
	客户端请求进入龙窟
	@param role:
	@param param:
	'''
	#玩家等级不足
	if role.GetLevel() < EnumGameConfig.DragonHoleNeedLevel:
		return
	#已经在该地图
	if role.GetSceneID() in Scene_List:
		return
	#角色状态判断
	if not Status.CanInStatus(role, EnumInt1.ST_TP):
		return
	#传送
	role.Revive(Can_Join_Scene_ID, TP_X, TP_Y)

def RequestExitScene(role, param):
	'''
	客户端请求退出龙窟
	@param role:
	@param param:
	'''
	if role.GetSceneID() in Scene_List:
		role.BackPublicScene()

def RequestFight(role, param):
	'''
	客户端请求战斗
	@param role:
	@param param:
	'''
	#玩家等级不足
	if role.GetLevel() < EnumGameConfig.DragonHoleNeedLevel:
		return
	#玩家不在指定的场景中
	sceneId = role.GetSceneID()
	if sceneId not in Scene_List:
		return
	#战斗状态
	if Status.IsInStatus(role, EnumInt1.ST_FightStatus):
		return
	cfg = DragonHoleConfig.DragonHoleConfigDict.get(role.GetLevel())
	if not cfg:
		print "GE_EXC,error while cfg = DragonHoleConfig.DragonHoleConfigDict.get(role.GetLevel()), no such rolelevel(%s)" % role.GetLevel()
		return
	if not cfg.campId or not cfg.fightType:
		return
	#战斗
	PVE_DragonHole(role, cfg.fightType, cfg.campId)

#if "_HasLoad" not in dir():
#	if Environment.HasLogic and (Environment.EnvIsFT() or Environment.IsDevelop) and not Environment.IsCross:
#		#注册场景函数
#		RegSceneFun()
#		#初始化龙窟
#		InitDragonHole()
#		#事件
#		Event.RegEvent(Event.Eve_ClientLost, OnRoleClientLost)
#		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
#		
#		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestJoinDragonHole", "客户端请求进入勇闯龙窟"), RequestEnterScene)
#		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestExitDragonHole", "客户端请求退出勇闯龙窟"), RequestExitScene)
#		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestDragonHoleFight", "客户端请求勇闯龙窟杀怪"), RequestFight)
