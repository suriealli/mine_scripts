# -*- coding: utf-8 -*-
from Integration.WebPage.brain import db as M
def openMemory(m):
	from MySQLdb import cursors
	from ComplexServer.Plug.DB import DBHelp
	if 'cursor' in m:
		return m['cursor']

	if 'db' in m:
		t=m['db'].split(':')
		if t[0]=='role':
			t[0]='server'
			t[1]=int(t[1])/2**32
		if t[0]=='server':
			if t[1]=='all' or t[1]=='0':
				t[0]="specified"
				t[1]=DBS['total'].replace('specified:','')
			else:
				if 'prefix' in m:
					con = DBHelp.ConnectMasterDBByID(int(t[1]),m['prefix'].rstrip('_'))
				else:
					con = DBHelp.ConnectMasterDBByID(int(t[1]))
	else:
		con=DBHelp.ConnectHouTaiWeb() #
	if m.get('dict',True)==True:
		con.cursorclass = cursors.DictCursor
	return con
	
#直接查询数据库
def query(m):
	if isinstance(m,basestring):
		return query({"sql":m})
	#track
	if 'track' in m:
		print str(m['sql'])
	#query merge
	if 'merge' in m:
		return M.queryMerge(m)
	with openMemory(m) as cur:
		cur.execute(m['sql'])
		data=cur.fetchall()
	if 'one' in m: #single record
		if len(data)>0:
			return data[0]
		else:
			return False
	return data

def remoteQuery(msg=None):
	if not msg:msg={}
	mmsg={}
	mmsg['sql']=msg['sql']
	mmsg['db']="server:%s"%msg['server']
	if 'prefix' in msg:
		mmsg['prefix']=msg['prefix']
	if 'dict' in msg:
		mmsg['dict']=False
	if 'merge' in msg:
		mmsg['merge']=msg['merge']
	data=M.query(mmsg)
	return data
	
M.query=query
M.openMemory=openMemory