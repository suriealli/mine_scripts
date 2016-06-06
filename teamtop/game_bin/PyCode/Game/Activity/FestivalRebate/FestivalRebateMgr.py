#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.FestivalRebate.FestivalRebateMgr")
#===============================================================================
# 春节大回馈 Mgr
#===============================================================================
import datetime
import Environment
import cRoleMgr
import cDateTime
import cNetMessage
import cComplexServer
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt, EnumSysData
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Role.Mail import Mail
from Game.SysData import WorldData
from Game.Persistence import Contain
from Game.Activity.FestivalRebate import FestivalRebateConfig


STATE_DEFAULT = 0
STATE_REWARD = 1

IDX_RMB = 0
IDX_STATE = 1

ORIGIN_DATETIME = (2000, 1, 1, 0, 0, 0)


if "_HasLoad" not in dir():
	#活动开关
	IS_START = False
	#活动结束时间戳
	END_TIME = 0
	#活动天数索引
	DAY_INDEX = 0
	#活动控制配置
	FestivalRebate_Active_Control = None
	
	#格式:  (IS_START, END_TIME, DAY_INDEX)
	FestivalRebate_ActiveState_S = AutoMessage.AllotMessage("FestivalRebate_ActiveState_S", "春节大回馈_活动状态同步")
	#格式:  (DAY_INDEX)
	FestivalRebate_DayIndex_S = AutoMessage.AllotMessage("FestivalRebate_DayIndex_S", "春节大回馈_天数索引同步")
	#格式:  {dayIndex:[buyRMB,state]} 第dayIndex天 购买了buyRMB神石  领取状态为state 0-未领取 1-已领取
	FestivalRebate_RoleActiveData_S = AutoMessage.AllotMessage("FestivalRebate_RoleActiveData_S", "春节大回馈_角色活动数据同步")
	
	Tra_FestivalRebate_Reward = AutoLog.AutoTransaction("Tra_FestivalRebate_Reward", "春节大回馈_领取回馈奖励")
	Tra_FestivalRebate_RewardSys = AutoLog.AutoTransaction("Tra_FestivalRebate_RewardSys", "春节大回馈_发放未领取的回馈奖励")
	
	
#===============================================================================
# 活动控制
#===============================================================================
def StartFestivalRebate(callArgv, regparam):
	'''
	春节大回馈_开启活动
	'''
	global IS_START
	if IS_START:
		print "GE_EXC,StartFestivalRebate Error:repeat Start Active"
		return 
	
	global END_TIME
	global FestivalRebate_Active_Control
	FestivalRebate_Active_Control, END_TIME = regparam
	if not CanStartActive():
		print "GE_EXC,StartFestivalRebate:new server can not start active"
		return 
	
	IS_START = True
	CalculateDayIndex()
	
	cNetMessage.PackPyMsg(FestivalRebate_ActiveState_S, (IS_START, END_TIME, DAY_INDEX))
	cRoleMgr.BroadMsg()


def EndFestivalRebate(callArgv, regparam):
	'''
	春节大回馈_结束活动
	'''
	global IS_START
	if not IS_START:
		print "GE_EXC,EndFestivalRebate Error: end active but not start"
		return 
	
	IS_START = False
	
	cNetMessage.PackPyMsg(FestivalRebate_ActiveState_S, (IS_START, END_TIME, DAY_INDEX))
	cRoleMgr.BroadMsg()
	
	AuToRewardAll()


#===============================================================================
# 客户端请求
#===============================================================================
def OnGetReward(role, msg):
	'''
	春节大回馈_请求领取奖励
	@param msg: targetIndex
	'''
	if not IS_START:
		return 
	
	if role.GetLevel() < EnumGameConfig.FestivalRebate_NeedLevel:
		return 
	
	#当前天数不足领取回馈奖励
	targetIndex = msg	
	if targetIndex + FestivalRebate_Active_Control.logDays > DAY_INDEX:
		return 
	
	roleId = role.GetRoleID()
	global FestivalRebate_Dict
	if roleId not in FestivalRebate_Dict:
		return 
	
	roleFRDict = FestivalRebate_Dict[roleId]
	if targetIndex not in roleFRDict:
		return 
	
	targetIndexData = roleFRDict[targetIndex]
	if targetIndexData[IDX_STATE] != STATE_DEFAULT:
		return 
	
	rebateRMB = FestivalRebateConfig.CalculateRebateRMB(targetIndexData[IDX_RMB])
	if rebateRMB < 1:
		return 
	
	with Tra_FestivalRebate_Reward:
		#记录状态
		targetIndexData[IDX_STATE] = STATE_REWARD
		#获得神石
		role.IncUnbindRMB_S(rebateRMB)
		#提示
		role.Msg(2, 0, GlobalPrompt.FestivalRebate_Tips_Reward % rebateRMB)
		#日志
		AutoLog.LogBase(roleId, AutoLog.eveFestivalRebate, (targetIndex, rebateRMB))
		#设置持久化数据改变标记
		FestivalRebate_Dict.changeFlag = True
	
	role.SendObj(FestivalRebate_RoleActiveData_S, roleFRDict)
	

#===============================================================================
# 辅助
#===============================================================================	
def AuToRewardAll():
	'''
	邮件处理未领取的返利
	'''
	if IS_START:
		return 
	
	global FestivalRebate_Dict
	if not FestivalRebate_Dict.returnDB:
		return
	
	with Tra_FestivalRebate_RewardSys:
		for tRoleId, tRoleFRDict in FestivalRebate_Dict.iteritems():
			rebateRMB = 0
			rebateList = []
			for tDayIndex, tData in tRoleFRDict.iteritems():
				if tData[IDX_STATE] == STATE_DEFAULT:
					rebateRMB += FestivalRebateConfig.CalculateRebateRMB(tData[IDX_RMB])
					rebateList.append((tDayIndex, rebateRMB))
					tData[IDX_STATE] = STATE_REWARD
			if rebateRMB > 0:
				#邮件
				Mail.SendMail(tRoleId,
							GlobalPrompt.FestivalRebate_Mail_Title,
							GlobalPrompt.FestivalRebate_Mail_Sender,
							GlobalPrompt.FestivalRebate_Mail_Content % rebateRMB,
							unbindrmb=rebateRMB)
				#日志
				AutoLog.LogBase(tRoleId, AutoLog.eveFestivalRebateSys, rebateList)
		FestivalRebate_Dict.changeFlag = True

def CanStartActive():
	'''
	根据活动配置数据 判断本服是否可以开启活动
	PS:唯一条件就是   在 活动开启时间点 本服开服天数 满足 配置最小开服天数
	'''
	#活动开启点 - 开服时间 >= 限制开服天数 可以开启 否则不能开启	(将两个比较时间 都先处理为当天的0点再做比较 忽略时分秒的影响)
	kaifuDate = WorldData.WD[EnumSysData.KaiFuKey]	
	kaifuDate = datetime.datetime(kaifuDate.year, kaifuDate.month, kaifuDate.day, 0, 0, 0)
	beginDate = FestivalRebate_Active_Control.beginTime
	beginDate = datetime.datetime(beginDate.year, beginDate.month, beginDate.day, 0, 0, 0)
	if (beginDate - kaifuDate).days + 1 < FestivalRebate_Active_Control.minKaiFuDays:
		return False
	else:
		return True


def CalculateDayIndex():
	'''
	计算当前活动开启天数
	'''
	if not IS_START:
		return 
	
	#当前日期时间
	nowDate = cDateTime.Now()
	#活动持续开启的天数
	#更新全局DAY_INDEX
	global DAY_INDEX
	interval = nowDate - FestivalRebate_Active_Control.beginTime
	DAY_INDEX = interval.days + 1	


#===============================================================================
# 事件
#===============================================================================
def AfterLoad():
	'''
	活动数据载回之后 再次触发自动发放奖励逻辑 
	活动结束时间点 处于避免停服过程
	PS 若已经正常自动发放了奖励  再跑一遍也不会重复发放奖励
	'''
	AuToRewardAll()


def AfterNewDay():
	'''
	跨天 重算天数索引
	'''
	if not IS_START:
		return 
	
	#重算天数
	CalculateDayIndex()
	
	#广播同步最新天数索引
	cNetMessage.PackPyMsg(FestivalRebate_DayIndex_S, DAY_INDEX)
	cRoleMgr.BroadMsg()


def OnSyncOtherDate(role, param=None):
	'''
	1.处理今日充值记录
	2.同步活动数据
	'''
	#活动未开启
	if not IS_START:
		return
	
	global DAY_INDEX
	role.SendObj(FestivalRebate_ActiveState_S, (IS_START, END_TIME, DAY_INDEX))
	
	#同步今日充值到持久化数据
	global FestivalRebate_Dict
	if not FestivalRebate_Dict.returnDB:
		return 
	
	if DAY_INDEX <= FestivalRebate_Active_Control.logDays:
		dayBuyRMB = role.GetDayBuyUnbindRMB_Q()
		if dayBuyRMB > 0:
			roleFRDict = FestivalRebate_Dict.setdefault(role.GetRoleID(), {})
			if DAY_INDEX in roleFRDict:
				roleFRDict[DAY_INDEX][IDX_RMB] = dayBuyRMB
			else:
				roleFRDict[DAY_INDEX] = [dayBuyRMB, STATE_DEFAULT]
			FestivalRebate_Dict.changeFlag = True
	
	#同步客户端活动数据
	role.SendObj(FestivalRebate_RoleActiveData_S, FestivalRebate_Dict.get(role.GetRoleID(), {}))


def AfterChangeDayBuyUnbindRMB_Q(role, param):
	'''
	今日购买神石数改变
	'''
	#活动未开启
	if not IS_START:
		return
	
	#不在记录天数范围内
	global DAY_INDEX
	if DAY_INDEX > FestivalRebate_Active_Control.logDays:
		return 
	
	#非充值增加
	oldValue, newValue = param
	if oldValue > newValue:
		return
	
	#持久化数据未载回
	global FestivalRebate_Dict
	if not FestivalRebate_Dict.returnDB:
		return
	
	roleFRDict = FestivalRebate_Dict.setdefault(role.GetRoleID(), {})
	if DAY_INDEX in roleFRDict:
		roleFRDict[DAY_INDEX][IDX_RMB] = newValue
	else:
		roleFRDict[DAY_INDEX] = [newValue, STATE_DEFAULT]
	
	FestivalRebate_Dict.changeFlag = True	
	role.SendObj(FestivalRebate_RoleActiveData_S, roleFRDict)
	

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#春节大回馈数据 {roleId:{dayIndex:[buyRMB,state],},}
		FestivalRebate_Dict = Contain.Dict("FestivalRebate_Dict", (2038, 1, 1), AfterLoad)
		
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
		
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncOtherDate)
		Event.RegEvent(Event.Eve_AfterChangeDayBuyUnbindRMB_Q, AfterChangeDayBuyUnbindRMB_Q)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("FestivalRebate_OnGetReward", "春节大回馈_请求领取奖励"), OnGetReward)
		
