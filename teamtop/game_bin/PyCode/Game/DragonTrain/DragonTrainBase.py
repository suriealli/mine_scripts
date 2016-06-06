#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.DragonTrain.DragonTrainBase")
#===============================================================================
# 驯龙系统基础模块
#===============================================================================
from Game.Role.Data import EnumObj, EnumTempObj
from Game.DragonTrain import DragonTrainConfig

if "_HasLoad" not in dir():
	#驯龙管理器枚举
	DRAGON_TRAIN_MGR_DRAGON_DICT_IDX = 1		#神龙
	DRAGON_TRAIN_MGR_EQUIPMENT_DICT_IDX = 2		#装备
	DRAGON_TRAIN_Vein_DICT_IDX = 3				#龙脉
	#龙枚举
	DRAGON_GRADE_IDX = 1		#阶级
	DRAGON_BALL_DICT_IDX = 2	#龙珠
	DRAGON_EVOLVE_LUCKY_IDX = 3	#进化祝福
	
class Dragon(object):
	def __init__(self, dragonId, dragonDataDict):
		self.dragon_id = dragonId
		self.grade = dragonDataDict.get(DRAGON_GRADE_IDX, 1)
		self.ball_dict = dragonDataDict.get(DRAGON_BALL_DICT_IDX,{})
		self.evolve_lucky = dragonDataDict.get(DRAGON_EVOLVE_LUCKY_IDX, 0)
	
class DragonTrainMgr(object):
	def __init__(self, role):
		dragonTrainDict = role.GetObj(EnumObj.DragonTrain)
		
		self.role = role
		self.dragon_dict = {}
		self.equipment_dict = {}
		self.dragon_property_dict = {}
		
		if DRAGON_TRAIN_MGR_DRAGON_DICT_IDX in dragonTrainDict:
			dragonDict = dragonTrainDict[DRAGON_TRAIN_MGR_DRAGON_DICT_IDX]
			for dragonId, dragonDataDict in dragonDict.iteritems():
				self.dragon_dict[dragonId] = Dragon(dragonId, dragonDataDict)
		
		if DRAGON_TRAIN_MGR_EQUIPMENT_DICT_IDX in dragonTrainDict:
			equipmentDict = dragonTrainDict[DRAGON_TRAIN_MGR_EQUIPMENT_DICT_IDX]
			for dragonId, eDict in equipmentDict.iteritems():
				self.equipment_dict[dragonId] = eDict
				#重算驯龙的属性
				self.recount_dragon_property(dragonId)
			
	def create_dragon(self, dragonId):
		d = {DRAGON_GRADE_IDX: 1, 
			DRAGON_BALL_DICT_IDX: {}, 
			DRAGON_EVOLVE_LUCKY_IDX: 0}
		self.dragon_dict[dragonId] = Dragon(dragonId, d)
		
	def get_total_property_dict(self):
		totalPropertyDict = {}
		TPG = totalPropertyDict.get
		
		for pDict in self.dragon_property_dict.itervalues():
			for pt, pv in pDict.iteritems():
				totalPropertyDict[pt] = TPG(pt, 0) + pv
		
		return totalPropertyDict
	
	def recount_dragon_property(self, dragonId):
		self.dragon_property_dict[dragonId] = propertyDict = {}
		PG = propertyDict.get
		#先计算驯龙装备属性(无装备不可能激活神龙)
		if dragonId not in self.equipment_dict:
			return
		equipmentDict = self.equipment_dict[dragonId]
		for equipmentCoding in equipmentDict.itervalues():
			equipmentConfig = DragonTrainConfig.DRAGON_EQUIPMENT.get(equipmentCoding)
			if not equipmentConfig:
				continue
			#驯龙装备属性
			for pt, pv in equipmentConfig.property_dict.iteritems():
				propertyDict[pt] = PG(pt, 0) + pv
		
		#激活后属性
		if dragonId not in self.dragon_dict:
			return
		dragonObj = self.dragon_dict[dragonId]
		dragonConfig = DragonTrainConfig.DRAGON_TRAIN_BASE.get((dragonId, dragonObj.grade))
		if not dragonConfig:
			return
		#唤醒神龙属性
		for pt, pv in dragonConfig.property_dict.iteritems():
			propertyDict[pt] = PG(pt, 0) + pv
			
		for position, grade in dragonObj.ball_dict.iteritems():
			ballConfig = DragonTrainConfig.DRAGON_BALL_BASE.get((dragonId, position, grade))
			if not ballConfig:
				continue
			#龙珠属性
			for pt, pv in ballConfig.property_dict.iteritems():
				propertyDict[pt] = PG(pt, 0) + pv
				
	def get_role_view_data(self):
		dragonDataList = [(dragonId, dragonObj.grade) for dragonId, dragonObj in self.dragon_dict.iteritems()]
		
		#这里要加上龙脉的属性字典
		role = self.role
		dragonvein_propertydict = role.GetTempObj(EnumTempObj.DragonVein).GetTotalProperty()
		
		return self.equipment_dict, self.dragon_property_dict, dragonDataList, dragonvein_propertydict
		
	def save(self):
		dragonTrainDict = self.role.GetObj(EnumObj.DragonTrain)
		
		dragonDict = dragonTrainDict.setdefault(DRAGON_TRAIN_MGR_DRAGON_DICT_IDX, {})
		dragonEquipmentDict = dragonTrainDict.setdefault(DRAGON_TRAIN_MGR_EQUIPMENT_DICT_IDX, {})
		
		for dragonId, dragonObj in self.dragon_dict.iteritems():
			dragonDict[dragonId] = {DRAGON_GRADE_IDX: dragonObj.grade, 
									DRAGON_BALL_DICT_IDX: dragonObj.ball_dict, 
									DRAGON_EVOLVE_LUCKY_IDX: dragonObj.evolve_lucky}
		
		for dragonId, equipmentDict in self.equipment_dict.iteritems():
			dragonEquipmentDict[dragonId] = equipmentDict
		
		
		
		
