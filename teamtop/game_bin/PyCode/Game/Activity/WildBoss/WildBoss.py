#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.WildBoss.WildBoss")
#===============================================================================
# 新版野外寻宝
#===============================================================================
import Environment
import copy
import random
import cRoleMgr
import cDateTime
import cSceneMgr
import cProcess
import cNetMessage
import cComplexServer
from ComplexServer.Time import Cron
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig, EnumAward,\
	EnumFightStatistics
from World import Define
from ComplexServer.Log import AutoLog
from Game.DailyDo import DailyDo
from Game.SysData import WorldData
from Game.Role import Status, Event
from Game.Fight import Middle, Fight
from Game.GlobalData import ZoneName
from Game.Activity.Award import AwardMgr
from Game.NPC import EnumNPCData, NPCServerFun
from Game.Role.Data import EnumTempObj, EnumInt1, EnumCD
from Game.Activity.WildBoss import WildBossScene, WildBossConfig




if "_HasLoad" not in dir():
	#是否可以进入标志
	WildBoss_CanIn = False
	#战区索引index-->战区对象
	WildRegion_Dict = {}
	#roleId --> wildrole
	WildRole_Dict = {}

	########################################消息###############################################
	#小伤害排行榜{role_id --> [role_name, damage]}
	WildBossDamageRank = AutoMessage.AllotMessage("WildBossDamageRank", "野外寻宝伤害排行榜")
	#个人伤害值
	WildBossDamage = AutoMessage.AllotMessage("WildBossDamage", "野外寻宝个人伤害")
	#小宝箱排行榜{role_id --> [role_name, box_cnt]}
	WildBossBoxRank = AutoMessage.AllotMessage("WildBossBoxRank", "野外寻宝宝箱排行榜")
	#个人宝箱数据{宝箱coding:宝箱个数}
	WildBossBox = AutoMessage.AllotMessage("WildBossBox", "野外寻宝个人宝箱数据")
	#结算时同步的大宝箱排行榜{role_id --> [role_name, zone_name, box_cnt]}
	WildBossFinallyData = AutoMessage.AllotMessage("WildBossFinallyData", "野外寻宝最后结算数据")
	#最后结算时同步客户端自己的宝箱数量
	WildBossFinallyCnt = AutoMessage.AllotMessage("WildBossFinallyCnt", "野外寻宝最后结算时自己的宝箱数量")
	#[战区索引, 连杀数, buff玩家名字, 积分, [最大血量, 当前血量]]
	WildBossRoleData = AutoMessage.AllotMessage("WildBossRoleData", "野外寻宝玩家个人数据")
	#客户端退出是判断
	WildBossHp = AutoMessage.AllotMessage("WildBossHp", "野外寻宝boss血量")
	
	
	########################################日志###############################################
	WildBossScore_Log = AutoLog.AutoTransaction("WildBossScore_Log", "野外寻宝积分日志")
	WildBossDropBox_Log = AutoLog.AutoTransaction("WildBossDropBox_Log", "野外寻宝离线宝箱掉落日志")


##############################################################################################
#随机区域范围
#{key:(左上角X坐标, 左上角Y坐标, 右下角X坐标, 右下角Y坐标, 中心点X坐标, 中心点Y坐标}
RANDOM_POS = {1:(739,1204,813,1738,(739+1204)/2,(813+1738)/2), 2:(1407,2314,1126,1605,(1407+2314)/2,(1126+1605)/2), \
			3:(1538,2350,809,1115,(1538+2350)/2,(809+1115)/2), 4:(2469,2708,964,1593,(2469+2708)/2,(964+1593)/2), \
			5:(2778, 3339,1003, 1836,(3339+2778)/2,(1836+1003)/2), 6:(1555,2451,1635,1923,(1555+2451)/2,(1635+1923)/2)}

#场景最大人数
MaxSceneRole = 50

def GetDeadRevivePos():
	#获取随机复活点
	psx1, psx2, psy1, psy2, _, _ = RANDOM_POS[random.randint(1, 6)]
	return random.randint(psx1, psx2), random.randint(psy1, psy2),

def GetBoxDropPos():
	return RANDOM_POS[random.randint(1, 6)]

def RequstJoin(role, msg):
	'''
	请求进入野外寻宝
	@param role:
	@param msg:
	'''
	global WildBoss_CanIn
	if not WildBoss_CanIn: return
	
	
	
	level = role.GetLevel()
	if level < EnumGameConfig.WildBossMinLevel:
		return
	
	if role.GetZDL() < EnumGameConfig.WildBossZdl:
		return
	
	if not Status.CanInStatus(role, EnumInt1.ST_WildBoss):
		#不能进入野外寻宝状态
		return
	
	#每日必做
	Event.TriggerEvent(Event.Eve_DoDailyDo, role, (DailyDo.Daily_WildBoss, 1))
	#元旦金猪活动任务进度
	Event.TriggerEvent(Event.Eve_NewYearDayPigTask, role, (EnumGameConfig.NewYearDay_Task_WildBoss, True))
	
	
	#传送到一个过渡场景
	role.GotoCrossServer(None, 85, 958, 579, WildBossScene.AfterRevive, ZoneName.ZoneName)
	
def RequestLeave(role, msg):
	'''
	请求离开野外寻宝
	@param role:
	@param msg:
	'''

	wildrole = role.GetTempObj(EnumTempObj.WildRoleObj)
	if wildrole and wildrole.role:
		#玩家从战区中离开
		wildrole.leave()
	role.SetTempObj(EnumTempObj.WildRoleObj, None)
	
	#回到本地服
	role.GotoLocalServer(None, None)
	
def RequestFight(role, msg):
	'''
	请求挑战
	@param role:
	@param msg:
	'''
	global WildBoss_CanIn
	if not WildBoss_CanIn: return
	
	RequestPVP(role, msg)

def RequestFastFight(role, msg):
	'''
	请求追杀
	@param role:
	@param msg:
	'''
	global WildBoss_CanIn
	if not WildBoss_CanIn: return
	
	if role.GetCD(EnumCD.WildBossFastFightCD):
		return
	
	if RequestPVP(role, msg) is True:
		role.SetCD(EnumCD.WildBossFastFightCD, 15)

def RequestPVP(role, right_role_id):

	if not right_role_id:
		return
	left_role_id = role.GetRoleID()
	if left_role_id == right_role_id:
		return
	right_role = cRoleMgr.FindRoleByRoleID(right_role_id)
	if not right_role:
		return
	
	if role.GetCD(EnumCD.WildBossFightCD):
		return
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	if right_role.GetCD(EnumCD.WildBossProtectCD):
		#被挑战者有保护时间
		role.Msg(2, 0, GlobalPrompt.WildBoss_PropectionTime % right_role.GetCD(EnumCD.WildBossProtectCD))
		return
	if not Status.CanInStatus(right_role, EnumInt1.ST_FightStatus):
		#不能进入战斗状态
		role.Msg(2, 0, GlobalPrompt.WildBoss_InFight)
		return
	
	right_wildrole = right_role.GetTempObj(EnumTempObj.WildRoleObj)
	if not right_wildrole or not right_wildrole.role:
		return
	left_wildrole = role.GetTempObj(EnumTempObj.WildRoleObj)
	if not left_wildrole or not left_wildrole.role:
		return
	
	#pvp战斗
	WildBossPvP(left_wildrole, right_wildrole, AfterPvpFight)
	role.SetCD(EnumCD.WildBossFightCD, 15)
	return True

def ReviveWildBoss(role, argv, regparam):
	#传送到野外寻宝场景
	if not Environment.IsCross:
		print "GE_EXC ReviveWildBoss error not in cross"
		return
	
	global WildBoss_CanIn
	if not WildBoss_CanIn:
		#如果活动已经关闭了, 回到本地服-这里用活动是否开启判断
		role.GotoLocalServer(None, None)
		return
	
	ZoneName = regparam
	roleId = role.GetRoleID()
	global WildRole_Dict
	wildrole = WildRole_Dict.get(roleId)
	if wildrole:
		wildrole.join(role)
		return
		
	#第一次进来,根据等级划分战区
	regionIndex = GetRegionIndexByLevel(role.GetLevel()) + 1
	WildRegion_Dict[regionIndex].Init_WBRole(role, ZoneName)

def AfterBackLocalServer(role, regparam):
	#之前结束活动回本服调用的函数, 不要删除
	#活动结束回到本地服的处理
	return
	big_box_rank_dict, (box_cnt, score) = regparam
	#结算数据
	role.SendObj(WildBossFinallyData, big_box_rank_dict)
	#自己的数据 -- 宝箱数量
	role.SendObj(WildBossFinallyCnt, (box_cnt, score))

###############################################################################################3
def GetRegionIndexByLevel(roleLevel):
	tmp_index = 0
	for index, minLevel in enumerate(EnumGameConfig.WildBossRegionList):
		if minLevel > roleLevel:
			return tmp_index
		tmp_index = index
	else:
		return tmp_index
	
def GetCloseValue(value, value_list):
	#返回第一个大于value的上一个值的下表索引
	tmp_level = 1
	for v in value_list:
		if v > value:
			return tmp_level
		tmp_level = v
	else:
		return tmp_level

def Cal_kill_addscore(kill_cnt):
	#计算连杀积分
	if kill_cnt in (10, 20, 30, 50, 100, 200):
		return kill_cnt
	return 0
		
def Cal_bekill_addscore(kill_cnt):
	#计算终结连杀积分
	if kill_cnt < 10:
		return 0
	elif 10 <= kill_cnt < 20:
		return 10
	elif 20 <= kill_cnt < 30:
		return 20
	elif 30 <= kill_cnt < 50:
		return 30
	elif 50 <= kill_cnt < 100:
		return 50
	elif 100 <= kill_cnt < 200:
		return 100
	elif 200 <= kill_cnt:
		return 200

def Count_score(win_wildrole, lose_wildrole):
	#计算积分
	#基础分10分
	base_score = 10
	#挑战获得积分
	fight_score = 0
	
	if lose_wildrole.score <= 500:
		fight_score = int(lose_wildrole.score * 0.1)
	elif lose_wildrole.score <= 1000:
		fight_score = int(lose_wildrole.score * 0.3)
	else:
		fight_score = int(lose_wildrole.score * 0.5)
	
	#连杀额外积分+终结连杀额外积分
	add_score = Cal_kill_addscore(win_wildrole.kill_cnt) + Cal_bekill_addscore(lose_wildrole.kill_cnt)
	
	#胜利者获得总积分
	total_score = base_score + fight_score + add_score
	win_wildrole.score += total_score
	lose_wildrole.score = max((lose_wildrole.score - fight_score), 0)
	
	return fight_score, total_score
	
###############################################################################################3
#时间触发
###############################################################################################3
def FiveMinuteReady():
	if Environment.IsPLXP or Environment.IsRUGN:
		#俄罗斯GameNet、波兰101xp屏蔽跨服
		return
	
	#五分钟准备
	if not Environment.IsCross:
		#不是跨服场景的话, 开服天数小于10天的不开
		if not WorldData.WD.returnDB:
			return
		if WorldData.GetWorldKaiFuDay() < 10:
			return
	
	if Environment.IsCross:
		#跨服14, 15, 16, 17不开
		if cDateTime.Hour() in (14, 15, 16, 17):
			return
		if cDateTime.Hour() == 18 and cDateTime.WeekDay() in (2, 4, 6, 0) and not Environment.EnvIsTK():
			#二、四、六、七开跨服战场
			return
	else:
		#本地15, 16, 17, 18不开
		if cDateTime.Hour() in (15, 16, 17, 18):
			return
		if cDateTime.Hour() == 19 and cDateTime.WeekDay() in (2, 4, 6, 0) and not Environment.EnvIsTK():
			#二、四、六、七开跨服战场
			return
	
	#五分钟后开启野外寻宝
	cComplexServer.RegTick(300, BeginWildBoss, None)
	
	if not Environment.IsCross:
		cRoleMgr.Msg(1, 0, GlobalPrompt.WildBoss_Ready)
	
def BeginWildBoss(argv, param):
	#开始野外寻宝活动
	global WildBoss_CanIn
	if WildBoss_CanIn:
		print 'GE_EXC, WildBoss_CanIn is already True'
	WildBoss_CanIn = True
	
	#25分钟活动
	if Environment.IsCross:
		cComplexServer.RegTick(1560, EndWildBoss, None)
	else:
		cComplexServer.RegTick(1500, EndWildBoss, None)
	
	if not Environment.IsCross:
		cRoleMgr.Msg(1, 0, GlobalPrompt.WildBoss_Begin)
		return
	
	#创建BossNPC
	sceneNpcDict = {1:{}, 2:{}, 3:{}, 4:{}, 5:{}, 6:{}}
	SSP = cSceneMgr.SearchPublicScene
	for regionIndex, sceneIdList in WildBossScene.WildBoss_SceneConfig_Dict.iteritems():
		npcCfg = EnumGameConfig.get_wildboss_npc_data(regionIndex)
		for sceneID in sceneIdList:
			scene = SSP(sceneID)
			if not scene:
				print "GE_EXC, BeginWildBoss can not find sceneID:%s" % sceneID
				continue
			npc = scene.CreateNPC(*npcCfg)
			sceneNpcDict[regionIndex][scene] = npc.GetNPCID()
	
	#创建战区
	global WildRegion_Dict
	for region_index in range(1, EnumGameConfig.WildBossRegionCnt + 1):
		scene_npc_dict =  sceneNpcDict.get(region_index)
		WildRegion_Dict[region_index] = WBRegion(scene_npc_dict, region_index)
	
	if not Environment.IsCross:
		cRoleMgr.Msg(1, 0, GlobalPrompt.WildBoss_Begin)
	
def EndWildBoss(argv, param):
	#结束野外寻宝
	global WildBoss_CanIn
	if not WildBoss_CanIn:
		print 'GE_EXC, WildBoss_CanIn is already False'
	WildBoss_CanIn = False
	if not Environment.IsCross:
		return
	
	#结束，清理，发奖
	global WildRegion_Dict, WildRole_Dict
	for wr in WildRegion_Dict.values():
		wr.end_wildboss()

	WildRegion_Dict = {}
	WildRole_Dict = {}
	
	#两分钟后踢掉所有还在跨服野外夺宝场景内的玩家
	cComplexServer.RegTick(120, KickAllRole, None)
	
def KickAllRole(argv, param):
	#踢掉所有人
	SSS = cSceneMgr.SearchPublicScene
	for sceneList in WildBossScene.WildBoss_SceneConfig_Dict.itervalues():
		for sceneId in sceneList:
			scene = SSS(sceneId)
			if scene:
				for role in scene.GetAllRole():
					role.GotoLocalServer(None, None)
	#处理准备间玩家
	readySceneId = WildBossScene.WildBoss_ReadySceneID
	scene = SSS(readySceneId)
	if not scene:
		print 'GE_EXC, EndWildBoss can not find ReadyScene id (%s)' % readySceneId
		return
	for role in scene.GetAllRole():
		role.GotoLocalServer(None, None)
	
##########################################################################################
class WBRegion():
	def __init__(self, scene_npc_dict, region_index):
		self.region_index = region_index
		
		#战区场景npc字典{scene --> npcId}
		self.scene_npc_dict = scene_npc_dict
		#战区场景列表
		self.scene_list = scene_npc_dict.keys()
		#使用过的场景id列表
		self.used_scene_list = []
		
		#同步数据的tick与控制BOSS死亡的tick
		self.broadcast_rank_tick = cComplexServer.RegTick(60, self.BroadcastRank)
		self.kill_boss_tick = cComplexServer.RegTick(600, self.time_kill_boss, None)
		#提前一分钟结束分配场景
		self.end_new_scene_tick = cComplexServer.RegTick(540, self.end_new_scene)
		
		self.InitWBScene()
	
	def InitWBScene(self):
		#当前玩家应该进入的wbscene
		self.now_wbsceneObj = None
		self.wbSceneObj_dict = {}
		
		self.role_cnt = 0
		self.now_scene_index = 0
		self.max_scene_index = len(self.scene_list) - 1
		self.nowScene = self.scene_list[self.now_scene_index]
		self.now_wbsceneObj = WBScene(self.nowScene, self)
		self.wbSceneObj_dict[self.now_wbsceneObj.scene_id] = self.now_wbsceneObj
		
		self.used_scene_list.append(self.now_wbsceneObj.scene)
	
	def GetJoinWBSceneObj(self):
		self.role_cnt += 1
		if self.role_cnt % MaxSceneRole != 0:
			return self.now_wbsceneObj
		
		if self.now_scene_index == self.max_scene_index:
			self.now_scene_index = 0
		else:
			self.now_scene_index += 1
		
		if self.end_new_scene_tick:
			self.nowScene = self.scene_list[self.now_scene_index]
		else:
			self.nowScene = self.used_scene_list[self.now_scene_index]
		
		self.now_wbsceneObj = self.wbSceneObj_dict.get(self.nowScene.GetSceneID())
		if not self.now_wbsceneObj:
			self.now_wbsceneObj = WBScene(self.nowScene, self)
			self.wbSceneObj_dict[self.now_wbsceneObj.scene_id] = self.now_wbsceneObj
			
			self.used_scene_list.append(self.nowScene)
			
		return self.now_wbsceneObj
	
	def end_new_scene(self, argv, param):
		#结束分配新场景
		self.end_new_scene_tick = 0
		self.now_scene_index = 0
		self.max_scene_index = len(self.used_scene_list) - 1
	
	def Init_WBRole(self, role, zone_name):
		#第一次进来，创建临时对象
		WBRole(role, zone_name, self, self.GetJoinWBSceneObj())
		
	def BroadcastRank(self, argv, param):
		global WildBoss_CanIn
		if not WildBoss_CanIn:
			return
		
		self.broadcast_rank_tick = cComplexServer.RegTick(60, self.BroadcastRank)
		for wbSceneObj in self.wbSceneObj_dict.itervalues():
			wbSceneObj.BroadcastRank()
	
	def time_kill_boss(self, argv, param):
		self.kill_boss_tick = 0
		
		#这里删除所有创建的boss
		for scene in self.scene_npc_dict.iterkeys():
			for npc in scene.GetAllNPC():
				npc.Destroy()
		
		for wbSceneObj in self.wbSceneObj_dict.itervalues():
			wbSceneObj.time_kill_boss()
		
	def end_wildboss(self):
		#结束野外寻宝活动
		if self.broadcast_rank_tick:
			#取消同步排行榜tick
			cComplexServer.UnregTick(self.broadcast_rank_tick)
			self.broadcast_rank_tick = 0
		
		if self.kill_boss_tick:
			#取消时间到杀死bosstick
			cComplexServer.UnregTick(self.kill_boss_tick)
			self.kill_boss_tick = 0
			
			#删除npc 
			for scene, npc_id in self.scene_npc_dict.iteritems():
				scene.DestroyNPC(npc_id)
			
		for wbSceneObj in self.wbSceneObj_dict.itervalues():
			wbSceneObj.end_wildboss()
		self.wbSceneObj_dict = {}

#=====================================================================================
class WBScene():
	def __init__(self, scene, region_obj):
		self.scene = scene
		self.scene_id = scene.GetSceneID()
		self.region_obj = region_obj
		self.region_index = region_obj.region_index
		
		self.npc_id = region_obj.scene_npc_dict.get(scene)
		
		self.wildRole_Dict = {}
		
		#小伤害排行榜字典(10个数据, 同步客户端用){role_id --> [role_name, damage]}
		self.small_damage_rank_dict = {}
		#10个伤害榜的最小值[roleid, damage]
		self.min_small_damage = None
		
		#大伤害排行榜字典(100个数据, 用于boss死亡后发奖){role_id --> damage}
		self.big_damage_rank_dict = {}
		#100个伤害榜的最小值[roleid, damage]
		self.min_big_damage = None
		
		#小宝箱排行榜(10个数据, 用于同步客户端)
		#{role_id --> [role_name, box_cnt, box_dict, zdl, score]}
		self.small_box_rank_dict = {}
		#积分排行榜(10个数据, 用于同步客户端)
		self.small_score_rank_dict = {}
		
		#大宝箱排行榜(50个数据, 结算数据)
		#{role_id --> [zoom_name, role_name, box_cnt, box_dict, zdl, score]}
		self.big_box_rank_dict = {}
		#大积分排行榜(50个数据, 结算数据)
		#{role_id --> [zoom_name, role_name, box_cnt, box_dict, zdl, score]}
		self.big_score_rank_dict = {}
		
		#boss数据，boss血量字典, 直接初始化(每个战区的boss一个血量字典)
		self.is_boss_dead = False
		self.max_hp = EnumGameConfig.get_wildboss_maxhp(self.region_index)
		self.boss_hp_dict = {'total_hp' : self.max_hp, -4 : self.max_hp}
		
		#宝箱掉落优先列表
		self.priority_coding_list = EnumGameConfig.get_wildboss_boxcoding(self.region_index)
		#预处理配置
		self.damageCfg_Dict = WildBossConfig.WildBossDamage_Dict.get(self.region_index)
		
		if not self.region_obj.kill_boss_tick:
			#boss已经到时间被杀死了, 直接进入pvp阶段
			self.is_boss_dead = True
			self.boss_hp_dict['total_hp'] = 0
	
	def BroadMsg(self):
		self.scene.BroadMsg()
	
	def SyncAllData(self, wildrole):
		#[连杀数, buff玩家名字, [最大血量, 当前血量]]
		wildrole.role.SendObj(WildBossRoleData, [self.region_index, wildrole.kill_cnt, wildrole.buff_role_name, wildrole.score, wildrole.hp])
		
		self.SyncBossHp(wildrole)
		
		if not self.is_boss_dead:
			self.sync_damage_data(wildrole)
		else:
			self.sync_box_data(wildrole)
	
	def SyncBossHp(self, wildrole):
		wildrole.role.SendObj(WildBossHp, self.boss_hp_dict.get('total_hp', self.max_hp))
		
	def sync_damage_data(self, wildrole):
		#同步小伤害榜与个人伤害
		wildrole.role.SendObj(WildBossDamageRank, self.small_damage_rank_dict)
		wildrole.role.SendObj(WildBossDamage, wildrole.damage)
	
	def sync_box_data(self, wildrole):
		#小宝箱榜与个人宝箱数据
		wildrole.role.SendObj(WildBossBoxRank, (self.small_box_rank_dict, self.small_score_rank_dict))
		wildrole.role.SendObj(WildBossBox, wildrole.box_dict)
		
	def BroadcastRank(self):
		#广播排行榜
		if not self.is_boss_dead:
			#boss没有死，伤害榜数据
			cNetMessage.PackPyMsg(WildBossDamageRank, self.small_damage_rank_dict)
			self.scene.BroadMsg()
		else:
			#boss死了, 构建用于同步的宝箱榜并且广播
			self.build_box_rank_sync_data()
			cNetMessage.PackPyMsg(WildBossBoxRank, (self.small_box_rank_dict, self.small_score_rank_dict))
			self.scene.BroadMsg()
	
	def try_in_small_damage_rank(self, role_id, role_name, wildrole):
		damage = wildrole.damage
		if not self.min_small_damage:
			#构建小排行榜最小值
			self.min_small_damage = [role_id, damage]
		
		if role_id in self.small_damage_rank_dict:
			self.small_damage_rank_dict[role_id][1] = damage
			if role_id == self.min_small_damage[0]:
				#是最小值的话更新最小值, 更新后这个最小值不一定是真的最小值了, 所以最后还要重新构建一个最小值
				self.min_small_damage[1] = damage
			else:
				#不是最小值的, 这里就可以retrun了
				return
		elif len(self.small_damage_rank_dict) < 10:
			self.small_damage_rank_dict[role_id] = [role_name, damage]
			if damage < self.min_small_damage[1]:
				#伤害值比最小值小, 更新最小值, 这里后面不用构建最小值了
				self.min_small_damage = [role_id, damage]
				return
			else:
				#伤害值比最小值大, 直接可以retrun
				return
		elif damage > self.min_small_damage[1]:
			del self.small_damage_rank_dict[self.min_small_damage[0]]
			self.small_damage_rank_dict[role_id] = [role_name, damage]
			#构建一个最小值(这个最小值不一定是真的最小值, 所以而后还要再次构建一次最小值)
			self.min_small_damage = [role_id, damage]
		elif damage <= self.min_small_damage[1]:
			return
		#构建最小值
		for role_id, value in self.small_damage_rank_dict.iteritems():
			if value[1] > damage : continue
			damage = value[1]
			self.min_small_damage = [role_id, damage]
	
	def try_in_big_damage_rank(self, wildrole):
		damage = wildrole.damage
		role_id = wildrole.role_id
		role_name = wildrole.role_name
		
		if not self.min_big_damage:
			self.min_big_damage = [role_id, damage]
		
		if role_id in self.big_damage_rank_dict:
			self.big_damage_rank_dict[role_id] = damage
			#尝试进入小排行榜
			self.try_in_small_damage_rank(role_id, role_name, wildrole)
			if role_id == self.min_big_damage[0]:
				#是最小值的话更新最小值, 更新后这个最小值不一定是真的最小值了, 所以最后还要重新构建一个最小值
				self.min_big_damage[1] = damage
			else:
				#不是最小值的, 不用再构建最小值, 这里就可以retrun了
				return
		elif len(self.big_damage_rank_dict) < 100:
			self.big_damage_rank_dict[role_id] = damage
			self.try_in_small_damage_rank(role_id, role_name, wildrole)
			if damage < self.min_big_damage[1]:
				#伤害值比最小值小, 更新最小值, 这里后面不用构建最小值了
				self.min_big_damage = [role_id, damage]
				return
			else:
				#伤害值比最小值大, 直接可以retrun
				return
		elif damage > self.min_big_damage[1]:
			del self.big_damage_rank_dict[self.min_big_damage[0]]
			self.big_damage_rank_dict[role_id] = damage
			#构建一个最小值(这个最小值不一定是真的最小值, 所以而后还要再次构建一次最小值)
			self.min_big_damage = [role_id, damage]
			self.try_in_small_damage_rank(role_id, role_name, wildrole)
		elif damage <= self.min_big_damage[1]:
			return
		#构建最小值
		for role_id, value in self.big_damage_rank_dict.iteritems():
			if value > damage : continue
			damage = value
			self.min_big_damage = [role_id, damage]
	
	def build_bos_data_and_sync(self):
		#根据大伤害榜数据构造宝箱数据并且同步
		if not self.is_boss_dead:
			return
		
		#对大排行榜进行一次排序	伤害值 --> 角色ID
		rank_data = self.big_damage_rank_dict.items()
		rank_data.sort(key = lambda x:(x[1], x[0]), reverse = True)
		
		#前一百名
		SBRBD = self.build_box_data_by_rank
		for rank, data in enumerate(rank_data):
			SBRBD(data[0], rank + 1)
		
		#一百名后
		SBD = self.big_damage_rank_dict
		for role_id, wildRole in self.wildRole_Dict.iteritems():
			if role_id in SBD : continue #前一百名
			if not wildRole.damage:
				#没有伤害
				if not wildRole.role or wildRole.role.IsKick():
					continue
				wildRole.role.SetAppStatus(100)
				continue
			#100名之后的奖励都是一样的(第100名的奖励)
			SBRBD(role_id, 100, wildRole)
		
		#构建用于同步的宝箱榜
		self.build_box_rank_sync_data()
		
		cNetMessage.PackPyMsg(WildBossBoxRank, (self.small_box_rank_dict, self.small_score_rank_dict))
		self.scene.BroadMsg()
	
	def build_box_data_by_rank(self, role_id, rank, wildrole = None):
		#根据排名和战区确定配置
		cfg = self.damageCfg_Dict.get(rank)
		if not cfg:
			print 'GE_EXC, WildBoss build_box can not find rank (%s) region_index (%s)' % (rank, self.region_index)
			return
		
		if wildrole is None:
			wildrole = self.wildRole_Dict.get(role_id)
		if not wildrole:
			#不正常，打印信息
			print "GE_EXC, wild boss build_data error not wildRole (%s, %s)" % (role_id, rank)
			return
		if not wildrole.role or wildrole.role.IsKick():
			self.create_drop_box(copy.deepcopy(cfg.boxDict))
			return
		
		#构建抢夺数据
		box_cnt = sum(cfg.boxDict.values())
		wildrole.box_dict = copy.deepcopy(cfg.boxDict)
		wildrole.box_cnt = box_cnt
		wildrole.role.SetAppStatus(WildBossConfig.WildBossRoleStatus_Dict.get((1, wildrole.kill_cnt), 0))
		
		#同步个人宝箱数据
		wildrole.role.SendObj(WildBossBox, wildrole.box_dict)
		self.updata_box_rank(wildrole)
	
	def build_box_rank_sync_data(self):
		#构建用于同步的宝箱榜
		rankList = self.big_box_rank_dict.values()
		rankList.sort(key = lambda it:it[1], reverse = True)
		
		rank_10 = rankList[:10]
		
		self.small_box_rank_dict = SR = {}
		#big_box_rank_dict role_id --> [role_name, box_cnt, box_dict, zdl, score, zoom_name, roleid]
		for rankdata in rank_10:
			SR[rankdata[6]] = rankdata
		
		srankList = self.big_score_rank_dict.values()
		srankList.sort(key = lambda it:it[4], reverse = True)
		
		srank_10 = srankList[:10]
		
		self.small_score_rank_dict = SS = {}
		#big_score_rank_dict role_id --> [role_name, box_cnt, box_dict, zdl, score, zoom_name, roleid]
		for rankdata in srank_10:
			SS[rankdata[6]] = rankdata
	
	def get_box_rank_sync_data_50(self):
		#构建前50名数据
		SBD = {}
		SSD = {}
		#big_box_rank_dict role_id --> [role_name, box_cnt, box_dict, zdl, score, zoom_name, roleid]
		
		#宝箱榜
		rankList = self.big_box_rank_dict.values()
		rankList.sort(key = lambda it:it[1], reverse = True)
		
		rank_50 = rankList[:50]
		
		for d in rank_50:
			#{role_id--> [role_name, zoom_name, box_cnt, box_dict, zdl, score]}
			SBD[d[6]] = [d[0], d[5], d[1], d[2], d[3], d[4]]
		
		#积分榜
		srankList = self.big_score_rank_dict.values()
		srankList.sort(key = lambda it:it[4], reverse = True)
		
		srank_50 = srankList[:50]
		
		for d in srank_50:
			#{role_id--> [role_name, zoom_name, box_cnt, box_dict, zdl, score]}
			SSD[d[6]] = [d[0], d[5], d[1], d[2], d[3], d[4]]
		
		return SBD, SSD
	
	def updata_box_rank(self, wildrole, isLeave = False):
		#更新宝箱排行榜里面的基础数据
		role_id = wildrole.role_id
		box_cnt = wildrole.box_cnt
		score = wildrole.score
		
		#至少有两个宝箱的才会上榜
		role_rank_data = self.big_box_rank_dict.get(role_id)
		if not role_rank_data:
			if box_cnt > 1:
				self.big_box_rank_dict[role_id] = [wildrole.role_name, box_cnt, wildrole.box_dict, wildrole.zdl, score, wildrole.zone_name, role_id]
		elif box_cnt <= 1:
			del self.big_box_rank_dict[role_id]
		else:
			self.big_box_rank_dict[role_id][1] = box_cnt
			self.big_box_rank_dict[role_id][4] = score
			
		#至少10分才会上榜
		role_score_rank_data = self.big_score_rank_dict.get(role_id)
		if not role_score_rank_data:
			if score >= 10:
				self.big_score_rank_dict[role_id] = [wildrole.role_name, box_cnt, wildrole.box_dict, wildrole.zdl, score, wildrole.zone_name, role_id]
				return
		elif isLeave:
			#离开的时候删除数据
			del self.big_score_rank_dict[role_id]
		elif score < 10:
			#小于10分不上榜
			del self.big_score_rank_dict[role_id]
		else:
			#更新数据
			self.big_score_rank_dict[role_id][1] = box_cnt
			self.big_score_rank_dict[role_id][4] = score
		
	def updata_box_rank_score(self, wildrole):
		#更新宝箱排行榜的积分
		role_id = wildrole.role_id
		score = wildrole.score
		box_cnt = wildrole.box_dict
		
		role_score_rank_data = self.big_score_rank_dict.get(role_id)
		if not role_score_rank_data:
			if score >= 10:
				self.big_score_rank_dict[role_id] = [wildrole.role_name, box_cnt, wildrole.box_dict, wildrole.zdl, score, wildrole.zone_name, role_id]
				return
		elif score < 10:
			del self.big_score_rank_dict[role_id]
		else:
			self.big_score_rank_dict[role_id][1] = box_cnt
			self.big_score_rank_dict[role_id][4] = score
		
	def snatch(self, fight, left_wildrole, right_wildrole):
		#抢夺宝箱
		snatch_box_dict = {}
		right_box_cnt = right_wildrole.box_cnt
		
		if right_box_cnt:
			#抢到的数据
			snatch_box_dict = self.snatchex(left_wildrole, right_wildrole)
		
		#计算积分
		fight_score, total_score = Count_score(left_wildrole, right_wildrole)
		
		#更新一下排行榜
		self.updata_box_rank(left_wildrole)
		self.updata_box_rank(right_wildrole)
		
		#战斗提示
		if total_score:
			fight.set_fight_statistics(left_wildrole.role_id, EnumFightStatistics.EnumWildBossScore, total_score)
		#提示
		r_tips = GlobalPrompt.WildBoss_BeSnatch % left_wildrole.role_name
		l_tips = GlobalPrompt.WildBoss_Snatch
		needTips = False
		if right_box_cnt:
			for coding, cnt in snatch_box_dict.iteritems():
				item_tips = GlobalPrompt.Item_Tips % (coding, cnt)
				r_tips += item_tips
				l_tips += item_tips
			needTips = True
		if fight_score > 0:
			needTips = True
			r_tips += GlobalPrompt.WildBoss_DecScore % fight_score
		if needTips:
			right_wildrole.role.Msg(2, 0, r_tips)
		l_tips += GlobalPrompt.WildBoss_AddScore % total_score
		left_wildrole.role.Msg(2, 0, l_tips)
		
	def snatchex(self, win_wildrole, lose_wildrole):
		win_box_dict = win_wildrole.box_dict
		lose_box_dict = lose_wildrole.box_dict
		
		#计算被挑战者被抢夺的箱子个数(数量向下取整)
		snatch_box_cnt = (lose_wildrole.box_cnt / 2) if lose_wildrole.box_cnt > 1 else 1
		
		#修改宝箱个数
		lose_wildrole.box_cnt -= snatch_box_cnt
		win_wildrole.box_cnt += snatch_box_cnt
		
		#按优先级抢夺宝箱
		snatch_box_dict = {}
		for coding in self.priority_coding_list:
			codingCnt = lose_box_dict.get(coding)
			if not codingCnt:
				continue
			if codingCnt >= snatch_box_cnt:
				#宝箱个数足够
				codingCnt -= snatch_box_cnt
				if codingCnt == 0:
					#数量刚刚好
					del lose_box_dict[coding]
				else:
					lose_box_dict[coding] = codingCnt
				snatch_box_dict[coding] = snatch_box_cnt
				break
			#宝箱个数不够
			snatch_box_cnt -= codingCnt
			snatch_box_dict[coding] = codingCnt
			del lose_box_dict[coding]
		else:
			print 'GE_EXC, WildBoss snatch can not find box coding to del'
			return {}
		
		#增加抢夺者宝箱
		for coding, cnt in snatch_box_dict.iteritems():
			win_box_dict[coding] = win_box_dict.get(coding, 0) + cnt
		return snatch_box_dict
	
	def snatch_fail(self, fight, win_wildrole, lose_wildrole):
		#挑战失败只掉积分
		fight_score, total_score = Count_score(win_wildrole, lose_wildrole)
		
		#更新一下排行榜的积分
		self.updata_box_rank(win_wildrole)
		self.updata_box_rank(lose_wildrole)
		
		if total_score:
			fight.set_fight_statistics(win_wildrole.role_id, EnumFightStatistics.EnumWildBossScore, total_score)
		if fight_score > 0:
			lose_wildrole.role.Msg(2, 0, GlobalPrompt.WildBoss_SnatchFail % fight_score)
		
		win_wildrole.role.Msg(2, 0, GlobalPrompt.WildBoss_BeSnatchWin % (lose_wildrole.role_name, total_score))
	
	def create_drop_box(self, box_dict):
		#创建掉落宝箱npc
		WCG = WildBossConfig.CodingToNpctype_Dict.get
		posX_1, posX_2, posY_1, posY_2, pos_1, pos_2 = GetBoxDropPos()
		SSC = self.scene.CreateNPC
		RR = random.randint
		for coding, cnt in box_dict.iteritems():
			npcType = WCG(coding)
			if not npcType:
				print 'GE_EXC, wild boss create_drop_box can not find coding (%s) npcType' % coding
				continue
			for _ in range(cnt):
				rd_X = RR(posX_1, posX_2)
				rd_Y = RR(posY_1, posY_2)
				npc = SSC(npcType, rd_X, rd_Y, 1, 1)
				npc.SetPyDict(1, coding)
		self.scene.Msg(15, 0, GlobalPrompt.WildBoss_DropBox % (pos_1, pos_2, pos_1, pos_2))
	
	def kill_rumor(self, role_name, kill_cnt):
		#连杀传闻
		if kill_cnt == 10:
			self.scene.Msg(15, 0, GlobalPrompt.WildBoss_Kill_1 % role_name)
		elif kill_cnt == 20:
			self.scene.Msg(15, 0, GlobalPrompt.WildBoss_Kill_2 % role_name)
		elif kill_cnt == 30:
			self.scene.Msg(15, 0, GlobalPrompt.WildBoss_Kill_3 % role_name)
		elif (50 <= kill_cnt < 100) and ((kill_cnt - 50) % 5 == 0):
			self.scene.Msg(15, 0, GlobalPrompt.WildBoss_Kill_4 % (role_name, kill_cnt))
		elif kill_cnt == 100:
			self.scene.Msg(15, 0, GlobalPrompt.WildBoss_Kill_5 % role_name)
		elif kill_cnt == 200:
			self.scene.Msg(15, 0, GlobalPrompt.WildBoss_Kill_6 % role_name)
	
	def after_pve_fight(self, wildrole, damage):
		#挑战boss后处理
		if self.is_boss_dead:
			return
		
		wildrole.after_pve_fight(damage)
		
		if self.boss_hp_dict.get('total_hp') > 0:
			#boss没有死, 将玩家传送到安全坐标
			wildrole.role.JumpPos(*EnumGameConfig.WildBossSafePos)
			return
		
		self.boss_dead()

	def time_kill_boss(self):
		#到时间boss未被击杀, 删除boss]
		if self.is_boss_dead:
			return
		
		self.boss_dead()
	
	def boss_dead(self):
		if self.is_boss_dead:
			print 'GE_EXC, WildBoss destroy boss is already dead'
			return
		
		#设置boss死亡标志
		self.is_boss_dead = True
		self.boss_hp_dict['total_hp'] = 0
		
		#同步BOSS血量0
		cNetMessage.PackPyMsg(WildBossHp, 0)
		self.scene.BroadMsg()
		
		#构建抢夺数据
		self.build_bos_data_and_sync()
		
		self.scene.Msg(15, 0, GlobalPrompt.WildBoss_KillBoss)
	
	def end_wildboss(self):
		#清理宝箱，buffnpc
		for npc in self.scene.GetAllNPC():
			npc.Destroy()
		
		ENUMTOW = EnumTempObj.WildRoleObj
		ScoreList = WildBossConfig.WildBossScore_List
		MaxScore = WildBossConfig.WildBossScoreMax
		WWG = WildBossConfig.WildBossScore_Dict.get
		EWBSA = EnumAward.WildBossScoreAward
		EWBMA = EnumAward.WildBossMoneyAward
		AS = AwardMgr.SetAward
		
		with WildBossScore_Log:
			damage_money_coe = EnumGameConfig.GetWildBossMaxMoneyCoe(self.region_index)
			max_damage_money = EnumGameConfig.GetWildBossMaxMoney(self.region_index)
			
			#发金币奖励和积分奖励
			for roleId, wildrole in self.wildRole_Dict.iteritems():
				#计算金币奖励
				reward_money = 0
				if wildrole.damage:
					reward_money = min(wildrole.damage / damage_money_coe, max_damage_money)
					AS(roleId, EWBMA, money = reward_money)
				
				#记录	伤害, 金币奖励, 积分
				AutoLog.LogBase(roleId, AutoLog.eveWildBossScore, (wildrole.damage, reward_money, wildrole.score))
				
				#计算积分奖励，10分以上才有奖励
				if wildrole.score <= 10:
					continue
				if wildrole.score >= MaxScore:
					score = MaxScore
				else:
					score = GetCloseValue(wildrole.score, ScoreList)
				cfg = WWG((score, self.region_index))
				if not cfg:
					print 'GE_EXC, wild boss end_wildboss can not find score %s, regionIndex %s cfg' % (score, self.region_index)
					continue
				AS(roleId, EWBSA, itemList = cfg.items, clientDescParam = (wildrole.score, ))
			
			#发放宝箱奖励,同步回本服的排行榜数据
			EWBA = EnumAward.WildBossBoxAward
			SBD, SSD = self.get_box_rank_sync_data_50()
			for role in self.scene.GetAllRole():
				#设置头顶状态
				role.SetAppStatus(0)
				
				wildrole = role.GetTempObj(ENUMTOW)
				box_cnt, score = 0, 0
				if wildrole:
					box_cnt, score = wildrole.box_cnt, wildrole.score
					if box_cnt:
						AS(wildrole.role_id, EWBA, itemList = wildrole.box_dict.items())
					
					#弹出结算面板
					#结算数据
					role.SendObj(WildBossFinallyData, (SBD, SSD))
					#自己的数据 -- 宝箱数量
					role.SendObj(WildBossFinallyCnt, (box_cnt, score))
					
					#清理自身数据
					role.SetTempObj(ENUMTOW, None)
				
				#记录	宝箱个数
				AutoLog.LogBase(role.GetRoleID(), AutoLog.eveWildBossBox, box_cnt)
			
#====================================================================================
class WBRole():
	def __init__(self, role, zone_name, region_obj, wscene_obj):
		self.role = role								#role
		self.role_id = role.GetRoleID()					#role_id
		self.role_name = role.GetRoleName()				#role_name
		self.zdl = role.GetZDL()						#战斗力
		self.zone_name = zone_name						#服务器名
		
		self.region_obj = region_obj					#战区对象
		self.region_index = region_obj.region_index		#战区索引
		self.wscene_obj = wscene_obj
		self.scene_id = wscene_obj.scene_id				#场景ID
		self.scene = wscene_obj.scene					#场景对象
		
		self.damage = 0									#伤害值
		self.score = 0									#积分
		self.box_dict = {}								#宝箱字典
		self.box_cnt = 0								#宝箱个数
		
		self.kill_cnt = 0								#连杀次数
		self.be_kill_cnt = 0 							#被连杀次数
		
		
		self.updata_fight_data()						#更新战斗数据
		self.pick_up_fight_data = None					#拾取的战斗数据
		self.buff_role_name = None						#拾取的buff玩家名字
		
		#绑定数据
		global WildRole_Dict
		WildRole_Dict[self.role_id] = self
		self.join(role)
		self.wscene_obj.wildRole_Dict[self.role_id] = self
	
	def join(self, role):
		role.SetTempObj(EnumTempObj.WildRoleObj, self)
		self.role = role
		
		#传送
		role.Revive(self.scene_id, *EnumGameConfig.WildBossSafePos)
		if self.wscene_obj.is_boss_dead:
			self.set_rolestatus()
		
		if self.score >= 10:
			self.wscene_obj.big_score_rank_dict[self.role_id] = [self.role_name, self.box_cnt, self.box_dict, self.zdl, self.score, self.zone_name, self.role_id]
		
		#同步数据
		self.wscene_obj.SyncAllData(self)
		
	def leave(self):
		#玩家离开
		if not self.wscene_obj.is_boss_dead:
			self.role = None
			return
		
		if self.role:
			self.role.SetAppStatus(0)
		else:
			print 'GE_EXC, wildboss leave role is empty'
		
		global WildBoss_CanIn
		if not WildBoss_CanIn: return
		
		if not self.box_cnt:
			return
		
		#创建掉落宝箱
		self.wscene_obj.create_drop_box(self.box_dict)
		
		boxCnt = self.box_cnt
		
		#处理宝箱榜
		self.box_cnt = 0
		self.box_dict = {}
		self.wscene_obj.updata_box_rank(self, True)
		self.role = None
		
		with WildBossDropBox_Log:
			AutoLog.LogBase(self.role_id, AutoLog.eveWildBossDropBox, boxCnt)
		
	def get_role_total_hp(self, is_max = False):
		#返回最大血量或当前血量
		if is_max is False:
			return self.bind_hp.get("total_hp", 0)
		
		role_data, heros_data = self.fight_data
		total_hp = role_data[20]
		for hero_value in heros_data.itervalues():
			total_hp += hero_value[20]
		return total_hp
	
	def updata_fight_data(self):
		#更新战斗数据
		self.fight_data = Middle.GetRoleData(self.role, use_property_X = True)
		max_hp = self.get_role_total_hp(True)
		#[最大血量, 当前血量]
		self.hp = [max_hp, max_hp]
		self.bind_hp = {}
		
	def updata_hp(self):
		self.hp[1] = self.get_role_total_hp()
	
	def after_pve_fight(self, damage):
		#更新伤害和排行榜
		self.damage += damage
		self.wscene_obj.try_in_big_damage_rank(self)
		self.wscene_obj.sync_damage_data(self)
	
	def pick_up_box(self, coding):
		#拾取一个宝箱(拾取是没有cd的)
		self.box_dict[coding] = self.box_dict.get(coding, 0) + 1
		self.box_cnt += 1
		self.set_rolestatus()
		self.wscene_obj.updata_box_rank(self)
		self.wscene_obj.SyncAllData(self)
		self.role.Msg(2, 0, GlobalPrompt.WildBoss_PickUpBox)
	
	def create_buff_npc(self, win_name):
		#创建buffNPC
		color = 1
		if 20 <= self.kill_cnt < 50:
			color = 2
		elif 50 <= self.kill_cnt:
			color = 3
		
		pos_x, pos_y = self.role.GetPos()
		npc = self.scene.CreateNPC(EnumGameConfig.WildBossBuffNpcType, pos_x, pos_y, EnumGameConfig.WildBossBuffNpcDirect, 1, {EnumNPCData.EnNPC_Name:GlobalPrompt.WildBoss_BuffName % self.role_name, EnumNPCData.EnNPC_Color:color})
		npc.SetPyDict(1, self.fight_data)
		npc.SetPyDict(2, self.role_name)
		
		#传闻提示
		self.scene.Msg(15, 0, GlobalPrompt.WildBoss_Bekill % (win_name, self.role_name, self.kill_cnt, pos_x, pos_y, pos_x, pos_y, self.role_name, self.role_name))
	
	def pick_up_buff(self, fight_data, buff_role_name):
		#拾取的时候打包一份战斗数据
		self.pick_up_fight_data = self.replace_pro(fight_data)
		self.buff_role_name = buff_role_name
		
		#同步数据
		self.role.SendObj(WildBossRoleData, [self.region_index, self.kill_cnt, buff_role_name, self.score, self.hp])
		self.role.Msg(2, 0, GlobalPrompt.WildBoss_PickUpBuff % (buff_role_name, buff_role_name))
		self.scene.Msg(15, 0, GlobalPrompt.WildBoss_PickUpBuffMsg % (self.role_name, buff_role_name))
		
	def replace_pro(self, fight_data):
		other_role_data, other_hero_data_dict = copy.deepcopy(fight_data)
		own_role_data, own_hero_data_dict = copy.deepcopy(self.fight_data)
		
		#替换主角属性
		self.replace_role_pro(other_role_data, own_role_data)
		
		#替换英雄属性
		for own_hero_datas in own_hero_data_dict.itervalues():
			hero_career = own_hero_datas[Middle.Career]
			max_attack = None #[pos, attack]
			for pos, other_hero_datas in other_hero_data_dict.iteritems():
				if other_hero_datas[Middle.Career] != hero_career:
					continue
				if hero_career == 1:
					attack = other_hero_datas[Middle.AttackP]
				else:
					attack = other_hero_datas[Middle.AttackM]
				if not max_attack or attack > max_attack[1]:
					max_attack = [pos, attack]
			if max_attack:
				#查找到匹配的属性了
				self.replace_hero_pro(other_hero_data_dict[max_attack[0]], own_hero_datas)
		return own_role_data, own_hero_data_dict
	
	def replace_role_pro(self, other_data, own_data):
		#用别人的主角属性替换自己的主角属性
		own_data[Middle.HelpStationProperty] = other_data[Middle.HelpStationProperty]
		own_data[Middle.MaxHP] = other_data[Middle.MaxHP]
		own_data[Middle.Morale] = other_data[Middle.Morale]
		own_data[Middle.Speed] = other_data[Middle.Speed]
		own_data[Middle.AttackP] = other_data[Middle.AttackP]
		own_data[Middle.AttackM] = other_data[Middle.AttackM]
		own_data[Middle.DefenceP] = other_data[Middle.DefenceP]
		own_data[Middle.DefenceM] = other_data[Middle.DefenceM]
		own_data[Middle.Crit] = other_data[Middle.Crit]
		own_data[Middle.CritPress] = other_data[Middle.CritPress]
		own_data[Middle.AntiBroken] = other_data[Middle.AntiBroken]
		own_data[Middle.NotBroken] = other_data[Middle.NotBroken]
		own_data[Middle.Parry] = other_data[Middle.Parry]
		own_data[Middle.Puncture] = other_data[Middle.Puncture]
		own_data[Middle.DamageUpgrade] = other_data[Middle.DamageUpgrade]
		own_data[Middle.DamageReduce] = other_data[Middle.DamageReduce]
		own_data[Middle.DragonTrainProperty] = other_data[Middle.DragonTrainProperty]
	
	def replace_hero_pro(self, other_hero_data, own_hero_data):
		#替换英雄属性
		own_hero_data[Middle.MaxHP] = other_hero_data[Middle.MaxHP]
		own_hero_data[Middle.Morale] = other_hero_data[Middle.Morale]
		own_hero_data[Middle.Speed] = other_hero_data[Middle.Speed]
		own_hero_data[Middle.AttackP] = other_hero_data[Middle.AttackP]
		own_hero_data[Middle.AttackM] = other_hero_data[Middle.AttackM]
		own_hero_data[Middle.DefenceP] = other_hero_data[Middle.DefenceP]
		own_hero_data[Middle.DefenceM] = other_hero_data[Middle.DefenceM]
		own_hero_data[Middle.Crit] = other_hero_data[Middle.Crit]
		own_hero_data[Middle.CritPress] = other_hero_data[Middle.CritPress]
		own_hero_data[Middle.AntiBroken] = other_hero_data[Middle.AntiBroken]
		own_hero_data[Middle.NotBroken] = other_hero_data[Middle.NotBroken]
		own_hero_data[Middle.Parry] = other_hero_data[Middle.Parry]
		own_hero_data[Middle.Puncture] = other_hero_data[Middle.Puncture]
		own_hero_data[Middle.DamageUpgrade] = other_hero_data[Middle.DamageUpgrade]
		own_hero_data[Middle.DamageReduce] = other_hero_data[Middle.DamageReduce]
	
	def set_rolestatus(self):
		haveBox = 1 if self.box_cnt else 0
		if 10 <= self.kill_cnt < 20:
			killCnt = 1
		elif 20 <= self.kill_cnt < 30:
			killCnt = 2
		elif 30 <= self.kill_cnt < 50:
			killCnt = 3
		elif 50 <= self.kill_cnt < 100:
			killCnt = 4
		elif 100 <= self.kill_cnt < 200:
			killCnt = 5
		elif 200 <= self.kill_cnt:
			killCnt = 6
		else:
			killCnt = 0
		role_status = WildBossConfig.WildBossRoleStatus_Dict.get((haveBox, killCnt))
		if not role_status:
			print 'GE_EXC, wild boss set_rolestatus can not find role status by havebox %s, killcnt %s' % (haveBox, killCnt)
			return
		self.role.SetAppStatus(role_status)
	
	def afterfight(self, isWin):
		if isWin is True:
			self.kill_cnt += 1
			self.be_kill_cnt = 0
		else:
			self.kill_cnt = 0
			self.be_kill_cnt += 1
			self.role.JumpPos(*GetDeadRevivePos())
			
		if not self.pick_up_fight_data:
			if isWin is True:
				self.updata_hp()
			else:
				self.updata_fight_data()
		else:
			self.pick_up_fight_data = None
			self.buff_role_name = None
		#设置玩家状态
		self.set_rolestatus()
	
def ClickBoss(role, npc):
	if not Environment.IsCross:
		return
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		return
	wildrole = role.GetTempObj(EnumTempObj.WildRoleObj)
	if not wildrole or not wildrole.role:
		return
	
	WildBossPve(wildrole, EnumGameConfig.return_wildboss_mcid(wildrole.region_index), AfterPVEFight, (wildrole.wscene_obj.boss_hp_dict.get('total_hp'), copy.deepcopy(wildrole.wscene_obj.boss_hp_dict)))
	
def WildBossPve(wildrole, mcid, afterFight, param = None):
	fight = Fight.Fight(EnumGameConfig.WildBossBossFightType)
	_, hpDict = param
	
	left_camp, right_camp = fight.create_camp()
	left_camp.create_online_role_unit(wildrole.role, control_role_id = wildrole.role.GetRoleID(), use_px = True)
	
	right_camp.bind_hp(hpDict)
	right_camp.create_monster_camp_unit(mcid)
	
	fight.after_fight_fun = afterFight
	fight.after_fight_param = param
	fight.start()

def AfterPVEFight(fightObj):
	if fightObj.result is None:
		print "GE_EXC, WildBoss fight error"
		return
	roles = fightObj.left_camp.roles
	if not roles:
		return
	role = list(roles)[0]
	
	wildrole = role.GetTempObj(EnumTempObj.WildRoleObj)
	if not wildrole or not wildrole.role:
		return
	
	wscene_obj = wildrole.wscene_obj
	oldHp, hpDict = fightObj.after_fight_param
	nowHp = hpDict.get('total_hp')
	damage = abs(oldHp - nowHp)
	#直接修正boss血量字典
	wscene_obj.boss_hp_dict["total_hp"] -= damage
	if wscene_obj.boss_hp_dict["total_hp"] < 0:
		wscene_obj.boss_hp_dict["total_hp"] = 0
	wscene_obj.boss_hp_dict[-4] -= damage
	wscene_obj.after_pve_fight(wildrole, damage)

#############################################################################################3
def WildBossPvP(left_wildrole, right_wildrole, after_pvp_fight):
	fight = Fight.Fight(EnumGameConfig.WildBossSingleFightType)
	left_camp, right_camp = fight.create_camp()
	
	#左阵营
	if left_wildrole.pick_up_fight_data:
		left_camp.create_online_role_unit(left_wildrole.role, fightData = left_wildrole.pick_up_fight_data, use_px = True)
	else:
		#没有buff的时候需要绑定血量字典
		left_camp.bind_hp(left_wildrole.bind_hp)
		left_camp.create_online_role_unit(left_wildrole.role, fightData = left_wildrole.fight_data, use_px = True)
	
	if left_wildrole.be_kill_cnt >= 5:
		#被连杀超过5次, 加增伤500%、免伤90%
		for u in left_camp.pos_units.itervalues():
			u.damage_upgrade_rate += 5
			u.damage_reduce_rate += 0.9
	
	#右阵营
	if right_wildrole.pick_up_fight_data:
		right_camp.create_online_role_unit(right_wildrole.role, fightData = right_wildrole.pick_up_fight_data, use_px = True)
	else:
		#没有buff
		right_camp.bind_hp(right_wildrole.bind_hp)
		right_camp.create_online_role_unit(right_wildrole.role, fightData = right_wildrole.fight_data, use_px = True)
	
	if right_wildrole.be_kill_cnt >= 5:
		#被连杀超过5次, 加增伤500%、免伤90%
		for u in right_camp.pos_units.itervalues():
			u.damage_upgrade_rate += 5
			u.damage_reduce_rate += 0.9
	
	fight.after_fight_fun = after_pvp_fight
	fight.after_fight_param = left_wildrole, right_wildrole
	fight.start()

def AfterPvpFight(fightObj):
	left_wildrole, right_wildrole = fightObj.after_fight_param
	
	if not fightObj.result:
		print 'GE_EXC, wild boss fight not fight.result'
		if left_wildrole.pick_up_fight_data:
			left_wildrole.pick_up_fight_data = None
			left_wildrole.buff_role_name = None
		if right_wildrole.pick_up_fight_data:
			right_wildrole.pick_up_fight_data = None
			right_wildrole.buff_role_name = None
		return
	
	if fightObj.result == -1:
		#抢夺失败
		AfterPvpFightEx(fightObj, right_wildrole, left_wildrole, False)
	else:
		AfterPvpFightEx(fightObj, left_wildrole, right_wildrole)

def AfterPvpFightEx(fightObj, win_wildRole, lose_wildRole, isSnatch = True):
	if lose_wildRole.kill_cnt >= 10:
		#终结10连杀以上玩家处理，创建buff
		lose_wildRole.create_buff_npc(win_wildRole.role_name)
	
	
	#抢夺宝箱和积分
	if isSnatch is True:
		win_wildRole.wscene_obj.snatch(fightObj, win_wildRole, lose_wildRole)
		#被挑战，并且输了，保护CD
		lose_wildRole.role.GetCD(EnumCD.WildBossProtectCD)
	else:
		win_wildRole.wscene_obj.snatch_fail(fightObj, win_wildRole, lose_wildRole)
		
	win_wildRole.afterfight(True)
	
	win_wildRole.wscene_obj.SyncAllData(win_wildRole)
	
	lose_wildRole.afterfight(False)
	win_wildRole.wscene_obj.SyncAllData(lose_wildRole)
	
	if win_wildRole.kill_cnt >= 10:
		win_wildRole.wscene_obj.kill_rumor(win_wildRole.role_name, win_wildRole.kill_cnt)

########################################################################################
def ClickBox(role, npc):
	global WildBoss_CanIn
	if not WildBoss_CanIn: return
	
	if not Environment.IsCross: return
	
	if Status.IsInStatus(role, EnumInt1.ST_FightStatus):
		#战斗状态中不能拾取
		return
	
	wildrole = role.GetTempObj(EnumTempObj.WildRoleObj)
	if not wildrole or not wildrole.role:
		return
	
	#宝箱coding
	coding = npc.GetPyDict().get(1)
	if not coding:
		return
	
	#删除npc
	npc.Destroy()
	
	#拾取
	wildrole.pick_up_box(coding)
	
def ClickBuff(role, npc):
	global WildBoss_CanIn
	if not WildBoss_CanIn: return
	
	if not Environment.IsCross: return
	
	if Status.IsInStatus(role, EnumInt1.ST_FightStatus):
		#战斗状态中不能拾取
		return
	
	wildrole = role.GetTempObj(EnumTempObj.WildRoleObj)
	if not wildrole or not wildrole.role:
		return
	
	if wildrole.pick_up_fight_data:
		role.Msg(2, 0, GlobalPrompt.WildBoss_PickUpBuffFail)
		return
	
	#战斗数据
	npcDict = npc.GetPyDict()
	fight_data = npcDict.get(1)
	if not fight_data:
		return
	
	fight_data_role_name = npcDict.get(2)
	if not fight_data_role_name:
		return
	
	#删除npc
	npc.Destroy()
	
	wildrole.pick_up_buff(fight_data, fight_data_role_name)

def InitClickFun():
	#boss点击函数
	NPCServerFun.RegNPCServerOnClickFunEx(EnumGameConfig.WildBossNpc_1[0], ClickBoss)
	NPCServerFun.RegNPCServerOnClickFunEx(EnumGameConfig.WildBossNpc_2[0], ClickBoss)
	NPCServerFun.RegNPCServerOnClickFunEx(EnumGameConfig.WildBossNpc_3[0], ClickBoss)
	NPCServerFun.RegNPCServerOnClickFunEx(EnumGameConfig.WildBossNpc_4[0], ClickBoss)
	NPCServerFun.RegNPCServerOnClickFunEx(EnumGameConfig.WildBossNpc_5[0], ClickBoss)
	NPCServerFun.RegNPCServerOnClickFunEx(EnumGameConfig.WildBossNpc_6[0], ClickBoss)
	
	#宝箱npc类型
	for npcType in set(WildBossConfig.CodingToNpctype_Dict.values()):
		NPCServerFun.RegNPCServerOnClickFunEx(npcType, ClickBox)
	
	#buff点击函数
	NPCServerFun.RegNPCServerOnClickFunEx(EnumGameConfig.WildBossBuffNpcType, ClickBuff)
	
def OnRoleClientLost(role, param):
	#刷新回到本地服
	if not Environment.IsCross:
		return
	
	wildrole = role.GetTempObj(EnumTempObj.WildRoleObj)
	if wildrole:
		wildrole.leave()
	role.SetTempObj(EnumTempObj.WildRoleObj, None)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		#版本判断
		if not Environment.EnvIsNAXP() and not Environment.IsNAPLUS1 and not Environment.EnvIsESP():
			#西班牙不开
			if Environment.EnvIsFT() or Environment.EnvIsQQ() or Environment.IsDevelop or Environment.EnvIsNA() or Environment.EnvIsTK() or Environment.EnvIsRU() or Environment.EnvIsPL():
				if not Environment.IsCross:
					if not Environment.IsRUGN:
						Cron.CronDriveByMinute((2038, 1, 1), FiveMinuteReady, H="14 <= H <= 19", M="M == 0")
				elif cProcess.ProcessID == Define.GetDefaultCrossID():
					#跨服场景野外寻宝活动早开一分钟
					if not Environment.IsRUGN:
						Cron.CronDriveByMinute((2038, 1, 1), FiveMinuteReady, H="13 <= H <= 18", M="M == 59")
	
	if Environment.HasLogic and not Environment.IsCross: 
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WildBoss_Join", "请求进入野外寻宝"), RequstJoin)
	
	if Environment.HasLogic and Environment.IsCross and cProcess.ProcessID == Define.GetDefaultCrossID():
		InitClickFun()
		Event.RegEvent(Event.Eve_ClientLost, OnRoleClientLost)
		Event.RegEvent(Event.Eve_BeforeExit, OnRoleClientLost)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WildBoss_Leave", "请求离开野外寻宝"), RequestLeave)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WildBoss_Fight", "请求野外寻宝挑战"), RequestFight)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WildBoss_RequestFastFight", "请求野外寻宝追杀"), RequestFastFight)
	

