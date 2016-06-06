#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.QandA.NewQandAMgr")
#===============================================================================
# 新答题活动控制  @author Administrator 2015
#===============================================================================
import cRoleMgr
import cProcess
import Environment
import cDateTime
import cComplexServer
from ComplexServer import Init
from ComplexServer.Plug.Control import ControlProxy
from Common.Other import EnumGameConfig
from Game.Role import Event
from Game.Persistence import Contain
from Game.GlobalData import ZoneName
from Game.Role.Mail import Mail
from Common.Other import GlobalPrompt
from Game.Role.Data import EnumObj, EnumDayInt1
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage, PyMessage
from Game.Activity.QandA import NewQandAConfig
from ComplexServer.Time import Cron

if "_HasLoad" not in dir():
	
	#以下枚举，用于新答题数据字典
	Enum_Questions = 8		#：[当天题目]
	Enum_Weeks = 9			#：距离2015年11月9日的多少周
	Enum_TodayPoints = 10	#：本日得分
	Enum_RefeshFlag = 11	#：今日是否重置题目
	Enum_BeginTime = 12		#：答题开始时间戳
	
	FINALS_CONTROL_RANK_CACHE = []		#答题决赛排行榜
	
	#消息
	finalsRankData = AutoMessage.AllotMessage("finalsRankData", "同步客户端决赛排行榜")
	finalsScoreData = AutoMessage.AllotMessage("finalsScoreData", "同步客户端决赛分数")
	anwserScoreData = AutoMessage.AllotMessage("anwserScoreData", "同步客户端今日答题得分等级")
	allQuestiontData = AutoMessage.AllotMessage("allQuestiontData", "同步客户端玩家剩余所有题目")
	passedScoreData = AutoMessage.AllotMessage("passedScoreData", "同步客户端往日得分数据")
	#日志
	questionRewardLog = AutoLog.AutoTransaction("questionRewardLog ", "新答题初赛发奖日志 ")
	canFinalsLog = AutoLog.AutoTransaction("canFinalsLog ", "新答题发送决赛资格日志 ")
	FinalsRewardLog = AutoLog.AutoTransaction("FinalsRewardLog", "新答题决赛跨服排名发奖")
	
	FinalsStart = False


#====================================================================
# 辅助函数
#====================================================================
def nowWeeks():
	#返回当天是距离2015年11月9日的多少周 16748
	#2015-11-13 16752
	day_2015_11_9 = 16748
	nowDays = cDateTime.Days()
	return (nowDays - day_2015_11_9) / 7
#注意处理答题时间超过两小时仍可答题情况


def timeOut(role):
	#如果时间超过20分钟，返回False
	weekDay = cDateTime.WeekDay()
	if weekDay == 0:
		needSeconds = 1800
	else:
		needSeconds = 1200
	
	global Enum_BeginTime
	beginSeconds = role.GetObj(EnumObj.NewQandAData)[Enum_BeginTime]
	if cDateTime.Seconds() - beginSeconds > needSeconds:
		global Enum_Questions
		if weekDay == 0:
			role.GetObj(EnumObj.NewQandAData)[0] = (-1, -1)
			role.SendObj(finalsScoreData, (-1, -1))
		else:
			role.GetObj(EnumObj.NewQandAData)[weekDay] = -1
			role.SendObj(anwserScoreData, -1)
		return True
	return False


#====================================================================
# 数据初始化
#====================================================================
def OnInitRole(role, msg=None):
	#初始化角色数据
	if not role.GetObj(EnumObj.NewQandAData):
		role.SetObj(EnumObj.NewQandAData, {0:None, 1:None, 2:None, 3:None, 4:None, 5:None, 6:None,
										8:[], 9:nowWeeks(), 10:0, 11:0, 12:None})


def RoleDataClear(role, msg=None):
	'''
	玩家每日数据清理，随机本日答题数据
	@param role:
	@param msg: None
	'''
	#活动30级开启
	if EnumGameConfig.Level_30 > role.GetLevel():
		return
	
	global Enum_RefeshFlag
	#如果已经随机了题目，返回
	if role.GetObj(EnumObj.NewQandAData)[Enum_RefeshFlag] == cDateTime.Days():
		return 
	
	global Enum_Questions, Enum_TodayPoints, Enum_Weeks
	
	QandAData = role.GetObj(EnumObj.NewQandAData)
	
	#清理跨周数据
	if nowWeeks() != QandAData[Enum_Weeks]:
		QandAData[Enum_Weeks] = nowWeeks()
		for i in range(0, 7):
			QandAData[i] = None
	#清理跨天数据
	role.SetDI1(EnumDayInt1.newQandARewardFlag, False)		#不可领奖
	QandAData[Enum_TodayPoints] = 0							#今日得分清零
	QandAData[Enum_BeginTime] = None						#清除开始答题时间
	QandAData[Enum_Questions] = []							#清空题库
	QandAData[Enum_RefeshFlag] = cDateTime.Days()			#设置今日时间为最新题库的标识
	
	nowWeekDay = cDateTime.WeekDay()
	questionTypeList = NewQandAConfig.questionTypeDict.get(nowWeekDay)
	if  not questionTypeList:
		print "GE_EXC, cannot find the type config in questionTypeDict." 
		return
	#随机出角色本日题库
	for (questionType, num) in questionTypeList:
		randomObj = NewQandAConfig.questionRandomDict.get(questionType)
		QandAData[Enum_Questions].extend(randomObj.RandomMany(num))
	
	#若玩家可以参加决赛,发送决赛邮件提醒
	if nowWeekDay == 0:
		if len([1 for x in range(1, 7) if QandAData[x] == 1 or QandAData[x] == 2]) < 3:
			QandAData[Enum_Questions] = []						#清空题库
			return
		with canFinalsLog:
			Mail.SendMail(role.GetRoleID(), GlobalPrompt.CanFinalsTitle, GlobalPrompt.Sender, GlobalPrompt.CanFinalsContent)


def RequestQuestionsBegin(role, msg):
	'''
	玩家获取所有今天题目，开始答题
	@param role:
	@param msg:
	'''
	global Enum_Questions, Enum_BeginTime
	QandAData = role.GetObj(EnumObj.NewQandAData)
	#周日特殊处理，决赛开启时不满足参赛资格
	weekDay = cDateTime.WeekDay()
	if role.GetObj(EnumObj.NewQandAData)[weekDay]:
		if weekDay == 0:
			role.SendObj(finalsScoreData, QandAData[0])
		else:
			role.SendObj(anwserScoreData, QandAData[weekDay])
		return
	if weekDay == 0:
		#周日决赛未开启
		global FinalsStart
		if not FinalsStart:
			#超过答题时间按答题超时处理
			role.GetObj(EnumObj.NewQandAData)[0] = (-1, -1)
			role.SendObj(finalsScoreData, (-1, -1))
			return 
		if not QandAData[Enum_Questions]:
			role.SendObj(allQuestiontData, (QandAData[Enum_BeginTime], []))
			return
	
	if not QandAData[Enum_BeginTime]:
		QandAData[Enum_BeginTime] = cDateTime.Seconds()
	#答题超时,清除答题时间，清除题目
	if timeOut(role):
		return
	role.SendObj(allQuestiontData, (QandAData[Enum_BeginTime], QandAData[Enum_Questions]))
	if weekDay != 0 :
		Event.TriggerEvent(Event.Eve_PassionMultiRewardTask, role, (EnumGameConfig.PassionMulti_Task_NewQandA, True))
	


def RequestUpdateAnswer(role, msg):
	'''
	玩家提交答案
	@param role:
	@param msg: (题目index, 题目answer)
	'''
	global FinalsStart
	if not cDateTime.WeekDay() and not FinalsStart:
		#超过答题时间按答题超时处理
		role.GetObj(EnumObj.NewQandAData)[0] = (-1, -1)
		role.SendObj(finalsScoreData, (-1, -1))
		return
	callBackId, (indexMsg, answerMsg) = msg
	#消息类型不对
	if not isinstance(answerMsg, tuple):
		return
	
	global Enum_Questions, Enum_BeginTime, Enum_TodayPoints
	
	QandAData = role.GetObj(EnumObj.NewQandAData)
	#未开始答题
	if not QandAData[Enum_BeginTime]:
		return
	#答题时间超时
	if timeOut(role):
		return
	#客户端要答的题目是否在题目集合
	if indexMsg not in QandAData[Enum_Questions]:
		return
	answerSet = NewQandAConfig.questionBankDict.get(indexMsg)
	
	if not answerSet:
		print "GE_EXC, can't find the question NO. %s, roleId = " % (indexMsg, role.GetRoleID())
		return 
	QandAData[Enum_Questions].remove(indexMsg)
	if set(answerMsg) == answerSet:
		QandAData[Enum_TodayPoints] = QandAData.get(Enum_TodayPoints, 0) + 1
	role.CallBackFunction(callBackId, 1)
	
	#最后一次答题，自动交卷
	if not QandAData[Enum_Questions]:
		if cDateTime.WeekDay() == 0:
			FinalsEnd(role)
		else:
			QuestionsEnd(role)


def QuestionsEnd(role):
	'''
	玩家请求结束初赛答题
	@param role: role
	'''
	#注意处理未完成答题的情况
	QandAData = role.GetObj(EnumObj.NewQandAData)
	
	point = QandAData[Enum_TodayPoints]
	pointLevelObj = NewQandAConfig.scoreRankdDict.get(point)
	if not pointLevelObj:
		print "GE_EXC, cannot find the pointLevel in scoreRankdDict where key = %s." % point
		return
	
	#如果今日已有成绩不能重复触发
	if QandAData[cDateTime.WeekDay()]:
		return
	QandAData[cDateTime.WeekDay()] = pointLevelObj.scoreIndex
	role.SetDI1(EnumDayInt1.newQandARewardFlag, True)
	role.SendObj(anwserScoreData, pointLevelObj.scoreIndex)


def FinalsEnd(role):
	'''
	结束决赛答题
	@param role: role
	'''
	global FinalsStart, Enum_BeginTime, Enum_TodayPoints
	if not FinalsStart: return
	
	QandAData = role.GetObj(EnumObj.NewQandAData)
	point = QandAData[Enum_TodayPoints]
	usedTime = cDateTime.Seconds() - QandAData[Enum_BeginTime]
	zName = ZoneName.GetZoneName(cProcess.ProcessID)
	QandAData[0] = (usedTime, point)
	
	#得分，答题用时，答题开始时间，角色ID，角色名，服务器名
	global QANDA_ROLE_RANK_LIST
	QANDA_ROLE_RANK_LIST.append((point, usedTime, QandAData[Enum_BeginTime], role.GetRoleID(), role.GetRoleName(), zName))
	
	role.SendObj(finalsScoreData, (usedTime, point))


def RequestQuestionsReward(role, msg):
	'''
	玩家请求领取答题奖励
	@param role:
	@param msg: 
	'''
	QandAData = role.GetObj(EnumObj.NewQandAData)
	if not role.GetDI1(EnumDayInt1.newQandARewardFlag):
		return
	
	rewardIndex = QandAData.get(cDateTime.WeekDay())
	if not rewardIndex:
		return
	#YY防沉迷对奖励特殊处理
	yyAntiFlag = role.GetAnti()
	if yyAntiFlag == 1:
		levelToRewardDict = NewQandAConfig.firstRewardDict_fcm.get(rewardIndex)
	elif yyAntiFlag == 0:
		levelToRewardDict = NewQandAConfig.firstRewardDict.get(rewardIndex)
	else:
		role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
		#设置已经领奖标识
		role.SetDI1(EnumDayInt1.newQandARewardFlag, False)
		return
	
	rewardList, moneyNum = levelToRewardDict.get(role.GetLevel())
	if not rewardList:
		print "GE_EXC, can't find the reward of new QandA, where rewardIndex = %s." % rewardIndex
		return
	
	#设置已经领奖标识
	role.SetDI1(EnumDayInt1.newQandARewardFlag, False)
	
	#发奖
	with questionRewardLog:
		role.IncMoney(moneyNum)
		for item in rewardList:
			role.AddItem(*item)
	#提示
	tips = GlobalPrompt.Money_Tips % moneyNum + ''.join(GlobalPrompt.Item_Tips % item for item in rewardList)
	role.Msg(2, 0, GlobalPrompt.Reward_Tips + tips)


def RequestFinalsRank(role, msg):
	'''
	新答题活动请求决赛排行榜
	@param role:
	@param msg:
	'''
	#活动30级开启
	if EnumGameConfig.Level_30 > role.GetLevel():
		return
	
	global FINALS_CONTROL_RANK_CACHE
	role.SendObj(finalsRankData, FINALS_CONTROL_RANK_CACHE)


def RequestPassedScore(role, msg):
	'''
	新答题活动请求历史成绩
	@param role:
	@param msg:
	'''
	#活动30级开启
	if EnumGameConfig.Level_30 > role.GetLevel():
		return
	
	msgDict = {}
	nowWeekDay = cDateTime.WeekDay()
	if nowWeekDay == 0:
		nowWeekDay = 6
	for i in range(0, nowWeekDay + 1):
		score = role.GetObj(EnumObj.NewQandAData).get(i)
		if not score:
			continue
		msgDict[i] = score
	
	role.SendObj(passedScoreData, msgDict)


#===============================================================================
# 处理定时触发
#===============================================================================
def FiveMinutesReady():
	'''
	新答题决赛开始前5分钟提示
	'''
	#系统通知
	cRoleMgr.Msg(11, 0, GlobalPrompt.FinalsReady_2)


def beginFinals():
	'''
	新答题决赛开始
	'''
	global FinalsStart, QANDA_ROLE_RANK_LIST
	FinalsStart = True
	QANDA_ROLE_RANK_LIST.clear()
	
	cRoleMgr.Msg(11, 0, GlobalPrompt.FinalsReady)


def endFinals():
	'''
	新答题决赛结束
	'''
	global FinalsStart
	FinalsStart = False
	#10秒之后发放普通奖励，邮件
	cComplexServer.RegTick(10, rewardCommon)


def rewardCommon(callargv, regparam):
	#邮件发放决赛答题普通奖励
	global FINALS_CONTROL_RANK_CACHE, QANDA_ROLE_RANK_LIST
	roleIdList = []
	for l in FINALS_CONTROL_RANK_CACHE:
		roleIdList.append(l[-1])
		
	rewards = NewQandAConfig.finalsRewardDict.get(51)
	if not rewards:
		print "GE_EXC, cannot find the reward of QAndAFinals, where rank > 50"
		return
	with FinalsRewardLog:
		for dataList in QANDA_ROLE_RANK_LIST:
			if dataList[3] in roleIdList:
				continue
			Mail.SendMail(dataList[3], GlobalPrompt.FinalsRewardTitle_2, GlobalPrompt.Sender, GlobalPrompt.FinalsRewardContent_2, items=rewards)
	QANDA_ROLE_RANK_LIST.clear()

#===============================================================================
# 处理控制进程推送的数据
#===============================================================================
def OnControlUpdataRank(sessionid, rankList):
	'''
	#控制进程更新了新的跨服排行榜数据过来
	@param sessionid:
	@param rankList:
	'''
	
	global FINALS_CONTROL_RANK_CACHE
	FINALS_CONTROL_RANK_CACHE = []
	for l in rankList:
		#记录数据，答题时间，答题用间，答题开始时间，角色ID，服务器名
		FINALS_CONTROL_RANK_CACHE.append((l[0], l[1], l[4], l[5], l[3]))


#===============================================================================
# 控制进程请求
#===============================================================================
def OnControlRequestRank(sessionid, msg):
	'''
	#控制进程请求获取本服富豪榜榜
	@param sessionid:
	@param msg:
	'''
	backid, _ = msg
	global QANDA_ROLE_RANK_LIST
	QANDA_ROLE_RANK_LIST.sort(key=lambda x:(-x[0], x[1], x[2], x[3]))
	ControlProxy.CallBackFunction(sessionid, backid, (cProcess.ProcessID, QANDA_ROLE_RANK_LIST[:50]))


#===============================================================================
# 服务器启动,数据载回后调用
#===============================================================================
def ServerUp():
	#起服的时候向控制进程请求跨服排行榜数据
	global QANDA_ROLE_RANK_LIST
	QANDA_ROLE_RANK_LIST.sort(key=lambda x:(-x[0], x[1], x[2], x[3]))
	ControlProxy.SendControlMsg(PyMessage.Control_LogicSendFinalsRankData, (cProcess.ProcessID, QANDA_ROLE_RANK_LIST[:50]))


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#得分，答题用时，答题开始时间，角色ID，角色名，服务器名
		QANDA_ROLE_RANK_LIST = Contain.List("QANDA_ROLE_RANK_LIST", (2038, 1, 1), ServerUp)
		Event.RegEvent(Event.Eve_AfterLevelUp, RoleDataClear)
		Event.RegEvent(Event.Eve_AfterLogin, RoleDataClear)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDataClear)
		Event.RegEvent(Event.Eve_InitRolePyObj, OnInitRole)
		#距离答题开始还有5分钟
		
		if Environment.EnvIsQQ() or Environment.EnvIsFT() or Environment.EnvIsYY() or Environment.IsDevelop:
			#波兰、繁体、俄罗斯、土耳其、西班牙不开新答题
			Cron.CronDriveByMinute((2038, 1, 1), FiveMinutesReady, w="w == 7", H="H == 13", M="M == 55")
			Cron.CronDriveByMinute((2038, 1, 1), beginFinals, w="w == 7", H="H == 14", M="M == 0")
			Cron.CronDriveByMinute((2038, 1, 1), endFinals, w="w == 7", H="H == 16", M="M == 0")
		#注册消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestQuestionsBegin", "玩家请求开始答题"), RequestQuestionsBegin)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestQuestionsReward", "玩家请求获取答题奖励"), RequestQuestionsReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestUpdateAnswer", "玩家请求提交答案"), RequestUpdateAnswer)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestFinalsRank", "玩家请求新答题决赛排行榜"), RequestFinalsRank)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestPassedScore", "玩家请求往日得分数据"), RequestPassedScore)
		#发送跨服排行榜数据到逻辑进程
		cComplexServer.RegDistribute(PyMessage.Control_UpdateNewQandARank, OnControlUpdataRank)
		#请求逻辑进程的答题决赛排行榜数据(回调)
		cComplexServer.RegDistribute(PyMessage.Control_RequestFinalsRankData, OnControlRequestRank)
