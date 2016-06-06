#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.TalentCard.TalentCardOperate")
#===============================================================================
# 天赋卡操作
#===============================================================================
import cRoleMgr
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from Game.Role.Data import EnumTempObj, EnumObj
from Game.Role import Event
from Game.TalentCard import TalentCardBase, TalentCardConfig
from Game.Role.Mail import Mail

if "_HasLoad" not in dir():
	MIN_ROLE_LEVEL = 80	#天赋卡开启等级
	
	Talent_Del_Card = AutoMessage.AllotMessage("Talent_Del_Card", "删除一张卡片")
	Talent_Syn_AllData = AutoMessage.AllotMessage("Talent_Syn_AllData", "同步所有天赋卡数据")
	Talent_Syn_unLockData = AutoMessage.AllotMessage("Talent_Syn_unLockData", "同步所有天赋卡格子信息")
	#日志
	TalentCardCost = AutoLog.AutoTransaction("TalentCardCost", "天赋卡升级消耗")
	DecTalentCard = AutoLog.AutoTransaction("DecTalentCard", "天赋卡分解")
	ExchangeCard = AutoLog.AutoTransaction("ExchangeCard", "兑换天赋卡")
	UnLockCard = AutoLog.AutoTransaction("UnLockCard", "天赋卡解锁卡槽消耗")
	TalentPutOn = AutoLog.AutoTransaction("TalentPutOn", "装备天赋卡")


def AddTalentCard(role, cardType):
	'''增加一个天赋卡'''
	TalentCardMgr = role.GetTempObj(EnumTempObj.TalentCardMgr)
	if TalentCardMgr.PackageIsFull():
		Mail.SendMail(role.GetRoleID(), GlobalPrompt.PackageFullTitle, GlobalPrompt.Sender, GlobalPrompt.Content, talents = [cardType])
		return
	TalentCardMgr.NewTalentCard(cardType)


def OnExchangeCard(role, param):
	'''
	兑换天赋卡
	@param role:
	@param param:
	'''
	backId, cardtype = param
	if not cardtype:
		return
	cardCfg = TalentCardConfig.TALENT_BASE_DICT.get(cardtype)
	if not cardCfg:
		print "GE_EXC,can not find cardId=(%s) in TalentCardBase" % cardtype
		return
	alentCardMgr = role.GetTempObj(EnumTempObj.TalentCardMgr)
	#检查天赋卡背包是否已满
	if alentCardMgr.PackageIsFull():
		role.Msg(2, 0, GlobalPrompt.TalentIsFull_Tips)
		return
	needItem, needCnt = cardCfg.exchangeItem
	if role.ItemCnt(needItem) < needCnt:
		return
	
	with ExchangeCard:
		if role.DelItem(needItem, needCnt) < needCnt:
			return
		alentCardMgr.NewTalentCard(cardtype)
		role.CallBackFunction(backId, 1)
		role.Msg(2, 0, GlobalPrompt.Talent_Exchange_Suc % (cardtype, 1))

def OnRolePutOnCard(role, param):
	'''
	玩家装备天赋卡
	@param role:
	@param param:
	'''
	backId, cardId = param
	if role.GetLevel() < MIN_ROLE_LEVEL:
		return
	TalentCardMgr = role.GetTempObj(EnumTempObj.TalentCardMgr)
	#从天赋卡背包获取卡片
	puton_card = TalentCardMgr.GetCardByCardId(cardId)
	if not puton_card:
		return
	puton_type = puton_card.GetCardType()
	#获取该玩家装备的天赋卡
	onputed_dict = TalentCardMgr.GetOwnerDict(2)
	length = len(onputed_dict)
	if length >= 3:
		#已经装满了
		return
	UnlockDict = role.GetObj(EnumObj.TalentUnlockDict)
	unlock = UnlockDict.get(1, 0)
	if unlock + 1 < length:#卡槽未解锁
		return
	put_index = 0
	if onputed_dict:
		puted_indexs = []
		for _, card in onputed_dict.iteritems():
			if card.GetCardType() == puton_type:
				role.Msg(2, 0, GlobalPrompt.TalentSameTpye_Tips)
				#已经装了同类型的天赋卡
				return
			puted_indexs.append(card.pos)
		#取出可装备的格子
		unlock_list = [i+1 for i in range(unlock + 1)]
		for index in unlock_list:
			if index not in puted_indexs:
				put_index = index
				break
	else:
		put_index = 1
	if not put_index:
		return
	with TalentPutOn:
		TalentCardMgr.DelCardByCardId(cardId)
	
	onputed_dict[cardId] = puton_card
	#修改位置
	puton_card.pos = put_index
	#重置玩家天赋卡技能
	TalentCardMgr.ResetCardSkill(2)
	#重算属性
	role.GetPropertyGather().ReSetRecountTalentFlag()
	#装备的天赋卡为3件时
	if len(onputed_dict) >= 3:
		#重算套装属性
		TalentCardMgr.ResetSuitID(2)
		role.GetPropertyGather().ReSetRecountTalentSuitFlag()
	#回调
	role.CallBackFunction(backId, (cardId, put_index))

def OnHeroPutOnCard(role, param):
	'''
	英雄装备天赋卡
	@param role:
	@param param:
	'''
	backId, (heroId, cardId) = param

	hero = role.GetHero(heroId)
	if not hero : return
	if not hero.GetStationID(): return
	if hero.GetLevel() < MIN_ROLE_LEVEL:
		role.Msg(2, 0, GlobalPrompt.TalentNeedLevel)
		return
	TalentCardMgr = role.GetTempObj(EnumTempObj.TalentCardMgr)
	puton_card = TalentCardMgr.GetCardByCardId(cardId)
	if not puton_card:
		return
	#英雄不能装备
	if not puton_card.GetHeroCanPut():
		return
	puton_type = puton_card.GetCardType()
	#获取该英雄装备的天赋卡
	hero_dict = TalentCardMgr.GetOwnerDict(heroId)
	length = len(hero_dict)
	if len(hero_dict) >= 3:
		#已经装满了
		return
	UnlockDict = role.GetObj(EnumObj.TalentUnlockDict)
	unlock = UnlockDict.get(heroId, 0)
	if unlock + 1 < length:#卡槽未解锁
		return
	put_index = 0
	if hero_dict:
		puted_list = []
		for _, card in hero_dict.iteritems():
			if card.GetCardType() == puton_type:
				role.Msg(2, 0, GlobalPrompt.TalentSameTpye_Tips)
				return
			puted_list.append(card.pos)
		#获取可装备的格子
		unlock_list = [i+1 for i in range(unlock+1)]
		for index in unlock_list:
			if index not in puted_list:
				put_index = index
				break
	else:
		put_index = 1
	if not put_index:
		return
	with TalentPutOn:
		TalentCardMgr.DelCardByCardId(cardId)
	hero_dict[cardId] = puton_card
	#修改位置
	puton_card.pos = put_index
	#重置改英雄的天赋卡技能
	TalentCardMgr.ResetCardSkill(heroId)
	#重算属性
	hero.GetPropertyGather().ReSetRecountTalentFlag()
	if len(hero_dict) >= 3:
		#重算套装属性
		TalentCardMgr.ResetSuitID(heroId)
		hero.GetPropertyGather().ReSetRecountTalentSuitFlag()
	#回调
	role.CallBackFunction(backId, (heroId, cardId ,put_index))

def OnRoleTakeOffCard(role, param):
	'''
	玩家请求下天赋卡
	@param role:
	@param param:
	'''
	backId, cardId = param
	
	TalentCardMgr = role.GetTempObj(EnumTempObj.TalentCardMgr)
	#天赋卡背包满了
	if TalentCardMgr.PackageIsFull():
		role.Msg(2, 0, GlobalPrompt.TalentIsFull_Tips)
		return
	#获取该玩家装备的天赋卡
	roleTalentDict = TalentCardMgr.GetOwnerDict(2)
	card = roleTalentDict.get(cardId)
	if not card:
		return
	del roleTalentDict[cardId]
	#修改位置
	card.pos = 0
	TalentCardMgr.card_owner_dict[1][cardId] = card
	#重置玩家天赋卡技能
	TalentCardMgr.ResetCardSkill(2)
	#重算属性
	role.GetPropertyGather().ReSetRecountTalentFlag()
	if len(roleTalentDict) >= 2:
		#重算套装属性
		TalentCardMgr.ResetSuitID(2)
		role.GetPropertyGather().ReSetRecountTalentSuitFlag()
	role.CallBackFunction(backId, cardId)
	
def OnHeroTakeOffCard(role, param):
	'''
	英雄请求下天赋卡
	@param role:
	@param param:
	'''
	backId, (cardId, heroId) = param
	
	hero = role.GetHero(heroId)
	if not hero : return
	if not hero.GetStationID(): return
	
	TalentCardMgr = role.GetTempObj(EnumTempObj.TalentCardMgr)	
	if TalentCardMgr.PackageIsFull():
		role.Msg(2, 0, GlobalPrompt.TalentIsFull_Tips)
		return
	#获取该英雄装备的天赋卡
	HeroTalentDict = TalentCardMgr.GetOwnerDict(heroId)
	if not HeroTalentDict:
		return
	card = HeroTalentDict.get(cardId)
	if not card:
		return
	del HeroTalentDict[cardId]
	#修改位置
	card.pos = 0
	TalentCardMgr.card_owner_dict[1][cardId] = card
	#重置天赋卡技能
	TalentCardMgr.ResetCardSkill(heroId)
	#重算属性
	hero.GetPropertyGather().ReSetRecountTalentFlag()
	if len(HeroTalentDict) >= 2:
		#重算套装属性
		TalentCardMgr.ResetSuitID(heroId)
		hero.GetPropertyGather().ReSetRecountTalentSuitFlag()
	role.CallBackFunction(backId, (heroId, cardId))
	
def OnLevelUpCard(role, param):
	'''
	玩家升级天赋卡
	@param role:
	@param param:
	'''
	backId, (ownerId, cardId) = param #这里做了约定，ownerId 1为背包， 2为玩家身上， heroID为英雄身上
	if role.GetLevel() < MIN_ROLE_LEVEL:
		return
	TalentCardMgr = role.GetTempObj(EnumTempObj.TalentCardMgr)
	ownerDict = TalentCardMgr.GetOwnerDict(ownerId)
	if not ownerDict:
		return
	owner = None
	if ownerId > 2:#英雄
		owner = role.GetHero(ownerId)
		if not owner : return
		if not owner.GetStationID(): return
	elif ownerId == 2:
		owner = role
	Levelup_card = TalentCardMgr.GetOwnerCard(ownerId, cardId)
	if not Levelup_card:
		return
	#该卡是否能升级
	canState = Levelup_card.CanCardLevelup()
	if not canState : return
	#根据等级读取配置表
	nowLevel = Levelup_card.cardLevel
	key = (Levelup_card.cfgId, nowLevel + 1)
	expCfg = TalentCardConfig.TALENT_LEVEL_EXP_DICT.get(key)
	if not expCfg:
		print "GE_EXC,can not find cardType(%s) and level(%s) in TALENT_LEVEL_EXP_DICT" % (Levelup_card.cfgId, nowLevel + 1)
		return
	delCoding, delNum = expCfg.starNum
	if role.ItemCnt(delCoding) < delNum:
		return

	DelList = []
	starNum = 0
	if expCfg.cardNum:
		for cardData in expCfg.cardNum:
			cardType, starNum = cardData
			cardList = TalentCardMgr.GetPackageNumForType(cardType)
			if len(cardList) < starNum:
				return
			DelList += cardList[0:starNum]
	with TalentCardCost:
		if role.DelItem(delCoding, delNum) < delNum:
			return
		if DelList:
			for delId in DelList:
				TalentCardMgr.DelCardByCardId(delId)
				role.SendObj(Talent_Del_Card, delId)
		Levelup_card.CardLevelUp()
		role.Msg(2, 0, GlobalPrompt.Talent_LevelUp % (nowLevel + 1))
	if owner:
		#重置天赋卡技能
		TalentCardMgr.ResetCardSkill(ownerId)
		owner.GetPropertyGather().ReSetRecountTalentFlag()
		if len(ownerDict) == 3:
			#重置天赋卡套装属性
			TalentCardMgr.ResetSuitID(ownerId)
			owner.GetPropertyGather().ReSetRecountTalentSuitFlag()
		
	#回调
	role.CallBackFunction(backId, (ownerId, cardId, Levelup_card.cardLevel))

def OnDecCard(role, param):
	'''
	玩家分解天赋卡
	@param role:
	@param param:
	'''
	backId, cardId = param
	if role.GetLevel() < MIN_ROLE_LEVEL:
		return
	TalentCardMgr = role.GetTempObj(EnumTempObj.TalentCardMgr)
#	if TalentCardMgr.PackageIsFull():
#		return
	#只分解背包中的天赋卡
	dec_card = TalentCardMgr.GetCardByCardId(cardId)
	if not dec_card:
		return
	key = (dec_card.cfgId, dec_card.cardLevel)
	cfg = TalentCardConfig.TALENT_DEC_DICT.get(key)
	if not cfg:
		print "GE_EXC,can not find cardType(%s) and cardLevel(%s) in OnDecCard" % (dec_card.cfgId, dec_card.cardLevel)
		return
	if role.GetUnbindRMB() < cfg.UnbindRMB:
		return
	AddList = {}
	totalNum = 0
	if cfg.backcard:
		for cardData in cfg.backcard:
			backtype, backnum = cardData
			AddList[backtype] = backnum
			totalNum += backnum

		if TalentCardMgr.GetEmptySize() < totalNum:
			role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)	
			return
	with DecTalentCard:
		tips = ""
		TalentCardMgr.DelCardByCardId(cardId)
		tips += GlobalPrompt.Talent_Dec_Suc % (dec_card.cfgId, 1)
		if cfg.UnbindRMB:
			role.DecUnbindRMB(cfg.UnbindRMB)
		if cfg.backstar:
			backCoding, backCnt = cfg.backstar
			role.AddItem(backCoding, backCnt)
			tips += GlobalPrompt.Item_Tips % (backCoding, backCnt)
		if AddList:
			for backtype, cnt in AddList.iteritems():
				for _ in range(cnt):
					TalentCardMgr.NewTalentCard(backtype)
				tips += GlobalPrompt.Talent_Tips % (backtype, cnt)
		role.Msg(2, 0, tips)
	#回调
	role.CallBackFunction(backId, cardId)

def OnUnlockCard(role, param):
	'''
	玩家请求解锁卡槽
	@param role:
	@param param:
	'''
	heroId = param
	UnlockDict = role.GetObj(EnumObj.TalentUnlockDict)
	unlock = 0
	if 1 == heroId:#主角
		unlock = UnlockDict.get(1, 0)
	else:
		hero = role.GetHero(heroId)
		if not hero : return
		if not hero.GetStationID(): return
		unlock = UnlockDict.get(heroId, 0)
	if unlock >= 2:#已经全部解锁
		return 
	unlockCfg = TalentCardConfig.TALENT_UNLOCK_DICT.get(unlock+1)
	if not unlockCfg:
		print "GE_EXC,can not find unlockId(%s) in OnUnlockCard" % (unlock+1)
		return
	needItem, needCnt = unlockCfg.needItem
	
	if role.ItemCnt(needItem) < needCnt:
		return
	with UnLockCard:
		if role.DelItem(needItem, needCnt) < needCnt:
			return
		UnlockDict[heroId] = unlock+1
		role.Msg(2, 0, GlobalPrompt.Talent_Unlock_Suc)
	#回调
	role.SendObj(Talent_Syn_unLockData, role.GetObj(EnumObj.TalentUnlockDict))

def SyncRoleOtherData(role, param):
	role.SendObj(Talent_Syn_AllData, role.GetObj(EnumObj.TalentCardDict))
	role.SendObj(Talent_Syn_unLockData, role.GetObj(EnumObj.TalentUnlockDict))

def BeforeSaveRole(role, param):
	TalentCardMgr = role.GetTempObj(EnumTempObj.TalentCardMgr)
	TalentCardMgr.SaveRoleTalent()
	
def InitRolePyObj(role, param):
	role.SetTempObj(EnumTempObj.TalentCardMgr, TalentCardBase.TalentCardMgr(role))

if "_HasLoad" not in dir():
	#事件
	Event.RegEvent(Event.Eve_InitRolePyObj, InitRolePyObj)
	Event.RegEvent(Event.Eve_BeforeSaveRole, BeforeSaveRole)
	Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
	#消息
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Exchange_Card", "兑换天赋卡"), OnExchangeCard)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_PutOn_Card", "玩家装备天赋卡"), OnRolePutOnCard)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Hero_PutOn_Card", "英雄装备天赋卡"), OnHeroPutOnCard)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Takeoff_Card", "玩家下天赋卡"), OnRoleTakeOffCard)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Hero_Takeoff_Card", "英雄下天赋卡"), OnHeroTakeOffCard)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_LevelUp_Card", "玩家升级天赋卡"), OnLevelUpCard)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Dec_Card", "玩家分解天赋卡"), OnDecCard)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_UnLock_Card", "玩家请求解锁卡槽"), OnUnlockCard)
	