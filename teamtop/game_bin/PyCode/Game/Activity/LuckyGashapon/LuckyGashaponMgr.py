# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.LuckyGashapon.LuckyGashaponMgr")
#===============================================================================
# 时装扭蛋逻辑控制 @author: Gaoshuai 2016-02-15
#===============================================================================
import cRoleMgr
import Environment
from Game.Role import Event
from Game.Activity import CircularDefine
from Game.Role.Data import EnumDayInt1, EnumDayInt8
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from Game.Activity.LuckyGashapon.LuckyGashaponConfig import FashionGashaponReward_Dict


if "_HasLoad" not in dir():
	# 消息
	GashaponRecordData = AutoMessage.AllotMessage("GashaponRecordData", "扭蛋获奖记录")
	GashaponAddRecordData = AutoMessage.AllotMessage("GashaponAddRecordData", "扭蛋获奖增加记录")
	# 日志
	TraCommonGashapon = AutoLog.AutoTransaction("TraCommonGashapon", "普通扭蛋")
	TraGoodGashapon = AutoLog.AutoTransaction("TraGoodGashapon", "高级扭蛋")
	TraSuperGashapon = AutoLog.AutoTransaction("TraSuperGashapon", "极品扭蛋")
	
	MAXRECORD = 50		#最大记录条数
	GashaponRecord = []
	OpenPanelSet = set()
	IsStart = False

def StartCircularActive(param1, param2):
	global IsStart
	if param2 != CircularDefine.CA_LuckyGashaponFashion:
		return
	
	if IsStart:
		print 'GE_EXC, LuckyFashionGashapon repeat opened'
	IsStart = True

def EndCircularActive(param1, param2):
	global IsStart
	if param2 != CircularDefine.CA_LuckyGashaponFashion:
		return
	if not IsStart:
		print 'GE_EXC, LuckyFashionGashapon is already end'
	IsStart = False

def RequestCommonGshapon(role, param):
	'''
	请求普通扭蛋, 每次抽奖扭蛋一次
	@param role:
	@param param: None
	'''
	global IsStart
	if not IsStart:return 
	
	if role.GetLevel() < EnumGameConfig.GashaponFashionLevel:
		return
	
	if role.GetDI8(EnumDayInt8.CommonGashaponTimes) >= EnumGameConfig.GashaponMaxTime:
		return
	if role.GetBindRMB() < EnumGameConfig.CommonGashaponCoast:
		return
	randomObj = FashionGashaponReward_Dict.get(1)
	if not randomObj:
		return
	coding, cnt = randomObj.RandomOne()
	with TraCommonGashapon:
		role.IncDI8(EnumDayInt8.CommonGashaponTimes, 1)
		role.DecBindRMB(EnumGameConfig.CommonGashaponCoast)
		role.AddItem(coding, cnt)
		
	role.Msg(2, 0, GlobalPrompt.Reward_Tips + GlobalPrompt.Item_Tips % (coding, cnt))
		
	
def RequestGoodGshapon(role, param):
	'''
	请求高级扭蛋
	@param role:
	@param param: 抽奖次数（1,10）
	'''
	global IsStart
	if not IsStart:return 
	
	if param not in (1, 10):
		return
	
	if role.GetLevel() < EnumGameConfig.GashaponFashionLevel:
		return
	needMoney = 0
	if not role.GetDI1(EnumDayInt1.LuckyGashponFashion):
		#第一次半价
		needMoney += EnumGameConfig.GoodGashaponRMB / 2
		needMoney += EnumGameConfig.GoodGashaponRMB * (param - 1)
	else:
		needMoney += EnumGameConfig.GoodGashaponRMB * param
	if role.GetUnbindRMB_Q() < needMoney:
		return
	specialItemList = []
	itemsDict = {}
	with TraGoodGashapon:
		role.SetDI1(EnumDayInt1.LuckyGashponFashion, 1)
		role.DecUnbindRMB_Q(needMoney)
		itemsList = GetReared(2,param)
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


def RequestSuperGshapon(role, param):
	'''
	请求极品扭蛋
	@param role:
	@param param: 抽奖次数（1,10）
	'''
	global IsStart
	if not IsStart:return 
	
	if param not in (1, 10):
		return
	
	if role.GetLevel() < EnumGameConfig.GashaponFashionLevel:
		return
	
	if role.ItemCnt(EnumGameConfig.SuperGashaponItem) < param:
		return
	
	with TraSuperGashapon:
		role.DelItem(EnumGameConfig.SuperGashaponItem,param)
		itemsList = GetReared(3,param)
		for items in itemsList:
			role.AddItem(*items)
	
	#广播消息
	BroadSpecial(role, 3, itemsList)


def GetReared(rewardType, cnt):
	'''
	随机扭蛋奖励
	@param rewardType: 2:高级扭蛋, 3:极品扭蛋
	@param cnt: 抽奖次数
	'''
	randomObj = FashionGashaponReward_Dict.get(rewardType)
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
			cRoleMgr.Msg(1, 0, GlobalPrompt.GashaponGoodTip % (role.GetRoleName(), coding, cnt))
		elif GashaponType == 3:
			cRoleMgr.Msg(1, 0, GlobalPrompt.GashaponSuperTip % (role.GetRoleName(), coding, cnt))
	
	global GashaponRecord
	GashaponRecord.extend(tmpRecord)
	#同步获奖数据
	global OpenPanelSet
	for roleid in OpenPanelSet:
		tmpRole = cRoleMgr.FindRoleByRoleID(roleid)
		if not tmpRole:
			continue
		tmpRole.SendObj(GashaponAddRecordData, tmpRecord)


def RequestOpenGshaponPanel(role, param):
	'''
	打开扭蛋面板
	@param role:
	@param param: None
	'''
	global OpenPanelSet, GashaponRecord, MAXRECORD
	OpenPanelSet.add(role.GetRoleID())
	GashaponRecord = GashaponRecord[-50:]
	role.SendObj(GashaponRecordData, GashaponRecord)
	

def RequestCloseGshaponPanel(role, param):
	'''
	关闭扭蛋面板
	@param role:
	@param param: None
	'''
	global OpenPanelSet
	OpenPanelSet.discard(role.GetRoleID())


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		
		Event.RegEvent(Event.Eve_StartCircularActive, StartCircularActive)
		Event.RegEvent(Event.Eve_EndCircularActive, EndCircularActive)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestCommonGshapon", "请求普通扭蛋"), RequestCommonGshapon)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestGoodGshapon", "请求高级扭蛋"), RequestGoodGshapon)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestSuperGshapon", "请求极品扭蛋"), RequestSuperGshapon)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestOpenGshaponPanel", "打开扭蛋面板"), RequestOpenGshaponPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestCloseGshaponPanel", "关闭扭蛋面板"), RequestCloseGshaponPanel)
