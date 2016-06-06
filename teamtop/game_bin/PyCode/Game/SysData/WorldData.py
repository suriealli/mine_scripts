#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.SysData.WorldData")
#===============================================================================
# 游戏世界数据
#===============================================================================
import cDateTime
import cNetMessage
import cProcess
import cRoleMgr
import cComplexServer
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumSysData, GlobalPrompt
from Game.Persistence import Contain
from Game.Role import Event
from Game import RTF




@RTF.RegFunctionBack
def SetKaiFuDateTime(y, m, d, H = 0, M = 0, S = 0):
	'''
	设置开服时间(运维)
	@param y:年
	@param m:月
	@param d:日
	@param H:时
	@param M:分
	@param S:秒
	'''
	import datetime
	WD[EnumSysData.KaiFuKey] = datetime.datetime(y, m, d, H, M, S)
	
	old_kaifuDay = GetWorldKaiFuDay()
	#更新当前的开服天数
	AfterSetKaiFuTime()
	#触发其他事件
	Event.TriggerEvent(Event.Eve_AfterSetKaiFuTime, None, (old_kaifuDay, GetWorldKaiFuDay()))
	#强制保存数据
	WD.SaveData()
	
@RTF.RegFunctionBack
def SetEndLimitTime(y, m, d, H = 0, M = 0, S = 0):
	'''
	设置新服开放普通号的时间(运维)
	@param y:年
	@param m:月
	@param d:日
	@param H:时
	@param M:分
	@param S:秒
	'''
	import time
	import datetime
	dt = datetime.datetime(y, m, d, H, M, S)
	Secs = int(time.mktime(dt.timetuple()))
	WD[EnumSysData.OpenLimitTimes] = Secs
	CheckLimitLogin()

def AfterLoad():
	#载入数据后，初始化
	if EnumSysData.KaiFuKey not in WD:
		WD[EnumSysData.KaiFuKey] = cDateTime.Now()
	
	#初始化开服天数
	if EnumSysData.KaiFuDay not in WD:
		WD[EnumSysData.KaiFuDay] = 1
	else:
		#尝试修正开服天数
		kaifutime = WD.get(EnumSysData.KaiFuKey)
		now = cDateTime.Now().date()
		WD[EnumSysData.KaiFuDay] = (now - kaifutime.date()).days + 1
	
	if EnumSysData.WorldLevelKey not in WD:
		WD[EnumSysData.WorldLevelKey] = 0
		
	if EnumSysData.WorldBuffLevel not in WD:
		WD[EnumSysData.WorldBuffLevel] = 0
	#初始化两个阵营人数
	if EnumSysData.CampLeftKey not in WD:
		WD[EnumSysData.CampLeftKey] = 0
	if EnumSysData.CampRightKey not in WD:
		WD[EnumSysData.CampRightKey] = 0
	
	#限制登录时间
	if EnumSysData.OpenLimitTimes not in WD:
		WD[EnumSysData.OpenLimitTimes] = 0
	else:
		CheckLimitLogin()

	#初始化微信关注人数
	if EnumSysData.WeiXinAttenionCnt not in WD:
		WD[EnumSysData.WeiXinAttenionCnt] = 0
	
	#初始化全服结婚对数
	if EnumSysData.MarryCnt not in WD:
		WD[EnumSysData.MarryCnt] = 0
	
	#合服天数
	if EnumSysData.HeFuDay not in WD:
		WD[EnumSysData.HeFuDay] = 0
		
	
	#初始化许愿池许愿次数
	if EnumSysData.WishPoolCnt not in WD:
		WD[EnumSysData.WishPoolCnt] = 0
	
	#初始化金币副本次数
	if EnumSysData.GoldMirrorCnt_1 not in WD:
		WD[EnumSysData.GoldMirrorCnt_1] = 0
	if EnumSysData.GoldMirrorCnt_2 not in WD:
		WD[EnumSysData.GoldMirrorCnt_2] = 0
	
	#服务器名字
	if EnumSysData.ServerName not in WD:
		WD[EnumSysData.ServerName] = cProcess.ProcessID
	
	if EnumSysData.GameServiceQQ not in WD:
		WD[EnumSysData.GameServiceQQ] = ""
	
	#元旦购物节积分
	if EnumSysData.HoilyShoppingScore not in WD:
		WD[EnumSysData.HoilyShoppingScore] = 0
		
	#跨服个人竞技场区域ID
	if EnumSysData.KuaFuJJCZoneId not in WD:
		WD[EnumSysData.KuaFuJJCZoneId] = 0
		
	#跨服个人竞技场版本ID
	if EnumSysData.KuaFuJJCVersionId not in WD:
		WD[EnumSysData.KuaFuJJCVersionId] = 0
	
	if EnumSysData.LanternRankServerType not in WD:
		WD[EnumSysData.LanternRankServerType] = None
	
	#魅力派对活动指定的服务器类型
	if EnumSysData.GlamourRankServerType not in WD:
		WD[EnumSysData.GlamourRankServerType] = 0
	
	#魅力派对活动指定的服务器类型
	if EnumSysData.QingMingRankServerType not in WD:
		WD[EnumSysData.QingMingRankServerType] = 0
	
	#至尊周卡公会副本替身组队是否开启
	if EnumSysData.SuperCardsUnionFB not in WD:
		WD[EnumSysData.SuperCardsUnionFB] = 0
	
	#王者积分活动指定的服务器类型
	if EnumSysData.WangZheRankServerType not in WD:
		WD[EnumSysData.WangZheRankServerType] = 0
	
	#神树密境神树等级、经验
	if EnumSysData.ShenshuLevel not in WD:
		WD[EnumSysData.ShenshuLevel] = 1
	if EnumSysData.ShenshuExp not in WD:
		WD[EnumSysData.ShenshuExp] = 0

	if EnumSysData.SuperTurnTableLotteryCount not in WD:
		WD[EnumSysData.SuperTurnTableLotteryCount] = 0
	
	#春节活跃有礼天数
	if EnumSysData.ChunJieActiveDays not in WD:
		WD[EnumSysData.ChunJieActiveDays] = 0
	
	from ComplexServer.Plug import Switch
	
	#合服服务器id集合
	if EnumSysData.LocalServerIDs not in WD:
		WD[EnumSysData.LocalServerIDs] = Switch.LocalServerIDs
	
	if EnumSysData.SecretGardenServerCnt not in WD:
		WD[EnumSysData.SecretGardenServerCnt] = 0
	
	
	#最后处理
	# 处理合服
	if WD.get(EnumSysData.HeFuCnt, 0) != Switch.MergeZoneCount:
		WD[EnumSysData.HeFuCnt] = Switch.MergeZoneCount
		WD[EnumSysData.HeFuKey] = cDateTime.Now()
		WD[EnumSysData.HeFuDay] = 1
		#合服后更新本服进程id集合
		WD[EnumSysData.LocalServerIDs] = Switch.LocalServerIDs
		# 触发合服事件
		Event.TriggerEvent(Event.Eve_AfterSystemHeFu, None, None)
	#载入数据之后
	Event.TriggerEvent(Event.Eve_AfterLoadWorldData, None, None)
	


def SetKeyValue(key, value):
	if not WD.returnDB:
		return
	WD[key] = value
	
	cNetMessage.PackPyMsg(WorldData_Set, (key, value))
	cRoleMgr.BroadMsg()

def DelKey(key):
	if not WD.returnDB:
		return
	if key not in WD:
		return
	del WD[key]
	cNetMessage.PackPyMsg(WorldData_Del, key)
	cRoleMgr.BroadMsg()

##############################################################################
def GetWorldKaiFuDay():
	#开服天数
	return WD.get(EnumSysData.KaiFuDay, 1) 

def SetWorldKaiFuDay(day):
	#设置开服天数
	SetKeyValue(EnumSysData.KaiFuDay, day)

def IsHeFu():
	#是否已经合服
	return WD.get(EnumSysData.HeFuCnt, 0) > 0

def GetHeFuCnt():
	#获取合服记录次数
	return WD.get(EnumSysData.HeFuCnt, 0)


def GetHeFuDay():
	#获取合服天数
	return WD.get(EnumSysData.HeFuDay, 0)

def SetHeFuDay(day):
	#设置合服天数
	SetKeyValue(EnumSysData.HeFuDay, day)

def GetWorldLevel():
	#获取世界等级
	return WD.get(EnumSysData.WorldLevelKey, 0)

def SetWorldLevel(level):
	#设置世界等级
	SetKeyValue(EnumSysData.WorldLevelKey, level)

def GetWorldBuffLevel():
	#获取世界BUFF等级
	return WD.get(EnumSysData.WorldBuffLevel, 0)

def SetWorldBuffLevel(level):
	#设置世界BUFF等级
	SetKeyValue(EnumSysData.WorldBuffLevel, level)

def GetWorldMaxFBID():
	#最大副本通关ID
	return WD.get(EnumSysData.FBActiveID, 0)

def SetWorldMaxFBID(fbId):
	##最大副本通关ID
	WD[EnumSysData.FBActiveID] = fbId

def SetWeiXinAttentionCnt(cnt):
	#设置微信关注人数
	SetKeyValue(EnumSysData.WeiXinAttenionCnt, cnt)
	
def GetWeiXinAttentionCnt():
	#获取微信关注人数
	return WD.get(EnumSysData.WeiXinAttenionCnt, 0)
	
def SetWishPoolCnt(cnt):
	#设置许愿池许愿次数
	SetKeyValue(EnumSysData.WishPoolCnt, cnt)
	
def GetWishPoolCnt():
	#获取许愿池许愿次数
	return WD.get(EnumSysData.WishPoolCnt, 0)
	
def SetGoldMirrorCnt_1(cnt):
	#设置金币副本1次数
	SetKeyValue(EnumSysData.GoldMirrorCnt_1, cnt)
	
def GetGoldMirrorCnt_1():
	#获取金币副本1次数
	return WD.get(EnumSysData.GoldMirrorCnt_1, 0)
	
def SetGoldMirrorCnt_2(cnt):
	#设置金币副本2次数
	SetKeyValue(EnumSysData.GoldMirrorCnt_2, cnt)
	
def GetGoldMirrorCnt_2():
	#获取金币副本2次数
	return WD.get(EnumSysData.GoldMirrorCnt_2, 0)

def ClearHoilyShoppingScore():
	#清理元旦购物积分
	if not WD.returnDB:
		return
	enum = EnumSysData.HoilyShoppingScore
	if enum not in WD:
		return
	WD[enum] = 0
	
	cNetMessage.PackPyMsg(WorldData_Set, (enum, 0))
	cRoleMgr.BroadMsg()
	
def IncHoilyShoppingScore(score, scoreList):
	#加元旦购物积分
	if not WD.returnDB:
		return
	enum = EnumSysData.HoilyShoppingScore
	if enum not in WD:
		return
	oldScore = WD[enum]
	newScore = oldScore + score
	WD[enum] = newScore
	
	CheckTips(oldScore, newScore, scoreList)
	
	cNetMessage.PackPyMsg(WorldData_Set, (enum, newScore))
	cRoleMgr.BroadMsg()
	
def CheckTips(oldScore, newScore, scoreList):
	#检查元旦购物积分提示
	for i in scoreList:
		if oldScore >= i:
			continue
		if i > newScore:
			continue
		cRoleMgr.Msg(1, 0, GlobalPrompt.HolidayShoppingTips % i)
		
def GetKuaFuJJCZoneId():
	#获取跨服个人竞技场区域ID
	return WD.get(EnumSysData.KuaFuJJCZoneId, 1) 

def SetKuaFuJJCZoneId(zoneId):
	#设置跨服个人竞技场区域ID
	SetKeyValue(EnumSysData.KuaFuJJCZoneId, zoneId)
	
def GetKuaFuJJCVersionId():
	#获取跨服个人竞技场版本ID
	return WD.get(EnumSysData.KuaFuJJCVersionId, 1) 

def SetKuaFuJJCVersionId(versionId):
	#设置跨服个人竞技场版本ID
	SetKeyValue(EnumSysData.KuaFuJJCVersionId, versionId)

def SetLanternRankServertype(serverType):
	#设置
	SetKeyValue(EnumSysData.LanternRankServerType, serverType)

def SetGlamourRankServerType(serverType):
	#设置魅力排行服务器类型
	SetKeyValue(EnumSysData.GlamourRankServerType, serverType)
		
def SetSpringBServerType(serverType):
	#设置新春最靓丽排行服务器类型
	SetKeyValue(EnumSysData.SpringBRankServerType, serverType)

def SetQingMingRankServerType(serverType):
	#设置魅力排行服务器类型
	SetKeyValue(EnumSysData.QingMingRankServerType, serverType)
	
def SetSuperCardsUnionFB(openOrClose):
	#设置至尊周卡公会副本替身组队开启与关闭
	SetKeyValue(EnumSysData.SuperCardsUnionFB, openOrClose)

def SetWangZheRankServerType(serverType):
	#设置王者积分排行服务器类型
	SetKeyValue(EnumSysData.WangZheRankServerType, serverType)
	
def GetShenshuLevel():
	return WD.get(EnumSysData.ShenshuLevel, 1) 
	
def SetShenshuLevel(shenshuLevel):
	#设置神树密境神树等级
	SetKeyValue(EnumSysData.ShenshuLevel, shenshuLevel)
	
def GetShenshuExp():
	return WD.get(EnumSysData.ShenshuExp, 0) 

def SetShenshuExp(shenshuExp):
	#设置神树密境神树经验
	SetKeyValue(EnumSysData.ShenshuExp, shenshuExp)

def GetSTTLotteryCnt():
	if not WD.returnDB:
		return
		
	return WD.get(EnumSysData.SuperTurnTableLotteryCount,0)

def SetSTTLotteryCnt(lotteryCnt):
	#设置超值转盘抽奖次数
	SetKeyValue(EnumSysData.SuperTurnTableLotteryCount,lotteryCnt)
	
#春节活跃有礼天数
def GetChunJieActiveDays():
	if not WD.returnDB:
		return
	return WD.get(EnumSysData.ChunJieActiveDays, 0)

def SetChunJieActiveDays(Days):
	SetKeyValue(EnumSysData.ChunJieActiveDays, Days)


def GetSecretGardenServerCnt():
	if not WD.returnDB:
		return 
	return WD.get(EnumSysData.SecretGardenServerCnt, 0) 

def SetSecretGardenServerCnt(newCnt):
	SetKeyValue(EnumSysData.SecretGardenServerCnt, newCnt)

def IncSecretGardenServerCnt(incCnt=1):
	SetKeyValue(EnumSysData.SecretGardenServerCnt, GetSecretGardenServerCnt() + incCnt)

	
##############################################################################
def SyncRoleOtherData(role, param):
	if not WD.returnDB:
		return
	role.SendObj(WorldData_Init, WD.data)

def AfterSetKaiFuTime():
	kaifuTime = WD.get(EnumSysData.KaiFuKey)
	now = cDateTime.Now()
	#重新设置开服天数
	SetWorldKaiFuDay((now.date() - kaifuTime.date()).days + 1)

def AfterNewDay():
	#新的一天，开服天数加一
	SetWorldKaiFuDay(GetWorldKaiFuDay() + 1)
	if IsHeFu():
		#已经是合服了
		SetHeFuDay(GetHeFuDay() + 1)

def CheckLimitLogin():
	#检查一下限登录
	nowSec = cDateTime.Seconds()
	openLimits = WD[EnumSysData.OpenLimitTimes]
	if openLimits <= nowSec:
		#已经过了这个时间了，不用开启限制登录了
		return
	#注册开放普通号的tick
	global EndLimitTickId
	if EndLimitTickId:
		print "GE_EXC, repeat CheckLimitLogin cancle old one !"
		cComplexServer.UnregTick(EndLimitTickId)
	#重新关闭一下限制登录
	from Game import Login
	Login.LimitLogin(1)
	EndLimitTickId = cComplexServer.RegTick(openLimits - nowSec, EndLimit, None)

def EndLimit(callargv, regparam):
	#关闭限制登录
	print "EndLimit,,Server Auto Open", cDateTime.Now()
	from Game import Login
	Login.LimitLogin(0)
	global EndLimitTickId
	EndLimitTickId = 0

@RTF.RegFunction
def SetGameServiceQQ(qqnum):
	'''
	设置客服QQ
	@param qqnum:qq
	'''
	global WD
	WD[EnumSysData.GameServiceQQ] = str(qqnum)


if "_HasLoad" not in dir():
	EndLimitTickId = 0
	if Environment.HasLogic or Environment.HasWeb:
		WD = Contain.Dict("world_data", (2038, 1, 1), AfterLoad, isSaveBig = False)
	
	if Environment.HasLogic:
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay, 0)
		
	WorldData_Init = AutoMessage.AllotMessage("WorldData_Init", "初始化世界数据")
	WorldData_Set = AutoMessage.AllotMessage("WorldData_Set", "设置世界数据")
	WorldData_Del = AutoMessage.AllotMessage("WorldData_Del", "删除世界数据")

	#角色登陆
	Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
	
