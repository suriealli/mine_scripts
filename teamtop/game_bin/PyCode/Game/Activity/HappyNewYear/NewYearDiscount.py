#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.HappyNewYear.NewYearDiscount")
#===============================================================================
# 新年乐翻天 -- 新年折扣汇
#===============================================================================
import time
import datetime
import Environment
import cRoleMgr
import cDateTime
from Common.Other import EnumGameConfig, GlobalPrompt
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumObj, EnumInt32
from Game.Role import Event
from Game.Activity.HappyNewYear import NewYearConfig
from Game.Activity import CircularDefine

if "_HasLoad" not in dir():
	IsOpen = False
	
	#{1:tickId, 2:{goodId:cnt}, 3:endtime, 4:freshCnt}
	NYearDiscountData = AutoMessage.AllotMessage("NYearDiscountData", "新年乐翻天数据")
	
	NYearDiscountBuy_Log = AutoLog.AutoTransaction("NYearDiscountBuy_Log", "新年折扣汇购买日志")
	NYearDiscountRefresh_Log = AutoLog.AutoTransaction("NYearDiscountRefresh_Log", "新年折扣汇刷新日志")
#===============================================================================
# 事件
#===============================================================================
def OpenAct(param1, param2):
	#开启活动
	if param2 != CircularDefine.CA_NewYearDiscount:
		return
	
	global IsOpen
	if IsOpen:
		print 'GE_EXC, HappyNewYear is already open'
	IsOpen = True

def CloseAct(param1, param2):
	#关闭活动
	if param2 != CircularDefine.CA_NewYearDiscount:
		return
	
	global IsOpen
	if not IsOpen:
		print 'GE_EXC, HappyNewYear is already close'
	IsOpen = False

def BeforeExit(role, param):
	discountObj = role.GetObj(EnumObj.NYearData).get(2)
	if not discountObj:
		#之前没有打开过面板,不管
		return
	
	if discountObj[1]:
		#如果有tick的话先取消tick
		role.UnregTick(discountObj[1])
		discountObj[1] = 0
		role.GetObj(EnumObj.NYearData)[2] = discountObj
	
def AfterLogin(role, param):
	global IsOpen
	if not IsOpen: return
	
	discountObj = role.GetObj(EnumObj.NYearData).get(2)
	if not discountObj:
		#之前没有打开过面板,不管
		return
	
	if not discountObj[1]:
		#如果之前的tick被取消了
		if cDateTime.Hour() < 12:
			#时间在12点之前, 重新注册刷新tick
			refresh = int(time.mktime((datetime.datetime(cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), 12, 0, 0)).timetuple()))
			tickId = role.RegTick(refresh - cDateTime.Seconds(), Refresh)
			role.GetObj(EnumObj.NYearData)[2][1] = tickId
#===============================================================================
# 辅助
#===============================================================================
def Refresh(role, argv, param):
	#获取随机到的物品配置
	itemList = GetItemList(role)
	if not itemList:
		print 'GE_EXC, NYD Refresh return error'
		return
	
	#打包字典
	tmpDict = {}
	for (goodId, itemCnt) in itemList:
		tmpDict[goodId] = itemCnt
	
	#这里需要把刷新的tick取消掉
	role.GetObj(EnumObj.NYearData)[2][1] = 0
	
	role.GetObj(EnumObj.NYearData)[2][2] = tmpDict
	role.SendObj(NYearDiscountData, role.GetObj(EnumObj.NYearData)[2])
	
def GetItemList(role):
	if role.IsKick():
		return
	
	roleLevel = role.GetLevel()
	
	for (minLevel, maxLevel) in NewYearConfig.NewYearDiscountLv_List:
		if minLevel > roleLevel:
			continue
		if maxLevel < roleLevel:
			continue
		levelRange =  (minLevel, maxLevel)
		if levelRange not in NewYearConfig.NYDiscountRandom_Dict:
			print 'GE_EXC, GetItemList can not find level range %s, %s in NYDiscountRandom_Dict' % levelRange
			return
		return NewYearConfig.NYDiscountRandom_Dict[levelRange].RandomMany(6)
#===============================================================================
# 请求
#===============================================================================
def RequestOpen(role, msg):
	'''
	请求打开面板
	@param role:
	@param msg:
	'''
	global IsOpen
	if not IsOpen: return
	
	if role.GetLevel() < EnumGameConfig.NYEAR_MIN_LEVEL:
		return
	
	discountObj = role.GetObj(EnumObj.NYearData).get(2)
	
	#有刷新tick了
	if discountObj:
		role.SendObj(NYearDiscountData, discountObj)
		return
	
	nowHour, nowSec = cDateTime.Hour(), cDateTime.Seconds()
	
	tickId = 0
	if nowHour < 12:
		#如果在12点之前打开面板的话注册12点刷新的tick
		refresh = int(time.mktime((datetime.datetime(cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), 12, 0, 0)).timetuple()))
		tickId = role.RegTick(refresh - nowSec, Refresh)
		
	#获取随机到的物品配置
	itemList = GetItemList(role)
	if not itemList:
		print 'GE_EXC, NYD RequestOpen return error'
		return
	
	#打包字典
	tmpDict = {}
	for (goodId, itemCnt) in itemList:
		tmpDict[goodId] = itemCnt
	
	role.GetObj(EnumObj.NYearData)[2] = packObj =  {1:tickId, 2:tmpDict, 3:0, 4:1, 5:cDateTime.Days()}
	role.SendObj(NYearDiscountData, packObj)
	
def RequestBuy(role, msg):
	'''
	请求购买
	@param role:
	@param msg:
	'''
	global IsOpen
	if not IsOpen: return
	
	if role.GetLevel() < EnumGameConfig.NYEAR_MIN_LEVEL:
		return
	
	goodId = msg
	
	dicountObj = role.GetObj(EnumObj.NYearData).get(2)
	#没有打开过面板 or 这批刷新的没有这个物品 or 这个物品已经被买完了
	if (not dicountObj) or (goodId not in dicountObj[2]) or (not dicountObj[2][goodId]):
		return
	
	#配置
	cfg = NewYearConfig.NYDiscount_Dict.get(goodId)
	if not cfg:
		print 'GE_EXC, RequestBuy can not din goodId %s in NYDiscount_Dict' % goodId
		return
	
	with NYearDiscountBuy_Log:
		if cfg.RMBType:
			#只限充值神石购买
			if role.GetUnbindRMB_Q() < cfg.needUnbindRMB:
				return
		else:
			if role.GetUnbindRMB() < cfg.needUnbindRMB:
				return
		if cfg.needScore:
			if role.GetI32(EnumInt32.NewYearScore) < cfg.needScore:
				return
		
		if cfg.RMBType:
			role.DecUnbindRMB_Q(cfg.needUnbindRMB)
		else:
			role.DecUnbindRMB(cfg.needUnbindRMB)
		if cfg.needScore:
			role.DecI32(EnumInt32.NewYearScore, cfg.needScore)
		
		#限购数量减1
		dicountObj[2][goodId] -= 1
		role.GetObj(EnumObj.NYearData)[2] = dicountObj
		
		#发物品
		role.AddItem(*cfg.item)
		
		role.SendObj(NYearDiscountData, dicountObj)
	
	role.Msg(2, 0, GlobalPrompt.Item_Tips % cfg.item)
	
def RequestFresh(role, msg):
	'''
	请求刷新
	@param role:
	@param msg:
	'''
	global IsOpen
	if not IsOpen: return
	
	if role.GetLevel() < EnumGameConfig.NYEAR_MIN_LEVEL:
		return
	
	discountObj = role.GetObj(EnumObj.NYearData).get(2)
	if not discountObj:
		return
	
	#配置
	freshCnt = discountObj[4]
	if freshCnt >= EnumGameConfig.NYEAR_MAX_REFRESH:
		freshCnt = EnumGameConfig.NYEAR_MAX_REFRESH
	cfg = NewYearConfig.NYDiscountFresh_Dict.get(freshCnt)
	if not cfg:
		print 'GE_EXC, RequestFresh can not find refresh cnt %s' % freshCnt
		return
	
	if role.GetI32(EnumInt32.NewYearScore) < cfg.needScore:
		return
	
	with NYearDiscountRefresh_Log:
		#扣积分
		role.DecI32(EnumInt32.NewYearScore, cfg.needScore)
		
		#获取随机到的物品配置
		itemList = GetItemList(role)
		if not itemList:
			print 'GE_EXC, NYD RequestFresh return error'
			return
		
		#打包字典
		tmpDict = {}
		for (goodId, itemCnt) in itemList:
			tmpDict[goodId] = itemCnt
		
		role.GetObj(EnumObj.NYearData)[2][2] = tmpDict
		role.GetObj(EnumObj.NYearData)[2][4] += 1
		
		role.SendObj(NYearDiscountData, role.GetObj(EnumObj.NYearData)[2])
		
		role.Msg(2, 0, GlobalPrompt.NYEAR_DISCOUNT_REFRESH % cfg.needScore)

def RoleDayClear(role, param):
	#清理积分
	role.SetI32(EnumInt32.NewYearScore, 0)
	
	discountObj = role.GetObj(EnumObj.NYearData).get(2)
	if not discountObj:
		#如果之前没有打开过面板, 不处理
		return
	
	if discountObj.get(1):
		#如果之前有tick, 先取消掉tick
		role.UnregTick(discountObj[1])
	
	global IsOpen
	if not IsOpen:
		#活动结束的话清理
		role.GetObj(EnumObj.NYearData)[2] = {}
		return
	
	nowHour, nowSec = cDateTime.Hour(), cDateTime.Seconds()
	tickId = 0
	if nowHour < 12:
		#如果在12点之前的话注册12点刷新tick
		refresh = int(time.mktime((datetime.datetime(cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), 12, 0, 0)).timetuple()))
		tickId = role.RegTick(refresh - nowSec, Refresh)
		
	#获取随机到的物品配置
	itemList = GetItemList(role)
	if not itemList:
		print 'GE_EXC, NYD RoleDayClear return error'
		return
	
	#打包字典
	tmpDict = {}
	for (goodId, itemCnt) in itemList:
		tmpDict[goodId] = itemCnt
	
	#重置数据
	role.GetObj(EnumObj.NYearData)[2] = packObj =  {1:tickId, 2:tmpDict, 3:0, 4:1, 5:cDateTime.Days()}
	role.SendObj(NYearDiscountData, packObj)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_BeforeExit, BeforeExit)
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		
		Event.RegEvent(Event.Eve_StartCircularActive, OpenAct)
		Event.RegEvent(Event.Eve_EndCircularActive, CloseAct)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NYearDiscount_Open", "新年乐翻天打开面板"), RequestOpen)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NYearDiscount_Buy", "新年乐翻天购买"), RequestBuy)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NYearDiscount_Refresh", "新年乐翻天刷新"), RequestFresh)
		