#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.NPC.PrivateNPC.PrivateNPC")
#===============================================================================
# 私有NPC基类
#===============================================================================
import traceback
import cNPCMgr
from Game.Role.Data import EnumTempObj
from Game.NPC import NPCMgr
from Game import GlobalMessage
from Game.Role import Event


def OnClickPrivateNPC(role, npcID):
	#点击玩家私有NPC
	#由C++触发，单人副本点击NPC调用，或者公共场景点击NPC，查询公告场景NPC管理没有发现，会尝试调用这个函数
	#NPC对象存储在角色
	npc = role.GetTempObj(EnumTempObj.PrivateNPCDict).get(npcID)
	if not npc:
		return
	if not npc.CanClick(role):
		return
	#因为是私有的NPC，就不用传role参数了
	npc.clickFun(npc)


def OnClickMirrorNPC(role, npcID):
	#点击副本私有NPC
	#由C++触发，多人副本点击NPC时触发
	#NPC对象存储在多人副本对象中
	mirrorScene = role.GetTempObj(EnumTempObj.MirrorScene)
	if not mirrorScene:
		return
	mirrorScene.OnClickMirrorNPC(role, npcID)



#私有NPC,属于一个玩家个人拥有
#请创建在单人副本中,多人副本不支持创建此NPC，会点击触发不了clickFun
class PrivateNPC(object):
	def __init__(self, role, npcType, x, y, direction, clickFun = None):
		'''
		玩家私有NPC
		@param role:角色对象
		@param npcType:npc类型
		@param x:位置
		@param y:位置
		@param direction:方向
		@param clickFun:点击函数
		'''
		self.gid = cNPCMgr.AllotGlobalID()
		self.role = role
		self.npcType = npcType
		self.posX = x
		self.posY = y
		self.direction = direction
		self.sceneId= role.GetSceneID()
		self.clickFun = clickFun
		
		#缓存NPC数据
		role.GetTempObj(EnumTempObj.PrivateNPCDict)[self.gid] = self
		
		self.SyncNPC()
		
	def SyncNPC(self):
		#同步NPC数据(如果特殊NPC,同步信息不一样可以重载这个函数)
		self.role.SendObj(GlobalMessage.NPC_Pos, (self.gid, self.npcType, self.posX, self.posY, self.direction))
	
	def Destroy(self):
		#告诉客户端NPC消失
		self.role.SendObj(GlobalMessage.NPC_Disappear, self.gid)
		self.role.GetTempObj(EnumTempObj.PrivateNPCDict).pop(self.gid, None)
	
	
	def CanClick(self, role):
		#是否可以点击
		return True
	
	def GetNPCID(self):
		#全局ID
		return self.gid
	
	def GetNPCType(self):
		#类型
		return self.npcType

	def GetNPCName(self):
		#名字
		return NPCMgr.GetNPCName(self.npcType)

#副本私有NPC,属于副本，不属于固定的玩家
#请创建在多人副本中
class MirrorNPC(object):
	def __init__(self, mirrorScene, npcType, x, y, direction, clickFun = None):
		'''
		#副本私有NPC
		@param mirrorScene:
		@param sceneID:
		@param npcType:
		@param x:
		@param y:
		@param direction:
		@param clickFun:
		'''
		self.gid = cNPCMgr.AllotGlobalID()
		self.npcType = npcType
		self.posX = x
		self.posY = y
		self.mirrorScene = mirrorScene
		self.clickFun = clickFun
		self.direction = direction
		
		self.BuildSyncMsg()
		
		self.mirrorScene.JoinNPC(self)
	
	def BuildSyncMsg(self):
		#构建同步消息(如果是特殊的NPC，同步消息不一样，可以重载此函数)
		self.Msg = GlobalMessage.NPC_Pos
		self.syncData = (self.gid, self.npcType, self.posX, self.posY, self.direction)
	
	def SyncToRole(self, role):
		#同步给一个角色
		role.SendObj(self.Msg, self.syncData)
	
	def SyncToRoles(self, roles):
		#同步给多个角色
		for role in roles:
			role.SendObj(self.Msg, self.syncData)
	
	def Destroy(self):
		#销毁这个NPC
		try:
			self.mirrorScene.LeaveNPC(self.gid)
		except:
			traceback.print_exc()
			
	def GetNPCID(self):
		#全局ID
		return self.gid
	
	def GetNPCType(self):
		#类型
		return self.npcType

	def GetNPCName(self):
		#名字
		return NPCMgr.GetNPCName(self.npcType)
	
	def CanClick(self, role):
		#是否可以点击
		return True

def AfterLogin(role, param):
	#先初始化，不然第一次取可能是None
	role.SetTempObj(EnumTempObj.PrivateNPCDict, {})

if "_HasLoad" not in dir():
	Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)

