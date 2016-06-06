#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 整个脚本系统的文件路径管理模块
# 关键是处理了服务器运行过程中自动生成文件夹的机制
#===============================================================================
import os
import Environment

class DynamicFolder(object):
	def __init__(self, exitstFolder):
		'''
		动态文件夹
		@param exitstFolder:已经存在的一个文件夹路径
		'''
		if exitstFolder.endswith(os.sep):
			exitstFolder = exitstFolder[:-1]
		self.baseFolderPath = exitstFolder
		self.folderPath = self.baseFolderPath
		self.__Check()
	
	def __Check(self):
		if not os.path.exists(self.baseFolderPath):
			raise Exception("nonexistent path %s" % self.baseFolderPath)
		if not os.path.isdir(self.baseFolderPath):
			raise Exception("nonexistent folder path %s" % self.baseFolderPath)
	
	def AppendPath(self, path):
		'''
		追加一个文件夹路径
		@param path:文件夹名
		'''
		_newPath = self.folderPath + os.sep + str(path)
		if os.path.exists(_newPath):
			if os.path.isdir(_newPath):
				self.folderPath = _newPath
				return self
			else:
				raise Exception("repeat file path %s" % _newPath)
		else:
			# 多进程下的安全创建文件夹
			try:
				# 尝试创建
				os.makedirs(_newPath)
			except:
				# 如果创建失败，有肯能是多进程同时启动的情况下被其他进程创建了
				# 断言此时必定有这个目录存在
				assert(os.path.exists(_newPath) and os.path.isdir(_newPath))
			self.folderPath = _newPath
			return self
	
	def FolderPath(self):
		'''
		获取文件夹路径（路径最后带分割符）
		'''
		return self.folderPath + os.sep
	
	def FilePath(self, fileName):
		'''
		获取文件路径
		@param fileName:文件名
		'''
		return self.folderPath + os.sep + fileName

#===============================================================================
# 文件夹定义
#===============================================================================
# 当前文件夹路径PyCode
CurFloderPath = os.path.dirname(os.path.realpath(__file__)) + os.sep
PyFloderPath = CurFloderPath
# 根目录路径GameProject
RootFloderPath = CurFloderPath[:-14]
ServerFloderPath = CurFloderPath[:-7]
# Python的寻找目录
PythonHome = ServerFloderPath + "PyLib"
# C++目录路径CCode
CFloderPath = ServerFloderPath + "CCode" + os.sep
# 配置表目录【兼容老版的目录格式】
if Environment.IsWindows or Environment.IP in ["192.168.8.110"]:
	ConfigPath =  RootFloderPath + "Config" + os.sep
else:
	ConfigPath = ServerFloderPath + "Config" + os.sep
# 脚本目录"Config" + os.sep
ScriptPath = ServerFloderPath + "Script" + os.sep
# 生成文件目录
FilePath = ServerFloderPath + "File" + os.sep
# Bin目录
BinPath = ServerFloderPath + "Bin" + os.sep
# Python辅助目录
PyHelpPath = ServerFloderPath + "PyHelp" + os.sep
