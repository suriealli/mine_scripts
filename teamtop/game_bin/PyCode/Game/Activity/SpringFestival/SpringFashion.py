#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.SpringFestival.SpringFashion")
#===============================================================================
# 靓丽时装秀
#===============================================================================
import Environment
import cRoleMgr
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event, KuaFu
from Game.SysData import WorldData
from Game.Role.Mail import Mail
from Game.Role.Data import EnumObj
from Game.Activity import CircularDefine
from Game.Activity.SpringFestival import SpringFestivalConfig

if "_HasLoad" not in dir():
	IS_START = False	#活动开关
	
	SpringFashionData = AutoMessage.AllotMessage("SpringFashionData", "春节时装秀兑换数据")
	#日志
	SpringFashion_Log = AutoLog.AutoTransaction("SpringFashion_Log", "春节时装秀兑换日志")
	SpringFashionSend_Log = AutoLog.AutoTransaction("SpringFashionSend_Log", "春节时装秀赠送日志")
#==================活动开关====================
def OpenSpringFashion(param1, param2):
	if param2 != CircularDefine.CA_SpringFashion:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC, NewYearShop is already open"
		return
	
	IS_START = True

def CloseSpringFashion(param1, param2):
	if param2 != CircularDefine.CA_SpringFashion:
		return
	
	global IS_START
	if not IS_START:
		print "GE_EXC, NewYearShop is already close"
		return
	
	IS_START = False
	
	
def RequestExchange(role, msg):
	'''
	请求新年兑不停兑换
	@param role:
	@param msg:
	'''
	global IS_START
	if not IS_START:
		return
	
	#等级判断
	if role.GetLevel() < EnumGameConfig.Spring_Festival_NeedLevel:
		return
	
	coding, cnt = msg
	cfg = SpringFestivalConfig.SPRING_SHOP_DICT.get(coding)
	if not cfg:
		print "GE_EXC, NEW YEAR shop can not find coding (%s) in NewYearShop_Dict" % coding
		return
	
	#角色等级不足
	if role.GetLevel() < cfg.needLevel:
		return
	
	#世界等级不足
	if WorldData.GetWorldLevel() < cfg.needWorldLevel:
		return
	
	if not cnt: return
	
	#兑换需要物品不够
	needCnt = cfg.needItemCnt * cnt
	if role.ItemCnt(cfg.needCoding) < needCnt:
		return
	
	if cfg.limitCnt:
		if cnt > cfg.limitCnt:
			#购买个数超过限购
			return
		elShopObj = role.GetObj(EnumObj.SpringFestivalData).get(8)
		if not elShopObj:
			elShopObj = {}
		if coding not in elShopObj:
			elShopObj[coding] = cnt
		elif elShopObj[coding] + cnt > cfg.limitCnt:
			#超过限购
			return
		else:
			elShopObj[coding] += cnt
		role.GetObj(EnumObj.SpringFestivalData)[8] = elShopObj
		#限购的记录购买数量
		role.SendObj(SpringFashionData, elShopObj)
	
	with SpringFashion_Log:
		#发放兑换物品
		role.DelItem(cfg.needCoding, needCnt)
		role.AddItem(coding, cnt)
	role.Msg(2, 0, GlobalPrompt.Reward_Tips + GlobalPrompt.Item_Tips % (coding, cnt))
	
def RequestOpenShop(role, param):
	'''
	请求打开新年兑不停商店
	@param role:
	@param param:
	'''
	global IS_START
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.Spring_Festival_NeedLevel:
		return
	
	role.SendObj(SpringFashionData, role.GetObj(EnumObj.SpringFestivalData).get(8))
	
def OnDonateGoods(role, param):
	'''
	春节靓丽时装秀赠送商品
	@param role:
	@param msg:
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.Spring_Festival_NeedLevel:
		return
	
	targetRoleId, targetCoding, donateCnt = param
	if not targetCoding or donateCnt < 1:
		return
	
	targetGoodCfg = SpringFestivalConfig.SPRING_SHOP_DICT.get(targetCoding)
	
	if not targetGoodCfg.isSend:#不能赠送的道具
		return
	# 自己送自己限制
	roleId = role.GetRoleID()
	if targetRoleId == roleId:
		return
	
	#非本服 
	if not KuaFu.IsLocalRoleByRoleID(targetRoleId):
		role.Msg(2, 0, GlobalPrompt.ChristmasFashionShow_Tips_NotLocalServer)
		return
	
	if role.ItemCnt(targetGoodCfg.needCoding) < targetGoodCfg.needItemCnt * donateCnt:
		return
	
	if targetGoodCfg.limitCnt:
		if donateCnt > targetGoodCfg.limitCnt:
			#购买个数超过限购
			return
		elShopObj = role.GetObj(EnumObj.SpringFestivalData).get(8)
		if not elShopObj:
			elShopObj = {}
		if targetCoding not in elShopObj:
			elShopObj[targetCoding] = donateCnt
		elif elShopObj[targetCoding] + donateCnt > targetGoodCfg.limitCnt:
			#超过限购
			return
		else:
			elShopObj[targetCoding] += donateCnt
		role.GetObj(EnumObj.SpringFestivalData)[8] = elShopObj
		#限购的记录购买数量
		role.SendObj(SpringFashionData, elShopObj)
		
	#赠送邮件内容
	with SpringFashionSend_Log:
		#口道具
		role.DelItem(targetGoodCfg.needCoding, targetGoodCfg.needItemCnt * donateCnt)
		
		Mail.SendMail(targetRoleId, GlobalPrompt.SpringFashion_Title, role.GetRoleName(), GlobalPrompt.SpringFashion_Contend, items = [(targetCoding, donateCnt)])
		
		role.Msg(2, 0, GlobalPrompt.Card_Give)
		role.SendObj(SpringFashionData, role.GetObj(EnumObj.SpringFestivalData).get(8))
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_StartCircularActive, OpenSpringFashion)
		Event.RegEvent(Event.Eve_EndCircularActive, CloseSpringFashion)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("SpringFashion_Exchange", "请求春节靓丽时装秀兑换"), RequestExchange)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("SpringFashion_Open", "请求打开春节靓丽时装秀商店"), RequestOpenShop)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("SpringFashion_OnDonateGoods", "春节靓丽时装秀赠送商品"), OnDonateGoods)
		