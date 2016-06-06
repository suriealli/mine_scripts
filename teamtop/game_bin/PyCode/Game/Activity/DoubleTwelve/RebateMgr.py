#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DoubleTwelve.RebateMgr")
#===============================================================================
# 双十二返利领不停
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Activity import CircularDefine
from Game.Activity.DoubleTwelve import DoubleTwelveConfig
from Game.Role import Event
from Game.Role.Data import EnumObj, EnumInt32

if "_HasLoad" not in dir():
	
	IS_START = False		#活动是否开启
	
	#消息
	Rebate_Show_Panel = AutoMessage.AllotMessage("Rebate_Show_Panel", "通知客户端显示返利领不停面板")
	
def ShowRebatePanel(role):
	if not IS_START:
		return
	rebateRewardDict = role.GetObj(EnumObj.DTRebateReward)
	
	role.SendObj(Rebate_Show_Panel, rebateRewardDict)

def RebateGetReward(role, rewardId):
	rebateRewardDict = role.GetObj(EnumObj.DTRebateReward)
	
	rebateConfig = DoubleTwelveConfig.REBATE.get(rewardId)
	if not rebateConfig:
		return
	
	#是否激活了对应奖励
	if rewardId not in rebateRewardDict:
		return
	if rebateRewardDict[rewardId] != 1:
		return
	
	rebateRewardDict[rewardId] = 2
	
	#奖励
	if rebateConfig.rewardMoney:
		role.IncMoney(rebateConfig.rewardMoney)
	if rebateConfig.rewardRMB:
		role.IncBindRMB(rebateConfig.rewardRMB)
	for itemCoding, itemCnt in rebateConfig.rewardItem:
		role.AddItem(itemCoding, itemCnt)
		
	#同步客户端
	ShowRebatePanel(role)
	
def CanActiveRebateReward(role):
	rebateRewardDict = role.GetObj(EnumObj.DTRebateReward)
	rebateDayConsumeUnbindRMB = role.GetDayConsumeUnbindRMB()
	
	for rewardId, config in DoubleTwelveConfig.REBATE.iteritems():
		if rewardId in rebateRewardDict:
			continue
		
		if rebateDayConsumeUnbindRMB < config.targetRMB:
			continue
		
		rebateRewardDict[rewardId] = 1
		
	#同步客户端
	ShowRebatePanel(role)
	
#===============================================================================
# 事件
#===============================================================================
def RebateStart(*param):
	'''
	返利领不停活动开启
	'''
	_, circularType = param
	if circularType != CircularDefine.CA_DTRebate:
		return
	
	global IS_START
	if IS_START is True:
		print "GE_EXC, Rebate is already start"
		return
	
	IS_START = True


def RebateEnd(*param):
	'''
	返利领不停活动关闭
	'''
	_, circularType = param
	if circularType != CircularDefine.CA_DTRebate:
		return
	
	global IS_START
	if IS_START is False:
		print "GE_EXC, Rebate is already end"
		return
	
	IS_START = False
	
def OnSyncRoleOtherData(role, param):
	'''
	角色登陆同步其它数据
	@param role:
	@param param:
	'''
	ShowRebatePanel(role)
	
def AfterChangeUnbindRMB(role, param):
	'''
	神石改变
	@param role:
	@param param:
	'''
	#活动是否开始
	if IS_START is False:
		return
	oldValue, newValue = param
	#充值
	if newValue >= oldValue:
		return
	#能否激活奖励
	CanActiveRebateReward(role)
	
	
def OnRoleDayClear(role, param):
	'''
	每日清理调用
	@param role:
	@param param:
	'''
	#重置奖励
	role.SetObj(EnumObj.DTRebateReward, {})
	#同步客户端
	ShowRebatePanel(role)
	
#===============================================================================
# 客户端请求
#===============================================================================
def RequestRebateOpenPanel(role, msg):
	'''
	返利领不停客户端请求打开面板
	@param role:
	@param msg:
	'''
	ShowRebatePanel(role)
	
def RequestRebateGetReward(role, msg):
	'''
	返利领不停客户端请求领取奖励
	@param role:
	@param msg:
	'''
	rewardId = msg
	
	#活动是否开始
	if IS_START is False:
		return
	
	#日志
	with TraDTRebateReward:
		RebateGetReward(role, rewardId)

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#事件
		Event.RegEvent(Event.Eve_StartCircularActive, RebateStart)
		Event.RegEvent(Event.Eve_EndCircularActive, RebateEnd)
		#角色登陆同步其它数据
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		#改变神石事件
		Event.RegEvent(Event.AfterChangeUnbindRMB_Q, AfterChangeUnbindRMB)
		Event.RegEvent(Event.AfterChangeUnbindRMB_S, AfterChangeUnbindRMB)
		#每日清理调用
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
		
		#日志
		TraDTRebateReward= AutoLog.AutoTransaction("TraDTRebateReward", "双十二返利领不停奖励")
		
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Rebate_Get_Reward", "返利领不停客户端请求领取奖励"), RequestRebateGetReward)
		
		
		