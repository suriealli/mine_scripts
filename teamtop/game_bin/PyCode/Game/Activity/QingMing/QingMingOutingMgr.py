#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.QingMing.QingMingOutingMgr")
#===============================================================================
# 清明踏青 Mgr
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Activity import CircularDefine
from Game.Role.Data import EnumObj, EnumInt16
from Game.Activity.QingMing import QingMingOutingConfig

if "_HasLoad" not in dir():
	IS_START = False
	
	QMO_DesktopState_S = AutoMessage.AllotMessage("QMO_DesktopState_S", "清明踏青_翻牌状态_同步")
	QMO_UnlockRewardRecord_S = AutoMessage.AllotMessage("QMO_UnlockRewardRecord_S", "清明踏青_解锁奖励领取记录_同步")
	
	Tra_QMO_Lottery = AutoLog.AutoTransaction("Tra_QMO_Lottery", "清明踏青_单次翻牌抽奖")
	Tra_QMO_LotteryAll = AutoLog.AutoTransaction("Tra_QMO_LotteryAll", "清明踏青_批量翻牌抽奖")
	
	Tra_QMO_GetUnlockReward = AutoLog.AutoTransaction("Tra_QMO_GetUnlockReward", "清明踏青_领取累计翻牌解锁奖励")
	Tra_QMO_ResetDesktop = AutoLog.AutoTransaction("Tra_QMO_ResetDesktop","清明踏青_重置所有翻牌")

#### 活动控制  start ####
def OnStartQingMingOuting(*param):
	'''
	开启活动
	'''
	_, circularType = param
	if CircularDefine.CA_QingMingOuting != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open QingMingOuting"
		return
		
	IS_START = True

def OnEndQingMingOuting(*param):
	'''
	结束活动
	'''
	_, circularType = param
	if CircularDefine.CA_QingMingOuting != circularType:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC, end QingMingOuting while not start"
		return
		
	IS_START = False

#### 客户端请求 start
def OnOpenPanel(role, msg = None):
	'''
	清明踏青_请求打开界面
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.QMO_NeedLevel:
		return
	
	role.SendObj(QMO_DesktopState_S, role.GetObj(EnumObj.QingMingData)[1])
	
def OnLottery(role, msg):
	'''
	清明踏青_请求翻牌抽奖
	@param msg: pos  
	'''
	if not IS_START:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.QMO_NeedLevel:
		return
	
	#目标牌位不存在
	targetPos = msg
	if targetPos not in EnumGameConfig.QMO_PosList:
		return
	
	#对应牌位已抽奖
	QingMingLotteryData = role.GetObj(EnumObj.QingMingData)[1]
	if targetPos in QingMingLotteryData:
		return
	
	#神石不足
	if role.GetUnbindRMB() < EnumGameConfig.QMO_LotteryPrice:
		return
	
	randomObj = QingMingOutingConfig.GetRadomObjByLevel(roleLevel)
	if not randomObj:
		print "GE_EXC, QingMingOutingMgr OnLottery can not get randomObj by roleLevel(%s),roleId(%s)" % (roleLevel, role.GetRoleID())
		return
	
	randomReward = randomObj.RandomOne()
	if not randomReward:
		print "GE_EXC, QingMingOutingMgr OnLottery can not random Reward with roleLevel(%s),roleId(%s)" % (roleLevel, role.GetRoleID())
		return
	
	isAll = False
	prompt = GlobalPrompt.QMO_Tips_Head
	rewardId, coding, cnt, isPrecious = randomReward
	with Tra_QMO_Lottery:
		#写翻牌状态
		QingMingLotteryData[targetPos] = rewardId
		#扣除幸运钥匙
		role.DecUnbindRMB(EnumGameConfig.QMO_LotteryPrice)
		#增加今日翻牌抽奖次数
		role.IncI16(EnumInt16.QingMingOutingLotteryCnt, 1)
		#获得抽奖奖励
		role.AddItem(coding, cnt)
		prompt += GlobalPrompt.QMO_Tips_Item % (coding, cnt)
		#判断幸运钥匙获得
		if len(QingMingLotteryData) >= len(EnumGameConfig.QMO_PosList):
			isAll = True
	
	#同步最新牌面状态
	role.SendObj(QMO_DesktopState_S, QingMingLotteryData)
	
	#获奖提示
	role.Msg(2, 0, prompt)
	#幸运钥匙获得
	if isAll:
		with Tra_QMO_Lottery:
			role.AddItem(EnumGameConfig.QMO_LotteryItemCoding, 1)
			role.Msg(2, 0, GlobalPrompt.QMO_Tips_LuckyKey % (EnumGameConfig.QMO_LotteryItemCoding, 1))
	#珍惜奖励广播
	if isPrecious:
		cRoleMgr.Msg(11, 0, GlobalPrompt.QMO_MSG_Precious % (role.GetRoleName(), coding, cnt))

def OnLotteryAll(role, msg = None):
	'''
	清明踏青_请求翻开所有剩余牌抽奖
	'''
	if not IS_START:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.QMO_NeedLevel:
		return
	
	#剩余可抽奖牌位不足
	QingMingLotteryData = role.GetObj(EnumObj.QingMingData)[1]
	remainPos = len(EnumGameConfig.QMO_PosList) - len(QingMingLotteryData) 
	if remainPos < 1:
		return
	
	#剩余神石不足
	needUnbindRMB = remainPos * EnumGameConfig.QMO_LotteryPrice
	if role.GetUnbindRMB() < needUnbindRMB:
		return
	
	randomObj = QingMingOutingConfig.GetRadomObjByLevel(roleLevel)
	if not randomObj:
		print "GE_EXC, QingMingOutingMgr OnLotteryAll can not get randomObj by roleLevel(%s),roleId(%s)" % (roleLevel, role.GetRoleID())
		return
	
	rewardDict = {}			#缓存奖励 道具
	rewardRecordDict = {}	#缓存翻牌中奖记录
	preciousRewardDict = {}	#缓存珍贵奖励
	for targetPos in EnumGameConfig.QMO_PosList:
		if targetPos in QingMingLotteryData:
			continue
		
		randomReward = randomObj.RandomOne()
		if not randomReward:
			print "GE_EXC, QingMingOutingMgr OnLotteryAll can not random Reward with roleLevel(%s),roleId(%s)" % (roleLevel, role.GetRoleID())
			continue
		
		rewardId, coding, cnt, isPrecious = randomReward
		rewardRecordDict[targetPos] = rewardId
		
		if coding in rewardDict:
			rewardDict[coding] += cnt
		else:
			rewardDict[coding] = cnt
		
		if isPrecious:
			if coding in preciousRewardDict:
				preciousRewardDict[coding] += cnt
			else:
				preciousRewardDict[coding] = cnt
	
	#没有随机获得奖励道具 (正常不会出现 此处以防万一 加此判断)
	if len(rewardDict) < 1:
		return
	
	isAll = False
	prompt = GlobalPrompt.QMO_Tips_Head
	with Tra_QMO_LotteryAll:
		#写翻牌抽奖记录
		QingMingLotteryData.update(rewardRecordDict)
		#扣除神石
		role.DecUnbindRMB(needUnbindRMB)
		#增加今日翻牌抽奖次数
		role.IncI16(EnumInt16.QingMingOutingLotteryCnt, remainPos)
		#抽奖获得
		for coding, cnt in rewardDict.iteritems():
			role.AddItem(coding, cnt)
			prompt += GlobalPrompt.QMO_Tips_Item % (coding, cnt)
		#判断幸运钥匙获得
		if len(QingMingLotteryData) >= len(EnumGameConfig.QMO_PosList):
			isAll = True
	
	#同步最新牌面状态
	role.SendObj(QMO_DesktopState_S, QingMingLotteryData)
	
	#获奖提示
	role.Msg(2, 0, prompt)
	#幸运钥匙获得
	if isAll:
		with Tra_QMO_Lottery:
			role.AddItem(EnumGameConfig.QMO_LotteryItemCoding, 1)
			role.Msg(2, 0, GlobalPrompt.QMO_Tips_LuckyKey % (EnumGameConfig.QMO_LotteryItemCoding, 1))
	#珍惜奖励广播
	if len(preciousRewardDict) >= 1:
		for coding, cnt in preciousRewardDict.iteritems():
			cRoleMgr.Msg(11, 0, GlobalPrompt.QMO_MSG_Precious % (role.GetRoleName(), coding, cnt))	
	
def OnGetUnlockReward(role, msg):
	'''
	清明踏青_请求领取累计翻牌解锁奖励
	@param msg: rewardIndex
	'''
	if not IS_START:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.QMO_NeedLevel:
		return
	
	#对应配置不存在
	rewardIndex = msg
	unlockRewardCfg = QingMingOutingConfig.GetUnlockRewardCfgByLevel(roleLevel, rewardIndex)
	if not unlockRewardCfg:
		return

	#已领取对应奖励
	unlockRewardRecordSet = role.GetObj(EnumObj.QingMingData)[2] 
	if rewardIndex in unlockRewardRecordSet:
		return
	
	#未解锁
	if role.GetI16(EnumInt16.QingMingOutingLotteryCnt) < unlockRewardCfg.needValue:
		return
	
	prompt = GlobalPrompt.QMO_Tips_UnlockRewardHead
	with Tra_QMO_GetUnlockReward:
		#写领取记录
		unlockRewardRecordSet.add(rewardIndex)
		#奖励获得
		for coding, cnt in unlockRewardCfg.rewardItems:
			role.AddItem(coding, cnt)
			prompt += GlobalPrompt.QMO_Tips_Item % (coding, cnt)
	
	#同步领取记录
	role.SendObj(QMO_UnlockRewardRecord_S, unlockRewardRecordSet)
	
	#提示
	role.Msg(2, 0, prompt)
	
def OnResetDesktop(role, msg = None):
	'''
	清明踏青_请求重置所有翻牌
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.QMO_NeedLevel:
		return
	
	#未翻开任何牌位
	QingMingLotteryData = role.GetObj(EnumObj.QingMingData)[1]
	if len(QingMingLotteryData) < 1:
		return
	
	with Tra_QMO_ResetDesktop:
		#写log
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveQMOResetDesktop, QingMingLotteryData)
		#重置牌面
		QingMingLotteryData.clear()
	
	#同步最新牌面
	role.SendObj(QMO_DesktopState_S, QingMingLotteryData)

def OnRoleDayClear(role, param = None):
	'''
	跨天清理 今日累计翻牌解锁奖励领取记录
	'''
	unlockRewardRecordSet = role.GetObj(EnumObj.QingMingData)[2]
	unlockRewardRecordSet.clear()
	
	#重置今日翻牌次数
	role.SetI16(EnumInt16.QingMingOutingLotteryCnt, 0)
	
	if not Environment.IsCross:
		role.SendObj(QMO_UnlockRewardRecord_S, unlockRewardRecordSet)

def OnSyncRoleOtherData(role, param = None):
	'''
	上线同步翻牌累计解锁奖励领取记录
	'''
	role.SendObj(QMO_UnlockRewardRecord_S, role.GetObj(EnumObj.QingMingData)[2])

def OnInitRole(role, param = None):
	'''
	初始化相关key
	'''
	QingMingData = role.GetObj(EnumObj.QingMingData)
	if 1 not in QingMingData:
		QingMingData[1] = {}
	
	if 2 not in QingMingData:
		QingMingData[2] = set()

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
		
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_InitRolePyObj, OnInitRole)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartQingMingOuting)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndQingMingOuting)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QMO_OnOpenPanel", "清明踏青_请求打开界面"), OnOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QMO_OnLottery", "清明踏青_请求翻牌抽奖"), OnLottery)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QMO_OnLotteryAll", "清明踏青_请求翻开所有剩余牌抽奖"), OnLotteryAll)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QMO_OnGetUnlockReward", "清明踏青_请求领取累计翻牌解锁奖励"), OnGetUnlockReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QMO_OnResetDesktopState", "清明踏青_请求重置所有翻牌"), OnResetDesktop)