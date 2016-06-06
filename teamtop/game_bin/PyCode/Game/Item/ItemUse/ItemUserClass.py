#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Item.ItemUse.ItemUserClass")
#===============================================================================
# 物品使用自动注册函数类
#===============================================================================
import random
import cRoleMgr
import cNetMessage
import cDateTime
from Util import Random
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from Game.Activity.Zuma import ZumaMgr
from Game.Item.ItemUse import ItemUseBase
from Game.Role.Data import EnumInt16, EnumTempObj, EnumInt32, EnumObj
from Game.Scene import SceneMgr
from Game.StationSoul import StationSoulConfig
from Game.StarGirl import StarGirlMgr
from Game.Activity.PassionAct import PassionTGPointExchangeMgr
from Game.Activity.PassionAct.PassionDefine import PassionNewYearPig
from Game.Union.UnionHongBao import UseItemSetUnionHongBao 


if "_HasLoad" not in dir():
	UseFireworks = AutoMessage.AllotMessage("UseFireworks", "放烟花")
	
##################################################################################
#普通单一类型
##################################################################################
class LiBao_Money(object):
	def __init__(self, coding, money):
		'''
		钱袋
		@param coding:物品编码
		@param money:1个物品对应的钱
		'''
		self.money = money
		ItemUseBase.RegItemUserEx(coding, self)
	
	def __call__(self, role, item, cnt):
		#先扣除物品 数量 cnt
		item.Use(cnt)
		total = self.money * cnt
		role.IncMoney(total)
		role.Msg(2, 0, GlobalPrompt.Item_Use_Tips_1 % total)
		
class LiBao_BindRMB(object):
	def __init__(self, coding, BindRMB):
		'''
		绑定，魔晶袋
		@param coding:物品编码
		@param BindRMB:1个物品对应的绑定货币
		'''
		self.BindRMB = BindRMB
		ItemUseBase.RegItemUserEx(coding, self)
	
	def __call__(self, role, item, cnt):
		#先扣除物品 数量 cnt
		item.Use(cnt)
		total = self.BindRMB * cnt
		role.IncBindRMB(total)
		role.Msg(2, 0, GlobalPrompt.Item_Use_Tips_2 % total)

class LiBao_UnbindRMB(object):
	def __init__(self, coding, UnbindRMB):
		'''
		系统神石
		@param coding:物品编码
		@param UnbindRMB:1个物品对应的绑定货币
		'''
		self.UnbindRMB = UnbindRMB
		ItemUseBase.RegItemUserEx(coding, self)
	
	def __call__(self, role, item, cnt):
		#先扣除物品 数量 cnt
		item.Use(cnt)
		total = self.UnbindRMB * cnt
		role.IncUnbindRMB_S(total)
		role.Msg(2, 0, GlobalPrompt.Item_Use_Tips_3 % total)
		
class LiBao_TiLi(object):
	def __init__(self, coding, tili):
		'''
		体力
		@param coding:物品编码
		@param BindRMB:1个物品对应的绑定货币
		'''
		self.tili = tili
		ItemUseBase.RegItemUserEx(coding, self)
	
	def __call__(self, role, item, cnt):
		#先扣除物品 数量 cnt
		item.Use(cnt)
		total = self.BindRMB * cnt
		role.IncTiLi(total)
		role.Msg(2, 0, GlobalPrompt.Item_Use_Tips_4 % total)

class LiBao_TarotHp(object):
	def __init__(self, coding, tarothp):
		'''
		命力
		@param coding:物品编码
		@param BindRMB:1个物品对应的绑定货币
		'''
		self.tarothp = tarothp
		ItemUseBase.RegItemUserEx(coding, self)
		
	def __call__(self, role, item, cnt):
		#先扣除物品 数量 cnt
		item.Use(cnt)
		total = self.tarothp * cnt
		role.IncTarotHP(total)
		role.Msg(2, 0, GlobalPrompt.Item_Use_Tips_5 % total)

class LiBao_MoonCake(object):
	def __init__(self, coding, tili):
		'''
		月饼
		@param coding:物品编码
		@param tili:使用增加的体力值
		'''
		self.tili = tili
		ItemUseBase.RegItemUserEx(coding, self)
	
	def __call__(self, role, item, cnt):
		#先扣除物品 数量 cnt
		item.Use(cnt)
		total = self.tili * cnt
		role.IncTiLi(total)
		role.Msg(2, 0, GlobalPrompt.Item_Use_Tips_4)
		
##################################################################################
#物品
##################################################################################
class LiBao_Items(object):
	def __init__(self, coding, items, items_60):
		'''
		物品
		@param coding:物品编码
		@param BindRMB:1个物品对应的绑定货币
		'''
		self.items = items
		self.items_60 = items_60#60级以后
		if not items or not items_60:
			print "GE_EXC, error in LiBao_Items (%s)" % coding
			return
			
		#self.needSize = len(items)
		
		ItemUseBase.RegItemUserEx(coding, self)
	
	def __call__(self, role, item, cnt):
		#先扣除物品 数量 cnt
		if role.PackageIsFull():
			role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
			return
		tips = GlobalPrompt.Item_Use_Tips
		
		item.Use(cnt)
		if role.GetLevel() < 60:
			for itemCoding, itemCnt in self.items:
				role.AddItem(itemCoding, itemCnt * cnt)
				tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt * cnt)
		else:
			for itemCoding, itemCnt in self.items_60:
				role.AddItem(itemCoding, itemCnt * cnt)
				tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt * cnt)
		
		role.Msg(2, 0, tips)
##################################################################################
#命魂
##################################################################################
class LiBao_Tarot(object):
	def __init__(self, coding, tarots, tarots_60):
		'''
		命魂
		@param coding:物品编码
		@param BindRMB:1个物品对应的绑定货币
		'''
		self.tarots = tarots
		self.tarots_60 = tarots_60#60级以后
		
		ItemUseBase.RegItemUserEx(coding, self)
	
	def __call__(self, role, item, cnt):
		#先扣除物品 数量 cnt
		emptySize = role.GetTarotEmptySize()
		if not emptySize:
			role.Msg(2, 0, GlobalPrompt.TarotIsFull_Tips)
			return
		if role.GetLevel() < 60:
			if emptySize < len(self.tarots) * cnt:
				cnt = emptySize / len(self.tarots)
		else:
			if emptySize < len(self.tarots_60) * cnt:
				cnt = emptySize / len(self.tarots_60)
		if not cnt:
			role.Msg(2, 0, GlobalPrompt.TarotIsFull_Tips)
			return
		item.Use(cnt)
		tips = GlobalPrompt.Item_Use_Tips
		
		if role.GetLevel() < 60:
			for cardType, cardCnt in self.tarots:
				role.AddTarotCard(cardType, cardCnt * cnt)
				tips += GlobalPrompt.Tarot_Tips % (cardType, cardCnt * cnt)
		else:
			for cardType, cardCnt in self.tarots_60:
				role.AddTarotCard(cardType, cardCnt * cnt)
				tips += GlobalPrompt.Tarot_Tips % (cardType, cardCnt * cnt)
		
		role.Msg(2, 0, tips)
##################################################################################
#普通礼包(注意被继承过,修改的时候需要全局搜索一下看看会不会导致其他问题)
##################################################################################
class LiBao_Normal(object):
	def __init__(self, coding, libao_cfg):
		'''
		普通礼包
		@param coding:物品编码
		@param BindRMB:1个物品对应的绑定货币
		'''
		self.libao_cfg = libao_cfg
		
		ItemUseBase.RegItemUserEx(coding, self)
	
	def __call__(self, role, item, cnt):
		#先扣除物品 数量 cnt
		if self.libao_cfg.items:
			if role.PackageEmptySize() < len(self.libao_cfg.items) * cnt:
				role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
				return False
		size = role.GetTarotEmptySize()
		if self.libao_cfg.tarots:
			if role.GetLevel() < 60:
				if not size:
					role.Msg(2, 0, GlobalPrompt.TarotIsFull_Tips)
					return False
				if size < len( self.libao_cfg.tarots) * cnt:
					cnt = size / len( self.libao_cfg.tarots)
		if self.libao_cfg.tarots_60:
			if role.GetLevel() >= 60:
				if not size:
					role.Msg(2, 0, GlobalPrompt.TarotIsFull_Tips)
					return False
				if size < len( self.libao_cfg.tarots_60) * cnt:
					cnt = size / len( self.libao_cfg.tarots_60)
		if not cnt:
			role.Msg(2, 0, GlobalPrompt.TarotIsFull_Tips)
			return
		item.Use(cnt)
		
		tips = GlobalPrompt.Item_Use_Tips
		
		if self.libao_cfg.money:
			total = self.libao_cfg.money * cnt
			role.IncMoney(total)
			tips += GlobalPrompt.Money_Tips % total
			
		if self.libao_cfg.tili:
			total = self.libao_cfg.tili * cnt
			role.IncTiLi(total)
			tips += GlobalPrompt.TiLi_Tips % total
			
		if self.libao_cfg.bindrmb:
			total = self.libao_cfg.bindrmb * cnt
			role.IncBindRMB(total)
			tips += GlobalPrompt.BindRMB_Tips % total
			
		if self.libao_cfg.unbindrmb:
			total = self.libao_cfg.unbindrmb * cnt
			role.IncUnbindRMB_S(total)
			tips += GlobalPrompt.UnBindRMB_Tips % total
			
		if self.libao_cfg.tarothp:
			total = self.libao_cfg.tarothp * cnt
			role.IncTarotHP(total)
			tips += GlobalPrompt.TarotHp_Tips % total
			
		if role.GetLevel() < 60:
			if self.libao_cfg.items:
				for itemCoding, itemCnt in self.libao_cfg.items:
					role.AddItem(itemCoding, itemCnt * cnt)
					tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt * cnt)
			if self.libao_cfg.tarots:
				for cardType, cardCnt in self.libao_cfg.tarots:
					role.AddTarotCard(cardType, cardCnt * cnt)
					tips += GlobalPrompt.Tarot_Tips % (cardType, cardCnt * cnt)
		else:
			if self.libao_cfg.items_60:
				for itemCoding, itemCnt in self.libao_cfg.items_60:
					role.AddItem(itemCoding, itemCnt * cnt)
					tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt * cnt)
					
			if self.libao_cfg.tarots_60:
				for cardType, cardCnt in self.libao_cfg.tarots_60:
					role.AddTarotCard(cardType, cardCnt * cnt)
					tips += GlobalPrompt.Tarot_Tips % (cardType, cardCnt * cnt)
		
		role.Msg(2, 0, tips)
		return True

##################################################################################
#随机物品
##################################################################################
class LiBao_Random_Item(object):
	def __init__(self, coding, libao_cfg):
		'''
		随机物品礼包
		@param coding:物品编码
		@param libao_cfg:
		'''
		self.coding = coding
		self.libao_cfg = libao_cfg
		self.randoms = Random.RandomRate()
		self.randoms_60 = Random.RandomRate()

		if self.libao_cfg.rateitems:
			for rate, itemCoding, cnt in self.libao_cfg.rateitems:
				self.randoms.AddRandomItem(rate, (itemCoding, cnt))
		
		if self.libao_cfg.rateitems_60:
			for rate, itemCoding, cnt in self.libao_cfg.rateitems_60:
				self.randoms_60.AddRandomItem(rate, (itemCoding, cnt))
		ItemUseBase.RegItemUserEx(coding, self)
		
	def __call__(self, role, item, cnt):
		if role.PackageIsFull():
			role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
			return
		#先扣除物品 数量 cnt
		item.Use(cnt)
		tips = GlobalPrompt.Item_Use_Tips
		rewardDict = {}
		if role.GetLevel() < 60:
			for _ in xrange(cnt):
				itemCoding, itemCnt = self.randoms.RandomOne()
				rewardDict[itemCoding] = rewardDict.get(itemCoding, 0) + itemCnt
		else:
			for _ in xrange(cnt):
				itemCoding, itemCnt = self.randoms_60.RandomOne()
				rewardDict[itemCoding] = rewardDict.get(itemCoding, 0) + itemCnt
		#是变身卡礼包,特殊处理
		if self.coding in EnumGameConfig.HALLOWEEN_CARD_LIOBAO:
			from Game.Activity.HalloweenAct import HalloweenMgr
			
			HalloweenData = role.GetObj(EnumObj.HalloweenData)
			collectData = HalloweenData.setdefault(1, {})

			for itemCoding, itemCnt in rewardDict.iteritems():
				role.AddItem(itemCoding, itemCnt)
				collectData[itemCoding] = collectData.get(itemCoding, 0) + itemCnt
				tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt)
			HalloweenMgr.CheckCardLimit(role)
		else:
			for itemCoding, itemCnt in rewardDict.iteritems():
				role.AddItem(itemCoding, itemCnt)
				tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt)
		role.Msg(2, 0, tips)
		
##################################################################################
#随机命魂
##################################################################################
class LiBao_Random_Tarot(object):
	def __init__(self, coding, libao_cfg):
		'''
		随机命魂礼包
		@param coding:物品编码
		@param libao_cfg:
		'''
		self.coding = coding
		self.libao_cfg = libao_cfg
		self.randoms = Random.RandomRate()
		self.randoms_60 = Random.RandomRate()

		if self.libao_cfg.ratetarots:
			for rate, cardType, cnt in self.libao_cfg.ratetarots:
				self.randoms.AddRandomItem(rate, (cardType, cnt))
				
		if self.libao_cfg.ratetarots_60:
			for rate, cardType, cnt in self.libao_cfg.ratetarots_60:
				self.randoms_60.AddRandomItem(rate, (cardType, cnt))
		ItemUseBase.RegItemUserEx(self.coding, self)
		
	def __call__(self, role, item, cnt):
		
		emptySize = role.GetTarotEmptySize()
		if not emptySize:
			role.Msg(2, 0, GlobalPrompt.TarotIsFull_Tips)
			return
		
		if emptySize < cnt:
			cnt = emptySize
			
		#先扣除物品 数量 cnt
		item.Use(cnt)
		
		tips = GlobalPrompt.Item_Use_Tips
		if role.GetLevel() < 60:
			for _ in xrange(cnt):
				cardType, cardCnt = self.randoms.RandomOne()
				role.AddTarotCard(cardType, cardCnt)
				tips += GlobalPrompt.Tarot_Tips % (cardType, cardCnt)
		else:
			for _ in xrange(cnt):
				cardType, cardCnt = self.randoms_60.RandomOne()
				role.AddTarotCard(cardType, cardCnt)
				tips += GlobalPrompt.Tarot_Tips % (cardType, cardCnt)
		role.Msg(2, 0, tips)
##################################################################################
#随机一个奖励
##################################################################################
class LiBao_Random(object):
	def __init__(self, coding, libao_cfg):
		'''
		随机礼包
		@param coding:物品编码
		@param libao_cfg:
		'''
		self.coding = coding
		self.libao_cfg = libao_cfg
		self.randoms = Random.RandomRate()
		self.randoms_60 = Random.RandomRate()
		
		if self.libao_cfg.ratemoney:
			self.randoms.AddRandomItem(self.libao_cfg.ratemoney[0], (self.IncMoney, self.libao_cfg.ratemoney[1]))
			self.randoms_60.AddRandomItem(self.libao_cfg.ratemoney[0], (self.IncMoney, self.libao_cfg.ratemoney[1]))
		
		if self.libao_cfg.ratebindrmb:
			self.randoms.AddRandomItem(self.libao_cfg.ratebindrmb[0], (self.IncBindRMB, self.libao_cfg.ratebindrmb[1]))
			self.randoms_60.AddRandomItem(self.libao_cfg.ratebindrmb[0], (self.IncBindRMB, self.libao_cfg.ratebindrmb[1]))
		
		if self.libao_cfg.rateunbindrmb:
			self.randoms.AddRandomItem(self.libao_cfg.rateunbindrmb[0], (self.IncUnbindRMB, self.libao_cfg.rateunbindrmb[1]))
			self.randoms_60.AddRandomItem(self.libao_cfg.rateunbindrmb[0], (self.IncUnbindRMB, self.libao_cfg.rateunbindrmb[1]))
		
		if self.libao_cfg.ratetili:
			self.randoms.AddRandomItem(self.libao_cfg.ratetili[0], (self.IncTiLi, self.libao_cfg.ratetili[1]))
			self.randoms_60.AddRandomItem(self.libao_cfg.ratetili[0], (self.IncTiLi, self.libao_cfg.ratetili[1]))
		
		if self.libao_cfg.ratetarothp:
			self.randoms.AddRandomItem(self.libao_cfg.ratetarothp[0], (self.IncTarotHP, self.libao_cfg.ratetarothp[1]))
			self.randoms_60.AddRandomItem(self.libao_cfg.ratetarothp[0], (self.IncTarotHP, self.libao_cfg.ratetarothp[1]))
		
		if self.libao_cfg.rateitems:
			for rate, itemCoding, cnt in self.libao_cfg.rateitems:
				self.randoms.AddRandomItem(rate, (self.AddItem, (itemCoding, cnt)))
		
		if self.libao_cfg.ratetarots:
			for rate, cardType, cnt in self.libao_cfg.ratetarots:
				self.randoms.AddRandomItem(rate, (self.AddTarot, (cardType, cnt)))
		
		if self.libao_cfg.rateitems_60:
			for rate, itemCoding, cnt in self.libao_cfg.rateitems_60:
				self.randoms_60.AddRandomItem(rate, (self.AddItem, (itemCoding, cnt)))
		
		if self.libao_cfg.ratetarots_60:
			for rate, cardType, cnt in self.libao_cfg.ratetarots_60:
				self.randoms_60.AddRandomItem(rate, (self.AddTarot, (cardType, cnt)))
		ItemUseBase.RegItemUserEx(self.coding, self)


	def IncMoney(self, role, param): 
		self.totalMoney += param
	
	def IncBindRMB(self, role, param): 
		self.totalBindRMB += param
		
	def IncUnbindRMB(self, role, param): 
		self.totalUnbindRMB += param
		
	def IncTiLi(self, role, param): 
		self.totalTiLi += param
	
	def IncTarotHP(self, role, param): 
		self.totalTarotHp += param
	
	def AddItem(self, role, param):
		itemCoding, itemCnt = param
		self.totalItems[itemCoding] = self.totalItems.get(itemCoding, 0) + itemCnt
	
	def AddTarot(self, role, param):
		cardType, cardCnt = param
		self.totalTarots[cardType] = self.totalTarots.get(cardType, 0) + cardCnt
	
	
	def Clear(self):
		self.totalMoney = 0
		self.totalBindRMB = 0
		self.totalUnbindRMB = 0
		self.totalTiLi = 0
		self.totalTarotHp = 0
		self.totalItems = {}
		self.totalTarots = {}
	
	def doReward(self, role):
		tips = GlobalPrompt.Item_Use_Tips
		if self.totalMoney:
			role.IncMoney(self.totalMoney)
			tips += GlobalPrompt.Money_Tips % self.totalMoney
		if self.totalBindRMB:
			role.IncBindRMB(self.totalBindRMB)
			tips += GlobalPrompt.BindRMB_Tips % self.totalBindRMB
		if self.totalUnbindRMB:
			role.IncUnbindRMB_S(self.totalUnbindRMB)
			tips += GlobalPrompt.UnBindRMB_Tips % self.totalUnbindRMB
		if self.totalTiLi:
			role.IncTiLi(self.totalTiLi)
			tips += GlobalPrompt.TiLi_Tips % self.totalTiLi
		if self.totalTarotHp:
			role.IncTarotHP(self.totalTarotHp)
			tips += GlobalPrompt.TarotHp_Tips % self.totalTarotHp
		if self.totalItems:
			for itemCoding, itemCnt in self.totalItems.iteritems():
				role.AddItem(itemCoding, itemCnt)
				tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt)
		if self.totalTarots:
			for cardType, cardCnt in self.totalTarots.iteritems():
				role.AddTarotCard(cardType, cardCnt)
				tips += GlobalPrompt.Tarot_Tips % (cardType, cardCnt)
		role.Msg(2, 0, tips)
		
		self.Clear()
		
	def __call__(self, role, item, cnt):
		#先扣除物品 数量 cnt
		item.Use(cnt)
		
		self.Clear()
		
		if role.GetLevel() < 60:
			for _ in xrange(cnt):
				fun, param = self.randoms.RandomOne()
				fun(role, param)
		else:
			for _ in xrange(cnt):
				fun, param = self.randoms_60.RandomOne()
				fun(role, param)
		
		self.doReward(role)
				
##################################################################################
#通用礼包，拥有所有礼包的功能，可以随机出一个奖励，可以必出一个奖励，也可以必出+随机组合
##################################################################################
class LiBao_Super(object):
	def __init__(self, coding, libao_cfg):
		'''
		
		@param coding:物品编码
		@param BindRMB:1个物品对应的绑定货币
		'''
		self.coding = coding
		self.libao_cfg = libao_cfg
		self.randoms = Random.RandomRate()
		self.randoms_60 = Random.RandomRate()
		
		if self.libao_cfg.ratemoney:
			self.randoms.AddRandomItem(self.libao_cfg.ratemoney[0], (self.IncMoney, self.libao_cfg.ratemoney[1]))
			self.randoms_60.AddRandomItem(self.libao_cfg.ratemoney[0], (self.IncMoney, self.libao_cfg.ratemoney[1]))
		
		if self.libao_cfg.ratebindrmb:
			self.randoms.AddRandomItem(self.libao_cfg.ratebindrmb[0], (self.IncBindRMB, self.libao_cfg.ratebindrmb[1]))
			self.randoms_60.AddRandomItem(self.libao_cfg.ratebindrmb[0], (self.IncBindRMB, self.libao_cfg.ratebindrmb[1]))
		
		if self.libao_cfg.rateunbindrmb:
			self.randoms.AddRandomItem(self.libao_cfg.rateunbindrmb[0], (self.IncUnbindRMB, self.libao_cfg.rateunbindrmb[1]))
			self.randoms_60.AddRandomItem(self.libao_cfg.rateunbindrmb[0], (self.IncUnbindRMB, self.libao_cfg.rateunbindrmb[1]))
		
		if self.libao_cfg.ratetili:
			self.randoms.AddRandomItem(self.libao_cfg.ratetili[0], (self.IncTiLi, self.libao_cfg.ratetili[1]))
			self.randoms_60.AddRandomItem(self.libao_cfg.ratetili[0], (self.IncTiLi, self.libao_cfg.ratetili[1]))
		
		if self.libao_cfg.ratetarothp:
			self.randoms.AddRandomItem(self.libao_cfg.ratetarothp[0], (self.IncTarotHP, self.libao_cfg.ratetarothp[1]))
			self.randoms_60.AddRandomItem(self.libao_cfg.ratetarothp[0], (self.IncTarotHP, self.libao_cfg.ratetarothp[1]))
		
		if self.libao_cfg.rateitems:
			for rate, itemCoding, cnt in self.libao_cfg.rateitems:
				self.randoms.AddRandomItem(rate, (self.AddItem, (itemCoding, cnt)))
		
		if self.libao_cfg.ratetarots:
			for rate, cardType, cnt in self.libao_cfg.ratetarots:
				self.randoms.AddRandomItem(rate, (self.AddTarot, (cardType, cnt)))
		
		if self.libao_cfg.rateitems_60:
			for rate, itemCoding, cnt in self.libao_cfg.rateitems_60:
				self.randoms_60.AddRandomItem(rate, (self.AddItem, (itemCoding, cnt)))
		
		if self.libao_cfg.ratetarots_60:
			for rate, cardType, cnt in self.libao_cfg.ratetarots_60:
				self.randoms_60.AddRandomItem(rate, (self.AddTarot, (cardType, cnt)))
		
		ItemUseBase.RegItemUserEx(self.coding, self)
	
	def Clear(self):
		self.totalMoney = 0
		self.totalBindRMB = 0
		self.totalUnbindRMB = 0
		self.totalTiLi = 0
		self.totalTarotHp = 0
		self.totalItems = {}
		self.totalTarots = {}
	
	def doReward(self, role):
		tips = GlobalPrompt.Item_Use_Tips
		if self.totalMoney:
			role.IncMoney(self.totalMoney)
			tips += GlobalPrompt.Money_Tips % self.totalMoney
		if self.totalBindRMB:
			role.IncBindRMB(self.totalBindRMB)
			tips += GlobalPrompt.BindRMB_Tips % self.totalBindRMB
		if self.totalUnbindRMB:
			role.IncUnbindRMB_S(self.totalUnbindRMB)
			tips += GlobalPrompt.UnBindRMB_Tips % self.totalUnbindRMB
		if self.totalTiLi:
			role.IncTiLi(self.totalTiLi)
			tips += GlobalPrompt.TiLi_Tips % self.totalTiLi
		if self.totalTarotHp:
			role.IncTarotHP(self.totalTarotHp)
			tips += GlobalPrompt.TarotHp_Tips % self.totalTarotHp
		if self.totalItems:
			for itemCoding, itemCnt in self.totalItems.iteritems():
				role.AddItem(itemCoding, itemCnt)
				tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt)
		if self.totalTarots:
			for cardType, cardCnt in self.totalTarots.iteritems():
				role.AddTarotCard(cardType, cardCnt)
				tips += GlobalPrompt.Tarot_Tips % (cardType, cardCnt)
		
		role.Msg(2, 0, tips)
		self.Clear()
		
	def __call__(self, role, item, cnt):
		#先扣除物品 数量 cnt
		if self.libao_cfg.items:
			if role.PackageIsFull():
				role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
				return
		
		if self.libao_cfg.tarots:
			if role.TarotPackageIsFull():
				role.Msg(2, 0, GlobalPrompt.TarotIsFull_Tips)
				return
		
		item.Use(cnt)
		#尝试清理数据
		self.Clear()
		
		if self.libao_cfg.money:
			total = self.libao_cfg.money * cnt
			self.totalMoney += total
			
		if self.libao_cfg.tili:
			total = self.libao_cfg.tili * cnt
			self.totalTiLi += total
			
		if self.libao_cfg.bindrmb:
			total = self.libao_cfg.bindrmb * cnt
			self.totalBindRMB += total
			
		if self.libao_cfg.unbindrmb:
			total = self.libao_cfg.unbindrmb * cnt
			self.totalUnbindRMB += total
			
		if self.libao_cfg.tarothp:
			total = self.libao_cfg.tarothp * cnt
			self.totalTarotHp += total
			
		if role.GetLevel() < 60:
			if self.libao_cfg.items:
				for itemCoding, itemCnt in self.libao_cfg.items:
					self.totalItems[itemCoding] = self.totalItems.get(itemCoding, 0) + itemCnt * cnt
			if self.libao_cfg.tarots:
				for cardType, cardCnt in self.libao_cfg.tarots:
					self.totalTarots[cardType] = self.totalTarots.get(cardType, 0) + cardCnt * cnt
			for _ in xrange(cnt):
				fun, param = self.randoms.RandomOne()
				fun(role, param)
			
		else:
			if self.libao_cfg.items_60:
				for itemCoding, itemCnt in self.libao_cfg.items_60:
					self.totalItems[itemCoding] = self.totalItems.get(itemCoding, 0) + itemCnt * cnt
			if self.libao_cfg.tarots_60:
				for cardType, cardCnt in self.libao_cfg.tarots_60:
					self.totalTarots[cardType] = self.totalTarots.get(cardType, 0) + cardCnt * cnt
			for _ in xrange(cnt):
				fun, param = self.randoms_60.RandomOne()
				fun(role, param)
		
		self.doReward(role)

	def IncMoney(self, role, param): 
		self.totalMoney += param
	
	def IncBindRMB(self, role, param): 
		self.totalBindRMB += param
		
	def IncUnbindRMB(self, role, param): 
		self.totalUnbindRMB += param
		
	def IncTiLi(self, role, param): 
		self.totalTiLi += param
	
	def IncTarotHP(self, role, param): 
		self.totalTarotHp += param
	
	def AddItem(self, role, param):
		itemCoding, itemCnt = param
		self.totalItems[itemCoding] = self.totalItems.get(itemCoding, 0) + itemCnt
	
	def AddTarot(self, role, param):
		cardType, cardCnt = param
		self.totalTarots[cardType] = self.totalTarots.get(cardType, 0) + cardCnt





##################################################################################
#特殊，坐骑食物
##################################################################################
class MountFood(object):
	def __init__(self, coding, foodId):
		'''
		坐骑食物
		@param coding:
		@param reputation:
		'''
		self.foodId = foodId
		ItemUseBase.RegItemUserEx(coding, self)
		
	def __call__(self, role, item, cnt):
		from Game.Mount import MountConfig, MountMgr
		from Game.Property import PropertyEnum
		config = MountConfig._MOUNT_FOOD.get(self.foodId)
		if not config:
			return
		#获取玩家坐骑进阶等级
		Evolve = role.GetI16(EnumInt16.MountEvolveID)
		if config.EatConditions > Evolve:
			role.Msg(2, 0, GlobalPrompt.MOUNT_LIMIT_FOOD)
			return
		#获取玩家已食用列表
		mountMgr = role.GetTempObj(EnumTempObj.MountMgr)
		if not mountMgr:
			return
		eated_food = mountMgr.eated_food
		if self.foodId in eated_food:
			role.Msg(2, 0, GlobalPrompt.MOUNT_EATED_FOOD)
			return	
		#先扣物品
		item.Use(cnt)
		mountMgr.eated_food.append(self.foodId)
		mountMgr.ResetAttribute()
		role.ResetGlobalMountProperty()
		MountMgr.SendMsgClient(role)
		cfg = MountConfig._MOUNT_FOOD.get(self.foodId)
		if not cfg:
			return
		hp,attack_p,attack_m = 0, 0, 0
		for pk, pv in cfg.property_dict.iteritems():
			if pk == PropertyEnum.maxhp:
				hp = pv
			elif pk == PropertyEnum.attack_p:
				attack_p = pv
			elif pk == PropertyEnum.attack_m:
				attack_m = pv
		role.Msg(2, 0, GlobalPrompt.MOUNT_FOOD_SUC % (attack_p, attack_m, hp))

##################################################################################
#翅膀
##################################################################################
class WingLiBao(object):
	def __init__(self, coding, wingId):
		'''
		需要钥匙的翅膀礼包
		@param coding:
		@param wingId:
		'''
		self.coding = coding
		self.wingId = wingId
		ItemUseBase.RegItemUserEx(coding, self)
		
	def __call__(self, role, item, cnt):
		from Game.Fashion import FashionOperate, FashionForing
		#扣礼包
		item.Use(1)
		#获得翅膀
		#role.AddWing(self.wingId)
		
		if role.PackageIsFull():#背包满了不让开
			role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
			return
		role.AddItem(self.wingId, 1)
		#激活时装
		FashionForing.RequestActiveFashion(role, self.wingId)
		#提示
		role.Msg(2, 0, GlobalPrompt.WING_LIBAO_PROMPT)


##################################################################################
#英雄
##################################################################################
class HeroLiBao(object):
	def __init__(self, coding, Heros):
		'''
		英雄礼包
		@param coding:
		@param Heros:
		'''
		self.coding = coding
		self.Heros = Heros
		ItemUseBase.RegItemUserEx(coding, self)
		
	def __call__(self, role, item, cnt):
		if role.GetTempObj(EnumTempObj.enHeroMgr).HeroEmptyCnt() < len(self.Heros):
			role.Msg(2, 0, GlobalPrompt.HeroIsFull_Tips)
			return
		#扣礼包
		item.Use(1)
		#获得英雄
		tips = GlobalPrompt.Item_Use_Tips
		for heroNumber in self.Heros:
			role.AddHero(heroNumber)
			tips += GlobalPrompt.Hero_Tips % (heroNumber, 1)
		#提示
		role.Msg(2, 0, tips)


##################################################################################
#龙晶礼包
##################################################################################
class LongJingLiBao(object):
	def __init__(self, coding, items):
		'''
		龙晶礼包
		@param coding:
		'''
		self.coding = coding
		self.items = items
		ItemUseBase.RegItemUserEx(coding, self)

	def __call__(self, role, item, cnt):
		#扣礼包
		item.Use(cnt)
		tips = GlobalPrompt.Item_Use_Tips
		roleLevel = role.GetLevel()
		if roleLevel <= 39:
			itemCoding, itemCnt = self.items[0]
			role.AddItem(itemCoding, itemCnt * cnt)
			tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt * cnt)
		elif roleLevel <= 59:
			itemCoding, itemCnt = self.items[1]
			role.AddItem(itemCoding, itemCnt * cnt)
			tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt * cnt)
		elif roleLevel <= 79:
			itemCoding, itemCnt = self.items[2]
			role.AddItem(itemCoding, itemCnt * cnt)
			tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt * cnt)
		elif roleLevel <= 99:
			itemCoding, itemCnt = self.items[3]
			role.AddItem(itemCoding, itemCnt * cnt)
			tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt * cnt)
		elif roleLevel <= 119:
			itemCoding, itemCnt = self.items[4]
			role.AddItem(itemCoding, itemCnt * cnt)
			tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt * cnt)
		else:
			print "GE_EXC, error in LongJingLiBao level overflow"
			itemCoding, itemCnt = self.items[4]
			role.AddItem(itemCoding, itemCnt * cnt)
			tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt * cnt)
		
		role.Msg(2, 0, tips)



class AiRenLiBao(object):
	def __init__(self, coding, item1, rateItems, unbindRMB, moneys):
		'''
		矮人礼包
		@param coding:
		'''
		self.coding = coding
		self.item1Coding = item1[0]
		self.item1Cnt = item1[1]
		
		#随机物品
		self.rateItems = Random.RandomRate()
		for rate, itemCoding, cnt in rateItems:
			self.rateItems.AddRandomItem(rate, (itemCoding, cnt))
		
		#等概率随机神石列表
		self.rateUnbindRMB = range(unbindRMB[0], unbindRMB[1] + 1)
		
		#随机金币
		self.rateMoney = Random.RandomRate()
		for rate, money in moneys:
			self.rateMoney.AddRandomItem(rate, money)
		
		ItemUseBase.RegItemUserEx(coding, self)

	def __call__(self, role, item, cnt):
		#扣礼包
		item.Use(cnt)
		
		role.AddItem(self.item1Coding, self.item1Cnt * cnt)
		
		totalMoney = 0
		totalUnbindRMB = 0
		itemDict = {}
		for _ in xrange(cnt):
			totalMoney += self.rateMoney.RandomOne()
			totalUnbindRMB += random.choice(self.rateUnbindRMB)
			itemCoding, itemCnt = self.rateItems.RandomOne()
			itemDict[itemCoding] = itemDict.get(itemCoding, 0) + itemCnt

		role.IncMoney(totalMoney)
		role.IncUnbindRMB_S(totalUnbindRMB)
		
		tips = GlobalPrompt.Item_Use_Tips
		tips += GlobalPrompt.Money_Tips % totalMoney
		tips += GlobalPrompt.UnBindRMB_Tips % totalUnbindRMB
		tips += GlobalPrompt.Item_Tips % (self.item1Coding, self.item1Cnt * cnt)
		
		for itemCoding, itemCnt in itemDict.iteritems():
			role.AddItem(itemCoding, itemCnt)
			tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt)
		
		role.Msg(2, 0, tips)



##################################################################################
#世界杯淘汰赛礼包
##################################################################################
class WorldCupLevelLiBao(object):
	def __init__(self, coding, itemList):
		'''
		世界杯淘汰赛礼包
		@param coding:
		'''
		self.coding = coding
		self.itemList = itemList
		self.randomItems = {}
		for i, items in enumerate(itemList):
			r = Random.RandomRate()
			self.randomItems[i] = r
			for itemCoding, itemCnt, rate in items:
				r.AddRandomItem(rate, (itemCoding, itemCnt))

		ItemUseBase.RegItemUserEx(coding, self)

	def __call__(self, role, item, cnt):
		#扣礼包
		item.Use(cnt)
		tips = GlobalPrompt.Item_Use_Tips
		roleLevel = role.GetLevel()
		itemDict = {}
		IG = itemDict.get

		levelindex = 0
		if roleLevel <= 39:
			levelindex = 0
		elif roleLevel <= 59:
			levelindex = 1
		elif roleLevel <= 79:
			levelindex = 2
		elif roleLevel <= 99:
			levelindex = 3
		elif roleLevel <= 119:
			levelindex = 4
		elif roleLevel <= 139:
			levelindex = 5
		elif roleLevel <= 159:
			levelindex = 6
		elif roleLevel <= 179:
			levelindex = 7
		else:
			levelindex = 7
			print "GE_EXC, error in WorldCupLevelLiBao level overflow (%s) (%s)" % (self.coding, roleLevel)
		
		SRR = self.randomItems.get(levelindex)
		if not SRR:
			print "GE_EXC, error in WorldCupLevelLiBao level overflow (%s) (%s)" % (self.coding, roleLevel)
			return
		
		SRR = SRR.RandomOne
		
		for _ in xrange(cnt):
			itemCoding, itemCnt = SRR()
			itemDict[itemCoding] = IG(itemCoding, 0) + itemCnt
		
		for itemCoding, itemCnt in itemDict.iteritems():
			role.AddItem(itemCoding, itemCnt)
			tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt)
		
		role.Msg(2, 0, tips)


class TwelvePalacePLiBao(object):
	def __init__(self, coding, itemList):
		'''
		十二星宫礼包
		@param coding:
		'''
		self.coding = coding
		self.itemList = itemList
		SR = self.randomItems = Random.RandomRate()
		for itemCoding, itemCnt, rate in itemList:
			SR.AddRandomItem(rate, (itemCoding, itemCnt))
		ItemUseBase.RegItemUserEx(coding, self)
	
	def __call__(self, role, item, cnt):
		#判断天赋卡背包是否有空间
		if role.GetTalentEmptySize() < cnt:
			role.Msg(2, 0, GlobalPrompt.TalentIsFull_Tips)
			return
		#扣礼包
		item.Use(cnt)
		
		tips = GlobalPrompt.Item_Use_Tips
		
		for _ in xrange(cnt):
			randomItems = self.randomItems.RandomOne()
			coding, icnt = randomItems
			if coding < 1000:
				#天赋卡
				role.AddTalentCard(coding)
				tips += GlobalPrompt.Talent_Tips % (coding, 1)
				cRoleMgr.Msg(1, 0, GlobalPrompt.Talent_Libao_Tips_1 % (role.GetRoleName(), coding, 1))
			else:
				role.AddItem(coding, icnt)
				tips += GlobalPrompt.Item_Tips % (coding, icnt)
		
		role.Msg(2, 0, tips)

class ShouChongLiBao(object):
	def __init__(self, coding, needUnbindRMB, rewardMoney, itemList):
		'''
		首充礼包
		@param coding:
		@param needUnbindRMB:开启需要的神石
		'''
		self.coding = coding
		self.needUnbindRMB = needUnbindRMB
		
		self.rewardMoney = rewardMoney
		self.itemList = itemList
		ItemUseBase.RegItemUserEx(coding, self)
	
	def __call__(self, role, item, cnt):
		#判断天赋卡背包是否有空间
		if role.GetUnbindRMB() < self.needUnbindRMB:
			return
		#扣礼包
		item.Use(1)
		
		#扣除神石
		role.DecUnbindRMB(self.needUnbindRMB)
		
		tips = GlobalPrompt.Item_Use_Tips
		tips += GlobalPrompt.Money_Tips % self.rewardMoney
		role.IncMoney(self.rewardMoney)
		for itemCoding, itemCnt in self.itemList:
			role.AddItem(itemCoding, itemCnt)
			tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt)
		
		role.Msg(2, 0, tips)
		
		
class Fireworks(object):
	def __init__(self, coding):
		'''
		烟花
		@param coding:烟花coding
		'''
		self.coding = coding
		ItemUseBase.RegItemUserEx(coding, self)
	
	def __call__(self, role, item, cnt):
		cfg = SceneMgr.SceneConfig_Dict.get(role.GetSceneID())
		if not cfg:
			return
		#只在公共场景燃放
		if cfg.SceneType != 2:
			role.Msg(2, 0, GlobalPrompt.UseFireWorksFail)
			return
		#是否可以燃放
		if not cfg.fireLimit:
			role.Msg(2, 0, GlobalPrompt.UseFireWorksFail)
			return
		
		#扣烟花
		item.Use(1)
		
		scene = role.GetScene()
		cNetMessage.PackPyMsg(UseFireworks, None)
		scene.BroadMsg()
		
		cRoleMgr.Msg(1, 0, GlobalPrompt.UseFireWorks_Tips % (role.GetRoleName(), scene.GetSceneName()))
		
class UniverLiBao(object):
	def __init__(self, coding, libaocfg):
		'''
		全民团购礼包
		@param coding:
		@param libaocfg:
		'''
		self.coding = coding
		self.libao_cfg = libaocfg
		ItemUseBase.RegItemUserEx(coding, self)
		
	def __call__(self, role, item, cnt):
		roleLevel = role.GetLevel()
		rewardItems = []
		if self.libao_cfg.items:
			rewardItems += self.libao_cfg.items
		if self.libao_cfg.levelVal1[0] <= roleLevel <= self.libao_cfg.levelVal1[1]:
			rewardItems += self.libao_cfg.levelitems1
		
		elif self.libao_cfg.levelVal2[0] <= roleLevel <= self.libao_cfg.levelVal2[1]:
			rewardItems += self.libao_cfg.levelitems2
		
		elif self.libao_cfg.levelVal3[0] <= roleLevel <= self.libao_cfg.levelVal3[1]:
			rewardItems += self.libao_cfg.levelitems3
		
		elif self.libao_cfg.levelVal4[0] <= roleLevel <= self.libao_cfg.levelVal4[1]:
			rewardItems += self.libao_cfg.levelitems4
		
		elif self.libao_cfg.levelVal5[0] <= roleLevel <= self.libao_cfg.levelVal5[1]:
			rewardItems += self.libao_cfg.levelitems5
		
		elif self.libao_cfg.levelVal6[0] <= roleLevel <= self.libao_cfg.levelVal6[1]:
			rewardItems += self.libao_cfg.levelitems6
		
		elif self.libao_cfg.levelVal7[0] <= roleLevel <= self.libao_cfg.levelVal7[1]:
			rewardItems += self.libao_cfg.levelitems7
		
		elif self.libao_cfg.levelVal8[0] <= roleLevel <= self.libao_cfg.levelVal8[1]:
			rewardItems += self.libao_cfg.levelitems8
			
		else:
			rewardItems += self.libao_cfg.levelitems7
		#扣礼包
		item.Use(cnt)
		tips = ""
		if self.libao_cfg.gold:
			role.IncMoney(self.libao_cfg.gold * cnt)
			tips += GlobalPrompt.Money_Tips % (self.libao_cfg.gold * cnt)
		if self.libao_cfg.bindrmb:
			role.IncBindRMB(self.libao_cfg.bindrmb * cnt)
			tips += GlobalPrompt.BindRMB_Tips % (self.libao_cfg.bindrmb * cnt)
		if self.libao_cfg.unbindrmb:
			role.IncUnbindRMB_S(self.libao_cfg.unbindrmb * cnt)
			tips += GlobalPrompt.UnBindRMB_Tips % (self.libao_cfg.unbindrmb * cnt)
		if rewardItems:
			for item in rewardItems:
				coding, codingcnt = item
				role.AddItem(coding, codingcnt * cnt)
				tips += GlobalPrompt.Item_Tips % (coding, codingcnt * cnt)
		role.Msg(2, 0, tips)



class TalentLiBao(object):
	def __init__(self, coding, cardList):
		'''
		天賦卡礼包
		@param coding:
		'''
		self.coding = coding
		self.cardList = cardList
		SR = self.randomCards = Random.RandomRate()
		for cardType, rate in cardList:
			SR.AddRandomItem(rate, cardType)
		ItemUseBase.RegItemUserEx(coding, self)
	
	def __call__(self, role, item, cnt):
		#判断天赋卡背包是否有空间
		if role.GetTalentEmptySize() < cnt:
			role.Msg(2, 0, GlobalPrompt.TalentIsFull_Tips)
			return
		item.Use(cnt)
		for _ in xrange(cnt):
			card = self.randomCards.RandomOne()
			role.AddTalentCard(card)
			role.Msg(2, 0, GlobalPrompt.Talent_Libao_Tips_2 % (card, 1))
		
class CardLiBao(object):
	def __init__(self, coding, dragonShardCnt, itemList):
		'''
		年卡相关礼包
		@param coding:
		@param dragonShardCnt:奖励龙晶数量
		@param itemList:
		'''
		self.coding = coding
		self.dragonShardCnt = dragonShardCnt
		self.itemList = itemList
		ItemUseBase.RegItemUserEx(coding, self)
	
	def __call__(self, role, item, cnt):
		#扣礼包
		item.Use(1)
		
		#根据等级给龙晶
		dragonShardCoding = 0
		level = role.GetLevel()
		if level >= 1 and level <= 39:
			dragonShardCoding = 25681
		elif level >= 40 and level <= 59:
			dragonShardCoding = 25682
		elif level >= 60 and level <= 79:
			dragonShardCoding = 25683
		elif level >= 80 and level <= 99:
			dragonShardCoding = 25684
		elif level >= 100 and level <= 119:
			dragonShardCoding = 25685
		elif level >= 120 and level <= 129:
			dragonShardCoding = 25686
		else:
			dragonShardCoding = 25686
		tips = GlobalPrompt.Item_Use_Tips
		role.AddItem(dragonShardCoding, self.dragonShardCnt)
		tips += GlobalPrompt.Item_Tips % (dragonShardCoding, self.dragonShardCnt)
		
		for itemCoding, itemCnt in self.itemList:
			role.AddItem(itemCoding, itemCnt)
			tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt)
		
		role.Msg(2, 0, tips)

class EquipmentEnchantLibao(object):
	def __init__(self, coding, itemList):
		'''
		装备附魔礼包，这是消耗道具开启的礼包 
		@param coding:礼包自己的coding
		@param itemList:开启礼包可以获得的物品 
		'''
		self.coding = coding
		self.itemList = itemList
		SR = self.randomItems = Random.RandomRate()
		for itemCoding, itemCnt, rate in itemList:
			SR.AddRandomItem(rate, (itemCoding, itemCnt))
		ItemUseBase.RegItemUserEx(coding, self)

	def __call__(self, role, item, cnt):
		#扣礼包
		item.Use(cnt)
		tips = GlobalPrompt.Item_Use_Tips
		awarddict = {}
		for _ in xrange(cnt):
			coding, icnt = self.randomItems.RandomOne()
			awarddict[coding] = awarddict.get(coding, 0) + icnt
		for iitem in awarddict.iteritems():
			role.AddItem(*iitem)
			tips += GlobalPrompt.Item_Tips % iitem
		role.Msg(2, 0, tips)

class MountEvolveFood(object):
	def __init__(self, coding, level):
		'''
		坐骑升阶丹
		@param coding:
		@param reputation:
		'''
		self.level = level
		ItemUseBase.RegItemUserEx(coding, self)
		
	def __call__(self, role, item, cnt):
		from Game.Mount import MountConfig, MountMgr
		
		mountMgr = role.GetTempObj(EnumTempObj.MountMgr)
		if not mountMgr:
			return
		#获取玩家坐骑进阶等级
		evolveId = role.GetI16(EnumInt16.MountEvolveID)
		
		if evolveId >= self.level:#坐骑等级大于该升阶丹的最大升阶数
			role.Msg(2, 0, GlobalPrompt.CAN_NOT_USE_MSG % ((self.level - 1) / 10))
			return
		
		if evolveId >= MountMgr.MAX_EVOLVEID:#坐骑已经是最高阶了
			return
		config = MountConfig._MOUNT_EVOLVE.get(evolveId)
		if not config:
			print "GE_EXC, can not find evolveId:(%s) Config in _MOUNT_EVOLVE in MountEvolveFood, " % evolveId
			return
		#转生中的坐骑不能使用
		if config.totalExp == role.GetI32(EnumInt32.MountExp):
			role.Msg(2, 0 , GlobalPrompt.MOUNT_EXP_MSG)
			return
		#先扣物品
		item.Use(cnt)
		if config.NextID:
			role.SetI32(EnumInt32.MountExp, config.totalExp)
			role.SendObj(MountMgr.Mount_Metempsychosis_for_client,config.NextID )
			MountEvolveID = role.GetI16(EnumInt16.MountEvolveID)
			role.Msg(2, 0, GlobalPrompt.USE_EVO_SUC_MSG % ((MountEvolveID - 1)/ 10, 10))
		else:
			#进化到下一个层次
			role.IncI16(EnumInt16.MountEvolveID, 1)
			#将坐骑经验清0
			role.SetI32(EnumInt32.MountExp, 0)
			#属性重算
			mountMgr.ResetAttribute()
			role.ResetGlobalMountProperty()
			MountEvolveID = role.GetI16(EnumInt16.MountEvolveID)
			role.Msg(2, 0, GlobalPrompt.USE_EVO_SUC_MSG % ((MountEvolveID - 1)/ 10, (MountEvolveID - 1) % 10))
		if role.GetI32(EnumInt32.MountTempExp) > 0:
			role.SetI32(EnumInt32.MountTempExp, 0)
		
class MountExpFood(object):
	def __init__(self, coding, exp):
		'''
		坐骑经验丹
		@param coding:
		@param reputation:
		'''
		self.exp = exp
		ItemUseBase.RegItemUserEx(coding, self)
		
	def __call__(self, role, item, cnt):
		from Game.Mount import MountConfig, MountMgr
		
		mountMgr = role.GetTempObj(EnumTempObj.MountMgr)
		if not mountMgr:
			return
		evolveId = role.GetI16(EnumInt16.MountEvolveID)
		if evolveId >= MountMgr.MAX_EVOLVEID:#坐骑已经是最高阶了
			return
		config = MountConfig._MOUNT_EVOLVE.get(evolveId)
		if not config:
			print "GE_EXC, can not find evolveId:(%s) Config in _MOUNT_EVOLVE in MountExpFood, " % evolveId
			return
		if config.totalExp == role.GetI32(EnumInt32.MountExp):
			role.Msg(2, 0, GlobalPrompt.MOUNT_EXP_MSG)
			return
		#先扣物品
		item.Use(cnt)
		MountMgr.AddMountExp(role, self.exp * cnt)
		role.Msg(2, 0, GlobalPrompt.USE_EXP_SUC_MSG % (self.exp * cnt))

class MountExpFoodTemp(object):
	def __init__(self, coding, exp):
		'''
		坐骑经验丹(加临时经验)
		@param coding:
		@param reputation:
		'''
		self.exp = exp
		ItemUseBase.RegItemUserEx(coding, self)
		
	def __call__(self, role, item, cnt):
		from Game.Mount import MountConfig, MountMgr
		if item.IsDeadTime():
			return
		mountMgr = role.GetTempObj(EnumTempObj.MountMgr)
		if not mountMgr:
			return
		evolveId = role.GetI16(EnumInt16.MountEvolveID)
		if evolveId >= MountMgr.MAX_EVOLVEID:#坐骑已经是最高阶了
			role.Msg(2, 0, GlobalPrompt.MOUNT_MAX_LEVEL)
			return
		config = MountConfig._MOUNT_EVOLVE.get(evolveId)
		if not config:
			print "GE_EXC, can not find evolveId:(%s) Config in _MOUNT_EVOLVE in MountExpFood, " % evolveId
			return
		if config.totalExp == role.GetI32(EnumInt32.MountExp):
			role.Msg(2, 0, GlobalPrompt.MOUNT_EXP_MSG)
			return
		#先扣物品
		item.Use(cnt)
		MountMgr.AddMountExpTemp(role, self.exp * cnt)
		role.Msg(2, 0, GlobalPrompt.USE_EXP_SUC_MSG % (self.exp * cnt))

class RandomMoneyLibao(object):
	def __init__(self, coding, ratelist):
		self.coding = coding 
		self.ratelist = ratelist
		SR = self.randomMoney = Random.RandomRate()
		for section, rate in ratelist:
			SR.AddRandomItem(rate, section)
		ItemUseBase.RegItemUserEx(coding, self)

	def __call__(self, role, item, cnt):
		#扣礼包
		item.Use(cnt)
		tips = GlobalPrompt.Item_Use_Tips
		MoneyToReward = 0
		for _ in xrange(cnt):
			section = self.randomMoney.RandomOne()
			MoneyToReward += random.randint(*section)
		role.IncMoney(MoneyToReward)
		tips += GlobalPrompt.Money_Tips % MoneyToReward
		role.Msg(2, 0, tips)

class MoonCakeTili(object):
	def __init__(self, coding, tili):
		'''
		中秋月饼
		@param coding: 物品编码
		@param tili: 使用增加的体力
		'''
		self.tili = tili
		ItemUseBase.RegItemUserEx(coding, self)
	
	def __call__(self, role, item, cnt):
		from Game.Role.Data import EnumDayInt8
		#每日使用次数检测
		usedNum = role.GetDI8(EnumDayInt8.AF_TodayMoonCakeUsedNum)
		if usedNum + cnt > EnumGameConfig.AF_MoonCakeDayNumMax:
			role.Msg(2, 0, GlobalPrompt.AF_MoonCakeTooMuchTip) 
			return
		
		#先扣物品
		item.Use(cnt)
		role.SetDI8(EnumDayInt8.AF_TodayMoonCakeUsedNum, usedNum + 1)
		role.IncTiLi(self.tili * cnt)
		role.Msg(2, 0, GlobalPrompt.AF_MoonCakeUseTip % (self.tili * cnt))


class DragonSoulLibao(object):
	def __init__(self, coding, mustItemList, itemList):
		'''
		龙灵礼包
		@param coding:礼包自己的coding
		@param itemList:开启礼包可以获得的物品 
		'''
		self.coding = coding
		self.itemList = itemList
		self.mustitemList = mustItemList
		SR = self.randomItems = Random.RandomRate()
		for itemCoding, itemCnt, rate in itemList:
			SR.AddRandomItem(rate, (itemCoding, itemCnt))
		ItemUseBase.RegItemUserEx(coding, self)

	def __call__(self, role, item, cnt):
		#扣礼包
		item.Use(cnt)
		tips = GlobalPrompt.Item_Use_Tips
		awarddict = {}
		if self.itemList:
			for _ in xrange(cnt):
				coding, icnt = self.randomItems.RandomOne()
				awarddict[coding] = awarddict.get(coding, 0) + icnt

		if 	self.mustitemList:
			for coding, icnt in self.mustitemList:
				awarddict[coding] = awarddict.get(coding, 0) + icnt * cnt

		for icoding, icnt in awarddict.iteritems():
			#26901为龙灵的itemcoding
			if icoding == 26901:
				role.IncDragonSoul(icnt)
			else:
				role.AddItem(icoding, icnt)
			tips += GlobalPrompt.Item_Tips % (icoding, icnt)
			
		role.Msg(2, 0, tips)

class ItemAddMount(object):
	def __init__(self, coding, mountId):
		self.mountId = mountId
		ItemUseBase.RegItemUserEx(coding, self)
	
	def __call__(self, role, item, cnt):
		from Game.Mount import MountMgr, MountConfig
		
		cfg = MountConfig._MOUNT_BASE.get(self.mountId)
		if not cfg:#不存在该坐骑ID
			print "GE_EXC,ItemAddMount can not find mountId(%s)" % self.mountId
			return
		
		mountMgr = role.GetTempObj(EnumTempObj.MountMgr)
		if self.mountId in mountMgr.MountId_list:#已经激活过了
			role.Msg(2, 0, GlobalPrompt.ACTIVE_MOUNT_REPEAT)
			return
		#扣道具
		item.Use(cnt)
		mountMgr.MountId_list.append(self.mountId)
		#幻化为该坐骑
		MountMgr.OnMount(role, self.mountId)
		
		if cfg.timeLimit:#有时限
			mountMgr.Mount_outData_dict[self.mountId] = cDateTime.Days() + cfg.timeLimit
			role.SendObj(MountMgr.Mount_Syn_Time, [mountMgr.Mount_outData_dict, mountMgr.MountAGDict])
		#属性重算
		mountMgr.ResetAttribute()
		role.ResetGlobalMountProperty()
		
		role.SendObj(MountMgr.Mount_Send_Unreal, mountMgr.MountId_list)
		#提示
		role.Msg(2, 0, GlobalPrompt.ACTIVE_MOUNT_SUC % cfg.mountName)
		
class ItemAddFirstPayMount(object):
	def __init__(self, coding, mountId):
		self.mountId = mountId
		ItemUseBase.RegItemUserEx(coding, self)
	
	def __call__(self, role, item, cnt):
		from Game.Mount import MountMgr, MountConfig
		
		cfg = MountConfig._MOUNT_BASE.get(self.mountId)
		if not cfg:#不存在该坐骑ID
			return
		
		mountMgr = role.GetTempObj(EnumTempObj.MountMgr)
		if self.mountId in mountMgr.MountId_list:#已经激活过了
			role.Msg(2, 0, GlobalPrompt.ACTIVE_MOUNT_REPEAT)
			return
		
		if self.mountId in role.GetObj(EnumObj.FirstPayBoxDay):
			#已经有这个坐骑了
			return
		
		role.SetObj(EnumObj.FirstPayBoxDay, {self.mountId : {1:cDateTime.Days(), 2:cDateTime.Days(), 3:1}})
		
		#扣道具
		item.Use(cnt)
		mountMgr.MountId_list.append(self.mountId)
		
		if cfg.timeLimit:#有时限
			mountMgr.Mount_outData_dict[self.mountId] = cDateTime.Days() + cfg.timeLimit
			role.SendObj(MountMgr.Mount_Syn_Time, [mountMgr.Mount_outData_dict, mountMgr.MountAGDict])
		
		#属性重算
		mountMgr.ResetAttribute()
		role.ResetGlobalMountProperty()
		
		role.SendObj(MountMgr.Mount_Send_Unreal, mountMgr.MountId_list)
		#提示
		role.Msg(2, 0, GlobalPrompt.ACTIVE_MOUNT_SUC % cfg.mountName)
	
class LuckyBag(object):
	
	def __init__(self, coding, cfg):
		self.coding = coding
		self.cfg = cfg
		ItemUseBase.RegItemUserEx(coding, self)
		
	def __call__(self, role, item, cnt):
		#背包不足
		if role.PackageEmptySize() < cnt:
			role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
			return
		#命魂背包空间不足 
		if role.GetTarotEmptySize() < cnt:
			role.Msg(2, 0, GlobalPrompt.TarotIsFull_Tips)
			return

		total_Item = {}
		total_Money = 0
		total_BindRMB = 0
		total_UnbindRMB_S = 0
		total_Tili = 0
		total_Tarot = {}
		
		total_list = []
		rolename = role.GetRoleName()
		from Game.Activity.LuckyBag import LuckyBagConfig
		LuckyBag_AwardIndex_Dict = LuckyBagConfig.LuckyBag_AwardIndex_Dict
		for _ in xrange(cnt):
			award_index = self.cfg.RandomRate.RandomOne()
			award_cfg = LuckyBag_AwardIndex_Dict.get(award_index)
			if not award_cfg:
				print "GE_EXC, error while award_cfg = LuckyBag_AwardIndex_Dict.get(award_index), no such award_index" % award_index
				return
			award_type = award_cfg.Type
			itemcoding = award_cfg.Coding
			itemcnt = award_cfg.Cnt
			#道具
			if award_type == 1:
				total_Item.setdefault(itemcoding, 0)
				total_Item[itemcoding] += itemcnt
			#命魂
			elif award_type == 2:
				total_Tarot.setdefault(itemcoding, 0)
				total_Tarot[itemcoding] += itemcnt
			#金币
			elif award_type == 3:
				total_Money += itemcnt
			#魔晶
			elif award_type == 4:
				total_BindRMB += itemcnt
			
			#神石
			elif award_type == 5:
				total_UnbindRMB_S += itemcnt
			#体力
			elif award_type == 6:
				total_Tili += itemcnt
			else:
				print "GE_EXC, error in RequestUseLuckBag, no such award_cfg.Type(%s)" % award_type
				return
			#如果需要记录红手榜的话
			if award_cfg.IsRedHand:
				total_list.append((self.coding, rolename, award_type, itemcoding, itemcnt))
				
		Tips = GlobalPrompt.LuckyBagUseTips

		item.Use(cnt)
		
		if total_Item:
			for item in total_Item.iteritems():
				role.AddItem(*item)
				Tips += GlobalPrompt.Item_Tips % item
				
		if total_Money:
			role.IncMoney(total_Money)
			Tips += GlobalPrompt.Money_Tips % total_Money
			
		if total_BindRMB:
			role.IncBindRMB(total_BindRMB)
			Tips += GlobalPrompt.BindRMB_Tips % total_BindRMB
			
		if total_UnbindRMB_S:
			role.IncUnbindRMB_S(total_UnbindRMB_S)
			Tips += GlobalPrompt.UnBindRMB_Tips % total_UnbindRMB_S
			
		if total_Tili:
			role.IncTiLi(total_Tili)
			Tips += GlobalPrompt.TiLi_Tips % total_Tili
			
		if total_Tarot:
			for tarot in total_Tarot.iteritems():
				role.AddTarotCard(*tarot)
				Tips += GlobalPrompt.Tarot_Tips % tarot
		
		from Game.Activity.LuckyBag import LuckyBagMgr
		LuckyBagDict = LuckyBagMgr.LuckyBagDict	
		redHandList = LuckyBagDict.get(self.coding, [])
		redHandList.extend(total_list)

		if len(redHandList) > 10:
			redHandList = redHandList[-10:]
			

		LuckyBagDict[self.coding] = redHandList
		
		role.Msg(2, 0, Tips)

##################################################################################
#随机魔晶礼包
##################################################################################
class RandomBindRMBLibao(object):
	def __init__(self, coding, ratelist):
		self.coding = coding 
		self.ratelist = ratelist
		SR = self.randomMoney = Random.RandomRate()
		for rate, bindRMB in ratelist:
			SR.AddRandomItem(rate, bindRMB)
		ItemUseBase.RegItemUserEx(coding, self)

	def __call__(self, role, item, cnt):
		#扣礼包
		item.Use(cnt)
		tips = GlobalPrompt.Item_Use_Tips
		BindRMBToReward = 0
		for _ in xrange(cnt):
			BindRMB = self.randomMoney.RandomOne()
			BindRMBToReward += BindRMB
		role.IncBindRMB(BindRMBToReward)
		tips += GlobalPrompt.BindRMB_Tips % BindRMBToReward
		role.Msg(2, 0, tips)
		
class CardBuff(object):
	'''
	变身卡
	'''
	def __init__(self, coding, buffId):
		self.buffId = buffId
		ItemUseBase.RegItemUserEx(coding, self)
	
	def __call__(self, role, item, cnt):
		from Game.Activity.HalloweenAct import HalloweenMgr, HalloweenConfig
		
		if role.GetSceneID() == EnumGameConfig.MarrySceneID:
			role.Msg(2, 0, GlobalPrompt.HallowNotChange)
			return
		
		cfg = HalloweenConfig.CARD_BUFF_DICT.get(self.buffId)
		if not cfg:
			print "GE_EXC,can not find buffId(%s) in UseTraCard" % self.buffId
			return
		now = cDateTime.Now()
		if now < cfg.startTime or now >= cfg.endTime:#过期
			role.Msg(2, 0, GlobalPrompt.HallowCardOverTime)
			return
		HalloweenData = role.GetObj(EnumObj.HalloweenData)
		buffDict = HalloweenData.setdefault(4, {})
		if len(buffDict) >= 5:
			role.Msg(2, 0, GlobalPrompt.ChangeCardUseLimit)
			return
		#扣除道具
		item.Use(cnt)
		
		nowTickData = HalloweenData.get(5, {})
		
		if self.buffId in buffDict:#假如buff已存在，删除原来的Tick
			role.UnregTick(nowTickData.get(self.buffId, 0))
		buffDict[self.buffId] = int(cDateTime.Seconds() + cfg.keepTime)
		#注册tick
		nowTickData[self.buffId] = role.RegTick(cfg.keepTime, HalloweenMgr.BuffEnd, self.buffId)
		#设置玩家状态
		role.SetAppStatus(self.buffId)
		role.SetI16(EnumInt16.RightBuffStatus, self.buffId)
		#重算属性
		role.GetPropertyGather().ReSetRecountCardBuffFlag()
		#同步给客户端
		HalloweenMgr.SynCardBuff(role)
		
class ChangeMountTime(object):
	'''
	将限时坐骑变永久坐骑
	'''
	def __init__(self, coding, mountId):
		self.mountId = mountId
		ItemUseBase.RegItemUserEx(coding, self)
		
	def __call__(self, role, item, cnt):
		from Game.Mount import MountMgr, MountConfig
		
		basecfg = MountConfig._MOUNT_BASE.get(self.mountId)
		if not basecfg:
			return
		if not basecfg.timeLimit:#不是有时限坐骑
			return
		
		mountMgr = role.GetTempObj(EnumTempObj.MountMgr)
		#玩家激活的坐骑中没有,#在历史记录也没有，即该玩家在调用该接口前未激活过该坐骑,直接返回
		if self.mountId not in mountMgr.MountId_list and \
			self.mountId not in mountMgr.history_outData_mountId:
			role.Msg(2, 0, GlobalPrompt.CHANGE_MOUNT_TIME_FAILT)
			return
		
		if self.mountId in mountMgr.MountId_list and self.mountId not in mountMgr.Mount_outData_dict:
			#已经激活且不在限时坐骑字典中
			role.Msg(2, 0, GlobalPrompt.CHANGE_MOUNT_TIME_FAILT_2)
			return
		
		#扣除道具
		item.Use(cnt)
		
		if self.mountId not in mountMgr.MountId_list:
			mountMgr.MountId_list.append(self.mountId)
		
		if self.mountId in mountMgr.Mount_outData_dict:
			del mountMgr.Mount_outData_dict[self.mountId]
		
		mountMgr.ResetAttribute()
		role.ResetGlobalMountProperty()
		role.SendObj(MountMgr.Mount_Syn_Time, [mountMgr.Mount_outData_dict, mountMgr.MountAGDict])
		role.Msg(2, 0, GlobalPrompt.CHANGE_MOUNT_TIME_SUC % basecfg.mountName)
		
class PetLiBao(object):
	'''
	宠物礼包
	'''
	def __init__(self, coding, petType, needRMB):
		self.petType = petType
		self.needRMB = needRMB
		ItemUseBase.RegItemUserEx(coding, self)
		
	def __call__(self, role, item, cnt):
		if role.GetUnbindRMB() < self.needRMB:
			return
		
		from Game.Pet import PetConfig
		Petcfg = PetConfig.PET_INIT_PROPERTY.get(self.petType)
		if not Petcfg:
			print "GE_EXC, petType(%s) is wrong in PetLiBao" % self.petType
			return
		#扣除道具
		item.Use(cnt)
		role.DecUnbindRMB(self.needRMB)
		#增加宠物
		role.AddPet(self.petType)
		role.Msg(2, 0, GlobalPrompt.PET_LIBAO_USE_MSG % Petcfg.name)


class JTGoldLiBao(object):
	'''
	荣誉礼包（金券）
	'''
	def __init__(self, coding, jtgold):
		self.jtgold = jtgold
		ItemUseBase.RegItemUserEx(coding, self)
		
	def __call__(self, role, item, cnt):
		
		item.Use(cnt)
		total = self.jtgold * cnt
		role.IncI32(EnumInt32.JTGold, total)

class TalentCardRandomLiBao(object):
	def __init__(self, coding, itemList):
		'''
		天赋卡随机礼包
		@param coding:
		'''
		self.coding = coding
		self.itemList = itemList
		SR = self.randomItems = Random.RandomRate()
		for itemCoding, itemCnt, rate in itemList:
			if itemCnt > 1:
				print "GE_EXC,TalentCardRandomLiBao::itemCnt(%s) > 1" % itemCnt
			SR.AddRandomItem(rate, (itemCoding, itemCnt))
		ItemUseBase.RegItemUserEx(coding, self)
	
	def __call__(self, role, item, cnt):
		#判断天赋卡背包是否有空间
		if role.GetTalentEmptySize() < cnt:
			role.Msg(2, 0, GlobalPrompt.TalentIsFull_Tips)
			return
		#扣礼包
		item.Use(cnt)
		
		tips = GlobalPrompt.Item_Use_Tips		
		for _ in xrange(cnt):
			randomItems = self.randomItems.RandomOne()
			coding, cnt = randomItems
			if coding < 1000:
				#增加天赋卡
				role.AddTalentCard(coding)
				#提示及广播
				tips += GlobalPrompt.Talent_Tips % (coding, cnt)
				role.Msg(2, 0, tips)
				cRoleMgr.Msg(1, 0, GlobalPrompt.Talent_Libao_Tips % (role.GetRoleName(), coding, cnt))
			else:
				print "GE_EXC, TalentCardRandomLiBao __call__ error coding(%s) > 1000 " % coding
			
class ZumaCardNormalLiBao(object):
	def __init__(self, coding, itemList):
		'''
		祖玛龙珠变身卡普通礼包
		@param coding:礼包自己的coding
		@param itemList:开启礼包可以获得的物品 
		'''
		self.coding = coding
		self.itemList = itemList
		SR = self.randomItems = Random.RandomRate()
		for itemCoding, itemCnt, rate in itemList:
			SR.AddRandomItem(rate, (itemCoding, itemCnt))
		ItemUseBase.RegItemUserEx(coding, self)

	def __call__(self, role, item, cnt):
		#扣礼包
		item.Use(cnt)
		tips = GlobalPrompt.Item_Use_Tips
		awarddict = {}
		if self.itemList:
			for _ in xrange(cnt):
				coding, icnt = self.randomItems.RandomOne()
				awarddict[coding] = awarddict.get(coding, 0) + icnt

		for icoding, icnt in awarddict.iteritems():
			role.AddItem(icoding, icnt)
			
			#是否添加收集
			ZumaMgr.IsIncCollectItem(role, icoding, icnt)
			
			tips += GlobalPrompt.Item_Tips % (icoding, icnt)
			
		role.Msg(2, 0, tips)
		
class ZumaCardAdvancedLiBao(object):
	def __init__(self, coding, itemList):
		'''
		祖玛龙珠变身卡高级礼包
		@param coding:礼包自己的coding
		@param itemList:开启礼包可以获得的物品 
		'''
		self.coding = coding
		self.itemList = itemList
		SR = self.randomItems = Random.RandomRate()
		for itemCoding, itemCnt, rate in itemList:
			SR.AddRandomItem(rate, (itemCoding, itemCnt))
		ItemUseBase.RegItemUserEx(coding, self)

	def __call__(self, role, item, cnt):
		#扣礼包
		item.Use(cnt)
		tips = GlobalPrompt.Item_Use_Tips
		awarddict = {}
		if self.itemList:
			for _ in xrange(cnt):
				coding, icnt = self.randomItems.RandomOne()
				awarddict[coding] = awarddict.get(coding, 0) + icnt

		for icoding, icnt in awarddict.iteritems():
			role.AddItem(icoding, icnt)
			
			#是否添加收集
			ZumaMgr.IsIncCollectItem(role, icoding, icnt)
			
			tips += GlobalPrompt.Item_Tips % (icoding, icnt)
			
		role.Msg(2, 0, tips)
	

class PetLiBao_1(object):
	'''
	宠物礼包(国服)
	'''
	def __init__(self, coding, petType):
		self.petType = petType
		ItemUseBase.RegItemUserEx(coding, self)
		
	def __call__(self, role, item, cnt):
		from Game.Pet import PetConfig
		Petcfg = PetConfig.PET_INIT_PROPERTY.get(self.petType)
		if not Petcfg:
			print "GE_EXC, petType(%s) is wrong in PetLiBao" % self.petType
			return
		#扣除道具
		item.Use(1)
		#增加宠物
		role.AddPet(self.petType)
		role.Msg(2, 0, GlobalPrompt.PET_LIBAO_USE_MSG % Petcfg.name)

class ItemAddTitle(object):
	'''
	道具增加称号
	'''
	def __init__(self, coding, titleId):
		self.titleId = titleId
		ItemUseBase.RegItemUserEx(coding,self)
		
	def __call__(self, role, item, cnt):
		from Game.Activity.Title import Title, TitleConfig
		
		Titlecfg = TitleConfig.Title_Dict.get(self.titleId)
		if not Titlecfg:
			print "GE_EXC, error in ItemAddTitle not this cfg (%s)" % self.titleId
			return
		
		titleDict = role.GetObj(EnumObj.Title)
		if not titleDict:
			return
		
		titleDataDict = titleDict.get(1)
		if self.titleId in titleDataDict:
			role.Msg(2, 0, GlobalPrompt.Title_RepeatTitle)
			return
		
		#扣除道具
		item.Use(1)
		#增加称号
		Title.AddTitle(role.GetRoleID(), self.titleId)
		
class ItemAddQinmi(object):
	'''
	道具增加亲密
	'''
	def __init__(self, coding, qinmi):
		self.qinmi = qinmi
		ItemUseBase.RegItemUserEx(coding,self)
		
	def __call__(self, role, item, cnt):
		#扣道具
		item.Use(cnt)
		
		#计算总的亲密
		totalQinmi = cnt * self.qinmi
		role.IncI32(EnumInt32.Qinmi, totalQinmi)
		
		#提示
		tips = GlobalPrompt.Item_Use_Tips
		tips += GlobalPrompt.CouplesGoal_Tips_Addinmi % totalQinmi
		role.Msg(2, 0, tips)
		
class ItemAddResource(object):
	'''
	道具增加公会资源
	'''
	def __init__(self, coding):
		ItemUseBase.RegItemUserEx(coding,self)
		
	def __call__(self, role, item, cnt):
		unionObj = role.GetUnionObj()
		if not unionObj:
			#提示
			role.Msg(2, 0, GlobalPrompt.UNION_CANT_USE_ITEM)
			return
		
		#扣道具
		item.Use(cnt)
		
		#计算总的亲密
		totalResoure = cnt
		unionObj.IncUnionResource(totalResoure)
		
		#提示
		tips = GlobalPrompt.Item_Use_Tips
		tips += GlobalPrompt.UnionResource_Tips % totalResoure
		role.Msg(2, 0, tips)
		
class ItemAddContribution(object):
	'''
	道具增加公会资源
	'''
	def __init__(self, coding):
		ItemUseBase.RegItemUserEx(coding,self)
		
	def __call__(self, role, item, cnt):
		unionObj = role.GetUnionObj()
		if not unionObj:
			#提示
			role.Msg(2, 0, GlobalPrompt.UNION_CANT_USE_ITEM)
			return
		
		#扣道具
		item.Use(cnt)
		
		#计算总的亲密
		totalContribution = cnt
		role.IncContribution(totalContribution)
		
		#提示
		tips = GlobalPrompt.Item_Use_Tips
		tips += GlobalPrompt.UnionContribution_Tips % totalContribution
		role.Msg(2, 0, tips)

class ItemAddReputation(object):
	def __init__(self, coding, reputation):
		'''
		道具增加声望
		@param coding:
		@param reputation:
		'''
		self.reputation = reputation
		ItemUseBase.RegItemUserEx(coding, self)
		
	def __call__(self, role, item, cnt):
		#检测使用数量是否合理
		if cnt < 1:
			return
		
		#计算总声望
		totalReputation = self.reputation * cnt
		
		#先扣物品
		item.Use(cnt)
		
		#增加声望值
		role.IncReputation(totalReputation)
		
		#冒泡提示
		role.Msg(2, 0, GlobalPrompt.Item_Use_Tips + GlobalPrompt.Reputation_Tips % totalReputation)
		
class ItemAddPetTrainValue(object):
	def __init__(self, coding, stardata):
		'''
		道具增加指定星级宠物所有属性
		@param coding:
		@param reputation:
		'''
		self.star, self.ptdict = stardata
		ItemUseBase.RegItemUserEx(coding, self)
		
	def __call__(self, role, item, cnt):
		#检测使用数量是否合理
		if cnt < 1:
			return
		if item.IsDeadTime():
			return
		petMgr = role.GetTempObj(EnumTempObj.PetMgr)
		if not petMgr:
			return
		if not petMgr.pet_dict:#玩家没宠物
			return
		hasStar = False
		for pet in petMgr.pet_dict.itervalues():
			if pet.star == self.star:
				hasStar = True
				break
		if not hasStar:
			role.Msg(2, 0, GlobalPrompt.PET_ITEM_NOT_STAR)
			return
		#先扣物品
		item.Use(cnt)
		#设置属性
		LatestActData = role.GetObj(EnumObj.LatestActData)
		petData = LatestActData.get(7, {})
		starData = petData.setdefault(self.star, {})
		PT_LIST = [1, 4, 6, 8, 9, 10, 11, 12, 13]#这个主要是防止策划配错
		for pt, pv in self.ptdict.iteritems():
			if pt not in PT_LIST:
				print "GE_EXC,ItemUserClass.ItemAddPetTrainValue pt(%s) is wrong" % pt
				return
			starData[pt] = starData.get(pt, 0) + pv * cnt
		from Game.Pet import PetMgr
		PetMgr.ItemPetTrainTigger(role, self.star)
		role.Msg(2, 0, GlobalPrompt.PET_ITEM_USE_SUC)
		
class ItemAddPetEvoValue(object):
	def __init__(self, coding, evodata):
		'''
		道具增加指定阶数宠物所有临时修行进度
		@param coding:
		@param reputation:
		'''
		self.evoId, self.tempValue = evodata
		ItemUseBase.RegItemUserEx(coding, self)
		
	def __call__(self, role, item, cnt):
		#检测使用数量是否合理
		if cnt < 1:
			return
		if item.IsDeadTime():
			return
		petMgr = role.GetTempObj(EnumTempObj.PetMgr)
		if not petMgr:
			return
		if not petMgr.pet_dict:#玩家没宠物
			return
		hasEvoId = False
		for pet in petMgr.pet_dict.itervalues():
			if pet.evoId == self.evoId:
				hasEvoId = True
				break
		if not hasEvoId:
			role.Msg(2, 0, GlobalPrompt.PET_ITEM_NOT_EVO)
			return
		#先扣物品
		item.Use(cnt)
		#设置属性
		LatestActData = role.GetObj(EnumObj.LatestActData)
		petData = LatestActData.get(8, {})
		petData[self.evoId] = petData.get(self.evoId, 0) + self.tempValue * cnt

		from Game.Pet import PetMgr
		PetMgr.ItemPetEvoTigger(role, self.evoId)
		role.Msg(2, 0, GlobalPrompt.PET_ITEM_USE_SUC)
		
class ItemAddWingTrainValue(object):
	def __init__(self, coding, tempValue):
		'''
		道具增加所有羽翼临时进度值
		@param coding:
		@param reputation:
		'''
		self.tempValue = tempValue
		ItemUseBase.RegItemUserEx(coding, self)
		
	def __call__(self, role, item, cnt):
		#检测使用数量是否合理
		if cnt < 1:
			return
		if item.IsDeadTime():
			return
		
		wingDict = role.GetObj(EnumObj.Wing).get(1, {})
		if not wingDict:
			return
		
		from Common import CValue
		nowValue = role.GetI16(EnumInt16.WingTempTrainValue)
		remainValue = CValue.MAX_INT16 - 1 - nowValue
		del_cnt = cnt
		if remainValue < self.tempValue * cnt:
			del_cnt = remainValue / self.tempValue
		if not del_cnt:
			return
		#先扣物品
		item.Use(del_cnt)
		#增加临时进度值
		role.IncI16(EnumInt16.WingTempTrainValue, self.tempValue * del_cnt)

		from Game.Wing import WingMgr
		WingMgr.ItemWingTigger(role)
		role.Msg(2, 0, GlobalPrompt.PET_ITEM_USE_SUC)
		
class ItemAddDragonTrainValue(object):
	def __init__(self, coding, tempData):
		'''
		道具增加所有羽翼临时进度值
		@param coding:
		@param reputation:
		'''
		self.tempData = tempData
		ItemUseBase.RegItemUserEx(coding, self)
		
	def __call__(self, role, item, cnt):
		#检测使用数量是否合理
		if cnt < 1:
			return
		if item.IsDeadTime():
			return
		
		grade, tempValue = self.tempData
		if tempValue <= 0:
			return
		
		dragonTrainMgr = role.GetTempObj(EnumTempObj.DragonTrainMgr)
		if not dragonTrainMgr:
			return
		IsFalse = False
		for _, dragonObj in dragonTrainMgr.dragon_dict.iteritems():
			if dragonObj.grade == grade:
				IsFalse = True
				break
		if not IsFalse:
			role.Msg(2, 0, GlobalPrompt.DRAGON_ITEM_NOT_EVO)
			return
		
		#先扣物品
		item.Use(cnt)
		#设置临时进度
		LatestActData = role.GetObj(EnumObj.LatestActData)
		petData = LatestActData.get(9, {})
		petData[grade] = petData.get(grade, 0) + tempValue * cnt
		
		from Game.DragonTrain import DragonTrainMgr
		DragonTrainMgr.ItemAddTempValue(role, grade)
		
class ItemAddWarStationPro(object):
	def __init__(self, coding):
		'''
		战魂强化石
		@param coding:
		@param reputation:
		'''
		ItemUseBase.RegItemUserEx(coding, self)
		
	def __call__(self, role, item, cnt):
		#检测使用数量是否合理
		if cnt < 1:
			return
		WarStationStarNum = role.GetI16(EnumInt16.WarStationStarNum)
		from Game.WarStation import WarStationConfig
		cfg = WarStationConfig.WAR_STATION_BASE.get(WarStationStarNum)
		if not cfg:
			print "GE_EXC,ItemUserClass.ItemAddWarStationPro starNum(%s) is wrong" % WarStationStarNum
			return
		
		if role.GetI16(EnumInt16.UseStationItemCnt) >= cfg.useTimes:
			role.Msg(2, 0, GlobalPrompt.WarStation_Item_False)
			return
		#先扣物品
		item.Use(cnt)
		#增加使用次数
		role.IncI16(EnumInt16.UseStationItemCnt, cnt)
		#重算属性
		role.GetTempObj(EnumTempObj.WarStationMgr).ReSetWSItemPro()
		role.ResetGlobalWStationItemProperty()
		#提示
		role.Msg(2, 0, GlobalPrompt.WarStation_Item_Suc % (role.GetI16(EnumInt16.UseStationItemCnt), cfg.useTimes))
		
		
class ItemAddStationSoulPro(object):
	def __init__(self, coding):
		'''
		阵灵强化石
		@param coding:
		'''
		ItemUseBase.RegItemUserEx(coding, self)
		
	def __call__(self, role, item, cnt):
		#检测使用数量是否合理
		if cnt < 1:
			return
		
		stationSoulId = role.GetI16(EnumInt16.StationSoulId)
		ssCfg = StationSoulConfig.StationSoul_BaseConfig_Dict.get(stationSoulId)
		if not ssCfg:
			print "GE_EXC, ItemAddStationSoulPro::not ssCfg with stationSoulId(%s) with role(%s)" % (stationSoulId, role.GetRoleID())
			return
		
		oldUseCnt = role.GetI16(EnumInt16.StationSoulItemCnt)
		if oldUseCnt + cnt > ssCfg.maxItemCnt:
			role.Msg(2, 0, GlobalPrompt.StationSoul_Item_Fail)
			return
		
		#扣除物品
		item.Use(cnt)
		#增加使用记录
		role.IncI16(EnumInt16.StationSoulItemCnt, cnt)
		
		#使用成功提示
		role.Msg(2, 0, GlobalPrompt.StationSoul_Item_Suc % (oldUseCnt+cnt, ssCfg.maxItemCnt))
		#重算属性
		role.ResetGlobalStationSoulItemProperty()


class ZhuanshuLibao(object):
	def __init__(self, coding, awardCoding, baseCnt, addCntList):
		'''
		@param coding:礼包自己的coding
		@param awardCoding:开启礼包获得物品道具
		@param baseCnt:开启礼包获得物品道具的基本数量
		@param addCntList:开启礼包获得物品道具的额外数量(数量，概率)
		'''
		self.coding = coding
		self.awardCoding = awardCoding
		self.baseCnt = baseCnt
		self.addCntList = addCntList
		
		SR = self.randomItems = Random.RandomRate()
		for addCnt, rate in addCntList:
			SR.AddRandomItem(rate, addCnt)
		ItemUseBase.RegItemUserEx(coding, self)

	def __call__(self, role, item, cnt):
		#扣礼包
		item.Use(1)
		tips = GlobalPrompt.Item_Use_Tips
		
		addCnt = self.randomItems.RandomOne()
		totalCnt = self.baseCnt + addCnt
		role.AddItem(self.awardCoding, totalCnt)
		tips += GlobalPrompt.Item_Tips % (self.awardCoding, totalCnt)
		role.Msg(2, 0, tips)
		
		from Game.Item import ItemConfig
		cfg1 = ItemConfig.ItemCfg_Dict.get(self.coding)
		cfg2 = ItemConfig.ItemCfg_Dict.get(self.awardCoding)
		if not cfg1 or not cfg2:
			return
		if addCnt > 0:
			cRoleMgr.Msg(1, 0, GlobalPrompt.ZhuanShuLibaoTips % (role.GetRoleName(), cfg1.name, cfg2.name, addCnt))

class HongBaoLiBao(object):
	def __init__(self, coding, itemList):
		'''
		红包礼包
		@param coding:
		'''
		self.coding = coding
		self.itemList = itemList
		self.randomItems = {}
		for i, items in enumerate(itemList):
			r = Random.RandomRate()
			self.randomItems[i] = r
			for itemCoding, itemCnt, rate, isPrecious in items:
				r.AddRandomItem(rate, (itemCoding, itemCnt, isPrecious))

		ItemUseBase.RegItemUserEx(coding, self)

	def __call__(self, role, item, cnt):
		#使用等级
		roleLevel = role.GetLevel()
		if roleLevel < 30:
			return
		#扣礼包
		item.Use(cnt)
		tips = GlobalPrompt.Item_Use_Tips
		itemDict = {}
		IG = itemDict.get

		levelindex = 0
		if roleLevel <= 39:
			levelindex = 0
		elif roleLevel <= 59:
			levelindex = 1
		elif roleLevel <= 79:
			levelindex = 2
		elif roleLevel <= 99:
			levelindex = 3
		elif roleLevel <= 179:
			levelindex = 4
		else:
			levelindex = 4
			print "GE_EXC, error in HongBaoLiBao level overflow (%s) (%s)" % (self.coding, roleLevel)
		
		SRR = self.randomItems.get(levelindex)
		if not SRR:
			print "GE_EXC, error in HongBaoLiBao level overflow (%s) (%s)" % (self.coding, roleLevel)
			return
		
		SRR = SRR.RandomOne
		
		for _ in xrange(cnt):
			itemCoding, itemCnt, isPrecious = SRR()
			itemDict[itemCoding] = IG(itemCoding, 0) + itemCnt
			if isPrecious:
				cRoleMgr.Msg(11, 0, GlobalPrompt.QiangHongBao_Msg_Presious % (role.GetRoleName(), itemCoding, itemCnt))
		
		for itemCoding, itemCnt in itemDict.iteritems():
			role.AddItem(itemCoding, itemCnt)
			tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt)
		
		role.Msg(2, 0, tips)

class RandomUnBindRMBLiBao(object):
	def __init__(self, coding, RMBRange):
		'''
		随机神石礼包
		@param coding:
		'''
		self.coding = coding
		self.RMBRange = RMBRange
		ItemUseBase.RegItemUserEx(coding, self)

	def __call__(self, role, item, cnt):
		#使用等级
		roleLevel = role.GetLevel()
		if roleLevel < 30:
			return
		#参数正检测
		if cnt < 1:
			return
		#扣礼包
		item.Use(cnt)
		tips = GlobalPrompt.Item_Use_Tips
		for _ in xrange(cnt):
			rRMBCnt = random.randint(*self.RMBRange)
			role.IncUnbindRMB_S(rRMBCnt)
			role.Msg(2, 0, tips + GlobalPrompt.UnBindRMB_Tips % rRMBCnt)
			
#星灵幸运石
class StarGirlLucky(object):
	def __init__(self, coding):
		'''
		星灵幸运石
		@param coding:
		'''
		ItemUseBase.RegItemUserEx(coding, self)
	def __call__(self, role, item, cnt):
		StarGirlMgr.StarLevelUpByLucky(role, item, cnt)
		
		
class ItemAddRingValue(object):
	def __init__(self, coding, tempValue):
		'''
		道具增加婚戒临时经验值
		@param coding:
		@param reputation:
		'''
		self.tempValue = tempValue
		ItemUseBase.RegItemUserEx(coding, self)
		
	def __call__(self, role, item, cnt):
		#检测使用数量是否合理
		if cnt < 1:
			return
		if item.IsDeadTime():
			return
		#等级
		if role.GetLevel() < EnumGameConfig.MarryLevelLimit:
			return
		
		from Game.Marry import MarryConfig, WeddingRing
		WeddingRingID = role.GetI16(EnumInt16.WeddingRingID)
		cfg = MarryConfig.WeddingRing_Dict.get(WeddingRingID)
		if not cfg:
			print "GE_EXC, RequestNormalForging can not find nowWeddingRingID (%s) in WeddingRing_Dict" % WeddingRingID
			return
		if cfg.nextID == -1:
			role.Msg(2, 0, GlobalPrompt.WeddingRing_MAX_LEVEL)
			return
		#当前经验值
		nowExp = role.GetI32(EnumInt32.WeddingRingExp)
		#经验满, 需要进阶
		if cfg.maxExp <= nowExp and cfg.isUpGrade:
			return
		#先扣物品
		item.Use(cnt)
		#增加临时经验值
		WeddingRing.AddTempExp(role, self.tempValue * cnt)
		
		
#幸运红包
class LuckyHongBao(object):
	def __init__(self, coding):
		'''
		幸运红包，积分道具的使用（消费积分和充值积分）
		@param coding:
		'''
		ItemUseBase.RegItemUserEx(coding, self)
	def __call__(self, role, item, cnt):
		PassionTGPointExchangeMgr.PassionRequestAddPoint(role, item, cnt)


class ItemUnionHongBao(object):
	def __init__(self, coding):
		'''
		公会红包，使用道具发红包
		@param coding:
		'''
		ItemUseBase.RegItemUserEx(coding, self)
	def __call__(self, role, item, cnt):
		UseItemSetUnionHongBao(role, item, cnt)


class CardAtlas(object):
	def __init__(self, coding, cardId):
		'''
		卡牌图鉴卡牌
		@param coding:
		'''
		self.cardId = cardId
		ItemUseBase.RegItemUserEx(coding, self)
		
	def __call__(self, role, item, cnt):
		#扣道具
		
		if role.CardAtlasPackageIsFull():
			role.Msg(2, 0, GlobalPrompt.CardAtlasFull_Tips)
			return
		
		item.Use(cnt)
		
		role.AddCardAtlas(self.cardId, cnt)
		
		#提示
		tips = GlobalPrompt.Item_Use_Tips
		tips += GlobalPrompt.CardAtlas_Tips % (self.cardId, cnt)
		
		role.Msg(2, 0, tips)
		
class CardAtlasChip(object):
	def __init__(self, coding, returnChip):
		'''
		卡牌图鉴卡牌碎片
		@param coding:
		'''
		self.returnChip = returnChip
		ItemUseBase.RegItemUserEx(coding, self)
		
	def __call__(self, role, item, cnt):
		#扣道具
		item.Use(cnt)
		
		returnChip = self.returnChip * cnt
		role.IncI32(EnumInt32.CardAtlasChip, returnChip)
		
		#提示
		tips = GlobalPrompt.Item_Use_Tips
		tips += GlobalPrompt.CardAtlasChip_Tips % returnChip
		role.Msg(2, 0, tips)
class NewYearPigAmount(object):
	'''
	新年活动金猪兑换道具使用
	'''
	def __init__(self, coding, itemList):
		self.coding = coding
		self.itemList = itemList
		SR = self.randomItems = Random.RandomRate()
		for itemCnt, rate in itemList:
			SR.AddRandomItem(rate, itemCnt)
		ItemUseBase.RegItemUserEx(coding, self)
	
	def __call__(self, role, item, cnt):
		#扣道具
		from Game.Activity.NewYearDay import NewYearDayPigMgr
		item.Use(cnt)
		numbers = 0
		for _ in xrange(cnt):
			icnt = self.randomItems.RandomOne()
			numbers += icnt
		tips = GlobalPrompt.NewYearDayPigAmountTips % numbers	
		PigAmount = role.GetObj(EnumObj.PassionActData)[PassionNewYearPig][2]
		PigAmount += numbers
		role.GetObj(EnumObj.PassionActData)[PassionNewYearPig][2] = PigAmount
		role.Msg(2, 0, tips)
		NewYearDayPigMgr.OpenNewYearDayPigShop(role)
	
class ItemAddSealLiLian(object):
	'''
	圣印历练值
	'''
	def __init__(self, coding, SealLiLianValue):
		self.SealLiLianValue = SealLiLianValue
		ItemUseBase.RegItemUserEx(coding, self)
		
	def __call__(self, role, item, cnt):
		#检测使用数量是否合理
		if cnt < 1:
			return
		
		totalSealLiLianValue = self.SealLiLianValue * cnt
		
		item.Use(cnt)
		
		role.IncI32(EnumInt32.SealLiLianAmounts, totalSealLiLianValue)
		
		#冒泡提示
		role.Msg(2, 0, GlobalPrompt.Item_Use_Tips + GlobalPrompt.SealExp_Tips % totalSealLiLianValue)


class ElementVisionItem(object):
	'''
	元素幻化外形解锁道具
	'''
	def __init__(self, coding, visionId):
		self.visionId = visionId
		ItemUseBase.RegItemUserEx(coding, self)
		
	def __call__(self, role, item, cnt):
		#检测使用数量是否合理 
		if 1 != cnt:
			return
		
		if role.GetLevel() < EnumGameConfig.ElementVision_NeedLevel:
			return
		
		#已经拥有了
		elementBrandMgr = role.GetElementBrandMgr()
		if not elementBrandMgr or elementBrandMgr.has_vision(self.visionId):
			return
		
		item.Use(cnt)
		
		elementBrandMgr.new_vision(self.visionId)
		
		
class ItemAddCollectWord(object):
	'''
	收集大作战收集字
	'''
	def __init__(self, coding, index):
		self.index = index
		ItemUseBase.RegItemUserEx(coding, self)
		
	def __call__(self, role, item, cnt):
		#检测使用数量是否合理
		if cnt < 1:
			return
		
		from Game.Activity.CollectFight import CollectFight
		if not CollectFight.IsStart or not CollectFight.IsControlSync or not CollectFight.AllServerData or not CollectFight.CollectFightDict.returnDB:
			role.Msg(2, 0, GlobalPrompt.CollectFightUseFail)
			return
		w = GlobalPrompt.ReturnCollectWord(self.index)
		if not w:
			return
		
		item.Use(cnt)
		
		CollectFight.AddWorld(role, self.index, cnt)
		
		#冒泡提示
		role.Msg(2, 0, GlobalPrompt.CollectFightUseSuccess % (cnt, w))
	

class ItemAddHeroByLevel(object):
	'''
	增加指定等级的英雄
	'''
	def __init__(self, coding, heroId, level):
		self.heroId, self.level = heroId, level
		ItemUseBase.RegItemUserEx(coding, self)
		
	def __call__(self, role, item, cnt):
		#检测使用数量是否合理
		if cnt < 1:
			return
		from Game.Hero import HeroConfig, HeroOperate
		cfg = HeroConfig.Hero_Base_Config.get(self.heroId)
		if not cfg:
			print "GE_EXC, AddHero can not find heroNumber:(%s) in Hero_Base_Config" % self.heroId
			return
			#英雄满了
		roleHeroMgr = role.GetTempObj(EnumTempObj.enHeroMgr)
		if not roleHeroMgr:
			return
		if roleHeroMgr.IsHeroFull():
			return
		item.Use(cnt)
		HeroOperate.AddHeroByLevel(role, self.heroId, self.level)
		