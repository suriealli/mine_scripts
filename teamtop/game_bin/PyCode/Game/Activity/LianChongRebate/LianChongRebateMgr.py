#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.LianChongRebate.LianChongRebateMgr")
#===============================================================================
# 连充返利 Mgr
#===============================================================================
import cRoleMgr
import cDateTime
import cNetMessage
import Environment
from Common.Other import GlobalPrompt
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Role.Data import EnumInt32, EnumObj
from Game.Activity.LianChongRebate import LianChongRebateConfig

if "_HasLoad" not in dir():
	IS_START = False
	ENDTIME = 0
	VERSION = 0
	
	#格式 : (IS_START, ENDTIME)
	LianChongRebate_ActiveStatus_S = AutoMessage.AllotMessage("LianChongRebate_ActiveStatus_S", "连充返利_同步活动状态")
	#格式: {1:{rewardType:[buyTimes,lastModifyDay],}, 2:{rewardType:set(rewardLevel)},3:set([rewardType1,rewardType2])}
	LianChongRebate_RoleActiveData_S = AutoMessage.AllotMessage("LianChongRebate_RoleActiveData_S", "连充返利_同步玩家活动数据")
	
	Tra_LianChongRebate_UpdateVersion = AutoLog.AutoTransaction("Tra_LianChongRebate_UpdateVersion", "连充返利_更新活动版本号")
	Tra_LianChongRebate_GetTodayReward = AutoLog.AutoTransaction("Tra_LianChongRebate_GetTodayReward", "连充返利_领取今日充值奖励项")
	Tra_LianChongRebate_GetUnlockReward = AutoLog.AutoTransaction("Tra_LianChongRebate_GetUnlockReward", "连充返利_领取解锁奖励")

#### 活动控制 start
def OnStartLianChongRebate(*param):
	'''
	连充返利_开启
	'''
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open LianChongRebate"
		return 
	
	global ENDTIME, VERSION
	_,activeParam = param
	VERSION, ENDTIME = activeParam
	IS_START = True
	
	#更新所有在线玩家 活动相关数据
	for tmpRole in cRoleMgr.GetAllRole():
		InitAndUpdateVersion(tmpRole)
	
	cNetMessage.PackPyMsg(LianChongRebate_ActiveStatus_S, (IS_START, ENDTIME))
	cRoleMgr.BroadMsg()

def OnEndLianChongRebate(*param):
	'''
	连充返利_结束
	'''
	global IS_START
	if not IS_START:
		print "GE_EXC,end LianChongRebate while not start"
	IS_START = False
	
	cNetMessage.PackPyMsg(LianChongRebate_ActiveStatus_S, (IS_START, ENDTIME))
	cRoleMgr.BroadMsg()


#### 客户端请求 start
def OnGetTodayReward(role, msg):
	'''
	连充返利_请求领取今日充值达标奖励
	@param msg: rewardType
	'''
	if not IS_START:
		return
	
	targetRewardType = msg
	#今日已经领取
	lianChongRebateData = role.GetObj(EnumObj.LianChongRebateData)
	rewardRecordList = lianChongRebateData[3]
	if targetRewardType in rewardRecordList:
		return
	
	#该项未达成
	achieveDataDict = lianChongRebateData[1]
	if targetRewardType not in achieveDataDict:
		return
	
	#该项非今日达成
	today = cDateTime.Days()
	buyTimes, lastUpdateDay = achieveDataDict[targetRewardType]
	if lastUpdateDay != today:
		return
	
	#获取奖励配置
	rewardCfg = LianChongRebateConfig.GetLianChongRewardCfg(targetRewardType, role.GetLevel(), buyTimes)
	if not rewardCfg:
		print "GE_EXC,LianChongRebateMgr::OnGetTodayReward::can not get rewardCfg by targetRewardType(%s), roleLevel(%s), buyTimes(%s),role(%s)" % (targetRewardType, role.GetLevel(), buyTimes, role.GetRoleID())
		return
	
	prompt = GlobalPrompt.LianChongRebate_Tips_Head
	with Tra_LianChongRebate_GetTodayReward:
		#写领取记录
		rewardRecordList.append(targetRewardType)
		#获得奖励
		for coding, cnt in rewardCfg.rewardItems:
			role.AddItem(coding, cnt)
			prompt += GlobalPrompt.LianChongRebate_Tips_Item % (coding, cnt)
	
	#奖励提示
	role.Msg(2, 0, prompt)
	#同步角色最新活动相关数据
	role.SendObj(LianChongRebate_RoleActiveData_S, role.GetObj(EnumObj.LianChongRebateData))

def OnGetUnlockReward(role, msg):
	'''
	连充返利_请求领取解锁奖励
	@param msg: rewardType, rewardLevel
	'''
	if not IS_START:
		return
	
	rewardType, rewardLevel = msg	
	unlockRewardCfg = LianChongRebateConfig.GetUnlockRewardCfg(rewardType, rewardLevel, role.GetLevel())
	if not unlockRewardCfg:
		return
	
	lianChongRebateData = role.GetObj(EnumObj.LianChongRebateData)
	rewardRecord = lianChongRebateData[2]
	rewardTypeRecordSet = rewardRecord.get(rewardType, set())
	#已领取此项奖励
	if rewardLevel in rewardTypeRecordSet:
		return
	
	needBuyTimes = LianChongRebateConfig.GetUnLockCfgByTypeAndLevel(rewardType, rewardLevel)
	if needBuyTimes is None:
		return
	
	achieveDateDict = lianChongRebateData[1]
	#没有解锁此项累计奖励
	if (rewardType not in achieveDateDict) or achieveDateDict[rewardType][0] < needBuyTimes:
		return
	
	prompt = GlobalPrompt.LianChongRebate_Tips_Head
	with Tra_LianChongRebate_GetUnlockReward:
		#写领取记录
		rewardTypeRecordSet.add(rewardLevel)
		rewardRecord[rewardType] = rewardTypeRecordSet
		#奖励获得
		coding, cnt = unlockRewardCfg.rewardItem
		role.AddItem(coding, cnt)
		prompt += GlobalPrompt.LianChongRebate_Tips_Item % (coding, cnt)

	#奖励提示
	role.Msg(2, 0, prompt)
	#同步角色最新活动相关数据
	role.SendObj(LianChongRebate_RoleActiveData_S, role.GetObj(EnumObj.LianChongRebateData))

#### helper start
def UpdateLianChongAchieveData(role, forceSync = False):
	'''
	充值之后 or 玩家登录 :根据玩家充值数据和成就数据 更新玩家成就数据
	'''
	if not IS_START:
		return
	
	isUpdate = False
	today = cDateTime.Days()
	dayBuyRMB = role.GetDayBuyUnbindRMB_Q()
	lianChongAchieveData = role.GetObj(EnumObj.LianChongRebateData)[1]
	
	#遍历配置充值目标奖励 判断玩家是否今日已计算该目标达成 已达成却未标记的进行标记
	for rewardType, needBuyRMB in LianChongRebateConfig.LianChong_RewardCondition_Dict.iteritems():
		#充值数不足矣达成此项
		if dayBuyRMB < needBuyRMB:
			continue
		roleRewardTypeData = lianChongAchieveData.get(rewardType, None)
		#此项目标非首次达成  判断是否需要增加该项目标今日完成
		if not (roleRewardTypeData is None):
			buyTimes, lastUpdateDay = roleRewardTypeData
			if lastUpdateDay == today:
				continue
			elif lastUpdateDay > today:
				print "GE_EXC,UpdateLianChongAchieveData::lastUpdateDay(%s) > today(%s),role(%s)" % (lastUpdateDay, today, role.GetRoleID())
				continue
			else:
				isUpdate = True
				roleRewardTypeData = [buyTimes+1, today]
				lianChongAchieveData[rewardType] = roleRewardTypeData
		#此项目标首次达成 直接增加目标达成
		else:
			isUpdate = True
			lianChongAchieveData[rewardType] = [1,today]
	
	#登录强制同步 or 充值解锁有更新同步
	if forceSync or isUpdate:
		role.SendObj(LianChongRebate_RoleActiveData_S, role.GetObj(EnumObj.LianChongRebateData))

#### 事件 start
def InitAndUpdateVersion(role, param = None):
	'''
	根据活动版本号 和 记录的版本好 处理角色Obj数据
	'''
	if Environment.IsCross:
		return
	
	#1.确保key存在
	lianChongRebateData = role.GetObj(EnumObj.LianChongRebateData)
	if 1 not in lianChongRebateData:
		lianChongRebateData[1] = {}
	if 2 not in lianChongRebateData:
		lianChongRebateData[2] = {}
	if 3 not in lianChongRebateData:
		lianChongRebateData[3] = []
	
	#活动没开返回   活动开启触发 和 开启后触发 保证升级版本号数据逻辑
	if not IS_START:
		return
	
	#2.根据版本号处理活动数据
	roleVersion = role.GetI32(EnumInt32.LianChongRebateVersion)
	if VERSION == roleVersion:
		return
	
	if VERSION < roleVersion:
		print "GE_EXC, LianChongRebateMgr::UpdateVersion VERSION(%s) < roleVersion (%s)" % (VERSION, roleVersion)
		return 
	
	#重置相关数据	
	with Tra_LianChongRebate_UpdateVersion:
		#升级版本号
		role.SetI32(EnumInt32.LianChongRebateVersion, VERSION)
		#Obj 
		role.SetObj(EnumObj.LianChongRebateData, {1:{}, 2:{},3:[]})

def AfterRecharge(role, param):
	'''
	今日购买神石数改变之后
	'''
	if not IS_START:
		return
	UpdateLianChongAchieveData(role)

def OnSyncRoleOtherData(role,param):
	'''
	兼容活动放出去当日 维护之前玩家充值触发完成返利项
	'''
	if not IS_START:
		return
	
	#同步活动状态
	role.SendObj(LianChongRebate_ActiveStatus_S, (IS_START, ENDTIME))
	#尝试更新玩家活动数据并同步
	UpdateLianChongAchieveData(role, forceSync = True)

def OnDailyClear(role, param):
	'''
	每日清理  当日充值返利项领奖标志
	'''
	#清空领取记录
	role.GetObj(EnumObj.LianChongRebateData)[3] = []
	#同步最新
	role.SendObj(LianChongRebate_RoleActiveData_S, role.GetObj(EnumObj.LianChongRebateData))

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, OnDailyClear)
		Event.RegEvent(Event.Eve_InitRolePyObj, InitAndUpdateVersion)
	
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		
		Event.RegEvent(Event.Eve_AfterChangeDayBuyUnbindRMB_Q, AfterRecharge)
#		cRoleDataMgr.SetInt32Fun(EnumInt32.DayBuyUnbindRMB_Q, AfterRecharge)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("LianChongRebate_OnGetToDayReward", "连充返利_请求领取今日充值达标奖励"), OnGetTodayReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("LianChongRebate_OnGetUnlockReward", "连充返利_请求领取解锁奖励"), OnGetUnlockReward)
