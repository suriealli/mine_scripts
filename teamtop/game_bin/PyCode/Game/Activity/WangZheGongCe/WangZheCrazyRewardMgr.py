#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.WangZheGongCe.WangZheCrazyRewardMgr")
#===============================================================================
# 奖励狂翻倍 mgr
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
from Game.Activity.WangZheGongCe import WangZheCrazyRewardConfig


IDX_CRAZYREWARD = 6 

if "_HasLoad" not in dir():
	IS_START = False
	
	#格式 {finishTaskIndex:rewardFlag,}
	WangZheCrazyReward_TaskData_S = AutoMessage.AllotMessage("WangZheCrazyReward_TaskData_S", "奖励狂翻倍_任务数据同步")
	
	Tra_WangZheCrazyReward_GetCrazyReward = AutoLog.AutoTransaction("Tra_WangZheCrazyReward_GetCrazyReward", "奖励狂翻倍_请求领取奖励")


# 活动控制 start
def OnStartWangZheCrazyReward(*param):
	'''
	奖励狂翻倍_活动开启
	'''
	_, circularType = param
	if CircularDefine.CA_WangZheCrazyReward != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open WangZheCrazyReward"
		return 
	
	IS_START = True

def OnEndWangZheCrazyReward(*param):
	'''
	奖励狂翻倍_活动结束
	'''
	_, circularType = param
	if CircularDefine.CA_WangZheCrazyReward != circularType:
		return
	
	global IS_START
	if not IS_START:
		print "GE_EXC,end WangZheCrazyReward while not start"
	IS_START = False


#客户端请求 start
def OnGetCrazyReward(role, msg):
	'''
	奖励狂翻倍_请求领取奖励
	@param msg: tastIndex
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.WangZheGongCe_NeedLevel:
		return
	
	taskIndex = msg
	taskCfg = WangZheCrazyRewardConfig.WZCR_TaskConfig_Dict.get(taskIndex)
	if not taskCfg:
		return
	
	#未完成对应任务 or 已领取对应奖励
	CRTaskDataDict = role.GetObj(EnumObj.WangZheGongCe)[IDX_CRAZYREWARD]
	if (taskIndex not in CRTaskDataDict) or CRTaskDataDict[taskIndex] is False:
		return
	
	prompt = GlobalPrompt.WZCR_Tips_Head
	with Tra_WangZheCrazyReward_GetCrazyReward:
		CRTaskDataDict[taskIndex] = False
		for coding, cnt in taskCfg.rewardItems:
			role.AddItem(coding, cnt)
			prompt += GlobalPrompt.Item_Tips % (coding, cnt)
	
	#获得提示
	role.Msg(2, 0, prompt)
	#同步最新数据
	role.SendObj(WangZheCrazyReward_TaskData_S, CRTaskDataDict)


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
		#王者公测奖励狂翻倍任务进度
		Event.TriggerEvent(Event.Eve_WangZheCrazyRewardTask, role, (EnumGameConfig.WZCR_Task_MarryParty, True))


# 事件 start
def OnInitRole(role, param = None):
	'''
	角色初始化相关key
	'''
	wangZheGongCeData = role.GetObj(EnumObj.WangZheGongCe)
	if IDX_CRAZYREWARD not in wangZheGongCeData:
		wangZheGongCeData[IDX_CRAZYREWARD] = {}

def OnDayClear(role, param = None):
	'''
	跨天清理 任务状态
	'''
	if not IS_START:
		return
	
	crazyTaskDataDict = role.GetObj(EnumObj.WangZheGongCe)[IDX_CRAZYREWARD]
	crazyTaskDataDict.clear()
	
	#同步最新
	role.SendObj(WangZheCrazyReward_TaskData_S, crazyTaskDataDict)
	

def OnSyncOtherData(role, param = None):
	'''
	角色上线   兼容维护前已完成的任务 并  同步奖励狂翻倍活动数据
	'''
	#更新前已完成今日派对 直接完成对应目标项
	if 3 == role.GetDI8(EnumDayInt8.PartyStatus):
		AfterFinishTask(role, (EnumGameConfig.WZCR_Task_MarryParty, False))
	
	role.SendObj(WangZheCrazyReward_TaskData_S, role.GetObj(EnumObj.WangZheGongCe)[IDX_CRAZYREWARD])
	
def AfterFinishTask(role, param = None):
	'''
	任务完成触发数据记录处理
	'''
	if not IS_START:
		return
	
	taskIndex, isSync = param
	if taskIndex not in WangZheCrazyRewardConfig.WZCR_TaskConfig_Dict:
		return
	
	CRTaskDataDict = role.GetObj(EnumObj.WangZheGongCe)[IDX_CRAZYREWARD]
	if taskIndex in CRTaskDataDict:
		return
	
	CRTaskDataDict[taskIndex] = True
	
	if isSync:
		role.SendObj(WangZheCrazyReward_TaskData_S, CRTaskDataDict)

if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.IsDevelop or Environment.EnvIsQQ() or Environment.EnvIsFT() or Environment.EnvIsTK() or Environment.EnvIsRU()):
		Event.RegEvent(Event.Eve_InitRolePyObj, OnInitRole)
	
	if Environment.HasLogic and not Environment.IsCross and (Environment.IsDevelop or Environment.EnvIsQQ() or Environment.EnvIsFT() or Environment.EnvIsTK() or Environment.EnvIsRU()):
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartWangZheCrazyReward)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndWangZheCrazyReward)
		
		Event.RegEvent(Event.Eve_RoleDayClear, OnDayClear)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncOtherData)
		
		Event.RegEvent(Event.Eve_WangZheCrazyRewardTask, AfterFinishTask)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WangZheCrazyReward_OnGetCrazyReward", "奖励狂翻倍_请求领取奖励"), OnGetCrazyReward)
		
