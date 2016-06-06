#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.CollectLongyin.CollectLongyin")
#===============================================================================
# 每日集龙印 -- 由之前的限制时间的活动改为日常活动了
#===============================================================================
import Environment
import cRoleMgr
import cDateTime
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Persistence import Contain
from Game.Role import Event
from Game.Role.Mail import Mail

if "_HasLoad" not in dir():
	#消息
	CollectLongyinData = AutoMessage.AllotMessage("CollectLongyinData", "每日集龙印数据")
	
	#日志
	CollectQiandao_Log = AutoLog.AutoTransaction("CollectQiandao_Log", "每日集龙印签到日志")
	CollectBuqian_Log = AutoLog.AutoTransaction("CollectBuqian_Log", "每日集龙印补签日志")
	CollectRmbReward_Log = AutoLog.AutoTransaction("CollectRmbReward_Log", "每日集龙印领取每日充值奖励龙印日志")
	CollectLongyinReward_Log = AutoLog.AutoTransaction("CollectLongyinReward_Log", "每日集龙印领取龙印日志")
#===============================================================================
# 客户端请求
#===============================================================================
def RequestOpenPanel(role, msg):
	'''
	请求打开每日集龙印面板 -- 打开面板的时候初始化每日集龙印的数据
	@param role:
	@param msg:
	'''
	global CollectLongyinDict
	
	#等级不足
	if role.GetLevel() < EnumGameConfig.CollectLongyinLvLimit:
		return
	
	#持久化字典没有载回
	if not CollectLongyinDict.returnDB:
		return
	
	roleId = role.GetRoleID()
	collectData = CollectLongyinDict.get(roleId)
	if not collectData:
		#初始化
		CollectLongyinDict[roleId] = collectData = {1:0, 2:0, 3:{cDateTime.Month():set()}, 4:set(), 5:set(), 6:1}
	role.SendObj(CollectLongyinData, collectData)

def RequestQiandao(role, msg):
	'''
	请求签到
	@param role:
	@param msg:
	'''
	global CollectLongyinDict
	
	#持久化字典没有载回
	if not CollectLongyinDict.returnDB:
		return
	
	#等级不足
	level = role.GetLevel()
	if level < EnumGameConfig.CollectLongyinLvLimit:
		return
	
	#根据等级获取配置
	from Game.Activity.CollectLongyin import CollectLongyinConfig
	cfg = CollectLongyinConfig.CollectQiandao_Dict.get(GetCloseValue(level, CollectLongyinConfig.CollectQiandaoLevel_List))
	if not cfg:
		print 'GE_EXC, collect longyin can not find qiandao cfg by level %s' % level
		return
	
	month, day = cDateTime.Month(), cDateTime.Day()
	
	roleId = role.GetRoleID()
	#{role_id:1:累计龙印个数, 2:当天累计充值, 3:{month:set()}, 4:set(当天领取充值奖励集合-每日清理), 5:set(领取收集龙印奖励集合), 6:补签次数}
	collectData = CollectLongyinDict.get(roleId)
	if not collectData:
		return
	if not collectData[3]:
		collectData[3][month] = set([day])
	elif month not in collectData[3] or day in collectData[3][month]:
		return
	else:
		collectData[3][month].add(day)
	
	collectData[1] += 1
	CollectLongyinDict[roleId] = collectData
	
	role.SendObj(CollectLongyinData, collectData)
	
	with CollectQiandao_Log:
		if role.PackageEmptySize() < len(cfg.rewardItem):
			Mail.SendMail(roleId, GlobalPrompt.CollectLongyin_MailTitle, GlobalPrompt.CollectLongyin_MailSender, GlobalPrompt.CollectLongyin_MailContent, items=cfg.rewardItem, money=cfg.rewardMoney)
		else:
			tips = GlobalPrompt.Reward_Tips
			for item in cfg.rewardItem:
				role.AddItem(*item)
				tips += GlobalPrompt.Item_Tips % item
			if cfg.rewardMoney:
				role.IncMoney(cfg.rewardMoney)
				tips += GlobalPrompt.Money_Tips % cfg.rewardMoney
			#每次加一个龙印
			tips += GlobalPrompt.CollectLongyin_Add % 1
			role.Msg(2, 0, tips)
	
def RequestBuqian(role, msg):
	'''
	请求补签
	@param role:
	@param msg:
	'''
	global CollectLongyinDict
	
	#持久化字典没有载回
	if not CollectLongyinDict.returnDB:
		return
	
	#等级不够
	level = role.GetLevel()
	if level < EnumGameConfig.CollectLongyinLvLimit:
		return
	
	#根据等级读取奖励
	from Game.Activity.CollectLongyin import CollectLongyinConfig
	qiandaoCfg = CollectLongyinConfig.CollectQiandao_Dict.get(GetCloseValue(level, CollectLongyinConfig.CollectQiandaoLevel_List))
	if not qiandaoCfg:
		print 'GE_EXC, collect longyin can not find qiandao cfg by level %s' % level
		return
	
	buqianDay = msg
	
	nowMonth = cDateTime.Month()
	
	#今天的不能补签
	if buqianDay == cDateTime.Day():
		return
	
	roleId = role.GetRoleID()
	collectData = CollectLongyinDict.get(roleId)
	if not collectData:
		return
	
	cfg = CollectLongyinConfig.CollectBuqian_Dict.get(collectData[6])
	if not cfg:
		print 'GE_EXC, collect longyin can not find buqian cnt %s in CollectBuqian_Dict' % collectData[6]
		return
	
	
	if role.GetUnbindRMB() < cfg.needUnbindRMB:
		return
	
	if not collectData[3]:
		collectData[3][nowMonth] = set([buqianDay])
	elif nowMonth not in collectData[3] or buqianDay in collectData[3][nowMonth]:
		return
	else:
		collectData[3][nowMonth].add(buqianDay)
	
	with CollectBuqian_Log:
		
		role.DecUnbindRMB(cfg.needUnbindRMB)
		
		collectData[6] += 1
		collectData[1] += 1
		
		CollectLongyinDict[roleId] = collectData
		
		if role.PackageEmptySize() < len(qiandaoCfg.rewardItem):
			Mail.SendMail(roleId, GlobalPrompt.CollectLongyin_MailTitle, GlobalPrompt.CollectLongyin_MailSender, GlobalPrompt.CollectLongyin_MailContent, items=qiandaoCfg.rewardItem, money=qiandaoCfg.rewardMoney)
		else:
			tips = GlobalPrompt.Reward_Tips
			for item in qiandaoCfg.rewardItem:
				role.AddItem(*item)
				tips += GlobalPrompt.Item_Tips % item
			if qiandaoCfg.rewardMoney:
				role.IncMoney(qiandaoCfg.rewardMoney)
				tips += GlobalPrompt.Money_Tips % qiandaoCfg.rewardMoney
			#每次加一个龙印
			tips += GlobalPrompt.CollectLongyin_Add % 1
			role.Msg(2, 0, tips)
		role.SendObj(CollectLongyinData, collectData)
	
def RequestRmbReward(role, msg):
	'''
	请求领取每日神石充值奖励
	@param role:
	@param msg:
	'''
	global CollectLongyinDict
	
	if not CollectLongyinDict.returnDB:
		return
	
	if role.GetLevel() < EnumGameConfig.CollectLongyinLvLimit:
		return
	
	roleId = role.GetRoleID()
	
	#没有数据
	collectData = CollectLongyinDict.get(roleId)
	if not collectData:
		return
	
	rmbRewardIndex = msg
	
	#已经领取过奖励
	if rmbRewardIndex in collectData[4]:
		return
	
	from Game.Activity.CollectLongyin import CollectLongyinConfig
	cfg = CollectLongyinConfig.CollectRmbReward_Dict.get(rmbRewardIndex)
	if not cfg:
		return
	
	totalRMB = collectData[2]
	if totalRMB < cfg.needRMB:
		return
	
	#记录领取奖励
	with CollectRmbReward_Log:
		collectData[4].add(rmbRewardIndex)
		collectData[1] += cfg.rewardLongyin
		CollectLongyinDict[roleId] = collectData
		
		AutoLog.LogBase(roleId, AutoLog.eveRewardLongyin, rmbRewardIndex)
	
	role.SendObj(CollectLongyinData, collectData)
	role.Msg(2, 0, GlobalPrompt.CollectLongyin_Add % cfg.rewardLongyin)
	
def RequestLongyinReward(role, msg):
	'''
	请求领取累计收集龙印奖励
	@param role:
	@param msg:
	'''
	global CollectLongyinDict
	
	if not CollectLongyinDict.returnDB:
		return
	
	if role.GetLevel() < EnumGameConfig.CollectLongyinLvLimit:
		return
	
	#没有数据
	roleId = role.GetRoleID()
	collectData = CollectLongyinDict.get(roleId)
	if not collectData:
		return
	
	rewardIndex = msg
	
	#已经领取过奖励
	if rewardIndex in collectData[5]:
		return
	
	from Game.Activity.CollectLongyin import CollectLongyinConfig
	cfg = CollectLongyinConfig.CollectLongyinReward_Dict.get(rewardIndex)
	if not cfg:
		return
	
	longyinCnt = collectData[1]
	if longyinCnt < cfg.needLongyinCnt:
		return
	
	if role.PackageEmptySize() < len(cfg.rewardItem):
		role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
		return
	
	#记录领取奖励
	collectData[5].add(rewardIndex)
	CollectLongyinDict[roleId] = collectData
	
	with CollectLongyinReward_Log:
		tips = GlobalPrompt.Reward_Tips
		for item in cfg.rewardItem:
			role.AddItem(*item)
			tips += GlobalPrompt.Item_Tips % item
		if cfg.rewardBindRMB:
			role.IncBindRMB(cfg.rewardBindRMB)
		tips += GlobalPrompt.BindRMB_Tips % cfg.rewardBindRMB
		role.Msg(2, 0, tips)
		
	role.SendObj(CollectLongyinData, collectData)
	
def GetCloseValue(value, valueList):
	tmp_level = 0
	for i in valueList:
		if i > value:
			return tmp_level
		tmp_level = i
	else:
		return tmp_level
#===============================================================================
# 事件
#===============================================================================
def SyncRoleOtherData(role, param):
	#同步集龙印数据
	global CollectLongyinDict
	if not CollectLongyinDict.returnDB:
		return
	
	if role.GetLevel() < EnumGameConfig.CollectLongyinLvLimit:
		return
	
	collectData = CollectLongyinDict.get(role.GetRoleID())
	if not collectData:
		return
	
	role.SendObj(CollectLongyinData, collectData)
	
def RoleDayClear(role, param):
	#每日清理玩家的当日累计充值和领取的累计充值奖励记录
	global CollectLongyinDict
	
	if not CollectLongyinDict.returnDB:
		return
	
	roleId = role.GetRoleID()
	collectData = CollectLongyinDict.get(roleId)
	if not collectData:
		return
	
	#当天累计充值
	collectData[2] = 0
	#当天领取的奖励集合
	collectData[4] = set()
	
	#跨月清理 -- 兼容之前的数据, 只有在跨月后才会清理记录的签到数据, 3中可能会有几个月的数据
	nowMonth = cDateTime.Month()
	if nowMonth not in collectData[3]:
		collectData = {1:0, 2:0, 3:{nowMonth:set()}, 4:set(), 5:set(), 6:1}
	
	CollectLongyinDict[roleId] = collectData
	
	role.SendObj(CollectLongyinData, collectData)
	
def AfterChangeUnbindRMB_Q(role, param):
	global CollectLongyinDict
	
	if not CollectLongyinDict.returnDB:
		return
	
	oldValue, newValue = param
	if oldValue > newValue:
		return
	
	roleId = role.GetRoleID()
	if roleId not in CollectLongyinDict:
		CollectLongyinDict[roleId] = {1:0, 2:newValue - oldValue, 3:{}, 4:set(), 5:set(), 6:1}
		role.SendObj(CollectLongyinData, {1:0, 2:newValue - oldValue, 3:{}, 4:set(), 5:set(), 6:1})
	else:
		collectData = CollectLongyinDict[roleId]
		collectData[2] += newValue - oldValue
		CollectLongyinDict[roleId] = collectData
		role.SendObj(CollectLongyinData, collectData)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic or Environment.HasWeb:
		#{role_id:{1:累计龙印个数, 2:当天累计充值, 3:{月份:set(天)}, 4:set(当天领取充值奖励集合-每日清理), 5:set(领取收集龙印奖励集合), 6:补签次数}}
		CollectLongyinDict = Contain.Dict("CollectLongyinDict", (2038, 1, 1))
		
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		Event.RegEvent(Event.Eve_AfterChangeDayBuyUnbindRMB_Q, AfterChangeUnbindRMB_Q)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CollectLongyin_OpenPanel", "请求每日集龙印面板"), RequestOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CollectLongyin_QianDao", "请求签到"), RequestQiandao)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CollectLongyin_BuQian", "请求补签"), RequestBuqian)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CollectLongyin_RmbReward", "请求累计充值神石奖励"), RequestRmbReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CollectLongyin_LongyinReward", "请求收集龙印奖励"), RequestLongyinReward)
		
	