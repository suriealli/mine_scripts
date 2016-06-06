#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Control.GlobalControl.UniversalBuyControl")
#===============================================================================
# 全民团购控制模块
#===============================================================================
import Environment
import cComplexServer
from ComplexServer.API import GlobalHttp

if "_HasLoad" not in dir():
	#跨服数据的初始值
	INIT_UBUY_GLOBAL_DATA = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0}

def AfterNewDay():
	'''
	全民团购
	'''
	global INIT_UBUY_GLOBAL_DATA
	GlobalHttp.SetGlobalDataByDict(INIT_UBUY_GLOBAL_DATA)
	
if "_HasLoad" not in dir():
	if Environment.HasControl:
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)