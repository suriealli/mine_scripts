#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 自动构建数据表
#===============================================================================
import os
import StringIO
from django.http import HttpResponse
from ComplexServer.Plug.DB import GlobalTable, HouTaiTable
from Integration import AutoHTML
from Integration.WebPage.User import Permission

class OugBuf(object):
	def __init__(self):
		self.buf = StringIO.StringIO()
	
	def __enter__(self):
		self.out = os.sys.stdout
		self.err = os.sys.stderr
		os.sys.stdout = self.buf
		os.sys.stderr = self.buf
		return self
	
	def __exit__(self, _type, _value, _traceback):
		os.sys.stdout = self.out
		os.sys.stderr = self.err
		return False
	
	def GetOutAndErr(self):
		return self.buf.getvalue()
	
	def ServerPrint(self, s):
		self.out.write(s)

def AutoCreate(request):
	'''【配置】--创建全局和后台表'''
	with OugBuf() as ob:
		GlobalTable.BuildTable()
		HouTaiTable.BuildTable()
		print "End"
		return HttpResponse(AutoHTML.PyStringToHtml(ob.GetOutAndErr()))

Permission.reg_develop(AutoCreate)

