#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.CI8")
#===============================================================================
# 客户端请求设置客户端专用数组
#===============================================================================
import traceback
import cRoleMgr
import Environment
from Common.Message import AutoMessage


def OnSetCI8(role, msg):
	#客户端请求设置CI8
	try:
		role.SetCI8(*msg)
	except:
		#失败了
		role.WPE()
		traceback.print_exc()


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_SetCI8", "请求设置CI8"), OnSetCI8)

