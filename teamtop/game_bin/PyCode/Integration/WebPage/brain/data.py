#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 数据
#===============================================================================
import time,json,traceback,collections
import me,server,tool

models={
	"connect_info":{
		"name":"连接记录表",
		"property":{
			"account":{"name":"连接帐号"},
			"connect_time":{"name":"连接时间"}
		},
		"spliter":"date(`connect_time`)"
	},
	"online_info":{
		"name":"在线信息表",
		"property":{
			"ips":{"name":"在线IP","type":"int"},
			"roles":{"name":"在线人数","type":"int"},
			"sta_time":{"name":"统计时间"}
		},
		"spliter":"date(`sta_time`)"
	},
	"role_data":{
		"name":"角色信息表",
		"property":{
			"role_id":{"name":"角色ID"},
			"connect_time":{"name":"连接时间"}
		},
		"spliter":"date(`connect_time`)"
	},
	"charge":{
		"name":"充值信息表",
		"property":{
			"account":{"name":"帐号"},
			"dt":{"name":"充值时间"}
		},
		"spliter":"date(`dt`)"
	},
}
targets={
	"account_num":{
		"name":"新帐号数",
		"table":"connect_info",
		"target":"account",
		"target_function":"count"
	},
	"apply_role_num":{
		"name":"申请创建数",
		"table":"connect_info",
		"target":"if(request_create>0,1,0)",
		"target_function":"sum"
	},
	"player_num":{
		"name":"新玩家数",
		"table":"connect_info",
		"target":"if(first_operate>0,1,0)",
		"target_function":"sum"
	},
	"pay_sum":{
		"name":"充值总额/元",
		"table":"charge",
		"target":"amt/100+pubacct_payamt_coins/10",
		"target_function":"sum"
	},
	"pay_num":{
		"name":"充值人数",
		"table":"charge",
		"target":"distinct(account)",
		"target_function":"count"
	},
	"pay_time":{
		"name":"充值次数",
		"table":"charge",
		"target":"account",
		"target_function":"count"
	},
	"max_online":{
		"name":"最大在线人数",
		"table":"online_info",
		"target":"roles",
		"target_function":"max"
	},
	"avg_online":{
		"name":"平均在线人数",
		"table":"online_info",
		"target":"roles",
		"target_function":"avg"
	},
	"min_roles":{
		"name":"最小在线人数",
		"table":"online_info",
		"target":"roles",
		"target_function":"min"
	},
	"max_ips":{
		"name":"最大在线IP",
		"table":"online_info",
		"target":"ips",
		"target_function":"max"
	},
	"avg_ips":{
		"name":"平均在线IP",
		"table":"online_info",
		"target":"ips",
		"target_function":"avg"
	},
	"min_ips":{
		"name":"最小在线IP",
		"table":"online_info",
		"target":"ips",
		"target_function":"min"
	}
}
servers_only=["max_ips","max_online","avg_online"];#not for single server
functions={
	"max":"最大值",
	"date":"日期",
	"sum":"相加",
	"count":"计数"
}

def check(S):
	data={}
	S['P']['check']=S['P'].get('check','')
	S['P']['server']=S['P'].get('server',S['A']['server'])
	S['P']['targets']=S['P'].getlist('column')
	S['P']['start_date']=S['P'].get('start_date',tool.date(time.time()-86400))
	S['P']['end_date']=S['P'].get('end_date',tool.date(time.time()-86400))
	S['P']['nogroup']=S['P'].get('nogroup','')
	S['P']['no_row_group']=S['P'].get('no_row_group','')
	S['P']['update']=S['P'].get('update',False)
	S['P']['servers']=S['P'].getlist('servers')
	
	data['servers']=server.getAll()
	data['targets']=targets
	data['functions']=functions
	data['got_targets']=json.dumps(S['P']['targets'])
	data['targets_info']=json.dumps(targets)
	
	#no target in,just return
	if len(S['P']['targets'])==0:
		data['tips']="请选择需要数据！"
		return	data
	
	if targets[S['P']['targets'][0]]['table']=='cache' and S['P']['server']=='all':
		S['P']['no_row_group']='true' #cache data need no group
	target_count=len(S['P']['targets'])
	temp=getData(S['P'])
	data['tips']='<br />'.join(temp['log'])
	#build table
	data['data']=temp['data']
	return data
	
#build table:({k:v,kk:vv},{})
def buildTable(m):
	table="<table class='p_table_order p_table'>"
	#build value
	i=0
	for k,v in m.items():
		if i==0:
			#build header
			table+="<tr>"
			for ii,jj in v.items():
				table+="<td>%s</td>"%targets.get(ii,{}).get('name',ii)
			table+="</tr>"
			i=1
			
		#build body
		table+="<tr>"
		for kk,vv in v.items():
			table+="<td>%s</td>"%vv
		table+="</tr>"
	table+="</table>"
	return table

def getData(get):
	D={}
	log=[]
	#dates
	dates=[]
	if get['nogroup']:
		dates=['%s~%s'%(get['start_date'],get['end_date'])]
	else:
		dates=tool.getDateRange(get['start_date'],get['end_date'])
	#get each target
	for v in get['targets']:
		#target_name
		name=v
		v=targets[v] #target config value
		if len(v)==0:
			continue
		target=addFunction({"type":models[v['table']]['property'].get(v['target'],{}).get('type'),"field":v['target'],"function":v['target_function']})
		#row=addFunction({"type":models[v['table']]['property'][v['row']].get('type'),"field":v['row'],"function":v['row_function']})
		#column=addFunction({"type":models[v['table']]['property'][v['column']].get('type'),"field":v['column'],"function":v['column_function']})
		#group by
		groupby=[]
		groupby_fields=[]
		#default group by date
		#condition
		condition=targets[name].get('condition','')
		#sql
		sql="select %s as %s,date_format(%s,'%%Y-%%m-%%d') as spliter from %s where %s between '%s' and '%s' %s group by spliter order by spliter asc"%(target,name,models[v['table']]['spliter'],v['table'],models[v['table']]['spliter'],get['start_date'],get['end_date'],condition)
		
		#servers
		all_server=server.getAll()
		servers=[get['server']]
		if get['server']=='5201314':
			servers=all_server.keys()
		if get['servers']:
			servers=get['servers']
		#traverse server
		if not name in D:
			D[name]=collections.OrderedDict()
			#add server
			D[name]['servers']=collections.OrderedDict()
			for sk in servers:
				if int(sk)==0:
					D[name]['servers'][sk]="全区汇总"
					continue
				D[name]['servers'][sk]=all_server.get(int(sk),{}).get('name',sk)
			#add dates
			for dk in dates:
				D[name][dk]=collections.OrderedDict()
				#all servers in this date,set default 0
				for sk in servers:
					D[name][dk][sk]=0
		for server_key in servers:
			temp={}
			temp=me.M('query',{"memory":"server:%s"%server_key,"sql":sql})
			for vv in temp:
				if get['nogroup']:
					D[name]['%s~%s'%(get['start_date'],get['end_date'])][server_key]+=vv[name]
				else:
					D[name][vv['spliter']][server_key]=vv[name]
		log.append('%s:%s'%(get['server'],sql))
	return {"data":D,"log":log}

def addFunction(m):
	if not m['function']:
		return m['field']
	if not m['type']:
		m['type']='var'
	#switch type
	if m['type']=='var':
		m['field']="%s(%s)"%(m['function'],m['field'])
	#timestamp
	elif m['type']=='timestamp':
		if m['function']=='date':
			m['field']="%s(from_unixtime(%s))"%(m['function'],m['field'])
		else:
			m['field']="%s(%s)"%(m['function'],m['field'])
	#number
	elif m['type']=='number':
		if m['function']=='sum':
			m['field']="ROUND(%s(%s),2)"%(m['function'],m['field'])
	#int
	elif m['type']=='int':
		if m['function'] in ['sum','avg','min','max']:
			m['field']="ROUND(%s(%s))"%(m['function'],m['field'])
	#distinct
	elif m['type']=='distinct':
		if m['function']=='sum' or m['function']=='count':
			m['field']="%s(distinct(%s))"%(m['function'],m['field'])
			
	return m['field']

def export(R):
	get={}
	data={}
	get['servers']=me.G(R,'servers')
	data['servers']=server.getAll()
	if get['servers']:
		get['sql']=me.G(R,'sql').strip()
		for k in get['servers']:
			cursor=me.openMemory({"memory":"server:%s"%k}).cursor()
			cursor.execute(get['sql'])
			temp=cursor.fetchall()
			import csv
			fieldnames=['ch_id','ch_role_id','ch_datetime','ch_event','ch_transaction','server']
			dict_writer = csv.DictWriter(file('base_login.csv', 'wb'),fieldnames=fieldnames)
	return data

#收集各服数据
def getAllData(S):
	if not user.inGroup(S,"operate"):return user.ban(S)
	log=[]
	log.append('#Get All Data#')
	#获取参数
	S['G']['servers']=S['G'].getlist('servers')
	S['G']['time_start']=S['G'].get('time_start','%s 00:00:00'%tool.date(time.time()))
	S['G']['time_end']=S['G'].get('time_end','%s 23:59:59'%tool.date(time.time()))
	S['G']['memory']=S['G'].get('memory',memory.DBS['total'])
	#auto update last
	S['G']['auto']=int(S['G'].get('auto'))
	if S['G']['auto']>0:
		now_time=time.time()
		S['G']['time_start']=tool.date(now_time-get['auto']*60,"%Y-%m-%d %H:%M:%S")
		S['G']['time_end']=tool.date(now_time,"%Y-%m-%d %H:%M:%S")
	#check
	S['G']['check']=S['G'].get('check','')
	S['G']['models']=S['G'].get('models','')
	log.append('$$Need Servers(%s) in (%s - %s)'%(','.join(S['G']['servers']),S['G']['time_start'],S['G']['time_end']))
	#获取所有model
	models={
		'role_data':{
			"property":['role_id','role_name','account','di32_10'],
			"spliter":'date_format(from_unixtime(`di32_10`),"%Y-%m-%d %H:%i:%s")',
			"ids":['role_id']
		},
		'charge':{
			"property":['cid','account','billno','date_format(`dt`,"%Y-%m-%d %H:%i:%s") as dt','role_id','amt','pubacct_payamt_coins'],
			"spliter":'date_format(`dt`,"%Y-%m-%d %H:%i:%s")',
			"ids":['cid']
		},
		'connect_info':{
			"property":['cid','account','first_operate','date_format(`connect_time`,"%Y-%m-%d %H:%i:%s") as connect_time','from_3','from_2','from_1','request_create'],
			"spliter":'date_format(`connect_time`,"%Y-%m-%d %H:%i:%s")',
			"ids":['cid']
		},
		'online_info':{
			"property":['date_format(`sta_time`,"%Y-%m-%d %H:%i:%s") as sta_time','ips','roles'],
			"spliter":'date_format(`sta_time`,"%Y-%m-%d %H:%i:%s")',
			"ids":['sta_time']
		}
	}
	#获取所有游戏服信息
	servers=server.getAll()
	#遍历所有服
	for k,v in servers.items():
		if S['G']['servers'] and str(k) not in S['G']['servers']:
			log.append("* %s not in [%s]"%(k,",".join(S['G']['servers'])))
			continue
		log.append('【SERVER:%s】'%k)
		#遍历所有汇总表
		for model_key,model in models.items():
			if S['G']['models'] and model_key not in S['G']['models'].split(','):
				log.append('## SKIP MODEL:%s ##'%model_key)
				continue
			log.append('== NOW MODEL:%s =='%model_key)
			filter='%s between "%s" and "%s"'%(model['spliter'],S['G']['time_start'],S['G']['time_end'])
			if not S['G']['check']:
				log.append('-- FORGET OLD DATA --')
				memory.get(S,"forget",{"memory":S['G']['memory'],"model":model_key,"filter":"%s and `server`=%s"%(filter,k)})
			
			temp=memory.get(S,"recall",{"memory":"server:%s"%k,"model":model_key,"field":'%s'%(','.join(model['property'])),"filter":filter})
			#add entity to total
			count=0
			error=[]
			exist=[]
			for entity in temp:
				count+=1
				entity['server']=k
				try:
					if S['G']['check']:
						filter={}
						for fv in model['ids']:
							filter[fv]=entity[fv]
						filter['server']=k
						if memory.get(S,"exist",{"memory":S['G']['memory'],"model":model_key,"filter":filter}):
							exist.append(str(entity[model['ids'][0]]))
							continue
					memory.get(S,"add",{"memory":S['G']['memory'],"model":model_key,"data":entity})
				except:
					error.append(str(entity[model['ids'][0]]))
					traceback.print_exc()
			if len(error)>0:
				log.append('@!ERR:%s'%(','.join(error)))
			if len(exist)>0:
				log.append('@!EXIST:%s'%(','.join(exist)))
			#log count
			log.append('#Count(%s:%s):%s'%(k,model_key,count))
	return '<br />'.join(log)