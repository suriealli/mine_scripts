#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Scene.PublicScene")
#===============================================================================
# 公共场景
#===============================================================================

if "_HasLoad" not in dir():
	SceneCreateFun = {}
	SceneJoinFun = {}
	SceneBeforeLeaveFun = {}
	SceneRestoreFun = {}
	

#语法糖注册调用
def RegSceneAfterCreateFun(sceneID):
	#注册创建场景时调用的函数
	def f(fun):
		global SceneCreateFun
		if sceneID in SceneCreateFun:
			print "GE_EXC,repeat sceneID in RegSceneAfterCreateFun (%s)" % sceneID
		SceneCreateFun[sceneID] = fun
		return fun
	return f

def RegSceneAfterJoinRoleFun(sceneID):
	#注册进入场景时函数
	def f(fun):
		global SceneJoinFun
		if sceneID in SceneJoinFun:
			print "GE_EXC,repeat sceneID in RegSceneAfterJoinRoleFun (%s)" % sceneID
		SceneJoinFun[sceneID] = fun
		return fun
	return f

def RegSceneBeforeLeaveFun(sceneID):
	#注册离开场景前函数
	def f(fun):
		global SceneBeforeLeaveFun
		if sceneID in SceneBeforeLeaveFun:
			print "GE_EXC,repeat sceneID in RegSceneBeforeLeaveFun (%s)" % sceneID
		SceneBeforeLeaveFun[sceneID] = fun
		return fun
	return f

def RegSceneAfterRestoreFun(sceneID):
	#注册恢复场景函数
	def f(fun):
		global SceneRestoreFun
		if sceneID in SceneRestoreFun:
			print "GE_EXC,repeat sceneID in RegSceneAfterRestoreFun (%s)" % sceneID
		SceneRestoreFun[sceneID] = fun
		return fun
	return f


#测试用
#@RegSceneAfterCreateFun(3)
#def AfterCreate(scene):
#	pass
#
#
#@RegSceneAfterJoinRoleFun(3)
#def AfterJoin(scene, role):
#	pass
#
#
#@RegSceneBeforeLeaveFun(3)
#def AfterBeforeLeave(scene, role):
#	pass

#@RegSceneBeforeLeaveFun(3)
#def AfterRestore(scene, role):
#	#角色场景数据恢复
#	pass

