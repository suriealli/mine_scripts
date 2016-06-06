#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DoubleEleven.DELoginRewardMgr")
#===============================================================================
# 双十一2015 登陆有礼 Mgr
#===============================================================================
import cRoleMgr
import cDateTime
import cNetMessage
import cComplexServer
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Role.Data import EnumObj
from Game.Activity.DoubleEleven import DELoginRewardConfig

IDX_DELoginReward = 1

if "_HasLoad" not in dir():
	#活动开关标志
	IS_START = False
	#活动结束时间戳
	ENDTIME = 0
	#天数索引
	DAYINDEX = 0
	
	#活动状态同步 格式: endTime (非零表示活动结束时间戳，零表示告知活动结束！)
	DELoginReward_ActiveState_S = AutoMessage.AllotMessage("DELoginReward_ActiveState_S", "登录有礼_活动状态同步")
	#今日奖励领取记录同步  格式：set(rewardIndex1,) 表示已经领取rewardIndex1
	DELoginReward_RewardRecord_S = AutoMessage.AllotMessage("DELoginReward_RewardRecord_S", "登录有礼_奖励状态同步")
	#登录有礼_活动天数同步 dayindex
	DELoginReward_DayIndex_S = AutoMessage.AllotMessage("DELoginReward_DayIndex_S", "登录有礼_活动天数同步")

	Tra_DELoginReward_GetReward = AutoLog.AutoTransaction("Tra_DELoginReward_GetReward", "登录有礼_领取奖励")

#===============================================================================
# 活动控制
#===============================================================================
def OpenActive(callArgv, regparam):
	'''
	古堡探秘-开启
	'''
	global ENDTIME
	global IS_START
	
	if IS_START:
		print 'GE_EXC, repeat start DELoginReward'
		return
	IS_START = True
	
	ENDTIME = regparam
	
	cNetMessage.PackPyMsg(DELoginReward_ActiveState_S, (IS_START,ENDTIME))
	cRoleMgr.BroadMsg()
	
	#活动开启即可计算天数索引  不能直接设置为1 有可能活动期间重启服务器
	CalculateDayIndex()
	
	
def CloseActive(callArgv, regparam):
	'''
	古堡探秘-结束
	'''
	global IS_START
	
	if not IS_START:
		print 'GE_EXC, repeat end DELoginReward'
		return
	IS_START = False
	
	cNetMessage.PackPyMsg(DELoginReward_ActiveState_S, (IS_START, ENDTIME))
	cRoleMgr.BroadMsg()


#===============================================================================
# 客户端请求
#===============================================================================
def OnGetReward(role, msg):
	'''
	登陆有礼_请求领取奖励
	@param msg: rewardindex
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.DELoginReward_NeedLevel:
		return
	
	targetRewardIndex = msg
	#今日对应奖励已经领取
	DELoginRewardSet = role.GetObj(EnumObj.ElevenActData)[IDX_DELoginReward]
	if targetRewardIndex in DELoginRewardSet:
		return
	
	#对应配置不存在
	rewardCfg = DELoginRewardConfig.GetCfgByIndex(DAYINDEX, targetRewardIndex)
	if not rewardCfg:
		return
	
	#今日充值神石数不足领奖条件
	if role.GetDayBuyUnbindRMB_Q() < rewardCfg.needDayBuyRMB:
		return
	
	prompt = GlobalPrompt.DELoginReward_Tips_Head
	with Tra_DELoginReward_GetReward:
		#添加领取记录
		DELoginRewardSet.add(targetRewardIndex)
		#获得奖励
		for coding, cnt in rewardCfg.rewardItems:
			role.AddItem(coding, cnt)
			prompt += GlobalPrompt.Item_Tips % (coding, cnt)
	
	#提示
	role.Msg(2, 0, prompt)
	#最新奖励状态同步
	role.SendObj(DELoginReward_RewardRecord_S, DELoginRewardSet)


#===============================================================================
# 辅助
#===============================================================================
def CalculateDayIndex(isBroad = True):
	'''
	计算当前活动开启天数
	'''
	#活动开始的天数
	baseCfg = DELoginRewardConfig.DELoginRewardActive_cfg 
	if not baseCfg:
		print "GE_EXC,CircularActive.DELoginRewardActive_cfg is None"
		return
	
	#当前日期时间
	nowDate = cDateTime.Now()
	#活动持续开启的天数
	durableDay = (nowDate - baseCfg.beginTime).days
	#更新全局DAY_INDEX
	global DAYINDEX
	DAYINDEX = durableDay + 1	
	#超过 强制设置最后一天
	if DAYINDEX > baseCfg.totalDay:
		DAYINDEX = baseCfg.totalDay
	
	if isBroad:
		cNetMessage.PackPyMsg(DELoginReward_DayIndex_S, DAYINDEX)
		cRoleMgr.BroadMsg()
		
#===============================================================================
# 事件
#===============================================================================
def OnDayClear(role, param = None):
	'''
	跨天清理领取记录
	'''
	DELoginRewardSet = role.GetObj(EnumObj.ElevenActData)[IDX_DELoginReward]
	DELoginRewardSet.clear()
	
	
	if IS_START:
		#最新奖励状态同步
		role.SendObj(DELoginReward_RewardRecord_S, role.GetObj(EnumObj.ElevenActData)[IDX_DELoginReward])
	
	
def OnInitRolePyObj(role, param = None):
	'''
	初始化相关key
	'''
	DEData = role.GetObj(EnumObj.ElevenActData)
	if IDX_DELoginReward not in DEData:
		DEData[IDX_DELoginReward] = set()
		

def OnSyncOtherData(role, param = None):
	'''
	上线处理
	1.同步活动开启
	2.同步领取记录
	'''
	if IS_START:
		#同步活动开启
		role.SendObj(DELoginReward_ActiveState_S, (IS_START, ENDTIME))
		#最新奖励状态同步
		role.SendObj(DELoginReward_RewardRecord_S, role.GetObj(EnumObj.ElevenActData)[IDX_DELoginReward])
		#同步今日活动天数
		role.SendObj(DELoginReward_DayIndex_S, DAYINDEX)
	else:
		pass


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, OnDayClear)
	
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_InitRolePyObj, OnInitRolePyObj)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncOtherData)
		
		cComplexServer.RegAfterNewDayCallFunction(CalculateDayIndex)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DELoginReward_OnGetReward", "登陆有礼_请求领取奖励"), OnGetReward)