#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 模块预载入
#===============================================================================
import os
import sys
import types
import traceback
from Util import Trace
from Util.PY import PyParseBuild

def GetModules(rootFloder, suffixs = set(["py", "pyc", "pyo"])):
	'''
	获取rootFloder目录下所有模块文件的信息（注意，去除了__init__模块）
	@param rootFloder:根目录
	@param suffixs:文件后缀
	@return: 模块名的集合
	'''
	# 加速
	suffixs = set(suffixs)
	# 去掉最后的分隔符
	if rootFloder.endswith(os.sep):
		rootFloder = rootFloder[:-1]
	# 非模块名路径长度
	unmoduleNamePathLen = len(rootFloder) + 1
	# 结果集
	result = set()
	# 遍历所有的文件信息
	for dirpath, _, filenames in os.walk(rootFloder):
		# 遍历所有的文件
		for fi in filenames:
			# __init__文件，导入包
			if fi == "__init__.py":
				fpns = dirpath
			# 构造文件路径
			else:
				fp = dirpath + os.sep + fi
				# 解析文件后缀
				pos = fp.rfind('.')
				if pos == -1:
					continue
				fpns, su = fp[:pos], fp[pos + 1:]
				# 不是模块文件，忽视之
				if su not in suffixs:
					continue
			# 将无后缀的文件路径变化为模块名
			moduleName = fpns[unmoduleNamePathLen:].replace(os.sep, '.')
			# 加入结果集
			if moduleName: result.add(moduleName)
	return result

def CheckFun(old_fun):
	def new_fun(*argv, **kwgv):
		try:
			import cProcess
			if cProcess.PyErrPrint(): 
				Trace.StackWarn("has except before")
			result = old_fun(*argv, **kwgv)
			if cProcess.PyErrPrint(): 
				Trace.StackWarn("has except after")
			return result
		except:
			raise
	return new_fun

def FindUncheckExcept(module):
	for name in dir(module):
		value = getattr(module, name)
		if not isinstance(value, types.FunctionType):
			continue
		setattr(module, name, CheckFun(value))

def LoadModules(moduleNames):
	'''
	预导入模块，并设置标识位
	@param moduleNames:模块名集合
	'''
	moduleList = []
	for moduleName in moduleNames:
		try:
			# 导入模块
			__import__(moduleName)
			# 获取模块对象
			module = sys.modules[moduleName]
			moduleList.append(module)
			# 标记该模块被预导入
			setattr(module, "_HasLoad", None)
			# 记录文件修改时间
			MODULE_FILE_TIME[moduleName] = GetModuleModifyTime(module)
			# 寻找未捕获的异常
			#FindUncheckExcept(module)
		except:
			traceback.print_exc()
	return moduleList

def LoadAllModule():
	'''
	载入所有的模块
	'''
	import DynamicPath
	return LoadModules(GetModules(DynamicPath.PyFloderPath, set(["py"])))

def LoadPartModule(startswith = ""):
	'''
	载入一部分的模块
	@param startswith:模块名开始
	'''
	import DynamicPath
	moduleNames = [modulename for modulename in GetModules(DynamicPath.PyFloderPath, set(["py"])) if modulename.startswith(startswith)]
	return LoadModules(moduleNames)

def LoadPartModuleEx(startswith = ""):
	'''
	载入一部分的模块，并且检查模块的reload特性
	@param startswith:模块名开始
	'''
	import DynamicPath
	moduleNames = [modulename for modulename in GetModules(DynamicPath.PyFloderPath, set(["py"])) if modulename.startswith(startswith)]
	moduleList = LoadModules(moduleNames)
	for module in moduleList:
		po = PyParseBuild.PyObj(module)
		po.CheckSelfInherit()
		po.CheckSelfUser()
	return moduleList

def LoadNotPartModule(startswith = ""):
	'''
	载入一部分的模块
	@param startswith:模块名开始
	'''
	import DynamicPath
	moduleNames = [modulename for modulename in GetModules(DynamicPath.PyFloderPath, set(["py"])) if not modulename.startswith(startswith)]
	return LoadModules(moduleNames)


def GetModuleModifyTime(module):
	'''获取模块的最后修改时间'''
	file_path = module.__file__
	if file_path.endswith(".pyc"):
		file_path = file_path[:-1]
	return os.stat(file_path).st_mtime

if "_HasLoad" not in dir():
	MODULE_FILE_TIME = {}

if __name__ == "__main__":
	LoadPartModuleEx("Common")
	LoadPartModuleEx("Global")
	LoadPartModuleEx("ComplexServer")
	LoadPartModuleEx("DB")
	LoadPartModuleEx("Game")
	LoadPartModuleEx("Control")

