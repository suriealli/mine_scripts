#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionOnlineGift")
#===============================================================================
# 在线有礼(七夕活动新增)
#===============================================================================
import cRoleMgr
import Environment
from Util import Random
from Game.Role import Event
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig
from Game.Activity import CircularDefine
from Game.Role.Data import EnumInt32, EnumObj, EnumDayInt8, EnumInt8, EnumTempInt64
from Game.Activity.PassionAct import PassionDefine, PassionOnlineGiftConfig, PassionActVersionMgr


if "_HasLoad" not in dir():
	GetCntMin = 60			#每隔60分钟获得一次翻拍次数
	OneMinSec = 60			#每分钟的秒数
	DailyMaxCnt = 2			#每天可以获得翻牌的最大次数
	IsStart = False
	
	#消息
	SyncPassionOnlineGiftOpenCardID = AutoMessage.AllotMessage("SyncPassionOnlineGiftOpenCardID", "同步激情活动在线有礼已翻开卡牌")
	
	#日志
	TraPassionOnlineGiftReward = AutoLog.AutoTransaction("TraPassionOnlineGiftReward", "激情活动在线有礼奖励")
	TraPassionOnlineAddCnt = AutoLog.AutoTransaction("TraPassionOnlineAddCnt", "激情活动在线有礼增加翻牌子次数")


def Start(*param):
	_, activetype = param
	if activetype != CircularDefine.CA_PassionOnlineGift:
		return
	global IsStart
	if IsStart:
		print "GE_EXC, PassionOnlineGift is already started "
		return
	IsStart = True
	
	#更新所有在线玩家 活动相关数据
	for theRole in cRoleMgr.GetAllRole():
		TryStartTick(theRole)
	

def End(*param):
	_, activetype = param
	if activetype != CircularDefine.CA_PassionOnlineGift:
		return
	global IsStart
	if not IsStart:
		print "GE_EXC, PassionOnlineGift is already ended "
		return
	IsStart = False


def RequestGetAward(role, msg):
	'''
	客户端请求获取奖励
	@ param:
	@ msg:
	'''
	#活动未开启
	if IsStart  is False:
		return
	
	#角色身上版本号与当前版本号不一致
	if role.GetI32(EnumInt32.PassionActVersion) != PassionActVersionMgr.PassionVersion:
		print "GE_EXC,role(%s) PassionAct version(%s) not equal to NowVersion(%s)" % (role.GetRoleID(), role.GetI32(EnumInt32.PassionActVersion, PassionActVersionMgr.PassionVersion))
		return
	
	#等级限制
	if role.GetLevel() < EnumGameConfig.PassionOnlineGiftNeedLevel:
		return
	
	if role.GetI8(EnumInt8.PassionOnlineGiftLeftCnt) <= 0:
		return
	
	#发奖
	OnlineGiftDict = role.GetObj(EnumObj.PassionActData).setdefault(PassionDefine.PassionOnlineGift, {})
	#已经获取的奖励索引集合
	HasGotSet = OnlineGiftDict.setdefault(1, set())
	#已经翻开的牌子的编号集合（这个是发给客户端看的）
	HasGotShowDict = OnlineGiftDict.setdefault(2, {})
	
	cardID = msg
	
	if cardID not in xrange(1, 15):
		return
	
	if cardID in HasGotShowDict:
		return
	
	#随机生成器
	randomRate = Random.RandomRate()
	RA = randomRate.AddRandomItem
	for rewardIndex, theconfig in PassionOnlineGiftConfig.OnlineGiftConfigDict.iteritems():
		if rewardIndex in HasGotSet:
			continue
		RA(theconfig.rate, theconfig)
	
	config = randomRate.RandomOne()
	if config is None:
		print "GE_EXC,error while config = randomRate.RandomOne() in PassionOnlineGift %s" % randomRate.randomList
		return
	
	with TraPassionOnlineGiftReward:
		role.DecI8(EnumInt8.PassionOnlineGiftLeftCnt, 1)
		HasGotSet.add(config.rewardIndex)
		HasGotShowDict[cardID] = config.rewardIndex
		role.AddItem(*config.rewardItem)
	
	#同步信息给客户端
	role.SendObj(SyncPassionOnlineGiftOpenCardID, HasGotShowDict)


def RequestOpenPanel(role, msg):
	if IsStart is False:
		return
	if role.GetLevel() < EnumGameConfig.PassionOnlineGiftNeedLevel:
		return
	OnlineGiftDict = role.GetObj(EnumObj.PassionActData).setdefault(PassionDefine.PassionOnlineGift, {})
	HasGotShowDict = OnlineGiftDict.get(2, {})
	role.SendObj(SyncPassionOnlineGiftOpenCardID, HasGotShowDict)


def TryStartTick(role):
	'''
	尝试启动在线计时器
	'''
	#活动非开启
	if not IsStart:
		return
	if role.GetLevel() < EnumGameConfig.PassionOnlineGiftNeedLevel:
		return
	if role.GetDI8(EnumDayInt8.PassionOnlineGiftOnlineMin) >= GetCntMin * DailyMaxCnt:
		return
	
	tickID = role.GetTI64(EnumTempInt64.PassionOnlineGiftTickId)
	if tickID:
		role.UnregTick(tickID)
		
	newTickID = role.RegTick(OneMinSec, CalcOnlineMin, None)
	role.SetTI64(EnumTempInt64.PassionOnlineGiftTickId, newTickID)


def CalcOnlineMin(role, callargv, regparam):
	#有可能角色已经不在了
	if role.IsKick():
		return
	
	if not IsStart:
		role.SetTI64(EnumTempInt64.PassionOnlineGiftTickId, 0)
		return
	
	#在线时间增加一分钟
	if role.GetDI8(EnumDayInt8.PassionOnlineGiftOnlineMin) >= GetCntMin * DailyMaxCnt:
		role.SetTI64(EnumTempInt64.PassionOnlineGiftTickId, 0)
		return
	
	tickID = role.RegTick(OneMinSec, CalcOnlineMin, None)
	role.SetTI64(EnumTempInt64.PassionOnlineGiftTickId, tickID)
	role.IncDI8(EnumDayInt8.PassionOnlineGiftOnlineMin, 1)
	
	#每满半个小时可翻牌子次数加一
	if role.GetDI8(EnumDayInt8.PassionOnlineGiftOnlineMin) % GetCntMin != 0:
		return
	
	with TraPassionOnlineAddCnt:
		role.IncI8(EnumInt8.PassionOnlineGiftLeftCnt, 1)


def OnDailyClear(role, param):
	TryStartTick(role)


def AfterLevelUp(role, param):
	#只有当是从小于30级升级为30级的时候才做这个操作
	if role.GetLevel() != EnumGameConfig.PassionOnlineGiftNeedLevel:
		return
	TryStartTick(role) 


def AfterLogin(role, param):
	TryStartTick(role)

	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross and (Environment.IsDevelop or Environment.EnvIsQQ() or Environment.EnvIsFT() or Environment.EnvIsNA() or Environment.EnvIsTK() or Environment.EnvIsPL()):
		Event.RegEvent(Event.Eve_StartCircularActive, Start)
		Event.RegEvent(Event.Eve_EndCircularActive, End)
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_RoleDayClear, OnDailyClear)
		Event.RegEvent(Event.Eve_AfterLevelUp, AfterLevelUp)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestPassionOnlineGiftOpenPanel", "客户端请求打开激情活动在线有礼面板"), RequestOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestPassionOnlineGiftGetAward", "客户端请求激情活动在线有礼获取奖励"), RequestGetAward)
