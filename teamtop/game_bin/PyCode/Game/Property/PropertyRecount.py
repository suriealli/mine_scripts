#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Property.PropertyRecount")
#===============================================================================
# 属性重算模块
#===============================================================================
import cDateTime
from Common.Other import EnumGameConfig
from Game.Dragon import DragonConfig
from Game.Fight import SkillConfig
from Game.Hero import HeroConfig
from Game.Marry import MarryConfig
from Game.Mount import MountMgr
from Game.Pet import PetConfig
from Game.Property import PropertyEnum
from Game.Role.Config import RoleConfig
from Game.Role.Data import EnumTempObj, EnumObj, EnumInt16, EnumTempInt64, EnumInt1,\
	EnumInt8
from Game.StarGirl import StarGirlDefine, StarGirlConfig
from Game.Wing import WingConfig
from Game.ZDL import ZDL
from Game.Activity.HalloweenAct import HalloweenConfig
from Game.JT import JTMedal
from Game.Union import UnionMagicTower
from Game.Activity.Title import TitleConfig
from Game.Fight.Station import StationConfig
from Game.Role.Obj import Base
from Game.StationSoul import StationSoulConfig
from Game.CardAtlas import CardAtlasConfig
from Game.ElementSpirit import ElementSpiritConfig
from Game.Seal import SealConfig

#助阵英雄加属性枚举类型	血、物攻、法功、战斗力
HelpStationProEnum = [1,4,6,16]

#####################################################################################
def RecountBase(pg, p_dict):
	#单位裸体属性
	if pg.heroId:
		RecountHeroBase(p_dict, pg.owner)
	else:
		RecountRoleBase(p_dict, pg.owner)

def RecountRoleBase(p_dict, role):
	#重算角色裸体属性
	cfg = RoleConfig.RoleBase_Dict.get((role.GetCareer(), role.GetGrade(), role.GetSex()))
	if not cfg:
		print "GE_EXC, error in RecountRoleBase not cfg (%s)" % role.GetRoleID()
		return
	
	PG = p_dict.get
	PA = PropertyEnum.attackspeed
	roleLevel = role.GetLevel()
	for pt, pvData in cfg.p_dict.iteritems():
		cfg_param, cfg_plus, cfg_coe = pvData
		if pt == PA:
			#速度不用除
			p_dict[pt] = PG(pt, 0) + (cfg_param + cfg_plus * roleLevel * cfg_coe)
		else:
			p_dict[pt] = PG(pt, 0) + (cfg_param + cfg_plus * roleLevel * cfg_coe) / 10000


def RecountHeroBase(p_dict, hero):
	#重算英雄裸体属性
	cfg = HeroConfig.Hero_Base_Config.get(hero.onumber)
	if not cfg:
		print "GE_EXC, can not find property cfg in Hero_Base_Config, (%s)" % hero.onumber
		return
		
	heroLevel = hero.GetLevel()
	PG = p_dict.get
	PA = PropertyEnum.attackspeed
	#注意HeroBase 中也运用了这个公式
	#属性公式 (参数都放大了10000倍(为了支持小数，向下取整))
	#(基础属性 + 成长 * 英雄等级 * 系数) / 10000
	for pt, pvData in cfg.p_dict.iteritems():
		cfg_param, cfg_plus, cfg_coe = pvData
		if pt == PA:
			#速度不用除
			p_dict[pt] = PG(pt, 0) + (cfg_param + cfg_plus * heroLevel * cfg_coe)
		else:
			p_dict[pt] = PG(pt, 0) + (cfg_param + cfg_plus * heroLevel * cfg_coe) / 10000
	
	for pt, pv in hero.cfg.p_dict_z.iteritems():
		p_dict[pt] = PG(pt, 0) + pv


def RecountZhuanShengPro(pg, p_dict):
	if pg.heroId:
		RecountHeroZhuanShengPro(p_dict, pg.owner)
	else:
		RecountRoleZhuanShengPro(p_dict, pg.owner)


def RecountHeroZhuanShengPro(p_dict, hero):
	addi = hero.role.GetZhuanShengHaloAddi()
	PG = p_dict.get
	for pt, pv in hero.cfg.p_dict_z.iteritems():
		p_dict[pt] = PG(pt, 0) + pv
	
	#如果是上阵英雄还要加上光环对转生部分属性的加成属性
	if hero.GetStationID():
		for pta, pva in hero.cfg.p_dict_z.iteritems():
			p_dict[pta] = PG(pta, 0) + pva * addi / 10000
		

def RecountRoleZhuanShengPro(p_dict, role):
	zhuanShengLv = role.GetZhuanShengLevel()
	zsCfg = HeroConfig.RoleZhuanShengConfigDict.get(zhuanShengLv)
	if not zsCfg:
		print "GE_EXC, error in RoleZhuanShengConfigDict not cfg (%s) for key(%s)" % (role.GetRoleID(), zhuanShengLv)
		return
	
	addi = role.GetZhuanShengHaloAddi()
	PG = p_dict.get
	for pt, pv in zsCfg.property_dict.iteritems():
		p_dict[pt] = PG(pt, 0) + pv * (10000 + addi) / 10000


def RecountCuiLianBase(pg, p_dict):
	#淬炼增加裸体属性
	if pg.heroId:
		CuiLianHero(p_dict, pg.owner)
	else:
		CuiLianRole(p_dict, pg.owner)

def CuiLianHero(p_dict, hero):
	#淬炼增加基础属性
	CuiLian_Num = hero.GetCuiLian()
	CuiLian_Dict = HeroConfig.CuiLianShi_Dict
	for p, v in CuiLian_Dict.items():
		#基础属性
		p_dict[p] = p_dict.get(p, 0) + v * CuiLian_Num

def CuiLianRole(p_dict, role):
	#淬炼增加基础属性
	CuiLian_Num = role.GetObj(EnumObj.En_RoleCuiLian).get(1, 0)
	CuiLian_Dict = HeroConfig.CuiLianShi_Dict
	for p, v in CuiLian_Dict.items():
		#基础属性
		p_dict[p] = p_dict.get(p, 0) + v * CuiLian_Num

def RecountEquipmentBase(propertyGather, p_dict):
	#装备基础属性
	equipmentMgr = propertyGather.owner.GetEquipmentMgr()
	if not equipmentMgr:
		return
	
	PG = p_dict.get
	for equipment in equipmentMgr.objIdDict.itervalues():
		#基础属性
		for p, v in equipment.cfg.p_dict.iteritems():
			p_dict[p] = PG(p, 0) + v
	#套装属性
	for pt, pv in equipmentMgr.GetStrengthenSuitDict().iteritems():
		p_dict[pt] = PG(pt, 0) + pv
	
def RecountEquipmentZhuanSheng(propertyGather, p_dict):
	#装备转生获得的  光环  属性加成
	equipmentMgr = propertyGather.owner.GetEquipmentMgr()
	if not equipmentMgr:
		return
	#转生  光环  属性加成
	for equipment in equipmentMgr.objIdDict.itervalues():
		if not equipment.cfg.ZhuanShengLevel:
			continue
		for pt, pv in equipment.cfg.p_dict.iteritems():
			p_dict[pt] = pv * propertyGather.role.GetZhuanShengHaloAddi() / 10000
			
def RecountEquipmentStrengthen(propertyGather, p_dict):
	#装备强化属性
	equipmentMgr = propertyGather.owner.GetEquipmentMgr()
	if not equipmentMgr:
		return
	PG = p_dict.get
	#强化属性
	for equipment in equipmentMgr.objIdDict.itervalues():
		for pt, pv in equipment.GetStrengthenP_Dict().iteritems():
			p_dict[pt] = PG(pt, 0) + pv

def RecountEquipmentGem(propertyGather, p_dict):
	#宝石属性
	equipmentMgr = propertyGather.owner.GetEquipmentMgr()
	if not equipmentMgr:
		return
	PG = p_dict.get
	for equipment in equipmentMgr.objIdDict.itervalues():
		for pt, pv in equipment.GetGemPropertyDict().iteritems():
			p_dict[pt] = PG(pt, 0) + pv

def RecountEquipmentWash(propertyGather, p_dict):
	#装备洗练属性
	equipmentMgr = propertyGather.owner.GetEquipmentMgr()
	if not equipmentMgr:
		return
	PG = p_dict.get
	for equipment in equipmentMgr.objIdDict.itervalues():
		for pt, pv in equipment.GetWashPropValue().iteritems():
			p_dict[pt] = PG(pt, 0) + pv
	
def RecountArtifactBase(propertyGather, p_dict):
	#神器基础属性
	ArtifactMgr = propertyGather.owner.GetArtifactMgr()
	if not ArtifactMgr:
		return
	PG = p_dict.get
	for Artifact in ArtifactMgr.objIdDict.itervalues():
		for pt, pv in Artifact.cfg.p_dict.iteritems():
			p_dict[pt] = PG(pt, 0) + pv
	
def RecountArtifactStrengthen(propertyGather, p_dict):
	#神器强化属性
	ArtifactMgr = propertyGather.owner.GetArtifactMgr()
	if not ArtifactMgr:
		return
	#神器强化属性
	PG = p_dict.get
	for Artifact in ArtifactMgr.objIdDict.itervalues():
		for pt, pv in Artifact.GetStrengthenP_Dict().iteritems():
			p_dict[pt] = PG(pt, 0) + pv

def RecountArtifactGem(propertyGather, p_dict):
	#符石属性
	ArtifactMgr = propertyGather.owner.GetArtifactMgr()
	if not ArtifactMgr:
		return
	PG = p_dict.get
	for Artifact in ArtifactMgr.objIdDict.itervalues():
		for pt, pv in Artifact.GetGemPropertyDict().iteritems():
			p_dict[pt] = PG(pt, 0) + pv

def RecountArtifactSuit(propertyGather, p_dict):
	#神器套装属性（万分比）
	ArtifactMgr = propertyGather.owner.GetArtifactMgr()
	if not ArtifactMgr:
		return
	#套装属性
	PG = p_dict.get
	for pt, pv in ArtifactMgr.GetSuitDict().iteritems():
		p_dict[pt] = PG(pt, 0) + pv
	
def RecountArtifactCuiLian(propertyGather, p_dict):
	#神器淬炼基础属性
	ArtifactMgr = propertyGather.owner.GetArtifactMgr()
	if not ArtifactMgr:
		return
	from Game.Item.ItemConfig import ArtifactCuiLianBase_Dict
	for Artifact in ArtifactMgr.objIdDict.itervalues():
		key = (Artifact.cfg.posType, Artifact.GetCuiLianLevel())
		property_Obj = ArtifactCuiLianBase_Dict.get(key)#获取神器淬炼基础属性配置
		if not property_Obj:
			print 'GE_EXC, RecountArtifactCuiLian can not find the configuration where key = (%s, %s)' % key
			return
		p_dict[property_Obj.pt1] = p_dict.get(property_Obj.pt1, 0) + property_Obj.pv1
		p_dict[property_Obj.pt2] = p_dict.get(property_Obj.pt2, 0) + property_Obj.pv2
	
def RecountArtifactCuiLianSuite(propertyGather, p_dict):
	#神器淬炼套装万分比属性加成属性
	ArtifactMgr = propertyGather.owner.GetArtifactMgr()
	if not ArtifactMgr:
		return
	#神器淬炼组合属性
	for pt, pv in ArtifactMgr.GetCuiLianSuitDict().iteritems():
		p_dict[pt] = p_dict.get(pt, 0) + pv
		
def RecountArtifactCuiLianHole(propertyGather, p_dict):
	#神器淬炼光环万分比属性加成属性
	ArtifactMgr = propertyGather.owner.GetArtifactMgr()
	if not ArtifactMgr:
		return
	#神器淬炼光环属性
	for pt, pv in ArtifactMgr.GetCuiLianHoleDict().iteritems():
		p_dict[pt] = p_dict.get(pt, 0) + pv
def RecountSkill(propertyGather, p_dict):
	#技能加绝对值属性
	#只有英雄有
	heroId = propertyGather.heroId
	if not heroId:
		return
	PG = p_dict.get
	SPG = SkillConfig.PassiveSkillConfig_Dict.get
	hero = propertyGather.owner
	for skillId, _ in hero.GetPassiveSkill():
		cfg = SPG(skillId)
		if not cfg:
			continue
		for pt, pv in cfg.property_dict.iteritems():
			p_dict[pt] = PG(pt, 0) + pv


def RecountSkillCoef(propertyGather, p_dict):
	#技能加万份比属性
	#只有英雄有
	heroId = propertyGather.heroId
	if not heroId:
		return
	PG = p_dict.get
	SPG = SkillConfig.PassiveSkillConfig_Dict.get
	hero = propertyGather.owner
	for skillId, _ in hero.GetPassiveSkill():
		cfg = SPG(skillId)
		if not cfg:
			continue
		for pt, pv in cfg.property_p_dict.iteritems():
			p_dict[pt] = PG(pt, 0) + pv

def RecountTarot(propertyGather, p_dict):
	#重算主角占卜属性
	TM = propertyGather.role.GetTempObj(EnumTempObj.enTarotMgr)
	heroId = propertyGather.heroId
	td = {}
	if not propertyGather.stationId:
		return
	if not heroId:
		td = TM.GetOwnerTarotDict(2)
		if not td : return
	else:
		td = TM.GetOwnerTarotDict(heroId)
		if not td : return
	
	PG = p_dict.get
	for card in td.itervalues():
		#第一个属性
		pt = card.card_cfg.pt
		p_dict[pt] = PG(pt, 0) + card.GetPropertyValue()
		#第二个属性
		pt2 = card.card_cfg.pt2
		p_dict[pt2] = PG(pt2, 0) + card.GetPropertyValue_2()

def RecountEvoPet(propertyGather, p_dict):
	#重算宠物进化属性
	pet = propertyGather.owner.GetPet()
	if not pet:
		return
	PG = p_dict.get
	for pt, pv in pet.GetPetEvoPro().iteritems():
		p_dict[pt] = PG(pt, 0) + pv
	
def RecountPet(propertyGather, p_dict):
	pet = propertyGather.owner.GetPet()
	if not pet:
		return
	#增加宠物属性
	petSoulPropertyDict = {}	#宠物之灵属性字典{属性枚举：属性增加百分比}
	#宠物之灵属性
	PPG = PetConfig.PET_SOUL_BASE.get
	PPPG = PetConfig.PET_SOUL_POS_TO_PROPERTY_ENUM.get
	PAP = PropertyEnum.attack_p
	PAM = PropertyEnum.attack_m
	for pos, coding in pet.soul_dict.iteritems():
		soulConfig = PPG(coding)
		if not soulConfig:
			continue
		
		#攻击属性需要特殊判断
		if pos == 1:
			if PAP in pet.property_dict:
				petSoulPropertyDict[PAP] = soulConfig.propertyPercentage
			elif PAM in pet.property_dict:
				petSoulPropertyDict[PAM] = soulConfig.propertyPercentage
			continue
		
		#其它属性
		propertyEnum = PPPG(pos)
		if not propertyEnum:
			continue
		petSoulPropertyDict[propertyEnum] = soulConfig.propertyPercentage
	
	career = propertyGather.owner.GetCareer()
	
	isMagic = True
	if not propertyGather.heroId or career == 1:
		isMagic = False
	PG = p_dict.get
	for pt, pv in pet.property_dict.iteritems():
		if isMagic is False and pt == 6:
			continue
		if isMagic is True and pt == 4:
			continue
		#判断是否有宠物之灵加成(百分比)
		if pt in petSoulPropertyDict:
			pv += int(pv * petSoulPropertyDict[pt] / 100)
		p_dict[pt] = PG(pt, 0) + pv
	
	#计算战斗力
	p_dict[PropertyEnum.zdl] = ZDL.GetZDL_Dict(p_dict)


def RecountHallows(propertyGather, p_dict):
	#重算圣器基础属性
	HallowsMgr = propertyGather.owner.GetHallowsMgr()
	if not HallowsMgr:
		return
	PG = p_dict.get
	for hallows in HallowsMgr.objIdDict.itervalues():
		#基础属性
		for pt, pv in hallows.GetHallowsBasePDICT().iteritems():
			p_dict[pt] = PG(pt, 0) + pv


def RecountHallowsCoef(propertyGather, p_dict):
	#重算圣器万分比属性
	HallowsMgr = propertyGather.owner.GetHallowsMgr()
	if not HallowsMgr:
		return
	PG = p_dict.get
	for hallows in HallowsMgr.objIdDict.itervalues():
		#万分比属性
		for pt, pv in hallows.GetHallowsCoefPDict().iteritems():
			p_dict[pt] = PG(pt, 0) + pv


def RecountHallowsShenzao(propertyGather, p_dict):
	#重算圣器神造属性
	HallowsMgr = propertyGather.owner.GetHallowsMgr()
	if not HallowsMgr:
		return
	PG = p_dict.get
	for hallows in HallowsMgr.objIdDict.itervalues():
		#万分比属性
		for pt, pv in hallows.GetHallowsShenzaoPDict().iteritems():
			p_dict[pt] = PG(pt, 0) + pv


def RecountHallowsGem(propertyGather, p_dict):
	#圣器雕纹属性
	hallowsMgr = propertyGather.owner.GetHallowsMgr()
	if not hallowsMgr:
		return
	PG = p_dict.get
	for hallows in hallowsMgr.objIdDict.itervalues():
		for pt, pv in hallows.GetGemPropertyDict().iteritems():
			p_dict[pt] = PG(pt, 0) + pv

def RecountRoleTalent(propertyGather, p_dict):
	#重算天赋卡属性
	TalentCardMgr = propertyGather.role.GetTempObj(EnumTempObj.TalentCardMgr)
	heroId = propertyGather.heroId
	cardDict = {}
	if not propertyGather.stationId:
		return
	if not heroId:
		cardDict = TalentCardMgr.GetOwnerDict(2)
	else:
		cardDict = TalentCardMgr.GetOwnerDict(heroId)
		if not cardDict:
			return
	PG = p_dict.get
	for card in cardDict.itervalues():
		for pt, pv in card.GetPropertyValue().iteritems():
			p_dict[pt] = PG(pt, 0) + pv
	
def RecountSuitTalent(propertyGather, p_dict):
	#重算天赋卡套装属性
	TalentCardMgr = propertyGather.role.GetTempObj(EnumTempObj.TalentCardMgr)
	heroId = propertyGather.heroId
	owner_suitId = 0
	if not heroId:
		owner_suitId = 2
	else:
		owner_suitId = heroId
	PG = p_dict.get
	for pt, pv in TalentCardMgr.GetSuitPro(owner_suitId).iteritems():
		p_dict[pt] = PG(pt, 0) + pv
		
def RecountGameUnionLogBuff(propertyGather, p_dict):
	#重算游戏联盟平台登录buff
	role = propertyGather.role
	buff_dict = {}
	if role.GetTI64(EnumTempInt64.IsGameUnionAiWan) == 1 and role.GetI1(EnumInt1.GameUnionBuff_Aiwan) == 1:
		buff_dict = EnumGameConfig.GameUnionAiWanBuff
	elif role.GetTI64(EnumTempInt64.IsGameUnionQQGJ) == 1 and role.GetI1(EnumInt1.GameUnionBuff_QQGJ) == 1:
		buff_dict = EnumGameConfig.GameUnionQQGJBuff
	if buff_dict:
		PG = p_dict.get
		for pt, pv in buff_dict.iteritems():
			p_dict[pt] = PG(pt, 0) + pv

def RecountRoleFashion(propertyGather, p_dict):
	#重算所有激活的时装基础属性，只有主角有
	if propertyGather.heroId:
		return
	FashionMgr = propertyGather.owner.GetTempObj(EnumTempObj.enRoleFashionGlobalMgr)
	if not FashionMgr:
		return
	PG = p_dict.get
	for pt, pv in FashionMgr.GetAllBasePro().iteritems():
		#基础属性
		p_dict[pt] = PG(pt, 0) + pv
	
def RecountRoleFashionHole(propertyGather, p_dict):
	#重算时装光环属性，只有主角有
	if propertyGather.heroId:
		return
	FashionMgr = propertyGather.owner.GetTempObj(EnumTempObj.enRoleFashionGlobalMgr)
	if not FashionMgr:
		return
	PG = p_dict.get
	for pt, pv in FashionMgr.GetHaloPro().iteritems():
		p_dict[pt] = PG(pt, 0) + pv
	
def RecountRoleFashionSuit(propertyGather, p_dict):
	#重算时装套装属性，只有主角有
	if propertyGather.heroId:
		return
	FashionGlobalMgr = propertyGather.owner.GetTempObj(EnumTempObj.enRoleFashionGlobalMgr)
	if not FashionGlobalMgr:
		return
	PG = p_dict.get
	for pt, pv in FashionGlobalMgr.GetSuitPro().iteritems():
		p_dict[pt] = PG(pt, 0) + pv
		
def RecountCardBuff(propertyGather, p_dict):
	#变身卡属性，只算主角的
	if propertyGather.heroId != 0:
		return
	role = propertyGather.role
	
	buffData = role.GetObj(EnumObj.HalloweenData).get(4, {})
	if not buffData:
		return
	nowTime = cDateTime.Seconds()
	PG = p_dict.get
	for buffId, endTime in buffData.items():
		if endTime <= nowTime:#过期就删除
			del buffData[buffId]
			continue
		buffConfig = HalloweenConfig.CARD_BUFF_DICT.get(buffId)
		if not buffConfig:
			continue
		for pt, pv in buffConfig.property_dict.iteritems():
			p_dict[pt] = PG(pt, 0) + pv
	
###################################################################################
#全局属性
def RecountHelpStation(role, p_dict):
	#助阵位
	sm = role.GetTempObj(EnumTempObj.enStationMgr)
	if not sm:
		return
	
	RG = role.GetHero
	PG = p_dict.get
	SHG = StationConfig.HSMosaicPercent_Dict.get
	SMG = sm.help_station_mosaic.get
	
	global HelpStationProEnum
	
	for station_id, heroId in sm.help_station_to_id.iteritems():
		hero = RG(heroId)
		if not hero:
			continue
		heroLevel = hero.GetLevel()
		for pt, pvData in hero.cfg.p_dict.iteritems():
			if pt not in HelpStationProEnum:
				continue
			cfg_param, cfg_plus, cfg_coe = pvData
			if station_id in (1, 2, 3):
				#主助阵位25%加成
				pv = (cfg_param + cfg_plus * heroLevel * cfg_coe) / 40000
			else:
				#副助阵位10%加成
				pv = (cfg_param + cfg_plus * heroLevel * cfg_coe) / 100000
			
			mosaicLevel = SMG(station_id)
			if mosaicLevel:
				#助阵位镶嵌加成
				mosaicCfg = SHG(mosaicLevel)
				pv = pv * (mosaicCfg.proPercent + 10000) / 10000
			
			p_dict[pt] = PG(pt, 0) + pv
	
		#转生属性
		for pt, pv in hero.cfg.p_dict_z.iteritems():
			if pt not in HelpStationProEnum:
				continue
			if station_id in (1, 2, 3):
				#主助阵位25%加成
				pvz = pv / 4
			else:
				#副助阵位10%加成
				pvz = pv / 10
			
			mosaicLevel = SMG(station_id)
			if mosaicLevel:
				#助阵位镶嵌加成
				mosaicCfg = SHG(mosaicLevel)
				pvz = pvz * (mosaicCfg.proPercent + 10000) / 10000
				
			p_dict[pt] = PG(pt, 0) + pvz
		
	role.SetTempObj(EnumTempObj.HelpStationProperty, p_dict)
	
	
def RecountMount(role, p_dict):
	#坐骑
	PG = p_dict.get
	Attribute_dict = MountMgr.GetAttribute(role)
	for pt, pv in Attribute_dict.iteritems():
		p_dict[pt] = PG(pt, 0) + pv
	
def RecountMountApp(role, p_dict):
	#坐骑外形品质外形属性
	PG = p_dict.get
	App_attribute_dict = MountMgr.GetAppAttrubute(role)
	for pt, pv in App_attribute_dict.iteritems():
		p_dict[pt] = PG(pt, 0) + pv
	
def RecountDragon(role, p_dict):
	'''
	神龙属性
	@param role:
	'''
	skillPoint = role.GetI16(EnumInt16.DragonAllSkillPoint)
	
	#是否满足最小技能点数属性条件
	if skillPoint < DragonConfig.MIN_SKILL_POINT:
		return
	
	#超过最大取最大
	if skillPoint >= DragonConfig.MAX_SKILL_POINT:
		skillPoint = DragonConfig.MAX_SKILL_POINT
	
	propertyConfig = DragonConfig.SKILL_POINT_PROPERTY.get(skillPoint)
	if not propertyConfig:
		return
	PG = p_dict.get
	for pt, pv in propertyConfig.property_dict.iteritems():
		p_dict[pt] = PG(pt, 0) + pv

def RecountWing(role, p_dict):
	'''
	主角翅膀属性
	@param role:
	'''
	wingDict = role.GetObj(EnumObj.Wing)[1]
	wingEvolveDict = role.GetObj(EnumObj.Wing)[2]
	
	PG = p_dict.get
	WWG = WingConfig.WING_BASE.get
	#翅膀基础属性
	for wingId, windDataList in wingDict.iteritems():
		level, _ = windDataList
		config = WWG((wingId, level))
		if not config:
			print "GE_EXC in RecountWing, unknow wing config (%s, %s)" % (wingId, level)
			continue
		
		for pt, pv in config.property_dict.iteritems():
			p_dict[pt] = PG(pt, 0) + pv
	
	#翅膀收集属性
	if len(wingDict) >= 4:
		collect4Config = None
		collect8Config = None
		for config in WingConfig.WING_COLLECT:
			cnt = 0
			for _, windDataList in wingDict.iteritems():
				level, _ = windDataList
				if level >= config.wingLevel:
					cnt += 1
			#4件以上
			if cnt >= 4:
				if collect4Config is None:
					collect4Config = config
			#8件以上
			if cnt >= 8:
				if collect8Config is None:
					collect8Config = config
		#属性只添加最高的那个
		if collect4Config:
			p_dict[PropertyEnum.antibroken] = PG(PropertyEnum.antibroken, 0) + collect4Config.antibroken
		if collect8Config:
			p_dict[PropertyEnum.notbroken] = PG(PropertyEnum.notbroken, 0) + collect8Config.notbroken
	
	WWEG = WingConfig.WING_EVOLVE.get
	#翅膀进阶属性
	for wingId, grade in wingEvolveDict.iteritems():
		if grade == 0:
			continue
		evolveConfig = WWEG((wingId, grade))
		if not evolveConfig:
			print "GE_EXC in RecountWing, unknow wing evolveConfig (%s, %s)" % (wingId, grade)
			continue
		for pt, pv in evolveConfig.property_dict.iteritems():
			p_dict[pt] = PG(pt, 0) + pv
		
	#计算战斗力（因为有战斗力评分对应的翅膀战斗力，所以这里需要计算战斗力）
	p_dict[PropertyEnum.zdl] = ZDL.GetZDL_Dict(p_dict)

def RecountWeddingRing(role, p_dict):
	#婚戒
	weddingRingID = role.GetI16(EnumInt16.WeddingRingID)
	if not weddingRingID:
		return
	cfg = MarryConfig.WeddingRing_Dict.get(weddingRingID)
	if not cfg:
		return
	PG = p_dict.get
	for pt, pv in cfg.p_dict.iteritems():
		p_dict[pt] = PG(pt, 0) + pv
	
	#计算战斗力（因为有战斗力评分对应战斗力，所以这里需要计算战斗力）
	p_dict[PropertyEnum.zdl] = ZDL.GetZDL_Dict(p_dict)
	
def RecountWeddingRingS(role, p_dict):
	#婚戒戒灵(不含攻击力加成)
	weddingRingSPro = role.GetObj(EnumObj.WeddingRingSoulPro)
	if not weddingRingSPro:
		return
	WRSD = weddingRingSPro[1]
	if not WRSD:
		return
	maxValueDict = MarryConfig.WeddingRingSoulPM_Dict
	if not maxValueDict:
		return
	PG = p_dict.get
	MG = maxValueDict.get
	for _, pDict in WRSD.iteritems():
		for pt, pv in pDict.iteritems():
			maxpv = MG(pt)
			if not maxpv:
				continue
			if pt == -16:
				#万份比，不在这里加
				continue
			if pt == 4:
				#物攻法功都加
				p_dict[4] = PG(4, 0) + pv[1] * maxpv / 10000
				p_dict[6] = PG(6, 0) + pv[1] * maxpv / 10000
			else:
				p_dict[pt] = PG(pt, 0) + pv[1] * maxpv / 10000
	
	#计算战斗力（因为有战斗力评分对应战斗力，所以这里需要计算战斗力）
	p_dict[PropertyEnum.zdl] = ZDL.GetZDL_Dict(p_dict)
	
	
def RecountWeddingRingSCoef(role, p_dict):
	#婚戒戒灵(万份比攻击力加成)
	weddingRingSPro = role.GetObj(EnumObj.WeddingRingSoulPro)
	if not weddingRingSPro:
		return
	WRSD = weddingRingSPro[1]
	if not WRSD:
		return
	maxValueDict = MarryConfig.WeddingRingSoulPM_Dict
	if not maxValueDict:
		return
	PG = p_dict.get
	MG = maxValueDict.get
	for _, pDict in WRSD.iteritems():
		for pt, pv in pDict.iteritems():
			if pt != -16:
				continue
			maxpv = MG(pt)
			if not maxpv:
				continue
			p_dict[4] = PG(4, 0) + pv[1] * maxpv / 10000
			p_dict[6] = PG(6, 0) + pv[1] * maxpv / 10000
			#万份比只有一个攻击属性
			break
		
	
def RecountWeddingRingSkill(role, p_dict):
	#夫妻技能
	skillSet = role.GetObj(EnumObj.WeddingRingStarObj).get(3)
	if not skillSet:
		return
	PG = p_dict.get
	MWG = MarryConfig.WeddingSkill_Dict.get
	for skillID in skillSet:
		cfg = MWG(skillID)
		if not cfg:
			continue
		for pt, pv in cfg.p_dict.iteritems():
			p_dict[pt] = PG(pt, 0) + pv
	
	#计算战斗力（因为有战斗力评分对应战斗力，所以这里需要计算战斗力）
	p_dict[PropertyEnum.zdl] = ZDL.GetZDL_Dict(p_dict)
	
def RecountDragonTrain(propertyGather, p_dict):
	#驯龙属性
	#英雄不计算驯龙属性
	if propertyGather.heroId != 0:
		return
	
	role = propertyGather.role
	dragonTrainMgr = role.GetTempObj(EnumTempObj.DragonTrainMgr)
	PG = p_dict.get
	for pt, pv in dragonTrainMgr.get_total_property_dict().iteritems():
		p_dict[pt] = PG(pt, 0) + pv
	
	#计算战斗力（因为有战斗力评分对应战斗力，所以这里需要计算战斗力）
	p_dict[PropertyEnum.zdl] = ZDL.GetZDL_Dict(p_dict)

def RecountFashionGlobal(role, p_dict):
	#时装的鉴定属性
	FashionGlobalMgr = role.GetTempObj(EnumTempObj.enRoleFashionGlobalMgr)
	if not FashionGlobalMgr:
		return
	PG = p_dict.get
	for pt, pv in FashionGlobalMgr.GetIdePro().iteritems():
		p_dict[pt] = PG(pt, 0) + pv

def RecountWStationBasePro(role, p_dict):
	#战阵基础属性（全队）
	WarStationMgr = role.GetTempObj(EnumTempObj.WarStationMgr)
	if not WarStationMgr:
		return
	PG = p_dict.get
	for pt, pv in WarStationMgr.GetStationBasePro().iteritems():
		p_dict[pt] = PG(pt, 0) + pv
	
def RecountWStationThousandPro(role, p_dict):
	#战阵万分比属性（全队）
	WarStationMgr = role.GetTempObj(EnumTempObj.WarStationMgr)
	if not WarStationMgr:
		return
	PG = p_dict.get
	for pt, pv in WarStationMgr.GetStationThousandPro().iteritems():
		p_dict[pt] = PG(pt, 0) + pv
		
def RecountEStationItemPro(role, p_dict):
	#战魂石属性
	WarStationMgr = role.GetTempObj(EnumTempObj.WarStationMgr)
	if not WarStationMgr:
		return
	PG = p_dict.get
	for pt, pv in WarStationMgr.GetWSItemPro().iteritems():
		p_dict[pt] = PG(pt, 0) + pv
	
def RecountStarGirl(propertyGather, p_dict):
	#星灵属性
	
	#英雄不计算星灵属性
	if propertyGather.heroId != 0:
		return
	
	role = propertyGather.role
	PG = p_dict.get
	SPG = StarGirlConfig.POWER_PROPERTY.get
	#星灵之力属性
	for cdEnum, girlId in StarGirlDefine.CD_ENUM_TO_GIRL_ID.iteritems():
		if not role.GetCD(cdEnum):
			continue
		
		powerConfig = SPG(girlId)
		if not powerConfig:
			continue
		for pt, pv in powerConfig.property_dict.iteritems():
			p_dict[pt] = PG(pt, 0) + pv
	
	#计算战斗力（因为有战斗力评分对应战斗力，所以这里需要计算战斗力）
	p_dict[PropertyEnum.zdl] = ZDL.GetZDL_Dict(p_dict)

def RecountDragonVein(propertyGather, p_dict):
	#龙脉
	
	#英雄不计算龙脉属性
	if propertyGather.heroId != 0:
		return
	
	role = propertyGather.role
	
	DragonVeinManager = role.GetTempObj(EnumTempObj.DragonVein)
	PG = p_dict.get
	for pt, pv in DragonVeinManager.GetTotalProperty().iteritems():
		p_dict[pt] = PG(pt, 0) + pv
	
	#计算战斗力（因为有战斗力评分对应战斗力，所以这里需要计算战斗力）
	p_dict[PropertyEnum.zdl] = ZDL.GetZDL_Dict(p_dict)

def RecountDragonVeinBuf(propertyGather, p_dict):
	#龙脉buf(也就是龙脉的被动技能)
	#之所以跟龙脉属性分开是因为龙脉属性仅在部分玩法中生效（跟坐骑一致），而这个buf则要在所有玩法中生效.同时龙脉buf的属性都是万分比属性
	#英雄不计算龙脉buf属性
	if propertyGather.heroId != 0:
		return
	
	role = propertyGather.role
	
	DragonVeinManager = role.GetTempObj(EnumTempObj.DragonVein)
	PG = p_dict.get
	for pt, pv in DragonVeinManager.GetTotalBufProperty().iteritems():
		p_dict[pt] = PG(pt, 0) + pv

	#计算战斗力（因为有战斗力评分对应战斗力，所以这里需要计算战斗力）
	p_dict[PropertyEnum.zdl] = ZDL.GetZDL_Dict(p_dict)


def RecountJTMedal(propertyGather, p_dict):
	if propertyGather.heroId != 0:
		return
	role = propertyGather.role
	propertydict = JTMedal.GetMedalPropertyDict(role)
	
	if not propertydict:
		return
	PG = p_dict.get
	for pt, pv in propertydict.iteritems():
		p_dict[pt] = PG(pt, 0) + pv
	#计算战斗力（因为有战斗力评分对应战斗力，所以这里需要计算战斗力）
	p_dict[PropertyEnum.zdl] = ZDL.GetZDL_Dict(p_dict)

def RecountQinmi(role, p_dict):
	#重算亲密等级属性
	QinmiLevel = role.GetI16(EnumInt16.QinmiLevel)
	if not QinmiLevel:
		return
	cfg = MarryConfig.Qinmi_Dict.get(QinmiLevel)
	if not cfg:
		print 'GE_EXC, RecountQinmi can not find qinmi level %s on role id %s' % (QinmiLevel, role.GetRoleID())
		return
	PG = p_dict.get
	for pt, pv in cfg.p_dict.iteritems():
		p_dict[pt] = PG(pt, 0) + pv
	
def RecountQinmiGrade(role, p_dict):
	#重算亲密度品阶属性
	QinmiGrade = role.GetI8(EnumInt8.QinmiGrade)
	if not QinmiGrade:
		return
	
	cfg = MarryConfig.QinmiGrade_Dict.get(QinmiGrade)
	if not cfg:
		print 'GE_EXC, RecountQinmiGrade can not find qinmi grade %s on role id %s' % (QinmiGrade, role.GetRoleID())
		return
	PG = p_dict.get
	for pt, pv in cfg.p_dict.iteritems():
		p_dict[pt] = PG(pt, 0) + pv

def RecountUnionSkill(role, p_dict):
	propertydict = UnionMagicTower.GetRoleUnionSkillProperty(role)
	if not propertydict:
		return
	PG = p_dict.get
	for pt, pv in propertydict.iteritems():
		p_dict[pt] = PG(pt, 0) + pv
	#计算战斗力
	p_dict[PropertyEnum.zdl] = ZDL.GetZDL_Dict(p_dict)
	


def RecountTitleRole(propertyGather, p_dict):
	#称号主角属性
	if propertyGather.heroId != 0:
		return
	
	role = propertyGather.role
	titleDict = role.GetObj(EnumObj.Title)
	titledatadict = titleDict.get(1)
	if not titledatadict:
		return
	nowSec = cDateTime.Seconds()
	PG = p_dict.get
	TTG = TitleConfig.Title_Dict.get
	TTLG = TitleConfig.TitleLevel_Dict.get
	TTSG = TitleConfig.TitleStar_Dict.get
	for titleId, titledata in titledatadict.iteritems():
		sec, level, _, star = titledata
		if sec < nowSec:
			continue
		cfg = TTG(titleId)
		if not cfg:
			print "GE_EXC, RecountTitleRole not cfg (%s)" % titleId
			continue
		if cfg.pType != 1:
			continue
		levelCfg = TTLG((titleId, level))
		if levelCfg:
			for pt, pv in levelCfg.property_dict.iteritems():
				p_dict[pt] = PG(pt, 0) + pv
		starCfg = TTSG((titleId, star))
		if starCfg: 
			for pt, pv in starCfg.property_dict.iteritems():
				p_dict[pt] = PG(pt, 0) + pv
	
def RecountTitleRoleEx(propertyGather, p_dict):
	#称号主角属性(隐藏属性)
	if propertyGather.heroId != 0:
		return
	
	role = propertyGather.role
	titleDict = role.GetObj(EnumObj.Title).get(1)
	if not titleDict:
		return
	
	nowSec = cDateTime.Seconds()
	PG = p_dict.get
	TTG = TitleConfig.Title_Dict.get
	TTLG = TitleConfig.TitleLevel_Dict.get
	TTSG = TitleConfig.TitleStar_Dict.get
	
	for titleId, titledata in titleDict.iteritems():
		sec, level, _, star = titledata
		if sec < nowSec:
			continue
		cfg = TTG(titleId)
		if not cfg:
			print "GE_EXC, RecountTitleRoleEx not cfg (%s)" % titleId
			continue
		if cfg.pType != 1:
			#主角隐藏属性
			continue
		levelCfg = TTLG((titleId, level))
		if levelCfg:
			for pt, pv in levelCfg.property_dict_2.iteritems():
				p_dict[pt] = PG(pt, 0) + pv
		starCfg = TTSG((titleId, star))
		if starCfg: 
			for pt, pv in starCfg.property_dict_2.iteritems():
				p_dict[pt] = PG(pt, 0) + pv
	
def RecountTitleRoleExCoef(propertyGather, p_dict):
	#重算称号万分比属性
	if propertyGather.heroId != 0:
		return
	
	role = propertyGather.role
	titleDict = role.GetObj(EnumObj.Title).get(1)
	if not titleDict:
		return
	
	nowSec = cDateTime.Seconds()
	PG = p_dict.get
	TTG = TitleConfig.Title_Dict.get
	TTLG = TitleConfig.TitleLevel_Dict.get
	TTSG = TitleConfig.TitleStar_Dict.get
	
	for titleId, titledata in titleDict.iteritems():
		sec, level, _, star = titledata
		if sec < nowSec:
			continue
		cfg = TTG(titleId)
		if not cfg:
			print "GE_EXC, RecountTitleRoleEx not cfg (%s)" % titleId
			continue
		if cfg.pType != 1:
			#主角隐藏属性
			continue
		levelCfg = TTLG((titleId, level))
		if levelCfg:
			for pt, pv in levelCfg.percent_property_dict.iteritems():
				p_dict[pt] = PG(pt, 0) + pv
		starCfg = TTSG((titleId, star))
		if starCfg: 
			for pt, pv in starCfg.percent_property_dict.iteritems():
				p_dict[pt] = PG(pt, 0) + pv
	
def RecountTitleTeam(role, p_dict):
	#称号全队属性
	titleDict = role.GetObj(EnumObj.Title)
	titledatadict = titleDict.get(1)
	if not titledatadict:
		return
	nowSec = cDateTime.Seconds()
	PG = p_dict.get
	TTG = TitleConfig.Title_Dict.get
	TTLG = TitleConfig.TitleLevel_Dict.get
	TTSG = TitleConfig.TitleStar_Dict.get
	for titleId, titledata in titledatadict.iteritems():
		sec, level, _, star = titledata
		if sec < nowSec:
			continue
		cfg = TTG(titleId)
		if not cfg:
			print "GE_EXC, RecountTitleTeam not cfg (%s)" % titleId
			continue
		if cfg.pType != 2:
			continue
		levelCfg = TTLG((titleId, level))
		if levelCfg:
			for pt, pv in levelCfg.property_dict.iteritems():
				p_dict[pt] = PG(pt, 0) + pv
		starCfg = TTSG((titleId, star))
		if starCfg: 
			for pt, pv in starCfg.property_dict.iteritems():
				p_dict[pt] = PG(pt, 0) + pv

def RecountTitleTeamEx(role, p_dict):
	#称号全队属性(隐藏属性)
	titleDict = role.GetObj(EnumObj.Title).get(1)
	if not titleDict:
		return
	
	nowSec = cDateTime.Seconds()
	PG = p_dict.get
	TTG = TitleConfig.Title_Dict.get
	TTLG = TitleConfig.TitleLevel_Dict.get
	TTSG = TitleConfig.TitleStar_Dict.get
	
	for titleId, titledata in titleDict.iteritems():
		sec, level, _, star = titledata
		if sec < nowSec:
			continue
		cfg = TTG(titleId)
		if not cfg:
			print "GE_EXC, RecountTitleTeamEx not cfg (%s)" % titleId
			continue
		if cfg.pType != 2:
			continue
		levelCfg = TTLG((titleId, level))
		if levelCfg:
			for pt, pv in levelCfg.property_dict_2.iteritems():
				p_dict[pt] = PG(pt, 0) + pv
		starCfg = TTSG((titleId, star))
		if starCfg: 
			for pt, pv in starCfg.property_dict_2.iteritems():
				p_dict[pt] = PG(pt, 0) + pv
	
def RecountTitleTeamExCoef(role, p_dict):
	#称号全队万分比属性(隐藏属性)
	titleDict = role.GetObj(EnumObj.Title).get(1)
	if not titleDict:
		return
	
	nowSec = cDateTime.Seconds()
	PG = p_dict.get
	TTG = TitleConfig.Title_Dict.get
	TTLG = TitleConfig.TitleLevel_Dict.get
	TTSG = TitleConfig.TitleStar_Dict.get
	
	for titleId, titledata in titleDict.iteritems():
		sec, level, _, star = titledata
		if sec < nowSec:
			continue
		cfg = TTG(titleId)
		if not cfg:
			print "GE_EXC, RecountTitleTeamEx not cfg (%s)" % titleId
			continue
		if cfg.pType != 2:
			continue
		levelCfg = TTLG((titleId, level))
		if levelCfg:
			for pt, pv in levelCfg.percent_property_dict.iteritems():
				p_dict[pt] = PG(pt, 0) + pv
		starCfg = TTSG((titleId, star))
		if starCfg: 
			for pt, pv in starCfg.percent_property_dict.iteritems():
				p_dict[pt] = PG(pt, 0) + pv
	
def RecountMarryRing(role, p_dict):
	#自己当前佩戴的订婚戒指ID, 是否铭刻
	if role.GetI8(EnumInt8.MarryStatus) != 3:
		#完婚状态属性才生效
		return
	ringIdSet = role.GetObj(EnumObj.En_RoleRing)
	ownRingCoding, ownImprint = 0, 0
	if ringIdSet:
		for ownRingId in ringIdSet:
			break
		ringMgr = role.GetTempObj(EnumTempObj.enRoleRingMgr)
		ownRing= ringMgr.FindProp(ownRingId)
		if not ownRing :
			return
		if ownRing.Obj_Type != Base.Obj_Type_Ring:
			return
		ownRingCoding = ownRing.ReturnCoding()
		ownImprint = ownRing.IsImprint()
	
	otherRingData = role.GetObj(EnumObj.MarryObj).get(6)
	otherRingCoding, otherRingImprintCoding = 0, 0
	if otherRingData:
		otherRingCoding, otherRingImprintCoding = otherRingData
	
	PG = p_dict.get
	#重算属性
	Owncfg = MarryConfig.Ring_Dict.get(ownRingCoding)
	if Owncfg:
		#未铭刻属性
		for pt, pv in Owncfg.p_dict.iteritems():
			p_dict[pt] = PG(pt, 0) + pv
		
		if ownImprint:
			#铭刻属性
			for pt, pv in Owncfg.imp_dict.iteritems():
				p_dict[pt] = PG(pt, 0) + pv
		
	otherCfg = MarryConfig.Ring_Dict.get(otherRingCoding)
	if otherCfg:
		#对方佩戴过的订婚戒指最好订婚戒指属性
		for pt, pv in otherCfg.p_dict.iteritems():
			p_dict[pt] = PG(pt, 0) + pv
	
	otherImprintCfg = MarryConfig.Ring_Dict.get(otherRingImprintCoding)
	if otherImprintCfg:
		#对方佩戴过的订婚戒指最好铭刻属性
		for pt, pv in otherCfg.imp_dict.iteritems():
			p_dict[pt] = PG(pt, 0) + pv

def RecountMagicSpirit(propertyGather, p_dict):
	#魔灵属性
	magicSpiritMgr = propertyGather.owner.GetMagicSpiritMgr()
	if not magicSpiritMgr:
		return
	PG = p_dict.get
	for magicSpirit in magicSpiritMgr.objIdDict.itervalues():
		for pt, pv in magicSpirit.GetPropertyDict().iteritems():
			p_dict[pt] = PG(pt, 0) + pv

def RecountStationSoulBase(role, p_dict):
	#阵灵基础属性
	nowSSId = role.GetI16(EnumInt16.StationSoulId)
	if not nowSSId:
		return
	
	nowCfg = StationSoulConfig.StationSoul_BaseConfig_Dict.get(nowSSId)
	if not nowCfg:
		print "GE_EXC, RecountStationSoulBase:: can not get stationsoul config by stationsoulId(%s) role(%s)" % (nowSSId, role.GetRoleID())
		return
	
	PG = p_dict.get
	for pt, pv in nowCfg.property_dict.iteritems():
		p_dict[pt] = PG(pt, 0) + pv

def RecountStationSoulPTT(role, p_dict):
	#阵灵属性万分比
	nowSSId = role.GetI16(EnumInt16.StationSoulId)
	if not nowSSId:
		return
	
	nowCfg = StationSoulConfig.StationSoul_BaseConfig_Dict.get(nowSSId)
	if not nowCfg:
		print "GE_EXC, RecountStationSoulPTT:: can not get stationsoul config by stationsoulId(%s) role(%s)" % (nowSSId, role.GetRoleID())
		return
	
	PG = p_dict.get
	for pt, pv in nowCfg.ppt_dict.iteritems():
		p_dict[pt] = PG(pt, 0) + pv	

		
def RecountStationSoulItemPro(role, p_dict):
	#阵灵强化石属性
	stationSoulUseCnt = role.GetI16(EnumInt16.StationSoulItemCnt)
	stationSoulItemCfg = StationSoulConfig.StationSoul_ItemConfig_Dict.get(StationSoulConfig.DEFAULT_STATIONSOUL_ITEM)
	if not stationSoulItemCfg:
		print "GE_EXC, RecountStationSoulItemPro::config error can not get stationSoulItemCfg"
		return
	
	PG = p_dict.get
	for pt, pv in stationSoulItemCfg.property_dict.iteritems():
		p_dict[pt] = PG(pt, 0) + pv * stationSoulUseCnt


def RecountZhuanShengHaloBase(role, p_dict):
	#重算转生光环基础属性	
	PG = p_dict.get
	config = HeroConfig.ZhuangShengHaloConfigDict.get(role.GetZhuanShengHaloLevel())
	if not config:
		print "GE_EXC, error while config = ZhuanShengConfig.ZhuangShengHaloConfigDict.get(zhuanShengHaloLv)" % role.GetZhuanShengHaloLevel()
		return
	
	for pt, pv in config.property_dict.iteritems():
		p_dict[pt] = PG(pt, 0) + pv
		
		
def RecountCardAtlas(role, p_dict):
	#图鉴全队属性
	cardAtlasObj = role.GetObj(EnumObj.CardAtlasDict)
	if not cardAtlasObj or 1 not in cardAtlasObj or 2 not in cardAtlasObj:
		return
	
	PG = p_dict.get
	CAGG = CardAtlasConfig.AtlasGrade_Dict.get
	CALG = CardAtlasConfig.AtlasLevel_Dict.get
	CASGG = CardAtlasConfig.AtlasSuitGrade_Dict.get
	
	for suitId, atlasData in cardAtlasObj[2].iteritems():
		minGrade = 0
		for atlasId, data in atlasData.iteritems():
			if atlasId == 0:
				minGrade = data
				continue
			grade, level = data
			
			gCfg = CAGG((atlasId, grade))
			lCfg = CALG(level)
			if not gCfg or not lCfg:
				continue
			
			#图鉴附加属性 = 图鉴品阶属性 + 强化等级属性 * 品阶强化系数
			
			#品阶有的属性才加强化等级属性
			pt_keys = []
			#图鉴品阶属性
			for pt, pv in gCfg.property_dict.iteritems():
				p_dict[pt] = PG(pt, 0) + pv
				pt_keys.append(pt)
			#强化等级属性 * 品阶强化系数 (强化属性在配置表里面已经乘了一百的)
			for pt in pt_keys:
				pv = lCfg.property_dict.get(pt)
				if not pv:
					continue
				p_dict[pt] = PG(pt, 0) + pv * gCfg.addCoef / 10000 / 100
			
		if not minGrade:
			continue
		cfg = CASGG((suitId, minGrade))
		if not cfg:
			continue
		#图鉴组绝对值属性
		for pt, pv in cfg.property_dict.iteritems():
			p_dict[pt] = PG(pt, 0) + pv
	
	
def RecountCardAtlasSuit(role, p_dict):
	#图鉴组全队万分比属性
	cardAtlasObj = role.GetObj(EnumObj.CardAtlasDict)
	if not cardAtlasObj or 1 not in cardAtlasObj or 2 not in cardAtlasObj:
		return
	
	PG = p_dict.get
	CASGG = CardAtlasConfig.AtlasSuitGrade_Dict.get
	
	for suitId, atlasData in cardAtlasObj[2].iteritems():
		minGrade = 0
		for atlasId, data in atlasData.iteritems():
			if atlasId:
				continue
			minGrade = data
		if not minGrade:
			continue
		cfg = CASGG((suitId, minGrade))
		if not cfg:
			continue
		for pt, pv in cfg.percent_property_dict.iteritems():
			p_dict[pt] = PG(pt, 0) + pv
	

def RecountElementSpiritBase(role, p_dict):
	#重算元素之灵基础属性
	elementSpiritCfg = ElementSpiritConfig.ElementSpirit_BaseConfig_Dict.get(role.GetI16(EnumInt16.ElementSpiritId))
	if not elementSpiritCfg:
		print "GE_EXC, RecountElementSpiritBase:: can not get elementSpirit config by ElementSpiritId(%s) role(%s)" % (role.GetI16(EnumInt16.ElementSpiritId), role.GetRoleID())
		return
	
	PG = p_dict.get
	for pt, pv in elementSpiritCfg.property_dict.iteritems():
		p_dict[pt] = PG(pt, 0) + pv


def RecountElementSpiritPTT(role, p_dict):
	#重算元素之灵属性万分比
	elementSpiritCfg = ElementSpiritConfig.ElementSpirit_BaseConfig_Dict.get(role.GetI16(EnumInt16.ElementSpiritId))
	if not elementSpiritCfg:
		print "GE_EXC, RecountElementSpiritPTT:: can not get elementSpirit config by ElementSpiritId(%s) role(%s)" % (role.GetI16(EnumInt16.ElementSpiritId), role.GetRoleID())
		return
	
	PG = p_dict.get
	for pt, pv in elementSpiritCfg.ppt_dict.iteritems():
		p_dict[pt] = PG(pt, 0) + pv	
	

def RecountElementBrandBase(role, p_dict):
	#重算元素印记基础属性
	elementBrandMgr = role.GetElementBrandMgr()
	if not elementBrandMgr:
		return
	
	ppt_dict = elementBrandMgr.get_base_pro()
	PG = p_dict.get
	for pt, pv in ppt_dict.iteritems():
		p_dict[pt] = PG(pt, 0) + pv

def RecountSealBase(role, p_dict):
	#重算圣印基础属性
	SealBaseMgr = role.GetObj(EnumObj.SealData)
	if not SealBaseMgr :
		return
	SealBaseConfig = SealConfig.Seal_BaseConfig_Dict
	PG = p_dict.get
	for _, SealId in SealBaseMgr.iteritems():
		SealBaseCf = SealBaseConfig.get(SealId)
		if not SealBaseCf :
			print "GE_EXC,RecountSealBase:: can not get SealBaseConfig config by SealId(%s) role(%s)" % (SealId, role.GetRoleID())
			continue
		for pt, pv in SealBaseCf.property_dict.iteritems() :
			p_dict[pt] = PG(pt, 0) + pv

def RecountSealPTT(role, p_dict):
	SealBaseMgr = role.GetObj(EnumObj.SealData)
	if not SealBaseMgr :
		return
	SealBaseConfig = SealConfig.Seal_BaseConfig_Dict
	PG = p_dict.get
	for _, SealId in SealBaseMgr.iteritems():
		SealBaseCf = SealBaseConfig.get(SealId)
		if not SealBaseCf :
			print "GE_EXC,RecountSealBase:: can not get SealBaseConfig config by SealId(%s) role(%s)" % (SealId, role.GetRoleID())
			continue
		for pt, pv in SealBaseCf.ppt_dict.iteritems() :
			p_dict[pt] = PG(pt, 0) + pv
			
			
def RecountElementBrandWash(role, p_dict):
	#重算元素印记基础属性
	elementBrandMgr = role.GetElementBrandMgr()
	if not elementBrandMgr:
		return
	
	ppt_dict = elementBrandMgr.get_wash_pro()
	PG = p_dict.get
	for pt, pv in ppt_dict.iteritems():
		p_dict[pt] = PG(pt, 0) + pv
