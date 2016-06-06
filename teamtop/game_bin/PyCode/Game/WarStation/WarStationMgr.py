#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.WarStation.WarStationMgr")
#===============================================================================
# 战阵
#===============================================================================
import Environment
import cRoleMgr
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Role.Data import EnumTempObj, EnumInt16, EnumCD
from Game.WarStation import WarStationBase, WarStationConfig

if "_HasLoad" not in dir():
	ONE_DAY_CD = 24 * 60 * 60	#1天的CD
	TEMP_BREAK_ITEM_ID = 28566	#临时战魂精华
	TEMP_STAR_ITEM_ID = 28565	#临时战魂珠
	#日志
	WarStationUpStarCost = AutoLog.AutoTransaction("WarStationUpStarCost", "战阵升星消耗")
	WarStationBreakCost = AutoLog.AutoTransaction("WarStationBreakCost", "战阵突破消耗")
	WarStationClearProcess = AutoLog.AutoTransaction("WarStationClearProcess", "战阵进度清空")

def RequestUpStationStar(role, param):
	'''
	客户端请求战阵升星
	@param role:
	@param param:
	'''
	isRMB = param
	
	starNum = role.GetI16(EnumInt16.WarStationStarNum)
	
	cfg = WarStationConfig.WAR_STATION_BASE.get(starNum)
	if not cfg:
		print "GE_EXC, can not find starNum(%s) in WarStationMgr.RequestUpStationStar" % starNum
		return
	if cfg.IsMax == 1:#已是最大星级
		return
	if cfg.NextID:#目前只能突破，不能升星
		return
	
	if not cfg.needItem:
		return
	if not cfg.price:
		return
	price = cfg.price
	needCoding, cnt = cfg.needItem
	
	tempCnt = role.ItemCnt_NotTimeOut(TEMP_STAR_ITEM_ID)
	itemCnt = role.ItemCnt(needCoding)
	costRMB = 0
	if tempCnt:#有临时道具
		if cnt > tempCnt:#临时道具小于配置数据
			remainCnt = cnt - tempCnt
			if remainCnt > itemCnt:#临时道具+永久道具小于配置数量
				newCnt = remainCnt - itemCnt
				needRMB = newCnt * price
				if isRMB:#有勾选神石消耗
					if role.GetUnbindRMB_Q() < needRMB:
						return
					else:
						costRMB = needRMB
				else:#直接返回
					return
			else:
				itemCnt = remainCnt
		else:
			tempCnt = cnt
			itemCnt = 0
	else:
		if itemCnt < cnt:
			if isRMB:
				needRMB = (cnt - itemCnt) * price
				if role.GetUnbindRMB_Q() < needRMB:
					return
				else:
					costRMB = needRMB
			else:
				return
		else:
			itemCnt = cnt
	
	with WarStationUpStarCost:
		if tempCnt:
			role.DelItem(TEMP_STAR_ITEM_ID, tempCnt)
		if itemCnt:
			role.DelItem(needCoding, itemCnt)
		if costRMB:
			role.DecUnbindRMB_Q(costRMB)
		#增加战阵星数
		role.IncI16(EnumInt16.WarStationStarNum, 1)
		#重算战阵基础属性
		WarStationMgr = role.GetTempObj(EnumTempObj.WarStationMgr)
		WarStationMgr.ReSetBaseStationPro()
		role.ResetGlobalWStationBaseProperty()
		role.Msg(2, 0, GlobalPrompt.WarStation_UpStar_Msg)
	###################################################################
	#精彩活动战魂培养日活动
	from Game.Activity.LatestActivity import LatestActivityMgr, EnumLatestType
	LatestActivityMgr.GetFunByType(EnumLatestType.ZhanHun_Latest, (role, 1))
	###################################################################
def RequestUpStationBreak(role, param):
	'''
	客户端请求战阵突破
	@param role:
	@param param:
	'''
	isRMB = param
	starNum = role.GetI16(EnumInt16.WarStationStarNum)
	
	cfg = WarStationConfig.WAR_STATION_BASE.get(starNum)
	if not cfg:
		print "GE_EXC, can not find starNum(%s) in WarStationMgr.RequestUpStationStar" % starNum
		return
	if cfg.IsMax:
		return
	if not cfg.NextID:#目前还不能突破
		return
	
	if not cfg.breakItem:
		return
	if not cfg.price:
		return
	price = cfg.price
	needCoding, cnt, progress, totalPrs = cfg.breakItem
	
	tempCnt = role.ItemCnt_NotTimeOut(TEMP_BREAK_ITEM_ID)
	itemCnt = role.ItemCnt(needCoding)
	costRMB = 0
	if tempCnt:#有临时道具
		if cnt > tempCnt:#临时道具小于配置数据
			remainCnt = cnt - tempCnt
			if remainCnt > itemCnt:#临时道具+永久道具小于配置数量
				newCnt = remainCnt - itemCnt
				needRMB = newCnt * price
				if isRMB:#有勾选神石消耗
					if role.GetUnbindRMB_Q() < needRMB:
						return
					else:
						costRMB = needRMB
				else:#无勾选直接返回
					return
			else:
				itemCnt = remainCnt
		else:
			tempCnt = cnt
			itemCnt = 0
	else:
		if itemCnt < cnt:
			if isRMB:
				needRMB = (cnt - itemCnt) * price
				if role.GetUnbindRMB_Q() < needRMB:
					return
				else:
					costRMB = needRMB
			else:
				return
		else:
			itemCnt = cnt
		
	if role.GetCD(EnumCD.WarStationCD) == 0 and role.GetI16(EnumInt16.WarStationTempValue):
		#进度的持续时间已结束，但却有临时进度，直接清空处理
		with WarStationClearProcess:
			role.SetI16(EnumInt16.WarStationTempValue, 0)
			return
	
	if role.GetI16(EnumInt16.WarStationTempValue) >= totalPrs:
		return
	
	with WarStationBreakCost:
		if tempCnt:
			role.DelItem(TEMP_BREAK_ITEM_ID, tempCnt)
		if itemCnt:
			role.DelItem(needCoding, itemCnt)
		if costRMB:
			role.DecUnbindRMB_Q(costRMB)
			
		role.IncI16(EnumInt16.WarStationTempValue, progress)
		if role.GetCD(EnumCD.WarStationCD) == 0:#还没有CD的话就设置个CD
			role.SetCD(EnumCD.WarStationCD, ONE_DAY_CD)
			
		if role.GetI16(EnumInt16.WarStationTempValue) >= totalPrs:#临时进度条满了，突破
			role.IncI16(EnumInt16.WarStationStarNum, 1)
			#清空临时进度
			role.SetI16(EnumInt16.WarStationTempValue, 0)
			#清空CD，假如有的话
			role.SetCD(EnumCD.WarStationCD, 0)
			#重算战阵基础属性
			WarStationMgr = role.GetTempObj(EnumTempObj.WarStationMgr)
			WarStationMgr.ReSetBaseStationPro()
			role.ResetGlobalWStationBaseProperty()
			#重算百分比属性
			WarStationMgr.ReSetThousandPro()
			role.ResetGlobalWStationThousandProperty()
			#公告
			nextCfg = WarStationConfig.WAR_STATION_BASE.get(role.GetI16(EnumInt16.WarStationStarNum))
			if not nextCfg:
				return
			cRoleMgr.Msg(11, 0, GlobalPrompt.WarStation_Msg % (role.GetRoleName(), cfg.grade, nextCfg.grade))
			###################################################################
	#精彩活动战魂培养日活动
	from Game.Activity.LatestActivity import LatestActivityMgr, EnumLatestType
	LatestActivityMgr.GetFunByType(EnumLatestType.ZhanHun_Latest, (role, 1))
	###################################################################
#==========================================
def OnRoleInit(role, param):
	role.SetTempObj(EnumTempObj.WarStationMgr, WarStationBase.WarStationData(role))
	
def OnRoleLogin(role, param):
	if role.GetCD(EnumCD.WarStationCD) > 0:
		WarStationMgr = role.GetTempObj(EnumTempObj.WarStationMgr)
		WarStationMgr.break_tick_id = role.RegTick(60 * 60, TriggerTick)
	
def TriggerTick(role, callargv, regparam):
	if role.IsKick():
		return
	if role.GetCD(EnumCD.WarStationCD):
		WarStationMgr = role.GetTempObj(EnumTempObj.WarStationMgr)
		WarStationMgr.break_tick_id = role.RegTick(60 * 60, TriggerTick)
	else:
		role.SetI16(EnumInt16.WarStationTempValue, 0)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		#角色初始化
		Event.RegEvent(Event.Eve_InitRolePyObj, OnRoleInit)
		#角色登录
		Event.RegEvent(Event.Eve_AfterLogin, OnRoleLogin)
	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("War_Station_UpStar", "客户端请求战阵升星"), RequestUpStationStar)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("War_Station_Break", "客户端请求战阵突破"), RequestUpStationBreak)
		
		
