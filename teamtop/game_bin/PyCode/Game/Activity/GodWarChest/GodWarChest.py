#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.GodWarChest.GodWarChest")
#===============================================================================
# 战神宝箱
#===============================================================================
import cRoleMgr
import cDateTime
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from Game.Role import Event
from Game.Role.Data import EnumObj
from Game.Activity import CircularDefine
from Game.Activity.GodWarChest import GodWarChestConfig


if "_HasLoad" not in dir():
	IS_START = False 	#活动开启标志
	
	LAST_REWARD_INDEX = 10	#最后一档奖励的索引
	BuyGodWarChestCost = AutoLog.AutoTransaction("BuyGodWarChestCost", "购买战神宝箱消耗")
	GetGodWarChestReward = AutoLog.AutoTransaction("GetGodWarChestReward", "战神宝箱领取奖励日志")
	GetGodWarChestFirstReward = AutoLog.AutoTransaction("GetGodWarChestFirstReward", "战神宝箱首次奖励日志")
	
def CloseGodWarChest(*param):
	#关闭战神宝箱
	_, circularType = param
	if circularType != CircularDefine.CA_GodWarChest:
		return
	
	global IS_START
	if not IS_START:
		print "GE_EXC, GodWarChest is already close"
		return
	
	IS_START = False
	
def StartGodWarChest(*param):
	'''
	开启战神宝箱
	'''
	_, circularType = param
	if circularType != CircularDefine.CA_GodWarChest:
		return
	
	global IS_START
	if IS_START is True:
		print "GE_EXC, GodWarChest is already start"
		return
	
	IS_START = True
#=============================消息处理=============================
def RequestBuyChest(role, param):
	'''
	购买战神宝箱
	@param role:
	@param param:
	'''
	global IS_START
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.GODWAR_CHEST_NEED_LEVEL:
		return
	
	index = param
	cfg = GodWarChestConfig.GOLD_WAR_CHEST_DICT.get(index)
	if not cfg:
		print "GE_EXC,can not find index(%s) in GodWarChestConfig.GOLD_WAR_CHEST_DICT" % index
		return
	
	if role.GetDayBuyUnbindRMB_Q() < cfg.needFillRMB:
		return
	
	if role.GetUnbindRMB_Q() < cfg.needRMB:
		return
	
	#{1:[index(0未购买,1-3为购买的档次),购买的时间],2:set(已领取的红包奖励)}
	GodWarChestData = role.GetObj(EnumObj.GodWarChestData)
	if GodWarChestData.get(1):#有购买信息
		return
	
	with BuyGodWarChestCost:
		role.DecUnbindRMB_Q(cfg.needRMB)
		GodWarChestData[1] = [index, cDateTime.Days()]
		role.SendObj(Sync_GodWarChest_Data, [GodWarChestData.get(1), GodWarChestData.get(2)])
		
	extendreward = getattr(cfg, 'extendreward')
	if not extendreward:
		print "GE_EXC,index(%s) in GodWarChestConfig.GOLD_WAR_CHEST_DICT has no extendreward" % index
		return
	
	#需要根据玩家的等级去取对应的奖励
	minlevel = GetCloseValue(role.GetLevel(), GodWarChestConfig.CHEST_MIN_LEVEL_LIST)
	if not minlevel:return
	
	rewardcfg = GodWarChestConfig.CHEST_REWARD_DICT.get((extendreward, minlevel))
	if not rewardcfg:
		print "GE_EXC,can not find index(%s) and minlevel(%s) in GodWarChestConfig.CHEST_REWARD_DICT" % (extendreward, minlevel)
		return
	with GetGodWarChestFirstReward:
		tips = GlobalPrompt.GroupBuyParty_Tips_Head
		if rewardcfg.Itemrewards:
			for item in rewardcfg.Itemrewards:
				coding, cnt = item[0], item[1]
				role.AddItem(coding, cnt)
				tips += GlobalPrompt.Item_Tips % (coding, cnt)
		if rewardcfg.bindRMB:
			role.IncBindRMB(rewardcfg.bindRMB)
			tips += GlobalPrompt.BindRMB_Tips % rewardcfg.bindRMB
		role.Msg(2, 0, tips)
		
def RequestGetChestReward(role, param):
	'''
	客户端请求领取宝箱奖励
	@param role:
	@param param:
	'''
	rewardindex = param
	if not rewardindex or rewardindex < 0:
		return
	GodWarChestData = role.GetObj(EnumObj.GodWarChestData)
	
	#检测是否已领取
	getedData = GodWarChestData.get(2, set())
	if rewardindex in getedData:
		return
	
	#获取玩家的档次,购买天数
	chestData = GodWarChestData.get(1, [])
	if not chestData:
		return
	if len(chestData) != 2:#数据不对
		chestData = []	#清除
		print "GE_EXC,data is Wrong in GodWarChest! roleId(%s)" % role.GetRoleID()
		return
	index, buyTime = chestData
	
	Chestcfg = GodWarChestConfig.GOLD_WAR_CHEST_DICT.get(index)
	if not Chestcfg:
		print "GE_EXC,can not find index(%s) in GodWarChestConfig.GOLD_WAR_CHEST_DICT" % index
		return
	
	NowDays = cDateTime.Days()		#当前的天数
	DiffDays = NowDays - buyTime	#距离购买那天过了多少天
	if DiffDays < 0:
		print "GE_EXC,In RequestGetChestReward,roleId(%s) and DiffDays(%s) is Wrong" % (role.GetRoleID(), DiffDays)
		return
	
	if not hasattr(Chestcfg, 'needDay%s' % rewardindex):
		return
	needDay = getattr(Chestcfg, 'needDay%s' % rewardindex)
	if DiffDays != needDay:#天数没达标
		return
	
	#获取对应的奖励ID
	rewardId = getattr(Chestcfg, 'dayreward%s' % rewardindex)
	if not rewardId:
		print "GE_EXC,can not find dayreward %s in RequestGetChestReward" % rewardindex
		return
	
	#需要根据玩家的等级去取对应的奖励
	minlevel = GetCloseValue(role.GetLevel(), GodWarChestConfig.CHEST_MIN_LEVEL_LIST)
	if not minlevel:return
	
	cfg = GodWarChestConfig.CHEST_REWARD_DICT.get((rewardId, minlevel))
	if not cfg:
		print "GE_EXC,can not find index(%s) and minlevel(%s) in GodWarChestConfig.CHEST_REWARD_DICT" % (rewardId, minlevel)
		return
	#加入已领取列表
	GodWarChestData[2].add(rewardindex)
	#给奖励
	GetReward(role, cfg)
	#检测是否已全部领取完，是的话要清理数据
	CheckGetAllReward(role)
	
def GetReward(role, cfg):
	with GetGodWarChestReward:
		tips = GlobalPrompt.Reward_Tips
		if cfg.Itemrewards:
			for item in cfg.Itemrewards:
				coding, cnt = item
				role.AddItem(coding, cnt)
				tips += GlobalPrompt.Item_Tips % (coding, cnt)
		if cfg.bindRMB:
			role.IncBindRMB(cfg.bindRMB)
			tips += GlobalPrompt.BindRMB_Tips % cfg.bindRMB
		#通知客户端
		GodWarChestData = role.GetObj(EnumObj.GodWarChestData)
		role.SendObj(Sync_GodWarChest_Data, [GodWarChestData.get(1), GodWarChestData.get(2)])
		
		role.Msg(2, 0, tips)
		
def CheckGetAllReward(role):
	'''
	假如全部领取完就清理所有数据
	@param role:
	'''
	GodWarChestData = role.GetObj(EnumObj.GodWarChestData)
	getedData = GodWarChestData.get(2, set())
	if LAST_REWARD_INDEX in getedData:#奖励全领取完了
		GodWarChestData[1] = []
		GodWarChestData[2] = set()
		#同步客户端
		role.SendObj(Sync_GodWarChest_Data, [GodWarChestData.get(1), GodWarChestData.get(2)])
		
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
		return tmp_level
#===================玩家事件==========================
def RoleDayClear(role, param):
	#这里主要处理玩家在线跨天
	GodWarChestData = role.GetObj(EnumObj.GodWarChestData)
	chestData = GodWarChestData.get(1)
	if chestData:#有购买战神宝箱
		_, buytime = chestData
		NowDays = cDateTime.Days()
		if NowDays - buytime >= 10:#购买已经过10天了，清除购买和领取信息
			GodWarChestData[1] = []
			GodWarChestData[2] = set()
			role.SendObj(Sync_GodWarChest_Data, [GodWarChestData.get(1), GodWarChestData.get(2)])
			
def AfterLogin(role, param):
	GodWarChestData = role.GetObj(EnumObj.GodWarChestData)
	if 1 not in GodWarChestData:#记录购买时的档次和时间
		GodWarChestData[1] = []
	if 2 not in GodWarChestData:
		GodWarChestData[2] = set()
		
	chestData = GodWarChestData.get(1)
	if chestData:#有购买战神宝箱
		_, buytime = chestData
		NowDays = cDateTime.Days()
		if NowDays - buytime >= 10:#购买已经过10天了，清除购买和领取信息
			GodWarChestData[1] = []
			GodWarChestData[2] = set()
			role.SendObj(Sync_GodWarChest_Data, [GodWarChestData.get(1), GodWarChestData.get(2)])
			
def SyncRoleOtherData(role, param):
	GodWarChestData = role.GetObj(EnumObj.GodWarChestData)
	role.SendObj(Sync_GodWarChest_Data, [GodWarChestData.get(1), GodWarChestData.get(2)])
	
if "_HasLoad" not in dir():
		Event.RegEvent(Event.Eve_StartCircularActive, StartGodWarChest)
		Event.RegEvent(Event.Eve_EndCircularActive, CloseGodWarChest)
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		
		Sync_GodWarChest_Data = AutoMessage.AllotMessage("Sync_GodWarChest_Data", "同步战神宝箱数据")
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Request_Buy_GodWarChest", "客户端请求购买战神宝箱"), RequestBuyChest)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Request_Get_GodWarChest", "客户端请求领取战神宝箱"), RequestGetChestReward)
		