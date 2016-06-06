#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.NPC.PrivateNPC.FBNPC")
#===============================================================================
# 副本私有NPC
#===============================================================================
from Game.NPC.PrivateNPC import PrivateNPC
from Game.FB import FBReward


#副本战斗NPC
class FBFightNPC(PrivateNPC.PrivateNPC):
	def __init__(self, role, index, npcData, clickFun = None):
		self.index = index#从0开始
		npcType, x, y, direction, self.rewardId, self.fightId, self.fightType = npcData
		PrivateNPC.PrivateNPC.__init__(self, role, npcType, x, y, direction, clickFun)

	def Destroy(self):
		#销毁
		PrivateNPC.PrivateNPC.Destroy(self)
		if self.rewardId:
			#奖励
			return FBReward.RewardRole(self.role, self.rewardId, self.index)
		
		return None, None
		
		
#恶魔深渊战斗NPC
class EvilHoleFightNPC(PrivateNPC.PrivateNPC):
	def __init__(self, role, npcData, clickFun = None):
		npcType, x, y, direction, self.fightId, self.fightType = npcData
		PrivateNPC.PrivateNPC.__init__(self, role, npcType, x, y, direction, clickFun)

	def Destroy(self):
		#销毁
		PrivateNPC.PrivateNPC.Destroy(self)


