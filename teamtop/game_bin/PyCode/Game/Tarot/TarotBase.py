#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Tarot.TarotBase")
#===============================================================================
# 塔罗牌数据模块
#===============================================================================
import traceback
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, EnumKick
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumObj, EnumInt32, EnumInt8, EnumTempObj
from Game.Tarot import TarotConfig

KR = "塔罗牌数据异常"

##################################################################################
#命魂存储数据key
CardTypeKey = 0#类型
CardLevelKey = 1#等级
CardExpKey = 2#经验
CardLockKey = 3#是否锁定
CardPosKey = 4# 命魂位置
##################################################################################

##################################################################################

TAROT_PACKAGE_SIZE = 30 #背包大小
#背包ID(程序用)
TAROT_PACKAGE_ID = 1
TAROT_ROLE_PACKAGE_ID = 2

#消点，获取配置
TTD_GET = TarotConfig.TarotCardConfig_Dict.get
TTE_GET = TarotConfig.TarotCardGradeLevelExp_Dict.get
TTLU_GET = TarotConfig.TarotCardLevelUpExp_Dict.get

if "_HasLoad" not in dir():
	Tarot_S_Update_Level_Exp = AutoMessage.AllotMessage("Tarot_S_Update_Level_Exp", "更新一个塔罗牌等级和经验(id,level, exp)")


#塔罗牌类
class TarotCard(object):
	def __init__(self, role, cardId, cardDataDict):
		self.role = role
		self.cardId = cardId
		
		self.cardType = cardDataDict[CardTypeKey]
		self.level = cardDataDict[CardLevelKey]
		self.exp = cardDataDict[CardExpKey]
		
		self.isLock = cardDataDict[CardLockKey]#1 锁定 ， 0 非锁定
		
		self.pos = cardDataDict.get(CardPosKey, 0)#位置 1,2,3,4,5,6,7,8
		self.AfterCreate()
		
		
	
	def AfterCreate(self):
		#初始化一些 配置
		self.card_cfg = TTD_GET(self.cardType)
		assert self.card_cfg is not None
		
		#配置表中的属性值是按照等级为下标填写的一个列表
		#self.real_property_value = self.card_cfg.pv[self.level - 1]
		#第一个属性
		self.real_property_value = 0
		#第二个属性
		self.real_property_value_2 = 0
		
		#缓存品阶
		self.grade = self.card_cfg.grade
		
		self.expCfg_Dict = None
		
	def GetGrade(self):
		#获取品阶(2 绿, 3 蓝, 4 紫色, 5 黄, 6红)
		return self.grade
	
	def IsLock(self):
		return self.isLock == 1
	
	def IsLog(self):
		#是否记录日志
		return self.card_cfg.isLog
	
	def CanEquitment(self):
		return self.card_cfg.canEquitment
	
	def CanMix(self):
		return self.card_cfg.canMix
	
	def CanBeMix(self):
		return self.card_cfg.canBeMix
	
	def OneKeyMix(self):
		return self.card_cfg.oneKeyMix
	
	
	def GetMixExp(self):
		#获取被融合是加的经验
		if self.level <= 1:
			return self.exp + self.card_cfg.baseExp
		else:
			gradeLevelExp = self.exp + self.card_cfg.baseExp
			gd = TTE_GET(self.card_cfg.grade)
			if not gd:
				return gradeLevelExp
			return gradeLevelExp + gd.get(self.level, 0)
	
	
	def GetSaveData(self):
		#获取持久化数据
		return {CardTypeKey : self.cardType, CardLevelKey : self.level, CardExpKey : self.exp, CardLockKey:self.isLock, CardPosKey : self.pos}
	
	def GetSyncData(self):
		#获取同步数据
		return {self.cardId : {CardTypeKey : self.cardType, CardLevelKey : self.level, CardExpKey : self.exp, CardLockKey:self.isLock, CardPosKey : self.pos}}
	
	
	def GetLevelUpExpDict(self):
		if self.expCfg_Dict is None:
			self.expCfg_Dict = TTLU_GET(self.grade)
		return self.expCfg_Dict
	
	def IncCardExp(self, exp):
		self.exp += exp
		#升级逻辑
		nowTotalExp = self.exp
		nowLevel = self.level
		if nowLevel >= EnumGameConfig.TarotCard_Max_Level:
			return
		newLevel = nowLevel
		expCfg_Dict = self.GetLevelUpExpDict()
		EXPDICT_GET = expCfg_Dict.get
		levelUp_exp = EXPDICT_GET(nowLevel)
		if not levelUp_exp:
			return
	
		for _ in xrange(10):
			if nowTotalExp < levelUp_exp:
				break
			nowTotalExp -= levelUp_exp
			newLevel += 1
			levelUp_exp = EXPDICT_GET(newLevel)
			if not levelUp_exp:
				break
			
		if newLevel > nowLevel:
			self.level = newLevel
			self.exp = nowTotalExp
			
			self.real_property_value = 0
			self.real_property_value_2 = 0
			
			#记录日志
			AutoLog.LogBase(self.role.GetRoleID(), AutoLog.eveTarot_LevelUp, (self.cardId, newLevel, nowLevel))
			
			#版本判断
			if Environment.EnvIsNA():
				#开服活动
				kaifuActMgr = self.role.GetTempObj(EnumTempObj.KaiFuActMgr)
				if self.GetGrade() >= 4:
					kaifuActMgr.tarot_level(newLevel)
						
		#更新等级
		self.role.SendObj(Tarot_S_Update_Level_Exp, (self.cardId, self.level, self.exp))
	
	def IncCardExpEx(self, exp):
		#这里没有同步客户端最新经验, 仅用于超级抽取
		
		self.exp += exp
		#升级逻辑
		nowTotalExp = self.exp
		nowLevel = self.level
		if nowLevel >= EnumGameConfig.TarotCard_Max_Level:
			return
		newLevel = nowLevel
		expCfg_Dict = self.GetLevelUpExpDict()
		EXPDICT_GET = expCfg_Dict.get
		levelUp_exp = EXPDICT_GET(nowLevel)
		if not levelUp_exp:
			return
	
		for _ in xrange(10):
			if nowTotalExp < levelUp_exp:
				break
			nowTotalExp -= levelUp_exp
			newLevel += 1
			levelUp_exp = EXPDICT_GET(newLevel)
			if not levelUp_exp:
				break
			
		if newLevel > nowLevel:
			self.level = newLevel
			self.exp = nowTotalExp
			
			self.real_property_value = 0
			self.real_property_value_2 = 0
			
			#记录日志
			AutoLog.LogBase(self.role.GetRoleID(), AutoLog.eveTarot_LevelUp, (self.cardId, newLevel, nowLevel))
			
			#版本判断
			if Environment.EnvIsNA():
				#开服活动
				kaifuActMgr = self.role.GetTempObj(EnumTempObj.KaiFuActMgr)
				if self.GetGrade() >= 4:
					kaifuActMgr.tarot_level(newLevel)
	
	def ResetProperty(self):
		#重置属性，等待下一次计算的时候触发重新生成
		if not self.card_cfg.canRing:
			return
		self.real_property_value = 0
		self.real_property_value_2 = 0
	
	def GetPropertyValue(self):
		#获取第一个属性
		if self.real_property_value:
			return self.real_property_value
		
		self.real_property_value = self.card_cfg.pv[self.level - 1]
		if not self.card_cfg.canRing:
			return self.real_property_value
		ringLevel = self.role.GetI8(EnumInt8.TarotRingLevel)
		if not ringLevel:
			return self.real_property_value
		
		coef_cfg = TarotConfig.TarotRingConfig_Dict.get(ringLevel)
		if not coef_cfg:
			return self.real_property_value
		
		coef = coef_cfg.Get_Coef(self.grade, self.level)
		self.real_property_value = int(self.real_property_value *(10000.0 + coef) / 10000.0)
		
		return self.real_property_value
	
	def GetPropertyValue_2(self):
		#获取第二个属性
		if self.real_property_value_2:
			return self.real_property_value_2
		
		self.real_property_value_2 = self.card_cfg.pv2[self.level - 1]
		if not self.card_cfg.canRing:
			return self.real_property_value_2
		ringLevel = self.role.GetI8(EnumInt8.TarotRingLevel)
		if not ringLevel:
			return self.real_property_value_2
		
		coef_cfg = TarotConfig.TarotRingConfig_Dict.get(ringLevel)
		if not coef_cfg:
			return self.real_property_value_2
		
		coef = coef_cfg.Get_Coef(self.grade, self.level)
		self.real_property_value_2 = int(self.real_property_value_2 *(10000.0 + coef) / 10000.0)
		
		return self.real_property_value_2


#管理器
class TarotMgr(object):
	def __init__(self, role):
		self.role = role
		self.tarotOwner_ID_Dict = {}# 1 --> {ID --> TarotCard}#背包
									# 2 --> {ID --> TarotCard}#角色
									# heroId --> {ID --> TarotCard}#英雄
		try:
			#全部塔罗牌数据 EnumObj.TarotCardDict
			# 1 --> {ID --> {0:type, 1:level, 2:exp, 3:islock}}
			# 2 --> {ID --> {0:type, 1:level, 2:exp, 3:islock}}
			# heroId --> {ID --> {0:type, 1:level, 2:exp, 3:islock}}
			tempTarotDict = role.GetObj(EnumObj.TarotCardDict)
			#消点
			SELF_T_OID_DICT = self.tarotOwner_ID_Dict
			#数据库的持久化数据生成TarotCard对象
			for packageId, ttDict in tempTarotDict.iteritems():
				SELF_T_OID_DICT[packageId] = temp_ID_D = {}
				for cardId, card_Data_dict in ttDict.iteritems():
					temp_ID_D[cardId] = TarotCard(role, cardId, card_Data_dict)
		except:
			#有异常，踢玩家，不保存数据
			traceback.print_exc()
			self.role.Kick(False, EnumKick.DataError_Tarot)

	def SaveRoleTarot(self):
		#持久化塔罗牌数据
		tempDict = {}
		for pId, ttDict in self.tarotOwner_ID_Dict.iteritems():
			if pId > 2 and not ttDict:
				continue
			temp_ID_D = tempDict[pId] = {}
			for tId, tarot_card in ttDict.iteritems():
				temp_ID_D[tId] = tarot_card.GetSaveData()
				
		self.role.SetObj(EnumObj.TarotCardDict, tempDict)
	
	def PackageIsFull(self):
		#背包是否已经满了
		return len(self.tarotOwner_ID_Dict[TAROT_PACKAGE_ID]) >= TAROT_PACKAGE_SIZE
	
	def PackageEmptySize(self):
		#空格子
		return TAROT_PACKAGE_SIZE - len(self.tarotOwner_ID_Dict[TAROT_PACKAGE_ID])
	
	
	def RoleTarotIdFull(self):
		#角色已经装备的卡牌满
		return False

	def GetPackageCard(self, cardId):
		return self.tarotOwner_ID_Dict[TAROT_PACKAGE_ID].get(cardId)
	
	def DelPackageCard(self, cardId):
		tc = self.tarotOwner_ID_Dict[TAROT_PACKAGE_ID][cardId]
		del self.tarotOwner_ID_Dict[TAROT_PACKAGE_ID][cardId]
		if tc.IsLog():
			#写日志
			AutoLog.LogObj(self.role.GetRoleID(), AutoLog.eveTarot_DelCard, tc.cardId, tc.cardType, 1, (tc.level, tc.exp), None)
		
	def NewTarotCard(self, card_Type):
		#构建一个塔罗牌对象
		#分配ID
		alloId = self.role.GetI32(EnumInt32.TaortAllotID) + 1
		#下个可分配ID自增
		self.role.IncI32(EnumInt32.TaortAllotID, 1)
		cardDataDict = {CardTypeKey : card_Type, CardLevelKey : 1, CardExpKey : 0, CardLockKey : 0, CardPosKey : 0}
		tc = TarotCard(self.role, alloId, cardDataDict)
		self.tarotOwner_ID_Dict[TAROT_PACKAGE_ID][alloId] = tc
		if tc.IsLog():
			#写日志
			AutoLog.LogObj(self.role.GetRoleID(), AutoLog.eveTarot_AddCard, alloId, card_Type, 1, None, None)
		
		tcGrade = tc.GetGrade()
		
		if tcGrade >= 4:
			from Game.Activity.ProjectAct import ProjectAct, EnumProActType
			ProjectAct.GetFunByType(EnumProActType.ProjectTatotEvent, [self.role, tcGrade])
			
		#版本判断
		if Environment.EnvIsNA():
			if tcGrade == 5:
				#开服活动
				kaifuActMgr = self.role.GetTempObj(EnumTempObj.KaiFuActMgr)
				kaifuActMgr.inc_yellow_tarot_cnt()
			if tcGrade >= 4:
				#通用活动
				HalloweenNAMgr = self.role.GetTempObj(EnumTempObj.HalloweenNAMgr)
				HalloweenNAMgr.IncTarotCnt(tcGrade)
		
		return alloId, tcGrade

	def NewTarotCards(self, typeList):
		res = []
		tpl = []
		for card_Type in typeList:
			alloId = self.role.GetI32(EnumInt32.TaortAllotID) + 1
			self.role.IncI32(EnumInt32.TaortAllotID, 1)
			cardDataDict = {CardTypeKey : card_Type, CardLevelKey : 1, CardExpKey : 0, CardLockKey : 0, CardPosKey : 0}
			tc = TarotCard(self.role, alloId, cardDataDict)
			self.tarotOwner_ID_Dict[TAROT_PACKAGE_ID][alloId] = tc
			res.append((alloId, card_Type))
			if tc.IsLog():
				#写日志
				AutoLog.LogObj(self.role.GetRoleID(), AutoLog.eveTarot_AddCard, alloId, card_Type, 1, None, None)
				
			tcGrade = tc.GetGrade()
			if tcGrade >= 4:
				from Game.Activity.ProjectAct import ProjectAct, EnumProActType
				ProjectAct.GetFunByType(EnumProActType.ProjectTatotEvent, [self.role, tcGrade])
			
			if tcGrade > 4:
				tpl.append(card_Type)
			
			#版本判断
			if Environment.EnvIsNA():
				if tcGrade == 5:
					#开服活动
					kaifuActMgr = self.role.GetTempObj(EnumTempObj.KaiFuActMgr)
					kaifuActMgr.inc_yellow_tarot_cnt()
				if tcGrade >= 4:
					#通用活动
					HalloweenNAMgr = self.role.GetTempObj(EnumTempObj.HalloweenNAMgr)
					HalloweenNAMgr.IncTarotCnt(tcGrade)
				
		return res, tpl

	def GetOwnerTarotDict(self, ownerId):
		#获取对应拥有者自己的塔罗牌字典
		return self.tarotOwner_ID_Dict.setdefault(ownerId, {})

	def ResetAllTarotProperty(self):
		#重置所有的卡的属性
		for ttDict in self.tarotOwner_ID_Dict.itervalues():
			for tarot_card in ttDict.itervalues():
				tarot_card.ResetProperty() 
				
	
	def GetRoleViewData(self):
		#获取角色用于查看的数据
		cd = {}
		for card in self.GetOwnerTarotDict(TAROT_ROLE_PACKAGE_ID).itervalues():
			cd[card.cardType] = card.level
		return cd 

	def GetHeroViewData(self, heroId):
		#获取角色用于查看的数据
		if heroId not in self.tarotOwner_ID_Dict:
			return {}
		cd = {}
		for card in self.GetOwnerTarotDict(heroId).itervalues():
			cd[card.cardType] = card.level
		return cd 

	def HeroHasCard(self, heroId):
		if heroId not in self.tarotOwner_ID_Dict:
			return False
		
		return self.tarotOwner_ID_Dict[heroId]

	

	