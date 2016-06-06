#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.BallFame.BallFame")
#===============================================================================
# 一球成名
#===============================================================================
import Environment
import cRoleMgr
import cNetMessage
import cComplexServer
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumDayInt8
from Game.Persistence import Contain
from Game.Activity.BallFame import BallFameConfig
from Game.Role import Event
from Game.Activity import CircularDefine, CircularActive

if "_HasLoad" not in dir():
	isBallFameOpen = False
	
	BallFameActiveId = 0
	
	BallFameObserver = []
	
	BallFame_Msg = AutoMessage.AllotMessage("BallFame_Msg", "一球成名进球信息")
	
	BallFameGoals_Log = AutoLog.AutoTransaction("BallFameGoals_Log", "一球成名进球日志")
	BallFameUCheers_Log = AutoLog.AutoTransaction("BallFameUCheers_Log", "一球成名公会喝彩日志")
	BallFameASCheers_Log = AutoLog.AutoTransaction("BallFameASCheers_Log", "一球成名全服喝彩日志")
	
def OpenBallFame(role, msg):
	if msg != CircularDefine.CA_BallFame:
		return
	global isBallFameOpen
	if isBallFameOpen:
		print "GE_EXC, BallFame is already open"
		return
	isBallFameOpen = True
	
	global BallFameActiveId
	if BallFameActiveId:
		print 'GE_EXC, BallFameActiveId is already have'
	isActiveTypeRepeat = False
	for activeId, (activeType, _) in CircularActive.CircularActiveCache_Dict.iteritems():
		if activeType != msg:
			continue
		if isActiveTypeRepeat:
			print 'GE_EXC, repeat BallFameActiveType in CircularActiveCache_Dict'
		BallFameActiveId = activeId
		isActiveTypeRepeat = True
	
def CloseBallFame(role, msg):
	if msg != CircularDefine.CA_BallFame:
		return
	global isBallFameOpen
	if not isBallFameOpen:
		print "GE_EXC, BallFame is already close"
	isBallFameOpen = False
	
	#活动结束清理数据
	global BallFameDict
	if BallFameDict:
		BallFameDict.clear()
	
	global BallFameObserver
	BallFameObserver = []
	
	global BallFameActiveId
	if not BallFameActiveId:
		print 'GE_EXC, BallFameActiveId is already zero'
	BallFameActiveId = 0
	
def ChangeCirActID(param1, param2):
	#改变活动ID
	circularType, circularId = param2
	
	if circularType != CircularDefine.CA_BallFame:
		return
	
	global BallFameActiveId
	BallFameActiveId = circularId
	
def RequestGoals(role, msg):
	'''
	进球
	@param role:
	@param msg:
	'''
	#活动未开启
	global isBallFameOpen
	if not isBallFameOpen: return
	
	global BallFameActiveId
	if not BallFameActiveId: return
	
	#等级不足
	if role.GetLevel() < EnumGameConfig.BallFame_LevelLimit:
		return
	#获取配置
	goalsCnt = role.GetDI8(EnumDayInt8.BallFameGoalsCnt)
	cfg = BallFameConfig.BF_GoalsDict.get(goalsCnt)
	if not cfg:
		print "GE_EXC, RequestGoals can not find goalsCnt %s in BF_GoalsDict" % goalsCnt
		return
	#没有足够的道具
	if role.ItemCnt(EnumGameConfig.BallFame_NeedItemCoding) < cfg.needItemCnt:
		return
	#背包空间不够
	if role.PackageIsFull():
		return
	boxCfg = BallFameConfig.BF_BoxDict.get(BallFameActiveId)
	if not boxCfg:
		return
	boxCoding = boxCfg.goalsBoxCoding
	
	#扣道具
	with BallFameGoals_Log:
		role.DelItem(EnumGameConfig.BallFame_NeedItemCoding, cfg.needItemCnt)
	
	global BallFameDict
	if not BallFameDict:
		BallFameDict["all_service"] = 0
	#+全服进球
	BallFameDict["all_service"] += 1
	#+公会进球
	unionID = role.GetUnionID()
	if unionID:
		if unionID not in BallFameDict:
			BallFameDict[unionID] = 1
		else:
			BallFameDict[unionID] += 1
	BallFameDict.changeFlag = True
	
	with BallFameGoals_Log:
		#加进球次数
		if goalsCnt < 127:
			role.IncDI8(EnumDayInt8.BallFameGoalsCnt, 1)
		#发放进球宝箱
		role.AddItem(boxCoding, 1)
	
	global BallFameObserver
	cNetMessage.PackPyMsg(BallFame_Msg, BallFameDict.data)
	for observer in BallFameObserver:
		observer.BroadMsg()
	role.Msg(2, 0, GlobalPrompt.BallFameGoalsTips % (boxCoding, 1))
	
def RequestASCheers(role, msg):
	'''
	全服喝彩
	@param role:
	@param msg:
	'''
	global isBallFameOpen
	if not isBallFameOpen: return
	
	global BallFameActiveId
	if not BallFameActiveId: return
	
	global BallFameDict
	if not BallFameDict: return
	
	#等级不足
	if role.GetLevel() < EnumGameConfig.BallFame_LevelLimit:
		return
	#全服喝彩次数
	cheersCnt = role.GetDI8(EnumDayInt8.BallFameASCheerCnt)
	#超过最大喝彩次数
	if cheersCnt >= EnumGameConfig.BallFame_MaxCheersCnt:
		return
	#获取配置
	cfg = BallFameConfig.BF_ASCDict.get(cheersCnt)
	if not cfg:
		print "GE_EXC, RequestASCheers can not find cheersCnt %s in BF_ASCDict" % cheersCnt
		return
	#需要的进球数不够
	if cfg.needGoalsCnt > BallFameDict["all_service"]:
		return
	#背包空间不够
	if role.PackageIsFull():
		return
	boxCfg = BallFameConfig.BF_BoxDict.get(BallFameActiveId)
	if not boxCfg:
		return
	boxCoding = boxCfg.cheersBoxCoding
	
	with BallFameASCheers_Log:
		#加全服喝彩次数
		role.IncDI8(EnumDayInt8.BallFameASCheerCnt, 1)
		#发放喝彩宝箱
		role.AddItem(boxCoding, 1)
		
	role.Msg(2, 0, GlobalPrompt.BallFameCheersTips % (boxCoding, 1))
	
def RequestUnionCheers(role, msg):
	'''
	帮派喝彩
	@param role:
	@param msg:
	'''
	global isBallFameOpen
	if not isBallFameOpen: return
	
	global BallFameActiveId
	if not BallFameActiveId: return
	
	global BallFameDict
	if not BallFameDict: return
	
	#等级不足
	if role.GetLevel() < EnumGameConfig.BallFame_LevelLimit:
		return
	#公会喝彩次数
	cheersCnt = role.GetDI8(EnumDayInt8.BallFameUnionCheerCnt)
	#超过最大喝彩次数
	if cheersCnt >= EnumGameConfig.BallFame_MaxCheersCnt:
		return
	#获取配置
	cfg = BallFameConfig.BF_UCDict.get(cheersCnt)
	if not cfg:
		print "GE_EXC, RequestUnionCheers can not find cheersCnt %s in BF_UCDict" % cheersCnt
		return
	#获取公会ID
	unionID = role.GetUnionID()
	if unionID not in BallFameDict:
		return
	#需要的公会进球数不足
	if cfg.needGoalsCnt > BallFameDict[unionID]:
		return
	#背包空间不够
	if role.PackageIsFull():
		return
	boxCfg = BallFameConfig.BF_BoxDict.get(BallFameActiveId)
	if not boxCfg:
		return
	boxCoding = boxCfg.cheersBoxCoding
	
	with BallFameUCheers_Log:
		#加公会喝彩次数
		role.IncDI8(EnumDayInt8.BallFameUnionCheerCnt, 1)
		#发放喝彩宝箱
		role.AddItem(boxCoding, 1)
		
	role.Msg(2, 0, GlobalPrompt.BallFameCheersTips % (boxCoding, 1))
	
def RequestOpenPanel(role, msg):
	'''
	打开面板
	@param role:
	@param msg:
	'''
	#活动未开始
	global isBallFameOpen
	if not isBallFameOpen: return
	
	#等级不足
	if role.GetLevel() < EnumGameConfig.BallFame_LevelLimit:
		return
	
	#加入观察者
	global BallFameObserver
	if role not in BallFameObserver:
		BallFameObserver.append(role)
	
	#同步进球信息
	global BallFameDict
	role.SendObj(BallFame_Msg, BallFameDict.data)
	
def RequestClosePanel(role, msg):
	'''
	关闭面板
	@param role:
	@param msg:
	'''
	#活动未开始
	global isBallFameOpen
	if not isBallFameOpen: return
	
	#等级不足
	if role.GetLevel() < EnumGameConfig.BallFame_LevelLimit:
		return
	
	#删除观察者
	global BallFameObserver
	if role in BallFameObserver:
		BallFameObserver.remove(role)
	
def BeforeExit(role, param):
	#活动未开启
	global isBallFameOpen
	if not isBallFameOpen: return
	
	#删除观察者
	global BallFameObserver
	if role in BallFameObserver:
		BallFameObserver.remove(role)
	
def AfterNewDay():
	#活动未开启
	global isBallFameOpen
	if not isBallFameOpen: return
	
	#清理数据
	global BallFameDict
	BallFameDict.clear()
	
	global BallFameObserver
	for observer in BallFameObserver:
		observer.SendObj(BallFame_Msg, BallFameDict.data)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic or Environment.HasWeb:
		BallFameDict = Contain.Dict("BallFameDict", (2038, 1, 1))
	
	if not Environment.IsCross and Environment.HasLogic:
		Event.RegEvent(Event.Eve_BeforeExit, BeforeExit)
		Event.RegEvent(Event.Eve_StartCircularActive, OpenBallFame)
		Event.RegEvent(Event.Eve_EndCircularActive, CloseBallFame)
		Event.RegEvent(Event.Eve_ChangeCirActID, ChangeCirActID)
		
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("BallFame_Goals", "一球成名进球"), RequestGoals)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("BallFame_ASCheers", "一球成名全服喝彩"), RequestASCheers)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("BallFame_UnionCheers", "一球成名公会喝彩"), RequestUnionCheers)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("BallFame_OpenPanel", "一球成名打开面板"), RequestOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("BallFame_ClosePanel", "一球成名关闭面板"), RequestClosePanel)
		
