#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ElementSpirit.ElementBrandConfig")
#===============================================================================
# 元素印记 config
#===============================================================================
import random
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile
from Game.Property import PropertyEnum


if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("ElementSpirit")
	
	#基本配置 {brandType:{brandColor:{brandLevel:cfg,},},}
	ElementBrand_BaseConfig_Dict = {}
	
	#印记类型 集合 set(brandType1,brandType2,...)
	ElementBrand_BrandType_RandomSet = set()
	ElementBrand_BrandType_RandomObj = Random.RandomRate()
	
	#印记雕刻 {sculptureType:cfg,}
	ElementBrand_SculptureConfig_Dict = {}
	
	#印记品阶值控制配置  {brandColor:cfg,}
	ElementBrand_TalentControl_Dict = {}
	
	#印记镶嵌孔 开放控制 {posIndex:needElementSpiritId,}
	ElementBrand_PosControl_Dict = {}
	
	#印记洗练配置  {proType:randomObj,}
	ElementBrand_WashConfig_Dict = {}
	
	#印记洗练属性类型配置{proType:maxProValue,}
	ElementBrand_ProTypeValue_Dict = {}
	
	
class ElementBrandBase(TabFile.TabLine):
	'''
	元素印记基本配置类
	'''
	FilePath = FILE_FLODER_PATH.FilePath("ElementBrandBase.txt")
	def __init__(self):
		self.brandType = int
		self.brandColor = int
		self.brandLevel = int
		self.brandName = str
		self.canEquip = int
		self.canShenJi = int
		self.shenJiNeedItem = self.GetEvalByString
		self.shenJiNeedBrandCnt = int
		self.shenJiNeedBrand = self.GetEvalByString
		self.canFenjie = int
		self.fenJieNeedRMB = int
		self.fenJieAddItem = self.GetEvalByString
		self.fenJieAddBrand = self.GetEvalByString
		self.tanlentLimit = int
		
		#属性万分比
		self.attack_pt = int
		self.attack_mt = int
		self.maxhp_t = int
		self.crit_t = int
		self.critpress_t = int
		self.parry_t = int
		self.puncture_t = int
		self.antibroken_t = int
		self.notbroken_t = int
		
		self.maxProCnt = int
		
		self.transmitAddItem = self.GetEvalByString
		self.transmitAddBrand = self.GetEvalByString
	
	def pre_process(self):
		self.InitPPT()
		if self.fenJieAddBrand:
			self.fenJieNeedPackageSize = len(self.fenJieAddBrand)
		else:
			self.fenJieNeedPackageSize = 0
	
	def InitPPT(self):
		'''
		预处理万分比属性
		'''
		self.ppt_dict = {}
		self.ppt_dict[PropertyEnum.attack_p] = self.attack_pt
		self.ppt_dict[PropertyEnum.attack_m] = self.attack_mt
		self.ppt_dict[PropertyEnum.maxhp] = self.maxhp_t
		self.ppt_dict[PropertyEnum.crit] = self.crit_t
		self.ppt_dict[PropertyEnum.critpress] = self.critpress_t
		self.ppt_dict[PropertyEnum.parry] = self.parry_t
		self.ppt_dict[PropertyEnum.puncture] = self.puncture_t
		self.ppt_dict[PropertyEnum.antibroken] = self.antibroken_t
		self.ppt_dict[PropertyEnum.notbroken] = self.notbroken_t	


def GetCfgByTCL(brandType, brandColor, brandLevel):
	'''
	获取对应 类型 品阶 等级 的印记配置
	'''
	typeDictDict = ElementBrand_BaseConfig_Dict.get(brandType, {})
	colorDict = typeDictDict.get(brandColor, {})
	brandCfg = colorDict.get(brandLevel, None)
	return brandCfg
	

def LoadElementBrandBase():
	'''
	加载并处理元素印记基本配置
	'''
	global ElementBrand_BaseConfig_Dict
	global ElementBrand_BrandType_RandomSet
	global ElementBrand_BrandType_RandomObj
	for cfg in ElementBrandBase.ToClassType():
		brandType = cfg.brandType		
		brandColor = cfg.brandColor
		brandLevel = cfg.brandLevel
		
		shenJiNeedBrandCnt = cfg.shenJiNeedBrandCnt
		shenJiNeedBrand = cfg.shenJiNeedBrand
		if shenJiNeedBrandCnt and not shenJiNeedBrand:
			print "GE_EXC,LoadElementBrandBase::shenJiNeedBrandCnt and not shenJiNeedBrand in brandType(%s),brandColor(%s),brandLevel(%s)" % (brandType,brandColor,brandLevel)
		
		if brandType not in ElementBrand_BrandType_RandomSet and cfg.canEquip:
			ElementBrand_BrandType_RandomSet.add(brandType)
			ElementBrand_BrandType_RandomObj.AddRandomItem(1, brandType)
		
		brandTypeDictDict = ElementBrand_BaseConfig_Dict.setdefault(brandType, {})
		brandColorDict = brandTypeDictDict.setdefault(brandColor, {})
		if brandLevel in brandColorDict:
			print "GE_EXC,repeat brandLevel(%s) with brandType(%s) and brandColor(%s) in ElementBrand_BaseConfig_Dict" % (brandType, brandColor, brandLevel)
		cfg.pre_process()
		brandColorDict[brandLevel] = cfg


class ElementBrandSculpture(TabFile.TabLine):
	'''
	元素印记雕刻配置类
	'''
	FilePath = FILE_FLODER_PATH.FilePath("ElementBrandSculpture.txt")
	def __init__(self):
		self.sculptureType = int
		self.needItem = self.GetEvalByString
		self.needRMBQ = int
		self.colorPool = self.GetEvalByString
	
	
	def pre_process(self):
		'''
		转载品阶随机对象
		'''
		self.colorRandomObj = Random.RandomRate()
		for color, rateValue in self.colorPool:
			self.colorRandomObj.AddRandomItem(rateValue, color)
	
	
	def random_color(self):
		'''
		随机品阶值
		'''
		return self.colorRandomObj.RandomOne()


def LoadElementBrandSculpture():
	'''
	加载元素印记雕刻配置
	'''
	global ElementBrand_SculptureConfig_Dict
	for cfg in ElementBrandSculpture.ToClassType():
		sculptureType = cfg.sculptureType
		if sculptureType in ElementBrand_SculptureConfig_Dict:
			print "GE_EXC,repeat sculptureType(%s) in ElementBrand_SculptureConfig_Dict" % sculptureType
		cfg.pre_process()
		ElementBrand_SculptureConfig_Dict[sculptureType] = cfg


class ElementBrandTalentControl(TabFile.TabLine):
	'''
	元素印记品阶值控制类
	'''
	FilePath = FILE_FLODER_PATH.FilePath("ElementBrandTalentControl.txt")
	def __init__(self):
		self.brandColor = int
		self.talentControl = self.GetEvalByString
	
	
	def pre_process(self):
		'''
		转载品质值区段随机对象
		'''
		self.talentRange_RandomObj = Random.RandomRate()
		for rangeDown, rangeUp, rateValue in self.talentControl:
			if rangeUp < rangeDown:
				print "GE_EXC,ElementBrandTalentControl::config error rangeUp(%s) < rangeDown(%s) in brandColor(%s)" % (rangeUp, rangeDown, self.brandColor)
				continue 
			self.talentRange_RandomObj.AddRandomItem(rateValue, [rangeDown, rangeUp])
		
	
	def random_tanlent(self):
		'''
		随机 品质值
		'''
		return random.randint(*self.talentRange_RandomObj.RandomOne())


def LoadElementBrandTalentControl():
	'''
	加载印记品阶值控制配置
	'''
	global ElementBrand_TalentControl_Dict
	for cfg in ElementBrandTalentControl.ToClassType():
		brandColor = cfg.brandColor
		if brandColor in ElementBrand_TalentControl_Dict:
			print "GE_EXC,repeat brandColor(%s) in ElementBrand_TalentControl_Dict" % brandColor
		cfg.pre_process()
		ElementBrand_TalentControl_Dict[brandColor] = cfg


def RandomSculptureDataByType(sculptureType):
	'''
	上层确保sculptureType正确存在
	根据雕刻类型 返回随机的雕刻结果
	'''
	if sculptureType not in ElementBrand_SculptureConfig_Dict:
		print "GE_EXC,RandomSculptureDataByType,error sculptureType(%s)" % sculptureType
		return None
	
	#随机印记类型
	brandType = ElementBrand_BrandType_RandomObj.RandomOne()
	
	#随机印记品阶
	sculptureCfg = ElementBrand_SculptureConfig_Dict[sculptureType]
	brandColor = sculptureCfg.random_color()
	
	#随机印记品质值
	if brandColor not in ElementBrand_TalentControl_Dict:
		print "GE_EXC, RandomSculptureDataByType,brandColor(%s) in ElementBrand_SculptureConfig_Dict and not in ElementBrand_TalentControl_Dict" % brandColor
		return None
	
	talentControlCfg = ElementBrand_TalentControl_Dict[brandColor]
	talentValue = talentControlCfg.random_tanlent()
	
	return [brandType, brandColor, talentValue]


class ElementBrandPosControl(TabFile.TabLine):
	'''
	印记镶嵌位置控制类
	'''
	FilePath = FILE_FLODER_PATH.FilePath("ElementBrandPosControl.txt")
	def __init__(self):
		self.posIndex = int
		self.needElementSpiritId = int


def LoadElementBrandPosControl():
	global ElementBrand_PosControl_Dict
	for cfg in ElementBrandPosControl.ToClassType():
		posIndex = cfg.posIndex
		needElementSpiritId = cfg.needElementSpiritId
		if posIndex in ElementBrand_PosControl_Dict:
			print "GE_EXC,repeat posIndex（%s) in ElementBrand_PosControl_Dict" % posIndex
		ElementBrand_PosControl_Dict[posIndex] = needElementSpiritId


class ElementBrandWash(TabFile.TabLine):
	'''
	印记洗练配置
	'''
	FilePath = FILE_FLODER_PATH.FilePath("ElementBrandWash.txt")
	def __init__(self):
		self.proType = int
		self.proName = str
		self.starLevel = int
		self.rateValue = int
		self.percentRange = self.GetEvalByString
		self.maxProValue = int
	

def LoadElementBrandWash():
	'''
	加载洗练配置
	'''
	global ElementBrand_WashConfig_Dict
	global ElementBrand_ProTypeValue_Dict
	for cfg in ElementBrandWash.ToClassType():
		proType = cfg.proType
		rateValue = cfg.rateValue
		percentRange = cfg.percentRange
		maxProValue = cfg.maxProValue
		randomObj = ElementBrand_WashConfig_Dict.setdefault(proType, Random.RandomRate())
		randomObj.AddRandomItem(rateValue, percentRange)
		ElementBrand_ProTypeValue_Dict[proType] = maxProValue


def WashBrandByData(lockProiTypeList=[], washCnt=1):
	'''
	根据 印记已经拥有的属性类型 lockProiTypeList 洗练出 washCnt 条属性
	@return: 洗练出来的属性字典  {proType:proValue,}
	'''
	newProDict = {}	
	proTypeRandom = Random.RandomRate()
	for proType in ElementBrand_WashConfig_Dict.keys():
		if proType not in lockProiTypeList:
			proTypeRandom.AddRandomItem(1, proType)
	
	newProTypeList = proTypeRandom.RandomMany(washCnt)
	for newProType in newProTypeList:
		newProDict[newProType] = random.randint(*ElementBrand_WashConfig_Dict[newProType].RandomOne())
	
	return newProDict


def LoadConfig():
	'''
	加载配置
	'''
	LoadElementBrandBase()
	LoadElementBrandSculpture()
	LoadElementBrandTalentControl()
	LoadElementBrandPosControl()
	LoadElementBrandWash()

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadConfig()
