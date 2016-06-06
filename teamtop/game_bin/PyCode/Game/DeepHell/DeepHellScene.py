#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.DeepHell.DeepHellScene")
#===============================================================================
# 深渊炼狱 Scene
#===============================================================================
import Environment
from Game.Scene import PublicScene
from Game.DeepHell import DeepHellCross, DeepHellDefine


def AfterRevive(role, regparam):
	'''
	本服来到跨服调用 
	'''
	role.RegTick(DeepHellDefine.REVIVE_DELAY, DeepHellCross.ReviveDeepHell, regparam)
	

def AfterJoinScene(scene, role):
	'''
	角色进入场景后处理	
	'''
	pass


def BeforeLeaveScene(scene, role):
	'''
	角色离开场景前处理	
	'''
	pass


def RegSceneFun(callArgvs = None, regParam = None):
	'''
	注册场景进入推出处理
	'''
	for _, sceneIdList in DeepHellDefine.DeepHell_SceneConfig_Dict.iteritems():
		for sceneId in sceneIdList:
			PublicScene.SceneJoinFun[sceneId] = AfterJoinScene
			PublicScene.SceneBeforeLeaveFun[sceneId] = BeforeLeaveScene	


if "_HasLoad" not in dir():
	if Environment.HasLogic and Environment.IsCross:
		RegSceneFun()
