#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.WarStation.WarStationBase")
#===============================================================================
# 战阵数据
#===============================================================================
from Game.Role.Data import EnumInt16
from Game.WarStation import WarStationConfig

WS_ITEM_CODING = 28588	#战魂石Coding


class WarStationData(object):
	def __init__(self, role):
		self.role = role
		self.break_tick_id = 0		#tick_id
		self.star_pro_dict = {}		#基础属性
		self.grade_pro_dict = {}	#万分比属性
		self.item_pro_dict = {}		#道具增加的属性
		self.InitData()
		
	def InitData(self):
		#战阵属性
		starNum = self.role.GetI16(EnumInt16.WarStationStarNum)
		station_cfg = WarStationConfig.WAR_STATION_BASE.get(starNum)
		if not station_cfg:
			print "GE_EXC,can not find starNum(%s) in WarStationBase" % starNum
			return
		
		#基础属性
		self.star_pro_dict = station_cfg.property_dict
		#万分比属性
		self.grade_pro_dict = station_cfg.thousand_pro_dict
		
		#战魂石属性
		item_use_cnt = self.role.GetI16(EnumInt16.UseStationItemCnt)
		if item_use_cnt <= 0:
			return
		item_cfg = WarStationConfig.WAR_STATION_ITEM.get(WS_ITEM_CODING)
		if not item_cfg:
			print "GE_EXC,can not find ws_coding(%s) in WarStationBase" % WS_ITEM_CODING
			return
		for pt, pv in item_cfg.property_dict.iteritems():
			self.item_pro_dict[pt] = pv * item_use_cnt
		
		
	def ReSetBaseStationPro(self):
		#重置基础属性
		self.star_pro_dict = {}
	
	def GetStationBasePro(self):
		#获取基础属性
		if self.star_pro_dict:
			return self.star_pro_dict
		
		starNum = self.role.GetI16(EnumInt16.WarStationStarNum)
		station_cfg = WarStationConfig.WAR_STATION_BASE.get(starNum)
		if not station_cfg:
			print "GE_EXC,can not find starNum(%s) in WarStationBase.GetStarPro" % starNum
			return
		self.star_pro_dict = station_cfg.property_dict
		return self.star_pro_dict
	
	def ReSetThousandPro(self):
		#重置万分比属性
		self.grade_pro_dict = {}
		
	def GetStationThousandPro(self):
		#获取万分比属性
		if self.grade_pro_dict:
			return self.grade_pro_dict
		starNum = self.role.GetI16(EnumInt16.WarStationStarNum)
		station_cfg = WarStationConfig.WAR_STATION_BASE.get(starNum)
		if not station_cfg:
			print "GE_EXC,can not find starNum(%s) in WarStationBase.GetStarPro" % starNum
			return
		self.grade_pro_dict = station_cfg.thousand_pro_dict
		return self.grade_pro_dict
		
	def ReSetWSItemPro(self):
		#重算战魂石属性
		self.item_pro_dict = {}
		
	def GetWSItemPro(self):
		#获取战魂石属性
		if self.item_pro_dict:
			return self.item_pro_dict
		self.item_pro_dict = {}
		#战魂石属性
		item_use_cnt = self.role.GetI16(EnumInt16.UseStationItemCnt)
		if item_use_cnt <= 0:
			return self.item_pro_dict
		item_cfg = WarStationConfig.WAR_STATION_ITEM.get(WS_ITEM_CODING)
		if not item_cfg:
			print "GE_EXC,can not find ws_coding(%s) in WarStationBase" % WS_ITEM_CODING
			return self.item_pro_dict
		for pt, pv in item_cfg.property_dict.iteritems():
			self.item_pro_dict[pt] = pv * item_use_cnt
		return self.item_pro_dict
	