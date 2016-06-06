#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Item.ItemConfig")
#===============================================================================
# 物品配置
#===============================================================================
import random
import Environment
import DynamicPath
from Util import Random
from Util.File import TabFile
from Game.Property import PropertyEnum




if "_HasLoad" not in dir():
	ITEM_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	ITEM_FILE_FOLDER_PATH.AppendPath("ItemConfig")
	
	#普通物品配置
	ItemCfg_Dict = {}
	
	ValueItems = set()
	
	#背包基础配置
	PackageSize_Dict = {}
	#背包开格子配置
	GridOpen_Dict = {}
	#物品出售给系统商店的价格计算参数配置表
	Equipment_Sell_Dict = {}
	#普通物品coding集合
	ItemCodingSet = set()
	#装备coding集合
	EquipmentCodingSet = set()
	
	GoodsSet = set()
	
	#套装
	Equipment_Suit_Dict = {}
	#神器套装
	Artifact_Suit_Dict = {}
	Artifact_Sell_Dict = {}#神器售卖配置
	ArtifactCuiLianLevel_Dict = {}
	ArtifactCuiLianBase_Dict = {}
	ArtifactCuiLian_Dict = {}
	ArtifactCuiLianSuite_Dict = {}
	ArtifactCuiLianHalo_Dict = {}	#神器淬炼光环属性
	
	ArtifactCuiLianIndex_Dict = {}
	ArtifactCuiLianSuite7_Dict = {}
	
	
	JTCrystalConfigDict = {}
	JTCrystalSealingConfigDict = {}
	
	#魔灵配置
	MagicSpirit_Dict = {}	#{coding:cfg,}


def CheckItemCoding(coding):
	global GoodsSet
	if coding not in GoodsSet:
		return False
	return True


#普通物品
class ItemConfig(TabFile.TabLine):
	ITEM_R = 1		#用于识别普通物品和装备
	useFun = None	#使用函数
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("Item.txt")
	def __init__(self):
		self.coding = int
		self.name = str
		self.canSell = int
		self.canOverlap = int
		self.salePrice = int
		self.canUse = int
		self.canUseSome = int#是否可以批量使用
		self.useLevel = int#使用等级
		self.useNeedItem = self.GetEvalByString
		self.needLog = int
		self.jiaMi = int
		
		#物品分类，为了坑爹的策划，把前端的列读进来判断
		self.kinds = int
		self.doubleclick = str
		
		self.minutes = self.GetEvalByString#有效时间
		
		self.timeoutCoding = self.GetEvalByString#叠加类型的时效物品过期后转换的物品类型

	def SetUseFun(self, fun):
		#设置这个物品的使用函数
		if self.useFun is not None:
			print "GE_EXC, repeat set usefun in item(%s)" % self.coding
		if not self.canUse:
			print "GE_EXC can not use this item in SetUseFun (%s)" % self.coding
		self.useFun = fun
	

	
#装备
class EquipmentConfig(TabFile.TabLine):
	ITEM_R = 2#用于识别普通物品和装备
	useFun = None
	canOverlap = False#默认不可以叠加
	canTrade = False
	kinds = 7
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("Equipment.txt")
	def __init__(self):
		self.coding = int
		self.name = str
		self.needlevel = int
		self.grade = int
		self.posType = int
		self.suitId = self.GetEvalByString
		self.StrengthRate = int
		self.Strength = int
		self.UpGrade = int
		self.forging = int
		self.ZhuanShengLevel = int			#装备转生等级
		self.needZhuanSheng = int			#转生装备佩戴需要英雄转生等级
		self.evolve = int					#是否可以进化
		self.zhuanSheng = int				#是否可以转生
		self.canSell = int
		self.salePrice = int
		self.jiaMi = int
		self.pt1 = int
		self.pv1 = int
		self.pt2 = int
		self.pv2 = int
		#是否需要记录日志
		self.needLog = int		
		self.holeNum = int
		self.Mosaic = int
		self.IsRole = int
		self.FreeWash = int
		self.UnlockWash = int
		self.WashLevel = int
		
	def InitProperty(self):
		self.p_dict = {}
		if self.pt1 and self.pv1:
			self.p_dict[self.pt1] = self.pv1
		if self.pt2 and self.pv2:
			self.p_dict[self.pt2] = self.pv2
		

	
#装备强化配置
class StrengthenConfig(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("Strengthen.txt")
	def __init__(self):
		self.posType = int
		self.level = int
		self.needMoney = int
		self.pt1 = int
		self.pv1 = int
		self.pt2 = int
		self.pv2 = int
	
	def InitProperty(self):
		self.p_dict = {}
		if self.pt1 and self.pv1:
			self.p_dict[self.pt1] = self.pv1
		if self.pt2 and self.pv2:
			self.p_dict[self.pt2] = self.pv2
		


#装备套装属性配置
class EquipmentSuitConfig(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("EquipmentSuit.txt")
	def __init__(self):
		self.suitId = int
		self.cnt = int
		self.equipId = self.GetEvalByString
		self.pt1 = int
		self.pv1 = int
		self.pt2 = int
		self.pv2 = int
	
	def Check(self):
		if self.pt1 == self.pt2:
			print "GE_EXC, EquipmentSuitConfig", self.suitId
		
		
		self.p_dict = {}
		if self.pt1 and self.pv1:
			self.p_dict[self.pt1] = self.pv1
		if self.pt2 and self.pv2:
			self.p_dict[self.pt2] = self.pv2
		

		

#装备升阶配置
class EquipmentUpgradeConfig(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("EquipmentUpgrade.txt")
	def __init__(self):
		self.srcType = int
		self.desType = int
		self.needLevel = int
		self.itemType1 = int
		self.cnt1 = int
		self.itemType2 = int
		self.cnt2 = int
		self.itemType3 = int
		self.cnt3 = int
		self.itemType4 = int
		self.cnt4 = int

#装备神铸配置
class EquipmentGodcastConfig(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("EquipmentGodcast.txt")
	def __init__(self):
		self.srcType = int
		self.desType = int
		self.needLevel = int
		self.itemType1 = int
		self.cnt1 = int
		self.itemType2 = int
		self.cnt2 = int
		self.itemType3 = int
		self.cnt3 = int
		self.itemType4 = int
		self.cnt4 = int

#背包空间基本配置
class PackageSizeConfig(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("PackageSize.txt")
	def __init__(self):
		self.vipLevel = int#扩充的次数
		self.baseSize = int
		self.openTimes = int


#背包开格子
class GridOpen(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("PackageGrid.txt")
	def __init__(self):
		self.openIndex = int#扩充的次数
		self.needRMB = int

#装备出售给系统商店
class EquipmentSell(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("EquipmentSell.txt")
	def __init__(self):
		self.ePos = int
		self.strengthLv = int
		self.sumcost = int

#装备宝石
class EquipmentGem(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("EquipmentGem.txt")	
	def __init__(self):
		self.GemID = int
		self.GemLevel = int
		self.GemType = int
		self.CanMix = int
		self.MixMoney = int
		self.MixNum = int
		self.NextGemID = int
		self.lowerlist = self.GetEvalByString
		self.decompositionNum = int
		self.pt1 = int
		self.pv1 = int
		self.pt2 = int
		self.pv2 = int
		self.IsResolve = int
		self.CostRMB = int
		self.GetResolve = int

	def Check(self):
		if self.pt1 == self.pt2:
			print "GE_EXC, EquipmentGem", self.GemID		
		self.p_dict = {}
		if self.pt1 and self.pv1:
			self.p_dict[self.pt1] = self.pv1
		if self.pt2 and self.pv2:
			self.p_dict[self.pt2] = self.pv2
		
		if self.lowerlist:
			lenl = len(self.lowerlist)
			if lenl != len(set(self.lowerlist)):
				print "GE_EXC, error in EquipmentGem lowerlist (%s)" % self.GemID
		
		#10级双属性宝石 分解数 相当于 1级单属性宝石
		if self.decompositionNum != (2 ** (self.GemLevel - 1)) and self.decompositionNum != (2 ** (self.GemLevel - 10)):
			print "GE_EXC, error in EquipmentGem decompositionNum (%s)" % self.GemID
		
	def Check_2(self):
		if self.NextGemID:
			from Game.Item import Gem
			if self.NextGemID not in Gem.Equipment_Gem_Dict:
				print "GE_EXC, self.NextGemID not in Gem.Equipment_Gem_Dict （%s）" % self.GemID
	

#宝石封灵			
class GemSealingSpirit(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("GemSealingSpirit.txt")
	def __init__(self):
		self.SealingLevel = int
		self.needItem = int
		self.NextLevel = int
		self.addExp = int
		self.needExp = int
		self.add6 = int
		self.add7 = int
		self.add8 = int
		self.add9 = int
		self.add10 = int
		self.add11 = int
		self.add12 = int

#装备附魔
class EquipmentEnchant(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("EquipmentEnchant.txt")
	def __init__(self):
		self.EnchantLevel 	= int
		self.needItem		= self.GetEvalByString
		self.AddPercent		= int
		self.IsAbroad		= int
		self.returnItem		= self.GetEvalByString
#===============神器相关=============================
#神器配置表
class ArtifactConfig(TabFile.TabLine):
	ITEM_R = 3#用于识别普通物品和装备及神器
	useFun = None
	canOverlap = False#默认不可以叠加
	canTrade = False
	kinds = 6
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("Artifact.txt")
	def __init__(self):
		self.coding = int
		self.name = str
		self.needlevel = int
		self.grade = int
		self.posType = int
		self.suitId = self.GetEvalByString
		self.maxSrength = int
		self.canSell = int
		self.salePrice = int
		self.Strength = int
		self.UpGrade = int
		self.jiaMi = int
		self.pt1 = int
		self.pv1 = int
		self.pt2 = int
		self.pv2 = int
		#是否需要记录日志
		self.needLog = int		
		self.holeNum = int
		self.Mosaic = int
		self.maxCuiLian = int

	def InitProperty(self):
		self.p_dict = {}
		if self.pt1 and self.pv1:
			self.p_dict[self.pt1] = self.pv1
		if self.pt2 and self.pv2:
			self.p_dict[self.pt2] = self.pv2
		
#神器强化配置
class ArtifactStrengthenConfig(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("ArtifactStrengthen.txt")
	def __init__(self):
		self.artifact = int
		self.level = int
		self.coding = int
		self.cnt = int
		self.pt1 = int
		self.pv1 = int
		self.pt2 = int
		self.pv2 = int
	
	def InitProperty(self):
		self.p_dict = {}
		if self.pt1 and self.pv1:
			self.p_dict[self.pt1] = self.pv1
		if self.pt2 and self.pv2:
			self.p_dict[self.pt2] = self.pv2
#神器升阶
class ArtifactUpgradeConfig(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("ArtifactUpgrade.txt")
	def __init__(self):
		self.srcType = int
		self.desType = int
		self.needLevel = int
		self.itemType1 = int
		self.cnt1 = int
		self.itemType2 = int
		self.cnt2 = int
		self.itemType3 = int
		self.cnt3 = int
		self.itemType4 = int
		self.cnt4 = int

#神器符石
class ArtifactGemConfig(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("ArtifactGem.txt")	
	def __init__(self):
		self.GemID = int
		self.GemLevel = int
		self.GemType = int
		self.CanMix = int
		self.MixMoney = int
		self.MixNum = int
		self.NextGemID = int
		self.lowerlist = self.GetEvalByString
		self.decompositionNum = int
		self.pt1 = int
		self.pv1 = int
		self.pt2 = int
		self.pv2 = int

	def Check(self):
		if self.pt1 == self.pt2:
			print "GE_EXC, ArtifactGem", self.GemID		
		self.p_dict = {}
		if self.pt1 and self.pv1:
			self.p_dict[self.pt1] = self.pv1
		if self.pt2 and self.pv2:
			self.p_dict[self.pt2] = self.pv2
		
		if self.lowerlist:
			lenl = len(self.lowerlist)
			if lenl != len(set(self.lowerlist)):
				print "GE_EXC, error in ArtifactGem lowerlist (%s)" % self.GemID
		
		if self.decompositionNum != (2 ** (self.GemLevel - 1)):
			print "GE_EXC, error in ArtifactGem decompositionNum (%s)" % self.GemID
	
	def Check_2(self):
		if self.NextGemID:
			from Game.Item import ArtifactGem
			if self.NextGemID not in ArtifactGem.Artifact_Gem_Dict:
				print "GE_EXC, self.NextGemID not in ArtifactGem.Artifact_Gem_Dict （%s）" % self.GemID
#符石封印
class ArtifactGemSealing(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("ArtifactGemSealing.txt")
	def __init__(self):
		self.SealingLevel = int
		self.needItem = int
		self.NextLevel = int
		self.addExp = int
		self.needExp = int
		self.add6 = int
		self.add7 = int
		self.add8 = int
		self.add9 = int
		self.add10 = int

#神器售卖
class ArtifactSell(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("ArtifactSell.txt")
	def __init__(self):
		self.strengthLv = int
		self.salereturn = self.GetEvalByString
		self.CuiLianReturn = self.GetEvalByString
		
#神器套装属性配置（万分比）
class ArtifactSuitConfig(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("ArtifactSuit.txt")
	def __init__(self):
		self.suitId = int
		self.cnt = int
		self.equipId = self.GetEvalByString
		self.pt1 = int
		self.pv1 = int
		self.pt2 = int
		self.pv2 = int
	
	def Check(self):
		if self.pt1 == self.pt2:
			print "GE_EXC, ArtifactSuitConfig", self.suitId		
		self.p_dict = {}
		if self.pt1 and self.pv1:
			self.p_dict[self.pt1] = self.pv1
		if self.pt2 and self.pv2:
			self.p_dict[self.pt2] = self.pv2

#神器淬炼等级
class ArtifactCuiLianLevel(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("ArtifactCuiLianLevel.txt")
	def __init__(self):
		self.cuiLianLevel = int
		self.needExp = int
		self.needAllExp = int
	

#神器淬炼基础属性加成
class ArtifactCuiLianBase(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("ArtifactCuiLianBase.txt")
	def __init__(self):
		self.cuiLianIndex = self.GetEvalByString
		self.pt1 = int
		self.pv1 = int
		self.pt2 = int
		self.pv2 = int
		
	def InitProperty(self):
		if self.pt1 == self.pt2:
			print "GE_EXC, ArtifactSuitConfig", self.suitId	
		self.p_dict = {}
		if self.pt1 and self.pv1:
			self.p_dict[self.pt1] = self.pv1
		if self.pt2 and self.pv2:
			self.p_dict[self.pt2] = self.pv2
			
#神器淬炼组合加成
class ArtifactCuiLian(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("ArtifactCuiLian.txt")
	def __init__(self):
		self.suiteIndex = self.GetEvalByString
		self.needCuiLian = self.GetEvalByString
		self.pv1 = int
		self.pt1 = int
		self.pv2 = int
		self.pt2 = int
		
	def InitProperty(self):
		self.p_dict = {}
		if self.pt1 and self.pv1:
			self.p_dict[self.pt1] = self.pv1
		if self.pt2 and self.pv2:
			self.p_dict[self.pt2] = self.pv2
#神器淬炼组合
class ArtifactCuiLianSuite(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("ArtifactCuiLianSuite.txt")
	def __init__(self):
		self.index = int
		self.artifact = self.GetEvalByString
		
##神器装备淬炼第七号组合最小等级配置
class ArtifactCuiLianSuite7(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("ArtifactCuiLianSuite7.txt")
	def __init__(self):
		self.minLevel = int
		self.suiteIndex = self.GetEvalByString
		
#神器淬炼组合
class ArtifactCuiLianIndex(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("ArtifactCuiLianIndex.txt")
	def __init__(self):
		self.pos1 = int
		self.lev1 = int
		self.pos2 = int
		self.lev2 = int
		self.index = int
		self.level = int
		
#神器淬炼光环
class ArtifactCuiLianHalo(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("ArtifactCuiLianHalo.txt")
	def __init__(self):
		self.haloLevel = int
		self.needExp = int
		self.needAllExp = int
		self.addPercent_4 = int
		self.addPercent_5 = int
		self.addPercent_6 = int
		self.addPercent_7 = int
		self.addPercent_8 = int
		self.addPercent_9 = int
		self.addPercent_10 = int
	def Initproperty(self):
		self.percent = {4:self.addPercent_4,
						5:self.addPercent_5, 6:self.addPercent_6, 7:self.addPercent_7,
						8:self.addPercent_8, 9:self.addPercent_9, 10:self.addPercent_10
						}
		
#===============圣器相关=============================
class HallowsConfig(TabFile.TabLine):
	ITEM_R = 4#用于识别普通物品/装备/神器/圣器
	useFun = None
	canOverlap = False#默认不可以叠加
	canTrade = False
	kinds = 6
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("Hallows.txt")
	def __init__(self):
		self.coding = int
		self.name = str
		self.needlevel = int
		self.hole = int
		self.grade = int
		self.maxShenzaoLevel = int
		self.inipropcnt = int
		self.posType = int
		self.sortLevel = int
		self.shenzaoProperty = self.GetEvalByString
		self.salePrice = self.GetEvalByString
		self.proprate = self.GetEvalByString
		self.ptmax = self.GetEvalByString
		self.ptbase = self.GetEvalByString
		self.canSell = int
		self.jiaMi = int
		#是否需要记录日志
		self.needLog = int
	def PreCoding(self, rdm):
		self.randomprop = rdm

		
class HallowsPropLevelConfig(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("HallowsBaseProp.txt")
	def __init__(self):
		self.PropLevel = int
		self.Rate = int
		self.Percent = self.GetEvalByString
		self.InitRate = int

		
class HallowsEnchantConfig(TabFile.TabLine):
	#圣器附魔配置表
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("HallowsEnchant.txt")
	def __init__(self):
		self.EnChantsLevel = int
		self.PropGain = int
		self.Cost = int
		self.CostItem = int
		self.PriceItem = int
		self.Price = int


class HallowsShenzaoConfig(TabFile.TabLine, PropertyEnum.PropertyRead):
	#圣器神造配置表
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("HallowsShenzao.txt")
	def __init__(self):
		PropertyEnum.PropertyRead.__init__(self)
		self.shenzaoLevel = int
		self.needExp = int
		self.sellReturn = self.GetEvalByString
		
class HallowsGemConfig(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("HallowsGem.txt")	
	def __init__(self):
		self.GemID = int
		self.GemLevel = int
		self.GemType = int
		self.CanMix = int
		self.MixMoney = int
		self.MixNum = int
		self.NextGemID = int
		self.lowerlist = self.GetEvalByString
		self.decompositionNum = int
		self.pt1 = int
		self.pv1 = int

	def Check(self):
		self.p_dict = {}
		if self.pt1 and self.pv1:
			self.p_dict[self.pt1] = self.pv1
		
		if self.lowerlist:
			lenl = len(self.lowerlist)
			if lenl != len(set(self.lowerlist)):
				print "GE_EXC, error in HallowsGem lowerlist (%s)" % self.GemID
		
		if self.decompositionNum != (2 ** (self.GemLevel - 1)):
			print "GE_EXC, error in HallowsGem decompositionNum (%s)" % self.GemID
	
	def Check_2(self):
		if self.NextGemID:
			from Game.Item import HallowsGem
			if self.NextGemID not in HallowsGem.Hallows_Gem_Dict:
				print "GE_EXC, self.NextGemID not in HallowsGem.Hallows_Gem_Dict （%s）" % self.GemID
		
#雕纹封印
class HallowsGemSealing(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("HallowsGemSealing.txt")
	def __init__(self):
		self.SealingLevel = int
		self.needItem = int
		self.NextLevel = int
		self.addExp = int
		self.needExp = int
		self.add6 = int
		self.add7 = int
		self.add8 = int
		self.add9 = int
		self.add10 = int
		
class JTCrystal(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("crystal.txt")
	def __init__(self):
		self.crystalID = int
		self.crystalLevel = int
		self.crystalType = int
		self.netxLevel = int
		self.lowerList = eval
		self.equalLowest = int
		self.pt = int
		self.pv = int
		

class JTCrystalSealing(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("crystalSealing.txt")
	def __init__(self):
		self.level = int
		self.addOn = eval
		self.needItem = int
		self.incExp = int
		self.highestlevel = int
		self.upLevelExp = int
		
class MagicSpirit(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("MagicSpirit.txt")
	def __init__(self):
		self.coding = int
		self.name = str
		self.magicSpiritLevel = int
		self.magicSpiritType = int
		self.propertyPool = self.GetEvalByString
		self.skillPointPool = self.GetEvalByString
		self.skillPointRange = self.GetEvalByString
		self.nextLevelID = int
		self.needItem = self.GetEvalByString
		self.needItemEx = self.GetEvalByString
		self.returnItem = self.GetEvalByString
		#是否需要记录日志
		self.needLog = int
		self.needlevel = int	
		self.canSell = int	
		self.jiaMi = int
		self.returnMoney = int
	
	def RandomPropertyList(self):
		'''
		返回随机属性字典{pt:pv}
		'''
		pt, pv = self.propertyRandom.RandomOne()
		return [pt, pv]
	
	def RandomSkillPointList(self):
		'''
		返回随机技能点字典{st:sv}
		'''
		st = self.skillPointRandom.RandomOne()
		svRangeList = self.skillPointRandomEx.RandomOne()
		sv = random.randint(*svRangeList)
		return [st,sv]
		
	def GetProValueByProType(self, proType):
		'''
		获取对应技能skillPointType的SkillPointValue
		'''
		proValue = None
		for tmpProType, tmpProValue, _ in self.propertyPool:
			if tmpProType == proType:
				proValue = tmpProValue
				break
		
		return proValue
#=====================================================================
#外部函数
def ItemCanOverlap(coding):
	#返回是否可以叠加
	global ItemCfg_Dict
	cfg = ItemCfg_Dict.get(coding)
	if not cfg:
		#默认不是普通物品都是不可以叠加的
		return False
	return cfg.canOverlap


def LoadItemConfig():
	#物品基础配置
	from Game.Role.Obj import Base
	from Game.Item import Item
	global ItemCfg_Dict
	global ValueItems
	
	for IC in ItemConfig.ToClassType():
		#是否重复coding
		if IC.coding in ItemCfg_Dict:
			print "GE_EXC, repeat coding in LoadItemConfig, (%s)" % IC.coding
		
		ItemCfg_Dict[IC.coding] = IC
		if IC.coding in Base.Obj_Config:
			print "GE_EXC, LoadItemConfig repeat coding in Base.Obj_Config, (%s)" % IC.coding
		Base.Obj_Config[IC.coding] = IC
		
		if IC.coding in Base.Obj_Type_Fun:
			print "GE_EXC, repeat RegTypeObjFun.(%s) " % IC.coding
		
		#设置： 创建这个coding物品需要调用的创建函数
		if IC.minutes:
			#时效性物品,检查是否可以叠加，过期转换物品等规则是否有问题
			if not IC.timeoutCoding:
				#时效性物品，没有配置过期后转换的coding，则认为是不可以叠加物品
				if IC.canOverlap:
					print "GE_EXC, time out item error (%s) this item can not overlap" % IC.coding 
				Base.Obj_Type_Fun[IC.coding] = Item.TimeItem
			else:
				#配置了过期转换的coding,则认为是可以叠加的(不可以叠加就不要配置这个啊，浪费了一个coding)
				if not IC.canOverlap:
					print "GE_EXC, time out item error (%s) this item must overlap" % IC.coding 
				if IC.coding == IC.timeoutCoding:
					#过期了重新变成自己？不行,转换逻辑会出问题的
					print "GE_EXC, time out item error IC.coding == IC.timeoutCoding (%s)" % IC.coding
				Base.Obj_Type_Fun[IC.coding] = Item.TimeItemOverlap
				Base.Obj_Time_Overlap.add(IC.coding)
		else:
			Base.Obj_Type_Fun[IC.coding] = Item.Item
		
		ItemCodingSet.add(IC.coding)
		GoodsSet.add(IC.coding)
		
		if IC.kinds == 2:
			ValueItems.add(IC.coding)


def LoadEquipmentConfig():
	#装备基础配置
	from Game.Role.Obj import Base
	from Game.Item import Item
	global ItemCfg_Dict

	for EC in EquipmentConfig.ToClassType():
		if EC.coding in ItemCfg_Dict:
			print "GE_EXC, repeat coding in LoadEquipmentConfig, (%s)" % EC.coding
		
		EC.InitProperty()
		
		ItemCfg_Dict[EC.coding] = EC
		if EC.coding in Base.Obj_Config:
			print "GE_EXC, LoadEquipmentConfig repeat coding in Base.Obj_Config"
		Base.Obj_Config[EC.coding] = EC
		
		if EC.coding in Base.Obj_Type_Fun:
			print "GE_EXC, repeat RegTypeObjFun. EC,(%s)" % EC.coding
		Base.Obj_Type_Fun[EC.coding] = Item.Equipment
		EquipmentCodingSet.add(EC.coding)
		GoodsSet.add(EC.coding)



def LoadPackageSizeConfig():
	#背包空间
	global PackageSize_Dict
	for ps in PackageSizeConfig.ToClassType():
		if ps.vipLevel in PackageSize_Dict:
			print "GE_EXC, repeat vipLevel in LoadPackageSizeConfig, (%s)" % ps.vipLevel
		PackageSize_Dict[ps.vipLevel] = ps


def LoadGridOpenConfig():
	#开格子
	global GridOpen_Dict
	for GO in GridOpen.ToClassType():
		if GO.openIndex in GridOpen_Dict:
			print "GE_EXC, repeat openIndex in LoadGridOpenConfig, (%s)" % GO.openIndex
		GridOpen_Dict[GO.openIndex] = GO.needRMB

def LoadEquipmentSellConfig():
	#装备价格
	for ES in EquipmentSell.ToClassType():
		key = ES.ePos, ES.strengthLv
		if key in Equipment_Sell_Dict:
			print "GE_EXC, repeat ePos=(%s) and strengthLv=(%s)in LoadEquipmentSellConfig" % (ES.ePos,ES.strengthLv)
		Equipment_Sell_Dict[key] = ES

def LoadStrengthen():
	#强化装备配置
	from Game.Item import EquipmentForing
	for SC in StrengthenConfig.ToClassType():
		key = SC.posType, SC.level
		if key in EquipmentForing.Strengthen_Dict:
			print "GE_EXC, repeat key in LoadStrengthen, posType(%s),level(%s)"  % (SC.posType, SC.level)
		EquipmentForing.Strengthen_Dict[key] = SC
		SC.InitProperty()

def LoadUpgradeConfig():
	#进阶装备配置
	from Game.Item import EquipmentForing
	for EUC in EquipmentUpgradeConfig.ToClassType():
		if EUC.srcType in EquipmentForing.Equipment_Upgrade_Dict:
			print "GE_EXC, repeat EUC.srcType in LoadUpgradeConfig, (%s)" % EUC.srcType
		if (EUC.itemType1 and EUC.cnt1 == 0) or (EUC.itemType2 and EUC.cnt2 == 0) or (EUC.itemType3 and EUC.cnt3 == 0):
			print "GE_EXC, LoadUpgradeConfig, srcType=(%s) has itemtype is no cnt" % EUC.srcType
		EquipmentForing.Equipment_Upgrade_Dict[EUC.srcType] = EUC

def LoadGodcastConfig():
	#进阶神铸配置
	from Game.Item import EquipmentForing
	for EUC in EquipmentGodcastConfig.ToClassType():
		if EUC.srcType in EquipmentForing.Equipment_Godcast_Dict:
			print "GE_EXC, repeat EUC.srcType in LoadGodcastConfig, (%s)" % EUC.srcType
		if (EUC.itemType1 and EUC.cnt1 == 0) or (EUC.itemType2 and EUC.cnt2 == 0) or (EUC.itemType3 and EUC.cnt3 == 0):
			print "GE_EXC, LoadGodcastConfig, srcType=(%s) has itemtype is no cnt" % EUC.srcType
		EquipmentForing.Equipment_Godcast_Dict[EUC.srcType] = EUC

def LoadEquipmentSuitConfig():
	#装备套装属性
	global Equipment_Suit_Dict
	for SSC in EquipmentSuitConfig.ToClassType():
		if SSC.suitId in Equipment_Suit_Dict:
			print "GE_EXC, repeat SSC.level in LoadStrengthenSuit, (%s)" % SSC.suitId
		Equipment_Suit_Dict[SSC.suitId] = SSC
		SSC.Check()

def LoadEquipmentGem():
	#装备宝石
	from Game.Item import Gem
	for cfg in EquipmentGem.ToClassType():
		if cfg.GemID in Gem.Equipment_Gem_Dict:
			print "GE_EXC,repeat GemID in EquipmentGem, (%s)"	% cfg.GemID
		Gem.Equipment_Gem_Dict[cfg.GemID] = cfg
		cfg.Check()
	
	for cfg in Gem.Equipment_Gem_Dict.itervalues():
		cfg.Check_2()
	

def LoadGemSealingSpirit():
	#宝石封灵
	from Game.Item import Gem
	for cfg in GemSealingSpirit.ToClassType():
		if cfg.SealingLevel in Gem.Sealing_Spirit_Dict:
			print "GE_EXC,repeat SealingLevel(%s) in GemSealingSpirit", cfg.SealingLevel
		Gem.Sealing_Spirit_Dict[cfg.SealingLevel] = cfg

def LoadArtifactConfig():
	#神器基础配置
	from Game.Role.Obj import Base
	from Game.Item import Item
	global ItemCfg_Dict

	for EC in ArtifactConfig.ToClassType():
		if EC.coding in ItemCfg_Dict:
			print "GE_EXC, repeat coding in LoadArtifactConfig, (%s)" % EC.coding
		
		EC.InitProperty()
		
		ItemCfg_Dict[EC.coding] = EC
		if EC.coding in Base.Obj_Config:
			print "GE_EXC, LoadArtifactConfig repeat coding in Base.Obj_Config"
		Base.Obj_Config[EC.coding] = EC
		
		if EC.coding in Base.Obj_Type_Fun:
			print "GE_EXC, repeat RegTypeObjFun. EC,(%s)" % EC.coding
		Base.Obj_Type_Fun[EC.coding] = Item.Artifact
		GoodsSet.add(EC.coding)

def LoadArtifactStrengConfig():
	#神器强化配置
	from Game.Item import ArtifactForing
	for AF in ArtifactStrengthenConfig.ToClassType():
		key = AF.artifact, AF.level
		if key in ArtifactForing.Artifact_Strengthen_Dict:
			print "GE_EXC,repeat key in ArtifactStrengthenConfig,artifact=%s,level=%s" % (AF.artifact, AF.level)
		ArtifactForing.Artifact_Strengthen_Dict[key] = AF
		AF.InitProperty()

def LoadArtifactUpgradeConfig():
	#进阶神器配置
	from Game.Item import ArtifactForing
	for EUC in ArtifactUpgradeConfig.ToClassType():
		if EUC.srcType in ArtifactForing.Artifact_Upgrade_Dict:
			print "GE_EXC, repeat EUC.srcType in LoadArtifactUpgradeConfig, (%s)" % EUC.srcType
		if (EUC.itemType1 and EUC.cnt1 == 0) or (EUC.itemType2 and EUC.cnt2 == 0) or (EUC.itemType3 and EUC.cnt3 == 0):
			print "GE_EXC, LoadArtifactUpgradeConfig, srcType=(%s) has itemtype is no cnt" % EUC.srcType
		ArtifactForing.Artifact_Upgrade_Dict[EUC.srcType] = EUC

def LoadArtifactSuitConfig():
	#装备套装属性
	global Artifact_Suit_Dict
	for SSC in ArtifactSuitConfig.ToClassType():
		if SSC.suitId in Artifact_Suit_Dict:
			print "GE_EXC, repeat SSC.level in LoadStrengthenSuit, (%s)" % SSC.suitId
		Artifact_Suit_Dict[SSC.suitId] = SSC
		SSC.Check()
		
def LoadArtifactGem():
	#神器符石
	from Game.Item import ArtifactGem
	for cfg in ArtifactGemConfig.ToClassType():
		if cfg.GemID in ArtifactGem.Artifact_Gem_Dict:
			print "GE_EXC,repeat GemID in ArtifactGem, (%s)"	% cfg.GemID
		ArtifactGem.Artifact_Gem_Dict[cfg.GemID] = cfg
		cfg.Check()
	for cfg in ArtifactGem.Artifact_Gem_Dict.itervalues():
		cfg.Check_2()
		
def LoadArtifactGemSealing():
	#符石封灵
	from Game.Item import ArtifactGem
	for cfg in ArtifactGemSealing.ToClassType():
		if cfg.SealingLevel in ArtifactGem.Sealing_Spirit_Dict:
			print "GE_EXC,repeat SealingLevel(%s) in GemSealingSpirit" % cfg.SealingLevel
		ArtifactGem.Sealing_Spirit_Dict[cfg.SealingLevel] = cfg

def LoadArtifactSellConfig():
	#装备价格
	for ES in ArtifactSell.ToClassType():
		if ES.strengthLv in Artifact_Sell_Dict:
			print "GE_EXC, repeat strengthLv=(%s)in LoadEquipmentSellConfig" % ES.strengthLv
		Artifact_Sell_Dict[ES.strengthLv] = ES
		
def LoadArtifactCuiLianHaloConfig():
	#神器装备淬炼光环
	global ArtifactCuiLianHalo_Dict
	for cfg in ArtifactCuiLianHalo.ToClassType():
		if cfg.haloLevel in ArtifactCuiLianHalo_Dict:
			print "GE_EXC, repeat haloLevel = (%s) in LoadArtifactCuiLianHaloConfig" % cfg.haloLevel
		ArtifactCuiLianHalo_Dict[cfg.haloLevel] = cfg
		cfg.Initproperty()
		
def LoadArtifactCuiLianBaseConfig():
	#神器装备淬炼基础属性加成
	global ArtifactCuiLianBase_Dict
	for cfg in ArtifactCuiLianBase.ToClassType():
		if cfg.cuiLianIndex in ArtifactCuiLianBase_Dict:
			print "GE_EXC, repeat cuiLianIndex = (%s) in LoadArtifactCuiLianBaseConfig" % cfg.cuiLianIndex
		cfg.InitProperty()
		ArtifactCuiLianBase_Dict[cfg.cuiLianIndex] = cfg
		
def LoadArtifactCuiLianLevelConfig():
	#神器装备淬炼等级配置
	global ArtifactCuiLianLevel_Dict
	for cfg in ArtifactCuiLianLevel.ToClassType():
		if cfg.cuiLianLevel in ArtifactCuiLianLevel_Dict:
			print "GE_EXC, repeat cuiLianLevel = (%s) in LoadArtifactCuiLianLevelConfig" % cfg.cuiLianLevel
		ArtifactCuiLianLevel_Dict[cfg.cuiLianLevel] = cfg
		
		
def LoadArtifactCuiLianSuiteConfig():
	#神器装备淬炼组合
	global ArtifactCuiLianSuite_Dict
	for cfg in ArtifactCuiLianSuite.ToClassType():
		if cfg.index in ArtifactCuiLianSuite_Dict:
			print "GE_EXC, repeat index = (%s) in LoadArtifactCuiLianSuiteConfig" % cfg.index
		ArtifactCuiLianSuite_Dict[cfg.index] = cfg.artifact
	
def LoadArtifactCuiLianSuite7Config():
	#神器装备淬炼第七号组合最小等级配置
	global ArtifactCuiLianSuite7_Dict
	for cfg in ArtifactCuiLianSuite7.ToClassType():
		if cfg.minLevel in ArtifactCuiLianSuite7_Dict:
			print "GE_EXC, repeat minLevel = (%s) in LoadArtifactCuiLianSuite7Config" % cfg.minLevel
		ArtifactCuiLianSuite7_Dict[cfg.minLevel] = cfg.suiteIndex
		
def LoadArtifactCuiLianIndexConfig():
	global	ArtifactCuiLianIndex_Dict
	for cfg in ArtifactCuiLianIndex.ToClassType():
		if (cfg.pos1, cfg.lev1, cfg.pos2, cfg.lev2) in ArtifactCuiLianIndex_Dict:
			print "GE_EXC, repeat (pos1,lev1,pos2,lev2) = (%s,%s,%s,%s) in LoadArtifactCuiLianSuite7Config" % (cfg.pos1, cfg.lev1, cfg.pos2, cfg.lev2)
		ArtifactCuiLianIndex_Dict[(cfg.pos1, cfg.lev1, cfg.pos2, cfg.lev2)] = (cfg.index, cfg.level)
		
def LoadArtifactCuiLianConfig():
	#神器装备淬炼组合加成
	global ArtifactCuiLian_Dict
	for cfg in ArtifactCuiLian.ToClassType():
		if cfg.suiteIndex in ArtifactCuiLian_Dict:
			print "GE_EXC, repeat suiteIndex = (%s) in LoadArtifactCuiLianConfig" % cfg.suiteIndex
		cfg.InitProperty()
		ArtifactCuiLian_Dict[cfg.suiteIndex] = cfg
		
def LoadEquipmentEnchant():
	#装备附魔
	from Game.Item import EquipmentForing
	for cfg in EquipmentEnchant.ToClassType():
		if cfg.EnchantLevel in EquipmentForing.Equipment_Enchant_Dict:
			print "GE_EXC,repeat EnchantLevel(%s) in LoadEquipmentEnchant" % cfg.EnchantLevel
		EquipmentForing.Equipment_Enchant_Dict[cfg.EnchantLevel] = cfg
		
def LoadHallowsConfig():
	#圣器配置
	from Game.Role.Obj import Base
	from Game.Item import Item
	global ItemCfg_Dict
	for Ha in HallowsConfig.ToClassType():
		if Ha.coding in ItemCfg_Dict:
			print "GE_EXC, repeat coding in LoadHallowsConfig, (%s)" % Ha.coding
		randomprop = Random.RandomRate()
		for rate, prop in Ha.proprate:
			randomprop.AddRandomItem(rate, prop)
		Ha.PreCoding(randomprop)
		ItemCfg_Dict[Ha.coding] = Ha
		if Ha.coding in Base.Obj_Config:
			print "GE_EXC, LoadHallowsConfig repeat coding in Base.Obj_Config, (%s)" % Ha.coding
		Base.Obj_Config[Ha.coding] = Ha
		if Ha.coding in Base.Obj_Type_Fun:
			print "GE_EXC, repeat RegTypeObjFun. Ha,(%s)" % Ha.coding
		Base.Obj_Type_Fun[Ha.coding] = Item.Hallows
		GoodsSet.add(Ha.coding)

def ReloadHallowsConfig():
	global ItemCfg_Dict
	for Ha in HallowsConfig.ToClassType():
		#print "BLUE. ReloadHallowsConfig", Ha.ptmax[1]
		oldHa = ItemCfg_Dict.get(Ha.coding)
		if not oldHa:
			print "GE_EXC ReloadHallowsConfig error （%s）" % Ha.coding
		oldHa.ptmax = Ha.ptmax


def LoadHallowsPropLevelConfig():
	from Game.Item import HallowsForing
	HallowsProplevelDict = HallowsForing.HallowsProplevelDict
	HallowsProplevelRandom = HallowsForing.HallowsProplevelRandom
	HallowsInitProplevelRandom = HallowsForing.HallowsInitProplevelRandom
	for config in HallowsPropLevelConfig.ToClassType():
		if config.PropLevel in HallowsProplevelDict:
			print "GE_EXC, repeat PropLevel in LoadHallowsPropLevelConfig, (%s)" % config.PropLevel
		HallowsProplevelRandom.AddRandomItem(config.Rate, config.PropLevel)
		HallowsInitProplevelRandom.AddRandomItem(config.InitRate, config.PropLevel)
		HallowsProplevelDict[config.PropLevel] = config.Percent

def LoadHallowsEnchantConfig():
	from Game.Item import HallowsForing
	HallowsEnchantDict = HallowsForing.HallowsEnchantDict
	for config in HallowsEnchantConfig.ToClassType():
		if config.EnChantsLevel in HallowsEnchantDict:
			print "GE_EXC, repeat EnChantsLevel in LoadHallowsEnchantConfig, (%s)" % config.EnChantsLevel
		HallowsEnchantDict[config.EnChantsLevel] = config

def LoadHallowsShenzaoConfig():
	from Game.Item import HallowsForing
	HallowShenzaoDict = HallowsForing.HallowShenzaoDict
	for config in HallowsShenzaoConfig.ToClassType():
		if config.shenzaoLevel in HallowShenzaoDict:
			print "GE_EXC, repeat EnChantsLevel in LoadHallowsShenzaoConfig, (%s)" % config.shenzaoLevel
		config.InitProperty()
		HallowShenzaoDict[config.shenzaoLevel] = config

def LoadHallowsGemConfig():
	from Game.Item import HallowsGem
	for cfg in HallowsGemConfig.ToClassType():
		if cfg.GemID in HallowsGem.Hallows_Gem_Dict:
			print "GE_EXC,repeat GemID in HallowsGem, (%s)"	% cfg.GemID
		HallowsGem.Hallows_Gem_Dict[cfg.GemID] = cfg
		cfg.Check()
	for cfg in HallowsGem.Hallows_Gem_Dict.itervalues():
		cfg.Check_2()
		
def LoadHallowsSealingSpirit():
	#雕纹封灵
	from Game.Item import HallowsGem
	for cfg in HallowsGemSealing.ToClassType():
		if cfg.SealingLevel in HallowsGem.Hallows_Spirit_Dict:
			print "GE_EXC,repeat SealingLevel(%s) in Hallows_Spirit_Dict", cfg.SealingLevel
		HallowsGem.Hallows_Spirit_Dict[cfg.SealingLevel] = cfg

class EquipmentUnlockCost(TabFile.TabLine):
	'''
	解锁装备新洗练消耗
	'''
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("EquipmentUnlockCost.txt")
	def __init__(self):
		self.unlockNum = int
		self.unbindRMB = int

def LoadEquipmentUnlockCost():
	from Game.Item import EquipmentForing
	
	for cfg in EquipmentUnlockCost.ToClassType():
		if cfg.unlockNum in EquipmentForing.Equipment_UnlockCost_Dict:
			print "GE_EXC,repeat unlockNum(%s) in LoadEquipmentUnlockCost" % cfg.unlockNum
		EquipmentForing.Equipment_UnlockCost_Dict[cfg.unlockNum] = cfg
		
class EquipmentWashMaxPro(TabFile.TabLine):
	'''
	装备洗练每种属性对应的最大值
	'''
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("EquipmentWashMaxPro.txt")
	def __init__(self):
		self.pt = int
		self.maxPv = int
		
def LoadEquipmentWashMaxPro():
	from Game.Item import EquipmentForing
	
	for cfg in EquipmentWashMaxPro.ToClassType():
		if cfg.pt in EquipmentForing.Equipment_WashMaxPro_Dict:
			print "GE_EXC,repeat pt(%s) in EquipmentForing.Equipment_WashMaxPro_Dict" % cfg.pt
		EquipmentForing.Equipment_WashMaxPro_Dict[cfg.pt] = cfg
		
class EquipmentWashBase(TabFile.TabLine):
	'''
	装备洗练星级基础配置
	'''
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("EquipmentWashBase.txt")
	def __init__(self):
		self.starlevel = int
		self.pro = int
		self.proportion = self.GetEvalByString
		self.ptlist = self.GetEvalByString
		
def LoadEquipmentWashBase():
	from Game.Item import EquipmentForing
	
	for cfg in EquipmentWashBase.ToClassType():
		if cfg.starlevel in EquipmentForing.Equipment_WashBase_Dict:
			print "GE_EXC,repeat starlevel(%s) in LoadEquipmentWashBase" % cfg.starlevel
		EquipmentForing.Equipment_WashBase_Dict[cfg.starlevel] = cfg
		
class EquipmentWashStar(TabFile.TabLine):
	'''
	装备洗练度对应的星级
	'''
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("EquipmentWashStar.txt")
	def __init__(self):
		self.ptList = self.GetEvalByString
		self.washStar = self.GetEvalByString
		self.listStar = int
	
	def StarRandom(self):
		self.starRandom = Random.RandomRate()
		from Game.Item import EquipmentForing
		for star in self.washStar:
			starCfg = EquipmentForing.Equipment_WashBase_Dict.get(star)
			if not starCfg:
				return
			self.starRandom.AddRandomItem(starCfg.pro, star)
			
def LoadEquipmentWashStar():
	from Game.Item import EquipmentForing
	
	for cfg in EquipmentWashStar.ToClassType():
		ptset = (cfg.ptList[0], cfg.ptList[1])
		if ptset in EquipmentForing.Equipment_WashStar_Dict:
			print "GE_EXC, repeat minptlist(%s) and maxptlist(%s) in LoadEquipmentWashStar" % (cfg.ptList[0], cfg.ptList[1])
		cfg.StarRandom()
		EquipmentForing.Equipment_WashStar_Dict[ptset] = cfg
		
		
def LoadJTCrystalConfig():
	global JTCrystalConfigDict
	for config in JTCrystal.ToClassType():
		if config.crystalID in JTCrystalConfigDict:
			print "GE_EXC, repeat config.crystalID(%s) in JTCrystalConfigDict" % config.crystalID
		JTCrystalConfigDict[config.crystalID] = config


def LoadJTCrystalSealing():
	global JTCrystalSealingConfigDict
	for config in JTCrystalSealing.ToClassType():
		if config.level in JTCrystalSealingConfigDict:
			print "GE_EXC, repeat config.level(%s) in JTCrystalSealingConfigDict" % config.level
		JTCrystalSealingConfigDict[config.level] = config

def LoadMagicSpirit():
	from Game.Role.Obj import Base
	from Game.Item import Item
	global MagicSpirit_Dict
	for cfg in MagicSpirit.ToClassType():
		coding = cfg.coding
		needItem = cfg.needItem
		needItemEx = cfg.needItemEx
		
		#构建属性随机器
		cfg.propertyRandom = Random.RandomRate()
		for pt, pv, rate in cfg.propertyPool:
			cfg.propertyRandom.AddRandomItem(rate, (pt,pv))
		
		#构建技能点类型随机器
		cfg.skillPointRandom = Random.RandomRate()
		for st,rate in cfg.skillPointPool:
			cfg.skillPointRandom.AddRandomItem(rate, st)
		
		#构建技能点数值随机器
		cfg.skillPointRandomEx = Random.RandomRate()
		for rangeDown, rangeUp, rate in cfg.skillPointRange:
			cfg.skillPointRandomEx.AddRandomItem(rate, [rangeDown, rangeUp])
		
		#装载配置
		if coding in MagicSpirit_Dict:
			print "GE_EXC,repeat coding(%s) in MagicSpirit_Dict" % coding 
		MagicSpirit_Dict[coding] = cfg
		
		if coding in Base.Obj_Config:
			print "GE_EXC, LoadMagicSpirit repeat coding(%s) in Base.Obj_Config" % coding
		Base.Obj_Config[coding] = cfg
		
		if coding in Base.Obj_Type_Fun:
			print "GE_EXC, LoadMagicSpirit repeat RegTypeObjFun. coding(%s)" % coding
		Base.Obj_Type_Fun[coding] = Item.MagicSpirit
		
		if (needItem and needItemEx) and (needItem[0] == needItemEx[0]):
			print "GE_EXC,LoadMagicSpirit needItem[0] == needItemEx[0]"


#装备转生配置
class EquipmentZhuanShengConfig(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("EquipmentZhuanSheng.txt")
	def __init__(self):
		self.srcType = int
		self.desType = int
		self.needLevel = int
		self.itemType1 = int
		self.cnt1 = int
		self.itemType2 = int
		self.cnt2 = int
		self.itemType3 = int
		self.cnt3 = int
		self.itemType4 = int
		self.cnt4 = int


def LoadZhuanShengConfig():
	#装备转生配置
	from Game.Item.EquipmentForing import Equipment_ZhuanSheng_Dict
	for EUC in EquipmentZhuanShengConfig.ToClassType():
		if EUC.srcType in Equipment_ZhuanSheng_Dict:
			print "GE_EXC, repeat EUC.srcType in LoadZhuanShengConfig, (%s)" % EUC.srcType
		if (EUC.itemType1 and EUC.cnt1 == 0) or (EUC.itemType2 and EUC.cnt2 == 0) or (EUC.itemType3 and EUC.cnt3 == 0):
			print "GE_EXC, LoadZhuanShengConfig, srcType=(%s) has itemtype is no cnt" % EUC.srcType
		Equipment_ZhuanSheng_Dict[EUC.srcType] = EUC	
		
#装备进化配置
class EquipmentEvolveConfig(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("EquipmentEvolve.txt")
	def __init__(self):
		self.srcType = int
		self.desType = int
		self.needLevel = int
		self.itemType1 = int
		self.cnt1 = int
		self.itemType2 = int
		self.cnt2 = int
		self.itemType3 = int
		self.cnt3 = int
		self.itemType4 = int
		self.cnt4 = int


def LoadEvolveConfig():
	#装备进化配置
	from Game.Item.EquipmentForing import Equipment_Evolve_Dict
	for EUC in EquipmentEvolveConfig.ToClassType():
		if EUC.srcType in Equipment_Evolve_Dict:
			print "GE_EXC, repeat EUC.srcType in LoadEvolveConfig, (%s)" % EUC.srcType
		if (EUC.itemType1 and EUC.cnt1 == 0) or (EUC.itemType2 and EUC.cnt2 == 0) or (EUC.itemType3 and EUC.cnt3 == 0):
			print "GE_EXC, LoadEvolveConfig, srcType=(%s) has itemtype is no cnt" % EUC.srcType
		Equipment_Evolve_Dict[EUC.srcType] = EUC	


class GemForge(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("GemForge.txt")
	def __init__(self):
		self.forgeId = int
		self.gemCodingA = int
		self.gemCodingB = int
		self.needItemA = self.GetEvalByString
		self.needItemB = self.GetEvalByString
		self.returnItem = self.GetEvalByString


def LoadGemForge():
	from Game.Item.Gem import GemForge_ForgeConfig_Dict
	for cfg in GemForge.ToClassType():
		forgeId = cfg.forgeId
		if forgeId in GemForge_ForgeConfig_Dict:
			print "GE_EXC, repeat forgeId(%s) in GemForge_ForgeConfig_Dict" % forgeId
		GemForge_ForgeConfig_Dict[forgeId] = cfg
	
	
class ForgeStoneTransform(TabFile.TabLine):
	FilePath = ITEM_FILE_FOLDER_PATH.FilePath("ForgeStoneTransform.txt")
	def __init__(self):
		self.transformId = int
		self.forgeStoneA = self.GetEvalByString
		self.needUnbindRMB = int
		self.forgeStoneB = self.GetEvalByString
	
	
def LoadForgeStoneTransform():
	from Game.Item.Gem import ForgeStone_TransformConfig_Dict
	for cfg in ForgeStoneTransform.ToClassType():
		transformId = cfg.transformId
		if transformId in ForgeStone_TransformConfig_Dict:
			print "GE_EXC, repeat transformId(%s) in ForgeStone_TransformConfig_Dict" % transformId
		ForgeStone_TransformConfig_Dict[transformId] = cfg
		
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadItemConfig()
		LoadEquipmentConfig()
		LoadEquipmentSellConfig()
		LoadPackageSizeConfig()
		LoadGridOpenConfig()
		LoadStrengthen()
		LoadUpgradeConfig()
		LoadGodcastConfig()
		LoadEquipmentSuitConfig()
		LoadEquipmentGem()
		LoadGemSealingSpirit()
		LoadArtifactConfig()
		LoadArtifactStrengConfig()
		LoadArtifactUpgradeConfig()
		LoadArtifactGem()
		LoadArtifactGemSealing()
		LoadArtifactSellConfig()
		LoadArtifactSuitConfig()
		LoadHallowsConfig()
		LoadHallowsPropLevelConfig()
		LoadHallowsEnchantConfig()
		LoadHallowsShenzaoConfig()
		LoadHallowsGemConfig()
		LoadHallowsSealingSpirit()
		LoadEquipmentEnchant()
		LoadEquipmentWashBase()
		LoadEquipmentWashStar()
		LoadEquipmentWashMaxPro()
		LoadEquipmentUnlockCost()
		LoadJTCrystalConfig()
		LoadJTCrystalSealing()
		LoadMagicSpirit()
		LoadEvolveConfig()
		LoadZhuanShengConfig()
		LoadArtifactCuiLianHaloConfig()
		LoadArtifactCuiLianSuiteConfig()
		LoadArtifactCuiLianConfig()
		LoadArtifactCuiLianBaseConfig()
		LoadArtifactCuiLianLevelConfig()
		LoadArtifactCuiLianIndexConfig()
		LoadArtifactCuiLianSuite7Config()
		LoadGemForge()
		LoadForgeStoneTransform()
