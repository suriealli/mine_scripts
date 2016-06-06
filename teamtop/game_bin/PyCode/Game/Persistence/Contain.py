#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Persistence.Contain")
#===============================================================================
# 持久化容器(最多存储大概40K左右的数据，不能超过64K，就是说一个持久化列表最多存储不超过6000个角色ID)
#===============================================================================
from Game.Persistence import Base

class List(Base.ObjBase):
	defualt_data_create = list
	
	def __repr__(self): 
		assert(self.returnDB)
		return repr(self.data)
	
	__hash__ = None
	
	def __contains__(self, item): 
		assert(self.returnDB)
		return item in self.data
	
	def __len__(self): 
		assert(self.returnDB)
		return len(self.data)
	
	def __getitem__(self, i): 
		assert(self.returnDB)
		return self.data[i]
	
	def __setitem__(self, i, item): 
		assert(self.returnDB)
		self.data[i] = item
		self.changeFlag = True
		
	def __delitem__(self, i): 
		assert(self.returnDB)
		del self.data[i]
		self.changeFlag = True
		
	def __getslice__(self, i, j):
		assert(self.returnDB)
		return self.data[i:j]
	
	def __setslice__(self, i, j, other):
		assert(self.returnDB)
		i = max(i, 0); j = max(j, 0)
		if isinstance(other, List):
			self.data[i:j] = other.data
		elif isinstance(other, type(self.data)):
			self.data[i:j] = other
		else:
			self.data[i:j] = list(other)
		self.changeFlag = True
			
	def __delslice__(self, i, j):
		assert(self.returnDB)
		i = max(i, 0); j = max(j, 0)
		del self.data[i:j]
		self.changeFlag = True
	
	def __add__(self, other):
		assert(self.returnDB)
		if isinstance(other, List):
			return self.data + other.data
		elif isinstance(other, type(self.data)):
			return self.data + other
		else:
			return self.data + list(other)
		
	def __radd__(self, other):
		assert(self.returnDB)
		if isinstance(other, List):
			return other.data + self.data
		elif isinstance(other, type(self.data)):
			return other + self.data
		else:
			return list(other) + self.data
		
	def __iadd__(self, other):
		assert(self.returnDB)
		if isinstance(other, List):
			self.data += other.data
		elif isinstance(other, type(self.data)):
			self.data += other
		else:
			self.data += list(other)
		return self
	
	def __mul__(self, n):
		assert(self.returnDB)
		return self.data*n
	
	__rmul__ = __mul__
	
	def __imul__(self, n):
		assert(self.returnDB)
		self.data *= n
		return self
	
	def append(self, item): 
		assert(self.returnDB)
		self.data.append(item)
		self.changeFlag = True
		
	def insert(self, i, item): 
		assert(self.returnDB)
		self.data.insert(i, item)
		self.changeFlag = True
		
	def pop(self, i=-1): 
		assert(self.returnDB)
		self.changeFlag = True
		return self.data.pop(i)
	
	def remove(self, item): 
		assert(self.returnDB)
		self.data.remove(item)
		self.changeFlag = True
		
	def count(self, item): 
		assert(self.returnDB)
		return self.data.count(item)
	
	def index(self, item, *args): 
		assert(self.returnDB)
		return self.data.index(item, *args)
	
	def reverse(self): 
		assert(self.returnDB)
		self.data.reverse()
		self.changeFlag = True
		
	def sort(self, *args, **kwds): 
		assert(self.returnDB)
		self.data.sort(*args, **kwds)
		self.changeFlag = True
		
	def extend(self, other):
		assert(self.returnDB)
		if isinstance(other, List):
			self.data.extend(other.data)
		else:
			self.data.extend(other)
		self.changeFlag = True
		
	def clear(self):
		assert(self.returnDB)
		self.data = self.defualt_data_create()
		self.changeFlag = True


class Dict(Base.ObjBase):
	defualt_data_create = dict
	
	def __repr__(self):
		assert(self.returnDB)
		return repr(self.data)
	
	__hash__ = None
	
	def __len__(self):
		assert(self.returnDB)
		return len(self.data)
	
	def __getitem__(self, key):
		assert(self.returnDB)
		if key in self.data:
			return self.data[key]
		if hasattr(self.__class__, "__missing__"):
			return self.__class__.__missing__(self, key)
		raise KeyError(key)
	
	def __setitem__(self, key, item):
		assert(self.returnDB)
		self.data[key] = item
		self.changeFlag = True
		
	def __delitem__(self, key):
		assert(self.returnDB)
		del self.data[key]
		self.changeFlag = True
	
	def clear(self):
		assert(self.returnDB)
		self.data.clear()
		self.changeFlag = True
	
	def keys(self):
		assert(self.returnDB)
		return self.data.keys()
	
	def items(self):
		assert(self.returnDB)
		return self.data.items()
	
	def iteritems(self):
		assert(self.returnDB)
		return self.data.iteritems()
	
	def iterkeys(self):
		assert(self.returnDB)
		return self.data.iterkeys()
	
	def itervalues(self):
		assert(self.returnDB)
		return self.data.itervalues()
	
	def values(self):
		assert(self.returnDB)
		return self.data.values()
	
	def has_key(self, key):
		assert(self.returnDB)
		return key in self.data
	
	def get(self, key, failobj=None):
		assert(self.returnDB)
		if key not in self:
			return failobj
		return self[key]
	
	def setdefault(self, key, failobj=None):
		assert(self.returnDB)
		if key not in self:
			self[key] = failobj
			self.changeFlag = True
		return self[key]
	
	def __contains__(self, key):
		assert(self.returnDB)
		return key in self.data

