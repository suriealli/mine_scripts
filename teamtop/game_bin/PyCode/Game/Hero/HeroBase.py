#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Hero.HeroBase")
#===============================================================================
# 英雄基础数据
#===============================================================================
import cProcess
from World import Define
from Common.Other import EnumKick
from Game.Role.Obj import Base, EnumOdata
from Game.Hero import HeroConfig
from Game.Role.Data import EnumObj, EnumTempObj, EnumInt16, EnumInt8
from Game import GlobalMessage
from Game.Role import Event
from Game.Pet import PetConfig
from Game.StationSoul import StationSoulConfig
from Game.ElementSpirit import ElementSpiritConfig

#英雄对象
class Hero(Base.ObjBase):
	Obj_Type = Base.Obj_Type_Hero
	def __init__(self, role, obj, needAfterCreate = False):
		Base.ObjBase.__init__(self, role, obj)
		self.onumber = self.otype
		
	def AfterCreate(self):
		Base.ObjBase.AfterCreate(self)
		
		#属性管理器
		self.CreatePropertyGather()
		self.equipmentMgr = None #装备管理器
		self.ArtifactMgr = None #神器管理器
		self.HallowsMgr = None	#圣器管理器
		self.magicSpiritMgr = None	#魔灵管理器
		
		self.odata[EnumOdata.enPetID] = 0	#宠物ID
		self.odata[EnumOdata.enPetType] = 0	#宠物类型
		
		#更新星级对应最大品阶记录
		sg_dict = self.role.GetObj(EnumObj.StarColor_Dict)
		
		roleStar = self.GetStar()
		colorCode = self.GetColorCode()
		oldMaxColorCode = sg_dict.get(roleStar)
		if not oldMaxColorCode or oldMaxColorCode < colorCode:
			sg_dict[roleStar] = colorCode
			self.role.SendObj(GlobalMessage.Msg_S_StarColorCode, sg_dict)
			
		#获得一个新英雄
		Event.TriggerEvent(Event.Eve_NewHero, self.role, self.onumber)
		
		return True
	
	def AfterLoad_Except(self):
		Base.ObjBase.AfterLoad_Except(self)
		#属性相关
		self.CreatePropertyGather()
		self.equipmentMgr = None #装备管理器
		self.ArtifactMgr = None #神器管理器
		self.HallowsMgr = None #圣器管理器
		self.magicSpiritMgr = None	#魔灵管理器
		
		#宠物ID
		if EnumOdata.enPetID not in self.odata:
			self.odata[EnumOdata.enPetID] = 0
		#宠物类型
		if EnumOdata.enPetType not in self.odata:
			self.odata[EnumOdata.enPetType] = 0
		else:
			#这里做老数据处理，将玩家的宠物类型改为宠物外观，外观ID值从100开始
			petType = self.odata[EnumOdata.enPetType]
			if petType != 0 and petType < 100:
				cfg = PetConfig.PET_EVOLUTION_DICT.get((petType, 1))
				if not cfg:
					print "GE_EXC,can not find petType(%s) and evoid=1 in AfterLoad_Except roleId(%s)" % (petType, self.role.GetRoleID())
					self.role.Kick(False, EnumKick.DataError_Hero)
				else:
					self.odata[EnumOdata.enPetType] = cfg.shapeId
		
		#圣器，新旧系统兼容处理
		heroHallowsDict = self.role.GetObj(EnumObj.En_HeroHallows)
		if self.oid not in heroHallowsDict:
			heroHallowsDict[self.oid] = set()
			
		#魔灵，新旧系统兼容处理
		magicSpiritDict = self.role.GetObj(EnumObj.En_HeroMagicSpirits)
		if self.oid not in magicSpiritDict:
			magicSpiritDict[self.oid] = set()
			
	def CreatePropertyGather(self):
		self.propertyGather =  self.role.CreateHeroProperty(self)
		self.propertyGather.SetStationID(self.GetStationID())
		
	def GetSyncData(self):
		#获取同步数据
		return (self.oid, self.onumber, self.odata)
	
	def GetHeroId(self):
		return self.oid
	
	def GetHeroName(self):
		#获取名字
		return self.cfg.name
	
	def GetCareer(self):
		#获取职业
		return self.cfg.career
		
	def GetType(self):
		#获取类型
		return self.cfg.heroType
	
	def GetStar(self):
		#获取星级
		return self.cfg.star
	
	def GetColorCode(self):
		#获取颜色编码
		return self.cfg.colorCode
	
	def GetGrade(self):
		#获取英雄品阶
		return self.cfg.grade
	
	def GetNumber(self):
		#获取英雄编号
		return self.onumber
	
	
	def GetEquipmentMgr(self):
		#获取装备管理器
		return self.equipmentMgr
	
	def GetArtifactMgr(self):
		#获取神器管理器
		return self.ArtifactMgr
	
	def GetHallowsMgr(self):
		#获取圣器管理器
		return self.HallowsMgr
	
	def GetMagicSpiritMgr(self):
		#获取魔灵管理器
		return self.magicSpiritMgr
	
	def GetPropertyGather(self):
		#获取属性管理器
		return self.propertyGather
	
	
	def GetLevel(self):
		#获取等级
		return self.odata.get(EnumOdata.enHerolevel)
	
	def SetLevel(self, level):
		#设置等级
		self.odata[EnumOdata.enHerolevel] = level

	def GetExp(self):
		#获取经验
		return self.odata.get(EnumOdata.enHeroExp)
	
	def SetExp(self, exp):
		#设置经验
		self.odata[EnumOdata.enHeroExp] = exp

	def GetStationID(self):
		#获取阵位ID
		return self.odata.get(EnumOdata.enStationID)

	def SetStationID(self, value):
		#设置阵位ID
		self.odata[EnumOdata.enStationID] = value
		
		self.propertyGather.SetStationID(value)
	
	def GetHelpStationID(self):
		#获取助阵位ID
		return self.odata.get(EnumOdata.enHelpStationID)
	
	def SetHelpStationID(self, value):
		#设置助阵位ID
		self.odata[EnumOdata.enHelpStationID] = value
		
	def GetPetID(self):
		#获取宠物ID
		return self.odata.get(EnumOdata.enPetID)
	
	def SetPetID(self, petId):
		#设置宠物ID
		self.odata[EnumOdata.enPetID] = petId
		
	def GetPetType(self):
		#获取宠物类型(已更改为外观ID)
		return self.odata.get(EnumOdata.enPetType)
	
	def SetPetType(self, petType):
		#设置宠物类型(已更改为外观ID)
		self.odata[EnumOdata.enPetType] = petType
	
	def UpGrade(self):
		#更新类型、配置
		self.onumber = self.cfg.nextGradeHeroNumber
		self.cfg = HeroConfig.Hero_Base_Config.get(self.cfg.nextGradeHeroNumber)
		
		#更新星级对应最大品阶记录
		sg_dict = self.role.GetObj(EnumObj.StarColor_Dict)
		
		roleStar = self.GetStar()
		colorCode = self.GetColorCode()
		oldMaxColorCode = sg_dict.get(roleStar)
		if not oldMaxColorCode or oldMaxColorCode < colorCode:
			sg_dict[roleStar] = colorCode
			self.role.SendObj(GlobalMessage.Msg_S_StarColorCode, sg_dict)
		
		#获得一个新英雄
		Event.TriggerEvent(Event.Eve_NewHero, self.role, self.onumber)
		
	def GetNormalSkill(self):
		#获取英雄技能
		return self.cfg.normal_skill
	
	def GetActiveSkill(self):
		#获取主动技能
		return self.cfg.learn_activeSkill
	
	def GetPassiveSkill(self):
		#获取被动技能格式[(2127,0), (2128, 0)]
		return self.cfg.learn_passiveSkill
	
	def GetPet(self):
		petId = self.GetPetID()
		if not petId:
			return None
		
		petMgr = self.role.GetTempObj(EnumTempObj.PetMgr)
		
		#找不到对应的宠物
		if petId not in petMgr.pet_dict:
			return  None
		pet = petMgr.pet_dict[petId]
		
		#双向验证
		if pet.hero_id != self.GetHeroId():
			if cProcess.ProcessID not in Define.TestWorldIDs:
				print "GE_EXC, role get pet error pet id not match (%s)" % self.role.GetRoleID()
			return  None
		
		return pet
	
	def GetTalentZDL(self):
		#获取英雄天赋卡技能战斗力
		TalentCardMgr = self.role.GetTempObj(EnumTempObj.TalentCardMgr)
		return TalentCardMgr.GetCardZDL(self.oid)

	def IsPutTalent(self):
		'''英雄是否装备了天赋卡'''
		TalentCardMgr = self.role.GetTempObj(EnumTempObj.TalentCardMgr)
		return TalentCardMgr.GetOwnerDict(self.oid)
	
	def Awaken(self):
		#更新类型、配置
		self.onumber = self.cfg.awakenHeroNumber
		self.cfg = HeroConfig.Hero_Base_Config.get(self.cfg.awakenHeroNumber)
		
		#更新星级对应最大品阶记录
		sg_dict = self.role.GetObj(EnumObj.StarColor_Dict)
		
		roleStar = self.GetStar()
		colorCode = self.GetColorCode()
		oldMaxColorCode = sg_dict.get(roleStar)
		if not oldMaxColorCode or oldMaxColorCode < colorCode:
			sg_dict[roleStar] = colorCode
			self.role.SendObj(GlobalMessage.Msg_S_StarColorCode, sg_dict)
		
		#获得一个新英雄
		Event.TriggerEvent(Event.Eve_NewHero, self.role, self.onumber)
	
	def GetMFZSkill(self):
		'''返回该英雄携带的魔法阵技能'''
		roleMFZData = self.role.GetObj(EnumObj.MFZData)
		mfzSkillList = []
		if 2 in roleMFZData and self.oid in roleMFZData[2]:
			mfzSkillList.append((roleMFZData[2][self.oid][0],roleMFZData[2][self.oid][1]))
			
		return mfzSkillList
	
	def GetMFZSkillPointDict(self):
		'''获取魔法阵技能点字典'''
		skillpointDict = {}
		tmpskillpointList = []
		magicSpiritMgrDict = self.role.GetTempObj(EnumTempObj.enHeroMagicSpiritMgrDict)
		magicSpiritMgr = magicSpiritMgrDict.get(self.oid, None)
		if not magicSpiritMgr:
			return skillpointDict
		
		for _, magicSpirit in magicSpiritMgr.objIdDict.iteritems():
			tmpskillpointList = magicSpirit.GetSavedRefreshSkillPoint()
			if len(tmpskillpointList) == 2:
				st = tmpskillpointList[0]
				sv = tmpskillpointList[1]
				if st in skillpointDict:
					skillpointDict[st] += sv
				else:
					skillpointDict[st] = sv
		
		return skillpointDict
	
	def UpdateAndSyncMFZSkillPassive(self):
		'''
		更新当前魔法阵技能携带状态
		'''
		from Game.MoFaZhen import MoFaZhenMgr
		MoFaZhenMgr.RealUpdateAndSyncMFZSkill(None, self)
	
	def IsPutMagicSpirit(self):
		'''
		判断是否穿戴了魔灵
		'''
		magicSpiritMgrDict = self.role.GetTempObj(EnumTempObj.enHeroMagicSpiritMgrDict)
		magicSpiritMgr = magicSpiritMgrDict.get(self.oid, None)
		if not magicSpiritMgr:
			return False
		
		if len(magicSpiritMgr.objIdDict) < 1:
			return False
		
		return True		
	
	def GetStationSoulSkill(self):
		'''返回该英雄主人的阵灵技能'''
		nowCfg = StationSoulConfig.StationSoul_BaseConfig_Dict.get(self.role.GetI16(EnumInt16.StationSoulId))
		if nowCfg and nowCfg.skillState:
			return nowCfg.skillState
		else:
			return None
	
	def GetMoFaZhen(self):
		'''
		返回英雄魔法阵数据
		'''
		moFaZhenDict = {} 
		
		#魔法阵技能数据
		moFaZhenDict[1] = self.GetMFZSkill()
		#属性数据
		p_dict = {}
		PG = p_dict.get
		magicSpiritMgrDict = self.role.GetTempObj(EnumTempObj.enHeroMagicSpiritMgrDict)
		magicSpiritMgr = magicSpiritMgrDict.get(self.oid, None)
		if magicSpiritMgr:
			for _, magicSpirit in magicSpiritMgr.objIdDict.iteritems():
				pt, pv = magicSpirit.odata[EnumOdata.enMagicSpiritSavedProperty]
				p_dict[pt] = PG(pt, 0) + pv			
			moFaZhenDict[2] = p_dict
			
		return moFaZhenDict
	
	def GetCuiLian(self):
		'''
		返回英雄淬炼次数
		'''
		return self.role.GetObj(EnumObj.En_RoleCuiLian).get(self.oid, 0)
		
	def AddCuiLian(self, msg):
		'''
		增加英雄淬炼次数
		'''
		if msg <= 0:
			return
		if self.GetCuiLian() + msg > self.GetCuiLian_MaxCnt():
			return
		CL_Dict = self.role.GetObj(EnumObj.En_RoleCuiLian) 
		CL_Dict[self.oid] = CL_Dict.get(self.oid, 0) + msg
		
	def GetCuiLian_MaxCnt(self):
		return self.cfg.CuiLianShiCnt
	
	def GetZhuanShengLevel(self):
		return self.cfg.zhuanshengLevel
	
	def ZhuanSheng(self):
		#更新类型、配置
		self.onumber = self.cfg.zhuanshengHeroNumber
		self.cfg = HeroConfig.Hero_Base_Config.get(self.cfg.zhuanshengHeroNumber)
		#更新星级对应最大品阶记录
		sg_dict = self.role.GetObj(EnumObj.StarColor_Dict)
		
		roleStar = self.GetStar()
		colorCode = self.GetColorCode()
		oldMaxColorCode = sg_dict.get(roleStar)
		if not oldMaxColorCode or oldMaxColorCode < colorCode:
			sg_dict[roleStar] = colorCode
			self.role.SendObj(GlobalMessage.Msg_S_StarColorCode, sg_dict)
		#获得一个新英雄
		Event.TriggerEvent(Event.Eve_NewHero, self.role, self.onumber)
	
	def GetElementSpiritSkill(self):
		'''返回该英雄主人的元素之灵技能'''
		elementSpiritCfg = ElementSpiritConfig.ElementSpirit_BaseConfig_Dict.get(self.role.GetI16(EnumInt16.ElementSpiritId))
		if not elementSpiritCfg:
			return None
		
		skillLevel = elementSpiritCfg.skillLevel
		skillType = self.role.GetI8(EnumInt8.ElementSpiritSkillType)
		skillId = ElementSpiritConfig.ElementSpirit_SkillConfig_Dict.get(skillType)
		if not skillId:
			return None
		
		return [(skillId, skillLevel)]