#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Control.GlobalControl.PassionTJHCControl")
#===============================================================================
# 天降横财 control
#===============================================================================
import cDateTime
import cComplexServer
import time
import datetime
import Environment
import DynamicPath
from Util import Random
from Util.File import TabFile
from Control import ProcessMgr
from Common.Message import PyMessage
from ComplexServer.Plug.Control import ControlProxy

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("PassionAct")
	
	CIRCULAR_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	CIRCULAR_FILE_FOLDER_PATH.AppendPath("CircularActive")
	
	#活动开关
	IS_START = False
	#当前缓存开奖结果所属回合
	ROUNDID = 0
	#天降横财 全局参与数据缓存 {UniqueCode:[roleId,roleName,zoneName],}
	TJHC_GlobalGamblerData_Dict = {}
	#抽奖中奖数据 {u_code:[roleId, roleName, zoneName, rewardId]}
	TJHC_LotteryResult_Dict = {}

	
	#天降横财奖励池配置 {rewardId:cfg,}
	TJHC_RewardConfig_Dict_C = {}
	#天降横财回合控制 {roundId:cfg,}
	TJHC_LotteryControl_Dict_C = {}
	
#===============================================================================
# 活动控制
#===============================================================================
def OpenActive(callArgv, regparam):
	'''
	天降横财-开启
	'''
	global ENDTIME
	global IS_START
	
	if IS_START:
		print 'GE_EXC, repeat start TJHC_Control'
		return
	IS_START = True
	
	#活动开启 即可处理
	InitActiveRound()
	
	
def CloseActive(callArgv, regparam):
	'''
	天降横财-结束
	'''
	global IS_START
	
	if not IS_START:
		print 'GE_EXC, repeat end TJHC_Control'
		return
	IS_START = False


def InitActiveRound():
	'''
	根据回合控制配置表 处理回合触发及tick
	'''
	nowTime = cDateTime.Seconds()
	for _, tCfg in TJHC_LotteryControl_Dict_C.iteritems():
		lotteryTime = int(time.mktime(tCfg.lotteryTime.timetuple()))
		if nowTime < lotteryTime:
			cComplexServer.RegTick(lotteryTime - nowTime, OnTickLottery, tCfg.roundId)


def OnTickLottery(callArgvs = None, regParams = None):
	'''
	tick触发 抽奖逻辑
	'''
	if not IS_START:
		print "GE_EXC,TJHC_Control::OnTickLottery,IS_START(%s)" % IS_START
		return
	
	roundId = regParams
	roundCfg = TJHC_LotteryControl_Dict_C.get(roundId)
	if not roundCfg:
		print "GE_EXC, TJHC_Control::OnTickLottery, can not find roundcfg by roundId(%s)" % roundId
		return
	
	global TJHC_GlobalGamblerData_Dict
	totalCodeCnt = len(TJHC_GlobalGamblerData_Dict)	
	
	#组装奖励随机器
	item_RandomObj = Random.RandomRate()
	for rewardId, rewardCnt in roundCfg.rewardPool:
		rewardCfg = TJHC_RewardConfig_Dict_C[rewardId]
		#满足抽奖所需参与兑奖券数
		if totalCodeCnt >= rewardCfg.lotteryNeedCnt:
			for _ in xrange(rewardCnt):
				item_RandomObj.AddRandomItem(1, rewardId)
		
	#组装uCode兑奖码随机器
	uCode_RanddomObj = Random.RandomRate()
	for uCode in TJHC_GlobalGamblerData_Dict.keys():
		uCode_RanddomObj.AddRandomItem(1, uCode)
	
	#双线随机抽奖
	global TJHC_LotteryResult_Dict
	TJHC_LotteryResult_Dict.clear()
	for _ in xrange(min(len(item_RandomObj.randomList),len(uCode_RanddomObj.randomList))):
		rewardId = item_RandomObj.RandomOneThenDelete()
		uCode = uCode_RanddomObj.RandomOneThenDelete()
		if not rewardId or not uCode:
			print "GE_EXC,TJHC_Control::OnTickLottery,not rewardId or not uCode"
			break
		
		roleId, roleName, zoneName = TJHC_GlobalGamblerData_Dict[uCode]
		TJHC_LotteryResult_Dict[uCode] = [roleId, roleName, zoneName, rewardId]
	
	#清楚本次参与兑奖码缓存
	TJHC_GlobalGamblerData_Dict.clear()
	#更新开奖回合
	global ROUNDID
	ROUNDID = roundId
	
	#同步本轮开奖结果
	for sessionid, cp in ProcessMgr.ControlProcesssSessions.iteritems():
		if cp.processid >= 30000:
			continue
		ControlProxy.SendLogicMsg(sessionid, PyMessage.TJHC_SendLotteryResult_Control2Logic, TJHC_LotteryResult_Dict)

	print "TJHC_Control::OnTickLottery,TJHC_LotteryResult_Dict",TJHC_LotteryResult_Dict
	
	
#===============================================================================
# 进程通信
#===============================================================================
def OnSendGamblerData(sessionid, msg):
	'''
	天降横财_发送参与兑奖数据_逻辑进程到控制进程
	@param sessionid: 
	@param msg:	GamberData
	'''
	if not IS_START:
		print "GE_EXC, TJHC_Control::OnSendGamblerData,IS_START(%s)" % IS_START
		return
	
	lGamblerData = msg	
	global TJHC_GlobalGamblerData_Dict
	TJHC_GlobalGamblerData_Dict.update(lGamblerData)


def OnRequestResult(sessionid, msg):
	'''
	逻辑进程请求开奖结果
	'''
	if not IS_START:
		print "GE_EXC, TJHC_Control::OnRequestResult,IS_START(%s)" % IS_START
		return
	
	backid, roundId = msg
	if ROUNDID != roundId:
		print "GE_EXC, TJHC_Control::OnRequestResult::ROUNDID(%s) != roundId(%s)" % (ROUNDID, roundId)
		return
	
	
	#回调开奖结果数据
	ControlProxy.CallBackFunction(sessionid, backid, (roundId, TJHC_LotteryResult_Dict))
	

#===============================================================================
# 配置
#===============================================================================
class PassionTJHCReward(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionTJHCReward.txt")
	def __init__(self):
		self.rewardId = int
		self.lotteryNeedCnt = int
		self.rewardItem = self.GetEvalByString


def LoadPassionTJHCReward():
	global TJHC_RewardConfig_Dict_C
	for cfg in PassionTJHCReward.ToClassType(False):
		rewardId = cfg.rewardId
		if rewardId in TJHC_RewardConfig_Dict_C:
			print "GE_EXC,repeat rewardId(%s) in TJHC_RewardConfig_Dict_C" % rewardId
		TJHC_RewardConfig_Dict_C[rewardId] = cfg
		
		
class PassionTJHCControl(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("PassionTJHCControl.txt")
	def __init__(self):
		self.roundId = int
		self.syncTime = self.GetDatetimeByString
		self.lotteryTime = self.GetDatetimeByString
		self.rewardPool = self.GetEvalByString


def LoadPassionTJHCControl():
	global TJHC_LotteryControl_Dict_C
	for cfg in PassionTJHCControl.ToClassType(False):
		roundId = cfg.roundId
		if roundId in TJHC_LotteryControl_Dict_C:
			print "GE_EXC,repeat roundId(%s) in TJHC_LotteryControl_Dict_C" % roundId
		
		for rewardId, _ in cfg.rewardPool:
			if rewardId not in TJHC_RewardConfig_Dict_C:
				print "GE_EXC, error rewardId(%s) of roundId(%s) that not in TJHC_RewardConfig_Dict" % (rewardId, roundId)
				
		TJHC_LotteryControl_Dict_C[roundId] = cfg


class PassionTJHCActive(TabFile.TabLine):
	FilePath = CIRCULAR_FILE_FOLDER_PATH.FilePath("PassionTJHCActive.txt")
	def __init__(self):
		self.activeName = str
		self.beginTime = eval
		self.endTime = eval
	
	def Active(self):
		beginTime = int(time.mktime(datetime.datetime(*self.beginTime).timetuple()))
		endTime = int(time.mktime(datetime.datetime(*self.endTime).timetuple()))
		nowTime = cDateTime.Seconds()
		if beginTime <= nowTime < endTime:
			#激活
			OpenActive(None, (endTime))
			cComplexServer.RegTick(endTime - nowTime, CloseActive)
		elif nowTime < beginTime:
			#注册一个tick激活
			cComplexServer.RegTick(beginTime - nowTime, OpenActive, (endTime))
			cComplexServer.RegTick(endTime - nowTime, CloseActive)


def LoadPassionTJHCActive():
	'''
	加载并启动活动
	'''
	for cfg in PassionTJHCActive.ToClassType(False):
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in PassionTJHCActive"
			continue
		cfg.Active()

def LoadTJHCConfig_C():
	'''
	优先加载奖励池
	'''
	LoadPassionTJHCReward()
	LoadPassionTJHCControl()


if "_HasLoad" not in dir():
	if Environment.HasControl:
		LoadTJHCConfig_C()
		LoadPassionTJHCActive()
		cComplexServer.RegDistribute(PyMessage.TJHC_SendGamblerData_Logic2Control, OnSendGamblerData)
		cComplexServer.RegDistribute(PyMessage.TJHC_RequestLotteryResult_Logic2Control, OnRequestResult)