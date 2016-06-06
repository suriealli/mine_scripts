#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.DragonTrain.DragonVeinBase")
#===============================================================================
# 龙脉基础模块
#===============================================================================
from Game.Role.Data import EnumObj
from Game.DragonTrain import DragonTrainConfig
from Game.DragonTrain import DragonTrainBase

class DragonVein(object):
	#龙脉
	def __init__(self, role, index):
		#龙脉的数据绑定在role_obj中
		DragonTrainDict = role.GetObj(EnumObj.DragonTrain)
		vein_data_dict = DragonTrainDict.setdefault(DragonTrainBase.DRAGON_TRAIN_Vein_DICT_IDX, {})
		vein_data = vein_data_dict.setdefault(index, {"grade":1, "level":0, "level_luck": 0, "grade_luck":0})
		
		self.index = index	#龙脉的索引，1：金脉 2：木脉
		self.grade = vein_data.setdefault("grade", 1)			#品阶
		self.level = vein_data.setdefault("level", 0)			#等级
		self.grade_luck = vein_data.setdefault("grade_luck", 0)	#品阶祝福值
		self.level_luck = vein_data.setdefault("level_luck", 0)	#等级祝福值
		self.property_dict = {}									#属性字典

		self.vein_data = vein_data								#龙脉的数据
		self.recountProperty()									#在初始化完成后要计算一次属性
		
		self.maxlevel = 0										#龙脉的最大等级
		self.maxgrade = 0										#龙脉的最大品阶
		self.name = ""											#龙脉的名字

		basecfg = DragonTrainConfig.DRAGON_VEIN_BASE.get(index, None)
		if not basecfg:
			print "GE_EXC, error while basecfg = DragonTrainConfig.DRAGON_VEIN_BASE.get(index, None), no such index(%s)" % index
			return
		self.maxgrade = basecfg.maxGrade
		self.maxlevel = basecfg.maxLevel
		self.name = basecfg.veinName
		
	def recountProperty(self):
		#获取龙脉的属性加成
		self.property_dict = propertyDict = {}
		level_cfg = DragonTrainConfig.DRAGON_VEIN_LEVEL.get((self.index, self.level), None)

		if not level_cfg:
			print "GE_EXC, error while level_cfg = DragonTrainConfig.DRAGON_VEIN_LEVEL.get((self.index, self.level), None),no such (self.index, self.level)(%s,%s)" % (self.index, self.level)
			return None
		
		grade_cfg = DragonTrainConfig.DRAGON_VEIN_GRADE.get((self.index, self.grade), None)
		if not grade_cfg:
			print "GE_EXC, error while grade_cfg = DragonTrainConfig.DRAGON_VEIN_GRADE.get((self.index, self.grade), None), no such (self.index, self.grade)(%s,%s)" % (self.index, self.grade)
			return None
		
		PG = propertyDict.get
		for pt, pv in level_cfg.property_dict.iteritems():
				propertyDict[pt] = PG(pt, 0) + pv

		for pt, pv in grade_cfg.property_dict.iteritems():
				propertyDict[pt] = PG(pt, 0) + pv
		
	def level_up(self, level):
		#升级，不能大于最大等级
		newlevel = self.level + level
		if newlevel > self.maxlevel:
			print "GE_EXC, error while up_level DragonVein, new level can not > max level(%s)" % self.maxlevel
			return
		self.level = newlevel
		self.vein_data["level"] = self.level
		self.recountProperty()
		
	def grade_up(self, grade):
		#升阶，也就是进化
		newgrade = self.grade + grade
		if newgrade > self.maxgrade:
			print "GE_EXC, error while upgrade DragonVein, new grade can not > max grade(%s)" % self.maxgrade
			return
		self.grade = newgrade
		self.vein_data["grade"] = self.grade
		self.recountProperty()
	
	def levelluck_set(self, luck):
		#设置等级祝福值
		if self.level_luck != luck:
			self.vein_data["level_luck"] = self.level_luck = luck
	
	def gradeluck_set(self, luck):
		#设置品阶祝福值
		if self.grade_luck != luck:
			self.vein_data["grade_luck"] = self.grade_luck = luck
		

class DragonVeinManager(object):
	#龙脉管理器 
	def __init__(self, role):
		self.role = role	#管理器首要，确定谁是管理器的拥有者
		self.vein_dict = {}	#在这个字典里面保存龙脉的情况{龙脉id:龙脉对象}
		self.total_level = 0
		self.grade_dict = {}
		self.totalPropertyDict = {}
		self.buf_set = set()
		self.buf_propertyDict = {}
		
		#在初始化的时候生成龙脉队形保存在上面的self.vein_dict中
		DragonTrainDict = role.GetObj(EnumObj.DragonTrain)
		vein_data_dict = DragonTrainDict.setdefault(DragonTrainBase.DRAGON_TRAIN_Vein_DICT_IDX, {})
		if vein_data_dict:
			vein_dict = self.vein_dict
			for vein_idx in vein_data_dict.iterkeys():
				vein_dict[vein_idx] = DragonVein(role, vein_idx)
		self.__RecountProperty()
		self.__RecountStatu()
	
	def VeinActivate(self, vein_idx):
		'''
		龙脉激活
		@param vein_idx:要升级的龙脉索引
		'''
		if vein_idx in self.vein_dict:
			return
		#默认初始化一个龙脉
		self.vein_dict[vein_idx] = DragonVein(self.role, vein_idx)
		self.__RecountProperty()
		self.__RecountStatu()

	def VeinLevelup(self, vein_idx, level):
		'''
		龙脉升级
		@param vein_idx:要升级的龙脉索引
		@param level:要升多少级
		'''
		#如果管理器中甚至还没有这个龙脉的话，也就是龙脉还没有激活
		vein_obj = self.vein_dict.get(vein_idx, None)
		if not vein_obj:
			return
		vein_obj.level_up(level)
		self.__RecountProperty()
		self.__RecountStatu()

	def VeinGradeup(self, vein_idx, grade):
		'''
		龙脉升级
		@param vein_idx:要升级的龙脉索引
		@param grade:要升多少阶级
		'''
		vein_obj = self.vein_dict.get(vein_idx, None)
		if not vein_obj:
			return
		vein_obj.grade_up(grade)
		self.__RecountProperty()
		self.__RecountStatu()

	def __RecountStatu(self):
		#重算总等级和每个品阶的龙脉的个数，重算激活的buf
		self.total_level = 0
		self.grade_dict = grade_dict = {}
		self.buf_propertyDict = buf_propertyDict = {}
		
		SGG = self.grade_dict.get
		for vein_obj in self.vein_dict.itervalues():
			self.total_level += vein_obj.level
			grade_dict[vein_obj.grade] = SGG(vein_obj.grade, 0) + 1
		
		#重算所有激活的buf的属性字典
		BPDG = buf_propertyDict.get
		SBA = self.buf_set.add
		total_level = self.total_level
		
		for buf_idx, buf_cfg in DragonTrainConfig.DRAGON_VEIN_BUF.iteritems():
			#否则计算大于buf要求品阶的龙脉的个数
			total_cnt = 0
			for grade, cnt in self.grade_dict.iteritems():
				if grade >= buf_cfg.activateNeedVeinGrade:
					total_cnt += cnt
			
			#如果总等级和符合要求的品阶的个数大于需求值，则激活某个buf
			if total_level >= buf_cfg.activateNeedVeinLevelSum and total_cnt >= buf_cfg.activateNeedVeinCount:
				SBA(buf_idx)
				for pt, pv in buf_cfg.property_dict.iteritems():
					buf_propertyDict[pt] = BPDG(pt, 0) + pv

	def __RecountProperty(self):
		#不需要每次都重算，仅在等级和品阶发生变化的时候才重算
		self.totalPropertyDict = totalPropertyDict = {}
		TPG = totalPropertyDict.get
		for vein_obj in self.vein_dict.itervalues():
			for pt, pv in vein_obj.property_dict.iteritems():
				totalPropertyDict[pt] = TPG(pt, 0) + pv

	def GetTotalProperty(self):
		#通过这里获取所有龙脉加起来的属性，之后要进行属性重算的
		return self.totalPropertyDict
	
	def GetTotalBufProperty(self):
		return self.buf_propertyDict
	
	def GetCurrentBufSet(self):
		return self.buf_set

