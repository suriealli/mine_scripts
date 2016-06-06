#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.KaiFuAct.KaiFuActMgr")
#===============================================================================
# 北美开服活动
#===============================================================================
import datetime
import cComplexServer
import cDateTime
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumSysData, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Activity.KaiFuAct import KaiFuActBase, KaiFuActConfig
from Game.Persistence import Contain
from Game.Role import Event
from Game.Role.Data import EnumTempObj, EnumInt16
from Game.SysData import WorldData
from Util import Time

if "_HasLoad" not in dir():
	
	MOUNT_EVOID_LIST = [21, 31, 41, 51, 61, 71]#各个阶数
	MOUNT_ACT_LIST = [14, 15]	#坐骑一起冲活动列表
	#一下为DB索引
	KAIFU_MOUNT_CNT = 1				#记录每个坐骑的阶数对应的人数
	#消息
	Kai_Fu_Act_Sync_All = AutoMessage.AllotMessage("Kai_Fu_Act_Sync_All", "通知客户端同步开服活动所有数据")
	Kai_Fu_Act_Icon_On = AutoMessage.AllotMessage("Kai_Fu_Act_Icon_On", "通知客户端开服活动图标出现")
	Kai_Fu_Act_Icon_Off = AutoMessage.AllotMessage("Kai_Fu_Act_Icon_Off", "通知客户端开服活动图标消失")

def IsIconOn():
	kaiFuDays = WorldData.GetWorldKaiFuDay()
	#遍历所有活动时间
	for actConfig in KaiFuActConfig.KAI_FU_ACT_BASE.itervalues():
		#判断活动时间
		if kaiFuDays >= actConfig.startDay and kaiFuDays <= actConfig.endDay:
			return True
		
	return False

def GetOverTimeSeconds(kaiFuDays, actConfig):
	kaiFuTime = WorldData.WD[EnumSysData.KaiFuKey]
	
	d1 = kaiFuTime + datetime.timedelta(days = actConfig.endDay - 1)
	
	overDateTime = datetime.datetime(d1.year, d1.month, d1.day, 23, 59)
	
	overSeconds = Time.DateTime2UnitTime(overDateTime)
	
	seconds = cDateTime.Seconds()
	if overSeconds < seconds:
		return 0
	
	return overSeconds - seconds

def KaiFuActOpenMainPanel(role):
	global KaifuActDict
	
	kaiFuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
	
	rewardStatusDict = {}	#奖励状态字典
	actOverTimeDict = {}	#活动结束剩余时间字典
	kaiFuDays = WorldData.GetWorldKaiFuDay()
	#遍历所有活动时间
	for actConfig in KaiFuActConfig.KAI_FU_ACT_BASE.itervalues():
		#判断活动时间(页签显示的时间)
		if kaiFuDays >= actConfig.startDay and kaiFuDays <= actConfig.tabEndDay:
			
			rewardStatusDict[actConfig.actId] = kaiFuActMgr.reward_status_dict.get(actConfig.actId, {})
			
			actOverTimeDict[actConfig.actId] = GetOverTimeSeconds(kaiFuDays, actConfig)
	
	mountDict = KaifuActDict.get(KAIFU_MOUNT_CNT)
	#奖励状态字典，累积消耗体力，在线时间，黄色命魂数量，新月长弓数量，新月战斧数量，4级符文购买数量，命魂等级达标数量，活动结束剩余时间字典,，
	#每日坐骑培养次数，各个阶段的坐骑数量，每日翅膀培养次数, 每日宠物培养次数
	role.SendObj(Kai_Fu_Act_Sync_All, (rewardStatusDict, kaiFuActMgr.tili, kaiFuActMgr.online_time, 
									kaiFuActMgr.yellow_tarot_cnt, kaiFuActMgr.xinyuechanggong, 
									kaiFuActMgr.xinyuezhanfu, kaiFuActMgr.rune_cnt, kaiFuActMgr.tarot_level_cnt, 
									actOverTimeDict, kaiFuActMgr.mount_train_cnt, mountDict, kaiFuActMgr.wing_train_cnt, 
									kaiFuActMgr.petcultivate_cnt))
	
	
def KaiFuActGetReward(role, actId, idx, backFunId):
	kaiFuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
	
	rewardConfig = KaiFuActConfig.KAI_FU_ACT_REWARD.get((actId, idx))
	if not rewardConfig:
		return
	
	if actId not in kaiFuActMgr.reward_status_dict:
		return
	rewardStatusDict = kaiFuActMgr.reward_status_dict[actId]
	if idx not in rewardStatusDict:
		return
	
	#是否可以领取
	if rewardStatusDict[idx] != 1:
		return
	
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
			
	#回调客户端
	role.CallBackFunction(backFunId, (actId, idx))
	
	#提示
	role.Msg(2, 0, rewardPrompt)
	
def CheckActState(actId):
	#检测指定活动是否开启
	config = KaiFuActConfig.KAI_FU_ACT_BASE.get(actId)
	if not config:
		return False
	kaiFuDays = WorldData.GetWorldKaiFuDay()
	if kaiFuDays < config.startDay or kaiFuDays > config.endDay:
		return False
	return True

def ChangeMountCntOnly(role):
	#这个函数只会在版本修复中执行一次
	global MOUNT_EVOID_LIST
	
	EvolveID = role.GetI16(EnumInt16.MountEvolveID)
	if EvolveID < MOUNT_EVOID_LIST[0]:
		return
	evoList = []	#保存玩家达到要求的阶数
	for evoId in MOUNT_EVOID_LIST:
		if evoId <= EvolveID:
			evoList.append(evoId)
	if evoList:
		AddMountCnt(evoList)
	
def CheckMountAct(syncRole = None):
	#检测坐骑一起冲活动
	global MOUNT_ACT_LIST
	#获取正在开启的坐骑一起冲
	rightActId = 0
	for actId in MOUNT_ACT_LIST:
		if CheckActState(actId) == True:
			rightActId = actId
			break
	if not rightActId : return
	
	#索引活动的奖励Id
	idxList = KaiFuActConfig.KAI_FU_ACT_ID_TO_IDX.get(rightActId)
	if not idxList:
		return
	
	global KaifuActDict
	
	mount_dict = KaifuActDict.get(KAIFU_MOUNT_CNT, {})
	can_reward = []#保存激活的奖励ID
	for idx in idxList:
		idxConfig = KaiFuActConfig.KAI_FU_ACT_REWARD.get((rightActId, idx))
		if not idxConfig:
			continue
		
		if idxConfig.needMountLevelCnt:
			evoId, cnt = idxConfig.needMountLevelCnt
			if mount_dict.get(evoId) < cnt:
				continue
			can_reward.append(idx)
		else:
			#这里直接返回是因为配置出错了
			continue
	if can_reward:#有激活的奖励
		if syncRole:
			kaiFuActMgr = syncRole.GetTempObj(EnumTempObj.KaiFuActMgr)
			if kaiFuActMgr:
				kaiFuActMgr.CheckMountCanReward(actId, can_reward)
		else:
			for crole in cRoleMgr.GetAllRole():
				kaiFuActMgr = crole.GetTempObj(EnumTempObj.KaiFuActMgr)
				if kaiFuActMgr:
					kaiFuActMgr.CheckMountCanReward(actId, can_reward)
		
def AddMountCnt(evoList):
	#增加某阶数的坐骑数量+1
	global KaifuActDict
	mount_dict = KaifuActDict.get(KAIFU_MOUNT_CNT, {})
	if type(evoList) == int:
		mount_dict[evoList] = mount_dict.get(evoList, 0) + 1
	else:
		for evoId in evoList:
			mount_dict[evoId] = mount_dict.get(evoId, 0) + 1
	KaifuActDict.changeFlag = True
	#检测是否激活了奖励
	CheckMountAct()
#===============================================================================
# 事件
#===============================================================================
def OnRoleInit(role, param):
	'''
	角色初始化
	@param role:
	@param param:
	'''
	if not role.GetTempObj(EnumTempObj.KaiFuActMgr):
		role.SetTempObj(EnumTempObj.KaiFuActMgr, KaiFuActBase.KaiFuActMgr(role))
	
def OnRoleLogin(role, param):
	'''
	角色登陆
	@param role:
	@param param:
	'''
	kaiFuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
	
	kaiFuDays = WorldData.GetWorldKaiFuDay()
	isNeedOnlineTick = False
	#判断是否在线奖励活动
	for actId in [5, 6]:
		#遍历所有活动时间
		actConfig = KaiFuActConfig.KAI_FU_ACT_BASE.get(actId)
		if not actConfig:
			continue
		
		#判断活动时间
		if kaiFuDays >= actConfig.startDay and kaiFuDays <= actConfig.endDay:
			isNeedOnlineTick = True
			break
		
	if isNeedOnlineTick is True:
		kaiFuActMgr.online_reward_tick_id = role.RegTick(60, OnlineReward)
	#培养羽翼活动开启
	if kaiFuActMgr.is_active(17):
		kaiFuActMgr.wing_train_level()
	#坐骑一起冲活动开启
	if kaiFuActMgr.is_active(14) or kaiFuActMgr.is_active(15):
		#检测是否激活了奖励
		CheckMountAct(role)
		
def OnSyncRoleOtherData(role, param):
	'''
	角色登陆同步其它数据
	@param role:
	@param param:
	'''
	#开服活动图标状态
	isIconOnFlag = IsIconOn()
	#图标状态
	if isIconOnFlag is True:
		role.SendObj(Kai_Fu_Act_Icon_On, None)
	else:
		role.SendObj(Kai_Fu_Act_Icon_Off, None)
	
def OnRoleSave(role, param):
	'''
	角色保存
	@param role:
	@param param:
	'''
	kaiFuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
	kaiFuActMgr.save()
	
def OnRoleDayClear(role, param):
	'''
	每日清理
	@param role:
	@param param:
	'''
	kaiFuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
	if not kaiFuActMgr:
		role.SetTempObj(EnumTempObj.KaiFuActMgr, KaiFuActBase.KaiFuActMgr(role))
		kaiFuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
		
	#体力大作战
	actId = 1
	if actId in kaiFuActMgr.reward_status_dict:
		del kaiFuActMgr.reward_status_dict[actId]
		kaiFuActMgr.tili = 0
		
	#每日必做积分奖励
	actId = 2
	if actId in kaiFuActMgr.reward_status_dict:
		del kaiFuActMgr.reward_status_dict[actId]
	
	#炼金奖励
	actId = 4
	if actId in kaiFuActMgr.reward_status_dict:
		del kaiFuActMgr.reward_status_dict[actId]
		
	#在线奖励
	actId = 5
	if actId in kaiFuActMgr.reward_status_dict:
		del kaiFuActMgr.reward_status_dict[actId]
		kaiFuActMgr.online_time = 0
	actId = 6
	if actId in kaiFuActMgr.reward_status_dict:
		del kaiFuActMgr.reward_status_dict[actId]
		kaiFuActMgr.online_time = 0
	
	#每日坐骑培养次数
	actId = 13
	if actId in kaiFuActMgr.reward_status_dict:
		del kaiFuActMgr.reward_status_dict[actId]
		kaiFuActMgr.mount_train_cnt = 0
	
	#每日羽翼培养次数
	actId = 16
	if actId in kaiFuActMgr.reward_status_dict:
		del kaiFuActMgr.reward_status_dict[actId]
		kaiFuActMgr.wing_train_cnt = 0
	
	#每日宠物培养
	actId = 19
	if actId in kaiFuActMgr.reward_status_dict:
		del kaiFuActMgr.reward_status_dict[actId]
		kaiFuActMgr.petcultivate_cnt = 0
		
def AfterChangeMountEvole(role, param):
	#玩家坐骑阶数改变事件
	_, newValue = param

	global MOUNT_EVOID_LIST
	
	minEvolve = 0
	#需要改动配置
	for evolveList in MOUNT_EVOID_LIST:
		if newValue == evolveList:
			minEvolve = evolveList
			break
	if not minEvolve:
		return
	AddMountCnt(minEvolve)
	
def AfterChangeVIP(role):
	kaiFuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
	if not kaiFuActMgr:
		return
	if kaiFuActMgr.is_active(14) or kaiFuActMgr.is_active(15):
		#检测是否激活了奖励
		CheckMountAct(role)


#===============================================================================
# 时间
#===============================================================================
def CallAfterNewDay():
	isIconOnFlag = IsIconOn()
	
	#是否在线奖励活动开始
	kaiFuDays = WorldData.GetWorldKaiFuDay()
	isNeedOnlineTick = False
	#判断是否在线奖励活动
	for actId in [5, 6]:
		actConfig = KaiFuActConfig.KAI_FU_ACT_BASE.get(actId)
		if not actConfig:
			continue
		#判断活动时间
		if kaiFuDays >= actConfig.startDay and kaiFuDays <= actConfig.endDay:
			isNeedOnlineTick = True
			break
	
	roleList = cRoleMgr.GetAllRole()
	for role in roleList:
		kaiFuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
		#图标状态
		if isIconOnFlag is True:
			role.SendObj(Kai_Fu_Act_Icon_On, None)
		else:
			role.SendObj(Kai_Fu_Act_Icon_Off, None)
		
		#在线奖励
		if isNeedOnlineTick is True:
			if kaiFuActMgr.online_reward_tick_id:
				#取消tick
				role.UnregTick(kaiFuActMgr.online_reward_tick_id)
			
			kaiFuActMgr.online_reward_tick_id = role.RegTick(60, OnlineReward)
			
def OnlineReward(role, callargv, regparam):
	if role.IsKick():
		return
	kaiFuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
	kaiFuActMgr.online_reward_tick_id = role.RegTick(60, OnlineReward)
	
	kaiFuActMgr.online_reward1()
	kaiFuActMgr.online_reward2()
	
#===============================================================================
# 客户端请求
#===============================================================================
def RequestKaiFuActOpenMainPanel(role, msg):
	'''
	客户端请求打开开服活动主面板
	@param role:
	@param msg:
	'''
	KaiFuActOpenMainPanel(role)
	
def RequestKaiFuActGetReward(role, msg):
	'''
	客户端请求打开开服活动主面板
	@param role:
	@param msg:
	'''
	backFunId, data = msg
	
	actId, idx = data
	
	#日志
	with TraKaiFuActReward:
		KaiFuActGetReward(role, actId, idx, backFunId)

#========================================================
def KaifuActDictAfterLoadDB():
	global KAIFU_MOUNT_CNT
	global KaifuActDict
	
	if KAIFU_MOUNT_CNT not in KaifuActDict:
		KaifuActDict[KAIFU_MOUNT_CNT] = {}
		
if "_HasLoad" not in dir():
	if Environment.HasLogic or Environment.HasWeb:
		KaifuActDict = Contain.Dict("KaifuActDict", (2038, 1, 1), KaifuActDictAfterLoadDB, isSaveBig = False)
		
	if Environment.HasLogic and (Environment.EnvIsNA() or Environment.IsDevelop) and not Environment.IsCross:
		#角色初始化
		Event.RegEvent(Event.Eve_InitRolePyObj, OnRoleInit)
		#角色登录
		Event.RegEvent(Event.Eve_AfterLogin, OnRoleLogin)
		#角色登陆同步其它数据
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		#角色保存
		Event.RegEvent(Event.Eve_BeforeSaveRole, OnRoleSave)
		#角色每日清理
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
		#玩家坐骑阶数改变
		Event.RegEvent(Event.Eve_AfterMountEvolve, AfterChangeMountEvole)
		#时间
		cComplexServer.RegAfterNewDayCallFunction(CallAfterNewDay)
		#日志
		TraKaiFuActReward = AutoLog.AutoTransaction("TraKaiFuActReward", "开服活动奖励(北美专属)")
		
		#注册消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Kai_Fu_Act_Open_Main_Panel", "客户端请求打开开服活动主面板"), RequestKaiFuActOpenMainPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Kai_Fu_Act_Get_Reward", "客户端请求领取开服活动奖励"), RequestKaiFuActGetReward)






