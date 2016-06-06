#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.RoleFightData.RoleFightData")
#===============================================================================
# 角色战斗数据管理模块
#===============================================================================
import Environment
from Game.Persistence import BigTable
from Game.Fight import Middle
from Game.Role import Event




class RoleFightBT(BigTable.BigTable):
	def SaveData(self):
		if self.returnDB:
			#只保存竞技场前2000名
			datadict = self.GetData()
			if len(datadict) > 3000:
				from Game.JJC import JJCMgr
				#人数大于3000人的时候才做数据整理逻辑，这样会在2000-3000之间拥有一个缓冲区
				for roleId in datadict.keys():
					roleRank = JJCMgr.GetJJCRank(roleId)
					if not roleRank or roleRank > 2000:
						self.DelKey(roleId)
		BigTable.BigTable.SaveData(self)


def GetRoleFightData(roleId):
	#获取战斗数据
	rD = RoleFD_BT.GetData().get(roleId)
	if not rD:
		return None
	return rD.get("fightData")


def UpdateRoleFightData(role):
	#更新战斗数据
	if not role.PropertyIsValid():
		#属性没有算好，强制重算一下属性
		role.ForceRecountProperty()
	roleId = role.GetRoleID()
	fightData = Middle.GetRoleData(role, True)
	RoleFD_BT.SetKeyValue(roleId, {"role_id" : roleId, "fightData" : fightData})


def UpdateFightData(roleId, fData):
	#用数据直接更新
	RoleFD_BT.SetKeyValue(roleId, {"role_id" : roleId, "fightData" : fData})

def DelFightData(roleId):
	RoleFD_BT.DelKey(roleId)


def HasFightData(role):
	#是否有战斗数据
	return role.GetRoleID() in RoleFD_BT.GetData()


def AfterLoadFromDB():
	#触发载入完毕事件
	Event.TriggerEvent(Event.Eve_Sys_RoleFightData_OK, None, None)


if "_HasLoad" not in dir():
	if Environment.HasLogic or Environment.HasWeb:
		#定义战斗数据持久化大表,每次载入50条记录
		RoleFD_BT = RoleFightBT("sys_rolefightdata", 50, AfterLoadFromDB)
		
		

