#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 日志表定义
#===============================================================================
import threading
import traceback
import cProcess
import cDateTime
import cComplexServer
import DynamicPath
from ComplexServer.Plug.DB import Column
from Util.MySQL import DynamicTable, DynamicColumn

if "_HasLoad" not in dir():
	LogCount = 0
	LogCountLock = threading.Lock()

SQL_RENAME = '''RENAME TABLE log_base TO log_base%s,
log_base_tmp TO log_base,
log_obj TO log_obj%s,
log_obj_tmp TO log_obj,
log_value TO log_value%s,
log_value_tmp TO log_value;'''

SQL_LOG_BASE = "insert into log_base (log_id, role_id, log_transaction, log_event, log_datetime, log_content) values (0, 0, 0, 0, now(), '');"

SliceCount = 9999999

def HasNewLog(cnt = 1):
	with LogCountLock:
		global LogCount
		LogCount += cnt

def ResetLogCount():
	with LogCountLock:
		global LogCount
		LogCount = 0

def GetLogCount():
	with LogCountLock:
		return LogCount

def GetFilePath():
	return "%slog_count_%s.txt" % (DynamicPath.FilePath, cProcess.ProcessID)

def ReadTableRowCount():
	try:
		with open(GetFilePath()) as f:
			return int(f.read())
	except:
		return SliceCount / 3 * 2

def WriteTableRowCount():
	try:
		with open(GetFilePath(), "w") as f:
			f.write(str(GetLogCount()))
	except:
		traceback.print_exc()

def SliceTable():
	# 如果日志太少，则不必切表
	if GetLogCount() < SliceCount:
		return
	DynamicTable.MySQL.Init(cProcess.ProcessID)
	DynamicTable.MySQL.UserTable("role_sys_log_%s" % cProcess.ProcessID)
	# 构建临时表
	for table in [log_base, log_obj, log_value]:
		table.Build()
	# 改表
	with DynamicTable.MySQL.GetConnect() as cur:
		now = cDateTime.Now()
		suff = "_%s_%s_%s_%s_%s_%s_%s" % (cProcess.ProcessID, now.year, now.month, now.day, now.hour, now.minute, now.second)
		# 切表之前需要加入一条定位日志
		cur.execute(SQL_LOG_BASE)
		cur.execute(SQL_RENAME % (suff, suff, suff))
		# 切表之后需要加入一条定位日志
		cur.execute(SQL_LOG_BASE)
		cur.close()
	DynamicTable.MySQL.Final()
	# 切表完毕，重置日志数
	ResetLogCount()

def BuildTable():
	'''
	1. 构建本模块定义的表
	2. 初始化日志条数
	'''
	global LogCount
	# 连接MySQL，并且构建数据库
	DynamicTable.MySQL.Init(cProcess.ProcessID)
	DynamicTable.MySQL.UserTable("role_sys_log_%s" % cProcess.ProcessID)
	# 构建表
	for table in [log_base, log_obj, log_value]:
		table.Build()
	# 统计日志
	with DynamicTable.MySQL.GetConnect() as cur:
		for table in [log_base, log_obj, log_value]:
			# 注意，这里改了表名，为切表服务
			table.Rename(table.name + "_tmp")
		# 如果数据为空，则是刚刚创建的表，需要往log_base中插入一条时间定位的日志
		if GetLogCount() == 0:
			cur.execute(SQL_LOG_BASE)
		cur.close()
	# 关闭MySQL
	DynamicTable.MySQL.Final()
	# 定时切表
	HasNewLog(ReadTableRowCount())
	cComplexServer.RegSaveCallFunction1(WriteTableRowCount)
	cComplexServer.RegAfterNewHourCallFunction(SliceTable)

#===============================================================================
# 列和索引定义
#===============================================================================
log_id = DynamicColumn.IntColumn("log_id", "bigint", False, False, "日志ID")
log_transaction = DynamicColumn.IntColumn("log_transaction", "smallint", True, False, "事务")
log_event = DynamicColumn.IntColumn("log_event", "smallint", True, False, "事件")
log_datetime = DynamicColumn.DateTimeColumn("log_datetime", "时间")
log_content = DynamicColumn.StringColumn("log_content", 10000, "内容")

log_id_index = DynamicColumn.ToMUL(log_id)
log_transaction_index = DynamicColumn.ToMUL(log_transaction)
log_event_index = DynamicColumn.ToMUL(log_event)
log_datetime_index = DynamicColumn.ToMUL(log_datetime)
role_id_index = DynamicColumn.ToMUL(Column.role_id)

#===============================================================================
# 表定义(注意表名要全小写字母)
#===============================================================================
log_base = DynamicTable.Table("log_base")
log_obj = DynamicTable.Table("log_obj")
log_value = DynamicTable.Table("log_value")

for table in (log_base, log_obj, log_value):
	table.AddColumn(log_id)
	table.AddColumn(Column.role_id)
	table.AddColumn(log_transaction)
	table.AddColumn(log_event)
	table.AddColumn(log_datetime)
	table.AddColumn(log_content)
	table.AddKey(log_id_index)
	table.AddKey(role_id_index)
	table.AddKey(log_transaction_index)
	table.AddKey(log_event_index)
	table.AddKey(log_datetime_index)

log_obj.AddColumn(Column.obj_id)
log_obj.AddColumn(Column.obj_type)
log_obj.AddColumn(Column.obj_int)
log_obj.AddColumn(Column.obj_data_small)
log_obj.AddKey(DynamicColumn.ToMUL(Column.obj_id))
log_obj.AddKey(DynamicColumn.ToMUL(Column.obj_type))

log_value.AddColumn(DynamicColumn.IntColumn("log_old_value", "bigint", False, False, "旧值"))
log_value.AddColumn(DynamicColumn.IntColumn("log_new_value", "bigint", False, False, "新值"))

