#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Tarot.TarotOperate")
#===============================================================================
# 塔罗牌操作
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Role.Data import EnumTempObj, EnumInt8, EnumInt32, EnumObj, EnumCD
from Game.Role.Mail import Mail
from Game.Tarot import TarotConfig, TarotBase



#背包ID(程序用)
TAROT_PACKAGE_ID = 1
ROLE_TAROT_PACKAGE_ID = 2

#一键出售的卡类型
SellTarotCardType = 1
#最大等级
TarotCardMaxLevel = 10

if "_HasLoad" not in dir():
	#消息
	Tarot_S_AllData = AutoMessage.AllotMessage("Tarot_S_AllData", "同步所有塔罗牌数据(EnumObj.En_Tarot)")
	Tarot_S_AddCard = AutoMessage.AllotMessage("Tarot_S_AddCard", "同步获得一个命魂(id, type)")

	#日志
	TraTarot_ZhanBu = AutoLog.AutoTransaction("TraTarot_ZhanBu", "塔罗牌占卜")
	TraTarot_OneKeyZhanBu = AutoLog.AutoTransaction("TraTarot_OneKeyZhanBu", "塔罗牌一键占卜")
	TraTarot_SuperZhanBu = AutoLog.AutoTransaction("TraTarot_SuperZhanBu", "塔罗牌超级占卜")
	TraTarot_Sell = AutoLog.AutoTransaction("TraTarot_Sell", "塔罗牌出售")
	TraTarot_OneKeySell = AutoLog.AutoTransaction("TraTarot_OneKeySell", "塔罗牌一键出售")
	TraTarot_SuperSell = AutoLog.AutoTransaction("TraTarot_SuperSell", "塔罗牌超级抽取出售")
	TraTarot_Mix = AutoLog.AutoTransaction("TraTarot_Mix", "塔罗牌融合")
	TraTarot_OneKeyMix = AutoLog.AutoTransaction("TraTarot_OneKeyMix", "塔罗牌一键融合")
	TraTarot_SuperMix = AutoLog.AutoTransaction("TraTarot_SuperMix", "塔罗牌超级占卜融合")
	
	TraTarot_ActiveByRMB = AutoLog.AutoTransaction("TraTarot_ActiveByRMB", "塔罗牌高级占卜")
	TraTarot_ExchangeCard = AutoLog.AutoTransaction("TraTarot_ExchangeCard", "塔罗牌兑换")
	TraTarot_OnStrengthenTarotRing = AutoLog.AutoTransaction("TraTarot_OnStrengthenTarotRing", "强化占卜光环")



##################################################################################
def GetTarotMgr(role):
	'''获取角色临时塔罗牌管理器'''
	return role.GetTempObj(EnumTempObj.enTarotMgr)

def GetMaxPackageSize(role):
	return role.GetI8(EnumInt8.TarotEquipmentPackageSize)

def GetTarotEmptySize(role):
	'''获取命魂背包格子数'''
	return role.GetTempObj(EnumTempObj.enTarotMgr).PackageEmptySize()

def TarotPackageIsFull(role):
	'''命魂背包是否已经满了'''
	return role.GetTempObj(EnumTempObj.enTarotMgr).PackageIsFull()


def AddTarotCard(role, card_type, cnt):
	'''增加一个命魂'''
	TM = role.GetTempObj(EnumTempObj.enTarotMgr)
	if TM.PackageEmptySize() < cnt:
		#空间不足
		Mail.SendMail(role.GetRoleID(), GlobalPrompt.PackageFullTitle, GlobalPrompt.Sender, GlobalPrompt.Content, None, [card_type] * cnt)
		return
	
	if cnt == 1:
		cardId, _, = TM.NewTarotCard(card_type)
		role.SendObj(Tarot_S_AddCard, (cardId, card_type))
		return
	else:
		for _ in xrange(cnt):
			cardId, _, = TM.NewTarotCard(card_type)
			role.SendObj(Tarot_S_AddCard, (cardId, card_type))


##################################################################################




##################################################################################
#客户端请求
##################################################################################
def OnTarotZhanBu(role, msg):
	'''
	请求占卜
	@param role:
	@param msg:
	'''
	backId, _ = msg
	nowIndex = role.GetI8(EnumInt8.TarotIndex)
	if not nowIndex:
		return
	
	cfg = TarotConfig.Tarot_ZhanBu_Config_Dict.get(nowIndex)
	if not cfg:
		return
	
	if role.GetMoney() < cfg.needMoney:
		return
	TM = GetTarotMgr(role)
	if TM.PackageIsFull():
		return
	
	with TraTarot_ZhanBu:
		role.DecMoney(cfg.needMoney)
	
		role.SetI8(EnumInt8.TarotIndex, cfg.RandomNextIndex())
		cardType = cfg.RandomCardType(role.GetLevel())
		
		cardId, cardGrade = TM.NewTarotCard(cardType)
		
		role.CallBackFunction(backId, (cardId, cardType))
		
		if cardGrade > 4:
			cRoleMgr.Msg(3, 0, GlobalPrompt.TarotGradeTips % (role.GetRoleName(), cardType, 1))
		
		#北美通用
		if Environment.EnvIsNA():
			HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
			HalloweenNAMgr.TarotTimes(1)

def OneKeyZhanBu(role, msg):
	'''
	一键占卜
	@param role:
	@param msg:
	'''
	backId, _ = msg
	TM = GetTarotMgr(role)
	packageEmptySize = TM.PackageEmptySize()
	if not packageEmptySize:
		return
	
	roleMoney = role.GetMoney()
	needMoney = 0
	nowIndex = role.GetI8(EnumInt8.TarotIndex)
	newCardList = []
	NA = newCardList.append
	roleLevel = role.GetLevel()
	TTG = TarotConfig.Tarot_ZhanBu_Config_Dict.get
	for _ in range(packageEmptySize):
		cfg = TTG(nowIndex)
		if not cfg:
			return
		needMoney += cfg.needMoney
		if needMoney > roleMoney:
			needMoney -= cfg.needMoney
			break
		NA(cfg.RandomCardType(roleLevel))
		nowIndex = cfg.RandomNextIndex()
	
	if not needMoney or not newCardList:
		return
	with TraTarot_OneKeyZhanBu:
		role.DecMoney(needMoney)
		role.SetI8(EnumInt8.TarotIndex, nowIndex)
		
		res, tpl = TM.NewTarotCards(newCardList)
		
		role.CallBackFunction(backId, res)
		
		roleName = role.GetRoleName()
		for cardType in tpl:
			cRoleMgr.Msg(3, 0, GlobalPrompt.TarotGradeTips % (roleName, cardType, 1))
		
		#北美通用
		if Environment.EnvIsNA():
			HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
			HalloweenNAMgr.TarotTimes(len(newCardList))

def SuperZhanBu(role, msg):
	'''
	请求超级抽取--300次抽取
	@param role:
	@param msg:
	'''
#	if role.GetCD(EnumCD.TarotSuperZhanbuCD):
#		return
	
	backId, _ = msg
	
	roleMoney = role.GetMoney()
	if roleMoney < EnumGameConfig.TarotSuperZhanbuMoneyLimit:
		return
	if role.GetVIP() < EnumGameConfig.TarotSuperZhanbuVipLimit:
		return
	if role.GetLevel() < EnumGameConfig.TarotSuperZhanbuLvLimit:
		return
	
	needMoney = 0
	nowIndex = role.GetI8(EnumInt8.TarotIndex)
	newCardList = []
	roleLevel = role.GetLevel()
	TTG = TarotConfig.Tarot_ZhanBu_Config_Dict.get
	
	global SellTarotCardType
	sellTarotCfg = TarotConfig.TarotCardConfig_Dict.get(SellTarotCardType)
	if not sellTarotCfg:
		return
	sellMoney = sellTarotCfg.sellMoney
	
	rumorTarotList = []
	RE = rumorTarotList.extend
	
	#先出售所有的金币命魂
	TM = GetTarotMgr(role)
	totalMoney = 0
	global TAROT_PACKAGE_ID
	packageDict = TM.tarotOwner_ID_Dict[TAROT_PACKAGE_ID]
	for cardId, card in packageDict.items():
		if card.IsLock():
			continue
		if card.cardType == SellTarotCardType:
			totalMoney += card.card_cfg.sellMoney
			del packageDict[cardId]
	if totalMoney:
		with TraTarot_SuperSell:
			role.IncMoney(totalMoney)
			roleMoney += totalMoney
	
	#计算背包格子
	packageEmptySize = TM.PackageEmptySize()
	if not packageEmptySize:
		return
	
	#300次抽取
	for _ in xrange(300):
		cfg = TTG(nowIndex)
		if not cfg:
			return
		needMoney += cfg.needMoney
		if needMoney > roleMoney:
			needMoney -= cfg.needMoney
			break
		cardType = cfg.RandomCardType(roleLevel)
		
		if cardType == SellTarotCardType:
			#金币元魂卖掉
			needMoney -= sellMoney
		else:
			packageEmptySize -= 1
			#其他的记录下来
			newCardList.append(cardType)
			
		nowIndex = cfg.RandomNextIndex()
		
		if packageEmptySize <= 0:
			#背包满了, 先融合一下
			tpl = SuperMix(role, newCardList, needMoney)
			roleMoney -= needMoney
			newCardList = []
			
			needMoney = 0
			if tpl:
				RE(tpl)
			#重新获取背包空格子数量
			packageEmptySize = TM.PackageEmptySize()
			if packageEmptySize <= 0:
				break
		
	if newCardList:
		#如果300次跑完了, 还有没有融合的, 融合一下
		tpl = SuperMix(role, newCardList, needMoney)
		if tpl:
			RE(tpl)
	
	role.SetI8(EnumInt8.TarotIndex, nowIndex)
#	role.SetCD(EnumCD.TarotSuperZhanbuCD, 1)
	
	packageDict = TM.tarotOwner_ID_Dict[TAROT_PACKAGE_ID]
	
	#回调 [[cardId, (cardType, level, exp, isLock)]]
	role.CallBackFunction(backId, [[cardId, (card.cardType, card.level, card.exp, card.isLock)] for cardId, card in packageDict.iteritems()])
	
	roleName = role.GetRoleName()
	
	for cardType in rumorTarotList:
		cRoleMgr.Msg(3, 0, GlobalPrompt.TarotGradeTips % (roleName, cardType, 1))
	
	#北美通用
	if Environment.EnvIsNA():
		HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
		HalloweenNAMgr.TarotTimes(len(newCardList))
	
	role.Msg(2, 0, GlobalPrompt.TarotSuperSuccess)
	
def SuperMix(role, newCardList, needMoney):
	#超级抽取融合
	TM = GetTarotMgr(role)
	
	#生成
	with TraTarot_SuperZhanBu:
		role.DecMoney(needMoney)
		_, tpl = TM.NewTarotCards(newCardList)
	
	mainCard = None
	packageDict = TM.tarotOwner_ID_Dict[TAROT_PACKAGE_ID]
	totalExp = 0
	delList = []
	DA = delList.append
	
	for carId, card in packageDict.items():
		if not card.OneKeyMix():
			#金币命魂和经验命魂不参与一键融合
			continue
		if card.level >= TarotCardMaxLevel:
			#满级不参与
			continue
		if mainCard is None:
			mainCard = card
			continue
		
		if mainCard.grade < card.grade or (mainCard.grade == card.grade and mainCard.level < card.level):
			if not mainCard.IsLock():
				DA(mainCard.cardId)
				totalExp += mainCard.GetMixExp()

			mainCard = card
		elif not card.IsLock():
			DA(carId)
			totalExp += card.GetMixExp()
	
	if mainCard is None or not delList or not totalExp:
		return None
	
	TMD = TM.DelPackageCard
	with TraTarot_SuperMix:
		for cardId in delList:
			TMD(cardId)
		#不同步客户端的提升经验
		mainCard.IncCardExpEx(totalExp)
	
	#返回需要公告的
	return tpl

def OnLockTarot(role, msg):
	'''
	锁定命魂
	@param role:
	@param msg:
	'''
	backId, (cardId, param) = msg
	if param != 1 and param != 0:
		return
	TM = GetTarotMgr(role)
	card = TM.GetPackageCard(cardId)
	if not card:
		return
	card.isLock = param
	role.CallBackFunction(backId, (cardId, param))


def OnSellTarot(role, msg):
	'''
	出售一张塔罗牌
	@param role:
	@param msg:
	'''
	backId, cardId = msg
	TM = GetTarotMgr(role)
	card = TM.GetPackageCard(cardId)
	if not card:
		return
	if card.IsLock():
		return
	card_cfg = card.card_cfg
	if not card_cfg.sellMoney and not card_cfg.sellHp:
		return
	
	with TraTarot_Sell:
		TM.DelPackageCard(cardId) 
		
		if card_cfg.sellMoney:
			role.IncMoney(card_cfg.sellMoney)
		if card_cfg.sellHp:
			role.IncI32(EnumInt32.TaortHP, card_cfg.sellHp)

	role.CallBackFunction(backId, cardId)


def OnOneKeySell(role, msg):
	'''
	一键出售
	@param role:
	@param msg:
	'''
	backId, _ = msg
	
	TM = GetTarotMgr(role)
	totalMoney = 0
	packageDict = TM.tarotOwner_ID_Dict[TAROT_PACKAGE_ID]
	sellIds = []
	SA = sellIds.append
	for cardId, card in packageDict.items():
		if card.IsLock():
			continue
		if card.cardType == SellTarotCardType:
			totalMoney += card.card_cfg.sellMoney
			del packageDict[cardId]
			SA(cardId)
	if not totalMoney:
		return
	
	with TraTarot_OneKeySell:
		role.IncMoney(totalMoney)
	role.CallBackFunction(backId, sellIds)


def MixTarotCard(role, msg):
	'''
	融合两张塔罗牌
	@param role:
	@param msg: (mainCard , deadId) mainId主卡Id, deadId 被吞噬的卡
	'''
	backId, (mianId, deadId) = msg
	TM = GetTarotMgr(role)
	mainCard = TM.GetPackageCard(mianId)
	if not mainCard:
		return
	
	if not mainCard.CanMix():
		return
	
	if mainCard.level >= TarotCardMaxLevel:
		return
	
	deadCard = TM.GetPackageCard(deadId)
	if not deadCard:
		return
	
	if deadCard.IsLock():
		return
	
	if not deadCard.CanBeMix():
		return
	
	with TraTarot_Mix:
		exp = deadCard.GetMixExp()
		TM.DelPackageCard(deadId)
		
		mainCard.IncCardExp(exp)
		
	role.CallBackFunction(backId, deadId)
	
def OneKeyMixCard(role, msg):
	'''
	一键融合
	@param role:
	@param msg:
	'''
	backId, _ = msg
	mainCard = None
	TM = GetTarotMgr(role)
	packageDict = TM.tarotOwner_ID_Dict[TAROT_PACKAGE_ID]
	totalExp = 0
	delList = []
	DA = delList.append

	for carId, card in packageDict.items():
		if not card.OneKeyMix():
			#金币命魂和经验命魂不参与一键融合
			continue
		if card.level >= TarotCardMaxLevel:
			#满级不参与
			continue
		if mainCard is None:
			mainCard = card
			continue

		if mainCard.grade < card.grade or (mainCard.grade == card.grade and mainCard.level < card.level):
			if not mainCard.IsLock():
				DA(mainCard.cardId)
				totalExp += mainCard.GetMixExp()

			mainCard = card
		elif not card.IsLock():
			DA(carId)
			totalExp += card.GetMixExp()

	if mainCard is None or not delList or not totalExp:
		return
	TMD = TM.DelPackageCard
	with TraTarot_OneKeyMix:
		for cardId in delList:
			TMD(cardId)
		mainCard.IncCardExp(totalExp)

	role.CallBackFunction(backId, delList)

def OnRolePutOnTarot(role, msg):
	'''
	角色佩戴卡牌
	@param role:
	@param msg:
	'''
	backId, (cardId, pos) = msg
	if pos < 0 or pos > 8:
		return
	TM = GetTarotMgr(role)
	package_card = TM.GetPackageCard(cardId)
	
	if not package_card:
		return
	if not package_card.CanEquitment():
		return
	
	roleTarotDict = TM.tarotOwner_ID_Dict[ROLE_TAROT_PACKAGE_ID]
	#是否已经装备满了
	if GetMaxPackageSize(role) <= len(roleTarotDict):
		return
	
	cardPt = (package_card.card_cfg.pt, package_card.card_cfg.pt2)
	for card in roleTarotDict.itervalues():
		if (card.card_cfg.pt, card.card_cfg.pt2) == cardPt:
			#不可以装备同类型的命魂
			return
		if card.pos == pos:
			#这个位置已经有卡了
			return
	
	
	del TM.tarotOwner_ID_Dict[TAROT_PACKAGE_ID][cardId]
	
	roleTarotDict[cardId] = package_card
	#修改位置
	package_card.pos = pos
	
	#重算属性
	role.GetPropertyGather().ReSetRecountTarotFlag()
	
	#回调
	role.CallBackFunction(backId, cardId)

	
def OnHeroPutOnTarot(role, msg):
	'''
	英雄佩戴塔罗牌
	@param role:
	@param msg:
	'''
	
	backId, (heroId, cardId, pos) = msg
	if pos < 0 or pos > 8:
		return
	TM = GetTarotMgr(role)
	package_card = TM.GetPackageCard(cardId)
	if not package_card:
		return
	if not package_card.CanEquitment():
		return
	
	hero = role.GetHero(heroId)
	if not hero:
		return
	if not hero.GetStationID():
		return
	
	heroTarotDict = TM.GetOwnerTarotDict(heroId)
	if heroTarotDict is None:
		print "GE_EXC, error in OnHeroPutOnTarot"
		return
	#是否已经装备满了
	if GetMaxPackageSize(role) <= len(heroTarotDict):
		return
	
	cardPt = (package_card.card_cfg.pt, package_card.card_cfg.pt2)
	for card in heroTarotDict.itervalues():
		if (card.card_cfg.pt, card.card_cfg.pt2) == cardPt:
			#不可以装备同类型的命魂
			return
		if card.pos == pos:
			#这个位置已经有卡了
			return
	
	del TM.tarotOwner_ID_Dict[TAROT_PACKAGE_ID][cardId]
	heroTarotDict[cardId] = package_card
	#修改位置
	package_card.pos = pos
	
	#重算属性
	hero.GetPropertyGather().ReSetRecountTarotFlag()
	
	role.CallBackFunction(backId, (heroId, cardId))
	
	
def OnTakeOffRoleTarot(role, msg):
	'''
	主角脱下一个塔罗牌
	@param role:
	@param msg:
	'''
	backId, cardId = msg
	TM = GetTarotMgr(role)
	
	if TM.PackageIsFull():
		return
	
	roleTarotDict = TM.tarotOwner_ID_Dict[ROLE_TAROT_PACKAGE_ID]
	card = roleTarotDict.get(cardId)
	if not card:
		return
	
	del roleTarotDict[cardId]
	#修改位置
	card.pos = 0
	TM.tarotOwner_ID_Dict[TAROT_PACKAGE_ID][cardId] = card
	#重算属性
	role.GetPropertyGather().ReSetRecountTarotFlag()
	role.CallBackFunction(backId, cardId)

def OnTakeOffHeroTarot(role, msg):
	'''
	英雄脱下一个塔罗牌
	@param role:
	@param msg:
	'''
	backId, (heroId, cardId) = msg
	
	TM = GetTarotMgr(role)
	if TM.PackageIsFull():
		return
	
	hero = role.GetHero(heroId)
	if not hero:
		return
	
	heroTarotDict = TM.tarotOwner_ID_Dict.get(heroId, None)
	if heroTarotDict is None:
		return
	card = heroTarotDict.get(cardId)
	if not card:
		return
	
	del heroTarotDict[cardId]
	#修改位置
	card.pos = 0
	
	TM.tarotOwner_ID_Dict[TAROT_PACKAGE_ID][cardId] = card
	
	#重算属性
	hero.GetPropertyGather().ReSetRecountTarotFlag()
	role.CallBackFunction(backId, (heroId, cardId))

def OnTarotActiveByRMB(role, msg):
	'''
	高级占卜
	@param role:
	@param msg:
	'''
	if role.GetVIP() < 3:
		return
	backId, _ = msg

	TM = GetTarotMgr(role)
	if TM.PackageIsFull():
		return
	
	needRMB = EnumGameConfig.TarotActive_NeedUnBindRMB
	#版本判断
	if Environment.EnvIsNA():
		needRMB = EnumGameConfig.TarotActive_NeedUnBindRMB_NA
	elif Environment.EnvIsRU():
		needRMB = EnumGameConfig.TarotActive_NeedUnBindRMB_RU
	
	with TraTarot_ActiveByRMB:
		if role.ItemCnt(EnumGameConfig.TarotActive_ItemCoding) >= 1:
			role.DelItem(EnumGameConfig.TarotActive_ItemCoding, 1)
		else:
			if role.GetUnbindRMB() < needRMB:
				return
			role.DecUnbindRMB(needRMB)
		
		cardType = TarotConfig.TarotActiveRMB(role.GetLevel())
		
		cardId, cardGrade = TM.NewTarotCard(cardType)
		
		role.CallBackFunction(backId, (cardId, cardType))
		
		Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_TarotAd, 1))
		
		if cardGrade > 4:
			cRoleMgr.Msg(3, 0, GlobalPrompt.TarotGradeTips % (role.GetRoleName(), cardType, 1))
		
	#================下面为精彩活动的处理===================
	from Game.Activity.WonderfulAct import WonderfulActMgr, EnumWonderType
	WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_Inc_Tarot, role)
	if Environment.EnvIsNA():
		HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
		HalloweenNAMgr.TarotTimes(1)
	
def OnExchangeCard(role, msg):
	'''
	兑换一个塔罗牌
	@param role:
	@param msg:
	'''
	card_Type = msg
	if role.TarotPackageIsFull():
		return
	
	cfg = TarotConfig.TarotShop_Config_Dict.get(card_Type)
	if not cfg:
		return
	if role.GetLevel() < cfg.needLevel:
		return
	if role.GetI32(EnumInt32.TaortHP) < cfg.needTarotHP:
		return
	
	with TraTarot_ExchangeCard:
		role.DecI32(EnumInt32.TaortHP, cfg.needTarotHP)
		
		role.AddTarotCard(card_Type, 1)


def OnStrengthenTarotRing(role, msg):
	'''
	请求强化占卜光环
	@param role:
	@param msg:
	'''
	cnt = msg
	if role.GetLevel() < EnumGameConfig.TarotRingNeedLevel:
		return
	
	level = role.GetI8(EnumInt8.TarotRingLevel)
	
	if level >= EnumGameConfig.TarotRingMaxLevel:
		return
	
	exp = role.GetI32(EnumInt32.TarotRingExp)
	
	levelUpExp = TarotConfig.TarotRingLevelExp_Dict.get(level)
	
	needExp = levelUpExp - exp
	if not needExp:
		#出错了
		print "GE_EXC, error in StrengthenTarotRing levelUpExp - exp"
		return
	if cnt > needExp:
		cnt = needExp
	
	if role.ItemCnt(EnumGameConfig.TarotRingStrengthenItemCoding) < cnt:
		return
	
	with TraTarot_OnStrengthenTarotRing:
		role.DelItem(EnumGameConfig.TarotRingStrengthenItemCoding, cnt)
		
		if exp + cnt >= levelUpExp:
			role.SetI32(EnumInt32.TarotRingExp, 0)
			role.IncI8(EnumInt8.TarotRingLevel, 1)
			
			#重置所有的符合加成的卡的属性
			GetTarotMgr(role).ResetAllTarotProperty()
			
			#重算属性
			role.ResetAllTarotProperty()
		else:
			role.IncI32(EnumInt32.TarotRingExp, cnt)


def AfterLevelUp(role, param):
	#升级触发开启可装备格子
	openSize = TarotConfig.TarotLevelOpenSizeConfig_Dict.get(role.GetLevel())
	if not openSize:
		return
	
	role.SetI8(EnumInt8.TarotEquipmentPackageSize, openSize)


def InitRolePyObj(role, param):
	role.SetTempObj(EnumTempObj.enTarotMgr, TarotBase.TarotMgr(role))

def SyncRoleOtherData(role, param):
	#同步命魂数据
	role.SendObj(Tarot_S_AllData, role.GetObj(EnumObj.TarotCardDict))
	
def BeforeSaveRole(role, param):
	GetTarotMgr(role).SaveRoleTarot()
	
if "_HasLoad" not in dir():
	Event.RegEvent(Event.Eve_AfterLevelUp, AfterLevelUp)
	Event.RegEvent(Event.Eve_InitRolePyObj, InitRolePyObj)
	Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
	
	Event.RegEvent(Event.Eve_BeforeSaveRole, BeforeSaveRole)
	
	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Tarot_OnTarotZhanBu", "请求占卜"), OnTarotZhanBu)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Tarot_OneKeyZhanBu", "请求一键占卜"), OneKeyZhanBu)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Tarot_SuperZhanBu", "请求超级抽取"), SuperZhanBu)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Tarot_OnTarotActiveByRMB", "请求直接激活塔罗牌"), OnTarotActiveByRMB)
	
	if Environment.HasLogic:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Tarot_OnMixTarotCard", "请求融合两张塔罗牌"), MixTarotCard)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Tarot_OnSellTarot", "请求出售塔罗牌"), OnSellTarot)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Tarot_OnOneKeySell", "请求一键出售"), OnOneKeySell)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Tarot_OneKeyMixCard", "请求一键合成命魂"), OneKeyMixCard)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Tarot_OnLockTarot", "请求锁定命魂"), OnLockTarot)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Tarot_OnRolePutOnTarot", "请求角色佩戴塔罗牌"), OnRolePutOnTarot)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Tarot_OnHeroPutOnTarot", "请求英雄佩戴塔罗牌"), OnHeroPutOnTarot)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Tarot_OnTakeOffRoleTarot", "请求脱下主角的塔罗牌"), OnTakeOffRoleTarot)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Tarot_OnTakeOffHeroTarot", "请求脱下英雄的塔罗牌"), OnTakeOffHeroTarot)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Tarot_OnExchangeCard", "请求兑换塔罗牌"), OnExchangeCard)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Tarot_OnStrengthenTarotRing", "请求强化占卜光环"), OnStrengthenTarotRing)
		
		