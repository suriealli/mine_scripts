#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.Award.AwardMgr")
#===============================================================================
# 玩法奖励管理
#===============================================================================
import cDateTime
import cRoleMgr
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Activity.Award import AwardConfig
from Game.Role import Call, Event
from Game.Role.Data import EnumObj
import Environment

if "_HasLoad" not in dir():
	AWARD_SAVE_DAYS_MAX = 7		#奖励最大保存天数
	
	
	#消息
	Award_Show_Main_Panel = AutoMessage.AllotMessage("Award_Show_Main_Panel", "通知客户端显示玩法奖励主面板")
	Award_Has_Award = AutoMessage.AllotMessage("Award_Has_Award", "通知客户端有活动奖励可以领取")
	
def ShowAwardMainPanel(role):
	'''
	显示奖励面板
	@param role:
	'''
	awardDict = role.GetObj(EnumObj.Award)[1]
	
	#枚举和奖励显示数量
	sendList = [(awardEnum, allAwardList) for awardEnum, allAwardList in awardDict.iteritems()]
	
	role.SendObj(Award_Show_Main_Panel, sendList)
	
def GetAward(role, awardId, awardIdx):
	'''
	领取奖励
	@param role:
	@param awardId:
	@param awardIdx:
	'''
	awardDict = role.GetObj(EnumObj.Award)[1]
	
	#是否可以领取对应奖励
	if awardId not in awardDict:
		return
	
	awardList = awardDict[awardId]
	#awardIdx是否存在
	if awardIdx < 0 or  awardIdx > len(awardList):
		return
	
	award = awardList[awardIdx - 1]
	_, money, exp, reputation, bindRMB, itemList, _ = award
	
	#先删除
	awardList.remove(award)
	
	#奖励
	if money > 0:
		role.IncMoney(money)
	if exp > 0:
		role.IncExp(int(exp * (1 + role.GetExpCoef() / 100.0)))
	if reputation > 0:
		role.IncReputation(reputation)
	if bindRMB > 0:
		role.IncBindRMB(bindRMB)
	if itemList:
		for item in itemList:
			role.AddItem(*item)
			
	#日志事件
	AutoLog.LogBase(role.GetRoleID(), AutoLog.eveGetAward)
		
	#显示主面板
	ShowAwardMainPanel(role)
	
#===============================================================================
# 离线命令调用奖励函数
#===============================================================================
def SetAward(roleId, awardEnum, money = 0, exp = 0, reputation = 0, bindRMB = 0, itemList = None, clientDescParam = ()):
	'''
	设置玩法奖励,发送离线命令
	@param roleId:
	@param param:
	'''
	if itemList is None:
		itemList = []
	
	Call.LocalDBCall(roleId, SetAwardCall, (awardEnum, cDateTime.Days(), money, exp, reputation, bindRMB, itemList, clientDescParam))

def SetAwardCall(role, param):
	'''
	设置奖励调用
	@param role:
	@param param:
	'''
	#调用离线命令
	awardEnum, days, money, exp, reputation, bindRMB, itemList, clientDescParam = param
	#是否已经7天没上线（奖励最多保存7天）
	if cDateTime.Days() - days > AWARD_SAVE_DAYS_MAX:
		return
	awardDict = role.GetObj(EnumObj.Award)[1]
	awardDict.setdefault(awardEnum, []).append((days, money, exp, reputation, bindRMB, itemList, clientDescParam))
	#通知客户端有奖励
	role.SendObj(Award_Has_Award, None)
	
#===============================================================================
# 事件
#===============================================================================
def OnSyncRoleOtherData(role, param):
	'''
	角色登录同步其他剩余的数据
	@param role:
	@param param:
	'''
	awardDict = role.GetObj(EnumObj.Award)[1]
	#枚举和奖励显示数量
	for awardList in awardDict.itervalues():
		if len(awardList) > 0:
			#通知客户端有奖励
			role.SendObj(Award_Has_Award, None)
			break
	

def OnRoleDayClear(role, param):
	'''
	每日清理
	@param role:
	@param param:
	'''
	#玩法奖励最多保存7天
	
	awardDict = role.GetObj(EnumObj.Award).get(1)
	if not awardDict:
		return
	
	currentDays = cDateTime.Days()
	for awardList in awardDict.itervalues():
		delAwardList = []	#保存需要删除的奖励
		for award in awardList:
			oldDays = award[0]
			if currentDays - oldDays > AWARD_SAVE_DAYS_MAX:
				delAwardList.append(award)
				
		for delAward in delAwardList:
			awardList.remove(delAward)
			
#===============================================================================
# 客户端请求
#===============================================================================
def RequestAwardOpenMainPanel(role, msg):
	'''
	客户端请求打开奖励面板
	@param role:
	@param msg:
	'''
	ShowAwardMainPanel(role)
	
def RequestAwardGet(role, msg):
	'''
	客户端请求领取奖励
	@param role:
	@param msg:
	'''
	awardId, awardIdx = msg
	
	#获取对应奖励的日志对象
	transaction = AwardConfig.AWARDID_TO_LOG_OBJ.get(awardId)
	if not transaction:
		return
	
	#日志
	with transaction:
		GetAward(role, awardId, awardIdx)

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		if not Environment.IsCross:
			#角色登录同步其他剩余的数据
			Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		#每日清理调用
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
		
		#注册消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Award_Open_Main_Panel", "客户端请求打开奖励主面板"), RequestAwardOpenMainPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Award_Get", "客户端请求领取奖励"), RequestAwardGet)
		
	