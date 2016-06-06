#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.GVE.GVEMirrorNPC")
#===============================================================================
# 注释
#===============================================================================
from Game.NPC.PrivateNPC import PrivateNPC

if "_HasLoad" not in dir():
	pass

class GVEMirrorNPC(PrivateNPC.MirrorNPC):
	def __init__(self, mirrorScene, index, npcData, clickFun = None):
		self.index = index
		npcType, x, y, direction, self.rewardId, self.mcid, self.fightType = npcData
		PrivateNPC.MirrorNPC.__init__(self, mirrorScene, npcType, x, y, direction, clickFun)

	def Destroy(self):
		#销毁
		PrivateNPC.MirrorNPC.Destroy(self)
