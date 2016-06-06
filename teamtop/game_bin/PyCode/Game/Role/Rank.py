#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Rank")
#===============================================================================
# 排行榜
#===============================================================================
import cRoleMgr
from Game.Role import Event
from Game.Persistence import Base

# 小型持久化排行榜，支持即时更新，动态通知
class SmallRoleRank(Base.ObjBase):
	defualt_data_create = dict		#持久化数据需要定义的数据类型
	max_rank_size = 3				#最大排行榜
	max_role_size = 0				#最大角色观察数
	Msg_Init = 0					#同步客户端所有的数据
	Msg_HasData = 0					#同步客户端一个数据
	Msg_Open = 0					#客户端打开排行榜
	Msg_Close = 0					#客户端关闭排行榜
	name = ""
	dead_time = (2013, 1, 1)
	needSync = True
	isSaveBig = False
	def __init__(self):
		Base.ObjBase.__init__(self, self.name, self.dead_time, self.AfterLoadFun, self.isSaveBig)
		if self.needSync is True:
			# 注册打开排行榜函数
			cRoleMgr.RegDistribute(self.Msg_Open, self.Open)
		self.roles = set()
		# 如果有观察角色，注册角色离线清理，注册关闭排行榜函数
		if self.max_role_size:
			Event.RegEvent(Event.Eve_BeforeExit, self.BeforeRoleExit)
			cRoleMgr.RegDistribute(self.Msg_Close, self.Close)
	
	# 这个需被子类重载，返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		return v1 < v2
	
	# 这个按需被子类重载，看在载入玩数据后是否还有下一步处理
	def AfterLoadFun(self):
		
		# 优化加速
		MAX_RANK_SIZE = self.max_rank_size
		DATA = self.data
		BUILD_MIN_VALUE = self.BuildMinValue
		#还是先构建一个最小值吧。
		BUILD_MIN_VALUE()
		# 如果排行榜爆了，需要重构数据
		if MAX_RANK_SIZE <= len(self.data):
			# 初始化最小值
			# 重构数据
			while 1:
				BUILD_MIN_VALUE()
				# 排行榜爆了
				if MAX_RANK_SIZE < len(DATA):
					del DATA[self.min_role_id]
					self.changeFlag = True
				else:
					break
	
	# 角色离线清理
	def BeforeRoleExit(self, role):
		self.roles.discard(role)
	
	# 计算这个排行榜的最小值和对于的角色
	def BuildMinValue(self):
		# 获取第一个role_id value
		for self.min_role_id, self.min_value in self.data.iteritems():
			break
		SIL = self.IsLess
		for role_id, value in self.data.iteritems():
			if SIL(value, self.min_value):
				self.min_value = value
				self.min_role_id = role_id
	
	# 有数据来了
	def HasData(self, role_id, value):
		# 很重要的一点，排行值只能是历史最大值
		old_value = self.data.get(role_id)
		if old_value and (not self.IsLess(old_value, value)):
			return
		
		# 排行榜未满
		if self.max_rank_size > len(self.data):
			# 入榜
			self.data[role_id] = value
			self.changeFlag = True
			# 有可能导致排行榜满了
			if self.max_rank_size == len(self.data):
				self.BuildMinValue()
			# 通知观察角色
			for role in self.roles:
				role.SendObj(self.Msg_HasData, (role_id, value))
		# 排行榜已满，并且排行值大于最小值
		elif self.IsLess(self.min_value, value):
			# 入榜
			self.data[role_id] = value
			self.changeFlag = True
			# 有可能导致排行榜爆了
			if self.max_rank_size < len(self.data):
				del self.data[self.min_role_id]
				self.BuildMinValue()
			elif role_id == self.min_role_id:
				#自己本身就是最小值，需要重新构建一个
				self.BuildMinValue()
				
			# 通知观察角色
			for role in self.roles:
				role.SendObj(self.Msg_HasData, (role_id, value))
	
	# 获取角色的排名（没上榜返回0）
	def GetRank(self, role_id):
		value = self.data.get(role_id)
		if value is None: return 0
		_v = value[0]
		rank = 1
		for _role_id, _value in self.data.iteritems():
			__v = _value[0]
			# 如果排行值大于，或者排行值等于并且role_id大于，则排在前面
			if (__v > _v) or (__v == _v and _role_id > role_id):
				rank += 1
		return rank
	
	# 获取排行列表
	def GetSort(self):
		pass
	
	# 打开排行榜
	def Open(self, role, msg = None):
		role.SendObj(self.Msg_Init, self.data)
		# 如果可以动态观察排行榜，并且该角色在排行榜中，加入观察者集合
		if len(self.roles) < self.max_role_size and role.GetRoleID() in self.data:
			self.roles.add(role)
	
	# 关闭排行榜
	def Close(self, role, msg = None):
		self.roles.discard(role)


#实时排行榜，不持久化
class LittleRank(object):
	def __init__(self, maxSize = 0):
		self.data = {}
		self.max_rank_size = maxSize
		self.hasData = False
		
	# 这个需被子类重载，返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		return v1 < v2
	
	# 计算这个排行榜的最小值和对于的角色
	def BuildMinValue(self):
		# 获取第一个role_id value
		for self.min_role_id, self.min_value in self.data.iteritems():
			break
		SIL = self.IsLess
		for role_id, value in self.data.iteritems():
			if SIL(value, self.min_value):
				self.min_value = value
				self.min_role_id = role_id
	
	# 有数据来了
	def HasData(self, role_id, value):
		if self.hasData is False:
			#第一次添加数据
			self.hasData = True
			self.data[role_id] = value
			self.min_role_id = role_id
			self.min_value = value
			return
		
		# 很重要的一点，排行值只能是历史最大值
		old_value = self.data.get(role_id)
		if old_value and (not self.IsLess(old_value, value)):
			return
		# 排行榜未满
		if self.max_rank_size > len(self.data):
			# 入榜
			self.data[role_id] = value
			# 有可能导致排行榜满了
			if self.max_rank_size == len(self.data):
				self.BuildMinValue()
		# 排行榜已满，并且排行值大于最小值
		elif self.IsLess(self.min_value, value):
			# 入榜
			self.data[role_id] = value
			# 有可能导致排行榜爆了
			if self.max_rank_size < len(self.data):
				del self.data[self.min_role_id]
				self.BuildMinValue()
			elif role_id == self.min_role_id:
				#自己本身就是最小值，需要重新构建一个
				self.BuildMinValue()

