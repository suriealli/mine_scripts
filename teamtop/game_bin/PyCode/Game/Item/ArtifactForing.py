#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Item.ArtifactForing")
#===============================================================================
# 神器强化，进阶，神铸
#===============================================================================
import cRoleMgr
import cProcess
import Environment
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumTempObj
from Game.Role.Obj import Base

if "_HasLoad" not in dir():
	Artifact_Strengthen_Dict = {} #神器强化
	Artifact_Upgrade_Dict = {} #神器进阶
	#消息
	Artifact_UpdateStrengthenLevel = AutoMessage.AllotMessage("Artifact_UpdateStrengthenLevel", "更新神器强化等级")
	Artifact_UpGradeOK = AutoMessage.AllotMessage("Artifact_UpGradeOK", "进阶成功")
	#日志
	TraStrengthenArtifact = AutoLog.AutoTransaction("TraStrengthenArtifact", "强化神器")
	TraUpGradeEquipment_log = AutoLog.AutoTransaction("TraUpGradeEquipment_log", "神器升阶")
	
def OnStrengthenArtifact(role, msg):
	'''
	强化神器
	@param role:
	@param msg:神器ID
	'''
	eId = msg
	globaldict = role.GetTempObj(EnumTempObj.enGlobalItemMgr)
	Artifact = globaldict.get(eId)
	if not Artifact:
		return
	if not Artifact.cfg.Strength:
		return
	oldLevel = Artifact.GetStrengthenLevel()
	if oldLevel >= Artifact.cfg.maxSrength:
		return
	newlevel = oldLevel + 1
	roleLevel = role.GetLevel()
	if newlevel > roleLevel:#强化等级必须小于等于人物等级 
		return
	
	posType = Artifact.cfg.posType
	if posType < 1 or posType > 6:
		#不是神器
		return
	
	key = Artifact.cfg.coding, newlevel
	global Artifact_Strengthen_Dict
	cfg = Artifact_Strengthen_Dict.get(key)
	if not cfg:
		print "GE_EXC, can not find cfg in Strengthen_Dict, posType(%s),level(%s)" % (posType, newlevel)
		return
	
	if role.ItemCnt(cfg.coding) < cfg.cnt:
		return
	with TraStrengthenArtifact:		
		if role.DelItem(cfg.coding, cfg.cnt) < cfg.cnt:
			return
		Artifact.SetStrengthenLevel(newlevel)
		if Artifact.owner:
			#强化属性字典需要重算属性
			Artifact.ResetStrengthen()
			#设置神器属性重算
			Artifact.owner.GetPropertyGather().ReSetRecountArtifactStrengthenFlag()
		#同步客户端
		role.SendObj(Artifact_UpdateStrengthenLevel, (eId, newlevel))
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveStrengthenEquipment, (eId, newlevel))
		
def UpGradeArtifact(role, msg):
	'''
	神器升阶
	@param role:
	@param msg:神器ID
	'''
	eId = msg
	globaldict = role.GetTempObj(EnumTempObj.enGlobalItemMgr)
	Artifact = globaldict.get(eId)
	if not Artifact:
		return
	if not Artifact.cfg.UpGrade:
		return
	global Artifact_Upgrade_Dict
	srcType = Artifact.otype
	cfg = Artifact_Upgrade_Dict.get(srcType)
	if not cfg:
		return
	if role.GetLevel() < cfg.needLevel:
		return
	packageMgr = role.GetTempObj(EnumTempObj.enPackMgr)#人物背包管理
	if cfg.cnt1 > 0:
		if packageMgr.ItemCnt(cfg.itemType1) < cfg.cnt1:
			return
	if cfg.cnt2 > 0:
		if packageMgr.ItemCnt(cfg.itemType2) < cfg.cnt2:
			return
	if cfg.cnt3 > 0:
		if packageMgr.ItemCnt(cfg.itemType3) < cfg.cnt3:
			return
	if cfg.cnt4 > 0:
		if packageMgr.ItemCnt(cfg.itemType4) < cfg.cnt4:
			return
	
	desType = cfg.desType #新神器类型
	fun = Base.Obj_Type_Fun.get(desType)
	if not fun:
		print "GE_EXC, UpGradeArtifact can not find fun , coding = (%s)" % desType
		return
	
	with TraUpGradeEquipment_log:
		#扣物品
		if cfg.cnt1 > 0:
			if role.DelItem(cfg.itemType1, cfg.cnt1) < cfg.cnt1:
				return
		if cfg.cnt2 > 0:
			if role.DelItem(cfg.itemType2, cfg.cnt2) < cfg.cnt2:
				return
		if cfg.cnt3 > 0:
			if role.DelItem(cfg.itemType3, cfg.cnt3) < cfg.cnt3:
				return
		if cfg.cnt4 > 0:
			if role.DelItem(cfg.itemType4, cfg.cnt4) < cfg.cnt4:
				return		
		#-----------------------------------------------------------
		owner = Artifact.owner
		owerId = 0
		mgr = Artifact.package
		ArtifactIdSet = None
		if mgr.heroId:
			owerId = mgr.heroId
			ArtifactIdSet = role.GetObj(mgr.ObjEnumIndex).get(owerId)
		else:
			owerId = role.GetRoleID()
			ArtifactIdSet = role.GetObj(mgr.ObjEnumIndex)
		#删除数据
		ArtifactIdSet.discard(eId)
		del mgr.objIdDict[eId]

		Artifact.package = None
		Artifact.owner = None
		cd_dict = mgr.codingGather.get(srcType)
		del cd_dict[eId]
		if not cd_dict:
			del mgr.codingGather[srcType]
		#全局管理器删除记录
		del globaldict[eId]

		#构建数据对象
		newId = cProcess.AllotGUID64()
		obj = newId, desType, 1, {}
		#根据注册函数，数据对象，生成物品对象
		newItem = fun(role, obj)

		newItem.package = mgr
		newItem.AfterCreate()
		if owner:
			newItem.owner = owner
		else:
			newItem.owner = None	
		#角色数组直接更新
		ArtifactIdSet.add(newId)
		#加入内部管理器
		mgr.objIdDict[newId] = newItem
		itemDict = mgr.codingGather.get(desType)
		if not itemDict:
			mgr.codingGather[desType] = itemDict = {}
		itemDict[newId] = newItem	
		#加入全局管理器
		globaldict[newId] = newItem		
		if newItem.cfg.posType <= 6:
			#强化等级保留
			newItem.SetStrengthenLevel(Artifact.GetStrengthenLevel())
			#淬炼等级保留
			newItem.SetCuiLianLevel(Artifact.GetCuiLianLevel())
			newItem.SetCuiLianExp(Artifact.GetCuiLianExp())
			#淬炼套装属性保留
			newItem.SetCuiLianSuite(Artifact.GetCuiLianSuite())
			#保留符石
			newItem.SetArtifactGemList(Artifact.GetArtifactGem())
			if owner:
				#重算属性
				owner.GetPropertyGather().ReSetRecountArtifactFlag()
				#触发套装属性
				if Artifact.cfg.suitId or newItem.cfg.suitId:					
					newItem.package.ResetSuit()
					role.GetPropertyGather().ReSetRecountArtifactSuitFlag()
		#记录日志
		AutoLog.LogObj(role.GetRoleID(), AutoLog.eveUpGradeEquipment, newId, newItem.otype, newItem.oint, newItem.odata, (eId, srcType))
		#同步客户端
		role.SendObj(Artifact_UpGradeOK, (newId, eId, owerId, newItem.GetSyncData(), ))		
		
		#版本判断
		if Environment.EnvIsNA():
			#开服活动
			kaifuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
			kaifuActMgr.get_shenqi(newItem.cfg.coding)
		
if "_HasLoad" not in dir():
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ArtifactForing_OnStrengthen1", "强化神器"), OnStrengthenArtifact)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ArtifactForing_UpGradeEquipment", "请求进阶神器"), UpGradeArtifact)
