#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.BlessRoulette.BlessRouletteMgr")
#===============================================================================
# 祝福轮盘Mgr
#===============================================================================
import Environment
from Game.Role import Event
import cRoleMgr
from Common.Message import AutoMessage
from Game.Activity import CircularDefine
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Activity.BlessRoulette import BlessRouletteConfig
from ComplexServer.Log import AutoLog

if "_HasLoad" not in dir():
	IS_START = False	#祝福轮盘活动开关标志
	
	BLESSROULETTE_MASTERRECORD_LIST = []		#祝福轮盘大奖记录[(roleName,coding,cnt),]
	BLESSROULETTE_ROLERECORDS_DICT = {}		#祝福轮盘玩家抽奖记录{roleId:[(coding,cnt),],}
	
	BLESSROULETTE_BROADROLE_SET = set()		#大将记录更新 需要广播的角色
	
	BlessRoulette_MineRecord_S = AutoMessage.AllotMessage("BlessRoulette_MineRecord_S", "祝福轮盘我的抽奖记录")
	BlessRoulette_MasterRecord_S = AutoMessage.AllotMessage("BlessRoulette_MasterRecord_S", "祝福轮盘本服大奖记录")

	BlessRoulette_DrawResult_SB = AutoMessage.AllotMessage("BlessRoulette_DrawResult_SB", "祝福轮盘抽奖结果")
	
	Tra_BlessRoulette_SingleDraw = AutoLog.AutoTransaction("Tra_BlessRoulette_SingleDraw", "祝福轮盘单次抽奖")
	Tra_BlessRoulette_BatchDraw = AutoLog.AutoTransaction("Tra_BlessRoulette_BatchDraw", "祝福轮盘批量抽奖")
	
def BlessRouletteStart(*param):
	'''
	祝福轮盘活动开启
	'''
	_, circularType = param
	if CircularDefine.CA_BlessRoulette != circularType:
		return
	
	global IS_START
	global BLESSROULETTE_MASTERRECORD_LIST
	global BLESSROULETTE_ROLERECORDS_DICT
	if IS_START:
		print "GE_EXC,repeat open BlessRoulette"
		return
		
	IS_START = True
	BLESSROULETTE_MASTERRECORD_LIST = []
	BLESSROULETTE_ROLERECORDS_DICT = {}

def BlessRouletteEnd(*param):
	'''
	祝福轮盘活动结束
	'''
	_, circularType = param
	if CircularDefine.CA_BlessRoulette != circularType:
		return
	
	# 未开启 
	global IS_START
	global BLESSROULETTE_MASTERRECORD_LIST
	global BLESSROULETTE_ROLERECORDS_DICT
	if not IS_START:
		print "GE_EXC, end BlessRoulette while not start"
		return
		
	IS_START = False
	BLESSROULETTE_MASTERRECORD_LIST = []
	BLESSROULETTE_ROLERECORDS_DICT = {}

def OnOpenPanel(role, param = None):
	'''
	打开祝福轮盘面板
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.BlessRoulette_NeedLevel:
		return
	
	roleId = role.GetRoleID()
	global BLESSROULETTE_BROADROLE_SET
	BLESSROULETTE_BROADROLE_SET.add(roleId)
	
	global BLESSROULETTE_ROLERECORDS_DICT
	mineRecordList = BLESSROULETTE_ROLERECORDS_DICT.get(roleId,[])
	role.SendObj(BlessRoulette_MineRecord_S, mineRecordList)
	
	global BLESSROULETTE_MASTERRECORD_LIST
	role.SendObj(BlessRoulette_MasterRecord_S, BLESSROULETTE_MASTERRECORD_LIST)

def OnClosePanel(role, param = None):
	'''
	祝福轮盘关闭面板
	'''
	global BLESSROULETTE_BROADROLE_SET
	BLESSROULETTE_BROADROLE_SET.discard(role.GetRoleID())

def OnSingleDraw(role, msg = None):
	'''
	祝福轮盘单次抽奖
	'''
	if not IS_START:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.BlessRoulette_NeedLevel:
		return
	
	if role.GetUnbindRMB() < EnumGameConfig.BlessRoulette_UnbindRMBCost:
		return
	
	#随机奖励
	coding, cnt, isRecord, itemIndex = BlessRouletteConfig.GetSingleRandomReward(role, roleLevel)
	if not coding or not cnt:
		print "GE_EXC,OnSingleDraw: random error coding(%s) or cnt(%s)" % (coding, cnt)
	
	#扣除抽奖神石
	with Tra_BlessRoulette_SingleDraw:
		role.DecUnbindRMB(EnumGameConfig.BlessRoulette_UnbindRMBCost)
	
	role.SendObjAndBack(BlessRoulette_DrawResult_SB, itemIndex, 3, SingleDrawCallBack, (coding, cnt, isRecord, itemIndex))

def SingleDrawCallBack(role,callargv, regparam):
	'''
	单次抽奖回调
	'''
	coding, cnt, isRecord, _ = regparam
	#process
	with Tra_BlessRoulette_SingleDraw:
		#物品获得
		role.AddItem(coding, cnt)
	
	mineInfo = (coding,cnt)
	roleId = role.GetRoleID()
	global BLESSROULETTE_ROLERECORDS_DICT
	mineRecordList = BLESSROULETTE_ROLERECORDS_DICT.get(roleId, [])
	if len(mineRecordList) >= EnumGameConfig.BlessRoulette_MineRecordSize:
		mineRecordList.pop(0)
	mineRecordList.append(mineInfo)
	#记录抽奖
	BLESSROULETTE_ROLERECORDS_DICT[roleId] = mineRecordList
	
	#获得物品提示
	rewardPrompt = GlobalPrompt.BlessRoulette_Tips_Reward_Head + GlobalPrompt.BlessRoulette_Tips_Reward_Item % (coding, cnt)
	role.Msg(2, 0, rewardPrompt)
	
	#抽奖之后更新抽奖记录再同步
	role.SendObj(BlessRoulette_MineRecord_S, mineRecordList)
	
	#大奖处理
	if isRecord:
		global BLESSROULETTE_MASTERRECORD_LIST
		masterInfo = (role.GetRoleName(),coding, cnt)
		if len(BLESSROULETTE_MASTERRECORD_LIST) >= EnumGameConfig.BlessRoulette_MasterRecordSize:
			BLESSROULETTE_MASTERRECORD_LIST.pop(0)
		BLESSROULETTE_MASTERRECORD_LIST.append(masterInfo)
		
		#先同步给自己
		role.SendObj(BlessRoulette_MasterRecord_S, BLESSROULETTE_MASTERRECORD_LIST)
		#大奖记录有更新 同步其他需要同步的玩家
		BroadMasterRecord(role)
		
def OnBatchDraw(role, msg = None):
	'''
	祝福轮盘批量摇奖
	'''
	if not IS_START:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.BlessRoulette_NeedLevel:
		return
	
	needUnbindRMB = EnumGameConfig.BlessRoulette_UnbindRMBCost * EnumGameConfig.BlessRoulette_BatchDrawNum
	if role.GetUnbindRMB() < needUnbindRMB:
		return
	
	#随机出奖励列表
	rewardList = BlessRouletteConfig.GetBatchRandomReward(role)
	#process
	isUpdateMasterRecord = False	#大奖记录是否有更新
	rewardDict = {}
	with Tra_BlessRoulette_BatchDraw:
		#扣钱
		role.DecUnbindRMB(needUnbindRMB)
		
		roleId = role.GetRoleID()
		roleName = role.GetRoleName()
		global BLESSROULETTE_MASTERRECORD_LIST
		global BLESSROULETTE_ROLERECORDS_DICT
		mineRecordList = BLESSROULETTE_ROLERECORDS_DICT.get(roleId,[])
		for coding, cnt, isRecord, _ in rewardList:
			#获得物品
			role.AddItem(coding, cnt)
			
			#统计
			if coding not in rewardDict:
				rewardDict[coding] = cnt
			else:
				rewardDict[coding] += cnt
			
			#更新玩家抽奖记录
			if len(mineRecordList) >= EnumGameConfig.BlessRoulette_MineRecordSize:
				mineRecordList.pop(0)
			mineRecordList.append((coding, cnt))
			#记录抽奖
			BLESSROULETTE_ROLERECORDS_DICT[roleId] = mineRecordList
			
			#更新大奖记录
			if isRecord:
				isUpdateMasterRecord = True
				if len(BLESSROULETTE_MASTERRECORD_LIST) >= EnumGameConfig.BlessRoulette_MasterRecordSize:
					BLESSROULETTE_MASTERRECORD_LIST.pop(0)
				BLESSROULETTE_MASTERRECORD_LIST.append((roleName,coding,cnt))
				
		#获得物品提示
		rewardPrompt = GlobalPrompt.BlessRoulette_Tips_Reward_Head
		for coding, cnt in rewardDict.iteritems():
			rewardPrompt += GlobalPrompt.BlessRoulette_Tips_Reward_Item % (coding, cnt)
		role.Msg(2, 0, rewardPrompt)
		
		#同步玩家抽奖记录	
		role.SendObj(BlessRoulette_MineRecord_S, mineRecordList)
		
		#同步大奖记录
		if isUpdateMasterRecord:
			#先同步给自己
			role.SendObj(BlessRoulette_MasterRecord_S, BLESSROULETTE_MASTERRECORD_LIST)
			#大奖记录有更新 同步其他需要同步的玩家
			BroadMasterRecord(role)

def BroadMasterRecord(role):
	'''
	大奖记录更新广播同步出去
	'''
	roleId = role.GetRoleID()
	global BLESSROULETTE_BROADROLE_SET
	for tmpRoleId in BLESSROULETTE_BROADROLE_SET:
		#已同步自己
		if tmpRoleId == roleId:
			continue
		#找不到role
		tmpRole = cRoleMgr.FindRoleByRoleID(tmpRoleId)
		if not tmpRole:
			continue
		#同步
		tmpRole.SendObj(BlessRoulette_MasterRecord_S, BLESSROULETTE_MASTERRECORD_LIST)

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, BlessRouletteStart)
		Event.RegEvent(Event.Eve_EndCircularActive, BlessRouletteEnd)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("BlessRoulette_OnOpenPanel", "祝福轮盘打开面板"), OnOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("BlessRoulette_OnClosePanel", "祝福轮盘关闭面板"), OnClosePanel)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("BlessRoulette_OnSingleDraw", "祝福轮盘单次摇奖"), OnSingleDraw)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("BlessRoulette_OnBatchDraw", "祝福轮盘批量抽奖"), OnBatchDraw)
		