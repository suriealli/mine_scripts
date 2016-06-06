#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.LanternFestival.LanternRiddles")
#===============================================================================
# 灯谜
#===============================================================================
import random
import cRoleMgr
import Environment
from Game.Role import Event, Status
from Game.Role.Mail import Mail
from ComplexServer.Time import Cron
from ComplexServer.Log import AutoLog
from Common.Other import GlobalPrompt, EnumGameConfig
from Common.Message import AutoMessage
from Game.Activity import CircularDefine
from Game.Role.Data import EnumDayInt8, EnumObj, EnumInt1
from Game.Activity.LanternFestival import LanternFestivalConfig


if "_HasLoad" not in dir():
	IsStart = False
	MaxGuessTime = 10		#最大答题次数
	AwardItem = (27883, 1)	#灯谜礼包
	
	SceneID = 16
	PosX, PosY = 5060, 1510
	
	#消息
	SyncLanternRiddlesList = AutoMessage.AllotMessage("SyncLanternRiddlesList", "同步客户端角色灯谜题目列表")
	#日志
	TraLanternRiddlesAward = AutoLog.AutoTransaction("TraLanternRiddlesAward", "元宵节猜灯谜奖励")
	TraLanternRiddlesBuyCnt = AutoLog.AutoTransaction("TraLanternRiddlesBuyCnt", "元宵节购买猜灯谜次数")
	TraLanternRiddlesGlobalMail = AutoLog.AutoTransaction("TraLanternRiddlesGlobalMail", "元宵节元宵节猜灯谜通知")


def Start(param1, param2):
	if param2 != CircularDefine.CA_LanternRiddle:
		return
	
	global IsStart
	if IsStart:
		print "GE_EXC, LanternRiddle is already started"
		return
	
	IsStart = True
	

def End(param1, param2):
	if param2 != CircularDefine.CA_LanternRiddle:
		return
	global IsStart
	if not IsStart:
		print "GE_EXC, LanternRiddle is already ended"
		return
	IsStart = False


def RequestGuessRiddle(role, msg):
	'''
	客户端请求猜灯谜
	'''
	if IsStart is False:
		return
	if role.GetLevel() < EnumGameConfig.LanternFestivalNeedLevel:
		return
	#超过了猜谜次数
	if role.GetDI8(EnumDayInt8.LanternFestivalRiddleTimes) >= MaxGuessTime:
		return
	
	lanternFestivalData = role.GetObj(EnumObj.LanternFestival)
	roleRiddleList = lanternFestivalData.get('riddles')
	#还没有生成过题目
	if roleRiddleList is None:
		return
	if len(roleRiddleList) < 20:
		return
	#当前题号
	theIndex = role.GetDI8(EnumDayInt8.LanternFestivalRiddleIndex)
	curIndex = roleRiddleList[theIndex]
	rightAnswer = LanternFestivalConfig.RiddleConfigDict.get(curIndex)
	if rightAnswer is None:
		print "error while rightAnswer = LanternFestivalConfig.RiddleConfigDict.get(curIndex)(%s)" % curIndex
		return

	answer = msg
	#题号增加
	role.IncDI8(EnumDayInt8.LanternFestivalRiddleIndex, 1)
	#答题次数增加
	role.IncDI8(EnumDayInt8.LanternFestivalRiddleTimes, 1)
	
	if answer == rightAnswer:
		with TraLanternRiddlesAward:
			role.AddItem(*AwardItem)
		role.Msg(2, 0, GlobalPrompt.LanternRiddleRight % AwardItem)
	
	else:
		role.Msg(2, 0, GlobalPrompt.LanternRiddleWrong)


def RequestBuyGuessTime(role, msg):
	'''
	客户端请求购买 猜灯谜次数
	'''
	if IsStart is False:
		return
	
	if role.GetLevel() < EnumGameConfig.LanternFestivalNeedLevel:
		return
	
	oldCnt = role.GetDI8(EnumDayInt8.LanternFestivalRiddleBuyTimes)
	nowCnt = oldCnt + 1
	
	price = LanternFestivalConfig.BuyRiddleTimesConfigDict.get(nowCnt)
	if not price:
		return
	if role.GetUnbindRMB() < price:
		return
	#这里增加日志
	with TraLanternRiddlesBuyCnt:
		role.DecUnbindRMB(price)
		role.IncDI8(EnumDayInt8.LanternFestivalRiddleBuyTimes, 1)
		role.DecDI8(EnumDayInt8.LanternFestivalRiddleTimes, 1)
	

def RequestOpenPanel(role, msg):
	'''
	客户端请求打开猜灯谜面板
	'''
	if IsStart is False:
		return
	
	if role.GetLevel() < EnumGameConfig.LanternFestivalNeedLevel:
		return
	
	lanternFestivalData = role.GetObj(EnumObj.LanternFestival)
	if 'riddles' not in lanternFestivalData:
		lanternFestivalData['riddles'] = random.sample(LanternFestivalConfig.RiddleList, 20)
	riddleList = lanternFestivalData['riddles']
	role.SendObj(SyncLanternRiddlesList, riddleList)


def DailyClear(role, param):
	'''
	每日清理
	'''
	lanternFestivalData = role.GetObj(EnumObj.LanternFestival)
	if 'riddles' in lanternFestivalData:
		del lanternFestivalData['riddles']
	
	if IsStart is False:
		return
	with TraLanternRiddlesGlobalMail:
		roleID = role.GetRoleID()
		Mail.SendMail(roleID, GlobalPrompt.LanternRiddle_Title, GlobalPrompt.LanternRiddle_Sender, GlobalPrompt.LanternRiddle_Content)


def GlobalTell():
	'''
	定时广播通知活动开始
	'''
	if IsStart is False:
		return
	cRoleMgr.Msg(1, 0, GlobalPrompt.LanternRiddleGlobalTell)


def RequestGoToRiddlePlace(role, msg):
	'''
	请求传送到答题的位置
	'''
	if IsStart is False:
		return
	if role.GetLevel() < EnumGameConfig.LanternFestivalNeedLevel:
		return
	#传送前判断是否能进入传送状态
	if not Status.CanInStatus(role, EnumInt1.ST_TP):
		return
	
	role.Revive(SceneID, PosX, PosY)
	

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, Start)
		Event.RegEvent(Event.Eve_EndCircularActive, End)
		Event.RegEvent(Event.Eve_RoleDayClear, DailyClear)
		
		Cron.CronDriveByMinute((2038, 1, 1), GlobalTell, M="M == 0 or M==30")
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestBuyGuessTime_LanternFestival", "客户端请求购买猜灯谜次数"), RequestBuyGuessTime)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestOpenLanternRiddlePanel", "客户端请求打开元宵猜灯谜活动面板"), RequestOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestLanternRiddleGuess", "客户端请求猜灯谜"), RequestGuessRiddle)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestGoToRiddlePlace", "客户端请求传送到猜灯谜位置"), RequestGoToRiddlePlace)
