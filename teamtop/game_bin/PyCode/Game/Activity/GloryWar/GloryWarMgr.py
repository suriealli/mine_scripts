#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.GloryWar.GloryWarMgr")
#===============================================================================
# 荣耀之战
#===============================================================================
import Environment
import cComplexServer
import cDateTime
import cRoleMgr
import cSceneMgr
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumAward, EnumGameConfig,\
	EnumFightStatistics
from ComplexServer.Log import AutoLog
from ComplexServer.Time import Cron
from Game import GlobalMessage
from Game.Activity.Award import AwardMgr
from Game.Activity.GloryWar import GloryWarConfig
from Game.Activity.WonderfulAct import WonderfulActMgr, EnumWonderType
from Game.DailyDo import DailyDo
from Game.Fight import Middle, Fight
from Game.NPC import NPCServerFun
from Game.Role import Event, Status, Call
from Game.Role.Data import EnumDayInt8, EnumInt1, EnumCD, EnumDayInt1,\
	EnumTempObj
from Game.Role.Mail import Mail
from Game.Scene import PublicScene
from Game.SysData import WorldData
from Game.SystemRank import SystemRank
from Util import Time
from Game.Activity.RewardBuff import RewardBuff


if "_HasLoad" not in dir():
	GW_CanIn = False										#是否能进入荣耀之战场景标志
	GW_Begin_PVP = False									#是否开始荣耀之战pvp战斗标志
	GW_Begin_PVE = False									#是否开始荣耀之战pve战斗标志
	GW_Camp_1 = None										#荣耀之战阵营1
	GW_Camp_2 = None										#荣耀之战阵营2
	
	GW_Npc_List = []										#pve创建的npc信息[(npc_id, npc_type)]
	GW_Npc = []												#pve创建的npc对象
	GW_ZDL_Rank = {}										#排行榜前20名
	GW_Camp_Rank_1 = [1, 4, 5, 8, 9, 12, 13, 16, 17, 20]	#战斗力榜第一阵营
	GloryWar_Camp_Pos_1 = (10, 347, 1560)					#阵营1进入位置
	GloryWar_Camp_Pos_2 = (10, 2392, 561)					#阵营2进入位置
	GloryWar_Camp_Npc_Pos_1 = (1099, 906, 1)				#阵营1npc位置
	GloryWar_Camp_Npc_Pos_2 = (1784, 821, 1)				#阵营2npc位置
	
	#消息
	GW_FastFightPvpData = AutoMessage.AllotMessage("GW_FastFightPvpData", "荣耀之战Pvp快速战斗数据")
	GW_FastFightPvpOwnData = AutoMessage.AllotMessage("GW_FastFightPvpOwnData", "荣耀之战Pvp自己的数据")
	GW_FastFightPveData = AutoMessage.AllotMessage("GW_FastFightPveData", "荣耀之战Pve快速战斗数据")
	GW_ScoreRankData = AutoMessage.AllotMessage("GW_ScoreRankData", "荣耀之战积分排行榜数据")
	GW_RoleScore = AutoMessage.AllotMessage("GW_RoleScore", "荣耀之战个人积分")
	GW_CampScore = AutoMessage.AllotMessage("GW_CampScore", "荣耀之战阵营积分")
	GW_KillRecord = AutoMessage.AllotMessage("GW_KillRecord", "荣耀之战击杀记录")
	
	#日志
	GW_KillNpcReward = AutoLog.AutoTransaction("GW_KillNpcReward", "荣耀之战击杀npc奖励")
	GW_JoinCampID_Log = AutoLog.AutoTransaction("GW_JoinCampID_Log", "荣耀之战进入分配阵营ID")
	GW_EndReward_Log = AutoLog.AutoTransaction("GW_EndReward_Log", "荣耀之战结束时发奖日志")
	
class GloryWarRole():
	def __init__(self, role, role_id, role_name, union_name, camp_obj, other_camp_obj):
		self.role = role
		self.role_id = role_id
		self.role_name = role_name
		self.camp_obj = camp_obj				#自己的阵营对象
		self.camp_id = camp_obj.camp_id
		self.other_camp_obj = other_camp_obj	#对面的阵营对象
		
		#积分
		self.score_tick = 0
		self.union_name = union_name
		#缓存数据
		self.score = 0
		
		#pvp
		self.pvp_tick = 0
		#缓存数据
		self.zdl_score = 0
		self.kill_cnt = 0
		self.be_kill_cnt = 0
		self.bind_hp = {}
		self.kill_record = []
		self.fight_data = Middle.GetRoleData(role, use_property_X = True)
		self.max_hp = self.now_hp = self.return_total_hp(is_max = True)
		self.hp = [self.max_hp, self.now_hp]
		
		#pve
		self.pve_tick = 0
		#缓存数据
		self.pve_npc = []
		self.now_npc_index =  1
		self.is_vote = False
		self.vote_number = 0
		
		self.init_zdl_score()
		
	def unreg_score_tick(self):
		if not self.score_tick:
			return
		self.role.UnregTick(self.score_tick)
		self.score_tick = 0
		
	def add_score(self, score):
		self.score += score
		
	def return_total_hp(self, is_max = False):
		if is_max:
			role_data, heros_data = self.fight_data
			total_hp = role_data[20]
			for hero_value in heros_data.itervalues():
				total_hp += hero_value[20]
			self.now_hp = total_hp
			return total_hp
		else:
			self.now_hp = self.bind_hp["total_hp"]
			return self.bind_hp["total_hp"]
		
	def init_zdl_score(self):
		zdl = GetCloseValue(self.role.GetZDL(), GloryWarConfig.GW_ZdlToScore_Key_List)
		self.zdl_score= GloryWarConfig.GW_ZdlToScore_Dict.get(zdl, 0)
		if not self.zdl_score:
			print 'GE_EXC, GloryWar init_zdl_score error'
			return
		
	def updata_fight_data(self):
		self.bind_hp = {}
		self.fight_data = Middle.GetRoleData(self.role, use_property_X = True)
		self.max_hp = self.now_hp = self.return_total_hp(is_max = True)
		self.hp = [self.max_hp, self.now_hp]
		return self.max_hp
	
	def unreg_pvp_tick(self):
		if not self.pvp_tick:
			return
		self.role.UnregTick(self.pvp_tick)
		self.pvp_tick = 0
		
	def add_kill_record(self, param):
		if len(self.kill_record) >= 4:
			self.kill_record.pop(0)
		self.kill_record.append(param)
	
	def build_npc_msg(self, npc_id, npc_type):
		if self.pve_npc:
			return
		self.pve_npc = [npc_id, npc_type]
	
	def unreg_pve_tick(self):
		if not self.pve_tick:
			return
		self.role.UnregTick(self.pve_tick)
		self.pve_tick = 0
	
class ScoreRank():
	def __init__(self, scene):
		self.score_datas = {}							#同步的数据
		self.camp_score = [0, 0]						#阵营总积分
		self.camp_npc = {}								#阵营npc{camp_id-->[npc_id, npc_type]}
		self.min_score = []								#最小值
		self.scene = scene
		
		#缓存
		self.role_score = {}							#{role_id --> score}
		self.role_msg = {}								#{role_id --> [unionId, level]}
		
	def in_score_rank(self, gloryWarRole):
		score, role_id = gloryWarRole.score, gloryWarRole.role_id
		
		#尝试构建最小分值
		if not self.min_score:
			self.min_score = [role_id, score]
		if role_id in self.score_datas:
			#在积分榜内, 更新分数
			self.score_datas[role_id][3] = score
			if role_id == self.min_score[0]:
				#是最小值的话更新分数
				self.min_score[1] = score
			else:
				return
		elif len(self.score_datas) < 10:
			#不在积分榜内, 积分榜内玩家个数小于10个
			self.score_datas[role_id] = [gloryWarRole.role_name, gloryWarRole.union_name, gloryWarRole.camp_id, score]
			#分数大于最小分数
			if score > self.min_score[1]:
				return
		elif score > self.min_score[1]:
			#不在积分榜内, 积分榜内玩家个数大于10个, 积分大于最小值
			del self.score_datas[self.min_score[0]]
			self.score_datas[role_id] = [gloryWarRole.role_name, gloryWarRole.union_name, gloryWarRole.camp_id, score]
			#因为可能该score是最小值了, 下面的逻辑没有更新self.min_score, 下次删除最小值时就会有一个key error
			#所以在这里先对self.min_score进行一次赋值, 如果下面逻辑没有找到最小值, 下次删除也不会有问题
			self.min_score = [role_id, score]
		elif score <= self.min_score[1]:
			#不在积分榜内, 且积分小于最小值
			return
		#构建最小值
		for roleID, value in self.score_datas.iteritems():
			if value[3] < score:
				score = value[3]
				self.min_score = [roleID, score]
		
	def add_score_role(self, gloryWarRole):
		role_id, role = gloryWarRole.role_id, gloryWarRole.role
		
		if role_id not in self.role_score:
			#第一次进入初始化{role_id-->积分}
			self.role_score[role_id] = gloryWarRole.score
		elif not gloryWarRole.score:
			#使用缓存数据更新
			gloryWarRole.score = self.role_score[role_id]
		
		if role_id not in self.role_msg:
			#初始化角色第一次进来时的信息{role_id-->公会ID, 角色等级}
			self.role_msg[role_id] = [role.GetUnionID(), role.GetLevel()]
		
		#尝试进入排行榜
		self.in_score_rank(gloryWarRole)
		
		#同步客户端
		if gloryWarRole.score_tick:
			gloryWarRole.unreg_score_tick()
			print 'GE_EXC, GloryWar score tick is alread exist'
		self.score_sync(role, param = gloryWarRole)
		
		if not self.camp_npc: return
		
		#同步npc信息
		if gloryWarRole.camp_id == 1:
			role.SendObj(GlobalMessage.Npc_TypeChange, self.camp_npc[2])
		else:
			role.SendObj(GlobalMessage.Npc_TypeChange, self.camp_npc[1])
		
	def del_score_role(self, gloryWarRole):
		#取消其tick
		gloryWarRole.unreg_score_tick()
		
		#更新一下缓存数据
		self.role_score[gloryWarRole.role_id] = gloryWarRole.score
		
	def add_score(self, gloryWarRole, score):
		#加个人积分
		gloryWarRole.add_score(score)
		#加阵营积分
		self.camp_score[gloryWarRole.camp_id - 1] += score
		#尝试进入排行榜
		self.in_score_rank(gloryWarRole)
		#同步一次排行榜
		self.score_sync_untick(gloryWarRole)
		
	def build_camp_npc(self, camp_id, npc_id, npc_type):
		#构建阵营npc
		self.camp_npc[camp_id] = [npc_id, npc_type]
		
	def updata_camp_npc(self, camp, camp_id, npc_type):
		#更新阵营npc索引
		self.camp_npc[camp_id][1] = npc_type
		#广播给对面阵营
		camp.broad_msg(self.camp_npc[camp_id])
		
	def score_sync_untick(self, gloryWarRole):
		role = gloryWarRole.role
		#取消tick
		gloryWarRole.unreg_score_tick()
		#注册一个新的tick
		gloryWarRole.score_tick = role.RegTick(20, self.score_sync, gloryWarRole)
		#同步积分榜数据
		role.SendObj(GW_ScoreRankData, self.score_datas)
		#同步个人积分
		role.SendObj(GW_RoleScore, gloryWarRole.score)
		#同步阵营积分
		role.SendObj(GW_CampScore, self.camp_score)
		
	def score_sync(self, role, argv = None, param = None):
		#param = gloryWarRole
		#注册下次同步的tick
		global GW_CanIn
		if not GW_CanIn: return
		
		param.score_tick = role.RegTick(20, self.score_sync, param)
		#同步积分榜数据
		role.SendObj(GW_ScoreRankData, self.score_datas)
		#个人积分
		role.SendObj(GW_RoleScore, param.score)
		#阵营积分
		role.SendObj(GW_CampScore, self.camp_score)
	
	def destroy(self):
		#取消所有同步积分榜的tick并将所有进入过的玩家的gloryWarRole临时对象清理掉
		ETGWR = EnumTempObj.GloryWarRole
		for role_id in self.role_score:
			role = cRoleMgr.FindRoleByRoleID(role_id)
			if not role:
				continue
			gloryWarRole = role.GetTempObj(ETGWR)
			if not gloryWarRole:
				continue
			#更新一下分数
			self.role_score[role_id] = gloryWarRole.score
			if gloryWarRole.role:
				gloryWarRole.unreg_score_tick()
			role.SetTempObj(ETGWR, None)
		
class FastFightPvp():
	def __init__(self, scene):
		self.scene = scene
		self.pvp_datas = {}							#同步数据
		
		#缓存
		self.be_kill_cnt = {}						#被杀次数
		self.kill_record = {}						#击杀记录
		
	def build_pvp_role(self, gloryWarRole):
		#构建pvp战斗所需的数据
		role_id, role_name = gloryWarRole.role_id, gloryWarRole.role_name
		
		if not gloryWarRole.be_kill_cnt and role_id in self.be_kill_cnt:
			#使用缓存更新被连杀数
			gloryWarRole.be_kill_cnt = self.be_kill_cnt[role_id]
		if not gloryWarRole.kill_record and role_id in self.kill_record:
			#使用缓存更新击杀记录
			gloryWarRole.kill_record = self.kill_record[role_id]
		
		#设置显示标志
		if role_id in self.pvp_datas:
			self.pvp_datas[role_id][0] = 1
			return
		
		#是否显示标志, 玩家名字, 连杀次数, 基础分数, 当前血量, 最大血量
		max_hp = gloryWarRole.max_hp
		self.pvp_datas[role_id] = [1, role_name, 0, gloryWarRole.zdl_score, max_hp, max_hp]
		
	def updata_hp(self, gloryWarRole):
		#更新血量
		self.pvp_datas[gloryWarRole.role_id][4] = gloryWarRole.return_total_hp()
		
	def updata_fight_data(self, gloryWarRole):
		#更新战斗数据及血量
		max_hp = gloryWarRole.updata_fight_data()
		
		self.pvp_datas[gloryWarRole.role_id][4] = max_hp
		self.pvp_datas[gloryWarRole.role_id][5] = max_hp
		
	def add_pvp_role(self, gloryWarRole):
		self.build_pvp_role(gloryWarRole)
		
		#活动未开始, 不发送数据
		global GW_Begin_PVP
		if not GW_Begin_PVP: return
		
		if gloryWarRole.pvp_tick:
			gloryWarRole.unreg_pvp_tick()
			print 'GE_EXC, GloryWar pvp tick is already exist'
		self.pvp_sync(gloryWarRole.role, param = gloryWarRole)
		
	def del_pvp_role(self, gloryWarRole):
		#设置不显示标志
		self.pvp_datas[gloryWarRole.role_id][0] = 0
		
		global GW_Begin_PVP
		if not GW_Begin_PVP: return
		
		#取消pvptick
		gloryWarRole.unreg_pvp_tick()
		#离开时更新一下缓存数据
		role_id = gloryWarRole.role_id
		self.be_kill_cnt[role_id] = gloryWarRole.be_kill_cnt
		self.kill_record[role_id] = gloryWarRole.kill_record
		
	def begin_send(self):
		#活动开始, 开始发送数据
		ETGWR = EnumTempObj.GloryWarRole
		for role in self.scene.GetAllRole():
			gloryWarRole = role.GetTempObj(ETGWR)
			if not gloryWarRole or not gloryWarRole.role:
				continue
			self.pvp_sync(role, param = gloryWarRole)
		
	def open_panel(self, gloryWarRole):
		global GW_Begin_PVP
		if not GW_Begin_PVP: return
		
		self.pvp_sync_untick(gloryWarRole)
		
	def add_kill(self, gloryWarRole, is_initor, name, score, npc_type = None):
		#获得胜利CD
		gloryWarRole.role.SetCD(EnumCD.GloryWarFightCD, EnumGameConfig.GloryWar_PvpFightWinCD)
		#加连杀数
		self.pvp_datas[gloryWarRole.role_id][2] += 1
		gloryWarRole.kill_cnt += 1
		#取消被连杀
		gloryWarRole.be_kill_cnt = 0
		#更新血量
		self.updata_hp(gloryWarRole)
		#更新击杀记录
		gloryWarRole.add_kill_record([is_initor, 1, name, score])
		#同步
		self.pvp_sync_untick(gloryWarRole)
		#是否传闻
		self.is_kill_rumor(gloryWarRole.kill_cnt, gloryWarRole.role_name)
	
	def be_kill(self, gloryWarRole, is_initor, kill_name, score):
		#获得失败CD
		gloryWarRole.role.SetCD(EnumCD.GloryWarFightCD, EnumGameConfig.GloryWar_PvpFightFailCD)
		#获得被点击cd
		gloryWarRole.role.SetCD(EnumCD.GloryWarClickFailCD, EnumGameConfig.GloryWar_PvpFightClickFailCD)
		
		#是否取消连杀传闻
		self.is_be_kill_rumor(gloryWarRole.kill_cnt, kill_name, gloryWarRole.role_name)
		#取消连杀
		self.pvp_datas[gloryWarRole.role_id][2] = 0
		gloryWarRole.kill_cnt = 0
		#加被连杀
		gloryWarRole.be_kill_cnt += 1
		#更新战斗数据
		self.updata_fight_data(gloryWarRole)
		#更新击杀记录
		gloryWarRole.add_kill_record([is_initor, 0, kill_name, score])
		#同步
		self.pvp_sync_untick(gloryWarRole)
	
	def is_kill_rumor(self, kill_cnt, role_name):
		#是否连杀传闻
		if kill_cnt < 8:
			return
		elif kill_cnt == 8:
			#各版本判断
			if Environment.EnvIsNA():
				cRoleMgr.Msg(11, 0, GlobalPrompt.GloryWar_EightKill % (role_name, kill_cnt))
			else:
				cRoleMgr.Msg(1, 0, GlobalPrompt.GloryWar_EightKill % (role_name, kill_cnt))
		elif kill_cnt == 15:
			#各版本判断
			if Environment.EnvIsNA():
				cRoleMgr.Msg(11, 0, GlobalPrompt.GloryWar_FifteenKill % role_name)
			else:
				cRoleMgr.Msg(1, 0, GlobalPrompt.GloryWar_FifteenKill % role_name)
		elif kill_cnt % 5 == 0 and kill_cnt != 10:
			#各版本判断
			if Environment.EnvIsNA():
				cRoleMgr.Msg(11, 0, GlobalPrompt.GloryWar_TwentyKill % (role_name, kill_cnt))
			else:
				cRoleMgr.Msg(1, 0, GlobalPrompt.GloryWar_TwentyKill % (role_name, kill_cnt))
		
	def is_be_kill_rumor(self, be_kill_cnt, role_name, kill_role_name):
		#是否取消连杀传闻
		if be_kill_cnt < 8:
			return
		#各版本判断
		if Environment.EnvIsNA():
			cRoleMgr.Msg(11, 0, GlobalPrompt.GloryWar_EndKill % (role_name, kill_role_name, be_kill_cnt))
		else:
			cRoleMgr.Msg(1, 0, GlobalPrompt.GloryWar_EndKill % (role_name, kill_role_name, be_kill_cnt))
		
	def pvp_sync(self, role, argv = None, param = None):
		#param = gloryWarRole
		#注册下次同步tick
		global GW_Begin_PVP
		if not GW_Begin_PVP: return
		
		param.pvp_tick = role.RegTick(10, self.pvp_sync, param)
		#同步
		role.SendObj(GW_FastFightPvpData, param.other_camp_obj.fast_fight.pvp_datas)
		#连杀, 当前血量, 最大血量
		role.SendObj(GW_FastFightPvpOwnData, (param.kill_cnt, param.now_hp, param.max_hp))
		role.SendObj(GW_KillRecord, param.kill_record)
		
	def pvp_sync_untick(self, gloryWarRole):
		role = gloryWarRole.role
		#先取消tick
		gloryWarRole.unreg_pvp_tick()
		#注册下次同步tick
		gloryWarRole.pvp_tick = role.RegTick(10, self.pvp_sync, gloryWarRole)
		#同步
		role.SendObj(GW_FastFightPvpData, gloryWarRole.other_camp_obj.fast_fight.pvp_datas)
		#连杀, 当前血量, 最大血量
		role.SendObj(GW_FastFightPvpOwnData, (gloryWarRole.kill_cnt, gloryWarRole.now_hp, gloryWarRole.max_hp))
		role.SendObj(GW_KillRecord, gloryWarRole.kill_record)
		
	def destroy(self):
		#取消所有tick
		ETGWR = EnumTempObj.GloryWarRole
		for role in self.scene.GetAllRole():
			gloryWarRole = role.GetTempObj(ETGWR)
			if not gloryWarRole or not gloryWarRole.role:
				continue
			gloryWarRole.unreg_pvp_tick()
		
class FastFightPve():
	def __init__(self, scene):
		self.scene = scene
		self.pve_datas = {}									#同步数据
		self.buff_set = set()								#buff集合
		
		#缓存
		self.roles_npc = {}									#role_id-->[npc_id, npc_type]
		self.now_npc_index = {}								#{role_id --> now_npc_index}
		self.vote_roles = set()								#投票玩家集合
		
	def build_pve_role(self, gloryWarRole, npc_id, npc_type, kill_cnt, ex):
		#构建pve数据
		role, role_id = gloryWarRole.role, gloryWarRole.role_id
		
		if role_id in self.now_npc_index:
			#使用缓存数据更新当前击杀的npc索引
			gloryWarRole.now_npc_index = self.now_npc_index[role_id]
		if not gloryWarRole.is_vote and role_id in self.vote_roles:
			#使用缓存数据更新更新当前是否投票
			gloryWarRole.is_vote = True
		gloryWarRole.build_npc_msg(npc_id, npc_type)
		
		if role_id in self.pve_datas:
			self.pve_datas[role_id][0] = 1
			return
		
		#是否显式, 玩家名字, 票数, 当前npc索引, buff集合, 连杀数, 是否投票, 战斗力, npc类型
		self.pve_datas[role_id] = [ex, gloryWarRole.role_name, 0, 1, self.buff_set, gloryWarRole.kill_cnt, 0, role.GetZDL(), npc_type]
		
	def add_pve_role(self, gloryWarRole, npc_id, npc_type, kill_cnt, ex = 1):
		self.build_pve_role(gloryWarRole, npc_id, npc_type, kill_cnt, ex)
		
		if gloryWarRole.pve_tick:
			gloryWarRole.unreg_pve_tick()
			print 'GE_EXC, GloryWar pve tick is already exist'
		self.pve_sync(gloryWarRole.role, param = gloryWarRole)
		#同步npc外形
		gloryWarRole.role.SendObj(GlobalMessage.Npc_TypeChange, gloryWarRole.pve_npc)
		
	def del_pve_role(self, gloryWarRole):
		#设置不显示标志
		self.pve_datas[gloryWarRole.role_id][0] = 0
		
		#取消tick
		gloryWarRole.unreg_pve_tick()
		#离开的时候更新一下缓存数据
		role_id = gloryWarRole.role_id
		self.roles_npc[role_id] = gloryWarRole.pve_npc
		self.now_npc_index[role_id] = gloryWarRole.now_npc_index
		
	def open_panel(self, gloryWarRole):
		global GW_Begin_PVE
		if not GW_Begin_PVE: return
		
		self.pve_sync_untick(gloryWarRole)
		
	def add_ticket(self, voteRole, beVoteRole):
		#投票
		vote_role_id = voteRole.role_id
		self.vote_roles.add(vote_role_id)
		voteRole.is_vote = True
		self.pve_datas[vote_role_id][6] = 1
		#被投票
		beVoteRole.vote_number += 1
		self.pve_datas[beVoteRole.role_id][2] += 1
		#同步投票者面板数据
		self.pve_sync_untick(voteRole)
		
	def add_kill(self, gloryWarRole, is_initor, name, score, npc_type = None):
		now_npc_index = gloryWarRole.now_npc_index
		
		#进度已经到最后一个npc了
		if now_npc_index > 6:
			return
		
		#加入buff集合
		self.buff_set.add(now_npc_index)
		if now_npc_index < 6:
			#不是最后一个
			role_id = gloryWarRole.role_id
			##########下面一行移到外面就可以让客户端知道通关了#########
			self.pve_datas[role_id][3] += 1
			self.pve_datas[role_id][8] = npc_type
			#改变外形
			gloryWarRole.pve_npc[1] = npc_type
			gloryWarRole.role.SendObj(GlobalMessage.Npc_TypeChange, gloryWarRole.pve_npc)
		gloryWarRole.now_npc_index += 1
		#同步面板数据
		self.pve_sync_untick(gloryWarRole)
		
	def is_max_index(self, npc_index):
		#检测是否是最大npc索引
		if npc_index not in self.buff_set:
			return True
		return False
		
	def pve_sync(self, role, argv = None, param = None):
		#param = gloryWarRole
		#注册下次同步tick
		global GW_Begin_PVE
		if not GW_Begin_PVE: return
		
		param.pve_tick = role.RegTick(10, self.pve_sync, param)
		#同步pve数据
		role.SendObj(GW_FastFightPveData, self.pve_datas)
		
	def pve_sync_untick(self, gloryWarRole):
		role = gloryWarRole.role
		#先取消tick
		gloryWarRole.unreg_pve_tick()
		#注册下次同步tick
		gloryWarRole.pve_tick = role.RegTick(10, self.pve_sync, gloryWarRole)
		#同步pve数据
		role.SendObj(GW_FastFightPveData, self.pve_datas)
		
	def destroy(self):
		#取消所有tick
		ETGWR = EnumTempObj.GloryWarRole
		for role in self.scene.GetAllRole():
			gloryWarRole = role.GetTempObj(ETGWR)
			if not gloryWarRole or not gloryWarRole.role:
				continue
			gloryWarRole.unreg_pve_tick()
		
class GloryWarCamp():
	def __init__(self, camp_id, score_rank, fast_fight):
		self.camp_id = camp_id									#阵营ID
		self.score_rank = score_rank							#积分榜
		self.fast_fight = fast_fight							#快速战斗面板
		self.broad_role = set()									#需要广播的角色集合
		self.total_role_cnt = 0									#阵营人数
		
	def add_camp_role(self, gloryWarRole, npc_id = 0, npc_type = 0, kill_cnt = 0, ex = 1):
		self.score_rank.add_score_role(gloryWarRole)
		
		self.broad_role.add(gloryWarRole.role)
		
		global GW_Begin_PVE
		if GW_Begin_PVE:
			global GW_Npc_List
			self.fast_fight.add_pve_role(gloryWarRole, GW_Npc_List[self.camp_id - 1][0], GW_Npc_List[self.camp_id - 1][1], kill_cnt = 0, ex = 1)
		else:
			self.fast_fight.add_pvp_role(gloryWarRole)
		
		self.total_role_cnt += 1
		
	def del_camp_role(self, gloryWarRole):
		self.score_rank.del_score_role(gloryWarRole)
		
		global GW_Begin_PVE
		if GW_Begin_PVE:
			self.fast_fight.del_pve_role(gloryWarRole)
		else:
			self.fast_fight.del_pvp_role(gloryWarRole)
		
		self.broad_role.discard(gloryWarRole.role)
		
		self.total_role_cnt -= 1
		
	def add_score(self, gloryWarRole, is_initor, is_win, name, score, npc_type = None):
		#加分
		self.score_rank.add_score(gloryWarRole, score)
		
		if is_win:
			self.fast_fight.add_kill(gloryWarRole, is_initor, name, score, npc_type)
		else:
			self.fast_fight.be_kill(gloryWarRole, is_initor, name, score)
	
	def broad_msg(self, msg):
		#向对面阵营广播己方npc进度
		for role in self.broad_role:
			role.SendObj(GlobalMessage.Npc_TypeChange, msg)
		
def CreateGloryWarRole(role, campId, otherCampId):
	gloryWarRole = GloryWarRole(role, role.GetRoleID(), role.GetRoleName(), ReturnUnionName(role), ReturnCampObj(campId), ReturnCampObj(otherCampId))
	role.SetTempObj(EnumTempObj.GloryWarRole, gloryWarRole)
	return gloryWarRole
	
def ReturnRevivePos(campId):
	if campId == 1:
		global GloryWar_Camp_Pos_1
		return GloryWar_Camp_Pos_1
	else:
		global GloryWar_Camp_Pos_2
		return GloryWar_Camp_Pos_2
	
def ReturnCampObj(campId):
	if campId == 1:
		global GW_Camp_1
		return GW_Camp_1
	else:
		global GW_Camp_2
		return GW_Camp_2
	
def ReturnUnionName(role):
	unionObj = role.GetUnionObj()
	if not unionObj:
		return None
	else:
		return unionObj.name

def AllocCamp(role):
	global GW_Camp_1
	global GW_Camp_2
	global GW_Camp_Rank_1
	global GW_ZDL_Rank
	
	with GW_JoinCampID_Log:
		#分配战斗力榜前20名的阵营
		roleId = role.GetRoleID()
		for rank_index, value in GW_ZDL_Rank.iteritems():
			if roleId not in value:
				continue
			if rank_index in GW_Camp_Rank_1:
				return 1
			else:
				return 2
		#分配战斗力榜后20名的阵营
		if GW_Camp_1.total_role_cnt < GW_Camp_2.total_role_cnt:
			return 1
		else:
			return 2
	
def InitClickFun():
	#初始化npc的点击函数
	for npc_type in GloryWarConfig.GW_NPC_Set:
		NPCServerFun.RegNPCServerOnClickFunEx(npc_type, ClickNpc)
	
def ClickNpc(role, npc):
	gloryWarRole = role.GetTempObj(EnumTempObj.GloryWarRole)
	if not gloryWarRole or not gloryWarRole.role:
		return
	
	if not Status.CanInStatus(gloryWarRole.role, EnumInt1.ST_FightStatus): return
	
	#点击对面阵营npc
	if npc.GetPyDict()[1] != gloryWarRole.camp_id: return
	
	#获取当前的npc进度
	npc_number = gloryWarRole.now_npc_index
	if npc_number > 6:
		return
	
	cfg = GloryWarConfig.GW_NPC_Dict.get((GetCloseValue(WorldData.GetWorldLevel(), GloryWarConfig.GW_WLList), npc_number))
	if not cfg:
		print "GE_EXC, GloryWarMgr can not find world level:(%s), npc_number:(%s) in GW_NPC_Dict" % (GetCloseValue(WorldData.GetWorldLevel(), GloryWarConfig.GW_WLList), npc_number)
		return
	
	#是否有buff
	if npc_number in gloryWarRole.camp_obj.fast_fight.buff_set:
		add_buff = True
	else:
		add_buff = False
	################################################
	#YY防沉迷对奖励特殊处理
	yyAntiFlag = role.GetAnti()
	if yyAntiFlag == 1:#收益减半
		tmpReword = cfg.reward_items_fcm
	elif yyAntiFlag == 0:#原有收益
		tmpReword = cfg.reward_items
	else:
		tmpReword = []
		role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
	################################################
	#进入战斗
	PVE(gloryWarRole.role, cfg.mcid, AfterPveFight, (gloryWarRole.camp_id, cfg.npc_number, cfg.next_npc_type, cfg.npc_name, cfg.score, tmpReword, gloryWarRole.vote_number, add_buff))
	
def PVE(role, mcid, AfterFight, param):
	#妖王争霸pve战斗
	fight = Fight.Fight(EnumGameConfig.GloryWar_PVEFightType)
	
	left_camp, right_camp = fight.create_camp()
	
	_, _, _, _, _, _, number_of_votes, add_buff = param
	
	left_camp.create_online_role_unit(role, control_role_id = role.GetRoleID(), use_px = True)
	if add_buff:
		#有buff
		for u in left_camp.pos_units.itervalues():
			u.damage_upgrade_rate += 10
			u.damage_reduce_rate += 0.9
	elif number_of_votes:
		#没有buff, 有票数
		if number_of_votes > 10:
			number_of_votes = 10
		for u in left_camp.pos_units.itervalues():
			u.damage_upgrade_rate += number_of_votes / 100.0
			u.damage_reduce_rate += number_of_votes / 100.0
	
	right_camp.create_monster_camp_unit(mcid)
	fight.after_fight_fun = AfterFight
	fight.after_fight_param = param
	fight.start()
	
def AfterPveFight(fightObj):
	#不胜利不处理
	if fightObj.result is None:
		print "GE_EXC, GloryWarMgr fight with monster error"
		return
	if fightObj.result != 1:
		return
	#活动结束了, 不处理
	global GW_Begin_PVE
	if not GW_Begin_PVE: return
	
	camp_id, npc_number, npc_type, npc_name, score, reward_items, _, _ = fightObj.after_fight_param
	
	roles = fightObj.left_camp.roles
	if not roles:
		return
	role = list(roles)[0]
	
	#不在场景中(可能强制离开了战斗状态了)
	if role.GetSceneID() != EnumGameConfig.GloryWar_SceneID:
		return
	gloryWarRole = role.GetTempObj(EnumTempObj.GloryWarRole)
	if not gloryWarRole or not gloryWarRole.role:
		return
	
	camp_1 = gloryWarRole.camp_obj
	camp_2 = gloryWarRole.other_camp_obj
	
	#是否需要广播改变对面阵营npc外形
	need_broad = camp_1.fast_fight.is_max_index(npc_number)
	
	#加分
	role_id = role.GetRoleID()
	camp_1.add_score(gloryWarRole, 1, 1, npc_name, score, npc_type)
	fightObj.set_fight_statistics(role_id, EnumFightStatistics.EnumGloryWarScore, score)
	
	with GW_KillNpcReward:
		#发奖励物品
		if role.PackageEmptySize() < len(reward_items):
			Mail.SendMail(role_id, GlobalPrompt.GloryWar_Mail_Title, GlobalPrompt.GloryWar_Mail_Send, GlobalPrompt.GloryWar_Mail_Content, items = reward_items)
		else:
			for item in reward_items:
				role.AddItem(*item)
		
	fightObj.set_fight_statistics(role_id, EnumFightStatistics.EnumItems, reward_items)
	
	#不需要广播改变对面阵营npc外形
	if not need_broad:
		return
	
	#广播
	camp_1.score_rank.updata_camp_npc(camp_2, camp_id, npc_type)
	#传闻
	if camp_id == 1:
		camp_name = GlobalPrompt.GloryWar_CampName_1
	elif camp_id == 2:
		camp_name = GlobalPrompt.GloryWar_CampName_2
	else:
		return
	
	union = role.GetUnionObj()
	if union:
		tips = GlobalPrompt.GloryWar_KillNpc_1 % (camp_name,
												union.name,
												role.GetRoleName(),
												npc_name,
												camp_name)
	else:
		tips = GlobalPrompt.GloryWar_KillNpc_2 % (camp_name,
												role.GetRoleName(),
												npc_name,
												camp_name)
	cRoleMgr.Msg(2, 0, tips)
	cRoleMgr.Msg(11, 0, tips)
		
def ClickRole(leftGloryWarRole, right_role_id):
	if not Status.CanInStatus(leftGloryWarRole.role, EnumInt1.ST_FightStatus):
		return
	
	right_role = cRoleMgr.FindRoleByRoleID(right_role_id)
	if not right_role:
		return
	
	if right_role.GetCD(EnumCD.GloryWarFightCD) or right_role.GetCD(EnumCD.GloryWarClickFailCD):
		#对方CD中
		leftGloryWarRole.role.Msg(2, 0, GlobalPrompt.GloryWar_OtherCD)
		return
	
	rightGloryWarRole = right_role.GetTempObj(EnumTempObj.GloryWarRole)
	if not rightGloryWarRole or not rightGloryWarRole.role:
		return
	
	PvpFight(leftGloryWarRole, rightGloryWarRole)
	
def PvpFight(leftGloryWarRole, rightGloryWarRole):
	if not Status.CanInStatus(rightGloryWarRole.role, EnumInt1.ST_FightStatus):
		PVP_D(leftGloryWarRole, rightGloryWarRole, AfterFight)
	else:
		PVP(leftGloryWarRole, rightGloryWarRole, AfterFight)
	
def PVP_D(leftGloryWarRole, rightGloryWarRole, AfterFight):
	fight = Fight.Fight(EnumGameConfig.GloryWar_PVPFightType)
	fight.pvp = True
	left_camp, right_camp = fight.create_camp()
	
	#绑定血量
	left_camp.bind_hp(leftGloryWarRole.bind_hp)
	right_camp.bind_hp(rightGloryWarRole.bind_hp)
	
	left_camp.create_online_role_unit(leftGloryWarRole.role, fightData = leftGloryWarRole.fight_data, use_px = True)
	if leftGloryWarRole.be_kill_cnt >= 10:
		#被连杀超过10次, 加增伤500%、免伤90%
		for u in left_camp.pos_units.itervalues():
			u.damage_upgrade_rate += 5
			u.damage_reduce_rate += 0.9
	right_camp.create_outline_role_unit(rightGloryWarRole.fight_data)
	if rightGloryWarRole.be_kill_cnt >= 10:
		#被连杀超过10次, 加增伤500%、免伤90%
		for u in right_camp.pos_units.itervalues():
			u.damage_upgrade_rate += 5
			u.damage_reduce_rate += 0.9
	fight.after_fight_fun = AfterFight
	fight.after_fight_param = (leftGloryWarRole, rightGloryWarRole)
	
	fight.start()

def PVP(leftGloryWarRole, rightGloryWarRole, AfterFight):
	fight = Fight.Fight(EnumGameConfig.GloryWar_PVPFightType)
	fight.pvp = True
	left_camp, right_camp = fight.create_camp()
	
	#绑定血量
	left_camp.bind_hp(leftGloryWarRole.bind_hp)
	right_camp.bind_hp(rightGloryWarRole.bind_hp)
	
	left_camp.create_online_role_unit(leftGloryWarRole.role, fightData = leftGloryWarRole.fight_data, use_px = True)
	if leftGloryWarRole.be_kill_cnt >= 10:
		#被连杀超过10次, 加增伤500%、免伤90%
		for u in left_camp.pos_units.itervalues():
			u.damage_upgrade_rate += 5
			u.damage_reduce_rate += 0.9
	right_camp.create_online_role_unit(rightGloryWarRole.role, fightData = rightGloryWarRole.fight_data, use_px = True)
	if rightGloryWarRole.be_kill_cnt >= 10:
		#被连杀超过10次, 加增伤500%、免伤90%
		for u in right_camp.pos_units.itervalues():
			u.damage_upgrade_rate += 5
			u.damage_reduce_rate += 0.9
	fight.after_fight_fun = AfterFight
	fight.after_fight_param = (leftGloryWarRole, rightGloryWarRole)
	
	fight.start()

def AfterFight(fightObj):
	if fightObj.result is None:
		print "GE_EXC, GloryWarMgr fight with role error"
		return
	
	leftGloryWarRole, rightGloryWarRole = fightObj.after_fight_param
	
	left_role_name = leftGloryWarRole.role_name
	right_role_name = rightGloryWarRole.role_name
	
	if fightObj.result == 1:
		#左阵营胜利, 加分
		win_score = CalScore(leftGloryWarRole, rightGloryWarRole)
		leftGloryWarRole.camp_obj.add_score(leftGloryWarRole, 1, 1, right_role_name, win_score)
		#右阵营胜利, 加分
		rightGloryWarRole.camp_obj.add_score(rightGloryWarRole, 0, 0, left_role_name, 3)
		#战斗奖励显示
		fightObj.set_fight_statistics(leftGloryWarRole.role_id, EnumFightStatistics.EnumGloryWarScore, win_score)
		fightObj.set_fight_statistics(rightGloryWarRole.role_id, EnumFightStatistics.EnumGloryWarScore, 3)
		#提示
		leftGloryWarRole.role.Msg(14, 0, GlobalPrompt.GloryWar_FightTips_1 % (right_role_name, win_score))
		rightGloryWarRole.role.Msg(14, 0, GlobalPrompt.GloryWar_FightTips_4 % left_role_name)
	elif fightObj.result == -1:
		#左阵营失败, 加分
		leftGloryWarRole.camp_obj.add_score(leftGloryWarRole, 1, 0, right_role_name, 3)
		#右阵营胜利, 加分
		win_score = CalScore(rightGloryWarRole, leftGloryWarRole)
		rightGloryWarRole.camp_obj.add_score(rightGloryWarRole, 0, 1, left_role_name, win_score)
		#战斗奖励显示
		fightObj.set_fight_statistics(leftGloryWarRole.role_id, EnumFightStatistics.EnumGloryWarScore, 3)
		fightObj.set_fight_statistics(rightGloryWarRole.role_id, EnumFightStatistics.EnumGloryWarScore, win_score)
		#提示
		leftGloryWarRole.role.Msg(14, 0, GlobalPrompt.GloryWar_FightTips_2 % right_role_name)
		rightGloryWarRole.role.Msg(14, 0, GlobalPrompt.GloryWar_FightTips_3 % (left_role_name, win_score))
	elif fightObj.result == 0:
		#平局, 都算失败
		leftGloryWarRole.camp_obj.add_score(leftGloryWarRole, 1, 0, right_role_name, 3)
		rightGloryWarRole.camp_obj.add_score(rightGloryWarRole, 0, 0, left_role_name, 3)
		#战斗奖励显示
		fightObj.set_fight_statistics(leftGloryWarRole.role_id, EnumFightStatistics.EnumGloryWarScore, 3)
		fightObj.set_fight_statistics(rightGloryWarRole.role_id, EnumFightStatistics.EnumGloryWarScore, 3)
		#提示
		leftGloryWarRole.role.Msg(14, 0, GlobalPrompt.GloryWar_FightTips_2 % right_role_name)
		rightGloryWarRole.role.Msg(14, 0, GlobalPrompt.GloryWar_FightTips_4 % left_role_name)
		
def CalScore(leftGloryWarRole, rightGloryWarRole):
	#胜利获得积分
	return rightGloryWarRole.zdl_score + rightGloryWarRole.kill_cnt * 2 + leftGloryWarRole.kill_cnt * 2

def Votes(voteRole, beVoteRole):
	if beVoteRole.role_id not in voteRole.camp_obj.fast_fight.pve_datas:
		return
	voteRole.camp_obj.fast_fight.add_ticket(voteRole, beVoteRole)
	
@PublicScene.RegSceneAfterJoinRoleFun(EnumGameConfig.GloryWar_SceneID)
def AfterJoin(scene, role):
	global GW_Begin_PVP
	gloryWarRole = role.GetTempObj(EnumTempObj.GloryWarRole)
	if not gloryWarRole:
		role.BackPublicScene()
		return
	
	if GW_Begin_PVP:
		if gloryWarRole.camp_id == 1:
			role.SetAppStatus(3)
		else:
			role.SetAppStatus(4)
	else:
		if gloryWarRole.camp_id == 1:
			role.SetAppStatus(5)
		else:
			role.SetAppStatus(6)
	
	gloryWarRole.role = role
	
	gloryWarRole.camp_obj.add_camp_role(gloryWarRole)
	
	Status.ForceInStatus(role, EnumInt1.ST_GloryWar)
	
	#每日必做 -- 荣耀之战
	Event.TriggerEvent(Event.Eve_DoDailyDo, role, (DailyDo.Daily_GW, 1))
	
@PublicScene.RegSceneBeforeLeaveFun(EnumGameConfig.GloryWar_SceneID)
def BeforeLeave(scene, role):
	role.SetAppStatus(0)
	
	Status.Outstatus(role, EnumInt1.ST_GloryWar)
	
	gloryWarRole = role.GetTempObj(EnumTempObj.GloryWarRole)
	if not gloryWarRole:
		return
	gloryWarRole.camp_obj.del_camp_role(gloryWarRole)
	
	gloryWarRole.role = None
	
def OnRoleClientLost(role, param):
	if role.GetSceneID() != EnumGameConfig.GloryWar_SceneID:
		return
	role.BackPublicScene()
#===============================================================================
# 开始、结束
#===============================================================================
def ReadyGloryWarFiveMinute():
	'''
	五分钟准备
	'''
	#世界数据未载回, 活动不开(如果尝试在载回后再次触发的话活动结束要延后)
	if not WorldData.WD.returnDB:
		print "GE_EXC, ReadyGloryWarFiveMinute world data have not return"
		return
	if WorldData.GetWorldLevel() < EnumGameConfig.GloryWar_WorldLevel:
		WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_Set_GloryWar, [])
		return
	scene = cSceneMgr.SearchPublicScene(EnumGameConfig.GloryWar_SceneID)
	if not scene:
		print "GE_EXC, GloryWarMgr can not find glory war sceneID:%s" % EnumGameConfig.GloryWar_SceneID
		return
	
	#国服开启公会圣域争霸的时候不开启荣耀之战
	if Environment.IsDevelop is True or Environment.EnvIsQQ():
		if Time.GetWeekDay(cDateTime.Now()) in (2, 5):
			#开服天数满31天，世界等级满80级，开启圣域争霸，关闭荣耀之战
			if WorldData.GetWorldKaiFuDay() >= 31 and WorldData.GetWorldLevel() >= 80:
				return
		
	cComplexServer.RegTick(240, ReadyGloryWarOneMinute, scene)
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.GloryWar_TenMinuteReady)
	
def ReadyGloryWarOneMinute(argv, regparam):
	'''
	一分钟准备
	'''
	global GW_CanIn
	if GW_CanIn: return
	
	GW_CanIn = True
	
	#创建积分榜对象
	GW_ScoreRank = ScoreRank(regparam)
	
	#创建两个阵营
	global GW_Camp_1, GW_Camp_2
	GW_Camp_1 = GloryWarCamp(1, GW_ScoreRank, FastFightPvp(regparam))
	GW_Camp_2 = GloryWarCamp(2, GW_ScoreRank, FastFightPvp(regparam))
	
	#计算战斗力前20名
	CalZdlRank()
	
	cComplexServer.RegTick(60, BeginGloryWarPvp)
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.GloryWar_OneMinuteReady)
	
def CalZdlRank():
	'''
	计算战斗力前20名
	'''
	rank_data = SystemRank.ZR.ReturnData().items()
	#战斗力 --> 等级 --> ID
	rank_data.sort(key = lambda x:(x[1][2], x[1][1], x[1][0]), reverse = True)
	global GW_ZDL_Rank
	GW_ZDL_Rank = dict(zip(range(1, 21), rank_data[0:20]))
	
def SetRoleStatus(camp, status):
	'''
	设置阵营所有玩家状态
	@param camp:阵营对象
	@param status:状态
	'''
	RFR = cRoleMgr.FindRoleByRoleID
	ETGWR = EnumTempObj.GloryWarRole
	for role_id in camp.fast_fight.pvp_datas:
		role = RFR(role_id)
		if not role:
			continue
		gloryWarRole = role.GetTempObj(ETGWR)
		if not gloryWarRole or not gloryWarRole.role:
			continue
		role.SetAppStatus(status)
	
def BeginGloryWarPvp(argv, regparam):
	'''
	开始pvp战斗
	'''
	global GW_Begin_PVP, GW_Camp_1, GW_Camp_2
	if GW_Begin_PVP: return
	
	GW_Begin_PVP = True
	
	#开始发送数据
	GW_Camp_1.fast_fight.begin_send()
	
	#设置角色点击状态
	SetRoleStatus(GW_Camp_1, 3)
	SetRoleStatus(GW_Camp_2, 4)
	
	cComplexServer.RegTick(1200, EndPvp)
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.GloryWar_PvpBegin)

def EndPvp(argv, param):
	'''
	结束pvp战斗
	@param argv:
	@param param:
	'''
	global GW_Begin_PVP
	GW_Begin_PVP = False
	
	BeginGloryWarPve()

def CreateGloryWarNpc(scene, cfg, npc_pos, camp_id, camp):
	'''
	创建荣耀之战阵营npc
	@param scene:场景对象
	@param cfg:npc配置
	@param npc_pos:npc位置
	@param camp_id:阵营ID
	'''
	global GW_Npc, GW_Npc_List
	
	#创建npc
	npc = scene.CreateNPC(cfg.npc_type, npc_pos[0], npc_pos[1], npc_pos[2], 1)
	npc.SetPyDict(1, camp_id)
	
	#构建阵营npc信息
	camp.score_rank.build_camp_npc(camp_id, npc.GetNPCID(), cfg.npc_type)
	GW_Npc_List.append((npc.GetNPCID(), cfg.npc_type))
	GW_Npc.append(npc)
	
	return npc
	
def BuildGloryWarPve(camp, npc, cfg, role_status, scene):
	'''
	构建荣耀之战pve数据
	@param camp:阵营对象
	@param npc:阵营npc
	@param cfg:npc配置
	@param role_status:需要设置的角色状态
	'''
	RFB = cRoleMgr.FindRoleByRoleID
	#销毁pvp快速战斗面板更新tick
	camp.fast_fight.destroy()
	#保存一份pvp快速战斗同步数据
	tmp_fast_fight_data = camp.fast_fight.pvp_datas
	#创建一个pve快速战斗面板对象
	camp.fast_fight = FastFightPve(scene)
	#根据保存的pvp快速战斗数据构建pve快速战斗面板数据
	ETGWR = EnumTempObj.GloryWarRole
	for role_id, value in tmp_fast_fight_data.iteritems():
		role = RFB(role_id)
		if not role:
			continue
		if not value[0]:
			continue
		gloryWarRole = role.GetTempObj(ETGWR)
		if not gloryWarRole or not gloryWarRole.role:
			continue
		role.SetAppStatus(role_status)
		camp.fast_fight.add_pve_role(gloryWarRole, npc.GetNPCID(), cfg.npc_type, value[2], value[0])
	
def BeginGloryWarPve():
	'''
	清理所有玩家状态, 开始15分钟pve战斗
	'''
	global GW_Begin_PVE
	if GW_Begin_PVE: return
	
	GW_Begin_PVE = True
	
	scene = cSceneMgr.SearchPublicScene(EnumGameConfig.GloryWar_SceneID)
	if not scene:
		print "GE_EXC, GloryWarMgr can not find glory war sceneID:%s" % EnumGameConfig.GloryWar_SceneID
		return
	cfg = GloryWarConfig.GW_NPC_Dict.get((GetCloseValue(WorldData.GetWorldLevel(), GloryWarConfig.GW_WLList), 1))
	if not cfg:
		print "GE_EXC, GloryWarMgr can not find world level:(%s), npc_number:(%s) in GW_NPC_Dict" % (GetCloseValue(WorldData.GetWorldLevel(), GloryWarConfig.GW_WLList), 1)
		return
	
	global GW_Camp_1, GW_Camp_2, GloryWar_Camp_Npc_Pos_1, GloryWar_Camp_Npc_Pos_2
	#创建第一阵营npc
	npc_1 = CreateGloryWarNpc(scene, cfg, GloryWar_Camp_Npc_Pos_1, 1, GW_Camp_1)
	BuildGloryWarPve(GW_Camp_1, npc_1, cfg, 5, scene)
	#创建第二阵营npc
	npc_2 = CreateGloryWarNpc(scene, cfg, GloryWar_Camp_Npc_Pos_2, 2, GW_Camp_2)
	BuildGloryWarPve(GW_Camp_2, npc_2, cfg, 6, scene)
	
	cComplexServer.RegTick(900, EndGloryWar)
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.GloryWar_PveBegin)

def EndGloryWar(argv, param):
	'''
	结束荣耀之战, 清理并发奖
	'''
	global GW_Begin_PVE, GW_CanIn, GW_Camp_1, GW_Camp_2
	GW_Begin_PVE = False
	GW_CanIn = False
	
	#清理tick
	GW_Camp_1.fast_fight.destroy()
	GW_Camp_1.score_rank.destroy()
	
	#删除npc
	scene = cSceneMgr.SearchPublicScene(EnumGameConfig.GloryWar_SceneID)
	if not scene:
		print "GE_EXC, GloryWarMgr can not find glory war sceneID:%s" % EnumGameConfig.GloryWar_SceneID
		return
	global GW_Npc, GW_Npc_List
	for npc in GW_Npc:
		npc.Destroy()
	GW_Npc_List = []
	GW_Npc = []
	
	#发奖
	Award(GW_Camp_1, GW_Camp_2)
	
	#将所有玩家清理出荣耀之战场景
	for role in scene.GetAllRole():
		role.BackPublicScene()
	
	#删除所有对象
	GW_Camp_1 = None
	GW_Camp_2 = None
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.GloryWar_End)
	
def GetCloseValue(value, value_list):
	'''
	返回第一个大于value的上一个值
	@param value:
	@param value_list:
	'''
	tmp_level = 0
	for i in value_list:
		if i > value:
			return tmp_level
		tmp_level = i
	else:
		#没有找到返回最后一个值
		return tmp_level
	
def CampReward(camp, role_msg, is_win):
	'''
	阵营奖励
	@param camp:阵营对象
	@param role_msg:玩家第一次进入活动时记录的union_id, level
	@param is_win:是否胜利
	'''
	GWG = GloryWarConfig.GW_CampReward_Dict.get
	RC = RewardBuff.CalNumber
	RG = RewardBuff.enGloryWar
	for role_id in camp.fast_fight.pve_datas:
		cfg = GWG((is_win, GetCloseValue(role_msg[role_id][1], GloryWarConfig.GW_CRList)))
		if not cfg:
			print "GE_EXC, GloryWarMgr can not find is_win:(%s), level:(%s) in GW_CampReward_Dict" % (is_win, GetCloseValue(role_msg[role_id][1], GloryWarConfig.GW_CRList))
			continue
		if is_win:
			desc = GlobalPrompt.GloryWar_CampWin
		else:
			desc = GlobalPrompt.GloryWar_CampFail
		with GW_EndReward_Log:
			AutoLog.LogBase(role_id, AutoLog.eveGloryWarCampWin, (camp.camp_id, is_win))
		AwardMgr.SetAward(role_id, EnumAward.GWCampAward, money = RC(RG, cfg.reward_money), reputation = RC(RG, cfg.reward_reputation), clientDescParam = (desc, ))
	
def UnionReward(role_msg, union_id, rank, name):
	'''
	公会排名奖励
	@param role_msg:玩家第一次进入活动时记录的union_id, level
	@param union_id:排名前三的玩家的union_id
	@param rank:排名
	'''
	GUG = GloryWarConfig.GW_UnionReward_Dict.get
	RC = RewardBuff.CalNumber
	RG = RewardBuff.enGloryWar
	for role_id in role_msg:
		if role_msg[role_id][0] != union_id:
			continue
		cfg = GUG((rank, GetCloseValue(role_msg[role_id][1], GloryWarConfig.GW_URList)))
		if not cfg:
			print "GE_EXC, GloryWarMgr can not find rank:(%s), level:(%s) in GW_UnionReward_Dict" % (rank, GetCloseValue(role_msg[role_id][1], GloryWarConfig.GW_URList))
			continue
		with GW_EndReward_Log:
			AutoLog.LogBase(role_id, AutoLog.eveGloryWarUnionRank, (name, rank))
		AwardMgr.SetAward(role_id, EnumAward.GWUnionAward, itemList = [(coding, RC(RG, cnt)) for (coding, cnt) in cfg.reward_items], clientDescParam = (name, rank))
	
def UnionAllReward(rank_data, role_msg, rank, name):
	'''
	积分排名前三的玩家的公会参与这发奖
	@param rank_data:
	@param role_msg:
	@param rank:
	'''
	GUG = GloryWarConfig.GW_UnionReward_Dict.get
	RC = RewardBuff.CalNumber
	RG = RewardBuff.enGloryWar
	rank_role_msg = role_msg[rank_data[rank - 1][0]]
	if not rank_role_msg[0]:
		cfg = GUG((rank, GetCloseValue(rank_data[rank - 1][0], GloryWarConfig.GW_URList)))
		if not cfg:
			print "GE_EXC, GloryWarMgr can not find rank:(%s), level:(%s) in GW_UnionReward_Dict" % (rank, GetCloseValue(rank_data[rank - 1][0], GloryWarConfig.GW_URList))
			return
		with GW_EndReward_Log:
			AutoLog.LogBase(rank_data[rank - 1][0], AutoLog.eveGloryWarUnionRank, (name, rank))
		AwardMgr.SetAward(rank_data[rank - 1][0], EnumAward.GWUnionAward, itemList = [(coding, RC(RG, cnt)) for (coding, cnt) in cfg.reward_items], clientDescParam = (name, rank))
	else:
		UnionReward(role_msg, rank_role_msg[0], rank, name)
	
def Award(camp1, camp2):
	'''
	活动结束后发奖
	@param camp1:阵营1对象
	@param camp2:阵营2对象
	'''
	score_rank = camp1.score_rank
	role_msg = score_rank.role_msg
	
	#阵营奖励
	if score_rank.camp_score[0] > score_rank.camp_score[1]:
		#第一阵营胜
		CampReward(camp1, role_msg, 1)
		CampReward(camp2, role_msg, 0)
	elif score_rank.camp_score[0] < score_rank.camp_score[1]:
		#第二阵营胜
		CampReward(camp1, role_msg, 0)
		CampReward(camp2, role_msg, 1)
	else:
		#平分, 两个阵营都算胜利
		CampReward(camp1, role_msg, 1)
		CampReward(camp2, role_msg, 1)
	
	#排行榜奖励 -- 先要排一次名次
	rank_data = camp1.score_rank.score_datas.items()
	rank_data.sort(key = lambda x : x[1][3], reverse = True)
	index = 1
	GRG = GloryWarConfig.GW_RankReward_Dict.get
	RC = RewardBuff.CalNumber
	RG = RewardBuff.enGloryWar
	for (role_id, _) in rank_data:
		cfg = GRG((index, GetCloseValue(role_msg[role_id][1], GloryWarConfig.GW_RRList)))
		index += 1
		if not cfg:
			print "GE_EXC, GloryWarMgr can not find index:(%s), level:(%s) in GW_RankReward_Dict" % (index, GetCloseValue(role_msg[role_id][1], GloryWarConfig.GW_RRList))
			continue
		with GW_EndReward_Log:
			AutoLog.LogBase(role_id, AutoLog.eveGloryWarScoreRank, index - 1)
		AwardMgr.SetAward(role_id, EnumAward.GWRankAward, money = RC(RG, cfg.reward_money), itemList = [(coding, RC(RG, cnt)) for (coding, cnt) in cfg.reward_items], clientDescParam = (index - 1, ))
	
	#公会奖励
	rank_len = len(rank_data)
	if rank_len >= 1:
		UnionAllReward(rank_data, role_msg, 1, rank_data[0][1][0])
	if rank_len >= 2:
		UnionAllReward(rank_data, role_msg, 2, rank_data[1][1][0])
	if rank_len >= 3:
		UnionAllReward(rank_data, role_msg, 3, rank_data[2][1][0])
	
	#积分奖励
	GSG = GloryWarConfig.GW_ScoreReward_Dict.get
	for role_id in score_rank.role_score:
		cfg = GSG((GetCloseValue(score_rank.role_score[role_id], GloryWarConfig.GW_SSList), GetCloseValue(role_msg[role_id][1], GloryWarConfig.GW_SRList)))
		if not cfg:
			print "GE_EXC, GloryWarMgr can not find score:(%s), level:(%s) in GW_ScoreReward_Dict" % (GetCloseValue(score_rank.role_score[role_id], GloryWarConfig.GW_SSList), GetCloseValue(role_msg[role_id][1], GloryWarConfig.GW_SRList))
			continue
		with GW_EndReward_Log:
			AutoLog.LogBase(role_id, AutoLog.eveGloryWarScore, score_rank.role_score[role_id])
		AwardMgr.SetAward(role_id, EnumAward.GWScoreAward, money = RC(RG, cfg.reward_money), reputation = RC(RG, cfg.reward_reputation), itemList = [(coding, RC(RG, cnt)) for (coding, cnt) in cfg.reward_items], clientDescParam = (score_rank.role_score[role_id], ))
		#离线命令设置今日参与了荣耀之战
		Call.LocalDBCall(role_id, HasJoinGloryWar, cDateTime.Days())
	
	#精彩活动--荣誉之战
	if not rank_data:
		return
	WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_Set_GloryWar, rank_data[0])
	
def CheckGloryWarRole(role):
	gloryWarRole = role.GetTempObj(EnumTempObj.GloryWarRole)
	if not gloryWarRole or not gloryWarRole.role:
		return None
	return gloryWarRole
#===============================================================================
# 离线命令
#===============================================================================
def HasJoinGloryWar(role, param):
	'''
	设置今日已经参与了荣耀之战
	@param role:
	@param param:
	'''
	oldDays = param
	newDays = cDateTime.Days()
	#若跨天则不需要设置
	if newDays > oldDays:
		return
	
	role.SetDI1(EnumDayInt1.GloryWarJoin, 1)

#===============================================================================
# 客户端请求
#===============================================================================
def RequestJoinGloryWar(role, msg):
	'''
	请求进入场景
	@param role:
	@param msg:
	'''
	global GW_CanIn
	if not GW_CanIn: return
	
	if role.GetLevel() < EnumGameConfig.GloryWar_LevelLimit:
		return
	if role.GetSceneID() == EnumGameConfig.GloryWar_SceneID:
		return
	if not Status.CanInStatus(role, EnumInt1.ST_GloryWar):
		return
	
	gloryWarRole = role.GetTempObj(EnumTempObj.GloryWarRole)
	if gloryWarRole and gloryWarRole.role:
		return
	
	#北美版
	if Environment.EnvIsNA():
		#今天是否已经参与过荣耀之战
		if role.GetDI1(EnumDayInt1.GloryWarJoin):
			#提示
			role.Msg(2, 0, GlobalPrompt.GloryWar_Has_Join)
			return
	
	campId = role.GetDI8(EnumDayInt8.GloryWar_CampId)
	if not gloryWarRole:
		if not campId:
			campId = AllocCamp(role)
		if campId == 1:
			otherCampId = 2
		else:
			otherCampId = 1
		role.SetDI8(EnumDayInt8.GloryWar_CampId, campId)
		gloryWarRole = CreateGloryWarRole(role, campId, otherCampId)
	
	if campId == 1:
		global GloryWar_Camp_Pos_1
		role.Revive(*GloryWar_Camp_Pos_1)
	else:
		global GloryWar_Camp_Pos_2
		role.Revive(*GloryWar_Camp_Pos_2)
	
	#找回
	Event.TriggerEvent(Event.Eve_FB_AfterHW, role, None)
	
	#圣诞转转乐
	Event.TriggerEvent(Event.Eve_IncChristmasWingLotteryTime, role, EnumGameConfig.Source_GloryWar)
	#元旦金猪活动任务进度
	Event.TriggerEvent(Event.Eve_NewYearDayPigTask, role, (EnumGameConfig.NewYearDay_Task_GloryWar, True))
	
	
def RequestLeaveGloryWar(role, msg):
	'''
	请求离开荣耀之战
	@param role:
	@param msg:
	'''
	if role.GetSceneID() != EnumGameConfig.GloryWar_SceneID:
		return
	if Status.IsInStatus(role, EnumInt1.ST_FightStatus):
		return
	gloryWarRole = CheckGloryWarRole(role)
	if not gloryWarRole: return
	
	role.BackPublicScene()
	
def RequestPvpFight(role, msg):
	'''
	请求pvp战斗
	@param role:
	@param msg:玩家ID
	'''
	if not msg or role.GetRoleID() == msg: return
	
	global GW_Begin_PVP
	if not GW_Begin_PVP: return
	
	if role.GetCD(EnumCD.GloryWarFightCD):
		role.Msg(2, 0, GlobalPrompt.GloryWar_OwnCD)
		return
	if role.GetSceneID() != EnumGameConfig.GloryWar_SceneID:
		return
	gloryWarRole = CheckGloryWarRole(role)
	if not gloryWarRole: return
	
	ClickRole(gloryWarRole, msg)
	
def RequestPveFight(role, msg):
	'''
	请求pve战斗
	@param role:
	@param msg:npc索引
	'''
	global GW_Begin_PVE
	if not GW_Begin_PVE: return
	
	global GW_Npc
	if not GW_Npc: return
	
	if role.GetSceneID() != EnumGameConfig.GloryWar_SceneID:
		return
	gloryWarRole = CheckGloryWarRole(role)
	if not gloryWarRole: return
	
	if gloryWarRole.camp_id == 1:
		ClickNpc(role, GW_Npc[0])
	else:
		ClickNpc(role, GW_Npc[1])
	
def RequestVotes(role, msg):
	'''
	请求投票
	@param role:
	@param msg:投给谁的角色ID -- 可以自己给自己投票
	'''
	if not msg: return
	
	global GW_Begin_PVE
	if not GW_Begin_PVE: return
	
	if role.GetSceneID() != EnumGameConfig.GloryWar_SceneID:
		return
	voteRole = CheckGloryWarRole(role)
	if not voteRole:
		return
	if voteRole.is_vote:
		return
	brole = cRoleMgr.FindRoleByRoleID(msg)
	if not brole:
		return
	beVoteRole = CheckGloryWarRole(brole)
	if not beVoteRole:
		return
	
	Votes(voteRole, beVoteRole)
	
def RequestOpenPanel(role, msg):
	'''
	请求打开快速战斗面板
	@param role:
	@param msg:None
	'''
	global GW_CanIn
	if not GW_CanIn: return
	
	if role.GetSceneID() != EnumGameConfig.GloryWar_SceneID:
		return
	gloryWarRole = CheckGloryWarRole(role)
	if not gloryWarRole: return
	
	gloryWarRole.camp_obj.fast_fight.open_panel(gloryWarRole)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		InitClickFun()
		Cron.CronDriveByMinute((2038, 1, 1), ReadyGloryWarFiveMinute, H = "H == 21", M = "M == 5")
	
	#北美版
	if Environment.EnvIsNA() and Environment.HasLogic and not Environment.IsCross:
		Cron.CronDriveByMinute((2038, 1, 1), ReadyGloryWarFiveMinute, H = "H == 15", M = "M == 5")
	
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_ClientLost, OnRoleClientLost)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GloryWar_Join", "请求进入荣耀之战"), RequestJoinGloryWar)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GloryWar_Leave", "请求离开荣耀之战"), RequestLeaveGloryWar)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GloryWar_PvpFight", "请求荣耀之战pvp战斗"), RequestPvpFight)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GloryWar_PveFight", "请求荣耀之战pve战斗"), RequestPveFight)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GloryWar_Votes", "请求荣耀之战投票"), RequestVotes)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GloryWar_OpenPanel", "请求荣耀之战打开快速战斗面板"), RequestOpenPanel)
		
		
