#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 有个服的辅助函数
#===============================================================================
from ComplexServer.Plug.DB import DBHelp
from World import Define

_ProcessCmp = {"All":0, "C":1, "GHL":2, "D":3}
_ProcessCashe = None
_ZoneCashe = None

class ProcessConfig(object):
	def __init__(self, pkey, ptype, pid, ip, port, bind_zid, work_zid, bind_zone_name, work_zome_name):
		self.pkey = pkey
		self.ptype = ptype
		self.pid = pid
		self.ip = ip
		self.port = port
		self.bind_zid = bind_zid
		self.work_zid = work_zid
		self.bind_zone_name = bind_zone_name
		self.work_zome_name = work_zome_name
	
	def __cmp__(self, other):
		# 先比较bind_zone_id
		result = cmp(self.work_zid, other.work_zid)
		# 再比较进程ID
		if result == 0:
			result = cmp(self.pid, other.pid)
		# 再比较类型排序
		if result == 0:
			result = cmp(_ProcessCmp[self.ptype], _ProcessCmp[other.ptype])
		return result
	
	def get_plug_coding(self):
		if self.ptype == "All":
			return "C|D|G|H|L"
		else:
			return self.ptype
	
	def get_name(self):
		if self.bind_zone_name == self.work_zome_name:
			return "%s_%s" % (self.pkey, self.work_zome_name)
		else:
			return "%s_%s.原%s" % (self.pkey, self.work_zome_name, self.bind_zone_name)
	
	def has_gateway(self):
		return "G" in self.get_plug_coding()
	
	def has_logic(self):
		return "L" in self.get_plug_coding()

class ZoneConfig(object):
	def __init__(self, zid, name, master_ip, master_port, master_user, master_pwd, be_merge_zid, be_merge_zone_name):
		self.zid = zid
		self.name = name
		self.master_ip = master_ip
		self.master_port = master_port
		self.master_user = master_user
		self.master_pwd = master_pwd
		self.be_merge_zid = be_merge_zid
		self.be_merge_zone_name = be_merge_zone_name
	
	def get_name(self):
		if self.be_merge_zone_name:
			return "%s.原%s" % (self.be_merge_zone_name, self.name)
		else:
			return self.name

def GetZoneNameByZID(cur, zid):
	if zid == 0:
		return "None"
	else:
		cur.execute("select name from zone where zid = %s;", zid)
		return cur.fetchall()[0][0]

def GetProcess():
	global _ProcessCashe
	if _ProcessCashe is None:
		d = {}
		con = DBHelp.ConnectGlobalWeb()
		with con as cur:
			# 获取所有的进程
			cur.execute("select pkey, ptype, pid, computer_name, port, bind_zid, work_zid from process;")
			for pkey, ptype, pid, computer_name, port, bind_zid, work_zid in cur.fetchall():
				# 根据所在机器名，获取机器IP
				cur.execute("select ip from computer where name = %s;", (computer_name,))
				ip = cur.fetchall()[0][0]
				# 控制进程和区没有关系，特殊处理
				if Define.IsControlProcessKey(pkey):
					bind_zone_name = ""
					work_zone_name = ""
				else:
					# 根据区ID，获取区名
					bind_zone_name = GetZoneNameByZID(cur, bind_zid)
					work_zone_name = GetZoneNameByZID(cur, work_zid)
				d[pkey] = ProcessConfig(pkey, ptype, pid, ip, port, bind_zid, work_zid, bind_zone_name, work_zone_name)
		_ProcessCashe = d
	return _ProcessCashe

def GetZone():
	global _ZoneCashe
	if _ZoneCashe is None:
		d = {}
		con = DBHelp.ConnectGlobalWeb()
		with con as cur:
			cur.execute("select zid, name, mysql_name, be_merge_zid from zone;")
			for zid, name, mysql_name, be_merge_zid in cur.fetchall():
				cur.execute("select master_ip, master_port, master_user, master_pwd from mysql where name = %s;", (mysql_name,))
				master_ip, master_port, master_user, master_pwd = cur.fetchall()[0]
				if be_merge_zid == 0:
					be_merge_zone_name = ""
				else:
					be_merge_zone_name = GetZoneNameByZID(cur, be_merge_zid)
				d[zid] = ZoneConfig(zid, name, master_ip, master_port, master_user, master_pwd, be_merge_zid, be_merge_zone_name)
		_ZoneCashe = d
	return _ZoneCashe

def GetFullNameByZoneID(zid):
	'''
	根据ID，获取区名
	@param zid:ID
	'''
	zone = GetZone().get(zid)
	if zone:
		return "%s(%s)" % (zid, zone.get_name())
	else:
		return str(zid)

def GetFullNameByRoleID(role_id):
	'''
	根据角色ID，获取区名
	@param role_id:角色ID
	'''
	return GetFullNameByZoneID(DBHelp.GetDBIDByRoleID(role_id))

def GetFullNameByProcessKey(pkey):
	'''
	根据进程KEY，获取进程名
	@param pkey:进程KEY
	'''
	process = GetProcess().get(pkey)
	if process:
		return process.get_name()
	else:
		return str(pkey)

def CmpProcessKey(pkey1, pkey2):
	'''
	比较两个进程KEY
	'''
	process1 = GetProcess().get(pkey1)
	if process1 is None:
		return -1
	process2 = GetProcess().get(pkey2)
	if process2 is None:
		return 1
	return cmp(process1, process2)

