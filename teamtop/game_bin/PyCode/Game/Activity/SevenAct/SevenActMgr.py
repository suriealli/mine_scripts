#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.SevenAct.SevenActMgr")
#===============================================================================
# 七日活动
#===============================================================================
import cRoleMgr
import cComplexServer
import Environment
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Activity.SevenAct import SevenActBase, SevenActConfig
from Game.Role import Event
from Game.Role.Data import EnumTempObj


if "_HasLoad" not in dir():
	SEVEN_ACT_NEED_LEVEL = 20		#七日活动需要的等级
	
	#消息
	Seven_Act_Sync_All = AutoMessage.AllotMessage("Seven_Act_Sync_All", "通知客户端同步开服活动所有数据")

def SevenActOpenMainPanel(role):
	sevenActMgr = role.GetTempObj(EnumTempObj.SevenActMgr)
	
	#奖励状态字典，累计充值神石，坐骑培养次数，累计登录次数，公会副本次数，竞技场挑战次数
	role.SendObj(Seven_Act_Sync_All, (sevenActMgr.reward_status_dict, sevenActMgr.buy_unbind_rmb, sevenActMgr.mount_train_cnt, 
									sevenActMgr.login_cnt, sevenActMgr.union_fb_cnt, sevenActMgr.jjc_cnt, sevenActMgr.online_time))
	
def SevenActGetReward(role, actId, idx, backFunId):
	sevenActMgr = role.GetTempObj(EnumTempObj.SevenActMgr)
	
	rewardConfig = SevenActConfig.SEVEN_ACT_REWARD.get((actId, idx))
	if not rewardConfig:
		return
	
	if actId not in sevenActMgr.reward_status_dict:
		return
	rewardStatusDict = sevenActMgr.reward_status_dict[actId]
	if idx not in rewardStatusDict:
		return
	
	#是否可以领取
	if rewardStatusDict[idx] != 1:
		return
	
	rewardStatusDict[idx] = 2
	
	rewardPrompt = ""
	#奖励
	if rewardConfig.rewardMoney:
		role.IncMoney(rewardConfig.rewardMoney)
		rewardPrompt += GlobalPrompt.Money_Tips % rewardConfig.rewardMoney
	if rewardConfig.rewardRMB:
		role.IncBindRMB(rewardConfig.rewardRMB)
		rewardPrompt += GlobalPrompt.BindRMB_Tips % rewardConfig.rewardRMB
	if rewardConfig.rewardItem:
		for coding, cnt in rewardConfig.rewardItem:
			role.AddItem(coding, cnt)
			rewardPrompt += GlobalPrompt.Item_Tips % (coding, cnt)
			
	#回调客户端
	role.CallBackFunction(backFunId, (actId, idx))
	
	#提示
	role.Msg(2, 0, rewardPrompt)

#===============================================================================
# 事件
#===============================================================================
def OnRoleInit(role, param):
	'''
	角色初始化
	@param role:
	@param param:
	'''
	if not role.GetTempObj(EnumTempObj.SevenActMgr):
		role.SetTempObj(EnumTempObj.SevenActMgr, SevenActBase.SevenActMgr(role))

def OnSyncRoleOtherData(role, param):
	'''
	角色登陆同步其它数据
	@param role:
	@param param:
	'''
	#版本判断
	if not Environment.EnvIsRU():
		return
	
	sevenActMgr = role.GetTempObj(EnumTempObj.SevenActMgr)
	if not sevenActMgr:
		role.SetTempObj(EnumTempObj.SevenActMgr, SevenActBase.SevenActMgr(role))
		sevenActMgr = role.GetTempObj(EnumTempObj.SevenActMgr)
	
	sevenActMgr.UpdateVersion()
	#累计登录
	sevenActMgr.login()


def OnRoleLogin(role, param):
	'''
	角色登陆
	@param role:
	@param param:
	'''
	sevenActMgr = role.GetTempObj(EnumTempObj.SevenActMgr)
	#判断是否在线奖励活动
	if sevenActMgr.is_active():
		sevenActMgr.online_reward_tick_id = role.RegTick(60, OnlineReward)


def OnChangeUnbindRMB_Q(role, param):
	'''
	神石改变
	@param role:
	@param param:
	'''
	oldValue, newValue = param
	
	if newValue > oldValue:
		#充值
		
		#增加的充值
		incRMB = newValue - oldValue
		
		#版本判断
		if Environment.EnvIsRU():
			#七日活动
			sevenActMgr = role.GetTempObj(EnumTempObj.SevenActMgr)
			#增加今日充值神石数量
			sevenActMgr.inc_buy_unbind_rmb(incRMB)
			#首充
			sevenActMgr.first_pay()
	else:
		#消费
		#版本判断
		if Environment.EnvIsRU():
			#七日活动
			sevenActMgr = role.GetTempObj(EnumTempObj.SevenActMgr)
			#首充
			sevenActMgr.day_first_consume()
		
def OnChangeUnbindRMB_S(role, param):
	'''
	神石改变
	@param role:
	@param param:
	'''
	oldValue, newValue = param
	
	#消费
	if newValue < oldValue:
		#版本判断
		if Environment.EnvIsRU():
			#七日活动
			sevenActMgr = role.GetTempObj(EnumTempObj.SevenActMgr)
			#首充
			sevenActMgr.day_first_consume()
			
def OnRoleDayClear(role, param):
	'''
	每日清理
	@param role:
	@param param:
	'''
	#版本判断
	if not Environment.EnvIsRU():
		return
	
	sevenActMgr = role.GetTempObj(EnumTempObj.SevenActMgr)
	if not sevenActMgr:
		role.SetTempObj(EnumTempObj.SevenActMgr, SevenActBase.SevenActMgr(role))
		sevenActMgr = role.GetTempObj(EnumTempObj.SevenActMgr)
	
	#累计登录
	sevenActMgr.login()

	#累计充值
	actId = 1
	if actId in sevenActMgr.reward_status_dict:
		del sevenActMgr.reward_status_dict[actId]
		
	sevenActMgr.buy_unbind_rmb = 0
		
	#每日首笔消费
	actId = 3
	if actId in sevenActMgr.reward_status_dict:
		del sevenActMgr.reward_status_dict[actId]
		
	sevenActMgr.is_first_consume = False
		
	#点石成金
	actId = 4
	if actId in sevenActMgr.reward_status_dict:
		del sevenActMgr.reward_status_dict[actId]
		
	#坐骑养成
	actId = 5
	if actId in sevenActMgr.reward_status_dict:
		del sevenActMgr.reward_status_dict[actId]
	
	sevenActMgr.mount_train_cnt = 0
		
	#心魔挑战
	actId = 7
	if actId in sevenActMgr.reward_status_dict:
		del sevenActMgr.reward_status_dict[actId]
		
	#挑战组队副本
	actId = 8
	if actId in sevenActMgr.reward_status_dict:
		del sevenActMgr.reward_status_dict[actId]
	
	#挑战竞技场
	actId = 9
	if actId in sevenActMgr.reward_status_dict:
		del sevenActMgr.reward_status_dict[actId]
	
	sevenActMgr.jjc_cnt = 0
		
	#挑战副本
	actId = 10
	if actId in sevenActMgr.reward_status_dict:
		del sevenActMgr.reward_status_dict[actId]

	#挑战公会副本
	actId = 11
	if actId in sevenActMgr.reward_status_dict:
		del sevenActMgr.reward_status_dict[actId]
	
	sevenActMgr.union_fb_cnt = 0
	
	#勇斗领主
	actId = 12
	if actId in sevenActMgr.reward_status_dict:
		del sevenActMgr.reward_status_dict[actId]
	
	#每日在线奖励
	actId = 13
	if actId in sevenActMgr.reward_status_dict:
		del sevenActMgr.reward_status_dict[actId]
	
	sevenActMgr.online_time = 0


def OnRoleSave(role, param):
	'''
	角色保存
	@param role:
	@param param:
	'''
	sevenActMgr = role.GetTempObj(EnumTempObj.SevenActMgr)
	sevenActMgr.save()

#===============================================================================
# 客户端请求
#===============================================================================
def RequestSevenActOpenMainPanel(role, msg):
	'''
	客户端请求打开开服活动主面板
	@param role:
	@param msg:
	'''
	SevenActOpenMainPanel(role)
	
def RequestSevenActGetReward(role, msg):
	'''
	客户端请求打开开服活动主面板
	@param role:
	@param msg:
	'''
	backFunId, data = msg
	actId, idx = data
	#日志
	with TraSevenActReward_RU:
		SevenActGetReward(role, actId, idx, backFunId)

#===============================================================================
# 时间
#===============================================================================
def CallAfterNewDay():
	SevenActConfig.InitIsActive()
	if not SevenActConfig.IsActive:
		return

	roleList = cRoleMgr.GetAllRole()
	for role in roleList:
		sevenActMgr = role.GetTempObj(EnumTempObj.SevenActMgr)
		if sevenActMgr.online_reward_tick_id:
			continue
		sevenActMgr.online_reward_tick_id = role.RegTick(60, OnlineReward)
			
def OnlineReward(role, callargv, regparam):
	if role.IsKick():
		return
	if not SevenActConfig.IsActive:
		return
	sevenActMgr = role.GetTempObj(EnumTempObj.SevenActMgr)
	sevenActMgr.online_reward_tick_id = role.RegTick(60, OnlineReward)
	sevenActMgr.online_reward1()


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross and (Environment.EnvIsRU() or Environment.IsDevelop):
		#角色初始化
		Event.RegEvent(Event.Eve_InitRolePyObj, OnRoleInit)
		Event.RegEvent(Event.Eve_AfterLogin, OnRoleLogin)
		#角色登陆同步其它数据
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		#角色神石改变
		Event.RegEvent(Event.AfterChangeUnbindRMB_Q, OnChangeUnbindRMB_Q)
		Event.RegEvent(Event.AfterChangeUnbindRMB_S, OnChangeUnbindRMB_S)
		#角色每日清理
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
		#角色保存
		Event.RegEvent(Event.Eve_BeforeSaveRole, OnRoleSave)
		
		#时间
		cComplexServer.RegAfterNewDayCallFunction(CallAfterNewDay)
		
		#日志
		TraSevenActReward = AutoLog.AutoTransaction("TraSevenActReward", "七日活动奖励(北美专属)")
		TraSevenActReward_RU = AutoLog.AutoTransaction("TraSevenActReward_RU", "七日活动奖励(俄罗斯专属)")
		
		#注册消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Seven_Act_Open_Main_Panel", "客户端请求打开七日活动主面板"), RequestSevenActOpenMainPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Seven_Act_Get_Reward", "客户端请求领取七日活动奖励"), RequestSevenActGetReward)
		
		