#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ElementSpirit.ElementalEssenceMgr")
#===============================================================================
# 元素精炼
#===============================================================================
import random
import Environment
import cRoleMgr
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumInt32, EnumDayInt8
from Game.ElementSpirit import ElementalEssenceConfig


if "_HasLoad" not in dir():
	#元素精炼的日志
	ElementalEssence_Log = AutoLog.AutoTransaction("ElementalEssence_Log", "元素精炼日志")


#元素精炼
def ElementalEssence_jinglian(role, ways):
	if ways != 1 and ways != 2:
		return
	#等级不够120
	if role.GetLevel() < EnumGameConfig.ElementalEssenceMinLevel :
		return
	#没有次数
	EssenceTimes = EnumGameConfig.ElementalEssenceTimes - role.GetDI8(EnumDayInt8.ElementalEssenceTimes)
	if EssenceTimes <= 0 :
		return
	ElemntalRadom = ElementalEssenceConfig.ElementalEssenceRandom.get(ways)
	RefineId = ElemntalRadom.RandomOne()
	ElementalAward = ElementalEssenceConfig.ElementalEssence.get(RefineId)
	#不够充值神石
	if ways == 2 and role.GetUnbindRMB() < ElementalAward.Cost:
		return
	with ElementalEssence_Log :
		role.IncDI8(EnumDayInt8.ElementalEssenceTimes, 1)
		#普通精炼
		if ways == 1 :
			minvalue = ElementalAward.MinElementalEssence
			maxvalue = ElementalAward.MaxElementalEssence
			
		#高级精炼
		elif ways == 2 :
			role.DecUnbindRMB(ElementalAward.Cost)
			minvalue = ElementalAward.MinElementalEssence
			maxvalue = ElementalAward.MaxElementalEssence
		IncAmount = random.randint(minvalue, maxvalue)
		role.IncI32(EnumInt32.ElementalEssenceAmount, IncAmount)
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveElementalEssenceTimes, (ways, IncAmount))
	tips = GlobalPrompt.ElementalEssenceAmounts % IncAmount
	role.Msg(2, 0, tips)
	
	


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ElementalEssence_jinglian", "进行元素精炼"), ElementalEssence_jinglian)