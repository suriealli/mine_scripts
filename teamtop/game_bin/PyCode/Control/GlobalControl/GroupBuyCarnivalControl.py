#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Control.GlobalControl.GroupBuyCarnivalControl")
#===============================================================================
# 团购嘉年华控制模块
#===============================================================================
import Environment
import cComplexServer
from Common.Other import GlobalDataDefine
from ComplexServer.API import GlobalHttp

if "_HasLoad" not in dir():
	pass

def AfterNewDay():
	'''
	团购嘉年华全局购买总数 跨天重置 
	'''
	GlobalHttp.SetGlobalData(GlobalDataDefine.GroupBuyCarnivalDataKey,0)
	
if "_HasLoad" not in dir():
	if Environment.HasControl:
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)	