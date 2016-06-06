#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.InviteFriendAndShare.InviteFriendAndShare")
#===============================================================================
# 好友邀请和分享
#===============================================================================
import cRoleMgr
import Environment
from Common import CValue
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumInt8, EnumDayInt8, EnumObj, EnumInt16
from Game.Activity.InviteFriendAndShare import InviteFriendAndShareConfig
from Game.Role import Event

if "_HasLoad" not in dir():
	IFAS_Share = AutoMessage.AllotMessage("IFAS_Share", "分享好友状态")
	IFAS_Reward = AutoMessage.AllotMessage("IFAS_Reward", "抽奖回调")
	
	IFAS_Log = AutoLog.AutoTransaction("IFAS_Log", "好友邀请和分享增加抽奖次数")
	IFAS_Reward_Log = AutoLog.AutoTransaction("IFAS_Reward_Log", "好友邀请和分享抽奖奖励")

def FriendShare(role, msg):
	'''
	分享好友
	@param role:
	@param msg:分享索引
	'''
	index = msg
	
	#不在配置表中的索引
	cfg = InviteFriendAndShareConfig.InviteFriend_Dict.get(index)
	if not cfg:
		return
	
	#邀请的不加
	if cfg.BigType == 5:
		return
	
	#分享状态列表
	ShareStatusList = role.GetObj(EnumObj.InviteFriendObj).get(1)
	
	#已分享
	if index in ShareStatusList:
		return
	
	ShareStatusList.append(index)
	
	with IFAS_Log:
		#加抽奖次数
		role.IncI16(EnumInt16.InviteReward, 1)
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveShareFriend, (index, 1))
	
	role.GetObj(EnumObj.InviteFriendObj)[1] = ShareStatusList
	
	#同步客户端分享好友状态信息
	role.SendObj(IFAS_Share, ShareStatusList)
	
	Event.TriggerEvent(Event.Eve_AfterShareQQ, role, None)

def InviteFriend(role, msg):
	'''
	邀请好友
	@param role:
	@param msg:[好友个数, 群个数]
	'''
	friend_cnt, qun_cnt = msg
	
	if role.GetDI8(EnumDayInt8.InviteFriendCnt) + friend_cnt > CValue.MAX_INT8:
		return
	
	#加邀请好友数目
	role.IncDI8(EnumDayInt8.InviteFriendCnt, friend_cnt)
	#加邀请群数目
	role.IncDI8(EnumDayInt8.InviteQunCnt, qun_cnt)
	
	#当前邀请次数
	nowFriendCnt = role.GetDI8(EnumDayInt8.InviteFriendCnt)
	nowQunCnt = role.GetDI8(EnumDayInt8.InviteQunCnt)
	
	#当前已完成的邀请次数
	InviteFriendCnt = role.GetObj(EnumObj.InviteFriendObj).get(2)
	InviteQunCnt = role.GetObj(EnumObj.InviteFriendObj).get(4)
	
	with IFAS_Log:
		#邀请一个好友
		if nowFriendCnt >= 1 and 1 not in InviteFriendCnt:
			InviteFriendCnt.add(1)
			role.IncI16(EnumInt16.InviteReward, 1)
			AutoLog.LogBase(role.GetRoleID(), AutoLog.eveInviteFriend, 1)
			
		#邀请二个好友
		if nowFriendCnt >= 2 and 2 not in InviteFriendCnt:
			InviteFriendCnt.add(2)
			role.IncI16(EnumInt16.InviteReward, 1)
			AutoLog.LogBase(role.GetRoleID(), AutoLog.eveInviteFriend, 2)
			
		if Environment.EnvIsQQ():
			#邀请一个群
			if nowQunCnt >= 1 and 1 not in InviteQunCnt:
				InviteQunCnt.add(1)
				role.IncI16(EnumInt16.InviteReward, 1)
			AutoLog.LogBase(role.GetRoleID(), AutoLog.eveInviteFriend, 3)
	
	role.GetObj(EnumObj.InviteFriendObj)[2] = InviteFriendCnt
	role.GetObj(EnumObj.InviteFriendObj)[4] = InviteQunCnt
	
	#触发成功邀请好友
	Event.TriggerEvent(Event.Eve_AfterInviteQQFriend, role, friend_cnt)
	
def InviteReward(role, msg):
	'''
	抽奖
	@param role:
	@param msg:
	'''
	#没有抽奖次数
	if not role.GetI16(EnumInt16.InviteReward):
		return
	
	#随机抽奖索引
	index = InviteFriendAndShareConfig.randomRewardIndex.RandomOne()
	
	#配置表
	cfg = InviteFriendAndShareConfig.InviteFriendReward_Dict.get(index)
	
	#减抽奖次数
	role.DecI16(EnumInt16.InviteReward, 1)
	
	#需要回调
	role.SendObjAndBack(IFAS_Reward, index, 5, CallBackFun, cfg)

def CallBackFun(role, callargv, regparam):
	#奖励配置
	cfg = regparam
	
	#发放奖励
	with IFAS_Reward_Log:
		if cfg.items:
			role.AddItem(*cfg.items)
			role.Msg(2, 0, GlobalPrompt.Item_Tips % cfg.items)
		if cfg.bindRMB:
			role.IncBindRMB(cfg.bindRMB)
			role.Msg(2, 0, GlobalPrompt.BindRMB_Tips % cfg.bindRMB)
	
def InviteeChange(role, param):
	inviteObj = role.GetObj(EnumObj.InviteInfo)
	
	#key:0 是邀请者
	if 0 in inviteObj:
		inviteSuccessCnt = len(inviteObj) - 1
	else:
		inviteSuccessCnt = len(inviteObj)
	
	#成功邀请个数
	role.SetI8(EnumInt8.InviteSuccess, inviteSuccessCnt)
	
	InviteFriendSuccessCnt = role.GetObj(EnumObj.InviteFriendObj).get(3)
	
	with IFAS_Log:
		#成功邀请二个
		if inviteSuccessCnt >= 2 and 2 not in InviteFriendSuccessCnt:
			InviteFriendSuccessCnt.add(2)
			role.IncI16(EnumInt16.InviteReward, 1)
			AutoLog.LogBase(role.GetRoleID(), AutoLog.eveInviteFriendSuccess, 1)
		
		#成功邀请五个
		if inviteSuccessCnt >= 5 and 5 not in InviteFriendSuccessCnt:
			InviteFriendSuccessCnt.add(5)
			role.IncI16(EnumInt16.InviteReward, 1)
			AutoLog.LogBase(role.GetRoleID(), AutoLog.eveInviteFriendSuccess, 2)
			
		#成功邀请十个
		if inviteSuccessCnt >= 10 and 10 not in InviteFriendSuccessCnt:
			InviteFriendSuccessCnt.add(10)
			role.IncI16(EnumInt16.InviteReward, 1)
			AutoLog.LogBase(role.GetRoleID(), AutoLog.eveInviteFriendSuccess, 3)
			
		#成功邀请十五个
		if inviteSuccessCnt >= 15 and 15 not in InviteFriendSuccessCnt:
			InviteFriendSuccessCnt.add(15)
			role.IncI16(EnumInt16.InviteReward, 1)
			AutoLog.LogBase(role.GetRoleID(), AutoLog.eveInviteFriendSuccess, 4)
			
		#成功邀请二十个
		if inviteSuccessCnt >= 20 and 20 not in InviteFriendSuccessCnt:
			InviteFriendSuccessCnt.add(20)
			role.IncI16(EnumInt16.InviteReward, 1)
			AutoLog.LogBase(role.GetRoleID(), AutoLog.eveInviteFriendSuccess, 5)
		
	role.GetObj(EnumObj.InviteFriendObj)[3] = InviteFriendSuccessCnt
	
def BeforNewDay(role, param):
	ShareStatusList = role.GetObj(EnumObj.InviteFriendObj).get(1)
	#根据配置表中设定清理好友分享状态列表中需要每日重置的状态
	IIG = InviteFriendAndShareConfig.InviteFriend_Dict.get
	tempList = []
	for index in ShareStatusList:
		cfg = IIG(index)
		if not cfg:
			continue
		if cfg.DayClear:
			continue
		tempList.append(index)
	
	#清理分享状态
	role.GetObj(EnumObj.InviteFriendObj)[1] = tempList
	
	#清理邀请次数
	role.GetObj(EnumObj.InviteFriendObj)[2] = set()
	
	#清理邀请群个数
	role.GetObj(EnumObj.InviteFriendObj)[4] = set()
	
	#同步客户端清理后的分享状态列表
	role.SendObj(IFAS_Share, tempList)

def SyncRoleOtherData(role, param):
	#上线同步分享状态
	role.SendObj(IFAS_Share, role.GetObj(EnumObj.InviteFriendObj)[1])
	
if "_HasLoad" not in dir():
	if Environment.HasLogic :
		Event.RegEvent(Event.Eve_RoleDayClear, BeforNewDay)
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_AfterInviteeChange, InviteeChange)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
	
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("IFAS_InviteFriend", "邀请好友"), InviteFriend)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("IFAS_FriendShare", "分享好友"), FriendShare)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("IFAS_InviteReward", "抽奖"), InviteReward)
	