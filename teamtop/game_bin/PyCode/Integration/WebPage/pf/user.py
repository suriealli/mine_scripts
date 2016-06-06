#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 用户登录
#===============================================================================
import hashlib,traceback
from Integration.WebPage.User import Permission

def login(request):
	data={}
	if 'name' in request.POST:
		account = me.G(request,"name")
		pwd = me.G(request,"password")
		code=me.G(request,"code").upper()
		if not code or code=="" or code!=request.session['code']:
			data['tips']='验证码输入不正确！'
		elif account=='' or pwd=='':
			data['tips']='输入参数不能存在空值！'
		else:
			pwd=encrypt(pwd)
			try:
				result=me.M('recall',{"one":"true","model":"user","field":"ugroup,name","filter":{"name":account,"password":pwd}})
				if result:
					# 保存session
					groups = result['ugroup']
					request.session['permission'] = groups.split(',')
					request.session['user']={"name":result['name']}
					#lang
					if 'lang' in request.POST:
						request.session['lang']=request.POST['lang']
					
					data['tips']="成功登录系统，请返回主菜单进行操作！"
					if 'before_login' in request.session:
						data['url']=request.session['before_login']
						del request.session['before_login']
					else:
						data['url']='/'
				else:
					data['tips']='用户名或密码错误！'
			except:
				traceback.print_exc()
				data['tips']='数据库读取出错！'
		Permission.monitor(request,data['tips'],"user/login",True)
		
	else:
		if 'user' in request.session:
			data['tips']="你当前已经登录，切换到其他用户请重新登录！"
	return data
def encrypt(key):
	import hashlib
	salt="lostnote-follow-his-own-soul-in-teamtop-with-lots-of-beautiful-girls-who-smile-like-lovely-angels-make-the-god-lost-in-heaven-and-finally-become-a-lostnote"
	key=hashlib.md5('%s%s'%(hashlib.md5(key.encode('utf-8')).hexdigest(),salt)).hexdigest()
	return key
def exit(request):
	data={}
	request.session['permission'] = []
	if 'user' in request.session:
		del request.session['user']
	if 'before_login' in request.session:
		del request.session['before_login']
	data['tips']="你已经成功退出!"
	return data

def add(request):
	data={}
	get={}
	if 'name' in request.POST:
		get['name'] = me.G(request,"name")
		get['password'] = me.G(request,"password")
		get['password_confirm'] = me.G(request,"password_confirm")
		get['group'] = request.POST.getlist("group")
		get['real_name'] = me.G(request,"real_name")
		ugroup=','.join(get['group'])
		if get['name']=='' or get['password']=='' or get['password_confirm']=='' or ugroup=='' or get['real_name']=='':
			data['tips']='输入参数不能存在空值！'
		elif get['password']!=get['password_confirm']:
			data['tips']='密码确认不一致！'
		else:
			get['password']=encrypt(get['password'])
			try:
				#if exist
				temp=me.M('recall',{"one":"true","model":"user","field":"name","filter":{"name":get['name']}})
				if temp:
					data['tips']='已经存在同名管理员！'
				else:
					me.M('remember',{"model":"user","data":{"real_name":get['real_name'],"name":get['name'],"password":get['password'],"ugroup":ugroup}})
					data['tips']='已经成功增加管理员%s！' % get['name']
			except:
				data['tips']='增加失败，请重新添加或联系管理员！'
	data['get']=get
	data['permissions']=Permission.getAll()
	data['groups']=Permission.group_list
	return data

def editPassword(request):
	data={}
	if 'password' in request.POST:
		name=me.G(request,'name')
		pwd=me.G(request,'password')
		password_confirm=me.G(request,"password_confirm")
		
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
				me.M('remember',{"action":"edit","model":"user","filter":{"name":name},"data":data})
				del request.session['user']
				data['tips']="更新成功！请重新登录系统！"
			except:
				data['tips']="更新失败！请重试！"
	else:
		data['name']=request.session['user']['name']
	return data

def edit(request):
	data={}
	uid=0
	if 'uid' in request.GET:
		uid=me.G(request,'uid','int')
		
	if 'uid' in request.POST: #update
		uid=me.G(request,"uid","int")
		ugroup = ','.join(me.G(request,"ugroup","list"))
		password=me.G(request,"password")
		password_confirm=me.G(request,"password_confirm")
		
		tips=''
		data={}
		data['ugroup']=ugroup
		if password!='':
			if password!=password_confirm:
				tips="密码确认不一致！"
			else:
				data['password']=encrypt(password)
		if tips=='':
			#check new
			try:
				me.M('remember',{"action":"edit","model":"user","filter":{"uid":uid},"data":data})
				data['tips']="更新成功！"
			except:
				data['tips']="更新失败！请重试！"
			
	if uid!=0:
		data['user']=me.M('recall',{"one":"true","model":"user","field":"uid,name,ugroup","filter":{"uid":uid}})
		data['ugroup']=data['user']['ugroup'].split(',')
		data['groups']=Permission.group_list
		return data
	
def list(request):
	data={}
	range_info=me.getRange(request,{"size":"20","model":"user","url":"/model/user/list"})
	data['range']=range_info['html']
	data['users']=me.M("recall",{"model":"user","field":"uid,name,real_name,ugroup","range":range_info['range']});
	return data

def log(request): #查看登录后操作记录
	data={}
	range_info=me.getRange(request,{"size":"20","model":"log_data","url":"/model/user/log"})
	data['range']=range_info['html']
	data['logs']=me.M('recall',{"model":"log_data","field":"time, user, get_data, post_data, response","range":range_info['range'],"option":{"order":"time,desc"}})
	return data

Permission.group([login,exit],['public'])
Permission.group([add,edit,list],['host'])
Permission.group([log],['host'])
#Permission.group([add],['log'])