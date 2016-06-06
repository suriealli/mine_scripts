#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fashion.FashionOperate")
#===============================================================================
# 时装穿戴
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Role.Data import EnumTempObj, EnumObj, EnumInt1, EnumTempInt64, EnumInt8
from Game.Role import Event
from Game.Item import ItemMsg, ItemConfig
from Game.Role.Obj import Base
from Game.Fashion import FashionBase
from Game.Fashion import FashionForing

if "_HasLoad" not in dir():
	Fashion_RolePutOn_OK = AutoMessage.AllotMessage("Fashion_RolePutOn_OK", "角色成功穿上一件时装")

def InsertFashion(mgr, prop):
	#管理器增加时装操作
	mgr.objIdDict[prop.oid] = prop
	prop.package = mgr
	
	cd_dict = mgr.codingGather.get(prop.otype)
	if not cd_dict:
		mgr.codingGather[prop.otype] = cd_dict = {}
	cd_dict[prop.oid] = prop
		
	
def RemoveFashion(mgr, prop):
	#管理器移除时装操作
	del mgr.objIdDict[prop.oid]
	prop.package = None
	
	cd_dict = mgr.codingGather.get(prop.otype)
	del cd_dict[prop.oid]
	if not cd_dict:
		del mgr.codingGather[prop.otype]

##########################################################################################

def OnPutOnRoleFashion(role, msg):
	'''
	角色穿时装
	@param role:
	@param msg:时装ID
	'''
	return#屏蔽角色穿时装
	eId = msg
	#等级不足
	packMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	#一定要在背包查找这个时装
	Fashion= packMgr.FindProp(eId)
	if not Fashion : return
	
	if Fashion.Obj_Type != Base.Obj_Type_Fashion:
		#不是时装
		return
	if Fashion.cfg.needlevel > role.GetLevel():
		#等级不足
		return
	#这件时装需要放置的位置
	posType = Fashion.cfg.posType
	if posType < 0 or posType > 4:
		print "GE_EXC, OnPutOnRoleFashion error pos (%s)" % posType
		return
	
	packIdSet = role.GetObj(EnumObj.En_PackageItems)
	FashionIdSet = role.GetObj(EnumObj.En_RoleFashions)
	roleFashionMgr = role.GetTempObj(EnumTempObj.enRoleFashionMgr)
	#看看原来的位置是否已经佩戴了一件时装
	Fashion_2 = None
	for eq in roleFashionMgr.objIdDict.values():
		if eq.cfg.posType == posType:
			Fashion_2 = eq
			break
	
	if Fashion_2:
		#交换两件时装
		#清理两个背包中的相关数据
		RemoveFashion(roleFashionMgr, Fashion_2)
		RemoveFashion(packMgr, Fashion)
		#清理角色OBJ记录
		packIdSet.discard(eId)
		FashionIdSet.discard(Fashion_2.oid)
		#清理拥有者
		Fashion_2.owner = None
		
		#重新写入交换后的数据
		InsertFashion(roleFashionMgr, Fashion)
		InsertFashion(packMgr, Fashion_2)
		#重新写入角色OBJ记录
		FashionIdSet.add(eId)
		packIdSet.add(Fashion_2.oid)
		##拥有者拥有者
		Fashion.owner = role
		
		#同步客户端，身上的时装脱到背包
		role.SendObj(ItemMsg.Item_SyncItem_Package, Fashion_2.oid)
	else:
		#直接穿上去
		#清理背包管理器
		RemoveFashion(packMgr, Fashion)
		#清理人物数组数据
		packIdSet.discard(eId)
		
		#更新角色时装管理器数据
		InsertFashion(roleFashionMgr, Fashion)
		#拥有者
		Fashion.owner = role
		#人物数组数据
		FashionIdSet.add(eId)
	#激活该时装
	FashionForing.ActiveFashion(role, Fashion.cfg.coding)
	if Fashion.cfg.posType == 4:#羽翼,激活羽翼系统相关的
		FashionForing.ActiveWingSys(role, Fashion.cfg.coding)
	#同步穿时装成功
	role.SendObj(Fashion_RolePutOn_OK, eId)
	if posType <= 4:
		#重算时装属性Flag
		role.GetPropertyGather().ReSetRecountFashionFlag()
	#重算光环属性
	role.GetPropertyGather().ReSetRecpintFashionHoleFlag()
	
	#时装外形改变
#	AfterChangeFashion(role, posType, Fashion.cfg.coding)

	#触发 情人目标-穿戴亲密恋人衣服
	if Fashion.cfg.coding == EnumGameConfig.QinmiLover_Coding:
		Event.TriggerEvent(Event.Eve_TryCouplesGoal, role, (EnumGameConfig.GoalType_ClothesEquip, 1))
	
def OnTakeOffRoleFashion(role, msg):
	'''
	角色脱时装
	@param role:
	@param msg:时装ID
	'''
	return #屏蔽角色脱时装
	eId = msg
	#等级不足
	if role.GetLevel() < EnumGameConfig.ACTIVE_FASHION_LEVEL:
		return
	
	if role.PackageIsFull():#背包已满
		return
	roleFashionMgr = role.GetTempObj(EnumTempObj.enRoleFashionMgr)
	Fashion = roleFashionMgr.FindProp(eId)
	if not Fashion:return#时装不存在
	
	if Fashion.Obj_Type != Base.Obj_Type_Fashion:
		#不是时装
		return
	
	FashionIdSet = role.GetObj(EnumObj.En_RoleFashions)
	if eId not in FashionIdSet:#装备Id不在已装备集合
		return
	
	#数组数据
	packIdSet = role.GetObj(EnumObj.En_PackageItems)
	
	FashionIdSet.discard(eId)
	RemoveFashion(roleFashionMgr, Fashion)
	Fashion.owner = None
	
	packIdSet.add(eId)
	InsertFashion(role.GetTempObj(EnumTempObj.enPackMgr), Fashion)
	
	posType = Fashion.cfg.posType
	if posType <= 4:
		#重算属性Flag
		role.GetPropertyGather().ReSetRecountFashionFlag()
	#重算光环属性
	role.GetPropertyGather().ReSetRecpintFashionHoleFlag()
	#时装外形改变
#	AfterChangeFashion(role, Fashion.cfg.posType, Fashion.cfg.coding, True)
	#同步客户端
	#身上的时装脱到背包
	role.SendObj(ItemMsg.Item_SyncItem_Package, eId)

def OnCheckFashion(role, param):
	'''
	玩家勾选了显示或关闭时装
	@param role:
	@param param:
	'''
	state = param #0为显示，1为屏蔽
	
	ViewState = role.GetI1(EnumInt1.FashionViewState)
	
	if ViewState == state:
		return
	
	role.SetI1(EnumInt1.FashionViewState, state)

def OnSaveFashion(role, param):
	'''
	玩家保存时装
	@param role:
	@param param:
	'''
	apedata = param

	#发的格式有问题
	if type(apedata) != dict:
		return
	FashionGlobalMgr = role.GetTempObj(EnumTempObj.enRoleFashionGlobalMgr)
	FashionApeData = role.GetObj(EnumObj.SaveFashionApe)
	for posType, coding in apedata.iteritems():
		if coding != 0 and coding not in FashionGlobalMgr.fashion_active_dict:#该时装未激活
			continue
		FashionApeData[posType] = coding
		AfterChangeFashion(role, posType, coding)
		#触发 情人目标-穿戴亲密恋人衣服
		if coding == EnumGameConfig.QinmiLover_Coding:
			Event.TriggerEvent(Event.Eve_TryCouplesGoal, role, (EnumGameConfig.GoalType_ClothesEquip, 1))
		
	role.Msg(2, 0, GlobalPrompt.FASHION_SAVE_SUC)
	
def AfterChangeFashion(role, posType, coding, putoff = False):
	if posType == 1:#为时装武器
		if putoff:
			role.SetTI64(EnumTempInt64.FashionWeapons, 0)
		else:
			role.SetTI64(EnumTempInt64.FashionWeapons, coding)
	elif posType == 2:#时装衣服
		if putoff:
			role.SetTI64(EnumTempInt64.FashionClothes, 0)
		else:
			role.SetTI64(EnumTempInt64.FashionClothes, coding)
	elif posType == 3:#时装帽子
		if putoff:
			role.SetTI64(EnumTempInt64.FashionHat, 0)
		else:
			role.SetTI64(EnumTempInt64.FashionHat, coding)
	elif posType == 4:#为时装翅膀
		if coding == 0:
			role.SetI8(EnumInt8.WingId, 0)
		else:
			#翅膀还是根据羽翼系统的显示规则
			cfg = ItemConfig.ItemCfg_Dict.get(coding)
			if not cfg:
				return
			role.SetI8(EnumInt8.WingId, cfg.wingId)
		
def InitRolePyObj(role, param):
	role.SetTempObj(EnumTempObj.enRoleFashionGlobalMgr, FashionBase.FashionMgr(role))
	#初始化时装外观
	FashionApeData = role.GetObj(EnumObj.SaveFashionApe)
	for posType, coding in FashionApeData.iteritems():
		if posType and coding:
			AfterChangeFashion(role, posType, coding)

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_InitRolePyObj, InitRolePyObj)
		
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Fashion_Puton", "玩家穿时装"), OnPutOnRoleFashion)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Fashion_Putoff", "玩家脱时装"), OnTakeOffRoleFashion)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Fashion_Check", "玩家勾选了显示或关闭时装"), OnCheckFashion)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Fashion_SaveFashion", "玩家保存时装"), OnSaveFashion)
		
	