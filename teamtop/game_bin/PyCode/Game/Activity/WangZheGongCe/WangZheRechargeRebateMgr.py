#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.WangZheGongCe.WangZheRechargeRebateMgr")
#===============================================================================
# 王者公测充值返利Mgr
#===============================================================================
import random
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Time import Cron
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Activity import CircularDefine
from Game.SysData import WorldDataNotSync
from Game.Role.Data import EnumObj, EnumInt32, EnumInt8
from Game.Activity.WangZheGongCe import WangZheRechargeRebateConfig

IDX_LOTTERYRECORD = 7
IDX_REBATERECORD = 8

if "_HasLoad" not in dir():
	IS_START = False
	
	#格式 set([1,2])
	WangZheRechargeRebate_RebateRecord_S = AutoMessage.AllotMessage("WangZheRechargeRebate_RebateRecord_S", "王者公测充值返利_返利领取记录同步")
	#格式set([1,2])
	WangZheRechargeRebate_LotteryRecord_s = AutoMessage.AllotMessage("WangZheRechargeRebate_LotteryRecord_s", "王者公测充值返利_转盘抽奖记录同步")
	
	Tra_WangZheRechargeRebate_Refresh = AutoLog.AutoTransaction("Tra_WangZheRechargeRebate_Refresh", "王者公测充值返利_转盘刷新")
	Tra_WangZheRechargeRebate_Lottery = AutoLog.AutoTransaction("Tra_WangZheRechargeRebate_Lottery", "王者公测充值返利_抽奖")
	Tra_WangZheRechargeRebate_Rebate = AutoLog.AutoTransaction("Tra_WangZheRechargeRebate_Rebate", "王者公测充值返利_领取充值返利")

# 活动控制 start
def OnStartWangZheRechargeRebate(*param):
	'''
	王者公测充值返利_活动开启
	'''
	_, circularType = param
	if CircularDefine.CA_WangZheRechargeRebare != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open WangZheRechargeRebate"
		return 
	
	IS_START = True

def OnEndWangZheRechargeRebate(*param):
	'''
	王者公测充值返利_活动结束
	'''
	_, circularType = param
	if CircularDefine.CA_WangZheRechargeRebare != circularType:
		return
	
	global IS_START
	if not IS_START:
		print "GE_EXC,end WangZheRechargeRebate while not start"
	IS_START = False

#客户端请求 start
def OnOpenPanel(role, msg = None):
	'''
	王者公测充值返利_请求打开面板
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.WangZheGongCe_NeedLevel:
		return
	
	role.SendObj(WangZheRechargeRebate_LotteryRecord_s, role.GetObj(EnumObj.WangZheGongCe)[IDX_LOTTERYRECORD])

def OnLottery(role, msg):
	'''
	王者公测充值返利_请求抽奖	
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.WangZheGongCe_NeedLevel:
		return
	
	backId,_ = msg	
	needItemCoding = EnumGameConfig.WZRR_LotteryItemCoding
	if role.ItemCnt(needItemCoding) < 1:
		return
	
	curWaveIndex = role.GetI8(EnumInt8.WangZheRechargeRebateWaveIndex)
	curLevelRangeId = role.GetI8(EnumInt8.WangZheRechargeRebateLevelRangeId)
	curLotteryRecordSet = role.GetObj(EnumObj.WangZheGongCe)[IDX_LOTTERYRECORD]
	randomObj = WangZheRechargeRebateConfig.GetDynamicRandomObj(curWaveIndex, curLevelRangeId, curLotteryRecordSet)
	if len(randomObj.randomList) < 1:
		return
	
	rewardInfo = randomObj.RandomOne()
	waveIndex, levelRangeId, itemIndex, coding, cnt, isPrecious = rewardInfo
	prompt = GlobalPrompt.WZRR_Tips_Head
	with Tra_WangZheRechargeRebate_Lottery:
		#扣除抽奖消耗道具
		role.DelItem(needItemCoding, 1)
		#更新中奖记录
		curLotteryRecordSet.add(itemIndex)
		#获得奖励
		role.AddItem(coding, cnt)
		prompt += GlobalPrompt.Item_Tips % (coding, cnt)
		
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveWangZheRechargeRebateLottery, [waveIndex, levelRangeId, itemIndex])
		
		role.GetDayConsumeUnbindRMB()
	
	#获得提示
	role.Msg(2, 0, prompt)
	#珍稀奖励广播
	if isPrecious:
		cRoleMgr.Msg(1, 0, GlobalPrompt.WZRR_Tips_Precious % (role.GetRoleName(), coding, cnt))
	#中奖回调
	role.CallBackFunction(backId, itemIndex)	
	#同步最新中奖记录
	role.SendObj(WangZheRechargeRebate_LotteryRecord_s, curLotteryRecordSet)
	
	#本轮抽取完毕 重刷下一轮
	if len(curLotteryRecordSet) == EnumGameConfig.WZRR_LotteryCnt:
		WZRRC = WangZheRechargeRebateConfig
		newLevelRangeId = WZRRC.GetLevelRangeIdByLevel(role.GetLevel())
		newWaveIndex = random.randint(1,len(WZRRC.WZRR_LotteryConfig_Dict.keys()))
		
		with Tra_WangZheRechargeRebate_Refresh:
			role.SetI8(EnumInt8.WangZheRechargeRebateWaveIndex, newWaveIndex)
			role.SetI8(EnumInt8.WangZheRechargeRebateLevelRangeId, newLevelRangeId)
			curLotteryRecordSet.clear()
		
		#重置广播
		cRoleMgr.Msg(1, 0, GlobalPrompt.WZRR_Tips_GameOver % role.GetRoleName())
		#同步最新
		role.SendObj(WangZheRechargeRebate_LotteryRecord_s, curLotteryRecordSet)
		

def OnGetRebateReward(role, msg):
	'''
	王者公测充值返利_请求领取返利奖励
	@param msg: rewardIndex
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.WangZheGongCe_NeedLevel:
		return
	
	rewardIndex = msg
	rebateRecordSet = role.GetObj(EnumObj.WangZheGongCe)[IDX_REBATERECORD]
	if rewardIndex in rebateRecordSet:
		return
	
	rebateCfg = WangZheRechargeRebateConfig.WZRR_RebateConfig_Dict.get(rewardIndex)
	if not rebateCfg:
		return
	
	if role.GetDayBuyUnbindRMB_Q() < rebateCfg.needRechargeRMB:
		return
	
	prompt = GlobalPrompt.WZRR_Tips_HeadEx
	with Tra_WangZheRechargeRebate_Rebate:
		#更新返利领取记录
		rebateRecordSet.add(rewardIndex)
		#获得
		for coding, cnt in rebateCfg.rewardItems:
			role.AddItem(coding, cnt)
			prompt += GlobalPrompt.Item_Tips % (coding, cnt)
	
	#获得提示
	role.Msg(2, 0, prompt)
	#同步最新返利领取记录
	role.SendObj(WangZheRechargeRebate_RebateRecord_S, rebateRecordSet)
		

#辅助 start
def RefreshLotteryDesk(role, isSync, refreshVersion):
	'''
	刷新转盘  选择性同步客户端  并记录最近的刷新时间点
	@param isSync: 是否同步转盘状态给客户端
	@param isCalculate: 是否重算刷新点 PS:转完转盘自动刷新不重算 
	'''
	if not IS_START:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.WangZheGongCe_NeedLevel:
		return
	
	WZRRC = WangZheRechargeRebateConfig
	levelRangeId = WZRRC.GetLevelRangeIdByLevel(roleLevel)
	waveIndex = random.randint(1,len(WZRRC.WZRR_LotteryConfig_Dict.keys()))
	if (levelRangeId not in WZRRC.WZRR_LevelRange2ID_Dict) or (waveIndex not in WZRRC.WZRR_LotteryConfig_Dict):
		print "GE_EXC, WangZheRechargeRebateMgr::RefreshLotteryDesk config error levelRangeId(%s), waveIndex(%s) by roleLevel(%s),role(%s)" % (levelRangeId, waveIndex, roleLevel, role.GetRoleID())
		return
	
	with Tra_WangZheRechargeRebate_Refresh:
		#刷新转盘
		role.SetI8(EnumInt8.WangZheRechargeRebateWaveIndex, waveIndex)
		role.SetI8(EnumInt8.WangZheRechargeRebateLevelRangeId, levelRangeId)
		WZRRLotteryRecordSet = role.GetObj(EnumObj.WangZheGongCe)[IDX_LOTTERYRECORD]
		WZRRLotteryRecordSet.clear()
		#保存最新刷新版本号
		role.SetI32(EnumInt32.WZRRRefreshVersion, refreshVersion)
	
	if isSync:
		role.SendObj(WangZheRechargeRebate_LotteryRecord_s, WZRRLotteryRecordSet)

	
#事件 start
def OnInitRole(role, param = None):
	'''
	角色初始化相关key
	'''
	wangZheGongCeData = role.GetObj(EnumObj.WangZheGongCe)
	if IDX_LOTTERYRECORD not in wangZheGongCeData:
		wangZheGongCeData[IDX_LOTTERYRECORD] = set()
		
	if IDX_REBATERECORD not in wangZheGongCeData:
		wangZheGongCeData[IDX_REBATERECORD] = set()

def OnRoleDayClear(role, param = None):
	'''
	跨天处理 删除充值返利领取记录 
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.WangZheGongCe_NeedLevel:
		return
	
	nowVersion = WorldDataNotSync.GetWZGCRefreshVersion()
	if role.GetI32(EnumInt32.WZRRRefreshVersion) < nowVersion:
		RefreshLotteryDesk(role, True, nowVersion)
	
	
	#跨天重置返利领取记录
	WZRRRebateRecordSet = role.GetObj(EnumObj.WangZheGongCe)[IDX_REBATERECORD]
	WZRRRebateRecordSet.clear()
	
	#同步返利领取记录
	role.SendObj(WangZheRechargeRebate_RebateRecord_S, role.GetObj(EnumObj.WangZheGongCe)[IDX_REBATERECORD])

def OnSyncOtherData(role, param = None):
	'''
	角色上线 判断是否刷新转盘  同步充值返利领取记录
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.WangZheGongCe_NeedLevel:
		return
	
	
	nowVersion = WorldDataNotSync.GetWZGCRefreshVersion()
	if role.GetI32(EnumInt32.WZRRRefreshVersion) < nowVersion:
		RefreshLotteryDesk(role, False, nowVersion)
	
	#同步返利领奖记录
	role.SendObj(WangZheRechargeRebate_RebateRecord_S, role.GetObj(EnumObj.WangZheGongCe)[IDX_REBATERECORD])
		
def AfterLevelUp(role, param = None):
	'''
	角色升级解锁玩法 
	'''
	if not IS_START:
		return
	
	#并不是刚刚解锁玩法
	if role.GetLevel() != EnumGameConfig.WangZheGongCe_NeedLevel:
		return
	
	nowVersion = WorldDataNotSync.GetWZGCRefreshVersion()
	RefreshLotteryDesk(role, True, nowVersion)	

def AutoRefreshLotteryDesk():
	'''
	定点刷新转盘
	'''
	if not IS_START:
		return
	
	#刷新版本递增
	newVersion = WorldDataNotSync.GetWZGCRefreshVersion() + 1
	WorldDataNotSync.SetWZGCRefreshVersion(newVersion)
	
	for tmpRole in cRoleMgr.GetAllRole():
		if tmpRole.GetLevel() >= EnumGameConfig.WangZheGongCe_NeedLevel:
			RefreshLotteryDesk(tmpRole, True, newVersion)
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.WZRR_Msg_AutoRefresh)


if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.IsDevelop or Environment.EnvIsQQ() or Environment.EnvIsFT() or Environment.EnvIsTK() or Environment.EnvIsRU()):
		Event.RegEvent(Event.Eve_InitRolePyObj, OnInitRole)
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
	
	if Environment.HasLogic and not Environment.IsCross and (Environment.IsDevelop or Environment.EnvIsQQ() or Environment.EnvIsFT() or Environment.EnvIsTK() or Environment.EnvIsRU()):
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartWangZheRechargeRebate)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndWangZheRechargeRebate)
		
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncOtherData)
		Event.RegEvent(Event.Eve_AfterLevelUp, AfterLevelUp)
		
		Cron.CronDriveByMinute((2038, 1, 1), AutoRefreshLotteryDesk, H = "H == 0", M = "M == 0")
		Cron.CronDriveByMinute((2038, 1, 1), AutoRefreshLotteryDesk, H = "H == 12", M = "M == 0")
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WangZheRechargeRebate_OnOpenPanel", "王者公测充值返利_请求打开面板"), OnOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WangZheRechargeRebate_OnLottery", "王者公测充值返利_请求抽奖"), OnLottery)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WangZheRechargeRebate_OnGetRebateReward", "王者公测充值返利_请求领取返利奖励"), OnGetRebateReward)
		
