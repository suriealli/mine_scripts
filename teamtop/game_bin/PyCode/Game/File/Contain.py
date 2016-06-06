#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.File.Contain")
#===============================================================================
# 文件容器
#===============================================================================
from Game.File import Base
	
class FileList(Base.FileObjBase):
	defualt_data_create = list
	
	def __repr__(self):
		return repr(self.data)
	
	__hash__ = None
	
	def __contains__(self, item):
		return item in self.data
	
	def __len__(self):
		return len(self.data)
	
	def __getitem__(self, i):
		return self.data[i]
	
	def __setitem__(self, i, item):
		self.data[i] = item
	
	def __delitem__(self, i):
		del self.data[i]
	
	def __getslice__(self, i, j):
		return self.data[i:j]

	
	def __setslice__(self, i, j, other):
		i = max(i, 0); j = max(j, 0)
		if isinstance(other, FileList):
			self.data[i:j] = other.data
		elif isinstance(other, type(self.data)):
			self.data[i:j] = other
		else:
			self.data[i:j] = list(other)
	
	def __delslice__(self, i, j):
		i = max(i, 0); j = max(j, 0)
		del self.data[i:j]
	
	def __add__(self, other):
		if isinstance(other, FileList):
			return self.data + other.data
		elif isinstance(other, type(self.data)):
			return self.data + other
		else:
			return self.data + list(other)
	
	def __radd__(self, other):
		if isinstance(other, FileList):
			return other.data + self.data
		elif isinstance(other, type(self.data)):
			return other + self.data
		else:
			return list(other) + self.data
	
	def __iadd__(self, other):
		if isinstance(other, FileList):
			self.data += other.data
		elif isinstance(other, type(self.data)):
			self.data += other
		else:
			self.data += list(other)
		return self
	
	def __mul__(self, n):
		return self.data*n
	
	__rmul__ = __mul__
	def __imul__(self, n):
		self.data *= n
		return self
	
	def append(self, item):
		self.data.append(item)
	
	def insert(self, i, item):
		self.data.insert(i, item)
	
	def pop(self, i=-1):
		return self.data.pop(i)
	
	def remove(self, item):
		self.data.remove(item)
	
	def count(self, item):
		return self.data.count(item)
	
	def index(self, item, *args):
		return self.data.index(item, *args)
	
	def reverse(self):
		self.data.reverse()
	
	def sort(self, *args, **kwds):
		self.data.sort(*args, **kwds)
	
	def extend(self, other):
		if isinstance(other, FileList):
			self.data.extend(other.data)
		else:
			self.data.extend(other)

class FileDict(Base.FileObjBase):
	defualt_data_create = dict
	
	def __repr__(self):
		return repr(self.data)
	
	__hash__ = None
	
	def __len__(self):
		return len(self.data)
	
	def __getitem__(self, key):
		if key in self.data:
			return self.data[key]
		if hasattr(self.__class__, "__missing__"):
			return self.__class__.__missing__(self, key)
		raise KeyError(key)
	
	def __setitem__(self, key, item):
		self.data[key] = item
	
	def __delitem__(self, key):
		del self.data[key]
	
	def clear(self):
		self.data.clear()
	
	def copy(self):
		if self.__class__ is FileDict:
			return FileDict(self.data.copy())
		import copy
		data = self.data
		try:
			self.data = {}
			c = copy.copy(self)
		finally:
			self.data = data
		c.update(self)
		return c
	
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
	
	def update(self, fd=None, **kwargs):
		if fd is None:
			pass
		elif isinstance(fd, FileDict):
			self.data.update(fd.data)
		elif isinstance(fd, type({})) or not hasattr(fd, 'items'):
			self.data.update(fd)
		else:
			for k, v in fd.items():
				self[k] = v
		if len(kwargs):
			self.data.update(kwargs)
	
	def get(self, key, failobj=None):
		if key not in self:
			return failobj
		return self[key]
	
	def setdefault(self, key, failobj=None):
		if key not in self:
			self[key] = failobj
		return self[key]
	
	def pop(self, key, *args):
		return self.data.pop(key, *args)
	
	def popitem(self):
		return self.data.popitem()
	
	def __contains__(self, key):
		return key in self.data

