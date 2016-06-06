#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DoubleEleven.ElevenTunable")
#===============================================================================
# 双十一轮盘控制 @author GaoShuai 2015
#===============================================================================
import cRoleMgr
import Environment
from Game.Role import Event
from Game.Activity import CircularDefine
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Game.Activity.DoubleEleven.ElevenTunableConfig import ElevenTutable_Dict
from Common.Other import GlobalPrompt

if "_HasLoad" not in dir():
	IsStart = False
	#消息
	ElevenTunableRewardData = AutoMessage.AllotMessage("ElevenTunableRewardData", "同步双十一转盘奖励")
	#日志
	ElevenTunableCost = AutoLog.AutoTransaction("ElevenTunableCost", "双十一转盘扣除道具")
	ElevenTunableLog = AutoLog.AutoTransaction("ElevenTunableLog", "双十一转盘发奖 ")
	
def StartCircularActive(param1, param2):
	global IsStart
	if param2 != CircularDefine.CA_ElevenTurntable:
		return
	if IsStart:
		print 'GE_EXC, ElevenTurntable is already start'
	IsStart = True

def EndCircularActive(param1, param2):
	global IsStart
	if param2 != CircularDefine.CA_ElevenTurntable:
		return
	if not IsStart:
		print 'GE_EXC, ElevenTurntable is already end'
	IsStart = False
def RequestElevenTunable(role, msg=None):
	'''
	请求双十一轮盘
	@param role:
	@param msg: None
	'''
	global IsStart
	if not IsStart: return
	
	#主角等级是否满足
	roleLevel = role.GetLevel()
	if roleLevel not in ElevenTutable_Dict:
		print 'GE_EXC, roleLevel not in ElevenTutable_Dict, role level = %s', roleLevel
		return
	randomObj, (keyCoding, keyCnt) = ElevenTutable_Dict[roleLevel]
	if not randomObj:
		print 'GE_EXC, can not get the randomObj in ElevenTutable_Dict, where key = %s', roleLevel
		return 
	
	if role.ItemCnt(keyCoding) < keyCnt:
		return
	index, itemCoding, itemCnt, special = randomObj.RandomOne()
	
	with ElevenTunableCost:
		#删除物品
		role.DelItem(keyCoding, keyCnt)
	
	#同步客户端
	role.SendObjAndBack(ElevenTunableRewardData, [index], 20, CallBackTunable, (special, itemCoding, itemCnt))

def CallBackTunable(role, callargv, regparam):
	'''
	双十一转盘回调
	@param role:
	@param callargv:
	@param regparam:
	'''
	global IsStart
	if not IsStart: return
	
	special, itemCoding, itemCnt = regparam
	#日志
	with ElevenTunableLog:
		#发奖励
		if itemCoding == 1:
			role.IncUnbindRMB_S(itemCnt)
		else:
			role.AddItem(itemCoding, itemCnt)
		
	if itemCoding == 1:
		specialTip = GlobalPrompt.TunableTip_special_RMB % (role.GetRoleName(), itemCnt)
		tip = GlobalPrompt.ElevenTuntable % itemCnt
	else:
		specialTip = GlobalPrompt.TunableTip_special % (role.GetRoleName(), itemCoding, itemCnt)
		tip = GlobalPrompt.Reward_Item_Tips % (itemCoding, itemCnt)
	if special:
		cRoleMgr.Msg(11, 0, specialTip)
	else:
		role.Msg(2, 0, tip)

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		
		Event.RegEvent(Event.Eve_StartCircularActive, StartCircularActive)
		Event.RegEvent(Event.Eve_EndCircularActive, EndCircularActive)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestElevenTunable", "请求双十一轮盘"), RequestElevenTunable)
