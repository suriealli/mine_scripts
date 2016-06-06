#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.YeYouJieKuangHuan.YeYouJieRechargeMgr")
#===============================================================================
# 页游节充值返利 Mgr
#===============================================================================
import cRoleMgr
import cNetMessage
import cDateTime
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Role.Data import EnumInt32, EnumObj
from Game.Activity.YeYouJieKuangHuan import YeYouJieRechargeConfig

if "_HasLoad" not in dir():
	IS_START = False
	BEGIN_SEC = None
	END_SEC = None
	
	Tra_YeYouJieRecharge_GetReward = AutoLog.AutoTransaction("Tra_YeYouJieRecharge_GetReward", "页游节充值返利_领取奖励")
	
	#格式 (IS_START, BEGIN_SEC, END_SEC)
	YeYouJieRecharge_ActiveState_S = AutoMessage.AllotMessage("YeYouJieRecharge_ActiveState_S", "页游节充值返利_活动状态同步")
	#格式set([1,2])
	YeYouJieRecharge_RewardRecord_S = AutoMessage.AllotMessage("YeYouJieRecharge_RewardRecord_S", "页游节充值返利_领奖记录同步")

def OnStartYeYouJieRecharge(calArgv, regparam):
	'''
	页游节充值返利_活动开始
	'''
	global IS_START
	global BEGIN_SEC
	global END_SEC
	if IS_START is True:
		print "GE_EXC, OnStartYeYouJieRecharge while IS_START is (%s)" % IS_START
		return
	
	IS_START = True
	BEGIN_SEC, END_SEC = regparam
	
	cNetMessage.PackPyMsg(YeYouJieRecharge_ActiveState_S, (IS_START, BEGIN_SEC, END_SEC))
	cRoleMgr.BroadMsg()

def OnEndYeYouJieRecharge(calargv, regparam):
	'''
	页游节充值返利_活动结束
	'''
	global IS_START
	if not IS_START:
		print "GE_EXC,OnEndYeYouJieRecharge while IS_START is (%s)" % IS_START
		return
	
	IS_START = False
	
	cNetMessage.PackPyMsg(YeYouJieRecharge_ActiveState_S, (IS_START, BEGIN_SEC, END_SEC))
	cRoleMgr.BroadMsg()


def OnGetReward(role, msg):
	'''
	页游节充值返利_请求领取返利奖励
	'''
	if not IS_START:
		return
	
	dayIndex = msg
	
	#等级不足
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.YeYouJieRechage_NeedLevel:
		return
		
	#活动开启第二天才可以领取
	activeContinueSec = cDateTime.Seconds() - BEGIN_SEC
	if dayIndex < 1 or activeContinueSec <= EnumGameConfig.ONEDAY_SEC or (activeContinueSec / EnumGameConfig.ONEDAY_SEC < dayIndex):
		return
	
	#未充值进账
	rechargeRMB = role.GetI32(EnumInt32.YeYouJieRechareRMB)
	if rechargeRMB < 1:
		return
	
	#今日奖励已领取
	rewardRecordSet = role.GetObj(EnumObj.YeYouJieKuangHuan)[1]
	if dayIndex in rewardRecordSet:
		return
	
	#获取对应奖励配置
	rewardCfg = YeYouJieRechargeConfig.GetCfgByDayAndRMBAndLevel(dayIndex, rechargeRMB, roleLevel)
	if not rewardCfg:
		print "GE_EXC, YeYouJieRechargeMgr::OnGetReward can not get rewardCfg by (dayIndex(%s), rechargeRMB(%s), roleLevel(%s)" % (dayIndex, rechargeRMB, roleLevel)
		return
	
	prompt = GlobalPrompt.Reward_Tips
	with Tra_YeYouJieRecharge_GetReward:
		#记录今日领奖标志
		rewardRecordSet.add(dayIndex)
		#奖励魔晶
		rewardBindRMB = rewardCfg.rewardBindRMB
		if rewardBindRMB > 0:
			role.IncBindRMB(rewardBindRMB)
			prompt += GlobalPrompt.BindRMB_Tips % rewardBindRMB
		#奖励金币
		rewardMoney = rewardCfg.rewardMoney
		if rewardMoney > 0:
			role.IncMoney(rewardMoney)
			prompt += GlobalPrompt.Money_Tips % rewardMoney
		#奖励道具
		for coding, cnt in rewardCfg.rewardItems:
			role.AddItem(coding, cnt)
			prompt += GlobalPrompt.Item_Tips % (coding, cnt)
	
	#获得提示
	role.Msg(2, 0, prompt)
	#同步领奖记录
	role.SendObj(YeYouJieRecharge_RewardRecord_S, rewardRecordSet)

def OnInitRole(role, param = None):
	'''
	初始化objkey
	'''
	yeYouJieKuangHuanData = role.GetObj(EnumObj.YeYouJieKuangHuan)
	if 1 not in yeYouJieKuangHuanData:
		yeYouJieKuangHuanData[1] = set() 

def OnSyncRoleOtherData(role, param = None):
	'''
	角色上线 同步活动状态 
	'''
	if not IS_START:
		return
	
	#活动开启当天  统计今日已充值的神石
	if (cDateTime.Seconds() - BEGIN_SEC) < EnumGameConfig.ONEDAY_SEC:
		role.SetI32(EnumInt32.YeYouJieRechareRMB, role.GetDayBuyUnbindRMB_Q())
	
	#同步活动状态
	role.SendObj(YeYouJieRecharge_ActiveState_S, (IS_START, BEGIN_SEC, END_SEC))
	
	#同步领奖记录
	role.SendObj(YeYouJieRecharge_RewardRecord_S, role.GetObj(EnumObj.YeYouJieKuangHuan)[1])

def AfterRecharge(role, param = None):
	'''
	活动开启首天  统计充值神石数量
	'''
	if not IS_START:
		return
	
	#非活动开启首天 不记录充值的神石熟练
	if (cDateTime.Seconds() - BEGIN_SEC) > EnumGameConfig.ONEDAY_SEC:
		return
	
	#非充值
	oldValue, newValue = param
	if newValue <= oldValue:
		return
	
	#统计充值神石数量
	oldRechageRMB = role.GetI32(EnumInt32.YeYouJieRechareRMB)
	role.SetI32(EnumInt32.YeYouJieRechareRMB, oldRechageRMB - oldValue + newValue) 

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_InitRolePyObj, OnInitRole)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		Event.RegEvent(Event.Eve_AfterChangeDayBuyUnbindRMB_Q, AfterRecharge)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("YeYouJieRechage_OnGetReward", "页游节充值返利_请求领取返利奖励"), OnGetReward)