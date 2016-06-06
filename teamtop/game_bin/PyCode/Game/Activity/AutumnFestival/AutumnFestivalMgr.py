#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.AutumnFestival.AutumnFestivalMgr")
#===============================================================================
# 中秋活动 akm
#===============================================================================
import time
import datetime
from random import randint
import cRoleMgr
import cDateTime
import cNetMessage
import cComplexServer
from ComplexServer.Log import AutoLog
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Role import Event
from Game.Role.Data import EnumInt8, EnumDayInt1, EnumInt32, EnumDayInt8
from Game.Activity.AutumnFestival import AutumnFestivalConfig

if "_HasLoad" not in dir():
	IS_START_DAILY = False				#中秋登陆开关
	IS_START_LATTERY = False			#中秋搏饼开关
	
	AF_Lattey_Master_Record_List = []	#缓存搏饼大奖记录  EnumGameConfig.AF_MasterRecordNum条
	
	AF_Lattery_RoleIds_List = []			#缓存打开搏饼面板的roleId
	
	AutumnFestivalDailyState = AutoMessage.AllotMessage("AutumnFestivalDailyState", "中秋登陆礼包活动状态")
	AutumnFestivalLatteryState = AutoMessage.AllotMessage('AutumnFestivalLatteryState', "中秋搏饼活动状态")	
	
	AFLatteryResultMsg = AutoMessage.AllotMessage("AFLatteryResultMsg", "中秋搏饼结果")
	AFLatteryMasterRecord = AutoMessage.AllotMessage('AFLatteryMasterRecord', "中秋搏饼大奖记录")
	
	Tra_AFDailyLiBao = AutoLog.AutoTransaction("Tra_AFDailyLiBao", "中秋每日登陆礼包领取")
	Tra_AFLatteryReward = AutoLog.AutoTransaction("Tra_AFLatteryReward", "中秋搏饼奖励")
	Tra_AFLatteryNumExchange = AutoLog.AutoTransaction("Tra_AFLatteryNumExchange","神石充值数兑换中秋搏饼次数")

#============= 活动控制 ====================
#启服之后根据当前时间和活动配置时间 处理各个tick
def Initialize():	
	'''
	初始化活动tick
	'''
	nowDate = (cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second())
	nowTime = int(time.mktime(datetime.datetime(cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second()).timetuple()))
	
	for _,config in AutumnFestivalConfig.AFC_CONFIG_DICT.iteritems():
		beginTime = int(time.mktime(datetime.datetime(*config.beginDate).timetuple()))
		endTime = int(time.mktime(datetime.datetime(*config.endDate).timetuple()))
		AF_Type = config.id
		
		if config.beginDate <= nowDate < config.endDate:
			#开启 并注册结束tick
			AF_Start(None,AF_Type)
			cComplexServer.RegTick(endTime - nowTime, AF_End, AF_Type)
		elif nowDate < config.beginDate:
			#注册开启和结束的tick
			cComplexServer.RegTick(beginTime - nowTime, AF_Start, AF_Type)
			cComplexServer.RegTick(endTime - nowTime, AF_End, AF_Type)

def AF_Start(callargv, regparam):
	'''
	开启中秋AF_Type活动
	'''
	AF_Type = regparam
	if 1 > AF_Type or AF_Type > 2:
		print "GE_EXC,error AF_Type(%s) on AF_Start" % AF_Type
		return
	
	global IS_START_DAILY
	global IS_START_LATTERY	
	global AF_Lattery_RoleIds_List
	global AF_Lattey_Master_Record_List
	
	if AF_Type == 1:
		#开启中秋登陆处理
		IS_START_DAILY = True		
		cNetMessage.PackPyMsg(AutumnFestivalDailyState, 1)
	elif AF_Type == 2:
		#开启中秋搏饼处理
		IS_START_LATTERY = True
		AF_Lattery_RoleIds_List = []
		AF_Lattey_Master_Record_List = []
		cNetMessage.PackPyMsg(AutumnFestivalLatteryState, 1)
	else:
		pass	
	
	#广播通知开启
	cRoleMgr.BroadMsg()

def AF_End(callargv, regparam):
	'''
	结束中秋AF_Type活动
	'''
	AF_Type = regparam
	if 1 > AF_Type or AF_Type > 2:
		print "GE_EXC,error AF_Type(%s) on AF_End" % AF_Type
		return
	
	global IS_START_DAILY
	global IS_START_LATTERY	
	global AF_Lattery_RoleIds_List
	global AF_Lattey_Master_Record_List
	
	if AF_Type == 1:
		#关闭中秋登陆处理
		IS_START_DAILY = False
		cNetMessage.PackPyMsg(AutumnFestivalDailyState, 0)
	elif AF_Type == 2:
		#关闭中秋搏饼处理
		IS_START_LATTERY = False
		AF_Lattery_RoleIds_List = []
		AF_Lattey_Master_Record_List = []
		cNetMessage.PackPyMsg(AutumnFestivalLatteryState, 0)
	else:
		pass
	
	#广播通知开启
	cRoleMgr.BroadMsg()
	
#============= 客户端请求 ====================
def RequestGetAFDailyLiBao(role,param):
	'''
	玩家请求领取中秋登陆礼包
	@param role:
	'''	
	#活动是否开启
	if not IS_START_DAILY:
		return
	
	#等级是否足够
	if role.GetLevel() < EnumGameConfig.AF_DailyLiBaoNeedLevel:
		return
	
	#今日是否已经领取
	IsGotToDay = role.GetDI1(EnumDayInt1.AFDailyLiBaoDay)
	if IsGotToDay:
		return
	
	#之前经领取此礼包id
	GotLiBaoID = role.GetI8(EnumInt8.AFDailyLiBaoID)	
	
	#不存在新的礼包
	LiBaoID = GotLiBaoID + 1
	if LiBaoID not in AutumnFestivalConfig.AF_DAILY_LIBAO_DICT:
		return
	
	#礼包配置
	cfg = AutumnFestivalConfig.AF_DAILY_LIBAO_DICT[LiBaoID]
	if not cfg:
		return
	
	#process
	with Tra_AFDailyLiBao:
		role.SetDI1(EnumDayInt1.AFDailyLiBaoDay, 1)
		role.SetI8(EnumInt8.AFDailyLiBaoID, LiBaoID)
		
		itemRewardPrompt = ""		
		for coding, cnt in cfg.items:
			role.AddItem(coding, cnt)
			itemRewardPrompt += GlobalPrompt.AF_LatteryRewardMsg_Item % (coding, cnt)
			
		role.Msg(2, 0, GlobalPrompt.AF_LatteryRewardMsg_Head + itemRewardPrompt)		

def RequestIncAFLatteryNum(role, param):
	'''
	玩家请求领取中秋登陆礼包
	玩家请求增加搏饼次数----（活动期间神石充值兑换）
	@param role:
	@param param:领取的额外搏饼次数对应的充值神石数
	'''	
	#活动未开启
	if not IS_START_LATTERY:
		return
	
	#索引不存在
	index = param
	if index not in AutumnFestivalConfig.AF_EXTRA_LATTERY_DICT:
		return
	
	cfg = AutumnFestivalConfig.AF_EXTRA_LATTERY_DICT[index]
	if not cfg:
		return
	
	#充值神石数不满足
	todayBuyRMB_Q = role.GetDayBuyUnbindRMB_Q()
	if todayBuyRMB_Q < cfg.value:
		return
	
	#已领取
	todayExtraAFLatteryRecord = role.GetI32(EnumInt32.DayExtraAFLatteryRecord)
	if todayExtraAFLatteryRecord & index:
		return	
	
	#process
	with Tra_AFLatteryNumExchange:
		role.SetI32(EnumInt32.DayExtraAFLatteryRecord, todayExtraAFLatteryRecord + index)	
		role.SetI8(EnumInt8.AFLatterySpecialNum, role.GetI8(EnumInt8.AFLatterySpecialNum) + 1)

def RequestAFLattery(role,param):
	'''
	响应玩家摇骰子请求
	'''
	#活动未开启
	if not IS_START_LATTERY:
		return
	
	#等级不足
	if role.GetLevel() < EnumGameConfig.AF_LatteryNeedLevel:
		return
	
	#剩余次数不足
	usedFreeNum = role.GetDI8(EnumDayInt8.AF_LatteryFreeNumUsed)
	dailyBoxNum = role.GetDI8(EnumDayInt8.AF_LatteryDailyBoxNum)
	specialNum = role.GetI8(EnumInt8.AFLatterySpecialNum)	
	if usedFreeNum >= EnumGameConfig.AF_LatteryInitNomalNum and dailyBoxNum < 1 and specialNum < 1:
		return
	
	diceType, diceList = RollDice()	
	result = [diceType,diceList]
	
	#免费次数-> 今日必做宝箱次数 -> 神石重置兑换次数
	if usedFreeNum < EnumGameConfig.AF_LatteryInitNomalNum:
		role.SetDI8(EnumDayInt8.AF_LatteryFreeNumUsed, usedFreeNum + 1)
	elif dailyBoxNum > 0:
		role.SetDI8(EnumDayInt8.AF_LatteryDailyBoxNum, dailyBoxNum - 1)
	elif specialNum > 0:
		role.SetI8(EnumInt8.AFLatterySpecialNum, specialNum - 1)
	
	role.SendObjAndBack(AFLatteryResultMsg, result, 5, LatteryCallBack, diceType)

def RequetOpenAFLatteryPanel(role,param):
	'''
	打开搏饼面板
	'''
	if not IS_START_LATTERY:
		return
	
	if role.GetLevel() < EnumGameConfig.AF_LatteryNeedLevel:
		return
	
	global AF_Lattery_RoleIds_List
	if role.GetRoleID() not in AF_Lattery_RoleIds_List:
		AF_Lattery_RoleIds_List.append(role.GetRoleID())	
	
	role.SendObj(AFLatteryMasterRecord, AF_Lattey_Master_Record_List)

def RequetCloseAFLatteryPanel(role,param):
	'''
	关闭搏饼面板
	'''
	if not IS_START_DAILY:
		return
	
	if role.GetLevel() < EnumGameConfig.AF_LatteryNeedLevel:
		return
	
	global AF_Lattery_RoleIds_List
	if role.GetRoleID() not in AF_Lattery_RoleIds_List:
		return
	
	AF_Lattery_RoleIds_List.remove(role.GetRoleID())

def RollDice():
	'''
	摇骰子
	@return: diceType 骰子对应奖励类型【1-9】
	@return: diceList 骰子点数集合
	'''
	diceType = 0
	diceList = []
	
	latteryValue = 0	
	for _ in range(EnumGameConfig.AF_LatteryRollNum):
		tmpDice = randint(1,6)
		latteryValue += EnumGameConfig.AF_LatteryDiceValue.get(tmpDice,0)
		diceList.append(tmpDice)
	
	# {1:100000,2:10000,3:1000,4:100,5:10,6:1}-->中秋节日快乐
	if latteryValue == 420000:
		#状元插金花  4个中，2个秋
		diceType = 9
	elif str(latteryValue).count('5') > 0 or str(latteryValue).count('6') > 0:
		#五王 5个或以上相同的字
		diceType = 8
	elif latteryValue >= 400000:
		#状元  4个中
		diceType = 7
	elif latteryValue == 111111:
		#对堂 无重字
		diceType = 6
	elif latteryValue >= 300000:
		#三红 3个中 
		diceType = 5
	elif str(latteryValue).count('4') > 0:
		#四进  4个相同的字，不包括4个中
		diceType = 4
	elif latteryValue >= 200000:
		#二举  2个中
		diceType = 3
	elif latteryValue >= 100000:
		#一秀 1个中
		diceType = 2
	else:
		#赏
		diceType = 1	
	
	return diceType,diceList	

def LatteryCallBack(role, callargv, regparam):
	'''
	搏饼回调
	@param regparam: 搏饼奖励类型
	'''
	dictType = regparam
	if dictType not in AutumnFestivalConfig.AF_LATTERY_REWARD_DICT:
		print "GE_EXC,LatteryCallBack error dictType(%s)" % dictType
		return
	
	cfg = AutumnFestivalConfig.AF_LATTERY_REWARD_DICT[dictType]
	if not cfg:
		print "GE_EXC,LatteryCallBack cfg error(%s)" % cfg
		return	
	
	#状元以上的 ::公告 & 大奖记录 
	if dictType > EnumGameConfig.AF_LatteryMasterTypeMin:
		global AF_Lattey_Master_Record_List
		AF_Lattey_Master_Record_List.append((role.GetRoleName(), dictType))
		
		relativeSize = len(AF_Lattey_Master_Record_List) - EnumGameConfig.AF_MasterRecordNum
		if relativeSize > 0:
			#记录数量超过 截断
			AF_Lattey_Master_Record_List = AF_Lattey_Master_Record_List[relativeSize:]
		
		#发送最新记录给当前打开面板的玩家
		for roleId in AF_Lattery_RoleIds_List:
			member = cRoleMgr.FindRoleByRoleID(roleId) 
			if not member:
				AF_Lattery_RoleIds_List.remove(roleId)
			member.SendObj(AFLatteryMasterRecord, AF_Lattey_Master_Record_List)
	
	#process
	AFLatteryRewardPromptMsg = ""
	AFLatteryRewardNotifyMsgList = []	
	with Tra_AFLatteryReward:
		for coding, cnt in cfg.nomalItems:
			AFLatteryRewardPromptMsg += GlobalPrompt.AF_LatteryRewardMsg_Item % (coding, cnt)
			AFLatteryRewardNotifyMsgList.append(GlobalPrompt.AF_LatteryRewardMsg_ItemEx % (coding, cnt))
			role.AddItem(coding, cnt)
		
		if cfg.extraItems:
			for coding, cnt in cfg.extraItems:
				AFLatteryRewardPromptMsg += GlobalPrompt.AF_LatteryRewardMsg_Item % (coding, cnt)
				AFLatteryRewardNotifyMsgList.append(GlobalPrompt.AF_LatteryRewardMsg_ItemEx % (coding, cnt))
				role.AddItem(coding, cnt)	
		
		if cfg.rewardCoin > 0:
			AFLatteryRewardPromptMsg += GlobalPrompt.AF_LatteryRewardMsg_Money % (cfg.rewardCoin)
			AFLatteryRewardNotifyMsgList.append(GlobalPrompt.AF_LatteryRewardMsg_Money % (cfg.rewardCoin))
			role.IncMoney(cfg.rewardCoin)
	
	#获得奖励提示
	rewardPrompt = GlobalPrompt.AF_LatteryRewardMsg_Head + AFLatteryRewardPromptMsg
	role.Msg(2, 0, rewardPrompt)
	
	# 搏饼大奖公告
	if dictType > EnumGameConfig.AF_LatteryMasterTypeMin and len(AFLatteryRewardNotifyMsgList) > 0:
		AFLatteryRewardNotifyMsg = GlobalPrompt.AF_LatteryRewardNotifySep.join(AFLatteryRewardNotifyMsgList)
		rewardNotify =  GlobalPrompt.AF_LatteryMasterReward % (role.GetRoleName(), GlobalPrompt.AF_LatteryType2Name(dictType), AFLatteryRewardNotifyMsg) 
		cRoleMgr.Msg(11, 0, rewardNotify)

#============= 事件处理 ====================
def OnSyncRoleOtherData(role, param):
	'''
	登陆下推已开启的中秋活动
	@param role:
	@param param:
	'''
	if IS_START_DAILY:
		role.SendObj(AutumnFestivalDailyState, 1)
		
	if IS_START_LATTERY:
		role.SendObj(AutumnFestivalLatteryState, 1)

def OnRoleDayClear(role,param):
	'''
	每日清除
	'''
	#清除神石充值兑换搏饼次数记录
	role.SetI32(EnumInt32.DayExtraAFLatteryRecord, 0)



def OnClientLostorExit(role, param):
	'''
	客户端掉线或退出的处理 
	@param role:
	@param param:
	'''	
	if not IS_START_LATTERY:
		return
	
	global AF_Lattery_RoleIds_List
	if role.GetRoleID() not in AF_Lattery_RoleIds_List:
		return
	
	AF_Lattery_RoleIds_List.remove(role.GetRoleID())
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
	
	if Environment.HasLogic and not Environment.IsCross:
		Initialize()
		
		Event.RegEvent(Event.Eve_ClientLost, OnClientLostorExit)
		Event.RegEvent(Event.Eve_BeforeExit, OnClientLostorExit)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)

		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestGetAFDailyLiBao", "玩家请求领取中秋登陆礼包"), RequestGetAFDailyLiBao)	
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestIncAFLatteryNum", "玩家请求增加中秋搏饼次数"), RequestIncAFLatteryNum)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequetOpenAFLatteryPanel", "玩家请求打开中秋搏饼面板"), RequetOpenAFLatteryPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequetCloseAFLatteryPanel", "玩家请求关闭中秋搏饼面板"), RequetCloseAFLatteryPanel)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestAFLattery", "玩家请求搏饼摇骰子"), RequestAFLattery)
