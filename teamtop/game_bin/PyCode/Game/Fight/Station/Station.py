#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.Station.Station")
#===============================================================================
# 阵位
#===============================================================================
import cRoleMgr
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Fight.Station import StationBase, StationConfig
from Game.Pet import PetMgr
from Game.Role import Event
from Game.Role.Data import EnumTempObj, EnumObj
from Game.Task import EnumTaskType

if "_HasLoad" not in dir():
	Station_Show_Change = AutoMessage.AllotMessage("Station_Show_Change", "通知客户端显示阵位变化")
	Help_Station_Show_Change = AutoMessage.AllotMessage("Help_Station_Show_Change", "通知客户端显示助阵位变化")
	StationMosaic_Data = AutoMessage.AllotMessage("StationMosaic_Data", "助阵位镶嵌数据")
	StationUnlock_Data = AutoMessage.AllotMessage("StationUnlock_Data", "助阵位解锁数据")
	
	StationMosaic_Log = AutoLog.AutoTransaction("StationMosaic_Log", "助阵位镶嵌日志")
	StationUnlock_Log = AutoLog.AutoTransaction("StationUnlock_Log", "助阵位解锁日志")

def CanOutStation(role, hero):
	#这个英雄是否可以下阵
	heroId = hero.GetHeroId()
	
	#有装备的不能下阵
	if hero.equipmentMgr.objIdDict:
		return False
	
	#有装备命魂不能下阵
	if role.GetTempObj(EnumTempObj.enTarotMgr).HeroHasCard(heroId):
		return False
	
	#有神器不能下阵
	if role.GetObj(EnumObj.En_HeroArtifact).get(heroId):
		return False
	
	#有圣器的不能下阵
	if role.GetObj(EnumObj.En_HeroHallows).get(heroId):
		return False
	
	#装备了天赋卡不能下阵
	if hero.IsPutTalent():
		return False
	
	#装备了魔灵不能下阵
	if hero.IsPutMagicSpirit():
		return False
	
	return True

def InStation(role, heroId, stationId):
	sm = role.GetTempObj(EnumTempObj.enStationMgr)
	
	if not sm: return
	
	#阵位不合法
	if not sm.station_is_legal(stationId):
		return
	
	#获取英雄
	hero = role.GetHero(heroId)
	if not hero:
		return
	
	#原阵位和要上阵的阵位相同
	heroStationID = hero.GetStationID()
	if heroStationID == stationId:
		return
	
	#该英雄在助阵位上
	if hero.GetHelpStationID():
		return
	
	#该类型英雄在助阵位上
	heroType = hero.GetType()
	if sm.type_in_help_station(heroType):
		return
	
	#阵位上有该类型英雄, 且该类型英雄的阵位不是要上阵的阵位
	stationID = sm.type_in_station(heroType)
	if stationID and stationID != stationId:
		return
	
	#上阵主角的位置
	if stationId == role.GetStationID():
		return
	
	sHeroId = sm.get_heroid_from_station(stationId)
	#该阵位上没有英雄, 直接上阵
	if not sHeroId:
		sm.in_station(heroId, stationId)
		
		hero.SetStationID(stationId)
		
		Event.TriggerEvent(Event.Eve_SubTask, role, (EnumTaskType.EnSubTask_HeroOnStation, hero.GetNumber()))
		
		role.SendObj(Station_Show_Change, (heroId, stationId))
		hero.propertyGather.ResetRecountZhuanShengFlag()
		role.Msg(2, 0, GlobalPrompt.Station_SuccessIn)
		return
	
	#该阵位上有英雄, 下阵原阵位上英雄再上阵
	sHero = role.GetHero(sHeroId)
	if not sHero:
		return
	
	if not CanOutStation(role, sHero):
		return
	
	#有宠物的先把宠物卸下
	petId = hero.GetPetID()
	if petId:
		PetMgr.OffPet(role, petId)
	
	sm.out_station(stationId)
	sm.in_station(heroId, stationId)
	sHero.SetStationID(0)
	hero.SetStationID(stationId)
	
	Event.TriggerEvent(Event.Eve_SubTask, role, (EnumTaskType.EnSubTask_HeroOnStation, hero.GetNumber()))
	
	role.SendObj(Station_Show_Change, (heroId, stationId, sHeroId, 0))
	
	#重算转生属性
	hero.propertyGather.ResetRecountZhuanShengFlag()
	
	role.Msg(2, 0, GlobalPrompt.Station_SuccessIn)
	
def OutStation(role, heroId):
	sm = role.GetTempObj(EnumTempObj.enStationMgr)
	if not sm: return
	
	#获取英雄
	hero = role.GetHero(heroId)
	if not hero:
		return
	
	if not CanOutStation(role, hero):
		return
	
	heroStationID = hero.GetStationID()
	#阵位不合法
	if not sm.station_is_legal(heroStationID):
		return
	
	#有宠物的先把宠物卸下
	petId = hero.GetPetID()
	if petId:
		PetMgr.OffPet(role, petId)
	
	sm.out_station(heroStationID)
	hero.SetStationID(0)
	#重算转生属性
	hero.propertyGather.ResetRecountZhuanShengFlag()
	#通知客户端阵位变化
	role.SendObj(Station_Show_Change, (heroId, 0))

def ChangeStation(role, station1, station2):
	sm = role.GetTempObj(EnumTempObj.enStationMgr)
	if not sm: return
	
	#阵位不合法
	if not sm.station_is_legal(station1) or not sm.station_is_legal(station2):
		return
	
	heroId1 = sm.get_heroid_from_station(station1)
	heroId2 = sm.get_heroid_from_station(station2)
	
	#第一个位置上没人
	if not heroId1:
		return
	
	#第二个位置没人
	if not heroId2 and heroId1 == role.GetRoleID():
		#位置1上是主角
		sm.out_station(station1)
		sm.in_station(heroId1, station2)
		role.SetStationID(station2)
		role.Msg(2, 0, GlobalPrompt.Station_SuccessIn)
		return
	elif not heroId2 and heroId1 != role.GetRoleID():
		#位置1上是英雄
		sm.out_station(station1)
		sm.in_station(heroId1, station2)
		hero1 = role.GetHero(heroId1)
		hero1.SetStationID(station2)
		role.SendObj(Station_Show_Change, (heroId1, station2))
		role.Msg(2, 0, GlobalPrompt.Station_SuccessIn)
		return
	
	if sm.is_station_role(station1):
		#阵位1上是主角 -- 先设置阵位再交换阵位对应的roleID或heroid
		role.SetStationID(station2)
		hero2 = role.GetHero(heroId2)
		hero2.SetStationID(station1)
		sm.type_to_station[hero2.GetType()] = station1
		sm.swap_station(station1, station2)
		role.SendObj(Station_Show_Change, (heroId2, station1))
		role.Msg(2, 0, GlobalPrompt.Station_SuccessIn)
		return
	elif sm.is_station_role(station2):
		#阵位2上是主角 -- 先设置阵位再交换阵位对应的roleID或heroid
		role.SetStationID(station1)
		hero1 = role.GetHero(heroId1)
		hero1.SetStationID(station2)
		sm.type_to_station[hero1.GetType()] = station2
		sm.swap_station(station1, station2)
		role.SendObj(Station_Show_Change, (heroId1, station2))
		role.Msg(2, 0, GlobalPrompt.Station_SuccessIn)
		return
	else:
		#交换的是两个英雄阵位
		hero1 = role.GetHero(heroId1)
		hero2 = role.GetHero(heroId2)
		hero1.SetStationID(station2)
		hero2.SetStationID(station1)
		sm.type_to_station[hero1.GetType()] = station2
		sm.type_to_station[hero2.GetType()] = station1
		sm.swap_station(station1, station2)
		role.SendObj(Station_Show_Change, (heroId1, station2, heroId2, station1))
		role.Msg(2, 0, GlobalPrompt.Station_SuccessIn)
		return
	
def OnHelpStation(role, heroId, stationId):
	sm = role.GetTempObj(EnumTempObj.enStationMgr)
	if not sm: return
	
	#助阵位不合法
	if not sm.help_station_is_legal(stationId):
		return
	
	next_help_station_id = sm.cal_next_help_station_id()
	if (not next_help_station_id) or (next_help_station_id != stationId):
		#判断助阵位ID
		return
	
	#助阵位有英雄了
	if sm.get_heroid_from_help_station(stationId):
		return
	
	hero = role.GetHero(heroId)
	if not hero:
		return
	
	#有装备的不能助阵
	if hero.equipmentMgr.objIdDict:
		return
	
	#英雄星级
	heroStar = hero.GetStar()
	if not heroStar:
		return
	
	if stationId in (1,2,3):
		#主助阵位声望有需求, 副助阵位开了就能上阵
		cfg = StationConfig.HelpStationAct_Dict.get((stationId, heroStar))
	
		if not cfg:
			print 'GE_EXC, OnHelpStation can not find stationId %s cfg' % stationId
			return
	
		#声望不足
		if role.GetReputation() < cfg.needRepution:
			return
	
	#该类型英雄上阵或助阵了
	heroType = hero.cfg.heroType
	if sm.type_in_station(heroType):
		#在上阵
		role.Msg(2, 0, GlobalPrompt.Station_TypeInStation)
		return
	if sm.type_in_help_station(heroType):
		#助阵位上有相同类型英雄
		return
	if not sm.check_can_in_help_station(hero, stationId):
		#判断一下星级
		return
	
	#可助阵
	sm.in_help_station(heroId, stationId)
	hero.SetHelpStationID(stationId)
	
	role.SendObj(Help_Station_Show_Change, (heroId, stationId))
	
	#属性重算 -- 全体上阵英雄
	role.ResetGlobalHelpStationProperty()
	
def OutHelpStation(role, heroId):
	sm = role.GetTempObj(EnumTempObj.enStationMgr)
	if not sm: return
	
	hero = role.GetHero(heroId)
	if not hero:
		return
	
	heroStationId = hero.GetHelpStationID()
	
	#该英雄不在助阵位上
	if not heroStationId:
		return
	
	#下阵
	sm.out_help_station(heroStationId)
	hero.SetHelpStationID(0)
	
	#重算助阵位属性
	role.ResetGlobalHelpStationProperty()
	
	role.SendObj(Help_Station_Show_Change, (heroId, 0))
	
def OnRoleInitPyObj(role, param):
	#初始化阵位
	
	#这里确保在初始化阵位管理器之前先初始化阵位obj
	if not role.GetObj(EnumObj.StationObj):
		role.SetObj(EnumObj.StationObj, {1:{}, 2:[]})
	
	role.SetTempObj(EnumTempObj.enStationMgr, StationBase.StationMgr(role))
#===============================================================================
def RequestInStation(role, msg):
	'''
	客户端请求上阵
	@param role:
	@param msg:
	'''
	if role.GetLevel() < EnumGameConfig.Station_Level_Limit:
		return
	
	heroId, stationId = msg
	if not heroId:
		return
	if not stationId:
		return
	if heroId == role.GetRoleID():
		return
	
	InStation(role, heroId, stationId)
	
def RequestOutStation(role, msg):
	'''
	客户端请求下阵
	@param role:
	@param msg:
	'''
	if role.GetLevel() < EnumGameConfig.Station_Level_Limit:
		return
	
	heroId = msg
	if not heroId:
		return
	if heroId == role.GetRoleID():
		return
	
	OutStation(role, heroId)

def RequestChangeStation(role, msg):
	'''
	客户端请求交换阵位
	@param role:
	@param msg:
	'''
	if role.GetLevel() < EnumGameConfig.Station_Level_Limit:
		return
	
	station1, station2 = msg
	
	ChangeStation(role, station1, station2)

def RequestOnHelpStation(role, msg):
	'''
	请求助阵
	@param role:
	@param msg:
	'''
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.HelpStation_Level_Limit:
		return
	
	heroId, stationId = msg
	
	if stationId in (4,5,6) and roleLevel < EnumGameConfig.HelpStation_Level_LimitEx:
		#副助阵位等级限制
		return
	
	if not heroId:
		return
	if not stationId:
		return
	if heroId == role.GetRoleID():
		return
	
	OnHelpStation(role, heroId, stationId)
	
def RequestOutHelpStation(role, msg):
	'''
	请求下助阵位
	@param role:
	@param msg:
	'''
	if role.GetLevel() < EnumGameConfig.HelpStation_Level_Limit:
		return
	
	heroId = msg
	if not heroId:
		return
	if heroId == role.GetRoleID():
		return
	
	OutHelpStation(role, heroId)
	
def RequestMosaic(role, msg):
	'''
	请求镶嵌助阵位神佑卷轴
	@param role:
	@param msg:
	'''
	#等级限制
	if role.GetLevel() < EnumGameConfig.HelpStation_Mosaic_LvLimit:
		return
	
	#阵位管理器
	sm = role.GetTempObj(EnumTempObj.enStationMgr)
	if not sm:
		return
	
	stationId = msg
	
	if stationId in (4,5,6) and (stationId not in role.GetObj(EnumObj.StationObj).get(2, [])):
		#副助阵位未开不让镶嵌
		return
	
	#镶嵌等级
	mosaicCfg = StationConfig.HelpStationMosaic_Dict.get(sm.help_station_mosaic.get(stationId, 0))
	if not mosaicCfg:
		print 'GE_EXC, RequestMosaic can not find stationId %s mosaicCfg' % stationId
		return
	
	if mosaicCfg.needCrystal <= 0:
		return
	
	#需要的一级神佑卷轴
	needCrystal = mosaicCfg.needCrystal
	#需要删除的item列表[(coding, cnt),]
	delItemList = []
	
	for itemCoding in mosaicCfg.lowList:
		itemCnt = role.ItemCnt(itemCoding)
		if itemCnt:
			#有道具的话, 计算道具能兑换多少一级神佑卷轴
			crystalCfg = StationConfig.HelpStationCrystalEx_Dict.get(itemCoding)
			if not crystalCfg:
				continue
			#计算能兑换多少个一级神佑卷轴
			totalCrystal = itemCnt * crystalCfg.exCrystal
			
			if totalCrystal >= needCrystal:
				#个数够了
				useCnt = needCrystal / crystalCfg.exCrystal
				delItemList.append((itemCoding, useCnt))
				break
			else:
				needCrystal -= totalCrystal
				delItemList.append((itemCoding, itemCnt))
	else:
		#个数不够
		return
	
	with StationMosaic_Log:
		#扣物品
		for (itemCoding, itemCnt) in delItemList:
			role.DelItem(itemCoding, itemCnt)
		#升级
		if stationId not in sm.help_station_mosaic:
			sm.help_station_mosaic[stationId] = 1
		else:
			sm.help_station_mosaic[stationId] += 1
		#日志
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveStationMosaic, sm.help_station_mosaic[stationId])
	
	#重算助阵位属性
	role.ResetGlobalHelpStationProperty()
	
	role.SendObj(StationMosaic_Data, sm.help_station_mosaic)
	
def RequestUnlock(role, msg):
	'''
	请求解锁副助阵位
	@param role:
	@param msg:
	'''
	#等级限制
	if role.GetLevel() < EnumGameConfig.HelpStation_Level_LimitEx:
		return
	
	#阵位管理器
	sm = role.GetTempObj(EnumTempObj.enStationMgr)
	if not sm:
		return
	
	if role.GetUnbindRMB() < EnumGameConfig.HSUnlockConsume:
		return
	
	stationId = msg
	
	if stationId in sm.help_station_limit:
		return
	
	if stationId not in (4, 5, 6):
		return
	
	stationObj = role.GetObj(EnumObj.StationObj)
	if not stationObj:
		return
	
	unlockList = stationObj.get(2)
	if unlockList is None:
		return
	if not unlockList:
		#没有解锁过的话必须先解锁4号位
		if stationId != 4:
			return
	else:
		#已经解锁过的, 按顺序解锁
		if stationId != (unlockList[-1] + 1):
			return
	
	cfg = StationConfig.HelpStationAct_Dict.get((stationId, 1))
	if not cfg:
		print 'GE_EXC, station RequestUnlock can not find unlock station %s cfg' % stationId
		return
	
	if role.GetReputation() < cfg.needRepution:
		return
	
	with StationUnlock_Log:
		#扣钱
		role.DecUnbindRMB(EnumGameConfig.HSUnlockConsume)
		#解锁
		sm.UnlockHelpStationId(stationId)
		#记下日志
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveStationUnlock, stationId)
		#同步最新的解锁数据
		role.SendObj(StationUnlock_Data, role.GetObj(EnumObj.StationObj).get(2, []))
	
def RequestOpenHelpStation(role, msg):
	'''
	请求打开助阵面板
	@param role:
	@param msg:
	'''
	#等级限制
	if role.GetLevel() < EnumGameConfig.HelpStation_Level_Limit:
		return
	
	#阵位管理器
	sm = role.GetTempObj(EnumTempObj.enStationMgr)
	if not sm:
		return
	
	role.SendObj(StationMosaic_Data, sm.help_station_mosaic)
	
	role.SendObj(StationUnlock_Data, role.GetObj(EnumObj.StationObj).get(2, []))
	
def OnRoleSave(role, param):
	sm = role.GetTempObj(EnumTempObj.enStationMgr)
	if not sm: return
	
	sm.save(role)
	
if "_HasLoad" not in dir():
	Event.RegEvent(Event.Eve_InitRolePyObj, OnRoleInitPyObj)
	
	#角色保存
	Event.RegEvent(Event.Eve_BeforeSaveRole, OnRoleSave)
	
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Station_OpenHelpStation", "客户端请求打开阵位面板"), RequestOpenHelpStation)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Station_In", "客户端请求上阵"), RequestInStation)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Station_Change", "客户端请求交换阵位"), RequestChangeStation)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Station_Out", "客户端请求下阵"), RequestOutStation)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Station_InHelpStation", "客户端请求上助阵位"), RequestOnHelpStation)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Station_OutHelpStation", "客户端请求下助阵位"), RequestOutHelpStation)	
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Station_Mosaic", "客户端请求助阵位镶嵌"), RequestMosaic)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Station_Unlock", "客户端请求解锁副助阵位"), RequestUnlock)
	
	
	
	
