#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("ComplexServer.BigMessage")
#===============================================================================
# 脚本层的超大消息传递
#===============================================================================
import cProcess
import cDateTime
import cComplexServer
from Util import Slice
from Common import Serialize, CValue
from Common.Message import PyMessage

class BigMessage(object):
	def __init__(self, msg_type):
		self.msg_type = msg_type
		self.msg_idx = 0
		self.msg_objs = []
	
	def OnRecv(self, idx, item):
		self.msg_idx += 1
		if self.msg_idx != idx:
			print "GE_EXC, receive big message(%s) idx(%s) != idx(%s)" % (self.msg_type, self.msg_idx, idx)
			return
		self.msg_objs.append(item)
	
	def OnOK(self, length):
		s = "".join(self.msg_objs)
		if len(s) != length:
			print "GE_EXC, receive big message(%s) length error" % self.msg_type
			return
		msg = Serialize.String2PyObj(s)
		cComplexServer.DoDistribute(self.msg_type, msg)

class BigCallBack(object):
	def __init__(self, fun_id):
		self.fun_id = fun_id
		self.fun_idx = 0
		self.fun_objs = []
	
	def OnRecv(self, idx, item):
		self.fun_idx += 1
		if self.fun_idx != idx:
			print "GE_EXC, receive big callback(%s) idx(%s) != idx(%s)" % (self.fun_id, self.fun_idx, idx)
			return
		self.fun_objs.append(item)
	
	def OnOK(self, length):
		s = "".join(self.fun_objs)
		if len(s) != length:
			print "GE_EXC, receive big callback(%s) length error" % self.fun_id
			return
		arg = Serialize.String2PyObj(s)
		cComplexServer.DoBackFunction(self.fun_id, arg)
		#print "BLUE OnOK", cDateTime.Now(), self.fun_id

def Send(sessionid, msg_type, msg_obj):
	global QUEUE_ID
	QUEUE_ID += 1
	queue_idx = 0
	s = Serialize.PyObj2String(msg_obj)
	PSB = PyMessage.Server_BigMessage
	CS = cComplexServer.SendPyMsg
	CS(sessionid, PSB, (QUEUE_ID, queue_idx, msg_type))
	for item in Slice.IterSlice(s, 32767):#每次传输32767个字节，不要超过65535
		queue_idx += 1
		CS(sessionid, PSB, (QUEUE_ID, queue_idx, item))
	CS(sessionid, PSB, (QUEUE_ID, -1, len(s)))

def CallBack(sessionid, fun_id, msg_obj):
	global QUEUE_ID
	QUEUE_ID += 1
	queue_idx = 0
	s = Serialize.PyObj2String(msg_obj)
	PSB = PyMessage.Server_BigCallBack
	CS = cComplexServer.SendPyMsg
	CS(sessionid, PSB, (QUEUE_ID, queue_idx, fun_id))
	for item in Slice.IterSlice(s, 32767):
		queue_idx += 1
		CS(sessionid, PSB, (QUEUE_ID, queue_idx, item))
	CS(sessionid, PSB, (QUEUE_ID, -1, len(s)))
	#print "BLUE CallBack", cDateTime.Now(), fun_id

def OnSend(sessionid, msg):
	queue_id, queue_idx, item = msg
	if queue_idx == 0:
		BIG_MESSAGES[queue_id] = BigMessage(item)
	elif queue_idx == -1:
		BIG_MESSAGES[queue_id].OnOK(item)
		del BIG_MESSAGES[queue_id]
	else:
		BIG_MESSAGES[queue_id].OnRecv(queue_idx, item)

def OnCallBack(sessionid, msg):
	queue_id, queue_idx, item = msg
	if queue_idx == 0:
		BIG_CALLBACKS[queue_id] = BigCallBack(item)
	elif queue_idx == -1:
		BIG_CALLBACKS[queue_id].OnOK(item)
		del BIG_CALLBACKS[queue_id]
	else:
		BIG_CALLBACKS[queue_id].OnRecv(queue_idx, item)

if "_HasLoad" not in dir():
	QUEUE_ID = cProcess.ProcessID * CValue.P2_32
	BIG_MESSAGES = {}
	BIG_CALLBACKS = {}
	cComplexServer.RegDistribute(PyMessage.Server_BigMessage, OnSend)
	cComplexServer.RegDistribute(PyMessage.Server_BigCallBack, OnCallBack)

