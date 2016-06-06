#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("DB.PersistenceVisit")
#===============================================================================
# 持久化数据
#===============================================================================
import Environment
from Common import Serialize
from ComplexServer.Plug.DB import DBWork

LoadPersistenceDataSQL = "select info, data from sys_persistence where per_key = %s;"
class LoadPerData(DBWork.DBVisit):
	def execute(self, con):
		with con as cur:
			self.result_big(self._execute(cur))
			cur.close()
	def _execute(self, cur):
		cur.execute(LoadPersistenceDataSQL, self.arg)
		result = cur.fetchall()
		if result:
			return Serialize.String2PyObj(result[0][0]), Serialize.String2PyObj(result[0][1])
		else:
			# 这里一定要返回两个值，用于给逻辑区分是自返回还是数据库返回
			return None, None

SavePersistenceDataSQL = "replace into sys_persistence (per_key, save_datetime, info, data) values(%s, NOW(), %s, %s)"
class SavePerData(DBWork.DBVisit):
	def _execute(self, cur):
		key, info, data = self.arg
		info = Serialize.PyObj2String(info)
		data = Serialize.PyObj2String(data)
		cur.execute(SavePersistenceDataSQL, (key, info, data))

if Environment.HasDB and "_HasLoad" not in dir():
	LoadPerData.reg()
	SavePerData.reg()
	


