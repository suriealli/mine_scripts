#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Pet.PetEvolution")
#===============================================================================
# 宠物进化
#===============================================================================
import random
import cRoleMgr
import Environment
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from Game.Role.Data import EnumInt8, EnumInt64, EnumTempObj, EnumObj
from Game.Pet import PetBase, PetConfig, PetMgr
from Game.Activity.WonderfulAct import WonderfulActMgr, EnumWonderType
from Game.Activity.LatestActivity import LatestActivityMgr, EnumLatestType

if "_HasLoad" not in dir():
	LUCKY_MAX = 10000
	
	PetEvolutionCost = AutoLog.AutoTransaction("PetEvolutionCost", "宠物修行消耗")
	PetEvolutionData = AutoLog.AutoTransaction("PetEvolutionData", "宠物进化")
	
def RequestPracticePet(role, param):
	'''
	宠物修行
	'''
	backId, (petId, coding) = param
	if coding:
		if role.ItemCnt(coding) <= 0:
			return
	petMgr = role.GetTempObj(EnumTempObj.PetMgr)
	#用宠物ID索引宠物
	if petId not in petMgr.pet_dict:
		return	
	pet = petMgr.pet_dict[petId]

	key = (pet.type, pet.evoId)
	cfg = PetConfig.PET_EVOLUTION_DICT.get(key)
	if not cfg:
		print "GE_EXC,can not find type(%s) and evoID(%s) in PracticePet" % (pet.type, pet.evoId)
		return
	#已经是最高级的了
	if not cfg.nextEvoId:
		return
	
	if pet.evoExp >= cfg.maxExp:
		return
	
	petData = role.GetObj(EnumObj.LatestActData).get(8, {})
	tempValue = petData.setdefault(pet.evoId, 0)
	if pet.evoExp + tempValue >= cfg.maxExp:
		pet.evoExp = cfg.maxExp
		petData[pet.evoId] = 0
		role.SendObj(PetMgr.Syn_PetTempEvoValue, petData)
	
	if cfg.petStar > pet.star:
		role.Msg(2, 0, GlobalPrompt.PET_EVOLUTION_STAR % cfg.petStar)
		return
	
	if role.GetUnbindRMB() < cfg.unBindRMB:
		return
	with PetEvolutionCost:
		if coding:
			if role.DelItem(coding, 1) < 1:
				return
		role.DecUnbindRMB(cfg.unBindRMB)
		
		total_luck = min(cfg.sucRate + pet.evoluck, cfg.maxRate)
		if coding:
			itemCfg = PetConfig.PET_ITEM_LUCK_DICT.get(coding)
			if not itemCfg:
				print "GE_EXC,can not find coding(%s) in PracticePet" % coding
			else:
				total_luck += itemCfg.itemRate
		suc_state = False
		if random.randint(1, LUCKY_MAX) <= total_luck:
			#修行成功
			pet.evoExp += cfg.addExp
			if pet.evoExp + tempValue >= cfg.maxExp:
				#清空临时修行进度
				pet.evoExp = cfg.maxExp
				petData[pet.evoId] = 0
				role.SendObj(PetMgr.Syn_PetTempEvoValue, petData)
			#清空额外幸运值
			pet.evoluck = 0
			role.Msg(2, 0, GlobalPrompt.PET_EVOLUTION_SUC % cfg.addExp)
			if pet.evoExp >= cfg.maxExp:
				role.Msg(2, 0, GlobalPrompt.PET_EVOLUTION_FULL)
			suc_state = True
		else:
			#修行失败,增加成功率
			pet.evoluck += cfg.addRate
			role.Msg(2, 0, GlobalPrompt.PET_EVOLUTION_FALSE % (cfg.addRate/100,'%'))
		
		AutoLog.LogBase(role.GetRoleID(), AutoLog.evePetEvoData, (pet.type, pet.evoId, suc_state))#宠物类型，进化ID，是否修行成功
	#精彩活动
	WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_PetEvo, (role, 1))
	#回调客户端
	role.CallBackFunction(backId, (pet.evoId, pet.evoExp, pet.evoluck))#宠物的进化ID,修为值

def RequestOneKeyPracticePet(role, param):
	'''
	一键宠物修行
	@param role:
	@param param:
	'''
	backId, (petId, coding) = param
	
	petMgr = role.GetTempObj(EnumTempObj.PetMgr)
	#用宠物ID索引宠物
	pet = petMgr.pet_dict.get(petId)
	if not pet:
		return
	key = (pet.type, pet.evoId)
	cfg = PetConfig.PET_EVOLUTION_DICT.get(key)
	if not cfg:
		print "GE_EXC,can not find type(%s) and evoID(%s) in PracticePet" % (pet.type, pet.evoId)
		return
	#已经是最高级的了
	if not cfg.nextEvoId:
		return
	# 需要进阶
	if pet.evoExp >= cfg.maxExp:
		return
	#临时修行进度处理
	petData = role.GetObj(EnumObj.LatestActData).get(8, {})
	tempValue = petData.setdefault(pet.evoId, 0)
	if pet.evoExp + tempValue >= cfg.maxExp:
		pet.evoExp = cfg.maxExp
		petData[pet.evoId] = 0
		role.SendObj(PetMgr.Syn_PetTempEvoValue, petData)
	
	if cfg.petStar > pet.star:
		role.Msg(2, 0, GlobalPrompt.PET_EVOLUTION_STAR % cfg.petStar)
		return
	if role.GetUnbindRMB() < cfg.unBindRMB:
		return
#	额外获取的成功率
	if coding:
		itemCfg = PetConfig.PET_ITEM_LUCK_DICT.get(coding)
		if not itemCfg:
			print "GE_EXC,can not find coding(%s) in PracticePet" % coding
			return
		extern_luck = itemCfg.itemRate
	else:
		extern_luck = 0
		
#	获取玩家身上的物品个数
	totalRMB = role.GetUnbindRMB()
	totalItemCnt = role.ItemCnt(coding)
	if coding:
		maxCnt = min(totalItemCnt, 50)
	else:
		maxCnt = 50
	maxCnt = min(maxCnt, int(totalRMB/cfg.unBindRMB))
	if not maxCnt:
		return
	
	cnt = 0
	now_veoexp = pet.evoExp
	now_evoluck = pet.evoluck
	while cnt < maxCnt:
		total_luck = min(cfg.sucRate + now_evoluck, cfg.maxRate) + extern_luck
		cnt += 1
		if random.randint(1, LUCKY_MAX) <= total_luck:
			#修行成功
			now_veoexp += cfg.addExp
			#清空额外幸运值
			now_evoluck = 0
			if now_veoexp + tempValue >= cfg.maxExp:
				break
		else:
			#修行失败,增加成功率
			now_evoluck += cfg.addRate
	need_rmb = cnt * cfg.unBindRMB
#	计算完，现在开始扣除
	with PetEvolutionCost:
		if coding:
			role.DelItem(coding, cnt)
		role.DecUnbindRMB(need_rmb)
		add_exp = now_veoexp - pet.evoExp
		pet.evoExp = now_veoexp
		pet.evoluck = now_evoluck
		if add_exp > 0:
			role.Msg(2, 0, GlobalPrompt.PET_ONEKEY_EVOLUTION_SUC % (cnt, add_exp))
		if pet.evoExp + tempValue >= cfg.maxExp:
			pet.evoExp = cfg.maxExp
			petData[pet.evoId] = 0
			role.SendObj(PetMgr.Syn_PetTempEvoValue, petData)
			role.Msg(2, 0, GlobalPrompt.PET_EVOLUTION_FULL)
		AutoLog.LogBase(role.GetRoleID(), AutoLog.evePetEvoTimesData, (pet.type, pet.evoId, cnt, add_exp))#宠物类型，进化ID，修行总次数，成功次数
	#精彩活动
	WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_PetEvo, (role, cnt))
	#回调客户端
	role.CallBackFunction(backId, (pet.evoId, pet.evoExp, pet.evoluck))#宠物的进化ID,修为值		

def RequestEvoPet(role, param):
	'''
	请求进化宠物
	@param role:
	@param param:
	'''
	backId, (petId, ownerId) = param
	
	petMgr = role.GetTempObj(EnumTempObj.PetMgr)
	#用宠物ID索引宠物
	if petId not in petMgr.pet_dict:
		return
	pet = petMgr.pet_dict[petId]
	
	key = (pet.type, pet.evoId)
	cfg = PetConfig.PET_EVOLUTION_DICT.get(key)
	if not cfg:
		print "GE_EXC,can not find type(%s) and evoID(%s) in PracticePet" % (pet.type, pet.evoId)
		return
	#已经是最高级的了
	if not cfg.nextEvoId:
		return
	#修为进度未满
	if pet.evoExp < cfg.maxExp:
		return
	
	pet.evoExp = 0
	pet.evoId = cfg.nextEvoId
	
	if cfg.nextshapeId:#存在宠物外形
		pet.AddShapeID(cfg.nextshapeId)
		pet.SetShapeID(cfg.nextshapeId)
	
		if role.GetRoleID() == ownerId:
			role.SetI8(EnumInt8.PetType, cfg.nextshapeId)
		else:
			hero = role.GetHero(ownerId)
			if hero:
				hero.SetPetType(cfg.nextshapeId)
				PetMgr.SysPetShape(role, ownerId, cfg.nextshapeId)
	
		if role.GetI64(EnumInt64.PetFollowID) == petId:#假如该宠物正在跟随
			role.SetI8(EnumInt8.PetFollowType, cfg.nextshapeId)
	#重算属性
	pet.RecountProperty()
	PetBase.RecountEvoPropertyByPet(role, pet)
	
	with PetEvolutionData:
		AutoLog.LogBase(role.GetRoleID(), AutoLog.evePetEvoSucData, (petId, pet.type, pet.evoId))#宠物ID，宠物类型，进化后的进化ID
	#北美相关活动
	if Environment.EnvIsNA():
		HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
		HalloweenNAMgr.Petpractice(pet.evoId)
	#最新活动
	LatestActivityMgr.GetFunByType(EnumLatestType.PetEvo_Latest, (role, pet.evoId))
	#回调客户端
	role.CallBackFunction(backId, (pet.evoId, pet.unlockRes_list, pet.evoExp, cfg.nextshapeId))

def RequestChangeShape(role, param):
	'''
	客户端请求宠物幻化
	@param role:
	@param param:
	'''
	backId, (petId, shapeId, Id) = param
	obj = None
	if role.GetRoleID() != Id:#是英雄
		obj = role.GetHero(Id)
	else:
		obj = role
	petMgr = role.GetTempObj(EnumTempObj.PetMgr)
	#用宠物ID索引宠物
	if petId not in petMgr.pet_dict:
		return
	pet = petMgr.pet_dict[petId]
	
	pet.SetShapeID(shapeId)#设置改宠物的外观
	if role.GetI64(EnumInt64.PetFollowID) == petId:#假如该宠物正在跟随
		role.SetI8(EnumInt8.PetFollowType, shapeId)
	if obj != role and obj:#是英雄
		obj.SetPetType(shapeId)
		PetMgr.SysPetShape(role, Id, shapeId)
	else:
		role.SetI8(EnumInt8.PetType, shapeId)
	#回调客户端
	role.CallBackFunction(backId, pet.shapeId)#当前使用的外形
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Pet_Practice", "客户端请求宠物修行"), RequestPracticePet)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Pet_OneKeyPractice", "客户端请求一键宠物修行"), RequestOneKeyPracticePet)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Pet_Evolution", "客户端请求宠物进化"), RequestEvoPet)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Pet_ChangeShape", "客户端请求宠物幻化"), RequestChangeShape)
