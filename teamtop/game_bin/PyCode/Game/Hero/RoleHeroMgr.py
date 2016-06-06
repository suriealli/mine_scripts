#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Hero.RoleHeroMgr")
#===============================================================================
# 角色英雄管理器
#===============================================================================
import traceback
from Common import Serialize
from Common.Other import   EnumKick
from Game.Hero import HeroBase
from Game.Role.Data import EnumObj

#角色自带临时英雄管理器
class RoleHeroMgr(object):
	def __init__(self, role, objsDict):
		self.role = role
		self.HeroDict = {}		#heroID --> hero
		
		#优化循环操作(消点)
		OJBS_POP = objsDict.pop
		SELF_HERO_DICT = self.HeroDict
		OBJ_TYPE_FUN = HeroBase.Hero
		try:
			herodataDict = role.GetObj(EnumObj.En_Hero_Data_Dict)
			if not herodataDict:
				herodataDict[1] = [] 	#英雄ID列表
				herodataDict[2] = {} 	#招募英雄CD字典	{heroNumber --> 下次招募时间戳}
				herodataDict[3] = {} 	#招募英雄类型字典	{heroType --> set(heroID)}
				
			SS2P = Serialize.String2PyObjEx
			for oid in herodataDict[1]:
				assert oid not in SELF_HERO_DICT
				obj = OJBS_POP(oid)
				newobj = OBJ_TYPE_FUN(role, obj)
				newobj.odata = SS2P(newobj.odata)
				SELF_HERO_DICT[newobj.oid] = newobj
				#触发对象载入后的调用函数
				newobj.AfterLoad_Except()
		except:
			#有异常，踢玩家，不保存数据
			traceback.print_exc()
			self.role.Kick(False, EnumKick.DataError_Hero)

	def GetDBObjList(self):
		#持久化
		objlist = []
		OA = objlist.append
		SP2S = Serialize.PyObj2String
		for obj in self.HeroDict.itervalues():
			OA((obj.oid, obj.onumber, obj.oint, SP2S(obj.odata)))
		return objlist
	
	def GetSyncObjDict(self):
		#同步客户端
		objDict = {}
		for obj in self.HeroDict.itervalues():
			objDict[obj.oid] = (obj.onumber, obj.odata)
		return objDict
	
	def Destroy(self):
		pass
	
	def HasHeroNumber(self, heroNumber):
		#是否有这个编号的英雄
		for heroobj in self.HeroDict.itervalues():
			if heroNumber == heroobj.onumber:
				return True
		return False
	
	def IsHeroFull(self):
		#最多招募34个英雄
		return len(self.HeroDict) >= 34
	
	
	def HeroEmptyCnt(self):
		#还可以招募多少个英雄
		return 34 - len(self.HeroDict)
	
	def HasTypeAndLevel(self, heroType, grade, level):
		#英雄类型, 品阶, 等级
		#返回是否有超过该英雄品阶、等级的英雄的相同类型英雄
		for heroobj in self.HeroDict.itervalues():
			if heroType != heroobj.GetType():
				continue
			if grade != heroobj.GetGrade():
				continue
			if level > heroobj.GetLevel():
				continue
			return True
		return False
	
	def GetHeroCnt(self):
		#返回现有英雄个数
		return len(self.HeroDict)
	
