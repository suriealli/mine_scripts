#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# c
#===============================================================================
# 跨线程调用
#===============================================================================
import sys
import Queue
import traceback

if "_HasLoad" not in dir():
	ThreadID_Name = {}

class CallQueue(Queue.Queue):
	'''
	跨Python线程函数调用队列
	'''
	def _init(self, maxsize):
		self.queue = []
	
	def _qsize(self):
		return len(self.queue)
	
	def _put(self, item):
		self.queue.append(item)
	
	def _get(self):
		q = self.queue
		self.queue = []
		return q

if "_HasLoad" not in dir():
	ThreadCallQueue = CallQueue()

def MainThreadCall():
	'''
	主线程呼叫跨线程函数队列中的函数
	'''
	try:
		calls = ThreadCallQueue.get_nowait()
		for call in calls:
			try:
				apply(*call)
			except:
				traceback.print_exc()
	except Queue.Empty:
		pass
	except:
		traceback.print_exc()

def ThreadApply(fun, argv):
	'''
	副线程请求主线程呼叫函数
	@param fun:函数
	@param argv:调用参数
	'''
	ThreadCallQueue.put((fun, argv))

def ShowThread(name = None):
	'''
	显示Python线程信息
	@param name:线程名
	'''
	for thread_id, stack in sys._current_frames().items():
		# 只显示没标记的线程栈
		if name is False and thread_id in ThreadID_Name:
			continue
		# 只显示标记的线程栈
		if name is True and thread_id not in ThreadID_Name:
			continue
		# 只显示指定名称的线程
		if isinstance(name, str) and ThreadID_Name.get(thread_id) != name:
			continue
		# 显示之
		traceback.print_stack(stack)

