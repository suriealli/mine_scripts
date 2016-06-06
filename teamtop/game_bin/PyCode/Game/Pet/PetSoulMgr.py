#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Pet.PetSoulMgr")
#===============================================================================
# 宠物附灵
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Pet import PetConfig, PetBase
from Game.Role.Data import EnumTempObj

if "_HasLoad" not in dir():
	#消息
	Pet_Show_All_Soul = AutoMessage.AllotMessage("Pet_Show_All_Soul", "通知客户端显示所有宠物之灵")

def PetSoulOn(role, petId, soulCoding):
	petMgr = role.GetTempObj(EnumTempObj.PetMgr)
	
	#是否有对应宠物
	if petId not in petMgr.pet_dict:
		return
	
	#是否有对应的宠物之灵
	itemCnt = role.ItemCnt(soulCoding)
	if itemCnt == 0:
		return
	
	#是否有对应的宠物之灵配置
	petSoulConfig = PetConfig.PET_SOUL_BASE.get(soulCoding)
	if not petSoulConfig:
		return
	
	#用宠物ID索引宠物
	pet = petMgr.pet_dict[petId]
	
	pos = petSoulConfig.position
	#宠物身上对应位置是否已经佩戴了宠物之灵
	if pos in pet.soul_dict:
		coding = pet.soul_dict[pos]
		#先删除身上的宠物之灵
		del pet.soul_dict[pos]
		#再获得对应的宠物之灵物品
		role.AddItem(coding, 1)
	
	#删除背包里的宠物之灵
	role.DelItem(soulCoding, 1)
	
	#佩戴宠物之灵
	pet.soul_dict[pos] = soulCoding
	
	#重算属性
	PetBase.RecountPropertyByPet(role, pet)
	
	#同步客户端
	role.SendObj(Pet_Show_All_Soul, (petId, pet.soul_dict.values()))
	
	#提示
	role.Msg(2, 0, GlobalPrompt.PET_SOUL_ON_SUCCESS_PROMPT)
	
def PetSoulOff(role, petId, pos):
	petMgr = role.GetTempObj(EnumTempObj.PetMgr)
	
	#是否有对应宠物
	if petId not in petMgr.pet_dict:
		return
	
	#用宠物ID索引宠物
	pet = petMgr.pet_dict[petId]
	
	#宠物身上对应位置是否已经佩戴了宠物之灵
	if pos not in pet.soul_dict:
		return
	
	petSoulCoding = pet.soul_dict[pos]
	#先删除身上的宠物之灵
	del pet.soul_dict[pos]
	#再获得对应的宠物之灵物品
	role.AddItem(petSoulCoding, 1)
	
	#重算属性
	PetBase.RecountPropertyByPet(role, pet)
	
	#同步客户端
	role.SendObj(Pet_Show_All_Soul, (petId, pet.soul_dict.values()))
	
	#提示
	role.Msg(2, 0, GlobalPrompt.PET_SOUL_OFF_SUCCESS_PROMPT)

def PetSoulUpgrade(role, petId, pos):
	petMgr = role.GetTempObj(EnumTempObj.PetMgr)
	
	#是否有对应宠物
	if petId not in petMgr.pet_dict:
		return
	
	#用宠物ID索引宠物
	pet = petMgr.pet_dict[petId]
	
	#宠物身上对应位置是否已经佩戴了宠物之灵
	if pos not in pet.soul_dict:
		return
	
	petSoulCoding = pet.soul_dict[pos]
	
	#是否有对应的宠物之灵配置
	petSoulConfig = PetConfig.PET_SOUL_BASE.get(petSoulCoding)
	if not petSoulConfig:
		return
	
	#是否可以升级
	if petSoulConfig.nextLevelCoding == 0:
		return
	
	#是否有足够的升级材料
	for coding, cnt in petSoulConfig.upgradeNeedItemList:
		itemCnt = role.ItemCnt(coding)
		if itemCnt < cnt:
			return
		
	#扣除升级材料
	for item in petSoulConfig.upgradeNeedItemList:
		role.DelItem(*item)
		
	#升级
	pet.soul_dict[pos] = petSoulConfig.nextLevelCoding
	
	#重算属性
	PetBase.RecountPropertyByPet(role, pet)
	
	#同步客户端
	role.SendObj(Pet_Show_All_Soul, (petId, pet.soul_dict.values()))
	
	#提示
	role.Msg(2, 0, GlobalPrompt.PET_SOUL_UPGRADE_SUCCESS_PROMPT)
	#北美通用活动
	if Environment.EnvIsNA():
		HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
		HalloweenNAMgr.PetSpiritLevel(petSoulConfig.nextLevelCoding)
#===============================================================================
# 客户端请求
#===============================================================================
def RequestPetSoulOn(role, msg):
	'''
	客户端请求佩戴宠物之灵
	@param role:
	@param msg:
	'''
	petId, soulCoding = msg
	
	#日志
	with TraPetSoulOn:
		PetSoulOn(role, petId, soulCoding)
	
def RequestPetSoulOff(role, msg):
	'''
	客户端请求卸下宠物之灵
	@param role:
	@param msg:
	'''
	petId, pos = msg
	
	#日志
	with TraPetSoulOff:
		PetSoulOff(role, petId, pos)
	
def RequestPetSoulUpgrade(role, msg):
	'''
	客户端请求宠物之灵升级
	@param role:
	@param msg:
	'''
	petId, pos = msg
	
	#日志
	with TraPetSoulUpgrade:
		PetSoulUpgrade(role, petId, pos)

if "_HasLoad" not in dir():
	#日志
	TraPetSoulOn = AutoLog.AutoTransaction("TraPetSoulOn", "宠物之灵佩戴")
	TraPetSoulOff = AutoLog.AutoTransaction("TraPetSoulOff", "宠物之灵卸下")
	TraPetSoulUpgrade = AutoLog.AutoTransaction("TraPetSoulUpgrade", "宠物之灵升级")
	
	#消息
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Pet_Soul_On", "客户端请求佩戴宠物之灵"), RequestPetSoulOn)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Pet_Soul_Off", "客户端请求卸下宠物之灵"), RequestPetSoulOff)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Pet_Soul_Upgrade", "客户端请求宠物之灵升级"), RequestPetSoulUpgrade)
	
	