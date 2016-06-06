#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.FiveOneDay.FiveOneLoginReward")
#===============================================================================
# 五一登录奖励
#===============================================================================
import Environment
import cRoleMgr
from Game.Role import Event
from Game.Activity import CircularDefine
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Role.Data import EnumDayInt1
from Game.Activity.FiveOneDay import FiveOneDayConfig

if "_HasLoad" not in dir():
	IS_START = False	#活动开启标志
	
	FiveOneLoginReward = AutoLog.AutoTransaction("FiveOneLoginReward", "五一活动登录奖励")
	
#======活动开关控制=======
def StartLoginReward(*param):
	#开启五一登录奖励活动
	_, circularType = param
	if circularType != CircularDefine.CA_FiveOneLogin:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open FiveOneLoginReward Act"
		return
	
	IS_START = True
	
def CloseLoginReward(*param):
	#关闭五一登录奖励活动
	_, circularType = param
	if circularType != CircularDefine.CA_FiveOneLogin:
		return
	
	global IS_START
	if not IS_START:
		print "GE_EXC, FiveOneLoginReward is already close"
		return
	
	IS_START = False
	
def RequestGetLoginReward(role, param):
	'''
	客户端请求领取五一登录奖励
	@param role:
	@param param:
	'''
	global IS_START
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.FIVE_ONE_NEED_LEVEL:
		return
	
	if role.GetDI1(EnumDayInt1.FiveOneLoginState):#已领取
		return
	
	with FiveOneLoginReward:
		role.SetDI1(EnumDayInt1.FiveOneLoginState, 1)
		
		cfg = FiveOneDayConfig.FIVEONE_LOGIN_REWARD
		tips =  ""
		if cfg.itemRewards:
			for coding, cnt in cfg.itemRewards:
				role.AddItem(coding, cnt)
				tips += GlobalPrompt.Item_Tips % (coding, cnt)
		role.Msg(2, 0, tips)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, StartLoginReward)
		Event.RegEvent(Event.Eve_EndCircularActive, CloseLoginReward)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("FiveOne_Get_LogionReward", "客户端请求领取五一登录奖励"), RequestGetLoginReward)
		