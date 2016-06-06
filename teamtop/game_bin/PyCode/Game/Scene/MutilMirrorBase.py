#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Scene.MutilMirrorBase")
#===============================================================================
# 多人副本基类
# 必须注册离开调用函数,函数内部处理角色临时缓存副本对象的清除,还有一些数据，状态的管理清除
# 副本内创建的NPC也要创建副本私有NPC
#===============================================================================
from Game import GlobalMessage
from Game.Role.Data import EnumTempObj




class MutilMirrorBase(object):
	def __init__(self):
		#角色们
		self.roles = set()
		#场景对象
		self.mirrorScene = None
		#全局ID(注意区别场景ID, 全局ID唯一， 场景ID不唯一)
		self.mirrorGId = 0
		#副本私有npc缓存
		self.mirrorNPCDict= {}

	def AfterJoinRole(self, role):
		#角色进入调用
		self.roles.add(role)
		#设置临时对象
		role.SetTempObj(EnumTempObj.MirrorScene, self)
	
	def AfterJoinRoles(self, roles):
		#多个角色进入后调用
		for role in roles:
			#角色进入调用
			self.roles.add(role)
			#设置临时对象
			role.SetTempObj(EnumTempObj.MirrorScene, self)
	
	def BeforeLeave(self, role):
		#角色离开调用
		self.roles.discard(role)
		
	def ReadyToDestroy(self):
		#准备销毁这个多人副本(一般用于多人限时副本)
		self.mirrorScene.ReadyToDestroy()
	
	def Destroy(self):
		#销毁副本(注意多人限时副本的处理需要非常小心,一般把权限交给C++处理比较好)
		if not self.mirrorScene:
			return
		if self.mirrorScene.IsDestroy():
			return
		#调用C++函数，踢掉副本内玩家,会触发玩家退出场景调用函数
		self.mirrorScene.Destroy()
		self.mirrorScene = None
		self.mirrorGId = 0
	
	def OnClickMirrorNPC(self, role, npcID):
		#点击了副本NPC
		npc = self.mirrorNPCDict.get(npcID)
		if not npc:
			return
		if not npc.clickFun:
			return
		#需要指定哪一个角色点击NPC
		npc.clickFun(npc, role)
	
	def JoinNPC(self, npc):
		#加入一个NPC
		self.mirrorNPCDict[npc.gid] = npc
		#同步消息
		npc.SyncToRoles(self.roles)

	def LeaveNPC(self, gid):
		#销毁一个NPC
		if gid not in self.mirrorNPCDict:
			return
		for role in self.roles:
			role.SendObj(GlobalMessage.NPC_Disappear, gid)
		del self.mirrorNPCDict[gid]

	def ClearAllNPC(self):
		#清理所有的NPC
		for npc in self.mirrorNPCDict.values():
			npc.Destroy()
	
	def SyncALLNPC(self, role):
		for npc in self.mirrorNPCDict.values():
			npc.SyncToRole(role)
	
	def BackToCity(self, role):
		role.BackPublicScene()



