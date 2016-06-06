#!/usr/bin/env python
# -*- coding:UTF-8 -*-
import os
import sys
reload(sys)
getattr(sys, "setdefaultencoding")("UTF-8")
path = os.path.dirname(os.path.realpath(__file__))
path = path[:path.find("PyCode") + 6]
if path not in sys.path: sys.path.append(path)
path = path.replace("PyCode", "PyHelp")
if path not in sys.path: sys.path.append(path)
#===============================================================================
# 命令行GM工具
#===============================================================================
import socket
import struct
import datetime
import types
import thread
import Queue
from ThirdLib import PrintHelp
from Common import CValue
from Common.Message import CMessage, PyMessage
from Common.Connect import Who

# C中的标识位定义
NONE_FLAG =				-100			#None
TRUE_FLAG =				-101			#True
FALSE_FLAG =			-102			#False
SMALL_TUPLE_FLAG =		-103			#Tuple
BIG_TUPLE_FLAG =		-104			#Tuple
SMALL_LIST_FLAG =		-105			#List
BIG_LIST_FLAG =			-106			#List
SMALL_SET_FLAG =		-107			#Set
BIG_SET_FLAG =			-108			#Set
SMALL_DICT_FLAG =		-109			#Dict
BIG_DICT_FLAG =			-110			#Dict
SMALL_STRING_FLAG =		-111			#String
BIG_STRING_FLAG =		-112			#String
DATETIME_FLAG =			-113			#DateTime
SIGNED_INT8_FLAG =		-114			#signed int8
SIGNED_INT16_FLAG =		-115			#signed int16
SIGNED_INT32_FLAG =		-116			#signed int32
SIGNED_INT64_FLAG =		-117			#signed int64

class GMConnect(object):
	def __init__(self, host, port, tgw = False):
		self.sock = socket.socket()
		self.sock.connect((host, port))
		if tgw:
			self.sock.sendall("tgw_l7_forward\r\nHost: %s:%s\r\n\r\n" % (host, port))
		self.thread = False
		self.queue = Queue.Queue()
		self.functions = {}
	
	def iamgm(self):
		msgbody = struct.pack("I", Who.enWho_GM_)
		self.sendmsg(CMessage.enProcessMsg_Who, msgbody)
	
	def iamclient(self):
		msgbody = struct.pack("I", Who.enWho_Client_)
		self.sendmsg(CMessage.enProcessMsg_Who, msgbody)
		msgtype, msg = self.recvmsg()
		assert msgtype == CMessage.enProcessMsg_OKClient
		print "gateway time is ", msg[1:]
	
	def sendmsg(self, msgtype, msgbody = ""):
		head = struct.pack("HH", 4 + len(msgbody), msgtype)
		self.sock.sendall(head + msgbody)
	
	def sendobj(self, msgtype, msgobj = None):
		msglis = []
		self.packobj(msgobj, msglis)
		self.sendmsg(msgtype, "".join(msglis))
	
	def packobj(self, msgobj, msglis):
		t = type(msgobj)
		if msgobj is None:
			msglis.append(struct.pack("b", NONE_FLAG))
		elif msgobj is True:
			msglis.append(struct.pack("b", TRUE_FLAG))
		elif msgobj is False:
			msglis.append(struct.pack("b", FALSE_FLAG))
		elif t == types.IntType or t == types.LongType:
			if CValue.MIN_INT8 <= msgobj <= CValue.MAX_INT8:
				if msgobj > NONE_FLAG:
					msglis.append(struct.pack("b", msgobj))
				else:
					msglis.append(struct.pack("b", SIGNED_INT8_FLAG))
					msglis.append(struct.pack("b", msgobj))
			elif CValue.MIN_INT16 <= msgobj <= CValue.MAX_INT16:
				msglis.append(struct.pack("b", SIGNED_INT16_FLAG))
				msglis.append(struct.pack("h", msgobj))
			elif CValue.MIN_INT32 <= msgobj <= CValue.MAX_INT32:
				msglis.append(struct.pack("b", SIGNED_INT32_FLAG))
				msglis.append(struct.pack("i", msgobj))
			else:
				msglis.append(struct.pack("b", SIGNED_INT64_FLAG))
				msglis.append(struct.pack("q", msgobj))
		elif t == types.TupleType or t == types.ListType or t == type(set()):
			size = len(msgobj)
			if size > CValue.MAX_UINT8:
				msglis.append(struct.pack("b", BIG_TUPLE_FLAG))
				msglis.append(struct.pack("H", size))
			else:
				msglis.append(struct.pack("b", SMALL_TUPLE_FLAG))
				msglis.append(struct.pack("B", size))
			for item in msgobj:
				self.packobj(item, msglis)
		elif t == types.ListType or t == type(set()):
			size = len(msgobj)
			if size > CValue.MAX_UINT8:
				msglis.append(struct.pack("b", BIG_LIST_FLAG))
				msglis.append(struct.pack("H", size))
			else:
				msglis.append(struct.pack("b", SMALL_LIST_FLAG))
				msglis.append(struct.pack("B", size))
			for item in msgobj:
				self.packobj(item, msglis)
		elif t == type(set()):
			size = len(msgobj)
			if size > CValue.MAX_UINT8:
				msglis.append(struct.pack("b", BIG_SET_FLAG))
				msglis.append(struct.pack("H", size))
			else:
				msglis.append(struct.pack("b", SMALL_SET_FLAG))
				msglis.append(struct.pack("B", size))
			for item in msgobj:
				self.packobj(item, msglis)
		elif t == types.DictType:
			size = len(msgobj)
			if size > CValue.MAX_UINT8:
				msglis.append(struct.pack("b", BIG_DICT_FLAG))
				msglis.append(struct.pack("H", size))
			else:
				msglis.append(struct.pack("b", SMALL_DICT_FLAG))
				msglis.append(struct.pack("B", size))
			for key, value in msgobj.iteritems():
				self.packobj(key, msglis)
				self.packobj(value, msglis)
		elif t == types.StringType:
			size = len(msgobj)
			if size > CValue.MAX_UINT8:
				msglis.append(struct.pack("b", BIG_STRING_FLAG))
				msglis.append(struct.pack("H", size))
			else:
				msglis.append(struct.pack("b", SMALL_STRING_FLAG))
				msglis.append(struct.pack("B", size))
			msglis.append(msgobj)
		elif t == datetime.datetime:
			msglis.append(struct.pack("b", DATETIME_FLAG))
			msglis.append(struct.pack("H", t.year))
			msglis.append(struct.pack("H", t.month))
			msglis.append(struct.pack("H", t.day))
			msglis.append(struct.pack("H", t.hour))
			msglis.append(struct.pack("H", t.minute))
			msglis.append(struct.pack("H", t.second))
		else:
			print "unpack type", t, msgobj
			assert False
	
	def unpackobj(self):
		flag = struct.unpack("b", self.body[:1])[0]
		self.body = self.body[1:]
		if flag > NONE_FLAG:
			return flag
		elif flag == NONE_FLAG:
			return None
		elif flag == TRUE_FLAG:
			return True
		elif flag == FALSE_FLAG:
			return False
		elif flag == SMALL_TUPLE_FLAG:
			size = struct.unpack("B", self.body[:1])[0]
			self.body = self.body[1:]
			lis = []
			for _ in xrange(size):
				lis.append(self.unpackobj())
			return tuple(lis)
		elif flag == BIG_TUPLE_FLAG:
			size = struct.unpack("H", self.body[:2])[0]
			self.body = self.body[2:]
			lis = []
			for _ in xrange(size):
				lis.append(self.unpackobj())
			return tuple(lis)
		elif flag == SMALL_LIST_FLAG:
			size = struct.unpack("B", self.body[:1])[0]
			self.body = self.body[1:]
			lis = []
			for _ in xrange(size):
				lis.append(self.unpackobj())
			return lis
		elif flag == BIG_LIST_FLAG:
			size = struct.unpack("H", self.body[:2])[0]
			self.body = self.body[2:]
			lis = []
			for _ in xrange(size):
				lis.append(self.unpackobj())
			return lis
		elif flag == SMALL_SET_FLAG:
			size = struct.unpack("B", self.body[:1])[0]
			self.body = self.body[1:]
			lis = []
			for _ in xrange(size):
				lis.append(self.unpackobj())
			return set(lis)
		elif flag == BIG_LIST_FLAG:
			size = struct.unpack("H", self.body[:2])[0]
			self.body = self.body[2:]
			lis = []
			for _ in xrange(size):
				lis.append(self.unpackobj())
			return set(lis)
		elif flag == SMALL_DICT_FLAG:
			size = struct.unpack("B", self.body[:1])[0]
			self.body = self.body[1:]
			dic = {}
			for _ in xrange(size):
				key = self.unpackobj()
				value = self.unpackobj()
				dic[key] = value
			return dic
		elif flag == BIG_DICT_FLAG:
			size = struct.unpack("H", self.body[:2])[0]
			self.body = self.body[2:]
			dic = {}
			for _ in xrange(size):
				key = self.unpackobj()
				value = self.unpackobj()
				dic[key] = value
			return dic
		elif flag == SMALL_STRING_FLAG:
			size = struct.unpack("B", self.body[:1])[0]
			self.body = self.body[1:]
			s = self.body[:size]
			self.body = self.body[size:]
			return s
		elif flag == BIG_STRING_FLAG:
			size = struct.unpack("H", self.body[:2])[0]
			self.body = self.body[2:]
			s = self.body[:size]
			self.body = self.body[size:]
			return s
		elif flag == DATETIME_FLAG:
			year = struct.unpack("H", self.body[:2])[0]
			self.body = self.body[2:]
			month = struct.unpack("H", self.body[:2])[0]
			self.body = self.body[2:]
			day = struct.unpack("H", self.body[:2])[0]
			self.body = self.body[2:]
			hour = struct.unpack("H", self.body[:2])[0]
			self.body = self.body[2:]
			minute = struct.unpack("H", self.body[:2])[0]
			self.body = self.body[2:]
			second = struct.unpack("H", self.body[:2])[0]
			self.body = self.body[2:]
			return datetime.datetime(year, month, day, hour, minute, second)
		elif flag == SIGNED_INT8_FLAG:
			i = struct.unpack("b", self.body[:1])[0]
			self.body = self.body[1:]
			return i
		elif flag == SIGNED_INT16_FLAG:
			i = struct.unpack("h", self.body[:2])[0]
			self.body = self.body[2:]
			return i
		elif flag == SIGNED_INT32_FLAG:
			i = struct.unpack("i", self.body[:4])[0]
			self.body = self.body[4:]
			return i
		elif flag == SIGNED_INT64_FLAG:
			i = struct.unpack("q", self.body[:8])[0]
			self.body = self.body[8:]
			return i
		else:
			print "unpack flag", flag, self.body
			assert False
	
	def __recvmsg(self):
		head = ""
		while len(head) != 4:
			head += self.sock.recv(4 - len(head))
		bodylen, msgtype = struct.unpack("HH", head)
		bodylen -= 4
		if bodylen == 0:
			return msgtype, ""
		body = ""
		while len(body) != bodylen:
			body += self.sock.recv(bodylen - len(body))
		return msgtype, body

	def recvmsg(self):
		assert not self.thread
		return self.__recvmsg()
	
	def recvobj(self):
		assert not self.thread
		msgtype, self.body = self.__recvmsg()
		if self.body:
			obj = self.unpackobj()
		else:
			obj = None
		del self.body
		return msgtype, obj
	
	def __threadrecvmsg(self):
		while self.thread:
			try:
				msgtype, msgbody = self.__recvmsg()
				fun = self.functions.get(msgtype)
				if fun: fun(msgbody)
			except:
				self.thread = False
				print "gm __recvmsg error."
	
	def __threadprintobj(self):
		while self.thread:
			try:
				msgtype, self.body = self.__recvmsg()
				obj = self.unpackobj()
				print msgtype
				PrintHelp.pprint(obj)
			except:
				#self.thread = False
				print "gm __threadprintobj error."
	
	def __threadrecvobj(self):
		while self.thread:
			try:
				msgtype, self.body = self.__recvmsg()
				obj = self.unpackobj()
				self.queue.put((msgtype, obj))
			except:
				#self.thread = False
				print "gm __threadrecvobj error."
	
	def threadrecvmsg(self):
		self.thread = True
		thread.start_new_thread(self.__threadrecvmsg, ())
	
	def threadprintobj(self):
		self.thread = True
		thread.start_new_thread(self.__threadprintobj, ())
	
	def threadrecvobj(self):
		self.thread = True
		thread.start_new_thread(self.__threadrecvobj, ())
	
	def iterobj(self):
		try:
			yield self.queue.get_nowait()
		except:
			pass
	
	def gmcommand(self, command):
		self.sendobj(PyMessage.GM_Request, command)
		msgtype, msgobj = self.recvobj()
		assert msgtype == PyMessage.GM_Response
		return msgobj
	
	def close(self):
		self.thread = False
		self.sock.close()

if __name__ == "__main__":
	import time
	gm = GMConnect("127.0.0.1", 9000, True)
	gm.iamgm()
	print gm.gmcommand("print %s" % ("1" * 9000))
	time.sleep(55)


