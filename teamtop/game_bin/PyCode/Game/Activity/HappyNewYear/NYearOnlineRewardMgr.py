#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.HappyNewYear.NYearOnlineRewardMgr")
#===============================================================================
# 新年冲冲冲
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Activity import CircularDefine
from Game.Role.Data import EnumInt16, EnumDayInt8, EnumObj, EnumInt32
from Game.Activity.HappyNewYear import NewYearConfig

ITEM_TYPE = 1	#奖励为道具
TALENT_TYPE = 2	#奖励为天赋卡
TAROT_TYPE = 3	#奖励为命魂
GOLD_TYPE = 4	#奖励为金币
if "_HasLoad" not in dir():
	IS_START = False
	
	RecordList = []		#奖励记录
	
	ONE_MINUTE_SECONDS = 60
	
	NYearOnlineRecord = AutoMessage.AllotMessage("NYearOnlineRecord", "同步新年冲冲冲奖励记录")
	NYearOnlineGetedRecord = AutoMessage.AllotMessage("NYearOnlineGetedRecord", "同步新年冲冲冲已领取记录")
	#日志
	NYear_Online_reward = AutoLog.AutoTransaction("NYear_Online_reward", "新年冲冲冲开启宝箱")
	
#===============循环活动控制开启===============
def OnStartNYearOnline(*param):
	'''
	开启活动
	'''
	_, circularType = param
	if CircularDefine.CA_NYearOnlineReward != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open HolidayOnline"
		return
		
	IS_START = True
	#给所有在线满足条件的玩家注册TICK
	for tmpRole in cRoleMgr.GetAllRole():
		if tmpRole.GetLevel() < EnumGameConfig.NYEAR_MIN_LEVEL:
			continue
		tmpRole.RegTick(ONE_MINUTE_SECONDS, UpdateOnlineMinutes)
		
def OnEndNYearOnline(*param):
	'''
	活动结束
	'''
	_, circularType = param
	if CircularDefine.CA_NYearOnlineReward != circularType:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC, end HolidayOnline while not start"
		return
		
	IS_START = False
	
#===========================客户端消息==============================
def OnGetOnlineReward(role, param):
	'''
	新年冲冲冲开启宝箱
	@param role:
	@param param:
	'''
	times = param
	if times <= 0:
		return
	with NYear_Online_reward:
		GetOnlineReward(role, times)
	
def GetOnlineReward(role, times):
	level = role.GetLevel()
	if level < EnumGameConfig.NYEAR_MIN_LEVEL:
		return
	minlevel = GetCloseValue(level, NewYearConfig.NYEAR_ONLIEN_MINLEVEL_LIST)
	if not minlevel:return
	
	yearCfg = NewYearConfig.NYEAR_ONLIEN_REWARD.get(minlevel)
	if not yearCfg:
		print "GE_EXC,can not find minLevel(%s) in NewYearConfig.NYEAR_ONLIEN_REWARD" % minlevel
		return
	
	NYearFreeTimes = role.GetDI8(EnumDayInt8.NYearFreeTimes)
	
	Freetimes = 0
	if times > NYearFreeTimes:
		needRmb = 0
		if NYearFreeTimes:
			Freetimes = NYearFreeTimes
			role.SetDI8(EnumDayInt8.NYearFreeTimes, 0)
			#剩余的为神石次数
			remaintimes = times - NYearFreeTimes
			needRmb = yearCfg.needUnbindRMB * remaintimes
		else:
			needRmb = yearCfg.needUnbindRMB * times
		if role.GetUnbindRMB() < needRmb:
			return
		role.DecUnbindRMB(needRmb)
		
	else:
		Freetimes = times
		role.DecDI8(EnumDayInt8.NYearFreeTimes, times)
	
	RewardList = []
	#首先取免费次数对应的奖励
	for _ in xrange(Freetimes):
		itemCoding, itemCnt, codingType, isRecord = yearCfg.randomReward_free.RandomOne()
		RewardList.append((itemCoding, itemCnt, codingType, isRecord))
	#神石次数为总次数减去免费次数
	for _ in xrange(times - Freetimes):
		itemCoding, itemCnt, codingType, isRecord = yearCfg.randomReward_RMB.RandomOne()
		RewardList.append((itemCoding, itemCnt, codingType, isRecord))
	
	tips = GlobalPrompt.Reward_Tips
	for itemCoding, itemCnt, codingType, isRecord in RewardList:
		if codingType == ITEM_TYPE:
			role.AddItem(itemCoding, itemCnt)
			tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt)
		elif codingType == TALENT_TYPE:
			role.AddTalentCard(itemCoding)
			tips += GlobalPrompt.Talent_Tips % (itemCoding, itemCnt)
		elif codingType == TAROT_TYPE:
			role.AddTarotCard(itemCoding, itemCnt)
			tips += GlobalPrompt.Tarot_Tips % (itemCoding, itemCnt)
		elif codingType == GOLD_TYPE:
			role.IncMoney(itemCoding)
			tips += GlobalPrompt.Money_Tips % itemCoding
		
		if isRecord:
			if codingType == TALENT_TYPE:
				cRoleMgr.Msg(11, 0, GlobalPrompt.NYEAR_ONLINE_REWARD_CARD_MSG % (role.GetRoleName(), itemCoding, itemCnt))
			if codingType == ITEM_TYPE:
				cRoleMgr.Msg(11, 0, GlobalPrompt.NYEAR_ONLINE_REWARD_ITEM_MSG % (role.GetRoleName(), itemCoding, itemCnt))
			if codingType == TAROT_TYPE:
				cRoleMgr.Msg(11, 0, GlobalPrompt.NYEAR_ONLINE_REWARD_TAROT_MSG % (role.GetRoleName(), itemCoding, itemCnt))
			Record(role, itemCoding, itemCnt, codingType, isRecord)
	role.Msg(2, 0, tips)
	
def OnGetOnlineFreeTimes(role, param):
	'''
	新年冲冲冲领取免费次数
	@param role:
	@param param:
	'''
	index = param
	
	NYearData = role.GetObj(EnumObj.NYearData)
	freeTimesSet = NYearData.get(1, set())
	
	if index in freeTimesSet:
		return
	
	yearcfg = NewYearConfig.NYAER_FREE_TIMES.get(index)
	if not yearcfg:
		print "GE_EXC, can not find index(%s) in NewYearConfig.NYAER_FREE_TIMES" % index
		return
	
	if yearcfg.needFill:#需要首充
		if not role.GetDayBuyUnbindRMB_Q():
			return
	if yearcfg.onlineTime:
		if role.GetI16(EnumInt16.NYearOnLineMinutes) < yearcfg.onlineTime:
			return
	freeTimesSet.add(index)
	#增加免费次数
	role.IncDI8(EnumDayInt8.NYearFreeTimes, yearcfg.freeTimes)
	role.SendObj(NYearOnlineGetedRecord, freeTimesSet)
	
def OnOpenOnlinePanle(role, param):
	'''
	新年冲冲冲打开宝箱界面
	'''
	if not IS_START:
		return
	global RecordList
	role.SendObj(NYearOnlineRecord, RecordList)
#=================================================================
def Record(role, itemCoding, itemCnt, codingtype, isRecord):
	if not isRecord:
		return
	RecordList.append([role.GetRoleName(), itemCoding, codingtype, itemCnt])
	if len(RecordList) > 9:
		RecordList.pop(0)
	
	role.SendObj(NYearOnlineRecord, RecordList)
	
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
	
def UpdateOnlineMinutes(role, calargv, regparam):
	'''
	每分钟更新在线分钟数
	'''
	if not IS_START:
		return
	
	if role.IsKick():
		return
	
	if role.GetLevel() < EnumGameConfig.NYEAR_MIN_LEVEL: 
		return
	
	#增加在线一分钟
	role.IncI16(EnumInt16.NYearOnLineMinutes, 1)
	#接着注册到下一分钟
	role.RegTick(ONE_MINUTE_SECONDS, UpdateOnlineMinutes)
	
def OnRoleLevelUp(role, param):
	'''
	玩家升级 检测是否达到等级 并注册TICK
	'''
	if not IS_START:
		return
	
	#此次升级不是 解锁等级限制
	if role.GetLevel() != EnumGameConfig.NYEAR_MIN_LEVEL:
		return 
	
	role.RegTick(ONE_MINUTE_SECONDS, UpdateOnlineMinutes)
	
def OnRoleLogin(role, param):
	'''
	登陆注册tick
	'''
	NYearData = role.GetObj(EnumObj.NYearData)
	if not NYearData:
		role.SetObj(EnumObj.NYearData, {1:set(), 2:{}, 3:{}})
		
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.NYEAR_MIN_LEVEL:
		return
	
	NYearData = role.GetObj(EnumObj.NYearData)
	role.SendObj(NYearOnlineGetedRecord, NYearData.get(1, set()))
	
	role.RegTick(ONE_MINUTE_SECONDS, UpdateOnlineMinutes)
	
def SyncRoleOtherData(role, param):
	if not IS_START:
		return
	NYearData = role.GetObj(EnumObj.NYearData)
	role.SendObj(NYearOnlineGetedRecord, NYearData.get(1, set()))
	
def OnRoleDayClear(role, param = None):
	'''
	在线奖励每日重置
	'''
	#重置在线分钟
	role.SetI16(EnumInt16.NYearOnLineMinutes, 0)
	
	NYearData = role.GetObj(EnumObj.NYearData)
	NYearData[1] = set()
	if not IS_START:
		return
	role.SendObj(NYearOnlineGetedRecord, NYearData.get(1, set()))
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
		
	if Environment.HasLogic and not Environment.IsCross:
		#监听事件
		Event.RegEvent(Event.Eve_AfterLogin, OnRoleLogin)
		Event.RegEvent(Event.Eve_AfterLevelUp, OnRoleLevelUp)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndNYearOnline)
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartNYearOnline)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		#监听消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NYear_OnlineReward_Msg", "新年冲冲冲开启宝箱"), OnGetOnlineReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NYear_OnlineReward_Freetimes_Msg", "新年冲冲冲领取免费次数"), OnGetOnlineFreeTimes)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NYear_Opne_Online_Msg", "新年冲冲冲打开宝箱界面"), OnOpenOnlinePanle)