#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.UnionKuaFuWar.UnionKuaFuWarCross")
#===============================================================================
# 公会圣域争霸跨服进程
#===============================================================================
import random
import cComplexServer
import cRoleMgr
import cSceneMgr
import cProcess
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumAward, GlobalPrompt
from World import Define
from Util.File import CircularBuffer
from ComplexServer.Log import AutoLog
from ComplexServer.Time import Cron
from Game.Activity.Award import AwardMgr
from Game.Activity.Title import Title
from Game.Fight import Fight, Middle
from Game.Role import Status, Call, Event
from Game.Role.Data import EnumTempInt64, EnumInt1, EnumCD, EnumTempObj
from Game.UnionKuaFuWar import UnionKuaFuWarConfig, UnionKuaFuWarRank



if "_HasLoad" not in dir():
	IS_READY = False						#跨服圣域争霸是否在准备阶段
	IS_START = False						#跨服圣域争霸是否开始
	
	WAR_TICK_ID = 0							#圣域争霸tickId
	FIGHT_CD = 15							#战斗CD
	SHOW_WAR_DATA_TICK_SEC = 5 * 60			#显示圣域争霸数据tick秒数
	CHALLENGE_RANDOM_ROLE_CNT = 10			#挑战随机的对手数量
	GATE_PANEL_DATA_TICK_SEC = 4 * 60		#显示城门面板数据tick秒数
	END_KICK_ROLE_TICK_SEC = 20				#结束踢掉玩家tick秒数
	MAX_RECORD_CNT = 5						#最大记录数量
	
	WAR_MGR_DICT = {}						#争霸管理字典
	ROLE_ZONEID_DICT = {}					#角色区域ID字典
	
	#消息
	Union_KuaFu_War_Cross_Show_Role_Data = AutoMessage.AllotMessage("Union_KuaFu_War_Cross_Show_Role_Data", "通知客户端显示公会圣域争霸角色数据")
	Union_KuaFu_War_Cross_Show_Gate_Data = AutoMessage.AllotMessage("Union_KuaFu_War_Cross_Show_Gate_Data", "通知客户端显示公会圣域争霸城门数据")
	Union_KuaFu_War_Cross_Show_Rank = AutoMessage.AllotMessage("Union_KuaFu_War_Cross_Show_Rank", "通知客户端显示公会圣域争霸排行榜")
	Union_KuaFu_War_Cross_Show_Record = AutoMessage.AllotMessage("Union_KuaFu_War_Cross_Show_Record", "通知客户端显示公会圣域争霸记录")
	Union_KuaFu_War_Cross_Show_Gate_Panel = AutoMessage.AllotMessage("Union_KuaFu_War_Cross_Show_Gate_Panel", "通知客户端显示公会圣域争霸城门面板")
	Union_KuaFu_War_Cross_Show_End_Panel = AutoMessage.AllotMessage("Union_KuaFu_War_Cross_Show_End_Panel", "通知客户端显示公会圣域争霸结束面板")
	Union_KuaFu_War_Cross_Show_Buff = AutoMessage.AllotMessage("Union_KuaFu_War_Cross_Show_Buff", "通知客户端显示公会圣域争霸Buff")
	

class WarRole(object):
	def __init__(self, role, zoneName):
		self.role = role
		#基础角色数据
		self.role_id = role.GetRoleID()
		self.role_name = role.GetRoleName()
		self.role_level = role.GetLevel()
		self.role_sex = role.GetSex()
		self.role_grade = role.GetGrade()
		self.role_career = role.GetCareer()
		self.role_zdl = role.GetZDL()
		self.role_wing_id = role.GetWingID()
		self.role_union_id = role.GetUnionID()
		self.role_fashion_clothes = role.GetTI64(EnumTempInt64.FashionClothes)
		self.role_fashion_hat = role.GetTI64(EnumTempInt64.FashionHat)
		self.role_fashion_weapons = role.GetTI64(EnumTempInt64.FashionWeapons)
		self.role_fashion_state = role.GetI1(EnumInt1.FashionViewState)
		
		self.role_zone_name = zoneName	#服名字
		
		self.buff_id = 0
		self.goddess_buff_level = 0
		
		self.circular_record = CircularBuffer.CircularBuffer(MAX_RECORD_CNT)		#争霸记录对象
		
		#争霸数据
		self.score = 0
		self.win_streak = 0
		self.lose_streak = 0
		
		self.update_fight_data()
		
	def get_role_total_hp(self, is_max = False):
		#返回最大血量或当前血量
		if is_max is False:
			return self.bind_hp.get("total_hp", 0)
		
		role_data, heros_data = self.fight_data
		total_hp = role_data[Middle.MaxHP]
		for hero_value in heros_data.itervalues():
			total_hp += hero_value[Middle.MaxHP]
		return total_hp
	
	def update_fight_data(self):
		#更新战斗数据
		self.fight_data = Middle.GetRoleData(self.role, use_property_X=True)
		max_hp = self.get_role_total_hp(True)
		#[最大血量, 当前血量]
		self.hp = [max_hp, max_hp]
		self.bind_hp = {}
	
	def update_hp(self):
		self.hp[1] = self.get_role_total_hp()
		
	def is_full_hp(self):
		if self.hp[1] >= self.hp[0]:
			return True
		return False
		
	def get_show_data(self):
		return (self.role_id, self.role_name, self.role_sex, self.role_grade, self.role_career, self.role_zdl,
			self.role_wing_id, self.role_fashion_clothes, self.role_fashion_hat, self.role_fashion_weapons, self.role_fashion_state)
	
	def add_record(self, record):
		self.circular_record.push_front(record)
		
	def win(self):
		#连杀+1
		self.win_streak += 1
		self.lose_streak = 0
		
		#更新血量
		self.update_hp()
		
		#女神庇护buff
		self.goddess_buff_level = 0
		
	def lost(self):
		#设置连胜连败
		self.win_streak = 0
		self.lose_streak += 1
		
		#更新战斗数据
		self.update_fight_data()
		
		if not self.goddess_buff_level:
			if self.lose_streak < 2:
				return
				
		goddessBuffConfig = UnionKuaFuWarConfig.UNION_KUAFU_WAR_GODDESS_BUFF.get(self.goddess_buff_level + 1)
		if not goddessBuffConfig:
			return
				
		#女神庇护buff
		self.goddess_buff_level += 1
		
		#提示
		if not self.role.IsKick():
			self.role.Msg(2, 0, GlobalPrompt.UNION_KUAFU_WAR_GODDESS_PROMPT % goddessBuffConfig.buffName)
		
		
	def create_buff(self, camp):
		for u in camp.pos_units.itervalues():
			#女神庇护buff
			if self.goddess_buff_level > 0:
				goddessBuffConfig = UnionKuaFuWarConfig.UNION_KUAFU_WAR_GODDESS_BUFF.get(self.goddess_buff_level)
				if goddessBuffConfig:
					u.damage_upgrade_rate += goddessBuffConfig.damageUpgradeRate / 10000.0
					u.damage_reduce_rate += goddessBuffConfig.damageReduceRate / 10000.0
			
			#公会神力buff
			warUnion = GetRoleWarUnion(self.role)
			for buffType, buffLevel in warUnion.buff_dict.iteritems():
				buffConfig = UnionKuaFuWarConfig.UNION_KUAFU_WAR_BUFF_BASE.get((buffType, buffLevel))
				if not buffConfig:
					continue
				
				if buffType == 1:
					#攻击
					u.attack_p = u.attack_p + (u.attack_p * (buffConfig.pctValue / 10000)) + buffConfig.absValue
					u.attack_m = u.attack_m + (u.attack_m * (buffConfig.pctValue / 10000)) + buffConfig.absValue
				elif buffType == 2:
					#生命
					addHp = (u.max_hp * (buffConfig.pctValue / 10000)) + buffConfig.absValue
					if u.hp >= u.max_hp:
						u.hp += addHp
					u.max_hp += addHp
				elif buffType == 3:
					#暴击
					u.crit = u.crit + (u.crit * (buffConfig.pctValue / 10000)) + buffConfig.absValue
				elif buffType == 4:
					#破档
					u.puncture = u.puncture + (u.puncture * (buffConfig.pctValue / 10000)) + buffConfig.absValue
				elif buffType == 5:
					#破防
					u.anti_broken = u.anti_broken + (u.anti_broken * (buffConfig.pctValue / 10000)) + buffConfig.absValue
				
						
class WarUnion(object):
	def __init__(self, unionId, unionName, zoneName):
		self.union_id = unionId
		self.union_name = unionName
		self.zone_name = zoneName
		self.member_roleid_set = set()
		self.online_role_set = set()
		
		#公会积分
		self.score = 0
		
		#公会buff
		self.buff_dict = {}
		
		#公会个人排行
		self.role_little_rank = UnionKuaFuWarRank.UnionKuaFuUnionRoleRank(UnionKuaFuWarConfig.UNION_ROLE_RANK_CNT)
		
	def join(self, role):
		roleId = role.GetRoleID()
		self.member_roleid_set.add(roleId)
		self.online_role_set.add(role)
		
	def in_role_rank(self, warRole, isDec = False):
		if isDec is True:
			#只有扣分才触发删除
			if warRole.role_id in self.role_little_rank.data:
				del self.role_little_rank.data[warRole.role_id]
			else:
				#扣分了，还不在榜上面，不入榜
				return
		#服务器名，角色名，个人积分
		self.role_little_rank.HasData(warRole.role_id, [warRole.role_name, warRole.role_zdl, warRole.score])
	
	def msg(self, prompt):
		#打包提示
		cRoleMgr.MsgPack(8, 0, prompt)
		for role in self.online_role_set:
			#公会频道
			role.BroadMsg()
			
	def activate_buff(self, buffType, warRole, buffZDLConfig):
		buffLevel = self.buff_dict.get(buffType, 0)
		
		buffBaseConfig = UnionKuaFuWarConfig.UNION_KUAFU_WAR_BUFF_BASE.get((buffType, buffLevel + 1))
		if not buffBaseConfig:
			return
		
		#已经是最大等级
		if buffLevel + 1 > buffBaseConfig.maxLevel:
			return
		
		self.buff_dict[buffType] = buffLevel + 1
		
		#通知所有公会成员
		for role in self.online_role_set:
			ShowBuff(role)
			
		#全公会提示
		self.msg(GlobalPrompt.UNION_KUAFU_WAR_BUFF_PROMPT % (warRole.role_name, buffZDLConfig.buffName, buffBaseConfig.buffName))
		
class GateMgr(object):
	def __init__(self, warMgr, gateId):
		self.war_mgr = warMgr
		self.gate_id = gateId
		self.is_broken = False
		self.gate_roleid_set = set()
		self.win_streak_roleid_set = set()
		
		#城门配置
		self.gate_config = UnionKuaFuWarConfig.UNION_KUAFU_WAR_GATE[gateId]
		#城门血量
		self.gate_hp = self.gate_config.gateHp
		
	def join(self, role):
		roleId = role.GetRoleID()
		self.gate_roleid_set.add(roleId)
		self.in_or_out_win_streak(GetWarRole(role))
		
	def leave(self, role):
		roleId = role.GetRoleID()
		#清理
		#城门角色
		self.gate_roleid_set.discard(roleId)
		#城门连杀
		self.win_streak_roleid_set.discard(roleId)
		
	def get_gate_show_data(self, role):
		roleId = role.GetRoleID()
		
		randomChallengeRoleIdList = random.sample(self.gate_roleid_set, min(len(self.gate_roleid_set), CHALLENGE_RANDOM_ROLE_CNT))
		randomWinSteakRoleIdList = random.sample(self.win_streak_roleid_set, min(len(self.win_streak_roleid_set), CHALLENGE_RANDOM_ROLE_CNT))
		
		warUnion = GetRoleWarUnion(role)
		union_role_id_set = set()
		if warUnion:
			union_role_id_set = warUnion.member_roleid_set

		#获取要显示的数据
		GETWARROLEBYROLEID = self.war_mgr.get_war_role_by_roleid
		challengeData = {}
		for challengeRoleId in randomChallengeRoleIdList:
			if challengeRoleId == roleId:
				#城门不显示自己
				continue
			if challengeRoleId in union_role_id_set:
				#不能攻击自己公会的成员
				continue
			war_role = GETWARROLEBYROLEID(challengeRoleId)
			if not war_role:
				continue
			challengeData[challengeRoleId] = [war_role.role_zone_name, war_role.role_name, war_role.role_level]
		
		winSteakData = {}
		for winSteakRoleId in randomWinSteakRoleIdList:
			if winSteakRoleId == roleId:
				#城门不显示自己
				continue
			if winSteakRoleId in union_role_id_set:
				#不能攻击自己公会的成员
				continue
			war_role = GETWARROLEBYROLEID(winSteakRoleId)
			if not war_role:
				continue
			winSteakData[winSteakRoleId] = [war_role.win_streak, war_role.role_zone_name, war_role.role_name, war_role.role_level]
		
		return challengeData, winSteakData
	
	def dec_hp(self):
		if self.is_broken is True:
			return
		
		self.gate_hp -= 1
		
		if self.gate_hp > 0:
			return
		self.is_broken = True
		
		#破城门清理玩家
		FINDROLEBYROLEID = cRoleMgr.FindRoleByRoleID
		for roleId in self.gate_roleid_set:
			role = FINDROLEBYROLEID(roleId)
			if not role:
				continue
			role.SetTI64(EnumTempInt64.UnionKuaFuWarGateID, 0)
			#显示
			ShowRoleData(role)
			ShowGateData(role)
		
		self.gate_roleid_set.clear()
		self.role_winning_streak_dict = {}
		
		#检测活动是否结束
		self.war_mgr.is_war_over()
		
		#传闻
		self.war_mgr.scene.Msg(8, 0, GlobalPrompt.UNION_KUAFU_WAR_GATE_BROKEN_HEARSAY % self.gate_config.gateName)
		
	def in_or_out_win_streak(self, warRole):
		if warRole.win_streak > 0:
			if warRole.win_streak > 5:
				#至少5连杀才能进榜
				if warRole.role_id in self.win_streak_roleid_set:
					return
				else:
					self.win_streak_roleid_set.add(warRole.role_id)
		else:
			#无连杀清理
			self.win_streak_roleid_set.discard(warRole.role_id)
		
		
class WarMgr(object):
	def __init__(self, zoneId, scene, zoneConfig):
		self.zone_id = zoneId
		self.war_role_dict = {}
		self.war_union_dict = {}
		self.join_roleid_set = set()
		self.gate_mgr_dict = {}
		self.processid_set = set()		#进程ID集合
		self.scene = scene
		self.zone_config = zoneConfig
		
		self.champion_union_name = ""		#冠军公会名
		self.champion_role_name = ""		#冠军圣域独裁者角色名
		self.champion_zone_name = ""		#冠军服务器名
		
		self.has_rewarded = False			#是否已经发奖
		
		for gateId in UnionKuaFuWarConfig.UNION_KUAFU_WAR_GATE.iterkeys():
			self.gate_mgr_dict[gateId] = GateMgr(self, gateId)
		
		#公会排行
		self.total_union_little_rank = UnionKuaFuWarRank.UnionKuaFuUnionRank(UnionKuaFuWarConfig.TOTAL_UNION_RANK_CNT)
		#个人总榜
		self.total_role_little_rank = UnionKuaFuWarRank.UnionKuaFuTotalRoleRank(UnionKuaFuWarConfig.TOTAL_ROLE_RANK_CNT)
		
		#注册tick循环同步圣域争霸数据
		cComplexServer.RegTick(SHOW_WAR_DATA_TICK_SEC, self.show_war_data)
		
	
	def get_war_role_by_roleid(self, roleId):
		return self.war_role_dict.get(roleId)
	
	def get_war_union(self, unionId):
		return self.war_union_dict.get(unionId)
		
	def get_gate_mgr(self, gateId):
		return self.gate_mgr_dict.get(gateId)
	
	def inc_role_score(self, warRole, incScore):
		warRole.score += incScore
		
		warUnion = self.get_war_union(warRole.role_union_id)
		if warUnion:
			#增加公会积分
			warUnion.score += incScore
			#公会总榜
			self.in_total_union_rank(warUnion)
			#公会个人榜
			warUnion.in_role_rank(warRole)
		#个人总榜
		self.in_total_role_rank(warRole)
		
	def dec_role_score(self, warRole, decScore):
		warRole.score -= decScore
		
		warUnion = self.get_war_union(warRole.role_union_id)
		if warUnion:
			#减少公会积分
			warUnion.score -= decScore
			#公会总榜
			self.in_total_union_rank(warUnion, True)
			#公会个人榜
			warUnion.in_role_rank(warRole, True)
		#个人总榜
		self.in_total_role_rank(warRole, True)
		
	def join_gate(self, role, gateMgr):
		role.SetTI64(EnumTempInt64.UnionKuaFuWarGateID, gateMgr.gate_id)
		gateMgr.join(role)
		
	def leave_gate(self, role, gateMgr):
		gateId = GetRoleGateID(role)
		if not gateId:
			return
		role.SetTI64(EnumTempInt64.UnionKuaFuWarGateID, 0)
		gateMgr.leave(role)
	
	def join_role(self, role, zoneName, unionName):
		roleId = role.GetRoleID()
		
		#是否有warRole对象
		warRole = self.war_role_dict.get(roleId)
		if not warRole:
			self.war_role_dict[roleId] = warRole = WarRole(role, zoneName)
	
		warRole.role = role
		#重新加入圣域争霸要更新战斗数据，回复血量，清空连胜连败，女神庇护buff
		warRole.update_fight_data()
		warRole.win_streak = 0
		warRole.lose_streak = 0
		warRole.goddess_buff_level = 0
		
		#保存圣域争霸角色对象
		role.SetTempObj(EnumTempObj.UnionKuaFuWarRole, warRole)
		role.SetTempObj(EnumTempObj.UnionKuaFuWarMgr, self)
		#圣域争霸公会
		unionId = role.GetUnionID()
		warUnion = self.war_union_dict.get(unionId)
		if not warUnion:
			self.war_union_dict[unionId] = warUnion = WarUnion(unionId, unionName, zoneName)
		
		role.SetTempObj(EnumTempObj.UnionKuaFuWarUnion, warUnion)
		warUnion.join(role)
		
	def in_total_union_rank(self, warUnion, isDec = False):
		if isDec is True:
			#只有扣分才触发删除
			if warUnion.union_id in self.total_union_little_rank.data:
				del self.total_union_little_rank.data[warUnion.union_id]
			else:
				#扣分了，还不在榜上面，不入榜
				return
		#服务器名，公会名，公会积分
		self.total_union_little_rank.HasData(warUnion.union_id, [warUnion.zone_name, warUnion.union_name, warUnion.score])
		
	def in_total_role_rank(self, warRole, isDec = False):
		if isDec is True:
			#只有扣分才触发删除
			if warRole.role_id in self.total_role_little_rank.data:
				del self.total_role_little_rank.data[warRole.role_id]
			else:
				#扣分了，还不在榜上面，不入榜
				return
		#服务器名，角色名，个人积分
		self.total_role_little_rank.HasData(warRole.role_id, [warRole.role_zone_name, warRole.role_name, warRole.score])
		
	def exit_scene(self, role):
		#若有城门离开场景要扣分
		gateId = GetRoleGateID(role)
		if gateId:
			gateMgr = self.get_gate_mgr(gateId)
			if gateMgr:
				warRole = GetWarRole(role)
				self.dec_role_score(warRole, gateMgr.gate_config.lostScore)
				#离开城门
				self.leave_gate(role, gateMgr)
		#离开公会在线集合
		warUnion = GetRoleWarUnion(role)
		if warUnion:
			warUnion.online_role_set.discard(role)
		
	def is_war_over(self):
		#判断所有城门是否已破
		for gateMgr in self.gate_mgr_dict.itervalues():
			if gateMgr.gate_hp > 0:
				return
		
		#发奖
		self.rank_reward()
		
		#注册tick，把本区域玩家踢出跨服
		cComplexServer.RegTick(END_KICK_ROLE_TICK_SEC, self.kick_all_role)
		
	def show_war_data(self, callArgv, regparam):
		if (IS_READY is False) and (IS_START is False):
			return
		
		for role in self.scene.GetAllRole():
			ShowGateData(role)
			ShowRank(role)
			ShowRoleData(role)
			
		cComplexServer.RegTick(SHOW_WAR_DATA_TICK_SEC, self.show_war_data)
		
	def rank_reward(self):
		#是否已经发奖
		if self.has_rewarded is True:
			return
		self.has_rewarded = True
		
		#个人总榜奖励
		TotalRoleRankReward(self)
		#公会相关排行榜奖励
		UnionRankReward(self)
		
		for role in self.scene.GetAllRole():
			#显示当前最新的数据
			ShowGateData(role)
			ShowRank(role)
			ShowRoleData(role)
			#显示结束面板(圣域独裁者角色名，冠军公会名，服务器名，倒计时秒数)
			role.SendObj(Union_KuaFu_War_Cross_Show_End_Panel, (self.champion_role_name, self.champion_union_name, self.champion_zone_name, END_KICK_ROLE_TICK_SEC))

	def kick_all_role(self, callArgv, regparam):
		#把玩家T出跨服场景
		for role in self.scene.GetAllRole():
			role.GotoLocalServer(None, None)

def GetWarRole(role):
	return role.GetTempObj(EnumTempObj.UnionKuaFuWarRole)

def GetWarMgr(role):
	return role.GetTempObj(EnumTempObj.UnionKuaFuWarMgr)

def GetRoleGateID(role):
	return role.GetTI64(EnumTempInt64.UnionKuaFuWarGateID)

def GetRoleWarUnion(role):
	return role.GetTempObj(EnumTempObj.UnionKuaFuWarUnion)

def GetWinStreakToHearsay(winStreak):
	if winStreak == 10:
		return GlobalPrompt.UNION_KUAFU_WAR_WIN_STREAK_HEARSAY2
	elif winStreak == 20:
		return GlobalPrompt.UNION_KUAFU_WAR_WIN_STREAK_HEARSAY3
	elif winStreak == 30:
		return GlobalPrompt.UNION_KUAFU_WAR_WIN_STREAK_HEARSAY4
	else:
		return None
		
def ChooseGate(role, gateId, backId):
	warMgr = GetWarMgr(role)
	if not warMgr:
		return
	#是否已经有在城门中
	nowGateId = GetRoleGateID(role)
	if nowGateId:
		return
	#城门是否已破
	gateMgr = warMgr.get_gate_mgr(gateId)
	if not gateMgr or gateMgr.is_broken is True:
		return

	warMgr.join_gate(role, gateMgr)
	
	#回调成功
	role.CallBackFunction(backId, None)
	#显示
	ShowRoleData(role)
	ShowGatePanelData(role)
	
def ChangeGate(role, gateId, backId):
	warMgr = GetWarMgr(role)
	if not warMgr:
		return
	#有城门才可以更换城门
	nowGateId = GetRoleGateID(role)
	if not nowGateId:
		return
	#在同一个城门中不用更换
	if nowGateId == gateId:
		return
	nowgateMgr = warMgr.get_gate_mgr(nowGateId)
	if not nowgateMgr:
		return
	#城门是否已破
	newgateMgr = warMgr.get_gate_mgr(gateId)
	if not newgateMgr:
		return
	if newgateMgr.is_broken is True:
		return
	
	#是否满血
	warRole = GetWarRole(role)
	if warRole.is_full_hp() is False:
		return
	
	#先离开城门
	warMgr.leave_gate(role, nowgateMgr)
	
	#再加入城门
	warMgr.join_gate(role, newgateMgr)
	
	#回调成功
	role.CallBackFunction(backId, None)
	
	#显示
	ShowRoleData(role)
	ShowGatePanelData(role)
	
def ChallengeRole(role, desRoleId):
	if not desRoleId or desRoleId == role.GetRoleID():
		return
	#判断自己CD
	if role.GetCD(EnumCD.UnionKuaFuWarFightCD):
		return
	
	#自己战斗状态
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	desRole = cRoleMgr.FindRoleByRoleID(desRoleId)
	if not desRole:
		#提示
		role.Msg(2, 0, GlobalPrompt.UNION_KUAFU_WAR_LEAVE_PROMPT)
		return
	
	#判断对手CD
	if desRole.GetCD(EnumCD.UnionKuaFuWarFightCD):
		#提示
		role.Msg(2, 0, GlobalPrompt.UNION_KUAFU_WAR_OTHER_CD_PROMPT)
		return
	
	#对手战斗状态
	if not Status.CanInStatus(desRole, EnumInt1.ST_FightStatus):
		return
	
	warMgr = GetWarMgr(role)
	if not warMgr:
		return
	
	gateId = GetRoleGateID(role)
	if not gateId:
		return
	
	gateMgr = warMgr.get_gate_mgr(gateId)
	if not gateMgr:
		return
	
	#城门是否已破
	if gateMgr.is_broken is True:
		return
	
	#是否和对手在同一个门中
	if desRoleId not in gateMgr.gate_roleid_set:
		#提示
		role.Msg(2, 0, GlobalPrompt.UNION_KUAFU_WAR_LEAVE_PROMPT)
		return
	
	warRole = GetWarRole(role)
	desWarRole = GetWarRole(desRole)
	
	#设置战斗CD
	role.SetCD(EnumCD.UnionKuaFuWarFightCD, FIGHT_CD)
	desRole.SetCD(EnumCD.UnionKuaFuWarFightCD, FIGHT_CD)
	
	PVP_UnionKuaFuWar(warRole, desWarRole, warMgr, 168, AfterFightPVP, (warMgr, gateMgr, warRole, desWarRole))
	
def ActivateBuff(role):
	warRole = GetWarRole(role)
	
	activateBuffId = warRole.buff_id + 1
	
	buffZDLConfig = UnionKuaFuWarConfig.UNION_KUAFU_WAR_BUFF_ZDL.get(activateBuffId)
	if not buffZDLConfig:
		return
	
	#判断战斗力
	if warRole.role_zdl < buffZDLConfig.needZDL:
		return
	
	warRole.buff_id = activateBuffId
	
	warUnion = GetRoleWarUnion(role)
	warUnion.activate_buff(buffZDLConfig.buffType, warRole, buffZDLConfig)
	
	
#===============================================================================
# 战斗相关
#===============================================================================
def PVP_UnionKuaFuWar(leftWarRole, rightWarRole, warMgr, fightType, AfterFight, afterFightParam=None, OnLeave=None, AfterPlay=None):
	'''
	公会圣域争霸PVP
	@param leftWarRole:
	@param rightWarRole:
	@param warMgr:
	@param fightType:
	@param AfterFight:
	@param afterFightParam:
	@param OnLeave:
	@param AfterPlay:
	'''
	# 1创建一场战斗(必须传入战斗类型，不同的战斗不要让策划复用战斗类型)
	fight = Fight.Fight(fightType)
	# 可以手动设置是否为pvp战斗，否则将是战斗配子表中战斗类型对应的pvp战斗取值
	fight.pvp = True
	# 可收到设置客户端断线重连是否还原战斗,默认不还原
	fight.restore = True
	# 2创建两个阵营
	left_camp, right_camp = fight.create_camp()
	
	# 3在阵营中创建战斗单位
	left_camp.bind_hp(leftWarRole.bind_hp)
	left_camp.create_online_role_unit(leftWarRole.role, fightData = leftWarRole.fight_data, use_px = True)
	leftWarRole.create_buff(left_camp)
	
	right_camp.bind_hp(rightWarRole.bind_hp)
	right_camp.create_online_role_unit(rightWarRole.role, fightData = rightWarRole.fight_data, use_px = True)
	rightWarRole.create_buff(right_camp)
	
	# 4设置回调函数（不是一定需要设置回调函数，按需来）
	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	# 如果需要带参数，则直接绑定在fight对象上
	fight.after_fight_param = afterFightParam
	# 5开启战斗（之后就不能再对战斗做任何设置了）
	fight.start()
	
def PVE_UnionKuaFuWar(warRole, fightType, mcid, AfterFight, regParam = None, OnLeave = None, AfterPlay = None):
	'''
	公会圣域争霸PVE
	@param warRole:
	@param fightType:
	@param mcid:
	@param AfterFight:
	@param regParam:
	@param OnLeave:
	@param AfterPlay:
	'''
	fight = Fight.Fight(fightType)
	fight.restore = True
	left_camp, right_camp = fight.create_camp()
	
	#保存血量
	left_camp.bind_hp(warRole.bind_hp)
	left_camp.create_online_role_unit(warRole.role, fightData = warRole.fight_data, use_px = True)
	right_camp.create_monster_camp_unit(mcid)

	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	fight.after_fight_param = regParam

	fight.start()
	
def AfterFightPVP(fight):
	warMgr, gateMgr, warRole, desWarRole = fight.after_fight_param
	
	#城门扣血
	gateMgr.dec_hp()
	
	#获取战斗玩家
	role = None
	desRole = None
	winRole = None
	lostRole = None
	winWarRole = None
	lostWarRole = None
	
	
	if fight.left_camp.roles:
		left_camp_roles_list = list(fight.left_camp.roles)
		role = left_camp_roles_list[0]
	if fight.right_camp.roles:
		right_camp_roles_list = list(fight.right_camp.roles)
		desRole = right_camp_roles_list[0]
	
	# fight.round当前战斗回合
	#print "fight round", fight.round
	# fight.result如果没“bug”的话将会取值1左阵营胜利；0平局；-1右阵营胜利
	# 故判断胜利请按照下面这种写法明确判定
	if fight.result == 1:
		#print "left win"
		winRole, lostRole, winWarRole, lostWarRole = role, desRole, warRole, desWarRole
	elif fight.result == -1:
		#print "right win"
		winRole, lostRole, winWarRole, lostWarRole = desRole, role, desWarRole, warRole
	else:
		#print "all lost"
		pass
	
	WinFight(warMgr, gateMgr, winWarRole, lostWarRole)
	LostFight(warMgr, gateMgr, winWarRole, lostWarRole)
	
	if lostRole:
		#战斗失败者再增加5秒战斗CD
		cd = lostRole.GetCD(EnumCD.UnionKuaFuWarFightCD) + 5
		lostRole.SetCD(EnumCD.UnionKuaFuWarFightCD, cd)
		#显示城门数据
		ShowRoleData(lostRole)
		ShowGateData(lostRole)
		ShowGatePanelData(lostRole)
		#显示排行榜
		ShowRank(lostRole)
		#显示记录
		ShowRecord(lostRole)
		#显示buff
		ShowBuff(lostRole)
	if winRole:
		#显示城门数据
		ShowRoleData(winRole)
		ShowGateData(winRole)
		ShowGatePanelData(winRole)
		#显示排行榜
		ShowRank(winRole)
		#显示记录
		ShowRecord(winRole)
		#显示buff
		ShowBuff(winRole)
	
def WinFight(warMgr, gateMgr, winWarRole, lostWarRole = None, isPve = False):
	winWarRole.win()
	
	#加分
	addScore = winWarRole.win_streak * gateMgr.gate_config.winStreakFactor + gateMgr.gate_config.winScore
	warMgr.inc_role_score(winWarRole, addScore)
	
	#更新连杀列表数据
	gateMgr.in_or_out_win_streak(winWarRole)
	
	#记录
	record = ""
	if isPve is False:
		#PVP
		record = GlobalPrompt.UNION_KUAFU_WAR_WIN_PVP_RECORD % (lostWarRole.role_name, addScore)
		winWarRole.add_record(record)
	else:
		#PVE
		record = GlobalPrompt.UNION_KUAFU_WAR_WIN_GUARD_RECORD % addScore
		winWarRole.add_record(record)
	#提示
	if winWarRole.role and (not winWarRole.role.IsKick()):
		winWarRole.role.Msg(2, 0, record)
	
	#传闻
	hearsay = GetWinStreakToHearsay(winWarRole.win_streak)
	if hearsay:
		warMgr.scene.Msg(1, 0, hearsay % (winWarRole.win_streak, winWarRole.role_name))
	elif winWarRole.win_streak > 30:
		#连杀超过30,每5连杀公告一次
		if winWarRole.win_streak % 5 == 0:
			warMgr.scene.Msg(1, 0, GlobalPrompt.UNION_KUAFU_WAR_WIN_STREAK_HEARSAY5 % (winWarRole.win_streak, winWarRole.role_name)) 
	
	if lostWarRole:
		#终结连杀
		if lostWarRole.win_streak >= 10:
			warMgr.scene.Msg(1, 0, GlobalPrompt.UNION_KUAFU_WAR_BREAK_WIN_STREAK % (winWarRole.role_name, lostWarRole.role_name, lostWarRole.win_streak))
	
def LostFight(warMgr, gateMgr, winWarRole, lostWarRole, isPve = False):
	lostWarRole.lost()
	
	#扣分
	warMgr.dec_role_score(lostWarRole, gateMgr.gate_config.lostScore)
	
	#更新连杀列表数据
	gateMgr.in_or_out_win_streak(lostWarRole)
	
	#记录
	record = ""
	if isPve is False:
		#PVP
		record = GlobalPrompt.UNION_KUAFU_WAR_LOST_PVP_RECORD % (winWarRole.role_name, gateMgr.gate_config.lostScore)
		lostWarRole.add_record(record)
	else:
		#PVE
		record = GlobalPrompt.UNION_KUAFU_WAR_LOST_GUARD_RECORD % gateMgr.gate_config.lostScore
		lostWarRole.add_record(record)
	#提示
	if lostWarRole.role and (not lostWarRole.role.IsKick()):
		lostWarRole.role.Msg(2, 0, record)
	
def AllRoleGoBackToLogicServer():
	#把玩家T出跨服场景
	for warMgr in WAR_MGR_DICT.itervalues():
		for role in warMgr.scene.GetAllRole():
			role.GotoLocalServer(None, None)
	
def WarClear():
	global WAR_TICK_ID
	WAR_TICK_ID = 0
	global WAR_MGR_DICT
	WAR_MGR_DICT = {}
	global ROLE_ZONEID_DICT
	ROLE_ZONEID_DICT = {}
	
#===============================================================================
# 显示
#===============================================================================
def ShowRoleData(role):
	warMgr = GetWarMgr(role)
	if not warMgr:
		return
	
	warRole = GetWarRole(role)
	warUnion = GetRoleWarUnion(role)
	if not warRole or not warUnion:
		return
	
	#血量百分比，连胜次数，公会积分，个人积分，当前在哪个城门
	maxHp, hp = warRole.hp
	hpPercentage = int((hp / float(maxHp)) * 100)
	role.SendObj(Union_KuaFu_War_Cross_Show_Role_Data, (hpPercentage, warRole.win_streak, warUnion.score, warRole.score, GetRoleGateID(role)))
	
def ShowGateData(role):
	warMgr = GetWarMgr(role)
	if not warMgr:
		return
	
	gateHpDict = {}
	for gateId, gateMgr in warMgr.gate_mgr_dict.iteritems():
		gateHpDict[gateId] = gateMgr.gate_hp
		
	role.SendObj(Union_KuaFu_War_Cross_Show_Gate_Data, gateHpDict)
	
def ShowGatePanelData(role):
	if IS_START is False:
		role.SendObj(Union_KuaFu_War_Cross_Show_Gate_Panel, ())
		return
	
	warMgr = GetWarMgr(role)
	if not warMgr:
		role.SendObj(Union_KuaFu_War_Cross_Show_Gate_Panel, ())
		return
	
	gateId = GetRoleGateID(role)
	if not gateId:
		role.SendObj(Union_KuaFu_War_Cross_Show_Gate_Panel, ())
		return
	
	gateMgr = warMgr.get_gate_mgr(gateId)
	showData = gateMgr.get_gate_show_data(role)
	
	role.SendObj(Union_KuaFu_War_Cross_Show_Gate_Panel, showData)

def ShowRank(role):
	warMgr = GetWarMgr(role)
	if not warMgr:
		return
	
	warUnion = GetRoleWarUnion(role)
	if not warUnion:
		return

	#公会排行，公会个人排行，个人排行总榜
	role.SendObj(Union_KuaFu_War_Cross_Show_Rank, (warMgr.total_union_little_rank.data, warUnion.role_little_rank.data, warMgr.total_role_little_rank.data))

def ShowRecord(role):
	warMgr = GetWarMgr(role)
	if not warMgr:
		return
	
	warRole = GetWarRole(role)
	
	role.SendObj(Union_KuaFu_War_Cross_Show_Record, warRole.circular_record.to_list())
	
def ShowBuff(role):
	warRole = GetWarRole(role)
	warUnion = GetRoleWarUnion(role)
	#当前开启到的buff，女神庇护buff等级，公会buff字典
	role.SendObj(Union_KuaFu_War_Cross_Show_Buff, (warRole.buff_id, warRole.goddess_buff_level, warUnion.buff_dict))

def SyncGatePanelDataCircular(role, callargv, regparam):
	#循环更新面板
	role.RegTick(GATE_PANEL_DATA_TICK_SEC, SyncGatePanelDataCircular)
	
	ShowGatePanelData(role)
	
	
#===============================================================================
# 进入跨服场景后调用
#===============================================================================
def AfterJoinReadyScene(role, param):
	#5s后传送到正式场景
	role.RegTick(5, AfterJoinCrossScene, param)

def AfterJoinCrossScene(role, argv, param):
	global ROLE_ZONEID_DICT
	zoneName, zoneId, processId, unionName, score = param
	if (IS_READY is False) and (IS_START is False):
		#活动已经结束了,或者没开启
		role.GotoLocalServer(None, None)
		return
	
	unionId = role.GetUnionID()
	if not unionId:
		#没有公会
		role.GotoLocalServer(None, None)
		return
	
	#创建争霸管理对象
	warMgr = WAR_MGR_DICT.get(zoneId)
	if not warMgr:
		#区域配置
		zoneConfig = UnionKuaFuWarConfig.UNION_KUAFU_WAR_ZONE.get(zoneId)
		if not zoneConfig:
			print "GE_EXC AfterJoinCrossScene error not zone cfg (%s), (%s)" % (zoneId, processId)
			role.GotoLocalServer(None, None)
			return
		#是否有这个场景
		scene = cSceneMgr.SearchPublicScene(zoneConfig.sceneId)
		if not scene:
			print "GE_EXC AfterJoinCrossScene error not scene cfg (%s), (%s)" % (zoneId, zoneConfig.sceneId)
			role.GotoLocalServer(None, None)
			return
		WAR_MGR_DICT[zoneId] = warMgr = WarMgr(zoneId, scene, zoneConfig)
	
	#跳转到圣域争霸
	role.Revive(warMgr.scene.GetSceneID(), 958, 579)
	
	#保存角色区域ID
	roleId = role.GetRoleID()
	ROLE_ZONEID_DICT[roleId] = zoneId
	
	#保存进程ID
	warMgr.processid_set.add(processId)
	warMgr.join_role(role, zoneName, unionName)
	
	#是否第一次进圣域争霸
	IsFirstJoinWar(warMgr, role, unionId, score)
	
	#循环同步城门面板数据
	SyncGatePanelDataCircular(role, None, None)
	
	#显示
	ShowRoleData(role)
	ShowGateData(role)
	ShowRank(role)
	ShowRecord(role)
	ShowBuff(role)

def IsFirstJoinWar(warMgr, role, unionId, score):
	roleId = role.GetRoleID()
	#是否第一次进入,奖励积分
	if roleId in warMgr.join_roleid_set:
		return
	
	warRole = GetWarRole(role)
	warMgr.join_roleid_set.add(roleId)
	warMgr.inc_role_score(warRole, score)
	#公会频道
	warUnion = GetRoleWarUnion(role)
	warUnion.msg(GlobalPrompt.UNION_KUAFU_WAR_NEW_JOIN_PROMPT % (role.GetRoleName(), score))

#===============================================================================
# 事件
#===============================================================================
def OnRoleExit(role, param):
	if not Environment.IsCross:
		return
	warMgr = GetWarMgr(role)
	if warMgr:
		warMgr.exit_scene(role)
	
#===============================================================================
# 时间
#===============================================================================
def WarReady():
	if UnionKuaFuWarConfig.IsTodayHasWar() is False:
		return
	
	global IS_READY
	IS_READY = True
	
	WarClear()
	
	#9分钟tick，9点10分触发
	cComplexServer.RegTick(9 * 60, WarStart)

def WarStart(callArgv, regparam):
	if UnionKuaFuWarConfig.IsTodayHasWar() is False:
		return
	
	global IS_READY
	IS_READY = False
	
	global IS_START
	IS_START = True
	
	#35分钟tick，9点45分触发
	global WAR_TICK_ID
	WAR_TICK_ID = cComplexServer.RegTick(35 * 60, WarEnd)

def WarEnd(callArgv, regparam):
	global IS_START
	if IS_START is False:
		return
	IS_START = False
	
	#排行榜奖励
	RankReward()
	
	#注册tick，把玩家踢出跨服
	cComplexServer.RegTick(END_KICK_ROLE_TICK_SEC, KickAllRole)
	
def KickAllRole(callArgv, regparam):
	#把玩家T出跨服场景
	AllRoleGoBackToLogicServer()
	WarClear()
	
def RankReward():
	for warMgr in WAR_MGR_DICT.itervalues():
		#发奖
		warMgr.rank_reward()
		
def TotalRoleRankReward(warMgr):
	#个人总榜
	roleSortList = warMgr.total_role_little_rank.data.items()
	#先个人总积分排名，再按roleId排名（roleId越小排名越前）
	roleSortList.sort(key=lambda x:(x[1][2], -x[0]), reverse=True)
	
	UUG = UnionKuaFuWarConfig.UNION_KUAFU_WAR_TOTAL_ROLE_RANK.get
	W_ZONEID = warMgr.zone_id
	WGR = warMgr.get_war_role_by_roleid
	AMSA = AwardMgr.SetAward
	EUA = EnumAward.UnionKuaFuWarRoleRankAward
	for idx, data in enumerate(roleSortList):
		rank = idx + 1
		rewardConfigDict = UUG((W_ZONEID, rank))
		if not rewardConfigDict:
			print "GE_EXC can't find rewardConfigDict in TotalRoleRankReward(%s, %s)" % (warMgr.zone_id, rank)
			continue
		
		roleId = data[0]
		warRole = WGR(roleId)
		if not warRole:
			continue
		
		rewardConfig = rewardConfigDict.get(warRole.role_level)
		if not rewardConfig:
			continue
		
		#分数是否满足条件
		if warRole.score < rewardConfig.needScore:
			continue
		
		AMSA(data[0], EUA, money = rewardConfig.rewardMoney, reputation = rewardConfig.rewardReputation, itemList = rewardConfig.rewardItem, clientDescParam = (rank,))
	
	#日志
	with TraUnionKuaFuTotalRoleRank:
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveUnionKuaFuWarTotalRoleRank, (warMgr.zone_id, roleSortList))
		
def UnionRankReward(warMgr):
	#公会总榜
	unionRankList = warMgr.total_union_little_rank.data.items()
	#先公会总积分排名，再按unionId排名（unionId越小排名越前）
	unionRankList.sort(key=lambda x:(x[1][2], -x[0]), reverse=True)
	
	#日志
	with TraUnionKuaFuTotalUnionRank:
		logUnionRankList = [l[0] for l in unionRankList]
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveUnionKuaFuWarTotalUnionRank, (warMgr.zone_id, logUnionRankList))
	
	#发放公会总榜奖励
	SendUnionRankReward(warMgr, unionRankList)
	
	#公会内个人榜
	unionRoleRankDict = {}
	for warUnion in warMgr.war_union_dict.itervalues():
		unionRoleSortList = warUnion.role_little_rank.data.items()
		#先个人总积分排名，再按roleId排名（roleId越小排名越前）
		unionRoleSortList.sort(key=lambda x:(x[1][2], -x[0]), reverse=True)
		unionRoleRankDict[warUnion.union_id] = unionRoleSortList
	
	#日志
	with TraUnionKuaFuUnionRoleRank:
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveUnionKuaFuWarUnionRoleRank, (warMgr.zone_id, unionRoleRankDict))
	
	#发放公会个人榜奖励
	SendUnionRoleRankReward(warMgr, unionRoleRankDict)
	
	#冠军公会奖励
	ChampionUnionTitleReward(warMgr, unionRankList, unionRoleRankDict)
	
	
def SendUnionRankReward(warMgr, unionRankList):
	#公会总榜奖励
	UUG = UnionKuaFuWarConfig.UNION_KUAFU_WAR_UNION_RANK.get
	W_ZONEID = warMgr.zone_id
	WGU =  warMgr.get_war_union
	WGR = warMgr.get_war_role_by_roleid
	AMSA = AwardMgr.SetAward
	EURA = EnumAward.UnionKuaFuWarUnionRankAward
	for idx, data in enumerate(unionRankList):
		rank = idx + 1
		unionId = data[0]
		
		rewardConfigDict = UUG((W_ZONEID, rank))
		if not rewardConfigDict:
			continue
		
		warUnion = WGU(unionId)
		if not warUnion:
			continue
		
		for roleId in warUnion.member_roleid_set:
			warRole = WGR(roleId)
			if not warRole:
				continue
			rewardConfig = rewardConfigDict.get(warRole.role_level)
			if not rewardConfig:
				continue
			
			AMSA(roleId, EURA, itemList = rewardConfig.rewardItem, clientDescParam = (rank, ))
	
	#其余没有上榜的玩家发放参与奖励
	joinRewardConfigDict = UnionKuaFuWarConfig.UNION_KUAFU_WAR_UNION_RANK.get((warMgr.zone_id, UnionKuaFuWarConfig.TOTAL_UNION_RANK_CNT + 1))
	if not joinRewardConfigDict:
		return
	UTD = warMgr.total_union_little_rank.data
	JG = joinRewardConfigDict.get
	CP = UnionKuaFuWarConfig.TOTAL_UNION_RANK_CNT + 1
	for unionId, warUnion in warMgr.war_union_dict.iteritems():
		#有排名的忽略
		if unionId in UTD:
			continue
		for roleId in warUnion.member_roleid_set:
			warRole = WGR(roleId)
			if not warRole:
				continue
			rewardConfig = JG(warRole.role_level)
			if not rewardConfig:
				continue
			
			AMSA(roleId, EURA, itemList = rewardConfig.rewardItem, clientDescParam = (CP, ))
	
def SendUnionRoleRankReward(warMgr, unionRoleRankDict):
	#公会个人榜奖励
	WGU = warMgr.get_war_union
	WGR = warMgr.get_war_role_by_roleid
	UUG = UnionKuaFuWarConfig.UNION_KUAFU_WAR_UNION_ROLE_RANK.get
	AMSA = AwardMgr.SetAward
	EURA = EnumAward.UnionKuaFuWarUnionRoleRankAward
	for unionId, sortList in unionRoleRankDict.iteritems():
		warUnion = WGU(unionId)
		if not warUnion:
			continue
		
		UMS = warUnion.member_roleid_set
		for idx, data in enumerate(sortList):
			rank = idx + 1
			roleId = data[0]
			score = data[1][2]
		
			warRole = WGR(roleId)
			if not warRole:
				continue
		
			#是否本公会成员
			if roleId not in UMS:
				continue
			
			rewardConfigDict = UUG((warMgr.zone_id, rank))
			if not rewardConfigDict:
				continue
			
			rewardConfig = rewardConfigDict.get(warRole.role_level)
			if not rewardConfig:
				continue
			
			if score < rewardConfig.needScore:
				#排名靠前的分数不满足条件，排名靠后的肯定不满足条件
				break
		
			AMSA(roleId, EURA, money = rewardConfig.rewardMoney, itemList = rewardConfig.rewardItem, clientDescParam = (rank, ))
	
def ChampionUnionTitleReward(warMgr, unionRankList, unionRoleRankDict):
	#提取冠军公会数据
	if len(unionRankList) == 0:
		#这个区域没有公会参与
		return
	
	championUnionId, data = unionRankList[0]
	championUnionName = data[1]
	
	#保存冠军公会名
	warMgr.champion_union_name = championUnionName
	
	#是否有冠军公会个人排行榜数据
	if championUnionId not in unionRoleRankDict:
		return
	
	#冠军公会前五名角色数据
	championRoleId = 0
	championRoleDataList = []
	topFiveList = unionRoleRankDict[championUnionId][:5]
	for idx, data in enumerate(topFiveList):
		rank = idx + 1
		roleId = data[0]
		warRole = warMgr.get_war_role_by_roleid(roleId)
		if not warRole:
			continue
		
		championRoleDataList.append(warRole.get_show_data())
		
		if rank == 1:
			#冠军公会第一名发称号
			championRoleId = roleId
			#保存圣域独裁者名字和服务器名
			warMgr.champion_role_name = warRole.role_name
			warMgr.champion_zone_name = warRole.role_zone_name
			
	#发放称号
	warUnion = warMgr.get_war_union(championUnionId)
	for memberId in warUnion.member_roleid_set:
		if memberId == championRoleId:
			#圣域独裁者
			Title.AddTitle(memberId, 42)
			continue
		#圣域勇士
		Title.AddTitle(memberId, 43)
	CS = Call.ServerCall
	for processId in warMgr.processid_set:
		#公会总排行，冠军公会前五名角色数据
		CS(processId, "Game.UnionKuaFuWar.UnionKuaFuWarMgr", "CrossCallWarEndRankReward", (unionRankList, championRoleDataList))
	
	#传闻
	warMgr.scene.Msg(1, 0, GlobalPrompt.UNION_KUAFU_WAR_END_HEARSAY % championUnionName) 
	
#===============================================================================
# 逻辑进程
#===============================================================================
def LogicCallServerData(param):
	zoneId, processId = param
	warMgr = WAR_MGR_DICT.get(zoneId)
	if not warMgr:
		#区域配置
		zoneConfig = UnionKuaFuWarConfig.UNION_KUAFU_WAR_ZONE.get(zoneId)
		if not zoneConfig:
			print "GE_EXC LogicCallServerData error not zone cfg (%s), (%s)" % (zoneId, processId)
			return
		
		#是否有这个场景
		scene = cSceneMgr.SearchPublicScene(zoneConfig.sceneId)
		if not scene:
			print "GE_EXC LogicCallServerData error not scene cfg (%s), (%s)" % (zoneId, zoneConfig.sceneId)
			return
		#创建争霸管理对象
		WAR_MGR_DICT[zoneId] = warMgr = WarMgr(zoneId, scene, zoneConfig)
	
	#保存进程ID
	warMgr.processid_set.add(processId)
	
	
#===============================================================================
# 客户端请求
#===============================================================================
def RequestUnionKuaFuWarCrossChooseGate(role, msg):
	'''
	客户端请求公会圣域争霸选择城门
	@param role:
	@param msg:
	'''
	if IS_START is False:
		return
	
	backId, gateId = msg
	
	ChooseGate(role, gateId, backId)
	
def RequestUnionKuaFuWarCrossChangeGate(role, msg):
	'''
	客户端请求公会圣域争霸更换城门
	@param role:
	@param msg:
	'''
	if IS_START is False:
		return
	
	backId, gateId = msg
	
	ChangeGate(role, gateId, backId)
	
def RequstUnionKuaFuWarCrossChallenge(role, msg):
	'''
	客户端请求公会圣域争霸挑战
	@param role:
	@param msg:
	'''
	if IS_START is False:
		return
	
	desRoleId = msg
	
	ChallengeRole(role, desRoleId)
	
def RequstUnionKuaFuWarCrossLeaveScene(role, msg):
	'''
	客户端请求离开跨公会圣域争霸场景
	@param role:
	@param msg:
	'''
	warMgr = GetWarMgr(role)
	if warMgr:
		warMgr.exit_scene(role)
	
	role.GotoLocalServer(None, None)
	
def RequstUnionKuaFuWarCrossActivateBuff(role, msg):
	'''
	客户端请求跨服公会圣域争霸激活buff
	@param role:
	@param msg:
	'''
	ActivateBuff(role)
	
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and Environment.IsCross:
		if cProcess.ProcessID == Define.GetDefaultCrossID():
			#事件
			#角色初始化
			Event.RegEvent(Event.Eve_BeforeExit, OnRoleExit)
			
			#时间
			Cron.CronDriveByMinute((2038, 1, 1), WarReady, H = "H == 21", M = "M == 1")
			
			#日志
			TraUnionKuaFuTotalRoleRank = AutoLog.AutoTransaction("TraUnionKuaFuTotalRoleRank", "公会圣域争霸个人总榜")
			TraUnionKuaFuTotalUnionRank = AutoLog.AutoTransaction("TraUnionKuaFuTotalUnionRank", "公会圣域争霸公会总榜")
			TraUnionKuaFuUnionRoleRank = AutoLog.AutoTransaction("TraUnionKuaFuUnionRoleRank", "公会圣域争霸公会内个人榜")
			
			#客户端请求消息
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_KuaFu_War_Cross_Choose_Gate", "客户端请求公会圣域争霸选择城门"), RequestUnionKuaFuWarCrossChooseGate)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_KuaFu_War_Cross_Change_Gate", "客户端请求公会圣域争霸更换城门"), RequestUnionKuaFuWarCrossChangeGate)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_KuaFu_War_Cross_Challenge", "客户端请求公会圣域争霸挑战"), RequstUnionKuaFuWarCrossChallenge)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_KuaFu_War_Cross_Activate_Buff", "客户端请求跨服公会圣域争霸激活Buff"), RequstUnionKuaFuWarCrossActivateBuff)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_KuaFu_War_Cross_Leave_Scene", "客户端请求离开跨公会圣域争霸场景"), RequstUnionKuaFuWarCrossLeaveScene)
			
			
