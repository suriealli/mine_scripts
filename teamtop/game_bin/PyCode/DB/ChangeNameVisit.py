#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("DB.ChangeNameVisit")
#===============================================================================
# 改名
#===============================================================================
import Environment
from ComplexServer.Plug.DB import DBWork

class check_name(DBWork.DBVisit):
	def _execute(self, cur):
		roleName = self.arg
		ret = cur.execute("insert ignore all_role_name (role_name) values('%s');" % roleName) > 0
		if not ret:#插入失败
			return False
		cur.close()
		return True

if Environment.HasDB and "_HasLoad" not in dir():
	check_name.reg()