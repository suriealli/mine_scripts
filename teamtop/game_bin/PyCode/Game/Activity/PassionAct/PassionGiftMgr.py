#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionGiftMgr")
#===============================================================================
# 激情有礼Mgr
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Activity import CircularDefine
from Game.Activity.PassionAct import PassionGiftConfig, PassionDefine
from Game.Role.Data import EnumDayInt1, EnumObj, EnumInt16, EnumInt8


if "_HasLoad" not in dir():
	IS_START = False
	#格式 set([rewardIndex,])
	PassionGift_AccuRewardRecord_S = AutoMessage.AllotMessage("PassionGift_AccuRewardRecord_S", "激情有礼_累计完成任务奖励领取记录同步")
	
	Tra_PassionGift_GetTodayReward = AutoLog.AutoTransaction("Tra_PassionGift_GetTodayReward", "激情有礼_领取今日任务达成奖励")
	Tra_PassionGift_GetAccuReward = AutoLog.AutoTransaction("Tra_PassionGift_GetAccuReward", "激情有礼_领取累计达成任务奖励")

		
#### 活动控制  start ####
def OnStartPassionGift(*param):
	'''
	开启活动
	'''
	_, circularType = param
	if CircularDefine.CA_PassionGift != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open PassionGift"
		return
		
	IS_START = True
	

def OnEndPassionGift(*param):
	'''
	结束活动
	'''
	_, circularType = param
	if CircularDefine.CA_PassionGift != circularType:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC, end PassionGift while not start"
		return
		
	IS_START = False
	

##### 客户端请求 start
def OnGetTodayReward(role, msg = None):
	'''
	激情有礼_请求领取今日任务达成奖励
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.PassionGift_NeedLevel:
		return
	
	isReward = role.GetDI1(EnumDayInt1.PassionGift_IsReward)
	if isReward:
		return
	
	dailyDoScore = role.GetI16(EnumInt16.DailyDoScore)
	if dailyDoScore < EnumGameConfig.PassionGift_TargetScore:
		return
	
	prompt = GlobalPrompt.PassionGift_Tips_Head
	with Tra_PassionGift_GetTodayReward:
		role.SetDI1(EnumDayInt1.PassionGift_IsReward, 1)
		coding, cnt = EnumGameConfig.PassionGift_TodayReward
		role.AddItem(coding, cnt)
		prompt += GlobalPrompt.Item_Tips % (coding, cnt)
	
	role.Msg(2, 0, prompt)
	

def OnGetAccuReward(role, msg):
	'''
	激情有礼_请求领取今日任务达成奖励
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.PassionGift_NeedLevel:
		return
	
	targetIndex = msg
	if targetIndex not in PassionGiftConfig.PassionGift_Reward_Dict:
		return
	
	rewardRecordSet = role.GetObj(EnumObj.PassionActData)[PassionDefine.PassionGift]
	if targetIndex in rewardRecordSet:
		return
	
	if targetIndex > role.GetI8(EnumInt8.PassionGiftAccuCnt):
		return
	
	prompt = GlobalPrompt.PassionGift_Tips_Head
	with Tra_PassionGift_GetAccuReward:
		rewardRecordSet.add(targetIndex)
		coding, cnt = PassionGiftConfig.PassionGift_Reward_Dict[targetIndex]
		role.AddItem(coding, cnt)
		prompt += GlobalPrompt.Item_Tips % (coding, cnt)
	
	role.SendObj(PassionGift_AccuRewardRecord_S, rewardRecordSet)
	
	role.Msg(2, 0, prompt)
	
	
#### 事件 start
def OnInitRole(role, param = None):
	'''
	初始化角色相关Key
	'''
	passisonActData = role.GetObj(EnumObj.PassionActData)
	if PassionDefine.PassionGift not in passisonActData:
		passisonActData[PassionDefine.PassionGift] = set()


def OnSyncOtherData(role, param = None):
	'''
	上线触发兼容处理 维护前活跃度达标 计算累计达成次数
	'''
	
	if not IS_START:
		return
	
	dailyDoScore = role.GetI16(EnumInt16.DailyDoScore)
	isAccu = role.GetDI1(EnumDayInt1.PassionGift_IsAccu) 
	if dailyDoScore >= EnumGameConfig.PassionGift_TargetScore and not isAccu:
		role.IncI8(EnumInt8.PassionGiftAccuCnt,1)
		role.SetDI1(EnumDayInt1.PassionGift_IsAccu,1)
	
	#同步领取记录
	role.SendObj(PassionGift_AccuRewardRecord_S, role.GetObj(EnumObj.PassionActData)[PassionDefine.PassionGift])
	

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		
		Event.RegEvent(Event.Eve_InitRolePyObj, OnInitRole)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncOtherData)
		
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartPassionGift)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndPassionGift)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("PassionGift_OnGetTodayReward", "激情有礼_请求领取今日任务达成奖励"), OnGetTodayReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("PassionGift_OnGetToDayReward", "激情有礼_请求领取今日任务达成奖励"), OnGetAccuReward)
