#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.AsteroidFields.AsteroidFields")
#===============================================================================
# 魔域星宫
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumFightStatistics, GlobalPrompt, EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Activity.AsteroidFields import AsteroidFieldsConfig
from Game.Fight import FightEx
from Game.Role import Event, Status
from Game.Role.Data import EnumInt1, EnumDayInt8, EnumObj


if "_HasLoad" not in dir():
	
	#日志
	Tra_EnterAsteroidField = AutoLog.AutoTransaction("Tra_EnterAsteroidField", "魔域星宫进入星域")
	Tra_AsteroidFieldsReward = AutoLog.AutoTransaction("Tra_AsteroidFieldsReward", "魔域星宫普通挑战发放奖励")
	Tra_AsteroidFieldsReward_Onekey = AutoLog.AutoTransaction("Tra_AsteroidFieldsReward_OneKey", "魔域星宫一键挑战发放奖励")
	Tra_AsteroidFieldsBuyXingdongli = AutoLog.AutoTransaction("Tra_AsteroidFieldsBuyXingdongli", "魔域星宫购买行动力")
	Tra_AsteroidFieldsResetchallenge = AutoLog.AutoTransaction("Tra_AsteroidFieldsResetchallenge", "魔域星宫重置关卡")
	#消息
	SyRoleData = AutoMessage.AllotMessage("AsteroidFields_SyRoleData", "魔域星宫同步玩家数据")



def RequestEnterAsteroidField(role, msg):
	'''
	请求进入星域
	@param role:
	@param msg:
	'''
	#如果玩家等级不符合要求，则该玩法不开放
	if role.GetLevel() < EnumGameConfig.AsteroidFields_NeedLevel:
		return
	#消息须包含请求进入的星域ID
	if not msg:
		return
	#获取请求进入的星域id
	afid = msg
	#进入该星域的等级要求
	guankacfg = AsteroidFieldsConfig.AsteroidFieldsGuanka_Dict.get(afid)
	if not guankacfg:
		print "GE_EXC, may not get config for AFId(%s) in AsteroidFieldsGuanka_Dict, a config error" % afid
		return
	aflevel = guankacfg.LevelNeeded
	#如果玩家未达到进入该星域的等级要求
	if role.GetLevel() < aflevel:
		return
	#如果玩家的行动力不足
	if EnumGameConfig.AsteroidFields_DailyInitXingdongli - role.GetDI8(EnumDayInt8.AsteroidFieldsChallengeTimes) <= 0:
		return
	#如果玩家已经在星域中了
	dailydict = role.GetObj(EnumObj.AsteroidFieldsDaily)
	if afid in dailydict:
		print "GE_EXC, role(%s) already in AsteroidField(%s)" % (role.GetRoleID(), afid)
		return
	#记录日志
	with Tra_EnterAsteroidField:
		#扣除玩家一点行动力
		role.IncDI8(EnumDayInt8.AsteroidFieldsChallengeTimes, EnumGameConfig.AsteroidFieldsXiongdongliToCost)
		#玩家进入星域
		dailydict[afid] = 0
	#同步玩家数据
	role.SendObj(SyRoleData, (role.GetObj(EnumObj.AsteroidFieldsDaily), role.GetObj(EnumObj.AsteroidFields)))
	
	Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_AsteroidFields, EnumGameConfig.AsteroidFieldsXiongdongliToCost))
	
def RequestChallenge(role, msg):
	'''
	请求挑战关卡
	@param role:
	@param msg:
	'''
	#消息不能为空
	if not msg:
		return
	#等级不符合要求，活动未开启
	if role.GetLevel() < EnumGameConfig.AsteroidFields_NeedLevel:
		return
	afid = msg
	#如果玩家不在星域中
	nowIndex = role.GetObj(EnumObj.AsteroidFieldsDaily).get(afid, None)
	if nowIndex is None:
		return
	guankacfg = AsteroidFieldsConfig.AsteroidFieldsGuanka_Dict.get(afid)
	#配置表错误
	if not guankacfg:
		print "GE_EXC, may not get config for AFId(%s) in AsteroidFieldsGuanka_Dict, a config error" % afid
		return
	if nowIndex >= guankacfg.LastIndex:
		return
	elif nowIndex == 0:
		afindex = guankacfg.FirstIndex
	else:
		afindex = nowIndex + 1
	#判断玩家是否可以进入战斗状态
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		return
	#获取战斗配置
	cfg = AsteroidFieldsConfig.AsteroidFieldsConfig_Dict.get(afindex)
	if not cfg:
		print "GE_EXC, RequestEnterAsteroidField can not find AFIndex (%s) in Config" % afindex
		return
	#开始战斗
	FightEx.PVE_AF(role, cfg.FightType, cfg.MonsterId, AfterFight, (afid, afindex, cfg))

def AfterFight(fightObj):
	'''
	战斗后处理
	@param fightObj:战斗对象
	'''
	#如果没有获取到战斗对象
	if not fightObj:
		print "GE_EXC, AsteroidFields fight error"
		return
	#如果战斗失败了
	if fightObj.result != 1:
		return
	#如果战斗胜利，则获取胜利玩家列表，这里只有一个玩家
	roles = fightObj.left_camp.roles
	if not roles:
		return
	#胜利玩家列表长度只能是1
	if len(roles) != 1:
		print "GE_EXC, There must be only one role in AsteroidFields fight"
		return
	role = list(roles)[0]
	afid, afindex, cfg = fightObj.after_fight_param
	#YY防沉迷对奖励特殊处理
	yyAntiFlag = role.GetAnti()
	if yyAntiFlag == 1:
		tmpMoney = cfg.MoneyToReward_fcm
		reward_items = cfg.GetRewardList(True)
	elif yyAntiFlag == 0:
		tmpMoney = cfg.MoneyToReward
		reward_items = cfg.GetRewardList(False)
	else:
		tmpMoney = 0
		reward_items = ()
		role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
	
	#取出玩家历史数据
	historydata = role.GetObj(EnumObj.AsteroidFields)
	#取出玩家当日数据
	dailydata = role.GetObj(EnumObj.AsteroidFieldsDaily)
	
	guankacfg = AsteroidFieldsConfig.AsteroidFieldsGuanka_Dict.get(afid)
	#配置表错误
	if not guankacfg:
		print "GE_EXC, may not get config for AFId(%s) in AsteroidFieldsGuanka_Dict, a config error" % afid
		return

	#战斗结束后发放奖励
	with Tra_AsteroidFieldsReward:
		#更新玩家通关的最大index
		historyIndex = historydata.get(afid)
		if not historyIndex:
			if afindex != guankacfg.FirstIndex:
				print "GE_EXC, error in AsteroidField afindex != FirstIndex"
				return
			historydata[afid] = afindex
		else:
			if afindex > historyIndex:
				if afindex != historyIndex + 1:
					print "GE_EXC, error in AsteroidField afindex != historyIndex + 1"
					return
				else:
					historydata[afid] = afindex

		#更新玩家的当日数据
		dailyIndex = dailydata.get(afid)
		if not dailyIndex:
			if afindex != guankacfg.FirstIndex:
				print "GE_EXC, error in AsteroidField afindex != FirstIndex"
				return
			dailydata[afid] = afindex
		else:
			if afindex > dailyIndex:
				if afindex != dailyIndex + 1:
					print "GE_EXC, error in AsteroidField afindex != dailyIndex + 1"
					return
			dailydata[afid] = afindex

		#奖励金币
		role.IncMoney(tmpMoney)
		#奖励物品
		role_AddItem = role.AddItem
		for code, cnt in reward_items:
			role_AddItem(code, cnt)
	#展示奖励
	roleID = role.GetRoleID()
	fightObj.set_fight_statistics(roleID, EnumFightStatistics.EnumMoney, cfg.MoneyToReward)
	fightObj.set_fight_statistics(roleID, EnumFightStatistics.EnumItems, reward_items)
	
	#同步玩家数据
	role.SendObj(SyRoleData, (role.GetObj(EnumObj.AsteroidFieldsDaily), role.GetObj(EnumObj.AsteroidFields)))

def OneKeyChallenge(role, msg):
	'''
	请求一键挑战
	@param role:
	@param msg:
	'''	
	#消息不可为空
	if not msg:
		return
	afid = msg
	
	#没有花行动力
	#取出玩家当日数据
	dailyDict = role.GetObj(EnumObj.AsteroidFieldsDaily)
	dailyIndex = dailyDict.get(afid, None)
	if dailyIndex is None:
		return
	#检测曾经是否通关过
	maxindex = role.GetObj(EnumObj.AsteroidFields).get(afid)
	if not maxindex:
		return
	#当前就处在最高的进度，不能使用一键挑战
	if dailyIndex >= maxindex:
		return
	awardMoney = 0
	awardItemDict = {}
	AFGet = AsteroidFieldsConfig.AsteroidFieldsConfig_Dict.get
	guankacfg = AsteroidFieldsConfig.AsteroidFieldsGuanka_Dict.get(afid)
	#配置表错误
	if not guankacfg:
		print "GE_EXC, may not get config for AFId(%s) in AsteroidFieldsGuanka_Dict, a config error" % afid
		return
	#遍历发放奖励
	if dailyIndex == 0:
		startIndex = guankacfg.FirstIndex
	else:
		startIndex = dailyIndex + 1
	for afindex in xrange(startIndex , maxindex + 1):
		cfg = AFGet(afindex)
		if not cfg:
			print "GE_EXC, no cfg in OneKeyChallenge (%s)" % afindex
			return
		################################################
		#YY防沉迷对奖励特殊处理
		yyAntiFlag = role.GetAnti()
		if yyAntiFlag == 1:
			tmpMoney = cfg.MoneyToReward_fcm
			tmpItems = cfg.GetRewardList(True)
		elif yyAntiFlag == 0:
			tmpMoney = cfg.MoneyToReward
			tmpItems = cfg.GetRewardList(False)
		else:
			tmpMoney = 0
			tmpItems = {}
			role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
		################################################
			
		awardMoney += tmpMoney
		for itemCoding, itemCnt in tmpItems:
			awardItemDict[itemCoding] = awardItemDict.get(itemCoding, 0) + itemCnt
	
	rewardMsg = GlobalPrompt.AsteroidFields_Tips_OneKeyAward
	#日志
	with Tra_AsteroidFieldsReward_Onekey:
		#更新玩家当日的通关进度
		dailyDict[afid] = maxindex
		role.IncMoney(awardMoney)
		rewardMsg = rewardMsg + GlobalPrompt.Money_Tips % awardMoney
		role_AddItem = role.AddItem
		for code, cnt in awardItemDict.iteritems():
			role_AddItem(code, cnt)
			rewardMsg = rewardMsg + GlobalPrompt.Item_Tips % (code, cnt)

	#同步玩家数据
	role.SendObj(SyRoleData, (role.GetObj(EnumObj.AsteroidFieldsDaily), role.GetObj(EnumObj.AsteroidFields)))
	#发放奖励提示
	role.Msg(2, 0, rewardMsg)

def Resetchallenge(role, msg):
	'''
	请求重置关卡
	@param role:
	@param msg:
	'''
	#获取当前通关进度
	afid = msg
	guankacfg = AsteroidFieldsConfig.AsteroidFieldsGuanka_Dict.get(afid)
	if not guankacfg:
		print "GE_EXC, may not get config for AFId(%s) in AsteroidFieldsGuanka_Dict, a config error" % afid
		return
	
	dailydata = role.GetObj(EnumObj.AsteroidFieldsDaily)
	dailyindex = dailydata.get(afid)
	if not dailyindex:
		return
	
	#检测曾经是否通关过
	maxindex = role.GetObj(EnumObj.AsteroidFields).get(afid)
	if not maxindex:
		return
	#重置关卡
	roleID = role.GetRoleID()
	#日志
	with Tra_AsteroidFieldsResetchallenge:
		if afid in dailydata:
			del dailydata[afid]
			AutoLog.LogBase(roleID, AutoLog.eveAsteroidFieldsReset, afid)
		
	#通知服务端
	role.SendObj(SyRoleData, (role.GetObj(EnumObj.AsteroidFieldsDaily), role.GetObj(EnumObj.AsteroidFields)))

def RequestBuyXiongdongli(role, msg):
	'''
	请求购买行动力
	@param role:
	@param msg:
	'''
	#如果玩家等级不足,活动尚未开放
	if role.GetLevel() < EnumGameConfig.AsteroidFields_NeedLevel:
		return
	#每天最多买两次
	if role.GetDI8(EnumDayInt8.AsteroidFieldsBuyTimes) >= 2:
		return
	#获取玩家的本次购买次数
	BuyTimes = role.GetDI8(EnumDayInt8.AsteroidFieldsBuyTimes) + 1
	#依据购买次数给出价格
	price = EnumGameConfig.AsteroidFields_XingdongliPrice.get(BuyTimes)
	#版本判断
	if Environment.EnvIsNA():
		price = EnumGameConfig.AsteroidFields_XingdongliPrice_NA.get(BuyTimes)
	elif Environment.EnvIsRU():
		price = EnumGameConfig.AsteroidFields_XingdongliPrice_RU.get(BuyTimes)
	if not price:
		print "GE_EXC, may not get AsteroidFields_XingdongliPrice for role(%s)'s %s BuyTime" % (role.GetRoleID(), BuyTimes)
		return
	#检测玩家神石是否足够
	if role.GetUnbindRMB() < price:
		return
	#日志
	with Tra_AsteroidFieldsBuyXingdongli:
		#玩家购买行动力次数+1
		role.IncDI8(EnumDayInt8.AsteroidFieldsBuyTimes, 1)
		#扣除神石
		role.DecUnbindRMB(price)
		#玩家行动力+1
		role.DecDI8(EnumDayInt8.AsteroidFieldsChallengeTimes, 1)
		
def RequestEnterAsteroidOpen(role, msg):
	#打开面板时发送玩家数据
	role.SendObj(SyRoleData, (role.GetObj(EnumObj.AsteroidFieldsDaily), role.GetObj(EnumObj.AsteroidFields)))

def DailyClear(role, param):
	'''
	每日清理
	@param role:
	@param param:
	'''
	#重置每日通关进度
	role.SetObj(EnumObj.AsteroidFieldsDaily, {})

if "_HasLoad" not in dir():
	
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, DailyClear)
	
	if not Environment.IsCross and Environment.HasLogic:
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("AsteroidFieldsRequestOpen", "魔域星宫打开面板"), RequestEnterAsteroidOpen)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("AsteroidFieldsRequestEnterAsteroidField", "魔域星宫请求进入魔域"), RequestEnterAsteroidField)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("AsteroidFieldsRequestChallenge", "魔域星宫请求挑战关卡"), RequestChallenge)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("AsteroidFieldsOneKeyChallenge", "魔域星宫一键挑战"), OneKeyChallenge)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("AsteroidFieldsResetchallenge", "魔域星宫重置关卡"), Resetchallenge)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("AsteroidFieldsRequestBuyXiongdongli", "魔域星宫请求购买行动力"), RequestBuyXiongdongli)

