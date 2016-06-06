#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.WangZheGongCe.WangZheFashionShowMgr")
#===============================================================================
# 最炫时装秀 Mgr
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
from Game.Activity.WangZheGongCe import WangZheFashionShowConfig

IDX_FASHIONSHOW = 3

if "_HasLoad" not in dir():
	IS_START = False
	
	#格式 ｛goodId:boughtCnt,｝
	WangZheFashionShow_BuyRecord_S = AutoMessage.AllotMessage("WangZheFashionShow_BuyRecord_S", "最炫时装秀_购买记录同步")
	
	Tra_WangZheFashionShow_BuyGoods = AutoLog.AutoTransaction("Tra_WangZheFashionShow_BuyGoods", "最炫时装秀_购买商品")
	Tra_WangZheFashionShow_DonateGoods = AutoLog.AutoTransaction("Tra_WangZheFashionShow_DonateGoods", "最炫时装秀_赠送商品")
	Tra_WangZheFashionShow_BeDonateGoods = AutoLog.AutoTransaction("Tra_WangZheFashionShow_BeDonateGoods", "最炫时装秀_被赠送商品")

#### 活动控制  start ####
def OnStartWangZheFashionShow(*param):
	'''
	开启活动
	'''
	_, circularType = param
	if CircularDefine.CA_WangZheFashionShow != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open WangZheFashionShow"
		return
		
	IS_START = True

def OnEndWangZheFashionShow(*param):
	'''
	结束活动
	'''
	_, circularType = param
	if CircularDefine.CA_WangZheFashionShow != circularType:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC, end WangZheFashionShow while not start"
		return
		
	IS_START = False
	
def OnBuyGoods(role, msg):
	'''
	最炫时装秀_请求购买商品
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.WangZheGongCe_NeedLevel:
		return
	
	#目标商品是否存在
	targetGoodId, buyCnt = msg
	targetGoodCfg = WangZheFashionShowConfig.WangZheFashionShow_GoodsConfig_Dict.get(targetGoodId)
	if not targetGoodCfg or buyCnt < 1:
		return
	
	#神石不足
	needUnbindRMB = targetGoodCfg.needUnbindRMB * buyCnt
	if role.GetUnbindRMB() < needUnbindRMB:
		return
	
	#剩余限购数量不足
	buyRecordDict = role.GetObj(EnumObj.WangZheGongCe)[IDX_FASHIONSHOW]
	boughtCnt = buyRecordDict.get(targetGoodId, 0)
	if boughtCnt + buyCnt > targetGoodCfg.limitCnt:
		return
	
	coding, cnt = targetGoodCfg.item
	cnt *= buyCnt
	with Tra_WangZheFashionShow_BuyGoods:
		#扣钱
		role.DecUnbindRMB(needUnbindRMB)
		#写购买记录
		buyRecordDict[targetGoodId] = boughtCnt + buyCnt
		#获得
		role.AddItem(coding, cnt)
	
	#获得提示
	prompt = GlobalPrompt.WZFS_Tips_Head + GlobalPrompt.Item_Tips % (coding, cnt)
	role.Msg(2, 0, prompt)
	#同步最新购买记录
	role.SendObj(WangZheFashionShow_BuyRecord_S, buyRecordDict)

def OnDonateGoods(role, msg):
	'''
	最炫时装秀_请求赠送商品
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.WangZheGongCe_NeedLevel:
		return
	
	targetRoleId, targetGoodId, donateCnt = msg
	targetGoodCfg = WangZheFashionShowConfig.WangZheFashionShow_GoodsConfig_Dict.get(targetGoodId)
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
	if role.GetUnbindRMB() < needUnbindRMB:
		return
	
	#赠送的物品
	coding, cnt = targetGoodCfg.item
	cnt *= donateCnt
	#返利的物品
	rebateCoding, rebateCnt = targetGoodCfg.rebateItem
	rebateCnt *= donateCnt
	#返利提示
	rebatePrompt = GlobalPrompt.WZFS_DonateTips_Head + GlobalPrompt.Item_Tips % (rebateCoding, rebateCnt)
	#赠送邮件内容
	with Tra_WangZheFashionShow_DonateGoods:
		#扣钱
		role.DecUnbindRMB(needUnbindRMB)
		#获得返利
		role.AddItem(rebateCoding, rebateCnt)
		#log
		AutoLog.LogBase(roleId, AutoLog.eveWangZheFashionShowDonate, (targetRoleId, coding, cnt))
	
	roleName = role.GetRoleName()
	Call.LocalDBCall(targetRoleId, ReceiveDonate, (roleId, roleName, coding, cnt))
	
	role.Msg(2, 0, rebatePrompt)
	
def ReceiveDonate(role, param):
	'''
	最炫时装秀_收到赠送商品  接受赠送的Role调用
	'''
	#解析参数
	roleId = role.GetRoleID()
	giveRoleId, giveRoleName, coding, cnt = param
	#组装附件
	itemList = []
	itemList.append((coding, cnt))
	#组装内容
	content = GlobalPrompt.WangZheFashionShowMail_Content % (giveRoleName, coding, cnt)
	#process
	with Tra_WangZheFashionShow_BeDonateGoods:
		#log
		AutoLog.LogBase(roleId, AutoLog.eveWangZheFashionShowReceive, (giveRoleId, coding, cnt))
		#发邮件
		Mail.SendMail(roleId, GlobalPrompt.WangZheFashionShowMail_Title, GlobalPrompt.WangZheFashionShowMail_Sender, content, itemList)
	
	#提示
	role.Msg(2, 0, content)

def OnInitRole(role, param = None):
	'''
	初始化角色相关key
	'''
	wangZheGongCeData = role.GetObj(EnumObj.WangZheGongCe)
	if IDX_FASHIONSHOW not in wangZheGongCeData:
		wangZheGongCeData[IDX_FASHIONSHOW] = {}

def OnSyncOtherData(role, param = None):
	'''
	角色上线 同步相关数据
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.WangZheGongCe_NeedLevel:
		return
	
	role.SendObj(WangZheFashionShow_BuyRecord_S, role.GetObj(EnumObj.WangZheGongCe)[IDX_FASHIONSHOW])
	
def AfterLevelup(role, param = None):
	'''
	角色升级 解锁玩法
	'''
	if not IS_START:
		return
	
	if role.GetLevel() != EnumGameConfig.WangZheGongCe_NeedLevel:
		return
	
	role.SendObj(WangZheFashionShow_BuyRecord_S, role.GetObj(EnumObj.WangZheGongCe)[IDX_FASHIONSHOW])

if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.IsDevelop or Environment.EnvIsQQ() or Environment.EnvIsFT() or Environment.EnvIsTK() or Environment.EnvIsRU()):
		Event.RegEvent(Event.Eve_InitRolePyObj, OnInitRole)
	
	if Environment.HasLogic and not Environment.IsCross and (Environment.IsDevelop or Environment.EnvIsQQ() or Environment.EnvIsFT() or Environment.EnvIsTK() or Environment.EnvIsRU()):
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartWangZheFashionShow)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndWangZheFashionShow)
		
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncOtherData)
		Event.RegEvent(Event.Eve_AfterLevelUp, AfterLevelup)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WangZheFashionShow_OnBuyGoods", "最炫时装秀_请求购买商品"), OnBuyGoods)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WangZheFashionShow_OnDonateGoods", "最炫时装秀_请求赠送商品"), OnDonateGoods)
