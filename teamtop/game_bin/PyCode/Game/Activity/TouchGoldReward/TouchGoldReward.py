#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.TouchGoldReward.TouchGoldReward")
#===============================================================================
# 点金大放送
#===============================================================================
import Environment
from Common.Message import AutoMessage
import cRoleMgr
from Game.Activity import CircularDefine, CircularActive
from Game.Persistence import Contain
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Activity.TouchGoldReward import TouchGoldRewardConfig
from Game.Role.Data import EnumObj
from ComplexServer.Log import AutoLog
from Game.Role import Event


#奖励加成buff枚举
EnumPrice = 1			#原石折扣buff
EnumScore = 2			#积分加成buff

if "_HasLoad" not in dir():
	IsStart = False
	
	#{1:set(已领取的奖励集合), 2:set(buff集合)}
	TouchGoldReward_Syn_Data = AutoMessage.AllotMessage("TouchGoldReward_Syn_Data", "同步点金大放送数据")
	#点金大放送期间点金次数
	TouchGoldCnt = AutoMessage.AllotMessage("TouchGoldCnt", "点金大放送点金次数")
	
	Tra_GetTouchGoldReward = AutoLog.AutoTransaction("Tra_GetTouchGoldReward", "获取点金大放送奖励")
	
def RequestReward(role, msg):
	'''
	客户端请求领取点金大放送奖励
	@param role:
	@param msg:
	'''
	global IsStart, TouchGoldReward_Dict
	if not IsStart: return
	
	if not TouchGoldReward_Dict.returnDB: return
	
	if role.GetLevel() < EnumGameConfig.TouchGoldRewardNeedLv:
		return
	
	index = msg
	roleId = role.GetRoleID()
	
	rewardDict = TouchGoldReward_Dict.get(roleId)
	if not rewardDict:
		return
	
	if index in rewardDict[1]:
		return
	
	cfg = TouchGoldRewardConfig.TouchGoldReward_Dict.get(index)
	if not cfg:
		return
	
	if rewardDict[3] < cfg.needCnt:
		return
	
	with Tra_GetTouchGoldReward:
		rewardDict[1].add(index)
		tips = None
		if cfg.rewardBuffIndex:
			rewardDict[2].add(cfg.rewardBuffIndex)
			tips = GlobalPrompt.Reward_Tips + GlobalPrompt.ReturnTouchGoldRewardBuffTips(cfg.rewardBuffIndex) if GlobalPrompt.ReturnTouchGoldRewardBuffTips(cfg.rewardBuffIndex) else None
			
		if cfg.rewardStone:
			from Game.Activity.TouchGold import TouchGold
			role.GetObj(EnumObj.ToouchGoldData)[cfg.rewardStone[0]] = role.GetObj(EnumObj.ToouchGoldData).get(cfg.rewardStone[0], 0) + cfg.rewardStone[1]
			TouchGold.SynStoneData(role)
			coding = TouchGold.MSG_TIPS_DICT.get(cfg.rewardStone[0])
			tips = GlobalPrompt.Reward_Tips + GlobalPrompt.Item_Tips % (coding, cfg.rewardStone[1]) if coding else None
			
		if cfg.rewardItems:
			tips = GlobalPrompt.Reward_Tips
			for item in cfg.rewardItems:
				role.AddItem(*item)
			tips += GlobalPrompt.Item_Tips % item
		
		TouchGoldReward_Dict.changeFlag = True
		
		AutoLog.LogBase(roleId, AutoLog.eveTouchGoldReward, index)
	
	role.SendObj(TouchGoldReward_Syn_Data, {1:rewardDict[1], 2:rewardDict[2]})
	
	if tips:
		role.Msg(2, 0, tips)
#===============================================================================
# buff
#===============================================================================
def AddBuff(role, index):
	global IsStart, TouchGoldReward_Dict
	if not IsStart:
		return
	if not TouchGoldReward_Dict.returnDB:
		return
	if role.GetLevel() < EnumGameConfig.TouchGoldRewardNeedLv:
		return
	
	cfg = TouchGoldRewardConfig.TouchGoldReward_Dict.get(index)
	if not cfg:
		return
	if not cfg.rewardBuffIndex:
		return
	
	roleId = role.GetRoleID()
	rewardDict = TouchGoldReward_Dict.get(roleId)
	if not rewardDict:
		return
	
	if index in rewardDict[1]:
		return
	
	rewardDict[1].add(index)
	rewardDict[2].add(cfg.rewardBuffIndex)
	tips = GlobalPrompt.Reward_Tips + GlobalPrompt.ReturnTouchGoldRewardBuffTips(cfg.rewardBuffIndex) if GlobalPrompt.ReturnTouchGoldRewardBuffTips(cfg.rewardBuffIndex) else None
	
	role.SendObj(TouchGoldReward_Syn_Data, {1:rewardDict[1], 2:rewardDict[2]})
	
	if tips:
		role.Msg(2, 0, tips)
	
def StonePriceBuffer(role, price):
	global TouchGoldReward_Dict
	if not TouchGoldReward_Dict.returnDB:
		return price
	roleId = role.GetRoleID()
	if roleId not in TouchGoldReward_Dict or EnumPrice not in TouchGoldReward_Dict[roleId][2]:
		return price
	
	return price * EnumGameConfig.TouchGoldRewardDiscount / 10

def ScoreBuffer(role, score):
	global TouchGoldReward_Dict
	if not TouchGoldReward_Dict.returnDB:
		return score
	
	roleId = role.GetRoleID()
	if roleId not in TouchGoldReward_Dict or EnumScore not in TouchGoldReward_Dict[roleId][2]:
		return score
	
	return score * EnumGameConfig.TouchGoldRewardMulti
#===============================================================================
# 活动开关
#===============================================================================
def Start(param1, param2):
	if param2 != CircularDefine.CA_TouchGoldReward:
		return
	
	global IsStart
	if IsStart:
		print "GE_EXC, TouchGoldReward is already Start"
	IsStart = True
	
	#活动开启的时候再检查一遍是否需要清理数据
	global TouchGoldReward_Dict
	if not TouchGoldReward_Dict.returnDB:
		print 'GE_EXC, TouchGoldReward not return db when start'
		return
	
	for _, (activeType, endSec) in CircularActive.CircularActiveCache_Dict.iteritems():
		if activeType != param2:
			continue
		if endSec != TouchGoldReward_Dict.get(0, 0):
			TouchGoldReward_Dict.clear()
			break
	TouchGoldReward_Dict[0] = endSec
	TouchGoldReward_Dict.changeFlag = True
	
def End(param1, param2):
	if param2 != CircularDefine.CA_TouchGoldReward:
		return
	
	global IsStart
	if not IsStart:
		print "GE_EXC, TouchGoldReward is already End"
	IsStart = False
	
	global TouchGoldReward_Dict
	if not TouchGoldReward_Dict.returnDB:
		print 'GE_EXC, TouchGoldReward not return db when end'
		return
	TouchGoldReward_Dict.clear()
	
#===============================================================================
# 数据载回
#===============================================================================
def AfterLoad():
	global TouchGoldReward_Dict
	if 0 in TouchGoldReward_Dict:
		return
	TouchGoldReward_Dict[0] = 0
	TouchGoldReward_Dict.changeFlag = True
	
#===============================================================================
# 事件
#===============================================================================
def SyncRoleOtherData(role, param):
	global IsStart, TouchGoldReward_Dict
	if not IsStart:
		return
	if not TouchGoldReward_Dict.returnDB:
		return
	
	touchData = TouchGoldReward_Dict.get(role.GetRoleID(), {})
	role.SendObj(TouchGoldCnt, touchData.get(3, 0))
	role.SendObj(TouchGoldReward_Syn_Data, {1:touchData.get(1, set()), 2:touchData.get(2, set())})
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		TouchGoldReward_Dict = Contain.Dict("TouchGoldReward_Dict", (2038, 1, 1), AfterLoad)
		
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		Event.RegEvent(Event.Eve_StartCircularActive, Start)
		Event.RegEvent(Event.Eve_EndCircularActive, End)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TouchGoldReward_Reward", "客户端请求领取点金大放送奖励"), RequestReward)
	
	
