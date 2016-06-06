#!/usr/bin/env python
# -*- coding:UTF-8 -*-
import os,sys
import traceback,cPickle,time,hashlib

S = {}
key = "follow-my-own-soul-in-time-"
# serve
def get(M):
	global S,key
	data = {}
	msg = M.POST.copy()
	if msg == {}:
		msg = M.GET.copy()
	# 来源
	#check permission
	if 'key' in msg and 'ts' in msg and (int(time.time()-time.timezone)-int(msg['ts'])) < 60 and msg['key'] == hashlib.md5(("%s%s"%(key,msg['ts'])).encode('utf-8')).hexdigest():
		try:
			url = M.META['PATH_INFO'].replace('serve/','/').strip('/').split('/')[0:2]

			sys.path.insert(0, os.path.dirname(__file__))
			App = __import__(url[0])
			To = getattr(App, url[1])
			data = To(msg)
		except:
			traceback.print_exc()
			data = {"tips":"error!"}
	else:
		data = {"tips":"Permission Denied!"}
	data = cPickle.dumps(data)
	from django.http import HttpResponse
	return HttpResponse(str(data))