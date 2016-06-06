#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Control.GlobalControl.GroupBuyPartyControl")
#===============================================================================
# 团购派对控制模块
#===============================================================================
import Environment
import cComplexServer
from Common.Other import GlobalDataDefine
from ComplexServer.API import GlobalHttp

if "_HasLoad" not in dir():
	pass

def AfterNewDay():
	'''
	团购派对全局购买总数 跨天重置 
	'''
	GlobalHttp.SetGlobalData(GlobalDataDefine.GroupBuyPartyDataKey_1, 0)
	GlobalHttp.SetGlobalData(GlobalDataDefine.GroupBuyPartyDataKey_2, 0)
	
if "_HasLoad" not in dir():
	if Environment.HasControl:
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)	