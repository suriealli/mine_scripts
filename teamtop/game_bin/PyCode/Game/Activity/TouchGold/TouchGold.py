#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.TouchGold.TouchGold")
#===============================================================================
# 点石成金
#===============================================================================
import Environment
import cRoleMgr
import cDateTime
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Role import Call, Event
from Game.Role.Mail import Mail
from Game.Role.Data import EnumCD, EnumObj, EnumInt16, EnumDayInt8, EnumInt32
from Game.Activity.TouchGold import TouchGoldConfig

if "_HasLoad" not in dir():
	#这些coding都是数值不是真实道具
	MSG_TIPS_DICT = {1:28979, 2:28980, 3:28981, 4:28982, 5:28983}
	
	TouchGold_Syn_stoneData = AutoMessage.AllotMessage("TouchGold_Syn_stoneData", "同步原石数据")
	TouchGold_Syn_StartTouch = AutoMessage.AllotMessage("TouchGold_Syn_StartTouch", "通知客户端开始点石成金")
	#日志
	Tra_GetStone = AutoLog.AutoTransaction("Tra_GetStone", "购买或获取原石")
	Tra_TouchGoldCost = AutoLog.AutoTransaction("Tra_TouchGoldCost", "点金花费")
	Tra_TouchGoldReward = AutoLog.AutoTransaction("Tra_TouchGoldReward", "点石成金奖励")
	Tra_TouchGoldExchange = AutoLog.AutoTransaction("Tra_TouchGoldExchange", "点石成金积分兑换")
	Tra_TouchGoldStoneBack = AutoLog.AutoTransaction("Tra_TouchGoldStoneBack", "点石成金原石回收")

def GetActState():
	if cDateTime.Hour() != 23:
		return True
	if 50 <= cDateTime.Minute() <= 59:
		return False
	else:
		return True

def RequestGetStone(role, param):
	'''
	客户端请求获取或购买原石
	@param role:
	@param param:
	'''
	IS_START = GetActState()
	if not IS_START:
		return
	gettype = param
	cfg = TouchGoldConfig.GET_STONE_DICT.get(gettype)
	if not cfg:
		return
	
	costUnbind_Q, cd, limitCnt = cfg.costUnbind_Q, cfg.cd, cfg.limitCnt
	if costUnbind_Q:
		from Game.Activity.TouchGoldReward import TouchGoldReward
		costUnbind_Q = TouchGoldReward.StonePriceBuffer(role, costUnbind_Q)
		if role.GetUnbindRMB_Q() < costUnbind_Q:
			return
	if cd:
		if role.GetCD(EnumCD.TouchGoldCD) > 0:
			return
	if not cfg.randomcnt:
		print "GE_EXC,RequestGetStone randomcnt is ZERO"
		return
	if limitCnt:
		if role.GetDI8(EnumDayInt8.TouchGoldFreeStones) >= limitCnt:
			return
		
	rewards = {}
	for _ in xrange(cfg.randomcnt):
		stonetype = cfg.RANDOM_STONE.RandomOne()
		rewards[stonetype] = rewards.get(stonetype, 0) + 1
	if not rewards:
		return
	global MSG_TIPS_DICT
	with Tra_GetStone:
		if limitCnt:
			role.IncDI8(EnumDayInt8.TouchGoldFreeStones, 1)
		if costUnbind_Q:
			role.DecUnbindRMB_Q(costUnbind_Q)
		if cd:
			role.SetCD(EnumCD.TouchGoldCD, cd)
		ToouchGoldData = role.GetObj(EnumObj.ToouchGoldData)
		tips = GlobalPrompt.Reward_Tips
		for stonetype, cnt in rewards.iteritems():
			ToouchGoldData[stonetype] = ToouchGoldData.get(stonetype, 0) + cnt
			#每个原石类型对应的数值coding
			coding = MSG_TIPS_DICT.get(stonetype)
			tips += GlobalPrompt.Item_Tips % (coding, cnt)

		role.Msg(2, 0, tips)
		SynStoneData(role)
	
def RequestTouchGold(role, param):
	'''
	客户端请求点金
	@param role:
	@param param:
	'''
	IS_START = GetActState()
	if not IS_START:
		return
	stone = param
	
	ToouchGoldData = role.GetObj(EnumObj.ToouchGoldData)
	if ToouchGoldData.get(stone, 0) < 1:
		return
	
	cfg = TouchGoldConfig.TOUCH_GOLD_DICT.get(stone)
	if not cfg:
		print "GE_EXC,can not find stone(%s) in RequestTouchGold" % stone
		return
	
	FreeState = False
	buycost = 0
	
	buyTimes = role.GetI16(EnumInt16.TouchGoldBuyTimes)
	#无免费次数
	if role.GetDI8(EnumDayInt8.TouchGoldFreeTimes) >= EnumGameConfig.Max_Free_Times:
		nextTimes = buyTimes + 1
		if nextTimes > TouchGoldConfig.MAX_BUY_TIMES:
			nextTimes = TouchGoldConfig.MAX_BUY_TIMES
		needUnbindRMB_Q = TouchGoldConfig.BUY_TIMES_COST.get(nextTimes)
		if not needUnbindRMB_Q:
			print "GE_EXC,can not find buyTimes(%s) in RequestGoldTimes" % nextTimes
			return
		if role.GetUnbindRMB_Q() < needUnbindRMB_Q:
			return
		buycost = needUnbindRMB_Q
	else:
		FreeState = True
	
	random_cnt = cfg.RANDOM_CNT.RandomOne()
	if not random_cnt:
		print "GE_EXC,random_cnt is zero!!!!!"
		return
	
	rewards_dict = {}
	for _ in xrange(random_cnt):
		item = cfg.RANDOM_ITEM.RandomOne()
		if not item:
			print "GE_EXC,RANDOM_ITEM is None!!"
			return
		coding, cnt = item
		rewards_dict[coding] = rewards_dict.get(coding, 0) + cnt
	if not rewards_dict:
		return
	
	with Tra_TouchGoldCost:
		if FreeState:
			role.IncDI8(EnumDayInt8.TouchGoldFreeTimes, 1)
		if buycost:
			role.DecUnbindRMB_Q(buycost)
			if buyTimes < TouchGoldConfig.MAX_BUY_TIMES:
				role.IncI16(EnumInt16.TouchGoldBuyTimes, 1)
		
		from Game.Activity.TouchGoldReward import TouchGoldReward
		roleId = role.GetRoleID()
		if TouchGoldReward.IsStart and TouchGoldReward.TouchGoldReward_Dict.returnDB:
			if roleId not in TouchGoldReward.TouchGoldReward_Dict:
				TouchGoldReward.TouchGoldReward_Dict[roleId] = {1:set(), 2:set(), 3:0}
			TouchGoldReward.TouchGoldReward_Dict[roleId][3] += 1
			role.SendObj(TouchGoldReward.TouchGoldCnt, TouchGoldReward.TouchGoldReward_Dict[roleId][3])
		
		#扣指定的原石
		ToouchGoldData[stone] = ToouchGoldData.get(stone, 0) - 1
		
		if cfg.rewarditem:
			for coding, cnt in cfg.rewarditem:
				rewards_dict[coding] = rewards_dict.get(coding, 0) + cnt
		role.SendObjAndBack(TouchGold_Syn_StartTouch, stone, 10, BackReward, (cfg.rewardpoint, role.GetRoleID(), rewards_dict, TouchGoldReward.TouchGoldReward_Dict.get(roleId, {}).get(3, 0)))
	
def BackReward(role, callargv, regparam):
	point, roleId, rewards, cnt = regparam
	Call.LocalDBCall(roleId, SendRewardEx, (rewards, point, cnt))
	
def SendReward(role, regparam):
	rewards, point = regparam
	tips = GlobalPrompt.Reward_Tips
	with Tra_TouchGoldReward:
		for coding, cnt in rewards.iteritems():
			role.AddItem(coding, cnt)
			tips += GlobalPrompt.Item_Tips %(coding, cnt)
		if point:
			role.IncI32(EnumInt32.TouchGoldPoint, point)
			tips += GlobalPrompt.TouchGold_PointMsg % point
		role.Msg(2, 0, tips)
	SynStoneData(role)
	
def SendRewardEx(role, regparam):
	rewards, point, lastCnt = regparam
	tips = GlobalPrompt.Reward_Tips
	
	from Game.Activity.TouchGoldReward import TouchGoldReward, TouchGoldRewardConfig
	with Tra_TouchGoldReward:
		for coding, cnt in rewards.iteritems():
			role.AddItem(coding, cnt)
			tips += GlobalPrompt.Item_Tips %(coding, cnt)
		if point:
			point = TouchGoldReward.ScoreBuffer(role, point)
			role.IncI32(EnumInt32.TouchGoldPoint, point)
			tips += GlobalPrompt.TouchGold_PointMsg % point
		role.Msg(2, 0, tips)
		
		for buffIndex, stoneCnt in TouchGoldRewardConfig.TouchGoldRewardStone_Dict.iteritems():
			if lastCnt != stoneCnt:
				continue
			TouchGoldReward.AddBuff(role, buffIndex)
			break
	SynStoneData(role)
	
def RequestTouchExchange(role, param):
	'''
	客户端请求点金积分兑换
	@param role:
	@param param:
	'''
	goodsId = param
	
	cfg = TouchGoldConfig.POINT_EXCHANGE_DICT.get(goodsId)
	if not cfg:
		print "GE_EXC,can not find goodsId(%s) in RequestTouchExchange" % goodsId
		return
	if not cfg.needPoint:
		return
	if role.GetI32(EnumInt32.TouchGoldPoint) < cfg.needPoint:
		return
	with Tra_TouchGoldExchange:
		role.DecI32(EnumInt32.TouchGoldPoint, cfg.needPoint)
		tips = GlobalPrompt.Reward_Tips
		if cfg.items:
			coding, cnt = cfg.items
			role.AddItem(coding, cnt)
			tips += GlobalPrompt.Item_Tips % (coding, cnt)
		role.Msg(2, 0, tips)
	
def SynStoneData(role):
	ToouchGoldData = role.GetObj(EnumObj.ToouchGoldData)
	role.SendObj(TouchGold_Syn_stoneData, ToouchGoldData)
	
def RoleDayClear(role, param):
	#每日清理
	if role.GetI16(EnumInt16.TouchGoldBuyTimes) > 0:
		role.SetI16(EnumInt16.TouchGoldBuyTimes, 0)
	
	ToouchGoldData = role.GetObj(EnumObj.ToouchGoldData)
	if not ToouchGoldData:
		return
	total_Point = 0
	for stone, cnt in ToouchGoldData.iteritems():
		if cnt <= 0: continue
		cfg = TouchGoldConfig.TOUCH_GOLD_DICT.get(stone)
		if not cfg:
			print "GE_EXC,can not find stone(%s) in RoleDayClear" % stone
			continue
		total_Point += cfg.backPoint * cnt
	if not total_Point:
		return
	with Tra_TouchGoldStoneBack:
		role.SetObj(EnumObj.ToouchGoldData, {})
		Mail.SendMail(role.GetRoleID(), GlobalPrompt.TouchGold_Title, GlobalPrompt.TouchGold_Sender, GlobalPrompt.TouchGold_Content % total_Point,touchpoint = total_Point)
		SynStoneData(role)
		
def SyncRoleOtherData(role, param):
	SynStoneData(role)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TouchStone_GetStone", "客户端请求获取或购买原石"), RequestGetStone)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TouchStone_TouchGold", "客户端请求点金"), RequestTouchGold)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TouchStone_TouchExchange", "客户端请求点金积分兑换"), RequestTouchExchange)
