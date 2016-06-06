#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.FB.EvilHole")
#===============================================================================
# 恶魔深渊
#===============================================================================
import cDateTime
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Role import Event, Status
from Game.Role.Data import EnumObj, EnumTempInt64, EnumInt1, EnumTempObj
from Game.FB import EvilHoleConfig
from Game.Scene import EvilHoleMirror
from Game.DailyDo import DailyDo
from Game import GlobalMessage


if "_HasLoad" not in dir():
	Tra_EvilHole_Join = AutoLog.AutoTransaction("Tra_EvilHole_Join", "进入恶魔深渊")
	Tra_EvilHole_SaoDang = AutoLog.AutoTransaction("Tra_EvilHole_SaoDang", "扫荡恶魔深渊")
	Tra_EvilHole_Cancle_SaoDang = AutoLog.AutoTransaction("Tra_EvilHole_Cancle_SaoDang", "取消扫荡恶魔深渊")
	Tra_EvilHole_fast_SaoDang = AutoLog.AutoTransaction("Tra_EvilHole_fast_SaoDang", "快速扫荡恶魔深渊")
	Tra_EvilHole_SaoDangReward 	= AutoLog.AutoTransaction("Tra_EvilHole_SaoDangReward", "领取恶魔深渊扫荡奖励")
	Tra_EvilHole_BoxReward 	= AutoLog.AutoTransaction("Tra_EvilHole_BoxReward", 	"领取恶魔深渊宝箱奖励")



def CheckStarColorCode(role, needStar, needColorCode):
	#检测是否有大于等级这个星级同时大于等于这个颜色编码的记录
	sg_dict = role.GetObj(EnumObj.StarColor_Dict)
	for star, maxColorCode in sg_dict.iteritems():
		if star < needStar:
			continue
		if maxColorCode < needColorCode:
			continue
		return True
	return False


def JoinEvilHole(role, msg):
	'''
	请求进入恶魔深渊
	@param role:
	@param msg:
	'''
	index = msg
	#进入恶魔深渊
	evilHoleCfg = EvilHoleConfig.EvilHoleCfg_Dict.get(index)
	if not evilHoleCfg:
		return
	
	if not Status.CanInStatus(role, EnumInt1.ST_InMirror):
		return
	
	if role.GetObj(EnumObj.EvilHold_SaoDangData):
		#正在扫荡中
		return
	#体力
	if role.GetTiLi() < EnumGameConfig.EvilHoleNeedTiLi:
		return
	
	if index not in role.GetObj(EnumObj.EvilHole_Star):
		#没有打过，重新判断进入条件
		#等级条件不满足
		if role.GetLevel() < evilHoleCfg.needLevel:
			return
		
		if evilHoleCfg.needPassIndex:
			#不达到前一个通关层的条件
			if evilHoleCfg.needPassIndex not in role.GetObj(EnumObj.EvilHole_Star):
				return
		#神将品阶
		if evilHoleCfg.needStar != 0:
			if not CheckStarColorCode(role, evilHoleCfg.needStar, evilHoleCfg.needColorCode):
				return
	else:
		#已经有挑战过，不用判断剩余的进入条件
		pass
	
	with Tra_EvilHole_Join:
		#扣除体力
		role.DecTiLi(EnumGameConfig.EvilHoleNeedTiLi)
		#进入
		em = EvilHoleMirror.EvilHoleMirror(role, evilHoleCfg)
		if em.createOk is True:
			em.AfterJoinRole()
		
		#每日必做 -- 恶魔深渊
		Event.TriggerEvent(Event.Eve_DoDailyDo, role, (DailyDo.Daily_EH, 1))

	#版本判断
	if Environment.EnvIsNA():
		#开服活动
		kaifuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
		kaifuActMgr.inc_consume_tili(EnumGameConfig.EvilHoleNeedTiLi)

def SaoDang(role, msg):
	'''
	请求扫荡恶魔深渊
	@param role:
	@param msg:
	'''
	index, times = msg
	if times < 1 :
		return
	starDict = role.GetObj(EnumObj.EvilHole_Star)
	if index not in starDict:
		return
	
	saoDangDict = role.GetObj(EnumObj.EvilHold_SaoDangData)
	if saoDangDict:
		#正在扫荡中
		return
	
	#判断体力
	needTiLi = EnumGameConfig.EvilHoleNeedTiLi * times
	if role.GetTiLi() < needTiLi:
		return
	
	with Tra_EvilHole_SaoDang:
		role.DecTiLi(needTiLi)
		
	#版本判断
	if Environment.EnvIsNA():
		#开服活动
		kaifuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
		kaifuActMgr.inc_consume_tili(needTiLi)
	
	if role.IsMonthCard():
		#月卡无CD扫荡
		role.SetObj(EnumObj.EvilHold_SaoDangData, { 0 : index, 1 : times, 2 : 0, 3 : 0})
		role.SendObj(EH_S_SaoDangData, role.GetObj(EnumObj.EvilHold_SaoDangData))
		#每日必做 -- 恶魔深渊
		Event.TriggerEvent(Event.Eve_DoDailyDo, role, (DailyDo.Daily_EH, times))
		if Environment.EnvIsNA():
			HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
			HalloweenNAMgr.ChallengeEvilHole(times)
		return
	
	times -= 1
	role.SetObj(EnumObj.EvilHold_SaoDangData, { 0 : index, 1 : 0, 2 : times, 3 : cDateTime.Seconds()})

	#缓存TICKID
	role.SetTI64(EnumTempInt64.SaoDangTickId, role.RegTick(EnumGameConfig.EvilHoleSaoDangSec, TickFinishSaoDang, (index, times)))
	
	role.SendObj(EH_S_SaoDangData, role.GetObj(EnumObj.EvilHold_SaoDangData))
	
	
def TickFinishSaoDang(role, callargv, regparam):
	#完成一次扫荡
	#首先清理缓存数据
	role.SetTI64(EnumTempInt64.SaoDangTickId, 0)
	
	#异步数据验证
	saoDangDict = role.GetObj(EnumObj.EvilHold_SaoDangData)
	if not saoDangDict:
		print "GE_EXC saoDangDict null error in TickFinishSaoDang (%s)" % role.GetRoleID()
		return
	
	index, times = regparam
	if index != saoDangDict[0]:
		print "GE_EXC saoDangDict error in TickFinishSaoDang (%s)" % role.GetRoleID()
		return
	if times != saoDangDict[2]:
		print "GE_EXC, TickFinishSaoDang data error ", times , saoDangDict[2]
		return
	
	#清理时间
	saoDangDict[3] = 0
	#完成次数加一。用于发奖
	saoDangDict[1] += 1
	
	#还有次数,继续扫荡
	if times >= 1:
		times -= 1
		#剩余扫荡次数减一
		saoDangDict[2] = times
		#记录开始时间
		saoDangDict[3] = cDateTime.Seconds()
		#开始下一次扫荡
		role.SetTI64(EnumTempInt64.SaoDangTickId, role.RegTick(EnumGameConfig.EvilHoleSaoDangSec, TickFinishSaoDang, (index, times)))
	
	role.SendObj(EH_S_SaoDangData, saoDangDict)
	
	#每日必做 -- 恶魔深渊
	Event.TriggerEvent(Event.Eve_DoDailyDo, role, (DailyDo.Daily_EH, 1))
	
	if Environment.EnvIsNA():
		#通用活动
		HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
		HalloweenNAMgr.ChallengeEvilHole(1)

def CancelSaoDang(role, msg):
	'''
	请求取消扫荡
	@param role:
	@param msg: 
	'''
	tickid = role.GetTI64(EnumTempInt64.SaoDangTickId)
	if not tickid:
		return
	
	role.UnregTick(tickid)
	role.SetTI64(EnumTempInt64.SaoDangTickId, 0)
	
	saoDangDict = role.GetObj(EnumObj.EvilHold_SaoDangData)
	if not saoDangDict:
		print "GE_EXC, error in RequestCancelEvilHoleSaoDang not data"
		return 
	#剩余次数
	times = saoDangDict[2]
	#清理剩余次数
	saoDangDict[2] = 0
	#时间差
	startTime = saoDangDict[3]
	if startTime:
		#清理时间
		saoDangDict[3] = 0
		#还有一次未完成的
		times += 1
	
	if saoDangDict[1] == 0:
		role.SetObj(EnumObj.EvilHold_SaoDangData, {})
		saoDangDict = {}
	with Tra_EvilHole_Cancle_SaoDang:
		#返回体力
		role.IncTiLi(times * EnumGameConfig.EvilHoleNeedTiLi)
	
	role.SendObj(EH_S_SaoDangData, saoDangDict)
	

def GetSaoDangReward(role, msg):
	'''
	请求领取恶魔深渊扫荡奖励
	@param role:
	@param msg:
	'''
	saoDangDict = role.GetObj(EnumObj.EvilHold_SaoDangData)
	if not saoDangDict:
		return
	
	index = saoDangDict[0]
	finishTimes = saoDangDict[1]
	if finishTimes <= 0:
		return
	star = role.GetObj(EnumObj.EvilHole_Star).get(index)
	if not star:
		print "GE_EXC, error in RequestEvilHoleSaoDangReward"
		return
	
	cfg = EvilHoleConfig.EvilHoleRewardDict.get(index)
	if not cfg:
		return
	#清理次数
	saoDangDict[1] = 0
	
	tickid = role.GetTI64(EnumTempInt64.SaoDangTickId)
	if not tickid:
		#全部数据都需要清理掉
		role.SetObj(EnumObj.EvilHold_SaoDangData, {})
		saoDangDict = {}
	
	with Tra_EvilHole_SaoDangReward:
		#奖励
		cfg.RewardRole(role, star, finishTimes)
	
	#同步剩余的扫荡数据
	role.SendObj(EH_S_SaoDangData, saoDangDict)
	
def FastSaoDang(role, msg):
	'''
	请求快速扫荡
	@param role:
	@param msg: 
	'''
	tickid = role.GetTI64(EnumTempInt64.SaoDangTickId)
	if not tickid:
		return
	
	saoDangDict = role.GetObj(EnumObj.EvilHold_SaoDangData)
	if not saoDangDict:
		print "GE_EXC, error in RequestJumpCDAtEvilHole not data"
		return
	
	
	times = saoDangDict[2]
	totalMinutes = times * EnumGameConfig.EvilHoleSaoDangSec / 60
	sec = EnumGameConfig.EvilHoleSaoDangSec - (cDateTime.Seconds() - saoDangDict[3])
	if sec > 0:
		#可以完成的次数加一
		times += 1
		totalMinutes += sec / 60
		if sec % 60 > 0:
			totalMinutes += 1

	if totalMinutes < 1:
		print "GE_EXC, error in RequestJumpCDAtEvilHole totalMinutes < 1"
		return
	
	needRmb = EnumGameConfig.FastSaoDangNeedRMB * totalMinutes
	if role.GetRMB() < needRmb:
		return
	
	with Tra_EvilHole_fast_SaoDang:
		role.DecRMB(needRmb)
	
		role.UnregTick(tickid)
		role.SetTI64(EnumTempInt64.SaoDangTickId, 0)
		saoDangDict[3] = 0
		saoDangDict[2] = 0
		#完成次数
		saoDangDict[1] += times
		
		#同步剩余的扫荡数据
		role.SendObj(EH_S_SaoDangData, saoDangDict)
		
		#每日必做 -- 恶魔深渊
		Event.TriggerEvent(Event.Eve_DoDailyDo, role, (DailyDo.Daily_EH, times))
		
		if Environment.EnvIsNA():
			#通用活动
			HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
			HalloweenNAMgr.ChallengeEvilHole(times)
		
def RequestGetBoxRewrad(role, msg):
	'''
	请求领取3星宝箱奖励
	@param role:
	@param msg: [backId, index]
	'''
	backId, index = msg
	star = role.GetObj(EnumObj.EvilHole_Star).get(index)
	if not star or star < 3:
		return
	starRewardData = role.GetObj(EnumObj.EvilHole_StarBoxReward)[1]
	if index in starRewardData:
		return
	
	cfg = EvilHoleConfig.EvilHoleRewardDict.get(index)
	if not cfg:
		return
	
	with Tra_EvilHole_BoxReward:
		starRewardData.add(index)
		cfg.BoxReward(role)
	
	role.CallBackFunction(backId, index)


def BuyMonthOrYearCard(role, param):
	#购买月卡的时候快速结束扫荡
	tickid = role.GetTI64(EnumTempInt64.SaoDangTickId)
	if not tickid:
		return
	
	saoDangDict = role.GetObj(EnumObj.EvilHold_SaoDangData)
	if not saoDangDict:
		print "GE_EXC, error in EvilHole BuyMonthOrYearCard not data"
		return
	
	times = saoDangDict[2]
	totalMinutes = times * EnumGameConfig.EvilHoleSaoDangSec / 60
	sec = EnumGameConfig.EvilHoleSaoDangSec - (cDateTime.Seconds() - saoDangDict[3])
	if sec > 0:
		#可以完成的次数加一
		times += 1
		totalMinutes += sec / 60
		if sec % 60 > 0:
			totalMinutes += 1

	if totalMinutes < 1:
		print "GE_EXC, error in EvilHole BuyMonthOrYearCard totalMinutes < 1"
		return

	role.UnregTick(tickid)
	role.SetTI64(EnumTempInt64.SaoDangTickId, 0)
	saoDangDict[3] = 0
	saoDangDict[2] = 0
	#完成次数
	saoDangDict[1] += times
	
	#同步剩余的扫荡数据
	role.SendObj(EH_S_SaoDangData, saoDangDict)
	
	#每日必做 -- 恶魔深渊
	Event.TriggerEvent(Event.Eve_DoDailyDo, role, (DailyDo.Daily_EH, times))
	#北美通用活动
	if Environment.EnvIsNA():
		HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
		HalloweenNAMgr.ChallengeEvilHole(times)
		
def AfterLogin(role, param):
	#尝试继续扫荡
	saodangData = role.GetObj(EnumObj.EvilHold_SaoDangData)
	if not saodangData:
		return
	#上次开始时间
	oldSec = saodangData[3]
	#如果上次开始扫荡的时间为0，表示没有开始扫荡
	if oldSec == 0:
		return
	#当前时间
	nowSec = cDateTime.Seconds()
	#时间差
	passTimeSec = nowSec - oldSec
	
	if passTimeSec < EnumGameConfig.EvilHoleSaoDangSec:
		tickSec = EnumGameConfig.EvilHoleSaoDangSec - passTimeSec
		#继续扫荡
		role.SetTI64(EnumTempInt64.SaoDangTickId, role.RegTick(tickSec, TickFinishSaoDang, (saodangData[0], saodangData[2])))
		return
	
	#还剩余未开始过的扫荡次数
	unFinishTimes = saodangData[2]
	#加上已经开始未完成的次数,就是总的未完成次数
	unFinishTimes += 1
	
	if unFinishTimes <= 1:
		#没有剩余的扫荡次数了，而且这次扫荡已经完成了，停止扫荡
		saodangData[3] = 0
		saodangData[1] += 1
		return
	
	#这段时间可以完成的扫荡次数
	finishTimes = passTimeSec / EnumGameConfig.EvilHoleSaoDangSec
	if finishTimes >= unFinishTimes:
		#全部完成
		saodangData[3] = 0
		saodangData[2] = 0
		saodangData[1] += unFinishTimes
	else:
		#完成一部分
		#注意，下面其实有多步计算的
		#用 saodangData[2] 剩余次数减去额外完成的次数(不包括已经开始的那一次)
		#即 saodangData[2] -= (finishTimes - 1)
		#然后又要付出一次用于马上开始的新的扫荡
		#saodangData[2] -= 1
		#所以有 saodangData[2] -= (finishTimes - 1 + 1)
		#即saodangData[2] -= finishTimes
		saodangData[3] = nowSec - (passTimeSec % EnumGameConfig.EvilHoleSaoDangSec)
		saodangData[2] -= finishTimes
		saodangData[1] += finishTimes
		
		tickSec = EnumGameConfig.EvilHoleSaoDangSec - passTimeSec % EnumGameConfig.EvilHoleSaoDangSec
		role.SetTI64(EnumTempInt64.SaoDangTickId, role.RegTick(tickSec, TickFinishSaoDang, (saodangData[0], saodangData[2])))


def SyncRoleOtherData(role, param):
	role.SendObj(EH_S_StarData, role.GetObj(EnumObj.EvilHole_Star))
	role.SendObj(EH_S_StarRewardData, role.GetObj(EnumObj.EvilHole_StarBoxReward)[1])
	role.SendObj(EH_S_SaoDangData, role.GetObj(EnumObj.EvilHold_SaoDangData))
	role.SendObj(GlobalMessage.Msg_S_StarColorCode, role.GetObj(EnumObj.StarColor_Dict))
	
if "_HasLoad" not in dir():
	#事件注册
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		Event.RegEvent(Event.Eve_BuyMonthOrYearCard, BuyMonthOrYearCard)
	
		EH_S_SaoDangData = AutoMessage.AllotMessage("EH_S_SaoDangData", "同步当前恶魔深渊扫荡数据")
		EH_S_StarData = AutoMessage.AllotMessage("EH_S_StarData", "同步当前恶魔深渊通关星级数据")
		EH_S_StarRewardData = AutoMessage.AllotMessage("EH_S_StarRewardData", "同步当前恶魔深渊已经领取3星宝箱的数据")
		
		#客户端请求消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("EH_Join", "请求进入恶魔深渊"), JoinEvilHole)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("EH_GetBoxRewrad", "恶魔深渊领取3星宝箱奖励"), RequestGetBoxRewrad)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("EH_FastSaoDang", "恶魔深渊快速扫荡"), FastSaoDang)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("EH_CancelSaoDang", "请求取消恶魔深渊扫荡扫荡"), 	CancelSaoDang)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("EH_GetSaoDangReward", "请求领取恶魔深渊扫荡奖励"),GetSaoDangReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("EH_SaoDang", "请求恶魔深渊扫荡挂机"),SaoDang)
		