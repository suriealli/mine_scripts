#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PetLuckyFarm.PetLuckyFarm")
#===============================================================================
# 宠物福田
#===============================================================================
import random
import cRoleMgr
import Environment
from Game.Role import Event
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.SysData import WorldData
from Game.Activity import CircularDefine
from Game.Activity.PetLuckyFarm import PetLuckyFarmConfig

if "_HasLoad" not in dir():
	
	__IsStart = False
	OneKeyTimes = 18
	
	SilverHoeType = 1		#银锄头
	GoldHoeType = 2			#金锄头
	
	#日志
	Tra_Collect_Silver = AutoLog.AutoTransaction("Tra_Collect_Silver_PetLuckyFarm", "宠物福田请求银锄头普通采集")
	Tra_Collect_Gold = AutoLog.AutoTransaction("Tra_Collect_Gold_PetLuckyFarm", "宠物福田请求金锄头普通采集")
	Tra_OnekeyCollect_Silver = AutoLog.AutoTransaction("Tra_OnekeyCollect_Silver_PetLuckyFarm", "宠物福田请求银锄头一键采集")
	Tra_OnekeyCollect_Gold = AutoLog.AutoTransaction("Tra_OnekeyCollect_Gold_PetLuckyFarm", "宠物福田请求金锄头一键采集")

def PetLuckyFarmStart(*param):
	'''
	宠物福田活动开启
	'''
	_, activetype = param
	if activetype != CircularDefine.CA_PetLuckyFarm:
		return
	global __IsStart
	if __IsStart:
		print "GE_EXC, PetLuckyFarm is already started "
		return
	__IsStart = True


def PetLuckyFarmEnd(*param):
	'''
	宠物福田活动关闭
	'''
	_, activetype = param
	if activetype != CircularDefine.CA_PetLuckyFarm:
		return
	global __IsStart
	if not __IsStart:
		print "GE_EXC, PetLuckyFarm is already ended "
		return
	__IsStart = False

def RequestCollect(role, msg):
	'''
	客户端请求采集
	'''
	backFunId, the_type = msg
	if not __IsStart:
		role.CallBackFunction(backFunId, 2)
		return
	#等级判断
	if role.GetLevel() < EnumGameConfig.PetLuckyFarmNeedLevel:
		role.CallBackFunction(backFunId, 2)
		return
	#世界等级
	world_level = WorldData.GetWorldLevel()
	config = PetLuckyFarmConfig.PetLuckyFarmConfigDict.get(world_level, None)
	if config == None:
		print "GE_EXC,error while config = PetLuckyFarmConfig.PetLuckyFarmConfigDict.get(world_level, None), no such world_level(%s)" % world_level
		role.CallBackFunction(backFunId, 2)
		return
	#要扣除的金币
	money_to_dec = 0
	
	# 金锄头的话是不用扣除金币的
	if the_type == GoldHoeType:
		if role.ItemCnt(EnumGameConfig.PetLuckyFarmGoldHoeCode) < 1:
			role.CallBackFunction(backFunId, 2)
			return
		reward_index = config.GoldRandomRate.RandomOne()
		item_to_del = EnumGameConfig.PetLuckyFarmGoldHoeCode
		Tra = Tra_Collect_Gold
	
	#银锄头一次扣80000金币
	elif the_type == SilverHoeType:
		money_to_dec = 0
		if Environment.EnvIsNA():
			money_to_dec = EnumGameConfig.PetLuckyFarmMoneyPerTime_NA
		else:
			money_to_dec = EnumGameConfig.PetLuckyFarmMoneyPerTime
		if role.ItemCnt(EnumGameConfig.PetLuckyFarmSilverHoeCode) < 1 or role.GetMoney() < money_to_dec:
			role.CallBackFunction(backFunId, 2)
			return
		reward_index = config.SilverRandomRate.RandomOne()
		item_to_del = EnumGameConfig.PetLuckyFarmSilverHoeCode
		Tra = Tra_Collect_Silver
		
	else :
		role.CallBackFunction(backFunId, 2)
		return
	
	reward_cfg = PetLuckyFarmConfig.PetLuckyFarmRewardConfigDict.get(reward_index, None)
	
	if reward_cfg == None:
		print "GE_EXC, error while reward_cfg = PetLuckyFarmConfig.PetLuckyFarmRewardConfigDict.get(reward_index, None), no such reward_index(%s)" % reward_index
		role.CallBackFunction(backFunId, 2)
		return
	
	Tips = GlobalPrompt.PetLuckyFarmTips
	BroadcastTips = GlobalPrompt.PetLuckFarmBroadcast_1 % role.GetRoleName()
	is_broadcast = False
	with Tra:
		if money_to_dec > 0:
			role.DecMoney(money_to_dec)
			
		if role.DelItem(item_to_del, 1) < 1:
			return
		#道具
		if reward_cfg.type == 1:
			role.AddItem(*reward_cfg.thing)
			Tips += GlobalPrompt.Item_Tips % reward_cfg.thing
			if reward_cfg.isBroadcast:
				BroadcastTips += GlobalPrompt.PetLuckFarmItemTips % reward_cfg.thing
				is_broadcast = True
		#命魂
		elif reward_cfg.type == 2:
			role.AddTarotCard(*reward_cfg.thing)
			Tips += GlobalPrompt.Tarot_Tips % reward_cfg.thing
			if reward_cfg.isBroadcast:
				BroadcastTips += GlobalPrompt.PetLuckFarmTarotTips % reward_cfg.thing
				is_broadcast = True
		
		else:
			role.CallBackFunction(backFunId, 2)
			return
	#回调客户端
	role.CallBackFunction(backFunId, 1)
	role.Msg(2, 0, Tips)
	#如果是稀有物品需要广播的话
	if is_broadcast:
		BroadcastTips += GlobalPrompt.PetLuckFarmBroadcast_2
		cRoleMgr.Msg(1, 0, BroadcastTips)
	

def RequestOnekeyCollect(role, msg):
	'''
	客户端请求一键采集
	'''
	backFunId, the_type = msg
	if not __IsStart:
		role.CallBackFunction(backFunId, 2)
		return
	if role.GetLevel() < EnumGameConfig.PetLuckyFarmNeedLevel:
		role.CallBackFunction(backFunId, 2)
		return
	#世界等级
	world_level = WorldData.GetWorldLevel()
	config = PetLuckyFarmConfig.PetLuckyFarmConfigDict.get(world_level, None)
	if config == None:
		print "GE_EXC,error while config = PetLuckyFarmConfig.PetLuckyFarmConfigDict.get(world_level, None), no such world_level(%s)" % world_level
		role.CallBackFunction(backFunId, 2)
		return
	#如果使用的是金锄头
	if the_type == GoldHoeType :
		money_to_dec = 0
		random_rate = config.GoldRandomRate
		item_to_del = EnumGameConfig.PetLuckyFarmGoldHoeCode
		Tra = Tra_OnekeyCollect_Gold
		
	#如果使用的是银锄头
	elif the_type == SilverHoeType:
		if Environment.EnvIsNA():
			money_to_dec = EnumGameConfig.PetLuckyFarmMoneyPerTime_NA * OneKeyTimes
		else:
			money_to_dec = EnumGameConfig.PetLuckyFarmMoneyPerTime * OneKeyTimes
		if role.GetMoney() < money_to_dec:
			role.CallBackFunction(backFunId, 2)
			return
		random_rate = config.SilverRandomRate
		item_to_del = EnumGameConfig.PetLuckyFarmSilverHoeCode
		Tra = Tra_OnekeyCollect_Silver
	else:
		role.CallBackFunction(backFunId, 2)
		return
	#道具不足
	if role.ItemCnt(item_to_del) < OneKeyTimes:
		role.CallBackFunction(backFunId, 2)
		return
	
	#先把奖励都计算出来
	reward_index_list = []
	for _ in xrange(OneKeyTimes):
		reward_index_list.append(random_rate.RandomOne())
	#奖励道具字典
	rewarditem_dict = {}
	#奖励命魂字典
	rewardtarot_dict = {}
	#需要广播的道具字典
	broadcastitem_dict = {}
	#需要广播的命魂字典
	broadcasttarot_dict = {}
	PG = PetLuckyFarmConfig.PetLuckyFarmRewardConfigDict.get
	for idx in reward_index_list:
		cfg = PG(idx, None)
		if cfg == None:
			print "GE_EXC, error while PetLuckyFarmConfig.PetLuckyFarmRewardConfigDict.get(idx, None), no such idx(%s)" % idx
			role.CallBackFunction(backFunId, 2)
			return
		code, cnt = cfg.thing
		if cfg.type == 1:
			rewarditem_dict[code] = rewarditem_dict.get(code, 0) + cnt
			if cfg.isBroadcast:
				broadcastitem_dict[code] = broadcastitem_dict.get(code, 0) + cnt

		elif cfg.type == 2:
			rewardtarot_dict[code] = rewardtarot_dict.get(code, 0) + cnt
			if cfg.isBroadcast:
				broadcasttarot_dict[code] = broadcasttarot_dict.get(code, 0) + cnt
		
		else:
			role.CallBackFunction(backFunId, 2)
			return
	Tips = GlobalPrompt.PetLuckyFarmTips
	with Tra:
		#扣除道具
		if role.DelItem(item_to_del, OneKeyTimes) < OneKeyTimes:
			role.CallBackFunction(backFunId, 2)
			return
		#扣除金币
		if money_to_dec > 0:
			role.DecMoney(money_to_dec)
		#奖励道具
		for code, cnt in rewarditem_dict.iteritems():
			role.AddItem(code, cnt)
			Tips += GlobalPrompt.Item_Tips % (code, cnt)
		#奖励命魂
		for code, cnt in rewardtarot_dict.iteritems():
			role.AddTarotCard(code, cnt)
			Tips += GlobalPrompt.Tarot_Tips % (code, cnt)
	#回调客户端
	role.CallBackFunction(backFunId, 1)
	
	#各种提示
	BroadCastTips = GlobalPrompt.PetLuckFarmBroadcast_1 % role.GetRoleName()
	is_broadcast = False
	if broadcastitem_dict:
		is_broadcast = True
		for code , cnt in broadcastitem_dict.iteritems():
			BroadCastTips += GlobalPrompt.PetLuckFarmItemTips % (code, cnt)
			
	if broadcasttarot_dict:
		is_broadcast = True
		for code , cnt  in broadcasttarot_dict.iteritems():
			BroadCastTips += GlobalPrompt.PetLuckFarmTarotTips % (code, cnt)
	if is_broadcast:
		BroadCastTips += GlobalPrompt.PetLuckFarmBroadcast_2
		cRoleMgr.Msg(1, 0, BroadCastTips)

	role.Msg(2, 0, Tips)
	
#===============================================================================
# 其它玩法掉锄头
#===============================================================================
def PetLuckyFarm_ExtendReward(role, param):
	#活动是否开始
	if __IsStart is False:
		return None
	
	activityType, idx = param
	
	oddsConfig = PetLuckyFarmConfig.HoeGetDict.get((activityType, idx))
	if not oddsConfig:
		return None
	
	rewardDict = {}
	#金锄头掉落
	if random.randint(1, 10000) <= oddsConfig.goldHoeOdds:
		rewardDict[oddsConfig.goldHoeCoding] = 1
	
	#银锄头掉落
	if random.randint(1, 10000) <= oddsConfig.silverHoeOdds:
		rewardDict[oddsConfig.silverHoeCoding] = 1
	
	return rewardDict

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		
		Event.RegEvent(Event.Eve_StartCircularActive, PetLuckyFarmStart)
		Event.RegEvent(Event.Eve_EndCircularActive, PetLuckyFarmEnd)

		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestCollect_PetLuckyFarm", "宠物福田请求采集集"), RequestCollect)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestOnekeyCollect_PetLuckyFarm", "宠物福田请求一键采集"), RequestOnekeyCollect)
