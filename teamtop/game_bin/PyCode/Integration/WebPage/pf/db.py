#!/usr/bin/env python
# -*- coding:UTF-8 -*-

# 获取系统数据库连接
def link(c):
	from MySQLdb import cursors
	from ComplexServer.Plug.DB import DBHelp
	if 'cursor' in c:
		return c['cursor']

	if 'db' in c:
		t = c['db'].split(':')
		if t[0] == 'role':
			t[0] = 'server'
			t[1] = int(t[1])/2**32
		if t[0] == 'server':
			if 'prefix' in c:
				con = DBHelp.ConnectMasterDBByID(int(t[1]), c['prefix'].rstrip('_'))
			else:
				con = DBHelp.ConnectMasterDBByID(int(t[1]))
	else:
		con = DBHelp.ConnectHouTaiWeb()

	if c.get('dict', True) == True:
		con.cursorclass = cursors.DictCursor
	return con

# 直接查询数据库
def query(c):
	if isinstance(c, basestring):
		return query({"sql": c})

	#track
	if 'track' in c:
		print str(c['sql'])

	#query merge
	if 'merge' in c:
		return queryMerge(c)

	con = link(c)
	with link(c) as cur:
		cur.execute(c['sql'])
		data = cur.fetchall()
	con.close()

	if 'one' in c: #single record
		if len(data) > 0:
			return data[0]
		else:
			return False
	return data

def remoteQuery(c=None):
	if not c:
		return ()
	data = ()
	cc = {}

	# 获取查询参数
	for v in ["prefix", "merge", "sql"]:
		if v in c:
			cc[v] = c[v]
	if 'dict' in c:
		cc['dict'] = False
	# 单服数据查询
	if c['server'] != 'all':
		cc['db'] = "server:%s" % c['server']
		data = query(cc)

	# 全服数据查询
	else:
		data = []
		import server
		servers = server.getAll().keys()
		for v in servers:
			cc['db'] = "server:%s" % v
			t = query(cc)
			for vv in t:
				data.append(vv)
	return data

def queryMerge(c):
	merge = c['merge']
	del c['merge']
	con = link(c)
	import MySQLdb
	con.cursorclass = MySQLdb.cursors.Cursor
	with con as cur:
		cur.execute("SHOW TABLES like '%s%%'" % (merge))
		tables = cur.fetchall()
	con.close()
	# query in all tables
	data = []
	import copy
	for table in tables:
		print "Now merge table:",table
		cc = copy.deepcopy(c)
		cc['sql'] = cc['sql'].replace("{table_field}", table[0])
		t = query(cc)
		for v in t:
			data.append(v)
		del t
	return data

def mergeQuery(c):
	sql = "SHOW TABLES where Tables_in_%s like '%s%%'" % (c['db']['name'], c['app'])
	#splitted apps
	apps = query({"sql": sql, "db": c['db']})
	merged_apps = []
	for v in apps: #get apps in range
		sql = "select date_format(min(%s),'%%Y-%%m-%%d %%H:%%i:%%s') as min,date_format(max(%s),'%%Y-%%m-%%d %%H:%%i:%%s') as max from %s" % (
			c['spliter'],
			c['spliter'],
			v['Tables_in_%s' % (c['db']['name'])]
		)
		result = query({"one": True, "sql": sql, "db": c['db']})
		if result['min']:
			if c['spliter_start'] > result['max'] or c['spliter_end'] < result['min']:
				continue
			else:
				merged_apps.append("%s" % v['Tables_in_%s' % c['db']['name']])
	data = []
	if len(merged_apps) > 0:#get data
		spliter_condition = "%s between '%s' and '%s'"%(c['spliter'],c['spliter_start'],c['spliter_end'])
		for v in merged_apps:
			now_app = v
			sql = c['sql'] % (now_app, spliter_condition)
			#track sql
			cc = {"sql": sql, "db": c["db"]}
			if "key" in c:
				cc['key'] = c['key']
			data = query(cc)
	return data