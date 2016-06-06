#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.RewardBuff.RewardBuffConfig")
#===============================================================================
# 奖励加成buff配置
#===============================================================================
import time
import DynamicPath
import Environment
from Util.File import TabFile
import cRoleMgr
import datetime
import cDateTime
import cNetMessage
import cComplexServer
from Common.Message import AutoMessage

if "_HasLoad" not in dir():
	#{奖励buff索引:buff失效时间}
	RewardBuffData = AutoMessage.AllotMessage("RewardBuffData", "奖励加成buff数据")
	
	RB_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	RB_FILE_FOLDER_PATH.AppendPath("RewardBuff")
	
	RewardBuff_Dict = {}
	
	RewardBuffAct_Dict = {}
	
	RewardBuffIndexToId_Dict = {}
	
def ActiveRewardBuff(argv, param):
	buffId, buffIndex, endTime = param
	
	global RewardBuffAct_Dict, RewardBuffIndexToId_Dict
	if buffId in RewardBuffAct_Dict:
		print 'GE_EXC, RewardBuffConfig Repeat active reward buff id %s' % buffId
		return
	RewardBuffAct_Dict[buffId] = endTime
	
	if buffIndex in RewardBuffIndexToId_Dict:
		print 'GE_EXC, ActiveRewardBuff repeat buff index %s' % buffIndex
	RewardBuffIndexToId_Dict[buffIndex] = buffId
	
	cNetMessage.PackPyMsg(RewardBuffData, RewardBuffAct_Dict)
	cRoleMgr.BroadMsg()

def CancelRewardBuff(argv, param):
	buffId, buffIndex = param
	
	global RewardBuffAct_Dict
	if buffId not in RewardBuffAct_Dict:
		print 'GE_EXC, RewardBuffConfig CancelRewardBuff can not find buff id %s' % buffId
		return
	del RewardBuffAct_Dict[buffId]
	
	if buffIndex not in RewardBuffIndexToId_Dict:
		print 'GE_EXC, CancelRewardBuff can not find buff index %s' % buffIndex
	else:
		del RewardBuffIndexToId_Dict[buffIndex]
	
	cNetMessage.PackPyMsg(RewardBuffData, RewardBuffAct_Dict)
	cRoleMgr.BroadMsg()
	
class RewardBuffConfig(TabFile.TabLine):
	FilePath = RB_FILE_FOLDER_PATH.FilePath("RewardBuff.txt")
	def __init__(self):
		self.buffId = int
		self.buffIndex = int
		self.beginTime = eval
		self.endTime = eval
		self.buffCoef = int
		self.needWorldLevel = int
	
	def Active(self):
		#开始时间戳
		beginTime = int(time.mktime(datetime.datetime(*self.beginTime).timetuple()))
		#结束时间戳
		endTime = int(time.mktime(datetime.datetime(*self.endTime).timetuple()))
		#当前时间戳
		nowTime = cDateTime.Seconds()
		
		if beginTime > endTime:
			return
		
		if beginTime <= nowTime < endTime:
			#在开始和结束时间戳之间, 激活
			ActiveRewardBuff(None, (self.buffId, self.buffIndex, endTime))
			cComplexServer.RegTick(endTime - nowTime, CancelRewardBuff, (self.buffId, self.buffIndex))
		elif nowTime < beginTime:
			#在开始时间戳之前
			cComplexServer.RegTick(beginTime - nowTime, ActiveRewardBuff, (self.buffId, self.buffIndex, endTime))
			cComplexServer.RegTick(endTime - nowTime, CancelRewardBuff, (self.buffId, self.buffIndex))
		
def LoadRewardBuffConfig():
	global RewardBuff_Dict
	
	for RBC in RewardBuffConfig.ToClassType():
		if RBC.buffId in RewardBuff_Dict:
			print "GE_EXC, repeat buffId (%s) in RewardBuff_Dict" % RBC.buffId
		if RBC.beginTime > RBC.endTime:
			print 'GE_EXC, RewardBuffConfig beginTime %s > endTime %s' % (RBC.beginTime, RBC.endTime)
			continue
		RewardBuff_Dict[RBC.buffId] = RBC
		RBC.Active()
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadRewardBuffConfig()
