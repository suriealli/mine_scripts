#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.NationDay.ExchangeReward")
#===============================================================================
# 奖励兑换
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Activity import CircularDefine
from Game.Activity.NationDay import ExchangeRewardConfig

if "_HasLoad" not in dir():
	IS_START = False	#活动状态标识 初始关闭
	
	Tra_ND_ExchangeRewad = AutoLog.AutoTransaction("Tra_ND_ExchangeRewad", "国庆奖励兑换")

#============ 状态 ==============	
def ND_ExchangeStart(*param):
	'''
	国庆奖励兑换活动开启
	'''
	_, circularType = param
	if circularType != CircularDefine.ND_ExchangeReward:
		return
	
	#重复开启
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open ND_ExchangeReward!"
		return
	
	#更新标志
	IS_START = True
	
def ND_ExchangeEnd(*param):
	'''
	国庆奖励兑换活动结束
	'''
	_, circularType = param
	if circularType != CircularDefine.ND_ExchangeReward:
		return
	
	#重复关闭
	global IS_START
	if not IS_START:
		print "GE_EXC,repeat close ND_ExchangeReward!"
		return
	
	#更新标志
	IS_START = False

#============= 请求 ================

def OnExchangeReward(role, msg):
	'''
	请求国庆奖励兑换
	@param role:
	@param msg: exchangType  
	'''	
	#活动未开启
	if not IS_START:
		return
	
	#等级不足
	if role.GetLevel() < EnumGameConfig.ND_ExchangeNeedLevel:
		return
	
	#兑换类型对应配置
	exchangeType = msg
	exchangeCfg = ExchangeRewardConfig.ND_EXCHANGE_REWARD_DICT.get(exchangeType, None)
	if not exchangeCfg:
		return
	
	#背包空间不足
	if role.PackageEmptySize() < 1:
		role.Msg(2, 0, GlobalPrompt.ND_Exchange_PackageIsFull)
		return 
	
	#没有足够的道具
	costItemCoding, costItemCnt = exchangeCfg.costItem
	if role.ItemCnt(costItemCoding) < costItemCnt:
		return
	
	#process
	with Tra_ND_ExchangeRewad:
		#扣除消耗
		role.DelItem(costItemCoding, costItemCnt)
		
		#获得物品
		gainItemCoding, gainItemCnt = exchangeCfg.gainItem
		role.AddItem(gainItemCoding, gainItemCnt)
		
		#坐骑获得广播
		if exchangeCfg.broadcast:
			cRoleMgr.Msg(11, 0, GlobalPrompt.ND_Exchange_MountExchange % (role.GetRoleName(), gainItemCoding, gainItemCnt))
				
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#活动控制
		Event.RegEvent(Event.Eve_StartCircularActive, ND_ExchangeStart)
		Event.RegEvent(Event.Eve_EndCircularActive, ND_ExchangeEnd)
		
		#玩家请求
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ND_OnExchangeReward", "请求国庆奖励兑换"), OnExchangeReward)