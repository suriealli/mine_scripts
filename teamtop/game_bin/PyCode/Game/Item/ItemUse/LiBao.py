#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Item.ItemUse.LiBao")
#===============================================================================
# 礼包
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile
from Game.Item.ItemUse import ItemUserClass, ItemUseClassExtend



EnumMoney = 1		#只出金币礼包
EnumBindRMB = 2		#只出魔晶
EnumUnbindRMB = 3	#只出神石
EnumTiLi = 4		#只出体力
EnumTarotHP = 5		#只出命力
EnumItem = 6		#只出物品
EnumTarot = 7		#只出命魂
EnumNormal = 8		#必出礼包
EnumItemRandom = 9	#随机物品礼包
EnumTarotRandom = 10	#随机命魂礼包
EnumRandom = 11		#混合随机礼包
EnumSuper = 12		#傻瓜礼包



if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("ItemConfig")
	
	LiBaoConfig_Dict = {}


class LiBaoConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("LiBao.txt")
	def __init__(self):
		self.itemCoding = int
		self.libaoType = int
		self.what = str
		self.money = self.GetEvalByString
		self.bindrmb = self.GetEvalByString
		self.unbindrmb = self.GetEvalByString
		self.tili = self.GetEvalByString
		self.tarothp = self.GetEvalByString
		
		self.items = self.GetEvalByString#[(itemcoding, cnt),]
		self.tarots = self.GetEvalByString#[(cardType, cnt),]
		self.items_60 = self.GetEvalByString#[(itemcoding, cnt),]
		self.tarots_60 = self.GetEvalByString#[(cardType, cnt),]
		
		self.ratemoney = self.GetEvalByString#(rate, money)
		self.ratebindrmb = self.GetEvalByString
		self.rateunbindrmb = self.GetEvalByString
		self.ratetili = self.GetEvalByString
		self.ratetarothp = self.GetEvalByString
		
		self.rateitems = self.GetEvalByString#[(rate, itemcoding, cnt)]
		self.ratetarots = self.GetEvalByString#[(rate, cardType, cnt),]
		self.rateitems_60 = self.GetEvalByString
		self.ratetarots_60 = self.GetEvalByString
	
	def Preprocess(self):
		
		if (self.items and (not self.items_60)) or (self.items_60 and (not self.items)):
			print "GE_EXC, Libao error items error %s" % self.itemCoding
		if (self.tarots and (not self.tarots_60)) or (self.tarots_60 and (not self.tarots)):
			print "GE_EXC, Libao error tarots error %s" % self.itemCoding
		if (self.rateitems and (not self.rateitems_60)) or (self.rateitems_60 and (not self.rateitems)):
			print "GE_EXC, Libao error rateitems error %s" % self.itemCoding
		if (self.ratetarots and (not self.ratetarots_60)) or (self.ratetarots_60 and (not self.ratetarots)):
			print "GE_EXC, Libao error ratetarots error %s" % self.itemCoding
			
		if self.libaoType == EnumMoney:
			ItemUserClass.LiBao_Money(self.itemCoding, self.money)
			return
		if self.libaoType == EnumBindRMB:
			ItemUserClass.LiBao_BindRMB(self.itemCoding, self.bindrmb)
			return
		if self.libaoType == EnumUnbindRMB:
			ItemUserClass.LiBao_UnbindRMB(self.itemCoding, self.unbindrmb)
			return
		if self.libaoType == EnumTiLi:
			ItemUserClass.LiBao_TiLi(self.itemCoding, self.tili)
			return
		if self.libaoType == EnumTarotHP:
			ItemUserClass.LiBao_TarotHp(self.itemCoding, self.tarothp)
			return
		if self.libaoType == EnumItem:
			ItemUserClass.LiBao_Items(self.itemCoding, self.items, self.items_60)
			return
		if self.libaoType == EnumTarot:
			ItemUserClass.LiBao_Tarot(self.itemCoding, self.tarots, self.tarots_60)
			return
		
		if self.libaoType == EnumNormal:
			#25839 20级等级礼包 #25840 30级等级礼包,特殊处理
			if self.itemCoding == 25839 or self.itemCoding == 25840:
				ItemUseClassExtend.LevelLiBao(self.itemCoding, self)
			else:
				ItemUserClass.LiBao_Normal(self.itemCoding, self)
			return
		
		if self.libaoType == EnumItemRandom:
			ItemUserClass.LiBao_Random_Item(self.itemCoding, self)
			return
		
		if self.libaoType == EnumTarotRandom:
			ItemUserClass.LiBao_Random_Tarot(self.itemCoding, self)
			return
		
		if self.libaoType == EnumRandom:
			ItemUserClass.LiBao_Random(self.itemCoding, self)
			return
		
		if self.libaoType == EnumSuper:
			ItemUserClass.LiBao_Super(self.itemCoding, self)
			return

def LoadLiBaoConfig():
	#装备价格
	for lb in LiBaoConfig.ToClassType():
		LiBaoConfig_Dict[lb.itemCoding] = lb
		lb.Preprocess()


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadLiBaoConfig()


