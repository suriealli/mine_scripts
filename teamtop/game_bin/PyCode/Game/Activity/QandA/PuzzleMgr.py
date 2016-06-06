#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.QandA.PuzzleMgr")
#===============================================================================
# 趣味拼图
#===============================================================================
import Environment
import cDateTime
import random
import cRoleMgr
import cNetMessage
import cComplexServer
from Game.Role import Event
from Game.Activity.QandA import PuzzleConfig
from Common.Other.GlobalPrompt import PackageIsFull_Tips
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumDayInt1,EnumObj,EnumCD
from Common.Other import EnumGameConfig ,GlobalPrompt

if "_HasLoad" not in dir() :
	IS_START = False			#拼图活动开始控制
	Puzzle_Time = 60 * 30				#拼图时间
	Puzzle_tick_time = 24 * 60 * 60		#拼图开启时间
	#日志
	Puzzle_Reward_Log = AutoLog.AutoTransaction("Puzzle_Reward_Log", "趣味拼图奖励")
	#消息
	Puzzle_Start = AutoMessage.AllotMessage("Puzzle_Start", "通知客户端拼图任务开启")
	Puzzle_Ready = AutoMessage.AllotMessage("Puzzle_Ready", "准备拼图")
	Puzzle_award = AutoMessage.AllotMessage("Puzzle_award", "拼图领奖")

		
def Get_Puzzle(role):
		'''
		创建拼图
		'''
		puzzleplayer = {}
		awardId = 0
		finsh = 0 				#防止完成后还能移动拼图
		tick = 0				#tick id
		begintime = cDateTime.Seconds()		#拼图开始时间
		endtime = 0			#拼图完成时间
		state = 2			#拼图状态
		awardstate = 0		#奖励状态(0代表不能领奖，1代表可以领奖，2代表已经领取奖励)
		signAward = 0		#奖励的等级
		PictureNumbers = len(PuzzleConfig.PUZZLE_PICTURE)
		PictureId = random.randint(1, PictureNumbers) #记录图片
		index = 1
		result= []
		#乱序拼图
		while index < 17:
			result.append(index)
			index += 1
		random.shuffle(result)			#记录拼图位置
		puzzle = result
		puzzleplayer[0] = puzzle
		puzzleplayer[1] = awardId
		puzzleplayer[2] = finsh
		puzzleplayer[3] = PictureId
		puzzleplayer[4] = tick
		puzzleplayer[5] = begintime
		puzzleplayer[6] = endtime
		puzzleplayer[7] = state
		puzzleplayer[8] = awardstate
		puzzleplayer[9] = signAward
		role.SetObj(EnumObj.PuzzleData, puzzleplayer)
		
#拼图任务开始
def CallAfterNewDay():
	global IS_START
	today = cDateTime.WeekDay()
	if today == 0:
		IS_START = True
		cNetMessage.PackPyMsg(Puzzle_Start, 1)
	else:
		IS_START = False
		if today != 1:
			return
		cNetMessage.PackPyMsg(Puzzle_Start, 0)

#开始拼图
def ReadyPuzzle(role, param):
	global IS_START
	if not IS_START :
		return
	#判断是否已经玩过
	rolelevel = role.GetLevel()
	if rolelevel < EnumGameConfig.Level_30 :
		return
	HasPlayed = role.GetDI1(EnumDayInt1.Puzzle_IsPlay)
	if  HasPlayed :
		player = role.GetObj(EnumObj.PuzzleData)
		if not player :
			return
		PuzzleBegin = player[5]
		puzzleplace = player[0]
		Endtime = player[5] + player[6]
		Puzzle_state = player[7]
		AwardId = player[9]
		if Puzzle_state == 0 :
			msg = player[3],puzzleplace,PuzzleBegin,Endtime,AwardId
		else :
			msg = player[3],puzzleplace,PuzzleBegin,Endtime,Puzzle_state,AwardId
		role.SendObj(Puzzle_award, player[8])
		role.SendObj(Puzzle_Ready, msg)
		return
		
	#获取玩家拼图状态
	player = role.GetObj(EnumObj.PuzzleData)
	#第一次开启游戏
	if not player :
		Get_Puzzle(role)
		player = role.GetObj(EnumObj.PuzzleData)
		PuzzleBegin = cDateTime.Seconds()
		player[5] = PuzzleBegin
		role.SetCD(EnumCD.PuzzleCD, Puzzle_Time)
		#30分后自动结束
		player[4] = role.RegTick(Puzzle_Time, EndPuzzle)
		puzzleplace = player[0]
		Endtime = PuzzleBegin
		Puzzle_state = player[7]
		msg = player[3],puzzleplace,PuzzleBegin,Endtime,Puzzle_state
		#发送乱序后的拼图
		role.SendObj(Puzzle_Ready, msg)
	#返回游戏
	else :
		PuzzleBegin = player[5]
		puzzleplace = player[0]
		Puzzle_state = player[7]
		Endtime = cDateTime.Seconds()
		msg = player[3],puzzleplace,PuzzleBegin,Endtime,Puzzle_state
		role.SendObj(Puzzle_Ready, msg)
	role.SendObj(Puzzle_award, 0)


#移动拼图	
def MovePuzzle(role,msg):
	global IS_START
	if not IS_START :
		return
	FristMove,SecondMove = msg
	player = role.GetObj(EnumObj.PuzzleData)
	finsh = player[2]
	if not player :
		return
	if finsh :
		return
	#获得玩家的拼图
	puzzle = player[0]
	if not puzzle :
		return
	if role.GetCD(EnumCD.PuzzleCD) <= 0:
		return
	#判断拼图是否合法
	if not (FristMove/4 == SecondMove/4 and abs(FristMove - SecondMove) ==1) :
		if abs(FristMove - SecondMove) != 4 :
			return
	#交换拼图
	puzzle[FristMove],puzzle[SecondMove] = puzzle[SecondMove],puzzle[FristMove]
	
	#检测是否已经拼完
	index = 0
	while index <16 :
		if index+1 != puzzle[index] :
			return
		index += 1
	#拼图已经完成
	role.SetDI1(EnumDayInt1.Puzzle_IsPlay, 1)
	time = role.GetCD(EnumCD.PuzzleCD)
	player[6] = Puzzle_Time-time 
	role.SetCD(EnumCD.PuzzleCD, 0)
	PuzzleAwardId = int
	roleLevel = role.GetLevel()
	mark = 0
	for awardid, cfg in PuzzleConfig.PUZZLE_AWARD.iteritems():
		if cfg.AwardLevel[0] <= roleLevel and roleLevel <= cfg.AwardLevel[1]:
			if cfg.LeftTime > time :
				mark+=1
				continue
			else :
				PuzzleAwardId = awardid
				break
		else :
			continue
	if not PuzzleAwardId :
		print "GE_EXC, MovePuzzle not PuzzleAwardId %s " % PuzzleAwardId
		return
	player[1] = PuzzleAwardId
	player[9] = mark
	player[2] = 1 
	player[7] = 1
	player[8] = 1
	role.UnregTick(player[4])
	ReadyPuzzle(role, None)



#60分后自动结束拼图
def EndPuzzle(role,callargv=None, regparam=None):
	global IS_START
	if not IS_START :
		return
	player = role.GetObj(EnumObj.PuzzleData)
	if not player :
		return
	if  player[2] == 1:
		return
	player[2] = 1
	player[7] = 0
	roleLevel = role.GetLevel() 
	for awardid, cfg in PuzzleConfig.PUZZLE_AWARD.iteritems():
		if cfg.AwardLevel[0] <= roleLevel and roleLevel <=cfg.AwardLevel[1]:
				PuzzleAwardId = awardid + 4
				break
		else :
			continue
	if not PuzzleAwardId :
		print "GE_EXC, MovePuzzle not PuzzleAwardId %s " % PuzzleAwardId
		return	
	player[1] = PuzzleAwardId
	player[6] = Puzzle_Time
	role.SendObj(Puzzle_award, 1)
	player[9] = 4
	player[8] = 1
	role.SetDI1(EnumDayInt1.Puzzle_IsPlay, 1)



#领取奖励
def GetPuzzleReward(role, param):
	global IS_START
	if not IS_START:
		return
	player = role.GetObj(EnumObj.PuzzleData)
	if not player :
		return
	if  not player[8] or player[8] == 2:
		return
	PuzzleAwardId = player[1]	
	if not PuzzleAwardId:
		print 'GE_EXC, GetPuzzleRewardt not PuzzleAwardId %s ' % PuzzleAwardId
		return
	cfg = PuzzleConfig.PUZZLE_AWARD.get(PuzzleAwardId)
	if not cfg:
		print "GE_EXC, PuzzleConfig.PUZZLE_AWARD has no awardId(%s)" % PuzzleAwardId
		return
	#YY防沉迷对奖励特殊处理
	yyAntiFlag = role.GetAnti()
	if yyAntiFlag == 1:
		AwardMoney = cfg.Money_fcm
		Awarditems = cfg.Award_fcm
	elif yyAntiFlag == 0:
		AwardMoney = cfg.Money
		Awarditems = cfg.Award
	else:
		role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
		player[8] = 2
		ReadyPuzzle(role, None)
		return
	count = role.PackageEmptySize()
	#检测背包是否足以放下奖励
	if len(Awarditems) > count:
		role.Msg(2, 0,PackageIsFull_Tips)
		return
	# 发送奖励
	with Puzzle_Reward_Log :
		tips = ""
		role.IncMoney(AwardMoney)
		tips += GlobalPrompt.Reward_Tips
		tips +=GlobalPrompt.Money_Tips % (AwardMoney)
		for coding, cnt in Awarditems:
			role.AddItem(coding, cnt)
			tips += GlobalPrompt.Item_Tips % (coding, cnt)
		role.Msg(2, 0, tips)
	player[8] = 2
	ReadyPuzzle(role, None)


def ClearPuzzleDate(role,param):
	role.SetObj(EnumObj.PuzzleData, {})


if "_HasLoad" not in dir() :
	if Environment.HasLogic and not Environment.IsCross:
		pass
		Event.RegEvent(Event.Eve_RoleDayClear,ClearPuzzleDate)
		#星期天拼图开始
		cComplexServer.RegAfterNewDayCallFunction(CallAfterNewDay)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ReadyPuzzle", "客户端请求拼图"), ReadyPuzzle)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("MovePuzzle", "移动拼图"), MovePuzzle)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GetPuzzleReward", "领取奖励"), GetPuzzleReward)
