#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.RMBBank.RMBBank")
#===============================================================================
# 神石银行
#===============================================================================
import Environment
import cRoleMgr
import cComplexServer
from Common.Message import AutoMessage, PyMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from ComplexServer.Plug.Control import ControlProxy
from Game.Persistence import Contain
from Game.Activity.RMBBank import RMBBankConfig
from Game.Role import Event
from Game.GlobalData import ZoneName

if "_HasLoad" not in dir():
	RMBBankData = AutoMessage.AllotMessage("RMBBankData", "神石银行存取数据")
	RMBBankRecord = AutoMessage.AllotMessage("RMBBankRecord", "神石银行存取记录")
	RMBBankSingleRecord = AutoMessage.AllotMessage("RMBBankSingleRecord", "神石银行单条存取记录")
	
	RMBBankBuy_Log = AutoLog.AutoTransaction("RMBBankBuy_Log", "神石银行存放日志")
	RMBBankExtract_Log = AutoLog.AutoTransaction("RMBBankExtract_Log", "神石银行提取日志")
	
	
	RMBBankRecordList = []
	
def RequestOpenBank(role, msg):
	'''
	请求打开银行
	@param role:
	@param msg:
	'''
	#等级
	if role.GetLevel() < EnumGameConfig.RMBBankLevelLimit:
		return
	
	#记录
	global RMBBankRecordList
	role.SendObj(RMBBankRecord, RMBBankRecordList)
	
def RequestStore(role, msg):
	'''
	请求存放
	@param role:
	@param msg:
	'''
	index = msg
	if not index: return
	
	#等级
	if role.GetLevel() < EnumGameConfig.RMBBankLevelLimit:
		return
	
	#配置
	cfg = RMBBankConfig.RMBBankGrade_Dict.get(index)
	if not cfg:
		return
	maxRMB = 0
	if Environment.EnvIsNA():
		maxRMB = EnumGameConfig.RMBBankMax_NA
	else:
		maxRMB = EnumGameConfig.RMBBankMax
	if cfg.RMB_Q > maxRMB:
		print "GE_EXC, index (%s) cfg.RMB_Q > EnumGameConfig.RMBBankMax" % index
		return
	
	#没有足够的Q点神石
	if role.GetUnbindRMB_Q() < cfg.RMB_Q:
		return
	
	roleID = role.GetRoleID()
	roleName = role.GetRoleName()
	storeRMB = cfg.RMB_Q
	
	with RMBBankBuy_Log:
		global RMBBankDict
		if roleID not in RMBBankDict:
			#没有存过, 不用判断是否超过限额和是否全部领取
			role.DecUnbindRMB_Q(storeRMB)
			RMBBankDict[roleID] = {1:storeRMB, 2:set()}
			role.SendObj(RMBBankData, {1:storeRMB, 2:set()})
		else:
			#存过, 需要判断存入额是否超过限额以及奖励是否全部领取(奖励已全部领取的话不能再存)
			bankData = RMBBankDict[roleID]
			if bankData[1] + storeRMB > maxRMB or bankData[2] == set(RMBBankConfig.RMBBankRate_Dict.keys()):
				return
			role.DecUnbindRMB_Q(storeRMB)
			bankData[1] += storeRMB
			RMBBankDict[roleID] = bankData
			role.SendObj(RMBBankData, bankData)
	
	#[存放, 服务器名字, 角色名字, 存放神石数, 0]
	record = [1, ZoneName.ZoneName, roleName, cfg.RMB_Q, 0]
	#更新本地缓存
	global RMBBankRecordList
	if len(RMBBankRecordList) >= 200:
		#超过一百条, 删除前面的
		RMBBankRecordList.pop(0)
	RMBBankRecordList.append(record)
	
	#更新跨服数据
	ControlProxy.SendControlMsg(PyMessage.Control_AddBankLog, record)
	
	#有新纪录
	role.SendObj(RMBBankSingleRecord, record)
	
def RequestExtract(role, msg):
	'''
	请求提取
	@param role:
	@param msg:
	'''
	index = msg
	if not index:
		return
	
	roleLevel = role.GetLevel()
	
	#等级
	if roleLevel < EnumGameConfig.RMBBankLevelLimit:
		return
	
	roleID = role.GetRoleID()
	roleName = role.GetRoleName()
	
	#没有存放
	global RMBBankDict
	if roleID not in RMBBankDict:
		return
	bankData = RMBBankDict[roleID]
	
	#该索引奖励已领取
	if index in bankData[2]:
		return
	
	#配置
	cfg = RMBBankConfig.RMBBankRate_Dict.get(index)
	if not cfg:
		return
	
	#领取奖励需要的等级
	if roleLevel < cfg.needLevel:
		return
	
	#加入领取集合
	bankData[2].add(index)
	RMBBankDict[roleID] = bankData
	
	#计算收益
	storeRMB = bankData[1]
	unbindRMB = int(storeRMB * cfg.returnUnbindRMBRates / 100.0)
	bindRMB = int(storeRMB * cfg.returnBindRMBRates / 100.0)
	
	#发放收益
	with RMBBankExtract_Log:
		role.IncBindRMB(bindRMB)
		role.IncUnbindRMB_S(unbindRMB)
	role.SendObj(RMBBankData, bankData)
	
	#记录
	record = [2, ZoneName.ZoneName, roleName, unbindRMB, bindRMB]
	#更新本地缓存
	global RMBBankRecordList
	if len(RMBBankRecordList) >= 200:
		#超过一百条, 删除前面的
		RMBBankRecordList.pop(0)
	RMBBankRecordList.append(record)
	
	#更新跨服数据
	ControlProxy.SendControlMsg(PyMessage.Control_AddBankLog, record)
	
	#有新纪录
	role.SendObj(RMBBankSingleRecord, record)
	
	role.Msg(2, 0, GlobalPrompt.RMBBankExtract_Tips % (unbindRMB, bindRMB))
	
def SyncRoleOtherData(role, param):
	#上线同步玩家神石银行存取数据, 用于控制按钮显示消失
	if role.GetLevel() < EnumGameConfig.RMBBankLevelLimit:
		return
	
	roleID = role.GetRoleID()
	
	global RMBBankDict
	if roleID not in RMBBankDict:
		return
	
	role.SendObj(RMBBankData, RMBBankDict[roleID])


def UpdateBankLog(sessionId, msg):
	#控制进程每小时同步数据过来，覆盖本地缓存
	global RMBBankRecordList
	RMBBankRecordList = msg


if "_HasLoad" not in dir():
	if Environment.HasLogic or Environment.HasWeb:
		RMBBankDict = Contain.Dict("RMBBankDict", (2038, 1, 1))
		
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RMBBank_OpenBank", "神石银行打开银行面板"), RequestOpenBank)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RMBBank_Store", "神石银行存入"), RequestStore)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RMBBank_Extract", "神石银行提取"), RequestExtract)
	if Environment.HasLogic:
		cComplexServer.RegDistribute(PyMessage.Control_UpdateBankLog, UpdateBankLog)
		