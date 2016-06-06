#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Shop.GSMall")
#===============================================================================
# GS返利商城
#===============================================================================
import DynamicPath
import Environment
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Shop import Trade
from Game.Role.Data import EnumObj, EnumTempObj, EnumInt1


if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("Shop")
	
	GSMallConfig_Dict = {}
	
class GSMall(Trade.ShopBase):
	FilePath = FILE_FOLDER_PATH.FilePath("GSMall.txt")
	def __init__(self):
		self.tradeId = int						#名字必须这样
		self.goodsId = int						#物品coding,宠物类型，翅膀类型，英雄编号
		self.goodsType = int					#1-普通物品,2-宠物,3-翅膀,4-英雄,5-系统神石,6-魔晶
		self.goodsName = str					#商品名字
		self.dayLimitCnt = int					#每日限购
		self.limitCnt = int						#永久限购
		self.rebateCoding = int					#返利道具coding
		self.needCnt = int						#需要返利道具个数
		
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
		elif self.goodsType == 5:
			self.per_trade_fun = self.CanBuyUnbindRMB_S
			self.add_fun = self.IncUnbindRMB_S
		elif self.goodsType == 6:
			self.per_trade_fun = self.CanBuyBindRMB
			self.add_fun = self.IncBindRMB
	
	def do_trade(self, role, cnt):
		with TraGSMallTrade:
			self._do_trade(role, cnt)
			AutoLog.LogBase(role.GetRoleID(), AutoLog.eveGSTrade, (self.goodsName, self.tradeId, cnt))
	
	def _do_trade(self, role, cnt):
		#交易主体
		if self.per_trade_fun is None or self.add_fun is None:
			print "GE_EXC, error in mall do_trade not per_trade_fun, or add_fun"
			return
		
		print self.dayLimitCnt, self.limitCnt
		
		if self.dayLimitCnt:
			limitDayDict = role.GetObj(EnumObj.GSMall_Limit_Dict).get(1, {})
			if self.dayLimitCnt < limitDayDict.get(self.tradeId, 0) + cnt:
				return
		
		#限购
		if self.limitCnt:
			limitDict = role.GetObj(EnumObj.GSMall_Limit_Dict).get(2, {})
			if self.limitCnt < limitDict.get(self.tradeId, 0) + cnt:
				return
		
		#货物分类判断是否可以购买
		if not self.per_trade_fun(role, cnt):
			return
		
		needCnt = self.needCnt * cnt
		if (not self.needCnt) or (not self.rebateCoding) or (role.ItemCnt(self.rebateCoding) < needCnt):
			return
		
		if not role.GetI1(EnumInt1.IsActGSMall):
			role.SetI1(EnumInt1.IsActGSMall, True)
		
		role.DelItem(self.rebateCoding, needCnt)
		
		#增加限购数量
		if self.limitCnt:
			limitDayDict = role.GetObj(EnumObj.GSMall_Limit_Dict).get(2, {})
			limitDict[self.tradeId] = limitDict.get(self.tradeId, 0) + cnt
			role.SendObj(GSMall_LimitData, role.GetObj(EnumObj.GSMall_Limit_Dict))
		
		if self.dayLimitCnt:
			limitDict = role.GetObj(EnumObj.GSMall_Limit_Dict).get(1, {})
			limitDayDict[self.tradeId] = limitDayDict.get(self.tradeId, 0) + cnt
			role.SendObj(GSMall_LimitData, role.GetObj(EnumObj.GSMall_Limit_Dict))
		
		self.RewardRole(role, cnt)
	
	def RewardRole(self, role, cnt):
		#获得货物
		self.add_fun(role, cnt)
		
		role.Msg(2, 0, GlobalPrompt.MallBuyOk)
		
	def CanBuyItem(self, role, cnt):
		return True

	def CanBuyHero(self, role, cnt):
		return not role.GetTempObj(EnumTempObj.enHeroMgr).IsHeroFull()
	
	def CanBuyPet(self, role, cnt):
		return True
	
	def CanBuyWing(self, role, cnt):
		return True
	
	def CanBuyUnbindRMB_S(self, role, cnt):
		return True
	
	def CanBuyBindRMB(self, role, cnt):
		return True
	
	def AddItem(self, role, cnt):
		role.AddItem(self.goodsId, cnt)
	
	def AddPet(self, role, cnt):
		for _ in range(cnt):
			role.AddPet(self.goodsId)
	
	def AddHero(self, role, cnt):
		for _ in range(cnt):
			role.AddHero(self.goodsId)
	
	def IncUnbindRMB_S(self, role, cnt):
		role.IncUnbindRMB_S(self.goodsId * cnt)
	
	def IncBindRMB(self, role, cnt):
		role.IncBindRMB(self.goodsId * cnt)

def RoleDayClear(role, param):
	#清理每日限购
	role.GetObj(EnumObj.GSMall_Limit_Dict)[1] = {}
	role.SendObj(GSMall_LimitData, role.GetObj(EnumObj.GSMall_Limit_Dict))

def AfterLogin(role, param):
	if not role.GetObj(EnumObj.GSMall_Limit_Dict):
		role.SetObj(EnumObj.GSMall_Limit_Dict, {1:{}, 2:{}})
	
def SyncRoleOtherData(role, param):
	role.SendObj(GSMall_LimitData, role.GetObj(EnumObj.GSMall_Limit_Dict))

if "_HasLoad" not in dir():
	if not Environment.IsCross:
		GSMall.reg()
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		
	TraGSMallTrade = AutoLog.AutoTransaction("TraGSMallTrade", "GS商城购物")
	
	GSMall_LimitData = AutoMessage.AllotMessage("GSMall_LimitData", "同步限购数据")

