#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Item.ItemBase")
#===============================================================================
# 物品基类
#===============================================================================
from Game.Role.Obj import Base




class ItemBase(Base.ObjBase):
	Obj_Type = Base.Obj_Type_Base
	def __init__(self, role, obj):
		Base.ObjBase.__init__(self, role, obj)
		self.package = None
	
	def GetSyncData(self):
		#获取同步客户端的数据
		return (self.oid, self.otype, self.oint, self.odata)
	
	def GetItemCoding(self):
		return self.otype
	
	def CanSell(self):
		return self.cfg.canSell
	
	def IsJiami(self):
		return self.cfg.jiaMi
	
	def SellPrice(self):
		return self.cfg.salePrice
	
	def IsNeedLog(self):
		#是否需要记录日志
		return self.cfg.needLog

	def IsDeadTime(self):
		#默认不过期
		return False
