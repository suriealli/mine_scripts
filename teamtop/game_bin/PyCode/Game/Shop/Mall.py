#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Shop.Mall")
#===============================================================================
# 商城模块
#===============================================================================
import datetime
import cRoleMgr
import cDateTime
import DynamicPath
import Environment
from Util.File import TabFile
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt, EnumSocial
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Role.Data import EnumCD
from Game.Shop import Trade
from Game.SysData import WorldData
from Game.Role.Data import EnumObj, EnumTempObj, EnumDayInt1, EnumInt32
from Game.Activity.HappyNewYear import NewYearDiscount
from Game.Role.Mail import Mail
from Game.Activity.DoubleEleven import ElevenMallReward


if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("Shop")
	
	MallConfig_Dict = {}
	
	CouponsConfig_Dict = {}
	
	
	
	

def GetDiscountItem(role, itemCoding, cnt):
	packageMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	codingGatherDict = packageMgr.codingGather.get(itemCoding)
	if not codingGatherDict:
		return None
	
	itemIds = set()
	hascnt = 0
	for itemId, item in codingGatherDict.iteritems():
		if item.IsDeadTime():
			continue
		itemIds.add(itemId)
		hascnt += 1
		if hascnt >= cnt:
			return itemIds
	return itemIds


class Mall(Trade.ShopBase):
	FilePath = DynamicPath.DynamicFolder(DynamicPath.ConfigPath).AppendPath("Shop").FilePath("Mall.txt")
	def __init__(self):
		self.tradeId = int#名字必须这样
		self.goodsId = int#物品coding,宠物类型，翅膀类型，英雄编号
		self.goodsType = int#1普通物品，2 宠物 3， 翅膀 4，英雄
		self.goodsName = str
		self.needLevel = int#
		self.needVIP = int
		self.needDay = self.GetEvalByString
		self.dayLimitCnt = int#每日限购
		self.limitCnt = int#永久限购
		self.baseRMB = int#基础价格
		self.discountRMB = int#折扣价格
		self.discountForever = int#是否永久打折

		self.discountCardCoding = int#折扣券
		self.VipLevelDiscount = int#VIP折扣需要的VIP等级
		self.CanGiving = int
		self.QRMB = int # QRMB 是否只能充值神石购买，并且不能放在购物车，不能使用代金券
		self.startTime = str
		self.endTime = str

	def Preprocess(self):
		#预处理
		self.per_trade_fun = None
		self.add_fun = None
		
		if self.goodsType == 1:
			self.per_trade_fun = self.CanBuyItem
			self.add_fun = self.AddItem
		elif self.goodsType == 2:
			self.per_trade_fun = self.CanBuyPet
			self.add_fun = self.AddPet
		elif self.goodsType == 3:
			self.per_trade_fun = self.CanBuyWing
			self.add_fun = self.AddWing
		elif self.goodsType == 4:
			self.per_trade_fun = self.CanBuyHero
			self.add_fun = self.AddHero
		
		if self.per_trade_fun is None or self.add_fun is None:
			print "GE_EXC, error in mall Preprocess not per_trade_fun, or add_fun (%s)" % self.tradeId
			return
		
		if self.CanGiving:
			#充值神石货物不能赠送
			if self.QRMB:
				print "GE_EXC mall errror QRMB can not giving (%s)" % self.tradeId
			#限购物品不能赠送
			if self.limitCnt or self.dayLimitCnt:
				print "GE_EXC mall errror limitCnt can not giving (%s)" % self.tradeId
				
		if not self.startTime:
			self.startTime = None
			if self.endTime:
				print "GE_EXC, error in mall end time error (%s)" % self.tradeId
			self.endTime = None
		else:
			if not self.endTime:
				print "GE_EXC, error in mall end time error (%s)" % self.tradeId
			self.startTime = datetime.datetime(*eval(self.startTime))
			self.endTime = datetime.datetime(*eval(self.endTime))
	
	def CanBuyNormal(self, role):
		if role.GetLevel() < self.needLevel:
			return False
		if self.needVIP:
			if role.GetVIP() < self.needVIP:
				return False
		#开服时间判断是否可以购买呢
		if self.needDay:
			worldDay = WorldData.GetWorldKaiFuDay()
			if worldDay < self.needDay[0] or worldDay > self.needDay[1]:
				return False
		if self.startTime:
			if self.startTime > cDateTime.Now() or cDateTime.Now() > self.endTime:
				#时间限购了
				return False
		return True
	
	def CanBuyLimit(self, role, cnt):
		#限购
		if self.limitCnt:
			limitDict = role.GetObj(EnumObj.Mall_Limit_Dict)
			if self.limitCnt < limitDict.get(self.tradeId, 0) + cnt:
				return False
		
		if self.dayLimitCnt:
			limitDayDict = role.GetObj(EnumObj.Mall_Day_Limit_Dict)
			if self.dayLimitCnt < limitDayDict.get(self.tradeId, 0) + cnt:
				return False
		return True
	
	def do_trade(self, role, cnt):
		with TraMallTrade:
			self._do_trade(role, cnt)
			AutoLog.LogBase(role.GetRoleID(), AutoLog.eveTrade, (self.goodsName, self.tradeId, cnt))
	
	def _do_trade(self, role, cnt):
		#交易主体
		if not self.CanBuyNormal(role):
			return
		if not self.CanBuyLimit(role, cnt):
			return
		
		#货物分类判断是否可以购买
		if not self.per_trade_fun(role, cnt):
			return
		
		#打折与扣钱
		NeedUnbindRMB = self.baseRMB * cnt
		if self.discountForever:
			NeedUnbindRMB = self.discountRMB * cnt
			if not NeedUnbindRMB:
				print "GE_EXC, error in mall trade not NeedUnbindRMB"
				return
			if self.QRMB:
				if role.GetUnbindRMB_Q() < NeedUnbindRMB:
					return
				role.DecUnbindRMB_Q(NeedUnbindRMB)
			else:
				if role.GetUnbindRMB() < NeedUnbindRMB:
					return
				role.DecUnbindRMB(NeedUnbindRMB)
		elif self.discountCardCoding:
			#折扣卡
			itemIds = GetDiscountItem(role, self.discountCardCoding, cnt)
			if itemIds:
				cnt = len(itemIds)
				NeedUnbindRMB = self.discountRMB * cnt
				if role.GetUnbindRMB() < NeedUnbindRMB:
					return
				for itemId in itemIds:
					role.DelProp(itemId)
				role.DecUnbindRMB(NeedUnbindRMB)
			else:
				if self.QRMB:
					if role.GetUnbindRMB_Q() < NeedUnbindRMB:
						return
					role.DecUnbindRMB_Q(NeedUnbindRMB)
				else:
					if role.GetUnbindRMB() < NeedUnbindRMB:
						return
					role.DecUnbindRMB(NeedUnbindRMB)
		elif self.VipLevelDiscount:
			#VIP打折
			if role.GetVIP() >= self.VipLevelDiscount:
				NeedUnbindRMB = self.discountRMB * cnt
	
			if self.QRMB:
				if role.GetUnbindRMB_Q() < NeedUnbindRMB:
					return
				role.DecUnbindRMB_Q(NeedUnbindRMB)
			else:
				if role.GetUnbindRMB() < NeedUnbindRMB:
					return
				role.DecUnbindRMB(NeedUnbindRMB)
		else:
			#不打折
			if self.QRMB:
				if role.GetUnbindRMB_Q() < NeedUnbindRMB:
					return
				role.DecUnbindRMB_Q(NeedUnbindRMB)
			else:
				if role.GetUnbindRMB() < NeedUnbindRMB:
					return
				role.DecUnbindRMB(NeedUnbindRMB)
		
		if NewYearDiscount.IsOpen:
			#新年乐翻天积分
			role.IncI32(EnumInt32.NewYearScore, NeedUnbindRMB)
			
		#增加限购数量
		if self.limitCnt:
			limitDict = role.GetObj(EnumObj.Mall_Limit_Dict)
			limitDict[self.tradeId] = limitDict.get(self.tradeId, 0) + cnt
			role.SendObj(Mall_S_LimitData, limitDict)
		
		if self.dayLimitCnt:
			limitDayDict = role.GetObj(EnumObj.Mall_Day_Limit_Dict)
			limitDayDict[self.tradeId] = limitDayDict.get(self.tradeId, 0) + cnt
			role.SendObj(Mall_S_DayLimitData, limitDayDict)
		
		role.SetDI1(EnumDayInt1.IsMallBuy, True)
		
		#双十一商城购物返利
		ElevenMallReward.MallAddConsume(role, NeedUnbindRMB)
		
		self.RewardRole(role, cnt)
		
	def RewardRole(self, role, cnt):
		#获得货物
		self.add_fun(role, cnt)
		
		role.Msg(2, 0, GlobalPrompt.MallBuyOk)
		#触发事件
		Event.TriggerEvent(Event.Eve_AfterMallBuy, role, (self.tradeId, cnt))
		
		#版本判断
		if Environment.EnvIsNA():
			#开服活动
			kaifuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
			kaifuActMgr.buy_rune(self.goodsId, cnt)
	
	
	def CanBuyItem(self, role, cnt):
		return True

	def CanBuyHero(self, role, cnt):
		return not role.GetTempObj(EnumTempObj.enHeroMgr).IsHeroFull()
	
	def CanBuyPet(self, role, cnt):
		return True
	
	def CanBuyWing(self, role, cnt):
		return True
	
	def AddItem(self, role, cnt):
		role.AddItem(self.goodsId, cnt)
		if self.goodsId not in EnumGameConfig.GEM_CONDIG_LIST:
			return
		from Game.Activity.WonderfulAct import WonderfulActMgr,EnumWonderType
		WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_Inc_Gem, [role, self.goodsId, cnt])
		if Environment.EnvIsNA():
			HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
			HalloweenNAMgr.BuyGem(self.goodsId, cnt)
				
	def AddPet(self, role, cnt):
		for _ in range(cnt):
			role.AddPet(self.goodsId)
	
	def AddHero(self, role, cnt):
		for _ in range(cnt):
			role.AddHero(self.goodsId)
	
	def AddWing(self, role, cnt):
		for _ in range(cnt):
			role.AddWing(self.goodsId)



def BuyInShoppingCart(role, msg):
	'''
	客户端使用购物车商城购物
	@param role:
	@param msg:
	'''
	#需要购物的商品{goods : cnt}列表, 使用的代金券物品ID
	goodsDict, couponsId = msg
	
	couponsItem = None
	couponCfg = None
	if couponsId:
		couponsItem = role.FindPackProp(couponsId)
		if not couponsItem:
			return
		if couponsItem.IsDeadTime():
			return 
		couponCfg = CouponsConfig_Dict.get(couponsItem.otype)
		if not couponCfg:
			return
	
	limitDict = role.GetObj(EnumObj.Mall_Limit_Dict)
	limitDayDict = role.GetObj(EnumObj.Mall_Day_Limit_Dict)
	
	totalNeedUnbindRMB = 0
	buylimitDict = {}
	daybuylimitDict = {}
	#heroCnt = 0
	goodCfgs = []
	for tradeId, cnt in goodsDict.iteritems():
		if cnt < 1:
			return
		cfg = MallConfig_Dict.get(tradeId)
		if not cfg:
			return
		if cfg.QRMB:
			#存在只能用充值神石购买的商品，不能使用购物车
			return
		goodCfgs.append((cfg, cnt))
		
		if not cfg.CanBuyNormal(role):
			return
		#限购
		if cfg.limitCnt:
			buylimitDict[cfg.tradeId] = nowtotalcnt = buylimitDict.get(cfg.tradeId, 0) + cnt
			if cfg.limitCnt < limitDict.get(cfg.tradeId, 0) + nowtotalcnt:
				return
			
		if cfg.dayLimitCnt:
			daybuylimitDict[cfg.tradeId] = nowtotalcnt = daybuylimitDict.get(cfg.tradeId, 0) + cnt
			if cfg.dayLimitCnt < limitDayDict.get(cfg.tradeId, 0) + nowtotalcnt:
				return
		
		#货物分类判断是否可以购买(单个货物)
		if not cfg.per_trade_fun(role, cnt):
			return
		
		#所有货物统计(只有英雄是特殊的)
		#可以暂时不做
		
		#打折与扣钱
		NeedUnbindRMB = cfg.baseRMB * cnt
		if cfg.discountForever:
			NeedUnbindRMB = cfg.discountRMB * cnt
			if not NeedUnbindRMB:
				print "GE_EXC, error in mall trade not NeedUnbindRMB"
				return
			totalNeedUnbindRMB += NeedUnbindRMB
		elif cfg.discountCardCoding:
			#折扣卡一律不打折
			totalNeedUnbindRMB += NeedUnbindRMB
		elif cfg.VipLevelDiscount:
			#VIP打折
			if role.GetVIP() >= cfg.VipLevelDiscount:
				NeedUnbindRMB = cfg.discountRMB * cnt
			totalNeedUnbindRMB += NeedUnbindRMB
		else:
			#不打折
			totalNeedUnbindRMB += NeedUnbindRMB
	
	if couponCfg:
		if couponCfg.needUnbindRMB > totalNeedUnbindRMB:
			#不足以使用代金券
			return
		totalNeedUnbindRMB -= couponCfg.num
	
	#if totalNeedUnbindRMB <= 0:
	#	print "GE_EXC,  error in BuyInShoppingCart totalNeedUnbindRMB < 0"
	#	return
	if totalNeedUnbindRMB > 0:
		if role.GetUnbindRMB() < totalNeedUnbindRMB:
			return
	else:
		if not couponsItem:
			print "GE_EXC error in BuyInShoppingCart totalNeedUnbindRMB < 0 and not couponsItem"
			return
	#增加限购数量
	if buylimitDict:
		for tradeId, cnt in buylimitDict.iteritems():
			limitDict[tradeId] = limitDict.get(tradeId, 0) + cnt
		role.SendObj(Mall_S_LimitData, limitDict)
	
	if daybuylimitDict:
		for tradeId, cnt in daybuylimitDict.iteritems():
			limitDayDict[tradeId] = limitDayDict.get(tradeId, 0) + cnt
		role.SendObj(Mall_S_DayLimitData, limitDayDict)
	
	
	with TraMallShoppingCart:
		#扣钱
		if totalNeedUnbindRMB > 0:
			role.DecUnbindRMB(totalNeedUnbindRMB)
		if couponsItem:
			role.DecPropCnt(couponsItem, 1)
		for cfg, cnt in goodCfgs:
			cfg.RewardRole(role, cnt)
		#记录今日已在商城购物
		role.SetDI1(EnumDayInt1.IsMallBuy, True)
		if NewYearDiscount.IsOpen and totalNeedUnbindRMB > 0:
			#新年乐翻天积分
			role.IncI32(EnumInt32.NewYearScore, totalNeedUnbindRMB)
		
		
def GivingGoods(role, param):
	'''
	客户端请求赠送商品
	@param role:
	@param param:
	'''
	backId, (tradeId, cnt, friendId) = param

	#是否本地角色
	from Game.Role import KuaFu
	if not KuaFu.IsLocalRoleByRoleID(friendId):
		return
	
	cfg = MallConfig_Dict.get(tradeId)
	if not cfg:
		return
	
	if not cfg.CanGiving or cfg.QRMB:
		return
	
	if not cfg.CanBuyNormal(role):
		return

	DelItemIDs = set()
	#打折与扣钱
	NeedUnbindRMB = cfg.baseRMB * cnt
	if cfg.discountForever:
		NeedUnbindRMB = cfg.discountRMB * cnt
		if not NeedUnbindRMB:
			print "GE_EXC, error in mall trade not NeedUnbindRMB"
			return
	elif cfg.discountCardCoding:
		itemIds = GetDiscountItem(role, cfg.discountCardCoding, cnt)
		if itemIds:
			cnt = len(itemIds)
			NeedUnbindRMB = cfg.discountRMB * cnt
			for itemId in itemIds:
				DelItemIDs.add(itemId)
	elif cfg.VipLevelDiscount:
		#VIP打折
		if role.GetVIP() >= cfg.VipLevelDiscount:
			NeedUnbindRMB = cfg.discountRMB * cnt
			
	if role.GetUnbindRMB() < NeedUnbindRMB:
		return
	
	#好友字典
	FriendDict = role.GetObj(EnumObj.Social_Friend)
	friendRole = cRoleMgr.FindRoleByRoleID(friendId)
	#在线判断等级
	if friendRole and friendRole.GetLevel() < cfg.needLevel:
		role.Msg(2, 0, GlobalPrompt.MALL_GIVING_MSG)
		return
	#为好友
	if friendId in FriendDict:
		if not friendRole:
			#不在线的判断好友字典中的好友等级是否满足条件
			if FriendDict[friendId][EnumSocial.RoleLevelKey] < cfg.needLevel:
				role.Msg(2, 0, GlobalPrompt.MALL_GIVING_MSG)
				return
	#为公会成员
	else:
		MallGivingUnionData = role.GetTempObj(EnumTempObj.MallGivingUnionData)
		if not MallGivingUnionData:
			return
		IsUnion = False
		for memberId, _, level, _ in MallGivingUnionData:
			if memberId == friendId:
				IsUnion = True
				if not friendRole:
					if level < cfg.needLevel:
						role.Msg(2, 0, GlobalPrompt.MALL_GIVING_MSG)
						return
		#不是公会成员
		if not IsUnion:
			return
	with TraMallGiving:
		role.DecUnbindRMB(NeedUnbindRMB)
		if DelItemIDs:
			for itemid in DelItemIDs:
				role.DelProp(itemid)
		if friendRole:
			friendRole.Msg(2, 0, GlobalPrompt.MALL_GIVING_GETED_MSG % (role.GetRoleName(), cfg.goodsId, cnt))
		Mail.SendMail(friendId, GlobalPrompt.MALL_GIVING_TITLE, GlobalPrompt.MALL_GIVING_SENDER, GlobalPrompt.MALL_GIVINT_DESC % (role.GetRoleName()), items = [(cfg.goodsId, cnt)])
		
		role.Msg(2, 0, GlobalPrompt.MALL_GIVING_SUC)
	role.CallBackFunction(backId, None)
	
def OpneGivingGoodsPanel(role, param):
	'''
	打开赠送界面
	@param role:
	@param param:
	'''
	OpenPanel(role)
	
def OpenPanel(role):
	'''
	返回所有公会成员 -- 10sCD
	@param role:
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		role.SendObj(MallGivingUnionMembers, role.GetTempObj(EnumTempObj.MallGivingUnionData))
		return
	
	if role.GetCD(EnumCD.UnionMallGviingCD):
		role.SendObj(MallGivingUnionMembers, role.GetTempObj(EnumTempObj.MallGivingUnionData))
		return
	
	role.SetCD(EnumCD.CardUMCD, 10)
	memberList = [(ID, member[1], member[2], member[5]) for (ID, member) in unionObj.members.iteritems()]
	role.SendObj(MallGivingUnionMembers, memberList)
	role.SetTempObj(EnumTempObj.MallGivingUnionData, memberList)

#代金券
class CouponsConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("Coupons.txt")
	def __init__(self):
		self.itemCoding = int
		self.needUnbindRMB = int
		self.num = int

def LoadCouponsConfig():
	#读配置表
	global CouponsConfig_Dict
	for cfg in CouponsConfig.ToClassType():
		CouponsConfig_Dict[cfg.itemCoding] = cfg
		#if cfg.needUnbindRMB <= cfg.num:
		#	print "GE_EXC LoadCouponsConfig error (%s)" % cfg.itemCoding

def RoleDayClear(role, param):
	#清理每日限购
	role.SetObj(EnumObj.Mall_Day_Limit_Dict, {})

def SyncRoleOtherData(role, param):
	role.SendObj(Mall_S_LimitData, role.GetObj(EnumObj.Mall_Limit_Dict))
	role.SendObj(Mall_S_DayLimitData, role.GetObj(EnumObj.Mall_Day_Limit_Dict))


if "_HasLoad" not in dir():
	if not Environment.IsCross:
		Mall.reg()
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		
	if Environment.HasLogic:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Mall_BuyInShoppingCart", "客户端使用购物车商城购物"), BuyInShoppingCart)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Mall_GivingGoods", "客户端请求赠送"), GivingGoods)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Mall_OpneGivingGoodsPanel", "客户端请求打开赠送界面"), OpneGivingGoodsPanel)
		
		LoadCouponsConfig()
		
	TraMallTrade = AutoLog.AutoTransaction("TraMallTrade", "神石商城购物")
	TraMallShoppingCart = AutoLog.AutoTransaction("TraMallShoppingCart", "神石商城购物车购物")
	TraMallGiving = AutoLog.AutoTransaction("TraMallGiving", "商城赠送")
	
	Mall_S_LimitData = AutoMessage.AllotMessage("Mall_S_LimitData", "同步永久限购数据")
	Mall_S_DayLimitData = AutoMessage.AllotMessage("Mall_S_DayLimitData", "同步每日限购数据")
	MallGivingUnionMembers = AutoMessage.AllotMessage("MallGivingUnionMembers", "商城赠送公会成员")

