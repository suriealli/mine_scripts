#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("DB.InfoVisit")
#===============================================================================
# 统计信息
#===============================================================================
import datetime
import Environment
from Common import CValue
from ThirdLib import PrintHelp
from ComplexServer.Plug.DB import DBWork

class Info_Connect(DBWork.DBVisit):
	def _execute(self, cur):
		cur.execute("insert ignore connect_info (account, userip, connect_time, from_1, from_2, from_3) values ('%s', '%s', now(), '%s', '%s', '%s');" % self.arg)

class Info_Create(DBWork.DBVisit):
	def _execute(self, cur):
		cur.execute("update connect_info set request_create = request_create + 1 where account = '%s';" % self.arg)

class Info_Operate(DBWork.DBVisit):
	def _execute(self, cur):
		cur.execute("update connect_info set first_operate = 1 where account = '%s';" % self.arg)

class Info_Status(DBWork.DBVisit):
	def _execute(self, cur):
		cur.execute("update connect_info set status = CONCAT(status, '|%s') where account = '%s';" % self.arg)

BaseTime = datetime.datetime(2013, 1, 1)
class Info_Login(DBWork.DBVisit):
	def _execute(self, cur):
		account, userip, role_id, from_1, from_2, from_3 = self.arg
		days = (datetime.datetime.now() - BaseTime).days
		lkey = days * CValue.P2_32 + role_id % CValue.P2_32
		cur.execute("insert ignore login_info (account, userip, login_day, lkey, from_1, from_2, from_3) values('%s', '%s', now(), %s, '%s', '%s', '%s');" % (account, userip, lkey, from_1, from_2, from_3))

class Info_Online(DBWork.DBVisit):
	def _execute(self, cur):
		cur.execute("insert into online_info (roles, ips, sta_time) values (%s, %s, now());" % self.arg)

class Info_Report(DBWork.DBVisit):
	def _execute(self, cur):
		role_id, report_info, login_info = self.arg
		report_info = PrintHelp.saferepr(report_info)
		login_info = PrintHelp.saferepr(login_info)
		cur.execute("replace into report_info (role_id, report_time, report_info, login_info) values(%s, now(), %s, %s)", (role_id, report_info, login_info))

if Environment.HasDB and "_HasLoad" not in dir():
	Info_Connect.reg()
	Info_Create.reg()
	Info_Operate.reg()
	Info_Status.reg()
	Info_Login.reg()
	Info_Online.reg()
	Info_Report.reg()
