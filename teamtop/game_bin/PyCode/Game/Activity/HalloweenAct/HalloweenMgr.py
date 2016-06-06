#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.HalloweenAct.HalloweenMgr")
#===============================================================================
# 万圣节活动
#===============================================================================
import random
import Environment
import cRoleMgr
import cComplexServer
import cNetMessage
import cSceneMgr
import cDateTime
from ComplexServer.Log import AutoLog
from ComplexServer.Time import Cron
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from Game.Scene import PublicScene
from Game.Role import Event, Status
from Game.Role.Mail import Mail
from Game.Role.Data import EnumObj, EnumInt1, EnumDayInt8, EnumInt16
from Game.Activity import CircularDefine
from Game.Activity.HalloweenAct import HalloweenConfig

if "_HasLoad" not in dir():
	
	IS_START = False	#万圣节活动开启标志
	BANQUET_START = False#万圣节宴会开启标志
	
	TASK_ID = 0			#宴会的任务ID
	FRESH_TASK_TIME = 0	#记录刷新任务的时间
	TIKC_TIME = 600	#刷新时间
	TASK_APPERAED_LIST = set()	#已出现的任务
	
	SCENE_ID = 315	#宴会场景ID
	
	POS_X, POS_Y = 625,622
	#消息
	Halloween_collect_reward = AutoMessage.AllotMessage("Halloween_collect_reward", "通知客户端万圣节有收集奖励可以领取")
	Halloween_Fire_Work = AutoMessage.AllotMessage("Halloween_Fire_Work", "通知客户端万圣节播放烟花")
	Syn_CardBuff_Data = AutoMessage.AllotMessage("Syn_CardBuff_Data", "同步玩家变身卡buff信息")
	Syn_GetedReward_Data = AutoMessage.AllotMessage("Syn_GetedReward_Data", "同步玩家已完成的任务")
	Syn_GoingTask_Data = AutoMessage.AllotMessage("Syn_GoingTask_Data", "同步玩家正在进行的任务")
	Syn_CollectReward_Data = AutoMessage.AllotMessage("Syn_CollectReward_Data", "同步玩家已领取的收集奖励")
	Syn_CollectCard_Data = AutoMessage.AllotMessage("Syn_CollectCard_Data", "同步玩家已收集的变身卡")
	#日子
	HalloweenKillReward = AutoLog.AutoTransaction("HalloweenKillReward", "万圣节击杀鬼奖励")
	HalloweenCollectReward = AutoLog.AutoTransaction("HalloweenCollectReward", "万圣节击收集奖励")
	HalloweenlightReward = AutoLog.AutoTransaction("HalloweenlightReward", "万圣节击点灯奖励")
	HalloweenTaskReward = AutoLog.AutoTransaction("HalloweenTaskReward", "万圣节任务奖励奖励")
#================活动开启与关闭====================
def StartCircularActive(*param):
	_, activetype = param
	if activetype != CircularDefine.CA_Halloween:
		return
	global IS_START
	if IS_START:
		print "GE_EXC, NationalDayFB is already started "
		return
	IS_START = True
	
def EndCircularActive(*param):
	_, activetype = param
	if activetype != CircularDefine.CA_Halloween:
		return
	global IS_START
	if not IS_START:
		print "GE_EXC, NationalDayFB is already ended "
		return
	IS_START = False
#==============================================
def CheckCardLimit(role):
	#检测收集的身卡是否满足了收集条件
	canReward = []
	
	HalloweenData = role.GetObj(EnumObj.HalloweenData)
	collectData = HalloweenData.setdefault(1, {})
	getedReward = HalloweenData.setdefault(2, set())
	#遍历收集配置
	for rewardId, cfg in HalloweenConfig.COLLECT_CARD_DICT.iteritems():
		if rewardId in getedReward:
			continue
		isNo = False
		for card in cfg.needCard:
			if collectData.get(card[0], 0) < card[1]:
				isNo = True
				break
		if isNo:
			continue
		canReward.append(rewardId)
	if canReward:
		role.SendObj(Halloween_collect_reward, canReward)
		
	role.SendObj(Syn_CollectCard_Data, collectData)
	return canReward

def StartBanquet():
	#宴会开始
	global TASK_ID
	global TASK_APPERAED_LIST
	global BANQUET_START
	global FRESH_TASK_TIME
	global TIKC_TIME
	
	if not IS_START:
		return
	
	BANQUET_START = True
	#重新开始时清理下已出现任务
	TASK_APPERAED_LIST = set()
	#随机个任务，并加入已出现列表
	TastList = HalloweenConfig.TASK_REWARD_DICT.keys()
	TASK_ID = random.choice(TastList)
	TASK_APPERAED_LIST.add(TASK_ID)
	FRESH_TASK_TIME = int(cDateTime.Seconds())
	#同步给指定场景的玩家
	SynTask()
	#再次注册tick
	cComplexServer.RegTick(TIKC_TIME, ResetTask)
	
def EndBanquet():
	#宴会结束
	global TASK_ID
	global BANQUET_START
	global TASK_APPERAED_LIST
	global FRESH_TASK_TIME
	global SCENE_ID
	BANQUET_START = False
	TASK_ID = 0
	TASK_APPERAED_LIST = set()
	FRESH_TASK_TIME = 0
	
	#踢出场景内的玩家
	scene = cSceneMgr.SearchPublicScene(SCENE_ID)
	if not scene:
		return
	for crole in scene.GetAllRole():
		if not crole:
			continue
		crole.BackPublicScene()
		
def ResetTask(callargv, regparam):
	global TASK_APPERAED_LIST
	global TASK_ID
	global BANQUET_START
	global FRESH_TASK_TIME
	global TIKC_TIME
	
	if not BANQUET_START:#活动已关闭，直接返回
		return
	TastList = HalloweenConfig.TASK_REWARD_DICT.keys()
	newList = []
	for taskId in TastList:
		if taskId not in TASK_APPERAED_LIST:
			newList.append(taskId)
	if not newList:#任务已经全部循环完了
		return
	#再次随机并加入已出现列表
	TASK_ID = random.choice(newList)
	TASK_APPERAED_LIST.add(TASK_ID)
	FRESH_TASK_TIME = int(cDateTime.Seconds())
	#同步给指定场景的玩家
	SynTask()
	#再次注册tick
	cComplexServer.RegTick(TIKC_TIME, ResetTask)

def SynTask():
	#同步给在该场景的玩家
	scene = cSceneMgr.SearchPublicScene(SCENE_ID)
	if not scene:
		return
	for crole in scene.GetAllRole():
		if not crole:
			continue
		crole.SendObj(Syn_GoingTask_Data, (TASK_ID, FRESH_TASK_TIME))
	
def RoleDayClear(role, param):
	#清理当日已完成的任务
	HalloweenData = role.GetObj(EnumObj.HalloweenData)
	HalloweenData[3] = set()
	
def OnRoleClientLost(role, param):
	#角色客户端掉线
	global FB_SENCEID_LIST
	
	if role.GetSceneID() == SCENE_ID:
		role.BackPublicScene()
		
def AfterLogin(role, param):
	HalloweenData = role.GetObj(EnumObj.HalloweenData)
	buffData = HalloweenData.setdefault(4, {})
	#将之前的buff相关Tick删除
	HalloweenData[5] = {}
	nowTickData = HalloweenData.get(5, {})
	#注册新的buff到期时间
	nowTime = cDateTime.Seconds()
	for buffId, endTime in buffData.items():
		if endTime > nowTime:#未结束
			#注册到期时间
			nowTickData[buffId] = role.RegTick(int(endTime - nowTime), BuffEnd, buffId)
		else:#已经结束了，就删除
			del buffData[buffId]
	#玩家上次使用的buff还存在
	if role.GetI16(EnumInt16.RightBuffStatus) in buffData:
		role.SetAppStatus(role.GetI16(EnumInt16.RightBuffStatus))
	else:
		#重置万圣节正在使用的buff外形
		role.SetI16(EnumInt16.RightBuffStatus, 0)
		role.SetAppStatus(0)
	#同步客户端buff
	SynCardBuff(role)
	
	global IS_START
	if IS_START:#活动还开启的话
		#上线同步当日已完成的任务
		getedTaskReward = HalloweenData.setdefault(3, set())
		role.SendObj(Syn_GetedReward_Data, getedTaskReward)
		#检测是否有收集奖励可领取
		CheckCardLimit(role)

def SyncRoleOtherData(role, param):
	#同步客户端buff
	SynCardBuff(role)
	global IS_START
	if IS_START:#活动还开启的话
		HalloweenData = role.GetObj(EnumObj.HalloweenData)
		#上线同步次当日已完成的任务
		getedTaskReward = HalloweenData.setdefault(3, set())
		role.SendObj(Syn_GetedReward_Data, getedTaskReward)
		#发送已领取的收集奖励
		role.SendObj(Syn_CollectReward_Data, HalloweenData.get(2, set()))
		#检测是否有收集奖励可领取
		CheckCardLimit(role)
		
def SynCardBuff(role):
	#同步buff信息给客户端
	HalloweenData = role.GetObj(EnumObj.HalloweenData)
	buffData = HalloweenData.setdefault(4, {})
	#同步给客户端
	role.SendObj(Syn_CardBuff_Data, buffData)
	
def BuffEnd(role, callargv, regparam):
	buffId = regparam
	
	if buffId == role.GetI16(EnumInt16.RightBuffStatus):
		#玩家正使用的变身卡时间结束,变回原形
		role.SetI16(EnumInt16.RightBuffStatus, 0)
		role.SetAppStatus(0)
	#删除该buff的相关信息
	HalloweenData = role.GetObj(EnumObj.HalloweenData)
	buffData = HalloweenData.setdefault(4, {})
	tickData = HalloweenData.setdefault(5, {})
	if buffId in buffData:#删除数据
		del buffData[buffId]
	if buffId in tickData:#删除tick
		del tickData[buffId]
	#重算属性
	role.GetPropertyGather().ReSetRecountCardBuffFlag()
	#同步给客户端
	role.SendObj(Syn_CardBuff_Data, buffData)
#=================客户端请求======================
def RequestKillGhost(role, param):
	'''
	客户端请求打鬼
	@param role:
	@param param:
	'''
	killType, times = param	#killType为0是金币，1为神石

	if not IS_START:#活动未开启
		return
	
	level = role.GetLevel()
	if level < EnumGameConfig.HALLOWEEN_MIN_LEVEL:
		return
	
	levelKey = None
	for levelrange in HalloweenConfig.KILL_GHOST_DICT.keys():
		if levelrange[0] <= level <= levelrange[1]:
			levelKey = levelrange
			break
	if not levelKey:
		print "GE_EXC,can not find level(%s) in HalloweenConfig.KILL_GHOST_DICT"
		return
	cfg = HalloweenConfig.KILL_GHOST_DICT.get(levelKey)
	if not cfg:
		print "GE_EXC,has not cfg in HalloweenConfig.KILL_GHOST_DICT"
		return

	if killType:#神石击杀
		if role.GetUnbindRMB() < cfg.unBindRMB * times:
			return
	else:#金币击杀
		#已经没金币击杀次数
		if role.GetDI8(EnumDayInt8.HalloweenKillTimes) + times > cfg.killTimes:
			return
		if role.GetMoney() < cfg.gold * times:
			return
		
	if role.PackageEmptySize() < times:#背包不足
		role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
		return
		
	with HalloweenKillReward:
		if killType:
			role.DecUnbindRMB(cfg.unBindRMB * times)
		else:
			role.DecMoney(cfg.gold * times)
			role.IncDI8(EnumDayInt8.HalloweenKillTimes, times)
		
		tips = ""
		tips += GlobalPrompt.HallowKillMsg % times
		for _ in range(times):
			coding, cnt, _, isBro = cfg.RandomRate.RandomOne()
			#潜规则，coding小于100为命魂
			if coding <= 100:
				role.AddTarotCard(coding, cnt)
				tips += GlobalPrompt.Tarot_Tips % (coding, cnt)
			else:
				role.AddItem(coding, cnt)
				tips += GlobalPrompt.Item_Tips % (coding, cnt)
			if isBro:
				if coding > 100:
					cRoleMgr.Msg(11, 0, GlobalPrompt.HalloweenKillMsg % (role.GetRoleName(), coding, cnt))
				else:
					cRoleMgr.Msg(11, 0, GlobalPrompt.HalloweenKillMsg2 % (role.GetRoleName(), coding, cnt))
		role.Msg(2, 0, tips)
		
def RequestGetReward(role, param):
	'''
	客户端请求领取变身卡收集奖励
	@param role:
	@param param:
	'''
	rewardId = param
	
	if not IS_START:#活动未开启
		return
	
	cfg = HalloweenConfig.COLLECT_CARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC, can not find rewardId(%s) in HalloweenConfig.COLLECT_CARD_DICT" % rewardId
		return
	
	HalloweenData = role.GetObj(EnumObj.HalloweenData)
	collectData = HalloweenData.setdefault(1, {})
	getedReward = HalloweenData.setdefault(2, set())
	
	if cfg.rewardId in getedReward:#已领取过
		return
	if cfg.needCard:
		for needItem in cfg.needCard:
			if collectData.get(needItem[0], 0) < needItem[1]:
				return
	else:#没要求，那就是配置问题了
		return
	
	with HalloweenCollectReward:
		getedReward.add(cfg.rewardId)#将奖励ID加入已领取列表

		tips = GlobalPrompt.RUSH_LEVEL_GET_REWARD_PROMPT
		broTip = GlobalPrompt.HallowCollect % (role.GetRoleName())
		for reward in cfg.reward:
			role.AddItem(*reward)
			tips += GlobalPrompt.Item_Tips % (reward[0], reward[1])
			broTip += GlobalPrompt.HallowItemTips % (reward[0], reward[1])
		role.Msg(2, 0, tips)
		if cfg.IsBro:#需要广播
			cRoleMgr.Msg(11, 0, broTip)
		
		#发送已领取的收集奖励
		role.SendObj(Syn_CollectReward_Data, getedReward)
		
def RequestJoinScene(role, param):
	'''
	客户端请求进入宴会场景
	@param role:
	@param param:
	'''
	global TASK_ID
	global IS_START
	global BANQUET_START
	global FRESH_TASK_TIME

	if not IS_START:
		return
	if not BANQUET_START:
		return
	
	if role.GetLevel() < EnumGameConfig.HALLOWEEN_MIN_LEVEL:
		return
	
	#是否可以进入宴会状态
	if not Status.CanInStatus(role, EnumInt1.ST_Halloween):
		return
	
	role.Revive(SCENE_ID, POS_X, POS_Y)
	#发送任务相关信息
	role.SendObj(Syn_GoingTask_Data, (TASK_ID, FRESH_TASK_TIME))

def RequestOpenLight(role, param):
	'''
	客户端请求点灯
	@param role:
	@param param:
	'''
	index = param
	
	global IS_START
	global SCENE_ID
	
	if not IS_START:
		return
	if role.GetSceneID() != SCENE_ID:#玩家所在的场景不对
		return
	
	cfg = HalloweenConfig.OPEN_LIGHT_DICT.get(index)
	if not cfg:
		print "GE_EXC,can not find index(%s) in HalloweenConfig.OPEN_LIGHT_DICT" % index
		return
	
	if role.GetUnbindRMB() < cfg.unBindRMB:#神石不足
		return
	
	level = role.GetLevel()
	randomRate = None

	if cfg.LevelRang1[0] <= level <= cfg.LevelRang1[1]:
		randomRate = cfg.RandomRate1
	elif cfg.LevelRang2[0] <= level <= cfg.LevelRang2[1]:
		randomRate = cfg.RandomRate2
	
	if not randomRate:
		print "GE_EXC,HalloweenConfig.OPEN_LIGHT_DICT LevelRang Is Wrong "
		return
	
	with HalloweenlightReward:
		role.DecUnbindRMB(cfg.unBindRMB)
		
		reward = []
		for _ in xrange(cfg.times):
			coding, cnt, _, isBro = randomRate.RandomOne()
			reward.append([coding, cnt, isBro])
		itemDict = {}
		tarotDict = {}
		IsBroCoding = set()
		for rewardData in reward:
			coding, cnt, isBro = rewardData
			if coding < 100:
				tarotDict[coding] = tarotDict.get(coding, 0) + cnt
			else:
				itemDict[coding] = itemDict.get(coding, 0) + cnt
			if isBro:
				IsBroCoding.add(coding)
				
		tips = ""
		tips += GlobalPrompt.HalloweenLightMsg % (cfg.unBindRMB, cfg.times)
		for coding, cnt in itemDict.iteritems():
			role.AddItem(coding, cnt)
			tips += GlobalPrompt.Item_Tips % (coding, cnt)
			if coding in IsBroCoding:
				cRoleMgr.Msg(11, 0, GlobalPrompt.HallowFire % (role.GetRoleName(), coding, cnt))
		for tarotId, cnt in tarotDict.iteritems():
			role.AddTarotCard(tarotId, cnt)
			tips += GlobalPrompt.Tarot_Tips % (coding, cnt)
			cRoleMgr.Msg(11, 0, GlobalPrompt.HallowFire2 % (role.GetRoleName(), coding, cnt))
		
		role.Msg(2, 0, tips)

		scene = role.GetScene()
		if cfg.extendReward:#有额外道具，这是发给该场景所有玩家的
			#发全服公告
			item, cnt = cfg.extendReward[0], cfg.extendReward[1]
			cRoleMgr.Msg(11, 0, GlobalPrompt.HallowFireGlobal % (role.GetRoleName(), item, cnt))
			#给该场景的玩家发奖励
			for crole in scene.GetAllRole():
				if crole.PackageEmptySize() < 1:#空间不足发邮件
					Mail.SendMail(crole.GetRoleID(), GlobalPrompt.HallowMailTitle, GlobalPrompt.DUKE_MAIL_TITLE, \
								GlobalPrompt.HallowDesc % (role.GetRoleName(), item, cnt))
				else:
					crole.AddItem(item, cnt)
		cNetMessage.PackPyMsg(Halloween_Fire_Work, index)
		scene.BroadMsg()

def RequestGetTaskReward(role, param):
	'''
	客户端请求领取任务奖励
	@param role:
	@param param:
	'''
	taskId = param
	
	if role.GetSceneID() != SCENE_ID:#不在指定场景里
		return
	
	if not BANQUET_START:#没开启
		return
	
	if taskId != TASK_ID:#不是正在进行的任务
		return
	
	HalloweenData = role.GetObj(EnumObj.HalloweenData)
	getedTaskReward = HalloweenData.setdefault(3, set())
	
	if taskId in getedTaskReward:#该任务当天已完成过
		return
	
	if role.PackageIsFull():#背包已满
		role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
		return
	
	cfg = HalloweenConfig.TASK_REWARD_DICT.get(taskId)
	if not cfg:
		print "GE_EXC,can not find taskId(%s) in HalloweenConfig.TASK_REWARD_DICT" % taskId
		return
	
	if cfg.buffId:
		if role.GetAppStatus() != cfg.buffId:#不是指定的buff状态
			role.Msg(2, 0, GlobalPrompt.HallowTaskMsg)
			return
	
	with HalloweenTaskReward:
		getedTaskReward.add(taskId) #加入已领取列表
		
		role.AddItem(*cfg.reward)
		role.Msg(2, 0, GlobalPrompt.Reward_Item_Tips % (cfg.reward[0], cfg.reward[1]))
		
		role.SendObj(Syn_GetedReward_Data, getedTaskReward)
		
def RequestBuffOperation(role, param):
	'''
	客户端请求开启/关闭buff
	@param role:
	@param param:
	'''
	state, buffId = param
	
	HalloweenData = role.GetObj(EnumObj.HalloweenData)
	buffData = HalloweenData.setdefault(4, {})
	
	if buffId not in buffData:#buff不存在
		return
	
	endTime = buffData.get(buffId, 0)
	if endTime <= cDateTime.Seconds():#buff时间已结束
		return
	
	if role.GetSceneID() == EnumGameConfig.MarrySceneID:
		role.Msg(2, 0, GlobalPrompt.HallowNotChange)
		return
	
	if state == 1:#开启
		role.SetI16(EnumInt16.RightBuffStatus, buffId)
		role.SetAppStatus(buffId)
	else:#关闭
		if buffId != role.GetAppStatus():#不是当前使用的buff
			return
		role.SetI16(EnumInt16.RightBuffStatus, 0)
		role.SetAppStatus(0)
		
def RequestExit(role, param):
	'''
	玩家请求退出副本
	@param role:
	@param param:
	'''
	if role.GetSceneID() != SCENE_ID:
		return
	role.BackPublicScene()
#================场景相关===================
@PublicScene.RegSceneAfterJoinRoleFun(SCENE_ID)
def AfterJoinScene(scene, role):
	#进入状态
	Status.ForceInStatus(role, EnumInt1.ST_Halloween)
	
@PublicScene.RegSceneBeforeLeaveFun(SCENE_ID)
def BeforeLeaveScene(scene, role):
	#退出状态
	Status.Outstatus(role, EnumInt1.ST_Halloween)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, StartCircularActive)
		Event.RegEvent(Event.Eve_EndCircularActive, EndCircularActive)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		Event.RegEvent(Event.Eve_ClientLost, OnRoleClientLost)
		#北美多开一场
		if Environment.EnvIsNA():
			Cron.CronDriveByMinute((2038, 1, 1), StartBanquet, H = "H == 13", M = "M == 30")
			Cron.CronDriveByMinute((2038, 1, 1), EndBanquet, H = "H == 14", M = "M == 30")
			
		Cron.CronDriveByMinute((2038, 1, 1), StartBanquet, H = "H == 18", M = "M == 30")
		Cron.CronDriveByMinute((2038, 1, 1), EndBanquet, H = "H == 19", M = "M == 30")
			
	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Halloween_Kill_Ghost", "客户端请求打鬼"), RequestKillGhost)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Halloween_Get_Reward", "客户端请求领取变身卡收集奖励"), RequestGetReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Halloween_Join_Scene", "客户端请求进入宴会场景"), RequestJoinScene)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Halloween_Open_Light", "客户端请求点灯"), RequestOpenLight)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Halloween_Get_TaskReward", "客户端请求领取任务奖励"), RequestGetTaskReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Halloween_Buff_Operation", "客户端请求开启/关闭buff"), RequestBuffOperation)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Halloween_Exit", "客户端请求退出万圣节宴会"), RequestExit)
		