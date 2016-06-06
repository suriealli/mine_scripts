#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.HeavenUnRMB.HeavenUnRMB")
#===============================================================================
# 天降神石
#===============================================================================
import random
import Environment
import cRoleMgr
import cDateTime
import cComplexServer
from ComplexServer.Log import AutoLog
from Util import Time
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumSysData
from Game.SysData import WorldData
from Game.Role import Call, Event
from Game.Role.Data import EnumInt8
from Game.Activity.HeavenUnRMB import HeavenUnRMBConfig

if "_HasLoad" not in dir():
	CallBackSec = 60
	
	EXTEND_CNT_DICT = {}	#每档每日能领取的上限
	EXTEND_DATA_INFO = []	#信息
	#消息
	HeavenUnRMB_CallBack_For_client = AutoMessage.AllotMessage("HeavenUnRMB_CallBack_For_client", "天降神石回调")
	HeavenUnRMB_Extend_Data = AutoMessage.AllotMessage("HeavenUnRMB_Extend_Data", "同步获得额外神石记录")
	#日志
	HeavenUnRMBReward = AutoLog.AutoTransaction("HeavenUnRMBReward", "天降神石奖励")
	HeavenUnRMBCost = AutoLog.AutoTransaction("HeavenUnRMBCost", "天降神石消耗")

def CheckState():
	'''
	检测活动是否开启
	'''
	if Environment.EnvIsYY():
		return True
	kaifu_time = WorldData.WD.get(EnumSysData.KaiFuKey)
	unit_time = Time.DateTime2UnitTime(kaifu_time)
	if kaifu_time.hour or kaifu_time.minute or kaifu_time.second:
		unit_time -= kaifu_time.hour * 3600 + kaifu_time.minute * 60 + kaifu_time.second
	start_time = unit_time + (2 * 3600 * 24)
	if cDateTime.Seconds() >= start_time:
		return True
	return False

def RequestOpenPanel(role, param):
	'''
	客户端请求打开天降神石
	@param role:
	@param param:
	'''
	if not Environment.EnvIsQQ() or not Environment.IsDevelop:
		global EXTEND_DATA_INFO
		role.SendObj(HeavenUnRMB_Extend_Data, EXTEND_DATA_INFO)
	
def RequestDraw(role, param):
	'''
	客户端请求摇奖
	@param role:
	@param param:
	'''
	index = param
	state = CheckState()
	if not state:
		return
	#获取玩家当前可以
	roleIndex = role.GetI8(EnumInt8.HeavenUnRMBIndex2)
	if roleIndex != index:
		return
	HeavenBase = HeavenUnRMBConfig.HEAVEN_BASE_DICT.get(index)
	if not HeavenBase:
		print "GE_EXC, can not find index(%s) in RequestDraw" % index
		return
	cfg, RANDOM = HeavenBase
	if not cfg.InputRMB:
		print "GE_EXC, HeavenUnRMB InputRMB is Wrong,index=(%s)" % index
		return
	if role.GetUnbindRMB_Q() < cfg.InputRMB:
		return
	IncRMB = 0
	#额外的神石
	IS_EXTEND = False
	if Environment.EnvIsQQ() or Environment.IsDevelop:
		if not cfg.ReturnRMB_QQ:
			return
		IncRMB = cfg.ReturnRMB_QQ
	else:
		MinRMB, MaxRMB = RANDOM.RandomOne()
		IncRMB = random.randint(MinRMB, MaxRMB)
		if not IncRMB:
			print "GE_EXC,HeavenUnRMB random no value, index=(%s)" % index 
			return
	
		if cfg.ExtendReturnRMB:
			global EXTEND_CNT_DICT
			global EXTEND_DATA_INFO
			nowCnt = EXTEND_CNT_DICT.get(index, 0)
			if nowCnt < cfg.ExtendReturnCnt:
				randomNum = random.randint(1, 10000)
				if randomNum <= cfg.ExtendReturnPro:
					IS_EXTEND = True
					EXTEND_CNT_DICT[index] = EXTEND_CNT_DICT.get(index, 0) + 1
					if len(EXTEND_DATA_INFO) < 10:
						EXTEND_DATA_INFO.append([role.GetRoleName(), cfg.InputRMB, IncRMB, cfg.ExtendReturnRMB])
					else:
						EXTEND_DATA_INFO.pop(0)
						EXTEND_DATA_INFO.append([role.GetRoleName(), cfg.InputRMB, IncRMB, cfg.ExtendReturnRMB])
	with HeavenUnRMBCost:
		role.IncI8(EnumInt8.HeavenUnRMBIndex2, 1)
		role.DecUnbindRMB_Q(cfg.InputRMB)
	roleId = role.GetRoleID()
	if IS_EXTEND:
		role.SendObjAndBack(HeavenUnRMB_CallBack_For_client, IncRMB, CallBackSec, CallBackPayReward, (roleId, IncRMB,cfg.InputRMB,cfg.ExtendReturnRMB))
	else:
		role.SendObjAndBack(HeavenUnRMB_CallBack_For_client, IncRMB, CallBackSec, CallBackPayReward, (roleId, IncRMB,cfg.InputRMB,0))

def CallBackPayReward(role, callargv, regparam):
	roleId, InputRMB, IncRMB, extendRMB = regparam
	Call.LocalDBCall(roleId, SendReward, (InputRMB, IncRMB, extendRMB))

def SendReward(role, regparam):
	IncRMB, InputRMB, extendRMB = regparam
	with HeavenUnRMBReward:
		if IncRMB:
			role.IncUnbindRMB_S(IncRMB)
		if extendRMB:
			role.IncUnbindRMB_S(extendRMB)
	if extendRMB:
		cRoleMgr.Msg(1, 0, GlobalPrompt.HeavenUpRMB_MSG2 % (role.GetRoleName(), InputRMB, IncRMB, extendRMB))
	else:
		cRoleMgr.Msg(1, 0, GlobalPrompt.HeavenUpRMB_MSG % (role.GetRoleName(), InputRMB, IncRMB))
	
	if not Environment.EnvIsQQ() or not Environment.IsDevelop:
		global EXTEND_DATA_INFO
		role.SendObj(HeavenUnRMB_Extend_Data, EXTEND_DATA_INFO)

def AfterLogin(role, param):
	if not role.GetI8(EnumInt8.HeavenUnRMBIndex2):
		role.SetI8(EnumInt8.HeavenUnRMBIndex2, 1)
		
def CallAfterNewDay():
	global EXTEND_CNT_DICT
	EXTEND_CNT_DICT = {}



def GMHeavenUnRMB(role):
	#GM指令发奖励
	if Environment.IsCross:
		print "GE_EXC, GMHeavenUnRMB error GM tool roleId(%s)"  % role.GetRoleID()
		return
	state = CheckState()
	if not state:
		return
	#获取玩家当前可以
	index = role.GetI8(EnumInt8.HeavenUnRMBIndex2)
	HeavenBase = HeavenUnRMBConfig.HEAVEN_BASE_DICT.get(index)
	if not HeavenBase:
		print "GE_EXC, can not find index(%s) in RequestDraw By GM tool roleId(%s)" % (index, role.GetRoleID())
		return
	cfg, RANDOM = HeavenBase
	if not cfg.InputRMB:
		print "GE_EXC, HeavenUnRMB InputRMB is Wrong,index=(%s) GM tool roleId(%s)" % (index, role.GetRoleID())
		return
	if role.GetUnbindRMB_S() < cfg.InputRMB:
		return
	MinRMB, MaxRMB = RANDOM.RandomOne()
	IncRMB = random.randint(MinRMB, MaxRMB)
	if not IncRMB:
		print "GE_EXC,HeavenUnRMB random no value, index=(%s) GM tool roleId(%s)" % (index, role.GetRoleID()) 
		return
	#额外的神石
	IS_EXTEND = False
	if cfg.ExtendReturnRMB:
		global EXTEND_CNT_DICT
		global EXTEND_DATA_INFO
		nowCnt = EXTEND_CNT_DICT.get(index, 0)
		if nowCnt < cfg.ExtendReturnCnt:
			randomNum = random.randint(1, 10000)
			if randomNum <= cfg.ExtendReturnPro:
				IS_EXTEND = True
				EXTEND_CNT_DICT[index] = EXTEND_CNT_DICT.get(index, 0) + 1
				if len(EXTEND_DATA_INFO) < 10:
					EXTEND_DATA_INFO.append([role.GetRoleName(), cfg.InputRMB, IncRMB, cfg.ExtendReturnRMB])
				else:
					EXTEND_DATA_INFO.pop(0)
					EXTEND_DATA_INFO.append([role.GetRoleName(), cfg.InputRMB, IncRMB, cfg.ExtendReturnRMB])
				
	with AutoLog.AutoTransaction(AutoLog.traRoleGM):
		role.IncI8(EnumInt8.HeavenUnRMBIndex2, 1)
		role.DecUnbindRMB_S(cfg.InputRMB)
	#roleId = role.GetRoleID()
	if IS_EXTEND:
		SendReward(role, (IncRMB, cfg.InputRMB, cfg.ExtendReturnRMB))
	else:
		SendReward(role, (IncRMB, cfg.InputRMB, 0))
		

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		#事件
		Event.RegEvent(Event.Eve_AfterLoginJoinScene, AfterLogin)
		cComplexServer.RegAfterNewDayCallFunction(CallAfterNewDay)
		
	if Environment.HasLogic and not Environment.IsCross:
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_request_Draw", "客户端请求摇奖"), RequestDraw)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_request_OpenPanel", "客户端请求打开天降神石"), RequestOpenPanel)
	