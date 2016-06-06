#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Pet.PetMgr")
#===============================================================================
# 宠物管理
#===============================================================================
import random
import cProcess
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Activity.WonderfulAct import WonderfulActMgr, EnumWonderType
from Game.Activity.ProjectAct import ProjectAct, EnumProActType
from Game.Pet import PetBase, PetConfig
from Game.Role import Event
from Game.Role.Data import EnumTempObj, EnumInt64, EnumInt8, EnumInt1, EnumObj
from Game.Activity.LatestActivity import LatestActivityMgr, EnumLatestType

if "_HasLoad" not in dir():
	FAST_TRAIN_CNT = 50		#快速培养次数
	LUCKY_MAX = 10000		#幸运值上限
	NEED_LEVEL = 70			#宠物系统需求等级
	
	#消息
	Hero_Pet_Type = AutoMessage.AllotMessage("Hero_Pet_Type", "同步英雄宠物类型")
	Hero_Pet_ID = AutoMessage.AllotMessage("Hero_Pet_ID", "同步英雄宠物ID")
	Pet_Show_Panel = AutoMessage.AllotMessage("Pet_Show_Panel", "通知客户端显示宠物面板")
	Syn_PetTempPt = AutoMessage.AllotMessage("Syn_PetTempPt", "同步宠物临时属性值")
	Syn_PetTempEvoValue = AutoMessage.AllotMessage("Syn_PetTempEvoValue", "同步宠物临时修行进度")

def AddPet(role, petType):
	petMgr = role.GetTempObj(EnumTempObj.PetMgr)
	
	#宠物初始属性配置
	petInitPropertyConfig = PetConfig.PET_INIT_PROPERTY.get(petType)
	if not petInitPropertyConfig:
		return
	
	petId = cProcess.AllotGUID64()
	petMgr.pet_dict[petId] = petMgr.create(petType, petInitPropertyConfig)
	
	#日志事件
	AutoLog.LogBase(role.GetRoleID(), AutoLog.eveAddPet, petType)
	
	#最新活动--宠物培养日
	LatestActivityMgr.GetFunByType(EnumLatestType.PetTrain_Latest, (role, 1))
	#最新活动--宠物修行日
	LatestActivityMgr.GetFunByType(EnumLatestType.PetEvo_Latest, (role, 1))
	
	#如果没有宠物跟随，则让新获得的宠物跟随
	if role.GetI64(EnumInt64.PetFollowID):
		return
	else:
		PetFollow(role, petId, 1)
#======宠物增加临时修行值=====
def ItemPetEvoTigger(role, evoId):
	#用道具增加指定阶数的临时修行进度，需要检测进度是否已满，满的话把临时进度设置成永久，并清理对应的临时属性
	petMgr = role.GetTempObj(EnumTempObj.PetMgr)
	if not petMgr:
		return
	if not petMgr.pet_dict:#玩家没宠物
		return
	ptDict = {}#用于存指定星级的宠物
	for petId, pet in petMgr.pet_dict.iteritems():
		if pet.evoId != evoId:
			continue
		ptDict[petId] = pet
	if not ptDict:
		return
	petData = role.GetObj(EnumObj.LatestActData).get(8, {})
	tempValue = petData.setdefault(evoId, 0)
	if not tempValue:
		return
	for petId, pet in ptDict.iteritems():
		#假如当前的宠物修行进度已满，忽视之
		key = (pet.type, pet.evoId)
		cfg = PetConfig.PET_EVOLUTION_DICT.get(key)
		if not cfg:
			print "GE_EXC,can not find type(%s) and evoID(%s) in ItemPetEvoTigger" % (pet.type, pet.evoId)
			return
		#已经是最高级的了
		if not cfg.nextEvoId:
			return
	
		if pet.evoExp >= cfg.maxExp:
			continue
		if pet.evoExp + tempValue >= cfg.maxExp:
			#将宠物进度设置成永久，清空临时进度
			pet.evoExp = cfg.maxExp
			tempValue = 0
			petData[pet.evoId] = 0
			AutoLog.LogBase(role.GetRoleID(), AutoLog.evePetItemEvoData, (petId, pet.evoId, tempValue))#宠物ID， 宠物进化度，多少临时属性变永久
	
		petMgr = role.GetTempObj(EnumTempObj.PetMgr)
	#同步临时修行进度
	role.SendObj(Syn_PetTempEvoValue, petData)
	
	petList = []
	for petId, petObj in petMgr.pet_dict.iteritems():
		petList.append((petId, petObj.type, petObj.star, petObj.hero_id, petObj.property_dict, petObj.lucky_dict, petObj.soul_dict.values(), \
						petObj.evoId, petObj.evoExp, petObj.evoluck, petObj.shapeId, petObj.unlockRes_list))
	
	#同步客户端
	role.SendObj(Pet_Show_Panel, petList)

#======宠物增加临时属性=======
def ItemPetTrainTigger(role, star):
	#用道具增加指定星级的临时属性，需要检测对应的属性是否已满，满的话把临时属性设置成永久属性，
	#并清理对应的临时属性
	petMgr = role.GetTempObj(EnumTempObj.PetMgr)
	if not petMgr:
		return
	if not petMgr.pet_dict:#玩家没宠物
		return
	ptDict = {}#用于存指定星级的宠物
	for petId, pet in petMgr.pet_dict.iteritems():
		if pet.star != star:
			continue
		ptDict[petId] = pet
	if not ptDict:
		return
	
	petData = role.GetObj(EnumObj.LatestActData).get(7, {})
	starData = petData.setdefault(star, {})
	if not starData:
		return
	for petId, pet in ptDict.iteritems():
		#宠物相关配置
		petConfig = PetConfig.PET_BASE.get((pet.type, pet.star))
		if not petConfig:
			return
		petMaxPropertyConfig = PetConfig.PET_MAX_PROPERTY.get((pet.type, pet.star))
		if not petMaxPropertyConfig:
			return
		
		petTrainPropertyConfig = PetConfig.PET_TRAIN_PROPERTY.get(pet.type)
		if not petTrainPropertyConfig:
			return
		for pt, pv in starData.items():
			if pv == 0:
				continue
			if pet.type in [1, 3, 4] and pt == 6:#物攻宠物法攻属性忽视
				continue
			if pet.type == 2 and pt == 4:#法攻宠物物攻属性忽视
				continue
			#对应属性是否存在
			if pt not in pet.property_dict:
				return
			if pt not in pet.lucky_dict:
				return
			if pt not in petMaxPropertyConfig.property_dict:
				return
			if pt not in petTrainPropertyConfig.property_dict:
				return
	
			#属性是否已满
			nowPv = pet.property_dict[pt]
			#当前的属性已经满了，就忽视
			if nowPv >= petMaxPropertyConfig.property_dict[pt]:
				continue
			if nowPv + pv >= petMaxPropertyConfig.property_dict[pt]:
				#属性值满了
				pet.property_dict[pt] = petMaxPropertyConfig.property_dict[pt]
				starData[pt] = 0
				#重算属性
				PetBase.RecountPropertyByPet(role, pet)
				#日志事件
				AutoLog.LogBase(role.GetRoleID(), AutoLog.evePetItemAddPro, (petId, pt, nowPv, pet.property_dict[pt]))
	#同步临时值属性
	role.SendObj(Syn_PetTempPt, petData)
	petList = []
	for petId, petObj in petMgr.pet_dict.iteritems():
		petList.append((petId, petObj.type, petObj.star, petObj.hero_id, petObj.property_dict, petObj.lucky_dict, petObj.soul_dict.values(), \
						petObj.evoId, petObj.evoExp, petObj.evoluck, petObj.shapeId, petObj.unlockRes_list))
	#同步客户端
	role.SendObj(Pet_Show_Panel, petList)
	
def SysPetShape(role, heroId, shapeId):
	#同步英雄宠物类型
	role.SendObj(Hero_Pet_Type, (heroId, shapeId))

def ShowPetPanel(role):
	'''
	显示宠物面板
	@param role:
	'''
	petMgr = role.GetTempObj(EnumTempObj.PetMgr)
	
	petList = []
	for petId, petObj in petMgr.pet_dict.iteritems():
		petList.append((petId, petObj.type, petObj.star, petObj.hero_id, petObj.property_dict, petObj.lucky_dict, petObj.soul_dict.values(), \
						petObj.evoId, petObj.evoExp, petObj.evoluck, petObj.shapeId, petObj.unlockRes_list))
	
	#同步客户端
	role.SendObj(Pet_Show_Panel, petList)
	
def TrainPet(role, petId, propertyEnum, backFunId):
	'''
	宠物培养
	@param role:
	@param petId:
	@param propertyEnum:
	'''
	petMgr = role.GetTempObj(EnumTempObj.PetMgr)
	
	#用宠物ID索引宠物
	if petId not in petMgr.pet_dict:
		return
	
	pet = petMgr.pet_dict[petId]
	
	#宠物相关配置
	petConfig = PetConfig.PET_BASE.get((pet.type, pet.star))
	if not petConfig:
		return
	petMaxPropertyConfig = PetConfig.PET_MAX_PROPERTY.get((pet.type, pet.star))
	if not petMaxPropertyConfig:
		return
	petTrainPropertyConfig = PetConfig.PET_TRAIN_PROPERTY.get(pet.type)
	if not petTrainPropertyConfig:
		return
	
	#对应属性是否存在
	if propertyEnum not in pet.property_dict:
		return
	if propertyEnum not in pet.lucky_dict:
		return
	if propertyEnum not in petMaxPropertyConfig.property_dict:
		return
	if propertyEnum not in petTrainPropertyConfig.property_dict:
		return
	
	#属性是否已满
	nowProperty = pet.property_dict[propertyEnum]
	trainAddPropety = petTrainPropertyConfig.property_dict[propertyEnum]
	if nowProperty >= petMaxPropertyConfig.property_dict[propertyEnum]:
		return
	
	#有道具优先扣除道具
	itemCnt = role.ItemCnt(petConfig.trainNeedItemCoding)
	if itemCnt > 0:
		#扣物品
		role.DelItem(petConfig.trainNeedItemCoding, 1)
	else:
		#是否够RMB
		if role.GetUnbindRMB() < petConfig.trainNeedRMB:
			return
		#扣RMB
		role.DecUnbindRMB(petConfig.trainNeedRMB)
		
	#是否培养成功
	nowLucky = pet.lucky_dict[propertyEnum]
	if random.randint(1, LUCKY_MAX) <= nowLucky:
		#成功
		#加属性
		pet.property_dict[propertyEnum] = nowProperty + trainAddPropety
		nowpt = pet.property_dict.get(propertyEnum)
		petptData = role.GetObj(EnumObj.LatestActData).get(7, {})
		starData = petptData.get(pet.star, {})
		temppt = starData.get(propertyEnum, 0)
		#当临时属性+当前属性的值大于或等于最大值时，将当前属性设置为最大值，并清空临时值
		if nowpt + temppt >= petMaxPropertyConfig.property_dict[propertyEnum]:
			pet.property_dict[propertyEnum] = petMaxPropertyConfig.property_dict[propertyEnum]
			if propertyEnum in [4, 6]:#物攻和法攻特殊处理
				starData[4] = 0
				starData[6] = 0
			else:
				starData[propertyEnum] = 0
			role.SendObj(Syn_PetTempPt, petptData)
		#初始化幸运值
		pet.lucky_dict[propertyEnum] = petConfig.initLucky
		#提示
		role.Msg(2, 0, GlobalPrompt.PET_TRAIN_SUCCESS_PROMPT % trainAddPropety)
	else:
		#失败
		#加幸运值
		totalLucky = nowLucky + petConfig.addLucky
		if totalLucky >= LUCKY_MAX:
			pet.lucky_dict[propertyEnum] = LUCKY_MAX
		else:
			pet.lucky_dict[propertyEnum] = totalLucky
		#提示
		role.Msg(2, 0, GlobalPrompt.PET_TRAIN_FAIL_PROMPT)
		
	#日志事件
	AutoLog.LogBase(role.GetRoleID(), AutoLog.evePetTrain, (petId, propertyEnum, nowProperty, pet.property_dict[propertyEnum]))
	
	#重算属性
	PetBase.RecountPropertyByPet(role, pet)
	#精彩活动增加宠物培养次数接口
	WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_Pet_Times, [role, 1])
	#专题活动增加宠物培养次数接口
	ProjectAct.GetFunByType(EnumProActType.ProjectPetEvent, (role, 1))
	#北美通用活动
	if Environment.EnvIsNA():
		HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
		HalloweenNAMgr.CultivatePet(1)
		HalloweenNAMgr.CultivatePetForever(1)
		#开服活动
		KaiFuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
		KaiFuActMgr.Petcultivate(1)
	#回调客户端(属性值，幸运值)
	role.CallBackFunction(backFunId, (pet.property_dict[propertyEnum], pet.lucky_dict[propertyEnum]))
	
def FastTrainPet(role, petId, propertyEnum, backFunId):
	'''
	宠物快速培养
	@param role:
	@param petId:
	@param propertyEnum:
	'''
	petMgr = role.GetTempObj(EnumTempObj.PetMgr)
	
	#用宠物ID索引宠物
	if petId not in petMgr.pet_dict:
		return
	
	pet = petMgr.pet_dict[petId]
	
	#宠物相关配置
	petConfig = PetConfig.PET_BASE.get((pet.type, pet.star))
	if not petConfig:
		return
	petMaxPropertyConfig = PetConfig.PET_MAX_PROPERTY.get((pet.type, pet.star))
	if not petMaxPropertyConfig:
		return
	petTrainPropertyConfig = PetConfig.PET_TRAIN_PROPERTY.get(pet.type)
	if not petTrainPropertyConfig:
		return
	
	#对应属性是否存在
	if propertyEnum not in pet.property_dict:
		return
	if propertyEnum not in pet.lucky_dict:
		return
	if propertyEnum not in petMaxPropertyConfig.property_dict:
		return
	if propertyEnum not in petTrainPropertyConfig.property_dict:
		return
	
	#属性是否已满
	nowProperty = pet.property_dict[propertyEnum]
	maxProperty = petMaxPropertyConfig.property_dict[propertyEnum]
	trainAddProperty = petTrainPropertyConfig.property_dict[propertyEnum]
	if nowProperty >= maxProperty:
		return
	#获取临时属性
	petData = role.GetObj(EnumObj.LatestActData).get(7, {})
	starData = petData.get(pet.star, {})
	tempPro = starData.get(propertyEnum, 0)
	
	itemCnt = role.ItemCnt(petConfig.trainNeedItemCoding)
	rmbCntTrainCnt = role.GetUnbindRMB() / petConfig.trainNeedRMB
	#总的可以培养的次数
	totalCanTrainCnt = itemCnt + rmbCntTrainCnt
	#是否满足进行快速培养的条件(道具和RMB加起来可以培养的次数比最少培养次数多)
	minNeedTrainCnt = min(int((maxProperty - nowProperty - tempPro) / trainAddProperty), FAST_TRAIN_CNT)
	if totalCanTrainCnt < minNeedTrainCnt:
		#提示
		role.Msg(2, 0, GlobalPrompt.PET_RMB_NOT_ENOUGH_PROMPT)
		return
	
	#循环(有最大次数限制)
	success = 0	#成功次数
	lost = 0	#失败次数
	
	nowProperty = pet.property_dict[propertyEnum]
	resultProperty = pet.property_dict[propertyEnum]
	resultLucky = pet.lucky_dict[propertyEnum]
	for _ in xrange(min(totalCanTrainCnt, FAST_TRAIN_CNT)):
		#判断属性上限
		if resultProperty + tempPro >= maxProperty:
			break
			
		if random.randint(1, LUCKY_MAX) <= resultLucky:
			#成功
			success += 1
			#加属性
			resultProperty += trainAddProperty
			#初始化幸运值
			resultLucky = petConfig.initLucky
		else:
			#失败
			lost += 1
			#加幸运值
			resultLucky += petConfig.addLucky
			if resultLucky >= LUCKY_MAX:
				resultLucky = LUCKY_MAX
	
	totalNeedItemCnt = success + lost
	if not totalNeedItemCnt: return
	#有道具优先扣除道具
	itemCnt = role.ItemCnt(petConfig.trainNeedItemCoding)
	if itemCnt >= totalNeedItemCnt and totalNeedItemCnt:
		#道具数量满足则全扣完
		role.DelItem(petConfig.trainNeedItemCoding, totalNeedItemCnt)
	elif itemCnt > 0:
		#有道具优先扣除道具
		role.DelItem(petConfig.trainNeedItemCoding, itemCnt)
		totalNeedItemCnt -= itemCnt
		
		needRMB = totalNeedItemCnt * petConfig.trainNeedRMB
		#是否够RMB
		if role.GetUnbindRMB() < needRMB:
			return
		#扣RMB
		role.DecUnbindRMB(needRMB)
	else:
		needRMB = totalNeedItemCnt * petConfig.trainNeedRMB
		#是否够RMB
		if role.GetUnbindRMB() < needRMB:
			return
		#扣RMB
		role.DecUnbindRMB(needRMB)
	
	#设置属性和幸运值
	pet.property_dict[propertyEnum] = resultProperty
	if pet.property_dict[propertyEnum] + tempPro >= maxProperty:
		#清空对应的临时属性
		if propertyEnum in [4, 6]:#物攻和法攻特殊处理
			starData[4] = 0
			starData[6] = 0
		else:
			starData[propertyEnum] = 0
		pet.property_dict[propertyEnum] = maxProperty
		role.SendObj(Syn_PetTempPt, petData)
	pet.lucky_dict[propertyEnum] = resultLucky
	
	#日志事件
	AutoLog.LogBase(role.GetRoleID(), AutoLog.evePetTrain, (petId, propertyEnum, nowProperty, pet.property_dict[propertyEnum]))
				
	#重算属性
	PetBase.RecountPropertyByPet(role, pet)
	#精彩活动增加宠物培养次数接口
	WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_Pet_Times, [role, success + lost])
	#专题活动增加宠物培养次数借口
	ProjectAct.GetFunByType(EnumProActType.ProjectPetEvent, (role, success + lost))
	#北美活动
	if Environment.EnvIsNA():
		#通用活动
		HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
		HalloweenNAMgr.CultivatePet(success + lost)
		HalloweenNAMgr.CultivatePetForever(success + lost)
		#开服活动
		KaiFuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
		KaiFuActMgr.Petcultivate(success + lost)
	#回调客户端(属性值，幸运值)
	role.CallBackFunction(backFunId, (pet.property_dict[propertyEnum], pet.lucky_dict[propertyEnum]))
	
	#提示
	role.Msg(2, 0, GlobalPrompt.PET_FAST_TRAIN_PROMPT % (success + lost, success, lost))
	
def UpgradePet(role, petId, backFunId):
	'''
	宠物升星
	@param role:
	@param petId:
	'''
	petMgr = role.GetTempObj(EnumTempObj.PetMgr)
	
	#用宠物ID索引宠物
	if petId not in petMgr.pet_dict:
		return
	
	pet = petMgr.pet_dict[petId]
	
	#宠物相关配置
	petConfig = PetConfig.PET_BASE.get((pet.type, pet.star))
	if not petConfig:
		return
	petMaxPropertyConfig = PetConfig.PET_MAX_PROPERTY.get((pet.type, pet.star))
	if not petMaxPropertyConfig:
		return
	
	#是否已经升到最高星
	if pet.star >= petConfig.maxStarLevel:
		return
	
	#判断所有属性是否已满
	for pEnum, pValue in pet.property_dict.iteritems():
		if pValue < petMaxPropertyConfig.property_dict[pEnum]:
			return
	
	#升星后配置
	afterUpgradePetConfig = PetConfig.PET_BASE.get((pet.type, pet.star + 1))
	if not afterUpgradePetConfig:
		return
	
	oldStar = pet.star
	#升星
	pet.star += 1
	
	#重新初始化幸运值
	for k in pet.lucky_dict.keys():
		pet.lucky_dict[k] = afterUpgradePetConfig.initLucky
		
	#回调客户端
	role.CallBackFunction(backFunId, pet.star)
	
	#日志事件
	AutoLog.LogBase(role.GetRoleID(), AutoLog.evePetUpgrade, (petId, oldStar, pet.star))
	
	#更新宠物面板
	ShowPetPanel(role)
	
	#精彩活动特殊处理
	if pet.star >= 2:
		WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_Inc_Pet, role)
	#北美
	if Environment.EnvIsNA():
		#通用活动
		HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
		HalloweenNAMgr.PetEvo(pet.star)
		#开服活动
		KaiFuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
		KaiFuActMgr.Petadvanced()
	#最新活动
	LatestActivityMgr.GetFunByType(EnumLatestType.PetTrain_Latest, (role, pet.star))
		
def OnPetRole(role, petId, backFunId):
	petMgr = role.GetTempObj(EnumTempObj.PetMgr)
	
	#用宠物ID索引宠物
	if petId not in petMgr.pet_dict:
		return
	
	pet = petMgr.pet_dict[petId]
	
	#先把此宠物从别人身上下阵(也可能没人佩戴此宠物)
	OffPet(role, petId)
	
	#主角身上是否已经佩戴宠物(是则下阵)
	rolePetId = role.GetI64(EnumInt64.PetID)
	if rolePetId:
		if rolePetId not in petMgr.pet_dict:
			return
		rolePet = petMgr.pet_dict[rolePetId]
		if rolePet.hero_id != role.GetRoleID():
			return
		rolePet.SetHeroID(0)
	
	#上阵
	pet.SetHeroID(role.GetRoleID())
	role.SetI64(EnumInt64.PetID, petId)
	role.SetI8(EnumInt8.PetType, pet.shapeId)

	#重算属性
	role.GetPropertyGather().ReSetRecountPetFlag()
	#重算属性
	pet.RecountProperty()
	role.GetPropertyGather().ReSetRecountPetRvoFlag()
	#成功回调客户端
	role.CallBackFunction(backFunId, None)
	
def OnPetHero(role, petId, heroId, backFunId):
	petMgr = role.GetTempObj(EnumTempObj.PetMgr)
	
	#用宠物ID索引宠物
	if petId not in petMgr.pet_dict:
		return
	
	pet = petMgr.pet_dict[petId]
	
	hero = role.GetHero(heroId)
	if not hero:
		return
	
	#英雄是否上阵(没上阵不可以佩戴宠物)
	if not hero.GetStationID():
		return
	
	#先把此宠物从别人身上卸下(也可能没人佩戴此宠物)
	OffPet(role, petId)
	
	#英雄身上是否已经佩戴宠物(是则卸下)
	heroPetId = hero.GetPetID()
	if heroPetId:
		if heroPetId not in petMgr.pet_dict:
			return
		heroPet = petMgr.pet_dict[heroPetId]
		if heroPet.hero_id != heroId:
			return
		heroPet.SetHeroID(0)
	
	#上阵
	pet.SetHeroID(heroId)
	hero.SetPetID(petId)
	hero.SetPetType(pet.shapeId)
	#重算属性
	hero.GetPropertyGather().ReSetRecountPetFlag()
	#重算属性
	pet.RecountProperty()
	hero.GetPropertyGather().ReSetRecountPetRvoFlag()
	#成功回调客户端
	role.CallBackFunction(backFunId, None)
	
	#同步英雄宠物类型
	role.SendObj(Hero_Pet_Type, (heroId, pet.shapeId))
	#同步英雄宠物ID
	role.SendObj(Hero_Pet_ID, (heroId, petId))
	
def OffPet(role, petId, backFunId = None):
	'''
	宠物下阵
	@param role:
	@param petId:
	@param backFunId:
	'''
	petMgr = role.GetTempObj(EnumTempObj.PetMgr)
	
	#用宠物ID索引宠物
	if petId not in petMgr.pet_dict:
		return
	
	pet = petMgr.pet_dict[petId]
	
	#没有人佩戴此宠物
	if not pet.hero_id:
		return
	
	#判断是在主角身上还是英雄身上
	if role.GetRoleID() == pet.hero_id:
		#主角
		pet.SetHeroID(0)
		role.SetI64(EnumInt64.PetID, 0)
		role.SetI8(EnumInt8.PetType, 0)
		#重算属性
		role.GetPropertyGather().ReSetRecountPetFlag()
		#重算属性
		pet.RecountProperty()
		role.GetPropertyGather().ReSetRecountPetRvoFlag()
	else:
		#英雄
		oldHeroId = pet.hero_id
		hero = role.GetHero(oldHeroId)
		if not hero:
			return
		pet.SetHeroID(0)
		hero.SetPetID(0)
		hero.SetPetType(0)
		#重算属性
		hero.GetPropertyGather().ReSetRecountPetFlag()
		#重算属性
		pet.RecountProperty()
		hero.GetPropertyGather().ReSetRecountPetRvoFlag()
		#同步英雄宠物类型
		role.SendObj(Hero_Pet_Type, (oldHeroId, 0))
		#同步英雄宠物ID
		role.SendObj(Hero_Pet_ID, (oldHeroId, 0))
		
	#成功回调客户端
	if backFunId:
		role.CallBackFunction(backFunId, None)
	
def FirePet(role, petId):
	'''
	解雇宠物
	@param role:
	@param petId:
	'''
	
def SetPetFastTrain(role):
	'''
	设置宠物快速培养
	@param role:
	'''
	#设置快速培养标志
	if role.GetI1(EnumInt1.PetFastTrain):
		role.SetI1(EnumInt1.PetFastTrain, 0)
	else:
		role.SetI1(EnumInt1.PetFastTrain, 1)
		
def PetFollow(role, petId, yesOrNo):
	petMgr = role.GetTempObj(EnumTempObj.PetMgr)
	
	#用宠物ID索引宠物
	if petId not in petMgr.pet_dict:
		return
	
	pet = petMgr.pet_dict[petId]
	
	if yesOrNo == 1:
		#跟随
		if role.GetI64(EnumInt64.PetFollowID) == petId:
			#已经跟随
			return
		#设置跟随
		role.SetI64(EnumInt64.PetFollowID, petId)
		role.SetI8(EnumInt8.PetFollowType, pet.shapeId)
	elif yesOrNo == 2:
		#取消跟随
		if role.GetI64(EnumInt64.PetFollowID) != petId:
			#此宠物没有跟随，无法取消
			return
		#取消跟随
		role.SetI64(EnumInt64.PetFollowID, 0)
		role.SetI8(EnumInt8.PetFollowType, 0)
	
#===============================================================================
# 事件
#===============================================================================
def OnRoleLogin(role, param):
	'''
	角色登陆
	@param role:
	@param param:
	'''
	if Environment.IsDevelop:
		RevertPet(role)

def SyncRoleOtherData(role, param):
	#同步宠物临时属性值
	petPtData = role.GetObj(EnumObj.LatestActData).get(7, {})
	petEvoData = role.GetObj(EnumObj.LatestActData).get(8, {})
	role.SendObj(Syn_PetTempPt, petPtData)
	role.SendObj(Syn_PetTempEvoValue, petEvoData)
	
def RoleDayClear(role, param):
	#清理宠物的临时培养属性和临时修行进度
	LatestActData = role.GetObj(EnumObj.LatestActData)
	LatestActData[7] = {}
	LatestActData[8] = {}
	role.SendObj(Syn_PetTempPt, {})
	role.SendObj(Syn_PetTempEvoValue, {})
	
def RevertPet(role):
	#导号改变角色ID，导致佩戴在主角身上的宠物记录的roleId和内网的不一致
	#修复之
	petId = role.GetI64(EnumInt64.PetID)
	if not petId:
		return
	petMgr = role.GetTempObj(EnumTempObj.PetMgr)
	#用宠物ID索引宠物
	if petId not in petMgr.pet_dict:
		return
	
	pet = petMgr.pet_dict[petId]
	
	roleId = role.GetRoleID()
	if pet.hero_id != roleId:
		pet.SetHeroID(roleId)
		#重算属性
		role.GetPropertyGather().ReSetRecountPetFlag()
		#重算属性
		pet.RecountProperty()
		role.GetPropertyGather().ReSetRecountPetRvoFlag()

def OnRoleInit(role, param):
	'''
	角色初始化
	@param role:
	@param param:
	'''
	role.SetTempObj(EnumTempObj.PetMgr, PetBase.PetMgr(role))

def OnRoleSave(role, param):
	'''
	角色保存
	@param role:
	@param param:
	'''
	petMgr = role.GetTempObj(EnumTempObj.PetMgr)
	petMgr.save()
	
#===============================================================================
# 客户端请求
#===============================================================================
def RequestOpenPetPanel(role, msg):
	'''
	客户端请求打开宠物面板
	@param role:
	@param msg:
	'''
	#等级限制
	if role.GetLevel() < NEED_LEVEL:
		return
	
	ShowPetPanel(role)
	
def RequestTrainPet(role, msg):
	'''
	客户端请求宠物培养
	@param role:
	@param msg:
	'''
	backFunId, data = msg
	petId, propertyEnum = data
	
	#等级限制
	if role.GetLevel() < NEED_LEVEL:
		return
	
	if role.GetI1(EnumInt1.PetFastTrain):
		#日志
		with TraPetTrain:
			FastTrainPet(role, petId, propertyEnum, backFunId)
	else:
		#日志
		with TraPetTrain:
			TrainPet(role, petId, propertyEnum, backFunId)
	
def RequestUpgradePet(role, msg):
	'''
	客户端请求宠物升星
	@param role:
	@param msg:
	'''
	backFunId, petId = msg
	
	#等级限制
	if role.GetLevel() < NEED_LEVEL:
		return
	
	#日志
	with TraPetUpgrade:
		UpgradePet(role, petId, backFunId)
	
def RequestPetOn(role, msg):
	'''
	客户端请求宠物上阵
	@param role:
	@param msg:
	'''
	backFunId, data = msg
	petId, roleOrHeroId = data
	
	#等级限制
	if role.GetLevel() < NEED_LEVEL:
		return
	
	if role.GetRoleID() == roleOrHeroId:
		OnPetRole(role, petId, backFunId)
	else:
		OnPetHero(role, petId, roleOrHeroId, backFunId)
		
def RequestPetOff(role, msg):
	'''
	客户端请求宠物下阵
	@param role:
	@param msg:
	'''
	backFunId, petId = msg
	
	#等级限制
	if role.GetLevel() < NEED_LEVEL:
		return
	
	OffPet(role, petId, backFunId)
	
def RequestPetFire(role, msg):
	'''
	客户端请求解雇宠物
	@param role:
	@param msg:
	'''
	petId = msg
	
	#等级限制
	if role.GetLevel() < NEED_LEVEL:
		return
	
	FirePet(role, petId)
	
def RequestSetPetFastTrain(role, msg):
	'''
	客户端请求宠物设置快速培养
	@param role:
	@param msg:
	'''
	#等级限制
	if role.GetLevel() < NEED_LEVEL:
		return
	
	SetPetFastTrain(role)
	
def RequestPetFollow(role, msg):
	'''
	客户端请求宠物跟随
	@param role:
	@param msg:
	'''
	petId, yesOrNo = msg
	
	#等级限制
	if role.GetLevel() < NEED_LEVEL:
		return
	
	PetFollow(role, petId, yesOrNo)
	
	
if "_HasLoad" not in dir():
	#角色登陆
	Event.RegEvent(Event.Eve_AfterLogin, OnRoleLogin)
	#角色初始化
	Event.RegEvent(Event.Eve_InitRolePyObj, OnRoleInit)
	#每日清理
	Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
	#角色保存
	Event.RegEvent(Event.Eve_BeforeSaveRole, OnRoleSave)
	Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
	#日志
	TraPetTrain = AutoLog.AutoTransaction("TraPetTrain", "宠物培养")
	TraPetUpgrade = AutoLog.AutoTransaction("TraPetUpgrade", "宠物升星")
	
	#消息
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Pet_Open_Panel", "客户端请求打开宠物面板"), RequestOpenPetPanel)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Pet_Train", "客户端请求宠物培养"), RequestTrainPet)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Pet_Upgrade", "客户端请求宠物升星"), RequestUpgradePet)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Pet_On", "客户端请求宠物上阵"), RequestPetOn)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Pet_Off", "客户端请求宠物下阵"), RequestPetOff)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Pet_Fire", "客户端请求解雇宠物"), RequestPetFire)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Pet_Set_Fast_Train", "客户端请求宠物设置快速培养"), RequestSetPetFastTrain)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Pet_Follow", "客户端请求宠物跟随"), RequestPetFollow)
