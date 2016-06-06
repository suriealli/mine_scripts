#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Control.GlobalControl.DEGroupBuyControl")
#===============================================================================
# 双十一2015 团购送神石控制模块
#===============================================================================
import Environment
import cComplexServer
from Common.Other import GlobalDataDefine
from ComplexServer.API import GlobalHttp

if "_HasLoad" not in dir():
	pass

def AfterNewDay():
	'''
	团购送神石 全局购买总数 跨天重置 
	'''
	GlobalHttp.SetGlobalData(GlobalDataDefine.DEGroupBuyDataKey,0)
	
if "_HasLoad" not in dir():
	if Environment.HasControl:
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)	