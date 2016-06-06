#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Obj.Unify")
#===============================================================================
# Obj统一入口
#===============================================================================
from Common.Message import AutoMessage
from Game.Item import PackMgr
from Game.Role.Data import EnumTempObj
from Game.Hero import RoleHeroMgr
from Common.Other import EnumKick

KR = "角色其他对象数据异常"

if "_HasLoad" not in dir():
	Item_SyncPackItemData = AutoMessage.AllotMessage("Item_SyncPackItemData", "同步背包所有物品数据")
	Item_SyncRoleEquipmentData = AutoMessage.AllotMessage("Item_SyncRoleEquipmentData", "同步角色所有装备数据")
	Item_SyncHeroEquipmentData = AutoMessage.AllotMessage("Item_SyncHeroEquipmentData", "同步英雄所有装备数据")
	Hero_SyncAllData = AutoMessage.AllotMessage("Hero_SyncAllData", "同步所有英雄数据")
	Item_SyncRoleArtifactData = AutoMessage.AllotMessage("Item_SyncRoleArtifactData", "同步角色所有神器数据")
	Item_SyncHeroArtifactData = AutoMessage.AllotMessage("Item_SyncHeroArtifactData", "同步英雄所有神器数据")
	Item_SyncRoleHallowsData = AutoMessage.AllotMessage("Item_SyncRoleHallowsData", "同步角色所有圣器数据")
	Item_SyncHeroHallowsData = AutoMessage.AllotMessage("Item_SyncHeroHallowsData", "同步英雄所有圣器数据")
	Item_SyncRoleFashionData = AutoMessage.AllotMessage("Item_SyncRoleFashionData", "同步角色所有时装数据")
	Item_SyncRoleRingData = AutoMessage.AllotMessage("Item_SyncRoleRingData", "同步角色订婚戒指数据")
	Item_SyncRoleMagicSpiritData = AutoMessage.AllotMessage("Item_SyncRoleMagicSpiritData", "同步角色魔灵数据")
	Item_SyncHeroMagicSpiritData = AutoMessage.AllotMessage("Item_SyncHeroMagicSpiritData", "同步英雄魔灵数据")
	

def OnLoadRoleObj(role, roleobj):
	#从数据库载入OBJ数据列表
	obj_dict = {}
	
	#先把obj列表转换成字典 objId --> obj
	for obj in roleobj:
		obj_dict[obj[0]] = obj
	
	RST = role.SetTempObj
	#先处理英雄
	heroMgr = RoleHeroMgr.RoleHeroMgr(role, obj_dict)
	RST(EnumTempObj.enHeroMgr, heroMgr)
	
	#初始化物品管理器
	
	#全局物品管理
	RST(EnumTempObj.enGlobalItemMgr, {})
	#背包
	RST(EnumTempObj.enPackMgr, PackMgr.PackMgr(role, obj_dict))
	#人物装备
	RST(EnumTempObj.enRoleEquipmentMgr, PackMgr.RoleEquipmentMgr(role, obj_dict))
	#人物神器
	RST(EnumTempObj.enRoleArtifactMgr, PackMgr.RoleArtifactMgr(role, obj_dict))
	#人物圣器
	RST(EnumTempObj.enRoleHallowsMgr, PackMgr.RoleHallowsMgr(role, obj_dict))
	#人物时装
	RST(EnumTempObj.enRoleFashionMgr, PackMgr.RoleFashionMgr(role, obj_dict))
	#订婚戒指
	RST(EnumTempObj.enRoleRingMgr, PackMgr.RingMgr(role, obj_dict))
	#魔灵
	RST(EnumTempObj.enRoleMagicSpiritMgr, PackMgr.RoleMagicSpiritMgr(role, obj_dict))
	
	#英雄装备
	heroEquipmentMgrDict = {}
	#英雄神器
	heroArtifactMgrDict = {}
	#英雄圣器
	heroHallowsMgrDict ={}
	#英雄魔灵
	heroMagicSpiritMgrDict = {}
	for heroId, hero in heroMgr.HeroDict.iteritems():
		heroEquipmentMgrDict[heroId] = hero.equipmentMgr = PackMgr.HeroEquipmentMgr(role, obj_dict, heroId, hero)
		heroArtifactMgrDict[heroId] = hero.ArtifactMgr = PackMgr.HeroArtifactMgr(role, obj_dict, heroId, hero)
		heroHallowsMgrDict[heroId] = hero.HallowsMgr = PackMgr.HeroHallowsMgr(role, obj_dict, heroId, hero)
		heroMagicSpiritMgrDict[heroId] = hero.magicSpiritMgr = PackMgr.HeroMagicSpiritMgr(role, obj_dict, heroId, hero)
		
	RST(EnumTempObj.enHeroEquipmentMgrDict, heroEquipmentMgrDict)
	RST(EnumTempObj.enHeroAtrifactMgrDict, heroArtifactMgrDict)
	RST(EnumTempObj.enHeroHallowsMrgDict, heroHallowsMgrDict)
	RST(EnumTempObj.enHeroMagicSpiritMgrDict, heroMagicSpiritMgrDict)
	#其他分发处理
	
	
	#结束判断字典内数据
	if obj_dict:
		#字典应该没东西了，全都处理了才对
		role.Kick(False, EnumKick.DataError)
		return False
	
	#载入数据完毕调用处理函数
	AfterLoadObj(role)
	return True

def AfterLoadObj(role):
	#分发处理完毕， 统一同步客户端
	RG = role.GetTempObj
	RS = role.SendObj
	#先英雄数据，因为装备上面可能有英雄数据
	heroMgr= RG(EnumTempObj.enHeroMgr)
	RS(Hero_SyncAllData, heroMgr.GetSyncObjDict())

	#获取物品管理器
	packMgr = RG(EnumTempObj.enPackMgr)
	roleEquipmentMgr = RG(EnumTempObj.enRoleEquipmentMgr)
	heroEquipmentMgrDict = RG(EnumTempObj.enHeroEquipmentMgrDict)
	roleArtifactMgr = RG(EnumTempObj.enRoleArtifactMgr)
	heroArtifactMgrDict = RG(EnumTempObj.enHeroAtrifactMgrDict)
	roleHallowsMgr = RG(EnumTempObj.enRoleHallowsMgr)
	heroHallowsMgrDict = RG(EnumTempObj.enHeroHallowsMrgDict)
	
	#玩家时装
	roleFashionMgr = RG(EnumTempObj.enRoleFashionMgr)
	#同步物品数据
	RS(Item_SyncPackItemData, packMgr.GetSyncObjDict())
	RS(Item_SyncRoleEquipmentData, roleEquipmentMgr.GetSyncObjDict())
	RS(Item_SyncRoleArtifactData, roleArtifactMgr.GetSyncObjDict())
	RS(Item_SyncRoleHallowsData, roleHallowsMgr.GetSyncObjDict())
	#同步角色时装数据
	RS(Item_SyncRoleFashionData, roleFashionMgr.GetSyncObjDict())
	#同步订婚戒指
	roleRingMgr = RG(EnumTempObj.enRoleRingMgr)
	RS(Item_SyncRoleRingData, roleRingMgr.GetSyncObjDict())
	#同步魔灵数据
	roleMagicSpiritMgr = RG(EnumTempObj.enRoleMagicSpiritMgr)
	RS(Item_SyncRoleMagicSpiritData, roleMagicSpiritMgr.GetSyncObjDict())
	
	for heroId, heroEquipmentMgr in heroEquipmentMgrDict.iteritems():
		RS(Item_SyncHeroEquipmentData,(heroId, heroEquipmentMgr.GetSyncObjDict(),))
	for heroId, heroArtifactMgr in heroArtifactMgrDict.iteritems():
		RS(Item_SyncHeroArtifactData,(heroId, heroArtifactMgr.GetSyncObjDict(),))	
	for heroId, heroHallowsMgr in heroHallowsMgrDict.iteritems():
		RS(Item_SyncHeroHallowsData,(heroId, heroHallowsMgr.GetSyncObjDict(),))
	
	#英雄魔灵	
	heroMagicSpiritMgrDict = RG(EnumTempObj.enHeroMagicSpiritMgrDict)	
	for heroId, heroMagicSpiritMgr in heroMagicSpiritMgrDict.iteritems():
		RS(Item_SyncHeroMagicSpiritData,(heroId, heroMagicSpiritMgr.GetSyncObjDict(),))

def GetRoleObj(role):
	#获取角色Obj,保存到数据库
	roleobj = []
	#物品obj管理器
	RG = role.GetTempObj
	packMgr = RG(EnumTempObj.enPackMgr)
	roleEquipmentMgr = RG(EnumTempObj.enRoleEquipmentMgr)
	herpEquipmentMgrDict = RG(EnumTempObj.enHeroEquipmentMgrDict)
	roleArtifactMgr = RG(EnumTempObj.enRoleArtifactMgr)
	heroArtifactMgrDict = RG(EnumTempObj.enHeroAtrifactMgrDict)
	roleHallowsMgr = RG(EnumTempObj.enRoleHallowsMgr)
	heroHallowsMgrDict = RG(EnumTempObj.enHeroHallowsMrgDict)
	#获取玩家时装obj
	roleFashionMgr = RG(EnumTempObj.enRoleFashionMgr)
	#英雄Obj
	heroMgr = RG(EnumTempObj.enHeroMgr)
	#订婚戒指
	ringMgr = RG(EnumTempObj.enRoleRingMgr)
	#魔灵
	magicSpiritMgr = RG(EnumTempObj.enRoleMagicSpiritMgr)
	heroMagicSpiritMgrDict = RG(EnumTempObj.enHeroMagicSpiritMgrDict)
	
	RE = roleobj.extend
	RE(packMgr.GetDBObjList())
	RE(roleEquipmentMgr.GetDBObjList())
	RE(roleArtifactMgr.GetDBObjList())
	RE(roleHallowsMgr.GetDBObjList())
	RE(roleFashionMgr.GetDBObjList())
	RE(ringMgr.GetDBObjList())
	RE(magicSpiritMgr.GetDBObjList())
	
	for herpEquipmentMgr in herpEquipmentMgrDict.itervalues():
		RE(herpEquipmentMgr.GetDBObjList())
	
	for herpArtifactMgr in heroArtifactMgrDict.itervalues():
		RE(herpArtifactMgr.GetDBObjList())
	
	for heroHallowsMgr in heroHallowsMgrDict.itervalues():
		RE(heroHallowsMgr.GetDBObjList())
	
	for heroMagicSpiritMgr in heroMagicSpiritMgrDict.itervalues():
		RE(heroMagicSpiritMgr.GetDBObjList())
	
	RE(heroMgr.GetDBObjList())
	return roleobj
