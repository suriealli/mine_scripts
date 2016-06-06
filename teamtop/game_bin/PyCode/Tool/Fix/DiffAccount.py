#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 查询不同的账号
#===============================================================================
import os
import sys
import datetime
datetime
path = os.path.dirname(os.path.realpath(__file__))
path = path[:path.find("PyCode") + 6]
if path not in sys.path: sys.path.append(path)
path = path.replace("PyCode", "PyHelp")
if path not in sys.path: sys.path.append(path)

from ComplexServer.Plug.DB import DBHelp

def diff_account():
	client_account = {}
	server_account = {}
	all_account = set()
	
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		cur.execute("select openid, status from stat.stat where time > '2014-10-30 16:00:00' and server = 394;")
		for account, status in cur.fetchall():
			client_account[account] = status
			all_account.add(account)
	
	con = DBHelp.ConnectMasterDBByID(394)
	with con as cur:
		cur.execute("select account, request_create, from_1 from role_sys_data_394.connect_info where connect_time > '2014-10-30 16:00:00';")
		for account, request_create, from_1 in cur.fetchall():
			server_account[account] = (request_create, from_1)
			all_account.add(account)
	
	for account in all_account:
		status = client_account.get(account)
		request_create = server_account.get(account)
		if status is not None and request_create is not None:
			continue
		print account, status, request_create

if __name__ == "__main__":
	diff_account()

	