#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.DB.StatisticsVisit")
#===============================================================================
# 统计访问
#===============================================================================
import cComplexServer
import Environment
from ComplexServer.Plug.DB import DBWork, DBHelp

class Statistics(DBWork.DBVisit):
	def _execute(self, cur):
		cur.execute("insert into sys_statistics (skey, roles, count, min_count, max_count, dt) values(%s, %s, %s, %s, %s, now());", self.arg)

class DelStatistics(DBWork.DBVisit):
	def _execute(self, cur):
		cur.execute("delete from sys_statistics where dt < %s;", DBHelp.GetTwoWeekAgoDateTime())

def AfterNewDay():
	DBWork.OnDBVisit_MainThread(0, "DelStatistics", None, (None, None))

if Environment.HasDB and "_HasLoad" not in dir():
	Statistics.reg()
	DelStatistics.reg()
	cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
