#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.RMBFund.RMBFund")
#===============================================================================
# 神石基金
#===============================================================================
import cComplexServer
import cNetMessage
import cRoleDataMgr
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Activity.RMBFund import RMBFundConfig
from Game.Persistence import Contain
from Game.Role import Event
from Game.Role.Data import EnumDisperseInt32
from Game.SysData import WorldData
from Game.Role.Mail import Mail

if "_HasLoad" not in dir():
	RMBFundIndex = AutoMessage.AllotMessage("RMBFundIndex", "神石基金开启编号")
	
	RMBFundRecord = AutoMessage.AllotMessage("RMBFundRecord", "神石基金购买记录")
	
	RMBFundBuy_Log = AutoLog.AutoTransaction("RMBFundBuy_Log", "神石基金购买日志")
	RMBFundExchange_Log = AutoLog.AutoTransaction("RMBFundExchange_Log", "神石基金兑换日志")
	RMBFundClear_Log = AutoLog.AutoTransaction("RMBFundClear_Log", "神石基金清理")
	RMBFundEnd_Log = AutoLog.AutoTransaction("RMBFundEnd_Log", "神石基金结束时邮件返还奖励")
	
def OpenFund(index):
	'''
	开启神石基金
	'''
	global RMBFundDict
	RMBFundDict["index"] = index
	
def CloseFund():
	'''
	关闭神石基金
	'''
	global RMBFundDict
	if not RMBFundDict["index"]:
		return
	RMBFundDict["index"] = 0
	
	delIdSet = set()
	
	for roleId, funddata in RMBFundDict.items():
		if roleId == "index":
			continue
		
		if not funddata[3] and (not funddata[5]):
			#有购买, 没有领取, 活动结束通过邮件返还
			
			#本金
			baseRMB = funddata[2]
			#利息
			cfg = RMBFundConfig.RMBFund_Dict.get(GetCloseValue(funddata[4], RMBFundConfig.RMBFund_List), None)
			if cfg:
				interestRMB = funddata[2] * cfg.rate / 10000
			else:
				interestRMB = 0
			#总和
			totalRMB= baseRMB + interestRMB
			with RMBFundEnd_Log:
				#邮件发放奖励后删除记录
				delIdSet.add(roleId)
				Mail.SendMail(roleId, GlobalPrompt.RMBFundMail_Title, GlobalPrompt.RMBFundMail_Sender, GlobalPrompt.RMBFundMail_Content % (baseRMB, interestRMB), unbindrmb = totalRMB)
		RMBFundDict[roleId] = {1:0, 2:0, 3:False, 4:0, 5:False}
		RMBFundDict.changeFlag = True
	
	for roleId in delIdSet:
		if roleId not in RMBFundDict:
			continue
		del RMBFundDict[roleId]
	RMBFundDict.changeFlag = True
	
def RequestBuyFund(role, msg):
	'''
	购买基金
	@param role:
	@param msg:
	'''
	global RMBFundDict
	if not RMBFundDict["index"]: return
	
	if role.GetLevel() < EnumGameConfig.RMBFund_LevelLimit:
		return
	
	roleId = role.GetRoleID()
	
	#没有充值
	rolefunddata = RMBFundDict.get(roleId)
	if not rolefunddata:
		return
	#已购买
	if rolefunddata[2]:
		return
	#累计充值
	consumeQPoint = rolefunddata[1]
	if not consumeQPoint:
		return
	#累计充值不足
	consume = GetCloseValue(consumeQPoint, RMBFundConfig.RMBPoint_List)
	if not consume:
		return
	
	#可以购买的基金
	canBuyFund = RMBFundConfig.RMBPoint_Dict.get(consume)
	if not canBuyFund:
		return
	
	#不是可以购买的金额
	if msg not in RMBFundConfig.RMBPoint_Dict.values():
		return
	#超过可以购买的基金
	if msg > canBuyFund:
		return
	
	#神石不足
	if role.GetUnbindRMB() < msg:
		return
	
	#扣钱
	with RMBFundBuy_Log:
		role.DecUnbindRMB(msg)
		
	#购买数据 --> #{1:活动期间累计充值, 2:购买金额, 3:是否领取, 4:天数, 5:活动是否结束}
	rolefunddata[2] = msg
	rolefunddata[4] = 1
	RMBFundDict.changeFlag = True
	
	role.SendObj(RMBFundRecord, rolefunddata)
	
def RequestExchange(role, msg):
	'''
	兑换基金 -- 活动结束后有未领取的基金可以领取
	@param role:
	@param msg:
	'''
	if role.GetLevel() < EnumGameConfig.RMBFund_LevelLimit:
		return
	
	roleId = role.GetRoleID()
	global RMBFundDict
	
	#没有充值
	rolefunddata = RMBFundDict.get(roleId)
	if not rolefunddata:
		return
	#没有购买
	if not rolefunddata[2]:
		return
	#已提取
	if rolefunddata[3]:
		return
	
	#这里不处理活动结束后的数据（旧数据）， 旧数据会在数据载回时被处理
	
	days = rolefunddata[4]
	if days <= 1:
		#第一天不能领取
		return
	
	#设置已领取标志
	rolefunddata[3] = True
	RMBFundDict.changeFlag = True
	
	with RMBFundExchange_Log:
		#计算本息
		rmb = CalEarn(days, rolefunddata[2])
		role.IncUnbindRMB_S(rmb)
	
	role.SendObj(RMBFundRecord, rolefunddata)
	role.Msg(2, 0, GlobalPrompt.UnBindRMB_Tips % rmb)
	
def CalEarn(days, rmb):
	'''
	计算本息
	@param days:
	@param rmb:
	'''
	cfg = RMBFundConfig.RMBFund_Dict.get(GetCloseValue(days, RMBFundConfig.RMBFund_List), None)
	if cfg is None:
		return
	return rmb + rmb * cfg.rate / 10000

def GetCloseValue(value, value_list):
	'''
	返回第一个大于value的上一个值
	@param value:
	@param value_list:
	'''
	tmp_level = 0
	for i in value_list:
		if i > value:
			return tmp_level
		tmp_level = i
	else:
		#没有找到返回最后一个值
		return tmp_level
	
def AfterChangeUnbindRMB(role, param):
	'''
	充值神石变化
	@param role:
	@param param:
	'''
	if not Environment.EnvIsNA():#以下逻辑只在北美用
		return
	
	oldValue, newValue = param
	
	if newValue <= oldValue:
		return
	
	global RMBFundDict
	if not RMBFundDict["index"]: return
	
	roleId = role.GetRoleID()
	
	if roleId not in RMBFundDict:
		RMBFundDict[roleId] = {1:0, 2:0, 3:False, 4:0, 5:False}
	
	#{1:活动期间累计充值, 2:购买金额, 3:是否领取, 4:天数, 5:活动是否结束}
	RMBFundDict[roleId][1] += newValue - oldValue
	RMBFundDict.changeFlag = True
	
	role.SendObj(RMBFundRecord, RMBFundDict[roleId])
	
def AfterConsumeQPoint(role, oldValue, newValue):
	'''
	记录活动期间充值 -- 活动期间充值没有等级限制
	@param role:
	@param oldValue:
	@param newValue:
	'''
	if Environment.EnvIsNA():#是北美环境直接返回
		return
	
	if newValue <= oldValue:
		return
	
	global RMBFundDict
	if not RMBFundDict["index"]: return
	
	roleId = role.GetRoleID()
	
	if roleId not in RMBFundDict:
		RMBFundDict[roleId] = {1:0, 2:0, 3:False, 4:0, 5:False}
	
	#{1:活动期间累计充值, 2:购买金额, 3:是否领取, 4:天数, 5:活动是否结束}
	RMBFundDict[roleId][1] += newValue - oldValue
	RMBFundDict.changeFlag = True
	
	role.SendObj(RMBFundRecord, RMBFundDict[roleId])
	
def SyncRoleOtherData(role, param):
	'''
	上线, 刷新同步其他数据
	@param role:
	@param param:
	'''
	global RMBFundDict
	role.SendObj(RMBFundIndex, RMBFundDict.get("index", 0))
	
	if role.GetLevel() < EnumGameConfig.RMBFund_LevelLimit:
		return
	
	roleId = role.GetRoleID()
	
	#没有充值
	rolefunddata = RMBFundDict.get(roleId)
	if not rolefunddata:
		return
	
	if (not RMBFundDict["index"]) and (rolefunddata[3] or (not rolefunddata[2])):
		#活动关闭, 奖励已领取或没有购买基金
		return
	
	role.SendObj(RMBFundRecord, rolefunddata)
	
def OpenOrClose(kaifuDay, oldDay = None):
	#开启或关闭
	global RMBFundDict
	if not RMBFundDict.returnDB: return
	
	nowIndex = RMBFundDict["index"]
	
	#如果当前活动是开的, 先尝试关闭活动
	if nowIndex and oldDay is None:
		#对直接设置开服时间不处理
		for (beginDay, endDay), index in RMBFundConfig.RMBFundActive_Dict.iteritems():
			if nowIndex != index:
				continue
			#当前开服天数不在当前索引对应的开服天数区间范围内, 关闭活动
			if kaifuDay >= endDay or kaifuDay < beginDay:
				CloseFund()
				cNetMessage.PackPyMsg(RMBFundIndex, 0)
				cRoleMgr.BroadMsg()
	
	#再尝试激活活动(激活的规则是必须要开服天数和开始天数相同才能激活)
	for (beginDay, endDay), index in RMBFundConfig.RMBFundActive_Dict.iteritems():
		if beginDay == kaifuDay:
			OpenFund(index)
			cNetMessage.PackPyMsg(RMBFundIndex, index)
			cRoleMgr.BroadMsg()
			break
		elif endDay == kaifuDay:
			CloseFund()
			cNetMessage.PackPyMsg(RMBFundIndex, 0)
			cRoleMgr.BroadMsg()
			break
		if oldDay is None:
			continue
		#修改开服时间触发
		if beginDay < kaifuDay < endDay:
			#当前的开服天数处在开启期间内,把活动开启来
			OpenFund(index)
			cNetMessage.PackPyMsg(RMBFundIndex, index)
			cRoleMgr.BroadMsg()
			break
		elif beginDay <= oldDay < endDay:
			#原来是开的，现在的天数不符合这个开启的时间段，所以要关闭
			CloseFund()
			cNetMessage.PackPyMsg(RMBFundIndex, 0)
			cRoleMgr.BroadMsg()
			break

def AfterSetKaiFuTime(p1, p2):
	old_kaifuDay, newDay = p2
	if old_kaifuDay == newDay:
		return
	OpenOrClose(newDay, old_kaifuDay)
	
def AfterNewDay():
	'''
	跨天时基金存放天数 + 1
	@param role:
	@param param:
	'''
	kaifuDay = WorldData.GetWorldKaiFuDay()
	OpenOrClose(kaifuDay)
	
	global RMBFundDict
	if not RMBFundDict["index"]:
		return
	
	for roleId, fundData in RMBFundDict.iteritems():
		if roleId == "index":
			continue
		#没有购买基金
		if not fundData[2]:
			continue
		#基金已兑换
		if fundData[3]:
			continue
		#活动结束
		if fundData[5]:
			continue
		
		#存储天数加一
		fundData[4] += 1
		RMBFundDict.changeFlag = True
		
		role = cRoleMgr.FindRoleByRoleID(roleId)
		if not role:
			continue
		
		role.SendObj(RMBFundRecord, fundData)
		
def AfterLoad():
	global RMBFundDict
	if "index" not in RMBFundDict:
		RMBFundDict["index"] = 0
		
	if not WorldData.WD.returnDB:
		return
	OpenOrClose(WorldData.GetWorldKaiFuDay())
	
	delIdSet = set()
	
	for roleId, funddata in RMBFundDict.items():
		if roleId == "index" or (not funddata[5]):
			continue
		
		#本金
		baseRMB = funddata[2]
		#利息
		cfg = RMBFundConfig.RMBFund_Dict.get(GetCloseValue(funddata[4], RMBFundConfig.RMBFund_List), None)
		if cfg:
			interestRMB = funddata[2] * cfg.rate / 10000
		else:
			interestRMB = 0
		#总和
		totalRMB= baseRMB + interestRMB
		
		with RMBFundEnd_Log:
			delIdSet.add(roleId)
			Mail.SendMail(roleId, GlobalPrompt.RMBFundMail_Title, GlobalPrompt.RMBFundMail_Sender, GlobalPrompt.RMBFundMail_Content % (baseRMB, interestRMB), unbindrmb = totalRMB)
		
		RMBFundDict[roleId] = {1:0, 2:0, 3:False, 4:0, 5:False}
		RMBFundDict.changeFlag = True
		
	for roleId in delIdSet:
		if roleId not in RMBFundDict:
			continue
		del RMBFundDict[roleId]
	RMBFundDict.changeFlag = True
	
def AfterLoadWorldData(param1, param2):
	OpenOrClose(WorldData.GetWorldKaiFuDay())

if "_HasLoad" not in dir():
	if Environment.HasLogic or Environment.HasWeb:
		RMBFundDict = Contain.Dict("RMBFundDict", (2038, 1, 1), AfterLoad)
	
	
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		Event.RegEvent(Event.Eve_AfterSetKaiFuTime, AfterSetKaiFuTime)
		Event.RegEvent(Event.Eve_AfterLoadWorldData, AfterLoadWorldData)
		Event.RegEvent(Event.AfterChangeUnbindRMB_Q, AfterChangeUnbindRMB)
		
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
	
		cRoleDataMgr.SetDisperseInt32Fun(EnumDisperseInt32.ConsumeQPoint, AfterConsumeQPoint)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RMBFund_Buy", "购买基金"), RequestBuyFund)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RMBFund_Exchange", "兑换基金"), RequestExchange)
	
	