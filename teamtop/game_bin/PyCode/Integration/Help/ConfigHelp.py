#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.Help.ConfigHelp")
#===============================================================================
# 配置辅助
#===============================================================================
from ComplexServer.Log import AutoLog
from Game.Fashion import FashionConfig



CodingNameCashe = None
PropNameCashe = None
#称号
TitleNameCashe = None

TarotCardCashe = None

TalentCardCache = None

#超值特惠礼包
TeHuiGoodsCache = None

def GetCodingName():
	global CodingNameCashe, PropNameCashe
	if CodingNameCashe is None:
		CodingNameCashe = {}
		PropNameCashe = {}
		from Game.Item import ItemConfig
		from Game.Hero import HeroConfig
		from Game.Marry import MarryConfig
		for cfg in ItemConfig.ItemConfig.ToClassType(False):
			CodingNameCashe[cfg.coding] = cfg.name
			PropNameCashe[cfg.coding] = cfg.name
		for cfg in ItemConfig.EquipmentConfig.ToClassType(False):
			CodingNameCashe[cfg.coding] = cfg.name
			PropNameCashe[cfg.coding] = cfg.name
			
		for cfg in ItemConfig.ArtifactConfig.ToClassType(False):
			CodingNameCashe[cfg.coding] = cfg.name
			PropNameCashe[cfg.coding] = cfg.name
		
		for cfg in ItemConfig.HallowsConfig.ToClassType(False):
			CodingNameCashe[cfg.coding] = cfg.name
			PropNameCashe[cfg.coding] = cfg.name
			
		for cfg in FashionConfig.FashionConfig.ToClassType(False):
			CodingNameCashe[cfg.coding] = cfg.name
			PropNameCashe[cfg.coding] = cfg.name
		
		for cfg in MarryConfig.RingConfig.ToClassType(False):
			CodingNameCashe[cfg.coding] = cfg.name
			PropNameCashe[cfg.coding] = cfg.name
		
		
		for cfg in HeroConfig.HeroBaseConfig.ToClassType(False):
			CodingNameCashe[cfg.heroNumber] = cfg.name
	return CodingNameCashe


def GetTarotNameCashe():
	global TarotCardCashe
	if TarotCardCashe is None:
		TarotCardCashe = {}
		from Game.Tarot import TarotConfig
		for cfg in TarotConfig.TarotCardConfig.ToClassType(False):
			TarotCardCashe[cfg.tType] = cfg.name
	return TarotCardCashe


def GetTalentCardCache():
	global TalentCardCache
	if TalentCardCache is None:
		TalentCardCache = {}
		from Game.TalentCard import TalentCardConfig
		for cfg in TalentCardConfig.TalentCardBase.ToClassType(False):
			TalentCardCache[cfg.cardId] = cfg.name
	return TalentCardCache

def GetTeHuiGoodsCache():
	global TeHuiGoodsCache
	if TeHuiGoodsCache is None:
		TeHuiGoodsCache = {}
		from Game.Activity.SuperPromption import SuperPromptionConfig
		for cfg in SuperPromptionConfig.SuperPromption_BaseConfig_Dict:
			TeHuiGoodsCache[cfg.goodsId] = cfg.goodsName
	return TeHuiGoodsCache		

def GetPropName():
	global CodingNameCashe, PropNameCashe
	if CodingNameCashe is None:
		CodingNameCashe = {}
		PropNameCashe = {}
		from Game.Item import ItemConfig
		from Game.Marry import MarryConfig
		for cfg in ItemConfig.ItemConfig.ToClassType(False):
			CodingNameCashe[cfg.coding] = cfg.name
			PropNameCashe[cfg.coding] = cfg.name
		for cfg in ItemConfig.EquipmentConfig.ToClassType(False):
			CodingNameCashe[cfg.coding] = cfg.name
			PropNameCashe[cfg.coding] = cfg.name
			
		for cfg in ItemConfig.ArtifactConfig.ToClassType(False):
			CodingNameCashe[cfg.coding] = cfg.name
			PropNameCashe[cfg.coding] = cfg.name
		
		for cfg in ItemConfig.HallowsConfig.ToClassType(False):
			CodingNameCashe[cfg.coding] = cfg.name
			PropNameCashe[cfg.coding] = cfg.name
		
		for cfg in FashionConfig.FashionConfig.ToClassType(False):
			CodingNameCashe[cfg.coding] = cfg.name
			PropNameCashe[cfg.coding] = cfg.name
		
		for cfg in MarryConfig.RingConfig.ToClassType(False):
			CodingNameCashe[cfg.coding] = cfg.name
			PropNameCashe[cfg.coding] = cfg.name
			
	return PropNameCashe

def GetFullNameByCoding(coding):
	name = GetCodingName().get(int(coding))
	if name:
		return "%s(%s)" % (coding, name)
	else:
		return str(coding)


def GetFullNameByTarotType(card_type):
	name = GetTarotNameCashe().get(int(card_type))
	if name:
		return "%s(%s)" % (card_type, name)
	else:
		return str(card_type)

def GetNameByTalentId(cardId):
	name = GetTalentCardCache().get(int(cardId))
	if name:
		return "%s(%s)" % (cardId, name)
	else:
		return str(cardId)

def GetNameByTeHuiGoodsId(goodsId):
	name = GetTeHuiGoodsCache().get(int(goodsId))
	if name:
		return "%s(%s)" % (goodsId, name)
	else:
		return str(goodsId)

def GetFullNameByTransaction(transaction):
	name = AutoLog.Transactions.get(transaction)
	if name:
		return "%s(%s)" % (transaction, name)
	else:
		return transaction

def GetFullNameByEvent(event):
	name = AutoLog.Events.get(event)
	if name:
		return "%s(%s)" % (event, name)
	else:
		return event

def HasItem(coding):
	return coding in GetPropName()

