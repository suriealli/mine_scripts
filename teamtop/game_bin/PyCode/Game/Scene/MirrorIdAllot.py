#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Scene.MirrorIdAllot")
#===============================================================================
# 分配副本全局ID
#===============================================================================

if "_HasLoad" not in dir():
	MirrorId_Allot = 0

def AllotMirrorID():
	global MirrorId_Allot
	MirrorId_Allot += 1
	return MirrorId_Allot
	





