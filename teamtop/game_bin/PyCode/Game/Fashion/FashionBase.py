#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fashion.FashionBase")
#===============================================================================
# 时装数据模块
#===============================================================================
from Game.Item import ItemBase, ItemConfig
from Game.Role.Obj import Base, EnumOdata
from Game.Role.Data import EnumObj, EnumTempObj, EnumInt8

class Fashion(ItemBase.ItemBase):
	#时装
	Obj_Type = Base.Obj_Type_Fashion
	def __init__(self, role, obj):
		ItemBase.ItemBase.__init__(self, role, obj)
		self.package = None
		#拥有者角色，在背包则是None
		self.owner = None
		#升星属性
		self.star_pro_dict = {}
		#升阶属性
		self.order_pro_dict = {}
		
	def AfterCreate(self, needInit = True):
		#先调用父类函数,载入相关配置
		Base.ObjBase.AfterCreate(self)
		#是否需要初始化,区别新装备或者获取了旧的
		if needInit is True:
			#私有数据初始化
			#时装升星
			self.odata[EnumOdata.enFashionStar] = [0, 0] #（星级， 幸运值）
			#时装升阶
			self.odata[EnumOdata.enFashionUpGrade] = [0, 0] #(阶数， 幸运值)
			
			
	def AfterLoad_Except(self):
		#数据库载入后调用
		Base.ObjBase.AfterLoad_Except(self)
		#缓存拥有者
		if self.package.ObjEnumIndex == EnumObj.En_RoleFashions:
			self.owner = self.package.role

	def AddLuckForStar(self, addLucky):
		#增加升星幸运值
		starData = self.odata.get(EnumOdata.enFashionStar)
		starData[1] += addLucky
		
	def GetStarData(self):
		#获取星阶数据
		return self.odata.get(EnumOdata.enFashionStar)
	
	def SetStarData(self, nextStar):
		#设置新的星级,幸运值清0
		self.odata[EnumOdata.enFashionStar] = [nextStar, 0]
	
	def ResetStarPro(self):
		#重置升星属性
		self.star_pro_dict = {}
		
	def GetStarPro(self):
		self.star_pro_dict = {}
		
		fashionId = self.cfg.coding
		#获取该时装的配置
		fashionCfg = ItemConfig.ItemCfg_Dict.get(fashionId)
		if not fashionCfg:
			print "GE_EXC,can not find coding(%s) in GetStarPro" % fashionId
			return
		#当前的星级
		nowStar = self.odata.get(EnumOdata.enFashionStar)[0]
		if nowStar <= 0:
			return self.star_pro_dict
		#升星属性1存在
		Starpt1, Starpv1 = fashionCfg.Starpt1, fashionCfg.Starpv1
		if Starpt1 and Starpv1:
			if len(Starpv1) < nowStar+1:#配置的该属性值列表有问题！
				print "GE_EXC, len(Starpv1)=(%s) < (%s) is wrong" % (len(Starpv1), nowStar+1)
				return self.star_pro_dict
			self.star_pro_dict[Starpt1] = self.star_pro_dict.get(Starpt1, 0) + Starpv1[nowStar]
		#升星属性2存在
		Starpt2, Starpv2 = fashionCfg.Starpt2, fashionCfg.Starpv2
		if Starpt2 and Starpv2:
			if len(Starpv2) < nowStar+1:#配置的该属性值列表有问题！
				print "GE_EXC, len(Starpv1)=(%s) < (%s) is wrong" % (len(Starpv2), nowStar+1)
				return self.star_pro_dict
			self.star_pro_dict[Starpt2] = self.star_pro_dict.get(Starpt2, 0) + Starpv2[nowStar]
		
		return self.star_pro_dict
	
	def GetOrderData(self):
		#获取阶数数据
		return self.odata.get(EnumOdata.enFashionUpGrade)
	
	def AddLuckyForOrder(self, addLucky):
		#增加升阶幸运值
		orderData = self.odata.get(EnumOdata.enFashionUpGrade)
		orderData[1] += addLucky
	
	def SetOrderData(self, nextOrder):
		#设置新的阶数
		self.odata[EnumOdata.enFashionUpGrade] = [nextOrder, 0]
		
	def ReSetOrderPro(self):
		#重置升阶属性
		self.order_pro_dict = {}
	
	def GetOrderPro(self):
		#获取升阶属性
		self.order_pro_dict = {}
		
		fashionId = self.cfg.coding
		#获取该时装的配置
		orderCfg = ItemConfig.ItemCfg_Dict.get(fashionId)
		if not orderCfg:
			print "GE_EXC,can not find coding(%s) in GetStarPro" % fashionId
			return
		
		nowOrder = self.odata.get(EnumOdata.enFashionUpGrade)[0]
		if nowOrder <= 0:
			return self.order_pro_dict
		
		Uppt1, Uppv1 = orderCfg.Uppt1, orderCfg.Uppv1
		if Uppt1 and Uppv1:#属性存在
			if len(Uppv1) < nowOrder+1:#配置的该属性值列表有问题！
				print "GE_EXC, len(Uppv1)=(%s) < (%s) is wrong" % (len(Uppv1), nowOrder+1)
				return self.order_pro_dict
			self.order_pro_dict[Uppt1] = self.order_pro_dict.get(Uppt1, 0) + Uppv1[nowOrder]
		Uppt2, Uppv2 = orderCfg.Uppt2, orderCfg.Uppv2
		if Uppt2 and Uppv2:#属性存在
			if len(Uppv2) < nowOrder+1:#配置的该属性值列表有问题！
				print "GE_EXC, len(Uppv1)=(%s) < (%s) is wrong" % (len(Uppv2), nowOrder+1)
				return self.order_pro_dict
			self.order_pro_dict[Uppt2] = self.order_pro_dict.get(Uppt2, 0) + Uppv2[nowOrder]
		return self.order_pro_dict
	
class FashionMgr(object):
	#管理时装的鉴定，套装属性
	def __init__(self, role):
		self.role = role
		self.suit_pro_dict = {}	#套装属性
		self.active_suit_set = set() #存套装属性ID
		self.ide_pro_dict = {} #时装总的鉴定属性
		self.hole_pro_dict = {}	#时装光环属性
		self.all_base_pro_dict = {}#所有激活时装的基础属性总和
		self.Gorgeous_dict = {}	#每个时装的华丽度
		self.total_gorgeous = 0	#总的华丽度
		#是否鉴定，时装阶数，套装ID
		# {coding --> [是否鉴定, 时装阶数, 套装ID, 时装星数, 鉴定额外幸运值, 升星祝福值， 升阶祝福值]}#激活的时装
		#注意：套装ID,这里已经不需要了！！！！
		#这里的阶数和星数只记录历史最高的，即2件相同时装，1件2星，一件3星，只记录3星的
		self.fashion_active_dict = role.GetObj(EnumObj.FashionData)
		self.InitFashionGorgeous()
	
	def InitFashionGorgeous(self):
		#初始化各个时装的华丽度
		for coding in self.fashion_active_dict.keys():
			if coding not in self.Gorgeous_dict:
				self.Gorgeous_dict[coding] = 0
			gorgeous = self.GetGorByCoding(coding)
			self.Gorgeous_dict[coding] = gorgeous
		for _, gorgeous in self.Gorgeous_dict.iteritems():
			self.total_gorgeous += gorgeous
		
	def GetGorByCoding(self, coding):
		#获取指定coding的时装华丽度
		data = self.fashion_active_dict.get(coding)
		if not data:
			return 0
		gorgeous = 0
		#基础华丽度
		item_cfg = ItemConfig.ItemCfg_Dict.get(coding)
		if item_cfg:
			if data[0]:
				gorgeous += item_cfg.idegorgeous
			else:
				gorgeous += item_cfg.gorgeous
		#根据阶数和星数取对应的华丽度
		star, order = data[3], data[1]
		from Game.Fashion import FashionConfig
		cfg = FashionConfig.FASHION_GOR_DICT.get((order, star))
		if cfg:
			gorgeous += cfg.gorgeous
		return gorgeous
		
	def SetGorByCoding(self, coding):
		#重新设置指定coding的时装华丽度
		gorgeous = self.GetGorByCoding(coding)
		self.Gorgeous_dict[coding] = gorgeous
		#重新算总的华丽度
		self.total_gorgeous = 0
		for _, gorgeous in self.Gorgeous_dict.iteritems():
			self.total_gorgeous += gorgeous
			
	def GetHaloPro(self):
		#获取时装光环属性
		self.hole_pro_dict = {}
		#获取时装光环等级，没有直接返回
		FashionHaloLevel = self.role.GetI8(EnumInt8.FashionHaloLevel)
		if not FashionHaloLevel: 
			#等级为0也需要同步次~因为玩家穿脱时界面显示的属性是有变化的
			SynRoleClient(self.role)
			return self.hole_pro_dict
		#获取光环等级对应的配置
		from Game.Fashion import FashionConfig
		holeCfg = FashionConfig.FASHION_HOLE_DICT.get(FashionHaloLevel)
		if not holeCfg:
			print "GE_EXC,can not find FashionHaloLevel(%s) in GetHaloPro" % FashionHaloLevel
			return self.hole_pro_dict
		
		#遍历激活的时装
		for coding, data in self.fashion_active_dict.iteritems():
			cfg = ItemConfig.ItemCfg_Dict.get(coding)
			if not cfg: continue
			fashion_pro = {}
			#基础属性
			for pt, pv in self.GetBasePro(coding).iteritems():
				fashion_pro[pt] = fashion_pro.get(pt, 0) + pv
			#获取升阶属性
			for pt, pv in self.GetOrderPro(coding).iteritems():
				fashion_pro[pt] = fashion_pro.get(pt, 0) + pv
			#获取升星属性
			for pt, pv in self.GetStarPro(coding).iteritems():
				fashion_pro[pt] = fashion_pro.get(pt, 0) + pv
			#根据时装的阶数获取对应的加成数值
			addpv = getattr(holeCfg, "addpro%s" % (data[1]+1))
			if not addpv:
				continue
			#根据光环等级获取对应的加成配置
			for pt, pv in fashion_pro.iteritems():
				self.hole_pro_dict[pt]= self.hole_pro_dict.get(pt, 0) + int(pv * (addpv / 100.0))
		#同步次客户端
		SynRoleClient(self.role)
		return self.hole_pro_dict
				
	def GetOrderPro(self, coding):
		#根据coding获取升阶属性
		pro_dict = {}
		#获取该时装的配置
		orderCfg = ItemConfig.ItemCfg_Dict.get(coding)
		if not orderCfg:
			print "GE_EXC,can not find coding(%s) in GetStarPro" % coding
			return pro_dict
		
		data = self.fashion_active_dict.get(coding)
		if not data:return pro_dict
		#当前的阶数
		nowOrder = data[1]
		if nowOrder <= 0:
			return pro_dict
		
		Uppt1, Uppv1 = orderCfg.Uppt1, orderCfg.Uppv1
		if Uppt1 and Uppv1:#属性存在
			if len(Uppv1) < nowOrder+1:#配置的该属性值列表有问题！
				print "GE_EXC, len(Uppv1)=(%s) < (%s) is wrong" % (len(Uppv1), nowOrder+1)
				return pro_dict
			pro_dict[Uppt1] = pro_dict.get(Uppt1, 0) + Uppv1[nowOrder]
		
		Uppt2, Uppv2 = orderCfg.Uppt2, orderCfg.Uppv2
		if Uppt2 and Uppv2:#属性存在
			if len(Uppv2) < nowOrder+1:#配置的该属性值列表有问题！
				print "GE_EXC, len(Uppv1)=(%s) < (%s) is wrong" % (len(Uppv2), nowOrder+1)
				return pro_dict
			pro_dict[Uppt2] = pro_dict.get(Uppt2, 0) + Uppv2[nowOrder]
		
		return pro_dict

	def GetBasePro(self, coding):
		#获取基础属性
		base_dict = {}
		cfg = ItemConfig.ItemCfg_Dict.get(coding)
		if not cfg:
			print "GE_EXC,can not find coding(%s) in GetStarPro" % coding
			return base_dict
		for pt, pv in cfg.p_dict.iteritems():
			base_dict[pt] = base_dict.get(pt, 0) + pv
		return base_dict

	def GetStarPro(self, coding):
		#获取升星属性
		star_pro = {}
		#获取该时装的配置
		fashionCfg = ItemConfig.ItemCfg_Dict.get(coding)
		if not fashionCfg:
			print "GE_EXC,can not find coding(%s) in GetStarPro" % coding
			return star_pro
		
		data = self.fashion_active_dict.get(coding)
		if not data:return star_pro
		#当前的星级
		nowStar = data[3]
		#升星属性1存在
		Starpt1, Starpv1 = fashionCfg.Starpt1, fashionCfg.Starpv1
		if Starpt1 and Starpv1:
			if len(Starpv1) < nowStar+1:#配置的该属性值列表有问题！
				print "GE_EXC, len(Starpv1)=(%s) < (%s) is wrong" % (len(Starpv1), nowStar+1)
				return star_pro
			star_pro[Starpt1] = star_pro.get(Starpt1, 0) + Starpv1[nowStar]
		#升星属性2存在
		Starpt2, Starpv2 = fashionCfg.Starpt2, fashionCfg.Starpv2
		if Starpt2 and Starpv2:
			if len(Starpv2) < nowStar+1:#配置的该属性值列表有问题！
				print "GE_EXC, len(Starpv1)=(%s) < (%s) is wrong" % (len(Starpv2), nowStar+1)
				return star_pro
			star_pro[Starpt2] = star_pro.get(Starpt2, 0) + Starpv2[nowStar]
		
		return star_pro

	def SetStarByCoding(self, coding, star):
		#设定时装的星级
		fashionData = self.fashion_active_dict.get(coding)
		if not fashionData:#没激活该时装
			return
		nowStar = fashionData[3]
		if nowStar >= star:
			return
		#清空祝福值
		fashionData[5] = 0
		#设定新的星级
		fashionData[3] = star
		#重新设定该时装的华丽度
		self.SetGorByCoding(coding)
		#重算基础属性
		self.ReSetAllBasePro()
		self.role.GetPropertyGather().ReSetRecountFashionFlag()
		#光环属性重算
		if self.role.GetI8(EnumInt8.FashionHaloLevel) > 0:
			self.role.GetPropertyGather().ReSetRecpintFashionHoleFlag()
		
	def ResetOrderbyCoding(self, coding, newOrder):
		#重新设定某个时装的阶数，假如该时装鉴定了并重算鉴定属性
		fashionData = self.fashion_active_dict.get(coding)
		if not fashionData:#没激活该时装
			return
		nowOrder = fashionData[1]
		if nowOrder >= newOrder:#记录的阶数大于新的阶数，值直接返回
			return
		#祝福值清0
		fashionData[6] = 0
		fashionData[1] = newOrder
		#重新设定该时装的华丽度
		self.SetGorByCoding(coding)
		#该时装未鉴定，不需要跑下面饿逻辑
		if fashionData[0] == 0:
			#同步客户端
			SynRoleClient(self.role)
			return
		#重算时装鉴定属性
		self.ResetFashionIde()
		self.role.ResetGlobalFashionProperty()
		#重算总的基础属性
		self.ReSetAllBasePro()
		self.role.GetPropertyGather().ReSetRecountFashionFlag()
		#需要重算光环属性
		if self.role.GetI8(EnumInt8.FashionHaloLevel) > 0:
			self.role.GetPropertyGather().ReSetRecpintFashionHoleFlag()
	
	def SetIdeByCoding(self, coding):
		#将某个时装设置为已鉴定
		fashionData = self.fashion_active_dict.get(coding)
		if not fashionData:#没激活该时装
			return
		if fashionData[0] == 1:#该时装已鉴定
			return
		#设置为激活
		fashionData[0] = 1
		#重新设定华丽度
		self.SetGorByCoding(coding)
		#重算时装鉴定属性
		self.ResetFashionIde()
		self.role.ResetGlobalFashionProperty()
		
	def GetIdxExtendPro(self, coding):
		#获取额外的幸运值
		fashionData = self.fashion_active_dict.get(coding)
		if not fashionData:#没激活该时装
			return
		return fashionData[4]
	
	def AddIdeExtendPro(self, coding, extendPro):
		#给某件时装增加额外鉴定幸运值
		fashionData = self.fashion_active_dict.get(coding)
		if not fashionData:#没激活该时装
			return
		if fashionData[0] == 1:#该时装已鉴定
			return
		Pro = fashionData[4]
		Pro += extendPro
		fashionData[4] = Pro
		SynRoleClient(self.role)
		
	def ResetFashionIde(self):
		#重置时装鉴定属性
		self.ide_pro_dict = {}
	
	def GetIdePro(self):
		#获取鉴定属性
		if self.ide_pro_dict:
			return self.suit_pro_dict
		self.ide_pro_dict = {}
		#衣柜等级
		from Game.Fashion import FashionConfig
		WardrobeLevel = self.role.GetI8(EnumInt8.FashionWardrobeLevel)
		WardrobeCfg = FashionConfig.FASHION_WARDROBE_DICT.get(WardrobeLevel)
		if not WardrobeCfg:
			print "GE_EXC,can not find WardrobeLevel(%s) in FashionBase.GetIdePro" % WardrobeLevel
			return self.ide_pro_dict
		
		for coding, data in self.fashion_active_dict.iteritems():
			#是否鉴定，阶数
			IsIde, order = data[0], data[1]
			if not IsIde:#没鉴定
				continue
			ide_pro = {}
			#获取该时装的配置
			cfg = ItemConfig.ItemCfg_Dict.get(coding)
			if not cfg:
				print "GE_EXC,can not find coding(%s) in GetIdePro" % coding
				return
			#鉴定属性1
			Jdpt1, Jdpv1 = cfg.Jdpt1, cfg.Jdpv1
			if Jdpt1 and Jdpv1:
				if len(Jdpv1) < order+1:
					print "GE_EXC, len(Jdpv1):%s < order(%s) is wrong" % (len(Jdpv1), order+1)
					return
				ide_pro[Jdpt1] = ide_pro.get(Jdpt1, 0) + Jdpv1[order]
			#鉴定属性2
			Jdpt2, Jdpv2 = cfg.Jdpt2, cfg.Jdpv2
			if Jdpt2 and Jdpv2:
				if len(Jdpv2) < order+1:
					print "GE_EXC, len(Jdpv2):%s < order(%s) is wrong" % (len(Jdpv2), order+1)
					return
				ide_pro[Jdpt2] = ide_pro.get(Jdpt2, 0) + Jdpv2[order]
			#鉴定属性3
			Jdpt3, Jdpv3 = cfg.Jdpt3, cfg.Jdpv3
			if Jdpt3 and Jdpv3:
				if len(Jdpv3) < order+1:
					print "GE_EXC, len(Jdpv1):%s < order(%s) is wrong" % (len(Jdpv3), order+1)
					return
				ide_pro[Jdpt3] = ide_pro.get(Jdpt3, 0) + Jdpv3[order]
				
				
			#根据时装的阶数获取对应的加成数值
			addpv = getattr(WardrobeCfg, "addpro%s" % (order+1))
			#根据衣柜等级获取对应的加成配置
			for pt, pv in ide_pro.iteritems():
				if addpv:
					self.ide_pro_dict[pt]= self.ide_pro_dict.get(pt, 0) + int(pv * (addpv / 10000.0) + pv)
				else:
					self.ide_pro_dict[pt]= self.ide_pro_dict.get(pt, 0) + pv
		SynRoleClient(self.role)
		return self.ide_pro_dict
			
	def ResetFashionSuit(self):
		#重置套装属性
		self.suit_pro_dict = {}
		self.active_suit_set = set()
		
	def GetSuitPro(self):
		#获取套装属性
		from Game.Fashion import FashionConfig
		
		if self.suit_pro_dict:
			return self.suit_pro_dict
		
		self.suit_pro_dict = {}
		self.active_suit_set = set()
		
		suit_dict = {}
		for coding, _ in self.fashion_active_dict.iteritems():
			cfg = ItemConfig.ItemCfg_Dict.get(coding)
			if not cfg:
				print "GE_EXC,can not find coding(%s) in GetSuitPro" % coding
				continue
			if not cfg.suitId:
				continue
			suit_dict[cfg.suitId] = suit_dict.get(cfg.suitId, 0) + 1
			
		for suitId, cnt in suit_dict.iteritems():
			cfg = FashionConfig.FASHION_SUIT_DICT.get(suitId)
			if not cfg:
				print "GE_EXC, can not find suitid(%s) in GetSuitPro" % suitId
				return
			if cnt < cfg.needCnt:#套装数不达标
				continue
			#累加激活的套装属性
			if cfg.pt1 and cfg.pv1:
				self.suit_pro_dict[cfg.pt1] = self.suit_pro_dict.get(cfg.pt1, 0) + cfg.pv1
			if cfg.pt2 and cfg.pv2:
				self.suit_pro_dict[cfg.pt2] = self.suit_pro_dict.get(cfg.pt2, 0) + cfg.pv2
			#缓存激活的套装ID
			self.active_suit_set.add(suitId)
		SynRoleClient(self.role)
		return self.suit_pro_dict
	
	def GetPosGradeStarDict(self):
		'''
		获取时装位置对应所有时装阶星数据 {pos:[grade,star]}
		'''
		posGradeStarDict = {}
		for coding, data in self.fashion_active_dict.iteritems():
			cfg = ItemConfig.ItemCfg_Dict.get(coding)
			if not cfg:
				continue
			if cfg.posType not in posGradeStarDict:
				posGradeStarDict[cfg.posType] = []
			posGradeStarDict[cfg.posType].append((data[1], data[3]))
		
		return posGradeStarDict
	
	def ReSetAllBasePro(self):
		#重置总的基础属性
		self.all_base_pro_dict = {}
		
	def GetAllBasePro(self):
		#获取总的基础属性
		if self.all_base_pro_dict:
			return self.all_base_pro_dict
		self.all_base_pro_dict = {}
		#获取所有时装的基础属性总和(基础属性，升星和升阶增加的基础属性)
		for coding, _ in self.fashion_active_dict.iteritems():
			cfg = ItemConfig.ItemCfg_Dict.get(coding)
			if not cfg: continue
			#基础属性
			for pt, pv in self.GetBasePro(coding).iteritems():
				self.all_base_pro_dict[pt] = self.all_base_pro_dict.get(pt, 0) + pv
			#获取升阶增加的属性
			for pt, pv in self.GetOrderPro(coding).iteritems():
				self.all_base_pro_dict[pt] = self.all_base_pro_dict.get(pt, 0) + pv
			#获取升星属性
			for pt, pv in self.GetStarPro(coding).iteritems():
				self.all_base_pro_dict[pt] = self.all_base_pro_dict.get(pt, 0) + pv
		SynRoleClient(self.role)
		return self.all_base_pro_dict
	
def SynRoleClient(role):
	from Game.Fashion import FashionForing
	#同步客户端时装鉴定，套装等信息
	FashionGlobalMgr = role.GetTempObj(EnumTempObj.enRoleFashionGlobalMgr)
	#激活的时装数据，套装属性，鉴定属性，光环属性，时装总基础属性,每个时装的华丽值，总的华丽值
	role.SendObj(FashionForing.Fashion_BackInfo, [FashionGlobalMgr.fashion_active_dict, FashionGlobalMgr.suit_pro_dict, FashionGlobalMgr.ide_pro_dict,\
												FashionGlobalMgr.hole_pro_dict, FashionGlobalMgr.all_base_pro_dict, FashionGlobalMgr.Gorgeous_dict, \
												FashionGlobalMgr.total_gorgeous])
	