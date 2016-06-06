#!/usr/bin/env python
# -*- coding:UTF-8 -*-
import traceback,time
import me,server,tool,memory,user,model,body,cache
#check role info
def check():
	data={}
	if not user.inGroup("operate"):return user.ban()
	me.S['G']['id_type']=me.S['G'].get("id_type","role_id")
	me.S['G']['id']=me.S['G'].get("id","")
	me.S['G']['server']=me.S['G'].get('server')
	me.S['G']['check_all']=me.S['G'].get("check_all","")
	if me.S['G']['id']:
		role_id=me.S['G']['id']
		if me.S['G']['id_type']!='role_id':
			role_id=getID({"from":me.S['G']['id_type'],"id":me.S['G']['id'],"server":me.S['G']["server"]})
		elif not role_id.isdigit():
			data['tips']="角色ID必须为数字！"
			return data
		if not role_id:
			data['tips']="角色ID不存在！"
		else:
			role_ids=[role_id]
			if me.S['G']['check_all']!="":
				role_ids=getAllID(role_id)
			#field
			field=["id","account","name","level","cash","money","create_time","time_total_online","tile_last_login","vip","ban_speak","ban_login","charge","role_union","role_fight"]
			fields=[]
			for v in field:
				if v in model.info('role')['map']:
					fields.append("%s as %s"%(model.info('role')['map'][v]['field'],v))
			data['data']={}
			#each role
			msg={
				"one":True,
				"model":model.info('role')['name'],
				"field":",".join(fields),
				"memory":"",
				"filter":{}
			}
			for v in role_ids:
				msg["memory"]="server:%s"%(getServerID(v))
				msg["filter"]={
					model.info('role')['map']['id']['field']:v
				}
				temp=memory.get("recall",msg)
				if temp and "id" in temp:
					if temp['id'] not in data['data']:
						data['data'][temp['id']]=tool.Dict([])
					data['data'][temp['id']]=temp
		if len(data['data'])==0:
			data["tips"]="没有找到匹配的角色！"
	data['servers']=server.getAll()
	return data
#longqi
def checkActive():
	if not user.inGroup("operate"):return user.ban()
	data={}
	#特定时间范围
	me.S['P']['date_start']=me.S['P'].get('date_start',tool.date(body.now()))
	me.S['P']['date_end']=me.S['P'].get('date_end',tool.date(body.now()))
	me.S['P']['level_start']=me.S['P'].get('level_start',0)
	me.S['P']['level_end']=me.S['P'].get('level_end',1000)
	me.S['P']['all']=me.S['P'].get('all','')
	sql='select count(*) as count,login.date as date from (select account,date_format(login_day,"%%Y-%%m-%%d") as date from login_info where date(login_day) between "%s" and "%s" group by account,date) as login inner join role_data as role on login.account=role.account and role.di32_11 between %s and %s group by date order by date asc'%(
		me.S['P']['date_start'],
		me.S['P']['date_end'],
		me.S['P']['level_start'],
		me.S['P']['level_end']
	)
	#single server
	if me.S['P']['all']=="":
		data["data"]=memory.get("query",{"sql":sql,"memory":"server:%s"%(me.S['A']['server'])})
	else:
		dates=tool.getDateRange(me.S['P']['date_start'],me.S['P']['date_end'])
		data['data']=tool.Dict()
		t=server.queryInAll({"sql":sql})
		for v in dates:
			data['data'][v]={"date":v,"count":0}
		for v in t:
			data['data'][v['date']]['count']+=v['count']
		data['data']=data['data'].values()
	return data
	
#包数据范围
def checkPackInfoRange():
	import tool
	if not user.inGroup("operate"):return user.ban()
	data={}
	me.S['P']['pack']=me.S['P'].get('pack','')
	me.S['P']['pack_index']=me.S['P'].get('pack_index',"i32")
	me.S['P']['index']=me.S['P'].get('index',0)
	me.S['P']['range']=me.S['P'].get('range','')
	if me.S['P']['range']=='':me.S['P']['range']='31,51,71,91,101'
	me.S['P']['all']=me.S['P'].get('all','')
	me.S['P']['export']=me.S['P'].get('export','')
	if me.S['P']['pack']!='':
		msg={
			"model":model.info('role')["name"],
			"field":"%s"%(me.S['P']['pack'])
		}
		#export role_id
		if me.S['P']['export']!="":
			msg['field']="role_id,%s"%msg['field']
		if me.S['P']['all']=='':
			msg.update({"memory":"server:%s"%(me.S['A']['server'])})
			temp=memory.get('recall',msg)
		else:
			temp=server.recallInAll(msg)
		t=[]
		import cPickle,struct
		setting={
			"i32":[1,"i",4],
			"i16":[2,"h",2]
		}
		for v in temp:
			try:
				v=cPickle.loads(v[me.S['P']['pack']])[setting[me.S['P']['pack_index']][0]]
				v=struct.unpack("%s"%(setting[me.S['P']['pack_index']][1])*(len(v)/setting[me.S['P']['pack_index']][2]),v)
				if me.S['P']['export']!="":
					role_id=v['role_id']
					t.append([role_id,v[int(me.S['P']['index'])]])
				else:
					t.append(v[int(me.S['P']['index'])])
				del v
			except:
				traceback.print_exc()
				pass
		#导出
		if me.S["P"]["export"]!="":
			try:
				temp=[]
				for v in t:
					if me.S['P']['export']=="":
						v=[v]
					temp.append(v)
				data=model.export(temp)
			except:
				traceback.print_exc()
				pass
		else:
			data['data']=tool.rangeDatum(t,me.S['P']['range'])
	#print data['data']
	return data
def getID(m):
	if 'server' not in m or 'from' not in m or 'id' not in m:
		return
	id_field=model.info('role')['map']['name']['field']
	if m['from']=="account":
		id_field=model.info('role')['map']['account']['field']
	temp=memory.get('recall',{"one":True,"memory":"server:%s" % m['server'],"model":model.info('role')['name'],"field":model.info('role')['map']['id']['field'],"filter":{id_field:m['id']}})
	if temp and model.info('role')['map']['id']['field'] in temp:
		return temp[model.info('role')['map']['id']['field']]

def getInfo(role_id,field="name"):
	#multi fields
	role_id=int(role_id)
	temp=field.split(',')
	field=''
	for v in temp:
		if v in model.info('role')['map']:
			field+=",%s as %s"%(model.info('role')['map'][v]['field'],v)
	field=field.strip(',')
	msg={
		"one":True,
		"memory":"role:%s" % role_id,
		"model":model.info('role')['name'],
		"field":"%s"%(field),
		"filter":{model.info('role')['map']['id']['field']:role_id}
	}
	temp=memory.get('recall',msg)
	if temp:
		return temp
	else:
		return msg

def ban():
	data={}
	me.S['G']['id_type']=me.S['G'].get('id_type','role_id')
	me.S['G']['id']=me.S['G'].get('id','')
	me.S['G']['type']=me.S['G'].get('type','speak')
	me.S['G']['server']=me.S['G'].get('server')
	me.S['G']['ban_all']=me.S['G'].get('ban_all',None)
	#ban single
	import time,tool
	if me.S['G']['id']!="":
		#transfer id
		role_id=me.S['G']['id']
		if me.S['G']['id_type']!='role_id':
			role_id=getID({"from":me.S['G']['id_type'],"id":role_id,"server":me.S['G']['server']})
		elif not role_id.isdigit():
			data['tips']="角色ID必须为数字！"
			return data
		
		if not role_id:
			data['tips']="角色ID不存在！"
		else:
			#ban all
			if me.S['G']['ban_all']:
				me.S['G']['ban_all']=None
				try:
					roles=getAllID(role_id)
					data['tips']=[]
					for v in roles:
						me.S['G']['ban_all']=None
						me.S['G']['id_type']="role_id"
						me.S['G']['id']=str(v)
						temp=ban()
						data['tips'].append(temp['tips'])
					data['tips']='<br />'.join(data['tips'])
				except:
					data['tips']="不存在此用户或封出错"
			else:
				#ban single
				post={}
				post['role_id']=int(role_id)
				post['end_time']=int(body.now())+86400*365
				post['expire_time']=int(body.now())-864000
				post['type']=me.S['G']['type']
				data=me.post("role/ban",post)
	data['servers']=server.getAll()
	return data
def checkBan():
	data={}
	me.S['G']['date_start']=me.S['G'].get('date_start',tool.date(body.now()))
	me.S['G']['date_end']=me.S['G'].get('date_end',tool.date(body.now()))
	me.S['G']['like']=me.S['G'].get('like',"")
	like=""
	if me.S['G']['like']!="":
		like=' and request like "%%%s%%"'%(me.S['G']['like'])
	data=model.get({"models":{
		"model":"action",
		"filter":'model="role" and action="ban" and request is not NULL and date_format(start_time,"%%Y-%%m-%%d") between "%s" and "%s"%s'%(me.S['G']['date_start'],me.S['G']['date_end'],like)
	}})
	data['servers']=server.getAll()
	return data
def getAllID(role_id):
	data=[]
	account=getInfo(role_id,'account')['account']
	temp=server.recallInAll({
		"model":model.info('role')['name'],
		"field":"%s as role_id"%(model.info('role')['map']['id']['field']),
		"filter":"%s='%s'"%(model.info('role')['map']['account']['field'],account)
	})
	for v in temp:
		data.append(v['role_id'])
	return data
def sendCommand(role,m):
	from ComplexServer.Plug.DB import DBHelp
	con=me.openMemory({"memory":"role:%s" % role,"dict":False})
	return DBHelp.InsertRoleCommand_Con(con, role, m)
	
#send mail
def sendMail():
	data={}
	#to send
	if not user.inGroup("operate"):return user.ban()
	me.S['P']['id_type']=me.S['P'].get("id_type","role_id")
	me.S['P']['id']=me.S['P'].get("id","")
	me.S['P']['roles']=me.S['P'].get("roles","")
	me.S['P']['server']=me.S['P'].get('server')
	#servers
	data['servers']=server.getAll()
	#get common param
	data['items']=me.post("item/getAll")
	items_json=[]
	for k,v in data['items'].items():
		items_json.append("%s/%s"%(v,k))
	import json
	data['items_json']=json.dumps(items_json)
	#send
	if me.S['P']['id'] or me.S['P']['roles']:
		if me.S['P']['roles']!="":
			role_id=[]
			temp=me.S['P']['roles'].splitlines()
			try:
				for v in temp:
					v=v.strip()
					if v=="":continue
					#transfer to id
					if me.S['P']['id_type']!="role_id":
						v=str(getID({"from":me.S['P']['id_type'],"id":v,"server":me.S['P']["server"]}))
					#check
					if v!="" and v.isdigit() and (v not in role_id):
						role_id.append(v)
			except:
				traceback.print_exc()
				data['tips']="多用户列表中存在有误记录！"
				return data
			del temp
			role_id=",".join(role_id)
		else:
			role_id=me.S['P']['id']
			if me.S['P']['id_type']!='role_id':
				role_id=getID({"from":me.S['P']['id_type'],"id":me.S['P']['id'],"server":me.S['P']["server"]})
			elif not role_id.isdigit():
				data['tips']="角色ID必须为数字！"
				return data
		
		if not role_id:
			data['tips']="角色ID不存在！"
		else:
			#get mail content
			me.S['P']['sender']=me.S['P'].get("sender",'')
			me.S['P']['content']=me.S['P'].get("content",'')
			me.S['P']['title']=me.S['P'].get("title",'')
			me.S['P']['items']=me.S['P'].getlist("items")
			me.S['P']['money']=me.S['P'].get("money","")
			me.S['P']["exp"]=me.S['P'].get("exp","")
			me.S['P']["strength"]=me.S['P'].get("strength","")
			me.S['P']["unbindrmb"]=me.S['P'].get("unbindrmb","")
			me.S['P']["bindrmb"]=me.S['P'].get("bindrmb","")
			#filter default
			for v in ['money','exp','strength','unbindrmb','bindrmb']:
				if me.S['P'][v]=="":me.S['P'][v]=0
			
			if str(me.S['P']['server'])=="all" and me.S['user']['name'] not in ["yanghongpeng","james"]:return user.ban()
			if me.S['P']['sender'] and me.S['P']['title'] and me.S['P']['content']:
				try:
					post={
						"game":me.S['A']['game'],
						"operator":int(me.S['A']['operator']),
						"server":me.S['P']['server'],
						"role_id":role_id,
						"user":me.S['user']['name'],
						"sender":me.S['P']['sender'],
						"title":me.S['P']['title'],
						"content":me.S['P']['content'],
						"items":','.join(me.S['P']['items']),
						"money":me.S['P']['money'],
						"exp":me.S['P']['exp'],
						"strength":me.S['P']['strength'],
						"unbindrmb":me.S['P']['unbindrmb'],
						"bindrmb":me.S['P']['bindrmb'],
						"time":tool.date(body.now(),'%Y-%m-%d %H:%M:%S')
					}
					#record mail
					memory.get("remember",{"model":"mail","data":post})
					data['tips']="成功添加邮件！请等待审核及发送！"
				except:
					traceback.print_exc()
					data['tips']="邮件添加失败！请重新添加！"
			else:
				data['tips']="请先完整填写邮件！"
	return data

def guideMail():
	if not user.inGroup("operate"):return user.ban()
	data={}
	if 'ids' in me.S['P']:
		if not user.inGroup("resource"):return user.ban()
		data={}
		if "ids" not in me.S['P']:
			data['tips']="请先选择待审核的邮件！"
			return data
		me.S['P']['ids']=me.S['P'].getlist('ids')
		get=memory.get("recall",{"model":"mail","filter":"id in (%s) and status!=1"%(",".join(me.S['P']['ids']))})
		status=[]
		for v in get:
			try:
				#非当前平台或游戏
				if v['game']!=me.S['A']['game'] or v['operator']!=int(me.S['A']['operator']):
					continue
				role_ids=str(v['role_id']).split(',')
				import log
				#对每个用户发放
				for role_id in role_ids:
					if role_id!="5201314":
						v['server']=getServerID(role_id)
					post={
						"server":v['server'],
						"role_id":role_id,
						"sender":v['sender'],
						"title":v['title'],
						"content":v['content'],
						"items":v['items'],
						"money":v['money'],
						"exp":v['exp'],
						"strength":v['strength'],
						"unbindrmb":v['unbindrmb'],
						"bindrmb":v['bindrmb']
					}
					log.add(post)
					data=me.post("role/sendMail",post)
				#log status
				status.append(str(v['id']))
			except:
				traceback.print_exc()
		#update status
		done=memory.get("remember",{"action":"edit","model":"mail","data":{"status":1},"filter":"id in (%s) and status!=1"%(",".join(status))})
		data={"tips":"成功审核并发送：(%s)"%(",".join(status))}
	
	temp=model.guide({"option":{"order":"time,desc"},"model":"mail","field":"*","filter":'operator=%s and game="%s"'%(me.S['A']['operator'],me.S['A']['game'])})
	data.update(temp)
	data['servers']=server.getAll()
	return data

def getServerID(role_id):
	return int(role_id)/2**32
#only longqi
def rankFight():
	if not user.inGroup("operate"):return user.ban()
	data={}
	me.S['G']['date_start']=me.S['G'].get('date_start',"2014-01-01")
	me.S['G']['date_end']=me.S['G'].get('date_end',tool.date(body.now()))
	me.S['G']['all']=me.S['G'].get('all',"")
	me.S['G']['export']=me.S['G'].get('export',"")
	me.S['G']['min_fight']=int(me.S['G'].get('min_fight',"10000"))
	me.S['G']['export_account']=me.S['G'].get('export_account',"")
	me.S['G']['export_level']=me.S['G'].get('export_level',"")
	
	msg={
		"model":model.info('role')['name'],
		"field":"%s as role_id,%s as fight"%(
			model.info('role')['map']['id']['field'],
			model.info('role')['map']['role_fight']['field']
		),
		"filter":'date(%s) between "%s" and "%s" and %s>=%s'%(
			model.info('role')['map']['create_time']['field'],
			me.S['G']['date_start'],
			me.S['G']['date_end'],
			model.info('role')['map']['role_fight']['field'],
			me.S['G']['min_fight']
		),
		"option":{"order":"fight,desc"},
		"range":me.S['G'].get("range","1,20")
	}
	
	if me.S['G']['all']=="":
		msg['memory']="server:%s"%me.S['A']['server']
		#export no range
		if me.S['G']['export']!="":
			del msg['range']
		data=model.get({
			"data":msg
		})
		#export no range
		if me.S['G']['export']=="":
			#range
			range_msg={
				"model":model.info('role')['name'],
				"filter":'date(%s) between "%s" and "%s" and %s>=%s'%(
					model.info('role')['map']['create_time']['field'],
					me.S['G']['date_start'],
					me.S['G']['date_end'],
					model.info('role')['map']['role_fight']['field'],
					me.S['G']['min_fight']
				),
				"url":me.S["path"],
				"msg":{
					"date_start":me.S['G']['date_start'],
					"date_end":me.S['G']['date_end'],
					"min_fight":str(me.S['G']['min_fight']),
				},
				"memory":"server:%s"%me.S['A']['server'],
				"size":"20",
				"range":me.S['G'].get("range",'1,20')
			}
			data['range']=body.getRange(range_msg) #get range
	else:
		#all servers
		me.S['G']['ranges']=me.S['G'].get('ranges',"20")
		key="%s_%s_role-fight_rank_all_%s"%(me.S['A']['game'],me.S['A']['operator'],me.S['G']['ranges'])
		data['data']=cache.get(key)
		if not data['data']:
			msg['range']="1,%s"%(me.S['G']['ranges'])
			data['data']=server.recallInAll(msg,{"server_field":True})
			data['data']=sorted(data['data'],key=lambda x : x['fight'],reverse=True)
			data['data']=data['data'][:int(me.S['G']['ranges'])]
			cache.set(key,data['data'],3600)#每小时更新
		else:
			data['tips']="你正在查看缓存排名数据，每小时更新！"
		data['servers']=server.getAll()
	#add name
	if me.S['G']['export']=="":
		field='name,time_last_login,time_total_online,vip'
		for v in data['data']:
			v.update(getInfo(v['role_id'],field))
	else:
		field=""
		if me.S['G']['export_account']!="":field+="account"
		if me.S['G']['export_level']!="":field+=",level"
		if field!="":
			for v in data['data']:
				try:
					v.update(getInfo(v['role_id'],field))
				except:
					traceback.print_exc()
					print "ERROR ID:",v['role_id']
					pass
	#export
	if me.S['G']['export']!="":
		fields=['role_id','fight']
		if me.S['G']['export_account']!="":fields.append("account")
		if me.S['G']['export_level']!="":fields.append("level")
		data=tool.dictToList(data['data'],fields)
		data.insert(0,fields)
		data=model.export(data)
	return data

#only longqi
def checkLog():
	if not user.inGroup("operate"):return user.ban()
	me.S['P']['id_type']=me.S['P'].get("id_type","role_id")
	me.S['P']['id']=me.S['P'].get("id","")
	me.S['P']['server']=me.S['P'].get('server')
	if me.S['P']['id']:
		role_id=me.S['P']['id']
		if me.S['P']['id_type']!='role_id':
			role_id=getID({"from":me.S['P']['id_type'],"id":me.S['P']['id'],"server":me.S['P']["server"]})
		elif not role_id.isdigit():
			data['tips']="角色ID必须为数字！"
			return data
		if not role_id:
			data['tips']="角色ID不存在！"
		#获取统计时间
		me.S['P']['start_time']=me.S['P'].get('start_time',"")
		me.S['P']['end_time']=me.S['P'].get('start_time',"")
		
		me.S['P']['log_type']=me.S['P'].get('log_type',tool.date(time.time()))
		#msg
		msg={}
		if me.S['P']['log_type']=="value":
			msg={
				"model":"log_value",
				"field":"log_datetime as time,log_event as event,log_transaction as transaction,log_new_value-log_old_value as value",
				"filter":'role_id=%s and log_datetime between "" and ""'
			}
def checkBaseLog():
	if not user.inGroup("operate"):return user.ban()
	data={}
	me.S['P']['date_start']=me.S['P'].get('date_start',tool.date(body.now()))
	me.S['P']['date_end']=me.S['P'].get('date_end',tool.date(body.now()))
	#只允许查一天
	if me.S['P']['date_start']!=me.S['P']['date_end']:
		data['tips']=word.check("因日志数据量太大，暂时只开放查一天的！")
		return data
	me.S['P']['all']=me.S['P'].get('all','')
	me.S['P']['range']=me.S['P'].get('range','10')
	me.S['P']['transaction']=me.S['P'].get('transaction','')
	me.S['P']['event']=me.S['P'].get('event','30088')
	if me.S['P']['event']!="":
		transaction_range=''
		if me.S['P']['transaction']!='':transaction_range=' and %s in (%s)'%(model.info('log_value')["map"]["transaction"]['field'],me.S['P']['transaction'])
		
		me.S['P']['parallel']=me.S['P'].get('parallel','')
		#并行开关
		parallel={"parallel":False}
		if me.S['P']['parallel']!="":
			parallel["parallel"]=True
		msg={
			"track":True,
			"model":"%s"%(model.info('log_base')["name"]),
			"field":"%s as role_id,%s as transaction"%(
				model.info('log_value')["map"]["role_id"]['field'],
				model.info('log_value')["map"]["transaction"]['field']
			),
			"filter":'DATE_FORMAT(%s,"%%Y-%%m-%%d") between "%s" and "%s" and %s in (%s)%s'%(
				model.info('log_value')["map"]["spliter"]['field'],
				me.S['P']['date_start'],
				me.S['P']['date_end'],
				model.info('log_value')["map"]["event"]['field'],
				me.S['P']['event'],
				transaction_range
			),
			"option":{"group":"transaction,role_id"},
			"range":"0,%s"%(me.S['P']['range']),
			"prefix_type":"log"
		}
		data['data']={}
		if me.S['P']['all']=='':
			msg.update({"memory":"server:%s"%(me.S['A']['server'])})
			temp=memory.get('recall',msg)
			for v in temp:
				if not v['transaction'] in data['data']:
					data['data'][v['transaction']]={"roles":0}
				data['data'][v['transaction']]["roles"]+=1
		else:
			msg['range']="0,100"
			temp=server.recallInAll(msg,parallel)
			t={}
			for v in temp:
				if not v['transaction'] in t:
					t[v['transaction']]={"roles":0}
				t[v['transaction']]['roles']+=1
			t=sorted(t.iteritems(), key=lambda x:x[1]["roles"],reverse=True)
			i=0
			for k,v in t:
				if i==int(me.S['P']['range']):break
				i+=1
				data['data'][k]=v
		#get transaction info
		transactions=me.post('log/getTransaction')
		for k,v in data['data'].items():
			data['data'][k]={"roles":v['roles'],"value":transactions.get(int(k),{"value":k})['value'],"desc":transactions.get(int(k),{"desc":""})['desc']}
	return data
def checkFightRange():
	import tool
	if not user.inGroup("operate"):return user.ban()
	data={}
	me.S['P']['date_start']=me.S['P'].get('date_start',tool.date(body.now()))
	me.S['P']['date_end']=me.S['P'].get('date_end',tool.date(body.now()))
	me.S['P']['min_fight']=me.S['P'].get('min_fight','10000')
	me.S['P']['range']=me.S['P'].get('range','')
	if me.S['P']['range']=='':me.S['P']['range']='20000,30000'
	me.S['P']['all']=me.S['P'].get('all','')
	msg={
		"model":model.info('role')["name"],
		"field":"%s as fight"%(
			model.info('role')["map"]["role_fight"]['field']
		),
		"filter":'date(%s) between "%s" and "%s" and %s>=%s'%(
			model.info('role')['map']['create_time']['field'],
			me.S['P']['date_start'],
			me.S['P']['date_end'],
			model.info('role')['map']['role_fight']['field'],
			me.S['P']['min_fight']
		),
	}
	if me.S['P']['all']=='':
		msg.update({"memory":"server:%s"%(me.S['A']['server'])})
		temp=memory.get('recall',msg)
	else:
		temp=server.recallInAll(msg)
	data['data']=tool.rangeData(temp,me.S['P']['range'],'fight')
	#print data['data']
	return data