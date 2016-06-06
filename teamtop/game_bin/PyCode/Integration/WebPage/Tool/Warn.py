#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 警告管理模块
#===============================================================================
import md5
import datetime
from django.http import HttpResponse
from ComplexServer.Plug.DB import DBHelp
from Integration import AutoHTML
from Integration.Help import WorldHelp
from Integration.WebPage.User import Permission

def AddWarn(request):
	zone_id = AutoHTML.AsInt(request.GET, "zone_id")
	text = AutoHTML.AsString(request.GET, "text")
	tkey = MakeKey(text)
	
	con = DBHelp.ConnectHouTaiWeb()
	with con as cur:
		h = cur.execute("insert into warn (zone_id, tkey, recv_time, text, is_read) values(%s, %s, now(), %s, 0);", (zone_id, tkey, text))
		cur.close()
		return HttpResponse(str(h))

def GetWarn(request):
	cnt = AutoHTML.AsInt(request.GET, "cnt")
	con = DBHelp.ConnectHouTaiWeb()
	with con as cur:
		cur.execute("select wid, zone_id, tkey, recv_time, text from warn where is_read = 0 limit %s;" % cnt)
		result = cur.fetchall()
		# 标记为已读
		max_wid = 0
		for row in result:
			if row[0] > max_wid:
				max_wid = row[0]
		if max_wid:
			cur.execute("update warn set is_read = 1 where wid <= %s" % max_wid)
		# 删除旧数据
		two_day_ago = datetime.datetime.now() - datetime.timedelta(days = 2)
		cur.execute("delete from warn where recv_time < %s;", two_day_ago)
		return HttpResponse(repr(result))

def GetWarnEx(request):
	tkey = AutoHTML.AsString(request.GET, "tkey")
	con = DBHelp.ConnectHouTaiWeb()
	
	with con as cur:
		if tkey.isdigit():
			cur.execute("select zone_id, recv_time, text, is_read from warn limit %s,1000;" % tkey)
		else:
			cur.execute("select zone_id, recv_time, text, is_read from warn where tkey = %s;", tkey)
		result = cur.fetchall()
		cur.close()
	table = AutoHTML.Table(["区", "时间", "内容", "是否读取"])
	for zone_id, recv_time, text, is_read in result:
		table.body.append((WorldHelp.GetFullNameByZoneID(zone_id), recv_time, AutoHTML.PyStringToHtml(text), is_read))
	return HttpResponse(table.ToHtml())

def MakeKey(text):
	m = md5.new()
	pos = text.find("GE_EXC")
	if pos != -1:
		b = False
		for idx in xrange(pos, len(text)):
			c = text[idx]
			#忽视检测括号中的内容(除去重复的内容)
			if c == '(':
				b = True
				continue
			if c == ')':
				b = False
				continue
			if b:
				continue
			m.update(c)
	elif text.find("Traceback") != -1:
		for row in text.split('\n'):
			if not row.startswith('  File "'):
				continue
			m.update(row)
	else:
		m.update(text)
	return m.hexdigest()

Permission.reg_public(AddWarn)
Permission.reg_public(GetWarn)
Permission.reg_public(GetWarnEx)

