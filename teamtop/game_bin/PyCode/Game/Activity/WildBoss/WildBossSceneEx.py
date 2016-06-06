#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.WildBoss.WildBossSceneEx")
#===============================================================================
# 野外寻宝场景注册
#===============================================================================
import Environment
from Game.Activity.WildBoss import WildBossScene
from Game.Scene import PublicScene

def RegSceneAfterJoinWildBossFun():
	for _, sceneIdList in WildBossScene.WildBoss_SceneConfig_Dict.iteritems():
		for sceneId in sceneIdList:
			PublicScene.SceneJoinFun[sceneId] = WildBossScene.AfterJoinEx
			PublicScene.SceneBeforeLeaveFun[sceneId] = WildBossScene.BeforeLeaveEx


if "_HasLoad" not in dir():
	if Environment.HasLogic and Environment.IsCross:
		RegSceneAfterJoinWildBossFun()
