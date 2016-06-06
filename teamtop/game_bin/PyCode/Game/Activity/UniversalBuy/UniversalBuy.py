#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.UniversalBuy.UniversalBuy")
#===============================================================================
# 全民团购
#===============================================================================
import cComplexServer
import Environment
import cDateTime
import cRoleMgr
from ComplexServer.API import GlobalHttp
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from Game.Persistence import BigTable
from Game.Role import Event
from Game.Role.Data import EnumObj
from Game.Activity.Award import AwardMgr
from Game.Activity.UniversalBuy import UniversalBuyConfig


if "_HasLoad" not in dir():
	IS_LOAD = False	#是否获取过全服数据
	
	UNIVER_INDEX_1 = 1
	UNIVER_INDEX_2 = 2
	UNIVER_INDEX_3 = 3
	UNIVER_INDEX_4 = 4
	UNIVER_INDEX_5 = 5
	UNIVER_INDEX_6 = 6
	UNIVER_INDEX_7 = 7
	UNIVER_INDEX_8 = 8
	UNIVER_INDEX_9 = 9

	MIN_LEVEL = 30	#开启活动的最低等级
	GLOBAL_BUY_DATA = {}	#商品ID-->数量
	BUYNUM_DEFINE = [25000,15000,7000,3000,1000]
	
	TICK_TIME = 55 * 60
	#消息
	UniverBuy_Server_Data = AutoMessage.AllotMessage("UniverBuy_Server_Data", "全民团购发跨服数据")
	UniverBuy_Role_Data = AutoMessage.AllotMessage("UniverBuy_Role_Data", "全民团购玩家数据")
	#日志
	UniverBuyCost = AutoLog.AutoTransaction("UniverBuyCost", "全民团购消费")
	UniverBuyUnlockReward = AutoLog.AutoTransaction("UniverBuyUnlockReward", "全民团购解锁奖励")
	UniverBuyGlobalData = AutoLog.AutoTransaction("UniverBuyGlobalData", "全民团购清理时的跨服购买数量")

def CheckActive():
	#检测活动是否开启
	cfg = UniversalBuyConfig.UNIVER_BUY_BASE
	now = cDateTime.Now()
	start = cfg.StartTime#指定开启时间
	end = cfg.EndTime#指定结束时间
	if start <= now <= end:
		return 1
	return 0

def GetBackData(value, regparam):
	#获取跨服数据回调
	if value is None:
		print "GE_EXC, UniversalBuy can not  GetBackData"
		return

	global GLOBAL_BUY_DATA
	global RANDON_LIST
	global BUYNUM_DEFINE

	key = regparam
	GLOBAL_BUY_DATA[key] = value

	MIN_CNT = value
	for i in xrange(len(BUYNUM_DEFINE)):
		if BUYNUM_DEFINE[i] <= MIN_CNT:
			MIN_CNT = BUYNUM_DEFINE[i]
			break
	if MIN_CNT in BUYNUM_DEFINE:
		cRoleMgr.Msg(11, 0, GlobalPrompt.UniverBuy_Msg %(key, MIN_CNT))


def CallPerHour():
	#每小时调用
	#检查活动是否开启，没开启直接return
	state = CheckActive()
	if not state:
		return
	
	if cDateTime.Hour() != 0:
		#GetGlobalData()
		GetGlobalDataByKeys()
		
	#假如为0点
	if cDateTime.Hour() == 23:
		#注册个55分钟的Tick
		cComplexServer.RegTick(TICK_TIME, TickGetData)
		
	elif cDateTime.Hour() == 0:
		GetResult()

def TickGetData(callargv, regparam):
	#这里再次获取数据是为了防止在0点获取时已经被清理了数据
	#GetGlobalData()
	GetGlobalDataByKeys()

def GetGlobalData():
	#获取跨服数据
	global IS_LOAD
	
	for index in UniversalBuyConfig.UNIVER_KEY_LIST:
		GlobalHttp.GetGlobalData(index, GetBackData, index)
	
	if not IS_LOAD:
		IS_LOAD = True


def GetGlobalDataByKeys():
	global IS_LOAD
	IS_LOAD = True
	GlobalHttp.GetGlobalDataByKeys(UniversalBuyConfig.UNIVER_KEY_LIST, GetBackDataEx)


def GetBackDataEx(backvalue, regparam):
	if backvalue is None:
		print "GE_EXC, UniversalBuy GetBackDataEx is None"
		return
	
	for key, value in backvalue.iteritems():
		GetBackData(int(value), int(key))

def GetResult():
	#根据每次商品对应的购买数，获取解锁的奖励
	for index in UniversalBuyConfig.UNIVER_KEY_LIST:
		PayReward(index)
	#发完奖励后，做数据清理操作
	ClearData()

def ClearData():
	#清除本服缓存的购买次数以存DB的玩家ID
	global GLOBAL_BUY_DATA
	#清DB
	for index in UniversalBuyConfig.UNIVER_KEY_LIST:
		SetUBData(index, set())
	#先记录一份全民团购本地最新的数据
	with UniverBuyGlobalData:
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveUniversalBuyData, GLOBAL_BUY_DATA)
	
	for key in GLOBAL_BUY_DATA.keys():
		GLOBAL_BUY_DATA[key] = 0
		
def PayReward(index):
	#根据商品ID发奖
	global GLOBAL_BUY_DATA
	
	cfg = UniversalBuyConfig.UNIVER_REWARD_DICT.get(index)
	if not cfg:
		print "GE_EXC,can not find index(%s) in PayReward" % index
		return
	roleId_list = GetUBData(index)
	if not roleId_list:
		return
	buyCnt = GLOBAL_BUY_DATA.get(index, 0)
	unlock_reward = []
	with UniverBuyUnlockReward:
		if buyCnt >= cfg.needCnt1:
			unlock_reward.append(cfg.libao1)
		if buyCnt >= cfg.needCnt2:
			unlock_reward.append(cfg.libao2)
		if buyCnt >= cfg.needCnt3:
			unlock_reward.append(cfg.libao3)
		if buyCnt >= cfg.needCnt4:
			unlock_reward.append(cfg.libao4)
		if buyCnt >= cfg.needCnt5:
			unlock_reward.append(cfg.libao5)
		if buyCnt >= cfg.needCnt6:
			unlock_reward.append(cfg.libao6)
		if buyCnt >= cfg.needCnt7:
			unlock_reward.append(cfg.libao7)
		if not unlock_reward:
			return
		for roleId in roleId_list:
			AwardMgr.SetAward(roleId, cfg.awardEnum, itemList = unlock_reward, clientDescParam = (index, len(unlock_reward)))

def RoleDayClear(role, param):
	'''
	玩家每日清理
	@param role:
	@param param:
	'''
	role.SetObj(EnumObj.UniverBuyDict, {})
	
def SyncRoleOtherData(role, param):
	'''
	同步数据
	@param role:
	@param param:
	'''
	if not CheckActive():
		return
	role.SendObj(UniverBuy_Role_Data, role.GetObj(EnumObj.UniverBuyDict))
#==============================================================
def RequestOpenPanel(role, param):
	'''
	客户端请求打开界面
	@param role:
	@param param:
	'''
	global IS_LOAD
	global GLOBAL_BUY_DATA
	
	if not CheckActive():
		return
	if not IS_LOAD:
		#GetGlobalData()
		GetGlobalDataByKeys()
		
	role.SendObj(UniverBuy_Server_Data, GLOBAL_BUY_DATA)
	role.SendObj(UniverBuy_Role_Data, role.GetObj(EnumObj.UniverBuyDict))

def RequestBuy(role, param):
	'''
	客户端请求购买商品
	@param role:
	@param param:
	'''
	index, cnt = param	#商品对应的格子
	if not CheckActive():
		return
	if cnt <= 0:
		return
	if index not in UniversalBuyConfig.UNIVER_KEY_LIST:
		return
	if role.GetLevel() < MIN_LEVEL:
		return
	roleObj = role.GetObj(EnumObj.UniverBuyDict)
	buyTimes = roleObj.get(index, 0)
	
	cfg = UniversalBuyConfig.UNIVER_REWARD_DICT.get(index)
	if not cfg:
		print "GE_EXC,can not find index(%s) in RequestBuy" % index
		return
	if buyTimes + cnt > cfg.BuyCnt:
		return
	if role.GetUnbindRMB() < cfg.discountRMB * cnt:
		return
	with UniverBuyCost:
		role.DecUnbindRMB(cfg.discountRMB * cnt)
		role.AddItem(cfg.ItemId, cnt)
		#记录该商品购买的次数
		roleObj[index] = roleObj.get(index, 0) + cnt
		#跨服数据
		GlobalHttp.IncGlobalData(index, cnt * cfg.times)
		#将该玩家的id存入对应商品中
		DB_value = GetUBData(index)
		if DB_value is None:
			SetUBData(index, set([role.GetRoleID()]))
		else:
			DB_value.add(role.GetRoleID())
			SysUniverBuyBT.HasChangeKey(index)
		role.SendObj(UniverBuy_Role_Data, role.GetObj(EnumObj.UniverBuyDict))
#============================================================
def GetUBData(index):
	d = SysUniverBuyBT.GetValue(index)
	if d is None:
		print "GE_EXC,can not find index(%s) in GetUBData" % index
		return None
	return d["univerbuy_data"]

def SetUBData(index, data):
	SysUniverBuyBT.SetKeyValue(index, {"univerbuy_index" : index, "univerbuy_data" : data})
	
def AfterLoadBT():
	if UNIVER_INDEX_1 not in SysUniverBuyBT.datas:
		SetUBData(UNIVER_INDEX_1, set())
	if UNIVER_INDEX_2 not in SysUniverBuyBT.datas:
		SetUBData(UNIVER_INDEX_2, set())
	if UNIVER_INDEX_3 not in SysUniverBuyBT.datas:
		SetUBData(UNIVER_INDEX_3, set())
	if UNIVER_INDEX_4 not in SysUniverBuyBT.datas:
		SetUBData(UNIVER_INDEX_4, set())
	if UNIVER_INDEX_5 not in SysUniverBuyBT.datas:
		SetUBData(UNIVER_INDEX_5, set())
	if UNIVER_INDEX_6 not in SysUniverBuyBT.datas:
		SetUBData(UNIVER_INDEX_6, set())
	if UNIVER_INDEX_7 not in SysUniverBuyBT.datas:
		SetUBData(UNIVER_INDEX_7, set())
	if UNIVER_INDEX_8 not in SysUniverBuyBT.datas:
		SetUBData(UNIVER_INDEX_8, set())
	if UNIVER_INDEX_9 not in SysUniverBuyBT.datas:
		SetUBData(UNIVER_INDEX_9, set())

if "_HasLoad" not in dir():
	if Environment.HasLogic or Environment.HasWeb:
		SysUniverBuyBT = BigTable.BigTable("univerbuy_info", 50, AfterLoadBT)
		
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
	if Environment.HasLogic and not Environment.IsCross:
		cComplexServer.RegBeforeNewHourCallFunction(CallPerHour)
	
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("UniverBuy_Open_Panel", "客户端请求打开全民团购界面"), RequestOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("UniverBuy_Buy_Index", "客户端请求购买全民团购商品"), RequestBuy)

