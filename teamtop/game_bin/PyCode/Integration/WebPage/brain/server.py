# -*- coding:UTF-8 -*-
import time,traceback
import me,game,tool,memory,user,model,cache,body
def add():
	if not user.inGroup("host"):return user.ban()
	data={}
	if 'zone_id' in me.S['P']:
		done=me.post("server/add",me.S['P'])
		if 'zone_id' in done:
			me.S['P']['zone_id']=done['zone_id']
			data=model.add()
		else:
			data['tips']="增加失败，请重新增加！"
	else:
		data=model.add()
	return data
	
def edit():
	if not user.inGroup("host"):return user.ban()
	data={}
	if 'zone_id' in me.S['P']:
		done=me.post("server/edit",me.S['P'])
		if 'zone_id' in done:
			me.S['P']['zone_id']=done['zone_id']
			data=model.edit()
		else:
			data['tips']="修改失败，请重新操作！"
	else:
		data=model.edit()
	return data

def checkOnlineDuration():
	if not user.inGroup("operate"):return user.ban()
	me.S['P']['export']=me.S['P'].get('export','')
	data={}
	data['temp']=game.act()
	if me.S['P']['export']=="":
		#chart
		data['chart']={
			"chart":{
				"caption":"【%s】玩家总在线时长/分钟"%getAll().get(me.S["A"]['server'],{"value":me.S["A"]['server']})["value"],
				"xAxisName":"Sex",
				"yAxisName":"Sales",
				"numberPrefix":"",
				"baseFontSize":'16'
			},
			"data":[]
		}
		
		data['total_online']=[]
		for v in data['temp']:
			v['range']='%s-%s' % (v['duration']*5,int(v['duration']+1)*5)
			data['total_online'].append(v)
			
		#chart
		for v in data['temp']:
			data['chart']['data'].append({"label":str(v['range'])+"分钟","value":v['count']})
		import json
		data['chart']=json.dumps(data['chart'])
		data['servers']=getAll()
	else:
		fields=['duration','count']
		data=tool.dictToList(data['temp'],fields)
		data.insert(0,fields)
		data=model.export(data)
	return data

def checkLevelRange():
	if not user.inGroup("operate"):return user.ban()
	data=model.get({
		"count":{
			"one":True,
			"memory":'server:%s'%me.S["A"]['server'],
			"model":model.info('role')['name'],
			"field":'count(*) as count'
		},
		"temp":{
			"memory":'server:%s'%me.S['A']['server'],
			"model":model.info('role')['name'],
			"field":'%s as level'%(model.info('role')['map']['level']['field'])
		}
	})
	#chart
	data['chart']={
		"chart":{
			"caption":"【%s】玩家等级分布"%getAll().get(me.S["A"]['server'],{"value":me.S["A"]['server']})["value"],
			"xAxisName":"Sex",
			"yAxisName":"Sales",
			"numberPrefix":"",
			"baseFontSize":'16'
		},
		"data":[]
	}
	
	data['level_data']={}
	for v in data['temp']:
		if v['level'] not in data['level_data']:
			data['level_data'][v['level']]={"rate":0,'count':0}
		data['level_data'][v['level']]['level']=v['level']
		data['level_data'][v['level']]['count']+=1
		data['level_data'][v['level']]['rate']=float(data['level_data'][v['level']]['count'])*100/float(data['count']['count'])
	#排序
	from collections import OrderedDict
	data['level_data']=OrderedDict(sorted(data['level_data'].items(), key=lambda t: t[0]))
	#chart
	max=0
	for k,v in data['level_data'].items():
		max=k
		data['chart']['data'].append({"label":str(v['level'])+'级',"value":v['count']})
	#流失到达率
	data['total']=data['count']['count']
	sum=data['count']['count']
	for i in range(0,max+1):
		if i not in data['level_data']:
			data['level_data'][i]={"rate":0,'count':0}
		if i+1 not in data['level_data']:
			data['level_data'][i+1]={"rate":0,'count':0}
		data['level_data'][i]['base']=sum
		sum-=data['level_data'][i]['count']
		data['level_data'][i]['reach']=sum
		data['level_data'][i+1]['base']=sum
		data['level_data'][i]['loss_rate']=float(data['level_data'][i]['count'])*100/float(data['level_data'][i]['base'])
		data['level_data'][i]['reach_rate']=float(data['level_data'][i]['reach'])*100/float(data['level_data'][i]['base'])
			
	data['level_data']=OrderedDict(sorted(data['level_data'].items(), key=lambda t: t[0]))
	import json
	data['chart']=json.dumps(data['chart'])
	data['servers']=getAll()
	return data

#查看老用户登录数据
def checkOldRoleLogin():
	if not user.inGroup("operate"):return user.ban()
	data={}
	import time,tool
	me.S['P']['date_start']=me.S['P'].get('date_start',tool.date(int(body.now())))
	me.S['P']['date_end']=me.S['P'].get('date_end',tool.date(int(body.now())))
	me.S['P']['all']=me.S['P'].get('all','')
	
	msg={
		"memory":"server:%s"%(me.S['A']['server']),
		"model":model.info('login')['name'],
		"field":'%s,date_format(%s,"%%Y-%%m-%%d") as date'%(model.info('login')['map']['key_role']['field'],model.info('login')['map']['spliter']['field']),
		"filter":'date(%s) between "%s" and "%s"'%(model.info('login')['map']['spliter']['field'],me.S['P']['date_start'],me.S['P']['date_end']),
		"join":{
			"model":"%s"%(model.info('role')['name']),
			"key":"%s-%s"%(model.info('login')['map']['key_role']['field'],model.info('role')['map']['key_login']['field']),
			"field":'sum(1) as login_num,sum(if(date=date(%s),1,0)) as new_role_login_num'%(model.info('role')['map']['create_time']['field']),
			"byname":"role_data",
			"option":{"group":"date"}
		}
	}
	#single
	if me.S['P']['all']=="":
		temp=memory.get("recall",msg)
		data['data']=temp
	else:
		del msg['memory']
		dates=tool.getDateRange(me.S['P']['date_start'],me.S['P']['date_end'])
		data['data']=tool.Dict()
		t=recallInAll(msg)
		for v in dates:
			data['data'][v]={"date":v,"login_num":0,"new_role_login_num":0}
		for v in t:
			data['data'][v['date']]['login_num']+=v['login_num']
			data['data'][v['date']]['new_role_login_num']+=v['new_role_login_num']
		data['data']=data['data'].values()
	return data

#查看注册留存
def checkRegisterKeep():
	if not user.inGroup("operate"):return user.ban()
	data={}
	import time,tool
	me.S['P']['date_start']=me.S['P'].get('date_start',tool.date(int(body.now())))
	me.S['P']['date_end']=me.S['P'].get('date_end',tool.date(int(body.now())))
	me.S['P']['all']=me.S['P'].get('all','')
	#pf
	me.S['P']['pf']=me.S['P'].get('pf','all')
	pf=""
	if me.S['P']['pf']!="all":
		pf=' and %s="%s"'%(model.info('connect')["map"]["pf"]['field'],me.S['P']['pf'])
		
	#get connect info
	if me.S['P']['date_start']==me.S['P']['date_end']: #当天每小时详细情况
		msg={
			"model":model.info('connect')['name'],
			"field":'date_format(%s,"%%Y-%%m-%%d %%H") as date,sum(1) as connect_num,sum(if(%s>0,1,0)) as R_num,sum(if(%s>0,1,0)) as player_num'%(model.info('connect')['map']['spliter']['field'],model.info('connect')['map']['request_create']['field'],model.info('connect')['map']['first_operate']['field']),
			"filter":'date(%s) between "%s" and "%s"%s'%(model.info('connect')['map']['spliter']['field'],me.S['P']['date_start'],me.S['P']['date_end'],pf),
			"option":{"group":"date"}
		}
		#single server
		if me.S['P']['all']=="":
			msg['memory']='server:%s' % me.S['A']['server']
			temp=model.get({
				"day":msg
			})
		#all server
		else:
			temp={'day':{}}
			t=recallInAll(msg)
			for v in t:
				if v['date'] not in temp['day']:
					temp['day'][v['date']]=v
				else:
					temp['day'][v['date']]['connect_num']+=v['connect_num']
					temp['day'][v['date']]['R_num']+=v['R_num']
					temp['day'][v['date']]['player_num']+=v['player_num']
			temp['day']=temp['day'].values()
		
		data['data_day']=[]
		for v in temp['day']:
			v['role_lost_rate']=100
			if v['connect_num']>0:
				v['role_lost_rate']=100-float(v['R_num'])*100/float(v['connect_num'])
			v['player_lost_rate']=100
			if v['R_num']>0:
				v['player_lost_rate']=100-float(v['player_num'])*100/float(v['R_num'])
			data['data_day'].append(v)
		del temp['day']
	# else:
	msg={
		"model":model.info('connect')['name'],
		"field":'date_format(%s,"%%Y-%%m-%%d") as date,sum(1) as connect_num,sum(if(%s>0,1,0)) as R_num,sum(if(%s>0,1,0)) as player_num'%(model.info('connect')['map']['spliter']['field'],model.info('connect')['map']['request_create']['field'],model.info('connect')['map']['first_operate']['field']),
		"filter":'date(%s) between "%s" and "%s"%s'%(model.info('connect')['map']['spliter']['field'],me.S['P']['date_start'],me.S['P']['date_end'],pf),
		"option":{"group":"date"}
	}
	#single server
	if me.S['P']['all']=="":
		msg['memory']='server:%s' % me.S['A']['server']
		temp=model.get({
			"temp":msg
		})
	#all server
	else:
		t=recallInAll(msg)
		temp={'temp':{}}
		for v in t:
			if v['date'] not in temp['temp']:
				temp['temp'][v['date']]=v
			else:
				temp['temp'][v['date']]['connect_num']+=v['connect_num']
				temp['temp'][v['date']]['R_num']+=v['R_num']
				temp['temp'][v['date']]['player_num']+=v['player_num']
		temp['temp']=temp['temp'].values()
	
	data['data']=[]
	for v in temp['temp']:
		v['role_lost_rate']=100
		if v['connect_num']>0:
			v['role_lost_rate']=100-float(v['R_num'])*100/float(v['connect_num'])
		v['player_loat_rate']=100
		if v['R_num']>0:
			v['player_lost_rate']=100-float(v['player_num'])*100/float(v['R_num'])
		data['data'].append(v)
	del temp['temp']
	return data
def checkDaysKeep():
	if not user.inGroup("operate"):return user.ban()
	data={}
	import time,tool
	me.S['P']['date_start']=me.S['P'].get('date_start',tool.date(int(body.now())))
	me.S['P']['date_end']=me.S['P'].get('date_end',tool.date(int(body.now())))
	me.S['P']['all']=me.S['P'].get('all','')
	#pf
	me.S['P']['pf']=me.S['P'].get('pf','all')
	#N天留存
	data['data']=[]
	data['temp']=game.act()
	for v in data['temp']:
		v['one_rate']=float(v['one'])*100/float(v['count'])
		v['two_rate']=float(v['two'])*100/float(v['count'])
		v['three_rate']=float(v['three'])*100/float(v['count'])
		v['four_rate']=float(v['four'])*100/float(v['count'])
		v['five_rate']=float(v['five'])*100/float(v['count'])
		v['six_rate']=float(v['six'])*100/float(v['count'])
		v['seven_rate']=float(v['seven'])*100/float(v['count'])
		v['fourteen_rate']=float(v['fourteen'])*100/float(v['count'])
		v['thirty_rate']=float(v['thirty'])*100/float(v['count'])
		data['data'].append(v)
	return data

def checkLostBack():
	data={}
	import time,tool
	me.S['P']['date_start']=me.S['P'].get('date_start',tool.date(int(body.now())))
	me.S['P']['date_end']=me.S['P'].get('date_end',tool.date(int(body.now())))
	#找出当前服指定日期范围内创建的所有帐号
	temp=memory.get("recall",{
		"memory":"server:%s"%(me.S['A']['server']),
		"model":model.info('role')['name'],
		"key":"account",
		"field":"%s as account,%s as create_time"%(model.info('login')['map']['account_id']['field'],model.info('login')['map']['create_time']['field']),
		"filter":'%s between "%s" and "%s"'%(model.info('login')['map']['create_time']['field'],me.S['P']['date_start'],me.S['P']['date_end'])
	})
	#找出此部分帐户在其他服最后登录时间
	accounts='"%s"'%('","'.join(temp.keys()))
	logins=game.act({"accounts":accounts})
	#找出回流用户：在此服新创建帐号距其他服最后登录时间大于7天的帐号
	data['data']={}
	backs=[]
	for v in logins:
		if tool.strtotime(temp[v['account']]['create_time'])-tool.strtotime(v['last_login_time'])>=86400*7:
			backs.append(v['account'])
	#获取回流用户付费等信息
	t=memory.get("recall",{
		"filter":'%s in ("%s")'%(model.info('charge')['map']['account']['field'],'","'.join(backs))
	})
	return data
	
def getAll(msg=None):
	data={}
	if not msg:msg={}
	
	msg['operator']=msg.get('operator',me.S['A'].get('operator',0))
	msg['game']=msg.get('game',me.S['A'].get('game',0))
	
	if str(msg['operator'])!="0" and str(msg['game'])!="0":
		#cache key
		key="%s_%s_server-name"%(me.S['A']['game'],me.S['A']['operator'])
		data=cache.get(key)
		if not data:
			#from interface
			data=me.post("server/getAll")
			from collections import OrderedDict
			data=OrderedDict(sorted(data.items(), key=lambda t: int(t[0])))
			t=tool.Dict()
			#key to int
			for k,v in data.items():
				t[int(k)]=v
			cache.set(key,t)
	else:
		print "%s:%s"%(str(msg['operator']),str(msg['game']))
	return data

def getProcess():
	data={}
	from Integration.Help import WorldHelp
	for pkey,p in WorldHelp.GetProcess().iteritems():
		if not p.has_logic():
			continue
		data[pkey]={}
		data[pkey]['name']=p.get_name()
	import collections
	data=collections.OrderedDict(sorted(data.items(),key = lambda t:t[0].replace('GHL','')))
	return data
	
#check onlin data		
def checkOnline():
	#check user group
	if not user.inGroup("operate"):return user.ban()
	data={}
	import time,tool
	#default date
	me.S['P']['date']=me.S['P'].get('date',tool.date(int(body.now())))
	me.S['P']['all']=me.S['P'].get('all','')
	if me.S['P']['date']:
		data=game.act()
		data['chart']={}
		data['chart']['chart']={
			"caption":"【%s】在线人数"%getAll().get(me.S["A"]['server'],{"value":me.S["A"]['server']})["value"],
			"subcaption":"5分钟统计一次",
			"numdivlines":"9",
			"linethickness":"2",
			"anchorradius":"3",
			"anchorbgalpha":"50",
			"numvdivlines":"24",
			"showalternatevgridcolor":"1",
			"alternatevgridalpha":"3",
			"animation":"0",
			"valueposition":"above",
			"baseFontSize":'12'
		}
		category=[]
		onlines=[]
		ips=[]
		for v in data['data']:
			category.append({"label":':'.join(v['time'].split(' ')[1].split(':')[:2])})
			onlines.append({"value":v['roles']})
			ips.append({"value":v['ips']})
		data['chart']['categories']=[{"category":category}]
		data['chart']['dataset']=[{
				"seriesname":"在线人数",
				"color":"ff0000",
				"showvalues":"1",
				"data":onlines
			},{
				"seriesname":"在线IP数",
				"color":"0000ff",
				"showvalues":"1",
				"valueposition":"below",
				"data":ips
			}
		]
		import json
		data['chart']=json.dumps(data['chart'])
	return data
#only longqi
def check3DaysOnline():
	if not user.inGroup("operate"):return user.ban()
	import time
	me.S['P']['date_end']=me.S['P'].get('date_end',tool.date(body.now()))
	last_day=tool.date(tool.strtotime(me.S['P']['date_end'],"%Y-%m-%d")-86400)
	last_week_day=tool.date(tool.strtotime(me.S['P']['date_end'],"%Y-%m-%d")-86400*7)
	me.S['P']['server']=me.S['P'].get('server',me.S['A']['server'])
	#cache
	key="%s_%s_server_check3DaysOnline_%s"%(me.S['A']['game'],me.S['A']['operator'],me.S['P']['date_end'])
	data=cache.get(key)
	
	if not data:
		data={}
		#common config
		data_msg={
			"memory":"server:%s"%me.S['P']['server'],
			"model":model.info('online')["name"],
			"field":'date_format(FROM_UNIXTIME(UNIX_TIMESTAMP(%s)-UNIX_TIMESTAMP(%s)%%(5*60)),"%%H:%%i") as date,%s as roles'%(
				model.info('online')["map"]["spliter"]['field'],
				model.info('online')["map"]["spliter"]['field'],
				model.info('online')['map']['roles']['field']
			),
			"filter":'DATE_FORMAT(%s,"%%Y-%%m-%%d") in ("%s")'%(
				model.info('online')["map"]["spliter"]['field'],
				me.S['P']['date_end']
			),
			"key":"date",
			"option":{"order":"date,asc","group":"date"}
		}
		import copy as CP
		last_day_msg=CP.deepcopy(data_msg)
		last_week_day_msg=CP.deepcopy(data_msg)
		last_day_msg['filter']='DATE_FORMAT(%s,"%%Y-%%m-%%d") in ("%s")'%(
			model.info('online')["map"]["spliter"]['field'],
			last_day
		)
		last_week_day_msg['filter']='DATE_FORMAT(%s,"%%Y-%%m-%%d") in ("%s")'%(
			model.info('online')["map"]["spliter"]['field'],
			last_week_day
		)
		#single
		data=model.get({
			"data":data_msg,
			"last_day_data":last_day_msg,
			"last_week_day_data":last_week_day_msg
		})
		
		chart_data={"data":[],"last_day_data":[],"last_week_day_data":[]}
		category=tool.getDateRange(me.S['P']['date_end'],me.S['P']['date_end'],300,"%H:%M")
		for v in category:
			for kk,vv in data.items():
				if v in vv:
					chart_data[kk].append({"value":"%s"%vv[v]['roles']})
				else:
					chart_data[kk].append({"value":"0"})
		#chart
		data['chart']={}
		data['chart']['chart']={
			"caption":'【%s】在线人数'%(getAll().get(me.S['P']['server'],{"value":me.S['P']['server']})['value']),
			"subcaption":"实时数据",
			"numdivlines":"9",
			"linethickness":"2",
			"anchorradius":"3",
			"anchorbgalpha":"50",
			"numvdivlines":"24",
			"showalternatevgridcolor":"1",
			"alternatevgridalpha":"3",
			"animation":"0",
			"valueposition":"above",
			"baseFontSize":'12'
		};
		data['chart']['categories']=[{"category":[]}]
		for v in category:
			data['chart']['categories'][0]["category"].append({"label":v})
		
		data['chart']['dataset']=[]
		colors={"data":"00ff00","last_day_data":"ff0000","last_week_day_data":"0000ff"}
		titles={"data":"当天在线","last_day_data":"昨天在线","last_week_day_data":"上周同天在线"}
		for k,v in chart_data.items():
			data['chart']['dataset'].append({
				"seriesname":titles[k],
				"color":colors[k],
				"showvalues":"1",
				"data":v
			})
		del data['last_week_day_data']
		del data['last_day_data']
		import json
		data['chart']=json.dumps(data['chart'])
		cache.set(key,data,60)
	else:
		data['tips']="你正在查看缓存数据，每1分钟缓存一次，缓存失效时间:%s"%(cache.getExpireTime(key))
	return data
#only longqi
def check3DaysReg():
	if not user.inGroup("operate"):return user.ban()
	import time
	me.S['P']['date_end']=me.S['P'].get('date_end',tool.date(body.now()))
	last_day=tool.date(tool.strtotime(me.S['P']['date_end'],"%Y-%m-%d")-86400)
	last_week_day=tool.date(tool.strtotime(me.S['P']['date_end'],"%Y-%m-%d")-86400*7)
	me.S['P']['server']=me.S['P'].get('server',me.S['A']['server'])
	#cache
	key="%s_%s_server_check3DaysReg_%s"%(me.S['A']['game'],me.S['A']['operator'],me.S['P']['date_end'])
	data=cache.get(key)
	
	if not data:
		data={}
		#common config
		data_msg={
			"memory":"server:%s"%me.S['P']['server'],
			"model":model.info('role')["name"],
			"field":'date_format(FROM_UNIXTIME(UNIX_TIMESTAMP(%s)-UNIX_TIMESTAMP(%s)%%(5*60)),"%%H:%%i") as date,count(%s) as roles'%(
				model.info('role')["map"]["create_time"]['field'],
				model.info('role')["map"]["create_time"]['field'],
				model.info('role')['map']['id']['field']
			),
			"filter":'DATE_FORMAT(%s,"%%Y-%%m-%%d") in ("%s")'%(
				model.info('role')["map"]["create_time"]['field'],
				me.S['P']['date_end']
			),
			"key":"date",
			"option":{"order":"date,asc","group":"date"}
		}
		import copy as CP
		last_day_msg=CP.deepcopy(data_msg)
		last_week_day_msg=CP.deepcopy(data_msg)
		last_day_msg['filter']='DATE_FORMAT(%s,"%%Y-%%m-%%d") in ("%s")'%(
			model.info('role')["map"]["create_time"]['field'],
			last_day
		)
		last_week_day_msg['filter']='DATE_FORMAT(%s,"%%Y-%%m-%%d") in ("%s")'%(
			model.info('role')["map"]["create_time"]['field'],
			last_week_day
		)
		#single
		data=model.get({
			"data":data_msg,
			"last_day_data":last_day_msg,
			"last_week_day_data":last_week_day_msg
		})
		
		chart_data={"data":[],"last_day_data":[],"last_week_day_data":[]}
		category=tool.getDateRange(me.S['P']['date_end'],me.S['P']['date_end'],300,"%H:%M")
		for v in category:
			for kk,vv in data.items():
				if v in vv:
					chart_data[kk].append({"value":"%s"%vv[v]['roles']})
				else:
					chart_data[kk].append({"value":"0"})
		#chart
		data['chart']={}
		data['chart']['chart']={
			"caption":'【%s】注册人数'%(getAll().get(me.S['P']['server'],{"value":me.S['P']['server']})['value']),
			"subcaption":"实时数据",
			"numdivlines":"9",
			"linethickness":"2",
			"anchorradius":"3",
			"anchorbgalpha":"50",
			"numvdivlines":"24",
			"showalternatevgridcolor":"1",
			"alternatevgridalpha":"3",
			"animation":"0",
			"valueposition":"above",
			"baseFontSize":'12'
		};
		data['chart']['categories']=[{"category":[]}]
		for v in category:
			data['chart']['categories'][0]["category"].append({"label":v})
		
		data['chart']['dataset']=[]
		colors={"data":"00ff00","last_day_data":"ff0000","last_week_day_data":"0000ff"}
		titles={"data":"当天注册","last_day_data":"昨天注册","last_week_day_data":"上周同天注册"}
		for k,v in chart_data.items():
			data['chart']['dataset'].append({
				"seriesname":titles[k],
				"color":colors[k],
				"showvalues":"1",
				"data":v
			})
		del data['last_week_day_data']
		del data['last_day_data']
		import json
		data['chart']=json.dumps(data['chart'])
		cache.set(key,data,60)
	else:
		data['tips']="你正在查看缓存数据，每1分钟缓存一次，缓存失效时间:%s"%(cache.getExpireTime(key))
	return data
#仅支持山海
def checkOnlineSummary():
	if not user.inGroup("operate"):return user.ban()
	data={}
	me.S['P']['date']=me.S['P'].get('date',"")
	if me.S['P']['date']!="":
		data=game.act()
	return data
def guide():
	if not user.inGroup("host"):return user.ban()
	msg={"filter":{}}
	if 'game' in me.S['A']:
		msg['filter']['game']=me.S['A']['game']
	if 'operator' in me.S['A']:
		msg['filter']['operator_id']=me.S['A']['operator']
	return model.guide(msg)
	
def listNotice():
	if not user.inGroup("operate"):return user.ban()
	data={}
	#edit listed notice
	if 'step' in me.S['P']:
		me.S["P"]['render']=me.S['P'].get('render','js')
		me.S["P"]['step']=me.S["P"].get('step','')
		if me.S["P"]['step']=='changeInterval':
			if me.S["P"].get('id','')!='':
				me.S["P"]['interval']=int(me.S["P"].get('interval',0))
				done=me.M("remember",{"action":"edit","model":"notice","data":{"interval_time":me.S["P"]['interval']},"filter":"nid in (%s)"%me.S["P"]['id']})
				if done:
					data['result']="true"
		#delete
		if me.S["P"]['step']=='changeVisible':
			if me.S["P"].get('id','')!='':
				memory.get("forget",{"model":"notice","filter":"nid in (%s)"%me.S["P"]['id']})
				data['result']="true"
		if me.S["P"]['render']=='js':
			import json
			data['response']=json.dumps(data)
		return data
	return data

def sendCommand(pkey,m):
	from Integration.Help import Concurrent
	return Concurrent.GMCommand(pkey,m)
	
def getLast():
	if 'operator' not in me.S['A']:
		return 0
	all=getAll()
	last=0
	for k,v in all.items():
		if k>last:
			last=k
	return last
#新进用户数据查看
def checkNewIn():
	if not user.inGroup("operate"):return user.ban()
	me.S['P']['date_start']=me.S['P'].get('date_start','')
	me.S['P']['date_end']=me.S['P'].get('date_end','')
	me.S['P']['parallel']=me.S['P'].get('parallel','')
	me.S['P']['update']=me.S['P'].get('update','')
	me.S['P']['stats']=me.S['P'].getlist('stats')
	data={}
	if me.S['P']['date_start']:
		#cache
		key="%s_%s_server-checkNewIn-%s-%s-%s"%(me.S['A']['game'],me.S['A']['operator'],me.S['P']['date_start'],me.S['P']['date_end'],'-'.join(me.S['P']['stats']))
		data=cache.get(key)
		if not data or me.S['P']['update']!='':
			data={"data":{}}
			#并行开关
			parallel={"parallel":False}
			if me.S['P']['parallel']!="":
				parallel["parallel"]=True
				
			#找出指定时间范围内在全服注册的所有帐号
			msg={
				"model":model.info('connect')["name"],
				"field":'%s as account'%(model.info('connect')["map"]["account_id"]['field']),
				"filter":'date(%s) between "%s" and "%s"'%(model.info('connect')["map"]["spliter"]['field'],me.S['P']['date_start'],me.S['P']['date_end'])
			}
			temp=recallInAll(msg,parallel);
			allIn=[]
			for v in temp:
				allIn.append(v['account'])
			#本月新进用户
			allIn={}.fromkeys(allIn).keys()
			#data['data']=",".join(allIn)
			#注册时间在指定日期范围前的同一帐号
			msg={
				"sql":'select %s as account from %s where '%(model.info('connect')["map"]["account_id"]['field'],model.info('connect')["name"])
			}
			msg['sql']+='%s in ("%s") and %s<"%s"'%(model.info('connect')["map"]["account_id"]['field'],'","'.join(allIn),model.info('connect')["map"]["spliter"]['field'],me.S['P']['date_start'])
			#data['data']=msg['filter']
			t=queryInAll(msg,parallel)
			#本月老用户
			oldIn=[]
			for v in t:
				oldIn.append(v['account'])
			oldIn={}.fromkeys(oldIn).keys()
			
			newIn=list(set(allIn)-set(oldIn))
			data['new_in']=len(newIn)
			#新进用户付费
			if 'pay' in me.S['P']['stats']: 
				msg={
					"sql":'select %s as account,%s as pay_num,%s as pay_sum from %s as charge where %s in ("%s") and %s not in ("","billno") and date(%s) between "%s" and "%s" group by account'%(
						model.info('charge')["map"]["account_id"]['field'],
						model.info('charge')["map"]["pay_num"]['field'],
						model.info('charge')["map"]["pay_sum"]['field'],
						model.info('charge')["name"],
						model.info('charge')["map"]["account_id"]['field'],
						'","'.join(newIn),
						model.info('charge')["map"]["id"]['field'],
						model.info('charge')["map"]["spliter"]['field'],
						me.S['P']['date_start'],
						me.S['P']['date_end']
					)
				}
				t=queryInAll(msg,parallel)
				stated=[]
				#init pay num and pay sum
				data['pay_sum']=0
				for v in t:
					try:
						data['pay_sum']+=v['pay_sum']
						stated.append(v['account'])
					except:
						print v
						traceback.print_exc()
						break
				data['pay_num']=len({}.fromkeys(stated).keys())
				stated=[]
			
			#非新进用户活跃
			if 'active_old' in me.S['P']['stats']:
				stated=[]
				
				msg='select role.%s as account from (select %s from %s where date(%s) between "%s" and "%s" group by %s) as login inner join %s as role on role.%s=login.%s and role.%s not in ("%s")'%(
					model.info('role')["map"]["account"]['field'],
					
					model.info('login')["map"]["key_role"]['field'],
					model.info('login')["name"],
					model.info('login')["map"]["spliter"]['field'],
					me.S['P']['date_start'],
					me.S['P']['date_end'],
					model.info('login')["map"]["key_role"]['field'],
					
					model.info('role')["name"],
					model.info('role')["map"]["key_login"]['field'],
					model.info('login')["map"]["key_role"]['field'],
					model.info('role')["map"]["account"]['field'],
					'","'.join(newIn)
				)
				t=queryInAll({"sql":msg},parallel)
				data['active_old']=[]
				for v in t:
					data['active_old'].append(v['account'])
				data['active_old']=len({}.fromkeys(data['active_old']).keys())
				stated=[]
			cache.set(key,data,86400)
	#统计项目
	data['stats']={"pay":"新进用户付费","active_old":"非新进用户活跃"}
	return data

def checkRoll():
	if not user.inGroup("operate"):return user.ban()
	data={"data":{}}
	me.S['P']['date_start']=me.S['P'].get('date_start','')
	me.S['P']['date_end']=me.S['P'].get('date_end','')
	
	#并行开关
	me.S['P']['parallel']=me.S['P'].get('parallel','')
	parallel={"parallel":False,"slave":True}
	if me.S['P']['parallel']!="":
		parallel["parallel"]=True

	if me.S['P']['date_start']:
		#找出指定时间范围内在目标服注册的所有帐号及时间
		temp=memory.get("recall",{
			"memory":"server:%s"%(me.S['A']['server']),
			"model":model.info('role')["name"],
			"field":'%s as account,%s as register_time,date_format(%s,"%%Y-%%m-%%d") as register_date'%(model.info('role')["map"]["account"]['field'],model.info('role')["map"]["create_time"]['field'],model.info('role')["map"]["create_time"]['field']),
			"key":"account",
			"filter":'date(%s) between "%s" and "%s"'%(model.info('role')["map"]["create_time"]['field'],me.S['P']['date_start'],me.S['P']['date_end']),
			"slave":True
		});
		#找出其他服这些帐号的注册记录
		msg={
			"model":model.info('role')["name"],
			"field":'%s as account,%s as register_time'%(model.info('role')["map"]["account"]['field'],model.info('role')["map"]["create_time"]['field']),
			"filter":'%s in ("%s")'%(model.info('role')["map"]["account"]['field'],'","'.join(temp.keys()))
		}
		parallel["servers"]=getAll().keys()
		parallel['servers'].remove(int(me.S['A']['server']))
		t=recallInAll(msg,parallel)
		
		#滚服帐号
		roll_accounts=[]
		#获取滚服帐号
		for v in t:
			try:
				if temp[v['account']]['register_time']>v['register_time']:
					if temp[v['account']]['register_date'] not in data['data']:	
						data['data'][temp[v['account']]['register_date']]={"num_roll":0,"num_pay":0,"sum_pay":0,"new_num_pay":0,"new_sum_pay":0,"old_num_pay":0,"old_sum_pay":0}
					data['data'][temp[v['account']]['register_date']]['num_roll']+=1
					#roll
					if not v['account'] in roll_accounts:
						roll_accounts.append(v['account'])
			except:
				traceback.print_exc()
				pass
		#非滚服新用户
		not_roll_new_accounts=list(set(temp.keys())-set(roll_accounts))
		#get pay
		msg={
			"memory":"server:%s"%(me.S['A']['server']),
			"model":"%s"%(model.info('charge')["name"]),
			"field":'%s as account,date_format(%s,"%%Y-%%m-%%d") as date,%s as pay_sum'%(model.info('role')["map"]["account"]['field'],model.info('charge')["map"]["spliter"]['field'],model.info('charge')['map']['pay_sum']['field']),
			"filter":'date(%s) between "%s" and "%s" and %s!="" and %s!="billno"'%(
				model.info('charge')["map"]["spliter"]['field'],
				me.S['P']['date_start'],
				me.S['P']['date_end'],
				model.info('charge')["map"]["id"]['field'],
				model.info('charge')["map"]["id"]['field']
			),
			"option":{"group":"date,account"},
			"slave":True
		}
		tem=memory.get("recall",msg)
		for v in tem:
			if v['date'] not in data['data']:	
				data['data'][v['date']]={"num_roll":0,"num_pay":0,"sum_pay":0,"new_num_pay":0,"new_sum_pay":0,"old_num_pay":0,"old_sum_pay":0}
			#滚服付费
			if v['account'] in roll_accounts:
				if v['date']==temp[v['account']]['register_date']:
					data['data'][v['date']]['num_pay']+=1
					data['data'][v['date']]['sum_pay']+=v['pay_sum']
				else:
					data['data'][v['date']]['old_num_pay']+=1
					data['data'][v['date']]['old_sum_pay']+=v['pay_sum']
				# data['data'][v['date']]['num_pay_after_roll']+=1
				# data['data'][v['date']]['sum_pay_after_roll']+=v['pay_sum']
			elif v['account'] in not_roll_new_accounts:
				#新用户付费
				if v['date']==temp[v['account']]['register_date']:#如果是范围内某于注册，为该天新增付费
					data['data'][v['date']]['new_num_pay']+=1
					data['data'][v['date']]['new_sum_pay']+=v['pay_sum']
				else:#必然是留存付费
					data['data'][v['date']]['old_num_pay']+=1
					data['data'][v['date']]['old_sum_pay']+=v['pay_sum']
			else:#非指定范围内注册帐号，在此范围内付费的，必然是之前注册的留存付费
				#留存用户付费
				data['data'][v['date']]['old_num_pay']+=1
				data['data'][v['date']]['old_sum_pay']+=v['pay_sum']
		from collections import OrderedDict
		data['data']=OrderedDict(sorted(data['data'].items(), key=lambda t: t[0]))
	#default
	if me.S['P']['date_start']=='':
		me.S['P']['date_start']=me.S['P'].get('date_start',tool.date(body.now()-86400))
	if me.S['P']['date_end']=='':
		me.S['P']['date_end']=me.S['P'].get('date_end',tool.date(body.now()-86400))
	return data

def getInfo(id=None):
	data={}
	if not id:id=me.S['A']['server']
	key="%s_%s_server-info"%(me.S['A']['game'],me.S['A']['operator'])
	data=cache.get(key)
	if not data:
		data=me.post('server/getInfo')
		cache.set(key,data)
	data=data.get(id,{})
	return data
	
def getMemoryInfo(id,prefix_type="data",slave=None):
	if not slave:slave=False
	data={}
	id=int(id)
	key="%s_%s_memory-info"%(me.S['A']['game'],me.S['A']['operator'])
	
	#memory prefix
	temp=memory.get("recall",{"one":True,"model":"game","field":"slave_switch,data_prefix,log_prefix","filter":{"byname":me.S['A']['game']}})
	name_prefix=temp['%s_prefix'%prefix_type]
	#game operator not in memory info get
	
	#slave
	options={}
	if temp['slave_switch']==1 or slave:
		key+='-slave'
		options['slave']="true"
	
	memory_info=cache.get(key)
	if not memory_info:
		if int(me.S['A']['operator']) in [1]:
			temp=me.post("server/getAllMemoryInfo",options)
		else:
			temp=memory.get("recall",{"model":"servers","key":"zone_id","field":"zone_id,mysql_ip,mysql_port,mysql_user,mysql_pwd","filter":{"operator_id":me.S['A']['operator'],"game":me.S['A']['game']}})
		memory_info=temp
		cache.set(key,memory_info)
	try:
		memory_info=memory_info.get(id,memory_info.get(str(id),{}))
		data={"name":"%s%s"%(name_prefix,id),"host":memory_info["mysql_ip"],"port":memory_info["mysql_port"],"user":memory_info["mysql_user"],"key":memory_info["mysql_pwd"]}
	except:
		print "Get Memory Info Error:",me.S['A']['game'],id,prefix_type,memory_info
		traceback.print_exc()
	return data

def getMemoryPrefix(prefix_type="data"):
	data=""
	#memory prefix
	temp=memory.get("recall",{"one":True,"model":"game","field":"slave_switch,data_prefix,log_prefix","filter":{"byname":me.S['A']['game']}})
	data=temp['%s_prefix'%prefix_type]
	return data
	
def recallInAll(m,option=None):
	data=[]
	if option==None:option={}
	#servers
	if 'servers' in option:
		servers=option['servers']
	else:
		servers=getAll().keys()
	msg=[]
	import copy as CP
	if option.get("parallel",False)==True:
		if me.S['user']['name']!="james":return []
		for v in servers:
			mmsg=CP.deepcopy(m)
			mmsg['memory']="server:%s"%v
			#need server key
			if option.get('server_field',False)==True:
				mmsg['field']+=',%s as server'%(v)
			msg.append(("recall",mmsg))
		temp=model.parallel(memory.getParallel,msg)
		for v in temp:
			for vv in v:
				data.append(vv)
	else:
		for v in servers:
			mmsg=CP.deepcopy(m)
			mmsg['memory']="server:%s"%v
			#need server key
			if option.get('server_field',False)==True:
				mmsg['field']+=',%s as server'%(v)
			try:
				temp=memory.get("recall",mmsg)
				for vv in temp:
					data.append(vv)
			except:
				traceback.print_exc()
				pass
	return data
def queryInAll(m,option=None):
	data=[]
	if option==None:option={}
	if 'servers' in option:
		servers=option['servers']
	else:
		servers=getAll().keys()
	msg=[]
	import copy as CP
	if option.get("parallel",False)==True:
		if me.S['user']['name']!="james":return []
		for v in servers:
			mmsg=CP.deepcopy(m)
			mmsg['memory']="server:%s"%v
			#need server key
			if option.get('server_field',False)==True:
				mmsg['sql']=mmsg['sql'].replace('{server_field}','%s as server'%(v))
			msg.append(("query",mmsg))
		temp=model.parallel(memory.getParallel,msg)
		for v in temp:
			for vv in v:
				data.append(vv)
	else:
		for v in servers:
			#print 'now server:%s'%v
			mmsg=CP.deepcopy(m)
			mmsg['memory']="server:%s"%v
			#need server key
			if option.get('server_field',False)==True:
				mmsg['sql']=mmsg['sql'].replace('{server_field}','%s as server'%(v))
			try:
				temp=memory.get("query",mmsg)
				for vv in temp:
					data.append(vv)
			except:
				traceback.print_exc()
				pass
	return data
#locate server
def locate():
	data=me.S['A'].get('server',0)
	if 'user' in me.S and 'operator' in me.S['A']:
		if 'server' in me.S['G']:
			servers=getAll()
			if int(me.S['G']['server']) in servers:
				data=me.S['G']['server']
	me.S['A']['server']=data

#from
#longqi
def checkConnectFrom():
	if not user.inGroup("operate"):return user.ban()
	data={}
	#特定时间范围
	me.S['P']['date_start']=me.S['P'].get('date_start',tool.date(body.now()))
	me.S['P']['date_end']=me.S['P'].get('date_end',tool.date(body.now()))
	me.S['P']['from_1']=me.S['P'].get('from_1',"qzone")
	me.S['P']['from_2']=me.S['P'].get('from_2',"")
	me.S['P']['from_3']=me.S['P'].get('from_3',"")
	me.S['P']['all']=me.S['P'].get('all','')
	
	#from
	from_sql=""
	if me.S['P']['from_1']!="":
		from_sql+=' and from_1="%s"'%me.S['P']['from_1']
	if me.S['P']['from_2']!="":
		from_sql+=' and from_2="%s"'%me.S['P']['from_2']
	if me.S['P']['from_3']!="":
		from_sql+=' and from_3="%s"'%me.S['P']['from_3']
	if from_sql!="":from_sql="%s "%from_sql
	sql='select count(*) as count,date_format(connect_time,"%%Y-%%m-%%d") as date from connect_info where date_format(connect_time,"%%Y-%%m-%%d") between "%s" and "%s"%s group by date'%(
		me.S['P']['date_start'],
		me.S['P']['date_end'],
		from_sql
	)
	#single server
	if me.S['P']['all']=="":
		data["data"]=memory.get("query",{"sql":sql,"memory":"server:%s"%(me.S['A']['server'])})
	else:
		dates=tool.getDateRange(me.S['P']['date_start'],me.S['P']['date_end'])
		data['data']=tool.Dict()
		t=queryInAll({"sql":sql})
		for v in dates:
			data['data'][v]={"date":v,"count":0}
		for v in t:
			data['data'][v['date']]['count']+=v['count']
		data['data']=data['data'].values()
	return data

def checkOnlineRange():
	if not user.inGroup("operate"):return user.ban()
	me.S['P']['date_start']=me.S['P'].get('date_start',tool.date(body.now()))
	me.S['P']['date_end']=me.S['P'].get('date_end',tool.date(body.now()))
	me.S['P']['range']=me.S['P'].get('range',"1000,2000")
	
	data={}
	#logout
	sql='select role_id,"logout" as type,date_format(log_datetime,"%%Y-%%m-%%d %%H:%%i:%%s") as time from {table_field} where log_transaction=699 and log_event=30042 and date_format(log_datetime,"%%Y-%%m-%%d") between "%s" and "%s"'%(me.S['P']['date_start'],me.S['P']['date_end'])
	roles={}
	logout=memory.get("query",{"memory":"server:%s"%me.S['A']['server'],"sql":sql,"prefix_type":"log","merge":"log_value"})
	#login
	sql='select role_id,"login" as type,date_format(log_datetime,"%%Y-%%m-%%d %%H:%%i:%%s") as time from {table_field} where log_transaction=530 and log_event=30001 and date_format(log_datetime,"%%Y-%%m-%%d") between "%s" and "%s"'%(me.S['P']['date_start'],me.S['P']['date_end'])
	login=memory.get("query",{"memory":"server:%s"%me.S['A']['server'],"sql":sql,"prefix_type":"log","merge":"log_base"})
	for v in login:
		if v['role_id'] not in roles:
			roles[v['role_id']]=[]
		roles[v['role_id']].append(v)
	for v in logout:
		if v['role_id'] not in roles:
			roles[v['role_id']]=[]
		roles[v['role_id']].append(v)
	times=[]
	import operator
	for k,v in roles.items():
		time_sum=0#用户总在线
		t=0
		v.sort(key=operator.itemgetter("time"))
		for vv in v:
			if vv['type']=="login":
				t=tool.strtotime(vv['time'])
			else:#计算下线时长
				time_sum+=tool.strtotime(vv['time'])-t
		times.append(time_sum)
	data['data']=tool.rangeDatum(times,me.S['P']['range'])
	return data
			