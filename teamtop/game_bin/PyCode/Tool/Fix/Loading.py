#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 查找导量问题
#===============================================================================
import os
import sys
path = os.path.dirname(os.path.realpath(__file__))
path = path[:path.find("PyCode") + 6]
if path not in sys.path: sys.path.append(path)
path = path.replace("PyCode", "PyHelp")
if path not in sys.path: sys.path.append(path)

from ComplexServer.Plug.DB import DBHelp

DBIDS = range(383, 390)
def check_all():
	for dbid in DBIDS:
		check_1(dbid)
	print
	for dbid in DBIDS:
		check_2(dbid)
	print
	for dbid in DBIDS:
		check_3(dbid)

def check_1(dbid):
	con = DBHelp.ConnectMasterDBByID(dbid)
	with con as cur:
		cur.execute("select HOUR(connect_time), count(*) from connect_info where request_create != 0 and from_1 = 'qqgame' group by HOUR(connect_time);")
		d = {}
		for hour, cnt in cur.fetchall():
			d[hour] = cnt
		print "*%s " % dbid,
		for idx in xrange(24):
			cnt = str(d.get(idx, 0))
			cnt = cnt.ljust(4)
			print cnt,
		print

def check_2(dbid):
	con = DBHelp.ConnectMasterDBByID(dbid)
	with con as cur:
		cur.execute("select HOUR(connect_time), count(*) from connect_info where request_create = 0 and from_1 = 'qqgame'  group by HOUR(connect_time);")
		d = {}
		for hour, cnt in cur.fetchall():
			d[hour] = cnt
		print "*%s " % dbid,
		for idx in xrange(24):
			cnt = str(d.get(idx, 0))
			cnt = cnt.ljust(4)
			print cnt,
		print

ACCOUNTS = {}
USERIPS = {}
def check_3(dbid):
	con = DBHelp.ConnectMasterDBByID(dbid)
	with con as cur:
		cur.execute("select account, userip from connect_info where request_create = 0;")
		for account, userip in cur.fetchall():
			ACCOUNTS[account] = ACCOUNTS.get(account, 0) + 1
			USERIPS[userip] = USERIPS.get(userip, 0) + 1
	if dbid >= 389:
		for d in [ACCOUNTS, USERIPS]:
			kv = d.items()
			kv.sort(key=lambda item:item[1])
			kv = kv[-40:]
			kv.sort(key=lambda item:item[0])
			for k, v in kv:
				print k, "-", v
		ta = 0
		la = 0
		for _, c in ACCOUNTS.iteritems():
			if c > 1:
				ta += c
				la += 1
		print "account", ta, la

if __name__ == "__main__":
	check_all()
