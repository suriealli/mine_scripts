#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Item.ItemOperate")
#===============================================================================
# 物品背包相关操作
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Item import ItemConfig, HallowsForing, EquipmentForing
from Game.Pet import PetConfig
from Game.Role.Data import EnumTempObj, EnumInt8, EnumTempInt64, EnumInt1
from Game.Role.Obj import Base
from Game.TalentCard import TalentCardConfig
from Game.Fashion import FashionConfig
from Game.Mount import MountConfig
from Game.StarGirl import StarGirlConfig
from Game.Marry import MarryConfig
from Game.Activity.Title import TitleConfig
from Game.Role import Event

##########################################################################################
def OnRequestOpenPackageGrid(role, msg):
	'''
	客户端请求使用神石开背包格子
	@param role:
	@param msg:开启数量
	'''
	opencfg = ItemConfig.PackageSize_Dict.get(role.GetVIP())
	if not opencfg:
		return
	
	openTimes = role.GetI8(EnumInt8.PackageOpenTimes)
	if openTimes >= opencfg.openTimes:
		#超过次数了
		return
	
	needRMB = ItemConfig.GridOpen_Dict.get(openTimes + 1)
	if not needRMB:
		return
	
	if role.GetRMB() < needRMB:
		return
	with TraOpen_PackageGrid:
		role.DecRMB(needRMB)
		role.IncI8(EnumInt8.PackageOpenTimes, 1)
	
	#重算背包格子
	role.GetTempObj(EnumTempObj.enPackMgr).CountPackageMaxSize()


def SellItem(role, msg):
	'''
	出售物品
	@param role:
	@param msg:物品ID
	'''
	with TraSellItem:
		__SellItem(role, msg)

def __SellItem(role, msg):
	itemId, cnt = msg
	if cnt < 1 : return
	packageMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	item = role.FindPackProp(itemId)
	if not item : return
	if not item.CanSell() : return

	#如果加密锁没有解开，且物品需要加密
	if item.IsJiami():
		if role.GetI1(EnumInt1.PackageHasPasswd):
			if not role.GetTI64(EnumTempInt64.PackageIsUnlock):
				return
	
	if item.oint < cnt : return
	itemCoding = item.GetItemCoding()
	
	#判断是否可以出售的宠物之灵(出售获得宠物精华)
	psCfg = PetConfig.PET_SOUL_SALE_RETURN.get(itemCoding)
	if psCfg:
		packageMgr.DecPropCnt(item, cnt)
		prompt = GlobalPrompt.ItemSell_TIPS_5 % (itemCoding, cnt)
		for returnCoding, returnCnt in psCfg:
			role.AddItem(returnCoding, returnCnt * cnt)
			prompt += GlobalPrompt.Item_Tips % (returnCoding, returnCnt * cnt)
		#提示
		role.Msg(2, 0, prompt)
		return
	tlCfg = TalentCardConfig.TALENT_DEBRIS_DICT.get(itemCoding)
	if tlCfg:
		returnCoding, returnCnt = tlCfg
		packageMgr.DecPropCnt(item, cnt)
		role.AddItem(returnCoding, returnCnt * cnt)
		role.Msg(2, 0, GlobalPrompt.ItemSell_TIPS_4 % (itemCoding, cnt, returnCoding, returnCnt * cnt))
		return
	mountCfg = MountConfig.MOUNT_ITEM_DICT.get(itemCoding)
	if mountCfg:#出售坐骑道具
		returnCoding, returnCnt = mountCfg.backItem
		packageMgr.DecPropCnt(item, cnt)
		role.AddItem(returnCoding, returnCnt * cnt)
		role.Msg(2, 0, GlobalPrompt.ItemSell_TIPS_4 % (itemCoding, cnt, returnCoding, returnCnt * cnt))
		return
	
	titleCfg = TitleConfig.TitleItem_Dict.get(itemCoding)
	if titleCfg:#出售称号道具
		returnCoding, returnCnt = titleCfg.backItem
		packageMgr.DecPropCnt(item, cnt)
		role.AddItem(returnCoding, returnCnt * cnt)
		role.Msg(2, 0, GlobalPrompt.ItemSell_TIPS_4 % (itemCoding, cnt, returnCoding, returnCnt * cnt))
		return
		
	sgcfg = StarGirlConfig.STARGIRL_SELL_ITEMDICT.get(itemCoding)
	if sgcfg:
		packageMgr.DecPropCnt(item, cnt)
		tips = GlobalPrompt.ItemSell_TIPS_5 % (itemCoding, cnt)
		for backItemCoding, backItemCnt in sgcfg:
			role.AddItem(backItemCoding, backItemCnt * cnt)
			tips += GlobalPrompt.Item_Tips % (backItemCoding, backItemCnt * cnt)
		role.Msg(2, 0, tips)
		return
	ringCfg = MarryConfig.Ring_Dict.get(itemCoding)
	if ringCfg:
		#删除铭刻信息
		from Game.Marry import MarryMgr
		MarryMgr.DelRoleRingData(role, role.GetRoleID(), itemId)
		#返还道具
		returnCoding = ringCfg.saleBack
		returnCnt = ringCfg.salePrice
		packageMgr.DecPropCnt(item, cnt)
		role.AddItem(returnCoding, returnCnt * cnt)
		role.Msg(2, 0, GlobalPrompt.ItemSell_TIPS_4 % (itemCoding, cnt, returnCoding, returnCnt * cnt))
		return
	
	magicSpiritCfg = ItemConfig.MagicSpirit_Dict.get(itemCoding)
	if magicSpiritCfg:
		#删除魔灵
		packageMgr.DecPropCnt(item, cnt)
		#返还道具
		prompt = None
		if magicSpiritCfg.returnItem:
			prompt = GlobalPrompt.ItemSell_TIPS_5 % (itemCoding, cnt)
			for _ in xrange(cnt):
				for returnCoding, returnCnt in magicSpiritCfg.returnItem:
					role.AddItem(returnCoding, returnCnt)
					prompt += GlobalPrompt.ItemSell_TIPS_6 % (returnCoding, returnCnt)
		#返还金币		
		if magicSpiritCfg.returnMoney:
			returnMoney = magicSpiritCfg.returnMoney * cnt
			role.IncMoney(returnMoney)
			prompt += GlobalPrompt.ItemSell_TIPS_7 % returnMoney
			
		#获得提示
		if prompt:
			role.Msg(2, 0, prompt)
		return
	#######################################################################################
	#出售过期的装备洗练升星石，每个返回50个装备洗练石
	from Common.Other.EnumGameConfig import EQUIPMENT_WASH_STONE_GUOQI, EQUIPMENT_WASH_CODING_TMP
	if itemCoding == EQUIPMENT_WASH_STONE_GUOQI:
		packageMgr.DecPropCnt(item, cnt)
		role.AddItem(EQUIPMENT_WASH_CODING_TMP, item.SellPrice() * cnt)
		num = item.SellPrice() * cnt
		role.Msg(2, 0, GlobalPrompt.ItemSell_TIPS_4 % (itemCoding, cnt, EQUIPMENT_WASH_CODING_TMP, num))
		return
	#######################################################################################
	from Game.DragonTrain import DragonTrainConfig
	DE = DragonTrainConfig.DRAGON_SALE_DICT
	if itemCoding in DE:
		dragon_cfg = DE.get(itemCoding)
		if not dragon_cfg:
			return
		totalSoul = cnt * dragon_cfg.price
		if not totalSoul: return
		packageMgr.DecPropCnt(item, cnt)
		role.IncDragonSoul(totalSoul)
		role.Msg(2, 0, GlobalPrompt.DragonSoul_Tips % totalSoul)
		return
	gMoney = 0
	if item.Obj_Type == Base.Obj_Type_Item or item.Obj_Type == Base.Obj_Type_TimeItemOverlap:
		gMoney = item.SellPrice() * cnt
		#删除物品
		packageMgr.DecPropCnt(item, cnt)
		role.IncMoney(gMoney)
	elif item.Obj_Type == Base.Obj_Type_Equipment:
		strength = item.GetStrengthenLevel()
		cfg = ItemConfig.Equipment_Sell_Dict.get((item.cfg.posType, strength))
		gMoney = item.cfg.salePrice
		if cfg : gMoney += cfg.sumcost
		level = item.GetEnchantLevel()
		returnCoding, returnCnt = 0, 0
		if level:
			enchant = EquipmentForing.Equipment_Enchant_Dict.get(level)
			if enchant:
				returnCoding, returnCnt = enchant.returnItem
		#删除物品
		if not packageMgr.DelProp(itemId):
			#删除失败
			return
		#增加金钱
		role.IncMoney(gMoney)
		#增加物品
		if returnCoding and returnCnt:
			role.AddItem(returnCoding, returnCnt)
			role.Msg(2, 0, GlobalPrompt.ItemSell_TIPS_4 % (itemCoding, cnt, returnCoding, returnCnt * cnt))
	elif item.Obj_Type == Base.Obj_Type_TimeItem:
		cnt = 1
		gMoney = item.SellPrice()
		#删除物品
		packageMgr.DecPropCnt(item, 1)
		role.IncMoney(gMoney) 
	elif item.Obj_Type == Base.Obj_Type_Artifact:#神器
		strength = item.GetStrengthenLevel()
		cfg = ItemConfig.Artifact_Sell_Dict.get(strength)
		#神器淬炼返还
		CuiLianLevel = item.GetCuiLianLevel()
		CuiLianCfg = ItemConfig.Artifact_Sell_Dict.get(CuiLianLevel)
		if not cfg : return
		gMoney = item.cfg.salePrice
		#删除物品
		if not packageMgr.DelProp(itemId):
			#删除失败
			return
		
		msgTip = GlobalPrompt.ItemSell_TIPS_5 % (itemCoding, cnt)
		
		if cfg.salereturn and strength:
			role.AddItem(*cfg.salereturn)
			msgTip += GlobalPrompt.ItemSell_TIPS_8 % (cfg.salereturn[0], cfg.salereturn[1])
		else:
			role.IncMoney(gMoney)
		
		if CuiLianLevel and CuiLianCfg.CuiLianReturn:
			role.AddItem(*CuiLianCfg.CuiLianReturn)
			msgTip += GlobalPrompt.ItemSell_TIPS_8 % (CuiLianCfg.CuiLianReturn[0], CuiLianCfg.CuiLianReturn[1])
			if not (cfg.salereturn and strength):
				msgTip += GlobalPrompt.ItemSell_TIPS_7 % gMoney
		
		if strength or CuiLianLevel:
			role.Msg(2, 0, msgTip)
			return
	elif item.Obj_Type == Base.Obj_Type_Hallows:
		base_price = item.cfg.salePrice
		if not packageMgr.DelProp(itemId):
			#删除失败
			return
		tips = GlobalPrompt.ItemSell_TIPS_4 % (itemCoding, cnt, base_price[0], base_price[1])
		
		if item.GetEnchantsLevel() > 0:
			enchant_cfg = HallowsForing.HallowsEnchantDict.get(item.GetEnchantsLevel())
			if not enchant_cfg:
				print "GE_EXC, error in sell Obj_Type_Hallows not enchant_cfg (%s)" % item.GetEnchantsLevel()
				return
			if enchant_cfg.PriceItem and enchant_cfg.Price:
				role.AddItem(enchant_cfg.PriceItem, enchant_cfg.Price)
				tips = tips + "," + GlobalPrompt.Item_Tips % (enchant_cfg.PriceItem, enchant_cfg.Price)
			
		shenzaoLevel, _ = item.GetShenzaoLevelAndExp()
		
		if shenzaoLevel > 0:
			shenzao_cfg = HallowsForing.HallowShenzaoDict.get(shenzaoLevel)
			if not shenzao_cfg:
				return
			if shenzao_cfg.sellReturn:
				role.AddItem(*shenzao_cfg.sellReturn)
				tips += "," + GlobalPrompt.Item_Tips % shenzao_cfg.sellReturn
			
		role.AddItem(*base_price)
		role.Msg(2, 0, tips)
		
		
	elif item.Obj_Type == Base.Obj_Type_Fashion:#时装
		order, _ = item.GetOrderData()
		key = None
		if itemCoding in FashionConfig.SELL_CODING_SET:
			key = (itemCoding, order)
		else:
			key = (item.cfg.posType, order)
		sellCfg = FashionConfig.FASHION_SELL_DICT.get(key)
		if not sellCfg:
			print "GE_EXC,error in sell Obj_Type_Fashion, posType(%s) and order(%s)" % (item.cfg.posType, order)
			return
		if not packageMgr.DelProp(itemId):
			#删除失败
			return
		role.AddItem(*sellCfg.backItem)
		role.Msg(2, 0, GlobalPrompt.ItemSell_TIPS_4 % (itemCoding, cnt, sellCfg.backItem[0], sellCfg.backItem[1]))
	else:
		print "GE_EXC, error in sell item not this item Obj_Type (%s)" % item.Obj_Type
	if gMoney:
		role.Msg(2, 0, GlobalPrompt.ItemSell_TIPS_3 % (itemCoding, cnt, gMoney))


def AfterLogin(role, param):
	#登录检查背包是否有已经过期的可叠加物品，替换成另外一种过期物品
	with TraLoginChangeTimeOutItem:
		packageMgr = role.GetTempObj(EnumTempObj.enPackMgr)
		for item in packageMgr.objIdDict.values():
			if not item.IsDeadTime():
				continue
			if not item.cfg.canOverlap:
				continue
			#已经过期，并且是可叠加的，转换成配置的过期物品
			packageMgr.ChangeTimeOutItem(item)
	
if "_HasLoad" not in dir():
	#客户端请求消息	
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Item_Open_PackageGrid", "请求开启背包格子"), OnRequestOpenPackageGrid)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Item_SellItem", "请求出售物品"), SellItem)
	
	#日志
	TraOpen_PackageGrid = AutoLog.AutoTransaction("TraOpen_PackageGrid", "开启背包格子")
	TraSellItem = AutoLog.AutoTransaction("TraSellItem", "出售物品")
	
	TraLoginChangeTimeOutItem = AutoLog.AutoTransaction("TraLoginChangeTimeOutItem", "登录检查和处理过期的叠加物品")
	
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)


