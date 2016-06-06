#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Property.PropertyGather")
#===============================================================================
# 属性集合
#===============================================================================
import traceback
import Environment
from Common.Message import AutoMessage
from Game.ZDL import ZDL
from Game.Property import PropertyEnum
from Game.Property import PropertyRecount


if "_HasLoad" not in dir():
	BaseRecountFun = PropertyRecount.RecountBase
	
	PetRecountFun = PropertyRecount.RecountPet
	PetRecountEvoPet = PropertyRecount.RecountEvoPet
	
	TarotRecountFun = PropertyRecount.RecountTarot
	
	SkillRecountFun = PropertyRecount.RecountSkill
	SkillCoefRecountFun = PropertyRecount.RecountSkillCoef
	
	CuiLianBaseRecountFun = PropertyRecount.RecountCuiLianBase
	
	EquipmentBaseRecountFun = PropertyRecount.RecountEquipmentBase
	EquipmentStrengthenRecountFun = PropertyRecount.RecountEquipmentStrengthen
	EquipmentZhuanShengRecountFun = PropertyRecount.RecountEquipmentZhuanSheng
	EquipmentGemRecountFun = PropertyRecount.RecountEquipmentGem
	EquipmentWashRecountFun = PropertyRecount.RecountEquipmentWash
	
	ArtifactBaseRecountFun = PropertyRecount.RecountArtifactBase
	ArtifactStrengthenRecountFun = PropertyRecount.RecountArtifactStrengthen
	ArtifactGemRecountFun = PropertyRecount.RecountArtifactGem
	ArtifactSuitRecountFun = PropertyRecount.RecountArtifactSuit
	ArtifactCuiLianRecountFun = PropertyRecount.RecountArtifactCuiLian
	ArtifactCuiLianSuiteRecountFun = PropertyRecount.RecountArtifactCuiLianSuite
	ArtifactCuiLianHoleRecountFun = PropertyRecount.RecountArtifactCuiLianHole
	
	HallowsRecountFun = PropertyRecount.RecountHallows
	HallowsCoefRecountFun = PropertyRecount.RecountHallowsCoef
	HallowsShenzaoRecountFun = PropertyRecount.RecountHallowsShenzao
	HallowsGemRecountFun = PropertyRecount.RecountHallowsGem
	
	TalentCardRecountFun = PropertyRecount.RecountRoleTalent
	TalentCardSuitRecountFun = PropertyRecount.RecountSuitTalent
	
	GameUnionLogBuffRecountFun = PropertyRecount.RecountGameUnionLogBuff
	
	DragonTrainRecountFun = PropertyRecount.RecountDragonTrain
	DragonVeinRecountFun = PropertyRecount.RecountDragonVein
	DragonVeinBufRecountFun = PropertyRecount.RecountDragonVeinBuf
	
	FashionRecountFun = PropertyRecount.RecountRoleFashion
	FashionSuitRecountFun = PropertyRecount.RecountRoleFashionSuit
	FashionHoleRecountFun = PropertyRecount.RecountRoleFashionHole
	
	HalloweenBuffRecountFun = PropertyRecount.RecountCardBuff
	StarGirlRecountFun = PropertyRecount.RecountStarGirl
	
	JTMedalRecountFun = PropertyRecount.RecountJTMedal
	TitleRoleRecountFun = PropertyRecount.RecountTitleRole
	TitleRoleExRecountFun = PropertyRecount.RecountTitleRoleEx
	TitleRoleExCoefRecountFun = PropertyRecount.RecountTitleRoleExCoef
	
	MagicSpiritRecountFun = PropertyRecount.RecountMagicSpirit
	
	ZhuanShengProRecountFun = PropertyRecount.RecountZhuanShengPro

	
	RecountZDLFun = ZDL.RecountPropertyGatherZDL

#属性数据结构
class Property(object):
	def __init__(self, recountFun = None):
		self.p_dict = {}
		self.need_recount = True
		self.recountFun = recountFun
	
	
	def AddProperty(self, otherProperty):
		pd = otherProperty.p_dict
		if not pd:
			return
		SPG = self.p_dict.get
		SP = self.p_dict
		for pt, pv in pd.iteritems():
			SP[pt] = SPG(pt, 0) + pv
	
	def PercentProperty(self, otherProperty):
		pd = otherProperty.p_dict
		if not pd:
			return
		SPG = self.p_dict.get
		SP = self.p_dict
		for pt, pv in pd.iteritems():
			nowpv = SPG(pt, 0)
			if not nowpv:
				continue
			SP[pt] = int(nowpv + pv * nowpv / 10000.0)
	
	def GoToRecount(self, param):
		#进入重算具体逻辑
		if self.need_recount is False:
			return False
		self.p_dict = {}
		self.need_recount = False
		try:
			self.recountFun(param, self.p_dict)
		except:
			traceback.print_exc()
		return True
	
	def DelProperty(self, pt):
		if pt not in self.p_dict:
			return
		del self.p_dict[pt]

#属性集合，里面包含个各种各样的属性结构
class PropertyGather(object):
	RECOUNTARTIFACT = None
	def __init__(self, mgr, role, owner):
		#管理器
		self.mgr = mgr
		#角色
		self.role = role
		#拥有者
		self.owner = owner
		#如果是英雄的就记录英雄ID
		if role is owner:
			self.heroId = 0
		else:
			self.heroId = owner.GetHeroId()
		
		#阵位
		self.stationId = owner.GetStationID()
		#职业(注意!主角 1，2，英雄1，2，3，主角只有物攻，英雄职业1物攻，其他法攻)
		self.career = owner.GetCareer()
		
		#重算标识
		self.need_recount = True
		
		#普通总属性
		self.total_p = Property()
		#包含坐骑的总属性
		self.total_p_m = Property()
		#总万份比属性
		self.total_p_coef = Property()
		#总万分比+隐藏万分比  h=hide
		self.total_p_h_coef = Property()
		#包含隐藏属性的总属性
		self.total_p_h = Property()
		
		#裸体属性
		self.base_p = Property(BaseRecountFun)
		#转生属性
		self.zhuanSheng_p = Property(ZhuanShengProRecountFun)

		#占卜命魂
		self.tarot_p = Property(TarotRecountFun)
		#宠物
		self.pet_p = Property(PetRecountFun)
		self.petEvo_p = Property(PetRecountEvoPet)
		
		#淬炼
		self.CuiLianBase_p = Property(CuiLianBaseRecountFun)
		#装备
		self.equipmentBase_p = Property(EquipmentBaseRecountFun)
		self.equipmentStrengthen_p = Property(EquipmentStrengthenRecountFun)
		self.equipmentZhuanSheng_p = Property(EquipmentZhuanShengRecountFun)
		self.equipmentGem_p = Property(EquipmentGemRecountFun)
		self.equipmentWash_p = Property(EquipmentWashRecountFun)
		#神器
		self.artifactBase_p = Property(ArtifactBaseRecountFun)
		self.artifactStrengthen_p = Property(ArtifactStrengthenRecountFun)
		self.artifactGem_p = Property(ArtifactGemRecountFun)
		self.artifactSuit_p = Property(ArtifactSuitRecountFun)
		self.artifactCuiLian_p = Property(ArtifactCuiLianRecountFun)
		self.artifactCuiLianSuite_p = Property(ArtifactCuiLianSuiteRecountFun)
		self.artifactCuiLianHole_p = Property(ArtifactCuiLianHoleRecountFun)
		
		
		#神器版本修复
		if Environment.EnvIsNA() or Environment.EnvIsFT() or Environment.EnvIsYY() or Environment.EnvIsEN() or Environment.EnvIsGER() or Environment.EnvIsESP():
			self.RECOUNTARTIFACT = self.RecountArtifact_Ex
		else:
			self.RECOUNTARTIFACT = self.RecountArtifact
		
		
		#圣器
		self.hallowsBase_p = Property(HallowsRecountFun)
		self.hallowsCoef_p = Property(HallowsCoefRecountFun)
		self.hallowsShenzao_p = Property(HallowsShenzaoRecountFun)
		self.hallowsGem_p = Property(HallowsGemRecountFun)
		
		#技能
		self.skill_p = Property(SkillRecountFun)
		self.skill_coef_p = Property(SkillCoefRecountFun)
		
		#天赋卡
		self.talentcard_p = Property(TalentCardRecountFun)
		self.talentcardsuit_p = Property(TalentCardSuitRecountFun)
		
		#游戏联盟登录
		self.GameUnion_p = Property(GameUnionLogBuffRecountFun)
		
		#驯龙
		self.dragonTrain_p = Property(DragonTrainRecountFun)
		
		#龙脉
		self.dragonVein_p = Property(DragonVeinRecountFun)
		
		#龙脉buf
		self.dragonVeinBuf_p = Property(DragonVeinBufRecountFun)
		
		#勋章
		self.JTMedal_p = Property(JTMedalRecountFun)
	
		#时装
		self.fashion_p = Property(FashionRecountFun)
		self.fashionSuit_p = Property(FashionSuitRecountFun)
		self.fashionHole_p = Property(FashionHoleRecountFun)
		
		self.hbuff_p = Property(HalloweenBuffRecountFun)
		#星灵
		self.starGirl_p = Property(StarGirlRecountFun)
		#称号基础属性
		self.titleRole_p = Property(TitleRoleRecountFun)
		#称号额外隐藏属性
		self.titleRoleEx_p = Property(TitleRoleExRecountFun)
		#称号加成万分比
		self.titleRoleEx_coef_p = Property(TitleRoleExCoefRecountFun)
		#魔灵
		self.magicSpirit_p = Property(MagicSpiritRecountFun)
		
		self.AfterCreate()
		
	def AfterCreate(self):
		self.TotalNeedRecount()
	
	################################################################################
	def SyncData(self):
		#同步数据
		if not self.heroId:
			self.role.SendObj(Msg_SyncRoleProperty, self.total_p.p_dict)
		else:
			self.role.SendObj(Msg_SyncHeroProperty, (self.heroId, self.total_p.p_dict))

	
	################################################################################
	#设置重算标识规则
	################################################################################
	def TotalNeedRecount(self):
		self.need_recount = True
		self.mgr.SetNeedRecount()
	
	def ReSetRecountBaseFlag(self):
		#设置裸体属性需要重算
		self.TotalNeedRecount()
		self.base_p.need_recount = True
		
	def ReSetRecountCuiLianFlag(self):
		#设置淬炼属性重算
		self.TotalNeedRecount()
		self.CuiLianBase_p.need_recount = True
			
	def ReSetRecountSkillFlag(self):
		#设置被动技能属性需要重算
		self.TotalNeedRecount()
		self.skill_p.need_recount = True
		self.skill_coef_p.need_recount = True
	
	def ReSetRecountEquipmentFlag(self):
		#设置装备全部属性需要重算
		self.TotalNeedRecount()
		self.equipmentBase_p.need_recount = True
		self.equipmentStrengthen_p.need_recount = True
		self.equipmentZhuanSheng_p.need_recount = True
		self.equipmentGem_p.need_recount = True
		self.equipmentWash_p.need_recount = True
		
	def ReSetRecountEquipmentZhuanShengFlag(self):
		#设置装备转生属性重算
		self.need_recount = True
		self.equipmentZhuanSheng_p.need_recount = True
		
	def ReSetRecountEquipmentBaseFlag(self):
		#设置装备基础属性需要重算
		self.need_recount = True
		self.equipmentBase_p.need_recount = True
		
	def ReSetRecountEquipmentStrengthenFlag(self):
		#设置装备强化属性需要重算
		self.TotalNeedRecount()
		self.equipmentStrengthen_p.need_recount = True
		
	def ReSetRecountEquipmentGemFlag(self):
		#设置装备宝石属性需要重算
		self.TotalNeedRecount()
		self.equipmentGem_p.need_recount = True
		
	def ReSetRecountEquipmentWashFlag(self):
		#设置装备洗练属性重算
		self.TotalNeedRecount()
		self.equipmentWash_p.need_recount = True
		
	def ReSetRecountArtifactFlag(self):
		#设置神器全部属性需要重算
		self.TotalNeedRecount()
		self.artifactBase_p.need_recount = True
		self.artifactStrengthen_p.need_recount = True
		self.artifactGem_p.need_recount = True
		self.artifactSuit_p.need_recount = True
		self.artifactCuiLian_p.need_recount = True
		self.artifactCuiLianSuite_p.need_recount = True
		self.artifactCuiLianHole_p.need_recount = True
		
	def ReSetRecountArtifactBaseFlag(self):
		#设置神器基础属性需要重算
		self.TotalNeedRecount()
		self.artifactBase_p.need_recount = True
		
	def ReSetRecountArtifactStrengthenFlag(self):
		#设置神器强化属性需要重算
		self.TotalNeedRecount()
		self.artifactStrengthen_p.need_recount = True
		
	def ReSetRecountArtifactGemFlag(self):
		#设置神器符文属性需要重算
		self.TotalNeedRecount()
		self.artifactGem_p.need_recount = True
		
	def ReSetRecountArtifactSuitFlag(self):
		#设置神器套装属性需要重算
		self.TotalNeedRecount()
		self.artifactSuit_p.need_recount = True
	
	def ReSetRecountArtifactCuiLianFlag(self):
		#设置神器淬炼属性需要重算
		self.TotalNeedRecount()
		self.artifactCuiLian_p.need_recount = True
		
	def ReSetRecountArtifactCuiLianSuiteFlag(self):
		#设置神器淬炼套装万分比加成重算
		self.TotalNeedRecount()
		self.artifactCuiLianSuite_p.need_recount = True
		
	def ReSetRecountArtifactCuiLianHoleFlag(self):
		#设置神器淬炼光环万分比加成重算
		self.TotalNeedRecount()
		self.artifactCuiLianHole_p.need_recount = True	
		
	def ReSetRecountTarotFlag(self):
		#设置占卜属性需要重算
		self.TotalNeedRecount()
		self.tarot_p.need_recount = True
		
	def ReSetRecountPetFlag(self):
		#设置宠物属性需要重算
		self.TotalNeedRecount()
		self.pet_p.need_recount = True
	
	def ReSetRecountPetRvoFlag(self):
		#设置宠物进化属性重算
		self.TotalNeedRecount()
		self.petEvo_p.need_recount = True
	
	def ReSetRecountHallowsFlag(self):
		#设置圣器属性重算
		self.TotalNeedRecount()
		self.hallowsBase_p.need_recount = True
		self.hallowsCoef_p.need_recount = True
		self.hallowsShenzao_p.need_recount = True
		self.hallowsGem_p.need_recount = True
		
	def ReSetRecountHallowsGemFlag(self):
		#设置圣器雕纹属性需要重算
		self.TotalNeedRecount()
		self.hallowsGem_p.need_recount = True
	
	def ReSetRecountHallowsShenzaoFlag(self):
		#设置圣器神造属性重算
		self.TotalNeedRecount()
		self.hallowsShenzao_p.need_recount = True
	
	def ReSetRecountTalentFlag(self):
		#设置天赋卡属性重算
		self.TotalNeedRecount()
		self.talentcard_p.need_recount = True
	
	def ReSetRecountTalentSuitFlag(self):
		#设置天赋卡套装属性重算
		self.TotalNeedRecount()
		self.talentcardsuit_p.need_recount = True
	
	def ReSetRecountGameUnionLogBuffFlag(self):
		#设置游戏联盟登录属性
		self.TotalNeedRecount()
		self.GameUnion_p.need_recount = True
		
	def ReSetRecountDragonTrainFlag(self):
		#设置驯龙属性需要重算
		self.TotalNeedRecount()
		self.dragonTrain_p.need_recount = True
		
	def ReSetRecountFashionFlag(self):
		#设置时装总基础属性重算
		self.TotalNeedRecount()
		self.fashion_p.need_recount = True
		
	def ReSetRecountFashionSuitFlag(self):
		#设置时装套装属性重算
		self.TotalNeedRecount()
		self.fashionSuit_p.need_recount = True
		
	def ReSetRecpintFashionHoleFlag(self):
		#设置时装光环属性重算
		self.TotalNeedRecount()
		self.fashionHole_p.need_recount = True
		
	def ReSetRecountStarGirlFlag(self):
		#设置星灵属性需要重算
		self.TotalNeedRecount()
		self.starGirl_p.need_recount = True
		
	def ReSetRecountCardBuffFlag(self):
		#设置变身卡属性重算
		self.TotalNeedRecount()
		self.hbuff_p.need_recount = True
	
	def ReSetRecountDragonVeinFlag(self):
		#设置龙脉属性需要重算
		self.TotalNeedRecount()
		self.dragonVein_p.need_recount = True
		
	def ReSetRecountDragonVeinBufFlag(self):
		#设置龙脉buf属性需要重算
		self.TotalNeedRecount()
		self.dragonVeinBuf_p.need_recount = True
	
	def ReSetRecountJTMedalFlag(self):
		#设置勋章属性需要重算
		self.TotalNeedRecount()
		self.JTMedal_p.need_recount = True
	
	
	def ResetRecountTitleRoleFlag(self):
		#称号主角属性
		self.TotalNeedRecount()
		self.titleRole_p.need_recount = True
		self.titleRoleEx_p.need_recount = True
		self.titleRoleEx_coef_p.need_recount = True
		
	def ResetRecountMagicSpiritFlag(self):
		#设置魔灵属性需要重算
		self.TotalNeedRecount()
		self.magicSpirit_p.need_recount = True
	
#	def ResetRecountStationSoulFlag(self):
#		#设置阵灵属性需要重算
#		self.TotalNeedRecount()
#		self.stationSoul_p.need_recount = True
	
	def SetStationID(self, stationId):
		#特殊，设置阵位触发重算属性
		if (self.stationId and not stationId) or (not self.stationId and stationId):
			#上阵或者下阵了
			self.TotalNeedRecount()
		self.stationId = stationId
	
	def ResetRecountZhuanShengFlag(self):
		#设置阵灵属性需要重算
		self.TotalNeedRecount()
		self.zhuanSheng_p.need_recount = True
	
	################################################################################
	#重算主体
	################################################################################
	def RecountAll(self):
		self.RecountBase()
		self.RecountCuiLian()
		self.RecountTarot()
		self.RecountEquipment()
		
		self.RECOUNTARTIFACT()
		
		self.RecountPet()
		self.RecountSkill()
		self.RecountHallows()
		self.RecountTalentCard()
		self.RecountGameUnionLogBuff()
		self.RecountDragonTrain()
		self.RecountFashion()
		self.RecountStarGirl()
		self.RecountCardBuff()
		self.RecountDragonVein()
		self.RecountDragonVeinBuf()
		self.RecountJTMedal()
		self.RecountTitleRole()
		self.RecountMagicSpirit()
		self.RecountZhuanSheng()
		#清零
		self.total_p.p_dict = {}
		self.total_p_coef.p_dict = {}
		self.total_p_h_coef.p_dict = {}
		self.total_p_m.p_dict = {}
		self.total_p_h.p_dict = {}
		
		#绝对值加法
		STA = self.total_p.AddProperty
		STA(self.base_p)
		STA(self.CuiLianBase_p)
		STA(self.tarot_p)
		STA(self.pet_p)
		STA(self.petEvo_p)
		STA(self.skill_p)
		
		STA(self.equipmentBase_p)
		STA(self.equipmentStrengthen_p)
		STA(self.equipmentGem_p)
		STA(self.equipmentWash_p)
		STA(self.equipmentZhuanSheng_p)
		
		STA(self.artifactBase_p)
		STA(self.artifactStrengthen_p)
		STA(self.artifactGem_p)
		STA(self.artifactCuiLian_p)
		
		STA(self.hallowsBase_p)
		STA(self.hallowsGem_p)

		STA(self.talentcard_p)
		STA(self.talentcardsuit_p)
		
		STA(self.GameUnion_p)

		STA(self.fashion_p)
		STA(self.fashionHole_p)
		STA(self.hbuff_p)
		STA(self.starGirl_p)
		
		STA(self.JTMedal_p)
		
		STA(self.magicSpirit_p)
		STA(self.zhuanSheng_p)
		
		#万份比加法
		STCA = self.total_p_coef.AddProperty
		STHCA = self.total_p_h_coef.AddProperty
		STCA(self.skill_coef_p)
		STCA(self.artifactSuit_p)
		STCA(self.artifactCuiLianSuite_p)
		STCA(self.artifactCuiLianHole_p)
		STCA(self.hallowsCoef_p)
		STCA(self.hallowsShenzao_p)
		STCA(self.fashionSuit_p)
		#(pvp属性)
		STMA = self.total_p_m.AddProperty
		#(隐藏属性)
		STHA = self.total_p_h.AddProperty
		#上阵才会加的属性
		SM = self.mgr
		if self.stationId:
			#翅膀
			STA(SM.wing_p)
			#助阵
			STA(SM.helpstation_p)
			#订婚戒指
			STA(SM.marryRing_p)
			#婚戒
			STA(SM.weddingRing_p)
			#婚戒戒灵
			STA(SM.weddingRingS_p)
			#婚技能
			STA(SM.weddingRingSkill_p)
			#时装鉴定属性
			STA(SM.fashionglobal_p)
			#亲密等级
			STA(SM.qinmi_p)
			#亲密品阶
			STA(SM.qinmiGrade_p)
			#公会技能
			STA(SM.unionSkill_p)
			#战阵基础属性
			STA(SM.warStationbase_p)
			#战阵战魂石属性
			STA(SM.warStationItem_p)
			#战阵万分比属性
			STCA(SM.warStationThousand_p)
			#阵灵基础属性 && 万分比属性
			STA(SM.stationSoulBase_p)
			STCA(SM.stationSoulPTT_p)
			#阵灵强化石属性
			STA(SM.stationSoulItem_p)
			#转生光环基础属性
			STA(SM.zhuanshengHaloBase_p)
			#卡牌图鉴全队属性
			STA(SM.cardAtlas_p)
			#卡牌图鉴全队万分比属性
			STCA(SM.cardAtlasSuit_coef_p)
			#元素之灵基础属性
			STA(SM.elementSpiritBase_p)
			#元素之灵属性万分比
			STCA(SM.elementSpiritPTT_p)
			#元素印记属性万分比 PS 印记的基本属性就是万分比的方式
			STCA(SM.elementBrandBase_p)
			#圣印基础属性
			STA(SM.sealBase_p)
			#圣印属性万分比
			STCA(SM.sealPTT_p)
			#印记洗练属性
			STA(SM.elementBrandWash_p)
			#==================================================
			#(pvp属性)
			#==================================================
			#坐骑(pvp属性)
			STMA(SM.mountBase_p)
			#坐骑外形品质(pvp属性)
			STMA(SM.mountApp_p)
			#神龙(pvp属性)
			STMA(SM.dragon_p)
			#称号主角(pvp属性)
			STMA(self.titleRole_p)
			#称号全队属性(pvp属性)
			STMA(SM.titleTeam_p)
			
			#==================================================
			#(称号隐藏属性--只在pvp中生效)
			#==================================================
			#称号个人
			STHA(self.titleRoleEx_p)
			STHA(SM.titleTeamEx_p)
			#称号全队
			STHCA(self.titleRoleEx_coef_p)
			STHCA(SM.titleTeamEx_coef_p)
			#==================================================
			#婚戒戒灵(攻击加成,万份比)
			STCA(SM.weddingRingS_coef)
			#==================================================
		#总的属性进行运算
		STMA(self.total_p)
		#pvp属性 + 隐藏属性
		STHA(self.total_p_m)
		
		#清理特殊属性(物攻法攻)
		if self.heroId == 0 or self.career == 1:
			#主角或者是防守英雄，删除法攻
			self.total_p.DelProperty(PropertyEnum.attack_m)
			self.total_p_m.DelProperty(PropertyEnum.attack_m)
			self.total_p_h.DelProperty(PropertyEnum.attack_m)
		else:
			#法攻英雄
			self.total_p.DelProperty(PropertyEnum.attack_p)
			self.total_p_m.DelProperty(PropertyEnum.attack_p)
			self.total_p_h.DelProperty(PropertyEnum.attack_p)
		
		#驯龙属性（只加主角，除龙脉buf不参与万分比计算）
		if self.heroId == 0:
			STMA(self.dragonTrain_p)
			STMA(self.dragonVein_p)
			STCA(self.dragonVeinBuf_p)
			STHA(self.dragonTrain_p)
			STHA(self.dragonVein_p)
		
		STHCA(self.total_p_coef)
		
		#万分比属性计算
		self.total_p.PercentProperty(self.total_p_coef)
		self.total_p_m.PercentProperty(self.total_p_coef)
		#隐藏属性与隐藏万分比计算
		self.total_p_h.PercentProperty(self.total_p_h_coef)
		#重算战斗力
		RecountZDLFun(self)
		
		self.SyncData()
		#重算完毕
		self.need_recount = False
	################################################################################



	################################################################################
	#每一个属性结构的重算规则定义
	################################################################################
	def RecountBase(self):
		#重算基础属性
		self.base_p.GoToRecount(self)
	def RecountCuiLian(self):
		#重算淬炼基础属性
		self.CuiLianBase_p.GoToRecount(self)
	def RecountTarot(self):
		#重算占卜属性
		self.tarot_p.GoToRecount(self)

	def RecountPet(self):
		#重算宠物属性
		self.pet_p.GoToRecount(self)
		self.petEvo_p.GoToRecount(self)
		
	def RecountEquipment(self):
		#装备
		self.equipmentBase_p.GoToRecount(self)
		self.equipmentStrengthen_p.GoToRecount(self)
		self.equipmentGem_p.GoToRecount(self)
		self.equipmentWash_p.GoToRecount(self)
		self.equipmentZhuanSheng_p.GoToRecount(self)
	
	def RecountArtifact(self):
		#神器(注意其他多语言版本的修复问题)
		self.artifactBase_p.GoToRecount(self)
		self.artifactStrengthen_p.GoToRecount(self)
		self.artifactGem_p.GoToRecount(self)
		self.artifactCuiLian_p.GoToRecount(self)
		self.artifactCuiLianSuite_p.GoToRecount(self)
		self.artifactCuiLianHole_p.GoToRecount(self)
		if self.artifactSuit_p.GoToRecount(self) is True:
			#神器套装BUG兼容@黄伟奇2014.7.7
			#因为一次代码错误，导致强化属性加到了套装属性上面
			#所以做了一个措施就是还是这么做，但是加上一个最大加成限制
			#攻击加成最多18.95%  生命加成最多31.74%
			#(限制规则中不包含原来的套装属性加成)
			#只有套装属性重算的时候才会跑这段逻辑，强化是不会触发了，做成和旧系统一样
			SAPG = self.artifactStrengthen_p.p_dict.get
			SAP = self.artifactSuit_p.p_dict
			for pt, pv in SAP.items():
				st_pv = SAPG(pt)
				if not st_pv:
					continue
				if pt == PropertyEnum.attack_p or pt == PropertyEnum.attack_m:
					st_pv = min(1895, st_pv)
					SAP[pt] = pv + st_pv
				elif pt == PropertyEnum.maxhp:
					st_pv = min(3174, st_pv)
					SAP[pt] = pv + st_pv
	
	def RecountArtifact_Ex(self):
		#北美，繁体的神器，修复了套装属性的BUG
		self.artifactBase_p.GoToRecount(self)
		self.artifactStrengthen_p.GoToRecount(self)
		self.artifactGem_p.GoToRecount(self)
		self.artifactSuit_p.GoToRecount(self)
		self.artifactCuiLian_p.GoToRecount(self)
		self.artifactCuiLianSuite_p.GoToRecount(self)
		self.artifactCuiLianHole_p.GoToRecount(self)
	

	def RecountSkill(self):
		#技能
		self.skill_p.GoToRecount(self)
		self.skill_coef_p.GoToRecount(self)
	
	def RecountHallows(self):
		#圣器
		self.hallowsBase_p.GoToRecount(self)
		self.hallowsCoef_p.GoToRecount(self)
		self.hallowsShenzao_p.GoToRecount(self)
		self.hallowsGem_p.GoToRecount(self)
		
	def RecountTalentCard(self):
		#天赋卡
		self.talentcard_p.GoToRecount(self)
		self.talentcardsuit_p.GoToRecount(self)
		
	def RecountGameUnionLogBuff(self):
		self.GameUnion_p.GoToRecount(self)
		
	def RecountDragonTrain(self):
		#重算驯龙属性
		self.dragonTrain_p.GoToRecount(self)
	
	def RecountFashion(self):
		#时装
		self.fashion_p.GoToRecount(self)
		self.fashionSuit_p.GoToRecount(self)
		self.fashionHole_p.GoToRecount(self)
		
	def RecountStarGirl(self):
		#重算星灵属性
		self.starGirl_p.GoToRecount(self)
	
	def RecountCardBuff(self):
		#重算变身卡属性
		self.hbuff_p.GoToRecount(self)
	
	def RecountDragonVein(self):
		#重算龙脉属性
		self.dragonVein_p.GoToRecount(self)
	
	def RecountDragonVeinBuf(self):
		#重算龙脉buff(龙脉被动技能)
		self.dragonVeinBuf_p.GoToRecount(self)
	
	def RecountJTMedal(self):
		#重算勋章属性
		self.JTMedal_p.GoToRecount(self)
	
	def RecountTitleRole(self):
		#重算称号的主角属性
		self.titleRole_p.GoToRecount(self)
		self.titleRoleEx_p.GoToRecount(self)
		self.titleRoleEx_coef_p.GoToRecount(self)
		
	def RecountMagicSpirit(self):
		#重算魔灵属性
		self.magicSpirit_p.GoToRecount(self)
	
	def RecountZhuanSheng(self):
		#重算转生属性
		self.zhuanSheng_p.GoToRecount(self)
	
#	def RecountTitleRoleEx(self):
#		#重算称号的主角属性(隐藏属性)
#		self.titleRoleEx_p.GoToRecount(self)
#		self.titleRoleEx_coef_p.GoToRecount(self)
	
if "_HasLoad" not in dir():
	#消息
	Msg_SyncRoleProperty = AutoMessage.AllotMessage("Msg_SyncRoleProperty", "同步主角属性")
	Msg_SyncHeroProperty = AutoMessage.AllotMessage("Msg_SyncHeroProperty", "同步英雄属性")




