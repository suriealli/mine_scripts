#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("ComplexServer.CtrlC")
#===============================================================================
# 信号模块(在控制台输入组合按键触发逻辑)
#===============================================================================
import signal
import Environment

def OnCtrlC(num, frame):
	if num != 2:
		return
	#重载所有的脚本
	from ComplexServer import GMEXE
	GMEXE.ReloadAll()


def OnCtrlBreak(num, frame):
	if num != 21:
		return
	#踢掉所有的角色
	import cRoleMgr
	for role in cRoleMgr.GetAllRole():
		role.Kick(1, 1)


if "_HasLoad" not in dir():
	if Environment.IsWindows and Environment.HasLogic:
		signal.signal(signal.SIGINT, OnCtrlC)
		signal.signal(signal.SIGBREAK, OnCtrlC)
