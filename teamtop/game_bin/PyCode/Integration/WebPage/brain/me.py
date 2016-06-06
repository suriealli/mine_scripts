#!/usr/bin/env python
# -*- coding:UTF-8 -*-
import traceback
#request
R={}
#models witch need request
NR=[]
S=None
#take action
def act():
	data={}
	#log
	#check permission
	import user
	if not user.can():
		return user.ban()
	import action
	action_id=action.start()
	#action not start
	if isinstance(action_id,dict):
		return action_id
	
	Action=False
	#this model Action
	try:
		Model=review(S['A']['model'])
		Action=getattr(Model,S['A']['action'])
	except:
		traceback.print_exc()
		pass
	#common model action
	if not Action:
		try:
			Model=review('model')
			Action=getattr(Model,S['A']['action'])
		except:
			traceback.print_exc()
			pass
	#take action
	if Action:
		if S['A']['model'] in NR:#need original request
			data=Action(R)
		else:
			try:
				data=Action()
			except:
				pass
				if 'user' in S:
					traceback.print_exc()
		if not data:
			data={}
	else:
		data={"tips":"No This Action!"}
	#log
	action.end(action_id)
	return data

#get request
def get(M):
	global R
	global S
	R=M #global request
	S=M.session
	if 'A' not in S:
		S['A']={}
	S['G']=M.GET.copy()
	S['P']=M.POST.copy()
	S["path"]=M.META['PATH_INFO']
	m={}
	m=getPath(S["path"])
	#session
	S['A']['model']=m['model']
	S['A']['action']=m['action']
	S['A']['ip']=M.META['REMOTE_ADDR']
	S['A']['host']=M.META['HTTP_HOST']
	prepare()
	import body
	#act
	# import cProfile, pstats, StringIO
	# pr = cProfile.Profile()
	# pr.enable()
	body.data=act()
	# pr.disable()
	# s = StringIO.StringIO()
	# sortby = 'cumulative'
	# ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
	# ps.print_stats()
	# print s.getvalue()
	#show
	data=body.show()
	#just for redirect
	from django.http import HttpResponse
	if isinstance(data,dict):
		if 'url' in data:
			from django.http import HttpResponseRedirect
			return HttpResponseRedirect(data['url'])
		if 'response' in data:
			return HttpResponse(data['response'])
		if 'return' in data:
			if 'type' in data:
				return HttpResponse(data['return'],data['type'])
			return data['return']
	return HttpResponse(str(data))
	
#get path info
def getPath(url):
	m={}
	url=url.strip('/').split('/')[0:2]
	m['model']='guide'
	m['action']='guide'
	if len(url)>0:
		if url[0]!='':
			m['model']=url[0]
	if len(url)>1:
		m['action']=url[1]
	return m
#preparation
def prepare():
	import os
	S.set_expiry(0)
	S['ME']=os.path.dirname(os.path.dirname(__file__))
	review('','brain') #brain
#review models
def review(m='',path='brain'):
	import os,sys
	if path!='' and m=="":
		full_path=os.path.dirname(__file__).replace('brain','')+path
		try:
			sys.path.remove(full_path)
		except:
			pass
		sys.path.insert(1,full_path)
	#get model
	if m!='':
		if path!='':
			m=__import__('%s.%s'%(path,m),fromlist=[m])
		else:
			m=__import__(m)
		return m
def serve(M):
	keys={
		"default":"follow-my-own-soul-in-time-",
		"3737":"from-3737-in-time-"
	}
	data={}
	#get serve msg
	msg=M.POST.copy()
	if msg=={}:
		msg=M.GET.copy()
	#来源
	source=msg.get('from','default')
	import time,hashlib
	#check permission
	if 'key' in msg and 'ts' in msg and (int(time.time()-time.timezone)-int(msg['ts']))<60 and msg['key']==hashlib.md5(("%s%s"%(keys[source],msg['ts'])).encode('utf-8')).hexdigest():
		try:
			global S
			S=M.session
			if 'A' not in S:
				S['A']={}
			#session
			m=getPath(M.META['PATH_INFO'].replace('serve/','/'))
			S['A']['model']=m['model']
			S['A']['action']=m['action']
			S['A']['ip']=M.META['REMOTE_ADDR']
			S['A']['host']=M.META['HTTP_HOST']
			prepare()
			Model=__import__('serve.%s'%m['model'],globals,locals,[m['model']])
			Action=getattr(Model,m['action'])
			data=Action(msg)
		except:
			traceback.print_exc()
			data={"tips":"error!"}
	else:
		data={"tips":"Permission Denied!"}
	if 'format' in msg and msg['format']=='json':
		import tool,json
		data=json.dumps(tool.filterDecimal(data))
	else:
		import cPickle
		data=cPickle.dumps(data)
	from django.http import HttpResponse
	return HttpResponse(str(data))

def post(path,msg=None,game=None):
	if not 'user' in S:return user.ban()
	data={}
	if not msg:msg={}
	if not game:game=S['A']['game']
	#get server url
	import tool,memory,copy
	temp=memory.get("recall",{"one":True,"model":"game","field":"`server`","filter":{"byname":game}})
	temp=eval(tool.filterJSON(temp['server']))
	try:
		path='%sserve/%s'%(temp.get(str(S['A']['operator']),temp.get('other','')),path)
		#set key
		import time,hashlib
		msg=copy.deepcopy(msg)
		msg['ts']=int(time.time()-time.timezone)
		msg['key']=hashlib.md5(("follow-my-own-soul-in-time-%s"%msg['ts']).encode('utf-8')).hexdigest()
		
		#post
		import requests,json
		get=requests.post(path,msg)
		if get.status_code==200:
			try:
				import cPickle
				data=cPickle.loads(get.text.encode('utf-8'))
			except:
				traceback.print_exc()
				data={"tips":get.text}
		else:
			data={"tips":get.status_code}
	except:
		traceback.print_exc()
	return data
def locateLang():
	#locate lang
	if 'lang' in S['G']:
		S['A']['lang']=S['G']['lang']
	elif 'lang' not in S['A']:
		S['A']['lang']="zh_cn"