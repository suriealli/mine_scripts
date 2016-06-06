#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionMultiRewardMgr")
#===============================================================================
# 激情奖励翻倍Mgr
#===============================================================================
import cRoleMgr
import cDateTime
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Activity import CircularDefine
from Game.Role.Data import EnumObj, EnumDayInt8
from Game.Activity.PassionAct import PassionMultiRewardConfig, PassionDefine



if "_HasLoad" not in dir():
	IS_START = False
	
	#格式 {finishTaskIndex:rewardFlag,}
	PassionMultiReward_TaskData_S = AutoMessage.AllotMessage("PassionMultiReward_TaskData_S", "激情奖励翻倍_任务数据同步")
	
	Tra_PassionMultiReward_GetCrazyReward = AutoLog.AutoTransaction("Tra_PassionMultiReward_GetCrazyReward", "激情奖励翻倍_请求领取奖励")


# 活动控制 start
def OnStartPassionMultiReward(*param):
	'''
	激情奖励翻倍_活动开启
	'''
	_, circularType = param
	if CircularDefine.CA_PassionMultiReward != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open PassionMultiReward"
		return 
	
	IS_START = True

def OnEndPassionMultiReward(*param):
	'''
	激情奖励翻倍_活动结束
	'''
	_, circularType = param
	if CircularDefine.CA_PassionMultiReward != circularType:
		return
	
	global IS_START
	if not IS_START:
		print "GE_EXC,end PassionMultiReward while not start"
	IS_START = False


#客户端请求 start
def OnGetCrazyReward(role, msg):
	'''
	激情奖励翻倍_请求领取奖励
	@param msg: tastIndex
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.PassionMultiReward_NeedLevel:
		return
	
	taskIndex = msg
	taskCfg = PassionMultiRewardConfig.PassionMultiReward_TaskConfig_Dict.get(taskIndex)
	if not taskCfg:
		return
	
	#未完成对应任务 or 已领取对应奖励
	CRTaskDataDict = role.GetObj(EnumObj.PassionActData)[PassionDefine.PassionMultiReward]
	if (taskIndex not in CRTaskDataDict) or CRTaskDataDict[taskIndex] is False:
		return
	
	prompt = GlobalPrompt.PassionMultiReward_Tips_Head
	with Tra_PassionMultiReward_GetCrazyReward:
		CRTaskDataDict[taskIndex] = False
		for coding, cnt in taskCfg.rewardItems:
			role.AddItem(coding, cnt)
			prompt += GlobalPrompt.Item_Tips % (coding, cnt)
	
	#获得提示
	role.Msg(2, 0, prompt)
	#同步最新数据
	role.SendObj(PassionMultiReward_TaskData_S, CRTaskDataDict)


#辅助start
#离线命令执行 修改请三思
def AfterParty(role, param):
	'''
	派对完成
	'''
	if not IS_START:
		return
	
	partyDays = param	
	if partyDays == cDateTime.Days():
		#王者公测激情奖励翻倍任务进度
		Event.TriggerEvent(Event.Eve_PassionMultiRewardTask, role, (EnumGameConfig.PassionMulti_Task_MarryParty, True))


# 事件 start
def OnInitRole(role, param = None):
	'''
	角色初始化相关key
	'''
	passionActData = role.GetObj(EnumObj.PassionActData)
	if PassionDefine.PassionMultiReward not in passionActData:
		passionActData[PassionDefine.PassionMultiReward] = {}

def OnDayClear(role, param = None):
	'''
	跨天清理 任务状态
	'''
	if not IS_START:
		return
	
	crazyTaskDataDict = role.GetObj(EnumObj.PassionActData)[PassionDefine.PassionMultiReward]
	crazyTaskDataDict.clear()
	
	#同步最新
	role.SendObj(PassionMultiReward_TaskData_S, crazyTaskDataDict)
	

def OnSyncOtherData(role, param = None):
	'''
	角色上线   兼容维护前已完成的任务 并  同步激情奖励翻倍活动数据
	'''
	#更新前已完成今日派对 直接完成对应目标项
	if 3 == role.GetDI8(EnumDayInt8.PartyStatus):
		AfterFinishTask(role, (EnumGameConfig.PassionMulti_Task_MarryParty, False))
	
	role.SendObj(PassionMultiReward_TaskData_S, role.GetObj(EnumObj.PassionActData)[PassionDefine.PassionMultiReward])
	
def AfterFinishTask(role, param = None):
	'''
	任务完成触发数据记录处理
	'''
	if not IS_START:
		return
	
	taskIndex, isSync = param
	if taskIndex not in PassionMultiRewardConfig.PassionMultiReward_TaskConfig_Dict:
		return 
	
	CRTaskDataDict = role.GetObj(EnumObj.PassionActData)[PassionDefine.PassionMultiReward]
	if taskIndex in CRTaskDataDict:
		return
	
	CRTaskDataDict[taskIndex] = True
	
	if isSync:
		role.SendObj(PassionMultiReward_TaskData_S, CRTaskDataDict)

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_InitRolePyObj, OnInitRole)
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartPassionMultiReward)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndPassionMultiReward)
		
		Event.RegEvent(Event.Eve_RoleDayClear, OnDayClear)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncOtherData)
		
		Event.RegEvent(Event.Eve_PassionMultiRewardTask, AfterFinishTask)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("PassionMultiReward_OnGetCrazyReward", "激情奖励翻倍_请求领取奖励"), OnGetCrazyReward)
