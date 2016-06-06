#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionSpringHongBao")
#===============================================================================
# 红包闹新春,春节活动 @author: GaoShuai 2016
#===============================================================================
import cRoleMgr
import Environment
from Game.Role.Data import EnumObj, EnumInt32
from Game.Role import Event
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from Game.Activity import CircularDefine
from Game.Activity.PassionAct import PassionDefine
from Game.Activity.PassionAct.PassionSpringHongBaoConfig import SpringHongBao_Dict


if "_HasLoad" not in dir():
	
	#消息
	SpringHongBaoData = AutoMessage.AllotMessage("SpringHongBaoData", "红包闹新春数据")
	#日志
	Tra_GetRewardSpringHongBao = AutoLog.AutoTransaction("Tra_GetRewardSpringHongBao", "红包闹新春领取奖励")
	IsStart = False


def StartCircularActive(param1, param2):
	global IsStart
	if param2 != CircularDefine.CA_PassionSpringHongBao:
		return
	if IsStart:
		print 'GE_EXC, SpringHongBao is already start'
	IsStart = True


def EndCircularActive(param1, param2):
	global IsStart
	if param2 != CircularDefine.CA_PassionSpringHongBao:
		return
	if not IsStart:
		print 'GE_EXC, SpringHongBao is already end'
	IsStart = False


def RequestSpringHongBaoReward(role, index):
	'''
	请求领取红包闹新春奖励
	@param role:
	@param index: 奖励index
	'''
	global IsStart
	if not IsStart:
		return
	if role.GetLevel() < EnumGameConfig.SpringHongBaoLevel:
		return
	SpringHongBaoSet = role.GetObj(EnumObj.PassionActData)[PassionDefine.PassionSpringHongBao]
	
	if index in SpringHongBaoSet:
		return
	configObj = SpringHongBao_Dict.get(index)
	if not configObj:
		return
	if role.GetI32(EnumInt32.SpringHongBaoRMB) < configObj.needRMB:
		return
	
	SpringHongBaoSet.add(index)
	#红包闹新春领取奖励
	tip = GlobalPrompt.Reward_Tips
	with Tra_GetRewardSpringHongBao:
		#删除物品及其他操作
		for Coding, cnt in configObj.reward:
			role.AddItem(Coding, cnt)
			tip += GlobalPrompt.Item_Tips % (Coding, cnt)
	
	role.SendObj(SpringHongBaoData, SpringHongBaoSet)
	role.Msg(2, 0, tip)


def RoleDayClear(role, param):
	#每日数据清理
	with Tra_GetRewardSpringHongBao:
		role.SetI32(EnumInt32.SpringHongBaoRMB, 0)
		role.GetObj(EnumObj.PassionActData).get(PassionDefine.PassionSpringHongBao).clear()
	role.SendObj(SpringHongBaoData, [])


def OnSyncRoleOtherData(role, param):
	'''
	角色登陆同步其它数据
	@param role:
	@param param:
	'''
	role.SendObj(SpringHongBaoData, role.GetObj(EnumObj.PassionActData).get(PassionDefine.PassionSpringHongBao))


def AfterLogin(role, param):
	'''
	角色登陆初始化数据
	@param role:
	@param param:
	'''
	if PassionDefine.PassionSpringHongBao not in role.GetObj(EnumObj.PassionActData):
		role.GetObj(EnumObj.PassionActData)[PassionDefine.PassionSpringHongBao] = set()

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#角色登陆同步其它数据
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		Event.RegEvent(Event.Eve_StartCircularActive, StartCircularActive)
		Event.RegEvent(Event.Eve_EndCircularActive, EndCircularActive)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestSpringHongBaoReward", "请求领取红包闹新春奖励"), RequestSpringHongBaoReward)
