#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.GroupBuyCarnival.GroupBuyCarnivalMgr")
#===============================================================================
# 团购嘉年华Mgr（一天一轮团购只卖一种物品）
#===============================================================================
import datetime
import Environment
import cRoleMgr
import cDateTime
import cNetMessage
import cComplexServer
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalDataDefine, GlobalPrompt, EnumAward
from ComplexServer.API import GlobalHttp
from Game.Persistence import Contain
from Game.Role.Data import EnumDayInt1
from Game.Activity.Award import AwardMgr
from Game.Activity.GroupBuyCarnival import GroupBuyCarnivalConfig
from Game.Role import Event

FIFTY_FIVE_MIN_SECONDS = 55 * 60		#55分钟秒数 
ONE_DAY_SECONDS = 24 * 60 * 60		#一天的总秒数
FIVE_MINUTE_SECONDS = 5 * 60		#五分钟秒数

if "_HasLoad" not in dir():
	IS_START = False	#团购嘉年华活动开关标志	
	GBC_DAY_INDEX = 0	#团购嘉年华当前波次
	GBC_GLOBAL_BUY_CNT = 0	#团购嘉年华上一个整点全局购买总数
	
	GBC_ActiveState_Sync = AutoMessage.AllotMessage("GBC_ActiveState_S", "同步团购嘉年华活动开关状态")
	GBC_WaveCount_Sync = AutoMessage.AllotMessage("GBC_WaveCount_S", "同步团购嘉年华活动最新波次")
	GBC_GlobalBuyCnt_Sync = AutoMessage.AllotMessage("GBC_GlobalBuyCnt_S", "同步上一个整点全局购买总数")
	
	Tra_GBC_BuyItem = AutoLog.AutoTransaction("Tra_GBC_BuyItem", "团购嘉年华购买物品")
	Tra_GBC_UnlockReward = AutoLog.AutoTransaction("Tra_GBC_UnlockReward","团购嘉年华解锁奖励")

######### 请求 ############
def OnOpenPanel(role, msg = None):
	'''
	打开面板 同步相关数据
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.GroupBuyCarnival_NeedLevel:
		return
	
	#同步当前波次
	role.SendObj(GBC_WaveCount_Sync, GBC_DAY_INDEX)
	#同步整点购买总数
	role.SendObj(GBC_GlobalBuyCnt_Sync, GBC_GLOBAL_BUY_CNT)

def OnBuyItem(role, msg = None):
	'''
	购买物品 
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.GroupBuyCarnival_NeedLevel:
		return
	
	#今日已购买
	if role.GetDI1(EnumDayInt1.GroupBuyCarnivalBuy):
		return
	
	#23:55分之后不再购买
	todaySeconds = cDateTime.Hour() * 3600 + cDateTime.Minute() * 60 + cDateTime.Second()
	if ONE_DAY_SECONDS - todaySeconds < FIVE_MINUTE_SECONDS:
		role.Msg(2, 0, GlobalPrompt.GBC_Tips_LastFiveMinute_Limit)
		return
	
	#获取购买配置
	roleLevel = role.GetLevel()
	GBCConfig = GroupBuyCarnivalConfig.GetGBCConfig(GBC_DAY_INDEX, roleLevel)
	if not GBCConfig:
		print "GE_EXC, cannot fing config with (GBC_DAY_INDEX(%s), roleLevel(%s))" % (GBC_DAY_INDEX, roleLevel)
		return
	
	if role.GetUnbindRMB() < GBCConfig.needRMB:
		return
	
	coding, cnt = GBCConfig.item
	with Tra_GBC_BuyItem:
		#扣钱
		role.DecUnbindRMB(GBCConfig.needRMB)
		#更新今日购买标志
		role.SetDI1(EnumDayInt1.GroupBuyCarnivalBuy, 1)
		#全局购买数更新
		GlobalHttp.IncGlobalData(GlobalDataDefine.GroupBuyCarnivalDataKey, cnt)
		#物品获得
		role.AddItem(coding, cnt)
	
	#记录购买玩家的roleId
	global GBC_RoleId_List
	if role.GetRoleID() not in GBC_RoleId_List:
		GBC_RoleId_List.append(role.GetRoleID())
	
	#获得提示
	rewardPrompt = GlobalPrompt.GBC_Tips_Reward_Head + GlobalPrompt.GBC_Tips_Reward_Item % (coding, cnt)
	role.Msg(2, 0, rewardPrompt)

######### TICK  ###########
def CallPerHour():
	'''
	整点触发处理 
	'''
	global IS_START
	oldState = IS_START
	IS_START = CheckActiveState()
	
	#活动开启
	if oldState != IS_START:
		cNetMessage.PackPyMsg(GBC_ActiveState_Sync, IS_START)
		cRoleMgr.BroadMsg()
		
		#此时活动结束 发奖 保存本服缓存购买总数和dayIndex供客户端显示最后一天的状态
		if not IS_START:
			#发奖
			AwardUnlockReward()	
			
	#未到开启时间
	if not IS_START:
		return
	
	#从关闭 到 开启 初始化一次dayIndex
	if oldState != IS_START:
		UpdateGBCDayIndex()
	
	#非零点整点数据更新
	if cDateTime.Hour() != 0:
		GetGBCGlobalData()
		
	if cDateTime.Hour() == 23:
		#23:55分取回数据 
		cComplexServer.RegTick(FIFTY_FIVE_MIN_SECONDS, TickGetGBCGlobalData)
	elif cDateTime.Hour() == 0:
		#跨天处理 （活动为继续开启状态） 
		#1.发奖
		AwardUnlockReward()	
		#2.1.重算dayIndex
		UpdateGBCDayIndex()
		#2.2.清除 本服缓存的全局购买总数
		global GBC_GLOBAL_BUY_CNT
		GBC_GLOBAL_BUY_CNT = 0
		
######## helper ########
def CheckActiveState():
	'''
	根据配置和当前时间判断 活动是否开启状态
	@return: True if need open, False otherwise. 
	'''
	now = cDateTime.Now()
	baseCfg = GroupBuyCarnivalConfig.GBC_BASE_CONFIG
	
	if not baseCfg:
		print "GE_EXC,GroupBuyCarnivalConfig error GBC_BASE_CONFIG is None"
		return False
	
	if baseCfg.startTime <= now < baseCfg.endTime:
		return True
	
	return False

def TickGetGBCGlobalData(callargv, regparam):
	'''
	定时器触发 跨天提前5min缓存今日购买总数
	'''
	GetGBCGlobalData()

def GetGBCGlobalData():
	'''
	获取团购嘉年华全局购买数据
	'''
	#获取全局购买总数 注册参数GBC_DAY_INDEX 防止数据回来时候 已经是下一个dayIndex了 
	GlobalHttp.GetGlobalData(GlobalDataDefine.GroupBuyCarnivalDataKey, GetGBCGlobalDataBack)

def GetGBCGlobalDataBack(backvalue, regparam):
	'''
	团购嘉年华全局购买总次数数据回来了
	'''
	if backvalue is None:
		print "GE_EXC, GroupBuyCarnival GetGBCGlobalDataBack::backvalue is None"
		return
	
#	#数据回来之前跨天了 不能赋值
#	oldDayIndex = regparam
#	if GBC_DAY_INDEX != oldDayIndex:
#		print "GE_EXC,GetGBCGlobalDataBack:: GBC_DAY_INDEX(%s) != oldDayIndex(%s)" % (GBC_DAY_INDEX, oldDayIndex)
#		return
	
	global GBC_GLOBAL_BUY_CNT
	GBC_GLOBAL_BUY_CNT = backvalue
	
	#此处最新整点数据已到位  广播提示在这里加
	
def AwardUnlockReward():
	'''
	根据23:55分返回的数据 处理解锁的奖励发放
	'''
	rewardList = []
	GBCConfig = GroupBuyCarnivalConfig.GetGBCConfig(GBC_DAY_INDEX)
	if not GBCConfig:
		print "GE_EXC,can not get config with dayIndex(%s),roleLevel(1)" % GBC_DAY_INDEX
		return
	
	for needCnt, coding, cnt in GBCConfig.rewards:
		if GBC_GLOBAL_BUY_CNT >= needCnt:
			rewardList.append((coding, cnt))
	
	#有解锁任何奖励
	global GBC_RoleId_List
	if len(rewardList) > 0:
		for roleId in GBC_RoleId_List:
			AwardMgr.SetAward(roleId, EnumAward.GroupBuyCarnivalAward, itemList = rewardList, clientDescParam = (GBC_DAY_INDEX, len(rewardList)))
	
	#发奖之后
	#清除本服购买玩家的roleId	
	GBC_RoleId_List.data = []
	GBC_RoleId_List.changeFlag = True

def UpdateGBCDayIndex():
	'''
	跨天重置并广播相关数据
	'''
	#重算 更新
	CalculateDayIndex()
	#活动开启状态下广播同步dayIndex
	if IS_START:
		cNetMessage.PackPyMsg(GBC_WaveCount_Sync, GBC_DAY_INDEX)
		cRoleMgr.BroadMsg()

def CalculateDayIndex():
	'''
	根据当前时间和活动配置开启时间 计算天数波叔
	'''
	#活动开始的天数
	baseCfg = GroupBuyCarnivalConfig.GBC_BASE_CONFIG
	if not baseCfg:
		print "GE_EXC,GroupBuyCarnivalConfig.GBC_BASE_CONFIG is None"
		return
	
	#当前日期时间
	nowDate = datetime.datetime(cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second())
	#活动持续开启的天数
	durableDay = (nowDate - baseCfg.startTime).days 	
	#更新全局DAY_INDEX
	global GBC_DAY_INDEX
	GBC_DAY_INDEX = durableDay + 1	
	#超过 强制设置最后一天
	if GBC_DAY_INDEX > baseCfg.totalDay:
		GBC_DAY_INDEX = baseCfg.totalDay

#def Initialize():
#	'''
#	服务器启动 初始化相关数据 IS_START，GBC_DAY_INDEX
#	'''
#	#启服时候跑下这两个 确保相关数据合理初始
#	CallPerHour()
#	UpdateGBCDayIndex()

def OnSyncRoleOtherData(role, param = None):
	'''
	登陆同步活动开启状态
	'''
	if IS_START:
		role.SendObj(GBC_ActiveState_Sync, IS_START)

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		
		GBC_RoleId_List = Contain.List("GroupBuyCarnival_RoleId_List")	#本服已购买玩家roleId记录(一天一轮团购只卖一种物品)[roleId,]
		
#		Initialize()		
		cComplexServer.RegBeforeNewHourCallFunction(CallPerHour)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GBC_OnBuyItem", "团购嘉年华购买物品"), OnBuyItem)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GBC_OnOpenPanel", "团购嘉年华打开面板"), OnOpenPanel)