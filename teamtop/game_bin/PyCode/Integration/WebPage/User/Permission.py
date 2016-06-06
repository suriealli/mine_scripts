#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 用户权限管理
#===============================================================================
import time
import json
import MySQLdb
import Environment
from ComplexServer.Plug.DB import DBHelp
from Integration import AutoHTML

#permission groups
group_list={'design':"策划", 'operate':"运营", 'develop':"开发",'host':"管理"}
public = set()
common = set()
design = set()
operate = set()
develop = set()
host = set()
log = set()

def group(funs, groups):
	for fun in funs:
		for group in groups:
			if isinstance(group, str):
				group_set = globals().get(group)
				if isinstance(group_set, set):
					group_set.add(AutoHTML.GetURL(fun))
					continue
			print "GE_EXC, can't find group(%s)" % group

def check(request, url):
	from Integration.WebPage.User import Permission
	if Environment.IsDevelop:
		return True
	if url in public:
		return True
	permission = request.session.get('permission')
	if permission is None:
		return False
	for group in permission:
		if url in getattr(Permission, group, []):
			return True
	return False

def getAll():
	data={}
	for p,v in group_list.items():
		data[p]={}
		data[p]['name']=v
		data[p]['value']=globals().get(p)
	return data
	
def monitor(request,response,url,force=False):
	if url in log or force:
		log_info={}
		if isinstance(request,dict):
			log_info=request
		else:
			log_info={
				"post":request.POST.copy(),
				"get":request.GET.copy(),
				"user":request.session.get('user',{}).get('name','unknown')+'/'+request.META['REMOTE_ADDR']
			}
		#log
		from ThirdLib import PrintHelp
		with DBHelp.ConnectHouTaiWeb() as cur:
			sql='insert into log_data (`url`,`time`,`user`,`get_data`,`post_data`,`response`) value ("%s","%s","%s","%s","%s","%s");' % (url,time.strftime('%Y-%m-%d %H:%M:%S'),log_info.get('user',''),MySQLdb.escape_string(PrintHelp.pformat(log_info.get('get',''))),MySQLdb.escape_string(PrintHelp.pformat(log_info.get('post',''))),MySQLdb.escape_string(str(response)))
			row = cur.execute(sql)
			return row > 0

def reg_public(fun):
	public.add(AutoHTML.GetURL(fun))

def reg_develop(fun):
	develop.add(AutoHTML.GetURL(fun))

def reg_operate(fun):
	operate.add(AutoHTML.GetURL(fun))

def reg_design(fun):
	design.add(AutoHTML.GetURL(fun))

def reg_host(fun):
	host.add(AutoHTML.GetURL(fun))

def reg_log(fun):
	log.add(AutoHTML.GetURL(fun))

def reg_common(fun):
	common.add(AutoHTML.GetURL(fun))

