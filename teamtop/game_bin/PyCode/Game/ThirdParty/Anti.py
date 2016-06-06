#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.Anti")
#===============================================================================
# 防沉迷
#===============================================================================
import cDateTime
import cRoleMgr
import Environment
from Common.Other import GlobalPrompt
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from ComplexServer.API import GlobalHttp
from Game import RTF
from Game.Role import Event
from Game.Role.Data import EnumInt32, EnumTempObj, EnumInt16, EnumTempInt64, EnumInt8

ANTI_UNCOMMITTED = 0
ANTI_NONAGE = 1
ANTI_PASS = 2

PromptOnlineMins = set([60,120,150,170,175])

TickTockMins = 1
OneMinuteSec = 60
OneHourSec = 3600 
ThreeHourMins = 180
FiveHourSecs = 18000

NT_VertifyPass 		= 1		#成功提交了满18的认证
NT_VertifyNonage 	= 2		#成功提交了没有满18的认证
NT_CountDown 		= 3		#强制离线倒计时提示
NT_UnVertify 		= 4		#登录or启动防沉迷时候 同步客户端角色防沉迷状态：未提交
NT_NonAge 			= 5		#登录or启动防沉迷时候 同步客户端角色防沉迷状态：提交未满18岁


if "_HasLoad" not in dir():
	#是否开启防沉迷标志
	ANTI_FLAG = False
	
	#防沉迷_通知 根据发的数据表示不同信息
	#1-未认证提示认证
	Anti_Notify_S = AutoMessage.AllotMessage("Anti_Notify_S", "防沉迷_通知")
	
	Tra_Anti_Vertify = AutoLog.AutoTransaction("Tra_Anti_Vertify", "防沉迷_认证")
	
	Tra_Anti_GlobalVertified = AutoLog.AutoTransaction("Tra_Anti_GlobalVertified", "防沉迷_全局认证同步")
	
	Tra_Anti_SystemVertify = AutoLog.AutoTransaction("Tra_Anti_SystemVertify", "防沉迷_系统自动认证")
	
	
#防沉迷控制start
@RTF.RegFunction
def AntiOn_off(param):
	'''
	防沉迷控制
	@param param:0-关闭 1-开启 
	'''
	if not Environment.HasLogic:
		return
	
	if not (Environment.IsDevelop or Environment.EnvIsQQ()):
		return
	
	global ANTI_FLAG
	#重复开启或者重复关闭 无视
	if (ANTI_FLAG and param) or (not ANTI_FLAG and not param):
		print "GE_EXC, repeat set Anti-addiction flag"
		return
	
	if param:
		ANTI_FLAG = True
		ActivateAnti()
	else:
		ANTI_FLAG = False
		FreezeAnti()


def ActivateAnti():
	'''
	开启防沉迷调用  根据在线玩家防沉迷状态 若已认证 则不处理 若未认证 注册防沉迷tick
	'''		
	for role in cRoleMgr.GetAllRole():
		if role.GetVIP() >= 4 or role.GetLevel() >= 60:
			with Tra_Anti_SystemVertify:
				role.SetI8(EnumInt8.AntiVerifiedState, ANTI_PASS)
		antiState = role.GetI8(EnumInt8.AntiVerifiedState)
		if antiState != ANTI_PASS:
			loginInfo = role.GetTempObj(EnumTempObj.LoginInfo)
			account = loginInfo["account"]	
			GlobalHttp.GetAntiData(account, DataBack_AfterLogin, role.GetRoleID())
		else:
			pass
			
		
def FreezeAnti():
	'''
	关闭防沉迷  注销在线玩家防沉迷tick
	'''
	for role in cRoleMgr.GetAllRole():
		ShutAndClearRoleAnti(role)
	

#客户端请求 start
def OnVerify(role, msg):
	'''
	防沉迷_请求认证
	@param msg: userName, idCard, antiState 姓名、身份证、状态（0-1-2） 
	'''
	if not ANTI_FLAG:
		return
	
	userName, idcard, antiState = msg
	if not (1 <= antiState <= 2):
		return
	
	#此次请求的认证状态不比当前认证状态更权威！ 
	oldState = role.GetI8(EnumInt8.AntiVerifiedState)
	if antiState < oldState:
		return
	
	with Tra_Anti_Vertify:
		#提交认证
		loginInfo = role.GetTempObj(EnumTempObj.LoginInfo)
		account = loginInfo["account"]	
		GlobalHttp.SetAntiData(account, userName, idcard, antiState, None, None)
		#直接设置本角色认证状态
		role.SetI8(EnumInt8.AntiVerifiedState, antiState)
		#若是通过认证 清除防沉迷统计数据
		if antiState == ANTI_PASS:
			ShutAndClearRoleAnti(role)
		else:
			#此时相当于提交了未满18岁的认证 不影响之前防沉迷进度
			pass
	
	#分别提示
	if antiState == ANTI_PASS:
		#通过认证
		role.SendObj(Anti_Notify_S, NT_VertifyPass)
	else:
		#未满18岁
		role.SendObj(Anti_Notify_S, NT_VertifyNonage)
	

#防沉迷状态查询返回处理
def DataBack_AfterLogin(response, regparam):
	'''
	登录后查询返回
	'''
	if not ANTI_FLAG:
		return
	
	#认证数据返回异常
	code, body = response
	if code != 200:
		print "GE_EXC,Anti::DataBack_AfterLogin:: code(%s)" % code
		return
	
	roleId = regparam
	role = cRoleMgr.FindRoleByRoleID(roleId)
	if not role or role.IsKick() or role.IsLost():
		return
	
	antiState = int(body)
	if antiState == ANTI_PASS:
		with Tra_Anti_GlobalVertified:
			ShutAndClearRoleAnti(role)
			role.SetI8(EnumInt8.AntiVerifiedState, ANTI_PASS)
	else:
		if antiState == ANTI_NONAGE:
			with Tra_Anti_GlobalVertified:
				role.SetI8(EnumInt8.AntiVerifiedState, ANTI_NONAGE)
		ExecuteRoleAnti(role)


#辅助 start
def ClearTodayAntiData(role, param = None):
	'''
	清除角色今日防沉迷数据
	'''		
	role.SetI16(EnumInt16.AntiOnlineMinCnt, 0)
	role.SetI32(EnumInt32.AntiUnlockTimestamp, 0)


def ShutAndClearRoleAnti(role, param = None):
	'''
	清除防沉迷统计数据 并且关闭防沉迷tick
	'''
	ClearTodayAntiData(role)
	ShutDownAntiTick(role)
	
	
def ShutDownAntiTick(role, parm = None):
	'''
	关闭角色防沉迷计时器
	'''
	tickId = role.GetTI64(EnumTempInt64.AntiTickId)
	if tickId:
		role.UnregTick(tickId)
		role.SetTI64(EnumTempInt64.AntiTickId, 0)


def ExecuteRoleAnti(role, param = None):
	'''
	根据角色防沉迷统计数据 执行防沉迷逻辑
	'''	
	if not role or role.IsLost() or role.IsKick():
		return
	
	if not ANTI_FLAG:
		return
	
	#再次确保不会处理已认证角色
	antiState = role.GetI8(EnumInt8.AntiVerifiedState)
	if antiState == ANTI_PASS:
		return
	
	onlineMins = role.GetI16(EnumInt16.AntiOnlineMinCnt)
	if onlineMins >= ThreeHourMins:
		#有效在线超过3个小时
		unlockTS = role.GetI32(EnumInt32.AntiUnlockTimestamp)
		nowSecs = cDateTime.Seconds()
		if nowSecs < unlockTS:
			#未达到超时自动解锁时间
			cdMins = ((unlockTS - nowSecs + OneMinuteSec - 1) / OneMinuteSec)
			role.RegTick(5, KickRoleByAnti, cdMins)
			return
		else:
			ClearTodayAntiData(role)
	
	#启动tick
	role.SetTI64(EnumTempInt64.AntiTickId, role.RegTick(OneMinuteSec, AntiTickTock))
	
	#强制离线倒计时提示
	if onlineMins in PromptOnlineMins:
		role.SendObj(Anti_Notify_S, NT_CountDown)
	
	#分别提示
	if antiState == ANTI_UNCOMMITTED and role.GetLevel() >= 30:
		role.SendObj(Anti_Notify_S, NT_UnVertify)


def KickRoleByAnti(role, calArgvs = None, regParam = None):
	'''
	防沉迷强制离线
	'''
	role.Kick(True, GlobalPrompt.Anti_Kick % regParam)

def AntiTickTock(role, calArgvs, regParam):
	'''
	防沉迷计时器
	'''
	if not role or (role.IsLost() or role.IsKick()):
		return
	
	if not ANTI_FLAG:
		return
	
	#统计防沉迷期间在线时间
	role.IncI16(EnumInt16.AntiOnlineMinCnt, TickTockMins)
	#检测处理
	onlineMins = role.GetI16(EnumInt16.AntiOnlineMinCnt)
	if onlineMins >= ThreeHourMins:
		nowSecs = cDateTime.Seconds()
		role.SetI32(EnumInt32.AntiUnlockTimestamp, nowSecs + FiveHourSecs)
		role.Kick(True, 0)
	else:
		role.SetTI64(EnumTempInt64.AntiTickId, role.RegTick(OneMinuteSec, AntiTickTock))
		if onlineMins in PromptOnlineMins:
			role.SendObj(Anti_Notify_S, NT_CountDown)

		
#事件 start
def OnSyncRoleData(role, param):
	'''
	角色上线完毕之后检测防沉迷状态 
	1.若满足沉迷 则kick 
	2.若未认证 则激活个人防沉迷tick
	'''
	#未开启防沉迷
	if not ANTI_FLAG:
		return
	
	#优化 VIP>=4 or roleLevel >= 60 直接设置为成年认证用户
	if role.GetVIP() >= 4 or role.GetLevel() >= 60:
		with Tra_Anti_SystemVertify:
			role.SetI8(EnumInt8.AntiVerifiedState, ANTI_PASS)
	
	#保存在角色的验证状态
	antiVerifiedState = role.GetI8(EnumInt8.AntiVerifiedState)
	if antiVerifiedState != ANTI_PASS:
		#查询全局认证数据 回调再处理
		loginInfo = role.GetTempObj(EnumTempObj.LoginInfo)
		account = loginInfo["account"]	
		GlobalHttp.GetAntiData(account, DataBack_AfterLogin, role.GetRoleID())

if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.IsDevelop or Environment.EnvIsQQ()):
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleData)
		Event.RegEvent(Event.Eve_RoleDayClear, ClearTodayAntiData)
		Event.RegEvent(Event.Eve_ClientLost, ShutDownAntiTick)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Anti_OnVerify", "防沉迷_请求认证"), OnVerify)