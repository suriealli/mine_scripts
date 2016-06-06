#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.File.Base")
#===============================================================================
# 文件对象基础
#===============================================================================
import cPickle
import datetime
import cProcess
import cDateTime
import Environment
import DynamicPath
from ComplexServer import Init

if Environment.HasLogic:
	FileFolder = DynamicPath.DynamicFolder(DynamicPath.FilePath)
	FileFolder.AppendPath("Logic_%s" % cProcess.ProcessID)

if "_HasLoad" not in dir():
	KeyDict = {}

def AsDatetime(arg):
	'''
	转化为datetime.datetime对象
	@param arg:参数
	'''
	if type(arg) == datetime.datetime:
		return arg
	else:
		return datetime.datetime(*arg)

def IsTimeOver(dt):
	return AsDatetime(dt) < cDateTime.Now()

class FileObjBase(object):
	# 默认值的创建函数
	defualt_data_create = lambda : None
	def __init__(self, key, deadTime = (2038, 1, 1), afterLoadFun = None):
		if not Environment.HasLogic:
			return
		if IsTimeOver(deadTime):
			return
		# 确保Key唯一
		if key in KeyDict:
			print "GE_EXC, repeat persistence data key(%s)" % key
			return
		KeyDict[key] = self
		# 初始化数据
		self.key = key
		self.filePath = FileFolder.FilePath(key)
		try:
			f = open(self.filePath, "rb")
			self.data = cPickle.load(f)
			f.close()
		except:
			self.data = self.defualt_data_create()
		# 注册保存的函数
		Init.FinalCallBack.RegCallbackFunction(self.SaveData)
	
	def SaveData(self):
		f = open(self.filePath, "wb")
		cPickle.dump(self.data, f, 1)
		f.close()

