#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionExchange")
#===============================================================================
# 激情活动 -- 限时兑换
#===============================================================================
import Environment
import cRoleMgr
from Common.Other import EnumGameConfig, GlobalPrompt
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumObj
from Game.Role import Event
from Game.Activity.PassionAct import PassionExchangeConfig, PassionDefine
from Game.Activity import CircularDefine


if "_HasLoad" not in dir():
	IsStart = False
	
	PassionExchangeRecordList = []
	
	#{1:0(占位), 2:{goodId:cnt}, 3:freshCnt}
	PassionExchangeData = AutoMessage.AllotMessage("PassionExchangeData", "激情活动限时兑换数据")
	PassionExchangeRecord = AutoMessage.AllotMessage("PassionExchangeRecord", "激情活动限时兑换数据记录")
	
	PassionExchangeBuy_Log = AutoLog.AutoTransaction("PassionExchangeBuy_Log", "激情活动限时兑换兑换日志")
	PassionExchangeRefresh_Log = AutoLog.AutoTransaction("PassionExchangeRefresh_Log", "激情活动限时兑换刷新日志")
#===============================================================================
# 事件
#===============================================================================
def StartCircularActive(param1, param2):
	if param2 != CircularDefine.CA_PassionExchange:
		return
	global IsStart
	if IsStart:
		print 'GE_EXC, PassionExchange is already start'
	IsStart = True

def EndCircularActive(param1, param2):
	if param2 != CircularDefine.CA_PassionExchange:
		return
	global IsStart, PassionExchangeRecordList
	if not IsStart:
		print 'GE_EXC, PassionExchange is already end'
	IsStart = False
	
	PassionExchangeRecordList = []
#===============================================================================
# 辅助
#===============================================================================
def GetCloseValue(value, valueList):
	#valueList是逆序的, 返回第一个小于等于value的值
	for i in valueList:
		if i <= value:
			return i
	else:
		return 0
	
def GetItemList(role):
	if role.IsKick():
		return
	
	advanceLevel = GetCloseValue(role.GetLevel(), PassionExchangeConfig.PassionExchangeAdvanceLV_List)
	normalLevel = GetCloseValue(role.GetLevel(), PassionExchangeConfig.PassionExchangeNormalLV_List)
	
	if (not advanceLevel) or (not normalLevel) or (advanceLevel not in PassionExchangeConfig.PassionExchangeAdvanceRD_Dict) or (normalLevel not in PassionExchangeConfig.PassionExchangeNormalRD_Dict):
		print 'GE_EXC, PassionExchange GetItemList can not find advanceLevel %s or normalLevel %s' % (advanceLevel, normalLevel)
		return
	
	return PassionExchangeConfig.PassionExchangeAdvanceRD_Dict[advanceLevel].RandomMany(2) + PassionExchangeConfig.PassionExchangeNormalRD_Dict[normalLevel].RandomMany(4)
#===============================================================================
# 请求
#===============================================================================
def RequestOpen(role, msg):
	'''
	激情活动限时兑换打开面板
	@param role:
	@param msg:
	'''
	global IsStart
	if not IsStart: return
	
	if role.GetLevel() < EnumGameConfig.PassionMinLevel:
		return
	
	exchangeObj = role.GetObj(EnumObj.PassionActData).get(PassionDefine.PassionExchange)
	
	global PassionExchangeRecordList
	
	if exchangeObj:
		#打开过面板
		role.SendObj(PassionExchangeData, exchangeObj)
		role.SendObj(PassionExchangeRecord, PassionExchangeRecordList)
		return
	
	#获取随机到的物品配置
	itemList = GetItemList(role)
	if not itemList:
		print 'GE_EXC, PassionExchange RequestOpen return error'
		return
	role.GetObj(EnumObj.PassionActData)[PassionDefine.PassionExchange] = packObj = {1:0, 2:{goodId:0 for goodId in itemList}, 3:1}
	
	role.SendObj(PassionExchangeData, packObj)
	role.SendObj(PassionExchangeRecord, PassionExchangeRecordList)
	
def RequestExchange(role, msg):
	'''
	激情活动限时兑换兑换
	@param role:
	@param msg:
	'''
	global IsStart
	if not IsStart: return
	
	if role.GetLevel() < EnumGameConfig.PassionMinLevel:
		return
	
	goodId, cnt = msg
	
	if cnt <= 0:
		return
	
	#配置
	cfg = PassionExchangeConfig.PassionExchange_Dict.get(goodId)
	if not cfg:
		print 'GE_EXC, PassionExchange RequestBuy can not din goodId %s in PassionExchange_Dict' % goodId
		return
	
	exchangeObj = role.GetObj(EnumObj.PassionActData).get(PassionDefine.PassionExchange)
	#没有打开过面板 or 这批刷新的没有这个物品 or 这个物品已经被买完了
	if (not exchangeObj) or (goodId not in exchangeObj[2]) or (exchangeObj[2][goodId] >= cfg.limitCnt) or (exchangeObj[2][goodId] + cnt > cfg.limitCnt):
		return
	
	needCnt, getCoding, getCnt = cfg.needCnt * cnt, cfg.items[0], cfg.items[1] * cnt
	
	if role.ItemCnt(cfg.needCoding) < needCnt:
		return
	
	with PassionExchangeBuy_Log:
		role.DelItem(cfg.needCoding, needCnt)
		
		#限购数量减1
		exchangeObj[2][goodId] += cnt
		role.GetObj(EnumObj.PassionActData)[PassionDefine.PassionExchange] = exchangeObj
		
		#发物品
		role.AddItem(getCoding, getCnt)
		
		if cfg.isRecord:
			global PassionExchangeRecordList
			PassionExchangeRecordList.append([role.GetRoleName(), getCoding, getCnt])
			if len(PassionExchangeRecordList) > 50:
				#超过50的话顶掉前面的
				PassionExchangeRecordList.pop(0)
			role.SendObj(PassionExchangeRecord, PassionExchangeRecordList)
		
		role.SendObj(PassionExchangeData, exchangeObj)
	role.Msg(2, 0, GlobalPrompt.Reward_Item_Tips % (getCoding, getCnt))
	
def RequestFresh(role, msg):
	'''
	激情活动限时兑换刷新
	@param role:
	@param msg:
	'''
	global IsStart
	if not IsStart: return
	
	if role.GetLevel() < EnumGameConfig.PassionMinLevel:
		return
	
	exchangeObj = role.GetObj(EnumObj.PassionActData).get(PassionDefine.PassionExchange)
	if not exchangeObj:
		return
	
	#配置
	freshCnt = exchangeObj[3]
	if freshCnt >= PassionExchangeConfig.PassionExchangeFreshMaxCnt:
		freshCnt = PassionExchangeConfig.PassionExchangeFreshMaxCnt
	cfg = PassionExchangeConfig.PassionExchangeFresh_Dict.get(freshCnt)
	if not cfg:
		print 'GE_EXC, PassionExchange RequestFresh can not find refresh cnt %s' % freshCnt
		return
	
	if role.GetUnbindRMB() < cfg.needRMB:
		return
	
	with PassionExchangeRefresh_Log:
		role.DecUnbindRMB(cfg.needRMB)
		
		#获取随机到的物品配置
		itemList = GetItemList(role)
		if not itemList:
			print 'GE_EXC, PassionExchange RequestFresh return error'
			return
		
		role.GetObj(EnumObj.PassionActData)[PassionDefine.PassionExchange][2] = {goodId:0 for goodId in itemList}
		role.GetObj(EnumObj.PassionActData)[PassionDefine.PassionExchange][3] += 1
		
		AutoLog.LogBase(role.GetRoleID(), AutoLog.evePassionExchangeRefresh, cfg.needRMB)
		
		role.SendObj(PassionExchangeData, role.GetObj(EnumObj.PassionActData)[PassionDefine.PassionExchange])
		
		role.Msg(2, 0, GlobalPrompt.PassionExchangeFresh % cfg.needRMB)

def RoleDayClear(role, param):
	exchangeObj = role.GetObj(EnumObj.PassionActData).get(PassionDefine.PassionExchange)
	if not exchangeObj:
		#如果之前没有打开过面板, 不处理
		return
	
	global IsStart
	if not IsStart:
		#活动结束的话清理
		role.GetObj(EnumObj.PassionActData)[PassionDefine.PassionExchange] = {}
		return
	
	#获取随机到的物品配置
	itemList = GetItemList(role)
	if not itemList:
		print 'GE_EXC, PassionExchange RoleDayClear return error'
		return
	
	#重置数据
	role.GetObj(EnumObj.PassionActData)[PassionDefine.PassionExchange] = packObj = {1:0, 2:{goodId:0 for goodId in itemList}, 3:1}
	role.SendObj(PassionExchangeData, packObj)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		
		Event.RegEvent(Event.Eve_StartCircularActive, StartCircularActive)
		Event.RegEvent(Event.Eve_EndCircularActive, EndCircularActive)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("PassionExchange_Open", "激情活动限时兑换打开面板"), RequestOpen)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("PassionExchange_Exchange", "激情活动限时兑换兑换"), RequestExchange)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("PassionExchange_Refresh", "激情活动限时兑换刷新"), RequestFresh)
		
