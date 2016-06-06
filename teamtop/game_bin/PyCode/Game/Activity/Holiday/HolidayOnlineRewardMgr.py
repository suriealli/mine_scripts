#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.Holiday.HolidayOnlineRewardMgr")
#===============================================================================
# 元旦在线奖励Mgr
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Activity import CircularDefine
from Game.Role.Data import EnumInt16, EnumDayInt8
from Game.Activity.Holiday import HolidayOnlineRewardConfig

ONE_MINUTE_SECONDS = 60

if "_HasLoad" not in dir():
	IS_START = False
	
	Tra_HolidayOnlineReward_GetReward = AutoLog.AutoTransaction("Tra_HolidayOnlineReward_GetReward", "元旦在线奖励_领取奖励")
	
#### 活动控制  start ####
def OnStartHolidayOnline(*param):
	'''
	开启活动
	'''
	_, circularType = param
	if CircularDefine.CA_HolidayOnlineReward != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open HolidayOnline"
		return
		
	IS_START = True
	#给所有在线满足条件的玩家注册TICK
	for tmpRole in cRoleMgr.GetAllRole():
		if tmpRole.GetLevel() < EnumGameConfig.HolidayOnlineReward_NeedLevel:
			continue
		tmpRole.RegTick(ONE_MINUTE_SECONDS, UpdateOnlineMinutes)

def OnEndHolidayOnline(*param):
	'''
	结束活动
	'''
	_, circularType = param
	if CircularDefine.CA_HolidayOnlineReward != circularType:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC, end HolidayOnline while not start"
		return
		
	IS_START = False

#### 请求start ####
def OnGetReward(role, msg):
	'''
	元旦在线奖励_领奖
	@param msg: rewardIndex
	'''
	if not IS_START:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.HolidayOnlineReward_NeedLevel:
		return
	
	#参数检测
	rewardIndex = msg
	rewardCfg = HolidayOnlineRewardConfig.Holiday_OnlineReward_Config_Dict.get(rewardIndex)
	if not rewardCfg:
		return
	
	#在线时间不够
	onlineMin = role.GetI16(EnumInt16.HolidayOnLineMinutes)
	if onlineMin < rewardCfg.needOnlineMin:
		return
	
	#已领取
	rewardRecord = role.GetDI8(EnumDayInt8.HolidayOnlineRewardRecord)
	if rewardIndex & rewardRecord:
		return
	
	#process
	rewardPrompt = GlobalPrompt.HolidayOnlineReward_Tips_Head
	with Tra_HolidayOnlineReward_GetReward:
		#更新领取记录
		role.IncDI8(EnumDayInt8.HolidayOnlineRewardRecord, rewardIndex)
		#普通奖励获得
		for coding, cnt in rewardCfg.nomalReward:
			role.AddItem(coding, cnt)
			rewardPrompt += GlobalPrompt.HolidayOnlineReward_Tips_Item % (coding, cnt)
		
		#获得祈福次数
		prayTime = rewardCfg.prayTime
		if prayTime > 0:
			role.IncDI8(EnumDayInt8.HolidayWishCnt, prayTime)
			rewardPrompt += GlobalPrompt.HolidayOnlineReward_Tips_prayTimes % rewardCfg.prayTime
		
		#VIP奖励
		if role.GetVIP() >= rewardCfg.VIPLevel:
			for coding, cnt in rewardCfg.VIPReward:
				role.AddItem(coding, cnt)
				rewardPrompt += GlobalPrompt.HolidayOnlineReward_Tips_Item % (coding, cnt)
			#金币
			rewardMoney = rewardCfg.rewardMoney
			if rewardMoney > 0:
				role.IncMoney(rewardMoney)
				rewardPrompt += GlobalPrompt.HolidayOnlineReward_Tips_Money % rewardMoney
	
	role.Msg(2, 0, rewardPrompt)
		
#### 事件 start ####
def UpdateOnlineMinutes(role, calargv, regparam):
	'''
	每分钟更新在线分钟数
	'''
	if not IS_START:
		return
	
	if role.IsKick():
		return
	
	if role.GetLevel() < EnumGameConfig.HolidayOnlineReward_NeedLevel: 
		return
	
	#增加在线一分钟
	role.IncI16(EnumInt16.HolidayOnLineMinutes, 1)
	#接着注册到下一分钟
	role.RegTick(ONE_MINUTE_SECONDS, UpdateOnlineMinutes)	
	
def OnRoleLogin(role, param):
	'''
	登陆注册tick
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.HolidayOnlineReward_NeedLevel:
		return
	
	role.RegTick(ONE_MINUTE_SECONDS, UpdateOnlineMinutes)

def OnRoleLevelUp(role, param):
	'''
	玩家升级 检测是否达到等级 并注册TICK
	'''
	if not IS_START:
		return
	
	#此次升级不是 解锁等级限制
	if role.GetLevel() != EnumGameConfig.HolidayOnlineReward_NeedLevel:
		return 
	
	role.RegTick(ONE_MINUTE_SECONDS, UpdateOnlineMinutes)	

def OnRoleDayClear(role, param = None):
	'''
	元旦在线奖励_每日重置
	'''
	#重置在线分钟
	role.SetI16(EnumInt16.HolidayOnLineMinutes, 0)

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
		
	if Environment.HasLogic and not Environment.IsCross:
		#监听事件
		Event.RegEvent(Event.Eve_AfterLogin, OnRoleLogin)
		Event.RegEvent(Event.Eve_AfterLevelUp, OnRoleLevelUp)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndHolidayOnline)	
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartHolidayOnline)
		#监听消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("HolidayOnlineReward_OnGetReward", "元旦在线奖励_领奖"), OnGetReward)
