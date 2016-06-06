#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 角色位置
#===============================================================================
import os
import struct
import datetime
from django.http import HttpResponse
from Common import Serialize
from Util import Time
from ThirdLib import BMP
from ComplexServer.Plug.DB import DBHelp
from Integration import AutoHTML, settings
from Integration.Help import WorldHelp
from Integration.WebPage.User import Permission
from Game.Role.Data import EnumInt32, EnumInt16

def Req(request):
	'''【数据与工具】--角色位置'''
	now = datetime.datetime.now()
	one_day_ago = now - datetime.timedelta(days = 1)
	return HttpResponse(html  % (AutoHTML.GetURL(Res), AutoHTML.ToDataBase(), op_select.ToHtml(), one_day_ago.strftime("%Y-%m-%d %H:%M:%S"), now.strftime("%Y-%m-%d %H:%M:%S")))

def Res(request):
	op = op_select.GetValue(request.POST)
	dbids = AutoHTML.AsDataBaseIDs(request.POST)
	condition = AutoHTML.AsString(request.POST, "condition")
	scene_id = AutoHTML.AsString(request.POST, "scene")
	start_time = AutoHTML.AsDateTime(request.POST, "start_time")
	end_time = AutoHTML.AsDateTime(request.POST, "end_time")
	
	if op == 0:
		return RoleLostPos(dbids[0], int(scene_id) if scene_id.isdigit() else 0, condition, start_time, end_time)
	elif op == 1:
		return ClientLost(dbids, scene_id, condition, start_time, end_time)
	else:
		return HttpResponse("别乱搞！")

def RoleLostPos(zone_id, scene_id, condition, start_time, end_time):
	con = DBHelp.ConnectMasterDBByID(zone_id)
	start_time = Time.DateTime2UnitTime(start_time)
	end_time = Time.DateTime2UnitTime(end_time)
	with con as cur:
		width = 0
		height = 0
		pos_list = []
		if condition:
			sql = "select array from role_data where %s and di32_10 > %s and di32_10 < %s;" % (condition, start_time, end_time)
		else:
			sql = "select array from role_data where di32_10 > %s and di32_10 < %s;" % (start_time, end_time)
		cur.execute(sql)
		for row in cur.fetchall():
			array = Serialize.String2PyObjEx(row[0])
			if array is None:
				continue
			i32 = struct.unpack("i" * (len(array[1]) / 4), array[1])
			scene = i32[EnumInt32.enLastPublicSceneID]
			if scene != scene_id:
				continue
			i16 = struct.unpack("h" * (len(array[2]) / 2), array[2])
			x = i16[EnumInt16.enLastPosX]
			y = i16[EnumInt16.enLastPosY]
			if x > width:
				width = x
			if y > height:
				height = y
			pos_list.append((x, y))
		bmp = BMP.bmp24(width + 100, height + 100)
		bmp.fill(BMP.back)
		bmp.drow_points(pos_list, BMP.white)
		now = datetime.datetime.now()
		file_name = "%s_%s_%s_%s_%s_%s_%s" % (zone_id, now.year, now.month, now.day, now.hour, now.minute, now.second)
		bmp.save_zip(settings.static_floder + os.sep, file_name)
		return HttpResponse("速度下载，可能会没了。。。<a href='/site_medias/%s.zip'>%s.zip</a>" % (file_name, file_name))

def ClientLost(dbids, replace, condition, start_time, end_time):
	if len(dbids) > 10:
		return HttpResponse("不能选择超过10个区！")
	
	info = []
	replace = eval(replace) if replace else {}
	
	for dbid in dbids:
		con = DBHelp.ConnectMasterDBByID(dbid)
		with con as cur:
			pf = replace.get("pf")
			if pf:
				cur.execute("select account, from_1, status from connect_info where connect_time > %s and connect_time < %s and from_1 = %s;", (start_time, end_time, pf))
			else:
				cur.execute("select account, from_1, status from connect_info where connect_time > %s and connect_time < %s;", (start_time, end_time))
			info.extend(cur.fetchall())
	
	if not condition:
		table = AutoHTML.Table(["账号", "渠道", "状态"], info, "客户端连接状态%s" % len(info))
		return HttpResponse(table.ToHtml())
	else:
		condition = eval(condition)
		d = {}
		if type(condition) is tuple:
			for _, _, status in info:
				status_list = []
				for s in status.split("|"):
					if not s.isdigit():
						continue
					s = int(s)
					if s in condition:
						continue
					s = replace.get(s, s)
					if s in status_list:
						continue
					status_list.append(s)
				status_string = "|".join([str(s) for s in status_list])
				d[status_string] = d.get(status_string, 0) + 1
		elif type(condition) is list:
			for _, _, status in info:
				status_list = []
				for s in status.split("|"):
					if not s.isdigit():
						continue
					s = int(s)
					if s in condition:
						continue
					s = replace.get(s, s)
					if s in status_list:
						continue
					status_list.append(s)
				for s in status_list:
					d[s] = d.get(s, 0) + 1
		elif condition == "wh":
			for _, _, status in info:
				w = None
				h = None
				b = -1
				for s in status.split("|"):
					if s == "28":
						b = 1
					if not s.startswith("-"):
						continue
					if w is None:
						w = int(s[1:])
					elif h is None:
						h = int(s[1:])
				if w is not None and h is not None:
					wh = b * ((w / 100 * 100) + (h / 100))
					if wh == 1193:
						print status
					d[wh] = d.get(wh, 0) + 1
		elif condition == "lsys":
			l = []
			for account, from_1, status in info:
				w = None
				h = None
				b = -1
				for s in status.split("|"):
					if not s.startswith("-"):
							continue
					if w is None:
						w = int(s[1:])
					elif h is None:
						h = int(s[1:])
				if h > 1000:
					l.append((account, from_1, status))
			table = AutoHTML.Table(["账号", "来源", "状态"], l, "客户端状态统计%s" % len(info))
			return HttpResponse(table.ToHtml())
		
		body = []
		for k, v in d.iteritems():
			body.append((v, k))
		if body:
			if type(body[0][1]) is int:
				body.sort(key=lambda item:item[1])
			else:
				body.sort(key=lambda item:item[0])
		table = AutoHTML.Table(["数量", "状态"], body, "客户端状态统计%s" % len(info))
		return HttpResponse(table.ToHtml())

op_select = AutoHTML.Select("op_select")
op_select.Append("角色流失图", 0)
op_select.Append("客户端流失情况", 1)

zone_select = AutoHTML.Select("zone_select")
for zone in WorldHelp.GetZone().values():
	zone_select.Append(zone.get_name(), zone.zid)

html = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>角色位置</title>
</head>
<body>
<form action="%s" method="POST" target="_blank">
%s<br>
%s<br>
场景ID<input type="text" name="scene" value=""/><br>
其他条件<input type="text" name="condition" value=""/><br>
开始<input type="text" name="start_time" value="%s"/><br>
结束<input type="text" name="end_time" value="%s"/><br>
<input type="submit" name="看看" />
</form>
</body>
</html>'''


Permission.reg_design(Req)
Permission.reg_design(Res)

