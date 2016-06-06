#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.RMBComing.RMBComing")
#===============================================================================
# 超级理财
#===============================================================================
import Environment
import cRoleMgr
import cDateTime
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from Game.Activity import CircularDefine
from Game.Role.Data import EnumObj
from Game.Role import Event
from Game.Activity.RMBComing import RMBComingConfig

if "_HasLoad" not in dir():
	IS_START = False	#开启标志
	#日志
	RMBComingCost = AutoLog.AutoTransaction("RMBComingCost", "购买超级理财消耗")
	RMBComingGetReward = AutoLog.AutoTransaction("RMBComingGetReward", "领取超级理财奖励")
	RMBComingGetCoding = AutoLog.AutoTransaction("RMBComingGetCoding", "领取超级理财道具奖励")
	
def CloseRMBComing(*param):
	#关闭超级理财
	_, circularType = param
	if circularType != CircularDefine.CA_RMBComfig:
		return
	
	global IS_START
	if not IS_START:
		print "GE_EXC, RMBComing is already close"
		return
	
	IS_START = False
	
def StartRMBComing(*param):
	'''
	开启超级理财
	'''
	_, circularType = param
	if circularType != CircularDefine.CA_RMBComfig:
		return
	
	global IS_START
	if IS_START is True:
		print "GE_EXC, RMBComing is already start"
		return
	
	IS_START = True
#================================================

def RequestBuyRMBComing(role, param):
	'''
	客户端请求购买超级理财
	@param role:
	@param param:
	'''
	global IS_START
	if not IS_START:
		return
	
	index = param
	
	cfg = RMBComingConfig.RMB_COMING_DICT.get(index)
	if not cfg:
		print "GE_EXC,can not find index(%s) in RequestBuyRMBComing" % index
		return
	
	if cfg.fillRMB > role.GetDayBuyUnbindRMB_Q():
		return
	
	if not cfg.needUnbindRMB_Q: return
	
	if role.GetUnbindRMB_Q() < cfg.needUnbindRMB_Q:
		return
	
	RMBCominglData = role.GetObj(EnumObj.RMBComingData)
	redData = RMBCominglData.get(1, [])
	if redData:
		#已购买了
		return
	
	with RMBComingCost:
		role.DecUnbindRMB_Q(cfg.needUnbindRMB_Q)
		#设置购买的超级理财
		RMBCominglData[1] = [index, cDateTime.Days()]
		#同步数据
		role.SendObj(Sync_RMBComing_Data, [RMBCominglData.get(1), RMBCominglData.get(2), RMBCominglData.get(3)])
		
def RequestGetRMBComingReward(role, param):
	'''
	客户端请求领取超级理财奖励
	@param role:
	@param param:
	'''
	index = param#(1 -- 7)
	RMBCominglData = role.GetObj(EnumObj.RMBComingData)
	REData = RMBCominglData.get(1, [])
	if not REData:#未购买超级理财
		return
	
	GetedData = RMBCominglData.get(2, set())
	if index in GetedData:#已领取
		return
	
	REindex ,buyTime = REData
	
	cfg = RMBComingConfig.RMB_COMING_DICT.get(REindex)
	if not cfg:
		print "GE_EXC,can not find index(%s) in RMBCominglConfig.RMB_COMING_DICT" % REindex
		return
	
	NowDays = cDateTime.Days()
	DiffDays = NowDays - buyTime
	if DiffDays < 0:
		print "GE_EXC,In RMBComing,roleId(%s) and DiffDays(%s) is Wrong" % (role.GetRoleID(), DiffDays)
		return
	
	if not hasattr(cfg, 'needDay%s' % index):
		return
		
	needDay = getattr(cfg, 'needDay%s' % index)
	if DiffDays < needDay:#天数没达标
		return
	
	strday = 'day%s' % min(needDay + 1, 7)
	if not hasattr(cfg, strday):
		return
	
	with RMBComingGetReward:
		RMBCominglData[2].add(index)
		
		rewardRMB = getattr(cfg, strday)
		if not rewardRMB:
			print "GE_EXC,In RMBComing rewardRMB is None,roleId(%s) and index(%s)" % (role.GetRoleID(), index)
			return
		tips = GlobalPrompt.Reward_Tips
		role.IncUnbindRMB_S(rewardRMB)
		tips += GlobalPrompt.UnBindRMB_Tips % rewardRMB
		role.Msg(2, 0, tips)
		#同步数据
		role.SendObj(Sync_RMBComing_Data, [RMBCominglData.get(1), RMBCominglData.get(2), RMBCominglData.get(3)])
	CheckReward(role)
		
def RequestGetCodingReward(role, param):
	'''
	客户端请求领取购买超级理财道具奖励
	@param role:
	@param param:
	'''
	RMBCominglData = role.GetObj(EnumObj.RMBComingData)
	REData = RMBCominglData.get(1, [])
	if not REData:#未购买超级理财
		return
	
	if RMBCominglData.get(3):#已领取过了
		return
	
	level = role.GetLevel()
	cfg = RMBComingConfig.RMB_COMING_REWARD_DICT.get(level)
	if not cfg:
		print "GE_EXC,can not find level(%s) in RMBCominglConfig.RMB_COMING_REWARD_DICT" % level
		return
	if not cfg.reward1 or not cfg.reward2 or not cfg.reward3:
		return
	
	with RMBComingGetCoding:
		RMBCominglData[3] = 1
		
		#获取玩家买的超级理财档次
		index, _ = REData
		coding, cnt = 0, 0
		if index == 1:
			coding, cnt = cfg.reward1
		elif index == 2:
			coding, cnt = cfg.reward2
		elif index == 3:
			coding, cnt = cfg.reward3
		if coding and cnt:
			tips = GlobalPrompt.Reward_Tips
			role.AddItem(coding, cnt)
			tips += GlobalPrompt.Item_Tips % (coding, cnt)
		role.Msg(2, 0, tips)
		
		role.SendObj(Sync_RMBComing_Data, [RMBCominglData.get(1), RMBCominglData.get(2), RMBCominglData.get(3)])

def CheckReward(role):
	#检测奖励是否全部领取完了
	RMBCominglData = role.GetObj(EnumObj.RMBComingData)
	getedData = RMBCominglData.get(2, set())
	if len(getedData) >= 7:#全部领取完了
		RMBCominglData[1] = []
		RMBCominglData[2] = set()
		RMBCominglData[3] = 0
		#同步客户端
		role.SendObj(Sync_RMBComing_Data, [RMBCominglData.get(1), RMBCominglData.get(2), RMBCominglData.get(3)])

def AfterLogin(role, param):
	#玩家登录
	RMBCominglData = role.GetObj(EnumObj.RMBComingData)
	if 1 not in RMBCominglData:#记录玩家购超级理财时的档次和时间
		RMBCominglData[1] = []
	if 2 not in RMBCominglData:#记录玩家已领取的超级理财奖励
		RMBCominglData[2] = set()
	if 3 not in RMBCominglData:
		RMBCominglData[3] = 0
	CheckReward(role)
	
def SyncRoleOtherData(role, param):
	#同步数据
	RMBCominglData = role.GetObj(EnumObj.RMBComingData)
	role.SendObj(Sync_RMBComing_Data, [RMBCominglData.get(1), RMBCominglData.get(2), RMBCominglData.get(3)])
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		
		Event.RegEvent(Event.Eve_StartCircularActive, StartRMBComing)
		Event.RegEvent(Event.Eve_EndCircularActive, CloseRMBComing)
		
		Sync_RMBComing_Data = AutoMessage.AllotMessage("Sync_RMBComing_Data", "同步超级理财数据")
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Request_Buy_RMBComing", "客户端请求购买超级理财"), RequestBuyRMBComing)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Request_Get_RMBComingReward", "客户端请求领取超级理财奖励"), RequestGetRMBComingReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Request_Get_CodingReward", "客户端请求领取超级理财道具奖励"), RequestGetCodingReward)
		