#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.WildBoss.WildBossScene")
#===============================================================================
# 注册野外寻宝场景
#===============================================================================
from Game.Scene import PublicScene

if "_HasLoad" not in dir():
	#所有场景ID列表
	WildBoss_SceneConfig_Dict = {1:range(80, 85) + range(86, 102), 2:range(102, 122), 3:range(122, 142), 4:range(142, 162), 5:range(544, 564), 6:range(702, 722)}
	#准备间场景
	WildBoss_ReadySceneID = 85
	
@PublicScene.RegSceneAfterJoinRoleFun(WildBoss_ReadySceneID)
def AfterJoin(scene, role):
	pass
	#AfterRevive(role, role.GetLevel())
	
def AfterRevive(role, regparam):
	#5s后传送到野外寻宝场景
	from Game.Activity.WildBoss import WildBoss
	role.RegTick(5, WildBoss.ReviveWildBoss, regparam)
	

def AfterJoinEx(scene, role):
	pass
	role.SetAppStatus(7)
		
def BeforeLeaveEx(scene, role):
	role.SetAppStatus(0)


