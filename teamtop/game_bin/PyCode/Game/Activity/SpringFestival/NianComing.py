#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.SpringFestival.NianComing")
#===============================================================================
# 年兽来了
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Activity import CircularDefine
from Game.Role.Data import EnumDayInt8, EnumObj
from Game.Activity.SpringFestival import SpringFestivalConfig

ITEM_TYPE = 1	#奖励为道具
TALENT_TYPE = 2	#奖励为天赋卡
TAROT_TYPE = 3	#奖励为命魂
GOLD_TYPE = 4	#奖励为金币
if "_HasLoad" not in dir():
	IS_START = False
	
	RecordList = []		#奖励记录
	
	NIAN_CODING = 27864	#年兽coding
	
	NianComing_Data = AutoMessage.AllotMessage("NianComing_Data", "同步年兽来了数据")
	NianComing_Record = AutoMessage.AllotMessage("NianComing_Record", "同步年兽来了奖励记录")
	#日志
	NianComfing_Times = AutoLog.AutoTransaction("NianComfing_Times", "领取年兽来了开宝箱次数")
	NianComfing_Reward = AutoLog.AutoTransaction("NianComfing_Reward", "领取年兽来了开启宝箱奖励")
	NianComfing_Exchange = AutoLog.AutoTransaction("NianComfing_Exchange", "兑换年兽")
#===============循环活动控制开启===============
def OnStartNYearOnline(*param):
	'''
	开启活动
	'''
	_, circularType = param
	if CircularDefine.CA_SpringFNianComing != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open SpringFNianComing"
		return
		
	IS_START = True
		
def OnEndNYearOnline(*param):
	'''
	活动结束
	'''
	_, circularType = param
	if CircularDefine.CA_SpringFNianComing != circularType:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC, end SpringFNianComing while not start"
		return
		
	IS_START = False

#=====================================================
def RequestGetTimes(role, param):
	'''
	客户端请求领取年兽来了开宝箱次数
	@param role:
	@param param:
	'''
	index = param
	
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.Spring_Festival_NeedLevel:
		return
	
	cfg = SpringFestivalConfig.NIAN_COMING_TIMES_DICT.get(index)
	if not cfg:
		print "GE_EXC,can not find index(%s) in NIAN_COMING_TIMES_DICT" % index
		return
	if not cfg.rewardTimes:
		print "GE_EXC,SpringFestivalConfig.NIAN_COMING_TIMES_DICT,index(%s) is rewardTimes=0" % index
		return
	
	SpringFestivalData = role.GetObj(EnumObj.SpringFestivalData)
	if index in SpringFestivalData.get(5, set()):
		return
	
	if role.GetDayBuyUnbindRMB_Q() < cfg.needUnRMB_Q:
		return
	
	with NianComfing_Times:
		SpringFestivalData[5].add(index)
		role.IncDI8(EnumDayInt8.NianComingTimes, cfg.rewardTimes)
		role.SendObj(NianComing_Data, SpringFestivalData.get(5))
		role.Msg(2, 0, GlobalPrompt.SpringNianComing % cfg.rewardTimes)
		
def RequestOpenBox(role, param):
	'''
	客户端请求开启年兽来了宝箱
	@param role:
	@param param:
	'''
	times = param
	if times < 0:
		return
	with NianComfing_Reward:
		GetReward(role, times)
		
def RequestExchangeNian(role, param):
	'''
	客户端请求兑换年兽
	@param role:
	@param param:年兽coding
	'''
	cfg = SpringFestivalConfig.NIAN_COMING_EXCHANGE_DICT.get(NIAN_CODING)
	if not cfg:
		return
	
	needConing, needCnt = cfg.needCoding, cfg.needCnt
	if role.ItemCnt(needConing) < needCnt:
		return
	
	with NianComfing_Exchange:
		role.DelItem(needConing, needCnt)
		role.AddItem(NIAN_CODING, 1)
		role.Msg(2, 0, GlobalPrompt.Reward_Item_Tips % (NIAN_CODING, 1))
		cRoleMgr.Msg(11, 0, GlobalPrompt.SpringExchangeComing % role.GetRoleName())
		
def RequestOpenPanel(role, param):
	'''
	客户端请求年兽来了面板
	@param role:
	@param param:
	'''
	global RecordList
	role.SendObj(NianComing_Record, RecordList)
#==========================================================
def GetReward(role, times):
	level = role.GetLevel()
	if level < EnumGameConfig.Spring_Festival_NeedLevel:
		return
	minlevel = GetCloseValue(level, SpringFestivalConfig.NIAN_MINLEVEL_LIST)
	if not minlevel:return
	
	cfg = SpringFestivalConfig.NIAN_COMING_REWARD_DICT.get(minlevel)
	if not cfg:
		print "GE_EXC,can not find minLevel(%s) in SpringFestivalConfig.NIAN_COMING_REWARD_DICT" % minlevel
		return
	
	NianComingTimes = role.GetDI8(EnumDayInt8.NianComingTimes)
	if times > NianComingTimes:
		return
	
	role.DecDI8(EnumDayInt8.NianComingTimes, times)
	
	RewardList = []
	for _ in xrange(times):
		itemCoding, itemCnt, codingType, isRecord = cfg.RMBReward_Random.RandomOne()
		RewardList.append((itemCoding, itemCnt, codingType, isRecord))
		
	NianCoding, Niancnt = 0, 0
	for _ in xrange(times):
		itemCoding, itemCnt = cfg.NianReward_Random.RandomOne()
		if not NianCoding:
			NianCoding = itemCoding
		Niancnt += itemCnt
		
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
			Record(role, itemCoding, itemCnt, codingType, isRecord)
	
	if NianCoding and Niancnt:
		role.AddItem(NianCoding, Niancnt)
		tips += GlobalPrompt.Item_Tips % (NianCoding, Niancnt)
	
	role.Msg(2, 0, tips)
		
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
	
def Record(role, itemCoding, itemCnt, codingtype, isRecord):
	if not isRecord:
		return
	global RecordList
	RecordList.append([role.GetRoleName(), itemCoding, codingtype, itemCnt])
	if len(RecordList) > 9:
		RecordList.pop(0)
	
	role.SendObj(NianComing_Record, RecordList)
#=============玩家事件===============
def OnRoleDayClear(role, param):
	SpringFestivalData = role.GetObj(EnumObj.SpringFestivalData)
	SpringFestivalData[5] = set()
	role.SendObj(NianComing_Data, SpringFestivalData.get(5))
	
def SyncRoleOtherData(role, param):
	global IS_START
	if not IS_START:
		return
	SpringFestivalData = role.GetObj(EnumObj.SpringFestivalData)
	role.SendObj(NianComing_Data, SpringFestivalData.get(5))
	global RecordList
	role.SendObj(NianComing_Record, RecordList)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
		
	if Environment.HasLogic and not Environment.IsCross:
		#监听事件
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndNYearOnline)
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartNYearOnline)
		
		#监听消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Request_NianComing_Gettimes", "客户端请求领取年兽来了开宝箱次数"), RequestGetTimes)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Request_NianComing_OpenBox", "客户端请求开启年兽来了宝箱"), RequestOpenBox)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Request_NianComing_ExchangeNian", "客户端请求兑换年兽"), RequestExchangeNian)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Request_NianComing_OpenPanel", "客户端请求年兽来了面板"), RequestOpenPanel)
		