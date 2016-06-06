#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Restore")
#===============================================================================
# 客户端重新连接的时候按顺序还原客户端数据
# 一般的恢复流程都是把客户端缺失的数据重新同步一次
# 极少情况下会做一下恢复的数据操作逻辑
# 玩家断线其实就是一个控制权暂时交给服务器托管的一个过程，重新连接后，一般不会影响当前role的具体逻辑
# 所以这个恢复大体上是把这个role当前拥有的数据重新同步一次给客户端
# 做个比喻就是电脑的显示器，键盘，鼠标断电了，主机还是正常的，重新通电后只是会把当前屏幕的信息同步显示一次，并重新活动控制权。
#===============================================================================
from Game.Role.Data import EnumTempInt64
from Game.Task.MainTaskFight import TaskFightBase


def RestoreClient(role):
	#恢复数据流程
	RestoreScene(role)
	RestoreMainTaskFight(role)
	RestoreFight(role)


def RestoreFight(role):
	from Game.Fight import Fight
	Fight.RestoreFight(role)


def RestoreScene(role):
	#先尝试恢复副本
	from Game.Scene import MirrorBase
	if MirrorBase.RestoreMirror(role) is True:
		return
	#不在副本内，恢复公共场景
	scene = role.GetScene()
	if scene:
		scene.RestoreRole(role)
	else:
		print "GE_EXC, RestorePublicScene error "


def RestoreMainTaskFight(role):
	#尝试恢复主线任务战斗中的特殊数据
	tstep = role.GetTI64(EnumTempInt64.MainTaskFightStep)
	if not tstep:
		return
	role.SendObj(TaskFightBase.MianTask_Fight, tstep)
