#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.NPC.NpcBase.NpcBase")
#===============================================================================
# 一些基础NPC
#===============================================================================
from Game.NPC import NPCCfgFun
from Game.Role.Data import EnumInt1
from Game.Role import Status


#传送门
class NpcTP(object):
	def __init__(self, npcId, sceneID, posX, posY):
		'''
		传送门
		@param npcId:
		@param sceneID:
		@param posX:
		@param posY:
		'''
		self.sceneID = sceneID
		self.posX = posX
		self.posY = posY
		
		NPCCfgFun.RegNPCCfgFunEx(npcId, self)
	
	def __call__(self, role):
		if not Status.CanInStatus(role, EnumInt1.ST_TP):
			return
		role.Revive(self.sceneID, self.posX, self.posY)





