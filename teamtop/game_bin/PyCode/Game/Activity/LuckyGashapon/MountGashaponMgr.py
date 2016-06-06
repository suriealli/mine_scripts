#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.LuckyGashapon.MountGashaponMgr")
#===============================================================================
# 坐骑扭蛋逻辑控制 @author: Gaoshuai 2016-02-15
#===============================================================================
import cRoleMgr
import Environment
from Game.Role import Event
from Game.Activity import CircularDefine
from Game.Role.Data import EnumDayInt1, EnumDayInt8
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from Game.Activity.LuckyGashapon.LuckyGashaponConfig import MountGashapon_Dict, MountGashaponExchange_Dict


if "_HasLoad" not in dir():
	# 消息
	MountGashaponData = AutoMessage.AllotMessage("MountGashaponData", "坐骑扭蛋获奖记录")
	MountGashaponAddData = AutoMessage.AllotMessage("MountGashaponAddData", "坐骑扭蛋获奖增加记录")
	# 日志
	TraCommonMountGashapon = AutoLog.AutoTransaction("TraCommonMountGashapon", "普通坐骑扭蛋")
	TraGoodMountGashapon = AutoLog.AutoTransaction("TraGoodMountGashapon", "高级坐骑扭蛋")
	TraSuperMountGashapon = AutoLog.AutoTransaction("TraSuperMountGashapon", "超级坐骑扭蛋")
	TraMountGashonExchange = AutoLog.AutoTransaction("TraMountGashonExchange", "坐骑扭蛋兑换")
	
	MAXRECORD = 50		#最大记录条数
	GashaponRecord = []
	OpenPanelSet = set()
	IsStart = False

def StartMountGashapon(param1, param2):
	global IsStart
	if param2 != CircularDefine.CA_LuckyGashaponMount:
		return
	
	if IsStart:
		print 'GE_EXC, LuckyMountGashapon repeat opened'
	IsStart = True

def EndMountGashapon(param1, param2):
	global IsStart
	if param2 != CircularDefine.CA_LuckyGashaponMount:
		return
	
	if not IsStart:
		print 'GE_EXC, LuckyMountGashapon is already end'
	IsStart = False

def RequestCommonMountGshapon(role, param):
	'''
	请求普通坐骑扭蛋, 每次抽奖扭蛋一次
	@param role:
	@param param: None
	'''
	global IsStart
	if not IsStart:return 
	
	if role.GetLevel() < EnumGameConfig.MountGashaponLevel:
		return
	
	if role.GetDI8(EnumDayInt8.CommonMountGashaponTimes) >= EnumGameConfig.MountGashaponMaxTime:
		return
	if role.GetBindRMB() < EnumGameConfig.CommonMountGashaponCoast:
		return
	randomObj = MountGashapon_Dict.get(1)
	if not randomObj:
		return
	coding, cnt = randomObj.RandomOne()
	with TraCommonMountGashapon:
		role.IncDI8(EnumDayInt8.CommonMountGashaponTimes, 1)
		role.DecBindRMB(EnumGameConfig.CommonMountGashaponCoast)
		role.AddItem(coding, cnt)
		
	role.Msg(2, 0, GlobalPrompt.Reward_Tips + GlobalPrompt.Item_Tips % (coding, cnt))
		
	
def RequestGoodMountGshapon(role, param):
	'''
	请求高级坐骑扭蛋
	@param role:
	@param param: 抽奖次数（1,10）
	'''
	global IsStart
	if not IsStart:return 
	
	if param not in (1, 10):
		return
	
	if role.GetLevel() < EnumGameConfig.MountGashaponLevel:
		return
	needMoney = 0
	if not role.GetDI1(EnumDayInt1.LuckyGashponMount):
		#第一次半价
		needMoney += EnumGameConfig.GoodMountGashaponRMB / 2
		needMoney += EnumGameConfig.GoodMountGashaponRMB * (param - 1)
	else:
		needMoney += EnumGameConfig.GoodMountGashaponRMB * param
	if role.GetUnbindRMB_Q() < needMoney:
		return
	specialItemList = []
	itemsDict = {}
	itemsList = GetReared(2, param)
	with TraGoodMountGashapon:
		role.SetDI1(EnumDayInt1.LuckyGashponMount, 1)
		role.DecUnbindRMB_Q(needMoney)
		for (coding, cnt), special in itemsList:
			role.AddItem(coding, cnt)
			itemsDict[coding] = itemsDict.get(coding, 0) + cnt
			if special:
				specialItemList.append((coding, cnt))
	
	tips = ''
	for coding, cnt in itemsDict.iteritems():
		tips += GlobalPrompt.Item_Tips % (coding, cnt)
	role.Msg(2, 0, GlobalPrompt.Reward_Tips + tips)
	
	#广播消息
	BroadSpecial(role, 2, specialItemList)


def RequestSuperMountGshapon(role, param):
	'''
	请求极品坐骑扭蛋
	@param role:
	@param param: 抽奖次数（1,10）
	'''
	global IsStart
	if not IsStart:return 
	if param not in (1, 10):
		return
	
	if role.GetLevel() < EnumGameConfig.MountGashaponLevel:
		return
	needRMB = EnumGameConfig.SuperMountGashaponRMB * param
	if role.GetUnbindRMB_Q() < needRMB:
		return
	specialItemList = []
	itemsDict = {}
	itemsList = GetReared(3, param)
	with TraSuperMountGashapon:
		role.DecUnbindRMB_Q(needRMB)
		#增加万能碎片
		role.AddItem(EnumGameConfig.MasterChipCoding, EnumGameConfig.MasterChipCnt * param)
		
		for (coding, cnt), special in itemsList:
			role.AddItem(coding, cnt)
			itemsDict[coding] = itemsDict.get(coding, 0) + cnt
			if special:
				specialItemList.append((coding, cnt))
	
	#广播消息
	BroadSpecial(role, 3, specialItemList)
	tips = GlobalPrompt.Item_Tips % (EnumGameConfig.MasterChipCoding, EnumGameConfig.MasterChipCnt * param)
	for coding, cnt in itemsDict.iteritems():
		tips += GlobalPrompt.Item_Tips % (coding, cnt)
	role.Msg(2, 0, GlobalPrompt.Reward_Tips + tips)


def GetReared(rewardType, cnt):
	'''
	随机扭蛋奖励
	@param rewardType: 2:高级扭蛋, 3:极品扭蛋
	@param cnt: 抽奖次数
	'''
	randomObj = MountGashapon_Dict.get(rewardType)
	if not randomObj:
		return []
	items = []
	for _ in range(0, cnt):
		items.append(randomObj.RandomOne())
	return items


def BroadSpecial(role, GashaponType, itemsList):
	tmpRecord = []
	for coding, cnt in itemsList:
		tmpRecord.append((role.GetRoleName(), GashaponType, coding, cnt))
		if GashaponType == 2:
			cRoleMgr.Msg(1, 0, GlobalPrompt.MountGashaponGoodTip % (role.GetRoleName(), coding, cnt))
		elif GashaponType == 3:
			cRoleMgr.Msg(1, 0, GlobalPrompt.MountGashaponSuperTip % (role.GetRoleName(), coding, cnt))
	
	global GashaponRecord
	GashaponRecord.extend(tmpRecord)
	#同步获奖数据
	global OpenPanelSet
	for roleid in OpenPanelSet:
		tmpRole = cRoleMgr.FindRoleByRoleID(roleid)
		if not tmpRole:
			continue
		tmpRole.SendObj(MountGashaponAddData, tmpRecord)


def RequestOpenMountGshapon(role, param):
	'''
	打开坐骑扭蛋面板
	@param role:
	@param param: None
	'''
	global OpenPanelSet, GashaponRecord, MAXRECORD
	OpenPanelSet.add(role.GetRoleID())
	GashaponRecord = GashaponRecord[-50:]
	role.SendObj(MountGashaponData, GashaponRecord)
	

def RequestCloseMountGshapon(role, param):
	'''
	关闭坐骑扭蛋面板
	@param role:
	@param param: None
	'''
	global OpenPanelSet
	OpenPanelSet.discard(role.GetRoleID())

def RequestMountGshaponExchange(role, param):
	'''
	关闭坐骑扭蛋面板
	@param role:
	@param param: (index, cnt)
	'''
	global IsStart
	if not IsStart:return 
	
	index, num = param
	if num < 1:
		return
	if index not in MountGashaponExchange_Dict:
		return
	rewardObj = MountGashaponExchange_Dict.get(index)
	if not rewardObj:
		print "GE_EXC, The MountGashponExchange configuration error, where index = %s" % index
		return
	if role.GetLevel() < rewardObj.needLevel:
		return
	if role.ItemCnt(EnumGameConfig.MasterChipCoding) < rewardObj.needItemCnt * num:
		return
	coding, cnt = rewardObj.rewardItems
	with TraMountGashonExchange:
		role.AddItem(coding, cnt * num)
		role.DelItem(EnumGameConfig.MasterChipCoding, rewardObj.needItemCnt * num)
	
	role.Msg(2, 0, GlobalPrompt.Reward_Tips + GlobalPrompt.Item_Tips % (coding, cnt * num))
	

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		
		Event.RegEvent(Event.Eve_StartCircularActive, StartMountGashapon)
		Event.RegEvent(Event.Eve_EndCircularActive, EndMountGashapon)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestCommonMountGshapon", "请求普通坐骑扭蛋"), RequestCommonMountGshapon)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestGoodMountGshapon", "请求高级坐骑扭蛋"), RequestGoodMountGshapon)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestSuperMountGshapon", "请求极品坐骑扭蛋"), RequestSuperMountGshapon)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestOpenMountGshapon", "打开坐骑扭蛋面板"), RequestOpenMountGshapon)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestCloseMountGshapon", "关闭坐骑扭蛋面板"), RequestCloseMountGshapon)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestMountGshaponExchange", "坐骑扭蛋兑换"), RequestMountGshaponExchange)
