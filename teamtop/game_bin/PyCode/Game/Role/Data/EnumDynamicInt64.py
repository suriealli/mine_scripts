#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Data.EnumDynamicInt64")
#===============================================================================
# 角色Int64数组(动态)使用枚举
#===============================================================================
import cRoleDataMgr
from Common import CValue, Coding
from Game.Role.Data import Enum
from ComplexServer.Log import AutoLog

if "_HasLoad" not in dir():
	checkEnumSet = set()

def F(uIdx, nMinValue, nMinAction, nMaxValue, nMaxAction, bSyncClient = False, sLogEvent = "", uOverTime = CValue.MAX_UINT32):
	'''
	设置数值规范
	@param uIdx:下标索引
	@param nMinValue:最小值
	@param nMinAction:超过最小值的处理
	@param nMaxValue:最大值
	@param nMaxAction:超过最大值的处理
	@param bSyncClient:数值改变了是否同步客户端
	@param sLogEvent:数值改变了是否记录日志
	@param uOverTime:超时时间（默认不超时）
	'''
	assert uIdx < (Coding.RoleDynamicInt64Range[1] - Coding.RoleDynamicInt64Range[0])
	if uIdx in checkEnumSet:
		print "GE_EXC, error in EnumDynamicInt64 rule repeat enum (%s)" % uIdx
	checkEnumSet.add(uIdx)
	if sLogEvent: AutoLog.RegEvent(Coding.RoleDynamicInt64Range[0] + uIdx, sLogEvent)
	cRoleDataMgr.SetDynamicInt64Rule(uIdx, nMinValue, nMinAction, nMaxValue, nMaxAction, bSyncClient, sLogEvent, uOverTime)

#===============================================================================
# 数组使用定义
#===============================================================================

################################################################################################
#主线
################################################################################################
Task_Main = 0 #主线任务步骤
Task_Main_Chirld1 = 1 #主线任务子任务1
Task_Main_Chirld2 = 2 #主线任务子任务2
Task_Main_Chirld3 = 3 #主线任务子任务3

F(Task_Main, 0, Enum.DoIgnore, CValue.MAX_INT64, Enum.DoIgnore, True)
F(Task_Main_Chirld1, 0, Enum.DoIgnore, CValue.MAX_INT64, Enum.DoIgnore, True)
F(Task_Main_Chirld2, 0, Enum.DoIgnore, CValue.MAX_INT64, Enum.DoIgnore, True)
F(Task_Main_Chirld3, 0, Enum.DoIgnore, CValue.MAX_INT64, Enum.DoIgnore, True)


Task_None = 4 #可以复用
F(Task_None, 0, Enum.DoIgnore, CValue.MAX_INT64, Enum.DoIgnore, False)






