#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ValentineDay.GlamourPartyMgr")
#===============================================================================
# 魅力派对 Mgr
#===============================================================================
import math
import cRoleMgr
import cDateTime
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Activity import CircularDefine
from Game.Role.Data import EnumObj, EnumInt32
from Game.Activity.ValentineDay import GlamourPartyConfig

IDX_PARTY = 4
if "_HasLoad" not in dir():
	IS_START = False
	
	Tra_GlamourParty_Party = AutoLog.AutoTransaction("Tra_GlamourParty_Party", "魅力派对_派对加成")
	Tra_GlamourParty_TargetReward = AutoLog.AutoTransaction("Tra_GlamourParty_TargetReward", "魅力派对_目标奖励")
	
	GlamourParty_TargetRewardRecord_S = AutoMessage.AllotMessage("GlamourParty_TargetRewardRecord_S", "魅力派对_同步目标奖励领取记录")

#### 活动控制  start ####
def OnStartGlamourParty(*param):
	'''
	开启活动
	'''
	_, circularType = param
	if CircularDefine.CA_GlamourParty != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open GlamourParty"
		return
		
	IS_START = True

def OnEndGlamourParty(*param):
	'''
	结束活动
	'''
	_, circularType = param
	if CircularDefine.CA_GlamourParty != circularType:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC, end GlamourParty while not start"
		return
		
	IS_START = False

#### 客户端请求 start
def OnGetTargetReward(role, msg):
	'''
	魅力派对_请求领取目标奖励
	@param msg:targetId 
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.GlamourParty_NeedLevel:
		return
	
	targetId = msg
	targetCfg = GlamourPartyConfig.GlamourParty_TargetConfig_Dict.get(targetId)
	if not targetCfg:
		return
	
	rewardRecordSet = role.GetObj(EnumObj.ValentineDayData)[IDX_PARTY]
	if targetId in rewardRecordSet:
		return
	
	historyGlamourExp = role.GetI32(EnumInt32.HistoryGlamourExp)
	if historyGlamourExp < targetCfg.needTotalGlamour:
		return
	
	prompt = GlobalPrompt.GlamourParty_Tips_Head	
	with Tra_GlamourParty_TargetReward:
		#写领取记录
		rewardRecordSet.add(targetId)
		role.GetObj(EnumObj.ValentineDayData)[IDX_PARTY] = rewardRecordSet
		#获得返利
		for coding, cnt in targetCfg.rewardItems:
			role.AddItem(coding, cnt)
			prompt += GlobalPrompt.GlamourParty_Tips_Item % (coding, cnt)
			
	#同步最新领取记录
	role.SendObj(GlamourParty_TargetRewardRecord_S, rewardRecordSet)
	#领取提示
	role.Msg(2, 0, prompt)

#离线命令执行 勿修改
def AfterParty(role, param):
	'''
	活动期间情迷派对后逻辑
	'''
	if not IS_START:
		return
	
	nowDays = cDateTime.Days()
	partyGrade, partyDays, qinmi = param
	partyBaseCfg = GlamourPartyConfig.GlamourParty_ConfigBase_Dict.get(partyGrade)
	if not partyBaseCfg:
		return
	
	with Tra_GlamourParty_Party:
		addGlamour = partyBaseCfg.addGlamour
		if partyDays == nowDays:
			#今日举行的party
			role.IncI32(EnumInt32.DayGlamourExp, addGlamour)
			role.IncI32(EnumInt32.HistoryGlamourExp, addGlamour)
			#尝试入魅力榜
			Event.TriggerEvent(Event.Eve_TryInGlamorRank, role)
		else:
			#今日之前 举行的party
			role.IncI32(EnumInt32.HistoryGlamourExp, addGlamour)
		
		#一定保证增加额外的亲密值
		qinmiPercent = partyBaseCfg.qinmiPercent
		qinmi = int(math.floor(qinmi * (qinmiPercent / 100.0)))
		if qinmi:
			role.IncI32(EnumInt32.Qinmi, qinmi)
	
	#亲密加成提示 可能取整就没掉了
	if qinmi:
		role.Msg(2, 0, GlobalPrompt.GlamourParty_Tips_PartyQinmi % qinmi)
	#魅力值增加提示 一定会增加累计魅力值
	role.Msg(2, 0, GlobalPrompt.GlamourParty_Tips_PartyGlamour % addGlamour)
	
	#触发情人目标 -每日派对
	Event.TriggerEvent(Event.Eve_TryCouplesGoal, role, (EnumGameConfig.GoalType_QinmiParty, 1))
	
def OnRoleInit(role, param):
	'''
	初始角色相关Obj的key
	'''
	valentineDayData = role.GetObj(EnumObj.ValentineDayData)
	if IDX_PARTY not in valentineDayData:
		valentineDayData[IDX_PARTY] = set()

def OnSyncRoleOtherData(role, param):
	'''
	上线同步数据
	'''
	if not IS_START:
		return
	
	#同步目标奖励领取记录
	rewardRecordList = role.GetObj(EnumObj.ValentineDayData)[IDX_PARTY]
	role.SendObj(GlamourParty_TargetRewardRecord_S, rewardRecordList)

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_InitRolePyObj, OnRoleInit)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartGlamourParty)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndGlamourParty)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GlamourParty_OnGetTargetReward", "魅力派对_请求领取目标奖励"), OnGetTargetReward)