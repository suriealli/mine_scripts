#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.Interface.YYBan")
#===============================================================================
# YY--封禁
#===============================================================================
import time
import traceback
import md5
import json
from django.http import HttpResponse
from Integration.Help import OtherHelp
from Integration import AutoHTML
from Integration.WebPage.User import Permission
from ComplexServer.Plug.DB import DBHelp

KEY = "YYBan_#gexdgk0_ufdj_f9"

#正式接口
def banSpeak(request):
	return _ban(request,{"type":"speak"})

def cancelBanSpeak(request):
	return _ban(request,{"type":"ban_speak"})

def banLogin(request):
	return _ban(request,{"type":"login"})

def cancelBanLogin(request):
	return _ban(request,{"type":"ban_login"})

def _ban(request,c):
	if not c:
		c = {}

	accounts = AutoHTML.AsString(request.GET, 'accounts')
	game = AutoHTML.AsString(request.GET, 'game')
	server = AutoHTML.AsString(request.GET, 'server')
	unixtime = AutoHTML.AsInt(request.GET, 'ts')
	sign = AutoHTML.AsString(request.GET, 'sign')
	
	# 若是禁言，增加keeptime
	keeptime = ''
	c['end_time'] = int(unixtime) + 3600
	if c['type'] == 'speak':
		keeptime = AutoHTML.AsInt(request.GET, 'keeptime')
		c['end_time'] = int(unixtime) + 60*int(keeptime)
	c['expire_time'] = int(unixtime) - 864000

	#验证时间
	if abs(time.time() - unixtime) > 900:
		return HttpResponse(-1)
	
	#签名验证
	if sign.lower() != md5.new("%s%s%s%s%s%s" % (accounts,keeptime,game,server,unixtime,KEY)).hexdigest():
		#return HttpResponse(-2);
		return HttpResponse(-1)
	
	# 转换帐号为角色ID
	accounts = accounts.split(',')

	con = DBHelp.ConnectMasterDBByID_HasExcept(server)
	if not con:
		#return HttpResponse(-3)
		return HttpResponse(-1)

	SQL = 'select role_id from role_data where account in ("%s")' % ('","'.join(accounts))
	c['role_id'] = []
	with con as cur:
		cur.execute(SQL)
		result = cur.fetchall()
		if not result:
			#print "YYBan:No accounts valid!"
			#return HttpResponse(-4)
			return HttpResponse(-1)
		for v in result:
			c['role_id'].append(str(v[0]))
		if len(c['role_id']) != len(accounts):
			#print "YYBan:Not all accounts valid!"
			#return HttpResponse(-5)
			return HttpResponse(-1)
	c['role_id'] = ','.join(c['role_id'])

	try:
		from Integration.WebPage.pf import role
		role.ban(c)
	except:
		#c['traceback'] = traceback.format_exc()
		#return HttpResponse(json.dumps(c))
		return HttpResponse(-1)

	return HttpResponse(1)

Permission.reg_public(banSpeak)
Permission.reg_public(cancelBanSpeak)
Permission.reg_public(banLogin)
Permission.reg_public(cancelBanLogin)