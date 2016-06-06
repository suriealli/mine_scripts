#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Observe")
#===============================================================================
# 角色观察模块(某些角色观察某些数据)
#===============================================================================
import cScriptMgr
import cNetMessage

class RoleDict(object):
	Msg_Init = 0
	Msg_Set = 0
	Msg_Del = 0
	def __init__(self, role, data):
		self.role = role
		self.data = data
		self.role.SendObj_NoExcept(self.Msg_Init, self.data)
	
	def __repr__(self):
		return repr(self.data)
	
	__hash__ = None
	
	def __len__(self):
		return len(self.data)
	
	def __getitem__(self, key):
		return self.data[key]
	
	def __setitem__(self, key, item):
		self.data[key] = item
		self.role.SendObj_NoExcept(self.Msg_Set, self.data)
	
	def __delitem__(self, key):
		del self.data[key]
		self.role.SendObj_NoExcept(self.Msg_Del, self.data)
	
	def clear(self):
		self.data.clear()
		self.role.SendObj_NoExcept(self.Msg_Init, self.data)
	
	def keys(self):
		return self.data.keys()
	
	def items(self):
		return self.data.items()
	
	def iteritems(self):
		return self.data.iteritems()
	
	def iterkeys(self):
		return self.data.iterkeys()
	
	def itervalues(self):
		return self.data.itervalues()
	
	def values(self):
		return self.data.values()
	
	def has_key(self, key):
		return key in self.data
	
	def get(self, key, failobj=None):
		if key not in self:
			return failobj
		return self[key]
	
	def pop(self, key):
		value = self.data.pop(key)
		self.role.SendObj_NoExcept(self.Msg_Del, self.data)
		return value
		
	def __contains__(self, key):
		return key in self.data

class RolesDict(object):
	Msg_Init = 0
	Msg_Set = 0
	Msg_Del = 0
	def __init__(self, data):
		self.roles = set()
		self.data = {}
		self.data.update(data)
	
	def add_role(self, role):
		self.roles.add(role)
		role.SendObj_NoExcept(self.Msg_Init, self.data)
	
	def del_role(self, role):
		self.roles.discard(role)
	
	def __repr__(self):
		return repr(self.data)
	
	__hash__ = None
	
	def __len__(self):
		return len(self.data)
	
	def __getitem__(self, key):
		return self.data[key]
	
	def __setitem__(self, key, item):
		self.data[key] = item
		cNetMessage.PackPyMsg(self.Msg_Set, (key, item))
		for role in self.roles:
			role.BroadMsg_NoExcept()
	
	def __delitem__(self, key):
		del self.data[key]
		cNetMessage.PackPyMsg(self.Msg_Del, key)
		for role in self.roles:
			role.BroadMsg_NoExcept()
	
	def clear(self):
		self.data.clear()
		cNetMessage.PackPyMsg(self.Msg_Init, self.data)
		for role in self.roles:
			role.BroadMsg_NoExcept()
	
	def keys(self):
		return self.data.keys()
	
	def items(self):
		return self.data.items()
	
	def iteritems(self):
		return self.data.iteritems()
	
	def iterkeys(self):
		return self.data.iterkeys()
	
	def itervalues(self):
		return self.data.itervalues()
	
	def values(self):
		return self.data.values()
	
	def has_key(self, key):
		return key in self.data
	
	def get(self, key, failobj=None):
		if key not in self:
			return failobj
		return self[key]
	
	def __contains__(self, key):
		return key in self.data

class RolesEntrustDict(object):
	Msg_Init = 0
	def __init__(self, data):
		self.roles = set()
		self.data = {}
		self.data.update(data)
		self.index = cScriptMgr.AllotFlagIndex()
		cScriptMgr.SetClearFun(self.index, self.sync_role)
		
	def add_role(self, role):
		self.roles.add(role)
	
	def del_role(self, role):
		self.roles.discard(role)
	
	def sync_role(self):
		cNetMessage.PackPyMsg(self.Msg_Init, self.data)
		for role in self.roles:
			role.BroadMsg_NoExcept()
	
	def __repr__(self):
		return repr(self.data)
	
	__hash__ = None
	
	def __len__(self):
		return len(self.data)
	
	def __getitem__(self, key):
		return self.data[key]
	
	def __setitem__(self, key, item):
		self.data[key] = item
		cScriptMgr.DirtyFlag(self.index)
	
	def __delitem__(self, key):
		del self.data[key]
		cScriptMgr.DirtyFlag(self.index)
	
	def clear(self):
		self.data.clear()
		cScriptMgr.DirtyFlag(self.index)
	
	def keys(self):
		return self.data.keys()
	
	def items(self):
		return self.data.items()
	
	def iteritems(self):
		return self.data.iteritems()
	
	def iterkeys(self):
		return self.data.iterkeys()
	
	def itervalues(self):
		return self.data.itervalues()
	
	def values(self):
		return self.data.values()
	
	def has_key(self, key):
		return key in self.data
	
	def get(self, key, failobj=None):
		if key not in self:
			return failobj
		return self[key]
	
	def __contains__(self, key):
		return key in self.data
