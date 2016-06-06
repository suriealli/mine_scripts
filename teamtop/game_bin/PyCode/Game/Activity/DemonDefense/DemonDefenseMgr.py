#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DemonDefense.DemonDefenseMgr")
#===============================================================================
# 魔兽入侵管理
#===============================================================================
import random
import Environment
import cComplexServer
import cDateTime
import cNetMessage
import cRoleMgr
import cSceneMgr
from Util import Random
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, EnumRoleStatus, EnumAward, GlobalPrompt,\
	EnumFightStatistics
from Game.SysData import WorldData
from ComplexServer.Log import AutoLog
from ComplexServer.Time import Cron
from Game.Activity.Award import AwardMgr
from Game.Activity.DemonDefense import DemonDefenseConfig
from Game.DailyDo import DailyDo
from Game.Fight import Fight
from Game.NPC import NPCServerFun
from Game.Role import Event, Status, Call
from Game.Role.Data import EnumDayInt8, EnumCD, EnumTempObj, EnumInt1,\
	EnumDayInt1
from Game.Scene import PublicScene
from Game.Union import UnionMgr, UnionDefine

if "_HasLoad" not in dir():
	IS_READY = False			#魔兽入侵活动是否准备中
	IS_START = False			#魔兽入侵活动是否开启
	
	DD_SCENE_ID = 7						#魔兽入侵场景ID
	DD_READY_DURATION = 60				#魔兽入侵准备时间
	DD_START_DURATION = 30 * 60			#魔兽入侵活动开始持续时间
	DD_HEARSAY_DURATION = 5 * 60		#魔兽入侵排行传闻发布时间
	DD_PER_INTERVAL_TIME = 60			#魔兽入侵刷新排行榜间隔时间
	DD_RANK_SHOW_CNT = 10				#魔兽入侵排行榜显示排名数量
	DD_NORMAL_DEMON_CNT = 4				#魔兽入侵普通魔兽数量
	DD_ENTER_SCENE_POS = ((47, 1084), (606, 1294))	#进入场景坐标
	DD_FIGHT_CD = 40					#魔兽入侵战斗CD
	DD_WAVE_CD = 10						#魔兽入侵波数间隔CD
	DD_RANDOM_OBJ_DICT = {}				#魔兽入侵抽奖随机对象字典
	
	DDMGR = None						#魔兽入侵管理器
	
	#消息
	DD_Start = AutoMessage.AllotMessage("DD_Start", "通知客户端魔兽入侵开始")
	DD_Show_Rank = AutoMessage.AllotMessage("DD_Show_Rank", "通知客户端展示魔兽入侵排行榜")
	DD_Show_Role_Data = AutoMessage.AllotMessage("DD_Show_Role_Data", "通知客户端展示魔兽入侵玩家数据")
	DD_End = AutoMessage.AllotMessage("DD_End", "通知客户端魔兽入侵结束")
	
class DDRole(object):
	def __init__(self, role):
		self.role_id = role.GetRoleID()		#roleId
		self.name = role.GetRoleName()		#角色名
		self.level = role.GetLevel()		#角色等级
		self.union_id = 0					#公会ID
		self.union_name = ""				#公会名
		self.hurt = 0						#伤害
		self.allot_lucky_draw_cnt = False	#分配抽奖次数
		#获取公会名
		unionObj = role.GetUnionObj()
		if unionObj:
			self.union_id = unionObj.union_id
			self.union_name = unionObj.name
			
class DDMgr(object):
	def __init__(self):
		self.wave = 0				#魔兽波数
		self.kill = 0				#击杀魔兽数量
		self.next_wave_time = 0		#下一波来临时间
		self.ddrole_dict = {}		#角色数据字典
		self.hp_dict = {}			#魔兽HP字典{npcId->{}, }
		self.fighting_dict = {}		#战斗中字典{npcId->[roleId,...], }
		self.rank_list = []			#排行榜列表
		self.npc_list = []			#npc列表
		self.scene = cSceneMgr.SearchPublicScene(DD_SCENE_ID)
		#创建魔兽
		self.NextWave()
		
	def CreateDemon(self):
		'''
		创建魔兽
		'''
		#世界数据没有载回
		if not WorldData.WD.returnDB:
			print"GE_EXC,WorldData not return when DemonDefense try CreateNPC"
			return
		#根据波数获取魔兽配置
		kfDay = WorldData.GetWorldKaiFuDay()
		demonConfig = DemonDefenseConfig.GetDemonConfig(self.wave,kfDay)
		if not demonConfig:
			return
		
		#boss
		npc = self.scene.CreateNPC(1078, 1609, 646, 1, 1)
		npcId = npc.GetNPCID()
		self.npc_list.append(npc)
		self.hp_dict[npcId] = demonConfig.bossHP
		self.fighting_dict[npcId] = []
		
		#monster
		for _ in xrange(DD_NORMAL_DEMON_CNT):
			npc = self.scene.CreateNPC(1079, 1786, 485, 1, 1)
			self.npc_list.append(npc)
			self.hp_dict[npc.GetNPCID()] = demonConfig.monsterHP
			
	def DecDemonHp(self, npcId, hurt):
		if npcId not in self.hp_dict:
			return
		
		demonHp = self.hp_dict[npcId]
		#击杀魔兽
		if hurt >= demonHp:
			#通知所有与此魔兽战斗的人战斗结束
			pass
		else:
			#扣血
			self.hp_dict[npcId] = demonHp - hurt
			
	def NextWave(self):
		'''
		下一波魔兽
		'''
		self.wave += 1
		self.next_wave_time = cDateTime.Seconds() + DD_WAVE_CD
		#创建
		self.CreateDemon()
		for role in self.scene.GetAllRole():
			ShowRoleData(role)
			
	def Fighting(self, role, npc):
		'''
		战斗中
		@param role:
		@param npc:
		'''
		npcId = npc.GetNPCID()
		roleId = role.GetRoleID()
		if npcId not in self.fighting_dict:
			return
		self.fighting_dict[npcId].append(roleId)
			
	def LeaveFighting(self, role, npcId):
		'''
		离开战斗
		@param role:
		@param npcId:
		'''
		roleId = role.GetRoleID()
		if npcId not in self.fighting_dict:
			return
		if roleId in self.fighting_dict[npcId]:
			self.fighting_dict[npcId].remove(roleId)
		
	def Ranking(self):
		'''
		排名
		'''
		rankList = [(ddrole.role_id, ddrole.name, ddrole.hurt, ddrole.union_name) for ddrole in self.ddrole_dict.itervalues()]
		
		#对伤害进行排序
		rankList.sort(key = lambda x:x[2], reverse = True)
		
		self.rank_list = rankList[:DD_RANK_SHOW_CNT]
		
	def DestroyNPC(self, npc):
		#击杀怪物数量增加
		self.kill += 1
		
		npcId = npc.GetNPCID()
		if npc in self.npc_list:
			self.npc_list.remove(npc)
		if npcId in self.hp_dict:
			del self.hp_dict[npcId]
			
		#所有正在和对应NPC战斗的玩家全部退出战斗
		if npcId in self.fighting_dict:
			fightRoleIdList = self.fighting_dict[npcId]
			for roleId in fightRoleIdList:
				role = cRoleMgr.FindRoleByRoleID(roleId)
				if not role:
					continue
				#退出战斗,魔兽胜利
				camp = role.GetTempObj(EnumTempObj.FightCamp)
				if not camp:
					continue
				camp.fight.end(-1)
			
			#删除对应npc战斗字典
			del self.fighting_dict[npcId]
		
		#删除
		self.scene.DestroyNPC(npcId)
		
		#本波魔兽已全部打完，出下一波
		if len(self.npc_list) == 0:
			self.NextWave()
			
	def Clear(self):
		#删除所有NPC
		for npc in self.npc_list:
			self.scene.DestroyNPC(npc.GetNPCID())
		self.npc_list = []
		
def GetRankHearsay(rank):
	'''
	获取排名对应的传闻
	@param rank:
	'''
	if rank == 1:
		return GlobalPrompt.DD_RANK_FIRST_HEARSAY
	elif rank == 2:
		return GlobalPrompt.DD_RANK_SECOND_HEARSAY
	elif rank == 3:
		return GlobalPrompt.DD_RANK_THIRD_HEARSAY
	else:
		return ""
	
def GetRankHearsayIfNoUnion(rank):
	'''
	获取排名对应的无公会传闻
	@param rank:
	'''
	if rank == 1:
		return GlobalPrompt.DD_RANK_FIRST_NO_UNION_HEARSAY
	elif rank == 2:
		return GlobalPrompt.DD_RANK_SECOND_NO_UNION_HEARSAY
	elif rank == 3:
		return GlobalPrompt.DD_RANK_THIRD_NO_UNION_HEARSAY
	else:
		return ""
	
def SaveRoleHurt(role, hurt):
	'''
	保存角色伤害
	@param role:
	@param hurt:
	'''
	roleId = role.GetRoleID()
	ddRole = DDMGR.ddrole_dict.get(roleId)
	if not ddRole:
		return
	
	ddRole.hurt += hurt
	
	#判断是否需要排名
	#排行榜是否已经有10名
	if len(DDMGR.rank_list) < DD_RANK_SHOW_CNT:
		DDMGR.Ranking()
	else:
		#伤害是否比最后一名高
		if ddRole.hurt > DDMGR.rank_list[-1][2]:
			DDMGR.Ranking()
			
def DDReward():
	'''
	魔兽入侵奖励
	'''
	#进行一次排名
	DDMGR.Ranking()
	#公会奖励
	UnionReward()
	#击杀奖励
	KillReward()
	#分配抽奖次数
	AllotLuckyDrawCnt()
	
def UnionReward():
	'''
	公会奖励
	'''
	rankList = DDMGR.rank_list[:3]
	for idx, data in enumerate(rankList):
		rank = idx + 1
		ddrole = DDMGR.ddrole_dict.get(data[0])
		if not ddrole:
			continue
		
		unionObj = UnionMgr.GetUnionObjByID(ddrole.union_id)
		if not unionObj:
			continue
		
		#公会奖励配置
		unionRewardConfigDict = DemonDefenseConfig.DD_UNION_REWARD.get(rank)
		if not unionRewardConfigDict:
			continue
		
		for memberId, memberData in unionObj.members.iteritems():
			level = memberData[UnionDefine.M_LEVEL_IDX]
			#获取奖励配置
			unionRewardConfig = unionRewardConfigDict.get(level)
			if not unionRewardConfig:
				continue
			
			#设置全体公会成员奖励
			AwardMgr.SetAward(memberId, EnumAward.DDUnionAward, itemList = [unionRewardConfig.rewardItem, ], clientDescParam = (rank, ))
			
	#日志
	with TraDDUnionRank:
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveDDUnionRank, rankList)
			
def KillReward():
	'''
	击杀奖励
	'''
	#日志
	with TraDDKillCnt:
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveDDKillCnt, DDMGR.kill)
		
	#击杀数为0
	if not DDMGR.kill:
		return
	
	#是否超过击杀最大数量
	killCnt = DDMGR.kill
	if killCnt > 500:
		killCnt = 500
	
	#击杀奖励(根据击杀数和等级发奖)
	configDict = DemonDefenseConfig.DD_KILL_REWARD.get(killCnt)
	if not configDict:
		print "GE_EXC can't find configDict in KillReward(%s)" % killCnt
		return
	for ddrole in DDMGR.ddrole_dict.itervalues():
		rewardConfig = configDict.get(ddrole.level)
		if not rewardConfig:
			continue
		#设置奖励
		AwardMgr.SetAward(ddrole.role_id, EnumAward.DDKillAward, money = rewardConfig.rewardMoney, exp = rewardConfig.rewardExp, clientDescParam = (DDMGR.kill, ))
		#离线命令设置今日参与了魔兽入侵
		Call.LocalDBCall(ddrole.role_id, HasJoinDD, cDateTime.Days())
	
def HurtReward(role, hurt, fightObj):
	'''
	伤害奖励
	@param role:
	@param hurt:
	'''
	#没有造成伤害则没有奖励
	if hurt == 0:
		return
	
	level = role.GetLevel()
	fightConfig = DemonDefenseConfig.DD_FIGHT_REWARD.get(level)
	if not fightConfig:
		return
	#YY防沉迷对奖励特殊处理
	yyAntiFlag = role.GetAnti()
	if yyAntiFlag == 1:
		minMoney = fightConfig.minRewardMoney_fcm
		maxMoney = fightConfig.maxRewardMoney_fcm
	elif yyAntiFlag == 0:
		minMoney = fightConfig.minRewardMoney
		maxMoney = fightConfig.maxRewardMoney
	else:
		minMoney = 0
		maxMoney = 0
		role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
	
	rewardMoney = 15 * hurt - 90000
	if minMoney == maxMoney == 0:
		rewardMoney = 0
	elif rewardMoney < minMoney:
		rewardMoney = minMoney
	elif rewardMoney > maxMoney:
		rewardMoney = maxMoney
	else:
		pass
	
	if rewardMoney > 0:
		role.IncMoney(rewardMoney)
		
	#战斗奖励统计显示
	fightObj.set_fight_statistics(role.GetRoleID(), EnumFightStatistics.EnumMoney, rewardMoney)
	
def AllotLuckyDrawCnt():
	'''
	分配抽奖次数
	'''
	#先分发给前10名#ddrole.role_id, ddrole.name, ddrole.hurt, ddrole.union_name
	for idx, data in enumerate(DDMGR.rank_list):
		rank = idx + 1
		roleId = data[0]
		ddrole = DDMGR.ddrole_dict.get(roleId)
		if not ddrole:
			continue
		#是否分配过抽奖次数
		if ddrole.allot_lucky_draw_cnt is True:
			continue
		#是否在线
		role = cRoleMgr.FindRoleByRoleID(roleId)
		if not role:
			continue
		#获取配置
		config = DemonDefenseConfig.DD_LUCKY_DRAW_CNT.get(rank)
		if not config:
			continue
		#设置次数
		ddrole.allot_lucky_draw_cnt = True
		role.SetDI8(EnumDayInt8.DD_Lucky_Draw_Cnt, config.cnt)
		
	#剩余的参与人全部只有1次抽奖机会
	for roleId, ddrole in DDMGR.ddrole_dict.iteritems():
		#是否分配过抽奖次数
		if ddrole.allot_lucky_draw_cnt is True:
			continue
		#是否在线
		role = cRoleMgr.FindRoleByRoleID(roleId)
		if not role:
			continue
		#设置次数
		role.SetDI8(EnumDayInt8.DD_Lucky_Draw_Cnt, 1)
	
def RandomXY(leftXY, rightXY):
	'''
	随机指定范围内的一个坐标
	@param leftXY:
	@param rightXY:
	'''
	lx, ly = leftXY
	rx, ry = rightXY
	randomX = 0
	randomY = 0
	if lx < rx:
		randomX = random.randint(lx, rx)
	else:
		randomX = random.randint(rx, lx)
	if ly < ry:
		randomY = random.randint(ly, ry)
	else:
		randomY = random.randint(ry, ly)
		
	return (randomX, randomY)

def ShowMainData(role, passState):
	'''
	显示主信息
	@param role:
	@param passState: 0不可以通过障碍，1可以通过障碍
	'''
	#是否可以通过障碍
	role.SendObj(DD_Start, passState)
	
def ShowRank(role):
	'''
	显示排行榜
	@param role:
	'''
	role.SendObj(DD_Show_Rank, DDMGR.rank_list)
	
def ShowRoleData(role):
	'''
	显示角色信息
	@param role:
	'''
	ddRole = DDMGR.ddrole_dict.get(role.GetRoleID())
	if not ddRole:
		return
	
	#伤害,波数,击杀数,下一波来临时间
	role.SendObj(DD_Show_Role_Data, (ddRole.hurt, DDMGR.wave, DDMGR.kill, DDMGR.next_wave_time))
	
def LuckyDraw(role, backFunId):
	'''
	抽奖
	@param role:
	@param backFunId:
	'''
	roleId = role.GetRoleID()
	
	#是否还有抽奖次数
	if not role.GetDI8(EnumDayInt8.DD_Lucky_Draw_Cnt):
		return
	
	global DD_RANDOM_OBJ_DICT
	r = None
	if roleId in DD_RANDOM_OBJ_DICT:
		r = DD_RANDOM_OBJ_DICT[roleId]
	else:
		r = Random.RandomRate()
		for odds, multiple in DemonDefenseConfig.DD_LUCKY_DRAW_ODDS:
			r.AddRandomItem(odds, multiple)
	
	#扣次数
	role.DecDI8(EnumDayInt8.DD_Lucky_Draw_Cnt, 1)
	
	#随机
	multiple = r.RandomOneThenDelete()
	
	#保存随机对象
	DD_RANDOM_OBJ_DICT[roleId] = r
	
	#如果用完抽奖次数则删除
	if role.GetDI8(EnumDayInt8.DD_Lucky_Draw_Cnt) == 0:
		del DD_RANDOM_OBJ_DICT[roleId]
		
	#回调客户端抽奖成功
	role.CallBackFunction(backFunId, multiple)
	
	#奖励
	level = role.GetLevel()
	config = DemonDefenseConfig.DD_LUCKY_DRAW_BASE.get(level)
	if not config:
		return
	
	#YY防沉迷对奖励特殊处理
	yyAntiFlag = role.GetAnti()
	if yyAntiFlag == 1:
		addMoney = config.moneyBase_fcm * multiple
	elif yyAntiFlag == 0:
		addMoney = config.moneyBase * multiple
	else:
		addMoney = 0
		role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
		return None
	
	if addMoney > 0:
		role.IncMoney(addMoney)
		
#===============================================================================
# 场景相关
#===============================================================================
@PublicScene.RegSceneAfterJoinRoleFun(DD_SCENE_ID)
def AfterJoin(scene, role):
	#进入魔兽入侵状态
	Status.ForceInStatus(role, EnumInt1.ST_DemonDefense)
	
	#特殊处理坐骑不可飞行
	role.SetTempFly(2)
	
	roleId = role.GetRoleID()
	
	global DDMGR
	#可能还未初始化
	if not DDMGR:
		return
	
	#初始化魔兽入侵角色数据
	if roleId not in DDMGR.ddrole_dict:
		DDMGR.ddrole_dict[roleId] = DDRole(role)
	
	#显示排行榜和角色数据
	ShowRank(role)
	ShowRoleData(role)
	
	if IS_READY is True:
		#未开始，不可以通过
		ShowMainData(role, 0)
		return
	
	if IS_START is True:
		#已经开始，可以通过
		ShowMainData(role, 1)
		return
	
@PublicScene.RegSceneBeforeLeaveFun(DD_SCENE_ID)
def AfterBeforeLeave(scene, role):
	#退出魔兽入侵状态
	Status.Outstatus(role, EnumInt1.ST_DemonDefense)
	
	#还原坐骑不可飞行状态
	role.SetTempFly(0)
	
#===============================================================================
# NPC相关
#===============================================================================
@NPCServerFun.RegNPCServerOnClickFun(1078)
def OnClick_BossDemon(role, npc):
	#还没开始
	if IS_START is False:
		return

	#世界数据没有载回
	if not WorldData.WD.returnDB:
		print"GE_EXC,WorldData not return when DemonDefense try CreateNPC"
		return

	#CD时间
	cd = role.GetCD(EnumCD.DD_Fight_CD)
	if cd > 0:
		return
	
	#获取配置
	kfDay = WorldData.GetWorldKaiFuDay()
	demonConfig = DemonDefenseConfig.GetDemonConfig(DDMGR.wave,kfDay)
	if not demonConfig:
		return
	
	#战斗状态
	if Status.IsInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	#设置CD
	role.SetCD(EnumCD.DD_Fight_CD, DD_FIGHT_CD)
	
	#设置外观状态
	role.SetAppStatus(EnumRoleStatus.Fighting)
	
	#血量字典
	nowHp = DDMGR.hp_dict.get(npc.GetNPCID(), demonConfig.bossHP)
	
	#保存战斗状态
	DDMGR.Fighting(role, npc)
	
	#战斗
	PVE_DD(role, 16, demonConfig.bossCampId, npc.GetNPCID(), demonConfig.bossHP, nowHp, AfterFight)
	
@NPCServerFun.RegNPCServerOnClickFun(1079)
def OnClick_NormalDemon(role, npc):
	#还没开始
	if IS_START is False:
		return

	#世界数据没有载回
	if not WorldData.WD.returnDB:
		print"GE_EXC,WorldData not return when DemonDefense try CreateNPC"
		return

	#CD时间
	cd = role.GetCD(EnumCD.DD_Fight_CD)
	if cd > 0:
		return
	
	#获取配置
	kfDay = WorldData.GetWorldKaiFuDay()
	demonConfig = DemonDefenseConfig.GetDemonConfig(DDMGR.wave,kfDay)
	if not demonConfig:
		return
	
	#战斗状态
	if Status.IsInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	#设置CD
	role.SetCD(EnumCD.DD_Fight_CD, DD_FIGHT_CD)
	
	#设置外观状态
	role.SetAppStatus(EnumRoleStatus.Fighting)
	
	#血量字典
	nowHp = DDMGR.hp_dict.get(npc.GetNPCID(), demonConfig.monsterHP)
	
	#保存战斗状态
	DDMGR.Fighting(role, npc)
	
	#战斗
	PVE_DD(role, 16, demonConfig.monsterCampId, npc.GetNPCID(), demonConfig.monsterHP, nowHp, AfterFight)
	
#===============================================================================
# 战斗相关
#===============================================================================
def PVE_DD(role, fightType, mcid, npcId, maxHP, nowHP, AfterFight, OnLeave = None, AfterPlay = None):
	'''
	魔兽入侵PVE
	@param role:
	@param fightType:
	@param mcid:
	@param npc:
	@param maxHP:
	@param hpDict:
	@param AfterFight:
	@param OnLeave:
	@param AfterPlay:
	'''
	# 1创建一场战斗(必须传入战斗类型，不同的战斗不要让策划复用战斗类型)
	fight = Fight.Fight(fightType)
	# 可以手动设置是否为pvp战斗，否则将是战斗配子表中战斗类型对应的pvp战斗取值
	# fight.pvp = True
	# 可收到设置客户端断线重连是否还原战斗,默认不还原
	fight.restore = True
	# 2创建两个阵营
	left_camp, right_camp = fight.create_camp()
	# 3在阵营中创建战斗单位
	left_camp.create_online_role_unit(role, role.GetRoleID(), use_px = True)
	# create_monster_camp_unit是创建一波怪物
	right_camp.create_monster_camp_unit(mcid)
	for u in right_camp.pos_units.itervalues():
		u.max_hp = maxHP
		u.hp = nowHP
	# 4设置回调函数（不是一定需要设置回调函数，按需来）
	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	# 如果需要带参数，则直接绑定在fight对象上
	fight.after_fight_param = (npcId, nowHP)
	# 5开启战斗（之后就不能再对战斗做任何设置了）
	fight.start()

def OnLeave(fight, role, reason):
	# reason 0战斗结束离场；1战斗中途掉线
	# fight.result如果没“bug”的话将会取值1左阵营胜利；0平局；-1右阵营胜利；None战斗未结束
	# 注意，只有在角色离开的回调函数中fight.result才有可能为None
	pass

def AfterFight(fight):
	npcId, beforeFightHp = fight.after_fight_param
	afterFightHp = 0
	for u in fight.right_camp.pos_units.itervalues():
		afterFightHp = u.hp
	
	hurt = abs(beforeFightHp - afterFightHp)
	
	#魔兽扣血
	DDMGR.DecDemonHp(npcId, hurt)
	
	#获取战斗role
	if not fight.left_camp.roles:
		return
	left_camp_roles_list = list(fight.left_camp.roles)
	role = left_camp_roles_list[0]
	
	#战斗CD判断
	if fight.round == 0:
		#0回合
		role.SetCD(EnumCD.DD_Fight_CD, min(role.GetCD(EnumCD.DD_Fight_CD), 10))
	elif fight.round == 1:
		#1回合
		role.SetCD(EnumCD.DD_Fight_CD, min(role.GetCD(EnumCD.DD_Fight_CD), 10))
	elif fight.round == 2:
		#2回合
		role.SetCD(EnumCD.DD_Fight_CD, min(role.GetCD(EnumCD.DD_Fight_CD), 20))
	elif fight.round == 3:
		#3回合
		role.SetCD(EnumCD.DD_Fight_CD, min(role.GetCD(EnumCD.DD_Fight_CD), 30))
	else:
		#4回合以上
		pass
	
	with TraDDAfterFight:
		#记录战斗回合数、战斗结束后获得CD
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveDemonDefenseAfterFight, (fight.round, role.GetCD(EnumCD.DD_Fight_CD)))
	
	#离开战斗
	DDMGR.LeaveFighting(role, npcId)
	#记录伤害
	SaveRoleHurt(role, hurt)
	#重置外形状态
	role.SetAppStatus(EnumRoleStatus.Nothing)
	
	#日志
	with TraDDHurtReward:
		#伤害奖励
		HurtReward(role, hurt, fight)
	
	# fight.round当前战斗回合
	# fight.result如果没“bug”的话将会取值1左阵营胜利；0平局；-1右阵营胜利
	# 故判断胜利请按照下面这种写法明确判定
	if fight.result == 1:
		#left win
		#是否有NPC，有则删除NPC
		npc = DDMGR.scene.SearchNPC(npcId)
		if npc:
			DDMGR.DestroyNPC(npc)
	elif fight.result == -1:
		#right win
		#随机一个复活点
		x, y = RandomXY(*DD_ENTER_SCENE_POS)
		role.JumpPos(x, y)
	else:
		#all lost
		pass
		
	#显示排行榜
	ShowRank(role)
	#显示玩家数据
	ShowRoleData(role)
		
def AfterPlay(fight):
	pass
	
#===============================================================================
# 离线命令
#===============================================================================
def HasJoinDD(role, param):
	'''
	设置今日已经参与了魔兽入侵
	@param role:
	@param param:
	'''
	oldDays = param
	newDays = cDateTime.Days()
	#若跨天则不需要设置
	if newDays > oldDays:
		return
	
	role.SetDI1(EnumDayInt1.DDJoin, 1)
	
#===============================================================================
# 事件
#===============================================================================
def OnRoleClientLost(role, param):
	'''
	角色客户端掉线
	@param role:
	@param param:
	'''
	if role.GetSceneID() == DD_SCENE_ID:
		role.BackPublicScene()
	
#===============================================================================
# 时间相关
#===============================================================================
def TenMinutesReadyDemonDefense():
	'''
	还有10分钟魔兽入侵准备
	'''
	if (Environment.IsDevelop or Environment.EnvIsQQ() or Environment.EnvIsFT()) and cDateTime.WeekDay() in (2, 4, 6):
		#国服、繁体2、4、6不开魔兽入侵
		return
	
	#传闻
	cRoleMgr.Msg(1, 0, GlobalPrompt.DD_READY_HEARSAY_1)
	
def DemonDefenseEveryFiveMinutes(callargv, regparam):
	'''
	魔兽入侵每五分钟调用
	@param callargv:
	@param regparam:
	'''
	#活动结束
	if IS_START is False:
		return
	
	#魔兽入侵每五分钟调用，用来发传闻
	cComplexServer.RegTick(DD_HEARSAY_DURATION, DemonDefenseEveryFiveMinutes)
	
	#ddrole.role_id, ddrole.name, ddrole.hurt, ddrole.union_name
	for idx, data in enumerate(DDMGR.rank_list[:3]):
		rank = idx + 1
		
		unionName = data[3]
		#判断是否有公会名
		if len(unionName) == 0:
			hearsay = GetRankHearsayIfNoUnion(rank)
			#传闻
			cRoleMgr.Msg(1, 0, hearsay % data[1])
		else:
			hearsay = GetRankHearsay(rank)
			#传闻
			cRoleMgr.Msg(1, 0, hearsay % (data[1], unionName))

def ReadyDemonDefense():
	'''
	魔兽入侵准备
	'''
	if (Environment.IsDevelop or Environment.EnvIsQQ() or Environment.EnvIsFT()) and cDateTime.WeekDay() in (2, 4, 6):
		#国服、繁体2、4、6不开魔兽入侵
		return
	
	#活动准备
	global IS_READY
	IS_READY = True
	
	global DDMGR
	DDMGR = DDMgr()		#创建魔兽入侵管理器
	
	#魔兽入侵准备时间1分钟
	cComplexServer.RegTick(DD_READY_DURATION, StartDemonDefense)
	
	#传闻
	cRoleMgr.Msg(1, 0, GlobalPrompt.DD_READY_HEARSAY_2)
	
def StartDemonDefense(callargv, regparam):
	'''
	魔兽入侵开始
	@param callargv:
	@param regparam:
	'''
	global IS_READY
	IS_READY = False
	
	global IS_START
	IS_START = True
	
	#魔兽入侵开始，注册结束时间,30分钟后结束
	cComplexServer.RegTick(DD_START_DURATION, EndDemonDefense)
	
	#魔兽入侵每五分钟调用，用来发传闻
	cComplexServer.RegTick(DD_HEARSAY_DURATION, DemonDefenseEveryFiveMinutes)
	
	#注册每分钟调用
	cComplexServer.RegTick(DD_PER_INTERVAL_TIME, PerIntervalTime)
	
	#广播给场景内所有玩家可以通过障碍
	cNetMessage.PackPyMsg(DD_Start, 1)
	cSceneMgr.BroadMsg(DD_SCENE_ID)
	
	#传闻
	cRoleMgr.Msg(1, 0, GlobalPrompt.DD_START_HEARSAY)
	
def EndDemonDefense(callargv, regparam):
	'''
	魔兽入侵结束
	@param callargv:
	@param regparam:
	'''
	global IS_START
	
	#活动关闭
	IS_START = False
	
	#活动结束清理
	DDMGR.Clear()
	
	#奖励
	DDReward()
	
	#通知客户端活动结束	
	for role in DDMGR.scene.GetAllRole():
		role.SendObj(DD_End, None)
		role.RegTick(10, Back, None)
		
	#传闻
	cRoleMgr.Msg(1, 0, GlobalPrompt.DD_END_HEARSAY)
		
def Back(role, callargv, regparam):
	#退出场景
	if role.GetSceneID() == DD_SCENE_ID:
		role.BackPublicScene()
		
def PerIntervalTime(callargv, regparam):
	#判断是否结束
	if IS_START is False:
		return
	
	#注册每分钟调用
	cComplexServer.RegTick(DD_PER_INTERVAL_TIME, PerIntervalTime)
	
	#广播给场景内所有玩家
	cNetMessage.PackPyMsg(DD_Show_Rank, DDMGR.rank_list)
	cSceneMgr.BroadMsg(DD_SCENE_ID)
		
#===============================================================================
# 客户端请求
#===============================================================================
def RequestDDEnterScene(role, msg):
	'''
	客户端请求进入魔兽入侵场景
	@param role:
	@param msg:
	'''
	#判断时间
	if IS_READY is not True:
		if IS_START is not True:
			return
		
	#需要等级
	if role.GetLevel() < EnumGameConfig.DD_NEED_LEVEL:
		return
	
	#是否可以进入魔兽入侵状态
	if not Status.CanInStatus(role, EnumInt1.ST_DemonDefense):
		return
	
	#北美版
	if Environment.EnvIsNA():
		#今天是否已经参与过魔兽入侵
		if role.GetDI1(EnumDayInt1.DDJoin):
			#提示
			role.Msg(2, 0, GlobalPrompt.DD_HAS_GET_REWARD_PROMPT)
			return
	
	#随机一个点
	x, y = RandomXY(*DD_ENTER_SCENE_POS)
	role.Revive(DD_SCENE_ID, x, y)
	
	#每日必做 -- 进入魔兽入侵场景
	Event.TriggerEvent(Event.Eve_DoDailyDo, role, (DailyDo.Daily_DD, 1))
	
	role.SetI1(EnumInt1.DemonDefenseIn, True)
	
	#找回
	if role.GetI1(EnumInt1.MDragonComeIn):
		Event.TriggerEvent(Event.Eve_FB_AfterDF, role, None)
	
	#圣诞转转乐
	Event.TriggerEvent(Event.Eve_IncChristmasMountotteryTime, role, EnumGameConfig.Source_DemonDefense)
	
	#王者公测奖励狂翻倍 任务进度
	Event.TriggerEvent(Event.Eve_WangZheCrazyRewardTask, role, (EnumGameConfig.WZCR_Task_DemonDefense, True))
	#激情活动奖励狂翻倍 任务进度
	Event.TriggerEvent(Event.Eve_PassionMultiRewardTask, role, (EnumGameConfig.PassionMulti_Task_DemonDefense, True))
	#元旦金猪活动任务进度
	Event.TriggerEvent(Event.Eve_NewYearDayPigTask, role, (EnumGameConfig.NewYearDay_Task_DemonDefense, True))
	
def RequestDDLeaveScene(role, msg):
	'''
	客户端请求离开魔兽入侵场景
	@param role:
	@param msg:
	'''
	if role.GetSceneID() == DD_SCENE_ID:
		role.BackPublicScene()

def RequestDDLuckyDraw(role, msg):
	'''
	客户端请求魔兽入侵抽奖
	@param role:
	@param msg:
	'''
	backFunId, _ = msg
	
	#日志
	with TraDDLuckyDraw:
		LuckyDraw(role, backFunId)

if "_HasLoad" not in dir():
	#日志
	TraDDHurtReward = AutoLog.AutoTransaction("TraDDHurtReward", "魔兽入侵伤害奖励")
	TraDDLuckyDraw = AutoLog.AutoTransaction("TraDDLuckyDraw", "魔兽入侵抽奖")
	TraDDUnionRank = AutoLog.AutoTransaction("TraDDUnionRank", "魔兽入侵公会排行")
	TraDDKillCnt = AutoLog.AutoTransaction("TraDDKillCnt", "魔兽入侵击杀数量")
	
	TraDDAfterFight = AutoLog.AutoTransaction("TraDDAfterFight", "魔兽入侵战斗后记录")
	
	if Environment.HasLogic and not Environment.IsCross:
		#在非北美体的情况下
		if not Environment.EnvIsNA() and not Environment.EnvIsEN() and not Environment.EnvIsYY():
			#距离魔兽入侵还有10分钟
			Cron.CronDriveByMinute((2038, 1, 1), TenMinutesReadyDemonDefense, H="H == 15", M="M == 50")
			#魔兽入侵准备
			Cron.CronDriveByMinute((2038, 1, 1), ReadyDemonDefense, H="H == 15", M="M == 59")
		#YY联运
		if Environment.EnvIsYY():
			#距离魔兽入侵还有10分钟
			Cron.CronDriveByMinute((2038, 1, 1), TenMinutesReadyDemonDefense, H = "H == 19", M = "M == 50")
			#魔兽入侵准备
			Cron.CronDriveByMinute((2038, 1, 1), ReadyDemonDefense, H = "H == 19", M = "M == 59")
		#北美版
		if Environment.EnvIsNA():
			#距离魔兽入侵还有10分钟
			Cron.CronDriveByMinute((2038, 1, 1), TenMinutesReadyDemonDefense, H = "H == 18", M = "M == 10")
			#魔兽入侵准备
			Cron.CronDriveByMinute((2038, 1, 1), ReadyDemonDefense, H = "H == 18", M = "M == 19")
		
		#北美版每天需要开两场
		if Environment.EnvIsNA():
			#距离魔兽入侵还有10分钟
			Cron.CronDriveByMinute((2038, 1, 1), TenMinutesReadyDemonDefense, H = "H == 11", M = "M == 20")
			#魔兽入侵准备
			Cron.CronDriveByMinute((2038, 1, 1), ReadyDemonDefense, H = "H == 11", M = "M == 29")
		
		#事件
		Event.RegEvent(Event.Eve_ClientLost, OnRoleClientLost)
		
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DD_Enter_Scene", "客户端请求进入魔兽入侵场景"), RequestDDEnterScene)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DD_Leave_Scene", "客户端请求离开魔兽入侵场景"), RequestDDLeaveScene)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DD_Lucky_Draw", "客户端请求魔兽入侵抽奖"), RequestDDLuckyDraw)
	
