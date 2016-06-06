# -*- coding: utf-8 -*-
import traceback,time
import me,memory,body,user,tool,server
def add():
	if 'user' not in me.S:return user.ban()
	data={}
	post={"name":me.S['A']['model'],"property":tool.copy(info(me.S['A']['model'])['property'])}
	if checkPost(post):
		#set data
		try:
			done=memory.get('add',{"model":info(me.S['A']['model'])['name'],"data":me.S['P']})
			data['tips']='已经成功增加记录!'
			data['id']=done
		except:
			traceback.print_exc()
			data['tips']='增加记录失败，请重新操作！'
			pass
	#else need a form to fill
	else:
		#get data
		if post['property'][info(me.S['A']['model'])['map']['id']['field']].get('auto',False)==True:
			del post['property'][info(me.S['A']['model'])['map']['id']['field']]
		data['common']=body.drawForm(post)
	return data

#check model entity owner
def checkOwner(msg):
	import home
	#just get my card data
	if 'card' in msg['filter']:
		if msg['filter']['card']!=me.S['card']['id']:
			msg['filter']['card']=me.S['card']['id']
	elif 'owner' not in msg['filter'] or (msg['filter']['owner']!=me.S['D']['owner']):
		#lostnote and need all
		if me.S['D']['owner'] in [3] and msg['filter'].get('owner','')==0:
			del msg['filter']['owner']
		else:
			msg['filter']['owner']=me.S['D']['owner']
	return msg
	
def copy():
	data={}
	data=edit()
	return data
def remove():
	if 'user' not in me.S:return user.ban()
	#no entity being edit
	if 'id' not in me.S['G']:
		return {"tips":"没有指定要移除的数据!"}
	done=memory.get('forget',{
		"model":info(me.S['A']['model'])['name'],
		"filter":{info(me.S['A']['model'])['map']['id']['field']:me.S['P'][info(me.S['A']['model'])['map']['id']['field']]}
	})
	if done:
		data['tips']='已经成功移除数据!'
	else:
		data['tips']='移除数据失败，请重新操作！'
	return data

def edit():
	if 'user' not in me.S:return user.ban()
	#no entity being edit
	if 'id' not in me.S['G']:
		return {"tips":"没有指定要编辑的数据!"}
	data={}
	post={"name":me.S['A']['model'],"property":tool.copy(info(me.S['A']['model'])['property'])}
	if checkPost(post):
		#set data
		done=memory.get('edit',{
			"model":info(me.S['A']['model'])['name'],
			"data":me.S['P'],
			"filter":{info(me.S['A']['model'])['map']['id']['field']:me.S['P'][info(me.S['A']['model'])['map']['id']['field']]}
		})
		if done:
			data['tips']='已经成功更新!'
		else:
			data['tips']='更新失败，请重新操作！'
	#else need a form to fill
	else:
		#get data
		post['property'][info(me.S['A']['model'])['map']['id']['field']]['type']="hidden"
		post['data']=memory.get("recall",{
			"one":True,
			"model":info(me.S['A']['model'])['name'],
			"filter":{info(me.S['A']['model'])['map']['id']['field']:me.S['G']['id']}
		})
		data['common']=body.drawForm(post)
	return data
	
def exist(msg):
	return memory.get('exist',{"model":"model","filter":{"byname":msg}})
#get entity info
def get(msg=None):
	if not msg:msg={}
	data={}
	for k,v in msg.items():
		#default model
		if 'model' not in v:
			v['model']=me.S['A']['model']
		if 'action' in v: #from model
			Model=me.review(v['model'])
			action=getattr(Model,v['action'])
			if 'msg' in v and 'session' in v:
				data[k]=action(v['msg'])
			elif 'session' in v:
				data[k]=action()
			else:
				data[k]=action()
			continue
		#if just for transfer
		if 'value' in v:
			data[k]=v['value']
		else:
			if 'filter' not in v:
				v['filter']={}
			#get info for the main query,not guide model,guide
			if k=="models":
				if 'category' in me.S['G']:
					if 'like' not in v['filter']:
						v['filter']['like']={}
					v['filter']['like']['category']=me.S['G']['category']
				if 'search' in me.S['G']:
					searchby='name'
					if 'by' in me.S['G']:
						searchby=me.S['G']['by']
					if 'like' not in v['filter']:
						v['filter']['like']={}
					v['filter']['like'][me.S['G']['search']]=searchby
				#set filter
				if 'filter' in me.S['G']:
					import urllib,json
					v['filter'].update(json.loads(urllib.unquote(me.S['G']['filter'].encode('utf-8','ignore')).decode('utf-8','ignore')))
				#set range
				if 'range' in me.S['G']:
					v['range']=me.S['G']['range']
				elif 'range' in v:
					me.S['G']['range']=v['range']
				#set order
				if 'order' in me.S['G']:
					v['option']={"order":me.S['G']['order']}
				elif 'order' in v:
					v['option']={"order":v['order']}
			cv=tool.copy(v)
			temp=memory.get('recall',cv)
			data[k]=temp
			if k=='models':
				range_msg={"model":v['model'],"filter":v.get('filter'),"url":me.S["path"]}
				if "range_msg" in v:
					range_msg['msg']=v['range_msg']
				if 'memory' in v:
					range_msg['memory']=v['memory']
				data['range']=body.getRange(range_msg) #get range
	return data

def info(msg=None):
	data={}
	import cache
	#get model info
	game="common"
	if 'game' in me.S['A'] and str(me.S['A']['game'])!="0":
		game=me.S['A']["game"]
	#cache
	key="%s_model-info"%(game)
	data=cache.get(key)
	if not data:
		data=getGameInfo()
		cache.set(key,data)
	#specified model
	if msg:
		data=data[msg]
	return data

def getGameInfo():
	data={}
	from heart import model as Model
	data=Model.info()
	for k,v in data.items():
		try:
			if isinstance(data[k]['property'],dict):
				continue
			data[k]['property']=tool.Dict(data[k]['property'])
			#print data[k]['property'],"AFTER"
			for kk,vv in v['map'].items():
				if isinstance(vv,basestring):
					data[k]['map'][kk]={"field":vv,"name":vv}
		except:
			traceback.print_exc()
			pass
	return data

def guide(msg=None):
	if 'user' not in me.S:return user.ban()
	data={}
	if not msg:msg={}
	#default field
	if 'field' not in msg:
		msg["field"]=info(me.S['A']['model'])["property"].keys()
		#remove some field
		for v in msg['field']:
			try:
				if info(me.S['A']['model'])["property"][v]["type"]=="password":
					msg['field'].remove(v)
			except:
				print info(me.S['A']['model'])["property"]
				traceback.print_exc()
		msg['field']="`%s`"%("`,`".join(msg['field']))
	msg['model']=msg.get('model',info(me.S['A']['model'])['name'])
	msg['range']=msg.get('range',me.S['G'].get('range',"1,20"))
	#get data
	data=get({
		"models":msg
	})
	data["common"]=""
	return data
def checkMemory():
	data={}
	models={}
	sql='Model Update me.SQL:<br />'
	models=memory.get('recall',{"model":"model"})
	for v in models:
		if 'property' in v and v['property']!='':
			try:
				sql+=syncMemory(v['byname'],eval(tool.filterJSON(v['property'])))
			except:
				print v['byname']
				traceback.print_exc()
				pass
	data['tips']={"msg":sql,"delay":16800000}
	return data

#check : check if structure changed ,if true, bak and sync
def syncMemory(model,property):
	if len(property)==0:
		return ''
	modelProperty={}
	modelProperty_list=property
	#to word
	for v in modelProperty_list:
		if 'type' not in v: #default type
			v['type']='var'
		if 'label' not in v: #default label
			v['label']=v['key'].capitalize()
		if v['type'] in ['radio']:
			v['type']='int'
		if v['type'] in ['category','file','hidden','model','checkbox','link','datetime']:
			v['type']='var'
		if v['type'] in ['code','textfield','files']:
			v['type']='text'
		if v['type'] in ['textarea']:
			v['type']='mediumtext'
		#set the default length to 50
		if 'length' not in v: #default length
			v['length']=''
			if v['type']=='var':
				v['length']='500'
			if v['type']=='int':
				v['length']='11'
		v['length']=str(v['length']) # length to str
		modelProperty[v['key']]=v
	update=False
	update=checkMemoryExist(model)
	#check database status
	sql='SELECT COLUMN_NAME FROM  `information_schema`.`COLUMNS` where `TABLE_SCHEMA`="meaing"  and  `TABLE_NAME`="'+model+'" order by COLUMN_NAME'
	modelFields=[]
	result=memory.get('fetchAll',sql)
	for v in result:
		modelFields.append(v)
	delete_sql=''
	for fk,fv in enumerate(modelFields):
		modelFields[fk]=fv['COLUMN_NAME']
		#delete unknown field
		if fv['COLUMN_NAME'] not in modelProperty and fv['COLUMN_NAME'] not in ["id","byname"]:
			delete_sql+='ALTER TABLE  `'+model+'` DROP  `'+fv['COLUMN_NAME']+'`;'
	#adjust
	action={}
	for property,structure in modelProperty.items():
		#if the same
		action[property]='update'
		if property not in modelFields:
			action[property]='add'
		#else:
			#if modelProperty[property]['type']!=memoryInfo[property]['type']:
				#modelProperty[property]['action']='change'
	#update table
	if not update:
		sql="CREATE TABLE IF NOT EXISTS `"+model+"` (`id` int(12) NOT NULL AUTO_INCREMENT,"
		for property,structure in modelProperty.items():
			#deal with the types
			if structure['type']=='var':
				sql+="`"+property+"` VARCHAR("+structure['length']+") DEFAULT ''"
			if structure['type']=='int':
				sql+="`"+property+"` INT("+structure['length']+") NOT NULL DEFAULT 0"
			if structure['type']=='float':
				sql+="`"+property+"` FLOAT("+structure['length']+") DEFAULT 0"
			if structure['type']=='decimal':
				sql+="`"+property+"` DECIMAL("+structure['length']+") NOT NULL DEFAULT 0"
			if structure['type']=='text':
				sql+="`"+property+"` TEXT NOT NULL"
			if structure['type']=='mediumtext':
				sql+="`"+property+"` MEDIUMTEXT NOT NULL"
			sql+=" COMMENT '"+structure['label']+"',"
		sql+="`byname` varchar(100) NOT NULL,PRIMARY KEY  (`id`)) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1;"
	else:
		#fields=array_keys(memoryInfo)
		#unset(fields[0])
		#print_r(modelFields)
		#fields=array_splice(fields,0,count(fields)-1)
		#add fields or update fields
		modelFields.remove('id')
		modelFields.remove('byname')
		sql=""
		for property,structure in modelProperty.items():
			if action.get(property)=='change':
				sql+="ALTER TABLE  `"+model+"` "
				if structure['type']=='var':
					sql+=action[property]+" `"+property+"` `"+property+"` VARCHAR("+structure['length']+") DEFAULT '',"
				if structure['type']=='int':
					sql+=action[property]+" `"+property+"` `"+property+"` INT("+structure['length']+") DEFAULT 0,"
				if structure['type']=='float':
					sql+=action[property]+" `"+property+"` `"+property+"` FLOAT("+structure['length']+") NOT NULL DEFAULT 0,"
				if structure['type']=='decimal':
					sql+=action[property]+" `"+property+"` `"+property+"` DECIMAL("+structure['length']+") NOT NULL DEFAULT 0,"
				if structure['type']=='text':
					sql+=action[property]+" `"+property+"` `"+property+"` TEXT NOT NULL,"
				if structure['type']=='mediumtext':
					sql+=action[property]+" `"+property+"` `"+property+"` MEDIUMTEXT NOT NULL,"
			elif action.get(property)=='add':
				sql+="ALTER TABLE  `"+model+"` "
				#add to where
				if property not in modelFields:
					modelFields.append(property)
				modelFields.sort()
				after=modelFields.index(property)
				if after!=0:
					after=modelFields[after-1]
				else:
					after='id'
				if structure['type']=='var':
					sql+=action[property]+" `"+property+"` VARCHAR("+structure['length']+") DEFAULT ''"
				if structure['type']=='int':
					sql+=action[property]+" `"+property+"` INT("+structure['length']+") NOT NULL DEFAULT 0"
				if structure['type']=='float':
					sql+=action[property]+" `"+property+"` FLOAT("+structure['length']+") NOT NULL DEFAULT 0"
				if structure['type']=='decimal':
					sql+=action[property]+" `"+property+"` `"+property+"` DECIMAL("+structure['length']+") NOT NULL DEFAULT 0,"
				if structure['type']=='text':
					sql+=action[property]+" `"+property+"` TEXT NOT NULL"
				if structure['type']=='mediumtext':
					sql+=action[property]+" `"+property+"` MEDIUMTEXT NOT NULL"
				sql+=" after `"+after+"`;"
	return sql+delete_sql

def view():
	import tool
	data={}
	#update visit count
	property=self('property')
	if 'visit' in property:
		temp=memory.get("recall",{"model":me.S['A']['model'],"one":True,"field":"visit","filter":{"owner":me.S['D']['owner'],"id":me.S['A']['entity']}})
		try:
			count=int(temp['visit'])+1
		except:
			count=1
		memory.get("remember",{"model":me.S["A"]["model"],"filter":{"owner":me.S['D']['owner'],"id":me.S['A']['entity']},"data":{"visit":count}})
	return data
def remove():
	data={}
	if not card.own():
		data=card.ban()
	else:#remove
		#check
		entity=me.S['M'].get('entity',me.S['A'].get('entity',False))
		if not entity:
			data['tips']={"msg":"No Entities me.Specified!"}
		else:
			if 'confirm' not in me.S['M']:
				data['tips']={"msg":"Are You Confirm to Remove These Entities?","url":me.S['path'].strip('/').replace(me.S['A']['model'],'%s/confirm/true'%me.S['A']['model']),"delay":16800000}
			else:
				#pending remove
				keep=True
				if me.S['A']['model']!='bin':
					temp=memory.get('recall',{"model":me.S['A']['model'],"key":"id","filter":"owner=%s and id in (%s)"%(me.S['card']['id'],entity)})
					if temp:
						#move to trash
						temp_name=''
						for k,v in temp.items():
							temp_name+=',%s'%v['name']
						import pickle,time
						temp=pickle.dumps(temp)
						done=memory.get("remember",{"model":"bin","data":{"name":temp_name.strip(','),"owner":S['card']['id'],"byname":'%s(%s)'%(me.S['A']['model'],me.S['M']['entity']),"time":time.strftime('%Y-%m-%d %H:%M:%S'),"content":temp}})
						if done:
							keep=False
				#empty bin
				elif entity=='all':
					done=memory.get('forget',{"model":"bin","filter":"where 1"})
					if done:
						data['tips']={"msg":"the bin is empty Now!"}
					else:
						data['tips']={"msg":"empty bin failed!"}
					return data
				else:
					keep=False
				if not keep:
					memory.get("forget",{"model":me.S['A']['model'],"filter":"owner=%s and id in (%s)"%(me.S['card']['id'],entity)})
					data['done']={"entity":entity}
					data['tips']={"msg":"has been removed!"}
				else:
					data['tips']={"msg":"has not been removed!"}
	return data
	
def check(msg={}):
	me.S['E']=me.S.get('E',{})
	#trim
	#check empty
	if msg.get(msg['check_key'])=='':
		me.S['E'][msg['check_key']]='Required'
		return
	import re
	if msg['if']=='isKey':
		if not bool(re.match(r'^[a-zA-Z\d_]{6,16}',msg[msg['check_key']],re.VERBOSE)):
			me.S['E'][msg['check_key']]='6-16 letter/number/underline'
	if msg['if']=='isLetter':
		if not bool(re.match(r'^[A-Za-z]+',msg[msg['check_key']],re.VERBOSE)):
			me.S['E'][msg['check_key']]='Letter only'
	if msg['if']=='isByname':
		if not bool(re.match(r'^[A-Za-z0-9-_]+',msg[msg['check_key']],re.VERBOSE)):
			me.S['E'][msg['check_key']]='Not byname'
	if msg['if']=='isMail':
		if not bool(re.match(r'[-a-zA-Z0-9._]+@[-a-zA-Z0-9_]+.[a-zA-Z0-9_.]+',msg[msg['check_key']],re.VERBOSE)):
			me.S['E'][msg['check_key']]='Wrong Email Format'
	if msg['if']=='isPhrase':
		if not bool(re.match(r'^([A-Za-z0-9]+[ ]+)+[A-Za-z0-9]+',msg[msg['check_key']],re.VERBOSE)):
			me.S['E'][msg['check_key']]='Letter,and at least one space'
	if msg['if']=='isChinese':
		if not bool(re.match(r'[\x7f-\xff]',msg[msg['check_key']],re.VERBOSE)):
			me.S['E'][msg['check_key']]='Chinese only'
	if msg['if']=='isAddress':
		if not bool(re.match(r'^[,\.#a-zA-Z0-9 ]{5,}',msg[msg['check_key']],re.VERBOSE)):
			me.S['E'][msg['check_key']]='Wrong Address Format'
	if msg['if']=='isZipcode':
		if not bool(re.match(r'^[a-zA-Z0-9]{2,10}',msg[msg['check_key']],re.VERBOSE)):
			me.S['E'][msg['check_key']]='Wrong Zipcode Format'
	if msg['if']=='isGlobalPhone':
		if not bool(re.match(r'\+[0-9]{1,4}\.[0-9]{10,15}',msg[msg['check_key']],re.VERBOSE)):
			me.S['E'][msg['check_key']]='Wrong Phone/Fax Format'
	if msg['if']=='isPhone':
		if not bool(re.match(r'^[0-9]{10,15}',msg[msg['check_key']],re.VERBOSE)):
			me.S['E'][msg['check_key']]='Wrong Phone/Fax Format'
	if msg['if']=='isNumber':
		if not bool(re.match(r'^[0-9]{1,}',msg[msg['check_key']],re.VERBOSE)):
			me.S['E'][msg['check_key']]='Number only'
	
#check entity data
def checkPost(msg):
	#no post
	data=False
	if not msg:
		data=True
	elif len(me.S['P'])>0:
		property=msg.get('property',{})
		#check format, not include the post just for check
		me.S['E']={}
		#check
		for k,v in me.S['P'].items():
			#if special
			if property.get(k,{'type':''}).get('type')=='link':
				if property.get(k,{'view':"select"}).get('view')=="checkbox":
					me.S['P'][k]=','.join(me.S['P'].getlist(k))
			#check format
			if 'check' in property.get(k,[]):
				check({'if':property[k]['check'],'check_key':k,k:v})
			#check confirm, eg. key==key_confirm
			key_parts=k.split('_')
			if len(key_parts)==2 and key_parts[1]=='confirm':
				if me.S['P'][key_parts[0]]!=me.S['P'][k]:
					me.S['E'][k]=key_parts[0]+' '+'确认不一致！'
				else:
					del me.S['P'][k]
		if len(me.S['E'])==0:
			data=True
	return data

def getEntity():
	data={}
	return data
def query():
	if not user.inGroup("host"):return user.ban()
	if not me.S['user']['name'] in ['james']:return user.ban()
	data={}
	me.S['P']['all']=me.S['P'].get('all','')
	me.S['P']['slave']=me.S['P'].get('slave','')
	me.S['P']['export']=me.S['P'].get('export','')
	me.S['P']['serialize']=me.S['P'].get('serialize','')
	me.S['P']['log']=me.S['P'].get('log','')
	me.S['P']['sql']=me.S['P'].get('sql','')
	
	me.S['P']['parallel']=me.S['P'].get('parallel','')
	me.S['P']['merge']=me.S['P'].get('merge','')
	#并行开关
	parallel={"parallel":False}
	if me.S['P']['parallel']!="":
		parallel["parallel"]=True
	#server field
	me.S['P']['server_field']=me.S['P'].get('server_field','')
	if me.S['P']['server_field']!="":
		parallel['server_field']=True
	if me.S['P']['sql']!="":
		#检查SQL安全性
		if memory.writeProtect(me.S['P']['sql'])=="":
			return {"tips":"SQL ERROR!"}
		
		msg={"sql":me.S['P']['sql'],"dict":False}
		if me.S['P']['log']!="":
			msg['prefix_type']="log"
		if me.S['P']['slave']!="":
			msg['slave']=True
		#merge query
		if me.S['P']['merge']!="":
			msg['merge']=me.S['P']['merge']
		if me.S['P']['all']=="":
			msg['memory']="server:%s"%(me.S['A']['server'])
			#need server key
			if parallel.get('server_field',False)==True:
				msg['sql']=msg['sql'].replace('{server_field}','%s as `server`'%(me.S['A']['server']))
			data['data']=memory.get("query",msg)
		else:
			data['data']=server.queryInAll(msg,parallel)
		if me.S['P']["serialize"]!="":
			import cPickle
			packs=me.S['P']['serialize'].split(',')
			for pack in packs:
				for v in data['data']:
					try:
						v[pack]=cPickle.loads(v[pack])
					except:
						traceback.print_exc()
						pass
		#export
		if me.S['P']['export']!='':
			try:
				data=export(data['data'])
			except:
				traceback.print_exc()
				pass
	return data
def export(msg,name="lostnote"):
	import csv
	from django.http import HttpResponse
	response = HttpResponse(mimetype="text/csv")  
	response['Content-Disposition'] = 'attachment; filename=%s.csv'%name  
	writer = csv.writer(response)
	for v in msg:
		writer.writerow(list(v))
	return {"return":response}

#对模块执行并行操作
def parallel(action,msg):
	from multiprocessing import Pool
	pool = Pool()
	
	data = pool.map(action,msg)
	pool.close() 
	pool.join()
	return data