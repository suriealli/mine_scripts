#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.HalloweenNA.HalloweenNAMgr")
#===============================================================================
# 北美万圣节活动(改为北通用活动模块)
#===============================================================================
import cRoleMgr
import cComplexServer
import Environment
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Persistence import Contain
from Game.Activity.HalloweenNA import HalloweenNABase, HalloweenNAConfig, HalloweenNADefine
from Game.Role import Event
from Game.Role.Data import EnumTempObj

if "_HasLoad" not in dir():
	SEVEN_ACT_NEED_LEVEL = 20		#七日活动需要的等级
	
	RIGHT_ACTID_LIST = [11, 12]
	#消息
	NA_Halloween_Sync_All = AutoMessage.AllotMessage("NA_Halloween_Sync_All", "通知客户端同步北美万圣节所有数据")
	NA_Halloween_Sync_StartingAct = AutoMessage.AllotMessage("NA_Halloween_Sync_StartingAct", "同步北美通用活动正在开启的活动")

def HalloweenOpenMainPanel(role):
	global HalloweenNaDict
	HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
	
	#奖励状态字典，累计充值神石，公会副本次数，竞技场挑战次数，在线时间， 累计羽翼培养， 活动期间合成宝石，英雄升级和进化,挑战恶魔深渊次数，宠物培养次数, 坐骑培养次数， 坐骑神石培养次数,\
	#解救奴隶次数,抓捕奴隶次数,累计消费，装备强化,占卜紫魂黄魂对应的数量,占卜次数,每日宝石合成数量,每日购买宝石,累计宠物培养次数，累计符文合成，累计派对数，累计情缘副本数
	role.SendObj(NA_Halloween_Sync_All, (HalloweenNAMgr.reward_status_dict, HalloweenNAMgr.buy_unbind_rmb,HalloweenNAMgr.union_fb_cnt, \
										HalloweenNAMgr.jjc_cnt, HalloweenNAMgr.online_time,HalloweenNAMgr.wing_train_totalcnt, \
										HalloweenNAMgr.gem_syn_dict, HalloweenNaDict.data, HalloweenNAMgr.EvilHole_times, \
										HalloweenNAMgr.Petevl_times, HalloweenNAMgr.mount_train_cnt, HalloweenNAMgr.mount_rmb_train_cnt, \
										HalloweenNAMgr.slave_cnt, HalloweenNAMgr.catch_slave_cnt,HalloweenNAMgr.total_cost_RMB, \
										HalloweenNAMgr.equipment_streng_cnt, HalloweenNAMgr.tarot_cnt_dict, HalloweenNAMgr.tarot_cnt, \
										HalloweenNAMgr.gem_day_syn_dict, HalloweenNAMgr.buy_gem_day_cnt, HalloweenNAMgr.Petevl_times_forever, \
										HalloweenNAMgr.Fuwen_syn_dict, HalloweenNAMgr.party_times_dict, HalloweenNAMgr.couples_fb_times))

def HalloweenGetReward(role, actId, idx, backFunId):
	HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
	
	rewardConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
	if not rewardConfig:
		return
	
	if actId not in HalloweenNAMgr.reward_status_dict:
		return
	rewardStatusDict = HalloweenNAMgr.reward_status_dict[actId]
	if idx not in rewardStatusDict:
		return
	
	#是否可以领取
	if rewardStatusDict[idx] != 1:
		return
	
	if rewardConfig.maxCnt > 0:
		global HalloweenNaDict
		actData = HalloweenNaDict.setdefault(actId, {})
		if actData.get(idx, 0) >= rewardConfig.maxCnt:#在玩家领取奖励的时候已经领完了
			#删除对应idx记录
			del rewardStatusDict[idx]
			return
		else:
			actData[idx] = actData.get(idx, 0) + 1	#全服领取数+1
			HalloweenNaDict[actId] = actData
			HalloweenNaDict.changeFlag = True
		
	rewardStatusDict[idx] = 2
	
	rewardPrompt = ""
	#奖励
	if rewardConfig.rewardMoney:
		role.IncMoney(rewardConfig.rewardMoney)
		rewardPrompt += GlobalPrompt.Money_Tips % rewardConfig.rewardMoney
	if rewardConfig.rewardRMB:
		role.IncBindRMB(rewardConfig.rewardRMB)
		rewardPrompt += GlobalPrompt.BindRMB_Tips % rewardConfig.rewardRMB
	if rewardConfig.rewardItem:
		for coding, cnt in rewardConfig.rewardItem:
			role.AddItem(coding, cnt)
			rewardPrompt += GlobalPrompt.Item_Tips % (coding, cnt)
	if rewardConfig.rewardTarot:
		role.AddTarotCard(rewardConfig.rewardTarot, 1)
		rewardPrompt += GlobalPrompt.Tarot_Tips % (rewardConfig.rewardTarot, 1)
	name = "actId = %d and idx = %d" % (actId, idx)
	AutoLog.LogBase(role.GetRoleID(), AutoLog.eveNAHalloween, name)
	#回调客户端
	role.CallBackFunction(backFunId, (actId, idx))
	global RIGHT_ACTID_LIST
	if actId in RIGHT_ACTID_LIST:
		HalloweenOpenMainPanel(role)
	#提示
	role.Msg(2, 0, rewardPrompt)
#===============================================================================
# 事件
#===============================================================================
def OnRoleInit(role, param):
	'''
	角色初始化
	@param role:
	@param param:
	'''
	if not role.GetTempObj(EnumTempObj.HalloweenNAMgr):
		role.SetTempObj(EnumTempObj.HalloweenNAMgr, HalloweenNABase.HalloweenMgr(role))
		
def OnSyncRoleOtherData(role, param):
	'''
	角色登陆同步其它数据
	@param role:
	@param param:
	'''
	#版本判断
	if not Environment.EnvIsNA():
		return
	
	HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
	if not HalloweenNAMgr:
		role.SetTempObj(EnumTempObj.HalloweenNAMgr, HalloweenNABase.HalloweenMgr(role))
		HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
	
	#同步客户端正在开启的活动
	role.SendObj(NA_Halloween_Sync_StartingAct, HalloweenNAConfig.HALLOWEENNA_STARING_SET)
	
def OnRoleLogin(role, param):
	'''
	角色登陆
	@param role:
	@param param:
	'''
	HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
	HalloweenNAMgr.UpdateVersion()
	#判断是否在线奖励活动
	actId = 9
	STARTING_LIST = HalloweenNAConfig.HALLOWEENNA_STARING_SET
	if actId in STARTING_LIST:
		HalloweenNAMgr.online_reward_tick_id = role.RegTick(60, OnlineReward)
	#判断玩家登录的时候是否开启了祝福活动
	for actId in HalloweenNADefine.BLESS_ACTID_LIST:
		if actId in STARTING_LIST:
			HalloweenNAMgr.Blessing()
			break
	#同步客户端正在开启的活动
	role.SendObj(NA_Halloween_Sync_StartingAct, HalloweenNAConfig.HALLOWEENNA_STARING_SET)
	
def AfterLevelUp(role, param):
	if role.GetLevel() == 30:
		for actId in HalloweenNADefine.BLESS_ACTID_LIST:
			if actId in HalloweenNAConfig.HALLOWEENNA_STARING_SET:
				HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
				HalloweenNAMgr.Blessing()
				return
		
def OnChangeUnbindRMB_Q(role, param):
	'''
	神石改变
	@param role:
	@param param:
	'''
	oldValue, newValue = param
	
	if newValue > oldValue:
		#充值
		
		#增加的充值
		incRMB = newValue - oldValue
		
		#版本判断
		if Environment.EnvIsNA():
			#北美万圣节
			HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
			#增加今日充值神石数量
			HalloweenNAMgr.inc_buy_unbind_rmb(incRMB)
			#首充
			HalloweenNAMgr.first_pay()
	else:
		#消费
		#版本判断
		if Environment.EnvIsNA():
			#北美万圣节
			HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
			#首充
			HalloweenNAMgr.day_first_consume()
			#一次性消费
			HalloweenNAMgr.OneTimeCost(oldValue - newValue)
			#每日累计消费
			HalloweenNAMgr.TotalCostRMB(oldValue - newValue)
			
def OnChangeUnbindRMB_S(role, param):
	'''
	神石改变
	@param role:
	@param param:
	'''
	oldValue, newValue = param
	
	#消费
	if newValue < oldValue:
		#版本判断
		if Environment.EnvIsNA():
			#北美万圣节
			HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
			#首充
			HalloweenNAMgr.day_first_consume()
			#一次性消费
			HalloweenNAMgr.OneTimeCost(oldValue - newValue)
			#每日累计消费
			HalloweenNAMgr.TotalCostRMB(oldValue - newValue)
			
def OnRoleDayClear(role, param):
	'''
	每日清理
	@param role:
	@param param:
	'''
	#版本判断
	if not Environment.EnvIsNA():
		return
	
	HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
	if not HalloweenNAMgr:
		role.SetTempObj(EnumTempObj.HalloweenNAMgr, HalloweenNABase.HalloweenMgr(role))
		HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
		
	#每日首笔消费
	for actId in HalloweenNADefine.DAY_COST_ACTID_LIST:
		if actId in HalloweenNAMgr.reward_status_dict:
			del HalloweenNAMgr.reward_status_dict[actId]
	HalloweenNAMgr.is_first_consume = False
		
	#心魔挑战
	for actId in HalloweenNADefine.PURGATORYPASS_ACTID_LIST:
		if actId in HalloweenNAMgr.reward_status_dict:
			del HalloweenNAMgr.reward_status_dict[actId]
			
	#挑战组队副本
	for actId in HalloweenNADefine.GVEFB_ACTID_LIST:
		if actId in HalloweenNAMgr.reward_status_dict:
			del HalloweenNAMgr.reward_status_dict[actId]
	
	#挑战竞技场
	for actId in HalloweenNADefine.JJC_ACTID_LIST:
		if actId in HalloweenNAMgr.reward_status_dict:
			del HalloweenNAMgr.reward_status_dict[actId]
	HalloweenNAMgr.jjc_cnt = 0
		
	#挑战副本
	for actId in HalloweenNADefine.FB_ACTID_LIST:
		if actId in HalloweenNAMgr.reward_status_dict:
			del HalloweenNAMgr.reward_status_dict[actId]
			
	#挑战公会副本
	for actId in HalloweenNADefine.UNION_FB_ACTID_LIST:
		if actId in HalloweenNAMgr.reward_status_dict:
			del HalloweenNAMgr.reward_status_dict[actId]
	HalloweenNAMgr.union_fb_cnt = 0
	
	#勇斗领主
	actId = 8
	if actId in HalloweenNAMgr.reward_status_dict:
		del HalloweenNAMgr.reward_status_dict[actId]
	
	#点石成金
	actId = 13
	if actId in HalloweenNAMgr.reward_status_dict:
		del HalloweenNAMgr.reward_status_dict[actId]
		
	#每日在线奖励
	actId = 9
	if actId in HalloweenNAMgr.reward_status_dict:
		del HalloweenNAMgr.reward_status_dict[actId]
	#祝福
	for actId in HalloweenNADefine.BLESS_ACTID_LIST:
		if actId in HalloweenNAMgr.reward_status_dict:
			del HalloweenNAMgr.reward_status_dict[actId]
	for actId in HalloweenNADefine.BLESS_ACTID_LIST:
		if HalloweenNAMgr.is_active(actId):
			HalloweenNAMgr.Blessing()
			break
	#解救奴隶
	actId = 17
	if actId in HalloweenNAMgr.reward_status_dict:
		del HalloweenNAMgr.reward_status_dict[actId]
	HalloweenNAMgr.slave_cnt = 0
	#恶魔深渊
	for actId in HalloweenNADefine.EVILHOLE_ACTID_LIST:
		if actId in HalloweenNAMgr.reward_status_dict:
			del HalloweenNAMgr.reward_status_dict[actId]
	HalloweenNAMgr.EvilHole_times = 0
	#宠物培养
	actId = 21
	if actId in HalloweenNAMgr.reward_status_dict:
		del HalloweenNAMgr.reward_status_dict[actId]
	HalloweenNAMgr.Petevl_times = 0
	#坐骑养成
	actId = 23
	if actId in HalloweenNAMgr.reward_status_dict:
		del HalloweenNAMgr.reward_status_dict[actId]
	HalloweenNAMgr.mount_train_cnt = 0
	HalloweenNAMgr.mount_rmb_train_cnt = 0
		
	#抓捕奴隶
	actId = 24
	if actId in HalloweenNAMgr.reward_status_dict:
		del HalloweenNAMgr.reward_status_dict[actId]
	HalloweenNAMgr.catch_slave_cnt = 0
	
	#英灵勇士2
	actId = 25
	if actId in HalloweenNAMgr.reward_status_dict:
		del HalloweenNAMgr.reward_status_dict[actId]
	
	#每日累计消费
#	actId = 26
#	if actId in HalloweenNAMgr.reward_status_dict:
#		del HalloweenNAMgr.reward_status_dict[actId]
#	HalloweenNAMgr.total_cost_RMB = 0
	#宠物转盘
	actId = 28
	if actId in HalloweenNAMgr.reward_status_dict:
		del HalloweenNAMgr.reward_status_dict[actId]
	#装备强化
	actId = 29
	if actId in HalloweenNAMgr.reward_status_dict:
		del HalloweenNAMgr.reward_status_dict[actId]
	HalloweenNAMgr.equipment_streng_cnt = 0
	#占卜天天乐
	actId = 32
	if actId in HalloweenNAMgr.reward_status_dict:
		del HalloweenNAMgr.reward_status_dict[actId]
	HalloweenNAMgr.tarot_cnt_dict = {}
	#占卜大家乐
	actId = 33
	if actId in HalloweenNAMgr.reward_status_dict:
		del HalloweenNAMgr.reward_status_dict[actId]
	HalloweenNAMgr.tarot_cnt = 0
	#宝石合成每日
	actId = 34
	if actId in HalloweenNAMgr.reward_status_dict:
		del HalloweenNAMgr.reward_status_dict[actId]
	HalloweenNAMgr.gem_day_syn_dict = {}
	#每日购买宝石
	actId = 35
	if actId in HalloweenNAMgr.reward_status_dict:
		del HalloweenNAMgr.reward_status_dict[actId]	
	HalloweenNAMgr.buy_gem_day_cnt = 0
	
	HalloweenNAMgr.online_time = 0

def OnRoleSave(role, param):
	'''
	角色保存
	@param role:
	@param param:
	'''
	HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
	HalloweenNAMgr.save()
	
#===============================================================================
# 客户端请求
#===============================================================================
def RequestNAHalloweenOpenMainPanel(role, msg):
	'''
	客户端请求打开北美万圣节面板
	@param role:
	@param msg:
	'''
	HalloweenOpenMainPanel(role)
	
def RequestNAHalloweenGetReward(role, msg):
	'''
	客户端请求领取北美万圣节奖励
	@param role:
	@param msg:
	'''
	backFunId, data = msg
	actId, idx = data
	
	if role.GetLevel() < SEVEN_ACT_NEED_LEVEL:
		return
	#日志
	with TraHalloweenNAReward:
		HalloweenGetReward(role, actId, idx, backFunId)

	
def CallAfterNewDay():
	HalloweenNAConfig.InitIsActive()
	actId = 9
	roleList = cRoleMgr.GetAllRole()
	for role in roleList:
		ClearDataForActIds(role)
		#同步客户端正在开启的活动
		STARTING_LIST = HalloweenNAConfig.HALLOWEENNA_STARING_SET
		role.SendObj(NA_Halloween_Sync_StartingAct, STARTING_LIST)
		
		HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
		#下面主要是做每日在线处理
		if actId not in STARTING_LIST:
			continue

		if HalloweenNAMgr.online_reward_tick_id:
			continue
		HalloweenNAMgr.online_reward_tick_id = role.RegTick(60, OnlineReward)

def ClearDataForActIds(role):
	#为一些活动做数据清理
	#开启中的活动
	STARTING_LIST = HalloweenNAConfig.HALLOWEENNA_STARING_SET
	HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
	#首充
	first_state = False
	for actId in HalloweenNADefine.FIRST_PAY_ACTID_LIST:
		if actId in STARTING_LIST:
			first_state = True
			break
	if not first_state:
		for actId in HalloweenNADefine.FIRST_PAY_ACTID_LIST:
			HalloweenNAMgr.reward_status_dict[actId] = {}
		if HalloweenNAMgr.is_first_pay == True:
			HalloweenNAMgr.is_first_pay = False
			
	#累计消费
	total_state = False
	for actId in HalloweenNADefine.TOTAL_COST_ACTID_LIST:
		if actId in STARTING_LIST:
			total_state = True
			break
	if not total_state:
		for actId in HalloweenNADefine.TOTAL_COST_ACTID_LIST:
			HalloweenNAMgr.reward_status_dict[actId] = {}
		if HalloweenNAMgr.total_cost_RMB != 0:
			HalloweenNAMgr.total_cost_RMB = 0
			
	#派对
	party_state = False
	for actId in HalloweenNADefine.PARTY_ACTID_LIST:
		if actId in STARTING_LIST:
			party_state = True
			break
	if not party_state:
		for actId in HalloweenNADefine.PARTY_ACTID_LIST:
			HalloweenNAMgr.reward_status_dict[actId] = {}
		HalloweenNAMgr.party_times_dict = {}
			
	#婚礼
	marry_state = False
	for actId in HalloweenNADefine.MARRY_ACTID_LIST:
		if actId in STARTING_LIST:
			marry_state = True
			break
	if not marry_state:
		for actId in HalloweenNADefine.MARRY_ACTID_LIST:
			HalloweenNAMgr.reward_status_dict[actId] = {}
	#情缘副本
	couplesfb_state = False
	for actId in HalloweenNADefine.COUPLESFB_ACTID_LIST:
		if actId in STARTING_LIST:
			couplesfb_state = True
			break
	if not couplesfb_state:
		for actId in HalloweenNADefine.COUPLESFB_ACTID_LIST:
			HalloweenNAMgr.reward_status_dict[actId] = {}
		HalloweenNAMgr.couples_fb_times = 0
		
def OnlineReward(role, callargv, regparam):
	if role.IsKick():
		return
	actId = 9
	if actId not in HalloweenNAConfig.HALLOWEENNA_STARING_SET:
		return
	HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
	HalloweenNAMgr.online_reward_tick_id = role.RegTick(60, OnlineReward)
	HalloweenNAMgr.online_reward()
	
	
#===========================================================================
def ResetDB(Nowversion):
	#重置数据
	global HalloweenNaDict
	
	version = HalloweenNaDict.setdefault('version', 0)
	if not version or version != Nowversion:
		HalloweenNaDict.clear()
		HalloweenNaDict['version'] = Nowversion
		HalloweenNaDict.changeFlag = True
	
def HalloweenNaDictAfterLoadDB():
	pass
	
if "_HasLoad" not in dir():
	if Environment.HasLogic or Environment.HasWeb:
		HalloweenNaDict = Contain.Dict("HalloweenNaDict", (2038, 1, 1), HalloweenNaDictAfterLoadDB, isSaveBig = False)
		
	if Environment.HasLogic and not Environment.IsCross and (Environment.EnvIsNA() or Environment.IsDevelop):
		#角色初始化
		Event.RegEvent(Event.Eve_InitRolePyObj, OnRoleInit)
		Event.RegEvent(Event.Eve_AfterLogin, OnRoleLogin)
		#角色登陆同步其它数据
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		#角色神石改变
		Event.RegEvent(Event.AfterChangeUnbindRMB_Q, OnChangeUnbindRMB_Q)
		Event.RegEvent(Event.AfterChangeUnbindRMB_S, OnChangeUnbindRMB_S)
		#角色每日清理
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
		#角色保存
		Event.RegEvent(Event.Eve_BeforeSaveRole, OnRoleSave)
		Event.RegEvent(Event.Eve_AfterLevelUp, AfterLevelUp)
		#时间
		cComplexServer.RegAfterNewDayCallFunction(CallAfterNewDay)
		#日志
		TraHalloweenNAReward = AutoLog.AutoTransaction("TraHalloweenNAReward", "北美万圣节奖励(北美专属)")
		
		#注册消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NAHalloween_Open_Main_Panel", "客户端请求打开北美万圣节面板"), RequestNAHalloweenOpenMainPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NAHalloween_Get_Reward", "客户端请求领取北美万圣节奖励"), RequestNAHalloweenGetReward)
		