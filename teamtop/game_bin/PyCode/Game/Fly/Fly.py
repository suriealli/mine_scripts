#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fly.Fly")
#===============================================================================
# 传送卷轴
#===============================================================================
import Environment
import DynamicPath
import cRoleMgr
from Util.File import TabFile
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Role import Status
from Game.Role.Data import EnumInt1



if "_HasLoad" not in dir():
	FLY_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FLY_FILE_FOLDER_PATH.AppendPath("Fly")
	
	FlyWorld_Config_Dict = {}
	
	TraFly = AutoLog.AutoTransaction("TraFly", "飞鞋传送")


#世界地图传送
class FlyWorldConfig(TabFile.TabLine):
	FilePath = FLY_FILE_FOLDER_PATH.FilePath("FlyWorld.txt")
	def __init__(self):
		self.sceneID = int
		self.x = int
		self.y = int
		self.needLevel = int


def LoadFlyWorldConfig():
	global FlyWorld_Config_Dict
	for FC in FlyWorldConfig.ToClassType():
		if FC.sceneID in FlyWorld_Config_Dict:
			print "GE_EXC, repeat sceneID in LoadFlyWorldConfig (%s)" % FC.sceneID
		FlyWorld_Config_Dict[FC.sceneID] = FC

#########################################################################################

def FlyWorld(role, msg):
	'''
	世界地图传送
	@param role:
	@param msg: 场景ID
	'''
	#状态管理
	if not Status.CanInStatus(role, EnumInt1.ST_TP):
		return
	
	
	if Status.IsInStatus(role, EnumInt1.ST_Team) or Status.IsInStatus(role, EnumInt1.ST_InTeamMirror):
		return
	
	sceneId = msg
	if role.GetSceneID() == sceneId:
		return
	
	global FlyWorld_Config_Dict
	cfg = FlyWorld_Config_Dict.get(sceneId)
	if not cfg:
		print "GE_EXC not cfg in FlyWorld sceneId(%s) roleId (%s)" % (sceneId, role.GetRoleID())
		return
	
	if role.GetLevel() < cfg.needLevel:
		return
	
	role.Revive(sceneId, cfg.x, cfg.y)


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadFlyWorldConfig()
		
	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Fly_FlyWorld", "请求世界地图传送"), FlyWorld)
	
	