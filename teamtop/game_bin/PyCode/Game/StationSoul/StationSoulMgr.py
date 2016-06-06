#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.StationSoul.StationSoulMgr")
#===============================================================================
# 阵灵 Mgr
#===============================================================================
import cRoleMgr
import cDateTime
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.StationSoul import StationSoulConfig
from Game.Role.Data import EnumInt16, EnumInt32, EnumTempInt64

ONEDAY_SEC = 24 * 60 * 60

if "_HasLoad" not in dir():
	Tra_StationSoul_Upgrade = AutoLog.AutoTransaction("Tra_StationSoul_Upgrade", "阵灵系统_阵灵升级")
	Tra_StationSoul_Break = AutoLog.AutoTransaction("Tra_StationSoul_Break", "阵灵系统_阵灵突破")
	Tra_StationSoul_OneKeyBreak = AutoLog.AutoTransaction("Tra_StationSoul_OneKeyBreak", "阵灵系统_阵灵一键突破")
	Tra_StationSoul_TimeOutClear = AutoLog.AutoTransaction("Tra_StationSoul_TimeOutClear", "阵灵系统_超时清除阵灵突破进度值")
	
def OnUpgrade(role, msg = None):
	'''
	阵灵系统_请求阵灵升级
	msg = isAutoRMB 材料不足是否消耗神石
	'''
	if role.GetLevel() < EnumGameConfig.StationSoul_NeedLevel:
		return
	
	nowStationSoulId = role.GetI16(EnumInt16.StationSoulId)
	nowCfg = StationSoulConfig.StationSoul_BaseConfig_Dict.get(nowStationSoulId)
	if not nowCfg:
		return
	
	#最大等级 or 需要突破
	if (not nowCfg.nextSSId) or nowCfg.canBreak:
		return
	
	#战魂等级不足
	nowWarStationId = role.GetI16(EnumInt16.WarStationStarNum)
	if nowWarStationId < nowCfg.needWarStationId:
		return
	
	#材料不足 && 未选择自动消耗神石
	backId, isAutoRMB = msg
	needCoding, needCnt = nowCfg.upgradeItem
	haveNomalCnt = role.ItemCnt(needCoding)
	haveOtherCnt = role.ItemCnt_NotTimeOut(nowCfg.otherItemCoding)
	
	
	needRMB = 0
	needNomalCnt = 0
	needOtherCnt = 0
	if (haveNomalCnt + haveOtherCnt) < needCnt:
		#材料不够
		if isAutoRMB:
			#神石代替
			needOtherCnt = haveOtherCnt
			needNomalCnt = haveNomalCnt
			needRMB = (needCnt - haveOtherCnt - haveNomalCnt) * nowCfg.price
		else:
			return
	else:
		#材料足够 优先消耗临时道具
		needOtherCnt = min(haveOtherCnt, needCnt)
		needNomalCnt = max(needCnt - haveOtherCnt,0)
		
	#再次验证 最后确保(至少需要消耗代价)
	if not (needNomalCnt > 0 or needOtherCnt > 0 or needRMB > 0):
		return
	
	if role.GetUnbindRMB_Q() < needRMB:
		return
	
	prompt = GlobalPrompt.StationSoul_Tips_Upgrade_Head
	with Tra_StationSoul_Upgrade:
		#消耗常规材料
		if needNomalCnt > 0:
			role.DelItem(needCoding, needNomalCnt)
		#消耗时效材料
		if needOtherCnt > 0:
			role.DelItem(nowCfg.otherItemCoding, needOtherCnt)
		#消耗神石
		if needRMB > 0:
			role.DecUnbindRMB_Q(needRMB)
		#处理升星成功 更新
		newId = nowCfg.nextSSId
		role.SetI16(EnumInt16.StationSoulId, newId)
		#触发阵灵改变事件
		Event.TriggerEvent(Event.Eve_AfterChangeStationSoul, role, None)
		#处理属性升级
		role.ResetStationSoulProperty()
	
	role.Msg(2, 0, prompt)
	role.CallBackFunction(backId, None)
	
	
def OnBreak(role, msg = None):
	'''
	阵灵系统_请求阵灵突破
	msg = isAutoRMB 材料不足是否消耗神石
	'''
	if role.GetLevel() < EnumGameConfig.StationSoul_NeedLevel:
		return
	
	nowStationSoulId = role.GetI16(EnumInt16.StationSoulId)
	nowCfg = StationSoulConfig.StationSoul_BaseConfig_Dict.get(nowStationSoulId)
	if not nowCfg:
		return
	
	#最大等级 or 不可突破
	if (not nowCfg.nextSSId) or (not nowCfg.canBreak):
		return
	
	nowWarStationId = role.GetI16(EnumInt16.WarStationStarNum)
	if nowWarStationId < nowCfg.needWarStationId:
		return
	
	#材料不足 && 未选择自动消耗神石
	backId, isAutoRMB = msg
	needCoding, needCnt, incExp, totalExp = nowCfg.breakItem
	haveNomalCnt = role.ItemCnt(needCoding)
	haveOtherCnt = role.ItemCnt_NotTimeOut(nowCfg.otherItemCoding)
	
	
	needRMB = 0
	needNomalCnt = 0
	needOtherCnt = 0
	if (haveNomalCnt + haveOtherCnt) < needCnt:
		#材料不够
		if isAutoRMB:
			#神石代替
			needOtherCnt = haveOtherCnt
			needNomalCnt = haveNomalCnt
			needRMB = (needCnt - haveOtherCnt - haveNomalCnt) * nowCfg.price
		else:
			return
	else:
		#材料足够 优先消耗临时道具
		needOtherCnt = min(haveOtherCnt, needCnt)
		needNomalCnt = max(needCnt - haveOtherCnt,0)
		
	#再次验证 最后确保(至少需要消耗代价)
	if not (needNomalCnt > 0 or needOtherCnt > 0 or needRMB > 0):
		return
	
	if role.GetUnbindRMB_Q() < needRMB:
		return
	
	isBreak = False
	nowExp = role.GetI16(EnumInt16.StationSoulExp)
	with Tra_StationSoul_Break:
		#消耗材料
		if needNomalCnt > 0:
			role.DelItem(needCoding, needNomalCnt)
		#消耗时效材料
		if needOtherCnt > 0:
			role.DelItem(nowCfg.otherItemCoding, needOtherCnt)
		#消耗神石
		if needRMB > 0:
			role.DecUnbindRMB_Q(needRMB)
		#增加突破值 or 处理突破成功
		if nowExp + incExp >= totalExp:
			isBreak = True
			#阵灵ID升级
			role.SetI16(EnumInt16.StationSoulId, nowCfg.nextSSId)
			#触发阵灵改变事件
			Event.TriggerEvent(Event.Eve_AfterChangeStationSoul, role, None)
			#清除突破值
			role.SetI16(EnumInt16.StationSoulExp, 0)
			#处理属性升级
			role.ResetStationSoulProperty()
		else:
			role.IncI16(EnumInt16.StationSoulExp, incExp)
		#处理进度值超时时间戳
		if nowExp == 0 and not isBreak:
			lastSecs = cDateTime.Seconds() + ONEDAY_SEC
			role.SetI32(EnumInt32.StationSoulTempExpLastSecs, lastSecs)
			role.SetTI64(EnumTempInt64.StationSoulExpTickId, role.RegTick(ONEDAY_SEC, ClearBreakExp))
	
	#分别提示 
	if isBreak:
		oldGrade = nowCfg.gradeLevel		
		cRoleMgr.Msg(11, 0, GlobalPrompt.StationSoul_Tips_BreakSucceed % (role.GetRoleName(), oldGrade, oldGrade + 1))
	else:
		role.Msg(2, 0, GlobalPrompt.StationSoul_Tips_BreakFailed % incExp)
	
	#分别回调
	role.CallBackFunction(backId, isBreak)

def OnOneKeyBreak(role, msg = None):
	'''
	阵灵系统_请求阵灵一键突破
	msg = isAutoRMB 材料不足是否消耗神石
	'''
	if role.GetLevel() < EnumGameConfig.StationSoul_NeedLevel:
		return
	
	nowStationSoulId = role.GetI16(EnumInt16.StationSoulId)
	nowCfg = StationSoulConfig.StationSoul_BaseConfig_Dict.get(nowStationSoulId)
	if not nowCfg:
		return
	
	#最大等级 or 不可突破
	if (not nowCfg.nextSSId) or (not nowCfg.canBreak):
		return
	
	nowWarStationId = role.GetI16(EnumInt16.WarStationStarNum)
	if nowWarStationId < nowCfg.needWarStationId:
		return
	
	#材料不足 && 未选择自动消耗神石
	backId, isAutoRMB = msg
	needCoding, needCnt, incExp, totalExp = nowCfg.breakItem
	nowExp = role.GetI16(EnumInt16.StationSoulExp)
	needExp = totalExp - nowExp
	#向上取整 计算所需材料总数
	needTotalCnt = needCnt * ((needExp + incExp - 1) / incExp)
	haveNomalCnt = role.ItemCnt(needCoding)
	haveOtherCnt = role.ItemCnt_NotTimeOut(nowCfg.otherItemCoding)
	
	
	needRMB = 0
	needNomalCnt = 0
	needOtherCnt = 0
	if (haveNomalCnt + haveOtherCnt) < needTotalCnt:
		#材料不够
		if isAutoRMB:
			#神石代替
			needOtherCnt = haveOtherCnt
			needNomalCnt = haveNomalCnt
			needRMB = (needTotalCnt - haveOtherCnt - haveNomalCnt) * nowCfg.price
		else:
			return
	else:
		#材料足够 优先消耗临时道具
		needOtherCnt = min(haveOtherCnt, needTotalCnt)
		needNomalCnt = max(needTotalCnt - haveOtherCnt,0)
		
	#再次验证 最后确保(至少需要消耗代价)
	if not (needNomalCnt > 0 or needOtherCnt > 0 or needRMB > 0):
		return
	
	if role.GetUnbindRMB_Q() < needRMB:
		return
	
	with Tra_StationSoul_OneKeyBreak:
		#消耗材料
		if needNomalCnt > 0:
			role.DelItem(needCoding, needNomalCnt)
		#消耗时效材料
		if needOtherCnt > 0:
			role.DelItem(nowCfg.otherItemCoding, needOtherCnt)
		#消耗神石
		if needRMB > 0:
			role.DecUnbindRMB_Q(needRMB)
		#处理升级 & 清空突破值
		role.SetI16(EnumInt16.StationSoulId, nowCfg.nextSSId)
		#触发阵灵改变事件
		Event.TriggerEvent(Event.Eve_AfterChangeStationSoul, role, None)
		role.SetI16(EnumInt16.StationSoulExp, 0)
		role.UnregTick(role.GetTI64(EnumTempInt64.StationSoulExpTickId))
		role.SetI32(EnumInt32.StationSoulTempExpLastSecs, 0)
		role.ResetStationSoulProperty()
	
	oldGrade = nowCfg.gradeLevel		
	cRoleMgr.Msg(11, 0, GlobalPrompt.StationSoul_Tips_BreakSucceed % (role.GetRoleName(), oldGrade, oldGrade + 1))
	role.CallBackFunction(backId, None)
	

#事件start
def ClearBreakExp(role, param = None):
	'''
	超时清除进阶进度值
	'''
	with Tra_StationSoul_TimeOutClear:
		role.SetI16(EnumInt16.StationSoulExp, 0)
		role.SetI32(EnumInt32.StationSoulTempExpLastSecs, 0)
		role.SetTI64(EnumTempInt64.StationSoulExpTickId, 0)
	

def AfterLogin(role, param = None):
	'''
	玩家上线处理 判断是否超时清除进度值 否则注册tick
	'''
	lastSecs = role.GetI32(EnumInt32.StationSoulTempExpLastSecs)
	if not lastSecs:
		return
	
	nowSecs = cDateTime.Seconds()
	if nowSecs >= lastSecs:
		ClearBreakExp(role)
	else:
		#注销老的tickId
		oldTickId = role.GetTI64(EnumTempInt64.StationSoulExpTickId)
		role.UnregTick(oldTickId)
		#计算并注册新的tick
		role.SetTI64(EnumTempInt64.StationSoulExpTickId, role.RegTick(lastSecs - nowSecs, ClearBreakExp))
	
def BeforeExit(role, param = None):
	'''
	角色掉线 注销tick
	'''
	oldTickId = role.GetTI64(EnumTempInt64.StationSoulExpTickId)
	if oldTickId:
		role.UnregTick(oldTickId)

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_BeforeExit, BeforeExit)
		
	
	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("StationSoul_OnUpgrade", "阵灵系统_请求阵灵升级"), OnUpgrade)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("StationSoul_OnBreak", "阵灵系统_请求阵灵突破"), OnBreak)		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("StationSoul_OnOneKeyBreak", "阵灵系统_请求阵灵一键突破"), OnOneKeyBreak)
