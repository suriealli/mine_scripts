#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.QQHallLottery.QQHallLotteryMgr")
#===============================================================================
# 大厅搏饼
#===============================================================================
import Environment
from random import randint
import cRoleMgr
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Activity import CircularDefine
from Game.Activity.QQHallLottery import QQHallLotteryConfig
from Game.Role.Data import EnumInt32, EnumInt16#, EnumTempInt64 

if "_HasLoad" not in dir():
	IS_START = False	#活动开关标志
	
	QQHall_Lottery_Master_Record_List = []	#缓存搏饼大奖记录  EnumGameConfig.AF_MasterRecordNum 条
	
	QQHall_Lottery_RoleIds_List = []	#缓存打开搏饼面板的roleId
	
	QQHallLotteryResultMsg = AutoMessage.AllotMessage("QQHallLottery_Result_SB", "大厅搏饼结果")
	QQHallLotteryMasterRecord = AutoMessage.AllotMessage('QQHallLottery_MasterRecord_S', "大厅搏饼大奖记录")
	
	Tra_QQHallLotteryReward = AutoLog.AutoTransaction("Tra_QQHallLotteryReward", "大厅搏饼奖励")
	Tra_QQHallLotteryNumExchange = AutoLog.AutoTransaction("Tra_QQHallLotteryNumExchange","大厅充值神石数兑换搏饼次数")

#============= 活动控制 ====================
def QQHallLotteryStart(*param):
	'''
	大厅搏饼开启
	'''
	_, circularType = param
	if CircularDefine.CA_QQHallLottery != circularType:
		return
	
	global IS_START	
	global QQHall_Lottery_RoleIds_List
	global QQHall_Lottery_Master_Record_List	
	if IS_START:
		print "GE_EXC,repeat open QQHallLottery"
		return
		
	IS_START = True
	QQHall_Lottery_RoleIds_List = []
	QQHall_Lottery_Master_Record_List = []

def QQHallLotteryEnd(*param):
	'''
	大厅搏饼结束
	'''
	_, circularType = param
	if CircularDefine.CA_QQHallLottery != circularType:
		return
	
	# 未开启 
	global IS_START
	global QQHall_Lottery_RoleIds_List
	global QQHall_Lottery_Master_Record_List	
	if not IS_START:
		print "GE_EXC, end QQHallLottery while not start"
		return
		
	IS_START = False
	QQHall_Lottery_RoleIds_List = []
	QQHall_Lottery_Master_Record_List = []

#### 客户端请求 start	
def OnGetLotteryNum(role, param):
	'''
	玩家请求领取大厅搏饼次数 （活动期间大厅神石充值兑换）
	@param role: id 充值神石可兑换次数对应配置ID
	'''	
	#活动未开启
	if not IS_START:
		return
	
	#索引不存在
	cfgId = param	
	cfg = QQHallLotteryConfig.QQHALL_LATTERY_EXTRA_TIMES_DICT.get(cfgId)
	if not cfg:
		return
	
	#充值神石数不满足
	todayBuyRMB_Q = role.GetDayBuyUnbindRMB_Q()
	if todayBuyRMB_Q < cfg.value:
		return
	
	#已领取
	todayExtraQQHallLotteryRecord = role.GetI32(EnumInt32.DayExtraQQHallRecord)
	if todayExtraQQHallLotteryRecord & cfgId:
		return	
	
	#process
	with Tra_QQHallLotteryNumExchange:
		role.SetI32(EnumInt32.DayExtraQQHallRecord, todayExtraQQHallLotteryRecord + cfgId)	
		role.IncI16(EnumInt16.QQHallLotteryEffectTimes, cfg.extraNum)

def OnLottery(role,param = None):
	'''
	响应玩家摇骰子请求
	'''
	#活动未开启
	if not IS_START:
		return
	
	#等级不足
	if role.GetLevel() < EnumGameConfig.QQHall_LotteryNeedLevel:
		return
	
	#剩余次数不足
	effectTimes = role.GetI16(EnumInt16.QQHallLotteryEffectTimes)
	if effectTimes < 1:
		return
	
	#随机出筛子并判定类型
	diceType, diceList = RollDice()	
	
	diceTypeConfigDict = QQHallLotteryConfig.QQHALL_LOTTERY_REWARD_DICT.get(diceType)
	if not diceTypeConfigDict:
		print "GE_EXC,RequestQQHallLottery::can not get cfg by diceType(%s)" % diceType
	
	roleLevel = role.GetLevel() 
	levelRangeId = 1
	for _,cfg in diceTypeConfigDict.iteritems():
		levelDown, levelUp = cfg.levelRange
		if roleLevel >= levelDown and roleLevel <=levelUp:
			levelRangeId = cfg.levelRangeId
			break
	
	result = [diceType, levelRangeId, diceList]
	
	#更新剩余次数
	with Tra_QQHallLotteryReward:
		role.DecI16(EnumInt16.QQHallLotteryEffectTimes, 1)	
	#通知客户端搏饼结果
	role.SendObjAndBack(QQHallLotteryResultMsg, result, 5, QQHallLotteryCallBack, (diceType,levelRangeId, diceList))

def OnOpenLotteryPanel(role,param = None):
	'''
	打开搏饼面板
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.QQHall_LotteryNeedLevel:
		return
	
	global QQHall_Lottery_RoleIds_List
	if role.GetRoleID() not in QQHall_Lottery_RoleIds_List:
		QQHall_Lottery_RoleIds_List.append(role.GetRoleID())	
	
	role.SendObj(QQHallLotteryMasterRecord, QQHall_Lottery_Master_Record_List)

def OnCloseLotteryPanel(role,param = None):
	'''
	关闭搏饼面板
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.QQHall_LotteryNeedLevel:
		return
	
	global QQHall_Lottery_RoleIds_List
	if role.GetRoleID() not in QQHall_Lottery_RoleIds_List:
		return
	
	QQHall_Lottery_RoleIds_List.remove(role.GetRoleID())

def RollDice():
	'''
	摇骰子
	@return: diceType 骰子对应奖励类型【1-9】
	@return: diceList 骰子点数集合
	'''
	diceType = 0
	diceList = []
	
	latteryValue = 0	
	for _ in range(EnumGameConfig.QQHall_LotteryRollNum):
		tmpDice = randint(1,6)
		latteryValue += EnumGameConfig.QQHall_LotteryDiceValue.get(tmpDice,0)
		diceList.append(tmpDice)
	
	# {1:100000,2:10000,3:1000,4:100,5:10,6:1}-->中秋节日快乐
	if latteryValue == 420000:
		#状元插金花  4个中，2个秋
		diceType = 9
	elif str(latteryValue).count('5') > 0 or str(latteryValue).count('6') > 0:
		#五王 5个或以上相同的字
		diceType = 8
	elif latteryValue >= 400000:
		#状元  4个中
		diceType = 7
	elif latteryValue == 111111:
		#对堂 无重字
		diceType = 6
	elif latteryValue >= 300000:
		#三红 3个中 
		diceType = 5
	elif str(latteryValue).count('4') > 0:
		#四进  4个相同的字，不包括4个中
		diceType = 4
	elif latteryValue >= 200000:
		#二举  2个中
		diceType = 3
	elif latteryValue >= 100000:
		#一秀 1个中
		diceType = 2
	else:
		#赏
		diceType = 1	
	
	return diceType,diceList	

def QQHallLotteryCallBack(role, callargv, regparam):
	'''
	搏饼回调
	@param regparam: 搏饼奖励类型
	'''
	diceType, levelRangeId, diceList = regparam
	if diceType not in QQHallLotteryConfig.QQHALL_LOTTERY_REWARD_DICT:
		print "GE_EXC,QQHallLotteryCallBack error diceType(%s)" % diceType
		return
	
	cfgDict = QQHallLotteryConfig.QQHALL_LOTTERY_REWARD_DICT.get(diceType)
	cfg = cfgDict.get(levelRangeId)
	if not cfg:
		print "GE_EXC,QQHallLotteryCallBack :: can not find config with diceType(%s), levelRangeId(%s)" % (diceType, levelRangeId)
		return	
	
	#状元以上的 ::公告 & 大奖记录 
	if diceType > EnumGameConfig.QQHall_LotteryMasterTypeMin:
		global QQHall_Lottery_Master_Record_List
		QQHall_Lottery_Master_Record_List.append((role.GetRoleName(), diceType))
		
		relativeSize = len(QQHall_Lottery_Master_Record_List) - EnumGameConfig.QQHall_LotteryMasterRecordNum
		if relativeSize > 0:
			#记录数量超过 截断
			QQHall_Lottery_Master_Record_List = QQHall_Lottery_Master_Record_List[relativeSize:]
		
		#发送最新记录给当前打开面板的玩家
		for roleId in QQHall_Lottery_RoleIds_List:
			member = cRoleMgr.FindRoleByRoleID(roleId) 
			if not member:
				QQHall_Lottery_RoleIds_List.remove(roleId)
			member.SendObj(QQHallLotteryMasterRecord, QQHall_Lottery_Master_Record_List)
	
	#process
	QQHallLotteryRewardPromptMsg = ""
	with Tra_QQHallLotteryReward:
		for coding, cnt in cfg.nomalItems:
			QQHallLotteryRewardPromptMsg += GlobalPrompt.QQHall_LotteryRewardMsg_Item % (coding, cnt)
			role.AddItem(coding, cnt)
		
		if cfg.rewardCoin > 0:
			QQHallLotteryRewardPromptMsg += GlobalPrompt.QQHall_LotteryRewardMsg_Money % (cfg.rewardCoin)
			role.IncMoney(cfg.rewardCoin)
		
		#日志
		logContent = (diceType,diceList)
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveQQHallLottery, logContent)
	
	#获得奖励提示
	rewardPrompt = GlobalPrompt.QQHall_LotteryRewardMsg_Head + QQHallLotteryRewardPromptMsg
	role.Msg(2, 0, rewardPrompt)
	
#============= 事件处理 ====================
def OnRoleDayClear(role,param):
	'''
	每日清除
	'''
	#清除神石充值兑换搏饼次数记录
	role.SetI32(EnumInt32.DayExtraQQHallRecord, 0)


def OnClientLostorExit(role, param):
	'''
	客户端掉线或退出的处理 
	@param role:
	@param param:
	'''	
	if not IS_START:
		return
	
	global QQHall_Lottery_RoleIds_List
	roleId = role.GetRoleID()
	if roleId not in QQHall_Lottery_RoleIds_List:
		return
	
	QQHall_Lottery_RoleIds_List.remove(roleId)

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		#每日清除
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
	
	if Environment.HasLogic and not Environment.IsCross:
		#掉线
		Event.RegEvent(Event.Eve_ClientLost, OnClientLostorExit)
		Event.RegEvent(Event.Eve_BeforeExit, OnClientLostorExit)
		#循环活动事件
		Event.RegEvent(Event.Eve_StartCircularActive, QQHallLotteryStart)
		Event.RegEvent(Event.Eve_EndCircularActive, QQHallLotteryEnd)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQHallLottery_OnGetLotteryNum", "大厅搏饼玩家请求领取次数"), OnGetLotteryNum)
	
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQHallLottery_OnOpenLotteryPanel", "大厅搏饼玩家请求面板"), OnOpenLotteryPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQHallLottery_OnCloseLotteryPanel", "大厅搏饼玩家请求关闭面板"), OnCloseLotteryPanel)
	
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQHallLottery_OnLottery", "大厅搏饼玩家请求摇骰子"), OnLottery)
