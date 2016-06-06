#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.StepByStep.StepByStep")
#===============================================================================
# 步步高升（这个只有繁体版有哦 ）
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumInt8
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Activity.StepByStep import StepByStepConfig

if "_HasLoad" not in dir():
	Tra_StepByStep_OpenChest = AutoLog.AutoTransaction("Tra_StepByStep_OpenChest", "步步高升打开宝箱")

def RequestOpenChest(role, msg):
	'''
	步步高升请求打开宝箱
	'''
	#等级限制
	if role.GetLevel() < EnumGameConfig.StepByStep_NeedLevel:
		return
	elderIndex = role.GetI8(EnumInt8.StepByStepChestIndex)
	newerIndex = msg
	
	if elderIndex >= EnumGameConfig.StepByStepMaxChestIndex:
		return
	if newerIndex != elderIndex + 1:
		return
	
	config = StepByStepConfig.StepByStepConfigDict.get(newerIndex, None)
	if config == None:
		print "GE_EXC, error while config = StepByStepConfig.StepByStepConfigDict.get(newerIndex, None), no such newerIndex(%s)" % newerIndex
		return
	
	#神石不足
	price = config.price
	if role.GetUnbindRMB_Q() < price:
		return
	Tips = GlobalPrompt.StepByStepTips
	with Tra_StepByStep_OpenChest:
		#扣除神石，只能是充值神石
		role.DecUnbindRMB_Q(price)
		#设置玩家已经打开的宝箱的index
		role.SetI8(EnumInt8.StepByStepChestIndex, newerIndex)

		if config.items:
			for item in config.items:
				role.AddItem(*item)
				Tips += GlobalPrompt.Item_Tips % item
				
		if config.unbindRMB:
			role.IncUnbindRMB_S(config.unbindRMB)
			Tips += GlobalPrompt.UnBindRMB_Tips % config.unbindRMB
			
		if config.bindRMB:
			role.IncBindRMB(config.bindRMB)
			Tips += GlobalPrompt.BindRMB_Tips % config.bindRMB
			
		if config.money:
			role.IncMoney(config.money)
			Tips += GlobalPrompt.Money_Tips % config.money
	
	role.Msg(2, 0, Tips)
	if config.isBroadcast:
		role_name = role.GetRoleName()
		chest_name = config.name
		cRoleMgr.Msg(11, 0, GlobalPrompt.StepByStepBroadCast % (role_name, chest_name))

if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.EnvIsFT() or Environment.IsDevelop) and not Environment.IsCross:
		#注册消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("StepByStep_RequestOpenChest", "客户端请求打开步步高升宝箱"), RequestOpenChest)
