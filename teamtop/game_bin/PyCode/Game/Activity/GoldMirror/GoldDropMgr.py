#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.GoldMirror.GoldDropMgr")
#===============================================================================
# 金币掉落管理
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Activity.GoldMirror import GoldMirrorConfig
from Game.Role.Data import EnumDayInt8, EnumDayInt1
from Game.SysData import WorldData

def GetGoldDropAward(role, awardType, totalMoney, backFunId):
	#判断每日参与次数是否有异常
	if role.GetDI8(EnumDayInt8.GoldDropAwardCnt_2) > 100:
		return
	if role.GetDI8(EnumDayInt8.GoldDropAwardCnt_2) >= WorldData.GetGoldMirrorCnt_1():
		return
	
	#获取金币掉落配置
	config = GoldMirrorConfig.GOLD_DROP_LIMIT.get(role.GetLevel())
	if not config:
		return
	
	#没有未领取的金币掉落玩法奖励
	if not role.GetDI1(EnumDayInt1.IsActGoldDrop):
		return
	
	#扣除次数
	role.IncDI8(EnumDayInt8.GoldDropAwardCnt_2, 1)
	
	#判断金币上限
	awardMoney = totalMoney
	if totalMoney > config.maxMoney:
		awardMoney = config.maxMoney
		
	if awardType == 1:
		#普通领奖
		if awardMoney > 0:
			role.IncMoney(awardMoney)
	elif awardType == 2:
		#消耗魔晶
		if role.GetRMB() < config.doubleNeedRMB:
			return
		role.DecRMB(config.doubleNeedRMB)
		
		#双倍领奖
		if awardMoney > 0:
			awardMoney = awardMoney * 2
			role.IncMoney(awardMoney)
	
	role.SetDI1(EnumDayInt1.IsActGoldDrop, False)
	
	#回调客户端领取成功
	role.CallBackFunction(backFunId, None)
	role.Msg(2, 0, GlobalPrompt.WPG_Finish % awardMoney)
#===============================================================================
# 客户端请求
#===============================================================================
def RequestGetGoldDropAward(role, msg):
	'''
	客户端请求打开领取金币掉落奖励
	@param role:
	@param msg:
	'''
	backFunId, data = msg
	
	awardType, totalMoney = data
	
	#日志
	with TraGoldDropAward:
		GetGoldDropAward(role, awardType, totalMoney, backFunId)

if "_HasLoad" not in dir():
	#日志
	TraGoldDropAward = AutoLog.AutoTransaction("TraGoldDropAward", "金币掉落副本奖励")
	if Environment.HasLogic and not Environment.IsCross:
		#注册消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Gold_Drop_Get_Award", "客户端请求打开领取金币掉落奖励"), RequestGetGoldDropAward)
	
	
	