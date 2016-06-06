#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ValentineDay.CouplesFashionShopMgr")
#===============================================================================
# 情侣炫酷时装 Mgr
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role.Mail import Mail
from Game.Role.Data import EnumObj
from Game.Activity import CircularDefine
from Game.Role import Event, Call, KuaFu
from Game.Activity.ValentineDay import CouplesFashionShopConfig

IDX_FASHION = 3
if "_HasLoad" not in dir():
	IS_START = False
	
	Tra_CouplesFashion_BuyGoods = AutoLog.AutoTransaction("Tra_CouplesFashion_BuyGoods", "情侣炫酷时装_购买商品")
	Tra_CouplesFashion_DonateGoods = AutoLog.AutoTransaction("Tra_CouplesFashion_DonateGoods", "情侣炫酷时装_赠送商品")
	Tra_CouplesFashion_BeDonateGoods = AutoLog.AutoTransaction("Tra_CouplesFashion_BeDonateGoods", "情侣炫酷时装_被赠送商品")
	
	CouplesFashion_BuyRecord_S = AutoMessage.AllotMessage("CouplesFashion_BuyRecord_S", "情侣炫酷时装_购买记录同步")

#### 活动控制  start ####
def OnStartCouplesFashion(*param):
	'''
	开启活动
	'''
	_, circularType = param
	if CircularDefine.CA_CouplesFashion != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open CouplesFashion"
		return
		
	IS_START = True

def OnEndCouplesFashion(*param):
	'''
	结束活动
	'''
	_, circularType = param
	if CircularDefine.CA_CouplesFashion != circularType:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC, end CouplesFashion while not start"
		return
		
	IS_START = False

def OnOpenPanel(role, msg = None):
	'''
	情侣炫酷时装_请求打开面板
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.CouplesFashion_NeedLevel:
		return
	
	buyRecordDict = role.GetObj(EnumObj.ValentineDayData)[IDX_FASHION]
	role.SendObj(CouplesFashion_BuyRecord_S, buyRecordDict)
#	print "GE_EXC,OnOpenPanel::buyRecordDict(%s)" % buyRecordDict
	
def OnBuyGoods(role, msg):
	'''
	情侣炫酷时装_请求购买商品
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.CouplesFashion_NeedLevel:
		return
	
	#目标商品是否存在
	targetGoodId, buyCnt = msg
	targetGoodCfg = CouplesFashionShopConfig.CouplesFashionShop_GoodsConfig_Dict.get(targetGoodId)
	if not targetGoodCfg or buyCnt < 1:
		return
	
	
	#神石不足
	needUnbindRMB = targetGoodCfg.needUnbindRMB * buyCnt
	if role.GetUnbindRMB() < needUnbindRMB:
		return
	
	#剩余限购数量不足
	buyRecordDict = role.GetObj(EnumObj.ValentineDayData)[IDX_FASHION]
	boughtCnt = buyRecordDict.get(targetGoodId, 0)
	if boughtCnt + buyCnt > targetGoodCfg.limitCnt:
		print "GE_EXC,CouplesFashion::boughtCnt + buyCnt > targetGoodCfg.limitCnt"
		return
	
	coding, cnt = targetGoodCfg.item
	cnt *= buyCnt
	with Tra_CouplesFashion_BuyGoods:
		#扣钱
		role.DecUnbindRMB(needUnbindRMB)
		#写购买记录
		buyRecordDict[targetGoodId] = boughtCnt + buyCnt
		role.GetObj(EnumObj.ValentineDayData)[IDX_FASHION] = buyRecordDict
		#获得
		role.AddItem(coding, cnt)
	
	#同步最新购买记录
	role.SendObj(CouplesFashion_BuyRecord_S, buyRecordDict)
#	print "GE_EXC,OnBuyGoods::buyRecordDict(%s)" % buyRecordDict
	
	#获得提示
	prompt = GlobalPrompt.CouplesFashion_Tips_Head + GlobalPrompt.CouplesFashion_Tips_Item % (coding, cnt)
	role.Msg(2, 0, prompt)

def OnDonateGoods(role, msg):
	'''
	情侣炫酷时装_请求赠送商品
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.CouplesFashion_NeedLevel:
		return
	
	targetRoleId, targetGoodId, donateCnt = msg
	targetGoodCfg = CouplesFashionShopConfig.CouplesFashionShop_GoodsConfig_Dict.get(targetGoodId)
	if not targetGoodCfg or donateCnt < 1:
		return
	
	# 自己送自己限制
	roleId = role.GetRoleID()
	if targetRoleId == roleId:
		return
	
	#非本服 
	if not KuaFu.IsLocalRoleByRoleID(targetRoleId):
		role.Msg(2, 0, GlobalPrompt.CouplesFashion_Tips_NotLocalServer)
		return
	
	needUnbindRMB = targetGoodCfg.needUnbindRMB * donateCnt
	if role.GetUnbindRMB() < needUnbindRMB:
		return
	
	#赠送的物品
	coding, cnt = targetGoodCfg.item
	cnt *= donateCnt
	#返利的物品
	rebateCoding, rebateCnt = targetGoodCfg.rebateItem
	rebateCnt *= donateCnt
	#返利提示
	rebatePrompt = GlobalPrompt.CouplesFashion_DonateTips_Head + GlobalPrompt.CouplesFashion_Tips_Item % (rebateCoding, rebateCnt)
	#赠送邮件内容
	with Tra_CouplesFashion_DonateGoods:
		#扣钱
		role.DecUnbindRMB(needUnbindRMB)
		#获得返利
		role.AddItem(rebateCoding, rebateCnt)
		#log
		AutoLog.LogBase(roleId, AutoLog.eveCouplesFashionDonate, (targetRoleId, coding, cnt))
	
	roleName = role.GetRoleName()
	Call.LocalDBCall(targetRoleId, ReceiveDonate, (roleId, roleName, coding, cnt))
	
	#赠送成功 获得返利提示
	role.Msg(2, 0, rebatePrompt)
	
def ReceiveDonate(role, param):
	'''
	情侣炫酷时装_收到赠送商品  接受赠送的Role调用
	'''
	#解析参数
	roleId = role.GetRoleID()
	giveRoleId, giveRoleName, coding, cnt = param
	#组装附件
	itemList = []
	itemList.append((coding, cnt))
	#组装内容
	content = GlobalPrompt.CouplesFashion_Mail_Content % (giveRoleName, coding, cnt)
	#process
	with Tra_CouplesFashion_BeDonateGoods:
		#log
		AutoLog.LogBase(roleId, AutoLog.eveCouplesFashionReceive, (giveRoleId, coding, cnt))
		#发邮件
		Mail.SendMail(roleId, GlobalPrompt.CouplesFashion_Mail_Title, GlobalPrompt.CouplesFashion_Mail_Sender, content, itemList)
	
	#提示
	role.Msg(2, 0, content)
	
def OnRoleInit(role, param):
	'''
	初始角色相关Obj的key
	'''
	valentineDayData = role.GetObj(EnumObj.ValentineDayData)
	if IDX_FASHION not in valentineDayData:
		valentineDayData[IDX_FASHION] = {}

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_InitRolePyObj, OnRoleInit)
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartCouplesFashion)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndCouplesFashion)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CouplesFashion_OnOpenPanel", "情侣炫酷时装_请求打开面板"), OnOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CouplesFashion_OnBuyGoods", "情侣炫酷时装_请求购买商品"), OnBuyGoods)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CouplesFashion_OnDonateGoods", "情侣炫酷时装_请求赠送商品"), OnDonateGoods)