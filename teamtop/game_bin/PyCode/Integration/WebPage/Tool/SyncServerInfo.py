#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 同步服信息
#===============================================================================
import json
import Environment
from django.http import HttpResponse
from ComplexServer.Plug.DB import DBHelp
from Integration.WebPage.User import Permission

def Reg_Interface(request):
	'''【测试】--同步服信息'''
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		zones = []
		cur.execute("select zid, name, ztype, public_ip, all_process_key, ghl_process_key, be_merge_zid from zone;")
		for zid, name, ztype, public_ip, all_process_key, ghl_process_key, be_merge_zid in cur.fetchall():
			if be_merge_zid:
				cur.execute("select ghl_process_key from zone where zid = %s;" % be_merge_zid)
				pkey = cur.fetchall()[0][0]
			else:
				if ztype == "Single":
					pkey = all_process_key
				elif ztype == "Standard":
					pkey = ghl_process_key
				else:
					continue
			cur.execute("select port, computer_name from process where pkey = %s;", pkey)
			result = cur.fetchall()
			port = result[0][0]
			if not public_ip:
				computer_name = result[0][1]
				public_ip = DBHelp.GetComputerPublicIP(cur, computer_name)
			zones.append((zid, public_ip, port, name))
	zones.sort(key=lambda item:item[0])
	return HttpResponse("var js_server_info = %s" % json.dumps(zones))

if Environment.IsDevelop:
	Permission.reg_public(Reg_Interface)
else:
	Permission.reg_develop(Reg_Interface)

