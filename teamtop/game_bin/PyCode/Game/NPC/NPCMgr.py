#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.NPC.NPCMgr")
#===============================================================================
# NPC管理器
#===============================================================================
import cNPCMgr
import Environment
import DynamicPath
from Util.File import TabFile
from Game.NPC import NPCServerFun
from Game.Role import Event


if "_HasLoad" not in dir():
	NPCConfig_Dict = {}
	
	SceneNPC_Dict = {}
	
	NPC_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	NPC_FILE_FOLDER_PATH.AppendPath("Npc")

class NPCConfig(TabFile.TabLine):
	FilePath = NPC_FILE_FOLDER_PATH.FilePath("NpcConfig.txt")
	def __init__(self):
		self.Type = int
		self.name = str
		self.clickLen = int
		self.clickType = int
		self.resname = int
		self.isMovingNPC = int

class SceneNPC(TabFile.TabLine):
	FilePath = NPC_FILE_FOLDER_PATH.FilePath("SceneNpc.txt")
	def __init__(self):
		self.sceneID = int
		self.npcID = int
		self.npcType = int
		self.npcPosX = int
		self.npcPosY = int
		
		self.transportSceneId = self.GetEvalByString
		self.tpPosX = self.GetEvalByString
		self.tpPosY = self.GetEvalByString
	
	def SetClickLen(self, l):
		self.clickLen = l

def LoadNPCConfig():
	global NPCConfig_Dict
	for NC in NPCConfig.ToClassType():
		cNPCMgr.CreateNPCTemplate(NC.Type, NC.name, NC.clickLen, NC.clickType, NC.isMovingNPC)
		NPCConfig_Dict[NC.Type] = NC


def LoadSceneNPC():
	global SceneNPC_Dict
	global NPCConfig_Dict
	
	for SN in SceneNPC.ToClassType():
		SceneNPC_Dict[SN.npcID] = SN
		cNPCMgr.CreateNPCConfigObj(SN.npcID, SN.sceneID, SN.npcType, SN.npcPosX, SN.npcPosY)
		
		npcCfg = NPCConfig_Dict.get(SN.npcType)
		if not npcCfg:
			print "GE_EXC, LoadSceneNPC error not npcType  npcid = (%s)" % SN.npcID
			continue
		
		SN.SetClickLen(npcCfg.clickLen)

def LoadNPCClickFun():
	#C++调用
	if Environment.HasLogic:
		for npcType, fun in NPCServerFun.NPCServerOnClickFun.iteritems():
			cNPCMgr.LoadNPCClickFun(npcType, fun)
		
		#传送门配置
		global SceneNPC_Dict
		from Game.NPC.NpcBase import NpcBase
		for npcId, cfg in SceneNPC_Dict.iteritems():
			if cfg.transportSceneId:
				if not cfg.tpPosX or not cfg.tpPosY:
					print "GE_EXC, error in sceneNPC config, pos Null NPCid = (%s)" % cfg.npcID
				NpcBase.NpcTP(npcId, cfg.transportSceneId, cfg.tpPosX, cfg.tpPosY)
	
def GetNPCName(npcType):
	global NPCConfig_Dict
	if npcType not in NPCConfig_Dict:
		return ""
	return NPCConfig_Dict[npcType].name

def AfterLoadScript(p1, p2):
	Event.TriggerEvent(Event.Eve_AfterLoadSceneNPC, SceneNPC_Dict, None)


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadNPCConfig()
		LoadSceneNPC()
		Event.RegEvent(Event.Eve_AfterLoadSucceed, AfterLoadScript)


