#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Obj.Base")
#===============================================================================
# Obj和管理基类
#===============================================================================
import traceback
from Common import Serialize
from Game.Role.Data import EnumTempObj
from Common.Other import EnumKick


KR = "背包数据异常"

if "_HasLoad" not in dir():
	Obj_Config = {}
	Obj_Type_Fun = {}
	#特殊的可叠加限时物品
	Obj_Time_Overlap = set()

#obj对象枚举
Obj_Type_Base = 1
Obj_Type_Item = 2
Obj_Type_Equipment = 3
Obj_Type_Hero = 4
Obj_Type_TimeItem = 5#时效性道具(不能叠加)
Obj_Type_Artifact = 6 #神器
Obj_Type_Hallows = 7#圣器
Obj_Type_DragonEquipment = 8#驯龙装备
Obj_Type_Fashion = 9	#时装
Obj_Type_Ring = 10	#订婚戒指
Obj_Type_MagicSpirit = 11	#魔灵
Obj_Type_TimeItemOverlap = 12#时效性道具(可以叠加)
#对象基类
class ObjBase(object):
	Obj_Type = Obj_Type_Base
	def __init__(self, role, obj):
		self.role = role
		self.oid, self.otype, self.oint, self.odata = obj
	
	def AfterCreate(self):
		# 创建调用
		cfg = Obj_Config.get(self.otype)
		if not cfg: 
			print "GE_EXC, create obj error not cfg (%s)" % self.otype
			return False
		self.cfg = cfg
		return True

	
	def AfterLoad_Except(self):
		# 数据库载入调用
		self.cfg = Obj_Config[self.otype]

	
	def BeforeDelete(self):
		pass
	
	def OnDeadTime(self, role, callargv, regparam):
		pass

###########################################################################
#包裹基类
###########################################################################
class PackageBase(object):
	#对应角色OBJ枚举
	ObjEnumIndex = -1
	TypeObjFun = lambda item: None
	def __init__(self, role, objDict, heroId = 0):
		'''
		初始化
		@param role:
		@param objDict:对象字典 objId --> DB_obj  从数据库载入，列表构建成字典
		'''
		self.role = role
		self.heroId = heroId
		self.objIdDict = {}			#oid --> obj
		self.codingGather = {}		#coding -> {oid --> obj}
		try:
			#优化循环操作(消点)
			OJBS_POP = objDict.pop
			OBJ_TYPE_FUN = self.TypeObjFun

			SELF_ID_OBJ_DICT = self.objIdDict
			SELF_COIDNGGATHER = self.codingGather
			SC_GET = self.codingGather.get
			OPI = self.ObjEnumIndex
			GLOBAL_ITEMDICT = role.GetTempObj(EnumTempObj.enGlobalItemMgr)
			
			tempObjIdSet = set()
			if heroId:
				tempObjIdSet = role.GetObj(OPI).get(heroId)
			else:
				tempObjIdSet = role.GetObj(OPI)
			
			SS2P = Serialize.String2PyObjEx
			#构建对象
			for oid in tempObjIdSet:
				obj = OJBS_POP(oid)
				otype = obj[1]
				#根据这个函数，传入DB对象数据，构建一个PYTHON对象
				newobj = OBJ_TYPE_FUN[otype](role, obj)
				#载入后调用,反序列化
				newobj.odata = SS2P(newobj.odata)
				#缓存背包
				newobj.package = self
				#内部coding管理容器
				coding_objDict = SC_GET(otype)
				if coding_objDict is None:
					SELF_COIDNGGATHER[otype] = coding_objDict = {}
				coding_objDict[oid] = newobj
				SELF_ID_OBJ_DICT[oid] = newobj
				#全局物品管理
				GLOBAL_ITEMDICT[oid] = newobj
				#触发对象载入后的调用函数
				newobj.AfterLoad_Except()
		except:
			#有异常，踢玩家，不保存数据
			traceback.print_exc()
			self.role.Kick(False, EnumKick.DataError)
	
	def GetMaxSize(self):
		return 0
	
	def EmptySize(self):
		return self.GetMaxSize() - len(self.objIdDict)
	
	def IsFull(self):
		return len(self.objIdDict) >= self.GetMaxSize()
	
	def UseSize(self):
		#已经使用的位置大小
		return len(self.objIdDict)
	
	def ItemCnt(self, coding):
		#这类coding数量
		obj_dict = self.codingGather.get(coding)
		if obj_dict is None:
			return 0
		cnt = 0
		for obj in obj_dict.itervalues():
			cnt += obj.oint
		return cnt
	
	
	def ItemCnt_NotTimeOut(self, coding):
		#非过期的物品数量
		obj_dict = self.codingGather.get(coding)
		if obj_dict is None:
			return 0
		cnt = 0
		for obj in obj_dict.itervalues():
			if obj.IsDeadTime():
				continue
			cnt += obj.oint
		return cnt
	
	def FindItem(self, coding):
		#特殊，按照一个coding搜索一个物品对象
		obj_dict = self.codingGather.get(coding)
		if not obj_dict:
			return None
		return obj_dict.values()[0]
		
		
	def FindProp(self, propId):
		#按照ID查找物品
		return self.objIdDict.get(propId)
	
	def GetDBObjList(self):
		#持久化数据，保存到数据库,注意要把odata序列化
		objlist = []
		OA = objlist.append
		SP2S = Serialize.PyObj2String
		for obj in self.objIdDict.itervalues():
			OA((obj.oid, obj.otype, obj.oint, SP2S(obj.odata)))
		return objlist
	
	def GetSyncObjDict(self):
		#同步客户端数据
		objDict = {}
		for obj in self.objIdDict.itervalues():
			objDict[obj.oid] = (obj.otype, obj.oint, obj.odata)
		return objDict
	
	def Destroy(self):
		pass



