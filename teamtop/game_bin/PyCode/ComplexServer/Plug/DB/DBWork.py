#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("ComplexServer.Plug.DB.DBWork")
#===============================================================================
# 数据库服务模块
#===============================================================================
import time
import Queue
import threading
import traceback
import cProcess
import cDateTime
import cComplexServer
from Common import Define
from ComplexServer import Thread, Statistics, BigMessage
from ComplexServer.Plug.DB import DBHelp

if "_HasLoad" not in dir():
	SERVER_GONE_ERROR = 2006
	IS_NET_MODEL = False
	# 连接要加锁
	ConnectLock = threading.Lock()
	# 显示异常要加锁
	TracebackLock = threading.Lock()


def NetModel():
	global IS_NET_MODEL
	IS_NET_MODEL = True

class DBVisit(object):
	@classmethod
	def reg(cls, alise = None):
		if cls.__name__ in DB_CLASS:
			print "GE_EXC, repeat db class(%s)." % cls.__name__
		DB_CLASS[cls.__name__] = cls
		if alise is not None:
			if alise in DB_CLASS:
				print "GE_EXC, repeat db alise(%s)." % alise
			DB_CLASS[alise] = cls
	
	def __init__(self, arg, back):
		self.arg = arg
		self.back = back  #local-->(backfun, regparam) or net-->#(sessionid, regparam)
	
	def executeex(self, thread):
		self.execute(thread.con)
	
	def execute(self, con):
		with con as cur:
			self.result(self._execute(cur))
			cur.close()
	
	def _execute(self, cur):
		return 
	
	def isnet(self):
		global IS_NET_MODEL
		return IS_NET_MODEL
	
	def result(self, dbresult):
		back1, back2 = self.back
		# 如果第一个返回信息是整数，则认为是网络模式
		if type(back1) is int or type(back1) is long:
			# back2就是回调函数id了，如果为0就是不需要回调的
			if back2:
				Thread.ThreadApply(OnDBReturn_Net_MainThread, (back1, back2, dbresult))
		# 否则认为是本地模式
		else:
			# back1就是回调函数了，如果为None说明不需要回调
			if back1 is not None:
				Thread.ThreadApply(OnDBReturn_Local_MainThread, (back1, back2, dbresult))
	
	def result_big(self, dbresult):
		back1, back2 = self.back
		# 如果第一个返回信息是整数，则认为是网络模式
		if type(back1) is int or type(back1) is long:
			# back2就是回调函数id了，如果为0就是不需要回调的
			if back2:
				Thread.ThreadApply(OnDBReturnBig_Net_MainThread, (back1, back2, dbresult))
		# 否则认为是本地模式
		else:
			# back1就是回调函数了，如果为None说明不需要回调
			if back1 is not None:
				Thread.ThreadApply(OnDBReturn_Local_MainThread, (back1, back2, dbresult))

class WorkThread(threading.Thread):
	def __init__(self, publicqueue, privatequeue, channel):
		threading.Thread.__init__(self)
		self.publicqueue = publicqueue
		self.privatequeue = privatequeue
		self.channel = channel
		# 角色权限
		self.rolelimit = {}
		self.connect()
		# 保存计时器
		self.lascsecond = cDateTime.Seconds()
	
	def connect(self):
		ConnectLock.acquire()
		try:
			self.con = DBHelp.ConnectMasterDBByID(cProcess.ProcessID)
			self.open = True
			# 打印一下连接成功
			print "BLUE %s connect mysql ok." % self.channel
			return True
		except Exception, e:
			self.open = False
			# 打印一下连接不成功
			print "RED %s connect mysql fail(%s)." % (self.channel, str(e))
			return False
		finally:
			ConnectLock.release()
		
	def ping(self):
		try:
			self.con.ping()
			return True
		except:
			return self.connect()
	
	def ntask(self):
		try:
			return self.privatequeue.get_nowait()
		except:
			try:
				return self.publicqueue.get_nowait()
			except:
				return None
	
	def start(self):
		threading.Thread.start(self)
		# 保存进程信息
		Thread.ThreadID_Name[self.ident] = "DBWorkThread"
	
	def stop(self):
		self.isrun = False
	
	def do_task(self, task, retry = 0):
		try:
			task.executeex(self)
		except Exception, e:
			# 先打印异常
			self.show_traceback()
			# 再检测连接状况
			self.ping()
			# 如果是断开服务器错误, 并且有重试次数，重新执行之
			if isinstance(e.args, tuple) and len(e.args) > 1 and e.args[0] == SERVER_GONE_ERROR and retry > 0:
				self.do_task(task, retry - 1)
	
	def show_traceback(self):
		if not self.open:
			return
		# 这里加锁，是为了断开连接的时候打印的异常好看些
		with TracebackLock:
			traceback.print_exc()
	
	def run(self):
		self.isrun = True
		# 以下的每个函数都要求无异常
		while self.isrun:
			# 数据库线程每秒调用一次的函数
			now = cDateTime.Seconds()
			if self.lascsecond != now:
				self.lascsecond = now
				self.callpersecond()
			# 真正的数据库任务
			task = self.ntask()
			if task:
				self.do_task(task, 1)
			else:
				time.sleep(0.01)
	
	def callpersecond(self):
		try:
			task = DB_CLASS["CheckCommand"](None, None)
			self.do_task(task)
		except:
			self.show_traceback()

if "_HasLoad" not in dir():
	PUBLIC_QUEUE = Queue.Queue(0)
	PRIVATE_QUEUE_LIST = []
	DB_THREAD_LIST = []
	DB_CLASS = {}
	Sta = Statistics.Statistics("数据库访问")

def GetQuerySize():
	size = PUBLIC_QUEUE.qsize()
	for query in PRIVATE_QUEUE_LIST:
		size += query.qsize()
	return size

def StartWorkThread():
	'''
	开启工作线程
	'''
	for channel in xrange(Define.DB_THREAD_NUM):
		pqueue = Queue.Queue(0)
		thread = WorkThread(PUBLIC_QUEUE, pqueue, channel)
		thread.start()
		PRIVATE_QUEUE_LIST.append(pqueue)
		DB_THREAD_LIST.append(thread)

def StopWorkThread():
	'''
	关闭工作线程
	'''
	# 1等待访问队列为空（最多等待15秒）
	for idx in xrange(15):
		if GetQuerySize() == 0:
			print "RED, db query empty in %s second." % idx
			break
		else:
			time.sleep(1)
	else:
		print "GE_EXC, db query is not empty."
	# 2关闭线程
	for thread in DB_THREAD_LIST:
		thread.stop()
	# 3等待线程放回
	for thread in DB_THREAD_LIST:
		thread.join(10)
	print "RED, db thread is join."

def OnDBVisit_MainThread(channel, classname, arg, back):
	'''
	访问DB请求（主线程调用）
	@param channel:频道
	@param classname:类名
	@param arg:参数
	@param back:回调信息
	'''
	cls = DB_CLASS.get(classname)
	if not cls:
		print "GE_EXC, can't find db class(%s)" % classname
		return
	# 统计
	Sta.Inc(classname)
#	if cls.__module__ in ("DB.PersistenceVisit","DB.BigTableVisit"):
#			if cls.__name__ == "SavePerData":
#				print "--------save persistence data", arg[0], cDateTime.Now()
#			if cls.__name__ in ("DelBTData", "SaveBTData"):
#				print "--------save bigtable        ", arg[0], cDateTime.Now()
#	if cls.__module__ == "DB.RoleVisit":
#		if cls.__name__ in ("SaveRole"):
#			print "RED", cls.__name__
#		else:
#			print "RED", cls.__name__, arg
	if channel is None:
		PUBLIC_QUEUE.put(cls(arg, back))
	else:
		# 关于角色ID和线程号直接的关系请搜索  !@RoleChannel
		PRIVATE_QUEUE_LIST[channel % Define.DB_THREAD_NUM].put(cls(arg, back))


def OnDBReturn_Local_MainThread(backfun, regparam, dbresult):
	'''
	DB请求返回，本地模式下（主线程调用）
	@param backfun:回调函数
	@param regparam:回调注册参数
	@param dbresult:数据库结果
	'''
	backfun(dbresult, regparam)

def OnDBReturn_Net_MainThread(sessionid, backfunid, dbresult):
	'''
	DB请求返回，网络模式下（主线程调用）
	@param sessionid:回调函数
	@param backfunid:回调注册参数
	@param dbresult:数据库结果
	'''
	cComplexServer.CallBackFunction(sessionid, backfunid, dbresult)

def OnDBReturnBig_Net_MainThread(sessionid, backfunid, dbresult):
	'''
	DB请求返回大数据，网络模式下（主线程调用）
	@param sessionid:回调函数
	@param backfunid:回调注册参数
	@param dbresult:数据库结果
	'''
	BigMessage.CallBack(sessionid, backfunid, dbresult)

