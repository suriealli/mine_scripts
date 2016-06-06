#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.VIP.Cards")
#===============================================================================
# 月卡
#===============================================================================
import Environment
import cRoleMgr
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig, EnumSocial
from ComplexServer.Log import AutoLog
from Game.Activity.WonderfulAct import WonderfulActMgr, EnumWonderType
from Game.Role import Event, Call
from Game.Role.Data import EnumObj, EnumCD, EnumInt1, EnumInt8, EnumTempObj
from Game.VIP import VIPConfig
from Game.Role.Mail import Mail
from Game.SuperCards import SuperCards

if "_HasLoad" not in dir():
	WEEK_CARD = 1		#周卡ID
	MONTH_CARD = 2		#月卡
	HALFYEAR_CARD = 3	#半年卡
	QUARTER_CARD = 4	#季度卡ID
	YEAR_CARD = 5		#年卡ID
	
	CardData = AutoMessage.AllotMessage("CardData", "月卡数据")
	CardFail = AutoMessage.AllotMessage("CardFail", "月卡时效")
	CardUnionMembers = AutoMessage.AllotMessage("CardUnionMembers", "月卡赠送公会成员")
	
	CardBuy_Log = AutoLog.AutoTransaction("CardBuy_Log", "月卡购买日志")
	CardRenewals_Log = AutoLog.AutoTransaction("CardRenewals_Log", "月卡续费日志")
	CardReviveFanquan_Log = AutoLog.AutoTransaction("CardReviveFanquan_Log", "月卡领取返券日志")
	CardGive_Log = AutoLog.AutoTransaction("CardGive_Log", "月卡赠送日志")
	CardRevive_Log = AutoLog.AutoTransaction("CardRevive_Log", "收到月卡日志")
	
	CardIdToEnumCD = {1:EnumCD.Card_Week, 2:EnumCD.Card_Month, 3:EnumCD.Card_HalfYear, 4:EnumCD.Card_Quarter, 5:EnumCD.Card_Year}
	
def BuyCard(role, cardID):
	'''
	开通
	@param role:
	@param cardID:卡片ID--周卡、月卡、半年卡
	'''
	cfg = VIPConfig.Cards_Dict.get(cardID)
	if not cfg:
		print "GE_EXC, Cards can not find cardID (%s) in Cards_Dict" % cardID
		return
	
	if Environment.EnvIsYY():
		if role.GetUnbindRMB_Q() < cfg.unbindRMB:
			return
	else:
		if role.GetUnbindRMB() < cfg.unbindRMB:
			return
	
	#非北美版本没有季度卡和年卡
	if not Environment.EnvIsNA():
		if cardID in (QUARTER_CARD, YEAR_CARD):
			return
	
	global CardIdToEnumCD
	if cardID not in CardIdToEnumCD:
		return
	if role.GetCD(CardIdToEnumCD[cardID]):
		return
	
	with CardBuy_Log:
		if Environment.EnvIsYY():
			role.DecUnbindRMB_Q(cfg.unbindRMB)
		else:
			role.DecUnbindRMB(cfg.unbindRMB)
		if cardID not in role.GetObj(EnumObj.CardsDict):
			role.GetObj(EnumObj.CardsDict)[cardID] = 0
		role.GetObj(EnumObj.CardsIsVaild)[cardID] = 1
		role.SetCD(CardIdToEnumCD[cardID], cfg.time)
		role.SendObj(CardData, role.GetObj(EnumObj.CardsDict))
		
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveCardsTime, (0, cfg.time))
		CardAct(role, cardID, 1)
		if Environment.EnvIsYY():
			if cardID == WEEK_CARD:
				Mail.SendMail(role.GetRoleID(), GlobalPrompt.YYCard_Mail_Title2, GlobalPrompt.YYCard_Mail_Send, \
						GlobalPrompt.YYCard_Mail_Content2, unbindrmb = cfg.unbindRMB)
			else:
				if cardID == MONTH_CARD:
					SuperCards.AcTiveSuperCard(role, 30)
				elif cardID == HALFYEAR_CARD:
					SuperCards.AcTiveSuperCard(role, 180)
				Mail.SendMail(role.GetRoleID(), GlobalPrompt.YYCard_Mail_Title, GlobalPrompt.YYCard_Mail_Send, \
							GlobalPrompt.YYCard_Mail_Content, unbindrmb = cfg.unbindRMB)
	
	buyTips = GlobalPrompt.ReturnBuyCardTips(cardID)
	if buyTips:
		cRoleMgr.Msg(1, 0, buyTips % role.GetRoleName())
	
def Renewals(role, cardID):
	'''
	续费
	@param role:
	@param cardID:卡片ID
	'''
	if cardID not in role.GetObj(EnumObj.CardsDict):
		return
	
	cfg = VIPConfig.Cards_Dict.get(cardID)
	if not cfg:
		print "GE_EXC, Cards can not find cardID (%s) in Cards_Dict" % cardID
		return
	
	if Environment.EnvIsYY():
		if role.GetUnbindRMB_Q() < cfg.unbindRMB:
			return
	else:
		if role.GetUnbindRMB() < cfg.unbindRMB:
			return
	
	global CardIdToEnumCD
	if cardID not in CardIdToEnumCD:
		return
	
	with CardRenewals_Log:
		if Environment.EnvIsYY():
			role.DecUnbindRMB_Q(cfg.unbindRMB)
		else:
			role.DecUnbindRMB(cfg.unbindRMB)
		oldTime = role.GetCD(CardIdToEnumCD[cardID])
		newTime = oldTime + cfg.time
		role.SetCD(CardIdToEnumCD[cardID], oldTime + cfg.time)
		
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveCardsTime, (oldTime, newTime))
		
		CardAct(role, cardID, 1)
		if Environment.EnvIsYY():
			if cardID == MONTH_CARD:
				SuperCards.AcTiveSuperCard(role, 30)
			elif cardID == HALFYEAR_CARD:
				SuperCards.AcTiveSuperCard(role, 180)
			Mail.SendMail(role.GetRoleID(), GlobalPrompt.YYCard_Mail_Title, GlobalPrompt.YYCard_Mail_Send, \
						GlobalPrompt.YYCard_Mail_Content, unbindrmb = cfg.unbindRMB)
	
	buyTips = GlobalPrompt.ReturnBuyCardTips(cardID)
	if buyTips:
		cRoleMgr.Msg(1, 0, buyTips % role.GetRoleName())
		
def CardAct(role, cardID, cnt):
	#拥有卡片后的的一些相关处理
	if cardID == WEEK_CARD:#首次购买周卡
		if not role.GetI1(EnumInt1.WeekCardFirst):
			role.SetI1(EnumInt1.WeekCardFirst, 1)
	else:
		if not role.GetI1(EnumInt1.MonthCardFirst):
			role.SetI1(EnumInt1.MonthCardFirst, 1)
		if not role.GetI8(EnumInt8.FiveGiftForth):
			role.SetI8(EnumInt8.FiveGiftForth, 1)
			
		#重置竞技场挑战CD
		role.SetCD(EnumCD.JJC_Challenge_CD, 0)
		
		role.SetCD(EnumCD.FT_JJC_CD, 0)
		
		Event.TriggerEvent(Event.Eve_BuyMonthOrYearCard, role)
		
	for _ in xrange(cnt):
		WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_Inc_Card, [role, cardID])
	
def Give(role, (friendRoleID, cardID, cnt)):
	'''
	赠送好友月卡
	@param role:
	@param friendRoleID:
	'''
	#是否本地角色
	from Game.Role import KuaFu
	if not KuaFu.IsLocalRoleByRoleID(friendRoleID):
		return
	#非北美版本没有季度卡和年卡
	if not Environment.EnvIsNA():
		if cardID in (QUARTER_CARD, YEAR_CARD):
			return
	cfg = VIPConfig.Cards_Dict.get(cardID)
	if not cfg:
		print "GE_EXC, Cards Give can not find cardID (%s) in Cards_Dict" % cardID
		return
	
	costRMB = cfg.unbindRMB * cnt
	#不够钱
	if Environment.EnvIsYY():
		if role.GetUnbindRMB_Q() < costRMB:
			return
	else:
		if role.GetUnbindRMB() < costRMB:
			return
	
	#好友字典
	FriendDict = role.GetObj(EnumObj.Social_Friend)
	
	friendRole = cRoleMgr.FindRoleByRoleID(friendRoleID)
	if friendRoleID in FriendDict:
		#好友列表的需要判断等级, 公会的不需要判断等级
		if friendRole and friendRole.GetLevel() < EnumGameConfig.Card_BuyLevelLimit:
			#在线的话判断当前实时等级是否满足条件
			return
		elif FriendDict[friendRoleID][EnumSocial.RoleLevelKey] < EnumGameConfig.Card_BuyLevelLimit:
			#不在线的判断好友字典中的好友等级是否满足条件
			return
	
	roleID = role.GetRoleID()
	with CardGive_Log:
		if Environment.EnvIsYY():
			role.DecUnbindRMB_Q(costRMB)
			Mail.SendMail(role.GetRoleID(), GlobalPrompt.YYCard_Mail_Title, GlobalPrompt.YYCard_Mail_Send, \
						GlobalPrompt.YYCard_MailS_Content, unbindrmb = costRMB)
		else:
			role.DecUnbindRMB(costRMB)
			
		AutoLog.LogBase(roleID, AutoLog.eveGiveCard, (friendRoleID, cardID))
	
	Call.LocalDBCall(friendRoleID, GiveCard, (roleID, role.GetRoleName(), cardID, cnt))
	
	role.Msg(2, 0, GlobalPrompt.Card_Give)
	
def GiveCard(role, param):
	#离线调用函数, 不要修改
	giveRoleID, giveRoleName, cardID, cnt = param
	
	cfg = VIPConfig.Cards_Dict.get(cardID)
	if not cfg:
		print "GE_EXC, Cards can not find cardID (%s) in Cards_Dict" % cardID
		return
	
	global CardIdToEnumCD
	if cardID not in CardIdToEnumCD:
		return
	
	if cardID not in role.GetObj(EnumObj.CardsDict):
		role.GetObj(EnumObj.CardsDict)[cardID] = 0
	
	with CardRevive_Log:
		oldTime = role.GetCD(CardIdToEnumCD[cardID])
		newTime = oldTime + cfg.time * cnt
		role.SetCD(CardIdToEnumCD[cardID], newTime)
		
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveReviveCard, (giveRoleID, cardID, oldTime, newTime))
		
		CardAct(role, cardID, cnt)
		
		role.SendObj(CardData, role.GetObj(EnumObj.CardsDict))
		if Environment.EnvIsYY():
			if cardID == MONTH_CARD:
				SuperCards.AcTiveSuperCard(role, 30)
			elif cardID == HALFYEAR_CARD:
				SuperCards.AcTiveSuperCard(role, 180)
		
		Mail.SendMail(role.GetRoleID(), GlobalPrompt.CardReviveMail_Title, GlobalPrompt.CardReviveMail_Sender, GlobalPrompt.Card_Revive % (giveRoleName, GlobalPrompt.ReturnCardName(cardID)))
		
	role.Msg(2, 0, GlobalPrompt.Card_Revive % (giveRoleName, GlobalPrompt.ReturnCardName(cardID)))
	
def OpenGive(role):
	'''
	返回所有公会成员 -- 10sCD
	@param role:
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	if role.GetCD(EnumCD.CardUMCD):
		role.SendObj(CardUnionMembers, role.GetTempObj(EnumTempObj.CardUM))
		return
	
	role.SetCD(EnumCD.CardUMCD, 10)
	memberList = [(ID, member[1], member[5]) for (ID, member) in unionObj.members.iteritems()]
	role.SendObj(CardUnionMembers, memberList)
	role.SetTempObj(EnumTempObj.CardUM, memberList)
	
def ReviveFanquan(role, cardID):
	'''
	领取返券
	@param role:
	@param msg:cardID
	'''
	#没有买过
	if cardID not in role.GetObj(EnumObj.CardsDict):
		return
	
	#失效了
	global CardIdToEnumCD
	if cardID not in CardIdToEnumCD: return
	if not role.GetCD(CardIdToEnumCD[cardID]):
		return
	
	#领过了
	if role.GetObj(EnumObj.CardsDict)[cardID]:
		return
	
	cfg = VIPConfig.Cards_Dict.get(cardID)
	if not cfg:
		print "GE_EXC, Cards can not find cardID (%s) in Cards_Dict" % cardID
		return
	
	with CardReviveFanquan_Log:
		role.GetObj(EnumObj.CardsDict)[cardID] = 1
		role.IncBindRMB(cfg.fanquan)
		role.SendObj(CardData, role.GetObj(EnumObj.CardsDict))
	
	role.Msg(2, 0, GlobalPrompt.Card_Award % cfg.fanquan)
	
def ReviveFanquanAndChest(role, cardId):
	'''
	领取魔晶和宝箱
	@param role:
	@param cardId:
	'''
	#没有买过
	if cardId not in role.GetObj(EnumObj.CardsDict):
		return
	
	#失效了
	global CardIdToEnumCD
	if cardId not in CardIdToEnumCD:
		return
	if not role.GetCD(CardIdToEnumCD[cardId]):
		return
	
	#领过了
	if role.GetObj(EnumObj.CardsDict)[cardId]:
		return
	
	cfg = VIPConfig.Cards_Dict.get(cardId)
	if not cfg:
		print "GE_EXC, Cards can not find cardId (%s) in Cards_Dict" % cardId
		return
	
	with CardReviveFanquan_Log:
		role.GetObj(EnumObj.CardsDict)[cardId] = 1
		role.IncBindRMB(cfg.fanquan)
		role.AddItem(cfg.chestCoding, 1)
		role.SendObj(CardData, role.GetObj(EnumObj.CardsDict))
	
	#提示
	prompt = GlobalPrompt.BindRMB_Tips % cfg.fanquan + GlobalPrompt.Item_Tips % (cfg.chestCoding, 1)
	role.Msg(2, 0, prompt)
	
#===============================================================================
# 上线 同步
#===============================================================================
def SyncCardsData(role, param):
	if role.GetLevel() < EnumGameConfig.Card_BuyLevelLimit:
		return
	role.SendObj(CardData, role.GetObj(EnumObj.CardsDict))
	
	global CardIdToEnumCD
	for cardID in role.GetObj(EnumObj.CardsIsVaild):
		if cardID not in CardIdToEnumCD:
			continue
		#下线期间失效
		if not role.GetCD(CardIdToEnumCD[cardID]) and role.GetObj(EnumObj.CardsIsVaild)[cardID] == 1:
			role.GetObj(EnumObj.CardsIsVaild)[cardID] = 0
			role.SendObj(CardFail, cardID)

def AfterDay(role, param):
	if role.GetLevel() < EnumGameConfig.Card_BuyLevelLimit:
		return
	
	#每天零点清理返券领取状态
	cardDict = role.GetObj(EnumObj.CardsDict)
	if not cardDict:
		return
	
	for cardId in cardDict:
		cardDict[cardId] = 0
	
	role.SendObj(CardData, role.GetObj(EnumObj.CardsDict))
	
def AfterLevelUp(role, param):
	#玩家等级到达32级, 体验半小时月卡功能
	if role.GetLevel() != EnumGameConfig.Card_BuyLevelLimit:
		return
	
	role.SetCD(CardIdToEnumCD[2], 1800)
	role.GetObj(EnumObj.CardsDict)[2] = 0
	role.SendObj(CardData, role.GetObj(EnumObj.CardsDict))
	#记录月卡有效
	role.SetObj(EnumObj.CardsIsVaild, {2 : 1})
	#重置竞技场挑战CD
	role.SetCD(EnumCD.JJC_Challenge_CD, 0)
	role.SetCD(EnumCD.FT_JJC_CD, 0)
	
def ClientLost(role, param):
	#检测月卡是否失效
	global CardIdToEnumCD
	for cardID in role.GetObj(EnumObj.CardsIsVaild):
		if cardID not in CardIdToEnumCD:
			continue
		if role.GetCD(CardIdToEnumCD[cardID]):
			continue
		role.GetObj(EnumObj.CardsIsVaild)[cardID] = 0
#===============================================================================
# 客户端请求
#===============================================================================
def RequestBuyCard(role, msg):
	if not msg:
		return
	if role.GetLevel() < EnumGameConfig.Card_BuyLevelLimit:
		return
	
	BuyCard(role, msg)
	
def RequestRenewals(role, msg):
	if not msg:
		return
	if role.GetLevel() < EnumGameConfig.Card_BuyLevelLimit:
		return
	
	Renewals(role, msg)

def RequestGive(role, msg):
	if not msg:
		return
	if role.GetLevel() < EnumGameConfig.Card_BuyLevelLimit:
		return
	
	#版本判断
	if Environment.EnvIsNA():
		#北美版屏蔽此功能
		return
	
	Give(role, msg)
	
def RequestOpenGive(role, msg):
	if role.GetLevel() < EnumGameConfig.Card_BuyLevelLimit:
		return
	
	OpenGive(role)
	
def RequestReviveFanquan(role, msg):
	if not msg:
		return
	if role.GetLevel() < EnumGameConfig.Card_BuyLevelLimit:
		return
	
	#各版本判断
	if Environment.EnvIsNA():
		#北美版
		cardId = msg
		ReviveFanquanAndChest(role, cardId)
	else:
		#其他版本
		ReviveFanquan(role, msg)
	
if "_HasLoad" not in dir():
	Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncCardsData)
	Event.RegEvent(Event.Eve_RoleDayClear, AfterDay)
	Event.RegEvent(Event.Eve_AfterLevelUp, AfterLevelUp)
	Event.RegEvent(Event.Eve_ClientLost, ClientLost)
	
	if Environment.HasLogic:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Cards_Buy", "请求购买月卡"), RequestBuyCard)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Cards_Renewals", "请求续费"), RequestRenewals)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Cards_ReviveFanquan", "请求领取返券"), RequestReviveFanquan)
		
	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Cards_Give", "请求赠送"), RequestGive)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Cards_OpenGive", "请求打开赠送"), RequestOpenGive)
	
	