#!/usr/bin/env python
# -*- coding:UTF-8 -*-
import os
import sys
path = os.path.dirname(os.path.realpath(__file__))
path = path[:path.find("PyCode") + 6]
if path not in sys.path: sys.path.append(path)
path = path.replace("PyCode", "PyHelp")
if path not in sys.path: sys.path.append(path)
#===============================================================================
# 构建任务进程
#===============================================================================
import DynamicPath

def BuildLinux():
	from ComplexServer.Plug.DB import DBHelp
	con = DBHelp.ConnectGlobalWeb()
	mutexs = set([])
	mutexs.add(("no_mutex", 5))
	with con as cur:
		cur.execute("select name from mysql;")
		for mysql_name, in cur.fetchall():
			mutexs.add((mysql_name, 1))
	for mutex, cnt in mutexs:
		print "python %sTool/WorkTask.py %s %s" % (DynamicPath.PyFloderPath, mutex, cnt)

if __name__ == "__main__":
	BuildLinux()
