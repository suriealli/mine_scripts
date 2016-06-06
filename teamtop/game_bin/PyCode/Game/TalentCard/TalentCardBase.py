#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.TalentCard.TalentCardBase")
#===============================================================================
# 星座天赋卡数据
#===============================================================================
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Game.Role.Data import EnumObj, EnumInt32
from Game.TalentCard import TalentCardConfig

TALENT_PACKAGE_SIZE = 144	#背包格子数

#星座天赋卡存储格式key
CARD_TYPE = 0
CARD_LEVEL = 1
CARD_POS = 2
CARD_SKILL = 3
CARD_SKILL_ZDL = 4

if "_HasLoad" not in dir():
	Talent_Syn_NewCard = AutoMessage.AllotMessage("Talent_Syn_NewCard", "同步新的天赋卡")
	
class TalentCard(object):
	def __init__(self, role, cardId, cardDict):
		self.role		= role
		self.cardId		= cardId
		self.cfgId		= cardDict.get(CARD_TYPE)
		self.cardLevel	= cardDict.get(CARD_LEVEL)
		self.pos		= cardDict.get(CARD_POS)
		self.skill		= cardDict.get(CARD_SKILL)
		self.skillzdl	= cardDict.get(CARD_SKILL_ZDL)
		self.AfterCreate()
	
	def AfterCreate(self):
		self.card_cfg = TalentCardConfig.TALENT_BASE_DICT.get(self.cfgId)
		if not self.card_cfg:
			print "GE_EXC,TalentCard AfterCreate can not find cfgId(%s)" % self.cfgId
			return
		self.real_property_value = {}
				
	def GetCardGrade(self):
		return self.card_cfg.grade

	def GetCardType(self):
		return self.card_cfg.cardtype
	
	def GetCardPos(self):
		return self.pos
		
	def GetCardLevel(self):
		return self.cardLevel
	
	def GetCardSuitId(self):
		return self.card_cfg.suitId
	
	def GetCardMaxLevel(self):
		return self.card_cfg.maxlevel
	
	def GetCardSkill(self):
		return self.skill
	
	def GetHeroCanPut(self):
		return self.card_cfg.heroput
	
	def CanCardLevelup(self):
		if self.cardLevel >= self.card_cfg.maxlevel:
			return False
		return True
	
	def CardLevelUp(self):
		'''
		给天赋卡升级
		'''
		if self.cardLevel >= self.card_cfg.maxlevel:
			return
		self.cardLevel += 1
		self.skill = self.card_cfg.cardskill[self.cardLevel - 1]
		self.skillzdl = self.card_cfg.skill_zdl[self.cardLevel - 1]
		self.ResetPropertyValue()
			
	def ResetPropertyValue(self):
		self.real_property_value = {}
		
	def GetPropertyValue(self):
		if self.real_property_value:
			return self.real_property_value
		if self.card_cfg.pt1 and self.card_cfg.pv1:
			self.real_property_value[self.card_cfg.pt1] = self.card_cfg.pv1[self.cardLevel - 1]
		if self.card_cfg.pt2 and self.card_cfg.pv2:
			self.real_property_value[self.card_cfg.pt2] = self.card_cfg.pv2[self.cardLevel - 1]
		return self.real_property_value

	def GetSaveData(self):
		return {CARD_TYPE:self.cfgId, CARD_LEVEL:self.cardLevel, CARD_POS:self.pos, \
				CARD_SKILL:self.skill, CARD_SKILL_ZDL:self.skillzdl}
	
class TalentCardMgr(object):
	
	def __init__(self, role):
		self.role = role
		self.suit_owner_pro_dict = {}	#记录天赋卡的套装属性
		self.suit_owner_skill_dict = {}	#记录天赋卡的套装技能
		self.suit_owner_zdl = {}		#记录天赋卡套装技能战斗力
		self.owner_skill_dict = {}		#记录天赋卡技能
		self.owner_skill_zdl = {}		#记录天赋卡技能战斗力
		self.card_owner_dict = {}	# 1 --> {ID --> card}#背包
									# 2 --> {ID --> card}#角色
									# heroId --> {ID --> card}#英雄
		try:
			# 1 --> {ID --> {0:type, 1:level, 2:pos, 3:skill}}
			# 2 --> {ID --> {0:type, 1:level, 2:pos, 3:skill}}
			# heroId --> {ID --> {0:type, 1:level, 2:pos, 3:skill}}
			TalentCardDict = role.GetObj(EnumObj.TalentCardDict)
			if TalentCardDict == {}:
				role.SetObj(EnumObj.TalentCardDict, {1 : {}, 2 : {}})
				TalentCardDict = role.GetObj(EnumObj.TalentCardDict)
			CARD_OWNER_DICT = self.card_owner_dict
			for packageId, cDict in TalentCardDict.iteritems():
				CARD_OWNER_DICT[packageId] = ONE_CARD_INFO = {}
				for cardId, cardInfo in cDict.iteritems():
					ONE_CARD_INFO[cardId] = TalentCard(role, cardId, cardInfo)
		except:
			print "GE_EXC, TalentCardMgr init error"
			

	def SaveRoleTalent(self):
		#持久化天赋卡数据
		tempDict = {}
		for pId, ttDict in self.card_owner_dict.iteritems():
			if pId > 2 and not ttDict:
				continue
			temp_ID_D = tempDict[pId] = {}
			for tId, tarlent_card in ttDict.iteritems():
				temp_ID_D[tId] = tarlent_card.GetSaveData()
		self.role.SetObj(EnumObj.TalentCardDict, tempDict)
		
	def GetPackageNumForType(self, ctype):
		'''
		在天赋背包中查找同类型且为1级的天赋卡数量
		'''
		cardDict = self.card_owner_dict.get(1)
		card_list = []
		for cardId, cardObj in cardDict.iteritems():
			if cardObj.cfgId == ctype and cardObj.GetCardLevel() == 1:
				card_list.append(cardId)
		return card_list
	
	def DelCardByCardId(self, cardId):
		#从背包删除天赋卡
		cardType = self.card_owner_dict[1].get(cardId).cfgId
		del self.card_owner_dict[1][cardId]
		AutoLog.LogObj(self.role.GetRoleID(), AutoLog.eveDelTalentCard, cardId, cardType, 1, None, None)
	
	def GetCardByCardId(self, cardId):
		#从背包获取天赋卡
		return self.card_owner_dict[1].get(cardId)
	
	def GetOwnerCard(self, ownerId, cardId):
		return self.card_owner_dict[ownerId].get(cardId)

	def GetOwnerDict(self, ownerId):
		#获取拥有者的天赋卡
		return self.card_owner_dict.setdefault(ownerId, {})

	def NewTalentCard(self, cardType):
		#构建个天赋卡对象
		card_cfg = TalentCardConfig.TALENT_BASE_DICT.get(cardType)
		if not card_cfg:
			print "GE_EXC,can not find cardId(%s) in NewTalentCards" % card_cfg
			return
		allotId = self.role.GetI32(EnumInt32.TalentAllotId) + 1
		self.role.IncI32(EnumInt32.TalentAllotId, 1)
		cardDict = {CARD_TYPE : cardType, CARD_LEVEL : 1, CARD_POS : 0, \
				CARD_SKILL:card_cfg.cardskill[0], CARD_SKILL_ZDL:card_cfg.skill_zdl[0]}
		self.card_owner_dict[1][allotId] = TalentCard(self.role, allotId, cardDict)
		AutoLog.LogObj(self.role.GetRoleID(), AutoLog.eveAddTalentCard, allotId, cardType, 1, None, None)
		self.role.SendObj(Talent_Syn_NewCard, (allotId, cardType, 1, 0))
		return allotId

	def PackageIsFull(self):
		#检查背包是否已满
		return len(self.card_owner_dict[1]) >= TALENT_PACKAGE_SIZE
	
	def GetEmptySize(self):
		return TALENT_PACKAGE_SIZE - len(self.card_owner_dict[1])

	def ResetCardSkill(self, ownerId):
		#重置天赋卡技能(穿，脱，升级触发)
		self.owner_skill_dict[ownerId] = []
		self.owner_skill_zdl[ownerId] = 0
		
	def GetCardZDL(self, ownerId):
		#获取拥有者的技能战斗力
		ownerDict = self.card_owner_dict.get(ownerId, {})
		if not ownerDict:
			return 0
		if not self.owner_skill_zdl.get(ownerId):
			self.owner_skill_zdl[ownerId] = 0
			for _, card in ownerDict.iteritems():
				self.owner_skill_zdl[ownerId] = self.owner_skill_zdl.get(ownerId, 0) + card.skillzdl
		skill_zdl = self.owner_skill_zdl.get(ownerId, 0)
		suit_zdl = self.suit_owner_zdl.get(ownerId, 0)
		return skill_zdl + suit_zdl

	def GetCardSkill(self, ownerId):
		#通过拥有者Id获取已激活的技能
		ownerDict = self.card_owner_dict.get(ownerId, {})
		if not ownerDict:
			return []
		if not self.owner_skill_dict.get(ownerId):
			self.owner_skill_dict[ownerId] = []
			for _, card in ownerDict.iteritems():
				self.owner_skill_dict[ownerId].append(card.skill)
		owner_skill = []
		if self.owner_skill_dict[ownerId]:
			owner_skill += self.owner_skill_dict[ownerId]
		suit_skill = self.suit_owner_skill_dict.get(ownerId)
		if suit_skill:
			owner_skill += suit_skill
		return owner_skill

	def ResetSuitID(self, ownerId):
		#重置拥有者的套装属性、技能和技能战斗力
		if ownerId in self.suit_owner_pro_dict:
			self.suit_owner_pro_dict[ownerId] = {}
		if ownerId in self.suit_owner_skill_dict:
			del self.suit_owner_skill_dict[ownerId]
		if ownerId in self.suit_owner_zdl:
			self.suit_owner_zdl[ownerId] = 0
		
	def GetSuitPro(self, ownerId):
		#获取套装
		if self.suit_owner_pro_dict.get(ownerId):
			return self.suit_owner_pro_dict.get(ownerId)
		owner_card_dict = self.card_owner_dict.get(ownerId, {})
		if len(owner_card_dict) < 3:
			return {}
		min_level = 10
		suitDict = {}
		Cardgrade = 0
		for _, card in owner_card_dict.iteritems():
			if card.cardLevel < min_level:
				min_level = card.cardLevel
			if card.GetCardGrade() >= 2:
				Cardgrade += 1
			suitIds = card.GetCardSuitId()
			for suitId in suitIds:
				suitDict[suitId] = suitDict.get(suitId, 0) + 1
		SUIT_CFG = TalentCardConfig.TALENT_SUIT_DICT.get
		for suitId, suitNum in suitDict.iteritems():
			suitcfg = SUIT_CFG(suitId)
			if not suitcfg:
				return {}
			if suitNum >= suitcfg.cnt:
				if ownerId not in self.suit_owner_pro_dict:
					self.suit_owner_pro_dict[ownerId] = {}
				PRO_DICT = self.suit_owner_pro_dict[ownerId]
				if suitcfg.pt1 and suitcfg.pv1:
					pv1 = suitcfg.pv1[min_level - 1]
					if Cardgrade == 3:
						pv1 = suitcfg.pv1[min_level - 1 + 5]
					PRO_DICT[suitcfg.pt1] = PRO_DICT.get(suitcfg.pt1, 0) + pv1
				if suitcfg.pt2 and suitcfg.pv2:
					pv2 = suitcfg.pv2[min_level - 1]
					if Cardgrade == 3:
						pv2 = suitcfg.pv2[min_level - 1 + 5]
					PRO_DICT[suitcfg.pt2] = PRO_DICT.get(suitcfg.pt2, 0) + pv2
				self.suit_owner_skill_dict[ownerId] = []
				if Cardgrade == 3:#3张都是橙色卡
					self.suit_owner_skill_dict[ownerId].append(suitcfg.skill[min_level - 1 + 5])
					self.suit_owner_zdl[ownerId] = suitcfg.skillzdl[min_level - 1 + 5]
				else:
					self.suit_owner_skill_dict[ownerId].append(suitcfg.skill[min_level - 1])
					self.suit_owner_zdl[ownerId] = suitcfg.skillzdl[min_level - 1]
		return self.suit_owner_pro_dict.get(ownerId, {})
	#==============以下用于获取角色查看的数据=================
	def GetRoleViewData(self):
		#获取角色查看的数据
		cd = {}
		for card in self.GetOwnerDict(2).itervalues():
			cd[card.pos] = [card.cardLevel, card.cfgId]
		return cd 

	def GetHeroViewData(self, heroId):
		#获取英雄查看的数据
		if heroId not in self.card_owner_dict:
			return {}
		cd = {}
		for card in self.GetOwnerDict(heroId).itervalues():
			cd[card.pos] = [card.cardLevel, card.cfgId]
		return cd 
	
		