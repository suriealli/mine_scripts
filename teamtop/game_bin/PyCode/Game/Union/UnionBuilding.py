#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Union.UnionBuilding")
#===============================================================================
# 公会建筑
#===============================================================================
import cRoleMgr
import Environment
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from Game.Union import UnionDefine, UnionConfig, UnionMgr


if "_HasLoad" not in dir():
	
	SyncUnionBuildingLevel_MaigicTower = AutoMessage.AllotMessage("SyncUnionBuildingLevel_MaigicTower", "同步公会魔法塔等级")
	SyncUnionBuildingLevel_ShenShouTan = AutoMessage.AllotMessage("SyncUnionBuildingLevel_ShenShouTan", "同步公会神兽坛等级")
	SyncUnionBuildingLevel_Store = AutoMessage.AllotMessage("SyncUnionBuildingLevel_Store", "同步公会商店等级")
	
	
	
	#日志
	TraUnionMagicTowerUpLevel = AutoLog.AutoTransaction("TraUnionMagicTowerUpLevel", "公会建筑魔法塔升级")
	TraUnionShenshouTanUpLevel = AutoLog.AutoTransaction("TraUnionShenshouTanUpLevel", "公会建筑神兽坛升级")
	TraUnionStoreUpLevel = AutoLog.AutoTransaction("TraUnionStoreUpLevel", "公会建筑商店升级")
	

def GetMaigicTowerLevel(unionObj):
	'''
	获取魔法塔等级
	'''
	otherData = unionObj.other_data.setdefault(UnionDefine.O_Building, {})
	return otherData.get(UnionDefine.BuildingT_MagicTower, 0)
	
	
def GetShenShouTanLevel(unionObj):
	'''
	获取神兽坛等级
	'''
	otherData = unionObj.other_data.setdefault(UnionDefine.O_Building, {})
	return otherData.get(UnionDefine.BuildingT_ShenShouTan, 0)


def GetStoreLevel(unionObj):
	'''
	获取公会商店等级
	'''
	otherData = unionObj.other_data.setdefault(UnionDefine.O_Building, {})
	return otherData.get(UnionDefine.BuildingT_Store, 0)


def SetMaigicTowerLevel(unionObj, value):
	'''
	设置魔法塔等级
	'''
	if value <= 0:
		return
	otherData = unionObj.other_data.setdefault(UnionDefine.O_Building, {})
	otherData[UnionDefine.BuildingT_MagicTower] = value
	
	
def SetShenShouTanLevel(unionObj, value):
	'''
	设置神兽坛等级
	'''
	if value <= 0:
		return
	otherData = unionObj.other_data.setdefault(UnionDefine.O_Building, {})
	otherData[UnionDefine.BuildingT_ShenShouTan] = value


def SetStoreLevel(unionObj, value):
	'''
	设置公会商店等级
	'''
	if value <= 0:
		return
	otherData = unionObj.other_data.setdefault(UnionDefine.O_Building, {})
	otherData[UnionDefine.BuildingT_Store] = value


def RequestMagicTowerUpLevel(role, unionObj):
	'''
	客户端请求魔法塔升级
	'''
	nowLevel = GetMaigicTowerLevel(unionObj)
	newLevel = nowLevel + 1
	if newLevel not in UnionConfig.UnionMagicTowerDict:
		return
	config = UnionConfig.UnionMagicTowerDict.get(nowLevel, None)
	if not config:
		return
	oldResource = unionObj.resource
	if oldResource < config.needUnionResorce:
		return
	
	with TraUnionMagicTowerUpLevel:
		unionObj.DecUnionResource(config.needUnionResorce)
		roleId = role.GetRoleID()
		AutoLog.LogBase(roleId, AutoLog.eveChangeUnionResource, (unionObj.union_id, oldResource, unionObj.resource))

	SetMaigicTowerLevel(unionObj, newLevel)
	role.SendObj(SyncUnionBuildingLevel_MaigicTower, GetMaigicTowerLevel(unionObj))
	
	role.Msg(2, 0, GlobalPrompt.UnionBuildingLevelUp)
	UnionMgr.UnionMsg(unionObj, GlobalPrompt.UnionBuildingLevelUpAll % (GlobalPrompt.UnionMagicTower, newLevel))


def RequestShenShouTanUpLevel(role, unionObj):
	'''
	请求神兽坛升级
	'''
	nowLevel = GetShenShouTanLevel(unionObj)
	newLevel = nowLevel + 1
	if newLevel not in UnionConfig.UnionShenShouTanDict:
		return
	config = UnionConfig.UnionShenShouTanDict.get(nowLevel, None)
	if not config:
		return
	oldResource = unionObj.resource
	if oldResource < config.needUnionResorce:
		return
	with TraUnionShenshouTanUpLevel:
		unionObj.DecUnionResource(config.needUnionResorce)
		roleId = role.GetRoleID()
		AutoLog.LogBase(roleId, AutoLog.eveChangeUnionResource, (unionObj.union_id, oldResource, unionObj.resource))
	SetShenShouTanLevel(unionObj, newLevel)
	role.SendObj(SyncUnionBuildingLevel_ShenShouTan, GetShenShouTanLevel(unionObj))
	role.Msg(2, 0, GlobalPrompt.UnionBuildingLevelUp)
	UnionMgr.UnionMsg(unionObj, GlobalPrompt.UnionBuildingLevelUpAll % (GlobalPrompt.UnionShenShoutan, newLevel))


def RequestStoreUpLevel(role, unionObj):
	'''
	请求商店升级
	'''
	nowLevel = GetStoreLevel(unionObj)
	newLevel = nowLevel + 1
	if newLevel not in UnionConfig.UnionStoreDict:
		return
	config = UnionConfig.UnionStoreDict.get(nowLevel, None)
	if not config:
		return
	oldResource = unionObj.resource
	if unionObj.resource < config.needUnionResorce:
		return
	with TraUnionStoreUpLevel:
		unionObj.DecUnionResource(config.needUnionResorce)
		roleId = role.GetRoleID()
		AutoLog.LogBase(roleId, AutoLog.eveChangeUnionResource, (unionObj.union_id, oldResource, unionObj.resource))
	SetStoreLevel(unionObj, newLevel)
	role.SendObj(SyncUnionBuildingLevel_Store, GetStoreLevel(unionObj))
	role.Msg(2, 0, GlobalPrompt.UnionBuildingLevelUp)
	UnionMgr.UnionMsg(unionObj, GlobalPrompt.UnionBuildingLevelUpAll % (GlobalPrompt.UnionStore, newLevel))


def RequestUnionBuildingUpLevel(role, msg):
	'''
	客户端请求升级某个公会建筑为
	@param role:
	@param msg:公会建筑物类型
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	roleID = role.GetRoleID()
	roleJob = unionObj.GetMemberJob(roleID)
	jobConfig = UnionConfig.UNION_JOB.get(roleJob)
	
	if jobConfig is None:
		return
	
	if not jobConfig.buildingLevelUp:
		return
	
	buildingType = msg
	fun = BuildingLevelUpFunDict.get(buildingType, None)
	if fun is None:
		return
	fun(role, unionObj)


def RequestGetUnionBuildingLevel(role, msg):
	'''
	客户端请求获取所有公会建筑等级
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	buildingType = msg
	if buildingType == UnionDefine.BuildingT_MagicTower:
		role.SendObj(SyncUnionBuildingLevel_MaigicTower, GetMaigicTowerLevel(unionObj))
		
	elif buildingType == UnionDefine.BuildingT_ShenShouTan:
		role.SendObj(SyncUnionBuildingLevel_ShenShouTan, GetShenShouTanLevel(unionObj))
		
	elif buildingType == UnionDefine.BuildingT_Store:
		role.SendObj(SyncUnionBuildingLevel_Store, GetStoreLevel(unionObj))
	
	role.SendObj(UnionMgr.SyncUnionResource, unionObj.resource)


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		BuildingLevelUpFunDict = {UnionDefine.BuildingT_MagicTower:RequestMagicTowerUpLevel,
								UnionDefine.BuildingT_ShenShouTan:RequestShenShouTanUpLevel,
								UnionDefine.BuildingT_Store:RequestStoreUpLevel}
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestUnionBuildingUpLevel", "客户端请求升级公会建筑"), RequestUnionBuildingUpLevel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestGetUnionBuildingLevel", "客户端请求获取公会建筑等级"), RequestGetUnionBuildingLevel)
