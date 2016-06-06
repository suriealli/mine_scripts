#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DailyMountLottery.DailyMountLotteryMgr")
#===============================================================================
# 天马行空
#===============================================================================
import cRoleMgr
import Environment
from Common.Other import GlobalPrompt
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Role.Data import EnumInt32
from Game.Activity import CircularDefine
from Game.Activity.DailyMountLottery import DailyMountLotteryConfig

if "_HasLoad" not in dir():
	IS_START = False	#天马行空开关标志
	
	Tra_DML_Lottery = AutoLog.AutoTransaction("Tra_DML_Lottery","天马行空抽奖")

def DaliyMountLotteryStart(*param):
	'''
	天马行空开启
	'''
	_, circularType = param
	if CircularDefine.CA_DaliyMountLottery != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open DaliyMountLottery"
		return
		
	IS_START = True

def DaliyMountLotteryEnd(*param):
	'''
	天马行空结束
	'''
	_, circularType = param
	if CircularDefine.CA_DaliyMountLottery != circularType:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC, end DaliyMountLottery while not start"
		return
		
	IS_START = False

def OnDMLLottery(role, msg = None):
	'''
	天马行空抽奖
	'''
	if not IS_START:
		return
	
	lotteryTimes = role.GetI32(EnumInt32.DailyMountLotteryTimes) + 1
	lotteryCfg = DailyMountLotteryConfig.GetLotteryCfgByTimes(lotteryTimes)
	if not lotteryCfg:
		print "GE_EXC,OnDMLLottery :: lotteryCfg is None for lotteryTimes(%s)" % lotteryTimes
		return
	
	lotteryAccTimes = role.GetI32(EnumInt32.DailyMountLotteryAccTimes) + 1
	lotteryAccCfg = DailyMountLotteryConfig.GetLotteryCfgByTimes(lotteryAccTimes)
	if not lotteryAccCfg:
		print "GE_EXC, OnDMLLottery :: lotteryAccCfg is None for lotteryAccTimes(%s)" % lotteryAccTimes
		return
	
	#未抽中特殊奖励累计次数对应随机奖励池&神石消耗 替换 今日抽奖总次数对应随机奖励池&神石消耗
	if lotteryTimes != lotteryAccTimes:
		lotteryCfg.randomer = lotteryAccCfg.randomer
		lotteryCfg.needRMB = lotteryAccCfg.needRMB
		
	if role.GetUnbindRMB() < lotteryCfg.needRMB:
		return
	
	if not lotteryCfg.randomer:
		print "GE_EXC,OnDMLLottery::lotteryCfg.randomer is None", lotteryCfg
		return
		
	#process
	randomCoding, randomCnt, IsBroad = lotteryCfg.randomer.RandomOne()
	rewardPrompt = GlobalPrompt.DML_Tips_Head + GlobalPrompt.DML_Tips_Item % (randomCoding, randomCnt) 
	with Tra_DML_Lottery:
		#扣神石
		role.DecUnbindRMB(lotteryCfg.needRMB)
		#增加今日抽奖总次数
		role.SetI32(EnumInt32.DailyMountLotteryTimes, lotteryTimes)
		#根据是否抽中特殊奖励 更新未抽中特殊奖励累积次数
		if IsBroad:
			role.SetI32(EnumInt32.DailyMountLotteryAccTimes, 0)
		else:
			role.SetI32(EnumInt32.DailyMountLotteryAccTimes, lotteryAccTimes)
		#获得随机奖励
		role.AddItem(randomCoding, randomCnt)
		#获得额外奖励
		if lotteryCfg.extraItem:
			for extraCoding, extraCnt in lotteryCfg.extraItem:
				role.AddItem(extraCoding, extraCnt)
				rewardPrompt += GlobalPrompt.DML_Tips_Item % (extraCoding, extraCnt)
	
	role.Msg(2, 0, rewardPrompt)	
	if IsBroad:
		broadPrompt = GlobalPrompt.DML_Broadcast_Mount % (role.GetRoleName(), randomCoding, randomCnt)
		cRoleMgr.Msg(1, 0, broadPrompt)
		
def OnRoleDayClear(role, param):
	'''
	每日清理天马行空抽奖次数
	'''
	role.SetI32(EnumInt32.DailyMountLotteryTimes, 0)
	role.SetI32(EnumInt32.DailyMountLotteryAccTimes, 0)

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
	
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, DaliyMountLotteryStart)
		Event.RegEvent(Event.Eve_EndCircularActive, DaliyMountLotteryEnd)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DailyMountLottry_OnDMLLottery", "请求天马行空抽奖"), OnDMLLottery)