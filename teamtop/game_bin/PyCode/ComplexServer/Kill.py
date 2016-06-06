#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("ComplexServer.Kill")
# from ComplexServer.Kill import Kill;Kill()
#===============================================================================
# 关闭进程
#===============================================================================
import time
import cRoleMgr
import cDateTime
import cComplexServer
import Environment
from ComplexServer import Init, Watch
from ComplexServer.Plug.Http import HttpWork
from ComplexServer.Plug.DB import DBProxy, DBWork
from Common.Other import EnumKick

def Kill():
	# 关闭监控线程
	if not Environment.IsQQUnion:
		Watch.StopWorkThread()
	# 将网络层发送模式切为即时发送
	cComplexServer.SetSendModel(False)
	# 1秒后真正开始关服
	cComplexServer.RegTick(1, RealKill, None)
	# 设置关服状态
	Init.IsStopState = True
	print "kill..."

def RealKill(callargv, regparam):
	# 如果有Http，直接停
	HttpWork.StopWorkThread()
	if Environment.HasLogic:
		KillLogic()
	elif Environment.HasDB:
		KillDB()
	else:
		Stop()

T_KILL = "服务器维护更新中..."
def KillLogic():
	print "RED, KillLogic."
	# T掉所有的角色
	for role in cRoleMgr.GetAllRole():
		role.Kick(True, EnumKick.ServerKill)
	# 强制调用各种保存回调
	cComplexServer.CallSave()
	# 如果有数据库连接，则等待网络成将数据全部保存完毕
	if DBProxy.DB_SESSION:
		cComplexServer.RegTick(1, KillLogic_Wait, None)
	# 如果自带数据库服务，则等待数据库保存完毕
	elif Environment.HasDB:
		DBWork.StopWorkThread()
		Stop()
	# 有逻辑不可能没有数据库服务
	else:
		assert False

def KillLogic_Wait(callargv, regparam):
	print "RED, KillLogic_Wait.", time.time()
	# 等待数据库连接中的消息全部发完(最多等待15秒)
	for idx in xrange(15):
		isSendOver = True
		for sessionid in DBProxy.DB_SESSION.keys():
			if not cComplexServer.IsSendOver(sessionid):
				isSendOver = False
				break
		if isSendOver:
			print "RED, logic save all data in %s second." % idx
			break
		else:
			time.sleep(1)
	else:
		print "GE_EXC, logic can't save all data."
	# 进程退出
	Stop()

def KillDB():
	print "RED, KillDB."
	# 要先等待网络层接收了所有的数据库请求（最多等待15秒）
	cComplexServer.RegTick(5, KillDB_Wait, 0)

def KillDB_Wait(callargv = None, cnt = 0):
	print "KillDB_Wait.", time.time()
	if cnt > 20:
		print "GE_EXC, net work is busy."
		DBWork.StopWorkThread()
		Stop()
		return
	if cDateTime.Seconds() - cComplexServer.GetLastMsgTime() > 3:
		print "RED, net work is over in %s count." % cnt
		DBWork.StopWorkThread()
		Stop()
		return
	cComplexServer.RegTick(1, KillDB_Wait, cnt + 1)

def Stop():
	print "RED, Stop"
	cComplexServer.Stop()

