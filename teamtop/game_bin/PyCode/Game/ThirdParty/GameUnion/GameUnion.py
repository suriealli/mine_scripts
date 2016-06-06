#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.GameUnion.GameUnion")
#===============================================================================
# 游戏联盟
#===============================================================================
import cRoleMgr
import Environment
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from Game.Role.Data import EnumTempInt64, EnumDayInt1, EnumInt8, EnumInt1, EnumObj
from Game.Role import Event
from Game.ThirdParty.GameUnion import GameUnionConfig


if "_HasLoad" not in dir():
	#消息
	Sync_AIWAN_rewarddata = AutoMessage.AllotMessage("Sync_AIWAN_rewarddata", "同步玩家爱玩奖励数据 ")
	Sync_QQGJ_rewarddata = AutoMessage.AllotMessage("Sync_QQGJ_rewarddata", "同步玩家QQ管家奖励数据 ")
	#日志
	Tra_GameUnionAiwanContiLog = AutoLog.AutoTransaction("Tra_GameUnionAiwanContiLog", "游戏联盟爱玩连续登录奖励")
	Tra_GameUnionQQGJContiLog = AutoLog.AutoTransaction("Tra_GameUnionQQGJContiLog", "游戏QQ管家连续登录奖励 ")
	Tra_GameUnionAiwanLog = AutoLog.AutoTransaction("Tra_GameUnionAiwanLog", "游戏联盟爱玩登录奖励")
	Tra_GameUnionQQGJLog = AutoLog.AutoTransaction("Tra_GameUnionQQGJLog", "游戏QQ管家登录奖励 ")

def ReqGetContiLogAward_Aiwan(role, msg):
	'''
	请求获取游戏联盟爱玩连续登录奖励
	@param role:
	@param msg:
	'''
	day = msg
	if not role.GetTI64(EnumTempInt64.IsGameUnionAiWan):
		return
	rewarddict = role.GetObj(EnumObj.GameUnionAiwanContiReward)
	#该日已经领取过了
	if day in rewarddict:
		return
	cfg = GameUnionConfig.GameUnionAiwanDict.get(day)
	if not cfg:
		print "GE_EXC, cfg = GameUnionConfig.GameUnionAiwanDict.get(role.GetI8(EnumInt8.GameUnionAiwan)), not cfg"
		return
	msg = GlobalPrompt.GameUnionAward_tips
	with Tra_GameUnionAiwanContiLog:
		rewarddict[day] = 1
		if cfg.bindRMB:
			role.IncBindRMB(cfg.bindRMB)
			msg = msg + GlobalPrompt.BindRMB_Tips % cfg.bindRMB
		if cfg.rewardItemList:
			for item in cfg.rewardItemList:
				role.AddItem(*item)
				msg = msg + GlobalPrompt.Item_Tips % item
	role.SendObj(Sync_AIWAN_rewarddata, rewarddict)
	role.Msg(2, 0, msg)

def ReqGetContiLogAward_QQGJ(role, msg):
	'''
	请求获取游戏联盟QQ管家连续登录奖励
	@param role:
	@param msg:
	'''
	day = msg
	if not role.GetTI64(EnumTempInt64.IsGameUnionQQGJ):
		return
	#当日已经领取过了
	rewarddict = role.GetObj(EnumObj.GameUnionQQGJContiReward)
	if day in rewarddict:
		return
	cfg = GameUnionConfig.GameUnionQQGJDict.get(day)
	if not cfg:
		print "GE_EXC, cfg = GameUnionConfig.GameUnionQQGJDict.get(role.GetI8(EnumInt8.GameUnionQQGJ)), not cfg"
		return
	msg = GlobalPrompt.GameUnionAward_tips
	with Tra_GameUnionQQGJContiLog:
		rewarddict[day] = 1
		if cfg.bindRMB:
			role.IncBindRMB(cfg.bindRMB)
			msg = msg + GlobalPrompt.BindRMB_Tips % cfg.bindRMB
		if cfg.rewardItemList:
			for item in cfg.rewardItemList:
				role.AddItem(*item)
				msg = msg + GlobalPrompt.Item_Tips % item
	role.SendObj(Sync_QQGJ_rewarddata, rewarddict)
	role.Msg(2, 0, msg)

def ReqGetLogAward_Aiwan(role, msg):
	'''
	请求获取游戏联盟爱玩登录奖励
	@param role:
	@param msg:
	'''
	#不是从游戏联盟爱玩登录的
	if not role.GetTI64(EnumTempInt64.IsGameUnionAiWan):
		return
	#当日已经领取过了
	if role.GetDI1(EnumDayInt1.GameUnionAiwanLogAward):
		return
	level = role.GetLevel()
	cfg = GameUnionConfig.GameUnionAiwanLogDict.get(level)
	if not cfg:
		print "GE_EXC, GameUnionConfig.GameUnionAiwanLogDict.get(level), not cfg"
		return
	msg = GlobalPrompt.GameUnionAward_tips
	with Tra_GameUnionAiwanLog:
		role.SetDI1(EnumDayInt1.GameUnionAiwanLogAward, 1)
		if cfg.bindRMB:
			role.IncBindRMB(cfg.bindRMB)
			msg = msg + GlobalPrompt.BindRMB_Tips % cfg.bindRMB
		if cfg.rewardItemList:
			for item in cfg.rewardItemList:
				role.AddItem(*item)
				msg = msg + GlobalPrompt.Item_Tips % item
	role.Msg(2, 0, msg)

def ReqGetLogAward_QQGJ(role, msg):
	'''
	请求获取游戏联盟QQ管家登录奖励
	@param role:
	@param msg:
	'''
	#不是从游戏联盟QQ管家登录的
	if not role.GetTI64(EnumTempInt64.IsGameUnionQQGJ):
		return
	#当日已经领取过了
	if role.GetDI1(EnumDayInt1.GameUnionQQGJLogAward):
		return
	level = role.GetLevel()
	cfg = GameUnionConfig.GameUnionQQGJLogDict.get(level)
	if not cfg:
		print "GE_EXC, GameUnionConfig.GameUnionQQGJLogDict.get(level), not cfg"
		return
	msg = GlobalPrompt.GameUnionAward_tips
	with Tra_GameUnionQQGJLog:
		role.SetDI1(EnumDayInt1.GameUnionQQGJLogAward, 1)
		if cfg.bindRMB:
			role.IncBindRMB(cfg.bindRMB)
			msg = msg + GlobalPrompt.BindRMB_Tips % cfg.bindRMB
		if cfg.rewardItemList:
			for item in cfg.rewardItemList:
				role.AddItem(*item)
				msg = msg + GlobalPrompt.Item_Tips % item
	role.Msg(2, 0, msg)

def ReqGetLogBuff_Aiwan(role, msg):
	'''
	请求领取游戏联盟爱玩登录buff
	@param role:
	@param 
	'''
	#不是从游戏联盟爱玩登录的
	if not role.GetTI64(EnumTempInt64.IsGameUnionAiWan):
		return
	#如果已经领取过
	if role.GetI1(EnumInt1.GameUnionBuff_Aiwan):
		return
	role.SetI1(EnumInt1.GameUnionBuff_Aiwan, 1)
	#重算属性
	role.GetPropertyGather().ReSetRecountGameUnionLogBuffFlag()

def ReqGetLogBuff_QQGJ(role, msg):
	'''
	请求领取游戏联盟QQ管家登录buff
	@param role:
	@param 
	'''
	#不是从游戏联盟QQ管家登录的
	if not role.GetTI64(EnumTempInt64.IsGameUnionQQGJ):
		return
	#如果已经领取过
	if role.GetI1(EnumInt1.GameUnionBuff_QQGJ):
		return
	role.SetI1(EnumInt1.GameUnionBuff_QQGJ, 1)
	#重算属性
	role.GetPropertyGather().ReSetRecountGameUnionLogBuffFlag()

def OnRoleLogin(role, param):
	'''
	同步其他数据
	@param role:
	@param param:
	'''
	#从爱玩平台登录 
	if role.GetTI64(EnumTempInt64.IsGameUnionAiWan):
		rewarddict = role.GetObj(EnumObj.GameUnionAiwanContiReward)
		if role.GetDI1(EnumDayInt1.GameUnionAiwanLog):
			role.SendObj(Sync_AIWAN_rewarddata, rewarddict)
			return

		#如果一轮循环的奖励没有领取完则不会进入下一轮循环
		if role.GetI8(EnumInt8.GameUnionAiwan) == 7:
			if len(rewarddict) != 7:
				role.SendObj(Sync_AIWAN_rewarddata, rewarddict)
				return
			else:
				rewarddict.clear()
		#增加登录天数
		role.SetDI1(EnumDayInt1.GameUnionAiwanLog, 1)
		role.IncI8(EnumInt8.GameUnionAiwan, 1)
		#不能大于7
		if role.GetI8(EnumInt8.GameUnionAiwan) > 7:
			role.SetI8(EnumInt8.GameUnionAiwan, role.GetI8(EnumInt8.GameUnionAiwan) % 7)
		role.SendObj(Sync_AIWAN_rewarddata, rewarddict)

	#从QQ管家平台登录
	if role.GetTI64(EnumTempInt64.IsGameUnionQQGJ):
		#如果领取过平台buff，则重算属性
		rewarddict = role.GetObj(EnumObj.GameUnionQQGJContiReward)
		if role.GetDI1(EnumDayInt1.GameUnionQQGJLog):
			role.SendObj(Sync_QQGJ_rewarddata, rewarddict)
			return
		#如果一轮循环的奖励没有领取完则不会进入下一轮循环
		if role.GetI8(EnumInt8.GameUnionQQGJ) == 7:
			if len(rewarddict) != 7:
				role.SendObj(Sync_QQGJ_rewarddata, rewarddict)
				return
			else:
				rewarddict.clear()
		#增加登录次数:
		role.SetDI1(EnumDayInt1.GameUnionQQGJLog, 1)
		role.IncI8(EnumInt8.GameUnionQQGJ, 1)
		#不能大于7
		if role.GetI8(EnumInt8.GameUnionQQGJ) > 7:
			role.SetI8(EnumInt8.GameUnionQQGJ, role.GetI8(EnumInt8.GameUnionQQGJ) % 7)
		role.SendObj(Sync_QQGJ_rewarddata, rewarddict)


if "_HasLoad" not in dir():
	if Environment.EnvIsQQ() and (not Environment.IsCross):
		#角色登陆同步其它剩余数据
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnRoleLogin)
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleLogin)
	if Environment.HasLogic and not Environment.IsCross:
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ReqGetContiLogAward_Aiwan", "请求获取游戏联盟爱玩连续登录奖励"), ReqGetContiLogAward_Aiwan)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ReqGetContiLogAward_QQGJ", "请求获取游戏联盟QQ管家连续登录奖励"), ReqGetContiLogAward_QQGJ)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ReqGetLogAward_Aiwan", "请求获取游戏联盟爱玩登录奖励"), ReqGetLogAward_Aiwan) 
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ReqGetLogAward_QQGJ", "请求获取游戏联盟QQ管家登录奖励"), ReqGetLogAward_QQGJ)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ReqGetLogBuff_Aiwan", "请求获取游戏联盟爱玩登录buff"), ReqGetLogBuff_Aiwan)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ReqGetLogBuff_QQGJ", "请求获取游戏联盟QQ管家登录buff"), ReqGetLogBuff_QQGJ)
