#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# lostnote
#===============================================================================
import me

def manage(R):
	data={}
	path='/model/dict/manage'
	data['types']={"config":"设置","script":"脚本"}
	from World import Define
	data['languages']=Define.Language[1:]
	#type
	get={}
	get['type']=R.GET.get('type','config')
	get['language']=R.GET.get('language','english')
	data['get']=get
	if R.GET.get('update')=='true': #update
		old=me.G(R,"old")
		new=me.G(R,"new")
		key=me.G(R,"key")
		#check new
		import re,json
		if re.findall(r'%[a-zA-Z]{1,2}',old,re.VERBOSE) != re.findall(r'%[a-zA-Z]{1,2}',new,re.VERBOSE):
			data['response']=json.dumps({"result":"false","key":key,"tips":"%通配符不匹配!"})
		try:
			me.M('remember',{"memory":"global","action":"edit","model":"language_"+get['type']+"_"+get['language'],"filter":{"source_text":old},"data":{"target_text":new}})
			data['response']=json.dumps({"result":"true","key":key})
		except:
			data['response']=json.dumps({"result":"false","key":key,"tips":"更新失败,请重试!"})
		return data
	#list words
	range_info=me.getRange(R,{"memory":"global","size":"20","model":"language_"+get['type']+"_"+get['language'],"url":path,"msg":{"type":get['type'],"language":get['language']}})
	data['range']=range_info['html']
	data['words']=me.M('recall',{"memory":"global","field":"source_text,target_text","model":"language_"+get['type']+"_"+get['language'],"range":range_info['range']})
	return data

