#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.DB.LogVisit")
#===============================================================================
# 日志模块
#===============================================================================
import cProcess
import Environment
from ComplexServer.Plug.DB import DBWork, LogTable

LOG_BASE_SQL = "insert into role_sys_log_" + str(cProcess.ProcessID) + ".log_base (log_id, role_id, log_transaction, log_event, log_datetime, log_content) values(%s, %s, %s, %s, now(), %s);"
LOG_OBJ_SQL = "insert into role_sys_log_"+ str(cProcess.ProcessID) + ".log_obj (log_id, role_id, log_transaction, log_event, log_datetime, obj_id, obj_type, obj_int, obj_data, log_content) values(%s, %s, %s, %s, now(), %s, %s, %s, %s, %s);"
LOG_VALUE_SQL = "insert into role_sys_log_"+ str(cProcess.ProcessID) + ".log_value (log_id, role_id, log_transaction, log_event, log_datetime, log_old_value, log_new_value, log_content) values(%s, %s, %s, %s, now(), %s, %s, %s);"

class LogBase(DBWork.DBVisit):
	def _execute(self, cur):
		cur.execute(LOG_BASE_SQL, self.arg)
		LogTable.HasNewLog()

class LogObj(DBWork.DBVisit):
	def _execute(self, cur):
		cur.execute(LOG_OBJ_SQL, self.arg)
		LogTable.HasNewLog()

class LogValue(DBWork.DBVisit):
	def _execute(self, cur):
		cur.execute(LOG_VALUE_SQL, self.arg)
		LogTable.HasNewLog()

if Environment.HasDB and "_HasLoad" not in dir():
	LogBase.reg()
	LogObj.reg()
	LogValue.reg()
