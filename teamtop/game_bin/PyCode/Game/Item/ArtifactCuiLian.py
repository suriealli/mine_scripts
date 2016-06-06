#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Item.ArtifactCuiLian")
#===============================================================================
# 神器淬炼		@author: GaoShuai
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumInt32, EnumTempObj, EnumObj, EnumInt8
from Game.Item.ItemConfig import ArtifactCuiLianHalo_Dict, ArtifactCuiLianSuite_Dict, ArtifactCuiLianLevel_Dict, ArtifactCuiLianSuite7_Dict, ArtifactCuiLianIndex_Dict

if "_HasLoad" not in dir():
	#消息
	Artifact_CuiLianSuite = AutoMessage.AllotMessage("Artifact_CuiLianSuite", "神器淬炼组合")
	Artifact_CuiLian_OK = AutoMessage.AllotMessage("Artifact_CuiLian_OK", "神器淬炼成功")
	#日志
	CuiLianStrengthLog = AutoLog.AutoTransaction("ArtifactCuiLianStrength", "神器淬炼光环强化")
	CuiLianLog = AutoLog.AutoTransaction("ArtifactCuiLian", "神器淬炼成功")			#最初版本日志，请保留
	CuiLianLog_1 = AutoLog.AutoTransaction("ArtifactCuiLian_1", "神器淬炼1次成功")
	CuiLianLog_50 = AutoLog.AutoTransaction("ArtifactCuiLian_50", "神器淬炼50次成功")
	
def ArtifactCuiLian(role, msg):
	'''
	神器淬炼
	@param role:
	@param msg:(神器ID, 神器位置, 淬炼次数)
	'''
	eId, _, cnt = msg
	if cnt not in (1, 50):
		return 
	if role.GetLevel() < EnumGameConfig.ArtifactCuiLian_Level:
		return
	if role.ItemCnt(EnumGameConfig.ArtifactCuilian) < cnt:
		return
	
	globaldict = role.GetTempObj(EnumTempObj.enGlobalItemMgr)
	Artifact = globaldict.get(eId)
	
	#如果没有神器，或神器在背包，返回
	if not Artifact or Artifact.owner == None:
		return
	tip1 = Artifact.GetCuiLianExp()		#记录淬炼升级的总经验，用于提示消息
	beginLevel = Artifact.GetCuiLianLevel()
	if ArtifactCuiLianLevel_Dict[beginLevel].needExp == 0:
		return
	#选择用哪个日志记录
	if cnt == 1:
		CuiLianOkLog = CuiLianLog_1
	else:
		CuiLianOkLog = CuiLianLog_50
	with CuiLianOkLog:
		while cnt > 0:
			oldLevel = Artifact.GetCuiLianLevel()
			oldExp = Artifact.GetCuiLianExp()
			cfg = ArtifactCuiLianLevel_Dict[oldLevel]
			if cfg.needExp == 0:
				break
			needExp = cfg.needAllExp - oldExp
			if needExp > cnt:
				needExp = cnt
			
			#获取可以淬炼的最大等级
			if needExp <= 0:
				break
			
			newExp = needExp + oldExp
			cnt -= needExp
			
			role.DelItem(EnumGameConfig.ArtifactCuilian, needExp)
			Artifact.SetCuiLianExp(newExp)
			if cfg.needAllExp == Artifact.GetCuiLianExp():
				Artifact.AddCuiLianLevel(1)
			
	role.SendObj(Artifact_CuiLian_OK, (eId, Artifact.GetCuiLianExp()))
	
	#如果淬炼后等级提升了，重算属性，重算组合
	endLevel = Artifact.GetCuiLianLevel()
	#如果已经升到了顶级，没有经验增加，直接返回

	if endLevel > beginLevel:
		#设置神器属性重算
		Artifact.owner.GetPropertyGather().ReSetRecountArtifactCuiLianFlag()
		Artifact.owner.GetPropertyGather().RECOUNTARTIFACT()
	
		ArtifactCuiLianSuite(role, Artifact.owner)		
		
	tip2 = Artifact.GetCuiLianExp()		#记录淬炼升级的总经验，用于提示消息
	tip = tip2 - tip1
	if tip > 0:
		role.Msg(2, 1, GlobalPrompt.ArtifactCuiLian % tip)
	
def ArtifactCuiLianSuite(role, owner):
	'''
	重算owner的所有神器组合属性
	@param role:
	@param owner:神器拥有者
	'''
	#取出该人物所有神器ID
	if owner == role:
		Artifact_Set = role.GetObj(EnumObj.En_RoleArtifact)
	else:
		ArtifactDict = role.GetObj(EnumObj.En_HeroArtifact)
		Artifact_Set = ArtifactDict.get(owner.GetHeroId())
	if not Artifact_Set:
		return
	#将所有神器取出到一个List
	globaldict = role.GetTempObj(EnumTempObj.enGlobalItemMgr)
	ArtifactList = map(lambda x:globaldict.get(x), Artifact_Set)
	
	poseType_set = set()	#所有神器位置的集合
	CuiLianLevel_Dict = {}	#神器位置对应淬炼等级字典	{神器位置:淬炼等级}
	ArtifactObj_Dict = {}	#临时存储神器对象字典		{神器位置:神器对象}
	for Artifact in ArtifactList:
		if not Artifact or Artifact.cfg.posType > 6:
			continue
		ArtifactObj_Dict[Artifact.cfg.posType] = Artifact
		poseType_set.add(Artifact.cfg.posType)
		CuiLianLevel_Dict[Artifact.cfg.posType] = Artifact.GetCuiLianLevel()
		#清除神器的淬炼组合属性
		Artifact.ClearCuiLianSuite()
		
	#判断是否符合组合7
	if len(poseType_set) == 6:
		minLevel = min(CuiLianLevel_Dict.values())
		if minLevel in ArtifactCuiLianSuite7_Dict:
			suiteIndex = ArtifactCuiLianSuite7_Dict[minLevel]
		for Artifact_tmp  in ArtifactObj_Dict.values():
			Artifact_tmp.AddCuiLianSuite(suiteIndex)
	
	#判断是否符合组合1,2,3,4,5,6
	for _, posTuple in ArtifactCuiLianSuite_Dict.items():
		if not poseType_set >= set(posTuple):
			continue
		if len(posTuple) > 2:
			continue
		pos1, pos2 = posTuple
		cuiLianIndex1 = (pos1, CuiLianLevel_Dict[pos1], pos2, CuiLianLevel_Dict[pos2])
		cuiLianIndex2 = (pos2, CuiLianLevel_Dict[pos2], pos1, CuiLianLevel_Dict[pos1])
		
		suiteIndex = None
		if cuiLianIndex1 in ArtifactCuiLianIndex_Dict:
			suiteIndex = ArtifactCuiLianIndex_Dict[cuiLianIndex1]
		elif cuiLianIndex2 in ArtifactCuiLianIndex_Dict:
			suiteIndex = ArtifactCuiLianIndex_Dict[cuiLianIndex2]
		if not suiteIndex:
			continue
		for i in posTuple:
			Artifact_tmp = ArtifactObj_Dict.get(i)
			if not Artifact_tmp:
				continue
			if suiteIndex in Artifact_tmp.GetCuiLianSuite():
				break
			Artifact_tmp.AddCuiLianSuite(suiteIndex)
			
	#取出所有神器位置:神器淬炼组合，组合消息发回客户端
	msg_Dict = {}
	for Oid in Artifact_Set:
		Artifact = globaldict.get(Oid)
		if not Artifact or Artifact.cfg.posType > 6:
			continue
		msg_Dict[Oid] = Artifact.GetCuiLianSuite()
	#重算淬炼组合属性
	owner.GetArtifactMgr().ResetCuiLianSuite()
	owner.GetArtifactMgr().ResetCuiLianHole()
	owner.GetPropertyGather().ReSetRecountArtifactCuiLianSuiteFlag()
	owner.GetPropertyGather().ReSetRecountArtifactCuiLianHoleFlag()
	owner.GetPropertyGather().RECOUNTARTIFACT()
	role.SendObj(Artifact_CuiLianSuite, msg_Dict)
	
def ArtifactCuiLianhole(role, msg):
	'''
	淬炼光环强化
	@param role:
	@param msg:强化次数
	'''
	if msg < 1:
		return
	if role.GetLevel() < EnumGameConfig.ArtifactCuiLian_Level:
		return
	
	HoleExp = role.GetI32(EnumInt32.AtifactHalo)
	oldLevel = role.GetArtifactCuiLianHoleLevel()
	obj = ArtifactCuiLianHalo_Dict.get(oldLevel)
	if not obj or obj.needExp == 0:
		return
	
	#实际需要淬炼强化石个数
	itemCnt = min(msg, obj.needAllExp - HoleExp)
	if itemCnt == 0:
		return
	#淬炼强化石不足
	if role.ItemCnt(EnumGameConfig.ArtifactCuilianHalo) < itemCnt:
		return
	
	with CuiLianStrengthLog:
		role.DelItem(EnumGameConfig.ArtifactCuilianHalo, itemCnt)
		role.IncI32(EnumInt32.AtifactHalo, itemCnt)
		newHoleExp = role.GetI32(EnumInt32.AtifactHalo)
		if newHoleExp == obj.needAllExp:
			role.IncI8(EnumInt8.AtifactHaloLevel, 1)
			
	newlevel = role.GetArtifactCuiLianHoleLevel()
	#提示消息
	msgTip = GlobalPrompt.ArtifactCuiLianHole1
	if newlevel > oldLevel:
		#重算所有光环属性
		reSetHoleProperty(role)
		#提示消息
		msgTip += GlobalPrompt.ArtifactCuiLianHole2 % newlevel
	
	role.Msg(2, 1, msgTip)
	
def reSetHoleProperty(role):
	# 重算主角淬炼光环属性
	role.GetArtifactMgr().ResetCuiLianHole()
	role.GetPropertyGather().ReSetRecountArtifactCuiLianHoleFlag()
	role.GetPropertyGather().RECOUNTARTIFACT()
	#重算有神器的英雄属性
	ArtifactDict = role.GetObj(EnumObj.En_HeroArtifact)
	for heroId in ArtifactDict.keys():
		#重算每个上阵英雄的光环属性加成
		hero = role.GetHero(heroId)
		hero.GetArtifactMgr().ResetCuiLianHole()
		hero.GetPropertyGather().ReSetRecountArtifactCuiLianHoleFlag()
		hero.GetPropertyGather().RECOUNTARTIFACT()
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Artifact_CuiLian", "请求神器淬炼"), ArtifactCuiLian)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ArtifactCuiLianhole", "淬炼光环强化"), ArtifactCuiLianhole)
	
