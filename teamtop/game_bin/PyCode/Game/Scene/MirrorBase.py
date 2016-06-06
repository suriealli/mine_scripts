#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Scene.MirrorBase")
#===============================================================================
# 单人副本基类
#===============================================================================
import cRoleMgr
from Common.Message import AutoMessage
from Game.Role.Data import EnumTempObj, EnumInt1
from Game.Role import Status


#副本基类
class SingleMirrorBase(object):
	MirrorType = 1
	def __init__(self, role):
		self.role = role
		#场景对象
		self.mirrorScene = None
		#全局ID(注意区别场景ID, 全局ID唯一， 场景ID不唯一)
		self.mirrorGId = 0
		
		self.createOk = False

	def AfterJoinRole(self):
		#角色进入调用,设置私有NPC字典
		self.role.SetTempObj(EnumTempObj.PrivateNPCDict, {})
	
	def AfterReLoginRole(self, role):
		#角斗重新登录过触发
		self.mirrorScene.RestoreRole(self.role)
		#场景内容恢复
		for npc in self.role.GetTempObj(EnumTempObj.PrivateNPCDict).values():
			npc.SyncNPC()
		
	
	
	def ClearAllNPC(self):
		if not self.role:
			return
		for npc in self.role.GetTempObj(EnumTempObj.PrivateNPCDict).values():
			npc.Destroy()

	def Destroy(self):
		#销毁副本
		if not self.mirrorScene:
			return
		#调用C++函数，踢掉副本内玩家,可能会触发玩家退出场景调用函数
		if self.mirrorScene.IsDestroy():
			return
		self.mirrorScene.Destroy()
		self.mirrorScene = None
		
		#此时role已经掉线
		if self.role.IsKick():
			return
		
		if self.role.GetTempObj(EnumTempObj.MirrorScene) == self:
			#清理临时缓存数据
			self.role.SetTempObj(EnumTempObj.MirrorScene, None)
			self.role.SetTempObj(EnumTempObj.PrivateNPCDict, {})



	def BackToCity(self, role):
		#客户端请求回城
		self.Destroy()
	
	
	def BeforeLeave(self, scene, role):
		#离开关卡调用， 一般用于角色掉线，或者没用通过回城达到离开关卡处理
		#请不要在此函数内调用scene.Destroy()
		#退出副本状态
		Status.Outstatus(role, EnumInt1.ST_InMirror)
	
		#清理临时缓存数据
		role.SetTempObj(EnumTempObj.MirrorScene, None)
		role.SetTempObj(EnumTempObj.PrivateNPCDict, {})
	
######################################################################################

def GetNowMirror(role):
	#获取角色当前所在副本
	mirror = role.GetTempObj(EnumTempObj.MirrorScene)
	if not mirror:
		return None
	# 检测场景是否符合
	if role.GetScene() is not mirror.mirrorScene:
		#print "GE_EXC, GetNowMirror error scene not mirror (%s)" % role.GetRoleID()
		return None
	return mirror
	
######################################################################################
#其他处理
######################################################################################

def RestoreMirror(role):
	mirror = role.GetTempObj(EnumTempObj.MirrorScene)
	if not mirror:
		return False
	mirror.AfterReLoginRole(role)
	return True


def BackToCity(role, msg):
	#客户端请求回城
	mirror = GetNowMirror(role)
	if not mirror:
		#print "GE_EXC, BackToCity error not mirror (%s)" % role.GetRoleID()
		return
	if not Status.CanInStatus(role, EnumInt1.ST_TP):
		#print "GE_EXC, role backtocity statue error (%s)" % role.GetRoleID()
		return
	mirror.BackToCity(role)

if "_HasLoad" not in dir():
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Mirror_BackToCity", "在副本内请求回城"), BackToCity)


