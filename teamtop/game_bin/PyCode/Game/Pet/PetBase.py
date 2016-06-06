#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Pet.PetBase")
#===============================================================================
# 宠物基础模块
#===============================================================================
from Game.Pet import PetConfig
from Game.Role.Data import EnumObj, EnumInt64
from Game.Property import PropertyEnum

if "_HasLoad" not in dir():
	TYPE_INDEX = 1
	STAR_INDEX = 2
	HEROID_INDEX = 3
	PROPERTY_INDEX = 4
	LUCKY_INDEX = 5
	SOUL_INDEX = 6		#附灵索引
	EVOLUTION_INDEX = 7	#宠物进化ID
	EVOEXP_INDEX = 8	#宠物当前的修为值
	EVOLUCK_INDEX = 9	#进化额外的幸运值
	SHAPEID_INDEX = 10	#正在使用的外观
	
class Pet(object):
	def __init__(self, petType, star, heroId, propertyDict, luckyDict, soulDict, evoId, evoExp, evoLuck, shapeId):
		self.type = petType
		self.star =star
		self.hero_id = heroId
		
		self.evoId = evoId			#宠物进化ID
		self.evoExp = evoExp		#宠物当前经验值
		self.evoluck = evoLuck		#进化幸运值
		self.shapeId = shapeId		#正在使用的外观

		self.property_dict = {}		#属性字典
		self.lucky_dict = {}		#属性幸运值字典
		self.soul_dict = {}			#附灵字典

		self.property_dict = propertyDict
		self.lucky_dict= luckyDict
		self.soul_dict = soulDict
		
		self.InitEvolution()
		
	def InitEvolution(self):
		#这里做的是宠物进化的相关处理
		self.PetEvo_Property = {}
		self.unlockRes_list = set()
		for evoId in range(1, self.evoId + 1):
			key = (self.type, evoId)
			cfg = PetConfig.PET_EVOLUTION_DICT.get(key)
			if not cfg:
				print "GE_EXC,can not find evoId(%s) and type(%s)in InitEvolution" % (evoId, self.type)
				return
			for pk, pv in cfg.property_dict.iteritems():
				self.PetEvo_Property[pk] = self.PetEvo_Property.get(pk, 0) + pv
			self.unlockRes_list.add(cfg.shapeId)
			if self.shapeId == 0:#这个只会出在新增宠物
				self.shapeId = cfg.shapeId
	
	def InitEvoPro(self):
		if not self.hero_id:
			self.PetEvo_Property = {}
			return
		for evoId in range(1, self.evoId + 1):
			key = (self.type, evoId)
			cfg = PetConfig.PET_EVOLUTION_DICT.get(key)
			if not cfg:
				print "GE_EXC,can not find type(%s) and evoId(%s) in InitEvolution" % (self.type, evoId)
				return
			for pk, pv in cfg.property_dict.iteritems():
				self.PetEvo_Property[pk] = self.PetEvo_Property.get(pk, 0) + pv
	
	def GetPetEvoPro(self):
		if not self.PetEvo_Property:
			self.InitEvoPro()
		return self.PetEvo_Property
	
	def RecountProperty(self):
		self.PetEvo_Property = {}
		
	def SetHeroID(self, heroId):
		self.hero_id = heroId
	
	def AddShapeID(self, shapeId):
		if not shapeId:
			return
		self.unlockRes_list.add(shapeId)

	def SetShapeID(self, shapeId):
		#设置外形ID
		if shapeId not in self.unlockRes_list:
			return
		self.shapeId = shapeId

class PetMgr(object):
	def __init__(self, role):
		self.role = role
		self.pet_dict = {}
		
		petDict = role.GetObj(EnumObj.Pet)
		for petId, petData in petDict.iteritems():
			self.pet_dict[petId] = Pet(petData[TYPE_INDEX], petData[STAR_INDEX],  petData[HEROID_INDEX],
									petData[PROPERTY_INDEX], petData[LUCKY_INDEX], petData[SOUL_INDEX], \
									petData.get(EVOLUTION_INDEX, 1), petData.get(EVOEXP_INDEX, 0), \
									petData.get(EVOLUCK_INDEX, 0), petData.get(SHAPEID_INDEX, 0))

	def create(self, petType, petInitPropertyConfig):
		propertyDict = {}
		luckDict = {}
		soulDict = {}
		for k, v in petInitPropertyConfig.property_dict.iteritems():
			#初始幸运值10000(培养必定成功)
			if v:
				propertyDict[k] = v
				luckDict[k] = 10000
		#宠物类型，星级，英雄id， 属性值， 幸运， 封灵， 进化id， 修为经验值，幸运值， 正在使用的外观
		return Pet(petType, 1, 0, propertyDict, luckDict, soulDict, 1, 0, 0, 0)
	
	def get_role_soul_dict(self, role):
		petId = role.GetI64(EnumInt64.PetID)
		if not petId:
			return {}
		
		if petId not in self.pet_dict:
			return {}
		
		pet = self.pet_dict[petId]
		
		return self.get_soul_property_dict(pet)
			
	def get_hero_soul_dict(self, hero):
		petId = hero.GetPetID()
		if not petId:
			return {}
		
		if petId not in self.pet_dict:
			return {}
		
		pet = self.pet_dict[petId]
		
		return self.get_soul_property_dict(pet)
	
	def get_soul_property_dict(self, pet):
		soulPropertyDict = {}	#宠物之灵属性字典{属性枚举：宠物之灵属性}
		#宠物之灵属性
		for pos, coding in pet.soul_dict.iteritems():
			soulConfig = PetConfig.PET_SOUL_BASE.get(coding)
			if not soulConfig:
				continue
			
			#攻击属性需要特殊判断
			if pos == 1:
				if PropertyEnum.attack_p in pet.property_dict:
					soulPropertyDict[PropertyEnum.attack_p] = int(pet.property_dict[PropertyEnum.attack_p] * soulConfig.propertyPercentage / 100)
				elif PropertyEnum.attack_m in pet.property_dict:
					soulPropertyDict[PropertyEnum.attack_m] = int(pet.property_dict[PropertyEnum.attack_m] * soulConfig.propertyPercentage / 100)
				
				continue
			
			#其它属性
			propertyEnum = PetConfig.PET_SOUL_POS_TO_PROPERTY_ENUM.get(pos)
			if not propertyEnum:
				continue
			soulPropertyDict[propertyEnum] = int(pet.property_dict[propertyEnum] * soulConfig.propertyPercentage / 100)
			
		return soulPropertyDict
			
	def save(self):
		petDict = self.role.GetObj(EnumObj.Pet)
		
		for petId, petObj in self.pet_dict.iteritems():
			d = {}
			if petId in petDict:
				d = petDict[petId]
				
			d[TYPE_INDEX] = petObj.type
			d[STAR_INDEX] = petObj.star
			d[HEROID_INDEX] = petObj.hero_id
			d[EVOLUTION_INDEX] = petObj.evoId
			d[EVOEXP_INDEX] = petObj.evoExp
			d[EVOLUCK_INDEX] = petObj.evoluck
			d[SHAPEID_INDEX] = petObj.shapeId
			
			d[PROPERTY_INDEX] = petObj.property_dict
			d[LUCKY_INDEX] = petObj.lucky_dict
			d[SOUL_INDEX] = petObj.soul_dict
			
			petDict[petId] = d

def RecountPropertyByPet(role, pet):
	'''
	重算宠物属性
	@param role:
	@param pet:
	'''
	#宠物没有被佩戴
	if not pet.hero_id:
		return
	
	if pet.hero_id == role.GetRoleID():
		#重算主角属性
		role.GetPropertyGather().ReSetRecountPetFlag()
	else:
		hero = role.GetHero(pet.hero_id)
		if not hero:
			return
		#重算英雄属性
		hero.GetPropertyGather().ReSetRecountPetFlag()

def RecountEvoPropertyByPet(role, pet):
	#重算宠物进化的属性
	#宠物没有被佩戴
	if not pet.hero_id:
		return
	
	if pet.hero_id == role.GetRoleID():
		#重算主角属性
		role.GetPropertyGather().ReSetRecountPetRvoFlag()
	else:
		hero = role.GetHero(pet.hero_id)
		if not hero:
			return
		#重算英雄属性
		hero.GetPropertyGather().ReSetRecountPetRvoFlag()
