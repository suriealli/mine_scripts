#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DragonTreasure.DragonTreasure")
#===============================================================================
# 巨龙宝藏
#===============================================================================
import copy
import random
import Environment
import cRoleMgr
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig, EnumFightStatistics
from ComplexServer.Log import AutoLog
from Game.Activity.DragonTreasure import DragonTreasureConfig, DragonTreasureDefine
from Game.DailyDo import DailyDo
from Game.Fight import Fight
from Game.Role import Event, Status
from Game.Role.Data import EnumDayInt8, EnumObj, EnumDayInt1, EnumInt1
from Game.ThirdParty.QQidip import QQEventDefine
from Game.VIP import VIPConfig


if "_HasLoad" not in dir():
	
	DRAGON_TIMES_IDX = 1	#持久化字典寻宝次数索引
	
	PERCIOUS_ITEM_INFO = [] #用于保存玩家挖宝获得珍贵道具

	CallBackSec = 120
	#消息
	Fresh_scene_for_client = AutoMessage.AllotMessage("Fresh_scene_for_client", "同步刷新后的场景")
	Fresh_event_for_client = AutoMessage.AllotMessage("Fresh_event_for_client", "同步特殊事件")
	Dig_CallBack_For_client = AutoMessage.AllotMessage("Dig_CallBack_For_client", "巨龙宝藏挖宝回调")
	Fresh_Precious_for_client = AutoMessage.AllotMessage("Fresh_Precious_for_client", "同步巨龙宝藏获取珍贵道具的玩家和道具信息")
	Fresh_GetItem_for_client = AutoMessage.AllotMessage("Fresh_GetItem_for_client", "同步已获取的挖宝奖励ID列表")
	Luck_Fresh_scene_for_client = AutoMessage.AllotMessage("Luck_Fresh_scene_for_client", "幸运挖矿新增的场景")
	Dragon_Treasure_Fight = AutoMessage.AllotMessage("Dragon_Treasure_Fight", "挖宝触发战斗")
	#日志
	DragonTreasureReward = AutoLog.AutoTransaction("DragonTreasureReward", "巨龙宝藏寻宝奖励")
	DragonTreasureEvent = AutoLog.AutoTransaction("DragonTreasureEvent", "巨龙宝藏特殊事件奖励")
	DragonTreasureDig = AutoLog.AutoTransaction("DragonTreasureDig", "巨龙宝藏挖宝奖励")
	DragonTreasureBuyDig = AutoLog.AutoTransaction("DragonTreasureBuyDig", "巨龙宝藏购买普通挖宝消费")
	DragonTreasureBuyLuckyDig = AutoLog.AutoTransaction("DragonTreasureBuyLuckyDig", "巨龙宝藏购买幸运挖宝消费")
	
def JudgeEvent(role, sceneId):
	'''
	根据给的场景Id判断玩家是否触发特殊事件
	@param sceneId:
	'''
	#获取玩家的特殊事件
	dragonTreasure_obj = role.GetObj(EnumObj.Dragon_Treasure)
	event_list = dragonTreasure_obj.get(2)
	if not event_list:#无特殊触发事件
		#根据场景ID获取新的事件
		event_id = DragonTreasureConfig.GetcfgBySceneId(sceneId)
		if not event_id:
			print "GE_EXC,can not find eventId by sceneId=(%s) in DragonTreasure48" % sceneId
			return
		dragonTreasure_obj[2] = [event_id,sceneId]
		role.SendObj(Fresh_event_for_client, [event_id, 0])
	else:
		event_id = event_list[0]
		#根据事件ID获取各各场景
		cfg = DragonTreasureConfig.DRAGON_EVENT_DICT.get(event_id)
		if not cfg:
			print "GE_EXC,can not find DragonEvent 57by eventId(%s)" % event_id
			return
		#获取玩家已经触发的场景id
		now_scene = event_list[1]
		#根据已触发的场景ID获取配置中下个该触发的场景ID
		next_scene, index = DragonTreasureConfig.GetNextSceneByScene(event_id, now_scene)
		if not next_scene or not index:
			return
		if next_scene == sceneId:
			if index == 2:#特殊事件完成
				#重置特殊事件
				dragonTreasure_obj[2] = []	
				with DragonTreasureEvent:
					if cfg.reward:
						role.IncDI8(EnumDayInt8.GoldenkeyNumber, cfg.reward)				
				role.SendObj(Fresh_event_for_client, [])
			elif index == 1:#还有下个场景
				dragonTreasure_obj[2] = [event_id,sceneId]
				role.SendObj(Fresh_event_for_client, [event_id, 1])
		else:#下个触发的场景不是当前场景，做重置处理
			#根据场景ID获取新的事件
			event_id = DragonTreasureConfig.GetcfgBySceneId(sceneId)
			dragonTreasure_obj[2] = [event_id,sceneId]
			role.SendObj(Fresh_event_for_client, [event_id, 0])
	
def JudgeFinishEvent(role, sceneId):			
	'''
	判断是否完成特殊事件
	@param sceneId:
	'''
	#获取玩家的特殊事件
	dragonTreasure_obj = role.GetObj(EnumObj.Dragon_Treasure)
	if not dragonTreasure_obj:
		print "GE_EXC, the roleId=(%s) can not find EnumObj.Dragon_Treasure121" % role.GetRoleID()
		return
	event_list = dragonTreasure_obj.get(2)
	if not event_list:
		return False
	else:
		event_id = event_list[0]
		#根据事件ID获取各各场景
		cfg = DragonTreasureConfig.DRAGON_EVENT_DICT.get(event_id)
		if not cfg:
			print "GE_EXC,can not find DragonEvent 100by eventId(%s)" % event_id
			return False
		#获取玩家已经触发的场景id
		now_scene = event_list[1]
		#根据已触发的场景ID获取配置中下个该触发的场景ID
		next_scene, index = DragonTreasureConfig.GetNextSceneByScene(event_id, now_scene)
		if next_scene == sceneId:
			if index == 2:#特殊事件完成
				return True
		return False
	
def FreshSecne(role, auto = 0):
	'''
	刷新场景id,3个不一样的场景
	'''
	selected_list = random.sample(range(1, DragonTreasureDefine.MAX_SCENE_NUM+1), 3)
	#记录到玩家身上
	dragonTreasure_obj = role.GetObj(EnumObj.Dragon_Treasure)
	dragonTreasure_obj[1] = selected_list
	if dragonTreasure_obj.has_key(4):
		dragonTreasure_obj[4] = []
	#将刷新后的场景发给客户端
	role.SendObj(Fresh_scene_for_client, selected_list)

def FreshSecneNew(role, scene):
	'''
	随机出3个不是已有的场景
	@param role:
	@param scene:
	'''
	scene_list = DragonTreasureConfig.SCENE_ID_LIST
	new_list = []
	for sceneId in scene_list:
		if sceneId not in scene:
			new_list.append(sceneId)
	selected_list = random.sample(new_list, 3)
	dragonTreasure_obj = role.GetObj(EnumObj.Dragon_Treasure)
	dragonTreasure_obj[4] = selected_list
	#将幸运挖矿的3个场景发给客户端
	role.SendObj(Luck_Fresh_scene_for_client, selected_list)
		
def RandomReward(role):
	'''
	#随机一个未获得过的奖励
	@param role:
	'''
	rewardId= DragonTreasureConfig.GetRandomOne(role)
	cfg = DragonTreasureConfig.DRAGON_REWARD_DICT.get(rewardId)
	if not cfg:
		print "GE_EXC,can not find rewardId=(%s) in DragonRrward149" % rewardId
		return
	return cfg,rewardId	

def OnBackFight(role, callargv, regparam):
	backboll = callargv
	if not backboll:
		return
	else:
		#判断玩家是否能进战斗状态
		if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
			return
		cfg, event_type = regparam
		FightPvE(role, cfg, event_type)
		
def FightPvE(role, cfg, event_type):
	tmpCfg = copy.copy(cfg)
	#YY防沉迷对奖励特殊处理,在创建战斗时就处理好了奖励
	yyAntiFlag = role.GetAnti()
	if yyAntiFlag == 1:#收益减半
		tmpCfg.RMB = tmpCfg.RMB_fcm
		tmpCfg.cnt = tmpCfg.cnt_fcm
	elif yyAntiFlag == 0:#原有收益
		pass
	else:
		tmpCfg.RMB = 0
		tmpCfg.cnt = 0
		
	fight = Fight.Fight(tmpCfg.fightType)
	fight.restore = True
	left_camp, right_camp = fight.create_camp()
	left_camp.create_online_role_unit(role, role.GetRoleID())
	right_camp.create_monster_camp_unit(tmpCfg.mci)
	fight.on_leave_fun = None			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	fight.after_fight_param = tmpCfg
	fight.after_play_param = tmpCfg
	fight.start()

def AfterFight(fight):
	#回调触发
	if fight.result != 1:
		return
	roles = fight.left_camp.roles
	if not roles:
		return
	role = list(roles)[0]
	cfg = fight.after_fight_param
	BindRMB, coding, cnt = cfg.RMB, cfg.item, cfg.cnt
	roleId = role.GetRoleID()
	fight.set_fight_statistics(roleId, EnumFightStatistics.EnumBindRMB, BindRMB)
	fight.set_fight_statistics(roleId, EnumFightStatistics.EnumItems, [(coding, cnt)])
	
def AfterPlay(fight):
	#战斗回调
	cfg = fight.after_play_param
	if fight.result == 1:
		for role in fight.left_camp.roles:
			#YY防沉迷无奖励提示
			if not cfg.RMB and not cfg.cnt:
				role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
				continue
			#日志
			with DragonTreasureReward:
				if cfg.RMB:
					role.IncBindRMB(cfg.RMB)
					role.Msg(2, 0, GlobalPrompt.DRAGON_REWARD_MSG1 % cfg.RMB)
				if cfg.item and cfg.cnt:
					role.AddItem(cfg.item, cfg.cnt)
					role.Msg(2, 0, GlobalPrompt.DRAGON_REWARD_MSG6 % (cfg.item, cfg.cnt))	
	elif fight.result == -1:
		print "right win"
	else:
		print "all lost"
#========================================================	
def RequestDragonSearch(role, msg):
	'''
	客户端请求寻宝
	@param role:
	@param msg:
	'''
	sceneId = msg
	#玩家等级不足
	if role.GetLevel() < DragonTreasureDefine.LIMIT_LEVEL:
		return
	dragonTreasure_obj = role.GetObj(EnumObj.Dragon_Treasure)
	if sceneId not in dragonTreasure_obj.get(1, []) and sceneId not in dragonTreasure_obj.get(4, []):
		return
	#事先判断玩家是否能进战斗状态，以防出现玩家点击战斗而无法进入战斗的问题
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	#触发事件
	event_type = DragonTreasureConfig.RANDOM.RandomOne()
	level = role.GetLevel()
	cfg = DragonTreasureConfig.GetEventByType(event_type, level)
	if not cfg:
		print "GE_EXC,can not find eventtype(%s) and level(%s) in DragonDigEvent" % (event_type, level)
		return
	#获取玩家已寻宝次数
	serched_times = role.GetDI8(EnumDayInt8.SerachDrgonTimes)
	if serched_times >= EnumGameConfig.SEARCH_MAX_TIMES:
		#获取玩家奖励得到的挖宝次数
		reward_times = role.GetDI8(EnumDayInt8.SerachDrgonTimesReward)
		if not reward_times:
			if role.GetDI8(EnumDayInt8.DragonCanDigTimes) > 0:
				role.DecDI8(EnumDayInt8.DragonCanDigTimes, 1)
			else:
				role.Msg(2, 0, GlobalPrompt.NO_TIMES_FOR_SECRCH_MSG)
				return
		else:
			role.DecDI8(EnumDayInt8.SerachDrgonTimesReward, 1)
	else:		
		role.IncDI8(EnumDayInt8.SerachDrgonTimes, 1)
		
	if cfg.mci and cfg.fightType:
		role.SendObjAndBack(Dragon_Treasure_Fight, cfg.EventId, CallBackSec, OnBackFight, [cfg, event_type] )
	else:
		with DragonTreasureReward:
			AddReward(role, cfg)
	#刷新界面场景
	FreshSecne(role)
	#判断玩家是否已触发了特殊事件
	JudgeEvent(role, sceneId)
	
	#每日必做 -- 挖宝
	Event.TriggerEvent(Event.Eve_DoDailyDo, role, (DailyDo.Daily_DT, 1))
	
	Event.TriggerEvent(Event.QQidip_Eve, role, QQEventDefine.QQ_DragonBaozang)
	
	#活跃度 -- 巨龙宝藏挖宝
	Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_DragonTreasure, 1))


def AddReward(role, cfg):
	#发奖
	#YY防沉迷对奖励特殊处理
	yyAntiFlag = role.GetAnti()
	if yyAntiFlag == 1:#收益减半
		tmpGold = cfg.Gold_fcm
		tmpRMB = cfg.RMB_fcm
		tmpCnt = cfg.cnt_fcm
	elif yyAntiFlag == 0:#原有收益
		tmpGold = cfg.Gold
		tmpRMB = cfg.RMB
		tmpCnt = cfg.cnt
	else:
		role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
		return 
	
	if tmpGold:
		role.IncMoney(tmpGold)
		role.Msg(2, 0, GlobalPrompt.DRAGON_REWARD_MSG3 % tmpGold)
	if tmpRMB:
		role.IncBindRMB(tmpRMB)
		role.Msg(2, 0, GlobalPrompt.DRAGON_REWARD_MSG1 % tmpRMB)
	if cfg.times:
		role.IncDI8(EnumDayInt8.SerachDrgonTimesReward, 1)
		role.Msg(2, 0, GlobalPrompt.DRAGON_REWARD_MSG4)
	if cfg.Lucktimes:
		role.IncDI8(EnumDayInt8.LuckSerachDrgonTimesReward, 1)
		role.Msg(2, 0, GlobalPrompt.DRAGON_REWARD_MSG5)
	if cfg.item and tmpCnt:
		role.AddItem(cfg.item, tmpCnt)
		role.Msg(2, 0, GlobalPrompt.DRAGON_REWARD_MSG6 % (cfg.item, cfg.cnt))
	

def RequestDragonOpenWin(role, msg):
	'''
	客户端请求巨龙宝藏打开界面
	@param role:
	@param msg:
	'''
	#等级不足
	if role.GetLevel() < DragonTreasureDefine.LIMIT_LEVEL:
		return
	dragonTreasure_obj = role.GetObj(EnumObj.Dragon_Treasure)
	scene = dragonTreasure_obj.get(1)
	if not scene:
		FreshSecne(role)
		scene = dragonTreasure_obj.get(1)
	event = dragonTreasure_obj.get(2)
	if event:
		_, index = DragonTreasureConfig.GetNextSceneByScene(event[0], event[1])
		if index:
			#同步特殊事件
			role.SendObj(Fresh_event_for_client, [event[0], index-1])
	else:
		role.SendObj(Fresh_event_for_client, event)
	#同步刷新后的场景
	role.SendObj(Fresh_scene_for_client, scene)
	global PERCIOUS_ITEM_INFO
	#同步获得珍贵道具玩家信息
	role.SendObj(Fresh_Precious_for_client, PERCIOUS_ITEM_INFO)
	#同步玩家已获取的奖励信息
	dragonTreasure_obj = role.GetObj(EnumObj.Dragon_Treasure)
	role.SendObj(Fresh_GetItem_for_client, dragonTreasure_obj.get(3))
	role.SendObj(Luck_Fresh_scene_for_client, dragonTreasure_obj.get(4))
	
def RequestDragonDig(role, msg):
	'''
	客户端请求挖宝
	@param role:
	@param msg:
	'''
	#等级不足
	if role.GetLevel() < DragonTreasureDefine.LIMIT_LEVEL:
		return
	Goldedkeys = role.GetDI8(EnumDayInt8.GoldenkeyNumber)
	if not Goldedkeys:
		return
	dragonTreasure_obj = role.GetObj(EnumObj.Dragon_Treasure)
	getted_reward = dragonTreasure_obj.get(3)
	if len(getted_reward) >= 8:
		return
	cfg, rewardId = RandomReward(role)
	if not cfg or not rewardId:
		return
	if cfg.itemconfig and  cfg.cnt:
		#判断背包
		if role.PackageEmptySize() < 1:
			#提示
			role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
			return
	
	role.DecDI8(EnumDayInt8.GoldenkeyNumber, 1)
	#加入玩家已领取列表中
	#获取玩家已获得列表
	dragonTreasure_obj = role.GetObj(EnumObj.Dragon_Treasure)
	getted_item = dragonTreasure_obj.get(3)
	if not getted_item:
		dragonTreasure_obj[3] = [rewardId,]
	else:
		dragonTreasure_obj[3].append(rewardId)
	role.SendObjAndBack(Dig_CallBack_For_client, [rewardId], CallBackSec, CallBackPayReward, [cfg, rewardId])
	
def CallBackPayReward(role, callargv, regparam):
	'''
	挖宝回调
	@param role:
	@param callargv:
	@param regparam:
	'''
	cfg, rewardId = regparam
	itemCoding = cfg.itemconfig
	################################################
	#YY防沉迷对奖励特殊处理
	tmpCnt = 0
	tmpBindRMB = 0
	yyAntiFlag = role.GetAnti()
	if yyAntiFlag == 1:#收益减半
		tmpCnt = cfg.cnt_fcm
		tmpBindRMB = cfg.bindRMB_fcm
	elif yyAntiFlag == 0:#原有收益
		tmpCnt = cfg.cnt
		tmpBindRMB = cfg.bindRMB
	else:
		tmpCnt = 0
		tmpBindRMB = 0
		role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
	################################################
	with DragonTreasureDig:
		if itemCoding and tmpCnt:
			#奖励
			role.AddItem(itemCoding, tmpCnt)
			role.Msg(2, 0, GlobalPrompt.Reward_Item_Tips % (itemCoding, tmpCnt))
		if tmpBindRMB:
			role.IncBindRMB(tmpBindRMB)
		#检测是否要发世界公告
		cfg = DragonTreasureConfig.DRAGON_REWARD_DICT.get(rewardId)
		if not cfg:
			print "GE_EXC,can not find DragonReward by319 rewardId=(%s)" % rewardId
			return
		if cfg.public and tmpBindRMB:
			#各版本判断
			if Environment.EnvIsNA():
				if tmpBindRMB != 10 and tmpBindRMB != 30:
					cRoleMgr.Msg(3, 0, GlobalPrompt.DIG_REWARD_MSG % (role.GetRoleName(), tmpBindRMB))
			else:
				cRoleMgr.Msg(3, 0, GlobalPrompt.DIG_REWARD_MSG % (role.GetRoleName(), tmpBindRMB))
	
			global PERCIOUS_ITEM_INFO
			if len(PERCIOUS_ITEM_INFO) >= 6:
				del PERCIOUS_ITEM_INFO[0]
			PERCIOUS_ITEM_INFO.append((role.GetRoleName(), rewardId, yyAntiFlag))
			role.SendObj(Fresh_Precious_for_client, PERCIOUS_ITEM_INFO)
	#同步玩家已领取的奖励列表
	dragonTreasure_obj = role.GetObj(EnumObj.Dragon_Treasure)
	role.SendObj(Fresh_GetItem_for_client, dragonTreasure_obj.get(3))
	
def RequestDragonLuckDig(role, msg):
	'''
	客户端请求幸运寻宝
	@param role:
	@param msg:
	'''
	#等级不足
	if role.GetLevel() < DragonTreasureDefine.LIMIT_LEVEL:
		return
	dragonTreasure_obj = role.GetObj(EnumObj.Dragon_Treasure)
	if dragonTreasure_obj.get(4, []): 
		role.Msg(2, 0, GlobalPrompt.DRAGON_LUCKY_DIG_MSG)
		return
	#获取幸运寻宝次数
	LuckTimes = role.GetDI1(EnumDayInt1.LuckSerachDrgonTimes)
	if not LuckTimes:
		role.SetDI1(EnumDayInt1.LuckSerachDrgonTimes, 1)
	else:		
		rewards_times = role.GetDI8(EnumDayInt8.LuckSerachDrgonTimesReward)
		if not rewards_times:
			if role.GetDI8(EnumDayInt8.DragonCanLuckyDigTimes) > 0:
				role.DecDI8(EnumDayInt8.DragonCanLuckyDigTimes, 1)
			else:
				return
		else:
			role.DecDI8(EnumDayInt8.LuckSerachDrgonTimesReward, 1)
	#获取当前的三个场景
	scene = dragonTreasure_obj.get(1)
	FreshSecneNew(role, scene)
	
def RequestBuyDragonDigTimes(role, param):
	'''
	客户端请求购买寻宝次数
	@param role:
	@param param:
	'''
	vip = role.GetVIP()
	vipConfig = VIPConfig._VIP_BASE.get(vip)
	max_buy_cnt = 0
	#根据vip等级获取玩家可以购买的总次数
	if vipConfig:
		max_buy_cnt = vipConfig.DragonDigCnt
	if not max_buy_cnt: return

	DragonBuyDigTimes = role.GetDI8(EnumDayInt8.DragonBuyedDigTimes)
	if DragonBuyDigTimes >= max_buy_cnt:#无次数剩余
		return
	
	#根据购买的次数换算需要的神石
	cfg = DragonTreasureConfig.BUY_DIG_COST_DICT.get(DragonBuyDigTimes + 1)
	if not cfg:
		print "GE_EXC,can not find BuyTime(%s) in RequestBuyDragonDigTimes" % (DragonBuyDigTimes+1)
		return
	
	DigCost = cfg.DigCost
	if role.GetUnbindRMB() < DigCost:
		return
	
	with DragonTreasureBuyDig:
		role.DecUnbindRMB(DigCost)
		role.IncDI8(EnumDayInt8.DragonBuyedDigTimes, 1)
		role.IncDI8(EnumDayInt8.DragonCanDigTimes, 1)
	
def RequestBuyLuckyDigTimes(role, param):
	'''
	客户端请求购买幸运寻宝次数
	@param role:
	@param param:
	'''
	vip = role.GetVIP()
	vipConfig = VIPConfig._VIP_BASE.get(vip)
	max_buy_cnt = 0
	#根据vip等级获取玩家可以购买的总次数
	if vipConfig:
		max_buy_cnt = vipConfig.DragonLuckyDigCnt
	if not max_buy_cnt: return

	DragonBuyDigTimes = role.GetDI8(EnumDayInt8.DragonBuyedLuckyDigTimes)
	if DragonBuyDigTimes >= max_buy_cnt:#无次数剩余
		return
	
	#根据购买的次数换算需要的神石
	cfg = DragonTreasureConfig.BUY_DIG_COST_DICT.get(DragonBuyDigTimes + 1)
	if not cfg:
		print "GE_EXC,can not find BuyTime(%s) in RequestBuyDragonDigTimes" % (DragonBuyDigTimes+1)
		return
	
	DigCost = cfg.DigLuckyCost
	if role.GetUnbindRMB() < DigCost:
		return
	
	with DragonTreasureBuyLuckyDig:
		role.DecUnbindRMB(DigCost)
		role.IncDI8(EnumDayInt8.DragonBuyedLuckyDigTimes, 1)
		role.IncDI8(EnumDayInt8.DragonCanLuckyDigTimes, 1)
#=======================================================
def RoleDayClear(role, param):
	'''
	玩家每日清理
	@param role:
	@param param:
	'''	
	if role.GetLevel() >= DragonTreasureDefine.LIMIT_LEVEL:
		#每日清空处理
		role.SetObj(EnumObj.Dragon_Treasure, {1:[], 2:[], 3:[], 4:[]})
		#刷新场景
		FreshSecne(role)
		#同步获得珍贵道具玩家信息(用于玩家清理时正打开界面)
		role.SendObj(Fresh_Precious_for_client, [])
		role.SendObj(Fresh_GetItem_for_client, [])
		role.SendObj(Luck_Fresh_scene_for_client, [])
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		
	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DragonTreasure_Start_Search", "客户端请求寻宝"), RequestDragonSearch)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DragonTreasure_Open_Win", "客户端打开巨龙宝藏界面"), RequestDragonOpenWin)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DragonTreasure_Dig", "客户端请求挖宝"), RequestDragonDig)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DragonTreasure_LuckDig", "客户端请求幸运寻宝"), RequestDragonLuckDig)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DragonTreasure_Buy_DigTimes", "客户端请求购买寻宝次数"), RequestBuyDragonDigTimes)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DragonTreasure_Buy_LuckyDigTimes", "客户端请求购买幸运寻宝次数"), RequestBuyLuckyDigTimes)
		
