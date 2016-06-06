#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.HunluanSpace.HunluanSpace")
#===============================================================================
# 混乱时空
#===============================================================================
import Environment
import random
import cRoleMgr
import cSceneMgr
import cDateTime
import cComplexServer
from Common.Message import AutoMessage
from Common.Other import EnumAward, GlobalPrompt,\
	EnumFightStatistics, EnumGameConfig
from ComplexServer.Time import Cron
from ComplexServer.Log import AutoLog
from Game.Fight import Fight, FightConfig
from Game.Union import UnionMgr
from Game.SysData import WorldData
from Game.Role import Status, Event
from Game.Activity.Award import AwardMgr
from Game.NPC import NPCServerFun, EnumNPCData
from Game.Role.Data import EnumTempObj, EnumInt1, EnumCD
from Game.Activity.HunluanSpace import HunluanSpaceScene, HunluanSpaceConfig
from Game.Activity.RewardBuff import RewardBuff

if "_HasLoad" not in dir():
	IsHunluanSpaceOpen = False					#活动开启标志
	HSActiveID = 0 								#活动ID
	BeginTime = 0								#活动开始时的时间戳
	WorldLevel = 0								#活动开始时算出的世界等级
	SpaceUnionRankObj = None					#公会排行榜对象
	SpacePersonRankObj = None					#个人排行榜对象
	TpPos = None								#传送点
	HunLuanSpaceUnion_Dict = {}					#参与的公会{unionID-->spaceObj}
	CanInUnionIDList = []						#可以进入的公会ID列表
	NowSceneIDList = []							#当前活动的场景ID列表
	
	#{层数 --> 场景ID}
	LevelToSceneID = {}
	#TP位置
	TpPosDict = {}
	
	#公会伤害榜	{union_id --> [公会名字, 伤害]}
	HunluanSpaceUnionRank = AutoMessage.AllotMessage("HunluanSpaceUnionRank", "混乱时空公会积分榜")
	#公会积分
	HunluanSpaceUnionScore = AutoMessage.AllotMessage("HunluanSpaceUnionScore", "混乱时空公会积分")
	#伤害buff
	HunluanSpaceUnionBuff = AutoMessage.AllotMessage("HunluanSpaceUnionBuff", "混乱时空公会是否有伤害buff")
	#击杀倒计时
	HunluanSpaceCountdown = AutoMessage.AllotMessage("HunluanSpaceCountdown", "混乱时空公会击杀倒计时")
	#个人伤害榜	{role_id --> [角色名字, 公会名字, 伤害]}
	HunluanSpacePersonRank = AutoMessage.AllotMessage("HunluanSpacePersonRank", "混乱时空个人积分榜")
	#当前所处层, 个人伤害
	HunluanSpacePersonData = AutoMessage.AllotMessage("HunluanSpacePersonData", "混乱时空个人信息")
	#怪物刷新层, 怪物波数
	HunluanSpaceMonsterLevel = AutoMessage.AllotMessage("HunluanSpaceMonsterLevel", "混乱时空怪物信息")
	#公会伤害值
	HunluanSpaceUnionDamage = AutoMessage.AllotMessage("HunluanSpaceUnionDamage", "混乱时空公会伤害值")
	#寻路路径{层数 --> 正确的传送门号码}
	HunluanSpaceDirect = AutoMessage.AllotMessage("HunluanSpaceDirect", "混乱时空传送路径")
	
	
	HunluanSpaceFight_Log = AutoLog.AutoTransaction("HunluanSpaceFight_Log", "混乱时空进入战斗日志")
	
class SpaceUnionRank():
	'''混乱时空公会伤害榜'''
	def __init__(self):
		self.max_union_cnt = 10
		
		self.min_union = None			#[union_id, union_damage]
		self.union_rank_dict = {}		#{union_id --> [union_id, union_damage]}
		
	def try_in_union_rank(self, union_id, union_obj):
		#尝试进入公会伤害榜
		union_damage = union_obj.union_damage
		
		if not self.min_union:
			self.min_union = [union_id, union_damage]
		
		if union_id in self.union_rank_dict:
			self.union_rank_dict[union_id][1] = union_damage
			if union_id == self.min_union[0]:
				self.min_union[1] = union_damage
			else:
				return
		elif len(self.union_rank_dict) < self.max_union_cnt:
			self.union_rank_dict[union_id] = [union_obj.union_name, union_damage]
			if union_damage > self.min_union[1]:
				return
		elif union_damage > self.min_union[1]:
			del self.union_rank_dict[self.min_union[0]]
			self.union_rank_dict[union_id] = [union_obj.union_name, union_damage]
			self.min_union = [union_id, union_damage]
		elif union_damage <= self.min_union[1]:
			return
		for unionID, value in self.union_rank_dict.iteritems():
			if value[1] >= union_damage:
				continue
			union_damage = value[1]
			self.min_union = [unionID, union_damage]
	
class SpacePersonRank():
	'''混乱时空个人伤害榜'''
	def __init__(self):
		self.max_role_cnt = 10
		
		self.min_role_score = None		#[role_id, damage]
		self.role_rank_dict = {}		#{role_id --> [role_name, union_name, damage, role_level]}
		
	def try_in_role_rank(self, role_id, spaceRole):
		#尝试进入个人伤害榜
		damage = spaceRole.damage
		
		if not self.min_role_score:
			self.min_role_score = [role_id, damage]
		
		if role_id in self.role_rank_dict:
			self.role_rank_dict[role_id][2] = damage
			if role_id == self.min_role_score[0]:
				self.min_role_score[1] = damage
			else:
				return
		elif len(self.role_rank_dict) < self.max_role_cnt:
			self.role_rank_dict[role_id] = [spaceRole.role_name, spaceRole.union_name, damage, spaceRole.role_level]
			if damage > self.min_role_score[1]:
				return
		elif damage > self.min_role_score[1]:
			del self.role_rank_dict[self.min_role_score[0]]
			self.role_rank_dict[role_id] = [spaceRole.role_name, spaceRole.union_name, damage, spaceRole.role_level]
			self.min_role_score = [role_id, damage]
		elif damage <= self.min_role_score[1]:
			return
		for roleID, value in self.role_rank_dict.iteritems():
			if value[2] >= damage:
				continue
			damage = value[2]
			self.min_role_score = [roleID, damage]
		
class SpaceUnion():
	'''混乱时空对象--每个公会一个'''
	def __init__(self, union_id, union_obj, active_id, person_rank, union_rank):
		self.union_id = union_id					#公会ID
		self.union_name = union_obj.name			#公会名字
		self.union_obj = union_obj					#公会对象
		self.active_id = active_id					#当前玩法id
		
		self.person_rank = person_rank				#个人排行榜
		self.union_rank = union_rank				#公会排行榜
		
		self.buff = False							#伤害buff
		self.time_past = False						#群魔乱舞九层boss是否过期
		
		self.countdown = 0							#挑战倒计时(梦幻龙域)
		
		self.union_damage = 0						#公会伤害值
		self.union_score = 0						#公会积分
		
		self.monster_level = 1						#当前刷怪层数
		self.monster_wave = 0						#当前怪物波数
		self.monster_name = None					#当前怪物名字
		
		self.boss = None							#群魔乱舞boss
		
		self.broad_role_set = set()					#需要广播的角色
		
		self.hp_dict = {}							#{npc_id --> hp_dict}
		self.boss_hp_dict = {}						#群魔乱舞boss血量字典
		
		self.npc_dict = {}							#创建的npc字典{npc_id --> npc}
		
		self.kill_npc_dict = {}						#记录击杀npc的玩家名字
		
		self.directions = {}						#传送阵传送{level --> 三个传送点}
		
		self.join_role_dict = {}					#进入过的玩家的ID集合(用于发奖){role_id --> 角色等级}
		
		self.role_data = {}							#公会玩家数据 {role_id --> [伤害值, 当前层数]}
		
		self.correct_directions = {}				#正确的传送路径{层数-->传送门号}
		
		#初始化传送阵
		self.init_directions()
		#选择玩法
		self.choice_create()
		
		#注册一个15s同步的tick
		self.sync_tick = cComplexServer.RegTick(15, self.sync_rank_data)
		
	def add_correct_dir(self, role_name, level, pos):
		#增加一个正确的路径
		if level in self.correct_directions:
			return
		self.correct_directions[level] = pos
		
		for role in self.broad_role_set:
			role.SendObj(HunluanSpaceDirect, self.correct_directions)
		
		UnionMgr.UnionMsg(self.union_obj, GlobalPrompt.HunluanSpace_First % (role_name, level + 1))
		
	def sync_rank_data(self, argv, param):
		#每15s同步一次公会伤害榜和个人伤害榜
		#注:不同公会的同步是错开的
		global IsHunluanSpaceOpen
		if not IsHunluanSpaceOpen:
			return
		
		for role in self.broad_role_set:
			role.SendObj(HunluanSpaceUnionRank, self.union_rank.union_rank_dict)
			role.SendObj(HunluanSpacePersonRank, self.person_rank.role_rank_dict)
			role.SendObj(HunluanSpaceUnionDamage, self.union_damage)
		
		self.sync_tick = cComplexServer.RegTick(15, self.sync_rank_data)
		
	def unreg_sync_rank_data(self):
		if not self.sync_tick:
			return
		cComplexServer.UnregTick(self.sync_tick)
		
	def init_directions(self):
		#初始化tp路线
		for i in xrange(1, 10):
			if i == 1:
				#第一层两个传送到本层, 一个传送到第二层
				tmp_list = [1, 1, 2]
			elif i == 2:
				#第二层只有一个传送到三层, 其他都回到一层
				tmp_list = [i+1, i-1, i-1]
			elif i == 9:
				#第九层都传送到第一层
				tmp_list = [1, 1, 1]
			else:
				#其他层一个传送到上一层, 一个传送到下一层, 一个传送到下两层
				tmp_list = [i+1, i-1, i-2]
			#打乱一下顺序
			random.shuffle(tmp_list)
			#每一层tp点对应的传送层数
			self.directions[i] = tmp_list
		
	def choice_create(self):
		#根据星期选择玩法
		if self.active_id == 2:
			#一三五七梦幻龙域
			#初始化倒计时
			self.init_countdown()
		else:
			#二四六群魔乱舞
			self.begin_devil()
		
	def init_countdown(self):
		#第二个活动需要根据时间来计算刷第几波, 第一个活动只需要在前五分钟计算
		global BeginTime
		pastSec = cDateTime.Seconds() - BeginTime
		#根据时间计算层数 -- (过去的分钟数)/5 + 1 = 应该是第几波
		self.monster_level = (pastSec / 60) / 5 + 1
		#初始化第一波
		self.monster_wave = 1
		#初始化倒计时
		nextSec = 300 - pastSec % 300
		self.countdown = cDateTime.Seconds() + nextSec
		#注册刷新下一波的tick
		self.next_demon_tick = cComplexServer.RegTick(nextSec, self.clear_demon)
		#创建妖怪
		self.create_demon()
		
	def begin_devil(self):
		#获取第九层场景ID
		global LevelToSceneID
		lastSceneID = LevelToSceneID.get(9)
		if not lastSceneID:
			print 'GE_EXC, HunluanSpace begin_devil can not find 9 level scene id'
			return
		#第九层场景对象
		scene = cSceneMgr.SearchPublicScene(lastSceneID)
		if not scene:
			print 'GE_EXC, HunluanSpace create devil can not find scene id 324'
			return
		#根据事先算好的世界等级获取boss配置
		global WorldLevel
		cfg = HunluanSpaceConfig.HunluanDevilBoss_Dict.get(WorldLevel)
		if not cfg:
			print 'GE_EXC, HunluanSpace begin_devil can not find worldLevel %s in HunluanDevilBoss_Dict' % WorldLevel
			return
		#创建boss
		self.boss = scene.CreateNPC(cfg.boss[0], cfg.boss[1], cfg.boss[2], cfg.boss[3], 1, {EnumNPCData.EnNPC_UnionID : self.union_id})
		#公会ID
		self.boss.SetPyDict(1, self.union_id)
		#战斗类型
		self.boss.SetPyDict(2, cfg.fightType)
		#阵营ID
		self.boss.SetPyDict(3, cfg.mcid)
		
		global BeginTime
		pastSec = cDateTime.Seconds() - BeginTime
		if (pastSec / 60 + 1) < 5:
			#如果在活动开始的5分钟内, 注册创建恶魔的tick
			cComplexServer.RegTick(300 - pastSec % 300, self.create_devil)
		else:
			self.create_devil(None, None)
		
	def create_devil(self, argv, regparam):
		global IsHunluanSpaceOpen
		if not IsHunluanSpaceOpen: return
		
		#开始创建恶魔的时候将第九层boss的过期标志设置了
		if not self.time_past:
			self.time_past = True
		
		#随机层数	[)+[)中间筛掉当前层, 第九层不刷
		self.monster_level = random.choice(range(1, self.monster_level) + range(self.monster_level + 1, 9))
		
		global WorldLevel
		cfg = HunluanSpaceConfig.HunluanDevil_Dict.get(WorldLevel)
		if not cfg:
			print 'GE_EXC, HunluanSpace can not find worldLevel %s in HunluanDevil_Dict' % WorldLevel
			return
		global NowSceneIDList
		sceneID = NowSceneIDList[self.monster_level-1]
		scene = cSceneMgr.SearchPublicScene(sceneID)
		if not scene:
			print 'GE_EXC, HunluanSpace begin_create_devil can not find scene id %s' % sceneID
			return
		
		#随机npc -- [名字, [(npcType, fightType, mcid, posx, posy, direct, 积分), ...]]
		npcCfg = cfg.randomNpc.RandomOne()
		self.monster_name = npcCfg[1]
		
		#创建恶魔 -- 恶魔没有挑战倒计时, 打完一波才刷新下一波
		for ng in npcCfg[2:][0]:
			npc = scene.CreateNPC(ng[0], ng[3], ng[4], ng[5], 1, {EnumNPCData.EnNPC_UnionID:self.union_id})
			#公会
			npc.SetPyDict(1, self.union_id)
			#积分
			npc.SetPyDict(2, ng[6])
			#战斗类型
			npc.SetPyDict(4, ng[1])
			#阵营ID
			npc.SetPyDict(5, ng[2])
			
			npcID = npc.GetNPCID()
			self.npc_dict[npcID] = npc
			self.hp_dict[npcID] = {}
			
		for role in self.broad_role_set:
			role.SendObj(HunluanSpaceMonsterLevel, (self.monster_level, self.monster_name))
		
		if npcCfg[0]:
			UnionMgr.UnionMsg(self.union_obj, GlobalPrompt.HunluanSpace_DevilBoss % self.monster_name)
		
	def ready_next_demon(self):
		global IsHunluanSpaceOpen
		if not IsHunluanSpaceOpen: return
		
		if self.monster_wave == 2:
			#已经是第二波了, 准备下一层怪物
			self.monster_level += 1
			self.monster_wave = 1
			self.countdown = 300 + cDateTime.Seconds()
			if self.next_demon_tick:
				cComplexServer.UnregTick(self.next_demon_tick)
			if self.monster_level > 9:
				#通关第九层, 不再注册清理tick
				self.next_demon_tick = 0
				UnionMgr.UnionMsg(self.union_obj, GlobalPrompt.HunluanSpace_DemonBoss_3)
				return
			self.next_demon_tick = cComplexServer.RegTick(300, self.clear_demon)
			#同步一下倒计时时间戳
			for role in self.broad_role_set:
				role.SendObj(HunluanSpaceCountdown, self.countdown)
		else:
			#第一波死掉了
			self.monster_wave += 1
		self.create_demon()
		
	def create_demon(self):
		global IsHunluanSpaceOpen
		if not IsHunluanSpaceOpen: return
		
		global NowSceneIDList
		sceneID = NowSceneIDList[self.monster_level - 1]
		scene = cSceneMgr.SearchPublicScene(sceneID)
		if not scene:
			print 'GE_EXC, HunluanSpace create demon can not find scene id %s' % sceneID
			return
		#获取配置
		global WorldLevel
		cfg = HunluanSpaceConfig.HunluanDemon_Dict.get((self.monster_level, self.monster_wave, WorldLevel))
		if not cfg:
			print 'GE_EXC, HunluanSpace can not find level %s, wave %s, worldLevel %s in HunluanDemon_Dict' % (self.monster_level, self.monster_wave, WorldLevel)
			return
		
		#创建妖怪
		for npcCfg in cfg.npc:
			#npcType, fightType, mcid, posx, posy, direct, 积分
			npc = scene.CreateNPC(npcCfg[0], npcCfg[3], npcCfg[4], npcCfg[5], 1, {EnumNPCData.EnNPC_UnionID:self.union_id})
			#公会
			npc.SetPyDict(1, self.union_id)
			#积分
			npc.SetPyDict(2, npcCfg[6])
			#战斗类型
			npc.SetPyDict(4, npcCfg[1])
			#阵营ID
			npc.SetPyDict(5, npcCfg[2])
			#{npcID --> npc}
			#用作挑战倒计时到后删除npc之用
			npcID = npc.GetNPCID()
			self.npc_dict[npcID] = npc
			self.hp_dict[npcID] = {}
			
		if self.monster_wave != 1:
			UnionMgr.UnionMsg(self.union_obj, GlobalPrompt.HunluanSpace_DemonBoss_2)
			return
		self.monster_name = cfg.waveName
		for role in self.broad_role_set:
			role.SendObj(HunluanSpaceMonsterLevel, (self.monster_level, self.monster_name))
			
		UnionMgr.UnionMsg(self.union_obj, GlobalPrompt.HunluanSpace_DemonBoss_1 % self.monster_level)
		
	def clear_demon(self, argv, regparam):
		global IsHunluanSpaceOpen
		if not IsHunluanSpaceOpen: return
		
		#清理掉没有杀死的妖怪, 创建下一波妖怪
		if self.npc_dict:
			for npc in self.npc_dict.itervalues():
				npc.Destroy()
			self.npc_dict = {}
		
		#刷怪层数+1
		self.monster_level += 1
		self.monster_wave = 1
		
		#倒计时
		self.countdown = 300 + cDateTime.Seconds()
		self.next_demon_tick = cComplexServer.RegTick(300, self.clear_demon)
		
		for role in self.broad_role_set:
			role.SendObj(HunluanSpaceCountdown, self.countdown)
		
		#创建妖怪
		self.create_demon()
		
	def unreg_next_demon_tick(self):
		if self.next_demon_tick:
			cComplexServer.UnregTick(self.next_demon_tick)
		
	def add_union_role(self, role):
		#加入一个公会成员 -- 用于广播buff, 刷怪的层数, 怪物的名字, 倒计时
		self.broad_role_set.add(role)
		
		#记录玩家参加过活动 -- 用于最后发奖
		roleID = role.GetRoleID()
		if roleID not in self.join_role_dict:
			self.join_role_dict[roleID] = role.GetLevel()
		spaceRole = role.GetTempObj(EnumTempObj.SpaceRole)
		if not spaceRole:
			#没有临时对象, 创建一个
			spaceRole = SpaceRole(roleID, role.GetRoleName(), role.GetLevel(), role, self, self.person_rank)
			role.SetTempObj(EnumTempObj.SpaceRole, spaceRole)
		elif not spaceRole.role:
			spaceRole.role = role
		
		#用缓存更新玩家数据
		if roleID in self.role_data:
			roleData = self.role_data[roleID]
			spaceRole.damage = roleData[0]
			spaceRole.level = roleData[1]
			spaceRole.scene_id = roleData[2]
		
	def del_union_role(self, role):
		if role in self.broad_role_set:
			self.broad_role_set.discard(role)
		
		#离开时更新一下缓存数据
		spaceRole = role.GetTempObj(EnumTempObj.SpaceRole)
		if not spaceRole:
			return
		self.role_data[role.GetRoleID()] = [spaceRole.damage, spaceRole.level, spaceRole.scene_id]
		
	def add_union_damage(self, damage):
		self.union_damage += damage
		self.union_rank.try_in_union_rank(self.union_id, self)
		
	def add_union_score(self, score):
		self.union_score += score
		#广播给所有在活动中的玩家公会积分改变
		for role in self.broad_role_set:
			role.SendObj(HunluanSpaceUnionScore, self.union_score)
		
	def add_buff(self):
		self.buff = True
		self.boss.Destroy()
		self.boss = None
		for role in self.broad_role_set:
			role.SendObj(HunluanSpaceUnionBuff, True)
		
class SpaceRole():
	'''混乱时空角色'''
	def __init__(self, role_id, role_name, role_level, role, union_obj, person_rank):
		self.role_id = role_id						#角色ID
		self.role_name = role_name					#角色名字
		self.role_level = role_level				#角色等级
		self.role = role							#角色role
		self.union_obj = union_obj					#混乱时空obj
		self.person_rank = person_rank				#个人伤害榜
		self.union_name = union_obj.union_name		#公会名字
		
		self.damage = 0								#伤害值
		self.level = 1								#当前位于哪一层(初始化第一层)
		self.scene_id = 0							#当前层的场景ID(没有初始化)
		
	def add_role_damage(self, damage):
		#增加伤害值
		self.damage += damage
		
		self.union_obj.add_union_damage(damage)
		
		self.union_obj.person_rank.try_in_role_rank(self.role_id, self)
		
		self.role.SendObj(HunluanSpacePersonData, (self.level, self.damage))
		
	def sync_data(self):
		#个人数据(当前层数和伤害值)
		self.role.SendObj(HunluanSpacePersonData, (self.level, self.damage))
		#公会积分
		self.role.SendObj(HunluanSpaceUnionScore, self.union_obj.union_score)
		#公会伤害榜
		self.role.SendObj(HunluanSpaceUnionRank, self.union_obj.union_rank.union_rank_dict)
		#个人伤害榜
		self.role.SendObj(HunluanSpacePersonRank, self.union_obj.person_rank.role_rank_dict)
		#怪物数据(刷新层数, 波数名字) -- 开始5分钟之内进去的不发这个, 客户端默认显示
		if (self.union_obj.active_id == 1 and self.union_obj.time_past) or self.union_obj.active_id == 2:
			self.role.SendObj(HunluanSpaceMonsterLevel, (self.union_obj.monster_level, self.union_obj.monster_name))
		#根据玩法确定的
		if self.union_obj.active_id == 1:
			#如果是群魔乱舞的话, 发送是否有buff
			self.role.SendObj(HunluanSpaceUnionBuff, self.union_obj.buff)
		else:
			#如果是梦幻龙域的话, 发送倒计时
			self.role.SendObj(HunluanSpaceCountdown, self.union_obj.countdown)
		#公会伤害值
		self.role.SendObj(HunluanSpaceUnionDamage, self.union_obj.union_damage)
		#路径
		self.role.SendObj(HunluanSpaceDirect, self.union_obj.correct_directions)
		
def RequestJoinSpace(role, msg):
	'''
	请求进入混乱时空
	@param role:
	@param msg:
	'''
	global IsHunluanSpaceOpen
	if not IsHunluanSpaceOpen: return
	global CanInUnionIDList
	if not CanInUnionIDList: return
	
	unionID= role.GetUnionID()
	if not unionID: return
	
	if unionID not in CanInUnionIDList:
		role.Msg(2, 0, GlobalPrompt.HunluanSpace_UnionLimit)
		return
	
	if role.GetLevel() < EnumGameConfig.HunluanSpace_LvLimit:
		return
	global NowSceneIDList
	if role.GetSceneID() in NowSceneIDList:
		return
	if not Status.CanInStatus(role, EnumInt1.ST_HunluanSpace):
		return
	
	global HunLuanSpaceUnion_Dict
	if unionID not in HunLuanSpaceUnion_Dict:
		global SpacePersonRankObj, SpaceUnionRankObj, HSActiveID
		if not HSActiveID:
			return
		#该公会还没有人进来过, 创建一个新的混乱时空公会对象
		HunLuanSpaceUnion_Dict[unionID] = spaceUnionObj = SpaceUnion(unionID, role.GetUnionObj(), HSActiveID, SpacePersonRankObj, SpaceUnionRankObj)
	else:
		spaceUnionObj = HunLuanSpaceUnion_Dict[unionID]
	spaceUnionObj.add_union_role(role)
	
	spaceRole = role.GetTempObj(EnumTempObj.SpaceRole)
	if not spaceRole or not spaceRole.role:
		return
	
	global TpPos
	if not spaceRole.scene_id:
		#初始化玩家第一次进入的场景ID
		spaceRole.scene_id = NowSceneIDList[0]
	role.Revive(spaceRole.scene_id, *TpPos)
	
	if not role.GetCD(EnumCD.HunluanSpaceCD):
		role.SetCD(EnumCD.HunluanSpaceCD, 15)
	
	#触发王者公测奖励狂翻倍任务进度
	Event.TriggerEvent(Event.Eve_WangZheCrazyRewardTask, role, (EnumGameConfig.WZCR_Task_HunLuanSpace, True))
	
	#触发激情活动奖励狂翻倍任务进度
	Event.TriggerEvent(Event.Eve_PassionMultiRewardTask, role, (EnumGameConfig.PassionMulti_Task_HunLuanSpace, True))
	#元旦金猪活动任务进度
	Event.TriggerEvent(Event.Eve_NewYearDayPigTask, role, (EnumGameConfig.NewYearDay_Task_HunluanSpace, True))
	
def RequestLeaveSpace(role, msg):
	'''
	请求离开混乱时空 -- 被踢公会, 有事件处理
	@param role:
	@param msg:
	'''
	global IsHunluanSpaceOpen
	if not IsHunluanSpaceOpen: return
	
	unionID= role.GetUnionID()
	if not unionID: return
	
	if role.GetLevel() < EnumGameConfig.HunluanSpace_LvLimit:
		return
	global NowSceneIDList
	if role.GetSceneID() not in NowSceneIDList:
		return
	if not Status.CanInStatus(role, EnumInt1.ST_TP):
		return
	
	spaceRole = role.GetTempObj(EnumTempObj.SpaceRole)
	if not spaceRole or not spaceRole.role:
		return
	
	role.BackPublicScene()
	
def ChoiceCanInUnion():
	'''
	筛选可以进入的公会ID
	'''
	unionData = UnionMgr.UNION_OBJ_DICT.items()
	unionData.sort(key = lambda x : (x[1].level, x[1].exp, x[0]), reverse = True)
	#取前100名公会的ID
	global CanInUnionIDList
	for data in unionData[:100]:
		CanInUnionIDList.append(data[0])
	
def HalfHourReady():
	'''
	半小时准备
	'''
	ChoiceCanInUnion()
	
	#....
	global HSActiveID, NowSceneIDList, LevelToSceneID, TpPosDict, TpPos
	if cDateTime.WeekDay() in (1, 3, 5, 0):
		##诸神之战取代原来的1,3,5,7的活动
		if not Environment.EnvIsNA():
			return
		#星期天是0...
		HSActiveID = 2
		NowSceneIDList = HunluanSpaceScene.HSDevilSceneList
		TpPosDict = {1:(16037, 2712, 1624, 1, 1), 2:(16038, 667, 553, 1, 1), 3:(16039, 2728, 561, 1, 1)}
		TpPos = (684, 1602)
	else:
		HSActiveID = 1
		NowSceneIDList = HunluanSpaceScene.HSDemonSceneList
		TpPosDict = {1:(16037, 2640,1730, 1, 1), 2:(16038, 794, 520, 1, 1), 3:(16039, 2585, 484, 1, 1)}
		TpPos = (758, 1688)
	
	for index, sceneID in enumerate(NowSceneIDList):
		LevelToSceneID[index + 1] = sceneID
	
	#场景不够 ?
	if len(NowSceneIDList) < 9:
		print 'GE_EXC, HunluanSpace scene less'
		return
	
	cComplexServer.RegTick(1200, TenMinuteReady)
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.HunluanSpace_HalfHourReady)
	
def TenMinuteReady(argv, regparam):
	'''
	10分钟准备
	@param argv:
	@param regparam:
	'''
	cComplexServer.RegTick(600, BeginHunluanSpace)
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.HunluanSpace_TenMinuteReady)
	
def BeginHunluanSpace(argv, regparam):
	#活动开始, 先创建各层tp, 第九层boss在一个公会有玩家进入的时候再创建
	global IsHunluanSpaceOpen
	if IsHunluanSpaceOpen:
		print 'GE_EXC, HunluanSpace IsHunluanSpaceOpen is already true'
	IsHunluanSpaceOpen = True
	
	#依赖世界数据, 如果没有载回来, 活动不开
	if not WorldData.WD.returnDB:
		return
	
	#活动开始的时候先把这时的世界等级计算出来
	global WorldLevel, SpacePersonRankObj, SpaceUnionRankObj, TpPosDict
	WorldLevel = GetCloseValue(WorldData.GetWorldLevel(), HunluanSpaceConfig.HunluanWorldLevel_List)
	
	global BeginTime
	BeginTime = cDateTime.Seconds()
	
	#创建个人积分榜对象
	SpacePersonRankObj = SpacePersonRank()
	#创建公会积分榜对象
	SpaceUnionRankObj = SpaceUnionRank()
	
	SSS = cSceneMgr.SearchPublicScene
	global NowSceneIDList
	for sceneId in NowSceneIDList:
		scene = SSS(sceneId)
		if not scene:
			print 'GE_EXC, ReadyHunluanSpace can not find scene id %s' % sceneId
			continue
		#创建tp
		for index, pos in TpPosDict.iteritems():
			npc = scene.CreateNPC(*pos)
			#npc位置 -- 这里不用记录层数, 玩家在哪一层可以确定
			npc.SetPyDict(1, index)
			
	cComplexServer.RegTick(1800, EndHunluanSpace)
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.HunluanSpace_Begin)
	
def EndHunluanSpace(argv, regparam):
	#结束混乱时空活动
	global IsHunluanSpaceOpen, HSActiveID
	if not IsHunluanSpaceOpen:
		print 'GE_EXC, IsHunluanSpaceOpen is already false'
	IsHunluanSpaceOpen = False
	HSActiveID = 0
	
	global SpaceUnionRankObj, SpacePersonRankObj, HunLuanSpaceUnion_Dict, WorldLevel, BeginTime
	
	AS = AwardMgr.SetAward
	
	#公会排名奖励
	union_rank_data = SpaceUnionRankObj.union_rank_dict.items()
	#伤害 --> ID
	union_rank_data.sort(key = lambda x : (x[1][1], x[0]), reverse = True)
	#公会前三有奖励
	union_rank_data = union_rank_data[:3]
	
	uTips = GlobalPrompt.HunluanSpace_URT
	uTipsFlag = False
	
	HHURG = HunluanSpaceConfig.HunluanUnionRank_Dict.get
	HHRL = HunluanSpaceConfig.HunluanRewardLevel_List
	RC = RewardBuff.CalNumber
	RH = RewardBuff.enHunluanSpace
	
	for index, union_data in enumerate(union_rank_data):
		if not union_data[1][1]:
			#没有伤害
			continue
		unionObj = HunLuanSpaceUnion_Dict.get(union_data[0])
		if not unionObj:
			#ID错了 ?
			continue
		for roleID, level in unionObj.join_role_dict.iteritems():
			#计算合适的等级
			cfg = HHURG((index + 1, GetCloseValue(level, HHRL)))
			if not cfg:
				print 'GE_EXC, HunluanSpace EndHunluanSpace can not find rank %s level %s union reward' % (index + 1, level)
				continue
			AS(roleID, EnumAward.HSUnionRankAward, itemList = [(coding, RC(RH, cnt)) for (coding, cnt) in cfg.rewardItems], clientDescParam = (index+1, ))
		if index == 0:
			uTipsFlag = True
			uTips += GlobalPrompt.HunluanSpace_RT_1 % unionObj.union_name
		elif index == 1:
			uTipsFlag = True
			uTips += GlobalPrompt.HunluanSpace_RT_2 % unionObj.union_name
		elif index == 2:
			uTipsFlag = True
			uTips += GlobalPrompt.HunluanSpace_RT_3 % unionObj.union_name
		
	#个人排名奖励
	person_rank_data = SpacePersonRankObj.role_rank_dict.items()
	#伤害 --> ID
	person_rank_data.sort(key = lambda x : (x[1][2], x[0]), reverse = True)
	#个人伤害榜前五有奖励
	person_rank_data = person_rank_data[:5]
	
	pTips = GlobalPrompt.HunluanSpace_PRT
	pTipsFlag = False
	
	HHPRG = HunluanSpaceConfig.HunluanPersonRank_Dict.get
	
	for index, person_data in enumerate(person_rank_data):
		if not person_data[1][2]:
			#没有伤害
			continue
		cfg = HHPRG((index + 1, GetCloseValue(person_data[1][3], HHRL)))
		if not cfg:
			print 'GE_EXC, HunluanSpace EndHunluanSpace can not find rank %s level %s person reward' % (index + 1, level)
			continue
		AS(person_data[0], EnumAward.HSPersonRankAward,money=RC(RH, cfg.rewardMoney), itemList = [(coding, RC(RH, cnt)) for (coding, cnt) in cfg.rewardItems], clientDescParam = (index+1, ))
		if index == 0:
			pTipsFlag = True
			pTips += GlobalPrompt.HunluanSpace_RT_1 % person_data[1][0]
		elif index == 1:
			pTipsFlag = True
			pTips += GlobalPrompt.HunluanSpace_RT_2 % person_data[1][0]
		elif index == 2:
			pTipsFlag = True
			pTips += GlobalPrompt.HunluanSpace_RT_3 % person_data[1][0]
		elif index == 3:
			pTipsFlag = True
			pTips += GlobalPrompt.HunluanSpace_RT_4 % person_data[1][0]
		elif index == 4:
			pTipsFlag = True
			pTips += GlobalPrompt.HunluanSpace_RT_5 % person_data[1][0]
		
	#公会积分奖励
	HHUSG = HunluanSpaceConfig.HunluanUnionScore_Dict.get
	HHUSL = HunluanSpaceConfig.HunluanUnionScore_List
	ESP = EnumTempObj.SpaceRole
	RFBR = cRoleMgr.FindRoleByRoleID
	
	global NowSceneIDList
	for unionObj in HunLuanSpaceUnion_Dict.itervalues():
		#取消tick
		unionObj.unreg_sync_rank_data()
		if HSActiveID == 2:
			#梦幻龙域的话取消掉下一波的tick
			unionObj.unreg_next_demon_tick()
		#计算一下积分, 获取配置
		if unionObj.union_score:
			score = GetCloseValue(unionObj.union_score, HHUSL)
		else:
			#0积分的话没有奖励
			score = 0
		#把所有进来过的玩家的临时对象清理掉
		for roleID, level in unionObj.join_role_dict.iteritems():
			role = RFBR(roleID)
			if role:
				#清理临时对象
				role.SetTempObj(ESP, None)
				#回城
				if role.GetSceneID() in NowSceneIDList:
					role.BackPublicScene()
			#奖励
			if score:
				cfg = HHUSG((score, GetCloseValue(level, HHRL)), None)
				if cfg:
					AS(roleID, EnumAward.HSUnionScoreAward, money=RC(RH, cfg.rewardMoney), itemList = [(coding, RC(RH, cnt)) for (coding, cnt) in cfg.rewardItems], exp=RC(RH, cfg.rewardExp), clientDescParam = (unionObj.union_score, ))
				else:
					print 'GE_EXC, HunluanSpace EndHunluanSpace can not find score %s level %s union score reward' % (score, level)
				
	SpaceUnionRankObj = None
	SpacePersonRankObj = None
	
	WorldLevel = 0
	HSActiveID = 0
	BeginTime = 0
	
	SSP = cSceneMgr.SearchPublicScene
	
	global LevelToSceneID
	for sceneID in LevelToSceneID.itervalues():
		scene = SSP(sceneID)
		if not scene:
			continue
		#删除所有npc
		for npc in scene.GetAllNPC():
			npc.Destroy()
	
	#清理
	global CanInUnionIDList, TpPos, TpPosDict
	TpPos = None
	NowSceneIDList = []
	CanInUnionIDList = []
	TpPosDict = {}
	LevelToSceneID = {}
	HunLuanSpaceUnion_Dict = {}
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.HunluanSpace_End)
	if uTipsFlag:
		cRoleMgr.Msg(1, 0, uTips)
	if pTipsFlag:
		cRoleMgr.Msg(1, 0, pTips)
	
def ClickTp(role, npc):
	#点击传送要战胜tp守卫
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	#根据世界等级获取tp守卫的mcid
	global WorldLevel
	cfg = HunluanSpaceConfig.HunluanTp_Dict.get(WorldLevel)
	if not cfg:
		print 'GE_EXC, HunluanSpace ClickTp can not find guard mcid by world level %s' % WorldLevel
		return
	
	if role.GetCD(EnumCD.HunluanSpaceCD):
		role.Msg(2, 0, GlobalPrompt.HunluanSpace_CD)
		return
	
	PVE_Guard(role, cfg.fightType, cfg.mcid, AfterGuardPlay, npc)
	
def PVE_Guard(role, fightType, mcid, afterPlay, param):
	#与tp守卫pve战斗 -- 不可跳过战斗
	fight = Fight.Fight(fightType)
	
	left_camp, right_camp = fight.create_camp()
	
	left_camp.create_online_role_unit(role, control_role_id = role.GetRoleID(), use_px = True)
	right_camp.create_monster_camp_unit(mcid)
	
	fight.after_play_fun = afterPlay
	fight.after_fight_param = param
	
	fight.start()
	
def AfterGuardPlay(fightObj):
	global IsHunluanSpaceOpen
	if not IsHunluanSpaceOpen: return
	
	#与tp守卫战斗结束收处理 --  这里要在战斗播放完后处理
	if fightObj.result is None:
		print "GE_EXC, HunluanSpace guard fight error"
		return
	
	roles = fightObj.left_camp.roles
	if not roles:
		return
	role = list(roles)[0]
	
	if fightObj.result == -1:
		#与守卫战斗后失败传送到固定点
		global TpPos
		role.JumpPos(*TpPos)
		return
	
	#选择传送到哪一层
	ChoiceRevive(role, fightObj.after_fight_param)
	
def ChoiceRevive(role, npc):
	#选择传送到哪一层
	if not Status.CanInStatus(role, EnumInt1.ST_TP):
		return
	
	spaceRole = role.GetTempObj(EnumTempObj.SpaceRole)
	if not spaceRole or not spaceRole.role:
		return
	
	#获取npc字典
	pos = npc.GetPyDict()[1]
	
	#根据玩家的当前层数获取公会该层的传送路线
	tpDirections = spaceRole.union_obj.directions.get(spaceRole.level)
	if not tpDirections:
		print 'GE_EXC, HunluanSpace ClickTp can not get tpDirections'
		return
	
	#获取传送的层数
	nextLevel = tpDirections[pos-1]
	
	global LevelToSceneID
	sceneID =LevelToSceneID.get(nextLevel)
	if not sceneID:
		print 'GE_EXC, HunluanSpace ClickTp can not get next scene id'
		return
	
	scene = cSceneMgr.SearchPublicScene(sceneID)
	if not scene:
		print 'GE_EXC, HunluanSpace can not find scene id %s' % sceneID
		return
	
	oldLevel = spaceRole.level
	spaceRole.level = nextLevel
	spaceRole.scene_id = sceneID
	
	#找到正确路径了
	if nextLevel - 1 == oldLevel:
		spaceRole.union_obj.add_correct_dir(role.GetRoleName(), oldLevel, pos)
		
		
	#传送
	global TpPos
	role.Revive(sceneID, *TpPos)
	
	#传送cd
	if not role.GetCD(EnumCD.HunluanSpaceCD):
		role.SetCD(EnumCD.HunluanSpaceCD, 5)
	
def ClickDemon(role, npc):
	#梦幻龙域
	if role.GetCD(EnumCD.HunluanSpaceCD):
		role.Msg(2, 0, GlobalPrompt.HunluanSpace_CD)
		return
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	spaceRole = role.GetTempObj(EnumTempObj.SpaceRole)
	if not spaceRole or not spaceRole.role:
		return
	
	if spaceRole.union_obj.active_id == 1:
		return
	
	npcDict = npc.GetPyDict()
	
	if role.GetUnionID() != npcDict[1]:
		return
	
	npcID = npc.GetNPCID()
	
	hp_dict = spaceRole.union_obj.hp_dict.get(npcID)
	if not hp_dict:
		#根据阵营ID获取其中monster血量
		oldHp = FightConfig.HSMONSTER_HP_DICT.get(npcDict[5])
		if not oldHp:
			print 'GE_EXC, HunluanSpace ClickDemon can not find monster hp % s' % npcDict[5]
			return
		#初始化血量字典
		spaceRole.union_obj.hp_dict[npcID] = hp_dict = {'total_hp':oldHp, -4:oldHp}
	else:
		oldHp = hp_dict['total_hp']
	
	role.SetCD(EnumCD.HunluanSpaceCD, EnumGameConfig.HunluanSpace_ClickCD)
	
	PVE_Demon(role, npcDict[4], npcDict[5], AfterDemonFight, (oldHp, npcID, npc, hp_dict.copy()))
	
def PVE_Demon(role, fightType, mcid, afterFight, param):
	fight = Fight.Fight(fightType)
	
	left_camp, right_camp = fight.create_camp()
	
	left_camp.create_online_role_unit(role, control_role_id = role.GetRoleID(), use_px = True)
	
	_, _, _, hp_dict = param
	
	#绑定血量字典
	right_camp.bind_hp(hp_dict)
	right_camp.create_monster_camp_unit(mcid)
	
	fight.after_fight_fun = afterFight
	fight.after_fight_param = param
	
	fight.start()
	
def AfterDemonFight(fightObj):
	global IsHunluanSpaceOpen
	if not IsHunluanSpaceOpen: return
	
	if fightObj.result is None:
		print 'GE_EXC, HunluanSpace demon fight error'
		return
	
	roles = fightObj.left_camp.roles
	if not roles:
		return
	role = list(roles)[0]
	
	oldHp, npcID, npc, hp_dict = fightObj.after_fight_param
	
	spaceRole = role.GetTempObj(EnumTempObj.SpaceRole)
	if not spaceRole or not spaceRole.role:
		return
	
	#战斗结束后npc可能已经被杀死了
	if npcID not in spaceRole.union_obj.npc_dict:
		killName = spaceRole.union_obj.kill_npc_dict.get(npcID)
		if killName:
			role.Msg(2, 0, GlobalPrompt.HunluanSpace_NoDamage % killName)
		return
	
	#计算伤害值
	nowHp = hp_dict.get('total_hp', None)
	if type(nowHp) != int:
		print 'GE_EXC, AfterDemonFight NOW HP ERROR'
		return
	damage = oldHp - nowHp
	if damage <= 0:
		return
	
	#修正血量
	spaceRole.union_obj.hp_dict[npcID]['total_hp'] -= damage
	if spaceRole.union_obj.hp_dict[npcID]['total_hp'] < 0:
		spaceRole.union_obj.hp_dict[npcID]['total_hp'] = 0
	spaceRole.union_obj.hp_dict[npcID][-4] -= damage
	
	spaceRole.add_role_damage(damage)
	
	with HunluanSpaceFight_Log:
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveHunluanSpaceInFight, (1, fightObj.round, role.GetCD(EnumCD.HunluanSpaceCD)))
	
	#当前总血量判断是否死亡
	if spaceRole.union_obj.hp_dict[npcID]['total_hp'] > 0:
		global TpPos
		role.JumpPos(*TpPos)
		return
	
	score = npc.GetPyDict().get(2)
	if not score:
		print 'GE_EXC, HuanluanSpace kill 0 score demon'
		return
	
	fightObj.set_fight_statistics(role.GetRoleID(), EnumFightStatistics.EnumHSScore, score)
	
	#加公会积分
	spaceRole.union_obj.add_union_score(score)
	
	#删除npc
	npc.Destroy()
	del spaceRole.union_obj.npc_dict[npcID]
	#记录击杀npc的玩家名字
	spaceRole.union_obj.kill_npc_dict[npcID] = role.GetRoleName()
	
	if not spaceRole.union_obj.npc_dict:
		#如果最后一个npc被击杀了, 刷出下一波
		spaceRole.union_obj.ready_next_demon()
	
def ClickDevil(role, npc):
	#群魔乱舞
	if role.GetCD(EnumCD.HunluanSpaceCD):
		role.Msg(2, 0, GlobalPrompt.HunluanSpace_CD)
		return
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	spaceRole = role.GetTempObj(EnumTempObj.SpaceRole)
	if not spaceRole or not spaceRole.role:
		return
	
	if spaceRole.union_obj.active_id == 2:
		return
	
	npcDict = npc.GetPyDict()
	if role.GetUnionID() != npcDict[1]:
		return
	
	npcID = npc.GetNPCID()
	hp_dict = spaceRole.union_obj.hp_dict.get(npcID)
	if not hp_dict:
		#根据阵营ID获取其中monster血量
		oldHp = FightConfig.HSMONSTER_HP_DICT.get(npcDict[5])
		if not oldHp:
			print 'GE_EXC, HunluanSpace ClickDemon can not find monster hp % s' % npcDict[5]
			return
		#初始化血量字典
		spaceRole.union_obj.hp_dict[npcID] = hp_dict = {'total_hp':oldHp, -4:oldHp}
	else:
		oldHp = hp_dict['total_hp']
	
	role.SetCD(EnumCD.HunluanSpaceCD, EnumGameConfig.HunluanSpace_ClickCD)
	
	PVE_Devil(role, npcDict[4], npcDict[5], AfterDevilFight, (spaceRole, oldHp, npcID, npc, hp_dict.copy()))
	
def PVE_Devil(role, fightType, mcid, afterFight, param):
	fight = Fight.Fight(fightType)
	
	left_camp, right_camp = fight.create_camp()
	
	left_camp.create_online_role_unit(role, control_role_id = role.GetRoleID(), use_px = True)
	
	spaceRole, _, _, _, hp_dict = param
	
	if spaceRole.union_obj.buff:
		#有buff的话增伤20%
		for u in left_camp.pos_units.itervalues():
			u.damage_upgrade_rate += 0.2
	
	#绑定血量字典
	right_camp.bind_hp(hp_dict)
	right_camp.create_monster_camp_unit(mcid)
	
	fight.after_fight_fun = afterFight
	fight.after_fight_param = param
	
	fight.start()
	
def AfterDevilFight(fightObj):
	global IsHunluanSpaceOpen
	if not IsHunluanSpaceOpen: return
	
	if fightObj.result is None:
		print 'GE_EXC, HunluanSpace devil fight error'
		return
	
	roles = fightObj.left_camp.roles
	if not roles:
		return
	role = list(roles)[0]
	
	#注:npc可能是个空对象
	_, oldHp, npcID, npc, hp_dict = fightObj.after_fight_param
	
	spaceRole = role.GetTempObj(EnumTempObj.SpaceRole)
	if not spaceRole or not spaceRole.role:
		return
	
	#战斗结束后npc可能已经被杀死了
	if npcID not in spaceRole.union_obj.npc_dict:
		killName = spaceRole.union_obj.kill_npc_dict.get(npcID)
		if killName:
			role.Msg(2, 0, GlobalPrompt.HunluanSpace_NoDamage % killName)
		return
	
	#计算伤害值
	nowHp = hp_dict.get('total_hp', None)
	if type(nowHp) != int:
		print 'GE_EXC, AfterDevilFight NOW HP ERROR'
		return
	damage = oldHp - nowHp
	if damage <= 0:
		return
	
	#修正血量
	spaceRole.union_obj.hp_dict[npcID]['total_hp'] -= damage
	if spaceRole.union_obj.hp_dict[npcID]['total_hp'] < 0:
		spaceRole.union_obj.hp_dict[npcID]['total_hp'] = 0
	spaceRole.union_obj.hp_dict[npcID][-4] -= damage
	
	spaceRole.add_role_damage(damage)
	
	with HunluanSpaceFight_Log:
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveHunluanSpaceInFight, (2, fightObj.round, role.GetCD(EnumCD.HunluanSpaceCD)))
	
	#当前总血量判断是否死亡
	if spaceRole.union_obj.hp_dict[npcID]['total_hp'] > 0:
		global TpPos
		role.JumpPos(*TpPos)
		return
	
	score = npc.GetPyDict().get(2)
	if not score:
		print 'GE_EXC, HunluanSpace killed 0 score devil'
		return
	
	fightObj.set_fight_statistics(role.GetRoleID(), EnumFightStatistics.EnumHSScore, score)
	
	#加公会积分
	spaceRole.union_obj.add_union_score(score)
	
	#删除npc
	npc.Destroy()
	del spaceRole.union_obj.npc_dict[npcID]
	
	#记录击杀npc的玩家名字
	spaceRole.union_obj.kill_npc_dict[npcID] = role.GetRoleName()
	
	if not spaceRole.union_obj.npc_dict:
		#如果最后一个npc被击杀了, 刷出下一波
		spaceRole.union_obj.create_devil(None, None)
	
def ClickDevilBoss(role, npc):
	#点击群魔乱舞boss
	if role.GetCD(EnumCD.HunluanSpaceCD):
		role.Msg(2, 0, GlobalPrompt.HunluanSpace_CD)
		return
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	spaceRole = role.GetTempObj(EnumTempObj.SpaceRole)
	if not spaceRole or not spaceRole.role:
		return
	
	#不是自己公会的boss
	npcDict = npc.GetPyDict()
	if role.GetUnionID() != npcDict[1]:
		return
	
	#过期了不让点了
	if spaceRole.union_obj.time_past:
		role.Msg(2, 0, GlobalPrompt.HunluanSpace_DevilBoss_1)
		return
	
	if not spaceRole.union_obj.boss_hp_dict:
		#根据阵营ID获取其中boss血量
		oldHp = FightConfig.HSMONSTER_HP_DICT.get(npcDict[3])
		if not oldHp:
			print 'GE_EXC, HunluanSpace ClickDevilBoss can not find monster hp % s' % npcDict[3]
			return
		#初始化血量字典
		spaceRole.union_obj.boss_hp_dict = hp_dict = {'total_hp':oldHp, -4:oldHp}
	else:
		hp_dict = spaceRole.union_obj.boss_hp_dict
		oldHp = hp_dict['total_hp']
		
	role.SetCD(EnumCD.HunluanSpaceCD, EnumGameConfig.HunluanSpace_ClickCD)
	
	PVE_DevilBoss(role, npcDict[2], npcDict[3], AfterDevilBoss, (oldHp, hp_dict.copy()))
	
def PVE_DevilBoss(role, fightType, mcid, afterFight, param):
	fight = Fight.Fight(fightType)
	
	left_camp, right_camp = fight.create_camp()
	
	left_camp.create_online_role_unit(role, control_role_id = role.GetRoleID(), use_px = True)
	
	_, hp_dict = param
	
	#绑定血量字典
	right_camp.bind_hp(hp_dict)
	right_camp.create_monster_camp_unit(mcid)
	
	fight.after_fight_fun = afterFight
	fight.after_fight_param = param
	
	fight.start()
	
def AfterDevilBoss(fightObj):
	global IsHunluanSpaceOpen
	if not IsHunluanSpaceOpen: return
	
	if fightObj.result is None:
		print 'GE_EXC, HunluanSpace devil boss fight error'
		return
	
	roles = fightObj.left_camp.roles
	if not roles:
		return
	role = list(roles)[0]
	
	spaceRole = role.GetTempObj(EnumTempObj.SpaceRole)
	if not spaceRole or not spaceRole.role:
		return
	
	#有buff了, 代表boss已经被击杀了
	if spaceRole.union_obj.buff:
		return
	
	#已经过期了
	if spaceRole.union_obj.time_past:
		return
	
	#先传送
	global TpPos
	role.JumpPos(*TpPos)
	
	oldHp, hp_dict = fightObj.after_fight_param
	
	#计算伤害
	nowHp = hp_dict.get('total_hp', None)
	if type(nowHp) != int:
		print 'GE_EXC, AfterDevilBoss NOW HP ERROR'
		return
	damage = oldHp - nowHp
	if damage <= 0:
		return
	
	#修正血量
	spaceRole.union_obj.boss_hp_dict['total_hp'] -= damage
	if spaceRole.union_obj.boss_hp_dict['total_hp'] < 0:
		spaceRole.union_obj.boss_hp_dict['total_hp'] = 0
	spaceRole.union_obj.boss_hp_dict[-4] -= damage
	
	with HunluanSpaceFight_Log:
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveHunluanSpaceInFight, (3, fightObj.round, role.GetCD(EnumCD.HunluanSpaceCD)))
	
	#当前总血量判断是否死亡
	if spaceRole.union_obj.boss_hp_dict['total_hp'] > 0:
		return
	
	#死了就给buff
	spaceRole.union_obj.add_buff()
	
def InitClickFun():
	'''
	初始化点击函数
	'''
	#tp点击函数
	for npcType in (16037, 16038, 16039):
		NPCServerFun.RegNPCServerOnClickFunEx(npcType, ClickTp)
	
	#群魔乱舞boss点击函数
	for npcType in HunluanSpaceConfig.HunluanDevilBNpcTypeSet:
		NPCServerFun.RegNPCServerOnClickFunEx(npcType, ClickDevilBoss)
	
	#恶魔点击函数
	for npcType in HunluanSpaceConfig.HunluanDevilNpcTypeSet:
		NPCServerFun.RegNPCServerOnClickFunEx(npcType, ClickDevil)
	
	#妖怪点击函数
	for npcType in HunluanSpaceConfig.HunluanDemonNpcTypeSet:
		NPCServerFun.RegNPCServerOnClickFunEx(npcType, ClickDemon)
	
def GetCloseValue(value, value_list):
	'''
	获取临近的值
	@param value:
	@param value_list:
	'''
	tmp_level = 0
	for i in value_list:
		if i > value:
			return tmp_level
		tmp_level = i
	else:
		return tmp_level
	
def ClientLost(role, param):
	'''
	刷新掉线
	@param role:
	@param param:
	'''
	global IsHunluanSpaceOpen
	if not IsHunluanSpaceOpen: return
	
	if role.GetLevel() < EnumGameConfig.HunluanSpace_LvLimit:
		return
	
	global NowSceneIDList
	if role.GetSceneID() not in NowSceneIDList:
		return
	
	spaceRole = role.GetTempObj(EnumTempObj.SpaceRole)
	if not spaceRole or not spaceRole.role:
		return
	
	role.BackPublicScene()
	
def AfterLeaveUnion(role, param):
	'''
	离开公会
	@param role:
	@param param:
	'''
	global IsHunluanSpaceOpen
	if not IsHunluanSpaceOpen: return
	
	if role.GetLevel() < EnumGameConfig.HunluanSpace_LvLimit:
		return
	
	global NowSceneIDList
	if role.GetSceneID() not in NowSceneIDList:
		return
	
	spaceRole = role.GetTempObj(EnumTempObj.SpaceRole)
	if not spaceRole or not spaceRole.role:
		return
	
	if role.GetRoleID() in spaceRole.union_obj.join_role_dict:
		del spaceRole.union_obj.join_role_dict[role.GetRoleID()]
	
	role.BackPublicScene()
	
	role.SetTempObj(EnumTempObj.SpaceRole, None)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross and not Environment.EnvIsYY():
		InitClickFun()
		Cron.CronDriveByMinute((2038, 1, 1), HalfHourReady, H = "H == 19", M = "M == 30")
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("HunluanSpace_Join", "请求进入混乱时空"), RequestJoinSpace)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("HunluanSpace_Leave", "请求离开混乱时空"), RequestLeaveSpace)
		
		Event.RegEvent(Event.Eve_ClientLost, ClientLost)
		Event.RegEvent(Event.Eve_BeforeExit, ClientLost)
		Event.RegEvent(Event.Eve_AfterLeaveUnion, AfterLeaveUnion)
		Event.RegEvent(Event.Eve_DelUnion, AfterLeaveUnion)
		
		
