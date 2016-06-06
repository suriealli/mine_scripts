#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionDaiBi")
#===============================================================================
# 充值送代币活动 @author GaoShuai 2016.2.29
#===============================================================================
import cRoleMgr
import Environment
from Game.Role import Event
from Game.Activity import CircularDefine
from Common.Message import AutoMessage
from Common.Other import  GlobalPrompt, EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumObj
from Game.Activity.PassionAct import PassionDefine

if "_HasLoad" not in dir():
	
	#公会红包消息
	PassionDaiBiData = AutoMessage.AllotMessage("PassionDaiBiData", "同步代币领取数据")
	
	#充值送代币领奖日志
	Tra_DaiBiGetReward = AutoLog.AutoTransaction("Tra_DaiBiGetReward", "充值送代币领取奖励 ")
	
	IsStart = False


def StartDaiBi(param1, param2):
	#开启充值送代币
	if param2 != CircularDefine.CA_PassionDaiBi:
		return
	
	global IsStart
	if IsStart:
		print 'GE_EXC, PassionDaiBi is already start'
	IsStart = True


def EndDaiBi(param1, param2):
	#关闭充值送代币
	if param2 != CircularDefine.CA_PassionDaiBi:
		return
	
	global IsStart
	if not IsStart:
		print 'GE_EXC, PassionDaiBi is already end'
	IsStart = False


def RequestGetDaiBi(role, param):
	'''
	请求领取充值满额奖励
	@param role:
	@param param:
	'''
	global IsStart
	if not IsStart:
		return
	#等级限制
	if role.GetLevel() < EnumGameConfig.DaiBiRoleLevel:
		return
	
	PassionDaiBiDict = role.GetObj(EnumObj.PassionActData).get(PassionDefine.PassionDaiBi)
	if role.GetDayBuyUnbindRMB_Q() < EnumGameConfig.DaiBiRechargeMoney_1:
		return
	
	if PassionDaiBiDict.get(1):
		return
	coding, cnt = EnumGameConfig.DaiBiReward
	with Tra_DaiBiGetReward:
		role.AddItem(coding, cnt)
		PassionDaiBiDict[1] = 1
	
	role.SendObj(PassionDaiBiData, (1, PassionDaiBiDict.get(2, 0)))
	role.Msg(2, 0, GlobalPrompt.Reward_Tips + GlobalPrompt.Item_Tips % (coding, cnt))


def RequestReGetDaiBi(role, param):
	'''
	请求领取充值满额重复奖励
	@param role:
	@param param:
	'''
	global IsStart
	if not IsStart:
		return
	#等级限制
	if role.GetLevel() < EnumGameConfig.DaiBiRoleLevel:
		return 
	PassionDaiBiDict = role.GetObj(EnumObj.PassionActData).get(PassionDefine.PassionDaiBi)
	maxCnt = role.GetDayBuyUnbindRMB_Q()/ EnumGameConfig.DaiBiRechargeMoney_2
	if PassionDaiBiDict[2] >= maxCnt:
		return
	#重复奖励做多领取100次
	if PassionDaiBiDict[2] >= EnumGameConfig.DaiBiRewardMaxTimes:
		return
	coding, cnt = EnumGameConfig.DaiBiReReward
	with Tra_DaiBiGetReward:
		PassionDaiBiDict[2] += 1
		role.AddItem(coding, cnt)
		role.IncUnbindRMB_S(EnumGameConfig.DaiBiReRewardRMB)
	
	role.SendObj(PassionDaiBiData, (PassionDaiBiDict.get(1, 0), PassionDaiBiDict.get(2, 0)))
	role.Msg(2, 0, GlobalPrompt.Reward_Tips + GlobalPrompt.Item_Tips % (coding, cnt) + GlobalPrompt.RMB_Tips % EnumGameConfig.DaiBiReRewardRMB)

def DaiBiDayClear(role, param):
	'''
	每日清理
	@param role:
	@param param:
	'''
	role.GetObj(EnumObj.PassionActData)[PassionDefine.PassionDaiBi] = {1:0, 2:0}
	
	
def DaiBiLoginIn(role, param):
	#初始化代币数据
	PassionObj = role.GetObj(EnumObj.PassionActData)
	if PassionDefine.PassionDaiBi not in PassionObj:
		PassionObj[PassionDefine.PassionDaiBi] = {1:0, 2:0}


def SyncDaiBiData(role, param):
	#玩家刷新，同步数据
	global IsStart
	if not IsStart:
		return
	PassionDaiBiDict = role.GetObj(EnumObj.PassionActData).get(PassionDefine.PassionDaiBi)
	role.SendObj(PassionDaiBiData, (PassionDaiBiDict.get(1, 0), PassionDaiBiDict.get(2, 0)))

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncDaiBiData)
		Event.RegEvent(Event.Eve_AfterLogin, DaiBiLoginIn)
		Event.RegEvent(Event.Eve_RoleDayClear, DaiBiDayClear)
		
		Event.RegEvent(Event.Eve_StartCircularActive, StartDaiBi)
		Event.RegEvent(Event.Eve_EndCircularActive, EndDaiBi)
		#角色登陆同步其它数据
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestGetDaiBi", "请求领取奖励"), RequestGetDaiBi)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestReGetDaiBi", "请求领取重复奖励"), RequestReGetDaiBi)
