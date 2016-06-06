#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ZhongQiu.ZhongQiuLianJin")
#===============================================================================
# 活动炼金BUFF (中秋)
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Activity import CircularDefine
from Game.Role.Data import EnumDayInt1, EnumCD


if "_HasLoad" not in dir():
	
	IS_START = False
	
	Tra_GetZhongQiuGoldBuff = AutoLog.AutoTransaction("Tra_GetZhongQiuGoldBuff", "中秋全民炼金_获取炼金buff")


#===============================================================================
# 活动控制
#===============================================================================
def OnStartZhongQiuLianJin(*param):
	'''
	活动开启
	'''
	_, circularType = param
	if CircularDefine.CA_ZhongQiuLianJin != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open ZhongQiuLianJin"
		return
		
	IS_START = True
	

def OnEndZhongQiuLianJin(*param):
	'''
	活动结束
	'''
	_, circularType = param
	if CircularDefine.CA_ZhongQiuLianJin != circularType:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC, end ZhongQiuLianJin while not start"
		return
		
	IS_START = False


#===============================================================================
# 客户端请求
#===============================================================================
def OnGetZhongQiuGoldBuff(role, msg = None):
	'''
	中秋全民齐炼金_请求获取buff
	'''
	if IS_START is False:
		return
	
	if role.GetLevel() < EnumGameConfig.ZhongQiuLianJin_NeedLevel:
		return
	
	#当天已经领取过
	if role.GetDI1(EnumDayInt1.ZhongQiuLianJin_IsReward):
		return
	
	with Tra_GetZhongQiuGoldBuff:
		#领取标志
		role.SetDI1(EnumDayInt1.ZhongQiuLianJin_IsReward, 1)
		#buff 持续时间
		role.SetCD(EnumCD.ZhongQiuLianJinCD, EnumGameConfig.ZhongQiuLianJinBuff_LastTime)
	

#===============================================================================
# 辅助
#===============================================================================
def GetGoldBuff(role):
	'''
	获取角色炼金buff百分比值
	'''
	if IS_START is False:
		return 0
	
	if not role.GetCD(EnumCD.ZhongQiuLianJinCD):
		return 0
	
	return EnumGameConfig.ZhongQiuLianJin_Buff


#===============================================================================
# 事件
#===============================================================================
def OnRoleDayClear(role, param = None):
	'''
	跨天重置炼金BUFF
	'''
	#不管现在活动是否开启 都要重置 因为有可能活动结束前最后领取buff
	role.SetCD(EnumCD.ZhongQiuLianJinCD, 0)
	

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ZhongQiu_OnGetZhongQiuGoldBuff", "中秋全民齐炼金_请求获取buff"), OnGetZhongQiuGoldBuff)
		
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
		
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartZhongQiuLianJin)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndZhongQiuLianJin)
