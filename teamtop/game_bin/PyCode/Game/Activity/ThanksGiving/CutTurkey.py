#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ThanksGiving.CutTurkey")
#===============================================================================
# 切火鸡
#===============================================================================
import random
import Environment
import cRoleMgr
import cDateTime
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Role import Event
from Game.Role.Data import EnumDayInt8
from Game.Activity.ThanksGiving import ThanksGivingConfig
from Game.Activity import CircularDefine

if "_HasLoad" not in dir():
	IsCutTurkeyOpen = False
	#{role_id --> {0:火鸡索引, 1:完成的次数, 2:需要的次数, 3:开始时间戳, 4:题目索引, 5:题目答案, 6:是否答对, 7:tickId, 8:奖励礼包coding}}
	CutTurkeyCntDict = {}
	
	#火鸡索引, 开始时间戳, 需要切的次数
	CutTurkeyData = AutoMessage.AllotMessage("CutTurkeyData", "切火鸡数据")
	#题目索引
	CutTurkeyQA = AutoMessage.AllotMessage("CutTurkeyQA", "切火鸡答题")
	
	CutTurkeyUse_Log = AutoLog.AutoTransaction("CutTurkeyUse_Log", "切火鸡使用神石")
	CutTurkey_Log = AutoLog.AutoTransaction("CutTurkey_Log", "切火鸡奖励")
	
def OpenCutTurkey(param1, param2):
	if param2 != CircularDefine.CA_CutTurkey:
		return
	
	global IsCutTurkeyOpen
	if IsCutTurkeyOpen:
		print 'GE_EXC, IsCutTurkeyOpen is already True'
	IsCutTurkeyOpen = True
	
def CloseCutTurkey(param1, param2):
	if param2 != CircularDefine.CA_CutTurkey:
		return
	
	global IsCutTurkeyOpen, CutTurkeyCntDict
	if not IsCutTurkeyOpen:
		print 'GE_EXC, IsCutTurkeyOpen is already False'
	IsCutTurkeyOpen = False
	
	CutTurkeyCntDict = {}
	
def GetCloseValue(value, value_list):
	tmp_level = 0
	for i in value_list:
		if i > value:
			return tmp_level
		tmp_level = i
	else:
		#没有找到返回最后一个值
		return tmp_level
	
def EndCut(role, argv = None, param = None):
	global CutTurkeyCntDict
	roleId = role.GetRoleID()
	
	#0火鸡索引, 1完成的次数, 2需要的次数, 3开始时间戳, 4题目索引, 5题目答案, 6是否答对, 7tickId, 8奖励礼包coding
	cutData = CutTurkeyCntDict.get(roleId)
	if not cutData:
		#没有数据了 ?
		return
	
	index, isCorrect, rewardCoding = cutData[0], cutData[6], cutData[8]
	
	#删除数据
	del CutTurkeyCntDict[roleId]
	
	with CutTurkey_Log:
		if isCorrect:
			#答对
			role.AddItem(rewardCoding, 2)
			#回调客户端显示特效
			if param:
				role.CallBackFunction(param, index)
			role.Msg(2, 0, GlobalPrompt.CutTurkeySuccess % (rewardCoding, 2))
		else:
			#答错, 不显示特效
			role.AddItem(rewardCoding, 1)
			role.Msg(2, 0, GlobalPrompt.CutTurkeyFail % (rewardCoding, 1))
	
	#通知客户端清理数据
	role.SendObj(CutTurkeyData, (0, 0, 0))
	
def RequestOpen(role, msg):
	'''
	请求打开面板
	@param role:
	@param msg:
	'''
	global IsCutTurkeyOpen
	if not IsCutTurkeyOpen: return
	
	if role.GetLevel() < EnumGameConfig.CutTurkeyLv:
		return
	
	roleId = role.GetRoleID()
	
	global CutTurkeyCntDict
	cutData = CutTurkeyCntDict.get(roleId)
	if not cutData:
		role.SendObj(CutTurkeyData, (0, 0, 0))
	else:
		#火鸡索引, 开始的时间戳, 需要切的次数
		role.SendObj(CutTurkeyData, (cutData[0], cutData[3], cutData[2]))
	
def RequestCut(role, msg):
	'''
	请求切火鸡
	@param role:
	@param msg:
	'''
	global IsCutTurkeyOpen
	if not IsCutTurkeyOpen: return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.CutTurkeyLv:
		return
	
	index = msg
	if index not in (1, 2):
		return
	
	if index == 1:
		if role.GetDI8(EnumDayInt8.CutTurkeyNCnt) >= EnumGameConfig.CutTurkeyNMaxCnt:
			#普通火鸡
			return
	else:
		#高级火鸡
		if role.GetDI8(EnumDayInt8.CutTurkeyACnt) >= EnumGameConfig.CutTurkeyAMaxCnt:
			return
		if role.GetUnbindRMB() < EnumGameConfig.CutTurkeyRMB:
			return
	
	roleId = role.GetRoleID()
	index = msg
	
	level = GetCloseValue(roleLevel, ThanksGivingConfig.CutTurkeyLevel_List)
	
	cfg = ThanksGivingConfig.CutTurkey_Dict.get((index, level))
	if not cfg:
		return
	
	global CutTurkeyCntDict
	if roleId in CutTurkeyCntDict:
		#已经开始切了
		return
	
	#随机需要的次数
	cnt = random.randint(*cfg.randomRange)
	#开始时间戳
	beginSec = cDateTime.Seconds()
	#随机题目
	qIndex = random.choice(cfg.questionsStore)
	
	with CutTurkeyUse_Log:
		if index == 2:
			role.DecUnbindRMB(EnumGameConfig.CutTurkeyRMB)
			role.IncDI8(EnumDayInt8.CutTurkeyACnt, 1)
		else:
			role.IncDI8(EnumDayInt8.CutTurkeyNCnt, 1)
		
		#0火鸡索引, 1完成的次数, 2需要的次数, 3开始时间戳, 4题目索引, 5题目答案, 6是否答对, 7tickId, 8奖励礼包coding
		CutTurkeyCntDict[roleId] = [index, 0, cnt, beginSec, qIndex, 0, 0, role.RegTick(EnumGameConfig.CutTurkeyCountdown, EndCut), cfg.rewardCoding]
	
	#火鸡索引, 开始时间戳, 需要切多少次
	role.SendObj(CutTurkeyData, (index, beginSec, cnt))
	
def RequestFinish(role, msg):
	'''
	请求完成切火鸡
	@param role:
	@param msg:
	'''
	global IsCutTurkeyOpen
	if not IsCutTurkeyOpen: return
	
	if role.GetLevel() < EnumGameConfig.CutTurkeyLv:
		return
	
	roleId = role.GetRoleID()
	cnt = msg
	
	global CutTurkeyCntDict
	cutData = CutTurkeyCntDict.get(roleId)
	if not cutData:
		#没有开始或者倒计时完了
		return
	
	#已经请求过一次了
	if cutData[1]:
		return
	
	cutData[1] = cnt
	
	#0火鸡索引, 1完成的次数, 2需要的次数, 3开始时间戳, 4题目索引, 5题目答案, 6是否答对, 7tickId, 8奖励礼包coding
	if cutData[1] == cutData[2]:
		#切够次数了, 生成答案
		cfg = ThanksGivingConfig.CutTurkeyQ_Dict.get(cutData[4])
		if not cfg:
			print 'GE_EXC, CutTurkey RequestFinish can not find questions %s answer' % cutData[4]
			return
		cutData[5] = cfg.answer
		
		role.SendObj(CutTurkeyQA, cutData[4])
	else:
		#次数不够, 取消tick
		role.UnregTick(cutData[7])
		#结束
		EndCut(role)
		
def RequestAnswer(role, msg):
	'''
	请求答题
	@param role:
	@param msg:
	'''
	global IsCutTurkeyOpen
	if not IsCutTurkeyOpen: return
	
	#等级不到
	if role.GetLevel() < EnumGameConfig.CutTurkeyLv:
		return
	
	roleId = role.GetRoleID()
	nowSec = cDateTime.Seconds()
	
	cutData = CutTurkeyCntDict.get(roleId)
	#0火鸡索引, 1完成的次数, 2需要的次数, 3开始时间戳, 4题目索引, 5题目答案, 6是否答对, 7tickId, 8奖励礼包coding
	if not cutData:
		return
	
	if (nowSec < cutData[3]) or ((nowSec - cutData[3]) > EnumGameConfig.CutTurkeyCountdown):
		return
	
	if cutData[1] != cutData[2]:
		#没有达到次数
		return
	
	backId, answer = msg
	
	#取消tick
	role.UnregTick(cutData[7])
	
	if answer != cutData[5]:
		#答错
		EndCut(role)
	else:
		#答对
		cutData[6] = 1
		CutTurkeyCntDict[roleId] = cutData
		
		EndCut(role, param=backId)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CutTurkey_Open", "切火鸡打开面板"), RequestOpen)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CutTurkey_Cut", "切火鸡切"), RequestCut)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CutTurkey_Finish", "切火鸡完成"), RequestFinish)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CutTurkey_Answer", "切火鸡答题"), RequestAnswer)
		
		Event.RegEvent(Event.Eve_StartCircularActive, OpenCutTurkey)
		Event.RegEvent(Event.Eve_EndCircularActive, CloseCutTurkey)
		