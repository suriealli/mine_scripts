#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Data.EnumInt64")
#===============================================================================
# 角色Int64数组使用枚举
#===============================================================================
import cRoleDataMgr
from Common import CValue, Coding
from ComplexServer.Log import AutoLog
from Game.Role.Data import Enum

if "_HasLoad" not in dir():
	checkEnumSet = set()
	
def F(uIdx, nMinValue, nMinAction, nMaxValue, nMaxAction, bSyncClient = False, sLogEvent = ""):
	'''
	设置数值规范
	@param uIdx:下标索引
	@param nMinValue:最小值
	@param nMinAction:超过最小值的处理
	@param nMaxValue:最大值
	@param nMaxAction:超过最大值的处理
	@param bSyncClient:数值改变了是否同步客户端
	@param sLogEvent:数值改变了是否记录日志
	'''
	assert uIdx < (Coding.RoleInt64Range[1] - Coding.RoleInt64Range[0])
	if uIdx in checkEnumSet:
		print "GE_EXC, error in EnumInt32 rule repeat enum (%s)" % uIdx
	checkEnumSet.add(uIdx)
	if sLogEvent: AutoLog.RegEvent(Coding.RoleInt64Range[0] + uIdx, sLogEvent)
	cRoleDataMgr.SetInt64Rule(uIdx, nMinValue, nMinAction, nMaxValue, nMaxAction, bSyncClient, sLogEvent)

#===============================================================================
# 数组使用定义
#===============================================================================
enMoney = 0 #金币
F(enMoney, 0, Enum.DoIgnore, CValue.MAX_INT64, Enum.DoIgnore, True, "改变金币")

En_Exp = 1 #经验
F(En_Exp, 0, Enum.DoIgnore, CValue.MAX_INT64, Enum.DoIgnore, True, "改变经验")

PetID = 2 #宠物ID
F(PetID, 0, Enum.DoIgnore, CValue.MAX_INT64, Enum.DoIgnore, True)

PetFollowID = 3 #跟随的宠物ID
F(PetFollowID, 0, Enum.DoIgnore, CValue.MAX_INT64, Enum.DoIgnore, True)

JTeamID = 4 #战队ID
F(JTeamID, 0, Enum.DoIgnore, CValue.MAX_INT64, Enum.DoIgnore, True, "战队ID")

JTHeroID = 5 #战队上阵的英雄ID
F(JTHeroID, 0, Enum.DoIgnore, CValue.MAX_INT64, Enum.DoIgnore, True)

JTFightTeamID = 6 #战队每天匹配战斗的第一个队伍ID 有了这个ID，就今天只能加入这个战队
F(JTFightTeamID, 0, Enum.DoIgnore, CValue.MAX_INT64, Enum.DoIgnore, False)
