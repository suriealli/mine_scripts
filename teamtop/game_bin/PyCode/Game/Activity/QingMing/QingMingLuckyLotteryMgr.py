#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.QingMing.QingMingLuckyLotteryMgr")
#===============================================================================
# 清明幸运大轮盘 Mgr
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Call, Event
from Game.Activity import CircularDefine
from Game.Activity.QingMing import QingMingLuckyLotteryConfig

if "_HasLoad" not in dir():
	IS_START = False
	QMLL_OnlineRole_Set = set()	#缓存打开面板的角色ID
	QMLL_PreciousRecord_List = []	#缓存大奖记录[(roleName,coding,cnt)]
	
	Tra_QMLL_SingleLottery = AutoLog.AutoTransaction("Tra_QMLL_SingleLottery", "清明幸运大轮盘_单次抽奖")
	
	QMLL_PreciousRecord_S = AutoMessage.AllotMessage("QMLL_PreciousRecord_S", "清明幸运大轮盘_大奖记录同步")
	QMLL_LotteryResult_SB = AutoMessage.AllotMessage("QMLL_LotteryResult_SB", "清明幸运大轮盘_抽奖结果同步回调")

#### 活动控制  start ####
def OnStartQingMingLuckyLottery(*param):
	'''
	开启活动
	'''
	_, circularType = param
	if CircularDefine.CA_QingMingLuckyLottery != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open QingMingLuckyLottery"
		return
		
	IS_START = True

def OnEndQingMingLuckyLottery(*param):
	'''
	结束活动
	'''
	_, circularType = param
	if CircularDefine.CA_QingMingLuckyLottery != circularType:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC, end QingMingLuckyLottery while not start"
		return
		
	IS_START = False

#### 请求start
def OnOpenPanel(role, msg = None):
	'''
	请求打开面板
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.QMLL_NeedLevel:
		return
	
	#缓存该玩家已打开面板
	global QMLL_OnlineRole_Set
	QMLL_OnlineRole_Set.add(role.GetRoleID())
	#同步当前大奖记录
	role.SendObj(QMLL_PreciousRecord_S, QMLL_PreciousRecord_List)

def OnClosePanel(role, msg = None):
	'''
	请求关闭面板
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.QMLL_NeedLevel:
		return
	
	#清除缓存该玩家已打开面板
	global QMLL_OnlineRole_Set
	QMLL_OnlineRole_Set.discard(role.GetRoleID())

def OnSingleLottery(role, msg = None):
	'''
	单次抽奖请求
	'''
	if not IS_START:
		return
	
	#等级不足
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.QMLL_NeedLevel:
		return
	
	#幸运钥匙不足
	if role.ItemCnt(EnumGameConfig.QMO_LotteryItemCoding) < 1:
		return
	
	randomObj = QingMingLuckyLotteryConfig.GetRandomObjByLevel(roleLevel)
	if not randomObj:
		print "GE_EXC, QingMingLuckyLottery::OnSingleLottery::can not get randomObj by roleLevel(%s)" % roleLevel
		return
	
	reward = randomObj.RandomOne()
	if not reward:
		print "GE_EXC, QingMingLuckyLottery::OnSingleLottery:: randomObj.RandomOne() is None"
		return
	
	#扣消耗
	with Tra_QMLL_SingleLottery:
		#扣神石
		role.DelItem(EnumGameConfig.QMO_LotteryItemCoding, 1)
	
	#抽奖结果 同步回调
	roleId = role.GetRoleID()
	roleName = role.GetRoleName()
	rewardId, itemIndex, coding, cnt, isPrecious = reward
	role.SendObjAndBack(QMLL_LotteryResult_SB, (itemIndex, rewardId), 8, OnSingleLotteryCallBack, (roleId, roleName, coding, cnt, isPrecious))
	
def OnSingleLotteryCallBack(role, calArgv, regParam):
	'''
	抽奖回调
	'''
	roleId, roleName, coding, cnt, isPrecious = regParam
	#大奖处理
	if isPrecious:
		global QMLL_PreciousRecord_List
		preciousInfo = (roleName, coding, cnt)
		if len(QMLL_PreciousRecord_List) >= EnumGameConfig.QMLL_RecordMaxNum:
			QMLL_PreciousRecord_List.pop(0)
		QMLL_PreciousRecord_List.append(preciousInfo)
		
		#同步最新珍贵奖励记录给缓存的role
		invalidRoleSet = set()
		global QMLL_OnlineRole_Set
		for tmpRoleId in QMLL_OnlineRole_Set:
			tmpRole = cRoleMgr.FindRoleByRoleID(tmpRoleId)
			if not tmpRole:
				invalidRoleSet.add(tmpRoleId)
				continue
			tmpRole.SendObj(QMLL_PreciousRecord_S, QMLL_PreciousRecord_List)
		
		#删除缓存的无效roleId
		if len(invalidRoleSet) > 0:
			QMLL_OnlineRole_Set.difference_update(invalidRoleSet)
		
		#珍贵奖励提示
		cRoleMgr.Msg(11, 0, GlobalPrompt.QMLL_MSG_Precious % (roleName, coding, cnt))
		
	Call.LocalDBCall(roleId, LotteryRealAward, (coding, cnt))

def LotteryRealAward(role, param):
	'''
	回调实际发奖励
	'''
	coding, cnt = param
	with Tra_QMLL_SingleLottery:
		#物品获得
		role.AddItem(coding, cnt)
		#获得提示
		role.Msg(2, 0, GlobalPrompt.QMLL_Tips_Head + GlobalPrompt.QMLL_Tips_Item % (coding, cnt))

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartQingMingLuckyLottery)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndQingMingLuckyLottery)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QMLL_OnOpenPanel", "清明幸运大轮盘_请求打开面板"), OnOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QMLL_OnClosePanel", "清明幸运大轮盘_请求关闭面板"), OnClosePanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QMLL_OnSingleLottery", "清明幸运大轮盘_请求单次抽奖"), OnSingleLottery)
