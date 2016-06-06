#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
import me,server

#获取请求开始处理
def guide(R):
	get={}
	data={}
	data['server']=int(R.session.get('server','0'))
	data['server_tips']='切换游戏服成功！'
	if data['server']==0:
		data['server']=server.getLast()
		R.session['server']=data['server']
		data['server_tips']="已为你选择最新游戏服！"
	data['servers']=server.getAll()
	get['server']=me.G(R,'server')
	if get['server']:
		R.session['server']=get['server']
		data['url']='/model'
		return data
	rights=me.getRights(R)
	from collections import OrderedDict
	rights=OrderedDict(sorted(rights.items(), key=lambda t: t[0]))
	data['guides']={}
	for k,v in rights.items():
		m=k.split('_')
		if m[0]=='guide':
			continue
		if not me.models[m[0]] in data['guides']:
			data['guides'][me.models[m[0]]]=[]
		data['guides'][me.models[m[0]]].append({"url":"/model/%s/%s" % (m[0],m[1]),"name":v['name']})
	return data