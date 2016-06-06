#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 移动CDKey
#===============================================================================
import os
import sys
path = os.path.dirname(os.path.realpath(__file__))
path = path[:path.find("PyCode") + 6]
if path not in sys.path: sys.path.append(path)
path = path.replace("PyCode", "PyHelp")
if path not in sys.path: sys.path.append(path)

from Util import Slice
from ComplexServer.Plug.DB import DBHelp

def Move():
	con = DBHelp.ConnectGlobalWeb();
	with con as cur:
		for table in ["cdkey_a1", "cdkey_a2", "cdkey_a3", "cdkey_a4", "cdkey_a5"]:
			cur.execute("select cdkey, role_id, activaty_datetime from web_global_qq.%s;" % table)
			result = cur.fetchall()
			h = 0
			for chunk in Slice.IterSlice(result, 1000):
				c = cur.executemany("insert ignore web_global_3737." + table + " (cdkey, role_id, activaty_datetime) values (%s, %s, %s)", chunk);
				if c:
					h += c
			print "result:", len(result), "h:", h

if __name__ == "__main__":
	Move()
