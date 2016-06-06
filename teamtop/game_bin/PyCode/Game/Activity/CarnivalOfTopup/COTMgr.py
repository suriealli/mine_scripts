#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.CarnivalOfTopup.COTMgr")
#===============================================================================
# 狂欢充值
#===============================================================================
import cRoleMgr
import Environment
from ComplexServer.Log import AutoLog
from Common.Other import GlobalPrompt, EnumGameConfig
from Common.Message import AutoMessage
from Game.Role import Event
from Game.Persistence import Contain
from Game.Activity import CircularDefine, CircularActive
from Game.Activity.CarnivalOfTopup import COTConfig

if "_HasLoad" not in dir():

	__COTSTART  = False
	COTActiveID = 0
	TREASURECHEST_CODE = 26222 #宝箱编码

	#日志
	Tra_CarnivalOfTopup_OpenTreasureChest = AutoLog.AutoTransaction("Tra_CarnivalOfTopup_OpenTreasureChest", "玩家在充值狂欢活动中打开宝箱")
#========================接口================================
def COTStart(*param):
	'''
	狂欢充值活动开启
	'''
	_, activetype = param
	if activetype != CircularDefine.CA_CarnivalOfTopup:
		return
	global __COTSTART
	if __COTSTART:
		print "GE_EXC, CarnivalOfTopup is already started "
		return
	__COTSTART = True
	
	global COTActiveID
	if COTActiveID:
		print 'GE_EXC, COTActiveID is already have'
	isActiveTypeRepeat = False
	for activeId, (activeType, _) in CircularActive.CircularActiveCache_Dict.iteritems():
		if activeType != activetype:
			continue
		#同一个active_type只允许同时出现一个
		if isActiveTypeRepeat:
			print 'GE_EXC, repeat isActiveTypeRepeat in CircularActiveCache_Dict'
		COTActiveID = activeId
		isActiveTypeRepeat = True
	
def COTEnd(*param):
	'''
	狂欢充值活动关闭
	'''
	_, activetype = param
	if activetype != CircularDefine.CA_CarnivalOfTopup:
		return
	global __COTSTART
	if not __COTSTART:
		print "GE_EXC, CarnivalOfTopup is already ended "
		return
	__COTSTART = False
	#清空奖励数据
	global AWARDDATA_DICT
	AWARDDATA_DICT.clear()
	
	global AWARDLIMIT_LIST
	AWARDLIMIT_LIST.data = []
	AWARDLIMIT_LIST.HasChange()
	
	global COTActiveID
	if not COTActiveID:
		print 'GE_EXC, SeaActiveID is already zero'
	COTActiveID = 0
	
def ChangeCirActID(param1, param2):
	#改变活动ID
	circularType, circularId = param2
	
	if circularType != CircularDefine.CA_CarnivalOfTopup:
		return
	
	global COTActiveID
	COTActiveID = circularId
#=====================接口===================================


def RequestOpenTreasureChest(role, msg):
	'''
	开启宝箱
	'''
	#如果活动没有开启
	if not __COTSTART:
		return
	#如果玩家等级不符合要求
	if role.GetLevel() < EnumGameConfig.COT_Level_Needed:
		return
	#如果玩家宝箱数量不符合要求
	if role.ItemCnt(TREASURECHEST_CODE) < 1:
		return
	#如果玩家的背包或者命魂背包已满，提示并返回
	if role.TarotPackageIsFull() or role.PackageIsFull():
		role.Msg(2, 0, GlobalPrompt.TarotPackageOrlPackageIsFull)
		return
	#如果天赋卡背包已满，提示并返回
	if role.GetTalentEmptySize() < 1:
		role.Msg(2, 0, GlobalPrompt.TalentCardPackageIsFull)
		return
	#对AWARDDATA_DICT中的awardid进行判断,如果已经超出限定的数量，则不再发放该种奖励。被限制的awardid保存在限制列表中
	global AWARDDATA_DICT
	global AWARDLIMIT_LIST
	
	#获取一个随机奖励id，limitlist为限制列表
	randomawardid = COTConfig.GetRandomOne(COTActiveID, AWARDLIMIT_LIST.data)
	
	#如果没有获取到随机id，则打印异常
	if not randomawardid:
		print "GE_EXC, may not get random award id for role(%s) in CarnivalOfTopup, possibly leaded by a config error" % role.GetRoleID()
		return
	#根据奖励id获取奖励配置
	awardcfg = COTConfig.COTConfigDict.get((COTActiveID, randomawardid))
	#如果没有获取到奖励配置，则打印异常
	if not awardcfg:
		print "GE_EXC,  may not get award config for role(%s) in CarnivalOfTopup, possibly leaded by a config error" % role.GetRoleID()
		return

	itemsmsg = ""
	tarotmsg = ""
	talentmsg = ""
	globalitemmsg = ""
	globaltarotmsg = ""
	globaltalencardmsg = ""
	isglobalPost = False
	with Tra_CarnivalOfTopup_OpenTreasureChest:
		#扣除玩家宝箱数量
		role.DelItem(TREASURECHEST_CODE,1)
		#奖励物品
		if awardcfg.awarditems:
			#消点
			role_AddItem = role.AddItem
			for item in  awardcfg.awarditems:
				role_AddItem(*item)
				itemsmsg = itemsmsg + GlobalPrompt.Item_Tips % item
				if list(item)[0] in EnumGameConfig.COT_GlobalItemList:
					globalitemmsg = globalitemmsg + GlobalPrompt.CarnivalOfTopup_Item_Tips % item
					isglobalPost = True
					
		#奖励命魂
		if awardcfg.addTarot:
			role_AddTarotCard = role.AddTarotCard
			for Tarot in awardcfg.addTarot:
				role_AddTarotCard(*Tarot)
				tarotmsg = tarotmsg + GlobalPrompt.Tarot_Tips % Tarot
				if list(Tarot)[0] in EnumGameConfig.COT_GlobalTarotList:
					globaltarotmsg = globaltarotmsg + GlobalPrompt.CarnivalOfTopup_Tarot_Tips % Tarot
					isglobalPost = True
		
		#奖励天赋卡
		if awardcfg.talentcard:
			role.AddTalentCard(awardcfg.talentcard)
			talentmsg = talentmsg + GlobalPrompt.Talent_Tips % (awardcfg.talentcard, 1)
			if awardcfg.talentcard in EnumGameConfig.COT_GlobalTalentList:
				globaltalencardmsg = globaltalencardmsg + GlobalPrompt.CarnivalOfTopup_Talent_Tips % (awardcfg.talentcard, 1)
				isglobalPost = True

	#更新奖励数据
	AWARDDATA_DICT[randomawardid] = AWARDDATA_DICT.get(randomawardid, 0) + 1

	#更新限制列表
	if not randomawardid in AWARDLIMIT_LIST:
		#如果该奖励id有限制
		if COTConfig.COTItemLimitDict.get(randomawardid):
			#如果累计发放该种奖励的次数超过了限制
			if AWARDDATA_DICT[randomawardid] >= COTConfig.COTItemLimitDict[randomawardid]:
				#则该种奖励id放入限制列表中
				AWARDLIMIT_LIST.append(randomawardid)
			
	#发放奖励提示
	role.Msg(2, 0, GlobalPrompt.CarnivalOfTopup_Awrad_Msg + itemsmsg + tarotmsg + talentmsg)
	if isglobalPost:
		cRoleMgr.Msg(1, 0, GlobalPrompt.CarnivalOfTopup_Award_GlobalMsg_1 % role.GetRoleName() + globalitemmsg + globaltarotmsg + globaltalencardmsg + GlobalPrompt.CarnivalOfTopup_Award_GlobalMsg_2)

if "_HasLoad" not in dir():
	if Environment.HasLogic or Environment.HasWeb:
		AWARDDATA_DICT = Contain.Dict("AWARDDATA_DICT", (2038, 1, 1), None, None, isSaveBig=False)#记录某中奖励发放的次数
		AWARDLIMIT_LIST = Contain.List("AWARDLIMIT_LIST", (2038, 1, 1), None, None, isSaveBig=False)#物品限制列表，在该列表中的物品不能作为奖品
	
	if Environment.HasLogic and not Environment.IsCross:
		#事件
		Event.RegEvent(Event.Eve_StartCircularActive, COTStart)
		Event.RegEvent(Event.Eve_EndCircularActive, COTEnd)
		Event.RegEvent(Event.Eve_ChangeCirActID, ChangeCirActID)
		
		#客户端请求
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestOpenTreasureChest", "客户端请求打开狂欢充值宝箱"), RequestOpenTreasureChest)
	

