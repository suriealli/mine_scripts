#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.CrossTeamTower.CTTNPC")
#===============================================================================
# 虚空幻境NPC
#===============================================================================
from Game.NPC.PrivateNPC import PrivateNPC


#普通怪物
class CTTMonsterNPC(PrivateNPC.MirrorNPC):
	def __init__(self, mirrorScene, index, npcData, clickFun = None):
		self.index = index
		npcType, x, y, direction, self.mcid, self.fightType, self.rewardcfg, = npcData
		PrivateNPC.MirrorNPC.__init__(self, mirrorScene, npcType, x, y, direction, clickFun)

	def Destroy(self):
		#销毁
		PrivateNPC.MirrorNPC.Destroy(self)

#传送门
class CTTDoorNPC(PrivateNPC.MirrorNPC):
	def __init__(self, mirrorScene, index, npcData, clickFun = None):
		self.index = index
		npcType, x, y, direction = npcData
		PrivateNPC.MirrorNPC.__init__(self, mirrorScene, npcType, x, y, direction, clickFun)

	def Destroy(self):
		#销毁
		PrivateNPC.MirrorNPC.Destroy(self)