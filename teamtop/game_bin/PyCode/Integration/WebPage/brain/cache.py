#!/usr/bin/env python
# -*- coding:UTF-8 -*-
import time
M={}
def get(key):
	global M
	data=None
	if key in M and time.time()<M[key]['expire']:
		data=M[key]['value']
	return data
def set(key,value,expire=86400):
	global M
	import time
	M[key]={"value":value,"expire":time.time()+expire}
def getExpireTime(key):
	import tool
	data=''
	try:
		if key in M:
			data=tool.date(float(M[key]['expire']),"%Y-%m-%d %H:%M:%S")
	except:
		pass
	return data