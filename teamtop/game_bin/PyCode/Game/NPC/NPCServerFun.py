#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.NPC.NPCServerFun")
#===============================================================================
# 服务器创建的NPC
#===============================================================================

if "_HasLoad" not in dir():
	NPCServerOnClickFun = {}


def RegNPCServerOnClickFun(npcType):
	#注册函数
	def f(fun):
		global NPCServerOnClickFun
		if not npcType:
			print "GE_EXC, error type in RegNPCServerOnClickFun (%s, %s)" % (npcType, fun)
		if npcType in NPCServerOnClickFun:
			print "GE_EXC,repeat npcType in RegNPCServerFun (%s)" % npcType
		NPCServerOnClickFun[npcType] = fun
		return fun
	return f

def RegNPCServerOnClickFunEx(npcType, fun):
	if not npcType:
		print "GE_EXC, error type in RegNPCServerOnClickFun (%s, %s)" % (npcType, fun)
	if npcType in NPCServerOnClickFun:
		print "GE_EXC,repeat npcType in RegNPCServerFun (%s)" % npcType
	NPCServerOnClickFun[npcType] = fun
