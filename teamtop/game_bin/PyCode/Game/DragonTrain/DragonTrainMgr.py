#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.DragonTrain.DragonTrainMgr")
#===============================================================================
# 驯龙系统管理
#===============================================================================
import random
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.DragonTrain import DragonTrainDefine, DragonTrainConfig,\
	DragonTrainBase
from Game.Role import Event
from Game.Role.Data import EnumTempObj, EnumDayInt8, EnumInt32, EnumObj
from Game.VIP import VIPConfig
from Game.DailyDo import DailyDo

if "_HasLoad" not in dir():
	#消息
	Dragon_Train_Sync_Main_Panel_Data = AutoMessage.AllotMessage("Dragon_Train_Sync_Main_Panel_Data", "通知客户端同步驯龙主面板数据")
	Dragon_Train_Show_Evolve_Panel = AutoMessage.AllotMessage("Dragon_Train_Show_Evolve_Panel", "通知客户端显示驯龙进化面板")
	Dragon_Equipment_Sync_All = AutoMessage.AllotMessage("Dragon_Equipment_Sync_All", "通知客户端所有驯龙装备信息")
	Dragon_Sync_TempValue_Data = AutoMessage.AllotMessage("Dragon_Sync_TempValue_Data", "同步客户端临时进化进度")
	
#=============道具增加临时神龙进化进度触发================
def ItemAddTempValue(role, grade):
	dragonTrainMgr = role.GetTempObj(EnumTempObj.DragonTrainMgr)
	if not dragonTrainMgr:
		return
	
	tempData = role.GetObj(EnumObj.LatestActData).get(9, {})
	tempValue = tempData.get(grade, 0)
	if not tempValue:
		return
	
	for dragonId, dragonObj in dragonTrainMgr.dragon_dict.iteritems():
		if dragonObj.grade != grade:
			continue
		config = DragonTrainConfig.DRAGON_TRAIN_BASE.get((dragonId, dragonObj.grade))
		if not config:
			return
		nextGrade = dragonObj.grade + 1
		#是否已经是最高阶
		nextGradeConfig = DragonTrainConfig.DRAGON_TRAIN_BASE.get((dragonId, nextGrade))
		if not nextGradeConfig:
			return
		if dragonObj.evolve_lucky + tempValue >= config.maxEvolveLucky:
			dragonObj.grade = nextGrade
			dragonObj.evolve_lucky = 0
			tempData[grade] = 0
			#重算属性
			dragonTrainMgr.recount_dragon_property(dragonId)
			role.GetPropertyGather().ReSetRecountDragonTrainFlag()
			#最新活动
			from Game.Activity.LatestActivity import LatestActivityMgr, EnumLatestType
			LatestActivityMgr.GetFunByType(EnumLatestType.DragonTrain_Latest, role)
			#提示
			role.Msg(2, 0, GlobalPrompt.DT_EVOLVE_SUCCESS_PROMPT % (config.dragonName, nextGradeConfig.gradeName))
			#传闻
			cRoleMgr.Msg(1, 0, GlobalPrompt.DT_EVOLVE_SUCCESS_HEARSAY % (role.GetRoleName(), config.dragonName, nextGradeConfig.gradeName))
			#显示面板
			ShowEvolvePanel(role, dragonId)
			#更新主面板数据
			SyncDragonTrainMainPanelData(role)
			break
	#同步客户端临时修行进度
	role.SendObj(Dragon_Sync_TempValue_Data, tempData)
	
def SyncDragonTrainMainPanelData(role):
	dragonTrainMgr = role.GetTempObj(EnumTempObj.DragonTrainMgr)
	dragonVeinManager = role.GetTempObj(EnumTempObj.DragonVein)
	
	dragonBallDict = {}
	dragonGradeDict = {}
	for dragonId, dragonObj in dragonTrainMgr.dragon_dict.iteritems():
		dragonBallDict[dragonId] = dragonObj.ball_dict
		dragonGradeDict[dragonId] = dragonObj.grade
	
	dragonTrainMgr_property_dict = dragonTrainMgr.get_total_property_dict()
	dragonVein_property_dict = dragonVeinManager.GetTotalProperty()
	
	#这里用dict实现浅拷贝，因为字典不需要深拷贝
	total_property_dict = dict(dragonTrainMgr_property_dict)

	for pt, pv in dragonVein_property_dict.iteritems():
		total_property_dict[pt] = total_property_dict.get(pt, 0) + pv

	role.SendObj(Dragon_Train_Sync_Main_Panel_Data, [dragonBallDict, total_property_dict, dragonGradeDict])
	
	
def SyncAllDragonEquipmentData(role):
	dragonTrainMgr = role.GetTempObj(EnumTempObj.DragonTrainMgr)
	
	role.SendObj(Dragon_Equipment_Sync_All, [dragonTrainMgr.equipment_dict, dragonTrainMgr.dragon_property_dict])
	
def ShowEvolvePanel(role, dragonId):
	dragonTrainMgr = role.GetTempObj(EnumTempObj.DragonTrainMgr)
	
	if dragonId not in dragonTrainMgr.dragon_dict:
		#未激活祝福值为0
		role.SendObj(Dragon_Train_Show_Evolve_Panel, 0)
		return
	
	dragonObj = dragonTrainMgr.dragon_dict[dragonId]
	
	role.SendObj(Dragon_Train_Show_Evolve_Panel, dragonObj.evolve_lucky)
	
def DragonTrainAwaken(role, dragonId):
	'''
	驯龙唤醒
	@param role:
	@param dragonId:
	'''
	dragonTrainMgr = role.GetTempObj(EnumTempObj.DragonTrainMgr)
	
	#已激活
	if dragonId in dragonTrainMgr.dragon_dict:
		return
	
	#是否存在对应的神龙
	dragonConfig = DragonTrainConfig.DRAGON_TRAIN_BASE.get((dragonId, 1))
	if not dragonConfig:
		return
	
	#装备没有齐全无法激活
	if dragonId not in dragonTrainMgr.equipment_dict:
		return
	
	equipmentDict = dragonTrainMgr.equipment_dict[dragonId]
	
	for posType in xrange(1, DragonTrainDefine.DRAGON_EQUIPMENT_CNT_MAX + 1):
		if posType not in equipmentDict:
			return
		
	dragonTrainMgr.create_dragon(dragonId)
	
	#重算主角驯龙属性
	dragonTrainMgr.recount_dragon_property(dragonId)
	role.GetPropertyGather().ReSetRecountDragonTrainFlag()
	
	SyncAllDragonEquipmentData(role)
	SyncDragonTrainMainPanelData(role)
	#最新活动
	from Game.Activity.LatestActivity import LatestActivityMgr, EnumLatestType
	LatestActivityMgr.GetFunByType(EnumLatestType.DragonTrain_Latest, role)
	#传闻
	cRoleMgr.Msg(1, 0, GlobalPrompt.DT_AWAKEN_SUCCESS_HEARSAY % (role.GetRoleName(), dragonConfig.dragonName))
	
def DragonTrainEvolve(role, dragonId):
	dragonTrainMgr = role.GetTempObj(EnumTempObj.DragonTrainMgr)
	
	if dragonId not in dragonTrainMgr.dragon_dict:
		return
	dragonObj = dragonTrainMgr.dragon_dict[dragonId]
	
	nextGrade = dragonObj.grade + 1
	#是否已经是最高阶
	nextGradeConfig = DragonTrainConfig.DRAGON_TRAIN_BASE.get((dragonId, nextGrade))
	if not nextGradeConfig:
		return
	
	config = DragonTrainConfig.DRAGON_TRAIN_BASE.get((dragonId, dragonObj.grade))
	if not config:
		return
	
	#判断进化条件
	#材料
	for coding, cnt in config.evolveNeedItem:
		itemCnt = role.ItemCnt(coding)
		if itemCnt < cnt:
			return
	for item in config.evolveNeedItem:
		role.DelItem(*item)
	
	#临时祝福值
	LatestActData = role.GetObj(EnumObj.LatestActData).get(9, {})
	tempValue = LatestActData.get(dragonObj.grade, 0)
	#祝福值
	if dragonObj.evolve_lucky + tempValue < config.successNeedMinLucky:
		#必定失败
		addLucky = random.randint(*config.failAddLuckyRange)
		dragonObj.evolve_lucky += addLucky
		#提示
		role.Msg(2, 0, GlobalPrompt.DT_EVOLVE_FAIL_PROMPT % addLucky)
		#显示面板
		ShowEvolvePanel(role, dragonId)
		return
	
	odds = config.oddsBase + (dragonObj.evolve_lucky * config.perLuckyAddOdds)
	successRi = random.randint(1, 100000)
	if (dragonObj.evolve_lucky + tempValue >= config.maxEvolveLucky) or (successRi < odds):
		#幸运值满必定成功
		#成功
		dragonObj.grade = nextGrade
		dragonObj.evolve_lucky = 0
		#重算属性
		dragonTrainMgr.recount_dragon_property(dragonId)
		role.GetPropertyGather().ReSetRecountDragonTrainFlag()
		#假如有临时祝福值
		if tempValue:
			LatestActData[dragonObj.grade - 1] = 0
			role.SendObj(Dragon_Sync_TempValue_Data, LatestActData)
		#提示
		role.Msg(2, 0, GlobalPrompt.DT_EVOLVE_SUCCESS_PROMPT % (config.dragonName, nextGradeConfig.gradeName))
		#传闻
		cRoleMgr.Msg(1, 0, GlobalPrompt.DT_EVOLVE_SUCCESS_HEARSAY % (role.GetRoleName(), config.dragonName, nextGradeConfig.gradeName))
		#最新活动
		from Game.Activity.LatestActivity import LatestActivityMgr, EnumLatestType
		LatestActivityMgr.GetFunByType(EnumLatestType.DragonTrain_Latest, role)
	else:
		#失败
		addLucky = random.randint(*config.failAddLuckyRange)
		dragonObj.evolve_lucky = min((dragonObj.evolve_lucky + addLucky), config.maxEvolveLucky)
		#提示
		role.Msg(2, 0, GlobalPrompt.DT_EVOLVE_FAIL_PROMPT % addLucky)
	
	#显示面板
	ShowEvolvePanel(role, dragonId)
	#更新主面板数据
	SyncDragonTrainMainPanelData(role)
	
def DragonTrainCollectSoul(role):
	cnt = role.GetDI8(EnumDayInt8.DragonTrainCollectSoulCnt)
	
	#VIP次数限制
	vip = role.GetVIP()
	
	if vip:
		vipConfig = VIPConfig._VIP_BASE.get(vip)
		if not vipConfig:
			return
		if cnt >= vipConfig.dragonSoulCnt:
			return
	else:
		if cnt >= EnumGameConfig.DT_NOT_VIP_DRAGON_SOUL_CNT:
			return
	
	config = DragonTrainConfig.DRAGON_COLLECT_SOUL.get(cnt + 1)
	if not config:
		return
	
	if role.GetUnbindRMB() < config.needRMB:
		return
	role.DecUnbindRMB(config.needRMB)
	
	#消耗次数
	role.IncDI8(EnumDayInt8.DragonTrainCollectSoulCnt, 1)
	
	addSoul = config.rewardSoul
	#是否有暴击
	isCrit = False
	r = random.randint(1, 10000)
	if r < config.critOdds:
		isCrit = True
		addSoul *= config.critTimes
		
	role.IncI32(EnumInt32.DragonTrainSoul, addSoul)
	
	#每日必做 -- 神龙聚灵
	Event.TriggerEvent(Event.Eve_DoDailyDo, role, (DailyDo.Daily_DragonTrain, 1))
	
	if isCrit is True:
		#提示
		role.Msg(2, 0, GlobalPrompt.DT_COLLECT_SOUL_CRIT_SUCCESS_PROMPT % (config.critTimes, addSoul))
	else:
		#提示
		role.Msg(2, 0, GlobalPrompt.DT_COLLECT_SOUL_SUCCESS_PROMPT % addSoul)
	
def DragonEquipmentActivate(role, dragonId, equipmentCoding):
	'''
	激活龙潭装备
	@param role:
	@param dragonId:
	@param equipmentCoding:
	'''
	dragonTrainMgr = role.GetTempObj(EnumTempObj.DragonTrainMgr)
	
	#是否拥有装备
	itemCnt = role.ItemCnt(equipmentCoding)
	if itemCnt == 0:
		return
	
	equipmentConfig = DragonTrainConfig.DRAGON_EQUIPMENT.get(equipmentCoding)
	if not equipmentConfig:
		return
	
	#不能用于激活
	if not equipmentConfig.canActivate:
		return
	
	#等级限制
	if role.GetLevel() < equipmentConfig.needLevel:
		return
	
	#装备与神龙不匹配
	if dragonId != equipmentConfig.dragonId:
		return
	
	if dragonId not in dragonTrainMgr.equipment_dict:
		dragonTrainMgr.equipment_dict[dragonId] = {}
		
	equipmentDict = dragonTrainMgr.equipment_dict[dragonId]
	#已激活
	if equipmentConfig.posType in equipmentDict:
		return
		
	role.DelItem(equipmentCoding, 1)
	equipmentDict[equipmentConfig.posType] = equipmentCoding
	
	#重算主角驯龙属性
	dragonTrainMgr.recount_dragon_property(dragonId)
	role.GetPropertyGather().ReSetRecountDragonTrainFlag()
	
	#同步驯龙面板的数据
	SyncAllDragonEquipmentData(role)
	SyncDragonTrainMainPanelData(role)
	
def DragonBallUpgrade(role, dragonId, position):
	dragonTrainMgr = role.GetTempObj(EnumTempObj.DragonTrainMgr)
	
	#未激活神龙
	if dragonId not in dragonTrainMgr.dragon_dict:
		return
	
	dragonObj = dragonTrainMgr.dragon_dict[dragonId]
	
	nextGrade = 0
	#是否已经提升过对应龙珠
	if position not in dragonObj.ball_dict:
		nextGrade = 1
	else:
		nextGrade = dragonObj.ball_dict[position] + 1
		
	ballConfig = DragonTrainConfig.DRAGON_BALL_BASE.get((dragonId, position, nextGrade))
	if not ballConfig:
		return
		
	#前置条件是否满足
	if ballConfig.needPreBallData:
		needPosition, needGrade = ballConfig.needPreBallData
		
		if needPosition not in dragonObj.ball_dict:
			return
		
		if dragonObj.ball_dict[needPosition] < needGrade:
			return
		
	if role.GetDragonSoul() < ballConfig.needDragonSoul:
		return
	role.DecDragonSoul(ballConfig.needDragonSoul)
		
	#提升
	dragonObj.ball_dict[position] = nextGrade
	
	#重算主角驯龙属性
	dragonTrainMgr.recount_dragon_property(dragonId)
	role.GetPropertyGather().ReSetRecountDragonTrainFlag()
	
	SyncDragonTrainMainPanelData(role)
	#提示
	role.Msg(2, 0, GlobalPrompt.DT_UPGRADE_BALL_SUCCESS_PROMPT)
	
	
def UpGradeDragonEquipment(role, dragonId, equipmentCoding):
	'''
	装备升阶
	@param role:
	@param msg:装备ID
	'''
	dragonTrainMgr = role.GetTempObj(EnumTempObj.DragonTrainMgr)
	#未激活神龙
	if dragonId not in dragonTrainMgr.dragon_dict:
		return
	updateconfig = DragonTrainConfig.DragonEquipUpgradeDict.get(equipmentCoding, None)
	if updateconfig == None:
		print "GE_EXC, error while updateconfig = DragonTrainConfig.DragonEquipUpgradeDict.get(equipmentCoding, None), no such equipmentCoding(%s)" % equipmentCoding
		return
	#等级不符合要求
	if role.GetLevel() < updateconfig.needLevel:
		return

	equipmentConfig = DragonTrainConfig.DRAGON_EQUIPMENT.get(equipmentCoding)
	if not equipmentConfig:
		print "GE_EXC, error while equipmentConfig = DragonTrainConfig.DRAGON_EQUIPMENT.get(equipmentCoding), no such equipmentCoding(%s)" % equipmentCoding
		return
	#装备没有激活
	if dragonId not in dragonTrainMgr.equipment_dict:
		return
	equipmentDict = dragonTrainMgr.equipment_dict[dragonId]
	#龙骸部位未激活
	if not equipmentConfig.posType in equipmentDict:
		return
	#发过来的原龙骸跟实际的不同
	if equipmentDict[equipmentConfig.posType] != equipmentCoding:
		return
	if role.ItemCnt(updateconfig.itemType1) < updateconfig.cnt1:
		return
	if role.ItemCnt(updateconfig.itemType2) < updateconfig.cnt2:
		return
	if role.ItemCnt(updateconfig.itemType3) < updateconfig.cnt3:
		return
	
	with TraDragonEquipUpgrade:
		if updateconfig.cnt1 > 0:
			if role.DelItem(updateconfig.itemType1, updateconfig.cnt1) < updateconfig.cnt1:
				return
		if updateconfig.cnt2 > 0:
			if role.DelItem(updateconfig.itemType2, updateconfig.cnt2) < updateconfig.cnt2:
				return
		if updateconfig.cnt3 > 0:
			if role.DelItem(updateconfig.itemType3, updateconfig.cnt3) < updateconfig.cnt3:
				return
			
		equipmentDict[equipmentConfig.posType] = updateconfig.desType

		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveUpGradeDragonEquipment, (equipmentCoding, updateconfig.desType))

	#重算主角驯龙属性
	dragonTrainMgr.recount_dragon_property(dragonId)
	role.GetPropertyGather().ReSetRecountDragonTrainFlag()
	#同步驯龙面板的数据
	SyncAllDragonEquipmentData(role)
	SyncDragonTrainMainPanelData(role)
	
	role.Msg(2, 0, GlobalPrompt.Dragon_Equip_Upgrade_Okay)

#===============================================================================
# 事件
#===============================================================================
def OnRoleInit(role, param):
	'''
	角色初始化
	@param role:
	@param param:
	'''
	role.SetTempObj(EnumTempObj.DragonTrainMgr, DragonTrainBase.DragonTrainMgr(role))

def OnRoleSave(role, param):
	'''
	角色保存
	@param role:
	@param param:
	'''
	dragonTrainMgr = role.GetTempObj(EnumTempObj.DragonTrainMgr)
	dragonTrainMgr.save()
	
#===============================================================================
# 客户端请求
#===============================================================================
def RequestDragonTrainOpenMainPanel(role, msg):
	'''
	客户端请求打开驯龙主面板
	@param role:
	@param msg:
	'''
	#等级限制
	if role.GetLevel() < DragonTrainDefine.DRAGON_TRAIN_NEED_LEVEL:
		return
	
	SyncDragonTrainMainPanelData(role)
	
def RequestDragonTrainOpenEvolvePanel(role, msg):
	'''
	客户端请求打开驯龙进化面板
	@param role:
	@param msg:
	'''
	dragonId = msg
	
	ShowEvolvePanel(role, dragonId)
	
	
def RequestDragonTrainAwaken(role, msg):
	'''
	客户端请求驯龙唤醒
	@param role:
	@param msg:
	'''
	dragonId = msg
	
	#等级限制
	if role.GetLevel() < DragonTrainDefine.DRAGON_TRAIN_NEED_LEVEL:
		return
	
	#日志
	with TraDragonTrainAwaken:
		DragonTrainAwaken(role, dragonId)
		
def RequestDragonTrainEvolve(role, msg):
	'''
	客户端请求驯龙进化
	@param role:
	@param msg:
	'''
	dragonId = msg
	
	#日志
	with TraDragonEvolve:
		DragonTrainEvolve(role, dragonId)
	
def RequestDragonTrainCollectSoul(role, msg):
	'''
	客户端请求驯龙聚灵
	@param role:
	@param msg:
	'''
	#等级限制
	if role.GetLevel() < DragonTrainDefine.DRAGON_TRAIN_NEED_LEVEL:
		return
	
	#日志
	with TraDragonCollectSoul:
		DragonTrainCollectSoul(role)
		
def RequestDragonEquipmentOpenPanel(role, msg):
	'''
	客户端请求打开龙潭面板
	@param role:
	@param msg:
	'''
	#等级限制
	if role.GetLevel() < DragonTrainDefine.DRAGON_TRAIN_NEED_LEVEL:
		return
	
	SyncAllDragonEquipmentData(role)
	
def RequestDragonEquipmentActivate(role, msg):
	'''
	客户端请求激活龙潭装备
	@param role:
	@param msg:
	'''
	dragonId, equipmentCoding = msg
	
	#等级限制
	if role.GetLevel() < DragonTrainDefine.DRAGON_TRAIN_NEED_LEVEL:
		return
	
	#日志
	with TraDragonEquipmentActivate:
		DragonEquipmentActivate(role, dragonId, equipmentCoding)
		
def RequestDragonEquipmentUpgrade(role, msg):
	'''
	客户端请求激活龙潭装备
	@param role:
	@param msg:
	'''
	dragonId, equipmentCoding = msg
	
	#等级限制
	if role.GetLevel() < DragonTrainDefine.DRAGON_TRAIN_NEED_LEVEL:
		return
	
	UpGradeDragonEquipment(role, dragonId, equipmentCoding)

		
def RequestDragonBallUpgrade(role, msg):
	'''
	客户端请求提升龙珠
	@param role:
	@param msg:
	'''
	dragonId, position = msg
	
	#等级限制
	if role.GetLevel() < DragonTrainDefine.DRAGON_TRAIN_NEED_LEVEL:
		return
	
	#日志
	with TraDragonBallUpgrade:
		DragonBallUpgrade(role, dragonId, position)


def OnRoleLogin(role, param):
	'''
	角色登录
	@param role:
	@param param:
	'''
	#登录的时候发送这条消息以通知客户端激活的龙脉技能情况
	SyncDragonTrainMainPanelData(role)

def RoleDayClear(role, param):
	'''
	玩家每日清理
	@param role:
	@param param:
	'''
	LatestActData = role.GetObj(EnumObj.LatestActData)
	LatestActData[9] = {}
	role.SendObj(Dragon_Sync_TempValue_Data, {})
	
def SyncRoleOtherData(role, param):
	LatestActData = role.GetObj(EnumObj.LatestActData)
	role.SendObj(Dragon_Sync_TempValue_Data, LatestActData.get(9, {}))
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		#角色初始化
		Event.RegEvent(Event.Eve_InitRolePyObj, OnRoleInit)
		#角色保存
		Event.RegEvent(Event.Eve_BeforeSaveRole, OnRoleSave)
		#角色登录
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnRoleLogin)
		#每日清0
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		#日志
		TraDragonTrainAwaken = AutoLog.AutoTransaction("TraDragonTrainAwaken", "驯龙唤醒")
		TraDragonCollectSoul = AutoLog.AutoTransaction("TraDragonCollectSoul", "驯龙聚灵")
		TraDragonEquipmentActivate = AutoLog.AutoTransaction("TraDragonEquipmentActivate", "驯龙装备激活")
		TraDragonBallUpgrade = AutoLog.AutoTransaction("TraDragonBallUpgrade", "驯龙提升龙珠")
		TraDragonEvolve = AutoLog.AutoTransaction("TraDragonEvolve", "驯龙进化")
		TraDragonEquipUpgrade = AutoLog.AutoTransaction("TraDragonEquipUpgrade", "驯龙装备进阶（龙骸进阶）")
	
	if Environment.HasLogic and not Environment.IsCross:
		#注册消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Dragon_Train_Open_Main_Panel", "客户端请求打开驯龙主面板"), RequestDragonTrainOpenMainPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Dragon_Train_Open_Evolve_Panel", "客户端请求打开驯龙进化面板"), RequestDragonTrainOpenEvolvePanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Dragon_Train_Awaken", "客户端请求驯龙唤醒"), RequestDragonTrainAwaken)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Dragon_Train_Evolve", "客户端请求驯龙进化"), RequestDragonTrainEvolve)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Dragon_Train_Collect_Soul", "客户端请求驯龙聚灵"), RequestDragonTrainCollectSoul)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Dragon_Equipment_Open_Panel", "客户端请求打开龙潭面板"), RequestDragonEquipmentOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Dragon_Equipment_Activate", "客户端请求激活龙潭装备"), RequestDragonEquipmentActivate)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Dragon_Ball_Upgrade", "客户端请求提升龙珠"), RequestDragonBallUpgrade)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Dragon_Equipment_Upgrade", "客户端请求提升龙骸"), RequestDragonEquipmentUpgrade)
	
