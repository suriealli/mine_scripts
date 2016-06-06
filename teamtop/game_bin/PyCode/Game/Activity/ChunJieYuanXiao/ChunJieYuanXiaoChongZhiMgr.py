#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ChunJieYuanXiao.ChunJieYuanXiaoChongZhiMgr")
#===============================================================================
# 元宵充值活动
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Activity import CircularDefine
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Role.Data import EnumDayInt1, EnumInt16
from Game.Role import Event
from Game.Activity.ChunJieYuanXiao import ChunJieYuanXiaoChongZhiConfig

if "_HasLoad" not in dir() :
	IsStart = False
	#日志
	YuanXiaoChongZhiReward_Log = AutoLog.AutoTransaction("YuanXiaoChongZhiReward_Log", "元宵充值活动领取奖励日志")


def StartActive(*param):
	_, circularType = param
	if CircularDefine.CA_ChunJieYuanXiaoChongZhi != circularType:
		return
	global IsStart
	if IsStart  :
		print "GE_EXC, repeat ChunJieYuanXiaoChongZhi has started"
	IsStart = True

def CloseActive(*param):
	_, circularType = param
	if CircularDefine.CA_ChunJieYuanXiaoChongZhi != circularType :
		return
	global IsStart
	if not IsStart :
		print "GE_EXC, repeat ChunJieYuanXiaoChongZhi has closed"
	IsStart = False

#========================================================================================
#活动控制
#========================================================================================

def RequestChongZhiReward(role, ways):
	global IsStart
	if not IsStart :
		return
	#等级不够
	if role.GetLevel() < EnumGameConfig.Level_30:
		return 
	if ways not in (1,2) :
		return
	config = ChunJieYuanXiaoChongZhiConfig.YuanXiaoChongZhiReward.get(ways)
	if not config :
		print "GE_EXC, repeat RewardId %s is not in YuanXiaoChongZhiReward in RequestChongZhiReward" % type
	NeedChargeRMB = config.NeedRechargeRMB
	#神石不够
	if role.GetDayBuyUnbindRMB_Q() < NeedChargeRMB :
		return
	#已经领取
	if ways == 1 and role.GetDI1(EnumDayInt1.ChunJieYuanXiaoChongZhi1) :
		return
	elif ways == 2 and role.GetDI1(EnumDayInt1.ChunJieYuanXiaoChongZhi2) :
		return
	with YuanXiaoChongZhiReward_Log :
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveChunJieYuanXiaoChongZhi, ways)
		if ways == 1 :
			role.SetDI1(EnumDayInt1.ChunJieYuanXiaoChongZhi1, 1)
		elif ways == 2 :
			role.SetDI1(EnumDayInt1.ChunJieYuanXiaoChongZhi2, 1)
		tips = GlobalPrompt.Reward_Tips
		for item, cnt in config.Awards :
			role.AddItem(item, cnt)
			tips += GlobalPrompt.Item_Tips % (item, cnt)
		role.IncI16(EnumInt16.ChunJieYuanXiao, config.HuaDengAmounts)
		tips += GlobalPrompt.PassionYuanXiaoTip % config.HuaDengAmounts
		role.Msg(2, 0, tips)
	


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestChunJieYuanXiaoChongZhiReward", "春节元宵充值活动奖励领取"), RequestChongZhiReward)
		Event.RegEvent(Event.Eve_StartCircularActive, StartActive)
		Event.RegEvent(Event.Eve_EndCircularActive, CloseActive)