#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.PackagePasswd.PackagePasswdMgr")
#===============================================================================
# 背包密码管理
#===============================================================================
import cRoleMgr
import Environment
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumObj, EnumInt1, EnumTempInt64
from ComplexServer.Time.Cron import cDateTime
from Game.Role import Event
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt

if "_HasLoad" not in dir():
	OneWeek = 60 * 60 * 24 * 7
	OneDay = 60 * 60 * 24
	OneHour = 60 * 60
	OneMinute = 60
	#日志
	Tra_UnlockPackage = AutoLog.AutoTransaction("Tra_UnlockPackage", "背包解锁")
	Tra_SetPackagePasswd = AutoLog.AutoTransaction("Tra_SetPackagePasswd", "设置背包加密锁密码")
	Tra_ResetPackagePasswd = AutoLog.AutoTransaction("Tra_ResetPackagePasswd", "重置背包加密锁密码")
	Tra_ClearPackagePasswd = AutoLog.AutoTransaction("Tra_ClearPackagePasswd", "清除背包加密锁密码")
	Tra_RequestClearPackagePasswd = AutoLog.AutoTransaction("Tra_RequestClearPackagePasswd", "清除背包加密锁密码")

def UnlockPackage(role, msg):
	the_passwd = msg
	#没有密码无需解锁
	if not role.GetI1(EnumInt1.PackageHasPasswd):
		return
	#如果密码不匹配
	if the_passwd != role.GetObj(EnumObj.PackagePasswd)['passwd']:
		role.Msg(2, 0, GlobalPrompt.PackagePasswd_UnlockFailedTip)
		return
	#设置背包解锁状态
	with Tra_UnlockPackage:
		role.SetTI64(EnumTempInt64.PackageIsUnlock, 1)
		# 记录玩家背包本次解锁输入的密码
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveUnlockPackage, the_passwd)
	role.Msg(4, 0, GlobalPrompt.PackagePasswd_UnlockOkayTip)

def ResetPackagePasswd(role, msg):
	'''
	重设加密锁密码
	@param role:
	@param msg:
	'''
	o_passwd , n_passwd = msg
	#没有密码不能重设 
	if not role.GetI1(EnumInt1.PackageHasPasswd):
		return
	#旧的密码
	if 'reset_time' in role.GetObj(EnumObj.PackagePasswd):
		role.Msg(2, 0, GlobalPrompt.PackagePasswd_PasswdCleanning)
		return
	old_passwd_local = role.GetObj(EnumObj.PackagePasswd).get('passwd', None)
	if old_passwd_local == None:
		role.Msg(2, 0, GlobalPrompt.PackagePasswd_ResetPasswdUnnecessary)
		return
	#如果密码验证失败
	if o_passwd != old_passwd_local:
		role.Msg(2, 0, GlobalPrompt.PackagePasswd_ResetPasswdFailed)
		return
	#对密码的格式做一下检查，必须是6位数字，且开头不能为0
	if not n_passwd.isdigit():
		return
	if len(n_passwd) != 6:
		return
	if n_passwd.startswith('0'):
		return
	
	with Tra_ResetPackagePasswd:
		#重新设置加密锁密码
		role.GetObj(EnumObj.PackagePasswd)['passwd'] = n_passwd
		#记录玩家的原密码和新密码
		AutoLog.LogBase(role.GetRoleID(), AutoLog.evePackageRestetPasswd, (o_passwd, n_passwd))
		
	role.Msg(2, 0, GlobalPrompt.PackagePasswd_ResetPasswdOkay)

def SetPackagePasswd(role, msg):
	'''
	设置加密锁
	@param role:
	@param msg:
	'''
	n_passwd = msg
	#已经有密码了不能直接设置
	if role.GetI1(EnumInt1.PackageHasPasswd):
		role.Msg(2, 0, GlobalPrompt.PackagePasswd_SetPasswdFailed)
		return
	#对密码格式进行检查，必须是6为数字,且开头不能为0
	if not n_passwd.isdigit():
		return
	if len(n_passwd) != 6:
		return
	if n_passwd.startswith('0'):
		return
	with Tra_SetPackagePasswd:
		role.GetObj(EnumObj.PackagePasswd)['passwd'] = n_passwd
		#记录玩家设置的新密码
		AutoLog.LogBase(role.GetRoleID(), AutoLog.evePackageSetPasswd, n_passwd)
		role.SetTI64(EnumTempInt64.PackageIsUnlock, 0)
		role.SetI1(EnumInt1.PackageHasPasswd, 1)
	role.Msg(4, 0, GlobalPrompt.PackagePasswd_SetPasswdOkay)

def RequestClearPasswd(role, msg):
	'''
	客户端请求清除加密锁
	@param role:
	@param msg:
	'''
	#没有密码不需清除 
	if not role.GetI1(EnumInt1.PackageHasPasswd):
		return
	passwmgrdict = role.GetObj(EnumObj.PackagePasswd)
	#如果已经申请了清除密码,且正在等待清除中
	if 'reset_time' in passwmgrdict:
		reset_time = passwmgrdict['reset_time']
		delta = reset_time - cDateTime.Seconds()
		days_left = delta / OneDay
		hours_left = (delta % OneDay) / OneHour
		minutes_left = (delta % OneHour) / OneMinute
		role.Msg(2, 0, GlobalPrompt.PackagePasswd_ClearPasswdOkay % (days_left, hours_left, minutes_left))
		return
	#否则的话设置一周后清除密码
	with Tra_RequestClearPackagePasswd:
		nowtime = cDateTime.Seconds()
		passwmgrdict['reset_time'] = nowtime + OneWeek
		role.RegTick(OneWeek, ClearPasswd, None)
		#记录玩家请求清除密码后预计清除密码的时间戳
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveRequestPackageClearPasswd, nowtime + OneWeek)
		role.Msg(2, 0, GlobalPrompt.PackagePasswd_ClearPasswdRequest)

def ClearPasswd(role, callargv, regparam):
	'''
	清除加密锁
	@param role:
	@param callargv:
	@param regparam:
	'''	
	#清除密码并删掉清除密码的状态
	passwmgrdict = role.GetObj(EnumObj.PackagePasswd)
	#如果密码不需要清除
	if not 'reset_time' in passwmgrdict:
		return
	with Tra_ClearPackagePasswd:
		if 'passwd' in passwmgrdict:
			del passwmgrdict['passwd']
		if 'reset_time' in passwmgrdict:
			del passwmgrdict['reset_time']
		#是否有密码的标志改为0
		role.SetI1(EnumInt1.PackageHasPasswd, 0)
		role.Msg(2, 0, GlobalPrompt.PackagePasswd_ClearPasswdSuccess)

#============角色事件处理=============================================
def OnRoleLogin(role, param):
	'''
	角色登录的时候检查是否有加密锁需要要清除，如果需要则清除
	@param role:
	@param callargv:
	@param regparam:
	'''	
	#在角色登录的时候注册tick
	reset_time = role.GetObj(EnumObj.PackagePasswd).get('reset_time', None)
	if reset_time == None:
		return
	now = cDateTime.Seconds()
	#如果当前时间还没到清除密码的时间，则注册一个tick用来清除密码；否则的话直接清除密码
	if reset_time > now:
		role.RegTick(reset_time - now, ClearPasswd, None)
	else:
		ClearPasswd(role, None, None)

def AfterRoleJoin(role, param):
	'''
	角色进入场景后如果有宝贝密码需要清除则发出一个弹窗
	@param role:
	@param param:
	'''	
	reset_time = role.GetObj(EnumObj.PackagePasswd).get('reset_time', None)
	if reset_time == None:
		return
	delta = reset_time - cDateTime.Seconds()
	days_left = delta / OneDay
	hours_left = (delta % OneDay) / OneHour
	minutes_left = (delta % OneHour) / OneMinute
	role.Msg(5, 0, GlobalPrompt.PackagePasswd_ClearPasswdOkay % (days_left, hours_left, minutes_left))

def OnRoleClientLost(role, param):
	'''
	角色刷新，掉线，顶号都都需要给背包重新上锁
	@param role:
	@param param:
	'''	
	if role.GetI1(EnumInt1.PackageHasPasswd):
		role.SetTI64(EnumTempInt64.PackageIsUnlock, 0)

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		#事件
		Event.RegEvent(Event.Eve_ClientLost, OnRoleClientLost)
		Event.RegEvent(Event.Eve_AfterLogin, OnRoleLogin)

	if Environment.HasLogic and not Environment.IsCross:
		#事件
		Event.RegEvent(Event.Eve_AfterLoginJoinScene, AfterRoleJoin)
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ResetPackagePasswd", "客户端请求重设背包加密锁密码"), ResetPackagePasswd)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("SetPackagePasswd", "客户端请求设置背包加密锁密码"), SetPackagePasswd)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestClearPackagePasswd", "客户端请求清除加密锁密码"), RequestClearPasswd)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestUnlockPackage", "客户端请请求解锁背包"), UnlockPackage)

