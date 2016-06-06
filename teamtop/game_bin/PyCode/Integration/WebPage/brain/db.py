# -*- coding: utf-8 -*-
import MySQLdb,traceback
import me
links_count=0
def openMemory(m):
	if 'cursor' in m:
		return m['cursor']

	#db info
	db_info={}
	if 'db' in m:
		if isinstance(m['db'],dict):
			db_info=m['db']
		else:
			import server,role
			t=m['db'].split(':')
			if t[0]=='server':
				if t[1]=='all' or t[1]=='0':
					t[0]="specified"
					from heart import db as heart_db
					t[1]=heart_db.DBS['total'].replace('specified:','')
				else:
					#get server db info
					db_info=server.getMemoryInfo(int(t[1]),m.get('prefix_type','data'),m.get('slave',False))
			if t[0]=='role':
				db_info=server.getMemoryInfo(role.getServerID(int(t[1])))
			if t[0]=='specified':
				config=t[1].split(',')
				db_info={"host":config[0],"port":int(config[1]),"name":config[2],"user":config[3],"key":config[4]}
	else:
		#default db houtai
		from heart import db as heart_db
		db_info=heart_db.info
	#connect
	con=MySQLdb.connect(port=db_info['port'],host=db_info['host'],user=db_info['user'],passwd=db_info['key'],db=db_info['name'],charset="utf8")
	
	if m.get('dict',True)==True:
		con.cursorclass = MySQLdb.cursors.DictCursor
	count(1)
	return con
	
#调用数据库记忆体
def get(act,msg):
	data={}
	action=globals().get(act)
	data=action(msg)
	return data
def getParallel(msg):
	msg[1]['slave']=True
	return get(msg[0],msg[1])
#forget
def forget(m):
	data={}
	filter=setFilter(m['filter'])
	if filter=='':
		return false
	sql='delete from `%s` %s' % (m['app'],filter)
	if 'track' in m:
		print sql
	checkMemory(m)
	link=openMemory(m)
	with link as conn:
		data=conn.execute(sql)
	close(link)
	return data
	
#增加数据
def add(m):
	#create sql and insert
	keys=[]
	values=[]
	for k,v in m['data'].items():
		keys.append(k)
		if isinstance(v,basestring):
			values.append('"%s"' % MySQLdb.escape_string(v))
		else:
			values.append(str(v))
	sql='INSERT INTO `%s` (`%s`) VALUES (%s)' % (m['app'],'`, `'.join(keys),','.join(values))
	if 'track' in m:
		print sql
		return
	checkMemory(m)
	insert_id=0
	link=openMemory(m)
	with link as conn:
		conn.execute(sql)
		insert_id=conn.lastrowid
	close(link)
	return insert_id

def exist(m):
	m.update({"one":True})
	data=recall(m)
	if data:
		return True
	return False
#编辑更新数据
def edit(m):
	where=setFilter(m['filter'])
	sql = 'update `%s` set ' % (m['app'])
	for key,value in m['data'].items():
		if isinstance(value,basestring):
			value='"%s"' % MySQLdb.escape_string(value)
		sql+=' `%s`=%s,' % (key,value)
	sql=sql.strip(',')
	sql+=where
	if 'track' in m:
		print str(sql)
	result=False
	checkMemory(m)
	try:
		link=openMemory(m)
		with link as conn:
			conn.execute(sql)
		close(link)
		result={'filter':filter}
	except:
		traceback.print_exc()
	return result

#防止误写入游戏服
def checkMemory(m):
	if 'db' in m:
		temp=m['db'].split(':')[0]
		if temp in ['server','role']:
			if 'from' not in m or m['from']!='lostnote':
				print "ERROR:please do not write to server database"
				exit()
#查询数据
def recall(m):
	field=m.get('field','*')
	filter=setFilter(m.get('filter',''))
	range=setRange(m.get('range',''))
	option=setOption(m.get('option',{}))
	#app
	sql="select %s from `%s` %s" % (field,m['app'],filter+option+range)
	#join
	if "join" in m:
		sql=join(sql,m['join'])
	#track
	if 'track' in m and m['track']==True:
		print str(sql)
		
	#remote query
	remote=inRemoteServer(m)
	if not remote:
		link=openMemory(m)
		with link as cur:
			cur.execute(sql)
			data=list(cur.fetchall())
		close(link)
	else:
		remote['sql']=sql
		try:
			data=list(me.post("db/remoteQuery",remote))
			if isinstance(data,dict) and 'tips' in data:
				data=[]
		except:
			data=[]
			print "remoteQuery Error:",remote
			traceback.print_exc()
			pass
		
	if 'one' in m: #single record
		if len(data)>0:
			return data[0]
		else:
			return False
	#has key
	if 'key' in m:
		import collections
		temp=collections.OrderedDict()
		for v in data:
			temp[v[m['key']]]=v
		data=temp
		#track
	if 'track' in m and m['track']=="return":
		return data,sql
	return data
#远程查询
def inRemoteServer(m):
	data=None
	if 'db' in m:
		#default db houtai
		local_operator=[]
		try:
			from heart import db as heart_db
			local_operator=heart_db.local_operator
		except:
			pass
		if int(me.S['A']["operator"]) not in local_operator:
			if isinstance(m['db'],dict):
				return data
			data={}
			temp=m['db'].split(':')
			if temp[0]=="server":
				data['server']=temp[1]
			if temp[0]=='role':
				import role
				data['server']=role.getServerID(int(temp[1]))
			if 'prefix_type' in m:
				import server
				data["prefix"]=server.getMemoryPrefix(m['prefix_type'])
			if 'dict' in m:
				data['dict']=m['dict']
			if 'merge' in m:
				data['merge']=m['merge']
	return data

#直接查询数据库
def query(m):
	if isinstance(m,basestring):
		return query({"sql":m})

	#track
	if 'track' in m:
		print str(m['sql'])
	#remote query
	remote=inRemoteServer(m)
	if not remote:
		#query merge
		if 'merge' in m:
			return queryMerge(m)
		link=openMemory(m)
		with link as cur:
			cur.execute(m['sql'])
			data=cur.fetchall()
		close(link)
	else:
		remote['sql']=m['sql']
		try:
			data=me.post("db/remoteQuery",remote)
			if isinstance(data,dict) and 'tips' in data:
				data=()
		except:
			print "remoteQuery Error:",remote
			data=()
			traceback.print_exc()
			pass
		
	if 'one' in m: #single record
		if len(data)>0:
			return data[0]
		else:
			return False
	return data

def queryMerge(msg):
	merge=msg['merge']
	del msg['merge']
	link=openMemory(msg)
	link.cursorclass = MySQLdb.cursors.Cursor
	with link as cur:
		cur.execute("SHOW TABLES like '%s%%'"%(merge))
		tables=cur.fetchall()
	close(link)
	#query in all tables
	data=[]
	import tool
	for table in tables:
		print "Now merge table:",table
		mmsg=tool.copy(msg)
		mmsg['sql']=mmsg['sql'].replace("{table_field}",table[0])
		t=query(mmsg)
		for v in t:
			data.append(v)
		del t
	return data

def mergeQuery(msg):
	sql="SHOW TABLES where Tables_in_%s like '%s%%'"%(msg['db']['name'],msg['app'])
	#splitted apps
	apps=query({"sql":sql,"db":msg['db']})
	merged_apps=[]
	for v in apps:#get apps in range
		sql="select date_format(min(%s),'%%Y-%%m-%%d %%H:%%i:%%s') as min,date_format(max(%s),'%%Y-%%m-%%d %%H:%%i:%%s') as max from %s"%(msg['spliter'],msg['spliter'],v['Tables_in_%s'%(msg['db']['name'])])
		#track sql
		if msg.get('track')=='sql':print(sql)
		result=query({"one":True,"sql":sql,"db":msg['db']})
		if msg.get('track')=='app_spliter':print(result)
		if result['min']:
			if msg.get('track')=='compare':print("%s>%s||%s<%s"%(msg['spliter_start'],result['max'],msg['spliter_end'],result['min']))
			if msg['spliter_start']>result['max'] or msg['spliter_end']<result['min']:
				continue
			else:
				merged_apps.append("%s"%v['Tables_in_%s'%msg['db']['name']])
	if msg.get('track')=='apps':print(merged_apps)
	#just need tables
	if msg.get('need')=='apps':
	    return merged_apps
	data=[]
	if len(merged_apps)>0:#get data
		spliter_condition="%s between '%s' and '%s'"%(msg['spliter'],msg['spliter_start'],msg['spliter_end'])
		for v in merged_apps:
			now_app=v
			sql=msg['sql']%(now_app,spliter_condition)
			#track sql
			if msg.get('track')=='sql':print(sql)
			mmsg={"sql":sql,"db":msg["db"]}
			if "key" in msg:
				mmsg['key']=msg['key']
			data=query(mmsg)
	if msg.get('track')=='result':print(data);exit()
	return data
#持久化数据到数据库
def remember(m):
	if 'server' in m or 'role' in m: #禁止后台修改游戏服数据
		return False
	action=m.get('action','add')
	action=globals().get(action)
	return action(m)
#{"join":{"key":"user-id","field":"name"}}
def join(sql,m):
	data=""
	if isinstance(m,list):
		data=sql
		for v in m:
			data=join(data,v)
		return data
	byname=m["app"]
	#byname
	if 'byname' in m:
		byname=m['byname']
	#join
	keys=m['key'].split('-')
	if len(keys)==1:
		keys=[keys[0],keys[0]]
	data="select a.*,%s from (%s) as a %s join %s as %s on a.%s=%s.%s"%(m['field'],sql,m.get("mode",'left'),m['app'],byname,keys[0],byname,keys[1])
	option=''
	if 'option' in m:
		option=setOption(m['option'])
	data+=option
	return data

#生成数据库条件限制语句
def setFilter(m):
	filter=''
	#if string return
	if isinstance(m,basestring):
		filter=m
	else:
		#if operator set
		operator=''
		if 'operator' in m: #operator
			operator=m['operator']
			del m['operator']
		if 'byname' in m and str(m['byname']).isdigit(): #id
			m['id']=m['byname']
			del m['byname']
		#add like
		if 'like' in m:
			for k,v in m['like'].items():
				if v!=None:
					filter+="`"+k+"` like '%"+v+"%' and "
			del m['like']
		#other filter
		if m:
			for k,v in m.items():
				sign='='
				if k in operator:
					sign=operator[k]
				if not str(v).isdigit():
					v='"'+v+'"'
				filter+='`'+k+'`'+sign+str(v)+' and '
	if filter!='':
		filter=' where '+filter.replace(' where ','').rstrip(' and')
	return filter

#生成数据库额外信息查询语句
def setOption(m):
	if isinstance(m,basestring):
		return m
	if not m:
		return ''
	option=''
	for k,v in m.items():
		if k=='order' and v!="":
			temp=v.split(',')
			option+=' order by `%s` %s'%(temp[0].replace('|','`,`'),temp[1])
		if k=='group' and v!="":
			option+=' group by %s'%v
	return option

#生成数据库分页查询语句
def setRange(m):
	if m=='':
		return m
	m=m.split(',')
	if len(m)==1:
		return " limit %s"%m[0]
	page=m[0]
	page_size=m[1]
	if int(page)>1:
		return ' limit '+str((int(page)-1)*int(page_size))+','+page_size
	else:
		return ' limit 0,'+page_size
def writeProtect(sql):
	keys=['UPDATE','INSERT','DROP','ALTER']
	for v in keys:
		try:
			idx=sql.upper().index(v)
			sql=""
		except:
			traceback.print_exc()
	return sql
def close(msg):
	count(-1)
	msg.close()

def count(msg=None):
	global links_count
	if not msg:return links_count
	links_count+=msg
	
def connect(m):
	#connect
	conn=MySQLdb.connect(host=m['host'],user=m['user'],passwd=m['key'],db=m['name'],charset="utf8")
	return conn,conn.cursor()