# -*- coding:UTF-8 -*-
import os,traceback,time
import me,tool,memory,model,user
#游戏具体操作
def act(msg=None):
	data={}
	if not msg:msg={}
	Model=msg.get("model",me.S['A']['model'])
	Action=msg.get("action",me.S['A']['action'])
	Act=False
	try:
		Model=me.review(Model,msg.get("game",me.S['A'].get('game','')))
		Act=getattr(Model,Action)
	except:
		traceback.print_exc()
		pass
	if Act:
		data=Act(msg)
	return data
def add():
	if not user.inGroup("host"):return user.ban()
	return model.add()
	
def edit():
	if not user.inGroup("host"):return user.ban()
	if 'id' in me.S['P'] and 'operators' not in me.S['P']:
		me.S['P']['operators']=''
	if 'operators' in me.S['P'] and me.S['P']['operators']!="":
		temp=memory.get('recall',{"one":True,"model":"game","field":"operators","filter":{"byname":me.S['P']['byname']}})
		import copy
		added_operators=copy.deepcopy(me.S['P'].getlist('operators'))
		for v in temp['operators'].split(','):
			if v in added_operators:
				added_operators.remove(v)
		#update game
		if len(added_operators)>0:
			temp=memory.get("recall",{"model":"operators","field":"operate_name as name,operator_id as id","key":"id","filter":'operator_id in ("%s")'%('","'.join(added_operators))})
			import json
			temp=json.dumps(temp)
			done=me.post('operators/add',{"operators":temp},me.S['P']['byname'])
	return model.edit()
	
def getAll():
	data={}
	temp=memory.get("recall",{"one":True,"model":"user","field":"game","filter":{"name":me.S['user']['name']}})
	data=memory.get("recall",{"model":"game","option":{"order":"id,desc"},"key":"key","field":"byname as `key`,name as `value`","filter":"byname in ('%s')"%("','".join(temp["game"].split(",")))})
	return data
	
def guide():
	if not user.inGroup("host"):return user.ban()
	return model.guide()
#locate operator
def locate():
	data=me.S['A'].get('game',0)
	if 'user' in me.S and 'game' in me.S['G']:
		#locate new operator
		temp=memory.get("recall",{"one":True,"model":"user","field":"game","filter":{"name":me.S['user']['name']}})
		if 'game' in me.S['G'] and me.S['G']['game'] in temp['game'].split(','):
			data=me.S['G']['game']
			me.S['A']['server']=0
	me.S['A']['game']=data