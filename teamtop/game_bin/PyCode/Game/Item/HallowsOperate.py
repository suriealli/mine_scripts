#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Item.HallowsOperate")
#===============================================================================
# 圣器角色操作（穿戴等）
#===============================================================================
import cRoleMgr
from Common.Message import AutoMessage
from Game.Item import ItemMsg
from Game.Role.Obj import Base
from Game.Role.Data import EnumTempObj, EnumObj
from Game.Role import Event
from Common.Other import EnumKick, GlobalPrompt

if "_HasLoad" not in dir():
	Hallows_RolePutOn_OK = AutoMessage.AllotMessage("Hallows_RolePutOn_OK", "角色成功装备一件圣器")
	Hallows_HeroPutOn_OK = AutoMessage.AllotMessage("Hallows_HeroPutOn_OK", "英雄成功装备一件圣器")

def AddHallow(mgr, prop):
	#管理器增加圣器
	mgr.objIdDict[prop.oid] = prop
	#设置物品管理器
	prop.package = mgr
	cd_dict = mgr.codingGather.get(prop.otype)
	if not cd_dict:
		mgr.codingGather[prop.otype] = cd_dict = {}
	cd_dict[prop.oid] = prop
	
def Removehallow(mgr, prop):
	#管理器移除圣器
	if prop.oid in mgr.objIdDict:
		del mgr.objIdDict[prop.oid]
	prop.package = None
	cd_dict = mgr.codingGather.get(prop.otype)
	if prop.oid in cd_dict:
		del cd_dict[prop.oid]
	if not cd_dict:
		del mgr.codingGather[prop.otype]

def OnRoleEquipHallows(role, msg):
	'''
	角色装备圣器
	@param role:
	@param msg:神器
	'''
	#获取圣器部件ID
	hallowID = msg
	if not msg:
		return
	#获取玩家背包管理器
	packMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	#背包管理器获取失败？
	if not packMgr:
		return
	#根据圣器部件ID，从玩家背包中获取圣器部件obj
	hallowthing = packMgr.FindProp(hallowID)
	#背包中不存在这个物品？
	if not hallowthing:
		return
	#该物品不是圣器部件
	if hallowthing.Obj_Type != Base.Obj_Type_Hallows:
		return
	
	#等级不足
	if role.GetLevel() < hallowthing.cfg.needlevel:
		return
	
	#获取圣器装备位置
	pos = hallowthing.cfg.posType
	#圣器部件的装备位置必须在1和6之间
	if not 0 <= pos <= 6:
		print "GE_EXC, error Pos(%s) for Hallow(hallowID) in config" % (pos, hallowID)
		return

	#获取角色圣器管理器
	RoleHallowsMgr = role.GetTempObj(EnumTempObj.enRoleHallowsMgr)
	#获取角色圣器ID集合
	HallowsIdSet = role.GetObj(EnumObj.En_RoleHallows)
	#获取角色背包ID集合
	packIdSet = role.GetObj(EnumObj.En_PackageItems)
	#玩家圣器装配字典
	roleHallowDict = RoleHallowsMgr.GetRoleHallowsDict()
	#获取该位置之前装配的圣器部件
	exhallowthing = roleHallowDict.get(pos)
	
	#如果该位置之前有圣器部件
	if exhallowthing:
		#交换角色和背包圣器部件信息
		Removehallow(RoleHallowsMgr, exhallowthing)
		Removehallow(packMgr, hallowthing)
		#清理角色和背包set
		packIdSet.discard(hallowID)
		HallowsIdSet.discard(exhallowthing.oid)
		#清理拥有者
		exhallowthing.owner = None
		#重新写入数据
		AddHallow(RoleHallowsMgr, hallowthing)
		AddHallow(packMgr, exhallowthing)
		#重新写入角色OBJ记录
		HallowsIdSet.add(hallowID)
		packIdSet.add(exhallowthing.oid)
		#拥有者
		hallowthing.owner = role
		#同步客户端，身上的圣器脱到背包
		role.SendObj(ItemMsg.Item_SyncItem_Package, exhallowthing.oid)
	#直接装备圣器
	else:
		Removehallow(packMgr, hallowthing)
		packIdSet.discard(hallowID)
		AddHallow(RoleHallowsMgr, hallowthing)
		hallowthing.owner = role
		HallowsIdSet.add(hallowID)
		#同步圣器装备成功
	role.SendObj(Hallows_RolePutOn_OK, hallowID)
	#触发重算
	role.GetPropertyGather().ReSetRecountHallowsFlag()


def OnRoleUnloadHallows(role, msg):
	'''
	角色卸载圣器
	@param role:
	@param msg:圣器id
	'''
	#获取圣器部件ID
	hallowID = msg
	if not msg:
		return
	#背包满了
	if role.PackageIsFull():
		role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
		return
	roleHallowsMgr = role.GetTempObj(EnumTempObj.enRoleHallowsMgr)
	hallows = roleHallowsMgr.FindProp(hallowID)
	#如果角色身上没有这件装备
	if not hallows:
		return
	hallowsIdSet = role.GetObj(EnumObj.En_RoleHallows)
	if not hallowID in hallowsIdSet:
		return
	#数组数据
	packIdSet = role.GetObj(EnumObj.En_PackageItems)
	hallowsIdSet.discard(hallowID)
	Removehallow(roleHallowsMgr, hallows)
	hallows.owner = None
	packIdSet.add(hallowID)
	AddHallow(role.GetTempObj(EnumTempObj.enPackMgr), hallows)
	#重算属性Flag
	role.GetPropertyGather().ReSetRecountHallowsFlag()
	#同步客户端
	#身上的神器脱到背包
	role.SendObj(ItemMsg.Item_SyncItem_Package, hallowID)

def OnHeroEquipHallows(role, msg):
	'''
	英雄装备圣器
	@param role:
	@param msg:(英雄ID, 圣器ID)
	'''
	heroId, hallowId = msg
	hero = role.GetHero(heroId)
	#如果没有获取到英雄
	if not hero:
		return
	#如果英雄没有出阵
	if not hero.GetStationID():
		return
	#获取英雄圣器管理器
	heroHallowsMgr = hero.HallowsMgr
	if not heroHallowsMgr:
		return
	#检查玩家背包
	packMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	#获取背包中的圣器
	hallowthing = packMgr.FindProp(hallowId)
	#无法装备背包中不存在的圣器
	if not hallowthing:
		return
	#无法装备一件不是圣器的物品
	if hallowthing.Obj_Type !=  Base.Obj_Type_Hallows:
		return
	#等级不足
	if  hero.GetLevel() < hallowthing.cfg.needlevel:
		return
	
	posType = hallowthing.cfg.posType
	#无法装备装备位置不正确的圣器
	if not 1 <= posType <= 6:
		return
	#获取背包id集合和英雄身上的圣器id集合，稍后需要进行操作
	packIdSet = role.GetObj(EnumObj.En_PackageItems)
	hallowsIdSet = role.GetObj(EnumObj.En_HeroHallows).get(heroId, None)
	if hallowsIdSet is None:
		print "GE_EXC, OnHeroEquipHallows error data  (%s)  Kick role " % role.GetRoleID()
		role.Kick(True, EnumKick.DataError_Pack)
		return
	
	#英雄圣器装配字典
	heroHallowsDict = heroHallowsMgr.GetHeroHallowsDict()
	exhallowthing = heroHallowsDict.get(posType)
	
	#如果英雄改位置有圣器
	if exhallowthing:
		#交换英雄和背包圣器部件信息
		Removehallow(heroHallowsMgr, exhallowthing)
		Removehallow(packMgr, hallowthing)
		#清理英雄和背包set
		packIdSet.discard(hallowId)
		hallowsIdSet.discard(exhallowthing.oid)
		#清理拥有者
		exhallowthing.owner = None
		#重新写入数据至管理器
		AddHallow(heroHallowsMgr, hallowthing)
		AddHallow(packMgr, exhallowthing)
		#重新写入角色obj记录
		hallowsIdSet.add(hallowId)
		packIdSet.add(exhallowthing.oid)
		#修改上装圣器拥有者为英雄
		hallowthing.owner = hero
		#同步客户端，身上的圣器脱到背包
		role.SendObj(ItemMsg.Item_SyncItem_Package, exhallowthing.oid)
	else:
		#背包管理器清除该圣器
		Removehallow(packMgr, hallowthing)
		packIdSet.discard(hallowId)
		#英雄圣器管理器增加该圣器
		AddHallow(heroHallowsMgr, hallowthing)
		hallowsIdSet.add(hallowId)
		hallowthing.owner = hero
	
	#同步圣器装备成功
	role.SendObj(Hallows_HeroPutOn_OK, (heroId,hallowId))
	#触发重算
	hero.GetPropertyGather().ReSetRecountHallowsFlag()

def OnHeroUnloadHallows(role, msg):
	'''
	英雄卸载圣器
	@param role:
	@param msg:(英雄ID, 圣器ID)
	'''
	heroId, hallowsId = msg
	#背包满了
	if role.PackageIsFull():
		role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
		return
	hero = role.GetHero(heroId)
	#获取不到英雄
	if not hero:
		return
	#获取英雄圣器管理器
	herohallowsMgr = hero.HallowsMgr
	if not herohallowsMgr:
		return
	#获取圣器
	hallowthing = herohallowsMgr.FindProp(hallowsId)
	if not hallowthing:
		return
	#获取英雄身上的圣器信息
	hallowsIdSet = role.GetObj(EnumObj.En_HeroHallows).get(heroId)
	if not hallowsId in hallowsIdSet:
		return
	#获取角色背包物品id集合
	packIdSet = role.GetObj(EnumObj.En_PackageItems)
	#英雄身上的圣器信息中删除hallowsId
	hallowsIdSet.discard(hallowsId)
	#修改圣器拥有者
	hallowthing.owner = None
	#角色圣器管理器删除该圣器
	Removehallow(herohallowsMgr, hallowthing)
	#背包管理器中增加该圣器
	AddHallow(role.GetTempObj(EnumTempObj.enPackMgr), hallowthing)
	packIdSet.add(hallowsId)
	#触发重算
	hero.GetPropertyGather().ReSetRecountHallowsFlag()
	#同步客户端身上的神器脱到背包
	role.SendObj(ItemMsg.Item_SyncItem_Package, hallowsId)
	
def OnRoleFirstLogin(role, param):
	'''
	角色在版本更新后第一次 登录
	@param role:
	@param param:
	'''
	if type(role.GetObj(EnumObj.En_RoleHallows)) != set:
		role.SetObj(EnumObj.En_RoleHallows, set())

if "_HasLoad" not in dir():
	#事件
	Event.RegEvent(Event.Eve_SyncRoleOtherData, OnRoleFirstLogin)
	#消息
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Hallows_RolePutOn", "角色装备圣器"), OnRoleEquipHallows)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Hallows_RolePutOff", "角色脱下圣器"), OnRoleUnloadHallows)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Hallows_HeroPutOn", "英雄装备圣器"), OnHeroEquipHallows)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Hallows_HeroPutOff", "英雄脱下圣器"), OnHeroUnloadHallows)
