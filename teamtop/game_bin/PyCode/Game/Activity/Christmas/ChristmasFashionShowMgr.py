#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.Christmas.ChristmasFashionShowMgr")
#===============================================================================
# 圣诞时装秀Mgr
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role.Mail import Mail
from Game.Role import Event, Call, KuaFu
from Game.Role.Data import EnumObj, EnumInt32
from Game.Activity import CircularDefine
from Game.Activity.Christmas import ChristmasFashionShowConfig

if "_HasLoad" not in dir():
	IS_START = False
	
	Tra_ChristmasFashionShow_BuyGoods = AutoLog.AutoTransaction("Tra_ChristmasFashionShow_BuyGoods", "圣诞时装秀_购买商品")
	Tra_ChristmasFashionShow_DonateGoods = AutoLog.AutoTransaction("Tra_ChristmasFashionShow_DonateGoods", "圣诞时装秀_赠送商品")
	Tra_ChristmasFashionShow_BeDonateGoods = AutoLog.AutoTransaction("Tra_ChristmasFashionShow_BeDonateGoods", "圣诞时装秀_被赠送商品")
	
	ChristmasFashionShow_BuyRecord_S = AutoMessage.AllotMessage("ChristmasFashionShow_BuyRecord_S", "圣诞时装秀_购买记录同步")

#### 活动控制  start ####
def OnStartFashionShow(*param):
	'''
	开启活动
	'''
	_, circularType = param
	if CircularDefine.CA_ChristmasFashionShow != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open FashionShow"
		return
		
	IS_START = True

def OnEndFashionShow(*param):
	'''
	结束活动
	'''
	_, circularType = param
	if CircularDefine.CA_ChristmasFashionShow != circularType:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC, end FashionShow while not start"
		return
		
	IS_START = False

def OnOpenPanel(role, msg = None):
	'''
	圣诞时装秀_请求打开面板
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.ChristmasFashionShow_NeedLevel:
		return
	
	buyRecordDict = role.GetObj(EnumObj.ChristmasActive)[3]
	role.SendObj(ChristmasFashionShow_BuyRecord_S, buyRecordDict)
	
def OnBuyGoods(role, msg):
	'''
	圣诞时装秀_请求购买商品
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.ChristmasFashionShow_NeedLevel:
		return
	
	#目标商品是否存在
	targetGoodId, buyCnt = msg
	targetGoodCfg = ChristmasFashionShowConfig.ChristmasFashionShow_GoodsConfig_Dict.get(targetGoodId)
	if not targetGoodCfg or buyCnt < 1:
		return
	
	
	#神石不足
	needUnbindRMB = targetGoodCfg.needUnbindRMB * buyCnt
	if role.GetUnbindRMB() < needUnbindRMB:
		return
	
	#剩余限购数量不足
	buyRecordDict = role.GetObj(EnumObj.ChristmasActive)[3]
	boughtCnt = buyRecordDict.get(targetGoodId, 0)
	if boughtCnt + buyCnt > targetGoodCfg.limitCnt:
		print "GE_EXC,ChristmasFashionShow::boughtCnt + buyCnt > targetGoodCfg.limitCnt"
		return
	
	coding, cnt = targetGoodCfg.item
	cnt *= buyCnt
	with Tra_ChristmasFashionShow_BuyGoods:
		#扣钱
		role.DecUnbindRMB(needUnbindRMB)
		#加积分
		role.IncI32(EnumInt32.ChristmasConsumeExp, needUnbindRMB)
		#写购买记录
		buyRecordDict[targetGoodId] = boughtCnt + buyCnt
		role.GetObj(EnumObj.ChristmasActive)[3] = buyRecordDict
		#获得
		role.AddItem(coding, cnt)
	
	buyRecordDict = role.GetObj(EnumObj.ChristmasActive)[3]
	role.SendObj(ChristmasFashionShow_BuyRecord_S, buyRecordDict)
	
	prompt = GlobalPrompt.ChristmasFashionShow_Tips_Head + GlobalPrompt.ChristmasFashionShow_Tips_Item % (coding, cnt)
	role.Msg(2, 0, prompt)
	
	#积分提示
	if needUnbindRMB > 0:
		role.Msg(2, 0, GlobalPrompt.Christmas_Tips_ConsumeEXp % needUnbindRMB)

def OnDonateGoods(role, msg):
	'''
	圣诞时装秀_请求赠送商品
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.ChristmasFashionShow_NeedLevel:
		return
	
	targetRoleId, targetGoodId, donateCnt = msg
	targetGoodCfg = ChristmasFashionShowConfig.ChristmasFashionShow_GoodsConfig_Dict.get(targetGoodId)
	if not targetGoodCfg or donateCnt < 1:
		return
	
	# 自己送自己限制
	roleId = role.GetRoleID()
	if targetRoleId == roleId:
		return
	
	#非本服 
	if not KuaFu.IsLocalRoleByRoleID(targetRoleId):
		role.Msg(2, 0, GlobalPrompt.ChristmasFashionShow_Tips_NotLocalServer)
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
	rebatePrompt = GlobalPrompt.ChristmasFashionShow_DonateTips_Head + GlobalPrompt.ChristmasFashionShow_Tips_Item % (rebateCoding, rebateCnt)
	#赠送邮件内容
	with Tra_ChristmasFashionShow_DonateGoods:
		#扣钱
		role.DecUnbindRMB(needUnbindRMB)
		#加积分
		role.IncI32(EnumInt32.ChristmasConsumeExp, needUnbindRMB)
		#获得返利
		role.AddItem(rebateCoding, rebateCnt)
		#log
		AutoLog.LogBase(roleId, AutoLog.eveChristmasFashionShowDonate, (targetRoleId, coding, cnt))
	
	roleName = role.GetRoleName()
	Call.LocalDBCall(targetRoleId, ReceiveDonate, (roleId, roleName, coding, cnt))
	
	role.Msg(2, 0, rebatePrompt)
	
	#积分提示
	if needUnbindRMB > 0:
		role.Msg(2, 0, GlobalPrompt.Christmas_Tips_ConsumeEXp % needUnbindRMB)
	
def ReceiveDonate(role, param):
	'''
	圣诞时装秀_收到赠送商品  接受赠送的Role调用
	'''
	#解析参数
	roleId = role.GetRoleID()
	giveRoleId, giveRoleName, coding, cnt = param
	#组装附件
	itemList = []
	itemList.append((coding, cnt))
	#组装内容
	content = GlobalPrompt.ChristmasFashionShowMail_Content % (giveRoleName, coding, cnt)
	#process
	with Tra_ChristmasFashionShow_BeDonateGoods:
		#log
		AutoLog.LogBase(roleId, AutoLog.eveChristmasFashionShowReceive, (giveRoleId, coding, cnt))
		#发邮件
		Mail.SendMail(roleId, GlobalPrompt.ChristmasFashionShowMail_Title, GlobalPrompt.ChristmasFashionShowMail_Sender, content, itemList)
	
	#提示
	role.Msg(2, 0, content)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartFashionShow)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndFashionShow)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChristmasFashionShow_OnOpenPanel", "圣诞时装秀_请求打开面板"), OnOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChristmasFashionShow_OnBuyGoods", "圣诞时装秀_请求购买商品"), OnBuyGoods)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChristmasFashionShow_OnDonateGoods", "圣诞时装秀_请求赠送商品"), OnDonateGoods)