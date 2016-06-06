#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionGodTreeExchange")
#===============================================================================
# 国庆神树兑换	@author: GaoShuai
#===============================================================================
import Environment
import cRoleMgr
from Game.Role import Event
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Activity import CircularDefine
from Game.Role.Data import EnumObj
from Common.Other import GlobalPrompt
from Game.Activity.PassionAct import PassionGodTreeExchangeConfig, PassionDefine


if "_HasLoad" not in dir():
	IsStart = False
	rewardList = []
	GoddTreeExchange_BroadRoleID_Set = set()
	
	GodTreeExchangeData = AutoMessage.AllotMessage("GodTreeExchangeData", "神树兑换个人数据")
	GodTreeExchangeRecord = AutoMessage.AllotMessage("GodTreeExchangeRecord", "神树兑换全服数据记录")
	#日志
	PassionGodTreeExchange_Log = AutoLog.AutoTransaction("PassionGodTreeExchange_Log", "神树兑换商店物品兑换日志")
	
def StartCircularActive(param1, param2):
	if param2 != CircularDefine.CA_PassionGodTreeExchange:
		return
	global IsStart
	if IsStart:
		print 'GE_EXC, PassionGodTreeExchange is already start'
	IsStart = True

def EndCircularActive(param1, param2):
	if param2 != CircularDefine.CA_PassionGodTreeExchange:
		return
	global IsStart, rewardList, GoddTreeExchange_BroadRoleID_Set
	if not IsStart:
		print 'GE_EXC, PassionGodTreeExchange is already end'
	IsStart = False
	rewardList = []
	GoddTreeExchange_BroadRoleID_Set.clear()
def RequestOpenPanel(role, param=None):
	'''
	神树兑换商店打开面板
	@param role:
	@param param: None
	'''
	global rewardList, IsStart, GoddTreeExchange_BroadRoleID_Set
	if not IsStart:
		return
	if len(rewardList) > 50:
		rewardList = rewardList[-50:]
	
	role.SendObj(GodTreeExchangeData, role.GetObj(EnumObj.PassionActData).get(PassionDefine.PassionGodTreeExchange))
	role.SendObj(GodTreeExchangeRecord, rewardList)
	GoddTreeExchange_BroadRoleID_Set.add(role.GetRoleID())
def RequestClosePanel(role, param=None):
	'''
	神树兑换商店关闭面板
	@param role:
	@param param: None
	'''
	global IsStart, GoddTreeExchange_BroadRoleID_Set
	if not IsStart:
		return
	GoddTreeExchange_BroadRoleID_Set.discard(role.GetRoleID())
def RequestGodTreeExchange(role, param):
	'''
	神树兑换商店请求兑换
	@param role:
	@param param: 物品索引index, 兑换个数
	'''
	global IsStart
	if not IsStart:
		return
	index, requestCnt = param
	if requestCnt <= 0:
		return
	itemObj = PassionGodTreeExchangeConfig.GodTreeExchange_Dict.get(index)
	if not itemObj:
		print "GE_EXC, can't find the itemObj in GodTreeExchange_Dict index = %s" % index
		return 
	#等级
	if role.GetLevel() < itemObj.minLevel:
		return
	#物品数量不够
	if role.ItemCnt(itemObj.needCoding) < itemObj.needCnt * requestCnt:
		return
	#物品数量超过限购
	exchangeObj = role.GetObj(EnumObj.PassionActData).get(PassionDefine.PassionGodTreeExchange)
	MaxNum = itemObj.limitCnt - exchangeObj.get(index, 0)
	if itemObj.limitCnt != -1 and MaxNum < requestCnt:
		return
	#记录玩家兑换数据
	if itemObj.limitCnt != -1:
		exchangeObj[index] = exchangeObj.get(index, 0) + requestCnt
	coding, cnt = itemObj.items
	with PassionGodTreeExchange_Log:
		role.DelItem(itemObj.needCoding, itemObj.needCnt * requestCnt)
		role.AddItem(coding, cnt * requestCnt)
	
	role.SendObj(GodTreeExchangeData, exchangeObj)
	
	global rewardList, GoddTreeExchange_BroadRoleID_Set
	rewardList.append((role.GetRoleName(), coding, cnt * requestCnt))
	#向打开面板玩家同步消息
	oldRoleSet = set()
	for roleId in GoddTreeExchange_BroadRoleID_Set:
		roleTmp = cRoleMgr.FindRoleByRoleID(roleId)
		if not roleTmp or roleTmp.IsLost() or roleTmp.IsKick():
			oldRoleSet.add(roleId)
			continue
		roleTmp.SendObj(GodTreeExchangeRecord, rewardList)
	GoddTreeExchange_BroadRoleID_Set -= oldRoleSet
	if itemObj.special:
		cRoleMgr.Msg(1, 0, GlobalPrompt.PassionGodTreeExchange % (role.GetRoleName(), coding, cnt * requestCnt))
	else:
		role.Msg(2, 0, GlobalPrompt.Item_Exchang_Tips + GlobalPrompt.Item_Tips % (coding, cnt * requestCnt))
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_StartCircularActive, StartCircularActive)
		Event.RegEvent(Event.Eve_EndCircularActive, EndCircularActive)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GodTreeExchange", "国庆神树兑换商店请求兑换"), RequestGodTreeExchange)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GodTreeExchangeOpenPanel", "国庆神树兑换商店打开面板"), RequestOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GodTreeExchangeClosePanel", "国庆神树兑换商店关闭面板"), RequestClosePanel)
		
