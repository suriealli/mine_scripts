#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 检测服务器哪里卡了，打印当前线程堆栈
#===============================================================================
import sys
import time
import threading
import traceback
import cProcess
import cDateTime
import DynamicPath

if "_HasLoad" not in dir():
	WT = None

class WatchThread(threading.Thread):
	def run(self):
		self.is_run = True
		self.last_seconds = cDateTime.Seconds()
		while self.is_run:
			# 休眠2秒
			for _ in xrange(4):
				time.sleep(0.5)
				if not self.is_run:
					break
			# 如果主线程时间未刷新，则主线程可能死循环了
			now_seconds = cDateTime.Seconds()
			if now_seconds == self.last_seconds:
				self.print_main_stack()
			self.last_seconds = now_seconds
	
	def print_main_stack(self):
		from ComplexServer.Plug.Http import HttpWork
		from ComplexServer.Plug.DB import DBWork
		thread_info = sys._current_frames()
		for thread in HttpWork.HTTP_THREAD_LIST:
			if thread.ident in thread_info:
				del thread_info[thread.ident]
		for thread in DBWork.DB_THREAD_LIST:
			if thread.ident in thread_info:
				del thread_info[thread.ident]
		if self.ident in thread_info:
			del thread_info[self.ident]
		# 打印线程栈
		now = cDateTime.Now()
		file_path = "%sMainStack_%s_%s_%s_%s_%s.log" % (DynamicPath.FilePath, cProcess.ProcessType, cProcess.ProcessID, now.year, now.month, now.day)
		with open(file_path, "a") as f:
			for thread_stack in thread_info.itervalues():
				print>>f, "%s Traceback:" % cDateTime.Now()
				traceback.print_stack(thread_stack, None, f)
				print>>f, "CycleError: endless cycle"
	
	def stop(self):
		self.is_run = False

def StartWorkThread():
	global WT
	WT = WatchThread()
	WT.start()

def StopWorkThread():
	global WT
	if not WT:
		return
	WT.stop()
	WT.join(5)
	WT = None
