#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 保存VIP角色数据
#===============================================================================
import os
import sys
path = os.path.dirname(os.path.realpath(__file__))
path = path[:path.find("PyCode") + 6]
if path not in sys.path: sys.path.append(path)
path = path.replace("PyCode", "PyHelp")
if path not in sys.path: sys.path.append(path)

import datetime
import traceback
from MySQLdb import cursors
from Util import OutBuf
from Common import Define, CValue
from ComplexServer.Plug.DB import DBHelp
from Integration.Help import WorldHelp

if "_HasLoad" not in dir():
	SaveRoleIDs = []

def SaveVIP():
	global SaveRoleIDs
	SaveRoleIDs = []
	now = datetime.datetime.now()
	date = "%s_%s_%s" % (now.year, now.month, now.day)
	with OutBuf.OutBuf() as Out:
		try:
			RealSaveVIP(date)
		except:
			traceback.print_exc()
		# 写保存日志
		with open("out.txt", "a") as f:
			f.write(Out.get_value())

def RealSaveVIP(date):
	global_con = DBHelp.ConnectGlobalWeb()
	with global_con as global_cur:
		for zid in WorldHelp.GetZone().iterkeys():
			try:
				SaveOneZone(global_cur, zid, date)
			except:
				traceback.print_exc()
		global_cur.close()

def SaveOneZone(global_cur, zid, date):
	zone_con = DBHelp.ConnectMasterDBByID(zid)
	zone_con.cursorclass = cursors.DictCursor
	with zone_con as zone_cur:
		# di32_12:VIP di32_0：活跃时间
		zone_cur.execute("select * from role_data where di32_12 > 2 and unix_timestamp(now()) - di32_0 < %s;" % DBHelp.TwoWeekSecond)
		for role_data in zone_cur.fetchall():
			try:
				SaveOneRoleForBack(global_cur, zone_cur, role_data, date)
			except:
				traceback.print_exc()
		zone_cur.close()

def SaveOneRoleForBack(global_cur, zone_cur, role_data, date):
	role_id = role_data["role_id"]
	SaveRoleIDs.append(role_id)
	zone_cur.execute("select * from role_obj_%s where role_id = %s;" % (role_id % Define.ROLE_HORIZONTAL_TABLE, role_id))
	role_objs = zone_cur.fetchall()
	bid = "%s.%s" % (date, role_id)
	global_cur.execute("replace into role_back (bid, role_id, back_time, role_data, role_objs) values(%s, %s, now(), %s, %s);", (bid, role_id, repr(role_data), repr(role_objs)))

def SaveOneRoleForRevert(global_cur, role_id):
	zone_con = DBHelp.ConnectMasterDBRoleID(role_id)
	zone_con.cursorclass = cursors.DictCursor
	with zone_con as zone_cur:
		zone_cur.execute("select * from role_data where role_id = %s;" % role_id)
		result = zone_cur.fetchall()
		if not result:
			return
		role_data = result[0]
		now = datetime.datetime.now()
		date = "%s_%s_%s_%s_%s_%s" % (now.year, now.month, now.day, now.hour, now.minute, now.second)
		SaveOneRoleForBack(global_cur, zone_cur, role_data, date)

def SaveOneRole(role_id):
	global_con = DBHelp.ConnectGlobalWeb()
	with global_con as global_cur:
		SaveOneRoleForRevert(global_cur, role_id)

def Revert(bid):
	global_con = DBHelp.ConnectGlobalWeb()
	with global_con as global_cur:
		global_cur.execute("select role_data, role_objs from role_back where bid = %s", bid)
		result = global_cur.fetchall()
		if not result:
			print "没有找到备份%s" % bid
			return
	role_data = eval(result[0][0])
	role_objs = eval(result[0][1])
	role_id = role_data["role_id"]
	# 先要再次保存下角色数据
	SaveOneRoleForRevert(global_cur, role_id)
	# 再还原角色数据
	zone_con = DBHelp.ConnectMasterDBRoleID(role_id)
	with zone_con as zone_cur:
		updates = []
		values = []
		for name, value in role_data.iteritems():
			updates.append("%s=%%s" % name)
			values.append(value)
		# 更新role_data
		sql = "update role_data set " + ",".join(updates) + " where role_id = %s;" % role_id
		zone_cur.execute(sql, values)
		# 删除所有的obj,再重新插入之
		zone_cur.execute("delete from role_obj_%s where role_id = %s" % (role_id % Define.ROLE_HORIZONTAL_TABLE, role_id))
		for role_obj in role_objs:
			sql = "insert into role_obj_%s " % (role_id % Define.ROLE_HORIZONTAL_TABLE) +  "(obj_id, obj_type, obj_int, obj_data) values (%s, %s, %s, %s)"
			values = (role_obj["obj_id"], role_obj["obj_type"], role_obj["obj_int", role_obj["obj_data"]])
			zone_cur.execute(sql, values)
		# 修正离线命令
		zone_cur.execute("select max(command_id) from role_command where role_id = %s;" % role_id)
		result = zone_cur.fetchall()
		if result:
			command_id = result[0][0]
			if command_id:
				commanx_size = command_id % CValue.P2_32
				zone_cur.execute("update role_data set command_size = %s, command_index = %s;" % (commanx_size, commanx_size))

if __name__ == "__main__":
	SaveVIP()
	print "save %s role data." % (len(SaveRoleIDs))
