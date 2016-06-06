#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.QingMing.QuanMingLianJin")
#===============================================================================
# 全民齐炼金
#===============================================================================
import cRoleMgr
import Environment
from Game.Role import Event
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Game.Role.Data import EnumDayInt1, EnumCD
from Game.Activity import CircularDefine
from Common.Other import EnumGameConfig, GlobalPrompt


if "_HasLoad" not in dir():
	
	IsStart = False
	TraGetQingMingGoldBuff = AutoLog.AutoTransaction("TraGetQingMingGoldBuff", "清明节活动获取全民炼金buff")


def Start(*param):
	'''
	活动开启
	'''
	_, circularType = param
	if CircularDefine.CA_QingMingQuanMingLianJin != circularType:
		return
	global IsStart
	if IsStart:
		print "GE_EXC,repeat open QingMingQuanMingLianJin"
		return
		
	IsStart = True
	

def End(*param):
	'''
	活动结束
	'''
	_, circularType = param
	if CircularDefine.CA_QingMingQuanMingLianJin != circularType:
		return
	
	# 未开启 
	global IsStart
	if not IsStart:
		print "GE_EXC, end QingMingQuanMingLianJin while not start"
		return
		
	IsStart = False


def RequestGetGoldBuff(role, msg):
	'''
	请求获取全民齐炼金buff
	'''
	if IsStart is False:
		return
	if role.GetLevel() < EnumGameConfig.QingMingLianJinNeedLevel:
		return
	#当天已经领取过
	if role.GetDI1(EnumDayInt1.QingMingQuanMingLianJin):
		return
	
	tips = GlobalPrompt.Reward_Tips
	with TraGetQingMingGoldBuff:
		role.SetDI1(EnumDayInt1.QingMingQuanMingLianJin, 1)
		role.SetCD(EnumCD.QingMingQuanMingLianJin, EnumGameConfig.QingMingLianJinBuffLastTime)
		for item in EnumGameConfig.QingMingLianJinItems:
			role.AddItem(*item)
			tips += GlobalPrompt.Item_Tips % item
		role.IncMoney(EnumGameConfig.QingMingLianJinMoney)
		tips += GlobalPrompt.Money_Tips % EnumGameConfig.QingMingLianJinMoney
	
	role.Msg(2, 0, tips)


def GetGoldBuff(role):
	'''
	获取角色炼金buff百分比值
	'''
	if IsStart is False:
		return 0
	if not role.GetCD(EnumCD.QingMingQuanMingLianJin):
		return 0
	
	return EnumGameConfig.QingMingLianJinBuff


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestGetQingMingGoldBuff", "客户端请求获取清明节全民齐炼金buff"), RequestGetGoldBuff)

		Event.RegEvent(Event.Eve_StartCircularActive, Start)
		Event.RegEvent(Event.Eve_EndCircularActive, End)
