#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.LostScene.LostSceneNPC")
#===============================================================================
# 注释
#===============================================================================
#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.CrossTeamTower.CTTNPC")
#===============================================================================
# 迷失之境NPC
#===============================================================================
from Game.NPC.PrivateNPC import PrivateNPC

class LostSceneMonsterNPC(PrivateNPC.MirrorNPC):
	def __init__(self, mirrorScene, npcData, roleId = None):
		self.roleId = roleId
		npcType, (x, y, direction) = npcData
		self.x = x
		self.y = y
		PrivateNPC.MirrorNPC.__init__(self, mirrorScene, npcType, x, y, direction)

	def Destroy(self):
		#销毁
		PrivateNPC.MirrorNPC.Destroy(self)
	
	def GetPos(self):
		return self.x, self.y

