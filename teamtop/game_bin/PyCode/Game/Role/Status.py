#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Status")
#===============================================================================
# 角色状态
#===============================================================================
import Environment
import DynamicPath
from Util import Trace
from Util.File import TabFile
from Game.Role.Data import EnumInt1
from Game.Role import Event


Tips_1 = "依赖的状态%s不存在,无法进行下一步操作"
Tips_2 = "你处于#C(#FF0000)%s#n中,无法执行此操作"


Tips_3 = "%s依赖的状态%s不存在,无法进行下一步操作"
Tips_4 = "%s处于#C(#FF0000)%s#n中,无法执行此操作"

if "_HasLoad" not in dir():
	FL = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FL.AppendPath("Status")
	Statuss = {}
	StatusEve = {}
	
	LoginStatusReset = set()

class StatusInfo(TabFile.TabLine):
	FilePath = FL.FilePath("StatusInfo.txt")
	UseCache = False
	def __init__(self):
		self.name = str
		self.zhname = str
		#self.relation  状态关系列表  (运行时定义)
		self.loginReset = int

def LoadConfig():
	NameStatuss = {}
	for si in StatusInfo.ToClassType():
		# 状态名称在枚举中，状态名称唯一
		assert hasattr(EnumInt1, si.name)
		assert si.name not in NameStatuss
		NameStatuss[si.name] = si
		
		if si.loginReset:
			#登陆处理
			uindex = getattr(EnumInt1, si.name)
			if uindex in EnumInt1.StatusSet:
				LoginStatusReset.add(uindex)
			else:
				#不是状态！！配置表错了
				print "GE_EXC, status error not statues uindex(%s), name(%s)" % (uindex, si.name)
		
	tf = TabFile.TabFile(FL.FilePath("StatusRelation.txt"))
	tf.Read()
	# 正方形
	if len(tf.enNameList) != len(tf.dataList) + 2:
		print "GE_EXC, StatusRelation enName(%s) != dataList(%s)" % (len(tf.enNameList), len(tf.dataList))
		return
	# 状态名称在状态表中, 并且状态名称唯一
	se = set()
	for row in tf.dataList:
		assert row[0] in NameStatuss
		assert row[0] not in se
		se.add(row[0])
	
	#保证行列状态名称一致
	for name in tf.enNameList:
		if name == "name-name": continue
		if name == "n":continue
		se.remove(name)
	#TODO
	
	
	# 构建条件
	for row in tf.dataList:
		for idx, cell in enumerate(row):
			if idx == 0:
				relation = []
			elif idx == 1:
				continue
			else:
				name = tf.enNameList[idx]
				if cell == "T":
					#状态互相依赖
					relation.append((getattr(EnumInt1, name), NameStatuss[name], True))
				elif cell == "F":
					#状态互斥
					relation.append((getattr(EnumInt1, name), NameStatuss[name], False))
				else:
					#两个状态没任何联系
					continue
		#给对应的status对象构造一个关系列表
		NameStatuss[row[0]].relation = relation
		
	# 将状态名改为状态下标
	for name, status in NameStatuss.iteritems():
		Statuss[getattr(EnumInt1, name)] = status


def TryInStatus(role, idx):
	'''
	尝试进入某个状态， 如果不能进入某个状态则会智能提示
	@param role:角色
	@param idx:下标
	'''
	status = Statuss[idx]
	for re_idx, re_status, re_bool in status.relation:
		if role.GetI1(re_idx) is re_bool:
			continue
		# 显示消息
		if re_bool:
			role.Msg(2, 0, Tips_1 % re_status.zhname)
			print "GE_EXC, TryInStatus(%s) fail, Because need in %s status." % (idx, re_idx)
		else:
			role.Msg(2, 0, Tips_2 % re_status.zhname)
			print "GE_EXC, TryInStatus(%s) fail, Because need not in %s status." % (idx, re_idx)
		return False
	else:
		role.SetI1(idx, True)
		return True

def TryInStatus_Roles(roles, idx):
	'''
	尝试进入某个状态， 如果不能进入某个状态则会智能提示
	@param roles:角色
	@param idx:下标
	'''
	status = Statuss[idx]
	for role in roles:
		for re_idx, re_status, re_bool in status.relation:
			if role.GetI1(re_idx) is re_bool:
				continue
			# 显示消息
			roleName = role.GetRoleName()
			if re_bool:
				for orole in roles:
					orole.Msg(2, 0, Tips_3 % (roleName, re_status.zhname))
				print "GE_EXC, TryInStatus_Roles(%s) fail, Because need in %s status." % (idx, re_idx)
			else:
				for orole in roles:
					orole.Msg(2, 0, Tips_4 % (roleName, re_status.zhname))
				print "GE_EXC, TryInStatus_Roles(%s) fail, Because need not in %s status." % (idx, re_idx)
			return False
	for role in roles:
		role.SetI1(idx, True)
	return True

def ForceInStatus(role, idx):
	'''
	强制进入某个状态， 如果不能进入某个状态则会智能提示
	@param role:角色
	@param idx:下标
	'''
	if IsInStatus(role, idx):
		print "GE_EXC, repeat ForceInStatus (%s)" % idx
		Trace.StackWarn("GE_EXC, repeat ForceInStatus")
		return
	status = Statuss[idx]
	for re_idx, _, re_bool in status.relation:
		if role.GetI1(re_idx) is re_bool:
			continue
		# 显示消息
		if re_bool:
			print "GE_EXC, ForceInStatus (%s) warning, Because need in status(%s)." % (idx, re_idx)
		else:
			print "GE_EXC, ForceInStatus (%s)  warning, Because need not in status(%s)." % (idx, re_idx)
	role.SetI1(idx, True)

def ForceInStatus_Roles(roles, idx):
	'''
	强制进入某个状态， 如果不能进入某个状态则会智能提示
	@param role:角色
	@param idx:下标
	'''
	for role in roles:
		if IsInStatus(role, idx):
			print "GE_EXC, repeat ForceInStatus_Roles (%s)" % idx
			continue
		status = Statuss[idx]
		for re_idx, _, re_bool in status.relation:
			if role.GetI1(re_idx) is re_bool:
				continue
			# 显示消息
			if re_bool:
				print "GE_EXC, ForceInStatus_Roles (%s) fail, Because need  in status(%s)." % (idx, re_idx)
			else:
				print "GE_EXC, ForceInStatus_Roles (%s) fail, Because need not in status(%s)." % (idx, re_idx)
		role.SetI1(idx, True)

def CanInStatus(role, idx):
	'''
	是否可以进入这个状态
	@param role:
	@param idx:
	'''
	
	if IsInStatus(role, idx):
		return False
	
	status = Statuss[idx]
	for re_idx, re_status, re_bool in status.relation:
		if role.GetI1(re_idx) is re_bool:
			continue
		# 显示消息
		if re_bool:
			#依赖的状态不存在
			role.Msg(2, 0, Tips_1 % re_status.zhname)
			#print " CanInStatusin (%s) fail, Because need in status(%s)." % (idx, re_idx)
		else:
			#有互斥的状态
			role.Msg(2, 0, Tips_2 % re_status.zhname)
			#print " CanInStatusin (%s) fail, Because need not in status(%s)." % (idx, re_idx)
		return False
	
	return True


def CanBeInStatus(role, idx):
	'''
	是否可以被动进入这个状态(不打印，不提示)
	@param role:
	@param idx:
	'''
	
	if IsInStatus(role, idx):
		return False
	
	status = Statuss[idx]
	for re_idx, _, re_bool in status.relation:
		if role.GetI1(re_idx) is re_bool:
			continue
		return False
	
	return True


def CanInStatus_Roles(roles, idx):
	'''
	多个角色是否可以进入这个状态
	@param roles:角色列表
	@param idx:
	'''
	
	for role in roles:
		if IsInStatus(role, idx):
			return False
	
	status = Statuss[idx]
	for role in roles:
		for re_idx, re_status, re_bool in status.relation:
			if role.GetI1(re_idx) is re_bool:
				continue
			# 显示消息
			roleName = role.GetRoleName()
			if re_bool:
				for orole in roles:
					orole.Msg(2, 0, Tips_3 % (roleName, re_status.zhname))
				#print "GE_EXC CanInStatus_Roles in (%s) fail, Because need in status(%s). roleID(%s)" % (idx, re_idx, role.GetRoleID())
			else:
				for orole in roles:
					orole.Msg(2, 0, Tips_4 % (roleName, re_status.zhname))
				#print "GE_EXC CanInStatus_Roles in (%s) fail, Because need not in status(%s).roleID(%s)" % (idx, re_idx, role.GetRoleID())
			return False
	
	return True



def Outstatus(role, idx):
	'''
	出某个状态
	@param role:角色
	@param idx:下标
	'''
	assert idx in Statuss
	role.SetI1(idx, False)


def Outstatus_Roles(roles, idx):
	'''
	多个角色出某个状态
	@param roles:角色列表
	@param idx:下标
	'''
	assert idx in Statuss
	for role in roles:
		role.SetI1(idx, False)


def IsInStatus(role, idx):
	'''
	是否在某个状态
	@param role:角色
	@param idx:下标
	'''
	return role.GetI1(idx)

def IsOutStatus(role, idx):
	'''
	是否不在某个状态
	@param role:角色
	@param idx:下标
	'''
	return not role.GetI1(idx)

def MustOutStatus(role, idxs):
	'''
	是否不在某一系列状态
	@param role:角色
	@param idxs:状态下标集合
	'''
	for idx in idxs:
		if role.GetI1(idx) is False:
			continue
		print "you are in %s status." % Statuss[idx].zhname
		return False
	else:
		return True

def MustInStatus(role, idxs):
	'''
	是否在一系列状态中
	@param role:
	@param idxs:
	'''
	for idx in idxs:
		if role.GetI1(idx) is True:
			continue
		print "you are in %s status." % Statuss[idx].zhname
		return False
	else:
		return True



def AfterLogin(role, param):
	#登陆修正状态
	for sr in LoginStatusReset:
		role.SetI1(sr, False)

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadConfig()
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)



