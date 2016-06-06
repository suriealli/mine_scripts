#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Item.FunGather")
#===============================================================================
# role 物品相关接口
#===============================================================================
from Game.Role.Data import EnumTempObj

def AddItem(role, coding, cnt):
	'''将一个物品加入背包 (coding, cnt)'''
	packMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	return packMgr.AddItem(coding, cnt)


def DelItem(role, coding, cnt):
	'''将一个物品从背包删除 (coding, cnt) 返回真正删除的个数'''
	packMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	return packMgr.DelItem(coding, cnt)

def DelProp(role, propId):
	'''将一个道具从背包删除 (propId) 返回是否删除成功'''
	packMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	return packMgr.DelProp(propId)

# 等下干掉
def DecPropCnt(role, prop, cnt):
	packMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	return packMgr.DecPropCnt(prop, cnt)

def ItemCnt(role, coding):
	'''获取物品数量 (coding) 返回物品数量'''
	packMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	return packMgr.ItemCnt(coding)

def ItemCnt_NotTimeOut(role, coding):
	'''获取物品数量 (coding) 返回还没有过期的物品数量  '''
	packMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	return packMgr.ItemCnt_NotTimeOut(coding)

def FindPackProp(role, propId):
	'''根据道具id，获取背包中的道具 返回道具对象或者None'''
	packMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	return packMgr.FindProp(propId)


def FindItem(role, coding):
	'''根据道具coding，获取背包中的道具 返回道具对象或者None'''
	packMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	return packMgr.FindItem(coding)

def PackageIsFull(role):
	'''判断背包是否满'''
	packMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	return packMgr.IsFull()

def PackageEmptySize(role):
	'''获取背包空格子数'''
	packMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	return packMgr.EmptySize()


def FindGlobalProp(role, propId):
	'''根据道具id，查询一个全局的物品'''
	return role.GetTempObj(EnumTempObj.enGlobalItemMgr).get(propId)
	
