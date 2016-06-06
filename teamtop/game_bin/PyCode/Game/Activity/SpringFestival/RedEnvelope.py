#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.SpringFestival.RedEnvelope")
#===============================================================================
# 春节红包
#===============================================================================
import Environment
import cRoleMgr
import cDateTime
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Role.Data import EnumObj
from Game.Role import Event
from Game.Activity.SpringFestival import SpringFestivalConfig

if "_HasLoad" not in dir():
	#日志
	SpringFestivalRedCost = AutoLog.AutoTransaction("SpringFestivalRedCost", "购买红包消耗")
	SpringFestivaGetReward = AutoLog.AutoTransaction("SpringFestivaGetReward", "领取红包奖励")
	SpringFestivaGetCoding = AutoLog.AutoTransaction("SpringFestivaGetCoding", "领取红包道具奖励")
	
def CheckActive():
	#检测活动是否开启
	cfg = SpringFestivalConfig.RED_ENVELOPE_TIME
	now = cDateTime.Now()
	start = cfg.StartTime#指定开启时间
	end = cfg.EndTime#指定结束时间
	if start <= now <= end:
		return 1
	return 0

def RequestBuyRedEnvelope(role, param):
	'''
	客户端请求购买红包
	@param role:
	@param param:
	'''
	index = param
	
	if not CheckActive():
		return
	
	if role.GetLevel() < EnumGameConfig.Spring_Festival_NeedLevel:
		return
	
	cfg = SpringFestivalConfig.RED_ENVELOPE_DICT.get(index)
	if not cfg:
		print "GE_EXC,can not find index(%s) in RequestBuyRedEnvelope" % index
		return
	
	if not cfg.needUnbindRMB_Q: return
	
	if role.GetUnbindRMB_Q() < cfg.needUnbindRMB_Q:
		return
	
	SpringFestivalData = role.GetObj(EnumObj.SpringFestivalData)
	redData = SpringFestivalData.get(1, [])
	if redData:
		#已购买了
		return
	
	with SpringFestivalRedCost:
		role.DecUnbindRMB_Q(cfg.needUnbindRMB_Q)
		#设置购买的红包
		SpringFestivalData[1] = [index, cDateTime.Days()]
		#同步数据
		role.SendObj(Sync_RedEnvelope_Data, [SpringFestivalData.get(1), SpringFestivalData.get(2), SpringFestivalData.get(7)])
		
def RequestGetRedEnvelopeReward(role, param):
	'''
	客户端请求领取红包奖励
	@param role:
	@param param:
	'''
	index = param#(1 -- 7)
	SpringFestivalData = role.GetObj(EnumObj.SpringFestivalData)
	REData = SpringFestivalData.get(1, [])
	if not REData:#未购买红包
		return
	
	GetedData = SpringFestivalData.get(2, set())
	if index in GetedData:#已领取
		return
	
	REindex ,buyTime = REData
	
	cfg = SpringFestivalConfig.RED_ENVELOPE_DICT.get(REindex)
	if not cfg:
		print "GE_EXC,can not find index(%s) in SpringFestivalConfig.RED_ENVELOPE_DICT" % REindex
		return
	
	NowDays = cDateTime.Days()
	DiffDays = NowDays - buyTime
	if DiffDays < 0:
		print "GE_EXC,In RedEnvelope,roleId(%s) and DiffDays(%s) is Wrong" % (role.GetRoleID(), DiffDays)
		return
	
	if not hasattr(cfg, 'needDay%s' % index):
		return
		
	needDay = getattr(cfg, 'needDay%s' % index)
	if DiffDays < needDay:#天数没达标
		return
	
	strday = 'day%s' % min(needDay + 1, 7)
	if not hasattr(cfg, strday):
		return
	
	with SpringFestivaGetReward:
		SpringFestivalData[2].add(index)
		
		rewardRMB = getattr(cfg, strday)
		if not rewardRMB:
			print "GE_EXC,In RedEnvelope rewardRMB is None,roleId(%s) and index(%s)" % (role.GetRoleID(), index)
			return
		tips = GlobalPrompt.Reward_Tips
		role.IncUnbindRMB_S(rewardRMB)
		tips += GlobalPrompt.UnBindRMB_Tips % rewardRMB
		role.Msg(2, 0, tips)
		#同步数据
		role.SendObj(Sync_RedEnvelope_Data, [SpringFestivalData.get(1), SpringFestivalData.get(2), SpringFestivalData.get(7)])
		
def RequestGetCodingReward(role, param):
	'''
	客户端请求领取购买红包道具奖励
	@param role:
	@param param:
	'''
	SpringFestivalData = role.GetObj(EnumObj.SpringFestivalData)
	REData = SpringFestivalData.get(1, [])
	if not REData:#未购买红包
		return
	
	if SpringFestivalData.get(7):#已领取过了
		return
	
	level = role.GetLevel()
	cfg = SpringFestivalConfig.RED_ENVELOPE_REWARD_DICT.get(level)
	if not cfg:
		print "GE_EXC,can not find level(%s) in SpringFestivalConfig.RED_ENVELOPE_REWARD_DICT" % level
		return
	if not cfg.reward1 or not cfg.reward2 or not cfg.reward3:
		return
	
	with SpringFestivaGetCoding:
		SpringFestivalData[7] = 1
		
		#获取玩家买的红包档次
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
		
		role.SendObj(Sync_RedEnvelope_Data, [SpringFestivalData.get(1), SpringFestivalData.get(2), SpringFestivalData.get(7)])

def AfterLogin(role, param):
	#玩家登录
	SpringFestivalData = role.GetObj(EnumObj.SpringFestivalData)
	if 1 not in SpringFestivalData:#记录玩家购红包时的档次和时间
		SpringFestivalData[1] = []
	if 2 not in SpringFestivalData:#记录玩家已领取的红包奖励
		SpringFestivalData[2] = set()
	if 3 not in SpringFestivalData:#记录已领取的天降财神奖励
		SpringFestivalData[3] = set()
	if 4 not in SpringFestivalData:#记录天降财神领取次数
		SpringFestivalData[4] = 0
	if 5 not in SpringFestivalData:#记录年兽来了已领取的奖励ID
		SpringFestivalData[5] = set()
	if 6 not in SpringFestivalData:#折扣汇
		SpringFestivalData[6] = {}
	if 7 not in SpringFestivalData:#购买红包是给的道具奖励
		SpringFestivalData[7] = 0
	if 8 not in SpringFestivalData:#时装秀兑换记录
		SpringFestivalData[8] = {}
	#同步数据
	if not CheckActive():
		return
	role.SendObj(Sync_RedEnvelope_Data, [SpringFestivalData.get(1), SpringFestivalData.get(2), SpringFestivalData.get(7)])
		
def SyncRoleOtherData(role, param):
	if not CheckActive():
		return
	#同步数据
	SpringFestivalData = role.GetObj(EnumObj.SpringFestivalData)
	role.SendObj(Sync_RedEnvelope_Data, [SpringFestivalData.get(1), SpringFestivalData.get(2), SpringFestivalData.get(7)])
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		
		Sync_RedEnvelope_Data = AutoMessage.AllotMessage("Sync_RedEnvelope_Data", "同步红包数据")
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Request_Buy_RedEnvelope", "客户端请求购买红包"), RequestBuyRedEnvelope)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Request_Get_RedEnvelopeReward", "客户端请求领取红包奖励"), RequestGetRedEnvelopeReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Request_Get_RedCodingReward", "客户端请求领取购买红包道具奖励"), RequestGetCodingReward)
		