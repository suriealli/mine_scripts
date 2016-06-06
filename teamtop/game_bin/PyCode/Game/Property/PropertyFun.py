#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Property.PropertyFun")
#===============================================================================
# 属性相关角色接口
#===============================================================================
from Game.Role.Data import EnumTempObj


def GetPropertyMgr(role):
	'''获取角色属性管理器'''
	return role.GetTempObj(EnumTempObj.PM)

def GetPropertyGather(role):
	'''获取主角属性集合'''
	return role.GetTempObj(EnumTempObj.PM).role_propertyGather


def CreateHeroProperty(role, hero):
	'''创建一个英雄属性集合'''
	return role.GetTempObj(EnumTempObj.PM).CreateHeroProperty(hero)

def RemoveHeroProperty(role, heroId):
	'''移除一个英雄的属性集合'''
	role.GetTempObj(EnumTempObj.PM).RemoveHeroProperty(heroId)


def PropertyIsValid(role):
	'''属性是否已经生效了'''
	return role.GetTempObj(EnumTempObj.PM).PropertyIsValid()

def SyncAllProperty(role):
	'''同步所有的属性'''
	return role.GetTempObj(EnumTempObj.PM).SyncAllProperty()





def ResetGlobalHelpStationProperty(role):
	'''设置全局助阵属性重算'''
	role.GetTempObj(EnumTempObj.PM).ResetGlobalHelpStationProperty()

def ResetGlobalMountProperty(role):
	'''设置全局坐骑属性重算'''
	role.GetTempObj(EnumTempObj.PM).ResetGlobalMountProperty()

def ResetGlobalMountAppProperty(role):
	'''设置全局坐骑外形品质属性重算'''
	role.GetTempObj(EnumTempObj.PM).ResetGlobalMountAppProperty()
	
def ResetGlobalDragonProperty(role):
	'''设置全局神龙属性重算'''
	role.GetTempObj(EnumTempObj.PM).ResetGlobalDragonProperty()

def ResetGlobalWingProperty(role):
	'''设置全局翅膀属性重算'''
	role.GetTempObj(EnumTempObj.PM).ResetGlobalWingProperty()

def ResetAllTarotProperty(role):
	'''设置所有的占卜属性重算(特殊)'''
	role.GetTempObj(EnumTempObj.PM).ResetAllTarotProperty()

def ResetGlobalWeddingRingProperty(role):
	'''设置全局婚戒属性重算'''
	role.GetTempObj(EnumTempObj.PM).ResetGlobalWeddingRingProperty()
	
def ResetGlobalWeddingRingSProperty(role):
	'''设置全局婚戒戒灵属性重算'''
	role.GetTempObj(EnumTempObj.PM).ResetGlobalWeddingRingSProperty()

def ResetGlobalWeddingRingSkillProperty(role):
	'''设置全局夫妻技能属性重算'''
	role.GetTempObj(EnumTempObj.PM).ResetGlobalWeddingRingSkillProperty()

def ResetGlobalFashionProperty(role):
	'''设置全局时装鉴定属性重算'''
	role.GetTempObj(EnumTempObj.PM).ResetGlobalFashionProperty()
	
def ResetGlobalQinmiProperty(role):
	'''设置全局亲密等级属性重算'''
	role.GetTempObj(EnumTempObj.PM).ResetGlobalQinmiProperty()
	
def ResetGlobalQinmiGradeProperty(role):
	'''设置全局亲密品阶属性重算'''
	role.GetTempObj(EnumTempObj.PM).ResetGlobalQinmiGradeProperty()

def ResetTitleProperty(role):
	'''设置称号属性重算'''
	role.GetTempObj(EnumTempObj.PM).ResetGlobalTitleTeamProperty()
	role.GetPropertyGather().ResetRecountTitleRoleFlag()

def ResetMarryRingProperty(role):
	'''设置订婚戒指属性重算'''
	role.GetTempObj(EnumTempObj.PM).ResetGlobalMarryRingProperty()

def ResetStationSoulProperty(role):
	'''设置阵灵属性重算'''
	role.GetTempObj(EnumTempObj.PM).ResetGlobalStationSoulBaseProperty()
	role.GetTempObj(EnumTempObj.PM).ResetGlobalStationSoulPPTProperty()

def ResetGlobalStationSoulItemProperty(role):
	'''设置重算阵灵强化石属性'''
	role.GetTempObj(EnumTempObj.PM).ResetGlobalStationSoulItemProperty()
	
def ResetGlobalWStationBaseProperty(role):
	'''重算战阵基础属性'''
	role.GetTempObj(EnumTempObj.PM).ResetGlobalWStationBaseProperty()
	
def ResetGlobalWStationThousandProperty(role):
	'''重算战阵万分比属性'''
	role.GetTempObj(EnumTempObj.PM).ResetGlobalWStationThousandProperty()

def ResetGlobalWStationItemProperty(role):
	'''重算战阵战魂石属性'''
	role.GetTempObj(EnumTempObj.PM).ResetGlobalWStationItemProperty()
	
def ResetGlobalZhuanShengHaloBaseProperty(role):
	'''重算转身光环基础 属性'''
	role.GetTempObj(EnumTempObj.PM).ResetGlobalZhuanShengHaloBaseProperty()
	
def ResetGlobalCardAtlasProperty(role):
	'''重算卡牌图鉴属性'''
	role.GetTempObj(EnumTempObj.PM).ResetGlobalCardAtlasProperty()

def ResetElementSpiritProperty(role):
	'''设置元素之灵属性重算'''
	role.GetTempObj(EnumTempObj.PM).ResetGlobalElementSpiritBaseProperty()
	role.GetTempObj(EnumTempObj.PM).ResetGlobalElementSpiritPPTProperty()

def ResetElementBrandBaseProperty(role):
	'''设置元素印记基本属性重算'''
	role.GetTempObj(EnumTempObj.PM).ResetGlobalElementBrandBaseProperty()
	role.GetTempObj(EnumTempObj.PM).ResetGlobalElementBrandWashProperty()

def ResetSealProperty(role):
	'''设置圣印属性重算'''
	role.GetTempObj(EnumTempObj.PM).ResetGlobalSealBaseProperty()
	role.GetTempObj(EnumTempObj.PM).ResetGlobalSealPPTProperty()
