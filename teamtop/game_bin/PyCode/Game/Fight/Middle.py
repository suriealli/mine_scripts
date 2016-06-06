#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.Middle")
#===============================================================================
# 中间数据
#===============================================================================
from Game.Property import PropertyEnum
from Game.Role.Data import EnumObj, EnumTempObj, EnumInt16, EnumInt8, EnumTempInt64, EnumInt1,\
	EnumInt64

RoleID = 1				#角色ID
ControlRoleID = 2		#控制角色ID
RoleName = 3			#角色名
FightPos = 4			#布阵位置
Level = 5				#等级
Sex = 6					#性别
Career = 7				#职业
Grade = 8				#品阶
HeroType = 9			#英雄类型
MonsterID = 10			#怪物ID
ActiveSkills = 11		#主动技能列表
PassiveSkills = 12		#被动技能列表
NormalSkill = 13		#普通技能（怪物，英雄只有一个）
#===============================================================================
# 注意，因为策划改动需求，对于英雄来说主动技能是多个了
# 但是为了兼容新旧配表【减少策划测试工作量】
# 和为了兼容外网的战斗数据缓存，这里改动了变量的语意。
# 真蛋碎，后面的修改注意别踩这个坑！
#===============================================================================
ActiveSkill = 14		#主动技能（怪物，英雄只有一个）
MountEvolveID = 15		#坐骑等级进化ID
MountProperty = 16		#坐骑属性字典
HelpStation = 17		#助阵英雄列表
HelpStationProperty = 18#助阵属性
WingID = 19				#翅膀

MaxHP = 20				#最大HP
Morale = 21				#士气
Speed = 22				#速度
AttackP = 23			#物攻
AttackM = 24			#法攻
DefenceP = 25			#物防
DefenceM = 26			#法防
Crit = 27				#暴击
CritPress = 28			#免暴
AntiBroken = 29			#破防
NotBroken = 30			#免破
Parry = 31				#格挡
Puncture = 32			#免挡
DamageUpgrade = 33		#增伤
DamageReduce = 34		#免伤

GActiveSkills = 35		#组队主动技能列表
GPassiveSkills = 36		#组队被动技能列表
GFightPos = 37			#组队位置
IsOnline = 38			#是否在线
GCareer = 39			#组队职业
StarGirlUnit = 40		#星灵单位
StarGirlID = 41			#星灵ID
StarGirlGrade = 42		#星灵品阶
StarGirlStarLevel = 43	#星灵星级
TitleProperty_Role = 44	#称号主角属性
TitleProperty_Team = 45	#称号队伍属性

PetType = 50			#宠物类型(改为宠物外观)

FashionClothes = 51		#时装衣服
FashionHat = 52			#时装帽子
FashionWeapons = 53		#时装武器
FashionState = 54		#时装显示状态
DragonTrainProperty = 55#驯龙属性字典
MountID = 56			#坐骑ID
WarStationID = 57		#战阵需要
StationSoulID = 58		#阵灵ID
#===============================================================================






#===============================================================================
# 专门用于特殊战斗修改战斗数据的
#===============================================================================
RoleDataHandle = None
class RDH(object):
	def __init__(self, fun):
		self.fun = fun
	
	def __enter__(self):
		global RoleDataHandle
		RoleDataHandle = self.fun
	
	def __exit__(self, _type, _value, _traceback):
		global RoleDataHandle
		RoleDataHandle = None
		return False
#上阵位置图
#	2
#	3	1
#	4

#战斗内位置图
#	2	1
#	4	3
#	6	5

#只有主角的战斗位置图
#	2(1主角)
#		3(2主角)
#	6(3主角)

#带一个英雄的战斗位置图 (英雄站位 = 主角站位 - 1)
#	2(1主角)	1(1英雄)
#	4(2主角)	3(2英雄)
#	6(3主角)	5(3英雄)

#上阵位置转换成战斗位置
POS_TRANSFORM = {1:3, 2:2, 3:4, 4:6}
#(只有主角)组队位置转换成战斗位置
GVE_POS_TRANSFORM = {0:0, 1:2, 2:3, 3:6}
#(有一个英雄的主角站位转换)
ROLE_POS_TEAM_TRANSFORM = {0:0, 1:2, 2:4, 3:6}
#(同上，根据主角位置转换)
HERO_POS_TEAM_TRANSFORM = {0:0, 1:1, 2:3, 3:5}

def GetRoleData(role, use_property_X = False, t_p_i = 0, role_realfight_pos = -1, use_property_H =False):
	'''
	获取战斗数据，主角和英雄
	@param role:
	@param use_property_X: 是否是PVP属性
	@param t_p_i: 只有主角的组队战斗，主角的站位
	@param role_realfight_pos: 主角带一个英雄，主角的站位 传入参数默认为 1,2,3
	'''
	role_data = _GetRoleData(role, use_property_X, t_p_i, role_realfight_pos, use_property_H)
	hero_datas = {}
	if role_realfight_pos == -1:
		#非主角类型的组队战斗才需要用到英雄
		for hero in role.GetTempObj(EnumTempObj.enHeroMgr).HeroDict.itervalues():
			stationId = hero.GetStationID()
			if not stationId:
				continue
			pos = POS_TRANSFORM[stationId]
			hero_datas[pos] = _GetHeroData(hero, pos, role, use_property_X, use_property_H)
		#处理怒气
		totalAnger = 0
		for heroData in hero_datas.itervalues():
			totalAnger += heroData.get(Morale, 0)
		role_data[Morale] = role_data.get(Morale, 0) + totalAnger
	else:
		#带一个英雄的组队战斗数据
		heropos = HERO_POS_TEAM_TRANSFORM[role_realfight_pos]
		jtherodata = _GetJTHeroData(role, heropos, use_property_X, use_property_H)
		if jtherodata:
		#替换hero_datas
			hero_datas[jtherodata[0]] = jtherodata[1]
		#处理怒气
		totalAnger = 0
		for hero in role.GetTempObj(EnumTempObj.enHeroMgr).HeroDict.itervalues():
			stationId = hero.GetStationID()
			if not stationId:
				continue
			p_dict = hero.GetPropertyGather().total_p_m.p_dict if use_property_X  else hero.GetPropertyGather().total_p.p_dict
			totalAnger += p_dict.get(PropertyEnum.anger, 0)
		role_data[Morale] = role_data.get(Morale, 0) + totalAnger
	
	if RoleDataHandle is not None:
		RoleDataHandle(role_data, hero_datas)
	return role_data, hero_datas

#===================================
#如果要增加战斗外观显示，请搜索get_unit_info
#===================================

def _GetRoleData(role, use_property_X = False, team_pos_index = 0, role_realfight_pos = 0, use_property_H = False):
	if use_property_H:
		p_dict = role.GetPropertyGather().total_p_h.p_dict
	elif use_property_X:
		p_dict = role.GetPropertyGather().total_p_m.p_dict
	else:
		p_dict = role.GetPropertyGather().total_p.p_dict
	
	PG = p_dict.get
	
	#骑乘坐骑战斗
	mountID = role.GetRightMountID()
	#战斗中的坐骑属性显示
	mountEvolveID = role.GetI16(EnumInt16.MountEvolveID) if use_property_X else 0
	#坐骑总属性(坐骑培养属性+坐骑外形品质属性)
	mountProperty = role.GetTempObj(EnumTempObj.MountMgr).GetTotalAttribute() if use_property_X else None
	#神龙属性
	dragonTrainProperty = role.GetTempObj(EnumTempObj.DragonTrainMgr).get_total_property_dict() if use_property_X else None
	#龙脉和驯龙的属性要加到一起
	if dragonTrainProperty != None:
		dragonTrainProperty = dict(dragonTrainProperty)
		DG = dragonTrainProperty.get
		for pt, pv in role.GetTempObj(EnumTempObj.DragonVein).GetTotalProperty().iteritems():
			dragonTrainProperty[pt] = DG(pt, 0) + pv
	#称号属性
	if use_property_H:
		title_Role_Property = dict(role.GetPropertyGather().titleRoleEx_p.p_dict, **role.GetPropertyGather().titleRole_p.p_dict)
		title_Team_Property = dict(role.GetTempObj(EnumTempObj.PM).titleTeamEx_p.p_dict, **role.GetTempObj(EnumTempObj.PM).titleTeam_p.p_dict)
	elif use_property_X:
		title_Role_Property = role.GetPropertyGather().titleRole_p.p_dict
		title_Team_Property = role.GetTempObj(EnumTempObj.PM).titleTeam_p.p_dict
	else:
		title_Role_Property = {}
		title_Team_Property = {}
	
	skillDict = role.GetObj(EnumObj.RoleSkill)
	role_ActiveSkills = [(skill_id, skillDict[skill_id]) for skill_id in role.GetObj(EnumObj.RoleFightSkill).get(1)]
	
	role_GActiveSkills = []
	role_GPassiveSkills = []
	DM = role.GetTempObj(EnumTempObj.DragonMgr)
	if DM:
		#有的环境下是没有这个系统的
		role_GActiveSkills = role.GetTempObj(EnumTempObj.DragonMgr).get_active_skills()
		role_GPassiveSkills = role.GetTempObj(EnumTempObj.DragonMgr).get_passive_skills()
	
	if team_pos_index == 0:
		#北美GVE
		team_pos_index = role.GetDragonCareerID()
		
	role_PassiveSkills = role.GetTempObj(EnumTempObj.TalentCardMgr).GetCardSkill(2)
	#装载魔法阵技能
	magicSpiritSkill = role.GetMFZSkill()
	if len(magicSpiritSkill):
		role_PassiveSkills += magicSpiritSkill
	#装载阵灵技能
	stationSoulSkill = role.GetStationSoulSkill()
	if stationSoulSkill:
		role_PassiveSkills += stationSoulSkill
	#装载元素之灵技能
	elementSpiritSkill = role.GetElementSpiritSkill()
	if elementSpiritSkill:
		role_PassiveSkills += elementSpiritSkill
		
	#组队战斗位置
	teamFightPos = team_pos_index
	if role_realfight_pos == -1:
		teamFightPos = GVE_POS_TRANSFORM[team_pos_index]
	else:
		teamFightPos = ROLE_POS_TEAM_TRANSFORM[role_realfight_pos]
	
	return {RoleID: role.GetRoleID(),
		RoleName: role.GetRoleName(),
		FightPos: POS_TRANSFORM[role.GetStationID()],
		GFightPos: teamFightPos,
		Level: role.GetLevel(),
		Sex: role.GetSex(),
		Career: role.GetCareer(),
		GCareer: role.GetDragonCareerID(),
		Grade: role.GetGrade(),
		ActiveSkills: role_ActiveSkills,
		PassiveSkills: role_PassiveSkills,
		GActiveSkills: role_GActiveSkills,
		GPassiveSkills: role_GPassiveSkills,
		MountEvolveID:mountEvolveID,
		MountID : mountID,
		MountProperty:mountProperty,
		HelpStation: role.GetTempObj(EnumTempObj.enStationMgr).GetHelpStationNumbers(),
		HelpStationProperty:role.GetTempObj(EnumTempObj.HelpStationProperty),
		WingID:role.GetWingID(),
		PetType:role.GetI8(EnumInt8.PetType),
		MaxHP: PG(PropertyEnum.maxhp, 0),
		Morale: PG(PropertyEnum.anger, 0),
		Speed: PG(PropertyEnum.attackspeed, 0),
		AttackP: PG(PropertyEnum.attack_p, 0),
		AttackM: PG(PropertyEnum.attack_m, 0),
		DefenceP: PG(PropertyEnum.defense_p, 0),
		DefenceM: PG(PropertyEnum.defense_m, 0),
		Crit: PG(PropertyEnum.crit, 0),
		CritPress: PG(PropertyEnum.critpress, 0),
		AntiBroken: PG(PropertyEnum.antibroken, 0),
		NotBroken: PG(PropertyEnum.notbroken, 0),
		Parry: PG(PropertyEnum.parry, 0),
		Puncture: PG(PropertyEnum.puncture, 0),
		DamageUpgrade: PG(PropertyEnum.damageupgrade, 0),
		DamageReduce: PG(PropertyEnum.damagereduce, 0),
		FashionClothes: role.GetTI64(EnumTempInt64.FashionClothes),
		FashionHat: role.GetTI64(EnumTempInt64.FashionHat),
		FashionWeapons: role.GetTI64(EnumTempInt64.FashionWeapons),
		FashionState: role.GetI1(EnumInt1.FashionViewState),
		DragonTrainProperty: dragonTrainProperty,
		StarGirlUnit: _GetStarGirlData(role),
		TitleProperty_Role : title_Role_Property,
		TitleProperty_Team : title_Team_Property,
		WarStationID: role.GetI16(EnumInt16.WarStationStarNum),
		StationSoulID: role.GetI16(EnumInt16.StationSoulId),
		}

def _GetJTHeroData(role, heropos, use_property_X, use_property_H):
	#获取组队战斗上阵英雄数据
	jtheroid = role.GetI64(EnumInt64.JTHeroID)
	if not jtheroid:
		return None
	hero = role.GetHero(jtheroid)
	if not hero or not hero.GetStationID():
		return None
	return heropos, _GetHeroData(hero, heropos, role, use_property_X, use_property_H)

	
def _GetStarGirlData(role):
	# 没有星灵出战
	starGirlId = role.GetI8(EnumInt8.StarGirlFightId)
	if not starGirlId:
		return None
	starGirlMgr = role.GetTempObj(EnumTempObj.StarGirlMgr)
	#是否已解锁
	if starGirlId not in starGirlMgr.girl_dict:
		return None
	
	starGirlObj = starGirlMgr.girl_dict[starGirlId]
	PG = starGirlObj.property_dict.get
	return {StarGirlID: starGirlId,
		StarGirlGrade: starGirlObj.grade,
		StarGirlStarLevel: starGirlObj.star_level,
		Level: starGirlObj.level,
		Career: 2,
		MaxHP: PG(PropertyEnum.maxhp, 0),
		Speed: PG(PropertyEnum.attackspeed, 0),
		AttackP: PG(PropertyEnum.attack_p, 0),
		AttackM: PG(PropertyEnum.attack_m, 0),
		DefenceP: PG(PropertyEnum.defense_p, 0),
		DefenceM: PG(PropertyEnum.defense_m, 0),
		Crit: PG(PropertyEnum.crit, 0),
		CritPress: PG(PropertyEnum.critpress, 0),
		AntiBroken: PG(PropertyEnum.antibroken, 0),
		NotBroken: PG(PropertyEnum.notbroken, 0),
		Parry: PG(PropertyEnum.parry, 0),
		Puncture: PG(PropertyEnum.puncture, 0),
		DamageUpgrade: PG(PropertyEnum.damageupgrade, 0),
		DamageReduce: PG(PropertyEnum.damagereduce, 0),
		ActiveSkill: starGirlObj.get_active_skill(),
		PassiveSkills: starGirlObj.get_passive_skill(),
		}

def _GetHeroData(hero, pos, role, use_property_X = False, use_property_H = False):
	if use_property_H:
		#称号全队隐藏属性
		p_dict = hero.GetPropertyGather().total_p_h.p_dict
	elif use_property_X:
		p_dict = hero.GetPropertyGather().total_p_m.p_dict
	else:
		p_dict = hero.GetPropertyGather().total_p.p_dict
	
	PG = p_dict.get
	roleid = role.GetRoleID()
	heroPassiveSkill = hero.GetPassiveSkill()
	TalentPassiveSkills = role.GetTempObj(EnumTempObj.TalentCardMgr).GetCardSkill(hero.GetHeroId())
	PassiveSkill = []
	PassiveSkill += heroPassiveSkill
	if TalentPassiveSkills:
		PassiveSkill += TalentPassiveSkills
	
	#魔法阵技能
	magicSpiritSkill = hero.GetMFZSkill()
	if len(magicSpiritSkill):
		PassiveSkill += magicSpiritSkill
	#装载阵灵技能
	stationSoulSkill = hero.GetStationSoulSkill()
	if stationSoulSkill:
		PassiveSkill += stationSoulSkill
	#装载元素之灵技能
	elementSpiritSkill = hero.GetElementSpiritSkill()
	if elementSpiritSkill:
		PassiveSkill += elementSpiritSkill
	
	return {RoleID: roleid,
		HeroType: hero.cfg.heroNumber,
		FightPos: pos,
		Level: hero.GetLevel(),
		Career: hero.GetCareer(),
		PetType:hero.GetPetType(),
		NormalSkill: hero.GetNormalSkill(),
		ActiveSkill: hero.GetActiveSkill(),
		PassiveSkills: PassiveSkill, 
		MaxHP: PG(PropertyEnum.maxhp, 0),
		Morale: PG(PropertyEnum.anger, 0),
		Speed: PG(PropertyEnum.attackspeed, 0),
		AttackP: PG(PropertyEnum.attack_p, 0),
		AttackM: PG(PropertyEnum.attack_m, 0),
		DefenceP: PG(PropertyEnum.defense_p, 0),
		DefenceM: PG(PropertyEnum.defense_m, 0),
		Crit: PG(PropertyEnum.crit, 0),
		CritPress: PG(PropertyEnum.critpress, 0),
		AntiBroken: PG(PropertyEnum.antibroken, 0),
		NotBroken: PG(PropertyEnum.notbroken, 0),
		Parry: PG(PropertyEnum.parry, 0),
		Puncture: PG(PropertyEnum.puncture, 0),
		DamageUpgrade: PG(PropertyEnum.damageupgrade, 0),
		DamageReduce: PG(PropertyEnum.damagereduce, 0),
		}
