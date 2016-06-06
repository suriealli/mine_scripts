#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Debug")
# from Game.Role.Debug import *
#===============================================================================
# 角色调试辅助
#===============================================================================
import cRoleMgr
from ThirdLib import PrintHelp
from Common.Message import AutoMessage

#===============================================================================
# 内网角色消息监控
#===============================================================================
if "_HasLoad" not in dir():
	DebugRoleID = set()

def OnDistribute(role, fun, msg):
	if role.GetRoleID() not in DebugRoleID:
		return
	print role.GetRoleID(), "BLUE -->", fun.__module__, fun.__name__
	PrintHelp.pprint(msg)

def DoSendObj(role, mtype, msg, callback):
	from Common.Message import MessageCheck
	if role.GetRoleID() not in DebugRoleID:
		return
	if callback is None:
		print "GREEN -->", role.GetRoleID(), mtype, MessageCheck._MSG.get(mtype, mtype)
	else:
		print "GREEN -->..", role.GetRoleID(), mtype, MessageCheck._MSG.get(mtype, mtype), callback.__module__, callback.__name__
	PrintHelp.pprint(msg)

def DoCallback(role, msg):
	if role.GetRoleID() not in DebugRoleID:
		return
	print "GREEN -->", role.GetRoleID()
	PrintHelp.pprint(msg)

def OnCallback(role, fun, msg):
	if role.GetRoleID() not in DebugRoleID:
		return
	print role.GetRoleID(), "BLUE -->", fun.__module__, fun.__name__
	PrintHelp.pprint(msg)

#===============================================================================
# 角色消息观察
#===============================================================================
def WatchRole(role, fun, msg):
	print "Watch", role.GetRoleID(), fun.__module__, fun.__name__
	PrintHelp.pprint(msg)

def AddWatch(role_id):
	cRoleMgr.AddWatchRole(role_id)

def ClearWatch():
	cRoleMgr.ClearWatchRole()

#===============================================================================
# 角色消息统计
#===============================================================================
def Start():
	cRoleMgr.SetStatistics(True)

def Close():
	cRoleMgr.SetStatistics(False)

def ShowAll():
	PrintHelp.pprint(cRoleMgr.GetRoleMessage())

def ShowTotal():
	d = cRoleMgr.GetRoleMessage()
	a = len(d)
	s = 0
	r = 0
	for ad in d.itervalues():
		sd, rd = ad
		s += (sum(sd.itervalues()))
		r += (sum(rd.itervalues()))
	print "role", a
	print "send", s
	print "recv", r

def ShowMostRole(c1 = 10, c2 = 10):
	d = cRoleMgr.GetRoleMessage()
	scl = []
	rcl = []
	# 求和
	for role_id, ad in d.iteritems():
		sd, rd = ad
		scl.append([role_id, sum(sd.itervalues()), sd])
		rcl.append([role_id, sum(rd.itervalues()), rd])
	# 排序1
	scl.sort(key=lambda it:it[1], reverse=True)
	rcl.sort(key=lambda it:it[1], reverse=True)
	# 排序2
	for info in scl:
		l = info[2].items()
		l.sort(key=lambda it:it[1], reverse=True)
		info[2] = l[:c2]
	for info in rcl:
		l = info[2].items()
		l.sort(key=lambda it:it[1], reverse=True)
		info[2] = l[:c2]
	# 打印
	print "Send ..."
	PrintHelp.pprint(scl[:c1])
	print "Recv ..."
	PrintHelp.pprint(rcl[:c1])

def ShowMostMsg(c1 = 10, c2 = 10):
	d = cRoleMgr.GetRoleMessage()
	smd = {}
	rmd = {}
	# 拆分统计
	for role_id, ad in d.iteritems():
		sd, rd = ad
		for msgType, cnt in sd.iteritems():
			_cnt, _d = smd.get(msgType, (0, {}))
			_d[role_id] = cnt
			smd[msgType] = [_cnt + cnt, _d]
		for msgType, cnt in rd.iteritems():
			_cnt, _d = rmd.get(msgType, (0, {}))
			_d[role_id] = cnt
			rmd[msgType] = [_cnt + cnt, _d]
	# 排序1
	sml = []
	for key, value in smd.iteritems():
		sml.append([key, value[0], value[1]])
	sml.sort(key=lambda it:it[1], reverse=True)
	rml = []
	for key, value in rmd.iteritems():
		rml.append([key, value[0], value[1]])
	rml.sort(key=lambda it:it[1], reverse=True)
	# 排序2
	for info in sml:
		l = info[2].items()
		l.sort(key=lambda it:it[1], reverse=True)
		info[2] = l[:c2]
	for info in rml:
		l = info[2].items()
		l.sort(key=lambda it:it[1], reverse=True)
		info[2] = l[:c2]
	# 打印
	print "Send ..."
	PrintHelp.pprint(sml[:c1])
	print "Recv ..."
	PrintHelp.pprint(rml[:c1])

def ShowLeastMsg(c = 0):
	# 初始化所有的消息
	md = {}
	for msgType in AutoMessage.Values:
		md[msgType] = 0
	# 获取收发的消息
	d = cRoleMgr.GetRoleMessage()
	# 拆分统计
	for _, ad in d.iteritems():
		sd, rd = ad
		for msgType, cnt in sd.iteritems():
			md[msgType] = md[msgType] + cnt
		for msgType, cnt in rd.iteritems():
			md[msgType] = md[msgType] + cnt
	# 获取少用的消息
	l = []
	for msg_type, cnt in md.iteritems():
		if cnt <= c:
			l.append((msg_type, cnt))
	# 排序
	l.sort(key=lambda it:it[1])
	# 打印
	print "Least ..."
	PrintHelp.pprint(l)

if "_HasLoad" not in dir():
	Logic_ToTime = AutoMessage.AllotMessage("Logic_ToTime", "逻辑进程改变时间")
