#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.NPC.NPCCfgFun")
#===============================================================================
# 配置的NPC函数
#===============================================================================
import traceback



if "_HasLoad" not in dir():
	NPCCfgFun_Dict = {}


def OnClick(role, npcId):
	'''
	当有个角色点击了这个NPC触发的函数
	@param role:点击NPC的角色对象
	@param npcType:npcType类型
	'''
	global NPCCfgFun_Dict
	fun = NPCCfgFun_Dict.get(npcId)
	if not fun:
		return
	
	try:
		fun(role)
	except:
		traceback.print_exc()

#语法糖
def RegNPCCfgFun(npcId):
	#注册函数
	def f(fun):
		global NPCCfgFun_Dict
		if npcId in NPCCfgFun_Dict:
			print "GE_EXC,repeat npcId in RegNPCCfgFun (%s)" % npcId
		NPCCfgFun_Dict[npcId] = fun
		return fun
	return f


#直接注册
def RegNPCCfgFunEx(npcId, fun):
	global NPCCfgFun_Dict
	if npcId in NPCCfgFun_Dict:
		print "GE_EXC,repeat npcId in RegNPCCfgFun (%s)" % npcId
	NPCCfgFun_Dict[npcId] = fun

