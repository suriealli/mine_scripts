#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Team.TeamData")
#===============================================================================
# 组队数据基类(只关注数据)
# 请不要继承这个类
#===============================================================================


if "_HasLoad" not in dir():
	#分配的队伍ID
	AllotTeamID = 0

class TeamData(object):
	max_member_cnt = 3
	def __init__(self, role, teamType):
		#分配队伍ID
		global AllotTeamID
		AllotTeamID += 1
		
		self.team_type = teamType
		self.team_id = AllotTeamID
		self.union_id = role.GetUnionID()
		self.processId = role.GetJTProcessID()
		self.fb_id = 0
		#创建者就是队长
		self.leader = role
		#生成成员列表,需要有顺序
		self.members = [role, ]

	def IsTeamLeader(self, role):
		'''
		是否队长
		@param role:
		'''
		return self.leader == role
	
	def IsFull(self):
		'''
		队伍是否已满
		'''
		#队伍是否已经满了(包括离线)
		return len(self.members) >= self.max_member_cnt
	
	
	