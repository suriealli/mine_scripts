#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.FiveOneDay.AttackBadDragon")
#===============================================================================
# 勇斗恶龙
#===============================================================================
import cRoleMgr
import Environment
import AttackBadDragonConfig
from Common.Other import GlobalPrompt,EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Activity import CircularDefine
from Common.Message import AutoMessage
from Game.Role.Data import EnumObj
from Game.Role import Event
from Game.Role.Mail import Mail

if "_HasLoad" not in dir():
	IS_START = False						#活动开启结束标志
	
	#消息
	BadDragon_Blood_for_client = AutoMessage.AllotMessage("BadDragon_Blood_for_client", "同步恶龙攻击次数和奖励字典")
	Times_And_Reward_for_client = AutoMessage.AllotMessage("Times_And_Reward_for_client", "同步恶龙攻击次数和奖励列表")
	Reward_for_client = AutoMessage.AllotMessage("Reward_for_client", "同步随机奖励")
	
	#日志
	AttickBadDragonCost = AutoLog.AutoTransaction("AttickBadDragonCost", "参加勇者斗恶龙消耗")
	AttackBadDragonReward = AutoLog.AutoTransaction("AttackBadDragonReward", "勇者斗恶龙奖励")
	AttackBadDragonMailReward = AutoLog.AutoTransaction("AttackBadDragonMailReward", "勇者斗恶龙邮件奖励")
	
def AttackBadDragonStart(*param):
	'''
	勇者斗恶龙活动开启
	'''
	_,circularType = param
	if circularType != CircularDefine.CA_FiveOneAttackDragon:
		return
	
	global IS_START
	if IS_START is True:
		print "GE_EXC, DragonBaoKu is already start"
		return
	
	IS_START = True
	
	for tmpRole in cRoleMgr.GetAllRole():
		tmpRole.SendObj(BadDragon_Blood_for_client, (tmpRole.GetObj(EnumObj.FiveOneDayObj).get(2,-1),tmpRole.GetObj(EnumObj.FiveOneDayObj).get(3,{})) )

def AttackBadDragonEnd(*param):
	'''
	勇者斗恶龙活动结束
	'''
	global IS_START
	
	_, circularType = param
	if circularType != CircularDefine.CA_FiveOneAttackDragon:
		return
	if not IS_START:
		print "GE_EXC, AttackDragon has been ended"
		return
	
	IS_START = False

#=============客户端消息处理======================
def SyncBadDragon(role, param):
	'''
	同步恶龙攻击次数
	@param role:
	@param param:
	'''
	global IS_START
	if not IS_START:
		return
	
	role.SendObj(BadDragon_Blood_for_client, (role.GetObj(EnumObj.FiveOneDayObj).get(2,-1),role.GetObj(EnumObj.FiveOneDayObj).get(3,{})) )
	
def RequestAttack(role, msg):
	'''
	 客户端请求勇者斗恶龙
	@param role:
	@param
		msg == 3	#一键收益,直接发奖励
		msg == 2	#领取奖励
		msg == 1 	#攻击恶龙
		msg == 0 	#挑战恶龙
	'''
	global IS_START
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.FIVE_ONE_NEED_LEVEL:
		return
	
	FiveOneDayObj = role.GetObj(EnumObj.FiveOneDayObj)
	Dragon_count = FiveOneDayObj.get(2, 0)
	
	if msg == 3:
		#一键收益,直接发奖励
		if Dragon_count > -1:
			return
		FastProfit(role)
	elif msg == 2:
		#领取奖励
		if Dragon_count != 10:
			return
		GetRewards(role)
	elif msg == 1:
		#攻击恶龙
		if Dragon_count == -1 or Dragon_count == 10:
			return
		AttackDragon(role)
	elif msg == 0:
		#挑战恶龙
		if Dragon_count != -1:
			return
		TryToAttack(role)
		
def TryToAttack(role):
	#当奖励字典不为空时，需要先领奖
	FiveOneDayObj = role.GetObj(EnumObj.FiveOneDayObj)
	if FiveOneDayObj[3]:
		return
	if FiveOneDayObj.get(2,-1) > -1:
		return
	
	DragonHornID = EnumGameConfig.FIVE_ONE_DRAGON_HORN_ID
	DragonHorn_num = role.ItemCnt(DragonHornID)
	
	if not DragonHorn_num:
		if Environment.EnvIsNA():
			if role.GetUnbindRMB() < EnumGameConfig.FIVE_ONE_ATTICK_NEED_RMB_NA:
				return
		else:
			if role.GetUnbindRMB() < EnumGameConfig.FIVE_ONE_ATTICK_NEED_RMB:
				return
	#如果有龙角就扣除龙角，如果没有龙角就扣除神石
	with AttickBadDragonCost:
		if DragonHorn_num > 0:
			role.DelItem(DragonHornID, 1)
		else:
			if Environment.EnvIsNA():
				role.DecUnbindRMB(EnumGameConfig.FIVE_ONE_ATTICK_NEED_RMB_NA)
			else:
				role.DecUnbindRMB(EnumGameConfig.FIVE_ONE_ATTICK_NEED_RMB)
	
	FiveOneDayObj[2] = 0
	role.SendObj(Times_And_Reward_for_client, (0, 0, 0) )
	
def GetRewards(role):
	'''
	领取奖励
	@param role:
	'''
	FiveOneDayObj = role.GetObj(EnumObj.FiveOneDayObj)
	reward_dict = FiveOneDayObj.get(3,{})
	if not reward_dict:
		print "GE_EXC, can not find reward_dict" 
		return
	reward_list = reward_dict.values()
	FiveOneDayObj[2] = -1
	FiveOneDayObj[3] = {}
	#领奖日志
	msg_tip = GlobalPrompt.Reward_Tips
	with AttackBadDragonReward:
		for coding, cnt in reward_list:
			msg_tip += GlobalPrompt.Item_Tips % (coding, cnt)
			role.AddItem(coding,cnt)
	role.Msg(2, 0, msg_tip)
	role.SendObj(BadDragon_Blood_for_client, (FiveOneDayObj.get(2,-1),FiveOneDayObj.get(3,{})) )
	

def FastProfit(role):
	'''
	一键收益
	@param role:
	'''
	FiveOneDayObj = role.GetObj(EnumObj.FiveOneDayObj)
	DragonBlood = FiveOneDayObj.get(2, 0)
	if DragonBlood is not -1:
		return	
	roleLevel = role.GetLevel()
	
	DragonHornID = EnumGameConfig.FIVE_ONE_DRAGON_HORN_ID
	DragonHorn_num =role.ItemCnt(DragonHornID)
	
	if not DragonHorn_num:
		if Environment.EnvIsNA():
			if role.GetUnbindRMB() < EnumGameConfig.FIVE_ONE_ATTICK_NEED_RMB_NA:
				return
		else:
			if role.GetUnbindRMB() < EnumGameConfig.FIVE_ONE_ATTICK_NEED_RMB:
				return
	
	#如果有龙角就扣除龙角，如果没有龙角就扣除神石
	with AttickBadDragonCost:
		if DragonHorn_num > 0:
			role.DelItem(DragonHornID, 1)
		else:
			if Environment.EnvIsNA():
				role.DecUnbindRMB(EnumGameConfig.FIVE_ONE_ATTICK_NEED_RMB_NA)
			else:
				role.DecUnbindRMB(EnumGameConfig.FIVE_ONE_ATTICK_NEED_RMB)
	
	reward_dict = {}
	for index in range(0,10):
		#随机奖品ID
		random_obj = AttackBadDragonConfig.REWARD_RANDOM_DICT.get(roleLevel)
		if not random_obj:
			print "GE_EXC, Can't Find roleLevel(%s) in REWARD_RANDOM_DICT" % roleLevel
			return
		coding, cnt = random_obj.RandomOne()
		if not coding or not cnt:
			print "GE_EXC, BadDragonReward is wrong"
			return
		reward_dict[index] = (coding, cnt)
		
	if not reward_dict: return
	reward_dict[10] = (EnumGameConfig.FIVE_ONE_DRAGON_BALL_ID, 1)
	FiveOneDayObj[3] = reward_dict
	FiveOneDayObj[2] = 10
	role.SendObj(BadDragon_Blood_for_client, (10, reward_dict) )
	

def AttackDragon(role):
	'''
	攻击恶龙
	@param role:
	'''
	FiveOneDayObj = role.GetObj(EnumObj.FiveOneDayObj)
	Dragon_count = FiveOneDayObj.get(2, 0)
		
	FiveOneDayObj[2] = FiveOneDayObj.get(2, 0) + 1
	
	
	reward_dict = FiveOneDayObj.get(3, {})
	roleLevel = role.GetLevel()
	random_obj = AttackBadDragonConfig.REWARD_RANDOM_DICT.get(roleLevel)
	if not random_obj:
		print "GE_EXC, Can't Find roleLevel(%s) in REWARD_RANDOM_DICT" % roleLevel
		return
	coding, cnt = random_obj.RandomOne()
	if not coding or not cnt:
		print "GE_EXC, BadDragonReward is wrong"
		return
	
	reward_dict[Dragon_count] = (coding,cnt)
	if FiveOneDayObj.get(2, 0) == 10:
		reward_dict[10] = (EnumGameConfig.FIVE_ONE_DRAGON_BALL_ID, 1)
	role.SendObj(Times_And_Reward_for_client, (FiveOneDayObj.get(2, 0), coding, cnt) )
	
def RoleDayClear(role, param):
	'''
	活动结束，自动发奖
	@param role:
	'''
	if IS_START is True:
		return
	
	reward_dict = role.GetObj(EnumObj.FiveOneDayObj).get(3,{})
	if not reward_dict:
		return
	
	reward_list = reward_dict.values()
	
	role.GetObj(EnumObj.FiveOneDayObj)[3] = {}
	
	#通过邮件发奖励
	with AttackBadDragonMailReward:
		Mail.SendMail(role.GetRoleID(), GlobalPrompt.FiveOne_AttickBadDragon, GlobalPrompt.Sender,\
				 GlobalPrompt.FiveOne_AttickBadDragon_Content,\
				 items = [(coding, cnt) for coding, cnt in reward_list])
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#事件
		Event.RegEvent(Event.Eve_StartCircularActive, AttackBadDragonStart)
		Event.RegEvent(Event.Eve_EndCircularActive, AttackBadDragonEnd)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		Event.RegEvent(Event.Eve_SyncRoleOtherData,SyncBadDragon)
		#日志
		
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestAttackBadDragonExchange", "客户端勇斗恶龙"), RequestAttack)
