#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DoubleTwelve.GroupBuyPartyMgr")
#===============================================================================
# 团购派对Mgr
#===============================================================================
import cRoleMgr
import cDateTime
import cNetMessage
import cComplexServer
import Environment
from Common.Message import AutoMessage
from Common.Other import GlobalDataDefine, EnumAward, EnumGameConfig, GlobalPrompt
from ComplexServer.API import GlobalHttp
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Persistence import Contain
from Game.Role.Data import EnumDayInt1
from Game.Activity.Award import AwardMgr
from Game.Activity.DoubleTwelve import GroupBuyPartyConfig

GBP_STATUS_CLOSE = 0
GPB_STATUS_OPEN = 1
GBP_DELAY_SECONDS = 60
ONE_MINUTE_SECONDS = 60				#一分钟秒数
FIVE_MINUTE_SECONDS = 5 * 60		#五分钟秒数 
FIFTY_FIVE_MIN_SECONDS = 55 * 60	#55分钟秒数
ONE_DAY_SECONDS = 24 * 60 * 60		#一天的总秒数

ITEMINDEX_ONE = 1
ITEMINDEX_TWO = 2

if "_HasLoad" not in dir():
	IS_START = False	#活动开关标志
	ENDTIME = 0			#活动结束时间戳
	GBP_DAYINDEX = 0	#活动开启天数
	GBP_GLOBALBUYCOUNT_DICT = {}	#缓存上个整点全局购买总数{itemIndex:count,}
	
	Tra_GroupBuyParty_BuyGood = AutoLog.AutoTransaction("Tra_GroupBuyParty_BuyGood", "团购派对购买商品")
	
	GroupBuyParty_ActiveStatus_Sync = AutoMessage.AllotMessage("GroupBuyParty_ActiveStatus_Sync", "同步团购派对活动状态")
	GroupBuyParty_DayIndex_Sync = AutoMessage.AllotMessage("GroupBuyParty_DayIndex_Sync", "同步团购团购开启天数")
	GroupBuyParty_BuyCount_Sync = AutoMessage.AllotMessage("GroupBuyParty_BuyCount_Sync", "团购派对同步购买总数")

#### 活动控制 start ####
def OnStartGroupBuyParty(callArgv, regparam):
	'''
	开启活动
	'''
	global IS_START
	global ENDTIME
	global GBP_GLOBALBUYCOUNT_DICT
	if IS_START:
		print "GE_EXC,repeat open GroupBuyParty"
		return
	
	IS_START = True
	ENDTIME = regparam
	GBP_GLOBALBUYCOUNT_DICT.clear()
	CalculateDayIndex()
	cNetMessage.PackPyMsg(GroupBuyParty_ActiveStatus_Sync, (GPB_STATUS_OPEN, ENDTIME))
	cRoleMgr.BroadMsg()
	cNetMessage.PackPyMsg(GroupBuyParty_DayIndex_Sync, GBP_DAYINDEX)
	cRoleMgr.BroadMsg()

def OnEndGroupBuyParty(callArgv, regparam):
	'''
	结束活动 已处理成延迟GBP_DELAY_SECONDS结束活动
	'''
	global IS_START
	global GBP_GLOBALBUYCOUNT_DICT
	if not IS_START:
		print "GE_EXC, end GroupBuyParty while not open"
		return
	
	IS_START = False
	GBP_GLOBALBUYCOUNT_DICT.clear()
	cNetMessage.PackPyMsg(GroupBuyParty_ActiveStatus_Sync, (GBP_STATUS_CLOSE, ENDTIME))
	cRoleMgr.BroadMsg()
	
#### 请求 start ####
def OnOpenPanel(role, msg = None):
	'''
	团购派对同步购买总数
	同步团购团购开启天数
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.DoubleTwelve_NeedLevel:
		return
	
	role.SendObj(GroupBuyParty_DayIndex_Sync, GBP_DAYINDEX)
	role.SendObj(GroupBuyParty_BuyCount_Sync, GBP_GLOBALBUYCOUNT_DICT)

def OnBuyGood(role, msg):
	'''
	团购派对请求购买商品
	@param msg: itemIndex 
	'''
	if not IS_START:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.DoubleTwelve_NeedLevel:
		return
	
	#是否已购买
	itemIndex = msg
	if itemIndex == ITEMINDEX_ONE:
		if role.GetDI1(EnumDayInt1.GroupBuyPartyBuyItemOne):
			return
	elif itemIndex == ITEMINDEX_TWO:
		if role.GetDI1(EnumDayInt1.GroupBuyPartyBuyItemTwo):
			return
	else:
		return
	
	#23:55分之后 0:01分之前 限制购买 活动延迟一分钟结束 避免先结束再发奖导致无法发最后一天的解锁奖励
	todaySeconds = cDateTime.Hour() * 3600 + cDateTime.Minute() * 60 + cDateTime.Second()
	if ONE_DAY_SECONDS - todaySeconds < FIVE_MINUTE_SECONDS:
		role.Msg(2, 0, GlobalPrompt.GroupBuyParty_Tips_LastFiveMinute_Limit)
		return
	
	if todaySeconds < ONE_MINUTE_SECONDS:
		role.Msg(2, 0, GlobalPrompt.GroupBuyParty_Tips_FirstOneMinute_Limit)
		return
	
	#获取商品配置
	goodCfg = GroupBuyPartyConfig.GetGoodCfgByIndexAndLevel(GBP_DAYINDEX, itemIndex, roleLevel)
	if not goodCfg:
		print "GE_EXC, OnBuyGood:: can not get goodCfg by GBP_DAYINDEX(%s), itemIndex(%s), roleLevel(%s)" % (GBP_DAYINDEX, itemIndex, roleLevel)
		return
	
	#神石不足
	needUnbindRMB = goodCfg.needRMB
	if role.GetUnbindRMB() < needUnbindRMB:
		return
	
	#process
	roleId = role.GetRoleID()
	coding, cnt = goodCfg.item
	global GroupBuyParty_BuyRecord_Dict
	with Tra_GroupBuyParty_BuyGood:
		#扣除神石
		role.DecUnbindRMB(needUnbindRMB)
		#1.写已构买标志 2.本服购买记录 3.更新全局购买总数
		if itemIndex == ITEMINDEX_ONE:
			role.SetDI1(EnumDayInt1.GroupBuyPartyBuyItemOne, 1)
			buyRecordList_ItemOne = GroupBuyParty_BuyRecord_Dict.get(ITEMINDEX_ONE, [])
			if roleId not in buyRecordList_ItemOne:
				buyRecordList_ItemOne.append(roleId)
				GroupBuyParty_BuyRecord_Dict[ITEMINDEX_ONE] = buyRecordList_ItemOne
				GroupBuyParty_BuyRecord_Dict.changeFlag = True
			
			GlobalHttp.IncGlobalData(GlobalDataDefine.GroupBuyPartyDataKey_1, 5)
		else:
			role.SetDI1(EnumDayInt1.GroupBuyPartyBuyItemTwo, 1)
			buyRecordList_ItemTwo = GroupBuyParty_BuyRecord_Dict.get(ITEMINDEX_TWO, [])
			if roleId not in buyRecordList_ItemTwo:
				buyRecordList_ItemTwo.append(roleId)
				GroupBuyParty_BuyRecord_Dict[ITEMINDEX_TWO] = buyRecordList_ItemTwo
				GroupBuyParty_BuyRecord_Dict.changeFlag = True
				
			GlobalHttp.IncGlobalData(GlobalDataDefine.GroupBuyPartyDataKey_2, 5)
		#获得物品
		role.AddItem(coding, cnt)
	
	bubblePrompt =GlobalPrompt.GroupBuyParty_Tips_Head + GlobalPrompt.GroupBuyParty_Tips_Item % (coding, cnt)
	role.Msg(2, 0, bubblePrompt)

#### TICK start ####
def CallBeforeNewHour():
	'''
	活动脉搏 整点触发
	'''
	if not IS_START:
		return
	
	#非零点整点数据更新
	if cDateTime.Hour() != 0:
		GetGBPGlobalData()
		
	if cDateTime.Hour() == 23:
		#23:55分取回数据 
		cComplexServer.RegTick(FIFTY_FIVE_MIN_SECONDS, TickGetGBCGlobalData)
	elif cDateTime.Hour() == 0:
		#跨天处理 （活动为继续开启状态） 
		#1.发奖
		AwardUnlockReward()	
		#2.1.重算dayIndex并同步
		UpdateAndSyncDayIndex()
		#2.2.清除 本服缓存的全局购买总数
		global GBP_GLOBALBUYCOUNT_DICT
		GBP_GLOBALBUYCOUNT_DICT.clear()

def TickGetGBCGlobalData(callargv, regparam):
	'''
	tick触发取回数据
	'''
	GetGBPGlobalData()

#### 处理 start ####
def GetGBPGlobalData():
	'''
	请求获取最新全局购买总数
	'''
	#获取第一个物品全局购买总数
	GlobalHttp.GetGlobalData(GlobalDataDefine.GroupBuyPartyDataKey_1, OnGlobalDataBack, ITEMINDEX_ONE)
	#获取第二个物品全局购买总数
	GlobalHttp.GetGlobalData(GlobalDataDefine.GroupBuyPartyDataKey_2, OnGlobalDataBack, ITEMINDEX_TWO)

def OnGlobalDataBack(backvalue, regparam):
	'''
	全局购买数据载回
	'''
	itemIndex = regparam
	global GBP_GLOBALBUYCOUNT_DICT
	if backvalue is None:
		print "GE_EXC, OnGlobalDataBack backvalue is None"
		return
	
	GBP_GLOBALBUYCOUNT_DICT[itemIndex] = backvalue

def AwardUnlockReward():
	'''
	根据当前数据 解锁奖励 并发奖
	'''
	#第一个商品解锁奖励
	rewardList = []
	rewardCfg = GroupBuyPartyConfig.GetRewardCfgByDayAndIndex(GBP_DAYINDEX, ITEMINDEX_ONE)
	if not rewardCfg:
		print "GE_EXC,can not get config with dayIndex(%s),itemIndex(%s)" % (GBP_DAYINDEX,ITEMINDEX_ONE)
		return
	
	buyCnt_itemOne = GBP_GLOBALBUYCOUNT_DICT.get(ITEMINDEX_ONE)
	for needCnt, coding, cnt in rewardCfg.rewards:
		if buyCnt_itemOne >= needCnt:
			rewardList.append((coding, cnt))
	
	#有解锁任何奖励
	global GroupBuyParty_BuyRecord_Dict
	buyRecordDict_ItemOne = GroupBuyParty_BuyRecord_Dict.get(ITEMINDEX_ONE, [])
	if len(rewardList) > 0:
		for tmpRoleId in buyRecordDict_ItemOne:
			AwardMgr.SetAward(tmpRoleId, EnumAward.GroupBuyPartyAward_1, itemList = rewardList, clientDescParam = (ITEMINDEX_ONE, len(rewardList)))
	
	#第二个商品解锁奖励
	rewardList = []
	rewardCfg = GroupBuyPartyConfig.GetRewardCfgByDayAndIndex(GBP_DAYINDEX, ITEMINDEX_TWO)
	if not rewardCfg:
		print "GE_EXC,can not get config with dayIndex(%s), itemIndex(%s)" % (GBP_DAYINDEX, ITEMINDEX_TWO)
		return
	
	buyCnt_itemTwo = GBP_GLOBALBUYCOUNT_DICT.get(ITEMINDEX_TWO)
	for needCnt, coding, cnt in rewardCfg.rewards:
		if buyCnt_itemTwo >= needCnt:
			rewardList.append((coding, cnt))
	
	#有解锁任何奖励
	buyRecordDict_ItemTwo = GroupBuyParty_BuyRecord_Dict.get(ITEMINDEX_TWO, [])
	if len(rewardList) > 0:
		for tmpRoleId in buyRecordDict_ItemTwo:
			AwardMgr.SetAward(tmpRoleId, EnumAward.GroupBuyPartyAward_2, itemList = rewardList, clientDescParam = (ITEMINDEX_TWO, len(rewardList)))
	
	#发奖之后
	#清除本服购买玩家的roleId	
	GroupBuyParty_BuyRecord_Dict.data = {}
	GroupBuyParty_BuyRecord_Dict.changeFlag = True
	
def UpdateAndSyncDayIndex():
	'''
	重算dayIndex并同步
	'''
	CalculateDayIndex()
	#活动开启状态下广播同步dayIndex
	if IS_START:
		cNetMessage.PackPyMsg(GroupBuyParty_DayIndex_Sync, GBP_DAYINDEX)
		cRoleMgr.BroadMsg()

def CalculateDayIndex():
	'''
	计算当前活动开启天数
	'''
	#活动开始的天数
	baseCfg = GroupBuyPartyConfig.GBP_BASECONFIG
	if not baseCfg:
		print "GE_EXC,GroupBuyPartyConfig.GBP_BASECONFIG is None"
		return
	
	#当前日期时间
	nowDate = cDateTime.Now()
	#活动持续开启的天数
	durableDay = (nowDate - baseCfg.startTime).days 	
	#更新全局DAY_INDEX
	global GBP_DAYINDEX
	GBP_DAYINDEX = durableDay + 1	
	#超过 强制设置最后一天
	if GBP_DAYINDEX > baseCfg.totalDay:
		GBP_DAYINDEX = baseCfg.totalDay
	
#### 事件 start ####
def OnSyncRoleOtherData(role, param):
	'''
	同步团购派对数据
	'''
	if not IS_START:
		return
	
	role.SendObj(GroupBuyParty_ActiveStatus_Sync, (GPB_STATUS_OPEN, ENDTIME))
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#事件
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		#TICK
		cComplexServer.RegBeforeNewHourCallFunction(CallBeforeNewHour)
		#持久化数据
		GroupBuyParty_BuyRecord_Dict = Contain.Dict("GroupBuyParty_BuyRecord_Dict")	#本服购买记录{itemIndex:[roleId,],}
		#请求
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GroupBuyParty_OnOpenPanel", "团购派对打开面板"), OnOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GroupBuyParty_OnBuyGood", "团购派对请求购买商品"), OnBuyGood)
