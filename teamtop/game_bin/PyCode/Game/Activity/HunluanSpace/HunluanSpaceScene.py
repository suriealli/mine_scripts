#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.HunluanSpace.HunluanSpaceScene")
#===============================================================================
# 混乱时空场景
#===============================================================================
import Environment
from Game.Scene import PublicScene
from Game.Role.Data import EnumTempObj, EnumInt1
from Game.Role import Status

if "_HasLoad" not in dir():
	HSDemonSceneList = range(316, 325)
	HSDevilSceneList = range(326, 335)
	
def AfterJoinHunluanSpace(scene, role):
	spaceRole = role.GetTempObj(EnumTempObj.SpaceRole)
	if not spaceRole:
		return
	spaceRole.union_obj.add_union_role(role)
	spaceRole.sync_data()
	
	Status.ForceInStatus(role, EnumInt1.ST_HunluanSpace)
	
def BeforeLeaveHunluanSpace(scene, role):
	Status.Outstatus(role, EnumInt1.ST_HunluanSpace)
	
	spaceRole = role.GetTempObj(EnumTempObj.SpaceRole)
	if not spaceRole or not spaceRole.role:
		return
	spaceRole.union_obj.del_union_role(role)
	spaceRole.role = None
	
def RegHunluanSpaceSceneFun():
	global HSDevilSceneList, HSDemonSceneList
	for sceneId in HSDevilSceneList:
		PublicScene.SceneJoinFun[sceneId] = AfterJoinHunluanSpace
		PublicScene.SceneBeforeLeaveFun[sceneId] = BeforeLeaveHunluanSpace
	
	for sceneId in HSDemonSceneList:
		PublicScene.SceneJoinFun[sceneId] = AfterJoinHunluanSpace
		PublicScene.SceneBeforeLeaveFun[sceneId] = BeforeLeaveHunluanSpace
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and (not Environment.IsCross):
		RegHunluanSpaceSceneFun()

