#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.Title.Title")
#===============================================================================
# 称号功能
#===============================================================================
import random
import cRoleMgr
import cDateTime
import cComplexServer
import Environment
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Role import Call, Event
from Game.Role.Data import EnumObj
from Game.Activity.Title import TitleConfig
from Game.JT import JTConfig

#永久称号时间
TitleSec = 60 *60 *24 * 365 * 50
#暴击概率 万份比 0.25
TitleRate = 2500
#每次培养获得经验(暴击3倍)
LevelUpPerExp = 20
NeedLevel = 90
if "_HasLoad" not in dir():
	#消息
	Title_S_UpdateData = AutoMessage.AllotMessage("Title_S_UpdateData", "同步更新称号数据")
	
	#日志
	Tra_Add_Title = AutoLog.AutoTransaction("Tra_Add_Title", "获得称号")
	Tra_Del_Title = AutoLog.AutoTransaction("Tra_Del_Title", "删除称号")
	Tra_LevelUp_Title = AutoLog.AutoTransaction("Tra_LevelUp_Title", "培养升级称号")
	Tra_StarUp_Title = AutoLog.AutoTransaction("Tra_StarUp_Title", "称号升星")



################################################################################
def AddTitle(roleId, titleId):
	#发称号接口
	cfg = TitleConfig.Title_Dict.get(titleId)
	if not cfg:
		print "GE_EXC, error in AddTitle not this cfg (%s)" % titleId
		return
	if cfg.time == 0:
		#永久称号
		Call.LocalDBCall(roleId, CallAddTitle, (titleId, cDateTime.Seconds() + TitleSec))
	else:
		Call.LocalDBCall(roleId, CallAddTitle, (titleId, cDateTime.Seconds() + cfg.time))


def DeleteTitleCall(roleId, titleId):
	Call.LocalDBCall(roleId, DeleteTitle, titleId)

def CallAddTitle(role, param):
	#离线命令获得一个称号
	titleId, time = param
	seconds = cDateTime.Seconds()
	if seconds >= time:
		#这个称号已经过期了，不给他加
		return
	#先检测一下身上的称号是否已经有过期的
	CheckTitleTimeOut(role)
	with Tra_Add_Title:
		titleDict = role.GetObj(EnumObj.Title)
		titleDataDict = titleDict[1]
		olddata = titleDataDict.get(titleId)
		if not olddata:
			titleDataDict[titleId] = [time,1,0,1]
		else:
			titleDataDict[titleId] = [time, olddata[1], olddata[2], olddata[3]]
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveDelTitle, (titleId, time))
	
	
	#是否自动佩戴
	titleEqu = titleDict.get(2)
	if len(titleEqu) < 5 and titleId not in titleEqu:
		titleEqu.append(titleId)
		Event.TriggerEvent(Event.Eve_ChangeTitle, role)
	
	#更新数据
	role.SendObj(Title_S_UpdateData, titleDict)
	#重算属性
	role.ResetTitleProperty()
	
def CheckTitleTimeOut(role):
	#检测过期的称号
	titleDict = role.GetObj(EnumObj.Title)
	if not titleDict:
		return
	titleDataDict = titleDict.get(1)
	if not titleDataDict:
		return
	titleEqu = titleDict.get(2)
	
	isChange = False
	isChangeEqu = False
	nowSec = cDateTime.Seconds()
	with Tra_Del_Title:
		for titleId, titledata in titleDataDict.items():
			if nowSec >= titledata[0]:
				del titleDataDict[titleId]
				if titleId in titleEqu:
					titleEqu.remove(titleId)
					isChangeEqu = True
				isChange = True
				AutoLog.LogBase(role.GetRoleID(), AutoLog.eveDelTitle, (titleId, titledata[0]))
	if isChange is False:
		return
	role.SendObj(Title_S_UpdateData, titleDict)
	if isChangeEqu is True:
		Event.TriggerEvent(Event.Eve_ChangeTitle, role)
	#重算属性
	role.ResetTitleProperty()

def DeleteJTeamTitleCall(roleId):
	#删除所有的战队相关称号
	Call.LocalDBCall(roleId, DeleteJTeamTitle, None)

def DeleteJTeamTitle(role, param):
	#删除所有的战队相关称号
	titleDict = role.GetObj(EnumObj.Title)
	if not titleDict:
		return
	titleDataDict = titleDict.get(1)
	if not titleDataDict:
		return
	for titleId in titleDataDict.keys():
		if titleId in JTConfig.JTGradeTitleSet:
			DeleteTitle(role, titleId)

def DeleteTitle(role, titleId):
	#手动删除一个称号
	titleDict = role.GetObj(EnumObj.Title)
	if not titleDict:
		return
	titleDataDict = titleDict.get(1)
	if not titleDataDict:
		return
	if titleId not in titleDataDict:
		return
	with Tra_Del_Title:
		del titleDataDict[titleId]
		titleEqu = titleDict.get(2)
		if titleId in titleEqu:
			titleEqu.remove(titleId)
			Event.TriggerEvent(Event.Eve_ChangeTitle, role)
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveDelTitle, (titleId, 0))
	role.SendObj(Title_S_UpdateData, titleDict)
	#重算属性
	role.ResetTitleProperty()

def CallPerHour():
	for role in cRoleMgr.GetAllRole():
		CheckTitleTimeOut(role)

def AfterLogin(role, param):
	#登录检测称号
	CheckTitleTimeOut(role)

def BeforeSaveRole(role, param):
	#保存之前检测一下称号
	CheckTitleTimeOut(role)

def SyncRoleTitleData(role, param = None):
	#同步数据
	role.SendObj(Title_S_UpdateData, role.GetObj(EnumObj.Title))




################################################################################

def RequestTitleLevelUp(role, msg):
	'''
	请求称号培养升级 1普通， 10 高级
	@param role:
	@param msg:
	'''
	backId, (titleId, levelUpType) = msg
	if levelUpType not in (1, 10):
		return
	if role.GetLevel() < NeedLevel:
		return
	titleDict = role.GetObj(EnumObj.Title)
	titleDataDict = titleDict.get(1)
	if not titleDataDict:
		return
	
	titledata = titleDataDict.get(titleId)
	if not titledata:
		return
	
	titleCfg = TitleConfig.Title_Dict.get(titleId)
	if not titleCfg or not titleCfg.canLevelUp:
		return
	nowLevel = titledata[1]
	nowKey = (titleId, nowLevel)
	nowLevelCfg = TitleConfig.TitleLevel_Dict.get(nowKey)
	if not nowLevelCfg:
		return
	nextKey = (titleId, nowLevel + 1)
	nextLevelCfg = TitleConfig.TitleLevel_Dict.get(nextKey)
	if not nextLevelCfg:
		return
	
	needUnbindRMB = 0
	useItemCnt = levelUpType
	hasItemCnt = role.ItemCnt(EnumGameConfig.TitleLevelItemCoding)
	if hasItemCnt < useItemCnt:
		if Environment.EnvIsNA():
			needUnbindRMB = (useItemCnt - hasItemCnt) * EnumGameConfig.LevelUpNeedUnbindRMB_NA
		else:
			needUnbindRMB = (useItemCnt - hasItemCnt) * EnumGameConfig.LevelUpNeedUnbindRMB
		useItemCnt = hasItemCnt
		if role.GetUnbindRMB() < needUnbindRMB:
			return
		
	critCnt = 0
	msgExp = 0
	isLevelUp = False
	nowExp = titledata[2]
	useExpCnt = 0
	for _ in range(levelUpType):
		exp = LevelUpPerExp
		if random.randint(0, 10000) < TitleRate:
			exp = LevelUpPerExp * 3 #暴击 3 倍经验
			critCnt += 1
		msgExp += exp
		nowExp += exp
		useExpCnt += 1
		if nowExp < nowLevelCfg.maxExp:
			continue
		nowLevel += 1
		nowExp = nowExp - nowLevelCfg.maxExp
		isLevelUp = True
		nowLevelCfg = nextLevelCfg
		nextLevelCfg = TitleConfig.TitleLevel_Dict.get((titleId, nowLevel + 1))
		if not nextLevelCfg:
			#满级
			nowExp = 0
			break
	
	if useExpCnt <= useItemCnt:
		useItemCnt = useExpCnt
		needUnbindRMB = 0
	else:
		if Environment.EnvIsNA():
			needUnbindRMB = (useExpCnt - useItemCnt) * EnumGameConfig.LevelUpNeedUnbindRMB_NA
		else:
			needUnbindRMB = (useExpCnt - useItemCnt) * EnumGameConfig.LevelUpNeedUnbindRMB

	with Tra_LevelUp_Title:
		if useItemCnt:
			role.DelItem(EnumGameConfig.TitleLevelItemCoding, useItemCnt)
		if needUnbindRMB:
			role.DecUnbindRMB(needUnbindRMB)
		if levelUpType == 1:
			AutoLog.LogBase(role.GetRoleID(), AutoLog.eveTitleLevelUp_1, (titleId, nowLevel, nowExp))
		else:
			AutoLog.LogBase(role.GetRoleID(), AutoLog.eveTitleLevelUp_2, (titleId, nowLevel, nowExp))
			
	titledata[1] = nowLevel
	titledata[2] = nowExp
	if isLevelUp is True:
		#重算属性
		role.ResetTitleProperty()
	
	role.CallBackFunction(backId, (titleId, nowLevel, nowExp))
	#提示
	if levelUpType == 1:
		if critCnt == 0:
			role.Msg(2, 0, GlobalPrompt.Title_tips_1 % msgExp)
		else:
			role.Msg(2, 0, GlobalPrompt.Title_tips_2 % msgExp)
	else:
		role.Msg(2, 0, GlobalPrompt.Title_tips_3 % (critCnt, msgExp))
	#精彩活动
	from Game.Activity.WonderfulAct import WonderfulActMgr, EnumWonderType
	WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_Act_TitleLevel, (role, levelUpType))


def RequestTitleStarUp(role, msg):
	'''
	称号升星
	@param role:
	@param msg:
	'''
	backId, titleId = msg
	if role.GetLevel() < NeedLevel:
		return
	titleDict = role.GetObj(EnumObj.Title)
	titleDataDict = titleDict.get(1)
	if not titleDataDict:
		return
	
	titledata = titleDataDict.get(titleId)
	if not titledata:
		return
	
	titleCfg = TitleConfig.Title_Dict.get(titleId)
	if not titleCfg or not titleCfg.canStarUp:
		return
	
	titleLevel = titledata[1]
	nowStar = titledata[3]
	nowKey = (titleId, nowStar)
	starCfg = TitleConfig.TitleStar_Dict.get(nowKey)
	if not starCfg:
		return
	
	nextKey = (titleId, nowStar + 1)
	nextCfg = TitleConfig.TitleStar_Dict.get(nextKey)
	if not nextCfg:
		return
	
	if titleLevel < starCfg.needTitleLevel:
		return
	
	for itemCoding, itemCnt in starCfg.needItems:
		if role.ItemCnt(itemCoding) < itemCnt:
			return
	
	with Tra_StarUp_Title:
		for itemCoding, itemCnt in starCfg.needItems:
			if role.DelItem(itemCoding, itemCnt) < itemCnt:
				print "GE_EXC, title star up error item "
				return
		titledata[3] = nowStar + 1
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveTitleStarUp, (titleId, nowStar + 1))
	
	role.ResetTitleProperty()
	role.CallBackFunction(backId, (titleId, nowStar + 1))
	role.Msg(2,0,GlobalPrompt.Title_tips_Star)


################################################################################
def RequestPutOnTitle(role, msg):
	'''
	请求佩戴称号
	@param role:
	@param msg:
	'''
	backId, titleId = msg
	titleDict  = role.GetObj(EnumObj.Title)
	titleDataDict = titleDict.get(1)
	if not titleDataDict:
		return
	if titleId not in titleDataDict:
		return
	titleEqulist = titleDict.get(2)
	if titleId in titleEqulist or len(titleEqulist) >= 5:
		return
	
	titleEqulist.append(titleId)
	Event.TriggerEvent(Event.Eve_ChangeTitle, role)
	#SyncRoleTitleData(role)
	role.CallBackFunction( backId, titleId)


def RequestTakeOffTitle(role, msg):
	'''
	请求卸下称号
	@param role:
	@param msg:
	'''
	backId, titleId = msg
	titleDict  = role.GetObj(EnumObj.Title)
	titleEqulist = titleDict.get(2)
	if not titleEqulist or titleId not in titleEqulist:
		return

	titleEqulist.remove(titleId)
	Event.TriggerEvent(Event.Eve_ChangeTitle, role)
	#SyncRoleTitleData(role)
	role.CallBackFunction( backId, titleId)

if "_HasLoad" not in dir():
	Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
	Event.RegEvent(Event.Eve_BeforeSaveRole, BeforeSaveRole)
	Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleTitleData)
	
	if Environment.HasLogic and not Environment.IsCross:
		cComplexServer.RegAfterNewHourCallFunction(CallPerHour)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TiTle_RequestPutOnTitle", "请求佩戴称号"), RequestPutOnTitle)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TiTle_RequestTakeOffTitle", "请求卸下称号"), RequestTakeOffTitle)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TiTle_RequestTitleLevelUp", "请求培养升级称号"), RequestTitleLevelUp)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TiTle_RequestTitleStarUp", "请求称号升星"), RequestTitleStarUp)
		
	