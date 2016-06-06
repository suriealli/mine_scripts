#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.OG.OGTaskMgr")
#===============================================================================
# OG任务管理
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Game.Activity.OG import OGConfig
from Game.Role import Event
from Game.Role.Data import EnumObj

if "_HasLoad" not in dir():
	#消息
	OG_Sync_All_Task = AutoMessage.AllotMessage("OG_Sync_All_Task", "通知客户端所有OG任务状态")

def FinishOGTask(role, taskId):
	ogTaskConfig = OGConfig.OG_TASK.get(taskId)
	if not ogTaskConfig:
		return
	
	ogTaskDict = role.GetObj(EnumObj.OG)
	
	#已经完成任务
	if taskId in ogTaskDict:
		return
	
	ogTaskDict[taskId] = 1

#===============================================================================
# 事件
#===============================================================================
def OnSyncRoleOtherData(role, param):
	'''
	角色登陆同步其它数据
	@param role:
	@param param:
	'''
	ogTaskDict = role.GetObj(EnumObj.OG)
	
	role.SendObj(OG_Sync_All_Task, ogTaskDict)

#===============================================================================
# 客户端请求
#===============================================================================
def RequestOGFinishTask(role, msg):
	'''
	客户端请求完成OG任务
	@param role:
	@param msg:
	'''
	taskId = msg
	
	FinishOGTask(role, taskId)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#版本判断
		if Environment.EnvIsNA():
			#角色登陆同步其它数据
			Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
			#注册消息
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("OG_Finish_Task", "客户端请求完成OG任务"), RequestOGFinishTask)
		
	