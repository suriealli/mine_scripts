# -*- coding:UTF-8 -*-
import time,traceback
import me,tool,memory,user,model,word
def start():
	if letGo():return False
	data={}
	data['model']=me.S['A']['model']
	data['action']=me.S['A']['action']
	data['start_time']=tool.date(time.time(),"%Y-%m-%d %H:%M:%S")
	data['status']='pending'
	data['user']=me.S.get('user',{"name":"unknown"})['name']
	#request log
	if "%s_%s"%(me.S['A']['model'],me.S['A']['action']) in ["role_ban"]:
		if len(me.S['G'])>0:
			data['request']=tool.pickle(me.S['G'])
	id=memory.get("remember",{"model":"action","data":data})
	return id

def end(id=False):
	if not id:return
	data={}
	data['end_time']=tool.date(time.time(),"%Y-%m-%d %H:%M:%S")
	data['status']='end'
	memory.get("remember",{"model":"action","action":"edit","data":data,"filter":{"id":id}})

def letGo():
	data=False
	if me.S['A']['model'] in ['action','tool','guide']:
		data=True
	if '%s_%s'%(me.S['A']['model'],me.S['A']['action']) in ['notice_loop']:
		data=True
	return data

def guide():
	if not user.inGroup('host'):return user.ban()
	return model.guide({"option":{"order":"start_time,desc"}})

def range():
	if not user.inGroup('host'):return user.ban()
	data={}
	msg={
		"model":"action",
		"field":"count(*) as count,concat(`model`,'_',`action`) as model_action",
		"option":{"group":"model_action","order":"count,desc"}
	}
	data['data']=memory.get("recall",msg)
	#chart
	data['chart']={
		"chart":{
			"caption":"%s"%(word.check('用户操作分布')),
			"xAxisName":"Sex",
			"yAxisName":"Sales",
			"numberPrefix":"",
			"baseFontSize":'16'
		},
		"data":[]
	}
	for v in data['data']:
		data['chart']['data'].append({"label":str(v['model_action']),"value":v['count']})
	import json
	data['chart']=json.dumps(data['chart'])
	return data