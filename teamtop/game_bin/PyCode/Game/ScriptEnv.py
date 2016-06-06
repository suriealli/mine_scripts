#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ScriptEnv")
#===============================================================================
# Game脚本模块环境管理
#===============================================================================
#import sys
#import types
#import DynamicPath
#import Environment
#from Util.File import TabFile
#from ComplexServer import Init
#
#
##===============================================================================
##配置表里面没有记录的模块，就会通用于所有的环境
##配置表里面有配置的模块名称，那么这个模块下任何消息的注册，Event的注册，Cron注册，cComplexServer的时间注册等
##都会加一个环境判断，只有在某些环境下才会执行以上逻辑，或者在某些配置的环境下，不执行这些逻辑
##这样做可以做到在特定的环境下配置一些系统的开启和关闭
##===============================================================================
#
#if "_HasLoad" not in dir():
#	ScriptEnvConfig_Dict = {}
#
#def FunIsValid(fun):
#	#这个模块在当前环境下是否是有效的
#	if not Environment.HasLogic:
#		#只有逻辑进程才会检测
#		return True
#	
#	moduleName = fun.__module__
#	#模块检测
#	sec = ScriptEnvConfig_Dict.get(moduleName)
#	if not sec:
#		return True
#	
#	if sec.env_valid:
#		#有配置生效限制,判断一下当前是否处于生效环境
#		for attName in sec.env_valid:
#			if getattr(Environment, attName) is True:
#				return True
#		else:
#			#不处于生效环境，这个模块下所有的函数都是无效的
#			return False
#	if sec.env_Unvalid:
#		#配置了无效的环境
#		for attName in sec.env_Unvalid:
#			if getattr(Environment, attName) is True:
#				#当前环境下，这个函数所属的模块无效，这里优先级最高
#				return False
#	return True
#
#class ScriptEnvConfig(TabFile.TabLine):
#	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
#	FILE_FOLDER_PATH.AppendPath("ScriptEnv")
#	FilePath = FILE_FOLDER_PATH.FilePath("ScriptEnv.txt")
#	def __init__(self):
#		self.moduleName = str
#		self.env_valid = self.GetEvalByString
#		self.env_Unvalid = self.GetEvalByString
#
#def LoadScriptEnvConfig():
#	global ScriptEnvConfig_Dict
#	for sec in ScriptEnvConfig.ToClassType(False):
#		if not sec.moduleName:
#			print "GE_EXC not modulename"
#			continue
#		if sec.moduleName in ScriptEnvConfig_Dict:
#			print "GE_EXC, repeat moduleName in LoadScriptEnvConfig (%s)" % sec.moduleName
#		
#		ScriptEnvConfig_Dict[sec.moduleName] = sec
#
#
#
#def UniversalFunction(*argv, **kwgv):
#	'''
#	万能函数
#	'''
#	from Util import Trace
#	#原则上来说不应该调用到，如果有调用则证明模块依赖关系没有处理好，或者有多语言环境的配置问题
#	Trace.StackWarn("ScirptEnv error use UniversalFunction.")
#
#def DisableFunction(funObj):
#	'''
#	禁用一个函数，就是把这个函数替换成一个空函数
#	@param funObj:函数对象
#	'''
#	# 替换函数
#	funObj.func_code = UniversalFunction.func_code
#	funObj.func_defaults = UniversalFunction.func_defaults
#	funObj.func_doc = UniversalFunction.func_doc
#
#
#def DisableModules():
#	if not Environment.HasLogic:
#		return
#	#替换模块里面的所有的函数
#	global ScriptEnvConfig_Dict
#	for module in sys.modules.values():
#		# 空模块
#		if not module:
#			continue
#		sec = ScriptEnvConfig_Dict.get(module.__name__)
#		if not sec:
#			#没有配置,不处理
#			continue
#		if sec.env_valid:
#			#有配置生效限制,判断一下当前是否处于生效环境
#			for attName in sec.env_valid:
#				if getattr(Environment, attName) is True:
#					break
#			else:
#				#不处于生效环境，这个模块下所有的函数都是无效的
#				DisableTheModule(module)
#		elif sec.env_Unvalid:
#			#配置了无效的环境
#			for attName in sec.env_Unvalid:
#				if getattr(Environment, attName) is True:
#					#当前环境下，这个函数所属的模块无效，这里优先级最高
#					DisableTheModule(module)
#					break
#		
#
#def DisableTheModule(module):
#	for name in dir(module):
#		module_obj = getattr(module, name)
#		
#		ObjType = type(module_obj)
#		if ObjType == types.FunctionType:
#			#函数
#			DisableFunction(module_obj)
#		elif ObjType == types.UnboundMethodType:
#			#类方法，暂时不处理
#			pass
#		elif ObjType in (types.TypeType, types.ClassType):
#			#类,暂时不处理
#			pass


#if "_HasLoad" not in dir():
#	#这个读表会先于环境生成，所以不用判断环境
#	pass
#	LoadScriptEnvConfig()
#	Init.InitCallBack.RegCallbackFunction(DisableModules, index = 0)
	
	