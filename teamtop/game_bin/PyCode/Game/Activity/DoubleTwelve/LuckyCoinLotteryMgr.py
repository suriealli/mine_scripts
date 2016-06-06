#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DoubleTwelve.LuckyCoinLotteryMgr")
#===============================================================================
# 好运币专场Mgr
#===============================================================================
import cRoleMgr
import Environment
from Util import Random
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event, Call
from Game.Activity import CircularDefine
from Game.Role.Data import EnumDayInt8, EnumInt16, EnumDayInt1
from Game.Activity.DoubleTwelve import LuckyCoinLotteryConfig

if "_HasLoad" not in dir():
	IS_START = False
	
	Tra_LuckyCoin_Lottery = AutoLog.AutoTransaction("Tra_LuckyCoin_Lottery", "好运币专场抽奖")
	Tra_LuckyCoin_LotteryReset = AutoLog.AutoTransaction("Tra_LuckyCoin_LotteryReset", "好运币专场重置转盘")
	
	LuckyCoin_LotteryResult_SB = AutoMessage.AllotMessage("LuckyCoin_LotteryResult_SB", "好运币专场抽奖结果")
	
#### 活动控制 start ####
def OnStartLuckyCoin(*param):
	'''
	开启活动
	'''
	_, circularType = param
	if CircularDefine.CA_DTLuckyCoinLottery != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open LoveTogether"
		return
		
	IS_START = True

def OnEndLuckyCoin(*param):
	'''
	结束活动
	'''
	_, circularType = param
	if CircularDefine.CA_DTLuckyCoinLottery != circularType:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC, end LoveTogether while not start"
		return
		
	IS_START = False

#### 请求 start ####
def OnOpenPanel(role, msg = None):
	'''
	打开面板 判断是否需要重新采集玩家当前所属等级区段对应的区段ID
	1.当前没有等级区段ID
	2.当前转盘没有抽奖
	3.当前等级不对应当前区段ID
	总之 转盘没有抽奖就重置等级区段ID
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.DoubleTwelve_NeedLevel:
		return
	
	backId,_ = msg
	#转盘没抽奖 采集重算保存
	lotteryRewardRecord = role.GetI16(EnumInt16.LuckyCoinLotteryRewardRecord)
	if not lotteryRewardRecord:
		roleLevel = role.GetLevel()
		levelRangeId = LuckyCoinLotteryConfig.GetRangeIdByLevel(roleLevel)
		role.SetDI8(EnumDayInt8.LuckyCoinLotteryLevelRangeId, levelRangeId)
	
	#回调
	levelRangeId = role.GetDI8(EnumDayInt8.LuckyCoinLotteryLevelRangeId)	
	print backId, levelRangeId
	role.CallBackFunction(backId, levelRangeId)

def OnLottery(role, msg = None):
	'''
	好运币专场抽奖
	'''
	if not IS_START:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.DoubleTwelve_NeedLevel:
		return
	
	#当前转盘需要重置才能抽奖
	lotteryRewardRecord = role.GetI16(EnumInt16.LuckyCoinLotteryRewardRecord)
	if lotteryRewardRecord >= EnumGameConfig.LuckyCoinLotter_AllLotteryRecord:
		return
	
	#好运币是否足够本次抽奖
	currentTimes = role.GetDI8(EnumDayInt8.LuckyCoinLotteryCurrentTimes)
	needLuckyCoin = LuckyCoinLotteryConfig.GetCostByLotteryTimes(currentTimes + 1)
	if role.ItemCnt(EnumGameConfig.LuckyCoinLotter_LuckyCoinCoding) < needLuckyCoin:
		return
	
	#构建本次抽奖随机器
	levelRangeId = role.GetDI8(EnumDayInt8.LuckyCoinLotteryLevelRangeId)
	lotteryRewardDict = LuckyCoinLotteryConfig.LuckyCoinLottery_LotteryRewardConfig_Dict.get(levelRangeId)
	if not lotteryRewardDict:
		print "GE_EXC,can not get lotteryItemsDict with levelRangeId(%s)" % levelRangeId
		return
	
	randomObj = Random.RandomRate()
	for rewardId, rewardCfg in  lotteryRewardDict.iteritems():
		rewardIndex = rewardCfg.rewardIndex
		coding, cnt = rewardCfg.rewardItem
		isPrecious = rewardCfg.isPrecious
		rateValue = rewardCfg.rateValue
		#未抽取该奖励 入选
		if not (lotteryRewardRecord & pow(2, rewardIndex)):
			randomObj.AddRandomItem(rateValue, (rewardId, rewardIndex, coding, cnt, isPrecious))
	
	#随机奖励
	randomReward = randomObj.RandomOne()
	rewardId, rewardIndex, coding, cnt, isPrecious = randomReward
	if not randomReward:
		print "GE_EXC, can not random reward with randomObj.randomList(%s),lotteryRewardRecord(%s)" % (randomObj.randomList, lotteryRewardRecord)
		return
	
	#process
	roleId = role.GetRoleID()
	roleName = role.GetRoleName()
	with Tra_LuckyCoin_Lottery:
		#扣除好运币消耗
		role.DelItem(EnumGameConfig.LuckyCoinLotter_LuckyCoinCoding, needLuckyCoin)
		#更新转盘状态
		role.IncI16(EnumInt16.LuckyCoinLotteryRewardRecord, pow(2, rewardIndex))
		#更新本轮次数
		role.IncDI8(EnumDayInt8.LuckyCoinLotteryCurrentTimes, 1)
	
	role.SendObjAndBack(LuckyCoin_LotteryResult_SB, randomReward, 8, LotteryCallBack, (roleId, roleName, randomReward))
def OnResetLottery(role, msg = None):
	'''
	好运币专场重置转盘
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.DoubleTwelve_NeedLevel:
		return
	
	backId,_ = msg
	
	needUnbindRMB = 0
	#已使用了免费次数
	if role.GetDI1(EnumDayInt1.LuckyCoinResetFree):
		resetTimes = role.GetDI8(EnumDayInt8.LuckyCoinLotteryResetTimes)
		needUnbindRMB = LuckyCoinLotteryConfig.GetResetCostByResetTimes(resetTimes + 1)
	
	#神石不足
	if role.GetUnbindRMB() < needUnbindRMB:
		return
	
	with Tra_LuckyCoin_LotteryReset:
		#扣除神石 更新对应重置次数
		if needUnbindRMB > 0:
			role.DecUnbindRMB(needUnbindRMB)
			role.IncDI8(EnumDayInt8.LuckyCoinLotteryResetTimes, 1)
		else:
			role.SetDI1(EnumDayInt1.LuckyCoinResetFree, 1)
		#重置转盘 本轮抽奖数
		role.SetI16(EnumInt16.LuckyCoinLotteryRewardRecord, 0)
		role.SetDI8(EnumDayInt8.LuckyCoinLotteryCurrentTimes, 0)
	
	#重置完毕 回调客户端
	role.CallBackFunction(backId, None)

#### 处理 start ####
def LotteryCallBack(role, callArgv, regparam):
	'''
	抽奖回调
	'''
	roleId, roleName, randomReward = regparam
	_, _, coding, cnt, isPrecious = randomReward
	
	#珍贵奖励广播
	if isPrecious:
		preciousMsg = GlobalPrompt.LuckyCoinLottery_Precious_Msg % (roleName, coding, cnt)
		cRoleMgr.Msg(11, 0, preciousMsg)
	
	Call.LocalDBCall(roleId, RealAward, (coding, cnt))

def RealAward(role, param):
	'''
	抽奖实际获得处理
	'''
	coding, cnt = param
	rewardPrompt = GlobalPrompt.LuckyCoinLottery_Tips_Head
	with Tra_LuckyCoin_Lottery:
		role.AddItem(coding, cnt)
		rewardPrompt += GlobalPrompt.LuckyCoinLottery_Tips_Item % (coding, cnt)
	
	role.Msg(2, 0, rewardPrompt)

#def IsNeedResetLottery(role):
#	'''
#	检测玩家转盘状态是否需要重置
#	'''
#	isFull = True
#	rewardRecord = role.GetI16(EnumInt16.LuckyCoinLotteryRewardRecord)
#	for rewardIndex in xrange(1, EnumGameConfig.LuckyCoinLotter_AwardNum + 1):
#		if not rewardRecord & pow(2, rewardIndex):
#			isFull = False
#			break
#	
#	return isFull

#### 事件 start ####
def OnRoleDayClear(role, param):
	'''
	每日重置
	'''
	#重置转盘
	role.SetI16(EnumInt16.LuckyCoinLotteryRewardRecord, 0)

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
	
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartLuckyCoin)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndLuckyCoin)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("LuckyCoin_OnOpenPanel", "好运币专场打开面板"), OnOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("LuckyCoin_OnLottery", "好运币专场抽奖"), OnLottery)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("LuckyCoin_OnResetLottery", "好运币专场重置转盘"), OnResetLottery)