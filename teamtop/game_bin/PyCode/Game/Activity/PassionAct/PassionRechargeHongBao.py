#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionRechargeHongBao")
#===============================================================================
# 充值送红包  @author: Gaoshuai 2015
#===============================================================================
import cRoleMgr
import Environment
from Game.Role.Data import EnumObj
from Game.Role import Event
from Game.Activity import CircularDefine
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from Game.Activity.PassionAct.PassionDefine import  PassionRechargeAndReward
from Game.Activity.PassionAct.PassionRechargeHongBaoConfig import RechargeHongBaoObj
if "_HasLoad" not in dir():
	
	#消息
	RewardCntData = AutoMessage.AllotMessage("RewardCntData", "可领奖次数")
	#日志
	TraRechargeAndReward = AutoLog.AutoTransaction("TraRechargeAndReward", "玩家领取充值领奖奖励 ")
	
	IsStart = False

def StartCircularActive(param1, param2):
	if param2 != CircularDefine.CA_PassionRechargeHongBao:
		return
	global IsStart
	if IsStart:
		print 'GE_EXC, PassionRechargeHongBao is already start'
	IsStart = True


def EndCircularActive(param1, param2):
	if param2 != CircularDefine.CA_PassionRechargeHongBao:
		return
	global IsStart
	if not IsStart:
		print 'GE_EXC, PassionRechargeHongBao is already end'
	IsStart = False


def RequestRechargeHongBao(role, msg):
	'''
	请求领取充值领奖奖励
	@param role:
	@param msg: None
	'''
	global IsStart
	if not IsStart:return
	if role.GetLevel() < EnumGameConfig.Level_30:
		return
	
	PassionData = role.GetObj(EnumObj.PassionActData)
	cnt = (role.GetDayBuyUnbindRMB_Q() - PassionData.get(PassionRechargeAndReward, 0)) / RechargeHongBaoObj.rechargeRMB
	if cnt <= 0:
		return
	with TraRechargeAndReward:
		PassionData[PassionRechargeAndReward] = PassionData.get(PassionRechargeAndReward, 0) + RechargeHongBaoObj.rechargeRMB
		for item in RechargeHongBaoObj.items:
			role.AddItem(*item)
	
	role.SendObj(RewardCntData, cnt - 1);
	tips = ''.join(GlobalPrompt.Item_Tips % item for item in RechargeHongBaoObj.items)
	role.Msg(2, 0, GlobalPrompt.Reward_Tips + tips)


def AfterChangeUnbindRMB_Q(role, param):
	'''
	@param role:
	@param msg: None
	'''
	global IsStart
	if not IsStart:return
	if role.GetLevel() < EnumGameConfig.Level_30:
		return
	cnt = (role.GetDayBuyUnbindRMB_Q() - role.GetObj(EnumObj.PassionActData).get(PassionRechargeAndReward, 0)) / RechargeHongBaoObj.rechargeRMB
	if cnt <= 0:
		return
		
	role.SendObj(RewardCntData, cnt)


def RoleDayClear(role, param):
	global IsStart
	if not IsStart:return
	
	role.GetObj(EnumObj.PassionActData)[PassionRechargeAndReward] = 0
	role.SendObj(RewardCntData, 0)


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, StartCircularActive)
		Event.RegEvent(Event.Eve_EndCircularActive, EndCircularActive)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, AfterChangeUnbindRMB_Q)
		Event.RegEvent(Event.Eve_AfterChangeDayBuyUnbindRMB_Q, AfterChangeUnbindRMB_Q)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestRechargeHongBao", "请求领取充值领奖奖励"), RequestRechargeHongBao)
