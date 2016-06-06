#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQLZ.QQLZHappyDraw")
#===============================================================================
# 蓝钻回馈大礼
#===============================================================================
import time
import cComplexServer
import Environment
import cDateTime
import cRoleMgr
import cNetMessage
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Role import Call, Event
from Game.Role.Data import EnumObj, EnumInt8 ,EnumInt1, EnumTempInt64
from Game.ThirdParty.QQLZ import QQLZFeedBackConfig

OPEN_STATE = 1
CLOSE_STATE = 0

if "_HasLoad" not in dir():
	IS_START = False	#蓝钻转转乐活动开关标志
	ENDTIME = 0			#活动结束时间戳
	#消息
	QQLZFeedBack_ActiveState = AutoMessage.AllotMessage("QQLZFeedBack_ActiveState", "蓝钻回馈大礼同步活动状态")
	QQLZFeedBack_OldRewards = AutoMessage.AllotMessage("QQLZFeedBack_OldRewards", "蓝钻回馈已经抽取奖励")
	QQLZFeedBack_LotteryResult = AutoMessage.AllotMessage("QQLZFeedBack_LotteryResult", "蓝钻回馈抽奖结果")
	#事务
	Tra_QQLZFeebBack_Lottery = AutoLog.AutoTransaction("Tra_QQLZFeebBack_Lottery", "蓝钻回馈大礼抽奖获得")
	
#============= 活动控制 ====================
#启服之后根据当前时间和活动配置时间 注册tick控制活动
def Initialize(p1,p2):	
	'''
	初始化活动tick
	'''
	#获取活动配置时间
	activeBase = QQLZFeedBackConfig.QQLZ_FEEDBACK_ACT_CONTROL
	if not activeBase:
		print "GE_EXC, activeBase is None while Initialize QQLZFeedBack"
		return
	beginDate = activeBase.beginDate
	endDate = activeBase.endDate
	
	#当前日期-时间
	nowDate = cDateTime.Now()
	nowTime = cDateTime.Seconds()
	
	#开始时间戳-结束时间戳
	beginTime = int(time.mktime(beginDate.timetuple()))
	endTime = int(time.mktime(endDate.timetuple()))
	
	if beginDate <= nowDate < endDate:
		#开启 并注册结束tick
		QQLZFeedBack_Start(None, endTime)
		cComplexServer.RegTick(endTime - nowTime, QQLZFeedBack_End)
	elif nowDate < beginDate:
		#注册开启和结束的tick
		cComplexServer.RegTick(beginTime - nowTime, QQLZFeedBack_Start, endTime)
		cComplexServer.RegTick(endTime - nowTime, QQLZFeedBack_End)
		
		
	#如果活动没有结束，对版本号进行检测
	if nowDate < endDate:
		Event.TriggerEvent(Event.Eve_QQCheckVersion, None, (1, beginDate, "QQLZFeedBack"))

def QQLZFeedBack_Start(callArgv, regParam):
	'''
	开启蓝钻转转乐
	'''
	global IS_START
	global ENDTIME
	if IS_START:
		print "GE_EXC,repeat start QQLZFeedBack"
		return
	
	IS_START = True
	ENDTIME = regParam
	cNetMessage.PackPyMsg(QQLZFeedBack_ActiveState, (OPEN_STATE, ENDTIME))
	cRoleMgr.BroadMsg()
	
def QQLZFeedBack_End(callArgv, regParam):
	'''
	结束蓝钻转转乐
	'''
	global IS_START
	if not IS_START:
		print "GE_EXC,close QQLZFeedBack while not open"
		return
	
	IS_START = False
	cNetMessage.PackPyMsg(QQLZFeedBack_ActiveState, (CLOSE_STATE, ENDTIME))
	cRoleMgr.BroadMsg()

def IsQQLZPlatform(role):
	is3366 = role.GetTI64(EnumTempInt64.Is3366)
	isQQGame = role.GetTI64(EnumTempInt64.IsQQGame)
	isWebsite = role.GetTI64(EnumTempInt64.IsWebsite)
	isDevelop = Environment.IsDevelop

	return is3366 or isQQGame or isWebsite or isDevelop

def SyncOldRewardData(role):
	pyobj = role.GetObj(EnumObj.QQLZFeedBackData)
	role.SendObj(QQLZFeedBack_OldRewards,pyobj)

def ClearOldRewardData(role):
	role.SetObj(EnumObj.QQLZFeedBackData,{})
	SyncOldRewardData(role)

def CheckTriggerNextRound(role):
	'''
	检测是否开启下一轮抽奖
	'''
	getedData = role.GetObj(EnumObj.QQLZFeedBackData)
	if len(getedData) >= 12:
		ClearOldRewardData(role)
		#随机一套奖励
		rewardGroupID = QQLZFeedBackConfig.GetRandomGroup(role.GetI8(EnumInt8.QQLZFeedBackRewardGroup))
		role.SetI8(EnumInt8.QQLZFeedBackRewardGroup,rewardGroupID)
		return True
	else:
		return False


def GoNextRound(role):
	ClearOldRewardData(role)
	#随机一套奖励
	rewardGroupID = QQLZFeedBackConfig.GetRandomGroup(role.GetI8(EnumInt8.QQLZFeedBackRewardGroup))
	role.SetI8(EnumInt8.QQLZFeedBackRewardGroup,rewardGroupID)

#=========消息处理===========
def OnLottery(role, param):
	'''
	蓝钻回馈大礼_请求抽奖
	@param role:
	@param param:
	'''

	if not IS_START:
		return
	
	if not IsQQLZPlatform(role):
		return

	if role.GetLevel() < EnumGameConfig.QQLZFeedBack_NeedLevel:
		return
	
	#剩余抽奖次数不足
	kaiTongTimes = role.GetI8(EnumInt8.QQLanZuanKaiTongTimes)
	usedTimes = role.GetI8(EnumInt8.QQLZFeedBackTimes)
	if usedTimes >= kaiTongTimes:
		return

	if CheckTriggerNextRound(role):
		return

	#随机一次奖励
	reward = QQLZFeedBackConfig.GetRandomOne(role)
	rewardId,(coding,cnt) = reward

	times = 1
	#活动首冲
	if role.GetI1(EnumInt1.QQLzFeedBackFirstrecharge):
		times = 2

	getedData = role.GetObj(EnumObj.QQLZFeedBackData)
	if rewardId in getedData:
		print "GE_EXC,repeat random rewardId in QQLZFeedBack.OnLottery"
		return
	with Tra_QQLZFeebBack_Lottery:
		#增加已抽奖次数
		role.IncI8(EnumInt8.QQLZFeedBackTimes, 1)
		role.SetI1(EnumInt1.QQLzFeedBackFirstrecharge,False)
		getedData[rewardId] = times
		#同步并等待回调
		role.SendObjAndBack(QQLZFeedBack_LotteryResult, (rewardId,times), 8, LotteryCallBack, (role.GetRoleID(), coding, cnt , times))
		
def LotteryCallBack(role, callargv, regparam):
	'''
	抽奖回调
	'''
	roleId, coding, cnt, times = regparam
	if not roleId or not coding or not cnt:
		print "GE_EXC, QQLZFeedBack error regparam:roleId(%s), coding(%s), cnt(%s)" % (roleId, coding, cnt)
		return
	
	Call.LocalDBCall(roleId, RealAward, (coding, cnt, times))
	
def RealAward(role, param):
	'''
	抽奖实际获得处理
	'''
	coding, cnt , times= param

	tips = GlobalPrompt.Reward_Tips

	with Tra_QQLZFeebBack_Lottery:
		#获得物品
		while(times > 0):
			role.AddItem(coding, cnt)
			tips += GlobalPrompt.Item_Tips % (coding,cnt)
			
			times -= 1

	role.Msg(2, 0, tips)

	SyncOldRewardData(role)
	#尝试触发下一套奖励
	CheckTriggerNextRound(role)

def OpenPanel(role, param):
	'''
	客户端请求打开界面
	@param role:
	@param param:
	'''
	#同步已领取列表给客户端
	if IsQQLZPlatform(role):
		SyncOldRewardData(role)

def OnChangeReward(role,param):
	'''
	更换奖励
	'''
	if IsQQLZPlatform(role):
		GoNextRound(role)

#===========玩家事件=============
def OnInitRolePyObj(role, param = None):
	'''
	初始化玩家obj
	@@@此时数据已经载入,不能覆盖
	'''
	pyobj = role.GetObj(EnumObj.QQLZFeedBackData)

def OnSyncRoleOtherData(role, param):
	if not IS_START:
		return

	role.SendObj(QQLZFeedBack_ActiveState, (OPEN_STATE, ENDTIME))

def AfterLogin(role, param):
	'''
	角色相关数据初始化
	'''
	#角色当前奖励组
	if role.GetI8(EnumInt8.QQLZFeedBackRewardGroup) == 0:
		role.SetI8(EnumInt8.QQLZFeedBackRewardGroup,1)

def OnQQLzTimesMayChanged(role, param):
	'''
	角色蓝钻开通次数改变
	@@@ old,new = param 注意old与new可能相等
	'''
	global IS_START
	if not IS_START:
		return

	old_times,new_times = param

	#首次开通
	if old_times == 0 and new_times > 0:
		role.SetI1(EnumInt1.QQLzFeedBackFirstrecharge,True)

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_AfterLoadSucceed, Initialize)
		#事件
		Event.RegEvent(Event.Eve_InitRolePyObj, OnInitRolePyObj)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_QQLZTimesMayChanged, OnQQLzTimesMayChanged)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQLZFeedBack_OnLottery", "蓝钻回馈大礼请求抽奖"), OnLottery)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQLZFeedBack_OpenPanel", "蓝钻回馈大礼请求打开界面"), OpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQLZFeedBack_ChangeReward", "蓝钻回馈大礼更换奖励"), OnChangeReward)
