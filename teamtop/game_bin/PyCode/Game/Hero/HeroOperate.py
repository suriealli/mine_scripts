#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Hero.HeroOperate")
#===============================================================================
# 英雄相关
#===============================================================================
import cRoleMgr
import cProcess
import cDateTime
import Environment
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Role.Obj import EnumOdata
from Game.Role.Base import LevelEXP
from Game.Role.Data import EnumTempObj, EnumObj, EnumInt32
from Game.Hero import HeroBase
from Game.Hero import HeroConfig
from Game.Item import PackMgr
from Game.Role.Config import RoleConfig, RoleBaseConfig
from Game.Task import EnumTaskType
from Game.Role import Event
from Game.Activity.WonderfulAct import WonderfulActMgr, EnumWonderType

if "_HasLoad" not in dir():
	
	Hero_ZhaoMo_Ok = AutoMessage.AllotMessage("Hero_ZhaoMo_Ok", "英雄招募成功")
	Hero_OnFire_Ok = AutoMessage.AllotMessage("Hero_OnFire_Ok", "英雄辞退成功")
	Hero_OnUpgrade_Ok = AutoMessage.AllotMessage("Hero_OnUpgrade_Ok", "英雄进阶成功")
	Hero_ZhaoMo_CD = AutoMessage.AllotMessage("Hero_ZhaoMo_CD", "英雄招募CD")
	Hero_OnAwaken_Ok = AutoMessage.AllotMessage("Hero_OnAwaken_Ok", "英雄觉醒成功")
	CuiLian_Dict = AutoMessage.AllotMessage("CuiLian_Dict", "同步淬炼数据字典")
	
	SyncHeroZhuanShengOk = AutoMessage.AllotMessage("SyncHeroZhuanShengOk", "同步英雄转生成功")
	
	
	#日志
	TraHeroZhaoMu = AutoLog.AutoTransaction("TraHeroZhaoMu", "招募英雄")
	TraHeroFire = AutoLog.AutoTransaction("TraHeroFire", "英雄离队")
	TraUseHeroExpItem = AutoLog.AutoTransaction("TraUseHeroExpItem", "使用英雄经验丹")
	TraUpgradeHero = AutoLog.AutoTransaction("TraUpgradeHero", "英雄进阶")
	TraUpgradeRole = AutoLog.AutoTransaction("TraUpgradeRole", "主角进阶")
	TraAwakenHero = AutoLog.AutoTransaction("TraAwakenHero", "英雄觉醒")
	TraCuiLianHero = AutoLog.AutoTransaction("TraCuiLianHero", "英雄淬炼")
	TraCuiLianRole = AutoLog.AutoTransaction("TraCuiLianRole", "主角淬炼")
	TraZhuanShengHaloLevelUp = AutoLog.AutoTransaction("TraZhuanShengHaloLevelUp", "转生光环升级")
	TraHeroZhuanSheng = AutoLog.AutoTransaction("TraHeroZhuanSheng", "英雄转生")
	TraRoleZhuanSheng = AutoLog.AutoTransaction("TraRoleZhuanSheng", "主角转生")
##################################################################################
def BuildNewHero():
	heroDataDict = {}
	heroDataDict[EnumOdata.enHeroExp] = 0		#经验
	heroDataDict[EnumOdata.enHerolevel] = 1		#等级
	heroDataDict[EnumOdata.enStationID] = 0		#阵位
	heroDataDict[EnumOdata.enHelpStationID] = 0	#助阵位
	
	#分配英雄Id -- heroId, heroData
	return cProcess.AllotGUID64(), heroDataDict

def BuildNewHeroByLevel(level):
	heroDataDict = {}
	heroDataDict[EnumOdata.enHeroExp] = 0		#经验
	heroDataDict[EnumOdata.enHerolevel] = level	#等级
	heroDataDict[EnumOdata.enStationID] = 0		#阵位
	heroDataDict[EnumOdata.enHelpStationID] = 0	#助阵位
	
	#分配英雄Id -- heroId, heroData
	return cProcess.AllotGUID64(), heroDataDict


def AddHero(role, param):
	'''直接增加一个英雄'''
	heroNumber = param
	if not heroNumber: return
	
	cfg = HeroConfig.Hero_Base_Config.get(heroNumber)
	if not cfg:
		print "GE_EXC, AddHero can not find heroNumber:(%s) in Hero_Base_Config" % heroNumber
		return
	
	#英雄满了
	roleHeroMgr = role.GetTempObj(EnumTempObj.enHeroMgr)
	if not roleHeroMgr:
		return
	if roleHeroMgr.IsHeroFull():
		return
	
	#初始化英雄
	heroId, heroDataDict = BuildNewHero()
	if not heroId or not heroDataDict:
		return
	newhero = HeroBase.Hero(role, (heroId, heroNumber, 0, heroDataDict))
	newhero.AfterCreate()
	
	#加入管理器
	roleHeroMgr.HeroDict[heroId] = newhero
	
	role_herodataDict = role.GetObj(EnumObj.En_Hero_Data_Dict)
	#记录ID(用于解雇时判断) -- ID唯一, type不唯一
	heroList = role_herodataDict[1]
	heroList.append(heroId)
	
	#记录Type(用于解雇时判断) -- heroType --> set(heroId)
	heroTypeToIdSet = role_herodataDict[3]
	heroType = newhero.cfg.heroType
	if heroType not in heroTypeToIdSet:
		heroTypeToIdSet[heroType] = set([heroId, ])
	else:
		heroTypeToIdSet[heroType].add(heroId)
	
	#初始化英雄身上的管理器
	InitHero(role, heroId, newhero)
	
	#记录日志
	AutoLog.LogObj(role.GetRoleID(), AutoLog.eveAddHero, heroId, heroNumber, 1, heroDataDict)
	#同步客户端
	role.SendObj(Hero_ZhaoMo_Ok, newhero.GetSyncData())
	
	return newhero

def AddHeroByLevel(role, heroNumber, level):
	'''直接增加一个英雄'''
	heroNumber, level = heroNumber, level
	if not heroNumber: return
	
	cfg = HeroConfig.Hero_Base_Config.get(heroNumber)
	if not cfg:
		print "GE_EXC, AddHero can not find heroNumber:(%s) in Hero_Base_Config" % heroNumber
		return
	
	#英雄满了
	roleHeroMgr = role.GetTempObj(EnumTempObj.enHeroMgr)
	if not roleHeroMgr:
		return
	if roleHeroMgr.IsHeroFull():
		return
	
	#初始化英雄
	heroId, heroDataDict = BuildNewHeroByLevel(level)
	if not heroId or not heroDataDict:
		return
	newhero = HeroBase.Hero(role, (heroId, heroNumber, 0, heroDataDict))
	newhero.AfterCreate()
	
	#加入管理器
	roleHeroMgr.HeroDict[heroId] = newhero
	
	role_herodataDict = role.GetObj(EnumObj.En_Hero_Data_Dict)
	#记录ID(用于解雇时判断) -- ID唯一, type不唯一
	heroList = role_herodataDict[1]
	heroList.append(heroId)
	
	#记录Type(用于解雇时判断) -- heroType --> set(heroId)
	heroTypeToIdSet = role_herodataDict[3]
	heroType = newhero.cfg.heroType
	if heroType not in heroTypeToIdSet:
		heroTypeToIdSet[heroType] = set([heroId, ])
	else:
		heroTypeToIdSet[heroType].add(heroId)
	
	#初始化英雄身上的管理器
	InitHero(role, heroId, newhero)
	
	#记录日志
	AutoLog.LogObj(role.GetRoleID(), AutoLog.eveAddHero, heroId, heroNumber, 1, heroDataDict)
	#同步客户端
	role.SendObj(Hero_ZhaoMo_Ok, newhero.GetSyncData())
	
	return newhero
##################################################################################
def OpenTavernPanel(role, msg):
	'''
	打开酒馆面板
	@param role:
	@param msg:
	'''
	#同步招募CD
	role.SendObj(Hero_ZhaoMo_CD, role.GetObj(EnumObj.En_Hero_Data_Dict)[2])
	
def OnHeroZhaoMu(role, msg):
	'''
	请求招募英雄
	@param role:
	@param msg:英雄编号
	'''
	heroNumber = msg
	if not heroNumber: return
	
	roleLevel = role.GetLevel()
	#开放招募等级
	if roleLevel < EnumGameConfig.Hero_ZhaoMu_LevelLimit:
		return
	
	#英雄配置
	cfg = HeroConfig.Hero_Base_Config.get(heroNumber)
	if not cfg:
		print "GE_EXC, OnHeroZhaoMu can not find heroNumber:(%s) in Hero_Base_Config" % heroNumber
		return
	
	#招募该英雄等级不足
	if roleLevel < cfg.needLevel:
		return
	
	#声望不足
	if role.GetReputation() < cfg.needReputation:
		return
	
	if cfg.needMoney:
		#需要金币
		needMoney = True
		if role.GetMoney() < cfg.needMoney:
			return
	elif cfg.needItems:
		#需要道具
		needMoney = False
		if role.ItemCnt(cfg.needItems[0]) < cfg.needItems[1]:
			return
	else:
		return
	
	#英雄满了
	roleHeroMgr = role.GetTempObj(EnumTempObj.enHeroMgr)
	if roleHeroMgr.IsHeroFull():
		return
	
	role_herodataDict = role.GetObj(EnumObj.En_Hero_Data_Dict)
	#该英雄在招募CD中
	heroCD = role_herodataDict.get(2)
	if heroNumber in heroCD and heroCD[heroNumber] > cDateTime.Seconds():
		return
	
	with TraHeroZhaoMu:
		#扣银币或道具
		if needMoney:
			role.DecMoney(cfg.needMoney)
		else:
			role.DelItem(*cfg.needItems)
		
		#构建英雄
		heroId, heroDataDict = BuildNewHero()
		if not heroId or not heroDataDict:
			return
		newhero = HeroBase.Hero(role, (heroId, heroNumber, 0, heroDataDict))
		newhero.AfterCreate()
		
		#加入管理器
		roleHeroMgr.HeroDict[heroId] = newhero
		
		#记录ID(用于解雇时判断) -- ID唯一, type不唯一
		heroList = role_herodataDict[1]
		heroList.append(heroId)
		
		#记录Type(用于解雇时判断) -- heroType --> set(heroId)
		heroTypeToIdSet = role_herodataDict[3]
		heroType = newhero.cfg.heroType
		if heroType not in heroTypeToIdSet:
			heroTypeToIdSet[heroType] = set([heroId, ])
		else:
			heroTypeToIdSet[heroType].add(heroId)
		
		#记录招募时间戳 -- 下一次招募的时间戳
		role_herodataDict[2][heroNumber] = cDateTime.Seconds() + cfg.coolCD
		
		#初始化英雄身上的管理器
		InitHero(role, heroId, newhero)
		
		#记录日志
		AutoLog.LogObj(role.GetRoleID(), AutoLog.eveAddHero, heroId, heroNumber, 1, heroDataDict)
		
		#同步客户端
		role.SendObj(Hero_ZhaoMo_Ok, newhero.GetSyncData())
		role.SendObj(Hero_ZhaoMo_CD, role.GetObj(EnumObj.En_Hero_Data_Dict)[2])
		
		#提示招募成功
		role.Msg(2, 0, GlobalPrompt.HeroZhaoMuSuccess)
		
		Event.TriggerEvent(Event.Eve_SubTask, role, (EnumTaskType.EnSubTask_ZhaoMuHero, newhero.GetNumber()))
	
def OnHeroFire(role, msg):
	'''
	英雄离队
	@param role:
	@param msg:英雄ID
	'''
	heroId = msg
	if not heroId: return
	
	herodataDict = role.GetObj(EnumObj.En_Hero_Data_Dict)
	
	#没有招募过该英雄
	heroList = herodataDict[1]
	if heroId not in heroList:
		return
	
	#获取不到这个英雄对象
	hero = role.GetHero(heroId)
	if not hero:
		return
	
	#获取最高英雄星级
	sg_dict = role.GetObj(EnumObj.StarColor_Dict)
	if not sg_dict:
		return
	maxStar = max(sg_dict.keys())
	
	nowStar = hero.GetStar()
	heroTypeToIdSet = herodataDict[3]
	heroIdSet = heroTypeToIdSet[hero.cfg.heroType]
	if ((maxStar - nowStar) < 3) and len(heroIdSet) < 2:
		#(当前最高英雄星级 - 当前要解雇的英雄的星级) < 3 的时候, 如果没有两个同一类型的英雄, 就不能解雇
		#(当前最高英雄星级 - 当前要解雇的英雄的星级) > 3 的时候, 不用判断英雄个数, 可以直接解雇
		
		#若该英雄的星级与最高星级差小于等于-3，则跳过判断该类英雄数量是否大于等于2，直接可进行解雇
		#这里要判断只有一个该类型英雄不能解雇
		return
	
	if heroId not in heroIdSet:
		print "GE_EXC, HeroOperate role (%s) have no heroId (%s) in heroTypeToIdSet, can't fire hero." % (role.GetRoleID(), heroId)
		return
	
	#解雇判断
	if not FireCheck(role, hero, heroId):
		return

	oldStar = hero.cfg.star
	oldLevel = hero.GetLevel()
	returnItems = hero.cfg.returnItems
	heroNumber = hero.onumber
	
	with TraHeroFire:
		#删除英雄数据
		heroList.remove(heroId)
		heroIdSet.discard(heroId)
		if not heroIdSet:
			del heroIdSet
		
		#删除英雄
		DelHero(role, heroId, heroNumber)
		
		#返还物品
		if returnItems:
			#紫色以上
			role.AddItem(*returnItems)
			role.Msg(2, 0, GlobalPrompt.HeroFire_Tips % returnItems)
		else:
			#紫色以下
			FireHeroReturnItem(role, oldStar, oldLevel)
		
def OnUseHeroExpItem(role, msg):
	'''
	使用英雄经验丹物品
	@param role:
	@param msg:(英雄ID,[(经验丹物品类型,使用数量)])
	'''
	heroId, items = msg
	
	if len(items) == 0 or len(items) > 3:
		return
	
	#主角不能使用经验丹
	if heroId == role.GetRoleID():
		return
	
	hero = role.GetHero(heroId)
	if not hero:
		return
	
	totalExp = 0
	totalMoney = 0
	
	for (coding, cnt) in items:
		if cnt <= 0:
			return
		cfg = HeroConfig.HeroExpItem_Dict.get(coding)
		if not cfg:
			print "GE_EXC, HeroOperate can not find coding:(%s) in HeroExpItem_Dict" % coding
			return
		#经验丹数量不够
		if role.ItemCnt(coding) < cnt:
			return
		#计算总经验
		totalExp += cfg.exp * cnt
		totalMoney += cfg.cost * cnt
	
	#金钱不足
	if role.GetMoney() < totalMoney:
		return
	
	with TraUseHeroExpItem:
		#删物品
		for (coding, cnt) in items:
			role.DelItem(coding, cnt)
		#扣钱
		role.DecMoney(totalMoney)
		#加经验 通知客户端
		LevelEXP.IncHeroExp(role, hero, totalExp, heroId)
	
	if Environment.EnvIsNA():
		HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
		HalloweenNAMgr.HeroLevel()
		
def OnRoleUpgrade(role, msg):
	'''
	请求主角升阶
	@param role:
	@param msg:None
	'''
	cfg = RoleConfig.RoleBase_Dict.get((role.GetCareer(), role.GetGrade(), role.GetSex()))
	if not cfg:
		print "GE_EXC, HeroOperate can not find career:(%s), grade:(%s), sex:(%s) in RoleBase_Dict" % (role.GetCareer(), role.GetGrade(), role.GetSex())
		return
	
	#等级不够
	if role.GetLevel() < cfg.upgradeNeedLv:
		return
	
	#没有下一阶了
	if cfg.nextGrade < 0:
		return
	
	#物品不足
	if role.ItemCnt(cfg.upgradeNeedItem[0]) < cfg.upgradeNeedItem[1]:
		return
	
	with TraUpgradeRole:
		#扣除物品
		role.DelItem(*cfg.upgradeNeedItem)
		#设置品阶
		role.SetGrade(cfg.nextGrade)
		#加技能点
		role.IncI32(EnumInt32.SkillPoint, cfg.getSkillPoint)
		
		role.GetPropertyGather().ReSetRecountBaseFlag()
	
	
	Event.TriggerEvent(Event.Eve_SubTask, role, (EnumTaskType.EnSubTask_RoleGrade, None))
	
	#主角进阶事件触发
	Event.TriggerEvent(Event.Eve_AfterRoleUpgrade, role, None)
	
def OnUpgradeHero(role, msg):
	'''
	请求进阶英雄(修改为给英雄加进阶经验值，经验满了才可以进阶)
	@param role:
	@param msg:英雄ID
	'''
	heroId, needHeroId = msg
	
	hero = role.GetHero(heroId)
	if not hero:
		return

	#是否有下一阶
	nextGradeHeroNumber = hero.cfg.nextGradeHeroNumber
	if not nextGradeHeroNumber:
		return
	nextCfg = HeroConfig.Hero_Base_Config.get(nextGradeHeroNumber)
	if not nextCfg:
		print "GE_EXC, OnUpgradeHero can not find nextGradeHeroNumber:(%s) in Hero_Base_Config" % nextGradeHeroNumber
		return
	
	#当前等阶配置
	nowCfg = HeroConfig.Hero_Base_Config.get(hero.onumber)
	if not nowCfg:
		print "GE_EXC, OnUpgradeHero can not find heroNumber:(%s) in Hero_Base_Config" % hero.onumber
		return
	
	#主角等级不足
	if role.GetLevel() < nowCfg.upgradeNeedRoleLv:
		return
	
	#未达到升阶等级要求
	if hero.GetLevel() < nowCfg.upgradeNeedLv:
		return
	
	#进阶物品不足
	if not nowCfg.upgradeNeedItem:
		return
	
	for item in nowCfg.upgradeNeedItem:
		if role.ItemCnt(item[0]) < item[1]:
			return
	
	heroIdList = role.GetObj(EnumObj.En_Hero_Data_Dict)[1]
	if not heroIdList:
		return
	
	#进阶需要英雄条件不满足
	needHeroNumber = 0
	if nowCfg.upgradeNeedHeroNumber:
		if not needHeroId:
			return
		if needHeroId not in heroIdList:
			return
		needHero = role.GetHero(needHeroId)
		if not needHero:
			return
		#橙色进红色, 需要紫色的英雄, 删除进阶需要一样编号英雄判断, 改为判断升阶需要英雄编号
		needHeroNumber = needHero.onumber
		if needHeroNumber != nowCfg.upgradeNeedHeroNumber:
			return
		#需要的英雄没有到达最高等级
		if needHero.GetLevel() != needHero.cfg.maxLevel:
			return
		#英雄需要的英雄要被解雇, 所以要判断是否能被解雇
		if not FireCheck(role, needHero, needHeroId):
			return
		
	heroTypeToIdSet = role.GetObj(EnumObj.En_Hero_Data_Dict)[3]
	heroType = hero.cfg.heroType
	
	with TraUpgradeHero:
		#扣除物品
		for item in nowCfg.upgradeNeedItem:
			role.DelItem(*item)
		
		#记录英雄升阶事件 -- 英雄ID, 升阶前英雄编号, 升阶后英雄编号
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveUpGradeHero, (heroId, hero.onumber, hero.cfg.nextGradeHeroNumber))
		
		#若升阶需要英雄, 删除升阶需要的英雄
		if nowCfg.upgradeNeedHeroNumber:
			#删除ID
			heroIdList.remove(needHeroId)
			#删除类型集合
			heroTypeToIdSet[heroType].discard(needHeroId)
			if not heroTypeToIdSet[heroType]:
				del heroTypeToIdSet[heroType]
			#删除英雄
			DelHero(role, needHeroId, needHeroNumber)
			
		oldStar = hero.GetStar()
		oldName = hero.GetHeroName()
		oldColorCode = hero.GetColorCode()
		
		#修改英雄类型、英雄配置
		hero.UpGrade()
		
		#属性重算
		hero.propertyGather.ReSetRecountBaseFlag()
		hero.propertyGather.ReSetRecountSkillFlag()
		if nextGradeHeroNumber in EnumGameConfig.WONDERFUL_HERO_IDS:
			WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_Inc_Hero,nextGradeHeroNumber)
		#升阶成功
		role.SendObj(Hero_OnUpgrade_Ok, (heroId, nextGradeHeroNumber))
		
	Event.TriggerEvent(Event.Eve_SubTask, role, (EnumTaskType.EnSubTask_UpgradeHero, nextGradeHeroNumber))
	
	#如果该英雄在助阵位上, 重算助阵属性
	if hero.GetHelpStationID():
		role.ResetGlobalHelpStationProperty()
	
	if oldColorCode == 4 and hero.GetColorCode() == 5:
		#英雄升橙传闻
		heroName = hero.GetHeroName()
		cRoleMgr.Msg(1, 0, GlobalPrompt.HeroGradeTips_1 % (role.GetRoleName(), oldName, heroName))
	elif oldColorCode == 5 and hero.GetColorCode() == 6:
		#英雄升红传闻
		heroName = hero.GetHeroName()
		cRoleMgr.Msg(1, 0, GlobalPrompt.HeroGradeTips_2 % (role.GetRoleName(), oldName, heroName))
	
	newStar = hero.GetStar()
	
	if oldStar== 3 and newStar == 4:
		#三星升四星
		UpdataExp(role, hero)
		cRoleMgr.Msg(1, 0, GlobalPrompt.HeroUpStar_1 % (role.GetRoleName(), oldName))
	elif oldStar == 4 and hero.GetStar() == 5:
		#四星升五星
		UpdataExp(role, hero)
		cRoleMgr.Msg(1, 0, GlobalPrompt.HeroUpStar_2 % (role.GetRoleName(), oldName))
	elif oldStar == 5 and hero.GetStar() == 6:
		#五星升六星
		UpdataExp(role, hero)
		cRoleMgr.Msg(1, 0, GlobalPrompt.HeroUpStar_3 % (role.GetRoleName(), oldName))
	elif oldStar == 6 and hero.GetStar() == 7:
		#六星升七星
		UpdataExp(role, hero)
		cRoleMgr.Msg(1, 0, GlobalPrompt.HeroUpStar_4 % (role.GetRoleName(), oldName))
	elif oldStar == 7 and hero.GetStar() == 8:
		#七星升八星
		UpdataExp(role, hero)
		cRoleMgr.Msg(1, 0, GlobalPrompt.HeroUpStar_5 % (role.GetRoleName(), oldName))
	
	if Environment.EnvIsNA():
		HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
		HalloweenNAMgr.HeroEvolution(hero.onumber)

def OnAwakenHero(role, msg):
	'''
	觉醒英雄
	@param msg: heroId
	'''
	heroId = msg
	
	hero = role.GetHero(heroId)
	if not hero:
		return
	
	#当前等阶配置
	nowCfg = HeroConfig.Hero_Base_Config.get(hero.onumber)
	if not nowCfg:
		print "GE_EXC, OnAwakenHero can not find heroNumber:(%s) in Hero_Base_Config" % hero.onumber
		return
	
	#是否可觉醒
	if not nowCfg.canAwaken:
		return

	#是否有下一阶
	awakenHeroNumber = hero.cfg.awakenHeroNumber
	if not awakenHeroNumber:
		return
	
	nextCfg = HeroConfig.Hero_Base_Config.get(awakenHeroNumber)
	if not nextCfg:
		print "GE_EXC, OnAwakenHero can not find nextGradeHeroNumber:(%s) in Hero_Base_Config" % awakenHeroNumber
		return
	
	#主角等级不足
	if role.GetLevel() < nowCfg.awakenRoleLevel:
		return
	
	#英雄等级不足
	if hero.GetLevel() < nowCfg.awakenHeroLevel:
		return
	
	#觉醒材料
	if not nowCfg.awakenNeedItem is None:
		for item in nowCfg.awakenNeedItem:
			if role.ItemCnt(item[0]) < item[1]:
				return
	
	with TraAwakenHero:
		#扣除物品
		for item in nowCfg.awakenNeedItem:
			role.DelItem(*item)
		
		#记录英雄升阶事件 -- 英雄ID, 升阶前英雄编号, 升阶后英雄编号
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveAwakenHero, (heroId, hero.onumber, hero.cfg.nextGradeHeroNumber))
		
		#修改英雄类型、英雄配置
		hero.Awaken()
		
		#属性重算
		hero.propertyGather.ReSetRecountBaseFlag()
		hero.propertyGather.ReSetRecountSkillFlag()
		if awakenHeroNumber in EnumGameConfig.WONDERFUL_HERO_IDS:
			WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_Inc_Hero,awakenHeroNumber)
		#升阶成功
		role.SendObj(Hero_OnAwaken_Ok, (heroId, awakenHeroNumber))
		
	#如果该英雄在助阵位上, 重算助阵属性
	if hero.GetHelpStationID():
		role.ResetGlobalHelpStationProperty()
		
	#觉醒提示 广播
	cRoleMgr.Msg(1, 0, GlobalPrompt.HeroAwaken_Msg_Succeed % (role.GetRoleName(), nowCfg.name, nextCfg.name))
	
	if Environment.EnvIsNA():
		HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
		HalloweenNAMgr.HeroEvolution(hero.onumber)
#===============================================================================
# 辅助
#===============================================================================
def InitHero(role, heroId, newhero):
	'''
	初始化英雄身上的管理器
	@param role:
	@param heroId:
	@param newhero:
	'''
	#初始化装备集合
	heroEquipmentDict = role.GetObj(EnumObj.En_HeroEquipments)
	heroEquipmentDict[heroId] = set()
	#英雄装备管理器
	heroEquipmentMgrDict = role.GetTempObj(EnumTempObj.enHeroEquipmentMgrDict)
	heroEquipmentMgrDict[heroId] = newhero.equipmentMgr = PackMgr.HeroEquipmentMgr(role, {}, heroId, newhero)
	#初始化神器集合
	heroArtifactDict = role.GetObj(EnumObj.En_HeroArtifact)
	heroArtifactDict[heroId] = set()
	#英雄神器管理器	
	heroArtifactMgrDict = role.GetTempObj(EnumTempObj.enHeroAtrifactMgrDict)
	heroArtifactMgrDict[heroId] = newhero.ArtifactMgr = PackMgr.HeroArtifactMgr(role, {}, heroId, newhero)
	#初始化圣器集合
	heroHallowsDict = role.GetObj(EnumObj.En_HeroHallows)
	heroHallowsDict[heroId] = set()
	#英雄圣器管理器
	heroHallowsMgrDict = role.GetTempObj(EnumTempObj.enHeroHallowsMrgDict)
	heroHallowsMgrDict[heroId] = newhero.HallowsMgr = PackMgr.HeroHallowsMgr(role, {}, heroId, newhero)
	#英雄魔灵集合
	heroMagicSpiritsDict = role.GetObj(EnumObj.En_HeroMagicSpirits)
	heroMagicSpiritsDict[heroId] = set()
	#英雄魔灵管理器
	heroMagicSpiritMgrDict = role.GetTempObj(EnumTempObj.enHeroMagicSpiritMgrDict)
	heroMagicSpiritMgrDict[heroId] = newhero.magicSpiritMgr = PackMgr.HeroMagicSpiritMgr(role, {}, heroId, newhero)
	
def FireCheck(role, hero, heroId):
	'''
	解雇, 删除时检测英雄是否能够被解雇, 删除
	@param role:
	@param hero:
	@param heroId:
	'''
	#上阵不能离队
	if hero.GetStationID():
		return
	
	#助阵不能离队
	if hero.GetHelpStationID():
		return
	
	#有装备的不能离队
	if hero.equipmentMgr.objIdDict:
		return
	
	#有装备命魂不能离队
	if role.GetTempObj(EnumTempObj.enTarotMgr).HeroHasCard(heroId):
		return
	
	#有神器的不能离队
	if role.GetObj(EnumObj.En_HeroArtifact).get(heroId):
		return
	
	#有宠物的不能离队
	if hero.GetPetID():
		return
	
	#有圣器的不能离队
	if role.GetObj(EnumObj.En_HeroHallows).get(heroId):
		return
	
	#装备了天赋卡不能离队
	if hero.IsPutTalent():
		return
	
	return True

def DelHero(role, heroId, heroNumber):
	'''
	删除英雄处理
	@param role:
	@param heroId:
	'''
	#删除英雄管理器
	del role.GetTempObj(EnumTempObj.enHeroMgr).HeroDict[heroId]
	#删除装备
	del role.GetObj(EnumObj.En_HeroEquipments)[heroId]
	del role.GetTempObj(EnumTempObj.enHeroEquipmentMgrDict)[heroId]
	#删除神器
	del role.GetObj(EnumObj.En_HeroArtifact)[heroId]
	del role.GetTempObj(EnumTempObj.enHeroAtrifactMgrDict)[heroId]
	#删除圣器
	del role.GetObj(EnumObj.En_HeroHallows)[heroId]
	del role.GetTempObj(EnumTempObj.enHeroHallowsMrgDict)[heroId]
	
	role.RemoveHeroProperty(heroId)
	
	#同步客户端解雇成功
	role.SendObj(Hero_OnFire_Ok, heroId)
	AutoLog.LogBase(role.GetRoleID(), AutoLog.eveFireHero, (heroId, heroNumber))
	
def FireHeroReturnItem(role, star, level):
	'''
	解雇紫色以下英雄返回物品
	@param role:
	@param heroType:
	'''
	itemCfg = HeroConfig.HeroLevelExpReturnItems_Dict.get(level)
	if not itemCfg:
		print "GE_EXC, HeroOperate can not find level:(%s) in HeroLevelExpReturnItems_Dict" % level
		return
	returnItem = itemCfg.get(star)
	if not returnItem:
		print "GE_EXC, HeroOperate can not find star:(%s) in HeroLevelExpReturnItems_Dict" % star
		return
	
	role.AddItem(*itemCfg.get(star))
	role.Msg(2, 0, GlobalPrompt.HeroFire_Tips % itemCfg.get(star))
	
def UpdataExp(role, hero):
	'''
	升星时更新英雄经验
	@param role:
	@param hero:
	'''
	cfg = HeroConfig.HeroLevelExp_Dict.get(hero.GetLevel())
	if not cfg:
		print "GE_EXC, UpdataExp can not find hero level (%s) in HeroLevelExp_Dict" % hero.GetLevel()
		return
	nowExp = cfg.get(hero.GetStar())
	if not nowExp:
		return
	hero.SetExp(nowExp)
	role.SendObj(LevelEXP.Hero_Exp, (hero.oid, nowExp))
	
	
def OnCuiLianHero(role, msg):
	'''
	请求英雄淬炼
	@param role:
	@param msg:(英雄ID, 请求英雄淬炼次数)
	'''
	heroId, MsgCnt = msg
	if role.GetLevel() < EnumGameConfig.CuiLian_Level:
		return
	hero = role.GetHero(heroId)
	
	#参数错误
	if not hero:
		return
	if MsgCnt <= 0:
		return
	#到达最高级
	PreNum = hero.GetCuiLian()
	if PreNum + MsgCnt > hero.GetCuiLian_MaxCnt():
		return
	#淬炼石不足
	if MsgCnt > role.ItemCnt(EnumGameConfig.CuiLianShi_Coding):
		return
	
	with TraCuiLianHero:
		role.DelItem(EnumGameConfig.CuiLianShi_Coding, MsgCnt)
		hero.AddCuiLian(MsgCnt)
	role.SendObj(CuiLian_Dict, role.GetObj(EnumObj.En_RoleCuiLian))
	hero.GetPropertyGather().ReSetRecountCuiLianFlag()
	#提示
	CL_Dict = HeroConfig.CuiLianShi_Dict
	tip = (CL_Dict[1], CL_Dict[4], CL_Dict[6], CL_Dict[5], CL_Dict[7], CL_Dict[8], CL_Dict[9], CL_Dict[12], CL_Dict[13],)
	tip = tuple([i * MsgCnt for i in tip])
	rewardPrompt = GlobalPrompt.CuiLian_Tips_2 % tip
	role.Msg(2, 0, rewardPrompt)

def OnCuiLianRole(role, msg):
	'''
	请求主角淬炼
	@param role:
	@param msg:请求主角淬炼次数
	'''
	if role.GetLevel() < EnumGameConfig.CuiLian_Level:
		return
	#参数错误
	if 0 >= msg:
		return
	#到达最高级
	PreNum = role.GetCuiLian()
	if PreNum + msg > role.GetCuiLian_MaxCnt():
		return
	#淬炼石不足
	if msg > role.ItemCnt(EnumGameConfig.CuiLianShi_Coding):
		return
	
	with TraCuiLianRole:
		role.DelItem(EnumGameConfig.CuiLianShi_Coding, msg)
		role.AddCuiLian(msg)
	role.SendObj(CuiLian_Dict, role.GetObj(EnumObj.En_RoleCuiLian))
	role.GetPropertyGather().ReSetRecountCuiLianFlag()
	#提示
	CL_Dict = HeroConfig.CuiLianShi_Dict
	tip = (CL_Dict[1], CL_Dict[4], CL_Dict[5], CL_Dict[7], CL_Dict[8], CL_Dict[9], CL_Dict[12], CL_Dict[13],)
	tip = tuple([i * msg for i in tip])
	rewardPrompt = GlobalPrompt.CuiLian_Tips_1 % tip
	role.Msg(2, 0, rewardPrompt)


def RequestHaloUpLevel(role, msg):
	'''
	升级转生光环
	'''
	if role.GetLevel() < RoleBaseConfig.ROLE_MAX_LEVEL:
		return
	
	#转生后才能升级光环
	if not role.GetZhuanShengLevel():
		return
	
	#可能已经是最大光环等级了
	haloLevel = role.GetZhuanShengHaloLevel()
	if haloLevel >= HeroConfig.MaxZhuanShengHaloLv:
		return
	
	config = HeroConfig.ZhuangShengHaloConfigDict.get(haloLevel)
	if not config:
		print "GE_EXC, error while config = ZhuanShengConfig.ZhuangShengHaloConfigDict.get(haloLevel) (s%)" % haloLevel
		return
	
	if role.GetExp() - RoleBaseConfig.ROLE_MAX_EXP < config.NeedExp:
		return
	
	#这里加日志
	with TraZhuanShengHaloLevelUp:
		role.SetZhuanShengHaloLevel(haloLevel + 1)
	
	#重算转生属性
	role.GetPropertyGather().ResetRecountZhuanShengFlag()
	#重算助阵属性
	role.ResetGlobalHelpStationProperty()
	#重算光环基础属性
	role.ResetGlobalZhuanShengHaloBaseProperty()
	
	#重算装备属性
	role.GetPropertyGather().ReSetRecountEquipmentZhuanShengFlag()
		
	for hero in role.GetAllHero().values():
		hero.GetPropertyGather().ResetRecountZhuanShengFlag()
		hero.GetPropertyGather().ReSetRecountEquipmentZhuanShengFlag()


def RequestHeroZhuanSheng(role, msg):
	'''
	英雄转生
	'''
	heroID = msg
	hero = role.GetHero(heroID)
	if not hero:
		return
	
	if not hero.cfg.canZhuanSheng:
		return
	
	if role.GetZhuanShengLevel() < hero.cfg.zhuanshengNeedRoleZSLv:
		return
	
	if hero.GetLevel() < hero.cfg.zhuanshengNeedLevel:
		return
	
	zhuanshengHeroNumber = hero.cfg.zhuanshengHeroNumber
	if not zhuanshengHeroNumber:
		return
	
	nextCfg = HeroConfig.Hero_Base_Config.get(zhuanshengHeroNumber)
	if not nextCfg:
		print "GE_EXC, OnUpgradeHero can not find zhuanshengHeroNumber:(%s) in Hero_Base_Config" % zhuanshengHeroNumber
		return
	
	if not hero.cfg.zhuanshengNeedItem:
		return
	
	itemCoding, itemCnt = hero.cfg.zhuanshengNeedItem
	if role.ItemCnt(itemCoding) < itemCnt:
		return
	
	if role.GetMoney() < hero.cfg.zhuanshengNeedMoney:
		return
	
	
	oldHeroZhuanShengLevel = hero.cfg.zhuanshengLevel
	oldHeroName = hero.cfg.name
	with TraHeroZhuanSheng:
		role.DecMoney(hero.cfg.zhuanshengNeedMoney)
		role.DelItem(itemCoding, itemCnt)
		
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveHeroZhuanSheng, (heroID, hero.onumber, hero.cfg.zhuanshengHeroNumber))
		hero.ZhuanSheng()
	
	#重算转生属性
	hero.propertyGather.ResetRecountZhuanShengFlag()
	#如果该英雄在助阵位上, 重算助阵属性
	if hero.GetHelpStationID():
		role.ResetGlobalHelpStationProperty()

	#同步客户端
	role.SendObj(SyncHeroZhuanShengOk, (heroID, zhuanshengHeroNumber))
	
	if oldHeroZhuanShengLevel > 0:
		cRoleMgr.Msg(1, 0, GlobalPrompt.ZhuanShengHeroTips2 % (role.GetRoleName(), oldHeroZhuanShengLevel, oldHeroName, hero.cfg.zhuanshengLevel, hero.cfg.name))
	elif oldHeroZhuanShengLevel == 0:
		cRoleMgr.Msg(1, 0, GlobalPrompt.ZhuanShengHeroTips1 % (role.GetRoleName(), oldHeroName, hero.cfg.zhuanshengLevel, hero.cfg.name))


def RequestRoleZhuanSheng(role, msg):
	'''
	主角转生
	'''
	if role.GetLevel() < RoleBaseConfig.ROLE_MAX_LEVEL:
		return
	
	if role.GetExp() < RoleBaseConfig.ROLE_MAX_EXP:
		return
	
	zhuanShengLv = role.GetZhuanShengLevel()
	
	config = HeroConfig.RoleZhuanShengConfigDict.get(zhuanShengLv)
	if not config:
		return
	
	needCoding, needCnt = config.NeedItem
	
	#最大转生等级
	if zhuanShengLv >= HeroConfig.MaxRoleZhuanShengLv:
		return
	
	if role.GetMoney() < config.NeedMoney:
		return
	
	if role.ItemCnt(needCoding) < needCnt:
		return
	
	if role.GetZhuanShengHaloLevel() < config.NeedHaloLv:
		return
	
	with TraRoleZhuanSheng:
		role.DecMoney(config.NeedMoney)
		role.DelItem(needCoding, needCnt)
		role.SetZhuanShengLevel(zhuanShengLv + 1)
		
	role.GetPropertyGather().ResetRecountZhuanShengFlag()
	cRoleMgr.Msg(1, 0, GlobalPrompt.ZhuanShengRoleTips % (role.GetRoleName(), (zhuanShengLv + 1)))


def SyncRoleCuiLianData(role, param):
	role.SendObj(CuiLian_Dict, role.GetObj(EnumObj.En_RoleCuiLian))
	
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleCuiLianData)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Hero_Tavern", "请求打开酒馆面板"), OpenTavernPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Hero_ZhaoMu", "招募英雄"), OnHeroZhaoMu)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Hero_OnFire", "辞退英雄"), OnHeroFire)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Hero_OnUseHeroExpItem", "使用英雄经验丹物品"), OnUseHeroExpItem)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Hero_OnUpgradeHero", "进阶英雄"), OnUpgradeHero)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Hero_OnUpgradeRole", "请求主角进阶"), OnRoleUpgrade)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Hero_OnAwakenHero", "觉醒英雄"), OnAwakenHero)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Hero_OnCuiLianHero", "英雄使用淬炼石"), OnCuiLianHero)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Hero_OnCuiLianRole", "主角使用淬炼石"), OnCuiLianRole)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestHeroZhuanSheng", "客户端请求英雄转生"), RequestHeroZhuanSheng)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestRoleZhuanShengHalo", "客户端请求主角转生"), RequestRoleZhuanSheng)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestUpLevelZhuanShengHalo", "客户端请求升级转生光环"), RequestHaloUpLevel)
