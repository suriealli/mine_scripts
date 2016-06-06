#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.CouplesFB.CouplesFBMgr")
#===============================================================================
# 注情缘副本
#===============================================================================
import random
import cComplexServer
import cDateTime
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumFightStatistics, EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Activity.CouplesFB import CouplesFBConfig, CouplesEnumType
from Game.Fight import Fight
from Game.Persistence import Contain
from Game.Role import Event, Status
from Game.Role.Data import EnumInt1, EnumCD, EnumObj, EnumDayInt8, EnumInt8, EnumTempObj
from Game.Scene import PublicScene
from Game.VIP import VIPConfig
from Game.ThirdParty.QQidip import QQEventDefine

if "_HasLoad" not in dir():
	AUTO_FB_ID = 0		#副本ID
	AllotTeamID = 0
	
	MAX_FB_TIMES = 2	#每日固定的副本次数
	MIN_CREATE_TEAM_LEVEL = 36	#创建队伍的最低等级
	
	FB_KEEP_TIME = 45 * 60		#副本持续时间
	
	MAP_INDEX_LINE = 10	#地图最大行数
	MAP_INDEX_VER = 20	#地图最大竖数
	MAX_INDEX = 200		#最大的格子数
	FIXED_OBX_INDEX = [189,190,199]	#boss周围障碍物格子
	
	MOVE_ADD_CD = 5		#每移动加的CD
	FIGHT_ADD_CD = 12	#每次战斗胜利后加的CD
	MAX_FORBID_CD = 31	#当移动CD大于等于31秒禁止移动
	EVENT_MOVE_CD = 10	#每次增加/减少的CD
	EVENT_PASS_CD = 10	#每次增加/减少通关时间
	EVENT_BUFF_CD = 8	#触发buffcd
	
	SCENE_ID = 62	#场景ID
	EventType_Function = {}
	
	FB_OBJECT_DICT = {}	#roleId --> obj	玩家开启的副本对象，表示服务器重启就没了

	TEAM_WAIT_DICT = {}	#roleId --> obj, 副本开启后就删除
	TEAMID_TO_TEAM = {}	#teamId --> obj, 副本开启后就删除

	FB_Team_SyncQuit = AutoMessage.AllotMessage("FB_Team_SyncQuit", "通知客户端退出情缘副本队伍")
	FB_Team_SyncInfo = AutoMessage.AllotMessage("FB_Team_SyncInfo", "通知客户端情缘副本队伍信息")
	FB_Team_Info = AutoMessage.AllotMessage("FB_Team_Info", "同步情缘大厅组队信息")
	FB_Show_Invite = AutoMessage.AllotMessage("FB_Show_Invite", "通知客户端显示情缘组队邀请信息")
	FB_Syn_Rank = AutoMessage.AllotMessage("FB_Syn_Rank", "同步情缘副本排行榜数据")
	FB_Sys_OpenPanel = AutoMessage.AllotMessage("FB_Sys_OpenPanel", "通知客户端打开组队面吧")
	FB_Syn_Join = AutoMessage.AllotMessage("FB_Syn_Join", "通知客户端进入情缘副本")
	FB_SyncInfo = AutoMessage.AllotMessage("FB_SyncInfo", "通知情缘副本各种信息")
	FB_Del_Obstacles = AutoMessage.AllotMessage("FB_Del_Obstacles", "通知客户端消除世界情缘副本boss障碍物")
	FB_Syn_Buffs = AutoMessage.AllotMessage("FB_Syn_Buffs", "同步情缘副本玩家的buff")
	FB_Already_Pass = AutoMessage.AllotMessage("FB_Already_Pass", "通知客户端通关情缘副本")
	FB_Lucky_Draw = AutoMessage.AllotMessage("FB_Lucky_Draw", "通知客户端幸运挖宝")
	
	#日志
	CouplesKillReward = AutoLog.AutoTransaction("CouplesKillReward", "情缘副本击杀小怪奖励")
	CouplesLuckyReward = AutoLog.AutoTransaction("CouplesLuckyReward", "情缘副本幸运抽奖奖励")
	CouplesPassReward = AutoLog.AutoTransaction("CouplesPassReward", "情缘副本通关奖励")
	CouplesQuickCD = AutoLog.AutoTransaction("CouplesQuickCD", "情缘副本加速CD消耗")
	CouplesBuyTimes = AutoLog.AutoTransaction("CouplesBuyTimes", "情缘副本购买副本次数消耗")
	CouplesQuickThrough = AutoLog.AutoTransaction("CouplesQuickThrough", "情缘副本一键收益")
	
def BuildEventType_Function():
	#创建配置表中的类型对应处理函数
	EventType_Function[CouplesEnumType.Event_Type_1] = "LuckDraw"
	EventType_Function[CouplesEnumType.Event_Type_2] = "MonsterFight"
	EventType_Function[CouplesEnumType.Event_Type_3] = "AddBuff"
	EventType_Function[CouplesEnumType.Event_Type_4] = "AddBuff"
	EventType_Function[CouplesEnumType.Event_Type_5] = "AddBuff"
	EventType_Function[CouplesEnumType.Event_Type_6] = "AddBuff"
	EventType_Function[CouplesEnumType.Event_Type_7] = "AddBuff"
	EventType_Function[CouplesEnumType.Event_Type_8] = "RandomTP"
	EventType_Function[CouplesEnumType.Event_Type_9] = "Obstacles"
	EventType_Function[CouplesEnumType.Event_Type_10] = "TriOrgan"
	EventType_Function[CouplesEnumType.Event_Type_11] = "FightBoss"
	EventType_Function[CouplesEnumType.Event_Type_12] = "Obstacles"
	
class CouplesFB(object):
	#情缘副本
	def __init__(self, roleA, roleB, leader_id, FBcfg):
		global AUTO_FB_ID
		AUTO_FB_ID += 1
		self.FBID = AUTO_FB_ID
		self.FBcfg = FBcfg
		self.boss_state = True	#副本标志。True为进行中，False表示结束
		self.leader_id = leader_id
		
		self.start_time = cDateTime.Seconds()	#副本开启时间
		self.total_event_time = 0		#副本触发事件增加/减少的通关时间
		self.inFB_role = set()	#保存在副本里的玩家
		#初始化玩家对应的位置
		self.roleID_pos = {}
		#保存玩家的外观数据
		self.role_Data = {}
		#保存玩家的buff信息
		self.role_buff = {}	#{roleId:{1:正在使用的buffId, 2:得到但未使用的buff}}
		#保存怪物的血量
		self.monster_hp_dict = {}
		#奖励信息
		self.rewards_data = None
		if roleA:
			self.roleID_pos[roleA.GetRoleID()] = 1
			sex, career, grade = roleA.GetPortrait()
			self.role_Data[roleA.GetRoleID()] = [roleA.GetRoleName(), sex, career, grade]
			roleA.IncDI8(EnumDayInt8.CouplesFBTimes, 1) #增加副本次数
			roleA.SetObj(EnumObj.CouplesFBRewardDict, {self.FBID:0})
			
			Event.TriggerEvent(Event.QQidip_Eve, roleA, QQEventDefine.QQ_CouplesFB)
			Event.TriggerEvent(Event.Eve_FB_CFB, roleA)
			Event.TriggerEvent(Event.Eve_LatestActivityTask, roleA, (EnumGameConfig.LA_CouplesFB, 1))
		if roleB:
			self.roleID_pos[roleB.GetRoleID()] = 1
			sex, career, grade = roleB.GetPortrait()
			self.role_Data[roleB.GetRoleID()] = [roleB.GetRoleName(), sex, career, grade]
			roleB.IncDI8(EnumDayInt8.CouplesFBTimes, 1) #增加副本次数
			roleB.SetObj(EnumObj.CouplesFBRewardDict, {self.FBID:0})
			Event.TriggerEvent(Event.Eve_FB_CFB, roleB)
			Event.TriggerEvent(Event.QQidip_Eve, roleB, QQEventDefine.QQ_CouplesFB)
			Event.TriggerEvent(Event.Eve_LatestActivityTask, roleA, (EnumGameConfig.LA_CouplesFB, 1))
		#保存随机触发事件配置
		self.random = CouplesFBConfig.RANDOM_EVENT_DICT.get(self.FBcfg.FBId)
		if not self.random:
			print "GE_EXC,can not find eventId(%s) in CouplesFB" % self.FBcfg.FBId
			return
		#保存幸运抽取配置
		self.luck_random = CouplesFBConfig.RANDOM_LUCKY_DICT.get(self.FBcfg.drawId)
		if not self.luck_random:
			print "GE_EXC,can not find drawId(%s) in CouplesFB" % self.FBcfg.drawId
			return
		#pve战斗
		self.monster_fight_data = [self.FBcfg.fightType, self.FBcfg.campId, self.FBcfg.fightrewards, self.FBcfg.monsterHp]
		self.boss_fight_data = [self.FBcfg.bossfightType, self.FBcfg.bosscampId, self.FBcfg.bossrewards, self.FBcfg.bossHp]
		
		self.InitData()
		#注册一个45分钟的Tick
		self.SpecialTickID = cComplexServer.RegTick(FB_KEEP_TIME, self.EndFBCallBack, None)

	def InitData(self):
		#随机配置，根据配置读取数据
		self.enemy_cnt = 0	#保存怪物数量
		self.organ_cnt = 0	#保存机关数量
		self.random_event_dict = {}	#缓存各种事件{格子--》事件}
		self.nothing_index_list = range(1, MAX_INDEX + 1)	#缓存可以随机传送的格子
		EventDict = CouplesFBConfig.EVENT_ID_DICT.get(self.FBcfg.eventId)
		if not EventDict:
			print "GE_EXC,can not find FBId(%s) in InitData" % self.FBcfg.eventId
			return

		for eventId, data in EventDict.iteritems():
			cnt, indexList = data
			random_index = random.sample(indexList, cnt)#随机选取几个格子
			for index in random_index:
				self.random_event_dict[index] = eventId
				self.nothing_index_list.remove(index)
			if CouplesEnumType.Event_Type_2 == eventId:
				self.enemy_cnt += len(random_index)
			if CouplesEnumType.Event_Type_10 == eventId:
				self.organ_cnt += len(random_index)
		self.SyncClient()

	def EndFBCallBack(self, callargv, regparam):
		#45分钟回调
		#当45后玩家还没击杀boss
		if self.boss_state:
			self.boss_state = False
			#给D级奖励
			reward_cfg = CouplesFBConfig.COUPLES_REWARD_DICT.get(self.FBcfg.rewardD)
			if not reward_cfg:
				print "GE_EXC,can't find reward(%s) in EndFBCallBack" % self.FBcfg.rewardD
				return
			self.rewards_data = [5, self.FBcfg.rewardD, reward_cfg]
			for member in self.inFB_role:
				member.BackPublicScene()
				member.SendObj(FB_Already_Pass, [self.rewards_data[0],self.rewards_data[1]])
				self.GetReward(member)
				member.Msg(2, 0, GlobalPrompt.COUPLES_FB_FAILED)
				
	def GetReward(self, role):
		#获取奖励
		if self.boss_state:
			return
		if not self.rewards_data:
			return
		global FB_OBJECT_DICT
		global TEAM_WAIT_DICT
		roleId = role.GetRoleID()
		roleObj = role.GetObj(EnumObj.CouplesFBRewardDict)
		if not roleObj:
			print "GE_EXC,CouplesFB GetReward the roleObj is None!"
			#不存在的话就数据异常了，就直接清除该玩家的副本对象
			if roleId in FB_OBJECT_DICT:
				del FB_OBJECT_DICT[roleId]
			return
		rewardState = roleObj.get(self.FBID, 0)
		if rewardState == 1:#已经领取过了
			return
		reward_cfg = self.rewards_data[2]
		with CouplesPassReward:
			role.SetObj(EnumObj.CouplesFBRewardDict, {self.FBID:1})
			if reward_cfg.gold:
				role.IncMoney(reward_cfg.gold)
			if reward_cfg.bindRMB:
				role.IncBindRMB(reward_cfg.bindRMB)
			if reward_cfg.items:
				for item in reward_cfg.items:
					role.AddItem(*item)
		if roleId in FB_OBJECT_DICT:
			del FB_OBJECT_DICT[roleId]
		#有队伍的话退出队伍
		team = TEAM_WAIT_DICT.get(roleId)
		if team:
			team.Quit(role)
		#北美通用活动
		if Environment.EnvIsNA():
			HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
			HalloweenNAMgr.CouplesFB()

	def MovePos(self, role, nextIndex):
		'''
		这个需要判断index是否超过最大值，然后检测index是否在random_event_dict里，
		在的话就触发事件，不在的话等再来次随机，看是否触发各种隐藏事件
		'''
		roleId = role.GetRoleID()
		nowIndex = self.roleID_pos.get(roleId)
		if not nowIndex:
			return
		#格子超过最大范围
		if nextIndex > MAX_INDEX:
			return
		indexList = CheckIndex(nowIndex)
		if nextIndex not in indexList:#下一步玩家不能到达
			return
		if role.GetCD(EnumCD.Cou_ForbidMoveCD) > 0:
			return
		#触发事件
		if nextIndex in self.random_event_dict:
			eventType = self.random_event_dict.get(nextIndex)
			self.GetFunByType(role, eventType, nowIndex, nextIndex)
		else:
			#不在的话~
			self.RandonEvent(role, nowIndex, nextIndex)
		
	def RoleUseBuff(self, role, buffId):
		#玩家使用buff
		roleId = role.GetRoleID()
		if roleId not in self.role_buff:
			self.role_buff[roleId] = {}
		rolebuff = self.role_buff.get(roleId, {})
		#获取玩家已有的buff
		getted_buffs = rolebuff.get(2, [])
		if buffId not in getted_buffs:
			return
		#从已有列表中删除buff
		getted_buffs.remove(buffId)
		rolebuff[1] = buffId
		if buffId != CouplesEnumType.BUFF_ADD_EFFECT_BUFF2:
			role.SetCD(EnumCD.Cou_BuffCD, 60)
		role.SendObj(FB_Syn_Buffs, self.role_buff[roleId])
		
	def GetUsingBuff(self, role, is_fight = 0):
		#获取正在使用的buff
		roleId = role.GetRoleID()
		rolebuff = self.role_buff.get(roleId)
		if not rolebuff:
			return 0
		using_buff = rolebuff.get(1, 0)
		if not using_buff:
			return 0
		if using_buff == CouplesEnumType.BUFF_ADD_EFFECT_BUFF2:
			if not is_fight:#是战斗的话，返回该使用的buff后，就直接做删除处理
				self.role_buff[roleId][1] = 0
				return CouplesEnumType.BUFF_ADD_EFFECT_BUFF2
		else:
			buff_cd = role.GetCD(EnumCD.Cou_BuffCD)
			if buff_cd <= 0:
				self.role_buff[roleId][1] = 0
				return 0
		return using_buff
	
	def AddMoveCD(self, role, addtype):
		#增加移动CD、战斗胜利CD、幸运抽宝CD
		moveCD = role.GetCD(EnumCD.Cou_MoveFB)
		add_cd = 0
		using_buff = self.GetUsingBuff(role)
		if addtype == 1:#移动CD
			add_cd = MOVE_ADD_CD
			if using_buff == CouplesEnumType.BUFF_DEC_MOVE_BUFF:
				buffcfg = CouplesFBConfig.COUPLES_BUFF_DICT.get(using_buff)
				add_cd = int(MOVE_ADD_CD * (1 - buffcfg.moveCD / 10000.0))
		elif addtype == 2:#战斗CD
			add_cd = FIGHT_ADD_CD
			if using_buff == CouplesEnumType.BUFF_DEC_FIGHT_BUFF:
				buffcfg = CouplesFBConfig.COUPLES_BUFF_DICT.get(using_buff)
				add_cd = int(FIGHT_ADD_CD * (1 - buffcfg.fightCD / 10000.0))
		elif addtype == 3:#buff CD
			add_cd = EVENT_BUFF_CD
		else:#其他CD,目前只有幸运抽奖的CD
			add_cd = EVENT_MOVE_CD
		nowCD = moveCD + add_cd
		if nowCD >= MAX_FORBID_CD:
			role.SetCD(EnumCD.Cou_ForbidMoveCD, nowCD)
		role.SetCD(EnumCD.Cou_MoveFB, nowCD)

	def RandonEvent(self, role, nowIndex, nextIndex):
		#触发随机事件
		event = self.random.RandomOne()
		using_buff = self.GetUsingBuff(role)
		add_cd = 0
		if event in [CouplesEnumType.Randon_Event_1, CouplesEnumType.Randon_Event_2]:
			add_cd = EVENT_MOVE_CD
			if using_buff == CouplesEnumType.BUFF_DEC_EVENT_BUFF:#减少触发事件概率buff
				add_cd = int(EVENT_MOVE_CD * 0.7)
		if event in [CouplesEnumType.Randon_Event_3, CouplesEnumType.Randon_Event_4]:
			add_cd = EVENT_PASS_CD
			if using_buff == CouplesEnumType.BUFF_DEC_EVENT_BUFF:#减少触发事件概率buff
				add_cd = int(EVENT_PASS_CD * 0.7)
		moveCD = role.GetCD(EnumCD.Cou_MoveFB)
		if event == CouplesEnumType.Randon_Event_1:
			role.SetCD(EnumCD.Cou_MoveFB, max(0, moveCD - add_cd))
			role.Msg(2, 0, GlobalPrompt.COUPLES_DELCD_MSG % add_cd)
		elif event == CouplesEnumType.Randon_Event_2:
			role.SetCD(EnumCD.Cou_MoveFB, moveCD + add_cd)
			role.Msg(2, 0, GlobalPrompt.COUPLES_ADDCD_MSG % add_cd)
		elif event == CouplesEnumType.Randon_Event_3:
			self.total_event_time += add_cd
			role.Msg(2, 0, GlobalPrompt.COUPLES_DELPASS_MSG % add_cd)
		elif event == CouplesEnumType.Randon_Event_4:
			self.total_event_time -= add_cd
			role.Msg(2, 0, GlobalPrompt.COUPLES_ADDPASS_MSG % add_cd)
		#增加移动CD
		self.AddMoveCD(role, 1)
		#移动玩家的位置
		self.MoveRolePos(role, nowIndex, nextIndex)
		
	def GetFunByType(self, role, Etype, nowIndex, nextIndex):
		global EventType_Function
		funName = EventType_Function.get(Etype)
		if not funName:
			print "GE_EXC, GetFunByType error Etype(%s)" % Etype
			return
		fun = getattr(self, funName)
		fun(role, nowIndex, nextIndex)
	
	def MonsterFight(self, role, nowIndex, nextIndex):
		#打普通怪，要保存怪物的血量
		#是否能进入战斗状态
		if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
			return
		if role.GetCD(EnumCD.Cou_ForbidMoveCD) > 0:
			return
		fightType, campId, rewardId, maxhp = self.monster_fight_data
		fight = Fight.Fight(fightType)
		left, right = fight.create_camp()
		left.create_online_role_unit(role)
		right.create_monster_camp_unit(campId)
		#检测是否有战斗增益buff
		using_buff = self.GetUsingBuff(role, 1)
		if using_buff:
			buffcfg = CouplesFBConfig.COUPLES_BUFF_DICT.get(using_buff)
			for u in left.pos_units.itervalues():
				u.damage_upgrade_rate += float(buffcfg.fightbuff) / 10000
		#绑定怪物血量
		monster_HP = self.monster_hp_dict.get(nextIndex, maxhp)
		for u in right.pos_units.itervalues():
			u.max_hp = self.FBcfg.monsterHp
			u.hp = monster_HP
		fight.after_fight_fun = self.AfterFight
		fight.after_fight_param = rewardId
		fight.start()
		#=======战斗后处理=========
		if fight.result is None:
			return
		if fight.result != 1:
			#保存血量
			afterFightHp = 0
			for u in right.pos_units.itervalues():
				afterFightHp = u.hp
			self.monster_hp_dict[nextIndex] = afterFightHp
			#战斗失败
			role.SetCD(EnumCD.Cou_ForbidMoveCD, MAX_FORBID_CD + 1)
			role.SetCD(EnumCD.Cou_MoveFB, MAX_FORBID_CD + 1)
			return
		self.monster_hp_dict[nextIndex] = 0
		#怪的数量减一
		if self.enemy_cnt > 0:
			self.enemy_cnt -= 1
			self.CheckState()

		#增加移动CD
		self.AddMoveCD(role, 2)
		#移动玩家的位置
		self.MoveRolePos(role, nowIndex, nextIndex)
	def AfterFight(self, fight):
		if fight.result != 1:
			return
		roles = fight.left_camp.roles
		if not roles:
			return
		role = list(roles)[0]
		rewardId = fight.after_fight_param
		reward_cfg = CouplesFBConfig.COUPLES_REWARD_DICT.get(rewardId)
		if not reward_cfg:
			print "GE_EXC,can't find reward(%s) in EndFBCallBack" % rewardId
			return
		roleId = role.GetRoleID()
		with CouplesKillReward:
			if reward_cfg.gold:
				role.IncMoney(reward_cfg.gold)
				fight.set_fight_statistics(roleId, EnumFightStatistics.EnumMoney, reward_cfg.gold)
			if reward_cfg.bindRMB:
				role.IncBindRMB(reward_cfg.bindRMB)
				fight.set_fight_statistics(roleId, EnumFightStatistics.EnumBindRMB, reward_cfg.bindRMB)
			if reward_cfg.items:
				for item in reward_cfg.items:
					role.AddItem(*item)
				fight.set_fight_statistics(roleId, EnumFightStatistics.EnumItems, reward_cfg.items)

	def LuckDraw(self, role, nowIndex, nextIndex):
		#幸运抽奖
		_, item, gold, bindRMB = self.luck_random.RandomOne()
		tips = ""
		with CouplesLuckyReward:
			if item:
				for reward in item:
					role.AddItem(*reward)
					tips += GlobalPrompt.Item_Tips % (reward[0], reward[1])
			if gold:
				role.IncMoney(gold)
				tips += GlobalPrompt.Money_Tips % (gold)
			if bindRMB:
				role.IncBindRMB(bindRMB)
				tips += GlobalPrompt.BindRMB_Tips % (bindRMB)
		#增加玩家CD
		self.AddMoveCD(role, 4)
		#移动玩家的位置
		self.MoveRolePos(role, nowIndex, nextIndex)
		role.Msg(2, 0, tips)
		
	def RandomTP(self, role, nowIndex, nextIndex):
		#随机传送
		index_list = []
		index_list.extend(self.nothing_index_list)
		if nowIndex in index_list:
			index_list.remove(nowIndex)
		tp_pos = random.choice(index_list)
		self.DelIndex(nextIndex)
		#增加玩家CD
		self.AddMoveCD(role, 1)
		#移动玩家的位置
		self.MoveRolePos(role, nowIndex, tp_pos)

	def TriOrgan(self, role, nowIndex, nextIndex):
		#触发机关
		if self.organ_cnt > 0:
			self.organ_cnt -= 1
			self.CheckState()
		#增加玩家CD
		self.AddMoveCD(role, 4)
		#移动玩家的位置
		self.MoveRolePos(role, nowIndex, nextIndex)
	
	def Obstacles(self, role, nowIndex, nextIndex):
		#障碍物
		return
	
	def AddBuff(self, role, nowIndex, nextIndex):
		#增加buff
		eventId = self.random_event_dict.get(nextIndex, 0)
		if not eventId:
			return
		roleId = role.GetRoleID()
		if roleId not in self.role_buff:
			self.role_buff[roleId] = {}
		if self.role_buff[roleId].has_key(2): 
			self.role_buff[roleId][2].append(eventId)
		else:
			self.role_buff[roleId][2] = [eventId]
		#增加玩家CD
		self.AddMoveCD(role, 3)
		#移动玩家的位置
		self.MoveRolePos(role, nowIndex, nextIndex)
		role.SendObj(FB_Syn_Buffs, self.role_buff[roleId])
		role.Msg(2, 0, GlobalPrompt.COUPLES_ADD_BUFF)

	def FightBoss(self, role, nowIndex, nextIndex):
		#打boss
		if self.enemy_cnt > 0 or self.organ_cnt > 0:
			return
		#是否能进入战斗状态
		if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
			return
		if role.GetCD(EnumCD.Cou_ForbidMoveCD) > 0:
			return
		if not self.boss_state:
			return
		fightType, campId, rewardId, maxhp= self.boss_fight_data
		fight = Fight.Fight(fightType)
		left, right = fight.create_camp()
		left.create_online_role_unit(role)
		right.create_monster_camp_unit(campId)
		#检测是否有战斗增益buff
		using_buff = self.GetUsingBuff(role, 1)
		if using_buff:
			buffcfg = CouplesFBConfig.COUPLES_BUFF_DICT.get(using_buff)
			for u in left.pos_units.itervalues():
				u.damage_upgrade_rate += float(buffcfg.fightbuff) / 10000
				
		#绑定怪物血量
		#绑定怪物血量
		monster_HP = self.monster_hp_dict.get(nextIndex, maxhp)
		for u in right.pos_units.itervalues():
			u.max_hp = self.FBcfg.bossHp
			u.hp = monster_HP
		fight.after_fight_fun = self.AfterFight
		fight.after_fight_param = rewardId
		fight.after_play_fun = self.AfterplayPVE
		fight.start()
		#=======战斗后处理=========
		if fight.result is None:
			return
		#只处理胜利的情况
		if fight.result != 1:
			#保存血量
			afterFightHp = 0
			for u in right.pos_units.itervalues():
				afterFightHp = u.hp
			self.monster_hp_dict[nextIndex] = afterFightHp
			role.SetCD(EnumCD.Cou_ForbidMoveCD, MAX_FORBID_CD + 1)
			role.SetCD(EnumCD.Cou_MoveFB, MAX_FORBID_CD + 1)
			return
		self.monster_hp_dict[nextIndex] = 0
		#设置为结束
		self.boss_state = False
		#取消服务器tick
		cComplexServer.UnregTick(self.SpecialTickID)

	def AfterplayPVE(self, fight):
		#战斗播放完,进行副本结算，发奖
		if fight.result != 1:
			return
		now_time = cDateTime.Seconds()
		#通关时间
		used_time = now_time - self.start_time - self.total_event_time
		rewardId = 0
		score_level = 0
		if used_time <= self.FBcfg.timeS:
			rewardId = self.FBcfg.rewardS
			score_level = 1
		elif used_time <= self.FBcfg.timeA:
			rewardId = self.FBcfg.rewardA
			score_level = 2
		elif used_time <= self.FBcfg.timeB:
			rewardId = self.FBcfg.rewardB
			score_level = 3
		elif used_time <= self.FBcfg.timeC:
			rewardId = self.FBcfg.rewardC
			score_level = 4
		else:
			rewardId = self.FBcfg.rewardD
			score_level = 5
		reward_cfg = CouplesFBConfig.COUPLES_REWARD_DICT.get(rewardId)
		if not reward_cfg:
			print "GE_EXC,can't find reward(%s) in EndFBCallBack" % rewardId
			return
		self.rewards_data = [score_level, rewardId, reward_cfg]
		for member in self.inFB_role:
			member.BackPublicScene()
			member.SendObj(FB_Already_Pass, [self.rewards_data[0],self.rewards_data[1]])
			self.GetReward(member)
		leader_data = self.role_Data.get(self.leader_id)
		if not leader_data:
			return
		leader_name = leader_data[0]
		#持久化操作
		SetDBResult(self.FBcfg.FBId, leader_name, used_time)

	def CheckState(self):
		if self.enemy_cnt == 0 and self.organ_cnt == 0:
			#清除boss周围的障碍物，固定189,190,199 3个位置
			for index in FIXED_OBX_INDEX:
				if index in self.random_event_dict:
					del self.random_event_dict[index]
			self.SyncClient()

	def MoveRolePos(self, role, nowIndex, nextIndex):
		self.roleID_pos[role.GetRoleID()] = nextIndex
		self.DelIndex(nextIndex)
		self.SyncClient()

	def DelIndex(self, index):
		#删除已激活的事件，并将该格子加入可传送列表
		if index in self.random_event_dict:
			del self.random_event_dict[index]
			self.nothing_index_list.append(index)
		if CouplesEnumType.Event_Type_2 not in self.random_event_dict and \
			CouplesEnumType.Event_Type_10 not in self.random_event_dict:
			self.CheckState()

	def SyncClient(self):
		#同步信息
		for member in self.inFB_role:
			member.SendObj(FB_SyncInfo, [self.roleID_pos, self.random_event_dict, self.total_event_time, self.role_Data, int(self.start_time)])
			
	def BeforeExitFB(self, role):
		if role in self.inFB_role:
			self.inFB_role.remove(role)

class CouplesTeam(object):
	max_member_cnt = 2
	def __init__(self, role):
		#分配队伍ID
		global AllotTeamID
		global TEAM_WAIT_DICT
		global TEAMID_TO_TEAM
		AllotTeamID += 1
		TEAM_WAIT_DICT[role.GetRoleID()] = self
		self.team_id = AllotTeamID
		TEAMID_TO_TEAM[self.team_id] = self
		#创建者就是队长
		self.leader = role
		#生成成员列表,需要有顺序
		self.members = [role, ]
		#创建成功，同步客户端
		self.SyncClient()
		
	def IsTeamLeader(self, role):
		return self.leader == role
	
	def IsFull(self):
		return len(self.members) >= self.max_member_cnt

	def Join(self, role):
		global TEAM_WAIT_DICT
		TEAM_WAIT_DICT[role.GetRoleID()] = self
		self.members.append(role)
		self.SyncClient()
		
	def Quit(self, role):
		#离开队伍
		self.RemoveMember(role)
		#通知客户端退出队伍
		role.SendObj(FB_Team_SyncQuit, None)
		#队伍已经没人了
		if not self.members:
			#清理队伍
			self.Clear()
			return
		#队长离开队伍
		if self.leader == role:
			#更换队长，取最近的成员
			self.NewLeader(self.members[0])
		#同步客户端
		self.SyncClient()
		
	def RemoveMember(self, role):
		global TEAM_WAIT_DICT	
		roleId = role.GetRoleID()
		self.members.remove(role)
		del TEAM_WAIT_DICT[roleId]

	def NewLeader(self, role):
		self.leader = role
		#同步客户端
		self.SyncClient()

	def Clear(self):
		#清理队伍数据
		global TEAMID_TO_TEAM
		if self.team_id in TEAMID_TO_TEAM:
			del TEAMID_TO_TEAM[self.team_id]

	def BroadMsg(self, msg, param):
		for member in self.members:
			member.SendObj(msg, param)

	def SyncClient(self):
		#同步队伍所有人队伍数据
		memberData = []
		for member in self.members:
			if member:
				memberData.append(GetRoleTeamData(member))
		if not memberData:
			return
		#leaderId，成员数据
		packData = self.leader.GetRoleID(), memberData
		self.BroadMsg(FB_Team_SyncInfo, packData)
	
	def AddMember(self, role):
		global TEAM_WAIT_DICT
		TEAM_WAIT_DICT[role.GetRoleID()] = self
		self.members.append(role)
		self.SyncClient()
		role.SendObj(FB_Sys_OpenPanel, None)
	
	def CanJoin(self, role):
		global TEAM_WAIT_DICT
		roleId = role.GetRoleID()
		if roleId in TEAM_WAIT_DICT:
			return
		if self.IsFull():
			#提示
			role.Msg(2, 0, GlobalPrompt.TEAM_FULL_PROMPT)
			return False
		return True

def GetTeamByTeamID(teamId):
	global TEAMID_TO_TEAM
	return TEAMID_TO_TEAM.get(teamId)

def GetRoleTeamData(role):
	'''
	用于同步的队员信息
	@param role:
	'''
	#roleId，名字，性别，职业，进阶
	return role.GetRoleID(), role.GetRoleName(), role.GetSex(), role.GetCareer(), role.GetGrade()

def CheckIndex(Nowindex):
	'''
	#获取玩家可移动的格子，返回格子列表
	'''
	divisor = Nowindex / MAP_INDEX_LINE
	remainder = Nowindex % MAP_INDEX_LINE
	adjacent_list = []
	if remainder == 0:#证明为该行的最后一个，相邻的最多3个，上、下，左
		if divisor == 1:#为第一行的最后一个
			#那只有左，下相邻
			adjacent_list.append(Nowindex + MAP_INDEX_LINE)
		elif divisor == MAP_INDEX_VER:#为最后一行的最后一个
			#有左，上相邻
			adjacent_list.append(Nowindex - MAP_INDEX_LINE)
		else:
			#左，上，下相邻
			adjacent_list.append(Nowindex + MAP_INDEX_LINE)
			adjacent_list.append(Nowindex - MAP_INDEX_LINE)
		adjacent_list.append(Nowindex - 1)
	elif remainder == 1:#证明为该行的第一个
		if divisor == 0:#为第一行第一个
			#有右，下相邻
			adjacent_list.append(Nowindex + MAP_INDEX_LINE)
		elif divisor == MAP_INDEX_VER - 1:#为最后行第一个
			adjacent_list.append(Nowindex - MAP_INDEX_LINE)
		else:
			adjacent_list.append(Nowindex + MAP_INDEX_LINE)
			adjacent_list.append(Nowindex - MAP_INDEX_LINE)
		adjacent_list.append(Nowindex + 1)
	else:#可能有上、下，左、右相邻
		if divisor == 0:#第一排，左、右、下
			adjacent_list.append(Nowindex + MAP_INDEX_LINE)
		elif divisor == MAP_INDEX_VER - 1:#最后排左、右、上
			adjacent_list.append(Nowindex - MAP_INDEX_LINE)
		else:#上、下、左、右
			adjacent_list.append(Nowindex + MAP_INDEX_LINE)
			adjacent_list.append(Nowindex - MAP_INDEX_LINE)
		adjacent_list.append(Nowindex + 1)
		adjacent_list.append(Nowindex - 1)
	return adjacent_list

#=====================副本内操作======================
#===================================================
def OnRoleClientLost(role, param):
	'''
	角色客户端掉线
	@param role:
	@param param:
	'''
	global FB_OBJECT_DICT
	global TEAM_WAIT_DICT
	
	if role.GetSceneID() == SCENE_ID:
		role.BackPublicScene()
	roleId = role.GetRoleID()
	#玩家离线后，在组队大厅有队伍时删除处理
	team = TEAM_WAIT_DICT.get(roleId)
	#有队伍则退出队伍
	if team:
		#离开队伍
		team.Quit(role)

	if roleId not in FB_OBJECT_DICT:
		return
	fbObj = FB_OBJECT_DICT.get(roleId)
	fbObj.BeforeExitFB(role)
	
def OnRoleExit(role, param):
	'''
	角色离线
	@param role:
	@param param:
	'''
	global FB_OBJECT_DICT
	global TEAM_WAIT_DICT
	
	if role.GetSceneID() == SCENE_ID:
		role.BackPublicScene()

	roleId = role.GetRoleID()
	team = TEAM_WAIT_DICT.get(roleId)
	#有队伍则退出队伍
	if team:
		#离开队伍
		team.Quit(role)
	if roleId not in FB_OBJECT_DICT:
		return
	fbObj = FB_OBJECT_DICT.get(roleId)
	fbObj.BeforeExitFB(role)

def RoleJoinFB(role, FBId):
	global FB_OBJECT_DICT
	
	roleId = role.GetRoleID()
	if roleId not in FB_OBJECT_DICT:
		return
	fbObj = FB_OBJECT_DICT.get(roleId)
	if not fbObj:
		return
	role.SendObj(FB_Syn_Join, FBId)
	role.Revive(SCENE_ID, 100, 100)
#===========================================================
def RequestStarFB(role, param):
	'''
	客户端请求开始副本
	@param role:
	@param param:
	'''
	FBId = param
	FBcfg = CouplesFBConfig.COUPLES_BASE_DICT.get(FBId)
	if not FBcfg:
		print "GE_EXC,can't find FBId(%s) in RequestJoinFB" % FBId
		return
	#判断玩家是否结婚了
	if role.GetI8(EnumInt8.MarryStatus) != 3:
		return
	
	global FB_OBJECT_DICT
	global TEAMID_TO_TEAM
	global TEAM_WAIT_DICT
	
	roleId = role.GetRoleID()
	team = TEAM_WAIT_DICT.get(roleId)
	if not team:
		return
	if team.leader != role:
		return
	for member in team.members:
		#是否可以进入情缘副本状态
		if not Status.CanInStatus(role, EnumInt1.ST_InCouplesFB):
			return
		if member.GetLevel() < FBcfg.needLevel:
			role.Msg(2, 0, GlobalPrompt.COUPLES_LEVEL_MSG)
			return
		if member.GetDI8(EnumDayInt8.CouplesFBTimes) >= MAX_FB_TIMES:
			role.Msg(2, 0, GlobalPrompt.COUPLES_NO_TIMES)
			return
		if member.GetRoleID() in FB_OBJECT_DICT:#重复创建
			return
		member.SetCD(EnumCD.Cou_ForbidMoveCD, 0)
		member.SetCD(EnumCD.Cou_MoveFB, 0)
	couplesObj = None
	if len(team.members) > 2:
		return
	elif len(team.members) == 1:#只有一个人
		couplesObj = CouplesFB(role, None, roleId, FBcfg)
		FB_OBJECT_DICT[roleId] = couplesObj
		RoleJoinFB(role, FBId)
	elif len(team.members) == 2:
		roleA, roleB = team.members[0], team.members[1]
		HW_bool = CheckHusWife(roleA, roleB)
		if not HW_bool:
			return
		couplesObj = CouplesFB(roleA, roleB, roleId, FBcfg)
		FB_OBJECT_DICT[roleA.GetRoleID()] = couplesObj
		FB_OBJECT_DICT[roleB.GetRoleID()] = couplesObj
		RoleJoinFB(roleA, FBId)
		RoleJoinFB(roleB, FBId)

def RequestExitFB(role, param):
	'''
	客户端请求退出副本
	@param role:
	@param param:
	'''
	backId,_ = param
	global FB_OBJECT_DICT
	roleId = role.GetRoleID()
	if role.GetSceneID() == SCENE_ID:
		role.BackPublicScene()
	fbObj = FB_OBJECT_DICT.get(roleId)
	if fbObj:
		fbObj.BeforeExitFB(role)
	role.CallBackFunction(backId, None)

def RequestMoveFBIndex(role, param):
	'''
	客户端请求移动
	@param role:
	@param param:
	'''
	global FB_OBJECT_DICT
	
	nextIndex = param
	
	roleId = role.GetRoleID()
	
	if roleId not in FB_OBJECT_DICT:
		return
	#有CD
	if role.GetCD(EnumCD.Cou_ForbidMoveCD) > 0:
		return
	FBObj = FB_OBJECT_DICT.get(roleId)
	FBObj.MovePos(role, nextIndex)

def RequestOpenPanel(role, param):
	'''
	打开情缘副本界面
	@param role:
	@param param:
	'''
	global FB_OBJECT_DICT
	global TEAM_WAIT_DICT
	#先同步排行榜
	role.SendObj(FB_Syn_Rank, dict(GetDBResult()))
	#这里先做些预防措施
	roleId = role.GetRoleID()
	roleObj = role.GetObj(EnumObj.CouplesFBRewardDict)
	if roleObj:
		if len(roleObj.values()) >= 1:
			if roleId not in FB_OBJECT_DICT:
				role.SetObj(EnumObj.CouplesFBRewardDict, {})
			else:
				if roleObj.values()[0] == 1:#已领取奖励
					del FB_OBJECT_DICT[roleId]
	if roleId in FB_OBJECT_DICT:#有副本未完成
		fbObj = FB_OBJECT_DICT.get(roleId)
		if not fbObj.boss_state and fbObj.rewards_data:
			role.SendObj(FB_Already_Pass, [fbObj.rewards_data[0],fbObj.rewards_data[1]])
			fbObj.GetReward(role)
		else:
			if not Status.CanInStatus(role, EnumInt1.ST_InCouplesFB):
				return
			RoleJoinFB(role, fbObj.FBcfg.FBId)
		return
	if role.GetI8(EnumInt8.MarryStatus) != 3:
		return
	
	team = TEAM_WAIT_DICT.get(roleId)
	if team:
		if len(team.members) >= 2:
			HW_bool = CheckHusWife(team.members[0],team.members[1])
			if not HW_bool:
				return
		sendList = []
		for member in team.members:
			sendList.append([member.GetRoleID(), member.GetRoleName(), member.GetSex(), member.GetCareer(), member.GetGrade()])
		role.SendObj(FB_Team_Info, [team.leader.GetRoleID(), sendList])
	else:
		#检测情侣是否创建了副本
		marryId = role.GetObj(EnumObj.MarryObj).get(1)
		mrole = cRoleMgr.FindRoleByRoleID(marryId)
		if not mrole:#不在线
			return
		mteam = TEAM_WAIT_DICT.get(marryId)
		if not mteam:
			return
		if mteam.leader != mrole or len(mteam.members) > 2:
			return
		role.SendObj(FB_Team_Info, [mteam.leader.GetRoleID(), [[mrole.GetRoleID(), mrole.GetRoleName(), mrole.GetSex(), mrole.GetCareer(), mrole.GetGrade()]]])

def CheckHusWife(roleA, roleB):
	#检查是否为夫妻
	if roleA.GetI8(EnumInt8.MarryStatus) != 3 or roleB.GetI8(EnumInt8.MarryStatus) != 3:
		return
	marryId = roleA.GetObj(EnumObj.MarryObj).get(1)
	if marryId != roleB.GetRoleID():
		return False
	return True
	
def RequestBuyTimes(role, param):
	'''
	客户端请求购买副本次数
	@param role:
	@param param:
	'''
	#没结婚不能购买
	if role.GetI8(EnumInt8.MarryStatus) != 3:
		return
	vip = role.GetVIP()
	if not vip:
		return
	max_buy_times = 0
	vipCfg = VIPConfig._VIP_BASE.get(vip)
	if vipCfg:
		max_buy_times = vipCfg.couplesTimes
	buyTimes = role.GetDI8(EnumDayInt8.CouplesFBBuyTimes)
	if buyTimes >= max_buy_times:
		role.Msg(2, 0, GlobalPrompt.COUPLES_NO_BUY_TIMES)
		return
	cfg = CouplesFBConfig.COUPLES_BUY_COST.get(buyTimes + 1)
	if not cfg:
		print "GE_EXC,can't find buyTimes(%s) in RequestBuyTimes" % (buyTimes + 1)
		return
	if role.GetUnbindRMB() < cfg.costRMB:
		return
	with CouplesBuyTimes:
		role.IncDI8(EnumDayInt8.CouplesFBBuyTimes, 1)
		role.DecUnbindRMB(cfg.costRMB)
		role.DecDI8(EnumDayInt8.CouplesFBTimes, 1)

def RequestQuickCD(role, param):
	'''
	客户端请求加速CD
	@param role:
	@param param:
	'''
	forbid_cd = role.GetCD(EnumCD.Cou_ForbidMoveCD)
	if forbid_cd < 2:#小于2秒不处理
		return
	bindRMB = forbid_cd / 2
	
	#版本判断
	if Environment.EnvIsNA():
		bindRMB *= 3
	
	if role.GetUnbindRMB() < bindRMB:
		return
	with CouplesQuickCD:
		role.DecUnbindRMB(bindRMB)
		role.SetCD(EnumCD.Cou_ForbidMoveCD, 0)
		role.SetCD(EnumCD.Cou_MoveFB, 0)
		
def RequestRoleUseBuff(role, param):
	'''
	客户端请求使用buff
	@param role:
	@param param:
	'''
	buffId = param
	
	global FB_OBJECT_DICT
	roleId = role.GetRoleID()
	if roleId not in FB_OBJECT_DICT:
		return
	fbObj = FB_OBJECT_DICT.get(roleId)
	fbObj.RoleUseBuff(role, buffId)
	
def RequestFastThrough(role, param):
	'''
	客户端请求情缘副本一键收益
	@param role:
	@param param:
	'''
	FBId, index = param	#index=1为免费收获，2为完美收获
	if index not in (1, 2):
		return
	
	#判断玩家是否结婚了
	if role.GetI8(EnumInt8.MarryStatus) != 3:
		return
	
	global FB_OBJECT_DICT
	if role.GetRoleID() in FB_OBJECT_DICT:#有副本未完成
		return
	
	global TEAM_WAIT_DICT
	if TEAM_WAIT_DICT.get(role.GetRoleID()):#有队伍
		return
	
	if role.GetDI8(EnumDayInt8.CouplesFBTimes) >= MAX_FB_TIMES:
		role.Msg(2, 0, GlobalPrompt.COUPLES_NO_TIMES)
		return
	
	FBcfg = CouplesFBConfig.COUPLES_BASE_DICT.get(FBId)
	if not FBcfg:
		print "GE_EXC,can't find FBId(%s) in RequestJoinFB" % FBId
		return
	
	if FBcfg.needLevel > role.GetLevel():
		return
	
	vip = role.GetVIP()
	if index == 1:#免费收获
		if role.GetBindRMB() < FBcfg.freeQuick:
			return
		if vip < FBcfg.FreeneedVIP:
			return
	elif index == 2:#完美收获
		if role.GetUnbindRMB() < FBcfg.RMBQuick:
			return
		if vip < FBcfg.RMBneedVIP:
			return
	else:
		return
	
	with CouplesQuickThrough:
		role.IncDI8(EnumDayInt8.CouplesFBTimes, 1)
		rewards_data = []
		if index == 1:
			role.DecBindRMB(FBcfg.freeQuick)
			rewards_data = [2, FBcfg.rewardA]
		else:
			role.DecUnbindRMB(FBcfg.RMBQuick)
			rewards_data = [1, FBcfg.rewardS]
		
		reward_cfg = CouplesFBConfig.COUPLES_REWARD_DICT.get(rewards_data[1])
		if not reward_cfg:
			print "GE_EXC,can't find reward(%s) in EndFBCallBack" % rewards_data[1]
			return
		tips = ""
		if reward_cfg.gold:
			role.IncMoney(reward_cfg.gold)
			tips += GlobalPrompt.Money_Tips % reward_cfg.gold
		if reward_cfg.bindRMB:
			role.IncBindRMB(reward_cfg.bindRMB)
			tips += GlobalPrompt.BindRMB_Tips % reward_cfg.bindRMB
		if reward_cfg.items:
			for item in reward_cfg.items:
				role.AddItem(*item)
				tips += GlobalPrompt.Item_Tips % (item[0], item[1])
					
		role.SendObj(FB_Already_Pass, [rewards_data[0], rewards_data[1]])
		
		Event.TriggerEvent(Event.Eve_FB_CFB, role)
		Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_CouplesFB, 1))
		
#=====================组队相关========================
def RequestCreateFBTeam(role, param):
	'''
	客户端请求创建情缘队伍
	@param role:
	@param param:
	'''
	global TEAM_WAIT_DICT
	global FB_OBJECT_DICT
	
	if role.GetLevel() < MIN_CREATE_TEAM_LEVEL:
		return
	roleId = role.GetRoleID()
	if roleId in TEAM_WAIT_DICT:
		return
	#是否还有副本收益次数
	if role.GetDI8(EnumDayInt8.CouplesFBTimes) >= MAX_FB_TIMES:
		return
	#判断是否结婚了
	if role.GetI8(EnumInt8.MarryStatus) != 3:
		return
	roleId = role.GetRoleID()
	#判断是否有副本
	if roleId in FB_OBJECT_DICT:
		return
	#创建队伍
	CouplesTeam(role)

def RequestExitFBTeam(role, param):
	'''
	退出队伍
	@param role:
	'''
	global TEAM_WAIT_DICT
	
	roleId = role.GetRoleID()
	team = TEAM_WAIT_DICT.get(roleId)
	if not team:
		return
	team.Quit(role)

def RequestJoinFBTeam(role, param):
	'''
	申请加入队伍
	@param role:
	@param param:
	'''
	global FB_OBJECT_DICT
	global TEAM_WAIT_DICT
	
	leader_id = param
	team = TEAM_WAIT_DICT.get(leader_id)
	if not team:
		#提示
		role.Msg(2, 0, GlobalPrompt.TEAM_NOT_EXIST_PROMPT)
		return
	#是否还有副本收益次数
	if role.GetDI8(EnumDayInt8.CouplesFBTimes) >= MAX_FB_TIMES:
		return
	if role.GetI8(EnumInt8.MarryStatus) != 3:#没结婚
		return
	marryObj = role.GetObj(EnumObj.MarryObj)
	if not marryObj:
		return
	if marryObj.get(1) != leader_id:#不是情侣
		return
	#判断自己是否已开启副本
	roleId = role.GetRoleID()
	if roleId in FB_OBJECT_DICT:
		return
	team.Join(role)
	
def RequestInviteFBTeam(role, param):
	'''
	组队邀请
	@param role:
	@param param:
	'''
	global TEAM_WAIT_DICT
	roleId = role.GetRoleID()
	team = TEAM_WAIT_DICT.get(roleId)
	if not team:
		return
	if team.IsFull():
		return
	if role.GetI8(EnumInt8.MarryStatus) != 3:#没结婚
		return
	marryObj = role.GetObj(EnumObj.MarryObj)
	if not marryObj:
		return
	desRoleId = marryObj.get(1)

	global FB_OBJECT_DICT
	if desRoleId in FB_OBJECT_DICT:#上次的奖励未领取
		role.Msg(2, 0, GlobalPrompt.COUPLES_INVETE_MSG2)
		return
	# 发送邀请
	desRole = cRoleMgr.FindRoleByRoleID(desRoleId)
	if not desRole:
		#提示
		role.Msg(2, 0, GlobalPrompt.COUPLES_INVITE_MSG)
		return
	if desRoleId in TEAM_WAIT_DICT:
		#提示
		role.Msg(2, 0, GlobalPrompt.TEAM_HAS_TEAM_PROMPT)
		return
	role.Msg(2, 0, GlobalPrompt.COUPLES_INVITE_SUC)
	#队伍id, 玩家名, 副本ID
	desRole.SendObjAndBack(FB_Show_Invite, (team.team_id, role.GetRoleName()), 120, InviteBack, (team.team_id))	

def InviteBack(role, callargv, regparam):
	'''
	邀请回调
	@param role:
	@param callargv:
	@param regparam:
	'''
	teamId = regparam
	#被邀请的角色回调函数
	if callargv != 1:
		#拒绝加入组队
		return
	if teamId == 0:
		#提示
		role.Msg(2, 0, GlobalPrompt.TEAM_NOT_EXIST_PROMPT)
		return
	team = GetTeamByTeamID(teamId)
	if not team:
		#提示
		role.Msg(2, 0, GlobalPrompt.TEAM_NOT_EXIST_PROMPT)
		return
	global FB_OBJECT_DICT
	roleId = role.GetRoleID()
	if roleId in FB_OBJECT_DICT:
		return
	if not team.CanJoin(role):
		return
	#加入队伍
	team.AddMember(role)
	
@PublicScene.RegSceneBeforeLeaveFun(SCENE_ID)
def AfterBeforeLeave(scene, role):
	#退出情缘副本状态
	Status.Outstatus(role, EnumInt1.ST_InCouplesFB)
	
@PublicScene.RegSceneAfterJoinRoleFun(SCENE_ID)
def AfterJoinRole(scene, role):
	global TEAM_WAIT_DICT
	global FB_OBJECT_DICT
	
	#强制进入情缘副本状态
	Status.ForceInStatus(role, EnumInt1.ST_InCouplesFB)
	
	team = TEAM_WAIT_DICT.get(role.GetRoleID())
	if team:
		team.Quit(role)
	fbObj = FB_OBJECT_DICT.get(role.GetRoleID())
	if not fbObj:
		return
	fbObj.inFB_role.add(role)
	fbObj.CheckState()
	role.SendObj(FB_Syn_Buffs, fbObj.role_buff.get(role.GetRoleID(),{}))
	fbObj.SyncClient()
#===================持久化数据操作==================
def SetDBResult(FBId, name, time):
	#每个副本只存前5名
	global COUPLES_RANK_DICT
	if FBId not in COUPLES_RANK_DICT:
		COUPLES_RANK_DICT[FBId] = []
	rank_list = COUPLES_RANK_DICT.get(FBId, [])
	for data in rank_list:
		if name == data[0]:#同名的话，通过时间更短就直接更改时间
			if time >= data[1]:
				return
			else:
				data[1] = time
				return
	if len(rank_list) < 5:
		rank_list.append([name, time])
	else:
		rank_list.sort(key = lambda x:x[1], reverse = True)
		last_rank = rank_list[0]
		if time < last_rank[1]:
			rank_list.remove(last_rank)
			rank_list.append([name, time])
		if len(rank_list) > 5:
			rank_list = rank_list[0:5]
	COUPLES_RANK_DICT.changeFlag = True
	
def GetDBResult():
	global COUPLES_RANK_DICT
	return COUPLES_RANK_DICT

def CouplesRankAfterLoadDB():
	pass
#===================持久化数据操作==================
	
if "_HasLoad" not in dir():
	if Environment.HasLogic or Environment.HasWeb:
		#情缘副本通关排行字典
		COUPLES_RANK_DICT = Contain.Dict("CouplesFB_Rank_List", (2038, 1, 1), CouplesRankAfterLoadDB, isSaveBig = False)
	if Environment.HasLogic:
		BuildEventType_Function()
		
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_ClientLost, OnRoleClientLost)
		Event.RegEvent(Event.Eve_BeforeExit, OnRoleExit)
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CouplesFB_Create_Team", "客户端请求创建情缘队伍"), RequestCreateFBTeam)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CouplesFB_Exit_Team", "客户端请求退出情缘队伍"), RequestExitFBTeam)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CouplesFB_Join_Team", "客户端请求加入情缘队伍"), RequestJoinFBTeam)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CouplesFB_Invite_Team", "客户端请求邀请玩家加入情缘队伍"), RequestInviteFBTeam)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CouplesFB_Request_OpenPanel", "客户端打开情缘副本界面"), RequestOpenPanel)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CouplesFB_Buy_Times", "客户端请求购买副本次数"), RequestBuyTimes)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CouplesFB_Request_QuickCD", "客户端请求加速CD"), RequestQuickCD)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CouplesFB_Request_Start", "客户端请求开始情缘副本"), RequestStarFB)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CouplesFB_Move_Index", "客户端请求移动"), RequestMoveFBIndex)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CouplesFB_Request_Exit", "客户端请求退出情缘副本"), RequestExitFB)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CouplesFB_Request_useBuff", "客户端请求使用buff"), RequestRoleUseBuff)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CouplesFB_Request_FastThrough", "客户端请求情缘副本一键收益"), RequestFastThrough)
