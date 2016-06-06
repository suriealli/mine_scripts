#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("ImportRole")
#===============================================================================
# 导角色
#===============================================================================
import urllib2
import datetime
from ComplexServer.Plug.DB import DBHelp
from Common import Define, CValue

datetime
#URL = "http://127.0.0.1:8000/DataBase/RoleData/ExportRole/?roleid=%s"
URL_QQ = "http://banben1.app100718848.twsapp.com:8008/DataBase/RoleData/ExportRole/?roleid=%s"
URL_QU = "http://quanju2.app100718848.twsapp.com:8000/DataBase/RoleData/ExportRole/?roleid=%s"
URL_NA = "http://banben.legendknight.com:8008/DataBase/RoleData/ExportRole/?roleid=%s"
URL_KGG = "http://kgg-global.legendknight.com:8000/DataBase/RoleData/ExportRole/?roleid=%s"
URL_FT = "http://220.130.123.111:8008/DataBase/RoleData/ExportRole/?roleid=%s"
URL_TK = "http://beta01.salagame.com:8008/DataBase/RoleData/ExportRole/?roleid=%s"
URL_RU = "http://msk-ver.srv.dragonknight.ru:8008/DataBase/RoleData/ExportRole/?roleid=%s"
URL_RUE = "http://sp-global.srv.dragonknight.ru:8008/DataBase/RoleData/ExportRole/?roleid=%s"
URL_PL = "http://dnpl-ver.salagame.com:8008/DataBase/RoleData/ExportRole/?roleid=%s"

def GetRoleInfo(role_id, evn):
	if evn.startswith("qq"):
		url = URL_QQ % role_id
	elif evn.startswith("na"):
		url = URL_NA % role_id
	elif evn.startswith("ft"):
		url = URL_FT % role_id
	elif evn.startswith("qu"):
		url = URL_QU % role_id
	elif evn.startswith("tk"):
		url = URL_TK % role_id
	elif evn.startswith('rue'):
		url = URL_RUE % role_id
	elif evn.startswith('ru'):
		url = URL_RU % role_id
	elif evn.startswith('pl'):
		url = URL_PL % role_id
	elif evn.startswith('kgg'):
		url = URL_KGG % role_id
	else:
		url = URL_QQ % role_id
	return eval(urllib2.urlopen(url).read())

def Insert(cur, d, table_name):
	keys = []
	formats = []
	values = []
	for key, value in d.iteritems():
		keys.append(key)
		formats.append("%s")
		values.append(value)
	sql = "replace into %s (%s) values(%s);" % (table_name, ", ".join(keys), ",".join(formats))
	#print sql
	cur.execute(sql, values)

def ImportRole(role_id, zone_id, account, env = "qq"):
	'''
	导入角色
	@param role_id:源角色ID
	@param zone_id:目标区ID
	@param account:目标帐号
	'''
	role_info = GetRoleInfo(role_id, env)
	if role_info is None:
		print "没有源角色ID", role_id
		return False
	RealImportRole(role_info, zone_id, account)

def RealImportRole(role_info, zone_id, account):
	role_data, role_obj, role_command, role_mail = role_info
	con = DBHelp.ConnectMasterDBByID(zone_id)
	if con is None:
		print "没有目标区ID", zone_id
		return
	with con as cur:
		# 剔除角色ID
		del role_data["role_id"]
		# 修正帐号
		role_data["account"] = account
		# 修正封号
		role_data["di32_3"] = 0
		# 删除相同的帐号
		if cur.execute("delete from role_data where account = %s;", role_data["account"]):
			print "删除了相同的帐号", role_data["account"]
		# 删除相同角色名
		if cur.execute("delete from role_data where role_name = %s;", role_data["role_name"]):
			print "删除了相同的帐号", role_data["role_name"]
		# 插入角色数据
		Insert(cur, role_data, "role_data")
		cur.execute("select last_insert_id();")
		new_role_id = cur.fetchall()[0][0]
		
		for obj in role_obj:
			# 修正角色ID
			obj["role_id"] = new_role_id
			# 删除相同的ObjID
			for idx in xrange(Define.ROLE_HORIZONTAL_TABLE):
				if cur.execute("delete from role_obj_%s where obj_id = %s;" % (idx, obj["obj_id"])):
					pass
					#print "删除了相同的ObjID", obj["obj_id"]
			# 插入OBJ
			Insert(cur, obj, "role_obj_%s" % (new_role_id % Define.ROLE_HORIZONTAL_TABLE))
		
		# 清除所有的角色命令
		for command in role_command:
			# 修正角色ID
			command["role_id"] = new_role_id
			# 修正命令ID
			command["command_id"] = (new_role_id % CValue.P2_32) * CValue.P2_32 + (command["command_id"] % CValue.P2_32)
			# 插入Command
			#print "command", command
			Insert(cur, command, "role_command")
		
		for mail in role_mail:
			# 修正角色ID
			mail["role_id"] = new_role_id
			# 插入邮件
			Insert(cur, mail, "role_mail")
		
		DBHelp.InsertRoleCommand_Cur(cur, new_role_id, "import Game.JJC.JJCMgr as m;m.ActivateJJC(role)")
		DBHelp.InsertRoleCommand_Cur(cur, new_role_id, "import Game.Pet.PetMgr as P;P.RevertPet(role)")
		
	print "BuileRole OK ----new_role_id (%s)---->" % new_role_id

if __name__ == "__main__":
	#ImportRole(4294967310, 2, "q11na", "qq")	#腾讯号(空间，朋友，3366，大厅)
	#ImportRole(1112396531454, 2, "q11na", "qu")	#腾讯游戏联盟
	ImportRole(21474838290, 5001, "q3", "kgg")	#北美
	#ImportRole(4294967310, 2, "q11na", "ft")	#繁体
