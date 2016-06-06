#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.KuafuZhanchang.KuafuZhanchangMgr")
#===============================================================================
# 跨服战场
#===============================================================================
import math
import heapq
import random
import cRoleMgr
import cDateTime
import cSceneMgr
import cComplexServer
import Environment
from ComplexServer.Time import Cron
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig, EnumAward
from Game.NPC import NPCServerFun
from Game.SysData import WorldData
from Game.Fight import Fight, Middle
from Game.Activity.KuafuZhanchang import KuafuZhanchangConfig
from Game.Role.Data import EnumCD, EnumInt1, EnumDayInt8
from Game.Scene import PublicScene
from Game.Activity.Award import AwardMgr
from Game.Role import Status, Event
from Util import Random

CAMP_ID = 0
MAX_HP = 1
NOW_HP = 2
ZDL = 3
LEVEL = 4
NAME = 5
JUDIAN_TYPE = 6
VOTES = 7
IS_BOSS = 8
IS_GUARD = 9
SCORE = 10
GUARD_TIME = 11
KILL_CNT = 12
	
if "_HasLoad" not in dir():
	#活动开启
	IsStart = False
	#是否能够进入
	CanIn = False
	
	#{role_id : [zdl、等级、名字]}
	KFZC_ALL_ROLE = {}
	
	#战斗数据 -- {role_id : fight_data}
	KFZC_ALL_ROLE_FIGHT_DATA = {}
	
	#血量 -- {role_id : hp_dict}
	KFZC_ALL_ROLE_HP_DATA = {}
	
	#{role_id : camp_id}
	KFZC_ROLE_CAMP = {}
	
	#{npc_id : judian_obj}
	KFZC_NPC_JUDIAN = {}
	
	#{scene_id : kfzc_obj}
	KFZC_SCENE_KFZC = {}
	
	#{role_id : judian_obj}
	KFZC_ROLE_JUDIAN = {}
	
	
	#{role_id : set(已转到的奖励id集合)}
	KFZC_TABLE_DICT = {}
	
	#攻击方 -- {role_id : [阵营id, 最大血量, 当前血量, 战斗力, 等级, 名字, 据点id, 得票数, 是否领主, 是否守卫, 积分, 复活时间, 连杀数]}
	KFZC_AttackData = AutoMessage.AllotMessage("KFZC_AttackData", "跨服战场攻击方数据")
	#防守方 -- {role_id : [阵营id, 最大血量, 当前血量, 战斗力, 等级, 名字, 据点id, 得票数, 是否领主, 是否守卫, 积分, 复活时间, 连杀数]}
	KFZC_DefenseData = AutoMessage.AllotMessage("KFZC_DefenseData", "跨服战场防守方数据")
	#守卫 & 领主 -- {1:[领主role_id, 领主名字], 2:{守卫role_id:名字}}
	KFZC_GuardData = AutoMessage.AllotMessage("KFZC_GuardData", "跨服战场守卫数据")
	#据点数据 -- [据点id, 阵营id, 归属时间戳, 投票时间戳, 守卫时间]
	KFZC_JudianData = AutoMessage.AllotMessage("KFZC_JudianData", "跨服战场据点数据")
	#投票数据 -- set(role_id)
	KFZC_JudianVotes = AutoMessage.AllotMessage("KFZC_JudianVotes", "跨服战场据点投票数据")
	
	#个人数据 -- [阵营id, 最大血量, 当前血量, 战斗力, 等级, 名字, 据点id, 得票数, 是否领主, 是否守卫, 积分, 复活时间, 连杀数]
	KFZC_PersonalData = AutoMessage.AllotMessage("KFZC_PersonalData", "跨服战场个人数据")
	
	#积分榜
	#{role_id : [阵营id, 最大血量, 当前血量, 战斗力, 等级, 名字, 据点id, 得票数, 是否领主, 是否守卫, 积分, 复活时间, 连杀数]}
	KFZC_ScoreRankData = AutoMessage.AllotMessage("KFZC_ScoreRankData", "跨服战场积分榜")
	
	#阵营积分 {阵营id:积分}
	KFZC_CampScore = AutoMessage.AllotMessage("KFZC_CampScore", "跨服战场阵营积分")
	
	KFZC_CampScoreEx = AutoMessage.AllotMessage("KFZC_CampScoreEx", "跨服战场阵营最终积分")
	
	#跨服战场击杀记录 -- [攻击者(1-自己, 2-别人), 胜负(1-胜, 2-负), 攻击者名字, 获得积分]
	KFZC_KillRecord = AutoMessage.AllotMessage("KFZC_KillRecord", "跨服战场击杀记录")
	
	#转盘奖励索引
	KFZC_TableIndex = AutoMessage.AllotMessage("KFZC_TableIndex", "跨服战场转盘奖励索引")
	#已领取转盘奖励
	KFZC_TableReward = AutoMessage.AllotMessage("KFZC_TableReward", "跨服战场转盘已领取转盘奖励索引")
	
	#===========================================================================
	# 日志
	#===========================================================================
	#跨服战场转盘
	KFZC_TurnTable_Log = AutoLog.AutoTransaction("KFZC_TurnTable_Log", "跨服战场转盘日志")
	#跨服战场积分日志
	KFZC_Score_Log = AutoLog.AutoTransaction("KFZC_Score_Log", "跨服战场积分日志")
	#跨服战场排行榜日志
	KFZC_Rank_Log = AutoLog.AutoTransaction("KFZC_Rank_Log", "跨服战场排行榜日志")
	
#===============================================================================
# scene
#===============================================================================
####################跨服战场场景#########################
def RegSceneAfterJoinWildBossFun():
	#注册进入场景后处理函数
	PSJF = PublicScene.SceneJoinFun
	PSBF = PublicScene.SceneBeforeLeaveFun
	EKD = EnumGameConfig.KFZC_SCENE_DICT
	
	for _, sceneIdList in EKD.iteritems():
		for sceneId in sceneIdList:
			PSJF[sceneId] = AfterJoin
			PSBF[sceneId] = BeforeLeave
	
def AfterJoin(scene, role):
	#进入战场场景
	global KFZC_SCENE_KFZC
	kfzc = KFZC_SCENE_KFZC.get(scene.GetSceneID())
	if not kfzc:
		return
	
	global KFZC_ROLE_CAMP
	role_id = role.GetRoleID()
	
	camp_id = KFZC_ROLE_CAMP.get(role_id)
	if not camp_id:
		return
	
	camp_data = kfzc.all_role_data.get(camp_id, {})
	role_data = camp_data.get(role_id)
	if not role_data:
		return
	
	#同步个人数据
	role.SendObj(KFZC_PersonalData, role_data)
	#同步贡献榜数据
	role.SendObj(KFZC_ScoreRankData, camp_data)
	#同步左右阵营贡献
	role.SendObj(KFZC_CampScore, kfzc.camp_score_data)
	#同步击杀记录
	role.SendObj(KFZC_KillRecord, kfzc.fight_record.setdefault(role_id, []))
	
def BeforeLeave(scene, role):
	#离开场景
	global KFZC_SCENE_KFZC
	kfzc = KFZC_SCENE_KFZC.get(scene.GetSceneID())
	if not kfzc:
		return
	
	kfzc.leave_role(role.GetRoleID(), role)
	
###############跨服战场准备场景############################
@PublicScene.RegSceneAfterJoinRoleFun(EnumGameConfig.KFZC_JUMP_SCENE)
def AfterJoinScene(scene, role):
	global KFZC_ALL_ROLE, KFZC_ALL_ROLE_HP_DATA, CanIn
	
	if not CanIn:
		#活动已经开始了, 将玩家踢回本服
		role.GotoLocalServer(None, None)
		return
	
	role_id = role.GetRoleID()
	
	#用作排序用
	KFZC_ALL_ROLE[role_id] = [role.GetZDL(), role.GetLevel(), role.GetRoleName()]
	#保存血量
	KFZC_ALL_ROLE_HP_DATA[role_id] = {}
	
@PublicScene.RegSceneBeforeLeaveFun(EnumGameConfig.KFZC_JUMP_SCENE)
def BeforeLeaveScene(scene, role):
	global KFZC_ALL_ROLE
	
	role_id = role.GetRoleID()
	
	if role_id in KFZC_ALL_ROLE:
		del KFZC_ALL_ROLE[role_id]
	
def RandomPos():
	pos = random.choice(EnumGameConfig.KFZC_JUMP_POS)
	return random.randint(*pos[:2]), random.randint(*pos[2:])
#===============================================================================
# class
#===============================================================================
class KFZC(object):
	'''
	创建参数 : 
		[(role_id, [最大血量, 当前血量, 战斗力, 等级, 名字， 积分， 连杀数]),...], 场景id
	'''
	def __init__(self, role_data, scene_id):
		self.scene_id = scene_id
		
		#(role_id, [战斗力, 等级, 名字]) -- 排序用
		self.role_data = role_data
		
		#左阵营
		#{role_id : [阵营id, 最大血量, 当前血量, 战斗力, 等级, 名字, 据点id, 得票数, 是否领主, 是否守卫, 积分, 复活时间, 连杀数]}
		self.left_role_data = {}
		self.left_roles = set()
		
		#右阵营
		#{role_id : [阵营id, 最大血量, 当前血量, 战斗力, 等级, 名字, 据点id, 得票数, 是否领主, 是否守卫, 积分, 复活时间, 连杀数]}
		self.right_role_data = {}
		self.right_roles = set()
		
		#共享引用
		self.all_role_data = {1:self.left_role_data, 2:self.right_role_data}
		
		#阵营积分 -- {camp_id:score}
		self.camp_score_data = {1:0, 2:0}
		
		#据点对象列表
		self.judian_list = []
		
		#战斗记录 -- {role_id : [攻击者(1-自己, 2-别人), 胜负(1-胜, 2-负), 攻击者名字, 获得积分]}
		self.fight_record = {}
		
		#创建npc
		self.create_npc()
		#分配阵营
		self.distribution_camp()
		
		self.check_cnt = 0
		
		#同步贡献榜tick
		self.sync_tick = cComplexServer.RegTick(EnumGameConfig.KFZC_SYNC_SEC, self.sync_data)
		#检查占据tick
		self.check_tick = cComplexServer.RegTick(EnumGameConfig.KFZC_CHECK_SEC, self.check_judian)
		
	def create_npc(self):
		#创建npc
		self.scene = cSceneMgr.SearchPublicScene(self.scene_id)
		if not self.scene:
			print "GE_EXC, kuafu zhanchang can not find scene id %s" % self.scene_id
			return
		
		global KFZC_NPC_JUDIAN
		
		#创建据点对象
		npc = self.scene.CreateNPC(*EnumGameConfig.KFZC_BIG_JUDIAN_NPC)
		KFZC_NPC_JUDIAN[npc.GetNPCID()] = judian = Judian(1, EnumGameConfig.KFZC_BIG_GUARD_CNT, self)
		self.judian_list.append(judian)
		
		npc = self.scene.CreateNPC(*EnumGameConfig.KFZC_SMALL_JUDIAN_NPC_1)
		KFZC_NPC_JUDIAN[npc.GetNPCID()] = judian = Judian(2, EnumGameConfig.KFZC_SMALL_GUARD_CNT, self)
		self.judian_list.append(judian)
		
		npc = self.scene.CreateNPC(*EnumGameConfig.KFZC_SMALL_JUDIAN_NPC_2)
		KFZC_NPC_JUDIAN[npc.GetNPCID()] = judian = Judian(3, EnumGameConfig.KFZC_SMALL_GUARD_CNT, self)
		self.judian_list.append(judian)
		
	def distribution_camp(self):
		#分配阵营
		#战斗力 --> 等级 --> 角色id
		self.role_data.sort(key = lambda x:(x[1][0], x[1][1], -x[0]), reverse=True)
		
		left_zdl = right_zdl = left_cnt = right_cnt = 0
		
		global KFZC_ROLE_CAMP, KFZC_SCENE_KFZC, KFZC_ALL_ROLE_FIGHT_DATA
		
		KFZC_SCENE_KFZC[self.scene_id] = self
		
		#人数平均 -- 向上取整, 在人数为奇数的时候倾向向右阵营多分配一人
		half_role_cnt = int(math.ceil(len(self.role_data) / 2.0))
		#是否分配到右阵营
		in_right = False
		
		CRFR = cRoleMgr.FindRoleByRoleID
		EKSP1 = EnumGameConfig.KFZC_SAFE_PLACE_1
		EKSP2 = EnumGameConfig.KFZC_SAFE_PLACE_2
		
		#{role_id : [阵营id, 最大血量, 当前血量, 战斗力, 等级, 名字, 据点id, 得票数, 是否领主, 是否守卫, 积分, 复活时间, 连杀数]}
		for role_data in self.role_data:
			role_id, (zdl, level, name) = role_data
			
			role = CRFR(role_id)
			if not role or role.IsKick():
				continue
			
			#战斗数据不能在刚跨服过来的时候取
			KFZC_ALL_ROLE_FIGHT_DATA[role_id] = fight_data = Middle.GetRoleData(role, use_property_X=True)
			if not fight_data:
				print 'GE_EXC, kuafu zhanchang distribution_camp get fight data error'
				continue
			
			#计算最大血量
			max_hp = CalMaxhp(fight_data)
			
			if in_right:
				self.right_role_data[role_id] = [2, max_hp, max_hp, zdl, level, name, 0, 0, 0, 0, 0, 0, 0]
				self.right_roles.add(role)
				
				right_zdl += zdl
				right_cnt += 1
				
				#记录玩家阵营id
				KFZC_ROLE_CAMP[role_id] = camp_id = 2
			else:
				self.left_role_data[role_id] = [1, max_hp, max_hp, zdl, level, name, 0, 0, 0, 0, 0, 0, 0]
				self.left_roles.add(role)
				
				left_zdl += zdl
				left_cnt += 1
				
				KFZC_ROLE_CAMP[role_id] = camp_id = 1
				
			#如果左阵营的战斗力 > 右阵营战斗力 & 右阵营的人数不足一半的话继续往右阵营分配人数
			in_right = True if left_zdl > right_zdl and right_cnt < half_role_cnt else False
			
			#传送
			if camp_id == 1:
				role.Revive(self.scene_id, random.randint(*EKSP1[0]), random.randint(*EKSP1[1]))
			else:
				role.Revive(self.scene_id, random.randint(*EKSP2[0]), random.randint(*EKSP2[1]))
		
	def leave_role(self, role_id, role):
		#玩家离开
		global KFZC_ROLE_JUDIAN, KFZC_ROLE_CAMP
		
		#离开据点
		judian = KFZC_ROLE_JUDIAN.get(role_id)
		if judian:
			judian.leave_role(role_id, role)
		
		#删除阵营记录
		camp_id = KFZC_ROLE_CAMP.get(role_id)
		if not camp_id:
			return
		del KFZC_ROLE_CAMP[role_id]
		
		if camp_id == 1 and role_id in self.left_role_data:
			del self.left_role_data[role_id]
			self.left_roles.discard(role)
			
		elif camp_id == 2 and role_id in self.right_role_data:
			del self.right_role_data[role_id]
			self.right_roles.discard(role)
		
	def return_role_data(self, role_id):
		#返回玩家数据
		return self.left_role_data.get(role_id) if role_id in self.left_role_data else self.right_role_data.get(role_id)
	
	def add_score(self, camp_id, score):
		#增加积分
		if camp_id not in self.camp_score_data:
			return
		self.camp_score_data[camp_id] += score
		
		with KFZC_Score_Log:
			AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveKFZCScore, (self.scene_id, camp_id, score))
		
		self.sync_score()
		
	def add_fight_record(self, role_id, role, record):
		#战斗记录
		record_list = self.fight_record.setdefault(role_id, [])
		if len(record_list) >= 6:
			#只记录四条
			record_list.pop(0)
		record_list.append(record)
		
		role.SendObj(KFZC_KillRecord, record_list)
		
	def sync_score(self):
		#同步积分
		for role in self.left_roles | self.right_roles:
			if not role or role.IsKick():
				continue
			role.SendObj(KFZC_CampScore, self.camp_score_data)
		
	def sync_data(self, argv, param):
		#左阵营积分榜
		global IsStart
		if not IsStart: return
		
		for role in self.left_roles:
			if not role or role.IsKick():
				continue
			role.SendObj(KFZC_ScoreRankData, self.left_role_data)
		
		#右阵营积分榜
		for role in self.right_roles:
			if not role or role.IsKick():
				continue
			role.SendObj(KFZC_ScoreRankData, self.right_role_data)
		
		self.sync_tick = cComplexServer.RegTick(EnumGameConfig.KFZC_SYNC_SEC, self.sync_data)
	
	def check_judian(self, argv, param):
		#结算时间点
		for judian in self.judian_list:
			judian.check_judian(param)
		
		self.check_cnt += 1
		
		if self.check_cnt >= 2:
			return
		
		self.check_tick = cComplexServer.RegTick(EnumGameConfig.KFZC_CHECK_SEC, self.check_judian)
		
	def reward(self):
		#左右阵营发奖
		
		#发奖前先强制结算一次占据
		self.check_judian(None, True)
		
		left_score = self.camp_score_data.get(1, 0)
		right_score = self.camp_score_data.get(2, 0)
		
		with KFZC_Rank_Log:
			#先记个日志吧
			AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveKFZCEndScore, (self.scene_id, left_score, right_score, self.left_role_data, self.right_role_data))
		
		if left_score > right_score:
			#左阵营胜
			self.reward_ex(self.left_role_data, 1)
			self.reward_ex(self.right_role_data, 2)
		elif left_score < right_score:
			#右阵营胜
			self.reward_ex(self.right_role_data, 1)
			self.reward_ex(self.left_role_data, 2)
		else:
			#积分相同, 双方都获得胜利加成
			self.reward_ex(self.right_role_data, 1)
			self.reward_ex(self.left_role_data, 1)
		
		#发奖后销毁对象
		self.destroy_kfzc()
		
	def reward_ex(self, role_data, is_win):
		#实际发放奖励
		#{role_id : [阵营id, 最大血量, 当前血量, 战斗力, 等级, 名字, 据点id, 得票数, 是否领主, 是否守卫, 积分, 复活时间, 连杀数]}
		if not role_data:
			return
		
		data = role_data.items()
		data.sort(key = lambda x : (x[1][SCORE], x[1][KILL_CNT], x[1][ZDL], x[1][LEVEL], -x[0]), reverse=True)
		
		KKG = KuafuZhanchangConfig.KFZC_PERSIONAL_SCORERANK_DICT
		CFR = cRoleMgr.FindRoleByRoleID
		EKS = EnumGameConfig.KFZC_MIN_SCORE
		tips = GlobalPrompt.KFZC_TIPS_18 if is_win == 1 else GlobalPrompt.KFZC_TIPS_19
		
		with KFZC_Score_Log:
			for index, d in enumerate(data):
				
				#积分少于多少不给奖励
				if d[1][SCORE] < EKS:
					continue
				cfg = KKG.get(is_win)
				if not cfg:
					print 'GE_EXC, KuafuZhanchang can not find win id %s' % is_win
					continue
				rank = index + 1
				for (min_rank, max_rank), cfgg in cfg.iteritems():
					if min_rank <= rank <= max_rank:
						break
				else:
					#找不到排名奖励就不给了
					continue
					
				role_id = d[0]
				role = CFR(role_id)
				if not role or role.IsKick():
					continue
				
				if cfgg.turnCnt:
					role.IncDI8(EnumDayInt8.KFZC_TurnTableCnt, cfgg.turnCnt)
				
				AwardMgr.SetAward(role_id, EnumAward.KFZCSeal, itemList = cfgg.items, clientDescParam = (tips, index+1))
			
	def destroy_kfzc(self):
		for role in self.scene.GetAllRole():
			role.SendObj(KFZC_CampScoreEx, self.camp_score_data)
		
		#销毁据点对象
		for judian in self.judian_list:
			judian.destroy_judian()
		
		#取消同步tick
		cComplexServer.UnregTick(self.sync_tick)
		cComplexServer.UnregTick(self.check_tick)
		
	def clear_role(self):
		for npc in self.scene.GetAllNPC():
			npc.Destroy()
		
		for role in self.scene.GetAllRole():
			role.GotoLocalServer(None, None)
		
class Judian(object):
	'''
	创建参数:据点类型, 跨服战场对象
	'''
	def __init__(self, judian_type, guard_cnt, kfzc_obj):
		#据点类型 (1-大, 2-小, 3-小）
		self.judian_type = judian_type
		
		#守卫个数
		self.guard_cnt = guard_cnt
		
		#阵营对象
		self.kfzc_obj = kfzc_obj
		
		#据点是否为空
		self.is_empty = True
		
		#攻击方id
		self.attack_camp_id = -1
		self.defense_camp_id = -1
		
		#{role_id : [阵营id, 最大血量, 当前血量, 战斗力, 等级, 名字, 据点id, 得票数, 是否领主, 是否守卫, 积分, 复活时间, 连杀数]}
		self.left_camp_dict = {}
		#{role_id : [阵营id, 最大血量, 当前血量, 战斗力, 等级, 名字, 据点id, 得票数, 是否领主, 是否守卫, 积分, 复活时间, 连杀数]}
		self.right_camp_dict = {}
		
		#左右阵营数据
		self.camp_dict = {1:self.left_camp_dict, 2:self.right_camp_dict}
		
		#战斗力用作当左右阵营人数相同时归属判定
		self.left_zdl = 0
		self.right_zdl = 0
		
		#同步的role
		self.roles = set()
		
		#最小堆
		#优先选择守卫（zdl --> role_level --> role_id, 复活时间)
		#[(zdl, role_level, role_id, 复活时间)]
		self.back_camp_list = []
		
		#只有防守方需要这个复活列表
		#复活按死亡先后顺序来, 只有前一个复活了后面的才有可能复活
		#[(zdl, level, role_id, 复活时间)]
		self.defense_fuhuo_list = []
		
		#进攻方的复活列表 -- 随机攻击用
		self.attack_fuhuo_list = []
		
		#守卫 -- {role_id:name}
		self.guard_dict = {}
		#领主 -- [role_id, name, 复活时间戳]
		self.boss_list = []
		#面板数据 -- [据点id, 阵营id, 归属时间戳, 投票时间戳, 守卫时间]
		self.judian_data = [self.judian_type, 0, 0, 0, 0]
		#已投票玩家id集合
		self.votes_role_set = set()
		
		#同步tick
		self.sync_judian_tick = 0
		#守卫tick
		self.guard_tick_id = 0
		
		#防守方复活tick
		self.defense_fuhuo_tick_id = 0
		#攻击方复活tick
		self.attack_fuhuo_tick_id = 0
		
		#归属tick
		self.belong_tick = 0
		#投票tick
		self.votes_tick = 0
		
	def add_watch_role(self, role_id, role):
		#观察者进入
		self.roles.add(role)
		
		global KFZC_ROLE_JUDIAN
		KFZC_ROLE_JUDIAN[role_id] = self
		
		#同步数据
		self.sync_role_data(role_id, role)
		
	def leave_watch_role(self, role_id, role):
		#观察者离开
		self.roles.discard(role)
		
		global KFZC_ROLE_JUDIAN
		if role_id in KFZC_ROLE_JUDIAN:
			del KFZC_ROLE_JUDIAN[role_id]
		
	def add_role(self, role_id, role):
		#玩家加入
		role_data = self.kfzc_obj.return_role_data(role_id)
		if not role_data:
			return
		
		camp_id = role_data[CAMP_ID]
		zdl = role_data[ZDL]
		level = role_data[LEVEL]
		name = role_data[NAME]
		judian_type = role_data[JUDIAN_TYPE]
		guard_time = role_data[GUARD_TIME]
		
		if not camp_id or judian_type:
			#不能直接从一个据点到另外一个据点
			return
		
		#修改玩家的据点id
		role_data[JUDIAN_TYPE] = self.judian_type
		
		if self.is_empty and not self.belong_tick:
			#据点是空的, 且不在归属计算阶段, 第一个玩家进入后30s判定据点归属
			self.belong_tick = cComplexServer.RegTick(EnumGameConfig.KFZC_BELONG_SEC, self.check_belong)
			#注册同步tick
			self.sync_judian_tick = cComplexServer.RegTick(5, self.sync_judian_data_tick)
			
			self.judian_data[2] = cDateTime.Seconds() + EnumGameConfig.KFZC_BELONG_SEC
			
			self.sync_judian()
		elif not self.is_empty and camp_id == self.defense_camp_id:
			#投票阶段完成后防守方可以上守卫
			#防守方进入
			if role_data[GUARD_TIME] > cDateTime.Seconds():
				#在复活时间, 进入复活
				self.add_defense_fuhuo(role_id)
			else:
				if self.guard_cnt > len(self.guard_dict):
					#如果守卫个数不足, 直接上守卫
					self.guard_dict[role_id] = name
					role_data[IS_GUARD] = 1
					self.sync_guard()
				else:
					#守卫个数足够了, 进入后备
					heapq.heappush(self.back_camp_list, (-zdl, -level, -role_id, -guard_time, name))
		elif not self.is_empty and camp_id == self.attack_camp_id:
			if role_data[GUARD_TIME] > cDateTime.Seconds():
				#在复活时间, 进入复活
				self.add_attack_fuhuo(role_id)
		
		#据点中玩家的数据是对阵营中玩家数据的引用共享
		if camp_id == 1:
			self.left_camp_dict[role_id] = role_data
			self.left_zdl += role_data[ZDL]
		else:
			self.right_camp_dict[role_id] = role_data
			self.right_zdl += role_data[ZDL]
		
		self.sync_role_data(role_id, role)
		
	def leave_role(self, role_id, role):
		#玩家离开 -- 离开据点和离开场景是一样的, 离开据点时要先处理防守方状态, 然后再删除数据
		
		#离开据点关面板
		self.leave_watch_role(role_id, role)
		
		global KFZC_ROLE_CAMP
		camp_id = KFZC_ROLE_CAMP.get(role_id)
		if not camp_id:
			return
		camp_dict = self.camp_dict.get(camp_id)
		if not camp_dict:
			return
		role_data = camp_dict.get(role_id)
		
		if not role_data or not role_data[JUDIAN_TYPE]:
			return
		
		role_data[JUDIAN_TYPE] = 0
		
		role_data[IS_GUARD] = 1
		
		if camp_id == self.defense_camp_id:
			#防守方离开
			if role_data[IS_BOSS]:
				#领主
				self.boss_list = []
				
				#先修改再删除
				role_data[IS_BOSS] = 0
			
			if role_data[IS_GUARD]:
				#守卫
				
				if role_id in self.guard_dict:
					del self.guard_dict[role_id]
				
				role_data[IS_GUARD] = 0
				
				if self.back_camp_list:
					#如果有后备的话从后备中提一个玩家来成为守卫
					zdl, _, rid, _, name = heapq.heappop(self.back_camp_list)
					if -rid in camp_dict:
						camp_dict[-rid][IS_GUARD] = 1
						self.guard_dict[-rid] = name
						
						#修改据点战斗力
						if camp_id == 1:
							self.left_zdl += zdl
						elif camp_id == 2:
							self.right_zdl += zdl
			
			#同步据点面板数据
			self.sync_guard()
		
		if camp_id == 1:
			self.left_zdl -= role_data[ZDL]
		elif camp_id == 2:
			self.right_zdl -= role_data[ZDL]
		
		role.SendObj(KFZC_PersonalData, role_data)
		
		del self.camp_dict[camp_id][role_id]
		
		#有人离开的时候检测一下是否需要切换阵营或者置空据点
		self.check_zhanju()
		
	def check_zhanju(self):
		#检测占据 -- 是否需要切换阵营或者置空据点
		
		if not self.left_camp_dict and not self.right_camp_dict:
			#两边都没有人了, 据点置空
			
			self.is_empty = True
			
			self.attack_camp_id = -1
			self.defense_camp_id = -1
			
			self.clear_judian()
			
			cComplexServer.UnregTick(self.sync_judian_tick)
			self.sync_judian_tick = 0
		
		elif not self.is_empty and self.camp_dict[self.attack_camp_id]:
			#攻击方有人
			if not self.camp_dict[self.defense_camp_id]:
				#防守方没人了
				self.switch_camp()
			elif (not self.boss_list or cDateTime.Seconds() < self.boss_list[2]) and (len(self.guard_dict) <= 1):
				#没有领主或者领主正在复活中 & 守卫的个数少于等于1
				self.switch_camp()
	
	def clear_judian(self):
		#清理据点数据
		self.boss_list = []
		self.guard_dict = {}
		self.judian_data = [self.judian_type, 0, 0, 0, 0]
		
		self.back_camp_list = []
		
		self.attack_fuhuo_list = []
		self.defense_fuhuo_list = []
		
		self.votes_role_set = set()
		
		for role_data in self.left_camp_dict.itervalues():
			role_data[VOTES] = 0
			role_data[GUARD_TIME] = 0
			role_data[IS_BOSS] = 0
			role_data[IS_GUARD] = 0
		for role_data in self.right_camp_dict.itervalues():
			role_data[VOTES] = 0
			role_data[GUARD_TIME] = 0
			role_data[IS_BOSS] = 0
			role_data[IS_GUARD] = 0
		
		#取消tick
		cComplexServer.UnregTick(self.belong_tick)
		self.belong_tick = 0
		
		cComplexServer.UnregTick(self.votes_tick)
		self.votes_tick = 0
		
		cComplexServer.UnregTick(self.guard_tick_id)
		self.guard_tick_id = 0
		
		cComplexServer.UnregTick(self.defense_fuhuo_tick_id)
		self.defense_fuhuo_tick_id = 0
		
		cComplexServer.UnregTick(self.attack_fuhuo_tick_id)
		self.attack_fuhuo_tick_id = 0
		
	def switch_camp(self):
		#切换阵营
		
		self.clear_judian()
		
		sec = cDateTime.Seconds() + EnumGameConfig.KFZC_VOTES_SEC
		
		#交换攻守方阵营id
		self.attack_camp_id, self.defense_camp_id = self.defense_camp_id, self.attack_camp_id
		
		#修改据点面板数据
		self.judian_data = [self.judian_type, self.defense_camp_id, cDateTime.Seconds(), sec, 0]
		
		#进入投票阶段
		self.votes_tick = cComplexServer.RegTick(EnumGameConfig.KFZC_VOTES_SEC, self.end_votes)
		
		self.sync_judian_data_no_tick()
		
		GCN = GlobalPrompt.KFZCReturnCampName
		GJN = GlobalPrompt.KFZCReturnJudianName
		
		self.kfzc_obj.scene.Msg(15, 0, GlobalPrompt.KFZC_TIPS_25 % (GCN(self.defense_camp_id), GCN(self.attack_camp_id), GJN(self.judian_type)))
		
	def check_belong(self, argv, param):
		#判断归属
		global IsStart
		if not IsStart: return
		
		if not self.left_camp_dict and not self.right_camp_dict:
			#两边都没有人
			return
		
		if not self.judian_data:
			return
		
		#投票时间戳
		sec = cDateTime.Seconds() + EnumGameConfig.KFZC_VOTES_SEC
		
		left_cnt = len(self.left_camp_dict)
		right_cnt = len(self.right_camp_dict)
		
		left_win = False
		if (left_cnt > right_cnt) or (left_cnt == right_cnt and self.left_zdl > self.right_zdl):
			#左阵营人多 或者 两方人数一致时左阵营总战斗力高
			left_win = True
		
		if left_win:
			self.attack_camp_id = 2
			self.defense_camp_id = 1
			self.judian_data = [self.judian_type, self.defense_camp_id, cDateTime.Seconds(), sec, 0]
		else:
			self.attack_camp_id = 1
			self.defense_camp_id = 2
			self.judian_data = [self.judian_type, self.defense_camp_id, cDateTime.Seconds(), sec, 0]
		
		#注册投票
		self.votes_tick = cComplexServer.RegTick(EnumGameConfig.KFZC_VOTES_SEC, self.end_votes)
		
		self.sync_judian_data_no_tick()
		
		GCN = GlobalPrompt.KFZCReturnCampName
		GJN = GlobalPrompt.KFZCReturnJudianName
		
		self.kfzc_obj.scene.Msg(15, 0, GlobalPrompt.KFZC_TIPS_26 % (GCN(self.defense_camp_id), GJN(self.judian_type)))
		
	def votes(self, role_id, role, votes_to_role_id):
		#投票
		if role_id in self.votes_role_set:
			return
		
		if cDateTime.Seconds() > self.judian_data[3]:
			#投票时间过了
			return
		
		global KFZC_ROLE_CAMP
		camp_id = KFZC_ROLE_CAMP.get(role_id)
		votes_camp_id = KFZC_ROLE_CAMP.get(votes_to_role_id)
		
		if camp_id != self.defense_camp_id or camp_id != votes_camp_id:
			#只有防守方能够投票
			return
		
		if camp_id not in self.camp_dict or votes_to_role_id not in self.camp_dict[camp_id]:
			return
		
		self.votes_role_set.add(role_id)
		
		self.camp_dict[camp_id][votes_to_role_id][VOTES] += 1
		
		self.sync_role_data(role_id, role)
		
	def end_votes(self, argv, param):
		#投票结束
		global IsStart
		if not IsStart: return
		
		camp_dict = self.camp_dict.get(self.defense_camp_id)
		if not camp_dict:
			return
		
		self.is_empty = False
		
		#按 票数 --> 战斗力 --> 积分 --> 等级 --> 角色id选出领主
		role_data = camp_dict.items()
		role_data.sort(key = lambda x : (x[1][VOTES], x[1][ZDL], x[1][SCORE], x[1][LEVEL], -x[0]), reverse=True)
		
		#领主
		self.boss_list = [role_data[0][0], role_data[0][1][NAME], 0]
		role_data[0][1][IS_BOSS] = 1
		
		#按 战斗力 --> 等级 --> 角色id选出守卫
		#从去掉领主的剩余中选出守卫
		role_data = role_data[1:]
		data = role_data[:5]
		
		#守卫
		self.guard_dict = {}
		for role_id, d in data:
			self.guard_dict[role_id] = d[NAME]
			d[IS_GUARD] = 1
		
		#每分钟检测占据, +占据时间
		self.guard_tick_id = cComplexServer.RegTick(60, self.guard_one_minute)
		
		self.sync_guard()
		
		self.back_camp_list = []
		
		last_role_data = role_data[5:]
		if not last_role_data:
			#没有人了
			return
		
		#构建后备队列
		for (role_id, data) in last_role_data:
			heapq.heappush(self.back_camp_list, (-data[ZDL], -data[LEVEL], -role_id, -data[GUARD_TIME], data[NAME]))
		
		self.sync_judian_data_no_tick()
		
	def check_judian(self, is_last=None):
		#检测占据
		if not self.judian_data:
			print 'GE_EXC, KuafuZhanchang check_judian empty judian_data'
			return
		
		camp_id = self.judian_data[1]
		if not camp_id:
			return
		
		#根据(据点类型, 时间)获取积分
		cfg = KuafuZhanchangConfig.KFZC_TIME_SCORE_DICT.get((self.judian_type, self.judian_data[4]))
		if not cfg:
			print 'GE_EXC, KuafuZhanchang  can not find judian type %s, guard time %s' % (self.judian_type, self.judian_data[4])
			return
		
		self.kfzc_obj.add_score(self.judian_data[1], cfg.score)
		
		#占据时间重新开始计算
		self.judian_data[4] = 0
		
		if self.guard_tick_id:
			#投票阶段后才会注册每分钟检测的tick, 如果有的话, 那么先取消tick, 再注册新的tick
			cComplexServer.UnregTick(self.guard_tick_id)
			if not is_last:
				self.guard_tick_id = cComplexServer.RegTick(60, self.guard_one_minute)
	
		self.sync_judian()
		
	def guard_one_minute(self, callargv, regparam):
		#成功守卫一分钟
		global IsStart
		if not IsStart: return
		
		if not self.judian_data:
			return
		
		self.judian_data[4] += 1
		
		if self.judian_data[4] == 10:
			cComplexServer.UnregTick(self.guard_tick_id)
			self.guard_tick_id = 0
		elif self.judian_data[4] > 10:
			print 'GE_EXC, kuafu zhanchang guard minutes %s' % self.judian_data[4]
			cComplexServer.UnregTick(self.guard_tick_id)
			self.guard_tick_id = 0
			return
		
		if self.judian_data[4] == 9:
			#第九次的时候少3s
			self.guard_tick_id = cComplexServer.RegTick(57, self.guard_one_minute, regparam)
		elif self.judian_data[4] < 9:
			self.guard_tick_id = cComplexServer.RegTick(60, self.guard_one_minute, regparam)
		
		self.sync_judian()
		
	def add_role_score(self, is_attack, role_id, other_role_id, record_name, is_win = False):
		#玩家积分
		role = cRoleMgr.FindRoleByRoleID(role_id)
		if not role or role.IsKick():
			return
		
		role_data = self.kfzc_obj.return_role_data(role_id)
		if not role_data:
			return
		other_role_data = self.kfzc_obj.return_role_data(other_role_id)
		if not other_role_data:
			return
		
		score = CalKillCntScore(role_data[KILL_CNT], other_role_data[KILL_CNT], is_win)
		role_data[SCORE] += score
		
		self.kfzc_obj.add_fight_record(role_id, role, (is_attack, is_win, record_name, score))
		
		if not is_win:
			#失败, 复活处理
			global KFZC_ROLE_CAMP
			camp_id = KFZC_ROLE_CAMP.get(role_id)
			
			if camp_id == self.attack_camp_id:
				self.add_attack_fuhuo(role_id)
				
			elif camp_id == self.defense_camp_id:
				if role_data[IS_BOSS]:
					#领主不加入复活
					sec = cDateTime.Seconds() + EnumGameConfig.KFZC_FUHUO_TIME
					role_data[IS_BOSS] = sec
					self.boss_list[2] = sec
				elif role_data[IS_GUARD]:
					role_data[IS_GUARD] = 0
					
					if role_id in self.guard_dict:
						del self.guard_dict[role_id]
					
					if self.back_camp_list:
					#如果有后备的话从后备中提一个玩家来成为守卫
						_, _, rid, _, name = heapq.heappop(self.back_camp_list)
						if -rid in self.camp_dict[self.defense_camp_id]:
							self.camp_dict[self.defense_camp_id][-rid][IS_GUARD] = 1
							self.guard_dict[-rid] = name
					self.add_defense_fuhuo(role_id)
				else:
					self.add_defense_fuhuo(role_id)
				
				self.sync_guard()
			
			#处理连杀
			role_data[KILL_CNT] = 0
			#cd
			role_data[GUARD_TIME] = cDateTime.Seconds() + EnumGameConfig.KFZC_FUHUO_TIME
			#更新战斗数据
			self.updata_fight_data(role_id, role, role_data)
		else:
			#更新血量
			global KFZC_ALL_ROLE_HP_DATA
			role_data[NOW_HP] = KFZC_ALL_ROLE_HP_DATA.get(role_id, {}).get("total_hp", 0)
			
			role_data[KILL_CNT] += 1
			
			tips = GlobalPrompt.KFZCReturnKillTips(role_data[KILL_CNT])
			if tips:
				self.kfzc_obj.scene.Msg(15, 0, tips % role.GetRoleName())
		
		self.sync_role_data(role_id, role)
	
	def updata_fight_data(self, role_id, role, role_data):
		#更新战斗数据和血量
		global KFZC_ALL_ROLE_FIGHT_DATA, KFZC_ALL_ROLE_HP_DATA
		KFZC_ALL_ROLE_FIGHT_DATA[role_id] = fight_data = Middle.GetRoleData(role, use_property_X=True)
		KFZC_ALL_ROLE_HP_DATA[role_id] = {}
		
		max_hp = CalMaxhp(fight_data)
		role_data[MAX_HP] = max_hp
		role_data[NOW_HP] = max_hp
		
	def click(self, left_role_id, left_role, right_role_id, right_role):
		#点击
		if not self.judian_data:
			return
		
		sec = cDateTime.Seconds()
		
		#归属阶段 or 投票阶段
		if sec < self.judian_data[2] or sec < self.judian_data[3]:
			return
		
		left_role_data, right_role_data = self.kfzc_obj.return_role_data(left_role_id), self.kfzc_obj.return_role_data(right_role_id)
		if not left_role_data or not right_role_data:
			return
		
		if left_role_data[CAMP_ID] == right_role_data[CAMP_ID]:
			return
		if left_role_data[JUDIAN_TYPE] != right_role_data[JUDIAN_TYPE]:
			return
		if sec < left_role_data[GUARD_TIME] or sec < right_role_data[GUARD_TIME]:
			#复活期间不能点人
			return
		
		if left_role_data[CAMP_ID] == self.attack_camp_id and (not right_role_data[IS_BOSS] and not right_role_data[IS_GUARD]):
			#点击者为攻击方, 只能攻击boss和守卫
			return
		
		if right_role_data[IS_BOSS] and len(self.guard_dict) > 1:
			#守卫没有了才能点击领主
			return
		
		#设置点击cd
		if left_role_data[CAMP_ID] == self.defense_camp_id:
			if left_role_data[IS_BOSS]:
				left_role.SetCD(EnumCD.KFZC_Fight_CD, EnumGameConfig.KFZC_FIGHT_BOSS_CD)
			elif left_role_data[IS_GUARD]:
				left_role.SetCD(EnumCD.KFZC_Fight_CD, EnumGameConfig.KFZC_FIGHT_GUARD_CD)
			else:
				left_role.SetCD(EnumCD.KFZC_Fight_CD, EnumGameConfig.KFZC_FIGHT_DEFENSE_CD)
		else:
			left_role.SetCD(EnumCD.KFZC_Fight_CD, EnumGameConfig.KFZC_FIGHT_ATTACK_CD)
		
		#进入战斗
		if not Status.CanInStatus(right_role, EnumInt1.ST_FightStatus):
			PVP_D(self, left_role_id, left_role, left_role_data, right_role_id, right_role, right_role_data, AfterPvpFight)
		else:
			PVP(self, left_role_id, left_role, left_role_data, right_role_id, right_role, right_role_data, AfterPvpFight)
		
	def click_random(self, left_role_id, left_role):
		#随机点击
		global KFZC_ROLE_CAMP
		camp_id = KFZC_ROLE_CAMP.get(left_role_id)
		if not camp_id:
			return
		
		left_role_data = self.kfzc_obj.return_role_data(left_role_id)
		if not left_role_data or cDateTime.Seconds() < left_role_data[GUARD_TIME]:
			#复活期间不能点人
			return
		
		if camp_id == self.attack_camp_id:
			#点击方是攻击方, 则只能点击守卫和boss
			can_attack_id_list = self.guard_dict.keys()
			
			if not can_attack_id_list and self.boss_list and cDateTime.Seconds() > self.boss_list[-1]:
				can_attack_id_list = [self.boss_list[0],]
		else:
			camp_dict = self.camp_dict.get(self.attack_camp_id)
			if not camp_dict:
				return
			
			#点击方是防守方, 随意选择
			can_attack_id_list = list(set(camp_dict.keys()) - set([role_id for (role_id, _) in self.attack_fuhuo_list]))
		
		if not can_attack_id_list:
			return
		
		right_role_id = random.choice(can_attack_id_list)
		
		right_role = cRoleMgr.FindRoleByRoleID(right_role_id)
		if not right_role:
			return
		
		right_role_data = self.kfzc_obj.return_role_data(right_role_id)
		if not right_role_data:
			return
		
		if left_role_data[CAMP_ID] == self.defense_camp_id:
			if left_role_data[IS_BOSS]:
				left_role.SetCD(EnumCD.KFZC_Fight_CD, EnumGameConfig.KFZC_FIGHT_BOSS_CD)
			elif left_role_data[IS_GUARD]:
				left_role.SetCD(EnumCD.KFZC_Fight_CD, EnumGameConfig.KFZC_FIGHT_GUARD_CD)
			else:
				left_role.SetCD(EnumCD.KFZC_Fight_CD, EnumGameConfig.KFZC_FIGHT_DEFENSE_CD)
		else:
			left_role.SetCD(EnumCD.KFZC_Fight_CD, EnumGameConfig.KFZC_FIGHT_ATTACK_CD)
		
		if not Status.CanInStatus(right_role, EnumInt1.ST_FightStatus):
			PVP_D(self, left_role_id, left_role, left_role_data, right_role_id, right_role, right_role_data, AfterPvpFight)
		else:
			PVP(self, left_role_id, left_role, left_role_data, right_role_id, right_role, right_role_data, AfterPvpFight)
		
	def add_attack_fuhuo(self, role_id):
		#加入攻击方复活列表
		if not self.attack_fuhuo_list:
			#复活列表中还没有玩家
			self.attack_fuhuo_tick_id = cComplexServer.RegTick(EnumGameConfig.KFZC_FUHUO_TIME, self.fuhuo_attack)
		self.attack_fuhuo_list.append((role_id, cDateTime.Seconds() + EnumGameConfig.KFZC_FUHUO_TIME))
		
	def add_defense_fuhuo(self, role_id):
		#加入防守方复活列表
		role_data = self.kfzc_obj.return_role_data(role_id)
		if not role_data:
			return
		
		if not self.defense_fuhuo_list:
			#复活列表中还没有玩家
			self.defense_fuhuo_tick_id = cComplexServer.RegTick(EnumGameConfig.KFZC_FUHUO_TIME, self.fuhuo_defense)
		self.defense_fuhuo_list.append((role_data[ZDL], role_data[LEVEL], role_id, cDateTime.Seconds() + EnumGameConfig.KFZC_FUHUO_TIME, role_data[NAME]))
		
	def fuhuo_attack(self, argv, param):
		#攻击方复活列表处理
		global IsStart
		if not IsStart: return
		
		self.attack_fuhuo_list.pop()
		
		sec = cDateTime.Seconds()
		
		pos = 0
		for (_, sc) in self.attack_fuhuo_list:
			if sc <= sec:
				pos += 1
			else:
				self.attack_fuhuo_tick_id = cComplexServer.RegTick(sc - sec, self.fuhuo_attack)
				break
		self.attack_fuhuo_list = self.attack_fuhuo_list[pos:]
	
	def fuhuo_defense(self, argv, param):
		#到复活列表中第一个玩家的复活时间了, 将该玩家插入到后备中
		global IsStart
		if not IsStart: return
		
		if not self.defense_fuhuo_list:
			return
		role_data = self.defense_fuhuo_list.pop()
		
		zdl, level, role_id, guard_time, name = role_data
		
		rdata = self.kfzc_obj.return_role_data(role_id)
		if rdata and rdata[JUDIAN_TYPE] == self.judian_type and role_id not in self.guard_dict:
			#需要该玩家还在据点中
			#这个时候如果守卫人数不足的话应该直接插入到守卫中
			if len(self.guard_dict) < self.guard_cnt:
				self.guard_dict[role_id] = name
				rdata[IS_GUARD] = 1
			else:
				heapq.heappush(self.back_camp_list, (-zdl, -level, -role_id, -guard_time, name))
		
		#判断余下的复活列表中玩家
		sec = cDateTime.Seconds()
		pos = 0
		
		for role_data in self.defense_fuhuo_list:
			zdl, level, role_id, guard_time, name = role_data
			
			rdata = self.kfzc_obj.return_role_data(role_id)
			if not rdata or rdata[JUDIAN_TYPE] != self.judian_type or role_id in self.guard_dict:
				pos += 1
				continue
			
			if guard_time <= sec:
				if len(self.guard_dict) < self.guard_cnt:
					self.guard_dict[role_id] = name
					rdata[IS_GUARD] = 1
				else:
					heapq.heappush(self.back_camp_list, (-zdl, -level, -role_id, -guard_time, name))
				pos += 1
			else:
				self.defense_fuhuo_tick_id = cComplexServer.RegTick(guard_time - sec, self.fuhuo_defense)
				break
		self.defense_fuhuo_list = self.defense_fuhuo_list[pos:]
		
		self.sync_guard()
		
	def sync_judian(self):
		#据点数据改变即时更新
		for role in self.roles:
			if not role or role.IsKick():
				continue
			role.SendObj(KFZC_JudianData, self.judian_data)
		
	def sync_guard(self):
		#守卫数据即时更新
		for role in self.roles:
			if not role or role.IsKick():
				continue
			role.SendObj(KFZC_GuardData, {1:self.boss_list, 2:self.guard_dict})
		
	def sync_role_data(self, role_id, role):
		#更新一个人
		role_data = self.kfzc_obj.return_role_data(role_id)
		if not role_data:
			return
		
		attack_data = self.left_camp_dict if self.attack_camp_id == 1 else self.right_camp_dict
		
		defense_data = self.right_camp_dict if self.attack_camp_id == 1 else self.left_camp_dict
		
		role.SendObj(KFZC_PersonalData, role_data)
		
		role.SendObj(KFZC_AttackData, attack_data)
		role.SendObj(KFZC_DefenseData, defense_data)
		role.SendObj(KFZC_GuardData, {1:self.boss_list, 2:self.guard_dict})
		role.SendObj(KFZC_JudianData, self.judian_data)
		role.SendObj(KFZC_JudianVotes, self.votes_role_set)
		
	def sync_judian_data_tick(self, argv, param):
		#同步据点数据
		global IsStart
		if not IsStart: return
		
		self.sync_judian_data_no_tick()
		
		self.sync_judian_tick = cComplexServer.RegTick(EnumGameConfig.KFZC_SYNC_SEC, self.sync_judian_data_tick)
		
	def sync_judian_data_no_tick(self):
		attack_data = self.left_camp_dict if self.attack_camp_id == 1 else self.right_camp_dict
		
		defense_data = self.right_camp_dict if self.attack_camp_id == 1 else self.left_camp_dict
		
		#进攻方
		for role in self.roles:
			if not role or role.IsKick():
				continue
			role.SendObj(KFZC_AttackData, attack_data)
			role.SendObj(KFZC_DefenseData, defense_data)
			role.SendObj(KFZC_GuardData, {1:self.boss_list, 2:self.guard_dict})
			role.SendObj(KFZC_JudianData, self.judian_data)
			role.SendObj(KFZC_JudianVotes, self.votes_role_set)
			
	def destroy_judian(self):
		#守卫tick
		cComplexServer.UnregTick(self.guard_tick_id)
		cComplexServer.UnregTick(self.defense_fuhuo_tick_id)
		cComplexServer.UnregTick(self.attack_fuhuo_tick_id)
		cComplexServer.UnregTick(self.belong_tick)
		cComplexServer.UnregTick(self.votes_tick)
#===============================================================================
# 辅助
#===============================================================================
def CalKillCntScore(own_cnt, other_cnt, is_win):
	#计算积分
	
	#战斗失败保底获得10积分
	#战斗胜利获得积分=2*连杀数+20
	#终结连杀额外获得积分=对方连杀数*7
	
	if is_win:
		return own_cnt * 2 + 20 + other_cnt * 7
	else:
		return 10

def PVP_D(judian, left_role_id, left_role, left_role_data, right_role_id, right_role, right_role_data, after_pvp_fight):
	#离线战斗
	fight = Fight.Fight(EnumGameConfig.KFZC_FIGHT_TYPE)
	
	left_camp, right_camp = fight.create_camp()
	
	global KFZC_ALL_ROLE_FIGHT_DATA, KFZC_ALL_ROLE_HP_DATA
	
	left_damage_upgrade_rate = 0
	left_deep_hurt = 0
	
	right_damage_upgrade_rate = 0
	right_deep_hurt = 0
	
	boss_cfg = KuafuZhanchangConfig.KFZC_BOSS_BUFF_DICT.get(judian.judian_type)
	if not boss_cfg:
		return
	
	guard_cfg = KuafuZhanchangConfig.KFZC_TIME_BUFF_DICT.get(judian.judian_data[-1])
	if not guard_cfg:
		return
	
	if left_role_data[IS_BOSS]:
		#领主
		left_damage_upgrade_rate = boss_cfg.damageupgrade / 100.0
		left_deep_hurt = boss_cfg.deephurt / 100.0
	elif left_role_data[IS_GUARD]:
		#守卫
		left_damage_upgrade_rate = guard_cfg.damageupgrade / 100.0
		left_deep_hurt = guard_cfg.deephurt / 100.0
	
	if right_role_data[IS_BOSS]:
		#领主
		right_damage_upgrade_rate = boss_cfg.damageupgrade / 100.0
		right_deep_hurt = boss_cfg.deephurt / 100.0
	elif right_role_data[IS_GUARD]:
		#守卫
		right_damage_upgrade_rate = guard_cfg.damageupgrade / 100.0
		right_deep_hurt = guard_cfg.deephurt / 100.0
	
	
	leftFightData = KFZC_ALL_ROLE_FIGHT_DATA.get(left_role_id)
	if not leftFightData:
		print 'GE_EXC, kuafu zhanchang can not find left role fight data'
		return
	rightFightData = KFZC_ALL_ROLE_FIGHT_DATA.get(right_role_id)
	if not rightFightData:
		print 'GE_EXC, kuafu zhanchang can not find left role fight data'
		return
	
	left_camp.bind_hp(KFZC_ALL_ROLE_HP_DATA.get(left_role_id, {}))
	left_camp.create_online_role_unit(left_role, fightData=leftFightData, use_px = True)
	for u in left_camp.pos_units.itervalues():
		u.damage_upgrade_rate += left_damage_upgrade_rate + right_deep_hurt
	
	#离线数据
	right_camp.bind_hp(KFZC_ALL_ROLE_HP_DATA.get(right_role_id, {}))
	right_camp.create_outline_role_unit(rightFightData)
	for u in right_camp.pos_units.itervalues():
		u.damage_upgrade_rate += right_damage_upgrade_rate + left_deep_hurt
		
	fight.after_fight_fun = after_pvp_fight
	fight.after_fight_param = judian, left_role_id, left_role.GetRoleName(), right_role_id, right_role.GetRoleName()
	fight.start()
	
def PVP(judian, left_role_id, left_role, left_role_data, right_role_id, right_role, right_role_data, after_pvp_fight):
	#在线战斗
	fight = Fight.Fight(EnumGameConfig.KFZC_FIGHT_TYPE)
	
	left_camp, right_camp = fight.create_camp()
	
	global KFZC_ALL_ROLE_FIGHT_DATA, KFZC_ALL_ROLE_HP_DATA
	
	left_damage_upgrade_rate = 0
	left_deep_hurt = 0
	
	right_damage_upgrade_rate = 0
	right_deep_hurt = 0
	
	boss_cfg = KuafuZhanchangConfig.KFZC_BOSS_BUFF_DICT.get(judian.judian_type)
	if not boss_cfg:
		print 'GE_EXC, kuafu zhanchang pvp can not find boss cfg by judian type %s' % judian.judian_type
		return
	
	guard_cfg = KuafuZhanchangConfig.KFZC_TIME_BUFF_DICT.get(judian.judian_data[-1])
	if not guard_cfg:
		print 'GE_EXC, kuafu zhanchang pvp can not find guard cfg by guard minutes %s' % judian.judian_data[-1]
		return
	
	if left_role_data[IS_BOSS]:
		#领主
		left_damage_upgrade_rate = boss_cfg.damageupgrade / 100.0
		left_deep_hurt = boss_cfg.deephurt / 100.0
	elif left_role_data[IS_GUARD]:
		#守卫
		left_damage_upgrade_rate = guard_cfg.damageupgrade / 100.0
		left_deep_hurt = guard_cfg.deephurt / 100.0
	
	if right_role_data[IS_BOSS]:
		#领主
		right_damage_upgrade_rate = boss_cfg.damageupgrade / 100.0
		right_deep_hurt = boss_cfg.deephurt / 100.0
	elif right_role_data[IS_GUARD]:
		#守卫
		right_damage_upgrade_rate = guard_cfg.damageupgrade / 100.0
		right_deep_hurt = guard_cfg.deephurt / 100.0
	
	#绑定血量
	leftFightData = KFZC_ALL_ROLE_FIGHT_DATA.get(left_role_id)
	if not leftFightData:
		print 'GE_EXC, kuafu zhanchang can not find left role fight data'
		return
	rightFightData = KFZC_ALL_ROLE_FIGHT_DATA.get(right_role_id)
	if not rightFightData:
		print 'GE_EXC, kuafu zhanchang can not find left role fight data'
		return
	
	left_camp.bind_hp(KFZC_ALL_ROLE_HP_DATA.get(left_role_id, {}))
	left_camp.create_online_role_unit(left_role, fightData=leftFightData, use_px = True)
	for u in left_camp.pos_units.itervalues():
		u.damage_upgrade_rate += left_damage_upgrade_rate + right_deep_hurt
	
	right_camp.bind_hp(KFZC_ALL_ROLE_HP_DATA.get(right_role_id, {}))
	right_camp.create_online_role_unit(right_role, fightData=rightFightData, use_px = True)
	for u in right_camp.pos_units.itervalues():
		u.damage_upgrade_rate += right_damage_upgrade_rate + left_deep_hurt
		
	fight.after_fight_fun = after_pvp_fight
	fight.after_fight_param = judian, left_role_id, left_role.GetRoleName(), right_role_id, right_role.GetRoleName()
	fight.start()
	
def AfterPvpFight(fightObj):
	if not fightObj.result:
		print 'GE_EXC, kuafu zhanchang not fight.result'
		return
	
	judian, left_role_id, left_role_name, right_role_id, right_role_name = fightObj.after_fight_param
	
	if fightObj.result == 1:
		#左阵营胜利
		judian.add_role_score(1, left_role_id, right_role_id, right_role_name, True)
		judian.add_role_score(2, right_role_id, left_role_id, left_role_name, False)
	else:
		#右阵营胜利
		judian.add_role_score(2, right_role_id, left_role_id, left_role_name, True)
		judian.add_role_score(1, left_role_id, right_role_id, right_role_name, False)
	
	#战斗检测据点占据情况
	judian.check_zhanju()
	
def CalMaxhp(fight_data):
	#计算血量
	role_data, heros_data = fight_data
	total_hp = role_data[20]
	for hero_value in heros_data.itervalues():
		total_hp += hero_value[20]
	return total_hp

#===============================================================================
# 时间控制
#===============================================================================
def CheckWeekDay():
	return cDateTime.WeekDay() in (0,2,4,6)

def CheckKaifuDay():
	#开服>10 & 二、四、六、七
	return WorldData.WD.returnDB and (WorldData.GetWorldKaiFuDay() > 10)

def BeginTips_1():
	return

	if not CheckKaifuDay() or not CheckWeekDay(): return
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.KFZC_TIPS_1)
	
def BeginTips_2():
	return

	if not CheckKaifuDay() or not CheckWeekDay(): return
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.KFZC_TIPS_2)

def BeginTips_3():
	return

	if Environment.IsCross:
		if not CheckWeekDay(): return
	else:
		#本服还要检测开服天数
		if not CheckKaifuDay() or not CheckWeekDay(): return
	
	global IsStart, CanIn
	if IsStart:
		print 'GE_EXC, KuafuZhanchang is already start'
	IsStart = True
	CanIn = True
	
	if not Environment.IsCross:
		cRoleMgr.Msg(1, 0, GlobalPrompt.KFZC_TIPS_3)

def BeginTips_4():
	return

	if not CheckKaifuDay() or not CheckWeekDay(): return
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.KFZC_TIPS_4)

def Begin():
	return
	
	if Environment.IsCross:
		if not CheckWeekDay(): return
		
		cComplexServer.RegTick(15, BeginEx)
	else:
		#本服还要检测开服天数
		if not CheckKaifuDay() or not CheckWeekDay(): return
		
		global CanIn, IsStart
		CanIn = False
		IsStart = False
		
		cRoleMgr.Msg(1, 0, GlobalPrompt.KFZC_TIPS_27)
		return
	
def BeginEx(argv, param):
	#分区
	region_1 = []
	region_2 = []
	region_3 = []
	
	global KFZC_ALL_ROLE, CanIn
	
	CanIn = False
	
	#打乱一下顺序
	all_role_data = KFZC_ALL_ROLE.items()
	random.shuffle(all_role_data)
	EKL = EnumGameConfig.KFZC_REGIONLEVEL_LIST
	for (role_id, role_data) in all_role_data:
		#在最后的时候按等级来区分战区
		level = role_data[1]
		
		if EKL[0] <= level < EKL[1]:
			#第一战区
			region_1.append((role_id, role_data))
			
		elif EKL[1] <= level < EKL[2]:
			#第二战区
			region_2.append((role_id, role_data))
			
		elif EKL[2] <= level:
			#第三战区
			region_3.append((role_id, role_data))
			
	#每张地图最大人数
	max_cnt = EnumGameConfig.KFZC_SCENE_CNT * EnumGameConfig.KFZC_ROLE_CNT
	
	AllocRegion(region_1, 1, max_cnt)
	AllocRegion(region_2, 2, max_cnt)
	AllocRegion(region_3, 3, max_cnt)
	
def AllocRegion(role_data, region_index, max_cnt):
	#分配每个等级段场景人数
	if not role_data:
		return
	
	roleCnt = len(role_data)
	begin_pos = 0
	EKG = EnumGameConfig.KFZC_SCENE_DICT.get
	KFZC_ROLE_CNT = EnumGameConfig.KFZC_ROLE_CNT
	KFZC_ROLECNTEX = EnumGameConfig.KFZC_ROLECNTEX
	KFZC_SCENE_CNT = EnumGameConfig.KFZC_SCENE_CNT
	
	if roleCnt > max_cnt:
		#人数超过了每张图60个人, 按地图张数平局分配人数
		
		#每张地图人数
		every_role_cnt = roleCnt / KFZC_SCENE_CNT
		#剩余人数
		shengyu_cnt = roleCnt - every_role_cnt * KFZC_SCENE_CNT
		
		for scene_id in EKG(region_index):
			if shengyu_cnt >= 2:
				#先每张地图多分两个人
				KFZC_SCENE_KFZC[scene_id] = KFZC(role_data[begin_pos:every_role_cnt+2], scene_id)
				
				begin_pos += every_role_cnt+2
				shengyu_cnt -= 2
				
			elif shengyu_cnt >= 1:
				#再每张地图多分一个人
				KFZC_SCENE_KFZC[scene_id] = KFZC(role_data[begin_pos:every_role_cnt+1], scene_id)
				
				begin_pos += every_role_cnt+1
				shengyu_cnt -= 1
				
			else:
				#不多分
				KFZC_SCENE_KFZC[scene_id] = KFZC(role_data[begin_pos:every_role_cnt], scene_id)
				
				begin_pos += every_role_cnt
	else:
		#人数不超过, 每张地图60人, 不足30的平均分配
		
		#战场个数
		if roleCnt < KFZC_ROLE_CNT:
			#最少也要分配一张地图
			zhanchangCnt = 1
			shengyuCnt = 0
			every_role_cnt = roleCnt
		else:
			#战场个数
			zhanchangCnt = roleCnt / KFZC_ROLE_CNT
			
			if roleCnt % KFZC_ROLE_CNT > KFZC_ROLECNTEX:
				#剩下的人数大于30,多分配一张地图
				every_role_cnt = KFZC_ROLE_CNT
				shengyuCnt = 0
				zhanchangCnt += 1
			else:
				#剩余的平均分配到战场中
				every_add = (roleCnt - zhanchangCnt * KFZC_ROLE_CNT) / zhanchangCnt
				#每个场景人数
				every_role_cnt = KFZC_ROLE_CNT + every_add
				#剩余
				shengyuCnt = roleCnt - every_role_cnt * zhanchangCnt
		
		for scene_id in EKG(region_index):
			
			if not zhanchangCnt:
				break
			zhanchangCnt -= 1
			
			if shengyuCnt >= 2:
				KFZC_SCENE_KFZC[scene_id] = KFZC(role_data[begin_pos:begin_pos+every_role_cnt+2], scene_id)
				
				begin_pos += every_role_cnt+2
				shengyuCnt -= 2
				
			elif shengyuCnt >= 1:
				KFZC_SCENE_KFZC[scene_id] = KFZC(role_data[begin_pos:begin_pos+KFZC_ROLE_CNT+1], scene_id)
				
				begin_pos += every_role_cnt+1
				shengyuCnt -= 1
				
			else:
				KFZC_SCENE_KFZC[scene_id] = KFZC(role_data[begin_pos:begin_pos+KFZC_ROLE_CNT], scene_id)
				
				begin_pos += every_role_cnt
	
def End():
	return

	#延迟了15s开启, 这里延迟20s结束
	cComplexServer.RegTick(20, EndEx)
	
def EndEx(argv, param):
	global IsStart
	if not IsStart:
		print 'GE_EXC, KuafuZhanchang is already end'
	IsStart = False
	
	global KFZC_ALL_ROLE, KFZC_ALL_ROLE_FIGHT_DATA, KFZC_ALL_ROLE_HP_DATA, KFZC_ROLE_CAMP, KFZC_NPC_JUDIAN, KFZC_SCENE_KFZC, KFZC_ROLE_JUDIAN
	
	for kfzc in KFZC_SCENE_KFZC.itervalues():
		kfzc.reward()
	
	#{role_id : [zdl、等级、名字]}
	KFZC_ALL_ROLE = {}
	#战斗数据 -- {role_id : fight_data}
	KFZC_ALL_ROLE_FIGHT_DATA = {}
	#血量 -- {role_id : hp_dict}
	KFZC_ALL_ROLE_HP_DATA = {}
	#{role_id : camp_id}
	KFZC_ROLE_CAMP = {}
	#{npc_id : judian_obj}
	KFZC_NPC_JUDIAN = {}
	#{role_id : judian_obj}
	KFZC_ROLE_JUDIAN = {}
	
	#一分钟后清理玩家
	cComplexServer.RegTick(60, ClearRole)
	
def ClearRole(argv, param):
	
	global KFZC_SCENE_KFZC
	for kfzc in KFZC_SCENE_KFZC.itervalues():
		kfzc.clear_role()
	KFZC_SCENE_KFZC = {}
	
	scene = cSceneMgr.SearchPublicScene(EnumGameConfig.KFZC_JUMP_SCENE)
	if scene:
		for role in scene.GetAllRole():
			role.GotoLocalServer(None, None)
#===============================================================================
# 请求
#===============================================================================
def RequestJoin(role, msg):
	'''
	请求进入跨服战场
	@param role:
	@param msg:
	'''
	global IsStart
	if not IsStart or not CanIn: return
	
	if role.GetLevel() < EnumGameConfig.KFZC_LEVEL:
		return
	
	x, y = RandomPos()
	role.GotoCrossServer(None, EnumGameConfig.KFZC_JUMP_SCENE, x, y, None, None)
	
def RequestClosePanel(role, msg):
	'''
	请求关闭据点面板
	@param role:
	@param msg:
	'''
	global IsStart
	if not IsStart: return
	
	global KFZC_ROLE_JUDIAN
	role_id = role.GetRoleID()
	
	judian = KFZC_ROLE_JUDIAN.get(role_id)
	if not judian:
		return
	judian.leave_watch_role(role_id, role)

def RequestLeave(role, msg):
	'''
	请求离开跨服战场
	@param role:
	@param msg:
	'''
	if role.GetSceneID() not in EnumGameConfig.KFZC_ALL_SCENE:
		return
	
	role.GotoLocalServer(None, None)
	
def RequestLeaveReady(role, msg):
	'''
	请求离开跨服战场准备间
	@param role:
	@param msg:
	'''
	if role.GetSceneID() != EnumGameConfig.KFZC_JUMP_SCENE:
		return
	
	role.GotoLocalServer(None, None)
	
def RequestVote(role, msg):
	'''
	请求跨服战场据点领主投票
	@param role:
	@param msg:
	'''
	global IsStart
	if not IsStart: return
	
	global KFZC_ROLE_JUDIAN
	role_id = role.GetRoleID()
	
	judian = KFZC_ROLE_JUDIAN.get(role_id)
	if not judian:
		return
	
	votes_to_role_id = msg
	if not votes_to_role_id:
		return
	
	judian.votes(role_id, role, votes_to_role_id)
	
def RequestJoinJudian(role, msg):
	'''
	请求进入跨服战场据点
	@param role:
	@param msg:
	'''
	global IsStart
	if not IsStart: return
	
	global KFZC_ROLE_JUDIAN
	role_id = role.GetRoleID()
	
	judian = KFZC_ROLE_JUDIAN.get(role.GetRoleID())
	if not judian:
		return
	judian.add_role(role_id, role)
	
def RequestLeaveJudian(role, msg):
	'''
	请求离开跨服战场据点
	@param role:
	@param msg:
	'''
	global IsStart
	if not IsStart: return
	
	global KFZC_ROLE_JUDIAN
	role_id = role.GetRoleID()
	
	judian = KFZC_ROLE_JUDIAN.get(role.GetRoleID())
	if not judian:
		return
	
	judian.leave_role(role_id, role)
	
def RequestAttack(role, msg):
	'''
	请求跨服战场攻击
	@param role:
	@param msg:
	'''
	global IsStart
	if not IsStart: return
	
	if role.GetCD(EnumCD.KFZC_Fight_CD):
		return
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	global KFZC_ROLE_JUDIAN
	role_id = role.GetRoleID()
	
	judian = KFZC_ROLE_JUDIAN.get(role.GetRoleID())
	if not judian:
		return
	
	fight_role_id = msg
	fight_role = cRoleMgr.FindRoleByRoleID(fight_role_id)
	if not fight_role:
		return
	
	judian.click(role_id, role, fight_role_id, fight_role)
	
def RequestAttackRandom(role, msg):
	'''
	请求跨服战场随机攻击
	@param role:
	@param msg:
	'''
	global IsStart
	if not IsStart: return
	
	if role.GetCD(EnumCD.KFZC_Fight_CD):
		return
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	global KFZC_ROLE_JUDIAN
	role_id = role.GetRoleID()
	
	judian = KFZC_ROLE_JUDIAN.get(role_id)
	if not judian:
		return
	
	judian.click_random(role_id, role)
	
def RequestTurntable(role, msg):
	'''
	请求跨服战场转盘
	@param role:
	@param msg:
	'''
	if role.GetLevel() < EnumGameConfig.KFZC_LEVEL:
		return
	if not role.GetDI8(EnumDayInt8.KFZC_TurnTableCnt):
		return
	
	global KFZC_TABLE_DICT
	roleId = role.GetRoleID()
	indexSet = KFZC_TABLE_DICT.setdefault(roleId, set())
	
	noIndex = True
	rd = Random.RandomRate()
	for index, cfg in KuafuZhanchangConfig.KFZC_TABLE_DICT.iteritems():
		if index in indexSet:
			continue
		noIndex = False
		rd.AddRandomItem(cfg.rate, index)
	
	if noIndex:
		return
	
	index = rd.RandomOne()
	indexSet.add(index)
	
	cfg = KuafuZhanchangConfig.KFZC_TABLE_DICT.get(index)
	if not cfg:
		print 'GE_EXC, KuafuZhanchang can not find table index %s' % index
		return
	
	with KFZC_TurnTable_Log:
		role.DecDI8(EnumDayInt8.KFZC_TurnTableCnt, 1)
	
	role.SendObjAndBack(KFZC_TableIndex, index, 10, CallBackFun, cfg)
	
def CallBackFun(role, callargv, regparam):
	cfg = regparam
	
	with KFZC_TurnTable_Log:
		tips = GlobalPrompt.Reward_Tips
		if cfg.items:
			role.AddItem(*cfg.items)
			tips += GlobalPrompt.Item_Tips % cfg.items
	
	role.Msg(2, 0, tips)
#===============================================================================
# 点击
#===============================================================================
def InitClick():
	NPCServerFun.RegNPCServerOnClickFunEx(EnumGameConfig.KFZC_BIG_JUDIAN_NPC[0], ClickJudian)
	NPCServerFun.RegNPCServerOnClickFunEx(EnumGameConfig.KFZC_SMALL_JUDIAN_NPC_1[0], ClickJudian)
	NPCServerFun.RegNPCServerOnClickFunEx(EnumGameConfig.KFZC_SMALL_JUDIAN_NPC_2[0], ClickJudian)
	
def ClickJudian(role, npc):
	global IsStart
	if not IsStart: return
	
	global KFZC_NPC_JUDIAN
	role_id = role.GetRoleID()
	judian_obj = KFZC_NPC_JUDIAN.get(npc.GetNPCID())
	
	if not judian_obj:
		return
	
	judian_obj.add_watch_role(role_id, role)
	
#===============================================================================
# 事件
#===============================================================================
def SyncRoleOtherData(role, param):
	if role.GetDI8(EnumDayInt8.KFZC_TurnTableCnt):
		global KFZC_TABLE_DICT
		role.SendObj(KFZC_TableReward, KFZC_TABLE_DICT.get(role.GetRoleID(), set()))
	
def AfterNewDay():
	global KFZC_TABLE_DICT
	KFZC_TABLE_DICT = {}
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.EnvIsTK() and not Environment.EnvIsESP() and not Environment.EnvIsRU():
		#跨服
		Cron.CronDriveByMinute((2038, 1, 1), Begin, H = "H == 19", M = "M == 0")
		
	if Environment.HasLogic and not Environment.EnvIsTK() and not Environment.EnvIsESP() and not Environment.EnvIsRU():
		#跨服&本服
		Cron.CronDriveByMinute((2038, 1, 1), BeginTips_3, H = "H == 18", M = "M == 55")
		
	if Environment.HasLogic and not Environment.IsCross and not Environment.EnvIsTK() and not Environment.EnvIsESP() and not Environment.EnvIsRU():
		#本服
		Cron.CronDriveByMinute((2038, 1, 1), BeginTips_1, H = "H == 18", M = "M == 30")
		Cron.CronDriveByMinute((2038, 1, 1), BeginTips_2, H = "H == 18", M = "M == 50")
		Cron.CronDriveByMinute((2038, 1, 1), BeginTips_4, H = "H == 18", M = "M == 58")
		#本服提前一分钟关闭入口
		Cron.CronDriveByMinute((2038, 1, 1), Begin, H = "H == 18", M = "M == 59")
		
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KuafuZhangchang_Join", "请求进入跨服战场"), RequestJoin)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KuafuZhangchang_Turntable", "请求跨服战场转盘"), RequestTurntable)
		
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
		
	if Environment.HasLogic and Environment.IsCross and not Environment.EnvIsTK() and not Environment.EnvIsESP() and not Environment.EnvIsRU():
		
		InitClick()
		
		Cron.CronDriveByMinute((2038, 1, 1), End, H = "H == 19", M = "M == 30")
		
		RegSceneAfterJoinWildBossFun()
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KuafuZhangchang_ClosePanel", "请求关闭据点面板"), RequestClosePanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KuafuZhangchang_Leave", "请求离开跨服战场"), RequestLeave)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KuafuZhangchang_LeaveReady", "请求离开跨服战场准备间"), RequestLeaveReady)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KuafuZhangchang_Vote", "请求跨服战场据点领主投票"), RequestVote)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KuafuZhangchang_JoinJudian", "请求进入跨服战场据点"), RequestJoinJudian)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KuafuZhangchang_LeaveJudian", "请求离开跨服战场据点"), RequestLeaveJudian)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KuafuZhangchang_Attack", "请求跨服战场攻击"), RequestAttack)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KuafuZhangchang_AttackRandom", "请求跨服战场随机攻击"), RequestAttackRandom)
