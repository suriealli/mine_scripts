#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.SystemRank.SystemRankBase")
#===============================================================================
# 系统排行榜基类
#===============================================================================
from Game.Role import Rank


class SysRankBase(Rank.SmallRoleRank):
	defualt_data_create = dict				#持久化数据需要定义的数据类型
	max_rank_size = 100						#最大排行榜 100个
	dead_time = (2038, 1, 1)
	# 打开排行榜
	def Open(self, role, msg = None):
		role.SendObj(self.Msg_Init, self.data)
	
	def ReturnData(self):
		return self.data