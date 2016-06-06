#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.StarGirl.StarGirlMgr")
#===============================================================================
# 星灵管理
#===============================================================================
import random
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Item import ItemConfig
from Game.Role import Event
from Game.Role.Data import EnumDayInt8, EnumTempObj, EnumInt16, EnumInt8
from Game.StarGirl import StarGirlConfig, StarGirlDefine, StarGirlBase
from Game.DailyDo import DailyDo
from Game.Activity.ProjectAct import ProjectAct, EnumProActType
from Game.Activity.LatestActivity import LatestActivityMgr, EnumLatestType
from Game.Task import EnumTaskType
from Game.Activity.WonderfulAct import WonderfulActMgr, EnumWonderType

MaxCD = 10 * 24 * 3600 #最大星灵之力CD


if "_HasLoad" not in dir():
	#消息
	Star_Girl_Sync_All = AutoMessage.AllotMessage("Star_Girl_Sync_All", "通知客户端同步星灵所有数据")
	Star_Girl_Sync_One = AutoMessage.AllotMessage("Star_Girl_Sync_One", "通知客户端同步星灵单个数据")
	Star_Girl_Power_End = AutoMessage.AllotMessage("Star_Girl_Power_End", "通知客户端星灵之力时间结束")
	
def SyncAllStarGirl(role):
	starGirlMgr = role.GetTempObj(EnumTempObj.StarGirlMgr)
	
	girlData = {}
	for girlId, girlObj in starGirlMgr.girl_dict.iteritems():
		girlData[girlId] = [girlObj.level, girlObj.exp, girlObj.grade, 
						girlObj.star_level, girlObj.star_bless_value, girlObj.pray_cnt]
	
	sealData = {}
	for sealId, sealObj in starGirlMgr.seal_dict.iteritems():
		sealData[sealId] = [sealObj.level, sealObj.exp]
	
	role.SendObj(Star_Girl_Sync_All, (girlData, sealData))
	
def SyncOneStarGirl(role, girlId):
	starGirlMgr = role.GetTempObj(EnumTempObj.StarGirlMgr)
	
	if girlId not in starGirlMgr.girl_dict:
		return
	girlObj = starGirlMgr.girl_dict[girlId]
	
	role.SendObj(Star_Girl_Sync_One, [girlObj.girl_id, girlObj.level, girlObj.exp, girlObj.grade, 
						girlObj.star_level, girlObj.star_bless_value, girlObj.pray_cnt])
	
def StarGirlUnlock(role, starGirlId):
	starGirlMgr = role.GetTempObj(EnumTempObj.StarGirlMgr)
	
	girlConfig = StarGirlConfig.STAR_GIRL_BASE.get((starGirlId, 1))
	if not girlConfig:
		return
	
	if starGirlId in starGirlMgr.girl_dict:
		print "GE_EXC, repeat StarGirlUnlock (%s) (%s)" % (role.GetRoleID(), starGirlId)
		return
	#判断条件
	if role.GetStarLucky() < girlConfig.unlockNeedStarLucky:
		return
	if role.GetLevel() < girlConfig.unlockNeedRoleLevel:
		return
	
	if girlConfig.unlockNeedItem:
		coding, cnt = girlConfig.unlockNeedItem
		itemCnt = role.ItemCnt(coding)
		if itemCnt < cnt:
			return
		role.DelItem(*girlConfig.unlockNeedItem)
	
	#解锁
	starGirlMgr.create_star_girl(starGirlId)
	
	#同步客户端
	SyncOneStarGirl(role, starGirlId)
	
	#日志事件
	AutoLog.LogBase(role.GetRoleID(), AutoLog.eveStarGirlUnlock, starGirlId)
	
	#支线任务
	Event.TriggerEvent(Event.Eve_SubTask, role, (EnumTaskType.EnSubTask_StarGirlUnLock, None))
	
	#提示
	role.Msg(2, 0, GlobalPrompt.STAR_GIRL_Tips_1)
	
	#传闻
	if girlConfig.unlockNeedItem:
		coding, _ = girlConfig.unlockNeedItem
		itemName = ItemConfig.ItemCfg_Dict[coding].name
		cRoleMgr.Msg(3, 0, GlobalPrompt.STAR_GIRL_UNLOCK_HEARSAY % (role.GetRoleName(), itemName, girlConfig.girlName))
	
	
def StarGirlDivine(role, divineType):
	'''
	星灵占星
	@param divineType:
	'''
	if divineType == 1:
		#普通占星
		if role.GetDI8(EnumDayInt8.StarGirlNormalDivineCnt) >= EnumGameConfig.STAR_GIRL_NORMAL_DIVINE_MAX_CNT:
			return
		
		if role.GetMoney() < EnumGameConfig.STAR_GIRL_NORMAL_DIVINE_MONEY:
			return
		
		role.IncDI8(EnumDayInt8.StarGirlNormalDivineCnt, 1)
		
		role.DecMoney(EnumGameConfig.STAR_GIRL_NORMAL_DIVINE_MONEY)
		
		role.IncStarLucky(EnumGameConfig.STAR_GIRL_NORMAL_DIVINE_REWARD_STAR_LUCKY)
		
		#每日必做 -- 星灵普通占星
		Event.TriggerEvent(Event.Eve_DoDailyDo, role, (DailyDo.Daily_StarGirlDivine, 1))
		
		#提示
		role.Msg(2, 0, GlobalPrompt.STAR_GIRL_DIVINE_SUCCESS % EnumGameConfig.STAR_GIRL_NORMAL_DIVINE_REWARD_STAR_LUCKY)
	elif divineType == 2:
		#虔诚占星
		cnt = role.GetDI8(EnumDayInt8.StarGirlSuperDivineCnt)
		if cnt >= EnumGameConfig.STAR_GIRL_SUPER_DIVINE_MAX_CNT:
			return
		
		config = StarGirlConfig.SUPER_DIVINE.get(cnt + 1)
		if role.GetUnbindRMB() < config.needRMB:
			return
		
		role.IncDI8(EnumDayInt8.StarGirlSuperDivineCnt, 1)
		
		role.DecUnbindRMB(config.needRMB)
		
		role.IncStarLucky(config.rewardStarLucky)
		
		#提示
		role.Msg(2, 0, GlobalPrompt.STAR_GIRL_DIVINE_SUCCESS % config.rewardStarLucky)
	else:
		return
	
def StarGirlLevelUp(role, starGirlId, backFunId):
	starGirlMgr = role.GetTempObj(EnumTempObj.StarGirlMgr)
	
	#是否已解锁
	if starGirlId not in starGirlMgr.girl_dict:
		return
	girlObj = starGirlMgr.girl_dict[starGirlId]
	
	#是否可以升级
	levelConfig = StarGirlConfig.STAR_GIRL_LEVEL.get((starGirlId, girlObj.level))
	if not levelConfig:
		return
	baseConfig = StarGirlConfig.STAR_GIRL_BASE.get((starGirlId, girlObj.grade))
	if not baseConfig:
		return
	if girlObj.level >= baseConfig.gradeMaxLevel:
		return
	
	if role.GetDI8(EnumDayInt8.StarGirlLevelUpFreeCnt) < EnumGameConfig.STAR_GIRL_GIRL_LEVEL_UP_FREE_CNT:
		#是否还有免费次数
		role.IncDI8(EnumDayInt8.StarGirlLevelUpFreeCnt, 1)
		
		#随机倍率
		critId = StarGirlConfig.LEVEL_UP_CRIT_RANDOM_OBJ.RandomOne()
		cirtConfig = StarGirlConfig.LEVEL_UP_CRIT.get(critId)
		if not cirtConfig:
			return
		
		isLevelUp = AddGirlExp(role, girlObj, levelConfig, cirtConfig.critExp, baseConfig.gradeMaxLevel)
		
		#免费次数有概率得到奖励物品
		ri = random.randint(1, 10000)
		if ri < cirtConfig.freeCntRewardItemOdds:
			for item in cirtConfig.freeCntRewardItem:
				role.AddItem(*item)
				
		#升级重算属性
		if isLevelUp:
			starGirlMgr.recount_star_girl_property(girlObj.girl_id)
		
		#每日必做 -- 星灵升级(使用一次免费次数+1)
		Event.TriggerEvent(Event.Eve_DoDailyDo, role, (DailyDo.Daily_StarGirlLvUp, 1))
		
		#回调倍数, 是否升级
		role.CallBackFunction(backFunId, (critId, 1 if isLevelUp else 0))
	else:
		#是否有升级道具
		coding, cnt = levelConfig.levelUpNeedItem
		itemCnt = role.ItemCnt(coding)
		if itemCnt < cnt:
			return
		
		role.DelItem(coding, cnt)
		
		#随机倍率
		critId = StarGirlConfig.LEVEL_UP_CRIT_RANDOM_OBJ.RandomOne()
		cirtConfig = StarGirlConfig.LEVEL_UP_CRIT.get(critId)
		if not cirtConfig:
			print "GE_EXC can't find crit config in StarGirlLevelUp (%s)"  % role.GetRoleID()
			return
		
		isLevelUp = AddGirlExp(role, girlObj, levelConfig, cirtConfig.critExp, baseConfig.gradeMaxLevel)
		
		#升级重算属性
		if isLevelUp:
			starGirlMgr.recount_star_girl_property(girlObj.girl_id)
		
		#回调倍数
		role.CallBackFunction(backFunId, (critId, 1 if isLevelUp else 0))
		
		#精彩活动
		WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_StarGirlLevelUp, (role, cnt))
		
		
	#同步客户端
	SyncOneStarGirl(role, starGirlId)
	
	Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_StarGirlUp, 1))
	
def StarGirlFastLevelUp(role, starGirlId, backFunId):
	starGirlMgr = role.GetTempObj(EnumTempObj.StarGirlMgr)
	
	#是否已解锁
	if starGirlId not in starGirlMgr.girl_dict:
		return
	girlObj = starGirlMgr.girl_dict[starGirlId]
	
	#是否可以升级
	levelConfig = StarGirlConfig.STAR_GIRL_LEVEL.get((starGirlId, girlObj.level))
	if not levelConfig:
		return
	baseConfig = StarGirlConfig.STAR_GIRL_BASE.get((starGirlId, girlObj.grade))
	if not baseConfig:
		return
	if girlObj.level >= baseConfig.gradeMaxLevel:
		return
	
	isLevelUp = False
	
	#统计所有道具奖励
	totalAddExp = 0
	totalRewardItemDict = {}
	
	hasUsedfreeCnt = role.GetDI8(EnumDayInt8.StarGirlLevelUpFreeCnt)
	if hasUsedfreeCnt < EnumGameConfig.STAR_GIRL_GIRL_LEVEL_UP_FREE_CNT:
		#免费升级
		
		freeCnt = EnumGameConfig.STAR_GIRL_GIRL_LEVEL_UP_FREE_CNT - hasUsedfreeCnt
		
		for _ in xrange(freeCnt):
			#扣除免费次数
			role.IncDI8(EnumDayInt8.StarGirlLevelUpFreeCnt, 1)
			#随机倍率
			critId = StarGirlConfig.LEVEL_UP_CRIT_RANDOM_OBJ.RandomOne()
			cirtConfig = StarGirlConfig.LEVEL_UP_CRIT.get(critId)
			if not cirtConfig:
				print "GE_EXC can't find crit config in StarGirlFastLevelUp (%s)"  % role.GetRoleID()
				continue
			
			#免费次数有概率得到奖励物品
			ri = random.randint(1, 10000)
			if ri < cirtConfig.freeCntRewardItemOdds:
				for coding, cnt in cirtConfig.freeCntRewardItem:
					#统计奖励
					if coding not in totalRewardItemDict:
						totalRewardItemDict[coding] = cnt
					else:
						totalRewardItemDict[coding] += cnt
			
			totalAddExp += cirtConfig.critExp
			
			#每日必做 -- 星灵升级(一键升级)
			Event.TriggerEvent(Event.Eve_DoDailyDo, role, (DailyDo.Daily_StarGirlLvUp, 1))
			
			Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_StarGirlUp, 1))
			
			isMaxLevel, isLevelUp = AddGirlExpIfMaxLevelThenStop(role, girlObj, levelConfig, cirtConfig.critExp, baseConfig.gradeMaxLevel)
			#已经满级
			if isMaxLevel:
				#奖励
				FastLevelUpReward(role, totalAddExp, totalRewardItemDict)
				#回调客户端升级
				role.CallBackFunction(backFunId, 1 if isLevelUp else 0)
				#同步客户端
				SyncOneStarGirl(role, starGirlId)
				return
			
	#道具升级
	#是否有升级道具
	coding, _ = levelConfig.levelUpNeedItem
	itemCnt = role.ItemCnt(coding)
	if not itemCnt:
		#提前发奖
		FastLevelUpReward(role, totalAddExp, totalRewardItemDict)
		#同步客户端
		SyncOneStarGirl(role, starGirlId)
		return
	
	totalConsumeItemCnt = 0		#统计总共消耗道具
	for _ in xrange(itemCnt):
		totalConsumeItemCnt += 1
		#随机倍率
		critId = StarGirlConfig.LEVEL_UP_CRIT_RANDOM_OBJ.RandomOne()
		cirtConfig = StarGirlConfig.LEVEL_UP_CRIT.get(critId)
		if not cirtConfig:
			print "GE_EXC can't find crit config in StarGirlFastLevelUp (%s)"  % role.GetRoleID()
			return
		
		totalAddExp += cirtConfig.critExp
		
		isMaxLevel, isLevelUp = AddGirlExpIfMaxLevelThenStop(role, girlObj, levelConfig, cirtConfig.critExp, baseConfig.gradeMaxLevel)
		
		Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_StarGirlUp, 1))
		
		if isMaxLevel:
			#已经满级
			break
	
	#扣除道具
	role.DelItem(coding, totalConsumeItemCnt)
	#奖励
	FastLevelUpReward(role, totalAddExp, totalRewardItemDict)
	#回调客户端升级
	role.CallBackFunction(backFunId, 1 if isLevelUp else 0)
	#同步客户端
	SyncOneStarGirl(role, starGirlId)
	#精彩活动
	WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_StarGirlLevelUp, (role, totalConsumeItemCnt))
	
def FastLevelUpReward(role, totalAddExp, totalRewardItemDict):
	prompt = GlobalPrompt.STAR_GIRL_TOTAL_EXP_PROMPT % totalAddExp
	
	#发道具奖励
	for coding, cnt in totalRewardItemDict.iteritems():
		role.AddItem(coding, cnt)
		
		prompt += GlobalPrompt.Item_Tips % (coding, cnt)
		
	#提示
	role.Msg(2, 0, prompt)
	
def AddGirlExp(role, girlObj, levelConfig, addExp, maxLevel):
	isLevelUp = False
	
	nowExp = girlObj.exp + addExp
	while nowExp >= levelConfig.levelUpMaxExp and girlObj.level != maxLevel:
		girlObj.level += 1
		
		isLevelUp = True
		
		nowExp -= levelConfig.levelUpMaxExp
		
		#是否已经是当前阶段最高级
		if girlObj.level == maxLevel:
			break
			
		levelConfig = StarGirlConfig.STAR_GIRL_LEVEL.get(girlObj.level)
		if not levelConfig:
			break
		
	girlObj.exp = nowExp
	
	return isLevelUp
	
	
def AddGirlExpIfMaxLevelThenStop(role, girlObj, levelConfig, addExp, maxLevel):
	starGirlMgr = role.GetTempObj(EnumTempObj.StarGirlMgr)
	
	isMaxLevel = False
	isLevelUp = False
	
	nowExp = girlObj.exp + addExp
	
	while nowExp >= levelConfig.levelUpMaxExp and girlObj.level != maxLevel:
		girlObj.level += 1
		isLevelUp = True
		#升级重算属性
		starGirlMgr.recount_star_girl_property(girlObj.girl_id)
		
		nowExp -= levelConfig.levelUpMaxExp
		
		#是否已经是当前阶段最高级
		if girlObj.level == maxLevel:
			girlObj.exp = nowExp
			isMaxLevel = True
			return isMaxLevel, isLevelUp
		
		levelConfig = StarGirlConfig.STAR_GIRL_LEVEL.get((girlObj.girl_id, girlObj.level))
		if not levelConfig:
			break
		
	girlObj.exp = nowExp
	
	return isMaxLevel, isLevelUp
	
def StarGirlEvolve(role, starGirlId, backFunId):
	starGirlMgr = role.GetTempObj(EnumTempObj.StarGirlMgr)
	
	#未解锁
	if starGirlId not in starGirlMgr.girl_dict:
		return
	girlObj = starGirlMgr.girl_dict[starGirlId]
	
	girlConfig = StarGirlConfig.STAR_GIRL_BASE.get((starGirlId, girlObj.grade))
	if not girlConfig:
		return
	
	nextGrade = girlObj.grade + 1
	#是否已经达到最高阶级
	if not StarGirlConfig.STAR_GIRL_BASE.get((starGirlId, nextGrade)):
		return
	#判断进阶条件
	#星灵等级是否满足
	if girlObj.level < girlConfig.gradeMaxLevel:
		return
	#进化道具是否满足
	coding, cnt = girlConfig.evolveNeedItem
	itemCnt = role.ItemCnt(coding)
	if itemCnt < cnt:
		return
	
	role.DelItem(coding, cnt)
	
	girlObj.grade = nextGrade
	
	#重算属性
	starGirlMgr.recount_star_girl_property(starGirlId)
	
	#同步客户端
	SyncOneStarGirl(role, starGirlId)
	
	#回调客户端
	role.CallBackFunction(backFunId, starGirlId)
	
	role.Msg(2, 0, GlobalPrompt.STAR_GIRL_Tips_4)
	
def StarLevelUpByLucky(role, item,cnt):
	#未知逻辑错误
	if cnt is not 1:
		return
	#等级不足
	if role.GetLevel() < 60:
		role.Msg(2, 0, GlobalPrompt.STAR_GIRL_LEVEL_LESS)
		return
	#道具过期
	if item is None:
		return
	if  item.IsDeadTime():
		role.Msg(2, 0, GlobalPrompt.STAR_GIRL_DEAD_ITEM)
		return
	
	luckyId		= item.oid
	luckyCoding = item.GetItemCoding()
	
	starGirlId = role.GetI8(EnumInt8.StarGirlFightId)
	#没有出战星灵
	if not starGirlId:
		role.Msg(2, 0, GlobalPrompt.STAR_GIRL_NO_FIGHT)
		return
	
	starGirlMgr = role.GetTempObj(EnumTempObj.StarGirlMgr)
	#是否已解锁
	if starGirlId not in starGirlMgr.girl_dict:
		return
	girlObj = starGirlMgr.girl_dict[starGirlId]
	
	nextStarLevel = girlObj.star_level + 1
	#是否已经达到最大星级
	starLevelConfig = StarGirlConfig.STAR_LEVEL.get((starGirlId, girlObj.star_level))
	if not starLevelConfig:
		return
	if nextStarLevel > starLevelConfig.maxStarlevel:
		role.Msg(2, 0, GlobalPrompt.STAR_GIRL_MAX_STAR)
		return
	
	isStarLevelUp = False
	if StarGirlConfig.StarLucky.isLucky(luckyCoding,girlObj.star_level):
		role.DelProp(luckyId)
		#升星成功
		#精彩活动
		#WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_StarGirlStar, (role, cnt))
		#成功
		girlObj.star_level = nextStarLevel
		girlObj.star_bless_value = 0
		girlObj.CancelBless()
		#回调客户端升星成功
		#role.CallBackFunction(backFunId, None)
		role.Msg(2, 0, GlobalPrompt.STAR_GIRL_Tips_2)
		isStarLevelUp = True
	else:
		#升星失败
		
		#祝福值已满
		bless_totle = girlObj.GetGrilTotleBless()
		if bless_totle >= starLevelConfig.maxBlessValue:
			role.Msg(2, 0, GlobalPrompt.STAR_GIRL_Tips_7)
			return
		
		role.DelProp(luckyId)
		cfg = StarGirlConfig.STAR_LUCKY.get(luckyCoding)
		tempBless,keeptime = cfg.addTempBless
		
		if tempBless + bless_totle > starLevelConfig.maxBlessValue:
			tempBless = starLevelConfig.maxBlessValue - bless_totle
			
		girlObj.AddGrilTempBless(role,tempBless,keeptime)
		starGirlMgr.SynTempBless()
		role.Msg(2, 0, GlobalPrompt.STAR_GIRL_Tips_6 % tempBless)

	if isStarLevelUp :
		#升星重算属性
		starGirlMgr.recount_star_girl_property(starGirlId)
		#专题活动
		ProjectAct.GetFunByType(EnumProActType.ProjectStarGirlStarEvent, [role, nextStarLevel])
		#最新活动
		LatestActivityMgr.GetFunByType(EnumLatestType.StarGirl_Latest, [role, nextStarLevel])
	#同步客户端
	SyncOneStarGirl(role, starGirlId)
	
def StarLevelUp(role, starGirlId, backFunId):
	starGirlMgr = role.GetTempObj(EnumTempObj.StarGirlMgr)
	
	isStarLevelUp = False
	
	#是否已解锁
	if starGirlId not in starGirlMgr.girl_dict:
		return
	girlObj = starGirlMgr.girl_dict[starGirlId]
	
	nextStarLevel = girlObj.star_level + 1
	#是否已经达到最大星级
	starLevelConfig = StarGirlConfig.STAR_LEVEL.get((starGirlId, girlObj.star_level))
	if not starLevelConfig:
		return
	if nextStarLevel > starLevelConfig.maxStarlevel:
		return

	coding, cnt = starLevelConfig.starLevelUpNeedItem
	itemCnt = role.ItemCnt(coding)
	if itemCnt < cnt:
		return
	
	role.DelItem(coding, cnt)
	#精彩活动
	WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_StarGirlStar, (role, cnt))
	
	total_star_bless_value = girlObj.star_bless_value
	if girlObj.temp_bless_data:
		total_star_bless_value += girlObj.temp_bless_data[0]
	#祝福值是否满足条件
	if total_star_bless_value < starLevelConfig.successNeedMinBlessValue:
		#必定失败，增加祝福值
		if total_star_bless_value + starLevelConfig.failAddBlessValue >= starLevelConfig.maxBlessValue:
			girlObj.star_bless_value = starLevelConfig.maxBlessValue
		else:
			girlObj.star_bless_value += starLevelConfig.failAddBlessValue
		#同步客户端
		SyncOneStarGirl(role, starGirlId)
		role.Msg(2, 0, GlobalPrompt.STAR_GIRL_Tips_3 % starLevelConfig.failAddBlessValue)
		return
	
	#祝福值满必定成功
	if total_star_bless_value < starLevelConfig.maxBlessValue:
		#配置表里面的是10W分之一
		ri = random.randint(1, 100000)
		if ri >= starLevelConfig.starLevelUpOdds:
			#失败
			if total_star_bless_value + starLevelConfig.failAddBlessValue >= starLevelConfig.maxBlessValue:
				girlObj.star_bless_value = starLevelConfig.maxBlessValue
			else:
				girlObj.star_bless_value += starLevelConfig.failAddBlessValue
			
			role.Msg(2, 0, GlobalPrompt.STAR_GIRL_Tips_3 % starLevelConfig.failAddBlessValue)
		else:
			#成功
			girlObj.star_level = nextStarLevel
			girlObj.star_bless_value = 0
			girlObj.CancelBless()
			isStarLevelUp = True
			#回调客户端升星成功
			role.CallBackFunction(backFunId, None)
			role.Msg(2, 0, GlobalPrompt.STAR_GIRL_Tips_2)
	else:
		#成功
		girlObj.star_level = nextStarLevel
		girlObj.star_bless_value = 0
		girlObj.CancelBless()
		isStarLevelUp = True
		#回调客户端升星成功
		role.CallBackFunction(backFunId, None)
		role.Msg(2, 0, GlobalPrompt.STAR_GIRL_Tips_2)
	
	#升星重算属性
	if isStarLevelUp:
		starGirlMgr.recount_star_girl_property(starGirlId)
		#专题活动
		ProjectAct.GetFunByType(EnumProActType.ProjectStarGirlStarEvent, [role, nextStarLevel])
		#最新活动
		LatestActivityMgr.GetFunByType(EnumLatestType.StarGirl_Latest, [role, nextStarLevel])
	#同步客户端
	SyncOneStarGirl(role, starGirlId)
	
def FastStarLevelUp(role, starGirlId, backFunId):
	starGirlMgr = role.GetTempObj(EnumTempObj.StarGirlMgr)
	
	isStarLevelUp = False
	
	#是否已解锁
	if starGirlId not in starGirlMgr.girl_dict:
		return
	girlObj = starGirlMgr.girl_dict[starGirlId]
	
	nextStarLevel = girlObj.star_level + 1
	#是否已经达到最大星级
	starLevelConfig = StarGirlConfig.STAR_LEVEL.get((starGirlId, girlObj.star_level))
	if not starLevelConfig:
		return
	if nextStarLevel > starLevelConfig.maxStarlevel:
		return
	
	coding, _ = starLevelConfig.starLevelUpNeedItem
	itemCnt = role.ItemCnt(coding)
	if not itemCnt:
		return
	
	totalConsumeItemCnt = 0
	for _ in xrange(itemCnt):
		
		totalConsumeItemCnt += 1
		
		total_bless_value = girlObj.star_bless_value
		if girlObj.temp_bless_data:
			total_bless_value += girlObj.temp_bless_data[0]
		#祝福值是否满足条件
		if total_bless_value < starLevelConfig.successNeedMinBlessValue:
			#必定失败，增加祝福值
			if total_bless_value + starLevelConfig.failAddBlessValue >= starLevelConfig.maxBlessValue:
				girlObj.star_bless_value = starLevelConfig.maxBlessValue
			else:
				girlObj.star_bless_value += starLevelConfig.failAddBlessValue
			continue
		
		
		if total_bless_value < starLevelConfig.maxBlessValue:
			#当前祝福值大于需要的最小祝福值,但是小于必定成功的祝福值，随机概率
			ri = random.randint(1, 100000)
			if ri >= starLevelConfig.starLevelUpOdds:
				#失败
				if girlObj.star_bless_value + starLevelConfig.failAddBlessValue >= starLevelConfig.maxBlessValue:
					girlObj.star_bless_value = starLevelConfig.maxBlessValue
				else:
					girlObj.star_bless_value += starLevelConfig.failAddBlessValue
			else:
				#成功
				girlObj.star_level = nextStarLevel
				girlObj.star_bless_value = 0
				girlObj.CancelBless()
				isStarLevelUp = True
				#回调客户端升星成功
				role.CallBackFunction(backFunId, None)
				break
		else:
			##祝福值满必定成功
			girlObj.star_level = nextStarLevel
			girlObj.star_bless_value = 0
			girlObj.CancelBless()
			isStarLevelUp = True
			#回调客户端升星成功
			role.CallBackFunction(backFunId, None)
			break
	
	#消耗道具
	role.DelItem(coding, totalConsumeItemCnt)
	#精彩活动
	WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_StarGirlStar, (role, totalConsumeItemCnt))
	#升星重算属性
	if isStarLevelUp:
		starGirlMgr.recount_star_girl_property(starGirlId)
		#专题活动
		ProjectAct.GetFunByType(EnumProActType.ProjectStarGirlStarEvent, [role, nextStarLevel])
		#最新活动
		LatestActivityMgr.GetFunByType(EnumLatestType.StarGirl_Latest, [role, nextStarLevel])
	#同步客户端
	SyncOneStarGirl(role, starGirlId)

def StarGirlPray(role, starGirlId, backFunId):
	starGirlMgr = role.GetTempObj(EnumTempObj.StarGirlMgr)
	
	#是否已解锁
	if starGirlId not in starGirlMgr.girl_dict:
		return
	girlObj = starGirlMgr.girl_dict[starGirlId]
	
	
	if girlObj.pray_cnt >= EnumGameConfig.STAR_GIRL_PRAY_FREE_CNT:
		return
	
	girlObj.pray_cnt += 1
	
	role.IncI16(EnumInt16.StarGirlLove, EnumGameConfig.STAR_GIRL_ADD_LOVE)
	
	#回调客户端
	role.CallBackFunction(backFunId, None)
	
	#同步客户端
	SyncOneStarGirl(role, starGirlId)
	
def StarGirlBuyLove(role):
	cnt = role.GetDI8(EnumDayInt8.StarGirlBuyLoveCnt)
	
	if cnt > 100:
		role.Msg(2, 0, GlobalPrompt.STAR_GIRL_Tips_5)
		return
	
	config = StarGirlConfig.BUY_LOVE_CNT.get(cnt + 1)
	if not config:
		return
	
	if role.GetUnbindRMB() < config.needRMB:
		return
	role.DecUnbindRMB(config.needRMB)
	
	role.IncDI8(EnumDayInt8.StarGirlBuyLoveCnt, 1)
	
	role.IncI16(EnumInt16.StarGirlLove, EnumGameConfig.STAR_GIRL_ADD_LOVE)
	
def StarGirlActivatePower(role, starGirlId, powerType):
	starGirlMgr = role.GetTempObj(EnumTempObj.StarGirlMgr)
	
	#是否已解锁
	if starGirlId not in starGirlMgr.girl_dict:
		return
	
	powerConsumeConfig = StarGirlConfig.POWER_CONSUME.get(powerType)
	if not powerConsumeConfig:
		return
	
	if role.GetI16(EnumInt16.StarGirlLove) < powerConsumeConfig.needLove:
		return
	
	#星灵之力CD枚举
	cdEnum = StarGirlDefine.GIRL_ID_TO_CD_ENUM.get(starGirlId)
	if not cdEnum:
		return
	
	role.DecI16(EnumInt16.StarGirlLove, powerConsumeConfig.needLove)
	
	if role.GetCD(cdEnum) >= MaxCD:
		#最多10天
		return
	
	#激活主角buff
	role.SetCD(cdEnum, role.GetCD(cdEnum) + powerConsumeConfig.powerTime)
	
	#重新注册星灵之力到期时间
	if starGirlId in starGirlMgr.girl_power_tick_id_dict:
		role.UnregTick(starGirlMgr.girl_power_tick_id_dict[starGirlId])
		starGirlMgr.girl_power_tick_id_dict[starGirlId] = role.RegTick(role.GetCD(cdEnum) + 5, PowerEnd)
	else:
		starGirlMgr.girl_power_tick_id_dict[starGirlId] = role.RegTick(role.GetCD(cdEnum) + 5, PowerEnd)
	
	
	#重算主角属性
	role.GetPropertyGather().ReSetRecountStarGirlFlag()
	
def StarGirlInherit(role, oldGirlId, newGirlId, backFunId):
	starGirlMgr = role.GetTempObj(EnumTempObj.StarGirlMgr)
	
	#是否已解锁
	if oldGirlId not in starGirlMgr.girl_dict:
		return
	if newGirlId not in starGirlMgr.girl_dict:
		return
	
	oldGirlObj = starGirlMgr.girl_dict[oldGirlId]
	newGirlObj = starGirlMgr.girl_dict[newGirlId]
	
	#配置表
	inheritConsumeConfig = StarGirlConfig.INHERIT_CONSUME.get(oldGirlObj.level)
	if not inheritConsumeConfig:
		return
	starLevelConfig = StarGirlConfig.STAR_LEVEL.get((newGirlId, newGirlObj.star_level))
	if not starLevelConfig:
		return
	
	#需要消耗道具
	needItemCoding, needItemCnt = inheritConsumeConfig.needItem
	itemCnt = role.ItemCnt(needItemCoding)
	if itemCnt < needItemCnt:
		return
	
	role.DelItem(needItemCoding, needItemCnt)
	
	#计算传承的总经验值
	totalInheritExp = 0
	for level in xrange(1, oldGirlObj.level):
		levelConfig = StarGirlConfig.STAR_GIRL_LEVEL.get((oldGirlId, level))
		if not levelConfig:
			continue
		totalInheritExp += levelConfig.levelUpMaxExp
	
	totalInheritExp += oldGirlObj.exp
	
	#传承等级相关
	newGirlLevel = newGirlObj.level
	newExp = newGirlObj.exp + totalInheritExp
	newGrade = max(newGirlObj.grade, oldGirlObj.grade)
	levelConfig = StarGirlConfig.STAR_GIRL_LEVEL.get((newGirlId, newGirlLevel))
	while newExp >= levelConfig.levelUpMaxExp and newGirlLevel != levelConfig.maxLevel:
		newGirlLevel += 1
		newExp -= levelConfig.levelUpMaxExp
		
		levelConfig = StarGirlConfig.STAR_GIRL_LEVEL.get((newGirlId, newGirlLevel))
		if not levelConfig:
			break
		
		newGrade = max(newGrade, levelConfig.inheritGrade)
		
		#是否已经是当前阶段最高级
		if newGirlLevel == levelConfig.maxLevel:
			#截断溢出经验
			if newExp > levelConfig.levelUpMaxExp:
				newExp = levelConfig.levelUpMaxExp
			break
			
		
	newGirlObj.level = newGirlLevel
	newGirlObj.exp = newExp
	#不能超出星灵最高阶级
	levelConfig = StarGirlConfig.STAR_GIRL_LEVEL.get((newGirlId, newGirlObj.level))
	newGirlObj.grade = min(newGrade, levelConfig.maxGrade)
	
	oldGirlObj.level = 1
	oldGirlObj.exp = 0
	oldGirlObj.grade = 1
	
	#获取最大星级
	maxStarLevel = max(newGirlObj.star_level, oldGirlObj.star_level)
	
	#传承祝福值计算
	starLevelConfig = StarGirlConfig.STAR_LEVEL.get((newGirlId, maxStarLevel))
	if newGirlObj.star_bless_value + oldGirlObj.star_bless_value >= starLevelConfig.maxBlessValue:
		newGirlObj.star_bless_value = starLevelConfig.maxBlessValue
	else:
		newGirlObj.star_bless_value += oldGirlObj.star_bless_value
	
	#传承星级相关
	newGirlObj.star_level = maxStarLevel
	oldGirlObj.star_level = 1
	oldGirlObj.star_bless_value = 0
	
	#传承后重算星灵属性
	starGirlMgr.recount_star_girl_property(oldGirlId)
	starGirlMgr.recount_star_girl_property(newGirlId)
	
	#同步客户端
	SyncAllStarGirl(role)
	#回调被传承的星灵ID
	role.CallBackFunction(backFunId, (oldGirlId, newGirlId))
	
	
	
def StarGirlFollow(role, starGirlId, followOrNot):
	starGirlMgr = role.GetTempObj(EnumTempObj.StarGirlMgr)
	
	#是否已解锁
	if starGirlId not in starGirlMgr.girl_dict:
		return
	
	if followOrNot:
		#跟随
		if role.GetI8(EnumInt8.StarGirlFollowId) == starGirlId:
			return
	
		role.SetI8(EnumInt8.StarGirlFollowId, starGirlId)
	else:
		#取消跟随
		role.SetI8(EnumInt8.StarGirlFollowId, 0)
	
	#同步客户端
	SyncAllStarGirl(role)
	
def StarGirlFight(role, starGirlId):
	starGirlMgr = role.GetTempObj(EnumTempObj.StarGirlMgr)
	
	#是否已解锁
	if starGirlId not in starGirlMgr.girl_dict:
		return
	
	role.SetI8(EnumInt8.StarGirlFightId, starGirlId)
	
	#触发重算战斗力事件
	Event.TriggerEvent(Event.Eve_RecountZDL, role)
	
	#同步客户端
	SyncAllStarGirl(role)
	
def StarGirlSealUnlock(role, sealId):
	starGirlMgr = role.GetTempObj(EnumTempObj.StarGirlMgr)
	
	sealConfig = StarGirlConfig.SEAL_BASE.get(sealId)
	if not sealConfig:
		return
	
	#判断条件
	isStarLevelOK = False
	for girlObj in starGirlMgr.girl_dict.itervalues():
		if girlObj.star_level >= sealConfig.unlockNeedStarLevel:
			isStarLevelOK = True
			break
		
	if isStarLevelOK is False:
		return
	
	if sealConfig.unlockNeedItem:
		coding, cnt = sealConfig.unlockNeedItem
		itemCnt = role.ItemCnt(coding)
		if itemCnt < cnt:
			return
		role.DelItem(*sealConfig.unlockNeedItem)

	#解锁
	starGirlMgr.create_seal(sealId)
	starGirlMgr.Recount_seal_property()
	#同步客户端
	SyncAllStarGirl(role)
	
#	#提示
#	role.Msg(2, 0, GlobalPrompt.STAR_GIRL_Tips_1)
#	
#	#传闻
#	if girlConfig.unlockNeedItem:
#		coding, _ = girlConfig.unlockNeedItem
#		itemName = ItemConfig.ItemCfg_Dict[coding].name
#		cRoleMgr.Msg(3, 0, GlobalPrompt.STAR_GIRL_UNLOCK_HEARSAY % (role.GetRoleName(), itemName, girlConfig.girlName))
	
	
def StarGirlSealLevelUpByLucky(role,sealId, levelUpCnt):
	#以下逻辑基于每次道具数消耗为1
	if role.GetLevel() < 60:
		role.Msg(2, 0, GlobalPrompt.STAR_GIRL_LEVEL_LESS_PARAM % 60)
		return
	
	starGirlMgr = role.GetTempObj(EnumTempObj.StarGirlMgr)
	
	#是否已解锁
	if sealId not in starGirlMgr.seal_dict:
		return
	sealObj = starGirlMgr.seal_dict[sealId]
	
	#是否可以升级
	levelConfig = StarGirlConfig.SEAL_LEVEL.get((sealId, sealObj.level))
	if not levelConfig:
		return
	#最大等级
	nowLevel = sealObj.level
	if nowLevel >= levelConfig.maxLevel:
		return
	
	#是否有足够的升级道具
	coding = levelConfig.luckyCoding
	#背包道具数量
	itemCnt = role.ItemCnt(coding)
	#道具不足
	if itemCnt < 1:
		return
	packageMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	codingGatherDict = packageMgr.codingGather.get(coding)
	if not codingGatherDict:
		return
	delItemId = 0
	for itemId, item in codingGatherDict.iteritems():
		if item.IsDeadTime():
			continue
		delItemId = itemId
		break
	if not delItemId:#全部是过期道具
		role.Msg(2, 0, GlobalPrompt.STAR_GIRL_DEAD_ITEM)
		return
	
	#升级消耗
	#道具数
	itemOnUse = 0
	
	#升级后数据
	afterLevel = nowLevel
	afterExp = 0
	afterCfg = StarGirlConfig.SEAL_LEVEL.get((sealId, nowLevel))
	isLevelUp = False
	
	toLevel = nowLevel + levelUpCnt
	while nowLevel < toLevel and nowLevel < levelConfig.maxLevel:
		delItemId = 0
		for itemId, item in codingGatherDict.iteritems():
			if item.IsDeadTime():
				continue
			delItemId = itemId
			break
		#道具满足
		if delItemId:
			temp_level = nowLevel + 1
			
			cfg = StarGirlConfig.SEAL_LEVEL.get((sealId, temp_level))
			if not cfg:
				break
			else:
				afterCfg = cfg
				isLevelUp = True
				itemOnUse += 1
				nowLevel = temp_level
				afterLevel = nowLevel
				role.DelProp(delItemId)
		#道具不足
		else:
			break
		
	sealObj.exp = afterExp
	sealObj.level = afterLevel
	sealObj.levelcfg = afterCfg
	
	if isLevelUp is True:
		starGirlMgr.Recount_seal_property()
	
	#同步客户端
	SyncAllStarGirl(role)
	
	
def StarGirlSealLevelUp(role, sealId, levelUpCnt):
	starGirlMgr = role.GetTempObj(EnumTempObj.StarGirlMgr)
	
	#是否已解锁
	if sealId not in starGirlMgr.seal_dict:
		return
	sealObj = starGirlMgr.seal_dict[sealId]
	
	#是否可以升级
	levelConfig = StarGirlConfig.SEAL_LEVEL.get((sealId, sealObj.level))
	if not levelConfig:
		return
	
	#是否有足够的升级道具
	coding, cnt = levelConfig.levelUpNeedItem
	totalItemCnt = cnt * levelUpCnt
	itemCnt = role.ItemCnt(coding)
	if itemCnt < totalItemCnt:
		return
	
	nowLevel = sealObj.level
	if nowLevel >= levelConfig.maxLevel:
		return
	
	totalUseItem = totalItemCnt
	levelUpUseItem = 0
	needItem = 0
	nowExp = sealObj.exp
	addExp = levelConfig.itemAddExp * totalItemCnt
	isLevelUp = False
	while nowExp + addExp >= levelConfig.levelUpNeedExp and nowLevel != levelConfig.maxLevel:
		#这一级需要的经验
		needExp = levelConfig.levelUpNeedExp - nowExp
		
		#这一级需要的物品
		needItem = needExp / levelConfig.itemAddExp
		if needExp % levelConfig.itemAddExp > 0:
			needItem += 1
			
		#升级消耗物品
		levelUpUseItem += needItem
		#暂时的总消耗物品
		totalUseItem = levelUpUseItem
		
		#这些物品产生的经验
		thisLevelAddExp = needItem * levelConfig.itemAddExp
		
		#经验溢出到下一级
		nowExp = thisLevelAddExp - needExp
		
		#升级
		nowLevel += 1
		isLevelUp = True
		#升级后的配置
		#是否已经是当前阶段最高级
		if nowLevel == levelConfig.maxLevel:
			break
		
		newcfg = StarGirlConfig.SEAL_LEVEL.get((sealId, nowLevel))
		if not newcfg:
			break
		levelConfig = newcfg
		#剩余物品的经验
		addExp = levelConfig.itemAddExp * (totalItemCnt - levelUpUseItem)
		#暂时总共使用的物品
		totalUseItem = totalItemCnt
		
		
	#扣除真正消耗的物品
	role.DelItem(coding, totalUseItem)
	
	sealObj.exp = nowExp + addExp
	sealObj.level = nowLevel
	sealObj.levelcfg = levelConfig
	
	if isLevelUp is True:
		starGirlMgr.Recount_seal_property()
	
	#同步客户端
	SyncAllStarGirl(role)

#===============================================================================
# 时间
#===============================================================================
def PowerEnd(role, callargv, regparam):
	#重算主角属性
	role.GetPropertyGather().ReSetRecountStarGirlFlag()
	#同步客户端
	role.SendObj(Star_Girl_Power_End, None)
	
#===============================================================================
# 事件
#===============================================================================
def OnRoleInit(role, param):
	'''
	角色初始化
	@param role:
	@param param:
	'''
	role.SetTempObj(EnumTempObj.StarGirlMgr, StarGirlBase.StarGirlMgr(role))

def OnRoleLogin(role, param):
	'''
	角色登录
	@param role:
	@param param:
	'''
	starGirlMgr = role.GetTempObj(EnumTempObj.StarGirlMgr)
	#注册星灵之力到期时间
	for cdEnum, girlId in StarGirlDefine.CD_ENUM_TO_GIRL_ID.iteritems():
		cd = role.GetCD(cdEnum)
		if role.GetCD(cdEnum):
			#注册星灵之力到期时间
			starGirlMgr.girl_power_tick_id_dict[girlId] = role.RegTick(cd + 5, PowerEnd)
	#临时祝福值
	for girlObj in starGirlMgr.girl_dict.values():
		girlObj.SetTempTick(role)
	
	starGirlMgr.SynTempBless()
	
def SyncRoleOtherData(role, param):
	'''
	角色登录同步其他剩余的数据
	@param role:
	@param param:
	'''
	starGirlMgr = role.GetTempObj(EnumTempObj.StarGirlMgr)
	starGirlMgr.SynTempBless()
	#同步星灵所有数据
	SyncAllStarGirl(role)
	
def OnRoleSave(role, param):
	'''
	角色保存
	@param role:
	@param param:
	'''
	starGirlMgr = role.GetTempObj(EnumTempObj.StarGirlMgr)
	starGirlMgr.save()
	
def OnRoleDayClear(role, param):
	'''
	每日清理
	@param role:
	@param param:
	'''
	starGirlMgr = role.GetTempObj(EnumTempObj.StarGirlMgr)
	
	for girlObj in starGirlMgr.girl_dict.itervalues():
		girlObj.pray_cnt = 0
	
#===============================================================================
# 客户端请求
#===============================================================================
def RequestStarGirlOpenMainPanel(role, msg):
	'''
	客户端请求打开星灵主面板
	@param role:
	@param msg:
	'''
	SyncAllStarGirl(role)

def RequestStarGirlUnlock(role, msg):
	'''
	客户端请求星灵解锁
	@param role:
	@param msg:
	'''
	starGirlId = msg
	
	#日志
	with TraStarGirlUnlock:
		StarGirlUnlock(role, starGirlId)

def RequestStarGirlDivine(role, msg):
	'''
	客户端请求星灵占星
	@param role:
	@param msg:
	'''
	divineType = msg
	
	#日志
	with TraStarGirlDivine:
		StarGirlDivine(role, divineType)
	
def RequestStarGirlLevelUp(role, msg):
	'''
	客户端请求星灵升级
	@param role:
	@param msg:
	'''
	backFunId, starGirlId = msg
	
	#日志
	with TraStarGirlLevelUp:
		StarGirlLevelUp(role, starGirlId, backFunId)
	
def RequestStarGirlFastLevelUp(role, msg):
	'''
	客户端请求星灵一键升级
	@param role:
	@param msg:
	'''
	backFunId, starGirlId = msg

	#日志
	with TraStarGirlLevelUp:
		StarGirlFastLevelUp(role, starGirlId, backFunId)
	
def RequestStarGirlEvolve(role, msg):
	'''
	客户端请求星灵进化
	@param role:
	@param msg:
	'''
	backFunId, starGirlId = msg
	
	#日志
	with TraStarGirlEvolve:
		StarGirlEvolve(role, starGirlId, backFunId)
	
def RequestStarGirlStarLevelUp(role, msg):
	'''
	客户端请求星灵升星
	@param role:
	@param msg:
	'''
	backFunId, starGirlId = msg
	
	#日志
	with TraStarGirlStarLevelUp:
			StarLevelUp(role, starGirlId, backFunId)
	
def RequestStarGirlStarFastLevelUp(role, msg):
	'''
	客户端请求星灵一键升星
	@param role:
	@param msg:
	'''
	backFunId, starGirlId= msg
	
	#日志
	with TraStarGirlStarLevelUp:
			FastStarLevelUp(role, starGirlId, backFunId)
	
def RequestStarGirlPray(role, msg):
	'''
	客户端请求星灵祈祷
	@param role:
	@param msg:
	'''
	backFunId, starGirlId = msg
	
	#日志
	with TraStarGirlPray:
		StarGirlPray(role, starGirlId, backFunId)
	
def RequestStarGirlBuyLove(role, msg):
	'''
	客户端请求星灵购买爱心值
	@param role:
	@param msg:
	'''
	#日志
	with TraStarGirlBuyLove:
		StarGirlBuyLove(role)
	
def RequestStarGirlActivatePower(role, msg):
	'''
	客户端请求星灵激活星灵之力
	@param role:
	@param msg:
	'''
	starGirlId, powerType = msg
	
	#日志
	with TraStarGirlActivatePower:
		StarGirlActivatePower(role, starGirlId, powerType)
	
def RequestStarGirlInherit(role, msg):
	'''
	客户端请求星灵传承
	@param role:
	@param msg:
	'''
	backFunId, data = msg
	oldGirlId, newGirlId = data
	
	#日志
	with TraStarGirlInherit:
		StarGirlInherit(role, oldGirlId, newGirlId, backFunId)
	
def RequestStarGirlFollow(role, msg):
	'''
	客户端请求星灵跟随
	@param role:
	@param msg:
	'''
	starGirlId, followOrNot = msg
	
	StarGirlFollow(role, starGirlId, followOrNot)
	
def RequestStarGirlFight(role, msg):
	'''
	客户端请求星灵出战
	@param role:
	@param msg:
	'''
	starGirlId = msg
	
	StarGirlFight(role, starGirlId)
	
def RequestStarGirlSealUnlock(role, msg):
	'''
	客户端请求星灵刻印解锁
	@param role:
	@param msg:
	'''
	sealId = msg
	
	#日志
	with TraStarGirlSealUnlock:
		StarGirlSealUnlock(role, sealId)
	
def RequestStarGirlSealLevelUp(role, msg):
	'''
	客户端请求星灵刻印升级
	@param role:
	@param msg:
	'''
	#print msg
	sealId, levelUpCnt , isLucky = msg
	if levelUpCnt < 1:
		return
	#日志
	with TraStarGirlSealLevelUp:
		if isLucky:
			StarGirlSealLevelUpByLucky(role, sealId, levelUpCnt)
		else:
			StarGirlSealLevelUp(role, sealId, levelUpCnt)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		#角色初始化
		Event.RegEvent(Event.Eve_InitRolePyObj, OnRoleInit)
		#角色登录
		Event.RegEvent(Event.Eve_AfterLogin, OnRoleLogin)
		#角色保存
		Event.RegEvent(Event.Eve_BeforeSaveRole, OnRoleSave)
		#角色每日清理
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
		#角色登录同步其他剩余的数据
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		
		#日志
		TraStarGirlUnlock = AutoLog.AutoTransaction("TraStarGirlUnlock", "星灵解锁")
		TraStarGirlDivine = AutoLog.AutoTransaction("TraStarGirlDivine", "星灵占星")
		TraStarGirlLevelUp = AutoLog.AutoTransaction("TraStarGirlLevelUp", "星灵升级")
		TraStarGirlEvolve = AutoLog.AutoTransaction("TraStarGirlEvolve", "星灵进化")
		TraStarGirlStarLevelUp = AutoLog.AutoTransaction("TraStarGirlStarLevelUp", "星灵升星")
		TraStarGirlPray = AutoLog.AutoTransaction("TraStarGirlPray", "星灵祈祷")
		TraStarGirlBuyLove = AutoLog.AutoTransaction("TraStarGirlBuyLove", "星灵购买爱心值")
		TraStarGirlActivatePower = AutoLog.AutoTransaction("TraStarGirlActivatePower", "星灵激活星灵之力")
		TraStarGirlInherit = AutoLog.AutoTransaction("TraStarGirlInherit", "星灵传承")
		TraStarGirlSealUnlock = AutoLog.AutoTransaction("TraStarGirlSealUnlock", "星灵刻印解锁")
		TraStarGirlSealLevelUp = AutoLog.AutoTransaction("TraStarGirlSealLevelUp", "星灵刻印升级")
	
	if Environment.HasLogic and not Environment.IsCross:
		#注册消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Star_Girl_Open_Main_Panel", "客户端请求打开星灵主面板"), RequestStarGirlOpenMainPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Star_Girl_Unlock", "客户端请求星灵解锁"), RequestStarGirlUnlock)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Star_Girl_Divine", "客户端请求星灵占星"), RequestStarGirlDivine)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Star_Girl_Level_Up", "客户端请求星灵升级"), RequestStarGirlLevelUp)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Star_Girl_Fast_Level_Up", "客户端请求星灵一键升级"), RequestStarGirlFastLevelUp)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Star_Girl_Evolve", "客户端请求星灵进化"), RequestStarGirlEvolve)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Star_Girl_Star_Level_Up", "客户端请求星灵升星"), RequestStarGirlStarLevelUp)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Star_Girl_Star_Fast_Level_Up", "客户端请求星灵一键升星"), RequestStarGirlStarFastLevelUp)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Star_Girl_Pray", "客户端请求星灵祈祷"), RequestStarGirlPray)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Star_Girl_Buy_Love", "客户端请求星灵购买爱心值"), RequestStarGirlBuyLove)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Star_Girl_Activate_Power", "客户端请求星灵激活星灵之力"), RequestStarGirlActivatePower)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Star_Girl_Activate_Inherit", "客户端请求星灵传承"), RequestStarGirlInherit)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Star_Girl_Follow", "客户端请求星灵跟随"), RequestStarGirlFollow)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Star_Girl_Fight", "客户端请求星灵出战"), RequestStarGirlFight)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Star_Girl_Seal_Unlock", "客户端请求星灵刻印解锁"), RequestStarGirlSealUnlock)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Star_Girl_Seal_Level_Up", "客户端请求星灵刻印升级"), RequestStarGirlSealLevelUp)


