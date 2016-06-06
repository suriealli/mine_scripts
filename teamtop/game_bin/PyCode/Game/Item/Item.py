#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Item.Item")
#===============================================================================
# 物品类模块
#===============================================================================
import cDateTime
import random
from Common.Other import EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Role.Obj import Base, EnumOdata
from Game.Role.Data import EnumObj, EnumInt8
from Game.Item import EquipmentForing, ItemBase, ArtifactForing, HallowsForing
from Game.Item import Gem
from Game.Item import HallowsGem
from Game.Item import ArtifactGem

#普通物品类
class Item(ItemBase.ItemBase):
	Obj_Type = Base.Obj_Type_Item
	def __init__(self, role, obj):
		ItemBase.ItemBase.__init__(self, role, obj)
		self.package = None
	
	def Use(self, cnt):
		#使用物品
		self.package.DecPropCnt(self, cnt)
		if self.cfg.useNeedItem:
			#扣除钥匙
			self.role.DelItem(self.cfg.useNeedItem, cnt)
	
	
#时效性物品(不能叠加)
class TimeItem(ItemBase.ItemBase):
	Obj_Type = Base.Obj_Type_TimeItem
	def __init__(self, role, obj):
		ItemBase.ItemBase.__init__(self, role, obj)
		self.package = None
	
	def AfterCreate(self):
		# 创建调用
		if ItemBase.ItemBase.AfterCreate(self) is False:
			return False
		assert self.cfg.minutes
		
		#初始化过期时间
		self.odata[EnumOdata.enDeadTime] = cDateTime.Minutes() + self.cfg.minutes

	def IsDeadTime(self):
		#是否已经过期了
		return cDateTime.Minutes() > self.odata[EnumOdata.enDeadTime]
	
	def Use(self, cnt):
		#使用物品
		self.package.DecPropCnt(self, cnt)
		if self.cfg.useNeedItem:
			#扣除钥匙
			self.role.DelItem(self.cfg.useNeedItem, cnt)


#时效性物品(可以叠加)
class TimeItemOverlap(ItemBase.ItemBase):
	Obj_Type = Base.Obj_Type_TimeItemOverlap
	def __init__(self, role, obj):
		ItemBase.ItemBase.__init__(self, role, obj)
		self.package = None
	
	def AfterCreate(self):
		# 创建调用
		if ItemBase.ItemBase.AfterCreate(self) is False:
			return False
		assert self.cfg.minutes
		assert self.cfg.canOverlap
		assert self.cfg.timeoutCoding
		
		#初始化过期时间
		self.odata[EnumOdata.enDeadTime] = cDateTime.Minutes() + self.cfg.minutes

	def IsDeadTime(self):
		#是否已经过期了
		return cDateTime.Minutes() > self.odata[EnumOdata.enDeadTime]
	
	def Use(self, cnt):
		#使用物品
		self.package.DecPropCnt(self, cnt)
		if self.cfg.useNeedItem:
			#扣除钥匙
			self.role.DelItem(self.cfg.useNeedItem, cnt)



#装备类
class Equipment(ItemBase.ItemBase):
	Obj_Type = Base.Obj_Type_Equipment
	def __init__(self, role, obj):
		ItemBase.ItemBase.__init__(self, role, obj)
		self.package = None
		#拥有者，角色或者英雄，在背包则是None
		self.owner = None
		#强化属性缓存字典
		self.strengthen_Dict = None
		#宝石属性缓存字典
		self.Gempro_Dict = None
		self.role = role
		
	def AfterCreate(self, needInit = True):
		#先调用父类函数,载入相关配置
		Base.ObjBase.AfterCreate(self)
		#是否需要初始化,区别新装备或者获取了旧的
		if needInit is True:
			#私有数据初始化
			#强化等级，默认0级
			self.odata[EnumOdata.enEquipmertStrengthenLevel] = 0
			#宝石镶嵌
			self.odata[EnumOdata.enEquipmertGemInlayLevelList] = []
			#附魔，默认0级
			self.odata[EnumOdata.enEquipmentEnchantLevel] = 0
			#默认的额外增加的属性条为0
			self.odata[EnumOdata.enEquipmentWashExtendHole] = 0
			#洗练的属性和未保存的属性
			self.odata[EnumOdata.enEquipmentWashProp] = {}
			self.odata[EnumOdata.enEquipmentRefineProp] = {}
			
			from Game.Activity.WonderfulAct import WonderfulActMgr, EnumWonderType
			WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_Inc_Equip, (self.role, self.cfg.coding))
			
	def AfterLoad_Except(self):
		#数据库载入后调用
		Base.ObjBase.AfterLoad_Except(self)
		#缓存拥有者
		if self.package.ObjEnumIndex == EnumObj.En_RoleEquipments:
			self.owner = self.package.role
		elif self.package.ObjEnumIndex == EnumObj.En_HeroEquipments:
			self.owner = self.package.hero
		if EnumOdata.enEquipmentEnchantLevel not in self.odata:
			self.odata[EnumOdata.enEquipmentEnchantLevel] = 0
		if EnumOdata.enEquipmentWashExtendHole not in self.odata:
			self.odata[EnumOdata.enEquipmentWashExtendHole] = 0
		if EnumOdata.enEquipmentWashProp not in self.odata:
			self.odata[EnumOdata.enEquipmentWashProp] = {}
		if EnumOdata.enEquipmentRefineProp not in self.odata:
			self.odata[EnumOdata.enEquipmentRefineProp] = {}
		
	def GetWashExtendHole(self):
		#获取装备额外开启的洗练属性条
		return self.odata.get(EnumOdata.enEquipmentWashExtendHole, 0)
	
	def ReSetWashExtendHole(self):
		#重置装备额外开启的属性条数
		self.odata[EnumOdata.enEquipmentWashExtendHole] = 0
		
	def SetWashExtendHole(self, newHole):
		#设置新的额外开启属性条数
		if self.odata.get(EnumOdata.enEquipmentWashExtendHole) >= newHole:
			return
		#设置装备额外开启的洗练属性条数
		self.odata[EnumOdata.enEquipmentWashExtendHole] = newHole
		
	def GetWashProp(self):
		#获取该装备的洗练数据
		return self.odata.get(EnumOdata.enEquipmentWashProp, {})
	
	def GetWashPropValue(self):
		ptDict = self.odata.get(EnumOdata.enEquipmentWashProp, {})
		EWD = EquipmentForing.Equipment_WashMaxPro_Dict.get
		propDict = {}
		for pt, proportion in ptDict.iteritems():
			maxCfg = EWD(pt)
			if not maxCfg:
				print "GE_EXC,can not find pt(%s) in RequestEquipmentWash" % pt
				return propDict
			pv = int(maxCfg.maxPv * proportion / 10000.0)
			propDict[pt] = pv
		return propDict
	
	def ReSetWashProp(self):
		#重置洗练属性
		self.odata[EnumOdata.enEquipmentWashProp] = {}
		
	def ReSetRefineProp(self):
		#重置未保存的洗练属性
		self.odata[EnumOdata.enEquipmentRefineProp] = {}
		
	def SetWashProp(self, propdict):
		#将未保存属性设置为洗练属性，设置ok后再清理未保存属性
		if not propdict:
			return
		
		self.odata[EnumOdata.enEquipmentWashProp] = propdict
		#重置未保存的洗练属性
		self.odata[EnumOdata.enEquipmentRefineProp] = {}
	
	def GetWashRefineProp(self):
		#获取未保存的洗练属性
		return self.odata.get(EnumOdata.enEquipmentRefineProp, {})
	
	def SetWashRefineProp(self, propdict):
		#设置新的未保存洗练属性
		ptCnt = self.cfg.FreeWash + self.odata.get(EnumOdata.enEquipmentWashExtendHole, 0)
		#保存的属性数量大于该装备实际的数量
		if ptCnt < len(propdict):
			return
		for pv in propdict.values():
			if not pv:
				return
		self.odata[EnumOdata.enEquipmentRefineProp] = propdict
		
	def AddNewWashProp(self, propdict):
		#增加新的洗练属性
		for pt, pv in propdict.iteritems():
			if not pv:
				continue
			if pt in self.odata[EnumOdata.enEquipmentWashProp]:
				continue
			self.odata[EnumOdata.enEquipmentWashProp][pt] = pv
		
	def AddDefineWashPro(self, propdict):
		#增加新的未保存属性
		for pt, pv in propdict.iteritems():
			if not pv:
				continue
			if pt in self.odata[EnumOdata.enEquipmentRefineProp]:
				continue
			self.odata[EnumOdata.enEquipmentRefineProp][pt] = pv
			
	def ResetStrengthen(self):
		#重置强化属性,获取时需要重算
		self.strengthen_Dict = None
	
	def GetStrengthenP_Dict(self):
		#获取强化属性字典
		if self.strengthen_Dict is not None:
			return self.strengthen_Dict
		#重算
		self.strengthen_Dict = {}
		level = self.GetStrengthenLevel()
		if level == 0:
			return self.strengthen_Dict
		#重算强化属性
		key = self.cfg.posType, level
		cfg = EquipmentForing.Strengthen_Dict.get(key)
		if cfg:
			SSD = self.strengthen_Dict
			for pt, pv in cfg.p_dict.iteritems():
				SSD[pt] = pv
			#先将强化属性 * 强化系数，有附魔的话再 * 附魔提升比例
			for pt, pv in SSD.iteritems():
				SSD[pt] = int(pv * self.cfg.StrengthRate / 100.0)
			EnchantLevel = self.odata.get(EnumOdata.enEquipmentEnchantLevel)
			if EnchantLevel > 0:
				EnchanCfg = EquipmentForing.Equipment_Enchant_Dict.get(EnchantLevel)
				if EnchanCfg:
					addPercent = EnchanCfg.AddPercent
					for pt, pv in SSD.iteritems():
						SSD[pt] = int(pv * (1 + addPercent / 100.0))
				else:
					print "GE_EXC,error in GetStrengthenP_Dict, EnchantLevel(%s)" % EnchantLevel
		else:
			print "GE_EXC, error in GetStrengthenP_Dict ,posType(%s),level(%s)" % (self.cfg.posType, level)
		return self.strengthen_Dict
	
	def SetStrengthenLevel(self, level):
		#设置强化等级
		self.odata[EnumOdata.enEquipmertStrengthenLevel] = level
	
	def GetStrengthenLevel(self):
		#获取强化等级
		return self.odata.get(EnumOdata.enEquipmertStrengthenLevel)
	
	def SetEnchantLevel(self, level):
		#设置附魔等级
		self.odata[EnumOdata.enEquipmentEnchantLevel] = level
	
	def GetEnchantLevel(self):
		#获取附魔等级
		return self.odata.get(EnumOdata.enEquipmentEnchantLevel)
	
	def ResetGemPro(self):
		#重置宝石属性，获取时重算
		self.Gempro_Dict = None
		
	def GetGemPropertyDict(self):
		if self.Gempro_Dict is not None:
			return self.Gempro_Dict
		self.Gempro_Dict = {}
		gem_list = self.GetEquipmentGem()
		if not gem_list:
			return self.Gempro_Dict
		
		sealing = self.role.GetI8(EnumInt8.SealingSpiritID)
		
		GEG = Gem.Equipment_Gem_Dict.get
		SG = self.Gempro_Dict
		SGG = self.Gempro_Dict.get
		sealing_cfg = None
		if sealing:
			sealing_cfg = Gem.Sealing_Spirit_Dict.get(sealing)
			if not sealing_cfg:
				print "GE_EXC, error in GetGemPropertyDict 1 not sealing cfg (%s)" % sealing
				return self.Gempro_Dict
		for value in gem_list:
			if len(value) < 3:
				continue
			cfg = GEG(value[0])
			if not cfg:
				print "GE_EXC,can not find coding(%s) in equipmentGem" % value[0]
				continue
			if cfg.pt1 and cfg.pv1:	
				if value[2] >= 6 and sealing_cfg and cfg.GemType not in EnumGameConfig.DEFENCE_TYPE_GEM:#宝石等级大于6级，且封灵等级不为1
					value_pt1 = getattr(sealing_cfg,"add%s" % value[2])
					SG[cfg.pt1] = SGG(cfg.pt1, 0) + int(cfg.pv1*(1 + value_pt1/100.0))
				else:
					SG[cfg.pt1] = SGG(cfg.pt1, 0) + cfg.pv1
			if cfg.pt2 and cfg.pv2:
				if value[2] >= 6 and sealing_cfg and cfg.GemType not in EnumGameConfig.DEFENCE_TYPE_GEM:#宝石等级大于6级，且封灵等级不为1
					value_pt2 = getattr(sealing_cfg,"add%s" % value[2])
					SG[cfg.pt2] = SGG(cfg.pt2, 0) + int(cfg.pv2 * (1 + value_pt2/100.0))
				else:
					SG[cfg.pt2] = SGG(cfg.pt2, 0) + cfg.pv2
		return SG
		
	def GetEquipmentGem(self):
		#获取已镶嵌的宝石
		return self.odata.get(EnumOdata.enEquipmertGemInlayLevelList)
	
	def SetEquipmentGemlist(self, gemlist):
		self.odata[EnumOdata.enEquipmertGemInlayLevelList] = gemlist
		
	def SetEquipmentGem(self, GemCoding, gemType, level):
		#插入宝石镶嵌
		equipmentgem = self.odata.get(EnumOdata.enEquipmertGemInlayLevelList)
		equipmentgem.append([GemCoding, gemType, level])
		
	def LevelUpEquipmentGem(self, index, GemCoding, gemType, level):
		#根据index更改对应项
		equipmentgem = self.odata.get(EnumOdata.enEquipmertGemInlayLevelList)
		if not equipmentgem:
			return
		Ocoding, Otype, _ = equipmentgem[index - 1]
		if Ocoding == GemCoding:
			print "GE_EXC LevelUpEquipmentGem repeat level up (%s)" % self.role.GetRoleID()
			return
		if Otype != gemType:
			print "GE_EXC LevelUpEquipmentGem error (%s)" % self.role.GetRoleID()
			return 
		equipmentgem[index - 1] = [GemCoding, gemType, level]
		
		AutoLog.LogObj(self.role.GetRoleID(), AutoLog.eveLevelEquipmentGem, self.oid, self.otype, self.oint, self.odata, [GemCoding, gemType, level])
	
	def delGembyLocation(self, index):
		#删除某个宝石
		if index < 1:
			return False
		equipmentgem = self.odata.get(EnumOdata.enEquipmertGemInlayLevelList)
		if not equipmentgem:
			return False
		if len(equipmentgem) < index:
			return False
		coding, _, _ = equipmentgem[index - 1]
		del equipmentgem[index - 1]
		return coding
	def CanZhuanSheng(self):
		if self.cfg.zhuanSheng == 0:
			return False
		else:
			return True

	def CanEvolve(self):
		if self.cfg.evolve == 0:
			return False
		else:
			return True

class Artifact(ItemBase.ItemBase):
	Obj_Type = Base.Obj_Type_Artifact
	def __init__(self, role, obj):
		ItemBase.ItemBase.__init__(self, role, obj)
		self.package = None
		#拥有者，角色或者英雄，在背包则是None
		self.owner = None
		#强化属性缓存字典
		self.strengthen_Dict = None
		#宝石属性缓存字典
		self.Gempro_Dict = None
		self.role = role
		
	def AfterCreate(self, needInit = True):
		#先调用父类函数,载入相关配置
		Base.ObjBase.AfterCreate(self)
		#是否需要初始化,区别新装备或者获取了旧的
		if needInit is True:
			#私有数据初始化
			#强化等级，默认0级
			self.odata[EnumOdata.enArtifactStrengthenLevel] = 0
			#宝石镶嵌
			self.odata[EnumOdata.enArtifactGemInlayLevelList] = []
			#神器淬炼
			self.odata[EnumOdata.enArtifactCuiLianLevel] = 0
			self.odata[EnumOdata.enArtifactCuiLianExp] = 0
			self.odata[EnumOdata.enArtifactCuiLianSuit] = []
			
	def AfterLoad_Except(self):
		#数据库载入后调用
		Base.ObjBase.AfterLoad_Except(self)
		#缓存拥有者
		if self.package.ObjEnumIndex == EnumObj.En_RoleArtifact:
			self.owner = self.package.role
		elif self.package.ObjEnumIndex == EnumObj.En_HeroArtifact:
			self.owner = self.package.hero

	def SellPrice(self):
		return self.cfg.price
	
	def ResetStrengthen(self):
		#重置强化属性,获取时需要重算
		self.strengthen_Dict = None
	
	def GetStrengthenP_Dict(self):
		#获取强化属性字典
		if self.strengthen_Dict is not None:
			return self.strengthen_Dict
		#重算
		self.strengthen_Dict = {}
		level = self.GetStrengthenLevel()
		if level == 0:
			return self.strengthen_Dict
		#重算强化属性
		key = self.cfg.coding, level
		cfg = ArtifactForing.Artifact_Strengthen_Dict.get(key)
		if cfg:
			self.strengthen_Dict = cfg.p_dict
		else:
			print "GE_EXC, error in GetStrengthenP_Dict ,posType(%s),level(%s)" % (self.cfg.posType, level)
		return self.strengthen_Dict
	
	def SetStrengthenLevel(self, level):
		#设置强化等级
		self.odata[EnumOdata.enArtifactStrengthenLevel] = level
	
	def GetStrengthenLevel(self):
		#获取强化等级
		return self.odata.get(EnumOdata.enArtifactStrengthenLevel)
	
	def SetCuiLianExp(self, Exp):
		#增加淬炼经验
		if Exp <= self.odata.get(EnumOdata.enArtifactCuiLianExp, 0) :
			return
		self.odata[EnumOdata.enArtifactCuiLianExp] = Exp
	
	def GetCuiLianExp(self):
		#获取淬炼经验
		return self.odata.get(EnumOdata.enArtifactCuiLianExp, 0)
	
	def SetCuiLianLevel(self, msg):
		#设置淬炼等级
		self.odata[EnumOdata.enArtifactCuiLianLevel] = msg
	
	def AddCuiLianLevel(self, msg):
		#增加神器淬炼等级
		self.odata[EnumOdata.enArtifactCuiLianLevel] = self.GetCuiLianLevel() + msg
	
	def GetCuiLianLevel(self):
		#获取神器淬炼等级
		return self.odata.get(EnumOdata.enArtifactCuiLianLevel, 0)
	
	def GetCuiLianSuite(self):
		#获取淬炼组合属性列表
		return self.odata.get(EnumOdata.enArtifactCuiLianSuit, [])
	
	def SetCuiLianSuite(self, msg):
		#设置淬炼组合属性列表
		self.odata[EnumOdata.enArtifactCuiLianSuit] = msg
		
	def ClearCuiLianSuite(self):
		#清除淬炼组合
		self.odata[EnumOdata.enArtifactCuiLianSuit] = []
	def AddCuiLianSuite(self, msg):
		#增加淬炼组合
		CuiLianSuiteList = self.GetCuiLianSuite()
		if not CuiLianSuiteList:
			self.odata[EnumOdata.enArtifactCuiLianSuit] = []
		self.odata[EnumOdata.enArtifactCuiLianSuit].append(msg)
#================================================================================
	def ResetGemPro(self):
		#重置宝石属性，获取时重算
		self.Gempro_Dict = None
		
	def GetGemPropertyDict(self):
		if self.Gempro_Dict is not None:
			return self.Gempro_Dict
		
		self.Gempro_Dict = {}
		gem_list = self.GetArtifactGem()
		if not gem_list:
			return self.Gempro_Dict
		
		SG = self.Gempro_Dict
		sealing = self.role.GetI8(EnumInt8.ArtifactSealingID)
		sealing_cfg = None
		if sealing:
			sealing_cfg = ArtifactGem.Sealing_Spirit_Dict.get(sealing)
			if not sealing_cfg:
				print "GE_EXC, error in GetGemPropertyDict 2 not sealing cfg (%s)" % sealing
				return SG
		
		SGG = self.Gempro_Dict.get
		AAG = ArtifactGem.Artifact_Gem_Dict.get
		for value in gem_list:
			if len(value) < 3:
				continue
			cfg = AAG(value[0])
			if not cfg:
				print "GE_EXC,can not find coding(%s) in ArtifactGem" % value[0]
				continue			
			if cfg.pt1 and cfg.pv1:	
				if value[2] >= 6 and sealing_cfg :#宝石等级大于或等于6级，且封灵等级不为1
					value_pt1 = getattr(sealing_cfg,"add%s" % value[2])
					SG[cfg.pt1] = SGG(cfg.pt1, 0) + int(cfg.pv1*(1 + value_pt1/100.0))
				else:
					SG[cfg.pt1] = SGG(cfg.pt1, 0) + cfg.pv1
			if cfg.pt2 and cfg.pv2:
				if value[2] >= 6 and sealing_cfg :#宝石等级大于6级，且封灵等级不为1
					value_pt2 = getattr(sealing_cfg,"add%s" % value[2])
					SG[cfg.pt2] = SGG(cfg.pt2, 0) + int(cfg.pv2 * (1 + value_pt2/100.0))
				else:
					SG[cfg.pt2] = SGG(cfg.pt2, 0) + cfg.pv2
		return SG
		
	def GetArtifactGem(self):
		#获取已镶嵌的宝石
		return self.odata.get(EnumOdata.enArtifactGemInlayLevelList)
	
	def SetArtifactGemList(self, genlist):
		self.odata[EnumOdata.enArtifactGemInlayLevelList] = genlist
		
	def SetArtifactGem(self, GemCoding, gemType, level):
		#插入宝石镶嵌
		Artifactgem = self.odata.get(EnumOdata.enArtifactGemInlayLevelList)
		Artifactgem.append([GemCoding, gemType, level])
		
	def ChangeArtifactGem(self, index, GemCoding, gemType, level):
		#根据index更改对应项
		Artifactgem = self.odata.get(EnumOdata.enArtifactGemInlayLevelList)
		if not Artifactgem:
			return
		Ocoding, Otype, _ = Artifactgem[index - 1]
		if Ocoding == GemCoding:
			print "GE_EXC LevelUpArtifactGem repeat level up (%s)" % self.role.GetRoleID()
			return
		if Otype != gemType:
			print "GE_EXC LevelUpArtifactGem error (%s)" % self.role.GetROleID()
			return
		Artifactgem[index - 1] = [GemCoding, gemType, level]
		AutoLog.LogObj(self.role.GetRoleID(), AutoLog.eveLevelArtifactGem, self.oid, self.otype, self.oint, self.odata, [GemCoding, gemType, level])	
	
	def delGembyLocation(self, index):
		#删除某个宝石
		if index < 1:
			return
		Artifactgem = self.odata.get(EnumOdata.enArtifactGemInlayLevelList)
		if not Artifactgem:
			return False
		if len(Artifactgem) < index:
			return
		coding, _, _ = Artifactgem[index - 1]
		del Artifactgem[index - 1]
		return coding
	
class Hallows(ItemBase.ItemBase):
	#物品类型为圣器，区分于其他obj
	Obj_Type = Base.Obj_Type_Hallows
	def __init__(self, role, obj):
		#继承父类属性
		ItemBase.ItemBase.__init__(self, role, obj)
		#拥有者，角色或者英雄，在背包为None
		self.owner = None
		#雕纹属性缓存字典
		self.Gempro_Dict = None
		#拥有玩家
		self.role = role

	def AfterCreate(self, needInit = True):
		Base.ObjBase.AfterCreate(self)
		if needInit is True:
			#圣器附魔等级默认为0
			self.odata[EnumOdata.enHallowsEnchants] = 0
			#圣器神造默认等级和经验值均为0
			self.odata[EnumOdata.enHallowsShenzaoLevelAndExp] = [0, 0]
			#圣器雕纹
			self.odata[EnumOdata.enHallowsGemInlayLevelList] = []
			#属性百分比字典初始化为空字典
			self.odata[EnumOdata.enHallowsProp] = {}
			self.odata[EnumOdata.enHallowsRefineProp] = {}
			#获取装备的属性条数(星阶不同，条数不同)
			propcn = self.cfg.inipropcnt
			#获取属性比例字典
			prop_dict = self.odata[EnumOdata.enHallowsProp]
			#消点优化
			rdmoneproplevel = HallowsForing.HallowsInitProplevelRandom.RandomOne
			GET = HallowsForing.HallowsProplevelDict.get
			RDI =  random.randint
			#获取属性列表
			proplist = self.cfg.randomprop.RandomMany(propcn)
			for prop in proplist:
				#如果是百分比属性
				prop_level = rdmoneproplevel()
				percent_tuple = GET(prop_level)
				ptm = self.cfg.ptmax.get(prop)
				prop_dict[prop] = min(RDI(*percent_tuple), ptm)
	

	def GetHallowsBasePDICT(self):
		#获取计算好的圣器基础属性字典
		baseprop_dict = {}
		#获取属性基础字典
		ptbase_dict_get = self.cfg.ptbase.get
		#获取附魔加成
		enchantgain_cfg = HallowsForing.HallowsEnchantDict.get(self.odata[EnumOdata.enHallowsEnchants], None)
		if enchantgain_cfg is None:
			enchantgain = 0
		else:	
			enchantgain = enchantgain_cfg.PropGain
		for k, v in self.odata[EnumOdata.enHallowsProp].iteritems():
			if type(k) != int:
				continue
			#获取属性基值
			ptb = ptbase_dict_get(k)
			#属性实际值
			ptv = ptb * v / 10000.0
			#附魔效果加成
			baseprop_dict[k] = int(ptv * (100 + enchantgain) / 100.0)
		return baseprop_dict
	
	def GetHallowsCoefPDict(self):
		#获取计算好的圣器万分比加成属性字典
		percentprop_dict = {}
		#获取属性基础字典
		ptbase_dict_get = self.cfg.ptbase.get
		#获取附魔加成
		enchantgain_cfg = HallowsForing.HallowsEnchantDict.get(self.odata[EnumOdata.enHallowsEnchants], None)
		if enchantgain_cfg is None:
			enchantgain = 0
		else:	
			enchantgain = enchantgain_cfg.PropGain
		for k, v in self.odata[EnumOdata.enHallowsProp].iteritems():
			if type(k) != str:
				continue
			#获取属性基值
			ptb = ptbase_dict_get(k)
			#属性实际值
			ptv = ptb * v / 10000.0
			#附魔效果加成
			percentprop_dict[int(k[-1])] = int(ptv * (100 + enchantgain) / 100.0)
			
		return percentprop_dict

		
	def GetHallowsShenzaoPDict(self):
		#获取神造万分比属性
		shenzaoCoefPDict = {}
		level, _ = self.GetShenzaoLevelAndExp()
		shenzao_cfg = HallowsForing.HallowShenzaoDict.get(level, None)
		if shenzao_cfg is not None:
			shenzaoProperty = self.cfg.shenzaoProperty
			CPG = shenzaoCoefPDict.get
			for k, v in shenzao_cfg.property_dict.iteritems():
				if k not in shenzaoProperty:
					continue
				shenzaoCoefPDict[k] = CPG(k, 0) + v
		return shenzaoCoefPDict


	def AfterLoad_Except(self):
		#数据库载入后调用
		Base.ObjBase.AfterLoad_Except(self)
		#缓存拥有者
		#如果是在主角的背包中，则拥有者为主角
		if self.package.ObjEnumIndex == EnumObj.En_RoleHallows:
			self.owner = self.package.role
		#如果是在英雄的背包中，则拥有者为英雄
		elif self.package.ObjEnumIndex ==EnumObj.En_HeroHallows:
			self.owner = self.package.hero
		
		self.odata.setdefault(EnumOdata.enHallowsShenzaoLevelAndExp, [0, 0])
		
		self.odata.setdefault(EnumOdata.enHallowsGemInlayLevelList, [])

	def SetEnchantsLevel(self, level):
		#设置附魔等级，附魔等级在必须为0到12
		if not 0 <= level <= 12:
			print "GE_EXC, error set Hallows SetEnchantsLevel level (%s)" % level
			return
		#设置附魔等级
		self.odata[EnumOdata.enHallowsEnchants] = level
	
	def GetEnchantsLevel(self):
		#获取附魔等级
		return self.odata.get(EnumOdata.enHallowsEnchants, 0)
	
	def SetShenzaoLevelAndExp(self, level, exp):
		#设置神造等级
		if not 0 <= level <= self.cfg.maxShenzaoLevel:
			print "GE_EXC,error set Hallows SetShenzaoLevelAndExp level(%s)" % level
			return
		#设置神造等级
		self.odata[EnumOdata.enHallowsShenzaoLevelAndExp] = [level, exp]
	
	def GetShenzaoLevelAndExp(self):
		#获取神造等级
		return self.odata.get(EnumOdata.enHallowsShenzaoLevelAndExp, [0, 0])
	
	def SetPropDict(self, propdict):
		#设置属性字典
		propcnt = self.cfg.inipropcnt

		#属性个数必须与圣器品阶相对应
		if len(propdict) != propcnt:
			print "GE_EXC SetPropDict len(propdict) != propcnt"
			return
		#黄色以下圣器不能设置百分比加成的属性
		if propcnt < 6:
			for prop in propdict.iterkeys():
				if isinstance(prop, str):
					print "GE_EXC, SetPropDict isinstance(prop, str)"
					return
		#属性字典值不能 小于等于0
		for v in propdict.itervalues():
			if not v:
				print "GE_EXC SetPropDict, not v"
				return
		self.odata[EnumOdata.enHallowsProp] = propdict

	def GetPropDict(self):
		#获取属性字典
		return self.odata.get(EnumOdata.enHallowsProp, {})
	
	def GetPropRefineDict(self):
		#获取洗练后未保存的属性字典
		return self.odata.get(EnumOdata.enHallowsRefineProp, {})

	def SetPropRefineDict(self, propdict):
		#设置洗练后未保存属性字典
		propcnt = self.cfg.inipropcnt
		#属性个数必须与圣器品阶相对应
		if len(propdict.keys()) != propcnt:
			return
		#黄色以下圣器不能设置百分比加成的属性
		if propcnt < 6:
			for prop in propdict.iterkeys():
				if isinstance(prop, str):
					return
		#属性字典值不能 小于等于0
		for v in propdict.itervalues():
			if not v:
				return
		self.odata[EnumOdata.enHallowsRefineProp] = propdict

	def ResetPropRefineDict(self):
		#重置洗练后未保存属性
		self.odata[EnumOdata.enHallowsRefineProp] = {}
	
	#===========================================================================
	# 雕纹
	#===========================================================================
	def ResetGemPro(self):
		#重置雕纹属性，获取时重算
		self.Gempro_Dict = None
		
	def GetGemPropertyDict(self):
		if self.Gempro_Dict is not None:
			return self.Gempro_Dict
		
		self.Gempro_Dict = {}
		gem_list = self.GetHallowsGem()
		if not gem_list:
			return self.Gempro_Dict
		
		sealing = self.role.GetI8(EnumInt8.HallowsSealingSpiritID)
		
		HHG = HallowsGem.Hallows_Gem_Dict.get
		SG = self.Gempro_Dict
		SGG = self.Gempro_Dict.get
		
		sealing_cfg = None
		if sealing:
			sealing_cfg = HallowsGem.Hallows_Spirit_Dict.get(sealing)
			if not sealing_cfg:
				print "GE_EXC, error in GetGemPropertyDict 1 not sealing cfg (%s)" % sealing
				return self.Gempro_Dict
			
		for value in gem_list:
			if len(value) < 3:
				continue
			cfg = HHG(value[0])
			if not cfg:
				print "GE_EXC,can not find coding(%s) in HallowsGem" % value[0]
				continue
			if cfg.pt1 and cfg.pv1:	
				if value[2] >= 6 and sealing_cfg:
					value_pt1 = getattr(sealing_cfg,"add%s" % value[2])
					SG[cfg.pt1] = SGG(cfg.pt1, 0) + int(cfg.pv1*(1 + value_pt1/100.0))
				else:
					SG[cfg.pt1] = SGG(cfg.pt1, 0) + cfg.pv1
		return SG
		
	def GetHallowsGem(self):
		#获取已镶嵌的雕纹
		return self.odata.get(EnumOdata.enHallowsGemInlayLevelList)
	
	def SetHallowsGemlist(self, gemlist):
		self.odata[EnumOdata.enHallowsGemInlayLevelList] = gemlist
		
	def SetHallowsGem(self, GemCoding, gemType, level):
		#插入雕纹镶嵌
		hallowsgem = self.odata.get(EnumOdata.enHallowsGemInlayLevelList)
		hallowsgem.append([GemCoding, gemType, level])
		
	def LevelUpHallowsGem(self, index, GemCoding, gemType, level):
		#根据index更改对应项
		hallowsgem = self.odata.get(EnumOdata.enHallowsGemInlayLevelList)
		if not hallowsgem:
			return
		Ocoding, Otype, _ = hallowsgem[index - 1]
		if Ocoding == GemCoding:
			print "GE_EXC LevelUpHallowsGem repeat level up (%s)" % self.role.GetRoleID()
			return
		if Otype != gemType:
			print "GE_EXC LevelUpHallowsGem error (%s)" % self.role.GetRoleID()
			return 
		hallowsgem[index - 1] = [GemCoding, gemType, level]
		
		AutoLog.LogObj(self.role.GetRoleID(), AutoLog.eveLevelHallowsGem, self.oid, self.otype, self.oint, self.odata, [GemCoding, gemType, level])
	
	def delGembyLocation(self, index):
		#删除某个雕纹
		if index < 1:
			return False
		hallowsgem = self.odata.get(EnumOdata.enHallowsGemInlayLevelList)
		if not hallowsgem:
			return False
		if len(hallowsgem) < index:
			return False
		coding, _, _ = hallowsgem[index - 1]
		del hallowsgem[index - 1]
		return coding
		
#订婚戒指
class Ring(ItemBase.ItemBase):
	Obj_Type = Base.Obj_Type_Ring
	def __init__(self, role, obj):
		ItemBase.ItemBase.__init__(self, role, obj)
		self.package = None
	
	def AfterLoad_Except(self):
		Base.ObjBase.AfterLoad_Except(self)
		if EnumOdata.enRingIsImprint not in self.odata:
			self.odata[EnumOdata.enRingIsImprint] = 0
		
	def SetIsImprint(self):
		self.odata[EnumOdata.enRingIsImprint] = 1
	
	def IsImprint(self):
		return self.odata.get(EnumOdata.enRingIsImprint, 0)
	
	def ReturnCoding(self):
		return self.otype
	
#魔灵类
class MagicSpirit(ItemBase.ItemBase):
	Obj_Type = Base.Obj_Type_MagicSpirit
	def __init__(self, role, obj):
		ItemBase.ItemBase.__init__(self, role, obj)
		#拥有者，角色或者英雄，在背包则是None
		self.owner = None
		#魔灵配置唯一ID
		self.onumber = self.otype
		#拥有玩家
		self.role = role
		
	def AfterCreate(self, needInit = True):
		#先调用父类函数,载入相关配置
		Base.ObjBase.AfterCreate(self)
		#是否需要初始化,区别新装备或者获取了旧的
		if needInit is True:
			#私有数据初始化
			##魔灵洗练保存的属性{pt:pv,}
			self.odata[EnumOdata.enMagicSpiritSavedProperty] = self.cfg.RandomPropertyList()
			#魔灵洗练未保存属性{pt:pv,}
			self.odata[EnumOdata.enMagicSpiritUnsavedProperty] = []
			##魔灵洗练保存的技能点{st:sv,}
			self.odata[EnumOdata.enMagicSpiritSavedSkillPoint] = self.cfg.RandomSkillPointList()
			#魔灵洗练未保存技能点{st:sv,}
			self.odata[EnumOdata.enMagicSpiritUnsavedSkillPoint] = []
			
	def AfterLoad_Except(self):
		#数据库载入后调用
		Base.ObjBase.AfterLoad_Except(self)
		#缓存拥有者
		if self.package.ObjEnumIndex == EnumObj.En_RoleMagicSpirits:
			self.owner = self.package.role
		elif self.package.ObjEnumIndex == EnumObj.En_HeroMagicSpirits:
			self.owner = self.package.hero
		
		#确保初始私有数据正常	
		if EnumOdata.enMagicSpiritSavedProperty not in self.odata:
			self.odata[EnumOdata.enMagicSpiritSavedProperty] = self.cfg.RandomPropertyList()
			
		if EnumOdata.enMagicSpiritUnsavedProperty not in self.odata:
			self.odata[EnumOdata.enMagicSpiritUnsavedProperty] = []
			
		if EnumOdata.enMagicSpiritSavedSkillPoint not in self.odata:
			self.odata[EnumOdata.enMagicSpiritSavedSkillPoint] = self.cfg.RandomSkillPointList()
			
		if EnumOdata.enMagicSpiritUnsavedSkillPoint not in self.odata:
			self.odata[EnumOdata.enMagicSpiritUnsavedSkillPoint] = []
	
	def GetSavedRefreshPro(self):
		'''
		获取保存的洗练属性字典
		'''
		return self.odata[EnumOdata.enMagicSpiritSavedProperty]
		
	def GetUnSavedRefreshPro(self):
		'''
		获取未保存的洗练属性字典
		'''
		return self.odata[EnumOdata.enMagicSpiritUnsavedProperty]
		
	def GetSavedRefreshSkillPoint(self):
		'''
		获取保存的洗练技能点字典
		'''
		return self.odata[EnumOdata.enMagicSpiritSavedSkillPoint]
		
	def GetUnSavedRefreshSkillPoint(self):
		'''
		获取保存的洗练技能点字典
		'''
		return self.odata[EnumOdata.enMagicSpiritUnsavedSkillPoint]
	
	def SetSavedRefreshPro(self, pro_list):
		'''
		设置保存的洗练属性字典
		'''
		self.odata[EnumOdata.enMagicSpiritSavedProperty] = pro_list
		
	def SetUnSavedRefreshPro(self, pro_list):
		'''
		设置未保存的洗练属性字典
		'''
		self.odata[EnumOdata.enMagicSpiritUnsavedProperty] = pro_list
	
	def SetSavedRefreshSkillPoint(self, sp_list):
		'''
		设置保存的洗练技能点字典
		'''
		self.odata[EnumOdata.enMagicSpiritSavedSkillPoint] = sp_list
		
	def SetUnSavedRefreshSkillPoint(self, sp_list):
		'''
		设置未保存的洗练技能点字典
		'''
		self.odata[EnumOdata.enMagicSpiritUnsavedSkillPoint] = sp_list
	
	def GetPropertyDict(self):
		'''
		返回魔灵属性字典
		'''
		p_dict = {}
		spList = self.odata[EnumOdata.enMagicSpiritSavedProperty]
		if len(spList) == 2:
			p_dict[spList[0]] = spList[1]
		return p_dict

