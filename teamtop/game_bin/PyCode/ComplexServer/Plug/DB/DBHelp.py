#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("ComplexServer.Plug.DB.DBHelp")
#===============================================================================
# 辅助模块
#===============================================================================
import time
import datetime
import traceback
import cDateTime
import Environment
from Common import CValue
from Common import Define as Common_Define
from World import Define as World_Define

if "_HasLoad" not in dir():
	MySQLInfoCashe = {}
	MySQLInfoCashe_Union = {}

OneDaySecond = 24 * 3600
TwoWeekSecond = 2 * 7 * 24 * 3600
TwoWeekDelta = datetime.timedelta(days = 14)
def GetTwoWeekAgoDateTime():
	return cDateTime.Now() - TwoWeekDelta

def GetTwoWeekAgoUnixTime():
	return cDateTime.Seconds() - TwoWeekSecond

def GetOneDayAgoUnixTime():
	return cDateTime.Seconds() - OneDaySecond

def GetDBIDByRoleID(roleid):
	return roleid / CValue.P2_32

def GetDBChannelByRoleID(roleid):
	return roleid % Common_Define.DB_THREAD_NUM

def ConnectGlobalWeb():
	'''
	连接Web的数据库
	'''
	import MySQLdb
	ip, port, user, pwd = World_Define.Web_Global_MySQL
	con = MySQLdb.connect(host = ip, port = port, user = user, passwd = pwd, db = "web_global_new_%s" % Environment.ReadConfig(), charset = "utf8", use_unicode = False)
	if World_Define.SQL_TIME_ZONE is not None:
		with con as cur:
			if cDateTime.GetDST() > 0:
				cur.execute(World_Define.SQL_TIME_ZONE_DST)
			else:
				cur.execute(World_Define.SQL_TIME_ZONE)
			cur.close()
	return con


def ConnectGlobalWeb_Unoin():
	'''
	连接Web的数据库 游戏联盟专用
	'''
	import MySQLdb
	ip, port, user, pwd = World_Define.Unoin_Web_Global_MySQL
	con = MySQLdb.connect(host = ip, port = port, user = user, passwd = pwd, db = "web_global_new_qu", charset = "utf8", use_unicode = False)
	return con

def ConnectHouTaiWeb():
	'''
	连接Web的数据库
	'''
	import MySQLdb
	ip, port, user, pwd = World_Define.Web_HouTai_MySQL
	con = MySQLdb.connect(host = ip, port = port, user = user, passwd = pwd, db = "web_houtai_new_%s" % Environment.ReadConfig(), charset = "utf8", use_unicode = False)
	if World_Define.SQL_TIME_ZONE is not None:
		with con as cur:
			if cDateTime.GetDST() > 0:
				cur.execute(World_Define.SQL_TIME_ZONE_DST)
			else:
				cur.execute(World_Define.SQL_TIME_ZONE)
			cur.close()
	return con

def GetMySQLInfoByID(dbid):
	'''
	根据数据库ID，查找MySQL连接信息
	@param dbid:数据库ID
	@return: (ip, port, user, pwd)
	'''
	for _ in xrange(5):
		try:
			return _GetMySQLInfoByID(dbid)
		except:
			traceback.print_exc()
			time.sleep(2)
	return None

def _GetMySQLInfoByID(dbid):
	# 如果不在缓存中，则去数据库查询
	if dbid not in MySQLInfoCashe:
		con = ConnectGlobalWeb()
		with con as cur:
			# 根据进程KEY，查找连接的mysql名
			cur.execute("select mysql_name from zone where zid = %s;", dbid)
			result = cur.fetchall()
			if len(result) != 1:
				return None
			name = result[0][0]
			# 根据mysql名，查找具体的连接信息
			cur.execute("select master_ip, master_port, master_user, master_pwd from mysql where name = %s;", name)
			result = cur.fetchall()
			if len(result) != 1:
				return None
			info = result[0]
			MySQLInfoCashe[dbid] = info
	return MySQLInfoCashe[dbid]



def _GetMySQLInfoByID_Union(dbid):
	# 如果不在缓存中，则去数据库查询
	if dbid not in MySQLInfoCashe_Union:
		con = ConnectGlobalWeb_Unoin()
		with con as cur:
			# 根据进程KEY，查找连接的mysql名
			cur.execute("select mysql_name from zone where zid = %s;", dbid)
			result = cur.fetchall()
			if len(result) != 1:
				return None
			name = result[0][0]
			# 根据mysql名，查找具体的连接信息
			cur.execute("select master_ip, master_port, master_user, master_pwd from mysql where name = %s;", name)
			result = cur.fetchall()
			if len(result) != 1:
				return None
			info = result[0]
			MySQLInfoCashe_Union[dbid] = info
	return MySQLInfoCashe_Union[dbid]



def GetStandardZoneConnectByID(pid):
	'''
	根据进程KEY，查找该进程所对应的标准区信息
	@param pid:进程ID
	@return: C进程连接信息，D进程连接信息，GHL进程连接信息，合服D进程连接信息
	'''
	for _ in xrange(5):
		try:
			return _GetStandardZoneConnectByID(pid)
		except:
			traceback.print_exc()
			time.sleep(2)
	return None

def _GetStandardZoneConnectByID(zid):
	con = ConnectGlobalWeb()
	with con as cur:
		# 根据区ID查找区信息
		cur.execute("select c_process_key, d_process_key, ghl_process_key, merge_zids from zone where zid = %s and ztype = 'Standard' and be_merge_zid = 0;", zid)
		result = cur.fetchall()
		if len(result) != 1:
			return None
		c_process_key, d_process_key, ghl_process_key, merge_zids = result[0]
		# 查找每个合区的信息
		merge_d_process_keys = []
		merge_zids = eval(merge_zids)
		for merge_zid in merge_zids:
			cur.execute("select d_process_key from zone where zid = %s and ztype = 'Standard' and be_merge_zid = %s;", (merge_zid, zid))
			result = cur.fetchall()
			if len(result) != 1:
				return None
			merge_d_process_keys.append(result[0][0])
		c_process_info = GetProcessInfoByProcessKey(cur, c_process_key)
		if not c_process_info:
			return None
		d_process_info = GetProcessInfoByProcessKey(cur, d_process_key)
		if not d_process_info:
			return None
		ghl_process_info = GetProcessInfoByProcessKey(cur, ghl_process_key)
		if not ghl_process_info:
			return None
		merge_d_process_infos = []
		for merge_d_process_key in merge_d_process_keys:
			merge_d_process_info = GetProcessInfoByProcessKey(cur, merge_d_process_key)
			if not merge_d_process_info:
				return None
			merge_d_process_infos.append(merge_d_process_info)
		return c_process_info, d_process_info, ghl_process_info, merge_d_process_infos

def GetProcessInfoByProcessKey(cur, process_key):
	'''
	根据进程KEY，获取进程信息
	@param cur:MySQL游标
	@param process_key:进程KEY
	@return:pid, ip, port 
	'''
	cur.execute("select pid, port, computer_name from process where pkey = %s;", process_key)
	result = cur.fetchall()
	if len(result) != 1:
		return None
	pid, port, computer_name = result[0]
	cur.execute("select ip from computer where name = %s;", computer_name)
	result = cur.fetchall()
	if len(result) != 1:
		return None
	ip = result[0][0]
	return pid, ip, port

def GetCrossZoneConnectByID(zid):
	con = ConnectGlobalWeb()
	extend_process_keys = set()
	extend_process_infos = []
	with con as cur:
		cur.execute("select c_process_key from zone where zid = %s and ztype = 'Standard' and be_merge_zid = 0;", zid)
		c_process_key = cur.fetchall()[0][0]
		cur.execute("select d_process_key, merge_zids, zid from zone where c_process_key = %s and zid != %s and ztype = 'Standard' and be_merge_zid = 0 and zid < 30000;", (c_process_key, zid))
		for d_process_key, merge_zids, main_zid in cur.fetchall():
			merge_zids = eval(merge_zids)
			assert d_process_key not in extend_process_keys
			extend_process_keys.add(d_process_key)
			extend_process_infos.append(GetProcessInfoByProcessKey(cur, d_process_key))
			for merge_zid in merge_zids:
				cur.execute("select d_process_key from zone where zid = %s and ztype = 'Standard' and be_merge_zid = %s;", (merge_zid, main_zid))
				result = cur.fetchall()
				assert len(result) == 1
				merge_d_process_key = result[0][0]
				assert merge_d_process_key not in extend_process_keys
				extend_process_keys.add(merge_d_process_key)
				extend_process_infos.append(GetProcessInfoByProcessKey(cur, merge_d_process_key))
	return extend_process_infos

def ConnectMasterDBByID(dbid, db = "role_sys_data"):
	'''
	根据数据库进程ID，连接MySQL主库
	@param processid:进程ID
	@param db:默认数据库名前缀
	'''
	import MySQLdb
	info = GetMySQLInfoByID(dbid)
	if not info:
		return None
	ip, port, user, pwd = info
	con = MySQLdb.connect(host = ip, port = port, user = user, passwd = pwd, db = "%s_%s" % (db, dbid), charset = "utf8", use_unicode = False)
	if World_Define.SQL_TIME_ZONE is not None:
		with con as cur:
			if cDateTime.GetDST() > 0:
				cur.execute(World_Define.SQL_TIME_ZONE_DST)
			else:
				cur.execute(World_Define.SQL_TIME_ZONE)
			cur.close()
	return con



def ConnectMasterDBByID_HasExcept(dbid, db = "role_sys_data"):
	'''
	根据数据库进程ID，连接MySQL主库
	@param processid:进程ID
	@param db:默认数据库名前缀
	'''
	import MySQLdb
	info = _GetMySQLInfoByID(dbid)
	if not info:
		return None
	ip, port, user, pwd = info
	con = MySQLdb.connect(host = ip, port = port, user = user, passwd = pwd, db = "%s_%s" % (db, dbid), charset = "utf8", use_unicode = False)
	if World_Define.SQL_TIME_ZONE is not None:
		with con as cur:
			if cDateTime.GetDST() > 0:
				cur.execute(World_Define.SQL_TIME_ZONE_DST)
			else:
				cur.execute(World_Define.SQL_TIME_ZONE)
			cur.close()
	return con


def ConnectMasterDBByID_Union_HasExcept(dbid, db = "role_sys_data"):
	'''
	根据数据库进程ID，连接MySQL主库 (游戏联盟专用)
	@param processid:进程ID
	@param db:默认数据库名前缀
	'''
	import MySQLdb
	info = _GetMySQLInfoByID_Union(dbid)
	if not info:
		return None
	ip, port, user, pwd = info
	con = MySQLdb.connect(host = ip, port = port, user = user, passwd = pwd, db = "%s_%s" % (db, dbid), charset = "utf8", use_unicode = False)
	return con


def ConnectMasterDBRoleID(roleid, db = "role_sys_data"):
	'''
	根据角色ID，获取数据库连接
	@param roleid:角色ID
	@param db:默认数据库名前缀
	'''
	dbid = GetDBIDByRoleID(roleid)
	return ConnectMasterDBByID(dbid, db)


def ConnectMasterDBRoleID_Unoin_HasExcept(roleid, db = "role_sys_data"):
	'''
	根据角色ID，获取数据库连接
	@param roleid:角色ID
	@param db:默认数据库名前缀
	'''
	dbid = GetDBIDByRoleID(roleid)
	return ConnectMasterDBByID_Union_HasExcept(dbid, db)


def ConnecMianZoneMasterDBByID(dbid, db = "role_sys_data"):
	#连接主区的数据库ID(合服后的主区)
	con = ConnectGlobalWeb()
	with con as cur:
		cur.execute("select be_merge_zid from zone where zid = %s;" % dbid)
		result = cur.fetchall()
		if not result:
			return ConnectMasterDBByID(dbid, db)
		be_merge_zid = result[0][0]
		if be_merge_zid == 0:
			return ConnectMasterDBByID(dbid, db)
		
		return ConnectMasterDBByID(be_merge_zid, db)


def GetPublicIPAndPortByZoneID(zid):
	'''
	根据区ID，获取区的网关IP和端口
	@param zid:
	'''
	con = ConnectGlobalWeb()
	with con as cur:
		cur.execute("select ztype, public_ip, all_process_key, ghl_process_key, be_merge_zid from zone where zid = %s;", zid)
		
		result = cur.fetchall()
		ztype, public_ip, all_process_key, ghl_process_key, be_merge_zid = result[0]
		if be_merge_zid:
			#已经合区了，使用主区的数据
			cur.execute("select ztype, public_ip, all_process_key, ghl_process_key, be_merge_zid from zone where zid = %s;", be_merge_zid)
			result = cur.fetchall()
			ztype, public_ip, all_process_key, ghl_process_key, be_merge_zid = result[0]
			
		if ztype == "Standard":
			pkey = ghl_process_key
		elif ztype == "Single":
			pkey = all_process_key
		else:
			assert False
		cur.execute("select port, computer_name from process where pkey = %s;", pkey)
		result = cur.fetchall()
		port = result[0][0]
		# 如果没有为这个区配置公共IP，则使用所在机器的公共IP
		if not public_ip:
			computer_name = result[0][1]
			public_ip = GetComputerPublicIP(cur, computer_name)
		return public_ip, port

def LoadLanguageByZoneId(zid):
	#根据区Id,返回服务器语言版本
	con = ConnectGlobalWeb()
	with con as cur:
		cur.execute("select language from zone where zid = %s;", zid)
		result = cur.fetchall()
		return result[0][0]

def GetComputerPublicIP(cur, computer_name):
	cur.execute("select public_ip from computer where name = %s;", (computer_name,))
	result = cur.fetchall()
	return result[0][0]

#===============================================================================
# 特殊SQL逻辑
#===============================================================================
def InsertRoleCommand_Con(con, roleid, command):
	'''
	插入一条角色离线命令
	@param con:数据库连接
	@param roleid:角色ID
	@param command:离线命令
	'''
	with con as cur:
		# 关于角色数据相关的地方请搜索关键字  !@RoleData。
		# di32_0就是角色最后活跃时间，定义在Game.Role.Data.EnumDisperseInt32
		if not cur.execute("select command_size, unix_timestamp(now()) - di32_0 from role_data where role_id = %s for update;" % roleid):
			return False
		result = cur.fetchall()
		command_size = result[0][0]
		no_active_time = result[0][1]
		if no_active_time > TwoWeekSecond:
			return True
		new_index = command_size + 1
		command_id = (roleid % CValue.P2_32) * CValue.P2_32 + new_index
		# 关于角色ID和线程号直接的关系请搜索  !@RoleChannel
		channel = GetDBChannelByRoleID(roleid)
		cur.execute("insert into role_command(command_id, role_id, command_index, command_datetime, command_text) values(%s, %s, %s, now(), %s);", (command_id, roleid, new_index, command))
		cur.execute("update role_data set command_size = %s where role_id = %s;" % (new_index, roleid))
		cur.execute("insert ignore into role_command_cache(channel, role_id) values(%s, %s);" % (channel, roleid))
		cur.close()
		return True

def InsertRoleCommand_Cur(cur, roleid, command):
	'''
	插入一条角色离线命令
	@param cur:数据库游标
	@param roleid:角色ID
	@param command:离线命令
	'''
	# 关于角色数据相关的地方请搜索关键字  !@RoleData。
	# di32_0就是角色最后保存时间，定义在Game.Role.Data.EnumDisperseInt32
	if not cur.execute("select command_size, unix_timestamp(now()) - di32_0 from role_data where role_id = %s for update;" % roleid):
		return False
	result = cur.fetchall()
	command_size = result[0][0]
	no_active_time = result[0][1]
	if no_active_time > TwoWeekSecond:
		return False
	new_index = command_size + 1
	command_id = (roleid % CValue.P2_32) * CValue.P2_32 + new_index
	# 关于角色ID和线程号直接的关系请搜索  !@RoleChannel
	channel = GetDBChannelByRoleID(roleid)
	cur.execute("insert into role_command(command_id, role_id, command_index, command_datetime, command_text) values(%s, %s, %s, now(), %s);", (command_id, roleid, new_index, command))
	cur.execute("update role_data set command_size = %s where role_id = %s;" % (new_index, roleid))
	cur.execute("insert ignore into role_command_cache(channel, role_id) values(%s, %s);" % (channel, roleid))
	return True

def SendRoleCommend(roleid, command):
	'''
	给角色发送一条离线命令
	@param roleid:角色ID
	@param command:离线命令
	'''
	con = ConnectMasterDBRoleID(roleid)
	return InsertRoleCommand_Con(con, roleid, command)

def SendRoleMail(roleid, title, sender, content, mail_transaction, maildata):
	'''
	给角色发一封邮件
	@param roleid:
	@param title:
	@param sender:
	@param content:
	@param mail_transaction:
	@param maildata:
	'''
	con = ConnectMasterDBRoleID(roleid)
	with con as cur:
		return InsertRoleMail(cur, roleid, title, sender, content, mail_transaction, maildata)


def SendRoleMail_Unoin(roleid, title, sender, content, mail_transaction, maildata):
	'''
	给角色发一封邮件 游戏联盟专用
	@param roleid:
	@param title:
	@param sender:
	@param content:
	@param mail_transaction:
	@param maildata:
	'''
	con = ConnectMasterDBRoleID_Unoin_HasExcept(roleid)
	with con as cur:
		return InsertRoleMail(cur, roleid, title, sender, content, mail_transaction, maildata)



def InsertRoleMail(cur, roleid, title, sender, content, mail_transaction, maildata):
	'''
	给角色插入一条邮件
	@param cur:数据库游标
	@param roleid:角色id
	@param title:标题
	@param sender:发送者
	@param content:内容
	@param mail_transaction:邮件日志事务
	@param maildata:邮件附件内容
	'''
	# 关于角色数据相关的地方请搜索关键字  !@RoleData。
	# di32_0就是角色最后保存时间，定义在Game.Role.Data.EnumDisperseInt32
	if not cur.execute("select unix_timestamp(now()) - di32_0 from role_data where role_id = %s for update;" % roleid):
		return 0
	no_active_time = cur.fetchall()[0][0]
	if no_active_time > TwoWeekSecond:
		print "GREEN role(%s) lost mail title(%s) sender(%s) mail_transaction(%s)" % (roleid, title, sender, mail_transaction)
		return 0
	h = cur.execute("insert into role_mail (role_id, title, sender, dt, content, mail_transaction, maildata) values(%s, %s, %s, now(), %s, %s, %s);", (roleid, title, sender, content, mail_transaction, repr(maildata)))
	cur.fetchall()
	return h

if __name__ == "__main__":
	_GetMySQLInfoByID(1)
	
