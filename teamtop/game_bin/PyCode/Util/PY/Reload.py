#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 模块重载
# 1.此模块中的reload是使用旧类和函数对象，函数的逻辑对象是用新的
# 2.这样做的好处是类和函数可以被第3方保存，reload模块后第3方的逻辑也同时改变
# 3.对于非类和函数对象，第3方的使用由模块开始引用之，能够使得reload模块后是使用新的对象
# 4.注意，使用本模块中的reload函数，要求被reload的模块在reload时执行的的模块级代码中
#    不能使用被reload模块中定义的逻辑对象
#===============================================================================
import types

def Reload(module, insteadData = False):
	'''
	重载某个模块
	@param module:模块对象
	@param insteadData:是否替换数据。False：只重载逻辑对象（类、函数）； True：重载逻辑和其他对象
	'''
	# 记录模块重载之前的所有顶层对象
	oldModule = {}
	for name in dir(module):
		oldModule[name] = getattr(module, name)
	
	# 重载模块
	newModule = reload(module)
	assert( id(module) == id(newModule))
	
	for name in dir(newModule):
		# 如果新的对象名不在旧模块中，不必处理
		if name not in oldModule:
			continue
		
		oldObj = oldModule[name]
		newObj = getattr(newModule, name)
		
		# 如果新对象的类型和旧对象的类型不同警告之
		if type(oldObj) != type(newObj):
			print "GE_EXC, after reload module(%s), obj(%s)'s old type(%s) != new type(%s)" % (module.__name__, name, str(type(oldObj)), str(type(newObj)))
			# 如果不替换数据，则使用旧对象
			if not insteadData:
				setattr(newModule, name, oldObj)
			continue
		
		# 尝试更新逻辑对象
		if Update(oldObj, newObj, insteadData):
			# 用更新后的旧逻辑替换reload后的新逻辑，保证函数指针不变
			setattr(newModule, name, oldObj)
		else:
			# 如果不替换数据, 非逻辑对象使用旧的对象
			if not insteadData:
				setattr(newModule, name, oldObj)

def UpdateFunction(oldFun, newFun):
	oldFun.func_code = newFun.func_code
	oldFun.func_defaults = newFun.func_defaults
	oldFun.func_doc = newFun.func_doc

def UnboundMethodType(oldMethod, newMethod):
	UpdateFunction(oldMethod.im_func, newMethod.im_func)

def UpdateClass(oldClass, newClass, insteadData):
	for name in newClass.__dict__.iterkeys():
		# 类实例的__dict__属性不可替换
		if name in ("__dict__", "__doc__"):
			continue
		
		newObj = getattr(newClass, name)
		oldObj = getattr(oldClass, name, None)
		
		# 如果新的对象和旧的对象是一个，则忽视之
		if newObj is oldObj:
			continue
		
		# 如果新的对象不在旧的对象中，添加之
		if oldObj is None:
			# 如果是类函数，则特殊构建之
			if type(newObj) is types.UnboundMethodType:
				im_func = newObj.im__func
				newObj = types.UnboundMethodType(im_func, None, oldClass)
			setattr(oldClass, name, newObj)
			continue
		
		# 如果新的对象和旧的对象的类型不同，警告之
		if type(oldObj) != type(newObj):
			print "GE_EXC, class(%s)'s obj(%s)'s old type(%s) != new type(%s)" % (newClass.__name__, name, str(type(oldObj)), str(type(newObj)))
			# 如果要替换数据，则用新的对象替换旧的对象
			if insteadData:
				setattr(oldClass, name, newObj)
			continue
		
		# 尝试更新逻辑对象
		if Update(oldObj, newObj, insteadData):
			pass
		else:
			# 如果要替换非逻辑对象，则用新的对象替换旧的对象
			if insteadData:
				setattr(oldClass, name, newObj)
				

def Update(oldObj, newObj, insteadData):
	oldObjType = type(oldObj)
	if oldObjType == types.FunctionType:
		UpdateFunction(oldObj, newObj)
	elif oldObjType in (types.TypeType, types.ClassType):
		UpdateClass(oldObj, newObj, insteadData)
	elif oldObjType == types.UnboundMethodType:
		UnboundMethodType(oldObj, newObj)
	else:
		return False
	return True

