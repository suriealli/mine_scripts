#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ClientPanel.PanelBase")
#===============================================================================
# 面板基类,不需要挂在NPC上面也可以显示出来的
#===============================================================================
from Common.Message import AutoMessage

CallBackSec = 300

ButtonTxt = "确定"

if "_HasLoad" not in dir():
	Msg_Dialog_Show = AutoMessage.AllotMessage("Msg_Dialog_Show", "普通对话")
	Msg_Dialog_Show_B = AutoMessage.AllotMessage("Msg_Dialog_Show_B", "普通对话(需要回调)")
	Msg_FilmDialog_Show = AutoMessage.AllotMessage("Msg_FilmDialog_Show", "电影式对话")
	Msg_FilmDialog_Show_B = AutoMessage.AllotMessage("Msg_FilmDialog_Show_B", "电影式对话(需要回调)")
	Msg_Select_Show = AutoMessage.AllotMessage("Msg_Select_Show", "选择对话")
	Msg_Request_Bool = AutoMessage.AllotMessage("Msg_Request_Bool", "询问并且返回是与否")
	Msg_Command = AutoMessage.AllotMessage("Msg_Command", "命令客户端执行一个指令")

def ClientCommand(role, command):
	'''命令很多话执行命令'''
	role.SendObj(Msg_Command, command)

#基础对话
class DialogBase(object):
	TxtType = 1 #发送字符串
	def __init__(self, role, fun = None, regparam = None):
		'''
		对话框基类
		@param role:对话的角色
		@param fun:回调函数
		@param regparam:注册参数
		'''
		
		self.role = role
		self.fun = fun
		self.regparam = regparam
		#对话列表
		self.dalogList = []
	
	def Append(self, npcType, text, buttonTxt = ButtonTxt):
		'''
		增加一次对话
		@param npcType: 0:自己半身像  非0:对应NPC半身像
		@param text:要说的话
		@param buttonTxt:按钮
		'''
		self.dalogList.append((npcType, text, buttonTxt))
	
	def Show(self):
		#展示对话
		if self.fun:
			self.role.SendObjAndBack(Msg_Dialog_Show_B, (self.TxtType, self.dalogList), CallBackSec, self._OnBack, self.regparam)
		else:
			self.role.SendObj(Msg_Dialog_Show, (self.TxtType, self.dalogList))
	
	def _OnBack(self, role, callArgv, regparam):
		'''
		回调
		@param role:回调的角色
		@param callArgv:回调参数，可能自回调，参数为None,但是不影响回调函数，直接调用
		@param regparam:注册参数，和self.regparam一样
		'''
		#客户端回调函数， 包装一层
		try:
			apply(self.fun, (role, regparam))
		except:
			print "GE_EXC, DialogBase (%s)" % str(self.fun)
			raise

#电影对白
class FilmDialogBase(object):
	TxtType = 1
	def __init__(self, role, fun = None, regparam = None):
		'''
		对话框基类
		@param role:对话的角色
		@param fun:回调函数
		@param regparam:注册参数
		'''
		self.role = role
		self.fun = fun
		self.regparam = regparam
		#对话列表
		self.dalogList = []
	
	def Append(self, npcType, text):
		'''
		增加一次对话
		@param npcType: 0:自己半身像  非0:对应NPC半身像
		@param text:要说的话
		'''
		self.dalogList.append((npcType, text))
	
	def Show(self):
		#展示对话
		if self.fun:
			self.role.SendObjAndBack(Msg_FilmDialog_Show_B, (self.TxtType, self.dalogList), CallBackSec, self._OnBack, self.regparam)
		else:
			self.role.SendObj(Msg_FilmDialog_Show, (self.TxtType, self.dalogList))
	
	def _OnBack(self, role, callArgv, regparam):
		'''
		回调
		@param role:回调的角色
		@param callArgv:回调参数，可能自回调，参数为None,但是不影响回调函数，直接调用
		@param regparam:注册参数，和self.regparam一样
		'''
		#客户端回调函数， 包装一层
		try:
			apply(self.fun, (role, regparam))
		except:
			print "GE_EXC, DialogBase (%s)" % str(self.fun)
			raise

#选择对话框
class SelectDalogBase(object):
	TxtType = 1
	def __init__(self, role, npcType, baseTxt):
		'''
		选择对话框
		@param role:
		@param npcType:0:自己半身像  非0:对应NPC半身像
		@param baseTxt:基本对话
		'''
		self.role = role
		self.dalogList = [(npcType, baseTxt)]
		self.funs = []
	
	def Append(self, text, fun, regparam = None):
		'''
		增加一个选项
		@param text:选项文字
		@param fun:回调函数
		@param regparam:注册参数
		'''
		self.dalogList.append(text)
		self.funs.append((fun, regparam))
	
	def Show(self):
		#展示
		self.role.SendObjAndBack(Msg_Select_Show, (self.TxtType, self.dalogList), CallBackSec, self._OnBack, None)


	def _OnBack(self, role, callargv, regparam):
		'''
		回调
		@param role:回调的角色
		@param callArgv:回调参数，可能自回调，参数为None
		@param regparam:注册参数，和self.regparam一样
		'''
		if callargv is None:
			#自动回调,不是玩家选择，默认不选择，区别于普通的对话框
			return
		
		if callargv > 0 and callargv <= len(self.funs):
			fun, regp = self.funs[callargv - 1]
			if fun:
				try:
					apply(fun, (role, regp))
				except:
					print "GE_EXC, SelectDalog (%s)" % str(fun)
					raise

#询问框 
class RequestBool(object):
	TxtType = 1
	def __init__(self, role, text, overTimesSec, backFun, regparam = None):
		'''
		弹出询问对话框，选择是与否，是：True 否 :False
		@param role:
		@param text:
		@param overTimesSec:超时时间 服务器多5秒
		@param backFun:
		@param regparam:
		'''
		
		role.SendObjAndBack(Msg_Request_Bool, (self.TxtType, text, overTimesSec), overTimesSec + 5, backFun, regparam)


