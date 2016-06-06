#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Item.EquipmentForing")
#===============================================================================
# 装备强化，进阶，神铸， 附魔
#===============================================================================
import random
import Environment
import cProcess
import cRoleMgr
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from Game.Role.Data import EnumTempObj, EnumCD, EnumInt32, EnumInt16
from Game.Role.Obj import Base
from Game.Role import Event
from Game.Role.Config import RoleBaseConfig

if "_HasLoad" not in dir():
	Strengthen_Dict = {} #装备强化
	Equipment_Upgrade_Dict = {} #装备进阶
	Equipment_Godcast_Dict = {} #装备神铸
	Equipment_Enchant_Dict = {} #装备附魔
	Equipment_WashBase_Dict = {}#装备洗练星级基础配置
	Equipment_WashMaxPro_Dict = {}#装备洗练属性对应的最大值配置
	Equipment_WashStar_Dict = {}#装备洗练洗练度对应的星级
	Equipment_UnlockCost_Dict = {}#开启额外的洗练属性消耗
	Equipment_ZhuanSheng_Dict = {}	#装备转生
	Equipment_Evolve_Dict = {}	#装备进化
	
	FORING_CD = 300 #V4以下每次强化加的时间
	MAX_FORING_CD = 1800 #最大的CD时间
	Strengthen_pro = 800 #双倍强化概率
	VIP_LEVEL_STRLEN = 7 #开启双倍强化的贵族等级
	VIP_STRENG_NO_CD = 4 #强化无CD
	OnekeyStrengthenLevel = 35 #一键强化等级限制
	OnekeyStrengthenVIP = 5		#一键强化vip限制
	OneKeyWashNeedStar = 12   #自动洗练需要洗练度星级
	
	MAX_ENCHANT_LEVEL = 10	#最大附魔等级
	MIN_CAN_ENCHANT_LEVEL = 60	#最低附魔等级
	#消息
	Equipment_UpdateStrengthenLevel = AutoMessage.AllotMessage("Equipment_UpdateStrengthenLevel", "更新装备强化等级")
	Equipment_UpGradeOK = AutoMessage.AllotMessage("Equipment_UpGradeOK", "装备进阶成功")
	Equipment_GodcastOK = AutoMessage.AllotMessage("Equipment_GodcastOK", "装备神铸成功")
	Equipment_EnchantOK = AutoMessage.AllotMessage("Equipment_EnchantOK", "装备附魔成功")
	Equipment_WashData = AutoMessage.AllotMessage("Equipment_WashData", "同步装备洗练属性")
	Equipment_ZhuanShengOK = AutoMessage.AllotMessage("Equipment_ZhuanShengOK", "装备转生成功")
	Equipment_EvolveOK = AutoMessage.AllotMessage("Equipment_EvolveOK", "装备进化成功")
	Equipment_OnekeyWashStop = AutoMessage.AllotMessage("Equipment_OnekeyWashStop", "装备自动洗练停止")
	#日志
	TraStrengthenEquipment = AutoLog.AutoTransaction("TraStrengthenEquipment1", "强化装备")
	TraOnekeyStrengthenEquipment = AutoLog.AutoTransaction("TraOnekeyStrengthenEquipment", "一键强化装备")
	TraUpGradeEquipment_log = AutoLog.AutoTransaction("TraUpGradeEquipment", "装备升阶")
	GodcastEquipment_log = AutoLog.AutoTransaction("GodcastEquipment", "装备神铸")
	QuickCD = AutoLog.AutoTransaction("QuickCD", "装备强化CD加速冷却")
	TraEnchantEquipment = AutoLog.AutoTransaction("TraEnchantEquipment", "装备附魔")
	EquipmentWashCost = AutoLog.AutoTransaction("EquipmentWashCost", "装备洗练消耗")
	EquipmentOneKeyWashCost = AutoLog.AutoTransaction("EquipmentOneKeyWashCost", "装备自动洗练消耗")
	EquipmentWashJiCheng = AutoLog.AutoTransaction("EquipmentWashJiCheng", "装备洗练继承消耗")
	EquipmentUnlockCost = AutoLog.AutoTransaction("EquipmentUnlockCost", "装备开启新的洗练属性消耗")
	EquipmentWashStone = AutoLog.AutoTransaction("EquipmentWashStone", "装备洗练使用升星石升星")
	Equipment_ZhuanSheng_log = AutoLog.AutoTransaction("Equipment_ZhuanSheng_log", "装备转生")
	Equipment_Evolve_log = AutoLog.AutoTransaction("Equipment_Evolve_log", "装备进化")
	
def OnStrengthenEquipment(role, msg):
	'''
	强化装备
	@param role:
	@param msg:装备ID
	'''
	eId = msg
	
	#版本特权判断
	if Environment.EnvIsNA():
		#北美版
		if not role.GetCD(EnumCD.Card_Quarter) and not role.GetCD(EnumCD.Card_HalfYear) and not role.GetCD(EnumCD.Card_Year):
			if role.GetCD(EnumCD.ForbidEquipmentCD) > 0:
				return
	else:
		#其他版本
		#小于贵族4 判断CD
		if role.GetVIP() < VIP_STRENG_NO_CD:
			if role.GetCD(EnumCD.ForbidEquipmentCD) > 0:
				return
			
	globaldict = role.GetTempObj(EnumTempObj.enGlobalItemMgr)
	equipment = globaldict.get(eId)
	if not equipment:
		return
	if not equipment.cfg.Strength:
		return
	oldLevel = equipment.GetStrengthenLevel()
	if oldLevel >= RoleBaseConfig.ROLE_MAX_LEVEL:
		return
	newlevel = oldLevel + 1
	roleLevel = role.GetLevel()
	if newlevel > roleLevel:#强化等级必须小于等于人物等级 
		return
	
	posType = equipment.cfg.posType
	if posType < 1 or posType > 6:
		#不是装备
		return
	
	key = posType, newlevel
	global Strengthen_Dict
	cfg = Strengthen_Dict.get(key)
	if not cfg:
		print "GE_EXC, can not find cfg in Strengthen_Dict, posType(%s),level(%s)" % (posType, newlevel)
		return
	
	
	tMoney = role.GetMoney()
	
	if tMoney < cfg.needMoney:
		return
	
	with TraStrengthenEquipment:
		#版本特权判断
		if Environment.EnvIsNA():
			#北美版
			if not role.GetCD(EnumCD.Card_Quarter) and not role.GetCD(EnumCD.Card_HalfYear) and not role.GetCD(EnumCD.Card_Year):
				cd_times = role.GetCD(EnumCD.EquipmentForintCD)
				if cd_times + FORING_CD >= MAX_FORING_CD:
					role.SetCD(EnumCD.ForbidEquipmentCD, cd_times + FORING_CD)
				role.SetCD(EnumCD.EquipmentForintCD, cd_times + FORING_CD)
		else:
			#其他版本
			if role.GetVIP() < VIP_STRENG_NO_CD:
				cd_times = role.GetCD(EnumCD.EquipmentForintCD)
				if cd_times + FORING_CD >= MAX_FORING_CD:
					role.SetCD(EnumCD.ForbidEquipmentCD, cd_times + FORING_CD)
				role.SetCD(EnumCD.EquipmentForintCD, cd_times + FORING_CD)
				
		global Strengthen_pro
		state = False
		if role.GetVIP() >= VIP_LEVEL_STRLEN:#双倍强化
			if random.randint(1, 10000) <= Strengthen_pro:
				if newlevel < RoleBaseConfig.ROLE_MAX_LEVEL:
					newlevel += 1
					state = True
		#扣除金币
		role.DecMoney(cfg.needMoney)
			
		equipment.SetStrengthenLevel(newlevel)
		if equipment.owner:
			#强化属性字典需要重算属性
			equipment.ResetStrengthen()
			#设置装备属性重算
			equipment.owner.GetPropertyGather().ReSetRecountEquipmentStrengthenFlag()
		#北美通用活动
		if Environment.EnvIsNA():
			HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
			HalloweenNAMgr.EquipmentStrengthen()
		#同步客户端
		role.SendObj(Equipment_UpdateStrengthenLevel, (eId, newlevel))
		
		Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_EquipmentForing, 1))
		
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveStrengthenEquipment, (eId, newlevel))
		if state:
			role.Msg(2, 0, GlobalPrompt.EQUIPMENT_STRENG_MSG)
			
def OnekeyStrengthenEquipment(role, msg):
	'''
	一键强化装备，仅在繁体版本有这个功能
	@param role:
	@param msg:装备ID
	'''
	#语言环境判断
	if not Environment.EnvIsFT():
		return
	if role.GetLevel() < OnekeyStrengthenLevel:
		return
	if role.GetVIP() < OnekeyStrengthenVIP:
		return
	eId = msg
	globaldict = role.GetTempObj(EnumTempObj.enGlobalItemMgr)
	equipment = globaldict.get(eId)
	if not equipment:
		return
	if not equipment.cfg.Strength:
		return
	oldLevel = equipment.GetStrengthenLevel()	
	if oldLevel >= RoleBaseConfig.ROLE_MAX_LEVEL:
		return
	roleLevel = role.GetLevel()
	if oldLevel >= roleLevel:
		return
	posType = equipment.cfg.posType
	if posType < 1 or posType > 6:
		#不是装备
		return
	newlevel = oldLevel
	needmoney = 0
	#记录双倍强化的次数
	doublestrenth = 0
	while newlevel < roleLevel:
		newlevel += 1
		key = posType, newlevel
		global Strengthen_Dict
		cfg = Strengthen_Dict.get(key)
		if not cfg:
			print "GE_EXC, can not find cfg in Strengthen_Dict, posType(%s),level(%s)" % (posType, newlevel)
			return
		needmoney += cfg.needMoney
		if needmoney > role.GetMoney():
			needmoney -= cfg.needMoney
			newlevel -= 1
			break
		if role.GetVIP() >= VIP_LEVEL_STRLEN:#双倍强化
			if random.randint(1, 10000) <= Strengthen_pro:
				if newlevel < RoleBaseConfig.ROLE_MAX_LEVEL:
					newlevel += 1
					doublestrenth += 1

	if not newlevel > oldLevel:
		return
	
	with TraOnekeyStrengthenEquipment:
		#扣钱
		role.DecMoney(needmoney)
		#强化
		equipment.SetStrengthenLevel(newlevel)
		
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveOnekeyStrengthenEquipment, (eId, newlevel))

	if equipment.owner:
		#强化属性字典需要重算属性
		equipment.ResetStrengthen()
		#设置装备属性重算
		equipment.owner.GetPropertyGather().ReSetRecountEquipmentStrengthenFlag()
	
	#同步客户端
	role.SendObj(Equipment_UpdateStrengthenLevel, (eId, newlevel))
	
	
	#双倍强化的情况
	if role.GetVIP() >= VIP_LEVEL_STRLEN:
		#金币先花完的情况
		if newlevel < roleLevel:
			role.Msg(2, 0, GlobalPrompt.EQUIPMENT_OnekeySTRENG_MSG1 % doublestrenth)
		else:
			role.Msg(2, 0, GlobalPrompt.EQUIPMENT_OnekeySTRENG_MSG2 % doublestrenth)
	#没有双倍强化的情况
	else:
		if newlevel < roleLevel:
			role.Msg(2, 0, GlobalPrompt.EQUIPMENT_OnekeySTRENG_MSG3)
		else:
			role.Msg(2, 0, GlobalPrompt.EQUIPMENT_OnekeySTRENG_MSG4)


def EquipmentForing_QuickCD(role, msg):
	'''
	请求加速冷却
	@param role:
	@param msg:
	'''
	forbid_cd = role.GetCD(EnumCD.ForbidEquipmentCD)
	if forbid_cd < 0:
		return
	#消耗的神石或魔晶=冷却时间（分钟）*1，向上取整
	Min = forbid_cd/60
	if forbid_cd % 60 != 0:
		Min += 1
	if role.GetRMB() < Min:
		return
	with QuickCD:
		role.DecRMB(Min)
		role.SetCD(EnumCD.EquipmentForintCD, 0)
		role.SetCD(EnumCD.ForbidEquipmentCD, 0)
		
def UpGradeEquipment(role, msg):
	'''
	装备升阶
	@param role:
	@param msg:装备ID
	'''
	eId = msg
	globaldict = role.GetTempObj(EnumTempObj.enGlobalItemMgr)
	equipment = globaldict.get(eId)
	if not equipment:
		return
	if not equipment.cfg.UpGrade:
		return

	global Equipment_Upgrade_Dict
	srcType = equipment.otype
	cfg = Equipment_Upgrade_Dict.get(srcType)
	if not cfg:
		return
	if role.GetLevel() < cfg.needLevel:
		return
#	owner = equipment.owner
#	if owner and owner.GetLevel() < cfg.needLevel:
#		role.Msg(2, 0, GlobalPrompt.UpGradeEquipment_Failt)
#		return
	
	packageMgr = role.GetTempObj(EnumTempObj.enPackMgr)#人物背包管理
	if cfg.cnt1 > 0:
		if packageMgr.ItemCnt(cfg.itemType1) < cfg.cnt1:
			return
	if cfg.cnt2 > 0:
		if packageMgr.ItemCnt(cfg.itemType2) < cfg.cnt2:
			return
	if cfg.cnt3 > 0:
		if packageMgr.ItemCnt(cfg.itemType3) < cfg.cnt3:
			return
	if cfg.cnt4 > 0:
		if packageMgr.ItemCnt(cfg.itemType4) < cfg.cnt4:
			return
	
	desType = cfg.desType #新装备类型
	fun = Base.Obj_Type_Fun.get(desType)
	if not fun:
		print "GE_EXC, UpGradeEquipment can not find fun , coding = (%s)" % desType
		return
	
	with TraUpGradeEquipment_log:
		#扣物品
		if cfg.cnt1 > 0:
			if role.DelItem(cfg.itemType1, cfg.cnt1) < cfg.cnt1:
				return
		if cfg.cnt2 > 0:
			if role.DelItem(cfg.itemType2, cfg.cnt2) < cfg.cnt2:
				return
		if cfg.cnt3 > 0:
			if role.DelItem(cfg.itemType3, cfg.cnt3) < cfg.cnt3:
				return
		if cfg.cnt4 > 0:
			if role.DelItem(cfg.itemType4, cfg.cnt4) < cfg.cnt4:
				return
		
		#-----------------------------------------------------------
		owner = equipment.owner

		owerId = 0
		mgr = equipment.package
		equipmentIdSet = None
		if mgr.heroId:
			owerId = mgr.heroId
			equipmentIdSet = role.GetObj(mgr.ObjEnumIndex).get(owerId)
		else:
			owerId = role.GetRoleID()
			equipmentIdSet = role.GetObj(mgr.ObjEnumIndex)
		#删除数据
		equipmentIdSet.discard(eId)
		del mgr.objIdDict[eId]

		equipment.package = None
		equipment.owner = None
		cd_dict = mgr.codingGather.get(srcType)
		del cd_dict[eId]
		if not cd_dict:
			del mgr.codingGather[srcType]
		#全局管理器删除记录
		del globaldict[eId]

		#构建数据对象
		newId = cProcess.AllotGUID64()
		obj = newId, desType, 1, {}
		#根据注册函数，数据对象，生成物品对象
		newItem = fun(role, obj)

		newItem.package = mgr
		newItem.AfterCreate()
		if owner:
			newItem.owner = owner
		else:
			newItem.owner = None	
		#角色数组直接更新
		equipmentIdSet.add(newId)
		#加入内部管理器
		mgr.objIdDict[newId] = newItem
		itemDict = mgr.codingGather.get(desType)
		if not itemDict:
			mgr.codingGather[desType] = itemDict = {}
		itemDict[newId] = newItem	
		#加入全局管理器
		globaldict[newId] = newItem		
		if newItem.cfg.posType <= 6:
			#强化等级保留
			newItem.SetStrengthenLevel(equipment.GetStrengthenLevel())
			#保留宝石
			newItem.SetEquipmentGemlist(equipment.GetEquipmentGem())
			#保留附魔等级
			newItem.SetEnchantLevel(equipment.GetEnchantLevel())
			#保留洗练属性
			newItem.SetWashExtendHole(equipment.GetWashExtendHole())
			newItem.SetWashProp(equipment.GetWashProp())
			
			if owner:
				#重算属性
				owner.GetPropertyGather().ReSetRecountEquipmentFlag()
				#触发套装属性
				if equipment.cfg.suitId or newItem.cfg.suitId:
					newItem.package.ResetStrengthenSuit()
		#触发事件
		Event.TriggerEvent(Event.Eve_AfterEquipmentUpgrade, role, desType)
		#记录日志
		AutoLog.LogObj(role.GetRoleID(), AutoLog.eveUpGradeEquipment, newId, newItem.otype, newItem.oint, newItem.odata, (eId, srcType))
		#同步客户端
		role.SendObj(Equipment_UpGradeOK, (newId, eId, owerId, newItem.GetSyncData(), ))		
#神铸
def GodcastEquipment(role, msg):
	'''
	装备神铸
	@param role:
	@param msg:装备ID
	'''
	eId = msg
	globaldict = role.GetTempObj(EnumTempObj.enGlobalItemMgr)
	equipment = globaldict.get(eId)
	if not equipment:
		return
	#该装备是否可神铸
	if not equipment.cfg.forging:
		return
	global Equipment_Godcast_Dict
	srcType = equipment.otype
	cfg = Equipment_Godcast_Dict.get(srcType)
	if not cfg:
		
		return
	if role.GetLevel() < cfg.needLevel:
		return
	packageMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	if cfg.cnt1 > 0:
		if packageMgr.ItemCnt(cfg.itemType1) < cfg.cnt1:
			return
	if cfg.cnt2 > 0:
		if packageMgr.ItemCnt(cfg.itemType2) < cfg.cnt2:
			return
	if cfg.cnt3 > 0:
		if packageMgr.ItemCnt(cfg.itemType3) < cfg.cnt3:
			return
	if cfg.cnt4 > 0:
		if packageMgr.ItemCnt(cfg.itemType4) < cfg.cnt4:
			return
	
	desType = cfg.desType #新装备类型
	fun = Base.Obj_Type_Fun.get(desType)
	if not fun:
		print "GE_EXC, UpGradeEquipment can not find fun , coding = (%s)" % desType
		return
	
	with GodcastEquipment_log:
		#扣物品
		if cfg.cnt1 > 0:
			if role.DelItem(cfg.itemType1, cfg.cnt1) < cfg.cnt1:
				return
		if cfg.cnt2 > 0:
			if role.DelItem(cfg.itemType2, cfg.cnt2) < cfg.cnt2:
				return
		if cfg.cnt3 > 0:
			if role.DelItem(cfg.itemType3, cfg.cnt3) < cfg.cnt3:
				return
		if cfg.cnt4 > 0:
			if role.DelItem(cfg.itemType4, cfg.cnt4) < cfg.cnt4:
				return
		
		#-----------------------------------------------------------
		owner = equipment.owner
		
		owerId = 0
		mgr = equipment.package
		
		equipmentIdSet = None
		if mgr.heroId:
			owerId = mgr.heroId
			equipmentIdSet = role.GetObj(mgr.ObjEnumIndex).get(owerId)
		else:
			owerId = role.GetRoleID()
			equipmentIdSet = role.GetObj(mgr.ObjEnumIndex)
		#删除数据
		equipmentIdSet.discard(eId)
		del mgr.objIdDict[eId]
		
		
		equipment.package = None
		equipment.owner = None
		cd_dict = mgr.codingGather.get(srcType)
		del cd_dict[eId]
		if not cd_dict:
			del mgr.codingGather[srcType]
		#全局管理器删除记录
		del globaldict[eId]

		#构建数据对象
		newId = cProcess.AllotGUID64()
		obj = newId, desType, 1, {}
		#根据注册函数，数据对象，生成物品对象
		newItem = fun(role, obj)
		
		newItem.package = mgr
		newItem.AfterCreate()
		if owner:
			newItem.owner = owner
		else:
			newItem.owner = None	
		#角色数组直接更新
		equipmentIdSet.add(newId)
		#加入内部管理器
		mgr.objIdDict[newId] = newItem
		itemDict = mgr.codingGather.get(desType)
		if not itemDict:
			mgr.codingGather[desType] = itemDict = {}
		itemDict[newId] = newItem	
		#加入全局管理器
		globaldict[newId] = newItem		
		if newItem.cfg.posType <= 6:
			#强化等级保留
			newItem.SetStrengthenLevel(equipment.GetStrengthenLevel())
			#保留宝石
			newItem.SetEquipmentGemlist(equipment.GetEquipmentGem())
			#保留附魔等级
			newItem.SetEnchantLevel(equipment.GetEnchantLevel())
			#保留洗练属性
			newItem.SetWashExtendHole(equipment.GetWashExtendHole())
			newItem.SetWashProp(equipment.GetWashProp())
			
			if owner:
				#重算属性
				owner.GetPropertyGather().ReSetRecountEquipmentFlag()
				#触发套装属性
				if equipment.cfg.suitId or newItem.cfg.suitId:
					newItem.package.ResetStrengthenSuit()
		#记录日志
		AutoLog.LogObj(role.GetRoleID(), AutoLog.eveGodcastEquipment, newId, newItem.otype, newItem.oint, newItem.odata, (eId, srcType))
		#同步客户端
		role.SendObj(Equipment_GodcastOK, (newId, eId, owerId, newItem.GetSyncData(), ))

def EnchantEquipment(role, param):
	'''
	请求附魔装备
	@param role:
	@param param:
	'''
	eId = param
	
	globaldict = role.GetTempObj(EnumTempObj.enGlobalItemMgr)
	equipment = globaldict.get(eId)
	if not equipment:
		return
	
	if role.GetLevel() < MIN_CAN_ENCHANT_LEVEL:
		return
	
	oldLevel = equipment.GetEnchantLevel()
	if oldLevel >= MAX_ENCHANT_LEVEL:
		return

	
	posType = equipment.cfg.posType
	if posType < 1 or posType > 6:
		#不是装备
		return
	if not equipment.cfg.Strength:#不能强化的装备不能附魔
		return
	newLevel = oldLevel + 1
	enchantCfg = Equipment_Enchant_Dict.get(newLevel)
	if not enchantCfg:
		print "GE_EXC,can not find enchantLevel(%s) in EnchantEquipment" % newLevel
		return

	itemCoding, cnt = enchantCfg.needItem
	if role.ItemCnt(itemCoding) < cnt:
		return
	
	with TraEnchantEquipment:
		if role.DelItem(itemCoding, cnt) < cnt:
			return
		equipment.SetEnchantLevel(newLevel)
		
		if equipment.owner:
			#强化属性字典需要重算属性
			equipment.ResetStrengthen()
			#设置装备属性重算
			equipment.owner.GetPropertyGather().ReSetRecountEquipmentStrengthenFlag()
		#同步客户端
		role.SendObj(Equipment_EnchantOK, (eId, newLevel))
		
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveEnchantEquipment, (eId, newLevel))
		role.Msg(2, 0, GlobalPrompt.Enchant_Suc_Msg % (equipment.cfg.name, newLevel))
		if enchantCfg.IsAbroad:#发世界公告
			cRoleMgr.Msg(11, 0, GlobalPrompt.Enchant_Abroad_Msg % (role.GetRoleName(), equipment.cfg.coding, 0,newLevel))

def RequestEquipmentWashUnlock(role, param):
	'''
	请求解锁装备的洗练锁
	@param role:
	@param param:
	'''
	eId = param
	globaldict = role.GetTempObj(EnumTempObj.enGlobalItemMgr)
	equipment = globaldict.get(eId)
	if not equipment:
		return
	if not equipment.GetWashProp():
		return
	#获取装备已解锁的数量
	extendHole = equipment.GetWashExtendHole()
	if extendHole >= equipment.cfg.UnlockWash:
		return
	
	costCfg = Equipment_UnlockCost_Dict.get(extendHole+1)
	if not costCfg:
		print "GE_EXC,can not find unlockNum(%s) in RequestEquipmentWashUnlock" % (extendHole+1)
		return
	unbindRMB = costCfg.unbindRMB
	if role.GetUnbindRMB() < unbindRMB:
		return
	
	with EquipmentUnlockCost:
		role.DecUnbindRMB(unbindRMB)
		equipment.SetWashExtendHole(extendHole+1)
		
		#根据该装备的洗练度获取该装备可以洗练出的星级
		starcfg = None
		washNum = role.GetI32(EnumInt32.EquipmentWashNum)
		for washList, cfg in Equipment_WashStar_Dict.iteritems():
			if washList[0] <= washNum <= washList[1]:
				starcfg = cfg
				break
		if not starcfg:
			print "GE_EXC, can not find washNum(%s) in RequestEquipmentWash" % washNum
			return
		oldWashPro = equipment.GetWashProp()
		ptDict = RandomNewProp(1, oldWashPro.keys(), starcfg)
		equipment.AddNewWashProp(ptDict)
		
		RefineProp = equipment.GetWashRefineProp()
		#假如存在未保存属性
		if RefineProp:
			refinePtDict =  RandomNewProp(1, RefineProp.keys(), starcfg)
			equipment.AddDefineWashPro(refinePtDict)
			
		if equipment.owner:
			equipment.owner.GetPropertyGather().ReSetRecountEquipmentWashFlag()
		role.SendObj(Equipment_WashData, [4, eId, equipment.GetWashProp(), equipment.GetWashRefineProp(), extendHole+1])
		
def RequestEquipmentWashInheritance(role, param):
	'''
	装备洗练属性继承
	@param role:
	'''
	eId, IeId = param	#前为消耗的装备，后为继承洗练属性的装备
	
	globaldict = role.GetTempObj(EnumTempObj.enGlobalItemMgr)
	equipment = globaldict.get(eId)
	if not equipment:
		return
	Iequipment = globaldict.get(IeId)
	if not Iequipment:
		return
	#只能是高洗练等级的可以继承低洗练等级的
	if equipment.cfg.WashLevel >= Iequipment.cfg.WashLevel:
		return
	#继承需要相同的部位才行
	if equipment.cfg.posType != Iequipment.cfg.posType:
		return
	
	costRMB = 0
	if Environment.EnvIsNA():
		costRMB = EnumGameConfig.EQUIPMENT_DEC_JICHENG_COST_NA
	else:
		costRMB = EnumGameConfig.EQUIPMENT_DEC_JICHENG_COST
	if role.GetUnbindRMB() < costRMB:
		return
	#低级装备必须得有洗练属性才能被继承
	washProp = equipment.GetWashProp()
	if not washProp:
		return
	#获取额外开启的洗练条数
	extendHole = equipment.GetWashExtendHole()
	with EquipmentWashJiCheng:
		role.DecUnbindRMB(costRMB)
		#继承的时候，低级的装备洗练数据直接覆盖高级装备，低级的再清空
		#获取高级装备的额外开孔数
		IextendHole = Iequipment.GetWashExtendHole()
		if IextendHole <= extendHole:
			#开孔数相等或小于低级装备的，直接覆盖洗练属性
			Iequipment.SetWashProp(washProp)
			Iequipment.SetWashExtendHole(extendHole)
		else:
			#高级开孔数大于低级额外开孔数，多出来的需要随机生成新的属性
			#根据该装备的洗练度获取该装备可以洗练出的星级
			global Equipment_WashStar_Dict
			starcfg = None
			washNum = role.GetI32(EnumInt32.EquipmentWashNum)
			for washList, cfg in Equipment_WashStar_Dict.iteritems():
				if washList[0] <= washNum <= washList[1]:
					starcfg = cfg
					break
			if not starcfg:
				print "GE_EXC, can not find washNum(%s) in RequestEquipmentWash" % washNum
				return
			#需要重新刷新的属性条数
			FreshNum = IextendHole - extendHole
			#获取随机生成的新属性
			ptDict = RandomNewProp(FreshNum, washProp.keys(), starcfg)
			if ptDict:
				for pt, pv in ptDict.iteritems():
					washProp[pt] = pv
		
			Iequipment.SetWashProp(washProp)
			Iequipment.SetWashExtendHole(extendHole)
		
		equipment.ReSetWashProp()
		equipment.ReSetRefineProp()
		equipment.ReSetWashExtendHole()
		#重算
		if Iequipment.owner:
			Iequipment.owner.GetPropertyGather().ReSetRecountEquipmentWashFlag()
		if equipment.owner:
			equipment.owner.GetPropertyGather().ReSetRecountEquipmentWashFlag()
			
		role.SendObj(Equipment_WashData, [3, IeId, Iequipment.GetWashProp(), {}, Iequipment.GetWashExtendHole()])
		
def RequestEquipmentWashSave(role, param):
	'''
	请求装备洗练保存
	@param role:
	@param param:
	'''
	eId = param
	
	globaldict = role.GetTempObj(EnumTempObj.enGlobalItemMgr)
	equipment = globaldict.get(eId)
	if not equipment:
		return
	#获取该装备未保存的属性
	refineProp = equipment.GetWashRefineProp()
	if not refineProp:
		return
	equipment.SetWashProp(refineProp)
	if equipment.owner:
		#重算
		equipment.owner.GetPropertyGather().ReSetRecountEquipmentWashFlag()
	
	role.SendObj(Equipment_WashData, [2, eId, equipment.GetWashProp(), {}, equipment.GetWashExtendHole()])
	
def RequestEquipmentWash(role, param):
	'''
	客户端请求洗练
	@param role:
	@param param:
	'''
	eId, lockList, isRMB = param
	if role.GetLevel() < EnumGameConfig.EQUIPMENT_MIN_ROLE_LEVEL:
		return
	
	globaldict = role.GetTempObj(EnumTempObj.enGlobalItemMgr)
	equipment = globaldict.get(eId)
	if not equipment:
		return
	#装备的强化等级是有要求的
	if equipment.GetStrengthenLevel() < EnumGameConfig.EQUIPMENT_MIN_STRENG_LEVEL:
		return
	#获取该装备额外解锁的洗练条数
	extendHole = equipment.GetWashExtendHole()
	#总的洗练条数为免费的+解锁的
	totalHole = extendHole + equipment.cfg.FreeWash
	#当总的洗练条数小于或等于锁住的属性时，直接返回
	lockCnt = len(lockList)
	if totalHole <= lockCnt:
		return
	#判断是否有装备洗练石或临时装备洗练石
	if not role.ItemCnt(EnumGameConfig.EQUIPMENT_WASH_CODING) and not role.ItemCnt_NotTimeOut(EnumGameConfig.EQUIPMENT_WASH_CODING_TMP):
		return
	
	needCodingCnt = 0
	lockCodingRMB = 0
	if lockList:#有锁定的属性需检测是否有锁定需要的道具
		lockCodingCnt = role.ItemCnt(EnumGameConfig.EQUIOMENT_WASH_LOCK_CODING)
		if lockCodingCnt < lockCnt:#锁不够用神石替代
			needCodingCnt = lockCodingCnt
			
			if Environment.EnvIsNA():
				lockCodingRMB = EnumGameConfig.EQUIPMENT_LOCK_COST_NA * (lockCnt - needCodingCnt)
			else:
				lockCodingRMB = EnumGameConfig.EQUIPMENT_LOCK_COST * (lockCnt - needCodingCnt)
				
			if isRMB:
				if role.GetUnbindRMB() < lockCodingRMB + EnumGameConfig.EQUIPMENT_WASH_UNBINDRMB:
					return
			else:
				if role.GetUnbindRMB() < lockCodingRMB:
					return
		else:
			needCodingCnt = lockCnt
	
	if isRMB:
		if role.GetUnbindRMB() < EnumGameConfig.EQUIPMENT_WASH_UNBINDRMB:
			return
	
	#根据该装备的洗练度获取该装备可以洗练出的星级
	global Equipment_WashStar_Dict
	starcfg = None
	washNum = role.GetI32(EnumInt32.EquipmentWashNum)
	for washList, cfg in Equipment_WashStar_Dict.iteritems():
		if washList[0] <= washNum <= washList[1]:
			starcfg = cfg
			break
	if not starcfg:
		print "GE_EXC, can not find washNum(%s) in RequestEquipmentWash" % washNum
		return
	
	#需要重新刷新的属性条数
	FreshNum = totalHole - lockCnt
	#获取随机生成的新属性
	ptDict = RandomNewProp(FreshNum, lockList, starcfg)

	#新的属性为锁定的属性+随机生成的新属性
	oldWashProp = equipment.GetWashProp()
	newWashPro = {}
	if lockList:
		for pt in lockList:
			newWashPro[pt] = oldWashProp.get(pt, 0)
	for pt, pv in ptDict.iteritems():
		newWashPro[pt] = pv
	with EquipmentWashCost:
		if role.ItemCnt_NotTimeOut(EnumGameConfig.EQUIPMENT_WASH_CODING_TMP) > 0:
			role.DelItem(EnumGameConfig.EQUIPMENT_WASH_CODING_TMP, 1)
		else:
			role.DelItem(EnumGameConfig.EQUIPMENT_WASH_CODING, 1)
		if lockList:#有锁定的属性需检测是否有锁定需要的道具
			if lockCodingRMB:
				role.DecUnbindRMB(lockCodingRMB)
			if needCodingCnt:
				role.DelItem(EnumGameConfig.EQUIOMENT_WASH_LOCK_CODING, needCodingCnt)
		if isRMB:
			if Environment.EnvIsNA():
				role.DecUnbindRMB(EnumGameConfig.EQUIPMENT_WASH_UNBINDRMB_NA)
			else:
				role.DecUnbindRMB(EnumGameConfig.EQUIPMENT_WASH_UNBINDRMB)
			role.IncI32(EnumInt32.EquipmentWashNum, EnumGameConfig.EQUIPMENT_INC_WASHNUM_RMB)
		else:
			role.IncI32(EnumInt32.EquipmentWashNum, EnumGameConfig.EQUIPMENT_INC_WASHNUM)
		#先将新生成的洗练属性存到未保存属性中
		equipment.SetWashRefineProp(newWashPro)
	
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveEquipmentWash, (eId, newWashPro))
		###################################################################
		#精彩活动装备洗练日活动
		from Game.Activity.LatestActivity import LatestActivityMgr, EnumLatestType
		LatestActivityMgr.GetFunByType(EnumLatestType.EquipmentWash_Latest, (role, 1))
		###################################################################
	role.SendObj(Equipment_WashData, [1, eId, oldWashProp, newWashPro, extendHole])


def RequestOneKeyEquipmentWash(role, param):
	'''
	客户端请求自动洗练
	@param role:
	@param param:
	'''
	eId, lockList, isRMB, useLockRMB, targetStar, isSkip = param
	
	if role.GetLevel() < EnumGameConfig.EQUIPMENT_MIN_ROLE_LEVEL:
		role.SendObj(Equipment_OnekeyWashStop, None)
		return
	
	globaldict = role.GetTempObj(EnumTempObj.enGlobalItemMgr)
	equipment = globaldict.get(eId)
	if not equipment:
		role.SendObj(Equipment_OnekeyWashStop, None)
		return
	
	theWashRefineProp = equipment.GetWashRefineProp()
	
	if not isSkip and theWashRefineProp:
		for k, v in theWashRefineProp.iteritems():
			if k in lockList:
				continue
			for cfg in Equipment_WashBase_Dict.itervalues():
				if v < cfg.proportion[0] or v > cfg.proportion[1]:
					continue
				if cfg.starlevel >= targetStar:
					role.SendObj(Equipment_OnekeyWashStop, None)
					return
	
	#装备的强化等级是有要求的
	if equipment.GetStrengthenLevel() < EnumGameConfig.EQUIPMENT_MIN_STRENG_LEVEL:
		role.SendObj(Equipment_OnekeyWashStop, None)
		return
	
	#根据该装备的洗练度获取该装备可以洗练出的星级
	global Equipment_WashStar_Dict
	starcfg = None
	washNum = role.GetI32(EnumInt32.EquipmentWashNum)
	for washList, cfg in Equipment_WashStar_Dict.iteritems():
		if washList[0] <= washNum <= washList[1]:
			starcfg = cfg
			break
	if not starcfg:
		print "GE_EXC, can not find washNum(%s) in RequestEquipmentWash" % washNum
		role.SendObj(Equipment_OnekeyWashStop, None)
		return
	
	if starcfg.listStar < OneKeyWashNeedStar:
		role.SendObj(Equipment_OnekeyWashStop, None)
		return
	
	if targetStar > starcfg.listStar:
		role.SendObj(Equipment_OnekeyWashStop, None)
		return
	
	#获取该装备额外解锁的洗练条数
	extendHole = equipment.GetWashExtendHole()
	#总的洗练条数为免费的+解锁的
	totalHole = extendHole + equipment.cfg.FreeWash
	#当总的洗练条数小于或等于锁住的属性时，直接返回
	lockCnt = len(lockList)
	if totalHole <= lockCnt:
		role.SendObj(Equipment_OnekeyWashStop, None)
		return
	
	#判断是否有装备洗练石或临时装备洗练石
	if not role.ItemCnt(EnumGameConfig.EQUIPMENT_WASH_CODING) and not role.ItemCnt_NotTimeOut(EnumGameConfig.EQUIPMENT_WASH_CODING_TMP):
		role.SendObj(Equipment_OnekeyWashStop, None)
		return
	
	needCodingCnt = 0
	lockCodingRMB = 0
	if lockList:#有锁定的属性需检测是否有锁定需要的道具
		lockCodingCnt = role.ItemCnt(EnumGameConfig.EQUIOMENT_WASH_LOCK_CODING)
		#如果洗练锁不足，并且也不能用神石代替的话就直接返回。否则判断神石数量
		if lockCodingCnt < lockCnt:
			needCodingCnt = lockCodingCnt
			lockCodingRMB = EnumGameConfig.EQUIPMENT_LOCK_COST * (lockCnt - needCodingCnt)
		else:
			needCodingCnt = lockCnt

	if useLockRMB and isRMB:
		if role.GetUnbindRMB() < EnumGameConfig.EQUIPMENT_WASH_UNBINDRMB + lockCodingRMB:
			role.SendObj(Equipment_OnekeyWashStop, None)
			return
	elif useLockRMB:
		if role.GetUnbindRMB() < lockCodingRMB:
			role.SendObj(Equipment_OnekeyWashStop, None)
			return
	elif isRMB:
		if role.GetUnbindRMB() < EnumGameConfig.EQUIPMENT_WASH_UNBINDRMB:
			role.SendObj(Equipment_OnekeyWashStop, None)
			return
		
	#需要重新刷新的属性条数
	FreshNum = totalHole - lockCnt
	#获取随机生成的新属性
	ptDict = RandomNewProp(FreshNum, lockList, starcfg)

	#新的属性为锁定的属性+随机生成的新属性
	oldWashProp = equipment.GetWashProp()
	newWashPro = {}
	if lockList:
		for pt in lockList:
			newWashPro[pt] = oldWashProp.get(pt, 0)
	for pt, pv in ptDict.iteritems():
		newWashPro[pt] = pv
		
	with EquipmentOneKeyWashCost:
		if role.ItemCnt_NotTimeOut(EnumGameConfig.EQUIPMENT_WASH_CODING_TMP) > 0:
			role.DelItem(EnumGameConfig.EQUIPMENT_WASH_CODING_TMP, 1)
		else:
			role.DelItem(EnumGameConfig.EQUIPMENT_WASH_CODING, 1)
		if lockList:#有锁定的属性需检测是否有锁定需要的道具
			if lockCodingRMB:
				role.DecUnbindRMB(lockCodingRMB)
			if needCodingCnt:
				role.DelItem(EnumGameConfig.EQUIOMENT_WASH_LOCK_CODING, needCodingCnt)
		if isRMB:
			role.DecUnbindRMB(EnumGameConfig.EQUIPMENT_WASH_UNBINDRMB)
			role.IncI32(EnumInt32.EquipmentWashNum, EnumGameConfig.EQUIPMENT_INC_WASHNUM_RMB)
		else:
			role.IncI32(EnumInt32.EquipmentWashNum, EnumGameConfig.EQUIPMENT_INC_WASHNUM)
		#先将新生成的洗练属性存到未保存属性中
		equipment.SetWashRefineProp(newWashPro)
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveEquipmentWash, (eId, newWashPro))
		###################################################################
		#精彩活动装备洗练日活动
		from Game.Activity.LatestActivity import LatestActivityMgr, EnumLatestType
		LatestActivityMgr.GetFunByType(EnumLatestType.EquipmentWash_Latest, (role, 1))
		###################################################################
		
	role.SendObj(Equipment_WashData, [1, eId, oldWashProp, newWashPro, extendHole])


def RandomNewProp(washNum, lockList, starcfg):
	#随机出新的洗练属性
	global Equipment_WashBase_Dict

	ptDict = {}
	EWD = Equipment_WashBase_Dict.get
	SRANDOM = starcfg.starRandom
	for _ in xrange(washNum):
		#先随机个星级
		star = SRANDOM.RandomOne()
		#然后根据星级去取对应的配置，随机出比例和随机出除锁定几条属性以为的其他属性中的一条
		baseCfg = EWD(star)
		if not baseCfg:
			print "GE_EXC, can not find star(%s) in RequestEquipmentWash" % star
			return ptDict
		#随机出比例
		proportion = random.randint(baseCfg.proportion[0], baseCfg.proportion[1])
		#取出除锁定以外和新生成的其他属性，从中随机出一个
		newSet = set()
		for pt in baseCfg.ptlist:
			if pt not in lockList and pt not in ptDict:
				newSet.add(pt)
		if not newSet:
			return ptDict
		selectPt = random.sample(newSet, 1)[0]
		ptDict[selectPt] = proportion
	return ptDict
	
#####################################################################
#精彩活动装备洗练增加函数，使用洗练升星石洗练
#####################################################################
def EquipmentForing_WashStone(role, param):
	'''
	客户端请求使用洗练升星石洗练
	@param role:
	@param param: equipment id
	@author: GaoShuai
	'''
	if role.GetLevel() < EnumGameConfig.EQUIPMENT_MIN_ROLE_LEVEL:
		return
	eId = param
	globaldict = role.GetTempObj(EnumTempObj.enGlobalItemMgr)
	equipment = globaldict.get(eId)
	if not equipment:
		return
	#装备的强化等级是有要求的
	if equipment.GetStrengthenLevel() < EnumGameConfig.EQUIPMENT_MIN_STRENG_LEVEL:
		return
	#判断是否有洗练升星石
	if role.ItemCnt_NotTimeOut(EnumGameConfig.EQUIPMENT_WASH_STONE) <= 0:
		return
	
	#根据该装备的洗练度获取该装备可以洗练出的星级，这里取最大星级
	global Equipment_WashStar_Dict
	starLevel = 0
	washNum = role.GetI32(EnumInt32.EquipmentWashNum)
	for washList, cfg in Equipment_WashStar_Dict.iteritems():
		if washList[0] <= washNum <= washList[1]:
			starLevel = cfg.washStar[-1]
			break
	if not starLevel:
		print "GE_EXC, can not find washNum(%s) in EquipmentForing_WashStone，role id is (%s)" % (washNum, role.GetRoleID())
		return
	
	baseCfg = Equipment_WashBase_Dict.get(starLevel)
	washList_tmp = []
	oldWashProp = equipment.GetWashProp()
	for key in oldWashProp:
		if oldWashProp[key] < baseCfg.proportion[0]:
			washList_tmp.append(key)
	#如果所有洗练属性满星，返回
	if len(washList_tmp) == 0:
		return
	
	from copy import copy
	newWashPro = copy(oldWashProp)
	#随机出新的洗练属性
	newProportion = random.randint(baseCfg.proportion[0], baseCfg.proportion[1])
	newWashPro[random.choice(washList_tmp)] = newProportion
	#获取随机生成的新属性
	
	#新的属性为锁定的属性+随机生成的新属性
	with EquipmentWashStone:
		role.DelItem(EnumGameConfig.EQUIPMENT_WASH_STONE, 1)
		
		#先将新生成的洗练属性存到未保存属性中
		equipment.SetWashRefineProp(newWashPro)
		
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveEquipmentWashUpStar, (eId, oldWashProp, newWashPro))
	role.SendObj(Equipment_WashData, [1, eId, oldWashProp, newWashPro, 0])
	
def RequestEquipZhuanSheng(role, param):
	'''
	客户端请求装备转生
	@param role:
	@param param:装备ID
	'''
	ExchangeEquipment(role, param, 1, Equipment_ZhuanSheng_log)
def RequestEquipEvolve(role, param):
	'''
	客户端请求装备进化
	@param role:
	@param param:装备ID
	'''
	ExchangeEquipment(role, param, 2, Equipment_Evolve_log)
def ExchangeEquipment(role, param, Etype, Equipment_log):
	'''
	@author: GaoShuai
	@param role:
	@param param:装备ID
	@Etype 1:转生，2:进化
	'''
	eId = param
	globaldict = role.GetTempObj(EnumTempObj.enGlobalItemMgr)
	equipment = globaldict.get(eId)
	if not equipment:
		return
	#该装备是否可转生或进化
	if Etype == 1:
		Flag = equipment.cfg.zhuanSheng
		Equipment_Dict = Equipment_ZhuanSheng_Dict
	elif Etype == 2:
		Flag = equipment.cfg.evolve
		Equipment_Dict = Equipment_Evolve_Dict
	else:
		return
	if not Flag:
		return
	srcType = equipment.otype
	cfg = Equipment_Dict.get(srcType)
	if not cfg:
		return
	if role.GetLevel() < cfg.needLevel:
		return
	mgr = equipment.package
	#判断装备是否可以转生
	if Etype == 1:
		if equipment.owner and equipment.cfg.ZhuanShengLevel >= equipment.owner.GetZhuanShengLevel():
			return
	#判断装备是否可以进化
	elif Etype == 2:
		if equipment.cfg.evolve == 0:
			return
		
	if cfg.cnt1 < 0 or cfg.cnt2 < 0 or cfg.cnt3 < 0 or cfg.cnt4 < 0:
		print "GE_EXC, EquipmentZhuanShengConfig error, one or more numbers < 0 in EquipmentZhuanSheng.txt or EquipmentEvolve.txt"
		return
	if role.ItemCnt(cfg.itemType1) < cfg.cnt1:
		return
	if role.ItemCnt(cfg.itemType2) < cfg.cnt2:
		return
	if role.ItemCnt(cfg.itemType3) < cfg.cnt3:
		return
	if role.ItemCnt(cfg.itemType4) < cfg.cnt4:
		return
	
	desType = cfg.desType #新装备类型
	fun = Base.Obj_Type_Fun.get(desType)
	if not fun:
		print "GE_EXC, Equipment ZhuanSheng or Evolve can not find fun, fun param = (%s)" % param
		return
	
	with Equipment_log:
		#扣物品
		if cfg.cnt1 > 0:
			if role.DelItem(cfg.itemType1, cfg.cnt1) < cfg.cnt1:
				return
		if cfg.cnt2 > 0:
			if role.DelItem(cfg.itemType2, cfg.cnt2) < cfg.cnt2:
				return
		if cfg.cnt3 > 0:
			if role.DelItem(cfg.itemType3, cfg.cnt3) < cfg.cnt3:
				return
		if cfg.cnt4 > 0:
			if role.DelItem(cfg.itemType4, cfg.cnt4) < cfg.cnt4:
				return
		#-----------------------------------------------------------
		owner = equipment.owner
		
		owerId = 0
		
		equipmentIdSet = None
		if mgr.heroId:
			owerId = mgr.heroId
			equipmentIdSet = role.GetObj(mgr.ObjEnumIndex).get(owerId)
		else:
			owerId = role.GetRoleID()
			equipmentIdSet = role.GetObj(mgr.ObjEnumIndex)
		#删除数据
		equipmentIdSet.discard(eId)
		del mgr.objIdDict[eId]
		
		
		equipment.package = None
		equipment.owner = None
		cd_dict = mgr.codingGather.get(srcType)
		del cd_dict[eId]
		if not cd_dict:
			del mgr.codingGather[srcType]
		#全局管理器删除记录
		del globaldict[eId]
		
		#构建数据对象
		newId = cProcess.AllotGUID64()
		obj = newId, desType, 1, {}
		#根据注册函数，数据对象，生成物品对象
		newItem = fun(role, obj)
		
		newItem.package = mgr
		newItem.AfterCreate()
		if owner:
			newItem.owner = owner
		else:
			newItem.owner = None	
		#角色数组直接更新
		equipmentIdSet.add(newId)
		#加入内部管理器
		mgr.objIdDict[newId] = newItem
		itemDict = mgr.codingGather.get(desType)
		if not itemDict:
			mgr.codingGather[desType] = itemDict = {}
		itemDict[newId] = newItem	
		#加入全局管理器
		globaldict[newId] = newItem		
		if newItem.cfg.posType <= 6:
			#强化等级保留
			newItem.SetStrengthenLevel(equipment.GetStrengthenLevel())
			#保留宝石
			newItem.SetEquipmentGemlist(equipment.GetEquipmentGem())
			#保留附魔等级
			newItem.SetEnchantLevel(equipment.GetEnchantLevel())
			#保留洗练属性
			newItem.SetWashExtendHole(equipment.GetWashExtendHole())
			newItem.SetWashProp(equipment.GetWashProp())
			#保留进化等级，如果是转生，转生等级+1，如果是进化转生等级不变
			if owner:
				#重算属性
				owner.GetPropertyGather().ReSetRecountEquipmentFlag()
				#触发套装属性
				if equipment.cfg.suitId or newItem.cfg.suitId:
					newItem.package.ResetStrengthenSuit()
		if Etype == 1:
			#记录日志,同步客户端
			AutoLog.LogObj(role.GetRoleID(), AutoLog.eveUpGradeEquipment, newId, newItem.otype, newItem.oint, newItem.odata, (eId, srcType))
			role.SendObj(Equipment_ZhuanShengOK, (newId, eId, owerId, newItem.GetSyncData(),))
		elif Etype == 2:
			#记录日志,同步客户端
			AutoLog.LogObj(role.GetRoleID(), AutoLog.eveGodcastEquipment, newId, newItem.otype, newItem.oint, newItem.odata, (eId, srcType))
			role.SendObj(Equipment_EvolveOK, (newId, eId, owerId, newItem.GetSyncData(),))

if "_HasLoad" not in dir():
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("EquipmentForing_OnStrengthen1", "强化装备"), OnStrengthenEquipment)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("EquipmentForing_QuickCD", "请求加速冷却"), EquipmentForing_QuickCD)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("EquipmentForing_UpGradeEquipment", "请求进阶装备"), UpGradeEquipment)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("EquipmentForing_GodcastEquipment", "请求神铸装备"), GodcastEquipment)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("EquipmentForing_EnchantEquipment", "请求附魔装备"), EnchantEquipment)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("EquipmentForing_Wash", "请求装备洗练"), RequestEquipmentWash)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("EquipmentForing_OneKeyWash", "请求装备自动洗练"), RequestOneKeyEquipmentWash)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("EquipmentForing_WashSave", "请求装备洗练保存"), RequestEquipmentWashSave)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("EquipmentForing_WashInheritance", "请求继承装备洗练属性"), RequestEquipmentWashInheritance)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("EquipmentForing_WashUnlock", "请求解锁装备的洗练锁"), RequestEquipmentWashUnlock)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("EquipmentForing_WashStone", "请求使用升星石的装备洗练"), EquipmentForing_WashStone)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("EquipmentForing_Evolve", "请求装备进化"), RequestEquipEvolve)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("EquipmentForing_ZhuanSheng", "请求装备转生"), RequestEquipZhuanSheng)
	if Environment.EnvIsFT() or Environment.IsDevelop:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("EquipmentForing_OnekeyOnStrengthen", "请求一键强化装备"), OnekeyStrengthenEquipment)
	
