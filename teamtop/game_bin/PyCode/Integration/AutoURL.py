#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 页面路径自动构建模块
#===============================================================================
import types
import inspect
import traceback
import StringIO
import Environment
from Util.PY import Load
from django.http import HttpResponse
from Integration.WebPage.User import Permission

def GetURI(name):
	'''
	根据模块名生成URI
	@param name:
	'''
	return name[len(auto_page) + 1:].replace('.', '/')

class RequestHandle(object):
	def __init__(self, url, fun):
		self.url = url
		self.fun = fun
	
	def __call__(self, request):
		if  Permission.check(request, self.url):
			try:
				response =  self.fun(request)
			except:
				if Environment.IsWindows:
					traceback.print_exc()
					raise
				f = StringIO.StringIO()
				traceback.print_exc(None, f)
				return HttpResponse(f.getvalue().replace('\n', '<br>'))
			Permission.monitor(request, response, self.url) #log access
			return response
		else:
			return HttpResponse("你没有权限(%s)!" % self.url)

def AutoBuild():
	'''
	自动构建WebPage目录下的模块的函数的URI和索引
	'''
	# 遍历WebPage下的所有模块
	for module in Load.LoadPartModule(auto_page):
		# 遍历模块中的所有元素
		for name in dir(module):
			# 如果不是函数，忽视之
			value = getattr(module, name)
			if type(value) != types.FunctionType:
				continue
			# 如果以_开头的函数忽视之
			if name.startswith("_"):
				continue
			# 获取函数信息
			args, varargs, keywords, _ = inspect.getargspec(value)
			# 如果不是Http处理函数，忽视之
			if not(len(args) == 1 and args[0] == "request" and varargs is None and keywords is None):
				continue
			# 构建URI， 并保持URI和对应的函数
			uri = getattr(value, "uri", None)
			if uri is None:
				uri = GetURI(module.__name__)
			if uri in auto_patterns:
				print "GE_EXC, auto build uri repeat error", module.__name__, value.__name__, uri
			uri = "%s/%s" % (uri, value.__name__)
			#auto_patterns["^%s/" % uri] = "%s.%s" % (module.__name__, value.__name__)
			auto_patterns["^%s/" % uri] = RequestHandle("/%s/" % uri, value)
			# 构建索引信息，并保存对应的URI
			index = inspect.getdoc(value)
			if not index:
				continue
			if index in auto_indexs:
				print "GE_EXC, auto build index repeat error", module.__name__, value.__name__, index
			auto_indexs["/%s/" % uri] = index

if "_HasLoad" not in dir():
	auto_patterns = {}
	auto_indexs = {}
	auto_page = "Integration.WebPage"
	# 按顺序载入脚本
	Load.LoadPartModule("Global")
	Load.LoadPartModule("ComplexServer")
	if Environment.IP != "10.207.148.145":
		Load.LoadPartModule("DB")
		Load.LoadPartModule("Control")
		Load.LoadPartModule("Game")
		Load.LoadPartModule("Integration")
	AutoBuild()
	_HasLoad = None

