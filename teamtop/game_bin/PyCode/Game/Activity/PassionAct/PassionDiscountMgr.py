#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionDiscountMgr")
#===============================================================================
# 特惠商品 Mgr
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role.Mail import Mail
from Game.Role.Data import EnumObj
from Game.Role import Event, Call, KuaFu
from Game.Activity import CircularDefine
from Game.Activity.PassionAct import PassionDiscountConfig, PassionDefine


if "_HasLoad" not in dir():
	IS_START = False
	
	#格式 ｛goodId:boughtCnt,｝
	PassionDiscount_BuyRecord_S = AutoMessage.AllotMessage("PassionDiscount_BuyRecord_S", "特惠商品_购买记录同步")
	
	Tra_PassionDiscount_BuyGoods = AutoLog.AutoTransaction("Tra_PassionDiscount_BuyGoods", "特惠商品_购买商品")
	Tra_PassionDiscount_DonateGoods = AutoLog.AutoTransaction("Tra_PassionDiscount_DonateGoods", "特惠商品_赠送商品")
	Tra_PassionDiscount_BeDonateGoods = AutoLog.AutoTransaction("Tra_PassionDiscount_BeDonateGoods", "特惠商品_被赠送商品")


#### 活动控制  start ####
def OnStartPassionDiscount(*param):
	'''
	开启活动
	'''
	_, circularType = param
	if CircularDefine.CA_PassionDiscount != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open PassionDiscount"
		return
		
	IS_START = True

def OnEndPassionDiscount(*param):
	'''
	结束活动
	'''
	_, circularType = param
	if CircularDefine.CA_PassionDiscount != circularType:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC, end PassionDiscount while not start"
		return
		
	IS_START = False
	
def OnBuyGoods(role, msg):
	'''
	特惠商品_请求购买商品
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.PassionDiscount_NeedLevel:
		return
	
	#目标商品是否存在
	targetGoodId, buyCnt = msg
	targetGoodCfg = PassionDiscountConfig.PassionDiscount_GoodsConfig_Dict.get(targetGoodId)
	if not targetGoodCfg or buyCnt < 1:
		return
	
	if role.GetLevel() < targetGoodCfg.needLevel:
		return
	
	#神石不足
	needUnbindRMB = targetGoodCfg.needUnbindRMB * buyCnt
	if role.GetUnbindRMB_Q() < needUnbindRMB:
		return
	
	#剩余限购数量不足
	if targetGoodCfg.limitCnt > 0:
		buyRecordDict = role.GetObj(EnumObj.PassionActData)[PassionDefine.PassionDiscount]
		boughtCnt = buyRecordDict.get(targetGoodId, 0)
		if boughtCnt + buyCnt > targetGoodCfg.limitCnt:
			return
	
	coding, cnt = targetGoodCfg.item
	cnt *= buyCnt
	with Tra_PassionDiscount_BuyGoods:
		#扣钱
		role.DecUnbindRMB_Q(needUnbindRMB)
		#写购买记录
		if targetGoodCfg.limitCnt > 0:
			buyRecordDict[targetGoodId] = boughtCnt + buyCnt
		#获得
		role.AddItem(coding, cnt)
	
	#获得提示
	prompt = GlobalPrompt.PassionDiscount_Tips_Head + GlobalPrompt.Item_Tips % (coding, cnt)
	role.Msg(2, 0, prompt)
	#同步最新购买记录
	role.SendObj(PassionDiscount_BuyRecord_S, buyRecordDict)

def OnDonateGoods(role, msg):
	'''
	特惠商品_请求赠送商品
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.PassionDiscount_NeedLevel:
		return
	
	targetRoleId, targetGoodId, donateCnt = msg
	targetGoodCfg = PassionDiscountConfig.PassionDiscount_GoodsConfig_Dict.get(targetGoodId)
	if not targetGoodCfg or donateCnt < 1:
		return
	
	# 自己送自己限制
	roleId = role.GetRoleID()
	if targetRoleId == roleId:
		return
	
	#非本服 
	if not KuaFu.IsLocalRoleByRoleID(targetRoleId):
		role.Msg(2, 0, GlobalPrompt.WZFS_Tips_NotLocalServer)
		return
	
	needUnbindRMB = targetGoodCfg.needUnbindRMB * donateCnt
	if role.GetUnbindRMB_Q() < needUnbindRMB:
		return
	
	#赠送的物品
	coding, cnt = targetGoodCfg.item
	cnt *= donateCnt
	#赠送邮件内容
	with Tra_PassionDiscount_DonateGoods:
		#扣钱
		role.DecUnbindRMB_Q(needUnbindRMB)
		#log
		AutoLog.LogBase(roleId, AutoLog.evePassionDiscountDonate, (targetRoleId, coding, cnt))
	
	roleName = role.GetRoleName()
	Call.LocalDBCall(targetRoleId, ReceiveDonate, (roleId, roleName, coding, cnt))
	
	#返利提示
	rebatePrompt = GlobalPrompt.PassionDiscount_DonateTips_Head
	role.Msg(2, 0, rebatePrompt)
	
def ReceiveDonate(role, param):
	'''
	特惠商品_收到赠送商品  接受赠送的Role调用
	'''
	#解析参数
	roleId = role.GetRoleID()
	giveRoleId, giveRoleName, coding, cnt = param
	#组装附件
	itemList = []
	itemList.append((coding, cnt))
	#组装内容
	content = GlobalPrompt.PassionDiscount_Mail_Content % (giveRoleName, coding, cnt)
	#process
	with Tra_PassionDiscount_BeDonateGoods:
		#log
		AutoLog.LogBase(roleId, AutoLog.evePassionDiscountReceive, (giveRoleId, coding, cnt))
		#发邮件
		Mail.SendMail(roleId, GlobalPrompt.PassionDiscount_Mail_Title, GlobalPrompt.PassionDiscount_Mail_Sender, content, itemList)
	
	#提示
	role.Msg(2, 0, content)

def OnInitRole(role, param = None):
	'''
	初始化角色相关key
	'''
	passionActData = role.GetObj(EnumObj.PassionActData)
	if PassionDefine.PassionDiscount not in passionActData:
		passionActData[PassionDefine.PassionDiscount] = {}

def OnSyncOtherData(role, param = None):
	'''
	角色上线 同步相关数据
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.PassionDiscount_NeedLevel:
		return
	
	role.SendObj(PassionDiscount_BuyRecord_S, role.GetObj(EnumObj.PassionActData)[PassionDefine.PassionDiscount])
	
def AfterLevelup(role, param = None):
	'''
	角色升级 解锁玩法
	'''
	if not IS_START:
		return
	
	if role.GetLevel() != EnumGameConfig.PassionDiscount_NeedLevel:
		return
	
	role.SendObj(PassionDiscount_BuyRecord_S, role.GetObj(EnumObj.PassionActData)[PassionDefine.PassionDiscount])

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_InitRolePyObj, OnInitRole)
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartPassionDiscount)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndPassionDiscount)
		
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncOtherData)
		Event.RegEvent(Event.Eve_AfterLevelUp, AfterLevelup)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("PassionDiscount_OnBuyGoods", "特惠商品_请求购买商品"), OnBuyGoods)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("PassionDiscount_OnDonateGoods", "特惠商品_请求赠送商品"), OnDonateGoods)
