#!/usr/bin/env python
# -*- coding:UTF-8 -*-
import traceback

def add(msg={}):
	data={}
	from ServerConfig import ServerDefine_3737 as s
	cross=False
	if str(msg['zone_id'])>=60000:
		cross=True
	data['zone_id']=s.add_zone(msg['machine_ip'],msg['public_ip'],msg['public_port'],msg['mysql_ip'],msg['mysql_port'],msg['mysql_user'],msg['mysql_pwd'],cross)
	return data
	
def getAll(msg=None):
	data={}
	from Integration.Help import WorldHelp
	import collections
	for zid,zone in WorldHelp.GetZone().iteritems():
		data[zid]={}
		data[zid]['value']=zone.get_name()
		data[zid]['key']=zid
	data=collections.OrderedDict(sorted(data.items(),key = lambda t:t[0]))
	return data
def getInfo(msg=None):
	if not msg:msg={}
	data={}
	servers=getAll().keys()
	from ComplexServer.Plug.DB import DBHelp
	from Common import Serialize
	sql = "select data from sys_persistence where per_key = 'world_data';"
	
	#import datetime
	#open_time_command='''import Game.SysData.WorldData as A;pprint(A.WD)'''
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
					data[str(v)]={"open_time":kaifutime,"open_days":kaifuday,"word_level":word_level}
					
					#real open time
					# try:
						# t=sendCommand(v,open_time_command)
						#print t
						# t=eval(t)
						# data[str(v)]['real_open_time']=t[1].strftime('%Y-%m-%d %H:%M:%S')
					# except:
						# traceback.print_exc()
				except:
					traceback.print_exc()
					pass
	except:
		traceback.print_exc()
	#print data
	return data
	
def getOpenTime(msg=None):
	if not msg:msg={}
	data={}
	import datetime
	open_time_command='''import Game.SysData.WorldData as A;pprint(A.WD)'''
	#real open time
	try:
		t=sendCommand(msg['server'],open_time_command)
		#print t
		t=eval(t)
		data['open_time']=t[1].strftime('%Y-%m-%d %H:%M:%S')
	except:
		traceback.print_exc()
	return data

def getMemoryInfo(msg=None):
	if not msg:msg={}
	data={}
	from Integration.Help import WorldHelp
	zone=WorldHelp.GetZone()[int(msg['server'])]
	data['zone_id']=msg['server']
	data['zone_name']=zone.get_name()
	data['mysql_ip']=zone.master_ip
	data['mysql_port']=zone.master_port
	data['mysql_user']=zone.master_user
	data['mysql_pwd']=zone.master_pwd
	return data

def getAllMemoryInfo(msg=None):
	if not msg:msg={}
	data={}
	#主从
	if 'slave' in msg:
		from ComplexServer.Plug.DB import DBHelp
		con = DBHelp.ConnectGlobalWeb()
		with con as cur:
			cur.execute("select zid,mysql_name from zone;")
			for zid,mysql_name in cur.fetchall():
				cur.execute("select slave_ip, slave_port,slave_user,slave_pwd from mysql where name = %s;", (mysql_name))
				temp=cur.fetchall()[0]
				data[int(zid)]={'zone_id':zid,"zone_name":"","mysql_ip":temp[0],'mysql_port':temp[1],'mysql_user':temp[2],"mysql_pwd":temp[3]}
	else:
		from Integration.Help import WorldHelp
		for k,zone in WorldHelp.GetZone().items():
			k=int(k)
			data[k]={}
			data[k]['zone_id']=k
			data[k]['zone_name']=zone.get_name()
			data[k]['mysql_ip']=zone.master_ip
			data[k]['mysql_port']=zone.master_port
			data[k]['mysql_user']=zone.master_user
			data[k]['mysql_pwd']=zone.master_pwd
	return data
	
#send command to server process
def sendCommand(pkey,m):
	from Integration.Help import Concurrent
	return Concurrent.GMCommand("GHL%s"%pkey,m)
#限制登录
def limitLogin(msg=None):
	if not msg:msg={}
	data={}
	
	if 'limited' in msg:
		for v in msg['server'].split(","):
			#设置限登录状态
			from django.utils import encoding
			command='''from Game import Login;Login.LimitLogin(%s)'''%(msg['limited'])
			command=encoding.smart_str(command)
			sendCommand("%s"%v,command)
	#检查当前状态
	command='''from Game import Login;print bool(Login.LimitLoginAccount)'''
	data['limited']=sendCommand("%s"%msg['server'].split(",")[0],command).replace('\n','')
	return data
	
#设置开服时间
def setOpenTime(msg=None):
	if not msg:msg={}
	data={}
	
	if 'open_time' in msg:
		try:
			#设置限登录状态
			from django.utils import encoding
			command='''from Game.SysData import WorldData;WorldData.SetKaiFuDateTime(%s);'''%(msg['open_time'])
			if 'login_time' in msg:
				command+='''WorldData.SetEndLimitTime(%s)'''%msg['login_time'];
				
			command=encoding.smart_str(command)
			sendCommand("%s"%msg['server'],command)
			data['tips']="成功设置服[%s]开服时间为：%s[%s]"%(msg['server'],msg['open_time'],command)
		except:
			traceback.print_exc()
			data['tips']="设置服[%s]开服时间失败！"%msg['server']
	else:
		data['tips']="请提供服[%s]开服时间！"%msg['server']
	return data