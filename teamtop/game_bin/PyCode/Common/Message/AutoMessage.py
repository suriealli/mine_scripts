#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Common.Message.AutoMessage")
#===============================================================================
# 智能消息定义模块
#===============================================================================
import os
import Environment
import DynamicPath
from Common import Coding
from Util.File import TabFile

MessageFile = DynamicPath.DynamicFolder(DynamicPath.ConfigPath).FilePath("AutoMessage.txt")

class Message(TabFile.TabLine):
	FilePath = MessageFile
	UseCache = False
	def __init__(self):
		self.name = str
		self.value = int
		self.zs = str

def LoadMsg():
	'''
	载入文件中的消息
	'''
	for m in Message.ToClassType(False):
		assert m.name not in AutoMsg
		assert m.value not in Values
		AutoMsg[m.name] = (m.value, m.zs)
		Values.add(m.value)

def SvnUp(isUp = True):
	'''
	更新文件消息
	'''
	global HasNewMsg, CanAllotMsg
	HasNewMsg = False
	# 只有WIN下逻辑进程才需要更新生成的消息
	if isUp and Environment.IsWindows and Environment.HasLogic and Environment.IP != "192.168.8.108":
		if not Environment.EnvIsFT() and not Environment.EnvIsNA() and not Environment.EnvIsRU():
			#只有主干开发环境才可以分配消息
			os.system('svn up %s' % MessageFile)
			CanAllotMsg = True
	# 载入文件中的消息
	AutoMsg.clear()
	Values.clear()
	LoadMsg()
	# 需要检测下消息是否正确
	CheckMessage()

def SvnCommit():
	'''
	提交文件消息
	'''
	global HasNewMsg, CanAllotMsg
	CanAllotMsg = False
	# 同时满足以下几个条件需要提交消息文件
	# 1 在WIN下
	# 2 有逻辑模块（有可能是django）
	# 3 有新消息
	if not Environment.IsWindows:
		return
	if not Environment.HasLogic:
		return
	if not HasNewMsg:
		return
	# 需要提交消息文件
	with open(MessageFile, "wb") as f:
		f.write("value\tname\tzs\r\n消息值\t消息名\t注释\r\n")
		msgs = AutoMsg.items()
		msgs.sort(key=lambda it:it[0])
		for name, (value, zs) in msgs:
			f.write("%s\t%s\t%s\r\n" % (value, name, zs))
	os.system('svn commit %s -m "Auto Message Commit"' % MessageFile)
	# 需要再次检测下消息是否正确
	CheckMessage()

def SvnCommitEx():
	'''
	提交文件消息
	'''
	global HasNewMsg, CanAllotMsg
	CanAllotMsg = False
	# 同时满足以下几个条件需要提交消息文件
	# 1 在WIN下
	# 2 有逻辑模块（有可能是django）
	# 3 有新消息
	if not Environment.IsWindows:
		return
	if not Environment.HasLogic:
		return
	if not HasNewMsg and Names == set(AutoMsg.keys()):
		return
	# 需要提交消息文件
	with open(MessageFile, "wb") as f:
		f.write("value\tname\tzs\r\n消息值\t消息名\t注释\r\n")
		msgs = AutoMsg.items()
		msgs.sort(key=lambda it:it[0])
		for name, (value, zs) in msgs:
#			if name not in Names:
#				print "-->delete message(%s) value(%s)" % (name, value)
#			else:
			f.write("%s\t%s\t%s\r\n" % (value, name, zs))
	os.system('svn commit %s -m "Auto Message Commit"' % MessageFile)
	# 需要再次检测下消息是否正确
	CheckMessage()

def AllotMessage(name, zs = "None"):
	'''
	分配一个消息
	@param name:消息名
	@param zs:消息注释
	'''
	# 消息名必须唯一
	if name in Names:
		print "AllotMessage Has name", name
	assert name not in Names
	Names.add(name)
	# 看是否已经有这个消息名了
	msginfo = AutoMsg.get(name)
	# 如果有，直接返回
	if msginfo:
		AutoMsg[name] = (msginfo[0], zs)
		return msginfo[0]
	# 否则分配一个可分配的消息，并记录之
	else:
		# 必须要在脚本载入的时候开始分配
		assert CanAllotMsg
		# 标记分配了新的消息
		global HasNewMsg
		for msg in xrange(*Coding.AutoMessageRange):
			if msg in Values:
				continue
			AutoMsg[name] = (msg, zs)
			Values.add(msg)
			HasNewMsg = True
			return msg
		assert False

def CheckMessage():
	'''
	检测消息
	'''
	from Common.Message import MessageCheck
	MessageCheck.Check()

if "_HasLoad" not in dir():
	HasNewMsg = None
	CanAllotMsg = None
	AutoMsg = {}
	Names = set()
	Values = set()
	if not Environment.HasLogic:
		LoadMsg()

