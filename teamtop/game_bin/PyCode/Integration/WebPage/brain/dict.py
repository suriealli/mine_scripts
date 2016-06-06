#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# lostnote
#===============================================================================
import me,body,user,memory

def manage():
	if not user.inGroup("develop"):return user.ban()
	data={}
	data['types']={"config":"设置","script":"脚本"}
	from World import Define
	data['languages']=Define.Language[1:]
	#type
	me.S['P']['G']['type']=me.S['P']['G'].get('type','config')
	me.S['P']['G']['language']=me.S['P']['G'].get('language','english')
	if me.S['P']['G'].get('update')=='true': #update
		old=me.S['P']['P'].get("old","")
		new=me.S['P']['P'].get("new","")
		key=me.S['P']['P'].get("key","")
		#check new
		import re,json
		if re.findall(r'%[a-zA-Z]{1,2}',old,re.VERBOSE) != re.findall(r'%[a-zA-Z]{1,2}',new,re.VERBOSE):
			data['response']=json.dumps({"result":"false","key":key,"tips":"%通配符不匹配!"})
		try:
			memory.get('remember',{"memory":"global","action":"edit","model":"language_"+me.S['P']['G']['type']+"_"+me.S['P']['G']['language'],"filter":{"source_text":old},"data":{"target_text":new}})
			data['response']=json.dumps({"result":"true","key":key})
		except:
			data['response']=json.dumps({"result":"false","key":key,"tips":"更新失败,请重试!"})
		return data
	#list words
	range_info=body.getRange({"memory":"global","size":"20","model":"language_"+me.S['P']['G']['type']+"_"+me.S['P']['G']['language'],"url":me.S['P']['path'],"msg":{"type":me.S['P']['G']['type'],"language":me.S['P']['G']['language']}})
	data['range']=range_info['html']
	data['words']=memory.get('recall',{"memory":"global","field":"source_text,target_text","model":"language_"+me.S['P']['G']['type']+"_"+me.S['P']['G']['language'],"range":range_info['range']})
	return data

