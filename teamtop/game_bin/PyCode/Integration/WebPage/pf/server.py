#!/usr/bin/env python
# -*- coding:UTF-8 -*-
import traceback

def getAll(c=None):
	data = {}
	from Integration.Help import WorldHelp
	import collections
	for zid,zone in WorldHelp.GetZone().iteritems():
		data[zid] = {}
		data[zid]['value'] = zone.get_name()
		data[zid]['key'] = zid
	data = collections.OrderedDict(sorted(data.items(), key = lambda t:t[0]))
	return data

def getInfo(c=None):
	if not c:
		c = {}
	data = {}
	servers = getAll().keys()
	from ComplexServer.Plug.DB import DBHelp
	from Common import Serialize
	sql = "select data from sys_persistence where per_key = 'world_data';"
	
	try:
		for v in servers:
			con = DBHelp.ConnectMasterDBByID(v)
			with con as cur:
				cur.execute(sql)
				result = cur.fetchall()
				if not result:
					continue
				try:
					worlddata = Serialize.String2PyObj(result[0][0])
					kaifutime = worlddata.get(1).strftime('%Y-%m-%d %H:%M:%S')
					kaifuday = worlddata.get(6)
					word_level = worlddata.get(2)
					data[str(v)] = {
						"open_time": kaifutime,
						"open_days": kaifuday,
						"word_level": word_level
					}
				except:
					traceback.print_exc()
					pass
	except:
		traceback.print_exc()
	#print data
	return data
	
def getOpenTime(c=None):
	if not c:
		c = {}
	data = {}
	import datetime
	open_time_command = '''import Game.SysData.WorldData as A;pprint(A.WD)'''
	#real open time
	try:
		t = sendCommand(c['server'], open_time_command)
		#print t
		t = eval(t)
		data['open_time'] = t[1].strftime('%Y-%m-%d %H:%M:%S')
	except:
		traceback.print_exc()
	return data

def getMemoryInfo(c=None):
	if not c:c = {}
	data = {}
	from Integration.Help import WorldHelp
	zone = WorldHelp.GetZone()[int(c['server'])]
	data['zone_id'] = c['server']
	data['zone_name'] = zone.get_name()
	data['mysql_ip'] = zone.master_ip
	data['mysql_port'] = zone.master_port
	data['mysql_user'] = zone.master_user
	data['mysql_pwd'] = zone.master_pwd
	return data

def getAllMemoryInfo(c=None):
	if not c:c = {}
	data = {}
	#主从
	if 'slave' in c:
		from ComplexServer.Plug.DB import DBHelp
		con = DBHelp.ConnectGlobalWeb()
		with con as cur:
			cur.execute("select zid,mysql_name from zone;")
			for zid,mysql_name in cur.fetchall():
				cur.execute("select slave_ip, slave_port,slave_user,slave_pwd from mysql where name = %s;", (mysql_name))
				temp = cur.fetchall()[0]
				data[int(zid)] = {
					'zone_id': zid,
					"zone_name": "",
					"mysql_ip": temp[0],
					'mysql_port': temp[1],
					'mysql_user': temp[2],
					"mysql_pwd": temp[3]
				}
	else:
		from Integration.Help import WorldHelp
		for k,zone in WorldHelp.GetZone().items():
			k = int(k)
			data[k] = {}
			data[k]['zone_id'] = k
			data[k]['zone_name'] = zone.get_name()
			data[k]['mysql_ip'] = zone.master_ip
			data[k]['mysql_port'] = zone.master_port
			data[k]['mysql_user'] = zone.master_user
			data[k]['mysql_pwd'] = zone.master_pwd
	return data
	
#send command to server process
def sendCommand(pkey,m):
	from Integration.Help import Concurrent
	return Concurrent.GMCommand("GHL%s" % pkey, m)

#限制登录
def limitLogin(c):
	data = {}
	if 'limited' in c:
		for v in c['server'].split(","):
			#设置限登录状态
			from django.utils import encoding
			command = '''from Game import Login;Login.LimitLogin(%s)'''%(c['limited'])
			command = encoding.smart_str(command)
			sendCommand("%s"%v, command)
	#检查当前状态
	command = '''from Game import Login;print bool(Login.LimitLoginAccount)'''
	data['limited'] = sendCommand("%s"%c['server'].split(",")[0], command).replace('\n', '')
	return data
	
#设置开服时间
def setOpenTime(c):
	data = {}
	if 'open_time' in c:
		try:
			#设置限登录状态
			from django.utils import encoding
			command = '''from Game.SysData import WorldData;WorldData.SetKaiFuDateTime(%s);'''%(c['open_time'])

			# 若明确了开放普通号登录的时间
			if 'login_time' in c:
				command += '''WorldData.SetEndLimitTime(%s);'''%c['login_time'];
			# 否则，马上开放
			else:
				command += '''from Game import Login;Login.LimitLogin(False)'''
				
			command = encoding.smart_str(command)
			sendCommand("%s"%c['server'], command)
			data['tips'] = "成功设置服[%s]开服时间为：%s[%s]"%(c['server'], c['open_time'], command)
		except:
			traceback.print_exc()
			data['tips'] = "设置服[%s]开服时间失败！"%c['server']
	else:
		data['tips'] = "请提供服[%s]开服时间！"%c['server']
	return data