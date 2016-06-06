#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.GoldChest.GoldChest")
#===============================================================================
# 黄金宝箱
#===============================================================================
import cRoleMgr
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Util import Random
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Role.Data import EnumObj, EnumDayInt8
from Game.Role import Event
from Game.Activity import CircularDefine, CircularActive
from Game.Activity.GoldChest import GoldChestConfig
import Environment

if "_HasLoad" not in dir():
	
	GoldKeyCode = 26478				#黄金钥匙的物品id
	GCActiveID = 0
	__IS_START = False
	#消息
	Sync_GoldChest_ChestData = AutoMessage.AllotMessage("Sync_GoldChest_ChestData", "同步黄金宝箱的开启情况")
	#日志
	Tra_GoldChest_Reward = AutoLog.AutoTransaction("Tra_GoldChest_Reward", "黄金宝箱开启箱子获得奖励")
	
#===================================================================================	
def GoldChestStart(*param):
	'''
	黄金宝箱活动开启
	'''
	_, circularType = param
	if circularType != CircularDefine.CA_GoldChest:
		return
	
	global __IS_START
	if __IS_START is True:
		print "GE_EXC, GoldChest has already been started"
		return
	__IS_START = True

	global GCActiveID
	if GCActiveID:
		print 'GE_EXC, COTActiveID is already have'
	isActiveTypeRepeat = False
	
	for activeId, (activeType, _) in CircularActive.CircularActiveCache_Dict.iteritems():
		if activeType != circularType:
			continue
		#同一个active_type只允许同时出现一个
		if isActiveTypeRepeat:
			print 'GE_EXC, repeat isActiveTypeRepeat in CircularActiveCache_Dict'
		GCActiveID = activeId
		isActiveTypeRepeat = True
	
def GoldChestEnd(*param):
	'''
	黄金宝箱活动关闭
	'''
	_, circularType = param
	if circularType != CircularDefine.CA_GoldChest:
		return
	global __IS_START
	if __IS_START is False:
		print "GE_EXC, GoldChest has already been ended"
		return
	__IS_START = False	
	
	global GCActiveID
	if not GCActiveID:
		print 'GE_EXC, SeaActiveID is already zero'
	GCActiveID = 0

def ChangeCirActID(param1, param2):
	#改变活动ID
	circularType, circularId = param2
	
	if circularType != CircularDefine.CA_GoldChest:
		return
	
	global GCActiveID
	GCActiveID = circularId
#===================================================================================		

def RequestOpenChest(role, msg):
	if __IS_START is False:
		return
	chestId = msg
	if not 0 < chestId <= 25:
		return
	#等级不够
	if role.GetLevel() < EnumGameConfig.GoldChestNeedLevel:
		return
	#获取玩家已经打开黄金宝箱的次数
	GoldChestCnt = role.GetDI8(EnumDayInt8.GoldChestCnt)
	if not GoldChestCnt < 25:
		return
	#获取玩家已经打开过哪些宝箱
	goldopendict = role.GetObj(EnumObj.GoldChestOpen)
	if chestId in goldopendict:
		
		return
	#本次打开黄金宝箱的次数的区间
	cntlevel = __GetCntLevel(GoldChestCnt + 1)
	if cntlevel == None:
		return
	cfg = GoldChestConfig.GoldChestConfigDict.get((GCActiveID, cntlevel))
	if not cfg:
		print 'GE_EXC, error in cfg = GoldChestConfig.GoldChestConfigDict.get((GCActiveID, cntlevel)), no such (GCActiveID, cntlevel)(%s,%s)' % (GCActiveID, cntlevel)
		return
	cost = GoldChestConfig.GoldChestCostDict.get(GoldChestCnt + 1)
	if not cost:
		print 'GE_EXC, cannot get cost GoldChestConfig.GoldChestCostDict.get(GoldChestCnt + 1),key = (%s)' % (GoldChestCnt + 1)
		return
	#如果玩家的黄金钥匙不足的话返回
	if role.ItemCnt(GoldKeyCode) < cost:
		return
	index = __GetRandomOne(role, cntlevel, cfg)
	#获取随机奖励失败了
	if index == None:
		return
	item = GoldChestConfig.ItemConfigDict.get(index)
	if not item:
		print "GE_EXC, error while item = GoldChestConfig.ItemConfigDict.get(index), no such index(%s)" % index
		return

	with Tra_GoldChest_Reward:
		#扣除道具
		if role.DelItem(GoldKeyCode, cost) < cost:
			return
		#增加次数
		role.IncDI8(EnumDayInt8.GoldChestCnt, 1)
		goldopendict[chestId] = item
		#如果物品的数量大于0的话就发放奖励物品
		if item[1]:
			role.AddItem(*item)
	role.SendObj(Sync_GoldChest_ChestData, role.GetObj(EnumObj.GoldChestOpen))
	if item:
		role.Msg(2, 0, GlobalPrompt.Reward_Tips + GlobalPrompt.Item_Tips % item)

def __GetCntLevel(cnt):
	'''
	获取当前的次数区间
	@param cnt:打开宝箱的次数
	'''
	CntLevelList = GoldChestConfig.CntLevelDict.get(GCActiveID)
	if CntLevelList == None:
		print "GE_EXC, error while CntLevelList = GoldChestConfig.CntLevelDict.get(GCActiveID),no such ActiveID(%s)" % GCActiveID
		return None
	cntlevellist_copy = list(CntLevelList)
	if not cnt in cntlevellist_copy:
		cntlevellist_copy.append(cnt)
	cntlevellist_copy.sort()
	return cntlevellist_copy.index(cnt) + 1

def __GetRandomOne(role, cntlevel, cfg):
	'''
	取出一个随机的物品index
	@param role:打开宝箱的次数
	@param cntlevel:当前打开宝箱的次数区间
	@param cfg:配置
	'''
	#首先获取玩家当日已经开启宝箱的情况
	roleSet = role.GetObj(EnumObj.GoldChest).setdefault(cntlevel, set([]))
	rdm = Random.RandomRate()
	for index, rate in cfg.rdmitems:
		if index in roleSet:
			continue
		rdm.AddRandomItem(rate, index)
	the_Index = rdm.RandomOne()
	if the_Index != None:
		roleSet.add(the_Index)
	return the_Index

def RequestOpenPanel(role, msg):
	'''
	客户端请求打开面板
	@param role:
	@param msg:
	'''
	role.SendObj(Sync_GoldChest_ChestData, role.GetObj(EnumObj.GoldChestOpen))

def DailyClear(role, param):
	'''
	每日清理
	@param role:
	@param param:
	'''
	if role.GetObj(EnumObj.GoldChest):
		role.GetObj(EnumObj.GoldChest).clear()
	if role.GetObj(EnumObj.GoldChestOpen):
		role.GetObj(EnumObj.GoldChestOpen).clear()
	role.SendObj(Sync_GoldChest_ChestData, role.GetObj(EnumObj.GoldChestOpen))

if "_HasLoad" not in dir():
	#事件
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, DailyClear)
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, GoldChestStart)
		Event.RegEvent(Event.Eve_EndCircularActive, GoldChestEnd)
		Event.RegEvent(Event.Eve_ChangeCirActID, ChangeCirActID)
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestOpenChest_GoldChest", "客户端请求打开黄金宝箱"), RequestOpenChest)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestOpenPanel_GoldChest", "客户端请求打开黄金宝箱面板"), RequestOpenPanel)
