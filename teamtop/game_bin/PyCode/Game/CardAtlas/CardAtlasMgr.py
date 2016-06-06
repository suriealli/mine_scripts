#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.CardAtlas.CardAtlasMgr")
#===============================================================================
# 卡牌图鉴
#===============================================================================
from Common.Message import AutoMessage
import cRoleMgr
import Environment
from Game.Role import Event
from Game.Role.Data import EnumObj, EnumInt32
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.CardAtlas import CardAtlasConfig
from ComplexServer.Log import AutoLog

if "_HasLoad" not in dir():
	#{卡牌id:卡牌数目}
	CardAtlas_SyncData = AutoMessage.AllotMessage("CardAtlas_SyncData", "卡牌图鉴同步数据")
	#{图鉴组id:{0:图鉴组品阶, 图鉴id:[品阶, 等级]}
	CardAtlasSuit_SyncData = AutoMessage.AllotMessage("CardAtlasSuit_SyncData", "卡牌图鉴组同步数据")
	#{图鉴id:[品阶, 等级]
	CardAtlasAll_SyncData = AutoMessage.AllotMessage("CardAtlasAll_SyncData", "卡牌图鉴所有图鉴同步数据")
	
	
	CardAtlasAct_Log = AutoLog.AutoTransaction("CardAtlasAct_Log", "图鉴激活日志")
	CardAtlasUpgrade_Log = AutoLog.AutoTransaction("CardAtlasUpgrade_Log", "图鉴升阶日志")
	CardAtlasLevel_Log = AutoLog.AutoTransaction("CardAtlasLevel_Log", "图鉴升级日志")
	CardAtlasChip_Log = AutoLog.AutoTransaction("CardAtlasChip_Log", "图鉴卡牌分解日志")
#===============================================================================
# 客户端请求
#===============================================================================
def RequestAct(role, msg):
	'''
	请求激活图鉴
	@param role:
	@param msg:
	'''
	if role.GetLevel() < EnumGameConfig.CardAtlasLevel:
		return
	
	atlasId = msg
	
	cfg = CardAtlasConfig.AtlasAct_Dict.get(atlasId)
	if (not cfg) or (not cfg.actNeedCard) or (cfg.belongSuit not in CardAtlasConfig.AtlasBelong_Dict):
		return
	
	cardAtlasObj = role.GetObj(EnumObj.CardAtlasDict)
	if not cardAtlasObj or 1 not in cardAtlasObj or 2 not in cardAtlasObj:
		return
	
	#已经激活过了
	if cfg.belongSuit in cardAtlasObj[2] and atlasId in cardAtlasObj[2][cfg.belongSuit]:
		return
	#没有激活需要的卡牌
	cardCnt = cardAtlasObj[1].get(cfg.actNeedCard)
	if not cardCnt:
		return
	
	with CardAtlasAct_Log:
		#扣卡牌
		cardAtlasObj[1][cfg.actNeedCard] = cardCnt = cardAtlasObj[1][cfg.actNeedCard] - 1
		if not cardCnt:
			del cardAtlasObj[1][cfg.actNeedCard]
		
		#激活图鉴
		if cfg.belongSuit not in cardAtlasObj[2]:
			cardAtlasObj[2][cfg.belongSuit] = {0:0}
		cardAtlasObj[2][cfg.belongSuit][atlasId] = [cfg.atlasGrade, 0]
		#激活图鉴组
		minGrade = 0
		if len(CardAtlasConfig.AtlasBelong_Dict[cfg.belongSuit]) == (len(cardAtlasObj[2][cfg.belongSuit]) - 1):
			gradeList = [data[0] for k, data in cardAtlasObj[2][cfg.belongSuit].iteritems() if k]
			if not gradeList:
				print 'GE_EXC, CardAtlasMgr RequestAct act card atlas suit error min grade %s' % role.GetRoleID()
			else:
				cardAtlasObj[2][cfg.belongSuit][0] = minGrade = min(gradeList)
		role.ResetGlobalCardAtlasProperty()
		
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveCardAtlasAct, (atlasId, minGrade))
	
	role.SendObj(CardAtlas_SyncData, cardAtlasObj[1])
	role.SendObj(CardAtlasSuit_SyncData, cardAtlasObj[2])
	role.SendObj(CardAtlasAll_SyncData, {k:v for d in cardAtlasObj[2].values() for k, v in d.items() if k})
	
	role.Msg(2, 0, GlobalPrompt.CardAtlasAct)
	
def RequestUpGrade(role, msg):
	'''
	请求图鉴升阶
	@param role:
	@param msg:
	'''
	if role.GetLevel() < EnumGameConfig.CardAtlasLevel:
		return
	
	atlasId = msg
	
	cardAtlasObj = role.GetObj(EnumObj.CardAtlasDict)
	if not cardAtlasObj or 1 not in cardAtlasObj or 2 not in cardAtlasObj:
		return
	
	actCfg = CardAtlasConfig.AtlasAct_Dict.get(atlasId)
	if not actCfg or not actCfg.belongSuit:
		return
	
	if actCfg.belongSuit not in cardAtlasObj[2]:
		return
	atlasData = cardAtlasObj[2][actCfg.belongSuit].get(atlasId)
	if not atlasData:
		return
	
	upgradeCfg = CardAtlasConfig.AtlasGrade_Dict.get((atlasId, atlasData[0]))
	if not upgradeCfg or not upgradeCfg.upGradeNeedCard or upgradeCfg.nextGrade == -1:
		return
	
	cardCnt = cardAtlasObj[1].get(upgradeCfg.upGradeNeedCard)
	if not cardCnt:
		return
	
	with CardAtlasUpgrade_Log:
		cardAtlasObj[1][upgradeCfg.upGradeNeedCard] = cardCnt = cardAtlasObj[1][upgradeCfg.upGradeNeedCard] - 1
		if not cardCnt:
			del cardAtlasObj[1][upgradeCfg.upGradeNeedCard]
		
		cardAtlasObj[2][actCfg.belongSuit][atlasId][0] = upgradeCfg.nextGrade
		
		#计算套装品阶
		
		minGrade = cardAtlasObj[2][actCfg.belongSuit][0]
		if minGrade:
			gradeList = [data[0] for k, data in cardAtlasObj[2][actCfg.belongSuit].iteritems() if k]
			if not gradeList:
				print 'GE_EXC, CardAtlasMgr RequestUpGrade act card atlas suit error min grade %s' % role.GetRoleID()
			else:
				cardAtlasObj[2][actCfg.belongSuit][0] = minGrade = min(gradeList)
		role.ResetGlobalCardAtlasProperty()
		
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveCardAtlasUpgrade, (atlasId, upgradeCfg.nextGrade, actCfg.belongSuit, minGrade))
	
	role.SendObj(CardAtlas_SyncData, cardAtlasObj[1])
	role.SendObj(CardAtlasSuit_SyncData, cardAtlasObj[2])
	role.SendObj(CardAtlasAll_SyncData, {k:v for d in cardAtlasObj[2].values() for k, v in d.items() if k})
	
	role.Msg(2, 0, GlobalPrompt.CardAtlasGradeUp)
	
def RequestUpLevel(role, msg):
	'''
	请求图鉴升级
	@param role:
	@param msg:
	'''
	if role.GetLevel() < EnumGameConfig.CardAtlasLevel:
		return
	
	atlasId = msg
	
	cardAtlasObj = role.GetObj(EnumObj.CardAtlasDict)
	if not cardAtlasObj or 1 not in cardAtlasObj or 2 not in cardAtlasObj:
		return
	
	actCfg = CardAtlasConfig.AtlasAct_Dict.get(atlasId)
	if not actCfg or not actCfg.belongSuit:
		return
	
	if actCfg.belongSuit not in cardAtlasObj[2]:
		return
	atlasData = cardAtlasObj[2][actCfg.belongSuit].get(atlasId)
	if not atlasData:
		return
	
	levelCfg = CardAtlasConfig.AtlasLevel_Dict.get(atlasData[1])
	if not levelCfg or levelCfg.nextLevel == -1 or not levelCfg.upLevelNeedChip:
		return
	
	nextCfg = CardAtlasConfig.AtlasLevel_Dict.get(levelCfg.nextLevel)
	if not nextCfg:
		return
	if nextCfg.needGrade > atlasData[0]:
		return
	
	if role.GetI32(EnumInt32.CardAtlasChip) < levelCfg.upLevelNeedChip:
		return
	
	with CardAtlasLevel_Log:
		role.DecI32(EnumInt32.CardAtlasChip, levelCfg.upLevelNeedChip)
		
		atlasData[1] += 1
		
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveCardAtlasLevel, (atlasId, atlasData[1]))
	
	role.ResetGlobalCardAtlasProperty()
	
	role.SendObj(CardAtlasSuit_SyncData, cardAtlasObj[2])
	role.SendObj(CardAtlasAll_SyncData, {k:v for d in cardAtlasObj[2].values() for k, v in d.items() if k})
	
	role.Msg(2, 0, GlobalPrompt.CardAtlasLevelUp)
	
def RequestSplit(role, msg):
	'''
	请求拆解图鉴
	@param role:
	@param msg:
	'''
	if role.GetLevel() < EnumGameConfig.CardAtlasLevel:
		return
	
	cardId, cnt = msg
	
	cardAtlasObj = role.GetObj(EnumObj.CardAtlasDict)
	if not cardAtlasObj or 1 not in cardAtlasObj or 2 not in cardAtlasObj:
		return
	
	allCnt = cardAtlasObj[1].get(cardId)
	if not allCnt or cnt <= 0 or allCnt < cnt:
		return
	
	cfg = CardAtlasConfig.Card_Dict.get(cardId)
	if not cfg or not cfg.returnChip:
		return
	
	returnChip = cfg.returnChip * cnt
	
	with CardAtlasChip_Log:
		if allCnt == cnt:
			del cardAtlasObj[1][cardId]
		else:
			cardAtlasObj[1][cardId] -= cnt
		
		role.IncI32(EnumInt32.CardAtlasChip, returnChip)
		
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveCardAtlasChip, cardId)
		
	role.SendObj(CardAtlas_SyncData, cardAtlasObj[1])
	
	role.Msg(2, 0, GlobalPrompt.CardAtlasChip % returnChip)
#===============================================================================
# 事件
#===============================================================================
def AfterLogin(role, param):
	if not role.GetObj(EnumObj.CardAtlasDict):
		role.SetObj(EnumObj.CardAtlasDict, {1:{}, 2:{}})
	
def SyncRoleOtherData(role, param):
	cardAtlasObj = role.GetObj(EnumObj.CardAtlasDict)
	if not cardAtlasObj:
		return
	
	role.SendObj(CardAtlas_SyncData, cardAtlasObj[1])
	role.SendObj(CardAtlasSuit_SyncData, cardAtlasObj[2])
	role.SendObj(CardAtlasAll_SyncData, {k:v for d in cardAtlasObj[2].values() for k, v in d.items() if k})
	
#===============================================================================
# 绑定role
#===============================================================================
def AddCardAtlas(role, cardId, cnt):
	'''增加卡牌'''
	if role.CardAtlasPackageIsFull():
		return
	cardAtlasObj = role.GetObj(EnumObj.CardAtlasDict)
	if not cardAtlasObj or 1 not in cardAtlasObj:
		return
	if cardId not in cardAtlasObj[1]:
		cardAtlasObj[1][cardId] = cnt
	else:
		cardAtlasObj[1][cardId] += cnt
	role.SendObj(CardAtlas_SyncData, cardAtlasObj[1])

def CardAtlasPackageIsFull(role):
	'''卡牌图鉴背包是否满了'''
	return len(role.GetObj(EnumObj.CardAtlasDict).get(1, {})) >= EnumGameConfig.CAMaxPackageSize

def CardAtlasPackageEmptySize(role):
	'''卡牌图鉴背包空格数'''
	return EnumGameConfig.CAMaxPackageSize - len(role.GetObj(EnumObj.CardAtlasDict).get(1, {}))

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CardAtlas_Act", "请求激活图鉴"), RequestAct)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CardAtlas_UpGrade", "请求图鉴升阶"), RequestUpGrade)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CardAtlas_UpLevel", "请求图鉴升级"), RequestUpLevel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CardAtlas_Split", "请求拆解图鉴"), RequestSplit)
		
	
