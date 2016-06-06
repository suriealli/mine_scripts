#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Item.ItemUse.ItemUseMgr")
#===============================================================================
# 注册物品使用函数的修饰器
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumTempObj
from ComplexServer import Init



###########################################################################################
def OnUseItem(role, msg):
	'''
	客户端请求使用物品
	@param role:
	@param msg:(物品ID,物品数量)
	'''
	itemId, cnt = msg
	if cnt < 1:
		print "GE_EXC, role use item cnt < 1 (%s)" % role.GetRoleID()
		role.WPE(11)
		return

	packMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	item = packMgr.objIdDict.get(itemId)
	if not item : return
	
	#不是普通物品不能使用
	if item.cfg.ITEM_R != 1 : return
	#配置了不能使用
	if not item.cfg.canUse : return
	#使用等级不够
	if item.cfg.useLevel > role.GetLevel() : return
	#数量不对
	if item.oint < cnt : return
	#已经过期了
	if item.IsDeadTime() : return
	#需要钥匙
	if item.cfg.useNeedItem:
		if role.ItemCnt(item.cfg.useNeedItem) < 1:
			return
	#使用调用函数
	if item.cfg.useFun is None:
		#print "GE_EXC, OnUseItem error not usefun (%s)" % item.otype
		return
	with TraUseItem:
		#调用函数
		item.cfg.useFun(role, item, cnt)


def OnServerUp():
	from Game.Item import ItemConfig
	for itemCoding, itemcfg in ItemConfig.ItemCfg_Dict.iteritems():
		if itemcfg.ITEM_R != 1:
			continue
		if not itemcfg.canUse:
			continue
		if itemcfg.useFun:
			continue
		if itemcfg.doubleclick != "0":
			continue
		
		print "GE_EXC, can use item but not use fun (%s)  (%s)" % (itemCoding, itemcfg.doubleclick)
	

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		TraUseItem = AutoLog.AutoTransaction("TraUseItem", "使用物品")
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Item_Use", "使用物品"), OnUseItem)

	if Environment.HasLogic and  not Environment.IsCross and Environment.IsDevelop:
		Init.InitCallBack.RegCallbackFunction(OnServerUp)

