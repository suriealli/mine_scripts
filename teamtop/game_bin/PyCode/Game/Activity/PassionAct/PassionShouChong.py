#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionShouChong")
#===============================================================================
# 每日首冲控制
#===============================================================================
import cRoleMgr
import Environment
from Game.Role import Event
from Game.Activity import CircularDefine
from Common.Other import EnumGameConfig
from Game.Role.Data import EnumInt8,EnumDayInt1
from Game.Activity.PassionAct import PassionShouChongConfig
from Common.Other import GlobalPrompt
from Game.Role.Data import EnumObj
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Activity.PassionAct import PassionDefine

if "_HasLoad" not in dir() :
	IsStart = False			#充值活动开始控制
	#日志
	ChongZhiDays = AutoLog.AutoTransaction("ChongZhiDays", "充值天数")
	ShouChong = AutoLog.AutoTransaction("ShouChong", "首冲奖励")
	ChongZhiAwards = AutoLog.AutoTransaction("ChongZhiAwards", "充值累计天数奖励")
	BuyShouChong = AutoLog.AutoTransaction("BuyShouChong", "首冲购买")
	#消息
	ChongZhiState = AutoMessage.AllotMessage("ChongZhiState", "充值天数状态")
	ShouChongState = AutoMessage.AllotMessage("ShouChongState", "首冲状态")
	BuyShouChongState = AutoMessage.AllotMessage("BuyShouChongState", "首冲购买状态")

def StartCircularActive(param1, param2):
	if param2 != CircularDefine.CA_PassionChongZhi:
		return
	global IsStart
	if IsStart:
		print 'GE_EXC, ChongZhi is already start'
	IsStart = True
	


def EndCircularActive(param1, param2):
	global IsStart
	if param2 != CircularDefine.CA_PassionChongZhi:
		return
	if not IsStart:
		print 'GE_EXC, ChongZhi is already end'
	IsStart = False
	


def GetShouChongState(role, param = None):
	'''
	获取充值状态
	'''
	global IsStart
	if not IsStart :
		return 
	if role.GetLevel() < EnumGameConfig.Level_30:
		return
	awards = role.GetObj(EnumObj.PassionActData).get(PassionDefine.PassionThanksGivingChongZhi, [])
	if not awards :
		awards = role.GetObj(EnumObj.PassionActData).setdefault(PassionDefine.PassionThanksGivingChongZhi, [])
	role.SendObj(ChongZhiState,awards)
	#首冲没有达到要求
	if role.GetDayBuyUnbindRMB_Q() < EnumGameConfig.ShouChongNumbers :
		role.SendObj(ShouChongState, 0)
		role.SendObj(BuyShouChongState, 0)
		return
	#首冲已经领取
	if role.GetDI1(EnumDayInt1.PassionShouChong) :
		role.SendObj(ShouChongState, 2)
	#首冲没有领取 
	else:
		role.SendObj(ShouChongState, 1)
	
	#已完成首冲购买
	if role.GetDI1(EnumDayInt1.BuyPassionShouChong) :
		role.SendObj(BuyShouChongState, 2)
	else:
		role.SendObj(BuyShouChongState, 1)

def ShouChongAward(role, param = None):
	'''
	领取首充奖励
	'''
	global IsStart
	if not IsStart :
		return 
	if role.GetLevel() < EnumGameConfig.Level_30:
		return
	if role.GetDI1(EnumDayInt1.PassionShouChong) :
		return
	DayBuRMB = role.GetDayBuyUnbindRMB_Q()
	if DayBuRMB < EnumGameConfig.ShouChongNumbers :
		return
	
	cfg = PassionShouChongConfig.SHOUCHONG_AWARD[0]
	items = cfg.rewardItem
	#检测背包是否足以放下奖励
	if len(items) > role.PackageEmptySize():
		role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
		return
	
	tips = GlobalPrompt.Reward_Tips
	with ShouChong :
		role.SetDI1(EnumDayInt1.PassionShouChong, 1)
		for item, cnt in items :
			role.AddItem(item, cnt)
			tips += GlobalPrompt.Item_Tips % (item, cnt)
	role.Msg(2, 0, tips)
	
	with ChongZhiDays:
		role.IncI8(EnumInt8.ChongZhiDays, 1)
	GetShouChongState(role, 1)


def BuyShouChongAward(role, param):
	'''
	购买每日首充
	@param role:
	@param param: 
	'''
	global IsStart
	if not IsStart:
		return 
	if role.GetLevel() < EnumGameConfig.Level_30:
		return
	
	if role.GetDI1(EnumDayInt1.BuyPassionShouChong):
		return
	if role.GetDayBuyUnbindRMB_Q() < EnumGameConfig.ShouChongNumbers :
		return
	
	cfg = PassionShouChongConfig.GetShouChongObj()
	if not cfg:
		print "GE_EXC, wrong configuration, please check the file ..../PassionAct/PassionShouChong.txt."
		return
	needMoney = cfg.Counts
	if needMoney > role.GetUnbindRMB_Q() :
		return
	tips = GlobalPrompt.Reward_Tips
	with BuyShouChong :
		role.SetDI1(EnumDayInt1.BuyPassionShouChong, 1)
		role.DecUnbindRMB_Q(needMoney)
		for item, cnt in cfg.rewardItem:
			role.AddItem(item, cnt)
			tips += GlobalPrompt.Item_Tips % (item, cnt)
	
	role.Msg(2, 0, tips)
	GetShouChongState(role, 1)

def ChongZhiAward(role,keys):
	'''
	领取充值天数累计奖励
	@param role:
	@param keys: 为领取奖励的索引
	'''
	global IsStart
	if not IsStart :
		return
	if role.GetLevel() < EnumGameConfig.Level_30:
		return
	awards = role.GetObj(EnumObj.PassionActData).get(PassionDefine.PassionThanksGivingChongZhi, [])
	if not awards :
		awards = role.GetObj(EnumObj.PassionActData).setdefault(PassionDefine.PassionThanksGivingChongZhi, [])
	if keys in awards:
		return
	cfg = PassionShouChongConfig.CHONGZHI_AWARD.get(keys)
	if not cfg :
		print "GE_EXC, cfg.keys(%s) in ChongZhiAward" % keys
		return
	days = role.GetI8(EnumInt8.ChongZhiDays)
	if days < cfg.ChongZhiDays :
		return
	items = cfg.rewardItem
	#检测背包是否足以放下奖励
	if len(items) > role.PackageEmptySize():
		role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
		return
	
	tips = GlobalPrompt.Reward_Tips
	#领取奖励
	with ChongZhiAwards :
		awards.append(keys)
		for item, cnt in items :
			role.AddItem(item, cnt)
			tips += GlobalPrompt.Item_Tips % (item, cnt)
	
	role.Msg(2, 0, tips)
	GetShouChongState(role, 1)


if "_HasLoad" not in dir() :
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, StartCircularActive)
		Event.RegEvent(Event.Eve_EndCircularActive, EndCircularActive)
		Event.RegEvent(Event.AfterChangeUnbindRMB_Q, GetShouChongState)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, GetShouChongState)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChongZhiAward", "充值天数累计奖励"), ChongZhiAward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ShouChongAward", "首冲奖励"), ShouChongAward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GetShouChongState", "首冲状态"), GetShouChongState)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("BuyShouChongAward", "首冲购买"), BuyShouChongAward)
