#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Property.PropertyMgr")
#===============================================================================
# 属性管理器
#===============================================================================
import cDateTime
import cRoleDataMgr
from Game.Property import PropertyGather
from Game.Role.Data import EnumTempObj, EnumInt8
from Game.Property import PropertyRecount
from Game.ZDL import ZDL



if "_HasLoad" not in dir():
	WingRecountFun = PropertyRecount.RecountWing
	MountRecountFun = PropertyRecount.RecountMount
	MountAppRecountFun = PropertyRecount.RecountMountApp
	DragonRecountFun = PropertyRecount.RecountDragon
	HelpStationRecountFun = PropertyRecount.RecountHelpStation
	WeddingRingRecountFun = PropertyRecount.RecountWeddingRing
	WeddingRingSRecountFun = PropertyRecount.RecountWeddingRingS
	WeddingRingSCoefRecountFun = PropertyRecount.RecountWeddingRingSCoef
	WeddingRingSkillRecountFun = PropertyRecount.RecountWeddingRingSkill
	FashionGlobalRecountFun = PropertyRecount.RecountFashionGlobal
	QinmiRecountFun = PropertyRecount.RecountQinmi
	QinmiGradeRecountFun = PropertyRecount.RecountQinmiGrade
	UnionSkillRecountFun = PropertyRecount.RecountUnionSkill
	TitleTeamRecountFun = PropertyRecount.RecountTitleTeam
	TitleTeamExRecountFun = PropertyRecount.RecountTitleTeamEx
	TitleTeamExCoefRecountFun = PropertyRecount.RecountTitleTeamExCoef
	MarryRingRecountFun = PropertyRecount.RecountMarryRing
	WSBaseProRecountFun = PropertyRecount.RecountWStationBasePro
	WSThousandRecountFun = PropertyRecount.RecountWStationThousandPro
	WSItemProRecountFun = PropertyRecount.RecountEStationItemPro
	StationSoulBaseRecountFun = PropertyRecount.RecountStationSoulBase
	StationSoulPTTRecountFun = PropertyRecount.RecountStationSoulPTT
	StaionSoulItemProRecountFun = PropertyRecount.RecountStationSoulItemPro
	ZhuanShengHaloBaseRecountFun = PropertyRecount.RecountZhuanShengHaloBase
	CardAtlasRecountFun = PropertyRecount.RecountCardAtlas
	CardAtlasSuitRecountFun = PropertyRecount.RecountCardAtlasSuit
	ElementSpiritBaseRecountFun = PropertyRecount.RecountElementSpiritBase
	ElementSpiritPTTRecountFun = PropertyRecount.RecountElementSpiritPTT
	ElementBrandBaseRecountFun = PropertyRecount.RecountElementBrandBase
	SealBaseRecountFun = PropertyRecount.RecountSealBase
	SealPTTRecountFun = PropertyRecount.RecountSealPTT
	ElementBrandWashRecountFun = PropertyRecount.RecountElementBrandWash
	
###############################################################################
def RecountPorperty(role):
	#C++调用触发重算
	role.GetTempObj(EnumTempObj.PM).CheckRecount()


###############################################################################
#属性管理器
###############################################################################
class PropertyMgr(object):
	def __init__(self, role):
		self.role = role
		#自己的属性集合
		self.role_propertyGather = PropertyGather.PropertyGather(self, role, role)
		#英雄属性集合字典
		self.hero_propertyGather_dict = {}
		#是否需要重算
		self.need_recount = True
		#全局属性是否需要重算
		self.global_need_recount = True
		#重算记录时间戳(防止循环重算,1秒只能触发一次进入重算主体)
		self.recount_secs = 0
		#已经重算的次数
		self.recount_cnt = 0
		
		PP = PropertyGather.Property
		#全局属性
		#翅膀
		self.wing_p = PP(WingRecountFun)
		#助阵位
		self.helpstation_p = PP(HelpStationRecountFun)
		#坐骑基础
		self.mountBase_p = PP(MountRecountFun)
		#坐骑外形品质
		self.mountApp_p = PP(MountAppRecountFun)
		#神龙
		self.dragon_p = PP(DragonRecountFun)
		#订婚戒指
		self.marryRing_p = PP(MarryRingRecountFun)
		#婚戒
		self.weddingRing_p = PP(WeddingRingRecountFun)
		#婚戒戒灵
		self.weddingRingS_p = PP(WeddingRingSRecountFun)
		#婚戒戒灵(万份比攻击力加成)
		self.weddingRingS_coef = PP(WeddingRingSCoefRecountFun)
		#夫妻技能
		self.weddingRingSkill_p = PP(WeddingRingSkillRecountFun)
		#时装
		self.fashionglobal_p = PP(FashionGlobalRecountFun)
		#亲密等级
		self.qinmi_p = PP(QinmiRecountFun)
		#亲密品阶
		self.qinmiGrade_p = PP(QinmiGradeRecountFun)
		#公会技能
		self.unionSkill_p = PP(UnionSkillRecountFun)
		#称号全队属性
		self.titleTeam_p = PP(TitleTeamRecountFun)
		#称号全队属性(隐藏属性)
		self.titleTeamEx_p = PP(TitleTeamExRecountFun)
		#称号全队万分比属性(隐藏属性)
		self.titleTeamEx_coef_p = PP(TitleTeamExCoefRecountFun)
		#战阵基础属性，全队
		self.warStationbase_p = PP(WSBaseProRecountFun)
		#战阵万分比属性
		self.warStationThousand_p = PP(WSThousandRecountFun)
		#战阵战魂石属性
		self.warStationItem_p = PP(WSItemProRecountFun)
		#阵灵基础属性
		self.stationSoulBase_p = PP(StationSoulBaseRecountFun)
		#阵灵万分比属性
		self.stationSoulPTT_p = PP(StationSoulPTTRecountFun)
		#阵灵强化石属性
		self.stationSoulItem_p = PP(StaionSoulItemProRecountFun)
		#转生光环基础属性
		self.zhuanshengHaloBase_p = PP(ZhuanShengHaloBaseRecountFun)
		#卡牌图鉴全队属性
		self.cardAtlas_p = PP(CardAtlasRecountFun)
		#卡牌图鉴全队万分比属性
		self.cardAtlasSuit_coef_p = PP(CardAtlasSuitRecountFun)
		#元素之灵基础属性
		self.elementSpiritBase_p = PP(ElementSpiritBaseRecountFun)
		#元素之灵属性万分比
		self.elementSpiritPTT_p = PP(ElementSpiritPTTRecountFun)
		#元素印记基础属性
		self.elementBrandBase_p = PP(ElementBrandBaseRecountFun)
		#圣印基础属性
		self.sealBase_p = PP(SealBaseRecountFun)
		#圣印属性万分比
		self.sealPTT_p = PP(SealPTTRecountFun)
		#元素印记洗练属性
		self.elementBrandWash_p = PP(ElementBrandWashRecountFun)
		
	def SyncAllProperty(self):
		#同步所有的属性给客户端
		self.role_propertyGather.SyncData()
		for pg in self.hero_propertyGather_dict.itervalues():
			pg.SyncData()
	
	def PropertyIsValid(self):
		#重算次数大于0，则有效
		return self.recount_cnt > 0
	
	
	def CreateHeroProperty(self, hero):
		heroId = hero.GetHeroId()
		if heroId in self.hero_propertyGather_dict:
			print "GE_EXC, repeat CreateHeroProperty (%s)" % heroId
			return
		PG = PropertyGather.PropertyGather(self, self.role, hero)
		self.hero_propertyGather_dict[heroId] = PG
		return PG
	
	def RemoveHeroProperty(self, heroId):
		if heroId not in self.hero_propertyGather_dict:
			print "GE_EXC, error in RemoveHeroProperty not this heroId"
			return
		del self.hero_propertyGather_dict[heroId]
	
	
	def CheckRecount(self):
		if self.need_recount is False:
			return
		
		nowsec = cDateTime.Seconds()
		if self.recount_secs >= nowsec:
			#这一秒已经触发过一次重算了，这里可能有循环调用重算的问题
			return
		#记录这次重算的时间点
		self.recount_secs = nowsec
		
		#先重算全局的属性
		need_recount_zdl = self.RecountGlobal()
		#主角
		if self.role_propertyGather.need_recount is True:
			self.role_propertyGather.RecountAll()
			need_recount_zdl = True
		#英雄
		for hero_propertyGather in self.hero_propertyGather_dict.itervalues():
			if hero_propertyGather.need_recount is True:
				hero_propertyGather.RecountAll()
				need_recount_zdl = True
		
		if need_recount_zdl is True:
			#重算战斗力
			self.RecountTotalZDL()
		#重算完毕
		self.need_recount = False
		#统计重算次数
		self.recount_cnt += 1
		self.role.FinishRecount()

	def RecountGlobal(self):
		#重算全局的属性
		if self.global_need_recount is False:
			return False
		
		self.wing_p.GoToRecount(self.role)
		self.mountBase_p.GoToRecount(self.role)
		self.mountApp_p.GoToRecount(self.role)
		self.helpstation_p.GoToRecount(self.role)
		self.marryRing_p.GoToRecount(self.role)
		self.weddingRing_p.GoToRecount(self.role)
		self.weddingRingS_p.GoToRecount(self.role)
		self.weddingRingS_coef.GoToRecount(self.role)
		self.weddingRingSkill_p.GoToRecount(self.role)
		self.fashionglobal_p.GoToRecount(self.role)
		self.qinmi_p.GoToRecount(self.role)
		self.qinmiGrade_p.GoToRecount(self.role)
		self.unionSkill_p.GoToRecount(self.role)
		self.titleTeam_p.GoToRecount(self.role)
		self.titleTeamEx_p.GoToRecount(self.role)
		self.titleTeamEx_coef_p.GoToRecount(self.role)
		self.warStationbase_p.GoToRecount(self.role)
		self.warStationThousand_p.GoToRecount(self.role)
		self.warStationItem_p.GoToRecount(self.role)
		self.stationSoulBase_p.GoToRecount(self.role)
		self.stationSoulPTT_p.GoToRecount(self.role)
		self.stationSoulItem_p.GoToRecount(self.role)
		self.zhuanshengHaloBase_p.GoToRecount(self.role)
		self.cardAtlas_p.GoToRecount(self.role)
		self.cardAtlasSuit_coef_p.GoToRecount(self.role)
		self.elementSpiritBase_p.GoToRecount(self.role)
		self.elementSpiritPTT_p.GoToRecount(self.role)
		self.elementBrandBase_p.GoToRecount(self.role)
		self.sealBase_p.GoToRecount(self.role)
		self.sealPTT_p.GoToRecount(self.role)
		self.elementBrandWash_p.GoToRecount(self.role)
		return True
	
	def RecountTotalZDL(self):
		#重算总战斗力
		ZDL.RecountTotalZDL(self.role)
	
	################################################################################
	#
	################################################################################
	def SetNeedRecount(self):
		self.need_recount = True
		self.role.SetNeedRecount()
	
	def SetAllStationRecount(self):
		#设置所有上阵的都需要重算属性
		self.role_propertyGather.need_recount = True
		for pg in self.hero_propertyGather_dict.itervalues():
			if pg.stationId >= 0:
				pg.need_recount = True
	
	def ResetGlobalHelpStationProperty(self):
		self.SetNeedRecount()
		self.global_need_recount = True
		self.helpstation_p.need_recount = True
		self.SetAllStationRecount()
	
	def ResetGlobalMountProperty(self):
		self.SetNeedRecount()
		self.global_need_recount = True
		self.mountBase_p.need_recount = True
		self.SetAllStationRecount()
		
	def ResetGlobalMountAppProperty(self):
		self.SetNeedRecount()
		self.global_need_recount = True
		self.mountApp_p.need_recount = True
		self.SetAllStationRecount()
		
	def ResetGlobalWingProperty(self):
		self.SetNeedRecount()
		self.global_need_recount = True
		self.wing_p.need_recount = True
		self.SetAllStationRecount()
		
	def ResetGlobalDragonProperty(self):
		self.SetNeedRecount()
		self.global_need_recount = True
		self.helpstation_p.need_recount = True
		self.SetAllStationRecount()
	
	def ResetGlobalMarryRingProperty(self):
		#订婚戒指
		self.SetNeedRecount()
		self.global_need_recount = True
		self.marryRing_p.need_recount = True
		self.SetAllStationRecount()
		
	def ResetGlobalWeddingRingProperty(self):
		#婚戒
		self.SetNeedRecount()
		self.global_need_recount = True
		self.weddingRing_p.need_recount = True
		self.SetAllStationRecount()
	
	def ResetGlobalWeddingRingSProperty(self):
		#婚戒戒灵
		self.SetNeedRecount()
		self.global_need_recount = True
		self.weddingRingS_p.need_recount = True
		self.weddingRingS_coef.need_recount = True
		self.SetAllStationRecount()
		
	def ResetGlobalWeddingRingSkillProperty(self):
		#夫妻技能
		self.SetNeedRecount()
		self.global_need_recount = True
		self.weddingRingS_p.need_recount = True
		self.weddingRingSkill_p.need_recount = True
		self.SetAllStationRecount()
		
	#特殊占卜光环引起
	def ResetAllTarotProperty(self):
		self.role_propertyGather.ReSetRecountTarotFlag()
		for pg in self.hero_propertyGather_dict.itervalues():
			if pg.stationId >= 0:
				pg.ReSetRecountTarotFlag()

	def ResetGlobalFashionProperty(self):
		#时装
		self.SetNeedRecount()
		self.global_need_recount = True
		self.fashionglobal_p.need_recount = True
		self.SetAllStationRecount()
	
	def ResetGlobalQinmiProperty(self):
		#亲密等级
		self.SetNeedRecount()
		self.global_need_recount = True
		self.qinmi_p.need_recount = True
		self.SetAllStationRecount()
	
	def ResetGlobalQinmiGradeProperty(self):
		#亲密品阶
		self.SetNeedRecount()
		self.global_need_recount = True
		self.qinmiGrade_p.need_recount = True
		self.SetAllStationRecount()
	
	def ResetGlobalUnionSkillProperty(self):
		#公会技能
		self.SetNeedRecount()
		self.global_need_recount = True
		self.unionSkill_p.need_recount = True
		self.SetAllStationRecount()
	
	def ResetGlobalTitleTeamProperty(self):
		#称号的全队属性
		self.SetNeedRecount()
		self.global_need_recount = True
		self.titleTeam_p.need_recount = True
		self.titleTeamEx_p.need_recount = True
		self.titleTeamEx_coef_p.need_recount = True
		self.SetAllStationRecount()
	
	def ResetGlobalWStationBaseProperty(self):
		#战阵基础属性
		self.SetNeedRecount()
		self.global_need_recount = True
		self.warStationbase_p.need_recount = True
		self.SetAllStationRecount()
		
	def ResetGlobalWStationThousandProperty(self):
		#战阵万分比属性
		self.SetNeedRecount()
		self.global_need_recount = True
		self.warStationThousand_p.need_recount = True
		self.SetAllStationRecount()
		
	def ResetGlobalWStationItemProperty(self):
		#战阵战魂石属性
		self.SetNeedRecount()
		self.global_need_recount = True
		self.warStationItem_p.need_recount = True
		self.SetAllStationRecount()
		
	def ResetGlobalStationSoulBaseProperty(self):
		#阵灵基础属性
		self.SetNeedRecount()
		self.global_need_recount = True
		self.stationSoulBase_p.need_recount = True
		self.SetAllStationRecount()
	
	def ResetGlobalStationSoulPPTProperty(self):
		#阵灵基础属性
		self.SetNeedRecount()
		self.global_need_recount = True
		self.stationSoulPTT_p.need_recount = True
		self.SetAllStationRecount()
		
	def ResetGlobalStationSoulItemProperty(self):
		#阵灵强化石属性
		self.SetNeedRecount()
		self.global_need_recount = True
		self.stationSoulItem_p.need_recount = True
		self.SetAllStationRecount()
	
	def ResetGlobalZhuanShengHaloBaseProperty(self):
		#转生光环基础属性
		self.SetNeedRecount()
		self.global_need_recount = True
		self.zhuanshengHaloBase_p.need_recount = True
		self.SetAllStationRecount()
		
	def ResetGlobalElementSpiritBaseProperty(self):
		#元素之灵基础属性
		self.SetNeedRecount()
		self.global_need_recount = True
		self.elementSpiritBase_p.need_recount = True
		self.SetAllStationRecount()
	
	def ResetGlobalCardAtlasProperty(self):
		#卡牌图鉴全队属性
		self.SetNeedRecount()
		self.global_need_recount = True
		self.cardAtlas_p.need_recount = True
		self.cardAtlasSuit_coef_p.need_recount = True
		self.SetAllStationRecount()
		
	def ResetGlobalElementSpiritPPTProperty(self):
		#元素之灵属性万分比
		self.SetNeedRecount()
		self.global_need_recount = True
		self.elementSpiritPTT_p.need_recount = True
		self.SetAllStationRecount()
		
	def ResetGlobalElementBrandBaseProperty(self):
		#元素之灵基础属性
		self.SetNeedRecount()
		self.global_need_recount = True
		self.elementBrandBase_p.need_recount = True
		self.SetAllStationRecount()
	
	def ResetGlobalSealBaseProperty(self):
		#圣印系统基础属性
		self.SetNeedRecount()
		self.global_need_recount = True
		self.sealBase_p.need_recount = True
		self.SetAllStationRecount()
	
	def ResetGlobalSealPPTProperty(self):
		#圣印系统属性万分比
		self.SetNeedRecount()
		self.global_need_recount = True
		self.sealPTT_p.need_recount = True
		self.SetAllStationRecount()
		
	def ResetGlobalElementBrandWashProperty(self):
		#元素之灵基础属性
		self.SetNeedRecount()
		self.global_need_recount = True
		self.elementBrandWash_p.need_recount = True
		self.SetAllStationRecount()
		
	
def InitMgr(role):
	#初始化属性管理器
	role.SetTempObj(EnumTempObj.PM, PropertyMgr(role))

def AfterSetStationID(role, oldValue, newValue):
	#角色改变阵位
	role.GetTempObj(EnumTempObj.PM).role_propertyGather.SetStationID(newValue)

if "_HasLoad" not in dir():
	cRoleDataMgr.SetInt8Fun(EnumInt8.enStationID, AfterSetStationID)
