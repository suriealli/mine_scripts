#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Mount.MountBase")
#===============================================================================
# 坐骑管理
#===============================================================================
from Game.Role.Data import EnumObj, EnumInt16
from Game.Mount import MountConfig

if "_HasLoad" not in dir():
	pass
	
class MountMgr(object):
	def __init__(self, role):
		self.role = role
		self.MountId_list = [] #进化解锁的坐骑ID
		self.eated_food = [] #食用过的食物ID
		self.Attribute_dict = {} #记录玩家坐骑总属性
		self.Mount_outData_dict = {}
		self.history_outData_mountId = set() #记录历史使用过的有时限坐骑
		self.MountAGDict = {} #坐骑外形品质进阶字典
		#初始化数据
		self.init_data()
	
	def init_data(self):
		#初始化
		mount_data_dict = self.role.GetObj(EnumObj.Mount)
		self.MountId_list = mount_data_dict.get(1)
		self.eated_food = mount_data_dict.get(2)
		self.Mount_outData_dict = mount_data_dict.get(3, {})
		self.history_outData_mountId = mount_data_dict.get(4, set())
		self.MountAGDict = mount_data_dict.get(5, {})
		self.history_outData_mountId = mount_data_dict.get(4, set())
		
		self.init_attribute()
		
	def init_attribute(self):
		#初始化坐骑属性
		self.Attribute_dict = {}
		#坐骑外观品质属性
		self.App_attribute_dict = {}
		#总的坐骑属性
		self.total_attribute_dict = {}
		
		#坐骑进化ID
		evolveId = self.role.GetI16(EnumInt16.MountEvolveID)
		if not evolveId:
			return
		#坐骑初始配置属性
		config = MountConfig._MOUNT_EVOLVE.get(evolveId)
		if not config:
			print "GE_EXC, can not find evolveId:(%s) Config in _MOUNT_EVOLVE in MountEvolve " % evolveId
			return
		#坐骑培养属性
		SA = self.Attribute_dict
		SAG = self.Attribute_dict.get
		for pk, pv in config.property_dict.iteritems():
			SA[pk] = SAG(pk, 0) + pv
		
		#解锁坐骑外形的属性
		if self.MountId_list:
			MMG = MountConfig._MOUNT_BASE.get
			for mountId in self.MountId_list:
				#每个坐骑的光环配置属性
				baseConfig = MMG(mountId)
				if not baseConfig:
					print "GE_EXC, can not find mountId:(%s) Config in MountBase, " % mountId
					continue
				for pk, pv in baseConfig.property_dict.iteritems():
					SA[pk] = SAG(pk, 0) + pv
		#食物所加的属性
		if self.eated_food:
			MFG = MountConfig._MOUNT_FOOD.get
			for foodId in self.eated_food:
				#每个食物的配置属性
				foodconfig = MFG(foodId)
				if not foodconfig:
					print "GE_EXC, can not find foodid=(%s) config in MountFood" % foodId
					continue
				for pk, pv in foodconfig.property_dict.iteritems():
					SA[pk] = SAG(pk, 0) + pv
		
		#重算一下坐骑外形品质属性
		if not self.App_attribute_dict:
			self.init_app_attribute()
		
		#计算坐骑总的属性
		if not self.total_attribute_dict:
			self.init_total_attribute()
		
	def init_app_attribute(self):
		#初始化坐骑外形品质属性
		MAG = MountConfig.MountApperanceGrade_Dict.get
		SA = self.App_attribute_dict
		SAG = self.App_attribute_dict.get
		for mountId, mountGrade in self.MountAGDict.iteritems():
			AGConfig = MAG((mountId, mountGrade))
			if not AGConfig:
				print "GE_EXC, can not find mountId:(%s), mountGrade:(%s) Config in MountApperanceGrade_Dict, " % (mountId, mountGrade)
				continue
			for pk, pv in AGConfig.property_dict.iteritems():
				SA[pk] = SAG(pk, 0) + pv
		
		#计算坐骑总的属性
		if not self.App_attribute_dict:
			self.init_total_attribute()
		
	def init_total_attribute(self):
		#初始化总的坐骑属性
		STD = self.total_attribute_dict
		STDG = self.total_attribute_dict.get
		for pt, pv in self.Attribute_dict.iteritems():
			STD[pt] = pv
		for pt, pv in self.App_attribute_dict.iteritems():
			STD[pt] = STDG(pt, 0) + pv
		
	def GetAttributeFood(self):
		#获取食物所加的属性
		Attribute_dict = {}
		AG = Attribute_dict.get
		if self.eated_food:
			MFG = MountConfig._MOUNT_FOOD.get
			for foodId in self.eated_food:
				#每个食物的配置属性
				foodconfig = MFG(foodId)
				if not foodconfig:
					print "GE_EXC, can not find foodid=(%s) config in MountFood" % foodId
					continue
				for pk, pv in foodconfig.property_dict.iteritems():
					Attribute_dict[pk] = AG(pk, 0) + pv
		return Attribute_dict
		
	def GetAttribute(self):
		#获取总属性
		if not self.Attribute_dict:
			self.init_attribute()
		return self.Attribute_dict
	
	def GetAppAttribute(self):
		#获取坐骑外形品质属性
		if not self.App_attribute_dict:
			self.init_app_attribute()
		return self.App_attribute_dict
	
	def GetTotalAttribute(self):
		if not self.total_attribute_dict:
			self.init_total_attribute()
		return self.total_attribute_dict
	
	def ResetAttribute(self):
		#重置坐骑属性
		self.total_attribute_dict = {}
		self.Attribute_dict = {}
		
	def ResetAppAttribute(self):
		#重置坐骑外形品质属性
		self.total_attribute_dict = {}
		self.App_attribute_dict = {}
		
	def save(self):
		mount_data_dict = self.role.GetObj(EnumObj.Mount)
		mount_data_dict[1] = self.MountId_list
		mount_data_dict[2] = self.eated_food
		mount_data_dict[3] = self.Mount_outData_dict
		mount_data_dict[4] = self.history_outData_mountId
		mount_data_dict[5] = self.MountAGDict
		
		