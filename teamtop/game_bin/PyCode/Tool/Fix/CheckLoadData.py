#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 检测载入数据
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
from ComplexServer.Plug.DB import DBHelp
from Common import Serialize
from Integration.Help import WorldHelp

datetime
TABLES = ["sys_persistence", "sys_union", "sys_jjc", "univerbuy_info",
		"sys_rolefightdata", "sys_role_view", "sys_role_slave", "sys_wonderfulactdata", "sys_ring"]
THREADS = []
LOCK = threading.Lock()

def reset():
	with open("log.txt", "w"):
		pass

def log(zone_id, l, s, o, total):
	with LOCK:
		with open("log.txt", "a") as f:
			print>>f, zone_id, int(l), int(s), int(o), total

def show():
	with open("log.txt", "r") as f:
		print f.read()

class LoadThread(threading.Thread):
	def __init__(self, zone_id):
		self.zone_id = zone_id
		self.result = []
		self.s = []
		self.o = []
		self.total = 0
		threading.Thread.__init__(self)
	
	def run(self):
		t1 = time.time()
		con = DBHelp.ConnectMasterDBByID(self.zone_id)
		with con as cur:
			for name in TABLES:
				cur.execute("select * from %s;" % name)
				self.result.append(cur.fetchall())
		t2 = time.time()
		for r in self.result:
			s = Serialize.PyObj2String(r)
			self.total += len(s)
			self.s.append(s)
		t3 = time.time()
		for s in self.s:
			self.o.append(Serialize.String2PyObj(s))
		t4 = time.time()
		log(self.zone_id, t2 - t1, t3 - t2, t4 - t3, self.total)

if __name__ == "__main__":
	reset()
	for zone_id in WorldHelp.GetZone().iterkeys():
		t = LoadThread(zone_id)
		t.start()
		THREADS.append(t)
	for t in THREADS:
		t.join()
	show()
	print "END"
