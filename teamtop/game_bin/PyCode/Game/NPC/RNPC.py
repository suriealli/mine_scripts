#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.NPC.RNPC")
#===============================================================================
# 和游戏角色一样的NPC(其实是一段数据)
#===============================================================================
from Common.Message import AutoMessage
from Common.Other import EnumAppearance
from Game.Role.Data import EnumTempInt64, EnumObj, EnumInt1



if "_HasLoad" not in dir():
	RNPCId_Allot = 0
	RNPC_Dict = {}

def AllotID():
	global RNPCId_Allot
	RNPCId_Allot += 1
	return RNPCId_Allot


if "_HasLoad" not in dir():
	#消息
	RNPC_Data = AutoMessage.AllotMessage("RNPC_Data", "一个真人NPC数据")
	RNPC_Remove = AutoMessage.AllotMessage("RNPC_Remove", "移除一个真人NPC")



class RNPC(object):
	def __init__(self, roleId, sceneId, posX, posY, direction, viewData, rnpcType):
		self.rnpcID = AllotID()
		self.rnpcType = rnpcType
		self.roleId = roleId
		self.sceneId = sceneId
		self.posX = posX
		self.posY = posY
		self.direction = direction
		self.viewData = viewData
		
		self.PackData()
		
		global RNPC_Dict
		RNPC_Dict[self.rnpcID] = self
		
	def PackData(self):
		self.data = (self.rnpcID, self.posX, self.posY, self.direction, self.viewData, self.rnpcType)
	
	def SyncToRole(self, role):
		role.SendObj(RNPC_Data, self.data)


def TestRNPC(role, posX, posY, direction = 0, rnpcType = 1):
	viewData = {}
	viewData[EnumAppearance.App_RoleID] = role.GetRoleID()
	viewData[EnumAppearance.App_Name] = role.GetRoleName()						#名字
	viewData[EnumAppearance.App_Sex] = role.GetSex()							#性别
	viewData[EnumAppearance.App_Career] = role.GetCareer()						#职业
	viewData[EnumAppearance.App_Grade] = role.GetGrade()					#进阶
	viewData[EnumAppearance.App_NewTitle] = role.GetObj(EnumObj.Title).get(2, [])				#角色称号
	viewData[EnumAppearance.App_WingId] = role.GetWingID()						#翅膀ID
	viewData[EnumAppearance.APP_FashionClothes] =  role.GetTI64(EnumTempInt64.FashionClothes)#时装衣服
	viewData[EnumAppearance.App_FashionHat] =  role.GetTI64(EnumTempInt64.FashionHat)#时装帽子
	viewData[EnumAppearance.App_FashionWeapons] =  role.GetTI64(EnumTempInt64.FashionWeapons)#时装武器
	viewData[EnumAppearance.App_FashionState] =  role.GetI1(EnumInt1.FashionViewState)#时装显示状态
	
	rnpc = RNPC(role.GetRoleID(),role.GetSceneID(), posX, posY, direction, viewData, rnpcType)
	rnpc.SyncToRole(role)

