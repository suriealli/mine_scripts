#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.FiveGift.FiveGiftMgr")
#===============================================================================
# 五重礼
#===============================================================================
import cDateTime
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Activity.FiveGift import FiveGiftConfig, FiveGiftDefine
from Game.Role import Event
from Game.Role.Data import EnumInt8, EnumInt1, EnumObj, EnumDayInt1, EnumInt16

if "_HasLoad" not in dir():
	FIVE_GIFT_NEED_TRADE_ID = 302		#第五重礼要求购买交易ID(超值宝石礼盒)
	FIRST_GIFT_NEED_Q_POINT = 100		#第一重礼需要的Q点数
	
	#福缘选择ID对应抽奖枚举
	CHOICEID_TO_ENUM = {1: EnumInt1.FiveGiftLucky1, 2: EnumInt1.FiveGiftLucky2, 3: EnumInt1.FiveGiftLucky3}
	#礼包ID对应传闻
	GIFTID_TO_HEARSAY = None
	
def GetHearsay(giftId):
	global GIFTID_TO_HEARSAY
	
	if GIFTID_TO_HEARSAY is None:
		GIFTID_TO_HEARSAY = {1: GlobalPrompt.FIVEGIFT_HEARSAY_1, 2: GlobalPrompt.FIVEGIFT_HEARSAY_2, 
						3: GlobalPrompt.FIVEGIFT_HEARSAY_3, 4: GlobalPrompt.FIVEGIFT_HEARSAY_4, 
						5: GlobalPrompt.FIVEGIFT_HEARSAY_5}
	
	return GIFTID_TO_HEARSAY.get(giftId, "")
	
def IsFinishSecondGift(role):
	'''
	是否完成了第二重礼包(福缘礼包)
	@param role:
	'''
	#已经激活了第二重礼包
	if role.GetI8(EnumInt8.FiveGiftSecond):
		return
	
	lucky1 = role.GetI1(EnumInt1.FiveGiftLucky1)
	lucky2 = role.GetI1(EnumInt1.FiveGiftLucky2)
	lucky3 = role.GetI1(EnumInt1.FiveGiftLucky3)
	if lucky1 and lucky2 and lucky3:
		#满足条件，设置为可领取
		role.SetI8(EnumInt8.FiveGiftSecond, 1)
		
def GetFiveGiftReward(role, giftId):
	'''
	领取五重礼奖励
	@param role:
	@param giftId:
	'''
	rewardEnum = FiveGiftDefine.GIFTID_TO_REWARD_ENUM.get(giftId)
	if not rewardEnum:
		return
	
	#是否可以领取
	if role.GetI8(rewardEnum) != 1:
		return
	
	#一定要领取上一重礼包才可以领取下一重礼包
	if giftId != 1:
		lastRewardEnum = FiveGiftDefine.GIFTID_TO_REWARD_ENUM.get(giftId - 1)
		if not lastRewardEnum:
			return
		#未领取上一重礼包
		if role.GetI8(lastRewardEnum) != 2:
			return
	
	#配置
	giftConfig = FiveGiftConfig.FIVE_GIFT_BASE.get(giftId)
	if not giftConfig:
		return
	
	#设置已领取
	role.SetI8(rewardEnum, 2)
	
	#领取的是否最后的第五重奖励
	if giftId == 5:
		#设定每日首充图标出现的时间(保存时间的第二天出现图标)
		role.SetI16(EnumInt16.DayFirstPayIconShowTime, cDateTime.Days())
		#如果领取的是最后第五重奖励，此处设置每日首充已完成，防止五重礼后再充钱被认为是完成了今日的每日首充
		role.SetDI1(EnumDayInt1.DayFirstPay, 1)
	
	#第一重礼送一个武将
	if giftId == 1:
		role.AddHero(9)
	
	#奖励
	prompt = ""
	if giftConfig.rewardMoney:
		#金币奖励
		role.IncMoney(giftConfig.rewardMoney)
		#提示
		prompt = GlobalPrompt.Money_Tips % giftConfig.rewardMoney
	if giftConfig.rewardBindRMB:
		#魔晶奖励
		role.IncBindRMB(giftConfig.rewardBindRMB)
		#提示
		prompt += GlobalPrompt.BindRMB_Tips % giftConfig.rewardBindRMB
	
	for item in giftConfig.rewardItem:
		role.AddItem(*item)
		#提示字符串
		prompt += GlobalPrompt.Item_Tips % (item[0], item[1])
		
	#提示
	role.Msg(2, 0, prompt)
	
	#传闻
	cRoleMgr.Msg(1, 0, GetHearsay(giftId) % role.GetRoleName())
		
def FiveGiftLuckyDraw(role, choiceId, backFunId):
	'''
	五重礼抽奖
	@param role:
	@param choiceId:
	@param backFunId:
	'''
	luckyEnum = CHOICEID_TO_ENUM.get(choiceId)
	if not luckyEnum:
		return
	
	#是否已经抽过奖
	if role.GetI1(luckyEnum):
		return
	
	#获取配置
	luckyConfig = FiveGiftConfig.FIVE_GIFT_LUCKY_DRAW_CONFIG.get(choiceId)
	if not luckyConfig:
		return
	randomObj = FiveGiftConfig.FIVE_GIFT_LUCKY_DRAW_RANDOM.get(choiceId)
	if not randomObj:
		return
	
	#需要的货币
	if choiceId == 1:
		#金币
		if role.GetMoney() < luckyConfig.needMoney:
			return
	elif choiceId == 2:
		#神石
		if role.GetUnbindRMB() < luckyConfig.needMoney:
			return
	elif choiceId == 3:
		#神石
		if role.GetUnbindRMB() < luckyConfig.needMoney:
			return
	else:
		return
		
	#设置已经抽过奖
	role.SetI1(luckyEnum, 1)
	
	#随机奖励
	rewardMoney = randomObj.RandomOne()
	#奖励
	if choiceId == 1:
		#金币
		role.IncMoney(rewardMoney)
		#提示
		role.Msg(2, 0, GlobalPrompt.Money_Tips % rewardMoney)
	elif choiceId == 2:
		#魔晶
		role.IncBindRMB(rewardMoney)
		#提示
		role.Msg(2, 0, GlobalPrompt.BindRMB_Tips % rewardMoney)
	elif choiceId == 3:
		#魔晶
		role.IncBindRMB(rewardMoney)
		#提示
		role.Msg(2, 0, GlobalPrompt.BindRMB_Tips % rewardMoney)
	else:
		return
	
	#是否完成了第二重礼
	IsFinishSecondGift(role)
	
	#回调客户端
	role.CallBackFunction(backFunId, rewardMoney / luckyConfig.needMoney)
	
#===============================================================================
# 客户端请求
#===============================================================================
def RequestFiveGiftGetReward(role, msg):
	'''
	客户端请求领取五重礼奖励
	@param role:
	@param msg:
	'''
	giftId = msg
	
	#日志
	with TraFiveGiftGetReward:
		GetFiveGiftReward(role, giftId)
	
def RequestFiveGiftLuckyDraw(role, msg):
	'''
	客户端请求五重礼福缘抽奖
	@param role:
	@param msg:
	'''
	backFunId , data = msg
	choiceId = data
	
	#日志
	with TraFiveGiftLuckyDraw:
		FiveGiftLuckyDraw(role, choiceId, backFunId)
	
#===============================================================================
# Event
#===============================================================================
def AfterEve_QPoint(role, param):
	'''
	消费Q点后调用
	@param role:
	@param param:
	'''
	#首充第一重
	if role.GetI8(EnumInt8.FiveGiftFirst) == 0:
		#是否充值达到100Q点
		if role.GetConsumeQPoint() < FIRST_GIFT_NEED_Q_POINT:
			return
		#0表示没有不可领取状态
		role.SetI8(EnumInt8.FiveGiftFirst, 1)
		from Game.Activity.WonderfulAct import WonderfulActMgr, EnumWonderType
		WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_Inc_Fill)
		
def OnRoleLevelUp(role, param):
	'''
	升级
	@param role:
	@param param:
	'''
	#是否已经激活第三重升级礼包
	if role.GetI8(EnumInt8.FiveGiftThird):
		return
	
	#激活礼包
	if role.GetLevel() >= 35:
		role.SetI8(EnumInt8.FiveGiftThird, 1)
		
def OnMallBuy(role, param):
	'''
	神石商城购买事件触发
	@param role:
	@param param:
	'''
	#设置完成第五重礼
	if role.GetI8(EnumInt8.FiveGiftFifth) > 0:
		return
	
	#是否购买了五重礼要求的宝石礼包
	mallLimitDict = role.GetObj(EnumObj.Mall_Limit_Dict)
	if FIVE_GIFT_NEED_TRADE_ID not in mallLimitDict:
		return
	
	role.SetI8(EnumInt8.FiveGiftFifth, 1)
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		#升级事件触发
		Event.RegEvent(Event.Eve_AfterLevelUp, OnRoleLevelUp)
	if Environment.HasLogic and not Environment.IsCross:
		#Q点消费事件触发
		Event.RegEvent(Event.Eve_GamePoint, AfterEve_QPoint, index = 0)
		#神石商城购买事件触发
		Event.RegEvent(Event.Eve_AfterMallBuy, OnMallBuy)
		
		#日志
		TraFiveGiftGetReward = AutoLog.AutoTransaction("TraFiveGiftGetReward", "五重礼领取奖励")
		TraFiveGiftLuckyDraw = AutoLog.AutoTransaction("TraFiveGiftLuckyDraw", "五重礼抽奖")
		
		#注册消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Five_Gift_Get_Reward", "客户端请求领取五重礼奖励"), RequestFiveGiftGetReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Five_Gift_Lucky_Draw", "客户端请求五重礼福缘抽奖"), RequestFiveGiftLuckyDraw)
		
	