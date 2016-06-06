#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.MDragonCome.MDragonComeMgr")
#===============================================================================
# 魔龙降临管理
#===============================================================================
import random
import cDateTime
import Environment
import cRoleMgr
import cSceneMgr
import cNetMessage
import cComplexServer
from Common.Message import AutoMessage
from Common.Other import EnumAward,GlobalPrompt,EnumRoleStatus,EnumGameConfig
from ComplexServer.Log import AutoLog
from ComplexServer.Time import Cron
from Game.Activity.Award import AwardMgr
from Game.Role.Data import EnumDayInt8, EnumInt1
from Game.Role import Event, Status, Call
from Game.Activity.MDragonCome import MDragonComeConfig
from Game.Scene import PublicScene
from Game.DailyDo import DailyDo
from Game.Fight import Fight
from Game.NPC import NPCServerFun
from Game.Union import UnionMgr, UnionDefine
	
if "_HasLoad" not in dir():
	IS_START = False

	MD_SCENE_ID				= 723				#同魔兽入侵场景ID
	MD_ATTACK_COUNT			= 10				#挑战次数限制

	MD_START_DURATION		= 30 * 60		#魔龙降临活动开始持续时间
	MD_HEARSAY_DURATION 	= 5 * 60		#排行传闻发布时间
	MD_PER_INTERVAL_TIME 	= 60			#刷新排行榜间隔时间
	MD_RANK_SHOW_CNT		= 10
	MD_ENTER_SCENE_POS 		= ((47, 1084), (606, 1294))	#进入场景坐标
	
	MD_OVER_TIME = 0

	MDMGR = None
	#日志
	TraMDUnionRank = AutoLog.AutoTransaction("TraMDUnionRank", "魔龙入侵公会排行")
	#消息
	MD_Show_Rank = AutoMessage.AllotMessage("MD_Show_Rank", "通知客户端展示魔兽入侵排行榜")
	MD_Show_Role_Data = AutoMessage.AllotMessage("MD_Show_Role_Data", "通知客户端展示魔兽入侵玩家数据")
	MD_SyncActive_Time = AutoMessage.AllotMessage("MD_Sync_Active_Time", "同步活动时间数据")

#魔龙降临角色关联数据
class MDRoleData(object):
	def __init__(self,role):
		self.role_id = role.GetRoleID()		#roleId
		self.name = role.GetRoleName()		#角色名
		self.level = role.GetLevel()		#角色等级
		self.union_id = 0					#公会ID
		self.union_name = ""				#公会名
		self.hurt = 0						#伤害

		self.boss = None
		#获取公会名
		unionObj = role.GetUnionObj()
		if unionObj:
			self.union_id = unionObj.union_id
			self.union_name = unionObj.name


#魔龙降临管理器
class MDragonMgr(object):
	def __init__(self):
		self.mdrole_dict = {}			#角色数据字典
		self.fighting_dict = set()		#战斗中role
		self.rank_list = []				#排行榜列表(role_id, name, hurt, union_name)
		self.scene = cSceneMgr.SearchPublicScene(MD_SCENE_ID)

	#创建魔龙场景数据
	def create_md_data(self):
		#boss
		self.boss = self.scene.CreateNPC(19054, 1832, 477, 1, 1)

	def Ranking(self):
		'''
		排名
		'''
		rankList = []
		
		for mdrole in self.mdrole_dict.itervalues():
			if mdrole.hurt > 0:
				rankList.append((mdrole.role_id, mdrole.name, mdrole.hurt, mdrole.union_name))
		
		#对伤害进行排序
		rankList.sort(key = lambda x:x[2], reverse = True)
	
		self.rank_list = rankList[:999]
		
	def Fighting(self,role):
		'''
		战斗中
		@param role:
		@param npc:
		'''
		roleId = role.GetRoleID()
		self.fighting_dict.add(roleId)
		
	def LeaveFighting(self, role):
		'''
		离开战斗
		@param role:
		@param npcId:
		'''
		roleId = role.GetRoleID()
		
		if roleId in self.fighting_dict:
			self.fighting_dict.remove(roleId)

	def Clear(self):
		
		if self.boss:
			self.scene.DestroyNPC(self.boss.GetNPCID())


def SaveRoleHurt(role, hurt):
	'''
	保存角色伤害
	@param role:
	@param hurt:
	'''
	roleId = role.GetRoleID()
	mdRole = MDMGR.mdrole_dict.get(roleId)
	if not mdRole:
		return
	
	mdRole.hurt += hurt
	
	#判断是否需要排名
	#排行榜是否已经有10名
	if len(MDMGR.rank_list) < MD_RANK_SHOW_CNT:
		MDMGR.Ranking()
	else:
		#伤害是否比最后一名高
		if mdRole.hurt > MDMGR.rank_list[-1][2]:
			MDMGR.Ranking()

def MDReward():
	'''
	魔兽入侵奖励
	'''
	#进行一次排名
	MDMGR.Ranking()
	#公会奖励
	UnionReward()
	#伤害排名奖励
	HurtRankReward()
	#伤害量奖励
	HurtReward()

def UnionReward():
	'''
	公会奖励
	'''
	
	rankList = MDMGR.rank_list[:3]
	for idx, data in enumerate(rankList):
		rank = idx + 1
		mdrole = MDMGR.mdrole_dict.get(data[0])
		if not mdrole:
			continue
		
		unionObj = UnionMgr.GetUnionObjByID(mdrole.union_id)
		if not unionObj:#角色没有工会，只发给该玩家工会奖励
			#获取奖励配置
			roleunionRewardConfig = MDragonComeConfig.UnionReward.get_config(rank, mdrole.level)
			if not roleunionRewardConfig:
				print "GE_EXC, cant find UnionReward( rank = %s ,level = %s)"%(rank,mdrole.level)
				continue
			AwardMgr.SetAward(mdrole.role_id, EnumAward.MDUnionAward, money = roleunionRewardConfig.rewardMoney,
																exp = roleunionRewardConfig.rewardExp,
																bindRMB = roleunionRewardConfig.rewardBindRMB,
										 						itemList = roleunionRewardConfig.rewardItem, 
										 						clientDescParam = (rank, ))
			continue
		
		for memberId, memberData in unionObj.members.iteritems():
			level = memberData[UnionDefine.M_LEVEL_IDX]
			#获取奖励配置
			unionRewardConfig = MDragonComeConfig.UnionReward.get_config(rank, level)
			if not unionRewardConfig:
				print "GE_EXC, cant find UnionReward( rank = %s ,level = %s)"%(rank,level)
				continue
			
			#设置全体公会成员奖励
			AwardMgr.SetAward(memberId, EnumAward.MDUnionAward, money = unionRewardConfig.rewardMoney,
																exp = unionRewardConfig.rewardExp,
																bindRMB = unionRewardConfig.rewardBindRMB,
										 						itemList = unionRewardConfig.rewardItem, 
										 						clientDescParam = (rank, ))
			
	#日志
	with TraMDUnionRank:
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveMDUnionRank, rankList)
			
def HurtRankReward():
	'''
	伤害排名奖励
	'''
	
	rankList = MDMGR.rank_list
	for idx, data in enumerate(rankList):
		rank = idx + 1
		mdrole = MDMGR.mdrole_dict.get(data[0])
		if not mdrole:
			continue
		
		hurtRankRewardConfig = MDragonComeConfig.HurtRankReward.get_config(rank, mdrole.level)
		if not hurtRankRewardConfig:
			print "GE_EXC, cant find hurtRankRewardConfig( rank = %s ,level = %s)" %(rank,mdrole.level)
			continue
		
		#设置奖励
		AwardMgr.SetAward(mdrole.role_id, EnumAward.MDHurtRankAward, money = hurtRankRewardConfig.rewardMoney,
																	 exp = hurtRankRewardConfig.rewardExp,
																	 bindRMB = hurtRankRewardConfig.rewardBindRMB,
																	 itemList = hurtRankRewardConfig.rewardItem, 
																	 clientDescParam = (rank, ))
			
	#日志
	with TraMDUnionRank:
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveMDUnionRank, rankList)

	
def HurtReward():
	'''
	伤害奖励
	@param role:
	@param hurt:
	'''
	
	for k in MDMGR.mdrole_dict.keys():
		mdrole = MDMGR.mdrole_dict[k]
		if not mdrole:
			continue
		
		if mdrole.hurt > 0:
			hurtReward = MDragonComeConfig.HurtReward.get_config(mdrole.hurt, mdrole.level)
			if not hurtReward:#可能不在配置表的范围内
				continue
			
			#设置奖励
			AwardMgr.SetAward(mdrole.role_id, EnumAward.MDHurtAward, money = hurtReward.rewardMoney,
																	 exp = hurtReward.rewardExp,
																	 bindRMB = hurtReward.rewardBindRMB,
																	 itemList = hurtReward.rewardItem,
																	 clientDescParam = (mdrole.hurt, ))
			

def Back(role, callargv, regparam):
	#退出场景
	if role.GetSceneID() == MD_SCENE_ID:
		role.BackPublicScene()

#===============================================================================
# 事件
#===============================================================================
def OnRoleClientLost(role, param):
	'''
	角色客户端掉线
	@param role:
	@param param:
	'''
	if role.GetSceneID() == MD_SCENE_ID:
		role.BackPublicScene()
	
#===============================================================================
# 时间相关
#===============================================================================
def TenMinutesReadyMagicDragon():
	'''
	还有10分钟魔龙降临开始
	'''
	if not IsMDWeekDay():
		return
	#传闻
	cRoleMgr.Msg(1, 0, GlobalPrompt.MD_READY_HEARSAY_1)
	
def OneMinutesReadyMagicDragon():
	'''
	还有1分钟魔龙降临开始
	'''
	if not IsMDWeekDay():
		return
	#传闻
	cRoleMgr.Msg(1, 0, GlobalPrompt.MD_READY_HEARSAY_2)
	
def GetRankHearsayIfNoUnion(rank):
	'''
	获取排名对应的无公会传闻
	@param rank:
	'''
	if rank == 1:
		return GlobalPrompt.MD_RANK_FIRST_NO_UNION_HEARSAY
	elif rank == 2:
		return GlobalPrompt.MD_RANK_SECOND_NO_UNION_HEARSAY
	elif rank == 3:
		return GlobalPrompt.MD_RANK_THIRD_NO_UNION_HEARSAY
	else:
		return ""
	
def GetRankHearsay(rank):
	'''
	获取排名对应的传闻
	@param rank:
	'''
	if rank == 1:
		return GlobalPrompt.MD_RANK_FIRST_HEARSAY
	elif rank == 2:
		return GlobalPrompt.MD_RANK_SECOND_HEARSAY
	elif rank == 3:
		return GlobalPrompt.MD_RANK_THIRD_HEARSAY
	else:
		return ""
	
def MDEveryFiveMinutes(callargv, regparam):
	'''
	每五分钟调用
	@param callargv:
	@param regparam:
	'''
	#活动结束
	if IS_START is False:
		return
	
	#每五分钟调用，用来发传闻
	cComplexServer.RegTick(MD_HEARSAY_DURATION, MDEveryFiveMinutes)
	
	#ddrole.role_id, ddrole.name, ddrole.hurt, ddrole.union_name
	for idx, data in enumerate(MDMGR.rank_list[:3]):
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
			
			
def PerIntervalTime(callargv, regparam):
	#判断是否结束
	if IS_START is False:
		return
	
	#注册每分钟调用
	cComplexServer.RegTick(MD_PER_INTERVAL_TIME, PerIntervalTime)
	
	#广播给场景内所有玩家
	cNetMessage.PackPyMsg(MD_Show_Rank, MDMGR.rank_list[:10])
	cSceneMgr.BroadMsg(MD_SCENE_ID)
	
def IsMDWeekDay():
	return cDateTime.WeekDay() in (2, 4, 6)

def StartMagicDragon():
	'''
	魔龙降临开始
	@param callargv:
	@param regparam:
	'''
	if not IsMDWeekDay():
		return
	
	global IS_START
	IS_START = True

	global MDMGR
	MDMGR = MDragonMgr()		#创建魔龙降临管理器
	MDMGR.create_md_data()		#创建场景数据
	
	#魔龙降临开始，注册结束时间,30分钟后结束
	cComplexServer.RegTick(MD_START_DURATION, EndMagicDragon)
	
	#每五分钟调用，用来发传闻
	cComplexServer.RegTick(MD_HEARSAY_DURATION, MDEveryFiveMinutes)
	
	#注册每分钟调用
	cComplexServer.RegTick(MD_PER_INTERVAL_TIME, PerIntervalTime)
	
	global MD_OVER_TIME
	MD_OVER_TIME = cDateTime.Seconds() + MD_START_DURATION
	
	#传闻
	cRoleMgr.Msg(1, 0, GlobalPrompt.MD_START_HEARSAY)

def EndMagicDragon(callargv, regparam):
	'''
	魔龙降临结束
	@param callargv:
	@param regparam:
	'''
	global IS_START
	
	#活动关闭
	IS_START = False
	
	#活动结束清理
	MDMGR.Clear()
	
	#奖励
	MDReward()
	
	#通知客户端活动结束	
	for role in MDMGR.scene.GetAllRole():
		#role.SendObj(MD_End, None)
		role.RegTick(10, Back, None)
		
	#传闻
	cRoleMgr.Msg(1, 0, GlobalPrompt.MD_END_HEARSAY)

def ShowRank(role):
	'''
	显示排行榜
	@param role:
	'''
	role.SendObj(MD_Show_Rank, MDMGR.rank_list[:10])

def ShowRoleData(role):
	'''
	显示角色信息
	@param role:
	'''
	mdRole = MDMGR.mdrole_dict.get(role.GetRoleID())
	if not mdRole:
		return
	
	role.SendObj(MD_Show_Role_Data, mdRole.hurt)
	
def SyncActiveTime(role):
	'''
	同步活动时间
	'''
	
	role.SendObj(MD_SyncActive_Time,MD_OVER_TIME)
	

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
#===============================================================================
# 场景相关
#===============================================================================
@PublicScene.RegSceneAfterJoinRoleFun(MD_SCENE_ID)
def AfterJoin(scene, role):
	#进入魔龙降临状态
	Status.ForceInStatus(role, EnumInt1.ST_MDragonCome)
	
	roleId = role.GetRoleID()
	
	global MDMGR
	#可能还未初始化
	if not MDMGR:
		return
	
	#初始化魔兽入侵角色数据
	if roleId not in MDMGR.mdrole_dict:
		MDMGR.mdrole_dict[roleId] = MDRoleData(role)
	
	#显示排行榜和角色数据
	ShowRank(role)
	ShowRoleData(role)
	#同步活动时间
	SyncActiveTime(role)
	
	
@PublicScene.RegSceneBeforeLeaveFun(MD_SCENE_ID)
def AfterBeforeLeave(scene, role):
	#退出魔龙入侵状态
	Status.Outstatus(role, EnumInt1.ST_MDragonCome)
	
#===============================================================================
# NPC相关
#===============================================================================
@NPCServerFun.RegNPCServerOnClickFun(19054)
def OnClick_BossDemon(role, npc):
	#还没开始
	
	if IS_START is False:
		return
	
	#没有剩余挑战次数
	fight_times = role.GetDI8(EnumDayInt8.MDragonTimes)
	if fight_times >= MD_ATTACK_COUNT:
		role.Msg(2, 0, GlobalPrompt.MD_NoTimes)
		return
	
	
	#获取配置(只有一个boss)
	BossConfig = MDragonComeConfig.MD_BOSS_CONFIG.get(0)# .DD_DEMON_BASE.get(DDMGR.wave)
	if not BossConfig:
		return
	
	#战斗状态
	if Status.IsInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	#设置外观状态
	role.SetAppStatus(EnumRoleStatus.Fighting)
	
	#血量字典
	#nowHp = DDMGR.hp_dict.get(npc.GetNPCID(), demonConfig.bossHP)
	
	#保存战斗状态
	MDMGR.Fighting(role)
	
	#战斗
	PVE_MD(role, 16, BossConfig.bossCampId, npc.GetNPCID(),AfterFight)

#===============================================================================
# 离线命令
#===============================================================================
def IncFightTimes(role, param):
	'''
	设置参与
	@param role:
	@param param:
	'''
	oldDays = param
	newDays = cDateTime.Days()
	#若跨天则不需要设置
	if newDays > oldDays:
		return
	
	with TraMDAttactTimes:
		role.IncDI8(EnumDayInt8.MDragonTimes,1)
	
#===============================================================================
# 战斗相关
#===============================================================================
def PVE_MD(role, fightType, mcid, npcId, AfterFight, OnLeave = None, AfterPlay = None):
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
	
	boosMaxHp = 0
	for u in right_camp.pos_units.itervalues():
		boosMaxHp = u.max_hp# = maxHP
		#u.hp = maxHP

	# 4设置回调函数（不是一定需要设置回调函数，按需来）
	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	# 如果需要带参数，则直接绑定在fight对象上
	fight.after_fight_param = boosMaxHp
	# 5开启战斗（之后就不能再对战斗做任何设置了）
	fight.start()

def OnLeave(fight, role, reason):
	# reason 0战斗结束离场；1战斗中途掉线
	# fight.result如果没“bug”的话将会取值1左阵营胜利；0平局；-1右阵营胜利；None战斗未结束
	# 注意，只有在角色离开的回调函数中fight.result才有可能为None
	pass

def AfterFight(fight):
	
	beforeFightHp = fight.after_fight_param
	afterFightHp = 0
	for u in fight.right_camp.pos_units.itervalues():
		afterFightHp = u.hp
	
	hurt = abs(beforeFightHp - afterFightHp)
	
	#获取战斗role
	if not fight.left_camp.roles:
		return
	left_camp_roles_list = list(fight.left_camp.roles)
	role = left_camp_roles_list[0]
	
	#离线命令设置魔龙挑战次数
	Call.LocalDBCall(role.GetRoleID(), IncFightTimes, cDateTime.Days())
	
	with TraMDAfterFight:
		#记录战斗回合数、战斗结束后获得CD
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveMDAfterFight, fight.round)
	
	
	#离开战斗
	MDMGR.LeaveFighting(role)
	#记录伤害
	SaveRoleHurt(role, hurt)
	#重置外形状态
	role.SetAppStatus(EnumRoleStatus.Nothing)
	
	# fight.round当前战斗回合
	# fight.result如果没“bug”的话将会取值1左阵营胜利；0平局；-1右阵营胜利
	# 故判断胜利请按照下面这种写法明确判定
	if fight.result == 1:
		#left win
		#是否有NPC，有则删除NPC
		#npc = MDMGR.scene.SearchNPC(npcId)
		#if npc:
		#	MDMGR.DestroyNPC(npc)
		pass
	elif fight.result == -1:
		#right win
		#随机一个复活点
		x, y = RandomXY(*MD_ENTER_SCENE_POS)
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
# 客户端请求
#===============================================================================
def RequestMDEnterScene(role,msg):
	'''
	客户端请求进入魔兽入侵场景
	@param role:
	@param msg:
	'''
	#判断时间
	if IS_START is not True:
		return
		
	#需要等级
	if role.GetLevel() < EnumGameConfig.MD_NEED_LEVEL:
		return
	
	#是否可以进入魔兽入侵状态
	if not Status.CanInStatus(role, EnumInt1.ST_MDragonCome):
		return

	#随机一个点
	#x, y = RandomXY(*MD_ENTER_SCENE_POS)
	role.Revive(MD_SCENE_ID, 344, 1271)

	#每日必做 -- 进入魔龙降临场景
	Event.TriggerEvent(Event.Eve_DoDailyDo, role, (DailyDo.Daily_DD, 1))
	
	role.SetI1(EnumInt1.MDragonComeIn, True)
	
	if role.GetI1(EnumInt1.DemonDefenseIn):
		Event.TriggerEvent(Event.Eve_FB_AfterDF, role, None)
	#激情活动奖励狂翻倍 任务进度
	Event.TriggerEvent(Event.Eve_PassionMultiRewardTask, role, (EnumGameConfig.PassionMulti_Task_MDragonCome, True))
	#元旦金猪活动任务进度
	Event.TriggerEvent(Event.Eve_NewYearDayPigTask, role, (EnumGameConfig.NewYearDay_Task_MDragonCome, True))
	


def RequestMDLeaveScene(role,msg):
	'''
	客户端请求离开魔兽入侵场景
	@param role:
	@param msg:
	'''
	if role.GetSceneID() == MD_SCENE_ID:
		role.BackPublicScene()


if "_HasLoad" not in dir():
	#日志
	#TraDDHurtReward = AutoLog.AutoTransaction("TraDDHurtReward", "魔兽入侵伤害奖励")
	#TraDDUnionRank = AutoLog.AutoTransaction("TraDDUnionRank", "魔兽入侵公会排行")
	
	TraMDAttactTimes = AutoLog.AutoTransaction("TraMDAttactTimes", "魔龙降临挑战次数")
	TraMDAfterFight = AutoLog.AutoTransaction("TraMDAfterFight", "魔龙入侵战斗后记录")
	
	if Environment.HasLogic and not Environment.IsCross and (Environment.EnvIsQQ() or Environment.EnvIsFT()):
		
		#距离 魔龙降临还有10分钟
		Cron.CronDriveByMinute((2038, 1, 1), TenMinutesReadyMagicDragon, H="H == 15", M="M == 50")
		#距离 魔龙降临还有1分钟
		Cron.CronDriveByMinute((2038, 1, 1), OneMinutesReadyMagicDragon, H="H == 15", M="M == 59")
		#魔龙降临准备
		Cron.CronDriveByMinute((2038, 1, 1), StartMagicDragon, H="H == 16", M="M == 00")
		#事件
		Event.RegEvent(Event.Eve_ClientLost, OnRoleClientLost)
		
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("MD_Enter_Scene", "客户端请求进入魔龙降临场景"), RequestMDEnterScene)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("MD_Leave_Scene", "客户端请求离开魔龙降临场景"), RequestMDLeaveScene)
	
