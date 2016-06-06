#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Scene.SceneMgr")
#===============================================================================
# 场景管理
#===============================================================================
import cSceneMgr
import Environment
import DynamicPath
from Util.File import TabFile
from Game.Scene import MapMgr, PublicScene

#先载入这个模块,初始化配置
MapMgr

#场景类型,参考C++定义(SceneType)
enSceneBase = 1
enScenePublic = 2
enMirrorBase = 3
enSingleMirror = 4
enMultiMirror = 5

if "_HasLoad" not in dir():
	SCENE_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	SCENE_FILE_FOLDER_PATH.AppendPath("SceneConfig")
	#场景配置
	SceneConfig_Dict = {}
	#安全坐标
	MapSafePos_Dict = {}
	

class SceneConfig(TabFile.TabLine):
	FilePath = SCENE_FILE_FOLDER_PATH.FilePath("SceneConfig.txt")
	def __init__(self):
		self.SceneId = int
		self.MapId = int
		self.SceneName = str
		self.SceneType = int#场景配置类型
		self.AreaSize = int
		self.IsSaveData = int
		self.CanSeeOther = int
		self.fireLimit = int
		
		self.IsCross = self.GetEvalByString
		
	def Check(self):
		if self.IsSaveData and self.SceneType != enScenePublic:
			print "GE_EXC, error in SceneConfig (%s), can not save role data" % self.SceneId
		
		if self.IsSaveData and self.IsCross:
			print "GE_EXC, error in SceneConfig (%s), can not save role data" % self.SceneId
		
		
#地图安全坐标
class MapSafePosConfig(TabFile.TabLine):
	FilePath = SCENE_FILE_FOLDER_PATH.FilePath("MapSafePos.txt")
	def __init__(self):
		self.mapID = int
		self.safeX = int
		self.safeY = int
		

def LoadSceneConfig():
	global SceneConfig_Dict
	for SC in SceneConfig.ToClassType():
		if SC.SceneId in SceneConfig_Dict:
			print "GE_EXC, error in LoadSceneConfig repeat id = (%s)" % SC.SceneId
		SceneConfig_Dict[SC.SceneId] = SC
		SC.Check()
		
def CreataPublicScene():
	#逻辑进程初始化完毕调用，创建所有的公共场景
	global SceneConfig_Dict
	SCPS = cSceneMgr.CreatePublicScene
	
	#获取注册的3个场景相关函数
	PSCG = PublicScene.SceneCreateFun.get
	PSJG = PublicScene.SceneJoinFun.get
	PSBG = PublicScene.SceneBeforeLeaveFun.get
	PSRG = PublicScene.SceneRestoreFun.get
	for SC in SceneConfig_Dict.itervalues():
		if SC.IsCross and not Environment.IsCross:
			#非跨服不创建跨服场景
			continue
		if SC.SceneType == 2:
			#只创建普通公共场景
			SID = SC.SceneId
			SCPS(SID, SC.SceneName, SC.MapId, SC.AreaSize, SC.IsSaveData, SC.CanSeeOther, PSCG(SID), PSJG(SID), PSBG(SID), PSRG(SID))
	
	#载入安全坐标配置
	global MapSafePos_Dict
	SL = cSceneMgr.LoadMapSafePos
	for mapId, m in MapSafePos_Dict.iteritems():
		SL(mapId, m.safeX, m.safeY)
	
def LoadMapSafePosConfig():
	#安全坐标
	global MapSafePos_Dict
	for MSPC in MapSafePosConfig.ToClassType():
		MapSafePos_Dict[MSPC.mapID] = MSPC


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadSceneConfig()
		LoadMapSafePosConfig()


