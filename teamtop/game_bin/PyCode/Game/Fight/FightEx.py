#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.FightEx")
#===============================================================================
# 战斗
#===============================================================================
from Game.Fight import Fight, Middle
from Game.Property import PropertyEnum
from Game.Role.Data import EnumTempObj

def PVE(role, fightType, mcid, AfterFight, regParam = None, OnLeave = None, AfterPlay = None):
	'''
	普通PVE
	@param role:
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
	
	left_camp.create_online_role_unit(role, role.GetRoleID())
	right_camp.create_monster_camp_unit(mcid)

	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	fight.after_fight_param = regParam

	fight.start()
	
def PVE_Wheel(role, fightType, mcidList, AfterFight, regParam = None, OnLeave = None, AfterPlay = None):
	'''
	普通PVE车轮战
	@param role:
	@param fightType:
	@param mcidList:
	@param AfterFight:
	@param regParam:
	@param OnLeave:
	@param AfterPlay:
	'''
	fight = Fight.Fight(fightType)
	fight.restore = True
	left_camp, right_camp = fight.create_camp()
	
	left_camp.create_online_role_unit(role, role.GetRoleID())
	
	for mcid in mcidList:
		right_camp.create_monster_camp_unit(mcid)

	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	fight.after_fight_param = regParam

	fight.start()



def PVE_Task(role, fightId, fightType, AfterFight, regParam = None, anger = 0, OnLeave = None, AfterPlay = None):
	'''
	主线任务战斗
	@param role:
	@param fightId:
	@param fightType:
	@param AfterFight:
	@param regParam:
	@param OnLeave:
	@param AfterPlay:
	'''
	fight = Fight.Fight(fightType)
	fight.restore = True
	left_camp, right_camp = fight.create_camp()
	
	left_camp.bind_moral(role.GetTempObj(EnumTempObj.MainTask_Moral))
	if anger:
		datas = Middle.GetRoleData(role)
		datas[0][Middle.Morale] = anger
		left_camp.create_online_role_unit(role, role.GetRoleID(), datas)
	else:
		left_camp.create_online_role_unit(role, role.GetRoleID())
	right_camp.create_monster_camp_unit(fightId)

	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	fight.after_fight_param = regParam

	fight.start()

def PVE_DayTask(role, fightId, fightType, AfterFight, regParam = None, OnLeave = None, AfterPlay = None):
	'''
	日常任务战斗
	@param role:
	@param fightId:
	@param fightType:
	@param AfterFight:
	@param regParam:
	@param OnLeave:
	@param AfterPlay:
	'''
	fight = Fight.Fight(fightType)
	fight.restore = True
	left_camp, right_camp = fight.create_camp()
	
	left_camp.create_online_role_unit(role, role.GetRoleID())
	right_camp.create_monster_camp_unit(fightId)

	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	fight.after_fight_param = regParam

	fight.start()


def PVE_Purgatory(role, fightType, mcidList, AfterFight, BuyLife, purgatoryId):
	'''
	心魔炼狱战斗
	@param role:
	@param fightType:
	@param mcidList:
	@param AfterFight:
	@param regParam:
	@param OnLeave:
	@param AfterPlay:
	'''
	fight = Fight.Fight(fightType)
	fight.restore = True
	fight.only_win_save_moral = False
	left_camp, right_camp = fight.create_camp()
	left_camp.bind_moral({})
	
	left_camp.create_online_role_unit(role, role.GetRoleID())
	for mcid in mcidList:
		right_camp.create_monster_camp_unit(mcid)
	
	fight.after_fight_fun = AfterFight
	fight.after_fight_param = purgatoryId
	fight.buy_life_fun = BuyLife
	fight.buy_role = role
	
	fight.start()


def PVE_EvilHole(role, fightIds, fightType, AfterFight, regParam = None, OnLeave = None, AfterPlay = None):
	'''
	恶魔深渊战斗
	@param role:
	@param fightId:
	@param fightType:
	@param AfterFight:
	@param regParam:
	@param OnLeave:
	@param AfterPlay:
	'''
	fight = Fight.Fight(fightType)
	fight.restore = True
	left_camp, right_camp = fight.create_camp()
	
	left_camp.create_online_role_unit(role, role.GetRoleID())
	for fightId in fightIds:
		right_camp.create_monster_camp_unit(fightId)

	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	fight.after_fight_param = regParam

	fight.start()

def PVE_FB(role, fightId, fightType, AfterFight, regParam = None, OnLeave = None, AfterPlay = None):
	'''
	副本战斗
	@param role:
	@param fightId:
	@param fightType:
	@param AfterFight:
	@param regParam:
	@param OnLeave:
	@param AfterPlay:
	'''
	fight = Fight.Fight(fightType)
	fight.restore = True
	left_camp, right_camp = fight.create_camp()
	
	left_camp.bind_moral(role.GetTempObj(EnumTempObj.FB_Moral))
	
	left_camp.create_online_role_unit(role, role.GetRoleID())
	right_camp.create_monster_camp_unit(fightId)

	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	fight.after_fight_param = regParam

	fight.start()
	
def PVE_UnionRobTreasure(role, mcid, fightType, AfterFight, regParam = None, OnLeave = None, AfterPlay = None):
	'''
	公会夺宝PVE
	@param role:
	@param mcid:
	@param fightType:
	@param AfterFight:
	@param regParam:
	@param OnLeave:
	@param AfterPlay:
	'''
	fight = Fight.Fight(fightType)
	fight.restore = True
	left_camp, right_camp = fight.create_camp()
	
	left_camp.create_online_role_unit(role, role.GetRoleID())
	right_camp.create_monster_camp_unit(mcid)

	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	fight.after_fight_param = regParam

	fight.start()

def PVE_HeroCall(role, fightType, mcid, AfterFight, param):
	'''
	英雄祭坛战斗
	@param role:
	@param fightType:
	@param mcidList:
	@param AfterFight:
	@param regParam:
	@param OnLeave:
	@param AfterPlay:
	'''
	fight = Fight.Fight(fightType)
	fight.restore = True
	left_camp, right_camp = fight.create_camp()
	
	left_camp.create_online_role_unit(role, role.GetRoleID())
	right_camp.create_monster_camp_unit(mcid)
	
	fight.after_fight_fun = AfterFight
	fight.after_fight_param = param
	fight.buy_role = role
	
	fight.start()
	
def PVE_UnionFB(leaderRole, fightRoleList, fightType, mcidList, AfterFight, regParam = None, OnLeave = None, AfterPlay = None):
	'''
	公会副本PVE
	@param leaderRole:
	@param fightRoleList:
	@param fightType:
	@param mcidList:
	@param AfterFight:
	@param regParam:
	@param OnLeave:
	@param AfterPlay:
	'''
	fight = Fight.Fight(fightType)
	fight.restore = True
	left_camp, right_camp = fight.create_camp()
	
	for fightRole in fightRoleList:
		left_camp.create_online_role_unit(fightRole, leaderRole.GetRoleID())
	
	for mcid in mcidList:
		right_camp.create_monster_camp_unit(mcid)

	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	fight.after_fight_param = regParam

	fight.start()
	
def PVE_UnionFB_Subsitute(leaderRole, roleFightDataList, fightType, mcidList, AfterFight, regParam = None, OnLeave = None, AfterPlay = None):
	'''
	公会副本替身PVE
	@param leaderRole:
	@param roleFightDataList:
	@param fightType:
	@param mcidList:
	@param AfterFight:
	@param regParam:
	@param OnLeave:
	@param AfterPlay:
	'''
	fight = Fight.Fight(fightType)
	fight.restore = True
	left_camp, right_camp = fight.create_camp()
	
	leaderRoleId = leaderRole.GetRoleID()
	for roleId, roleFightData in roleFightDataList:
		if roleId == leaderRoleId:
			left_camp.create_online_role_unit(leaderRole, leaderRoleId)
		else:
			left_camp.create_outline_role_unit(roleFightData, leaderRole.GetRoleID())
	
	for mcid in mcidList:
		right_camp.create_monster_camp_unit(mcid)

	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	fight.after_fight_param = regParam

	fight.start()
	
def PVE_HT(role, fightType, mcid, AfterFight, param):
	'''
	英灵神殿pve
	@param role:
	@param fightType:
	@param mcid:
	@param AfterFight:
	@param param:
	'''
	fight = Fight.Fight(fightType)
	fight.restore = True
	left_camp, right_camp = fight.create_camp()
	left_camp.create_online_role_unit(role, role.GetRoleID())
	right_camp.create_monster_camp_unit(mcid)
	
	fight.after_fight_fun = AfterFight
	fight.after_fight_param = param
	
	fight.start()
	
def PVE_HS(role, fightType, mcid, AfterFight, param):
	'''
	英雄圣殿pve
	@param role:
	@param fightType:
	@param mcid:
	@param AfterFight:
	@param param:
	'''
	fight = Fight.Fight(fightType)
	fight.restore = True
	left_camp, right_camp = fight.create_camp()
	left_camp.create_online_role_unit(role, role.GetRoleID())
	right_camp.create_monster_camp_unit(mcid)
	
	fight.after_fight_fun = AfterFight
	fight.after_fight_param = param
	
	fight.start()
	
def PVE_AF(role, fightType, mcid, AfterFight, param):
	'''
	魔域星宫pve
	@param role:
	@param fightType:
	@param mcid:
	@param AfterFight:
	@param param:
	'''
	fight = Fight.Fight(fightType)
	fight.restore = True
	left_camp, right_camp = fight.create_camp()
	left_camp.create_online_role_unit(role, role.GetRoleID())
	right_camp.create_monster_camp_unit(mcid)
	fight.after_fight_fun = AfterFight
	fight.after_fight_param = param
	
	fight.start()
	
def PVE_GVEFB(leaderRole, fightRoleList, fightType, mcid, propertyDict, AfterFight, regParam=None, OnLeave=None, AfterPlay=None):
	'''
	GVE副本战斗
	@param leaderRole:
	@param fightRoleList:
	@param fightType:
	@param mcidList:
	@param AfterFight:
	@param regParam:
	@param OnLeave:
	@param AfterPlay:
	'''
	fight = Fight.Fight(fightType)
	fight.restore = True
	left_camp, right_camp = fight.create_camp()
	
	for index, fightRole in enumerate(fightRoleList):
		left_camp.create_online_role_unit(fightRole, fightRole.GetRoleID(), team_pos_index = index + 1)
	
	for u in left_camp.pos_units.itervalues():
		u.max_hp += propertyDict.get(PropertyEnum.maxhp, 0)
		u.hp += propertyDict.get(PropertyEnum.maxhp, 0)
		u.attack_p += propertyDict.get(PropertyEnum.attack_p, 0)
		u.defence_p += propertyDict.get(PropertyEnum.defense_p, 0)
		u.attack_m += propertyDict.get(PropertyEnum.attack_m, 0)
		u.defence_m += propertyDict.get(PropertyEnum.defense_m, 0)
		u.crit += propertyDict.get(PropertyEnum.crit, 0)
		u.crit_press += propertyDict.get(PropertyEnum.critpress, 0)
		u.anti_broken += propertyDict.get(PropertyEnum.antibroken, 0)
		u.not_broken += propertyDict.get(PropertyEnum.notbroken, 0)
		u.parry += propertyDict.get(PropertyEnum.parry, 0)
		u.puncture += propertyDict.get(PropertyEnum.puncture, 0)
		u.damage_upgrade_rate += propertyDict.get(PropertyEnum.damageupgrade, 0)
		u.damage_reduce_rate += propertyDict.get(PropertyEnum.damagereduce, 0)
		u.parry += propertyDict.get(PropertyEnum.parry, 0)

	right_camp.create_monster_camp_unit(mcid)

	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	fight.after_fight_param = regParam

	fight.start()

def PVE_KaifuBossTeam(leaderRole, fightRoleList, fightType, mcidList, AfterFight, regParam=None, OnLeave=None, AfterPlay=None):
	'''
	开服boss组队PVE
	@param leaderRole:
	@param fightRoleList:
	@param fightType:
	@param mcidList:
	@param AfterFight:
	@param regParam:
	@param OnLeave:
	@param AfterPlay:
	'''
	fight = Fight.Fight(fightType)
	fight.restore = True
	left_camp, right_camp = fight.create_camp()
	
	for fightRole in fightRoleList:
		left_camp.create_online_role_unit(fightRole, leaderRole.GetRoleID())
	
	for mcid in mcidList:
		right_camp.create_monster_camp_unit(mcid)

	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	fight.after_fight_param = regParam

	fight.start()

def PVE_KaifuBossSingle(role, fightType, mcidList, AfterFight, regParam=None, OnLeave=None, AfterPlay=None):
	'''
	恶开服boss单挑PVE
	@param role:
	@param fightId:
	@param fightType:
	@param AfterFight:
	@param regParam:
	@param OnLeave:
	@param AfterPlay:
	'''
	fight = Fight.Fight(fightType)
	fight.restore = True
	left_camp, right_camp = fight.create_camp()
	
	left_camp.create_online_role_unit(role, role.GetRoleID())
	for mcid in mcidList:
		right_camp.create_monster_camp_unit(mcid)

	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	fight.after_fight_param = regParam

	fight.start()
	
def PVE_MainTaskSpecial1(role, fightId, fightType, AfterFight, regParam = None, anger = 0, OnLeave = None, AfterPlay = None):
	'''
	特殊主线战斗1
	@param role:
	@param fightId:
	@param fightType:
	@param AfterFight:
	@param regParam:
	@param anger:
	@param OnLeave:
	@param AfterPlay:
	'''
	fight = Fight.Fight(fightType)
	fight.restore = True
	fight.group_need_hero = True
	left_camp, right_camp = fight.create_camp()
	
	#给予主动技能
	datas = Middle.GetRoleData(role, False)
	role_data, _ = datas
	role_data[Middle.GFightPos] = 2
	role_data[Middle.GCareer] = 1
	role_data[Middle.GActiveSkills] = [(2004,1), (2006,1)]
	role_data[Middle.MaxHP] = 5000000
	role_data[Middle.AttackP] = 210000
	role_data[Middle.AttackM] = 210000
	
	left_camp.create_online_role_unit(role, role.GetRoleID(), datas)
	right_camp.create_monster_camp_unit(fightId)

	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	fight.after_fight_param = regParam

	fight.start()
	
def PVE_MainTaskSpecial2(role, fightId, fightType, AfterFight, regParam = None, anger = 0, OnLeave = None, AfterPlay = None):
	'''
	特殊主线战斗2
	@param role:
	@param fightId:
	@param fightType:
	@param AfterFight:
	@param regParam:
	@param anger:
	@param OnLeave:
	@param AfterPlay:
	'''
	fight = Fight.Fight(fightType)
	fight.restore = True
	fight.group_need_hero = True
	left_camp, right_camp = fight.create_camp()
	
	#给予主动技能
	datas = Middle.GetRoleData(role, False)
	role_data, _ = datas
	role_data[Middle.GFightPos] = 2
	role_data[Middle.GCareer] = 1
	role_data[Middle.GActiveSkills] = [(2004,1), (2006,1)]
	role_data[Middle.Morale] = 100	#怒气满
	role_data[Middle.MaxHP] = 5000000
	role_data[Middle.AttackP] = 210000
	role_data[Middle.AttackM] = 210000
	role_data[Middle.GPassiveSkills].append(("NewPlayer1", 0))#被动技能，用于战斗中召唤
	
	left_camp.create_online_role_unit(role, role.GetRoleID(), datas)
	right_camp.create_monster_camp_unit(fightId)

	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	fight.after_fight_param = regParam

	fight.start()


def PVE_MainTaskSpecial_tw1(role, fightId, fightType, AfterFight, regParam=None, anger=0, OnLeave=None, AfterPlay=None):
	'''
	繁体特殊主线战斗1
	@param role:
	@param fightId:
	@param fightType:
	@param AfterFight:
	@param regParam:
	@param anger:
	@param OnLeave:
	@param AfterPlay:
	'''
	fight = Fight.Fight(fightType)
	fight.restore = True
	fight.group_need_hero = True
	left_camp, right_camp = fight.create_camp()
	
	#给予主动技能
	datas = Middle.GetRoleData(role, False)
	role_data, _ = datas
	role_data[Middle.ActiveSkills] = [(3, 1), (5, 1)]
	role_data[Middle.Morale] = 100	#怒气满
	role_data[Middle.MaxHP] = 5000000
	role_data[Middle.AttackP] = 260000
	role_data[Middle.AttackM] = 260000
	
	left_camp.create_online_role_unit(role, role.GetRoleID(), datas)
	right_camp.create_monster_camp_unit(fightId)

	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	fight.after_fight_param = regParam

	fight.start()


def PVE_MainTaskSpecial_tw2(role, fightId, fightType, AfterFight, regParam=None, anger=0, OnLeave=None, AfterPlay=None):
	'''
	繁体特殊主线战斗2
	@param role:
	@param fightId:
	@param fightType:
	@param AfterFight:
	@param regParam:
	@param anger:
	@param OnLeave:
	@param AfterPlay:
	'''
	fight = Fight.Fight(fightType)
	fight.restore = True
	fight.group_need_hero = True
	left_camp, right_camp = fight.create_camp()
	
	#给予主动技能
	datas = Middle.GetRoleData(role, False)
	role_data, _ = datas
	role_data[Middle.MountID] = 6
	role_data[Middle.ActiveSkills] = [(3, 1), (5, 1)]
	role_data[Middle.Morale] = 100	#怒气满
	role_data[Middle.MaxHP] = 5000000
	role_data[Middle.AttackP] = 260000
	role_data[Middle.AttackM] = 260000
	
	left_camp.create_online_role_unit(role, role.GetRoleID(), datas)
	right_camp.create_monster_camp_unit(fightId)

	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	fight.after_fight_param = regParam

	fight.start()
	
	
def GoldMirrorPVE(role, fightType, mcid, AfterFight, regParam):
	'''
	金币副本
	@param role:
	@param fightType:
	@param mcid:
	@param AfterFight:
	@param regParam:
	'''
	fight = Fight.Fight(fightType)
	left_camp, right_camp = fight.create_camp()
	
	left_camp.create_online_role_unit(role, role.GetRoleID())
	right_camp.create_monster_camp_unit(mcid)

	fight.after_fight_fun = AfterFight
	fight.after_fight_param = regParam

	fight.start()



def PVE_TT(leaderRole, fightRoleList, fightType, mcid, AfterFight, regParam=None, OnLeave=None, AfterPlay=None):
	'''
	组队爬塔战斗
	@param leaderRole:
	@param fightRoleList:
	@param fightType:
	@param mcidList:
	@param AfterFight:
	@param regParam:
	@param OnLeave:
	@param AfterPlay:
	'''
	fight = Fight.Fight(fightType)
	fight.restore = True
	left_camp, right_camp = fight.create_camp()
	
	for index, fightRole in enumerate(fightRoleList):
		left_camp.create_online_role_unit(fightRole, fightRole.GetRoleID(), use_px = True, team_pos_index = index + 1)
	
	right_camp.create_monster_camp_unit(mcid)

	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	fight.after_fight_param = regParam

	fight.start()

	
def PVE_CTT(leaderRole, fightRoleList, fightType, mcid, AfterFight, regParam=None, OnLeave=None, AfterPlay=None):
	'''
	虚空幻境战斗
	@param leaderRole:
	@param fightRoleList:
	@param FightDatas:
	@param fightType:
	@param mcid:
	@param AfterFight:
	@param regParam:
	@param OnLeave:
	@param AfterPlay:
	'''
	fight = Fight.Fight(fightType)
	fight.restore = False
	fight.group_need_hero = True
	left_camp, right_camp = fight.create_camp()
	
	for index, fightRole in enumerate(fightRoleList):
		left_camp.create_online_role_unit(fightRole, fightRole.GetRoleID(), use_px = True, role_realfight_pos = index + 1)
	
	right_camp.create_monster_camp_unit(mcid)

	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	fight.after_fight_param = regParam

	fight.start()
	
	

def PVP_JT(leftRoles, rightRoles, fightType, AfterFight, regParam = None, OnLeave = None, AfterPlay = None):
	'''
	组队竞技场战斗
	@param leftRoles:
	@param rightRoles:
	@param fightType:
	@param mcidList:
	@param AfterFight:
	@param regParam:
	@param OnLeave:
	@param AfterPlay:
	'''
	fight = Fight.Fight(fightType)
	fight.restore = False
	fight.group_need_hero = True
	left_camp, right_camp = fight.create_camp()
	
	for index, fightRole in enumerate(leftRoles):
		left_camp.create_online_role_unit(fightRole, fightRole.GetRoleID(), use_px = True, role_realfight_pos = index + 1, use_property_H=True)
		
	for index, fightRole in enumerate(rightRoles):
		right_camp.create_online_role_unit(fightRole, fightRole.GetRoleID(), use_px = True, role_realfight_pos = index + 1, use_property_H=True)

	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	fight.after_fight_param = regParam

	fight.start()

def PVP_JTGroup(leftRoles, rightRoles, fightType, AfterFight, regParam = None, OnLeave = None, AfterPlay = None):
	'''
	跨服争霸小组赛
	@param leftRoles:
	@param rightRoles:
	@param fightType:
	@param mcidList:
	@param AfterFight:
	@param regParam:
	@param OnLeave:
	@param AfterPlay:
	'''
	fight = Fight.Fight(fightType)
	fight.restore = False
	fight.group_need_hero = True
	left_camp, right_camp = fight.create_camp()
	
	for index, fightRole in enumerate(leftRoles):
		left_camp.create_online_role_unit(fightRole, fightRole.GetRoleID(), use_px = True, role_realfight_pos = index + 1, use_property_H=True)
		
	for index, fightRole in enumerate(rightRoles):
		right_camp.create_online_role_unit(fightRole, fightRole.GetRoleID(), use_px = True, role_realfight_pos = index + 1, use_property_H=True)

	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	fight.after_fight_param = regParam

	fight.start()
	
	return fight

def PVP_JTFinal(leftRoles, rightRoles, fightType, AfterFight, regParam = None, OnLeave = None, AfterPlay = None):
	'''
	跨服争霸总决赛
	@param leftRoles:
	@param rightRoles:
	@param fightType:
	@param mcidList:
	@param AfterFight:
	@param regParam:
	@param OnLeave:
	@param AfterPlay:
	'''
	fight = Fight.Fight(fightType)
	fight.restore = False
	fight.group_need_hero = True
	left_camp, right_camp = fight.create_camp()
	
	for index, fightRole in enumerate(leftRoles):
		left_camp.create_online_role_unit(fightRole, fightRole.GetRoleID(), use_px = True, role_realfight_pos = index + 1, use_property_H=True)
		
	for index, fightRole in enumerate(rightRoles):
		right_camp.create_online_role_unit(fightRole, fightRole.GetRoleID(), use_px = True, role_realfight_pos = index + 1, use_property_H=True)
	
	for u in left_camp.pos_units.itervalues():
		u.new_passive_skill(1233,1)
	for u in right_camp.pos_units.itervalues():
		u.new_passive_skill(1233,1)
		
	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	fight.after_fight_param = regParam

	fight.start()
	return fight

def PVE_UnionTask(role, fightId, fightType, AfterFight, regParam = None, OnLeave = None, AfterPlay = None):
	'''
	公会任务战斗
	@param role:
	@param fightId:
	@param fightType:
	@param AfterFight:
	@param regParam:
	@param OnLeave:
	@param AfterPlay:
	'''
	fight = Fight.Fight(fightType)
	fight.restore = True
	left_camp, right_camp = fight.create_camp()
	
	left_camp.create_online_role_unit(role, role.GetRoleID())
	right_camp.create_monster_camp_unit(fightId)

	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	fight.after_fight_param = regParam

	fight.start()
	
def PVP_JJC(role, fightType, desRoleFightData, AfterFight, afterFightParam = None, OnLeave = None, AfterPlay = None):
	'''
	竞技场PVP
	@param role:
	@param fightType:
	@param hasBuff:
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
	left_camp.create_online_role_unit(role, role.GetRoleID(), use_px = True)
	right_camp.create_outline_role_unit(desRoleFightData)
	# 4设置回调函数（不是一定需要设置回调函数，按需来）
	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	# 如果需要带参数，则直接绑定在fight对象上
	fight.after_fight_param = afterFightParam
	# 5开启战斗（之后就不能再对战斗做任何设置了）
	fight.start()
	
def PVP_UnionExplore(role, fightType, desRoleFightData, AfterFight, afterFightParam = None, OnLeave = None, AfterPlay = None):
	'''
	公会魔域探秘PVP
	@param role:
	@param fightType:
	@param hasBuff:
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
	left_camp.create_online_role_unit(role, role.GetRoleID(), use_px = True)
	right_camp.create_outline_role_unit(desRoleFightData)
	# 4设置回调函数（不是一定需要设置回调函数，按需来）
	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	# 如果需要带参数，则直接绑定在fight对象上
	fight.after_fight_param = afterFightParam
	# 5开启战斗（之后就不能再对战斗做任何设置了）
	fight.start()
	