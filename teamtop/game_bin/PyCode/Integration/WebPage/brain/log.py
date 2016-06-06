# -*- coding:UTF-8 -*-
import time,traceback
import me,tool,memory,user,model
def add(msg):
	import MySQLdb
	data=memory.get("remember",{"model":"log","data":{
		"get":MySQLdb.escape_string(str(me.S['G'])),
		"post":MySQLdb.escape_string(str(me.S['P'])),
		"url":me.S['path'],
		"user":"%s/%s"%(me.S.get('user',{"name":"unknown"})['name'],me.S['A']['ip']),
		"time":time.strftime('%Y-%m-%d %H:%M:%S'),
		"response":str(msg)
	}})
	return data

def edit():
	if not user.inGroup("operate"):return user.ban()
	return model.edit()
def guide():
	if not user.inGroup("operate"):return user.ban()
	msg={}
	me.S['G']['order']=me.S['G'].get('order','time,desc')
	return model.guide()
	
def send(nid):
	data={}
	msg=memory.get("recall",{"one":True,"filter":{"nid":nid}})
	data=game.act(msg)
	return data