#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Union.UnionStore")
#===============================================================================
# 公会商店
#===============================================================================
import cRoleMgr
import Environment
from Game.Role import Event
from Game.Role.Data import EnumObj
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from Game.Union import UnionDefine, UnionConfig, UnionMgr


if "_HasLoad" not in dir():
	
	#消息
	Sync_UnionStoreNormalGoods = AutoMessage.AllotMessage("Sync_UnionStoreNormalGoods", "同步公会商店普通商品的购买次数")
	Sync_UnionStoreShouGoods = AutoMessage.AllotMessage("Sync_UnionStoreShouGoods", "同步公会商店 神兽掉落商品的剩余个数")
	
	#日志
	TraRoleBuyNormalGood_UnionStore = AutoLog.AutoTransaction("TraRoleBuyNormalGood_UnionStore", "角色购买公会商店普通商品")
	TraRoleBuyShenShouGood_UnionStore = AutoLog.AutoTransaction("TraRoleBuyShenShouGood_UnionStore", "角色购买公会商店神兽掉落商品")
	
	
#===============================================================================
#基本操作
#===============================================================================

def GetActiveGoodId(unionObj):
	'''
	公会商店获取已经激活的商品id
	'''
	otherData = unionObj.other_data
	return otherData.setdefault(UnionDefine.O_StoreGoods, set())


def IsActiveGood(unionObj, goodId):
	'''
	某样商品是否已经激活
	'''
	goodSet = GetActiveGoodId(unionObj)
	if goodId in goodSet:
		return True
	return False


def EnableGoodId(unionObj, goodId):
	'''
	激活某个商品 
	'''
	if goodId not in UnionConfig.UnionGoodConfigDict:
		return
	goodSet = GetActiveGoodId(unionObj)
	goodSet.add(goodId)
	unionObj.HasChange()
	

def DisableGoodId(unionObj, goodId):
	'''
	反激活某个商品
	'''
	goodSet = GetActiveGoodId(unionObj)
	goodSet.discard(goodId)	
	unionObj.HasChange()


def GetShenShouGoodId(unionObj):
	'''
	获取神兽掉落的所有商品id和数量
	'''
	otherData = unionObj.other_data
	return otherData.get(UnionDefine.O_ShenShouGoods, {})


def SetShenShouGoodId(unionObj, goodDict):
	'''
	设置神兽掉落商品字典
	'''
	otherData = unionObj.other_data
	otherData[UnionDefine.O_ShenShouGoods] = goodDict


def GetShenShouGoodLeftCnt(unionObj, goodId):
	'''
	获取神兽掉落商品的剩余数量
	'''
	otherData = unionObj.other_data
	goodDict = otherData.get(UnionDefine.O_ShenShouGoods, {})
	return goodDict.get(goodId, 0)


def SetShenShouGoodLeftCnt(unionObj, goodId, value):
	'''
	设置神兽掉落某样商品的剩余数量
	'''
	if value < 0:
		return
	otherData = unionObj.other_data
	goodDict = otherData.setdefault(UnionDefine.O_ShenShouGoods, {})
	goodDict[goodId] = value
	unionObj.HasChange()


#===============================================================================
#客户端请求
#===============================================================================
def RequestActiveNormalGood(role, msg):
	'''
	客户端请求激活商品
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	goodId = msg
	roleID = role.GetRoleID()
	roleJob = unionObj.GetMemberJob(roleID)
	
	jobConfig = UnionConfig.UNION_JOB.get(roleJob)
	
	if jobConfig is None:
		return
	
	if not jobConfig.goodActivate:
		return
	
	if IsActiveGood(unionObj, goodId):
		return
	config = UnionConfig.UnionGoodConfigDict.get(goodId)
	if config is None:
		return
	
	if unionObj.level < config.needStoreLevel:
		return
	if unionObj.resource < config.needUnionResorce:
		return
	unionObj.DecUnionResource(config.needUnionResorce)
	EnableGoodId(unionObj, goodId)
	
	normalGoods = GetActiveGoodId(unionObj)
	roleNormalGoods = role.GetObj(EnumObj.Union).setdefault(2, {})
	role.SendObj(Sync_UnionStoreNormalGoods, (normalGoods, roleNormalGoods))
	role.Msg(2, 0, GlobalPrompt.UnionStoreActiveGoodOkay)
	UnionMgr.UnionMsg(unionObj, GlobalPrompt.UnionStoreActiveGoodOkayAll % config.item)
	
def RequestBuyNormalGood(role, msg):
	'''
	客户端请求购买由工会大佬激活的普通商品
	'''	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	goodId = msg
	if not IsActiveGood(unionObj, goodId):
		return
	
	
	config = UnionConfig.UnionGoodConfigDict.get(goodId)
	if config is None:
		return
	
	#超出每日限购的数量，如果为0的话表示不限购
	roleNormalGoods = role.GetObj(EnumObj.Union).setdefault(2, {})
	if config.dailyLimitCnt > 0:
		if roleNormalGoods.get(goodId, 0) >= config.dailyLimitCnt:
			return
	
	if role.GetContribution() < config.costContribution:
		return
	
	if role.GetUnbindRMB() < config.costUnbindRMB:
		return
	
	with TraRoleBuyNormalGood_UnionStore:
		role.DecUnbindRMB(config.costUnbindRMB)
		role.DecContribution(config.costContribution)
		roleNormalGoods[goodId] = roleNormalGoods.get(goodId, 0) + 1
		role.AddItem(*config.item)
	
	
	normalGoods = GetActiveGoodId(unionObj)
	roleNormalGoods = role.GetObj(EnumObj.Union).setdefault(2, {})
	role.SendObj(Sync_UnionStoreNormalGoods, (normalGoods, roleNormalGoods))
	
	role.Msg(2, 0, GlobalPrompt.UnionGoodBuyOkay)

	

def RequestBuyShenshouGood(role, msg):
	'''
	客户端请求购买神兽掉落商品
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	goodId = msg
	leftCnt = GetShenShouGoodLeftCnt(unionObj, goodId)
	if leftCnt <= 0:
		role.Msg(2, 0, GlobalPrompt.UnionGoodNoLeft)
		return
	config = UnionConfig.UnionShenShouGoodDict.get(goodId)
	if not config:
		return
	
	roleShenShouGoods = role.GetObj(EnumObj.Union).setdefault(3, {})
	buyCnt = roleShenShouGoods.get(goodId, 0)
	if config.dailyLimitCnt > 0:
		if buyCnt >= config.dailyLimitCnt:
			return
		
	if role.GetUnbindRMB() < config.costUnbindRMB:
		return
	if role.GetContribution() < config.costContribution:
		return
	
	with TraRoleBuyShenShouGood_UnionStore:
		role.DecUnbindRMB(config.costUnbindRMB)
		role.DecContribution(config.costContribution)
		role.AddItem(*config.item)
		roleShenShouGoods[goodId] = roleShenShouGoods.get(goodId, 0) + 1

		
	shenShouGoods = GetShenShouGoodId(unionObj)
	SetShenShouGoodLeftCnt(unionObj, goodId, leftCnt - 1)
	for roleId in unionObj.members.iterkeys():
		the_role = cRoleMgr.FindRoleByRoleID(roleId)
		if the_role is None:
			continue
		roleShenShouGoods = the_role.GetObj(EnumObj.Union).setdefault(3, {})
		the_role.SendObj(Sync_UnionStoreShouGoods, (shenShouGoods, roleShenShouGoods))
	
	role.Msg(2, 0, GlobalPrompt.UnionGoodBuyOkay)
	
	
def RequestGoods(role, msg):
	'''
	客户端请求获取商店的的商品数据
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	normalGoods = GetActiveGoodId(unionObj)
	shenShouGoods = GetShenShouGoodId(unionObj)
	roleNormalGoods = role.GetObj(EnumObj.Union).setdefault(2, {})
	roleShenShouGoods = role.GetObj(EnumObj.Union).setdefault(3, {})
	role.SendObj(Sync_UnionStoreShouGoods, (shenShouGoods, roleShenShouGoods))
	role.SendObj(Sync_UnionStoreNormalGoods, (normalGoods, roleNormalGoods))
	

def DayClear(role, param):
	'''
	每日清理
	'''
	roleNormalGoods = role.GetObj(EnumObj.Union).setdefault(2, {})
	roleShenShouGoods = role.GetObj(EnumObj.Union).setdefault(3, {})
	roleNormalGoods.clear()
	roleShenShouGoods.clear()


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_RoleDayClear, DayClear)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestGoods_UnionStore", "客户端请求获取商店商品数据"), RequestGoods)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestActiveNormalGood_UnionStore", "客户端请求激活商品"), RequestActiveNormalGood)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestBuyNormalGood_UnionStore", "客户端请求购买由工会大佬激活的普通商品"), RequestBuyNormalGood)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestBuyShenshouGood_UnionStore", "客户端请求购买神兽掉落商品"), RequestBuyShenshouGood)

