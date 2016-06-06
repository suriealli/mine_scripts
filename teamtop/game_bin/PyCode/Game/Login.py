#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Login")
#===============================================================================
# 登录模块
#===============================================================================
import random
import traceback
import cProcess
import cDateTime
import cGatewayForward
import cComplexServer
import cRoleMgr
import cSceneMgr
import Environment
from World import Define
from Util import Function
from Common import Serialize, CValue
from Common.Message import OtherMessage, MessageCheck
from ComplexServer.API import QQHttp
from ComplexServer.Log import AutoLog
from ComplexServer.Plug.DB import DBProxy
from ComplexServer.Plug.Gateway import ClientMgr
from Game import RTF
from Game.Role import RoleMgr, Event, Version, RoleInit, Restore, HeFu, KuaFu,\
	GMRole
from Game.Role.Data import EnumDisperseInt32, EnumTempObj, EnumObj, EnumTempInt64
from Game.Role.Obj import Unify as ObjUnify
from Game.Property import PropertyMgr
from Common.Other import EnumKick



T_GMLock = "您的账号处于临时锁定状态，请稍候再登录！"
T_Limit = "服务器暂未开启，请稍候再登录！"
T_Limit_Force = "服务器正在维护中，请稍后再登录"
T_LostConnect = "断线了"
T_REPEAT_ROLE = "登陆错误，请再次登陆！"
T_DATA_ERROR = "您的角色数据(1)错误，请联系我们的客服！"
T_ARRAY_ERROR = "您的角色数据(2)错误，请联系我们的客服！"
T_OBJ_ERROR = "您的角色数据(3)错误，请联系我们的客服！"
T_FIX_ERROR = "您的角色数据(4)错误，请联系我们的客服！"
T_LoginTimeOver = "您长时间未完成登录，与服务器断开连接！"
T_ServerBusy = "系统繁忙，请稍候再登录！"

if "_HasLoad" not in dir():
	LostState = {}
	
	ClientState = {}
	ClientLoginInfo = {}
	ClientRoleId = {}
	RoleIdLoadTime = {}
	GMLockAccount = {}
	FroceLimit = False
	LimitLoginAccount = {}
	LimitLoginTickId = 0
	_NoState = 0
	_WaitAccountCheck = 1
	_WaitAccountLoad = 2
	_WaitCreateRole = 3
	_WaitCreateRoleReturn = 4
	_WaitCliektOK = 5
	_WaitLoadRole = 6
	_LoingOK = 7
	MaxLoginTime = 600
	
	#起始场景和坐标
	BEGIN_SCENE_ID = 15
	BEGIN_POS_X1 = 1361#1361,593左上
	BEGIN_POS_X2 = 1735#1735,955右下
	BEGIN_POS_Y1 = 593
	BEGIN_POS_Y2 = 955
	
	TraLogin = AutoLog.AutoTransaction("TraLogin", "登录")
	



def OnClientNew(clientKey):
	#有新的客户端连接
	assert clientKey not in ClientState
	ClientState[clientKey] = _NoState
	LostState[clientKey] = [cDateTime.Seconds(), _NoState, 0]
	#注册一个检测登录是否正常的tick
	cComplexServer.RegTick(MaxLoginTime, CheckClientState, clientKey)

def OnClientLost(clientKey):
	# 客户端断线删除客户端的Key
	if clientKey in ClientState:
		LS = LostState.get(clientKey)
		if LS:
			LS[1] = ClientState[clientKey]
			LS[2] = cDateTime.Seconds()
		del ClientState[clientKey]
	if clientKey in ClientRoleId: del ClientRoleId[clientKey]
	if clientKey in ClientLoginInfo: del ClientLoginInfo[clientKey]
	#角色断线
	role = cRoleMgr.FindRoleByClientKey(clientKey)
	if role is None:
		return
	if role.IsLost():
		return
	Event.TriggerEvent(Event.Eve_ClientLost, role)
	role.Save()
	role.Lost()
	roleId = role.GetRoleID()
	if role.GetTI64(EnumTempInt64.KickTickID):
		role.UnregTick(role.GetTI64(EnumTempInt64.KickTickID))
	
	pf = role.GetTempObj(EnumTempObj.LoginInfo).get("pf")
	if pf == "qqgame":
		#记录长时间离线踢玩家的tick
		role.SetTI64(EnumTempInt64.KickTickID, role.RegTick(3600, LostKick, roleId))
	else:
		role.SetTI64(EnumTempInt64.KickTickID, role.RegTick(300, LostKick, roleId))

def CheckClientState(callargv, clientKey):
	# 如果已经完成登录了，则忽视之
	if ClientState.get(clientKey, _LoingOK) == _LoingOK:
		return
	# 踢掉此玩家
	KickClient(clientKey, EnumKick.LoginTimeOut)

def KickClient(clientKey, msg):
	# 先告诉客户端为啥被T
	cGatewayForward.SendClientMsg(clientKey, OtherMessage.OMsg_Kick, msg)
	cComplexServer.RegTick(2, RealKick, clientKey)

def RealKick(callargv, clientKey):
	# 真正踢掉此玩家
	cGatewayForward.KickClient(clientKey)

def LostClient(clientKey):
	#断开一个客户端的连接
	cGatewayForward.KickClient(clientKey)

def LostKick(role, callargv, roleId):
	#断线一段时间后踢掉
	role = cRoleMgr.FindRoleByRoleID(roleId)
	if role: role.Kick(True, EnumKick.LostKick)


def OnClientRequestLogin(clientKey, loginInfo):
	'''
	客户端请求登陆
	@param clientKey:
	@param loginInfo: {"serverid":XXX, "account":XXX, "userip":XXX, "openkey":XXX, "pf":XXX, "pfkey":XXX}
	'''
	# 检测状态
	state = ClientState.get(clientKey)
	if state != _NoState:
		print "GE_EXC, error state(%s) on OnClientRequestLogin" % state
		return False
	serverid = int(loginInfo["serverid"])
	account = loginInfo["account"]
	openkey = loginInfo["openkey"]
	userip = loginInfo["userip"]
	from_1 = loginInfo["pf"]
	from_2 = loginInfo.get("app_custom", "")
	from_3 = loginInfo.get("app_contract_id", "")
	
	if not from_2 : from_2 = loginInfo.get("app_user_source", "")
	if not from_2 : from_2 = loginInfo.get("via", "")
	if from_1 == "website" or not from_2 : from_2 = loginInfo.get("adtag", "")
	
	# 检测限登录
	if LimitLoginAccount and account not in LimitLoginAccount:
		cGatewayForward.SendClientMsg(clientKey, OtherMessage.OMsg_LoginFail, T_Limit)
		return True
	# 组合登录信息
	loginInfo["ClientKey"] = clientKey
	# 帐号检测
	ClientState[clientKey] = _WaitAccountCheck
	# 检测锁定账号
	if account in GMLockAccount:
		if openkey == GMLockAccount[account]:
			OnLoginBack((200, repr({"ret":0, "msg":"OK"})), loginInfo)
		else:
			cGatewayForward.SendClientMsg(clientKey, OtherMessage.OMsg_LoginFail, T_GMLock)
		return True
	# 统计信息
	DBProxy.DBVisit(serverid, None, "Info_Connect", (account, userip, from_1, from_2, from_3))
	# 按照环境登录
	if Environment.IsDevelop:
		OnLoginBack((200, repr({"ret":0, "msg":"OK"})), loginInfo)
	elif Environment.EnvIsQQ():
		QQHttp.get_info(account, openkey, from_1, OnLoginBack, loginInfo)
	else:
		DBProxy.DBVisit(serverid, None, "CanLogin", (account, openkey), OnLoginBack, loginInfo)
	return True


def OnLoginBack(response, loginInfo):
	account = loginInfo["account"]
	clientKey = loginInfo["ClientKey"]
	# Http没有返回
	if response is None:
		ClientState[clientKey] = _NoState
		cGatewayForward.SendClientMsg(clientKey, OtherMessage.OMsg_LoginFail, T_ServerBusy)
		print "GE_EXC, response is None", account
		return
	# 检测状态
	state = ClientState.get(clientKey, 0)
	if state != _WaitAccountCheck:
		#print "GE_EXC, error state(%s) on OnLoginOK" % state, account
		return
	# 检测登录信息
	code, body = response
	if code != 200:
		ClientState[clientKey] = _NoState
		cGatewayForward.SendClientMsg(clientKey, OtherMessage.OMsg_LoginFail, T_ServerBusy)
		#print "GE_EXC OnLoginBack get_info error code (%s)" % code, account
		return
	
	true = 1
	false = 2
	true, false
	body = eval(body)
	if body["ret"] != 0:
		ClientState[clientKey] = _NoState
		cGatewayForward.SendClientMsg(clientKey, OtherMessage.OMsg_LoginFail, body["msg"])
		#print "GE_EXC OnLoginBack get_info error(%s)" % body["ret"], account
		return
	# 载入帐号信息
	ClientState[clientKey] = _WaitAccountLoad
	# 组合登录信息(更新第三方數據)
	loginInfo.update(body)
	# 载入帐号
	LoadAccountInfo(loginInfo)

def LoadAccountInfo(loginInfo):
	#根据账号载入角色ID数据
	DBProxy.DBVisit(loginInfo["serverid"], None, "LoadAccountInfo", loginInfo["account"], OnLoadAccountReturn, loginInfo)

T_CORSS_CREATE_ROLE = "跨服不能创建角色！"
def OnLoadAccountReturn(ret, loginInfo):
	clientKey = loginInfo["ClientKey"]
	# 检测状态
	state = ClientState.get(clientKey, 0)
	if state != _WaitAccountLoad:
		print "GE_EXC, error state(%s) on OnLoadAccountReturn" % state
		return
	account = loginInfo["account"]
	if not account:
		print "GE_EXC, not account on OnLoadAccountReturn"
		return False
	# 超时返回
	if ret is None:
		print "GE_EXC, time over OnLoadAccountReturn"
		return False
	# 记录客户端的登录信息
	ClientLoginInfo[clientKey] = loginInfo
	roleId = ret
	# 没有角色信息
	if roleId == 0:
		# 跨服不能创建角色
		if cProcess.ProcessID in Define.CrossWorlds:
			KickClient(clientKey, EnumKick.CrossCreateRole)
		else:
			ClientState[clientKey] = _WaitCreateRole
			#还没有角色，让客户端弹出创建角色面板
			cGatewayForward.SendClientMsg(loginInfo["ClientKey"], OtherMessage.OMsg_RoleError)
	#已有角色，准备登陆
	else:
		# 这里保存角色ID
		ClientRoleId[clientKey] = roleId
		#同步服务器时间
		SyncServerTime(clientKey)

def OnClientRequestCreateRole(clientKey, createData):
	# 检测状态
	roleName = createData[1]
	roleSex = createData[2]
	roleCareer = createData[3]
	#性别只有男性1， 女性2
	if roleSex != 1 and roleSex != 2:
		print "GE_EXC, ERROR roleSex (%s)OnClientRequestCreateRole" % roleSex
		return False
	#职业只有骑士1，法师2
	if roleCareer != 1 and roleCareer != 2:
		print "GE_EXC, ERROR roleCareer (%s)OnClientRequestCreateRole" % roleCareer
		return False
	state = ClientState.get(clientKey, 0)
	if state != _WaitCreateRole:
		print "GE_EXC, error state(%s) on OnClientRequestCreateRole" % state
		return False
	loginInfo = ClientLoginInfo.get(clientKey)
	if not loginInfo:
		print "GE_EXC, OnClientRequestCreateRole error  not loginInfo"
		return False
	# 统计信息
	account = loginInfo["account"]
	DBProxy.DBVisit(cProcess.ProcessID, None, "Info_Create", account)
	#更新状态
	ClientState[clientKey] = _WaitCreateRoleReturn
	# 这里可以加速下，先看看内存中是否有这个角色名
	if roleName in RoleMgr.RoleName_Roles:
		#已经有这个名字，让客户端重新输入名字
		OnCreateRoleReturn(0, clientKey)
		return True
	# 如果是腾讯平台，则过滤敏感字
	regparam = (loginInfo, clientKey, account, roleName, roleSex, roleCareer)
	if Environment.EnvIsQQ():
		QQHttp.word_filter(account, loginInfo["openkey"], loginInfo["pf"], roleName, OnRoleNameBack, regparam)
	else:
		OnRoleNameBack((200, repr({"ret":0, "is_dirty":0})), regparam)
	return True

def OnRoleNameBack(response, regparam):
	loginInfo, clientKey, account, roleName, roleSex, roleCareer = regparam
	loginInfo
	account
	roleSex
	roleCareer
	# Http查询失败
	if response is None:
		print "GE_EXC, OnRoleNameBack is None"
		OnCreateRoleReturn(0, clientKey)
		return
	code, body = response
	if code != 200:
		print "GE_EXC, OnRoleNameBack code(%s)" % code
	body = eval(body)
	if body["ret"] != 0:
		print "GE_EXC, OnRoleNameBack error(%s)" % body["msg"]
		OnCreateRoleReturn(0, clientKey)
		return
	# 接口返回有问题，打印下看看
	if "is_dirty" not in body:
		print "GE_EXC, OnRoleNameBack back error", body
	if body.get("is_dirty", 0) != 0:
		OnCreateRoleReturn(0, clientKey)
		return
	# 去“主”数据库中分配角色名（这里为了保证数据互通后角色名唯一）
	DBProxy.DBVisit(cProcess.ProcessID, 0, "AllotRoleName", roleName, OnAllotRoleNameReturn, regparam)

def OnAllotRoleNameReturn(ret, regparam):
	loginInfo, clientKey, account, roleName, roleSex, roleCareer = regparam
	if not ret:
		OnCreateRoleReturn(0, clientKey)
	else:
		# 尝试去数据库创建角色， 这里当然是创建在指定服务器上,如果重名会返回，然后让客户端重新输入名字
		DBProxy.DBVisit(loginInfo["serverid"], None, "CreateRole", (account, roleName, roleSex, roleCareer), OnCreateRoleReturn, clientKey)

T_RoleError = "该角色名已存在！"
def OnCreateRoleReturn(ret, clientKey):
	# 检测状态
	state = ClientState.get(clientKey, 0)
	if state != _WaitCreateRoleReturn:
		print "GE_EXC, error state(%s) on OnCreateRoleReturn" % state
		return
	roleid = ret
	# 创建角色失败，可能是名字重复了
	if roleid == 0:
		#继续设置角色状态
		ClientState[clientKey] = _WaitCreateRole
		#继续弹出创建角色面板
		cGatewayForward.SendClientMsg(clientKey, OtherMessage.OMsg_RoleError, T_RoleError) 
	else:
		#第一次登陆角色通知
		cGatewayForward.SendClientMsg(clientKey, OtherMessage.OMsg_FirstCreateRole)
		# 这里保存角色ID
		ClientRoleId[clientKey] = ret
		#同步服务器时间
		SyncServerTime(clientKey)

def SyncServerTime(clientKey):
	#同步服务器时间，等待客户端加载主程序
	ClientState[clientKey] = _WaitCliektOK
	#客户端在收到这条消息时就开始加载主程序
	cGatewayForward.SendClientMsg(clientKey, OtherMessage.OMsg_ServerUnixTime, (cDateTime.Seconds(), cDateTime.TimeZoneSeconds(), cDateTime.GetDST()))

T_RoleIsLoading = "系统繁忙，请稍候再登录！"
T_RepeatRole1 = "您的角色已经登录，现在已经将已经登录的角色顶号下来了，请重新登录！"
T_RepeatRole2 = "您的角色已经在其他地方登录了，请确认是否正常！"
def OnClietOK(clientKey, msg):
	#客户端加载主程序成功，服务器开始去DB载入玩家数据
	# 检测状态
	state = ClientState.get(clientKey, 0)
	if state != _WaitCliektOK:
		print "GE_EXC, error state(%s) on OnClietOK" % state
		return False
	roleId = ClientRoleId.get(clientKey)
	if not roleId:
		print "GE_EXC, no role id on OnClietOK"
		return False
	now = cDateTime.Seconds()
	if now - RoleIdLoadTime.get(roleId, 0) < 70:
		# 最近载入过，但是没有载入成功， 一段时间内暂时不能载
		KickClient(clientKey, EnumKick.CrossCreateRole)
		return False
	role = cRoleMgr.FindRoleByRoleID(roleId)
	if role:
		if Environment.IsCross:
			#跨服直接踢掉
			#重复登陆，两边都踢掉
			KickClient(clientKey, EnumKick.RepeatLogin)
			role.Kick(True, EnumKick.RepeatLogin)
		else:
			#重复登录，顶掉前面的连接
			ReLogin(role, clientKey)
	else:
		# 允许登陆，向DB请求角色数据
		DBProxy.DBRoleVisit(roleId, "LoadRole", (roleId, cProcess.ProcessID), OnLoadRoleReturn, (roleId, clientKey))
		RoleIdLoadTime[roleId] = now
		ClientState[clientKey] = _WaitLoadRole
	return True


DI32_BEGIN = 6
ROLE_DATE_LENGTH = DI32_BEGIN + len(EnumDisperseInt32.L)
ARRAY_LENGTH = 11

def OnLoadRoleReturn(ret, param):
	# DB返回角色数据，开始处理数据并且进入游戏场景
	roleId, clientKey = param
	state = ClientState.get(clientKey)
	# 删除载入角色数据时间
	if roleId in RoleIdLoadTime: del RoleIdLoadTime[roleId]
	#===========================================================================
	# 这里要特殊检查下跨服带来的两种新状态
	#===========================================================================
	if ret is True:
		# 需要尝试再次载入角色数据
		if state != _WaitLoadRole:
			print "GE_EXC, error state(%s) on OnLoadRoleReturn retry" % state
			KickClient(clientKey, EnumKick.RepeatLogin)
		else:
			RoleIdLoadTime[roleId] = cDateTime.Seconds()
			DBProxy.DBRoleVisit(roleId, "LoadRole", (roleId, cProcess.ProcessID), OnLoadRoleReturn, (roleId, clientKey))
		return
	if ret is False:
		# 被顶号再顶号了
		KickClient(clientKey, EnumKick.RepeatLogin)
		return
	#===========================================================================
	# 这里要特殊检查载入角色数据是否超时
	#===========================================================================
	# 超时返回
	if ret is None:
		print "GE_EXC, load role(%s) time over." % roleId
		KickClient(clientKey, EnumKick.LoadRoleDataTimeOut)
		return
	#===========================================================================
	# 接下来进行登陆验证
	#===========================================================================
	# 当载入角色数据后，客户端已经断开连接
	if state is None:
		print "GS_EXC, error state(%s) on OnLoadRoleReturn" % state
		return
	# 检测状态
	if state != _WaitLoadRole:
		print "GE_EXC, error state(%s) on OnLoadRoleReturn" % state
		KickClient(clientKey, EnumKick.RepeatLogin)
		return
	# 获取登录信息
	loginInfo = ClientLoginInfo.get(clientKey)
	if not loginInfo:
		print "GE_EXC, no login info on OnLoadRoleReturn"
		KickClient(clientKey, EnumKick.RepeatLogin)
		return
	roledata, roleobj = ret
	# 重复载入
	if roledata is None:
		# 如果的确能已经有这个角色了，T客户端
		if cRoleMgr.FindRoleByRoleID(roleId):
			print "GE_EXC, repeat load role(%s) but find." % roleId
			KickClient(clientKey, EnumKick.RepeatLogin)
		# 如果没有这个角色，在强制载入角色
		else:
			print "GE_EXC, repeat load role(%s) but not find." % roleId
			DBProxy.DBRoleVisit(roleId, "LoadRoleData_Force", (roleId, cProcess.ProcessID), OnLoadRoleReturn, (roleId, clientKey))
		return
	# 居然没有角色数据
	if len(roledata) != ROLE_DATE_LENGTH:
		print "GE_EXC, load role(%s) error role data(%s) != end obj(%s)" % (roleId, len(roledata), ROLE_DATE_LENGTH)
		KickClient(clientKey, EnumKick.DataError)
		return	
	# 关于角色数据相关的地方请搜索关键字 !@RoleData
	account = roledata[0]
	role_id = roledata[1]
	role_name = roledata[2]
	command_size = roledata[3]
	command_index = roledata[4]
	
	array = roledata[5]
	di32 = tuple(roledata[DI32_BEGIN:])

	if array is None:
		# 初始化  i64 i32 i16 i8  di8 i1  di1 di64 ci8 cd objs
		array = ["", "", "", "", "", "", "", None, "", None, ()]
	elif len(array) != ARRAY_LENGTH:
		array = Serialize.String2PyObjEx(array)
		if len(array) != ARRAY_LENGTH:
			print "GE_EXC, role login data array len(%s) is not %s." % (len(array), ARRAY_LENGTH)
			KickClient(clientKey, EnumKick.DataError)
			return
	# 先尝试创建Role，如果创建不出来，直接返回，不必进行下面的工作了。
	role = cRoleMgr.CreateRole(role_id, role_name, account, clientKey, command_size, command_index)
	if role is None:
		print "GE_EXC, create role fail."
		KickClient(clientKey, EnumKick.CreateRoleFail)
		return
	i64 = array[0]
	i32 = array[1]
	i16 = array[2]
	i8 = array[3]
	di8 = array[4]
	i1 = array[5]
	di1 = array[6]
	di64 = array[7]
	ci8 = array[8]
	cd = array[9]
	objs = array[10]
	# 首先 ，同步基础数据
	role.SyncDataBase()
	# 处理载入的数组数据
	role.InitI64(i64)
	role.InitI32(i32)
	role.InitI16(i16)
	role.InitI8(i8)
	role.InitDI8(di8)
	role.InitI1(i1)
	role.InitDI1(di1)
	role.InitDI64(di64)
	role.InitCI8(ci8)
	role.InitDI32(di32)
	role.InitObj(objs)#角色身上的对象(PyObj)，都是字典结构， 并且不同于obj数据
	role.InitCD(cd)
	#初始化属性管理器(可能很多系统都会触发属性管理器的逻辑，所以优先初始化这个管理器)
	PropertyMgr.InitMgr(role)
	# 告诉客户端角色初始数据已经同步OK了,并且【检测每日清零数组】，更新连续登陆天数 
	# 旧版本是这个调用里面触发每日清理的 2014.9.23 HWQ 修改为afterlogin后触发
	role.SyncOK()
	# 设置登录信息
	role.SetTempObj(EnumTempObj.LoginInfo, loginInfo)
	# 初始化第一次登陆角色数据(每一个角色永远 只 会调用一次)
	RoleInit.InitRole(role)
	# 分发处理从数据库载入的obj数据,生成对应的临时管理器
	ObjUnify.OnLoadRoleObj(role, roleobj)
	if role.IsKick():
		#可能在处理obj数据时出现异常把角色踢掉了
		return
	#根据角色obj字典数据生成python处理对象，并且同步角色 python obj(有需求才选择同步)
	#触发Eve_InitRolePyObj
	RoleMgr.InitRoleOtherPyObj(role)
	#=============在这一步之前要确保角色数据已经全部载入，初始化，预处理完毕===================
	# 设置登录状态
	ClientState[clientKey] = _LoingOK
	# 登录之前第1件事情--确定没封号
	if role.GetDI32(EnumDisperseInt32.CanLoginTime) > cDateTime.Seconds():
		role.Kick(True, EnumKick.LimitLogin)
		return
	# 登录之前第2件事情--确定没穿越
	# 如果上次保存的进程和载入的进程是同一个，则必须当前时间大于保存时间
	if role.GetDI32(EnumDisperseInt32.LastSaveProcessID) == cProcess.ProcessID:
		exitsec = cDateTime.Seconds() - role.GetDI32(EnumDisperseInt32.LastSaveUnixTime)
		if exitsec < 0:
			#穿越了
			role.Msg(4, 0, "你的号穿越了啊！")
			print "GE_EXC, role(%s) through time same process." % role.GetRoleID()
			role.Kick(False, EnumKick.ThroughTime)
			return
		if (Environment.EnvIsQQ() or Environment.IsDevelop) and not Environment.IsCross:
			if exitsec > 604800 and role.GetDI32(EnumDisperseInt32.GM_UnbindRMB) >= 10000:
				#发资源超过10000神石，并且1周内没有登录的，锁号
				if GMRole.IsLock(role):
					return
	# 如果上次保存的进程和载入的进程不是同一个（可能跨服等），给予10分钟缓冲区间
	else:
		if cDateTime.Seconds() - role.GetDI32(EnumDisperseInt32.LastSaveUnixTime) < -600:
			print "GE_EXC, role(%s) through time diff process." % role.GetRoleID()
			role.Kick(False, EnumKick.ThroughTime)
			return
	# 登录之前第3件事情--修正角色数据(在做这一步之前，要确定所有的系统数据都初始化完毕)
	if not Version.BeforeRoleLogin(role):
		role.Kick(False, EnumKick.VersionFixError)
		return
	# ======================到这里登录完成了======================
	# 合服处理
	HeFu.HeFuInit(role)
	# 先告诉角色管理器， 
	RoleMgr.RoleLogin(role)
	# 触发Eve_AfterLogin
	Event.TriggerEvent(Event.Eve_AfterLogin, role)
	#触发每日清理
	role.ClearPerDay()
	#计算离线恢复体力
	role.CountTiLi()
	#触发同步其他剩余数据
	RoleMgr.SyncRoleOtherPyObj(role)
	# 最后进入场景,开始游戏
	try:
		LoginJoinScene(role, clientKey)
	except:
		traceback.print_exc()
		role.Kick(False, EnumKick.SceneError)
		return
	if role.IsKick():
		return
	# 好了，可以记录登录日志了（登录日志有些多，只记录较高等级的付费玩家玩家）
	if Environment.IsCross:
		return
	if role.GetLevel() <= 30:
		return
	if role.GetConsumeQPoint() <= 0:
		return
	ALB = AutoLog.LogBase
	ALOBJ = AutoLog.eveLoginObj
	with TraLogin:
		#记录IP
		userip = role.GetTempObj(EnumTempObj.LoginInfo).get("userip")
		pf = role.GetTempObj(EnumTempObj.LoginInfo).get("pf")
		role.SetTempObj(EnumTempObj.LoginTime, cDateTime.Now())
		#记录基本数据
		ALB(role_id, AutoLog.eveLoginData, (role.GetLevel(), role.GetReputation(), role.GetMoney(), role.GetBindRMB(), role.GetUnbindRMB(), userip, pf))
		obj_log = []
		for obj in roleobj:
			obj_log.append((obj[0], obj[1], obj[2]))
			if len(obj_log) == 50:
				ALB(role_id, ALOBJ, obj_log)
				obj_log = []
		if obj_log:
			ALB(role_id, ALOBJ, obj_log)

def LoginJoinScene(role, clientKey):
	#登陆进入场景
	connectInfo = role.GetObj(EnumObj.ReConnect)
	if Environment.IsCross:
		sceneId, posX, posY = connectInfo[KuaFu.SCENE_INFO]
	else:
		sceneId = role.GetLastSceneID()
		posX, posY = role.GetLastPos()
		if 0 == sceneId:
			sceneId = BEGIN_SCENE_ID
			posX, posY = GetRandomBeginPos()
	scene = cSceneMgr.SearchPublicScene(sceneId)
	scene.JoinRole(role, posX, posY)
	Event.TriggerEvent(Event.Eve_AfterLoginJoinScene, role)
	#执行进入场景后的回调函数
	backfun = connectInfo.get(KuaFu.BACKFUN)
	regparam = connectInfo.get(KuaFu.REGPARAM)
	env = connectInfo.get(KuaFu.Env)
	#这里先把连接信息清理
	connectInfo.clear()
	if not backfun:
		return
	if env == 2 and not Environment.IsCross:
		return
	if env == 1 and Environment.IsCross:
		return
	backfun = Function.FunctionUnpack(*backfun)
	regparam = eval(regparam)
	backfun(role, regparam)
	
	if Environment.IsCross:
		role.RegTick(2, CrossMsg, None)

def CrossMsg(role, callArgv, regparam):
	if not role or role.IsKick() or role.IsLost():
		return
	role.Msg(2, 0, "")
	

def BeforeExitByKickRole(role):
	# 踢玩家的时候触发回调, 管理器删除角色....
	RoleMgr.BeforeExitByKickRole(role)

def SaveRole(role):
	Event.TriggerEvent(Event.Eve_BeforeSaveRole, role)
	# 关于角色数据相关的地方请搜索关键字  !@RoleData
	roleId = role.GetRoleID()
	_, command_index = role.GetCommand()
	i64 = role.SeriI64()
	i32 = role.SeriI32()
	i16 = role.SeriI16()
	i8 = role.SeriI8()
	di8 = role.SeriDI8()
	i1 = role.SeriI1()
	di1 = role.SeriDI1()
	di64 = role.SeriDI64()
	ci8 = role.SeriCI8()
	cd = role.SeriCD()
	objs = role.SeriObj()
	array = [i64, i32, i16, i8, di8, i1, di1, di64, ci8, cd, objs]
	roledata = [command_index, array]
	roledata.extend(role.SeriDI32())
	roledata.append(roleId)
	roleobj = ObjUnify.GetRoleObj(role)
	DBProxy.DBRoleVisit(roleId, "SaveRole", (roleId, cProcess.ProcessID, roledata, roleobj))

def ExitRole(roleid):
	# 这里要明确的告诉DB，角色退出了
	DBProxy.DBRoleVisit(roleid, "ExitRole", (roleid, cProcess.ProcessID))

def ReLogin(role, clientKey):
	#尝试断开上一个连接
	if not role.IsLost():
		#必须先触发一次保存，在断开上一个连接，因为角色保存的时候会触发一些中间数据生成角色持久化的数据的逻辑
		#如果不生成这些持久化数据，则如果某些系统是只同步持久化的基础数据给客户端，
		#服务器用的是持久化基础数据生成的中间数据来操作系统逻辑。因为性能考虑，这些中间数据生成为持久化数据的时机一般都是
		#角色离线或者强制保存时，所以这里必须触发一次保存角色数据
		#触发这个角色断开连接
		Event.TriggerEvent(Event.Eve_ClientLost, role)
		role.Save()
		role.Lost()
	loginInfo = ClientLoginInfo.get(clientKey)
	if not loginInfo:
		print "GE_EXC, ReLogin not loginInfo (%s)" % role.GetRoleID()
	else:
		#重新设置登录信息
		role.SetTempObj(EnumTempObj.LoginInfo, loginInfo)
	#重新设置clientKey
	role.ReLogin(clientKey)
	#登录成功
	ClientState[clientKey] = _LoingOK
	#客户端数据同步恢复流程
	role.SyncDataBase()
	role.SyncByReLogin()
	#重新登录是不用触发每日清理的，因为角色一直在线,跨天的在线角色会自动执行每日清理
	role.SyncOK()
	#同步物品
	ObjUnify.AfterLoadObj(role)
	#同步属性
	role.SyncAllProperty()
	#登录处理
	RoleMgr.RoleLogin(role)
	#其他剩余数据同步
	Event.TriggerEvent(Event.Eve_SyncRoleOtherData, role)
	#还原客户端(场景)
	Restore.RestoreClient(role)
	#删除注册踢玩家的tick
	if role.GetTI64(EnumTempInt64.KickTickID):
		role.UnregTick(role.GetTI64(EnumTempInt64.KickTickID))
		role.SetTI64(EnumTempInt64.KickTickID, 0)

@RTF.RegFunction
def LockAccount(account, pwd = ""):
	'''
	GM锁定账号
	@param account:帐号
	@param pwd:密码
	'''
	if pwd:
		GMLockAccount[account] = pwd
		for role in cRoleMgr.GetAllRole():
			if role.GetTempObj(EnumTempObj.LoginInfo)["account"] == account:
				role.Kick(True, EnumKick.GMLock)
				break
	else:
		if account in GMLockAccount:
			del GMLockAccount[account]
	return pwd

@RTF.RegFunctionBack
def LimitLogin(b):
	'''
	设置限登录(运维)
	@param b:是否限登录
	'''
	if not Environment.HasLogic:
		return
	if not b and cProcess.ProcessID in Define.TestWorldIDs and Environment.EnvIsQQ():
		#腾讯测试服永远都是限制登录状态
		print "GE_EXC qq test server can not set limit login! "
		return
	global LimitLoginTickId
	if b:
		InitLimitLoginAccount()
		if LimitLoginTickId:
			cComplexServer.UnregTick(LimitLoginTickId)
			LimitLoginTickId = 0
	else:
		from Game.Persistence import Base, BigTable
		if Base.AllLoadReturn is False or BigTable.AllLoadReturn is False:
			print "GE_EXC, error LimitLogin data not return db base(%s), bigtable(%s)" % (Base.AllLoadReturn, BigTable.AllLoadReturn)
			if not LimitLoginTickId:
				LimitLoginTickId = cComplexServer.RegTick(10, LimitTick, None)
			return
		LimitLoginAccount.clear()

def InitLimitLoginAccount():
	from ComplexServer.Plug.DB import DBHelp
	LimitLoginAccount["None"] = "None"
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		cur.execute("select account, info from inner_account;")
		for account, info in cur.fetchall():
			LimitLoginAccount[account] = info

def LimitTick(callargv, regparam):
	#Tick触发开放限制
	global LimitLoginTickId
	LimitLoginTickId = 0
	LimitLogin(False)

def MatchMsg(clientKey, msg):
	#判断客户端消息和服务端消息的正确性
	if Environment.IsDevelop:
		needUpdate = False
		for k, v in msg.iteritems():
			if v != MessageCheck.MSG.get(k):
				needUpdate = True
				break
		if needUpdate is True:
			roleId = ClientRoleId.get(clientKey)
			print "GE_EXC ----------------Update Client Msg--------------------------"
			print "BLUE, role(%s) login....." % roleId
			print "GE_EXC Warning Client's Msg not Match Server's, please Update Client"
			print "GE_EXC ----------------Update Client Msg--------------------------"
			cComplexServer.RegTick(10, WarningMsg, roleId)
	return True

def WarningMsg(argv, reg):
	role = cRoleMgr.FindRoleByRoleID(reg)
	if not role:
		return
	role.Msg(4, 0, "你的客户端消息太旧了，请更新一下消息，或者使用别的客户端")

def OnClientStatus(clientKey, msg):
	if type(msg) is not int:
		return True
	state = ClientState.get(clientKey)
	if state != _WaitCreateRole:
		return True
	loginInfo = ClientLoginInfo.get(clientKey)
	if not loginInfo:
		return True
	account = loginInfo["account"]
	DBProxy.DBVisit(cProcess.ProcessID, None, "Info_Status", (msg, account))
	return True


def GetRandomBeginPos():
	return random.randint(BEGIN_POS_X1, BEGIN_POS_X2), random.randint(BEGIN_POS_Y1, BEGIN_POS_Y2)

def ChangeBeginPos():
	global BEGIN_SCENE_ID
	global BEGIN_POS_X1
	global BEGIN_POS_X2
	global BEGIN_POS_Y1
	global BEGIN_POS_Y2
	
	#各版本判断
	if Environment.EnvIsNA() or Environment.EnvIsFT() or Environment.EnvIsTK():
		#起始场景和坐标
		BEGIN_SCENE_ID = 63
		BEGIN_POS_X1 = 220
		BEGIN_POS_X2 = 440
		BEGIN_POS_Y1 = 1479
		BEGIN_POS_Y2 = 1633


if "_HasLoad" not in dir():
	# 非内网环境，需要限登录之
	if not Environment.IsDevelop and Environment.HasLogic:
		LimitLogin(True)
	
	ChangeBeginPos()
	ClientMgr.SetClientNewFun(OnClientNew)
	ClientMgr.SetClientLostFun(OnClientLost)
	# 注意下，注册RegClientMsgDistribute需要在OtherMessage中定义
	ClientMgr.RegClientMsgDistribute(OtherMessage.OMsg_Login, OnClientRequestLogin)
	ClientMgr.RegClientMsgDistribute(OtherMessage.OMsg_CreateRole, OnClientRequestCreateRole)
	ClientMgr.RegClientMsgDistribute(OtherMessage.OMsg_ClientOK, OnClietOK)
	ClientMgr.RegClientMsgDistribute(OtherMessage.OMsg_ChechMsg, MatchMsg)
	ClientMgr.RegClientMsgDistribute(OtherMessage.OMsg_ClientStatus, OnClientStatus)

