#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ChangeRoleGender.ChangeRoleGender")
#===============================================================================
# 变性系统
#===============================================================================
import cRoleMgr
import Environment
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Game.Role import Event
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Role.Data import EnumInt8

if "_HasLoad" not in dir():
	

	#日志
	Tra_changeRoleGenderSuccessfully  = AutoLog.AutoTransaction("Tra_changeRoleGenderSuccessfully", "变性成功")
	
def RequestChangeGender(role, msg):
	'''
	客户端请求变性
	@param role:
	@param param:
	'''
	#判断婚姻状态
	if role.GetI8(EnumInt8.MarryStatus) != 0:
		role.Msg(2, 0, GlobalPrompt.ChangeRoleGender_Tips1)
		return
	if role.GetLevel() < EnumGameConfig.ChangeGenderNeedLevel:
		return
	if role.ItemCnt(EnumGameConfig.ChangeGenderCardCode) < 1:
		return
	#完成变性记录日志
	with Tra_changeRoleGenderSuccessfully: 
		if role.DelItem(EnumGameConfig.ChangeGenderCardCode, 1) < 1:
			return
		oldgender = role.GetSex()
		newgender = role.ChangeSex()
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveChangeRoleGender, (oldgender, newgender))
		#触发事件
		Event.TriggerEvent(Event.Eve_RoleChangeGender, role, None)

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestChangeGender", "客户端请求变性"), RequestChangeGender)
