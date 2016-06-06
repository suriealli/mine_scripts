#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 任务系统
#===============================================================================
import datetime
import traceback
from ThirdLib import PrintHelp
from ComplexServer.Plug.DB import DBHelp
from Integration import AutoHTML

datetime

def safe_repr(o):
	return PrintHelp.saferepr(o)

class Task(object):
	NO_MUTEX = "no_mutex"
	RTYPE = None
	def __init__(self, tid = 0):
		self.tid = tid
		self.ctasks = []
		self.errors = []
		self.results = []
		self.rows = 0
	
	def append_ctask(self, ctid, cname):
		assert ctid not in self.ctasks
		self.ctasks.append((ctid, cname))
	
	def create(self, name, instruction, argv):
		if instruction.startswith("#"):
			bsmall = True
		else:
			bsmall = self.test_ctask(argv)
		con = DBHelp.ConnectHouTaiWeb()
		with con as cur:
			cur.execute("select count(*) from task where total != finish")
			cnt = cur.fetchall()[0][0]
			if cnt > 100:
				return 0
			sql = "insert into task (cls, name, instruction, argv, total) values (%s, %s, %s, %s, %s)"
			param = (safe_repr((self.__class__.__module__, self.__class__.__name__)), name, instruction, safe_repr(argv), len(self.ctasks))
			cur.execute(sql, param)
			self.tid = con.insert_id()
			for ctid, cname in self.ctasks:
				if bsmall:
					cname = "#" + cname
				cur.execute("insert into ctask (tid, ctid, cname, mutex) values(%s, %s, %s, %s)", (self.tid, ctid, cname, self._get_mutex(ctid)))
			return self.tid
	
	def test_ctask(self, argv):
		test_cnt = 4
		if len(self.ctasks) < test_cnt:
			return True
		for idx in xrange(test_cnt):
			ridx = int(float(idx) / test_cnt * len(self.ctasks))
			ctid, cname = self.ctasks[ridx]
			self.rows = 0
			self._do_ctask(ctid, argv, "limit 10000")
			self.ctasks[ridx] = (ctid, "%s【%s】" % (cname, self.rows))
			if self.rows >= 9999:
				return False
		return True
	
	def _get_mutex(self, ctid):
		return self.NO_MUTEX
	
	def do_ctask(self, lock_id, ctid, process):
		try:
			con = DBHelp.ConnectHouTaiWeb()
			with con as cur:
				cur.execute("select argv from task where tid = %s;" % self.tid)
				argv = eval(cur.fetchall()[0][0])
			con.close()
			
			try:
				result = self._do_ctask(ctid, argv)
			except:
				result = traceback.format_exc()
			
			con = DBHelp.ConnectHouTaiWeb()
			with con as cur:
				h = cur.execute("update ctask set result = %s, work_state = 'ok' where lock_id = %s and process = %s and result is NULL;", (safe_repr(result), lock_id, process))
				if h:
					cur.execute("update task set finish = finish + 1 where tid = %s;" % self.tid)
					return True
				else:
					return False
		except:
			return traceback.format_exc()
	
	def _do_ctask(self, ctid, argv, limit = ""):
		assert False
	
	def do_task(self):
		try:
			con = DBHelp.ConnectHouTaiWeb()
			with con as cur:
				cur.execute("select ctid, cname, process, work_state, result from ctask where tid = %s;" % self.tid)
				for ctid, cname, process, work_state, result in cur.fetchall():
					if result is None:
						continue
					result = eval(result)
					if self._is_result(result):
						if type(result) == str:
							self.errors.append((ctid, cname, AutoHTML.PyStringToHtml(result)))
						else:
							self.errors.append((ctid, cname, AutoHTML.PyObjToHtml(result)))
						continue
					self.results.append((ctid, cname, result))
			con.close()
		except:
			return traceback.format_exc()
	
	def _is_result(self, result):
		return self.RTYPE is not None and self.RTYPE != type(result)
	
	def get_task_error(self):
		if self.errors:
			table = AutoHTML.Table(["子任务ID", "子任务名", "错误详情"], self.errors, "问题列表")
			return table.ToHtml()
		else:
			return ""
	def get_task_result(self):
		return "get_task_result"
	
class ZoneTask(Task):
	def _get_mutex(self, ctid):
		con = DBHelp.ConnectGlobalWeb()
		with con as cur:
			cur.execute("select mysql_name from zone where zid = %s" % ctid)
			return cur.fetchall()[0][0]
