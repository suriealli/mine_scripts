#!/usr/bin/env python
# -*- coding:UTF-8 -*-
import traceback

def setServerQQ(msg=None):
	if not msg:msg={}
	data={}
	if msg.get('qq','')=='' or msg.get('server','')=='':
		data['tips']="QQ或SERVER不能为空"
		return data
	servers=msg['server'].split(',')
	from Integration.Help import Concurrent
	from Integration.WebPage.brain import tool
	command='''
import Game.SysData.WorldData as A
A.SetGameServiceQQ(%s)'''
	try:
		tg = Concurrent.TaskGroup()
		from django.utils import encoding
		command=command%(msg['qq'])
		command=encoding.smart_str(command)
		for v in servers:
			tg.append(Concurrent.GMTask('GHL%s'%v,command))
		tg.execute()
		data['tips']="成功设置服(%s)VIP服务QQ为(%s)"%(msg['server'],msg['qq'])
	except:
		data['tips']="设置失败，请重试或联系管理员！"
		traceback.print_exc()
	#print data
	return data