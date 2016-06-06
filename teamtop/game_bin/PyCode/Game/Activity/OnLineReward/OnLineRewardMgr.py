#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.OnLineReward.OnLineRewardMgr")
#===============================================================================
# 在线奖励
#===============================================================================
import Environment
import cRoleMgr
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumDisperseInt32,EnumInt32, EnumInt8
from Game.Activity.OnLineReward import OnLineRewardConfig
from Game.Role import Event

if "_HasLoad" not in dir():
	#日志
	TraOnLineReward = AutoLog.AutoTransaction("TraOnLineReward", "领取在线奖励")


def OnGetOnlineReward(role, msg):
	'''
	获取在线奖励
	@param role:
	@param msg:None
	'''
	if role.GetLevel() < EnumGameConfig.OnlineReward_NEED_LEVEL :
		return
	#获取角色获取在线奖励的时间
	OLRewardtime = role.GetI32(EnumInt32.OnLineRewardTime)
	#获取角色在线的总时间
	OnlineTimes = role.GetDI32(EnumDisperseInt32.enOnlineTimes)
	#获取角色的在线奖励类型
	OnLineRewardType = role.GetI8(EnumInt8.OnLineRewardType)
	#判断角色是否还可以继续获得在线奖励，若小于0，说明在线奖励已经全部领取完成
	if OnLineRewardType < 0:
		return
	if OnLineRewardType == 0:
		OnLineRewardType = 1
	#获取在线奖励配置,判断是否成功获取到配置数据
	cfg = OnLineRewardConfig.OLRConfig_Dict.get(OnLineRewardType)
	if not cfg:
		print "GE_EXC ,  can not find OnLineRewardConfig for OnLineRewardType : %s " % OnLineRewardType
		return
	#总在线减去当前在线奖励判断一下
	dis = OnlineTimes - OLRewardtime
	#判断累积在线时间是否已经达到奖励要求
	if cfg.sec > dis:
		return
	#若玩家背包空间不足，则提示玩家清理背包后再领奖
	if role.PackageEmptySize() < len(cfg.serverItem) :
		role.Msg(2, 0, GlobalPrompt.OnLineReward_PackageSize_warning)
		return
	with TraOnLineReward:
		#设置奖励标识
		role.SetI32(EnumInt32.OnLineRewardTime, OnlineTimes)
		role.SetI8(EnumInt8.OnLineRewardType, cfg.nextRewardtype)
		role.IncBindRMB(cfg.rewardrmb)
		role.IncMoney(cfg.rewardmoney)
		AddItem = role.AddItem
		for itemCoding, cnt in cfg.serverItem:
			AddItem(itemCoding, cnt)
		itemRewardMsg = ""
		for itemCoding, cnt in cfg.serverItem:
			itemRewardMsg = itemRewardMsg + GlobalPrompt.OnLineRewardMsg_Item % (itemCoding, cnt)
		if cfg.rewardmoney == 0:
			moneyRewardMsg = ""
		else:
			moneyRewardMsg = GlobalPrompt.OnLineRewardMsg_Money % cfg.rewardmoney
		if cfg.rewardrmb == 0:
			rmbRewardMsg = ""
		else:
			rmbRewardMsg = GlobalPrompt.OnLineRewardMsg_RMB % cfg.rewardrmb
		OnLineRewardMsg = GlobalPrompt.OnLineRewardMsg_Head + itemRewardMsg + moneyRewardMsg + rmbRewardMsg
		role.Msg(2, 0, OnLineRewardMsg)
		
def AfterLogin(role, param):
	times = role.GetDI32(EnumDisperseInt32.enOnlineTimes)
	#登录同步
	role.SetI32(EnumInt32.OnLineRewardTime, times)
	
	if role.GetI32(EnumInt32.OnLineTimeToday) == 0:
		role.SetI32(EnumInt32.OnLineTimeToday, times)

def RoleDayClear(role, param):
	times = role.GetDI32(EnumDisperseInt32.enOnlineTimes)
	#每天清理的时候把在线奖励领奖事件调整到当前，即重置一下
	role.SetI32(EnumInt32.OnLineRewardTime, times)
	
	#每日累计在线时间计算逻辑
	role.SetI32(EnumInt32.OnLineTimeToday, times)


#当天在线秒数 = 总在线时间秒数 - 今天0点的总在线时间秒数
def GetOnLineTimeToday(role):
	'''获取当前累计在线时间'''
	return role.GetDI32(EnumDisperseInt32.enOnlineTimes) - role.GetI32(EnumInt32.OnLineTimeToday)


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
	
	if Environment.HasLogic and not Environment.IsCross:
		#客户端请求
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("OLR_OnGetOnlineReward", "请求获取在线奖励"), OnGetOnlineReward)


