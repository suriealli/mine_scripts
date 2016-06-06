#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.WangZheGongCe.ZaiXianLuxuryRewardMgr")
#===============================================================================
# 在线有豪礼 Mgr
#===============================================================================
import cRoleMgr
import cComplexServer
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Activity import CircularDefine
from Game.Activity.WangZheGongCe import ZaiXianLuxuryRewardConfig
from Game.Role.Data import  EnumInt8, EnumTempInt64, EnumDayInt8, EnumObj

idx_ZXLR = 1
OneMinute_Sec = 60

if "_HasLoad" not in dir():
	IS_START = False
	
	#格式  {(rewardIndex,levelRangeId,):[itemIndex,],}
	ZXLR_RewardRecord_S = AutoMessage.AllotMessage("ZXLR_RewardRecord_S", "在线有豪礼_领奖记录同步")
	
	Tra_ZaiXianLuxuryReward_GetReward = AutoLog.AutoTransaction("Tra_ZaiXianLuxuryReward_GetReward", "在线有豪礼_领奖奖励")
	
#### 活动控制 start
def OnStartZaiXianLuxuryReward(*param):
	'''
	在线有豪礼_开启
	'''
	_, circularType = param
	if CircularDefine.CA_ZaiXianLuxuryReward != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open ZaiXianJiangLi"
		return 
	
	IS_START = True
	
	#更新所有在线玩家 活动相关数据
	for tmpRole in cRoleMgr.GetAllRole():
		TryStartTick(tmpRole)

def OnEndZaiXianJiangLi(*param):
	'''
	在线有豪礼_结束
	'''
	_, circularType = param
	if CircularDefine.CA_ZaiXianLuxuryReward != circularType:
		return
	
	global IS_START
	if not IS_START:
		print "GE_EXC,end ZaiXianJiangLi while not start"
	IS_START = False

def OnGetReward(role, msg = None):
	'''
	在线有豪礼_请求领奖
	'''
	if not IS_START:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.WangZheGongCe_NeedLevel:
		return
	
	#没有剩余奖励项可以领取
	roleRewardIndex = role.GetDI8(EnumDayInt8.ZaiXianLuxuryRewardIndex)
	targetRewardIndex = roleRewardIndex + 1
	if targetRewardIndex > ZaiXianLuxuryRewardConfig.ZXLR_MAX_REWARDINDEX:
		return
	
	#目标奖励项不存在或者在线时长不足解锁
	onlineMins = role.GetI8(EnumInt8.ZaiXianLuxuryRewardOnLineMins) 
	needOnLineMins = ZaiXianLuxuryRewardConfig.GetNeedOnLineMinsByIndex(targetRewardIndex)
	if (needOnLineMins is None) or (onlineMins < needOnLineMins):
		return
	
	levelRangeId =ZaiXianLuxuryRewardConfig.GetLevelRangeIdByLevel(roleLevel)
	randomObj = ZaiXianLuxuryRewardConfig.GetRandomObjByLevelAndIndex(roleLevel, targetRewardIndex)
	if not randomObj:
		print "GE_EXC, ZaiXianLuxuryReward config error can not get randomObj by rolelevel(%s) and rewardIndex(%s) role(%s)" % (roleLevel, targetRewardIndex, role.GetRoleID())
		return
	
	rewardInfoList = randomObj.RandomMany(EnumGameConfig.ZaiXianLuxuryReward_RewardCnt)
	if len(rewardInfoList) != EnumGameConfig.ZaiXianLuxuryReward_RewardCnt:
		print "GE_EXC, ZaiXianLuxuryReward config error len(rewardInfoList)(%s) != (%s) by rolelevel(%s) and rewardIndex(%s) role(%s)" % (len(rewardInfoList), EnumGameConfig.ZaiXianLuxuryReward_RewardCnt, roleLevel, targetRewardIndex, role.GetRoleID())
		return
	
	prompt = GlobalPrompt.ZXLR_Tips_Head
	with Tra_ZaiXianLuxuryReward_GetReward:
		#设置最新领奖index
		role.SetDI8(EnumDayInt8.ZaiXianLuxuryRewardIndex, targetRewardIndex)
		#更新领取记录
		rewardRecordDict = role.GetObj(EnumObj.WangZheGongCe)[idx_ZXLR]
		recordKey = (targetRewardIndex, levelRangeId,)
		recordInfos = [itemIndex[0] for itemIndex in rewardInfoList]
		rewardRecordDict[recordKey] = recordInfos
		#重置在线时间
		role.SetI8(EnumInt8.ZaiXianLuxuryRewardOnLineMins, 0)
		#发奖励
		for _, coding, cnt in rewardInfoList:
			role.AddItem(coding, cnt)
			prompt += GlobalPrompt.Item_Tips % (coding, cnt)
	
	#奖励提示
	role.Msg(2, 0, prompt)
	#同步最新领奖记录
	role.SendObj(ZXLR_RewardRecord_S, rewardRecordDict)
	#重新尝试启动计时器
	TryStartTick(role)

#### 辅助 start
def TryStartTick(role):
	'''
	尝试启动在线计时器
	'''
	#活动非开启
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.WangZheGongCe_NeedLevel:
		return
	
	#今日剩余可领奖机会不足
	roleRewardIndex = role.GetDI8(EnumDayInt8.ZaiXianLuxuryRewardIndex)
	if roleRewardIndex >= ZaiXianLuxuryRewardConfig.ZXLR_MAX_REWARDINDEX:
		return
	
	#当前档倒计时跑够了 可以领奖无需启动计时器
	onlineMins = role.GetI8(EnumInt8.ZaiXianLuxuryRewardOnLineMins)
#	print "GE_EXC,TryStartTick::roleRewardIndex:(%s), onlineMins:(%s)" % (roleRewardIndex, onlineMins)
	nextOnLineMins = ZaiXianLuxuryRewardConfig.GetNeedOnLineMinsByIndex(roleRewardIndex+1)
	if onlineMins >= nextOnLineMins:
		return
	
	#如果有tick 先注销掉 (1.避免注册多个计时器  2.避免失效tickId)
	tickId = role.GetTI64(EnumTempInt64.ZaiXianLuxuryRewardTickId)
	if tickId:
		cComplexServer.UnregTick(tickId)
	
	#注册tick 保存
	tickId = cComplexServer.RegTick(OneMinute_Sec, OnTickTack, (role.GetRoleID(),roleRewardIndex + 1))
	role.SetTI64(EnumTempInt64.ZaiXianLuxuryRewardTickId, tickId)
	
def OnTickTack(callargv, regparam):
	'''
	计时器
	'''	
	roleId, targetRewardIndex = regparam
	role = cRoleMgr.FindRoleByRoleID(roleId)
	if role is None or role.IsKick() or role.IsLost():
		return
	
	#活动结束了 注销Tick
	if not IS_START:
		role.SetTI64(EnumTempInt64.ZaiXianLuxuryRewardTickId, 0)
	
	
	#在线时间增加一分钟
	onlineMins = role.GetI8(EnumInt8.ZaiXianLuxuryRewardOnLineMins)
	onlineMins += 1
	role.SetI8(EnumInt8.ZaiXianLuxuryRewardOnLineMins, onlineMins)
	
	#未达到可抽奖在线时间 继续 tick
	newTickId = 0
	needOnLineMins = ZaiXianLuxuryRewardConfig.GetNeedOnLineMinsByIndex(targetRewardIndex)
	if onlineMins < needOnLineMins:
		newTickId = cComplexServer.RegTick(OneMinute_Sec, OnTickTack, (role.GetRoleID(), targetRewardIndex))
	else:
		pass
	
	#保存 新的tickId
	role.SetTI64(EnumTempInt64.ZaiXianLuxuryRewardTickId, newTickId)
	
def OnInitRole(role, param):
	'''
	初始化角色
	'''
	wangZheGongCeData = role.GetObj(EnumObj.WangZheGongCe)
	if idx_ZXLR not in wangZheGongCeData:
		wangZheGongCeData[idx_ZXLR] = {}
		
def OnSyncRoleOtherData(role,param):
	'''
	兼容活动放出去当日 维护之前玩家充值触发完成返利项
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.WangZheGongCe_NeedLevel:
		return
	
	#尝试启动在线计时器
	TryStartTick(role)
	
	rewardRecordDict = role.GetObj(EnumObj.WangZheGongCe)[idx_ZXLR]
	role.SendObj(ZXLR_RewardRecord_S, rewardRecordDict)
	
def OnDailyClear(role, param):
	'''
	每日清理  当日充值返利项领奖标志
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.WangZheGongCe_NeedLevel:
		return
	
	#重置昨日计时器
	role.SetI8(EnumInt8.ZaiXianLuxuryRewardOnLineMins, 0)
	#如果有tick 先注销掉 (1.避免注册多个计时器  2.避免失效tickId)
	tickId = role.GetTI64(EnumTempInt64.ZaiXianLuxuryRewardTickId)
	if tickId:
		cComplexServer.UnregTick(tickId)
	
	#尝试启动在线计时器
	TryStartTick(role)
	
	#清除领奖记录
	rewardRecordDict = role.GetObj(EnumObj.WangZheGongCe)[idx_ZXLR]
	rewardRecordDict.clear()
	
	#同步最新领取记录
	role.SendObj(ZXLR_RewardRecord_S, rewardRecordDict)

def OnClientLost(role, param = None):
	'''
	客户端掉线 取消在线计时器
	'''
	tickId = role.GetTI64(EnumTempInt64.ZaiXianLuxuryRewardTickId)
	if tickId:
		cComplexServer.UnregTick(tickId)
	
	#清理tickId
	role.SetTI64(EnumTempInt64.ZaiXianLuxuryRewardTickId, 0)

def AfterLevelUp(role, param = None):
	'''
	角色升级尝试启动在线计时器
	'''
	#刚刚解锁玩法
	if role.GetLevel() == EnumGameConfig.WangZheGongCe_NeedLevel:
		TryStartTick(role) 
		#同步领取记录
		rewardRecordDict = role.GetObj(EnumObj.WangZheGongCe)[idx_ZXLR]
		role.SendObj(ZXLR_RewardRecord_S, rewardRecordDict)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.IsDevelop or Environment.EnvIsQQ() or Environment.EnvIsFT() or Environment.EnvIsTK() or Environment.EnvIsRU()):
		Event.RegEvent(Event.Eve_InitRolePyObj, OnInitRole)
		Event.RegEvent(Event.Eve_RoleDayClear, OnDailyClear)
		Event.RegEvent(Event.Eve_ClientLost, OnClientLost)
		Event.RegEvent(Event.Eve_BeforeExit, OnClientLost)
		Event.RegEvent(Event.Eve_AfterLevelUp, AfterLevelUp)
		
	if Environment.HasLogic and not Environment.IsCross and (Environment.IsDevelop or Environment.EnvIsQQ() or Environment.EnvIsFT() or Environment.EnvIsTK() or Environment.EnvIsRU()):
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartZaiXianLuxuryReward)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndZaiXianJiangLi)
		
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ZaiXianLuxuryReward_OnGetReward", "在线有豪礼_请求领取奖励"), OnGetReward)
