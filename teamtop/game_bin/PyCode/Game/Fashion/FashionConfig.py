#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fashion.FashionConfig")
#===============================================================================
# 时装配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	FASHION_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FASHION_FILE_FOLDER_PATH.AppendPath("Fashion")
	
	FASHION_STAR_DICT = {}	#时装升星，通过部件判断
	STAR_CODING_SET = set()	#时装升星通过coding判断的列表
	FASHION_ORDER_DICT = {}	#时装升阶
	ORDER_CODING_SET = set()#时装升阶通过coding判断的列表
	FASHION_SUIT_DICT = {}	#时装套装
	FASHION_WING_DICT = {}	#时装翅膀
	FASHION_SELL_DICT = {}	#时装出售
	SELL_CODING_SET = set()	#时装出售通过coding判断的列表
	FASHION_HOLE_DICT = {}	#时装光环
	FASHION_GOR_DICT = {}	#时装华丽度
	FASHION_WARDROBE_DICT = {}#时装衣柜
	
class FashionConfig(TabFile.TabLine):
	#时装
	ITEM_R = 5#用于识别普通物品/装备/神器/圣器/时装
	useFun = None
	canOverlap = False#默认不可以叠加
	canTrade = False
	kinds = 7
	FilePath = FASHION_FILE_FOLDER_PATH.FilePath("Fashion.txt")
	def __init__(self):
		self.coding 	= int
		self.name 		= str
		self.wingId 	= int
		self.needlevel 	= int
		self.grade 		= int
		self.posType 	= int
		self.suitId 	= int
		self.canSell 	= int
		self.salePrice 	= int
		self.Idepro 	= int
		self.FaileIdepro= int
		self.needItem 	= self.GetEvalByString
		self.gorgeous	= int
		self.idegorgeous= int
		self.jiaMi = int
		#基础属性
		self.Basept1 = int
		self.Basepv1 = int
		self.Basept2 = int
		self.Basepv2 = int
		#升星属性
		self.Starpt1 = int
		self.Starpv1 = self.GetEvalByString
		self.Starpt2 = int
		self.Starpv2 = self.GetEvalByString
		#升价属性
		self.Uppt1	 = int
		self.Uppv1	 = self.GetEvalByString
		self.Uppt2	 = int
		self.Uppv2	 = self.GetEvalByString
		#鉴定属性
		self.Jdpt1 = int
		self.Jdpv1 = self.GetEvalByString
		self.Jdpt2 = int
		self.Jdpv2 = self.GetEvalByString
		self.Jdpt3 = int
		self.Jdpv3 = self.GetEvalByString
		#是否需要记录日志
		self.needLog = int
		
	def InitProperty(self):
		self.p_dict = {}
		if self.Basept1 and self.Basepv1:
			self.p_dict[self.Basept1] = self.Basepv1
		if self.Basept2 and self.Basepv2:
			self.p_dict[self.Basept2] = self.Basepv2
			
		self.Star_p_dict = {}
		if self.Starpt1 and self.Starpv1:
			self.Star_p_dict[self.Starpt1] = self.Starpv1
		if self.Starpt2 and self.Starpv2:
			self.Star_p_dict[self.Starpt2] = self.Starpv2
		
		self.Up_p_dict = {}
		if self.Uppt1 and self.Uppv1:
			self.Up_p_dict[self.Uppt1] = self.Uppt1
		if self.Uppt1 and self.Uppv1:
			self.Up_p_dict[self.Uppt1] = self.Uppt1
			
		self.Jd_p_dict = {}
		if self.Jdpt1 and self.Jdpv1:
			self.Jd_p_dict[self.Jdpt1] = self.Jdpv1
		if self.Jdpt2 and self.Jdpv2:
			self.Jd_p_dict[self.Jdpt2] = self.Jdpv2
		if self.Jdpt3 and self.Jdpv3:
			self.Jd_p_dict[self.Jdpt3] = self.Jdpv3
			
class FashionStar(TabFile.TabLine):
	#时装升星
	FilePath = FASHION_FILE_FOLDER_PATH.FilePath("FashionStar.txt")
	def __init__(self):
		self.posType  = int
		self.starNum  = int
		self.nextStar = int
		self.needItem = self.GetEvalByString
		self.minLucky = int
		self.maxLucky = int
		self.baseLucky= int
		self.addLucky = self.GetEvalByString
		self.Starcoding = int

class FashionUp(TabFile.TabLine):
	#时装升阶
	FilePath = FASHION_FILE_FOLDER_PATH.FilePath("FashionUp.txt")
	def __init__(self):
		self.posType  = int
		self.order    = int
		self.nextOrder= int
		self.needItem = self.GetEvalByString
		self.minLucky = int
		self.maxLucky = int
		self.baseLucky= int
		self.addLucky = self.GetEvalByString
		self.Luckcoding= int
		
class FashionSuit(TabFile.TabLine):
	#时装套装
	FilePath = FASHION_FILE_FOLDER_PATH.FilePath("FashionSuit.txt")
	def __init__(self):
		self.suitId	 = int
		self.needCnt = int
		self.pt1	 = int
		self.pv1	 = int
		self.pt2	 = int
		self.pv2	 = int
		
class FashionWing(TabFile.TabLine):
	#时装ID对应道具ID配置表
	FilePath = FASHION_FILE_FOLDER_PATH.FilePath("FashionWing.txt")
	def __init__(self):
		self.wingId = int
		self.coding = int
		self.name   = str

class FashionSell(TabFile.TabLine):
	#时装出售配置表
	FilePath = FASHION_FILE_FOLDER_PATH.FilePath("FashionSell.txt")
	def __init__(self):
		self.posType	= int
		self.order		= int
		self.backItem	= self.GetEvalByString
		
class FashionHole(TabFile.TabLine):
	#时装光环
	FilePath = FASHION_FILE_FOLDER_PATH.FilePath("FashionHole.txt")
	def __init__(self):
		self.holeLevel	 = int
		self.nextLevel	 = int
		self.needexp	 = int
		self.needCoding	 = int
		self.addexp		 = int
		self.addpro1	 = int
		self.addpro2	 = int
		self.addpro3	 = int
		self.addpro4	 = int
		self.addpro5	 = int
		
class FashionGorgeous(TabFile.TabLine):
	#时装华丽度
	FilePath = FASHION_FILE_FOLDER_PATH.FilePath("FashionGorgeous.txt")
	def __init__(self):
		self.order	= int
		self.star	= int
		self.gorgeous=int
		
class FashionWardrobe(TabFile.TabLine):
	#时装衣柜
	FilePath = FASHION_FILE_FOLDER_PATH.FilePath("FashionWardrobe.txt")
	def __init__(self):
		self.level	 = int
		self.nextLevel	 = int
		self.needexp	 = int
		self.addpro1	 = int
		self.addpro2	 = int
		self.addpro3	 = int
		self.addpro4	 = int
		self.addpro5	 = int
		
def LoadFashionHole():
	global FASHION_HOLE_DICT
	
	for cfg in FashionHole.ToClassType():
		if cfg.holeLevel in FASHION_HOLE_DICT:
			print "GE_EXC, repeat holeLevel(%s) in LoadFashionHole" % cfg.holeLevel
		FASHION_HOLE_DICT[cfg.holeLevel] = cfg
		
def LoadFashionBase():
	#时装基础配置
	from Game.Role.Obj import Base
	from Game.Item import ItemConfig
	from Game.Fashion import FashionBase
	for EC in FashionConfig.ToClassType():
		if EC.coding in ItemConfig.ItemCfg_Dict:
			print "GE_EXC, repeat coding in LoadEquipmentConfig, (%s)" % EC.coding
		
		EC.InitProperty()
		
		ItemConfig.ItemCfg_Dict[EC.coding] = EC
		if EC.coding in Base.Obj_Config:
			print "GE_EXC, LoadEquipmentConfig repeat coding in Base.Obj_Config"
		Base.Obj_Config[EC.coding] = EC
		
		if EC.coding in Base.Obj_Type_Fun:
			print "GE_EXC, repeat RegTypeObjFun. EC,(%s)" % EC.coding
		Base.Obj_Type_Fun[EC.coding] = FashionBase.Fashion
		ItemConfig.GoodsSet.add(EC.coding)

def LoadFashionStar():
	global FASHION_STAR_DICT
	global STAR_CODING_SET
	
	for cfg in FashionStar.ToClassType():
		key = (cfg.posType, cfg.starNum)
		if key in FASHION_STAR_DICT:
			print "GE_EXC, repeat posType(%s) and starNum(%s) in LoadFashionStar" % (cfg.posType, cfg.starNum)
		FASHION_STAR_DICT[key] = cfg
		if cfg.posType > 10000:
			STAR_CODING_SET.add(cfg.posType)

def LoadFashionUp():
	global FASHION_ORDER_DICT
	global ORDER_CODING_SET
	for cfg in FashionUp.ToClassType():
		key = (cfg.posType, cfg.order)
		if key in FASHION_ORDER_DICT:
			print "GE_EXC, repeat posType(%s) and order(%s) in LoadFashionUp" % (cfg.posType, cfg.order)
		FASHION_ORDER_DICT[key] = cfg
		if cfg.posType > 10000:
			ORDER_CODING_SET.add(cfg.posType)
		
def LoadFashionSuit():
	global FASHION_SUIT_DICT
	
	for cfg in FashionSuit.ToClassType():
		if cfg.suitId in FASHION_SUIT_DICT:
			print "GE_EXC,repeat suitId(%s) in LoadFashionSuit" % cfg.suitId
		FASHION_SUIT_DICT[cfg.suitId] = cfg

def LoadFashionWing():
	global FASHION_WING_DICT
	
	for cfg in FashionWing.ToClassType():
		if cfg.wingId in FASHION_WING_DICT:
			print "GE_EXC,repeat wingId(%s) in LoadFashionWing" % cfg.wingId
		FASHION_WING_DICT[cfg.wingId] = cfg
	
def LoadFashionSell():
	global FASHION_SELL_DICT
	global SELL_CODING_SET
	
	for cfg in FashionSell.ToClassType():
		key = (cfg.posType, cfg.order)
		if key in FASHION_SELL_DICT:
			print "GE_EXC,repeat posType(%s) and order(%s) in LoadFashionSell" % (cfg.posType, cfg.order)
		FASHION_SELL_DICT[key] = cfg
		if cfg.posType > 10000:
			SELL_CODING_SET.add(cfg.posType)
		
def LoadFashionGorgeous():
	global FASHION_GOR_DICT
	
	for cfg in FashionGorgeous.ToClassType():
		key = (cfg.order, cfg.star)
		if key in FASHION_GOR_DICT:
			print "GE_EXC,repeat LoadFashionGorgeous order(%s) and star(%s)" % (cfg.order, cfg.star)
		FASHION_GOR_DICT[key] = cfg
		
def LoadFashionWardrobe():
	global FASHION_WARDROBE_DICT
	
	for cfg in FashionWardrobe.ToClassType():
		if cfg.level in FASHION_WARDROBE_DICT:
			print "GE_EXC,repeat LoadFashionWardrobe level(%s)" % cfg.level
		FASHION_WARDROBE_DICT[cfg.level] = cfg
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadFashionBase()
		LoadFashionStar()
		LoadFashionUp()
		LoadFashionSuit()
		LoadFashionWing()
		LoadFashionSell()
		LoadFashionHole()
		LoadFashionGorgeous()
		LoadFashionWardrobe()