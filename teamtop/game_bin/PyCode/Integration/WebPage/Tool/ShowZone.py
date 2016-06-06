#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 显示区
#===============================================================================
from django.http import HttpResponse
from ComplexServer.Plug.DB import DBHelp
from Integration import AutoHTML
from Integration.WebPage.User import Permission
from World import Define

html = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>区信息</title>
</head>
<body>
%s<br>
%s<br>
</body>
</html>'''

def ShowZone(request):
	'''【配置】--游戏区信息'''
	computers = {}
	mysqls = {}
	processs = {}
	zones = {}
	con = DBHelp.ConnectGlobalWeb()
	suff = AutoHTML.AsBool(request.GET, "tmp")
	if suff:
		suff = "_tmp"
	else:
		suff = ""
	with con as cur:
		cur.execute("select name, ip from computer%s;" % suff)
		for name, ip in cur.fetchall():
			computers[name] = ip
		cur.execute("select name, master_ip, master_port, master_user, master_pwd from mysql%s;" % suff)
		for name, ip, port, user, pwd in cur.fetchall():
			mysqls[name] = (ip, port, user, pwd)
		cur.execute("select pkey, computer_name, port, bind_zid, work_zid from process%s;" % suff)
		for pkey, computer_name, port, bind_zid, work_zid in cur.fetchall():
			processs[pkey] = (computer_name, port, bind_zid, work_zid, DBHelp.GetComputerPublicIP(cur, computer_name))
		cur.execute("select zid, name, ztype, language, all_process_key, c_process_key, d_process_key, ghl_process_key, mysql_name, public_ip, be_merge_zid, merge_zids from zone%s;" % suff)
		for zid, zname, ztype, language, all_process_key, c_process_key, d_process_key, ghl_process_key, mysql_name, public_ip, be_merge_zid, merge_zids in cur.fetchall():
			zones[zid] = (zname, ztype, language, all_process_key, c_process_key, d_process_key, ghl_process_key, mysql_name, public_ip, be_merge_zid, eval(merge_zids))
	
		control = AutoHTML.Table(["进程Key", "所在机器", "监听端口"], [], "全局控制进程")
		for pkey, (computer_name, port, _, _, _) in processs.iteritems():
			if not Define.IsControlProcessKey(pkey):
				continue
			machine_info = "%s.%s" % (computers[computer_name], computer_name)
			control.body.append((pkey, machine_info, port))
		control.body.sort()
		
		zone = AutoHTML.Table(["区ID", "区名", "MySQL连接", "区类型", "语言版本", "网关IP", "网关端口", "机器IP", "进程信息"], [], "区信息")
		for zid, (zname, ztype, language, all_process_key, c_process_key, d_process_key, ghl_process_key, mysql_name, public_ip, be_merge_zid, merge_zids) in zones.iteritems():
			if ztype == "Single":
				all_process = processs[all_process_key]
				assert zid == all_process[2]
				computer_name = all_process[0]
				machine_info = "%s.%s" % (computers[computer_name], computer_name)
				if not public_ip:
					public_ip = all_process[4]
				public_port = all_process[1]
				mysql = "mysql -h%s -P%s -u%s -p%s" % mysqls[mysql_name]
				process_info = []
				process_info.append((all_process_key, all_process[1]))
				process_info = AutoHTML.MakeInnerTable(process_info)
			elif ztype == "Standard":
				# 被合的区不显示在这里
				if be_merge_zid:
					continue
				d_process = processs[d_process_key]
				ghl_process = processs[ghl_process_key]
				assert d_process[0] == ghl_process[0]
				assert zid == d_process[2]
				assert zid == ghl_process[2]
				computer_name = ghl_process[0]
				machine_info = "%s.%s" % (computers[computer_name], computer_name)
				if not public_ip:
					public_ip = ghl_process[4]
				public_port = ghl_process[1]
				mysql = "mysql -h%s -P%s -u%s -p%s" % mysqls[mysql_name]
				process_info = []
				process_info.append((d_process_key, d_process[1]))
				process_info.append((ghl_process_key, ghl_process[1]))
				# 处理合区信息
				for merge_zid in merge_zids:
					cur.execute("select name, d_process_key, mysql_name from zone%s where zid = %s;" % (suff, merge_zid))
					merge_result = cur.fetchall()
					zname += "<br>-->%s" % merge_result[0][0]
					merge_d_process_key = merge_result[0][1]
					mysql += "<br>%s" % "mysql -h%s -P%s -u%s -p%s" % mysqls[merge_result[0][2]]
					process_info.append((merge_d_process_key, processs[merge_d_process_key][1]))
				process_info = AutoHTML.MakeInnerTable(process_info)
			else:
				assert False
			zone.body.append((zid, zname, mysql, ztype, language, public_ip, public_port, machine_info, process_info))
		zone.body.sort(key=lambda it:it[0])
		return HttpResponse(html % (control.ToHtml(), zone.ToHtml("top")))

Permission.reg_develop(ShowZone)
Permission.reg_design(ShowZone)

