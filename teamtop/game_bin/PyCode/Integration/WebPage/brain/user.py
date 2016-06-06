#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 用户登录
#===============================================================================
import hashlib,traceback
import me,memory,body,model

def login():
	'''
	【用户】 登录系统
	'''
	data={}
	me.locateLang()
	#login ban
	import time
	if 'login_failed' not in me.S:
		me.S['login_failed']={"times":0,"ban":0}
	if me.S['login_failed']['times']>3:
		if time.time()-me.S['login_failed']['ban']<0:
			return {"tips":"登录失败次数过多，已被禁止登录！"}
		else:
			me.S['login_failed']={"times":0,"ban":0}
	#login
	if 'name' in me.S["P"]:
		account = me.S["P"].get("name","")
		pwd = me.S["P"].get("password","")
		code=me.S["P"].get("code","")
		if code=="" or code!=me.S['code']:
			data['tips']='信息输入不正确！'
		elif account=='' or pwd=='':
			data['tips']='输入参数不能存在空值！'
		else:
			pwd=encrypt(pwd)
			try:
				result=memory.get('recall',{"one":"true","model":"user","field":"ugroup,operator,name","filter":{"name":account,"password":pwd}})
				if result:
					# 保存session
					groups = result['ugroup']
					me.S['user']={"name":result['name'],"group":result['ugroup'],"operator":result['operator']}
					data['tips']="成功登录系统，请返回主菜单进行操作！"
					if 'before_login' in me.S:
						data['url']=me.S['before_login']
						del me.S['before_login']
					else:
						data['url']='/'
				else:
					#ban
					me.S['login_failed']['times']+=1
					data['tips']='信息输入不正确！'
					if me.S['login_failed']['times']>2:
						me.S['login_failed']['ban']=time.time()+300
						data['tips']="登录失败次数过多，已被禁止登录！"
			except:
				traceback.print_exc()
				data['tips']='数据库读取出错！'
		import log
		log.add(data['tips'])
	else:
		if 'user' in me.S:
			data['tips']="你当前已经登录，切换到其他用户请重新登录！"
	return data
def exit():
	'''
	【用户】 安全退出
	'''
	data={}
	if 'user' in me.S:
		del me.S['user']
	if 'before_login' in me.S:
		del me.S['before_login']
	data['tips']="你已经成功退出,请<a href='/user/login'>重新登录</a>!"
	return data

def add():
	if not inGroup("host"):return ban()
	if "password" in me.S["P"]:
		me.S["P"]["password"]=encrypt(me.S["P"]["password"])
	return model.add()
def encrypt(key):
	import hashlib
	salt="lostnote-follow-his-own-soul-in-teamtop-with-lots-of-beautiful-girls-who-smile-like-lovely-angels-make-the-god-lost-in-heaven-and-finally-become-a-lostnote"
	key=hashlib.md5('%s%s'%(hashlib.md5(key.encode('utf-8')).hexdigest(),salt)).hexdigest()
	return key
def editPassword():
	'''
	【用户】 修改密码
	'''
	if not 'user' in me.S:return ban()
	data={}
	if 'password' in me.S['P']:
		name=me.S['P'].get('name','')
		pwd=me.S['P'].get('password','')
		password_confirm=me.S['P'].get("password_confirm",'')
		
		tips=''
		data={}
		if pwd!='':
			if pwd!=password_confirm:
				tips="密码确认不一致！"
			else:
				data['password']=encrypt(pwd)
		if tips=='':
			#check new
			try:
				memory.get('remember',{"action":"edit","model":"user","filter":{"name":name},"data":data})
				del me.S['user']
				data['tips']="更新成功！请重新登录系统！"
			except:
				data['tips']="更新失败！请重试！"
	else:
		me.S['P']['name']=me.S['user']['name']
	return data

def edit():
	if not inGroup("host"):return ban()
	if 'password' in me.S['P']:
		if me.S['P']['password']=="":
			del me.S['P']['password']
		else:
			me.S['P']['password']=encrypt(me.S['P']['password'])
	return model.edit()

def ban():
	return {"tips":"请先登录！","url":"/user/login"}

def guide():
	if not inGroup("host"):return ban()
	return model.guide()

def inGroup(group):
	data=False
	if "user" in me.S and group in me.S["user"]["group"].split(","):
		data=True
	return data
def translate():
	if not inGroup("operate"):return ban()
	lang=me.S['P'].get('lang','')
	if lang in ["zh_cn","en_us"]:
		Word=me.review("words","heart")
		data=[]
		for k,v in Word.info.items():
			if lang!="zh_cn":
				k=v[lang]
			k=k.decode("utf8")
			data.append([k])
		fields=[lang]
		data.insert(0,fields)
		data=model.export(data,lang)
	return data