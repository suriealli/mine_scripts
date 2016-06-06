#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.LanternFestival.LanternRebate")
#===============================================================================
# 花灯返利
#===============================================================================
import cRoleMgr
import cNetMessage
import cRoleDataMgr
import Environment
from Game.Role import Event
from Game.Persistence import Contain
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from Game.Activity import CircularDefine
from Game.Role.Data import EnumInt32, EnumObj
from Game.Activity.LanternFestival import LanternFestivalConfig


if "_HasLoad" not in dir():
	IsStart = False
	
	#消息
	SyncLanternRebateRoleData = AutoMessage.AllotMessage("SyncLanternRebateRoleData", "同步客户端花灯返利角色返利领取数据")
	SyncLanternRebateServerData = AutoMessage.AllotMessage("SyncLanternRebateServerData", "同步客户端花灯返利全服返利数据")
	
	#日志
	Tra_LanternRebate = AutoLog.AutoTransaction("Tra_LanternRebate", "元宵节花灯返利")
	
	
def Start(param1, param2):
	if param2 != CircularDefine.CA_LanternRebate:
		return
	
	global IsStart
	if IsStart:
		print "GE_EXC, LanternRebate is already started"
		return
	
	IsStart = True
	

def End(param1, param2):
	if param2 != CircularDefine.CA_LanternRebate:
		return
	global IsStart
	if not IsStart:
		print "GE_EXC, LanternRebate is already ended"
		return
	IsStart = False



def AfterChangeLanternPoint(role, oldValue, newValue):
	if IsStart is False:
		return
	if newValue <= oldValue:
		return
	if role.GetLevel() < EnumGameConfig.LanternFestivalNeedLevel:
		return
	
	needGloabalTell = False
	roleId = role.GetRoleID()
	roleName = role.GetRoleName()
	#拿出这个活动的配置字典
	for index, needPoint in LanternFestivalConfig.LanternRebateActiveDict.iteritems():
		#如果新值小于激活该index需要的积分，则不能激活
		if newValue < needPoint:
			continue
		theDict = LanternFestivalRebateDict.setdefault(index, {})
		#激活顺便更新角色的名字
		if not roleId in theDict:
			needGloabalTell = True
			
		theDict[roleId] = roleName
		LanternFestivalRebateDict.HasChange()
	
	if needGloabalTell:
		cNetMessage.PackPyMsg(SyncLanternRebateServerData, LanternFestivalRebateDict.data)
		cRoleMgr.BroadMsg()
		


def RequestGetAward(role, msg):
	'''
	客户端请求领取花灯返利奖励
	'''
	index, rebateLevel = msg
	
	config = LanternFestivalConfig.LanternRebateDict.get((index, rebateLevel))
	if config is None:
		return
	
	if role.GetLevel() < EnumGameConfig.LanternFestivalNeedLevel:
		return
	#角色VIP等级不符合要求
	if role.GetVIP() < config.NeedVIPLevel:
		return
	#返利列表
	rebateDict = LanternFestivalRebateDict.get(index, [])
	if not rebateDict:
		return
	
	gotRebateDict = role.GetObj(EnumObj.LanternFestival).setdefault('rebate', {})
	gotRebateSet = gotRebateDict.setdefault(index, {}).setdefault(rebateLevel, set())
	
	rebateRoleID = None
	for roleId in rebateDict.iterkeys():
		if roleId not in gotRebateSet:
			rebateRoleID = roleId
			break
		
	if not rebateRoleID:
		return
	#获取要感谢的那个玩家的名字，用于发奖的时候的提示信息
	thankName = rebateDict[rebateRoleID]
	#这里要增加日志
	itemCoding, itemCnt = config.Items
	
	with Tra_LanternRebate:
		gotRebateSet.add(rebateRoleID)
		role.AddItem(itemCoding, itemCnt)
	
	role.SendObj(SyncLanternRebateRoleData, gotRebateDict)
	
	role.Msg(2, 0, GlobalPrompt.Reward_Item_Tips % (itemCoding, itemCnt))
	cRoleMgr.Msg(11, 0, GlobalPrompt.LanternRebateGlobalTips % (role.GetRoleName(), itemCoding, itemCnt, thankName))
	
	

def SyncRoleOtherData(role, param):
	if not IsStart:
		return
	gotRebateDict = role.GetObj(EnumObj.LanternFestival).get('rebate', {})
	role.SendObj(SyncLanternRebateRoleData, gotRebateDict)
	role.SendObj(SyncLanternRebateServerData, LanternFestivalRebateDict.data)


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, Start)
		Event.RegEvent(Event.Eve_EndCircularActive, End)
		
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		
		cRoleDataMgr.SetInt32Fun(EnumInt32.LanternFestivalPoint, AfterChangeLanternPoint)
		#奖励索引-->{roleID-->roleName}
		LanternFestivalRebateDict = Contain.Dict("LanternFestivalRebateDict")
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestGetLanternRebate", "客户端请求元获取花灯返利奖励"), RequestGetAward)


		
