#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 统计等待状态
#===============================================================================
import os
import sys
import datetime
path = os.path.dirname(os.path.realpath(__file__))
path = path[:path.find("PyCode") + 6]
if path not in sys.path: sys.path.append(path)
path = path.replace("PyCode", "PyHelp")
if path not in sys.path: sys.path.append(path)

from ComplexServer.Plug.DB import DBHelp

CLIENTS = {}

UI = {19:20, 18:21, 15:16, 12:10}
#UI = {}

EX = set(range(39, 100))
EX.add(11)
EX = set([11, 1, 3, 4, 5, 6])
#EX = set()

OPERATE = set([41, 42, 43, 44, 45, 46])
CREATE = set([18, 21])
OK = set([13, 14])

BT = datetime.datetime(2014, 10, 30, 16, 0, 0)

class ClientState(object):
	def __init__(self, account, ip, agent):
		self.account = account
		self.ip = ip
		self.agent = agent
		self.stat_list = []
	
	def do_stat(self, stat, dt):
		if stat == 30:
			self.stat_list = [(stat, dt)]
		else:
			self.stat_list.append((stat, dt))
	
	def get_last_stat(self):
		return self.stat_list[-1][0]

	def get_s(self):
		return "".join(["-%s" % UI.get(item[0], item[0]) for item in self.stat_list if item[0] not in EX])
	
	def get_set(self):
		return set([UI.get(item[0], item[0]) for item in self.stat_list if item[0] not in EX])
	
	def get_connect_time(self):
		return (self.stat_list[-1][1] - self.stat_list[0][1]).seconds
	
	def get_ip(self):
		return self.ip
	
	def get_agent(self):
		return self.agent
	
	def has_operate(self):
		for stat, _ in self.stat_list:
			if stat in OPERATE:
				return True
		return False
	
	def has_create(self):
		for stat, _ in self.stat_list:
			if stat in CREATE:
				return True
		return False
	
	def is_ok(self):
		for stat, _ in self.stat_list:
			if stat in OK:
				return True
		return False

def get_client(account, ip, agent):
	client = CLIENTS.get(account)
	if client is None:
		CLIENTS[account] = client = ClientState(account, ip, agent)
	return client

def check_stat():
	con = DBHelp.ConnectGlobalWeb()
	
	check_sql(con, "select (status div 10) as s, count(distinct(openid)) as copenid from stat.stat where time > '%s' group by (status div 10) order by copenid;" % BT)
	check_sql(con, "select count(distinct(openid)) from stat.stat where time > '%s' and status >= 41 and status <= 46;" % BT)
	
	with con as cur:
		cur.execute("select openid, (status div 10), time, ip, agent from stat.stat where server > 300 and time > '%s';" % BT)
		for account, stat, dt, ip, agent in cur.fetchall():
			client = get_client(account, ip, agent)
			client.do_stat(stat, dt)
	print "=========================", len(CLIENTS)
	d_stat = {}
	d_stat_client = {}
	d_stat_cnt = {}
	total = 0
	for client in CLIENTS.itervalues():
		for stat in client.get_set():
			d_stat[stat] = d_stat.get(stat, 0) + 1
		
		#if client.has_operate() and (not client.has_create()):
		if not client.is_ok():
			s = client.get_s()
			d_stat_client.setdefault(s, []).append(client)
			d_stat_cnt[s] = d_stat_cnt.get(s, 0) + 1
			total += 1
	
	print_dict(d_stat)
	print "========================="
	print_dict(d_stat_cnt)
	print "=========================", len(CLIENTS), total

def check_sql(con, sql):
	print "******", sql
	with con as cur:
		cur.execute(sql)
		for row in cur.fetchall():
			for c in row:
				print c,
			print

def check_other_info(d_stat_client, k, fun_name):
	print "------------------------", k, fun_name
	l_client = d_stat_client.get(k, [])
	d_time = {}
	for client in l_client:
		info = getattr(client, fun_name)()
		d_time[info] = d_time.get(info, 0) + 1
	
	kv = d_time.items()
	kv.sort(key=lambda item:item[1])
	for k, v in kv[-20:]:
		print "*%s" % v, k

def print_dict(d):
	kv = d.items()
	kv.sort(key=lambda item:item[1])
	for k, v in kv:
		print "*%s" % v, k

if __name__ == "__main__":
	check_stat()
