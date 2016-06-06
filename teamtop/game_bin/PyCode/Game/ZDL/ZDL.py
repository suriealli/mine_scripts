#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ZDL.ZDL")
#===============================================================================
# 战斗力
#===============================================================================
import Environment
from Common.Message import AutoMessage
from Game.Property import PropertyEnum
from Game.Role.Data import EnumTempObj, EnumTempInt64, EnumInt8
from Game.Role import Event

#####################################################################################
#策划配置的战斗力计算参数
maxhp = 2500			#生命
attackspeed = 0		#攻击速度
anger = 0			#怒气
attack_p = 7500		#物击
defense_p = 5000		#物防
attack_m = 7500		#法攻
defense_m = 5000		#法防
crit = 5000			#暴击
critpress = 5000		#免暴
antibroken = 5000		#破防
notbroken = 5000		#免破
parry = 5000			#格挡
puncture = 5000		#破挡
damageupgrade = 0	#增伤
damagereduce = 0	#免伤


#####################################################################################
if "_HasLoad" not in dir():
	ZDLParam_Dict = {}
	
	ZDLParam_Dict_Career1 = {}
	ZDLParam_Dict_Career2 = {}

#####################################################################################
def BuildParamDict():
	#构建战斗力参数字典
	global ZDLParam_Dict
	ZDLParam_Dict = {}
	ZDLParam_Dict[PropertyEnum.maxhp] = maxhp
	ZDLParam_Dict[PropertyEnum.attackspeed] = attackspeed
	ZDLParam_Dict[PropertyEnum.anger] = anger
	ZDLParam_Dict[PropertyEnum.attack_p] = attack_p
	ZDLParam_Dict[PropertyEnum.defense_p] = defense_p
	ZDLParam_Dict[PropertyEnum.attack_m] = attack_m
	ZDLParam_Dict[PropertyEnum.defense_m] = defense_m
	ZDLParam_Dict[PropertyEnum.crit] = crit
	ZDLParam_Dict[PropertyEnum.critpress] = critpress
	ZDLParam_Dict[PropertyEnum.antibroken] = antibroken
	ZDLParam_Dict[PropertyEnum.notbroken] = notbroken
	ZDLParam_Dict[PropertyEnum.parry] = parry
	ZDLParam_Dict[PropertyEnum.puncture] = puncture
	ZDLParam_Dict[PropertyEnum.damageupgrade] = damageupgrade
	ZDLParam_Dict[PropertyEnum.damagereduce] = damagereduce
	
	import copy
	global ZDLParam_Dict_Career1, ZDLParam_Dict_Career2
	
	ZDLParam_Dict_Career1 = copy.deepcopy(ZDLParam_Dict)
	del ZDLParam_Dict_Career1[PropertyEnum.attack_m]
	
	ZDLParam_Dict_Career2 = copy.deepcopy(ZDLParam_Dict)
	del ZDLParam_Dict_Career1[PropertyEnum.attack_p]


def GetZDL_Dict(p_dict):
	global ZDLParam_Dict
	if not ZDLParam_Dict or not p_dict:
		return 0
	total = 0
	ZG = ZDLParam_Dict.get
	for pt, pv in p_dict.iteritems():
		total += pv * ZG(pt, 0)
	
	return int(total / 10000.0)


################################################################################
#主角，英雄，总战斗力计算
################################################################################
def RecountPropertyGatherZDL(propertyGather):
	#重算角色总属性集合的战斗力
	#设置这个属性集合的战斗力，等待所有的单位重算完毕才开始把各个单位的战斗力相加
	m_zdl = GetZDL_Dict(propertyGather.total_p_m.p_dict)
	#额外加上天赋卡技能战力
	m_zdl += propertyGather.owner.GetTalentZDL()
	
	#两个战斗力都一样
	propertyGather.total_p.p_dict[PropertyEnum.zdl] = m_zdl
	propertyGather.total_p_m.p_dict[PropertyEnum.zdl] = m_zdl

def GetRoleZDL(role):
	#获取主角战斗力
	return role.GetPropertyGather().total_p_m.p_dict.get(PropertyEnum.zdl, 0)

def GetHeroZDL(role):
	#获取玩家英雄战斗力
	herozdl_dict = {}
	enzdl = PropertyEnum.zdl
	roleHeroMgr = role.GetTempObj(EnumTempObj.enHeroMgr)
	for hero in roleHeroMgr.HeroDict.itervalues():
		if hero.GetStationID() > 0:
			herozdl_dict[hero.GetHeroId()] = hero.GetPropertyGather().total_p_m.p_dict.get(enzdl, 0)
	return herozdl_dict

def RecountTotalZDL(role):
	#所有的单位战斗力重算完毕，开始累加战斗力
	enzdl = PropertyEnum.zdl
	enattack = PropertyEnum.attack_p
	ROLEPRG = role.GetPropertyGather()
	roleZDL = ROLEPRG.total_p_m.p_dict.get(enzdl, 0)
	
	PetZDL = ROLEPRG.pet_p.p_dict.get(enzdl, 0)
	w_p_dict = role.GetPropertyMgr().wing_p.p_dict
	wingZDL = w_p_dict.get(enzdl, 0)
	
	dragonTrainZDL = ROLEPRG.dragonTrain_p.p_dict.get(enzdl, 0)
	#驯龙的战斗力需要加上龙脉基础属性增加的战斗力
	dragonTrainZDL += ROLEPRG.dragonVein_p.p_dict.get(enzdl, 0)

	role_pm = role.GetTempObj(EnumTempObj.PM)
	#婚戒战斗力
	WeddingRingZDL = role_pm.weddingRing_p.p_dict.get(enzdl, 0)
	WeddingRingZDL += role_pm.weddingRingS_p.p_dict.get(enzdl, 0)
	WeddingRingZDL += role_pm.weddingRingSkill_p.p_dict.get(enzdl, 0)
	#特殊婚戒加的攻击
	WeddingRingattack = role_pm.weddingRing_p.p_dict.get(enattack, 0)
	WeddingRingattack += role_pm.weddingRingS_p.p_dict.get(enattack, 0)
	WeddingRingattack += role_pm.weddingRingSkill_p.p_dict.get(enattack, 0)
	
	roleHeroMgr = role.GetTempObj(EnumTempObj.enHeroMgr)
	
	heroZDL = 0
	totalWingZDL = wingZDL
	totalWeddingRingzdl = WeddingRingZDL
	cnt = 1
	#特殊处理翅膀属性
	wingAttack = w_p_dict.get(PropertyEnum.attack_p, 0)
	for hero in roleHeroMgr.HeroDict.itervalues():
		if hero.GetStationID() > 0:
			#只有上阵的才算战斗力
			heroZDL += hero.GetPropertyGather().total_p_m.p_dict.get(enzdl, 0)
			PetZDL += hero.GetPropertyGather().pet_p.p_dict.get(enzdl, 0)
			totalWingZDL += wingZDL
			totalWeddingRingzdl += WeddingRingZDL
			cnt += 1
	#因为翅膀是加物攻和法攻的，需要减去一个攻击对应的战斗加成(一个单位只有一种攻击属性算战斗力)
	totalWingZDL -= int(wingAttack * ZDLParam_Dict.get(enattack, 0) / 10000.0) * cnt
	totalWingZDL = max(totalWingZDL, 0)
	#同上
	totalWeddingRingzdl -= int(WeddingRingattack * ZDLParam_Dict.get(enattack, 0) / 10000.0) * cnt
	totalWeddingRingzdl = max(totalWeddingRingzdl, 0)
	
	#星灵战斗力(出战星灵)
	girlZDL = 0
	starGirlMgr = role.GetTempObj(EnumTempObj.StarGirlMgr)
	fightGirlId = role.GetI8(EnumInt8.StarGirlFightId)
	if fightGirlId:
		p_dict = starGirlMgr.get_star_girl_property(fightGirlId)
		girlZDL = GetZDL_Dict(p_dict)
	
	#记录最新的总战斗力
	role.SetZDL(heroZDL + roleZDL + girlZDL)
	
	if not Environment.IsCross:
		#触发精彩活动
		from Game.Activity.WonderfulAct import WonderfulActMgr, EnumWonderType
		WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_Inc_ZDL, role)
	
	#同步部分客户端不能计算的战斗力(战斗力评分系统)
	if role.GetTI64(EnumTempInt64.TotalPetZDL) != PetZDL or role.GetTI64(EnumTempInt64.TotalWingZDL) != totalWingZDL or \
		role.GetTI64(EnumTempInt64.TotalWeddingRingZDL) != totalWeddingRingzdl or \
		role.GetTI64(EnumTempInt64.DragonTrainZDL) != dragonTrainZDL:
		
		role.SetTI64(EnumTempInt64.TotalPetZDL, PetZDL)
		role.SetTI64(EnumTempInt64.TotalWingZDL, totalWingZDL)
		role.SetTI64(EnumTempInt64.TotalWeddingRingZDL, totalWeddingRingzdl)
		
		role.SetTI64(EnumTempInt64.DragonTrainZDL, dragonTrainZDL)
		role.SendObj(ZDL_Sync_SomeData, (PetZDL, totalWingZDL, totalWeddingRingzdl, dragonTrainZDL))
	
################################################################################
def SyncRoleOtherData(role, param):
	PetZDL = role.GetTI64(EnumTempInt64.TotalPetZDL)
	wingZDL = role.GetTI64(EnumTempInt64.TotalWingZDL)
	totalWeddingRingzdl = role.GetTI64(EnumTempInt64.TotalWeddingRingZDL)
	dragonTrainZDL = role.GetTI64(EnumTempInt64.DragonTrainZDL)
	
	if wingZDL or PetZDL or totalWeddingRingzdl or dragonTrainZDL:
		role.SendObj(ZDL_Sync_SomeData, (PetZDL, wingZDL, totalWeddingRingzdl, dragonTrainZDL))

#===============================================================================
# 事件
#===============================================================================
def OnRecountZDL(role, param):
	'''
	重算战斗力
	@param role:
	@param param:
	'''
	RecountTotalZDL(role)


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		BuildParamDict()
		
	#事件
	Event.RegEvent(Event.Eve_RecountZDL, OnRecountZDL)

	Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
	ZDL_Sync_SomeData = AutoMessage.AllotMessage("ZDL_Sync_SomeData", "同步一部分的战斗力信息")





