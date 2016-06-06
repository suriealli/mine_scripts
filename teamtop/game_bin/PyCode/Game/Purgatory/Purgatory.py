#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Purgatory.Purgatory")
#===============================================================================
# 心魔炼狱
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt, EnumFightStatistics
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumDayInt8, EnumInt1, EnumObj, EnumTempObj, EnumCD
from Game.Role import Status, Event
from Game.Purgatory import PurgatoryConfig
from Game.Fight import FightEx, Middle, Operate
from Game.VIP import VIPConfig
from Game.DailyDo import DailyDo
from Game.ThirdParty.QQidip import QQEventDefine
from Game.Persistence import Contain
from Game.Activity.SevenDayHegemony import SDHFunGather, SDHDefine

if "_HasLoad" not in dir():
	PurgatoryRewardData = AutoMessage.AllotMessage("PurgatoryRewardData", "心魔炼狱通关数据")
	PurgatoryJoinID = AutoMessage.AllotMessage("PurgatoryJoinID", "心魔炼狱进入炼狱ID")
	SyncBestInPurgatory = AutoMessage.AllotMessage("SyncBestInPurgatory", "同步客户端角色在心魔炼狱中取得的最好成绩 ")
	
	PurgatoryRatingReward_Log = AutoLog.AutoTransaction("PurgatoryRatingReward_Log", "心魔炼狱领取评级奖励")
	PurgatoryMonsterReward_Log = AutoLog.AutoTransaction("PurgatoryMonsterReward_Log", "心魔炼狱领取击杀怪物奖励")
	PurgatoryBuyLife_Log = AutoLog.AutoTransaction("PurgatoryBuyLife_Log", "心魔炼狱买活")
	PurgatoryOnekeyReward_Log = AutoLog.AutoTransaction("PurgatoryOnekeyReward_Log", "心魔炼狱一键收益奖励")
	
	
def JoinDemons(role, purgatoryId):
	'''
	进入炼狱
	@param role:
	@param purgatoryId:炼狱ID
	'''
	#配置
	cfg = PurgatoryConfig.Purgatory_Dict.get(purgatoryId)
	if not cfg:
		print "GE_EXC, Purgatory can not find purgatoryId:(%s) in Purgatory_Dict" % purgatoryId
		return
	#等级
	if role.GetLevel() < cfg.minLevel:
		return
	#次数
	if role.GetDI8(EnumDayInt8.PurgatoryCnt) >= EnumGameConfig.PurgatoryMaxCnt:
		return
	#是否能进入战斗
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		return
	if len(role.GetObj(EnumObj.PurgatoryReward)) > 1:
		return
	
	#减进入次数
	role.IncDI8(EnumDayInt8.PurgatoryCnt, 1)
	FightEx.PVE_Purgatory(role, EnumGameConfig.PurgatoryFightType, cfg.mcidList, AfterFight, BuyLife, purgatoryId)
	
	#同步客户端进入的炼狱ID
	role.SendObj(PurgatoryJoinID, (purgatoryId, 0))
	#记录进入战斗
	role.SetTempObj(EnumTempObj.PurgatoryInFight, purgatoryId)
	
	#每日必做 -- 进入炼狱
	Event.TriggerEvent(Event.Eve_DoDailyDo, role, (DailyDo.Daily_P, 1))
	
	Event.TriggerEvent(Event.QQidip_Eve, role, QQEventDefine.QQ_Purgatory)
	
	#活跃度
	Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_Purgatory, 1))
	
def AfterFight(fightObj):
	if fightObj.result is None:
		print "GE_EXC, Purgatory fight error"
		return
	
	purgatoryId = fightObj.after_fight_param
	
	roles = fightObj.left_camp.roles
	if not roles:
		return
	role = list(roles)[0]
	
	if fightObj.result == 1:
		fightRound = fightObj.round
		if fightRound > 99:
			#超过99回合, 强制修正为99回合
			fightRound = 99
		cfg = PurgatoryConfig.Purgatory_Dict.get(purgatoryId)
		if not cfg:
			return
		
		#获取通关后评级
		passLevel = cfg.RTS.get(GetCloseValue(fightObj.round, sorted(cfg.PRR.keys())), 0)
		fightObj.set_fight_statistics(role.GetRoleID(), EnumFightStatistics.EnumPurgatoryStar, passLevel)
		
		#版本判断
		if Environment.EnvIsNA():
			#北美万圣节
			HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
			HalloweenNAMgr.purgatoryPass(purgatoryId, passLevel)
		elif Environment.EnvIsRU():
			#七日活动
			sevenActMgr = role.GetTempObj(EnumTempObj.SevenActMgr)
			sevenActMgr.purgatoryPass(purgatoryId, passLevel)
			
	elif fightObj.result == -1 or fightObj.result == 0:
		fightRound = 0
		fightObj.set_fight_statistics(role.GetRoleID(), EnumFightStatistics.EnumPurgatoryStar, 0)
	else:
		fightObj.set_fight_statistics(role.GetRoleID(), EnumFightStatistics.EnumPurgatoryStar, 0)
		return
	
	#设置离开心魔炼狱战斗
	role.SetTempObj(EnumTempObj.PurgatoryInFight, 0)
	
	if fightRound:
		wheels = fightObj.right_camp.monster_wave
	else:
		wheels = fightObj.right_camp.monster_wave - 1
	
	purgatoryObj = role.GetObj(EnumObj.PurgatoryReward)
	if not wheels and not fightRound:
		if purgatoryId in purgatoryObj:
			del purgatoryObj[purgatoryId]
	else:
		purgatoryObj[purgatoryId] = [wheels, fightRound]
		
		maxRecordDict = purgatoryObj.get(0, {})
		if purgatoryId not in maxRecordDict:
			maxRecordDict[purgatoryId] = [wheels, fightRound]
		else:
			hWheels, hFightRound = maxRecordDict[purgatoryId]
			if (wheels > hWheels) or (wheels == hWheels and fightRound < hFightRound) :
				maxRecordDict[purgatoryId] = [wheels, fightRound]
		purgatoryObj[0] = maxRecordDict
		
	role.SetObj(EnumObj.PurgatoryReward, purgatoryObj)
	
	#只有胜利了才会更新最好成绩
	if fightObj.result == 1:
		#记录角色的最好成绩
		global PurgatoryBestDict
		roleId = role.GetRoleID()
		currentData = [purgatoryId, fightRound]
		historyId, historyRound = PurgatoryBestDict.get(roleId, [0, 0])
		if purgatoryId > historyId:
			PurgatoryBestDict[roleId] = currentData
		elif purgatoryId == historyId:
			if fightRound < historyRound or historyRound == 0:
				PurgatoryBestDict[roleId] = currentData
		
		if SDHFunGather.StartFlag[SDHDefine.Purgatory] is True:
			role.SendObj(SyncBestInPurgatory, PurgatoryBestDict.get(roleId, [0, 0]))

	role.SendObj(PurgatoryRewardData, purgatoryObj)
	if fightRound:
		Event.TriggerEvent(Event.Eve_FinishPurgatory, role, (purgatoryId, fightRound))
	
	
def GetCloseValue(value, value_list):
	#返回第一个大于value的值
	for i in value_list:
		if i >= value:
			return i
	else:
		return i
	
def GetCloseValueEx(value, value_list):
	#返回第一个大于value的上一个值
	tmpValue = 0
	for i in value_list:
		if i > value:
			return tmpValue
		tmpValue = i
	else:
		return None
	
def BuyLife(fight):
	role = fight.buy_role
	if role.IsKick():
		return
	buy_life_count = fight.buy_life_count
	vipLevel = role.GetVIP()
	
	if not vipLevel:
		fight.buy_life_fun = None
	
	if buy_life_count >= 1:
		cfg = VIPConfig._VIP_BASE.get(vipLevel)
		if not cfg:
			print "GE_EXC, Purgatory can not find vip level (%s) in _VIP_BASE" % vipLevel
			return
		
		#最后一次买活了
		if fight.buy_life_count == cfg.lyTimes - 1:
			fight.buy_life_fun = None
		
		rmbCfg = PurgatoryConfig.PurgatoryFuhuo_Dict.get(buy_life_count + 1)
		if not rmbCfg:
			print "GE_EXC, Purgatory can not find buy_life_count (%s) in PurgatoryFuhuo_Dict" % buy_life_count + 1
			return
		
		#买活钱不够
		if role.GetRMB() < rmbCfg.bindRMB:
			fight.buy_life_fun = None
			return
		
		with PurgatoryBuyLife_Log:
			role.DecRMB(rmbCfg.bindRMB)
	
	fight.left_camp.create_outline_role_unit(Middle.GetRoleData(role), role.GetRoleID())
	for unit in fight.left_camp.pos_units.itervalues():
		unit.create()
	fight.play_info.append((Operate.FightMsg, 2, 0, GlobalPrompt.Purgatory_Fuhuo_Success))
	
def MonsterReward(role, purgatoryId):
	'''
	击杀怪物奖励
	@param role:
	@param purgatoryId:炼狱ID
	'''
	purgatoryObj = role.GetObj(EnumObj.PurgatoryReward)
	if not purgatoryObj:
		return
	#没有奖励
	if purgatoryId not in purgatoryObj:
		return
	#配置
	cfg = PurgatoryConfig.Purgatory_Dict.get(purgatoryId)
	if not cfg:
		print "GE_EXC, Purgatory can not find purgatoryId:(%s) in Purgatory_Dict" % purgatoryId
		return
	#杀怪个数
	killMonsterCnt = purgatoryObj[purgatoryId][0]
	if not killMonsterCnt:
		return
	
	#YY防沉迷对奖励特殊处理
	yyAntiFlag = role.GetAnti()
	if yyAntiFlag == 1:
		#根据杀怪个数获取奖励物品、金钱
		rewardItems, rewardMoney = cfg.PKR_fcm.get(killMonsterCnt, (None, None))
	elif yyAntiFlag == 0:
		#根据杀怪个数获取奖励物品、金钱
		rewardItems, rewardMoney = cfg.PKR.get(killMonsterCnt, (None, None))
	else:
		rewardItems, rewardMoney = (), 0
		role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
#	if not rewardItems:
#		print "GE_EXC, Purgatory can not find killMonsterCnt:(%s) in PKR" % killMonsterCnt
#		return
	#计算物品总个数
	itemDict = {}
	for item in rewardItems:
		if item[0] not in itemDict:
			itemDict[item[0]] = item[1]
		else:
			itemDict[item[0]] += item[1]
	if role.PackageEmptySize() < len(itemDict):
		return
	
	with PurgatoryMonsterReward_Log:
		purgatoryObj[purgatoryId][0] = 0
		
		tips = GlobalPrompt.Purgatory_Revive_Success
		
		for coding, cnt in itemDict.iteritems():
			role.AddItem(coding, cnt)
			tips += GlobalPrompt.Item_Tips % (coding, cnt)
		
		goldBuff = role.GetEarningGoldBuff()
		isHalfYearCard = False
		if Environment.EnvIsNA():
			if role.GetCD(EnumCD.Card_Year):
				isHalfYearCard = True
		else:
			if role.GetCD(EnumCD.Card_HalfYear):
				#有半年卡, 金币加成10%, 加多一条提示
				isHalfYearCard = True
		if isHalfYearCard:
			goldBuff += EnumGameConfig.Card_HalfYearGold
		
		if goldBuff:
			#有金币加成buff
			rewardMoney += rewardMoney * goldBuff / 100
			role.IncMoney(rewardMoney)
		else:
			#没有金币加成buff
			role.IncMoney(rewardMoney)
		tips += GlobalPrompt.Money_Tips % rewardMoney
		
		if not purgatoryObj[purgatoryId][0] and not purgatoryObj[purgatoryId][1]:
			del purgatoryObj[purgatoryId]
		role.SetObj(EnumObj.PurgatoryReward, purgatoryObj)
		
	role.SendObj(PurgatoryRewardData, purgatoryObj)
	
	if isHalfYearCard:
		role.Msg(2, 0, tips + GlobalPrompt.Card_GoldBuff_Tips)
	else:
		role.Msg(2, 0, tips)
	
def RatingReward(role, purgatoryId, ratingRound):
	'''
	评级奖励
	@param role:
	@param purgatoryId:炼狱ID
	@param ratingRound:评级回合数 
	'''
	purgatoryObj = role.GetObj(EnumObj.PurgatoryReward)
	if not purgatoryObj:
		return
	if purgatoryId not in purgatoryObj:
		return
	#配置
	cfg = PurgatoryConfig.Purgatory_Dict.get(purgatoryId)
	if not cfg:
		print "GE_EXC, Purgatory can not find purgatoryId:(%s) in Purgatory_Dict" % purgatoryId
		return
	#未通关
	clearRound = purgatoryObj[purgatoryId][1]
	if not clearRound:
		return
	if clearRound > 99:
		#回合数超过99强制修正
		clearRound = 99
	if clearRound > ratingRound:
		return
	#YY防沉迷对奖励特殊处理
	yyAntiFlag = role.GetAnti()
	if yyAntiFlag == 1:
		#根据回合数拿到奖励物品
		rewardItems = cfg.PRR_fcm.get(ratingRound)
	elif yyAntiFlag == 0:
		#根据回合数拿到奖励物品
		rewardItems = cfg.PRR.get(ratingRound)
	else:
		role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
		rewardItems = ()
		
#	if not rewardItems:
#		print "GE_EXC, Purgatory RatingReward can not find ratingRound:(%s) in PRR" % ratingRound
#		return

	#背包满
	if role.PackageEmptySize() < len(rewardItems):
		return
	
	with PurgatoryRatingReward_Log:
		purgatoryObj[purgatoryId][1] = 0
		
		tips = GlobalPrompt.Purgatory_Revive_Success
		for item in rewardItems:
			tips += GlobalPrompt.Item_Tips % item
			role.AddItem(*item)
		
		if not purgatoryObj[purgatoryId][0] and not purgatoryObj[purgatoryId][1]:
			del purgatoryObj[purgatoryId]
		role.SetObj(EnumObj.PurgatoryReward, purgatoryObj)
		
	role.SendObj(PurgatoryRewardData, purgatoryObj)
	role.Msg(2, 0, tips)
	
#===============================================================================
# 上线同步客户端
#===============================================================================
def SyncDemonsRewardData(role, param):
	roleId = role.GetRoleID()
	if SDHFunGather.StartFlag[SDHDefine.Purgatory] is True:
		role.SendObj(SyncBestInPurgatory, PurgatoryBestDict.get(roleId, [0, 0]))
		
	role.SendObj(PurgatoryRewardData, role.GetObj(EnumObj.PurgatoryReward))
	
	purgatoyrID = role.GetTempObj(EnumTempObj.PurgatoryInFight)
	if not purgatoyrID:
		return
	camp = role.GetTempObj(EnumTempObj.FightCamp)
	if camp is None:
		return
	role.SendObj(PurgatoryJoinID, (purgatoyrID, camp.fight.round))
	
def RoleDayClear(role, param):
	role.GetObj(EnumObj.PurgatoryReward)[0] = {}
	role.SendObj(PurgatoryRewardData, role.GetObj(EnumObj.PurgatoryReward))
	
def AfterLogin(role, param):
	if 0 not in role.GetObj(EnumObj.PurgatoryReward):
		role.GetObj(EnumObj.PurgatoryReward)[0] = {}
	
#===============================================================================
# 客户端请求
#===============================================================================
def RequestJoinPurgatory(role, msg):
	'''
	请求进入炼狱
	@param role:
	@param msg:炼狱ID
	'''
	if not msg:
		return
	
	if msg in role.GetObj(EnumObj.PurgatoryReward):
		return
	
	JoinDemons(role, msg)

def RequestMonsterRward(role, msg):
	'''
	请求领取击杀怪物奖励
	@param role:
	@param msg:炼狱ID
	'''
	if not msg:
		return
	
	MonsterReward(role, msg)
	
def RequestRatingReward(role, msg):
	'''
	请求领取评级奖励
	@param role:
	@param msg:炼狱ID, 评级回合
	'''
	if not msg:
		return
	purgatoryId, clearRound = msg
	
	RatingReward(role, purgatoryId, clearRound)
	
def RequestOnekeyReward(role, msg):
	'''
	请求一键收益
	@param role:
	@param msg:
	'''
	if not msg: return
	
	#次数
	if role.GetDI8(EnumDayInt8.PurgatoryCnt) >= EnumGameConfig.PurgatoryMaxCnt:
		return
	if role.GetVIP() < EnumGameConfig.PurgatoryOnekeyVIP:
		return
	
	purgatoryId, ratingRound = msg
	
	if len(role.GetObj(EnumObj.PurgatoryReward)) > 1:
		return
	
	todayMaxRecord = role.GetObj(EnumObj.PurgatoryReward).get(0)
	if not todayMaxRecord:
		return
	
	if purgatoryId not in todayMaxRecord:
		return
	killMonsterCnt, clearRound = todayMaxRecord[purgatoryId]
	
	#配置
	cfg = PurgatoryConfig.Purgatory_Dict.get(purgatoryId)
	if not cfg:
		print "GE_EXC, Purgatory can not find purgatoryId:(%s) in Purgatory_Dict" % purgatoryId
		return
	
	itemCnt = 0
	itemDict = {}
	rewardMoney = 0
	yyAntiFlag = role.GetAnti()
	#根据杀怪个数获取奖励物品、金钱
	if killMonsterCnt:
		#YY防沉迷对奖励特殊处理
		if yyAntiFlag == 1:
			rewardItems, rewardMoney = cfg.PKR_fcm.get(killMonsterCnt, (None, None))
		elif yyAntiFlag == 0:
			rewardItems, rewardMoney = cfg.PKR.get(killMonsterCnt, (None, None))
		else:
			rewardItems, rewardMoney = [], 0
			role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
		
#		if not rewardItems:
#			print "GE_EXC, Purgatory can not find killMonsterCnt:(%s) in PKR" % killMonsterCnt
#			return

		#计算物品总个数
		for item in rewardItems:
			if item[0] not in itemDict:
				itemDict[item[0]] = item[1]
			else:
				itemDict[item[0]] += item[1]
		itemCnt = len(itemDict)
		if role.PackageEmptySize() < itemCnt:
			return
	
	ratingReward = []
	if ratingRound:
		if clearRound > 99:
			#回合数超过99强制修正
			clearRound = 99
		if clearRound > ratingRound:
			return
		#YY防沉迷对奖励特殊处理
		if yyAntiFlag == 1:
			ratingReward = cfg.PRR_fcm.get(ratingRound)
		elif yyAntiFlag == 0:
			ratingReward = cfg.PRR.get(ratingRound)
		else:
			role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
		#根据回合数拿到奖励物品
#		if not ratingReward:
#			print "GE_EXC, Purgatory RequestOnekeyReward can not find ratingRound:(%s) in PRR" % ratingRound
#			return

		#背包满
		itemCnt += len(ratingReward)
		if role.PackageEmptySize() < itemCnt:
			return
	
	with PurgatoryOnekeyReward_Log:
		role.IncDI8(EnumDayInt8.PurgatoryCnt, 1)
		tips = GlobalPrompt.Purgatory_Revive_Success
		#击杀怪物
		for coding, cnt in itemDict.iteritems():
			role.AddItem(coding, cnt)
			tips += GlobalPrompt.Item_Tips % (coding, cnt)
		#评级
		for item in ratingReward:
			tips += GlobalPrompt.Item_Tips % item
			role.AddItem(*item)
		
		if rewardMoney:
			goldBuff = role.GetEarningGoldBuff()
			isHalfYearCard = False
			if Environment.EnvIsNA():
				if role.GetCD(EnumCD.Card_Year):
					isHalfYearCard = True
			else:
				if role.GetCD(EnumCD.Card_HalfYear):
					#有半年卡, 金币加成10%, 加多一条提示
					isHalfYearCard = True
			if isHalfYearCard:
				goldBuff += EnumGameConfig.Card_HalfYearGold
				
			if goldBuff:
				#有金币加成buff
				rewardMoney += rewardMoney * goldBuff / 100
				role.IncMoney(rewardMoney)
			else:
				#没有金币加成buff
				role.IncMoney(rewardMoney)
			tips += GlobalPrompt.Money_Tips % rewardMoney
		
	#每日必做 -- 进入炼狱
	Event.TriggerEvent(Event.Eve_DoDailyDo, role, (DailyDo.Daily_P, 1))
	
	Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_Purgatory, 1))
	
	if rewardMoney:
		if isHalfYearCard:
			role.Msg(2, 0, tips + GlobalPrompt.Card_GoldBuff_Tips)
		else:
			role.Msg(2, 0, tips)
	else:
		role.Msg(2, 0, tips)
		
if "_HasLoad" not in dir():
	if (Environment.HasLogic and not Environment.IsCross) or Environment.HasWeb:
		#记录角色心魔炼狱的最好成绩 roleid-->[心魔炼狱id，轮数]
		PurgatoryBestDict = Contain.Dict("PurgatoryBestDict", (2038, 1, 1))
		
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncDemonsRewardData)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Purgatory_Join", "请求进入心魔炼狱"), RequestJoinPurgatory)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Purgatory_Monster_Reward", "请求领取心魔炼狱怪物奖励"), RequestMonsterRward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Purgatory_Rating_Reward", "请求领取心魔炼狱评级奖励"), RequestRatingReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Purgatory_OnekeyReward", "请求心魔炼狱一键收益"), RequestOnekeyReward)
		
