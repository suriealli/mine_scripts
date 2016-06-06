#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("World.Build")
#===============================================================================
# 构建
#===============================================================================
from ComplexServer.Plug.DB import GlobalTable, DBHelp

def _CopyTable(cur, ftable, ttable):
	cur.execute(ftable.GetSelectAllValueSQL(""))
	result = cur.fetchall()
	cur.execute("truncate %s;" % ttable.name)
	cur.executemany(ttable.GetInsertAllValueSQL(), result)

def CopyFromTemp():
	'''
	将临时游戏世界配置拷贝到正式游戏配置
	'''
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		_CopyTable(cur, GlobalTable.computer_tmp, GlobalTable.computer)
		_CopyTable(cur, GlobalTable.mysql_tmp, GlobalTable.mysql)
		_CopyTable(cur, GlobalTable.process_tmp, GlobalTable.process)
		_CopyTable(cur, GlobalTable.zone_tmp, GlobalTable.zone)

def CopyToTemp():
	'''
	将正式游戏配置拷贝到临时游戏配置
	'''
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		_CopyTable(cur, GlobalTable.computer, GlobalTable.computer_tmp)
		_CopyTable(cur, GlobalTable.mysql, GlobalTable.mysql_tmp)
		_CopyTable(cur, GlobalTable.process, GlobalTable.process_tmp)
		_CopyTable(cur, GlobalTable.zone, GlobalTable.zone_tmp)

if __name__ == "__main__":
	CopyFromTemp()
	print "Copy End."

