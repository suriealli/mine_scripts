#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# lostnote
#===============================================================================
import traceback
import MySQLdb
from Integration import AutoHTML

#数据库
DBS={
	"total":"specified:10.190.141.7,3306,longqi,root,Nigenaocan"
	#"total":"specified:127.0.0.1,3306,longqi,root,jamesmysql1988"
}
#模型信息
models={"charge":"充值统计","dict":"字典管理","guide":"导航","user":"用户操作","role":"角色操作","server":"游戏服","machine":"设备管理","data":"数据统计"}
#权限信息
rights={
	"dict_manage":{"name":"管理字典"},
	"guide_guide":{"name":"系统首页"},
	"server_checkRegisterKeep":{"name":"查看注册留存"},
	"server_checkOnlineDuration":{"name":"总在线时长分布"},
	"server_checkLevelRange":{"name":"角色等级分布"},
	"server_list":{"name":"管理游戏服"},
	"server_checkOnline":{"name":"在线人数统计"},
	"server_checkRoll":{"name":"查看滚服数据"},
	"server_sendNotice":{"name":"发送公告"},
	"server_listNotice":{"name":"查看历史公告"},
	"user_add":{"name":"增加用户"},
	"user_editPassword":{"name":"更改密码"},
	"user_list":{"name":"管理用户"},
	"user_log":{"name":"用户操作日志"},
	"machine_ShowFile":{"name":"日志文件"},
	"machine_syncClient":{"name":"同步客户端"},
	"machine_changeClientLocation":{"name":"切换客户端资源路径"}
}
#组权限
permissions={
	"public":["user_login","user_exit","tool_drawCode"],
	"common":["guide_guide","user_editPassword"],
	"operate":['server_listNotice','server_sendNotice','server_checkOnline','server_checkOnlineDuration','server_checkLevelRange','server_checkRegisterKeep','server_checkRoll',"machine_changeClientLocation"],
	"develop":['dict_manage',"machine_ShowFile"],
	"design":['server_checkOnline','server_checkOnlineDuration','server_checkLevelRange','server_checkRegisterKeep'],
	"host":["user_add","user_list","user_edit","user_log"]
}
#获取请求开始处理
def get(R):
	import os,sys
	sys.path.insert(0,os.path.dirname(__file__)) #root path
	m=getPath(R.META['PATH_INFO'])
	#session
	R.session.set_expiry(0)
	R.session['ME']=os.path.dirname(os.path.dirname(__file__))
	R.session['model']=m['model']
	R.session['action']=m['action']
	
	#get data
	data={}
	#check permission
	if checkPermission(R):#通过权限检验
		try:
			model=review(m['model'])
			action=getattr(model,m['action'])
			data=action(R)
			if not data:
				data={}
		except:
			traceback.print_exc()
			pass
	else:
		R.session['before_login']="/model"
		data={"url":"/model/user/login"}
	if 'url' in data: #仅作重定向
		from django.http import HttpResponseRedirect
		return HttpResponseRedirect(data['url'])
	if 'response' in data: #仅供输出
		from django.http import HttpResponse
		return HttpResponse(data['response'])
	if 'return' in data: #仅供输出
		if 'type' in data:
			from django.http import HttpResponse
			return HttpResponse(data['return'],data['type'])
		return data['return']
	#add meta info
	data['action']=m['action']
	data['model']=m['model']
	#增加翻译词典
	
	if 'lang' in R.GET:
		R.session['lang']=R.GET['lang']
	if 'lang' not in R.session:
		R.session['lang']=='zh_cn'
	data['S']=R.session
	data['dict']=review('words').get(R.session.get('lang','zh_cn'))
	from django.shortcuts import render_to_response
	return render_to_response(m['model']+".htm",data)
def say(R,msg):
	import words
	data=words.check(msg,R.session.get('lang','zh_cn'))
	return data
#获取权限列表
def getRights(R):
	data={}
	groups=R.session['permission']
	if 'public' in groups:
		groups.remove('public')
	groups.append('public')
	if 'common' in groups:
		groups.remove('common')
	groups.append('common')
	temp=[]
	for k,v in permissions.items():
		if k in groups:
			temp+=v
	for v in temp:
		if v in rights:
			data[v]=rights[v]
	return data

#get param: R,param key,param format
def G(R,key,format="string"):
	data=""
	if format=="string":
		data=AutoHTML.AsString(R.POST,key)
		if not data:
			data=AutoHTML.AsString(R.GET,key)
	elif format=="int":
		data=AutoHTML.AsInt(R.POST,key)
		if not data:
			data=AutoHTML.AsInt(R.GET,key)
	elif format=="list":
		data=AutoHTML.AsList(R.POST,key)
		if not data:
			data=AutoHTML.AsList(R.GET,key)
	return data
	
#检查权限
def checkPermission(R):
	#if local machine
	if 'key' in R.GET and R.GET['key']=="lostnote":
		if R.META['REMOTE_ADDR']=='127.0.0.1' and R.session['action'] in ['loopNotice','manageAllData']:
			return True
		else:
			print R.META['REMOTE_ADDR'],R.META['HTTP_HOST']
	#public rights
	if R.session['model']+'_'+R.session['action'] in permissions.get('public',[]):
		return True
	#not login
	if 'user' not in R.session or 'permission' not in R.session:
		return False
	else:
		#public rights
		if R.session['model']+'_'+R.session['action'] in permissions.get('common',[]):
			return True
		hasPermission=False
		for v in R.session['permission']:
			if R.session['model']+'_'+R.session['action'] in permissions.get(v,[]):
				hasPermission=True
				break
		return hasPermission

def openMemory(m):
	from MySQLdb import cursors
	from ComplexServer.Plug.DB import DBHelp
	if 'cursor' in m:
		return m['cursor']

	if 'memory' in m:
		memory=m['memory'].split(':')
		if memory[0]=='server':
			if memory[1]=='all' or memory[1]=='0':
				memory[0]="specified"
				memory[1]=DBS['total'].replace('specified:','')
			else:
				con = DBHelp.ConnectMasterDBByID(int(memory[1]))
		if memory[0]=='role':
			con = DBHelp.ConnectMasterDBRoleID(int(memory[1]))
		if memory[0]=='global':
			con=DBHelp.ConnectGlobalWeb()
		if memory[0]=='specified':
			config=memory[1].split(',')
			con=MySQLdb.connect(port=int(config[1]),host=config[0],user=config[3],passwd=config[4],db=config[2])
	else:
		con=DBHelp.ConnectHouTaiWeb() #
	if m.get('dict',True)==True:
		con.cursorclass = cursors.DictCursor
	return con
	
#调用数据库记忆体
def M(act,msg):
	data={}
	action=globals().get(act)
	data=action(msg)
	return data
#forget
def forget(m):
	data={}
	filter=setFilter(m['filter'])
	if filter=='':
		return false
	sql='delete from `%s` %s' % (m['model'],filter)
	if 'track' in m:
		print sql
	checkMemory(m)
	with openMemory(m) as conn:
		data=conn.execute(sql)
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
	sql='INSERT INTO `%s` (`%s`) VALUES (%s)' % (m['model'],'`, `'.join(keys),','.join(values))
	if 'track' in m:
		print sql
		return
	checkMemory(m)
	with openMemory(m) as conn:
		conn.execute(sql)
	return True

def exist(m):
	m.update({"one":True})
	data=recall(m)
	if data:
		return True
	return False
#编辑更新数据
def edit(m):
	where=setFilter(m['filter'])
	sql = 'update `%s` set ' % (m['model'])
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
		with openMemory(m) as conn:
			conn.execute(sql)
		result={'filter':filter}
	except:
		traceback.print_exc()
	return result

#防止误写入游戏服
def checkMemory(m):
	if 'memory' in m:
		temp=m['memory'].split(':')[0]
		if temp in ['server','role']:
			if 'from' not in m or m['from']!='lostnote':
				print "ERROR:please do not write to server database"
				exit()
#查询数据
def recall(m):
	m['field']=m.get('field','*')
	m['filter']=setFilter(m.get('filter',''))
	m['range']=setRange(m.get('range',''))
	m['option']=setOption(m.get('option',{}))
	#model
	sql="select %s from `%s` %s" % (m['field'],m['model'],m['filter']+m['option']+m['range'])
	#track
	if 'track' in m:
		print str(sql)
		
	with openMemory(m) as cur:
		cur.execute(sql)
		data=cur.fetchall()
		
	if 'one' in m: #single record
		if len(data)>0:
			return data[0]
		else:
			return False
	return data

#直接查询数据库
def query(m):
	if isinstance(m,basestring):
		return query({"sql":m})
	#track
	if 'track' in m:
		print str(m['sql'])
		
	with openMemory(m) as cur:
		cur.execute(m['sql'])
		data=cur.fetchall()
		
	if 'one' in m: #single record
		if len(data)>0:
			return data[0]
		else:
			return False
	return data

#持久化数据到数据库
def remember(m):
	if 'server' in m or 'role' in m: #禁止后台修改游戏服数据
		return False
	action=m.get('action','add')
	action=globals().get(action)
	return action(m)

#载入模型
def review(model):
	#get model
	import importlib
	model=importlib.import_module(model)
	return model

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
		filter=' where '+filter.rstrip(' and')
	return filter

#生成数据库额外信息查询语句
def setOption(m):
	if not m:
		return ''
	option=''
	for k,v in m.items():
		if k=='order':
			temp=v.split(',')
			option+=' order by `%s` %s'%(temp[0].replace('|','`,`'),temp[1])
		if k=='group':
			option+=' group by %s'%v
	return option

#生成数据库分页查询语句
def setRange(m):
	if m=='':
		return m
	m=m.split(',')
	page=m[0]
	page_size=m[1]
	return ' limit '+str((int(page)-1)*int(page_size))+','+page_size

#获取分页信息
def getRange(R,m={}):
	#if is a instant scent render with javascript
	m['render']=' href="'
	#get now range
	size=m.get('size','10')
	m['range']=R.GET.get('range','1,'+size)
	msg_path=''
	if 'msg' in m:
		for k,v in m['msg'].items():
			msg_path+='&'+k+'='+v
	m['render']=m['render']+m['url']
	#get model count
	msg={'one':True,'model':m['model'],'field':'count(*) as count'}
	if 'memory' in m:
		msg['memory']=m['memory']
	if 'filter' in m:
		msg['filter']=m['filter']
	if 'option' in m:
		msg['option']=m['option']
	m['count']=M('recall',msg)
	m['count']=m['count']['count']
	#if count 0
	if m['count']==0:
		return {"html":'<div id="range" class="warm">'+"没有数据!"+'</div>',"range":m['range']}
	Range=m['range'].split(',')
	page_size=int(Range[1])
	page=int(Range[0])
	import math
	page_count=int(math.ceil(float(m['count'])/page_size))
	if page_count==0:
		page_count=1
	pre_page=page-1
	if pre_page<1:
		pre_page=1
	next_page=page+1
	if next_page>page_count:
		next_page=page_count
	start_page=page-5
	if start_page<1:
		start_page=1
	end_page=page+5
	if end_page>page_count:
		end_page=page_count
	color=''
	active=''
	range_html='%s %s &nbsp<a %s?range=1,%s%s">%s</a>&nbsp<a %s?range=%s,%s%s">%s</a>&nbsp' % ('总页数',page_count,m['render'],page_size,msg_path,'首页',m['render'],pre_page,page_size,msg_path,'上页')
	start_list_page=1
	if page>1 and (page-5)>0:
		start_list_page=page-5
	end_list_page=start_list_page+9
	if page_count<end_list_page:
		end_list_page=page_count
	for i in range(start_list_page,end_list_page+1):
		color=''
		active=''
		#active
		if i==page:
			color='red'
			active='class="active"'
		range_html+='<a %s style="color:%s" %s?range=%s,%s%s">%s</a>&nbsp' % (active,color,m['render'],i,page_size,msg_path,i)
	range_html+='<a %s?range=%s,%s%s">%s</a>&nbsp<a %s?range=%s,%s%s">%s</a>&nbsp' % (m['render'],next_page,page_size,msg_path,'下页',m['render'],page_count,page_size,msg_path,'末页')
	return {"html":'<div id="range">%s</div>' % range_html,"range":m['range']}

#获取模型与行为
def getPath(url):
	m={}
	url=url.split('/')[1:4]
	#不是我开发的
	if url[0]!='model':
		return {"model":"unknown"}
	m['model']='guide'
	m['action']='guide'
	if len(url)>1:
		m['model']=url[1]
	if len(url)>2:
		m['action']=url[2]
	return m
#get function URL
def getURL(fun):
	return AutoHTML.GetURL(fun)