#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QSaveDeskTop")
#===============================================================================
# 游戏桌面保存领取奖励
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumInt1



def RequestQSaveDeskTop(role, msg):
	'''
	游戏桌面保存领取奖励
	@param role:
	@param msg:
	'''
	if role.GetI1(EnumInt1.QSaveDeskTop_Flag):
		return
	if role.PackageEmptySize() < len(EnumGameConfig.QSaveItems):
		role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
		return
	tips = GlobalPrompt.Reward_Tips
	with TraQSaveDeskTop:
		role.SetI1(EnumInt1.QSaveDeskTop_Flag, True)
		
		role.IncBindRMB(EnumGameConfig.QSaveBindRMB)
		tips += GlobalPrompt.BindRMB_Tips % EnumGameConfig.QSaveBindRMB
		
		for itemCoding, cnt in EnumGameConfig.QSaveItems:
			role.AddItem(itemCoding, cnt)
			tips += GlobalPrompt.Item_Tips % (itemCoding, cnt)
	
	role.Msg(2, 0, tips)

if "_HasLoad" not in dir():
	if Environment.EnvIsQQ() and not Environment.IsCross and Environment.HasLogic:
		TraQSaveDeskTop = AutoLog.AutoTransaction("TraQSaveDeskTop", "游戏桌面保存领取奖励")
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QSaveDeskTop", "游戏桌面保存领取奖励"), RequestQSaveDeskTop)
	