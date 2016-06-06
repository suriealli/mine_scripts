#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Hero.HeroAltar")
#===============================================================================
# 英雄祭坛
#===============================================================================
import Environment
import cRoleMgr
import cNetMessage
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt, EnumFightStatistics
from ComplexServer.Log import AutoLog
from Game.Hero import HeroConfig
from Game.Fight import FightEx
from Game.Role import Event, Status
from Game.Role.Data import EnumTempObj, EnumInt1, EnumCD
from Game.Task import EnumTaskType
from Game.Persistence import Contain

if "_HasLoad" not in dir():
	HeroAltarRecord = AutoMessage.AllotMessage("HeroAltarRecord", "英雄祭坛获得英雄记录")
	HeroAltarSingleRecord = AutoMessage.AllotMessage("HeroAltarSingleRecord", "英雄祭坛获得英雄单条记录")
	
	HeroAltarCall_Log = AutoLog.AutoTransaction("HeroAltar_Log", "英雄祭坛点将日志")
	HeroAltarChange_Log = AutoLog.AutoTransaction("HeroAltarChange_Log", "英雄祭坛兑换日志")
	
	#英雄祭坛观察者列表
	HeroAltarObserver = []
	
def GetItemIdNA(role):
	#获取一个没过期的指定道具
	packageMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	codingGatherDict = packageMgr.codingGather.get(EnumGameConfig.NA_HEROALTAR_CODING)
	if not codingGatherDict:
		return 0
	itemId = 0
	for Id, item in codingGatherDict.iteritems():
		if item.IsDeadTime():
			continue
		itemId = Id
		break
	return itemId

def NormalCall(role, index, cfg):
	if role.GetTempObj(EnumTempObj.enHeroMgr).GetHeroCnt() > EnumGameConfig.Hero_Altar_Normal_HeroCnt:
		return
	
	#随机一个阵营ID
	mcid = cfg.normal_call.RandomOne()
	if not mcid:
		return
	
	if role.ItemCnt(cfg.needItem[0]) >= cfg.needItem[1]:
		role.DelItem(*cfg.needItem)
	elif not role.GetVIP() and role.GetUnbindRMB() >= cfg.needUnbindRMB:
		needUnbindRMB = cfg.needUnbindRMB
		if Environment.EnvIsNA():#北美祭坛文书
			itemId = GetItemIdNA(role)
			if itemId:
				role.DelProp(itemId)
				needUnbindRMB = int(needUnbindRMB * EnumGameConfig.NA_HEROALTAR_DISCOUNT / 10)
		#非vip不打折
		role.DecUnbindRMB(needUnbindRMB)
	elif role.GetVIP() and role.GetUnbindRMB() >= cfg.needUnbindRMB * 8 / 10:
		needUnbindRMB = int(cfg.needUnbindRMB * 8 / 10)
		if Environment.EnvIsNA():
			itemId = GetItemIdNA(role)
			if itemId:
				role.DelProp(itemId)
				needUnbindRMB = int(needUnbindRMB * EnumGameConfig.NA_HEROALTAR_DISCOUNT / 10)
		#vip打折
		role.DecUnbindRMB(needUnbindRMB)
	else:
		return
	
	FightEx.PVE_HeroCall(role, EnumGameConfig.Hero_Altar_FightType, mcid, AfterCall, (index, mcid))
	
	Event.TriggerEvent(Event.Eve_SubTask, role, (EnumTaskType.EnSubTask_UseHeroDesk, 1))
	Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_HeroAltar, 1))
	
def AdvancedCall(role, index, cfg):
	if role.GetTempObj(EnumTempObj.enHeroMgr).GetHeroCnt() > EnumGameConfig.Hero_Altar_Advanced_HeroCnt:
		return
	
	#随机一个阵营ID
	mcid = cfg.advanced_call.RandomOne()
	if not mcid:
		return
	
	#拥有物品个数
	haveCnt = role.ItemCnt(cfg.needItem[0])
	#需要物品个数
	needCnt = cfg.needItem[1] * 10
	
	if haveCnt >= needCnt:
		#只使用物品
		role.DelItem(cfg.needItem[0], needCnt)
		FightEx.PVE_HeroCall(role, EnumGameConfig.Hero_Altar_FightType, mcid, AfterCall, (index, mcid))
		Event.TriggerEvent(Event.Eve_SubTask, role, (EnumTaskType.EnSubTask_UseHeroDesk, 1))
		Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_HeroAltar, 12))
		return
	
	if role.GetVIP() < 5:
		#使用物品后需要元宝(V5以下不打折)
		needUnbindRMB = (needCnt - haveCnt) * cfg.needUnbindRMB
	else:
		#使用物品后需要元宝(V5及以上打折)
		needUnbindRMB = (needCnt - haveCnt) * cfg.needUnbindRMB * 8 / 10
	itemId = 0
	if Environment.EnvIsNA():
		itemId = GetItemIdNA(role)
		if itemId:
			needUnbindRMB = needUnbindRMB * EnumGameConfig.NA_HEROALTAR_DISCOUNT / 10
	
	if role.GetUnbindRMB() < needUnbindRMB:
		return
	
	if haveCnt:
		role.DelItem(cfg.needItem[0], haveCnt)
	if itemId:
		role.DelProp(itemId)
	role.DecUnbindRMB(needUnbindRMB)
	
	FightEx.PVE_HeroCall(role, EnumGameConfig.Hero_Altar_FightType, mcid, AfterCall, (index, mcid))
	Event.TriggerEvent(Event.Eve_SubTask, role, (EnumTaskType.EnSubTask_UseHeroDesk, 1))
	Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_HeroAltar, 12))
	
def DiscountCall(role, index, cfg):
	if role.GetCD(EnumCD.HeroAltarDiscountCD):
		return
	
	if role.GetTempObj(EnumTempObj.enHeroMgr).GetHeroCnt() > EnumGameConfig.Hero_Altar_Normal_HeroCnt:
		return
	
	if role.GetUnbindRMB() < cfg.discountUnbindRMB:
		return
	
	#随机一个阵营ID
	mcid = cfg.normal_call.RandomOne()
	if not mcid:
		return
	
	role.SetCD(EnumCD.HeroAltarDiscountCD, EnumGameConfig.Hero_Altar_DiscountCD)
	
	role.DecUnbindRMB(cfg.discountUnbindRMB)
	
	FightEx.PVE_HeroCall(role, EnumGameConfig.Hero_Altar_FightType, mcid, AfterCall, (index, mcid))
	
	Event.TriggerEvent(Event.Eve_SubTask, role, (EnumTaskType.EnSubTask_UseHeroDesk, 1))
	Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_HeroAltar, 1))
	
def AfterCall(fightObj):
	if fightObj.result is None:
		print "GE_EXC, HeroAltar fight error"
		return
	index, mcid = fightObj.after_fight_param
	cfg = HeroConfig.HeroAltarReward_Dict.get(mcid)
	if not cfg:
		print "GE_EXC, HeroAltar can not find mcid:(%s) in HeroAltarReward_Dict" % mcid
		return
	roles = fightObj.left_camp.roles
	if not roles:
		return
	role = list(roles)[0]
	
	altarCfg = HeroConfig.HeroAltar_Dict.get(index)
	if not altarCfg:
		print "GE_EXC, HeroAltar can not find index:(%s) in HeroAltar_Dict" % index
		return
	
	roleId = role.GetRoleID()
	with HeroAltarCall_Log:
		#物品
		if cfg.rewardItems:
			for item in cfg.rewardItems:
				role.AddItem(*item)
			fightObj.set_fight_statistics(roleId, EnumFightStatistics.EnumItems, cfg.rewardItems)
		
		if not cfg.heroNumber:
			return
		
		#英雄
		if len(cfg.heroNumber) == 1:
			hero = role.AddHero(cfg.heroNumber[0])
			cRoleMgr.Msg(11, 1, GlobalPrompt.HeroAltar_AddHero_Tips_1 % (role.GetRoleName(),
																		roleId,
																		role.GetSex(),
																		role.GetLevel(),
																		role.GetCareer(),
																		role.GetGrade(),
																		role.GetRoleName(),
																		altarCfg.name,
																		hero.GetHeroName())
						)
		elif len(cfg.heroNumber) == 2:
			heroNameList = []
			for heroNumber in cfg.heroNumber:
				hero = role.AddHero(heroNumber)
				heroNameList.append(hero.GetHeroName())
			cRoleMgr.Msg(11, 1, GlobalPrompt.HeroAltar_AddHero_Tips_2 % (role.GetRoleName(),
																		roleId,
																		role.GetSex(),
																		role.GetLevel(),
																		role.GetCareer(),
																		role.GetGrade(),
																		role.GetRoleName(),
																		altarCfg.name,
																		heroNameList[0],
																		heroNameList[1])
						)
		fightObj.set_fight_statistics(roleId, EnumFightStatistics.EnumHeroNumber, cfg.heroNumber)
		
		#记录获得英雄（最多20条记录）
		global HeroAltarRecordList
		if len(HeroAltarRecordList) < 20:
			HeroAltarRecordList.append((roleId, role.GetRoleName(), role.GetLevel(), role.GetSex(), role.GetCareer(), role.GetGrade(), index, cfg.heroNumber))
		else:
			HeroAltarRecordList.pop(0)
			HeroAltarRecordList.append((roleId, role.GetRoleName(), role.GetLevel(), role.GetSex(), role.GetCareer(), role.GetGrade(), index, cfg.heroNumber))
		HeroAltarRecordList.SaveData()
		
		#只同步给打开面板的观察者
		global HeroAltarObserver
		cNetMessage.PackPyMsg(HeroAltarSingleRecord, (roleId, role.GetRoleName(), role.GetLevel(), role.GetSex(), role.GetCareer(), role.GetGrade(), index, cfg.heroNumber))
		for observer in HeroAltarObserver:
			observer.BroadMsg()
		
		#触发支线任务
		Event.TriggerEvent(Event.Eve_SubTask, role, (EnumTaskType.EnSubTask_UpgradeHero, 0))
		
def ChangeHero(role, heroNumber):
	#是否有这个英雄
	if not HeroConfig.Hero_Base_Config.get(heroNumber):
		print "GE_EXC, HeroAltar can not find heroNumber:(%s) in Hero_Base_Config" % heroNumber
		return
	cfg = HeroConfig.HeroChange_Dict.get(heroNumber)
	if not cfg:
		print "GE_EXC, HeroAltar can not find heroNumber:(%s) in HeroChange_Dict" % heroNumber
		return
	if role.GetLevel() < cfg.needLevel:
		return
	if role.ItemCnt(cfg.needItem[0]) < cfg.needItem[1]:
		return
	
	role.DelItem(*cfg.needItem)
	role.AddHero(heroNumber)
	role.Msg(2, 0, GlobalPrompt.HeroAltar_Change)
	
	Event.TriggerEvent(Event.Eve_SubTask, role, (EnumTaskType.EnSubTask_UpgradeHero, heroNumber))
	
#===============================================================================
# 上线同步
#===============================================================================
def BeforeExit(role, param):
	#从观察者中删除
	global HeroAltarObserver
	if role in HeroAltarObserver:
		HeroAltarObserver.remove(role)
#===============================================================================
# 客户端请求
#===============================================================================
def RequestCall(role, msg):
	'''
	请求点将
	@param role:
	@param msg:点将台星级, 点将等级(高级-1, 普通-0, 折扣-2)
	'''
	if not msg:
		return
	
	index, level = msg
	
	#配置
	cfg = HeroConfig.HeroAltar_Dict.get(index)
	if not cfg:
		print "GE_EXC, HeroAltar can not find index:(%s) in HeroAltar_Dict" % index
		return
	
	#等级
	if role.GetLevel() < EnumGameConfig.Hero_Altar_LevelLimit \
		or role.GetLevel() < cfg.openLevel:
		return
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		return
	with HeroAltarCall_Log:
		if level == 0:
			NormalCall(role, index, cfg)
		elif level == 1:
			AdvancedCall(role, index, cfg)
		elif level == 2:
			DiscountCall(role, index, cfg)
		
def RequestChange(role, msg):
	'''
	请求兑换
	@param role:
	@param msg:英雄number
	'''
	if not msg:
		return
	if role.GetTempObj(EnumTempObj.enHeroMgr).IsHeroFull():
		return
	
	with HeroAltarChange_Log:
		ChangeHero(role, msg)

def RequestOpenAltar(role, msg):
	'''
	请求打开祭坛
	@param role:
	@param msg:None
	'''
	#等级
	if role.GetLevel() < EnumGameConfig.Hero_Altar_LevelLimit:
		return
	
	#加入观察者
	global HeroAltarObserver
	if role not in HeroAltarObserver:
		HeroAltarObserver.append(role)
	
	#同步获得英雄记录
	global HeroAltarRecordList
	role.SendObj(HeroAltarRecord, HeroAltarRecordList.data)
	
def RequestCloseAltar(role, msg):
	'''
	请求关闭祭坛
	@param role:
	@param msg:
	'''
	global HeroAltarObserver
	if role in HeroAltarObserver:
		HeroAltarObserver.remove(role)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic or Environment.HasWeb:
		HeroAltarRecordList = Contain.List("HeroAltarRecordList", (2038, 1, 1), isSaveBig = False)
	
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_BeforeExit, BeforeExit)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Hero_Call", "请求开启祭坛"), RequestCall)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Hero_Change", "请求兑换英雄"), RequestChange)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Hero_OpenAltar", "请求打开祭坛"), RequestOpenAltar)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Hero_CloseAltar", "请求关闭祭坛"), RequestCloseAltar)
		