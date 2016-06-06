# -*- coding:UTF-8 -*-
import time
import me,tool,memory,model,user
def add():
	if not user.inGroup("host"):return user.ban()
	return model.add()
	
def edit():
	if not user.inGroup("host"):return user.ban()
	return model.edit()
	
def getAll():
	data={}
	#operators available
	temp=model.get({
		"can_manage":{"one":True,"model":"user","field":"operator","filter":{"name":me.S['user']['name']}},
		"has_game":{"one":True,"model":"game","field":"operators","filter":{"byname":me.S['A']['game']}},
	})
	if not temp['can_manage'] or not temp['has_game']:
		return data
	temp=list(set(temp['can_manage']['operator'].split(',')).intersection(set(temp['has_game']['operators'].split(','))))
	data=memory.get("recall",{
		"model":model.info('operators')['name'],
		"key":"key",
		"filter":"%s in ('%s')"%(model.info('operators')['map']['id']['field'],"','".join(temp)),
		"field":"%s as `key`,%s as `value`"%(model.info('operators')['map']['id']['field'],model.info('operators')['map']['name']['field']),
		"option":{"order":"%s,asc"%(model.info('operators')['map']['id']['field'])}
	})
	return data

def guide():
	if not user.inGroup("host"):return user.ban()
	return model.guide()
#locate operator
def locate():
	data=me.S['A'].get('operator',0)
	if 'user' in me.S:
		#locate new operator
		temp=getAll()
		if 'operator' in me.S['G'] and int(me.S['G']['operator']) in temp:
			data=me.S['G']['operator']
	me.S['A']['operator']=data