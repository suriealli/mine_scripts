#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("DB.LoginVisit")
#===============================================================================
# 登录访问
#===============================================================================
import cProcess
import Environment
from ComplexServer.Plug.DB import DBWork, DBHelp

T_Login_Error = "登录失败，请重新登录！"
class CanLogin(DBWork.DBVisit):
	def _execute(self, cur):
		cur.execute("select thirdparty from account_login where account = %s and session = %s and login_time + INTERVAL 12 HOUR > NOW();", self.arg)
		result = cur.fetchall()
		# 这里和Http返回的形式一样
		if result:
			return 200, repr({"ret":0, "msg":"OK", "thirdparty":result[0][0]})
		else:
			return 200, repr({"ret":1, "msg":T_Login_Error, "thirdparty":None})

class LoadAccountInfo(DBWork.DBVisit):
	def _execute(self, cur):
		cur.execute("select role_id from role_data where account = %s", self.arg)
		ret = cur.fetchall()
		if ret:
			return ret[0][0]
		else:
			return 0

class AllotRoleName(DBWork.DBVisit):
	def _execute(self, cur):
		h = cur.execute("insert ignore all_role_name(role_name) values (%s);", self.arg)
		cur.close()
		return h

class CreateRole(DBWork.DBVisit):
	def execute(self, con):
		with con as cur:
			h = cur.execute("insert ignore into role_data (account, role_name, di32_7, di32_8) values(%s, %s, %s, %s)", self.arg)
			if h:
				roleid = con.insert_id()
				if DBHelp.GetDBIDByRoleID(roleid) != cProcess.ProcessID:
					print "GE_EXC role id(%s) not equal process id(%s)" % (roleid, cProcess.ProcessID)
					cProcess.Crash()
				#返回自增ID，即角色ID
				self.result(roleid)
			else:
				self.result(0)
			cur.close()

if Environment.HasDB and "_HasLoad" not in dir():
	CanLogin.reg()
	LoadAccountInfo.reg()
	AllotRoleName.reg()
	CreateRole.reg()
