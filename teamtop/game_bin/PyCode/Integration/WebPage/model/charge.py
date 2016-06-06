#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 充值
#===============================================================================
import traceback,time
import me,server,tool,role

def check(R):
	get={}
	data={}
	get['month']=me.G(R,'month')
	if not get['month']:
		get['month']=tool.date(time.time(),"%Y-%m")
	get['server']=me.G(R,'server')
	if not get['server']:
		get['server']=R.session['server']
	data['get']=get
	if get['month']:
		data['data']=me.M('recall',{"memory":"server:%s"%get['server'],"model":"charge","field":'date_format(dt,"%Y-%m-%d") as date,count(distinct(role_id)) as pay_num,count(*) as pay_times,sum(amt/10+pubacct_payamt_coins) as pay_sum',"filter":'billno!="" and billno!="billno" and DATE_FORMAT(dt,"%%Y-%%m")="%s"'%get['month'],"option":{"order":"date,asc","group":"date"}})
		for v in data['data']:
			v['arpu']='%.2f'%(v['pay_sum']/v['pay_num']/10)
			v['pay_sum']='%.2f'%(v['pay_sum']/10)
		#month data
		data['month']=me.M('recall',{"memory":"server:%s"%get['server'],"model":"charge","field":'date_format(dt,"%Y-%m") as month,count(distinct(role_id)) as pay_num,count(*) as pay_times,sum(amt/10+pubacct_payamt_coins) as pay_sum',"filter":'billno!="" and billno!="billno" and DATE_FORMAT(dt,"%%Y-%%m")="%s"'%get['month'],"option":{"group":"month"}})
		for v in data['month']:
			v['arpu']='%.2f'%(v['pay_sum']/v['pay_num']/10)
			v['pay_sum']='%.2f'%(v['pay_sum']/10)
		#chart
		data['chart']={}
		data['chart']['chart']={
			"caption":'游戏服%s充值概况'%server.getAll().get(get['server'],{"name":get['server']})['name'],
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
		category=[]
		pay_sum=[]
		pay_num=[]
		for v in data['data']:
			category.append({"label":v['date']})
			pay_sum.append({"value":v['pay_sum']})
			pay_num.append({"value":v['pay_num']})
		data['chart']['categories']=[{"category":category}]
		data['chart']['dataset']=[{
				"seriesname":"充值总额",
				"color":"ff0000",
				"showvalues":"1",
				"data":pay_sum
			},{
				"seriesname":"充值人数",
				"color":"0000ff",
				"showvalues":"1",
				"valueposition":"below",
				"data":pay_num
			}
		]
		import json
		data['chart']=json.dumps(data['chart'])
	return data
def checkRolePay(R):
	data={}
	get={}
	get['type']=me.G(R,'type')
	get['id']=me.G(R,'id')
	get['server']=me.G(R,'server',"int")
	get['start_date']=me.G(R,'start_date')
	get['end_date']=me.G(R,'end_date')
	if get['start_date']=='':
		get['start_date']=tool.date(time.time())
	if get['end_date']=='':
		get['end_date']=tool.date(time.time())
	data['get']=get
	data['servers']=server.getAll()
	if get['id']:
		#transfer id
		id=get['id']
		import role
		if get['type']!='roleid':
			id=role.getID({"from":get['type'],"id":get['id'],"server":get['server']})
		elif not id.isdigit():
			data['tips']="角色ID必须为数字！"
			return data
		if not id:
			data['tips']="角色ID不存在！"
		else:
			#check charge details by ID
			data['data']=me.M('recall',{"memory":"server:%s"%get['server'],"model":"charge","field":'role_id,date_format(dt,"%Y-%m-%d %H:%i:%s") as date,(amt/10+pubacct_payamt_coins) as pay_sum',"filter":'billno!="" and billno!="billno" and role_id=%s and DATE_FORMAT(dt,"%%Y-%%m-%%d") between "%s" and "%s"'%(id,get['start_date'],get['end_date']),"option":{"order":"date,asc"}})
			data['sum']=me.M('recall',{"one":True,"memory":"server:%s"%get['server'],"model":"charge","field":'role_id,date_format(dt,"%Y-%m-%d") as date,sum(amt/10+pubacct_payamt_coins) as pay_sum',"filter":'billno!="" and billno!="billno" and role_id=%s and DATE_FORMAT(dt,"%%Y-%%m-%%d") between "%s" and "%s"'%(id,get['start_date'],get['end_date']),"option":{"order":"date,asc"}})
	return data

def checkPayitem(R):
	get={}
	data={}
	get['date_start']=me.G(R,'date_start')
	get['date_end']=me.G(R,'date_end')
	if get['date_start']=='':
		get['date_start']=tool.date(time.time())
	if get['date_end']=='':
		get['date_end']=tool.date(time.time())
	data['data']={}
	#items
	from Integration.Help import ConfigHelp
	import item as model_item
	sql='select payitem,(amt/10+pubacct_payamt_coins) as sum_pay from charge where billno!="" and billno!="billno" and payitem!="" and date(`dt`) between "%s" and "%s"'%(get['date_start'],get['date_end'])
	temp=me.M("query",{"sql":sql,"memory":"server:%s"%R.session['server']})
	for v in temp:
		item=v['payitem'].split('*')
		if item[0] not in data['data']:
			data['data'][item[0]]={"name":model_item.goods.get(item[0],item[0]),"num_pay":0,"sum_pay":0}
		data['data'][item[0]]['num_pay']+=int(item[2])
		data['data'][item[0]]['sum_pay']+=v['sum_pay']
	data['get']=get
	return data

def rank(R):
	get={}
	data={}
	get['start_date']=me.G(R,'start_date')
	get['end_date']=me.G(R,'end_date')
	get['red']=me.G(R,'red')
	if get['start_date']=='':
		get['start_date']="2014-01-01"
	if get['end_date']=='':
		get['end_date']=tool.date(time.time())
	data['get']=get
	range_info=me.getRange(R,{"memory":"server:%s"%R.session['server'],"size":"20","model":"charge","url":"/model/charge/rank","filter":'date(`dt`) between "%s" and "%s"'%(get['start_date'],get['end_date'])})
	data['range']=range_info['html']
	data['data']=me.M('recall',{"memory":"server:%s"%R.session['server'],"model":"charge","field":"role_id,account,sum(amt/10+pubacct_payamt_coins) as pay_sum","range":range_info['range'],"filter":'date(`dt`) between "%s" and "%s"'%(get['start_date'],get['end_date']),"option":{"order":"pay_sum,desc","group":"role_id"}})
	for v in data['data']:
		if not v['role_id']:
			continue
		v['name']=role.getInfo(v['role_id'])['role_name']
		v['pay_sum']='%.2f'%(v['pay_sum']/10)
	return data