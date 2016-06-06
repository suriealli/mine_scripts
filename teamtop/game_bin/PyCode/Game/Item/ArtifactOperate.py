#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Item.ArtifactOperate")
#===============================================================================
# 神器穿戴相关
#===============================================================================
import cRoleMgr
import Game.Item.ArtifactCuiLian as ArtifactCuiLian
from Common.Message import AutoMessage
from Game.Role.Data import EnumTempObj, EnumObj
from Game.Item import ItemMsg
from Game.Role.Obj import Base

if "_HasLoad" not in dir():
	#消息
	Artifact_RolePutOn_OK = AutoMessage.AllotMessage("Artifact_RolePutOn_OK", "角色成功穿上一件神器")
	Artifact_HeroPutOn_OK = AutoMessage.AllotMessage("Artifact_HeroPutOn_OK", "英雄成功穿上一件神器")

def InsertEquipment(mgr, prop):
	#管理器增加神器操作
	mgr.objIdDict[prop.oid] = prop
	prop.package = mgr
	
	cd_dict = mgr.codingGather.get(prop.otype)
	if not cd_dict:
		mgr.codingGather[prop.otype] = cd_dict = {}
	cd_dict[prop.oid] = prop
	
	
def RemoveEquipment(mgr, prop):
	#清除该装备淬炼组合属性
	prop.ClearCuiLianSuite()
	#管理器移除神器操作
	del mgr.objIdDict[prop.oid]
	prop.package = None
	
	cd_dict = mgr.codingGather.get(prop.otype)
	del cd_dict[prop.oid]
	if not cd_dict:
		del mgr.codingGather[prop.otype]

##########################################################################################
def OnPutOnRoleArtifact(role, msg):
	'''
	角色穿神器
	@param role:
	@param msg:神器ID
	'''
	eId = msg
	packMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	#一定要在背包查找这个神器
	Artifact= packMgr.FindProp(eId)
	if not Artifact : return
	
	if Artifact.Obj_Type != Base.Obj_Type_Artifact:
		#竟然不是神器?
		return
	if Artifact.cfg.needlevel > role.GetLevel():
		#等级不足
		return
	#这件神器需要放置的位置
	posType = Artifact.cfg.posType
	if posType < 0 or posType > 8:
		print "GE_EXC, OnPutOnRoleArtifact error pos (%s)" % posType
		return
	
	packIdSet = role.GetObj(EnumObj.En_PackageItems)
	ArtifactIdSet = role.GetObj(EnumObj.En_RoleArtifact)
	roleArtifactMgr = role.GetTempObj(EnumTempObj.enRoleArtifactMgr)
	#看看原来的位置是否已经佩戴了一件神器
	Artifact_2 = None
	for eq in roleArtifactMgr.objIdDict.values():
		if eq.cfg.posType == posType:
			Artifact_2 = eq
			break
	
	if Artifact_2:
		#交换两件神器
		#清理两个背包中的相关数据
		RemoveEquipment(roleArtifactMgr, Artifact_2)
		RemoveEquipment(packMgr, Artifact)
		#清理角色OBJ记录
		packIdSet.discard(eId)
		ArtifactIdSet.discard(Artifact_2.oid)
		#清理拥有者
		Artifact_2.owner = None
		
		#重新写入交换后的数据
		InsertEquipment(roleArtifactMgr, Artifact)
		InsertEquipment(packMgr, Artifact_2)
		#重新写入角色OBJ记录
		ArtifactIdSet.add(eId)
		packIdSet.add(Artifact_2.oid)
		##拥有者拥有者
		Artifact.owner = role
		
		if Artifact.cfg.suitId and Artifact.cfg.suitId != Artifact_2.cfg.suitId:
			#触发重置套装属性
			roleArtifactMgr.ResetSuit()
			role.GetPropertyGather().ReSetRecountArtifactSuitFlag()
		
		#同步客户端，身上的神器脱到背包
		role.SendObj(ItemMsg.Item_SyncItem_Package, Artifact_2.oid)
	else:
		#直接穿上去
		#清理背包管理器
		RemoveEquipment(packMgr, Artifact)
		#清理人物数组数据
		packIdSet.discard(eId)
		
		#更新角色神器管理器数据
		InsertEquipment(roleArtifactMgr, Artifact)
		#拥有者
		Artifact.owner = role
		#人物数组数据
		ArtifactIdSet.add(eId)
		
		if Artifact.cfg.suitId:
			#重置套装属性
			roleArtifactMgr.ResetSuit()
			role.GetPropertyGather().ReSetRecountArtifactSuitFlag()
	#同步穿神器成功
	role.SendObj(Artifact_RolePutOn_OK, eId)
	if posType <= 6:
		#重算神器属性Flag
		role.GetPropertyGather().ReSetRecountArtifactFlag()
	
	#重算淬炼组合
	ArtifactCuiLian.ArtifactCuiLianSuite(role, role)

def OnTakeOffRoleArtifact(role, msg):
	'''
	角色脱神器
	@param role:
	@param msg:神器ID
	'''
	
	eId = msg
	if role.PackageIsFull():
		return
	roleArtifactMgr = role.GetTempObj(EnumTempObj.enRoleArtifactMgr)
	Artifact = roleArtifactMgr.FindProp(eId)
	if not Artifact:return
	
	ArtifactIdSet = role.GetObj(EnumObj.En_RoleArtifact)
	if eId not in ArtifactIdSet:
		return
	
	#数组数据
	packIdSet = role.GetObj(EnumObj.En_PackageItems)
	
	ArtifactIdSet.discard(eId)
	RemoveEquipment(roleArtifactMgr, Artifact)
	Artifact.owner = None
	
	packIdSet.add(eId)
	InsertEquipment(role.GetTempObj(EnumTempObj.enPackMgr), Artifact)
	
	posType = Artifact.cfg.posType
	if Artifact.cfg.suitId:
		#重置套装属性
		roleArtifactMgr.ResetSuit()
		role.GetPropertyGather().ReSetRecountArtifactSuitFlag()
		
	if posType <= 6:
		#重算属性Flag
		role.GetPropertyGather().ReSetRecountArtifactFlag()
	#同步客户端
	#身上的神器脱到背包
	role.SendObj(ItemMsg.Item_SyncItem_Package, eId)
	
	#重算淬炼组合
	ArtifactCuiLian.ArtifactCuiLianSuite(role, role)

def OnPutOnHeroArtifact(role, msg):
	'''
	英雄穿神器
	@param role:
	@param msg:(英雄ID, 神器ID)
	'''
	
	heroId, eId = msg
	hero = role.GetHero(heroId)
	if not hero : return
	if not hero.GetStationID():
		return
	heroArtifactMgr = hero.ArtifactMgr
	if not heroArtifactMgr : return
	
	packMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	Artifact= packMgr.FindProp(eId)
	if not Artifact : return
	
	if Artifact.Obj_Type != Base.Obj_Type_Artifact:
		return
	if Artifact.cfg.needlevel > hero.GetLevel():
		#等级
		return
	#这件神器需要放置的位置
	posType = Artifact.cfg.posType
	if posType < 0 or posType > 6:
		return
	
	packIdSet = role.GetObj(EnumObj.En_PackageItems)
	ArtifactIdSet = role.GetObj(EnumObj.En_HeroArtifact).get(heroId)
	
	##看看原来的位置是否已经佩戴了一件神器
	Artifact_2 = None
	for eq in heroArtifactMgr.objIdDict.values():
		if eq.cfg.posType == posType:
			Artifact_2 = eq
			break
	
	if Artifact_2:
		#交换两件神器
		packIdSet.discard(eId)
		ArtifactIdSet.discard(Artifact_2.oid)
		
		RemoveEquipment(heroArtifactMgr, Artifact_2)
		RemoveEquipment(packMgr, Artifact)
		
		Artifact_2.owner = None
		
		InsertEquipment(heroArtifactMgr, Artifact)
		InsertEquipment(packMgr, Artifact_2)
		
		ArtifactIdSet.add(eId)
		packIdSet.add(Artifact_2.oid)
		#更新拥有者
		Artifact.owner = hero
		
		if Artifact.cfg.suitId and Artifact.cfg.suitId != Artifact_2.cfg.suitId:
			#重置套装属性
			heroArtifactMgr.ResetSuit()
			hero.GetPropertyGather().ReSetRecountArtifactSuitFlag()
		#身上的神器脱到背包
		role.SendObj(ItemMsg.Item_SyncItem_Package, Artifact_2.oid)
	else:
		#直接穿上去
		RemoveEquipment(packMgr, Artifact)
		#删除人物数组数据
		packIdSet.discard(eId)
		
		InsertEquipment(heroArtifactMgr, Artifact)
		ArtifactIdSet.add(eId)
		#拥有者
		Artifact.owner = hero
		
		if Artifact.cfg.suitId:
			#重置套装属性
			heroArtifactMgr.ResetSuit()
			hero.GetPropertyGather().ReSetRecountArtifactSuitFlag()
	#重算属性Flag
	hero.propertyGather.ReSetRecountArtifactFlag()
	role.SendObj(Artifact_HeroPutOn_OK, (heroId, eId))
	
	#重算淬炼组合
	ArtifactCuiLian.ArtifactCuiLianSuite(role, hero)
	
def OnTakeOffHeroArtifact(role, msg):
	'''
	英雄脱神器
	@param role:
	@param msg:(英雄ID, 神器ID)
	'''
	heroId, eId = msg
	if role.PackageIsFull() : return
	
	hero = role.GetHero(heroId)
	if not hero:return
	
	heroArtifactMgr = hero.ArtifactMgr
	if not heroArtifactMgr:return
	
	Artifact = heroArtifactMgr.FindProp(eId)
	if not Artifact:return
	
	ArtifactIdSet = role.GetObj(EnumObj.En_HeroArtifact).get(heroId)
	if eId not in ArtifactIdSet : return
	
	packIdSet = role.GetObj(EnumObj.En_PackageItems)
	
	ArtifactIdSet.discard(eId)
	Artifact.owner = None
	RemoveEquipment(heroArtifactMgr, Artifact)
	
	InsertEquipment(role.GetTempObj(EnumTempObj.enPackMgr), Artifact)
	packIdSet.add(eId)
	if Artifact.cfg.suitId:
		#重置套装属性
		heroArtifactMgr.ResetSuit()
		hero.GetPropertyGather().ReSetRecountArtifactSuitFlag()
	#重算属性Flag
	hero.propertyGather.ReSetRecountArtifactFlag()
	
	#同步客户端身上的神器脱到背包
	role.SendObj(ItemMsg.Item_SyncItem_Package, eId)
	
	#重算淬炼组合
	ArtifactCuiLian.ArtifactCuiLianSuite(role, hero)
	
if "_HasLoad" not in dir():
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Artifact_RolePutOn", "角色穿上神器"), OnPutOnRoleArtifact)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Artifact_RoleTakeOff", "角色脱下神器"), OnTakeOffRoleArtifact)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Artifact_HeroPutOn", "英雄穿上神器"), OnPutOnHeroArtifact)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Artifact_HeroTakeOff", "英雄脱下神器"), OnTakeOffHeroArtifact)
	
