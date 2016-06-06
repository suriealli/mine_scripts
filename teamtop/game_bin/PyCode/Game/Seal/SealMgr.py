#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Seal.SealMgr")
#===============================================================================
# 圣印系统
#===============================================================================
import cRoleMgr
import Environment
from ComplexServer.Log import AutoLog
from Game.Seal import SealConfig
from Game.Role.Data import EnumObj, EnumInt32
from Common.Other import EnumGameConfig
from Common.Message import AutoMessage
from Game.Role import Event
from Common.Other import GlobalPrompt
if "_HasLoad" not in dir():
	#消息
	SealActivation = AutoMessage.AllotMessage("SealActivation", "已经激活的圣印")
	#日志
	Tra_SealUpGrade = AutoLog.AutoTransaction("Tra_SealUpGrade", "圣印系统_圣印升级日志")
	Tra_SealActivate = AutoLog.AutoTransaction("Tra_SealActivate", "圣印系统_圣印激活日志")
	
def SealActivate(role, SealId):
	'''
	激活圣印
	SealData{type:sealid}
	'''
	#低于等级
	if role.GetLevel() < EnumGameConfig.SealMinLevel :
		return
	SealMgr = SealConfig.Seal_BaseConfig_Dict.get(SealId)
	#没有该圣印
	if not SealMgr :
		print "GE_EXC, repeat no SealId %s in SealActivate " % SealId
		return
	#检测是否为激活的圣印
	if not SealMgr.needSealAmounts :
		print "GE_EXC, repeat  SealId %s is not a Action Seal in SealActivate " % SealId
		return
	NowSealType = SealMgr.SealType
	SealData = role.GetObj(EnumObj.SealData)
	#前序圣印没有开启
	if NowSealType != 1 and NowSealType - 1 not in SealData :
		role.Msg(2, 0, GlobalPrompt.NotActiveSeal)
		return
	#圣印已经激活
	if NowSealType in SealData :
		return
	NeedSealAmount = SealMgr.needSealAmounts
	#圣印纹章不足
	if role.GetI32(EnumInt32.SealAmounts) < NeedSealAmount :
		return
	with Tra_SealActivate :
		role.DecI32(EnumInt32.SealAmounts, NeedSealAmount)
		SealData[NowSealType] = SealId
		#处理属性升级
		role.ResetSealProperty()
	#同步客户端消息	
	role.SendObj(SealActivation, SealData)
	role.Msg(2, 0, GlobalPrompt.ActiveSealSuccess)

def UpGradeSealStar(role, SealId):
	'''
	升级圣印
	'''
	#低于等级
	if role.GetLevel() < EnumGameConfig.SealMinLevel :
		return
	SealMgr = SealConfig.Seal_BaseConfig_Dict.get(SealId)
	#没有该圣印
	if not SealMgr :
		return
	#检测是否升级圣印
	if not SealMgr.needLiLianAmount :
		return
	NowSealType = SealMgr.SealType
	SealData = role.GetObj(EnumObj.SealData)
	#圣印没有激活
	if NowSealType not in SealData :
		print "GE_EXC, repeat no SealType %s in UpGradeSealStar " % NowSealType
		return
	#最后的圣印等级
	LastSealLevel = SealConfig.Seal_BaseConfig_Dict.get(SealData[NowSealType])
	if not LastSealLevel :
		print "GE_EXC, repeat no SealId %s in Seal_BaseConfig_Dict" % SealData[NowSealType]
		return
	#已经是最高级
	if not LastSealLevel.nextSSId :
		role.Msg(2, 0, GlobalPrompt.MaxSealLevel)
		return
	if LastSealLevel.nextSSId != SealId :
		return 
	NeedLiNian = SealMgr.needLiLianAmount
	#历练值不足
	if NeedLiNian > role.GetI32(EnumInt32.SealLiLianAmounts) :
		role.Msg(2, 0, GlobalPrompt.NotEnoughLiLianAmout)
		return
	with Tra_SealUpGrade :
		role.DecI32(EnumInt32.SealLiLianAmounts, NeedLiNian)
		SealData[NowSealType] = LastSealLevel.nextSSId
		role.ResetSealProperty()
	role.SendObj(SealActivation, SealData)


def SyncRoleOtherData(role, param):
	'''
	登陆后同步圣印信息给客户端
	'''
	SealData = role.GetObj(EnumObj.SealData)
	role.SendObj(SealActivation, SealData)



if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross and not Environment.EnvIsTK():
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("SealMgr_SealActivate", "圣印系统_请求激活圣印"), SealActivate)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("SealMgr_UpGradeSealStar", "圣印系统_请求升级圣印"), UpGradeSealStar)
