#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Wing.WingMgr")
#===============================================================================
# 翅膀管理器
#===============================================================================
import random
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Role.Data import EnumObj, EnumInt8, EnumTempObj, EnumInt16
from Game.Wing import WingConfig
from Game.Activity.WonderfulAct import WonderfulActMgr, EnumWonderType
from Game.Activity.ProjectAct import ProjectAct, EnumProActType
from Game.Activity.LatestActivity import LatestActivityMgr, EnumLatestType
		
if "_HasLoad" not in dir():
	WING_NORMAL_DATA_IDX = 1
	WING_EVOLVE_DATA_IDX = 2
	
	WING_ADVANCED_TRAIN_CNT = 50	#翅膀高级培养次数
	WING_NEED_LEVEL = 65			#翅膀系统开放等级
	WING_EVOLVE_NEED_LEVEL = 75		#翅膀进阶开放等级
	
	#交易ID索引翅膀ID
	TRADEID_TO_WINGID = {602: 2, 603: 3, 604: 4, 
						605: 5, 606: 6, 607: 7, 608: 8}
	
	#消息
	Wing_Show_Panel = AutoMessage.AllotMessage("Wing_Show_Panel", "通知客户端显示翅膀面板")
	
def ItemWingTigger(role):
	#道具增加临时进度触发
	wingDict = role.GetObj(EnumObj.Wing)[WING_NORMAL_DATA_IDX]
	if not wingDict:
		return
	
	tempValue = role.GetI16(EnumInt16.WingTempTrainValue)
	if not tempValue:
		return
	
	for wingId, data in wingDict.items():
		
		level, exp = data
		
		#翅膀配置
		wingConfig = WingConfig.WING_BASE.get((wingId, level))
		if not wingConfig:
			return
	
		#是否已经达到最高等级
		if level >= wingConfig.maxLevel:
			continue
		
		nowExp = exp + tempValue
		if nowExp >= wingConfig.levelUpExp:#给翅膀升级，并清除临时值
			wingDict[wingId] = [level + 1, 0]
			role.SetI16(EnumInt16.WingTempTrainValue, 0)
			#属性重算
			role.ResetGlobalWingProperty()
			WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_Change_Wing, [role, 0, level + 1])
			#北美用
			if Environment.EnvIsNA():
				KaiFuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
				KaiFuActMgr.wing_train_level()
			#最新活动
			LatestActivityMgr.GetFunByType(EnumLatestType.WingTrain_Latest, role)
			ShowWingPanel(role)
			return
	
def WingPutOn(role, wingId):
	'''
	装备翅膀
	@param role:
	@param wingId:
	'''
	wingDict = role.GetObj(EnumObj.Wing)[WING_NORMAL_DATA_IDX]
	
	if wingId not in wingDict:
		return
	
	role.SetI8(EnumInt8.WingId, wingId)
	
def WingPutOff(role, wingId):
	'''
	卸下翅膀
	@param role:
	@param wingId:
	'''
	wingDict = role.GetObj(EnumObj.Wing)[WING_NORMAL_DATA_IDX]
	
	if wingId not in wingDict:
		return
	
	role.SetI8(EnumInt8.WingId, 0)
	
def WingTrain(role, wingId, backFunId):
	'''
	翅膀培养
	@param role:
	@param wingId:
	@param backFunId:
	'''
	wingDict = role.GetObj(EnumObj.Wing)[WING_NORMAL_DATA_IDX]
	
	if wingId not in wingDict:
		return
	
	level, exp = wingDict[wingId]
	
	#翅膀配置
	wingConfig = WingConfig.WING_BASE.get((wingId, level))
	if not wingConfig:
		return
	
	#是否已经达到最高等级
	if level >= wingConfig.maxLevel:
		return
	
	#有道具优先扣除道具
	itemCnt = role.ItemCnt(wingConfig.trainNeedItemCoding)
	if itemCnt > 0:
		#扣物品
		role.DelItem(wingConfig.trainNeedItemCoding, 1)
	else:
		#是否够RMB
		if role.GetUnbindRMB() < wingConfig.trainNeedRMB:
			return
		#扣RMB
		role.DecUnbindRMB(wingConfig.trainNeedRMB)
	
	addExp = wingConfig.trainAddExp
	#判断是否有暴击经验
	if random.randint(1, 10000) < wingConfig.trainCritOdds:
		addExp = wingConfig.trainAddExp * wingConfig.trainCrit
	#临时经验获取
	tempExp = role.GetI16(EnumInt16.WingTempTrainValue)
	
	nowExp = exp + addExp
	if nowExp + tempExp>= wingConfig.levelUpExp:
		#升级到最高级经验设置为0
		if level + 1 >= wingConfig.maxLevel:
			nowExp = 0
		else:
			nowExp -= wingConfig.levelUpExp
			if tempExp:
				nowExp = 0
		if tempExp:#有临时修行值则清0
			role.SetI16(EnumInt16.WingTempTrainValue, 0)
			
		wingDict[wingId] = [level + 1, nowExp]
		#属性重算
		role.ResetGlobalWingProperty()
		WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_Change_Wing, [role, 0, level + 1])
		#北美用
		if Environment.EnvIsNA():
			KaiFuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
			KaiFuActMgr.wing_train_level()
		#最新活动
		LatestActivityMgr.GetFunByType(EnumLatestType.WingTrain_Latest, role)
	else:
		wingDict[wingId] = [level, nowExp]
	#精彩活动相关--增加翅膀培养次数
	WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_Wing_Times, [role, 1])
	#专题活动相关
	ProjectAct.GetFunByType(EnumProActType.ProjectWingEvent, [role, 1])
	#北美用
	if Environment.EnvIsNA():
		#北美开服
		KaiFuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
		KaiFuActMgr.wing_train_count(1)
		#北美通用活动
		HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
		HalloweenNAMgr.WingCultivate(1)
		
	#回调客户端培养成功(翅膀id，翅膀等级，翅膀经验)
	role.CallBackFunction(backFunId, (wingId, wingDict[wingId][0], wingDict[wingId][1]))
	
	#提示
	role.Msg(2, 0, GlobalPrompt.WING_TRAIN_PROMPT % addExp)
	
def WingAdvancedTrain(role, wingId, backFunId):
	'''
	翅膀高级培养
	@param role:
	@param wingId:
	@param backFunId:
	'''
	wingDict = role.GetObj(EnumObj.Wing)[WING_NORMAL_DATA_IDX]
	
	if wingId not in wingDict:
		return
	
	level, exp = wingDict[wingId]
	
	#翅膀配置
	wingConfig = WingConfig.WING_BASE.get((wingId, level))
	if not wingConfig:
		return
	
	#是否已经达到最高等级
	if level >= wingConfig.maxLevel:
		return
	
	#有道具优先扣除道具
	itemCnt = role.ItemCnt(wingConfig.trainNeedItemCoding)
	if itemCnt >= WING_ADVANCED_TRAIN_CNT:
		#扣物品
		role.DelItem(wingConfig.trainNeedItemCoding, WING_ADVANCED_TRAIN_CNT)
	else:
		#先判断RMB是否足够
		needItemCnt = WING_ADVANCED_TRAIN_CNT - itemCnt
		totalRMB = wingConfig.trainNeedRMB * needItemCnt
		#是否够RMB
		if role.GetUnbindRMB() < totalRMB:
			return
		
		if itemCnt > 0:
			#扣物品
			role.DelItem(wingConfig.trainNeedItemCoding, itemCnt)
		#扣RMB
		role.DecUnbindRMB(totalRMB)
	#临时进度
	tempExp = role.GetI16(EnumInt16.WingTempTrainValue)
	
	newLevel = level
	newExp = exp
	critCnt = 0		#暴击次数
	totalExp = 0	#总共获得的经验
	isMaxLevel = False	#等级已满
	for _ in xrange(WING_ADVANCED_TRAIN_CNT):
		addExp = wingConfig.trainAddExp
		#判断是否有暴击经验
		if random.randint(1, 10000) < wingConfig.trainCritOdds:
			addExp *= wingConfig.trainCrit
			critCnt += 1
		#计算总共获取的经验
		totalExp += addExp
		newExp += addExp
		while(newExp + tempExp >= wingConfig.levelUpExp):
			needExp = wingConfig.levelUpExp
			wingConfig = WingConfig.WING_BASE.get((wingId, newLevel + 1))
			newLevel += 1
			#有临时值
			if tempExp:
				if newExp < needExp:
					newExp = 0
				else:
					if tempExp < needExp:#假如临时值小于升级需要的经验
						newExp -= needExp - tempExp
				tempExp = 0
				role.SetI16(EnumInt16.WingTempTrainValue, 0)
			else:
				newExp -= needExp
			
			if not wingConfig or not wingConfig.levelUpExp:
				isMaxLevel = True
				#升级到最高级经验设置为0
				newExp = 0
				break
		#等级已满
		if isMaxLevel:
			break
	
	wingDict[wingId] = [newLevel, newExp]
	
	#是否要重算属性
	if newLevel != level:
		#属性重算
		role.ResetGlobalWingProperty()
		WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_Change_Wing, [role, 0, newLevel])
		#北美用
		if Environment.EnvIsNA():
			KaiFuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
			KaiFuActMgr.wing_train_level()
		#最新活动
		LatestActivityMgr.GetFunByType(EnumLatestType.WingTrain_Latest, role)
	#回调客户端培养成功(翅膀id，翅膀等级，翅膀经验)
	role.CallBackFunction(backFunId, (wingId, wingDict[wingId][0], wingDict[wingId][1]))
	
	#精彩活动相关--增加翅膀培养次数
	WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_Wing_Times, [role, WING_ADVANCED_TRAIN_CNT])
	#专题活动相关
	ProjectAct.GetFunByType(EnumProActType.ProjectWingEvent, [role, WING_ADVANCED_TRAIN_CNT])
	#北美用
	if Environment.EnvIsNA():
		#北美开服活动
		KaiFuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
		KaiFuActMgr.wing_train_count(WING_ADVANCED_TRAIN_CNT)
		#北美通用活动
		HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
		HalloweenNAMgr.WingCultivate(WING_ADVANCED_TRAIN_CNT)
	#提示
	role.Msg(2, 0, GlobalPrompt.WING_ADVANCED_TRAIN_PROMPT % (critCnt, totalExp))
	
def WingEvolve(role, wingId, backFunId):
	wingNormalDict = role.GetObj(EnumObj.Wing)[WING_NORMAL_DATA_IDX]
	wingEvolveDict = role.GetObj(EnumObj.Wing)[WING_EVOLVE_DATA_IDX]
	
	#是否已经激活翅膀
	if wingId not in wingNormalDict:
		return
	wingLevel, _ = wingNormalDict[wingId]

	#获取进阶配置
	nextGrade = 0
	if wingId not in wingEvolveDict:
		nextGrade = 1
	else:
		#是否已经达到最大阶级
		currentGrade = wingEvolveDict[wingId]
		nowEvolveConfig = WingConfig.WING_EVOLVE.get((wingId, currentGrade))
		if not nowEvolveConfig:
			return
		if currentGrade >= nowEvolveConfig.maxGrade:
			return
		
		nextGrade = currentGrade + 1
	
	#判断进阶条件
	evolveConfig = WingConfig.WING_EVOLVE.get((wingId, nextGrade))
	if not evolveConfig:
		return
	if wingLevel < evolveConfig.needWingLevel:
		return
	if role.ItemCnt(evolveConfig.needItemCoding) < evolveConfig.needItemCnt:
		return
	
	#消耗
	role.DelItem(evolveConfig.needItemCoding, evolveConfig.needItemCnt)
	
	#升阶
	wingEvolveDict[wingId] = nextGrade
	
	#属性重算
	role.ResetGlobalWingProperty()
	
	#回调客户端进阶成功(翅膀id，阶级)
	role.CallBackFunction(backFunId, (wingId, nextGrade))
	
#===============================================================================
# 显示
#===============================================================================
def ShowWingPanel(role):
	'''
	显示翅膀面板
	@param role:
	'''
	wingDataDict = role.GetObj(EnumObj.Wing)[WING_NORMAL_DATA_IDX]
	wingEvolveDict = role.GetObj(EnumObj.Wing)[WING_EVOLVE_DATA_IDX]
	
	#发送给客户端
	role.SendObj(Wing_Show_Panel, (wingDataDict, wingEvolveDict))
	
#===============================================================================
# 事件
#===============================================================================
def OnRoleInit(role, param):
	'''
	角色初始化
	@param role:
	@param param:
	'''
	wingDict = role.GetObj(EnumObj.Wing)
	
	#初始化翅膀进阶数据
	if WING_EVOLVE_DATA_IDX not in wingDict:
		wingDict[WING_EVOLVE_DATA_IDX] = {}

def RoleDayClear(role, param):
	'''
	玩家每日清理
	@param role:
	@param param:
	'''
	if role.GetI16(EnumInt16.WingTempTrainValue) > 0:
		role.SetI16(EnumInt16.WingTempTrainValue, 0)
#===============================================================================
# 接口
#===============================================================================
def AddWing(role, wingId):
	'''添加一个翅膀'''
	wingDict = role.GetObj(EnumObj.Wing)[WING_NORMAL_DATA_IDX]
	
	#是否已经拥有这个翅膀
	if wingId in wingDict:
		return
	
	#是否有这个翅膀配置
	wingConfig = WingConfig.WING_BASE.get((wingId, 1))
	if not wingConfig:
		return
	
	#等级，经验
	wingDict[wingId] = [1, 0]
	
	#如果没有佩戴翅膀则自动佩戴
	if role.GetI8(EnumInt8.WingId) == 0:
		role.SetI8(EnumInt8.WingId, wingId)

	WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_Change_Wing, [role, 1, 1])
	#属性重算
	role.ResetGlobalWingProperty()
	
	#日志事件
	AutoLog.LogBase(role.GetRoleID(), AutoLog.eveAddWing, wingId)
#===============================================================================
# 客户端请求
#===============================================================================
def RequestWingOpenPanel(role, msg):
	'''
	客户端请求打开翅膀面板
	@param role:
	@param msg:
	'''
	#等级限制
	if role.GetLevel() < WING_NEED_LEVEL:
		return
	
	ShowWingPanel(role)
	
def RequestWingPutOn(role, msg):
#	'''
#	客户端请求装备翅膀
#	@param role:
#	@param msg:
#	'''
#羽翼系统的穿戴和卸下功能屏蔽，移至时装系统
#	wingId = msg
#	
#	#等级限制
#	if role.GetLevel() < WING_NEED_LEVEL:
#		return
#	
#	WingPutOn(role, wingId)

	pass

def RequestWingPutOff(role, msg):
#	'''
#	客户端请求卸下翅膀
#	@param role:
#	@param msg:
#	'''
#羽翼系统的穿戴和卸下功能屏蔽，移至时装系统
#	wingId = msg
#	
#	#等级限制
#	if role.GetLevel() < WING_NEED_LEVEL:
#		return
#	
#	WingPutOff(role, wingId)
	pass

def RequestWingTrain(role, msg):
	'''
	客户端请求翅膀培养
	@param role:
	@param msg:
	'''
	backFunId, data = msg
	wingId = data
	
	#等级限制
	if role.GetLevel() < WING_NEED_LEVEL:
		return
	
	#日志
	with TraWingTrain:
		WingTrain(role, wingId, backFunId)
	
def RequestWingAdvancedTrain(role, msg):
	'''
	客户端请求翅膀高级培养
	@param role:
	@param msg:
	'''
	backFunId, data = msg
	wingId = data
	
	#等级限制
	if role.GetLevel() < WING_NEED_LEVEL:
		return
	
	#日志
	with TraWingAdvancedTrain:
		WingAdvancedTrain(role, wingId, backFunId)
		
def RequestWingEvolve(role, msg):
	'''
	客户端请求翅膀进阶
	@param role:
	@param msg:
	'''
	backFunId, wingId = msg
	
	#等级限制
	if role.GetLevel() < WING_EVOLVE_NEED_LEVEL:
		return
	
	#日志
	with TraWingEvolve:
		WingEvolve(role, wingId, backFunId)
	
	
if "_HasLoad" not in dir():
	#角色初始化
	Event.RegEvent(Event.Eve_InitRolePyObj, OnRoleInit)
	#每日清理
	Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
	#日志
	TraWingTrain = AutoLog.AutoTransaction("TraWingTrain", "翅膀培养")
	TraWingAdvancedTrain = AutoLog.AutoTransaction("TraWingAdvancedTrain", "翅膀高级培养")
	TraWingEvolve = AutoLog.AutoTransaction("TraWingEvolve", "翅膀进阶")
	
	#注册消息
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Wing_Open_Panel", "客户端请求打开翅膀面板"), RequestWingOpenPanel)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Wing_Put_On", "客户端请求装备翅膀"), RequestWingPutOn)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Wing_Put_Off", "客户端请求卸下翅膀"), RequestWingPutOff)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Wing_Train", "客户端请求翅膀培养"), RequestWingTrain)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Wing_Advanced_Train", "客户端请求翅膀高级培养"), RequestWingAdvancedTrain)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Wing_Evolve", "客户端请求翅膀进阶"), RequestWingEvolve)
	