#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionSignInAwardMgr")
#===============================================================================
# 感恩节签到奖励
#===============================================================================
import Environment
import cDateTime
import cRoleMgr
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Activity import CircularDefine
from Common.Other import GlobalPrompt
from Game.Role.Data import EnumDayInt8
from Game.Activity.PassionAct import PassionSignInConfig
from Game.Role import Event
from Common.Other import EnumGameConfig 

if "_HasLoad" not in dir() :
	IS_START = False			#感恩节签到活动开始控制
	#日志
	SignIn_Award_Log = AutoLog.AutoTransaction("SignIn_Award_Log", "签到奖励")
	#消息
	SignInState = AutoMessage.AllotMessage("SignInState", "签到状态")
	


def StartThanksSignIn(*param):
	'''
	签到任务开启
	'''
	global IS_START
	_, circularType = param
	if circularType != CircularDefine.CA_PassionSignInAward :
		return
	if IS_START :
		print "GE_EXC,repeat open StartThanksSignIn"
		return
	IS_START = True


def CloseThanksSignIn(*param):
	'''
	签到任务结束
	'''
	global IS_START
	_, circularType = param
	if circularType != CircularDefine.CA_PassionSignInAward :
		return
	if not IS_START :
		print "GE_EXC,repeat open CloseThanksSignIn"
		return
	IS_START = False
	

def SignInAward(role,msg = None):
	'''
	领取奖励
	'''
	global IS_START
	if not IS_START :
		return
	Level = role.GetLevel()
	if Level < EnumGameConfig.Level_30 :
		return
	signstate = role.GetDI8(EnumDayInt8.ThanksSignIn)
	time = cDateTime.Hour()
	index = 0
	count = 0
	for awardid, cfg in PassionSignInConfig.SIGN_IN_AWARD.iteritems() :
		if cfg.SignInTime <= time :
			continue
		count = 2**(awardid-1)
		if signstate >= count :
			return
		items = cfg.rewardItem
		index = awardid
		break
	if index == 0 :
		return
	if index == 3 :
		index = 4
	with SignIn_Award_Log :
		index += signstate			#以二进制形式表示领取状态，如第一时间段加上第二时间段的话就是3
		role.SetDI8(EnumDayInt8.ThanksSignIn, index)
		tips = ""
		tips += GlobalPrompt.Reward_Tips
		for cfg in items :
			role.AddItem(cfg[0],cfg[1])
			tips += GlobalPrompt.Item_Tips % (cfg[0],cfg[1])
		role.Msg(2, 0, tips)
			
def LoadSignIn(role,msg = None):
	global IS_START
	if not IS_START :
		return
	Level = role.GetLevel()
	if Level < EnumGameConfig.Level_30 :
		return
	signstate = role.GetDI8(EnumDayInt8.ThanksSignIn)
	role.SendObj(SignInState, signstate)


if "_HasLoad" not in dir() :
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, StartThanksSignIn)
		Event.RegEvent(Event.Eve_EndCircularActive, CloseThanksSignIn)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("SignInAward", "客户端请求领取奖励"), SignInAward)