#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQLZ.QQLZShopMgr")
#===============================================================================
# 注释 @author: GaoShuai 2016
#===============================================================================
import cRoleMgr
import Environment
from Game.Role import Event
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Game.Role.Data import EnumTempInt64, EnumObj
from Game.ThirdParty.QQLZ.QQLZShopConfig import QQLZShop_Dict
from Common.Other import GlobalPrompt


if "_HasLoad" not in dir():
	#消息
	QQLZShopData = AutoMessage.AllotMessage("QQLZShopData", "QQ蓝钻商店购买数据")
	#日志
	Tra_QQLZShopConsume = AutoLog.AutoTransaction("Tra_QQLZShopConsume", "QQ蓝钻商店消费")


def IsQQLZ(role):
	return 0 #2016/1/14 屏蔽蓝钻buff和蓝钻商店
	#蓝钻用户在蓝钻渠道登录,返回蓝钻等级
	if role.GetTI64(EnumTempInt64.QVIP) != 2:
		return 0
	return role.GetQQLZ()


def RequestQQLZShopBuy(role, msg):
	'''
	蓝钻商店请求购买
	@param role:
	@param msg: 物品index, 购买数量
	'''
	#判断渠道
	if not IsQQLZ(role):
		return
	buyIndex, buyCnt = msg
	buyObj = QQLZShop_Dict.get(buyIndex)
	if not buyObj:
		return
	minLevel, maxLevel = buyObj.needLevel
	if role.GetLevel() < minLevel or role.GetLevel() > maxLevel :
		return
	
	if buyObj.recharge:
		#充值神石
		if role.GetUnbindRMB_Q() < buyObj.needRMB:
			return
	else:
		if role.GetUnbindRMB() < buyObj.needRMB:
			return
		
	if not role.GetObj(EnumObj.QQLZShopData):
		role.SetObj(EnumObj.QQLZShopData, {})
	ShopDict = role.GetObj(EnumObj.QQLZShopData)
	if ShopDict.get(buyIndex, 0) + buyCnt > buyObj.dayMax:
		return
	#QQ蓝钻商店消费
	with Tra_QQLZShopConsume:
		#删除物品及其他操作
		if buyObj.recharge:
			role.DecUnbindRMB_Q(buyObj.needRMB)
		else:
			role.DecUnbindRMB(buyObj.needRMB)
		itemCoding, cnt = buyObj.item
		role.AddItem(itemCoding, cnt * buyCnt)
	
	ShopDict[buyIndex] = ShopDict.get(buyIndex, 0) + buyCnt
	role.SendObj(QQLZShopData, ShopDict)
	role.Msg(2, 0, GlobalPrompt.Reward_Tips + GlobalPrompt.Item_Tips % (itemCoding, cnt * buyCnt))

def RequestQQLZOpenShop(role, msg):
	'''
	打开蓝钻商店
	@param role:
	@param msg: 
	'''
	if not role.GetObj(EnumObj.QQLZShopData):
		role.SetObj(EnumObj.QQLZShopData, {})
	role.SendObj(QQLZShopData, role.GetObj(EnumObj.QQLZShopData))
	

def QQLZRoleDayClear(role, param):
	'''
	每日数据清理
	@param role:
	@param param:
	'''
	role.SetObj(EnumObj.QQLZShopData, {})


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_RoleDayClear, QQLZRoleDayClear)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestQQLZShopBuy", "蓝钻商店请求购买"), RequestQQLZShopBuy)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestQQLZOpenShop", "打开蓝钻商店"), RequestQQLZOpenShop)
