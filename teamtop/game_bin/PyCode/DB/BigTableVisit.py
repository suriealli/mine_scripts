#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("DB.BigTableVisit")
#===============================================================================
# 大表
#===============================================================================
import threading
import traceback
import Environment
from Util.MySQL import DynamicColumn
from Common import Serialize
from ComplexServer.Plug.DB import DBWork, SystemTable

# 缓存删除和保存数据库SQL
Lock = threading.Lock()
DeleteSQLs = {}
InsertAllSQLs = {}
TransDatas = {}

def InitTableInfo(name, pri):
	Lock.acquire()
	try:
		# 在这里缓存下该表的删除和保存数据的SQL, 和数据转换规则
		table = SystemTable.GetTableByName(name)
		names = table.GetColumnNames()
		DeleteSQLs[name] = "delete from %s where %s in (%s)" % (name, pri, "%s")
		InsertAllSQLs[name] = table.GetInsertAllValueSQL("REPLACE")
		# 在这里缓存下Python对象和数据库类型之间的转化
		MySQL2Python = {}
		Python2MySQL = {}
		for idx, cname in enumerate(names):
			column = table.columns[cname]
			if type(column) == DynamicColumn.ObjColumn:
				MySQL2Python[idx] = Serialize.String2PyObj
				Python2MySQL[idx] = Serialize.PyObj2String
		if MySQL2Python:
			TransDatas[name] = (MySQL2Python, Python2MySQL)
	except:
		traceback.print_exc()
	finally:
		Lock.release()

class LoadBTData(DBWork.DBVisit):
	def execute(self, con):
		with con as cur:
			self.result_big(self._execute(cur))
			cur.close()
	
	def _execute(self, cur):
		name = self.arg
		pri = SystemTable.GetPRIByName(name)
		InitTableInfo(name, pri)
		sql = SystemTable.GetTableByName(name).GetSelectAllValueSQL("")
		cur.execute(sql)
		ret =  cur.fetchall()
		# 尝试转换
		trans = TransDatas.get(name)
		if trans:
			MySQL2Python = trans[0]
			result = []
			for row in ret:
				row = list(row)
				for idx, fun in MySQL2Python.iteritems():
					row[idx] = fun(row[idx])
				result.append(row)
			return result
		else:
			return ret

class DelBTData(DBWork.DBVisit):
	def _execute(self, cur):
		name, keys = self.arg
		sql = DeleteSQLs[name]
		cur.execute(sql % ",".join([str(key) for key in keys]))

class SaveBTData(DBWork.DBVisit):
	def _execute(self, cur):
		name, rows = self.arg
		# 尝试转换
		trans = TransDatas.get(name)
		if trans:
			Python2MySQL = trans[1]
			result = []
			for row in rows:
				row = list(row)
				for idx, fun in Python2MySQL.iteritems():
					row[idx] = fun(row[idx])
				result.append(tuple(row))
			rows = result
		sql = InsertAllSQLs[name]
		cur.executemany(sql, rows)

if Environment.HasDB and "_HasLoad" not in dir():
	LoadBTData.reg()
	DelBTData.reg()
	SaveBTData.reg()
