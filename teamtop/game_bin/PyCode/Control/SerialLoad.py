#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Control.SerialLoad")
#===============================================================================
# 串行载入数据
#===============================================================================
import cDateTime
import cComplexServer
from Common import Define
from Control import ProcessMgr
from Common.Message import PyMessage

def load_zone_mysql_info():
	from ComplexServer.Plug.DB import DBHelp
	if not Define.SERIAL_LOAD:
		return
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		cur.execute("select zid, mysql_name from zone where be_merge_zid = 0;")
		for zid, mysql_name in cur.fetchall():
			ZONE_ID_TO_MYSQL_NAME[zid] = mysql_name

def on_request_load(sessionid, msg):
	global REQUEST_LOAD_CNT, SUCCESS_LOAD_CNT, WAIT_LOAD_CNT
	processid, _, _ = msg
	mysql_name = ZONE_ID_TO_MYSQL_NAME.get(processid)
	if mysql_name is None:
		print "GE_EXC, unknown mysql name by process id(%s)." % processid
		mysql_name = "unknown"
	load_info = MYSQL_NAME_TO_LOAD_INFO.setdefault(mysql_name, {})
	load_log = load_info.setdefault(msg, [])
	load_log.append("request at %s" % cDateTime.Now())
	REQUEST_LOAD_CNT += 1
	# 加速载入
	if not WAIT_LOAD_CNT:
		check_per_minute()

def on_success_load(sessionid, msg):
	global REQUEST_LOAD_CNT, SUCCESS_LOAD_CNT, WAIT_LOAD_CNT
	processid, _, _ = msg
	mysql_name = ZONE_ID_TO_MYSQL_NAME.get(processid)
	if mysql_name is None:
		print "GE_EXC, unknown mysql name by process id(%s)." % processid
		mysql_name = "unknown"
	load_info = MYSQL_NAME_TO_LOAD_INFO[mysql_name]
	load_log = load_info[msg]
	load_log.append("success at %s" % cDateTime.Now())
	load_log.append("success")
	SUCCESS_LOAD_CNT += 1
	WAIT_LOAD_CNT -= 1
	# 加速载入
	if not WAIT_LOAD_CNT:
		check_per_minute()

def check_per_minute():
	global REQUEST_LOAD_CNT, SUCCESS_LOAD_CNT, WAIT_LOAD_CNT
	if REQUEST_LOAD_CNT == SUCCESS_LOAD_CNT:
		return
	cnt = 0
	for load_info in MYSQL_NAME_TO_LOAD_INFO.itervalues():
		for msg, load_log in load_info.iteritems():
			if load_log[-1] == "success":
				continue
			processid, ptype, name = msg
			control_process = ProcessMgr.ControlProcesssIds.get(processid)
			if control_process is None:
				print "GE_EXC, can't find control process by process id(%s)" % processid
				continue
			cComplexServer.SendPyMsg(control_process.session_id, PyMessage.Control_CommandLoad, (ptype, name))
			cnt += 1
			WAIT_LOAD_CNT += 1
			if cnt >= MAX_LOAD_CNT:
				return

if "_HasLoad" not in dir():
	MAX_LOAD_CNT = 100
	REQUEST_LOAD_CNT = 0
	WAIT_LOAD_CNT = 0
	SUCCESS_LOAD_CNT = 0
	ZONE_ID_TO_MYSQL_NAME = {}
	MYSQL_NAME_TO_LOAD_INFO = {}
	load_zone_mysql_info()
	cComplexServer.RegAfterNewMinuteCallFunction(check_per_minute)
	cComplexServer.RegDistribute(PyMessage.Control_RequestLoad, on_request_load)
	cComplexServer.RegDistribute(PyMessage.Control_SuccessLoad, on_success_load)
