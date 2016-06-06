#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Property.PropertyEnum")
#===============================================================================
# 角色属性枚举(请不要随便修改枚举顺序，枚举存在，删除，插入，都是不允许的，只能往后面加)
#===============================================================================
#PropertyEnum_Begin
# 属性枚举定义
enNone = 0			#占位
maxhp = 1			#生命
attackspeed = 2		#攻击速度
anger = 3			#怒气
attack_p = 4		#物攻
defense_p = 5		#物防
attack_m = 6		#法攻
defense_m = 7		#法防
crit = 8			#暴击
critpress = 9		#免暴
antibroken = 10		#破防
notbroken = 11		#免破
parry = 12			#格挡
puncture = 13		#破挡
damageupgrade = 14	#增伤
damagereduce = 15	#免伤
zdl = 16			#战斗力(程序用)
enTotal = 17		#总共个数
attackPercent = -16	#攻击加成万分比
#PropertyEnum_End



#########################################################################
#属性读表类，读表的时候可以继承这个类，达到读取属性的目的
#########################################################################
class PropertyRead(object):
	NeedCountPropertyZDl = True#是否需要计算这个属性的战斗
	def __init__(self):
		self.maxhp = int
		self.attackspeed = int
		self.anger = int
		
		self.attack_p = int
		self.defense_p = int
		
		self.attack_m = int
		self.defense_m = int
		
		self.crit = int
		self.critpress = int
		
		self.antibroken = int
		self.notbroken = int
		
		self.parry = int
		self.puncture = int
		
		self.damageupgrade = int
		self.damagereduce = int


	def InitProperty(self):
		self.property_dict = {}
		from Game.Property import PropertyEnum
		for name in ["maxhp", "attackspeed", "anger", "attack_p", "defense_p",
					"attack_m", "defense_m", "crit", "critpress", "antibroken", "notbroken",
					"parry", "puncture", "damageupgrade", "damagereduce"]:
			property_value = getattr(self, name)
			if property_value:
				self.property_dict[getattr(PropertyEnum, name)] = property_value
		
class PropertyRead_2(object):
	NeedCountPropertyZDl = True#是否需要计算这个属性的战斗
	def __init__(self):
		self.maxhp_2 = int
		self.attackspeed_2 = int
		self.anger_2 = int
		
		self.attack_p_2 = int
		self.defense_p_2 = int
		
		self.attack_m_2 = int
		self.defense_m_2 = int
		
		self.crit_2 = int
		self.critpress_2 = int
		
		self.antibroken_2 = int
		self.notbroken_2 = int
		
		self.parry_2 = int
		self.puncture_2 = int
		
		self.damageupgrade_2 = int
		self.damagereduce_2 = int

	def InitProperty_2(self):
		self.property_dict_2 = {}
		proEnumDict = {"maxhp_2":1, "attackspeed_2":2, "anger_2":3, "attack_p_2":4, "defense_p_2":5,
					"attack_m_2":6, "defense_m_2":7, "crit_2":8, "critpress_2":9, "antibroken_2":10, "notbroken_2":11,
					"parry_2":12, "puncture_2":13, "damageupgrade_2":14, "damagereduce_2":15}
		
		for name in ["maxhp_2", "attackspeed_2", "anger_2", "attack_p_2", "defense_p_2",
					"attack_m_2", "defense_m_2", "crit_2", "critpress_2", "antibroken_2", "notbroken_2",
					"parry_2", "puncture_2", "damageupgrade_2", "damagereduce_2"]:
			property_value = getattr(self, name)
			if property_value:
				self.property_dict_2[proEnumDict.get(name)] = property_value





