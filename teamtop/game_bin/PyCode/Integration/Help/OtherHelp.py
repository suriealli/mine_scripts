#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 其他的辅助
#===============================================================================
import datetime
import traceback
import Environment
import DynamicPath
from Util.PY import PyParseBuild
from Integration import AutoHTML
from django.http import HttpResponse

def GetModuleDefine(module, valuetype = int):
	#如果是用于同步模块变量到后台，然后让客户端构建AS3代码用，则必须是 int 其他类型需尚未做支持构建AS3代码的脚本
	l = []
	mo = PyParseBuild.PyObj(module)
	for info in mo.GetEnumerateInfo(False):
		if isinstance(info[1], valuetype):
			l.append(info)
	return l

def GetMoudleDefineZS(module, valuetype = int):
	d = {}
	mo = PyParseBuild.PyObj(module)
	for info in mo.GetEnumerateInfo(False):
		if isinstance(info[1], valuetype):
			_, value, zs = info
			d[value]= zs
	return d
	

def Apply(fun, request, file_name):
	try:
		response = fun(request)
		if not isinstance(response, HttpResponse):
			response = HttpResponse(str(response))
		return response
	except:
		if Environment.IsWindows:
			raise
		else:
			with open(DynamicPath.DynamicFolder(DynamicPath.FilePath).FilePath(file_name), "a") as f:
				f.write(str(datetime.datetime.now()))
				f.write("\n")
				traceback.print_exc(None, f)
			return AutoHTML.Error

class Request(object):
	def __init__(self, d):
		self.GET = d
		self.POST = d

def PrintTraceback(file_name):
	with open(DynamicPath.DynamicFolder(DynamicPath.FilePath).FilePath(file_name), "a") as f:
		traceback.print_exc(None, f)
