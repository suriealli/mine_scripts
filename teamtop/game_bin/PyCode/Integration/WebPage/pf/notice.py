#!/usr/bin/env python
# -*- coding:UTF-8 -*-
import traceback

def send(msg=None):
	data={}
	if not msg:msg={}
	#instance notice
	from django.utils import encoding
	msg['content']=msg['content'].replace("'",'').replace('"','')
	command='import cRoleMgr;cRoleMgr.Msg(1,0,"%s")' % msg['content']
	command=encoding.smart_str(command)
	#send
	import server
	for v in msg['server'].split(','):
		try:
			data['track']='P:%s|R:%s|%s,'%('%s'%v,server.sendCommand('%s'%v,command),msg['now_time'])
		except:
			traceback.print_exc()
			data['track']='P:%s|R:%s|%s,'%('%s'%v,"0",msg['now_time'])
			pass
	data['tips']="发送%s(P:服务器ID,R:结果)：%s"%(command,data['track'])
	return data