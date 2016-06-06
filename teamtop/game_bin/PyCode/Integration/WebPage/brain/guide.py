#!/usr/bin/env python
# -*- coding:UTF-8 -*-
import traceback
import me,user,game,operators,server,model,memory,right,cache
#guide user to take action
def guide():
	if "user" not in me.S:return user.ban()
	data={}
	#cache
	if 'cache' in me.S['G']:
		if me.S['G']['cache']=="empty":
			cache.M={}
		elif me.S['G']['cache']=="track":
			if 'key' in me.S['G']:
				print cache.M.get(me.S['G']['key'],{})
			else:
				print cache.M
		elif me.S['G']['cache']=="keys":
			print cache.M.keys()
	#/cache
	#locate lang
	if 'lang' in me.S['G']:
		me.S['A']['lang']=me.S['G']['lang']
	elif 'lang' not in me.S['A']:
		me.S['A']['lang']="zh_cn"
	#/locate language
	#locate operator and server
	game.locate()
	#update model info
	model.info()
	operators.locate()
	server.locate()
	
	try:
		data['server_info']=server.getInfo()
	except:
		pass
		#traceback.print_exc()
	#get rights
	rights=right.getAll()
	#guides
	data['guides']={}
	for k,v in rights.items():
		m=k.split('_')
		if not m[0] in data['guides']:
			#not this model info
			if m[0] not in model.info():
				continue
			data['guides'][m[0]]={"name":model.info(m[0])['label'],"rights":[]}
		data['guides'][m[0]]["rights"].append({"url":"/%s/%s" % (m[0],m[1]),"name":v['name']})
	from collections import OrderedDict
	data['guides']=OrderedDict(sorted(data['guides'].items(), key=lambda t: t[0]))
	#get games,operators,servers and set default
	data['games']=game.getAll()
	#S['A']['game']=0;S['A']['operator']=0;S['A']['server']=0;
	if str(me.S['A'].get('game',0))=="0":
		me.S['A']['game']=data['games'].keys()[0]
		game.locate()
	data['operators']=operators.getAll()
	if str(me.S['A'].get('operator',0))=="0":
		me.S['A']['operator']=data['operators'].keys()[0]
		operators.locate()
	data['servers']=server.getAll()
	if str(me.S['A'].get('server',0))=="0":
		try:
			me.S['A']['server']=data['servers'].keys()[0]
			server.locate()
		except:
			traceback.print_exc()
			pass
	#other info
	data['links_count']=memory.links_count
	return data