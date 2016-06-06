#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DukeOnDuty.DukeOnDuty")
#===============================================================================
# 城主轮值
#===============================================================================
import random
import time
import Environment
import cComplexServer
import cSceneMgr
import cRoleMgr
import cNetMessage
import cDateTime
from ComplexServer.Time import Cron
from ComplexServer.Log import AutoLog
from Common.Other import EnumSysData,GlobalPrompt,EnumGameConfig,EnumSocial,EnumFightStatistics
from Common.Message import AutoMessage
from Game.Persistence import Contain
from Game.SysData import WorldData
from Game.SystemRank import SystemRank
from Game.Fight import Fight, Middle
from Game.Activity.Award import AwardMgr
from Game.Activity.Title import Title
from Game.NPC import EnumNPCData, NPCServerFun
from Game.Role import Status, Event, Call
from Game.Role.Mail import Mail
from Game.Role.Data import EnumCD, EnumInt1, EnumDayInt8
from Game.Property import PropertyEnum
from Game.Union import UnionMgr
from Game.Activity.WonderfulAct import WonderfulActMgr, EnumWonderType
from Game.Activity.DukeOnDuty import DukeOnDutyDefine, DukeOnDutyConfig
from Game.ThirdParty.QQidip import QQEventDefine
from Game.Scene import PublicScene
from Game.Activity.RewardBuff import RewardBuff

if "_HasLoad" not in dir():
	BOSS_OBJ = None			#缓存雕像
	IS_BOSS_EXISTED = 0 	#雕像是否存在 1为第一模型，2为残破模型
	
	PATRON_SAINT_OBJ = None #缓存守护神
	#持久化字典索引
	DUKE_ON_DUTY_IDX1 = 1 	
	DUKE_ON_DUTY_IDX2 = 2
	DUKE_ON_DUTY_IDX3 = 3
	DUKE_ON_DUTY_IDX4 = 4
	DUKE_ON_DUTY_IDX5 = 5
	
	ATTACK_UNION_LIST = []	#该次活动可参加轮值的攻方工会
	DEFENCE_UNION_LIST = [] #该次活动可参加轮值的守方工会
	ROLE_ID_DUKE = []		#保存可参加轮值的玩家
	ROLE_JOIN_DUKE = [] 	#缓存进入轮值场景的玩家
	
	UNION_OBJ = {}			#缓存参加的工会数据
	UNION_POINT_DICT = {}	#缓存攻方积分

	ATTACK_PLAYER_DICT = {} #在战场的攻方玩家
	DEFENCE_PLAYER_DICT = {}#在战场的守方玩家

	
	ROLE_FIGHT_DICT = {} 	#缓存玩家战斗信息
	IS_START = False		#活动开关
	IS_PREPARE = False  	#准备开关
	
	STATUE_HP = None		#保存雕像的血
	_SAVE_ROLE_HP = {}  	#保存玩家血量
	SAVE_FIGHT_DATA = {}	#保存玩家的战斗数据
	
	
	#idip统计信息
	RoleSet = set()
	
	DIFF_BETWEEN_SECOND = 23 * 3600 + 40 * 60	#23小时40分
	
	Duty_On_Show_Rank = AutoMessage.AllotMessage("Duty_On_Show_Rank", "通知客户端工会排行")
	Duty_Union_Member_Point_Rank = AutoMessage.AllotMessage("Duty_Union_Member_Point_Rank", "工会成员积分排行榜更新")	
	Duty_Role_After_Fight = AutoMessage.AllotMessage("Duty_Role_After_Fight", "玩家战斗后数据通知")
	Duty_Send_player_data = AutoMessage.AllotMessage("Duty_Send_player_data", "发送匹配玩家的数据")
	Duty_Send_Buff_Data = AutoMessage.AllotMessage("Duty_Send_Buff_Data", "同步buff数据")
	Duty_Send_Union_Total_Point = AutoMessage.AllotMessage("Duty_Send_Union_Total_Point", "同步工会总积分")
	Duty_Send_Data_Role = AutoMessage.AllotMessage("Duty_Send_Data_Role", "玩家进场景发送血量和工会排名")
	Duty_After_Fight_Data = AutoMessage.AllotMessage("Duty_After_Fight_Data", "城主雕像被灭")
	Duty_After_Duty_Fight_Result = AutoMessage.AllotMessage("Duty_After_Duty_Fight_Result", "轮值战斗结果")
	Duty_Send_Close_War = AutoMessage.AllotMessage("Duty_Send_Close_War", "通知客户端关闭战场界面")
	Duty_Send_Statu_HP = AutoMessage.AllotMessage("Duty_Send_Statu_HP", "通知客户端雕像半血")
	Duty_Send_role_HP = AutoMessage.AllotMessage("Duty_Send_role_HP", "通知客户端玩家血量")
	#日志
	DukeQuackCDCost = AutoLog.AutoTransaction("DukeQuackCDCost", "城主加速CD消耗")
	DutyUnionRankReward = AutoLog.AutoTransaction("DutyUnionRankReward", "城主轮值工会排名奖励")
	DutyPersonRankReward = AutoLog.AutoTransaction("DutyPersonRankReward", "城主轮值个人排名奖励")
	DutySendMail = AutoLog.AutoTransaction("DutySendMail", "城主轮值邮件")
	
class GangOnDuty(object):
	def __init__(self, unionID, unionName, camp):
		self.name = unionName		#工会名
		self.unionID = unionID		#工会ID
		self.camp = camp			#阵营，是守方还是攻方
		self.total_point = 0		#总积分数
		self.kill_row = {}			#连胜纪录
		self.personal_point = {}	#个人积分纪录
		self.join_roleid_set = {}	#参加的成员
		self.buff = None			#buff
		self.attack_buff = None		#连攻buff
	
	def AddPoint(self, state, role, fight_name, point):
		'''
		增加积分
		@param state:胜利/失败 标志
		@param role:
		@param fight_name:对手名字
		@param point:
		'''
		if not role:
			return
		roleId = role.GetRoleID()
		unionId = role.GetUnionID()
		if unionId != self.unionID:
			return
		self.total_point += point
		if roleId in self.personal_point:
			self.personal_point[roleId][3] += point
		else:
			self.personal_point[roleId] =  [roleId, role.GetRoleName(), role.GetLevel(), point]
		
		global UNION_POINT_DICT
		global ATTACK_UNION_LIST
		global ROLE_FIGHT_DICT
		if self.camp:#是攻击方记录
			UNION_POINT_DICT[self.unionID] = [self.unionID, self.name, self.total_point]
		
		if roleId not in ROLE_FIGHT_DICT:#记录玩家的战斗日志
			ROLE_FIGHT_DICT[roleId] = [[state, fight_name, point]]
		else:
			ROLE_FIGHT_DICT[roleId].append([state, fight_name, point])
		#跟新排行榜
		self.Fresh_rank()
		#连斩
		#0主动PVP攻击输，1主动PVP攻击赢，2攻击雕像，3攻击守护神，4被攻击输，5被攻击
		if roleId not in self.kill_row:
			self.kill_row[roleId] = 0
		if state == 1 or state == 5:#PVP战斗胜利
			self.kill_row[roleId] = self.kill_row.get(roleId, 0) + 1
			if self.kill_row[roleId] == 5:
				#各版本判断
				if Environment.EnvIsNA():
					cRoleMgr.Msg(11, 0, GlobalPrompt.DUKE_KILL_FIVE % role.GetRoleName())
				else:
					cRoleMgr.Msg(1, 0, GlobalPrompt.DUKE_KILL_FIVE % role.GetRoleName())
			if self.kill_row[roleId] == 10:
				#各版本判断
				if Environment.EnvIsNA():
					cRoleMgr.Msg(11, 0, GlobalPrompt.DUKE_KILL_TEN % role.GetRoleName())
				else:
					cRoleMgr.Msg(1, 0, GlobalPrompt.DUKE_KILL_TEN % role.GetRoleName())
			if self.kill_row[roleId] >= 15:
				#各版本判断
				if Environment.EnvIsNA():
					cRoleMgr.Msg(11, 0, GlobalPrompt.DUKE_KILL_FIFTEEN % (role.GetRoleName(), self.kill_row[roleId]))
				else:
					cRoleMgr.Msg(1, 0, GlobalPrompt.DUKE_KILL_FIFTEEN % (role.GetRoleName(), self.kill_row[roleId]))
		elif state == 0 or state == 4:#PVP战斗失败
			killNum = self.kill_row[roleId]
			if killNum >= 5:
				#各版本判断
				if Environment.EnvIsNA():
					cRoleMgr.Msg(11, 0, GlobalPrompt.DUKE_KILLED_MSG % (fight_name, role.GetRoleName(), killNum))
				else:
					cRoleMgr.Msg(1, 0, GlobalPrompt.DUKE_KILLED_MSG % (fight_name, role.GetRoleName(), killNum))
			self.kill_row[roleId] = 0	#清空连斩
		#连斩数据，积分数据，战斗记录, 工会积分
		role.SendObj(Duty_Role_After_Fight, [self.kill_row[roleId], self.personal_point[roleId][3], ROLE_FIGHT_DICT[roleId], self.total_point])
	
	def GetKillRow(self, roleId):
		'''
		获取连斩数
		@param roleId:
		'''
		if roleId in self.kill_row:
			return self.kill_row[roleId]
		return 0
		
	def Fresh_rank(self):
		'''
		跟新排行榜
		'''
		rank_list = self.personal_point.values()
		rank_list.sort(key = lambda x:x[3], reverse=True)
		select_list = rank_list[0:10]
		for roleId, _ in self.join_roleid_set.iteritems():
			member = cRoleMgr.FindRoleByRoleID(roleId)
			if not member:
				continue
			member.SendObj(Duty_Union_Member_Point_Rank, select_list)
			member.SendObj(Duty_Send_Union_Total_Point, [self.name, self.total_point])
	
	def SendPersonReward(self):
		'''
		发工会成员排行奖励
		'''
		rank_list = self.personal_point.values()
		if not rank_list:
			return
		rank_list.sort(key = lambda x:x[3], reverse=True)
		DOC = DukeOnDutyConfig.PERSON_RANK_REWARD_DICT.get
		rank = 0
		RC = RewardBuff.CalNumber
		RD = RewardBuff.enDukeOnDuty
		with DutyPersonRankReward:
			for data in rank_list:
				money = None
				awardEnum = None
				rank += 1
				roleId = data[0]
				level = data[2]
				if rank > 10:
					money, awardEnum = DOC(11).GetRewardByLevel(level)
				else:
					money, awardEnum = DOC(rank).GetRewardByLevel(level)
				if money:
					AwardMgr.SetAward(roleId, awardEnum, money = RC(RD, money))
	
	def SetTitle(self):
		if not self.personal_point:
			return
		for roleId, _ in self.personal_point.iteritems():
			Title.AddTitle(roleId, DukeOnDutyDefine.DUKE_TITLE_ID)
		
	def SetBuffID(self, role,buffId):
		'''
		设置buff
		@param role:
		@param buffId:
		'''
		if self.buff:
			if self.buff >= buffId:
				return
		self.buff = buffId
		for roleId, _ in self.join_roleid_set.iteritems():
			member = cRoleMgr.FindRoleByRoleID(roleId)
			if not member:
				continue
			member.SendObj(Duty_Send_Buff_Data, [self.buff, self.attack_buff, self.camp])
		cRoleMgr.Msg(11, 0, GlobalPrompt.DUKE_BUFF_MSG % (self.name, role.GetRoleName(), buffId))
		
	def GetBuff(self):
		'''
		获取buff
		'''
		return self.buff
	
	def add_attack_buff(self, buffId):
		'''
		设置连破buff
		@param buffId:
		'''
		if not self.camp:
			return
		self.attack_buff = buffId
		for roleId, _ in self.join_roleid_set.iteritems():
			member = cRoleMgr.FindRoleByRoleID(roleId)
			if not member:
				continue
			member.SendObj(Duty_Send_Buff_Data, [self.buff, self.attack_buff, self.camp])
				
	def GetAttackBuff(self):
		'''
		获取连破buff
		'''
		return self.attack_buff
#=======================================================
def RoleExitDuke(role, msg):
	'''
	玩家请求退出城主轮值
	@param role:
	@param msg:
	'''
	global ROLE_FIGHT_DICT
	global ATTACK_PLAYER_DICT
	global DEFENCE_PLAYER_DICT
	roleId = role.GetRoleID()
	if role.GetSceneID() == EnumGameConfig.DUKE_SCENE_ID:
		#清除玩家战斗记录
		if roleId in ROLE_FIGHT_DICT:
			del ROLE_FIGHT_DICT[roleId]
		#将玩家从战斗队列中去出
		if roleId in DEFENCE_PLAYER_DICT:
			del DEFENCE_PLAYER_DICT[roleId]
		if roleId in ATTACK_PLAYER_DICT:
			del ATTACK_PLAYER_DICT[roleId]	
		if roleId in ROLE_JOIN_DUKE:
			ROLE_JOIN_DUKE.remove(roleId)
		role.BackPublicScene()

def RoleJoinDuke(role, msg):
	'''
	玩家请求进入城主轮值
	@param role:
	@param msg:
	'''
	global IS_PREPARE
	if not IS_PREPARE:
		return
	#已经在此场景
	if role.GetSceneID() == EnumGameConfig.DUKE_SCENE_ID:
		return
	#需要等级
	if role.GetLevel() < DukeOnDutyDefine.LIMIT_LEVLE:
		role.Msg(2, 0, GlobalPrompt.DUKE_NO_PER)
		return	
	#传送前判断是否能进入传送状态
	if not Status.CanInStatus(role, EnumInt1.ST_TP):
		return
	
	if role.GetCD(EnumCD.UnionDukeCD):
		role.Msg(2, 0, GlobalPrompt.DUKE_NOT_JION_MSG)
		return
	#没公会
	unionID = role.GetUnionID()
	if not unionID:
		role.Msg(2, 0, GlobalPrompt.DUKE_NO_PER)
		return
	#在进入的时候再清理次城主buff
	SetRoleBuff(role, (0, 0, 0))
	global ATTACK_UNION_LIST
	global DEFENCE_PLAYER_LIST
	global UNION_OBJ
	global ROLE_FIGHT_DICT
	#工会不在攻守列表
	if unionID not in ATTACK_UNION_LIST and unionID not in DEFENCE_UNION_LIST:
		role.Msg(2, 0, GlobalPrompt.DUKE_NO_PER)
		return
	UnionObj = role.GetUnionObj()
	roleId = role.GetRoleID()	
	if roleId not in ROLE_ID_DUKE:#当天8点以后进工会的玩家
		role.Msg(2, 0, GlobalPrompt.DUKE_NO_PER)
		return
	#清除玩家战斗记录
	if roleId in ROLE_FIGHT_DICT:
		del ROLE_FIGHT_DICT[roleId]
	if roleId not in ROLE_JOIN_DUKE:
		ROLE_JOIN_DUKE.append(roleId)
	if IS_START:#假如活动开启
		if roleId in ATTACK_PLAYER_DICT:
			del ATTACK_PLAYER_DICT[roleId]
		if roleId in DEFENCE_PLAYER_DICT:
			del DEFENCE_PLAYER_DICT[roleId]
		if role.GetCD(EnumCD.Duty_CD) > 0:
			role.SetCD(EnumCD.Duty_CD, 0)
		role.SetCD(EnumCD.JOIN_Duty_CD, EnumGameConfig.FIGHT_LOST_CD)
	#没工会对象
	if unionID not in UNION_OBJ:
		if unionID in ATTACK_UNION_LIST:
			UNION_OBJ[unionID] = GangOnDuty(unionID, UnionObj.name, 1)
		if unionID in DEFENCE_UNION_LIST:
			UNION_OBJ[unionID] = GangOnDuty(unionID, UnionObj.name, 0)
	unionObj = UNION_OBJ[unionID]
	if roleId not in unionObj.join_roleid_set:
		unionObj.join_roleid_set[roleId] = [roleId, role.GetLevel()]
	if roleId not in unionObj.personal_point:
		unionObj.personal_point[roleId] = [roleId, role.GetRoleName(), role.GetLevel(), 0]
	attackState = unionObj.camp
	if attackState:#是攻方
		defence_times = DukeOnDuty.get(2)
		times = min(DukeOnDutyDefine.MAX_BUFF_KEEP_DAY, defence_times)
		cfg = DukeOnDutyConfig.ATTACK_BUFF_INFO_DICT.get(times)
		if cfg:
			attack_buff = unionObj.GetAttackBuff()
			if not attack_buff:
				unionObj.add_attack_buff(times)
		if unionID not in UNION_POINT_DICT:#加入攻方积分缓存
			UNION_POINT_DICT[unionID] = [unionID, UnionObj.name, 0]
	x, y = GetPos(attackState)
	#将玩家传送进场景
	role.Revive(EnumGameConfig.DUKE_SCENE_ID, x, y)
	SynRole(role, unionObj)
	
	if role.GetRoleID() not in RoleSet:
		RoleSet.add(role.GetRoleID())
		Event.TriggerEvent(Event.QQidip_Eve, role, QQEventDefine.QQ_Duty)
	
	#圣诞转转乐
	Event.TriggerEvent(Event.Eve_IncChristmasMountotteryTime, role, EnumGameConfig.Source_DukeOnDuty)
	
	#王者公测奖励狂翻倍触发任务进度
	Event.TriggerEvent(Event.Eve_WangZheCrazyRewardTask, role, (EnumGameConfig.WZCR_Task_DukeOnDuty, True))
	#激情活动奖励狂翻倍触发任务进度
	Event.TriggerEvent(Event.Eve_PassionMultiRewardTask, role, (EnumGameConfig.PassionMulti_Task_DukeOnDuty, True))
	#元旦金猪活动任务进度
	Event.TriggerEvent(Event.Eve_NewYearDayPigTask, role, (EnumGameConfig.NewYearDay_Task_DukeOnDuty, True))
	

def ClientAddBuff(role, msg):
	'''
	客户端请求升级buff
	@param role:
	@param msg:
	'''
	buffId = msg
	cfg = DukeOnDutyConfig.BUFF_INFO_DICT.get(buffId)
	if not cfg:
		print "can not find key=%s in BuffInfo" % buffId
		return
	need_ZDL = cfg[2]
	ZDL = role.GetZDL()
	if ZDL < need_ZDL:
		return
	unionID = role.GetUnionID()
	UnionObj = role.GetUnionObj()
	
	roleId = role.GetRoleID()
	if unionID not in UNION_OBJ:
		if unionID in ATTACK_UNION_LIST:
			UNION_OBJ[unionID] = GangOnDuty(unionID, UnionObj.name, 1)
		else:
			UNION_OBJ[unionID] = GangOnDuty(unionID, UnionObj.name, 0)
		if roleId not in UNION_OBJ[unionID].join_roleid_set:
			UNION_OBJ[unionID].join_roleid_set[roleId] = [roleId, role.GetLevel()]
	UNION_OBJ[unionID].SetBuffID(role, buffId)

def ClientQuickCD(role, msg):
	'''
	客户端请求加速CD
	@param role:
	@param msg:
	'''
	cd = role.GetCD(EnumCD.Duty_CD)
	if cd <= 0:
		return
	times = role.GetDI8(EnumDayInt8.DukeDutyCDTimes)
	cfg = DukeOnDutyConfig.CD_COST_DICT.get(times+1)
	if not cfg:
		print "GE_EXC,can not find times(%s) in CDCost" % times
		return
	
	global ATTACK_UNION_LIST
	unionId = role.GetUnionID()
	Reduced = 100
	if unionId in ATTACK_UNION_LIST:
		defence_times = DukeOnDuty.get(2)
		if defence_times == 0:
			defence_times = 1
		times = min(DukeOnDutyDefine.MAX_BUFF_KEEP_DAY, defence_times)
		costcfg = DukeOnDutyConfig.QUICK_CD_DICT.get(times)
		if not costcfg:
			print "GE_EXC,can not find times(%s) in DukeOnDutyConfig.ATTACK_BUFF_INFO_DICT,ClientQuickCD" % times
			return
		Reduced = costcfg.reduced
	
	cost = int(cfg.cost * (Reduced / 100.0))
	if role.GetRMB() < cost:
		return
	with DukeQuackCDCost:
		role.IncDI8(EnumDayInt8.DukeDutyCDTimes, 1)
		role.DecRMB(cost)
		role.SetCD(EnumCD.Duty_CD, 0)
	
def ClientAttackStatue(role, msg):	
	'''
	客户端请求攻击雕像
	@param role:
	@param msg:
	'''
	global IS_START
	global IS_BOSS_EXISTED
	global STATUE_HP
	global DEFENCE_PLAYER_DICT
	if not IS_START:
		role.Msg(2, 0, GlobalPrompt.DUKE_NO_START)
		return
	if not IS_BOSS_EXISTED:
		return
	unionId = role.GetUnionID()
	if not unionId:
		role.BackPublicScene()
		return
	if Status.IsInStatus(role, EnumInt1.ST_FightStatus):
		return
	if DEFENCE_PLAYER_DICT:
		MatchingPlayer(role)
		return
	if role.GetCD(EnumCD.Duty_CD) > 0:
		role.Msg(2, 0, GlobalPrompt.DUKE_ON_CD)
		return
	if role.GetCD(EnumCD.JOIN_Duty_CD) > 0:
		role.Msg(2, 0, GlobalPrompt.DUKE_ON_CD)
		return
	maxHp = GetMaxBossHP(IS_BOSS_EXISTED)
	if IS_BOSS_EXISTED == 1:#攻击外城雕像
		PVE_DukeWar(DukeOnDutyDefine.BOSS_FIGHT_TYPE,role, DukeOnDutyDefine.BOSS_CAMP, maxHp, STATUE_HP, unionId, 1)

	elif IS_BOSS_EXISTED == 2:#攻击内城雕像
		PVE_DukeWar(DukeOnDutyDefine.BOSS_FIGHT_TYPE,role, DukeOnDutyDefine.BOSS_CAMP, maxHp, STATUE_HP, unionId, 2)

def FightRolePVP(role, msg):
	'''
	客户端请求攻击
	@param role:
	@param msg:
	'''
	global ATTACK_PLAYER_DICT
	global DEFENCE_PLAYER_DICT
	roleIdB, state = msg
	if not roleIdB:
		return
	roleId = role.GetRoleID()
	roleB = cRoleMgr.FindRoleByRoleID(roleIdB)
	if roleIdB == roleId:
		return
	if not roleB:
		if roleIdB in ATTACK_PLAYER_DICT:
			del ATTACK_PLAYER_DICT[roleIdB]
		if roleIdB in DEFENCE_PLAYER_DICT:
			del DEFENCE_PLAYER_DICT[roleIdB]
		role.Msg(2, 0, GlobalPrompt.DUKE_PLAYER_LOST)
		return
	if roleB.GetCD(EnumCD.Duty_CD) > 0:
		role.Msg(2, 0, GlobalPrompt.DUKE_PLAYER_LOST)
		return
	if roleB.GetCD(EnumCD.JOIN_Duty_CD) > 0:
		role.Msg(2, 0, GlobalPrompt.DUKE_PLAYER_LOST)
		return
	if role.GetCD(EnumCD.Duty_CD) > 0:
		role.Msg(2, 0, GlobalPrompt.DUKE_ON_CD)
		return
	if role.GetCD(EnumCD.JOIN_Duty_CD) > 0:
		role.Msg(2, 0, GlobalPrompt.DUKE_ON_CD)
		return
	if roleId not in ATTACK_PLAYER_DICT and roleId not in DEFENCE_PLAYER_DICT:
		return
	if 0 == state:#我是防守者
		if roleId in ATTACK_PLAYER_DICT:#同为攻击者
			return
		if roleIdB not in ATTACK_PLAYER_DICT:
			role.Msg(2, 0, GlobalPrompt.DUKE_PLAYER_LOST)
			return
	elif 1 == state:#我是攻击者
		if roleId in DEFENCE_PLAYER_DICT:
			return
		if roleIdB not in DEFENCE_PLAYER_DICT:
			role.Msg(2, 0, GlobalPrompt.DUKE_PLAYER_LOST)
			return	
	#战斗
	PVP_DukeWar(role, roleB, DukeOnDutyDefine.PVP_FIGHT_TYPE, AfterPlay2, Afterfight, AfterFightLevel)
	
def ClientClosePanel(role, msg):
	'''
	关闭战场界面
	@param role:
	@param msg:
	'''
	global ATTACK_PLAYER_DICT
	global DEFENCE_PLAYER_DICT
	
	roleId = role.GetRoleID()
	#清除玩家所在队列
	if roleId in ATTACK_PLAYER_DICT:
		del ATTACK_PLAYER_DICT[roleId]
	if roleId in DEFENCE_PLAYER_DICT:
		del DEFENCE_PLAYER_DICT[roleId]

def FreshWarPanel(role, msg):		
	'''
	客户端请求刷新战场界面
	@param role:
	@param msg:
	'''
	global IS_START
	global IS_BOSS_EXISTED
	if not IS_START:
		return
	if not IS_BOSS_EXISTED:
		return
	MatchingPlayer(role)
	
def ClickOKBtn(role, msg):
	'''
	客户端点击确认传送，只针对击败外城雕像
	@param role:
	@param callargv:
	@param regparam:
	'''
	global ATTACK_UNION_LIST
	global DEFENCE_UNION_LIST
	unionId = role.GetUnionID()
	if role.GetCD(EnumCD.Duty_CD) > 0:
		role.SetCD(EnumCD.Duty_CD, 0)
	if unionId in ATTACK_UNION_LIST:
		X,Y = DukeOnDutyDefine.ATTACK_POS2
		role.JumpPos(X, Y)
	if unionId in DEFENCE_UNION_LIST:
		X,Y = DukeOnDutyDefine.DEFENCE_POS2
		role.JumpPos(X, Y)
#=======================================================
@NPCServerFun.RegNPCServerOnClickFun(1081)
def OnClick_1081(role, npc):
	global IS_BOSS_EXISTED
	global IS_START
	#点击城主
	unionId = role.GetUnionID()
	if not unionId:
		role.BackPublicScene()
		return
	#还没开始
	if IS_START is False:
		role.Msg(2, 0, GlobalPrompt.DUKE_NO_START)
		return
	#Boss不存在
	if 0 == IS_BOSS_EXISTED:
		return
	roleId = role.GetRoleID()
	if roleId in ATTACK_PLAYER_DICT or roleId in DEFENCE_PLAYER_DICT:
		return
	#CD时间
	if role.GetCD(EnumCD.Duty_CD) > 0 or role.GetCD(EnumCD.JOIN_Duty_CD) > 0:
		role.Msg(2, 0, GlobalPrompt.DUKE_ON_CD)
		return
	MatchingPlayer(role)

@NPCServerFun.RegNPCServerOnClickFun(3008)
def OnClick_3000(role, npc):
	#点击守护神
	global UNION_OBJ
	unionId = role.GetUnionID()
	if not unionId:
		role.BackPublicScene()
		return
	if unionId not in UNION_OBJ:
		return
	if not UNION_OBJ[unionId].camp:#只有攻方可以打
		return
	#还没开始
	if IS_START is False:
		role.Msg(2, 0, GlobalPrompt.DUKE_NO_START)
		return
	#Boss不存在
	if PATRON_SAINT_OBJ is False:
		return
	#CD时间
	if role.GetCD(EnumCD.Duty_CD) > 0 or role.GetCD(EnumCD.JOIN_Duty_CD) > 0:
		role.Msg(2, 0, GlobalPrompt.DUKE_ON_CD)
		return
	maxHp = GetMaxBossHP(3)
	PVEPatronSaint(DukeOnDutyDefine.BOSS_FIGHT_TYPE2, role, DukeOnDutyDefine.BOSS_CAMP2, maxHp, STATUE_HP, unionId)
		
def PVP_DukeWar(roleA, roleB, ftype, afterplay = None, afterfight = None, afterleave = None, regparam = None):
	'''
	PVP战斗
	@param roleA:
	@param roleB:
	@param ftype:
	@param leave_fun:
	@param backFun:
	@param regparam:
	'''
	# 判断战斗状态互斥
	if Status.IsInStatus(roleA, EnumInt1.ST_FightStatus):
		return
	roleIdA = roleA.GetRoleID()
	roleIdB = roleB.GetRoleID()
	state_B = False
	if Status.IsInStatus(roleB, EnumInt1.ST_FightStatus):
		if not _SAVE_ROLE_HP.get(roleIdB):
			roleA.Msg(2, 0, GlobalPrompt.DUKE_PLAYER_LOST)
			return
		state_B = True
	global SAVE_FIGHT_DATA
	if roleIdA not in SAVE_FIGHT_DATA:
		roleA_maxhp = GetRoleMaxHp(roleA)
		fightA_data = Middle.GetRoleData(roleA, True)
		SAVE_FIGHT_DATA[roleIdA] = [fightA_data, roleA_maxhp]
	if roleIdB not in SAVE_FIGHT_DATA:
		roleB_maxhp = GetRoleMaxHp(roleB)
		fightB_data = Middle.GetRoleData(roleB, True)
		SAVE_FIGHT_DATA[roleIdB] = [fightB_data, roleB_maxhp]
	#战斗
	fight = Fight.Fight(ftype)
	fight.pvp = True
	#2创建两个阵营
	left, right = fight.create_camp()
	roleA_HP = _SAVE_ROLE_HP.setdefault(roleA.GetRoleID(), {})
	roleB_HP = _SAVE_ROLE_HP.setdefault(roleB.GetRoleID(), {})
	#绑定血量
	left.bind_hp(roleA_HP)
	right.bind_hp(roleB_HP)
	#在阵营中创建战斗单位
	left.create_online_role_unit(roleA,fightData = SAVE_FIGHT_DATA.get(roleIdA)[0], use_px = True)
	if state_B:
		right.create_outline_role_unit(SAVE_FIGHT_DATA.get(roleIdB)[0])
	else:
		right.create_online_role_unit(roleB, fightData = SAVE_FIGHT_DATA.get(roleIdB)[0], use_px = True)
	fight.after_fight_fun = afterfight
	fight.after_play_fun = afterplay
	fight.on_leave_fun = afterleave
	if state_B:
		fight.after_fight_param = (roleA, roleB, True)
		fight.after_play_param = (roleA, roleB, True)
	else:
		fight.after_fight_param = (roleA, roleB, False)
		fight.after_play_param = (roleA, roleB, False)
	#=============玩家A buff==============
	unionIdA = roleA.GetUnionID()
	if unionIdA not in UNION_OBJ:
		return
	buff_idA = UNION_OBJ[unionIdA].GetBuff()
	if buff_idA:
		AddBuffEffect(left, buff_idA, 1)
	attack_buffA = UNION_OBJ[unionIdA].GetAttackBuff()
	if attack_buffA:
		AddBuffEffect(left, attack_buffA, 2)
	#=============玩家B buff==============
	unionIdB = roleB.GetUnionID()
	if unionIdB not in UNION_OBJ:
		return
	buff_idB = UNION_OBJ[unionIdB].GetBuff()
	if buff_idB:
		AddBuffEffect(right, buff_idB, 1)
	attack_buffB = UNION_OBJ[unionIdB].GetAttackBuff()
	if attack_buffB:
		AddBuffEffect(right, attack_buffB, 2)
	fight.start()
	#============战斗结果============
	if fight.result is None:
		return
	global IS_START
	#活动是否已经结束
	if IS_START is False:
		return

	win_role = None
	lost_role = None
	lost_zdl = 0
	if fight.result == -1:#战斗失败
		win_role = roleB
		lost_role = roleA
		lost_zdl = roleA.GetZDL()
	else:
		#战斗胜利
		win_role = roleA
		lost_role = roleB
		lost_zdl = roleB.GetZDL()
	if win_role:#胜利方
		win_point = 0
		duke = DukeOnDutyConfig.ZDL_POINT_DICT
		for key, cfg in duke.iteritems():
			if key[0] <= lost_zdl < key[1]:
				win_point = cfg.point
				break
		unionId = win_role.GetUnionID()
		if unionId not in UNION_OBJ:
			return
		if win_role == roleA:
			UNION_OBJ[unionId].AddPoint(1, win_role, lost_role.GetRoleName(), win_point)
		else:
			UNION_OBJ[unionId].AddPoint(5, win_role, lost_role.GetRoleName(), win_point)
		winID = win_role.GetRoleID()
		max_hp = SAVE_FIGHT_DATA.get(winID)[1]
		remaining_hp = _SAVE_ROLE_HP.get(winID)
		if remaining_hp:
			total_hp = remaining_hp.get('total_hp')
			win_role.SendObj(Duty_Send_role_HP, [max_hp, total_hp])
	if lost_role:#失败方
		unionId_B = lost_role.GetUnionID()
		if unionId_B not in UNION_OBJ:
			return
		roleId_B = lost_role.GetRoleID()
		global ATTACK_PLAYER_DICT
		global DEFENCE_PLAYER_DICT
		global ATTACK_UNION_LIST
		global DEFENCE_UNION_LIST
		global STATUE_HP
		#将玩家移除战场
		if roleId_B in ATTACK_PLAYER_DICT:
			del ATTACK_PLAYER_DICT[roleId_B]
		if roleId_B in DEFENCE_PLAYER_DICT:
			del DEFENCE_PLAYER_DICT[roleId_B]
		MatchingPlayer(win_role)	
		if roleId_B in _SAVE_ROLE_HP:
			_SAVE_ROLE_HP[roleId_B] = {}
		unionObj = UNION_OBJ[unionId_B]
		if lost_role == roleA:
			unionObj.AddPoint(0, lost_role, win_role.GetRoleName(), DukeOnDutyDefine.LOST_POINT_PVP)
		else:
			unionObj.AddPoint(4, lost_role, win_role.GetRoleName(), DukeOnDutyDefine.LOST_POINT_PVP)		
		#失败方重新存储战斗数据
		role_maxhp = GetRoleMaxHp(lost_role)
		fightA_data = Middle.GetRoleData(lost_role, True)
		SAVE_FIGHT_DATA[roleId_B] = [fightA_data, role_maxhp]
		#增加失败CD
		lost_role.SetCD(EnumCD.Duty_CD, EnumGameConfig.FIGHT_LOST_CD)
		camp = unionObj.camp
		x, y = GetPos(camp)
		lost_role.JumpPos(x, y)
		lost_role.SendObj(Duty_Send_role_HP, [role_maxhp, role_maxhp])
		lost_role.SendObj(Duty_Send_Close_War, 1)
	
def PVE_DukeWar(ftype, role, mid, bossmaxhp, bosshp, unionId,  index = 1):
	'''
	与雕像战斗
	@param ftype
	@param role:
	@param mid:
	@param bossmaxhp:
	@param bosshp:
	@param unionId
	@param leave_fun:
	@param backFun:
	@param regparam:
	'''
	global STATUE_HP
	global IS_BOSS_EXISTED
	global BOSS_OBJ
	global _SAVE_ROLE_HP
	global ROLE_JOIN_DUKE
	# 判断战斗状态互斥
	if Status.IsInStatus(role, EnumInt1.ST_FightStatus):
		return
	if unionId not in UNION_OBJ:
		return
	role.SendObj(Duty_Send_Close_War, 1)
	global SAVE_FIGHT_DATA
	roleId = role.GetRoleID()
	if roleId not in SAVE_FIGHT_DATA:
		role_maxhp = GetRoleMaxHp(role)
		fight_data = Middle.GetRoleData(role, True)
		SAVE_FIGHT_DATA[roleId] = [fight_data, role_maxhp]
	buff = UNION_OBJ[unionId].GetBuff()
	attack_buff = UNION_OBJ[unionId].GetAttackBuff()
		
	#战斗流程
	fight = Fight.Fight(ftype)	
	left, right = fight.create_camp()
	left.create_online_role_unit(role, fightData = SAVE_FIGHT_DATA.get(roleId)[0])#玩家不可操控
	if buff:
		AddBuffEffect(left, buff, 1)
	if attack_buff:
		AddBuffEffect(left, attack_buff, 2)
	role_HP = _SAVE_ROLE_HP.setdefault(role.GetRoleID(), {})
	#绑定血量
	left.bind_hp(role_HP)
	right.create_monster_camp_unit(mid)
	for u in right.pos_units.itervalues():
		u.max_hp = bossmaxhp
		u.hp = bosshp
	fight.after_fight_fun = AfterFightPVE
	fight.after_fight_param = (1, STATUE_HP, unionId)
	fight.after_play_fun = AfterPlay #需要客户端播发完
	fight.after_play_param = (STATUE_HP, role)
	fight.start()
	
#=======战斗后处理============
	if fight.result is None:
		return
	unit = fight.right_camp.get_least_hp_units(1)
	hurt = 0	#玩家造成的伤害
	if unit:
		if fight.result == 1:#战斗胜利
			hurt = STATUE_HP
			STATUE_HP = 0
		else:#战斗失败
			hurt = STATUE_HP - unit[0].hp
			#保存Boss血量
			if STATUE_HP:
				if STATUE_HP >= hurt:
					STATUE_HP -= hurt
				else:
					STATUE_HP = 0
	else:#不存在，貌似怪物已经干掉了
		STATUE_HP = 0
	role_maxhp = GetRoleMaxHp(role)
	#战斗失败
	if STATUE_HP > 0:
		RemoveRole(role, unionId)
		if roleId in _SAVE_ROLE_HP:
			_SAVE_ROLE_HP[roleId] = {}
		fight_data = Middle.GetRoleData(role, True)
		SAVE_FIGHT_DATA[roleId] = [fight_data, role_maxhp]
		role.SetCD(EnumCD.Duty_CD, EnumGameConfig.FIGHT_LOST_CD)
		role.SendObj(Duty_Send_role_HP, [role_maxhp, role_maxhp])
	#战斗胜利
	elif STATUE_HP == 0:
		if not IS_START:
			return
		if index == 1:#击败外城雕像
			if IS_BOSS_EXISTED == 1:
				if IS_START:
					CreateDuke(2)
					TP_ALL_PLAYER()
		elif index == 2:#击败内城雕像
			if IS_BOSS_EXISTED == 2:
				IS_BOSS_EXISTED = 0
				scene = cSceneMgr.SearchPublicScene(EnumGameConfig.DUKE_SCENE_ID)
				if scene:
					scene.DestroyNPC(BOSS_OBJ.GetNPCID())
					BOSS_OBJ = None
					#创建守护神
					x, y = DukeOnDutyDefine.BOSS_POS_3
					global PATRON_SAINT_OBJ
					PATRON_SAINT_OBJ = scene.CreateNPC(DukeOnDutyDefine.BOSS_ID_2, x, y, DukeOnDutyDefine.BOSS_TOWARD3, 1)
					#设置守护神血量
					SetBossHP(3)
					for role_id in ROLE_JOIN_DUKE:
						c_role = cRoleMgr.FindRoleByRoleID(role_id)
						if not c_role:
							continue
						c_role.SendObj(Duty_After_Fight_Data, 0)
		remaining_hp = _SAVE_ROLE_HP.get(roleId)
		if remaining_hp:
			total_hp = remaining_hp.get('total_hp')
			total_maxhp = SAVE_FIGHT_DATA.get(roleId)[1]
			role.SendObj(Duty_Send_role_HP, [total_maxhp, total_hp])
		else:
			role.SendObj(Duty_Send_role_HP, [role_maxhp, role_maxhp])
	else:
		return
	
def PVEPatronSaint(ftype, role, mid, bossmaxhp, bosshp, unionId):
	#攻击守护神
	global BOSS_OBJ
	global SAVE_FIGHT_DATA
	global STATUE_HP
	global PATRON_SAINT_OBJ
	global ROLE_JOIN_DUKE
	# 判断战斗状态互斥
	if Status.IsInStatus(role, EnumInt1.ST_FightStatus):
		return
	if unionId not in UNION_OBJ:
		return
	roleId = role.GetRoleID()
	role_maxhp = GetRoleMaxHp(role)
	if roleId not in SAVE_FIGHT_DATA:
		fight_data = Middle.GetRoleData(role, True)
		SAVE_FIGHT_DATA[roleId] = [fight_data, role_maxhp]
	role.SendObj(Duty_Send_Close_War, 1)
	buff = UNION_OBJ[unionId].GetBuff()
	attack_buff = UNION_OBJ[unionId].GetAttackBuff()
		
	#战斗流程
	fight = Fight.Fight(ftype)
	left, right = fight.create_camp()
	left.create_online_role_unit(role,fightData = SAVE_FIGHT_DATA.get(roleId)[0])
	if buff:
		AddBuffEffect(left, buff, 1)
	if attack_buff:
		AddBuffEffect(left, attack_buff, 2)

	right.create_monster_camp_unit(mid)
	for u in right.pos_units.itervalues():
		u.max_hp = bossmaxhp
		u.hp = bosshp
	fight.after_fight_fun = AfterFightPVE
	fight.after_fight_param = (2, STATUE_HP, unionId)
	fight.after_play_fun = AfterPlay
	fight.after_play_param = (0, role)
	fight.start()
	#=====战斗后处理=========
	if fight.result is None:
		return
	unit = fight.right_camp.get_least_hp_units(1)
	hurt = 0
	if unit:
		if fight.result == 1:#战斗胜利
			hurt = STATUE_HP
			STATUE_HP = 0
		else:#战斗失败
			hurt = STATUE_HP - unit[0].hp
			#保存Boss血量
			if STATUE_HP:
				if STATUE_HP >= hurt:
					STATUE_HP -= hurt
				else:
					STATUE_HP = 0
	else:#不存在，貌似怪物已经干掉了
		hurt = STATUE_HP
		STATUE_HP = 0

	X, Y = DukeOnDutyDefine.ATTACK_POS2
	
	if STATUE_HP:
		fight_data = Middle.GetRoleData(role, True)
		SAVE_FIGHT_DATA[roleId] = [fight_data, role_maxhp]
		role.JumpPos(X, Y)
		role.SetCD(EnumCD.Duty_CD, EnumGameConfig.FIGHT_LOST_CD)
		role.SendObj(Duty_Send_role_HP, [role_maxhp, role_maxhp])
	else:#删除守护神
		scene = cSceneMgr.SearchPublicScene(EnumGameConfig.DUKE_SCENE_ID)
		if scene:
			if not PATRON_SAINT_OBJ:
				return
			scene.DestroyNPC(PATRON_SAINT_OBJ.GetNPCID())
			PATRON_SAINT_OBJ = None
			for role_id in ROLE_JOIN_DUKE:
				c_role = cRoleMgr.FindRoleByRoleID(role_id)
				if not c_role:
					continue
				c_role.SendObj(Duty_After_Fight_Data, -1)
			cRoleMgr.Msg(1, 0, GlobalPrompt.DUKE_GAME_OVER)
#=======================================================
def AddBuffEffect(camp, buff, bufftype):
	#增加buff效果
	info = None
	if bufftype == 1:#为普通buff
		info = DukeOnDutyConfig.BUFF_INFO_DICT.get(buff)
	else:
		info = DukeOnDutyConfig.ATTACK_BUFF_INFO_DICT.get(buff)
	if not info:
		return
	pt1, value1 = info[0]
	if pt1 == PropertyEnum.damageupgrade:
		for u in camp.pos_units.itervalues():
			u.damage_upgrade_rate += float(value1) / 10000
	pt2, value2 = info[1]
	if pt2 == PropertyEnum.damagereduce:
		for u in camp.pos_units.itervalues():
			u.damage_reduce_rate += float(value2) / 10000
			
def AfterFightPVE(fight):
	#回调触发
	if fight.result is None:
		return

	index, oldhp, unionId = fight.after_fight_param
	
	unit = fight.right_camp.get_least_hp_units(1)
	hurt = 0	#玩家造成的伤害

	if fight.result == 1:#战斗胜利
		hurt = oldhp
	else:#战斗失败
		if unit:
			hurt = oldhp - unit[0].hp
		else:
			hurt = oldhp
	roles = fight.left_camp.roles
	if not roles:
		return
	role = list(roles)[0]
	
	point = GetPointByHurt(role, hurt)
	roleId = role.GetRoleID()
	if index == 1:
		UNION_OBJ[unionId].AddPoint(2, role, '', point)
		fight.set_fight_statistics(roleId, EnumFightStatistics.EnumDukePoint, point)
	else:
		UNION_OBJ[unionId].AddPoint(3, role, '', point)
		fight.set_fight_statistics(roleId, EnumFightStatistics.EnumDukePoint, point)
	
def GetRoleMaxHp(role):
	'''
	获取玩家最大血量
	@param role:
	'''	
	role_data, hero_data = Middle.GetRoleData(role, True)
	total_maxhp = role_data.get(Middle.MaxHP)
	if hero_data:
		for _, data in hero_data.iteritems():
			total_maxhp += data.get(Middle.MaxHP)
	return total_maxhp
		
def AfterPlay(fight):
	pass

def AfterFightLevel(fight, role):
	pass
	
def AfterPlay2(fight):
	pass
		
def Afterfight(fight):
	roleA ,roleB, state = fight.after_fight_param
	if state and fight.result == 1:#B失败了且在战斗中
		roleB.SetCD(EnumCD.Duty_CD, EnumGameConfig.FIGHT_LOST_CD)
	roleIdA = roleA.GetRoleID()
	roleIdB = roleB.GetRoleID()
	win_point = 0
	lost_zdl = 0
	fightresult = False
	if fight.result == -1:
		lost_zdl = roleA.GetZDL()
		fightresult = True
	elif fight.result == 1:
		lost_zdl = roleB.GetZDL()
	else:
		return
	duke = DukeOnDutyConfig.ZDL_POINT_DICT
	for key, cfg in duke.iteritems():
		if key[0] <= lost_zdl < key[1]:
			win_point = cfg.point
			break
	if fightresult:
		fight.set_fight_statistics(roleIdA, EnumFightStatistics.EnumDukePoint, DukeOnDutyDefine.LOST_POINT_PVP)
		fight.set_fight_statistics(roleIdB, EnumFightStatistics.EnumDukePoint, win_point)
	else:
		fight.set_fight_statistics(roleIdB, EnumFightStatistics.EnumDukePoint, DukeOnDutyDefine.LOST_POINT_PVP)
		fight.set_fight_statistics(roleIdA, EnumFightStatistics.EnumDukePoint, win_point)
		
def RemoveRole(role, unionId):
	#将攻方玩家从列表中移除
	global ATTACK_PLAYER_DICT
	global IS_BOSS_EXISTED
	global _SAVE_ROLE_HP
	
	roleId = role.GetRoleID()
	if roleId in _SAVE_ROLE_HP:
		_SAVE_ROLE_HP[roleId] = {}
	if roleId in ATTACK_PLAYER_DICT:
		del ATTACK_PLAYER_DICT[roleId]
	if IS_BOSS_EXISTED == 1:
		x, y = DukeOnDutyDefine.ATTACK_POS1
	else:
		x, y = DukeOnDutyDefine.ATTACK_POS2
	role.JumpPos(x, y)

def TP_ALL_PLAYER():
	'''
	通知场景玩家
	'''
	global ROLE_JOIN_DUKE
	global ATTACK_PLAYER_DICT
	global DEFENCE_PLAYER_DICT
	
	for roleId in ROLE_JOIN_DUKE:
		role = cRoleMgr.FindRoleByRoleID(roleId)
		if not role:
			continue
		if role.GetCD(EnumCD.Duty_CD) > 0:
			role.SetCD(EnumCD.Duty_CD, 0)
		if roleId in ATTACK_PLAYER_DICT:
			role.SetCD(EnumCD.JOIN_Duty_CD, 60)
		else:
			role.SetCD(EnumCD.JOIN_Duty_CD, 55)
		sendList, afterFightHp, leader_name = GetAllData()
		maxHp = 0
		if IS_BOSS_EXISTED:#雕像
			maxHp = GetMaxBossHP(IS_BOSS_EXISTED)
		if PATRON_SAINT_OBJ:#有守护神
			maxHp = GetMaxBossHP(3)
		role.SendObj(Duty_Send_Statu_HP, (sendList,[leader_name, maxHp, afterFightHp]))
		#雕像不存在且守护神也不存在
		if IS_BOSS_EXISTED ==0 and not PATRON_SAINT_OBJ:
			role.SendObj(Duty_After_Fight_Data, -1)
		else:
			role.SendObj(Duty_After_Fight_Data, IS_BOSS_EXISTED)

def SynRole(role, unionObj):
	#同步工会积分排行和工会成员积分排行，及boss血量
	global _SAVE_ROLE_HP
	global IS_BOSS_EXISTED

	roleId = role.GetRoleID()
	unionObj.Fresh_rank()
	SendInfoRole(role)
	buff = unionObj.GetBuff()
	attack_buff = unionObj.GetAttackBuff()
	if unionObj.camp:
		role.SendObj(Duty_Send_Buff_Data, [buff, attack_buff, 1])
	else:
		role.SendObj(Duty_Send_Buff_Data, [buff, attack_buff, 0])
	#玩家战斗数据
	total_maxhp = GetRoleMaxHp(role)
	if roleId in SAVE_FIGHT_DATA:
		total_maxhp = SAVE_FIGHT_DATA.get(roleId)[1]
	remaining_hp = _SAVE_ROLE_HP.get(roleId)
	if remaining_hp:
		total_hp = remaining_hp.get('total_hp')
		role.SendObj(Duty_Send_role_HP, [total_maxhp, total_hp])
	else:
		role.SendObj(Duty_Send_role_HP, [total_maxhp, total_maxhp])
	#雕像不存在且守护神也不存在
	if IS_BOSS_EXISTED ==0 and not PATRON_SAINT_OBJ:
		role.SendObj(Duty_After_Fight_Data, -1)
	else:
		role.SendObj(Duty_After_Fight_Data, IS_BOSS_EXISTED)
	
def GetPos(camp):
	global IS_BOSS_EXISTED
	if 1 == camp:
		if IS_BOSS_EXISTED == 1:#外城
			return DukeOnDutyDefine.ATTACK_POS1
		elif IS_BOSS_EXISTED == 2:#内城
			return DukeOnDutyDefine.ATTACK_POS2
		else:#出守护神
			return DukeOnDutyDefine.ATTACK_POS2
	else:
		if IS_BOSS_EXISTED == 1:
			return DukeOnDutyDefine.DEFENCE_POS1
		elif IS_BOSS_EXISTED == 2:
			return DukeOnDutyDefine.DEFENCE_POS2
		else:
			return DukeOnDutyDefine.DEFENCE_POS2
		
def SendResult(name , state):
	'''
	广播给场景中的玩家活动结果
	@param name:城主工会名
	@param state:1 代表攻方赢， 0 代表守方赢
	'''
	for roleId in ROLE_JOIN_DUKE:
		role = cRoleMgr.FindRoleByRoleID(roleId)
		if not role:
			continue
		role.SendObj(Duty_After_Duty_Fight_Result, [name, state])
	if state:
		cRoleMgr.Msg(3, 0, GlobalPrompt.DUKE_END_MSG2 % name)
	else:
		cRoleMgr.Msg(3, 0, GlobalPrompt.DUKE_END_MSG1 % name)

def MatchingPlayer(role):
	'''
	匹配队友和对手
	@param role:
	'''
	global ATTACK_PLAYER_DICT
	global DEFENCE_PLAYER_DICT
	unionId = role.GetUnionID()
	if not unionId or unionId not in UNION_OBJ:
		role.BackPublicScene()
		return
	unionObj = UNION_OBJ[unionId]
	roleId = role.GetRoleID()
	buff = unionObj.GetBuff()
	name =  role.GetRoleName()
	level = role.GetLevel()
	armyList = []
	if 1 == unionObj.camp:#攻方
		armyList = DEFENCE_PLAYER_DICT.values()
		if roleId not in ATTACK_PLAYER_DICT:
			ATTACK_PLAYER_DICT[roleId] = [roleId, name, level, buff]
	elif 0 == unionObj.camp:#守方
		armyList = ATTACK_PLAYER_DICT.values()
		if roleId not in DEFENCE_PLAYER_DICT:
			DEFENCE_PLAYER_DICT[roleId] = [roleId, name, level, buff]
	#将序列随机打乱
	random.shuffle(armyList)
	selected_list = armyList[0:8]
	role.SendObj(Duty_Send_player_data, selected_list)
		
def SendInfoRole(role):
	global IS_START
	sendList, afterFightHp, leader_name = GetAllData()
	maxHp = 0
	if IS_BOSS_EXISTED:
		maxHp = GetMaxBossHP(IS_BOSS_EXISTED)
	if PATRON_SAINT_OBJ:#有守护神
		maxHp = GetMaxBossHP(3)
	role.SendObj(Duty_Send_Data_Role, [sendList, [leader_name, maxHp, afterFightHp], IS_START])

def Per10Second(callargv, regparam):
	#每10秒跟新一次伤害排行和雕像血量
	global IS_START
	#判断是否结束
	if not IS_START:
		return
	#注册每10秒调用
	cComplexServer.RegTick(10, Per10Second)
	
	scene = cSceneMgr.SearchPublicScene(EnumGameConfig.DUKE_SCENE_ID)
	if not scene:
		return
	sendList, afterFightHp, leader_name = GetAllData()
	maxHp = 0
	if IS_BOSS_EXISTED:
		maxHp = GetMaxBossHP(IS_BOSS_EXISTED)
	if PATRON_SAINT_OBJ:#有守护神
		maxHp = GetMaxBossHP(3)
	#广播给场景内所有玩家
	cNetMessage.PackPyMsg(Duty_On_Show_Rank, (sendList,[leader_name, maxHp, afterFightHp]))
	cSceneMgr.BroadMsg(EnumGameConfig.DUKE_SCENE_ID)

def GetAllData():
	#排行榜排序
	rank_list = UNION_POINT_DICT.values()
	#对伤害进行排序
	rank_list.sort(key=lambda x:x[2], reverse=True)
	#发送前3名
	sendList = rank_list[0:3]
		
	#战斗后Boss血量
	afterFightHp = 0
	if IS_BOSS_EXISTED:#先默认取最大血量
		afterFightHp = GetMaxBossHP(IS_BOSS_EXISTED)
	if PATRON_SAINT_OBJ:#有守护神，先默认取最大血量
		afterFightHp = GetMaxBossHP(3)
	if STATUE_HP:
		afterFightHp = STATUE_HP
	unionId = DukeOnDuty.get(1)
	leader_name = ""
	unionObj = UnionMgr.GetUnionObjByID(unionId)
	if unionObj:
		leader_name = unionObj.leader_name
	return sendList, afterFightHp, leader_name

def CreateDuke(index):
	'''
	创建雕像
	'''
	global BOSS_OBJ
	
	global IS_BOSS_EXISTED
	
	scene = cSceneMgr.SearchPublicScene(EnumGameConfig.DUKE_SCENE_ID)
	if scene:	
		unionId = DukeOnDuty.get(1)
		leader_name = GlobalPrompt.DUKE_LEADER_NAME
		UnionObj = UnionMgr.GetUnionObjByID(unionId)
		if UnionObj:
			leader_name += UnionObj.leader_name
		if index == 1:
			if IS_BOSS_EXISTED == 1:
				return
			x, y = DukeOnDutyDefine.BOSS_POS_1
			BOSS_OBJ = scene.CreateNPC(DukeOnDutyDefine.BOSS_ID_1, x, y, DukeOnDutyDefine.BOSS_TOWARD1, 1, {EnumNPCData.EnNPC_Name : leader_name})
			IS_BOSS_EXISTED = 1
			SetBossHP(IS_BOSS_EXISTED)
		else:
			if IS_BOSS_EXISTED == 2:
				return
			if BOSS_OBJ:
				scene.DestroyNPC(BOSS_OBJ.GetNPCID())
				BOSS_OBJ = None
			x, y = DukeOnDutyDefine.BOSS_POS_2
			BOSS_OBJ = scene.CreateNPC(DukeOnDutyDefine.BOSS_ID_1, x, y, DukeOnDutyDefine.BOSS_TOWARD2, 1, {EnumNPCData.EnNPC_Name : leader_name})
			IS_BOSS_EXISTED = 2
			SetBossHP(IS_BOSS_EXISTED)
			
def GetMaxBossHP(bossType):
	#获取boss的最大血量
	hpCfg = DukeOnDutyConfig.GetBossHpConfig(WorldData.GetWorldKaiFuDay())
	if not hpCfg:
		print "GE_EXC, can not find kaifuday(%s) in BOSS_HP_DICT" % WorldData.GetWorldKaiFuDay()
		#找不到就设定个固定值
		return DukeOnDutyDefine.MAX_BOSS_HP
	else:
		if bossType == 1:
			return hpCfg.bossHp1
		elif bossType == 2:
			return hpCfg.bossHp2
		else:
			return hpCfg.bossHp3
	
def SetBossHP(bossType):
	#通过世界等级设置当前boss的最大血量
	global STATUE_HP

	hpCfg = DukeOnDutyConfig.GetBossHpConfig(WorldData.GetWorldKaiFuDay())
	if not hpCfg:
		print "GE_EXC, can not find kaifuday(%s) in BOSS_HP_DICT" % WorldData.GetWorldKaiFuDay()
		#找不到就设定个固定值
		STATUE_HP = DukeOnDutyDefine.MAX_BOSS_HP
	else:
		if bossType == 1:#外城
			STATUE_HP = hpCfg.bossHp1
		elif bossType == 2:#内城
			STATUE_HP = hpCfg.bossHp2
		else:#守护神
			STATUE_HP = hpCfg.bossHp3
		
def GetPointByHurt(role, hurt):
	#根据玩家造成的伤害计算活动的积分
	cfg = DukeOnDutyConfig.GetBossHpConfig(WorldData.GetWorldKaiFuDay())
	if not cfg:
		print "GE_EXC, can not find kaifuday() in GetPointByHurt" % WorldData.GetWorldKaiFuDay()
		return 0
	point = hurt / cfg.divisor
	if min(point, cfg.minpoint) == point:
		return cfg.minpoint
	if max(point, cfg.maxpoint) == point:
		return cfg.maxpoint
	return point

def CanIntoDukeOnDuty(callargv, regparam):
	'''
	准备阶段，可进入
	'''
	global IS_PREPARE
	
	IS_PREPARE = True
	#创建雕像
	CreateDuke(1)
	#清除城主身上的buff
	ClearRoleBuff()
	#1分钟准备时间
	cComplexServer.RegTick(DukeOnDutyDefine.BOSS_READY_DURATION, StartDukeOnDuty)
	
	cRoleMgr.Msg(3, 0, GlobalPrompt.DUKE_READY_MSG4)
	
def StartDukeOnDuty(callargv, regparam):
	'''
	开始了
	'''
	global IS_START
	IS_START = True
	
	cComplexServer.RegTick(10, Per10Second)
	cComplexServer.RegTick(20 * 60, EndDukeOnDuty)
	cRoleMgr.Msg(1, 0, GlobalPrompt.DUKE_START_MSG)
	
def EndDukeOnDuty(callargv, regparam):
	'''
	活动结束
	'''
	global BOSS_OBJ
	global IS_START
	global UNION_POINT_DICT
	global DEFENCE_UNION_LIST
	global IS_BOSS_EXISTED
	global PATRON_SAINT_OBJ
	global DUKE_ON_DUTY_IDX1
	global DUKE_ON_DUTY_IDX2
	global DUKE_ON_DUTY_IDX3
	IS_START = False
	#获取攻方积分前3工会
	rank_list = UNION_POINT_DICT.values()
	rank_list.sort(key=lambda x:x[2], reverse = True)
	select_list = rank_list[0:3]
	defence_unionId = 0
	if not DEFENCE_UNION_LIST:
		defence_unionId = 0
	else:
		defence_unionId = DEFENCE_UNION_LIST[0]
	reward_dict = {}
	state = False
	if IS_BOSS_EXISTED:#雕像存在
		state = True
		scene = cSceneMgr.SearchPublicScene(EnumGameConfig.DUKE_SCENE_ID)
		if scene:#删除雕像
			scene.DestroyNPC(BOSS_OBJ.GetNPCID())
			BOSS_OBJ = None
		IS_BOSS_EXISTED = 0
		SetDukeUnion(defence_unionId, defence_unionId, rank_list, 0)
		reward_dict[1] = defence_unionId
		length = len(select_list)
		if length >= 1:
			reward_dict[2] = select_list[0][0]
		if length >= 2:
			reward_dict[3] = select_list[1][0]
		if length >= 3:
			reward_dict[4] = select_list[2][0]		
	else:#雕像不存在
		scene = cSceneMgr.SearchPublicScene(EnumGameConfig.DUKE_SCENE_ID)
		if scene:#删除守护神
			if PATRON_SAINT_OBJ:
				scene.DestroyNPC(PATRON_SAINT_OBJ.GetNPCID())
				PATRON_SAINT_OBJ = None
		if not select_list:
			Duke_id = 0
		else:
			#攻方积分第一的为城主
			Duke_id = select_list[0][0]
		SetDukeUnion(Duke_id, defence_unionId, rank_list, 1)
		length = len(select_list)
		if length >= 1:
			reward_dict[1] = select_list[0][0]
		if length >= 2:
			reward_dict[2] = select_list[1][0]
		if length >= 3:
			reward_dict[3] = select_list[2][0]
		reward_dict[4] = defence_unionId
	#发工会排名奖励
	with DutyUnionRankReward:
		SendUinonReward(reward_dict, state)
	for _, obj in UNION_OBJ.iteritems():
		obj.SendPersonReward()
	ClearData()

def SetDukeUnion(unionId, defUnionId, rankList, state):
	if not unionId:
		return
	defenceId = DukeOnDuty.get(DUKE_ON_DUTY_IDX1)
	unionS = False
	if defenceId and unionId == defenceId:
		unionS = True
	#防守成功	
	DukeOnDuty[DUKE_ON_DUTY_IDX1] = unionId
	if not state:
		if unionS:
			DukeOnDuty[DUKE_ON_DUTY_IDX2] += 1
		else:
			DukeOnDuty[DUKE_ON_DUTY_IDX2] = 0
		DukeOnDuty[DUKE_ON_DUTY_IDX4] = 1 #守方成功
	else:
		DukeOnDuty[DUKE_ON_DUTY_IDX2] = 0
		DukeOnDuty[DUKE_ON_DUTY_IDX4] = 2 #攻方成功
		
	DukeOnDuty[DUKE_ON_DUTY_IDX3] = rankList
	DukeOnDuty[DUKE_ON_DUTY_IDX5] = defUnionId
	print "DukeOnDuty.SetDukeUnion is OK", DukeOnDuty
	unionObj = UnionMgr.GetUnionObjByID(unionId)
	#广播结果
	unionName = ""
	if not unionObj:
		SendResult(unionName ,state)
	else:
		unionName = unionObj.name
		SendResult(unionName ,state)
	#增加称号
	if unionId in UNION_OBJ:
		UNION_OBJ[unionId].SetTitle()
	#增加城主buff
	AddRoleBuff(unionId)
	WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_Set_Duke, unionObj)
	
def SendUinonReward(reward_dict, state):
	'''
	给排名奖励
	@param reward_dict:
	'''
	global UNION_OBJ
	RC = RewardBuff.CalNumber
	RD = RewardBuff.enDukeOnDuty
	for order, unionId in reward_dict.iteritems():
		if unionId not in UNION_OBJ:
			continue
		role_list = UNION_OBJ[unionId].join_roleid_set.values()
		if not role_list:
			continue
		cfg_list = DukeOnDutyConfig.UNION_RANK_REWARD_DICT.get(order)
		if not cfg_list:
			continue
		for role_info in role_list:
			for cfg in cfg_list:
				if cfg.Minlevel <= role_info[1] <= cfg.Maxlevel:
					item_list = []
					if cfg.itemId1 and cfg.cnt1:
						item_list.append((cfg.itemId1, cfg.cnt1))
					if cfg.itemId2 and cfg.cnt2:
						item_list.append((cfg.itemId2, cfg.cnt2))
					if cfg.itemId3 and cfg.cnt3:
						item_list.append((cfg.itemId3, cfg.cnt3))
					if cfg.itemId4 and cfg.cnt4:
						item_list.append((cfg.itemId4, cfg.cnt4))
					desc = GlobalPrompt.DUKE_DEFENCE
					if not state:
						desc = GlobalPrompt.DUKE_ATTACK
					AwardMgr.SetAward(role_info[0], cfg.awardEnum, money = RC(RD, cfg.money), itemList = [(coding, RC(RD, cnt)) for (coding, cnt) in item_list], clientDescParam = (desc, order))
					break

def ClearData():
	'''
	清除数据
	'''
	global IS_START
	global IS_PREPARE
	global ATTACK_UNION_LIST
	global DEFENCE_UNION_LIST
	global ROLE_ID_DUKE
	global ROLE_JOIN_DUKE
	global UNION_OBJ
	global UNION_POINT_DICT
	global ATTACK_PLAYER_DICT
	global DEFENCE_PLAYER_DICT
	global ROLE_FIGHT_DICT
	global STATUE_HP
	global _SAVE_ROLE_HP
	global SAVE_FIGHT_DATA
	IS_START = False
	IS_PREPARE = False
	
	ATTACK_UNION_LIST = []
	DEFENCE_UNION_LIST = []
	ROLE_ID_DUKE = []
	ROLE_JOIN_DUKE = []
	
	UNION_OBJ = {}			#缓存参加的工会数据
	UNION_POINT_DICT = {}	#缓存攻方积分

	ATTACK_PLAYER_DICT = {} #在战场的攻方玩家
	DEFENCE_PLAYER_DICT = {}#在战场的守方玩家
			
	ROLE_FIGHT_DICT = {} 	#缓存玩家战斗信息
	STATUE_HP = None		#保存雕像的血
	_SAVE_ROLE_HP = {}  	#保存玩家血量
	SAVE_FIGHT_DATA = {}
	cComplexServer.RegTick(DukeOnDutyDefine.BOSS_READY_DURATION, TPRole)
	
	global RoleSet
	RoleSet = set()

def TPRole(callargv, regparam):
	scene = cSceneMgr.SearchPublicScene(EnumGameConfig.DUKE_SCENE_ID)
	if scene:
		#所有角色被退出场景
		for role in scene.GetAllRole():
			if role:
				if role.GetCD(EnumCD.Duty_CD) > 0:
					role.SetCD(EnumCD.Duty_CD, 0)
				role.BackPublicScene()
		
def DukeOnDutyAfterLoadDB():
	global DukeOnDuty
	global DUKE_ON_DUTY_IDX1
	global DUKE_ON_DUTY_IDX2
	global DUKE_ON_DUTY_IDX3
	global DUKE_ON_DUTY_IDX4
	if DUKE_ON_DUTY_IDX1 not in DukeOnDuty:
		DukeOnDuty[DUKE_ON_DUTY_IDX1] = 0 #工会ID
	if DUKE_ON_DUTY_IDX2 not in DukeOnDuty:
		DukeOnDuty[DUKE_ON_DUTY_IDX2] = 0 #工会连守天数
	if DUKE_ON_DUTY_IDX3 not in DukeOnDuty:
		DukeOnDuty[DUKE_ON_DUTY_IDX3] = [] #排行榜信息
	if DUKE_ON_DUTY_IDX4 not in DukeOnDuty:
		DukeOnDuty[DUKE_ON_DUTY_IDX4] = 0
	if DUKE_ON_DUTY_IDX5 not in DukeOnDuty:
		DukeOnDuty[DUKE_ON_DUTY_IDX5] = 0
		
def SendMailDay():
	#筛选工会和发工会邮件
	global ATTACK_UNION_LIST
	global DEFENCE_UNION_LIST
	
	ATTACK_UNION_LIST = []
	DEFENCE_UNION_LIST = []
	
	#获取工会排名
	sys_rank = SystemRank.GetSortUnionList()
	union_rank = sys_rank[0:8]
	k = 1
	RANK_LIST = {}
	for data in union_rank:
		RANK_LIST[k] = data
		k += 1
	firstState = CheckKaifuTime()
	if firstState:
	#开服第一天
		if RANK_LIST:
			for key, value in RANK_LIST.iteritems():
				if key == 1:
					DEFENCE_UNION_LIST.append(value[0])
				elif 1< key <= 8:
					ATTACK_UNION_LIST.append(value[0])
	else:
		defenceId = DukeOnDuty.get(DUKE_ON_DUTY_IDX1)
		if defenceId:
			for key, value in RANK_LIST.iteritems():
				if 1 <= key <= 8 and value[0] != defenceId:
					ATTACK_UNION_LIST.append(value[0])
			DEFENCE_UNION_LIST.append(defenceId)
		else:
			for key, value in RANK_LIST.iteritems():
				if key == 1:
					DEFENCE_UNION_LIST.append(value[0])
				elif 1< key <= 8:
					ATTACK_UNION_LIST.append(value[0])
	#发邮件
	for unionId in ATTACK_UNION_LIST:
		SendMailByUnionId(unionId)
	for unionId in DEFENCE_UNION_LIST:
		SendMailByUnionId(unionId)	
	cComplexServer.RegTick(35 * 60, RadioMsg3)

def SendMailByUnionId(unionId):
	unionObj = UnionMgr.GetUnionObjByID(unionId)
	if not unionObj:
		return
	global ROLE_ID_DUKE
	with DutySendMail:
		for roleId, _ in unionObj.members.iteritems():
			if roleId not in ROLE_ID_DUKE:
				ROLE_ID_DUKE.append(roleId)
			Mail.SendMail(roleId, GlobalPrompt.DUKE_MAIL, GlobalPrompt.DUKE_MAIL_TITLE, GlobalPrompt.DUKE_MAIL_DESC)
#6.40 公告
def RadioMsg1():
	cRoleMgr.Msg(3, 0, GlobalPrompt.DUKE_READY_MSG2)
	cComplexServer.RegTick(60 * 60, RadioMsg2)
#7.40公告
def RadioMsg2(callargv, regparam):
	cRoleMgr.Msg(3, 0, GlobalPrompt.DUKE_READY_MSG1)
#8.35公告
def RadioMsg3(callargv, regparam):
	cRoleMgr.Msg(3, 0, GlobalPrompt.DUKE_READY_MSG3)
	cComplexServer.RegTick(4 * 60, CanIntoDukeOnDuty)

#=====================城主收益buff=======================
def CheckKaifuTime():
	kaifutimes = WorldData.WD.get(EnumSysData.KaiFuKey)
	kaifuyear = kaifutimes.year
	kaifumon = kaifutimes.month
	kaifuday = kaifutimes.day
	now_time = time.localtime(time.time())
	if now_time[0] == kaifuyear and now_time[1] == kaifumon and now_time[2] == kaifuday:
		return True
	return False

def AddRoleBuff(defence_id):
	'''
	添加城主收益buff
	'''
	unionObj = UnionMgr.GetUnionObjByID(defence_id)
	if not unionObj:
		return
	expbonus = 0
	goldbonus = 0
	firstState = CheckKaifuTime()
	if firstState:#开服第一天
		goldbonus = DukeOnDutyDefine.KAIFU_BUFF_VALUE
	else:
		keepdays = DukeOnDuty.get(2)
		if keepdays >= DukeOnDutyDefine.MAX_BUFF_KEEP_DAY:#连守天数大于最大天数，取最大连守天数
			keepdays = DukeOnDutyDefine.MAX_BUFF_KEEP_DAY
		cfg = DukeOnDutyConfig.EARNING_BUFF_DICT.get(keepdays)
		if not cfg:
			return
		expbonus = cfg.expbonus
		goldbonus = cfg.goldbonus
	for roleid, _ in unionObj.members.iteritems():
		Call.LocalDBCall(roleid, SetRoleBuff2, (expbonus, goldbonus, 1, cDateTime.Seconds()))

def SetRoleBuff2(role, param):
	expbonus, goldbonus, chatinfo, second = param
	#当前时间秒数
	nowSceond = cDateTime.Seconds()
	if nowSceond - second >= DIFF_BETWEEN_SECOND:#当相差23小时40分，直接返回
		return
	role.SetEarningExpBuff(expbonus)
	role.SetEarningGoldBuff(goldbonus)
	role.SetChatInfo(EnumSocial.RoleDukeKey, chatinfo)
	
def SetRoleBuff(role, param):
	expbonus, goldbonus, chatinfo = param
	role.SetEarningExpBuff(expbonus)
	role.SetEarningGoldBuff(goldbonus)
	role.SetChatInfo(EnumSocial.RoleDukeKey, chatinfo)
	
def ClearRoleBuff():
	'''
	清除城主收益buff
	'''
	defence_id = DukeOnDuty.get(1)
	unionObj = UnionMgr.GetUnionObjByID(defence_id)
	if not unionObj:
		return
		
	for roleid, _ in unionObj.members.iteritems():
		Call.LocalDBCall(roleid, SetRoleBuff2, (0, 0, 0, cDateTime.Seconds()))
		
def AfterRoleHeFu(role, param):
	#合服后玩家处理
	#清除玩家的城主buff相关
	SetRoleBuff(role, (0, 0, 0))

def AfterLogin(role, param):
	#玩家上线后，检测玩家是否是城主公会
	unionId = role.GetUnionID()
	if not unionId:
		#清除玩家的城主buff相关
		SetRoleBuff(role, (0, 0, 0))
		return
	
	global DukeOnDuty
	defence_id = DukeOnDuty.get(1, 0)
	if unionId != defence_id:#不是城主公会
		#清除玩家的城主buff相关
		SetRoleBuff(role, (0, 0, 0))
#=======================================================	
def BeforeExit(role, param):
	'''
	退出之前，清除一些数据
	@param role:
	@param param:
	'''
	global IS_START
	global ATTACK_PLAYER_DICT
	global DEFENCE_PLAYER_DICT
	global ROLE_JOIN_DUKE
	global ROLE_FIGHT_DICT
	if not IS_START:
		return
	roleId = role.GetRoleID()
	if roleId in ATTACK_PLAYER_DICT:
		del ATTACK_PLAYER_DICT[roleId]
	if roleId in DEFENCE_PLAYER_DICT:
		del DEFENCE_PLAYER_DICT[roleId]	
	if roleId in ROLE_JOIN_DUKE:
		ROLE_JOIN_DUKE.remove(roleId)
	#清除玩家战斗记录
	if roleId in ROLE_FIGHT_DICT:
		del ROLE_FIGHT_DICT[roleId]

def ClientLost(role, param):
	'''
	玩家掉线
	@param role:
	@param param:
	'''
	if role.GetSceneID() == DukeOnDutyDefine.DUKE_SCENE_ID_1:
		role.BackPublicScene()
		roleId = role.GetRoleID()
		global ATTACK_PLAYER_DICT
		global DEFENCE_PLAYER_DICT
		if roleId in ATTACK_PLAYER_DICT:
			del ATTACK_PLAYER_DICT[roleId]
		if roleId in DEFENCE_PLAYER_DICT:
			del DEFENCE_PLAYER_DICT[roleId]
			
@PublicScene.RegSceneBeforeLeaveFun(EnumGameConfig.DUKE_SCENE_ID)
def AfterBeforeLeave(scene, role):
	#退出城主轮值状态
	Status.Outstatus(role, EnumInt1.ST_DukeOnDuty)
	
@PublicScene.RegSceneAfterJoinRoleFun(EnumGameConfig.DUKE_SCENE_ID)
def AfterJoinRole(scene, role):
	#强制进入城主轮值状态
	Status.ForceInStatus(role, EnumInt1.ST_DukeOnDuty)
#====================为工会界面轮值排名做的======================
def GetDukeRankData(role, msg):
	'''
	获取工会轮值积分排行
	@param role:
	@param msg:
	'''
	backId, _ = msg
	global DukeOnDuty
	global DUKE_ON_DUTY_IDX1
	global DUKE_ON_DUTY_IDX3
	rank_list = []
	name = ""
	times = 0
	tbool = 0
	last_name = ""
	if DUKE_ON_DUTY_IDX1 in DukeOnDuty:
		unionId = DukeOnDuty.get(DUKE_ON_DUTY_IDX1)
		unionObj = UnionMgr.GetUnionObjByID(unionId)
		if unionObj:
			name = unionObj.name
	if DUKE_ON_DUTY_IDX2 in DukeOnDuty:
		times = DukeOnDuty.get(DUKE_ON_DUTY_IDX2)
	if DUKE_ON_DUTY_IDX3 in DukeOnDuty:
		rank_list = DukeOnDuty.get(DUKE_ON_DUTY_IDX3, {})
	if DUKE_ON_DUTY_IDX4 in DukeOnDuty:
		tbool = DukeOnDuty.get(DUKE_ON_DUTY_IDX4)
	if DUKE_ON_DUTY_IDX5 in DukeOnDuty:
		last_union = DukeOnDuty.get(DUKE_ON_DUTY_IDX5)
		unionobj = UnionMgr.GetUnionObjByID(last_union)
		if unionobj:
			last_name = unionobj.name
	role.CallBackFunction(backId, [name, times, tbool, rank_list, last_name])
	
#===================================================
if "_HasLoad" not in dir():
	if Environment.HasLogic or Environment.HasWeb:
		DukeOnDuty = Contain.Dict("DukeOnDuty", (2038, 1, 1), DukeOnDutyAfterLoadDB, isSaveBig = False)
	
	if Environment.HasLogic and not Environment.IsCross:
		#发公告
		Cron.CronDriveByMinute((2038, 1, 1), RadioMsg1, H = "H == 18", M = "M == 40")
		#筛选
		Cron.CronDriveByMinute((2038, 1, 1), SendMailDay, H = "H == 20", M = "M == 00")
		
		Event.RegEvent(Event.Eve_BeforeExit, BeforeExit)
		Event.RegEvent(Event.Eve_ClientLost, ClientLost)
		Event.RegEvent(Event.Eve_AfterRoleHeFu, AfterRoleHeFu)
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Duty_Role_Join_Duke_Scene", "客户端请求进入城主轮值"), RoleJoinDuke)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Duty_Role_Exit_Duke_Scene", "客户端请求退出城主轮值"), RoleExitDuke)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Duty_Role_Add_Buff_Scene", "客户端请求进入升级buff"), ClientAddBuff)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Duty_Role_Quick_CD_Scene", "客户端请求加速CD"), ClientQuickCD)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Duty_Role_Attack_Statue", "客户端请求攻击雕像"), ClientAttackStatue)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Duty_Role_Close_Panel", "客户端请求关闭战场界面"), ClientClosePanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Duty_Role_Attack_Role", "客户端请求攻击玩家"), FightRolePVP)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Get_Duke_Rank_Data", "客户端请求获取轮值积分榜"), GetDukeRankData)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Duty_Fresh_War_Panel", "客户端请求刷新战场界面"), FreshWarPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Duty_Click_OK_Btn", "客户端点击确认"), ClickOKBtn)
		
