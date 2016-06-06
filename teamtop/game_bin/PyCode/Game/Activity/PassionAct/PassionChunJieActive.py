#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionChunJieActive")
#===============================================================================
# 活跃有礼
#===============================================================================
import Environment
import cRoleMgr
import cComplexServer
import datetime
import cDateTime
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Activity import CircularDefine
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.SysData import WorldData
from Game.Role.Data import EnumInt16, EnumDayInt1
from Game.Activity.PassionAct import PassionChunJieActiveConfig
from Game.Role import Event


if "_HasLoad" not in dir():
	IsStart = False
	#消息同步
	ChunJieActiveToday = AutoMessage.AllotMessage("ChunJieActiveToday", "激情活动春节活跃有礼第几天")
	#日志的同步
	PassionChunJieActiveLogin_Log = AutoLog.AutoTransaction("PassionChunJieActiveLogin_Log", "激情活动春节活跃有礼登陆日志")
	PassionChunJieActiveDailyDoReward_Log = AutoLog.AutoTransaction("PassionChunJieActiveDailyDoReward_Log", "激情活动春节活跃有礼每天完成日志")
	PassionChunJieActiveRechargeReward_Log = AutoLog.AutoTransaction("PassionChunJieActiveRechargeReward_Log", "激情活动春节活跃有礼充值日志")
	


def StartActive(*param):
	_, circularType = param
	if CircularDefine.CA_PassionChunJieActive != circularType:
		return
	global IsStart
	if IsStart  :
		print "GE_EXC, repeat PassionChunJieActive has started"
	IsStart = True
	SysToday(None)
	
def CloseActive(*param):
	_, circularType = param
	if CircularDefine.CA_PassionChunJieActive != circularType:
		return
	global IsStart
	if not IsStart :
		print "GE_EXC, repeat PassionChunJieActive has closed"
	IsStart =False
	WorldData.SetChunJieActiveDays(0)

def SysToday(*param):
	global IsStart
	if not IsStart :
		return
	if not WorldData.WD.returnDB:
		return
	#计算今天是第几天
	from Game.Activity import CircularActive 
	acfg = CircularActive.CircularActiveConfig_Dict.get(CircularDefine.CA_PassionChunJieActive)
	if not acfg :
		print "GE_EXC, repeat this is not circularId %s in CircularActiveConfig_Dict in PassionChunJieActive EveryNewDay" % CircularDefine.CA_PassionChunJieActive
	startdate = datetime.datetime(*acfg.startDate)
	NowDate = cDateTime.Now().date()
	overdays = (NowDate - startdate.date()).days + 1
	WorldData.SetChunJieActiveDays(overdays)
#====================================================================
#客户端请求
#====================================================================
def RequestLoginAward(role, param = 0):
	global IsStart
	#领取登陆奖励
	if not IsStart:
		return
	if role.GetLevel() < EnumGameConfig.Level_30:
		return
	#已经领取
	if role.GetDI1(EnumDayInt1.PassionChunJieLoginAward) :
		return
	if not WorldData.WD.returnDB:
		print "GE_EXC, returnDB is False in Game.Activity.PassionAct.PassionChunJieActive RequestLoginAward"
		return
	Days = WorldData.GetChunJieActiveDays()
	Config = PassionChunJieActiveConfig.PassionChunJieActiveConfigDict.get(Days)
	if not Config :
		print "GE_EXC, repeat Days %s is not in PassionChunJieActiveConfigDict  in RequestLoginAward" % Days
		return
	LoginAward = Config.LoginReward
	if not LoginAward :
		print "GE_EXC, repeat Days %s is not in PassionChunJieActiveConfigDict  in RequestLoginAward" % Days
		return
	#发奖励
	with PassionChunJieActiveLogin_Log :
		role.SetDI1(EnumDayInt1.PassionChunJieLoginAward, 1)
		tips = GlobalPrompt.Reward_Tips
		for item, cnt in LoginAward :
			role.AddItem(item, cnt)
			tips += GlobalPrompt.Item_Tips % (item, cnt)
		role.Msg(2, 0, tips)


def RequestDailyDoReward(role, param = 0):
	global IsStart
	#领取每日活跃度奖励
	if not IsStart:
		return
	if role.GetLevel() < EnumGameConfig.Level_30:
		return
	#已经领取
	if role.GetDI1(EnumDayInt1.PassionChunJieDailyDoReward) :
		return
	if not WorldData.WD.returnDB:
		print "GE_EXC, returnDB is False in Game.Activity.PassionAct.PassionChunJieActive RequestDailyDoReward"
		return
	Days = WorldData.GetChunJieActiveDays()
	
	DailyDoScore = PassionChunJieActiveConfig.PassionChunJieActiveConfigDict.get(Days).MinDailyDoScore
	#活跃度不足
	if DailyDoScore > role.GetI16(EnumInt16.DailyDoScore) :
		return
	DailyDoReward = PassionChunJieActiveConfig.PassionChunJieActiveConfigDict.get(Days).DailyDoReward
	if not DailyDoReward :
		print "GE_EXC, repeat Days %s is not in PassionChunJieActiveConfigDict  in RequestDailyDoReward" % Days
		return
	#发奖励
	with PassionChunJieActiveDailyDoReward_Log :
		role.SetDI1(EnumDayInt1.PassionChunJieDailyDoReward, 1)
		tips = GlobalPrompt.Reward_Tips
		for item, cnt in DailyDoReward :
			role.AddItem(item, cnt)
			tips += GlobalPrompt.Item_Tips % (item, cnt)
		role.Msg(2, 0, tips)



def RequestRechargeReward(role, param):
	global IsStart
	#领取充值奖励
	if not IsStart:
		return
	if role.GetLevel() < EnumGameConfig.Level_30:
		return
	#已经领取
	if role.GetDI1(EnumDayInt1.PassionChunJieRechargeReward) :
		return
	if not WorldData.WD.returnDB:
		print "GE_EXC, returnDB is False in Game.Activity.PassionAct.PassionChunJieActive RequestRechargeReward"
		return
	Days = WorldData.GetChunJieActiveDays()
	
	MinRechargeRMB = PassionChunJieActiveConfig.PassionChunJieActiveConfigDict.get(Days).MinRechargeRMB
	#充值不足
	if MinRechargeRMB > role.GetDayBuyUnbindRMB_Q() :
		return
	RechargeReward = PassionChunJieActiveConfig.PassionChunJieActiveConfigDict.get(Days).RechargeReward
	if not RechargeReward :
		print "GE_EXC, repeat Days %s is not in PassionChunJieActiveConfigDict  in RequestDailyDoReward" % Days
		return
	#发奖励
	with PassionChunJieActiveRechargeReward_Log :
		role.SetDI1(EnumDayInt1.PassionChunJieRechargeReward, 1)
		tips = GlobalPrompt.Reward_Tips
		for item, cnt in RechargeReward :
			role.AddItem(item, cnt)
			tips += GlobalPrompt.Item_Tips % (item, cnt)
		role.Msg(2, 0, tips)
		


#===============================================================
#新的一天
#===============================================================
def EveryNewDay():
	global IsStart
	if not IsStart:
		return
	if not WorldData.WD.returnDB:
		print "GE_EXC, returnDB is False in Game.Activity.PassionAct.PassionChunJieActive EveryNewDay"
		return
	SysToday(None)
	#垮天给所有在线玩家更新新的一天
	for tmpRole in cRoleMgr.GetAllRole():
		SyncRoleOtherData(tmpRole)

def SyncRoleOtherData(role, param = 1):
	global IsStart
	if not IsStart:
		return
	if not WorldData.WD.returnDB:
		print "GE_EXC, returnDB is False in Game.Activity.PassionAct.PassionChunJieActive EveryNewDay"
		return
	Days = WorldData.GetChunJieActiveDays()
	role.SendObj(ChunJieActiveToday, Days)
	



if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestPassionChunJieLoginAward", "活跃有礼登陆奖励领取"), RequestLoginAward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestPassionChunJieDailyDoReward", "活跃有礼活跃度奖励领取"), RequestDailyDoReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestPassionChunJieRechargeReward", "活跃有礼充值奖励领取"), RequestRechargeReward)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		cComplexServer.RegAfterNewDayCallFunction(EveryNewDay)
		Event.RegEvent(Event.Eve_StartCircularActive, StartActive)
		Event.RegEvent(Event.Eve_EndCircularActive, CloseActive)
		Event.RegEvent(Event.Eve_AfterLoadWorldData, SysToday)