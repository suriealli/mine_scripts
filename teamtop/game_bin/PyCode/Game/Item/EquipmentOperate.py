#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Item.EquipmentOperate")
#===============================================================================
# 装备穿戴相关
#===============================================================================
import cRoleMgr
from Common.Message import AutoMessage
from Game.Role.Data import EnumTempObj, EnumObj
from Game.Item import ItemMsg
from Game.Role.Obj import Base

if "_HasLoad" not in dir():
	Equipment_RolePutOn_OK = AutoMessage.AllotMessage("Equipment_RolePutOn_OK", "角色成功穿上一件装备")
	Equipment_HeroPutOn_OK = AutoMessage.AllotMessage("Equipment_HeroPutOn_OK", "英雄成功穿上一件装备")

def InsertEquipment(mgr, prop):
	#管理器增加装备操作
	mgr.objIdDict[prop.oid] = prop
	prop.package = mgr
	
	cd_dict = mgr.codingGather.get(prop.otype)
	if not cd_dict:
		mgr.codingGather[prop.otype] = cd_dict = {}
	cd_dict[prop.oid] = prop
		
	
def RemoveEquipment(mgr, prop):
	#管理器移除装备操作
	del mgr.objIdDict[prop.oid]
	prop.package = None
	
	cd_dict = mgr.codingGather.get(prop.otype)
	del cd_dict[prop.oid]
	if not cd_dict:
		del mgr.codingGather[prop.otype]

##########################################################################################
def OnPutOnRoleEquipment(role, msg):
	'''
	角色穿装备
	@param role:
	@param msg:装备ID
	'''
	eId = msg
	packMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	#一定要在背包查找这个装备
	equipment= packMgr.FindProp(eId)
	if not equipment : return
	
	if equipment.Obj_Type != Base.Obj_Type_Equipment:
		#竟然不是装备?
		return
	if equipment.cfg.needlevel > role.GetLevel():
		#等级不足
		return
	#转生等级
	if equipment.cfg.ZhuanShengLevel > role.GetZhuanShengLevel():
		return 
	#这件装备需要放置的位置
	posType = equipment.cfg.posType
	if posType < 0 or posType > 8:
		print "GE_EXC, OnPutOnRoleEquipment error pos (%s)" % posType
		return
	
	packIdSet = role.GetObj(EnumObj.En_PackageItems)
	equipmentIdSet = role.GetObj(EnumObj.En_RoleEquipments)
	roleEquipmentMgr = role.GetTempObj(EnumTempObj.enRoleEquipmentMgr)
	#看看原来的位置是否已经佩戴了一件装备
	equipment_2 = None
	for eq in roleEquipmentMgr.objIdDict.values():
		if eq.cfg.posType == posType:
			equipment_2 = eq
			break
	
	if equipment_2:
		#交换两件装备
		#清理两个背包中的相关数据
		RemoveEquipment(roleEquipmentMgr, equipment_2)
		RemoveEquipment(packMgr, equipment)
		#清理角色OBJ记录
		packIdSet.discard(eId)
		equipmentIdSet.discard(equipment_2.oid)
		#清理拥有者
		equipment_2.owner = None
		
		#重新写入交换后的数据
		InsertEquipment(roleEquipmentMgr, equipment)
		InsertEquipment(packMgr, equipment_2)
		#重新写入角色OBJ记录
		equipmentIdSet.add(eId)
		packIdSet.add(equipment_2.oid)
		##拥有者拥有者
		equipment.owner = role
		
		if equipment.cfg.suitId and equipment.cfg.suitId != equipment_2.cfg.suitId:
			#触发重置套装属性
			roleEquipmentMgr.ResetStrengthenSuit()
		
		#同步客户端，身上的装备脱到背包
		role.SendObj(ItemMsg.Item_SyncItem_Package, equipment_2.oid)
	else:
		#直接穿上去
		#清理背包管理器
		RemoveEquipment(packMgr, equipment)
		#清理人物数组数据
		packIdSet.discard(eId)
		
		#更新角色装备管理器数据
		InsertEquipment(roleEquipmentMgr, equipment)
		#拥有者
		equipment.owner = role
		#人物数组数据
		equipmentIdSet.add(eId)
		
		if equipment.cfg.suitId:
			#重置套装属性
			roleEquipmentMgr.ResetStrengthenSuit()
	
	#同步穿装备成功
	role.SendObj(Equipment_RolePutOn_OK, eId)
	if posType <= 6:
		#重算装备属性Flag
		role.GetPropertyGather().ReSetRecountEquipmentFlag()


def OnTakeOffRoleEquipment(role, msg):
	'''
	角色脱装备
	@param role:
	@param msg:装备ID
	'''
	
	eId = msg
	if role.PackageIsFull():
		return
	roleEquipmentMgr = role.GetTempObj(EnumTempObj.enRoleEquipmentMgr)
	equipment = roleEquipmentMgr.FindProp(eId)
	if not equipment:return
	
	equipmentIdSet = role.GetObj(EnumObj.En_RoleEquipments)
	if eId not in equipmentIdSet:
		return
	
	#数组数据
	packIdSet = role.GetObj(EnumObj.En_PackageItems)
	
	equipmentIdSet.discard(eId)
	RemoveEquipment(roleEquipmentMgr, equipment)
	equipment.owner = None
	
	packIdSet.add(eId)
	InsertEquipment(role.GetTempObj(EnumTempObj.enPackMgr), equipment)
	
	posType = equipment.cfg.posType
	if equipment.cfg.suitId:
		#重置套装属性
		roleEquipmentMgr.ResetStrengthenSuit()
	if posType <= 6:
		#重算属性Flag
		role.GetPropertyGather().ReSetRecountEquipmentFlag()

	#同步客户端
	#身上的装备脱到背包
	role.SendObj(ItemMsg.Item_SyncItem_Package, eId)
	

def OnPutOnHeroEquipment(role, msg):
	'''
	英雄穿装备
	@param role:
	@param msg:(英雄ID, 装备ID)
	'''
	
	heroId, eId = msg
	hero = role.GetHero(heroId)
	if not hero : return
	if not hero.GetStationID():
		return
	heroEquipmentMgr = hero.equipmentMgr
	if not heroEquipmentMgr : return
	
	packMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	equipment= packMgr.FindProp(eId)
	if not equipment : return
	
	if equipment.Obj_Type != Base.Obj_Type_Equipment:
		return
	if equipment.cfg.needlevel > hero.GetLevel():
		#等级
		return
	if equipment.cfg.IsRole == 1:#只有主角能穿戴
		return
	#转生等级
	if equipment.cfg.ZhuanShengLevel > hero.GetZhuanShengLevel():
		return 
	#这件装备需要放置的位置
	posType = equipment.cfg.posType
	if posType < 0 or posType > 6:
		return
	
	packIdSet = role.GetObj(EnumObj.En_PackageItems)
	equipmentIdSet = role.GetObj(EnumObj.En_HeroEquipments).get(heroId)
	
	##看看原来的位置是否已经佩戴了一件装备
	equipment_2 = None
	for eq in heroEquipmentMgr.objIdDict.values():
		if eq.cfg.posType == posType:
			equipment_2 = eq
			break
	
	if equipment_2:
		#交换两件装备
		packIdSet.discard(eId)
		equipmentIdSet.discard(equipment_2.oid)
		
		RemoveEquipment(heroEquipmentMgr, equipment_2)
		RemoveEquipment(packMgr, equipment)
		
		equipment_2.owner = None
		
		InsertEquipment(heroEquipmentMgr, equipment)
		InsertEquipment(packMgr, equipment_2)
		
		equipmentIdSet.add(eId)
		packIdSet.add(equipment_2.oid)
		#更新拥有者
		equipment.owner = hero
		
		if equipment.cfg.suitId and equipment.cfg.suitId != equipment_2.cfg.suitId:
			#重置套装属性
			heroEquipmentMgr.ResetStrengthenSuit()
		#身上的装备脱到背包
		role.SendObj(ItemMsg.Item_SyncItem_Package, equipment_2.oid)
	else:
		#直接穿上去
		RemoveEquipment(packMgr, equipment)
		#删除人物数组数据
		packIdSet.discard(eId)
		
		InsertEquipment(heroEquipmentMgr, equipment)
		equipmentIdSet.add(eId)
		#拥有者
		equipment.owner = hero
		
		if equipment.cfg.suitId:
			#重置套装属性
			heroEquipmentMgr.ResetStrengthenSuit()
	#重算属性Flag
	hero.propertyGather.ReSetRecountEquipmentFlag()
	role.SendObj(Equipment_HeroPutOn_OK, (heroId, eId))
	

def OnTakeOffHeroEquipment(role, msg):
	'''
	英雄脱装备
	@param role:
	@param msg:(英雄ID, 装备ID)
	'''
	heroId, eId = msg
	if role.PackageIsFull() : return
	
	hero = role.GetHero(heroId)
	if not hero:return
	
	heroEquipmentMgr = hero.equipmentMgr
	if not heroEquipmentMgr:return
	
	equipment = heroEquipmentMgr.FindProp(eId)
	if not equipment:return
	
	equipmentIdSet = role.GetObj(EnumObj.En_HeroEquipments).get(heroId)
	if eId not in equipmentIdSet : return
	
	packIdSet = role.GetObj(EnumObj.En_PackageItems)
	
	equipmentIdSet.discard(eId)
	equipment.owner = None
	RemoveEquipment(heroEquipmentMgr, equipment)
	
	InsertEquipment(role.GetTempObj(EnumTempObj.enPackMgr), equipment)
	packIdSet.add(eId)
	if equipment.cfg.suitId:
		#重置套装属性
		heroEquipmentMgr.ResetStrengthenSuit()
	#重算属性Flag
	hero.propertyGather.ReSetRecountEquipmentFlag()
	
	#同步客户端身上的装备脱到背包
	role.SendObj(ItemMsg.Item_SyncItem_Package, eId)
	
if "_HasLoad" not in dir():
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Equipment_RolePutOn", "角色穿上装备"), OnPutOnRoleEquipment)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Equipment_RoleTakeOff", "角色脱下装备"), OnTakeOffRoleEquipment)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Equipment_HeroPutOn", "英雄穿上装备"), OnPutOnHeroEquipment)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Equipment_HeroTakeOff", "英雄脱下装备"), OnTakeOffHeroEquipment)
	
