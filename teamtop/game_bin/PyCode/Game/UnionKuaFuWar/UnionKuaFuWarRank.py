#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.UnionKuaFuWar.UnionKuaFuWarRank")
#===============================================================================
# 注释
#===============================================================================
from Game.Role import Rank

class UnionKuaFuUnionRank(Rank.LittleRank):
	def __init__(self, maxRankSize):
		Rank.LittleRank.__init__(self, maxRankSize)
	
	# 返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		return v1[2] < v2[2]
	
class UnionKuaFuUnionRoleRank(Rank.LittleRank):
	def __init__(self, maxRankSize):
		Rank.LittleRank.__init__(self, maxRankSize)
	
	# 返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		return v1[2] < v2[2]

class UnionKuaFuTotalRoleRank(Rank.LittleRank):
	def __init__(self, maxRankSize):
		Rank.LittleRank.__init__(self, maxRankSize)
	
	# 返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		return v1[2] < v2[2]
	
