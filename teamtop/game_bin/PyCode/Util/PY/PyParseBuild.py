#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 模块解析和构建
#===============================================================================
import os
import types
import string
import DynamicPath

def PyCodeRound(l):
	'''
	将一行python代码截尾（注意，会自动截掉注释）
	@param l:一行代码
	'''
	# 去注释
	pos = l.find('#')
	if pos != -1:
		l = l[:pos]
	# 去掉末尾的tab和空格
	while 1:
		if not l: break
		if l[-1] in ('	', ' '):
			l = l[:-1]
		else:
			break
	return l

def PyCodeTrip(l):
	'''
	将python代码字符串的头尾的空格和tab去掉
	@param l:代码字符串
	'''
	# 去掉头部tab和空格
	while 1:
		if not l: break
		if l[0] in ('	', ' '):
			l = l[1:]
		else:
			break
	# 去掉末尾的tab和空格
	while 1:
		if not l: break
		if l[-1] in ('	', ' '):
			l = l[:-1]
		else:
			break
	return l

class PyFile(object):
	def __init__(self, moduleName, filePath = None):
		self.moduleName = moduleName
		if filePath:
			if filePath.endswith(".py"):
				self.filePath = filePath
			elif filePath.endswith(".pyc"):
				self.filePath = filePath[:-1]
			else:
				self.filePath = DynamicPath.PyFloderPath + moduleName.replace('.', os.sep) + ".py"
		else:
			self.filePath = DynamicPath.PyFloderPath + moduleName.replace('.', os.sep) + ".py"
		self.__Read()
	
	def __Read(self):
		self.fileList = []
		try:
			with open(self.filePath) as f:
				fileList = f.read().split('\n')
			# 去掉回车
			for l in fileList:
				if l.endswith('\r'):
					l = l[:-1]
				self.fileList.append(l)
		except:
			print "can't open file(%s)" % self.filePath
	
	def ReplaceXRLAM(self):
		if len(self.fileList) < 3:
			return
		if self.fileList[2].find("XRLAM") > 0:
			self.fileList[2] = '# XRLAM("%s")' % self.moduleName
		else:
			print "GE_EXC, module(%s) has not xrlam." % self.moduleName
	
	def ReplaceCode(self, codeList, beginFlag = "AutoCodeBegin", endFlag = "AutoCodeEnd"):
		isreplace, hasbegin, hasend = False, False, False
		newList = []
		for l in self.fileList:
			if l.find(beginFlag) != -1:
				# 必须没遇到过开始标识
				assert(not hasbegin)
				isreplace = True
				hasbegin = True
				newList.append(l)
				newList.extend(codeList)
				continue
			if l.find(endFlag) != -1:
				# 必须先遇到开始标识
				assert(hasbegin)
				isreplace = False
				hasend = True
				newList.append(l)
				continue
			if not isreplace:
				newList.append(l)
		if hasbegin and hasend:
			self.fileList = newList
		else:
			print "module(%s) not find begin flag(%s) and end flag(%s)" % (self.moduleName, hasbegin, hasend)
	
	def ReplaceCEnumerate(self, enumName, enumInfo, beginFlag = "AutoCodeBegin", endFlag = "AutoCodeEnd"):
		codeList = ["# %s" % enumName]
		for info in enumInfo:
			codeList.append("%s = %s\t\t#%s" % info)
		self.ReplaceCode(codeList, beginFlag, endFlag)
	
	def Write(self):
		# 没有内容，不写
		if not self.fileList:
			return
		with open(self.filePath, 'w') as f:
			f.write('\n'.join(self.fileList))
		print ">>> build module(%s)" % self.moduleName
	
	def GetCodes(self):
		'''
		获得所有的代码信息
		'''
		result = []
		for idx, l in enumerate(self.fileList):
			if l.startswith('#'):
				continue
			result.append((idx, l))
		return result
	
	def GetEqualInfo(self):
		'''
		获取模块中的等式信息
		@return: [(key, value, zs), ...]
		'''
		result = []
		for l in self.fileList:
			pos = l.find('#')
			if pos == -1:
				co, zs = l, ""
			else:
				co, zs = l[:pos], l[pos + 1:]
			pos = co.find('=')
			if pos == -1:
				continue
			k, v = PyCodeTrip(co[:pos]), PyCodeTrip(co[pos + 1:])
			result.append((k, v, zs))
		return result
	
	def GetModuleExecuteCodes_Reload(self):
		'''
		获取在relaod的时候会执行的代码信息
		'''
		result = []
		tab = False
		for idx, l in enumerate(self.fileList):
			# 注释
			if l.startswith("#"):
				continue
			# 截尾
			l = PyCodeRound(l)
			# 空字符串
			if not l:
				continue
			# 代码以缩进开头
			if l.startswith('	'):
				# 如果此时会执行缩进代码，记录之
				if tab:
					result.append((idx, l))
				# 此行代码已经处理完毕了
				continue
			else:
				# 标记缩进逻辑结束了
				tab = False
			
			# 导入
			if l.startswith("from "):
				continue
			if l.startswith("import "):
				continue
			# 函数定义
			if l.startswith("def"):
				continue
			# 类定义
			if l.startswith("class"):
				continue
			# 必定是测试逻辑和reloa的时候不会执行的代码，忽视之
			if l.startswith("if __name__ == '__main__'") \
			or l.startswith('if __name__ == "__main__"') \
			or l.find("'_HasLoad' not in dir()") > 0 \
			or l.find('"_HasLoad" not in dir()') > 0:
				continue
			# 以导致缩进开头的关键字开始的代码行，标记会执行缩进代码
			if l.startswith("if ") \
			or l.startswith("for ") \
			or l.startswith("elif") \
			or l.startswith("else") :
				tab = True
			result.append((idx, l))
		return result


class PyObj(object):
	CodeChar = string.letters + string.digits + "_" + '"'
	def __init__(self, module):
		self.module = module
		self.pyFile = PyFile(module.__name__, module.__file__)
		self.__LogicInfo()
	
	def __LogicInfo(self):
		self.funs = []
		self.clss = []
		for name in dir(self.module):
			obj = getattr(self.module, name)
			if type(obj) == types.FunctionType and obj.__module__ == self.module.__name__:
				self.funs.append(obj)
			elif type(obj) in (types.TypeType, types.ClassType) and obj.__module__ == self.module.__name__:
				self.clss.append(obj)
	
	def __HasUserObj(self, l, objName):
		pos = l.find(objName)
		if pos < 0: return False
		p = pos -1
		if p >= 0 and l[p] in self.CodeChar:
			return False
		n = pos + len(objName)
		if n < len(l) and l[n] in self.CodeChar:
			return False
		return True
	
	def FixXRLAM(self):
		if len(self.pyFile.fileList) < 3:
			print "GE_EXC, model(%s) length < 3." % (self.module.__name__), len(self.pyFile.fileList)
			return
		line = self.pyFile.fileList[2]
		if line.find("XRLAM") != 2:
			print "GE_EXC, model(%s) XRLAM error." % (self.module.__name__)
			self.pyFile.fileList[2] = '# XRLAM("%s")' % self.module.__name__
			self.pyFile.Write()
			return
		xrlam = line[9:-2]
		if xrlam != self.module.__name__:
			print "GE_EXC, model(%s) XRLAM unequal." % (self.module.__name__)
			self.pyFile.fileList[2] = '# XRLAM("%s")' % self.module.__name__
			self.pyFile.Write()
			return
	
	def CheckSelfInherit(self):
		'''
		检测一个模块中是否有类继承该模块的其他类
		'''
		errorList = []
		for c1 in self.clss:
			for c2 in self.clss:
				if c1 == c2: continue
				if not issubclass(c1, c2): continue
				errorList.append((c1, c2))
		if not errorList: return
		print "-------- module(%s)" % self.module.__name__
		for c1, c2 in errorList:
			print "%s is subclass of %s" % (c1.__name__, c2.__name__)
	
	def CheckSelfUser(self):
		'''
		检测一个模块中，是否有reload执行的代码中使用了该模块的函数和类
		'''
		errorList = []
		for idx, l in self.pyFile.GetModuleExecuteCodes_Reload():
			for fun in self.funs:
				# 枚举模块不检测
				if fun.__module__.startswith("Game.Role.Data.Enum"):
					continue
				if not self.__HasUserObj(l, fun.__name__):
					continue
				errorList.append((idx, l, fun.__name__))
			for cls in self.clss:
				if not self.__HasUserObj(l, cls.__name__):
					continue
				errorList.append((idx, l, cls.__name__))
		if not errorList: return
		print "======== module(%s)" % self.module.__name__
		for idx, l, name in errorList:
			print "%s line(%s) user %s" % (idx, l, name)
	
	def GetEnumerateInfo(self, uniq = True):
		'''
		获取这个模块中枚举的信息
		@return: [(变量名, 值, 注释)]
		'''
		result = []
		us = set()
		for k, _, zs in self.pyFile.GetEqualInfo():
			if not hasattr(self.module, k):
				continue
			if uniq and k in us:
				continue
			result.append((k, getattr(self.module, k), zs))
			us.add(k)
		return result

