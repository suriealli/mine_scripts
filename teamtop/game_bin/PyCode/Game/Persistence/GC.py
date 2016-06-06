#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Persistence.GC")
#===============================================================================
# 回收内存
#===============================================================================
import gc
import cProcess
import cComplexServer
from Game.Persistence import Base, BigTable

def CheckLoad(callargv, regparam):
	if Base.CheckAllLoadReturn() and BigTable.CheckAllLoadReturn():
		gc.collect()
		cProcess.MallocTrim()
		print "BLUE, system load all persistence data."
	else:
		cComplexServer.RegTick(10, CheckLoad, None)

if "_HasLoad" not in dir():
	cComplexServer.RegTick(10, CheckLoad)
