# -*- coding:UTF-8 -*-
import traceback,time
import me,server,tool,role,user,memory,body,model,cache,word
def check():
	if not user.inGroup("operate"):return user.ban()
	me.S['P']['date_start']=me.S['P'].get('date_start',tool.monthRange())
	me.S['P']['date_end']=me.S['P'].get('date_end',tool.monthRange(False))
	me.S['P']['server']=me.S['P'].get('server',me.S['A']['server'])
	#pf
	me.S['P']['pf']=me.S['P'].get('pf','all')
	me.S['P']['parallel']=me.S['P'].get('parallel','')
	me.S['P']['count_repeat']=me.S['P'].get('count_repeat','')
	#cache
	key="%s_%s_charge_check_%s_%s_%s_%s"%(me.S['A']['game'],me.S['A']['operator'],me.S['P']['date_start'],me.S['P']['date_end'],me.S['P'].get('all',me.S['P']['server']),me.S['P']['pf'])
	data=cache.get(key)
	#全服开关
	me.S['P']['all']=me.S['P'].get('all','')
	
	if not data:
		data={}
		pf=""
		if me.S['P']['pf']!="all":
			pf=' and %s="%s"'%(model.info('charge')["map"]["pf"]['field'],me.S['P']['pf'])
		#common config
		msg_data={
			"memory":"server:%s"%me.S['P']['server'],
			"model":model.info('charge')["name"],
			"field":'date_format(%s,"%%Y-%%m-%%d") as date,%s as pay_num,%s as pay_times,%s*%s as pay_sum'%(
				model.info('charge')["map"]["spliter"]['field'],
				model.info('charge')['map']['pay_num']['field'],
				model.info('charge')['map']['pay_times']['field'],
				model.info('charge')['map']['pay_sum']['field'],
				body.config['currency_rate'][body.config["operator_currency"][int(me.S['A']['operator'])]]
			),
			"filter":'DATE_FORMAT(%s,"%%Y-%%m-%%d") between "%s" and "%s" and %s not in ("","billno")%s'%(
				model.info('charge')["map"]["spliter"]['field'],
				me.S['P']['date_start'],
				me.S['P']['date_end'],
				model.info('charge')["map"]["id"]['field'],
				pf
			),
			"option":{"order":"date,asc","group":"date"}
		}
		msg_sum={
			"memory":"server:%s"%me.S['P']['server'],
			"model":model.info('charge')["name"],
			"field":'%s as pay_num,%s as pay_times,%s*%s as pay_sum'%(
				model.info('charge')['map']['pay_num']['field'],
				model.info('charge')['map']['pay_times']['field'],
				model.info('charge')['map']['pay_sum']['field'],
				body.config['currency_rate'][body.config["operator_currency"][int(me.S['A']['operator'])]]
			),
			"filter":'DATE_FORMAT(%s,"%%Y-%%m-%%d") between "%s" and "%s" and %s not in ("","billno")%s'%(
				model.info('charge')["map"]["spliter"]['field'],
				me.S['P']['date_start'],
				me.S['P']['date_end'],
				model.info('charge')["map"]["id"]['field'],
				pf
			)
		}
		#single
		if me.S['P']['all']=="":
			data=model.get({
				"data":msg_data,
				"sum_all":msg_sum
			})
			data['sum_all']=data['sum_all'][0]
		#all server
		else:
			#并行开关
			parallel={"parallel":False}
			if me.S['P']['parallel']!="":
				parallel["parallel"]=True
			#charge from all server
			temp_data=server.recallInAll(msg_data,parallel)
			temp_sum=server.recallInAll(msg_sum,parallel)
			data['data']=tool.Dict()
			data['sum_all']=tool.Dict()
			for vv in temp_data:
				if vv['date'] not in data['data']:
					data['data'][vv['date']]={"date":vv['date'],"pay_num":vv['pay_num'],"pay_times":vv['pay_times'],"pay_sum":vv['pay_sum']}
				else:
					data['data'][vv['date']]['pay_num']+=vv['pay_num']
					data['data'][vv['date']]['pay_times']+=vv['pay_times']
					data['data'][vv['date']]['pay_sum']+=vv['pay_sum']
			data['data']=data['data'].values()
			
			#sum
			data['sum_all']={"pay_num":0,"pay_times":0,"pay_sum":0}
			for vv in temp_sum:
				if not vv['pay_sum']:continue
				data['sum_all']['pay_num']+=vv['pay_num']
				data['sum_all']['pay_times']+=vv['pay_times']
				data['sum_all']['pay_sum']+=vv['pay_sum']
			#去重充值人数
			data['sum_distinct_pay_num']=0
			if me.S["P"]["count_repeat"]!="":
				msg_sum.update({
					"field":'%s as account_id'%(
						model.info('charge')["map"]["account_id"]['field']
					),
					"option":{
						"group":"%s"%(
							model.info('charge')["map"]["account_id"]['field']
						)
					}
				})
				temp_num=server.recallInAll(msg_sum,parallel)
				data['sum_distinct_pay_num']=[]
				for v in temp_num:
					data['sum_distinct_pay_num'].append(v['account_id'])
					del v
				data['sum_distinct_pay_num']=len({}.fromkeys(data['sum_distinct_pay_num']).keys())
		#chart
		data['chart']={}
		data['chart']['chart']={
			"caption":'【%s】%s/%s'%(server.getAll().get(me.S['P']['server'],{"value":me.S['P']['server']})['value'],word.check("充值概况"),word.check(body.config['currency_name'][body.config["operator_currency"][int(me.S['A']['operator'])]])),
			"subcaption":word.check("实时数据"),
			"yaxisname": "%s/%s"%(word.check("充值总额"),word.check(body.config['currency_name'][body.config["operator_currency"][int(me.S['A']['operator'])]])),
			"xaxisname": word.check("日期"),
			"forceAxisLimits" : "1",
			"pixelsPerPoint": "0",
			"pixelsPerLabel": "30",
			"lineThickness": "1",
			"compactdatamode" : "1",
			"dataseparator" : "|",
			"labelHeight": "30",
			"theme": "fint",
			"bgAlpha":0
		};
		category=[]
		pay_sum=[]
		pay_num=[]
		for v in data['data']:
			category.append(v['date'])
			pay_sum.append("%s"%v['pay_sum'])
			pay_num.append("%s"%v['pay_num'])
		data['chart']['categories']=[{"category":'|'.join(category)}]
		data['chart']['dataset']=[{
				"seriesname":word.check("充值总额"),
				"showvalues":"1",
				"data":"|".join(pay_sum)
			},{
				"seriesname":word.check("充值人数"),
				"showvalues":"1",
				"valueposition":"below",
				"data":"|".join(pay_num)
			}
		]
		import json
		data['chart']=json.dumps(data['chart'])
		cache.set(key,data,60)
	else:
		data['tips']="%s:%s"%(word.check("你正在查看缓存数据，每1分钟缓存一次，缓存失效时间"),cache.getExpireTime(key))
	return data
def checkPayLogin():
	if not user.inGroup("operate"):return user.ban()
	me.S['P']['date_pay_start']=me.S['P'].get('date_pay_start',tool.date(body.now()))
	me.S['P']['date_pay_end']=me.S['P'].get('date_pay_end',tool.date(body.now()))
	me.S['P']['date_login_start']=me.S['P'].get('date_login_start',tool.date(body.now()))
	me.S['P']['date_login_end']=me.S['P'].get('date_login_end',tool.date(body.now()))
	sql='select count(distinct login.account) as `count` from (SELECT account FROM charge where date(dt) between "%s" and "%s" and billno not in ("","billno") GROUP BY account) AS role INNER JOIN login_info as login on role.account=login.account and date(login.login_day) between "%s" and "%s"'%(
		me.S['P']['date_pay_start'],
		me.S['P']['date_pay_end'],
		me.S['P']['date_login_start'],
		me.S['P']['date_login_end']
	)
	data={"count":memory.get("query",{"memory":"server:%s"%(me.S['A']['server']),"sql":sql,"one":True})['count']}
	return data
	
def checkNewAccountPay():
	if not user.inGroup("operate"):return user.ban()
	data={}
	me.S['P']['date_pay_start']=me.S['P'].get('date_pay_start',tool.date(body.now()))
	me.S['P']['date_pay_end']=me.S['P'].get('date_pay_end',tool.date(body.now()))
	me.S['P']['date_connect_start']=me.S['P'].get('date_connect_start',tool.date(body.now()))
	me.S['P']['date_connect_end']=me.S['P'].get('date_connect_end',tool.date(body.now()))
	me.S['P']['all']=me.S['P'].get('all','')
	sql='select count(distinct pay.account) as `count`,sum(pay.pay_sum) as pay_sum,pay_date from (SELECT date_format(%s,"%%Y-%%m-%%d") as pay_date,%s*%s as pay_sum,%s as account FROM %s where date(%s) between "%s" and "%s" and billno not in ("","billno") GROUP BY account) AS pay INNER JOIN %s as connect on pay.account=connect.%s and date(connect.%s) between "%s" and "%s" group by pay_date'%(
		model.info('charge')['map']['spliter']['field'],
		model.info('charge')['map']['pay_sum']['field'],
		body.config['currency_rate'][body.config["operator_currency"][int(me.S['A']['operator'])]],
		model.info('charge')['map']['account_id']['field'],
		model.info('charge')['name'],
		model.info('charge')['map']['spliter']['field'],
		me.S['P']['date_pay_start'],
		me.S['P']['date_pay_end'],
		model.info('connect')['name'],
		model.info('connect')['map']['account_id']['field'],
		model.info('connect')['map']['spliter']['field'],
		me.S['P']['date_connect_start'],
		me.S['P']['date_connect_end']
	)
	if me.S['P']['all']=="":
		data['data']=memory.get("query",{"memory":"server:%s"%(me.S['A']['server']),"sql":sql})
	else:
		t=server.queryInAll({"sql":sql})
		data['data']=tool.Dict()
		for v in t:
			if v['pay_date'] not in data['data']:
				data['data'][v['pay_date']]={"pay_date":v['pay_date'],"count":0,"pay_sum":0}
			data['data'][v['pay_date']]['count']+=v['count']
			data['data'][v['pay_date']]['pay_sum']+=v['pay_sum']
		data['data']=data['data'].values()
	return data
	
def check3Days():
	if not user.inGroup("operate"):return user.ban()
	import time
	me.S['P']['date_end']=me.S['P'].get('date_end',tool.date(body.now()))
	last_day=tool.date(tool.strtotime(me.S['P']['date_end'],"%Y-%m-%d")-86400)
	last_week_day=tool.date(tool.strtotime(me.S['P']['date_end'],"%Y-%m-%d")-86400*7)
	me.S['P']['server']=me.S['P'].get('server',me.S['A']['server'])
	#cache
	key="%s_%s_charge_check3Days_%s"%(me.S['A']['game'],me.S['A']['operator'],me.S['P']['date_end'])
	data=cache.get(key)
	
	if not data:
		data={}
		#common config
		data_msg={
			"memory":"server:%s"%me.S['P']['server'],
			"model":model.info('charge')["name"],
			"field":'date_format(FROM_UNIXTIME(UNIX_TIMESTAMP(%s)-UNIX_TIMESTAMP(%s)%%(5*60)),"%%H:%%i") as date,%s as pay_num,%s as pay_times,%s*%s as pay_sum'%(
				model.info('charge')["map"]["spliter"]['field'],
				model.info('charge')["map"]["spliter"]['field'],
				model.info('charge')['map']['pay_num']['field'],
				model.info('charge')['map']['pay_times']['field'],
				model.info('charge')['map']['pay_sum']['field'],
				body.config['currency_rate'][body.config["operator_currency"][int(me.S['A']['operator'])]]
			),
			"filter":'DATE_FORMAT(%s,"%%Y-%%m-%%d") in ("%s") and %s not in ("","billno")'%(
				model.info('charge')["map"]["spliter"]['field'],
				me.S['P']['date_end'],
				model.info('charge')["map"]["id"]['field']
			),
			"key":"date",
			"option":{"order":"date,asc","group":"date"}
		}
		last_day_msg=tool.copy(data_msg)
		last_week_day_msg=tool.copy(data_msg)
		last_day_msg['filter']='DATE_FORMAT(%s,"%%Y-%%m-%%d") in ("%s") and %s not in ("","billno")'%(
			model.info('charge')["map"]["spliter"]['field'],
			last_day,
			model.info('charge')["map"]["id"]['field']
		)
		last_week_day_msg['filter']='DATE_FORMAT(%s,"%%Y-%%m-%%d") in ("%s") and %s not in ("","billno")'%(
			model.info('charge')["map"]["spliter"]['field'],
			last_week_day,
			model.info('charge')["map"]["id"]['field']
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
					chart_data[kk].append({"value":"%s"%vv[v]['pay_sum']})
				else:
					chart_data[kk].append({"value":"0"})
		#chart
		data['chart']={}
		data['chart']['chart']={
			"caption":'【%s】%s/%s'%(server.getAll().get(me.S['P']['server'],{"value":me.S['P']['server']})['value'],word.check('充值概况'),word.check(body.config['currency_name'][body.config["operator_currency"][int(me.S['A']['operator'])]])),
			"subcaption":word.check("实时数据"),
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
		titles={"data":word.check("当天充值"),"last_day_data":word.check("昨天充值"),"last_week_day_data":word.check("上周同天充值")}
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
		data['tips']="%s:%s"%(word.check('你正在查看缓存数据，每1分钟缓存一次，缓存失效时间'),cache.getExpireTime(key))
	return data
def checkNew():
	if not user.inGroup("operate"):return user.ban()
	me.S['P']['date_start']=me.S['P'].get('date_start',tool.date(body.now()))
	me.S['P']['date_end']=me.S['P'].get('date_end',tool.date(body.now()))
	me.S['P']['all']=me.S['P'].get('all','')
	sql='SELECT sum(if(is_new,pay_sum,0)) AS new_pay_sum,sum(if(is_new,pay_num,0)) AS new_pay_num,sum(if(is_new,0,pay_sum)) AS old_pay_sum,sum(if(is_new,0,pay_num)) AS old_pay_num,date FROM ( SELECT IF ( date_format(from_unixtime(role.di32_10), "%%Y-%%m-%%d") = date, 1, 0 ) AS is_new, pay_sum, pay_num, date FROM ( SELECT role_id, (sum( amt / 10 + pubacct_payamt_coins ))*%s AS pay_sum, count(DISTINCT(charge.role_id)) AS pay_num,date_format(dt,"%%Y-%%m-%%d") AS date FROM charge WHERE billno NOT IN ("", "billno") AND date_format(dt, "%%Y-%%m-%%d") BETWEEN "%s" AND "%s" GROUP BY role_id, date) AS charge LEFT JOIN role_data AS role USING (role_id)) AS charge GROUP BY date ORDER BY date ASC'%(body.config['currency_rate'][body.config["operator_currency"][int(me.S['A']['operator'])]],me.S['P']['date_start'],me.S['P']['date_end'])
	data={}
	if me.S['P']['all']=='':
		data['data']=memory.get("query",{"sql":sql,"memory":"server:%s"%(me.S["A"]["server"])})
	else:
		data['data']=tool.Dict()
		t=server.queryInAll({"sql":sql})
		for v in t:
			if v['date'] not in data['data']:
				data['data'][v['date']]={"new_pay_sum":0,"new_pay_num":0,"old_pay_sum":0,"old_pay_num":0,"date":v["date"]}
			data['data'][v['date']]['new_pay_sum']+=v['new_pay_sum']
			data['data'][v['date']]['new_pay_num']+=v['new_pay_num']
			data['data'][v['date']]['old_pay_sum']+=v['old_pay_sum']
			data['data'][v['date']]['old_pay_num']+=v['old_pay_num']
		data['data']=data['data'].values()
	return data
#just longqi now
def checkFirstPay():
	if not user.inGroup("operate"):return user.ban()
	data={}
	me.S['P']['date_start']=me.S['P'].get('date_start',tool.date(body.now()))
	me.S['P']['date_end']=me.S['P'].get('date_end',tool.date(body.now()))
	sql='select charge.role_id as role_id,spliter,charge.level as level,pay,role_name,count(%s) as login_time,key_login from (select charge.role_id as role_id,spliter,charge.level as level,pay,role.%s as role_name,role.%s as key_login from (SELECT %s as role_id,min(%s) as spliter,%s as level,%s*%s as pay FROM %s where %s NOT IN ("billno", "") GROUP BY %s HAVING date(spliter) BETWEEN "%s" AND "%s") as charge left join %s as role on charge.%s=role.%s) as charge left join %s as login on login.%s=charge.key_login and date(login.%s)<="%s" group by charge.role_id,key_login'%(
		model.info('login')["map"]["spliter"]['field'],
		model.info('role')["map"]["name"]['field'],
		model.info('role')["map"]["key_login"]['field'],
		model.info('charge')["map"]["role_id"]['field'],
		model.info('charge')["map"]["spliter"]['field'],
		model.info('charge')["map"]["level"]['field'],
		model.info('charge')["map"]["pay"]['field'],
		body.config['currency_rate'][body.config["operator_currency"][int(me.S['A']['operator'])]],
		model.info('charge')["name"],
		model.info('charge')["map"]['id']['field'],
		model.info('charge')["map"]["role_id"]['field'],
		me.S['P']['date_start'],
		me.S['P']['date_end'],
		model.info('role')["name"],
		model.info('charge')["map"]["role_id"]['field'],
		model.info('role')["map"]["id"]['field'],
		model.info('login')["name"],
		model.info('login')["map"]['key_role']['field'],
		model.info('login')["map"]['spliter']['field'],
		me.S['P']['date_end']
	)
	data['data']=memory.get("query",{"sql":sql,"memory":"server:%s"%(me.S["A"]["server"])})
	data['count']=len(data['data'])
	return data

def checkLevel():
	import tool
	if not user.inGroup("operate"):return user.ban()
	data={}
	me.S['P']['date_start']=me.S['P'].get('date_start',tool.date(body.now()))
	me.S['P']['date_end']=me.S['P'].get('date_end',tool.date(body.now()))
	me.S['P']['range']=me.S['P'].get('range','')
	if me.S['P']['range']=='':me.S['P']['range']='31,51,71,91,101'
	me.S['P']['all']=me.S['P'].get('all','')
	msg={
		"model":model.info('charge')["name"],
		"field":"%s as level,sum(1) as times,%s as pay_num,%s*%s as pay_sum"%(
			model.info('charge')["map"]["level"]['field'],
			model.info('charge')["map"]["pay_num"]['field'],
			model.info('charge')["map"]["pay_sum"]['field'],
			body.config['currency_rate'][body.config["operator_currency"][int(me.S['A']['operator'])]]
		),
		"filter":'date(%s) between "%s" and "%s" and %s!="" and %s!="billno"'%(
			model.info('charge')["map"]["spliter"]['field'],
			me.S['P']['date_start'],
			me.S['P']['date_end'],
			model.info('charge')["map"]["id"]['field'],
			model.info('charge')["map"]["id"]['field']
		),
		"option":{"group":"%s,level"%(model.info('charge')["map"]["role_id"]['field'])}
	}
	if me.S['P']['all']=='':
		msg.update({"memory":"server:%s"%(me.S['A']['server'])})
		temp=memory.get('recall',msg)
	else:
		temp=server.recallInAll(msg)
	data['data']=tool.rangeData(temp,me.S['P']['range'],'level',True)
	#print data['data']
	return data
def checkSumRange():
	import tool
	if not user.inGroup("operate"):return user.ban()
	data={}
	me.S['P']['month']=me.S['P'].get('month',tool.date(body.now(),"%Y-%m"))
	me.S['P']['range']=me.S['P'].get('range','')
	if me.S['P']['range']=='':me.S['P']['range']='1001,5001,20001,50001,100000'
	me.S['P']['all']=me.S['P'].get('all','')
	msg={
		"model":model.info('charge')["name"],
		"field":"%s as pay_sum"%(model.info('charge')["map"]["pay_sum"]['field']),
		"filter":'DATE_FORMAT(%s,"%%Y-%%m")="%s" and %s!="" and %s!="billno"'%(
			model.info('charge')["map"]["spliter"]['field'],
			me.S['P']['month'],
			model.info('charge')["map"]["id"]['field'],
			model.info('charge')["map"]["id"]['field']
		),
		"option":{"group":"%s"%(model.info('charge')["map"]["account_id"]['field'])}
	}
	if me.S['P']['all']=='':
		msg.update({"memory":"server:%s"%(me.S['A']['server'])})
		temp=memory.get('recall',msg)
	else:
		temp=server.recallInAll(msg)
	t=[]
	for v in temp:
		t.append(v['pay_sum'])
	data['data']=tool.rangeDatum(t,me.S['P']['range'])
	return data
def checkCashConsume():
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
	me.S['P']['event']=me.S['P'].get('event',model.info('log_value')["map"]["log_value_event_cash"]['field'])
	transaction_range=''
	if me.S['P']['transaction']!='':transaction_range=' and %s in (%s)'%(model.info('log_value')["map"]["transaction"]['field'],me.S['P']['transaction'])
	
	me.S['P']['parallel']=me.S['P'].get('parallel','')
	#并行开关
	parallel={"parallel":False}
	if me.S['P']['parallel']!="":
		parallel["parallel"]=True
	msg={
		"model":"%s"%(model.info('log_value')["name"]),
		"field":"%s as role_id,%s as transaction,sum(%s-%s) as consume"%(
			model.info('log_value')["map"]["role_id"]['field'],
			model.info('log_value')["map"]["transaction"]['field'],
			model.info('log_value')["map"]["old_value"]['field'],
			model.info('log_value')["map"]["new_value"]['field']
		),
		"filter":'DATE_FORMAT(%s,"%%Y-%%m-%%d") between "%s" and "%s" and %s>%s and %s in (%s)%s'%(
			model.info('log_value')["map"]["spliter"]['field'],
			me.S['P']['date_start'],
			me.S['P']['date_end'],
			model.info('log_value')["map"]["old_value"]['field'],
			model.info('log_value')["map"]["new_value"]['field'],
			model.info('log_value')["map"]["event"]['field'],
			me.S['P']['event'],
			transaction_range
		),
		"option":{"group":"transaction,role_id","order":"consume,desc"},
		"range":"0,%s"%(me.S['P']['range']),
		"prefix_type":"log"
	}
	data['data']={}
	if me.S['P']['all']=='':
		msg.update({"memory":"server:%s"%(me.S['A']['server'])})
		temp=memory.get('recall',msg)
		for v in temp:
			if not v['transaction'] in data['data']:
				data['data'][v['transaction']]={"consume":0,"roles":0}
			data['data'][v['transaction']]["consume"]+=v['consume']
			data['data'][v['transaction']]["roles"]+=1
	else:
		msg['range']="0,100"
		temp=server.recallInAll(msg,parallel)
		t={}
		for v in temp:
			if not v['transaction'] in t:
				t[v['transaction']]={"consume":0,"roles":0}
			t[v['transaction']]['consume']+=v['consume']
			t[v['transaction']]['roles']+=1
		t=sorted(t.iteritems(), key=lambda x:x[1]["consume"],reverse=True)
		i=0
		for k,v in t:
			if i==int(me.S['P']['range']):break
			i+=1
			data['data'][k]=v
	#get transaction info
	transactions=me.post('log/getTransaction')
	for k,v in data['data'].items():
		data['data'][k]={"consume":v['consume'],"roles":v['roles'],"value":transactions.get(int(k),{"value":k})['value'],"desc":transactions.get(int(k),{"desc":""})['desc']}
	return data
def checkFirstConsume():
	if not user.inGroup("operate"):return user.ban()
	data={}
	me.S['P']['date_start']=me.S['P'].get('date_start',tool.date(body.now()))
	me.S['P']['date_end']=me.S['P'].get('date_end',tool.date(body.now()))
	#只允许查一天
	if me.S['P']['date_start']!=me.S['P']['date_end']:
		data['tips']=word.check("因日志数据量太大，暂时只开放查一天的！")
		return data
	me.S['P']['range']=me.S['P'].get('range','10')
	me.S['P']['transaction']=me.S['P'].get('transaction','')
	me.S['P']['event']=me.S['P'].get('event',model.info('log_value')["map"]["log_value_event_cash"]['field'])
	transaction_range=''
	if me.S['P']['transaction']!='':transaction_range=' and %s in (%s)'%(model.info('log_value')["map"]["transaction"]['field'],me.S['P']['transaction'])
	
	me.S['P']['parallel']=me.S['P'].get('parallel','')
	#并行开关
	parallel={"parallel":False}
	if me.S['P']['parallel']!="":
		parallel["parallel"]=True
	msg={
		"model":"%s"%(model.info('log_value')["name"]),
		"field":"min(%s) as datetime,%s as role_id,%s as transaction,(%s-%s) as consume"%(
			model.info('log_value')["map"]["spliter"]['field'],
			model.info('log_value')["map"]["role_id"]['field'],
			model.info('log_value')["map"]["transaction"]['field'],
			model.info('log_value')["map"]["old_value"]['field'],
			model.info('log_value')["map"]["new_value"]['field']
		),
		"filter":'DATE_FORMAT(%s,"%%Y-%%m-%%d") between "%s" and "%s" and %s>%s and %s in (%s)%s'%(
			model.info('log_value')["map"]["spliter"]['field'],
			me.S['P']['date_start'],
			me.S['P']['date_end'],
			model.info('log_value')["map"]["old_value"]['field'],
			model.info('log_value')["map"]["new_value"]['field'],
			model.info('log_value')["map"]["event"]['field'],
			me.S['P']['event'],
			transaction_range
		),
		"option":{"group":"role_id","order":"datetime,asc"},
		"prefix_type":"log"
	}
	data['data']={}
	msg.update({"memory":"server:%s"%(me.S['A']['server'])})
	data['data']=memory.get('recall',msg)
	#get transaction info
	data['transactions']=me.post('log/getTransaction')
	return data
def checkRolePay():
	if not user.inGroup("operate"):return user.ban()
	data={}
	me.S['G']['type']=me.S['G'].get('type','')
	me.S['G']['id']=me.S['G'].get('id','')
	me.S['G']['server']=me.S['G'].get('server',me.S['A']['server'])
	me.S['G']['date_start']=me.S['G'].get('date_start',tool.date(body.now()))
	me.S['G']['date_end']=me.S['G'].get('date_end',tool.date(body.now()))
	#全服或导出
	me.S['G']['all']=me.S['G'].get('all','')
	me.S['G']['export']=me.S['G'].get('export','')
	if me.S['G']['all']!="":me.S['G']['export']="true"
	
	role_filter=''
	if me.S['G']['id']:
		#transfer id
		role_id=me.S['G']['id']
		import role
		if me.S['G']['type']!='role_id':
			role_id=role.getID({"from":me.S['G']['type'],"id":me.S['G']['id'],"server":me.S['G']['server']})
		elif not role_id.isdigit():
			data['tips']=word.check("角色ID必须为数字！")
			return data
		if not role_id:
			data['tips']=word.check("角色ID不存在！")
		else:
			role_filter=' and %s=%s'%(model.info('charge')['map']['role_id']['field'],role_id)
	
	#check charge details by ID
	data_msg={
		"model":model.info('charge')['name'],
		"memory":"server:%s"%me.S['A']['server'],
		"field":'%s as role_id,%s as account,%s as billno,date_format(%s,"%%Y-%%m-%%d %%H:%%i:%%s") as date,%s*%s as pay'%(
			model.info('charge')['map']['role_id']['field'],
			model.info('charge')['map']['account_id']['field'],
			model.info('charge')['map']['id']['field'],
			model.info('charge')['map']['spliter']['field'],
			model.info('charge')['map']['pay']['field'],
			body.config['currency_rate'][body.config["operator_currency"][int(me.S['A']['operator'])]]
		),
		"filter":'%s not in ("","billno")%s and DATE_FORMAT(%s,"%%Y-%%m-%%d") between "%s" and "%s"'%(
			model.info('charge')['map']['id']['field'],
			role_filter,
			model.info('charge')['map']['spliter']['field'],
			me.S['G']['date_start'],
			me.S['G']['date_end']),
		"option":{"order":"date,asc"},
		"range":me.S['G'].get("range",'1,10')
	}
	if me.S['G']['export']=="":
		sum_msg={
			"one":True,
			"memory":"server:%s"%me.S['A']['server'],
			"model":model.info('charge')['name'],
			"field":'%s as role_id,%s as billno,date_format(%s,"%%Y-%%m-%%d %%H:%%i:%%s") as date,%s*%s as pay_sum'%(
				model.info('charge')['map']['role_id']['field'],
				model.info('charge')['map']['id']['field'],
				model.info('charge')['map']['spliter']['field'],
				model.info('charge')['map']['pay_sum']['field'],
				body.config['currency_rate'][body.config["operator_currency"][int(me.S['A']['operator'])]]
			),
			"filter":'%s not in ("","billno")%s and DATE_FORMAT(%s,"%%Y-%%m-%%d") between "%s" and "%s"'%(
				model.info('charge')['map']['id']['field'],
				role_filter,
				model.info('charge')['map']['spliter']['field'],
				me.S['G']['date_start'],me.S['G']['date_end']),
			"option":{"order":"date,asc"}
		}
		data=model.get({
			"data":data_msg,
			"sums":sum_msg
		})
		import role
		for v in data['data']:
			v.update(role.getInfo(v['role_id'],'name'))
		#range
		range_msg={
			"model":model.info('charge')['name'],
			"filter":'%s not in ("","billno")%s and DATE_FORMAT(%s,"%%Y-%%m-%%d") between "%s" and "%s"'%(
				model.info('charge')['map']['id']['field'],
				role_filter,model.info('charge')['map']['spliter']['field'],
				me.S['G']['date_start'],me.S['G']['date_end']),
			"url":me.S["path"],
			"msg":{
				"type":str(me.S['G']['type']),
				"id":str(me.S['G']['id']),
				"date_start":me.S['G']['date_start'],
				"date_end":me.S['G']['date_end']
			},
			"memory":"server:%s"%me.S['G']['server'],
			"size":"10",
			"range":me.S['G'].get("range",'1,10')
		}
		data['range']=body.getRange(range_msg) #get range
		data['servers']=server.getAll()
	else:
		del data_msg['range']
		if me.S['G']['all']=="":
			data_msg['field']+=",%s as server"%(me.S['A']['server'])
			data=memory.get("recall",data_msg)
		else:
			del data_msg['memory']
			data=server.recallInAll(data_msg,{"server_field":True})
		fields=['server','role_id','billno','date','pay']
		try:
			data=tool.dictToList(data,fields)
			data.insert(0,fields)
			data=model.export(data)
		except:
			traceback.print_exc()
			pass
	return data

def checkPayitem():
	if not user.inGroup("operate"):return user.ban()
	data={"data":{}}
	me.S['P']['date_start']=me.S['P'].get('date_start',tool.date(body.now()))
	me.S['P']['date_end']=me.S['P'].get('date_end',tool.date(body.now()))
	me.S['P']['all']=me.S['P'].get('all','')
	#items
	msg={
		"model":model.info('charge')['name'],
		"field":"%s as payitem,%s as pay"%(model.info('charge')['map']['payitem']['field'],model.info('charge')['map']['pay']['field']),
		"filter":'%s!="" and %s!="" and date(`%s`) between "%s" and "%s"'%(model.info('charge')['map']['id']['field'],model.info('charge')['map']['payitem']['field'],model.info('charge')['map']['spliter']['field'],me.S['P']['date_start'],me.S['P']['date_end'])
	}
	if me.S['P']['all']=="":
		msg['memory']="server:%s"%me.S['A']['server']
		temp=model.get({
			"data":msg
		})
	else:
		temp={}
		temp['data']=server.recallInAll(msg)
	
	import item
	item_info=item.getAll()
	for v in temp['data']:
		item=v['payitem'].split('*')
		if item[0] not in data['data']:
			data['data'][item[0]]={"name":item_info.get(str(item[0]),{"name":item[0]})['name'],"num_pay":0,"sum_pay":0}
		data['data'][item[0]]['num_pay']+=int(item[2])
		data['data'][item[0]]['sum_pay']+=v['pay']
	return data

#商场购买道具,暂只支持龙骑
def checkBuyItem():
	if not user.inGroup("operate"):return user.ban()
	data={"data":{}}
	me.S['P']['date_start']=me.S['P'].get('date_start',tool.date(body.now()))
	me.S['P']['date_end']=me.S['P'].get('date_end',tool.date(body.now()))
	me.S['P']['all']=me.S['P'].get('all','')
	me.S['P']['parallel']=me.S['P'].get('parallel','')
	#并行开关
	parallel={"parallel":False}
	if me.S['P']['parallel']!="":
		parallel["parallel"]=True
	#cache
	key="%s_%s_charge_checkBuyItem_%s_%s_%s"%(me.S['A']['game'],me.S['A']['operator'],me.S['P']['date_start'],me.S['P']['date_end'],me.S['P'].get('all',me.S['A']['server']))
	cache_data=cache.get(key)
	
	if not cache_data:
		msg={
			"prefix_type":"log",
			"memory":"server:%s"%me.S['A']['server'],
			"model":"log_obj",
			"field":"obj_type,obj_int",
			"filter":'log_transaction=844 and log_event=30007 and date(`log_datetime`) between "%s" and "%s"'%(me.S['P']['date_start'],me.S['P']['date_end'])
		}
		if me.S['P']['all']=='':
			#items
			temp=model.get({"data":msg})
		else:
			temp={"data":server.recallInAll(msg,parallel)}
		import item
		item_info=item.getAllGoods()
		for v in temp['data']:
			#item=eval(v['log_content'])
			try:
				if v['obj_type'] not in data['data']:
					data['data'][v['obj_type']]={"id":v['obj_type'],"name":item_info.get(str(v['obj_type']),v['obj_type']),"num_buy":v['obj_int']}
				data['data'][v['obj_type']]['num_buy']+=v['obj_int']
				# if "%s_%s"%(item[0],item[1]) not in data['data']:
					# data['data']["%s_%s"%(item[0],item[1])]={"id":str(item[1]),"name":"%s"%(item_info.get(str(item[0]),{"goods":{str(item[1]):str(item[1])}})['goods'].get(str(item[1]),str(item[1]))),"num_buy":0,"type":item_info.get(str(item[0]),{"name":str(item[0])})['name']}
				# data['data']["%s_%s"%(item[0],item[1])]['num_buy']+=int(item[2])
			except:
				traceback.print_exc()
				pass
		cache.set(key,data,3600)
	else:
		data=cache_data
		data['tips']="%s:%s"%("你正在查看缓存数据，每1分钟缓存一次，缓存失效时间",cache.getExpireTime(key))
	return data
def rank():
	if not user.inGroup("operate"):return user.ban()
	data={}
	me.S['G']['red']=me.S['G'].get('red',"3")
	me.S['G']['date_start']=me.S['G'].get('date_start',"2014-01-01")
	me.S['G']['date_end']=me.S['G'].get('date_end',tool.date(body.now()))
	me.S['G']['all']=me.S['G'].get('all',"")
	
	msg={
		"model":model.info('charge')['name'],
		"field":"%s as role_id,%s as account_id,%s*%s as pay_sum,date_format(max(%s),'%%Y-%%m-%%d %%H:%%i:%%s') as time_last_pay"%(
			model.info('charge')['map']['role_id']['field'],
			model.info('charge')['map']['account_id']['field'],
			model.info('charge')['map']['pay_sum']['field'],
			body.config['currency_rate'][body.config["operator_currency"][int(me.S['A']['operator'])]],
			model.info('charge')['map']['spliter']['field']
		),
		"range":me.S['G'].get('range','1,20'),
		"filter":'%s!="" and %s!="billno" and date(`%s`) between "%s" and "%s"'%(model.info('charge')['map']['id']['field'],model.info('charge')['map']['id']['field'],model.info('charge')['map']['spliter']['field'],me.S['G']['date_start'],me.S['G']['date_end']),
		"option":{"order":"pay_sum,desc","group":"role_id"},
		"range":me.S['G'].get("range","1,20")
	}
	if me.S['G']['all']=="":
		msg['memory']="server:%s"%me.S['A']['server']
		data=model.get({
			"data":msg
		})
		#range
		range_msg={
			"model":model.info('charge')['name'],
			"filter":'%s!="" and %s!="billno" and date(`%s`) between "%s" and "%s"'%(model.info('charge')['map']['id']['field'],model.info('charge')['map']['id']['field'],model.info('charge')['map']['spliter']['field'],me.S['G']['date_start'],me.S['G']['date_end']),
			"url":me.S["path"],
			"msg":{
				"red":me.S['G']['red'],
				"date_start":me.S['G']['date_start'],
				"date_end":me.S['G']['date_end']
			},
			"memory":"server:%s"%me.S['A']['server'],
			"size":"20",
			"range":me.S['G'].get("range",'1,20')
		}
		data['range']=body.getRange(range_msg) #get range
	else:
		#all servers
		me.S['G']['ranges']=me.S['G'].get('ranges',"20")
		key="%s_%s_charge_rank_all_%s"%(me.S['A']['game'],me.S['A']['operator'],me.S['G']['ranges'])
		data['data']=cache.get(key)
		if not data['data']:
			msg['range']="1,%s"%(me.S['G']['ranges'])
			data['data']=server.recallInAll(msg,{"server_field":True})
			data['data']=sorted(data['data'],key=lambda x : x['pay_sum'],reverse=True)
			data['data']=data['data'][:int(me.S['G']['ranges'])]
			cache.set(key,data['data'],3600)#每小时更新
		else:
			data['tips']=word.check("你正在查看缓存排名数据，每小时更新！")
		data['servers']=server.getAll()
	#add name
	for v in data['data']:
		v.update(role.getInfo(v['role_id'],'name,cash,time_last_login,time_total_online,vip'))
		v['is_red']=False
		try:
			if (body.now()-tool.strtotime(v['time_last_pay']))/86400<int(me.S['G']['red']):
				v['is_red']=True
		except:
			print v
	return data