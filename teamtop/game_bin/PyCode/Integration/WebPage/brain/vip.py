# -*- coding:UTF-8 -*-
import time,traceback
import me,user,model,tool,memory,server,role
def get():
	data={}
	if 'game' in me.S['G']:
		get={}
		try:
			get['game']=str(me.S['G']['game'])
			get['name']=str(me.S['G'].get('name',''))
			get['sex']=int(me.S['G'].get('sex',0))
			get['id_card']=str(me.S['G'].get('id_card',''))
			get['phone']=str(me.S['G'].get('phone',0))
			get['qq']=int(me.S['G'].get('qq',0))
			get['address']=str(me.S['G'].get('address',''))
			get['zipcode']=str(me.S['G'].get('zipcode',''))
			get['server']=int(me.S['G']['server'])
			get['role_id']=int(me.S['G']['role_id'])
			get['time']=tool.date(time.time(),"%Y-%m-%d %H:%M:%S")
			
			done=False
			if not memory.get("exist",{"model":"vip","filter":{"role_id":get["role_id"]}}):
				done=memory.get("remember",{"model":"vip","data":get})
			if done:
				data['response']="%s"%(get['role_id'])
			else:
				data['response']="DATABASE ERROR!"
		except:
			traceback.print_exc()
			import cPickle
			data['response']="%s"%(cPickle.dumps(get))
	else:
		data['response']="No Game Specified！"
	return data

def guide():
	if not user.inGroup("operate"):return user.ban()
	data={}
	msg={"filter":{"game":me.S['A']["game"]}}
	me.S['G']['export']=me.S['G'].get('export','')
	
	#export no dict
	if me.S['G']['export']!="":
		msg["range"]="1,1000000"
	#filter
	range_msg={}
	if "role_id" in me.S["G"]:
		if me.S['G']['role_id']!="":
			msg["filter"]["role_id"]=int(me.S["G"]["role_id"])
			range_msg['role_id']=me.S["G"]["role_id"]
	if "server" in me.S["G"]:
		if me.S['G']['server']!="":
			msg["filter"]["server"]=int(me.S["G"]["server"])
			range_msg['server']=me.S["G"]["server"]
	if "qq" in me.S["G"]:
		if me.S['G']['qq']!="":
			msg["filter"]["qq"]=int(me.S["G"]["qq"])
			range_msg['qq']=me.S["G"]["qq"]
	if "operator" not in msg["filter"]:
		msg["filter"]["operator"]={}
	#time range
	me.S["G"]["date_start"]=me.S["G"].get("date_start","")
	me.S["G"]["date_end"]=me.S["G"].get("date_end","")
	range_msg['date_start']=me.S["G"]["date_start"]
	range_msg['date_end']=me.S["G"]["date_end"]
	if me.S["G"]["date_start"]!="" and me.S["G"]["date_end"]!="":
		msg["filter"]["time"]='%s 00:00:00" and "%s 23:59:59'%(me.S["G"]["date_start"],me.S["G"]["date_end"])
		msg["filter"]["operator"]["time"]=" between "
	elif me.S["G"]["date_start"]!="":
		msg["filter"]["time"]='%s 00:00:00'%me.S["G"]["date_start"]
		msg["filter"]["operator"]["time"]=">="
	elif me.S["G"]["date_end"]!="":
		msg["filter"]["time"]='%s 23:59:59'%(me.S["G"]["date_end"])
		msg["filter"]["operator"]["time"]="<="
	#range
	msg['range_msg']=range_msg
	data=model.guide(msg)
	
	#servers
	data['servers']=server.getAll()
	#add info
	for v in data['models']:
		v['server_name']=data['servers'].get(v['server'],{"value":v['server']})['value']
		try:
			info=role.getInfo(v['role_id'],'name,time_last_login,charge')
			info['role_name']=info['name']
			del info['name']
			v.update(info)
		except:
			print info
			traceback.print_exc()
			pass
		#last pay
		try:
			v['time_last_pay']=memory.get("recall",{"one":True,"memory":"server:%s"%(v['server']),"model":"%s"%(model.info('charge')["name"]),"field":"date_format(max(%s),'%%Y-%%m-%%d %%H:%%i:%%s') as time_last_pay"%(model.info('charge')['map']["spliter"]["field"]),"filter":{"%s"%(model.info('charge')['map']["role_id"]['field']):v['role_id']}})['time_last_pay']
		except:
			v['time_last_pay']="-"
			traceback.print_exc()
			pass
	#export
	if me.S['G']['export']!="":
		fields=["server","server_name","role_id","role_name","name","sex","id_card","phone","qq","address","zipcode","time_last_login","time_last_pay","charge","time"]
		data=tool.dictToList(data['models'],fields)
		data.insert(0,fields)
		data=model.export(data)
	else:
		#red
		import time
		for v in data['models']:
			v['login_red']=""
			v['pay_red']=""
			try:
				if time.time()-tool.strtotime(v.get('time_last_login',''))>3*86400:
					v['login_red']="color:red"
				if time.time()-tool.strtotime(v.get('time_last_pay',''))>7*86400:
					v['pay_red']="color:red"
			except:
				traceback.print_exc()
	return data
	
def edit():
	if not user.inGroup("operate"):return user.ban()
	return model.edit()