#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 并行运算
#===============================================================================
import sys
import time
import Queue
import threading
import traceback
from MySQLdb import cursors
import Environment
from Tool.GM import GMCMD
from Integration import AutoHTML
from Integration.Help import WorldHelp
from ComplexServer.Plug.DB import DBHelp

class Task(object):
	def __init__(self, task_id):
		self.task_id = task_id
	
	def do(self):
		try:
			return self._do()
		except:
			if Environment.IsWindows:
				traceback.print_exc()
			return str(sys.exc_info()[1])
	
	def _do(self):
		pass
	
	def stop(self):
		try:
			self._stop()
		except:
			if Environment.IsWindows:
				traceback.print_exc()
	
	def _stop(self):
		pass

class GMTask(Task):
	def __init__(self, task_id, command):
		Task.__init__(self, task_id)
		self.command = command
		self.gm = None
		self.lock = threading.Lock()
	
	def _do(self):
		process = WorldHelp.GetProcess().get(self.task_id)
		# 可能连接不上，必须在锁范围以外
		gm = GMCMD.GMConnect(process.ip, process.port, process.has_gateway())
		with self.lock:
			if self.gm is False:
				return
			self.gm = gm
		self.gm.iamgm()
		return self.gm.gmcommand(self.command)
	
	def _stop(self):
		with self.lock:
			if self.gm:
				self.gm.sock.close()
			self.gm = False

class DBTask(Task):
	def __init__(self, task_id, sql, start_time, end_time):
		Task.__init__(self, task_id)
		self.sql = sql
		self.start_time = start_time
		self.end_time = end_time
	
	def _do(self):
		result = []
		if self.start_time != self.end_time:
			con = DBHelp.ConnectMasterDBByID(self.task_id, "role_sys_log")
			from Integration.WebPage.DataBase import RoleLog
			with con as cur:
				suffs = RoleLog.get_suffs(cur, self.start_time, self.end_time)
		else:
			con = DBHelp.ConnectMasterDBByID(self.task_id)
			suffs = [""]
		con.cursorclass = cursors.DictCursor
		with con as cur:
			for suff in suffs:
				sql = self.sql % {"dbid":self.task_id, "suff":suff}
				cur.execute(sql)
				result.extend(cur.fetchall())
		return result

class WorkThread(threading.Thread):
	def __init__(self, group):
		threading.Thread.__init__(self)
		self.group = group
		self.task = None
		self.lock = threading.Lock()
	
	def get(self):
		with self.lock:
			self.task = self.group.get()
	
	def stop(self, timeout):
		# 等待指定的时间
		self.join(timeout)
		# 强行结束任务
		with self.lock:
			if self.task:
				self.task.stop()
	
	def run(self):
		while self.group.isrun:
			# 线程安全的获取任务
			self.get()
			# 如果没有任务，则退出工作循环
			if self.task is None:
				break
			# 执行任务
			results = self.task.do()
			# 保存结果
			self.group.put_results(self.task.task_id, results)
		# 所有任务执行完成

class TaskGroup(object):
	def __init__(self):
		self.applys = Queue.Queue(0)
		self.lock = threading.Lock()
		self.tasks = []
		self.results = {}
		self.results_types = None
		self.task_time = 5
		self.thread_cnt = 10
		self.isrun = True
	
	def append(self, task):
		assert task.task_id not in self.tasks
		self.applys.put(task)
		self.tasks.append(task.task_id)
	
	def get(self):
		try:
			return self.applys.get_nowait()
		except Queue.Empty:
			pass
		except:
			if Environment.IsWindows:
				traceback.print_exc()
		return None
	
	def put_results(self, task_id, task_results):
		if not self.isrun:
			return
		with self.lock:
			if self.results_types is None:
				self.results[task_id] = task_results
			elif isinstance(task_results, self.results_types):
				self.results[task_id] = task_results
	
	def is_all_ok(self):
		return len(self.results) == len(self.tasks)
	
	def execute(self):
		threads = []
		for _ in xrange(min(self.thread_cnt, len(self.tasks))):
			thread = WorkThread(self)
			thread.start()
			threads.append(thread)
		# 等待线程结束
		begin_time = int(time.time())
		thread_time = self.task_time * (len(self.tasks) / self.thread_cnt + 1)
		for thread in threads:
			use_time = int(time.time()) - begin_time
			timeout = 1 if use_time >= thread_time else thread_time - use_time
			thread.stop(timeout)
		# 不再接受结果
		self.isrun = False
		# 返回结果
		return self.results
	
	def to_html(self, keyfun = None, keycmp = None, valuefun = None):
		if self.is_all_ok():
			table = ["<font color='blue'>%s个请求全部返回结果</font><br>" % len(self.tasks)]
		else:
			table = ["<font color='red'>请求：%s, 结果：%s</font><br>" % (len(self.tasks), len(self.results))]
		# 按照任务ID排序
		self.tasks.sort()
		# 构建表格
		table.append("<table border='1'>")
		table.append("<tr><td>%s</td><td>%s</td></tr>" % ("KEY", "结果"))
		pass_v = 0
		for key in self.tasks:
			value = self.results.get(key, "no return")
			# 先变换结果数据
			if valuefun:
				value = valuefun(value)
			# 如果不需要显示则忽视之
			if value is True:
				pass_v += 1
				continue
			# 尝试字符串的html转换
			if type(value) == str:
				value = AutoHTML.PyStringToHtml(value)
			# 转换key
			if keyfun:
				key = keyfun(key)
			# 构建之
			table.append("<tr><td>%s</td><td>%s</td></tr>" % (key, value))
		table.append("</table>")
		if pass_v:
			table.append("<br><font color='blue'>%s个结果不显示</font>" % pass_v)
		return "".join(table)

def GMCommand(pkey, command):
	process = WorldHelp.GetProcess().get(pkey)
	if not process:
		return None
	gm = GMCMD.GMConnect(process.ip, process.port, process.has_gateway())
	gm.iamgm()
	return gm.gmcommand(command)

