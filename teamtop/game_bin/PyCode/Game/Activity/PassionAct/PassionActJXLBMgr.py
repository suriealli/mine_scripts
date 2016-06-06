#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionActJXLBMgr")
#===============================================================================
# 惊喜礼包管理器
#===============================================================================
import Environment
import cRoleMgr
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Common.Other import GlobalPrompt,EnumGameConfig
from Game.Role import Event
from Game.Role.Data import EnumObj
from Game.Activity import CircularDefine
from Game.Activity.PassionAct.PassionDefine import PassionJXLB
from Game.Activity.PassionAct.PassionActJXLBConfig import JXLB_Dict


if "_HasLoad" not in dir():

	IsOpen = False

	JXLBOpenLimit = 10	#礼包每日限购次数
	#日志
	PassionJXLBOpen = AutoLog.AutoTransaction("PassionJXLBOpen", "开启惊喜礼包")
	#消息
	PassionJXLBData = AutoMessage.AllotMessage("PassionJXLBData", "惊喜礼包购买数据")		#{物品索引:已购买数量}

def StartActivity(param1, param2):
	if param2 != CircularDefine.CA_PassionJXLB:
		return
	
	global IsOpen
	if IsOpen:
		print "GE_EXC, PassionJXLB is already open"
		return
	
	IsOpen = True

def EndActivity(param1, param2):
	if param2 != CircularDefine.CA_PassionJXLB:
		return
	
	global IsOpen
	if not IsOpen:
		print "GE_EXC, PassionJXLB is already close"
		return
	
	IsOpen = False

def SysncRoleData(role):
	global IsOpen
	if not IsOpen: return

	jxlb_dict = role.GetObj(EnumObj.PassionActData)[PassionJXLB]
	role.SendObj(PassionJXLBData,jxlb_dict)
	
def OpenPane(role,msg):
	'''
	请求打开面板
	'''
	global IsOpen
	if not IsOpen: return

	SysncRoleData(role)

def TriggerextReward():
	'''
	发送至尊奖励
	'''
	pass

def OpenPackage(role,msg):
	'''
	请求开启礼包
	'''
	global IsOpen
	if not IsOpen: return

	if role.GetLevel() < EnumGameConfig.NewYearDayMinLevel:
		return

	#参数合法性检测
	if not msg: return
	index = msg

	#限购检测
	jxlb_dict = role.GetObj(EnumObj.PassionActData)[PassionJXLB]
	jxlb_open_times = jxlb_dict.get(index,0)
	if jxlb_open_times >= JXLBOpenLimit:
		return

	#神石检测
	jxlb_cfg = JXLB_Dict.get(index,None)
	if not jxlb_cfg:
		return
	needRMB = jxlb_cfg.needRMB[jxlb_open_times]

	if role.GetUnbindRMB() < needRMB:
		return

	#随机奖励
	item = jxlb_cfg.RandomRate.RandomOne()
	#触发至尊奖励
	is_ext_item = False
	if jxlb_open_times + 1 >= JXLBOpenLimit:
		is_ext_item = True

	tips = GlobalPrompt.Reward_Tips
	with PassionJXLBOpen:
		role.DecUnbindRMB(needRMB)
		jxlb_dict[index] = jxlb_dict.get(index,0) + 1
		#发放奖励道具
		if is_ext_item:
			role.AddItem(*jxlb_cfg.extReward)
			tips += GlobalPrompt.Item_Tips % jxlb_cfg.extReward
		else:
			role.AddItem(*item)
			tips += GlobalPrompt.Item_Tips % item
	
	SysncRoleData(role)
	role.Msg(2, 0, tips)

def OnRoleInit(role,param):
	'''
	角色初始化
	'''
	if PassionJXLB not in role.GetObj(EnumObj.PassionActData):
		role.GetObj(EnumObj.PassionActData)[PassionJXLB] = {}

def RoleDayClear(role, param):
	global IsOpen
	if not IsOpen: return

	jxlb_dict = role.GetObj(EnumObj.PassionActData)[PassionJXLB]
	jxlb_dict.clear()

	SysncRoleData(role)

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_StartCircularActive, StartActivity)
		Event.RegEvent(Event.Eve_EndCircularActive, EndActivity)
		Event.RegEvent(Event.Eve_InitRolePyObj, OnRoleInit)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("PassionActJXLB_RequestOpenPackage","请求开启礼包"), OpenPackage)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("PassionActJXLB_RequestOpenPane", "请求打开惊喜礼包面板"), OpenPane)