#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.NewYearDay.NewYearDayPigMgr")
#===============================================================================
# 元旦好福利
#===============================================================================
import cNetMessage
import Environment
import cRoleMgr
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Activity import CircularDefine
from Game.Role.Data import EnumObj
from Game.Activity.NewYearDay import NewYearDayPigconfig
from Common.Other import GlobalPrompt, EnumGameConfig
from Game.Role import Event
from Game.Activity.PassionAct.PassionDefine import PassionNewYearPig

if "_HasLoad" not in dir():
	IsStart = False
	#元旦好福利消息同步
	NewYearDayPigStart = AutoMessage.AllotMessage("NewYearDayPigStart", "元旦金猪活动开启")
	NewYearDayPig_TaskData = AutoMessage.AllotMessage("NewYearDayPig_TaskData", "元旦金猪任务数据同步")
	NewYearDayPigShop_Data = AutoMessage.AllotMessage("NewYearDayPigShop_Data", "元旦金猪兑换商店同步")
	NewYearDayPigAmount = AutoMessage.AllotMessage("NewYearDayPigAmount", "元旦金猪数量同步")
	#元旦好福利活动的日志
	NewYearDayPig_Task_Log = AutoLog.AutoTransaction("NewYearDayPig_Task_Log", "元旦活动金猪数据记录")
	NewYearDayPigShop_Log = AutoLog.AutoTransaction("NewYearDayPigShop_Log", "元旦活动兑换商店记录")


def OpenActive(callArgv, param):
	if CircularDefine.CA_NewYearDayPig != param :
		return
	global IsStart
	if IsStart :
		print "GE_EXC, NewYearDayEgg has Started"
	IsStart = True
	#通知客户端活动开启
	cNetMessage.PackPyMsg(NewYearDayPigStart, 1)

def CloseActive(callArgv, param):
	if CircularDefine.CA_NewYearDayPig != param :
		return
	global IsStart
	if not IsStart :
		print "GE_EXC, NewYearDayEgg has Closed"
	IsStart = False
	cNetMessage.PackPyMsg(NewYearDayPigStart, 0)


#=====================================================================
# 客户端请求
#=====================================================================
def OpenNewYearDayPigShop(role, param=1):
	global IsStart
	if not IsStart :
		return
	if role.GetLevel() < EnumGameConfig.NewYearDayMinLevel :
		return
	NewYearPig_Data = role.GetObj(EnumObj.PassionActData)[PassionNewYearPig]
	PigShop = NewYearPig_Data[1]
	PigAmount = NewYearPig_Data[2]
	TaskData =  NewYearPig_Data[3]
	#同步客户端
	role.SendObj(NewYearDayPigShop_Data, PigShop)
	role.SendObj(NewYearDayPigAmount, PigAmount)
	role.SendObj(NewYearDayPig_TaskData, TaskData)
	

#领取金猪
def GetNewYearDayPigAmount(role, index):
	global IsStart
	if not IsStart :
		return
	if role.GetLevel() < EnumGameConfig.NewYearDayMinLevel :
		return
	TaskData = role.GetObj(EnumObj.PassionActData)[PassionNewYearPig][3]
	if index not in TaskData :
		return
	if TaskData[index] != 1 :
		return
	with NewYearDayPig_Task_Log :
		TaskData[index] = 2
		PigAmount = role.GetObj(EnumObj.PassionActData)[PassionNewYearPig][2]
		PigAmount += NewYearDayPigconfig.GetPigAmount[index]
		role.GetObj(EnumObj.PassionActData)[PassionNewYearPig][2] = PigAmount
		tips =""
		tips += GlobalPrompt.NewYearDayPigAmountTips % NewYearDayPigconfig.GetPigAmount[index]
	role.Msg(2, 0, tips)
	role.SendObj(NewYearDayPig_TaskData, TaskData)
	role.SendObj(NewYearDayPigAmount, PigAmount)

#兑换物品
def BuyPigShopItem(role, param):
	'''
	商城[0(coding,cnt),1needcnt(需要金猪的数量),2leftcnt(剩余可兑换的数量), 等级区间]
	'''
	global IsStart
	if not IsStart:
		return
	index, numbers = param
	if role.GetLevel() < EnumGameConfig.NewYearDayMinLevel :
		return
	if numbers < 1:
		return
	Shop = NewYearDayPigconfig.PigShop
	NewYearPigDate = role.GetObj(EnumObj.PassionActData)[PassionNewYearPig]
	if 2 not in NewYearPigDate:
		NewYearPigDate[2] = 0
	PigAmount = NewYearPigDate[2]
	Item = Shop.get(index)
	if not Item :
		print "GE_EXC, has no index %s in BuyPigShopItem" % index
		return
	#小于等级区间的最少等级
	if role.GetLevel() < Item.NeedLevel[0] or role.GetLevel() >Item.NeedLevel[1]:
		return
	#金猪数量不足
	PigNeeds = Item.NeedCnt*numbers
	if PigNeeds > PigAmount :
		return
	#剩余数量不足
	if index not in NewYearPigDate[1]:
		NewYearPigDate[1][index] = Item.LeftCounts 
	LeftCnts = NewYearPigDate[1][index]
	if LeftCnts < numbers :
		return
	#兑换奖励
	with NewYearDayPigShop_Log :
		#减去所需的金猪数量
		PigAmount -= PigNeeds
		NewYearPigDate[2] = PigAmount
		LeftCnts -= numbers
		tips = ""
		tips += GlobalPrompt.Reward_Tips
		itemcoding, cnt = Item.rewardItems
		role.AddItem(itemcoding, cnt*numbers)
		tips += GlobalPrompt.Item_Tips % (itemcoding, cnt*numbers)
		role.Msg(2, 0, tips)
	NewYearPigDate[1][index] = LeftCnts
	role.SendObj(NewYearDayPigShop_Data, NewYearPigDate[1])
	role.SendObj(NewYearDayPigAmount, PigAmount)
	
#=======================================================================
#完成任务触发
#=======================================================================
def AfterFinishTask(role, param = None):
	'''
	任务完成触发数据记录处理
	'''
	global IsStart
	if not IsStart:
		return
	taskIndex, isSync = param
	if taskIndex not in NewYearDayPigconfig.GetPigAmount:
		return 
	NewYearPigDate = role.GetObj(EnumObj.PassionActData)[PassionNewYearPig]
	if 3 not in NewYearPigDate :
		NewYearPigDate[3] = {}
	CRTaskDataDict = NewYearPigDate[3]
	if taskIndex not in CRTaskDataDict:
		CRTaskDataDict[taskIndex] = 0
	if CRTaskDataDict[taskIndex] :
		return
	CRTaskDataDict[taskIndex] = 1
	if isSync:
		role.SendObj(NewYearDayPig_TaskData, CRTaskDataDict)


#每天重新初始化数据
def ClearAfterNewDay(role, param=0):
	global IsStart
	if not IsStart:
		return
	if role.GetLevel() < EnumGameConfig.NewYearDayMinLevel :
		return
	NewYearPig_Data = role.GetObj(EnumObj.PassionActData)[PassionNewYearPig]
	#初始化任务数据
	TaskDate = {}
	for keys in NewYearDayPigconfig.GetPigAmount.iterkeys() :
			TaskDate[keys] = 0
	#初始化商店数据
	PigShop = {}
	NewYearPig_Data[1], NewYearPig_Data[3] = PigShop, TaskDate


def StateicPig(role, param):
	'''
	检测对象是否存在
	'''
	if PassionNewYearPig not in role.GetObj(EnumObj.PassionActData) :
		role.GetObj(EnumObj.PassionActData)[PassionNewYearPig] = {}
	NewYearPig_Data = role.GetObj(EnumObj.PassionActData)[PassionNewYearPig]
	if 1 not in NewYearPig_Data:
		PigShop = {}
		NewYearPig_Data[1] = PigShop
	if 2 not in NewYearPig_Data:
		NewYearPig_Data[2] = 0
		
	if 3 not in NewYearPig_Data:
		TaskDate = {}
		for keys in NewYearDayPigconfig.GetPigAmount.iterkeys() :
			TaskDate[keys] = 0
		NewYearPig_Data[3] = TaskDate

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("OpenNewYearDayPigShop", "打开元旦金猪面板"), OpenNewYearDayPigShop)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GetNewYearDayPigAmount", "领取元旦金猪"), GetNewYearDayPigAmount)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("BuyPigShopItem", "金猪兑换"), BuyPigShopItem)
		Event.RegEvent(Event.Eve_StartCircularActive, OpenActive)
		Event.RegEvent(Event.Eve_EndCircularActive, CloseActive)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OpenNewYearDayPigShop)
		Event.RegEvent(Event.Eve_RoleDayClear, ClearAfterNewDay)
		Event.RegEvent(Event.Eve_NewYearDayPigTask, AfterFinishTask)
		Event.RegEvent(Event.Eve_InitRolePyObj, StateicPig)
