#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 服务器
#===============================================================================
import time
import me,tool

def checkOnlineDuration(R):
	data={}
	get={}
	data['temp']=me.M('query',{"memory":'server:%s' % R.session['server'],"sql":'select round(di32_1/300) as duration,count(*) as count from role_data group by duration'})
	#chart
	data['chart']={
		"chart":{
			"caption":"玩家总在线时长/分钟",
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
	data['get']=get
	data['servers']=getAll()
	
	return data

def checkLevelRange(R):
	data={}
	get={}
	data['count']=me.M('recall',{"one":True,"memory":'server:%s' % R.session['server'],"model":"role_data","field":'count(*) as count'})
	data['temp']=me.M('query',{"memory":'server:%s' % R.session['server'],"sql":'select di32_11 as level from role_data'})
	#chart
	data['chart']={
		"chart":{
			"caption":"玩家等级分布",
			"xAxisName":"Sex",
			"yAxisName":"Sales",
			"numberPrefix":"",
			"baseFontSize":'16'
		},
		"data":[]
	}
	
	data['level_data']={}
	import struct
	for v in data['temp']:
		# v['level'] = v['level_b']
		# if not v['level']:
			# continue
		# v['level'] = struct.unpack("H", v['level'])[0]

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
	#data['level_data'][0]={"count":0,"rate":0,"base":0,"reach":0,"reach_rate":0,"loss_rate":0}
	for i in range(0,max+1):
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
	data['get']=get
	data['servers']=getAll()
	
	return data
#查看注册留存
def checkRegisterKeep(R):
	data={}
	get={}
	import time,tool
	if 'start_date' not in R.POST:
		get['start_date']=tool.date(int(time.time()))
		get['end_date']=tool.date(int(time.time()))
	else:
		get['start_date']=me.G(R,'start_date')
		get['end_date']=me.G(R,'end_date')
		
	data['get']=get
	temp={}
	#get connect info
	if get['start_date']==get['end_date']: #当天每小时详细情况
		data['day']=me.M('query',{"memory":'server:%s' % R.session['server'],"sql":'select date_format(connect_time,"%%Y-%%m-%%d %%H") as date,sum(1) as connect_num,sum(if(request_create>0,1,0)) as R_num,sum(if(first_operate>0,1,0)) as player_num from connect_info where date(connect_time) between "%s" and "%s" group by date' % (get['start_date'],get['end_date'])})
		data['data_day']=[]
		for v in data['day']:
			v['role_lost_rate']=100
			if v['connect_num']>0:
				v['role_lost_rate']=100-float(v['R_num'])*100/float(v['connect_num'])
			v['player_loat_rate']=100
			if v['R_num']>0:
				v['player_lost_rate']=100-float(v['player_num'])*100/float(v['R_num'])
			data['data_day'].append(v)
		del data['day']
	# else:
	data['temp']=me.M('query',{"memory":'server:%s' % R.session['server'],"sql":'select date_format(connect_time,"%%Y-%%m-%%d") as date,sum(1) as connect_num,sum(if(request_create>0,1,0)) as R_num,sum(if(first_operate>0,1,0)) as player_num from connect_info where date(connect_time) between "%s" and "%s" group by date' % (get['start_date'],get['end_date'])})
	data['data']=[]
	for v in data['temp']:
		v['role_lost_rate']=100
		if v['connect_num']>0:
			v['role_lost_rate']=100-float(v['R_num'])*100/float(v['connect_num'])
		v['player_loat_rate']=100
		if v['R_num']>0:
			v['player_lost_rate']=100-float(v['player_num'])*100/float(v['R_num'])
		data['data'].append(v)
	del data['temp']
	
	#N天留存
	data['keep']=[]
	data['temp']=me.M('query',{"memory":'server:%s' % R.session['server'],"sql":'select date_format(FROM_UNIXTIME(di32_10),"%%Y-%%m-%%d") as date, count(account) as count,  sum(if(datediff(FROM_UNIXTIME(di32_16),FROM_UNIXTIME(di32_10))>=1,1,0)) as one,sum(if(datediff(FROM_UNIXTIME(di32_16),FROM_UNIXTIME(di32_10))>=2,1,0)) as two,sum(if(datediff(FROM_UNIXTIME(di32_16),FROM_UNIXTIME(di32_10))>=3,1,0)) as three,sum(if(datediff(FROM_UNIXTIME(di32_16),FROM_UNIXTIME(di32_10))>=4,1,0)) as four,sum(if(datediff(FROM_UNIXTIME(di32_16),FROM_UNIXTIME(di32_10))>=5,1,0)) as five,sum(if(datediff(FROM_UNIXTIME(di32_16),FROM_UNIXTIME(di32_10))>=6,1,0)) as six,sum(if(datediff(FROM_UNIXTIME(di32_16),FROM_UNIXTIME(di32_10))>=7,1,0)) as seven,sum(if(datediff(FROM_UNIXTIME(di32_16),FROM_UNIXTIME(di32_10))>=14,1,0)) as fourteen,sum(if(datediff(FROM_UNIXTIME(di32_16),FROM_UNIXTIME(di32_10))>=30,1,0)) as thirty from role_data where date(FROM_UNIXTIME(di32_10)) between "%s" and "%s" and di32_16>0 group by date(FROM_UNIXTIME(di32_10))' % (get['start_date'],get['end_date'])})
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
		data['keep'].append(v)
	data['get']=get
	return data
	
def getAll():
	data={}
	from Integration.Help import WorldHelp
	import collections
	for zid,zone in WorldHelp.GetZone().iteritems():
		data[zid]={}
		data[zid]['name']=zone.get_name()
		try:
			index=data[zid]['name'].index('模拟')
			del data[zid]
		except:
			pass
	data=collections.OrderedDict(sorted(data.items(),key = lambda t:t[0]))
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
	data=collections.OrderedDict(sorted(data.items(),key = lambda t:int(t[0].replace('GHL',''))))
	return data
			
def checkOnline(R):
	data={}
	get={}
	import time,tool
	if 'date' not in R.POST:
		get['date']=tool.date(int(time.time()))
	else:
		get['date']=me.G(R,'date')
	data['get']=get
	temp={}
	data['data']=me.M('query',{"memory":"server:%s" % R.session['server'],"sql":'select ips,roles,date_format(sta_time,"%%Y-%%m-%%d %%H:%%i:%%s") as sta_time from online_info where date(sta_time)="%s"' % get['date']})
	
	data['status']=me.M('query',{"one":True,"memory":"server:%s" % R.session['server'],"sql":'select max(ips) as max_ips,round(avg(ips)) as avg_ips,min(ips) as min_ips,max(roles) as max_roles,round(avg(roles)) as avg_roles,min(roles) as min_roles from online_info where date(sta_time)="%s"' % get['date']})
	
	data['chart']={}
	data['chart']['chart']={
		"caption":"服%s在线人数"%getAll().get(R.session['server'],{}).get('name',R.session['server']),
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
		category.append({"label":':'.join(v['sta_time'].split(' ')[1].split(':')[:2])})
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
	data['get']=get
	return data
	
def list(R):
	data={}
	data['data']=getAll()
	return data
	
def listNotice(R):
	get={}
	data={}
	#edit listed notice
	if 'step' in R.POST:
		get['render']=me.G(R,'render')
		get['step']=me.G(R,'step')
		if get['step']=='changeInterval':
			get['id']=me.G(R,'id')
			get['interval']=me.G(R,'interval','int')
			done=me.M("remember",{"action":"edit","model":"notice","data":{"interval_time":get['interval']},"filter":"nid in (%s)"%get['id']})
			if done:
				data['result']="true"
		#delete
		if get['step']=='changeVisible':
			get['id']=me.G(R,'id')
			me.M("forget",{"model":"notice","filter":"nid in (%s)"%get['id']})
			data['result']="true"
		if get['render']=='js':
			import json
			data['response']=json.dumps(data)
		return data
	range_info=me.getRange(R,{"size":"20","model":"notice","url":"/model/server/listNotice","option":{"order":"nid,desc"}})
	data['range']=range_info['html']
	data['notices']=me.M("recall",{"model":"notice","field":"nid,content,start_time,end_time,interval_time,track,process,sender","range":range_info['range'],"option":{"order":"nid,desc"}})
	return data

def loopNotice(R):
	import time,math
	now_time=time.time()
	from_time=now_time-60 #从哪个时间开始计算公告
	temp=me.M("recall",{"field":"nid,process,content,UNIX_TIMESTAMP(end_time) as endtime,UNIX_TIMESTAMP(start_time) as starttime,interval_time,track","model":"notice","filter":"interval_time>0 and UNIX_TIMESTAMP(end_time)>%s"%from_time})
	for v in temp:
		times=math.floor((from_time-v['starttime'])/v['interval_time'])+1
		left=(from_time-v['starttime'])%v['interval_time']
		#track($times.'/'.$left,"times/left",$msg['track'])
		if v['interval_time']-left>60 or v['track'].find("/%s,"%(times))>=0:
			#track($value['interval']-$left,"not in range",$msg['track'])
			continue
		#send
		command='import cRoleMgr;cRoleMgr.Msg(1,0,"%s")' % v['content']
		process=v['process'].split(',')
		for vv in process:
			try:
				result=sendCommand(vv,command)
			except:
				pass
		track='%s%s/%s,'%(v['track'],now_time,times)
		me.M("remember",{"action":"edit","model":"notice","filter":{"nid":v['nid']},"data":{"track":track}})
		#print track
		#log
	return
	
def sendNotice(R):
	data={}
	get={}
	data['processes']=getProcess()
	if 'process' in R.POST:
		get['process']=me.G(R,'process','list')
		get['content']=me.G(R,'content').replace("'",'').replace('"','')
		get['interval']=me.G(R,'interval','int')
		get['start_time']=me.G(R,'start_time')
		get['end_time']=me.G(R,'end_time')
		
		data['get']=get
		if len(get['process'])==0 or get['content']=='':
			data['tips']="你就不能完整填写公告再发吗!|-_-..."
			return data
		#instance notice
		track=''
		if get['interval']==0:
			command='import cRoleMgr;cRoleMgr.Msg(1,0,"%s")' % get['content']
			for v in get['process']:
				try:
					result=sendCommand(v,command)
					track+='P:%s|R:%s,'%(v,result)
				except:
					pass
			data['tips']="发送%s(P:服务器ID,R:结果)：%s"%(command,track)
		else:
			if get['start_time']=='' or get['end_time']=='':
				data['tips']="请设定循环公告时间范围！"
			data['tips']="循环公告已保存，请到历史公告查看循环发送结果！"
		me.M("remember",{"action":"add","model":"notice","data":{"track":track,"interval_time":get['interval'],"content":get['content'],"process":','.join(get['process']),"start_time":get['start_time'],"end_time":get['end_time'],"sender":R.session['user']['name']}})
	return data

def sendCommand(pkey,m):
	from Integration.Help import Concurrent
	return Concurrent.GMCommand(pkey,m)
	
def getLast():
	all=getAll()
	last=0
	for k,v in all.items():
		if k>last:
			last=k
	return last
	
def checkRoll(R):
	get={}
	data={"data":{}}
	get['date_start']=me.G(R,'date_start')
	get['date_end']=me.G(R,'date_end')
		
	if get['date_start']:
		sql='select account,group_concat(`server` order by `di32_10` asc) as servers,group_concat(date_format(from_unixtime(di32_10),"%Y-%m-%d %H:%i:%s") order by `di32_10` asc) as create_time from (select account from role_data group by account having count(*)>1) as role_all left join role_data using(account) group by account order by di32_10 asc'
		
		temp=me.M("query",{"memory":me.DBS['total'],"sql":sql})
		for v in temp:
			#if is first server,not roll in
			servers=v['servers'].split(',')
			#roll index
			try:
				roll_index=servers.index(R.session['server'])
			except:
				roll_index=-1
			#never to this server or first is this server
			if roll_index<=0:
				continue
			#roll time
			roll_time=v['create_time'].split(',')[roll_index]
			#not in data range
			if tool.strtotime(roll_time)>(tool.strtotime(get['date_end'],"%Y-%m-%d")+86400) or tool.strtotime(roll_time)<tool.strtotime(get['date_start'],"%Y-%m-%d"):
				continue
			#roll roles in this range
			roll_date=tool.date(tool.strtotime(roll_time))
			if roll_date not in data['data']:
				data["data"][roll_date]={"num_roll":0,"num_pay":0,"sum_pay":0,"num_pay_after_roll":0,"sum_pay_after_roll":0}
			#roll num +1 in this date
			data["data"][roll_date]['num_roll']+=1
			#pay in roll date
			sql='select sum(amt/10+pubacct_payamt_coins) as sum_pay_in_roll_day from charge where date(dt)=date("%s") and dt>"%s" and account="%s" and billno!="" and `server`=%s'%(roll_time,roll_time,v['account'],R.session['server'])
			temp=me.M("query",{"memory":me.DBS['total'],"one":True,"model":"charge","sql":sql})
			if temp['sum_pay_in_roll_day']>0:
				data["data"][roll_date]['num_pay']+=1
				data["data"][roll_date]['sum_pay']+=temp['sum_pay_in_roll_day']
			#pay in all date after roll
			sql='select sum(amt/10+pubacct_payamt_coins) as sum_pay_after_roll,date_format(dt,"%%Y-%%m-%%d") as date from charge where date(dt) between "%s" and "%s" and dt>"%s" and account="%s" and billno!="" and `server`=%s group by date'%(get['date_start'],get['date_end'],roll_time,v['account'],R.session['server'])
			temp=me.M("query",{"memory":me.DBS['total'],"model":"charge","sql":sql})
			
			for vv in temp:
				if vv['date'] not in data["data"]:
					data["data"][vv['date']]={"num_roll":0,"num_pay":0,"sum_pay":0,"num_pay_after_roll":0,"sum_pay_after_roll":0}
				
				data["data"][vv['date']]['num_pay_after_roll']+=1
				data["data"][vv['date']]['sum_pay_after_roll']+=vv['sum_pay_after_roll']

	#default
	if not get['date_start']:
		get['date_start']=tool.date(time.time()-86400)
	if not get['date_end']:
		get['date_end']=tool.date(time.time()-86400)
	data['get']=get
	return data