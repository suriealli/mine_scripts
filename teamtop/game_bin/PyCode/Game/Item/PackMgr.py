#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Item.PackMgr")
#===============================================================================
# 物品包裹
#===============================================================================
import cProcess
from Util import Trace
from ComplexServer.Log import AutoLog
from Game.Item import ItemConfig, ItemMsg
from Game.Role.Data import EnumTempObj, EnumObj, EnumInt8
from Game.Role.Obj import Base
from Game.Role.Mail import Mail
from Common.Other import GlobalPrompt
from Game.Item.ItemConfig import ArtifactCuiLian_Dict, ArtifactCuiLianHalo_Dict




class PackMgr(Base.PackageBase):
	#人物背包
	ObjEnumIndex = EnumObj.En_PackageItems
	TypeObjFun = Base.Obj_Type_Fun
	
	def __init__(self, role, objDict, heroId = 0):
		Base.PackageBase.__init__(self, role, objDict, heroId)
		
		self.packageMaxSize = 0
		self.CountPackageMaxSize()
	
	def CountPackageMaxSize(self):
		#计算背包空间
		self.packageMaxSize = 0
		cfg = ItemConfig.PackageSize_Dict.get(self.role.GetVIP())
		if not cfg:
			print "GE_EXC CountPackageMaxSize error not this cfg (%s)" % self.role.GetVIP()
			return 0
		self.packageMaxSize = cfg.baseSize + self.role.GetI8(EnumInt8.PackageOpenTimes) * 5

	def GetMaxSize(self):
		return self.packageMaxSize
	
	def AddItem(self, coding, cnt):
		if cnt < 1:
			print "GE_EXC, AddItem error cnt < 1 roleId(%s), (%s, %s)" % (self.role.GetRoleID(),coding, cnt)
			Trace.StackWarn("AddItem error")
			return None
		if coding in ItemConfig.ValueItems:
			print "GE_EXC, AddItem error is  Value item roleId(%s)(%s, %s)" % (self.role.GetRoleID(), coding, cnt)
			Trace.StackWarn("AddItem error")
			return None
		if not ItemConfig.ItemCanOverlap(coding):
			return self.AddCanNotOverlaoItem(coding, cnt)
		else:
			return self.AddCanOverlapItem(coding, cnt)
	
	def AddCanNotOverlaoItem(self, coding, cnt):
		#不可叠加
		if self.EmptySize() < cnt:
			AutoLog.LogObj(self.role.GetRoleID(), AutoLog.eveAddItemPackageFull, 0, coding, cnt, {}, None)
			Mail.SendMail(self.role.GetRoleID(), GlobalPrompt.PackageFullTitle, GlobalPrompt.Sender, GlobalPrompt.Content, [(coding, cnt)])
			return None
		fun = Base.Obj_Type_Fun.get(coding)
		if not fun:
			print "GE_EXC, AddItem can not find fun , coding = (%s)" % coding
			Trace.StackWarn("AddItem error")
			return None
		for _ in xrange(cnt):
			if self.EmptySize() <= 0:
				break
			#构建数据对象(id, coding, cnt, odata)
			obj = cProcess.AllotGUID64(), coding, 1, {}
			#根据注册函数，数据对象，生成物品对象
			newItem = fun(self.role, obj)
			newItem.package = self
			newItem.AfterCreate()
			
			#角色
			self.role.GetObj(self.ObjEnumIndex).add(newItem.oid)
			#加入内部管理器
			itemDict = self.codingGather.get(coding)
			if not itemDict:
				self.codingGather[coding] = itemDict = {}
			#coding管理
			itemDict[newItem.oid] = newItem
			#ID管理
			self.objIdDict[newItem.oid] = newItem
			#加入全局管理器
			g_dict = self.role.GetTempObj(EnumTempObj.enGlobalItemMgr)
			g_dict[newItem.oid] = newItem
			#同步客户端
			self.role.SendObj(ItemMsg.Item_SyncItemData, newItem.GetSyncData())
			if newItem.IsNeedLog():
				#记录日志
				AutoLog.LogObj(self.role.GetRoleID(), AutoLog.eveAddItem, newItem.oid, coding, 1, newItem.odata)
		return True
	
	def AddCanOverlapItem(self, coding, cnt):
		#增加可叠加物品
		if self.IsFull():
			AutoLog.LogObj(self.role.GetRoleID(), AutoLog.eveAddItemPackageFull, 0, coding, cnt, {}, None)
			Mail.SendMail(self.role.GetRoleID(), GlobalPrompt.PackageFullTitle, GlobalPrompt.Sender, GlobalPrompt.Content, [(coding, cnt)])
			return None
		
		#特殊，可以叠加的时效性物品，先看看背包有没有这类物品
		if coding in Base.Obj_Time_Overlap:
			self._CheckAndChangeTimeOutItem(coding)
		
		if coding in self.codingGather:
			#背包已经有这类物品，直接增加叠加数量
			return self._AddCodingCnt(coding, cnt)
		
		if self.EmptySize() <= 0:
			print "GE_EXC, packageis full in additem"
			return None
		
		fun = Base.Obj_Type_Fun.get(coding)
		if not fun:
			print "GE_EXC, AddItem can not find fun , coding = (%s)" % coding
			return None
		
		#构建数据对象
		obj = cProcess.AllotGUID64(), coding, cnt, {}
		
		#根据注册函数，数据对象，生成物品对象
		newItem = fun(self.role, obj)
		newItem.package = self
		newItem.AfterCreate()
		
		#角色
		self.role.GetObj(self.ObjEnumIndex).add(newItem.oid)
		#加入内部管理器
		itemDict = self.codingGather.get(coding)
		if not itemDict:
			self.codingGather[coding] = itemDict = {}
		itemDict[newItem.oid] = newItem
		self.objIdDict[newItem.oid] = newItem
		#加入全局管理器
		g_dict = self.role.GetTempObj(EnumTempObj.enGlobalItemMgr)
		g_dict[newItem.oid] = newItem
		
		self.role.SendObj(ItemMsg.Item_SyncItemData, newItem.GetSyncData())
		if newItem.IsNeedLog():
			#记录日志
			AutoLog.LogObj(self.role.GetRoleID(), AutoLog.eveAddItem, newItem.oid, coding, cnt, newItem.odata)
		return newItem
	
	def _CheckAndChangeTimeOutItem(self, coding):
		item = self.FindItem(coding)
		if not item:
			return
		if not item.IsDeadTime():
			return
		self.ChangeTimeOutItem(item)
		
	def ChangeTimeOutItem(self, item):
		#已经过期，删除这个物品，转换成过期类物品
		timeoutCoding = item.cfg.timeoutCoding
		cnt = item.oint
		self.DelProp(item.oid)
		if timeoutCoding:
			self.AddItem(timeoutCoding, cnt)
		else:
			print "GE_EXC, ChangeTimeOutItem error (%s)" % item.otype
		
	def _AddCodingCnt(self, coding, cnt):
		#背包已经有这类物品，直接增加叠加数量
		obj = self.codingGather.get(coding).values()[0]
		obj.oint += cnt
		self.role.SendObj(ItemMsg.Item_SyncItemCnt, (obj.oid, obj.oint))
		if obj.IsNeedLog():
			#记录日志
			AutoLog.LogObj(self.role.GetRoleID(), AutoLog.eveAddItem, obj.oid, coding, cnt, obj.odata)
		return obj
	
	
	def DelItem(self, coding, cnt):
		#删除指定coding数量的物品,注意处理返回值
		if cnt > self.ItemCnt(coding) or cnt <= 0:
			print "GE_EXC, DelItem error cnt  roleId (%s), (%s, %s)" % (self.role.GetRoleID(), coding, cnt)
			Trace.StackWarn("DelItem error")
			return 0
		if coding not in self.codingGather:
			print "GE_EXC, DelItem error coding(%s)  cnt (%s)not in self.codingGather" % (coding, cnt)
			Trace.StackWarn("DelItem")
			return 0
		if not ItemConfig.ItemCanOverlap(coding):
			#不可叠加
			idlist = self.codingGather[coding].keys()
			if len(idlist) < cnt:
				print "GE_EXC, DelItem error len(idlist) < cnt" % (coding, cnt)
				return 0
			#循环删除这类物品
			for i in xrange(cnt):
				propid = idlist[i]
				self.DelProp(propid)
				self.role.SendObj(ItemMsg.Item_SyncDel, propid)
			return cnt
		else:
			obj = self.codingGather.get(coding).values()[0]
			if obj.oint < cnt:
				print "GE_EXC, DelItem error obj.oint < cnt" % (coding, cnt)
				return 0
			if obj.oint <= cnt:
				#数量为0，直接删除物品
				self.DelProp(obj.oid)
				self.role.SendObj(ItemMsg.Item_SyncDel, obj.oid)
			else:
				obj.oint -= cnt
				if obj.IsNeedLog():
					#日志，记录扣除数量，剩余数量
					AutoLog.LogObj(self.role.GetRoleID(), AutoLog.eveDelItem, obj.oid, obj.otype, cnt, obj.odata, obj.oint)
				self.role.SendObj(ItemMsg.Item_SyncItemCnt, (obj.oid, obj.oint))
			return cnt
		
	def DelProp(self, oid):
		#删除指定ID物品，并且同步客户端
		if self._DelProp(oid) is True:
			self.role.SendObj(ItemMsg.Item_SyncDel, oid)
			return True
		else:
			print "GE_EXC, DelProp error (%s)" % oid
			Trace.StackWarn("DelProp")
			return False
	
	def _DelProp(self, oid):
		#删除物品，内部方法，判断数据正确性
		if oid not in self.objIdDict:
			return False
		obj = self.objIdDict.get(oid)
		if not obj:
			return False
		
		objIdset = self.role.GetObj(self.ObjEnumIndex)
		if oid not in objIdset:
			return False

		g_dict = self.role.GetTempObj(EnumTempObj.enGlobalItemMgr)
		if oid not in g_dict:
			return False
		
		if obj.otype not in self.codingGather:
			return False
		
		c_dict = self.codingGather.get(obj.otype, {})
		if oid not in c_dict:
			return False
		
		#内部容器
		del self.objIdDict[oid]

		objIdset.discard(oid)
		del c_dict[oid]
		if not c_dict:
			del self.codingGather[obj.otype]
		#全局
		del g_dict[oid]
		if obj.IsNeedLog():
			# 日志
			AutoLog.LogObj(self.role.GetRoleID(), AutoLog.eveDelItem, obj.oid, obj.otype, obj.oint, obj.odata, 0)
		return True
	
	def DecPropCnt(self, item, cnt):
		if cnt < 1:
			print "GE_EXC, DecPropCnt cnt < 1 (%s), (%s, %s)" % (self.role.GetRoleID(), item.otype, cnt)
			Trace.StackWarn("DecPropCnt")
			return
		#删除指定物品对象的数量
		if item.oint <= cnt:
			self.DelProp(item.oid)
		else:
			item.oint -= cnt
			if item.IsNeedLog():
				#日志，记录扣除数量，剩余数量
				AutoLog.LogObj(self.role.GetRoleID(), AutoLog.eveDelItem, item.oid, item.otype, cnt, item.odata, item.oint)
			self.role.SendObj(ItemMsg.Item_SyncItemCnt, (item.oid, item.oint))


class RoleEquipmentMgr(Base.PackageBase):
	#角色身上装备管理器
	ObjEnumIndex = EnumObj.En_RoleEquipments
	TypeObjFun = Base.Obj_Type_Fun
	def __init__(self, role, objDict, heroId = 0):
		Base.PackageBase.__init__(self, role, objDict, heroId)
		#套装属性字典
		self.StrengthenSuitDict = None
		self.StrengthenSuitLevel = []
		
	def GetMaxSize(self):
		#角色只有6个格子
		return 6
		
	def ResetStrengthenSuit(self):
		#重算套装属性
		self.StrengthenSuitDict = None
		self.StrengthenSuitLevel = []
		
	def GetStrengthenSuitDict(self):		
		#获取套装属性
		if self.StrengthenSuitDict is not None:
			return self.StrengthenSuitDict
		#重算设置套装属性
		self.StrengthenSuitDict = {}
		self.StrengthenSuitLevel = []
		suit_dict = {}
		for equipment in self.objIdDict.itervalues():
			if equipment.cfg.posType > 6:
				continue
			csuitId = equipment.cfg.suitId
			#无套装属性
			if not csuitId:
				continue		
			if type(csuitId) == int:#整形
				suit_dict[csuitId] = suit_dict.get(csuitId, 0) + 1	
			elif type(csuitId) == list:
				for value in csuitId:
					suit_dict[value] = suit_dict.get(value, 0) + 1
		ESD = ItemConfig.Equipment_Suit_Dict.get		
		for suitId, cnt in suit_dict.iteritems():
			cfg = ESD(suitId)
			if not cfg:
				return self.StrengthenSuitDict
			if cnt < cfg.cnt:
				continue
			else:
				if cfg.pt1 and cfg.pv1:
					self.StrengthenSuitDict[cfg.pt1] = self.StrengthenSuitDict.get(cfg.pt1, 0) + cfg.pv1
				if cfg.pt2 and cfg.pv2:
					self.StrengthenSuitDict[cfg.pt2] = self.StrengthenSuitDict.get(cfg.pt2, 0) + cfg.pv2
				self.StrengthenSuitLevel.append(suitId)
		
		return self.StrengthenSuitDict

class HeroEquipmentMgr(Base.PackageBase):
	#英雄身上装备管理器
	ObjEnumIndex = EnumObj.En_HeroEquipments
	TypeObjFun = Base.Obj_Type_Fun
	def __init__(self, role, objDict, heroId, hero):
		assert heroId != 0
		self.hero = hero
		assert hero is not None
		Base.PackageBase.__init__(self, role, objDict, heroId)
		self.StrengthenSuitDict = None
		self.StrengthenSuitLevel = []
		
	def GetMaxSize(self):
		#英雄只有6格子
		return 6
	
	def ResetStrengthenSuit(self):
		self.StrengthenSuitDict = None
		self.StrengthenSuitLevel = []
	
	def GetStrengthenSuitDict(self):
		if self.StrengthenSuitDict is not None:
			return self.StrengthenSuitDict
		#重算设置套装属性
		self.StrengthenSuitDict = {}
		self.StrengthenSuitLevel = []
		suit_dict = {}
		for equipment in self.objIdDict.itervalues():
			if equipment.cfg.posType > 6:
				#其他装备
				continue
			csuitId = equipment.cfg.suitId
			if not csuitId:
				continue
			if type(csuitId) == int:#整形
				suit_dict[csuitId] = suit_dict.get(csuitId, 0) + 1
			elif type(csuitId) == list:
				for value in csuitId:
					suit_dict[value] = suit_dict.get(value, 0) + 1
		ESD = ItemConfig.Equipment_Suit_Dict.get
		for suitId, cnt in suit_dict.iteritems():
			cfg = ESD(suitId)
			if not cfg:
				return self.StrengthenSuitDict
			if cnt < cfg.cnt:
				continue
			else:
				#跟新套装属性
				if cfg.pt1 and cfg.pv1:
					self.StrengthenSuitDict[cfg.pt1] = self.StrengthenSuitDict.get(cfg.pt1, 0) + cfg.pv1
				if cfg.pt2 and cfg.pv2:
					self.StrengthenSuitDict[cfg.pt2] = self.StrengthenSuitDict.get(cfg.pt2, 0) + cfg.pv2
				self.StrengthenSuitLevel.append(suitId)
		
		return self.StrengthenSuitDict

class RoleArtifactMgr(Base.PackageBase):
	#角色身上神器管理器
	ObjEnumIndex = EnumObj.En_RoleArtifact
	TypeObjFun = Base.Obj_Type_Fun
	def __init__(self, role, objDict, heroId = 0):
		Base.PackageBase.__init__(self, role, objDict, heroId)
		#套装属性字典
		self.StrengthenSuitDict = None
		self.StrengthenSuitLevel = []
		self.CuiLianSuiteDict = None
		self.CuiLianHoleDict = None
		
	def GetMaxSize(self):
		#角色只有6格子
		return 6
		
	def ResetSuit(self):
		#重算套装属性
		self.StrengthenSuitDict = None
		self.StrengthenSuitLevel = []
		
	def GetSuitDict(self):		
		#获取套装属性
		if self.StrengthenSuitDict is not None:
			return self.StrengthenSuitDict
		#重算设置套装属性
		self.StrengthenSuitDict = {}
		self.StrengthenSuitLevel = []
		suit_dict = {}
		for Artifact in self.objIdDict.itervalues():
			if Artifact.cfg.posType > 6:
				continue
			csuitId = Artifact.cfg.suitId
			#无套装属性
			if not csuitId:
				continue		
			if type(csuitId) == int:#整形
				suit_dict[csuitId] = suit_dict.get(csuitId, 0) + 1	
			elif type(csuitId) == list:
				for value in csuitId:
					suit_dict[value] = suit_dict.get(value, 0) + 1
		ESD = ItemConfig.Artifact_Suit_Dict.get
		for suitId, cnt in suit_dict.iteritems():
			cfg = ESD(suitId)
			if not cfg:
				return self.StrengthenSuitDict
			if cnt < cfg.cnt:
				continue
			else:
				if cfg.pt1 and cfg.pv1:
					self.StrengthenSuitDict[cfg.pt1] = self.StrengthenSuitDict.get(cfg.pt1, 0) + cfg.pv1
				if cfg.pt2 and cfg.pv2:
					self.StrengthenSuitDict[cfg.pt2] = self.StrengthenSuitDict.get(cfg.pt2, 0) + cfg.pv2
				self.StrengthenSuitLevel.append(suitId)
		
		return self.StrengthenSuitDict
	
	
	def ResetCuiLianSuite(self):
		#重算套装属性
		self.CuiLianSuiteDict = None
		
	def GetCuiLianSuitDict(self):
		if self.CuiLianSuiteDict is not None:
			return self.CuiLianSuiteDict
		#重算设置套装属性
		self.CuiLianSuiteDict = {}
		propertySet = set()
		
		for Artifact in self.objIdDict.itervalues():
			if Artifact.cfg.posType > 6:
				continue
			#将所有淬炼套装属性取出到一个集合
			for suiteIndex in Artifact.GetCuiLianSuite():
				propertySet.add(suiteIndex)
			
		for key in propertySet:
			cfg = ArtifactCuiLian_Dict.get(key)
			if not cfg:
				print "GE_EXC can't find key(%s) in ArtifactCuiLian_Dict." % key
				continue
			if cfg.pt1 and cfg.pv1:
				self.CuiLianSuiteDict[cfg.pt1] = self.CuiLianSuiteDict.get(cfg.pt1, 0) + cfg.pv1
			if cfg.pt2 and cfg.pv2:
				self.CuiLianSuiteDict[cfg.pt2] = self.CuiLianSuiteDict.get(cfg.pt2, 0) + cfg.pv2
			
		return self.CuiLianSuiteDict
	
	def ResetCuiLianHole(self):
		#重算套装属性
		self.CuiLianHoleDict = None
	def GetCuiLianHoleDict(self):
		if self.CuiLianHoleDict is not None:
			return self.CuiLianHoleDict
		self.CuiLianHoleDict = {}
		HoleLevel = self.role.GetArtifactCuiLianHoleLevel()
		CuiLianHalo = ArtifactCuiLianHalo_Dict.get(HoleLevel)
		if not CuiLianHalo:
			return
		suiteSet = set()
		for Artifact in self.objIdDict.itervalues():
			if Artifact.cfg.posType > 6:
				continue
			suiteList = Artifact.GetCuiLianSuite()
			for suite in suiteList:
				suiteSet.add(suite)
		for suiteIndex, level in suiteSet: 
			cfg = ArtifactCuiLian_Dict.get((suiteIndex, level))
			if not cfg:
				continue
			pv = CuiLianHalo.percent.get(level, 0)
			if cfg.pt1 and pv:
				self.CuiLianHoleDict[cfg.pt1] = self.CuiLianHoleDict.get(cfg.pt1, 0) + pv
			if cfg.pt2 and pv:
				self.CuiLianHoleDict[cfg.pt2] = self.CuiLianHoleDict.get(cfg.pt2, 0) + pv
		return self.CuiLianHoleDict
		
class HeroArtifactMgr(Base.PackageBase):
	#英雄身上神器管理器
	ObjEnumIndex = EnumObj.En_HeroArtifact
	TypeObjFun = Base.Obj_Type_Fun
	def __init__(self, role, objDict, heroId, hero):
		assert heroId != 0
		self.hero = hero
		assert hero is not None
		Base.PackageBase.__init__(self, role, objDict, heroId)
		self.StrengthenSuitDict = None
		self.StrengthenSuitLevel = []
		self.CuiLianSuiteDict = None
		self.CuiLianHoleDict = None
		
	def GetMaxSize(self):
		#英雄只有6格子
		return 6
	
	def ResetSuit(self):
		self.StrengthenSuitDict = None
		self.StrengthenSuitLevel = []
	
	def GetSuitDict(self):
		#获取套装属性
		if self.StrengthenSuitDict is not None:
			return self.StrengthenSuitDict
		#重算设置套装属性
		self.StrengthenSuitDict = {}
		self.StrengthenSuitLevel = []
		suit_dict = {}
		for Artifact in self.objIdDict.itervalues():
			if Artifact.cfg.posType > 6:
				continue
			csuitId = Artifact.cfg.suitId
			#无套装属性
			if not csuitId:
				continue		
			if type(csuitId) == int:#整形
				suit_dict[csuitId] = suit_dict.get(csuitId, 0) + 1	
			elif type(csuitId) == list:
				for value in csuitId:
					suit_dict[value] = suit_dict.get(value, 0) + 1
		ESD = ItemConfig.Artifact_Suit_Dict.get
		for suitId, cnt in suit_dict.iteritems():
			cfg = ESD(suitId)
			if not cfg:
				return self.StrengthenSuitDict
			if cnt < cfg.cnt:
				continue
			else:
				if cfg.pt1 and cfg.pv1:
					self.StrengthenSuitDict[cfg.pt1] = self.StrengthenSuitDict.get(cfg.pt1, 0) + cfg.pv1
				if cfg.pt2 and cfg.pv2:
					self.StrengthenSuitDict[cfg.pt2] = self.StrengthenSuitDict.get(cfg.pt2, 0) + cfg.pv2
				self.StrengthenSuitLevel.append(suitId)
		
		return self.StrengthenSuitDict
	
	def ResetCuiLianSuite(self):
		#重算套装属性
		self.CuiLianSuiteDict = None
		
	def GetCuiLianSuitDict(self):
		if self.CuiLianSuiteDict is not None:
			return self.CuiLianSuiteDict
		#重算设置套装属性
		self.CuiLianSuiteDict = {}
		propertySet = set()
		
		for Artifact in self.objIdDict.itervalues():
			if Artifact.cfg.posType > 6:
				continue
			#将所有淬炼套装属性取出到一个集合
			for suiteIndex in Artifact.GetCuiLianSuite():
				propertySet.add(suiteIndex)
			
		for key in propertySet:
			cfg = ArtifactCuiLian_Dict.get(key)
			if not cfg:
				print "GE_EXC can't find key(%s) in ArtifactCuiLian_Dict." % key
				continue
			if cfg.pt1 and cfg.pv1:
				self.CuiLianSuiteDict[cfg.pt1] = self.CuiLianSuiteDict.get(cfg.pt1, 0) + cfg.pv1
			if cfg.pt2 and cfg.pv2:
				self.CuiLianSuiteDict[cfg.pt2] = self.CuiLianSuiteDict.get(cfg.pt2, 0) + cfg.pv2
			
		return self.CuiLianSuiteDict
	
	def ResetCuiLianHole(self):
		#重算套装属性
		self.CuiLianHoleDict = None
	def GetCuiLianHoleDict(self):
		if self.CuiLianHoleDict is not None:
			return self.CuiLianHoleDict
		self.CuiLianHoleDict = {}
		HoleLevel = self.role.GetArtifactCuiLianHoleLevel()
		CuiLianHalo = ArtifactCuiLianHalo_Dict.get(HoleLevel)
		if not CuiLianHalo:
			return
		suiteSet = set()
		for Artifact in self.objIdDict.itervalues():
			if Artifact.cfg.posType > 6:
				continue
			Suite = Artifact.GetCuiLianSuite()
			for suite, level in Suite: 
				suiteList = Artifact.GetCuiLianSuite()
				for suite in suiteList:
					suiteSet.add(suite)
		for suiteIndex, level in suiteSet: 
			cfg = ArtifactCuiLian_Dict.get((suiteIndex, level))
			if not cfg:
				continue
			pv = CuiLianHalo.percent.get(level, 0)
			if cfg.pt1 and pv:
				self.CuiLianHoleDict[cfg.pt1] = self.CuiLianHoleDict.get(cfg.pt1, 0) + pv
			if cfg.pt2 and pv:
				self.CuiLianHoleDict[cfg.pt2] = self.CuiLianHoleDict.get(cfg.pt2, 0) + pv
				
		return self.CuiLianHoleDict
	
class RoleHallowsMgr(Base.PackageBase):
	ObjEnumIndex = EnumObj.En_RoleHallows
	TypeObjFun = Base.Obj_Type_Fun
	def __init__(self, role, objDict, heroId = 0):
		Base.PackageBase.__init__(self, role, objDict, heroId)
	def GetMaxSize(self):
		#角色只有6格子
		return 6
	def GetRoleHallowsDict(self):
		roleHallowsdict = {}
		for hallows in self.objIdDict.itervalues():
			roleHallowsdict[hallows.cfg.posType] = hallows
		return roleHallowsdict
		
			

class HeroHallowsMgr(Base.PackageBase):
	ObjEnumIndex = EnumObj.En_HeroHallows
	TypeObjFun = Base.Obj_Type_Fun
	def __init__(self, role, objDict, heroId, hero):
		assert heroId != 0
		self.hero = hero
		assert hero is not None
		Base.PackageBase.__init__(self, role, objDict, heroId)
	def GetMaxSize(self):
		#英雄只有6格子
		return 6
	def GetHeroHallowsDict(self):
		heroHallowsdict ={}
		for hallows in self.objIdDict.itervalues():
			heroHallowsdict[hallows.cfg.posType] = hallows
		return heroHallowsdict
	
class RoleFashionMgr(Base.PackageBase):
	#时装
	ObjEnumIndex = EnumObj.En_RoleFashions
	TypeObjFun = Base.Obj_Type_Fun
	def __init__(self, role, objDict, heroId = 0):
		Base.PackageBase.__init__(self, role, objDict)
		
	def GetMaxSize(self):
		#只有4格子
		return 4
	
class RingMgr(Base.PackageBase):
	#订婚戒指
	ObjEnumIndex = EnumObj.En_RoleRing
	TypeObjFun = Base.Obj_Type_Fun
	def __init__(self, role, objDict, heroId = 0):
		Base.PackageBase.__init__(self, role, objDict)

class RoleMagicSpiritMgr(Base.PackageBase):
	#角色身上魔灵管理器
	ObjEnumIndex = EnumObj.En_RoleMagicSpirits
	TypeObjFun = Base.Obj_Type_Fun
	def __init__(self, role, objDict, heroId = 0):
		Base.PackageBase.__init__(self, role, objDict, heroId)

class HeroMagicSpiritMgr(Base.PackageBase):
	#英雄身上魔灵管理器
	ObjEnumIndex = EnumObj.En_HeroMagicSpirits
	TypeObjFun = Base.Obj_Type_Fun
	def __init__(self, role, objDict, heroId, hero):
		self.hero = hero
		Base.PackageBase.__init__(self, role, objDict, heroId)
