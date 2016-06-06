#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ZhongQiu.ZhongQiuShouChongMgr")
#===============================================================================
# 中秋首冲 Mgr
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Activity import CircularDefine
from Game.Role.Data import EnumDayInt1, EnumInt8, EnumObj
from Game.Activity.ZhongQiu import ZhongQiuShouChongConfig


IDX_RECHARGE = 1

if "_HasLoad" not in dir():
	IS_START = False
	
	Tra_ZhongQiuShouChong_Recharge = AutoLog.AutoTransaction("Tra_ZhongQiuShouChong_Recharge", "中秋首冲_记录今日首冲")
	Tra_ZhongQiuShouChong_GetReward = AutoLog.AutoTransaction("Tra_ZhongQiuShouChong_GetReward", "中秋首冲_领取首冲奖励")
	
	
	ZhongQiuShouChong_RewardRecord_S = AutoMessage.AllotMessage("ZhongQiuShouChong_RewardRecord_S", "中秋首冲_领取记录同步")
	
#===============================================================================
# 活动控制
#===============================================================================
def OnStartZhongQiuShouChong(*param):
	'''
	活动开启
	'''
	_, circularType = param
	if CircularDefine.CA_ZhongQiuRecharge != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open ZhongQiuShouChong"
		return
		
	IS_START = True
	

def OnEndZhongQiuShouChong(*param):
	'''
	活动结束
	'''
	_, circularType = param
	if CircularDefine.CA_ZhongQiuRecharge != circularType:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC, end ZhongQiuShouChong while not start"
		return
		
	IS_START = False


#===============================================================================
# 客户端请求
#===============================================================================
def OnGetShouChongReward(role, msg):
	'''
	中秋首冲_请求领取首冲奖励
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.ZhongQiuShouChong_NeedLevel:
		return
	
	dayIndex = msg
	rewardCfg = ZhongQiuShouChongConfig.ZhongQiuShouChong_Reward_Dict.get(dayIndex, None)
	if not rewardCfg:
		return
	
	#充值天数不达标
	rechargeDays = role.GetI8(EnumInt8.ZhongQiuShouChong_RechargeDays)
	if dayIndex > rechargeDays:
		return
	
	#已经领取对应天数的奖励
	rechargeRewardRecord_Set = role.GetObj(EnumObj.ZhongQiuData)[IDX_RECHARGE]
	if dayIndex in rechargeRewardRecord_Set:
		return 
	
	prompt = GlobalPrompt.Reward_Tips
	with Tra_ZhongQiuShouChong_GetReward:
		#领取记录
		rechargeRewardRecord_Set.add(dayIndex)
		#物品获得
		for coding, cnt in rewardCfg.rewardItems:
			role.AddItem(coding, cnt)
			prompt += GlobalPrompt.Item_Tips % (coding, cnt)
		#步数获得
		if rewardCfg.rewardStep > 0:
			role.IncI8(EnumInt8.HuoYueDaLi_EffectStep, rewardCfg.rewardStep)
			prompt += GlobalPrompt.HuoYueDaLi_Tips_Steps % rewardCfg.rewardStep
	
	#提示
	role.Msg(2, 0, prompt)
	#同步最新领取记录
	role.SendObj(ZhongQiuShouChong_RewardRecord_S, rechargeRewardRecord_Set)


#===============================================================================
# 辅助
#===============================================================================
def OnRecordShouChong(role, param = None):
	'''
	尝试记录今日首冲
	'''
	if not IS_START:
		return
	
	if role.GetDI1(EnumDayInt1.ZhongQiuShouChong_IsRecord):
		return
	
	if role.GetDayBuyUnbindRMB_Q() < EnumGameConfig.ZhongQiuShouChong_MinRMB:
		return
	
	with Tra_ZhongQiuShouChong_Recharge:
		role.IncI8(EnumInt8.ZhongQiuShouChong_RechargeDays, 1)
		role.SetDI1(EnumDayInt1.ZhongQiuShouChong_IsRecord, 1)


#===============================================================================
# 事件
#===============================================================================
def OnSyncOtherData(role, param = None):
	'''
	上线处理
	'''
	OnRecordShouChong(role)
	
	#同步最新领取记录
	role.SendObj(ZhongQiuShouChong_RewardRecord_S, role.GetObj(EnumObj.ZhongQiuData)[IDX_RECHARGE])

	
def OnInitPyRole(role, param = None):
	'''
	初始化相关key
	'''
	zhongQiuDataDict = role.GetObj(EnumObj.ZhongQiuData)
	if IDX_RECHARGE not in zhongQiuDataDict:
		zhongQiuDataDict[IDX_RECHARGE] = set()
		

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_InitRolePyObj, OnInitPyRole)
		
		Event.RegEvent(Event.Eve_AfterChangeDayBuyUnbindRMB_Q, OnRecordShouChong)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncOtherData)
		
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartZhongQiuShouChong)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndZhongQiuShouChong)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ZhongQiuShouChong_OnGetShouChongReward", "中秋首冲_请求领取首冲奖励"), OnGetShouChongReward)
