#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.RushLevel.RushLevelMgr")
#===============================================================================
# 冲级排名活动
#===============================================================================
import Environment
import cComplexServer
import cDateTime
import cRoleMgr
from Util import Time
from Common.Message import AutoMessage
from Common.Other import EnumSysData, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Activity.RushLevel import RushLevelConfig
from Game.Persistence import Contain
from Game.Role import Event, Call
from Game.Role.Data import EnumInt8
from Game.RoleView import RoleView
from Game.SysData import WorldData
from Game.SystemRank import SystemRank
import datetime

if "_HasLoad" not in dir():
	RANK_DATA_IDX = 1
	
	RUSH_LEVEL_END_TIME = 0			#冲级排名活动结束时间
	IN_RANK_NEED_LEVEL = 38			#进榜需要的等级
	REWARD_DURATION = 24 * 60		#活动奖励有效期24小时
	REWARD_DURATION_NA = 29 * 60	#活动奖励有效期29小时（北美）
	
	REWARDID_TO_ENUM = {1: EnumInt8.RushLevelTop, 2: EnumInt8.RushLevel44, 
					3: EnumInt8.RushLevel46, 4: EnumInt8.RushLevel48}
	
	#消息
	Rush_Level_Show_Panel = AutoMessage.AllotMessage("Rush_Level_Show_Panel", "通知客户端显示冲级排名面板")
	
def AfterLoad():
	pass

def GetEndTime():
	'''
	获取结束时间 
	'''
	global RUSH_LEVEL_END_TIME
	if RUSH_LEVEL_END_TIME > 0:
		return RUSH_LEVEL_END_TIME
	
	#数据库还没载回
	if not WorldData.WD.returnDB:
		return 0
	
	kafuTime = WorldData.WD.get(EnumSysData.KaiFuKey)
	
	
	#版本判断
	if Environment.EnvIsNA():
		#计算活动结束时间
		RUSH_LEVEL_END_TIME = Time.DateTime2UnitTime(kafuTime) / 60 + REWARD_DURATION_NA
	else:
		#计算活动结束时间
		RUSH_LEVEL_END_TIME = Time.DateTime2UnitTime(kafuTime) / 60 + REWARD_DURATION
	
	return RUSH_LEVEL_END_TIME

def GetReward(role, rewardId):
	'''
	领取奖励
	@param role:
	@param rewardId:
	'''
	rewardEnum = REWARDID_TO_ENUM.get(rewardId)
	if not rewardEnum:
		return
	
	#是否可以领取奖励
	if role.GetI8(rewardEnum) != 1:
		return
	
	#奖励配置
	rewardConfig = RushLevelConfig.RUSH_LEVEL_REWARD.get(rewardId)
	if not rewardConfig:
		return
	
	#设置已领取
	role.SetI8(rewardEnum, 2)
	
	#奖励
	if rewardConfig.rewardHeroNumber > 0:
		#英雄奖励
		role.AddHero(rewardConfig.rewardHeroNumber)
		
	promptStrList = [GlobalPrompt.RUSH_LEVEL_GET_REWARD_PROMPT, ]	#提示字符串列表
	for item in rewardConfig.rewardItemList:
		#物品奖励
		role.AddItem(*item)
		#加入提示字符串列表
		promptStrList.append(GlobalPrompt.Item_Tips % (item[0], item[1]))
		
	#日志事件
	AutoLog.LogBase(role.GetRoleID(), AutoLog.eveRushLevelReward, rewardId)
	
	#提示
	role.Msg(2, 0, ''.join(promptStrList))
	
def UpdateRushLevelRank():
	'''
	更新冲级排名排行榜
	'''
	#更新冲级排行榜数据
	d = SystemRank.LR.data
	#roleId，名字，等级，经验
	rankList = [(roleId, info[0], info[1], info[4]) for roleId, info in d.iteritems()]
	#先用等级排序，相同等级则用经验排序
	rankList.sort(key = lambda x:(x[2], x[3]), reverse = True)
	#保存前三名
	rankList = rankList[:3]
	#先清空排名字典
	RL.clear()
	for data in rankList:
		roleId = data[0]
		level = data[2]
		#需要达到38级才入榜
		if level < IN_RANK_NEED_LEVEL:
			break
		#获取头像数据(性别, 职业, 进阶)
		sex, career, grade = RoleView.GetOfflineHead(roleId)
		#roleId，性别，职业，进阶，名字，等级，经验
		RL.setdefault(RANK_DATA_IDX, []).append((roleId, sex, career, grade, data[1], data[2], data[3]))
	
#===============================================================================
# 显示
#===============================================================================
def ShowRushLevelPanel(role):
	if not RL:
		return
	#同步客户端
	role.SendObj(Rush_Level_Show_Panel, RL[RANK_DATA_IDX])

#===============================================================================
# 离线命令
#===============================================================================
def RushLevelReward(role, param):
	'''
	冲级排名奖励
	@param role:
	@param param:
	'''
	if role.GetI8(EnumInt8.RushLevelTop) == 0:
		#设置可以领取
		role.SetI8(EnumInt8.RushLevelTop, 1)
	
#===============================================================================
# 时间相关
#===============================================================================
def PerMinute():
	minutes = cDateTime.Minutes()
	endMinutes = GetEndTime()
	from Game.Activity.KaifuTarget import TimeControl
	if not WorldData.WD.returnDB:
		if minutes == endMinutes:
			print "not WorldData.WD.returnDB and minutes == endMinutes in PerMinute"
		return
	kaifuTime = WorldData.WD[EnumSysData.KaiFuKey]
	
	if Environment.EnvIsRU() and kaifuTime > datetime.datetime(2015,4,10,0,0,0):
		return
	if kaifuTime < TimeControl.KaifuTargetTime_New:
		return
	
	#活动已经结束
	if minutes > endMinutes:
		return
	
	#活动结束时间到
	if minutes == endMinutes:
		#强制保存一次排行榜
		SystemRank.CallPerHour()
		
		#更新冲级排行榜数据
		d = SystemRank.LR.data
		#roleId，名字，等级，经验
		rankList = [(roleId, info[0], info[1], info[4]) for roleId, info in d.iteritems()]
		#先用等级排序，相同等级则用经验排序
		rankList.sort(key = lambda x:(x[2], x[3]), reverse = True)
		#保存前三名
		rankList = rankList[:3]
		#先清空排名字典
		RL.clear()
		for data in rankList:
			roleId = data[0]
			level = data[2]
			#需要达到38级才入榜
			if level < IN_RANK_NEED_LEVEL:
				break
			#获取头像数据(性别, 职业, 进阶)
			head = RoleView.GetOfflineHead(roleId)
			sex, career, grade = head
			#roleId，性别，职业，进阶，名字，等级，经验
			RL.setdefault(RANK_DATA_IDX, []).append((roleId, sex, career, grade, data[1], data[2], data[3]))
		
		#没有人进入排名
		if not rankList:
			return
		
		#奖励只给第一名
		firstData = rankList[0]
		roleId = firstData[0]
		roleName = firstData[1]
		level = firstData[2]
		#等级是否满足条件
		if level >= 44:
			#离线命令
			Call.LocalDBCall(roleId, RushLevelReward, None)
			#传闻
			cRoleMgr.Msg(1, 0, GlobalPrompt.RUSH_LEVEL_TOP_HEARSAY % roleName)
			
def PerHour():
	minutes = cDateTime.Minutes()
	endMinutes = GetEndTime()
	from Game.Activity.KaifuTarget import TimeControl
	if not WorldData.WD.returnDB:
		return
	kaifuTime = WorldData.WD[EnumSysData.KaiFuKey]
	if Environment.EnvIsRU() and kaifuTime > datetime.datetime(2015,4,10,0,0,0):
		return
	if kaifuTime < TimeControl.KaifuTargetTime_New:
		return
	
	#活动已经结束
	if minutes > endMinutes:
		return
	#更新冲级排名排行榜
	UpdateRushLevelRank()
			
#===============================================================================
# 事件
#===============================================================================
def OnRoleLevelUp(role, param):
	'''
	升级
	@param role:
	@param param:
	'''
	minutes = cDateTime.Minutes()
	endMinutes = GetEndTime()
	from Game.Activity.KaifuTarget import TimeControl
	if not WorldData.WD.returnDB:
		return
	kaifuTime = WorldData.WD[EnumSysData.KaiFuKey]
	if Environment.EnvIsRU() and kaifuTime > datetime.datetime(2015,4,10,0,0,0):
		return
	if kaifuTime < TimeControl.KaifuTargetTime_New:
		return
	
	#活动已经结束
	if minutes >= endMinutes:
		return
	
	level = role.GetLevel()
	if level == 44:
		if role.GetI8(EnumInt8.RushLevel44) == 0:
			#设置可领取
			role.SetI8(EnumInt8.RushLevel44, 1)
	elif level == 46:
		if role.GetI8(EnumInt8.RushLevel46) == 0:
			#设置可领取
			role.SetI8(EnumInt8.RushLevel46, 1)
	elif level == 48:
		if role.GetI8(EnumInt8.RushLevel48) == 0:
			#设置可领取
			role.SetI8(EnumInt8.RushLevel48, 1)
	else:
		pass

def AfterSetKaiFuTime(param1, param2):
	#重新设置了开服时间，把这个缓存的时间重新设置一遍
	global RUSH_LEVEL_END_TIME
	RUSH_LEVEL_END_TIME = 0


#===============================================================================
# 客户端请求
#===============================================================================
def RequestRushLevelOpenPanel(role, msg):
	'''
	客户端请求打开冲级排名面板
	@param role:
	@param msg:
	'''
	from Game.Activity.KaifuTarget import TimeControl
	if not WorldData.WD.returnDB:
		print "GE_EXC, WorldData.WD.returnDB is False in RequestRushLevelOpenPanel"
		return
	kaifuTime = WorldData.WD[EnumSysData.KaiFuKey]
	if Environment.EnvIsRU() and kaifuTime > datetime.datetime(2015,4,10,0,0,0):
		return
	if kaifuTime < TimeControl.KaifuTargetTime_New:
		return
	
	ShowRushLevelPanel(role)
	
def RequestRushLevelGetReward(role, msg):
	'''
	客户端请求领取冲级排名奖励
	@param role:
	@param msg:
	'''
	from Game.Activity.KaifuTarget import TimeControl
	kaifuTime = WorldData.WD[EnumSysData.KaiFuKey]
	if Environment.EnvIsRU() and kaifuTime > datetime.datetime(2015,4,10,0,0,0):
		return
	if kaifuTime < TimeControl.KaifuTargetTime_New:
		return
	
	rewardId = msg
	
	#日志
	with TraRushLevelGetReward:
		GetReward(role, rewardId)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic or Environment.HasWeb:
		RL = Contain.Dict("rush_level", (2038, 1, 1), AfterLoad, isSaveBig = False)
	
	if Environment.HasLogic and not Environment.IsCross:
		#升级事件触发
		Event.RegEvent(Event.Eve_AfterLevelUp, OnRoleLevelUp)
		#注册每分钟调用
		cComplexServer.RegAfterNewMinuteCallFunction(PerMinute)
		#注册每小时调用
		cComplexServer.RegAfterNewHourCallFunction(PerHour)
		
		Event.RegEvent(Event.Eve_AfterSetKaiFuTime, AfterSetKaiFuTime)
		
		#日志
		TraRushLevelGetReward = AutoLog.AutoTransaction("TraRushLevelGetReward", "领取冲级排名奖励")
		
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Rush_Level_Open_Panel", "客户端请求打开冲级排名面板"), RequestRushLevelOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Rush_Level_Get_Reward", "客户端请求领取冲级排名奖励"), RequestRushLevelGetReward)

