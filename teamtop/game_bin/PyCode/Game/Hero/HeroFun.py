#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Hero.HeroFun")
#===============================================================================
# 角色英雄相关接口
#===============================================================================
from Game.Role.Data import EnumTempObj

def GetAllHero(role):
	'''获取所有英雄 英雄id --> 英雄对象'''
	return role.GetTempObj(EnumTempObj.enHeroMgr).HeroDict

def GetHero(role, heroId):
	'''根据英雄id获取英雄对象 返回英雄对象或者None'''
	#根据英雄ID获取英雄对象
	return role.GetTempObj(EnumTempObj.enHeroMgr).HeroDict.get(heroId)
	

