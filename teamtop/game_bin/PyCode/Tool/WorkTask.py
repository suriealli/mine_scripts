#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 任务工作
#===============================================================================
import os
import sys
path = os.path.dirname(os.path.realpath(__file__))
path = path[:path.find("PyCode") + 6]
if path not in sys.path: sys.path.append(path)
path = path.replace("PyCode", "PyHelp")
if path not in sys.path: sys.path.append(path)

import time
import datetime
import threading
import traceback
import Environment
import DynamicPath
from Util import OutBuf
from ComplexServer.Plug.DB import DBHelp

class TaskThread(threading.Thread):
	def __init__(self, mutex):
		threading.Thread.__init__(self)
		self.mutex = mutex
	
	def get_process(self):
		return "%s.%s" % (self.mutex, self.ident)
	
	def run(self):
		with OutBuf.OutLog_NoExcept(get_log_file_path(self.mutex), PLOCK):
			while 1:
				# 这里防止死锁，要分段处理
				has_task = False
				get_task = False
				# 1查询是否有任务
				con = DBHelp.ConnectHouTaiWeb()
				with con as cur:
					try:
						# 凌晨可以做所有的工作
						if WORK_TIME[0] < datetime.datetime.now().time() < WORK_TIME[1]:
							cur.execute("select lock_id, tid, ctid from ctask where mutex = %s and process = '' limit 1;", self.mutex)
						# 其他时间段做轻松的工作
						else:
							cur.execute("select lock_id, tid, ctid from ctask where mutex = %s and process = '' and cname like '#%%' limit 1;", self.mutex)
						result1 = cur.fetchall()
					except:
						traceback.print_exc()
						result1 = []
					if result1:
						lock_id, tid, ctid = result1[0]
						cur.execute("select cls from task where tid = %s;" % tid)
						result2 = cur.fetchall()
						if result2:
							logic = eval(result2[0][0])
							has_task = True
				# 2如果有任务，尝试获取任务
				if has_task:
					try:
						with con as cur:
							cur.execute("select process from ctask where lock_id = %s for update;", lock_id)
							result3 = cur.fetchall()
							if result3 and result3[0][0] == "":
								cur.execute("update ctask set process = %s, work_state = %s, start_time = now() where lock_id = %s;", (self.get_process(), "working", lock_id))
								get_task = True
					except:
						traceback.print_exc()
				# 此时可以关闭连接了
				con.close()
				# 3如果获取到了任务，执行任务
				if get_task:
					self.work(logic, lock_id, tid, ctid)
				else:
					time.sleep(1)
	
	def work(self, logic, lock_id, tid, ctid):
		from Integration import AutoHTML
		try:
			self.log("working task(%s), ctask(%s)" % (tid, ctid))
			module_name, cls_name = logic
			__import__(module_name)
			module = sys.modules[module_name]
			# 做着一步是为了保证代码最新
			reload(module)
			module = sys.modules[module_name]
			cls = getattr(module, cls_name)
			obj = cls(tid)
			ret = obj.do_ctask(lock_id, ctid, self.get_process())
			if ret is True:
				self.log("success task(%s), ctask(%s)" % (tid, ctid))
			elif ret is False:
				self.log("fail task(%s), ctask(%s)" % (tid, ctid))
			else:
				con = DBHelp.ConnectHouTaiWeb()
				with con as cur:
					cur.execute("update ctask set work_state = %s where tid = %s and ctid = %s and process = %s and result is NULL;", (AutoHTML.PyStringToHtml(str(ret)), tid, ctid, self.get_process()))
				con.close()
		except:
			con = DBHelp.ConnectHouTaiWeb()
			with con as cur:
				cur.execute("update ctask set work_state = %s where tid = %s and ctid = %s and process = %s and result is NULL;", (AutoHTML.PyStringToHtml(traceback.format_exc()), tid, ctid, self.get_process()))
			con.close()
	
	def log(self, s):
		with PLOCK:
			with open(get_log_file_path(self.mutex), "a") as f: 
				f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
				f.write(" : ")
				f.write(s)
				f.write("\n")
	
def get_log_file_path(mutex):
	return DynamicPath.FilePath + "WorkTask_%s-%s.log" % (mutex, os.getpid())

def do_work(mutex, cnt):
	if Environment.IsWindows:
		os.system("del %s*.log" % DynamicPath.FilePath)
	else:
		open(get_log_file_path(mutex), "w").close()
	
	from django.core.management import setup_environ
	from Integration import settings
	setup_environ(settings)
	
	thread_list = []
	for _ in xrange(cnt):
		thread_list.append(TaskThread(mutex))
	for thread in thread_list:
		thread.start()
	for thread in thread_list:
		thread.join()

if __name__ == "__main__":
	PLOCK = threading.Lock()
	WORK_TIME = (datetime.time(2, 30, 0), datetime.time(5, 0, 0))
	if len(sys.argv) >= 3:
		do_work(sys.argv[1], int(sys.argv[2]))
	else:
		do_work("mysql_108", 3)
